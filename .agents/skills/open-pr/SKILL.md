---
name: open-pr
description: Opens a pull request for the current task following project conventions. Triggers when asked to open, create, or submit a PR after implementation is complete. Does NOT trigger for reviewing or merging PRs.
---

## Step 1 — commit all relevant files

Before anything else, make sure all relevant files are staged and committed to the working branch:

```bash
git status
git add <relevant files>
git commit -m "<type>(T-XX): <short imperative summary>"
```

Only commit files that belong to the current task. Do not use `git add .` or `git add -A` — stage files explicitly. Follow the commit conventions in `AGENTS.md` and include a `Co-authored-by` trailer for the AI agent.

## Step 2 — analyze the diff

Once committed, run the diff analyzer to get a structured summary of what changed:

```bash
python3 .agents/skills/open-pr/scripts/analyze_diff.py
```

The output includes `changed_files`, `commit_subjects`, and a `diff_excerpt` (capped at 400 lines). Use these to derive:
- **What?** — concrete changes made (from `changed_files` and `diff_excerpt`)
- **Why?** — motivation behind them (from `commit_subjects` and task context)

## Step 3 — open the PR

Then open the PR by running:

```bash
python3 .agents/skills/open-pr/scripts/open_pr.py <path-to-pr.json>
```

The PR always targets `main` — the script enforces this automatically.

## Input JSON format

Create a temporary file (e.g. `/tmp/pr.json`) with this structure:

```json
{
  "task_id": "T-04",
  "task_name": "WhatsApp redirect",
  "title": "feat(T-04): add WhatsApp URL builder with E.164 formatting",
  "what": [
    "Add build_wa_url() helper that formats E.164 numbers for wa.me",
    "Add client-side redirect on button click and Enter key"
  ],
  "why": [
    "Users need to open WhatsApp without saving the number as a contact",
    "E.164 formatting is required by the wa.me URL spec"
  ]
}
```

## Conventions

- **Title** follows Conventional Commits: `<type>(T-XX): <short imperative summary>` — max 72 chars, no period
- **Task/Issue** section must reference `docs/tasks.md` using the format `T-XX · Task name`
- **What?** and **Why?** must be bullet lists — no prose paragraphs
- PR body is built from `.github/pull_request_template.md` sections
- Never skip or replace the template with free-form text
