
## 2026-10-10 — M3 supervised and M4 exploratory benchmark

- Proxy USGS labels, frozen block split, 2 km buffer. M3 best per pixel: random forest 0.50; with 64 px context: 0.63. M4 HyperSIGMA spatial 0.67; HyperFree 0.54.
- Context and 64-line guard controls run. No leakage; pretraining gain not demonstrated.
- Records: `results/phase-1/m3-supervised-baselines/`, `results/phase-2/m4-transfer/`.

## 2026-10-10 — Diviner temperature comparison

- Downloaded four Diviner GCP tiles (10°S–30°N, about 625 MB) from the PDS Geosciences Node with verified TLS; MD5 values match the bundle manifest. Added `scripts/compare_e1g2_diviner_temperature.py` and the `m2-diviner-temperature` module. IIRS − Diviner bolometric: median +5.0 K over 33 bins, r = 0.81.

## 2026-10-10 — M2 pilot and M3 unsupervised reference

- Built an ignored E1G2 working cube (222 VALID bands), per-line OAT geometry, and per-pixel latitude/longitude from the SLDEM-corrected candidate grid.
- Radiance-unit physics test passed for all three products. The label unit is correct.
- Recorded E1G2 apparent reflectance, brightness temperature, exploratory thermal removal, SLDEM topographic validation (r = 0.877), and k-means spectral units. See the five new modules under `results/phase-1/`.
- Failed gates recorded: the 2.9 µm band depth, spectral-unit block-split stability, and IBD 2 µm signal-to-noise ratio.
- Next: Diviner temperature comparison; absolute reflectance scale; photometric correction.

## 2026-10-08 — Clarify official band validity and audit public processing code

- Read Appendix H of the official SIS V17. It explicitly states that only `VALID` bands are valid, while `SATURATION`, `OSF`, and `INVALID` bands are to be treated as invalid. OSF marks lower-confidence radiance; invalid spectral regions are updated from neighboring bands except bands 1–5. These instructions concern spectral bands, not individual pixel quality.
- Audited the public CH2IIRS thermal implementation at commit `cd84557b67317aa70cfdd7aa552d701861dc1a7b`. The inspected routines use all-band inputs and longwave bands near 4500–4874 nm, but do not implement explicit per-pixel fill or saturation masks. The code is a method reference, not archive authority.
- Confirmed the SIS names `.oat`, `.oath`, `.lbr`, and `.spm` as orbit/attitude, orbit/attitude header, lunar libration, and Sun-parameter ancillary data. These are not the sought pixel-quality mask.
- Saved the source/method review in `results/phase-1/m1-processing-code-audit/`. Existing mode values and figure remain in the inventory module; no metric, mask, or correction was created.
- Next: use Appendix H to define band selection, while keeping pixel masks, radiance validation, and absolute geometry as independent open gates.

# Progress

## 2026-10-10 — Retrieve M³ candidate through ODE

- Used the official PDS Geosciences Node ODE REST API as an alternate metadata route. It returned the full candidate PDS3 label and file inventory for `M3G20090206T010833_V01_RFL`.
- Confirmed dimensions 304 samples × 27,796 lines × 85 float32 bands, invalid constant -999.0, thermal-correction flag `Y`, and required source pixel-location file `M3G20090206T010833_V03_LOC.IMG`. The RFL cube is listed as 2,700,001 KiB.
- ODE's binary URLs resolve to the JPL Imaging Node. Both Python and curl with standard TLS validation reject its certificate chain. No bypass used; cube and LOC file are not downloaded. Actual valid-pixel overlap remains unmeasured.
- Exa found the documented USGS-hosted PDS4 M3 bundle route; requests to its root and candidate volume paths returned 404. NASA Open Data lists no downloadable resources. P1 is blocked until a valid official binary route or local archive files are available. See [the M1 gate follow-up](../results/phase-1/m1-gate-followup-20261010/summary.md).

## 2026-10-10 — Refresh the M1 clarification and M³ candidate checks

- Re-ran the PDS ODE footprint query. It returned the same five M³ L2 candidates; `M3G20090206T010833_V01_L2` remains the top sparse-grid candidate with 1,033/1,476 geometry nodes (69.99%). This is not a pixel-area or valid-pixel overlap result.
- Reviewed the official PRADAN FAQ; it refers users to the SIS and guide but does not resolve Level-1 saturation or fill semantics. User reports prior contact attempts received no response. Do not repeat outreach.
- Tried to fetch the top M³ label from the PDS Imaging Node. TLS verification failed on a self-signed certificate chain, so the label and cube were not retrieved and coverage remains unmeasured. No certificate checks were bypassed.
- Parsed the supplied V6 product guide (p. 14). It documents post-LUT destriping and radiance post-processing and attributes differences from direct LUT calculations to those steps; it does not quantify the local E3G2 ratio. It states calibrated units as mW, while the matched E1G2 label declares µW, leaving a factor-of-1000 unit conflict open.
- No scientific gate closed. No mask, radiance correction, reflectance, thermal result, or metric was produced. See `results/phase-1/m1-gate-followup-20261010/`.
- Next: use published/data-based alternatives and official PDS access sites, as recorded in the latest Exa review below. Keep M2 gated until radiance and mask evidence is sufficient.

## 2026-10-10 — Exa review of alternative M1 validation paths

- IIRS–M³ comparisons normalized at 810 nm support spectral-shape checks only. The 2025 Apollo 16/RELAB 62231 method is an absolute-reflectance route requiring a separate IIRS scene. Diviner temperatures matched by ground control points and acquisition time can check derived E1G2 temperature, not IIRS radiance units.
- The PDS Imaging Node index lists multiple official M³ access sites. Next data step is to try an official listed site for the current candidate and measure actual valid-pixel overlap.
- Replaced provider-contact action with these data-based alternatives. Unit conflict, pixel mask/fill semantics, and independent radiance scale remain open. No new metric or reflectance product was created.
- Evidence: [M1 alternative validation record](../results/phase-1/m1-gate-followup-20261010/summary.md).

## 2026-10-08 — Apply the SLDEM relative geometry candidate

- Applied the saved training-fitted affine offset model to a separate derived copy of the 1,476-node E1G2 sparse geometry grid. Source ZIP and original coordinates are unchanged.
- Recomputed the 34 held-out tie residuals without refitting. They reproduce the prior result within `1e-5` pixel: median 0.375 px, p95 1.487 px, RMSE 0.699 px.
- Predicted median absolute shifts are about 98.8 m east-west and 37.3 m north-south. Saved the coordinate CSV, JSON, SVG, script, and module records in `results/phase-1/m1-sldem-correction-candidate/`.
- This is a relative morphology registration result, not absolute geolocation validation. The ties are not surveyed controls. Radiance, saturation/fill, reflectance, and thermal gates remain open.
- Next: compare the candidate with independent absolute controls or an independently corrected IIRS geometry product before accepting coordinates.

## 2026-10-08 — Check public guidance on IIRS mask and fill rules

- Checked the public PRADAN IIRS FAQ, ISRO's Chandrayaan-2 processing description, and the primary LPSC 2025 abstract on IIRS Level-0 recalibration.
- The FAQ directs users to the SIS and product guide. ISRO describes Level 1 as radiance with geometric tagging. Neither public official source specifies the archived Level-1 saturation test or fill encoding.
- The LPSC abstract uses the LUT, saturation radiance, and detector dynamic range in a separate raw-count recalibration and reports differences from archived Level 1. It does not establish an official Level-1 mask or fill rule.
- Recorded the failed clarification gate and sources in the literature module, gap matrix, README, and task findings. No metric or figure was produced, and no mask or correction was assigned.
- Next: obtain authoritative processing guidance and an independent radiance reference. Keep M2 reflectance gated.

## 2026-10-08 — Reconcile the E3G2 audit checklist

- Confirmed that the planned comparison of raw-count distributions and LUT predictions against both 2020 E3G2 calibrated cubes was already completed and recorded with per-band CSV, JSON summary, and figure in `results/phase-1/m1-e3g2-lineage-check/`.
- Marked the corresponding M1 checklist item complete. This audit compares an intermediate LUT stage with Level 1; it does not reproduce downstream destriping/post-processing or validate radiance independently. No mask or reflectance was produced.
- The next calibration gate still requires an authoritative field interpretation, independent radiance validation, and a controlled downstream reconstruction if its coefficients are available. Absolute geometry also remains unvalidated; the SLDEM result is relative registration only.

## 2026-10-08 — Test E1G2 registration against an illumination-matched SLDEM2015 hillshade

- Downloaded the two official 512-pixel/degree SLDEM2015 tiles covering the E1G2 scene and saved them under ignored `data/reference/sldem2015_e1g2/`. Their sizes match the official tile index. Decoded signed elevations with Pillow; OpenCV's bundled JPEG2000 decoder rejected the signed component.
- Added `scripts/register_iirs_to_sldem_hillshade.py` and declared Pillow in the research requirements. The script uses scene-level IIRS sun angles, tests both azimuth directions, chooses the direction and score cutoff from training ties only, and fixes four held-out line blocks with 150-line guards.
- Added a DEM validity check after discovering 6,718 nodata cells in the local crop. Match patches touching nodata or its one-pixel gradient boundary are excluded. The selected run retained 116 of 155 training candidates and 34 of 40 held-out candidates.
- The clockwise-from-north hypothesis won on training NCC (median 0.626 versus 0.203). Held-out fit residual median is 0.375 IIRS px, p95 1.487 px, RMSE 0.699 px. All five predeclared relative-registration candidate criteria pass. This is not absolute geolocation validation; the tie fit uses the sparse IIRS geometry as its starting map and corrected coordinates have not been applied to an IIRS cube.
- Saved the reproducible script, CSV, JSON, SVG figure, and module summary/findings/notes under `results/phase-1/m1-sldem-hillshade/`. Updated README workflow, plan, project charter, and task records. Pillow 12.3.0 is in the exact dependency lock and is now an explicit requirement.
- Verification: Python bytecode compilation passes; see final diff/path checks before reporting. The result does not close radiance, saturation/fill, reflectance, thermal, or absolute-geometry gates.
- Next: use the independent ISRO correction output or well-distributed controls to check absolute geometry; separately measure valid M³ overlap inside the IIRS ribbon.

## 2026-10-08 — Run the first full-resolution 2D WAC tie grid

- Added `requirements-research.txt` and an exact-version lock, then created the ignored `.venv/` with Python 3.11.16, NumPy 2.2.6, OpenCV 4.14.0, and Matplotlib 3.11.2.
- Added a separate reproducible registration script so the earlier one-column script and artifacts remain unchanged. It tests five sample columns, 2D gradient matching with subpixel peak refinement, a score cutoff selected from training candidates only, and a robust affine offset fit on training blocks.
- Ran `.venv/bin/python scripts/register_iirs_to_wac_grid.py` on E1G2 band 40 and the existing WAC crop. It produced 245 candidate windows, 41 training matches, and 17 held-out matches across five cross-track columns and five spatial blocks.
- Held-out residual median is 2.236 IIRS pixels, p95 6.343 pixels, and RMSE 3.572 pixels. The candidate limits (median <= 1 px, p95 <= 2 px, and local-bin median <= 1.5 px) fail. The geometry gate remains open; do not tune against this holdout.
- A second run with the same inputs and environment reproduced the tie CSV and summary JSON byte-for-byte. The locked dependencies reinstall in `.venv/`, and the script passes Python bytecode compilation.
- Re-ran the saturation-table/LUT diagnostic successfully. Median LUT radiance divided by table value under counterfactual mW interpretation is 1.559 for E1G2 and 5,118 for E3G2. It assigns no mask and does not resolve field semantics.
- Saved CSV, JSON, SVG, and module records under `results/phase-1/m1-wac-2d-grid/`; updated the scientific plan, project status, README workflow, and results index.
- Next: test an illumination-matched hillshade or independent geometry tool with fresh validation controls. Continue to defer M³ pixel overlap until geometry and inputs are adequate; mask and independent-radiance gates also remain open.

## 2026-10-03 — Audit both E3G2 raw/LUT/calibrated pairs

- Scanned all pixels in 127 valid bands for the 2020 `m65` and `d18` raw/calibrated pairs; compared LUT output with calibrated radiance on a fixed grid, converting each product by its label unit.
- Only one raw count per scene reaches `Dynamic_Range`. The XML-declared saturation comparison flags 99.99885% (`m65`) and 99.99877% (`d18`) of valid band-pixels; treating the table numbers as mW flags none.
- The LUT-stage values track Level 1 variation, with median per-band Level-1/LUT-stage ratios 0.000200 and 0.0001999 and median correlations 0.898 and 0.924. Appendix F places destriping and radiance post-processing after the LUT, so this is an incomplete stage-to-stage comparison, not evidence of a LUT scale error.
- Saved exact per-band metrics, JSON summary, and figure in `results/phase-1/m1-e3g2-lineage-check/`. No mask or reflectance was produced.
- Follow-up: Appendix F confirms the raw archive is dark-subtracted, defines the LUT output as an intermediate radiance stage, then applies destriping and post-processing. No destriping coefficients are present in the local official archive. The measured Level-1/LUT-stage ratio is therefore unexplained, not evidence by itself of a LUT error.
- Next: run a small spectral quality pilot using the matched E1G2 Level-1 radiance cube, without assigning unverified masks. Keep thermal correction gated on fill/saturation semantics, independent radiance validation, and geometry review.

## 2026-10-03 — Probe saturation fields on a small E1G2 sample

- Sampled 16 scan lines spread across the E1G2 scene, all 250 samples, and all 222 valid bands (888,000 band-pixel observations).
- The saturation threshold as labeled flags 868,507 values (97.8048%); the paired raw count comparison flags zero values at or above `Dynamic_Range`. Raw sample values range 0–8,439.
- The median per-band sampled calibrated/LUT median ratio is 1.00139, with per-band ratios from 0.9060 to 1.0960. This is internal consistency only.
- Saved a reproducible per-band CSV, JSON summary, and figure in `results/phase-1/m1-saturation-sample/`. No mask or reflectance was produced.
- The small sample reproduces the mismatch; it does not establish the field semantics or fill rule. Next: obtain official clarification before creating masks or continuing to M2.

## 2026-10-03 — Check official saturation tables against the LUT by mode

- Applied E1G2 and E3G2 LUTs at each mode-valid band's `Dynamic_Range` count across all 250 sample positions. The median LUT radiance divided by the saturation number is 1.559 for E1G2 and 5,118 for E3G2 if those numbers are treated counterfactually as mW. Both XML files declare µW.
- The mode difference argues against one simple inferred unit correction. This internal table comparison does not establish official field semantics.
- Saved reproducible per-band values, JSON, plot, and limitations in `results/phase-1/m1-saturation-sample/`.
- Next best local action: compare actual raw-count distributions and LUT predictions with the available E3G2 calibrated cubes, preserving m65/d18 units. Keep fill and Level-1 pixel masks unresolved.

## 2026-10-03 — Check papers on IIRS saturation and fill semantics

- Used Exa to search IIRS instrument, thermal-correction, calibration-validation, and reflectance-processing papers for saturation, dynamic-range, fill, and invalid-pixel rules.
- Found a relevant LPSC 2025 abstract. Laferriere and Bramson use the ISRO LUT, saturation radiance, and CCD dynamic range to convert linearized Level-0 counts to radiance. Their reconstructed radiance differs from ISRO Level 1, partly because they omit order-sorting-filter adjustments and keystone correction.
- The 2020 instrument paper covers lab saturation-radiance characterization. A 2023 IIRS calibration-validation abstract reports deep-space dark-offset correction. The papers reviewed do not define archived Level-1 fill values or per-pixel saturation masks.
- Recorded the source-backed findings in the M1 literature module, task findings, gap matrix, scientific plan, and README. No metrics or masks were generated. The scientific quality gates remain open.
- Next: ask the IIRS team to clarify field application, fill values, and pixel validity. Do not infer a mask from the published recalibration method.

## 2026-10-01 — Review full-resolution WAC tie confidence

- Audited the existing E1G2 band-40 held-out tie rows. All 12 accepted held-out ties have gradient NCC scores from 0.206 to 0.320 (median 0.258); five residuals exceed 2 IIRS pixels and two exceed 3 pixels, with a maximum of 7.021 pixels.
- Similar NCC scores accompany both small and large residuals. The current acceptance threshold is not a reliable confidence filter. Three blocks contribute four ties each, but these remain image matches, not absolute control points.
- Updated the M1 reference-data findings, summary, and README. Geometry remains provisional; WAC does not validate radiance, and M1 mask/radiance gates remain open.
- Next: acquire or identify independent, well-distributed geometry controls, and obtain authoritative guidance on saturation, dynamic-range, and fill semantics before correction work.

## 2026-09-29 — Acquire WAC reference crop for E1G2 geometry

- Retrieved `WAC_GLOBAL_O000N0000_100M.PYR.TIF` metadata and 164 tiled image regions through HTTP byte ranges. Transferred 10,747,904 raster bytes from the 1,617,959,634-byte pyramid and assembled an 824 x 10,230 8-bit crop at 100 m/pixel with 20 km margin around projected IIRS control coordinates.
- Corrected the E1G2 geometry description: the image is 250 samples x 12,210 lines. Its 1,476 coordinate records cover six sample positions at each of 246 sampled scan lines spanning the image, not 246 of 250 lines.
- The source version, ETag, retrieval time, crop origin, TIFF scale/tiepoint, and projection assumption are saved in `results/phase-1/m1-reference-data/wac_crop_metadata.json`. The crop is under ignored `data/reference/lroc_wac_e1g2/`; the acquisition can be rerun with `scripts/fetch_wac_reference_crop.py`.
- Visually inspected a temporary preview. No registration, held-out residual, or calibration validation was performed. The WAC crop is only a spatial reference.
- Next: register the sparse IIRS geometry to the WAC crop using documented training controls, then quantify held-out residuals in metres and IIRS pixels. Keep M1 mask and independent radiance gates open.

## 2026-09-29 — Compare the E1G2 browse image with WAC

- Interpolated the IIRS sparse geometry grid and used it to warp the LROC WAC crop into the official 175 x 8,547 browse image. Matched local x/y image gradients; 23 accepted tie windows trained a robust linear along-track offset correction.
- Held out windows in two separated 1,000-line blocks. Eight accepted ties produced a residual RMSE of 0.781 IIRS cube-pixel equivalents (57.4 WAC projected metres), with 95th percentile 1.075 pixels (78.0 projected metres). Saved per-patch CSV, metric JSON, and SVG figure under `results/phase-1/m1-reference-data/`.
- This is provisional browse-scale image consistency, not surveyed absolute geolocation error. The lower-resolution browse and only two held-out spatial blocks are insufficient to close the geometry gate. The metric does not validate IIRS radiance.
- Next: match confidence needs review, and absolute controls are needed before accepting geometry. Preserve mask and independent radiance blockers.

## 2026-09-29 — Match full-resolution E1G2 band 40 to WAC

- Extracted official E1G2 band 40 (1,369.6 nm, valid in the local mode table) from the calibrated archive without extracting the full cube. A 1st-to-99th-percentile display stretch was used only for morphology matching. The generated image and extraction metadata remain under ignored `data/reference/lroc_wac_e1g2/`.
- Repeated the WAC geowarp and image-tie fit at 250 x 12,210 resolution. Used 30 accepted training ties and 12 held-out ties across three spatial blocks. Held-out RMSE is 2.757 IIRS pixels (198.2 WAC projected map metres); p95 is 5.317 pixels (382.7 projected map metres).
- The full-resolution residuals are larger than the browse-scale result and include several large tie errors. This does not establish absolute geolocation accuracy. The geometry gate remains open. Per-tie values, metric metadata, and figure are saved in `results/phase-1/m1-reference-data/`.
- Next: review match confidence, improve held-out control coverage, and seek independent absolute controls. Radiance scale, masks, and reflectance gates remain separate.

## 2026-09-29 — Screen M³ footprints against sparse E1G2 geometry

- Saved PDS ODE product-footprint WKT for the five M³ candidates. Compared those footprints with the 1,476 IIRS geometry-table coordinates from the matched calibrated archive.
- `M3G20090206T010833_V01_L2` contains 1,033 IIRS control points (69.99%), highest among the five. Other counts are 703 (47.63%), 259 (17.55%), 5 (0.34%), and 0. Values and SVG plot are saved in `results/phase-1/m1-reference-data/metrics/` and `figures/`.
- This is a sparse geometry-point screen only. It does not measure areal or valid-pixel overlap. No M³ data cube was downloaded and no reflectance comparison was run.
- Next: inspect per-pixel location and special-pixel behavior for the top candidate, estimate a spatially matched sample, then download only the needed M³ product/area. M1 mask and radiance validation gates remain open.

## 2026-09-29 — Review M³ Level-2 candidate labels

- Retrieved the five PDS M³ labels returned by the footprint-intersection search. All describe 304-sample, 85-band Level-2 reflectance cubes, with thermal correction flagged and -999.0 listed as the special-pixel value. Stored IDs, timestamps, dimensions, and label URLs in `results/phase-1/m1-reference-data/m3_label_review.csv`.
- Candidate scene lengths vary from 9,310 to 27,796 lines. The shortest cube is not selected based on size alone because the amount of usable overlap is not known.
- No image cubes or geolocation arrays were acquired, and no spectral comparison was performed. The label review establishes product metadata only.
- Next: compare the E1G2 sparse geometry with M³ pixel-location data, inspect valid pixels for shared support, and estimate which small candidate is useful before downloading its full cube. Keep IIRS radiance and mask blockers active.

## 2026-09-29 — Define independent geometry and reflectance reference paths

- Identified LROC WAC global imagery at 100 m/pixel as an external geometry reference candidate for the low-latitude E1G2 footprint. The operational next step is a footprint-sized acquisition, documented control-point registration, and residual measurement on held-out points. This can test geolocation, not radiometric calibration.
- Queried PDS ODE for M³ Level-2 footprint intersections with E1G2 bounds. Five orbit-1080 candidates were returned; metadata and label review are saved in `results/phase-1/m1-reference-data/`. Sparse control-grid coverage ranks one product first, while per-pixel valid overlap remains unchecked.
- No reference imagery was acquired. No image registration, validated common pixel area, reflectance comparison, metrics, or figures were produced. Planning record: `results/phase-1/m1-reference-data/`.
- The Apollo 16 site used in the 2025 Level-2 paper is outside this E1G2 scene footprint, so that paper's ground comparison is not a local calibration target.
- Next: inspect the five M³ candidate labels and select valid common coverage; acquire a cropped WAC reference; separately seek authoritative mask/radiance guidance and independent calibration evidence. Compare M³ spectra only after IIRS reflectance gates pass.

## 2026-09-29 — Recheck saturation, fill, and geometry metadata

- Read the official E1G2 saturation-table XML and calibrated-product labels from the already verified archive. The table unit declarations are explicit: `Saturation` is `µW/cm**2/sr/µm` and `Dynamic_Range` is `count`. The previous alternate mW calculation is counterfactual only. It does not resolve why 99.878921% of valid-band radiance values meet the declared threshold while zero raw counts meet the dynamic-range values.
- The calibrated QUB label has no `Special_Constants` or missing-value constant. This leaves pixel fill and validity rules unresolved; do not classify zeros or other values as fill.
- The geometry label declares a 1,476-row table with longitude, latitude, pixel, and line fields. The 250-sample x 12,210-line image has six geometry samples at each of 246 sampled scan lines spanning lines 0–12,209. It is a sparse control grid, not full per-pixel geometry.
- Updated the E1G2 module record, data dictionary, task plan, README workflow, and scientific plan to distinguish known units from unresolved field application. M1 remains open; reflectance and thermal processing remain blocked.
- Next: obtain authoritative clarification of the saturation and fill rules, independently validate radiance, register the strip against an independent lunar reference with residuals, and review candidate independent tracks before fixing any geographic split.

## 2026-09-28 — Audit E1G2 radiance values, thresholds, and footprint

- Added a reproducible streamed audit of the matching E1G2 raw and calibrated cubes. It scanned all 781,440,000 calibrated values without extracting either QUB from its archive.
- All values are finite. The 222 officially valid bands contain 4,829 zero and 42,081 negative band-pixels. Sampled positive medians span 118.218–1,305.46 µW/cm²/sr/µm.
- Found a threshold conflict: the saturation CSV labels its threshold in µW, which 99.878921% of valid-band values meet or exceed. If threshold values are interpreted as mW, only 12 exceed. Paired raw counts do not reach the table's dynamic-range field. None of these comparisons defines a mask. The official LUT comparison supports internal radiance-scale consistency: after converting product values from µW to mW, the median calibrated/LUT ratio is 1.00375 and median per-band correlation is 0.922. This does not replace independent calibration validation.
- The sparse geometry grid covers approximately 5.47°W–3.50°W and 6.53°S–26.86°N. It shows a low-latitude strip but is not a full-resolution footprint.
- Saved per-band QA values and the radiance/LUT/threshold/geometry figure under `results/phase-1/m1-e1g2-scene/`. The README now has an M1 breakdown table, evidence links, and a glossary for E1G2 and other product terms. Its Mermaid LR chart traces all three pairs through the QA outputs and remaining M2/M3 gates.
- Next: obtain authoritative interpretation of saturation, dynamic-range, and fill fields. Define documented per-pixel validity rules, validate the radiance scale independently, and review full-resolution geometry. Keep thermal correction blocked.

## 2026-09-28 — Verify the matched E1G2 raw/calibrated pair

- Refreshed PRADAN access and downloaded only `ch2_iir_nci_20260227T1239538758_d_img_d18.zip`, alongside the previously acquired matching raw NRI ZIP. Other files from the bulk selection were not downloaded.
- Both ZIP archives passed CRC checks. The raw and calibrated PDS4 labels match on observation start/stop, job ID, imaging orbit 29042, dumping orbit 29043, exposure e1, gain g2, 12,210 × 250 × 256 axes, and all band centers.
- Streamed each QUB directly from its ZIP. Both actual MD5 values match the values in their PDS4 labels. No cube was extracted to disk.
- The calibrated label declares `µW/cm**2/sr/µm`. This scale has not been validated against numeric samples or independent references. Geometry, saturation units, and pixel masks remain open.
- Extracted and reviewed the official calibrated browse PNG, then embedded it in the README with a limitation caption.
- Updated the M1 acquisition record, README LR flow, and project status. No reflectance, correction, or metric was produced.

## 2026-09-28 — Inspect candidate E1G2 raw product label

- Selected the matching 2026-02-27 raw and calibrated product IDs from the PRADAN-generated list without running the bulk downloader.
- Downloaded only the raw NRI ZIP to ignored `data/pradan/e1g2_candidate_20260227T1239538758/`. Its ZIP CRC passed. The XML label confirms start time `2026-02-27T12:39:53.8758Z`, exposure `e1`, and gain `g2`.
- Requested the matching calibrated NCI ZIP. PRADAN returned HTTP 302 to sign-in, so the calibrated file was not saved and the pair is not yet verified.
- Next: regenerate a PRADAN script selecting only the calibrated product after refreshing the session, then validate its XML, pair fields, units, footprint, and archive checksum.

## 2026-09-28 — Read supplied IIRS PDS4 User Guide text

- Reviewed the user-supplied V6 guide text. It defines raw `nri` and calibrated `nci` products, confirms that the filename timestamp is the observation start time, and defines `d18` as a station ID, not an exposure/gain mode.
- The guide gives a Level 1 radiance to apparent-reflectance formula and warns users about longwave thermal emission. It does not identify the selected scene's exposure/gain or resolve the saturation-table units and fill mask.
- This supports checking the product XML for `exposure=e1` and `gain=g2`; the selected candidate raw label passes that check.

## 2026-09-28 — Review IIRS thermal and reflectance literature

- Reviewed primary IIRS papers from 2022, 2024, 2025, and 2026, the official PRADAN FAQ, and a public IIRS processing implementation.
- The 2022 thermal paper used E1G2. The official workbook confirms E1G2 bands 226–248 span 4504.1–4874.9 nm, so E1G2 is now the preferred mode for the thermal pilot.
- A 2026 sensitivity paper reports that a 4 K temperature difference can cause a 14.39% reflectance difference at 3156 nm. This makes temperature uncertainty a required M2 output.
- Created an initial cited gap matrix and documented the targeted review under `results/phase-1/m1-literature/`.
- A public map of PRADAN exposed the FAQ and contacts pages but no product listing. The FAQ describes raw and calibrated products and directs users to the product guide. The authenticated browse/data-table path is still needed to select a scene.
- Next: acquire a matched E1G2 raw/calibrated pair from PRADAN, inspect its geometry and footprint, and resolve the saturation-table unit and per-pixel mask before reflectance processing.

## 2026-09-28 — Scan calibrated pilot radiance cubes

- Scanned every pixel in all 256 bands of the `m65` and `d18` calibrated cubes. Saved exact per-band finite, zero, negative, positive, and candidate saturation-threshold counts plus sampled quantiles in `results/phase-1/m1-inventory/metrics/pilot_radiance_quality_by_band.csv`; saved the plot alongside it.
- After applying each PDS4 unit prefix, sampled median ranges are comparable between the scenes. This supports the declared scale provisionally but does not independently validate radiometric calibration.
- Recorded a failed saturation-unit gate: the saturation XML's µW interpretation flags nearly all positive pixels, while the SIS's general mW interpretation flags none. No saturation mask was created, and zero values remain unclassified.
- Next: obtain authoritative clarification of the table units and pixel validity, identify a thermal-capable observation or validate another thermal method, then select nonoverlapping tracks before M2/M3.

## 2026-09-28 — Display the two active pilot strips

- Verified the official calibrated-product browse PNGs against their PDS4 MD5 values.
- Generated full-coverage, four-part preview figures for `m65` and `d18`, and embedded both in the README with source and interpretation limits.
- Kept the original browse files and scene archives ignored; only the derived figures and generation script are tracked.

## 2026-09-28 — Official IIRS archive inspected

- Received `data/pradan/iir.zip`, verified all ZIP entries, and recorded SHA-256 `5afe64c3efe445e6d0334e8a374756ecab45698494dcee0d19616bf5dcb80720`. The archive contains the 149-page SIS V17, LUTs, saturation tables, solar flux, and band-validity workbook. The separate user guide is absent.
- The SIS confirms Level 1 calibrated radiance and places thermal and photometric correction in Level 2 processing. Both pilots are `E3G2`; the official mask has no valid 4–5 µm bands for that mode.
- Saved source band flags in `results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv` and a plot in `figures/band_validity_by_mode.svg`.
- Next work: validate each cube's unit scale and pixel masks, then assess a suitable mode or method for thermal correction. No reflectance claim was made.

## 2026-09-28 — M1 pilot dictionary and guide access check

- Corrected the M1 summary to reflect completed extraction, integrity checks, and XML pairing.
- Added a provisional data dictionary from the four active PDS4 labels. Both calibrated labels call their cubes radiance spectral images; their declared units differ by a factor of 1000 in prefix.
- Confirmed the official `iir.zip` guide/SIS is listed by the PRADAN IIRS FAQ, while its `Other Downloads` page redirects unauthenticated requests to ISSDC sign-in. No guide-based calibration, fill, saturation, or band-validity claim was made.
- Next work: obtain the guide through authorized access, validate the unit conventions and representative values, then select independent scenes. M2 correction remains gated.

## 2026-09-28 — Local tooling removed from Git

- Kept `.agents/skills` and `.codex` on disk while removing them from Git tracking.
- Added ignore rules and corrected the setup guide to show these are local-only files.

## 2026-09-28 — Codex setup

- Adapted the supplied project workflow to Codex's local instruction, skill, hook, and custom-agent locations.
- Created a charter, current task plan, findings, lessons, changelog, error registry, improvement ledger, research prompt, and observation checklist.
- Kept `AGENTS.md` and `codex.md` local and ignored. Added a Git commit-message check for the no-co-author rule.
- Next work: create and verify an M1 manifest for the four raw scenes, then obtain the official IIRS product guide and calibrated counterparts.

## 2026-09-28 — Research result protocol

- Added a phase and module result structure under `results/`.
- Required concise summaries, findings, and notes for every module.
- Required machine-readable metric values plus PNG or SVG figures whenever metrics or graphs are produced.
- No metric figures were created because M1 inventory metrics have not yet been computed.
- Active next step: finish the M1 manifest and integrity checks for the four local scenes.
- M1 manifest and integrity verification completed for all four local scenes. The next M1 unit is product-guide and calibrated-counterpart identification, followed by acquisition of independent scenes.
- The supplied PRADAN URL list was checked before download. It contains no exact timestamp match for the four raw scenes; the interrupted partial transfer was removed. A new PRADAN selection is required.
- HyperFree and HyperSIGMA are now explicitly scheduled for Phase 4 (M4), after the M1–M3 quality gates. M5 adaptation and M6 scientific tasks follow reproducible M4 transfer results.
- Replaced the old `data/` contents with four selected pilot archives: raw and calibrated pairs for `20200208T1245274109_d_img_d18` and `20200208T0057589143_d_img_m65`. All four downloads completed and passed Python ZIP integrity checks. Next: extract and inspect their XML labels.
- Extracted all four pilot archives and regenerated the active manifest. Both raw-to-calibrated pairs match on timestamp, job ID, orbit, dimensions, and wavelengths. The calibrated unit strings differ by product and are now recorded as an M2 conversion gate.

## Earlier work

- Researched M1–M3, documented scientific gates in `docs/m1_m3_plan.md`, and inventoried four raw IIRS strips.
- Extracted all four ZIP archives locally and checked the expected file counts and sizes.
- Pushed the initial documentation to `main`; mission data remain untracked.
