# ProjectPage — Static Site Generator for GitHub Project Pages

## [S1] Problem

Multiple projects (TradingBot, CTF-LLM) share an identical layout for their
GitHub Pages documentation sites: Dracula theme, JetBrains Mono font, sidebar
navigation, hero section, feature cards, tables, code blocks, glossary lists,
and tech stack badges. The HTML is hand-written and duplicated — any layout
change must be edited in every project, and creating a page for a new project
means copying and hand-editing 600+ lines of HTML.

## [S2] Solution

A Python + Jinja2 static site generator that:

1. Reads project data from a TOML file
2. Renders a single Jinja2 HTML template with the shared Dracula layout
3. Outputs a self-contained `index.html` — no external CSS, no build step

The generator lives in the `ProjectSite` repo and is triggered by GitHub
Actions on push. Each project gets one TOML file and one generated HTML page.

## [S3] TOML Data Schema

Each `.toml` file in `projects/` describes one project page.

### Top-level fields

```toml
[project]
name = "TradingBot"                        # page title, hero heading
tagline = "Multi-stock ML trading bot"     # hero tagline
subtitle = "All S&P 500 stocks pass through..."  # hero subtitle (longer)
description = "..."                        # meta description for SEO
github_url = "https://github.com/yuzu-octopus/Simple-Trader"
page_url = "https://yuzu-octopus.github.io/TradingBot/"

[brand]
tagline = "ML · S&P 500 · Transformer"     # shown in sidebar below name
logo_svg = """<svg viewBox="0 0 64 64"...>"""  # inline SVG for sidebar logo
```

### Section types

#### `features` — card grid

```toml
[[sections]]
id = "features"
type = "features"
title = "Features"
icon = "grid"

[[sections.items]]
title = "Decoder-Only Transformer"
body = "Causal masking across stocks — each stock attends to itself..."
```

#### `table` — data table

```toml
[[sections]]
id = "cli"
type = "table"
title = "CLI Reference"
icon = "info"

headers = ["Flag", "Default", "Description"]

[[sections.rows]]
cells = ["--mode", "train", "train or infer"]
```

#### `steps` — numbered instructions

```toml
[[sections]]
id = "how-it-works"
type = "steps"
title = "How It Works"
icon = "layers"

[[sections.items]]
title = "1. Data"
body = "Downloads OHLCV for all S&P 500 stocks via yfinance..."
```

#### `terms` — glossary

```toml
[[sections]]
id = "terms"
type = "terms"
title = "Terminology"
icon = "document"

[[sections.items]]
term = "MSE"
definition = "Mean Squared Error per stock..."
```

#### `code_block` — code snippet

```toml
[[sections]]
id = "quickstart"
type = "code_block"
title = "Quick Start"
icon = "play"
code = """
# 1. Install dependencies
uv sync

# 2. Train the model
uv run python main.py --mode train
"""
```

#### `stack` — tech badges

```toml
[[sections]]
id = "stack"
type = "stack"
title = "Tech Stack"
icon = "layers"

[[sections.items]]
name = "PyTorch"
description = "deep learning framework"
```

#### `text` — arbitrary text/HTML

```toml
[[sections]]
id = "intro"
type = "text"
title = "Introduction"
icon = "home"
body = "Some <strong>HTML</strong> content here."
```

### Icons

Named SVG icons available for sidebar nav entries. Each maps to an inline
Material Design SVG path in the template:

- `home` — house icon
- `grid` — 4-square grid
- `info` — alert/circle-i
- `chip` — CPU/chip
- `layers` — stacked layers
- `document` — file outline
- `play` — play triangle
- `gear` — cog/gear

## [S4] Generator Script (`genpage.py`)

A single Python script with:

```
usage: genpage.py [-h] [--input INPUT] [--output OUTPUT]

Generate project page from TOML data.

options:
  --input INPUT    TOML data file (default: projects/tradingbot.toml)
  --output OUTPUT  Output HTML file (default: docs/index.html)
```

**Behavior:**
1. Parse TOML with `tomllib` (stdlib, Python 3.11+) or `tomli` (fallback)
2. Validate required fields (project.name, sections)
3. Load `template.html.j2` from the same directory
4. Render with Jinja2 — passing the parsed TOML data
5. Write `index.html` to the output path

**Batch mode** (for CI): scan `projects/*.toml` and generate each into
`docs/<project-name>/index.html`.

Dependencies (minimal): `jinja2`, `tomli` (Python < 3.11).

## [S5] Jinja2 Template (`template.html.j2`)

A single template containing:

- The full Dracula CSS (`<style>...</style>`) — identical palette and layout
  to the existing pages (--bg, --panel, --purple, etc.)
- Sidebar rendered from project + brand data + auto-generated nav from sections
- A Jinja2 `{% macro %}` or `{% block %}` for each section type (features,
  table, steps, terms, code_block, stack, text)
- Mobile responsive rules (same breakpoint as existing pages)
- Footer with copyright and GitHub Pages credit

**Template structure:**

```html
<!doctype html>
<html lang="en">
<head>
  {# Meta from project data #}
  <title>{{ project.name }} | {{ project.tagline }}</title>
  <style>/* full Dracula CSS */</style>
</head>
<body>
  <aside class="sidebar">
    {# Brand from project.brand #}
    {# Nav auto-generated from sections #}
  </aside>
  <main class="main">
    {# hero — always from project top-level #}
    {% for section in sections %}
      {% if section.type == "features" %}
        {% include "_features.html" %}
      {% elif section.type == "table" %}
        ...
      {% endif %}
    {% endfor %}
  </main>
</body>
</html>
```

## [S6] GitHub Actions Workflow

File: `.github/workflows/deploy.yml`

Trigger: `push` to `main` when TOML files change (paths filter).

Steps:
1. Checkout repo
2. Setup Python (3.11+)
3. Install deps (`pip install jinja2`)
4. Run `genpage.py --batch` — scans `projects/*.toml`, generates into
   `docs/<project-name>/index.html`
5. Commit generated HTML back to the repo (or deploy to `gh-pages` branch)

If committing back: the Action uses `git diff` to check for changes before
committing to avoid infinite CI loops.

## [S7] Repo Layout

```
ProjectSite/
├── projects/                    # TOML data — one per project
│   ├── tradingbot.toml
│   └── ctf-llm.toml
├── docs/                        # Generated output (GitHub Pages root)
│   ├── index.html               # (optional) landing/redirect page
│   ├── TradingBot/
│   │   └── index.html
│   └── CTF-LLM/
│       └── index.html
├── genpage.py                   # Generator script
├── template.html.j2             # Jinja2 template
├── .github/workflows/
│   └── deploy.yml
└── pyproject.toml               # Project metadata + deps
```

The `docs/` directory is the GitHub Pages publish root. Each project's page
lives at `docs/<ProjectName>/index.html`, served at
`yuzu-octopus.github.io/<ProjectName>/`.

## [S8] Migration

1. Hand-write `projects/tradingbot.toml` from the existing
   `TradingBot/docs/index.html`
2. Hand-write `projects/ctf-llm.toml` from the existing
   `finetuning/docs/index.html`
3. Run `genpage.py --batch` to verify output matches (visual comparison)
4. Replace the hand-written HTML files with generated ones
5. Set up CI
6. Future projects: just add a `.toml` file
