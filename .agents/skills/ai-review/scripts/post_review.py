#!/usr/bin/env python3
"""Post an AI code review as a PR review with resolvable inline comments."""

import json
import os
import re
import subprocess
import sys

REVIEW_TEXT_FILE = "/tmp/ai-review.md"
MARKER = "<!-- ai-review -->"
REPO = "raschmitt/zapinit"

# Matches lines like: - `path/to/file.py:42` - description - severity: high
ISSUE_RE = re.compile(r'-\s+`([^:`]+):(\d+)(?:-\d+)?`\s*[-—]\s*(.+)')


def run_gh(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=True,
    )


def get_head_sha(pr_number: str) -> str:
    result = run_gh("api", f"repos/{REPO}/pulls/{pr_number}", "--jq", ".head.sha")
    return result.stdout.strip()


def get_diff_lines(pr_number: str) -> dict[str, set[int]]:
    """Return {file_path: set_of_line_numbers} for lines present in the PR diff."""
    result = run_gh("api", f"repos/{REPO}/pulls/{pr_number}/files", "--jq", ".")
    files = json.loads(result.stdout)
    diff_lines: dict[str, set[int]] = {}
    for f in files:
        path = f["filename"]
        patch = f.get("patch", "")
        diff_lines[path] = _parse_patch_lines(patch)
    return diff_lines


def _parse_patch_lines(patch: str) -> set[int]:
    lines: set[int] = set()
    current = 0
    for raw in patch.splitlines():
        if raw.startswith("@@"):
            m = re.search(r'\+(\d+)', raw)
            if m:
                current = int(m.group(1)) - 1
        elif raw.startswith("+") or raw.startswith(" "):
            current += 1
            lines.add(current)
    return lines


def parse_findings(text: str) -> list[tuple[str, int, str]]:
    """Extract (path, line, body) tuples from the Issues Found section."""
    m = re.search(r'### Issues Found\n(.*?)(?=\n###|\Z)', text, re.DOTALL)
    if not m:
        return []
    findings = []
    for match in ISSUE_RE.finditer(m.group(1)):
        path, line, body = match.group(1), int(match.group(2)), match.group(3).strip()
        findings.append((path, line, body))
    return findings


def post_review(pr_number: str, body: str, comments: list[dict], commit_id: str) -> None:
    payload = json.dumps({
        "commit_id": commit_id,
        "body": body,
        "event": "COMMENT",
        "comments": comments,
    })
    run_gh(
        "api", f"repos/{REPO}/pulls/{pr_number}/reviews",
        "-X", "POST",
        "--input", "-",
        stdin=payload,
    )


def main() -> None:
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER env var not set", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(REVIEW_TEXT_FILE):
        print(f"Review text not found: {REVIEW_TEXT_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(REVIEW_TEXT_FILE) as f:
        review_text = f.read()

    commit_id = get_head_sha(pr_number)
    diff_lines = get_diff_lines(pr_number)
    findings = parse_findings(review_text)

    comments = []
    skipped = 0
    for path, line, body in findings:
        if path in diff_lines and line in diff_lines[path]:
            comments.append({"path": path, "line": line, "body": body})
        else:
            skipped += 1

    post_review(pr_number, review_text, comments, commit_id)
    print(f"Posted PR review: {len(comments)} inline comment(s), {skipped} finding(s) in body only")


if __name__ == "__main__":
    main()
