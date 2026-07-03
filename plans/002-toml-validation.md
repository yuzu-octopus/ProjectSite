# Plan 002: Add TOML schema validation to genpage.py

**Finding:** #2 — `genpage.py` passes raw TOML dict to Jinja2 with no validation. Missing required fields cause opaque `UndefinedError` with no actionable message.

**Stamp:** f9687b2

## Why

A user types `genpage.py --input project.toml --output docs/index.html` and gets:
```
jinja2.exceptions.Undefined: 'project' is undefined
```
No hint about what's wrong or how to fix it. A 5-line validation gives a clear error.

## Scope

**In scope:**
- `genpage.py` — add validation in `generate_one()` before `render()`

**Out of scope:**
- `template.html.j2` — no changes
- Full JSON Schema / TOML schema validation — YAGNI, just check the 3 required top-level keys

## Steps

1. Read `genpage.py`
2. Add a validation function after `load_toml()`:

```python
REQUIRED_TOP_KEYS = {"project", "brand", "sections"}
REQUIRED_PROJECT_KEYS = {"name", "tagline", "subtitle", "description", "github_url", "page_url", "logo_svg", "favicon_data"}


def validate(data: dict) -> None:
    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        raise SystemExit(f"Missing top-level keys: {', '.join(sorted(missing))}")
    for key in REQUIRED_PROJECT_KEYS:
        if key not in data["project"]:
            raise SystemExit(f"Missing project.{key}")
    if not isinstance(data["sections"], list) or not data["sections"]:
        raise SystemExit("sections must be a non-empty array")
```

3. Call `validate(data)` in `generate_one()` before `render()`:

```python
def generate_one(input_path: Path, output_path: Path) -> None:
    data = load_toml(input_path)
    validate(data)
    html = render(TEMPLATE, data)
    ...
```

4. Run `ruff check genpage.py` — confirm no lint errors
5. Run the generator against `project.toml` — confirm it still works
6. Test with a broken TOML (missing `project.name`) — confirm clear error message

## Verification

- `ruff check genpage.py` — passes
- `uv run python genpage.py --input project.toml --output /tmp/test.html` — generates successfully
- `echo '[project]' > /tmp/bad.toml && uv run python genpage.py --input /tmp/bad.toml --output /tmp/out.html` — exits with clear error message mentioning missing keys
