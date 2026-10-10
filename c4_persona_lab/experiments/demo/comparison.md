# PlotTwist C4 experiment comparison

Evidence mode: **DEMO**. Repeats requested: 2. Shuffle seed: 42.

**These are deterministic simulator checks, not LLM findings.** The offline policy scripts persona wording and ignores sampling values. Repeated outputs and low latency cannot establish which prompt, persona or generation settings work best on a language model. Run the live command and complete the human ratings before making that claim.

## Observed mechanical metrics

| Variant | Runs | Expected tools observed | Completed | Tool errors | Mean words | Mean ms |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 14 | 14/14 | 14/14 | 0 | 38.7 | 11.4 |
| brief_plan | 14 | 14/14 | 14/14 | 0 | 38.7 | 11.2 |
| few_shot | 14 | 14/14 | 14/14 | 0 | 38.7 | 9.2 |
| in_message | 14 | 14/14 | 14/14 | 0 | 38.7 | 9.5 |
| compact_instructions | 14 | 14/14 | 14/14 | 0 | 38.7 | 14.5 |
| temperature_low | 14 | 14/14 | 14/14 | 0 | 38.7 | 11.8 |
| temperature_high | 14 | 14/14 | 14/14 | 0 | 38.7 | 11.2 |
| top_p_low | 14 | 14/14 | 14/14 | 0 | 38.7 | 11.2 |
| frequency_high | 14 | 14/14 | 14/14 | 0 | 38.7 | 12.8 |
| presence_high | 14 | 14/14 | 14/14 | 0 | 38.7 | 15.0 |
| short_output | 14 | 14/14 | 14/14 | 0 | 38.7 | 9.3 |
| long_output | 14 | 14/14 | 14/14 | 0 | 38.7 | 15.9 |
| cipher_persona | 14 | 14/14 | 14/14 | 0 | 34.7 | 10.9 |
| cipher_prompt_only | 14 | 14/14 | 14/14 | 0 | 34.7 | 14.0 |
| muse_persona | 14 | 14/14 | 14/14 | 0 | 48.9 | 12.5 |
| muse_prompt_only | 14 | 14/14 | 14/14 | 0 | 48.9 | 10.4 |

These checks measure tool execution and response size. They do not prove factual correctness, naturalness, creativity, or task completion. An extra valid tool call can lower exact-tool-set match without being a failure.

## Paired study design

The same cases and repetition indices run under each variant. A seeded shuffle limits order bias. Single-axis rows differ from baseline in exactly one setting; persona bundles deliberately change the prompt, task and configuration together, so they are not single-factor causal comparisons. Prompt-only persona rows help separate wording from the bundle. Temperature is changed with top-p held at 1; the top-p variant holds temperature fixed. API sampling remains stochastic even when the runner order is reproducible.

| Variant | Factor | Change |
|---|---|---|
| baseline | baseline | Clue / direct / zero task demos / system instructions |
| brief_plan | reasoning | reasoning: direct -> brief_plan |
| few_shot | examples | examples: zero_shot -> few_shot |
| in_message | instruction_role | instruction_role: system -> user |
| compact_instructions | instruction_detail | instruction_detail: full -> compact |
| temperature_low | temperature | temperature: 0.45 -> 0.1 |
| temperature_high | temperature | temperature: 0.45 -> 0.85 |
| top_p_low | top_p | top_p: 1.0 -> 0.4 |
| frequency_high | frequency_penalty | frequency_penalty: 0.15 -> 0.8 |
| presence_high | presence_penalty | presence_penalty: 0.0 -> 0.8 |
| short_output | max_tokens | max_tokens: 700 -> 180 |
| long_output | max_tokens | max_tokens: 700 -> 1200 |
| cipher_persona | persona_bundle | Composite persona prompt, task and matching configuration; not a single-factor causal claim |
| cipher_prompt_only | persona | Persona prompt/task only: clue -> cipher; baseline sampling retained |
| muse_persona | persona_bundle | Composite persona prompt, task and matching configuration; not a single-factor causal claim |
| muse_prompt_only | persona | Persona prompt/task only: clue -> muse; baseline sampling retained |

## What the course comparisons mean here

- Direct vs brief-plan is a CoT-style prompting comparison using a short, user-facing action rationale. It does not request, expose, or measure private chain-of-thought.
- Zero-shot means zero solved *task* demonstrations. Both arms keep one greeting/protocol format example because the assignment explicitly requires a worked example inside the instructions. Few-shot adds two complete tool-use demonstrations.
- System vs in-message moves the same experimental instruction/persona/tool-description block. Fixed business facts and the JSON protocol boundary remain system-level in both arms.
- The compact-instructions variant isolates the effect of the detailed instruction block while retaining the protocol, factual boundaries and enquiry permission rule.
- `top_k` is unavailable in OpenAI Chat Completions and is reported as not applicable. It is never silently passed or ignored. The UI's `max_tokens` maps to the API's `max_completion_tokens`.
- An alternate model is optional because access varies. Use `--compare-model gpt-4.1` for a supported non-reasoning Chat Completions comparison if your account has access. Unsupported parameter/model combinations remain errors in the logs.

## Human rubric and reflection

Use `human_ratings.csv`. Blind the variant labels when possible and rate each criterion from 1 (poor) to 5 (excellent). Review the case-specific rubric, the reply and observations together.

1. Factual grounding: correct catalogue facts; no invented prices, availability or promises.
2. Task usefulness: the recommendation answers the actual request and identifies missing inputs.
3. Tool judgment: appropriate selection, sequence, validation and recovery.
4. Persona fit: vocabulary, structure and task emphasis match Clue, Cipher or Muse.
5. Naturalness: clear, respectful wording with appropriate length.
6. Creativity: coherent original story ideas where requested, marked as concepts.

Suggested decision rule: first reject variants with serious factual or privacy failures. Compare mean usefulness and naturalness on the same cases, then use latency and verbosity as secondary criteria. Report per-case variation and sample size; do not treat a small mean difference as proof.

Reflection prompts: Which persona was most useful for which task? Which single-axis prompt/configuration choice helped? Did tool observations change the next action? How did the full instruction block differ from compact instructions? What failures or implementation challenges remain?

**Current conclusion:** The saved demo run establishes a working experiment harness and action-observation-final pipeline. A best LLM persona/configuration has not been established because no live LLM evidence was collected in this run.
