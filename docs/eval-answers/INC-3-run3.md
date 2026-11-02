# INC-3-run3

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Approval rates looked off during the week of September 21. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02, current time not available to me (CST)

## What moved
Approval rate fell for three days (Sept 22–24) and went back to normal on Sept 25. The cause was our own fraud rule change on Electronics ecommerce, not the issuers.

**Approval rate** (`gold_daily_approval`, all regions and channels):

| Period | Approval rate |
|---|---|
| Sept 15–21 baseline | 93.80% |
| Sept 22 | 93.03% |
| Sept 23 | 92.75% |
| Sept 24 | 93.02% |
| Sept 25 | 93.97% |

- Sept 22–24 averaged about 92.9%, roughly 0.9 points below baseline.
- Volume was flat at about 71.5k auths a day.
- Tokenized and non-tokenized traffic both dropped, by 0.8 and 1.0 points, so it wasn't specific to one of them.

**Code 59 (suspected fraud) declines** (`gold_declines_by_category`):

| Date | All code 59 | Electronics ecommerce |
|---|---|---|
| Sept 18–21 | about 210 a day | 4–8 a day |
| Sept 22 | 856 | 666 |
| Sept 23 | 891 | 678 |
| Sept 24 | 869 | 650 |
| Sept 25 | 203 | 10 |

- Electronics ecommerce accounts for nearly all of the jump.
- Sept 23 summary (`daily_ops_summary`): code 59 was 891 declines against a previous-7-day average of 301. Codes 05 and 51 were flat.
- Sept 22–24 had about 2,000 more code 59 declines than baseline. That is close to the roughly 1,850 approvals lost compared with the baseline rate.
- The increase showed up at many issuers at once. The top five on Sept 23 (Martinez Bank, Hall Bank, Fuller Credit Union, Dixon Financial and Page Bank) each rose 4–5 times. Because it was spread across issuers, it points to our rule rather than the banks.
- Latency spikes: none on Sept 23.

## Why (documents relied on)
- **`fraud-rule-change-log.md`, "FR-2041: Electronics card-not-present threshold tightened (2026-09-22)":**
  - At 2026-09-22 00:00 UTC, the Electronics (MCC 5732) ecommerce risk threshold went from 780 to 640.
  - It went to 100% of traffic with no A/B test.
  - The pre-launch estimate was about 1.5 times normal code 59 declines.
- **`fraud-rule-change-log.md`, "FR-2041-RB: Rollback (2026-09-25)":**
  - The threshold was restored to 780 at 2026-09-25 00:00 UTC.
  - The stated reason was merchant complaints and a much larger decline increase than estimated.

The timing, the channel and category scope, and the rollback date all match the tables. The actual effect was far above the 1.5 times estimate. `runbook-decline-spike.md` (Step 2) says a much bigger effect than estimated means the threshold is too tight. The August airline postmortem (`postmortem-2026-08-airline-rule.md`) describes the same pattern, but I used it only as precedent.

## What I could not confirm
- **Good customers declined:** the only evidence is the merchant complaints cited in the rollback entry. The tables have no fraud-outcome or customer-legitimacy data.
- **Approval rate for Electronics ecommerce alone:** `gold_daily_approval` has no merchant category. I inferred the impact from decline counts.
- **Size of the multiple:** the driver tool's 6.7 times figure is understated. Its 7-day baseline for Sept 23 includes the already-affected Sept 22. Against Sept 18–21, the increase is over 100 times.
- **Whether the rule caught any real fraud:** `gold_chargebacks_weekly` is weekly and its data runs past the decline data, so I didn't use it. I can check it if you want.
- **Regional split:** I only looked at all-region totals and the Sept 23 lowest regions (BR, US-West and UK, at 92.1–92.7%). I didn't test whether the rule hit regions unevenly.

The log says the follow-up is a 10% traffic-split re-test before any relaunch, plus adding code 59 by merchant category to the daily ops review.
