# E3G2 paired-lineage notes

- Command: `uv run --no-project --with numpy --with matplotlib python scripts/audit_e3g2_raw_lut_calibrated_pairs.py`.
- The script reads raw and calibrated cubes from the four existing extracted 2020 E3G2 products. It does not modify source data.
- The paired scenes are selected by observation timestamp and matching `m65` or `d18` suffix from the verified inventory. Labels define the data types, units, and dimensions.
- E3G2 validity and saturation fields use band numbering mapped from the official zero-based table rows. LUT coefficients are read band-major with 250 sample entries per band.
- Exact counts include every spatial pixel in all 127 E3G2-valid bands. LUT ratios and correlations use every 32nd line and every fifth sample.
- Saturation comparison A converts the XML-declared µW threshold to mW; comparison B treats the numeric threshold as mW counterfactually. Raw `Dynamic_Range` comparison is raw count >= table count. None is a validated pixel mask.
- LUT calculation uses `raw_count * Multiplicative_Factor + Offset`, which Appendix F identifies as the LUT radiance stage after dark subtraction. The raw PDS product is documented as already dark-subtracted. Archived Level 1 follows additional destriping and post-processing, so the present comparison omits those steps and must not be called a complete reconstruction.
- Outputs: `metrics/e3g2_raw_lut_calibrated_by_band.csv`, `metrics/e3g2_raw_lut_calibrated_summary.json`, and `figures/e3g2_raw_lut_calibrated_diagnostics.png`.
- Code base revision: `304c5e8bc880d754ecab0b75983c8370b73d033e`; script SHA-256: `e6f40721c2c9dc5c5154a401fd76778a16ca711e93a9b34ec1134791637d1f48`.
