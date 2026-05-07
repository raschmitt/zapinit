# AGENTS.md

Guidelines for AI agents working in this repository. Read this before making any change.

---

## GitHub Account

Always use the **`raschmitt`** account for every interaction with GitHub and the `gh` CLI.

This repo uses a multi-account SSH setup. The correct remote host alias is `github-raschmitt`, not `github.com`.

```bash
# Verify the active account before any gh command
gh auth status

# Correct remote URL format for this repo
git remote set-url origin git@github-raschmitt:raschmitt/zapinit.git

# If you need to switch active account
gh auth switch --user raschmitt
```

Never push or open PRs from the `raschmitt-tl` account.

---

## Branch Rules

**No direct pushes to `main`.** Every change — including docs, config, and fixes — goes through a pull request.

Branch naming follows this pattern:

```
<type>/<short-description>
```

| Type | When to use |
|---|---|
| `feat/` | New feature or user-facing behavior |
| `fix/` | Bug fix |
| `chore/` | Tooling, deps, config, CI |
| `docs/` | Documentation only |
| `test/` | Adding or fixing tests with no behavior change |
| `refactor/` | Code change with no behavior or test change |

Examples:
```
feat/phone-country-selector
fix/empty-number-validation
chore/add-ci-workflow
docs/update-architecture
test/bdd-redirect-scenarios
```

Keep branch names lowercase, hyphen-separated, no slashes beyond the prefix.

---

## Commit Conventions

One task = one commit. Do not bundle unrelated changes.

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short imperative summary>

<optional body: explain the why, not the what>
```

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Non-functional change (deps, config, tooling) |
| `docs` | Documentation only |
| `test` | Tests only |
| `refactor` | Refactor with no behavior change |
| `style` | Formatting, whitespace — no logic change |
| `ci` | CI/CD pipeline changes |

Rules:
- Summary line: max 72 characters, imperative mood ("add", "fix", "remove" — not "added" or "fixes")
- No period at the end of the summary line
- Body is optional but recommended when the *why* is non-obvious
- Never use `--no-verify` to skip hooks

---

## Pull Requests

Every PR must have:

**Title** — same format as a commit message summary:
```
feat(redirect): add WhatsApp URL builder with E.164 formatting
```

**Description** — always use the repository PR template located at `.github/pull_request_template.md`. Never skip or replace it with free-form text. The template sections are:

| Section | What to write |
|---|---|
| `## Task/Issue` | Link to the task in `docs/tasks.md` (e.g. `T-02`) or an issue number |
| `## What?` | What this PR changes — specific and concise |
| `## Why?` | Why the change is needed and what problem it solves |

When opening a PR via `gh pr create`, pass the description through a heredoc so the template structure is preserved:

```bash
gh pr create \
  --title "feat(redirect): add WhatsApp URL builder" \
  --body "$(cat <<'EOF'
## Task/Issue
T-04 · WhatsApp redirect

## What?
Add E.164 phone number formatting and wa.me URL construction.

## Why?
Users need to be redirected to the correct WhatsApp Web URL based on
the country code and local number they entered.
EOF
)"
```

Additional rules:
- Keep PRs small and focused on a single task
- Do not mix feature changes with refactors in the same PR
- All CI checks must pass before merging
- Never force-push to a PR branch after review has started

---

## Testing Requirements

**No feature PR is complete without tests.**

- Every new user-facing behavior must have at least one BDD scenario in `tests/features/`
- Every new helper function must have at least one unit test
- Every new route must have at least one integration test using `TestClient`
- Check `docs/tasks.md` — BDD scenarios are already written for each task; implement them, don't skip them

Run the full suite before opening a PR:

```bash
pytest
```

Run linting:

```bash
ruff check .
ruff format --check .
```

Both must pass with zero errors.

---

## Task Tracking

`docs/tasks.md` is the source of truth for what needs to be done.

- Before starting work, find the relevant task and mark it `[-]` (in progress)
- When the PR is merged, mark it `[x]` (done) in a follow-up commit to `main` via PR, or include it in the same PR
- Do not invent scope beyond what the task describes — if the task is small, the PR should be small

---

## Code Standards

- Python 3.11+
- Type hints on all function signatures
- No `print()` in production code — use `logging` if needed
- No hardcoded secrets, tokens, or phone numbers in any file
- No commented-out code committed to the repo
- Prefer explicit over implicit; prefer flat over nested
- Keep functions small and single-purpose

---

## AI-Specific Practices

These rules exist because AI agents make mistakes that humans rarely make. Follow them strictly.

### Read before writing
Always read the relevant files before editing them. Do not assume file contents.

### Verify, don't guess
Before referencing a function, class, or file path, confirm it exists. Grep or read first.

### One thing at a time
Complete one task fully (code + tests + passing CI) before moving to the next. Do not leave half-done changes in a branch.

### Explain before acting on irreversible changes
For destructive or hard-to-reverse operations (dropping files, force operations, schema changes), state what you are about to do and why before executing.

### Never touch unrelated files
If a file is not required by the current task, do not modify it — not for cleanup, not for style, not for "while I'm here" improvements.

### Do not hallucinate dependencies
Only use libraries that are already in `requirements.txt` or `requirements-dev.txt`. If you need a new dependency, add it explicitly and justify it.

### Secrets and credentials
Never commit `.env` files, API keys, tokens, or real phone numbers. If you need environment variables, document them in the README under a dedicated section and load them with `python-dotenv` or native environment access.

### Keep diffs minimal
A small, focused diff is easier to review and less likely to introduce bugs. Resist the urge to refactor surrounding code unless the task explicitly requires it.
