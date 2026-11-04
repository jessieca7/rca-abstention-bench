# Kafka queue problems — OpenTelemetry demo
**Flag:** `kafkaQueueProblems` (older alias: `kafka-queue-lag`; not the actual flag key).
**Services:** Checkout produces order events; Fraud Detection consumes them.
**Trigger:** fraud-detection consumer lag increases while checkout continues producing messages.
**Demo-specific cause:** the flag makes Fraud Detection **sleep a configured N milliseconds per record**, slowing consumption below production rate.
**Confirm:** inspect enabled flag and its per-record delay; compare order-production rate, fraud-consumption rate, and lag over time.
**Check 1:** examine Kafka consumer group lag by partition and confirm the fraud-detection consumer is still polling.
**Check 2:** check processing duration and throughput in traces/metrics; look for elevated per-message handling time without equivalent broker failure.
**Check 3:** distinguish from `kafkaConsumerDead`, where Fraud Detection stops polling and leaves the group entirely.
**Read-only check:** `kafka-consumer-groups.sh --bootstrap-server <broker> --describe --group <group>` (values: check).
**Safe mitigation:** in the controlled demo, reduce the injected delay or disable `kafkaQueueProblems`; confirm with the experiment owner.
**Escalate:** if lag persists after the flag is disabled, inspect consumer errors, group health, and underlying Kafka conditions.
**Recovery:** lag declines, consumer processing catches up, and end-to-end order-event delay returns toward baseline.
**Never:** reset offsets, delete topics, or skip orders to make the lag graph look healthy.
**Evidence needed for benchmark:** flag variant/delay + before/after lag and consumer-processing samples (not yet collected).
**Written by:** AI-drafted; Jessieca review/edit pending. **Source:** https://opentelemetry.io/docs/demo/feature-flags/ ; https://opentelemetry.io/docs/specs/semconv/messaging/messaging-metrics/
