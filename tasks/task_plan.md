# Current task plan

## Goal

Complete a defensible M1–M3 foundation for Chandrayaan-2 IIRS, following [the scientific implementation plan](../docs/m1_m3_plan.md). This file tracks the current work; that document defines the detailed quality gates.

## Phase 0 — Project setup

- [x] Record project context and scientific risks.
- [x] Add local Codex instructions, tracked workflow files, starter skills, and checks.
- [x] Confirm raw data and local instructions are excluded from Git.

**Status:** complete on 2026-09-28.

## Phase 1 — M1 product inventory

- [ ] Parse every PDS4 label into a versioned manifest.
- [ ] Verify archive and extracted cube checksums and dimensions.
- [ ] Obtain IIRS product guide and identify calibrated counterpart products.
- [ ] Select additional independent scenes and record the split design.

**Status:** pending. Next concrete unit: manifest and integrity verification for the four existing scenes.

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

## Review

Setup is complete. Scientific implementation has not started; see `tasks/progress.md` for the handoff.
