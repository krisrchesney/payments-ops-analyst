# INC-2-run1

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Some merchants said card payments felt slow one morning during the week of September 14. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02, time not available to me (CST)

**What moved:** UK authorization latency rose for two hours on Thursday, Sept 17, 09:00–10:59 UTC. Merchants would have seen it in the UK morning.

**Numbers** (`gold_latency_hourly`, UK region)

| Hour (UTC) | p50 | p95 | p99 |
|---|---|---|---|
| 08:00 | 170 ms | 348 ms | 423 ms |
| 09:00 | 970 ms | 2016 ms | 2322 ms |
| 10:00 | 983 ms | 2084 ms | 2776 ms |
| 11:00 | 164 ms | 345 ms | 391 ms |

- **Size of the jump:** p95 was about 6 times the UK baseline of about 349 ms (the average before Sept 14). Median latency rose about 5.7 times.
- **Scope:** these two UK hours were the only region-hours in Sept 14–20 where p95 exceeded 1.5 times that region's baseline. No other region or day was affected.
- **Traffic:** volume was normal at 235 and 271 auths in the two hours, so this wasn't a load surge.

**Why it happened:** this comes from `platform-change-log.md`, section "CHG-7731: UK gateway connection-pool change (2026-09-17)".
- At 08:55 UTC the UK gateway's connection pool to the card network was cut from 400 to 120 connections as part of a cost review.
- Requests queued at the gateway.
- The pool was restored to 400 at 10:58 UTC, and latency was normal by 11:00.

The timing matches the data. The change came 5 minutes before the spike, the spike was UK-only, and recovery came right after the rollback. `runbook-latency-spike.md` (Steps 1–3) says to check scope and recent changes first, so I used it to frame the checks.

**Customer impact:** I found no approval damage.
- UK approval rate on Sept 17 was 93.86%, against 93.73% for Sept 10–16.
- UK code 91 (issuer unavailable) declines were 36 on Sept 17, against 38.4 per day in the baseline. There was no timeout spike.
- That agrees with the change log's "requests were slow but completed."

**What I could not confirm**
- **Cause:** the gold tables don't record config changes. The link to CHG-7731 rests on matching timing and scope, not on a direct measurement. I did not find a document that contradicts it.
- **Reports:** I have no merchant complaint data, so I can't tie "felt slow" to this window. It is the only latency anomaly that week, which makes it the likely match.
- **Hourly impact:** approval and decline tables are daily, so I couldn't check the two affected hours on their own. A small hourly effect or some abandoned checkouts could be hidden in the daily figures. Abandonment isn't in the data at all.
- **Cost review:** I found no document explaining the cost review or who approved the change.
- **Follow-ups:** the change log lists a staging load test and a per-region p95 alert. I couldn't verify whether either exists.
