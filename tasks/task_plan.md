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
- [ ] Obtain the authenticated IIRS product guide/SIS and validate the two pilot products' unit conventions, fill/saturation rules, band validity, and correction lineage. Label-based pairing and a provisional data dictionary are complete.
- [ ] Select additional independent scenes and record the split design.

**Status:** in progress. The active two-pair inventory and metadata lineage passed. Next concrete unit: obtain the official guide through PRADAN access, resolve the calibrated-unit discrepancy, then select independent scenes and freeze the acquisition plan.

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
