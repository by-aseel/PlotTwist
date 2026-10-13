# PlotTwist C3 Space preparation

Validated locally on 14 October 2026. Hosting is not yet deployed.

- Four upload files are prepared: `app.py`, `README.md`, `requirements.txt`, and `LICENSE`.
- The bootstrap reconstructs eight runtime files byte-for-byte from the existing C3 source.
- Gradio app construction succeeds using the pinned local dependencies.
- In a simulated Space environment, launch selects `0.0.0.0:7860` with public Gradio sharing disabled.
- Offline enquiry and unanswered-question requests execute the real local tools and produce lead/feedback records.
- Records remain scoped to the browser/session identifier.
- The upload files contain no API key, environment file, or customer database.
- No live API call, cloud build, or public Space was verified by these local checks.

Hugging Face's signed-in creation page currently disables Gradio and Docker Spaces on this account and says a paid PRO plan is required. A free Static Space would not execute this Python backend. The full Gradio app can be uploaded once Gradio hosting is available on the owner's account.
