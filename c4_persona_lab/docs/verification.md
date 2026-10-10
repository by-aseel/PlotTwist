# C4 verification record

Validation date: **10 October 2026**. These results concern the manual graph implementation, deterministic experiment harness, notebook execution, and supplied business document. They are not live LLM performance results.

## Completed checks

| Check | Observed result | What it establishes |
|---|---|---|
| Backend suite | **23 tests passed** | Tested graph, protocol, tool, persistence, persona, configuration, and error paths behave as asserted |
| Notebook | **14 offline code cells executed through IPython** in an isolated workspace | Embedded files reconstruct and the full readable implementation runs in the local validation environment |
| Demo matrix | **224 attempts: 16 variants x 7 cases x 2 repeats** | The runner emits comparison files and exercises the deterministic workflow under all recorded conditions |
| Demo observations | **224 expected-tool checks and bounded completions passed; zero tool errors** | The scripted cases followed the expected mechanical paths |
| PDF | Four pages rendered to PNG and visually inspected | Readable layout, complete business facts, and Aseel/Noah/Jiso/Felix were checked |
| Submission mapping | Checklist compared with supplied C4 requirements | Framework, manual loop, personas, instructions, experiments, and reflection have documented evidence locations |

The suite exercises action/observation/final transitions, an observation-dependent second action, malformed JSON recovery, unknown tools, invalid arguments, rejection of ambiguous action-plus-final responses, and the model-call bound. It also covers multi-turn enquiries, session-scoped/idempotent records, cancellation of saving, invalid or fabricated contact details, group limits, quote-only services, and a labeled Muse story concept.

Configuration checks verify persona defaults, explicit overrides, prompt conditions, experiment axes, and forwarding generation controls to a fake API client. A passing parameter-forwarding test does not prove that every external model supports those parameters. Missing credentials and live request failures remain explicit errors rather than silently changing to demo mode.

The notebook was executed through IPython, including the editable `%%writefile` source cells, in its dedicated `c4_persona_lab_notebook/` workspace. This is local code-execution evidence, not a completed interactive Colab session. It does not exercise the real OpenAI service.

## Reproduce the checks

From the project folder, after installing requirements:

```powershell
python -m unittest discover -s tests -v
python experiments.py --mode demo --repeats 2 --output experiments/demo
```

The experiment output includes `metrics.csv`, `raw_traces.json`, `comparison.md`, and `human_ratings.csv`. Inspect the raw tool observations before relying on an aggregate metric. "Completed" records a workflow ending, not a human judgment that the user's task was solved well.

## Evidence still needed for empirical conclusions

No real OpenAI calls were made during this preparation. Demo wording is scripted, and changing sampling controls cannot establish a temperature, top-p, or penalty effect on that simulator. Therefore no best LLM persona, prompt setup, or model is claimed. The human-rating sheet is provided for actual assessment, not filled with invented judgments.

Add a local API key, run the live matrix into a separate `experiments/live/` directory, complete the ratings, and update the reflection using measured evidence. If comparing model types, pass two compatible models available to your account. Keep failed runs visible in the analysis.

The brief-plan option is a user-visible rationale and a CoT-style prompt proxy, not access to hidden reasoning. Zero-shot omits solved task examples but retains the common protocol-only example. The role comparison keeps fixed factual boundaries system-level in both conditions. These design limits should accompany any final conclusions.

No GitHub repository or hosted Space was published. The supplied video is a supplementary captioned screenshot walkthrough of offline UI states, not continuous footage of a live model session.
