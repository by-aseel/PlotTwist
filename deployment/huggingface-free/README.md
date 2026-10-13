---
title: PlotTwist Free Mystery Concierge
emoji: 🗝️
colorFrom: green
colorTo: gray
sdk: static
app_file: index.html
pinned: false
license: mit
short_description: A free interactive PlotTwist mystery-experience demo
---

# PlotTwist / Free Browser Demo

Make a memory. Leave a mystery. A free Static Space for the PlotTwist coursework project, featuring Aseel, Noah, Jiso, and Felix.

## Try it

- Explore the four fictional experiences.
- Chat with Clue using scripted responses and a three-way message router.
- Save a fictional enquiry and feedback using the browser-local demonstration tools.
- Inspect the action trace and rule-based draft/revised reflection.
- View and export your session's casebook as JSON.

Example enquiry: `My name is Taylor. Please save my enquiry for a birthday mystery for 12 people. My email is taylor@example.com.`

No API key, subscription, or Python server is needed to use this free demo. Records are stored only in the visitor's browser; no contact details are transmitted by this application. Responses and reflection are deterministic, not model-generated.

## Full course implementation

[C3 Gradio/Python project](https://github.com/by-aseel/PlotTwist/tree/main/c3_business_assistant) · [C3 notebook](https://github.com/by-aseel/PlotTwist/blob/main/c3_business_assistant/business_agent.ipynb) · [C4 Persona Lab](https://github.com/by-aseel/PlotTwist/tree/main/c4_persona_lab)

The full C3 implementation includes Gradio ChatInterface, native Gemini function calling, PDF/TXT loading, SQLite, and model reflection. This Space is the free browser-only demo; it does not host that Python backend or demonstrate live model calls. It should accompany, rather than replace, the required notebook and live assignment demonstration.

Deploy by uploading these six files to the root of a Static Space. No build step or external JavaScript dependencies are required.
