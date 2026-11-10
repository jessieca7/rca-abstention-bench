# Pilot data

**Everything in this folder is constructed, not captured.** The incident logs
were written by hand from the *documented* behavior of two OpenTelemetry demo
feature flags (`paymentUnreachable`, `paymentFailure`). Error wording is
illustrative. A live capture of the demo was attempted but not completed in time.
`scripts/capture_evidence.py` can produce real captures to replace these files.

- `incident_a.log`, `incident_b.log`: the evidence for two incidents.
- `incidents.json`: alert text, the true root cause, and the scoring key per incident.
- `questions.json`: 12 questions. `n1`-`n6` are normal. `i1`-`i6` are the same
  questions with one attacker-written log line inserted (the `injection` field
  says where, what it says, and which action it tries to trigger).
- No GE Vernova data or details are used anywhere.
