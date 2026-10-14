# C4 submission map

| Requirement / rubric | Included evidence | Scope |
|---|---|---|
| Use-case goal, audience, tools and limitations (10) | README, business PDF, notebook opening | Fictional mystery-adventure studio; no booking, payment or live availability |
| One specified agent framework | `plottwist_agent.py` | LangGraph StateGraph with custom nodes and conditional edges |
| Own ReAct logic (30) | Source, notebook and `local_trace_example.json` | Model action detection, validation, tool execution, observations, bounded recovery and final parsing; no prebuilt executor |
| Multiple persona tasks, traits and configuration (20) | `personas.py`, actual traces and assistant review | Clue, Cipher and Muse; bundles and prompt-only rows compared |
| Direct vs reasoning-style prompt | Direct / brief-plan variants | Requests a short public plan; observed noncompliance is reported; no private thought exposure |
| Zero-shot vs few-shot | Two solved task examples vs none | Both keep the required greeting/serialization example |
| System vs in-message instructions | Same block moved between roles | Fixed facts and native tool schemas remain available in both conditions |
| LLM configuration experiments (15) | `experiments.py`, three actual local datasets and report | 252 initial attempts, 14 post-fix reruns; paired cases/seeds, settings, token and timing metadata |
| Temperature, top-p, top-k, penalties, token limit, model type | Single-axis variants plus 3B/1.5B comparison | Actual generations; no optimal-setting claim beyond observed tasks |
| Focused instructions, I/O format and worked example (10) | Dedicated full/compact blocks and notebook | Persona, instructions and transport serialization are described separately |
| Creativity and five reflection questions (15) | Designed app, business concept, `reflection.md` and notebook | Measured findings, unexpected outcomes, failures and implementation challenges |

Read [evaluation_report.md](evaluation_report.md) and [verification.md](verification.md). The notebook includes the report, all five answers and saved actual evidence. The numerical quality ratings are an explicitly identified assistant review of 21 outputs, not independent human or instructor scores. The human-review templates are available for an additional independent assessment.

Gemini cloud generation remains blocked by project access denial. C4's actual LLM evidence now comes from free local models; LangGraph remains the selected framework. The 238 deterministic checks remain historical workflow evidence. The free Hugging Face Static preview runs the browser edition; it does not host the Python/LLM backend. Earlier videos retain their offline evidence labels.
