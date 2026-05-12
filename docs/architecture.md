# Architecture

## Overview

**zapinit** is a web application that lets users open a WhatsApp conversation with any phone number without saving it as a contact. The user enters a number, selects the country code, and is redirected to `https://wa.me/<number>` — no backend processing required for the core flow.

The system is intentionally thin: the server only renders HTML. All business logic lives in the browser. This keeps the stack simple, cost-free to run, and easy to migrate or extend.

---

## System Diagram

```
┌─────────────────────────────────────────────────────┐
│                      Browser                        │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │               zapinit UI                     │  │
│  │  ┌──────────────────────────────────────┐    │  │
│  │  │  Country Selector  │  Phone Input    │    │  │
│  │  └──────────────────────────────────────┘    │  │
│  │               [ Open on WhatsApp ]            │  │
│  └───────────────────────────────────────────────┘  │
│                        │                            │
│              JS builds wa.me URL                    │
│                        │                            │
└────────────────────────┼────────────────────────────┘
                         │ redirect
                         ▼
              https://wa.me/<E.164 number>
                  (WhatsApp Web / App)

┌─────────────────────────────────────────────────────┐
│                  FastAPI Server                     │
│                                                     │
│   GET /  ──►  Jinja2 render  ──►  index.html        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Web framework | FastAPI | Async, typed, easy to extend with REST endpoints later |
| Templating | Jinja2 | Standard, zero runtime cost on the client |
| Styling | Tailwind CSS (CDN) | No build step required for MVP; swap to local bundle later |
| Phone input | intl-tel-input (CDN) | Mature library, flag sprites, E.164 formatting, browser locale detection |
| Testing | pytest + pytest-bdd | BDD scenarios in Gherkin, no extra toolchain |
| Linting | ruff | Fast, single tool replaces flake8 + isort + pyupgrade |
| Server | Uvicorn | ASGI, pairs naturally with FastAPI |

All choices are open-source and free. No vendor lock-in.

---

## Directory Structure

```
zapinit/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── templates/
│   │   └── index.html       # Single-page Jinja2 template
│   └── static/
│       └── js/
│           └── app.js       # Phone input init + redirect logic
├── tests/
│   ├── features/
│   │   └── whatsapp_redirect.feature   # Gherkin scenarios
│   ├── step_defs/
│   │   └── test_redirect_steps.py      # pytest-bdd step definitions
│   └── conftest.py
├── docs/
│   ├── architecture.md
│   └── tasks.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Key Design Decisions

### Redirect is client-side only

The `wa.me` URL is constructed and opened entirely in JavaScript. This means:
- Zero latency from the server on the critical path
- No phone numbers are sent to or logged by the server
- Privacy by default

### E.164 phone number format

`intl-tel-input` outputs numbers in E.164 format (e.g. `+5511999999999`). The redirect strips the `+` to match the `wa.me/<number>` spec. Validation is delegated to the library — no custom regex.

### Country auto-detection (DEPRECATED)

The previous auto-detection feature using `navigator.language` was removed to simplify the user experience and ensure consistency. The app now defaults to **Brazil (BR)** for all users. The auto-detection logic was deprecated as it often failed to accurately reflect the user's actual location (e.g., English browser settings for users in Brazil).

### Vendor-agnostic deployment

The app is a **static-only** application hosted on **GitHub Pages**. While it includes a FastAPI server for local development and testing, no backend is required for production.

| Option | Type | Recommendation |
|---|---|---|
| **GitHub Pages** | Static | **Primary** (Cost-free, no server) |
| ~~Render / Fly.io~~ | Server | DEPRECATED |
| ~~Docker~~ | Container | DEPRECATED |

The project has moved away from server-based hosting and containers in favor of a simpler, truly cost-free static model.

---

## Testing Strategy

Tests follow BDD using **Gherkin feature files** and **pytest-bdd** step definitions.

```
tests/
├── features/
│   └── whatsapp_redirect.feature   # human-readable scenarios
└── step_defs/
    └── test_redirect_steps.py      # mapped step implementations
```

### Layers

| Layer | Tool | What it covers |
|---|---|---|
| Unit | pytest | Phone number parsing, URL construction helpers |
| Integration | pytest + FastAPI TestClient | Route responses, template rendering |
| BDD | pytest-bdd | End-to-end user-facing scenarios in Gherkin |

No mocks for the HTTP layer — FastAPI's `TestClient` runs the actual app in-process.

---

## AI Workflow Strategy

Automated AI tasks are implemented as **skills** — self-contained instruction sets that can be invoked locally by a developer or triggered automatically by a GitHub Actions workflow. The two entry points must be equivalent: running a skill locally should produce the same result as the workflow run.

### Skill structure

Each skill lives under `.agents/skills/<name>/` and follows the [Codex skills spec](https://developers.openai.com/codex/skills):

```
.agents/skills/<name>/
├── SKILL.md          # required — instructions for the AI agent
├── scripts/          # optional — deterministic helper scripts
├── references/       # optional — supplementary docs
└── assets/           # optional — templates and config files
```

All logic belongs in `SKILL.md`. Scripts are only added when deterministic behavior or external tooling is needed.

### Naming convention

Skills and their corresponding workflows follow a `<context>-<action>` pattern:

| Skill | Workflow | Purpose |
|---|---|---|
| `pr-review` | `pr-review.yml` | Review PR diffs and post findings |
| `pr-fix` | `pr-fix.yml` | Fix unresolved review threads |
| `pr-open` | _(called from auto-implement)_ | Open a PR after implementation |
| `task-find-next` | _(called from auto-implement)_ | Select the next task to implement |

### Workflow design rule

Workflows must be **thin wrappers** — no business logic. A workflow's job is to set up the environment and call the skill:

```yaml
- name: Run skill
  env:
    GH_TOKEN: ${{ secrets.GH_PAT }}
  run: |
    opencode run -m <model> --dangerously-skip-permissions \
      "Follow the instructions in: @.agents/skills/<name>/SKILL.md"
```

Any logic beyond checkout, dependency install, git identity, and the `opencode run` call is a sign the logic belongs in `SKILL.md` instead.

---

## Future Expansion

The architecture is intentionally minimal so it can grow in any direction:

- **Browser extension** — reuse the same `app.js` logic, wrap in a Manifest V3 extension
- **REST API** — add FastAPI routes; the server is already async
- **Analytics** — add a POST `/track` endpoint, store to any SQL/NoSQL DB behind an abstraction layer
- **Auth & SaaS plans** — plug in any OIDC provider (Keycloak, Auth0 free tier, self-hosted Authelia)
- **Mobile app** — expose the same API, build a thin native shell
