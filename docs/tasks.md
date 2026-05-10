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

### ~~T-04 · WhatsApp redirect~~

- [x] On button click, read the full number from `intl-tel-input` in E.164 format
- [x] Strip the leading `+`
- [x] Validate that the number is not empty and has at least 7 digits
- [x] Redirect to `https://wa.me/<number>` in a new tab
- [x] Show inline error if number is invalid or empty

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

### ~~T-23 · About section on website~~

- [x] Add a brief section below the main input explaining what zapinit does and why it exists
- [x] Keep it short — one or two sentences on the use case and the motivation (no need to save a contact just to send a message)
- [x] Section must be accessible in both light and dark mode

---

### ~~T-24 · GitHub repo link on website~~

- [x] Add a link to the GitHub repository somewhere unobtrusive on the page (e.g. footer or top corner)
- [x] Use the GitHub mark SVG icon
- [x] Link opens in a new tab
- [x] Must be accessible in both light and dark mode

---

### ~~T-15 · Dark mode support~~

- [x] Implement dark mode using Tailwind CSS `dark:` classes
- [x] Add a theme toggle switch (Sun/Moon icon)
- [x] Persist theme preference in `localStorage`
- [x] Respect system-level color scheme preference (`prefers-color-scheme`)
- [x] Ensure all components (inputs, dropdowns, buttons) are accessible in dark mode

---

### T-25 · Buy Me a Coffee integration

- [-] Add a Buy Me a Coffee (or Buy Me a Beer) button on the website
- [-] Add the same sponsor link to the README under a dedicated `## Support` section
- [-] Button should be visually consistent with the page style and work in both light and dark mode

---

### ~~T-29 · UI localization (PT / EN)~~

- [x] Detect browser language via `navigator.language` on page load
- [x] If the language starts with `"pt"` (e.g. `pt-BR`, `pt-PT`), apply Portuguese strings; otherwise default to English
- [x] No other languages required
- [x] Localised strings must cover all user-visible text: button label, input placeholder, both error messages, and the about blurb
- [x] Add a `i18n` object in `app.js` keyed by locale (`"pt"` / `"en"`) and apply it via a single `applyLocale(lang)` function so adding new locales later requires only a new key
- [x] Expose `applyLocale` on `globalThis` to allow test stubs to call it directly

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
    And the empty-number error is "Por favor, insira um número de telefone"
    And the invalid-number error is "Número de telefone inválido"
    And the about blurb is "Cansado de salvar um contato só para mandar uma mensagem? Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça."

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
    And the empty-number error is "Please enter a phone number"
    And the invalid-number error is "Invalid phone number"
    And the about blurb is "Tired of saving a contact just to send one message? Type a number and open WhatsApp instantly, no contacts, no clutter."

  Scenario: Browser language is not set (falls back to English)
    Given the browser language is not set
    When the page loads
    Then the button label is "Open on WhatsApp"
    And the phone input placeholder is "Phone number"
    And the empty-number error is "Please enter a phone number"
    And the invalid-number error is "Invalid phone number"
    And the about blurb is "Tired of saving a contact just to send one message? Type a number and open WhatsApp instantly, no contacts, no clutter."
```

**Notes:**
- Language detection reads `navigator.language` — do not use `navigator.languages` (array) to keep the logic simple
- Tests should stub `navigator.language` via `Object.defineProperty` and call `globalThis.applyLocale(lang)` directly (passing the detected language string) to avoid full browser rendering for string-mapping coverage
- At least one test must exercise the actual page-load init path: stub `navigator.language`, trigger the init function (or reload the module), and assert that the UI strings change — this verifies that `navigator.language` is read and `applyLocale` is invoked during startup, not just that `applyLocale` maps strings correctly in isolation
- The about blurb text is set by T-23; the PT translation is: *"Cansado de salvar um contato só para mandar uma mensagem? Digite um número e abra o WhatsApp na hora, sem contatos, sem bagunça."*

---

### T-30 · DESIGN.md — living design document

- [ ] Create `docs/DESIGN.md` documenting the current visual and UX design of the app
- [ ] Cover: color palette (`#25D366` WhatsApp green, grays used for text and borders, red for errors), typography (system font stack), layout (centered column, `max-w-xl`, pill-shaped input + button), component inventory (country selector, phone input, CTA button, error message, about blurb, theme toggle), dark mode strategy (Tailwind `dark:` classes, `localStorage` persistence, `prefers-color-scheme` fallback)
- [ ] Include a **Design decisions** section explaining the key choices and their rationale (e.g. no external fonts, WhatsApp brand color, pill shape)
- [ ] Include a **Future considerations** section as a placeholder for evolving the design
- [ ] Update `AGENTS.md` to reference `docs/DESIGN.md`: AI agents working on UI tasks must read it before making visual changes, and must update it when introducing new components or changing existing ones

**Notes:**
- The document is descriptive (current state), not prescriptive — it captures what exists, not what should exist
- Keep it concise and scannable; use tables for the color palette and component inventory
- No new UI changes in this task — documentation only

---

### T-31 · SVG favicons with light/dark mode support

- [ ] Create two SVG favicons: one for light mode, one for dark mode — both AI-generated and consistent with the design documented in `docs/DESIGN.md` (T-30 must land first)
- [ ] Light mode favicon: white or light background with the WhatsApp green (`#25D366`) `zap` motif
- [ ] Dark mode favicon: dark background (`#111827` or similar) with the same green motif so it remains visible against browser chrome in dark mode
- [ ] Dynamically switch the active favicon based on the current theme (match the theme toggle state stored in `localStorage`, same logic used by the dark mode toggle)
- [ ] Also respond to `prefers-color-scheme` changes at runtime so the favicon updates without a page reload when the OS theme changes
- [ ] Place SVG files in `app/static/` and reference them from `<head>` via `<link rel="icon">` tags
- [ ] No raster fallbacks required — SVG is sufficient for all target browsers

**BDD scenarios:**

```gherkin
Feature: Dynamic favicon

  Scenario: Light mode favicon is active in light mode
    Given the theme is set to "light"
    When the page loads
    Then the favicon href points to the light-mode SVG

  Scenario: Dark mode favicon is active in dark mode
    Given the theme is set to "dark"
    When the page loads
    Then the favicon href points to the dark-mode SVG

  Scenario: Favicon updates when theme is toggled
    Given the theme is set to "light"
    When the user toggles to dark mode
    Then the favicon href updates to the dark-mode SVG without a page reload
```

**Notes:**
- Favicon switching should reuse the existing theme state rather than duplicating detection logic
- SVG favicons are generated by an AI tool (e.g. described as a prompt to an image/SVG model); the output must be clean inline SVG with no external dependencies
- Depends on T-30 for design reference

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

### ~~T-21 · PR preview deployments~~

- [x] Add `.github/workflows/preview.yml` that deploys the static page to a temporary URL on each PR open/update
- [x] Post the preview URL as a comment on the PR
- [x] Tear down the preview when the PR is closed or merged

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

### T-32 · Authenticate auto-implement workflow as `raschmitt` and sign commits

Follow-up improvement to T-22. The auto-implement workflow currently runs as `github-actions[bot]`, which means:
- OpenCode free tier won't comment on its own PRs (only on PRs opened by the paid user)
- Commits appear as "Unverified" on GitHub

- [ ] Create a GitHub Personal Access Token (classic, scopes: `repo`, `workflow`) for the `raschmitt` account and store it as `GH_PAT` in repository secrets
- [ ] Create a GPG key, add the public half to the GitHub account (Settings → SSH and GPG keys), and store the private key as `GPG_PRIVATE_KEY` in repository secrets
- [ ] In `.github/workflows/auto-implement.yml`, replace `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` with `GH_TOKEN: ${{ secrets.GH_PAT }}`
- [ ] Add a step before OpenCode runs that imports the GPG key and configures git identity + commit signing:
  ```yaml
  - name: Configure git identity and signing
    run: |
      echo "${{ secrets.GPG_PRIVATE_KEY }}" | gpg --batch --import
      git config user.name "raschmitt"
      git config user.email "<raschmitt's GitHub email>"
      git config user.signingkey "$(gpg --list-secret-keys --keyid-format=long | awk '/^sec/ {print $2}' | cut -d'/' -f2)"
      git config commit.gpgsign true
  ```
- [ ] Verify: PRs opened by the workflow are authored by `raschmitt`, commits carry the **Verified** badge, and the `GH_PAT` has the `workflow` scope so `.github/workflows/` changes can be pushed without error

**Notes:**
- The `workflow` scope on the PAT is required to push workflow file changes (the default `GITHUB_TOKEN` does not support this), which also unblocks tasks like T-26, T-27, T-28
- GPG key creation: `gpg --full-generate-key` (RSA 4096, no expiry recommended for CI); export with `gpg --armor --export-secret-key <key-id>`
- The git email must match a verified email on the GitHub account for the Verified badge to appear

---

### T-33 · Manual task selection via `workflow_dispatch`


Add a `workflow_dispatch` input to the auto-implement workflow so the user can pick which task to run when triggering manually, while preserving the existing `find-next-task` auto-detect behaviour on scheduled runs.

- [ ] Add an `inputs.task_id` text field to `workflow_dispatch` in `.github/workflows/auto-implement.yml` — accepts a task ID (e.g. `T-26`) or left blank for auto-detect
- [ ] Pass the input as a `TASK_ID` environment variable to the OpenCode step
- [ ] Update the OpenCode prompt: if `TASK_ID` is set and non-empty, skip `find-next-task` and use the ID directly; otherwise fall through to existing auto-detect logic
- [ ] Verify: manual dispatch with a task ID implements that task directly; empty ID or scheduled runs keep the current behaviour

---

## Milestone 3 — Future SaaS

> These tasks are not scheduled. Listed for architectural awareness.

- [ ] **T-08** · ~~Dockerfile + docker-compose for local dev and deployment~~ (DEPRECATED: Switching to static hosting)
- [ ] **T-09** · `POST /track` endpoint to log redirects (privacy-safe: no full numbers, only country code + digit count)
- [ ] **T-10** · User auth with OIDC (vendor-agnostic: Keycloak, Authelia, or Auth0 free tier)
- [ ] **T-11** · Browser extension (Manifest V3) reusing `app.js` logic
- [ ] **T-12** · Saved history (localStorage-first, optional cloud sync behind auth)
- [ ] **T-13** · PWA manifest + service worker for installable mobile experience
