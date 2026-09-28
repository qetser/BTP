# Improvements

Status: `[ ]` open, `[~]` in progress, `[x]` implemented, `[!]` needs a project decision.

## Architectural and process improvements

### 2026-09-28 — Calibrated-product lineage

**Source:** Initial IIRS inventory
**Category:** Data quality
**Status:** `[~]`

**What:** Validate the paired pilot cubes' numerical unit scales and pixel masks against the official SIS, labels, and calibration tables.
**Why:** The official SIS and mode tables are now available, but product-specific units and pixel-level validity have not been validated for reflectance processing.
**Tradeoff:** Requires more acquisition and validation before modeling.
**Effort:** Medium.

**Update (2026-09-28):** A full scan finds almost all valid-band values above the saturation CSV threshold as labeled, while no paired raw counts reach `dynamic_range`. A fixed-grid comparison to the official LUT supports the radiance scale internally (median calibrated/LUT ratio 1.00375, median band correlation 0.922). The threshold semantics and masks remain unresolved, and no independent calibration reference was used.

### 2026-09-28 — Thermal-capable pilot mode

**Source:** Official IIRS `E3G2` band-validity workbook
**Category:** Data quality
**Status:** `[~]`

**What:** Acquire and validate a paired `E1G2` pilot with valid long-wavelength bands, or validate another thermal correction method before 3 µm analysis.
**Why:** The current `E3G2` pilots have no valid 4–5 µm bands. Published IIRS thermal work used `E1G2`, and the official workbook marks bands 226–248 (4504.1–4874.9 nm) valid in that mode.
**Tradeoff:** Additional acquisition or method validation is needed.
**Effort:** Medium.

**Update (2026-09-28):** A matched 2026-02-27 E1G2 raw/calibrated pair has been acquired and passes label identity, ZIP CRC, and embedded QUB MD5 checks. This closes the acquisition portion only. Radiance scale, geometry, saturation/fill masks, correction quality, and independent coverage remain open.

### 2026-09-28 — Independent evaluation coverage

**Source:** M1–M3 research review
**Category:** Testing
**Status:** `[ ]`

**What:** Acquire more nonoverlapping IIRS tracks and reviewed label regions before publishing scores.
**Why:** Four current strips are geographically limited and none is polar.
**Tradeoff:** Larger data and review burden.
**Effort:** Large.

### 2026-09-28 — Research and review cadence

**Source:** Codex setup adaptation
**Category:** Process
**Status:** `[!]`

**What:** Specify a digest cadence, source scope, independent-review model, and evaluation criteria before enabling background research or cross-model checks.
**Why:** An unbounded recurring task would create noise and unverified claims.
**Tradeoff:** Remains manual until decided.
**Effort:** Small to define; ongoing to operate.

### 2026-09-28 — Structured research result artifacts

**Source:** User feedback
**Category:** Process and reproducibility
**Status:** `[x]`

**What:** Store phase and module summaries, findings, notes, machine-readable metrics, and metric figures under `results/`.
**Why:** Research decisions and quantitative evidence must survive context changes and remain reviewable.
**Tradeoff:** Each module needs a small documentation step before it can be marked complete.
**Effort:** Small.

## Implemented

- 2026-09-28: Added local untracked project instructions and a commit-message check for co-author attribution.
- 2026-09-28: Added the phase/module result protocol and initialized M1–M3 result directories.
