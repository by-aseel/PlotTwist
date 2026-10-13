"""Native Google Gen AI transport with a small internal message compatibility layer.

The compatibility attributes keep C3's explicit, tested tool loop readable. All
network requests use google.genai, never the OpenAI SDK or a proxy endpoint.
Native model Content objects are carried through unchanged to preserve signatures.
"""
from __future__ import annotations
import json
import os
import time
import uuid
from types import SimpleNamespace
from google import genai
from google.genai import types

class GeminiRequestError(RuntimeError):
    def __init__(self, code, status):
        self.code = code
        super().__init__(f"Gemini request failed: {code or 'transport error'} {status or ''}. Check model access, key and quota in AI Studio.")

class GeminiClient:
    def __init__(self, api_key=None, client=None, minimum_interval=None):
        self.client = client or genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"),
            http_options=types.HttpOptions(timeout=45000, retry_options=types.HttpRetryOptions(attempts=1)))
        self.chat = SimpleNamespace(completions=self)
        self.minimum_interval = float(os.getenv("GEMINI_REQUEST_INTERVAL", "4") if minimum_interval is None else minimum_interval)
        self.last_request = 0.0

    def create(self, *, model, messages, tools=None, tool_choice="auto", temperature=0.35,
               top_p=1.0, top_k=40, frequency_penalty=0.0, presence_penalty=0.0,
               max_completion_tokens=1200, response_format=None, parallel_tool_calls=False):
        systems, contents, names, native_ids = [], [], {}, {}
        for message in messages:
            role = message["role"]
            if role == "system":
                systems.append(message["content"])
                continue
            for call in message.get("tool_calls", []):
                names[call["id"]] = call["function"]["name"]
            if message.get("_native_content") is not None:
                native_calls = [p.function_call for p in message["_native_content"].parts or [] if p.function_call]
                for call, native in zip(message.get("tool_calls", []), native_calls):
                    native_ids[call["id"]] = native.id
                contents.append(message["_native_content"])
                continue
            if role == "tool":
                name = names.get(message["tool_call_id"])
                if not name:
                    raise ValueError("Tool observation has no matching function call")
                observation = json.loads(message["content"])
                part = types.Part(function_response=types.FunctionResponse(name=name, id=native_ids.get(message["tool_call_id"], message["tool_call_id"]), response=observation))
                contents.append(types.Content(role="user", parts=[part]))
                continue
            parts = []
            if message.get("content"):
                parts.append(types.Part.from_text(text=message["content"]))
            for call in message.get("tool_calls", []):
                parts.append(types.Part.from_function_call(name=call["function"]["name"],
                    args=json.loads(call["function"]["arguments"])))
            if parts:
                contents.append(types.Content(role="model" if role == "assistant" else "user", parts=parts))
        config = dict(system_instruction="\n\n".join(systems), temperature=temperature,
            top_p=top_p, top_k=top_k, frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty, max_output_tokens=max_completion_tokens,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
        if model.startswith("gemini-2.5"):
            config["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        elif model.startswith("gemini-3"):
            config["thinking_config"] = types.ThinkingConfig(thinking_level="minimal")
        if tools:
            declarations = [types.FunctionDeclaration(name=t["function"]["name"],
                description=t["function"]["description"], parameters_json_schema=t["function"]["parameters"]) for t in tools]
            config["tools"] = [types.Tool(function_declarations=declarations)]
            forced = isinstance(tool_choice, dict)
            config["tool_config"] = types.ToolConfig(function_calling_config=types.FunctionCallingConfig(
                mode="ANY" if forced else "AUTO",
                allowed_function_names=[tool_choice["function"]["name"]] if forced else None))
        elif response_format:
            config["response_mime_type"] = "application/json"
        delay = self.minimum_interval - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)
        self.last_request = time.monotonic()
        try:
            response = self.client.models.generate_content(model=model, contents=contents,
                config=types.GenerateContentConfig(**config))
        except Exception as exc:
            # SDK error strings can contain request metadata. Never log headers/keys.
            code = getattr(exc, "code", None)
            status = getattr(exc, "status", None)
            raise GeminiRequestError(code, status) from None
        candidates = response.candidates or []
        if not candidates or not candidates[0].content:
            raise ValueError("Gemini returned no candidate content; check safety feedback")
        candidate = candidates[0]
        reason = str(getattr(candidate.finish_reason, "value", candidate.finish_reason))
        if reason == "MAX_TOKENS":
            raise ValueError("Model output reached max_tokens before completion; raise the output limit and retry")
        text, calls = [], []
        for part in candidate.content.parts or []:
            if part.text and not part.thought:
                text.append(part.text)
            if part.function_call:
                call = part.function_call
                calls.append(SimpleNamespace(id=call.id or "gemini_"+uuid.uuid4().hex,
                    function=SimpleNamespace(name=call.name, arguments=json.dumps(dict(call.args or {})))))
        message = SimpleNamespace(content="".join(text), tool_calls=calls, refusal=None,
            native_content=candidate.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason="stop")])
