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
        autoescape=False,  # noqa: S701 — trusted TOML input, static site output
    )
    template = env.get_template(template_name)
    return template.render(**data)


def generate_one(input_path: Path, output_path: Path) -> None:
    data = load_toml(input_path)
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
