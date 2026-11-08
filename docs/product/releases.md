# Release notes

*A personal project on simulated data. A release here means work finished and checked, not software shipped to customers. Evidence for each item is in the [project summary](../project-summary.md).*

## R5: Detection (in progress, due by November 9, 2026)

**Goal:** flag unusual changes automatically, so a person doesn't have to notice a problem first.

**Added so far**
- A `gold_anomalies` table that flags approval drops, decline spikes and latency spikes against the previous 14 days. Its [thresholds, flags and limits](../detection.md) are written up.
- An hourly feed job that writes the next simulated hour of payments and refreshes the pipeline. It has been run by hand twice (one hour, then 335 hours), and its schedule is paused.
- A [test plan](../detection-test.md) for detection, with predictions and scoring written before the data exists, and a [scorer](../../evals/detection_test.py) that applies it.

**Checked:** all 3 planted incidents were flagged in 21 rows from 15,120 checks, with no flag on a normal day.

**Checked, independent test:** on 4 newly planted incidents with the thresholds unchanged, 2 of the 3 expected catches were made (latency and an Airlines fraud rule), 1 was missed by 2.5 declines (a bank outage, 22.5 extra against a minimum of 25), the incident meant to be missed was missed, and there were no false alarms in 10,080 checks. [Details](../detection.md#the-independent-test).

**Checked, feed:** one run added exactly the new file's 2,976 rows to bronze and silver, and the 21 flags didn't change.

**Still to do:** a run from the schedule, and an alert and dashboard.

**Known limits**
- The first table's thresholds were set knowing the answers. The independent test is small: four incidents, in the same simulator.
- Some flags on incident days are only partly explained by the incident, and could point someone to a bank that has no problem.
- The assistant can't read this table yet.

## R4: Evaluation and launch (November 2, 2026)

**Goal:** measure how well the assistant works, and make the project easy to review.

**Added**
- A [formal evaluation](../eval.md): 12 isolated runs, graded against rules written before any run. 8 of 12 passed.
- A [scope and timeline page](https://krisrchesney.github.io/payments-ops-analyst/roadmap.html) and a read-only [project board](https://krisrchesney.github.io/payments-ops-analyst/board.html).
- These release notes and a [one-page product brief](brief.md).

**Changed**
- Query results now come through Arrow, replacing a pandas call that was being deprecated. Results matched the old path on all 5 reporting tables.
- The tools now return dates as `2026-09-12` instead of `2026-09-12T00:00:00.000`.
- The automated tests now use the current GitHub Actions versions.

**Moved out:** the two-minute demo recording, so detection could come first. No date is set.

**Known limits**
- 2 of the 9 answers to questions that pointed to a problem contained a wrong figure, so answers still need checking.
- Only 1 of 3 runs with no hint found all three planted incidents.

## R3: Document search (November 1 to 2, 2026)

**Goal:** let the assistant explain why a number moved, and cite where the reason came from.

**Added**
- 10 simulated operations documents, including change logs, issuer notices, runbooks and past incident reviews.
- A pipeline step that splits the documents into 52 sections, with data quality rules that stop the pipeline if a section's text or labels come out wrong.
- A Databricks Vector Search index with managed embeddings.
- A sixth read-only tool, `search_runbooks`, which brought the automated tests to 17.
- A public code repository and project page.

**Checked:** in a live check, the expected document was in the top 3 results for 6 of 6 test questions.

**Known limits:** the same author wrote the documents and the test questions, and in one test the right document won by only 0.620 to 0.617.

## R2: AI assistant and daily note (October 31 to November 1, 2026)

**Goal:** let someone ask about the reports in plain English and get an answer that names its numbers.

**Added**
- A local copy of the reporting tables, and a Model Context Protocol server with 5 read-only tools.
- Safeguards: the reports run on an in-memory database with file and network access off, and the SQL tool accepts only a single SELECT.
- A report of declines by merchant category, added because the hand investigation showed it was missing.
- A [drafted daily note](../sample-daily-note-2026-09-23.md) for the operations manager.

**Checked:** the assistant found all three planted incidents, and all 10 figures in the sample note matched the reports.

**Known limits:** it could say what moved, but not why. It had no documents to search until R3.

## R1: Data and reporting pipeline (October 27 to 31, 2026)

**Goal:** produce daily operations reports that an analyst can trust.

**Added**
- A generator for 2 million simulated authorizations and 7,497 chargebacks, with three planted incidents and a separate answer key.
- A Spark pipeline on Databricks, from raw files through bronze, silver and gold tables, deployed from code.
- Daily approval, decline reason and hourly latency reports, plus weekly chargebacks.

**Checked**
- Bronze row counts matched the source files, and each report was checked against a hand-written query or total.
- A test file proved the quality rules: its 10 planted bad rows and 2 duplicates were removed, and its 5 good rows were kept.
- [All three incidents were found by hand](../incidents-by-hand.md) and confirmed against the answer key.

**Known limits:** it covers the cardholder, merchant, issuer and disputes. The acquirer, the network as a separate step, and clearing and settlement aren't modeled.
