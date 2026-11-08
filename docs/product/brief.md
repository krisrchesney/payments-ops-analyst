# Product brief: Payments Ops Analyst

*A personal project on simulated data. Nobody has bought or used this. The customer, value and pricing below are reasoned assumptions that haven't been tested with real customers.*

## Customer

The buyer is the head of payment operations at a company that handles card authorizations for many banks or merchants, such as a payment processor. The daily user is the operations analyst on shift, and the operations manager reads the daily note.

Processors are the first target because they see the same problem across many banks and merchants, and they run rules of their own that can cause it.

## Problem

When approvals drop, an analyst has to do two jobs by hand. First they slice reports by region, bank, merchant category and channel to find what moved. Then they search change logs, bank notices and runbooks to find out why.

Two things make this costly:
- **Each wrongly declined payment is a lost sale.** The longer a cause takes to find, the more sales it costs.
- **Small problems get missed.** In this project's data, a bank outage moved the overall approval rate by only about 0.2 points.

## Offer

An assistant that answers "what changed, where and why?" in plain English, from the company's own reports and documents.

- **It shows its evidence:** each answer names the numbers and the document section behind it, and says what it couldn't confirm.
- **It can't change anything:** its tools are read-only, and it doesn't touch authorization decisions.
- **It drafts the daily note:** the analyst's findings also become a short note for the manager to edit and send.

**What the evaluation says about it today**
- When a question pointed to a problem, it found the true cause in 9 of 9 runs.
- 2 of those 9 answers had a wrong figure, so a person still needs to check the numbers.
- With no hint, only 1 of 3 runs found all three planted problems, and nothing alerts anyone yet. A real product would need [automatic detection](https://krisrchesney.github.io/payments-ops-analyst/roadmap.html). A first version exists and had one small [independent test](../detection.md#the-independent-test): 2 of 3 expected catches, 1 narrow miss, no false alarms. It is still checked only on simulated data.

These results come from [simulated data and documents](../eval.md), so they don't predict performance on a real company's data.

## Pricing

**The hypothesis:** a price tier based on transaction volume, with a minimum annual fee.

| Option | Why or why not |
|---|---|
| **Volume tier with a minimum fee (chosen)** | The value comes from approvals recovered and investigation hours saved, and both grow with volume. Payments buyers are used to volume-based pricing, and the minimum fee covers smaller customers |
| Price per user | Only a few analysts would use it, so this would charge very little for a large company's value |
| Free with existing reporting | Easier to adopt, but it hides the product's value and makes it hard to justify on its own. A vendor that already sells reporting could offer it as a paid add-on instead |

No price is set, because there's no evidence yet to base one on.

## What would need to be true

Before building this as a real product, these need testing with real operations teams:

1. **Time saved:** how long do investigations take today, and how much does this shorten them?
2. **Trust:** will analysts rely on it if they still have to check the figures?
3. **Data access:** will a company connect its reports and internal documents to an AI tool, and under what security terms?
4. **Real documents:** does search still find the right answer in real change logs, which are messier than these?
5. **Willingness to pay:** does the value justify a volume-based price?
