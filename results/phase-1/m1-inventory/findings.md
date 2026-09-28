# M1 inventory findings

- Four active IIRS ZIP archives and extracted products are available locally under ignored `data/`: two raw and two calibrated products.
- Each active label describes a 256-band cube with band centers from approximately 712.3 to 5009.7 nm.
- The two active pilot footprints are low latitude, approximately 31.6 degrees south to 1.5 degrees south. None is polar.
- Raw detector counts are not calibrated radiance or reflectance. The calibrated products have product-specific radiance units and are not yet validated as corrected reflectance.
- Checksums, complete label field coverage, calibrated product pairing, and independent scene selection remain open.

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
- The product guide and calibrated product pairing therefore remain an acquisition task, not a completed M1 result.

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
- These labels establish a raw-to-calibrated pair, but they do not by themselves prove that the values are corrected reflectance. Thermal and photometric validation remains open.
