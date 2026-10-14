"""Local-model transport and graph integration contracts; no downloads or network."""
import json
from pathlib import Path
import tempfile
import unittest
from ollama_model import OllamaModel, LocalModelError
from plottwist_agent import PlotTwistAgent

class LocalModelTests(unittest.TestCase):
    def test_sampling_history_and_json_response_forwarded_to_local_model(self):
        captured=[]
        def transport(payload):
            captured.append(payload)
            return {"done":True,"done_reason":"stop","model":"qwen3:4b", "message":{"content":'{"final":"Hello"}'},"eval_count":12}
        model=OllamaModel(transport=transport)
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode="local",model=model,db_path=Path(folder)/'records.sqlite3')
            result=agent.respond("Hi",history=[{"role":"user","content":"Prior birthday preference"}],settings={"model":"qwen3:4b","top_k":20,"temperature":.2,"top_p":.7,"frequency_penalty":.3,"presence_penalty":.4,"max_tokens":999,"generation_seed":123})
        request=captured[0]
        self.assertEqual(result['mode'],'local')
        self.assertEqual(request['model'],'qwen3:4b')
        self.assertEqual((request['options']['temperature'],request['options']['top_k'],request['options']['num_predict']),(.2,20,999))
        self.assertEqual((request['options']['top_p'],request['options']['frequency_penalty'],request['options']['presence_penalty'],request['options']['seed']),(.7,.3,.4,123))
        system_messages=[m for m in request['messages'] if m['role']=='system']
        self.assertEqual(len(system_messages),1)
        self.assertIn('Dedicated instructions',system_messages[0]['content'])
        self.assertIn('PlotTwist Experiences',system_messages[0]['content'])
        self.assertNotIn('format',request)
        self.assertEqual(len(request['tools']),4)
        self.assertFalse(request['think'])
        self.assertTrue(any(x['content']=='Prior birthday preference' for x in request['messages']))
        self.assertEqual(result['trace'][0]['generation']['eval_count'],12)

    def test_model_action_observation_loop_uses_real_tools(self):
        requests=[]
        outputs=[{"action":{"tool":"search_experiences","arguments":{"query":"birthday","guests":8}}},
                 {"action":{"tool":"estimate_event","arguments":{"experience_id":"birthday","guests":8}}},
                 {"final":"Birthday Mystery Nights starts at an indicative USD 240 per group."}]
        def transport(payload):
            requests.append(json.loads(json.dumps(payload)))
            return {"done":True,"done_reason":"stop","message":{"content":json.dumps(outputs.pop(0))}}
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',model=OllamaModel(transport=transport),db_path=Path(folder)/'records.sqlite3')
            result=agent.respond('Birthday for 8 guests',settings={'model':'qwen2.5:3b'})
        self.assertEqual(result['model_calls'],3)
        self.assertEqual(requests[1]['messages'][-1]['role'],'tool')
        self.assertEqual(requests[1]['messages'][-1]['tool_name'],'search_experiences')
        self.assertEqual(requests[1]['messages'][-2]['tool_calls'][0]['function']['name'],'search_experiences')
        self.assertIn('240',requests[2]['messages'][-1]['content'])
        self.assertNotIn('think',requests[0])

    def test_native_tool_call_is_detected_and_returned_to_manual_graph(self):
        model=OllamaModel(transport=lambda _: {'done':True,'message':{'content':'Look up the package.', 'tool_calls':[{'function':{'name':'search_experiences','arguments':{'query':'birthday','guests':8}}}]}})
        settings={'model':'qwen2.5:3b','reasoning':'brief_plan','temperature':.1,'top_p':1,'top_k':40,'frequency_penalty':0,'presence_penalty':0,'max_tokens':700}
        result=json.loads(model.complete([{'role':'system','content':'Instructions'},{'role':'user','content':'Birthday for 8'}],settings))
        self.assertEqual(result['action']['tool'],'search_experiences')
        self.assertEqual(result['plan'],'Look up the package.')

    def test_local_failure_has_no_demo_fallback(self):
        def failed(_):raise LocalModelError('Server unavailable',503)
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',model=OllamaModel(transport=failed),db_path=Path(folder)/'records.sqlite3')
            result=agent.respond('Birthday for 8 guests')
        self.assertEqual(result['route'],'error')
        self.assertEqual(result['trace'][0]['api_code'],503)
        self.assertEqual(result['mode'],'local')

    def test_printed_function_proposal_is_an_action_not_a_false_save_reply(self):
        model=OllamaModel(transport=lambda _: {'done':True,'message':{'content':'I will save it.\n{"name":"record_customer_interest","arguments":{"email":"aseel@example.com","name":"Aseel","message":"birthday enquiry"}}'}})
        settings={'model':'qwen2.5:1.5b','reasoning':'direct','temperature':.45,'top_p':1,'top_k':40,'frequency_penalty':.15,'presence_penalty':0,'max_tokens':700}
        result=json.loads(model.complete([{'role':'system','content':'Instructions'},{'role':'user','content':'Please save my enquiry'}],settings))
        self.assertNotIn('final',result)
        self.assertEqual(result['action']['tool'],'record_customer_interest')
        self.assertEqual(model.last_metrics['tool_proposal_source'],'model_content')

    def test_local_mode_cannot_transmit_to_remote_host(self):
        for url in ('https://example.com','http://example.com:11434','ftp://localhost:11434'):
            with self.subTest(url=url),self.assertRaises(ValueError):OllamaModel(base_url=url)

    def test_incomplete_output_returns_to_manual_parser(self):
        model=OllamaModel(transport=lambda _: {'done':True,'done_reason':'length','message':{'content':'{"final":'}})
        settings={'model':'qwen3:4b','reasoning':'direct','temperature':.1,'top_p':1,'top_k':40,'frequency_penalty':0,'presence_penalty':0,'max_tokens':180}
        self.assertEqual(model.complete([{'role':'user','content':'Hi'}],settings),'{"final":')
        self.assertTrue(model.last_metrics['truncated'])
