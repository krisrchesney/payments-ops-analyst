"""Tests for the MCP server tools, run against a tiny fake set of gold tables (no Databricks needed)."""
import importlib
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_server"))


@pytest.fixture()
def server(tmp_path, monkeypatch):
    d1, d2, d3 = date(2026, 9, 1), date(2026, 9, 2), date(2026, 9, 3)
    pd.DataFrame({
        "event_date": [d1, d2, d3], "region": ["UK"] * 3, "channel": ["ecommerce"] * 3, "is_tokenized": [False] * 3,
        "auths": [100, 100, 100], "approved": [95, 95, 80], "declined_amount": [5.0, 5.0, 20.0], "approval_rate": [0.95, 0.95, 0.80],
    }).to_parquet(tmp_path / "gold_daily_approval.parquet")
    pd.DataFrame({
        "event_date": [d1, d2, d3, d3], "region": ["UK"] * 4, "issuer_id": ["I001"] * 4, "issuer_name": ["Test Bank"] * 4,
        "response_code": ["05", "05", "05", "91"], "declines": [5, 5, 5, 10], "share_of_declines": [1.0, 1.0, 0.33, 0.67],
    }).to_parquet(tmp_path / "gold_decline_reasons.parquet")
    pd.DataFrame({
        "event_date": [d1, d2, d3], "mcc": ["5732"] * 3, "mcc_description": ["Electronics"] * 3,
        "channel": ["ecommerce"] * 3, "response_code": ["59"] * 3, "declines": [1, 1, 12],
    }).to_parquet(tmp_path / "gold_declines_by_category.parquet")
    pd.DataFrame({
        "event_hour": [datetime(2026, 9, 3, h, tzinfo=timezone.utc) for h in range(3)], "region": ["UK"] * 3,
        "auths": [10, 10, 10], "p50_latency_ms": [100, 100, 900], "p95_latency_ms": [300, 300, 2000], "p99_latency_ms": [400, 400, 2500],
    }).to_parquet(tmp_path / "gold_latency_hourly.parquet")
    pd.DataFrame({
        "week_start": [d1], "mcc": ["5732"], "mcc_description": ["Electronics"], "reason": ["fraud"],
        "chargebacks": [3], "chargeback_amount": [100.0],
    }).to_parquet(tmp_path / "gold_chargebacks_weekly.parquet")
    monkeypatch.setenv("PAYOPS_EXPORTS", str(tmp_path))
    import server as s
    s = importlib.reload(s)   # pick up the new PAYOPS_EXPORTS and a fresh database
    return s


def test_list_metrics(server):
    m = server.list_metrics()
    assert m["tables"]["gold_daily_approval"]["row_count"] == 3
    assert m["response_codes"]["91"].startswith("issuer unavailable")


def test_query_gold_reads(server):
    r = server.query_gold("SELECT SUM(auths) AS n FROM gold_daily_approval")
    assert r["rows"] == [{"n": 300}]


@pytest.mark.parametrize("bad", [
    "DROP TABLE gold_daily_approval",
    "SELECT 1; DROP TABLE gold_daily_approval",
    "COPY gold_daily_approval TO 'leak.csv'",
    "INSERT INTO gold_daily_approval SELECT * FROM gold_daily_approval",
    "SELECT * FROM read_csv('C:/Windows/win.ini')",
])
def test_query_gold_blocks_writes_and_file_access(server, bad):
    r = server.query_gold(bad)
    assert "error" in r
    assert server.query_gold("SELECT COUNT(*) AS n FROM gold_daily_approval")["rows"] == [{"n": 3}]


def test_compare_periods_finds_the_drop(server):
    r = server.compare_periods("approval_rate", "region", "2026-09-01", "2026-09-02", "2026-09-03", "2026-09-03")
    assert r["rows"][0] == {"region": "UK", "period_a": 0.95, "period_b": 0.8, "change": -0.15, "pct_change": -15.8}


def test_top_decline_drivers(server):
    r = server.top_decline_drivers("2026-09-03", "2026-09-03", baseline_days=2)
    assert r["by_issuer_and_code"][0]["response_code"] == "91"
    assert r["by_category_channel_and_code"][0]["mcc_description"] == "Electronics"


def test_daily_ops_summary(server):
    r = server.daily_ops_summary("2026-09-03")
    assert r["approval"]["approval_rate"] == 0.8
    assert len(r["latency_spikes"]) == 1


# search_runbooks tests use a fake search, so they need neither Databricks nor a network.
FAKE_ROW = ["fraud-rule-change-log.md#05", "fraud-rule-change-log.md", "FR-2041: Electronics", "Fraud rule change log\nFR-2041", 0.66313]


def test_search_runbooks_returns_sections_to_cite(server, monkeypatch):
    monkeypatch.setattr(server, "_query_index", lambda question, k: [FAKE_ROW])
    r = server.search_runbooks("why were electronics declined?")
    assert r["results"] == [{"chunk_id": "fraud-rule-change-log.md#05", "source_file": "fraud-rule-change-log.md",
                             "heading": "FR-2041: Electronics", "text": "Fraud rule change log\nFR-2041", "score": 0.663}]
    assert r["source"]["question"] == "why were electronics declined?"


@pytest.mark.parametrize("asked, sent", [(3, 3), (0, 1), (500, 10)])
def test_search_runbooks_keeps_k_in_range(server, monkeypatch, asked, sent):
    seen = []
    monkeypatch.setattr(server, "_query_index", lambda question, k: seen.append(k) or [])
    assert server.search_runbooks("anything", k=asked)["results"] == []
    assert seen == [sent]


def test_search_runbooks_rejects_a_blank_question(server, monkeypatch):
    monkeypatch.setattr(server, "_query_index", lambda question, k: pytest.fail("should not search"))
    assert "error" in server.search_runbooks("   ")


def test_search_failure_is_reported_and_gold_tools_still_work(server, monkeypatch):
    def down(question, k):
        raise ConnectionError("cannot reach Databricks\nlong detail")
    monkeypatch.setattr(server, "_query_index", down)
    assert server.search_runbooks("anything") == {"error": "Document search is unavailable: cannot reach Databricks"}
    assert server.query_gold("SELECT COUNT(*) AS n FROM gold_daily_approval")["rows"] == [{"n": 3}]
