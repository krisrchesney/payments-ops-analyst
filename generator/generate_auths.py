"""Generate synthetic card authorization and chargeback data.

All data is synthetic. Nothing here is real card, merchant or cardholder data.

Writes Parquet files you upload to a Databricks Volume (the bronze landing zone):
  out/authorizations/part-XXXX.parquet
  out/chargebacks/part-0000.parquet
  out/merchants.parquet, out/issuers.parquet
  out/incidents.json   ground truth for the injected incidents, used to test the agent

Usage:
  python generator/generate_auths.py --rows 2000000 --days 28 --out out
"""
import argparse
import json
import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from faker import Faker

REGIONS = ["US-Midwest", "US-Northeast", "US-South", "US-West", "CA", "UK", "DE", "BR"]
REGION_WEIGHTS = [0.18, 0.17, 0.2, 0.17, 0.07, 0.09, 0.07, 0.05]
CHANNELS = ["card_present", "contactless", "ecommerce", "card_on_file"]
CHANNEL_WEIGHTS = [0.3, 0.25, 0.3, 0.15]
# MCC: merchant category code (ISO 18245), with a typical ticket size in USD
MCCS = {
    "5411": ("Grocery stores", 60), "5812": ("Restaurants", 45), "5541": ("Fuel", 50),
    "5311": ("Department stores", 90), "5732": ("Electronics", 250), "4121": ("Rideshare and taxi", 25),
    "4511": ("Airlines", 420), "7011": ("Hotels", 300), "5999": ("Misc retail", 70),
    "4899": ("Streaming and cable", 18),
}
# ISO 8583 style response codes; "00" is approved
DECLINES = {"05": 0.45, "51": 0.30, "54": 0.06, "14": 0.04, "59": 0.05, "91": 0.10}
BASE_DECLINE_RATE = 0.06


def build_dims(rng, fake, n_merchants=800, n_issuers=40):
    mcc_codes = list(MCCS)
    merchants = pd.DataFrame({
        "merchant_id": [f"M{i:05d}" for i in range(n_merchants)],
        "merchant_name": [fake.company() for _ in range(n_merchants)],
        "mcc": rng.choice(mcc_codes, n_merchants),
        "region": rng.choice(REGIONS, n_merchants, p=REGION_WEIGHTS),
    })
    merchants["mcc_description"] = merchants["mcc"].map(lambda m: MCCS[m][0])
    issuers = pd.DataFrame({
        "issuer_id": [f"I{i:03d}" for i in range(n_issuers)],
        "issuer_name": [f"{fake.last_name()} {rng.choice(['Bank', 'Credit Union', 'Financial'])}" for _ in range(n_issuers)],
        "home_region": rng.choice(REGIONS, n_issuers, p=REGION_WEIGHTS),
    })
    return merchants, issuers


def pick_incidents(rng, start, days, issuers):
    """Three injected incidents the ops agent should be able to find and explain."""
    def at(day, hour):
        return start + timedelta(days=int(day), hours=int(hour))
    outage_issuer = issuers.sample(1, random_state=int(rng.integers(1e9))).iloc[0]
    return [
        {"id": "INC-1", "type": "issuer_outage", "issuer_id": outage_issuer.issuer_id,
         "start": at(days * 0.4, 14).isoformat(), "end": at(days * 0.4, 17).isoformat(),
         "effect": "Most of this issuer's authorizations decline with 91 (issuer unavailable)."},
        {"id": "INC-2", "type": "latency_spike", "region": "UK",
         "start": at(days * 0.6, 9).isoformat(), "end": at(days * 0.6, 11).isoformat(),
         "effect": "Authorization latency in UK roughly 6x normal; approvals unchanged."},
        {"id": "INC-3", "type": "fraud_rule_tightened", "mcc": "5732",
         "start": at(days * 0.75, 0).isoformat(), "end": at(days * 0.75 + 3, 0).isoformat(),
         "effect": "Electronics ecommerce declines with 59 (suspected fraud) jump for three days."},
    ]


def generate_chunk(rng, n, start, days, merchants, issuers, incidents, id_offset):
    ts = start + pd.to_timedelta(rng.random(n) * days * 86400, unit="s")
    m = merchants.iloc[rng.integers(0, len(merchants), n)].reset_index(drop=True)
    iss = issuers.iloc[rng.integers(0, len(issuers), n)].reset_index(drop=True)
    channel = rng.choice(CHANNELS, n, p=CHANNEL_WEIGHTS)
    typical = m["mcc"].map(lambda c: MCCS[c][1]).to_numpy()
    amount = np.round(rng.lognormal(np.log(typical), 0.6), 2)
    # Wallet tokenization (e.g. phone wallets) is common for contactless and ecommerce
    token_p = np.select([channel == "contactless", channel == "ecommerce", channel == "card_on_file"], [0.85, 0.45, 0.6], 0.05)
    tokenized = rng.random(n) < token_p
    latency = rng.gamma(4.0, 45.0, n)  # ms, mean about 180

    decline_p = np.full(n, BASE_DECLINE_RATE) + np.where(channel == "ecommerce", 0.03, 0) - np.where(tokenized, 0.015, 0)
    codes = np.where(rng.random(n) < decline_p,
                     rng.choice(list(DECLINES), n, p=list(DECLINES.values())), "00").astype(object)

    for inc in incidents:
        s, e = pd.Timestamp(inc["start"]), pd.Timestamp(inc["end"])
        in_window = (ts >= s) & (ts < e)
        if inc["type"] == "issuer_outage":
            hit = in_window & (iss["issuer_id"].to_numpy() == inc["issuer_id"]) & (rng.random(n) < 0.8)
            codes[hit] = "91"
        elif inc["type"] == "latency_spike":
            hit = in_window & (m["region"].to_numpy() == inc["region"])
            latency[hit] *= 6
        elif inc["type"] == "fraud_rule_tightened":
            hit = in_window & (m["mcc"].to_numpy() == inc["mcc"]) & (channel == "ecommerce") & (rng.random(n) < 0.35)
            codes[hit] = "59"

    return pd.DataFrame({
        "auth_id": [f"A{id_offset + i:010d}" for i in range(n)],
        "event_ts": ts,
        "card_token": [f"tok_{x:012x}" for x in rng.integers(0, 2**44, n)],
        "merchant_id": m["merchant_id"],
        "issuer_id": iss["issuer_id"],
        "channel": channel,
        "is_tokenized": tokenized,
        "amount": amount,
        "currency": "USD",
        "response_code": codes.astype(str),
        "latency_ms": np.round(latency).astype(int),
    })


def make_chargebacks(rng, auths, rate=0.004):
    approved = auths[auths["response_code"] == "00"]
    cb = approved.sample(frac=rate, random_state=int(rng.integers(1e9)))
    reasons = rng.choice(["fraud", "not_received", "not_as_described", "duplicate"], len(cb), p=[0.5, 0.25, 0.18, 0.07])
    return pd.DataFrame({
        "chargeback_id": [f"C{i:08d}" for i in range(len(cb))],
        "auth_id": cb["auth_id"].to_numpy(),
        "filed_ts": (cb["event_ts"] + pd.to_timedelta(rng.integers(3, 60, len(cb)), unit="D")).to_numpy(),
        "reason": reasons,
        "amount": cb["amount"].to_numpy(),
    })


def write_parquet(df, path):
    # Spark can't read nanosecond Parquet timestamps, so store microseconds
    df.to_parquet(path, index=False, coerce_timestamps="us", allow_truncated_timestamps=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=int, default=2_000_000)
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--chunk", type=int, default=500_000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--start", default="2026-09-01")
    ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)

    rng = np.random.default_rng(a.seed)
    fake = Faker()
    Faker.seed(a.seed)
    start = datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc)
    merchants, issuers = build_dims(rng, fake)
    incidents = pick_incidents(rng, start, a.days, issuers)

    os.makedirs(f"{a.out}/authorizations", exist_ok=True)
    os.makedirs(f"{a.out}/chargebacks", exist_ok=True)
    merchants.to_parquet(f"{a.out}/merchants.parquet", index=False)
    issuers.to_parquet(f"{a.out}/issuers.parquet", index=False)

    cbs, done, part = [], 0, 0
    while done < a.rows:
        n = min(a.chunk, a.rows - done)
        df = generate_chunk(rng, n, start, a.days, merchants, issuers, incidents, done)
        write_parquet(df, f"{a.out}/authorizations/part-{part:04d}.parquet")
        cbs.append(make_chargebacks(rng, df))
        done += n
        part += 1
        print(f"wrote {done:,} / {a.rows:,} authorizations")

    cb = pd.concat(cbs, ignore_index=True)
    cb["chargeback_id"] = [f"C{i:08d}" for i in range(len(cb))]
    write_parquet(cb, f"{a.out}/chargebacks/part-0000.parquet")
    with open(f"{a.out}/incidents.json", "w") as f:
        json.dump(incidents, f, indent=2)
    print(f"wrote {len(cb):,} chargebacks and {len(incidents)} incidents to {a.out}/")


if __name__ == "__main__":
    main()
