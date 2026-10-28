# Backlog (to enter in Jira)

*Starter backlog. Reword, split or reorder as Product Owner. The S1 to S4 tag is the proposed sprint; it matches Sprints 1 to 4 of the learning plan. Put it in Jira's Labels field.*

*Only the current sprint's stories go into a Jira sprint. Everything else waits in the Backlog section until that sprint's planning.*

## Epic 1: Data foundation
- **S1** As a data engineer, I can land synthetic authorizations, chargebacks, merchants and issuers in a Databricks volume so the pipeline has a stable source.
  - AC: files in `/Volumes/workspace/payments/landing/`; row counts match the generator output.
- **S2** As a data engineer, new files in the landing volume are loaded into bronze tables automatically, with where and when each row arrived. *(PAYOPS-24, added after Sprint 1)*
  - AC: four bronze tables (authorizations, chargebacks, merchants, issuers); row counts match landing (2,000,000 / 7,497 / 800 / 40); each row has `_ingested_at` and `_source_file`.
- **S2** As an ops analyst, I can trust that the cleaned authorization table (silver layer) has no duplicates or invalid codes.
  - AC: expectations on amount, response code, merchant; dropped-row counts visible in the pipeline UI.
- **S2** As an ops analyst, I can see daily approval rate by region, channel and tokenization.
  - AC: `gold_daily_approval` matches a hand-written SQL check for two sample days.
- **S2** As an ops analyst, I can see decline reasons by issuer and region.
  - AC: `gold_decline_reasons` shares add up to 100% per day and region.
- **S2** As an ops analyst, I can see p50, p95 and p99 latency by hour and region.
  - AC: `gold_latency_hourly` exists; the UK latency spike (INC-2) is visible in it.
- **S2** As an ops manager, I can see weekly chargebacks by merchant category and reason.
  - AC: `gold_chargebacks_weekly` totals match the chargebacks source count.

## Epic 2: Ops assistant
- **S3** As an ops analyst, I can ask Claude "why did approvals drop in region X on date Y" and get the top drivers with the numbers used.
  - AC: the MCP tools `query_gold` and `compare_periods` return results; the answer cites the table and values.
- **S3** As an ops manager, I get a drafted daily ops note.
  - AC: the note lists the day's approval rate, top 3 decline reasons and any latency spike, each with its number.
- **S4** As the product owner, I can run an evaluation that checks the assistant against the three injected incidents.
  - AC: one question per incident, 3 runs each, pass or fail recorded in `docs/eval.md`.

## Epic 3: Launch
- **S4** As a hiring manager, I can understand the project in two minutes from the README and a recording.
  - AC: README has architecture, results and next steps; a 2-minute recording is linked.
- **S4** As the product owner, I publish release notes for R1, R2 and R3.
  - AC: `docs/product/releases.md` lists what shipped in each release.
- **S4** As the product owner, I write a one-page operational reports product brief with a pricing hypothesis.
  - AC: one page; states the customer, the problem, the offer and a pricing model with reasoning.
