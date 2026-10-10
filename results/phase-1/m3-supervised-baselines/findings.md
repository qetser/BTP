# Findings

- **All learned baselines beat the majority class by a wide margin.** Macro F1 is 0.40–0.50 against 0.10. IIRS spectra therefore carry information that matches the USGS map units, even at 1:5M.
- **Spatial context is the largest single gain.** Averaging spectra over 64 × 64 px raises the random forest from 0.50 to 0.63. This happens because the labels are large polygons and the per-pixel spectra are noisy.
- **The from-scratch 1D CNN (0.49) does not beat the random forest (0.50).** With about 85,000 training pixels and noisy spectra, extra model capacity does not help here.
- **No sign of split leakage.** Widening the guard from 25 to 64 lines changes every method by 0.04 or less.
- **The physical band-parameter baseline is weakest (0.40).** Four hand-made parameters lose information that the full spectrum keeps. The 2 µm band depth is noisy (see the spectral-units module).
- **Failed or open gates:**
  - The labels are proxy, not reviewed.
  - There is a single scene, so no scene-level generalization is tested.
  - The wide confidence intervals mean that differences below about 0.1 are not significant.
