# Pipeline spec

The original spec for the bronze, silver and gold tables. The code is in `transformations/`, and `docs.py` adds the document sections used for search.

Use Spark Declarative Pipelines (Lakeflow). Current Python syntax per the Databricks docs (checked 2026-10-27):

```python
from pyspark import pipelines as dp   # `import dlt` still works but is deprecated
```

Decorators: `@dp.table` (streaming tables), `@dp.materialized_view`, `@dp.temporary_view`. Expectations: `@dp.expect(...)` and its drop/fail variants; check the "expectations" page for exact names.

## Bronze (raw, append only)
- `bronze_authorizations`: Auto Loader (`cloudFiles`, format parquet) from `/Volumes/workspace/payments/landing/authorizations/`. Add `_ingested_at` and `_source_file`.
- `bronze_chargebacks`, `bronze_merchants`, `bronze_issuers`: same pattern.

## Silver (clean and conformed)
- `silver_authorizations`: types fixed, one row per `auth_id` (dedupe), `is_approved = response_code == "00"`, `event_date`, `event_hour`, joined to merchant (mcc, mcc_description, region) and issuer.
- Expectations: `amount > 0`, `response_code` in the known list, `merchant_id` not null. Drop bad rows and watch the counts in the pipeline UI.
- `silver_chargebacks`: joined to the original authorization.

## Gold (what the ops team and the agent read)
- `gold_daily_approval`: by date, region, channel, is_tokenized: auth count, approval rate, declined amount.
- `gold_decline_reasons`: by date, region, issuer, response_code: count and share of declines.
- `gold_latency_hourly`: by hour and region: p50, p95, p99 latency (`percentile_approx`).
- `gold_chargebacks_weekly`: by week, mcc, reason: count, amount, rate per 1,000 approvals.

## Done when
- The pipeline runs end to end on Free Edition with expectations showing dropped-row counts.
- You can point to INC-1, INC-2 and INC-3 from `incidents.json` in the gold tables by hand. If you can't see them, the agent won't either.
- Gold tables are exported to Parquet (Catalog Explorer download, or `COPY INTO` a volume and download) for the MCP server.

## Free Edition limits to plan around
Serverless only; one active pipeline per type; a daily fair-use quota that shuts compute off for the day if exceeded; non-commercial use. Start with `--rows 2000000` and scale only if runs stay quick.
