# Independent topographic validation of IIRS temperature and geometry

**Status:** Passed as a physical consistency test. IIRS 4.5–4.9 µm brightness temperature follows local solar illumination computed from SLDEM2015, which is an independent laser-altimetry and stereo DEM. Pearson r = 0.877. A linear model fitted on alternate 500-line blocks predicts the held-out blocks with R² = 0.78. This jointly supports three things: the thermal signal is surface emission, the radiance scale is correct, and the provisional SLDEM-corrected geometry places pixels on the right terrain. It is not a surveyed absolute geolocation test.

## Source and run

- IIRS: E1G2 `20260227T1239538758`, brightness temperature and 1.5 µm apparent reflectance from [the thermal module](../m2-thermal-brightness/summary.md).
- Reference: SLDEM2015 at 512 pixels/degree (about 59 m), tiles `00N_30N_315_360` and `30S_00S_315_360`, as used in [the hillshade registration](../m1-sldem-hillshade/summary.md). DEM crop nodata: 6,718 samples.
- Method: SLDEM slopes are sampled at each IIRS pixel through the provisional SLDEM-corrected geometry. Local cos(i) is computed from the per-line OAT sun azimuth (clockwise from north, as selected by the hillshade registration) and sun elevation. Pixels with local cos(i) ≤ 0.05 are excluded (5,704 pixels). Cast shadows are not modeled.
- Split: the linear fit of temperature against cos(i) uses even 500-line blocks, and evaluation uses odd blocks. The Pearson r uses all 3,034,675 retained pixels.
- Command: `uv run --no-project --with numpy --with matplotlib --with opencv-python-headless --with pillow python scripts/run_e1g2_topographic_validation.py`. Code baseline `304c5e8`; script SHA-256 `cd7df74e…45e2`.
- Figure: [topographic validation](figures/e1g2_topographic_validation.png).
- Values: [temperature against cos(i) bins](metrics/e1g2_bt_vs_local_cos_incidence.csv) and [summary](metrics/e1g2_topographic_validation_summary.json).

## Result

| Quantity | Value |
|---|---|
| Pearson r, brightness temperature against SLDEM local cos(i) | 0.877 |
| Held-out R² (odd 500-line blocks) | 0.784 |
| Fitted slope (even blocks) | 113.9 K per unit cos(i) |
| Temperature minus equilibrium model, p16 / p50 / p84 | −7.4 / −1.7 / +4.2 K |
| Pearson r, I/F at 1.5 µm against local cos(i) | 0.548 |
| Local slope p50 / p95 | 4.1° / 17.4° |
| CV of 1.5 µm reflectance, flat versus local incidence | 0.260 → 0.248 |

Temperature follows the equilibrium curve over cos(i) from about 0.35 to 0.65, where most pixels lie. It is warmer than the model on poorly lit slopes and cooler than the model on strongly lit slopes. Normalizing reflectance by local incidence turns the 1.5 µm histogram from one peak with a shoulder into two separate peaks. That is consistent with separating dark mare from bright highland material once the slope shading is removed.

## Limits and next gate

The flatter-than-model slope is expected from lateral heat conduction, morning thermal lag, sub-pixel roughness, and resolution mismatch between IIRS (about 80 m) and the DEM (about 59 m), but these causes are not separated here. The equilibrium model uses a constant albedo of 0.12. The test supports relative geometry at the scale of terrain features. It does not measure absolute position error. Next gate: compare temperatures with Diviner data at matched local time, and apply a photometric model (Lommel–Seeliger or Hapke) with local incidence and emission angles for the reflectance product.
