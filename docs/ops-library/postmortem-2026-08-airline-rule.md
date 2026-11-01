# Postmortem: airline fraud rule blocked good customers (2026-08-11)

*Synthetic document. Owner: Fraud Strategy. A past incident, kept for learning.*

## Summary
On 2026-08-11, a new rule (FR-2019) lowered the risk-score threshold for airline (MCC 4511) ecommerce. Over the next 4 days, code 59 (suspected fraud) declines on airline ecommerce rose to about 12 times normal, at almost every issuer. Most declined bookings were legitimate.

## How it was found
- The daily ops review showed airline ecommerce approval rate down about 4 points.
- Slicing by issuer showed the rise everywhere, which pointed to our own rule rather than to banks.
- The fraud rule change log showed FR-2019 had gone live the same morning.

## What went wrong
- The rule launched to 100% of traffic at once, with no test group.
- The expected effect was estimated at 1.5 times normal declines; the real effect was about 12 times.

## Lessons
- Launch new rules on high-value categories to 10% of traffic first.
- Track code 59 by merchant category and channel in the daily review.
- When code 59 rises across many issuers in one category, check the fraud rule change log first.
