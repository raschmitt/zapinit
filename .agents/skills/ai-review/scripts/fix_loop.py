#!/usr/bin/env python3
"""Orchestrator for the AI fix loop.

Fetches unresolved AI review threads (filtering out those with replies),
fetches CI failure logs, and writes a structured input file for the model.
After the model runs, reads the output and posts iteration tracking.
"""

import json
import os
import re
import subprocess
import sys

MARKER = "<!-- ai-review -->"
FIX_MARKER = "<!-- ai-fix -->"
REPO = "raschmitt/zapinit"
INPUT_FILE = "/tmp/ai-fix-input.json"
OUTPUT_FILE = "/tmp/ai-fix-output.json"
MAX_ITERATIONS = 5


def run_gh(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=True,
    )


def get_unresolved_threads(pr_number: str) -> list[dict]:
    """Fetch unresolved AI review threads that have no replies yet."""
    owner, repo_name = REPO.split("/")
    query = (
        f'{{ repository(owner: "{owner}", name: "{repo_name}") {{'
        f" pullRequest(number: {pr_number}) {{"
        f"  reviewThreads(first: 100) {{ nodes {{"
        f"    id isResolved"
        f"    comments(first: 2) {{ nodes {{ body path line databaseId }} totalCount }}"
        f"  }} }} }} }} }}"
    )
    try:
        result = run_gh("api", "graphql", "-f", f"query={query}")
    except subprocess.CalledProcessError as e:
        print(f"Error fetching review threads: {e}", file=sys.stderr)
        return []

    data = json.loads(result.stdout)
    threads = (
        data.get("data", {})
        .get("repository", {})
        .get("pullRequest", {})
        .get("reviewThreads", {})
        .get("nodes", [])
    )

    unresolved: list[dict] = []
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
        if MARKER not in comment.get("body", ""):
            continue
        unresolved.append(
            {
                "thread_id": thread["id"],
                "path": comment.get("path", ""),
                "line": comment.get("line"),
                "body": comment.get("body", ""),
                "comment_id": comment.get("databaseId"),
            }
        )
    return unresolved


def resolve_thread(thread_id: str) -> None:
    """Resolve a review thread via GraphQL."""
    mutation = (
        'mutation { resolveReviewThread(input: { threadId: "' + thread_id + '" }) {'
        " thread { isResolved } } }"
    )
    try:
        run_gh("api", "graphql", "-f", f"query={mutation}")
    except subprocess.CalledProcessError as e:
        print(f"Error resolving thread {thread_id}: {e}", file=sys.stderr)


def reply_to_thread(thread_id: str, body: str) -> None:
    """Reply to a review thread via GraphQL."""
    mutation = (
        "mutation { addPullRequestReviewThreadReply(input: {"
        ' pullRequestReviewThreadId: "'
        + thread_id
        + '", body: "'
        + escape_graphql(body)
        + '"'
        " }) { comment { id } } }"
    )
    try:
        run_gh("api", "graphql", "-f", f"query={mutation}")
    except subprocess.CalledProcessError as e:
        print(f"Error replying to thread {thread_id}: {e}", file=sys.stderr)


def escape_graphql(s: str) -> str:
    """Escape a string for GraphQL input (minimal escaping)."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def fetch_diff(pr_number: str) -> str:
    """Fetch the full diff for the PR."""
    try:
        result = run_gh(
            "api",
            f"repos/{REPO}/pulls/{pr_number}",
            "--jq",
            ".diff_url",
        )
        diff_url = result.stdout.strip()
        result = run_gh("api", diff_url, "--jq", ".")
        # gh api with a URL returns the body directly
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def get_iteration_count(pr_number: str) -> int:
    """Read the iteration counter from a bot comment on the PR."""
    try:
        result = run_gh(
            "api",
            f"repos/{REPO}/issues/{pr_number}/comments",
            "--jq",
            ".",
        )
        comments = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return 0

    for comment in reversed(comments):
        body = comment.get("body", "")
        if FIX_MARKER in body:
            m = re.search(r"Iteration\s+(\d+)", body)
            if m:
                return int(m.group(1))
    return 0


def update_iteration_counter(pr_number: str, iteration: int) -> None:
    """Post or update the iteration counter comment."""
    body = f"🤖 AI Fix Loop — Iteration {iteration}/{MAX_ITERATIONS}\n\n{FIX_MARKER}"

    try:
        result = run_gh(
            "api",
            f"repos/{REPO}/issues/{pr_number}/comments",
            "--jq",
            ".",
        )
        comments = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        comments = []

    existing_id = None
    for comment in comments:
        if FIX_MARKER in comment.get("body", ""):
            existing_id = comment["id"]
            break

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


def main() -> None:
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER env var not set", file=sys.stderr)
        sys.exit(1)

    iteration = get_iteration_count(pr_number)
    if iteration >= MAX_ITERATIONS:
        print(f"Max iterations ({MAX_ITERATIONS}) reached — posting human-help comment")
        run_gh(
            "api",
            f"repos/{REPO}/issues/{pr_number}/comments",
            "-X",
            "POST",
            "--input",
            "-",
            stdin=json.dumps(
                {
                    "body": (
                        "⚠️ AI Fix Loop reached the maximum of "
                        f"{MAX_ITERATIONS} iterations without full resolution.\n\n"
                        "A human reviewer needs to take over this PR."
                    )
                }
            ),
        )
        sys.exit(0)

    threads = get_unresolved_threads(pr_number)
    if not threads:
        print("No unresolved AI review threads without replies — nothing to do")
        sys.exit(0)

    diff = fetch_diff(pr_number)

    input_data = {
        "pr_number": pr_number,
        "unresolved_threads": threads,
        "diff_excerpt": diff[:50000] if diff else "",
        "iteration": iteration + 1,
        "max_iterations": MAX_ITERATIONS,
    }

    with open(INPUT_FILE, "w") as f:
        json.dump(input_data, f, indent=2)
    print(f"Wrote input to {INPUT_FILE} ({len(threads)} threads)")

    update_iteration_counter(pr_number, iteration + 1)
    print(f"Updated iteration counter to {iteration + 1}")

    print("Waiting for the model to process...")

    # Wait for the model to write the output file
    # The workflow will call opencode, which writes /tmp/ai-fix-output.json
    # We check in a loop (up to 10 minutes) for the file to appear


if __name__ == "__main__":
    main()
