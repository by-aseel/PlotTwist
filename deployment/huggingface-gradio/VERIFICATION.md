# PlotTwist C3 Space preparation

Validated locally on 14 October 2026. Hosting is not yet deployed.

- Four upload files are prepared: `app.py`, `README.md`, `requirements.txt`, and `LICENSE`.
- The bootstrap reconstructs nine runtime files byte-for-byte from the current C3 source, including the free local-model transport and Reflection lab.
- Gradio app construction succeeds using the pinned local dependencies.
- In a simulated Space environment, launch selects `0.0.0.0:7860` with public Gradio sharing disabled.
- Offline enquiry and unanswered-question requests execute the real local tools and produce lead/feedback records.
- Records remain scoped to the browser/session identifier.
- The upload files contain no API key, environment file, or customer database.
- These bootstrap checks use demo mode. Separate actual local-model generation, tools and reflection are verified in the C3 report/video; no Gemini cloud build or hosted Python Space is claimed.

Hugging Face's signed-in creation page currently disables Gradio and Docker Spaces on this account and says a paid PRO plan is required. A free Static Space would not execute this Python backend. The full Gradio app can be uploaded once Gradio hosting is available on the owner's account.
