# Fix Plan — Cross-Project Design Cohesion

**Reviewed:** 2026-07-04
**Projects compared:** ProjectSite, TradingBot, CTF-LLM, simple-webpage
**Method:** Fetched live GitHub Pages HTML for all 4 projects, compared CSS/JS/HTML structure against `template.html.j2`

---

## Result: No design drift

All 4 live pages have **identical CSS, JS, and HTML structure**. The template is a perfect single-source generator — every project that runs the generator gets the same visual output. No template changes needed.

---

## One issue found

### simple-webpage: logo SVG uses hardcoded colors

**Problem:** `logo_svg` in simple-webpage's `project.toml` uses hardcoded hex values (`#bd93f9`, `#50fa7b`) and a `0 0 40 40` viewBox instead of CSS variables and the standard `0 0 64 64` viewBox.

**Impact:**
- `updateFavicon()` theme adaptation broken — favicon stays dark-themed even in light mode
- Missing background `<rect>` means favicon has no rounded-corner container
- Non-standard viewBox (40x40 vs 64x64) means logo renders at different scale

**Fix:** Update `logo_svg` in `simple-webpage/project.toml`:
```xml
<!-- Before (broken) -->
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
<polyline points="12 10 5 20 12 30" stroke="#bd93f9" .../>
<polyline points="28 10 35 20 28 30" stroke="#bd93f9" .../>
<line x1="24" y1="30" x2="16" y2="10" stroke="#50fa7b" .../>
</svg>

<!-- After (matches convention) -->
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<rect width="64" height="64" rx="14" fill="var(--panel)"/>
<polyline points="18 16 8 32 18 48" stroke="var(--purple)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<polyline points="46 16 56 32 46 48" stroke="var(--purple)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<line x1="40" y1="48" x2="24" y2="16" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

**File:** `simple-webpage/project.toml` → `[project] logo_svg`
**Effort:** Trivial — one field edit
