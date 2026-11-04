"""Write simulated card authorizations for the next hour (or hours) into the landing volume.

PAYOPS-55. All data is synthetic. The feed keeps a simulated clock that starts where the generated month
ended (2026-09-29 00:00 UTC). Each hour is one file, landing/authorizations/feed-YYYY-MM-DDTHH.parquet, and the
file names are the clock: the next hour is the one after the latest feed file, so running twice never
rewrites an hour. An hour is generated from a seed of (seed, hour number), so the same hour always comes out
the same.

Planted incidents come from landing/feed/incidents.json: a list shaped like out/incidents.json (type
issuer_outage, latency_spike or fraud_rule_tightened, with start, end and the issuer_id, region or mcc it
hits). Add hit_rate, latency_multiplier or decline_rate to set how strong one is. Upload the file before the
hours it covers are written, e.g.
  databricks fs cp incidents.json dbfs:/Volumes/workspace/payments/landing/feed/incidents.json

Usage:
  python generator/feed_hour.py --landing /Volumes/workspace/payments/landing --hours 1
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
except NameError:  # some job runners execute the file without setting __file__
    sys.path.insert(0, os.getcwd())
import generate_auths  # noqa: E402

FIRST_HOUR = "2026-09-29T00"  # the hour after the generated month ends
ROWS_PER_HOUR = 2976          # the month's 2,000,000 rows over its 672 hours
ORIGINAL_ROWS = 2_000_000
ID_BLOCK = 100_000            # auth ids reserved per hour, so ids stay unique if the row count changes
HOUR_FORMAT = "%Y-%m-%dT%H"
TARGET_KEY = {"issuer_outage": "issuer_id", "latency_spike": "region", "fraud_rule_tightened": "mcc"}


def parse_hour(text):
    return datetime.strptime(text, HOUR_FORMAT).replace(tzinfo=timezone.utc)


def utc(text):
    ts = pd.Timestamp(text)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def latest_hour(folder):
    """The hour of the newest feed file in the folder, or None if the feed hasn't started."""
    names = sorted(n for n in os.listdir(folder) if n.startswith("feed-") and n.endswith(".parquet"))
    return parse_hour(names[-1][len("feed-"):-len(".parquet")]) if names else None


def load_incidents(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        incidents = json.load(f)
    for inc in incidents:
        kind = inc.get("type")
        if kind not in TARGET_KEY:
            raise ValueError(f"{path}: unknown incident type {kind!r}, expected one of {sorted(TARGET_KEY)}")
        for key in ("start", "end", TARGET_KEY[kind]):
            if key not in inc:
                raise ValueError(f"{path}: a {kind} incident needs {key!r}")
        inc["start"], inc["end"] = utc(inc["start"]).isoformat(), utc(inc["end"]).isoformat()
    return incidents


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--landing", required=True, help="landing folder, e.g. /Volumes/workspace/payments/landing")
    ap.add_argument("--hours", type=int, default=1, help="how many hours to write; more than 1 catches the clock up")
    ap.add_argument("--rows-per-hour", type=int, default=ROWS_PER_HOUR)
    ap.add_argument("--first-hour", default=FIRST_HOUR)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    if not 0 < a.rows_per_hour < ID_BLOCK:
        ap.error(f"--rows-per-hour must be between 1 and {ID_BLOCK - 1:,}")

    folder = f"{a.landing}/authorizations"
    os.makedirs(folder, exist_ok=True)
    merchants = pd.read_parquet(f"{a.landing}/merchants.parquet")
    issuers = pd.read_parquet(f"{a.landing}/issuers.parquet")
    incidents = load_incidents(f"{a.landing}/feed/incidents.json")

    first = parse_hour(a.first_hour)
    last = latest_hour(folder)
    hour = first if last is None else last + timedelta(hours=1)
    for _ in range(a.hours):
        n = int((hour - first) / timedelta(hours=1))
        rng = np.random.default_rng([a.seed, n])
        df = generate_auths.generate_chunk(rng, a.rows_per_hour, hour, 1 / 24, merchants, issuers,
                                           incidents, ORIGINAL_ROWS + n * ID_BLOCK)
        path = f"{folder}/feed-{hour.strftime(HOUR_FORMAT)}.parquet"
        generate_auths.write_parquet(df, path)
        end = hour + timedelta(hours=1)
        active = [i["type"] for i in incidents if utc(i["start"]) < end and utc(i["end"]) > hour]
        print(f"wrote {len(df):,} authorizations for {hour:%Y-%m-%d %H}:00 UTC to {path}"
              + (f" (planted: {', '.join(active)})" if active else ""))
        hour = end


if __name__ == "__main__":
    main()
