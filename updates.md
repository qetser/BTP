# Updates

Meaningful project changes are recorded newest first. Entries describe the change and evidence; the Git history supplies the exact commit hash.

## 2026-09-28 — Record pilot radiance dictionary and M1 gate

**Phase:** Phase 1, M1 product documentation

**Type:** Research evidence and status correction

- Added a provisional label-based data dictionary and corrected stale M1 status text after the active two-pair XML comparison.
- Recorded the calibrated labels' radiance description and different unit prefixes.
- Checked PRADAN guide access: the documented `Other Downloads` page requires sign-in, so guide-specific calibration and mask rules remain unverified.

**Why:** The M2 pilot needs explicit product semantics and a clear unit gate before numerical processing.

**Impact:** No reflectance product, scientific metric, or model result was created. M1 remains open for guide interpretation and independent coverage.

## 2026-09-28 — Extract and pair the M2 pilot products

**Phase:** Phase 1, M1 product lineage
**Type:** Data and research evidence

- Cleared the old ignored data products and kept only two selected raw/calibrated pairs.
- Extracted all four archives and regenerated the active metadata manifest.
- Confirmed exact raw-to-calibrated pairing by timestamp, job ID, orbit, dimensions, and wavelength table.
- Recorded product-specific calibrated units in `results/phase-1/m1-inventory/pilot_lineage.md`.

**Why:** M2 needs a verified raw-to-calibrated pair and explicit units before any numerical correction or reflectance interpretation.

**Impact:** The active local pilot is two pairs from 2020-02-08. The previous four-scene raw inventory remains historical and is no longer present in `data/`.

## 2026-09-28 — Reject nonmatching PRADAN download list

**Phase:** Phase 1, M1 product lineage
**Type:** Research evidence

- Compared the ten supplied PRADAN `ndi` URLs with the four raw scene timestamps.
- Found no exact observation match; all supplied URLs are from 2024 or 2025.
- Stopped and removed the partial first download before retaining any product.

**Why:** A derived product from another observation cannot serve as the calibrated counterpart for a raw scene.

**Impact:** No new data was retained. A new PRADAN selection must be generated using the raw observation timestamp.

## 2026-09-28 — Complete M1 local integrity inventory

**Phase:** Phase 1, M1 inventory
**Type:** Feature and research evidence

- Added `scripts/build_iirs_manifest.py` to parse PDS4 labels and compute archive and cube integrity fields.
- Added `results/phase-1/m1-inventory/iirs_inventory.csv` with metadata, dimensions, byte counts, MD5, and ZIP SHA-256 values.
- Recorded the four-scene integrity pass in the M1 findings and observation checklist.

**Why:** The raw scenes must be traceable and byte-verified before calibration work begins.

**Impact:** All four local scenes passed the integrity checks. Calibrated product lineage and independent coverage remain open.

## 2026-09-28 — Make foundation-model timing explicit

**Phase:** Research roadmap
**Type:** Planning

- Added Phase 4 for HyperFree and HyperSIGMA transfer experiments.
- Added Phase 5 for lunar self-supervised adaptation and Phase 6 for downstream scientific tasks.
- Kept M1 manifest and integrity verification as the active next step.

**Why:** Foundation-model comparisons are only interpretable after calibration, labels, splits, and M3 baselines pass their quality gates.

**Impact:** No model runs or scientific results changed.

## 2026-09-28 — Add research result protocol

**Phase:** Project workflow setup
**Type:** Documentation and process

- Added `results/` phase and module directories for M1 inventory, M2 calibration, and M3 baselines.
- Added rules for concise findings, research notes, machine-readable metrics, and PNG or SVG metric figures.
- Marked M1 manifest and integrity verification as the active next unit.

**Why:** Every scientific stage needs a durable evidence trail. Quantitative claims must be accompanied by source values and a saved figure.

**Impact:** No data or scientific scores changed. The result directories contain setup notes only until processing runs.

## 2026-09-28 — Keep agent tooling local

**Phase:** Project workflow setup
**Type:** Configuration

- Removed `.agents/skills` and `.codex` from Git tracking while preserving their local files.
- Added ignore rules and updated the setup guide and Git scope lesson.

**Why:** The project's agent tooling should remain specific to this checkout, as requested.

**Impact:** Fresh clones will need to recreate local skills and Codex configuration if wanted.

## 2026-09-28 — Codex project setup

**Phase:** Project workflow setup
**Type:** Configuration and documentation

- Added the project charter, living logs, current task plan, research prompt, observation checklist, and Codex-native skills, agents, and session-start reminder.
- Kept `AGENTS.md` and `codex.md` local and ignored; added a local Git hook to reject Claude/Codex co-author trailers.

**Why:** Preserve scientific decisions and operational context across sessions while keeping the requested local instructions out of Git.

**Impact:** No scientific data or model outputs changed. Project hooks require trust in a fresh Codex session.

## 2026-09-28 — Initial IIRS research and archive inventory

**Phase:** M1 planning
**Type:** Documentation

- Added the M1–M3 README and implementation plan, inventoried four raw IIRS archives, and extracted all four locally.

**Why:** Establish the calibration and evaluation gates before reporting scientific baselines.

**Impact:** Data remain ignored by Git; no calibrated reflectance or scores exist yet.
