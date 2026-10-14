# Manual LangGraph ReAct workflow

The same graph runs the Gemini, real local Ollama and deterministic demonstration modes. Providers supply model text; the application owns action parsing, tool execution, observations, recovery and finalization. No prebuilt executor is used.

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	model(model)
	parse(parse)
	action(action)
	recover(recover)
	finish(finish)
	__end__([<p>__end__</p>]):::last
	__start__ --> model;
	action --> model;
	model --> parse;
	parse -.-> action;
	parse -.-> finish;
	parse -.-> recover;
	recover --> model;
	finish --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```
