# Plans

**Base commit:** f9687b2

| # | Plan | Status | Depends on |
|---|------|--------|------------|
| 003 | Deduplicate projectpage skill CI section | DONE | — |
| 001 | Fix CI workflow auth in README | DONE (already fixed in 6a78fb3) | 003 |
| 002 | Add TOML schema validation | DONE | — |
| 004 | CSS polish — fluid type, text-wrap, hover | DONE | — |

**Execution order:** 003 → 001 → 002 → 004

**Findings index:**

| # | Finding | Status |
|---|---------|--------|
| 1 | CI workflow auth mismatch | → Plan 001 |
| 2 | No TOML schema validation | → Plan 002 |
| 3 | Hardcoded copyright year | Deferred (trivial, can bundle later) |
| 4 | Skill duplicates README CI | → Plan 003 |
| 5 | No tests | Deferred (plan 002 validation is a start) |
| 6 | CI uses pip not uv | Deferred (works, cosmetic) |
