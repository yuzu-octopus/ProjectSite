#!/usr/bin/env python3
"""Generate project page HTML from TOML data + Jinja2 template."""

import argparse
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).parent
TEMPLATE = "template.html.j2"


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


REQUIRED_TOP_KEYS = {"project", "brand", "sections"}
REQUIRED_PROJECT_KEYS = {
    "name", "tagline", "subtitle", "description",
    "github_url", "page_url", "logo_svg", "favicon_dark", "favicon_light",
}


def validate(data: dict) -> None:
    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        msg = f"Missing top-level keys: {', '.join(sorted(missing))}"
        raise SystemExit(msg)
    for key in REQUIRED_PROJECT_KEYS:
        if key not in data["project"]:
            msg = f"Missing project.{key}"
            raise SystemExit(msg)
    if not isinstance(data["sections"], list) or not data["sections"]:
        msg = "sections must be a non-empty array"
        raise SystemExit(msg)


def render(template_name: str, data: dict) -> str:
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
        generate_one(toml_path, output_path)


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
