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

4.  Save the review to `/tmp/ai-review.md` in this format:

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

5.  Post or update the PR comment by running:

    ```bash
    python3 .agents/skills/ai-review/scripts/post_review.py
    ```

## Rules

- Be constructive and specific — reference exact file paths and line numbers
- Focus on the diff only — do not review unchanged code
- Flag missing tests as a high-severity issue for new features or behaviour changes
- Do not modify any files — this is a review-only task
