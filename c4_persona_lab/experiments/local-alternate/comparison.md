# PlotTwist C4 experiment comparison

Evidence mode: **LOCAL**. Repeats requested: 2. Shuffle seed: 42.

These rows contain real local model-generated answers and failures from Ollama, running through the same LangGraph ReAct loop. No cloud generation fee or Gemini access is required. Sampling seeds are paired by repetition; API token and duration metadata are retained in model traces. Review responses as well as mechanical metrics before selecting a configuration.

## Observed mechanical metrics

| Variant | Runs | Expected tools observed | Completed | Tool errors | Mean words | Mean ms |
|---|---:|---:|---:|---:|---:|---:|
| alternate_model | 14 | 2/14 | 13/14 | 0 | 64.6 | 5102.8 |

These checks measure tool execution and response size. They do not prove factual correctness, naturalness, creativity, or task completion. An extra valid tool call can lower exact-tool-set match without being a failure.

## Paired study design

The same cases and repetition indices run under each variant. A seeded shuffle limits order bias. Single-axis rows differ from baseline in exactly one setting; persona bundles deliberately change the prompt, task and configuration together, so they are not single-factor causal comparisons. Prompt-only persona rows help separate wording from the bundle. Temperature is changed with top-p held at 1; the top-p variant holds temperature fixed. API sampling remains stochastic even when the runner order is reproducible.

| Variant | Factor | Change |
|---|---|---|
| alternate_model | model | model: qwen2.5:3b -> qwen2.5:1.5b |

## What the course comparisons mean here

- Direct vs brief-plan is a CoT-style prompting comparison using a short, user-facing action rationale. It does not request, expose, or measure private chain-of-thought.
- Zero-shot means zero solved *task* demonstrations. Both arms keep one greeting/protocol format example because the assignment explicitly requires a worked example inside the instructions. Few-shot adds two complete tool-use demonstrations.
- System vs in-message moves the same experimental instruction/persona/tool-description block. Fixed business facts and the JSON protocol boundary remain system-level in both arms.
- The compact-instructions variant isolates the effect of the detailed instruction block while retaining the protocol, factual boundaries and enquiry permission rule.
- Local generation forwards all six sampling/output controls to Ollama. max_tokens maps to num_predict; native function schemas are supplied in both prompt-placement arms.
- The alternate model changes only model from the same baseline. Separate batch files preserve initial results and post-fix validation; consult docs/evaluation_report.md for the combined findings.

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

**Current conclusion:** Inspect failures and complete human ratings before stating which configuration worked best.
