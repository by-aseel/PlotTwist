# C3 submission map

This map distinguishes included implementation from account-dependent submission steps.

| Requirement | Evidence to inspect | Status |
|---|---|---|
| Fictional identity, mission, services, team, value proposition | `me/about_business.pdf`, `me/business_summary.txt` | Included |
| Alternate summary filename in task text | `me/summary.txt`, identical to `business_summary.txt` | Included |
| Main Jupyter/Colab notebook | `business_agent.ipynb`, self-contained with readable implementation cells | Included; offline cells executed |
| Clearly labeled persona and instructions | Notebook sections and agent source | Included |
| Three-way message router | Backend routing function; notebook routing walkthrough | Implemented; demonstrate all three routes |
| Name/email/notes lead collection | `record_customer_interest(email, name, message)` | Implemented |
| Feedback and unanswered questions | `record_feedback(question)` | Implemented |
| Tool schemas and observable results | Source schemas, README tool table, notebook trace | Included |
| Summary and PDF used for knowledge | Source loading code and notebook source inspection | Included |
| History and model-selected tool calls | Live backend model loop | Implemented; run with your API key |
| Gradio ChatInterface | `app.py` | Included |
| API key in local `.env`, not uploaded | `.env.example` and `.gitignore` | User supplies private key |
| Working installation | `requirements.txt`, tests, README commands | 15 backend tests passed; rerun in your environment |
| Reflection bonus | Reflection implementation and trace | Included; inspect a draft/revision pair |
| GitHub repository and video | `docs/demo_script.md`, supplementary `docs/demo_walkthrough.mp4` | Screenshot walkthrough included; final live recording and GitHub publication remain user steps |
| Hugging Face bonus | README deployment instructions | Optional; not deployed by this package |

## Before recording

1. Install requirements and run the tests.
2. Add your key locally, choose live mode, and verify that the run reports live mode.
3. Show a factual question, complete lead collection, and a feedback/unanswered question.
4. Open the tool trace and show actual tool observations and reflection evidence.
5. Record the walkthrough with synthetic contact details and no visible key.
6. Review the final files, omit secrets and runtime customer records, then publish the repository and submit your video according to the course instructions.

Demo mode is useful for rehearsals and plumbing checks. Its canned responses must not be described as measured LLM behavior or model-generated tool choices.
