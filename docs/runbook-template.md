# Runbook template

Copy this file into data/kb/ and rename it, e.g. rb-payment-unreachable.md.
The file name (without .md) is its evidence id. Write short, plain sentences.
Source for facts: https://opentelemetry.io/docs/demo/feature-flags/

---

# <Title: the problem in a few words>

## Symptoms
What a person sees. (e.g. "Checkout fails", "orders are delayed")

## Services involved
Which services are affected? (e.g. checkout, payment)

## What to check
1. First thing to look at (a log line, a metric, a dashboard)
2. Second thing
3. Third thing

## Likely root cause
The usual reason, in one or two sentences.

## Fix
What to do to resolve it.

## Source
Where the facts came from (a link) and who wrote this page.
