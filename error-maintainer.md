# Error registry

Record non-routine build, runtime, data-integrity, or workflow failures with cause, resolution, and prevention. Expected validation failures are reported in the relevant quality report instead.

| ID | Date | Symptom | Status | Resolution |
| --- | --- | --- | --- | --- |
| ERR-001 | 2026-09-28 | Bundled skill validator could not import PyYAML | Resolved by alternative validation | Standard-library checks completed |
| ERR-002 | 2026-09-28 | `unzip` command unavailable during archive verification | Resolved by alternative validation | Python `zipfile` checks passed for all four archives |
| ERR-003 | 2026-09-28 | Manifest omitted expected byte counts for calibrated float32 cubes | Resolved by parser update | Added IEEE754LSBSingle item size and reran pair assertions |
| ERR-004 | 2026-09-28 | Git commit blocked because local author identity was unset | Resolved by local repository configuration | Set a local human project identity; global Git config unchanged |

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

### ERR-002 — `unzip` command unavailable

**Date:** 2026-09-28
**Severity:** Low
**Category:** Dependency
**Status:** Resolved by alternative validation

**Symptom:** The `unzip` command was not installed when checking the four downloaded PRADAN archives.
**Context:** Verification of the selected raw and calibrated IIRS pilot downloads.
**Root cause:** The environment lacks the command-line ZIP utility.
**Resolution:** Used Python's standard-library `zipfile.ZipFile.testzip()` for all four archives. All returned `bad=None`.
**Prevention:** Prefer the dependency-free Python archive check when validating downloaded ZIPs in this environment.

### ERR-003 — Calibrated byte-size field omitted

**Date:** 2026-09-28
**Severity:** Medium
**Category:** Logic
**Status:** Resolved

**Symptom:** The active manifest left `expected_file_bytes_from_axes` blank for calibrated products.
**Context:** M1 manifest generation after extracting the two raw/calibrated pilot pairs.
**Root cause:** The parser handled `UnsignedLSB2` but not `IEEE754LSBSingle`.
**Resolution:** Added the four-byte IEEE754 mapping, regenerated the manifest, and verified declared, axis-derived, archive, and extracted sizes for all four products.
**Prevention:** Keep the data-type-to-item-size mapping explicit and assert it for every product family.

### ERR-004 — Git author identity missing

**Date:** 2026-09-28
**Severity:** Low
**Category:** Configuration
**Status:** Resolved

**Symptom:** `git commit` could not auto-detect an email address.
**Context:** Commit of the verified IIRS pilot pair update on `main`.
**Root cause:** No repository-local or global Git `user.name` and `user.email` were configured.
**Resolution:** Set a repository-local human project identity only. No global configuration was changed.
**Prevention:** Configure the intended repository-local author before the next commit if the project owner wants a different identity.

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
