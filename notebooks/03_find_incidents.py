# Databricks notebook source
display(spark.sql("""
    SELECT event_date,
           SUM(auths)                               AS auths,
           ROUND(SUM(approved) / SUM(auths) * 100, 2) AS approval_pct
    FROM workspace.payments.gold_daily_approval
    GROUP BY event_date
    ORDER BY approval_pct
    LIMIT 5
"""))

# COMMAND ----------

display(spark.sql("""
    SELECT event_date, region,
           SUM(auths)                               AS auths,
           ROUND(SUM(approved) / SUM(auths) * 100, 2) AS approval_pct
    FROM workspace.payments.gold_daily_approval
    GROUP BY event_date, region
    ORDER BY approval_pct
    LIMIT 10
"""))

# COMMAND ----------

# DBTITLE 1,b
display(spark.sql("""
    SELECT event_date, issuer_name, SUM(declines) AS issuer_unavailable_declines
    FROM workspace.payments.gold_decline_reasons
    WHERE response_code = '91'          -- 91 = issuer unavailable (the bank didn't answer)
    GROUP BY event_date, issuer_name
    ORDER BY issuer_unavailable_declines DESC
    LIMIT 10
"""))

# COMMAND ----------

display(spark.sql("""
    SELECT event_date, response_code,
           SUM(declines) AS declines
    FROM workspace.payments.gold_decline_reasons
    GROUP BY event_date, response_code
    ORDER BY event_date, response_code
"""))

# COMMAND ----------

code, first_day, last_day = "59", "2026-09-22", "2026-09-24"   # <- replace with your answer from cell 4

display(spark.sql(f"""
    SELECT mcc_description, channel, COUNT(*) AS declines
    FROM workspace.payments.silver_authorizations
    WHERE response_code = '{code}'
      AND event_date BETWEEN '{first_day}' AND '{last_day}'
    GROUP BY mcc_description, channel
    ORDER BY declines DESC
    LIMIT 10
"""))