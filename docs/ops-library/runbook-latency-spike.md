# Runbook: authorization latency spike

*Synthetic document. Owner: Platform Engineering and Payments Operations.*

## When to use this runbook
Use it when p95 authorization latency in a region goes above 3 times its normal level for 15 minutes or more. Normal p95 is about 350 ms in most regions.

## Step 1: Find the scope
- Is it one region or all of them? One region points to that region's gateway or network link.
- Is it one issuer? If so, it's more likely the issuer's host; see the issuer-down runbook.

## Step 2: Check recent changes
- Look in the platform change log for anything in that region in the last 24 hours: gateway configuration, connection pools, network links, database patches.
- A change that started minutes before the spike is the first suspect.

## Step 3: Roll back first, investigate second
- If a recent change matches, roll it back. Then confirm that latency recovers within 15 minutes.

## Step 4: Check customer impact
- Slow authorizations can turn into timeouts (code 91) or abandoned checkouts.
- Compare the region's approval rate during the spike with the same hours on prior days.

## Step 5: Close out
- Record the start and end times, the peak p95, the change involved and the rollback time.
