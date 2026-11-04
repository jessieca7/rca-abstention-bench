# Payment unreachable — OpenTelemetry demo
**Flag:** `paymentUnreachable` (older alias: `payment-unreachable`; not the actual flag key).
**Service:** Checkout calls Payment; **Trigger:** checkout payment calls fail or time out.
**Demo-specific cause:** enabling the flag makes Checkout use a **bad Payment service address**, rather than breaking Payment itself.
**Confirm:** check flag status/variant in the demo feature-flags UI; compare failed Checkout → Payment spans with successful baseline traces.
**Check 1:** inspect failed Checkout outbound calls for destination address, name-resolution/connection errors, and timing.
**Check 2:** compare Payment service health and inbound requests; a healthy Payment service with missing matching calls supports caller misconfiguration.
**Check 3:** confirm failures begin after the flag changes; distinguish this flag from `paymentFailure`, which injects errors inside Payment.
**Safe mitigation:** in the controlled demo, disable `paymentUnreachable` or restore the correct destination using the flag UI, with approval.
**Escalate:** if errors continue after disabling the flag, investigate Checkout service discovery/configuration and contact the service owner.
**Recovery:** observe Checkout → Payment calls succeeding again and error rate returning to baseline.
**Never:** replay real charges, expose payment details, or change live routing based only on a guessed cause.
**Evidence needed for benchmark:** flag state + one failed trace/log showing wrong destination and one healthy comparison (not yet collected).
**Written by:** AI-drafted; Jessieca review/edit pending. **Status:** public demo guidance, not incident evidence.
**Source:** https://opentelemetry.io/docs/demo/feature-flags/ ; https://opentelemetry.io/docs/specs/semconv/http/http-spans/
