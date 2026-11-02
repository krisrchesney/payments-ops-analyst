"""Does the real search find the right document? (PAYOPS-67)

Asks the live Vector Search index a fixed set of plain-English questions and checks that the expected
section or file is in the top 3. The questions avoid rule IDs and change numbers on purpose.
Needs Databricks access, so it is a separate script and not part of the pytest run.

Run:
  .venv\\Scripts\\python mcp_server\\check_retrieval.py
Exits with 1 if any question misses.
"""
import sys

import server

TOP_K = 3

# question -> what counts as a hit: an exact chunk_id, or a file name for "any section of this file"
CASES = {
    "Why were online electronics purchases being declined as suspected fraud in late September?":
        ["fraud-rule-change-log.md#05", "fraud-rule-change-log.md#06"],
    "What changed in the UK that could make authorizations slow on September 17?":
        ["platform-change-log.md#03"],
    "Which bank had an outage around September 12 causing timeouts?":
        ["issuer-status-notices.md#02"],
    "One bank's declines suddenly spiked. What should I do first?":
        ["runbook-issuer-down.md"],
    "Authorization latency jumped in one region. How do I respond?":
        ["runbook-latency-spike.md"],
    "What does response code 91 mean and who owns it?":
        ["response-code-guide.md"],
}


def main():
    misses = 0
    for question, expected in CASES.items():
        r = server.search_runbooks(question, k=TOP_K)
        if "error" in r:
            sys.exit(r["error"])
        hit = any(s["chunk_id"] in expected or s["source_file"] in expected for s in r["results"])
        misses += not hit
        print(f"\n{'HIT ' if hit else 'MISS'}  {question}")
        for s in r["results"]:
            print(f"      {s['score']:.3f}  {s['chunk_id']}  |  {s['heading']}")
    print(f"\n{len(CASES) - misses} of {len(CASES)} questions found the expected document in the top {TOP_K}.")
    sys.exit(1 if misses else 0)


if __name__ == "__main__":
    main()
