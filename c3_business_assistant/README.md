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

**Make a memory. Leave a mystery.** Clue helps hosts, friends and workplace teams explore a fictional mystery-experience studio. C3 now works with a **free actual local Qwen model**, short-term memory, three-way routing, two validated tools, a Gradio ChatInterface and model reflection. The native Gemini option remains available; this account's Google generation access is denied.

The fictional team is **Aseel** — Story Director, **Noah** — Puzzle Architect, **Jiso** — Experience Producer, and **Felix** — Guest Experience Lead. These roles do not attribute coursework authorship.

**[Current English local-model demo](docs/local_functionality_demo.mp4)** · [Measured report](docs/local_evaluation_report.md) · [Submission map](docs/assignment_checklist.md) · [Video scope/transcript](docs/local_video_scope.md)

## Free real-model setup

Install [Ollama](https://ollama.com/download) from its official site, then download the model once:

```powershell
ollama pull qwen2.5:3b
```

Use Python 3.11 or 3.12. In this C3 folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py --mode local
```

Alternatively, double-click `launch_local.bat` after setting up Ollama. Open the printed Gradio URL (normally `http://127.0.0.1:7860`). Keep Ollama and the Python app running. No API key or paid account is needed. The model download is approximately 1.9 GB; speed depends on memory and hardware. The recorded run used an RTX 3050 laptop.

Optional local `.env` settings (copy `.env.example`):

```text
PLOTTWIST_MODE=local
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_SEED=43
```

Local mode connects only to loopback. It fails visibly if unavailable and never substitutes a scripted reply. Explicit `--mode demo` or `launch_demo.bat` provides a labeled deterministic rehearsal. `--mode live` uses the private Gemini key; `--mode auto` chooses Gemini if a key exists, otherwise demo. The CLI flag overrides the environment default.

## Try the complete flow

Keep reflection checked. Use these fictional test messages:

1. `What does Birthday Mystery Nights include, how long does it last, and what is its starting price?`
2. `Please save an enquiry for a birthday mystery for 10 guests.`
3. `My name is Aseel.`
4. `My email is aseel@example.com.`
5. `Do you have confirmed wheelchair access at a venue next Friday?`
6. `The puzzles were too difficult. Please record my feedback.`

Inspect **Latest activity** for route, actual model requests, tool arguments/observations and reflection. Open **The casebook → Refresh this casebook** to inspect this browser session's records or export JSON. Refreshing starts a new session; earlier records remain locally stored. The **Reflection lab** separately reviews a deliberately flawed test draft, visibly demonstrating correction without saving anything.

## Implementation

| File | Purpose |
|---|---|
| `business_agent.ipynb` | Self-contained notebook with readable implementation, labeled persona/instructions and saved actual evidence |
| `prompts.py` | Separate PERSONA, INSTRUCTIONS, exact tool schemas and reflection instructions |
| `plottwist_agent.py` | Router, memory, six-round manual model/action/observation loop, validated dispatch, SQLite and reflection |
| `local_client.py` | Native Ollama transport, history/tool conversion, structured action proposals, parsing and generation telemetry |
| `gemini_client.py` | Native Google Gen AI transport retained for the model family named in the assignment |
| `interface.py`, `app.py`, `assets/style.css` | Designed Gradio ChatInterface, activity, casebook, reflection lab and launch |
| `me/about_business.pdf`, `me/business_summary.txt`, `me/summary.txt` | Business dossier and canonical knowledge; summary alias is identical |
| `docs/local_validation.json` | Seven actual final model turns, tools, records and reflection |
| `docs/local_reflection_challenge.json` | Actual correction of a labeled deliberately flawed test draft |
| `tests/` | 27 controlled behavioral and transport checks |

The system prompt combines separately labeled persona/instructions with both knowledge sources. Before the model acts, a heuristic router selects **general_question**, **lead_collection**, or **feedback_unanswered**. Recent history and validated lead state carry missing fields across turns.

The model receives route-appropriate tools. Incomplete leads cannot write; complete leads and unknown/feedback messages require the corresponding action. Ollama lacks a native forced-tool switch, so required actions can be generated as schema-constrained JSON proposals. The parser detects native or printed structured actions; the application validates and executes them, returns actual observations, and asks the model to finish. The adapter's `chat.completions` attribute is an internal compatibility interface, not an OpenAI request. Success disables further writes for that turn; failures and loop limits stay visible.

A second model call reviews the draft against instructions, knowledge and observations. The trace logs original draft, revised reply, `changed`, checks and native generation metadata. An unchanged reply is a review, not a correction. Small models can still miss errors or give inaccurate check summaries; inspect the [measured limitations](docs/local_evaluation_report.md).

## Required tools

| Name | Required parameters | Output and side effect |
|---|---|---|
| `record_customer_interest` | `email:string`, `name:string`, `message:string` | Validates customer contacts, saves a SQLite lead, returns success/reference or error |
| `record_feedback` | `question:string` | Saves feedback or an unknown question, returns success/reference or error |

[MCP-style documentation](docs/tool_schemas.md) includes descriptions, parameter/output fields and examples. These are local functions described with schemas, not an MCP server. Successful saves print `[tool log]`. Customer provenance, exact argument keys, deduplication and session scoping are enforced by code.

Local records **do not send email, contact a company, confirm access or book an event**. No payment, live venue or calendar exists. Use fictional contacts for demos and omit databases from submission.

## Business knowledge

| Experience | Group | Duration | Fictional indicative starting price |
|---|---:|---:|---:|
| Birthday Mystery Nights | 6–20 | 2 hours | USD 240 / group |
| City Quests | 2–12 | 90 minutes | USD 90 / group |
| Corporate Missions | 10–60 | 2.5 hours | USD 650 / group |
| Custom Story Adventures | Bespoke | Agreed with team | Quote-only |

Specific inclusions, final quotes, availability, venues, cancellation policies, languages and accessibility arrangements need human review. The bot should state uncertainty and log unknown questions.

## Notebook and checks

Run `business_agent.ipynb` top to bottom. It reconstructs support files in its own directory and writes readable editable source modules. **10 code cells are executed with saved outputs.** The default conversation is a portable deterministic rehearsal; a separate evidence section displays the actual local report, tool observations and reflection correction.

Set `RUN_LOCAL=True` after starting Ollama for fresh real generations. Leave `RUN_LIVE=False`; both flags cannot be true. Ordinary Colab cannot reach a laptop's localhost Ollama server. For Colab, upload the notebook alone and use its rehearsal/read the included evidence, or configure an accessible Gemini account privately. Set `RUN_UI=True` to launch Gradio; public share links should use fictional inputs.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe validate_local.py --output data/my-local-validation.json
```

All **27 C3 tests** pass. Controlled fixtures establish mechanics; the separate actual local runs establish operating model generation, tool round trips and reflection. Final acceptance: seven turns, one saved lead, two saved feedback/unknown records, seven actual reflection passes, plus a controlled changed-draft review. Earlier failed development runs are preserved. See [verification](docs/verification.md).

## Submission and hosting

Submit the [C3 GitHub folder](https://github.com/by-aseel/PlotTwist/tree/main/c3_business_assistant), notebook and current demo video according to the portal's requested fields. Source, PDF/summary, README, configuration templates, report and evidence are included. The original assignment names Gemini/OpenAI; the user-selected local alternative is explicitly identified and Gemini integration is retained. Understand the code and follow course attribution rules.

The [free Hugging Face Static preview](https://huggingface.co/spaces/by-aseel/plottwist-free-demo) uses browser demonstration logic. It does not host Python, Gradio or Ollama. Full Python Space hosting remains unavailable on this account. The prepared Gradio package can use Gemini with a private secret after access is restored; local mode needs Ollama on the same host. No paid plan or billing has been enabled.

Earlier [offline walkthrough](docs/functionality_walkthrough.mp4) and [quick rehearsal](docs/quick_demo.mp4) remain historical supplementary videos. The current [video scope](docs/local_video_scope.md) distinguishes actual local captures and the controlled reflection challenge.

## Troubleshooting

- **Server/model unavailable:** start Ollama, check `ollama list`, and pull `qwen2.5:3b`.
- **Port occupied:** use `python app.py --mode local --port 7863`.
- **Activation blocked:** call `.venv\Scripts\python.exe` directly; no policy change is needed.
- **Dependency missing:** install requirements with the interpreter used to launch.
- **Wrong mode:** use `--mode local` and check the UI badge.
- **Model mistakes:** inspect the trace and sources; tool success is separate from answer quality.
- **Gemini error:** see [historical migration status](docs/gemini_migration.md). Quota reset does not repair project access denial.

## Implementation references

- [Ollama chat API](https://docs.ollama.com/api/chat)
- [Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling)
- [Google function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Gradio ChatInterface](https://www.gradio.app/docs/gradio/chatinterface) — pinned 5.50.0.
