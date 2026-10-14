---
title: PlotTwist C3 Mystery Concierge
emoji: 🗝️
colorFrom: green
colorTo: gray
sdk: gradio
sdk_version: 5.50.0
python_version: "3.12"
app_file: app.py
pinned: false
license: mit
short_description: Mystery experiences, enquiries, feedback, and reflection
---

# PlotTwist / C3 Mystery Concierge

**Make a memory. Leave a mystery.** Meet Clue, the adventure consultant for a fictional mystery-experience studio. The team is Aseel, Noah, Jiso, and Felix.

This Space runs the C3 coursework application's custom Gradio ChatInterface, three-way message router, validated customer-interest and feedback tools, local casebook, and optional reflection pass.

## Try the demo

1. Ask `What adventures do you offer?`.
2. Send `My name is Taylor. Please save my enquiry for a birthday mystery for 12 people. My email is taylor@example.com.`.
3. Send `The puzzles were too difficult.` or `Are your City Quests wheelchair accessible?`.
4. Inspect **Latest activity**, then **The casebook → Refresh this casebook**.

Without an Gemini key, the interface explicitly runs a scripted offline demo with actual local tool writes. In live mode, Gemini generates responses and tool calls, and a second model call checks the draft against the instructions. The trace records the original and revised replies. The offline demo cannot establish live model performance.

## Source and notebook

[Complete C3 source and README](https://github.com/by-aseel/PlotTwist/tree/main/c3_business_assistant) · [Self-contained notebook](https://github.com/by-aseel/PlotTwist/blob/main/c3_business_assistant/business_agent.ipynb) · [Tool schemas](https://github.com/by-aseel/PlotTwist/blob/main/c3_business_assistant/docs/tool_schemas.md)

`app.py` bootstraps a ZIP bundle of those same Python modules, CSS, and business files. The bundle has no environment file, credentials, or runtime database. Keeping the deployment to four root files makes browser upload reproducible; the readable implementations remain available in GitHub and in the coursework notebook.

## Free local generation

The packaged source also supports `--mode local` with Ollama and `qwen2.5:3b`. That server must run on the same machine as Python; an ordinary hosted Space cannot connect to the owner’s laptop at localhost. This package does not install model weights or provide a hosted Ollama server. Actual local-model evidence and the current video are in the linked C3 repository.

## Owner configuration

For live mode, the owner can add `GEMINI_API_KEY` as a **Space secret**, set `GEMINI_MODEL=gemini-3.5-flash-lite`, and set `PLOTTWIST_MODE=live`. The default is `auto`, which chooses demo when no key is configured. Do not put a key in repository files.

Starting prices, experiences, and team roles are fictional. Saved enquiries do not send email or confirm bookings. Local records may be lost when the Space restarts; use synthetic contact details for coursework demonstrations.
