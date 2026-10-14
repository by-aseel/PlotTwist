# PlotTwist C4 evaluation report

**Evaluation date: 14 October 2026.** The implementation completed **238 of 238 benchmark runs**, observed the expected tool sets in every run, and reported **zero tool failures**. Across the reviewed replies, Clue was the strongest general concierge design, Cipher was more useful for planning constraints, and Muse supplied the most complete story concept. These selections describe the implemented demonstration and the assistant's qualitative review.

## Method

The evaluation used the project's **offline deterministic model**, seven fictional customer scenarios, 17 configurations and two repeats. The real LangGraph graph, parsing, tool validation, observations and SQLite writes executed locally. Gemini did not generate these replies: its separate access attempts failed with 403. The benchmark therefore measures workflow behavior and demonstrates persona styles; it cannot establish a language model's sampling effects. The 21 distinct outputs reviewed here cover seven cases under three persona bundles. Review notes are assistant assessments, not an independent human study.

Jobs used shuffle seed 42 and an isolated database. Each trial began with a fresh session. The raw traces preserve the prompt, settings, model mode, actions, observations, final reply and local records. Two repeats check repeatability of the deterministic implementation; they are not two independent samples of model creativity.

## Results

| Measure | Observed result | Interpretation |
|---|---:|---|
| Completed runs | 238/238 | All benchmark requests reached a bounded final reply |
| Expected tool sets observed | 238/238 | Required actions appeared in each scenario's trace |
| Tool errors | 0 | Selected valid benchmark actions executed successfully |
| Format/runtime errors | 0 | The scripted protocol completed without recovery errors in this matrix |
| Tool executions | 306 | Actual local catalogue, estimate, enquiry and feedback calls |
| Visible brief-plan events | 18 | Short next-action explanations appeared in the brief-plan condition |
| C4 behavior/transport tests | 29 passed | Includes malformed actions, false contacts, cancellation, isolation and API-error recovery |
| Companion C3 tests | 20 passed | Includes routing, tools, memory, reflection and native SDK contracts |

The tool totals were 136 catalogue searches, 102 estimates, 34 enquiry saves and 34 feedback records. Mechanical completion is narrower than customer satisfaction: an answer can finish successfully while still missing a useful detail.

### Persona comparison

| Persona | Runs in its bundle | Mean reply words | Strongest observed use | Main limitation |
|---|---:|---:|---|---|
| Clue | 14 | 38.7 | Friendly first contact and a clear next question | Repeated branding; custom-story request gets logistics rather than a premise |
| Cipher | 14 | 34.7 | Budget, capacity and missing planning inputs | Less suited to a request whose main goal is a story concept |
| Muse | 14 | 48.9 | A labeled imaginative concept with a practical follow-up | Story-title prefix also appears on administrative and accessibility replies |

For eight birthday guests, all three replies used the same tool estimate: USD 240 per group and 120 minutes. Clue finished with a date/atmosphere question. Cipher added venue, access and budget checks and kept availability unverified. Muse added a missing-alibi concept. The meaningful difference was task emphasis and presentation, rather than a different price or capacity result.

For 24 colleagues and a USD 500 budget, each reply recognized the USD 650 corporate starting price exceeded the budget. Cipher's operational follow-up was the most relevant to that decision. Muse's added story hook was less useful at this stage. No persona invented a discount.

For a custom time-travel adventure with 14 guests, Muse supplied **The Tomorrow Heist**, with contradictory witness accounts, timeline reconstruction and a collaborative finale. It described this as a proposed concept and kept capacity, duration and price subject to team confirmation. Clue and Cipher collected scoping inputs without giving an equally complete premise. This supports choosing Muse for the implemented creative demonstration, rather than using it for every request.

### Prompt and configuration comparisons

| Comparison | Observed result | Conclusion supported by this run |
|---|---|---|
| Direct / brief plan | Final replies matched baseline on all seven unique cases; brief plans added 18 trace events across two repeats | Brief plan improves demonstration visibility; customer-answer improvement was not shown |
| Zero task examples / few-shot | Final replies and expected tool paths matched | Worked examples document the desired protocol; their effect on Gemini remains unmeasured |
| System / in-message instructions | Both placements completed all cases | Both message layouts are wired; the deterministic policy cannot establish a stronger prompt role |
| Full / compact instructions | Both completed all cases with the same final replies | Instruction content differs, but a causal behavioral effect was not shown |
| Temperature, top-p, top-k, penalties and output cap | Controls were validated and native forwarding was tested; final replies matched baseline | Parameter wiring is verified; output variation, cost and model quality effects are not measured offline |
| Persona bundle / prompt-only persona | Corresponding persona replies matched | In the simulator, style follows the persona policy; sampling settings do not explain the differences |
| Model type | No successful live generation available | No model ranking is supported |

Zero-shot retains the common greeting/protocol example required by the instructions assignment; few-shot adds two solved customer tasks. The placement experiment moves the persona/instructions block, while factual business boundaries remain system-level. Brief plans describe an observable next action and do not expose private chain-of-thought.

## Tool use and instruction checks

Birthday, corporate and custom-story requests followed **search -> estimate -> final**. Accessibility/availability questions called `record_feedback` and acknowledged the information gap. The enquiry case stored the exact provided name and email and explicitly said that no email or booking was made. The oversized birthday case searched the catalogue, avoided a false standard-package fit and suggested custom scoping.

Separate controlled-response tests verified recovery from malformed JSON, unknown tools and invalid arguments; refusal to save fabricated contact details; explicit cancellation; session isolation; deduplication; bounded loops; and safe live-error handling. These tests validate the application's enforcement layer and recovery contracts. They do not establish how often an unconstrained LLM would attempt an invalid action.

A noteworthy quality gap survived the mechanical checks: the oversized-group final reply did not explicitly state the published birthday capacity of 6-20. Muse's repeated story title also weakened naturalness on routine enquiries and unknown questions. These observations explain why passing tool metrics alone is insufficient for choosing a persona.

## Configuration rationale and expected live behavior

The course-demo profile uses Clue, full system instructions, worked task examples and brief-plan visibility. Clue's temperature 0.45 is intended to support friendly variation; Cipher's 0.10 favors consistent planning language; Muse's 0.85 and higher presence penalty are intended to broaden story ideas. Their output caps are 700, 850 and 1000 respectively, with top-p 1 and top-k 40 held steady in the persona defaults.

These are **design hypotheses**, not measured Gemini effects. On a compatible sampling model, lower temperature may narrow variation and examples may make the action format easier to follow; a shorter cap may truncate an answer. Google discourages changing sampling defaults for Gemini 3 and newer families, so the coursework sampling experiment must disclose model-specific support and any parameters the API ignores or rejects. [Official generation guidance](https://ai.google.dev/gemini-api/docs/troubleshooting).

## Decision and next improvements

Use **Clue for general discovery**, **Cipher for feasibility decisions**, and **Muse when the guest requests a story concept**. Keep package facts and tool validation shared across personas. For the classroom demonstration, brief-plan traces make the action/observation cycle easiest to inspect. The run does not establish a best live generation configuration.

The next improvements are to make persona openings depend on the request, state exact capacity in no-fit replies, and keep budget follow-ups focused on feasibility. A future live evaluation should preserve this benchmark, add independent qualitative ratings, and compare actual successful generated replies with the same settings and cases.

## Reproduction and evidence

```powershell
python -m unittest discover -s tests -v
python experiments.py --mode demo --repeats 2 --output experiments/demo
```

- [Raw traces](../experiments/demo/raw_traces.json) and [mechanical comparison](../experiments/demo/comparison.md)
- [Metrics](../experiments/demo/metrics.csv)
- [21 reviewed outputs and qualitative notes](../experiments/offline_review/reviewed_outputs.csv)
- [Machine-readable evaluation summary](../experiments/offline_review/summary.json)
- [Five reflection answers](reflection.md)
