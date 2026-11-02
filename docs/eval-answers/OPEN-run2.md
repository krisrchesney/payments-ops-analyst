# OPEN-run2

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Review September 1 to 28. Is anything unusual, and why? Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02, current time not available to me (CST)

## Summary
Sep 1–28 had three unusual events. The biggest was a fraud-rule change on Sep 22–24. The other two were an issuer outage on Sep 12 and a UK latency spike on Sep 17.

Baseline approval was about 93.8% a day (`gold_daily_approval`). Across the whole month, regional approval rates barely moved, within ±0.4 points.

### 1. Sep 22–24: approval dip caused by our own fraud rule (largest)
- **Approval rate:** 93.0%, 92.8% and 93.0% on Sep 22, 23 and 24. Typical days were about 93.8%. It was back to 94.0% on Sep 25.
- **Code 59 (suspected fraud):** about 860–890 declines a day, against about 210 normally (`gold_decline_reasons`).
- **Where it was concentrated:** Electronics, ecommerce, code 59 (`gold_declines_by_category`). It ran at 666, 678 and 650 a day, against 4–5 a day on Sep 19–21. That is about 91 times baseline.
- **Where it was not:** the top five issuers each rose 4–7 times on code 59. Card-present and contactless electronics did not show up as drivers.
- **Cause:** FR-2041 went live Sep 22 at 00:00 UTC. It lowered the Electronics ecommerce risk threshold from 780 to 640 (`fraud-rule-change-log.md`, "FR-2041"). The timing and scope match the numbers.
- **Estimate vs actual:** the pre-launch estimate was about 1.5 times normal declines. The actual was about 91 times. No A/B test was run.
- **Rollback:** FR-2041-RB restored the threshold to 780 on Sep 25 at 00:00 UTC (`fraud-rule-change-log.md`, "FR-2041-RB"). Electronics code 59 fell to 10, 6 and 5 on Sep 25–27. The log cites merchant complaints about good customers being declined.

### 2. Sep 12: Trujillo Credit Union outage
- **Code 91 (issuer unavailable):** 593 declines on Sep 12, against about 440 normally.
- **Trujillo Credit Union code 91:** 178 on Sep 12, against 6–13 on neighbouring days (`gold_decline_reasons`).
- **Cause:** the issuer's host lost its database connection at about 14:00 UTC and recovered at 17:00 UTC (`issuer-status-notices.md`, "Trujillo Credit Union: unplanned host outage"). The notice says no fault was found on our side and stand-in processing was not enabled.
- **Approval impact:** approval fell to 93.6% on Sep 12, the month's lowest outside Sep 22–24.

### 3. Sep 17: UK latency spike
- **UK p95 latency:** 2,016 ms at 09:00 UTC and 2,084 ms at 10:00 UTC, against about 345 ms normally. P50 rose from about 170 ms to about 970 ms (`gold_latency_hourly`).
- **Cause:** CHG-7731 cut the UK gateway connection pool from 400 to 120 at 08:55 UTC. It was rolled back at 10:58 UTC (`platform-change-log.md`, "CHG-7731"). The window matches the data.
- **Approval impact:** I saw none. Sep 17 approval was 93.8%, in line with normal, which matches the log's "none measured".

### Checked and not the cause
- FR-2033 (airline threshold relaxed, Sep 4) and FR-2038 (hotel rule, Sep 15) did not produce a visible spike in the daily totals.
- Dixon Financial's planned maintenance on Sep 6 (03:00–03:30 UTC) did not show up in daily totals.
- The Aug 11 airline postmortem is a similar earlier incident, so I used it only for context.

### What I could not confirm
- **Rule justification:** I could not confirm whether the FR-2041 declines were actually fraud. The tables hold no ground truth, and `gold_chargebacks_weekly` was not checked for Electronics.
- **Merchant impact:** I could not confirm the revenue lost. I didn't compute `declined_amount` for Electronics ecommerce.
- **Trujillo timing:** the exact outage window rests on the issuer notice. The tables are daily by issuer, so I couldn't verify the hours.
- **Latency screen:** I used a rough screen of twice the overall average p95. It could miss smaller regional spikes. The 2× rule was not run per region, so I haven't ruled out other regional spikes.
- **Minor days:** I did not review small day-to-day dips such as Sep 9 and Sep 19.
