
## 2026-10-10 — M3 supervised baselines and exploratory M4 transfer

**Phase:** M3 baselines and M4 transfer (exploratory, pre-gate)
**Type:** Benchmark with saved metrics and figures

- Built proxy labels from the USGS Unified Geologic Map (1:5M): 5 groups, 2 km contact buffer.
- Frozen split: 250-line blocks (train, train, val, test), 25-line guards; a 64-line guard leakage control was also run.
- M3 macro F1: majority 0.10; band parameters 0.40; logistic regression 0.46; random forest 0.50; 1D CNN 0.49 (GPU); 64 px context random forest 0.63.
- M4 frozen linear probes: HyperFree 0.54; HyperSIGMA spatial 0.67; HyperSIGMA spectral 0.57. The context control explains most of HyperSIGMA's lead, so the pretraining gain is not demonstrated.
- Diviner GCP check: IIRS − Diviner bolometric +5.0 K median, profile r = 0.81.
- E3G2 LUT gap explained by exposure scaling (median ratio 0.944).
- Binned spectral-unit stability: 0.71, still below 0.8.
- The README was restructured into numbered sections with all figures; the tall browse strips were removed.

**Impact:** M3 and M4 have first exploratory scores. Labels remain proxy, and scene-level generalization is untested.

**Next:** **Recommended P1:** M³ files by manual download. P2: more E1G2 scenes. P3: photometric correction, then re-run M3/M4.

## 2026-10-10 — Diviner temperature comparison

**Phase:** M2 calibration pilot
**Type:** Analysis with saved metrics and figure

- Reference: Diviner Global Cumulative Product (LRO-L-DLRE-5-GCP-V1.0, Williams et al. 2017), four tiles from the PDS Geosciences Node, checksums recorded.
- Matched local time: 8.12–8.24 h, from the per-line subsolar point.
- IIRS − Diviner bolometric: median +5.0 K (IQR +3.4 to +7.1 K) over 33 latitude bins; +3.2 K with emissivity 1; profile r = 0.81. Diviner channel 3 − bolometric is +2.1 K, which implies a 4.7 µm roughness excess of 0 to about +12 K.
- Open: the offset is larger on dark units (+6.5 to +10.6 K) than on bright highland (+0.3 to +1.6 K).

**Impact:** The IIRS 4.7 µm temperature scale is consistent with Diviner at bin level. This is not an absolute radiance calibration.

**Next:** **Recommended P1:** Diviner RDR points near 08:10 to remove the local-time interpolation gap. P2: explain the albedo-dependent offset.

## 2026-10-10 — M2 physical pilot and M3 unsupervised reference

**Phase:** M2 calibration pilot and M3 reference baseline
**Type:** Analysis with saved metrics and figures

- Tested radiance units by physics (I/F and brightness temperature). The label unit is correct for all three local products: 2020 `m65` stores mW, while 2020 `d18` and 2026 E1G2 `d18` store µW. The V6 guide's general mW statement does not hold for `d18` products.
- E1G2 apparent reflectance: median 0.098 at 1.5 µm, and dark-to-bright contrast about 1.9×. Junction steps appear at 1.16, 1.30, 1.83, 1.99 and 3.4 µm.
- E1G2 brightness temperature (4.5–4.9 µm, ε = 0.95, reflected part removed): median 327.8 K, within about ±15 K of radiative equilibrium depending on the albedo law.
- Independent test: temperature against SLDEM2015 local illumination gives r = 0.877 and held-out R² = 0.784 on alternate 500-line blocks.
- Exploratory 2.9 µm band depth failed its quality gate (noise-dominated). No hydration claim is made.
- M3 unsupervised reference: k = 6 spectral units with seed ARI ≥ 0.95. The block-split stability gate fails (ARI ≤ 0.60). The darkest unit coincides with the Rimae Bode dark mantle deposit.
- New modules: `m2-radiance-unit-physics`, `m2-apparent-reflectance`, `m2-thermal-brightness`, `m2-topographic-validation`, and `m3-spectral-units`. New scripts: `build_e1g2_working_cube.py`, `run_e1g2_m2_physical_pilot.py`, `run_e1g2_topographic_validation.py`, `run_e1g2_m3_spectral_units.py`, and `run_e3g2_radiance_unit_physics.py`.

**Impact:** The unit-scale gate is closed on physical grounds. The mask/fill, absolute-scale, photometric and 3 µm gates remain open. README, task plan and module records are updated.

**Next:** **Recommended P1:** compare temperatures with Diviner at matched local time. P2: absolute reflectance scale (M³ or Apollo 16). P3: re-test spectral-unit stability on spatially binned spectra.

## 2026-10-10 — Exa review identifies alternative validation routes

**Phase:** M1 calibration and reference-data gate
**Type:** Primary-source literature and archive-access review

- Reviewed published IIRS/M³, IIRS Level-2 reflectance, and independent IIRS recalibration methods through Exa. Across the current and preceding Exa passes, 147 result slots were requested/reviewed; results overlap, so this is not a unique-source count.
- IIRS/M³ data normalized at 810 nm support spectral-shape comparison only. Apollo 16 plus RELAB 62231 gives a published absolute-reflectance method for a separate IIRS scene. Diviner temperatures matched by ground control points and acquisition time can check derived temperature, not IIRS radiance scale.
- The official PDS Imaging Node lists multiple M³ access sites. Try a PDS-listed endpoint for the current candidate and measure real valid-pixel coverage; do not bypass TLS validation.
- The user has already tried contacting the IIRS team without response; further outreach is not a project action.
- Saved source scope, limitations, and next gates in `results/phase-1/m1-gate-followup-20261010/`.

**Impact:** No M1 quality gate closed. The unit conflict, pixel mask/fill semantics, independent absolute radiance validation, and common M³ valid-pixel overlap remain open. No new metric or reflectance product was created.

**Next:** **Recommended P1:** retrieve the current M³ candidate from a trusted PDS-listed mirror and measure geolocated valid-pixel overlap. P2: search/acquire an Apollo 16 IIRS scene for the RELAB empirical-line path.

## 2026-10-10 — Retrieve the M³ candidate label through ODE

**Phase:** M1 reference-data access gate
**Type:** Official PDS metadata and product-file retrieval attempt

- Used the NASA PDS Geosciences Node ODE REST interface with `results=fl` for `M3G20090206T010833_V01_RFL`. The full Level-2 label and product-file inventory were returned inline.
- Confirmed 304 samples × 27,796 lines × 85 float32 bands, invalid constant -999.0, and the source location product `M3G20090206T010833_V03_LOC.IMG`. The RFL cube is listed as 2,700,001 KiB.
- The file inventory links the binaries to the JPL Imaging Node. Python and curl with default TLS validation reject its certificate chain. No bypass was used; RFL and LOC remain undownloaded.
- Saved concise metadata and file links in `results/phase-1/m1-gate-followup-20261010/m3_candidate_ode_metadata.json` and updated the M1 reference-data record.

**Impact:** P1 reached a binary-access block. ODE returned the label and file list; strict TLS fails at the JPL host, while the documented USGS PDS4 URL returns 404. Common valid-pixel overlap remains unmeasured. The sparse footprint count is only a candidate-ranking screen.

**Next:** Resume with both RFL and LOC when an official route validates or the archive files are available locally, then calculate actual geolocated valid-pixel overlap.

## 2026-10-08 — Official band-validity semantics and external code audit

**Phase:** M1 spectral quality and processing references
**Type:** SIS interpretation and public implementation review

- SIS V17 Appendix H clearly defines band validity: only `VALID` bands are valid; `SATURATION`, `OSF`, and `INVALID` are excluded. OSF is lower confidence; INVALID spectra are updated from neighboring bands except bands 1–5.
- The rule is band-level. It does not resolve per-pixel saturation, fill values, or the threshold mismatch.
- Audited CH2IIRS at commit `cd84557b67317aa70cfdd7aa552d701861dc1a7b`. The inspected thermal routines do not apply explicit per-pixel fill/saturation masks. Treat the repository as a method reference only, not ground truth for the archive.
- The SIS identifies the repeated `.oat`, `.oath`, `.lbr`, and `.spm` files as orbit/attitude, attitude-header, lunar-libration, and Sun-parameter data. These ancillary files do not provide pixel flags.
- Saved review at `results/phase-1/m1-processing-code-audit/`. No new metric, mask, or reflectance product was produced.

**Next:** Use Appendix H for band selection. Keep the pixel mask, radiance validation, and absolute geometry gates open.

# Updates

## 2026-10-10 — Refresh M1 provider-guidance and M³ candidate checks

**Phase:** M1 calibration and reference-data gate
**Type:** Public-source review and candidate metadata retrieval attempt

- Re-ran the PDS ODE footprint query. It returned the same five M³ Level-2 candidates; `M3G20090206T010833_V01_L2` remains top in the sparse geometry-node screen at 1,033/1,476 nodes (69.99%). This is not valid-pixel coverage.
- The current PRADAN FAQ still does not specify archived Level-1 saturation-mask or fill rules. Its contacts page lists IIRS payload contacts. A focused clarification request is recorded in the follow-up notes; no external message was sent.
- The PDS Imaging Node candidate-label request failed TLS verification because the server chain was self-signed. We did not bypass certificate verification. The candidate cube and actual overlap remain unchecked.
- The local LTA assembly instructions cover archive layout. The supplied V6 user guide was subsequently parsed and reviewed; see the 2026-10-10 guide update below.
- Saved source, method, observations, limits, and the next gate in `results/phase-1/m1-gate-followup-20261010/`.

**Impact:** No scientific gate closed. Do not create a pixel mask, radiance correction, or reflectance product from the current evidence. M2 remains gated.

**Historical next step (superseded):** The contact suggestion above is withdrawn because the user has already tried contacting the team without response. Current alternatives are recorded in the latest update above.

## 2026-10-10 — Supplied V6 guide clarifies processing stages and exposes unit conflict

**Phase:** M1 calibration gate
**Type:** Local primary documentation review

- Parsed the supplied 50-page V6 guide. Page 14 documents dark subtraction, LUT correction, destriping, radiance conversion, then keystone and radiance post-processing. It states that these later steps cause differences between direct raw/LUT calculations and archived calibrated values.
- This explains why the E3G2 audit compares different stages, but does not quantify the measured ratio or reproduce the processing. The exact ratio remains unvalidated.
- The guide says calibrated radiance values are stored in mW cm⁻² sr⁻¹ µm⁻¹; the matched E1G2 PDS4 label says µW cm⁻² sr⁻¹ µm⁻¹. The provider must resolve which unit describes the QUB values.
- The guide does not define per-pixel saturation or fill rules. No mask, corrected radiance, or reflectance was created.

**Next:** Ask the IIRS team to confirm the product unit and pixel validity/fill rules. See `results/phase-1/m1-gate-followup-20261010/`.

## 2026-10-08 — Apply the SLDEM relative geometry candidate

**Phase:** M1 geometry validation
**Type:** Derived geolocation candidate with held-out residual reproduction

- Evaluated the saved training-only affine offset field at each node of the sparse E1G2 geometry grid and sampled the original interpolated geometry at shifted image coordinates.
- Recomputed the 34 held-out image-tie residuals without fitting or tuning. They match the saved result within `1e-5` pixel: median 0.375 px, p95 1.487 px, RMSE 0.699 px.
- Candidate median absolute shifts are about 98.8 m east-west and 37.3 m north-south. The original ZIP and geometry were not changed.
- Saved script, candidate coordinate CSV, JSON values, SVG figure, and module records in `results/phase-1/m1-sldem-correction-candidate/`.

**Impact:** The held-out relative-registration result is reproducible after application to a separate sparse-coordinate candidate. Absolute geolocation remains provisional because the controls are morphology ties, not surveyed points.

**Next:** Compare against independent correction data or absolute controls. Keep radiance and pixel-mask gates separate.

## 2026-10-08 — Check public IIRS mask and fill guidance

**Phase:** M1 calibration and literature gate
**Type:** Source review; clarification gate remains failed

- Checked the official PRADAN IIRS FAQ and ISRO's public Chandrayaan-2 processing description. They point users to archive documentation and define the broad Level-1/Level-2 distinction, but do not specify saturation-mask application or cube fill encoding.
- Reviewed the primary LPSC 2025 IIRS recalibration abstract. It uses the ISRO LUT, saturation radiance, and CCD dynamic range to reconstruct radiance from linearized Level-0 counts. It reports differences from archived Level 1 and does not define the archived product's pixel mask or fill rules.
- Saved the source-backed findings and search record in `results/phase-1/m1-literature/`; updated `docs/gap_matrix.md`, `README.md`, and task records. No metric, figure, mask, or correction was produced.

**Impact:** Public-source review does not resolve the threshold mismatch or the absent fill constant. M2 reflectance remains blocked.

**Next:** Obtain authoritative processing guidance and an independent radiance reference. Preserve the separate geometry gate.

## 2026-10-08 — Test illumination-matched SLDEM2015 hillshade registration

**Phase:** M1 geometry validation
**Type:** Held-out relative-registration diagnostic

- Acquired local north/south SLDEM2015 tiles for the E1G2 footprint and generated hillshade using scene-level sun elevation and azimuth. The script tests both azimuth directions and selects from training scores only.
- Excluded tie patches that intersect DEM nodata or its one-pixel gradient boundary. With a fixed training-only score threshold, 34 held-out ties across five columns and four blocks have median residual 0.375 IIRS px, p95 1.487 px, and RMSE 0.699 px. The predeclared relative-registration candidate limits pass.
- Saved CSV, JSON, figure, script, and module records in `results/phase-1/m1-sldem-hillshade/`.

**Impact:** The hillshade provides a stronger relative-registration result than WAC for this scene. Residuals measure consistency with a training-fitted offset field, not absolute position error. Absolute geometry remains provisional; radiance and mask gates are unchanged.

**Next:** Compare corrected coordinates with the independent ISRO correction output or well-distributed controls, then measure valid M³ overlap within the IIRS footprint.

## 2026-10-08 — Full-resolution 2D WAC tie-grid test

**Phase:** M1 geometry validation
**Type:** Diagnostic and workflow setup

- Added a Python 3.11 research environment with range requirements and an exact tested lock.
- Implemented subpixel 2D gradient matching at five cross-track columns. The training-only score threshold and spatially held-out blocks prevent threshold selection from using held-out residuals.
- Evaluated 17 held-out ties across five columns and five spatial blocks. Median residual is 2.236 IIRS pixels, p95 is 6.343 pixels, and RMSE is 3.572 pixels. The candidate relative-registration criteria fail.
- Re-ran the saturation-table/LUT consistency diagnostic. It continues to support no inferred unit correction and no pixel mask.
- Saved per-tie values, summary metrics, and a figure in `results/phase-1/m1-wac-2d-grid/`.

**Why:** The earlier full-resolution tie set sampled only one cross-track column and could not assess cross-track behavior.

**Impact:** Geometry remains an open gate. WAC tie residuals are relative image-registration evidence, not absolute geolocation validation. Do not tune the model on this held-out set.

Meaningful project changes are recorded newest first. Entries describe the change and evidence; the Git history supplies the exact commit hash.

## 2026-10-03 — Audit both E3G2 raw/LUT/calibrated pairs

**Phase:** Phase 1, M1 product inventory
**Type:** Exploratory calibration-path audit

- Scanned all valid-band pixels in both matched 2020 E3G2 raw/calibrated pairs and compared fixed-grid raw-count LUT predictions with calibrated radiance using each label's unit.
- Only one raw count per scene reaches `Dynamic_Range`. The declared saturation field flags about 99.9988% of valid band-pixels; the counterfactual numeric-mW comparison flags none.
- The sampled LUT-stage and archived Level-1 values covary; median per-band Level-1/LUT-stage ratios are approximately 0.0002 in both scenes. The official guide says destriping and radiance post-processing follow the LUT, so this comparison omits documented steps. Saved machine-readable values and figure in `results/phase-1/m1-e3g2-lineage-check/`.
- No mask or correction was created. The magnitude difference after the documented pipeline stages remains unexplained.

**Why:** Test whether the cross-mode table/LUT discrepancy persists in actual matched E3G2 products.

**Impact:** This audit does not establish a calibration-scale error. Verify LUT indexing and reproduce downstream steps before interpreting the intermediate-to-Level-1 difference.

## 2026-10-03 — Correct interpretation of LUT-stage comparison

**Phase:** Phase 1, M1 product inventory
**Type:** Documentation correction

- Read Appendix F of the official archive SIS and the raw/calibrated processing description in the supplied Users Guide V6.
- The guide says the raw PDS product is dark-subtracted. Appendix F defines LUT output as radiance, then applies destriping and post-processing before Level 1. The E3G2 audit compared the LUT stage directly with final Level 1.
- Revised the result wording and figure labels to describe a stage-to-stage diagnostic. The ratio remains unexplained; it does not alone indicate a LUT error.

**Next:** The official archive contains no destriping coefficients. Use the matched E1G2 Level-1 radiance cube for a small spectral quality pilot, without assigning unverified masks. Keep fill, saturation, independent validation, and thermal-correction gates open.

## 2026-10-03 — Compare saturation table/LUT scale across modes

**Phase:** Phase 1, M1 product inventory
**Type:** Exploratory calibration-metadata diagnostic

- Compared the official LUT prediction at `Dynamic_Range` with saturation values for every valid band in E1G2 and E3G2. The XML files for both modes declare saturation radiance in µW.
- If the table numbers are treated counterfactually as mW, median LUT/saturation ratios are 1.559 for E1G2 and 5,118 for E3G2. This does not support one simple unit correction across modes.
- Saved per-band CSV, JSON, and a figure under `results/phase-1/m1-saturation-sample/`. No masks were created.

**Why:** Determine whether the apparent E1G2 unit-scale lead holds across modes.

**Impact:** The mode difference cautions against applying a single inferred correction. Next compare actual E3G2 raw counts and LUT predictions with the two calibrated products, retaining their different m65/d18 units. The scientific gate remains open.

## 2026-10-03 — Compare E1G2 saturation table with the calibration LUT

**Phase:** Phase 1, M1 product inventory
**Type:** Exploratory calibration-metadata diagnostic

- Applied the LUT at the official `Dynamic_Range` count for every sample-column coefficient in 222 valid E1G2 bands.
- Median predicted LUT radiance divided by the `Saturation` numeric value is 1.559 under a counterfactual mW interpretation (10th–90th percentile 1.028–1.856). Using the XML-declared µW value makes the ratio 1,000 times larger.
- Saved per-band CSV, JSON summary, and plot with a reproducible script in `results/phase-1/m1-saturation-sample/`.
- The scale relationship suggests a possible XML unit-label inconsistency, but it is not exact and does not authorize a Level-1 mask. The fill rule remains unknown.

**Why:** Use available official files to investigate the mismatch without waiting for a PRADAN or ISRO response.

**Impact:** Best next local step is to repeat the table-to-LUT check on available E3G2 pairs and mode tables. Saturation and fill gates remain open.

## 2026-10-03 — Probe E1G2 saturation fields on a small sample

**Phase:** Phase 1, M1 product inventory
**Type:** Exploratory data-quality sample

- Added and ran a reproducible fixed-line probe over 16 lines, every spatial sample, and all 222 E1G2-valid bands (888,000 band-pixel observations).
- The declared radiance threshold flags 97.8048% of sampled values; the paired raw-count comparison flags none at or above `Dynamic_Range`. The median per-band sampled calibrated/LUT ratio is 1.00139, with per-band values from 0.9060 to 1.0960.
- Saved per-band CSV, JSON summary, and PNG figure with method and limits in `results/phase-1/m1-saturation-sample/`.
- No mask or corrected product was created. The sample reproduces the full-cube mismatch but does not interpret table semantics or fill values.

**Why:** Check whether the full-cube threshold mismatch also appears in a small, spatially distributed sample before deciding whether to proceed.

**Impact:** The sample supports the mismatch finding. The official Level-1 masking and fill rules remain unresolved; the M2 gate remains open.

## 2026-10-03 — Extend the IIRS literature review to mask semantics

**Phase:** M1 literature review
**Type:** Targeted literature review

- Used Exa to search IIRS calibration, validation, and thermal-processing papers for saturation, dynamic-range, fill, and invalid-pixel conventions.
- Found that Laferriere and Bramson's LPSC 2025 abstract uses the ISRO LUT, saturation radiance, and CCD dynamic range to convert linearized Level-0 counts to radiance. Their reconstructed radiance differs from ISRO Level 1, partly because their pipeline omits order-sorting-filter adjustments and keystone correction.
- Found no reviewed paper that specifies IIRS Level-1 fill values or a per-pixel saturation mask. The 2023 calibration-validation abstract reports deep-space dark-offset correction, which is a separate issue from fill encoding.
- Updated the M1 literature records, gap matrix, scientific plan, task logs, and README. No metric, mask, or corrected product was created.

**Why:** Check whether published IIRS processing methods explain the mismatch between the official table fields and the paired E1G2 data.

**Impact:** The literature suggests that saturation radiance and dynamic range can serve together in a raw-count calibration path. It does not validate an interpretation of the local Level-1 thresholds. The M1 mask, fill, and radiance validation gates remain open.

## 2026-09-29 — Add a trackable research agenda to the guide

**Phase:** M1–M6 research roadmap
**Type:** Research planning and communication

- Added a status table with twelve work items, next actions, and the evidence needed to close each gate.
- Added a Mermaid dependency map that shows parallel M1 work and the gates before M2 reflectance, M3 baselines, and later transfer and science work.
- Added commands to reproduce the main completed radiance, mode-validity, and WAC registration checks.

**Why:** Show the work sequence and current blockers in a form that supports planning and progress review.

**Impact:** No scientific results or quality-gate statuses changed.

## 2026-09-29 — Consolidate the research guide into one project snapshot

**Phase:** M1–M3 project orientation
**Type:** Research communication

- Combined the overview, workflow, reproduction notes, and glossary into `research_guide/README.md`. Removed the separate guide pages.
- Added the research approach, stage status, next steps, figures, and Mermaid diagrams. Linked each result to its evidence and limitations.
- Explained how M1 data checks support M2 reflectance work, how M2 supports M3 baselines, and why model transfer waits until those stages pass.

**Why:** Keep the full project explanation in one readable place and show how current checks move toward the research question.

**Impact:** No data, measurements, metrics, or scientific quality-gate status changed.

## 2026-09-29 — Add a visual research guide

**Phase:** M1–M3 project orientation
**Type:** Research communication

- Reorganized `research_guide/` into short lessons that explain the research question, data checks, calibration cross-check, geometry review, and future model evaluation.
- Added plain-language Mermaid diagrams and existing project figures, with captions that state what each visual can and cannot show.
- Linked the guide to the detailed evidence records and the M1 Mermaid flowchart in the main README.

**Why:** Make the project's purpose, current evidence, and remaining gates easier to explain without hiding scientific uncertainty.

**Impact:** No science results, metrics, data products, or quality-gate status changed.

## 2026-09-29 — Match full-resolution E1G2 band 40 to WAC

**Phase:** M1 reference data
**Type:** Full-resolution geometry diagnostic

- Extracted calibrated band 40 at 1,369.6 nm from the E1G2 BSQ archive. The band is marked valid in the official mode table. A 1st-to-99th-percentile display stretch was used only for morphology matching.
- Used 30 accepted training image ties and 12 held-out ties in three along-track blocks. Held-out RMSE is 2.757 IIRS pixels (198.2 WAC projected map metres), with p95 5.317 pixels (382.7 projected map metres). Values and SVG are stored under `results/phase-1/m1-reference-data/metrics/` and `figures/`.
- Added reproducible extraction and registration scripts. Corrected pixel-scale conversion and recorded source image checksums and projection metadata.

**Why:** Check whether the preliminary browse-scale WAC registration holds at the full dimensions of an IIRS spectral image.

**Impact:** Full-resolution residuals are larger and variable. These image ties do not provide absolute surveyed geolocation accuracy. The geometry gate remains open. Radiance validation and pixel-mask gates are unchanged.

## 2026-09-29 — Compute a preliminary WAC-to-IIRS browse registration

**Phase:** M1 reference data
**Type:** Spatial registration diagnostic

- Used the E1G2 sparse longitude/latitude grid to geowarp the WAC crop into the official IIRS browse image. Matched x/y gradient patches; fit a robust along-track correction on 23 training ties and evaluated 8 held-out ties across two separated blocks.
- Held-out residual RMSE is 0.781 IIRS cube-pixel equivalents (57.4 WAC projected map metres), with 95th percentile 1.075 pixels (78.0 projected metres). Saved per-window CSV values, JSON metadata, and an SVG plot.
- Corrected the geometry grid description: the cube is 250 samples x 12,210 lines, with six sparse coordinate samples at each of 246 sampled scan lines.

**Why:** Obtain an initial external-image check of the E1G2 spatial geometry after acquiring the WAC crop.

**Impact:** This is a browse-scale image-consistency diagnostic, not surveyed absolute geolocation accuracy or radiometric validation. Full-resolution geometry remains open. The next step is tie matching on a full-resolution IIRS band with more spatially separated holdout regions.

## 2026-09-29 — Acquire footprint-sized LROC WAC crop

**Phase:** M1 reference data
**Type:** External geometry-reference acquisition

- Used HTTP byte-range requests to retrieve 164 tiles from `WAC_GLOBAL_O000N0000_100M.PYR.TIF`, assembling an 824 x 10,230 pixel grayscale crop at 100 m/pixel with a 20 km margin around projected E1G2 geometry.
- Fetched 10,747,904 tile bytes from the 1,617,959,634-byte source pyramid. The local crop is in ignored `data/reference/lroc_wac_e1g2/`; acquisition metadata and source version are recorded in `results/phase-1/m1-reference-data/wac_crop_metadata.json`.
- Added a rerunnable acquisition script and updated the README, task records, gap matrix, and reference-data module notes.

**Why:** Obtain the external image needed to measure E1G2 geolocation against held-out control points.

**Impact:** The crop was visually inspected, but no registration or residual was computed. It cannot validate radiometric calibration. IIRS mask and independent radiance gates remain open.

## 2026-09-29 — Rank M³ candidates with sparse geometry points

**Phase:** M1 reference data
**Type:** Spatial candidate-screening diagnostic

- Retrieved ODE footprint polygons and counted how many of the 1,476 E1G2 geometry coordinates fall inside each candidate footprint.
- The leading product footprint contains 1,033 points (69.99%). Saved source footprint metadata, a metrics CSV, SVG figure, and analysis script.
- Marked the result as a sparse-point screen, not a pixel-area or valid-pixel overlap fraction.

**Why:** Rank candidate M³ scenes before acquiring large reflectance cubes.

**Impact:** No M³ cube was downloaded; no radiance, reflectance, or model result changed. M2 remains gated.

## 2026-09-29 — Review M³ Level-2 candidate labels

**Phase:** M1 reference data
**Type:** Source metadata review

- Retrieved the five public PDS labels identified by the ODE footprint query.
- Recorded the 304 x 85 dimensions, line counts, thermal-correction flag, special-pixel value, and reflectance scale in `m3_label_review.csv`.
- Kept actual pixel overlap and product selection open. No M³ cubes or geolocation arrays were downloaded.

**Why:** Confirm candidate product contents before acquiring large reference cubes.

**Impact:** No radiance, reflectance, masks, or metrics changed. M2 remains gated.

## 2026-09-29 — Identify independent references for E1G2

**Phase:** M1 references
**Type:** Evidence-backed acquisition plan

- Added LROC WAC imagery as a geometry-reference candidate and specified held-out control-point residuals as the validation output.
- Queried PDS ODE for footprint intersection and saved five orbit-1080 M³ Level-2 candidates plus a rerunnable script. Their actual valid-pixel overlap remains to be checked.
- Kept M³ as a future reflectance comparator, gated on IIRS mask, radiance, geometry, and reflectance checks.
- Recorded that neither data source is local and no comparison has been computed. Clarified that Apollo 16 is outside the current E1G2 footprint.
- Added `results/phase-1/m1-reference-data/` with source, method, limitations, and next gate; updated README flowchart and gap matrix.

**Why:** Geometry validation and reflectance comparison answer different questions and must not be conflated.

**Impact:** No cube, mask, reflectance, or model metric changed. M2 remains gated.

## 2026-09-29 — Clarify IIRS saturation fields and geometry gate

**Phase:** Phase 1, M1 product and data quality

**Type:** Scientific metadata review and documentation

- Checked the official E1G2 saturation-table XML. It declares saturation radiance in µW/cm**2/sr/µm and dynamic range in counts. The mW comparison is counterfactual and is not the table's declared unit.
- Checked the calibrated QUB label. It has no missing-value constant, so it does not define a fill value.
- Checked the geometry product label. It declares 1,476 coordinate rows with pixel and line indices: six sample positions at each of 246 sampled scan lines across a 250-sample x 12,210-line image. The grid is sparse, and registration error remains unmeasured at this stage.
- Updated the M1 summary, task plan, gap matrix, project charter, data dictionary, and research logs. The mask, independent radiance, geometry-registration, and coverage gates remain open. M2 and M3 remain gated.

**Why:** Keep the known unit declarations separate from the unresolved mismatch and mask rules.

**Impact:** The M1 record no longer treats the saturation unit as ambiguous. It does not assign a pixel mask or report new scientific metrics.

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
