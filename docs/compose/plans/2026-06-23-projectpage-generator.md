# ProjectPage Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python + Jinja2 static site generator that reads project data from TOML files and produces self-contained GitHub Pages HTML.

**Architecture:** One Python script (`genpage.py`) reads TOML files via stdlib `tomllib` and renders a single Jinja2 template (`template.html.j2`) with the Dracula theme. A GitHub Action auto-generates on push. Each project gets one TOML file.

**Tech Stack:** Python 3.14, Jinja2, GitHub Actions

---

### Task 1: Project scaffolding and dependencies

**Covers:** (scaffolding — no spec section)

**Files:**
- Create: `pyproject.toml`
- Create: `projects/.gitkeep`
- Create: `docs/.gitkeep`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "projectpage"
version = "0.1.0"
description = "Static site generator for GitHub project pages"
requires-python = ">=3.11"
dependencies = [
    "jinja2>=3.0",
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.uv]
dev-dependencies = []
```

- [ ] **Step 2: Create placeholder directories**

```bash
mkdir -p projects docs
touch projects/.gitkeep docs/.gitkeep
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.venv/
.ruff_cache/
```

- [ ] **Step 4: Create AGENTS.md with build/check commands**

```markdown
# Commands

## Run generator (single project)
uv run python genpage.py --input projects/tradingbot.toml

## Run generator (batch mode — all projects)
uv run python genpage.py --batch

## Lint
ruff check genpage.py template.html.j2

## Type check
pyright genpage.py
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml projects/ docs/ .gitignore AGENTS.md
git commit -m "chore: scaffold project structure"
```

---

### Task 2: Create the Jinja2 template

**Covers:** [S3, S5]

**Files:**
- Create: `template.html.j2`

This is the largest file. It contains the full Dracula CSS (copied from the existing TradingBot/docs/index.html), inline SVG icons as macros, and rendered sections for each type.

- [ ] **Step 1: Write template.html.j2**

The template has these sections in order:

```
1. DOCTYPE + <head> with meta/project data
2. <style> block — full Dracula CSS (copy CSS lines 22-421 from TradingBot/docs/index.html)
3. <body> — sidebar with brand, auto-generated nav, footer
4. <main> — hero + section renderers
5. JavaScript for mobile toggle
```

Here's the complete template:

```jinja2
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ project.name }} | {{ project.tagline }}</title>
  <meta name="description" content="{{ project.description }}">
  <meta name="theme-color" content="#282a36">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{{ project.name }} | {{ project.tagline }}">
  <meta property="og:description" content="{{ project.description }}">
  <meta property="og:url" content="{{ project.page_url }}">
  {% if project.og_image %}
  <meta property="og:image" content="{{ project.page_url }}{{ project.og_image }}">
  {% endif %}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{ project.name }} | {{ project.tagline }}">
  <meta name="twitter:description" content="{{ project.description }}">
  {% if project.og_image %}
  <meta name="twitter:image" content="{{ project.page_url }}{{ project.og_image }}">
  {% endif %}
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{{ project.favicon_data | urlencode }}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    /* === FULL DRACULA CSS === */
    /* Copy the entire CSS block from TradingBot/docs/index.html lines 23-421.
       This includes: :root variables, reset, body, links, sidebar, main,
       hero, card grid, tables, code blocks, steps, terms, stack badges,
       scrollbar, skip-link, mobile toggle, and responsive rules.
       The class names and structure are unchanged from the existing pattern. */
  </style>
</head>
<body>

<button class="mobile-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open'); document.querySelector('.main').classList.toggle('shifted');" aria-label="Toggle mobile menu">&#9776;</button>
<a class="skip-link" href="#hero">Skip to content</a>

<aside class="sidebar" id="sidebar">
  <div class="sidebar-brand">
    <div class="logo">{{ project.logo_svg }}</div>
    <div class="name">{{ project.name }}</div>
    <div class="tagline">{{ brand.tagline }}</div>
  </div>
  <hr class="sidebar-divider">
  <ul class="sidebar-nav">
    <li><a href="#hero"><span class="icon">{{ icon("home") }}</span> Home</a></li>
    {% for section in sections %}
    <li><a href="#{{ section.id }}"><span class="icon">{{ icon(section.icon) }}</span> {{ section.title }}</a></li>
    {% endfor %}
  </ul>
  <hr class="sidebar-divider">
  <div class="sidebar-footer">
    <div>&copy; 2026 yuzu-octopus</div>
    <div>Powered by <a href="https://pages.github.com/" target="_blank" rel="noopener noreferrer">GitHub Pages</a></div>
  </div>
</aside>

<main class="main">

  {# === HERO === #}
  <section id="hero" class="hero">
    <div class="container">
      <h1>{{ project.name }}</h1>
      <p class="tagline">{{ project.tagline }}</p>
      <p class="subtitle">{{ project.subtitle }}</p>
      <div class="cta">
        <a href="{{ project.github_url }}" class="btn btn-primary">View on GitHub</a>
        {% if project.quickstart_url %}
        <a href="{{ project.quickstart_url }}" class="btn btn-outline">Quick Start</a>
        {% endif %}
      </div>
    </div>
  </section>

  {# === SECTIONS === #}
  {% for section in sections %}
  <section id="{{ section.id }}">
    <div class="container">
      <h2>{{ section.title }}</h2>

      {% if section.type == "features" %}
      <div class="grid">
        {% for item in section.items %}
        <div class="card">
          <h3>{{ item.title }}</h3>
          <p>{{ item.body }}</p>
        </div>
        {% endfor %}
      </div>

      {% elif section.type == "table" %}
      <table>
        <thead>
          <tr>{% for header in section.headers %}<th>{{ header }}</th>{% endfor %}</tr>
        </thead>
        <tbody>
          {% for row in section.rows %}
          <tr>{% for cell in row.cells %}<td>{{ cell }}</td>{% endfor %}</tr>
          {% endfor %}
        </tbody>
      </table>

      {% elif section.type == "steps" %}
      <ul class="steps">
        {% for item in section.items %}
        <li><strong>{{ item.title }}</strong> &mdash; {{ item.body }}</li>
        {% endfor %}
      </ul>

      {% elif section.type == "terms" %}
      <ul class="terms">
        {% for item in section.items %}
        <li><span class="term">{{ item.term }}</span> &mdash; {{ item.definition }}</li>
        {% endfor %}
      </ul>

      {% elif section.type == "code_block" %}
      <pre><code>{{ section.code | e }}</code></pre>

      {% elif section.type == "stack" %}
      <div class="stack">
        {% for item in section.items %}
        <span class="badge"><strong>{{ item.name }}</strong> &mdash; {{ item.description }}</span>
        {% endfor %}
      </div>

      {% elif section.type == "text" %}
      {{ section.body }}

      {% endif %}
    </div>
  </section>
  {% endfor %}

</main>

</body>
</html>
```

And the icon macro (included in the template, typically before `<!doctype>` or in the body — Jinja2 macros must be defined before use, so add this near the bottom of `<head>` or at the top of `<body>`):

```jinja2
{% macro icon(name) %}
{% if name == "home" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"/></svg>
{% elif name == "grid" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M3,3H11V11H3V3M3,13H11V21H3V13M13,3H21V11H13V3M13,13H21V21H13V13Z"/></svg>
{% elif name == "info" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/></svg>
{% elif name == "chip" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M17,7A2,2 0 0,1 19,9V17A2,2 0 0,1 17,19H7A2,2 0 0,1 5,17V9A2,2 0 0,1 7,7H17M7,9V17H17V9H7M12,2A2,2 0 0,1 14,4V6H15V4A3,3 0 0,0 12,1A3,3 0 0,0 9,4V6H10V4A2,2 0 0,1 12,2Z"/></svg>
{% elif name == "layers" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M12,16L19.36,10.27L21,9L12,3L3,9L4.63,10.27M12,18.54L4.62,12.81L3,14.07L12,20L21,14.07L19.37,12.8L12,18.54Z"/></svg>
{% elif name == "document" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M10,19L12,17L14,19L15,18L13,16L15,14L14,13L12,15L10,13L9,14L11,16L9,18L10,19Z"/></svg>
{% elif name == "play" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M8,5.14V19.14L19,12.14L8,5.14Z"/></svg>
{% elif name == "gear" %}
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M3,17V19H9V17H3M3,5V7H13V5H3M13,21V19H21V17H13V15H11V21H13M7,9V11H3V13H7V15H9V9H7M21,13V11H11V13H21M15,9H17V7H21V5H17V3H15V9Z"/></svg>
{% endif %}
{% endmacro %}
```

- [ ] **Step 2: Commit**

```bash
git add template.html.j2
git commit -m "feat: add Jinja2 template with Dracula theme and all section types"
```

---

### Task 3: Create the generator script

**Covers:** [S4]

**Files:**
- Create: `genpage.py`

- [ ] **Step 1: Write genpage.py**

```python
#!/usr/bin/env python3
"""Generate project page HTML from TOML data + Jinja2 template."""

import argparse
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


HERE = Path(__file__).parent
TEMPLATE = "template.html.j2"
DEFAULT_INPUT = HERE / "projects"
DEFAULT_OUTPUT = HERE / "docs"


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def render(template_name: str, data: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(HERE),
        autoescape=False,
    )
    template = env.get_template(template_name)
    return template.render(**data)


def generate_one(input_path: Path, output_path: Path) -> None:
    data = load_toml(input_path)
    html = render(TEMPLATE, data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✓ {output_path}")


def batch(input_dir: Path, output_dir: Path) -> None:
    toml_files = sorted(input_dir.glob("*.toml"))
    if not toml_files:
        print("No .toml files found in", input_dir)
        return
    for toml_path in toml_files:
        project_dir = output_dir / toml_path.stem
        output_path = project_dir / "index.html"
        generate_one(toml_path, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate project page from TOML")
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="TOML file (single mode) or directory (batch mode)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output HTML path (single mode) or directory (batch mode)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: process all .toml files in input directory",
    )
    args = parser.parse_args()

    if args.batch:
        input_dir = Path(args.input) if args.input else DEFAULT_INPUT
        output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT
        batch(input_dir, output_dir)
    else:
        input_path = Path(args.input) if args.input else DEFAULT_INPUT / "tradingbot.toml"
        output_path = Path(args.output) if args.output else DEFAULT_OUTPUT / "index.html"
        generate_one(input_path, output_path)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add genpage.py
git commit -m "feat: add genpage.py CLI entry point"
```

---

### Task 4: Create TOML data files for existing projects

**Covers:** [S3]

**Files:**
- Create: `projects/tradingbot.toml`
- Create: `projects/ctf-llm.toml`

- [ ] **Step 1: Create projects/tradingbot.toml**

Extract from `/Users/yuzu/Documents/projects/TradingBot/docs/index.html`:

```toml
[project]
name = "TradingBot"
tagline = "Multi-stock ML trading bot"
subtitle = "All S&P 500 stocks pass through a single decoder-only Transformer in one forward pass. Learns inter-stock relationships — outputs per-stock buy/sell confidence scores from -1 to +1."
description = "Multi-stock ML trading bot using a decoder-only Transformer with RankGLU output and market-guided gating. Learns inter-stock relationships across the S&P 500."
github_url = "https://github.com/yuzu-octopus/Simple-Trader"
page_url = "https://yuzu-octopus.github.io/TradingBot/"
quickstart_url = "#quickstart"
logo_svg = """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" rx="12" fill="#44475a"/><polyline points="12,46 20,30 28,38 36,20 44,32 52,18" fill="none" stroke="#50fa7b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="52" cy="18" r="3" fill="#bd93f9"/></svg>"""
favicon_data = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='10' fill='%23282a36'/><path d='M8 48h48v4H8z' fill='%236272a4'/><polyline points='16,44 24,28 32,36 40,18 48,30' fill='none' stroke='%2350fa7b' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/><circle cx='48' cy='30' r='3' fill='%23bd93f9'/></svg>"""

[brand]
tagline = "ML · S&P 500 · Transformer"

[[sections]]
id = "features"
type = "features"
title = "Features"
icon = "grid"

[[sections.items]]
title = "Decoder-Only Transformer"
body = "Causal masking across stocks — each stock attends to itself and preceding stocks. Research shows decoder-only beats encoder-only for stock prediction. ~478K parameters."

[[sections.items]]
title = "Multi-Window Features"
body = "30 technical indicators (SMA, RSI, MACD, Bollinger, volatility, returns, drawdown) computed per-window at 1y, 1m, 1w, 1d lookbacks — 120 features per stock per day."

[[sections.items]]
title = "Portfolio-Aware Training"
body = "From MSE to MSRR (direct Sharpe optimization), margin ranking, and ListNet losses. MSRR optimizes portfolio weights, not individual stock errors."

[[sections.items]]
title = "Market-Guided Gating"
body = "SPY state (returns, volatility, volume) rescales features before the transformer. The model adapts to bull/bear/high-volatility regimes automatically."

[[sections]]
id = "cli"
type = "table"
title = "CLI Reference"
icon = "info"
headers = ["Flag", "Default", "Description"]

[[sections.rows]]
cells = ["--mode", "train", "train or infer"]

[[sections.rows]]
cells = ["--loss", "mse", "mse, msrr, margin, listnet"]

[[sections.rows]]
cells = ["--seeds", "1", "Ensemble size (multiple random seeds, average predictions)"]

[[sections.rows]]
cells = ["--grad-accum", "1", "Gradient accumulation steps (simulates larger batch)"]

[[sections.rows]]
cells = ["--resume", "off", "Resume training from last checkpoint"]

[[sections.rows]]
cells = ["--walk-forward", "off", "Sliding chronological train/val/test windows"]

[[sections.rows]]
cells = ["--force-features", "off", "Rebuild feature matrix from scratch"]

[[sections.rows]]
cells = ["--model <path>", "—", "Load model from data/models/<path>/best.pt"]

[[sections]]
id = "architecture"
type = "table"
title = "Model Architecture"
icon = "chip"
headers = ["Property", "Value"]

[[sections.rows]]
cells = ["Parameters", "~478K"]

[[sections.rows]]
cells = ["Architecture", "Decoder-only Transformer (causal), 3 layers, 4 heads"]

[[sections.rows]]
cells = ["Output head", "RankGLU (residual bottleneck GLU)"]

[[sections.rows]]
cells = ["Conditioning", "MarketGate (SPY-based gating, 5 features)"]

[[sections.rows]]
cells = ["d_model", "128"]

[[sections.rows]]
cells = ["d_ff", "256"]

[[sections.rows]]
cells = ["Dropout", "0.1"]

[[sections.rows]]
cells = ["Activation", "GELU"]

[[sections.rows]]
cells = ["Optimizer", "AdamW (1e-4, weight decay 1e-4)"]

[[sections.rows]]
cells = ["Input features", "120 per stock (30 indicators × 4 windows)"]

[[sections.rows]]
cells = ["Output", "tanh, scores in [-1, +1]"]

[[sections]]
id = "how-it-works"
type = "steps"
title = "How It Works"
icon = "layers"

[[sections.items]]
title = "1. Data"
body = "Downloads OHLCV for all S&P 500 stocks via yfinance (~10 years), cached to CSV. Tickers fetched live from Wikipedia."

[[sections.items]]
title = "2. Features"
body = "Builds parallel feature matrix: 30 technical indicators per stock per date at 4 lookback windows (1y, 1m, 1w, 1d). SMA, RSI, MACD, Bollinger Bands, volatility, returns, max drawdown, volume ratio."

[[sections.items]]
title = "3. Model"
body = "Decoder-only Transformer with causal masking. Each stock attends to itself and preceding stocks. MarketGate rescales features by SPY state. RankGLU output head produces confidence scores."

[[sections.items]]
title = "4. Training"
body = "Supervised regression on next-day cross-sectional z-score returns. Supports MSE, MSRR (direct Sharpe optimization), margin ranking, and ListNet losses. Mixed precision, gradient accumulation, cosine annealing LR, early stopping."

[[sections.items]]
title = "5. Threshold"
body = "Post-training calibration via isotonic regression. Dual-threshold search maximizes Sharpe ratio — not just return. Produces separate buy and sell thresholds."

[[sections]]
id = "terms"
type = "terms"
title = "Terminology"
icon = "document"

[[sections.items]]
term = "MSE"
definition = "Mean Squared Error per stock. Simple regression baseline: loss = Σ(predicted - actual)²."

[[sections.items]]
term = "MSRR"
definition = "Max Sharpe Ratio Regression. Loss = (1 - portfolio_return)². Directly optimizes portfolio Sharpe. Noisier but higher ceiling."

[[sections.items]]
term = "Margin / ListNet"
definition = "Pairwise ranking loss (margin: correct relative order) and listwise ranking loss (ListNet: top-1 probability distribution). Good for ranking tasks."

[[sections.items]]
term = "Mixed Precision"
definition = "float16 for compute-heavy ops, float32 for critical ops. 30-40% speedup on CUDA and MPS with no accuracy loss."

[[sections.items]]
term = "RankGLU"
definition = "Residual bottleneck GLU output head: direct linear path + gated nonlinear branch. Preserves ranking while adding controlled interactions."

[[sections.items]]
term = "MarketGate"
definition = "SPY market features (returns, volatility, volume ratio) rescale stock features before the transformer. Regime-adaptive conditioning from MASTER (AAAI 2024)."

[[sections.items]]
term = "Walk-Forward"
definition = "Multiple chronological train/val/test folds evaluated sequentially. Gold standard for financial ML — captures regime changes."

[[sections.items]]
term = "Z-Score Norm"
definition = "Training targets normalized per-day: mean=0, std=1 after winsorizing extremes. Standard in ranking-aware models."

[[sections]]
id = "quickstart"
type = "code_block"
title = "Quick Start"
icon = "play"
code = """
# 1. Install dependencies
uv sync

# 2. Train the model (MSE baseline)
uv run python main.py --mode train

# 3. Train with MSRR loss (gradient accumulation)
uv run python main.py --mode train --loss msrr --grad-accum 4

# 4. Ensemble training (5 seeds)
uv run python main.py --mode train --loss msrr --seeds 5 --grad-accum 4

# 5. Walk-forward validation
uv run python main.py --mode train --walk-forward

# 6. Get today's trading signals
uv run python main.py --mode infer"""

[[sections]]
id = "stack"
type = "stack"
title = "Tech Stack"
icon = "layers"

[[sections.items]]
name = "PyTorch"
description = "deep learning framework"

[[sections.items]]
name = "numpy"
description = "numerical computing"

[[sections.items]]
name = "pandas"
description = "data manipulation"

[[sections.items]]
name = "scikit-learn"
description = "preprocessing + calibration"

[[sections.items]]
name = "yfinance"
description = "Yahoo Finance API"

[[sections.items]]
name = "unlockedpd"
description = "accelerated rolling ops"

[[sections.items]]
name = "tqdm"
description = "progress bars"

[[sections.items]]
name = "uv"
description = "Python package manager"
```

- [ ] **Step 2: Create projects/ctf-llm.toml**

Extract from `/Users/yuzu/Documents/projects/finetuning/docs/index.html`:

```toml
[project]
name = "CTF-LLM"
tagline = "Fine-tune LLMs to solve CTF challenges"
subtitle = "End-to-end pipeline for cybersecurity CTF and competitive programming using Unsloth + QLoRA on Google Colab's free T4 GPU."
description = "End-to-end pipeline for fine-tuning open-source LLMs on CTF challenges using Unsloth and QLoRA."
github_url = "https://github.com/yuzu-octopus/CTF-LLM"
page_url = "https://yuzu-octopus.github.io/CTF-LLM/"
quickstart_url = "#quickstart"
logo_svg = """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><path d="M16 8v48" stroke="#6272a4" stroke-width="2.5" stroke-linecap="round"/><path d="M16 10h32l-8 10 8 10H16z" fill="#bd93f9"/></svg>"""
favicon_data = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='10' fill='%23282a36'/><path d='M16 8v48' stroke='%236272a4' stroke-width='2'/><path d='M16 10h32l-8 10 8 10H16z' fill='%23bd93f9'/></svg>"""
og_image = "og-image.png"

[brand]
tagline = "fine-tune · CTF · qLoRA"

[[sections]]
id = "features"
type = "features"
title = "Features"
icon = "grid"

[[sections.items]]
title = "End-to-end Pipeline"
body = "Scrapes CTF writeups from 13 GitHub repos, downloads curated HuggingFace datasets, processes to ChatML, trains with Unsloth QLoRA, evaluates on a 210-question benchmark."

[[sections.items]]
title = "4 Models Supported"
body = "Gemma 4 E4B, Gemma 4 12B, Qwen 3.5 9B, Qwen 3.5 4B — all running 4-bit QLoRA on a free T4 GPU (16GB VRAM)."

[[sections.items]]
title = "210-Question Benchmark"
body = "Curated evaluation set across 4 categories (pwn, rev, crypto, web) and 3 difficulty levels with Wilson 95% CI and McNemar's test."

[[sections.items]]
title = "Colab-Ready"
body = "Single finetune.sh handles session creation, dependency install, file upload, training, and model download."

[[sections]]
id = "models"
type = "table"
title = "Supported Models"
icon = "chip"
headers = ["Model", "Parameters", "Fast Mode (LoRA r)", "Quality Mode (LoRA r)", "VRAM (T4)", "Status"]

[[sections.rows]]
cells = ["Gemma 4 E4B", "~4.5B", "8", "32", "~10GB", "Comfortable"]

[[sections.rows]]
cells = ["Gemma 4 12B", "~12B", "8", "32", "~11GB", "Tight"]

[[sections.rows]]
cells = ["Qwen 3.5 9B", "~9B", "8", "32", "~12GB", "Comfortable"]

[[sections.rows]]
cells = ["Qwen 3.5 4B", "~4B", "8", "16", "~8GB", "Comfortable"]

[[sections]]
id = "modes"
type = "table"
title = "Training Modes"
icon = "gear"
headers = ["Parameter", "Fast (~30 min)", "Quality (~50-70 min)"]

[[sections.rows]]
cells = ["Dataset", "~500 examples", "2500+ examples"]

[[sections.rows]]
cells = ["LoRA rank", "8", "32"]

[[sections.rows]]
cells = ["Max seq length", "2048", "4096"]

[[sections.rows]]
cells = ["Epochs", "1", "2"]

[[sections]]
id = "benchmark"
type = "text"
title = "Benchmark Stats"
icon = "layers"
body = """
<p style="margin-bottom: 20px;"><strong style="color: var(--purple);">210 questions</strong> across 4 categories and 3 difficulty levels.</p>
<ul class="stats">
  <li><strong>Categories</strong> &mdash; pwn (57), rev (50), crypto (50), web (53)</li>
  <li><strong>Difficulties</strong> &mdash; easy (72), medium (79), hard (59)</li>
  <li><strong>Task types</strong> &mdash; flag_extraction, multiple_choice, code_generation, vulnerability_identification, patch_generation, exploit_trace</li>
  <li><strong>Statistical rigor</strong> &mdash; Wilson 95% CI, McNemar's test, contamination check, cheating detection</li>
</ul>
"""

[[sections]]
id = "quickstart"
type = "code_block"
title = "Quick Start"
icon = "play"
code = """
# 1. Install dependencies
uv sync

# 2. Run full pipeline (build data + train)
./finetune.sh gemma4 --all

# 3. Evaluate
./finetune.sh gemma4 --eval"""

[[sections]]
id = "stack"
type = "stack"
title = "Tech Stack"
icon = "layers"

[[sections.items]]
name = "Unsloth"
description = "QLoRA fine-tuning"

[[sections.items]]
name = "PyTorch"
description = "deep learning"

[[sections.items]]
name = "HuggingFace"
description = "datasets + models"

[[sections.items]]
name = "Google Colab"
description = "free T4 GPU"

[[sections.items]]
name = "uv"
description = "Python package manager"
```

- [ ] **Step 3: Commit**

```bash
git add projects/tradingbot.toml projects/ctf-llm.toml
git commit -m "feat: add TOML data for TradingBot and CTF-LLM"
```

---

### Task 5: Create GitHub Actions workflow

**Covers:** [S6]

**Files:**
- Create: `.github/workflows/deploy.yml`

- [ ] **Step 1: Create deploy.yml**

```yaml
name: Deploy project pages

on:
  push:
    branches: [main]
    paths:
      - "projects/**"
      - "template.html.j2"
      - "genpage.py"
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install jinja2
      - name: Generate project pages
        run: python genpage.py --batch
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

- [ ] **Step 2: Create .github/workflows/ dir**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: add GitHub Actions workflow for auto-deploy"
```

---

### Task 6: Generate and verify output

**Covers:** [S8]

- [ ] **Step 1: Install dependencies and generate**

```bash
cd /Users/yuzu/Documents/Projects/ProjectSite
uv sync
uv run python genpage.py --batch
```

Expected output:
```
  ✓ docs/TradingBot/index.html
  ✓ docs/CTF-LLM/index.html
```

- [ ] **Step 2: Verify TradingBot output**

```bash
python3 -c "
from pathlib import Path
html = Path('docs/TradingBot/index.html').read_text()
assert 'TradingBot' in html
assert 'Decoder-Only Transformer' in html
assert 'CLI Reference' in html
assert 'Model Architecture' in html
assert 'How It Works' in html
assert 'Quick Start' in html
assert 'Tech Stack' in html
print('TradingBot: all sections present')
"
```

- [ ] **Step 3: Verify CTF-LLM output**

```bash
python3 -c "
from pathlib import Path
html = Path('docs/CTF-LLM/index.html').read_text()
assert 'CTF-LLM' in html
assert 'End-to-end Pipeline' in html
assert 'Supported Models' in html
assert 'Training Modes' in html
assert 'Benchmark Stats' in html
assert 'Quick Start' in html
assert 'Tech Stack' in html
print('CTF-LLM: all sections present')
"
```

- [ ] **Step 4: Open in browser to visually verify**

```bash
open docs/TradingBot/index.html
# Visually confirm: sidebar, hero, features, table, steps, terms, code, stack
```

```bash
open docs/CTF-LLM/index.html
# Visually confirm: sidebar, hero, features, tables, text section, code, stack
```

- [ ] **Step 5: Compare with original pages**

Open side by side:
- `/Users/yuzu/Documents/projects/TradingBot/docs/index.html`
- `/Users/yuzu/Documents/projects/finetuning/docs/index.html`

Verify: same layout, same fonts, same colors, same content, same mobile responsive behavior.

- [ ] **Step 6: Commit generated output and migration plan**

```bash
git add docs/TradingBot/index.html docs/CTF-LLM/index.html
git commit -m "feat: generate initial project pages"
```
