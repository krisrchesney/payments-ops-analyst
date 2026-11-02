"""Docs layer: the ops library, split into sections the agent can search (RAG).

PAYOPS-61. One table:
  docs_chunks  materialized view, one row per "## " section of each document in landing/docs/

Vector Search reads this table, so it needs a stable key (chunk_id) and has no load timestamp:
a value that changes every run would make every section look edited and get embedded again.
"""
from pyspark import pipelines as dp
from pyspark.sql import functions as F

# /Volumes/workspace/payments/landing, set in resources/payments_ops.pipeline.yml
LANDING = spark.conf.get("landing_path")


@dp.materialized_view(
    comment="Ops library sections for runbook search (synthetic documents).",
    # Both are needed for a Vector Search Delta Sync index to read a materialized view's changes.
    table_properties={"pipelines.externalMetadata.enabled": "true",
                      "delta.enableChangeDataFeed": "true"})
@dp.expect_or_fail("section_has_text", "length(text) > length(doc_title)")
# Guards a bug from the first run: "." matched line breaks here, so every section held the whole document.
@dp.expect_or_fail("labels_are_one_line", "instr(doc_title, char(10)) = 0 AND instr(heading, char(10)) = 0")
def docs_chunks():
    # wholetext: one row per file, not one per line
    files = (spark.read.format("text").option("wholetext", True).load(f"{LANDING}/docs")
             .select(F.col("_metadata.file_name").alias("source_file"),
                     F.regexp_replace("value", "\r", "").alias("raw")))
    sections = (files
                .withColumn("doc_title", F.regexp_extract("raw", r"(?m)^# ([^\n]+)", 1))
                .select("source_file", "doc_title",
                        F.posexplode(F.split("raw", r"(?m)^## ")).alias("section_number", "part"))
                # Part 0 is whatever comes before the first "## ": the title and the "Synthetic document" line.
                .filter(F.col("section_number") > 0))
    return sections.select(
        F.format_string("%s#%02d", F.col("source_file"), F.col("section_number")).alias("chunk_id"),
        "source_file",
        "doc_title",
        "section_number",
        F.regexp_extract("part", r"^([^\n]*)", 1).alias("heading"),
        # Keep the document title with the text, so a section like "Lessons" still says what it is about.
        F.concat_ws("\n", F.col("doc_title"), F.trim(F.col("part"))).alias("text"))
