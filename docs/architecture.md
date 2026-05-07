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

### Country auto-detection

The browser's `navigator.language` tag (e.g. `pt-BR`, `en-US`) is parsed on load to pre-select the country. Falls back to Brazil (`BR`) if the locale is ambiguous or unavailable. No geolocation API is used — no permission prompt, no latency.

### Vendor-agnostic deployment

The app has no hard dependency on any cloud provider. Any environment that runs Python 3.11+ and exposes a port works:

| Option | Free tier |
|---|---|
| Render | Yes (spins down on idle) |
| Railway | Yes (limited hours/month) |
| Fly.io | Yes (2 shared VMs) |
| Self-hosted VPS | Depends on provider |

A single `Dockerfile` (to be added) covers all of the above.

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

## Future Expansion

The architecture is intentionally minimal so it can grow in any direction:

- **Browser extension** — reuse the same `app.js` logic, wrap in a Manifest V3 extension
- **REST API** — add FastAPI routes; the server is already async
- **Analytics** — add a POST `/track` endpoint, store to any SQL/NoSQL DB behind an abstraction layer
- **Auth & SaaS plans** — plug in any OIDC provider (Keycloak, Auth0 free tier, self-hosted Authelia)
- **Mobile app** — expose the same API, build a thin native shell
