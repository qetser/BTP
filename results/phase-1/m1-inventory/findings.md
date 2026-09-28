# M1 inventory findings

- Four active IIRS ZIP archives and extracted products are available locally under ignored `data/`: two raw and two calibrated products.
- Each active label describes a 256-band cube with band centers from approximately 712.3 to 5009.7 nm.
- The two active pilot footprints are low latitude, approximately 31.6 degrees south to 1.5 degrees south. None is polar.
- Raw detector counts are not calibrated radiance or reflectance. The calibrated products have product-specific radiance units and are not yet validated as corrected reflectance.
- Cube checksums and metadata pairing are complete. The official SIS is now available. Numeric unit validation, cube fill interpretation, and independent scene selection remain open.

## Integrity run

- Run command: `python3 scripts/build_iirs_manifest.py`
- Run date: 2026-09-28 UTC
- Four of four extracted cubes matched their PDS4 declared MD5 checksums.
- Four of four cubes matched the declared file size, axis-derived size, and ZIP entry size.
- All four products contain 256 wavelength centers from 712.3 to 5009.7 nm.
- ZIP SHA-256 values are recorded in the manifest for archive identity.
- This is an integrity result only. It does not establish calibrated radiance, reflectance, or scientific labels.

## Official product path

- The [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) confirms that IIRS has separate raw and calibrated products, that the data folder distinguishes raw and calibrated products, and that the IIRS archive and product guide are under `Other Downloads` → `iir`.
- The historical four-scene local ZIPs contained only `data/raw`, `browse/raw`, and raw miscellaneous files. The active extraction contains both `data/raw` and `data/calibrated` products.
- The official archive/SIS has since been acquired. The separate user guide PDF is not in that ZIP. The two active pilot pairs are verified from their XML labels below.

## Supplied PRADAN download list

- The supplied script lists ten `ch2_iir_ndi_*_d_rfl_d18_srd.zip` derived reflectance products.
- Their observation dates are in January, May, and July 2024 or July 2025.
- None matches the four local raw observation timestamps from 2020-02-05, 2021-11-22, or 2023-11-30.
- No file from that list was retained. A partial first download was stopped and removed before completion.

## New PRADAN script check

- The URL for `ch2_iir_nri_20200205T1756034306_d_img_d18.zip` is valid and returns HTTP 200 with 649,743,724 bytes.
- That exact ZIP is already present locally with the same byte size, so it does not need to be downloaded again.
- The second URL, `ch2_iir_nri_20191211T1440089859_d_img_d18.zip`, is a separate 2019 raw observation. It is not the calibrated counterpart for the 2020 scene and is not part of the current four-scene set.

## Expanded PRADAN selection check

- All 30 supplied URLs returned HTTP 200 with `application/zip` metadata.
- The selection contains 12 complete raw/calibrated pairs with the same timestamp and detector suffix.
- It contains four calibrated-only products and two raw-only products.
- The local target `20200205T1756034306_d_img_d18` is still raw-only in the supplied selection. No calibrated counterpart for that exact observation is present here.
- The 12 complete pairs are suitable candidates for an M2 pilot after one pair is selected and both XML labels are compared.

## Active pilot lineage

- The selected `m65` and `d18` pairs have identical observation times, job IDs, orbit numbers, dimensions, and wavelength tables between raw and calibrated labels.
- Raw products are `UnsignedLSB2` detector counts. Calibrated products are `IEEE754LSBSingle` floating-point values.
- The calibrated `m65` label declares `mW/cm**2/sr/µm`; the calibrated `d18` label declares `µW/cm**2/sr/µm`. Units must be carried per product into M2.
- Both calibrated XML `File/comment` fields describe a radiance spectral image. These labels establish radiance product identity, but not the calibration algorithm or corrected reflectance. Thermal and photometric validation remains open.

## Guide access and unit gate

- The [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) directs users to `Other Downloads` → `iir.zip`. An unauthenticated request to the [download page](https://pradan.issdc.gov.in/ch2/protected/miscDownloads.xhtml) redirected to ISSDC sign-in on 2026-09-28. The user subsequently supplied the ZIP; its contents and findings are recorded below.
- The calibrated labels' `mW` and `µW` unit prefixes differ by 1000. Their numeric scales and official conversion conventions have not been checked. Pooling or converting these cubes for M2 is blocked pending that check.
- The provisional [data dictionary](data_dictionary.md) lists what the local labels establish and which mask and calibration fields remain unknown.

## Official archive and mode validity

- The user supplied official `iir.zip` on 2026-09-28. ZIP CRC validation passed; the archive SHA-256 is `5afe64c3efe445e6d0334e8a374756ecab45698494dcee0d19616bf5dcb80720`. It contains the SIS V17 (March 2026), LUTs, saturation tables, solar flux, and band validity. The separate user guide PDF is absent.
- SIS V17 section 4.2.2 describes dark subtraction, LUT correction, destriping, and post-processing before storing Level 1 radiance. Section 4.2.3 and Appendix L describe thermal and photometric correction as Level 2 work. This confirms the active calibrated cubes are not corrected reflectance.
- Both pilots are `E3G2` at 10 ms. The official workbook marks bands 7–28, 35–68, and 76–146 valid for `E3G2`. Bands 147 onward, including 4–5 µm, are invalid or low confidence for this mode. The full [CSV](metrics/band_validity_by_mode.csv) and [figure](figures/band_validity_by_mode.svg) preserve the source flags by mode.
- SIS V17 section 4.2.2 uses `mW/cm²/sr/µm` as the general radiance unit. The active `d18` XML and `E3G2` saturation-table XML use `µW/cm²/sr/µm`; the active `m65` XML uses `mW/cm²/sr/µm`. These source declarations need numerical checks before any unit conversion is accepted. The workbook's mode mask is not a per-pixel saturation mask.

## 2026-09-28 radiance cube quality scan

- Run command: `uv run --no-project --with numpy --with matplotlib python scripts/analyze_iirs_radiance_pilot.py`.
- The scan covered all 256 bands and all pixels in each calibrated cube: 2,731,250 pixels in `m65` and 2,731,750 in `d18`. All values were finite. On the 127 officially valid `E3G2` bands, aggregate exact zeros were 2,809 (`m65`) and 3,059 (`d18`); negative values were 26 in each cube. These counts are summed across bands, so they are not unique-pixel counts. Neither zero nor negative is assigned a fill meaning.
- After applying the unit prefixes in the PDS4 labels, fixed-grid positive-pixel median values on valid bands span 0.115–1.547 mW/cm²/sr/µm (`m65`) and 0.104–1.199 mW/cm²/sr/µm (`d18`). Their comparable scale supports, but does not independently prove, the labels' `mW` versus `µW` prefixes.
- The official E3G2 saturation CSV's label declares µW/cm²/sr/µm, while the SIS describes Level 1 radiance generally in mW/cm²/sr/µm. Comparing table values as µW flags nearly all positive pixels at or above threshold across valid bands; comparing them as mW flags none. This disagreement fails the saturation-unit gate. These counts are candidate comparisons only and must not be used as a pixel mask.
- The full per-band values, including invalid bands for audit, are in [`pilot_radiance_quality_by_band.csv`](metrics/pilot_radiance_quality_by_band.csv), with a plot in [`pilot_radiance_quality_by_band.png`](figures/pilot_radiance_quality_by_band.png). Quantiles use every 32nd line and every 5th sample; counts are exact.
- Gate result: radiance prefixes are provisionally supported by cross-scene scale, but numerical radiance validation is incomplete; fill and pixel saturation masks are unresolved. M2 correction remains blocked. The 3.16–5.01 µm segment is not valid for these E3G2 products, including the 4–5 µm region required by the current thermal plan.

## Pilot strip browse previews

- The two calibrated-product browse PNGs pass the MD5 values declared in their PDS4 browse labels. Their dimensions are 175 × 7647 (`m65`) and 175 × 7649 (`d18`) pixels.
- The labels describe the PNGs as count-calibrated subsampled browse images. The [four-part `m65` preview](figures/calibrated_browse_m65_four_part_preview.png) and [four-part `d18` preview](figures/calibrated_browse_d18_four_part_preview.png) show the full browse strips for visual orientation. They do not establish radiance scale, surface reflectance, georegistration, or scientific labels.
