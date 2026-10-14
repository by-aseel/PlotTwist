> Historical offline evidence, prepared before the actual local model study. The current measured results are in `evaluation_report.md` and `reflection.md`.

# C4 reflection / PlotTwist evaluation

This reflection draws on the 14 October 2026 offline evaluation: 238 runs over seven fictional scenarios and 17 conditions, plus 29 C4 behavior/transport tests. The deterministic model exercised the real LangGraph and local tools. An assistant reviewed 21 distinct persona/case replies. Gemini generation was blocked by project access denial, so the findings below describe implemented workflow behavior and reviewed demonstration styles. [Full evaluation report](evaluation_report.md).

## 1. Which persona gave the most helpful or natural results?

**Clue was my preferred general concierge design.** In the eight-guest birthday example, it gave the correct USD 240 starting price and two-hour duration, then asked for the date and atmosphere. This was a useful, approachable next step. Its repeated branded opening still made some replies sound formulaic.

**Cipher was more useful for operational planning.** In the corporate-budget case, it preserved the USD 650 starting price, identified that USD 500 was insufficient, and asked about the final budget, venue, date and access needs. Its constraint checklist suited the task better than a story hook.

**Muse was strongest for the creative demonstration.** For 14 time-travel fans, it offered The Tomorrow Heist, a timeline puzzle and a shared finale, while clearly labeling the concept and keeping custom scope quote-only. Its story-title prefix was awkward for enquiry confirmation and accessibility questions. The most helpful persona therefore depended on the task. These judgments concern the inspected offline replies, rather than sampled Gemini performance.

## 2. Which prompt and configuration combination performed best?

All 17 conditions completed all 14 assigned runs with the expected tools and zero tool failures. The deterministic policy produced identical final replies when temperature, top-p, top-k, penalties, output cap, examples, role or instruction detail changed. There was therefore **no measured generation-configuration winner**.

For a course demonstration, I selected **Clue with full system instructions, few-shot task examples and a brief visible plan**. This is a presentation and inspectability choice: full instructions state the boundaries, examples make the action format understandable, and the brief-plan condition added 18 verifiable next-action notes across its two repeats. The extra notes did not improve the final answers in this matrix.

The intended persona defaults remain Clue temperature 0.45/output cap 700, Cipher 0.10/850 and Muse 0.85/1000. Top-p 1 and top-k 40 are held steady; the separate top-k variant uses 20. These controls are validated and their native Gemini forwarding is tested. Their intended effect on model variation remains a hypothesis, and Google recommends default sampling for Gemini 3.

## 3. How well did the agent reason and use tools?

The agent completed 238 bounded action cycles and executed 306 local tool calls: 136 searches, 102 estimates, 34 enquiry saves and 34 feedback records. Birthday, corporate and custom-story requests used search -> estimate -> final. Unknown access/venue questions logged feedback and kept the answer unverified. Enquiry confirmations followed successful storage observations and made no email or booking promise.

The controlled-response tests also demonstrated malformed-action recovery, rejected fabricated contacts, cancellation, session isolation and explicit failures. This provides good evidence for the implemented action/observation pipeline. It does not measure an LLM's internal reasoning or reliability on new requests. Brief-plan notes explain the next action without exposing private chain-of-thought.

## 4. Did the instructions block change behavior noticeably? How?

The full and compact variants produced the same final replies and tool paths in this run. I cannot attribute a behavioral improvement to the longer prompt because the deterministic model uses its coded policy. What changed was the message content: the full block makes each input, output, grounding, contact, unknown-question and error-handling rule explicit, with a worked protocol example.

Application validation made the boundaries observable in tests. A fabricated email was rejected before storage; explicit refusal to save prevented an enquiry write; and an error observation could return to the next step. These are enforcement-layer effects, rather than proof that prompt wording alone caused safer behavior.

Zero-shot omitted solved task demonstrations while keeping the common protocol example. Few-shot added two solved tasks. The placement comparison moved the persona and instructions as a unit and retained fixed business facts in the system context. This kept the comparisons well defined.

## 5. What were the biggest implementation challenges?

**Reliable actions:** distinguishing action from final, validating tool names and arguments, returning observations and bounding recovery required explicit graph nodes rather than a prebuilt executor.

**Factual creativity:** Muse needed room for story concepts while prices, availability, accessibility and reservations remained grounded. The reviewed time-travel answer achieved this separation, although its title was overused on unrelated requests.

**Fair comparisons:** persona bundles change wording, task and defaults together. Prompt-only persona arms isolate wording from configuration; single-factor arms isolate each setting. The deterministic outputs demonstrated wiring but could not reveal sampling effects.

**Metrics that miss quality:** every tool check passed, yet the oversized birthday reply omitted the exact 6-20 capacity. Reviewing actual replies exposed limitations that a completion percentage would hide.

**Service access and packaging:** Gemini returned 403 project access denial, so no live model findings were available. The project still provides a working no-cost offline demonstration, executed notebook, test suite, raw evidence and reproducible comparison. Credentials, databases and private account-support records remain outside the submitted repository.

The resulting design uses Clue for discovery, Cipher for logistics and Muse for requested story concepts. Future model-quality conclusions require successful generated replies and ratings under the same benchmark.
