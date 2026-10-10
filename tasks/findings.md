
## 2026-10-08 — SIS band rules are explicit; pixel mask still unresolved

- SIS V17 Appendix H (pp. 115–126) states that only bands tagged `VALID` are valid. `SATURATION`, `OSF`, and `INVALID` bands must be treated as invalid. The SIS says OSF bands have lower-confidence radiance and invalid bands are updated from neighboring bands except bands 1–5.
- This resolves mode-specific spectral band selection: 222 bands are valid in E1G2, including 226–248 at 4504.1–4874.9 nm; 127 are valid in E3G2. It does not provide a per-pixel mask.
- The inspected public CH2IIRS thermal routines at commit `cd84557b67317aa70cfdd7aa552d701861dc1a7b` contain no explicit per-pixel fill/saturation mask. This is only an implementation audit and cannot prove the absence of provider-side mask data.
- SIS product descriptions identify `.oat`, `.oath`, `.lbr`, and `.spm` as orbit/attitude, header, libration-angle, and Sun-parameter ancillary products; they do not supply pixel flags.
- Record: `results/phase-1/m1-processing-code-audit/`. Continue to keep pixel validity, radiance validation, and geometry as separate gates.
# Findings

## 2026-10-10 — M³ candidate binary access remains blocked

- ODE returns the selected Level-2 label and file list, but the JPL host rejects strict TLS validation in this environment. The documented USGS PDS4 bundle root and probed volume paths return 404; NASA Open Data has no downloadable resources.
- The binary RFL cube and referenced LOC image were not retrieved. Actual common valid-pixel overlap remains unknown; do not substitute sparse-footprint coverage.
- Record and source links: `results/phase-1/m1-gate-followup-20261010/`.

## 2026-10-08 — Apply SLDEM relative correction candidate

- Applied the training-fitted offset field to a separate copy of the 1,476-node E1G2 sparse geometry grid. The source archive and cube are unchanged.
- Recomputed the saved 34 held-out residuals from observed offsets and model coefficients without refitting. Median residual 0.375 px, p95 1.487 px, and RMSE 0.699 px reproduce within `1e-5` pixel.
- Candidate median absolute shifts are approximately 98.8 m east-west and 37.3 m north-south. This is a relative correction candidate, not surveyed geolocation accuracy.
- See [`m1-sldem-correction-candidate`](../results/phase-1/m1-sldem-correction-candidate/summary.md). Next compare against independent correction data or absolute controls. No radiance, mask, or reflectance gate was closed.

## 2026-10-08 — SLDEM2015 hillshade registration

- A training-selected sun-azimuth direction and five-column tie grid improved local image-match consistency relative to the WAC grid. The selected clockwise-from-north hillshade scored median training NCC 0.626; the reverse direction scored 0.203.
- After excluding nodata-intersecting patches, 34 held-out ties across four fixed line blocks and five cross-track columns have median affine-model residual 0.375 IIRS px, p95 1.487 px, and RMSE 0.699 px. The predeclared relative-registration candidate rule passes.
- This residual tests held-out tie offsets against a training-fitted affine field. Sparse IIRS coordinates initialized the DEM mapping, and there are no surveyed controls in this run. Do not interpret the pass as absolute geolocation accuracy; corrected coordinates have not been applied to downstream products.
- Complete evidence and limits are in `results/phase-1/m1-sldem-hillshade/`.

## 2026-10-08 — 2D WAC tie-grid diagnostic

- Installed the minimal image-analysis stack in ignored `.venv/`; exact versions are in `requirements-research.lock`.
- Implemented a separate five-column subpixel tie-grid run on E1G2 band 40 against the current WAC crop. The score cutoff is the training-candidate 25th percentile and was applied unchanged to held-out ties.
- The run retained 41 training and 17 held-out ties across five columns and five held-out spatial blocks. Held-out median residual is 2.236 IIRS pixels, p95 6.343 pixels, and RMSE 3.572 pixels. The candidate limits fail.
- The worst approximate 10 km line-bin median with at least three ties is 5.619 pixels. Do not tune the model against these held-out ties.
- These are relative WAC morphology matches. Absolute geometry, saturation/fill masks, independent radiance scale, and M³ valid-pixel overlap remain open.
- Evidence: [`m1-wac-2d-grid`](../results/phase-1/m1-wac-2d-grid/summary.md).

## 2026-10-03 — Paired E3G2 LUT-stage comparison

- Compared both 2020 E3G2 raw/calibrated pairs on all 127 valid bands. Applied each product's declared unit prefix before comparison with LUT radiance interpreted in mW from the SIS.
- Only one raw count per scene meets its `Dynamic_Range` value. Reading the saturation field as declared µW flags 99.9988% of valid-band pixels in each cube; the counterfactual mW threshold flags none.
- Median per-band Level-1/LUT-stage ratios are about 0.0002 for both scenes, while median per-band correlations are 0.898 (`m65`) and 0.924 (`d18`). Appendix F documents destriping and radiance post-processing after the LUT, so the comparison omits downstream steps.
- The V6 user guide states that destriping and radiance post-processing follow the LUT and attributes differences from direct raw/LUT calculations to those steps. It does not quantify the observed ratio of about 0.0002, so the exact magnitude remains unreproduced. This does not by itself indicate a LUT-scale error. No mask was created. See the [audit record](../results/phase-1/m1-e3g2-lineage-check/summary.md) and [2026-10-10 follow-up](../results/phase-1/m1-gate-followup-20261010/summary.md).

## 2026-10-03 — Small E1G2 sample reproduces threshold mismatch

- Probed 16 scan lines across the 2026 E1G2 strip, all 250 samples, and all 222 mode-valid bands (888,000 band-pixel observations).
- 868,507 sample radiances (97.8048%) meet the table's declared saturation threshold. No sampled raw counts reach `Dynamic_Range`; the raw-count range is 0–8,439.
- The median per-band sampled calibrated/LUT ratio is 1.00139, while per-band ratios range 0.9060–1.0960. Aggregate agreement conceals band-level variation.
- This reproduces the full-cube mismatch but does not tell us whether those table fields define Level-1 saturation or how fill is encoded. No mask was made. See the [sample record](../results/phase-1/m1-saturation-sample/summary.md).

## 2026-10-03 — Table-to-LUT check suggests a unit-label lead

- Applied the official LUT gain/offset at the official E1G2 `Dynamic_Range` count for every sample column and valid band. The median predicted LUT radiance divided by the `Saturation` number is 1.559 when the number is treated counterfactually as mW (10th–90th percentile 1.028–1.856); under the XML-declared µW conversion the ratio is 1,000 times larger.
- E3G2 has a very different median ratio under the same counterfactual reading: 5,118 (10th–90th percentile 1,029–8,993). Both XML labels declare µW. The mode difference does not support one simple unit correction.
- This remains an internal metadata comparison, not proof of a unit-label error or a Level-1 mask. Best next local check: compare actual raw-count distributions and LUT predictions with the two calibrated E3G2 products, retaining their distinct m65/d18 units. See the [saved metrics and limits](../results/phase-1/m1-saturation-sample/summary.md).

## 2026-10-08 — Public official guidance does not resolve IIRS mask semantics

- The public [PRADAN FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) points users to the SIS and user guide but gives no archived Level-1 saturation or fill rule.
- ISRO's public processing description identifies Level-1 as corrected radiance with geometric tagging and Level-2 as including thermal, photometric, and geometric corrections. It does not define application of the saturation or dynamic-range fields to Level-1 pixels.
- A primary 2025 LPSC abstract uses those fields in a separate Level-0 raw-count recalibration and reports differences from archived Level 1. It does not define Level-1 mask or fill semantics. Do not turn this method into a local mask rule.
- The clarification gate failed. The threshold mismatch, absent fill constant, and independent-radiance requirement remain open. Sources and search record are in [`m1-literature`](../results/phase-1/m1-literature/findings.md).

## 2026-10-03 — Literature check on IIRS saturation and fill rules

- The IIRS instrument paper describes laboratory count-to-radiance characterization, including saturation radiance. It does not define fill values or pixel masks for archived Level-1 cubes.
- Laferriere and Bramson's LPSC 2025 abstract says they used the ISRO LUT, saturation radiance, and CCD dynamic range to convert linearized Level-0 counts to radiance. Their result differs from ISRO Level 1. They note missing order-sorting-filter radiance adjustments and keystone correction in their reconstruction.
- This method suggests the two table fields may be paired calibration inputs. It does not establish their official interpretation for Level-1 pixel masking. The reviewed papers do not define IIRS fill values or the invalid-pixel encoding in these cubes.
- The E1G2 comparison remains unresolved: 99.878921% of valid-band Level-1 values meet the declared saturation radiance, while paired raw counts do not reach `Dynamic_Range`. The calibrated QUB label declares no missing-value constant. Do not assign a mask from these data or papers.
- Evidence and source links are recorded in [`m1-literature/findings.md`](../results/phase-1/m1-literature/findings.md). The next gate is authoritative guidance from the IIRS data-processing team, plus independent radiance validation.

## 2026-09-29 — WAC reference crop acquisition

- Retrieved an E1G2-sized subset of the LROC WAC global morphologic pyramid TIFF by HTTP byte ranges. 164 tiles (10,747,904 raster bytes) produced an 824 x 10,230 pixel crop at 100 m/pixel, with 20 km margin. Source product metadata and crop georeferencing details are recorded in [`wac_crop_metadata.json`](../results/phase-1/m1-reference-data/wac_crop_metadata.json).
- The crop is available under ignored `data/reference/lroc_wac_e1g2/`. Visual inspection confirmed a continuous grayscale lunar surface image. Subsequent browse and full-resolution tie diagnostics are provisional and do not validate radiometric calibration.
- Next gate: review tie residuals, improve match confidence, and seek well-distributed absolute controls.

## 2026-09-29 — Preliminary browse-scale WAC registration

- The official E1G2 browse image and WAC morphology align after projecting the sparse IIRS geolocation grid into the WAC orthographic image. A robust linear along-track correction fitted to 23 training image ties was evaluated on 8 held-out ties in two separated along-track blocks.
- Held-out residual RMSE is 0.781 IIRS cube-pixel equivalents (57.4 WAC projected map metres); the 95th percentile is 1.075 pixels (78.0 projected metres). The tie CSV and JSON summary preserve per-window values, data versions, split and units. See the [figure](../results/phase-1/m1-reference-data/figures/iirs_wac_registration_browse_residuals.svg).
- This is provisional image-alignment evidence only. The ties come from the 175 x 8,547 browse, not a full-resolution band, and are not surveyed ground controls. Eight ties in two regions are not enough to validate absolute geolocation. The geometry gate remains open; continue with full-resolution band imagery and more separated held-out regions.

## 2026-09-29 — Full-resolution WAC registration diagnostic

- Extracted calibrated E1G2 band 40 at 1,369.6 nm, marked valid in the official mode table, with a 1st-to-99th-percentile display stretch for morphology matching only. The 250 x 12,210 image produced 30 accepted training image ties and 12 held-out ties in three along-track blocks.
- Held-out residual RMSE is 2.757 IIRS pixels (198.2 WAC projected map metres); the 95th percentile is 5.317 pixels (382.7 projected map metres). Several held-out ties show larger residuals, and the full-resolution RMSE exceeds the browse-scale residual. Per-tie values, source metadata, and figure are saved in the module record.
- These are local image matches, not absolute surveyed ground controls. The tie count, three holdout blocks, and variable match residuals are not sufficient to close the geometry gate. Continue with match-confidence review and well-distributed controls.

## 2026-09-29 — Screen M³ footprints against sparse E1G2 geometry

- The ODE-reported footprint for `M3G20090206T010833_V01_L2` contains 1,033/1,476 sparse E1G2 geometry points (69.99%), the most among five label-reviewed candidates.
- This is a control-grid point count, not a pixel area or valid-data fraction. M³ per-pixel location and fill arrays have not been checked. Machine-readable values and SVG figure are saved under `results/phase-1/m1-reference-data/metrics/` and `figures/`.
- Continue with pixel-level footprint and valid-pixel assessment before downloading a complete cube or comparing spectra.

## 2026-09-29 — Review M³ Level-2 candidate labels

- All five candidate labels describe Level-2 reflectance cubes with 304 samples and 85 bands. They set `CH1:THERMAL_CORRECTION_FLAG = Y`, declare special-pixel value -999.0, and define stored 1.0 as 100% reflectance.
- Scene lengths range from 9,310 to 27,796 lines. The shortest file is not automatically the best comparator; actual shared valid coverage remains unknown.
- See [`m3_label_review.csv`](../results/phase-1/m1-reference-data/m3_label_review.csv). No image cube, valid-pixel mask, or spectral metric was produced.

## 2026-09-29 — Independent references for E1G2

- LROC WAC global morphology imagery at 100 m/pixel is the spatial reference for the low-latitude E1G2 strip. A crop is local, and provisional browse/full-resolution tie diagnostics exist. They do not establish absolute geolocation error. This does not test radiometric calibration.
- The PDS Chandrayaan-1 M³ Level-2 collection contains pixel-located, reflectance-calibrated observations. It is a future reflectance comparator after IIRS calibration, mask, geometry, and correction gates pass, not a direct comparator for the current Level-1 radiance cube.
- The ODE footprint-intersection query found five M³ Level-2 candidate labels in orbit 1080 on 2009-02-05/06. Candidate metadata are in [`m3_overlap_candidates.csv`](../results/phase-1/m1-reference-data/m3_overlap_candidates.csv). Inspect actual label geometry and valid pixels before selecting one.
- The 2025 paper's Apollo 16 ground comparison is outside the E1G2 footprint. No local validation follows from that paper's result.
- See the source-backed [reference-data plan](../results/phase-1/m1-reference-data/summary.md). WAC imagery and provisional relative alignment metrics are local; no M³ image, local ground target, or validated absolute geolocation result exists.

## 2026-09-29 — Clarify saturation units and geometry product

- The official E1G2 saturation-table XML explicitly defines saturation radiance in `µW/cm**2/sr/µm` and dynamic range in `count`. The table and calibrated cube labels agree on radiance units. Do not describe this as an unresolved unit choice. The unresolved observation is numerical and operational: 99.878921% of valid-band radiance values meet the table threshold, but no raw counts reach the dynamic-range values. The alternative mW calculation is counterfactual and not supported by the table XML.
- The calibrated QUB label defines no missing-value constant, so fill values and per-pixel validity cannot be inferred from it. The image dimensions are 250 samples x 12,210 lines. Its geometry table has 1,476 rows: six sample positions at each of 246 scan-line positions spanning lines 0–12,209. It is not a full per-pixel geometry array.
- The LUT comparison is internal to the official calibration path, not independent validation. The current scene is not ready for masks, reflectance, or thermal correction. Seek authoritative clarification, independent radiometric validation, and image registration against an external lunar reference.

## 2026-09-28 — E1G2 calibrated-value and footprint audit

- The E1G2 cube scan is complete and reproducible from [`analyze_iirs_e1g2_scene.py`](../scripts/analyze_iirs_e1g2_scene.py). It streams the matched raw and calibrated QUBs from their ignored ZIPs and saves [`per-band values`](../results/phase-1/m1-e1g2-scene/metrics/e1g2_radiance_by_band.csv) and a [radiance/threshold/geometry figure](../results/phase-1/m1-e1g2-scene/figures/e1g2_radiance_and_footprint.png).
- Every calibrated value is finite. On the 222 bands marked valid by the E1G2 workbook, 4,829 band-pixels are exactly zero and 42,081 are negative. Sampled positive median radiance ranges from 118.218 to 1,305.46 µW/cm²/sr/µm.
- The calibrated product and official E1G2 saturation table both declare µW/cm²/sr/µm. Direct per-band comparison places 99.878921% of valid-band radiance values at or above the saturation threshold. A counterfactual mW interpretation yields 12 exceedances. The paired raw counts never reach the table's `dynamic_range` field. These candidate comparisons conflict and do not define pixel masks.
- The sparse geometry grid covers about 5.47°W–3.50°W and 6.53°S–26.86°N. It establishes low-latitude coverage only; full-resolution geolocation remains to be validated.
- Finding: the saturation/fill mask gate remains failed. The official LUT supports internal radiance-scale consistency, but independent validation remains open. Do not run thermal correction or treat zero/negative values as fill before authoritative rules are identified.

## 2026-09-28 — Local IIRS data and first-phase gates

- The active local data set contains two extracted raw/calibrated IIRS pairs from 2020-02-08. Raw labels describe 256-band `UnsignedLSB2` detector-count cubes; calibrated labels describe 256-band IEEE754LSBSingle cubes. Band centers span 712.3 to 5009.7 nm. Source: ignored `data/extracted/` and the active inventory in [`results/phase-1/m1-inventory/iirs_inventory.csv`](../results/phase-1/m1-inventory/iirs_inventory.csv).
- The four label-corner latitude ranges are approximately 30.9°S to 23.3°N. None is polar. Source: the same PDS4 labels.
- ISRO distinguishes raw and calibrated IIRS products and points to its product guide under `Other Downloads` → `iir.zip`. Source: [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml).
- Published IIRS Level-2 work includes thermal correction beyond about 2.5 µm before reflectance interpretation. Source: [Chauhan et al. 2025](https://onlinelibrary.wiley.com/doi/abs/10.1111/maps.70037).
- The USGS unified lunar map is a 1:5M geologic-unit map and cannot be assumed to provide per-pixel mineral abundance labels. Source: [USGS map release](https://astrogeology.usgs.gov/search/map/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2/).
- The historical M1 manifest run on 2026-09-28 matched declared file size, axis-derived size, ZIP entry size, and PDS4 MD5 for the initial four local cubes. It is retained as [`iirs_inventory_initial_four_scenes.csv`](../results/phase-1/m1-inventory/iirs_inventory_initial_four_scenes.csv); those old files were later removed from `data/` by request.

## Unresolved

- Whether corresponding calibrated products are downloadable for the four historical raw scenes. The active three-scene pilot has exact raw/calibrated pairs.
- Which high-confidence labels and additional tracks can support M3 evaluation.
- Whether polar IIRS shadowed observations have enough indirect-light signal for a 3 µm measurement.
- The E1G2 saturation-table unit fields are explicit, but their operational use and mismatch with observed values remain unresolved. Its calibrated cube label declares no missing-value constant. The user supplied text from the IIRS PDS4 User Guide V6; it documents filenames, raw/calibrated product contents, a basic apparent-reflectance conversion, and cautions about longwave radiance, but the supplied sections do not settle these mask rules.
- The supplied PRADAN download script lists ten `ndi` derived products dated 2024 and 2025. None matches the four local raw observation timestamps, so no exact counterpart was downloaded. A partial transfer was stopped and removed.
- The latest PRADAN script contains the already-local 2020 raw scene plus an unrelated 2019 raw scene. Neither is a calibrated counterpart.
- The expanded PRADAN selection had 30 reachable URLs: 12 complete raw/calibrated pairs, four calibrated-only products, and two raw-only products. The target 2020-02-05 raw scene remains without a calibrated counterpart in that selection. Two pairs from the selection were subsequently downloaded as the active pilot.
- The two 2020 E3G2 pilot pairs are extracted and paired by exact observation timestamp, job ID, orbit, dimensions, and wavelength table. Calibrated units differ between products: `mW/cm**2/sr/µm` for `m65` and `µW/cm**2/sr/µm` for `d18`. A third 2026 E1G2 pair is verified and its full-cube audit is recorded above. The historical four-product manifest is [`results/phase-1/m1-inventory/iirs_inventory.csv`](../results/phase-1/m1-inventory/iirs_inventory.csv).
- Both calibrated XML labels call the cube a radiance spectral image. The unit-prefix difference requires value-level validation before M2. The official archive now supplies mode-level band validity and saturation tables, while cube fill and per-pixel masks remain unresolved. See the [data dictionary](../results/phase-1/m1-inventory/data_dictionary.md).

## 2026-09-28 — Official IIRS archive

- The official `iir.zip` is now local, ZIP verified, and identified by SHA-256 in the [M1 summary](../results/phase-1/m1-inventory/summary.md). Its SIS V17 establishes calibrated Level 1 radiance and a separate Level 2 reflectance process. The separate user guide PDF is absent from this ZIP.
- The user supplied the V6 IIRS PDS4 User Guide text, dated 2021-08-23. It confirms `nri` denotes raw, `nci` calibrated, the timestamp is the observation start time, and station suffix `d18` is not a mode. Its XML label example format supports checking `exposure` and `gain` in the labels. The guide describes apparent reflectance from Level 1 radiance but does not specify the currently unresolved saturation-unit convention or fill mask.
- Both original 2020 pilots use `E3G2`. The official band-validity table ends its valid `E3G2` coverage at band 146 (3155.9 nm), leaving no valid 4–5 µm bands for a thermal fit that requires that region. The separate 2026 scene uses E1G2. A LUT comparison supports internal radiance-scale consistency, but the saturation-threshold QA gate remains unresolved. See the [source CSV](../results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv) and [figure](../results/phase-1/m1-inventory/figures/band_validity_by_mode.svg).
- The SIS describes LUT radiance output in `mW`; source XML labels differ by product (`mW` and `µW`), and saturation-table XML labels `µW`. For E1G2, converting calibrated values from µW to mW gives a median Level-1/LUT-stage ratio of 1.00375 and median band correlation of 0.922 on a fixed grid. The documented later pipeline steps make this an incomplete stage comparison, not independent calibration validation. Pixel-mask checks remain open.

## 2026-09-28 — Pilot radiance quality scan

- Both calibrated cubes were scanned across all bands and pixels. All values are finite. Exact zeros and negatives are rare on officially valid E3G2 bands, but their meanings are not established. Full counts, sampled quantiles, source units, and candidate threshold comparisons are saved in [`pilot_radiance_quality_by_band.csv`](../results/phase-1/m1-inventory/metrics/pilot_radiance_quality_by_band.csv), with its plot at [`pilot_radiance_quality_by_band.png`](../results/phase-1/m1-inventory/figures/pilot_radiance_quality_by_band.png).
- Applying the PDS4 unit prefixes produces comparable fixed-grid median ranges across the two paired scenes. This supports the unit labels provisionally; no independent calibration reference was used.
- The saturation-table XML declares µW, while the SIS describes Level 1 radiance generally in mW. On valid bands the former interpretation flags nearly every positive pixel at or above threshold, and the latter flags none. Treat the saturation-unit gate as failed and do not use either as a pixel mask. See the M1 module findings for the exact counts and method.
- M2 remains blocked. E3G2 has no valid 4–5 µm bands, and the current pair does not support a validated thermal correction or 3 µm reflectance result.

## 2026-09-28 — Literature review identifies E1G2 as the next pilot target

- A targeted review found that Verma et al. (2022) used E1G2 IIRS radiance strips and the 2.5–5 µm range for thermal correction. The local official validity workbook marks E1G2 bands 226–248 (4504.1–4874.9 nm) valid. This gives a concrete mode and wavelength range for scene acquisition.
- Gou et al. (2026) report that the 4504–4875 nm interval gives a more stable temperature estimate than the 2566–2937 nm interval. Their sensitivity example reports a 14.39% reflectance difference at 3156 nm for a 4 K temperature difference. Temperature and uncertainty checks must therefore remain explicit in M2.
- Chauhan et al. (2025) describe IIRS Level-2 processing to thermally corrected reflectance through 3.3 µm, standard geometry correction, empirical-line adjustment, and comparison with same-region M³ data. Bose et al. (2024) describe photometric correction over 0.8–2.0 µm and comparison with M³; that work does not validate thermal correction at 3 µm.
- The published method and official mode table identify E1G2 as a candidate acquisition path. The matched E1G2 pair is now acquired and its full-cube values and sparse geometry have been checked. The official LUT-stage comparison is numerically close to Level 1 (median ratio 1.00375, median per-band correlation 0.922), but is incomplete and is not independent scale validation. The saturation table flags 99.878921% of valid-band values under its declared units, while paired raw counts do not reach its dynamic-range field. These checks do not define masks; authoritative threshold/fill semantics and independent radiance validation remain open.
- A live read-only check of PRADAN's public Browse and Download link redirected to a sign-in page with username and password fields. No public product table or IIRS filters were visible, and no account details were submitted. Scene selection therefore requires authorized PRADAN access.
- **E1G2 pair:** The 2026-02-27 raw and calibrated labels match on timestamp, job ID `IIRXXD18CHO2904302NNNN26058141632221_V2_1`, imaging orbit 29042, dumping orbit 29043, exposure e1, gain g2, dimensions, and wavelengths. Both ZIP CRC checks and both embedded QUB MD5 checks pass. The calibrated label declares `µW/cm**2/sr/µm`; internal LUT scale comparison passes; independent unit validation, footprint, and masks remain open. See the [E1G2 acquisition record](../results/phase-1/m1-e1g2-scene/summary.md).
- An initial source-backed matrix is in [`docs/gap_matrix.md`](../docs/gap_matrix.md). Search scope and limitations are recorded in [`m1-literature/notes.md`](../results/phase-1/m1-literature/notes.md).
## 2026-10-10 — M1 gate follow-up

- The current public IIRS FAQ and the local assembly procedure do not resolve archived Level-1 saturation-mask application or fill encoding. The FAQ identifies the SIS/user guide as product references; the PRADAN contacts page lists IIRS payload contacts. See `results/phase-1/m1-gate-followup-20261010/`.
- PDS ODE still returns five M³ Level-2 footprint candidates. The top sparse-grid candidate remains `M3G20090206T010833_V01_L2`, but the 69.99% value counts sparse geometry nodes, not common valid pixels.
- The candidate label fetch failed TLS verification due to a self-signed certificate chain. No unsafe TLS override was used. Product-level M³ coverage was not measured.
- Gate: pixel masks/fill, independent radiance validation, and actual M³ overlap remain open. No M2 correction or M3 comparison is supported yet.

## Alternative validation routes (2026-10-10)

- User reports prior contact attempts to the IIRS team received no response; further outreach is not the next step.
- Published IIRS–M³ spectra normalized to unity at 810 nm check spectral shape only, not absolute scale. [LPSC 2021 abstract 2436](../results/phase-1/m1-gate-followup-20261010/findings.md)
- Apollo 16 with RELAB spectrum 62231 offers a published empirical-line absolute-reflectance route on a separate scene; it does not apply to the current strip.
- Diviner comparison matched by ground control points and acquisition time provides a derived-temperature check in the published conditions, not an independent radiance-unit check.
- Official PDS M³ volumes list multiple access sites. Fetch the current candidate through an official listed endpoint and calculate actual geolocated valid-pixel coverage before any spectral comparison.
- These alternatives do not resolve local Level-1 units, fill, or pixel-mask semantics. M2 remains gated.
- P1 follow-up: ODE REST returned the selected M³ label and file list. It identifies a 304 × 27,796 × 85 float32 RFL cube, invalid constant -999, and source location file `M3G20090206T010833_V03_LOC.IMG`. The 2,700,001 KiB cube and LOC file remain hosted on the JPL Imaging Node; strict TLS checks fail in this environment. No actual pixel-valid overlap has been computed. See [`m3_candidate_ode_metadata.json`](../results/phase-1/m1-gate-followup-20261010/m3_candidate_ode_metadata.json).

## M2 pilot and M3 reference findings (2026-10-10)

- The label radiance unit is physically correct for all three local products (I/F and temperature test). Stored scale differs by product: `m65` stores mW and `d18` stores µW. Read the unit from each label. [Module](../results/phase-1/m2-radiance-unit-physics/findings.md)
- The saturation table's declared µW is inconsistent with physically valid radiance, because it flags 99.88% of valid E1G2 data. Read as mW, it flags 12 values. This is evidence, not a provider rule. No mask is assigned.
- E3G2 Level-1 radiance is physically plausible. The roughly 5000× Level-1/LUT-stage gap therefore lies in the local LUT application or the LUT unit convention, not in the archived product.
- E1G2 brightness temperature follows independent SLDEM illumination (r = 0.877; held-out R² = 0.78). This supports the radiance scale, the thermal signal and the relative geometry together. [Module](../results/phase-1/m2-topographic-validation/findings.md)
- The exploratory 2.9 µm band depth is noise-dominated. No hydration claim. [Module](../results/phase-1/m2-thermal-brightness/findings.md)
- Spectral units are seed-stable but not region-stable (block ARI ≤ 0.60). IBD 2 µm is noise-dominated at pixel scale. [Module](../results/phase-1/m3-spectral-units/findings.md)
- E1G2 brightness temperature is warmer than Diviner GCP bolometric temperature at matched local time (08:07–08:15) by a median of +5.0 K over 33 latitude bins (IQR +3.4 to +7.1 K; r = 0.81). This lies within the expected 4.7 µm roughness excess. The offset is larger on dark units (r = −0.57 against 1.5 µm reflectance); the cause is open. [Module](../results/phase-1/m2-diviner-temperature/findings.md)

## M3 supervised and M4 exploratory findings (2026-10-10)

- Per-pixel classical baselines reach macro F1 0.46–0.50 on proxy USGS groups (majority 0.10). The from-scratch CNN gives no gain over the random forest.
- 64 px spatial context raises the random forest to 0.63. Frozen HyperSIGMA spatial reaches 0.67, with overlapping intervals, so the Earth-pretraining benefit is not demonstrated.
- No split leakage: a 64-line guard changes results by 0.04 or less.
- The latest PyTorch wheel (CUDA 13) silently falls back to the CPU on this machine's CUDA 12.5 driver. Pin `torch==2.5.1`.
