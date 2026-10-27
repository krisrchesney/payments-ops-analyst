import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "generator"))
import generate_auths  # noqa: E402


def test_small_run(tmp_path):
    generate_auths.main(["--rows", "60000", "--chunk", "25000", "--days", "10", "--out", str(tmp_path)])
    auths = pd.read_parquet(tmp_path / "authorizations")
    assert len(auths) == 60000
    assert auths["auth_id"].is_unique
    approval = (auths["response_code"] == "00").mean()
    assert 0.88 < approval < 0.97

    incidents = json.loads((tmp_path / "incidents.json").read_text())
    outage = next(i for i in incidents if i["type"] == "issuer_outage")
    ts = pd.to_datetime(auths["event_ts"], utc=True)
    win = (ts >= pd.Timestamp(outage["start"])) & (ts < pd.Timestamp(outage["end"])) & (auths["issuer_id"] == outage["issuer_id"])
    assert (auths.loc[win, "response_code"] == "91").mean() > 0.6

    cb = pd.read_parquet(tmp_path / "chargebacks")
    assert cb["auth_id"].isin(auths["auth_id"]).all()
    assert cb["chargeback_id"].is_unique
