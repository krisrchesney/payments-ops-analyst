# OPEN-run1

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Review September 1 to 28. Is anything unusual, and why? Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02 (CST), exact time unavailable to me

## Summary
Two things stood out between Sep 1 and Sep 28. The big one is a fraud-rule spike on Sep 22–24. The smaller one is a single-issuer outage on Sep 12. The other days were flat, with an approval rate (AR) of about 93.6–93.9%.

## 1. Sep 22–24: code 59 (suspected fraud) spike on Electronics ecommerce
**What moved** (`gold_daily_approval`, `gold_decline_reasons`, `gold_declines_by_category`):
- **Approval rate:** 93.0%, 92.8% and 93.0% on Sep 22, 23 and 24, against about 93.8% on Sep 15–21. It was back to 94.0% on Sep 25.
- **Declined amount:** about $854k–$900k per day, against about $640k–$700k on normal days.
- **Code 59 declines:** 856, 891 and 869 per day, against about 190–250 normally. Sep 25 was 203. The other codes did not move.
- **Electronics, ecommerce, code 59:** 666, 678 and 650 declines per day, against 4–5 per day on Sep 19–21. It fell back to 10 on Sep 25. Electronics on other channels stayed at single digits, so the change was specific to ecommerce.
- **Issuers:** the increase was spread across many issuers at once, each at 4–7 times its baseline. Miller, Dixon, Lopez, Thomas and Hall were the top five.
- **Tokenization:** AR fell for both tokenized (94.6% to 93.8%) and untokenized (93.1% to 92.2%) traffic, so it wasn't specific to either.

**Why:** the evidence points to our own fraud rule, not the banks.
- `fraud-rule-change-log.md`, "FR-2041" (Sep 22): at 00:00 UTC the Electronics (MCC 5732) ecommerce threshold was lowered from 780 to 640. It went to 100% of traffic with no A/B test. The pre-launch estimate was about 1.5 times normal code 59 declines.
- `fraud-rule-change-log.md`, "FR-2041-RB" (Sep 25): the threshold was restored to 780 at 00:00 UTC on Sep 25. The log gives the reason as merchant complaints and a much larger increase than estimated.
- `response-code-guide.md`, "59: Suspected fraud": a code 59 rise at many issuers in one category or channel points to our rules first.
- `runbook-decline-spike.md`, "Step 2": the rule went live in the 48 hours before the spike, and its effect was much larger than estimated.

The timing and scope both match the data. The spike starts on the launch day, covers only the targeted channel and category, and ends on the rollback day. The effect was far above the 1.5× estimate. The August airline incident (`postmortem-2026-08-airline-rule.md`) followed the same pattern.

## 2. Sep 12: code 91 (issuer unavailable) bump
- **Code 91 declines:** 593 on Sep 12, against a prior 7-day average of 447. Overall AR dipped slightly to 93.6%, against 93.8%.
- **Cause:** Trujillo Credit Union alone had 178 declines per day against a baseline of 11, about 16 times higher. It was spread across all regions (for example, US-Midwest 40 and US-South 34).
- **Why:** `issuer-status-notices.md`, "Trujillo Credit Union: unplanned host outage (2026-09-12)". The issuer's host lost its database connection at about 14:00 UTC and recovered at 17:00 UTC. Stand-in processing was not enabled for them. The document says no fault was found on our side.

## Not an issue
- The Sep 6 Dixon maintenance and the Sep 20 Lopez maintenance were planned. I saw no meaningful code 91 effect from either in the daily totals.
- The airline rules FR-2033 (Sep 4) and FR-2038 (Sep 15) turned up in my searches. Their timing and category don't match the Sep 22–24 spike, so I ruled them out.
- Miller Credit Union's BIN migration is dated Sep 28. Miller shows up in the Sep 22–24 code 59 list, but that predates the migration, and its rise looks the same as the other issuers'.

## What I could not confirm
- **Legitimate customers:** the gold tables don't say whether the declined Electronics orders were actually good customers. That claim comes from merchant complaints reported in the change log. I found no merchant-level data to check it.
- **Approval rate by category:** I measured the rule's impact through decline counts and overall AR. I did not pull Electronics ecommerce AR specifically.
- **Chargebacks:** I did not check `gold_chargebacks_weekly`, so I can't say whether the original fraud concern behind FR-2041 was real.
- **Trujillo outage timing:** the 14:00–17:00 UTC window comes from the issuer notice. I did not check it against hourly data in `gold_latency_hourly`. The Sep 12 daily summary showed no latency spikes.
- **Rollback effect:** Sep 25 data is consistent with the rollback working, but I only have daily granularity. I can't verify the exact hour of recovery.
