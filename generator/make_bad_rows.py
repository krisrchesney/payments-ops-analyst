"""Make a small authorizations file with known bad rows, to prove silver's quality rules work (PAYOPS-34).

Every row is labeled with what it should do in silver. Upload the file to the landing volume's
authorizations folder and re-run the pipeline: Auto Loader reads only this new file.

Expected after the run:
  bronze_authorizations   2,000,000 -> 2,000,017  (all 17 rows land in bronze, bad or not)
  silver_authorizations   2,000,000 -> 2,000,005  (only the 5 good rows get through)
  dropped by rules        10 = positive_amount 3 + known_response_code 3 + known_merchant 4
  removed as duplicates   2  (copies of an auth_id that is already in bronze)

Usage:
  python generator/make_bad_rows.py --out out/test
"""
import argparse
import os
from datetime import datetime, timezone

import pandas as pd

TS = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)   # last day of the generated month
GOOD = dict(merchant_id="M00005", issuer_id="I010", channel="card_present", is_tokenized=False,
            amount=42.50, currency="USD", response_code="00", latency_ms=150)

# (auth_id, overrides, what silver should do)
CASES = [
    # 3 rows break positive_amount
    ("TEST-AMT-NEG", dict(amount=-10.00), "drop: positive_amount"),
    ("TEST-AMT-ZERO", dict(amount=0.00), "drop: positive_amount"),
    ("TEST-AMT-NEG2", dict(amount=-0.01), "drop: positive_amount"),
    # 3 rows break known_response_code
    ("TEST-CODE-99", dict(response_code="99"), "drop: known_response_code"),
    ("TEST-CODE-XX", dict(response_code="XX"), "drop: known_response_code"),
    ("TEST-CODE-BLANK", dict(response_code=""), "drop: known_response_code"),
    # 4 rows break known_merchant (3 merchants that don't exist, 1 missing merchant)
    ("TEST-MERCH-1", dict(merchant_id="M99991"), "drop: known_merchant"),
    ("TEST-MERCH-2", dict(merchant_id="M99992"), "drop: known_merchant"),
    ("TEST-MERCH-3", dict(merchant_id="M99993"), "drop: known_merchant"),
    ("TEST-MERCH-NULL", dict(merchant_id=None), "drop: known_merchant"),
    # 2 copies of an auth_id already in bronze: dedup keeps the original
    ("A0000000000", dict(), "remove: duplicate"),
    ("A0000000001", dict(), "remove: duplicate"),
    # 5 good rows: should reach silver
    ("TEST-GOOD-1", dict(), "keep"),
    ("TEST-GOOD-2", dict(response_code="05"), "keep"),
    ("TEST-GOOD-3", dict(channel="ecommerce", is_tokenized=True), "keep"),
    ("TEST-GOOD-4", dict(amount=0.01), "keep"),
    ("TEST-GOOD-5", dict(merchant_id="M00799", issuer_id="I039"), "keep"),
]


def build():
    rows = []
    for auth_id, overrides, expect in CASES:
        row = dict(GOOD, auth_id=auth_id, event_ts=TS, card_token=f"tok_test_{auth_id.lower()}")
        row.update(overrides)
        rows.append((row, expect))
    df = pd.DataFrame([r for r, _ in rows])
    # Same columns, order and types as the generator's authorization files
    df = df[["auth_id", "event_ts", "card_token", "merchant_id", "issuer_id", "channel",
             "is_tokenized", "amount", "currency", "response_code", "latency_ms"]]
    df["latency_ms"] = df["latency_ms"].astype("int64")
    df["is_tokenized"] = df["is_tokenized"].astype(bool)
    return df, [e for _, e in rows]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="out/test")
    a = ap.parse_args(argv)
    df, expects = build()
    os.makedirs(a.out, exist_ok=True)
    path = f"{a.out}/part-test-bad-rows.parquet"
    df.to_parquet(path, index=False, coerce_timestamps="us", allow_truncated_timestamps=True)
    print(f"wrote {len(df)} rows to {path}")
    for (auth_id, _, _), e in zip(CASES, expects):
        print(f"  {auth_id:16s} {e}")


if __name__ == "__main__":
    main()
