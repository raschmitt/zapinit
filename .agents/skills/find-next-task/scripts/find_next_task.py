#!/usr/bin/env python3
"""Identifies the next available task from docs/tasks.md.

Outputs JSON with the first task that is:
  - not crossed out in tasks.md (not done)
  - not referenced in any open PR title as (T-XX)
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def get_open_pr_task_ids() -> set[str]:
    result = subprocess.run(
        ["gh", "pr", "list", "--json", "title", "--state", "open"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Warning: could not fetch open PRs: {result.stderr}", file=sys.stderr)
        return set()

    prs = json.loads(result.stdout)
    task_ids: set[str] = set()
    for pr in prs:
        match = re.search(r"\(T-(\d+)\)", pr["title"])
        if match:
            task_ids.add(f"T-{match.group(1)}")
    return task_ids


def find_next_task(tasks_file: str = "docs/tasks.md") -> None:
    content = Path(tasks_file).read_text()
    open_pr_ids = get_open_pr_task_ids()

    # Matches:  ### T-04 · Some Name        (available)
    #           ### ~~T-01 · Some Name~~     (done)
    header_re = re.compile(r"^### (~~)?(T-\d+) · (.+?)(~~)?$", re.MULTILINE)

    for m in header_re.finditer(content):
        is_done = bool(m.group(1))
        task_id = m.group(2)
        task_name = m.group(3).strip()

        if is_done:
            continue

        if task_id in open_pr_ids:
            continue

        print(json.dumps({"id": task_id, "name": task_name}))
        return

    print(json.dumps({"id": None, "name": None, "message": "no available tasks"}))


if __name__ == "__main__":
    tasks_file = sys.argv[1] if len(sys.argv) > 1 else "docs/tasks.md"
    find_next_task(tasks_file)
