# M1 inventory summary

**Status:** Pilot archive download complete; XML extraction and product-lineage inspection open
**Scope:** Two locally downloaded raw/calibrated IIRS pairs for the 2020-02-08 observations
**Current conclusion:** The active local data set now contains one `d18` raw/calibrated pair and one `m65` raw/calibrated pair. The archives are valid ZIPs and are ready for XML inspection and M2 pilot work.
**Verified so far:** All four selected URLs returned HTTP 200. Python ZIP integrity checks passed for all four archives. The previous four-scene inventory is retained as a historical record, but those old files were removed from `data/`.
**Historical manifest:** [`iirs_inventory_initial_four_scenes.csv`](iirs_inventory_initial_four_scenes.csv)
**Next gate:** Extract the four selected archives, parse both raw and calibrated labels, compare lineage and units, and create the M2 pilot quality report.

No scientific metric or graph has been computed for M1 yet. Therefore `metrics/` and `figures/` contain no result files.
