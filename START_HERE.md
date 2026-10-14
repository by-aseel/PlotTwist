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
- C4 comparison runner plus 238 saved **demo** runs, a raw trace file, metrics, and a human-rating sheet.
- Offline validation: **20 C3 tests + 36 C4 tests passed**, and both notebooks' offline code cells executed through IPython. Each project's `docs/verification.md` records the scope and limits.

## Run actual models and submit

1. C4 supports free local Ollama generation; install Ollama and pull `qwen2.5:3b`. No API key is needed for local mode.
2. For C3 or the optional C4 Gemini route, configure a private Gemini key and launch `--mode live` when generation access is restored. Google project access denial remains unresolved; the C4 local route works independently.
3. C4 now runs free actual models with `python app.py --mode local` after installing Ollama and pulling `qwen2.5:3b`. The 252-run comparison, 14 parser reruns and measured reflection are already included; see `c4_persona_lab/docs/local_models.md`.
4. Record your final walkthrough using the supplied script. The included MP4s are supplementary screenshot presentations, not continuous recordings of live API calls.
5. Review the files and create/push your GitHub submission. Keep `.env`, private traces, and customer databases out of the repository. The GitHub repository has been published; submit its assignment folder link and the requested notebook/demo evidence.
6. Hugging Face Spaces deployment is optional; instructions and Space metadata are included in each README. A free Static demo is deployed; the updated Gradio package is prepared but its Python backend is not hosted.

The business, prices, and example customer data are fictional. Enquiry tools save local records; they do not send email or confirm bookings. The demo experiments verify the workflow and cannot establish a best-performing LLM persona.

## Actual free C4 model evidence

[Measured report](c4_persona_lab/docs/evaluation_report.md) · [Five answers](c4_persona_lab/docs/reflection.md). These include actual Qwen model generations and failures, not simulator outputs. No paid API key is needed for local mode. The full backend must run on your computer; the free Static Space is a separate browser demonstration.
