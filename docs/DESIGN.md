# Design

Living document capturing the current visual and UX design of zapinit. This is descriptive, not prescriptive — it reflects what exists, not what should exist.

---

## Overview

zapinit is a single-page web tool that redirects the user to a WhatsApp chat given a phone number. The UI is minimal: a logo, a country selector + phone input, a call-to-action button, and a handful of supporting elements — all within a centered column layout.

---

## Color Palette

| Token | Hex | Usage |
|---|---|---|
| WhatsApp green | `#25D366` | CTA button background, "zap" in the logo |
| CTA hover | `#1ebe5d` | Button hover state |
| CTA active | `#18a852` | Button active/pressed state |
| Error red | `#ef4444` (red-500) | Error message text (light mode) |
| Error red (dark) | `#f87171` (red-400) | Error message text (dark mode) |
| Text primary | `#374151` (gray-700) | Input text, logo "init" (light mode) |
| Text primary (dark) | `#d1d5db` (gray-300) | Input text, logo "init" (dark mode) |
| Text muted | `#6b7280` (gray-500) | About blurb, icon buttons (light mode) |
| Text muted (dark) | `#9ca3af` (gray-400) | About blurb, icon buttons (dark mode) |
| Border | `#e5e7eb` (gray-200) | Input container border (light mode) |
| Border (dark) | `#374151` (gray-700) | Input container border (dark mode) |
| Page background | `#ffffff` | Page background (light mode) |
| Page background (dark) | `#111827` (gray-900) | Page background (dark mode) |
| BMC hover yellow | `#FFDD00` | Buy Me a Coffee icon hover |
| GitHub hover (light) | `#374151` (gray-700) | GitHub icon hover |
| GitHub hover (dark) | `#e5e7eb` (gray-200) | GitHub icon hover |

---

## Typography

| Property | Value |
|---|---|
| Font family | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif` |
| Logo size | `text-5xl` (3rem / 48px) |
| Logo weight | `font-light` |
| Input text | `text-base` (1rem / 16px) |
| Country selector | `text-sm` (0.875rem / 14px) |
| Button text | `font-medium` |
| Error message | `text-sm` |
| About blurb | `text-sm` |

No external fonts are loaded. The system font stack ensures fast rendering and a native feel on every platform.

---

## Layout

```
┌──────────────────────────────────────┐
│                           [🌙 theme] │  top-right
│                                      │
│          zapinit                     │  centered, 5xl
│                                      │
│    ┌──────────┬──────────────────┐   │
│    │  🇧🇷 +55  │  [Phone number]  │   │  pill-shaped input row
│    └──────────┴──────────────────┘   │
│                                      │
│         [📱 Open on WhatsApp]        │  pill-shaped CTA button
│                                      │
│          (error message)             │  centered, red
│                                      │
│    Tired of saving a contact...      │  about blurb, centered
│                                      │
│                              [☕][🐙] │  bottom-right
└──────────────────────────────────────┘
```

- **Container:** `w-full max-w-xl` centered via `flex flex-col items-center`
- **Min-height:** `min-h-screen` so the column is vertically centered on all viewports
- **Padding:** `px-4` on the body for small screens
- **Spacing:** `gap-8` between vertical sections
- **Responsive:** the CTA button switches from `w-full` (mobile) to `w-auto` (sm breakpoint via `sm:w-auto`)

---

## Component Inventory

| Component | Element | ID | Behavior |
|---|---|---|---|
| Logo | `<h1>` | — | "zap" in green, "init" in gray; `select-none` |
| Country selector | `<select>` | `country` | Populated from JS `COUNTRIES` array; defaults to Brazil (BR, +55); sorted by dial code ascending |
| Phone input | `<input type="tel">` | `phone` | `autocomplete="tel"`; placeholder set to "Phone number" |
| CTA button | `<button>` | `open-wa` | WhatsApp SVG icon + "Open on WhatsApp" label; green pill shape |
| Error message | `<p>` | `error-msg` | Hidden by default (`hidden`); shown via JS on validation failure |
| About blurb | `<p>` | — | Static text below the input area; explains the app's purpose |
| Theme toggle | `<button>` | `theme-toggle` | Fixed `top-4 right-4`; sun/moon SVG icons; toggles `dark` class on `<html>` |
| Buy Me a Coffee | `<a>` | `bmc-link` | Icon link fixed `bottom-4 right-4`; opens `buymeacoffee.com/raschmitt` |
| GitHub link | `<a>` | `github-link` | Icon link next to BMC; opens repo URL |

---

## Dark Mode Strategy

1. **Flash prevention:** An inline `<script>` in `<head>` reads `localStorage.getItem('theme')` first, falls back to `matchMedia('(prefers-color-scheme: dark)')`, and applies the `dark` class immediately — before the body renders.
2. **Toggle:** A button in the top-right corner switches between `dark` and light by toggling the `dark` class on `<html>`. The moon icon is shown in light mode; the sun icon in dark mode.
3. **Persistence:** `localStorage.setItem('theme', 'dark'|'light')` is set on every toggle. On next load the stored value takes priority.
4. **Tailwind:** `darkMode: 'class'` in the Tailwind config enables `dark:` variant class toggling. Every color token and surface has a dark-mode counterpart.

---

## Design Decisions

### No external fonts
System font stack loads instantly, matches the OS chrome, and avoids an extra network request. There is no visual benefit to a custom font for a tool this simple.

### WhatsApp brand green for CTA
Using `#25D366` makes the primary action immediately recognisable to WhatsApp users. The icon inside the button reinforces the destination. Hover and active states darken the green for tactile feedback.

### Pill shape (`rounded-full`)
The pill shape softens the interface and is consistent with WhatsApp's own UI language (chat bubbles, profile avatars). Both the input container and the CTA button use full border-radius.

### Client-side redirect only
The wa.me URL is constructed and opened in the browser with no server round-trip. This keeps phone numbers off the wire, avoids server-side logging, and eliminates latency.

### Centered single-column layout
A single purpose demands a single focal point. The centered column keeps the user's attention on the input and button pair. No sidebar, no navigation, no distractions.

### Country selector defaults to Brazil
The creator's primary audience is Brazilian. Rather than guess the user's country from the browser locale (which can be wrong), the app always defaults to Brazil (+55). The user can still pick any country from the dropdown.

### Dark mode with `prefers-color-scheme` + `localStorage`
The system preference is the default, but the explicit toggle and localStorage override give the user control. The inline script prevents the flash of unstyled light theme on load.

---

## Future Considerations

- **SVG favicons:** Light and dark variants switched dynamically based on the active theme (see T-31)
- **UI localization:** Portuguese and English string tables switchable via `navigator.language` (see T-29)
- **Saved history:** Recent numbers stored in `localStorage` with a quick-select UI
- **PWA:** Manifest + service worker for an installable, offline-capable app
- **Browser extension:** Wrap the same `app.js` logic in a Manifest V3 extension for use from any tab
- **Animation:** Subtle transitions on the CTA, error appearance, and theme toggle for polish
