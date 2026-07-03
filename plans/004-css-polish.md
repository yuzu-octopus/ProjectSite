# Plan 004: CSS polish — fluid type, text-wrap, hover derivation

**Finding:** Template uses fixed font sizes and hardcoded hover colors. Vanilla-webpage skill recommends `clamp()`, `text-wrap: balance`, and `color-mix()` for modern CSS patterns.

**Stamp:** f9687b2

## Why

Fixed `font-size: 3rem` on h1 looks oversized on narrow screens and undersized on wide ones. `clamp(1.8rem, 4vw + 1rem, 3rem)` scales proportionally. `text-wrap: balance` fixes orphaned words in long headings. `color-mix()` derives hover from the primary color so changing `--purple` automatically adjusts hover — no hardcoded second color to maintain.

## Scope

**In scope:**
- `template.html.j2` — CSS changes only (3 rules)

**Out of scope:**
- HTML structure changes
- New features or sections

## Steps

1. Read `template.html.j2`
2. Replace `.hero h1` font-size (line 209):
   - Before: `font-size: 3rem;`
   - After: `font-size: clamp(1.8rem, 4vw + 1rem, 3rem);`

3. Replace `h2` font-size (line 199):
   - Before: `font-size: 1.6rem;`
   - After: `font-size: clamp(1.2rem, 2vw + 0.8rem, 1.6rem);`

4. Add `text-wrap: balance` to headings (line 72):
   - Before: `h1, h2, h3, h4 { font-weight: 700; }`
   - After: `h1, h2, h3, h4 { font-weight: 700; text-wrap: balance; }`

5. Replace `.btn-primary:hover` (lines 249-253):
   - Before: `background: var(--pink); border-color: var(--pink); color: var(--fg);`
   - After: `background: color-mix(in oklch, var(--purple), black 15%); border-color: color-mix(in oklch, var(--purple), black 15%); color: var(--fg);`

6. Regenerate the project page and open in browser to verify

## Verification

- `uv run python genpage.py --input project.toml --output docs/index.html` — generates
- Open in browser — headings scale smoothly, no orphaned words, hover looks natural
- `ruff check genpage.py` — still passes (no Python changes)
