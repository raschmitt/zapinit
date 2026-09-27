---
name: pr-review
description: Reviews PR code diffs for bugs, security issues, and quality problems. Triggers when asked to review or audit a pull request diff.
---

Review the PR diff and post a structured review with inline comments, summary comment, and reaction management.

**Important:** The model handles ALL GitHub interactions (posting, reactions, dedup) via `gh api` — no external scripts.

## Process

1.  **Add 👀 reaction** to signal that review is in progress:

    ```bash
    gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/reactions -X POST --field content=eyes
    ```

2.  **Get the diff** of the PR:

    ```bash
    git diff origin/main...HEAD
    ```

3.  **Read the task specification and design references**:

    ```bash
    grep -A 50 "### T-26" docs/tasks.md | head -60
    ```

    Then read the referenced `.md` files for context:
    - `docs/tasks.md` — find the current task section and verify what it demands
    - `docs/architecture.md` — check architectural decisions and tech stack
    - `DESIGN.md` — check visual and UX design conventions

4.  **Dedup check — query existing unresolved review threads**. This prevents raising the same finding twice. Query for open (unresolved) threads that contain the `<!-- ai-review -->` marker:

    ```bash
    gh api graphql -f query='
    {
      repository(owner: "raschmitt", name: "zapinit") {
        pullRequest(number: '$PR_NUMBER') {
          reviewThreads(first: 100) {
            nodes {
              isResolved
              comments(first: 2) {
                nodes { body path line }
                totalCount
              }
            }
          }
        }
      }
    }' --jq '.data.repository.pullRequest.reviewThreads.nodes[] |
         select(.isResolved == false) |
         select(.comments.nodes[0].body | test("<!-- ai-review -->")) |
         {path: .comments.nodes[0].path, line: .comments.nodes[0].line}'
    ```

    Store the resulting `(path, line)` pairs. Also check for **unresolved PR issue comments** (summary comments) containing the marker:

    ```bash
    gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments \
      --jq '[.[] | select(.body | contains("<!-- ai-review -->")) | {id, body: (.body | split("\n")[0:2] | join(" "))}]'
    ```

    In your review, omit any finding whose `path` and `line` already appear in the unresolved threads. If the issue was previously flagged but the thread is now resolved, you may raise it again if it still exists in the code.

    **Skip threads with replies** (`totalCount > 1`) — those are already being discussed and should not be re-raised.

5.  **Read the full content** of each changed file to understand context.

6.  **Analyze** the changes for:
    - **Task compliance** — does the PR deliver what `docs/tasks.md` asks for? Are all subtasks implemented?
    - **Architectural fit** — does the implementation follow `docs/architecture.md`? (tech stack, vendor choices, design decisions)
    - **Design consistency** — if `DESIGN.md` exists and the PR touches UI, does it follow the documented design?
    - Logic errors and potential bugs
    - Security vulnerabilities
    - Code quality and maintainability issues
    - Missing error handling
    - Deviation from project conventions (see `AGENTS.md` — code standards, commit conventions, testing requirements)
    - Missing or inadequate tests (check the `tests/` directory)
    - Edge cases not handled

7.  **Build the review output**:

    Format each finding as a line-specific inline comment body:

    ```
    **<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>  <title>**

    <description>

    <!-- ai-review -->
    ```

    Severity mapping:
    | Severity | Badge |
    |---|---|
    | high | `P1` orange |
    | medium | `P2` yellow |
    | low | `P2` yellow |

    Build the summary comment body:

    ```markdown
    ### 💡 AI Code Review

    Here are some automated review suggestions for this pull request.

    **Reviewed commit:** `<first 10 chars of HEAD SHA>`

    <details><summary>ℹ️ About this review</summary>
    <br/>

    This review was generated automatically by the AI Code Review workflow
    using OpenCode CLI with the Minimax M2.5 Free model.

    </details>
    <!-- ai-review -->
    ```

8.  **Post the PR review with inline comments** via the GitHub API. This creates resolvable inline comments on the PR:

    ```bash
    gh api repos/raschmitt/zapinit/pulls/$PR_NUMBER/reviews -X POST \
      --input - <<'EOF'
    {
      "commit_id": "<HEAD_SHA>",
      "body": "<!-- ai-review -->",
      "event": "COMMENT",
      "comments": [
        {
          "path": "<file_path>",
          "line": <line_number>,
          "side": "RIGHT",
          "body": "<formatted comment body>"
        }
      ]
    }
    EOF
    ```

    Build the JSON payload with all inline findings in a single review. For findings whose line number is not in the diff, post a **file-level** comment instead:

    ```bash
    gh api repos/raschmitt/zapinit/pulls/$PR_NUMBER/comments -X POST \
      --input - <<'EOF'
    {
      "body": "<formatted comment body>",
      "commit_id": "<HEAD_SHA>",
      "path": "<file_path>",
      "subject_type": "file"
    }
    EOF
    ```

9.  **Post or update the summary comment** on the PR (issue comment, not review). Check if one already exists with `<!-- ai-review -->` and update it via PATCH, otherwise create via POST:

    ```bash
    # Find existing summary comment ID:
    EXISTING_ID=$(gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments \
      --jq '.[] | select(.body | contains("<!-- ai-review -->")) | .id' | head -1)

    if [ -n "$EXISTING_ID" ]; then
      gh api repos/raschmitt/zapinit/issues/comments/$EXISTING_ID -X PATCH \
        --input - <<'EOF'
    {"body": "<summary body>"}
    EOF
    else
      gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments -X POST \
        --input - <<'EOF'
    {"body": "<summary body>"}
    EOF
    fi
    ```

10. **Remove 👀 reaction** (review is done). Find the reaction ID first:

    ```bash
    EYES_ID=$(gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/reactions \
      --jq '.[] | select(.content == "eyes" and .user.login == "github-actions[bot]") | .id')
    if [ -n "$EYES_ID" ]; then
      gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/reactions/$EYES_ID -X DELETE
    fi
    ```

11. **Manage 👍 reaction** — add when no open AI review threads remain, remove when there are open threads:

    ```bash
    # Count open unresolved threads with our marker and no replies
    OPEN_COUNT=$(gh api graphql -f query='
    {
      repository(owner: "raschmitt", name: "zapinit") {
        pullRequest(number: '$PR_NUMBER') {
          reviewThreads(first: 100) {
            nodes {
              isResolved
              comments(first: 2) {
                nodes { body }
                totalCount
              }
            }
          }
        }
      }
    }' --jq '[.data.repository.pullRequest.reviewThreads.nodes[] |
         select(.isResolved == false) |
         select(.comments.nodes[0].body // "" | test("<!-- ai-review -->")) |
         select(.comments.totalCount == 1)] | length')

    # Find existing thumbs-up reaction
    THUMBS_ID=$(gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/reactions \
      --jq '.[] | select(.content == "+1" and .user.login == "github-actions[bot]") | .id')

    if [ "$OPEN_COUNT" -gt 0 ]; then
      # Open comments exist — remove thumbs-up if present
      if [ -n "$THUMBS_ID" ]; then
        gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/reactions/$THUMBS_ID -X DELETE
      fi
    else
      # No open comments — add thumbs-up if not already present
      if [ -z "$THUMBS_ID" ]; then
        gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/reactions -X POST --field content='+1'
      fi
    fi
    ```

## Rules

- Be constructive and specific — reference exact file paths and line numbers
- Focus on the diff only — do not review unchanged code
- Flag missing tests as a high-severity issue for new features or behaviour changes
- Do not modify any files — this is a review-only task
- **Avoid repeating findings** that already have open unresolved threads on the same `(path, line)` — unless the issue is still present and unaddressed, in which case note it as persisting rather than raising it as new
- **Never flag task-compliance or test-coverage issues on docs PRs.** A PR is a docs PR if all changed files are under `docs/` and the commit type is `docs:`. Such PRs have no implementation obligation — adding or updating task definitions is their entire purpose. If the PR touches files outside `docs/` or uses a non-`docs` commit type, apply the full review
- **Handle all `gh api` error responses gracefully** — if a command fails, log the error and continue rather than aborting the entire review
