# Week 1 (about 20 hours)

Goal: by the end of the week, data is landed in Databricks, bronze and silver run, and the product docs exist. Do the product work (project 3) in the same week so the backlog drives the build.

## Day 1: product first (3 h)
- [ ] Read the Scrum Guide (about 1 h): https://scrumguides.org/scrum-guide.html
- [ ] Take the free Product Owner Open assessment once to get a baseline: https://www.scrum.org/open-assessments/product-owner-open
- [ ] Edit `docs/product/PRD.md`: answer the open questions in your own words.
- [ ] Create a free Jira site (up to 10 users): https://www.atlassian.com/software/jira/pricing. Make a Scrum project "PAYOPS" and enter the epics and stories from `docs/product/backlog.md`. Plan Sprint 1 with the stories marked S1.

## Day 2: Databricks setup (3 h)
- [ ] Sign up for Databricks Free Edition: https://www.databricks.com/learn/free-edition
- [ ] Read PySpark Getting Started and run the DataFrame live notebook: https://spark.apache.org/docs/latest/api/python/getting_started/index.html
- [ ] In Catalog, create schema `workspace.payments` and volume `landing`.

## Day 3: land the data (3 h)
- [ ] Run the generator locally: `.venv\Scripts\python generator\generate_auths.py --rows 2000000 --out out`
- [ ] Upload `out/authorizations`, `out/chargebacks`, `merchants.parquet`, `issuers.parquet` to the `landing` volume. Keep `incidents.json` local; it's the answer key.
- [ ] In a notebook, `spark.read.parquet(...)` each one, check counts, `printSchema()`, and try 5 queries by hand (approval rate by region, top decline codes, p95 latency by region).

## Day 4 and 5: bronze and silver (8 h)
- [ ] Read the Spark Declarative Pipelines overview: https://docs.databricks.com/aws/en/ldp/
- [ ] Build bronze and silver per `pipelines/README.md`. Write it yourself; use Claude to explain errors and review.
- [ ] Add the expectations and look at the dropped-row counts.
- [ ] Read the Delta Lake docs on time travel and schema evolution: https://docs.delta.io/index.html

## End of week (3 h)
- [ ] Sprint 1 review and retro notes in `docs/product/sprints/sprint-1.md` (template there).
- [ ] Commit, and tick the boxes in the README's Status list.

Week 2: gold tables, finding the three incidents by hand, export. Week 3: MCP server and agent evaluation. Week 4: demo recording, release notes, product brief.
