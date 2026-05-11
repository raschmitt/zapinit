#!/usr/bin/env python3
"""Post AI code review findings as resolvable inline PR comments."""

import json
import os
import re
import subprocess
import sys

REVIEW_TEXT_FILE = "/tmp/ai-review.md"
MARKER = "<!-- ai-review -->"
REPO = "raschmitt/zapinit"

# Matches: - `path/to/file.py:42` - severity: high - Short title: Description.
ISSUE_RE = re.compile(
    r'-\s+`([^:`]+):(\d+)(?:-\d+)?`\s*-\s*severity:\s*(high|medium|low)\s*-\s*([^:]+):\s*(.+)',
    re.IGNORECASE,
)
SEVERITY_BADGE = {
    "high": ("P1", "orange"),
    "medium": ("P2", "yellow"),
    "low": ("P3", "blue"),
}


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
    result = run_gh("api", f"repos/{REPO}/pulls/{pr_number}/files", "--jq", ".")
    files = json.loads(result.stdout)
    diff_lines: dict[str, set[int]] = {}
    for f in files:
        diff_lines[f["filename"]] = _parse_patch_lines(f.get("patch", ""))
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


def parse_findings(text: str) -> list[tuple[str, int, str, str, str]]:
    """Return (path, line, severity, title, description) for each finding."""
    m = re.search(r'### Issues Found\n(.*?)(?=\n###|\Z)', text, re.DOTALL)
    if not m:
        return []
    findings = []
    for match in ISSUE_RE.finditer(m.group(1)):
        findings.append((
            match.group(1),
            int(match.group(2)),
            match.group(3).lower(),
            match.group(4).strip(),
            match.group(5).strip(),
        ))
    return findings


def format_comment(severity: str, title: str, description: str) -> str:
    priority, color = SEVERITY_BADGE.get(severity, ("P2", "yellow"))
    badge = f"![{priority} Badge](https://img.shields.io/badge/{priority}-{color}?style=flat)"
    return f"**<sub><sub>{badge}</sub></sub>  {title}**\n\n{description} {MARKER}"


def post_inline_comment(pr_number: str, path: str, line: int, body: str, commit_id: str) -> int:
    payload = json.dumps({
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "line": line,
        "side": "RIGHT",
    })
    result = run_gh(
        "api", f"repos/{REPO}/pulls/{pr_number}/comments",
        "-X", "POST",
        "--input", "-",
        stdin=payload,
    )
    return json.loads(result.stdout)["id"]


def add_reactions(comment_id: int, reactions: list[str]) -> None:
    for reaction in reactions:
        run_gh(
            "api", f"repos/{REPO}/pulls/comments/{comment_id}/reactions",
            "-X", "POST",
            "--input", "-",
            stdin=json.dumps({"content": reaction}),
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

    posted = 0
    skipped = 0
    for path, line, severity, title, description in findings:
        if path not in diff_lines or line not in diff_lines[path]:
            print(f"Skipping {path}:{line} — not in diff")
            skipped += 1
            continue
        body = format_comment(severity, title, description)
        comment_id = post_inline_comment(pr_number, path, line, body, commit_id)
        add_reactions(comment_id, ["eyes", "+1"])
        print(f"Posted inline comment on {path}:{line} (id={comment_id})")
        posted += 1

    print(f"Done: {posted} inline comment(s) posted, {skipped} skipped (not in diff)")


if __name__ == "__main__":
    main()
