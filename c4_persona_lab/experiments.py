"""Controlled, repeatable experiment runner with raw outputs and honest evidence labels.

Run demo to validate the pipeline. Run live with your own API key to gather LLM
evidence. The script never substitutes demo output after a live failure.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from personas import DEFAULT_SETTINGS, PERSONAS, normalize_settings
from plottwist_agent import build_agent

CASES = [
    {"id": "birthday_fit", "prompt": "Recommend a birthday mystery for 8 guests with a $300 budget.", "expected_tools": ["search_experiences", "estimate_event"], "rubric": "Fits 8; USD 240 group starting price; 2 hours; indicative quote; useful next question."},
    {"id": "corporate_budget", "prompt": "Plan a corporate mission for 24 colleagues. Our budget is $500. Can it fit?", "expected_tools": ["search_experiences", "estimate_event"], "rubric": "Corporate capacity fits; USD 650 exceeds USD 500; do not invent a discount."},
    {"id": "unknown_access", "prompt": "Do you offer wheelchair access at a confirmed venue next Friday?", "expected_tools": ["record_feedback"], "rubric": "Does not invent access/venue/availability; records question; identifies need for team confirmation."},
    {"id": "save_enquiry", "prompt": "My name is Aseel, my email is aseel@example.com. Please save my enquiry for a birthday mystery for 10 guests.", "expected_tools": ["record_customer_interest"], "rubric": "Valid local enquiry; exact supplied name/email; no claim of email or booking."},
    {"id": "story_concept", "prompt": "Design a custom story adventure for 14 guests who love time travel.", "expected_tools": ["search_experiences", "estimate_event"], "rubric": "Original coherent concept; custom scope and price remain quote-only; practical personalization question."},
    {"id": "oversized_group", "prompt": "I want Birthday Mystery Nights for 90 guests. What works?", "expected_tools": ["search_experiences"], "rubric": "Explains standard birthday capacity 6-20; offers custom scoping instead of a false fit."},
    {"id": "team_facts", "prompt": "Who are Aseel, Noah, Jiso and Felix on your team?", "expected_tools": [], "rubric": "Correct four team names and roles; no invented credentials."},
]

def experiment_variants(model="gpt-4.1-mini", compare_model=None):
    """Each single-axis row changes one field from an identical baseline."""
    baseline = {**DEFAULT_SETTINGS, "model": model}
    variants = [{"id": "baseline", "factor": "baseline", "change": "Clue / direct / zero task demos / system instructions", "settings": baseline}]
    changes = [
        ("brief_plan", "reasoning", "brief_plan"),
        ("few_shot", "examples", "few_shot"),
        ("in_message", "instruction_role", "user"),
        ("compact_instructions", "instruction_detail", "compact"),
        ("temperature_low", "temperature", 0.1),
        ("temperature_high", "temperature", 0.85),
        ("top_p_low", "top_p", 0.4),
        ("frequency_high", "frequency_penalty", 0.8),
        ("presence_high", "presence_penalty", 0.8),
        ("short_output", "max_tokens", 180),
        ("long_output", "max_tokens", 1200),
    ]
    for variant_id, key, value in changes:
        variants.append({"id": variant_id, "factor": key, "change": f"{key}: {baseline[key]} -> {value}", "settings": {**baseline, key: value}})
    for persona in ("cipher", "muse"):
        variants.append({"id": persona + "_persona", "factor": "persona_bundle", "change": "Composite persona prompt, task and matching configuration; not a single-factor causal claim", "settings": {**baseline, "persona": persona, **PERSONAS[persona]["config"]}})
        variants.append({"id": persona + "_prompt_only", "factor": "persona", "change": f"Persona prompt/task only: clue -> {persona}; baseline sampling retained", "settings": {**baseline, "persona": persona}})
    if compare_model:
        variants.append({"id": "alternate_model", "factor": "model", "change": f"model: {model} -> {compare_model}", "settings": {**baseline, "model": compare_model}})
    return variants

def evaluate_result(result, case, elapsed_ms):
    """Mechanical checks, not a judge of creativity, naturalness, or overall quality."""
    actions = [x for x in result["trace"] if x["type"] == "action"]
    observations = [x for x in result["trace"] if x["type"] == "observation"]
    tool_names = [x["tool"] for x in actions]
    errors = sum(x["type"] in ("error", "parse_error", "budget") for x in result["trace"])
    tool_errors = sum(not x["result"].get("ok", False) for x in observations)
    expected = set(case["expected_tools"])
    actual = set(tool_names)
    # Saving enquiries may reasonably also look up the requested package; recall
    # and exact match are separately exposed rather than conflating the two.
    return {
        "expected_tools_observed": expected <= actual,
        "exact_tool_set_match": expected == actual,
        "tool_calls": len(actions), "tool_errors": tool_errors,
        "format_or_runtime_errors": errors,
        "completed": result["route"] not in ("error", "budget_exhausted"),
        "latency_ms": round(elapsed_ms, 2), "reply_words": len(result["reply"].split()),
        "model_calls": result.get("model_calls", 0),
        "successful_local_saves": sum(x["result"].get("saved_locally", False) for x in observations),
    }

def write_report(path, records, variants, mode, repeats, seed):
    grouped = defaultdict(list)
    for row in records:
        grouped[row["variant"]].append(row)
    lines = ["# PlotTwist C4 experiment comparison", "", f"Evidence mode: **{mode.upper()}**. Repeats requested: {repeats}. Shuffle seed: {seed}.", ""]
    if mode == "demo":
        lines += ["**These are deterministic simulator checks, not LLM findings.** The offline policy scripts persona wording and ignores sampling values. Repeated outputs and low latency cannot establish which prompt, persona or generation settings work best on a language model. Run the live command and complete the human ratings before making that claim.", ""]
    else:
        lines += ["These rows contain actual API attempts, including any failures. Configuration comparisons are descriptive; review all raw outputs and fill the human rubric before choosing a winner. Model aliases can change, so use a dated model snapshot for stronger reproducibility.", ""]
    lines += ["## Observed mechanical metrics", "", "| Variant | Runs | Expected tools observed | Completed | Tool errors | Mean words | Mean ms |", "|---|---:|---:|---:|---:|---:|---:|"]
    for variant in variants:
        rows = grouped[variant["id"]]
        if not rows:
            continue
        lines.append(f"| {variant['id']} | {len(rows)} | {sum(r['expected_tools_observed'] for r in rows)}/{len(rows)} | {sum(r['completed'] for r in rows)}/{len(rows)} | {sum(r['tool_errors'] for r in rows)} | {statistics.mean(r['reply_words'] for r in rows):.1f} | {statistics.mean(r['latency_ms'] for r in rows):.1f} |")
    lines += ["", "These checks measure tool execution and response size. They do not prove factual correctness, naturalness, creativity, or task completion. An extra valid tool call can lower exact-tool-set match without being a failure.", "", "## Paired study design", "", "The same cases and repetition indices run under each variant. A seeded shuffle limits order bias. Single-axis rows differ from baseline in exactly one setting; persona bundles deliberately change the prompt, task and configuration together, so they are not single-factor causal comparisons. Prompt-only persona rows help separate wording from the bundle. Temperature is changed with top-p held at 1; the top-p variant holds temperature fixed. API sampling remains stochastic even when the runner order is reproducible.", "", "| Variant | Factor | Change |", "|---|---|---|"]
    for variant in variants:
        lines.append(f"| {variant['id']} | {variant['factor']} | {variant['change']} |")
    lines += ["", "## What the course comparisons mean here", "", "- Direct vs brief-plan is a CoT-style prompting comparison using a short, user-facing action rationale. It does not request, expose, or measure private chain-of-thought.", "- Zero-shot means zero solved *task* demonstrations. Both arms keep one greeting/protocol format example because the assignment explicitly requires a worked example inside the instructions. Few-shot adds two complete tool-use demonstrations.", "- System vs in-message moves the same experimental instruction/persona/tool-description block. Fixed business facts and the JSON protocol boundary remain system-level in both arms.", "- The compact-instructions variant isolates the effect of the detailed instruction block while retaining the protocol, factual boundaries and enquiry permission rule.", "- `top_k` is unavailable in OpenAI Chat Completions and is reported as not applicable. It is never silently passed or ignored. The UI's `max_tokens` maps to the API's `max_completion_tokens`.", "- An alternate model is optional because access varies. Use `--compare-model gpt-4.1` for a supported non-reasoning Chat Completions comparison if your account has access. Unsupported parameter/model combinations remain errors in the logs.", "", "## Human rubric and reflection", "", "Use `human_ratings.csv`. Blind the variant labels when possible and rate each criterion from 1 (poor) to 5 (excellent). Review the case-specific rubric, the reply and observations together.", "", "1. Factual grounding: correct catalogue facts; no invented prices, availability or promises.", "2. Task usefulness: the recommendation answers the actual request and identifies missing inputs.", "3. Tool judgment: appropriate selection, sequence, validation and recovery.", "4. Persona fit: vocabulary, structure and task emphasis match Clue, Cipher or Muse.", "5. Naturalness: clear, respectful wording with appropriate length.", "6. Creativity: coherent original story ideas where requested, marked as concepts.", "", "Suggested decision rule: first reject variants with serious factual or privacy failures. Compare mean usefulness and naturalness on the same cases, then use latency and verbosity as secondary criteria. Report per-case variation and sample size; do not treat a small mean difference as proof.", "", "Reflection prompts: Which persona was most useful for which task? Which single-axis prompt/configuration choice helped? Did tool observations change the next action? How did the full instruction block differ from compact instructions? What failures or implementation challenges remain?", "", "**Current conclusion:** " + ("The saved demo run establishes a working experiment harness and action-observation-final pipeline. A best LLM persona/configuration has not been established because no live LLM evidence was collected in this run." if mode == "demo" else "Inspect failures and complete human ratings before stating which configuration worked best."), ""]
    path.write_text("\n".join(lines), encoding="utf-8")

def run_experiments(mode="demo", repeats=2, output="experiments/demo", model="gpt-4.1-mini", compare_model=None, variant_ids=None, seed=42):
    if mode not in ("demo", "live"):
        raise ValueError("Experiments require explicit demo or live mode")
    if not isinstance(repeats, int) or repeats < 1:
        raise ValueError("repeats must be a positive integer")
    variants = experiment_variants(model, compare_model)
    if variant_ids:
        wanted = set(variant_ids)
        known = {v["id"] for v in variants}
        if not wanted <= known:
            raise ValueError("Unknown variants: " + ", ".join(sorted(wanted - known)))
        variants = [v for v in variants if v["id"] in wanted]
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    # An isolated DB keeps synthetic experiment enquiries out of the interactive app.
    agent = build_agent(mode=mode, db_path=destination / "experiment_records.sqlite3")
    jobs = [(variant, case, repeat) for repeat in range(1, repeats + 1) for case in CASES for variant in variants]
    random.Random(seed).shuffle(jobs)
    records, raw = [], []
    started_at = datetime.now(timezone.utc).isoformat()
    for index, (variant, case, repeat) in enumerate(jobs, 1):
        run_id = f"{variant['id']}--{case['id']}--r{repeat}"
        agent.store.clear_session(run_id)
        settings = normalize_settings(variant["settings"])
        started = time.perf_counter()
        result = agent.respond(case["prompt"], session_id=run_id, settings=settings)
        metric = evaluate_result(result, case, (time.perf_counter() - started) * 1000)
        row = {"run_id": run_id, "variant": variant["id"], "factor": variant["factor"], "case": case["id"], "repeat": repeat, "mode": mode, "model": settings["model"] if mode == "live" else "deterministic-demo", **metric}
        records.append(row)
        raw.append({**row, "prompt": case["prompt"], "settings": settings, "reply": result["reply"], "route": result["route"], "trace": result["trace"], "records": agent.store.records(run_id), "rubric": case["rubric"]})
        if mode == "live":
            print(f"[{index}/{len(jobs)}] {run_id}: {result['route']}", flush=True)
        # Save a checkpoint after every attempt so paid live runs survive interruption.
        (destination / "raw_traces.json").write_text(json.dumps({"metadata": {"mode": mode, "started_at_utc": started_at, "repeats": repeats, "seed": seed, "planned_runs": len(jobs), "completed_runs": len(raw), "demo_is_not_llm_evidence": mode == "demo"}, "runs": raw}, indent=2, ensure_ascii=False), encoding="utf-8")
    with (destination / "metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    rating_fields = ["run_id", "case", "factual_grounding_1_5", "task_usefulness_1_5", "tool_judgment_1_5", "persona_fit_1_5", "naturalness_1_5", "creativity_1_5", "serious_failure", "notes"]
    with (destination / "human_ratings.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rating_fields)
        writer.writeheader()
        writer.writerows({"run_id": row["run_id"], "case": row["case"]} for row in records)
    write_report(destination / "comparison.md", records, variants, mode, repeats, seed)
    return records

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("demo", "live"), default="demo")
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--output", default=None)
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--compare-model", default=None)
    parser.add_argument("--variants", default=None, help="Comma-separated variant IDs; omit for the full matrix")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    output = args.output or f"experiments/{args.mode}"
    rows = run_experiments(args.mode, args.repeats, output, args.model, args.compare_model, args.variants.split(",") if args.variants else None, args.seed)
    print(f"Saved {len(rows)} {args.mode.upper()} attempts to {Path(output).resolve()}")
    if args.mode == "demo":
        print("Simulator verification only. No LLM prompt/persona/configuration conclusions can be inferred.")
