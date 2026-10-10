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

**Update (2026-09-29):** The official E1G2 saturation-table XML explicitly declares `Saturation` in µW/cm**2/sr/µm and `Dynamic_Range` in counts. This resolves the unit-field question, not the observed mismatch: 99.878921% of valid-band calibrated values meet the declared saturation threshold, while no raw counts reach `Dynamic_Range`. The calibrated QUB label contains no missing-value constant. A fixed-grid comparison to the official LUT supports the radiance scale internally (median calibrated/LUT ratio 1.00375, median band correlation 0.922), but no independent calibration reference was used. Field application, fill rules, and masks remain unresolved.

**Update (2026-10-03):** Targeted Exa literature searches found a 2025 LPSC abstract that converts linearized Level-0 counts to radiance using the ISRO LUT, saturation radiance, and CCD dynamic range. Its reconstructed radiance differs from ISRO Level 1, partly because it omits order-sorting-filter adjustments and keystone correction. The paper does not define the official Level-1 threshold test or fill values. Treat this as a method lead, not a rule for the local mask. The quality gate remains open.

**Update (2026-10-03):** A fixed-line E1G2 sample of 888,000 valid-band observations found 97.8048% at or above the declared radiance threshold and zero raw counts at or above `Dynamic_Range`. A table-only comparison gives median LUT/saturation ratios of 1.559 for E1G2 and 5,118 for E3G2 if the saturation numbers are treated counterfactually as mW; both XML labels declare µW. This does not support one inferred correction across modes. See `results/phase-1/m1-saturation-sample/`; no mask was assigned and the gate remains open.

**Update (2026-10-03):** Auditing both paired E3G2 products gives median per-band Level-1/LUT-stage ratios near 0.0002 after applying each calibrated label's unit conversion; median correlations are 0.898 (`m65`) and 0.924 (`d18`). The guide documents later destriping and radiance post-processing, and the archive contains no destriping coefficients. The stage difference remains unexplained and does not prove a LUT error. See `results/phase-1/m1-e3g2-lineage-check/`; no correction or mask was applied. The next pilot should use the matched E1G2 Level-1 product.

**Update (2026-10-08):** Rechecked the public PRADAN FAQ and ISRO processing description. They do not define archived Level-1 saturation-mask application or fill encoding. The LPSC 2025 abstract uses saturation radiance and detector dynamic range in a separate Level-0 recalibration but does not establish Level-1 mask semantics. The clarification gate remains open; see `results/phase-1/m1-literature/findings.md`.

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
