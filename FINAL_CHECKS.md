# Final delivery checks

Verified locally on 10 October 2026.

- C3: 15 backend tests passed; all 10 notebook code cells executed in order through IPython.
- C4: 23 backend tests passed; all 14 notebook code cells executed in order through IPython.
- C4 simulator: 224 recorded runs, covering 16 variants and 7 cases with 2 repeats. These are workflow checks, not live LLM findings.
- Browser: C3 enquiry submission, casebook refresh, and JSON export worked with the same browser session.
- Browser: C4 search and estimate sequence, persona switching, three-persona comparison, feedback storage, and JSON export worked.
- Desktop interfaces inspected. C4 phone-width inspection found clipping from Gradio padding; the shared layout was corrected and rechecked.
- Both four-page business PDFs were rendered and reviewed; the requested team is Aseel, Noah, Jiso, and Felix.
- Two 32-second captioned screenshot walkthroughs are included. They show offline demo states and are supplementary presentation material.
- The ZIP packages exclude runtime databases, caches, virtual environments, and real `.env` files.

No live OpenAI request, empirical LLM comparison, GitHub publication, or hosted deployment was performed. Follow `START_HERE.md` for those account-dependent steps. The source includes real API integration; offline mode is clearly labeled in the interface and saved experiments.
