#!/usr/bin/env python3
"""Produces a structured summary of the diff between the current branch and main.

Usage:
    python3 analyze_diff.py

Output is JSON intended to be read by the agent before building the PR JSON.
"""

import json
import os
import re
import subprocess
import sys


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
    )
    if result.returncode != 0:
        raise RuntimeError(
            (result.stderr or result.stdout).strip() or f"git {' '.join(args)} failed"
        )
    return result.stdout.strip()


def ensure_repo() -> None:
    try:
        inside = run_git(["rev-parse", "--is-inside-work-tree"])
    except RuntimeError as exc:
        raise RuntimeError("Not inside a git repository") from exc
    if inside != "true":
        raise RuntimeError("Not inside a git repository")


def get_branch_name() -> str:
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"])


def get_changed_files() -> list[dict]:
    output = run_git(["diff", "--name-status", "main...HEAD"])
    files = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        files.append({"status": parts[0], "path": parts[-1]})
    return files


def get_diff_stat() -> dict:
    output = run_git(["diff", "--shortstat", "main...HEAD"])
    stat = {"files": 0, "insertions": 0, "deletions": 0}
    if not output:
        return stat
    if m := re.search(r"(\d+) files? changed", output):
        stat["files"] = int(m.group(1))
    if m := re.search(r"(\d+) insertions?\(\+\)", output):
        stat["insertions"] = int(m.group(1))
    if m := re.search(r"(\d+) deletions?\(-\)", output):
        stat["deletions"] = int(m.group(1))
    return stat


def get_commit_subjects() -> list[str]:
    output = run_git(["log", "--format=%s", "main..HEAD"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_diff_excerpt() -> str:
    output = run_git(["diff", "--unified=0", "--no-color", "--minimal", "main...HEAD"])
    lines = output.splitlines()
    return "\n".join(lines[:400])


def main() -> None:
    try:
        ensure_repo()
        payload = {
            "branch_name": get_branch_name(),
            "diff_range": "main...HEAD",
            "diff_stat": get_diff_stat(),
            "changed_files": get_changed_files(),
            "commit_subjects": get_commit_subjects(),
            "diff_excerpt": get_diff_excerpt(),
        }
        print(json.dumps(payload, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
