#!/usr/bin/env python3
"""Post or update the AI review comment on the PR."""

import json
import os
import subprocess
import sys

REVIEW_FILE = "/tmp/ai-review.md"
MARKER = "<!-- ai-review -->"


def run_gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=True,
    )


def main() -> None:
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER env var not set", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(REVIEW_FILE):
        print(f"Review file not found: {REVIEW_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(REVIEW_FILE) as f:
        review_body = f.read()

    if MARKER not in review_body:
        print(
            f"Warning: review file does not contain marker {MARKER!r}. "
            "Comment update will not work on re-push.",
            file=sys.stderr,
        )

    # List existing PR comments and find one with the marker
    result = run_gh(
        "api",
        f"repos/raschmitt/zapinit/issues/{pr_number}/comments",
        "--jq",
        ".[]",
    )
    comments = json.loads(result.stdout) if result.stdout.strip() else []

    existing_id: int | None = None
    for comment in comments:
        if MARKER in comment.get("body", ""):
            existing_id = comment["id"]
            break

    if existing_id is not None:
        run_gh(
            "api",
            f"repos/raschmitt/zapinit/issues/comments/{existing_id}",
            "-X",
            "PATCH",
            "-f",
            f"body={review_body}",
        )
        print(f"Updated review comment (ID: {existing_id})")
    else:
        run_gh("pr", "comment", pr_number, "--body-file", REVIEW_FILE)
        print("Posted new review comment")


if __name__ == "__main__":
    main()
