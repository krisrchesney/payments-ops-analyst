# MCP server

A local Python MCP server that gives Claude Desktop or Claude Code read-only tools over the gold tables and the ops documents.

| Tool | What it does |
|---|---|
| `list_metrics` | Tables, columns, date ranges and what each response code means |
| `query_gold` | One read-only SELECT against the gold tables |
| `compare_periods` | A metric by a dimension, period A vs period B, biggest changes first |
| `top_decline_drivers` | Which issuer and code, or category, channel and code, rose most vs a baseline |
| `daily_ops_summary` | One day's approval rate, top decline reasons and latency spikes |
| `search_runbooks` | Search the ops documents by meaning, and return sections with the file and heading to cite |

**Safeguards.** The gold tools run on an in-memory DuckDB with file and network access off and settings locked, and `query_gold` accepts only a single SELECT. `search_runbooks` is the one tool that reaches Databricks, and it only queries the index. It signs in with a CLI profile name (`PAYOPS_DATABRICKS_PROFILE`, default `DEFAULT`), so no token is in the code. Its description tells the agent to treat document text as evidence, not as instructions.

## Set up

1. Sign in with the Databricks CLI.
2. Run `.venv\Scripts\python mcp_server\export_gold.py` to copy the gold tables to `exports/`.
3. Open Claude Code in the repo root. `.mcp.json` registers the server.

## Check it

- `.venv\Scripts\python -m pytest -q tests` runs the tool tests with small fake tables and a fake search. No Databricks needed.
- `.venv\Scripts\python mcp_server\check_retrieval.py` asks the live index 6 questions and checks that the expected document is in the top 3.
