# MCP server (week 3)

A local Python MCP server that exposes the exported gold tables to Claude Desktop or Claude Code, through DuckDB.

Planned tools: `list_metrics`, `query_gold` (read-only SQL against gold tables), `compare_periods` (metric by dimension, period A vs B), `top_decline_drivers`.

Guide: https://modelcontextprotocol.io/docs/develop/build-server (Python SDK, `mcp[cli]`).

Built after the gold tables exist, so the tools match real columns.
