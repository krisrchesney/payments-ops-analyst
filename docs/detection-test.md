# Detection test plan

*All data is synthetic. This plan was written before any of the test data was generated, and its predictions are fixed. The results will be added to [the detection write-up](detection.md) whichever way they go.*

**Results (November 8, 2026): [see the detection write-up](detection.md#the-independent-test).** Two of the three incidents it should catch were caught, one was missed by 2.5 declines, the expected miss happened, and there were no false alarms.

## Why a second test

The first 21 flags came from thresholds chosen while looking at the three planted incidents, so they show the detector can work, not that it will. This test plants new incidents in new data, with the [thresholds frozen](https://github.com/krisrchesney/payments-ops-analyst/blob/master/pipelines/transformations/gold.py) as they are today.

What is and isn't independent: the author of this plan knows the thresholds, so the strengths below were picked to sit on both sides of them on purpose. What's independent is the data, which doesn't exist yet, and the targets, none of which was in the first test. This checks whether the detector behaves the way its own arithmetic predicts on fresh data. It doesn't show how real incidents would be caught.

## What will be generated

The hourly feed continues from September 29, 2026, 00:00 UTC. One batch writes 14 days, September 29 to October 12, which is 336 hours at 2,976 authorizations each (about 1 million rows). The incidents in [`detection-test-incidents.json`](detection-test-incidents.json) go in first, and the data is generated once. No hour is regenerated or retried to get a better result.

Days with no incident are the control: September 29 to October 2, October 4, 6 and 8, and October 10 to 12.

## The planted incidents and what I expect

| | When (UTC) | What | Expected result, from the data's volumes and the thresholds |
|---|---|---|---|
| **TEST-A** | Oct 3, 14:00 to 17:00 | DE latency about 2.2 times normal | A latency flag for DE. 2.2 is only just over the line of 2.0, so I expect at least 2 of the 3 hours to flag, and all 3 with about 3-in-4 odds |
| **TEST-B** | Oct 5, 10:00 to 12:00 | A quarter of Vance Credit Union's authorizations decline with 91 | A decline spike for Vance Credit Union, code 91: about 37 extra declines against a baseline near 11. An approval drop is **not** expected: it should score about 3.4 against the line of 4, with roughly a 1-in-4 chance of flagging anyway |
| **TEST-C** | Oct 7, all day | 5% of Airlines ecommerce authorizations decline with 59 | A decline spike for Airlines, ecommerce, code 59: about 88 extra against a baseline near 8. Nothing else, because the extra declines spread thinly across 40 issuers and 8 regions |
| **TEST-D** | Oct 9, all day | 0.8% of Restaurants ecommerce authorizations decline with 59 | **Missed on purpose.** About 18 extra declines, under the 25 minimum. A flag would come about 1 time in 10 |

Everywhere else I expect no flags.

TEST-D is there to show the cost of the 25-decline minimum: a real problem of 18 extra declines a day goes unflagged. A miss here is the expected outcome, not a failure.

## How the results will be scored

Scoring is fixed now, so it can't bend to fit the results.

1. **Hit:** a flag from the expected detector on the incident's target, on the incident's day (for latency, an hour inside the window).
2. **Explained flag:** any other flag on an incident day counts as explained only if its score drops below its threshold when the incident's own declines are removed. This is the same re-scoring used in the first write-up.
3. **False alarm:** any flag that isn't a hit or an explained flag, on any of the 14 days.
4. **Surprises:** an expected hit that is missed, or TEST-D being flagged, is reported as a surprise.
5. **What gets reported:** every new flag in a table, the number of checks made, hits, explained flags, false alarms and surprises, and the near misses on both sides, as the first write-up did.

**A good result:** A, B and C each caught by the expected flag, with no false alarms. TEST-D missed.

## Rules

- The thresholds in `gold.py` and the scoring above don't change before the results are published.
- If a threshold is changed afterwards, the original results stay next to the new ones.
- The results are published whichever way they go.

## Limits that already apply

- The simulator has only three kinds of incident, so this tests new targets and strengths, not new kinds of failure.
- The data is calmer than real payments: no weekends, no daily peaks, and every issuer the same size. A real false-alarm rate would be higher.
- The expected results rest on rough volume arithmetic. They're written down so they can be wrong in public.
