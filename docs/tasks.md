# Tasks

Task status: `[ ]` todo · `[x]` done · `[-]` in progress

---

## Milestone 1 — Core MVP

### ~~T-01 · Project scaffold~~

- [x] Create `app/main.py` with FastAPI app instance
- [x] Create `app/templates/index.html` (empty base)
- [x] Create `app/static/js/app.js` (empty)
- [x] Add `requirements.txt` (fastapi, uvicorn, jinja2)
- [x] Add `requirements-dev.txt` (pytest, pytest-bdd, httpx, ruff)
- [x] Confirm `uvicorn app.main:app --reload` starts without errors

---

### ~~T-02 · Main page — Google-style layout~~

- [x] Centered layout with logo/name at the top
- [x] Phone number input area in the center
- [x] "Open on WhatsApp" button (WhatsApp green `#25D366`)
- [x] Responsive for mobile and desktop
- [x] No external fonts — system font stack only

**BDD scenarios:**

```gherkin
Feature: Main page renders correctly

  Scenario: User opens the app
    Given the user navigates to "/"
    Then the page title contains "zapinit"
    And a phone number input is visible
    And an "Open on WhatsApp" button is visible
```

---

### ~~T-03 · Country selector with static default (Brazil)~~

- [x] Integrate `intl-tel-input` via CDN (Custom implementation in `app.js`)
- [x] ~~On page load, read `navigator.language` to detect country~~ (DEPRECATED: Feature removed to simplify UX)
- [x] Default to Brazil (`BR` / `+55`) for all users
- [x] Dropdown shows country flag and dial code

**BDD scenarios (DEPRECATED):**
> Note: Auto-detection tests are kept for reference but are currently disabled/failing due to hardcoded default.

```gherkin
Feature: Country auto-detection

  Scenario: Browser locale is pt-BR
    Given the browser language is "pt-BR"
    When the page loads
    Then the country selector defaults to "Brazil (+55)"

  Scenario: Browser locale is en-US
    Given the browser language is "en-US"
    When the page loads
    Then the country selector defaults to "United States (+1)"

  Scenario: Browser locale is unavailable
    Given the browser language is not set
    When the page loads
    Then the country selector defaults to "Brazil (+55)"
```

---

### T-04 · WhatsApp redirect

- [ ] On button click, read the full number from `intl-tel-input` in E.164 format
- [ ] Strip the leading `+`
- [ ] Validate that the number is not empty and has at least 7 digits
- [ ] Redirect to `https://wa.me/<number>` in a new tab
- [ ] Show inline error if number is invalid or empty

**BDD scenarios:**

```gherkin
Feature: WhatsApp redirect

  Scenario: Valid Brazilian number
    Given the country is set to "Brazil (+55)"
    And the user types "11 99999-9999"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/5511999999999" in a new tab

  Scenario: Valid US number
    Given the country is set to "United States (+1)"
    And the user types "415 555 0100"
    When the user clicks "Open on WhatsApp"
    Then the browser opens "https://wa.me/14155550100" in a new tab

  Scenario: Empty number
    Given the phone input is empty
    When the user clicks "Open on WhatsApp"
    Then an error message "Please enter a phone number" is displayed
    And no redirect occurs

  Scenario: Number too short
    Given the country is set to "Brazil (+55)"
    And the user types "123"
    When the user clicks "Open on WhatsApp"
    Then an error message "Invalid phone number" is displayed
    And no redirect occurs

  Scenario: Submit via Enter key
    Given the country is set to "Brazil (+55)"
    And the user types "11 99999-9999"
    When the user presses the Enter key
    Then the browser opens "https://wa.me/5511999999999" in a new tab
```

---

### ~~T-14 · GitHub Pages deployment~~

- [x] Create a static version of the app (move `index.html` to root or `dist/`)
- [x] Ensure all assets (`app.js`, CSS) are referenced with relative paths
- [x] Add `.github/workflows/deploy.yml` for automated deployment to GH Pages
- [x] Verify the app is live at `https://<user>.github.io/zapinit/`

---

### ~~T-21 · PR preview deployments~~

- [x] Add `.github/workflows/preview.yml` that deploys the static page to a temporary URL on each PR open/update
- [x] Post the preview URL as a comment on the PR
- [x] Tear down the preview when the PR is closed or merged

---

### T-23 · About section on website

- [ ] Add a brief section below the main input explaining what zapinit does and why it exists
- [ ] Keep it short — one or two sentences on the use case and the motivation (no need to save a contact just to send a message)
- [ ] Section must be accessible in both light and dark mode

---

### T-24 · GitHub repo link on website

- [ ] Add a link to the GitHub repository somewhere unobtrusive on the page (e.g. footer or top corner)
- [ ] Use the GitHub mark SVG icon
- [ ] Link opens in a new tab
- [ ] Must be accessible in both light and dark mode

---

### T-26 · AI code review on every PR push

- [ ] Add `.github/workflows/ai-review.yml` that triggers on every `push` event to an open PR (`pull_request` → `synchronize` + `opened`)
- [ ] Use OpenAI Codex free tier via the `openai/codex` CLI to review the diff introduced by the push
- [ ] Post the review as a PR comment (update existing comment on re-push rather than creating a new one)
- [ ] Add `OPENAI_API_KEY` to repository secrets
- [ ] Scope the review to changed files only to stay within free-tier token limits

**Notes:**
- Run Codex with the diff (`git diff origin/main...HEAD`) as input so the review is focused on new changes
- Use a hidden HTML marker in the comment (e.g. `<!-- ai-review -->`) to identify and update it on subsequent pushes

---

### T-27 · Gemini fix loop on AI review and workflow failures

Closes the feedback loop started by T-22 (auto-implement) and T-26 (Codex review).

- [ ] Add `.github/workflows/ai-fix.yml` that triggers whenever T-26 posts or updates a review comment, and whenever any CI workflow job fails on a PR
- [ ] Workflow invokes Gemini CLI in YOLO mode with the following context: current diff, Codex review comment, and failed workflow logs (fetched via `gh run view`)
- [ ] Gemini applies fixes, commits to the PR branch, and pushes — which re-triggers Codex (T-26) for another review pass
- [ ] Loop continues until Codex marks the review as satisfied (detect via a specific marker in the comment, e.g. `<!-- review: ok -->`) AND all CI jobs pass
- [ ] Add a max-iteration guard (e.g. 5 rounds) to prevent infinite loops — post a comment asking for human intervention if the limit is reached
- [ ] Workflow must be idempotent: skip if the last commit on the branch was already made by the automation bot

**Notes:**
- Gemini should be given `AGENTS.md` as context so fixes respect project standards
- Workflow logs for failed jobs can be fetched with `gh run view <run-id> --log-failed`
- The loop only runs on PRs opened by the T-22 auto-implement workflow, not on human PRs

---

### T-28 · Auto-merge automation-driven PRs

Depends on T-27 — merge should only trigger once the fix loop exits cleanly.

- [ ] Initially: post a comment on the PR indicating it is ready to merge and tag the repo owner for manual review
- [ ] Later (phase 2): automatically merge the PR using `gh pr merge --squash --auto` once T-27 exits cleanly and all branch protection checks pass
- [ ] Ensure the merge commit message follows Conventional Commits format
- [ ] Notify via a final PR comment summarising what was implemented and what CI checks passed

**Notes:**
- Phase 1 (manual) should be shipped first to build confidence in the automation quality before enabling auto-merge
- Auto-merge should respect any branch protection rules already in place

---

### T-25 · Buy Me a Coffee integration

- [ ] Add a Buy Me a Coffee (or Buy Me a Beer) button on the website
- [ ] Add the same sponsor link to the README under a dedicated `## Support` section
- [ ] Button should be visually consistent with the page style and work in both light and dark mode

---

### T-29 · UI localization (PT / EN)

- [ ] Detect browser language via `navigator.language` on page load
- [ ] If the language starts with `"pt"` (e.g. `pt-BR`, `pt-PT`), apply Portuguese strings; otherwise default to English
- [ ] No other languages required
- [ ] Localised strings must cover all user-visible text: button label, input placeholder, both error messages, and the about blurb
- [ ] Add a `i18n` object in `app.js` keyed by locale (`"pt"` / `"en"`) and apply it via a single `applyLocale(lang)` function so adding new locales later requires only a new key
- [ ] Expose `applyLocale` on `globalThis` to allow test stubs to call it directly

**BDD scenarios:**

```gherkin
Feature: UI localization

  Scenario: Browser language is Portuguese (Brazil)
    Given the browser language is "pt-BR"
    When the page loads
    Then the button label is "Abrir no WhatsApp"
    And the phone input placeholder is "Número de telefone"
    And the empty-number error is "Por favor, insira um número de telefone"
    And the invalid-number error is "Número de telefone inválido"
    And the about blurb is "Cansado de salvar um contato só para mandar uma mensagem? Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça."

  Scenario: Browser language is Portuguese (Portugal)
    Given the browser language is "pt-PT"
    When the page loads
    Then the button label is "Abrir no WhatsApp"
    And the phone input placeholder is "Número de telefone"

  Scenario: Browser language is English
    Given the browser language is "en-US"
    When the page loads
    Then the button label is "Open on WhatsApp"
    And the phone input placeholder is "Phone number"
    And the empty-number error is "Please enter a phone number"
    And the invalid-number error is "Invalid phone number"
    And the about blurb is "Tired of saving a contact just to send one message? Type a number and open WhatsApp instantly, no contacts, no clutter."

  Scenario: Browser language is unsupported (falls back to English)
    Given the browser language is "fr-FR"
    When the page loads
    Then the button label is "Open on WhatsApp"
    And the phone input placeholder is "Phone number"

  Scenario: Browser language is not set (falls back to English)
    Given the browser language is not set
    When the page loads
    Then the button label is "Open on WhatsApp"
    And the phone input placeholder is "Phone number"
```

**Notes:**
- Language detection reads `navigator.language` — do not use `navigator.languages` (array) to keep the logic simple
- Tests should stub `navigator.language` via `Object.defineProperty` and call `globalThis.applyLocale()` directly to avoid full browser rendering
- The about blurb text is set by T-23; the PT translation is: *"Cansado de salvar um contato só para mandar uma mensagem? Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça."*

---

## Milestone 2 — Quality & CI

### T-05 · Test suite setup

- [ ] Create `tests/conftest.py` with FastAPI `TestClient` fixture
- [ ] Create `tests/features/` directory for `.feature` files
- [ ] Create `tests/step_defs/` for pytest-bdd step definitions
- [ ] All tests pass with `pytest`
- [ ] Remove `sonar.coverage.exclusions=app/static/**` from `sonar-project.properties`

**BDD scenarios:**

```gherkin
Feature: Server health

  Scenario: Root route responds
    Given the application is running
    When a GET request is made to "/"
    Then the response status is 200
    And the response body contains "zapinit"
```

---

### T-06 · Phone number URL builder unit tests

- [ ] Extract URL construction to a pure Python helper `build_wa_url(e164: str) -> str`
- [ ] Unit test all edge cases (leading `+`, spaces, dashes, country codes)

**BDD scenarios:**

```gherkin
Feature: WhatsApp URL builder

  Scenario Outline: Build wa.me URL from E.164 number
    Given the E.164 number is "<e164>"
    When the URL is built
    Then the result is "<expected_url>"

    Examples:
      | e164             | expected_url                        |
      | +5511999999999   | https://wa.me/5511999999999         |
      | +14155550100     | https://wa.me/14155550100           |
      | +447911123456    | https://wa.me/447911123456          |
```

---

### ~~T-07 · CI pipeline~~

- [x] Add `.github/workflows/ci.yml`
- [x] Steps: install deps → ruff lint → pytest
- [x] Pipeline runs on every push and pull request to `main`
- [x] No paid GitHub Actions minutes required (public repo uses free tier)

---

### ~~T-16 · Code coverage and mutation testing in CI~~

- [x] Add `pytest-cov==7.1.0` and `mutmut==2.5.1` to `requirements-dev.txt`
- [x] Configure coverage in `pyproject.toml`: source = `app/`, fail under **80%**
- [x] Extend `.github/workflows/ci.yml` with a `test` job: `pytest --cov=app --cov-fail-under=80 --cov-report=xml`
- [x] Add a `mutation` job that runs `scripts/check_mutation_score.py` and fails below **50%** (raise to 65% after T-06 lands)
- [x] Upload `coverage.xml` as a CI artifact for inspection
- [x] Add `scripts/check_mutation_score.py` that parses `mutmut junitxml` output and enforces the threshold

**Thresholds and rationale:**

| Metric | Threshold | Rationale |
|---|---|---|
| Line coverage | 80% | Current coverage is 100%; threshold ensures it stays high as new code is added |
| Mutation score | 50% → 65% | Starting at 50% (current score); 5 surviving mutants are static-file config lines not exercised by BDD integration tests — raise to 65% when T-06 unit tests land |

---

### ~~T-17 · SonarCloud integration~~

- [x] Create a SonarCloud account and link the `raschmitt/zapinit` GitHub repository
- [x] Add `sonar-project.properties` at the repo root with project key, organization, and source/test paths
- [x] Add a `sonarcloud` job to `.github/workflows/ci.yml` that runs after `test` and uploads `coverage.xml` to SonarCloud
- [x] Configure SonarCloud GitHub app so analysis results appear as PR checks and inline code annotations
- [x] Set Quality Gate to block PR merge if gate fails (Sonar way: coverage drop, new bugs, new vulnerabilities)

**Notes:**
- SonarCloud is free for public repos — no billing required
- `coverage.xml` produced by T-16 is the input; T-16 must land first
- The `SONAR_TOKEN` secret must be added to the GitHub repo settings before the workflow step runs

---

### ~~T-18 · Security scanning in CI~~

- [x] Add `pip-audit==2.10.0` and `bandit==1.9.4` to `requirements-dev.txt`
- [x] Add a `security` job to `.github/workflows/ci.yml` with the following steps:
  - `pip-audit` — dependency vulnerability scan (fail on any finding)
  - `bandit -r app/` — static analysis for common Python security issues (fail on medium+ severity)
- [x] Enable GitHub Dependabot for automated dependency update PRs (add `.github/dependabot.yml`)
- [x] Enable GitHub secret scanning on the repository settings to block accidental credential commits

**Notes:**
- `pip-audit` and `bandit` are both free and open source; add them as dev dependencies
- Bandit scope is `app/` only — exclude `tests/` to avoid false positives on test helpers
- The `security` job can run in parallel with `test`; it does not depend on coverage results

---

### ~~T-19 · Dependabot auto-merge~~

- [x] Extend `.github/dependabot.yml` to monitor all ecosystems in use: `pip` and `github-actions` (already present); detect and add `npm` if a `package.json` is introduced
- [x] Create `.github/workflows/dependabot-auto-merge.yml` that:
  - Triggers only on Dependabot PRs (`github.actor == 'dependabot[bot]'`)
  - Auto-approves the PR using `gh pr review --approve`
  - Enables auto-merge (squash) for **patch and minor** updates only — skips major version bumps
  - Waits for all CI checks to pass before merging (auto-merge handles this natively)
- [x] Set workflow permissions: `contents: write`, `pull-requests: write`

**Notes:**
- Project currently uses `pip` and `github-actions` ecosystems — no `npm` present
- Major version updates require manual review; the workflow must parse the version bump from the Dependabot PR metadata to enforce this
- `GITHUB_TOKEN` is sufficient — no PAT required as long as branch protection allows the token to merge

---

### ~~T-22 · Automated task implementation workflow~~

- [x] Add `.github/workflows/auto-implement.yml` scheduled every 6 hours (`cron: '0 */6 * * *'`)
- [x] Workflow reads `docs/tasks.md`, identifies the next unchecked `[ ]` task in order, and skips tasks with unmet pre-conditions
- [x] Invokes Gemini CLI in YOLO mode (`gemini --yolo`) with a prompt that includes `AGENTS.md`, `docs/tasks.md`, and `docs/architecture.md` as context so it follows project standards
- [x] Gemini creates a feature branch, implements the task, and opens a PR following the branch naming and PR template conventions in `AGENTS.md`
- [x] Workflow posts a summary comment on the opened PR indicating it was auto-generated
- [x] Add `GEMINI_API_KEY` to repository secrets (manual: add to GitHub repo Settings → Secrets)

**Notes:**
- YOLO mode allows Gemini to run shell commands and edit files without confirmation prompts
- The workflow must skip a task if an open PR already references it (by task ID in the PR title or branch name) or if a branch for it already exists — both checks required for idempotency
- Auto-generated PRs still go through the full CI pipeline before any merge

---

### ~~T-15 · Dark mode support~~

- [x] Implement dark mode using Tailwind CSS `dark:` classes
- [x] Add a theme toggle switch (Sun/Moon icon)
- [x] Persist theme preference in `localStorage`
- [x] Respect system-level color scheme preference (`prefers-color-scheme`)
- [x] Ensure all components (inputs, dropdowns, buttons) are accessible in dark mode

---

## Milestone 3 — Future SaaS

> These tasks are not scheduled. Listed for architectural awareness.

- [ ] **T-08** · ~~Dockerfile + docker-compose for local dev and deployment~~ (DEPRECATED: Switching to static hosting)
- [ ] **T-09** · `POST /track` endpoint to log redirects (privacy-safe: no full numbers, only country code + digit count)
- [ ] **T-10** · User auth with OIDC (vendor-agnostic: Keycloak, Authelia, or Auth0 free tier)
- [ ] **T-11** · Browser extension (Manifest V3) reusing `app.js` logic
- [ ] **T-12** · Saved history (localStorage-first, optional cloud sync behind auth)
- [ ] **T-13** · PWA manifest + service worker for installable mobile experience
