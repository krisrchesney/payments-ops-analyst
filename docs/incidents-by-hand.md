# Incidents found by hand (PAYOPS-43)

Found from the gold tables (and silver for one drill-down) in the Databricks notebook `03_find_incidents`, before looking at `incidents.json`. Checked against the answer key afterwards.

| Incident | When | Where | What moved | Cause | Answer key |
|---|---|---|---|---|---|
| **INC-1** | Sep 12, 2026 | Trujillo Credit Union (all regions) | Code `91` (issuer unavailable): **178** declines that day vs ~20 for a normal issuer-day; next-highest issuer-day all month was 26. Sep 12 was the 4th-lowest approval day company-wide (93.60%). | The issuer stopped answering: an issuer outage. | ✅ issuer outage, I020 Trujillo Credit Union, Sep 12 14:00 to 17:00 UTC |
| **INC-2** | Sep 17, 2026, 09:00 to 11:00 UTC | UK | Hourly p95 latency **2,016 to 2,084 ms** vs ~348 ms typical; approvals unaffected. | Slow authorizations in the UK. | ✅ latency spike, UK (found in PAYOPS-12) |
| **INC-3** | Sep 22 to 24, 2026 | Electronics, ecommerce (all regions) | Code `59` (suspected fraud): **856 / 891 / 869** a day vs ~210 normal; **1,994** of the code-59 declines on those days were Electronics ecommerce vs ~30 for any other category and channel. Electronics in stores only 28. | A fraud rule tightened on online electronics purchases. | ✅ fraud rule tightened, MCC 5732 Electronics, ecommerce, Sep 22 to 25 |

## How each was found

- **INC-3 showed first, as a dip:** the lowest region-days were almost all Sep 22 to 24, across every region, which pointed at something not regional. Charting declines by code per day showed code `59` jumping about 4×; silver showed it was Electronics ecommerce.
- **INC-1 was hidden at day × region level** (one issuer is ~1 in 40 transactions, for a few hours). It showed up by filtering to code `91` (the bank didn't respond) and ranking issuer-days.
- **INC-2 was hidden in whole-month averages** and obvious in the hourly table.

**Lesson:** averages over long periods or big groups hide short or narrow incidents; slice by time, by code and by the entity that could fail.

*All data is synthetic.*
