# Payments Ops Analyst

A Spark pipeline on Databricks that turns synthetic card authorizations into operational reports, plus a Claude agent that explains why the numbers moved. The agent gets the numbers from the reports and the reason from a searchable library of runbooks and change logs (RAG), and it cites both.

**Personal portfolio project. All data and documents in this repo are synthetic.** The data comes from `generator/generate_auths.py`, and the documents describe a fictional payment processor. No real card, merchant, issuer or cardholder data is used, and this is not employer or production work.

**Follow the work:** [Project page](https://krisrchesney.github.io/payments-ops-analyst/) | [Scope and timeline](https://krisrchesney.github.io/payments-ops-analyst/roadmap.html) | [Project board](https://krisrchesney.github.io/payments-ops-analyst/board.html) | [Evaluation results](docs/eval.md)

## What it does

Ask it: *"Approval rates looked off during the week of September 21. Find what moved and explain why."*

The question gives no hint of the cause. The agent finds that suspected-fraud declines on online electronics jumped from about 8 a day to about 665 for three days, and it finds the fraud rule change and rollback in the change log that match those dates. It also says what it could not confirm. [Read the full answer and the check of each claim.](docs/sample-why-answer-week-of-2026-09-21.md)

## Architecture

```
generator (local Python, Faker + NumPy)
   └─ Parquet files ──upload──> Databricks Volume  /Volumes/workspace/payments/landing/
                                   │
               Spark Declarative Pipeline (Lakeflow), Databricks Free Edition
                 bronze: raw authorizations, chargebacks, merchants, issuers
                 silver: typed, deduplicated, joined, expectations on bad rows
                 gold:   daily ops tables (approval rate, decline reasons, latency, chargebacks)
                         and anomaly flags (not exported to the agent yet)
                 docs_chunks: ops documents split into 52 sections
                         │                         │
          export gold tables to Parquet     Vector Search index (managed embeddings)
                         │                         │
   mcp_server (local Python) ── DuckDB ────────────┘
     list_metrics, query_gold, compare_periods, top_decline_drivers, daily_ops_summary, search_runbooks
                         │
              Claude Desktop / Claude Code
```

Why the agent runs locally: Databricks Free Edition limits outbound internet from notebooks, and the Claude API has no free tier. An MCP server used from a Claude subscription costs nothing extra.

## How this maps to a card payment

Card payments typically run on the four-party model: the cardholder and their bank (the issuer), and the merchant and its bank (the acquirer). A card network connects the two banks, and its switch routes each authorization request to the issuer and carries the answer back. Clearing and settlement move the money later.

| Step | In this project |
|---|---|
| Cardholder | `card_token`, `is_tokenized`, `channel` |
| Merchant | `merchant_id`, `mcc`, region |
| Acquirer | Not modeled |
| Network and switch | Not modeled as a step; `latency_ms` is one total for the authorization |
| Issuer | `issuer_id`, and the result in `response_code`. Most declines are the issuer's decision; `91` means no answer came back, and the planted `59` spike comes from the processor's rule |
| Clearing and settlement | Not modeled |
| Disputes | Chargebacks linked to an approved `auth_id`. A real chargeback attaches to the cleared transaction, but clearing isn't modeled here |

**Viewpoint:** the reports and documents are written for an operations team at a fictional payment processor that handles authorizations on behalf of many banks and merchants. That's why it can compare 40 issuers at once and run fraud rules of its own.

**Response codes** follow general ISO 8583 style. Each real network and processor publishes its own list, so these won't match any one network exactly. For example, `91` is usually defined as the issuer or switch being inoperative, and it's called "issuer unavailable" here.

## Data

| Table | Grain | Notes |
|---|---|---|
| authorizations | one row per authorization | `response_code` is ISO 8583 style (`00` approved; 05, 51, 54, 14, 59, 91 declines), `is_tokenized` marks wallet tokens, `latency_ms` |
| chargebacks | one row per dispute | links to an approved `auth_id`; reason is fraud, not_received, not_as_described or duplicate |
| merchants | one row per merchant | MCC (merchant category code) and region |
| issuers | one row per issuer | home region |
| incidents.json | ground truth | three injected incidents (issuer outage, UK latency spike, electronics fraud-rule change) used to test whether the agent finds the real cause |
| docs_chunks | one row per document section | 10 synthetic documents in `docs/ops-library/`, split at `##` headings |

## Status

- [x] Synthetic data generator with tests
- [x] Bronze/silver/gold pipeline on Databricks (`pipelines/`), deployed with a bundle, every layer verified
- [x] Data quality rules proven with a file of planted bad rows
- [x] All three incidents found by hand from gold (`docs/incidents-by-hand.md`)
- [x] Gold export and MCP server (`mcp_server/`), 17 tests passing
- [x] Agent connected to Claude Code (`.mcp.json`) and found all three incidents, numbers checked against gold
- [x] Daily ops note drafted by the agent, every number checked (`docs/sample-daily-note-2026-09-23.md`)
- [x] Runbook search (RAG) with Databricks Vector Search: 6 of 6 test questions found the expected document in the top 3
- [x] Agent explains a metric move by citing a document and gold numbers (`docs/sample-why-answer-week-of-2026-09-21.md`)
- [x] Formal agent evaluation: [8 of 12 runs passed](docs/eval.md). All 9 runs with a hint found the right cause, 2 of them had a wrong figure, and 1 of 3 no-hint runs found all three incidents
- [x] Anomaly table flags all three incidents with no flag on a normal day ([thresholds and limits](docs/detection.md)). Thresholds were set knowing the answers, so this isn't an independent test
- [x] Hourly data feed job: one run by hand added exactly the new hour's rows. The schedule is paused, so it hasn't run on its own
- [ ] Detection test on newly planted incidents: the [plan and predictions](docs/detection-test.md) are written first, and the data isn't generated yet
- [ ] Alert and dashboard. Today someone has to look, because nothing alerts anyone
- [ ] Demo recording

Verified facts and evidence for each item: `docs/project-summary.md`. Databricks notebooks for the early checks and the incident search are in `notebooks/`.

## Results

From the [formal evaluation](docs/eval.md), which graded 12 isolated runs against rules written before any run:

| Test | Result |
|---|---|
| All runs | 8 of 12 passed |
| A question points to the problem | 9 of 9 found the true cause and the right document; 2 of those had a wrong figure, so 7 passed |
| No hint: review the whole month | 1 of 3 found all three planted incidents |
| Time per run | 31 to 46 seconds, against a target of under 1 minute |

The same author wrote the data, documents and questions, so these results don't predict performance on real data.

## Next steps

1. Finish automatic detection: run the [detection test](docs/detection-test.md) on newly planted incidents, then add an alert and dashboard. See the [scope and timeline](https://krisrchesney.github.io/payments-ops-analyst/roadmap.html).
2. Record the demo.

Also see the [release notes](docs/product/releases.md) and the [product brief](docs/product/brief.md).

## How it was built

Claude Code wrote the Python under my direction. I set the requirements and product decisions, reviewed what it wrote, ran the deployments and tests, and typed the Databricks notebook queries myself. Commits are marked `Co-Authored-By`. The product requirements are in `docs/product/PRD.md`. The Jira board is private, and the [project board](https://krisrchesney.github.io/payments-ops-analyst/board.html) is a read-only copy of it.

## Run it

The tests need no Databricks account:

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest -q tests
```

Generate the data:

```
.venv\Scripts\python generator\generate_auths.py --rows 2000000 --days 28 --out out
```

To run the whole thing, you also need a Databricks workspace signed in through the CLI. Upload `out/` to the landing volume and `docs/ops-library/` (without its README) to `landing/docs`, then deploy with `databricks bundle deploy` and `databricks bundle run payments_ops_pipeline`. Create the Vector Search endpoint and index, then run `mcp_server/export_gold.py`. See `mcp_server/README.md` for the agent. The bundle keeps its original internal name, `payments-ops-pipeline`.

## License

MIT
