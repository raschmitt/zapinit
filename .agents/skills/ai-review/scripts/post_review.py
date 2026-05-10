#!/usr/bin/env python3
"""Post or update an inline AI code review on the PR via the Reviews API."""

import json
import os
import subprocess
import sys

REVIEW_TEXT_FILE = "/tmp/ai-review.md"
COMMENTS_FILE = "/tmp/ai-review-comments.json"
MARKER = "<!-- ai-review -->"

REPO = "raschmitt/zapinit"


def run_gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=True,
    )


def dismiss_old_review(pr_number: str) -> None:
    result = run_gh(
        "api",
        f"repos/{REPO}/pulls/{pr_number}/reviews",
        "--jq",
        ".",
    )
    reviews = json.loads(result.stdout) if result.stdout.strip() else []
    for review in reviews:
        if MARKER in review.get("body", ""):
            review_id = review["id"]
            run_gh(
                "api",
                f"repos/{REPO}/pulls/{pr_number}/reviews/{review_id}/dismissals",
                "-X",
                "PUT",
                "-f",
                "message=Superseded by updated review",
            )
            print(f"Dismissed old review (ID: {review_id})")
            return


def main() -> None:
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER env var not set", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(REVIEW_TEXT_FILE):
        print(f"Review text not found: {REVIEW_TEXT_FILE}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(COMMENTS_FILE):
        print(f"Comments file not found: {COMMENTS_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(REVIEW_TEXT_FILE) as f:
        body = f.read()
    with open(COMMENTS_FILE) as f:
        comments_data = json.load(f)

    dismiss_old_review(pr_number)

    review_payload = {
        "body": body,
        "event": "COMMENT",
        "comments": comments_data.get("comments", []),
    }

    payload_file = "/tmp/ai-review-payload.json"
    with open(payload_file, "w") as f:
        json.dump(review_payload, f)

    result = run_gh(
        "api",
        f"repos/{REPO}/pulls/{pr_number}/reviews",
        "-X",
        "POST",
        "--input",
        payload_file,
    )
    new_review = json.loads(result.stdout)
    print(f"Posted new review (ID: {new_review['id']})")


if __name__ == "__main__":
    main()
