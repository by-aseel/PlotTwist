# C3 verification / 14 October 2026

**27 behavioral/transport tests pass.** These controlled fixtures verify routing, multi-turn collection, customer provenance, deduplication, session isolation, malformed arguments, loop bounds, failure handling, native Gemini observation matching, local transport, structured actions and reflection. Fixtures do not measure model quality.

Separate actual Ollama runs are preserved in [local_validation.json](local_validation.json) and [local_reflection_challenge.json](local_reflection_challenge.json), with the [measured report](local_evaluation_report.md). The final seven turns request and execute both required tools and review replies with the actual model. Earlier development failures are retained. The controlled flawed-draft correction has no database side effects. No cloud answer or fallback is claimed.

The self-contained notebook's **10 code cells** execute through IPython in a clean directory. Its default conversation is a deterministic rehearsal; a separate evidence cell displays saved actual local outputs and the report. Set RUN_LOCAL=True for fresh local generations after starting Ollama. No remote Colab session is claimed.

```powershell
python -m unittest discover -s tests -v
ollama pull qwen2.5:3b
python app.py --mode local
```

The browser UI is exercised with actual local-model responses, tool observations, the session casebook and Reflection lab. [Current English video](local_functionality_demo.mp4) and [scope](local_video_scope.md) document that evidence. Earlier offline videos remain historical rehearsals. Full Python hosting on Hugging Face is still account-blocked; the free Static Space is a scripted preview. Gemini's historical 403/404 failures are preserved and have not been retried. Notebook bundles and submission archives exclude credentials, customer databases and model weights.
