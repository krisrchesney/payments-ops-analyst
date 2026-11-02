# Ops library (synthetic)

These are made-up operations documents for a fictional payment processor. They exist so the agent has something to search (RAG, Jira epic PAYOPS-49). No real company, rule, system or person is described.

Each `##` heading is one searchable section. The pipeline splits files at those headings into the `docs_chunks` table.

| File | What it is |
|---|---|
| `fraud-rule-change-log.md` | Every fraud-rule change: when, what, why, rollback |
| `platform-change-log.md` | Infrastructure and network changes by region |
| `issuer-status-notices.md` | Outage and maintenance notices received from issuers |
| `response-code-guide.md` | What each decline code means and who owns it |
| `runbook-issuer-down.md` | What to do when one issuer's declines spike |
| `runbook-latency-spike.md` | What to do when authorization latency jumps |
| `runbook-decline-spike.md` | What to do when a decline code spikes across many issuers |
| `escalation-guide.md` | Who to contact and when |
| `postmortem-2026-06-issuer-timeouts.md` | Past incident: an issuer's timeouts misread as fraud |
| `postmortem-2026-08-airline-rule.md` | Past incident: a fraud rule blocked good airline sales |
