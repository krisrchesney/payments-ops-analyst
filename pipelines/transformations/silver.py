"""Silver layer: cleaned card authorizations, ready for reporting.

PAYOPS-9. One table, silver_authorizations:
  - one row per auth_id (duplicates removed, earliest-loaded copy kept)
  - is_approved, event_date, event_hour added
  - merchant details (name, MCC, region) and issuer details joined in
  - three data quality rules drop bad rows; the dropped counts show in the pipeline UI
"""
from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F

# ISO 8583-style response codes the generator can produce. Anything else is invalid.
KNOWN_CODES = ("00", "05", "51", "54", "14", "59", "91")
KNOWN_CODES_SQL = ", ".join(f"'{c}'" for c in KNOWN_CODES)

QUALITY_RULES = {
    "positive_amount": "amount > 0",
    "known_response_code": f"response_code IN ({KNOWN_CODES_SQL})",
    "known_merchant": "merchant_id IS NOT NULL AND mcc IS NOT NULL",
}


@dp.materialized_view(comment="Cleaned card authorizations: deduplicated, enriched, quality-checked (synthetic data).")
@dp.expect_all_or_drop(QUALITY_RULES)
def silver_authorizations():
    auths = spark.read.table("bronze_authorizations")

    # Keep one row per auth_id: the copy that was loaded first.
    first_copy = Window.partitionBy("auth_id").orderBy("_ingested_at", "_source_file")
    deduped = (auths
               .withColumn("_copy", F.row_number().over(first_copy))
               .filter("_copy = 1")
               .drop("_copy"))

    merchants = spark.read.table("bronze_merchants").select(
        "merchant_id", "merchant_name", "mcc", "mcc_description", "region")
    issuers = spark.read.table("bronze_issuers").select(
        "issuer_id", "issuer_name", F.col("home_region").alias("issuer_home_region"))

    return (deduped
            .join(merchants, "merchant_id", "left")
            .join(issuers, "issuer_id", "left")
            .withColumn("is_approved", F.col("response_code") == "00")
            .withColumn("event_date", F.to_date("event_ts"))
            .withColumn("event_hour", F.date_trunc("hour", "event_ts")))
