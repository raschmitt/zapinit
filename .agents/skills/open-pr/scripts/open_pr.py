#!/usr/bin/env python3
"""Opens a pull request for the current task using project conventions.

Usage:
    python3 open_pr.py <path-to-pr.json>

JSON schema:
    {
        "task_id":   "T-04",
        "task_name": "WhatsApp redirect",
        "title":     "feat(T-04): add WhatsApp URL builder",
        "what":      ["Add build_wa_url() helper", ...],
        "why":       ["Users need to open WhatsApp without saving contact", ...]
    }
"""

import json
import subprocess
import sys
from pathlib import Path


def build_body(task_id: str, task_name: str, what: list[str], why: list[str]) -> str:
    what_bullets = "\n".join(f"- {item}" for item in what)
    why_bullets = "\n".join(f"- {item}" for item in why)
    return (
        f"## Task/Issue\n"
        f"{task_id} · {task_name}\n\n"
        f"## What?\n"
        f"{what_bullets}\n\n"
        f"## Why?\n"
        f"{why_bullets}\n"
    )


def open_pr(pr_file: str) -> None:
    data = json.loads(Path(pr_file).read_text())

    required = {"task_id", "task_name", "title", "what", "why"}
    missing = required - data.keys()
    if missing:
        print(
            f"Error: missing fields in JSON: {', '.join(sorted(missing))}",
            file=sys.stderr,
        )
        sys.exit(1)

    body = build_body(data["task_id"], data["task_name"], data["what"], data["why"])

    push = subprocess.run(
        ["git", "push", "-u", "origin", "HEAD"],
        capture_output=True,
        text=True,
    )
    if push.returncode != 0:
        print(f"Error pushing branch:\n{push.stderr}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            "main",
            "--title",
            data["title"],
            "--body",
            body,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error opening PR:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(result.stdout.strip())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-pr.json>", file=sys.stderr)
        sys.exit(1)
    open_pr(sys.argv[1])
