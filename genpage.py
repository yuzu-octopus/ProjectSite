#!/usr/bin/env python3
"""Generate project page HTML from TOML data + Jinja2 template."""

import argparse
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).parent
TEMPLATE = "template.html.j2"


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


KNOWN_SECTION_TYPES = {
    "features", "table", "steps", "terms", "code_block", "stack", "text", "links", "custom",
    "notice", "timeline", "workflow",
}

REQUIRED_TOP_KEYS = {"project", "brand", "sections"}
REQUIRED_PROJECT_KEYS = {
    "name", "tagline", "subtitle", "description",
    "github_url", "page_url", "logo_svg",
}


_ITEMS_TYPES = {"features", "steps", "stack", "links", "timeline", "workflow", "terms"}
_BODY_TYPES = {"text", "custom", "notice"}


_ITEM_KEYS = {
    "features": ("title", "body"),
    "steps": ("title", "body"),
    "stack": ("name", "description"),
    "links": ("title", "url", "description"),
    "timeline": ("title", "body"),
    "workflow": ("title", "body"),
    "terms": ("term", "definition"),
}


def _validate_section_fields(section: dict, index: int, st: str) -> None:
    if st in _ITEMS_TYPES:
        items = section.get("items")
        if not isinstance(items, list):
            msg = f"sections[{index}] type='{st}' requires 'items' to be a list"
            raise SystemExit(msg)
        required = _ITEM_KEYS.get(st, ())
        for j, item in enumerate(items):
            if not isinstance(item, dict):
                msg = f"sections[{index}].items[{j}] must be a dict"
                raise SystemExit(msg)
            for key in required:
                if key not in item:
                    msg = f"sections[{index}].items[{j}] type='{st}' requires '{key}'"
                    raise SystemExit(msg)
    elif st == "code_block":
        if "code" not in section or not isinstance(section["code"], str):
            msg = f"sections[{index}] type='code_block' requires 'code' (string)"
            raise SystemExit(msg)
    elif st == "table":
        if "headers" not in section or not isinstance(section["headers"], list):
            msg = f"sections[{index}] type='table' requires 'headers' (list)"
            raise SystemExit(msg)
        if "rows" not in section or not isinstance(section["rows"], list):
            msg = f"sections[{index}] type='table' requires 'rows' (list)"
            raise SystemExit(msg)
    elif st in _BODY_TYPES:
        if "body" not in section or not isinstance(section["body"], str):
            msg = f"sections[{index}] type='{st}' requires 'body' (string)"
            raise SystemExit(msg)


def validate(data: dict) -> None:
    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        msg = f"Missing top-level keys: {', '.join(sorted(missing))}"
        raise SystemExit(msg)

    project = data.get("project", {})
    for key in REQUIRED_PROJECT_KEYS:
        if key not in project:
            msg = f"Missing project.{key}"
            raise SystemExit(msg)

    brand = data.get("brand", {})
    if "tagline" not in brand:
        msg = "Missing brand.tagline"
        raise SystemExit(msg)

    sections = data.get("sections", [])
    if not isinstance(sections, list) or not sections:
        msg = "sections must be a non-empty array"
        raise SystemExit(msg)

    for i, section in enumerate(sections):
        for key in ("id", "type", "icon"):
            if key not in section:
                msg = f"sections[{i}] missing required field '{key}'"
                raise SystemExit(msg)

        st = section["type"]
        if st not in KNOWN_SECTION_TYPES:
            valid = ", ".join(sorted(KNOWN_SECTION_TYPES))
            msg = f"sections[{i}] unknown type '{st}'. Valid types: {valid}"
            raise SystemExit(msg)

        _validate_section_fields(section, i, st)


def render(template_name: str, data: dict) -> str:
    data["current_year"] = datetime.now(UTC).year
    env = Environment(
        loader=FileSystemLoader(HERE),
        autoescape=False,  # noqa: S701 — trusted TOML input, static site output
    )
    template = env.get_template(template_name)
    return template.render(**data)


def generate_one(input_path: Path, output_path: Path) -> None:
    data = load_toml(input_path)
    validate(data)
    html = render(TEMPLATE, data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"  \u2713 {output_path}")


def batch(input_dir: Path, output_dir: Path) -> None:
    toml_files = sorted(input_dir.glob("*.toml"))
    if not toml_files:
        print("No .toml files found in", input_dir)
        return
    for toml_path in toml_files:
        project_dir = output_dir / toml_path.stem
        output_path = project_dir / "index.html"
        try:
            generate_one(toml_path, output_path)
        except SystemExit as e:
            print(f"  ! {toml_path.name}: {e.code or 'error'}")
        except Exception as e:
            print(f"  ! {toml_path.name}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate project page from TOML")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="TOML file (single mode) or directory (batch mode)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output HTML path (single mode) or directory (batch mode)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: process all .toml files in input directory",
    )
    args = parser.parse_args()

    if args.batch:
        batch(Path(args.input), Path(args.output))
    else:
        generate_one(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
