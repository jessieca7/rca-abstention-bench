# Abstention Benchmark for RCA Agents

When the runbooks and telemetry an RCA (root-cause-analysis) agent retrieves are
not enough to find the cause, does it say "I can't tell", or does it guess?
Which design reduces made-up root causes: prompting, a retrieval-confidence
cutoff, a deterministic rule gate, or self-consistency?

**Status:** work in progress. Results will be added after the evaluation runs.

## Layout

- `data/kb/` — runbooks and incident evidence (OpenTelemetry demo app, public data)
- `data/questions.json` — labeled answerable and unanswerable questions
- `src/rca_abstention_bench/` — config, LLM client, schema; later retriever, agent designs, metrics
- `scripts/` — runnable helper scripts
- `tests/` — tests (`uv run pytest`)

## Run

```bash
ollama serve &              # local model server
uv run python scripts/hello_llm.py
uv run pytest
```

Builds on UAEval4RAG, AbstentionBench and ORCA-bench. Details will be in `docs/related-work.md`.
