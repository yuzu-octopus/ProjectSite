# ProjectPage Generator

Generates self-contained GitHub Pages HTML for project showcase pages from
TOML data + a Jinja2 template. The template uses a Dracula dark theme (default)
with an Alucard light theme, JetBrains Mono font, sidebar navigation,
responsive layout, and scroll-reveal animations.

## Usage

```bash
# Single project
uv run python genpage.py --input path/to/project.toml --output docs/index.html

# Batch: all .toml files in a directory → output/<name>/index.html each
uv run python genpage.py --input projects/ --output docs/ --batch
```

## TOML Schema

Each `.toml` file describes one project page. The file has two top-level
tables and an array of sections.

### `[project]` — required

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Page title and hero heading |
| `tagline` | string | Short descriptor shown in hero |
| `subtitle` | string | Longer explanation in hero (1-2 sentences) |
| `description` | string | Meta description for SEO |
| `github_url` | string | Link to the GitHub repo |
| `page_url` | string | URL where the page will be served |
| `quickstart_url` | string | Optional — link for the "Quick Start" CTA button (usually `"#quickstart"`) |
| `logo_svg` | string | Inline SVG for the sidebar logo (64×64) |
| `favicon_data` | string | Inline SVG for the browser favicon |
| `og_image` | string | Optional — filename of an OG image (e.g. `"og-image.png"`) |

### `[brand]` — required

| Field | Type | Description |
|-------|------|-------------|
| `tagline` | string | Short text shown below the project name in the sidebar |

### `[[sections]]` — array, at least one

Each section becomes a sidebar nav entry and a content block. Order in the
TOML determines page flow. Required fields across all sections:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | URL anchor and sidebar link target (e.g. `"features"`) |
| `type` | string | One of the section types below |
| `title` | string | Section heading and sidebar label |
| `icon` | string | Named icon for sidebar — see [Icons](#icons) |

Additional fields depend on `type`:

#### `type = "features"` — card grid

```toml
[[sections]]
id = "features"
type = "features"
title = "Features"
icon = "grid"

[[sections.items]]
title = "Feature Name"
body = "Description of the feature."
```

#### `type = "table"` — data table

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

#### `type = "steps"` — numbered list

```toml
[[sections]]
id = "how-it-works"
type = "steps"
title = "How It Works"
icon = "layers"

[[sections.items]]
title = "1. Data"
body = "Downloads OHLCV from yfinance…"
```

#### `type = "terms"` — glossary

```toml
[[sections]]
id = "terms"
type = "terms"
title = "Terminology"
icon = "document"

[[sections.items]]
term = "MSE"
definition = "Mean Squared Error per stock…"
```

#### `type = "code_block"` — pre-formatted code

```toml
[[sections]]
id = "quickstart"
type = "code_block"
title = "Quick Start"
icon = "play"
code = """
# Install dependencies
uv sync

# Train
uv run python main.py
"""
```

#### `type = "stack"` — tech badge grid

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

#### `type = "text"` — raw HTML block

```toml
[[sections]]
id = "intro"
type = "text"
title = "Introduction"
icon = "home"
body = """
<p>Some <strong>HTML</strong> content here.</p>
"""
```

### Icons

Named SVG icons available for sidebar nav entries:

`home` `grid` `info` `chip` `layers` `document` `play` `gear` `link`

#### `type = "links"` — external resource cards

```toml
[[sections]]
id = "links"
type = "links"
title = "Related"
icon = "link"

[[sections.items]]
title = "Dracula Theme"
url = "https://draculatheme.com"
description = "Official Dracula color palette"
```

#### `type = "custom"` — injectable HTML block

```toml
[[sections]]
id = "notice"
type = "custom"
body = """
<div style="padding: 1rem; border-left: 3px solid var(--cyan);">
  <strong>Custom content</strong> goes here.
</div>
"""
```

## CI Setup (per project)

Each project repo runs the generator in CI and commits the result to its
`docs/` folder. Example GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy project page

permissions:
  contents: write

on:
  push:
    branches: [main]
    paths:
      - "project.toml"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Checkout generator
        uses: actions/checkout@v4
        with:
          repository: yuzu-octopus/ProjectSite
          path: generator
          persist-credentials: false
      - name: Generate page
        run: |
          pip install jinja2
          python generator/genpage.py --input project.toml --output docs/index.html
      - name: Commit generated page
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add docs/
          git diff --cached --quiet || git commit -m "ci: regenerate project page [skip ci]"
          git push
```

## Generator Files

| File | Purpose |
|------|---------|
| `genpage.py` | CLI entry point — reads TOML, renders template, writes HTML |
| `template.html.j2` | Jinja2 template — Dracula theme, all section types |
| `pyproject.toml` | Python metadata, dependency on `jinja2` |

## Notes

- Add a **`.nojekyll`** file to the output directory (`docs/`) to prevent GitHub
  Pages' default Jekyll build from interfering with the generated HTML.
