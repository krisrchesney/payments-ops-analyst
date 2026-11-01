# Runbook: one issuer's declines spike

*Synthetic document. Owner: Payments Operations.*

## When to use this runbook
Use it when code 91 (issuer unavailable) or code 05 rises sharply for **one issuer** while other issuers look normal. A common trigger is more than 5 times that issuer's usual hourly code 91 count.

## Step 1: Confirm it is one issuer
- Compare the issuer's declines by code against its own last 7 days.
- Check that other issuers in the same region are normal. If they're not, use the latency runbook instead, because it may be our network.

## Step 2: Check for a notice
- Look in issuer status notices for planned maintenance in that window.
- If it's planned and short, note it in the daily ops note and take no other action.

## Step 3: Contact the issuer
- If there's no notice, Issuer Relations contacts the issuer's operations desk.
- Ask: is your authorization host up, and when did it start?

## Step 4: Consider stand-in processing
- Stand-in lets us approve low-risk transactions for the issuer while it's down, within limits the issuer agreed to.
- It's only possible if the issuer has signed up for stand-in. Check the issuer profile.

## Step 5: Close out
- Record the start and end times, the count of declines and the issuer's explanation.
- Ask the issuer for a root-cause report within 5 business days.
