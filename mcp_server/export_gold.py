"""Copy the gold tables from Databricks to local Parquet files in exports/ (PAYOPS-44).

The Claude agent reads these local copies, so asking it questions uses no Databricks compute.
Re-run after every pipeline run to refresh them.

Uses your Databricks CLI login (profile DEFAULT by default) and the workspace's SQL warehouse.

Usage:
  python mcp_server/export_gold.py
  python mcp_server/export_gold.py --profile DEFAULT --out exports
"""
import argparse
import os
import time

import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import Disposition, Format, StatementState

SCHEMA = "workspace.payments"
TABLES = [
    "gold_daily_approval",
    "gold_decline_reasons",
    "gold_declines_by_category",
    "gold_latency_hourly",
    "gold_chargebacks_weekly",
]

# How to turn Databricks column types (sent as text) back into proper types
CONVERT = {
    "DATE": lambda s: pd.to_datetime(s).dt.date,
    "TIMESTAMP": lambda s: pd.to_datetime(s, utc=True),
    "INT": lambda s: pd.to_numeric(s).astype("Int64"),
    "LONG": lambda s: pd.to_numeric(s).astype("Int64"),
    "SHORT": lambda s: pd.to_numeric(s).astype("Int64"),
    "DOUBLE": lambda s: pd.to_numeric(s),
    "FLOAT": lambda s: pd.to_numeric(s),
    "DECIMAL": lambda s: pd.to_numeric(s),
    "BOOLEAN": lambda s: s.map({"true": True, "false": False}),
}


def run_query(w, warehouse_id, sql):
    """Run one SQL statement on the warehouse and return a DataFrame."""
    resp = w.statement_execution.execute_statement(
        statement=sql, warehouse_id=warehouse_id, wait_timeout="50s",
        disposition=Disposition.INLINE, format=Format.JSON_ARRAY)
    # A cold warehouse can take longer than 50 seconds to start: keep checking until it finishes.
    while resp.status.state in (StatementState.PENDING, StatementState.RUNNING):
        time.sleep(3)
        resp = w.statement_execution.get_statement(resp.statement_id)
    if resp.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(f"query failed: {resp.status.error.message if resp.status.error else resp.status.state}")

    columns = resp.manifest.schema.columns
    rows = list(resp.result.data_array or [])
    # Big results come back in chunks: fetch the rest.
    for i in range(1, resp.manifest.total_chunk_count or 1):
        chunk = w.statement_execution.get_statement_result_chunk_n(resp.statement_id, i)
        rows.extend(chunk.data_array or [])

    df = pd.DataFrame(rows, columns=[c.name for c in columns])
    for c in columns:
        kind = c.type_name.value if hasattr(c.type_name, "value") else str(c.type_name)
        if kind in CONVERT and len(df):
            df[c.name] = CONVERT[kind](df[c.name])
    return df


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", default="DEFAULT")
    ap.add_argument("--out", default="exports")
    a = ap.parse_args(argv)

    w = WorkspaceClient(profile=a.profile)
    warehouses = list(w.warehouses.list())
    if not warehouses:
        raise SystemExit("No SQL warehouse found in this workspace.")
    warehouse = warehouses[0]
    print(f"using SQL warehouse: {warehouse.name} (starts automatically if stopped)")

    os.makedirs(a.out, exist_ok=True)
    for table in TABLES:
        df = run_query(w, warehouse.id, f"SELECT * FROM {SCHEMA}.{table}")
        path = os.path.join(a.out, f"{table}.parquet")
        df.to_parquet(path, index=False, coerce_timestamps="us", allow_truncated_timestamps=True)
        print(f"  {table:28s} {len(df):>7,} rows -> {path}")
    print("done")


if __name__ == "__main__":
    main()
