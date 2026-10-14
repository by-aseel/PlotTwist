"""Actual Ollama generation adapted to C3's existing manual tool loop.

No API key, remote endpoint, scripted reply, or automatic tool execution.
"""
from __future__ import annotations
import copy
import json
import os
import time
from types import SimpleNamespace
from urllib.parse import urlparse
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import HTTPError, URLError


class LocalModelError(RuntimeError):
    def __init__(self, message, code=None):
        self.code = code
        super().__init__(message)


class LocalClient:
    def __init__(self, base_url=None, transport=None):
        self.base_url = (base_url or os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434')).rstrip('/')
        parsed = urlparse(self.base_url)
        if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1'):
            raise ValueError('Local mode requires a loopback Ollama URL')
        self._opener = build_opener(ProxyHandler({}))
        self.transport = transport or self._request
        self.chat = SimpleNamespace(completions=self)
        self.last_metrics = {}

    def _request(self, payload):
        request = Request(self.base_url+'/api/chat', data=json.dumps(payload).encode('utf-8'),
                          headers={'Content-Type': 'application/json'})
        try:
            with self._opener.open(request, timeout=180) as response:
                return json.load(response)
        except HTTPError as exc:
            raise LocalModelError(f'Ollama returned HTTP {exc.code}', exc.code) from None
        except (URLError, TimeoutError):
            raise LocalModelError('Start Ollama and download the selected local model; request unavailable or timed out') from None

    def create(self, *, model, messages, tools=None, tool_choice='auto', temperature=.35,
               response_format=None, parallel_tool_calls=False, **kwargs):
        systems, conversation, call_names = [], [], {}
        for item in messages:
            role = item['role']
            if role == 'system':
                systems.append(item['content'])
                continue
            message = {'role': role, 'content': item.get('content') or ''}
            if role == 'assistant' and item.get('tool_calls'):
                message['tool_calls'] = []
                for call in item['tool_calls']:
                    function = call['function']
                    args = function['arguments']
                    if isinstance(args, str): args = json.loads(args)
                    call_names[call['id']] = function['name']
                    message['tool_calls'].append({'function': {'name': function['name'], 'arguments': args}})
            elif role == 'tool':
                if item['tool_call_id'] not in call_names:
                    raise ValueError('Tool observation has no matching model call')
                message['tool_name'] = call_names[item['tool_call_id']]
            conversation.append(message)
        native_tools = copy.deepcopy(tools or [])
        if tool_choice == 'none': native_tools = []
        for tool in native_tools: tool['function'].pop('strict', None)
        if isinstance(tool_choice, dict):
            name = tool_choice['function']['name']
            native_tools = [t for t in native_tools if t['function']['name'] == name]
            if not native_tools: raise ValueError('Requested tool is not defined')
            systems.append(f'Application routing requirement: request the supplied {name} function before replying. Use the actual customer text and validated lead fields for its arguments. The application executes it; you must wait for its observation before claiming success.')
        if any(item['role']=='tool' for item in conversation):
            systems.append('Use the tool observation to complete this customer turn. Do not repeat a successful save. A local record does not send email, confirm a booking, or promise a later reply.')
        if systems: conversation.insert(0, {'role':'system','content':'\n\n'.join(systems)})
        payload = {'model':model,'messages':conversation,'stream':False,'keep_alive':'10m',
                   'options':{'temperature':temperature,'num_ctx':8192,'num_predict':1000,'seed':int(os.getenv('OLLAMA_SEED','43'))}}
        if native_tools: payload['tools'] = native_tools
        if isinstance(tool_choice,dict):
            # Ollama has no native forced-tool switch. Constrain the model's
            # structured action proposal; the agent still validates and executes it.
            function=native_tools[0]['function']
            payload['format']={'type':'object','properties':{'name':{'type':'string','enum':[function['name']]},'arguments':function['parameters']},'required':['name','arguments'],'additionalProperties':False}
        if response_format:
            payload['format'] = {'type':'object','properties':{'revised_reply':{'type':'string'},'checks':{'type':'array','items':{'type':'string'}}},'required':['revised_reply','checks'],'additionalProperties':False}
        if model.startswith('qwen3'):
            payload['think'] = False
            conversation[0]['content'] += '\n/no_think'
        started = time.perf_counter()
        response = self.transport(payload)
        self.last_metrics = {k:response.get(k) for k in ('model','created_at','done_reason','total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration')}
        self.last_metrics.update(request_elapsed_ms=round((time.perf_counter()-started)*1000,2),generation_seed=payload['options']['seed'])
        if not response.get('done') or response.get('done_reason')=='length':
            raise LocalModelError('Local output did not complete within its token limit')
        message = response.get('message', {})
        content = message.get('content') or ''
        if '<think>' in content or '</think>' in content:
            raise LocalModelError('Model ignored the no-thinking output protocol; private reasoning was not exposed')
        native_calls = message.get('tool_calls') or []
        # Small models may print a structured call rather than use tool_calls.
        if native_tools and not native_calls:
            decoder = json.JSONDecoder()
            for offset,char in enumerate(content):
                if char!='{': continue
                try: value,_ = decoder.raw_decode(content[offset:])
                except ValueError: continue
                if isinstance(value,dict) and isinstance(value.get('name'),str) and isinstance(value.get('arguments'),dict):
                    native_calls.append({'function':value})
            if native_calls:
                content = ''
                self.last_metrics['tool_proposal_source'] = 'model_content'
        if not parallel_tool_calls and len(native_calls)>1:
            raise LocalModelError('Model requested parallel calls although one call per round was required')
        calls=[]
        for index,call in enumerate(native_calls):
            function=call['function'];args=function['arguments']
            if isinstance(args,dict): args=json.dumps(args,ensure_ascii=False)
            calls.append(SimpleNamespace(id=f'local_{len(messages)}_{index}',function=SimpleNamespace(name=function['name'],arguments=args)))
        if not calls and not content.strip(): raise LocalModelError('Local model returned no answer or action')
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content,tool_calls=calls))])
