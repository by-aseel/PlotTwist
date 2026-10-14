# Final delivery checks / 14 October 2026

- C3: 27 automated tests passed; 10 offline notebook cells executed. Actual free local model integration, model-requested tools and reflection are verified; Gemini remains included but Google generation is denied.
- C4: 36 automated tests passed; 14 notebook cells executed; custom manual LangGraph ReAct implementation retained.
- Actual local C4 study: 252 initial Qwen2.5 3B/1.5B attempts across 18 configurations, seven cases and two paired seeds. Another 14 actual runs validate the printed-action parser correction.
- Actual evidence includes replies, failed attempts, tool observations, native token/timing metadata, model digests, comparison tables and five measured reflection answers. A 21-output assistant review is explicitly distinguished from independent human scoring.
- Reply termination, expected tools, rejected tool calls, successful local saves and factual quality are separate measures. The report preserves hallucinations and does not promise full marks or autonomous reliability.
- Earlier 238 deterministic checks and archived offline videos remain labeled as workflow demonstrations.
- Real local Gradio callbacks are exercised; the free Static Space remains a browser preview. Full Python backend hosting is still account-blocked.
- Notebooks and ZIPs are checked for credentials, execution errors and integrity. Real .env files, databases, caches, runtime binaries and model weights are excluded from submission and Git.

Read the [C4 measured report](c4_persona_lab/docs/evaluation_report.md), [local setup](c4_persona_lab/docs/local_models.md), and each project's verification notes.


## Actual free C3 model evidence

[Current English functionality video](c3_business_assistant/docs/local_functionality_demo.mp4) · [Measured seven-case report](c3_business_assistant/docs/local_evaluation_report.md) · [Controlled reflection correction](c3_business_assistant/docs/local_reflection_challenge.json). C3 runs qwen2.5:3b through Ollama with no paid API key. The model requests the two real tools, observes their results and performs a second model review. The notebook displays this actual evidence separately from its default rehearsal. 27 C3 tests pass; the existing 36 C4 tests and measured study are retained. Full Python backend hosting on Hugging Face remains unavailable; the Static preview is separate.
