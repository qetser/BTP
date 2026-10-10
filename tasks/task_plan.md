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
- [x] Obtain and inspect the official IIRS archive/SIS, calibration tables, band-validity list, and supplied V6 user-guide text. The guide PDF is not included in `iir.zip`; the available guide text documents product naming and apparent-reflectance conversion. SIS Appendix H confirms that only `VALID` bands are valid, while `SATURATION`, `OSF`, and `INVALID` are band-level exclusions. The saturation XML declares radiance and count units, but neither it nor the SIS explains the observed threshold mismatch or cube fill behavior.
- [x] Validate numerical unit scales: on 2026-10-10 the physical I/F and brightness-temperature test showed that each label's unit is correct for all three local products (`m65` stores mW; both `d18` products store µW). See [unit test](../results/phase-1/m2-radiance-unit-physics/summary.md).
- [ ] Validate fill and per-pixel saturation rules. The saturation table read in its declared µW flags 99.88% of physically valid E1G2 radiance, so the table's unit is inconsistent with the product. No mask is assigned.
- [ ] Select additional independent scenes and record the split design.
- [~] Build the cited M1 literature gap matrix and use it to guide acquisition and processing choices. The 2026-10-08 public-source check found no official rule for Level-1 saturation masks or fill values. The 2025 LPSC raw-count recalibration uses the ISRO LUT, saturation radiance, and CCD dynamic range, but does not define archived Level-1 mask semantics. SIS Appendix H confirms the mode-dependent band table is an exclusion rule at band level. An audit of the public CH2IIRS implementation found no explicit per-pixel fill/saturation handling in the inspected thermal routines; this does not establish that the archive lacks provider masks. Keep the interpretation gate open.

**Status:** in progress. **Update 2026-10-10:** the guide/label unit conflict is resolved on physical grounds; each product label's unit is correct (see the M2 pilot modules). The mask, fill, absolute-scale and absolute-geometry gates remain open. The earlier status follows. The active 2020 two-pair inventory, metadata lineage, SIS review, full cube scan, and targeted literature review are recorded. A matched 2026-02-27 E1G2 raw/calibrated pair passes label identity, ZIP CRC, and embedded cube MD5 checks. Its full-cube radiance and paired raw-count scan is complete, and its sparse grid confirms low-latitude coverage. The E1G2 LUT-stage output is numerically close to Level 1 on a fixed grid (median ratio 1.00375; median per-band correlation 0.922), but this is not independent validation. The supplied V6 guide says calibrated products use mW units while the E1G2 PDS4 label says µW; this factor-of-1000 conflict remains unresolved. The guide documents downstream destriping and radiance post-processing and attributes LUT-to-Level-1 differences to those steps, but the observed E3G2 ratios have not been reproduced. Saturation fields and fill rules remain unresolved: direct XML-unit comparison flags nearly all radiances in E1G2/E3G2, while almost no raw counts reach `Dynamic_Range`. The QUB labels declare no fill constant. Do not create masks or infer corrections from these comparisons. E1G2 bands 226–248 (4504.1–4874.9 nm) are mode-valid. Published alternatives now identified: normalized IIRS–M³ spectra can check relative spectral shape; the Apollo 16/RELAB 62231 empirical-line method requires a separate IIRS scene covering Apollo 16; and Diviner comparison matched by ground control points and acquisition time can check derived temperature. None resolves current-scene radiance units or mask semantics. ODE has returned the M³ candidate label and file inventory, but its JPL-hosted RFL and LOC binaries could not be fetched because local TLS validation fails. Next: obtain both binaries through a valid-TLS official route, then measure geolocated valid-pixel overlap; plan an Apollo 16 scene for absolute reflectance comparison; continue local label/SIS/guide evidence review for units and masks; preserve all open gates before M2 or M3.

**Current M1 quality unit:**

1. [x] Scan both calibrated cubes and save per-band finite, zero, negative, and candidate saturation-threshold counts with a figure. Keep zero-value and threshold flags distinct from confirmed fill or saturation.
2. [~] Compare representative valid-band radiance distributions after applying only PDS4 unit prefixes. The 2020 E3G2 calibrated medians are provisionally comparable across the `m65` and `d18` labels, but the fixed-grid LUT-stage/Level-1 check gives a median ratio near 0.0002 in both scenes. Appendix F documents later processing steps, so this comparison is incomplete. The official 2026 E1G2 LUT comparison gives median ratio 1.00375 and median per-band correlation 0.922; neither check is independent calibration validation. The official XML declares saturation radiance in µW/cm²/sr/µm and `dynamic_range` in counts. Applying those units flags nearly all valid E1G2 and E3G2 band-pixels, while almost no paired raw counts meet `dynamic_range`. The alternate mW comparison is counterfactual and differs by mode. Mask and numeric-scale gates remain open.
3. [x] Review published IIRS thermal methods and official mode validity. Prioritize E1G2 because the published thermal study used it and the official workbook marks bands 226–248 valid across 4504.1–4874.9 nm. This is mode selection evidence, not validation of the correction or mask.
4. [x] Verify the 2026-02-27 E1G2 raw/calibrated pair. Labels match on observation time, job ID, orbit, mode, dimensions, and wavelengths; both ZIP CRC and embedded QUB MD5 checks pass. The LUT comparison supports the calibrated unit scale internally. Independent validation and full-resolution geometry remain open.
5. [x] Stream the E1G2 raw and calibrated cubes, compare per-band values with the official radiance and dynamic-range fields, and inspect the sparse geometry grid. Save exact counts, sampled quantiles, and an explanatory figure. The LUT-stage comparison is numerically close to Level 1, but later pipeline steps are documented; threshold comparisons conflict and do not establish a mask.
   - [x] Compare both 2020 E3G2 raw/calibrated pairs with their official LUT on all 127 valid bands. LUT-stage values covary with Level 1 (median per-band correlations 0.898 for `m65`, 0.924 for `d18`) and their median Level-1/LUT-stage ratios are about 0.0002. The V6 guide says downstream destriping and radiance post-processing account for differences from direct LUT calculations, but the observed ratios have not been reproduced from these steps. See [E3G2 audit](../results/phase-1/m1-e3g2-lineage-check/summary.md).
6. Apply the official Appendix H `VALID` band table to spectral analyses. The V6 guide says calibrated values are mW, while the matched E1G2 label says µW. Direct XML-unit saturation comparisons flag nearly all valid-band radiances, while almost no paired raw counts meet `Dynamic_Range`; QUB labels declare no missing-value constant. These ambiguities remain unresolved. Do not make masks or apply an inferred correction. Use available alternatives with strict scope: (a) retrieve the official M³ candidate through a trusted PDS-listed endpoint, measure geolocated valid-pixel overlap, then compare spectral shape only after IIRS gates pass; this P1 is currently blocked because JPL TLS validation fails and the documented USGS PDS4 route returns 404; (b) select a separate Apollo 16 IIRS scene and implement the published RELAB 62231 empirical-line reflectance method; (c) compare E1G2 temperatures against matched Diviner/model values after units, masks, and geometry pass. None substitutes for resolving Level-1 data semantics. Register geometry against independent lunar controls with measured residuals.
   - Geometry validation path: the WAC 100 m/pixel crop and two-dimensional tie grid are recorded. The first WAC grid failed candidate relative-registration criteria (41 training, 17 held-out; median 2.236 px, p95 6.343 px). The SLDEM2015 illumination-matched hillshade diagnostic then passed all five candidate relative-registration criteria with 116 training and 34 held-out matches, median 0.375 px, p95 1.487 px, and RMSE 0.699 px. Nodata-intersecting patches are excluded. These are residuals against a training-fitted affine offset field, not surveyed absolute errors. A separate sparse-geometry candidate now contains the predicted corrected coordinates; neither the source geometry table nor IIRS product cube was changed. Absolute geometry remains provisional. See [WAC results](../results/phase-1/m1-wac-2d-grid/summary.md), [SLDEM results](../results/phase-1/m1-sldem-hillshade/summary.md), and [candidate correction](../results/phase-1/m1-sldem-correction-candidate/summary.md).
   - [x] Run an illumination-matched SLDEM2015 hillshade registration using fresh, fixed held-out line blocks. Azimuth direction and NCC cutoff were selected from training only. The run meets the candidate relative-registration limits; do not tune on its holdout. See [hillshade results](../results/phase-1/m1-sldem-hillshade/summary.md).
   - [x] Apply the training-fitted SLDEM offset field to a separate derived copy of the sparse geometry table; reproduce held-out tie residuals without refitting. Source geometry and cube are unchanged. Absolute geolocation remains provisional because the controls are morphology matches. See [candidate correction results](../results/phase-1/m1-sldem-correction-candidate/summary.md).
   - Reflectance comparison path identified: PDS ODE returned five M3 Level-2 footprint-intersection candidates for E1G2. Their labels report 304 x 85-band cubes, thermal correction flagged, and special pixel -999.0. Next assess IIRS/M3 common valid coverage using the available geolocation, then acquire the best candidate. Attempt spectral comparison only after IIRS mask, radiance, geometry, and reflectance gates pass. Match spatial support, wavelength response, and viewing/illumination geometry; do not call this a direct IIRS radiance calibration check.
   - Apollo 16 ground comparison in the 2025 IIRS Level-2 paper is outside the current E1G2 footprint (about 5.47°W–3.50°W). Treat it as a separate-scene acquisition path for reflectance scale validation, not a local target.
   - [x] Run a separate, fixed-line E1G2 sample probe of calibrated radiance versus the saturation table, paired raw counts versus `Dynamic_Range`, and paired LUT predictions. The sample reproduces the full-cube mismatch; its diagnostic flags do not assign a mask or close the semantics gate. See [sample record](../results/phase-1/m1-saturation-sample/summary.md).
   - [x] Compare official E1G2 LUT predictions at `Dynamic_Range` with the saturation table. This suggests a possible unit-label mismatch, but is not an official interpretation.
   - [x] Repeat the table-to-LUT comparison for E3G2. Its counterfactual mW ratio differs sharply from E1G2, so no single unit correction is supported.
   - [x] Compare actual raw-count distributions and LUT predictions with both E3G2 calibrated products. Preserve their different `m65`/`d18` product units. Full valid-band count scans and fixed-grid LUT comparisons are recorded in [the E3G2 audit](../results/phase-1/m1-e3g2-lineage-check/summary.md); the V6 guide attributes stage differences to downstream steps, but the measured ratio has not been reproduced.
7. Select additional independent tracks and provinces after footprints are reviewed. Do not begin 3 µm reflectance processing or M3 scoring until applicable quality gates pass.

## Phase 2 — M2 calibrated reflectance

- [x] One-scene E1G2 pilot (2026-10-10): apparent reflectance (median 0.098 at 1.5 µm), brightness temperature (median 327.8 K), and exploratory thermal removal. See [reflectance](../results/phase-1/m2-apparent-reflectance/summary.md) and [thermal](../results/phase-1/m2-thermal-brightness/summary.md).
- [x] Independent topographic test: IIRS temperature against SLDEM2015 local illumination, r = 0.877, held-out R² = 0.78. See [topographic validation](../results/phase-1/m2-topographic-validation/summary.md).
- [x] Compare temperatures with Diviner at matched local time (about 08:15). Done 2026-10-10 with the Diviner GCP: IIRS − bolometric median +5.0 K over 33 bins, r = 0.81. See `results/phase-1/m2-diviner-temperature/`.
- [ ] Validate absolute reflectance scale (M³ common pixels or Apollo 16 / RELAB 62231) and apply photometric correction with local incidence and emission angles.
- [ ] Re-run the 3 µm analysis with uncertainty propagation. The exploratory 2.9 µm band depth failed its quality gate.
- [ ] Export traceable analysis-ready patches.

**Status:** pilot in progress. Products are provisional; corrected reflectance is not validated.

## Phase 3 — M3 baselines

- [~] Physical and clustering references: E1G2 IBD 1 µm and 2 µm maps and k-means spectral units recorded (2026-10-10). Seed stability passes (ARI ≥ 0.95); the geographic block-split stability gate fails (ARI ≤ 0.60). See [spectral units](../results/phase-1/m3-spectral-units/summary.md).
- [ ] Review labels and freeze geographically independent splits.
- [x] Exploratory supervised baselines on proxy USGS labels with a frozen block split: random forest 0.50, 1D CNN 0.49, 64 px context random forest 0.63 macro F1. See [M3 supervised baselines](../results/phase-1/m3-supervised-baselines/summary.md).
- [ ] Report held-out metrics only on defensible labels, with uncertainty.

**Status:** unsupervised reference started on one scene; supervised work gated by labels and more scenes.

## Phase 4 — M4 Earth-to-Moon foundation-model transfer

- [x] Select and freeze the public HyperFree and HyperSIGMA checkpoints and record their licenses, input bands, preprocessing, and commit or release identifiers. See [model inventory](../results/phase-2/m4-transfer/model_inventory.md).
- [x] Exploratory (pre-gate) frozen linear probes on the M3 split: HyperSIGMA spatial 0.67, HyperFree 0.54; a context control at 0.63 shows no demonstrated pretraining gain. See [M4 summary](../results/phase-2/m4-transfer/summary.md).
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
