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

### T-03 · Country selector with browser auto-detection

- [ ] Integrate `intl-tel-input` via CDN
- [ ] On page load, read `navigator.language` to detect country
- [ ] Fall back to Brazil (`BR` / `+55`) when locale is ambiguous or unavailable
- [ ] Dropdown shows country flag and dial code

**BDD scenarios:**

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

### T-14 · GitHub Pages deployment

- [ ] Create a static version of the app (move `index.html` to root or `dist/`)
- [ ] Ensure all assets (`app.js`, CSS) are referenced with relative paths
- [ ] Add `.github/workflows/deploy.yml` for automated deployment to GH Pages
- [ ] Verify the app is live at `https://<user>.github.io/zapinit/`

---

## Milestone 2 — Quality & CI

### T-05 · Test suite setup

- [ ] Create `tests/conftest.py` with FastAPI `TestClient` fixture
- [ ] Create `tests/features/` directory for `.feature` files
- [ ] Create `tests/step_defs/` for pytest-bdd step definitions
- [ ] All tests pass with `pytest`

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

### T-07 · CI pipeline

- [x] Add `.github/workflows/ci.yml`
- [x] Steps: install deps → ruff lint → pytest
- [x] Pipeline runs on every push and pull request to `main`
- [x] No paid GitHub Actions minutes required (public repo uses free tier)

---

### T-16 · Code coverage and mutation testing in CI

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

### T-17 · SonarCloud integration

- [ ] Create a SonarCloud account and link the `raschmitt/zapinit` GitHub repository
- [ ] Add `sonar-project.properties` at the repo root with project key, organization, and source/test paths
- [ ] Add a `sonarcloud` job to `.github/workflows/ci.yml` that runs after `test` and uploads `coverage.xml` to SonarCloud
- [ ] Configure SonarCloud GitHub app so analysis results appear as PR checks and inline code annotations
- [ ] Set Quality Gate to block PR merge if gate fails (Sonar way: coverage drop, new bugs, new vulnerabilities)

**Notes:**
- SonarCloud is free for public repos — no billing required
- `coverage.xml` produced by T-16 is the input; T-16 must land first
- The `SONAR_TOKEN` secret must be added to the GitHub repo settings before the workflow step runs

---

### T-18 · Security scanning in CI

- [x] Add `pip-audit==2.10.0` and `bandit==1.9.4` to `requirements-dev.txt`
- [x] Add a `security` job to `.github/workflows/ci.yml` with the following steps:
  - `pip-audit` — dependency vulnerability scan (fail on any finding)
  - `bandit -r app/` — static analysis for common Python security issues (fail on medium+ severity)
- [x] Enable GitHub Dependabot for automated dependency update PRs (add `.github/dependabot.yml`)
- [ ] Enable GitHub secret scanning on the repository settings to block accidental credential commits

**Notes:**
- `pip-audit` and `bandit` are both free and open source; add them as dev dependencies
- Bandit scope is `app/` only — exclude `tests/` to avoid false positives on test helpers
- The `security` job can run in parallel with `test`; it does not depend on coverage results

---

### T-15 · Dark mode support

- [ ] Implement dark mode using Tailwind CSS `dark:` classes
- [ ] Add a theme toggle switch (Sun/Moon icon)
- [ ] Persist theme preference in `localStorage`
- [ ] Respect system-level color scheme preference (`prefers-color-scheme`)
- [ ] Ensure all components (inputs, dropdowns, buttons) are accessible in dark mode

---

## Milestone 3 — Future SaaS

> These tasks are not scheduled. Listed for architectural awareness.

- [ ] **T-08** · ~~Dockerfile + docker-compose for local dev and deployment~~ (DEPRECATED: Switching to static hosting)
- [ ] **T-09** · `POST /track` endpoint to log redirects (privacy-safe: no full numbers, only country code + digit count)
- [ ] **T-10** · User auth with OIDC (vendor-agnostic: Keycloak, Authelia, or Auth0 free tier)
- [ ] **T-11** · Browser extension (Manifest V3) reusing `app.js` logic
- [ ] **T-12** · Saved history (localStorage-first, optional cloud sync behind auth)
- [ ] **T-13** · PWA manifest + service worker for installable mobile experience
