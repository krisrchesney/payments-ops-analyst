# Runbook: a decline code spikes across many issuers

*Synthetic document. Owner: Payments Operations and Fraud Strategy.*

## When to use this runbook
Use it when one decline code, most often 59 (suspected fraud), rises at **many issuers at the same time**, usually in one merchant category or channel.

## Step 1: Slice it
- Break the declines down by merchant category (MCC), channel (ecommerce, card-present, contactless, card-on-file) and issuer.
- A rise in one category and one channel, spread across many issuers, almost always comes from a processor-side rule, not from the banks.

## Step 2: Check the fraud rule change log
- Look for any rule that went live in the 48 hours before the spike and that targets that category or channel.
- Compare the rule's expected effect with what you see. A much bigger effect than estimated means the threshold is too tight.

## Step 3: Decide: keep, adjust or roll back
- Get Fraud Strategy and a sample of the declined transactions.
- If most declined transactions look legitimate (false positives), roll back the rule or loosen the threshold.
- Weigh fraud prevented against good sales lost. Lost sales at large merchants also bring complaints and churn.

## Step 4: Tell merchants
- If large merchants are affected, Merchant Support tells them what happened and when it was fixed.

## Step 5: Close out
- Record the rule ID, the time the spike started and ended, the extra declines and the decision.
- New rules on high-value categories should launch to a small share of traffic first.
