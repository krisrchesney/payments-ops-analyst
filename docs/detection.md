# Automatic detection

*All data is synthetic. The figures here come from the `gold_anomalies` table and read-only queries on the same data, run on November 3, 2026.*

**Result: all 3 planted incidents were flagged, and no flag fell on a normal day.** The table has 21 rows from 15,120 checks over September 8 to 28. This is not an independent test, because the thresholds were chosen knowing the answers. [The real test is still to come.](#the-independent-test)

## What this does

Before this table, someone had to notice a problem and ask. `gold_anomalies` compares each day or hour with the same series' recent past and writes a row when the change is too large to be normal. It says what moved. It doesn't say why, and it doesn't alert anyone yet.

The thresholds are at the top of [`gold.py`](https://github.com/krisrchesney/payments-ops-analyst/blob/master/pipelines/transformations/gold.py).

## How each check works

Every check compares a value with a **baseline: the median of the same series over the previous 14 days.** A median holds steady during a multi-day incident, where an average would rise and hide the later days. Electronics declines show this: the baseline stayed at 9 on all three days of INC-3.

| Check | Looks at | Score | Flags when |
|---|---|---|---|
| Approval drop | Daily approval rate by region and by issuer | Standard errors below baseline, given that day's volume | Score is 4 or more |
| Decline spike | Daily declines by issuer and code, and by category, channel and code | (declines − baseline) / √baseline | Score is 5 or more **and** at least 25 extra declines |
| Latency spike | Hourly p95 latency by region | Value as a multiple of baseline | Score is 2 or more |

A series can't flag until it has 7 days of history.

## Why these thresholds

| Threshold | Evidence | Margin |
|---|---|---|
| Approval score of 4 | The highest scores on normal days were 3.36 (US-South, Sep 9) and 3.34 (Lee Credit Union, Sep 16) | Thin. The lowest real flag scored 4.07 |
| Decline score of 5 | Fuller Credit Union code 05 on Sep 9 had 30.5 extra declines and scored 4.47, so a line of 4 would raise a false alarm | Thin at the bottom. It's the only row with 25 or more extra declines that scored under 5 |
| At least 25 extra declines | This stops Fitzgerald Financial code 59 on Sep 8, which scored 5.2 on only 9 extra declines. It also stops 93 small side effects of INC-3 | Thin. Two INC-3 side effects had 24 extra |
| Latency ratio of 2 | Normal hours reached 1.25 at most. The incident hours reached 5.81 and 6.0 | Wide, but only because the planted spike was so large |

## The 21 flags

### INC-1: Trujillo Credit Union outage, Sep 12 (2 flags)

| Check | Series | Observed | Baseline | Score |
|---|---|---|---|---|
| Decline spike | Trujillo Credit Union, code 91 | 178 | 11 | 50.35 |
| Approval drop | Trujillo Credit Union | 84.90% | 93.54% | 14.79 |

### INC-2: UK latency, Sep 17 (2 flags)

| Check | Series | Hour (UTC) | Observed | Baseline | Ratio |
|---|---|---|---|---|---|
| Latency spike | UK | 09:00 | 2,016 ms | 347 ms | 5.81 |
| Latency spike | UK | 10:00 | 2,084 ms | 347.5 ms | 6.00 |

These are the only two hours flagged, and approvals didn't flag that day, which matches what was planted.

### INC-3: Electronics fraud rule, Sep 22 to 24 (17 flags)

The category flags name the actual problem:

| Day | Series | Observed | Baseline | Score |
|---|---|---|---|---|
| Sep 22 | Electronics, ecommerce, code 59 | 666 | 9 | 219.00 |
| Sep 23 | Electronics, ecommerce, code 59 | 678 | 9 | 223.00 |
| Sep 24 | Electronics, ecommerce, code 59 | 650 | 9 | 213.67 |

The other 14 are places where the same declines showed up:

| Day | Check | Series | Observed | Baseline | Score |
|---|---|---|---|---|---|
| Sep 22 | Approval drop | US-West | 92.58% | 93.72% | 5.24 |
| Sep 22 | Decline spike | Christensen Bank, code 59 | 30 | 5 | 11.18 |
| Sep 22 | Decline spike | Lopez Bank, code 59 | 34 | 6 | 11.43 |
| Sep 23 | Approval drop | US-West | 92.21% | 93.66% | 6.66 |
| Sep 23 | Approval drop | US-South | 92.73% | 93.72% | 4.85 |
| Sep 23 | Approval drop | US-Northeast | 92.75% | 93.76% | 4.71 |
| Sep 23 | Approval drop | BR | 92.08% | 93.71% | 4.07 |
| Sep 23 | Approval drop | Hall Bank | 90.87% | 94.18% | 5.91 |
| Sep 23 | Approval drop | Neal Bank | 91.29% | 93.83% | 4.46 |
| Sep 23 | Decline spike | Hall Bank, code 59 | 31 | 4.5 | 12.49 |
| Sep 23 | Decline spike | Martinez Bank, code 59 | 34 | 6 | 11.43 |
| Sep 24 | Approval drop | US-West | 92.64% | 93.66% | 4.70 |
| Sep 24 | Approval drop | Zuniga Financial | 91.30% | 93.89% | 4.51 |
| Sep 24 | Decline spike | Miller Credit Union, code 59 | 31 | 5 | 11.63 |

## How much of each flag came from the incident

A flag on an incident day isn't automatically caused by the incident. This table removes the fraud rule's declines (Electronics, ecommerce, code 59) and scores the approval flags again.

| Day | Series | Score | Score without the rule | Extra declines | From the rule |
|---|---|---|---|---|---|
| Sep 22 | US-West | 5.24 | −0.82 | 141 | 174 |
| Sep 23 | US-West | 6.66 | 0.59 | 181 | 176 |
| Sep 23 | US-Northeast | 4.71 | 0.42 | 129 | 125 |
| Sep 23 | US-South | 4.85 | 1.73 | 140 | 96 |
| Sep 23 | BR | 4.07 | 3.05 | 60 | 16 |
| Sep 23 | Hall Bank | 5.91 | 3.82 | 58 | 22 |
| Sep 23 | Neal Bank | 4.46 | 2.45 | 45 | 22 |
| Sep 24 | US-West | 4.70 | −0.80 | 128 | 160 |
| Sep 24 | Zuniga Financial | 4.51 | 3.11 | 45 | 15 |

All 9 fall below the line without the rule, so the incident is what pushed each one over. But BR, Hall Bank, Neal Bank and Zuniga Financial are only partly explained by it. More than half of their extra declines came from outside the rule, which looks like ordinary variation that happened to land on an incident day. Someone reading those four rows could go looking for a problem at those banks that doesn't exist.

The five issuer flags on code 59 are similar but more clearly tied to the incident. Between 20 of 30 and 29 of 34 of those declines came from the rule, and each drops under the 25 extra-decline line without it.

## Closest calls

**Incident days that didn't flag**

- US-Northeast on Sep 22 scored 3.99 on approval against a line of 4. Its approval rate was 92.89% against a 93.76% baseline.
- Martinez Bank on Sep 23 (3.88) and Lee Credit Union on Sep 24 (3.82) also fell just short on approval.
- 93 issuer and code 59 series scored 5 or more on Sep 22 to 24 but had fewer than 25 extra declines. Fuller Credit Union on Sep 23 and Roy Financial on Sep 22 both had 24.
- INC-1 never flagged at region level. One issuer's outage is too small to move a whole region's approval rate.

None of these lost an incident, because each one was flagged elsewhere.

**Normal days that came close**

- Fuller Credit Union code 05 on Sep 9 scored 4.47 with 30.5 extra declines, against a line of 5.
- US-South on Sep 9 scored 3.36 and Lee Credit Union on Sep 16 scored 3.34 on approval, against a line of 4.
- Fitzgerald Financial code 59 on Sep 8 scored 5.2, stopped only by the 25-decline minimum.

## Limits

- **Tuned on known answers.** The thresholds were set while looking at these incidents, so this result shows the checks can work, not that they will.
- **The data is easier than real payments.** The simulator spreads volume evenly across every hour and day, with no weekends or daily peaks, and latency has no daily pattern. Real data would raise false alarms that this table can't show. The latency ratio is the most exposed, because it compares every hour with the same median.
- **The planted incidents are large.** Latency was multiplied by 6 and electronics declines rose about 70 times. A spike of 1.5 times normal wouldn't flag.
- **No flags in a series' first 7 days.** Nothing could flag on September 1 to 7.
- **Long incidents go quiet.** An incident lasting more than about a week would become most of the 14-day window, pull the median toward it and stop flagging.
- **Whole days only for approvals and declines.** The INC-1 outage lasted three hours, but its flags only give the date. A day still arriving is skipped until all 24 of its hours are in the data, so a partial day is never compared with full-day baselines. A problem on the current day is therefore flagged only after the day ends.
- **Rows aren't incidents.** 21 rows describe 3 incidents, and nothing groups them yet. INC-3 alone is 17 rows, and the most useful row isn't marked as such.
- **The assistant can't read the flags yet.** The table isn't in the export the assistant works from, so it can't use a flag as a starting point.
- **Only these views are watched.** Approval rate by region and issuer, declines by the two groupings above, and p95 latency by region. Chargebacks and single merchants aren't covered. A problem shows up only if it's visible in one of those views.

## The independent test

The next step is a [test plan](detection-test.md) that plants four new incidents through the hourly feed, using these same thresholds, with predictions and scoring written down before any of the data exists. Its result will be reported here whichever way it goes, including if it's missed or raises a false alarm. Any later change to a threshold will be listed beside the original numbers, not in place of them.
