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
| `logo_svg` | string | Inline SVG for the sidebar logo (64×64). Use CSS variables for theme support. |
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
<div class="callout callout-info"><strong>Note:</strong> This is a notice.</div>
"""
```

#### `type = "notice"` — themed callout box

Wraps body HTML in a themed callout. Supports `notice_type`: `info` (default), `warning`, `success`, `error`.

```toml
[[sections]]
id = "notice"
type = "notice"
title = "Hardware Note"
icon = "info"
notice_type = "warning"
body = """
<p>This requires a GPU with at least 8GB VRAM.</p>
"""
```

#### `type = "timeline"` — vertical connector timeline

Items appear as a vertical list with connector dots and a line on the left. Optional `date` field.

```toml
[[sections]]
id = "milestones"
type = "timeline"
title = "Milestones"
icon = "layers"

[[sections.items]]
title = "Phase 1"
body = "Initial implementation"
date = "Jan 2026"

[[sections.items]]
title = "Phase 2"
body = "Optimization"
```

#### `type = "workflow"` — horizontal scroll-snap cards

Items display as numbered cards in a horizontally scrollable row with CSS scroll-snap. Best for sequential steps or pipeline stages.

```toml
[[sections]]
id = "pipeline"
type = "workflow"
title = "Pipeline"
icon = "layers"

[[sections.items]]
title = "Data"
body = "Collect and clean data"

[[sections.items]]
title = "Train"
body = "Train the model"

[[sections.items]]
title = "Evaluate"
body = "Benchmark results"
```

#### `type = "code_block"` — pre-formatted code with syntax highlighting

```toml
[[sections]]
id = "quickstart"
type = "code_block"
title = "Quick Start"
icon = "play"
language = "python"
code = """
def hello():
    print("Hello, world!")
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
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/
          git diff --cached --quiet || git commit -m "ci: regenerate project page [skip ci]"
          git push https://${{ github.actor }}:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}.git HEAD:${{ github.ref_name }}
```

## Generator Files

| File | Purpose |
|------|---------|
| `genpage.py` | CLI entry point — reads TOML, renders template, writes HTML |
| `template.html.j2` | Jinja2 template — Dracula/Alucard theme, all section types |
| `pyproject.toml` | Python metadata, dependency on `jinja2` |

## Custom HTML Classes

When using `type = "custom"` or `type = "text"`, you can use these CSS classes.
All classes use `var(--*)` tokens — they work in both dark and light themes.

### Callouts

```html
<div class="callout callout-info">This is informational.</div>
<div class="callout callout-warning">This is a warning.</div>
<div class="callout callout-success">This succeeded.</div>
<div class="callout callout-error">This is an error.</div>
```

### Keyboard Shortcuts

```html
Press <kbd class="kbd">Ctrl</kbd> + <kbd class="kbd">K</kbd> to search.
```

### Dividers

```html
<hr class="divider">
```

### Styled HTML Elements

These elements are automatically styled in the Dracula/Alucard theme:

| Element | Style |
|---------|-------|
| `<strong>` | Purple text (bold) |
| `<em>` | Cyan italic |
| `<blockquote>` | Purple left border, muted background |
| `<figure>` + `<figcaption>` | Centered image with caption |
| `<details>` / `<summary>` | Collapsible section with purple summary |
| `<code>` | Green code on panel background |
| `<a>` | Cyan links, pink on hover |

### Available CSS Variables

Use these in inline styles for theme consistency:

`--bg` `--panel` `--fg` `--muted` `--purple` `--pink` `--cyan` `--green`
`--orange` `--red` `--yellow`

## Syntax Highlighting

Code blocks support syntax highlighting via Prism.js (loaded from CDN).
Add a `language` field to your `code_block` section:

```toml
[[sections]]
id = "quickstart"
type = "code_block"
title = "Quick Start"
icon = "play"
language = "python"
code = """
def hello():
    print("Hello, world!")
"""
```

Supported languages: Python, JavaScript, TypeScript, HTML, CSS, Bash, Shell Session, TOML, YAML, JSON, Rust, Go, C, C++, Java, Swift, Kotlin, Docker, Markdown, Diff, SQL, Lua, Ruby, PowerShell.

## Notes

- Add a **`.nojekyll`** file to the output directory (`docs/`) to prevent GitHub
  Pages' default Jekyll build from interfering with the generated HTML.
