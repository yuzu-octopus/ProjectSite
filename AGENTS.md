# Commands

## Run generator (single project)
uv run python genpage.py --input projects/tradingbot.toml

## Run generator (batch mode — all projects)
uv run python genpage.py --batch

## Lint
ruff check genpage.py template.html.j2

## Type check
pyright genpage.py
