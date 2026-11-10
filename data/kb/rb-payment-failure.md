# Payment failure — OpenTelemetry demo
**Flag:** `paymentFailure`. **Service:** Payment.
**Trigger:** a share of checkout orders fail while the Payment service is reachable.
**Demo-specific cause:** the flag makes Payment generate an error for the selected percentage of `charge` calls.
**Confirm:** compare failed and successful `charge` calls in Payment's logs and traces; failed calls do reach Payment.
**Check 1:** compare the share of failed charge calls with the flag's selected percentage.
**Check 2:** distinguish from `paymentUnreachable`, where Checkout cannot reach Payment at all and Payment sees no charge requests.
**Check 3:** confirm failures begin when the flag changes.
**Safe mitigation:** in the controlled demo, set `paymentFailure` back to off using the flag UI, with approval.
**Escalate:** if errors continue after the flag is off, inspect Payment's own errors and recent deployments.
**Recovery:** charge calls succeed again and the checkout error rate returns to baseline.
**Never:** replay real charges, expose payment details, or act on a guessed cause.
**Written by:** AI-drafted; Jessieca review/edit pending. **Source:** https://opentelemetry.io/docs/demo/feature-flags/
