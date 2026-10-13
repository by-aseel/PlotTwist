# PlotTwist C4 — functionality walkthrough

Duration: 511.7 seconds. English narration uses the installed Microsoft Zira Desktop voice.

This is an **edited screenshot walkthrough of actual UI interactions**, with readable source and captured trace explanations. It is not a continuous screen recording. The local apps were run in explicit offline demo mode; the public Space is the Static JavaScript demo. No live OpenAI API call is shown. Only synthetic customer details are used.

### 00:00:00.000 — One mystery. Three minds.

Now, the C4 Persona Lab. It extends the same fictional business with three distinct agent personas and a manually assembled LangGraph action loop. This section shows configuration controls, search and estimate tools, persona comparison, records, experiments, and reflection. The captured responses are offline simulations running through the real graph, not measurements of a live language model.

### 00:00:29.538 — Each persona has a task, voice, and configuration.

Clue helps first-time guests select an experience. Cipher checks group capacity, budget, and duration. Muse develops original story concepts within known business constraints. Each persona has its own prompt, task, settings, and rationale. The configuration file starts Clue at temperature 0.45, Cipher at 0.10, and Muse at 0.85, with different penalties and output budgets.

### 00:01:01.535 — The lab exposes the experiment controls.

The interface lets me choose a persona, direct or brief-plan responses, zero-shot or few-shot examples, and system or in-message instruction placement. Sampling controls include temperature, top-p, penalties, and maximum output tokens. Switching persona loads its defaults. Offline mode demonstrates the control wiring; changing sampling values does not turn the scripted simulator into a stochastic model.

### 00:01:32.643 — Cipher checks an event brief against the catalogue.

I ask Cipher to plan a birthday mystery for ten people with a three-hundred-dollar budget. The graph searches the catalogue, estimates the selected package, and produces a grounded planning brief. Birthday Mystery Nights fits ten guests, lasts one hundred twenty minutes, and starts at two hundred forty dollars per group. Final scope and availability still require human review.

### 00:01:59.712 — Reason → act → observe → continue.

The trace exposes an action with tool arguments, then the actual returned observation. A second action estimates the selected experience. The observation reports capacity, duration, and starting price, and the next step produces the final reply. The brief plan is a concise explanation of the next action. It is not private model reasoning or evidence of a live model thinking process.

### 00:02:28.064 — Muse adds a story concept while keeping the facts.

I start a fresh chat with Muse and request the same birthday plan, adding an original story hook. The answer proposes a missing-alibi concept where each guest contributes one page to the final reveal. The package size, duration, and starting price remain the same. The imagined story is labeled as a concept rather than a confirmed service inclusion.

### 00:02:52.313 — Compare the same brief across all three personas.

Persona Studio sends the shared brief to fresh conversations for Clue, Cipher, and Muse. Clue asks about the atmosphere. Cipher lists practical checks. Muse offers a story concept and personalization question. The side-by-side display keeps the factual baseline comparable. Here, these style differences are scripted demonstrations; the display does not establish which real model persona performs best.

### 00:03:23.954 — A lead is recorded through the same graph.

I provide the fictional customer name, email address, and permission to save the event enquiry. The graph selects record customer interest, validates the arguments, writes a local record, and returns the observation. The final reply acknowledges storage. It explicitly avoids claiming that an email was sent or a reservation was created.

### 00:03:48.998 — Feedback and unknowns become useful records.

Feedback about difficult puzzles triggers the feedback tool. A later question about wheelchair access and next Friday is also logged because the catalogue cannot verify those details. The graph returns a successful storage observation, and the assistant states the information gap. These cases show the boundary between a known business fact and a detail that needs team confirmation.

### 00:04:15.091 — A budget constraint stays visible in the answer.

I lower the budget to one hundred dollars. The estimate still reports the real catalogue starting price of two hundred forty dollars for the birthday package. Cipher explicitly says that this exceeds the stated budget. The answer preserves the constraint rather than changing the price to make the recommendation seem feasible.

### 00:04:36.775 — Inspect and export the C4 casebook.

The C4 casebook shows the saved customer enquiry, puzzle feedback, and unanswered accessibility question from this session. Export creates a downloadable JSON file. The local records preserve the actual payloads and timestamps. The same storage boundary applies: the records support a classroom review, and no external customer service workflow is triggered.

### 00:05:03.078 — Change one prompt condition at a time.

I switch to direct output, zero solved task examples, and in-message instruction placement to demonstrate the alternate controls. The experiment runner isolates these factors in separate variants. A fixed protocol example stays in both example conditions. The role comparison moves the experimental instruction block while essential business and protocol boundaries remain in the system message.

### 00:05:30.691 — The ReAct loop is assembled manually.

The implementation creates model, parse, action, recover, and finish nodes in a LangGraph StateGraph. The parser selects an action, recovery, or final path. Action observations feed back into the model node. A configured call bound prevents an endless loop. This graph uses the project’s own parser and registry rather than a prebuilt agent executor.

### 00:05:58.039 — Detailed instructions and a worked protocol example.

The C4 system separates the chosen persona from detailed operating rules and the JSON action protocol. Its instructions cover grounded facts, missing information, customer permission, tool failures, and final response behavior. A minimal worked protocol example is included. Few-shot mode adds solved tool-use demonstrations. Invalid model outputs are handled by the recovery path and remain visible in the trace.

### 00:06:28.640 — 224 checks, with the evidence mode kept explicit.

The saved experiment matrix covers sixteen variants, seven cases, and two repeats, for two hundred twenty-four deterministic runs. Expected tool observations and completed responses are recorded for all runs, with zero tool errors. Raw traces, metrics, and comparison reports are included. These results check mechanics; they do not measure live-model creativity, naturalness, or prompt quality.

### 00:06:59.038 — Reflection answers five assignment questions.

The reflection document addresses persona helpfulness, prompt and configuration performance, tool reasoning, instruction effects, and implementation challenges. The notebook includes the reflection content as well. It separates design rationale from measured results and does not invent a live-model winner. After real API experiments, add measured findings and human ratings to support the final comparison.

### 00:07:27.716 — Run the lab and reproduce the checks.

C4 launches with the same environment setup, normally on port 7861. The behavioral suite passes twenty-three tests, including parsing, tools, failures, persistence, and loop bounds. To evaluate real model behavior, configure the private key and run the live experiment command. Review raw outputs, complete human ratings, and preserve the run mode and model configuration with every result.

### 00:08:00.128 — Everything needed to review both projects.

The repository contains two separate project folders, executable notebooks, business sources, READMEs, requirements, tests, and experiment artifacts. C4 also includes its five-question reflection. Use the chapter videos to review functionality, and run the notebooks to inspect the implementation. This edited walkthrough documents actual offline actions; a live API run and measured C4 comparisons remain the final evidence to add.
