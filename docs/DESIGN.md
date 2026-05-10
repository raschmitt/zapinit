# Design

Living document capturing the current visual and UX design of zapinit.

---

## Color Palette

| Token | Hex | Usage |
|---|---|---|
| WhatsApp green | `#25D366` | Brand color, CTA button background, logo "zap" half |
| Green hover | `#1ebe5d` | CTA button hover state |
| Green active | `#18a852` | CTA button active/pressed state |
| White | `#ffffff` | Page background (light mode) |
| Gray 900 | `#111827` | Page background (dark mode) |
| Gray 700 | `#374151` | Primary text (dark mode logo "init" half) |
| Gray 500 | `#6b7280` | Secondary text, about blurb, icons (light mode) |
| Gray 400 | `#9ca3af` | Secondary text (dark mode), placeholder text (dark mode) |
| Gray 300 | `#d1d5db` | Logo "init" half (dark mode) |
| Gray 200 | `#e5e7eb` | Input container border (light mode) |
| Gray 100 | `#f3f4f6` | Hover background for icon buttons (light mode) |
| Gray 700 | `#374151` | Input container border (dark mode) |
| Gray 800 | `#1f2937` | Hover background for icon buttons (dark mode) |
| Red 500 | `#ef4444` | Error message text (light mode) |
| Red 400 | `#f87171` | Error message text (dark mode) |

---

## Typography

| Element | Stack |
|---|---|
| Body / UI | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif` |
| Logo | Same system stack, `font-light`, `tracking-tight`, `text-5xl` |

No external fonts are loaded. The system font stack ensures fast rendering and native feel across platforms.

---

## Layout

The page uses a single centered column layout:

```
┌────────────────────────────────────┐
│         Theme toggle (top-right)   │
│                                    │
│           zapinit (logo)           │
│                                    │
│  ┌── country ──┴── phone ──────┐  │
│  │  [▼ +55 🇧🇷] │ [__________]  │  │
│  └──────────────────────────────┘  │
│                                    │
│        [  Open on WhatsApp  ]      │
│                                    │
│          [error message]           │
│                                    │
│  About blurb (one sentence)        │
│                                    │
│                     GitHub link BR │
└────────────────────────────────────┘
```

- **Max width**: `max-w-xl` (36rem / 576px)
- **Centering**: `flex-col items-center justify-center` with `min-h-screen`
- **Padding**: `px-4` on body for safe margins on small screens
- **Spacing**: `gap-8` between major sections

---

## Component Inventory

| Component | Element | Description |
|---|---|---|
| **Logo** | `<h1>` | "zap" in green (`#25D366`) + "init" in gray, `text-5xl font-light tracking-tight`, non-selectable |
| **Country selector** | `<select>` | Dropdown listing ~67 countries sorted by dial code ascending. Each option shows flag emoji + dial code. Default: Brazil (+55). Styled inline inside the pill-shaped input group. |
| **Phone input** | `<input type="tel">` | Text input with `autocomplete="tel"`. Placeholder: "Phone number" (localised). Flex-grows inside the pill container. Validation via `libphonenumber-js`. |
| **CTA button** | `<button>` | "Open on WhatsApp" with WhatsApp icon SVG. WhatsApp green background, pill shape, full-width on mobile, auto-width on desktop. Opens `wa.me/<number>` in a new tab via `window.open`. |
| **Error message** | `<p>` | Hidden by default, shown inline when validation fails. Red text, positioned below the CTA button. Two messages: empty-number and invalid-number. |
| **About blurb** | `<p>` | One-sentence description below the button. Gray, centered, `max-w-sm` constrained. Explains the value proposition. |
| **Theme toggle** | `<button>` | Fixed top-right corner. Sun/Moon SVG icons toggled via `hidden` class. Persists preference to `localStorage`. |
| **GitHub link** | `<a>` | Fixed bottom-right corner. GitHub mark SVG icon. Opens `https://github.com/raschmitt/zapinit` in a new tab. |

---

## Dark Mode Strategy

Dark mode is implemented with Tailwind's `class`-based strategy:

1. **Detection**: On page load, an inline `<script>` before the DOM reads `localStorage.getItem('theme')`. If `"dark"`, or if no preference is stored and `prefers-color-scheme: dark` matches, the `dark` class is added to `<html>`.
2. **Toggle**: A Sun/Moon button in the top-right corner switches the theme. Clicking stores the inverse preference in `localStorage` and toggles the `dark` class.
3. **Styling**: All components use Tailwind `dark:` prefixed classes for dark mode variants. The logo "init" half, borders, text, and backgrounds all have explicit dark mode counterparts.
4. **Fallback**: If `localStorage` is empty, the OS-level `prefers-color-scheme` media query is used as the default. No flash of unstyled dark mode occurs because the theme script runs synchronously before rendering.

---

## Design Decisions

| Decision | Rationale |
|---|---|
| **No external fonts** | Eliminates render-blocking requests and CLS from font swaps. System fonts render instantly and feel native on every OS. |
| **WhatsApp brand green (`#25D366`) as accent** | Creates a strong visual association with WhatsApp. The color appears in the logo and the CTA button, guiding users to the primary action. |
| **Pill-shaped (`rounded-full`) input + button** | Rounded shapes feel modern and approachable. Consistent pill shapes across these two elements creates visual harmony. |
| **Country selector as a native `<select>`** | Lightweight, no external dependencies, accessible by default, works on all devices without JS overhead for the dropdown itself. |
| **Server renders HTML only** | Keeps the backend trivial — no API, no auth, no DB. The entire business logic lives in `app.js`. This makes static deployment (GitHub Pages) possible. |
| **Dark mode persists to localStorage** | Respects user choice across sessions. The `prefers-color-scheme` fallback means new visitors get the OS default without explicit configuration. |
| **libphonenumber-js for validation** | Lightweight client-side phone validation library. Parses and validates E.164 numbers without a network round-trip. |
| **Fixed-position icon buttons** | Theme toggle (top-right) and GitHub link (bottom-right) stay accessible regardless of scroll position. Minimal visual weight — small, monochrome, no background. |

---

## Future Considerations

- **Favicon with light/dark variants** — Two SVGs that switch based on the active theme, matching the logo color scheme.
- **Localization (PT / EN)** — Detect browser language and swap UI strings for all user-visible text.
- **Donation / sponsor button** — Buy Me a Coffee or similar, visually consistent with the page style.
- **PWA manifest + service worker** — Enable installable mobile experience with offline support.
- **Browser extension** — Wrap the same `app.js` logic in a Manifest V3 extension for use from any page.
- **Accessibility audit** — Review contrast ratios, keyboard navigation, and screen reader support against WCAG 2.1 AA.
