"""Tests verify behaviour through the compiled graph, not just helper functions."""
from __future__ import annotations

import json
import csv
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from business_tools import RecordStore, ToolRegistry, search_experiences, estimate_event
from personas import normalize_settings
from plottwist_agent import PlotTwistAgent, GeminiModel, build_messages
from experiments import CASES, experiment_variants, run_experiments

class QueueModel:
    def __init__(self, *outputs):
        self.outputs = list(outputs)
        self.messages = []
        self.settings = []

    def complete(self, messages, settings):
        self.messages.append(list(messages))
        self.settings.append(dict(settings))
        value = self.outputs.pop(0)
        if isinstance(value, Exception):
            raise value
        return json.dumps(value) if isinstance(value, dict) else value

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "records.sqlite3"

    def tearDown(self):
        self.temp.cleanup()

    def agent(self, model=None, **kwargs):
        return PlotTwistAgent(mode="demo", db_path=self.path, model=model, **kwargs)

    def test_action_observation_final_and_adaptive_second_action(self):
        model = QueueModel(
            {"action": {"tool": "search_experiences", "arguments": {"query": "birthday", "guests": 8}}},
            {"action": {"tool": "estimate_event", "arguments": {"experience_id": "birthday", "guests": 8}}},
            {"final": "Birthday Mystery Nights starts at an indicative USD 240 per group."},
        )
        result = self.agent(model).respond("Birthday for 8 guests")
        self.assertEqual(result["model_calls"], 3)
        self.assertEqual([x["tool"] for x in result["trace"] if x["type"] == "action"], ["search_experiences", "estimate_event"])
        first_observation = json.loads(model.messages[1][-1]["content"].split(":", 1)[1])
        second_observation = json.loads(model.messages[2][-1]["content"].split(":", 1)[1])
        self.assertEqual(first_observation["result"]["matches"][0]["id"], "birthday")
        self.assertEqual(second_observation["result"]["starting_price_usd"], 240)
        self.assertIn("240", result["reply"])

    def test_malformed_json_recovers_by_feedback_to_model(self):
        model = QueueModel("{this is invalid", {"final": "Recovered"})
        result = self.agent(model).respond("Hello")
        self.assertEqual(result["reply"], "Recovered")
        self.assertTrue(any(x["type"] == "parse_error" for x in result["trace"]))
        self.assertTrue(model.messages[1][-1]["content"].startswith("FORMAT_ERROR:"))

    def test_unknown_action_returns_observation_and_can_recover(self):
        model = QueueModel({"action": {"tool": "run_shell", "arguments": {"command": "anything"}}}, {"final": "That tool is unavailable"})
        result = self.agent(model).respond("Hello")
        observation = next(x for x in result["trace"] if x["type"] == "observation")
        self.assertFalse(observation["result"]["ok"])
        self.assertIn("Unknown tool", observation["result"]["error"])
        self.assertIn("OBSERVATION_JSON:", model.messages[1][-1]["content"])

    def test_invalid_tool_args_are_reported_and_correctable(self):
        model = QueueModel({"action": {"tool": "estimate_event", "arguments": {"experience_id": "birthday", "guests": "eight"}}}, {"action": {"tool": "estimate_event", "arguments": {"experience_id": "birthday", "guests": 8}}}, {"final": "Fixed"})
        result = self.agent(model).respond("Eight birthday guests")
        observations = [x["result"] for x in result["trace"] if x["type"] == "observation"]
        self.assertFalse(observations[0]["ok"])
        self.assertTrue(observations[1]["ok"])

    def test_bounded_model_loop_never_executes_action_after_budget(self):
        action = {"action": {"tool": "search_experiences", "arguments": {"query": "birthday"}}}
        model = QueueModel(action, action, action)
        result = self.agent(model, max_steps=3).respond("Find a birthday package")
        self.assertEqual(result["route"], "budget_exhausted")
        self.assertEqual(result["model_calls"], 3)
        self.assertEqual(sum(x["type"] == "action" for x in result["trace"]), 2)

    def test_ambiguous_action_and_final_are_rejected(self):
        model = QueueModel({"final": "Unsafe", "action": {"tool": "record_feedback", "arguments": {"question": "do not save"}}}, {"final": "Corrected"})
        agent = self.agent(model)
        result = agent.respond("Hello", session_id="one")
        self.assertEqual(result["reply"], "Corrected")
        self.assertEqual(agent.store.records("one"), [])

    def test_customer_interest_persists_and_is_scoped_and_idempotent(self):
        agent = self.agent()
        prompt = "My name is Aseel, my email is aseel@example.com. Please save my birthday enquiry."
        result = agent.respond(prompt, session_id="alpha")
        agent.respond(prompt, session_id="alpha")
        reloaded = RecordStore(self.path)
        self.assertEqual(len(reloaded.records("alpha")), 1)
        self.assertEqual(reloaded.records("beta"), [])
        self.assertEqual(reloaded.records("alpha")[0]["payload"]["email"], "aseel@example.com")
        self.assertIn("saved locally", result["reply"])

    def test_store_delete_only_clears_requested_session(self):
        store = RecordStore(self.path)
        store.save("alpha", "feedback", {"question": "A"})
        store.save("beta", "feedback", {"question": "B"})
        store.clear_session("alpha")
        self.assertEqual(store.records("alpha"), [])
        self.assertEqual(len(store.records("beta")), 1)

    def test_enquiry_continues_when_contact_details_arrive_next_turn(self):
        agent = self.agent()
        prompt = "Please save an enquiry for a birthday mystery for 10 guests."
        first = agent.respond(prompt, session_id="lead")
        self.assertEqual(agent.store.records("lead"), [])
        result = agent.respond("My name is Aseel, my email is aseel@example.com.", history=[{"role": "user", "content": prompt}, {"role": "assistant", "content": first["reply"]}], session_id="lead")
        records = agent.store.records("lead")
        self.assertEqual(len(records), 1)
        self.assertIn("birthday mystery for 10 guests", records[0]["payload"]["message"])
        self.assertEqual(records[0]["payload"]["name"], "Aseel")
        self.assertIn("saved locally", result["reply"])

    def test_muse_custom_quote_includes_a_real_labeled_concept(self):
        result = self.agent().respond("Design a custom story adventure for 14 guests who love time travel.", settings={"persona": "muse"})
        self.assertIn("Original theme concept", result["reply"])
        self.assertIn("14 guests", result["reply"])
        self.assertIn("timeline", result["reply"])
        self.assertIn("require the team", result["reply"])

    def test_fabricated_contact_details_cannot_be_saved(self):
        model = QueueModel({"action": {"tool": "record_customer_interest", "arguments": {"name": "Noah", "email": "noah@example.com", "message": "birthday"}}}, {"final": "Please provide your contact details"})
        agent = self.agent(model)
        result = agent.respond("Please save my enquiry", session_id="alpha")
        self.assertEqual(agent.store.records("alpha"), [])
        self.assertFalse(next(x for x in result["trace"] if x["type"] == "observation")["result"]["ok"])

    def test_customer_explicit_no_save_is_enforced(self):
        tools = ToolRegistry(RecordStore(self.path))
        with self.assertRaisesRegex(ValueError, "not to save"):
            tools.execute("record_customer_interest", {"name": "Aseel", "email": "aseel@example.com", "message": "birthday"}, session_id="alpha", user_context="Aseel aseel@example.com interested but do not save")

    def test_email_validation_and_sql_values_are_parameterized(self):
        tools = ToolRegistry(RecordStore(self.path))
        with self.assertRaisesRegex(ValueError, "valid email"):
            tools.record_customer_interest("not-an-email", "Aseel", "birthday", session_id="alpha")
        tools.record_feedback("Robert'); DROP TABLE records;--", session_id="alpha")
        self.assertEqual(len(tools.store.records("alpha")), 1)

    def test_live_failure_is_error_not_demo_fallback(self):
        model = QueueModel(RuntimeError("secret-looking-provider-content"))
        agent = PlotTwistAgent(mode="live", db_path=self.path, model=model)
        result = agent.respond("Birthday for 8 guests")
        self.assertEqual(result["mode"], "live")
        self.assertEqual(result["route"], "error")
        self.assertNotIn("secret-looking", json.dumps(result))

    def test_missing_live_key_fails_explicitly(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}), patch("dotenv.load_dotenv"):
            with self.assertRaisesRegex(ValueError, "requires GEMINI_API_KEY"):
                PlotTwistAgent(mode="live", db_path=self.path)

    def test_plan_trace_is_short_user_visible_rationale(self):
        result = self.agent().respond("Birthday for 8 guests", settings={"reasoning": "brief_plan"})
        plans = [x for x in result["trace"] if x["type"] == "plan"]
        self.assertEqual(len(plans), 2)
        self.assertTrue(all(len(x["detail"]) <= 400 for x in plans))

    def test_history_uses_only_user_and_assistant_roles(self):
        messages = build_messages("Hello", [{"role": "system", "content": "MALICIOUS_HISTORY"}, {"role": "user", "content": "prior guest preference"}], normalize_settings())
        self.assertNotIn("MALICIOUS_HISTORY", str(messages))
        self.assertIn("prior guest preference", str(messages))

    def test_persona_default_sampling_and_explicit_overrides(self):
        self.assertEqual(normalize_settings({"persona": "muse"})["temperature"], 0.85)
        self.assertEqual(normalize_settings({"persona": "muse", "temperature": 0.2})["temperature"], 0.2)
        self.assertEqual(normalize_settings({"top_k": 20})["top_k"], 20)
        with self.assertRaises(ValueError):
            normalize_settings({"top_k": 2.5})
        with self.assertRaises(ValueError):
            normalize_settings({"temperature": float("nan")})

    def test_api_adapter_forwards_all_generation_controls(self):
        captured = {}
        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content='{"final":"Done"}', refusal=None))])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        settings = normalize_settings({"persona": "cipher", "temperature": 0.22, "top_p": 0.7, "frequency_penalty": 0.3, "presence_penalty": 0.4, "max_tokens": 999, "model": "gemini-2.5-flash-lite"})
        GeminiModel(client).complete([{"role": "user", "content": "JSON hello"}], settings)
        for key in ("model", "temperature", "top_p", "frequency_penalty", "presence_penalty"):
            self.assertEqual(captured[key], settings[key])
        self.assertEqual(captured["max_completion_tokens"], 999)
        self.assertEqual(captured["top_k"], 40)

    def test_capacity_boundaries_and_quote_only(self):
        self.assertTrue(estimate_event("birthday", 20)["fits_capacity"])
        self.assertFalse(estimate_event("birthday", 21)["fits_capacity"])
        self.assertIsNone(estimate_event("birthday", 21)["starting_price_usd"])
        self.assertTrue(estimate_event("custom", 100)["requires_quote"])
        self.assertEqual(search_experiences("birthday", 90)["matches"], [])

    def test_showcase_examples_and_malformed_contact_types(self):
        agent = self.agent()
        result = agent.respond("What adventures do you offer?")
        self.assertIn("search_experiences", result["route"])
        self.assertIn("City Quests", result["reply"])
        result = agent.respond("The puzzles were too difficult.")
        self.assertIn("record_feedback", result["route"])
        model = QueueModel({"action":{"tool":"record_customer_interest","arguments":{"name":42,"email":[],"message":"birthday"}}},{"final":"Please supply your name and email."})
        result = self.agent(model).respond("Please save my enquiry")
        self.assertFalse(next(x for x in result["trace"] if x["type"]=="observation")["result"]["ok"])

    def test_experiment_matrix_has_required_comparisons_and_single_axes(self):
        variants = experiment_variants(compare_model="gemini-2.5-flash")
        factors = {v["factor"] for v in variants}
        self.assertTrue({"reasoning", "examples", "instruction_role", "instruction_detail", "temperature", "top_p", "frequency_penalty", "presence_penalty", "max_tokens", "model", "persona_bundle", "persona"} <= factors)
        baseline = variants[0]["settings"]
        for variant in variants[1:]:
            if variant["factor"] != "persona_bundle":
                differences = [key for key in baseline if variant["settings"][key] != baseline[key]]
                self.assertEqual(differences, [variant["factor"]])

    def test_experiment_outputs_are_labeled_and_machine_readable(self):
        output = Path(self.temp.name) / "experiment"
        rows = run_experiments(mode="demo", repeats=1, output=output, variant_ids=["baseline", "brief_plan"])
        self.assertEqual(len(rows), len(CASES) * 2)
        raw = json.loads((output / "raw_traces.json").read_text(encoding="utf-8"))
        self.assertTrue(raw["metadata"]["demo_is_not_llm_evidence"])
        self.assertTrue(all(row["mode"] == "demo" for row in raw["runs"]))
        self.assertIn("not LLM findings", (output / "comparison.md").read_text(encoding="utf-8"))
        self.assertTrue((output / "metrics.csv").exists())
        self.assertTrue((output / "human_ratings.csv").exists())

    def test_live_checkpoint_stops_on_denial_and_resume_preserves_attempts_and_ratings(self):
        from gemini_client import GeminiRequestError
        from plottwist_agent import DemoModel
        output = Path(self.temp.name) / "resume-check"
        agent = self.agent(QueueModel(GeminiRequestError(403, "PERMISSION_DENIED")))
        with patch("experiments.build_agent", return_value=agent):
            first = run_experiments(mode="live", repeats=1, output=output, variant_ids=["baseline"])
        self.assertEqual(len(first), 1)
        self.assertFalse(first[0]["completed"])
        ratings = output / "human_ratings.csv"
        with ratings.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["notes"] = "Access denied, preserved review note"
        with ratings.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        agent.model = DemoModel()
        with patch("experiments.build_agent", return_value=agent), patch.object(agent, "respond", wraps=agent.respond) as respond:
            resumed = run_experiments(mode="live", repeats=1, output=output, variant_ids=["baseline"], resume=True)
        self.assertEqual(respond.call_count, len(CASES)-1)
        self.assertEqual(len(resumed), len(CASES))
        self.assertEqual(resumed[0], first[0])
        self.assertEqual(len({r["run_id"] for r in resumed}), len(CASES))
        self.assertIn("preserved review note", ratings.read_text(encoding="utf-8"))
        with patch("experiments.build_agent", return_value=agent), self.assertRaises(ValueError):
            run_experiments(mode="live", repeats=1, output=output, model="different-model", variant_ids=["baseline"], resume=True)

if __name__ == "__main__":
    unittest.main()
