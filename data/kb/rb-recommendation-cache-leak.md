# Recommendation cache failure — OpenTelemetry demo
**Flag:** `recommendationCacheFailure` (older alias: `recommendation-cache-leak`; not the actual flag key).
**Service:** Recommendation; **Trigger:** rising memory use and intermittent latency/error spikes.
**Demo-specific cause:** an **exponentially growing application cache** leaks memory; roughly half of requests cause growth.
**Confirm:** enable/inspect flag; allow enough traffic for a trend (the demo walkthrough suggests about 10 minutes).
**Check 1:** view Recommendation CPU and memory, request latency (especially p95/p99), and error rate over the same period.
**Check 2:** search slow Jaeger traces involving Recommendation; inspect the waterfall for time spent in this service.
**Check 3:** compare trace attribute `app.cache_hit=true` vs. `false`; check whether `app.products.count` becomes unusually high.
**Diagnosis:** growing memory plus a very high product count and slower cache misses supports the documented demo cache leak.
**Safe mitigation:** in the controlled demo, disable `recommendationCacheFailure` after collecting evidence; observe recovery.
**Escalate:** if memory or latency remains elevated, examine Recommendation application state and instance restarts with its owner.
**Recovery:** memory stops growing abnormally and latency/errors return toward pre-fault levels after a controlled reset (check).
**Never:** assume Redis, run `FLUSHALL`, or claim a specific heap/storage cause without supporting evidence.
**Evidence needed for benchmark:** flag state + memory trend + slow trace with `app.cache_hit` and `app.products.count` (not yet collected).
**Written by:** AI-drafted; Jessieca review/edit pending. **Status:** public demo guidance, not incident evidence.
**Source:** https://opentelemetry.io/docs/demo/feature-flags/recommendation-cache/ ; https://opentelemetry.io/docs/demo/feature-flags/
