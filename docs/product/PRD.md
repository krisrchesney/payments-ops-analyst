# PRD: Payments Ops Analyst

*A personal project on simulated data. The users, risks and pricing below are reasoned assumptions, not research with real customers.*

## Problem
Payment operations analysts see the daily approval rate, decline mix and latency move, but finding why takes manual slicing across region, issuer, merchant category and channel. Small drops get missed, and big ones take hours to explain.

**Primary user for v1:** the ops analyst on shift. The analyst's question, "what changed, where and why?", is the hard part. The manager's daily note is built from that same answer, so serving the analyst first gives the manager what they need too.

## Users
- Ops analyst: needs to know what changed and where, fast.
- Ops manager: needs a short daily note for leadership.
- No other direct users in v1. Teams such as Fraud Strategy, Platform Engineering and Issuer Relations receive the findings through the analyst.

## Goals (v1)
1. Daily ops tables (approval rate, decline reasons, latency, chargebacks) refreshed by a pipeline with data quality checks.
2. An assistant that answers "what changed and why" questions from those tables and from searchable ops documents, citing the numbers and documents it used.
3. A drafted daily ops note the manager can edit and send.

## Non-goals (v1)
- Real-time alerting.
- Fraud scoring or changing authorization decisions.
- Real payment data (all synthetic).

## Success metrics
- The assistant finds the true cause of each injected incident (INC-1 to INC-3) from a plain-language question: target 3 of 3.
- Every number in an answer matches the gold tables: target 100%.
- Time from question to answer under 1 minute.
- The right document is in the top 3 search results for each incident: target 3 of 3.
- A daily note is good enough to send when:
  1. Every figure matches the gold tables.
  2. It names a cause only when the evidence supports one, and otherwise says the cause is unknown.
  3. It states its caveats, such as a baseline skewed by the incident itself.

## Scope by release
- **R1 (Sprints 1-2):** pipeline bronze to gold; incidents visible by hand.
- **R2 (Sprint 3):** MCP server with query tools; Claude answers questions; daily note draft.
- **R3 (Sprint 4):** runbook search (RAG), so answers can cite why a metric moved.
- **R4 (Sprint 5):** formal evaluation against incidents.json; operational reports product brief. The demo recording moved to a later date.
- **R5 (Sprint 6):** automatic detection: hourly feed, anomaly table, alert and dashboard.

## Risks
- Free Edition compute quota stops runs for the day: keep data small.
- The agent states a cause it can't support: require it to cite the table and numbers, and test this.
- A document matches by date but isn't the real cause: tell the agent to treat documents as leads and check their timing and scope against the numbers.
- Tests look better than real use, because the same author wrote the data, documents and test questions: say so in the results, and don't treat a high score as proof.
- Text inside a retrieved document tries to steer the agent: keep every tool read-only, and tell the agent to treat documents as evidence, not instructions.

## Pricing hypothesis (see the [product brief](brief.md))
If this were sold to processors, issuers or acquirers, a transaction volume tier with a minimum fee would fit best. The value comes from approvals recovered and investigation hours saved, and both grow with volume, which a per-seat price would miss because only a few analysts would use it. Payments buyers are also used to volume-based pricing. A bundle with existing reporting would make it easier to adopt, but it would hide the product's value and make it hard to justify on its own. A vendor that already sells reporting could still bundle it as a paid add-on. This is an untested assumption.
