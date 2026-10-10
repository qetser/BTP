# M3 unsupervised reference: spectral parameters and spectral units (E1G2)

**Status:** First M3 reference baseline computed on one scene. The spectral-parameter maps (1.58 µm albedo, and 1 µm and 2 µm integrated band depth) show coherent geologic units. The k-means spectral units are reproducible across random seeds (ARI ≥ 0.95 for k = 3–6). They fail the geographic stability gate: models trained on alternate 500-line blocks agree at ARI 0.53–0.60, below the 0.8 target. These are spectral units, not mineral labels. No supervised model or held-out accuracy is reported, because no reviewed labels exist.

## Source and run

- Input: E1G2 apparent reflectance from [the M2 pilot](../m2-apparent-reflectance/summary.md), normalized by SLDEM local incidence ([topographic module](../m2-topographic-validation/summary.md)), 845–2460 nm. Pixels need local cos(i) > 0.2.
- Preprocessing, all scene-derived:
  1. Column flat field per band. This removes column-median differences by construction.
  2. Empirical polishing: divide by the ratio of the scene-median spectrum to its 4th-order polynomial fit. The coefficients range 0.949–1.053 ([values](metrics/e1g2_polishing_coefficients.csv)).
  3. Despiking: a band value more than 6 robust sigma from the median of its four nearest bands is replaced by that median. 548,786 band values were replaced, 8,183 pixels were dropped, and no columns were dropped.
  4. A 3-band running mean.
- Parameters: IBD 1 µm with a linear continuum from 0.85 to 1.58 µm, and IBD 2 µm from 1.58 to 2.45 µm. These are adapted from the M³ definitions, because IIRS has no valid band below 813 nm, so the 699 nm anchor is unavailable.
- Units: PCA with 4 components, fitted on 200,000 random pixels, applied to the shape vector (spectrum divided by its mean) plus log albedo, standardized. Then k-means for k = 3–8.
- Split: the stability test fits separate models on even and odd 500-line blocks and compares their labels on odd-block pixels. Seed stability compares 5 random initializations.
- Command: `uv run --no-project --with numpy --with matplotlib --with scikit-learn python scripts/run_e1g2_m3_spectral_units.py`. Code baseline `304c5e8`; script SHA-256 `14d32e01…47f3`.
- Figures: [parameter maps, unit spectra, and model selection](figures/e1g2_spectral_parameters_and_unit_spectra.png), and [spectral-unit map](figures/e1g2_spectral_unit_map.png).
- Values: [model selection](metrics/e1g2_kmeans_model_selection.csv), [unit summary](metrics/e1g2_spectral_unit_summary.csv), [unit median spectra](metrics/e1g2_spectral_unit_median_spectra.csv), and [run summary](metrics/e1g2_spectral_units_summary.json).

## Result

| Unit | Share | Albedo 1.58 µm | IBD 1 µm | IBD 2 µm | Median latitude | Location in the strip |
|---|---|---|---|---|---|---|
| 1 | 12.8% | 0.079 | 0.029 | 0.015 | 10.9°N | Rimae Bode dark mantle deposit (about 9.5–14°N) and the Sinus Medii edge (about 1–3.5°N) |
| 2 | 14.3% | 0.091 | 0.022 | 0.014 | 20.5°N | Dark smooth plains north of Montes Apenninus (about 19–22.5°N) |
| 3 | 24.0% | 0.099 | 0.023 | 0.011 | 5.0°N | Intermediate terrain (about 0–9°N) |
| 4 | 21.7% | 0.113 | 0.013 | 0.013 | 17.1°N | Apennine and Archimedes uplands |
| 5 | 8.1% | 0.131 | 0.010 | 0.017 | 16.5°N | Bright slopes and fresh material |
| 6 | 19.2% | 0.132 | 0.018 | 0.008 | 2.2°S | Southern highlands (south of about 0°) |

- The darkest unit has the deepest 1 µm band and the steepest red slope beyond 2 µm. It coincides with the Rimae Bode regional pyroclastic deposit (Pigue et al., LPSC 2022, abstract 2128), where Fe-bearing volcanic glass is reported. This is a spatial association only, not a mineral identification.
- PCA: PC1 explains 52.0% of variance, PC2 18.5%, PC3 3.8%, and PC4 2.3%.
- Stability across k = 3–8: seed ARI ranges 0.70–0.99, block-split ARI 0.33–0.60, and silhouette 0.25–0.29. No k reached the 0.8 block-split target. The fallback k = 6 is the one with the highest block-split ARI.

## Limits and next gate

The low silhouette and block-split ARI show that spectral variation along the strip is mostly continuous. Unit boundaries therefore depend on which terrain a model was trained on. IBD 1 µm and IBD 2 µm are almost uncorrelated pixel by pixel (r = 0.02). The 2 µm parameter is noisy, and the 1 µm continuum is truncated at 0.85 µm. Polishing removes any feature that the whole scene shares. There is one scene and no labels. Next gate: add scenes from other provinces, build reviewed labels (for example from published FeO maps or M³-derived units), and then train supervised models on a frozen geographic split.

## Binned stability re-test (2026-10-10)

Command: `uv run --no-project --with numpy --with matplotlib --with scikit-learn python scripts/run_e1g2_m3_binned_stability.py`. The same preprocessed reflectance was averaged over 1×1, 2×2, 4×4 and 8×8 pixel bins, and the same features, PCA, k range, and stability tests were repeated. The best block-split ARI was 0.603 for 1×1, 0.604 for 2×2, **0.709 for 4×4 (k = 5)**, and 0.580 for 8×8. **No configuration reached 0.8, so the gate still fails.** Seed stability stays at or above 0.71. Values: [binned CSV](metrics/e1g2_binned_stability.csv), [summary](metrics/e1g2_binned_stability_summary.json). Figure: [binned stability](figures/e1g2_binned_stability.png).
