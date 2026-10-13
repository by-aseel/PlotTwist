# C3 verification / Gemini migration

Validated on **14 October 2026**.

| Check | Result | Scope |
|---|---|---|
| Backend and native SDK transport | **20 tests passed** | Routing/tools/history/reflection or ReAct graph, privacy, errors, Gemini settings, IDs and signatures |
| Dependency check | `pip check` passed | Installed pinned dependencies are compatible |
| Notebook | **10 offline cells executed through IPython** | Embedded modules/assets reconstruct and execute; no live quality evidence |
| Generation access | **Failed** | Actual Gemini API generation returned 403; no demo fallback |
| Live attempt log | `docs/live_access_attempt.json` | Actual request, safe error code and skipped reflection after failure |

## Reproduce

```powershell
python -m unittest discover -s tests -v
python app.py --mode demo
```

The five native transport tests use fake SDK responses to validate native function observation matching, preserved signatures, history/system conversion, JSON mode, output controls, truncation and sanitized remote errors. They do not establish service access. Existing tests validate real local tools and persistence, including deduplication and session isolation.

The notebook runs locally through IPython in a separate workspace; this does not claim an interactive Colab session. Business PDFs and the archived offline UI footage were reviewed during earlier preparation. Video source narration predates the Gemini migration; its scope note identifies that limitation.

The public Hugging Face Space is the free Static edition. The updated Python/Gradio deployment bundle is prepared and locally validated, but the full backend hosting bonus is pending hosting access. C3's model reflection bonus is implemented and tested with controlled responses; a successful live recording still needs restored Gemini access.

See [Gemini migration and rerun instructions](gemini_migration.md) for status and exact commands. No empirical persona winner or sampled configuration effect is claimed from scripted output or failed generation calls.
