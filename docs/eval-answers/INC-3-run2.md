# INC-3-run2

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Approval rates looked off during the week of September 21. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02, current time unavailable to me (CST)

## What moved
Approval rates fell for three days, 22–24 Sept, and recovered on 25 Sept. The cause was code 59 (suspected fraud) declines on Electronics e-commerce.

**Overall approval (`gold_daily_approval`)**

| Period | Approval rate |
|---|---|
| 15–21 Sept baseline | 93.72%–93.93% (about 93.8%) |
| 22 Sept | 93.03% |
| 23 Sept | 92.75% |
| 24 Sept | 93.02% |
| 25 Sept | 93.97% |
| 26–28 Sept | 93.77%–93.90% |

That is a drop of about 0.8 to 1.0 points. Volume was flat at about 71,000–72,000 auths a day, so traffic mix did not cause it.

**Only e-commerce fell.** Card-present, contactless and card-on-file were unchanged.
- Non-tokenized e-commerce fell from about 90.6–91.3% to 88.4% (22 Sept), 87.9% (23 Sept) and 88.2% (24 Sept).
- Tokenized e-commerce fell from about 92.1–92.8% to 90.0%, 89.6% and 89.8%.
- Both recovered on 25 Sept.

**Decline codes (`gold_decline_reasons`)**
- Code 59 averaged 211.6 declines a day over 15–21 Sept. It averaged 872.0 a day over 22–24 Sept, about 4.1 times higher.
- Codes 05, 14, 51, 54 and 91 stayed within normal range.
- `daily_ops_summary` for 22 Sept showed no latency spikes.

**Where the 59s were (`gold_declines_by_category`)**
- Electronics e-commerce code 59 went from 4–11 a day before 22 Sept to 666, 678 and 650 on 22–24 Sept.
- It fell back to 10, 6, 5 and 12 on 25–28 Sept.
- Total code 59 went from about 210 a day to 856, 891 and 869 on 22–24 Sept, then back to 203–225. Electronics e-commerce accounts for nearly all of the increase.
- The issuer view showed code 59 up 5 to 8 times at several issuers at once (Lopez Bank 7.9×, Christensen Bank 6×, Roy Financial 5×, Miller Credit Union 6.7×, Johnson Credit Union 5.1×). A rise spread across issuers points to our own rule rather than to the banks.

## Why it happened
Our own fraud rule change was the cause, according to `fraud-rule-change-log.md`:
- **FR-2041, "Electronics card-not-present threshold tightened (2026-09-22)":** at 00:00 UTC on 22 Sept the Electronics (MCC 5732) e-commerce risk-score threshold went from 780 to 640. Card-present and contactless were not changed. It went to 100% of traffic with no A/B test. The pre-launch estimate was about 1.5× normal code 59 declines.
- **FR-2041-RB, "Rollback of the Electronics threshold (2026-09-25)":** at 00:00 UTC on 25 Sept the threshold went back to 780. The stated reasons were merchant complaints and a much larger decline increase than estimated.

The dates and scope match the numbers. The spike starts on 22 Sept and ends on 25 Sept, and it is confined to Electronics e-commerce. The actual increase was about 90× on Electronics e-commerce (666 a day against a baseline of about 7), far above the 1.5× estimate. This is the same pattern as the August airline rule incident in `postmortem-2026-08-airline-rule.md`, and the check in `runbook-decline-spike.md` (Step 2: check the fraud rule change log) points to the same cause.

## What I could not confirm
- **Whether the declined customers were legitimate.** The change log says merchants reported good customers declined, but the gold tables have no fraud-outcome data. Chargebacks are only weekly by MCC and I did not link them to these declines.
- **Electronics e-commerce approval rate.** `gold_daily_approval` has no MCC dimension, so I could not compute that rate or its volume directly.
- **Lost sales.** I did not estimate revenue impact.
- **The "fraud on high-value orders" rationale.** I have no data to test whether it was justified.
- **Time of day.** The tables are daily or hourly UTC and I did not check the hour the rule took effect or was rolled back. The log's 00:00 UTC times fit the daily pattern.
- **Today's time.** I have no clock, so the CST time in the first line is not available.
