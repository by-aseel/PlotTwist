# Real model generation without a paid API

C4 supports a **local** mode using Ollama and the existing custom LangGraph ReAct graph. Ollama serves the language model; LangGraph remains the single agent framework. The assignment allows a model choice and requires varying configurations, so this path can produce actual LLM evidence without Gemini access or paid generation.

## Setup

Install Ollama from its official source, then download the models:

```powershell
ollama pull qwen2.5:3b
ollama pull qwen2.5:1.5b
```

Keep `ollama serve` running if your installation does not start it automatically. Default endpoint: `http://127.0.0.1:11434`. This project's adapter accepts loopback endpoints only. Model weights are downloaded once; local generation requires no API key or paid account. Local compute, disk space and initial downloads are still required.

From the C4 project folder:

```powershell
python app.py --mode local
```

The UI explicitly displays **LOCAL AI / OLLAMA** and the actual model responses. Set `OLLAMA_MODEL=qwen2.5:3b` in your private `.env` to choose the interactive model. Gemini live mode and the deterministic demo remain available as separate choices.

## Controlled comparison

```powershell
python experiments.py --mode local --model qwen2.5:3b --repeats 2 --output experiments/local
python experiments.py --mode local --model qwen2.5:3b --compare-model qwen2.5:1.5b --variants alternate_model --repeats 2 --output experiments/local-alternate
```

Together these request 252 runs: 17 primary configurations × seven scenarios × two repeats, followed by 14 alternate-model runs with the same baseline settings and paired seeds. Model comparison runs form a separate batch to avoid repeated model loading on a 6 GB GPU. This means latency is subject to order/cache effects; compare native load and generation metrics too. An individual run may use multiple model calls. Add `--resume` to the identical command after an interruption. Existing failed attempts are retained; retry them in a separate output folder if needed. A single shuffled 252-run design is also available by supplying `--compare-model` without filtering variants in the first command.

The model receives the actual system prompt, persona, instructions, history, current request and four native function definitions. Ollama returns a model-selected function call or final text. The thin adapter serializes the call or text into the existing JSON protocol. The application parses that action, validates and executes the real tool, returns its observation, and asks the model for the next step. On the next native request, serialized actions become assistant tool calls and observations become tool messages. This is the same manual graph used for Gemini; no prebuilt executor or scripted reply substitution is involved. Saved `raw_output` entries are this canonical protocol representation; final wording and function arguments are preserved.

| Course setting | Native Ollama option |
|---|---|
| temperature | temperature |
| top-p | top_p |
| top-k | top_k |
| frequency penalty | frequency_penalty |
| presence penalty | presence_penalty |
| max tokens | num_predict |
| model type | model |

Context length is held at 8192; repeat penalty at 1; min-p at 0. Generation seeds are paired by repetition (shuffle seed + repeat). The brief-plan arm requests a short visible next-action plan, not private reasoning. Token counts, stop reason and timing metadata are logged alongside the canonical responses and tool observations. Quantized model and runtime versions accompany the results. Qwen3 preflight attempted both the native `think=false` flag and `/no_think`; it did not reliably obey the output protocol in this runtime. Responses containing thinking tags are rejected without publishing private reasoning. Qwen3 is not the default evaluation or interactive model.

Read the generated replies and traces before declaring a winner. Mechanical completion alone does not prove grounding or helpfulness. Local model speed depends on hardware and loading time; the request metadata distinguishes loading from generation durations.

## Official references

- [Windows runtime and portable CLI](https://docs.ollama.com/windows)
- [Native chat API](https://docs.ollama.com/api/chat)
- [Generation parameter reference](https://docs.ollama.com/modelfile)
- [Native presence/frequency options](https://github.com/ollama/ollama/blob/v0.40.4/api/types.go)
- [Native tool-call and tool-observation protocol](https://docs.ollama.com/capabilities/tool-calling)
- [Qwen thinking-mode switches](https://qwenlm.github.io/blog/qwen3/)
- [Qwen3 4B](https://ollama.com/library/qwen3:4b)
- [Qwen2.5 3B](https://ollama.com/library/qwen2.5:3b)
- [Qwen2.5 1.5B](https://ollama.com/library/qwen2.5:1.5b)
