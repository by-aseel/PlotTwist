# C3 / Five-minute demo script

Use live mode for the final model demonstration. Demo mode is suitable for rehearsal; name it accurately if you show it. The messages below are inputs and expected **behaviors**, not a transcript of an unperformed live run.

| Time | On screen | What to say or do |
|---|---|---|
| 0:00-0:40 | Branded app and experience cards | "PlotTwist creates fictional mystery adventures. Clue helps guests explore services and routes enquiries to useful actions." |
| 0:40-1:20 | Notebook persona and instructions | Explain the difference between the voice of Clue and the rules about facts, unknowns, and contact records. |
| 1:20-2:00 | General question | Ask: "What options suit 10 friends, and what are the starting prices?" Show the general route and compare the answer with the business PDF. |
| 2:00-2:50 | Enquiry conversation | Ask: "I'd like the team to contact me about a birthday mystery for 10 people." Then provide: "My name is Sam Rivera. My email is sam@example.com. Please save this enquiry." Show collection of missing fields and the lead tool observation. |
| 2:50-3:30 | Feedback | Ask: "Feedback: the instructions at the start of our mystery felt rushed." Show the feedback record and a courteous acknowledgement. |
| 3:30-4:10 | Unknown question | Ask: "What is your cancellation policy?" Show that Clue does not invent terms, records the question, and explains human follow-up. |
| 4:10-4:40 | Trace | Point to a requested tool, its arguments, the returned observation, and draft/reflection evidence. Explain that a local record is not a sent email. |
| 4:40-5:00 | Source and checklist | Show the business sources, notebook, requirements, README, and route/tool checks. State the run mode used and remaining deployment choice. |

## Questions worth preparing for

- **Why a router?** It makes each message's handling visible and gives the three assignment intents dedicated paths.
- **Where is memory?** Recent conversation turns are passed into the agent; SQLite holds explicit lead and feedback records.
- **What makes this an agent?** In live mode, model tool requests cause validated local actions and the resulting observations return to the model before the final answer.
- **What happens with unknown facts?** The assistant admits the gap and records the question instead of creating a price, policy, venue, or capability.
- **What does reflection prove?** The trace makes a check and any revision visible. It is evidence about that run, not a guarantee that every future answer is correct.
