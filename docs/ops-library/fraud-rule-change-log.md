# Fraud rule change log

*Synthetic document. Owner: Fraud Strategy team. Every change to a live fraud rule is logged here before it ships. Times are UTC.*

## FR-2031: Fuel pump pre-auth velocity (2026-09-02)
- **Change:** lowered the allowed number of fuel (MCC 5541) pre-authorizations per card from 6 to 4 in one hour.
- **Why:** card-testing attempts at unattended fuel pumps.
- **Expected effect:** very small. Under 0.05% more code 59 declines on fuel, card-present only.
- **Status:** live. Monitored for 7 days, no rise in complaints.

## FR-2033: Airline risk threshold relaxed (2026-09-04)
- **Change:** raised the risk-score threshold for airline (MCC 4511) ecommerce from 820 to 850, so fewer airline sales are declined.
- **Why:** follow-up to the August airline postmortem; the old threshold blocked good customers.
- **Expected effect:** slightly fewer code 59 declines on airlines.
- **Status:** live.

## FR-2036: Device fingerprint check for streaming (2026-09-09)
- **Change:** new rule scoring device fingerprints on streaming and cable (MCC 4899) card-on-file renewals.
- **Mode:** monitor only. It scores and logs but does not decline anything.
- **Status:** monitor only until at least 2026-10-15.

## FR-2038: Hotel no-show pattern (2026-09-15)
- **Change:** added a score boost for repeated hotel (MCC 7011) reservations from new cards in a short time.
- **Expected effect:** under 0.1% more code 59 on hotels, ecommerce.
- **Status:** live.

## FR-2041: Electronics card-not-present threshold tightened (2026-09-22)
- **Change:** at 2026-09-22 00:00 UTC, lowered the risk-score threshold for Electronics (MCC 5732) **ecommerce** from 780 to 640. Card-present and contactless electronics were not changed.
- **Why:** a rise in reported fraud on high-value electronics orders shipped to new addresses.
- **Expected effect, as estimated before launch:** about 1.5 times the normal code 59 (suspected fraud) declines on Electronics ecommerce.
- **Approved by:** Fraud Strategy lead. No A/B test was run; the rule went to 100% of traffic at once.
- **Status:** rolled back. See FR-2041-RB.

## FR-2041-RB: Rollback of the Electronics threshold (2026-09-25)
- **Change:** at 2026-09-25 00:00 UTC, restored the Electronics ecommerce threshold to 780.
- **Why:** merchant complaints and a much larger decline increase than estimated. Merchant Support reported many large electronics retailers seeing good customers declined.
- **Follow-up:** re-test the rule with a 10% traffic split before any new launch. Add code 59 by merchant category to the daily ops review.

## FR-2044: Rideshare card-on-file retune (2026-09-27)
- **Change:** small retune of the rideshare (MCC 4121) card-on-file model.
- **Expected effect:** none visible in daily totals.
- **Status:** live.
