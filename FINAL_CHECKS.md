# Final delivery checks / 14 October 2026

- C3: 20 automated tests passed; 10 offline notebook cells executed. Native Gemini integration and reflection remain included; Google generation is denied.
- C4: 36 automated tests passed; 14 notebook cells executed; custom manual LangGraph ReAct implementation retained.
- Actual local C4 study: 252 initial Qwen2.5 3B/1.5B attempts across 18 configurations, seven cases and two paired seeds. Another 14 actual runs validate the printed-action parser correction.
- Actual evidence includes replies, failed attempts, tool observations, native token/timing metadata, model digests, comparison tables and five measured reflection answers. A 21-output assistant review is explicitly distinguished from independent human scoring.
- Reply termination, expected tools, rejected tool calls, successful local saves and factual quality are separate measures. The report preserves hallucinations and does not promise full marks or autonomous reliability.
- Earlier 238 deterministic checks and archived offline videos remain labeled as workflow demonstrations.
- Real local Gradio callbacks are exercised; the free Static Space remains a browser preview. Full Python backend hosting is still account-blocked.
- Notebooks and ZIPs are checked for credentials, execution errors and integrity. Real .env files, databases, caches, runtime binaries and model weights are excluded from submission and Git.

Read the [C4 measured report](c4_persona_lab/docs/evaluation_report.md), [local setup](c4_persona_lab/docs/local_models.md), and each project's verification notes.
