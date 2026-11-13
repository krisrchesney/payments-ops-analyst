# Why this exists

*Written November 2026. Everything here is synthetic data; nothing is real payment data or employer work.*

## In 30 seconds

When more card payments than usual start getting declined, someone has to work out what changed and why. This project tries to do that job with software. It builds daily reports from simulated payments, and an AI assistant uses them to answer "what moved, and why?" It shows the numbers it used and the document that explains the cause.

## Why I built it

I wanted to see whether an AI assistant could do the detective work of finding what moved in payment data and why, and to test it honestly instead of just demoing it working once. Payments gave me problems with clear causes to plant.

## How it works

1. **Make the data.** A script writes 2 million fake card payments and plants three problems on purpose: a bank outage, a slow connection and a fraud rule change. The answer key is kept where the assistant can't see it.
2. **Build the reports.** A pipeline on Databricks, a cloud data platform, turns the data into daily tables.
3. **Give the assistant read-only tools.** It can look up the reports and search a small library of fake documents, such as guides for handling problems and logs of changes. It can't change anything.
4. **Ask a question** and check the answer against the key. [See an example answer.](docs/sample-why-answer-week-of-2026-09-21.md)

## Choices I made, and why

- **Fake data with a hidden answer key**, so I can tell whether the assistant is right.
- **Reports plus documents.** The numbers show what moved, and the documents explain why.
- **Pass rules written before any test, with no retakes.** Wrong answers stay in the results.
- **The assistant runs on my own computer**, on my Claude subscription, because the free tools I used can't call it.
- **When the problem detector missed a case, I didn't adjust it to fit.** That would have hidden the result.
- **Claude Code wrote the Python under my direction.** I set the requirements, reviewed the code, ran the deployments and tests, and checked the numbers.

## What I found

- **The assistant:** I asked four questions three times each. 8 of the 12 answers passed. When a question pointed toward the problem, it found the real cause every time, but two answers had a wrong number, so a person still has to check them. With no hint, it found all three problems in only 1 of 3 answers. [Full results.](docs/eval.md)
- **The problem detector:** in a fair test with four newly planted problems, it caught two of the three it should catch, narrowly missed one, and raised no false alarms. [Full results.](docs/detection.md)

**What not to trust:** I wrote the data, the documents and the questions myself, and the simulated data has no weekends or busy hours. These results show the method works. They don't predict how it would do at a real company.

## What's not finished

- The dashboard and daily alert are built but not deployed, so nobody is told about a problem yet.
- There is no demo recording.
- The detector's cutoff for flagging is probably too strict. I'd test a lower one on fresh data.

## Where to look

[Project page](https://krisrchesney.github.io/payments-ops-analyst/) · [Test results](docs/eval.md) · [Detector write-up](docs/detection.md) · [Product brief](docs/product/brief.md)
