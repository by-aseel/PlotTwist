# C4 verification — real free local generation

Validated on **14 October 2026**.

| Check | Result | Scope |
|---|---|---|
| C4 backend, Gemini and Ollama contracts | **36 tests passed** | Manual graph, consent/privacy, schema checks, persistence, settings/history conversion, native and printed action detection, errors and truncation |
| C3 unchanged backend | **20 tests passed** | Separate assignment; no new successful Gemini-generation claim |
| Dependencies | `pip check` | Pinned environment compatibility |
| C4 notebook | **14 code cells executed through IPython** | Standalone reconstruction and demo execution; actual model datasets/report are embedded separately |
| Actual model comparison | **252 initial attempts** | Qwen2.5 3B/1.5B, seven paired cases, 18 configurations, two seeds |
| Parser correction | **14 actual reruns** | Printed function proposal now reaches the real tool; original evidence retained |
| Assistant quality review | **21 actual replies** | Explicitly labeled subjective, unblinded assistant assessment |
| Local Gradio | `local_gradio_check.json` | Real `/chat` and persona-comparison callbacks; actual outputs retained |
| Historical simulator | **238 deterministic runs** | Separate workflow evidence; not included in LLM quality totals |

## Reproduce

```powershell
python -m unittest discover -s tests -v
python app.py --mode local
```

Install Ollama and download the selected model first; see [local_models.md](local_models.md) for the exact study commands. Local mode supplies native schemas, history, instructions and sampling controls to the model. The application manually detects/executes actions and returns observations. A runtime failure is retained as an error and never replaced with a demo response.

The [evaluation report](evaluation_report.md) distinguishes graph termination from factual correctness and includes hallucinations, rejected calls and the code correction. Raw `raw_output` fields contain the adapter's canonical JSON representation of generated final text or function arguments, with native token/timing metadata. They are not fabricated output or private reasoning.

The real comparison demonstrates operation and experimentation; it does not establish reliable autonomous business advice. The public Hugging Face Space remains the free Static edition. Full Python hosting is account-blocked, and Gemini generation still returns access denial. C3's reflection bonus remains implemented and verified with controlled responses; no successful Gemini recording is claimed. Earlier UI videos document the offline version.

Notebooks, ZIPs and Git contents are checked to exclude real `.env` files, API keys, databases, caches, virtual environments, runtime binaries and model weights. Only fictional customer test inputs are published.
