# Knowledge base

Runbooks and incident evidence for the OpenTelemetry demo app.

Rules:
- Public data only. Nothing from an employer or private system.
- Every file is listed below with its source and who wrote it.
- File name (without extension) is the evidence id used in `data/questions.json`.

| File | Source | Written by |
|------|--------|------------|
| rb-payment-unreachable.md | OpenTelemetry demo feature flag `paymentUnreachable` (https://opentelemetry.io/docs/demo/feature-flags/) | AI-drafted; Jessieca review/edit pending |
| rb-payment-failure.md | OpenTelemetry demo feature flag `paymentFailure` (https://opentelemetry.io/docs/demo/feature-flags/) | AI-drafted; Jessieca review/edit pending |
| rb-kafka-queue-lag.md | OpenTelemetry demo feature flag `kafkaQueueProblems` (https://opentelemetry.io/docs/demo/feature-flags/) | AI-drafted; Jessieca review/edit pending |
| rb-recommendation-cache-leak.md | OpenTelemetry demo feature flag `recommendationCacheFailure` (https://opentelemetry.io/docs/demo/feature-flags/recommendation-cache/) | AI-drafted; Jessieca review/edit pending |

## Notes

- These runbooks explain possible demo failures. They are not measured facts from a particular run.
- Incident evidence files (flag state, metrics, trace ids, sanitized log excerpts) must come from real demo runs. Never invent measurements. Still to collect.
- After review, update authorship to: `Drafted with AI; reviewed and edited by Jessieca`. Do not claim review before it has happened.
