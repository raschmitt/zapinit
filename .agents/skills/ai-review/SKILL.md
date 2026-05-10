---
name: ai-review
description: Reviews PR code diffs for bugs, security issues, and quality problems. Triggers when asked to review or audit a pull request diff.
---

Review the PR diff and post a structured review comment.

## Process

1.  Get the diff of the PR:

    ```bash
    git diff origin/main...HEAD
    ```

2.  Read the task specification and design references:

    ```bash
    grep -A 50 "### T-26" docs/tasks.md | head -60
    ```

    Then read the referenced `.md` files for context:
    - `docs/tasks.md` — find the current task section and verify what it demands
    - `docs/architecture.md` — check architectural decisions and tech stack
    - `docs/DESIGN.md` — if it exists, check visual and UX design conventions

3.  Read the full content of each changed file to understand context.

4.  Analyze the changes for:
    - **Task compliance** — does the PR deliver what `docs/tasks.md` asks for? Are all subtasks implemented?
    - **Architectural fit** — does the implementation follow `docs/architecture.md`? (tech stack, vendor choices, design decisions)
    - **Design consistency** — if `docs/DESIGN.md` exists and the PR touches UI, does it follow the documented design?
    - Logic errors and potential bugs
    - Security vulnerabilities
    - Code quality and maintainability issues
    - Missing error handling
    - Deviation from project conventions (see `AGENTS.md` — code standards, commit conventions, testing requirements)
    - Missing or inadequate tests (check the `tests/` directory)
    - Edge cases not handled

5.  Save the review summary to `/tmp/ai-review.md` in this format:

    ```markdown
    ## AI Code Review

    ### Summary
    <brief overview of the changes>

    ### Issues Found
    <file:line> - <description> - <severity: high/medium/low>

    ### Suggestions
    <actionable recommendations>

    ### Overall Assessment
    <concise verdict — pass / needs-work / fail>

    <!-- ai-review -->
    ```

6.  Save inline review comments to `/tmp/ai-review-comments.json`. Each comment
    must target a specific line in the diff (use `git diff origin/main...HEAD`
    to verify line numbers). The `side` field is always `"RIGHT"` (the new
    version of the file):

    ```json
    {
      "comments": [
        {
          "path": "relative/file/path.py",
          "line": 42,
          "side": "RIGHT",
          "body": "Specific, actionable feedback about this line."
        }
      ]
    }
    ```

    Rules for inline comments:
    - Only include comments for lines that actually changed in the diff
    - Use the line number from the new (right) version of the file
    - Keep each comment focused on a single issue
    - If no issues found on specific lines, use an empty array: `"comments": []`
    - **Fallback**: if a finding cannot be pinned to a specific line (e.g. missing test, architectural concern, missing feature), do NOT create an inline comment — include it in the `Issues Found` or `Suggestions` section of the review summary instead

7.  Post the inline review by running:

    ```bash
    python3 .agents/skills/ai-review/scripts/post_review.py
    ```

## Rules

- Be constructive and specific — reference exact file paths and line numbers
- Focus on the diff only — do not review unchanged code
- Flag missing tests as a high-severity issue for new features or behaviour changes
- Do not modify any files — this is a review-only task
