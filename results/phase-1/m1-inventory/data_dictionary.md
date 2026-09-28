# Pilot IIRS data dictionary

**Status:** Provisional label-based dictionary. The official IIRS guide and archive/SIS have not been inspected.

| Field | Raw `nri` products | Calibrated `nci` products | Evidence and limit |
| --- | --- | --- | --- |
| Processing level | `Raw` | `Calibrated` | PDS4 `processing_level` in each local XML label. |
| Cube values | `UnsignedLSB2` detector counts | `IEEE754LSBSingle` radiance image values | PDS4 `Element_Array/data_type`; calibrated `File/comment` says radiance spectral image. |
| Declared physical unit | No radiance or reflectance unit | `mW/cm**2/sr/µm` for `m65`; `µW/cm**2/sr/µm` for `d18` | PDS4 `Element_Array/unit`. The factor of 1000 between unit strings requires guide and value-level validation before pooling cubes. |
| Spectral grid | 256 bands, 712.3 to 5009.7 nm | Same within each pair | PDS4 `Band_Bin_Set`; band widths vary and must be carried per band. |
| Cube size | 2 bytes per sample | 4 bytes per sample | Declared and extracted sizes match; see manifest. |
| Pair identity | 2020-02-08 `m65`, orbit 2038; 2020-02-08 `d18`, orbit 2044 | Same observation time, job ID, orbit, dimensions, and wavelength table as its raw partner | [`pilot_lineage.md`](pilot_lineage.md). This proves metadata pairing, not a documented calibration algorithm. |
| Fill, saturation, and valid bands | Unknown | Unknown | No rule inferred from binary values or generic PDS4 type. Obtain official guide/SIS and calibration material. |
| Reflectance and thermal correction | None established | None established | Radiance units and label description do not establish corrected reflectance. |

## Source and access record

- Local evidence: the four extracted PDS4 XML labels under ignored `data/extracted/`, with archive and cube identity in [`iirs_inventory.csv`](iirs_inventory.csv). Reproduce the manifest with the command in the [summary](summary.md).
- [PRADAN's IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) identifies raw and calibrated products and directs users to `Other Downloads` → `iir.zip` for the archive/SIS and user guide.
- On 2026-09-28, an unauthenticated request for [`miscDownloads.xhtml`](https://pradan.issdc.gov.in/ch2/protected/miscDownloads.xhtml) redirected to ISSDC sign-in. The guide was therefore not acquired or used to infer calibration constants or mask rules.

## Next gate

Obtain the official `iir.zip` through authorized PRADAN access. Record its guide/SIS title, version, checksum, calibration level, unit conventions, fill/saturation and band-validity rules, and raw-to-calibrated processing description. Then check representative calibrated values against the declared units before the M2 pilot.
