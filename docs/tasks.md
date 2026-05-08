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

- [ ] Add `.github/workflows/ci.yml`
- [ ] Steps: install deps → ruff lint → pytest
- [ ] Pipeline runs on every push and pull request to `main`
- [ ] No paid GitHub Actions minutes required (public repo uses free tier)

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
