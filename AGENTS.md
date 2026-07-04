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

# Template Features

- Copy button uses Material Symbols icons (content_copy → check/close)
- Workflow cards get hover lift (translateY(-2px))
- Cards have border-color transition on hover
- No box-shadow anywhere (flat design)
- Scroll-spy uses visibility Map for tall/custom sections
- OG image: Pillow renders text, cairosvg renders logo only
