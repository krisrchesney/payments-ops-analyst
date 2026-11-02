# OPEN-run3

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Review September 1 to 28. Is anything unusual, and why? Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

**Sept 1–28 review: two unusual events**

**1. Electronics ecommerce fraud declines, Sept 22–24 (the main one)**
- **Approval rate:** It sat at about 93.8% every day. It dropped to 93.03% on Sept 22, 92.75% on Sept 23 and 93.02% on Sept 24, then returned to 93.97% on Sept 25 (`gold_daily_approval`). Declined dollar amount rose from about $670k a day to $854k–$900k.
- **Regions:** Every region fell, between 0.7 and 1.4 points, when I compared Sept 15–21 with Sept 22–24. US-West fell most (93.82% to 92.47%). The drop is not tied to one region.
- **Cause by category:** Code 59 (suspected fraud) declines on Electronics ecommerce went from about 7 a day in the baseline to about 665 a day, roughly 91 times (`gold_declines_by_category`). The daily counts were 666, 678 and 650, and they fell back to 10 on Sept 25. Nothing else in the top increases moved by more than about 1.2 times.
- **Cause by issuer:** Code 59 rose 4 to 7 times at the top five issuers, including Miller Credit Union, Dixon Financial, Lopez Bank, Thomas Financial and Hall Bank. A rise across many issuers points to our own rules rather than the banks, as `response-code-guide.md` ("59: Suspected fraud") says.
- **Why it happened:** `fraud-rule-change-log.md`, entry FR-2041, says that on Sept 22 at 00:00 UTC the Electronics (MCC 5732) ecommerce risk threshold was lowered from 780 to 640.
  - The rule went to 100% of traffic with no A/B test.
  - The estimate before launch was about 1.5 times normal code 59 declines. The actual rise was about 91 times.
  - Entry FR-2041-RB restored the threshold to 780 on Sept 25 at 00:00 UTC, citing merchant complaints. That matches the recovery in the data.
- **Process guidance:** `runbook-decline-spike.md` (Step 2) and `postmortem-2026-08-airline-rule.md` (Lessons) cover this pattern. The August airline rule FR-2019 caused the same thing, and the lesson was to launch new rules to 10% of traffic first.

**2. UK latency spike, Sept 17**
- UK p95 latency was 2,016 ms at 09:00 UTC and 2,084 ms at 10:00 UTC (`gold_latency_hourly`). No other region-hour went above 800 ms.
- `platform-change-log.md`, entry CHG-7731, explains it. The UK gateway connection pool was cut from 400 to 120 at 08:55 UTC and restored at 10:58 UTC. The spike lines up with those times.
- Declines in the UK on Sept 16–18 look normal. Code 91 was 44, 36 and 33, and no code spiked. That agrees with the log's note of no approval impact.

**Things I could not confirm**
- **Good customers:** The gold tables show declines, not which ones were legitimate. The claim that good customers were blocked comes only from the rollback entry's "merchant complaints" wording.
- **Lost sales:** I did not calculate the revenue lost on Electronics. The extra declined dollars are overall figures, not Electronics-only.
- **Rule effect:** The log gives no reason the rule's effect was about 60 times the estimate. I can't say whether the 640 threshold or something else caused that.
- **Real fraud:** I can't tell whether any of the extra declines stopped real fraud.
- **Other tables:** I did not look at `gold_chargebacks_weekly`. It would show whether fraud losses changed after the rollback, and its dates run into November.
- **Other change-log entries:** FR-2033 (airline threshold relaxed on Sept 4), FR-2036 (a monitor-only rule) and CHG-7750 (BR network link maintenance) did not produce visible movement in the daily numbers I checked. I did not test each of them directly.
