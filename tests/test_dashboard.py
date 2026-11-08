import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboards"))
import build_dashboard  # noqa: E402

BUILT = build_dashboard.build()
FILE = ROOT / "dashboards" / "payments_ops_monitor.lvdash.json"


def widgets():
    for page in BUILT["pages"]:
        for item in page["layout"]:
            yield page, item


def test_the_committed_json_is_what_the_script_builds():
    assert json.loads(FILE.read_text(encoding="utf-8")) == BUILT


def test_datasets_use_bare_table_names_and_one_statement():
    for ds in BUILT["datasets"]:
        sql = "".join(ds["queryLines"])
        assert not re.search(r"\bworkspace\.|\bpayments\.", sql), ds["name"]          # the bundle supplies catalog and schema
        assert ";" not in sql, ds["name"]
        assert re.findall(r"\bFROM (\w+)", sql) and all(t.startswith("gold_") for t in re.findall(r"\bFROM (\w+)", sql) if t != "complete" and t != "latest")


COLUMNS = {   # what each dataset's SELECT returns, written out so a renamed alias is caught here
    "ds_kpi": {"latest_day", "approval_rate", "declines", "flags_latest_day", "flags_last_7_days"},
    "ds_day": {"event_date", "auths", "approved", "approval_rate"},
    "ds_declines": {"event_date", "response_code", "declines"},
    "ds_latency": {"event_date", "region", "peak_p95_ms"},
    "ds_flags": {"event_date", "period_start", "detector", "entity", "observed", "baseline", "score"},
}


def bound_names(spec):
    if spec["widgetType"] == "table":
        return {c["fieldName"] for c in spec["encodings"]["columns"]}
    if spec["widgetType"].startswith("filter"):
        return {f["fieldName"] for f in spec["encodings"]["fields"]}
    return {v["fieldName"] for v in spec["encodings"].values() if isinstance(v, dict) and "fieldName" in v}


def test_every_widget_field_is_a_real_dataset_column_and_matches_its_encoding():
    assert {ds["name"] for ds in BUILT["datasets"]} == set(COLUMNS)
    for ds in BUILT["datasets"]:
        sql = "".join(ds["queryLines"])
        for col in COLUMNS[ds["name"]]:
            assert col in re.findall(r"\w+", sql), (ds["name"], col)    # the column really is selected
    for page, item in widgets():
        w = item["widget"]
        if "queries" not in w:
            continue
        for q in w["queries"]:
            names = {f["name"] for f in q["query"]["fields"]}
            assert names <= COLUMNS[q["query"]["datasetName"]], w["name"]
            assert bound_names(w["spec"]) <= names, w["name"]                          # an unmatched name shows "no selected fields"


def test_the_main_page_fills_the_12_column_grid_without_overflow():
    for page in BUILT["pages"]:
        assert page["layoutVersion"] == "GRID_V1"
        assert all(i["position"]["x"] + i["position"]["width"] <= 12 for i in page["layout"])
    rows = {}
    for item in BUILT["pages"][0]["layout"]:
        rows[item["position"]["y"]] = rows.get(item["position"]["y"], 0) + item["position"]["width"]
    assert all(total == 12 for total in rows.values()), rows


def test_date_filter_binds_only_datasets_that_have_a_date_column():
    flt = BUILT["pages"][1]["layout"][0]["widget"]
    bound = {q["query"]["datasetName"] for q in flt["queries"]}
    assert bound == {"ds_day", "ds_declines", "ds_latency", "ds_flags"}        # not ds_kpi: it describes the latest day


def test_alert_and_dashboard_resources_are_consistent():
    alert = (ROOT / "resources" / "payments_ops.alert.yml").read_text(encoding="utf-8")
    assert "GREATER_THAN" in alert and "double_value: 0" in alert and "${workspace.current_user.userName}" in alert
    assert "@" not in re.sub(r"\$\{[^}]*\}", "", alert)                                   # no email address stored in the repo
    dash = (ROOT / "resources" / "payments_ops.dashboard.yml").read_text(encoding="utf-8")
    assert "payments_ops_monitor.lvdash.json" in dash and "dataset_catalog" in dash and "dataset_schema" in dash
    bundle = (ROOT / "databricks.yml").read_text(encoding="utf-8")
    assert "warehouse_id:" in bundle and "lookup:" in bundle
