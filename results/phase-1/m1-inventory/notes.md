# M1 inventory notes

- Keep the raw archives immutable and untracked.
- The first executable task is a manifest and integrity script. Its output should be versioned as a small CSV or JSON file under `results/` or `manifests/`, with an exception log for missing metadata.
- Do not make a metric plot for archive counts or dimensions unless those values are deliberately analyzed as a quality result. Inventory evidence is currently recorded as text.
- M1 cannot pass until the official IIRS product guide and calibrated counterparts are identified.
- The reproducible manifest command is `python3 scripts/build_iirs_manifest.py` from the repository root.
- The generated CSV is small enough to track. Raw ZIP archives and cubes remain ignored under `data/`.

## PRADAN matching procedure

1. Sign in to [PRADAN Chandrayaan-2](https://pradan.issdc.gov.in/ch2/) and open the IIRS data table.
2. Search using the exact UTC observation timestamp from the raw XML label, for example `2020-02-05T17:56:03.4306Z`. Keep the instrument, date, and detector or product suffix filters unchanged while checking both product types.
3. Download the IIRS archive and product guide from `Other Downloads` → `iir`. The guide defines the naming convention and product levels.
4. Look for the same timestamp and observation suffix in the calibrated listing. PRADAN's FAQ example uses `nci` for a calibrated IIRS image and our local raw files use `nri`, but the filename is only a candidate match.
5. Confirm the match inside the downloaded calibrated XML: the observation time, orbit, footprint or geometry, dimensions, wavelength table, and source observation must agree with the raw record. Confirm that the product path is calibrated and that its units and processing level are documented. Record the calibrated product ID, label, ZIP checksum, and any raw-to-calibrated reference in the manifest.

Do not rename a raw `nri` product to `nci`, and do not treat a file as calibrated based on the filename alone. The XML label and the official guide are authoritative.

The supplied PRADAN script must not be used for the current raw scenes. Its ten URLs point to different 2024 and 2025 `ndi` derived products. Generate a new PRADAN selection using one of the four raw timestamps, then verify the downloaded XML before choosing a local filename.

The latest two-file script was checked with HTTP HEAD requests only. The first URL is the already-downloaded 2020 raw scene. The second is an unrelated 2019 raw scene. Do not run the script for M2 calibration; it contains no calibrated product.

The expanded 30-file script was also checked with HTTP HEAD requests only. It includes 12 complete `nri` plus `nci` pairs. The selected pilot now contains the complete `20200208T1245274109_d_img_d18` pair and the complete `20200208T0057589143_d_img_m65` pair. Both pairs passed ZIP integrity checks and are ready for extraction and XML comparison.
