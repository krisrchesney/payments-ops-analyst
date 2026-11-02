# Sample agent answer: why did approvals move? (Jira PAYOPS-68)

*All data and documents are synthetic. This is the agent's answer, followed by a check of each claim against the Databricks gold tables and the source documents.*

**The question**, asked in a new Claude Code session with the MCP server connected. The question gives no hint of the cause:

> Approval rates looked off during the week of September 21. Find what moved, explain why it happened, cite any document you relied on, and back it up with numbers from the gold tables. Tell me anything you could not confirm.

## The agent's answer

**What moved:** Approval rate fell on Sept 22, 23 and 24 only, and the drop came from one segment: Electronics (MCC 5732) ecommerce, response code 59 (suspected fraud). The week of Sept 21 as a whole looked only mildly worse (US-West −0.55 pts, other regions −0.15 to −0.5 pts). That is because the problem lasted 3 days.

**Why it happened:** Fraud rule FR-2041 went live on 2026-09-22 at 00:00 UTC. It lowered the risk-score threshold for Electronics ecommerce from 780 to 640, and it went to 100% of traffic with no A/B test. It was rolled back on 2026-09-25 at 00:00 UTC (FR-2041-RB), after merchant complaints and a much larger decline increase than the pre-launch estimate of about 1.5×.

**Numbers from the gold tables:**

| Check | Before | Sept 22–24 |
|---|---|---|
| Overall daily approval rate (`gold_daily_approval`) | 93.8% (Sept 21: 93.80%) | 93.03%, 92.75%, 93.02% |
| Electronics ecommerce code 59 declines per day (`gold_declines_by_category`) | about 8 (Sept 14–21 average) | 666, 678, 650 |
| Ecommerce channel approval rate (Sept 14–21 vs Sept 22–24) | 91.66% | 88.89% (−2.77 pts) |
| Other channels (same periods) | — | −0.2 to +0.2 pts |

- **Rollback:** Electronics code 59 was back to 10, 6 and 5 on Sept 25–27, and overall approval returned to 93.97%, 93.77% and 93.90%.
- **Regions:** Every region fell by 0.6–1.3 pts on the three bad days, with US-West and UK the largest. A region-wide drop fits a rule that applies to all traffic.
- **Size:** The roughly 650 extra declines a day lines up with the roughly 550–750 fewer approvals a day implied by the overall rate drop.
- **Overshoot:** Actual declines ran about 80× the 8-day baseline, versus the 1.5× the log estimated.

**Documents relied on** (via `search_runbooks`):

- `fraud-rule-change-log.md`, "FR-2041: Electronics card-not-present threshold tightened (2026-09-22)"
- `fraud-rule-change-log.md`, "FR-2041-RB: Rollback of the Electronics threshold (2026-09-25)"
- `response-code-guide.md`, "59: Suspected fraud". A rise at many issuers points to our own rules.
- `runbook-decline-spike.md`, "Step 2: Check the fraud rule change log"

I also saw `postmortem-2026-08-airline-rule.md`. It is an earlier, similar incident, and I did not use it as evidence for this one.

**What I could not confirm:**

- **Legitimate customers:** I can't confirm the declined customers were good ones. That claim rests only on the rollback entry's reference to merchant complaints. The gold tables hold no fraud-outcome labels.
- **Issuer breadth:** I couldn't show the decline was spread across issuers. The gold tables have no category-by-issuer view. My issuer check showed all 40 issuers with code 59 in both periods, which proves nothing. The "own rule, not one bank" reading comes from timing, the channel and category concentration, and the response-code guide.
- **Exact hours:** The gold approval and decline tables are daily. Matching the rule's 00:00 UTC start and stop to the hour would need hourly data, and only latency is hourly.
- **Rule cause:** The match between the rule and the numbers is on timing and scope. The data cannot isolate the 640 threshold as the cause. Nothing else in the gold tables points to a competing cause.
- **Other movers:** Hotels card-present code 05 (+13.7 a day, 1.2×) and Kelly Credit Union code 05 (+9.4 a day) rose slightly. These are too small to explain the drop, and I didn't investigate them.

## The check

Each figure was rerun as SQL on Databricks. The cited sections were read in the source documents.

| Claim | Result |
|---|---|
| Overall approval, Sep 21 to 27 | Matches: 93.80, 93.03, 92.75, 93.02, 93.97, 93.77, 93.90 |
| Electronics ecommerce code 59, Sep 22 to 27 | Matches: 666, 678, 650, 10, 6, 5 |
| Baseline of about 8 a day, Sep 14 to 21 | Matches: 7.75 |
| Ecommerce approval 91.66% to 88.89%; other channels within 0.2 pts | Matches: −0.19, −0.21, +0.19 |
| Week-over-week by region, and 0.6 to 1.3 pts on the bad days | Matches: bad-day drops run from 0.61 to 1.34 |
| About 550 to 750 fewer approvals a day | Matches: about 71,700 authorizations a day × 0.77 to 1.05 pts |
| Hotels +13.7 and Kelly Credit Union +9.4 | Matches |
| FR-2041 and FR-2041-RB details; the guide and runbook sections | Each cited section says what the agent claimed |
| **"About 80×" baseline** | **Slightly low.** 664.7 ÷ 7.75 is about 86× |

**One thing the agent could have shown.** It said it couldn't show the rise was spread across issuers. `gold_decline_reasons` does show this: code 59 rose at all 40 issuers (2.6× to 7.0×, median 4.3×), and the largest issuer accounts for only 3.5% of the rise. It had checked which issuers had code 59, not how much it rose. That doesn't change its conclusion, and it did tell the reader the gap was there.

**Limit of this test.** This is one question, and the documents were written for this project by someone who knew the planted incidents. The [full evaluation](eval.md) is 12 runs, and it blocks the agent from reading the rest of this repo.
