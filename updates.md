# Updates

Meaningful project changes are recorded newest first. Entries describe the change and evidence; the Git history supplies the exact commit hash.

## 2026-09-28 — Set the next IIRS thermal pilot target from literature

**Phase:** Phase 1, M1 acquisition and gap analysis

**Type:** Literature review and processing plan

- Reviewed IIRS thermal, reflectance, photometric, and hydration papers from 2021 through 2026, plus the official PRADAN FAQ and mode-validity workbook.
- Identified E1G2 as the next thermal pilot mode. The 2022 study used E1G2, and the local official workbook marks bands 226–248 valid from 4504.1 to 4874.9 nm.
- Recorded the 2026 finding that reflectance near 3156 nm is sensitive to temperature uncertainty. M2 must propagate that uncertainty.
- Added an initial cited gap matrix, M1 literature records, README literature notes, and an updated Mermaid flow. No new data or corrected reflectance was produced.

**Why:** The current E3G2 strips lack valid longwave channels for the documented thermal method. Literature and mode metadata provide a concrete acquisition target.

**Impact:** E1G2 is a candidate mode, not a validated correction. The saturation-unit conflict, per-pixel masks, scene acquisition, and independent coverage remain open.

## 2026-09-28 — Explain the pilot scan in the README

**Phase:** Phase 1, M1 product inventory

**Type:** Research communication

- Added the calibrated cube scan results and a three-panel quality figure to the README.
- Explained which counts are exact, how sampled quantiles were computed, and why the saturation comparison does not define a pixel mask.
- Added a left-to-right Mermaid flow from paired products and official references through the scan outputs and remaining M1 gates.

**Why:** Readers need a clear account of the evidence and the gates that still block reflectance work.

**Impact:** No scientific data or result changed. The README now reports the provisional unit-scale finding and the unresolved saturation-unit conflict.

## 2026-09-28 — Scan calibrated pilot radiance cubes

**Phase:** Phase 1, M1 product inventory

**Type:** Research evidence and quality figure

- Added a reproducible scan of every pixel in the two calibrated pilot cubes, preserving per-band counts and fixed-grid positive-pixel quantiles in CSV and a PNG figure.
- Recorded provisionally comparable radiance scales after applying the product unit prefixes.
- Found that the saturation table's declared µW unit and the SIS's general mW unit produce opposite candidate-mask outcomes. Marked the saturation gate unresolved and kept the candidate counts separate from confirmed masks.
- Updated the M1 summary, findings, data dictionary, task plan, and progress log. E3G2's lack of valid 4–5 µm bands and the unresolved masks continue to block reflectance correction.

**Why:** Establish data-quality evidence for the active cubes before any M2 correction.

**Impact:** No reflectance, saturation mask, label, or model metric was created. The active task remains M1 until the threshold convention, thermal method, and independent coverage are resolved.

## 2026-09-28 — Display active IIRS strips in README

**Phase:** Phase 1, M1 product inventory

**Type:** Research visualization and documentation

- Verified both calibrated-product browse PNGs against their PDS4 labels.
- Added two reproducible four-part strip previews and embedded them in the README with source, order, and scientific limits.

**Why:** Readers can identify the actual pilot observations without mistaking browse display values for calibrated radiance or reflectance.

**Impact:** No numerical calibration, reflectance, or model result changed.

## 2026-09-28 — Show M1 findings and validity figure in README

**Phase:** Phase 1, M1 communication

**Type:** Documentation

- Added the official archive findings and embedded the saved band-validity SVG in the README with a caption, source CSV, and generation script.
- Clarified that the four scene archives and the separate official `iir.zip` are all local and integrity checked.

**Why:** Readers need to see the mode limitation and unresolved calibration gate alongside the pilot status.

**Impact:** No data, scientific metric, or model result changed.

## 2026-09-28 — Inspect official IIRS archive and validity

**Phase:** Phase 1, M1 product documentation

**Type:** Research evidence

- Verified the supplied official `iir.zip` and read its SIS V17, calibration tables, and band-validity workbook.
- Saved the mode validity CSV and SVG figure; recorded that both `E3G2` pilots lack valid 4–5 µm bands.
- Updated the pilot dictionary and M2 gate for unit-scale, pixel-mask, and thermal-method validation.

**Why:** Instrument mode validity and radiance units control which corrections and spectral claims are defensible.

**Impact:** No reflectance cube or scientific performance score was produced.

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
