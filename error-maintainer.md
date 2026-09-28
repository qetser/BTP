# Error registry

Record non-routine build, runtime, data-integrity, or workflow failures with cause, resolution, and prevention. Expected validation failures are reported in the relevant quality report instead.

| ID | Date | Symptom | Status | Resolution |
| --- | --- | --- | --- | --- |
| ERR-001 | 2026-09-28 | Bundled skill validator could not import PyYAML | Resolved by alternative validation | Standard-library checks completed |

### ERR-001 — Bundled skill validator unavailable

**Severity:** Low
**Category:** Dependency
**Status:** Resolved by alternative validation

**Symptom:** `quick_validate.py` exited with `ModuleNotFoundError: No module named 'yaml'`. The default Python 3.8 also lacks `tomllib` for the agent TOML check.
**Context:** Verification of the new Codex skills and project agent configuration.
**Attempts:** Ran the bundled validator; checked available Python versions and modules.
**Root cause:** PyYAML is not installed in this environment; `tomllib` starts with Python 3.11.
**Resolution:** Validated skill frontmatter, names, and placeholders with a dependency-free script; parsed hook JSON and agent TOML with Python 3.11; tested the session-start script and Git commit-message check.
**Prevention:** Use the bundled validator when its dependency is available; otherwise record the alternative checks instead of claiming it ran.

## Entry template

### ERR-NNN — short title

**Date:** YYYY-MM-DD
**Severity:** Critical / High / Medium / Low
**Category:** Build / Runtime / Data / Logic / Configuration
**Status:** Open / Resolved / Workaround

**Symptom:** Exact message or observable failure.
**Context:** Command, data product, environment, and affected files.
**Attempts:** What was tried and what happened.
**Root cause:** Evidence for the cause.
**Resolution:** Exact change and verification.
**Prevention:** Rule, check, or test, if justified.
