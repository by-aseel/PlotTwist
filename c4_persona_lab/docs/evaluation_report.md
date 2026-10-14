# PlotTwist C4: actual local model evaluation

**14 October 2026 — real language-model generation, no paid API.** The initial comparison contains **252 actual attempts**: 238 Qwen2.5 3B runs across 17 configurations and 14 paired Qwen2.5 1.5B runs. A further **14 actual reruns** test a parser correction discovered during the model comparison. Earlier deterministic checks remain separate under `experiments/demo/`; they are not part of these LLM results.

## Scenario, method and reproducibility

PlotTwist is a fictional mystery-adventure studio. Its assistant helps birthday hosts, small groups and corporate planners choose an experience, evaluate group constraints, develop proposed stories, and record authorized enquiries or unknown questions. It can search the catalogue, estimate a group event, save customer interest, and save feedback. It cannot book, send email, verify venues/accessibility/availability, take payment, or promise a final quote.

The same custom LangGraph model → parse → action/observation → model → final graph is used for actual generation. Ollama supplies native function calls and final text; the adapter serializes them for the manual parser and translates prior actions/observations back to native assistant/tool messages. It does not execute tools itself or substitute scripted responses. The business inputs and example contact address are fictional test inputs; the responses and decisions in this study are actual model generations.

Seven fixed cases cover birthday fit, insufficient corporate budget, unknown accessibility/availability, consented enquiry saving, a time-travel story concept, an oversized birthday group and the four team roles. Every configuration uses the same cases and two paired seeds (43, 44); shuffle seed is 42. Each request allows at most six model calls. The primary batch is shuffled; the alternate-model batch runs afterward to avoid repeated model loading on a 6 GB GPU. This batch order and initial loading mean response latency is descriptive, not a controlled hardware speed ranking.

The baseline is Clue, direct response, zero solved task demonstrations, full system instructions, temperature 0.45, top-p 1, top-k 40, frequency penalty 0.15, presence penalty 0, and maximum 700 output tokens. Single-axis variants change one field. Cipher and Muse bundle variants change task, wording and matching configuration together; prompt-only variants retain baseline sampling. The brief-plan condition asks for a short public next-step statement; it does not expose or measure private chain-of-thought. Both zero-shot and few-shot retain the required greeting/serialization worked example; few-shot adds two solved tool-use tasks.

Runtime: Ollama 0.40.4, Q4_K_M quantization, 8192-token context, fixed repeat penalty 1 and min-p 0. Hardware: HP Victus, Intel i5-13420H, 7.6 GB RAM and RTX 3050 laptop GPU with 6 GB VRAM. Exact model digests, API timing/token fields, settings, actual replies and observations are preserved. See [setup and commands](local_models.md), [model manifest](../experiments/local/model_manifest.json), [primary traces](../experiments/local/raw_traces.json), [alternate traces](../experiments/local-alternate/raw_traces.json) and [post-fix traces](../experiments/local-alternate-fix/raw_traces.json).

## Measured workflow results

The initial study returned replies for **251/252** attempts and made **475 model calls**. Strict expected-tool coverage was **116/252**. There were **31 rejected tool attempts**, **9 format/budget events**, and **20 successful local save observations**. Successful save observations can include deduplicated operations; they are not emails or bookings. No cloud fallback was used.

| Configuration | Runs | Reply returned | Strict tools observed | Tool errors | Local saves | Mean words | Mean ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| presence_high | 14 | 14/14 | 7/14 | 1 | 1 | 65.1 | 3998.7 |
| top_p_low | 14 | 14/14 | 6/14 | 0 | 2 | 74.2 | 6288.9 |
| frequency_high | 14 | 14/14 | 7/14 | 2 | 0 | 65.9 | 2881.7 |
| top_k_low | 14 | 14/14 | 6/14 | 2 | 0 | 71.5 | 2502.0 |
| compact_instructions | 14 | 14/14 | 6/14 | 2 | 0 | 68.8 | 2764.5 |
| temperature_low | 14 | 14/14 | 6/14 | 1 | 1 | 64.1 | 2329.7 |
| temperature_high | 14 | 14/14 | 9/14 | 1 | 2 | 76.2 | 3459.1 |
| brief_plan | 14 | 14/14 | 6/14 | 2 | 1 | 57.9 | 2474.8 |
| short_output | 14 | 14/14 | 6/14 | 2 | 1 | 71.2 | 2877.9 |
| long_output | 14 | 14/14 | 6/14 | 2 | 1 | 65.4 | 2525.0 |
| cipher_persona | 14 | 14/14 | 7/14 | 3 | 2 | 82.1 | 3650.5 |
| baseline | 14 | 14/14 | 6/14 | 2 | 0 | 75.8 | 2737.8 |
| muse_prompt_only | 14 | 14/14 | 7/14 | 3 | 0 | 75.9 | 3314.7 |
| muse_persona | 14 | 14/14 | 7/14 | 4 | 0 | 80.1 | 3669.2 |
| cipher_prompt_only | 14 | 14/14 | 7/14 | 2 | 3 | 80.1 | 3366.5 |
| in_message | 14 | 14/14 | 7/14 | 2 | 1 | 64.9 | 2785.6 |
| few_shot | 14 | 14/14 | 8/14 | 0 | 5 | 57.3 | 2833.9 |
| alternate_model | 14 | 13/14 | 2/14 | 0 | 0 | 64.6 | 5102.8 |

**Reply returned does not mean the task was solved correctly.** It records graph termination rather than factual accuracy. Strict tools observed requires every scenario's expected tool name; merely choosing a tool that later fails can satisfy this metric, so tool errors and saves must be read alongside it. Search already returns some capacity/price facts, so missing the requested estimate can coexist with a factually useful reply. Conversely, a normal final reply can contain a serious hallucination. `metrics.csv` and the raw traces expose these distinctions.

## Persona assessment

An explicitly identified **Codex assistant review** assessed 21 original outputs: repetition 1 for all seven cases under Clue, Cipher and Muse bundles. Ratings are subjective, unblinded and made by the implementation assistant; they are not independent human or instructor scores. Full answers, criterion scores and reasons are saved in [assistant_ratings.csv](../experiments/local/assistant_ratings.csv). The separate human-rating templates remain available for an independent review.

| Persona bundle | Reviewed replies | Grounding / 5 | Usefulness / 5 | Naturalness / 5 |
|---|---:|---:|---:|---:|
| Clue | 7 | 3.14 | 2.71 | 3.43 |
| Cipher | 7 | 4.29 | 2.29 | 3.00 |
| Muse | 7 | 2.57 | 1.57 | 2.29 |

Clue was the most useful and natural of these three bundles in this small review. Its team reply used clear role paraphrases, and its story reply proposed travellers from different eras solving a threat to history. Cipher gave useful numeric package checklists but often repeated questions, added irrelevant catalogue material, or omitted an explicit budget verdict. Muse's higher temperature and penalties did not reliably create an original story: its tested story response listed ordinary packages and asked for more input.

These averages are low in absolute terms. The Clue corporate response incorrectly said USD 650 fit a USD 500 budget. Clue and Muse invented wheelchair access; Muse also implied next-Friday availability. Some enquiry calls supplied an empty name despite the explicit Aseel input; validation rejected those writes. Muse described a USD 30 starting-price share as a required nightly contribution. Those are substantive failures, preserved rather than omitted from the comparison.

## Prompt and configuration findings

- **Few-shot vs zero task demonstrations:** tool errors fell from baseline 2 to 0, strict tool coverage rose from 6/14 to 8/14, and both enquiry cases saved the actual supplied name/email. Both access cases logged the unknown question. Across the whole arm there were five successful save observations. This was the most useful tested prompt change for those operational tasks, but its first corporate reply still said USD 650 fit USD 500 and its first birthday reply misstated City Quest duration. It is not an overall factual-quality winner.
- **Direct vs brief-plan:** strict coverage stayed 6/14 in both arms. Only one plan field was emitted across the primary study; it contained draft-like prose rather than the requested concise next-step sentence. There is no evidence here that the brief-plan instruction consistently produced a visible plan or improved reasoning. The study compares the instruction conditions, not hidden thought processes.
- **System vs in-message:** strict coverage changed from 6/14 to 7/14, with two format events in the in-message arm and none at baseline. Inspected in-message access answers admitted uncertainty but did not log the question. This is mixed evidence, not proof that one placement always wins. Native function schemas and fixed business boundaries remain available in both arms.
- **Full vs compact instructions:** both reached 6/14 strict coverage and two tool errors. Compact used fewer input tokens, but equal workflow totals do not show equal grounding. Detailed instructions alone did not prevent the reviewed hallucinations.
- **Temperature:** low temperature remained 6/14 strict coverage; high temperature reached 9/14, the highest primary arm. However, a high-temperature corporate reply invented tax/fee inclusion and an hourly per-person interpretation. More correct tool names did not establish better customer answers.
- **Top-p/top-k and penalties:** lower top-p/top-k did not improve strict coverage beyond baseline; raised frequency/presence penalties reached 7/14. These descriptive differences span only 14 cases per arm. No general optimal setting or statistical significance is established.
- **Token limit:** the 180-token arm had one truncated call followed by parser recovery; all 14 ultimately returned replies. Raising the limit to 1200 did not improve strict coverage or save correctness beyond baseline. This is a useful recovery example, not evidence that long outputs are better.
- **Model size:** Qwen2.5 1.5B initially executed one search and zero writes, returned 13/14 replies and exhausted the call budget on one story case. Only the two tool-free team cases met strict tool expectations. It invented a false fit for 90 birthday guests and printed a save proposal as text. The 3B baseline selected real tools but still had grounding and save-argument failures. The 3B route is the more viable tested implementation; neither model demonstrated reliable autonomous business advice.

## A defect found and corrected by real experiments

The original local parser bridge handled native `tool_calls`. The 1.5B model sometimes wrote a JSON function proposal inside ordinary content. Treating that as final text could show a save claim without executing it. The adapter now detects structured name/arguments proposals and returns an action to the existing manual dispatcher. Consent, exact customer details, allowlisting and SQLite validation still apply. Multiple proposals are rejected for recovery rather than silently dropping actions.

The separate post-fix batch used the same 14 alternate-model cases and settings. It returned **13/14** replies, observed the strict tool expectations in **3/14**, and produced **1 successful local save observations**. The first enquiry now reached `record_customer_interest`; that enquiry executed no tool in the original batch. This verifies a parser improvement, not a factual-quality improvement. The second enquiry and other weak answers remain in the traces. Initial comparison files are unchanged, and post-fix results are explicitly separated; a rerun of current code may therefore differ from the initial dataset.

## Practical choice and remaining limits

For a **supervised demonstration of enquiry saving and unknown-question logging**, the strongest tested starting point is Clue + few-shot + full system instructions on Qwen2.5 3B, with the baseline sampling settings. That recommendation is limited to the observed operational tasks. No tested configuration is recommended for unsupervised final pricing, accessibility or booking advice. Arithmetic checks in observations, stronger final-answer grounding checks, broader cases and independent review are reasonable next experiments; they are not claimed as completed features.

The exercise establishes actual persona/configuration experiments, real tool execution, bounded recovery and measured reflection without a paid generation service. It does not establish general model superiority, statistically significant effects or full assignment marks. Google generation remains denied, and the public free Hugging Face Space remains a browser-only Static preview rather than a hosted Python/LLM backend. Earlier deterministic comparisons and videos retain their original evidence labels.
