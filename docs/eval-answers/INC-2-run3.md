# INC-2-run3

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Some merchants said card payments felt slow one morning during the week of September 14. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02 (current time not available to me), CST

## Summary
The slowdown was a UK-only latency spike on **2026-09-17, 09:00–10:59 UTC**. It was caused by a connection-pool reduction at the UK authorization gateway. The change log says the pool was cut from 400 to 120 connections.

## What moved (`gold_latency_hourly`, UK)
| Hour (UTC) | p50 | p95 |
|---|---|---|
| 06:00–08:00 | 158–170 ms | 348–363 ms |
| **09:00** | **970 ms** | **2,016 ms** |
| **10:00** | **983 ms** | **2,084 ms** |
| 11:00 onward | 158–165 ms | 334–345 ms |

- **Size of the spike:** UK p95 rose to about 6 times the UK median p95 of 348 ms, and p50 rose about 6 times as well.
- **Scope:** these two UK hours were the only region-hours in September 1–28 where p95 was over twice that region's median. No other region crossed that line, so I did not find a spike in any other region.
- **Volume:** traffic was normal (235 and 271 auths in the two hours), so this was not a load surge.

## Why it happened
- **Document:** `platform-change-log.md`, section "CHG-7731: UK gateway connection-pool change (2026-09-17)".
- **Cause:** at 08:55 UTC the UK gateway's connection pool to the card network was cut from 400 to 120 as part of a cost review. Requests queued at the gateway.
- **Fix:** the pool was restored at 10:58 UTC, and latency was normal by 11:00.
- **Timing match:** the change came 5 minutes before the first slow hour, and recovery matches the rollback. Both fit the gold-table hours above.
- **Runbook:** `runbook-latency-spike.md` ("Step 2: Check recent changes" and "Step 3: Roll back first") describes this pattern. I used it for context only.

## Customer impact (`gold_daily_approval`, `gold_decline_reasons`)
- **UK approval rate:** 93.86% on Sept 17, against 93.5–93.8% on the days around it (Sept 10–16 and 18–20). I saw no dip.
- **Code 91 (issuer timeouts):** 422 declines across all regions on Sept 17, against a Sept 10–16 average of 463.6 per day. That is lower, not higher.
- **Change log:** it says approval impact was "none measured; requests were slow but completed". The daily numbers agree. The slowness was real, but it did not turn into declines.

## What I could not confirm
- **Merchant reports:** I have no merchant complaint data, so I can't tie specific complaints to this window. The match rests on timing and region.
- **Hour-level approvals:** the approval table is daily only. A small dip inside the two slow hours could be hidden in the daily figure. I also didn't break code 91 down by UK and hour.
- **Abandoned checkouts:** nothing in the gold tables captures them, so I can't say whether any slow payments were given up.
- **Change log vs. gold tables:** the 08:55 and 10:58 times come only from the change log. The gold tables confirm the hourly effect, not the exact minutes.
- **Other days that week:** I didn't find any other latency anomaly in September 14–20, so this is the only candidate.
