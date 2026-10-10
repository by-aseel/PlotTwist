# C3 verification record

Validation date: **10 October 2026**. This record covers the delivered source, offline behavior, notebook execution, and business document. It does not claim a successful live API call or a hosted deployment.

## Completed checks

| Check | Observed result | What it establishes |
|---|---|---|
| Backend suite | **15 tests passed** | The tested routing, tool, storage, memory, error, and reflection paths behave as asserted |
| Notebook | **10 offline code cells executed through IPython** in an isolated workspace | Embedded support files reconstruct and the code executes in order in the local validation environment |
| Business knowledge | Summary and PDF loading exercised by the backend suite | Both requested source formats can be read |
| PDF | Four pages rendered to PNG and visually inspected | Page layout, readable text, footer spacing, and the requested team names were checked |
| Submission files | Assignment checklist compared with supplied C3 requirements | Required local artifacts are mapped to their implementations; account-dependent steps remain identified |

The tests cover all three routes, multi-turn lead collection, session separation, durable/deduplicated storage, cancellation, scoped export, unknown-question logging, malformed tool arguments, storage errors, and bounded tool loops. Fake API responses exercise history forwarding, action/observation round-trips, live-error handling, and reflection draft/revision logging without making network requests.

The notebook check uses IPython to execute the code cells, including the readable `%%writefile` implementation. It is not evidence of a completed interactive Google Colab session or a real model run. The notebook remains self-contained and reconstructs assets in its own `c3_business_assistant_notebook/` directory.

## Reproduce the backend check

From the project folder, using the environment in which requirements are installed:

```powershell
python -m unittest discover -s tests -v
```

For a notebook review, open `business_agent.ipynb` in Jupyter or upload that file to Colab. Leave `RUN_LIVE = False` for offline execution, run cells in order, and inspect the returned route/tool/reflection evidence. A local notebook editor may require installing the development dependencies from `requirements-dev.txt`.

## Not verified by these checks

- No real OpenAI request was run with a user's API key. Tests named "live" use fake client responses where applicable.
- No empirical claim is made about the model's factual accuracy, naturalness, or reliability across arbitrary user inputs.
- No public GitHub repository or Hugging Face Space was created or verified.
- The supplementary walkthrough is a captioned presentation of offline UI screenshots, not continuous live model footage.

To complete the live evidence, supply a key locally, launch with `--mode live`, exercise the three routes, inspect actual tool observations and reflection, and record the successful run. Do not infer live readiness from the demo mode label or from a passing mocked-client test alone.
