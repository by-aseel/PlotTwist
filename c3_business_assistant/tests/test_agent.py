"""No API key or network required. Fake completions exercise the real live loop."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plottwist_agent import ConfigurationError, EventStore, PlotTwistAgent, SessionTools, route_message


KNOWLEDGE = {
    "business_summary.txt": "PlotTwist Experiences. Birthday Mystery Nights from $240/group. Aseel, Noah, Jiso, Felix.",
    "about_business.pdf": "City Quests from $90/group. Corporate Missions from $650/group. All fictional USD prices. Custom Story Adventures: quote only.",
}


def completion(content=None, tool=None, arguments=None, call_id="call_1"):
    calls = [] if tool is None else [SimpleNamespace(id=call_id, function=SimpleNamespace(name=tool, arguments=arguments))]
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content, tool_calls=calls))])


class FakeClient:
    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls.append(copy.deepcopy(kwargs))
        if not self.answers:
            raise AssertionError("Unexpected additional model call")
        result = self.answers.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.knowledge_patch = patch("plottwist_agent.load_knowledge", return_value=KNOWLEDGE)
        self.knowledge_patch.start()
        self.env_patch = patch.dict(os.environ, {"GEMINI_API_KEY": ""})
        self.env_patch.start()
        self.dotenv_patch = patch("dotenv.load_dotenv")
        self.dotenv_patch.start()
        self.agents = []

    def tearDown(self):
        for agent in self.agents:
            agent.store.close()
        self.dotenv_patch.stop()
        self.env_patch.stop()
        self.knowledge_patch.stop()
        self.temp.cleanup()

    def agent(self, **kwargs):
        kwargs.setdefault("db_path", Path(self.temp.name) / f"agent-{len(self.agents)}.sqlite3")
        agent = PlotTwistAgent(**kwargs)
        self.agents.append(agent)
        return agent

    def test_mode_and_both_knowledge_sources(self):
        agent = self.agent()
        self.assertEqual(agent.mode, "demo")
        self.assertIn("SOURCE: business_summary.txt", agent.system_prompt)
        self.assertIn("SOURCE: about_business.pdf", agent.system_prompt)
        with self.assertRaises(ConfigurationError):
            self.agent(mode="live")

    def test_three_routes_and_word_boundaries(self):
        self.assertEqual(route_message("What services do you offer?"), "general_question")
        self.assertEqual(route_message("I want to book a birthday mystery"), "lead_collection")
        self.assertEqual(route_message("I want a birthday mystery for 12 people."), "lead_collection")
        self.assertEqual(route_message("The puzzles were too difficult."), "feedback_unanswered")
        self.assertEqual(route_message("The puzzle was confusing"), "feedback_unanswered")
        self.assertEqual(route_message("What is your refund policy?"), "feedback_unanswered")
        self.assertNotEqual(route_message("Do you have Facebook?"), "lead_collection")
        self.assertEqual(route_message("cancel", collecting_lead=True), "lead_collection")

    def test_multiturn_lead_and_session_isolation(self):
        agent = self.agent(mode="demo")
        history = []
        for message in ["I want to book a birthday for 12 people.", "My name is Mira.", "mira@example.com"]:
            result = agent.respond(message, history, "guest-A")
            history += [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
        self.assertIn("saved locally", result["reply"])
        records = agent.records("guest-A")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["data"]["name"], "Mira")
        self.assertIn("12 people", records[0]["data"]["message"])
        self.assertEqual(agent.records("guest-B"), [])
        other = agent.respond("other@example.com", session_id="guest-B")
        self.assertIn("your name", other["reply"])
        self.assertEqual(agent.stats("guest-B")["leads"], 0)

    def test_demo_unknown_question_is_really_logged(self):
        agent = self.agent(mode="demo")
        result = agent.respond("Are dogs welcome?", session_id="questions")
        self.assertEqual(result["route"], "feedback_unanswered")
        self.assertEqual(agent.records("questions")[0]["data"]["question"], "Are dogs welcome?")
        self.assertEqual(next(t for t in result["trace"] if t["stage"] == "tool")["source"], "deterministic_demo")

    def test_live_tool_roundtrip_keeps_history_and_returns_observation(self):
        fake = FakeClient(
            completion(tool="record_customer_interest", arguments=json.dumps({"email": "mira@example.com", "name": "Mira", "message": "Birthday for 12"})),
            completion("Your enquiry was saved locally."),
        )
        agent = self.agent(mode="live", client=fake)
        history = [{"role": "user", "content": "I want a birthday for 12. My name is Mira."}, {"role": "assistant", "content": "What is your email?"}]
        result = agent.respond("mira@example.com", history, "live-A", {"reflection": False})
        self.assertEqual(agent.stats("live-A")["leads"], 1)
        observation = next(x for x in fake.calls[1]["messages"] if x["role"] == "tool")
        self.assertEqual(observation["tool_call_id"], "call_1")
        self.assertTrue(json.loads(observation["content"])["ok"])
        self.assertIn(history[0], fake.calls[0]["messages"])
        self.assertEqual(result["reply"], "Your enquiry was saved locally.")
        self.assertEqual(result["mode"], "live")

    def test_malformed_model_arguments_reach_model_as_error(self):
        fake = FakeClient(completion(tool="record_feedback", arguments="{broken"), completion("The feedback was not saved."))
        agent = self.agent(mode="live", client=fake)
        agent.respond("I have feedback", session_id="bad-json", settings={"reflection": False})
        observation = next(x for x in fake.calls[1]["messages"] if x["role"] == "tool")
        self.assertFalse(json.loads(observation["content"])["ok"])
        self.assertEqual(agent.records("bad-json"), [])

    def test_model_cannot_invent_customer_details_or_session_scope(self):
        invented = {"email": "invented@example.com", "name": "Felix", "message": "Birthday"}
        fake = FakeClient(completion(tool="record_customer_interest", arguments=json.dumps(invented)), completion("Please share your contact details."))
        agent = self.agent(mode="live", client=fake)
        result = agent.respond("I'd like to book a birthday.", session_id="A", settings={"reflection": False})
        self.assertEqual(agent.records("A"), [])
        tool = next(x for x in result["trace"] if x["stage"] == "tool")
        self.assertEqual(tool["result"]["kind"], "validation_error")
        extra = agent._call_tool("record_feedback", {"question": "hi", "session_id": "victim"}, "A", [], "hi")
        self.assertFalse(extra["ok"])

    def test_live_failure_does_not_fall_back_to_demo(self):
        fake = FakeClient(RuntimeError("simulated API failure containing secret detail"))
        agent = self.agent(mode="live", client=fake)
        result = agent.respond("What are your services?", session_id="fail")
        self.assertEqual(result["mode"], "live")
        self.assertIn("live model request failed", result["reply"])
        self.assertNotIn("secret detail", json.dumps(result))
        self.assertEqual(agent.records("fail"), [])

    def test_live_reflection_logs_actual_draft_and_revision(self):
        draft = "Custom adventures cost $50."
        revised = "Custom Story Adventures are quote only."
        fake = FakeClient(completion(draft), completion(json.dumps({"revised_reply": revised, "checks": ["Removed unsupported price."]})))
        agent = self.agent(mode="live", client=fake)
        result = agent.respond("Tell me about custom adventures.")
        audit = next(x for x in result["trace"] if x["stage"] == "reflection")
        self.assertEqual(audit["draft"], draft)
        self.assertEqual(audit["revised"], revised)
        self.assertTrue(audit["changed"])
        self.assertEqual(result["reply"], revised)
        self.assertNotIn("tools", fake.calls[1])

    def test_reflection_failure_is_visible_and_keeps_real_draft(self):
        fake = FakeClient(completion("Hello from Clue."), completion("not-json"))
        agent = self.agent(mode="live", client=fake)
        result = agent.respond("Hello")
        self.assertEqual(result["reply"], "Hello from Clue.")
        self.assertEqual(result["trace"][-1]["status"], "failed_draft_retained")

    def test_tool_validation_and_storage_errors(self):
        agent = self.agent(mode="demo")
        tools = agent.tools_for("local")
        self.assertFalse(tools.record_customer_interest("not-email", "Mira", "Birthday")["ok"])
        self.assertFalse(tools.record_feedback("")["ok"])
        with self.assertLogs("plottwist.c3", level="ERROR"):
            with patch.object(agent.store, "append", side_effect=sqlite3.OperationalError("disk full")):
                self.assertEqual(tools.record_feedback("A concern")["kind"], "storage_error")

    def test_durable_deduplicated_records_and_scoped_export(self):
        agent = self.agent(mode="demo")
        first = agent.tools_for("one").record_feedback("Please add hints")
        second = agent.tools_for("one").record_feedback("Please add hints")
        agent.tools_for("two").record_feedback("Private to session two")
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(second["status"], "already_recorded")
        exported = Path(agent.export_records("one", Path(self.temp.name) / "export.json")).read_text()
        self.assertNotIn("Private to session two", exported)
        reopened = EventStore(agent.store.path)
        try:
            self.assertEqual(len(reopened.records("one")), 1)
        finally:
            reopened.close()

    def test_cancel_pending_lead_does_not_record_or_keep_contact(self):
        agent = self.agent(mode="demo")
        agent.respond("I want to book. My name is Mira.", session_id="stop")
        result = agent.respond("cancel", session_id="stop")
        self.assertIn("stopped", result["reply"])
        self.assertFalse(agent.store.state("stop")["collecting_lead"])
        self.assertEqual(agent.records("stop"), [])

    def test_tool_loop_has_a_bound(self):
        fake = FakeClient(*(completion(tool="record_feedback", arguments='{"question":"Repeated"}', call_id=f"call_{i}") for i in range(6)))
        agent = self.agent(mode="live", client=fake)
        result = agent.respond("Feedback", settings={"reflection": False})
        self.assertEqual(len(fake.calls), 6)
        self.assertIn("tool-call limit", result["reply"])
        self.assertEqual(len(agent.records()), 1)

    def test_live_cancel_is_enforced_without_a_model_call(self):
        fake = FakeClient()
        agent = self.agent(mode="live", client=fake)
        agent.store.save_state("cancel-live", {"collecting_lead": True, "lead": {"name": "Mira"}})
        result = agent.respond("Don't save this. Stop.", session_id="cancel-live")
        self.assertIn("stopped", result["reply"])
        self.assertEqual(fake.calls, [])
        self.assertEqual(agent.store.state("cancel-live")["lead"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
