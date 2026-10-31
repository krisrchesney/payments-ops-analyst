"""Bronze layer: raw data from the landing volume, as it arrived, plus where and when.

PAYOPS-24. Four tables:
  bronze_authorizations  streaming table (Auto Loader picks up new files each run)
  bronze_chargebacks     streaming table (same)
  bronze_merchants       materialized view (one small file, reread each run)
  bronze_issuers         materialized view (same)
"""
from pyspark import pipelines as dp
from pyspark.sql import functions as F

# /Volumes/workspace/payments/landing, set in resources/payments_ops.pipeline.yml
LANDING = spark.conf.get("landing_path")


def _with_lineage(df):
    """Add when each row was loaded and which file it came from."""
    return (df
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source_file", F.col("_metadata.file_path")))


def _auto_loader(folder):
    """Stream a landing folder with Auto Loader: all files on the first run, only new files after."""
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "parquet")
            .load(f"{LANDING}/{folder}"))


@dp.table(comment="Raw card authorizations, as landed (synthetic data).")
def bronze_authorizations():
    return _with_lineage(_auto_loader("authorizations"))


@dp.table(comment="Raw chargebacks, as landed (synthetic data).")
def bronze_chargebacks():
    return _with_lineage(_auto_loader("chargebacks"))


@dp.materialized_view(comment="Merchant reference list, reread from its single file each run.")
def bronze_merchants():
    return _with_lineage(spark.read.parquet(f"{LANDING}/merchants.parquet"))


@dp.materialized_view(comment="Issuer reference list, reread from its single file each run.")
def bronze_issuers():
    return _with_lineage(spark.read.parquet(f"{LANDING}/issuers.parquet"))
