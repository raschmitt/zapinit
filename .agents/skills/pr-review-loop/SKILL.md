---
name: pr-review-loop
description: Decision framework for processing PR review comments one by one. Based on real iterative PR review experience. Use when you need to analyse review feedback, decide what to fix vs what to reply to, and commit fixes.
---

## Decision framework

For each unresolved review thread, follow this process:

### 1. Understand the thread

- Read the file path and line number
- Read the surrounding code context
- Read the reviewer's concern

### 2. Categorise

**Valid issues** (fix these):
- Logic errors or bugs
- Missing edge-case handling
- Deviations from project conventions
- Missing tests for new behaviour
- Security vulnerabilities
- Incorrect type annotations

**Invalid / by-design** (reply explaining why, leave unresolved):
- The code is intentionally written this way (e.g. IIFE runs before DOMContentLoaded for FOUC prevention)
- The concern is already handled elsewhere (e.g. null check on a different line)
- False alarm — the test assertion is correct but the reviewer misread it
- Pre-existing code not introduced by this PR — out of scope
- The reviewer suggested a pattern that doesn't apply here (e.g. server-side check for client-only code)
- Cosmetic/style preferences that violate the principle of minimal diffs

### 3. For valid issues

- Apply the smallest possible fix — resist the urge to refactor surrounding code
- Verify the fix locally with `pytest` and `ruff check .`
- Track the thread in the output as fixed

### 4. For invalid issues

- Draft a concise, technically precise reply explaining why the comment does not apply
- Reference specific lines or behaviours (e.g. "the null check is on line 87")
- Leave the thread **unresolved** — the AI Code Review will skip it on re-review because it has a reply
- Track the thread in the output as replied

### 5. Commit discipline

- One thread per commit — separate `git commit` for each fix
- Use conventional commit messages: `fix: <description>` or `chore: <description>`
- If no code changes were made (all replies), do not commit or push
