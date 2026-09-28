# Improvements

Status: `[ ]` open, `[~]` in progress, `[x]` implemented, `[!]` needs a project decision.

## Architectural and process improvements

### 2026-09-28 — Calibrated-product lineage

**Source:** Initial IIRS inventory
**Category:** Data quality
**Status:** `[ ]`

**What:** Pair each raw scene with its official calibrated product and document units, versions, and checksums.
**Why:** The current cubes are detector counts, so mineral and hydration features cannot be interpreted directly.
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

## Implemented

- 2026-09-28: Added local untracked project instructions and a commit-message check for co-author attribution.
