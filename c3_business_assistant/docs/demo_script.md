# Actual local C3 demo / English

Start Ollama with qwen2.5:3b, launch `python app.py --mode local`, and check **LOCAL AI · OLLAMA**. Keep reflection checked. Use fictional contacts only.

1. Ask: `What does Birthday Mystery Nights include, how long does it last, and what is its starting price?` Show the factual answer and general-question route; inspect any qualifiers against the business dossier.
2. Send: `Please save an enquiry for a birthday mystery for 10 guests.` Then `My name is Aseel.` Then `My email is aseel@example.com.` Show missing-field questions followed by record_customer_interest and its actual success observation.
3. Ask: `Do you have confirmed wheelchair access at a venue next Friday?` Show record_feedback and the statement that access/availability cannot be confirmed.
4. Send: `The puzzles were too difficult. Please record my feedback.` Show its actual feedback observation.
5. Open **The casebook**, refresh, and show this session's saved records.
6. Expand **Reflection** in Latest activity: original draft, reviewed reply, checks, changed flag and native generation metadata. An unchanged reply is still a review, not a correction.
7. Open **Reflection lab** and review the supplied deliberately flawed test draft. Show the actual correction and its clear test-input provenance. This separate experiment creates no records.

The current [English demonstration](local_functionality_demo.mp4) is an edited walkthrough of actual browser captures. [Scope](local_video_scope.md) explains its evidence. The seven-case automated actual run and a controlled reflection run are in the JSON evidence files. The previous videos used deterministic rehearsals and remain labeled accordingly.
