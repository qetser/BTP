# M1 inventory summary

**Status:** Local pilot inventory and quality scan complete; radiance scale is provisionally consistent across the two labels, but saturation-unit interpretation and independent coverage gates remain open

**Scope:** Two raw/calibrated IIRS pairs observed on 2020-02-08

**Source data:** Four original PRADAN ZIP archives and their extracted PDS4 products in ignored `data/`

**Method:** `python3 scripts/build_iirs_manifest.py --data-root data/pradan --extracted-root data/extracted`

**Evidence:** [`iirs_inventory.csv`](iirs_inventory.csv), [`pilot_lineage.md`](pilot_lineage.md), and [`data_dictionary.md`](data_dictionary.md)

**Validity artifact:** [Mode CSV](metrics/band_validity_by_mode.csv) and [mode figure](figures/band_validity_by_mode.svg). The source is official `iir.zip` SHA-256 `5afe64c3efe445e6d0334e8a374756ecab45698494dcee0d19616bf5dcb80720`, SIS V17 (March 2026), and its band-validity workbook. Wavelength units are nm; validity is a binary flag by band and exposure/gain mode. No train/validation/test split applies to this instrument metadata. Generation code commit: `4ef154b`.

**Pilot radiance quality:** [CSV](metrics/pilot_radiance_quality_by_band.csv) and [figure](figures/pilot_radiance_quality_by_band.png). Both full calibrated cubes were scanned by band. Counts are exact; positive-pixel quantiles use every 32nd line and every 5th sample. The figure compares candidate saturation thresholds using the saturation XML's µW unit and the SIS's general mW unit. No train/validation/test split applies to this M1 instrument check. Source data are the two calibrated 2020-02-08 cubes and official `iir.zip` above. Code was run from working-tree revision `f58ff4c`; `scripts/analyze_iirs_radiance_pilot.py` was uncommitted at scan time.

**Browse figures:** [`m65`](figures/calibrated_browse_m65_four_part_preview.png) and [`d18`](figures/calibrated_browse_d18_four_part_preview.png). They use the calibrated-product browse PNGs (PDS4 label version 1.0), not the radiance cube values. The browse images are 8-bit display products with no physical radiance unit. No train/validation/test split applies to these M1 inventory previews. The generation command is `uv run --no-project --with pillow python scripts/build_iirs_strip_previews.py`; code commit `0dd800d`.

All four extracted cubes match their PDS4 MD5 and declared byte size. Each raw product has an exact calibrated match by observation time, job ID, orbit, dimensions, and wavelength table. The calibrated labels explicitly call their cubes radiance spectral images, but declare different units for the two pairs. Neither product is validated reflectance.

The supplied official archive confirms that the calibrated cubes are Level 1 radiance. On officially valid `E3G2` bands, sampled positive-pixel medians in the two cubes have comparable magnitudes after converting each declared unit to mW/cm²/sr/µm. This supports, but does not independently prove, the product unit prefixes. Zero values are rare and no nonfinite values occur on valid bands; zero is not confirmed as fill. The saturation table has an unresolved unit conflict: treating its numeric values as µW puts almost every positive pixel at or above threshold, while treating them as mW puts none at or above threshold. Do not use either comparison as a saturation mask until the official convention is resolved. Both pilots' valid bands stop at 3155.9 nm, so thermal correction requiring 4–5 µm and all 3 µm reflectance work remain blocked. The two current tracks do not meet the independent coverage gate for later evaluation.

The initial four raw scenes are retained only as a historical manifest: [`iirs_inventory_initial_four_scenes.csv`](iirs_inventory_initial_four_scenes.csv). The validity CSV and figure document instrument metadata; no reflectance or scientific performance metric has been computed.
