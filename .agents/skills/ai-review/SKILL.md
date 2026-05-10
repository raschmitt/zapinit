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

2.  Read the full content of each changed file to understand context.

3.  Analyze the changes for:
    - Logic errors and potential bugs
    - Security vulnerabilities
    - Code quality and maintainability issues
    - Missing error handling
    - Deviation from project conventions (see `AGENTS.md` — code standards, commit conventions, testing requirements)
    - Missing or inadequate tests (check the `tests/` directory)
    - Edge cases not handled

4.  Save the review summary to `/tmp/ai-review.md` in this format:

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

5.  Save inline review comments to `/tmp/ai-review-comments.json`. Each comment
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

6.  Post the inline review by running:

    ```bash
    python3 .agents/skills/ai-review/scripts/post_review.py
    ```

## Rules

- Be constructive and specific — reference exact file paths and line numbers
- Focus on the diff only — do not review unchanged code
- Flag missing tests as a high-severity issue for new features or behaviour changes
- Do not modify any files — this is a review-only task
