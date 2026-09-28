# Improvements

Status: `[ ]` open, `[~]` in progress, `[x]` implemented, `[!]` needs a project decision.

## Architectural and process improvements

### 2026-09-28 — Calibrated-product lineage

**Source:** Initial IIRS inventory
**Category:** Data quality
**Status:** `[~]`

**What:** Complete the official calibration guide review and validate the differing unit conventions for the two paired pilot scenes.
**Why:** The active pilot now contains raw counts and calibrated radiance products, but their unit conventions and mask rules have not been validated for reflectance processing.
**Tradeoff:** Requires more acquisition and validation before modeling.
**Effort:** Medium.

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
