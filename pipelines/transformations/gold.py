"""Gold layer: the summary tables the ops team (and later the Claude agent) read.

PAYOPS-10 to 13. All materialized views over silver, recomputed each run:
  gold_daily_approval      approval rate by day, region, channel, tokenized
  gold_decline_reasons     declines by day, region, issuer, response code, with share of the day's declines
  gold_declines_by_category  declines by day, merchant category, channel, response code
  gold_latency_hourly      p50 / p95 / p99 authorization latency by hour and region
  gold_chargebacks_weekly  chargebacks by week filed, merchant category and reason

Each keeps the dimensions an analyst would slice by, so questions like "why did approvals drop in
the UK on Sep 17" can be answered from gold without going back to silver.
"""
from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F


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
