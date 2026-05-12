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
    r"-\s+`([^:`]+):(\d+)(?:-\d+)?`\s*-\s*severity:\s*(high|medium|low)\s*-\s*([^:]+):\s*(.+)",
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
            m = re.search(r"\+(\d+)", raw)
            if m:
                current = int(m.group(1)) - 1
        elif raw.startswith("+") or raw.startswith(" "):
            current += 1
            lines.add(current)
    return lines


def parse_findings(text: str) -> list[tuple[str, int, str, str, str]]:
    """Return (path, line, severity, title, description) for each finding."""
    m = re.search(r"### Issues Found\n(.*?)(?=\n###|\Z)", text, re.DOTALL)
    if not m:
        return []
    findings = []
    for match in ISSUE_RE.finditer(m.group(1)):
        findings.append(
            (
                match.group(1),
                int(match.group(2)),
                match.group(3).lower(),
                match.group(4).strip(),
                match.group(5).strip(),
            )
        )
    return findings


def format_comment(severity: str, title: str, description: str) -> str:
    priority, color = SEVERITY_BADGE.get(severity, ("P2", "yellow"))
    badge = f"![{priority} Badge](https://img.shields.io/badge/{priority}-{color}?style=flat)"
    return f"**<sub><sub>{badge}</sub></sub>  {title}**\n\n{description}\n\n{MARKER}"


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


def find_summary_comment_id(pr_number: str) -> int | None:
    result = run_gh("api", f"repos/{REPO}/issues/{pr_number}/comments", "--jq", ".")
    comments = json.loads(result.stdout)
    for comment in comments:
        if MARKER in comment.get("body", ""):
            return comment["id"]
    return None


def post_or_update_summary(pr_number: str, body: str) -> None:
    existing_id = find_summary_comment_id(pr_number)
    if existing_id:
        run_gh(
            "api",
            f"repos/{REPO}/issues/comments/{existing_id}",
            "-X",
            "PATCH",
            "--input",
            "-",
            stdin=json.dumps({"body": body}),
        )
        print("Updated existing summary comment")
    else:
        run_gh(
            "api",
            f"repos/{REPO}/issues/{pr_number}/comments",
            "-X",
            "POST",
            "--input",
            "-",
            stdin=json.dumps({"body": body}),
        )
        print("Created new summary comment")


def post_review(pr_number: str, comments: list[dict], commit_id: str) -> None:
    if not comments:
        return
    payload = json.dumps(
        {
            "commit_id": commit_id,
            "body": MARKER,
            "event": "COMMENT",
            "comments": comments,
        }
    )
    run_gh(
        "api",
        f"repos/{REPO}/pulls/{pr_number}/reviews",
        "-X",
        "POST",
        "--input",
        "-",
        stdin=payload,
    )


def post_file_comment(pr_number: str, path: str, body: str, commit_id: str) -> None:
    """Post a file-level inline comment when a specific line isn't in the diff."""
    payload = json.dumps(
        {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "subject_type": "file",
        }
    )
    run_gh(
        "api",
        f"repos/{REPO}/pulls/{pr_number}/comments",
        "-X",
        "POST",
        "--input",
        "-",
        stdin=payload,
    )


def get_unresolved_positions(pr_number: str) -> tuple[set[tuple[str, int]], set[str]]:
    """
    Query GitHub for open (unresolved) review threads that contain our MARKER.
    Returns:
        line_positions: {(path, line)} for line-specific unresolved comments
        file_positions: {path} for file-level unresolved comments
    """
    owner, repo_name = REPO.split("/")
    query = (
        f'{{ repository(owner: "{owner}", name: "{repo_name}") {{'
        f" pullRequest(number: {pr_number}) {{"
        f" reviewThreads(first: 100) {{ nodes {{ isResolved"
        f" comments(first: 2) {{ nodes {{ body path line }} totalCount }}"
        f" }} }} }} }} }}"
    )
    try:
        result = run_gh("api", "graphql", "-f", f"query={query}")
    except subprocess.CalledProcessError:
        print("Warning: could not fetch review threads; skipping dedup check")
        return set(), set()

    data = json.loads(result.stdout)
    threads = (
        data.get("data", {})
        .get("repository", {})
        .get("pullRequest", {})
        .get("reviewThreads", {})
        .get("nodes", [])
    )

    line_positions: set[tuple[str, int]] = set()
    file_positions: set[str] = set()
    for thread in threads:
        if thread.get("isResolved"):
            continue
        comments_node = thread.get("comments", {})
        total_count = comments_node.get("totalCount", 1)
        if total_count > 1:
            continue
        nodes = comments_node.get("nodes", [])
        if not nodes:
            continue
        comment = nodes[0]
        path = comment.get("path")
        line = comment.get("line")
        if not path:
            continue
        if line is not None:
            try:
                line_positions.add((path, int(line)))
            except (ValueError, TypeError):
                file_positions.add(path)
        else:
            file_positions.add(path)

    return line_positions, file_positions


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
    unresolved_lines, unresolved_files = get_unresolved_positions(pr_number)

    line_comments: list[dict] = []
    file_comments: list[tuple[str, str]] = []

    for path, line, severity, title, description in findings:
        if (path, line) in unresolved_lines:
            print(f"Skipping {path}:{line} — already has an open comment")
            continue
        body = format_comment(severity, title, description)
        if path in diff_lines and line in diff_lines[path]:
            line_comments.append(
                {"path": path, "line": line, "side": "RIGHT", "body": body}
            )
        elif path in diff_lines:
            if path in unresolved_files:
                print(f"Skipping {path} (file-level) — already has an open comment")
                continue
            file_comments.append((path, body))
        else:
            print(f"Skipping {path}:{line} — file not in diff")

    review_body = build_review_body(commit_id)
    post_or_update_summary(pr_number, review_body)
    post_review(pr_number, line_comments, commit_id)
    print(f"Posted review: {len(line_comments)} inline comment(s)")

    for path, body in file_comments:
        post_file_comment(pr_number, path, body, commit_id)
        print(f"Posted file-level comment on {path}")

    print(
        f"Done: {len(line_comments)} line comment(s), {len(file_comments)} file comment(s)"
    )


if __name__ == "__main__":
    main()
