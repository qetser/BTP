# Progress

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
- The geometry label declares a 1,476-row table with longitude, latitude, pixel, and line fields across 246 of 250 image lines. It is a sparse control grid, not full per-pixel geometry. Registration error has not been measured against an independent reference.
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
