# PRD: Payments Ops Assistant

*Draft started 2026-10-27. *

## Problem
Payment operations analysts see the daily approval rate, decline mix and latency move, but finding why takes manual slicing across region, issuer, merchant category and channel. Small drops get missed, and big ones take hours to explain.

**Q:** Who is the primary user: an ops analyst on shift, or the ops manager writing the morning summary? Pick one for v1.

## Users
- Ops analyst: needs to know what changed and where, fast.
- Ops manager: needs a short daily note for leadership.
- **Q:** Anyone else for v1?

## Goals (v1)
1. Daily ops tables (approval rate, decline reasons, latency, chargebacks) refreshed by a pipeline with data quality checks.
2. An assistant that answers "what changed and why" questions from those tables, citing the numbers it used.
3. A drafted daily ops note the manager can edit and send.

## Non-goals (v1)
- Real-time alerting.
- Fraud scoring or changing authorization decisions.
- Real payment data (all synthetic).

## Success metrics
- The assistant finds the true cause of each injected incident (INC-1 to INC-3) from a plain-language question: target 3 of 3.
- Every number in an answer matches the gold tables: target 100%.
- Time from question to answer under 1 minute.
- **Q:** What would make the daily note "good enough to send"? Define 2 or 3 checks.

## Scope by release
- **R1 (Sprints 1-2):** pipeline bronze to gold; incidents visible by hand.
- **R2 (Sprint 3):** MCP server with query tools; Claude answers questions; evaluation against incidents.json.
- **R3:** daily note draft; demo recording; operational reports product brief.

## Risks
- Free Edition compute quota stops runs for the day: keep data small.
- The agent states a cause it can't support: require it to cite the table and numbers, and test this.
- **Q:** Anything else you'd flag?

## Pricing hypothesis (for the product brief, R3)
**Q:** If this were a product sold to issuers or acquirers, would it be priced per seat, per transaction volume tier, or bundled with existing reporting? Write one paragraph with your reasoning.
