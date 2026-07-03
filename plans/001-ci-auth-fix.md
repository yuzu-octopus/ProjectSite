# Plan 001: Fix CI workflow auth in README

**Finding:** #1 — README.md CI example (lines 169-206) uses plain `git push` without `persist-credentials: false` on the first checkout. Users copying this get 403 on repos with restrictive default permissions.

**Stamp:** f9687b2

## Why

The projectpage skill's version (now being removed in plan 003) had the fix: `persist-credentials: false` on the generator checkout. But the README — the canonical reference — never got it. After plan 003 removes the skill's duplicate, the README is the only source. It must work.

## Scope

**In scope:**
- `README.md` lines 169-206 — the CI YAML example

**Out of scope:**
- `.github/workflows/check.yml` — already works (single repo checkout, has `permissions: contents: write`)
- `template.html.j2`, `genpage.py` — no changes

## Steps

1. Read `README.md` lines 169-206
2. Add `persist-credentials: false` to the generator checkout step (after `path: generator`)
3. The workflow should look like this after the fix:

```yaml
      - name: Checkout generator
        uses: actions/checkout@v4
        with:
          repository: yuzu-octopus/ProjectSite
          path: generator
          persist-credentials: false
```

4. Verify the full README renders correctly (no broken markdown)

## Verification

- Read `README.md` — confirm `persist-credentials: false` is present in the CI example
- Confirm the CI YAML is syntactically valid (no missing indentation)
- `ruff check genpage.py` still passes (no Python changes, but sanity check)
