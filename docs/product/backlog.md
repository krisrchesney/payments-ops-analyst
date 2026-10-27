# Backlog (to enter in Jira)

*Starter backlog. Reword, split or reorder as Product Owner. S1, S2, S3 is the proposed sprint.*

## Epic 1: Data foundation
- **S1** As a data engineer, I can land synthetic authorizations, chargebacks, merchants and issuers in a Databricks volume so the pipeline has a stable source.
  - AC: files in `/Volumes/workspace/payments/landing/`; row counts match the generator output.
- **S1** As an ops analyst, I can trust that silver authorizations have no duplicates or invalid codes.
  - AC: expectations on amount, response code, merchant; dropped-row counts visible in the pipeline UI.
- **S2** As an ops analyst, I can see daily approval rate by region, channel and tokenization.
  - AC: `gold_daily_approval` matches a hand-written SQL check for two sample days.
- **S2** As an ops analyst, I can see decline reasons by issuer and region.
- **S2** As an ops analyst, I can see p50, p95 and p99 latency by hour and region.
- **S2** As an ops manager, I can see weekly chargebacks by merchant category and reason.

## Epic 2: Ops assistant
- **S3** As an ops analyst, I can ask Claude "why did approvals drop in region X on date Y" and get the top drivers with the numbers used.
  - AC: the MCP tools `query_gold` and `compare_periods` return results; the answer cites the table and values.
- **S3** As the product owner, I can run an evaluation that checks the assistant against the three injected incidents.
  - AC: a script asks one question per incident and records pass or fail; results saved in the repo.
- **S3** As an ops manager, I get a drafted daily ops note.

## Epic 3: Launch
- As a hiring manager, I can understand the project in two minutes from the README and a recording.
- As the product owner, I publish release notes for R1, R2 and R3.
- As the product owner, I write a one-page operational reports product brief with a pricing hypothesis.
