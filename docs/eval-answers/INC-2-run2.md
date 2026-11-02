# INC-2-run2

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Some merchants said card payments felt slow one morning during the week of September 14. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02, current CST time not available to me

## Summary
Card payments were slow in the **UK on 2026‑09‑17, 09:00–10:59 UTC**. A gateway connection‑pool reduction caused it. I found no approval impact in the daily data.

## What moved (`gold_latency_hourly`, UK)
| Hour (UTC) | p50 | p95 | p99 |
|---|---|---|---|
| 08:00 | 170 ms | 348 ms | 423 ms |
| **09:00** | 970 ms | **2,016 ms** | 2,322 ms |
| **10:00** | 983 ms | **2,084 ms** | 2,776 ms |
| 11:00 | 164 ms | 345 ms | 391 ms |

- **Baseline:** UK median hourly p95 for 09‑01 to 09‑13 was 348 ms. The spike hours ran about 5.8–6.0 times that baseline.
- **Scope:** These were the only two region‑hours from 09‑14 to 09‑20 where p95 exceeded twice the region's baseline. No other region was affected.
- **Volume:** Auth volume was normal (235 and 271 auths per hour), so the slowdown wasn't caused by a traffic surge.

## Why it happened
`platform-change-log.md`, section **"CHG‑7731: UK gateway connection‑pool change (2026‑09‑17)"**, says:
- At 08:55 UTC the UK gateway's connection pool to the card network was cut from 400 to 120 connections as part of a cost review.
- Requests queued at the gateway, and p95 rose from about 09:00.
- The pool was restored at 10:58 UTC, and latency was normal by 11:00.

The document matches the data on timing (change at 08:55, spike from 09:00, recovery at 11:00), region (UK only) and size of effect. I'm treating it as the cause, not just a nearby document. `runbook-latency-spike.md` ("Step 2: Check recent changes" and "Step 3: Roll back first") is consistent with how the incident was handled.

## Customer impact (`gold_daily_approval`, `gold_decline_reasons`)
- **UK approval rate:** 93.86% on 09‑17, against 93.73% for 09‑10 to 09‑16. That's no drop, and it agrees with the change log's "none measured".
- **Code 91 (issuer timeouts):** 422 per day across all regions on 09‑17, against 463.6 for the prior week. Slow requests did not turn into timeouts.

## What I could not confirm
- **Hour‑level approval:** The approval table is daily. A short UK dip inside the two hours, or abandoned checkouts, would not show up. I only have the change log's "none measured".
- **Which merchants:** The gold tables have no merchant‑level latency. I can't tie the incident to the merchants who complained, only to the UK region and time window. If they were UK merchants on the morning of 09‑17, that fits.
- **Cause of the cost review:** I only have the change log's one‑line reason. I found nothing on who approved the change or whether staging load‑testing was done. The follow‑ups (staging load test, per‑region p95 alert) are listed, but I can't tell whether they were completed.
- **Other mornings:** I checked all regions for 09‑14 to 09‑20. If merchants meant a different week or a latency level below twice baseline, this data wouldn't show it.
