# Findings

## 2026-09-28 — Local IIRS data and first-phase gates

- The active local data set contains two extracted raw/calibrated IIRS pairs from 2020-02-08. Raw labels describe 256-band `UnsignedLSB2` detector-count cubes; calibrated labels describe 256-band IEEE754LSBSingle cubes. Band centers span 712.3 to 5009.7 nm. Source: ignored `data/extracted/` and the active inventory in [`results/phase-1/m1-inventory/iirs_inventory.csv`](../results/phase-1/m1-inventory/iirs_inventory.csv).
- The four label-corner latitude ranges are approximately 30.9°S to 23.3°N. None is polar. Source: the same PDS4 labels.
- ISRO distinguishes raw and calibrated IIRS products and points to its product guide under `Other Downloads` → `iir.zip`. Source: [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml).
- Published IIRS Level-2 work includes thermal correction beyond about 2.5 µm before reflectance interpretation. Source: [Chauhan et al. 2025](https://onlinelibrary.wiley.com/doi/abs/10.1111/maps.70037).
- The USGS unified lunar map is a 1:5M geologic-unit map and cannot be assumed to provide per-pixel mineral abundance labels. Source: [USGS map release](https://astrogeology.usgs.gov/search/map/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2/).
- The historical M1 manifest run on 2026-09-28 matched declared file size, axis-derived size, ZIP entry size, and PDS4 MD5 for the initial four local cubes. It is retained as [`iirs_inventory_initial_four_scenes.csv`](../results/phase-1/m1-inventory/iirs_inventory_initial_four_scenes.csv); those old files were later removed from `data/` by request.

## Unresolved

- Whether corresponding calibrated products are downloadable for all four scenes.
- Which high-confidence labels and additional tracks can support M3 evaluation.
- Whether polar IIRS shadowed observations have enough indirect-light signal for a 3 µm measurement.
- Which official calibrated product and product guide correspond to each verified raw scene.
- The [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) confirms separate raw and calibrated products and directs users to the IIRS archive and product guide under `Other Downloads` → `iir`. The current local ZIPs contain only raw data folders, so calibrated lineage is still unresolved.
- The supplied PRADAN download script lists ten `ndi` derived products dated 2024 and 2025. None matches the four local raw observation timestamps, so no exact counterpart was downloaded. A partial transfer was stopped and removed.
- The latest PRADAN script contains the already-local 2020 raw scene plus an unrelated 2019 raw scene. Neither is a calibrated counterpart.
- The expanded PRADAN selection has 30 reachable URLs: 12 complete raw/calibrated pairs, four calibrated-only products, and two raw-only products. The target 2020-02-05 raw scene remains without a calibrated counterpart in this selection. No files were downloaded.
- The active two-pair pilot is now extracted and paired by exact observation timestamp, job ID, orbit, dimensions, and wavelength table. Calibrated units differ between products: `mW/cm**2/sr/µm` for `m65` and `µW/cm**2/sr/µm` for `d18`. The active manifest is [`results/phase-1/m1-inventory/iirs_inventory.csv`](../results/phase-1/m1-inventory/iirs_inventory.csv).
