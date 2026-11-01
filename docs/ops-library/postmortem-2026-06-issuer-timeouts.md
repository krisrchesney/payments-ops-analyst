# Postmortem: issuer timeouts first read as fraud (2026-06-18)

*Synthetic document. Owner: Payments Operations. A past incident, kept for learning.*

## Summary
On 2026-06-18, Thomas Financial's authorization host slowed for about 2 hours. Many of its responses timed out and were declined with code 91. A second share of its declines came back as code 05. The first responder assumed a fraud attack, which delayed the right fix by about 40 minutes.

## What happened
- 10:10 UTC: Thomas Financial code 91 declines rose to about 9 times normal.
- 10:25 UTC: on-call saw code 05 also rising and escalated to Fraud Strategy.
- 11:05 UTC: Issuer Relations reached the issuer, who confirmed a host problem.
- 12:05 UTC: the issuer recovered.

## What went wrong
- We looked at code 05 first and missed that code 91, the clearer signal, was concentrated at one issuer.
- No one checked issuer status notices or contacted the issuer early.

## Lessons
- A spike at **one issuer** points to the issuer, not to fraud. Follow the issuer-down runbook.
- Check code 91 by issuer first.
