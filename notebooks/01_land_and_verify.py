# Databricks notebook source
base = "/Volumes/workspace/payments/landing"

auths = spark.read.parquet(f"{base}/authorizations")   # a folder: Spark reads every part file in it
print("authorizations:", auths.count())                 # expect 2,000,000
auths.printSchema()

# COMMAND ----------

base = "/Volumes/workspace/payments/landing"

chargebacks = spark.read.parquet(f"{base}/chargebacks")   # a folder: Spark reads every part file in it
print("chargebacks:", chargebacks.count())                 # expect 7,497
chargebacks.printSchema()

# COMMAND ----------

base = "/Volumes/workspace/payments/landing"

merchants = spark.read.parquet(f"{base}/merchants.parquet")   # a file: Spark reads the file
print("merchants:", merchants.count())                 # expect 800
merchants.printSchema()

# COMMAND ----------

base = "/Volumes/workspace/payments/landing"

issuers = spark.read.parquet(f"{base}/issuers.parquet")   # a file: Spark reads the file
print("issuers:", issuers.count())                 # expect 40
issuers.printSchema()

# COMMAND ----------

from pyspark.sql import functions as F

auth_m = auths.join(merchants.select("merchant_id", "region", "mcc_description"), on="merchant_id", how="left")

q1 = (auth_m
      .withColumn("approved", F.when(F.col("response_code") == "00", 1).otherwise(0))
      .groupBy("region")
      .agg(F.count("*").alias("auths"),
           F.avg("approved").alias("approval_rate"))
      .orderBy("approval_rate"))

display(q1)

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import Window

# Declines = authorizations that were not approved (response_code != "00")
declines = auths.filter(F.col("response_code") != "00")

# Top 5 decline codes overall
top_overall = (declines
               .groupBy("response_code")
               .agg(F.count("*").alias("decline_count"))
               .orderBy(F.desc("decline_count"))
               .limit(5))

display(top_overall)

# Top 5 decline codes by channel
window = F.row_number().over(
    Window.partitionBy("channel").orderBy(F.desc("decline_count")))

top_by_channel = (declines
                  .groupBy("channel", "response_code")
                  .agg(F.count("*").alias("decline_count"))
                  .withColumn("rank", window)
                  .filter(F.col("rank") <= 5)
                  .orderBy("channel", "rank"))

display(top_by_channel)

# COMMAND ----------

from pyspark.sql import functions as F

auth_r = auths.join(merchants.select("merchant_id", "region"), on="merchant_id", how="left")

p95 = (auth_r
       .groupBy("region")
       .agg(F.percentile_approx("latency_ms", 0.95).alias("p95_latency_ms"),
            F.count("*").alias("auths"))
       .orderBy(F.desc("p95_latency_ms")))

display(p95)

# COMMAND ----------

from pyspark.sql import functions as F

q = (auth_m
      .withColumn("approved", F.when(F.col("response_code") == "00", 1).otherwise(0))
      .groupBy("mcc_description")
      .agg(F.count("*").alias("auths"),
           F.avg("approved").alias("approval_rate"))
      .orderBy("approval_rate"))

display(q2)


# COMMAND ----------

q.explain(mode="formatted")