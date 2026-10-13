# Gemini migration and rerun instructions

The projects use `google-genai==1.66.0` with Pydantic 2.12.3, compatible with the pinned Gradio 5.50.0. Each project remains standalone. No OpenAI client or API key is required.

## Configuration

Create a key in https://aistudio.google.com/api-keys and keep it in local `.env`:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_REQUEST_INTERVAL=4
```

The interval is request pacing, not a claim about your quota. Check actual limits in AI Studio. Free-tier access and availability are account-specific; this project never enables billing. Use only fictional enquiry data for shared evaluations.

## What changed

- C3 converts system instructions, user input, short-term history and tool declarations into native Gemini requests. Its local loop validates model function calls and returns matching native function responses. Candidate content is preserved, including any required signatures. SDK automatic execution is disabled.
- C3 reflection uses a second Gemini JSON response and retains the original/revised answer. Errors remain visible, with no demo substitution.
- C4 uses native generation inside its existing custom LangGraph ReAct graph. JSON actions are parsed and executed locally, then observations return to the next model call.
- Persona controls include temperature, top-p, top-k, frequency/presence penalties and output cap. Gemini 2.5 is the intended sampling-study family when accessible. Google discourages sampling changes for Gemini 3; disclose this if using Gemini 3. Minimal thinking is selected for interactive Gemini 3 requests, and private reasoning is not displayed.
- Each API request has a timeout and no hidden retries. Safe errors expose status codes, never credentials or headers. The experiment runner checkpoints and stops on systemic access/quota errors.

## Live attempts and remaining work

On 14 October 2026 model listing succeeded, but generation did not: Gemini 2.5 Flash-Lite returned 404 (unavailable to new users); the replacement Gemini 3.5 Flash-Lite and other tested Gemini 3 models returned 403 (project denied access). There is no successful live comparison evidence. Resolve the denial in Google AI Studio / Google support before further generation attempts. Waiting for quota reset does not fix a 403 access denial.

After access is restored:

```powershell
python app.py --mode live
```

C4 sampling matrix, only if both 2.5 models are accessible:

```powershell
python experiments.py --mode live --model gemini-2.5-flash-lite --compare-model gemini-2.5-flash --repeats 2 --output experiments/live-full
```

This requests 252 cases: 18 variants × 7 cases × 2 repeats; each case may need multiple model calls. For a checkpoint interrupted by network/quota, rerun the identical command with `--resume`. A failed attempt stays recorded; rerun failed cases in a new output folder after fixing access. The human-rating sheet is intentionally unfilled until successful answers exist. Read the raw traces, rate each criterion, and update the five reflection answers with actual observations.

## Bonus scope

C3 reflection and its visible draft/revision logs are implemented. The free public Hugging Face Space remains a Static browser demonstration. It does not run Python, Gradio or Gemini and cannot be described as the full backend deployment bonus. The Gradio deployment package is updated for Gemini and ready for an account with hosting access; set GEMINI_API_KEY as a private Space secret.

## Official references

- [Google Gen AI SDK](https://ai.google.dev/gemini-api/docs/libraries)
- [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Generation configuration](https://ai.google.dev/api/generate-content)
- [Gemini 3.5 parameter guidance](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.5)
