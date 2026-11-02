# INC-1-run2

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Several merchants said more cards than usual were declined on September 12. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02, time not available to me (no clock tool in this session, so I can't give a CST time)

## Summary

The Sept 12 rise in declines came from one issuer, Trujillo Credit Union. It had a host outage, and we returned code 91 (issuer unavailable) for its cards. The effect on the overall approval rate was small.

## What moved (gold tables)

- **Overall approval:** 93.60% on Sept 12, against 93.81% for the previous 7 days (Sept 5–11). That is about 0.2 points lower (`gold_daily_approval`).
- **Code 91 declines:** 593 on Sept 12, against a 447.3/day baseline (`daily_ops_summary`). The other top codes barely moved:
  - Code 05 fell, from 1,995 to 1,883.
  - Code 51 rose slightly, from 1,310 to 1,386.
- **Trujillo Credit Union, code 91:** 178 declines on Sept 12, against 11.3/day in the baseline. That is 15.8 times the baseline and +166.7/day (`gold_decline_reasons`). This one issuer accounts for more than the whole net rise in code 91 (+146/day).
- **Spread across regions:** the Trujillo code 91 declines appeared in every region, not one.

  | Region | Declines on Sept 12 |
  |---|---|
  | US-Midwest | 40 |
  | US-South | 34 |
  | US-West | 31 |
  | US-Northeast | 27 |
  | CA | 15 |
  | DE | 15 |
  | UK | 13 |
  | BR | 3 |

  Those regions were typically at 0–5 on surrounding days. A spread across regions fits a problem at the issuer. It does not fit a gateway problem on our side.
- **Latency:** no region had an hour with p95 over twice normal (`daily_ops_summary`). This is consistent with the failure being at the issuer.

## Why it happened (documents)

- **`issuer-status-notices.md`, "Trujillo Credit Union: unplanned host outage (2026-09-12)":**
  - The issuer's authorization host lost its database connection at about 14:00 UTC.
  - Requests failed or timed out, and we answered with code 91.
  - The issuer reported it at 14:20 UTC and confirmed recovery at 17:00 UTC.
  - Our side found no fault, and stand-in processing was not enabled for this issuer.
  - The follow-up is for Issuer Relations to request a root-cause report and discuss enabling stand-in.
- **`response-code-guide.md`, "91: Issuer unavailable":** a sharp rise at one issuer usually means that issuer's systems are down. A rise across all issuers in one region would point to our network or gateway. This case is the first pattern.
- **Timing and scope check:** the notice is dated Sept 12 and names the issuer that shows the 15.8× spike. That match is why I'm treating it as the cause and not just a document near the right date.

## What I could not confirm

- **Outage hours:** the 14:00–17:00 UTC window comes only from the issuer's notice. The gold tables are daily by issuer, so I couldn't check the hours against the data.
- **Cards declined:** the 178 declines are authorization attempts, not unique cards. Some of the 178 may be retries.
- **Merchant reports:** I can't tie the merchant complaints to this outage. The small rises in code 51 (e.g. Fuel card-on-file, Airlines contactless) and code 14 (Restaurants ecommerce, 21 against 8/day) are modest, and I found no document explaining them. They may be normal variation.
- **Root cause:** the issuer's root cause is still outstanding, as the follow-up in the notice says.
- **Network or fraud effects:** I didn't search the platform or fraud change logs. Nothing in the data points that way, since code 05 fell and latency was normal.
