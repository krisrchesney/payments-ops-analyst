"""Run the agent evaluation in docs/eval.md (PAYOPS-16).

Each run is a new Claude Code session in an empty folder with only the 6 tools from mcp_server, so the
agent can't read the answer key, the code or the write-ups in this repo. Answers go to docs/eval-answers/,
timings and search hits to docs/eval-answers/runs.json, and the full session logs to evals/logs/ (git-ignored).

Run from the repo root (needs Claude Code signed in, the Databricks CLI signed in, and exports/):
  python evals/run_eval.py
  python evals/run_eval.py --only INC-1 --runs 1
Set CLAUDE_CONFIG_DIR first to use a clean Claude Code profile.
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ANSWERS = REPO / "docs" / "eval-answers"
LOGS = REPO / "evals" / "logs"
MODEL = "claude-sonnet-5-5"
MAX_TURNS = 30
TOOL_PREFIX = "mcp__payments-ops__"

ASK = ("Find what moved, explain why it happened, cite any document you relied on, and back it up with "
       "numbers from the gold tables. Tell me anything you could not confirm.")
# question id -> opening line, documents that must appear in the top 3 of a search
QUESTIONS = {
    "INC-1": ("Several merchants said more cards than usual were declined on September 12.",
              ["issuer-status-notices.md"]),
    "INC-2": ("Some merchants said card payments felt slow one morning during the week of September 14.",
              ["platform-change-log.md"]),
    "INC-3": ("Approval rates looked off during the week of September 21.",
              ["fraud-rule-change-log.md"]),
    "OPEN": ("Review September 1 to 28. Is anything unusual, and why?",
             ["issuer-status-notices.md", "platform-change-log.md", "fraud-rule-change-log.md"]),
}


def mcp_config(folder):
    """The server definition, with this machine's paths, kept outside the repo."""
    python = REPO / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        python = REPO / ".venv" / "bin" / "python"
    config = {"mcpServers": {"payments-ops": {"command": str(python), "args": [str(REPO / "mcp_server" / "server.py")]}}}
    path = Path(folder) / "mcp.json"
    path.write_text(json.dumps(config))
    return path


def search_hits(events, documents):
    """For each required document: did it appear in the top 3 results of any search in this run?"""
    search_ids = {block["id"] for e in events if e.get("type") == "assistant"
                  for block in e["message"]["content"]
                  if block.get("type") == "tool_use" and block["name"] == TOOL_PREFIX + "search_runbooks"}
    found = set()
    for e in events:
        if e.get("type") != "user" or not isinstance(e["message"]["content"], list):
            continue
        for block in e["message"]["content"]:
            if block.get("type") != "tool_result" or block.get("tool_use_id") not in search_ids:
                continue
            content = block.get("content")
            text = content if isinstance(content, str) else "".join(c.get("text", "") for c in content)
            try:
                results = json.loads(text).get("results", [])
            except json.JSONDecodeError:
                continue
            found.update(r["source_file"] for r in results[:3])
    return {doc: doc in found for doc in documents}


def run_one(question_id, run, folder, config):
    opening, documents = QUESTIONS[question_id]
    command = [shutil.which("claude"), "-p", f"{opening} {ASK}", "--model", MODEL, "--max-turns", str(MAX_TURNS),
               "--tools", "", "--allowedTools", TOOL_PREFIX + "*", "--strict-mcp-config", "--mcp-config", str(config),
               "--setting-sources", "project", "--output-format", "stream-json", "--verbose"]
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    start = time.time()
    done = subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True, encoding="utf-8")
    seconds = round(time.time() - start, 1)

    name = f"{question_id}-run{run}"
    (LOGS / f"{name}.jsonl").write_text(done.stdout, encoding="utf-8")
    events = [json.loads(line) for line in done.stdout.splitlines() if line.startswith("{")]
    result = next((e for e in events if e.get("type") == "result"), {})
    tools = [block["name"].removeprefix(TOOL_PREFIX) for e in events if e.get("type") == "assistant"
             for block in e["message"]["content"] if block.get("type") == "tool_use"]
    usage = result.get("usage", {})

    answer = result.get("result") or ""
    (ANSWERS / f"{name}.md").write_text(
        f"# {name}\n\n*The agent's answer, unedited. All data and documents are synthetic.*\n\n"
        f"**Question:** {opening} {ASK}\n\n---\n\n{answer}\n", encoding="utf-8")
    print(f"{name}: {seconds}s, {len(tools)} tool calls, ended {result.get('subtype')}", flush=True)
    return {"id": name, "question": question_id, "run": run, "seconds": seconds, "turns": result.get("num_turns"),
            "tool_calls": len(tools), "tools": tools, "search_top3": search_hits(events, documents),
            "input_tokens": sum(usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
            "output_tokens": usage.get("output_tokens"), "ended": result.get("subtype"),
            "is_error": result.get("is_error", True), "exit_code": done.returncode}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--only", choices=list(QUESTIONS), help="run just this question")
    p.add_argument("--runs", type=int, default=3, help="runs per question")
    p.add_argument("--workers", type=int, default=3, help="sessions at the same time")
    a = p.parse_args()

    ANSWERS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    out = ANSWERS / "runs.json"
    done = {r["id"] for r in json.loads(out.read_text())} if out.exists() else set()   # a run is never repeated
    jobs = [(q, r) for q in ([a.only] if a.only else QUESTIONS) for r in range(1, a.runs + 1)
            if f"{q}-run{r}" not in done]
    with tempfile.TemporaryDirectory() as root:
        config = mcp_config(root)
        folders = [Path(root) / f"{q}-{r}" for q, r in jobs]
        for folder in folders:
            folder.mkdir()
        with ThreadPoolExecutor(a.workers) as pool:
            records = list(pool.map(lambda j: run_one(*j[0], j[1], config), zip(jobs, folders)))

    kept = json.loads(out.read_text()) if out.exists() else []
    out.write_text(json.dumps(sorted(kept + records, key=lambda r: r["id"]), indent=1) + "\n")
    print(f"wrote {len(records)} runs to {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
