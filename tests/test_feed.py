import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "generator"))
import feed_hour  # noqa: E402
import generate_auths  # noqa: E402

ROWS = 3000


@pytest.fixture
def landing(tmp_path):
    """A landing folder with just the reference files, like the volume before the feed starts."""
    from faker import Faker
    fake = Faker()
    Faker.seed(1)
    merchants, issuers = generate_auths.build_dims(np.random.default_rng(1), fake, n_merchants=50, n_issuers=8)
    merchants.to_parquet(tmp_path / "merchants.parquet", index=False)
    issuers.to_parquet(tmp_path / "issuers.parquet", index=False)
    return tmp_path


def run(landing, hours=1):
    feed_hour.main(["--landing", str(landing), "--hours", str(hours), "--rows-per-hour", str(ROWS)])


def feed_files(landing):
    return sorted((landing / "authorizations").glob("feed-*.parquet"))


def test_first_run_writes_one_exact_hour(landing):
    run(landing)
    [file] = feed_files(landing)
    assert file.name == "feed-2026-09-29T00.parquet"
    df = pd.read_parquet(file)
    assert len(df) == ROWS
    assert df["auth_id"].is_unique
    ts = pd.to_datetime(df["event_ts"], utc=True)
    assert ts.min() >= pd.Timestamp("2026-09-29 00:00", tz="UTC")
    assert ts.max() < pd.Timestamp("2026-09-29 01:00", tz="UTC")


def test_clock_continues_and_never_rewrites_an_hour(landing):
    run(landing)
    first = pd.read_parquet(feed_files(landing)[0])
    run(landing, hours=2)
    files = feed_files(landing)
    assert [f.name for f in files] == [f"feed-2026-09-29T0{h}.parquet" for h in range(3)]
    assert pd.read_parquet(files[0]).equals(first)
    ids = pd.concat([pd.read_parquet(f)["auth_id"] for f in files])
    assert ids.is_unique
    assert not ids.isin([f"A{i:010d}" for i in range(0, 2_000_000, 50_000)]).any()


def test_same_hour_comes_out_the_same(landing, tmp_path_factory):
    other = tmp_path_factory.mktemp("other")
    for name in ("merchants.parquet", "issuers.parquet"):
        (other / name).write_bytes((landing / name).read_bytes())
    run(landing)
    run(other)
    assert pd.read_parquet(feed_files(landing)[0]).equals(pd.read_parquet(feed_files(other)[0]))


def test_planted_incident_only_touches_its_hours(landing):
    issuer = pd.read_parquet(landing / "issuers.parquet")["issuer_id"].iloc[0]
    plan = [{"id": "TEST", "type": "issuer_outage", "issuer_id": issuer, "hit_rate": 1.0,
             "start": "2026-09-29T01:00:00", "end": "2026-09-29T02:00:00"}]
    (landing / "feed").mkdir()
    (landing / "feed" / "incidents.json").write_text(json.dumps(plan))
    run(landing, hours=3)
    before, during, after = (pd.read_parquet(f) for f in feed_files(landing))
    hit = during[during["issuer_id"] == issuer]
    assert len(hit) > 0 and (hit["response_code"] == "91").all()
    assert (before.loc[before["issuer_id"] == issuer, "response_code"] == "91").mean() < 0.1
    assert (after.loc[after["issuer_id"] == issuer, "response_code"] == "91").mean() < 0.1


def test_incident_strength_can_be_set(landing):
    plan = [{"id": "TEST", "type": "latency_spike", "region": "UK", "latency_multiplier": 3,
             "start": "2026-09-29T00:00:00+00:00", "end": "2026-09-29T01:00:00+00:00"}]
    (landing / "feed").mkdir()
    (landing / "feed" / "incidents.json").write_text(json.dumps(plan))
    run(landing, hours=2)
    first, second = (pd.read_parquet(f) for f in feed_files(landing))
    merchants = pd.read_parquet(landing / "merchants.parquet").set_index("merchant_id")["region"]
    uk = lambda df: df["merchant_id"].map(merchants) == "UK"  # noqa: E731
    ratio = first.loc[uk(first), "latency_ms"].median() / second.loc[uk(second), "latency_ms"].median()
    assert 2.4 < ratio < 3.6


@pytest.mark.parametrize("plan, message", [
    ([{"type": "meteor", "start": "2026-09-29T01", "end": "2026-09-29T02"}], "unknown incident type"),
    ([{"type": "latency_spike", "start": "2026-09-29T01", "end": "2026-09-29T02"}], "needs 'region'"),
])
def test_bad_plan_is_rejected(landing, plan, message):
    (landing / "feed").mkdir()
    (landing / "feed" / "incidents.json").write_text(json.dumps(plan))
    with pytest.raises(ValueError, match=message):
        run(landing)
    assert feed_files(landing) == []
