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
- [x] Obtain and inspect the official IIRS archive/SIS, calibration tables, band-validity list, and supplied V6 user-guide text. The guide PDF is not included in `iir.zip`; the available guide text documents product naming and apparent-reflectance conversion. Official saturation XML declares radiance and count units, but does not explain the observed threshold mismatch or cube fill behavior.
- [ ] Validate numerical unit scales, fill and per-pixel saturation rules for the active calibrated cubes, and a correction path that respects each selected mode's band validity.
- [ ] Select additional independent scenes and record the split design.
- [~] Build the cited M1 literature gap matrix and use it to guide acquisition and processing choices.

**Status:** in progress. The active 2020 two-pair inventory, metadata lineage, SIS review, full cube scan, and targeted literature review are recorded. A matched 2026-02-27 E1G2 raw/calibrated pair passes label identity, ZIP CRC, and embedded cube MD5 checks. Its full-cube radiance and paired raw-count scan is complete, and its sparse grid confirms low-latitude coverage. The official LUT reproduces calibrated values on a fixed grid: median calibrated/LUT ratio 1.00375 and median per-band correlation 0.922. This supports the numeric scale internally, but does not independently validate calibration. The E1G2 saturation XML declares radiance in µW/cm²/sr/µm and dynamic range in counts. Applying those fields yields an unresolved mismatch: 99.878921% of valid-band radiance values meet the saturation threshold, but no raw counts reach `dynamic_range`. The cube label declares no fill constant. Do not create masks from these comparisons. The official workbook marks E1G2 bands 226–248 (4504.1–4874.9 nm) valid. Next: clarify field application and fill rules, validate radiance independently and geometry against a reference, then select independent coverage before M2 or M3.

**Current M1 quality unit:**

1. [x] Scan both calibrated cubes and save per-band finite, zero, negative, and candidate saturation-threshold counts with a figure. Keep zero-value and threshold flags distinct from confirmed fill or saturation.
2. [~] Compare representative valid-band radiance distributions after applying only PDS4 unit prefixes. The 2020 cross-scene scales are provisionally comparable. A fixed-grid comparison with the official LUT supports the calibrated numeric scale (median ratio 1.00375, median per-band correlation 0.922), but it is not independent calibration validation. The official XML declares saturation radiance in µW/cm²/sr/µm and `dynamic_range` in counts. Under these units, 99.878921% of valid-band radiance values meet the threshold and no raw counts meet `dynamic_range`; the alternative mW calculation is counterfactual only. The mask gate remains failed. Obtain authoritative field application and fill rules before assigning masks.
3. [x] Review published IIRS thermal methods and official mode validity. Prioritize E1G2 because the published thermal study used it and the official workbook marks bands 226–248 valid across 4504.1–4874.9 nm. This is mode selection evidence, not validation of the correction or mask.
4. [x] Verify the 2026-02-27 E1G2 raw/calibrated pair. Labels match on observation time, job ID, orbit, mode, dimensions, and wavelengths; both ZIP CRC and embedded QUB MD5 checks pass. The LUT comparison supports the calibrated unit scale internally. Independent validation and full-resolution geometry remain open.
5. [x] Stream the E1G2 raw and calibrated cubes, compare per-band values with the official radiance and dynamic-range fields, and inspect the sparse geometry grid. Save exact counts, sampled quantiles, and an explanatory figure. The LUT supports the radiance scale internally, but threshold comparisons conflict and do not establish a mask.
6. Obtain authoritative guidance on how to apply the E1G2 saturation-radiance and raw-count dynamic-range fields, and on the calibrated cube's fill and per-pixel validity rules. The XML declares units, but the paired data produce a severe mismatch; the QUB label contains no missing-value constant. Validate radiance against an independent reference and register the sparse geometry against an independent lunar reference with measured residuals. Do not make a mask from the current threshold comparisons.
   - Geometry validation path identified: acquire the LROC WAC 100 m/pixel global morphologic map covering the E1G2 footprint, use it only for image registration, and report residuals on held-out control points. The WAC image can test spatial alignment; it cannot validate radiometric scale.
   - Reflectance comparison path identified: PDS ODE returned five M3 Level-2 footprint-intersection candidates for E1G2. Their labels report 304 x 85-band cubes, thermal correction flagged, and special pixel -999.0. Next assess IIRS/M3 common valid coverage using the available geolocation, then acquire the best candidate. Attempt spectral comparison only after IIRS mask, radiance, geometry, and reflectance gates pass. Match spatial support, wavelength response, and viewing/illumination geometry; do not call this a direct IIRS radiance calibration check.
   - Apollo 16 ground comparison in the 2025 IIRS Level-2 paper is outside the current E1G2 footprint (about 5.47°W–3.50°W), so it is not a local validation target.
7. Select additional independent tracks and provinces after footprints are reviewed. Do not begin 3 µm reflectance processing or M3 scoring until applicable quality gates pass.

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
