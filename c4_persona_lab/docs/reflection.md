# C4 reflection / Design rationale and evidence boundaries

This write-up separates design judgments from empirical findings. The project includes a deterministic demo model and a live OpenAI adapter. **No live-model performance finding is claimed in this document.** Demo responses are scripted and sampling controls do not change their generation. After running the live matrix, add the measured comparisons described below and preserve the original result files.

The saved demonstration covers 16 variants, 7 cases, and 2 repeats: 224 deterministic runs. Its report records completed responses and expected tool observations for all 224 runs, with no tool errors. These are mechanical checks of the scripted graph workflow, not scores for factual accuracy, naturalness, creativity, or real-model task completion. See `../experiments/demo/comparison.md` and its raw traces for the actual evidence.

## 1. Which persona gave the most helpful or natural results?

The intended match is Clue for first-time guest advice, Cipher for logistics, and Muse for original story concepts. Clue uses accessible language and a welcoming follow-up; Cipher foregrounds numbers and missing constraints; Muse adds a narrative hook while labeling invented ideas as concepts. These are deliberate prompt and task differences, not observations of live model quality.

The most helpful persona is likely task-dependent. A birthday host exploring possibilities may value Clue's conversational style; an organizer comparing group capacity may value Cipher's precision. That is a hypothesis to test. For a measured answer, rate each live response for correctness, helpfulness, naturalness, and persona fit, then compare by task instead of collapsing every task into one winner.

## 2. Which prompt and configuration combination performed best?

No empirical winner is established before live evaluation. A reasonable starting configuration is Clue at temperature 0.45 with full instructions in the system role, direct output, and top-p 1.0. Cipher's 0.10 temperature is intended to reduce variation for planning; Muse's 0.85 temperature and presence penalty are intended to diversify story ideas. None guarantees factuality.

The experiment runner compares persona defaults, prompt conditions, and generation settings. Few-shot examples may improve action formatting, while additional instructions and plans can increase latency and output length. To identify a winner, first reject responses that invent facts or claim failed actions succeeded. Among the remaining responses, compare task usefulness, naturalness, tool success, and cost/latency. Report the model, settings, task set, repeats, and failures along with the result.

The lab does not silently simulate top-k: the selected OpenAI API does not offer it. The setting is marked not applicable and rejected. A model-type comparison requires two compatible models and actual calls to both.

## 3. How well did the agent reason and use tools?

The implementation makes the action cycle observable. A custom LangGraph node requests a model response; another path parses one JSON action or final answer; the registry validates and executes the action; the observation returns to the model. An explicit step bound prevents an endless loop. A failed tool result remains a failure observation, so the answer can explain or repair the problem.

A demo path such as catalogue search -> estimate -> final answer demonstrates that observations move through the graph. It cannot prove the quality of a real model's reasoning. Live evaluation should inspect whether the chosen tool was appropriate, whether the next action used the observation, and whether the answer stayed within known facts. A valid JSON response alone is not enough.

The "brief plan" condition is a concise user-facing plan, used as a CoT-style prompt proxy. It does not expose hidden chain-of-thought. Its effect should be evaluated through observable answer and tool quality. The trace displays verifiable actions and observations rather than an invented account of internal thought.

## 4. Did the instructions block change behavior? How?

The full block separates responsibilities: read inputs, follow the persona, use catalogue tools, ground facts, collect missing fields, obtain customer authorization, log unknowns, handle errors, treat observations as data, and follow the response protocol. A minimal protocol example is included inside the instructions. The compact condition reduces detail while retaining essential boundaries.

These instructions create testable expectations. For example, "Please save my enquiry" without a name and email should lead to a clarification; an unavailable venue fact should lead to an honest gap and feedback record. Whether the detailed block improves live adherence is an empirical question. Compare full and compact results on exactly those cases and report both successes and failures.

The zero-shot condition omits solved customer-task demonstrations; it still includes the fixed protocol example used in every condition. Few-shot adds solved action/observation demonstrations. The role experiment moves the persona and experimental instructions between system and user-message positions, while fixed business boundaries stay in a system message. Thus it measures the placement of that block, not removal of all system instructions.

## 5. What were the biggest implementation challenges?

**Action reliability.** The model must return a recognizable action, the arguments must match a real schema, and the observation must be returned before requesting another step. Explicit parsing and validation make those failure points visible.

**A fair comparison.** Changing persona wording and every generation control at once obscures the cause of a difference. Persona-default comparisons show overall behavior; narrower one-control comparisons help interpret individual settings. Repeats are still needed because live outputs vary.

**Factual creativity.** Muse must be free to invent a story premise without inventing a venue, confirmed date, accessibility capability, or price. The source catalogue and instructions distinguish creative proposals from business facts.

**Honest evidence.** A polished demo can look persuasive even when it uses scripted responses. The UI, notebook, and experiment exports retain run mode, and this reflection avoids treating deterministic output as a live LLM finding.

**Useful persistence.** The local tools save enquiries and feedback without pretending to send messages. Records are useful for a classroom demonstration; they do not provide a production booking or customer-service system.

## Add measured findings after the live run

Run the live comparison from the README, then record:

| Evidence to report | Where to find it |
|---|---|
| Model, settings, condition, task, repeat, mode | Experiment row and raw trace |
| Action sequence and successful/failed observations | `raw_traces.json` |
| Automatic comparison measures | `metrics.csv` and `comparison.md` |
| Human usefulness, naturalness, and persona-fit judgments | Completed `human_ratings.csv` |
| Best condition for each task and why | Your synthesis of the preceding evidence |
| Limitations | Small sample, task coverage, model variation, metric blind spots, and untested deployment conditions |

A defensible conclusion may identify different winners for logistics and creative tasks. If the differences are small or inconsistent, report that uncertainty rather than forcing an overall winner.
