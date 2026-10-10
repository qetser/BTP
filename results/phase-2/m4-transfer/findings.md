# Findings

- **Earth hyperspectral features carry useful lunar information.** All three frozen probes beat the per-pixel spectral random forest by point estimate: 0.54–0.67 against 0.50.
- **Most of HyperSIGMA's advantage is spatial context.** A random forest on 64-pixel window-mean spectra, with no pretraining, reaches 0.63 (0.66 with the 64-line guard), against HyperSIGMA spatial at 0.67. The intervals overlap almost completely. Pretraining benefit is not demonstrated.
- **No leakage effect.** HyperSIGMA spatial is 0.67 with both 25- and 64-line guards, although its 64 px tiles exceed the 25-line guard.
- **HyperFree, which is per-pixel and wavelength-aware, adds about 0.04 over the per-pixel random forest.** The intervals overlap. A second run scored 0.48, so this margin is within probe-training variance.
- **The HyperSIGMA spectral encoder scores 0.57–0.61 despite being band-order blind.** Its tile-level vector mostly encodes tile-scale brightness and texture statistics, consistent with the context finding.
- **Open gates recorded as findings:** pre-gate start, proxy labels, a single scene, no zero-shot and no fine-tuning, provisional reflectance, and an untested HyperSIGMA input scale (`hypersigma_scale = 1.0`).
