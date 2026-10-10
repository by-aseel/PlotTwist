# C4 / Six-minute persona-lab walkthrough

The following is a recording plan, not a transcript of live results. Use live mode to demonstrate model-generated actions and say which model is running.

| Time | Show | Demonstration |
|---|---|---|
| 0:00-0:40 | Business and use case | Explain that PlotTwist helps guests choose and personalize mystery experiences; factual details come from a small catalogue. |
| 0:40-1:20 | Persona controls | Introduce Clue's guest advice, Cipher's logistics, and Muse's concept design. Show the differing prompt traits and generation defaults. |
| 1:20-2:10 | Action-observation loop | As Cipher ask: "Plan a birthday mystery for 10 people with a budget of USD 300." Inspect catalogue search, the estimate observation, and the final grounded recommendation. |
| 2:10-3:00 | Persona contrast | Start a fresh conversation as Muse. Ask the same question, adding: "Give it an original story hook." Compare style while checking that price and group constraints remain correct. |
| 3:00-3:45 | Unknowns and persistence | Ask: "Is your venue wheelchair accessible next Friday?" Show that missing access/venue/date information is not invented and the unknown is recorded. |
| 3:45-4:20 | Lead tool | Ask: "I'm Sam Rivera, sam@example.com. Please save my enquiry about a mystery for 10 friends." Show successful local storage, with no claim that an email or booking occurred. |
| 4:20-5:00 | Notebook and graph | Display actual `StateGraph` code, conditional edges, JSON action/final parsing, tool registry, and the loop bound. Explain why this is a manual ReAct implementation. |
| 5:00-5:40 | Experiments | Show direct/brief-plan, zero/few-shot, role and sampling comparisons. Open a raw trace and the aggregate report. Clearly identify demo versus live evidence. |
| 5:40-6:00 | Reflection | State one measured finding from your live run and one limitation. If only demo results exist, explicitly say that no empirical LLM winner has been established. |

## Explain the reasoning control accurately

"The brief-plan option exposes a concise plan for the next action, and the trace shows actual tool observations. We are not accessing private model reasoning. Our direct-versus-plan comparison is a practical CoT-style prompt experiment with that limitation."

## A good evaluation answer

Explain that the same task set and repeats help compare conditions; schema validity, successful tools, factual grounding, and human helpfulness ratings answer different questions. A colorful persona can sound attractive while making a wrong factual claim. Choose based on the evidence appropriate to the task, not the highest temperature or longest response.
