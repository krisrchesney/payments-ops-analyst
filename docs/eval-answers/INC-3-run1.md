# INC-3-run1

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Approval rates looked off during the week of September 21. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02 (CST), exact time unavailable because I have no clock tool

## What moved

Approval rate fell on Sep 22, 23 and 24 and went back to normal on Sep 25. The cause is a fraud rule change on Electronics ecommerce, which sharply raised code 59 (suspected fraud) declines.

**Overall approval rate** (`gold_daily_approval`, all regions):

| Date | Approval rate |
|---|---|
| Sep 14–21 (baseline) | 93.7–93.9% |
| Sep 22 | 93.03% |
| Sep 23 | 92.75% |
| Sep 24 | 93.02% |
| Sep 25–28 | 93.8–93.97% |

- The three-day dip averages about 92.9%, roughly 0.9 points below baseline. Volume stayed flat at about 71.5k auths a day.
- Over the full Sep 21–27 week the drop is smaller, 0.2 to 0.6 points per region, because the four normal days dilute it. US-West is the largest at −0.55 points.
- **Channel:** ecommerce fell from 91.66% to 88.89% (−2.8 points) between Sep 14–20 and Sep 22–24. Card-present, card-on-file and contactless were within ±0.2 points.
- **Code 59 on Electronics ecommerce** (`gold_declines_by_category`):

| Date | Declines |
|---|---|
| Sep 18–21 | 4–8 a day |
| Sep 22 | 666 |
| Sep 23 | 678 |
| Sep 24 | 650 |
| Sep 25 onward | 5–12 a day |

- **Daily summary, Sep 23:** total code 59 declines were 891, against a prior 7-day average of 301. Codes 05 and 51 were flat, at 2,026 vs 1,975 and 1,338 vs 1,343.
- **Issuers:** `gold_decline_reasons` shows code 59 up about 3 to 5 times at many unrelated issuers, including Martinez Bank, Hall Bank, Fuller Credit Union, Dixon Financial and Page Bank. It is not one bank.
- **Latency:** the daily summary shows no latency spikes, so this is not an infrastructure problem.

## Why it happened

The cause is **FR-2041**, in `fraud-rule-change-log.md`, section "FR-2041: Electronics card-not-present threshold tightened (2026-09-22)".

- At 2026-09-22 00:00 UTC, the risk-score threshold for Electronics (MCC 5732) ecommerce was lowered from 780 to 640.
- It went to 100% of traffic with no A/B test.
- Fraud Strategy had estimated about 1.5 times the normal code 59 declines. The actual increase was more than 100 times on Electronics ecommerce (about 665 a day against about 5).
- **FR-2041-RB** (same file, section "Rollback of the Electronics threshold (2026-09-25)") restored the threshold to 780 at 2026-09-25 00:00 UTC. The log cites merchant complaints about good customers being declined.

I checked the timing and scope against the numbers rather than relying on the date match alone:
- The spike starts and ends on the exact days of the rule and its rollback.
- It is confined to Electronics ecommerce, and card-present and contactless electronics were not changed.
- The `response-code-guide.md` section "59: Suspected fraud" says code 59 rising at many issuers in one category points to our own rules. That matches.
- `runbook-decline-spike.md` ("Step 2") and `postmortem-2026-08-airline-rule.md` describe the same pattern from the August airline rule.

## What I could not confirm

- **Whether the declined customers were legitimate.** The rollback entry says merchants reported good customers declined, but the gold tables have no data on fraud outcomes. I did not query `gold_chargebacks_weekly`, and its dates (some weeks after Sep 28) are not tied to this rule.
- **The rule's fraud-prevention benefit.** I have no data on fraud it may have stopped.
- **An exact count of lost approvals.** I did not compute declines above baseline across all codes. The dip of roughly 0.9 points is overall, and the ecommerce drop of about 2.8 points is the larger effect.
- **Why the estimate was 1.5 times when the result was over 100 times.** The documents don't explain it.
- **Minor drift in code 05.** Some issuers and categories, such as Kelly Credit Union and Hotels, show code 05 about 1.2 times baseline. That is small and I found no document explaining it.

The log's own follow-up is to re-test the rule at a 10% traffic split and to add code 59 by merchant category to the daily review.
