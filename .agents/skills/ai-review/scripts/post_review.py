#!/usr/bin/env python3
"""Post or update an AI code review as an issue comment on the PR."""

import json
import os
import subprocess
import sys

REVIEW_TEXT_FILE = "/tmp/ai-review.md"
MARKER = "<!-- ai-review -->"

REPO = "raschmitt/zapinit"


def run_gh(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=True,
    )


def find_existing_comment(pr_number: str) -> dict | None:
    result = run_gh(
        "api",
        f"repos/{REPO}/issues/{pr_number}/comments",
        "--jq",
        ".",
    )
    comments = json.loads(result.stdout) if result.stdout.strip() else []
    for comment in comments:
        if MARKER in comment.get("body", ""):
            return comment
    return None


def post_or_update_comment(pr_number: str, body: str) -> None:
    payload = json.dumps({"body": body})
    existing = find_existing_comment(pr_number)
    if existing:
        comment_id = existing["id"]
        run_gh(
            "api",
            f"repos/{REPO}/issues/comments/{comment_id}",
            "-X", "PATCH",
            "--input", "-",
            stdin=payload,
        )
        print(f"Updated existing comment (ID: {comment_id})")
    else:
        run_gh(
            "api",
            f"repos/{REPO}/issues/{pr_number}/comments",
            "-X", "POST",
            "--input", "-",
            stdin=payload,
        )
        print("Posted new comment")


def main() -> None:
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER env var not set", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(REVIEW_TEXT_FILE):
        print(f"Review text not found: {REVIEW_TEXT_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(REVIEW_TEXT_FILE) as f:
        body = f.read()

    post_or_update_comment(pr_number, body)


if __name__ == "__main__":
    main()
