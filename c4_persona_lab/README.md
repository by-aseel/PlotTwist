---
title: PlotTwist C4 Persona Lab
emoji: 🔎
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 5.50.0
python_version: "3.12"
app_file: app.py
pinned: false
---

# PlotTwist / C4 Persona Lab

**One business. Three minds. Follow every action.**

This standalone C4 project extends PlotTwist into a custom ReAct agent built with **LangGraph**. Three personas approach the same mystery-experience business differently: Clue welcomes new guests, Cipher checks the plan, and Muse develops the story. The designed Gradio lab exposes persona and generation controls alongside an observable action/observation trace.

The fictional business team is **Aseel** (Story Director), **Noah** (Puzzle Architect), **Jiso** (Experience Producer), and **Felix** (Guest Experience Lead).

## English functionality video

**[Watch the short working demo](docs/quick_demo.mp4)** — 32 seconds, focused on replies, tools, and saved records.

[Watch the full narrated C4 walkthrough](docs/functionality_walkthrough.mp4) · [Transcript](docs/functionality_transcript.md) · [Subtitles](docs/functionality_walkthrough.srt)

The 8:31 video covers the working features, implementation, setup, and checks. It uses actual offline UI captures and source explanations, with synthesized English narration. [Video scope and evidence limits](docs/functionality_video.md) explains what still needs a live model run.

## Run locally

Use Python 3.11 or 3.12. Open a terminal inside this folder.

On Windows, double-clicking `launch_demo.bat` also creates a local virtual environment, installs the requirements, and launches demo mode.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py --mode demo
```

On macOS/Linux, activate with `source .venv/bin/activate`. If PowerShell activation is restricted, use `.\.venv\Scripts\python.exe` directly. Open the local address printed by Gradio, normally `http://127.0.0.1:7861`.

Demo mode uses a deterministic scenario simulator through the real graph. It proves that parsing, actions, observations, and termination can work together. Its scripted persona wording and unchanged sampling behavior cannot establish which LLM configuration is best.

For live mode, copy `.env.example` to `.env`, insert your private Gemini API key, then run:

```powershell
python app.py --mode live
```

The initial model is `gemini-2.5-flash-lite`. `--mode auto` selects live mode when a key is present, otherwise demo. The package includes no real API key. Live API use and model comparisons can incur account charges.

## What is included

| File | Purpose |
|---|---|
| `react_agent.ipynb` | Main executable teaching notebook and comparison walkthrough |
| `gemini_client.py` | Native Google Gen AI transport, safe errors and matching tool observations |
| `plottwist_agent.py` | Manual ReAct nodes, state transitions, parser, model adapters, and prompt assembly |
| `personas.py` | Three personas, matching generation defaults, rationale, and setting validation |
| `business_tools.py` | Catalogue search, estimates, validated enquiry/feedback storage, tool registry |
| `experiments.py` | Reproducible comparison runner and result export |
| `app.py` | Designed Gradio persona lab |
| `me/` | PDF business dossier and both summary filename variants |
| `docs/reflection.md` | Answers to all five reflection questions, with evidence limitations |
| `docs/assignment_checklist.md` / `docs/demo_script.md` | Submission map and walkthrough |
| `docs/verification.md` | What was tested, how to reproduce it, and what still requires a live API run |
| `docs/demo_walkthrough.mp4` | Supplementary captioned walkthrough made from actual offline UI screenshots |
| `tests/` | Behavioral checks for the implementation |

## Defined use case

**Scenario:** a fictional PlotTwist Experiences concierge helps a guest plan a mystery event. Example request: "Plan a birthday mystery for 10 friends with a USD 300 budget."

- **Goal:** recommend a suitable experience, check group capacity and indicative price, propose a labeled story concept when appropriate, and record authorized enquiries or feedback.
- **Target audience:** birthday hosts, friends and small groups, workplace teams, and guests requesting custom stories.
- **Tools:** `search_experiences`, `estimate_event`, `record_customer_interest`, and `record_feedback`.
- **Constraints:** use only known catalogue facts; custom adventures require a quote. No live availability, verified venue/access arrangements, payment, email-sending or booking service exists. SQLite records are local, and a recorded enquiry does not confirm an event.

## The manual ReAct loop

The code constructs a `StateGraph` with explicit state, custom nodes, and conditional edges. It does not use `AgentExecutor`, `create_react_agent`, or a prebuilt tool executor.

1. Build the persona, dedicated instructions, tool descriptions, knowledge, history, and current message.
2. Ask the model for a JSON **action** or **final** response.
3. Parse the response and validate the exact tool name and argument schema.
4. Execute the tool and append its real result as an observation.
5. Return to the model so the observation can change the next action.
6. Finish on a valid final response, or stop with an explicit bounded-loop/error outcome.

The graph diagram can be generated directly from the live implementation:

```python
from plottwist_agent import build_agent
agent = build_agent(mode="demo")
print(agent.graph.get_graph().draw_mermaid())
```

The trace records actions, tool observations, parsing/loop events, and optional brief plans. A brief plan is a short customer-visible account of the next step; it is not a transcript of private model reasoning.

## Persona design

| Persona | Primary task | Style and values | Temperature | Top-p | Frequency / presence penalty | Output cap |
|---|---|---|---:|---:|---:|---:|
| Clue | Match first-time guests to an experience | Warm, clear, lightly playful; inclusion and honest expectations | 0.45 | 1.0 | 0.15 / 0.0 | 700 |
| Cipher | Check capacity, budget, duration, and missing constraints | Precise, compact, numerical; feasibility and accuracy | 0.10 | 1.0 | 0.0 / 0.0 | 850 |
| Muse | Invent a personalized story concept within the facts | Vivid, accessible, original; guest agency | 0.85 | 1.0 | 0.30 / 0.50 | 1000 |

These are design hypotheses. Low temperature can reduce variation but does not guarantee truth; higher temperature is not itself proof of creativity. Default top-p stays at 1.0 so temperature is the principal sampling change. The experiment runner changes individual controls to make comparisons more interpretable.

`max_tokens` maps to native Gemini `max_output_tokens`. Top-k is validated and forwarded (persona defaults: 40; comparison: 20). The experimental matrix targets Gemini 2.5, if accessible. Google discourages changing sampling defaults on Gemini 3; current interactive setup uses Gemini 3.5 Flash-Lite with minimal thinking. Sampling controls remain explicit coursework experiments, with unsupported settings reported as errors.

## Prompt experiments

- **Direct vs. brief plan:** compare a final/action response with a short visible plan. This is a CoT-style prompting proxy; hidden chain-of-thought is never requested or displayed.
- **Zero-shot vs. few-shot:** the zero-shot condition has no solved task demonstrations. Both retain a minimal "hello" protocol example to satisfy the instruction-format requirement. Few-shot adds complete action/observation examples for actual tasks.
- **System vs. in-message instructions:** move the experimental persona/instructions block between roles. Fixed business boundaries and output-format constraints remain system-level in both conditions.
- **Full vs. compact instructions:** compare the detailed operational block with a shorter block. This tests instruction detail without removing the core factual and consent constraints.
- **Generation configuration:** vary temperature, top-p, penalties, output cap, and optionally a second compatible model.

The code implements one chosen framework, LangGraph. The three personas are configurations of one agent, not three agents negotiating with each other.

## Tools and business boundaries

| Tool | Purpose |
|---|---|
| `search_experiences` | Match catalogue experiences to the request and group size |
| `estimate_event` | Check group fit and return the catalogue's indicative group starting price |
| `record_customer_interest` | Save customer-authorized name, email, and enquiry notes locally |
| `record_feedback` | Save feedback or an unknown question locally |

See `business_tools.py` and the notebook for the exact schemas and outputs. Local SQLite records do not send email, make a booking, or create an appointment. Group starting prices are USD 240 for Birthday Mystery Nights, USD 90 for City Quests, and USD 650 for Corporate Missions. Custom Story Adventures requires a quote. There is no live availability or verified venue; language and access requirements need a person to review them.

## Reproduce the comparisons

```powershell
python -m unittest discover -s tests -v
python experiments.py --mode demo --repeats 2 --output experiments/demo
```

The demo run is a workflow check. After adding a key, collect actual model evidence with:

```powershell
python experiments.py --mode live --repeats 2 --output experiments/live
```

For a model-type comparison, add `--model MODEL_A --compare-model MODEL_B` using two compatible model names available to your account. Results are written as `metrics.csv`, `raw_traces.json`, `comparison.md`, and `human_ratings.csv` under the output directory. Keep demo and live results in separate directories. A full live matrix makes many requests; use `python experiments.py --help` to inspect the available controls before running it.

Read raw traces before interpreting aggregate scores. Complete the human-rating sheet for helpfulness, naturalness, and persona fit, then update `docs/reflection.md` with the actual results. Do not claim a best configuration from scripted demo outputs.

Package validation passed 29 backend/transport tests and executed the notebook's offline code cells through IPython. The included demo comparison contains 238 deterministic runs across 17 variants, 7 cases, and 2 repeats. These are workflow checks, not measured LLM performance. See `docs/verification.md` for the validation scope and limits.

## Notebook and presentation

Open `react_agent.ipynb` in Jupyter, or upload **only that notebook** to Colab and run from the top. It is self-contained: it reconstructs supporting assets in `c4_persona_lab_notebook/`, and the complete editable modules appear in readable `%%writefile` cells. It runs an action/observation example, compares the personas, and provides opt-in live evaluation and the reflection write-up. `docs/demo_script.md` supplies a concise presentation plan.

`docs/demo_walkthrough.mp4` is a supplementary captioned video built from actual offline UI screenshots. It is not a continuous live API screen recording; record the final live demonstration after adding your key. To create a temporary public Gradio link deliberately, use `python app.py --mode demo --share`, or set `share=True` in the notebook launch cell. Use synthetic records. Both project folders are published in this repository. No public Gradio link or hosted deployment has been created.

## Optional hosting

For Hugging Face Spaces, create a Gradio Space and put this folder's contents at its root. README metadata already identifies Gradio 5.50.0, Python 3.12, and `app.py`. Set the API key as a secret and configure `PLOTTWIST_MODE=live`, `GRADIO_SERVER_NAME=0.0.0.0`, `PORT=7860`, and your model. Hosted disk can be ephemeral; SQLite here is a teaching store. Exclude `.env`, customer data, and private traces from uploads.

## Troubleshooting

- A missing package usually means the notebook and terminal use different Python environments; install the requirements in the running interpreter.
- A malformed action is handled by the graph's format/error path. Inspect the trace instead of treating it as a successful tool call.
- A low output cap can truncate JSON; raise it and compare again, preserving the failed run in your evaluation.
- A model may reject a sampling parameter. Use a compatible Chat Completions model; the app does not silently claim to apply unsupported settings.
- If the port is occupied, set `--port 7863`.
- If notebook files are missing, rerun the setup cell and the relevant `%%writefile` cells; the notebook includes the required modules and assets.

## Course alignment

Prepared for the supplied EECE 503P/798S C4 assignment and lecture material. See the checklist for the exact rubric mapping and the reflection for honest interpretation limits. Review and understand the code, run live experiments, and follow your course's attribution rules before submission.

## Implementation references

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) explains the states, custom nodes, and conditional edges used to build the loop.
- [Gemini GenerateContent API](https://ai.google.dev/api/generate-content) documents the live native generation interface and parameters. C4 parses its own JSON action protocol instead of using a prebuilt executor.
- [Gradio ChatInterface](https://www.gradio.app/docs/gradio/chatinterface) documents the chat component used in the lab. This project pins Gradio 5.50.0; newer documentation may describe later releases.

## Gemini access and remaining evidence (14 October 2026)

Both projects now use the native Google Gen AI SDK. Real generation probes returned 404 for Gemini 2.5 Flash-Lite (unavailable to new users) and 403 for Gemini 3.5 Flash-Lite, 3.1 Flash-Lite, 3.5 Flash and 3.8 Flash (project access denied). Listing models succeeded, but this does not establish generation access. No successful live answer or empirical LLM winner is claimed. See [Gemini migration and rerun instructions](docs/gemini_migration.md) for the remaining action.
