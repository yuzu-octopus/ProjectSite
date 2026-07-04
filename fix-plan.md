# Fix Plan — ProjectSite Audit

**Audit date:** July 4, 2026
**Current state:** All checks pass (ruff, pyright, generation). No known bugs.
**Adversarial review:** ✅ Completed — incorporated below.

---

## 🔴 Priority 1 — Critical Quality & Usability

### F1: No tests exist

**Problem:** `genpage.py` has zero tests. No unit tests for `validate()`, no integration tests for `generate_one()`. A regression would only be caught manually.

**Fix:**
- Add `test_genpage.py` using pytest:
  - `test_validate_rejects_missing_top_keys`
  - `test_validate_rejects_missing_project_key` — each required key
  - `test_validate_rejects_missing_brand_tagline`
  - `test_validate_rejects_empty_sections`
  - `test_validate_rejects_unknown_section_type`
  - `test_validate_rejects_missing_section_id_type_icon`
  - `test_validate_rejects_items_not_list` — e.g. `items = "string"` instead of array
  - `test_validate_rejects_code_block_missing_code`
  - `test_validate_rejects_features_missing_items`
  - `test_validate_accepts_valid_data` — golden-path
  - `test_generate_one_produces_html` — end-to-end with minimal valid TOML
  - `test_batch_skips_invalid_toml` — batch mode doesn't crash on bad files
  - `test_section_types_match_template` — parses template AST, asserts KNOWN_SECTION_TYPES matches (F14)
- Add `pytest` to `pyproject.toml` dev dependencies
- Add `pytest` step to CI

**Files:** `test_genpage.py` (new), `pyproject.toml`, `.github/workflows/check.yml`

### F2: No type checking in CI

**Problem:** AGENTS.md documents `pyright genpage.py` but CI only runs `ruff check`. Type errors can silently enter the codebase.

**Fix:**
- Add `pyright` to CI dependencies
- Add `pyright genpage.py` step after lint in CI

**Files:** `.github/workflows/check.yml`

### F3: All content invisible when JavaScript is disabled

**Problem:** Every `<section>` has `class="reveal"` which sets `opacity: 0`. If JS fails or is disabled, users see a blank page.

**Fix:** Add a `<noscript>` block with a style override:
```html
<noscript><style>.reveal { opacity: 1; transform: none; }</style></noscript>
```
Simpler than the `.js` class toggle approach — guaranteed to only fire when JS is off, no DOM manipulation needed.

**Files:** `template.html.j2`

### F4: No `prefers-color-scheme` detection on first visit

**Problem:** The theme only uses `localStorage`. First-time visitors always get dark theme, even if their OS is set to light mode.

**Fix:** In the inline theme-detection script, fall back to system preference:
```js
var saved = localStorage.getItem('theme');
if (saved) {
  document.documentElement.setAttribute('data-theme', saved);
} else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
  document.documentElement.setAttribute('data-theme', 'light');
}
```
Note: the `meta[name="theme-color"]` is set to `#282a36` in `<head>`. For first-visit light-mode users, this is briefly wrong until the script runs. This is acceptable — the script runs synchronously in `<head>`.

**Files:** `template.html.j2`

---

## 🟠 Priority 2 — Important Improvements

### F5: README has duplicate `code_block` documentation

**Problem:** `type = "code_block"` appears twice:
1. A basic version without `language` field
2. A version WITH `language` field and syntax highlighting

Users copy the first and miss syntax highlighting.

**Fix:**
- Remove the first (basic) `code_block` entry entirely
- Keep only the second version that includes `language`
- Note that `language` is optional (plain `<pre><code>` fallback when omitted)

**Files:** `README.md`

### F6: Sidebar nav has no active-section highlighting

**Problem:** No visual indication of which section the user is currently viewing.

**Fix:**
- Extend the existing IntersectionObserver to track which section is most visible
- Add `.active` class to the corresponding sidebar `<a>` element
- CSS: `.sidebar-nav a.active { background: color-mix(in srgb, var(--purple) 20%, transparent); color: var(--purple); }`

Note: use the observer already created for `.reveal` — extend it rather than creating a second one. Track the "most visible" section to avoid flicker when between sections.

**Files:** `template.html.j2`

### F7: Prism token misclassifications — documentation fix only

**Problem:** YAML with `${{ }}` template syntax (e.g., CI workflow examples) highlights poorly in Prism. The original plan suggested `shell-session` as a workaround — this was **wrong**; `shell-session` looks for CLI prompt symbols and would produce worse output.

**Fix:** Add a note in README and template comments:
- For YAML containing `${{ github.* }}` template syntax, use `language = "text"` to avoid broken highlighting
- OR: accept imperfect highlighting — the code is still readable
- The CI example in `project.toml` already uses `language = "yaml"` — this is fine since the `${{ }}` tokens are a minor visual issue, not a readability problem

No code changes needed. This is a known limitation of Prism.js, not a bug.

**Files:** `README.md`

### F8: Sidebar doesn't auto-close on mobile when a nav link is clicked

**Problem:** On mobile, clicking a sidebar nav link scrolls to the section but leaves the sidebar open, obscuring the content.

**Fix:** Add a delegated click handler on `.sidebar-nav`:
```js
document.querySelector('.sidebar-nav').addEventListener('click', function(e) {
  if (e.target.closest('a[href^="#"]')) {
    closeSidebar();
  }
});
```
This is cleaner than adding `onclick` to every `<a>` — one handler, no template changes needed.

**Files:** `template.html.j2`

### F9: Section-specific field validation (including type checks)

**Problem:** `validate()` checks section `type` is known, but doesn't verify the section has the fields its type requires, or that those fields have the right types (e.g., `items` must be a list, not a string).

If `items = "some string"` in TOML, Jinja2's `{% for item in section.items %}` iterates over characters — producing garbled output without any error.

**Fix:** After the existing type-name check, add per-type validation:
- `features`, `steps`, `stack`, `links`, `timeline`, `workflow`: require `items` (must be a list)
- `code_block`: require `code` (must be a string)
- `table`: require `headers` (list of strings) and `rows` (list of dicts with `cells`)
- `terms`: require `items` (list of dicts, each with `term` and `definition` strings)
- `text`, `custom`, `notice`: require `body` (must be a string)

**Files:** `genpage.py`

### F10: No `@media print` styles

**Problem:** Printing produces suboptimal results: fixed sidebar takes space, dark backgrounds waste ink.

**Fix:**
```css
@media print {
  .sidebar, .theme-toggle, .mobile-toggle, .sidebar-overlay { display: none; }
  .main { margin-left: 0; }
  body { background: white; color: black; }
  pre, code, .card, .callout { background: #f5f5f5; border: 1px solid #ccc; }
  a { color: #0066cc; }
}
```

**Files:** `template.html.j2`

---

## 🟡 Priority 3 — Polish & Consistency

### F11: CI uses `pip` instead of `uv`

**Problem:** AGENTS.md documents `uv run`, project uses `uv.lock`, but CI uses `pip install`. Inconsistent.

**Fix:**
- Install `uv` in CI (`pip install uv`)
- Replace `pip install jinja2 ruff` with `uv pip install --system jinja2 ruff pyright pytest`

**Files:** `.github/workflows/check.yml`

### F12: Plan 004 is DONE but marked TODO

**Problem:** `plans/README.md` still shows Plan 004 as "TODO" but all its changes (clamp(), text-wrap: balance) are already in the template.

**Fix:** Mark Plan 004 as DONE.

**Files:** `plans/README.md`

### F13: No copy-to-clipboard button on code blocks

**Problem:** Users must manually select and copy command snippets.

**Fix:**
- Wrap each `<pre>` in a `<div class="code-block-wrapper">` with `position: relative`
- Add a `<button class="copy-btn">` positioned absolutely in the top-right corner
- On click: copy `pre.querySelector('code').textContent` to clipboard (targets code element directly, avoids grabbing button text)
- Show "Copied!" feedback for 2 seconds
- Style with `var(--muted)` / `var(--purple)` on hover

**Files:** `template.html.j2`

### F14: `KNOWN_SECTION_TYPES` can drift from template

**Problem:** The Python set and Jinja2 `{% elif %}` chain can get out of sync.

**Fix (updated after adversarial review):** Instead of comments, add a unit test (bundled with F1) that:
1. Reads `template.html.j2` and extracts all `{% elif section.type == "X" %}` values using regex
2. Asserts the extracted set equals `KNOWN_SECTION_TYPES`
3. The test also catches `{% if section.type == "X" %}` for the first branch

This mechanically prevents drift without relying on developer discipline.

**Files:** `test_genpage.py` (as part of F1)

### F15: CI git user config inconsistency

**Problem:** `.github/workflows/check.yml` uses `user.name "github-actions"` with email `github-actions@github.com`. The README CI example correctly uses `github-actions[bot]` with the noreply email. GitHub's bot avatar/linking only works with the proper ID-based noreply email.

**Fix:**
- Change `user.name` to `github-actions[bot]`
- Change `user.email` to `41898282+github-actions[bot]@users.noreply.github.com`

**Files:** `.github/workflows/check.yml`

---

## 🟢 Priority 4 — Nice to Have / Deferred

### F16: TypedDict for TOML data — NOT RECOMMENDED

**Analysis after adversarial review:** `TypedDict` provides zero runtime safety because `tomllib.load()` returns `dict[str, Any]`. It would pass pyright but silently accept malformed TOML at runtime. This is false security.

**Decision:** Skip. Focus on F9 (runtime validation with type checks) instead.

### F17: XSS footgun with `autoescape=False`

**Observation:** The template uses `autoescape=False` (line with `# noqa: S701`). Fields like `project.name`, `section.title`, and `section.body` (in `text`/`custom`/`notice` types) are rendered without escaping. This is a deliberate design choice — TOML input is considered "trusted."

`code_block` content correctly uses `| e` filter.

**Fix:** Add a note to README's "Notes" section:
> TOML input is fully trusted — HTML in `body` fields is rendered raw. Only use `code_block` with `language` for untrusted code snippets (it auto-escapes).

**Files:** `README.md`

### F18: Dynamic favicon regeneration on every theme toggle

**Observation:** `updateFavicon()` clones SVG, tree-walks elements, resolves CSS variables, serializes. Works fine for simple SVGs but is O(n) on SVG element count and runs on every toggle.

**Current status:** No action needed. The project's logo SVG has ~8 elements.

### F19: CSS is one monolithic block (~700 lines)

**Observation:** Inline `<style>` is hard to navigate. But "single self-contained HTML file" is an explicit design goal.

**Decision:** Leave as-is. This is a feature, not a bug.

---

## Summary of Changes

| # | Priority | File | Change |
|---|----------|------|--------|
| F1 | 🔴 | `test_genpage.py` (new) | Pytest tests for validation, generation, type-check sync |
| F1 | 🔴 | `pyproject.toml` | Add pytest dev dependency |
| F1 | 🔴 | `.github/workflows/check.yml` | Add pytest step |
| F2 | 🔴 | `.github/workflows/check.yml` | Add pyright step |
| F3 | 🔴 | `template.html.j2` | `<noscript>` fallback for reveal animations |
| F4 | 🔴 | `template.html.j2` | `prefers-color-scheme` fallback in theme init |
| F5 | 🟠 | `README.md` | Deduplicate code_block docs |
| F6 | 🟠 | `template.html.j2` | Scroll-spy active nav highlighting |
| F7 | 🟠 | `README.md` | Document Prism YAML limitation with `${{ }}` |
| F8 | 🟠 | `template.html.j2` | Auto-close mobile sidebar on nav click |
| F9 | 🟠 | `genpage.py` | Per-type field validation with type checks |
| F10 | 🟠 | `template.html.j2` | `@media print` styles |
| F11 | 🟡 | `.github/workflows/check.yml` | Use uv instead of pip |
| F12 | 🟡 | `plans/README.md` | Mark Plan 004 as DONE |
| F13 | 🟡 | `template.html.j2` | Copy button on code blocks |
| F14 | 🟡 | `test_genpage.py` (part of F1) | Test that KNOWN_SECTION_TYPES matches template |
| F15 | 🟡 | `.github/workflows/check.yml` | Fix git user.name + user.email for bot avatar |
| F17 | 🟢 | `README.md` | Document autoescape/XSS trust boundary |

**Total: 15 actionable findings (down from 16 — F14 merged into F1, F16 removed)**

## Execution Order

```
F3 + F4 (template JS fixes, independent)
  → F1 + F9 (tests + validation, interdependent)
    → F2 + F11 + F15 (CI fixes, all in check.yml)
      → F5 + F7 + F12 + F17 (docs housekeeping)
        → F6 + F8 + F10 (JS/CSS UX improvements)
          → F13 (code block polish)
```
