"""Gold layer: the summary tables the ops team (and later the Claude agent) read.

PAYOPS-10 to 13. All materialized views over silver, recomputed each run:
  gold_daily_approval      approval rate by day, region, channel, tokenized
  gold_decline_reasons     declines by day, region, issuer, response code, with share of the day's declines
  gold_declines_by_category  declines by day, merchant category, channel, response code
  gold_latency_hourly      p50 / p95 / p99 authorization latency by hour and region
  gold_chargebacks_weekly  chargebacks by week filed, merchant category and reason
  gold_anomalies           unusual approval drops, decline spikes and latency spikes (PAYOPS-56)

Each keeps the dimensions an analyst would slice by, so questions like "why did approvals drop in
the UK on Sep 17" can be answered from gold without going back to silver.
"""
from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F

# Anomaly thresholds. Each value is compared with the median of the same series over the previous
# 14 days, which a multi-day incident can't drag up the way an average would.
BASELINE_DAYS = 14
MIN_BASELINE_DAYS = 7           # no flags until a series has this much history
APPROVAL_DROP_Z = 4.0           # standard errors below baseline, given that day's volume
DECLINE_SPIKE_Z = 5.0           # (declines - baseline) / sqrt(baseline), with counts treated as Poisson
DECLINE_SPIKE_MIN_EXCESS = 25   # extra declines that day, so tiny series can't flag on a few declines
LATENCY_SPIKE_RATIO = 2.0       # hourly p95 as a multiple of baseline


@dp.materialized_view(comment="Daily approval rate by region, channel and tokenization (synthetic data).")
def gold_daily_approval():
    return (spark.read.table("silver_authorizations")
            .groupBy("event_date", "region", "channel", "is_tokenized")
            .agg(F.count("*").alias("auths"),
                 F.sum(F.col("is_approved").cast("int")).alias("approved"),
                 F.sum(F.when(~F.col("is_approved"), F.col("amount")).otherwise(0)).alias("declined_amount"))
            .withColumn("approval_rate", F.round(F.col("approved") / F.col("auths"), 4)))


@dp.materialized_view(comment="Declines by day, region, issuer and response code, with each row's share of that day and region's declines.")
def gold_decline_reasons():
    declines = (spark.read.table("silver_authorizations")
                .filter(~F.col("is_approved"))
                .groupBy("event_date", "region", "issuer_id", "issuer_name", "response_code")
                .agg(F.count("*").alias("declines")))
    day_region = Window.partitionBy("event_date", "region")
    return declines.withColumn(
        "share_of_declines", F.round(F.col("declines") / F.sum("declines").over(day_region), 6))


@dp.materialized_view(comment="Declines by day, merchant category, channel and response code.")
def gold_declines_by_category():
    # Added in Sprint 3: finding INC-3 by hand needed merchant category, which no other gold table kept.
    return (spark.read.table("silver_authorizations")
            .filter(~F.col("is_approved"))
            .groupBy("event_date", "mcc", "mcc_description", "channel", "response_code")
            .agg(F.count("*").alias("declines")))


@dp.materialized_view(comment="Authorization latency percentiles by hour and region.")
def gold_latency_hourly():
    pct = F.percentile_approx("latency_ms", F.array(F.lit(0.5), F.lit(0.95), F.lit(0.99)))
    return (spark.read.table("silver_authorizations")
            .groupBy("event_hour", "region")
            .agg(F.count("*").alias("auths"), pct.alias("_p"))
            .select("event_hour", "region", "auths",
                    F.col("_p")[0].alias("p50_latency_ms"),
                    F.col("_p")[1].alias("p95_latency_ms"),
                    F.col("_p")[2].alias("p99_latency_ms")))


@dp.materialized_view(comment="Chargebacks by week filed, merchant category and reason.")
def gold_chargebacks_weekly():
    merchant_of_auth = spark.read.table("silver_authorizations").select("auth_id", "mcc", "mcc_description")
    return (spark.read.table("bronze_chargebacks")
            .join(merchant_of_auth, "auth_id", "left")
            .withColumn("week_start", F.to_date(F.date_trunc("week", "filed_ts")))
            .groupBy("week_start", "mcc", "mcc_description", "reason")
            .agg(F.count("*").alias("chargebacks"),
                 F.round(F.sum("amount"), 2).alias("chargeback_amount")))


def _with_daily_baseline(df):
    """Add baseline (median of `value` over the previous 14 days of this entity) and days of history."""
    window = (Window.partitionBy("entity").orderBy(F.expr("unix_date(event_date)"))
              .rangeBetween(-BASELINE_DAYS, -1))
    return (df.withColumn("baseline", F.expr("percentile(value, 0.5)").over(window))
            .withColumn("history", F.count("value").over(window))
            .filter(F.col("history") >= MIN_BASELINE_DAYS))


def _anomaly_rows(df, detector, scope, metric):
    return df.select(F.lit(detector).alias("detector"), F.lit(scope).alias("scope"), "entity",
                     F.lit(metric).alias("metric"), F.col("period_start").cast("timestamp").alias("period_start"),
                     F.col("value").cast("double").alias("observed"), F.col("baseline").cast("double").alias("baseline"),
                     F.round("score", 2).alias("score"))


def _complete_days():
    """Days that have all 24 hours in the data, so a day still arriving isn't scored against full days."""
    return (spark.read.table("gold_latency_hourly")
            .select(F.to_date("event_hour").alias("event_date"), "event_hour").distinct()
            .groupBy("event_date").agg(F.count("*").alias("hours"))
            .filter(F.col("hours") == 24)
            .select("event_date"))


def _approval_drops(column, scope):
    daily = (spark.read.table("silver_authorizations")
             .groupBy(F.col(column).alias("entity"), "event_date")
             .agg(F.count("*").alias("auths"), F.sum(F.col("is_approved").cast("int")).alias("approved"))
             .join(_complete_days(), "event_date")
             .withColumn("value", F.col("approved") / F.col("auths")))
    return _anomaly_rows(
        _with_daily_baseline(daily)
        .withColumn("score", (F.col("baseline") - F.col("value"))
                    / F.sqrt(F.col("baseline") * (1 - F.col("baseline")) / F.col("auths")))
        .filter(F.col("score") >= APPROVAL_DROP_Z)
        .withColumnRenamed("event_date", "period_start"),
        "approval_drop", scope, "approval_rate")


def _decline_spikes(table, keys, scope):
    declines = spark.read.table(table).join(_complete_days(), "event_date")
    counts = declines.groupBy("event_date", *keys).agg(F.sum("declines").alias("value"))
    # A day with no declines has no row, so fill in zeros or the baseline would skip quiet days.
    every_day = (declines.select("event_date").distinct()
                 .crossJoin(declines.select(*keys).distinct()))
    filled = (every_day.join(counts, ["event_date", *keys], "left")
              .withColumn("value", F.coalesce(F.col("value"), F.lit(0)))
              .withColumn("entity", F.concat_ws(" / ", *keys)))
    return _anomaly_rows(
        _with_daily_baseline(filled)
        .withColumn("score", (F.col("value") - F.col("baseline")) / F.sqrt(F.greatest(F.col("baseline"), F.lit(1))))
        .filter((F.col("score") >= DECLINE_SPIKE_Z)
                & (F.col("value") - F.col("baseline") >= DECLINE_SPIKE_MIN_EXCESS))
        .withColumnRenamed("event_date", "period_start"),
        "decline_spike", scope, "declines")


def _latency_spikes():
    window = (Window.partitionBy("entity").orderBy(F.unix_timestamp("period_start"))
              .rangeBetween(-BASELINE_DAYS * 86400, -3600))
    hourly = (spark.read.table("gold_latency_hourly")
              .select(F.col("region").alias("entity"), F.col("event_hour").alias("period_start"),
                      F.col("p95_latency_ms").alias("value")))
    return _anomaly_rows(
        hourly.withColumn("baseline", F.expr("percentile(value, 0.5)").over(window))
        .withColumn("history", F.count("value").over(window))
        .filter(F.col("history") >= MIN_BASELINE_DAYS * 24)
        .withColumn("score", F.col("value") / F.col("baseline"))
        .filter(F.col("score") >= LATENCY_SPIKE_RATIO),
        "latency_spike", "region", "p95_latency_ms")


@dp.materialized_view(comment="Unusual approval drops, decline spikes and latency spikes compared with the previous 14 days.")
def gold_anomalies():
    return (_approval_drops("region", "region")
            .unionByName(_approval_drops("issuer_name", "issuer"))
            .unionByName(_decline_spikes("gold_decline_reasons", ["issuer_name", "response_code"], "issuer_and_code"))
            .unionByName(_decline_spikes("gold_declines_by_category", ["mcc_description", "channel", "response_code"],
                                         "category_channel_and_code"))
            .unionByName(_latency_spikes()))
