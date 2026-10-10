# E1G2 brightness temperature and exploratory thermal removal

**Status:** Brightness temperature computed for 3,040,527 pixels. It agrees with radiative equilibrium along the strip and with independent terrain illumination (see [topographic validation](../m2-topographic-validation/summary.md)). The thermal removal over 2.5–3.6 µm is exploratory and does not pass a quality gate. No hydration result is claimed.

## Source and run

- Data: E1G2 `20260227T1239538758`, bands 4504–4875 nm (the SIS `VALID` range used by Chauhan et al. 2021 and CH2IIRS).
- Method: brightness temperature is the median over these bands of the Planck inversion of (L − reflected)/ε, with emissivity 0.95. The reflected component uses the 2.3–2.5 µm apparent reflectance held flat. The sensitivity case extrapolates a per-pixel linear slope fitted over 1.6–2.5 µm. Chauhan et al. (2021) and CH2IIRS neglect the reflected term. Here it is about 6% of the 4.7 µm signal.
- Model: T = [(1−A)·S·cos(i) / (d²·ε·σ)]^¼, with A = 0.12, S = 1361 W/m², ε = 0.95, and d = 0.99193 AU (Hayne et al. 2017 parameter values). The model has no thermal inertia or roughness.
- Thermal removal: R = π(L − εB(T))·d² / (F·cos i) for 2.45–3.65 µm. Exploratory 2.9 µm band depth: trough at 2.85–2.95 µm against a linear continuum between 2.45–2.6 and 3.45–3.65 µm.
- Command: `scripts/run_e1g2_m2_physical_pilot.py`. Code baseline `304c5e8`.
- Split: no train/test split applies.
- Figure: [temperature map, latitude profile, and thermal removal](figures/e1g2_brightness_temperature_and_thermal_removal.png).
- Values: [per-latitude temperatures](metrics/e1g2_temperature_by_latitude.csv), [thermal removal spectrum](metrics/e1g2_thermal_removal_spectrum.csv), and [run summary](metrics/e1g2_m2_pilot_summary.json).

## Result

- Brightness temperature: median 327.8 K, p05 304.7 K, p95 342.0 K. Over 1° latitude bins, the median lies between 1 and 10 K below the equilibrium model (321.8–333.5 K). It is closest to the model in the dark units (2–3°N and 10–12°N) and coolest relative to the model in the bright highland south of 0°. That pattern is expected, because darker surfaces absorb more sunlight.
- The sloped-reflectance sensitivity case changes the median temperature by only −0.74 K.
- The 18°N bin (Montes Apenninus) is 16 K below the model. The strip crosses steep, sun-facing and shadowed slopes there. The topography module explains this pattern.
- After thermal removal, the median 2.5–3.6 µm reflectance stays nearly flat at 0.2–0.35 instead of rising to 0.83. There is a residual kink at 3.4 µm.
- The exploratory 2.9 µm band depth is median 0.045, with p05 −0.146 and p95 0.172. The spread is larger than the median, so the parameter is dominated by noise and model error at pixel scale.

## Limits and next gate

The 2.9 µm parameter is not evidence of OH or H₂O. It has no independent reference, no emissivity or roughness model, and no uncertainty propagation. It is sensitive to temperature errors of a few kelvin. Laferriere and Bramson (LPSC 2025, abstract 1644) report that ISRO Level-1 differs from their recalibration near 3 µm and beyond 4 µm. That affects both the temperature and the 3 µm region. Next gate: compare temperatures with Diviner at matched local time (about 08:15 lunar local time), then repeat the 3 µm analysis with uncertainty estimates and an independent reference scene.

## Albedo-law comparison (2026-10-10)

Command: `uv run --no-project --with numpy --with matplotlib python scripts/compare_e1g2_temperature_albedo_models.py`. Pixel-weighted residuals (IIRS minus model) over SLDEM local cos(i) bins:

| Model | Mean residual | RMS residual |
|---|---|---|
| Constant A = 0.12 | −1.3 K | 5.0 K |
| Hayne et al. (2017) A(i), A0 = 0.07 | +8.0 K | 12.1 K |
| Hayne A(i), A0 = 0.12 | +13.2 K | 16.1 K |
| Hayne A(i), A0 = 0.16 | +17.5 K | 19.8 K |

The simple constant-albedo model fits best. With the physically preferred incidence-dependent albedo, IIRS is 8–18 K warmer than equilibrium. Two causes are plausible and cannot be separated here: sub-pixel roughness, which makes nadir views warmer, and a radiance bias of roughly 15% beyond 4 µm (Laferriere and Bramson, LPSC 2025, report Level-1 differences there). **The agreement with the constant-albedo model may be coincidental.** A Diviner comparison at matched local time is required. Values: [model table](metrics/e1g2_temperature_vs_albedo_models.csv), [summary](metrics/e1g2_temperature_vs_albedo_models_summary.json). Figure: [albedo models](figures/e1g2_temperature_vs_albedo_models.png).
