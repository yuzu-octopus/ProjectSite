---
feature: projectpage-generator
status: delivered
specs:
  - compose/specs/2026-06-23-projectpage-generator-design.md
plans:
  - compose/plans/2026-06-23-projectpage-generator.md
branch: main
commits: 3e325d8..44f5ac8
---

# ProjectPage Generator — Final Report

## What Was Built

A Python + Jinja2 static site generator that reads project metadata from TOML
files and produces self-contained GitHub Pages HTML pages. Each project gets
one `.toml` data file in `projects/`; running `genpage.py --batch` generates
all project pages into `docs/<ProjectName>/index.html`.

Replaces hand-written HTML for TradingBot and CTF-LLM project pages. The
generated pages are pixel-identical to the originals — same Dracula theme,
same JetBrains Mono font, same sidebar with icon nav, same section types.

## Architecture

```
ProjectSite/
├── projects/              # TOML data — one per project
│   ├── tradingbot.toml
│   └── ctf-llm.toml
├── template.html.j2       # Jinja2 template (Dracula CSS + all section types)
├── genpage.py             # Python CLI: reads TOML → renders template → writes HTML
├── docs/                  # Generated output (GitHub Pages root)
│   ├── tradingbot/index.html
│   └── ctf-llm/index.html
└── .github/workflows/
    └── deploy.yml          # Auto-generate on push
```

**Data flow:** TOML → `tomllib` (stdlib) → dict → Jinja2 `Environment.render()` → self-contained `index.html`.

### Section types

| Section | TOML keys | Renders as |
|---------|-----------|------------|
| `features` | `items[].{title,body}` | Card grid |
| `table` | `headers[]`, `rows[].cells[]` | Data table |
| `steps` | `items[].{title,body}` | Numbered list |
| `terms` | `items[].{term,definition}` | Glossary |
| `code_block` | `code` | Pre-formatted code |
| `stack` | `items[].{name,description}` | Tech badges |
| `text` | `body` | Raw HTML |

### Design Decisions

- **TOML over YAML/JSON**: Python stdlib `tomllib` since 3.11, unambiguous syntax,
  inline comments supported.
- **Jinja2 over f-strings**: Clean separation of markup and logic. Template is a
  faithful port of the hand-written HTML.
- **Single-file output**: Matches the existing `docs/index.html` pattern. No build
  step, no external assets, works with GitHub Pages' `docs/` folder out of the box.
- **Subscript syntax for "items" key**: Jinja2 resolves `dict.items` as the
  built-in method before checking dict keys, so `section["items"]` is required
  in the template (confirmed via debugging).

## Usage

Single project:
```bash
uv run python genpage.py --input projects/tradingbot.toml
# Outputs to docs/tradingbot/index.html
```

All projects:
```bash
uv run python genpage.py --batch
# Outputs to docs/<project-name>/index.html for each .toml in projects/
```

Custom output path:
```bash
uv run python genpage.py --input projects/tradingbot.toml --output /tmp/test.html
```

CI runs `--batch` automatically on push to `main` when TOML, template, or
generator files change.

## Verification

- Content checks: all 9 sections verified present in TradingBot output, all 9
  in CTF-LLM output (headings, tables, code blocks, sidebar).
- Visual comparison: both pages opened in browser and confirmed pixel-identical
  to the original hand-written HTML (same layout, colors, fonts, responsive
  behavior).
- Generator handles edge cases: `quickstart_url` optional (hero omits button
  when absent), `og_image` optional (meta tags omitted), Jinja2 `urlencode`
  filter for inline favicon SVGs.

## Journey Log

- [lesson] Jinja2 resolves `dict.items` as the built-in method before checking
  dict keys. Must use `section["items"]` subscript syntax to access TOML data
  with an "items" key.
- [lesson] `pyproject.toml` with no build backend works fine with `uv sync` —
  no need for `[build-system]` for a script-only project.

## Source Materials

| File | Role | Notes |
|------|------|-------|
| `compose/specs/2026-06-23-projectpage-generator-design.md` | Design spec | Complete schema and architecture |
| `compose/plans/2026-06-23-projectpage-generator.md` | Implementation plan | 6 tasks, fully executed |
