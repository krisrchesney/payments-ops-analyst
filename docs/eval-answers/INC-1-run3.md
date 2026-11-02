# INC-1-run3

*The agent's answer, unedited. All data and documents are synthetic.*

**Question:** Several merchants said more cards than usual were declined on September 12. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

---

2026-11-02 (CST; the current time isn't available to me)

**What moved:** Trujillo Credit Union started returning code 91 (issuer unavailable) in every region on September 12. Nothing else moved by much, so the effect was small overall.

**Numbers from the gold tables** (baseline is Sept 5–11, from `gold_decline_reasons`, `gold_daily_approval` and `gold_declines_by_category`):
- **Trujillo, code 91:** 178 declines on Sept 12 against about 11.3 a day in the baseline, roughly 15.8 times higher. It was the largest mover by a wide margin. The next largest increase was about 12 a day.
- **Spread:** Trujillo's declines appeared in 7 regions: US-Midwest 40, US-South 34, US-West 31, US-Northeast 27, CA 15, DE 15 and UK 13 (BR had 3). The days around it had only 1–5 per region, and Sept 13 was back to normal.
- **Code 91 overall:** 593 declines against a baseline of 447.3 a day, an increase of about 146. Trujillo's increase of about 167 more than accounts for it.
- **Approval rate:** 93.60% against 93.81% in the previous 7 days. The lowest regions were DE at 93.33%, CA at 93.41% and US-South at 93.48%.
- **Other codes:** Code 05 was lower than baseline (1,883 against 1,995.4). Code 51 was slightly higher (1,386 against 1,310.4), with several issuers up about 1.4 times. That is a modest rise, and the response-code guide says it rarely points to a system problem.
- **Latency:** The daily summary showed no hours where p95 latency was over twice normal, so our own gateway looks healthy.

**Why it happened:** `issuer-status-notices.md`, section "Trujillo Credit Union: unplanned host outage (2026-09-12)", says:
- The issuer's authorization host lost its database connection at about 14:00 UTC.
- Requests failed or timed out, so we answered with code 91.
- The issuer confirmed recovery at 17:00 UTC.
- We found no fault on our side.
- Stand-in processing was not enabled for Trujillo.

`response-code-guide.md`, section "91: Issuer unavailable", supports this reading. A sharp rise at one issuer across regions points to that issuer's systems. A rise across all issuers in one region would point to our network. The pattern here is the first kind.

The document's date and scope fit the data: it names Trujillo, Sept 12 and code 91, and the spike is one issuer on that one day.

**What I could not confirm:**
- **Hours:** The decline tables are daily, so I couldn't check that Trujillo's declines fell inside 14:00–17:00 UTC. That timing comes only from the notice.
- **Root cause:** The notice gives the issuer's own description. The root-cause report is still a follow-up with Issuer Relations.
- **Stand-in:** I can't say how many declines stand-in would have prevented.
- **Merchants:** I have no merchant-level data, so I can't tie this to the specific merchants who complained. The category breakdown shows code 91 up for Fuel (ecommerce) and Rideshare (ecommerce), but it has no issuer column, so I can't link those to Trujillo.
- **Other increases:** The smaller rises (code 51 at Airlines and Fuel, code 14 at Restaurants ecommerce) have no documented explanation. They are small next to the Trujillo effect.

Overall, the 0.2-point dip in approval rate seems too small to explain merchants noticing, unless they mostly serve Trujillo cardholders. If those merchants can send their affected card BINs or issuers, that would confirm it.
