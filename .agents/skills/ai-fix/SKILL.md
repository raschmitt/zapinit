---
name: ai-fix
description: Applies fixes for AI review comments on a PR. Invoked by the AI Fix Loop workflow when the AI Code Review workflow completes or CI fails.
---

Apply fixes for AI review comments on the current PR.

## Process

1. Read the input context from `/tmp/ai-fix-input.json`.

2. Fetch the full diff:
   ```bash
   git diff origin/main...HEAD
   ```

3. For each thread in `unresolved_threads`:
   - Read the surrounding code to understand context
   - Decide: is this a real bug/issue or is it invalid/by-design?
   - For **valid** issues: apply the minimal fix
   - For **invalid** issues: prepare a reply explaining why (leave unresolved — the dedup will skip it)

4. Write the output to `/tmp/ai-fix-output.json`:
   ```json
   {
     "fixed_threads": [{"path": "...", "line": 42}],
     "replied_threads": [{"path": "...", "line": 10, "reply": "..."}],
     "committed": false
   }
   ```

5. After writing the output, commit and push:
   - Stage only changed files
   - Commit with a conventional commit message
   - Push to the PR branch

## Rules

- One fix per thread — do not batch unrelated changes
- Follow the decision framework in `@.agents/skills/pr-review-loop/SKILL.md`
- If no threads can be fixed (all invalid), set `committed: false` and do not push
- If iteration ≥ max_iterations, set `committed: false` and do not push — human help needed
- Do not modify files outside the scope of the review comments
