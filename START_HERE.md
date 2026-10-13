# Welcome to PlotTwist

Two complete, separate course projects share one fictional mystery-experience studio. The team is **Aseel, Noah, Jiso, and Felix**. Each folder contains its own application, self-contained notebook, business PDF, summary, README, dependencies, examples, and presentation materials.

| Open this | What you get |
|---|---|
| [C3 Business Assistant](c3_business_assistant/README.md) | Clue, three-way routing, lead/feedback tools, chat memory, and reflection |
| [C4 Persona Lab](c4_persona_lab/README.md) | Clue/Cipher/Muse personas, a manual LangGraph ReAct loop, configurable prompts, and experiment reports |
| [C3 notebook](c3_business_assistant/business_agent.ipynb) | Standalone Jupyter/Colab submission |
| [C4 notebook](c4_persona_lab/react_agent.ipynb) | Standalone Jupyter/Colab submission |
| [C3 walkthrough](c3_business_assistant/docs/demo_walkthrough.mp4) | Captioned video using actual offline UI screenshots |
| [C4 walkthrough](c4_persona_lab/docs/demo_walkthrough.mp4) | Captioned video using actual offline UI screenshots |

## Fastest start on Windows

Install Python 3.11 or 3.12, open either project folder, and double-click **`launch_demo.bat`**. It creates a local virtual environment, installs the pinned requirements, and launches Gradio. The first run needs internet access to install dependencies. Follow the local URL printed in the terminal.

To run manually from either project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py --mode demo
```

C3 defaults to port **7860**; C4 defaults to **7861**. Demo mode needs no key and uses real local tools with deterministic responses. For Colab, upload only the desired `.ipynb` and run top to bottom; its source modules and support files are embedded.

## Ready to use

- Two custom Gradio interfaces and the complete editable Python source.
- Two self-contained notebooks, with readable main implementation cells.
- Business PDFs, summaries, separate READMEs, requirement maps, and presentation scripts.
- Local SQLite enquiry/feedback logging and visible action traces.
- C4 comparison runner plus 224 saved **demo** runs, a raw trace file, metrics, and a human-rating sheet.
- Offline validation: **15 C3 tests + 23 C4 tests passed**, and both notebooks' offline code cells executed through IPython. Each project's `docs/verification.md` records the scope and limits.

## Finish the account-dependent steps

1. Copy `.env.example` to `.env` inside the chosen project and add your private OpenAI API key.
2. Launch `python app.py --mode live`, check the reported mode, and demonstrate actual model tool use. No live API connection was verified during preparation.
3. In C4, run `python experiments.py --mode live --repeats 2 --output experiments/live`. Complete the human-rating sheet and add measured findings to `docs/reflection.md`.
4. Record your final walkthrough using the supplied script. The included MP4s are supplementary screenshot presentations, not continuous recordings of live API calls.
5. This repository contains both project submissions. Add your final live video link and completed C4 findings, then submit the relevant project folder link through your instructor's submission channel. Keep `.env`, private traces, and customer databases out of Git.
6. A [free PlotTwist Static Space](https://huggingface.co/spaces/by-aseel/plottwist-free-demo) is deployed. It is a browser-only scripted demo. The full Python/Gradio deployment remains separate; its instructions and metadata are included in each README.

The business, prices, and example customer data are fictional. Enquiry tools save local records; they do not send email or confirm bookings. The demo experiments verify the workflow and cannot establish a best-performing LLM persona.
