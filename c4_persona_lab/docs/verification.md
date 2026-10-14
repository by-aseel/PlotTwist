# C4 verification / Gemini migration

Validated on **14 October 2026**.

| Check | Result | Scope |
|---|---|---|
| Backend and native SDK transport | **29 tests passed** | Routing/tools/history/reflection or ReAct graph, privacy, errors, Gemini settings, IDs and signatures |
| Dependency check | `pip check` passed | Installed pinned dependencies are compatible |
| Notebook | **14 offline cells executed through IPython** | Embedded modules/assets reconstruct and execute; no live quality evidence |
| Generation access | **Failed** | Actual Gemini API generation returned 403; no demo fallback |
| Comparison matrix | **238 deterministic checks** | 17 variants × 7 cases × 2 repeats; all completed, expected tools observed, zero tool errors |
| Live checkpoint | **1 failed attempt of 7 planned** | `experiments/live-access-check/`; stopped on Google access denial |

## Reproduce

```powershell
python -m unittest discover -s tests -v
python app.py --mode demo
```

The five native transport tests use fake SDK responses to validate native function observation matching, preserved signatures, history/system conversion, JSON mode, output controls, truncation and sanitized remote errors. They do not establish service access. Existing tests validate real local tools and persistence, including deduplication and session isolation.

The notebook runs locally through IPython in a separate workspace; this does not claim an interactive Colab session. Business PDFs and the archived offline UI footage were reviewed during earlier preparation. Video source narration predates the Gemini migration; its scope note identifies that limitation.

The public Hugging Face Space is the free Static edition. The updated Python/Gradio deployment bundle is prepared and locally validated, but the full backend hosting bonus is pending hosting access. C3's model reflection bonus is implemented and tested with controlled responses; a successful live recording still needs restored Gemini access.

See [Gemini migration and rerun instructions](gemini_migration.md) for status and exact commands. No empirical persona winner or sampled configuration effect is claimed from scripted output or failed generation calls.

## Completed no-cost comparison

The 14 October 2026 evaluation reran 238 offline cases and all 49 C3/C4 tests. The [evaluation report](evaluation_report.md) compares actual tool behavior and persona replies; 21 reviewed outputs and their assistant assessment notes are saved in `experiments/offline_review/`. The notebook displays both this report and the completed five-question reflection. Model sampling effects remain hypotheses because no successful Gemini generation was available.
