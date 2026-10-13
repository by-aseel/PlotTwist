"""Native SDK contract tests: no network, no credential required."""
import json
from types import SimpleNamespace
import unittest
from google.genai import types
from gemini_client import GeminiClient, GeminiRequestError

class NativeTests(unittest.TestCase):
    def client(self, responses):
        self.requests=[]
        def generate_content(**kwargs):
            self.requests.append(kwargs)
            value=responses.pop(0)
            if isinstance(value,Exception): raise value
            return value
        return GeminiClient(client=SimpleNamespace(models=SimpleNamespace(generate_content=generate_content)), minimum_interval=0)

    def response(self, parts, reason="STOP"):
        return SimpleNamespace(candidates=[SimpleNamespace(content=types.Content(role="model",parts=parts),finish_reason=reason)])

    def test_native_function_roundtrip_preserves_content_signature_and_id(self):
        native=types.Part(function_call=types.FunctionCall(id="call-one",name="record_feedback",args={"question":"Access?"}),thought_signature=b"native-signature")
        c=self.client([self.response([native]), self.response([types.Part.from_text(text="Saved locally.")])])
        schema=[{"function":{"name":"record_feedback","description":"Log unknown questions", "parameters":{"type":"object","properties":{"question":{"type":"string"}},"required":["question"]}}}]
        messages=[{"role":"system","content":"Business facts"},{"role":"system","content":"Instructions"},{"role":"user","content":"Prior turn"},{"role":"assistant","content":"Prior answer"},{"role":"user","content":"Access?"}]
        result=c.create(model="gemini-2.5-flash-lite",messages=messages,tools=schema,tool_choice={"function":{"name":"record_feedback"}})
        reply=result.choices[0].message;call=reply.tool_calls[0]
        messages.append({"role":"assistant","content":reply.content,"_native_content":reply.native_content,"tool_calls":[{"id":call.id,"function":{"name":call.function.name,"arguments":call.function.arguments}}]})
        messages.append({"role":"tool","tool_call_id":call.id,"content":json.dumps({"ok":True,"saved_locally":True})})
        c.create(model="gemini-2.5-flash-lite",messages=messages,tools=schema)
        first,second=self.requests
        self.assertIn("Business facts",first["config"].system_instruction)
        self.assertIn("Instructions",first["config"].system_instruction)
        self.assertTrue(first["config"].automatic_function_calling.disable)
        self.assertEqual(first["config"].tool_config.function_calling_config.allowed_function_names,["record_feedback"])
        self.assertEqual(second["contents"][-2].parts[0].thought_signature,b"native-signature")
        observation=second["contents"][-1].parts[0].function_response
        self.assertEqual((observation.name,observation.id),("record_feedback","call-one"))
        self.assertTrue(observation.response["saved_locally"])
        self.assertEqual([x.role for x in first["contents"]],["user","model","user"])

    def test_json_mode_controls_native_output_budget(self):
        c=self.client([self.response([types.Part.from_text(text='{"final":"OK"}')])])
        result=c.create(model="gemini-2.5-flash-lite",messages=[{"role":"user","content":"Hello"}],temperature=.2,top_p=.7,top_k=20,frequency_penalty=.3,presence_penalty=.4,max_completion_tokens=999,response_format={"type":"json_object"})
        config=self.requests[0]["config"]
        self.assertEqual((config.temperature,config.top_p,config.top_k,config.frequency_penalty,config.presence_penalty,config.max_output_tokens),(.2,.7,20,.3,.4,999))
        self.assertEqual(config.response_mime_type,"application/json")
        self.assertEqual(json.loads(result.choices[0].message.content),{"final":"OK"})

    def test_truncated_or_blocked_response_is_not_success(self):
        for response in [self.response([types.Part.from_text(text='{"final":')],"MAX_TOKENS"),SimpleNamespace(candidates=[])]:
            with self.subTest(response=response),self.assertRaises(ValueError):
                self.client([response]).create(model="gemini-2.5-flash-lite",messages=[{"role":"user","content":"Hi"}])

    def test_remote_error_never_exposes_raw_request_or_retries(self):
        class RemoteError(Exception):
            code=403
            status="PERMISSION_DENIED"
        c=self.client([RemoteError("secret-in-error-text")])
        with self.assertRaises(GeminiRequestError) as caught:
            c.create(model="gemini-3.5-flash-lite",messages=[{"role":"user","content":"Hi"}])
        self.assertNotIn("secret-in-error-text",str(caught.exception))
        self.assertEqual(caught.exception.code,403)
        self.assertEqual(len(self.requests),1)

    def test_current_model_thinking_and_private_text(self):
        c=self.client([self.response([types.Part(text="private",thought=True),types.Part.from_text(text="Hello")])])
        r=c.create(model="gemini-3.5-flash-lite",messages=[{"role":"user","content":"Hi"}])
        self.assertEqual(self.requests[0]["config"].thinking_config.thinking_level.value,"MINIMAL")
        self.assertEqual(r.choices[0].message.content,"Hello")
