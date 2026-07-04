#!/usr/bin/env python3
"""Generate project page HTML from TOML data + Jinja2 template."""

import argparse
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Dracula dark theme palette for OG image generation
_DRACULA = {
    "--bg": "#282a36", "--panel": "#44475a", "--fg": "#f8f8f2",
    "--muted": "#6272a4", "--purple": "#bd93f9", "--pink": "#ff79c6",
    "--cyan": "#8be9fd", "--green": "#50fa7b", "--orange": "#ffb86c",
    "--red": "#ff5555", "--yellow": "#f1fa8c",
}

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
_VALID_NOTICE_TYPES = {"info", "warning", "success", "error"}


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
        for j, row in enumerate(section["rows"]):
            if not isinstance(row, dict) or "cells" not in row or not isinstance(row["cells"], list):
                msg = f"sections[{index}].rows[{j}] requires 'cells' (list)"
                raise SystemExit(msg)
    elif st in _BODY_TYPES:
        if "body" not in section or not isinstance(section["body"], str):
            msg = f"sections[{index}] type='{st}' requires 'body' (string)"
            raise SystemExit(msg)
        if st == "notice" and "notice_type" in section and section["notice_type"] not in _VALID_NOTICE_TYPES:
                valid = ", ".join(sorted(_VALID_NOTICE_TYPES))
                msg = f"sections[{index}] notice_type must be one of: {valid}"
                raise SystemExit(msg)


def validate(data: dict) -> None:
    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        msg = f"Missing top-level keys: {', '.join(sorted(missing))}"
        raise SystemExit(msg)

    project = data.get("project", {})
    if not isinstance(project, dict):
        msg = "project must be a table"
        raise SystemExit(msg)
    for key in REQUIRED_PROJECT_KEYS:
        if key not in project:
            msg = f"Missing project.{key}"
            raise SystemExit(msg)

    brand = data.get("brand", {})
    if not isinstance(brand, dict):
        msg = "brand must be a table"
        raise SystemExit(msg)
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

        sid = section["id"]
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", sid):
            msg = f"sections[{i}] id must match [a-zA-Z0-9_-]+, got '{sid}'"
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


def _resolve_svg_vars(svg: str) -> str:
    """Replace var(--*) references in SVG with Dracula dark theme colors."""
    for var_name, color in _DRACULA.items():
        svg = svg.replace(f"var({var_name})", color)
    return svg


def _escape_xml(text: str) -> str:
    """Escape text for XML/SVG embedding."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _extract_logo_inner(logo_svg: str) -> tuple[str, str]:
    """Resolve colors and extract inner content + viewBox from a logo SVG.

    Returns (inner_svg_content, viewBox_string).
    """
    resolved = _resolve_svg_vars(logo_svg)
    resolved = re.sub(r"<\?xml[^>]*\?>", "", resolved).strip()
    vb_match = re.search(r'viewBox="([^"]*)"', resolved)
    viewBox = vb_match.group(1) if vb_match else "0 0 64 64"
    svg_start = re.search(r"<svg[^>]*>", resolved)
    if not svg_start:
        return resolved, viewBox
    inner_start = svg_start.end()
    svg_end = resolved.rfind("</svg>")
    inner = resolved[inner_start:svg_end].strip() if svg_end != -1 else resolved[inner_start:]
    return inner, viewBox


def generate_og_image(project: dict, output_path: Path) -> None:
    """Generate a 1200x630 OG preview PNG with Dracula theme (logo + title)."""
    try:
        import cairosvg
    except (ImportError, OSError):
        print("  ! cairosvg not available, skipping OG image")
        return

    name = project.get("name", "")
    tagline = project.get("tagline", "")
    subtitle = project.get("subtitle", "")
    logo_svg = project.get("logo_svg", "")

    logo_inner, viewBox = _extract_logo_inner(logo_svg)

    # Truncate long subtitle to avoid overflow
    if len(subtitle) > 120:
        subtitle = subtitle[:117] + "..."

    og_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#282a36" rx="16"/>
  <svg x="80" y="175" width="240" height="240" viewBox="{viewBox}">
{logo_inner}
  </svg>
  <text x="360" y="245" font-family="JetBrains Mono,monospace" font-size="52" font-weight="700" fill="#bd93f9">{_escape_xml(name)}</text>
  <text x="360" y="315" font-family="JetBrains Mono,monospace" font-size="28" fill="#f8f8f2">{_escape_xml(tagline)}</text>
  <text x="360" y="365" font-family="JetBrains Mono,monospace" font-size="20" fill="#6272a4">{_escape_xml(subtitle)}</text>
  <rect x="360" y="395" width="80" height="4" fill="#bd93f9" rx="2"/>
</svg>"""

    try:
        cairosvg.svg2png(
            bytestring=og_svg.encode("utf-8"),
            write_to=str(output_path),
            output_width=1200,
            output_height=630,
        )
    except Exception as e:
        print(f"  ! OG image generation failed: {e}")


def generate_one(input_path: Path, output_path: Path) -> None:
    data = load_toml(input_path)
    validate(data)

    # Ensure output directory exists before generating OG image
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate OG image before render so template can reference it
    og_path = output_path.parent / "og-image.png"
    generate_og_image(data.get("project", {}), og_path)
    # Set og_image for template (only if not already set by user)
    project = data.setdefault("project", {})
    if "og_image" not in project:
        project["og_image"] = "og-image.png"

    html = render(TEMPLATE, data)
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
