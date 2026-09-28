# Active pilot product lineage

**Status:** Complete for metadata pairing; physical calibration validation not complete

## Pair checks

| Pair | Raw processing and type | Calibrated processing and type | Shared identity | Dimensions |
| --- | --- | --- | --- | --- |
| `20200208T0057589143_d_img_m65` | `Raw`, `UnsignedLSB2`, no physical unit | `Calibrated`, `IEEE754LSBSingle`, `mW/cm**2/sr/µm` | Same start and stop time, job ID, and imaging orbit 2038 | 10,925 lines × 250 samples × 256 bands |
| `20200208T1245274109_d_img_d18` | `Raw`, `UnsignedLSB2`, no physical unit | `Calibrated`, `IEEE754LSBSingle`, `µW/cm**2/sr/µm` | Same start and stop time, job ID, and imaging orbit 2044 | 10,927 lines × 250 samples × 256 bands |

## Findings

- The `nri` and `nci` labels use the same observation timestamp and job ID for both pairs, establishing a direct raw-to-calibrated product match.
- Raw files are 16-bit unsigned detector-count cubes. Calibrated files are 32-bit IEEE floating-point cubes and are approximately twice the raw cube size.
- Both pairs preserve the same 256 band centers from 712.3 to 5009.7 nm.
- Calibrated units differ between the two products. This must be handled explicitly in M2 and must not be normalized by filename or detector suffix.
- The calibrated product is radiance-like according to its unit string. It is not yet documented here as corrected reflectance, so reflectance and thermal correction work remains open.

## Evidence

- Metadata manifest: [`iirs_inventory.csv`](iirs_inventory.csv)
- Extracted labels: ignored `data/extracted/`
- Reproduction command: `python3 scripts/build_iirs_manifest.py --data-root data/pradan --extracted-root data/extracted`
