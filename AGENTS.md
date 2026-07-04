# Commands

## Run generator (single project)
uv run python genpage.py --input path/to/project.toml --output docs/index.html

## Run generator (batch mode — all .toml files in a directory)
uv run python genpage.py --input projects/ --output docs/ --batch

## Lint
ruff check genpage.py

## Type check
pyright genpage.py

## Test
uv run pytest tests/ -v

## Test
uv run pytest tests/ -v
