# Current task plan

## Goal

Complete a defensible M1–M3 foundation for Chandrayaan-2 IIRS, following [the scientific implementation plan](../docs/m1_m3_plan.md). This file tracks the current work; that document defines the detailed quality gates.

## Research artifact rule

Every phase and module produces a concise record under `results/<phase>/<module>/`. Each record has a summary, findings, and notes. Metrics must be saved as machine-readable CSV or JSON together with a PNG or SVG figure. No score is reported without both artifacts and its data split, units, source version, and code commit.

## Phase 0 — Project setup

- [x] Record project context and scientific risks.
- [x] Add local Codex instructions, tracked workflow files, starter skills, and checks.
- [x] Confirm raw data and local instructions are excluded from Git.

**Status:** complete on 2026-09-28.

## Phase 1 — M1 product inventory

- [x] Parse every PDS4 label into a versioned manifest.
- [x] Verify archive and extracted cube checksums and dimensions.
- [x] Obtain and inspect the official IIRS archive/SIS, calibration tables, and band-validity list. The separate user guide PDF is not included in `iir.zip`.
- [ ] Validate the two pilot cubes' numerical unit scales, fill and per-pixel saturation rules, and a correction path that respects the selected mode's band validity.
- [ ] Select additional independent scenes and record the split design.
- [~] Build the cited M1 literature gap matrix and use it to guide acquisition and processing choices.

**Status:** in progress. The active two-pair inventory, metadata lineage, SIS review, full cube scan, and targeted literature review are recorded. Radiance unit prefixes are provisionally supported by comparable sampled medians, but saturation-table units and pixel masks remain unresolved. Published IIRS thermal work uses E1G2, and the local official workbook marks bands 226–248 (4504.1–4874.9 nm) valid in that mode. Next: acquire and verify a paired E1G2 scene, resolve the saturation convention, and select independent coverage before M2 or M3.

**Current M1 quality unit:**

1. [x] Scan both calibrated cubes and save per-band finite, zero, negative, and candidate saturation-threshold counts with a figure. Keep zero-value and threshold flags distinct from confirmed fill or saturation.
2. [~] Compare representative valid-band radiance distributions after applying only the PDS4 unit prefixes. The cross-scene scales are provisionally comparable. Saturation-table unit comparison failed: interpreting its values as µW flags nearly all positive pixels; interpreting them as mW flags none. Resolve against authoritative documentation before assigning masks.
3. [x] Review published IIRS thermal methods and official mode validity. Prioritize E1G2 because the published thermal study used it and the official workbook marks bands 226–248 valid across 4504.1–4874.9 nm. This is mode selection evidence, not validation of the correction or mask.
4. Select and verify a paired E1G2 scene, resolve saturation units and pixel masks, then freeze nonoverlapping track/province coverage. Do not begin 3 µm reflectance processing or M3 scoring until the applicable quality gates pass.

## Phase 2 — M2 calibrated reflectance

- [ ] Implement one-scene pilot only after source units and calibration lineage are known.
- [ ] Validate geometry, masks, thermal correction, and photometry against independent references.
- [ ] Export traceable analysis-ready patches.

**Status:** pending; gated by Phase 1 calibration evidence.

## Phase 3 — M3 baselines

- [ ] Review labels and freeze geographically independent splits.
- [ ] Implement physical and clustering references, then a from-scratch CNN.
- [ ] Report held-out metrics only on defensible labels, with uncertainty.

**Status:** pending; gated by Phase 2 quality report and label review.

## Phase 4 — M4 Earth-to-Moon foundation-model transfer

- [ ] Select and freeze the public HyperFree and HyperSIGMA checkpoints and record their licenses, input bands, preprocessing, and commit or release identifiers.
- [ ] Build a wavelength-aware IIRS adapter and test SWIR-only input before adding the extended mid-infrared bands.
- [ ] Evaluate frozen zero-shot transfer with spectral-library prototypes on the same held-out split used by M3.
- [ ] Train a frozen-encoder linear probe with the same labels, masks, and split.
- [ ] Run controlled fine-tuning only after the zero-shot and linear-probe runs are reproducible.
- [ ] Save every run configuration, metric CSV or JSON, and PNG or SVG figure under `results/phase-2/m4-transfer/`.

**Status:** future; starts only when the M3 quality gate passes. HyperFree and HyperSIGMA are comparison backbones, not substitutes for calibrated data or defensible labels.

## Phase 5 — M5 lunar self-supervised adaptation

- [ ] Continue pretraining the selected backbone on unlabeled calibrated IIRS patches with masked spectral reconstruction.
- [ ] Compare reconstruction, derivative, and band-ratio constraints in an ablation.
- [ ] Re-evaluate under the same few-shot and held-out protocol as M4.
- [ ] Save checkpoints, run manifests, metrics, and figures under `results/phase-2/m5-adaptation/`.

**Status:** future; gated by reproducible M4 transfer results and sufficient calibrated unlabeled coverage.

## Phase 6 — M6 downstream scientific tasks

- [ ] Evaluate mineral classification or abundance proxies only on reviewed labels.
- [ ] Evaluate the thermally corrected 3 micrometre hydration index with uncertainty and independent references.
- [ ] Keep any water-ice interpretation separate from an apparent hydroxyl or water-equivalent absorption result.
- [ ] Save maps, metric artifacts, and limitations under `results/phase-2/m6-science/`.

**Status:** future; gated by M2 correction quality, M3 labels, and M4/M5 model validation.

## Review

Setup and the local M1 pilot inventory are complete. M1 scientific documentation and coverage gates remain open; see `tasks/progress.md` for the handoff.
