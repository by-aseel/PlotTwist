# C4 submission map

| Requirement / rubric | Evidence | Readiness |
|---|---|---|
| Use-case write-up: goal, audience, tools, constraints (10) | README, business PDF, notebook opening, tool registry | Included |
| One supported framework | Explicit LangGraph `StateGraph` | Included |
| Manually implemented ReAct logic (30) | Custom model, parse, tool/observation, and finalization logic in `plottwist_agent.py` | Implemented; inspect the graph and a trace |
| No prebuilt executor | Source uses custom nodes/edges | Included |
| At least two personas with tasks, traits, and configuration (20) | Clue, Cipher, Muse in `personas.py` and notebook | Three included |
| Direct vs. reasoning prompt | `reasoning=direct` / `brief_plan` | Implemented as a visible-plan CoT-style proxy; no hidden reasoning |
| Zero-shot vs. few-shot | No solved tasks vs. solved action/observation examples | Included; both retain a protocol-only example |
| System vs. in-message instructions | `instruction_role=system` / `user` | Included; fixed factual boundaries remain system-level |
| LLM configuration experiments and comparison (15) | `experiments.py`, result files, notebook | Runner included; live results require an API key |
| Top-k coverage | Native Gemini top_k; UI slider; 40 vs 20 variant | Implemented; live effect pending access |
| Different model comparison | CLI `--model` / `--compare-model` | Optional compatible models supplied at run time |
| Clear, focused instructions and example (10) | `INSTRUCTIONS`, `COMPACT_INSTRUCTIONS`, `FEW_SHOT_EXAMPLES` | Included |
| Reflection questions and creative presentation (15) | `docs/reflection.md`, notebook, designed app | Included; measured LLM conclusions require live runs |

Validation completed during preparation: 29 backend/transport tests passed, the self-contained notebook's offline code cells executed through IPython, and 238 deterministic comparison runs were saved under `experiments/demo/`. See `verification.md` for scope and limits. The supplementary `docs/demo_walkthrough.mp4` uses actual offline UI screenshots; it is not a continuous live API recording.

## Complete your empirical submission

1. Run the tests and the demo matrix to verify the workflow.
2. Configure your private API key and run the live matrix, preserving the reported mode and model for every run.
3. Read the raw traces and score the human-rating sheet without hiding failed runs.
4. Write a measured conclusion in the reflection using the actual result files. Compare correctness, action success, and helpfulness separately.
5. Record a brief walkthrough of two personas, a multi-tool path, a known unknown, and the comparison report.
6. Review the files and publish/submit using the channel required by the instructor. No account publication is claimed in this package.

The delivered demo evidence validates graph mechanics and exports. It cannot show an LLM's response quality, naturalness, temperature effect, or best model configuration.

## Gemini access status (14 October 2026)

Native Gemini integration is implemented. Generation is blocked by Google project access denial (403); Gemini 2.5 Flash-Lite also rejects new users (404). See [migration and rerun instructions](gemini_migration.md). Saved deterministic comparisons verify mechanics only. Live persona rankings, configuration effects and actual model reflection remain unmeasured.
