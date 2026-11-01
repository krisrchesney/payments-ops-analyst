# Platform change log

*Synthetic document. Owner: Platform Engineering. Changes to authorization infrastructure (gateways, databases, network links). Times are UTC.*

## CHG-7702: DE database patch (2026-09-05)
- **Change:** security patch on the DE region's authorization database replicas, 02:00–02:40 UTC.
- **Impact:** none expected. Traffic failed over to the other replica during the patch.
- **Status:** complete.

## CHG-7715: US-West gateway autoscaling (2026-09-10)
- **Change:** raised the minimum number of US-West gateway servers from 6 to 8.
- **Why:** headroom ahead of holiday traffic.
- **Status:** complete.

## CHG-7731: UK gateway connection-pool change (2026-09-17)
- **Change:** at 08:55 UTC, the UK authorization gateway's connection pool to the card network was reduced from 400 to 120 connections as part of a cost review.
- **Observed:** requests queued at the gateway. On-call saw p95 authorization latency in the UK rise sharply from about 09:00 UTC.
- **Rollback:** pool restored to 400 at 10:58 UTC; latency returned to normal by 11:00 UTC.
- **Approval impact:** none measured; requests were slow but completed.
- **Follow-up:** load test any connection-pool change in staging first; add a p95 latency alert per region.

## CHG-7744: Logging library upgrade (2026-09-24)
- **Change:** upgraded the logging library on all gateways, rolling, region by region.
- **Impact:** none expected or seen.
- **Status:** complete.

## CHG-7750: BR network link maintenance (2026-09-27)
- **Change:** carrier maintenance on the backup network link for BR, 04:00–05:00 UTC. The primary link carried all traffic.
- **Impact:** none.
