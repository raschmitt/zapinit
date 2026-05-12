#!/usr/bin/env python3
"""Manage the thumbs-up reaction based on open AI review comments.

Adds 👍 when there are no open AI review threads; removes it when there are.
"""

import json
import os
import subprocess
import sys

REPO = "raschmitt/zapinit"


def run_gh(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=True,
    )


def has_open_unresolved_threads(pr_number: str) -> bool:
    owner, repo_name = REPO.split("/")
    query = (
        f'{{ repository(owner: "{owner}", name: "{repo_name}") {{'
        f" pullRequest(number: {pr_number}) {{"
        f" reviewThreads(first: 100) {{ nodes {{ isResolved"
        f" comments(first: 2) {{ nodes {{ body }} totalCount }}"
        f" }} }} }} }} }}"
    )
    try:
        result = run_gh("api", "graphql", "-f", f"query={query}")
    except subprocess.CalledProcessError:
        print("Warning: could not fetch review threads; assuming no open comments")
        return False

    data = json.loads(result.stdout)
    threads = (
        data.get("data", {})
        .get("repository", {})
        .get("pullRequest", {})
        .get("reviewThreads", {})
        .get("nodes", [])
    )

    for thread in threads:
        if thread.get("isResolved"):
            continue
        comments_node = thread.get("comments", {})
        total_count = comments_node.get("totalCount", 1)
        if total_count > 1:
            continue
        nodes = comments_node.get("nodes", [])
        if nodes:
            return True
    return False


def get_thumbsup_reaction_id(pr_number: str) -> str | None:
    result = run_gh(
        "api",
        f"repos/{REPO}/issues/{pr_number}/reactions",
        "--jq",
        '.[] | select(.content == "+1" and .user.login == "github-actions[bot]") | .id',
    )
    val = result.stdout.strip()
    return val if val else None


def main() -> None:
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER env var not set", file=sys.stderr)
        sys.exit(1)

    open_comments = has_open_unresolved_threads(pr_number)
    existing_id = get_thumbsup_reaction_id(pr_number)

    if open_comments:
        print("Open AI review comments found")
        if existing_id:
            run_gh(
                "api",
                f"repos/{REPO}/issues/{pr_number}/reactions/{existing_id}",
                "-X",
                "DELETE",
            )
            print("Removed 👍 reaction")
        else:
            print("No 👍 reaction to remove")
    else:
        print("No open AI review comments")
        if existing_id:
            print("👍 already present, skipping")
        else:
            run_gh(
                "api",
                f"repos/{REPO}/issues/{pr_number}/reactions",
                "-X",
                "POST",
                "--input",
                "-",
                stdin=json.dumps({"content": "+1"}),
            )
            print("Added 👍 reaction")


if __name__ == "__main__":
    main()
