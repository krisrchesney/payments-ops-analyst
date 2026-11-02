# INC-1-run1

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Several merchants said more cards than usual were declined on September 12. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02, current time in CST unavailable to me (only the date is known)

**What moved:** Code 91 ("issuer unavailable") declines for one issuer, Trujillo Credit Union. The overall drop was small, so merchants most likely noticed it through that issuer's cardholders.

**Numbers (gold tables, 2026-09-12 vs. the 7 days before, 09-05 to 09-11)**
- `gold_daily_approval`: the approval rate was 93.6%, against 93.8% in the prior week. The dip is small and company-wide.
- `gold_decline_reasons`:
  - Total code 91 declines were 593, against a baseline of 447.3 per day.
  - Trujillo Credit Union code 91 declines were 178, against a baseline of 11.3 per day (15.8×). That's an increase of about 167 per day, which is more than the whole company-wide increase of about 146, so other issuers' 91 declines were slightly lower.
  - The Trujillo spike hit every region that day: US-Midwest 40, US-South 34, US-West 31, US-Northeast 27, CA 15, DE 15, UK 13, BR 3. On the days around it, Trujillo had only 1–5 code 91 declines per region.
  - Trujillo's code 91 declines were back to 1–3 per region on 09-13.
- Codes 05 (1,883 vs. 1,995 average) and 51 (1,386 vs. 1,310) were close to normal.
- `gold_declines_by_category` shows code 91 rising in Fuel ecommerce (25 vs. 12.7) and Rideshare and taxi ecommerce (30 vs. 18.9). Those increases are modest, and I did not link them to Trujillo.

**Why it happened:** `issuer-status-notices.md`, section "Trujillo Credit Union: unplanned host outage (2026-09-12)", says:
- Trujillo's authorization host lost its database connection at about 14:00 UTC.
- Requests to Trujillo failed or timed out, so we returned code 91.
- Trujillo confirmed recovery at 17:00 UTC.
- We found no fault on our side, and stand-in processing was not enabled for this issuer.

`response-code-guide.md`, section "91: Issuer unavailable", fits this. A sharp rise for one issuer across all regions points to that issuer's systems being down. A rise for all issuers in one region would point to our network or gateway, and that isn't what the data shows.

**What I could not confirm**
- **Hours:** The decline tables are daily, so I could not check the 14:00–17:00 UTC window from the data. The notice's timing and the daily spike agree, but I did not verify the hours.
- **Cause:** The root cause is the issuer's own account. I haven't seen the root-cause report, which the notice says Issuer Relations is requesting.
- **Latency:** `daily_ops_summary` reported no latency spikes for the day, so I found no sign of a problem on our side. That absence doesn't prove there was none.
- **Merchants:** I can't tie the specific merchants' complaints to Trujillo cardholders. The tables have no merchant or issuer-by-merchant breakdown.
- **Other increases:** Code 51 was about 1.4× normal for a few issuers, and Restaurants ecommerce code 14 was 2.6× (21 vs. 8). These are small and I did not investigate them.
- **Stand-in:** The notice says stand-in processing was off for Trujillo and mentions a follow-up to discuss enabling it. Whether it would have prevented these declines is untested.
