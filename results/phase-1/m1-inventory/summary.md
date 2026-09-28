# M1 inventory summary

**Status:** Local pilot inventory and metadata pairing complete; M1 documentation and coverage gates open

**Scope:** Two raw/calibrated IIRS pairs observed on 2020-02-08

**Source data:** Four original PRADAN ZIP archives and their extracted PDS4 products in ignored `data/`

**Method:** `python3 scripts/build_iirs_manifest.py --data-root data/pradan --extracted-root data/extracted`

**Evidence:** [`iirs_inventory.csv`](iirs_inventory.csv), [`pilot_lineage.md`](pilot_lineage.md), and [`data_dictionary.md`](data_dictionary.md)

All four extracted cubes match their PDS4 MD5 and declared byte size. Each raw product has an exact calibrated match by observation time, job ID, orbit, dimensions, and wavelength table. The calibrated labels explicitly call their cubes radiance spectral images, but declare different units for the two pairs. Neither product is validated reflectance.

The official IIRS product guide and archive/SIS are behind PRADAN's authenticated `Other Downloads` page. Their calibration conventions, fill and saturation values, and band validity rules have not been verified, so the M2 correction pilot remains gated. The two current tracks also do not meet the independent coverage gate for later evaluation.

The initial four raw scenes are retained only as a historical manifest: [`iirs_inventory_initial_four_scenes.csv`](iirs_inventory_initial_four_scenes.csv). No scientific metric or graph was computed for M1, so there are no metric or figure files.
