#!/usr/bin/env python3
"""Post AI code review as a PR review with resolvable inline comments."""

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
# Low maps to P2 to match Codex (P1 orange, P2 yellow only)
SEVERITY_BADGE = {
    "high": ("P1", "orange"),
    "medium": ("P2", "yellow"),
    "low": ("P2", "yellow"),
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
    """Return {file_path: set_of_line_numbers} for every line present in the diff."""
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


def parse_verdict(text: str) -> str:
    m = re.search(r'### Overall Assessment\s*\n+(.+)', text)
    if not m:
        return "unknown"
    line = m.group(1).strip().lower()
    for verdict in ("fail", "needs-work", "pass"):
        if verdict in line:
            return verdict
    return "unknown"


def format_comment(severity: str, title: str, description: str) -> str:
    priority, color = SEVERITY_BADGE.get(severity, ("P2", "yellow"))
    badge = f"![{priority} Badge](https://img.shields.io/badge/{priority}-{color}?style=flat)"
    return f"**<sub><sub>{badge}</sub></sub>  {title}**\n\n{description}"


def build_review_body(commit_id: str) -> str:
    short_sha = commit_id[:10]
    return (
        f"### 💡 AI Code Review\n\n"
        f"Here are some automated review suggestions for this pull request.\n\n"
        f"**Reviewed commit:** `{short_sha}`\n\n"
        f"<details><summary>ℹ️ About this review</summary>\n"
        f"<br/>\n\n"
        f"This review was generated automatically by the AI Code Review workflow "
        f"using OpenCode CLI with the Minimax M2.5 Free model.\n\n"
        f"Reviews are triggered on every pull request push.\n\n"
        f"</details>\n"
        f"{MARKER}"
    )


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


def post_file_comment(pr_number: str, path: str, body: str, commit_id: str) -> None:
    """Post a file-level inline comment when a specific line isn't in the diff."""
    payload = json.dumps({
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "subject_type": "file",
    })
    run_gh(
        "api", f"repos/{REPO}/pulls/{pr_number}/comments",
        "-X", "POST",
        "--input", "-",
        stdin=payload,
    )


def react_to_pr(pr_number: str, reaction: str) -> None:
    run_gh(
        "api", f"repos/{REPO}/issues/{pr_number}/reactions",
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
    verdict = parse_verdict(review_text)

    line_comments: list[dict] = []
    file_comments: list[tuple[str, str]] = []

    for path, line, severity, title, description in findings:
        body = format_comment(severity, title, description)
        if path in diff_lines and line in diff_lines[path]:
            line_comments.append({"path": path, "line": line, "side": "RIGHT", "body": body})
        elif path in diff_lines:
            file_comments.append((path, body))
        else:
            print(f"Skipping {path}:{line} — file not in diff")

    review_body = build_review_body(commit_id)
    post_review(pr_number, review_body, line_comments, commit_id)
    print(f"Posted review: {len(line_comments)} inline comment(s)")

    for path, body in file_comments:
        post_file_comment(pr_number, path, body, commit_id)
        print(f"Posted file-level comment on {path}")

    if verdict == "pass":
        react_to_pr(pr_number, "+1")
        print("Added 👍 to PR (verdict: pass)")

    print(f"Done: {len(line_comments)} line comment(s), {len(file_comments)} file comment(s)")


if __name__ == "__main__":
    main()
