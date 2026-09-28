# Findings

## 2026-09-28 — Local IIRS data and first-phase gates

- The active local data set contains two extracted raw/calibrated IIRS pairs from 2020-02-08. Raw labels describe 256-band `UnsignedLSB2` detector-count cubes; calibrated labels describe 256-band IEEE754LSBSingle cubes. Band centers span 712.3 to 5009.7 nm. Source: ignored `data/extracted/` and the active inventory in [`results/phase-1/m1-inventory/iirs_inventory.csv`](../results/phase-1/m1-inventory/iirs_inventory.csv).
- The four label-corner latitude ranges are approximately 30.9°S to 23.3°N. None is polar. Source: the same PDS4 labels.
- ISRO distinguishes raw and calibrated IIRS products and points to its product guide under `Other Downloads` → `iir.zip`. Source: [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml).
- Published IIRS Level-2 work includes thermal correction beyond about 2.5 µm before reflectance interpretation. Source: [Chauhan et al. 2025](https://onlinelibrary.wiley.com/doi/abs/10.1111/maps.70037).
- The USGS unified lunar map is a 1:5M geologic-unit map and cannot be assumed to provide per-pixel mineral abundance labels. Source: [USGS map release](https://astrogeology.usgs.gov/search/map/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2/).
- The historical M1 manifest run on 2026-09-28 matched declared file size, axis-derived size, ZIP entry size, and PDS4 MD5 for the initial four local cubes. It is retained as [`iirs_inventory_initial_four_scenes.csv`](../results/phase-1/m1-inventory/iirs_inventory_initial_four_scenes.csv); those old files were later removed from `data/` by request.

## Unresolved

- Whether corresponding calibrated products are downloadable for the four historical raw scenes. The active two-scene pilot already has exact calibrated pairs.
- Which high-confidence labels and additional tracks can support M3 evaluation.
- Whether polar IIRS shadowed observations have enough indirect-light signal for a 3 µm measurement.
- The official IIRS guide/SIS and its calibration conventions for the active pilot. The [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) directs users to `Other Downloads` → `iir.zip`, but that page redirected unauthenticated access to sign-in on 2026-09-28.
- The supplied PRADAN download script lists ten `ndi` derived products dated 2024 and 2025. None matches the four local raw observation timestamps, so no exact counterpart was downloaded. A partial transfer was stopped and removed.
- The latest PRADAN script contains the already-local 2020 raw scene plus an unrelated 2019 raw scene. Neither is a calibrated counterpart.
- The expanded PRADAN selection had 30 reachable URLs: 12 complete raw/calibrated pairs, four calibrated-only products, and two raw-only products. The target 2020-02-05 raw scene remains without a calibrated counterpart in that selection. Two pairs from the selection were subsequently downloaded as the active pilot.
- The active two-pair pilot is now extracted and paired by exact observation timestamp, job ID, orbit, dimensions, and wavelength table. Calibrated units differ between products: `mW/cm**2/sr/µm` for `m65` and `µW/cm**2/sr/µm` for `d18`. The active manifest is [`results/phase-1/m1-inventory/iirs_inventory.csv`](../results/phase-1/m1-inventory/iirs_inventory.csv).
- Both calibrated XML labels call the cube a radiance spectral image. The unit-prefix difference requires value-level validation before M2. The official archive now supplies mode-level band validity and saturation tables, while cube fill and per-pixel masks remain unresolved. See the [data dictionary](../results/phase-1/m1-inventory/data_dictionary.md).

## 2026-09-28 — Official IIRS archive

- The official `iir.zip` is now local, ZIP verified, and identified by SHA-256 in the [M1 summary](../results/phase-1/m1-inventory/summary.md). Its SIS V17 establishes calibrated Level 1 radiance and a separate Level 2 reflectance process. The separate user guide PDF is absent from this ZIP.
- Both active pilots use `E3G2`. The official band-validity table ends its valid `E3G2` coverage at band 146 (3155.9 nm), leaving no valid 4–5 µm bands for a thermal fit that requires that region. See the [source CSV](../results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv) and [figure](../results/phase-1/m1-inventory/figures/band_validity_by_mode.svg).
- The SIS uses `mW` for calibrated radiance generally; source XML labels differ by product (`mW` and `µW`), and the `E3G2` saturation XML uses `µW`. Numerical unit-scale and pixel-mask checks remain open.

## 2026-09-28 — Pilot radiance quality scan

- Both calibrated cubes were scanned across all bands and pixels. All values are finite. Exact zeros and negatives are rare on officially valid E3G2 bands, but their meanings are not established. Full counts, sampled quantiles, source units, and candidate threshold comparisons are saved in [`pilot_radiance_quality_by_band.csv`](../results/phase-1/m1-inventory/metrics/pilot_radiance_quality_by_band.csv), with its plot at [`pilot_radiance_quality_by_band.png`](../results/phase-1/m1-inventory/figures/pilot_radiance_quality_by_band.png).
- Applying the PDS4 unit prefixes produces comparable fixed-grid median ranges across the two paired scenes. This supports the unit labels provisionally; no independent calibration reference was used.
- The saturation-table XML declares µW, while the SIS describes Level 1 radiance generally in mW. On valid bands the former interpretation flags nearly every positive pixel at or above threshold, and the latter flags none. Treat the saturation-unit gate as failed and do not use either as a pixel mask. See the M1 module findings for the exact counts and method.
- M2 remains blocked. E3G2 has no valid 4–5 µm bands, and the current pair does not support a validated thermal correction or 3 µm reflectance result.
