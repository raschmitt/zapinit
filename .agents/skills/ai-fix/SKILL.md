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

Read `.agents/skills/ai-fix/assets/ai-fix-ignore` and collect all glob patterns. Files matching any pattern must never be modified.

```bash
cat .agents/skills/ai-fix/assets/ai-fix-ignore
```

### 2. Fetch the diff

```bash
git fetch origin main
git diff origin/main...HEAD
```

### 3. Fetch unresolved review threads

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

### 4. For each unresolved thread

**If the thread's `path` matches a pattern in `.agents/skills/ai-fix/assets/ai-fix-ignore`:**

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

### 5. Commit and push (only if code changed)

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

## Rules

- **Never submit a new PR review.** Only reply to or resolve existing threads.
- **Never post new issue comments.**
- **Never modify files matching patterns in `.agents/skills/ai-fix/assets/ai-fix-ignore`** — reply to those threads instead.
- Replies to invalid or protected threads do NOT count as code changes — do not push for those alone.
