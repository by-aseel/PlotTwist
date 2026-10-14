"""Real local LLM generation through Ollama; the agent still owns its ReAct loop."""
from __future__ import annotations
import json
import os
import threading
import time
from urllib.parse import urlparse
from urllib.request import Request, ProxyHandler, build_opener
from urllib.error import HTTPError, URLError

class LocalModelError(RuntimeError):
    def __init__(self, message, code=None):
        self.code = code
        super().__init__(message)

def native_tools():
    """Typed definitions; the application still validates and executes every call."""
    string = {"type": "string"}
    tools = {
        "search_experiences": ({"query": string, "guests": {"type": ["integer", "null"]}}, ["query"]),
        "estimate_event": ({"experience_id": {"type": "string", "enum": ["birthday", "city", "corporate", "custom"]}, "guests": {"type": "integer"}}, ["experience_id", "guests"]),
        "record_customer_interest": ({"email": string, "name": string, "message": string}, ["email", "name", "message"]),
        "record_feedback": ({"question": string}, ["question"]),
    }
    descriptions = {
        "search_experiences": "Look up catalogue recommendations. Only query and optional guests are accepted; no budget or price argument exists.",
        "estimate_event": "Check the package capacity and indicative starting price for a guest count. Use after search when planning a specific group.",
        "record_customer_interest": "Save locally only with customer consent and customer-supplied name/email. Does not send mail or book.",
        "record_feedback": "Save feedback or an unanswered customer question locally. Does not send a message or establish an answer.",
    }
    definitions = []
    for name, (properties, required) in tools.items():
        definitions.append({"type": "function", "function": {"name": name, "description": descriptions[name],
            "parameters": {"type": "object", "properties": properties, "required": required, "additionalProperties": False}}})
    return definitions

class OllamaModel:
    def __init__(self, base_url=None, transport=None):
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        parsed = urlparse(self.base_url)
        if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("Local mode requires a loopback Ollama URL")
        self.transport = transport or self._request
        self._opener = build_opener(ProxyHandler({}))
        self.last_metrics = {}
        self._lock = threading.Lock()

    def _request(self, payload):
        req = Request(self.base_url + "/api/chat", data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json"}, method="POST")
        try:
            with self._opener.open(req, timeout=180) as response:
                return json.load(response)
        except HTTPError as exc:
            raise LocalModelError(f"Ollama returned HTTP {exc.code}. Check the model is downloaded and the request options are supported.", exc.code) from None
        except (URLError, TimeoutError):
            raise LocalModelError("Local model server is unavailable or timed out. Start ollama serve and download the selected model.") from None

    def complete(self, messages, settings):
        systems = [m["content"] for m in messages if m["role"] == "system"]
        conversation = []
        for message in messages:
            if message["role"] == "system":
                continue
            item = dict(message)
            if item["role"] == "assistant":
                try:
                    parsed = json.loads(item["content"])
                    if "action" in parsed:
                        action = parsed["action"]
                        item = {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": action["tool"], "arguments": action["arguments"]}}]}
                except (ValueError, TypeError, KeyError):
                    pass
            elif item["content"].startswith("OBSERVATION_JSON:"):
                observation = json.loads(item["content"].split(":", 1)[1])
                item = {"role": "tool", "tool_name": observation["tool"], "content": json.dumps(observation["result"])}
            conversation.append(item)
        if systems:
            conversation.insert(0, {"role": "system", "content": "\n\n".join(systems) + "\nLocal transport protocol supersedes the JSON serialization instructions: for an action, call exactly one supplied native function. The application executes it and returns a tool observation. For a completed reply, write the customer-facing answer as ordinary text; the adapter serializes it as final JSON. Do not print a function call as ordinary text. In brief-plan mode, put only one short public plan sentence in content alongside the native call. Never expose private reasoning. Only the team can verify a final quote, venue, or availability; you cannot check those yourself."})
        if settings["model"].startswith("qwen3"):
            # Qwen's documented soft switch supplements the runtime switch.
            conversation[0] = {**conversation[0], "content": conversation[0]["content"] + "\n/no_think"}
        options = {key: settings[key] for key in ("temperature", "top_p", "top_k", "frequency_penalty", "presence_penalty")}
        options.update(num_predict=settings["max_tokens"], num_ctx=8192,
                       seed=settings.get("generation_seed", -1), repeat_penalty=1.0, min_p=0.0)
        payload = {"model": settings["model"], "messages": conversation, "tools": native_tools(),
                   "stream": False, "keep_alive": "10m", "options": options}
        if settings["model"].startswith("qwen3"):
            payload["think"] = False
        with self._lock:
            started = time.perf_counter()
            response = self.transport(payload)
            self.last_metrics = {key: response.get(key) for key in (
                "model", "created_at", "done_reason", "total_duration", "load_duration",
                "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration")}
            self.last_metrics["request_elapsed_ms"] = round((time.perf_counter()-started)*1000, 2)
            self.last_metrics["generation_seed"] = options["seed"]
            if not response.get("done"):
                raise LocalModelError("Local model response did not finish")
            message = response.get("message", {})
            content = message.get("content", "")
            if "</think>" in content or "<think>" in content:
                raise LocalModelError("Model ignored the no-thinking output protocol; private reasoning was not exposed")
            calls = message.get("tool_calls", [])
            if not calls and isinstance(content, str):
                # Some small models print a native call in content instead of
                # using tool_calls. Detect that proposal before treating text as
                # a final answer; validation/consent still belong to the graph.
                proposals = []
                decoder = json.JSONDecoder()
                for offset, char in enumerate(content):
                    if char != "{":
                        continue
                    try:
                        value, _ = decoder.raw_decode(content[offset:])
                    except ValueError:
                        continue
                    if isinstance(value, dict) and isinstance(value.get("name"), str) and isinstance(value.get("arguments"), dict):
                        proposals.append({"function": {"name": value["name"], "arguments": value["arguments"]}})
                if proposals:
                    calls = proposals
                    self.last_metrics["tool_proposal_source"] = "model_content"
                    content = ""  # A proposed save is not an acknowledgement.
            if calls:
                if len(calls) != 1:
                    # Feed a protocol error back through the graph rather than silently dropping calls.
                    return json.dumps({"protocol_error": "Request exactly one tool call at a time."})
                function = calls[0]["function"]
                result = {"action": {"tool": function["name"], "arguments": function["arguments"]}}
                if settings["reasoning"] == "brief_plan" and content.strip():
                    result["plan"] = content.strip()[:400]
                return json.dumps(result)
            if not isinstance(content, str) or not content.strip():
                raise LocalModelError("Local model returned no answer content")
            if response.get("done_reason") == "length":
                # Keep the original partial draft for the graph's JSON recovery path.
                self.last_metrics["truncated"] = True
                return content
            # Native tool-calling models return ordinary final text. Serialize it
            # without rewriting its claims; malformed JSON still goes to recovery.
            if content.lstrip().startswith(("{", "```")):
                return content
            return json.dumps({"final": content})
