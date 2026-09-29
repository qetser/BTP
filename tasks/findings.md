# Findings

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
- The SIS describes LUT radiance output in `mW`; source XML labels differ by product (`mW` and `µW`), and saturation-table XML labels `µW`. For E1G2, converting calibrated values from µW to mW gives a median LUT ratio of 1.00375 and median band correlation of 0.922 on a fixed grid. This supports internal scale consistency, not independent calibration validation. Pixel-mask checks remain open.

## 2026-09-28 — Pilot radiance quality scan

- Both calibrated cubes were scanned across all bands and pixels. All values are finite. Exact zeros and negatives are rare on officially valid E3G2 bands, but their meanings are not established. Full counts, sampled quantiles, source units, and candidate threshold comparisons are saved in [`pilot_radiance_quality_by_band.csv`](../results/phase-1/m1-inventory/metrics/pilot_radiance_quality_by_band.csv), with its plot at [`pilot_radiance_quality_by_band.png`](../results/phase-1/m1-inventory/figures/pilot_radiance_quality_by_band.png).
- Applying the PDS4 unit prefixes produces comparable fixed-grid median ranges across the two paired scenes. This supports the unit labels provisionally; no independent calibration reference was used.
- The saturation-table XML declares µW, while the SIS describes Level 1 radiance generally in mW. On valid bands the former interpretation flags nearly every positive pixel at or above threshold, and the latter flags none. Treat the saturation-unit gate as failed and do not use either as a pixel mask. See the M1 module findings for the exact counts and method.
- M2 remains blocked. E3G2 has no valid 4–5 µm bands, and the current pair does not support a validated thermal correction or 3 µm reflectance result.

## 2026-09-28 — Literature review identifies E1G2 as the next pilot target

- A targeted review found that Verma et al. (2022) used E1G2 IIRS radiance strips and the 2.5–5 µm range for thermal correction. The local official validity workbook marks E1G2 bands 226–248 (4504.1–4874.9 nm) valid. This gives a concrete mode and wavelength range for scene acquisition.
- Gou et al. (2026) report that the 4504–4875 nm interval gives a more stable temperature estimate than the 2566–2937 nm interval. Their sensitivity example reports a 14.39% reflectance difference at 3156 nm for a 4 K temperature difference. Temperature and uncertainty checks must therefore remain explicit in M2.
- Chauhan et al. (2025) describe IIRS Level-2 processing to thermally corrected reflectance through 3.3 µm, standard geometry correction, empirical-line adjustment, and comparison with same-region M³ data. Bose et al. (2024) describe photometric correction over 0.8–2.0 µm and comparison with M³; that work does not validate thermal correction at 3 µm.
- The published method and official mode table identify E1G2 as a candidate acquisition path. The matched E1G2 pair is now acquired and its full-cube values and sparse geometry have been checked. The official LUT comparison supports internal scale consistency (median calibrated/LUT ratio 1.00375, median per-band correlation 0.922). The saturation table flags 99.878921% of valid-band values under its declared units, while paired raw counts do not reach its dynamic-range field. These checks do not define masks; authoritative threshold/fill semantics and independent radiance validation remain open.
- A live read-only check of PRADAN's public Browse and Download link redirected to a sign-in page with username and password fields. No public product table or IIRS filters were visible, and no account details were submitted. Scene selection therefore requires authorized PRADAN access.
- **E1G2 pair:** The 2026-02-27 raw and calibrated labels match on timestamp, job ID `IIRXXD18CHO2904302NNNN26058141632221_V2_1`, imaging orbit 29042, dumping orbit 29043, exposure e1, gain g2, dimensions, and wavelengths. Both ZIP CRC checks and both embedded QUB MD5 checks pass. The calibrated label declares `µW/cm**2/sr/µm`; internal LUT scale comparison passes; independent unit validation, footprint, and masks remain open. See the [E1G2 acquisition record](../results/phase-1/m1-e1g2-scene/summary.md).
- An initial source-backed matrix is in [`docs/gap_matrix.md`](../docs/gap_matrix.md). Search scope and limitations are recorded in [`m1-literature/notes.md`](../results/phase-1/m1-literature/notes.md).
