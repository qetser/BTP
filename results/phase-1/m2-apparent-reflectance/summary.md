# E1G2 apparent reflectance pilot

**Status:** First apparent-reflectance product computed for the 2026 E1G2 scene (0.81–2.6 µm). Values and spectral shape are physically plausible. The product is provisional because it has no photometric correction, no empirical-line or M³ scale validation, and detector-junction steps remain in the spectra. It is not corrected reflectance in the sense of the M2 gate.

## Source and run

- Data: `ch2_iir_nci_20260227T1239538758_d_img_d18` (E1G2), 222 SIS `VALID` bands (813–4997 nm), 12,210 × 250 pixels, label unit µW/cm²/sr/µm (confirmed in [the unit test](../m2-radiance-unit-physics/summary.md)).
- Method: I/F = π·L·d² / F, where F is the ASTM G173 extraterrestrial irradiance convolved per band and d = 0.99193 AU. Apparent reflectance = I/F / cos(i), with per-line solar zenith from the OAT file (56.8–61.7°). There is no topographic or photometric correction in this product. The SLDEM local-incidence version is in [the topographic validation](../m2-topographic-validation/summary.md).
- Quality mask: a pixel is kept if all 222 valid bands are finite and positive. 3,040,527 of 3,052,500 pixels (99.61%) pass. This is a data-driven mask, not a provider fill or saturation rule.
- Command: `scripts/run_e1g2_m2_physical_pilot.py` (see [unit-test notes](../m2-radiance-unit-physics/notes.md)). Code baseline commit `304c5e8`, script uncommitted at run time.
- Split: no train/test split applies.
- Figures: [strip maps](figures/e1g2_apparent_reflectance_strip_maps.png) and [spectra](figures/e1g2_apparent_reflectance_spectra.png).
- Values: [per-band spectra](metrics/e1g2_apparent_reflectance_spectra.csv) and [run summary](metrics/e1g2_m2_pilot_summary.json).

## Result

- Apparent reflectance at 1.5 µm: median 0.098, p05 0.068, p95 0.150. The median at 813 nm is 0.070.
- The darkest 10% of pixels (1.5 µm reflectance ≤ 0.0736) and the brightest 10% (≥ 0.138) differ by a factor of about 1.9. That is consistent with the published mare/highland albedo contrast of about 2×.
- Spectra are red-sloped from 0.8 to 2.5 µm, as expected for space-weathered lunar soils. Beyond about 3 µm, apparent reflectance rises steeply because thermal emission dominates the signal. This is expected for a surface at about 330 K.
- Across-track striping at 1.5 µm: the relative standard deviation of column medians is 1.4%.
- The 1.5 µm map shows coherent terrain. Dark units lie at about 1–4.5°N (near the western edge of Sinus Medii), 9.5–14°N (Rimae Bode dark mantle deposit), and 19–22.5°N. Bright, rough terrain lies at about 15.5–19°N (Montes Apenninus) and south of 0°. Feature names come from IAU gazetteer positions and are not mapped boundaries.

## Limits and next gate

The spectra show steps near 1.16, 1.30, 1.83, and 1.99 µm, and near 3.4 µm. They occur at the same wavelengths in every pixel class, so they are probably detector or filter-junction artifacts. Straight segments mark gaps where SIS bands are invalid. There is no photometric normalization to standard geometry. Absolute scale is unvalidated. The 0.84/1.0 µm ratio panel mainly measures continuum slope, because IIRS has no valid band below 813 nm. Use [the M3 band-depth maps](../m3-spectral-units/summary.md) for the 1 µm band. Next gate: an absolute reflectance check against M³ or Apollo 16, then photometric correction.
