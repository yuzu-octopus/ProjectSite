# Plan 003: Deduplicate projectpage skill CI section

**Finding:** #4 — projectpage skill (71 lines) contains a full CI YAML that duplicates README.md:169-206. Two sources of truth that will drift.

**Stamp:** f9687b2

## Why

The skill's CI workflow (lines 26-62) has an explicit auth URL for `git push` that the README's version lacks. Users hitting the skill get a working workflow; users reading the README get one that 403s on restrictive repos. The fix is to make the README canonical and have the skill reference it.

## Scope

**In scope:**
- `~/.config/mimocode/skills/projectpage/SKILL.md` — replace CI YAML block with a pointer to the README

**Out of scope:**
- `README.md` — that's plan 001's job
- `genpage.py`, `template.html.j2` — no changes

## Steps

1. Read the current `projectpage/SKILL.md`
2. Replace lines 21-62 (the "## CI Setup" section with the full YAML) with:

```markdown
## CI Setup

Use the CI workflow from the README — do NOT copy a different version.
The README has the working `permissions: contents: write` and `persist-credentials: false`
that prevent 403 errors.

See: https://raw.githubusercontent.com/yuzu-octopus/ProjectSite/main/README.md
(search for "## CI Setup")
```

3. Keep lines 1-20 (header + boundary guard + "webfetch the README") and lines 63-71 (SVG guidelines) intact.

## Verification

- Read the skill file — confirm no YAML block remains, pointer to README is present
- Confirm the skill is under 40 lines total
