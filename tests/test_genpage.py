"""Tests for genpage.py validation and generation."""

import re
import textwrap
from pathlib import Path

import pytest

from genpage import (
    KNOWN_SECTION_TYPES,
    TEMPLATE,
    _validate_section_fields,
    batch,
    generate_one,
    validate,
)

HERE = Path(__file__).parent.parent


def _make_data(**overrides: object):
    """Minimal valid TOML data dict."""
    data = {
        "project": {
            "name": "Test",
            "tagline": "Test tagline",
            "subtitle": "Test subtitle",
            "description": "Test description",
            "github_url": "https://github.com/test/test",
            "page_url": "https://test.github.io/test/",
            "logo_svg": '<svg viewBox="0 0 64 64"></svg>',
        },
        "brand": {"tagline": "Test brand"},
        "sections": [
            {
                "id": "features",
                "type": "features",
                "icon": "grid",
                "title": "Features",
                "items": [{"title": "A", "body": "B"}],
            }
        ],
    }
    data.update(overrides)
    return data


class TestValidateTopKeys:
    def test_rejects_missing_project(self):
        data = _make_data()
        del data["project"]
        with pytest.raises(SystemExit, match="project"):
            validate(data)

    def test_rejects_missing_brand(self):
        data = _make_data()
        del data["brand"]
        with pytest.raises(SystemExit, match="brand"):
            validate(data)

    def test_rejects_missing_sections(self):
        data = _make_data()
        del data["sections"]
        with pytest.raises(SystemExit, match="sections"):
            validate(data)

    def test_rejects_empty_sections(self):
        with pytest.raises(SystemExit, match="non-empty"):
            validate(_make_data(sections=[]))


class TestValidateProjectKeys:
    @pytest.mark.parametrize(
        "key",
        ["name", "tagline", "subtitle", "description", "github_url", "page_url", "logo_svg"],
    )
    def test_rejects_missing_project_key(self, key):
        data = _make_data()
        del data["project"][key]
        with pytest.raises(SystemExit, match=key):
            validate(data)


class TestValidateBrand:
    def test_rejects_missing_brand_tagline(self):
        data = _make_data()
        del data["brand"]["tagline"]
        with pytest.raises(SystemExit, match="tagline"):
            validate(data)


class TestValidateSections:
    def test_rejects_unknown_type(self):
        data = _make_data(sections=[{"id": "x", "type": "bogus", "icon": "info"}])
        with pytest.raises(SystemExit, match="unknown type"):
            validate(data)

    @pytest.mark.parametrize("key", ["id", "type", "icon"])
    def test_rejects_missing_required_field(self, key):
        sec = {"id": "x", "type": "features", "icon": "grid", "items": []}
        del sec[key]
        with pytest.raises(SystemExit, match=f"missing required field '{key}'"):
            validate(_make_data(sections=[sec]))

    def test_rejects_items_not_list(self):
        sec = {"id": "x", "type": "features", "icon": "grid", "items": "string"}
        with pytest.raises(SystemExit, match="requires 'items' to be a list"):
            validate(_make_data(sections=[sec]))


class TestValidatePerType:
    def test_code_block_requires_code(self):
        sec = {"id": "x", "type": "code_block", "icon": "code"}
        with pytest.raises(SystemExit, match="requires 'code'"):
            validate(_make_data(sections=[sec]))

    def test_code_block_requires_code_string(self):
        sec = {"id": "x", "type": "code_block", "icon": "code", "code": 123}
        with pytest.raises(SystemExit, match="requires 'code'"):
            validate(_make_data(sections=[sec]))

    def test_table_requires_headers(self):
        sec = {"id": "x", "type": "table", "icon": "grid", "rows": []}
        with pytest.raises(SystemExit, match="requires 'headers'"):
            validate(_make_data(sections=[sec]))

    def test_table_requires_rows(self):
        sec = {"id": "x", "type": "table", "icon": "grid", "headers": ["A"]}
        with pytest.raises(SystemExit, match="requires 'rows'"):
            validate(_make_data(sections=[sec]))

    def test_terms_requires_term_and_definition(self):
        sec = {
            "id": "x",
            "type": "terms",
            "icon": "info",
            "items": [{"term": "A"}],
        }
        with pytest.raises(SystemExit, match="requires 'definition'"):
            validate(_make_data(sections=[sec]))

    def test_features_requires_title_and_body(self):
        sec = {"id": "x", "type": "features", "icon": "grid", "items": [{"title": "A"}]}
        with pytest.raises(SystemExit, match="requires 'body'"):
            validate(_make_data(sections=[sec]))

    def test_stack_requires_name_and_description(self):
        sec = {"id": "x", "type": "stack", "icon": "layers", "items": [{"name": "A"}]}
        with pytest.raises(SystemExit, match="requires 'description'"):
            validate(_make_data(sections=[sec]))

    def test_links_requires_url(self):
        sec = {
            "id": "x",
            "type": "links",
            "icon": "link",
            "items": [{"title": "A", "description": "B"}],
        }
        with pytest.raises(SystemExit, match="requires 'url'"):
            validate(_make_data(sections=[sec]))

    def test_items_must_be_dicts(self):
        sec = {"id": "x", "type": "features", "icon": "grid", "items": ["string"]}
        with pytest.raises(SystemExit, match="must be a dict"):
            validate(_make_data(sections=[sec]))

    def test_text_requires_body(self):
        sec = {"id": "x", "type": "text", "icon": "info"}
        with pytest.raises(SystemExit, match="requires 'body'"):
            validate(_make_data(sections=[sec]))

    def test_custom_requires_body(self):
        sec = {"id": "x", "type": "custom", "icon": "info"}
        with pytest.raises(SystemExit, match="requires 'body'"):
            validate(_make_data(sections=[sec]))

    def test_notice_requires_body(self):
        sec = {"id": "x", "type": "notice", "icon": "info", "notice_type": "info"}
        with pytest.raises(SystemExit, match="requires 'body'"):
            validate(_make_data(sections=[sec]))


class TestValidateGoldenPath:
    def test_accepts_valid_data(self):
        validate(_make_data())


class TestGenerateOne:
    def test_produces_html(self, tmp_path):
        toml_path = tmp_path / "test.toml"
        out_path = tmp_path / "out" / "index.html"
        toml_path.write_text(
            textwrap.dedent("""\
                [project]
                name = "Test"
                tagline = "Tag"
                subtitle = "Sub"
                description = "Desc"
                github_url = "https://github.com/t/t"
                page_url = "https://t.github.io/t/"
                logo_svg = '<svg viewBox="0 0 64 64"></svg>'

                [brand]
                tagline = "Brand"

                [[sections]]
                id = "feat"
                type = "features"
                icon = "grid"
                title = "Features"

                [[sections.items]]
                title = "A"
                body = "B"
            """),
            encoding="utf-8",
        )
        generate_one(toml_path, out_path)
        assert out_path.exists()
        html = out_path.read_text()
        assert "Test" in html
        assert "Features" in html


class TestBatch:
    def test_skips_invalid_toml(self, tmp_path):
        good = tmp_path / "good.toml"
        bad = tmp_path / "bad.toml"
        good.write_text(
            textwrap.dedent("""\
                [project]
                name = "Good"
                tagline = "T"
                subtitle = "S"
                description = "D"
                github_url = "https://github.com/g/g"
                page_url = "https://g.github.io/g/"
                logo_svg = '<svg></svg>'

                [brand]
                tagline = "B"

                [[sections]]
                id = "f"
                type = "features"
                icon = "grid"
                title = "F"

                [[sections.items]]
                title = "A"
                body = "B"
            """),
            encoding="utf-8",
        )
        bad.write_text("this is not valid toml {{{", encoding="utf-8")
        out_dir = tmp_path / "docs"
        batch(tmp_path, out_dir)
        assert (out_dir / "good" / "index.html").exists()
        assert not (out_dir / "bad" / "index.html").exists()


class TestSectionTypesMatchTemplate:
    """F14: Ensure KNOWN_SECTION_TYPES matches template elif chain."""

    def test_types_match_template(self):
        template_text = (HERE / TEMPLATE).read_text()
        # Find first branch: {% if section.type == "X" %}
        first = re.search(r'\{%\s*if section\.type\s*==\s*"(\w+)"', template_text)
        # Find elif branches: {% elif section.type == "X" %}
        elifs = re.findall(r'\{%\s*elif section\.type\s*==\s*"(\w+)"', template_text)
        template_types = set(elifs)
        if first:
            template_types.add(first.group(1))
        assert template_types == KNOWN_SECTION_TYPES, (
            f"Template types {template_types} != KNOWN_SECTION_TYPES {KNOWN_SECTION_TYPES}\n"
            f"Missing from template: {KNOWN_SECTION_TYPES - template_types}\n"
            f"Extra in template: {template_types - KNOWN_SECTION_TYPES}"
        )
