# Updates

Meaningful project changes are recorded newest first. Entries describe the change and evidence; the Git history supplies the exact commit hash.

## 2026-09-28 — Summarize M1 work and explain IIRS product terms

**Phase:** Phase 1, M1 product inventory and data quality

**Type:** Results documentation

- Added an M1 summary table to the README with work performed, key outputs, numerical results, evidence links, and gate status.
- Added a glossary for IIRS, E1G2/E3G2, NRI/NCI, raw counts, calibrated radiance, LUTs, bands, PDS4 labels, QUB, integrity checks, and quality masks.
- Expanded the Mermaid LR chart to trace all three pairs through mode checks, cube scans, LUT comparison, threshold and geometry gates, saved evidence, and M2/M3 readiness.
- Linked table rows to the supporting figures, CSVs, scripts, and module records. Stated clearly that M1 does not produce reflectance or mineral, hydration, or ice detections.
- Updated `results/README.md`, which had incorrectly stated that no quantitative results existed. It now indexes M1 measurements, evidence figures, module records, and remaining gates.

**Why:** Readers need to understand both the measured results and the terms used to describe the products.

**Impact:** M1 evidence and open gates are now summarized in one place. M2 reflectance processing and M3 scoring remain gated by unresolved masks, independent radiance validation, geometry, and coverage.

## 2026-09-28 — Audit E1G2 radiance scale, thresholds, and footprint

**Phase:** Phase 1, M1 data quality and geometry

**Type:** Full-cube QA analysis and research documentation

- Streamed the matched raw and calibrated E1G2 QUB objects from their ZIP archives; all 781,440,000 calibrated values are finite.
- Compared calibrated values with the official band-major LUT using `raw_count × gain + offset`, then converted product values from µW to mW as directed by the SIS. The fixed-grid median calibrated/LUT ratio is 1.00375, with median per-band correlation 0.922. This supports internal scale consistency, not independent calibration validation.
- The saturation CSV threshold as labeled is met or exceeded by 99.878921% of valid-band values. Interpreting table values as mW yields 12 exceedances. No paired raw counts reach `dynamic_range`. These checks do not define masks, so no saturation or fill mask was assigned.
- Inspected the 1,476-point sparse geometry grid, which spans about 5.47°W–3.50°W and 6.53°S–26.86°N.
- Saved a per-band CSV, reproducible scan script, figure, and findings record. Updated the README figure and LR flow, task plan, and gap matrix.

**Why:** E1G2 supplies officially valid longwave bands, but thermal processing needs trustworthy radiance values, masks, and spatial geometry first.

**Impact:** The scene is a low-latitude E1G2 candidate, not a validated thermal-correction input. M2 remains blocked pending authoritative threshold/fill semantics, independent radiance validation, and full-resolution geometry review.

## 2026-09-28 — Verify the matched E1G2 raw/calibrated pair

**Phase:** Phase 1, M1 acquisition and inventory

**Type:** Product acquisition, integrity checks, and documentation

- Downloaded only the matching calibrated NCI product for the previously verified raw E1G2 candidate.
- Both ZIP CRC checks passed. Raw and calibrated XML labels match on timestamp, job ID, orbit, mode, dimensions, and wavelengths. Both QUB streams match their PDS4 MD5 declarations.
- Recorded calibrated radiance units as labeled (`µW/cm**2/sr/µm`), with numerical unit validation still open. Geometry, saturation/fill masks, and independent coverage remain open.
- Extracted the official calibrated browse PNG and added it to the README with clear interpretation limits. Updated the Mermaid LR flow to show the completed pair checks and remaining M1 gates.

**Why:** The thermal pilot needs a matched radiance product in a mode with valid longwave bands. XML and checksum checks establish product identity and integrity before scientific processing.

**Impact:** An E1G2 pair is now available locally and passes archive/cube integrity checks. No reflectance, thermal correction, or metric was computed. M2 remains gated by unit, geometry, and mask validation.

## 2026-09-28 — Verify the raw label for an E1G2 candidate

**Phase:** Phase 1, M1 acquisition and gap analysis

**Type:** Product acquisition and label verification

- Selected the matching 2026-02-27 raw/calibrated product IDs from the PRADAN-generated list. Downloaded only the raw NRI ZIP, not the bulk selection.
- ZIP CRC passed. The raw PDS4 label confirms `exposure=e1`, `gain=g2`, and start time `2026-02-27T12:39:53.8758Z`.
- The request for the matching calibrated NCI ZIP returned HTTP 302 to sign-in; it was not saved.
- Updated the README flow and M1 records with the confirmed raw-mode evidence and the remaining calibrated-pair gate.

**Why:** Filename suffixes do not encode exposure/gain. The XML label is needed to verify E1G2.

**Impact:** This is a verified raw E1G2 candidate only. Do not use it for thermal correction until its calibrated counterpart and data quality are checked.

## 2026-09-28 — Incorporate supplied IIRS User Guide text

**Phase:** Phase 1, M1 product documentation

**Type:** Documentation review

- Recorded the user-supplied V6 guide definitions for raw `nri`, calibrated `nci`, timestamp, station suffix, and apparent-reflectance conversion.
- Updated the acquisition records to make clear that `d18` is a station ID and does not identify exposure/gain. The product XML is required to verify E1G2.
- Kept saturation-table unit and fill-mask interpretation unresolved because the supplied guide sections do not answer those questions.

**Why:** Interpret filenames and product levels correctly without treating the station suffix as a mode identifier.

**Impact:** The guide supports the XML-based E1G2 check on the selected raw candidate. It does not close the calibrated-pair, mask, or thermal-correction gates.

## 2026-09-28 — Verify PRADAN scene-table access gate

**Phase:** Phase 1, M1 acquisition and gap analysis

**Type:** Live archive access check and workflow update

- Opened the official public Browse and Download route in a read-only browser session. It redirected to account sign-in; no scene table or IIRS filters were visible.
- Submitted no credentials and downloaded no data. Stopped the browser session after recording the result.
- Updated the README LR diagram, task plan, findings, and literature module records to show the authenticated acquisition gate and the required pair checks.

**Why:** E1G2 is the literature-backed thermal-pilot target, but selecting an actual observation requires access to the protected scene table.

**Impact:** E1G2 remains a candidate mode, not an acquired or validated scene. The next action is to use authorized PRADAN access to select a matched raw/calibrated pair and inspect labels, validity, units, checksums, and footprint. Existing saturation, mask, and independent-coverage gates remain open.

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
