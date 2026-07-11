---
name: projectpage
description: Set up a project to use the ProjectSite static site generator — create project.toml, configure CI, generate docs/index.html
---

# ProjectPage Generator — Project Setup Skill

Use this skill when asked to create a GitHub Pages project page, set up a
project page generator, or convert a project to use the Dracula-themed
project template.

> **CRITICAL: NEVER touch the ProjectSite repo.**
> You read the README from GitHub — you do NOT clone, checkout, edit, or
> push to github.com/yuzu-octopus/ProjectSite. All work happens in the
> **target project's own repo**.

webfetch https://raw.githubusercontent.com/yuzu-octopus/ProjectSite/main/README.md

The README has the full TOML schema and CI config. Follow it.

## Template Features

- **Dark/Light theme**: Dracula dark (default) + Alucard light. Toggle with localStorage. First visit respects `prefers-color-scheme`.
- **Scroll-reveal animations**: Sections animate in on scroll. Falls back to visible when JS disabled (`<noscript>`).
- **Scroll-spy**: Active sidebar nav highlighting tracks current section. Works correctly for tall custom sections.
- **Syntax highlighting**: Prism.js via CDN. Add `language` field to `code_block` sections.
- **Copy-to-clipboard**: All code blocks get an icon-based copy button (Material Symbols). Shows check icon on success, close icon on failure. Includes `aria-label` for accessibility.
- **OG image auto-generation**: A 1200x630 Dracula-themed preview PNG is generated alongside each page. Pillow renders text (name, tagline, subtitle) with word-boundary wrapping and truncation. cairosvg renders only the logo SVG. Requires both `pillow` and `cairosvg`; gracefully skips if unavailable.
- **Print styles**: Sidebar hidden, backgrounds removed, clean print output.
- **Utility CSS classes**: `.callout`, `.callout-info/warning/success/error`, `.kbd`, `.divider`
- **Theme-aware logo**: Use CSS variables (`var(--panel)`, `var(--green)`, etc.) in `logo_svg`.

## CI Setup

Use the CI workflow from the README — do NOT copy a different version.
The README has the working `permissions: contents: write` and `persist-credentials: false`
that prevent 403 errors.

See: https://raw.githubusercontent.com/yuzu-octopus/ProjectSite/main/README.md
(search for "CI Setup")

## Logo & Favicon

For `logo_svg`: keep it geometric, use Dracula palette
(`#44475a`, `#50fa7b`, `#bd93f9`, `#6272a4`). 64×64 viewBox for logo.
Use CSS variables (`var(--panel)`, `var(--green)`, etc.) for theme support.

The favicon auto-generates from the sidebar logo — serialized into a data URI.
Theme-aware: CSS variables resolve to current theme colors.
No favicon fields needed in project.toml.

## Section Types

### Standard types

| Type | Required fields | Description |
|------|----------------|-------------|
| `features` | `items` (list of `{title, body}`) | Card grid |
| `table` | `headers` (list), `rows` (list of `{cells}`) | Data table |
| `steps` | `items` (list of `{title, body}`) | Numbered list |
| `terms` | `items` (list of `{term, definition}`) | Glossary |
| `code_block` | `code` (string). Optional: `language` | Preformatted code |
| `stack` | `items` (list of `{name, description}`) | Tech badge grid |
| `text` | `body` (string) | Raw HTML block |
| `links` | `items` (list of `{title, url, description}`) | External resource cards |
| `custom` | `body` (string) | Injectable HTML block |
| `notice` | `body` (string). Optional: `notice_type` | Themed callout box |
| `timeline` | `items` (list of `{title, body}`, optional `date`) | Vertical connector timeline |
| `workflow` | `items` (list of `{title, body}`) | Horizontal scroll-snap cards |

### Sidebar behavior

Each section renders a sidebar nav entry. Sections with empty `title` are
**skipped** in the sidebar (useful for `custom` sections that are pure content).

For `custom` sections, you can set sidebar entry independently:
```toml
[[sections]]
id = "notice"
type = "custom"
title = ""           # empty = no sidebar entry
icon = ""
sidebar_title = "Tip"  # override sidebar text
sidebar_icon = "info"  # override sidebar icon
body = "..."
```

## Standard Icon Mapping

Every section type has a **canonical icon**. Use these defaults so all
project pages share a consistent visual language. Only deviate if the
section's meaning genuinely calls for a different icon.

| Section type | Canonical icon | Material Symbol |
|-------------|---------------|-----------------|
| `features` | `grid` | grid_view |
| `table` (CLI/config) | `gear` | settings |
| `table` (model/spec) | `chip` | memory |
| `table` (generic) | `layers` | layers |
| `steps` | `play` | play_arrow |
| `terms` | `document` | description |
| `code_block` (quickstart) | `play` | play_arrow |
| `code_block` (CI/build) | `gear` | settings |
| `code_block` (other) | `code` | code |
| `stack` | `layers` | layers |
| `text` | `info` | info |
| `links` | `link` | link |
| `custom` | `layers` | layers |
| `notice` | `info` | info |
| `timeline` | `calendar` | calendar_month |
| `workflow` | `rocket` | rocket_launch |

### All available icon names

See the [icon macro in template.html.j2](../template.html.j2#L892) for the full list of ~130 supported Material Symbols icon names.

### Buttons

- Primary button: solid purple fill, hollow outline on hover with pop-up effect
- All buttons use `var(--purple)` border, `var(--fg)` text, 8px border-radius
- No box-shadow on any element (flat design)

### Hover Effects

- Cards: `translateY(-2px)` + `border-color: var(--purple)` on hover
- Workflow cards: same lift effect as cards
- Link cards: `translateY(-3px)` on hover
- Buttons: `translateY(-1px)` on hover

### Styled HTML Elements

For `type = "custom"` or `type = "text"` sections, these elements are themed:
- `<strong>` → purple bold
- `<em>` → cyan italic
- `<blockquote>` → purple border, muted background
- `<figure>` + `<figcaption>` → centered image with caption
- `<details>` / `<summary>` → collapsible section with purple summary
- `<code>` → green code on panel background
- `<a>` → cyan links, pink on hover

### Utility Classes

- `.callout` with variants: `.callout-info`, `.callout-warning`, `.callout-success`, `.callout-error`
- `.kbd` — keyboard shortcut styling (8px border-radius)
- `.divider` — themed horizontal rule
- Use `var(--*)` CSS variables in inline styles for theme consistency.

## Validation

The generator validates TOML structure before rendering:
- Required top-level keys: `project`, `brand`, `sections`
- Required `project.*` fields: `name`, `tagline`, `subtitle`, `description`, `github_url`, `page_url`, `logo_svg`
- Required `brand.tagline`
- Each section must have `id`, `type`, `icon`
- Per-type field validation: `items` must be list, `code` must be string, `body` must be string, etc.
- Per-item field validation: each item must have its type's required fields
