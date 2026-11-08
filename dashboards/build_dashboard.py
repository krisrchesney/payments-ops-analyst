"""Builds dashboards/payments_ops_monitor.lvdash.json (PAYOPS-57).

The dashboard JSON is long and repetitive, so it is generated from this file and kept next to it. Run
  python dashboards/build_dashboard.py
after editing, then deploy with the bundle. Queries use bare table names: the bundle supplies the catalog and schema
(dataset_catalog and dataset_schema in resources/payments_ops.dashboard.yml). All data is synthetic.
"""
import json
from pathlib import Path

OUT = Path(__file__).with_name("payments_ops_monitor.lvdash.json")

LATEST_DAY_CTE = (
    "WITH complete AS (SELECT CAST(event_hour AS DATE) AS d FROM gold_latency_hourly "
    "GROUP BY CAST(event_hour AS DATE) HAVING COUNT(DISTINCT event_hour) = 24), "
    "latest AS (SELECT MAX(d) AS day FROM complete) "
)

# dataset name -> (display name, SQL, has a date column the date filter can bind to)
DATASETS = {
    "ds_kpi": ("Latest complete day", LATEST_DAY_CTE +
               "SELECT l.day AS latest_day, "
               "(SELECT SUM(approved) * 1.0 / SUM(auths) FROM gold_daily_approval WHERE event_date = l.day) AS approval_rate, "
               "(SELECT SUM(declines) FROM gold_decline_reasons WHERE event_date = l.day) AS declines, "
               "(SELECT COUNT(*) FROM gold_anomalies WHERE CAST(period_start AS DATE) = l.day) AS flags_latest_day, "
               "(SELECT COUNT(*) FROM gold_anomalies WHERE CAST(period_start AS DATE) > date_sub(l.day, 7)) AS flags_last_7_days "
               "FROM latest l", False),
    "ds_day": ("Approval rate by day",
               "SELECT event_date, SUM(auths) AS auths, SUM(approved) AS approved, SUM(approved) * 1.0 / SUM(auths) AS approval_rate "
               "FROM gold_daily_approval GROUP BY event_date ORDER BY event_date", True),
    "ds_declines": ("Declines by response code",
                    "SELECT event_date, response_code, SUM(declines) AS declines FROM gold_decline_reasons "
                    "GROUP BY event_date, response_code ORDER BY event_date", True),
    "ds_latency": ("Peak latency by region",
                   "SELECT CAST(event_hour AS DATE) AS event_date, region, MAX(p95_latency_ms) AS peak_p95_ms FROM gold_latency_hourly "
                   "GROUP BY CAST(event_hour AS DATE), region ORDER BY event_date", True),
    "ds_flags": ("Flags",
                 "SELECT CAST(period_start AS DATE) AS event_date, period_start, detector, entity, observed, baseline, score "
                 "FROM gold_anomalies ORDER BY period_start DESC, score DESC", True),
}


def field(name, expr=None):
    return {"name": name, "expression": expr or f"`{name}`"}


def widget(name, dataset, fields, spec, disaggregated=True, qname="main_query"):
    return {"name": name,
            "queries": [{"name": qname, "query": {"datasetName": dataset, "fields": fields, "disaggregated": disaggregated}}],
            "spec": spec}


def counter(name, title, column, fmt=None):
    enc = {"fieldName": column, "displayName": title}
    if fmt:
        enc["format"] = fmt
    return widget(name, "ds_kpi", [field(column)], {"version": 2, "widgetType": "counter", "encodings": {"value": enc},
                                                    "frame": {"title": title, "showTitle": True}})


def place(w, x, y, width, height):
    return {"widget": w, "position": {"x": x, "y": y, "width": width, "height": height}}


def build():
    datasets = [{"name": n, "displayName": d, "queryLines": [sql + " "]} for n, (d, sql, _) in DATASETS.items()]
    header = {"name": "header", "multilineTextboxSpec": {"lines": [
        "# Payments ops monitor\n",
        "Approvals, declines, latency and the flags raised by `gold_anomalies`. All data is simulated. The four numbers below describe the latest day with all 24 hours in the data.\n"]}}
    pct = {"type": "number-percent", "decimalPlaces": {"type": "max", "places": 2}}
    approval = widget("approval-trend", "ds_day", [field("event_date"), field("approval_rate")], {
        "version": 3, "widgetType": "line",
        "encodings": {"x": {"fieldName": "event_date", "scale": {"type": "temporal"}, "displayName": "Day"},
                      "y": {"fieldName": "approval_rate", "scale": {"type": "quantitative"}, "displayName": "Approval rate",
                            "format": pct}},
        "frame": {"title": "Approval rate by day", "showTitle": True}})
    declines = widget("declines-by-code", "ds_declines", [field("event_date"), field("response_code"), field("declines")], {
        "version": 3, "widgetType": "bar",
        "encodings": {"x": {"fieldName": "event_date", "scale": {"type": "temporal"}, "displayName": "Day"},
                      "y": {"fieldName": "declines", "scale": {"type": "quantitative"}, "displayName": "Declines"},
                      "color": {"fieldName": "response_code", "scale": {"type": "categorical"}, "displayName": "Response code"}},
        "frame": {"title": "Declines by response code", "showTitle": True}})
    latency = widget("latency-by-region", "ds_latency", [field("event_date"), field("region"), field("peak_p95_ms")], {
        "version": 3, "widgetType": "line",
        "encodings": {"x": {"fieldName": "event_date", "scale": {"type": "temporal"}, "displayName": "Day"},
                      "y": {"fieldName": "peak_p95_ms", "scale": {"type": "quantitative"}, "displayName": "Highest hourly p95 (ms)"},
                      "color": {"fieldName": "region", "scale": {"type": "categorical"}, "displayName": "Region"}},
        "frame": {"title": "Slowest hour of each day, by region (p95 latency)", "showTitle": True}})
    cols = [("period_start", "When"), ("detector", "Check"), ("entity", "Series"), ("observed", "Observed"),
            ("baseline", "Baseline"), ("score", "Score")]
    flags = widget("flags-table", "ds_flags", [field(c) for c, _ in cols], {
        "version": 2, "widgetType": "table",
        "encodings": {"columns": [{"fieldName": c, "displayName": d} for c, d in cols]},
        "frame": {"title": "Flags raised by gold_anomalies, newest first", "showTitle": True}})
    main = {"name": "overview", "displayName": "Overview", "pageType": "PAGE_TYPE_CANVAS", "layoutVersion": "GRID_V1", "layout": [
        place(header, 0, 0, 12, 2),
        place(counter("kpi-approval", "Approval rate, latest day", "approval_rate", pct), 0, 2, 3, 3),
        place(counter("kpi-declines", "Declines, latest day", "declines"), 3, 2, 3, 3),
        place(counter("kpi-flags-day", "Flags, latest day", "flags_latest_day"), 6, 2, 3, 3),
        place(counter("kpi-flags-week", "Flags, last 7 days", "flags_last_7_days"), 9, 2, 3, 3),
        place(approval, 0, 5, 6, 5), place(declines, 6, 5, 6, 5),
        place(latency, 0, 10, 12, 5),
        place(flags, 0, 15, 12, 6)]}
    date_queries = [{"name": f"q_{n}", "query": {"datasetName": n, "fields": [field("event_date")], "disaggregated": False}}
                    for n, (_, _, dated) in DATASETS.items() if dated]
    date_filter = {"name": "filter-date", "queries": date_queries, "spec": {
        "version": 2, "widgetType": "filter-date-range-picker",
        "encodings": {"fields": [{"fieldName": "event_date", "queryName": q["name"]} for q in date_queries]},
        "frame": {"showTitle": True, "title": "Date range"}}}
    filters = {"name": "filters", "displayName": "Filters", "pageType": "PAGE_TYPE_GLOBAL_FILTERS", "layoutVersion": "GRID_V1",
               "layout": [place(date_filter, 0, 0, 4, 2)]}
    theme = {"canvasBackgroundColor": {"light": "#FCFCFC", "dark": "#1F272D"}, "widgetBackgroundColor": {"light": "#FFFFFF", "dark": "#11171C"},
             "fontColor": {"light": "#11171C", "dark": "#E8ECF0"}, "selectionColor": {"light": "#2272B4", "dark": "#8ACAFF"},
             "visualizationColors": ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#56B4E9", "#7A7A7A", "#F0E442"],
             "widgetHeaderAlignment": "LEFT"}
    return {"datasets": datasets, "pages": [main, filters], "uiSettings": {"theme": theme}}


if __name__ == "__main__":
    OUT.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT)
