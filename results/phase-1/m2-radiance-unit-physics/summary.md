# Radiance-unit physical plausibility test

**Status:** Passed for all three local calibrated products. For each product, the unit declared in the PDS4 label gives physically plausible lunar radiance. The other reading gives impossible values. The V6 guide's general mW statement is therefore not correct for the `d18` products. This closes the numerical unit-scale question for these products on physical grounds. It does not validate absolute radiometric accuracy, saturation semantics, or fill rules.

## Source and run

- E1G2: `ch2_iir_nci_20260227T1239538758_d_img_d18` (label: µW/cm²/sr/µm), 222 SIS `VALID` bands, all 3,052,500 pixels.
- E3G2: `20200208T0057589143_m65` (label: mW) and `20200208T1245274109_d18` (label: µW), 127 `VALID` bands, every 16th line.
- Solar reference: ASTM G173-03 extraterrestrial spectrum (280–4000 nm, from pvlib 0.16.1), extended beyond 4 µm with a 5778 K blackbody scaled to 3.8–4.0 µm. Each band is modeled as a Gaussian whose FWHM equals the local band spacing, because the labels give no FWHM. Local copy SHA-256: `318953d6…6e4f5e`.
- Geometry: per-line solar zenith from each product's OAT file. The Sun–Moon distance uses a low-precision solar ephemeris plus the OAT geocentric lunar vector (0.99193 AU for E1G2).
- Commands: `scripts/build_e1g2_working_cube.py`, `scripts/run_e1g2_m2_physical_pilot.py`, and `scripts/run_e3g2_radiance_unit_physics.py`. Exact commands are in [notes](notes.md).
- Split: no train/test split applies. This is a physical consistency test against independent references.
- Code baseline commit: `304c5e8` (the scripts were uncommitted at run time; their SHA-256 values are in [notes](notes.md)).
- Figures: [E1G2 reflected-light and thermal tests](figures/e1g2_radiance_unit_physical_test.png) and [E3G2 reflected-light tests](figures/e3g2_radiance_unit_physical_test.png).
- Values: [E1G2 per band](metrics/e1g2_iof_by_band_under_unit_hypotheses.csv), [E1G2 summary](metrics/e1g2_m2_pilot_summary.json), [E3G2 per band](metrics/e3g2_iof_by_band_under_unit_hypotheses.csv), and [E3G2 summary](metrics/e3g2_unit_test_summary.json).

## Result

| Product | Label unit | Median I/F at 1.5 µm, read as µW | Read as mW | Physically plausible |
|---|---|---|---|---|
| 2026 E1G2 `d18` | µW | 0.0515 | 51.5 | µW (label correct) |
| 2020 E3G2 `m65` | mW | 0.000065 | 0.0654 | mW (label correct) |
| 2020 E3G2 `d18` | µW | 0.0557 | 55.7 | µW (label correct) |

The lunar I/F at these solar zenith angles (43–62°) is expected to fall in roughly the 0.04–0.13 range near 750 nm, and slightly higher at 1.5 µm (see [findings](findings.md) for the sources). An I/F above 1 is impossible for a natural surface.

An independent thermal test supports the same conclusion for E1G2. With the label unit, the median 4.5–4.9 µm brightness temperature is 327.8 K (p05–p95: 304.7–342.0 K), against a radiative-equilibrium prediction of 321.8–333.5 K. Reading the values as mW gives a median of 1,207 K, which is impossible for the lunar surface.

## Limits and next gate

The test discriminates a factor of 1000. It does not establish absolute accuracy at the percent level, because the solar spectrum, band response, phase behavior, and photometry each carry several percent of uncertainty. The saturation-table and fill-value questions remain open (see findings). Next gate: absolute reflectance-scale validation against an independent reference, either M³ over common ground or an Apollo 16 IIRS scene with the RELAB 62231 method.
