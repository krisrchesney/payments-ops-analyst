"""The detection test in docs/detection-test.md: make the test data locally, check the planted incidents, score the flags.

All data is synthetic. The data is the same data the Databricks feed job writes: every hour is generated from a seed
of (seed, hour number), and the dimension tables come from the same seed as the month-long run. Nothing here changes
the thresholds in pipelines/transformations/gold.py. The scoring rules below are the ones in the test plan, which was
approved before any test data existed. This script itself was written after the data had been generated on Databricks,
and it was committed before its author read any of the flags it scores.

  python evals/detection_test.py generate --out out/detection-test     # 336 hours, about 1 million rows
  python evals/detection_test.py check    --data out/detection-test    # did the planted incidents land as planned?
  python evals/detection_test.py score    --data out/detection-test --anomalies gold_anomalies.csv

`score` needs the rows of workspace.payments.gold_anomalies exported from Databricks (CSV or Parquet). It looks only at
flags on the 14 test days, September 29 to October 12.
"""
import argparse
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "generator"))
PLAN_PATH = ROOT / "docs" / "detection-test-incidents.json"

FIRST_DAY, LAST_DAY = pd.Timestamp("2026-09-29"), pd.Timestamp("2026-10-12")
HOURS = 14 * 24
# thresholds as in pipelines/transformations/gold.py; a test checks they have not drifted
APPROVAL_DROP_Z, DECLINE_SPIKE_Z, DECLINE_SPIKE_MIN_EXCESS, LATENCY_SPIKE_RATIO = 4.0, 5.0, 25, 2.0
EXPECTED_HOURS_A = 2        # TEST-A: "at least 2 of the 3 hours"
SHOULD_MISS = {"TEST-D"}


def load_plan(path=PLAN_PATH):
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    for inc in plan:
        inc["start_ts"], inc["end_ts"] = pd.Timestamp(inc["start"]).tz_convert("UTC").tz_localize(None), pd.Timestamp(inc["end"]).tz_convert("UTC").tz_localize(None)
        inc["day"] = inc["start_ts"].normalize()
    return plan


# ---- data ---------------------------------------------------------------------------------------------
def make_dims(seed=7):
    """The merchant and issuer tables, rebuilt the way generate_auths.py builds them for the month-long run."""
    import generate_auths
    from faker import Faker
    rng = np.random.default_rng(seed)
    fake = Faker()
    Faker.seed(seed)
    return generate_auths.build_dims(rng, fake)


def generate(out, seed=7):
    import feed_hour
    out = Path(out)
    if (out / "authorizations").exists() and any((out / "authorizations").glob("feed-*.parquet")):
        sys.exit(f"{out} already has feed files; the test data is generated once. Delete the folder to start over.")
    (out / "feed").mkdir(parents=True, exist_ok=True)
    merchants, issuers = make_dims(seed)
    merchants.to_parquet(out / "merchants.parquet", index=False)
    issuers.to_parquet(out / "issuers.parquet", index=False)
    shutil.copy(PLAN_PATH, out / "feed" / "incidents.json")
    feed_hour.main(["--landing", str(out), "--hours", str(HOURS), "--seed", str(seed)])


def load_data(folder):
    folder = Path(folder)
    auths = pd.concat([pd.read_parquet(f) for f in sorted((folder / "authorizations").glob("feed-*.parquet"))], ignore_index=True)
    merchants = pd.read_parquet(folder / "merchants.parquet")[["merchant_id", "mcc", "mcc_description", "region"]]
    issuers = pd.read_parquet(folder / "issuers.parquet")[["issuer_id", "issuer_name"]]
    df = auths.merge(merchants, on="merchant_id").merge(issuers, on="issuer_id")
    df["event_ts"] = pd.to_datetime(df["event_ts"], utc=True).dt.tz_localize(None)
    df["day"], df["hour"] = df["event_ts"].dt.normalize(), df["event_ts"].dt.floor("h")
    df["approved"] = df["response_code"] == "00"
    return df


def target_mask(df, inc):
    """The rows an incident's own rule acts on: its target and its response code. Latency has none."""
    if inc["type"] == "issuer_outage":
        return (df["issuer_id"] == inc["issuer_id"]) & (df["response_code"] == "91")
    if inc["type"] == "fraud_rule_tightened":
        return (df["mcc"] == inc["mcc"]) & (df["channel"] == "ecommerce") & (df["response_code"] == "59")
    return pd.Series(False, index=df.index)


def expected_entity(df, inc):
    """The entity name gold_anomalies uses for the flag each incident should produce."""
    if inc["type"] == "issuer_outage":
        names = df.loc[df["issuer_id"] == inc["issuer_id"], "issuer_name"]
        return "issuer_and_code", f"{names.iloc[0] if len(names) else inc['issuer_id']} / 91"
    if inc["type"] == "fraud_rule_tightened":
        descs = df.loc[df["mcc"] == inc["mcc"], "mcc_description"]
        return "category_channel_and_code", f"{descs.iloc[0] if len(descs) else inc['mcc']} / ecommerce / 59"
    return "region", inc["region"]


# ---- check ---------------------------------------------------------------------------------------------
def check(df, plan):
    """Plain measurements of what each planted incident did to the data. These are about the data, not the detector."""
    rows = []
    for inc in plan:
        window = (df["event_ts"] >= inc["start_ts"]) & (df["event_ts"] < inc["end_ts"])
        if inc["type"] == "latency_spike":
            inside = df[window & (df["region"] == inc["region"])]["latency_ms"].quantile(.95)
            other = df[~window & (df["region"] == inc["region"])]["latency_ms"].quantile(.95)
            rows.append((inc["id"], f"{inc['region']} p95 latency in the window", f"{inside:.0f} ms", f"{other:.0f} ms elsewhere ({inside / other:.2f}x; planned {inc['latency_multiplier']}x)"))
        elif inc["type"] == "issuer_outage":
            mine = df["issuer_id"] == inc["issuer_id"]
            n, hit = (window & mine).sum(), (window & mine & (df["response_code"] == "91")).sum()
            per_window = (df[mine & (df["response_code"] == "91")].groupby("hour").size().reindex(pd.date_range(FIRST_DAY, periods=HOURS, freq="h"), fill_value=0))
            normal = per_window[~per_window.index.isin(pd.date_range(inc["start_ts"], inc["end_ts"], freq="h", inclusive="left"))].mean() * ((inc["end_ts"] - inc["start_ts"]).total_seconds() / 3600)
            rows.append((inc["id"], f"{inc['issuer_id']} requests and code 91 in the window", f"{n} requests, {hit} with 91", f"about {normal:.1f} 91s expected in a normal window; planned hit rate {inc['hit_rate']}"))
        else:
            mine = (df["mcc"] == inc["mcc"]) & (df["channel"] == "ecommerce")
            per_day = df[mine & (df["response_code"] == "59")].groupby("day").size().reindex(pd.date_range(FIRST_DAY, LAST_DAY), fill_value=0)
            on = int(per_day.get(inc["day"], 0))
            normal = per_day.drop(inc["day"]).mean()
            rows.append((inc["id"], f"MCC {inc['mcc']} ecommerce code 59 on {inc['day']:%b %d}", f"{on}", f"{normal:.1f} on a normal day, so {on - normal:.0f} extra (planned rate {inc['decline_rate']})"))
    return rows


# ---- score ---------------------------------------------------------------------------------------------
def load_flags(path):
    path = Path(path)
    flags = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    flags["period_start"] = pd.to_datetime(flags["period_start"], utc=True).dt.tz_localize(None)
    flags["day"] = flags["period_start"].dt.normalize()
    return flags[(flags["day"] >= FIRST_DAY) & (flags["day"] <= LAST_DAY)].reset_index(drop=True)


def _se(b, n):
    return math.sqrt(b * (1 - b) / n)


def explain(flag, df, inc):
    """Score a flag again with the incident's own declines removed, as the first write-up did.
    Returns (score without the rule, extra declines the rule contributed, explained?)."""
    mask = target_mask(df, inc)
    day = df["day"] == flag["day"]
    if flag["detector"] == "approval_drop":
        col = "region" if flag["scope"] == "region" else "issuer_name"
        entity = day & (df[col] == flag["entity"])
        n, approved = int(entity.sum()), int(df[entity & df["approved"]].shape[0])
        removed = int((entity & mask).sum())
        n2, b = n - removed, flag["baseline"]
        score = (b - approved / n2) / _se(b, n2)
        return score, removed, score < APPROVAL_DROP_Z
    if flag["detector"] == "decline_spike":
        keys = flag["entity"].split(" / ")
        if flag["scope"] == "issuer_and_code":
            entity = day & (df["issuer_name"] == keys[0]) & (df["response_code"] == keys[1])
        else:
            entity = day & (df["mcc_description"] == keys[0]) & (df["channel"] == keys[1]) & (df["response_code"] == keys[2])
        removed = int((entity & mask).sum())
        value, b = flag["observed"] - removed, flag["baseline"]
        excess = value - b
        score = excess / math.sqrt(max(b, 1))
        return score, removed, bool(score < DECLINE_SPIKE_Z or excess < DECLINE_SPIKE_MIN_EXCESS)
    return float("nan"), 0, False        # a latency flag has no declines to remove


def score_flags(flags, df, plan):
    """Classify every flag on the 14 test days: hit, explained flag, false alarm. Returns (rows, summary)."""
    incident_days = {inc["day"]: inc for inc in plan}
    expect = {inc["id"]: expected_entity(df, inc) for inc in plan}
    rows, hits = [], {inc["id"]: 0 for inc in plan}
    for _, f in flags.sort_values(["period_start", "detector", "entity"]).iterrows():
        status, note, inc = "false alarm", "", incident_days.get(f["day"])
        for p in plan:
            scope, entity = expect[p["id"]]
            if p["type"] == "latency_spike":
                is_hit = f["detector"] == "latency_spike" and f["entity"] == entity and p["start_ts"] <= f["period_start"] < p["end_ts"]
            else:
                is_hit = f["detector"] == "decline_spike" and f["scope"] == scope and f["entity"] == entity and f["day"] == p["day"]
            if is_hit:
                status, hits[p["id"]], note = "hit", hits[p["id"]] + 1, p["id"]
                break
        if status != "hit" and inc is not None and inc["type"] != "latency_spike":
            new_score, removed, explained = explain(f, df, inc)
            if explained:
                status, note = "explained", f"{inc['id']}: score without its declines {new_score:.2f}, {removed} of its declines removed"
            else:
                note = f"{inc['id']} day, but still flagged without its declines (score {new_score:.2f})"
        rows.append(dict(day=f["day"].date(), when=f["period_start"], detector=f["detector"], series=f["entity"],
                         observed=f["observed"], baseline=f["baseline"], score=f["score"], status=status, note=note))
    out = pd.DataFrame(rows)
    surprises = []
    for p in plan:
        n = hits[p["id"]]
        if p["id"] in SHOULD_MISS and n:
            surprises.append(f"{p['id']} was flagged ({n}); the plan expected a miss")
        elif p["id"] not in SHOULD_MISS:
            need = EXPECTED_HOURS_A if p["type"] == "latency_spike" else 1
            if n < need:
                surprises.append(f"{p['id']} was not caught as planned ({n} flagged; expected at least {need})")
    summary = dict(flags=len(out), hits=hits, explained=int((out["status"] == "explained").sum()) if len(out) else 0,
                   false_alarms=int((out["status"] == "false alarm").sum()) if len(out) else 0, surprises=surprises)
    return out, summary


def checks_made(df):
    """Series-days the detector looked at over the 14 days, so a false-alarm count has a denominator."""
    days = 14
    regions, issuers = df["region"].nunique(), df["issuer_name"].nunique()
    issuer_code = df[df["response_code"] != "00"][["issuer_name", "response_code"]].drop_duplicates().shape[0]
    cat_code = df[df["response_code"] != "00"][["mcc_description", "channel", "response_code"]].drop_duplicates().shape[0]
    return dict(approval=(regions + issuers) * days, decline_issuer_code=issuer_code * days, decline_category=cat_code * days,
                latency=regions * HOURS)


def markdown(out, summary, made):
    lines = ["| Day | When (UTC) | Check | Series | Observed | Baseline | Score | Result | Note |", "|---|---|---|---|---|---|---|---|---|"]
    for r in out.itertuples():
        when = f"{r.when:%H:00}" if r.detector == "latency_spike" else ""
        lines.append(f"| {r.day} | {when} | {r.detector.replace('_', ' ')} | {r.series} | {r.observed:g} | {r.baseline:g} | {r.score:g} | {r.status} | {r.note} |")
    lines += ["", f"Series-days checked: {sum(made.values()):,} ({made}).",
              f"Flags: {summary['flags']}. Hits: {summary['hits']}. Explained: {summary['explained']}. False alarms: {summary['false_alarms']}.",
              "Surprises: " + ("; ".join(summary["surprises"]) or "none") + "."]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate"); g.add_argument("--out", default="out/detection-test"); g.add_argument("--seed", type=int, default=7)
    c = sub.add_parser("check"); c.add_argument("--data", default="out/detection-test")
    s = sub.add_parser("score"); s.add_argument("--data", default="out/detection-test"); s.add_argument("--anomalies", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "generate":
        generate(a.out, a.seed)
        return
    df, plan = load_data(a.data), load_plan()
    if a.cmd == "check":
        print(f"{len(df):,} authorizations, {df['hour'].nunique()} hours, {FIRST_DAY:%b %d} to {LAST_DAY:%b %d}")
        for name in ("I017",):
            print(f"{name} is {df.loc[df['issuer_id'] == name, 'issuer_name'].iloc[0]}")
        for row in check(df, plan):
            print(" | ".join(row))
        return
    out, summary = score_flags(load_flags(a.anomalies), df, plan)
    print(markdown(out, summary, checks_made(df)))


if __name__ == "__main__":
    main()
