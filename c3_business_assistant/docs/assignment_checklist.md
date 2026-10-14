# C3 requirement-to-evidence map

| Requirement | Where to inspect | Evidence |
|---|---|---|
| Business identity, mission, services, team, value proposition | me/about_business.pdf; me/business_summary.txt | Fictional PlotTwist, Aseel/Noah/Jiso/Felix |
| Standalone notebook | business_agent.ipynb | 10 executed cells; sources and support files embedded |
| Separate persona and instructions | prompts.py; notebook labeled source section | PERSONA and INSTRUCTIONS assembled with PDF/TXT knowledge |
| Three intents before acting | plottwist_agent.py route_message; docs/local_validation.json | All three routes exercised with actual local model |
| record_customer_interest(email,name,message) | TOOL_SCHEMAS, agent loop | Three-turn contact collection and actual successful lead observation |
| record_feedback(question) | TOOL_SCHEMAS, agent loop | Actual unknown question and feedback logging |
| MCP-style tool schemas/logging | docs/tool_schemas.md; trace; terminal | Name, parameters, result schema and real local SQLite/print logs |
| Model receives history and tools | local_client.py; _live_reply | Native Ollama / structured action proposal, observation returned to model |
| Gemini/OpenAI model integration named in assignment | gemini_client.py | Native Gemini retained; account generation denied; local alternative accepted by user |
| Gradio ChatInterface | interface.py create_app | Real local chat, activity trace, casebook and Reflection lab |
| Reflection bonus | _reflect; docs/local_reflection_challenge.json | Actual second model pass; controlled flawed-draft correction visibly changed |
| Working installation and tests | README.md; docs/verification.md | 27 tests, clean notebook execution, actual model integration runs |
| GitHub and functionality video | Repository; docs/local_functionality_demo.mp4 | Current actual-local video plus earlier labeled rehearsals |
| Hugging Face bonus | Free Static Space; deployment instructions | Static preview deployed; full Python backend hosting remains unavailable |

## Submit

Submit the C3 GitHub folder link, the self-contained business_agent.ipynb and the current functionality video in the format your course portal requests. Include the business summary and PDF (already in the repository and embedded notebook). Check the portal's upload/link fields rather than assuming a repository link alone replaces explicitly requested files. Keep .env, real customer records and model weights private.

Current walkthrough: [video](local_functionality_demo.mp4), [script](demo_script.md), [measured evidence](local_evaluation_report.md). It uses fictional example contacts and real generated model responses. No numeric grade is guaranteed.
