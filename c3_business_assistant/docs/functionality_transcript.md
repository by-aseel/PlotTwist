# PlotTwist C3 — functionality walkthrough

Duration: 441.9 seconds. English narration uses the installed Microsoft Zira Desktop voice.

This is an **edited screenshot walkthrough of actual UI interactions**, with readable source and captured trace explanations. It is not a continuous screen recording. The local apps were run in explicit offline demo mode; the public Space is the Static JavaScript demo. No live OpenAI API call is shown. Only synthetic customer details are used.

### 00:00:00.000 — Make a memory. Leave a mystery.

Welcome to PlotTwist, a fictional mystery experience business. This is the C3 business assistant walkthrough. It shows the working interface, message routing, memory, local tools, and reflection. The captured conversations use offline demo mode. Real OpenAI integration is implemented in the code, but no live API call is shown in this video.

### 00:00:28.033 — One business. Four ways into the story.

The business offers Birthday Mystery Nights, City Quests, Corporate Missions, and Custom Story Adventures. Package details come from the text summary and four-page PDF dossier. Prices are illustrative starting prices per group. Behind the Plot introduces Aseel, Noah, Jiso, and Felix, and provides the business PDF for download.

### 00:00:53.351 — Persona gives the voice. Instructions give the rules.

The persona and operating instructions are clearly separated in prompts dot py and in the notebook. Clue sounds warm and curious. The instructions require grounded answers, missing-field collection, honest handling of unknowns, and acknowledgement only after successful tool results. These two labeled blocks are assembled with the business knowledge into the system prompt.

### 00:01:19.215 — Classify first. Then choose the handling path.

Before answering, the agent classifies the incoming message into general question, lead collection, or feedback and unanswered question. This implementation uses lightweight heuristics and recent conversation context. The latest activity panel exposes the route. Because the router is heuristic, unfamiliar wording can fall into the unanswered path; live model quality still needs separate evaluation.

### 00:01:47.767 — A general question, answered from known facts.

I ask, What adventures do you offer? Clue describes the four experiences and their known limits and starting prices. The activity shows general question. The knowledge trace identifies the text summary and PDF as loaded sources. The answer invites a useful next step without inventing availability or confirming a booking.

### 00:02:12.045 — The enquiry begins with the event brief.

Next, I request contact about a birthday mystery for ten people. The route changes to lead collection. Clue asks for the missing name and email address while keeping the event brief from the previous turn. This demonstrates short-term conversational memory: the customer does not need to repeat all of the event details.

### 00:02:34.714 — The next message completes the enquiry.

I supply the fictional name Sam Rivera, the example email address, and permission to save the enquiry. The agent combines these details with the earlier event request. The customer interest tool writes an actual local record. Only after its successful result does Clue confirm that the enquiry was saved.

### 00:02:57.028 — Tool contract → validated arguments → saved record.

The required function is record customer interest, with email, name, and message parameters. Its documented schema rejects extra fields, and the implementation validates the supplied details. Here is the captured tool result from this run: success is true, the kind is lead, and the status is saved. Local logging also prints the tool event.

### 00:03:22.852 — Feedback has its own handling path.

I report that the instructions at the start of the mystery felt rushed. The router selects feedback and unanswered question. The second required function, record feedback, receives the question text and saves it locally. The visible arguments and returned record show that this is a real persistence action, even though the demo reply is scripted.

### 00:03:46.750 — An unknown policy is logged, without a guess.

I ask about the cancellation policy. That policy is absent from the business profile. Clue admits the information gap and records the unanswered question through the feedback tool. It does not manufacture terms or promise that somebody received a message. The record is available for local review in the casebook.

### 00:04:09.769 — Reflection makes the draft and final reply visible.

Reflection is enabled before the final reply. This captured audit shows the original draft, revised reply, checks, and a changed flag. The draft already passed, so changed is false. Offline mode uses a deterministic guardrail audit. Live mode uses a second model request to review and revise the draft when necessary; the code logs both versions.

### 00:04:37.537 — The casebook turns actions into inspectable records.

The casebook contains the lead, feedback, and unanswered question from this browser session. Refresh retrieves only this session’s records. Export creates a JSON file that can be downloaded and checked. SQLite provides local persistence. Starting a new browser session changes the visible casebook while earlier records remain in the local database.

### 00:05:03.625 — How the live model and tool round trip work.

The live adapter passes the system prompt, current route, chat history, user message, and tool schemas to OpenAI Chat Completions. A model tool request is executed by the validated registry. Its result is appended with the matching tool call identifier and returned to the model. If no tool is requested, the generated text becomes the draft reply.

### 00:05:30.023 — The notebook and Gradio demo are included.

The main notebook contains readable persona, instructions, schemas, and agent implementation cells. It reconstructs the supporting files in a separate notebook workspace. The launch section creates the designed Gradio interface. Set Run UI to true after running the earlier cells. The folder version also launches directly from app dot py.

### 00:05:55.506 — The free hosted edition is available now.

This public Hugging Face Space is running the free Static edition. I enter a business question and receive a response. It includes browser-based routing, local records, and a rule-based reflection check. This free edition uses JavaScript and scripted replies; it does not host the full Python agent, Gradio backend, or live OpenAI calls.

### 00:06:20.415 — Run it. Test it. Keep the run mode visible.

To try C3 locally, create a virtual environment, install the requirements, and launch app dot py in demo mode. The default address uses port 7860. For live mode, privately configure your API key in the local environment file and change the mode. Fifteen behavioral tests pass, including controlled model tool-round-trip and reflection checks. These tests do not measure live model quality.

### 00:06:52.347 — C3 submission: repository plus a functionality video.

C3 is submitted as a GitHub repository and a functionality video. Include the notebook, business sources, requirements, README, and working code. This walkthrough documents the offline functionality and explains the implemented live path. Before presenting real model behavior as tested, configure the key and record a live run. The Static Space supplements the project; it does not replace the full agent.
