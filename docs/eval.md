# Agent evaluation

*All data and documents are synthetic. These rules were written before any evaluation run, and results are reported as they come out.*

**Result: 8 of 12 runs passed on November 2, 2026.** With a question pointing at the incident, all 9 runs found the right incident and cause, and 7 passed once every figure was checked. With no hint, 1 of 3 found all three incidents. [Full results.](#results)

## What this tests

Can the agent find a planted incident from a plain question, name the true cause, cite the right document and get every number right? There is one question for each of the three incidents in the data, plus one question that gives no hint at all. Each question runs 3 times, for 12 runs in total.

## How each run works

- **Fresh session:** each run starts a new Claude Code session with the same question and no memory of earlier runs.
- **Model:** Claude Sonnet 5.5.
- **Tools:** only the agent's 6 read-only tools. Its file, shell and web tools are switched off, and it runs from an empty folder, so it can't read the answer key, the code or the write-ups in this repo. The session's only other instructions are general formatting rules that say nothing about this project.
- **Limit:** 30 turns per run.
- **Saved:** the full answer, the tools called, the time taken and the tokens used.

## The questions

Each question ends with the same request:

> Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

| Incident | The question opens with |
|---|---|
| INC-1 | "Several merchants said more cards than usual were declined on September 12." |
| INC-2 | "Some merchants said card payments felt slow one morning during the week of September 14." |
| INC-3 | "Approval rates looked off during the week of September 21." |
| OPEN (no hint) | "Review September 1 to 28. Is anything unusual, and why?" |

The questions don't name the bank, region, merchant category, response code or cause. INC-3 uses the same wording as the [published sample answer](sample-why-answer-week-of-2026-09-21.md), which doesn't count toward this score.

INC-1 needed a realistic opening because approval that day was only about 0.2 points below normal. Nobody would ask about that dip unless something else had drawn their attention.

## How a run passes

A run passes only if it meets all four rules. Otherwise it fails.

### 1. Found: it names the right incident

| Incident | Required |
|---|---|
| INC-1 | Trujillo Credit Union, code 91 (issuer unavailable), September 12 |
| INC-2 | UK, September 17, the hours starting 09:00 and 10:00 UTC, and p95 latency as the measure that moved |
| INC-3 | Electronics (MCC 5732), ecommerce, code 59 (suspected fraud), September 22 to 24 |

### 2. Cause: it names the true cause and cites the right document

| Incident | Required cause | Required document and section |
|---|---|---|
| INC-1 | The issuer's own host outage | `issuer-status-notices.md`, "Trujillo Credit Union: unplanned host outage (2026-09-12)" |
| INC-2 | The UK gateway connection pool was reduced from 400 to 120, and later restored | `platform-change-log.md`, "CHG-7731: UK gateway connection-pool change (2026-09-17)" |
| INC-3 | The fraud rule tightened on September 22 and was rolled back on September 25 | `fraud-rule-change-log.md`, both "FR-2041" and "FR-2041-RB" |

Blaming a different change or an earlier incident fails this rule. The documents include several that are near the right date or look similar but aren't the cause.

### 3. Numbers: every figure is correct

Every figure in the answer is checked against the gold tables or the cited document.

- A figure stated exactly must match after rounding to the precision given.
- A figure described as "about" must be within 10% of the true value.
- One wrong figure fails the run.

These are the main figures the checks expect:

| Incident | Expected figures |
|---|---|
| INC-1 | 178 code 91 declines at Trujillo on September 12, against about 11 a day from September 5 to 11. Overall approval was 93.60% that day |
| INC-2 | UK p95 of 2,016 ms and 2,084 ms, against a median of 348 ms. UK approval was 93.86% that day, so approvals did not fall |
| INC-3 | 666, 678 and 650 declines a day, against about 8 a day from September 14 to 21 |

### 4. Honesty: it doesn't overclaim

- It states at least one real limit of its evidence.
- It doesn't present a claim as confirmed by the data when only a document supports it. For example, the gold approval and decline tables are daily, so they can't confirm the hour an outage or a rule change started.
- INC-2 only: it says approvals were not affected. Treating this as a decline problem fails the run.

### The no-hint question

An OPEN run passes only if it finds all three incidents and meets the Found, Cause, Numbers and Honesty rules for each. It may also flag other things that look unusual, as long as their numbers are correct and it doesn't claim a cause the evidence doesn't support. Each extra item is listed in the results, so false alarms stay visible.

## Grading

Claude Code grades each run against these rules and reruns each figure as SQL on Databricks. I then review every grade.

- **No retakes:** a failed run stays failed. A run is only repeated if something outside the agent broke, such as Databricks being unreachable, and the report says so.
- **No changing the rules:** if a rule turns out to be wrong after the runs, the original score stays, and any corrected score is shown beside it with the reason.

## Also recorded

These don't affect pass or fail. They come from the [PRD's success metrics](product/PRD.md).

- **Time:** seconds per run, against the target of under 1 minute.
- **Search:** whether the required document appeared in the top 3 results of any search in the run.
- **Effort:** turns, tool calls and tokens.

## Limits of this test

- The same author wrote the data, the documents, the questions and these rules, so a high score isn't proof the agent would do this on real incidents.
- Three runs per question shows whether the answers are consistent, but it's a small sample.
- The first three questions point to a rough date, which a real analyst would often have too.
- The no-hint question still needs someone to ask it. It tests whether the agent can spot problems when asked, not automatic detection. Nothing in this project watches the data on its own yet.

## Results

| Question | Run 1 | Run 2 | Run 3 | Passed |
|---|---|---|---|---|
| INC-1 | [Pass](eval-answers/INC-1-run1.md) | [Pass](eval-answers/INC-1-run2.md) | [Fail](eval-answers/INC-1-run3.md) | 2 of 3 |
| INC-2 | [Pass](eval-answers/INC-2-run1.md) | [Pass](eval-answers/INC-2-run2.md) | [Fail](eval-answers/INC-2-run3.md) | 2 of 3 |
| INC-3 | [Pass](eval-answers/INC-3-run1.md) | [Pass](eval-answers/INC-3-run2.md) | [Pass](eval-answers/INC-3-run3.md) | 3 of 3 |
| OPEN | [Fail](eval-answers/OPEN-run1.md) | [Pass](eval-answers/OPEN-run2.md) | [Fail](eval-answers/OPEN-run3.md) | 1 of 3 |
| **Total** | | | | **8 of 12** |

Each answer is published unedited, including the date line that the general formatting rules added.

### The four failures

| Run | Rule failed | What happened |
|---|---|---|
| INC-1 run 3 | Numbers | It found the right bank and cause, but said the declines appeared in 7 regions. There were 8, and it listed the eighth in the same sentence. This is the closest call, and it fails because the rule allows no wrong figures. |
| INC-2 run 3 | Numbers | It found the right region and cause, but said UK approval on nearby days ran from 93.5% to 93.8%. Its own query showed 94.39% on September 14 and 94.21% on September 20. Its conclusion that approvals didn't fall still holds. |
| OPEN run 1 | Found | It found the fraud rule and the bank outage but missed the UK slowdown, and it described the other days as flat. |
| OPEN run 3 | Found | It found the fraud rule and the UK slowdown but missed the bank outage. |

### What the results show

- **It's reliable at finding a cause once a question points to the problem.** All 9 of those runs found the right incident and cited the right document.
- **Its figures aren't reliable enough to skip checking.** Two answers contained a wrong number, even though their tool results or their own text had the right one.
- **It doesn't reliably spot problems without a hint.** Only 1 of 3 no-hint runs found all three incidents. The two it missed are the quiet ones: the UK slowdown didn't lower approvals, and the bank outage barely moved the overall rate. It found the fraud rule, the largest incident, every time.
- **False alarms:** none of the three no-hint runs reported an extra incident. OPEN run 1 called FR-2038 an airline rule when it's a hotel rule, while ruling it out as a cause.

### How the other measures came out

| Measure | Target | Result |
|---|---|---|
| Time per run | Under 1 minute | All 12 runs, from 31 to 46 seconds. Three sessions ran at a time |
| Right document in the top 3 of a search | Every incident | 8 of 9 runs with a hint. INC-2 run 3 still cited the right document. In the no-hint runs, 7 of 9 document checks, and the two misses match the incidents those runs missed |
| Every figure correct | 100% | 10 of the 12 answers had no wrong figure |
| Turns per run | Not set | 6 to 14 |
| Tool calls per run | Not set | 5 to 13 |
| Tokens per run | Not set | About 30,000 to 79,000 in, including cached context, and 2,000 to 4,000 out |

The raw figures for each run are in [runs.json](eval-answers/runs.json). The runner is [evals/run_eval.py](../evals/run_eval.py).
