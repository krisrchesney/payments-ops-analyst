# Escalation guide

*Synthetic document. Owner: Payments Operations. Team names only; no individual contacts.*

## Severity levels
- **Sev 1:** approval rate down more than 2 points for a region or a top-20 merchant for 30 minutes or more, or authorizations failing outright. Page on-call now.
- **Sev 2:** a clear spike in one decline code, issuer or region with measurable lost approvals. Raise it within 1 hour.
- **Sev 3:** small or short movements. Note them in the daily ops note.

## Who owns what
- **Issuer Relations:** issuer outages, maintenance and stand-in setup.
- **Platform Engineering:** gateways, latency, network links and database changes.
- **Fraud Strategy:** fraud rules, models and code 59 behavior.
- **Merchant Support:** telling affected merchants and collecting complaints.

## What to include when you escalate
- When it started and whether it's still going.
- Which region, issuer, merchant category or channel is affected.
- The numbers: affected authorizations, extra declines and the approval rate change.
- Any matching change or notice you found.
