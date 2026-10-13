# C4 completion status

## Completed implementation and mechanical evidence

- Explicit use-case summary: goal, audience, tools and boundaries.
- Manual LangGraph action/observation/final workflow.
- Three personas with task, wording, matching settings and rationale.
- Dedicated full instructions split into one purpose per numbered rule.
- Dedicated compact instructions and a worked protocol example.
- Direct/brief-plan, zero/few-shot, instruction-role/detail and generation variants.
- Experiment logging and comparison reports.
- Five-question reflection included in the executable notebook.
- 23 behavioral tests and a 224-run deterministic demonstration matrix.

## Live evidence still required

Live API access is not yet available at this preparation step. No live experiment or model-quality finding is claimed. The agent supports OpenAI live mode, but an offline simulation cannot establish prompt/configuration performance.

After a private key is configured:

1. Verify a short live task and a real action/observation cycle.
2. Run the comparison matrix with the same task cases and repeats.
3. Preserve raw replies, tool observations, model/settings, timings and failures.
4. Rate factuality, usefulness, naturalness, persona fit and creativity. Assistant-reviewed ratings must be labeled as such and should be reviewed by the student; they are not independent human-study evidence.
5. Summarize per-task results and update reflection questions 1-4 with measured findings.
6. Re-execute the notebook and add a short live demonstration clip.

`top_k` is rejected by the selected adapter and documented as not applicable. Brief-plan is a concise, observable action rationale rather than hidden chain-of-thought. Alternate-model comparisons are supported but need actual accessible models and runs.

Never include `.env`, real credentials, runtime databases or real customer data in the submission.
