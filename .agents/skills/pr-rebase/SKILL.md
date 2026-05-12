---
name: pr-rebase
description: Rebases a PR branch onto the latest main, resolving conflicts intelligently using an AI agent. Triggers when asked to rebase a pull request.
---

Rebase a PR branch onto the latest `main`, resolve conflicts intelligently, and force-push.

## Prerequisites

- `PR_NUMBER` environment variable must be set to the PR number.
- `GH_TOKEN` must be set with a token that has `pull-requests: write` and `contents: write` scope.

## Process

### 1. Fetch PR branch details

Get the PR head ref:

```bash
HEAD_REF=$(gh api repos/raschmitt/zapinit/pulls/$PR_NUMBER --jq '.head.ref')
```

### 2. Fetch and checkout the PR branch

```bash
git fetch origin "$HEAD_REF"
git checkout "$HEAD_REF"
```

### 3. Fetch the latest main

```bash
git fetch origin main
```

### 4. Attempt rebase

```bash
git rebase origin/main
```

### 5. If rebase succeeds (no conflicts)

Push directly — no AI conflict resolution needed:

```bash
git push origin HEAD:refs/heads/"$HEAD_REF"
```

Stop here. Do not proceed further.

### 6. If rebase fails (conflicts exist)

#### 6a. Load protected file patterns

```bash
cat .agents/skills/pr-fix/assets/ai-fix-ignore
```

#### 6b. Identify conflicting files

```bash
CONFLICT_FILES=$(git diff --name-only --diff-filter=U)
echo "$CONFLICT_FILES"
```

#### 6c. Resolve each conflicting file

For each file in `$CONFLICT_FILES`:

- **If the file matches a pattern in `ai-fix-ignore`** (e.g. `.github/workflows/**`):
  These are config/workflow files — use the `main` version (rebase "ours" strategy):

  ```bash
  git checkout --ours -- "<file>"
  git add "<file>"
  ```

- **Otherwise (feature code):**
  Read the current conflicted state to understand both sides:

  ```bash
  cat "<file>"
  ```

  Understand the intent of both sides (the PR branch change and the main branch change). Resolve the conflict by preserving the intent of both sides. Favour the PR branch intent for feature code. Remove all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).

  Stage the resolved file:

  ```bash
  git add "<file>"
  ```

### 7. Continue rebase

```bash
git rebase --continue
```

If `git rebase --continue` fails with new conflicts, repeat from step 6b.

### 8. Force-push with lease

```bash
if ! git push --force-with-lease origin HEAD:refs/heads/"$HEAD_REF"; then
  gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments \
    --field body="The automated rebase succeeded, but the force-push failed. This may be due to network issues or permission errors. Please push manually:

\`\`\`
git push --force-with-lease origin HEAD:refs/heads/$HEAD_REF
\`\`\`"
  exit 1
fi
```

### 9. If rebase still fails after AI resolution attempt

Post a comment on the PR listing the files that could not be resolved:

```bash
gh api repos/raschmitt/zapinit/issues/$PR_NUMBER/comments \
  --field body="The automated rebase could not resolve conflicts in these files:

$(echo "$CONFLICT_FILES" | sed 's/^/- /')

These files require manual resolution. Please rebase locally and resolve the remaining conflicts."
  exit 1
```

## Rules

- **Never create a new branch** — only operate on the existing PR branch
- **Never change the PR target** — always rebase onto `origin/main`
- **Always use `--force-with-lease`** — never a bare `--force`
- **Protected files** (matching `ai-fix-ignore` patterns) must always use the `main` version during conflict resolution
- **Do not modify any files outside the rebase conflict resolution** — this is a rebase-only task
