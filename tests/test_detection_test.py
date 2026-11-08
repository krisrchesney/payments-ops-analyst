import re
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import detection_test as dtest  # noqa: E402

PLAN = dtest.load_plan()
DAY = pd.Timestamp("2026-10-07")


def rows(n, **over):
    base = dict(issuer_id="I001", issuer_name="Alpha Bank", mcc="5411", mcc_description="Grocery stores", channel="card_present",
                region="US-West", response_code="00", latency_ms=180, event_ts=DAY + pd.Timedelta(hours=9))
    base.update(over)
    return [dict(base) for _ in range(n)]


def frame(*parts):
    df = pd.DataFrame([r for part in parts for r in part])
    df["event_ts"] = pd.to_datetime(df["event_ts"])
    df["day"], df["hour"] = df["event_ts"].dt.normalize(), df["event_ts"].dt.floor("h")
    df["approved"] = df["response_code"] == "00"
    return df


def flag_frame(**f):
    row = dict(detector="approval_drop", scope="region", entity="US-West", metric="approval_rate", period_start=DAY,
               observed=0.9, baseline=0.95, score=7.0)
    row.update(f)
    flags = pd.DataFrame([row])
    flags["period_start"] = pd.to_datetime(flags["period_start"])
    flags["day"] = flags["period_start"].dt.normalize()
    return flags


def test_thresholds_match_the_pipeline():
    """The scorer re-scores with the pipeline's thresholds, so they must not drift apart."""
    gold = (ROOT / "pipelines" / "transformations" / "gold.py").read_text(encoding="utf-8")
    grab = lambda name: float(re.search(rf"^{name}\s*=\s*([\d.]+)", gold, re.M).group(1))  # noqa: E731
    assert (grab("APPROVAL_DROP_Z"), grab("DECLINE_SPIKE_Z"), grab("DECLINE_SPIKE_MIN_EXCESS"), grab("LATENCY_SPIKE_RATIO")) == (
        dtest.APPROVAL_DROP_Z, dtest.DECLINE_SPIKE_Z, dtest.DECLINE_SPIKE_MIN_EXCESS, dtest.LATENCY_SPIKE_RATIO)


def test_the_plan_has_the_four_incidents():
    assert [p["id"] for p in PLAN] == ["TEST-A", "TEST-B", "TEST-C", "TEST-D"]
    assert [p["day"] for p in PLAN] == [pd.Timestamp(d) for d in ("2026-10-03", "2026-10-05", "2026-10-07", "2026-10-09")]


def test_a_flag_that_the_incident_explains_is_marked_explained():
    airlines = rows(50, mcc="4511", mcc_description="Airlines", channel="ecommerce", response_code="59")
    df = frame(rows(900), rows(50, response_code="51"), airlines)       # 1000 requests, 900 approved, 50 from the rule
    out, summary = dtest.score_flags(flag_frame(), df, PLAN)
    assert out.loc[0, "status"] == "explained" and summary["false_alarms"] == 0


def test_a_flag_the_incident_does_not_explain_is_a_false_alarm_even_on_an_incident_day():
    df = frame(rows(900), rows(100, response_code="51"))                  # the declines have nothing to do with the rule
    out, summary = dtest.score_flags(flag_frame(), df, PLAN)
    assert out.loc[0, "status"] == "false alarm" and summary["false_alarms"] == 1


def test_a_flag_on_a_control_day_is_a_false_alarm():
    df = frame(rows(100, event_ts=pd.Timestamp("2026-10-04 09:00")))
    out, _ = dtest.score_flags(flag_frame(period_start=pd.Timestamp("2026-10-04")), df, PLAN)
    assert out.loc[0, "status"] == "false alarm"


def test_hits_and_surprises():
    airlines = rows(10, mcc="4511", mcc_description="Airlines", channel="ecommerce", response_code="59")
    restaurants = rows(10, mcc="5812", mcc_description="Restaurants", channel="ecommerce", response_code="59")
    vance = rows(5, issuer_id="I017", issuer_name="Vance Credit Union")
    de = rows(5, region="DE")
    df = frame(airlines, restaurants, vance, de)
    hit_c = flag_frame(detector="decline_spike", scope="category_channel_and_code", entity="Airlines / ecommerce / 59", period_start="2026-10-07")
    flagged_d = flag_frame(detector="decline_spike", scope="category_channel_and_code", entity="Restaurants / ecommerce / 59", period_start="2026-10-09")
    flags = pd.concat([hit_c, flagged_d], ignore_index=True)
    out, summary = dtest.score_flags(flags, df, PLAN)
    assert summary["hits"]["TEST-C"] == 1 and summary["hits"]["TEST-D"] == 1
    text = " ".join(summary["surprises"])
    assert "TEST-D was flagged" in text                      # D should have been missed
    assert "TEST-A was not caught" in text and "TEST-B was not caught" in text and "TEST-C" not in text


def test_latency_needs_two_of_three_hours():
    de = rows(3, region="DE")
    flags = pd.concat([flag_frame(detector="latency_spike", scope="region", entity="DE", metric="p95_latency_ms",
                                  period_start=f"2026-10-03 {h}:00", observed=500, baseline=200, score=2.5) for h in (14, 15)], ignore_index=True)
    _, summary = dtest.score_flags(flags, frame(de), PLAN)
    assert summary["hits"]["TEST-A"] == 2 and not any("TEST-A" in s for s in summary["surprises"])


def test_target_mask_matches_each_incident_kind():
    df = frame(rows(2, issuer_id="I017", response_code="91"), rows(2, issuer_id="I017"),
               rows(2, mcc="4511", channel="ecommerce", response_code="59"), rows(2, mcc="4511", channel="ecommerce"))
    by_id = {p["id"]: p for p in PLAN}
    assert dtest.target_mask(df, by_id["TEST-B"]).sum() == 2
    assert dtest.target_mask(df, by_id["TEST-C"]).sum() == 2
    assert dtest.target_mask(df, by_id["TEST-A"]).sum() == 0
