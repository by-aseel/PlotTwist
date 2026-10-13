---
title: PlotTwist C3 Business Assistant
emoji: 🗝️
colorFrom: green
colorTo: gray
sdk: gradio
sdk_version: 5.50.0
python_version: "3.12"
app_file: app.py
pinned: false
---

# PlotTwist / C3 Business Assistant

**Your people. Your story. One unexpected turn.**

Clue is the virtual adventure consultant for PlotTwist Experiences, a fictional studio that turns birthdays, outings, and team events into shared mysteries. This standalone C3 submission combines a custom Gradio interface, a three-way message router, OpenAI tool calling, local lead and feedback records, and a reflection step.

The business team is **Aseel** (Story Director), **Noah** (Puzzle Architect), **Jiso** (Experience Producer), and **Felix** (Guest Experience Lead). These are fictional business roles, not an attribution of coursework authorship.

## Start in five minutes

Use Python 3.11 or 3.12. Open a terminal **inside this folder**.

On Windows, you can also double-click `launch_demo.bat`. It creates a local virtual environment, installs the requirements, and launches the offline app.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py --mode demo
```

On macOS or Linux, activate with `source .venv/bin/activate` instead. If PowerShell activation is restricted, call `.\.venv\Scripts\python.exe` directly for the install and launch commands. Open the local address printed by Gradio, normally `http://127.0.0.1:7860`.

**Demo mode needs no API key.** It runs deterministic responses through the project workflow so the interface, routing, persistence, and observable tool steps can be demonstrated. It does not measure LLM quality or satisfy the live model demonstration by itself.

## Connect the live model

```powershell
Copy-Item .env.example .env
```

Edit your local `.env` to set `OPENAI_API_KEY` and `OPENAI_MODEL`, then run:

```powershell
python app.py --mode live
```

Use the model name in `.env.example` as the initial choice. `--mode auto` uses the configured API key when available and otherwise chooses demo mode. A missing key or an API error is a setup/runtime issue; do not present a demo reply as a successful live model response. Keep `.env` out of Git and recordings. This project supplies an example file, never a real secret.

## What is included

| File | Purpose |
|---|---|
| `business_agent.ipynb` | Guided, runnable main notebook: sources, persona, instructions, router, tools, conversation, and Gradio launch |
| `plottwist_agent.py` | Agent logic and the public `build_agent()` interface |
| `app.py` | Designed Gradio application |
| `me/about_business.pdf` | Four-page business dossier |
| `me/business_summary.txt` | Canonical text knowledge source |
| `me/summary.txt` | Identical alias for the alternate filename used in the task text |
| `requirements.txt` / `.env.example` | Dependencies and local configuration template |
| `docs/assignment_checklist.md` | Requirement-to-evidence map and submission steps |
| `docs/verification.md` | What was tested, how to reproduce it, and what still requires a live API run |
| `docs/demo_script.md` | Short, repeatable presentation script |
| `docs/demo_walkthrough.mp4` | Supplementary captioned walkthrough made from actual offline UI screenshots |
| `tests/` | Behavioral checks included with the implementation |

## How Clue works

1. Load the supplied PDF and summary as business knowledge.
2. Keep **persona** (voice and identity) separate from **instructions** (behavior and boundaries).
3. Classify the message as a general question, lead collection, or feedback/unanswered question.
4. Pass the user's message, recent conversation, and tool schemas to the live model.
5. Validate and execute requested tools, return their observations to the model, and complete the answer.
6. Check the draft against the instructions and expose the draft/revision evidence in the trace.

The router is deliberately small and inspectable. The implementation uses the current OpenAI Python client style, `client.chat.completions.create(...)`, for the Chat Completions interaction described in the assignment.

### Tools

The source code contains the exact machine-readable JSON schemas. These are ordinary local tool functions described with schema fields, not an MCP server.

| Tool | Required input | Result and side effect |
|---|---|---|
| `record_customer_interest` | `email: string`, `name: string`, `message: string` | Validates the enquiry, writes a local SQLite lead record, and returns a success/error observation |
| `record_feedback` | `question: string` | Writes feedback or an unanswered question to SQLite and returns a success/error observation |

See [tool schemas and expected outputs](docs/tool_schemas.md) for each tool's exact inputs, success/error fields, example JSON, and logging evidence. Every successful save also prints a `[tool log]` line in the terminal or notebook output.

A saved record **does not send email or reserve an event**. Demonstrate persistence with synthetic data, such as `sam@example.com`. The app has no payment system, booking calendar, or real customer support inbox. The notebook and trace show what the tools actually returned.

### Business facts

| Experience | Group | Duration | Fictional starting price |
|---|---:|---:|---:|
| Birthday Mystery Nights | 6-20 | 2 hours | USD 240 / group |
| City Quests | 2-12 | 90 minutes | USD 90 / group |
| Corporate Missions | 10-60 | 2.5 hours | USD 650 / group |
| Custom Story Adventures | Bespoke | Agreed with the team | Quote-only |

Prices are starting prices. There is no fixed venue, verified service location, live availability, or published cancellation policy. Access requirements and languages need human review. Clue should record unknowns instead of inventing an answer.

## Try the notebook

Install Jupyter if it is not already available, open `business_agent.ipynb`, and run from the top. The notebook is self-contained: it reconstructs its supporting files in a separate `c3_business_assistant_notebook/` directory, and the complete editable agent modules appear in readable `%%writefile` cells. It defaults to demo mode. Its live cell is opt-in and asks for a key through a hidden prompt if one is not configured.

For Colab, upload **only `business_agent.ipynb`** and run from the top; the business PDF, summary, interface assets, and required support files are embedded. Launch Gradio with `share=True` only when you intentionally want a temporary public link; use synthetic data in that session.

## Verify and present

```powershell
python -m unittest discover -s tests -v
```

The 15 included backend tests passed during package validation; the notebook's offline code cells were also executed through IPython. Those checks use offline or fake API responses and do not establish a successful connection to a real OpenAI account. See `docs/verification.md` for the validation scope and limits.

See `docs/demo_script.md` for a five-minute presentation plan and `docs/demo_walkthrough.mp4` for a supplementary captioned video made from actual offline UI screenshots. The video is not a continuous live API screen recording. Final coursework still needs your live API run and a recording that meets your instructor's expectations. Both project folders are published in this repository. No Hugging Face deployment has been made.

## Optional Hugging Face Spaces deployment

Create a Gradio Space and upload the project contents with `app.py` and `requirements.txt` at the repository root. The metadata at the top of this README supplies the SDK settings. Add `OPENAI_API_KEY` as a Space secret and the desired `OPENAI_MODEL` as configuration. Set `PLOTTWIST_MODE=live`, `GRADIO_SERVER_NAME=0.0.0.0`, and `PORT=7860`. Standard hosted disk may be ephemeral, so local SQLite is a teaching store, not a durable production CRM. Do not upload `.env`, local databases, or real customer traces. Publication is optional and is a separate account action.

## Troubleshooting

- **Port already in use:** run `python app.py --mode demo --port 7862`.
- **Missing module:** reinstall the requirements using the same Python interpreter that launches the app.
- **Key not found:** check that `.env` is beside `app.py`, then restart the app.
- **Model or parameter rejected:** choose a model that supports Chat Completions and the sampling parameters used in the source.
- **PDF not found in the notebook:** rerun the first setup cell to reconstruct the embedded support files in the notebook workspace.
- **Unexpected old demo records:** use a fresh synthetic identity/session and inspect the storage path in the backend before removing any files.

## Course alignment and authorship

Prepared for the supplied EECE 503P/798S C3 assignment. The supplied C3/C4 lecture decks informed the separation of persona, instructions, memory, tools, routing, and reflection. The business facts, design, and example enquiries are fictional. Review and understand the code, run the live demonstration, and follow your course's attribution rules before submission.

## Implementation references

- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling) describes the schema/request/execution/observation cycle used by the live backend.
- [Gradio ChatInterface](https://www.gradio.app/docs/gradio/chatinterface) documents the chat component used inside the custom interface. This project pins Gradio 5.50.0; newer online documentation may describe later releases.
