# Plan: Fix template issues

## Critical Fixes

### 1. Favicon — use MDI icon as default, allow override in project.toml

The favicon should use a simple MDI-style icon (the home or page icon) instead
of the current custom circle+plus design. Keep `favicon_dark`/`favicon_light`
as optional overrides in project.toml.

**Changes to template.html.j2:**
- Replace hardcoded favicon SVG with a simple MDI-style icon using CSS variables
- Make `favicon_dark`/`favicon_light` optional — if not provided, use default

**Changes to genpage.py:**
- Remove `favicon_dark`/`favicon_light` from `REQUIRED_PROJECT_KEYS`
- Make them optional in validation

### 2. Fix link styling — make selectors more specific

Line 89: `a:not(.btn):not(.link-card)` is too broad. Fix by scoping to main content.

**Replace with:**
```css
.main a { color: var(--cyan); text-decoration: none; }
.main a:hover { color: var(--pink); }
.sidebar-footer a { color: var(--purple); text-decoration: none; }
.sidebar-footer a:hover { color: var(--pink); }
```

### 3. Fix theme toggle border behavior

The theme toggle should:
- Default: `border: 1px solid var(--muted)` (neutral border)
- Hover: border changes to `var(--purple)`, icon changes color to `var(--purple)`
- No persistent pink/purple border

**Replace focus-visible pink with purple to match theme:**
```css
.theme-toggle:focus-visible {
  outline: 2px solid var(--purple);
  outline-offset: 2px;
}
```

### 4. Fix MDI icon name mappings

Add a mapping dict in Jinja2 macro to convert friendly names to MDI names:

```
home → mdi-home ✓
grid → mdi-view-grid (not mdi-grid)
info → mdi-information (not mdi-info)
chip → mdi-chip ✓
layers → mdi-layers ✓
document → mdi-file-document (not mdi-document)
play → mdi-play ✓
gear → mdi-cog (not mdi-gear)
link → mdi-link ✓
```

### 5. Fix code block consistency

Add Prism CSS overrides to match non-highlighted code blocks:
- Same font-size, font-family, line-height
- Same padding, border-radius, background

### 6. Add more Prism languages

Add: YAML, JSON, TypeScript, PHP, Rust, Go, C, C++, Java, Swift, Kotlin, Shell (bash alias), Dockerfile, Markdown

## Files to modify

- `template.html.j2` — all CSS/HTML changes
- `genpage.py` — make favicon fields optional
- `README.md` — update icon names, add new language support
