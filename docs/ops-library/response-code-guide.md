# Response code guide

*Synthetic document. Owner: Payments Operations. ISO 8583 style response codes used in our authorization data, and who to talk to when one moves.*

## 00: Approved
The issuer approved the authorization. Approval rate = 00 responses / all authorizations.

## 05: Do not honor
A generic decline from the issuer, with no reason given. It is the largest decline code, about 45% of declines. It moves with issuer risk settings. A rise at a single issuer usually means that issuer changed something; ask Issuer Relations.

## 51: Insufficient funds
The cardholder doesn't have enough money or credit. It follows paydays and month-end and rarely points to a system problem.

## 54: Expired card
The card is past its expiry date. A rise often means a merchant has stale card-on-file data. It's a merchant issue, not a platform issue.

## 14: Invalid card number
The card number failed checks. A rise at one merchant can mean card testing (fraudsters trying lists of numbers); tell Fraud Strategy.

## 59: Suspected fraud
Declined because a fraud rule or model scored the transaction as risky. Rules can be ours (processor side) or the issuer's.
- If code 59 rises **at many issuers at once** in one merchant category or channel, suspect **our** fraud rules first and check the fraud rule change log.
- If it rises at **one issuer** only, it's likely the issuer's own fraud system.

## 91: Issuer unavailable
We could not reach the issuer, or the issuer timed out. A sharp rise for **one issuer** usually means that issuer's systems are down; check issuer status notices and follow the issuer-down runbook. A rise for **all issuers in one region** points to a network or gateway problem on our side; check the platform change log.
