# Pilot IIRS data dictionary

**Status:** PDS4 label and official archive/SIS review complete for product type and mode validity. Radiance scaling and pixel-level mask validation remain open.

| Field | Raw `nri` products | Calibrated `nci` products | Evidence and limit |
| --- | --- | --- | --- |
| Processing level | `Raw` | `Calibrated` | PDS4 `processing_level` in each local XML label. |
| Cube values | `UnsignedLSB2` detector counts | `IEEE754LSBSingle` radiance image values | PDS4 `Element_Array/data_type`; calibrated `File/comment` says radiance spectral image. |
| Declared physical unit | No radiance or reflectance unit | `mW/cm**2/sr/µm` for `m65`; `µW/cm**2/sr/µm` for `d18` | PDS4 `Element_Array/unit`. On officially valid E3G2 bands, sampled median magnitudes are comparable after applying these prefixes, which provisionally supports the labels. This is not an independent calibration check. See the quality CSV and figure. |
| Spectral grid | 256 bands, 712.3 to 5009.7 nm | Same within each pair | PDS4 `Band_Bin_Set`; band widths vary and must be carried per band. |
| Cube size | 2 bytes per sample | 4 bytes per sample | Declared and extracted sizes match; see manifest. |
| Pair identity | 2020-02-08 `m65`, orbit 2038; 2020-02-08 `d18`, orbit 2044 | Same observation time, job ID, orbit, dimensions, and wavelength table as its raw partner | [`pilot_lineage.md`](pilot_lineage.md). This proves metadata pairing, not a documented calibration algorithm. |
| Exposure and gain | `e3`, `g2`, 10 ms | Same within each pair | Pilot XML labels; SIS V17 section 3.3 maps `e3` to 10 ms. |
| Band validity | Mode-specific list | Mode-specific list | Archive `miscellaneous/ch2_iirs_band_validity_list.xls`, SIS V17 Appendix H. For pilot `E3G2`, valid bands are 7–28, 35–68, and 76–146. See [CSV](metrics/band_validity_by_mode.csv) and [figure](figures/band_validity_by_mode.svg). |
| Saturation | Mode-specific raw dynamic range and radiance thresholds | Same source, subject to unit validation | Archive `calibration/ch2_iirs_cal_e3g2_saturations_radiance.csv` and its XML. Unit interpretation fails the pilot check: the XML declares µW but SIS text gives mW; the two readings respectively flag nearly all or none of positive pixels. Do not derive a pixel mask yet. `-9999` is the table's unavailable saturation value, not an established cube fill value. |
| Cube fill and invalid-pixel value | Unknown | Unknown | SIS and local XML review did not establish a cube fill rule. Zero values observed in a spot check must not be assigned a meaning without validation. |
| Reflectance and thermal correction | None established | None established | SIS V17 sections 4.2.3 and Appendix L put thermal and photometric correction in derived Level 2 processing. The pilot cubes are Level 1 radiance, not corrected reflectance. |

## Source and access record

- Local evidence: the four extracted PDS4 XML labels under ignored `data/extracted/`, with archive and cube identity in [`iirs_inventory.csv`](iirs_inventory.csv). Reproduce the manifest with the command in the [summary](summary.md).
- The official `iir.zip` was transferred to ignored `data/pradan/iir.zip`. Its SHA-256 is `5afe64c3efe445e6d0334e8a374756ecab45698494dcee0d19616bf5dcb80720`; all ZIP entries pass CRC validation. It contains the 149-page *IIRS PDS4 Data Products and Archive SIS*, V17 (March 2026), calibration lookup tables, saturation tables, solar flux, and band validity. The separate *IIRS PDS4 Data Products User Guide* PDF is not inside the ZIP.
- The extracted SIS is at `data/pradan/iir/document/ch2_iirs_pds_dp_archive_sis.pdf` (ignored). Its PDS4 XML does not state an MD5; the `E3G2` LUT and saturation CSV files match the MD5 values in their XML labels.
- [PRADAN's IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) identifies raw and calibrated products and directs users to `Other Downloads` → `iir.zip`. The archive was supplied after the unauthenticated download redirected to sign-in.

## Next gate

Validate representative calibrated values against each label's unit and the `E3G2` saturation table, then establish pixel-level invalid and saturation masks. The current `E3G2` validity list ends at 3155.9 nm, so a pilot relying on valid 4–5 µm radiance for thermal fitting needs a different exposure mode or a separately validated method. The supplied V6 user-guide text documents apparent-reflectance conversion but does not resolve saturation units or fill details.
