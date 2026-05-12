---
name: ai-fix
description: Processes unresolved PR review threads — fixes valid issues and replies to invalid ones. Triggers when asked to fix review comments or address PR feedback. Can be run locally or called by the AI Fix Loop workflow.
---

Process all unresolved review threads on the current PR and either fix the code or reply with reasoning.

## Prerequisites

- `PR_NUMBER` environment variable must be set to the PR number.
- `GH_TOKEN` must be set with a token that has `pull-requests: write` and `contents: write` scope.

## Process

### 1. Load protected files

Read `.ai-fix-ignore` and collect all glob patterns. Files matching any pattern must never be modified.

```bash
cat .ai-fix-ignore
```

### 2. Check iteration limit

```bash
gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments --jq '.'
```

Look for a comment containing `<!-- ai-fix -->`. Extract the iteration number from it (e.g. `iteration=3`). If the number is **≥ 5**, stop immediately — do nothing further. If no such comment exists, this is iteration 1.

### 3. Fetch the diff

```bash
git fetch origin main
git diff origin/main...HEAD
```

### 4. Fetch unresolved review threads

```bash
gh api graphql -f query='
  {
    repository(owner: "raschmitt", name: "zapinit") {
      pullRequest(number: $PR_NUMBER) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            comments(first: 2) {
              totalCount
              nodes { body path line }
            }
          }
        }
      }
    }
  }'
```

Only process threads where `isResolved: false` AND `totalCount == 1` (no replies yet — already-replied threads are skipped to avoid loops).

### 5. For each unresolved thread

**If the thread's `path` matches a pattern in `.ai-fix-ignore`:**

Reply explaining the file is protected from automated fixes and must be addressed manually. Do NOT resolve the thread.

```bash
gh api graphql -f query='mutation {
  addPullRequestReviewThreadReply(input: {
    pullRequestReviewThreadId: "<ID>",
    body: "This file is listed in `.ai-fix-ignore` and cannot be modified automatically. Please apply the fix manually."
  }) { comment { id } }
}'
```

**If the issue is valid and the file is not protected:**

Fix the code, then resolve the thread.

```bash
gh api graphql -f query='mutation {
  resolveReviewThread(input: { threadId: "<ID>" }) {
    thread { isResolved }
  }
}'
```

**If the issue is not valid:**

Reply with a brief explanation. Do NOT resolve the thread.

```bash
gh api graphql -f query='mutation {
  addPullRequestReviewThreadReply(input: {
    pullRequestReviewThreadId: "<ID>",
    body: "<explanation>"
  }) { comment { id } }
}'
```

### 6. Commit and push (only if code changed)

If no files were changed, stop here. Do NOT push.

If files were changed:

```bash
git add -A
git commit -m "fix: apply review fixes" -m "Co-authored-by: claude <claude@anthropic.com>"
git push origin HEAD:refs/heads/<PR_HEAD_REF>
```

The PR head ref can be retrieved with:

```bash
gh api repos/raschmitt/zapinit/pulls/$PR_NUMBER --jq '.head.ref'
```

### 7. Update the iteration counter

Find the existing `<!-- ai-fix -->` comment and PATCH it; if none exists, POST a new one.

```bash
# Find existing comment ID
COMMENT_ID=$(gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments \
  --jq '.[] | select(.body | contains("<!-- ai-fix -->")) | .id')

# PATCH if found
gh api repos/raschmitt/zapinit/issues/comments/$COMMENT_ID \
  -X PATCH -f body="<!-- ai-fix --> iteration=N"

# POST if not found
gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments \
  -X POST -f body="<!-- ai-fix --> iteration=1"
```

## Rules

- **Never submit a new PR review.** Only reply to or resolve existing threads.
- **Never post new issue comments** other than the `<!-- ai-fix -->` iteration counter.
- **Never modify files matching patterns in `.ai-fix-ignore`** — reply to those threads instead.
- Replies to invalid or protected threads do NOT count as code changes — do not push for those alone.
