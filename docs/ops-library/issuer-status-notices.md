# Issuer status notices

*Synthetic document. Owner: Issuer Relations. Notices that issuing banks send us about planned maintenance or unplanned outages on their side. Times are UTC.*

## Dixon Financial: planned maintenance (2026-09-06)
- **Window:** 03:00–03:30 UTC.
- **Expected effect:** authorizations may decline with code 91 (issuer unavailable) during the window. Low traffic at that hour.
- **Notice received:** 2026-09-01.

## Trujillo Credit Union: unplanned host outage (2026-09-12)
- **Reported by issuer:** 2026-09-12 at 14:20 UTC, after our on-call saw their declines rise.
- **Issuer's description:** their card authorization host lost its database connection at about 14:00 UTC. Requests to them failed or timed out, so we answered with code 91 (issuer unavailable).
- **Resolved:** issuer confirmed recovery at 17:00 UTC.
- **Our side:** no fault found in our systems. Stand-in processing was not enabled for this issuer.
- **Follow-up:** Issuer Relations to ask Trujillo Credit Union for a root-cause report and to discuss enabling stand-in.

## Lopez Bank: planned maintenance (2026-09-20)
- **Window:** 05:00–05:20 UTC.
- **Expected effect:** short burst of code 91.
- **Notice received:** 2026-09-14.

## Miller Credit Union: BIN range migration (2026-09-28)
- **Change:** moving some cards to a new BIN range. No downtime expected.
- **Notice received:** 2026-09-15.
