# Notes

- Run order: `build_e1g2_working_cube.py`, then `run_e1g2_m2_physical_pilot.py`, then `run_e1g2_topographic_validation.py`, then `run_e1g2_m3_spectral_units.py`. The last step takes about 3 minutes with 96 cores. Environment: scikit-learn 1.9.1 and NumPy 2.2.6.
- Ignored output: `data/derived/e1g2/spectral_units.npy` (int16; −1 means masked).
- Units are ordered by mean albedo so that colors are reproducible between runs. Categorical colors follow the fixed order of the reference palette.
- Feature latitudes in the figures come from the IAU gazetteer via the research notes: Flammarion 3.4°S, Sinus Medii western edge about 2°N, Rimae Bode deposit 11.6°N, Montes Apenninus about 19.5°N at this longitude, and Montes Archimedes 25.3°N. They mark positions, not mapped unit boundaries.
- The Clementine FeO algorithm needs R750 and R950. IIRS has no valid band at 750 nm, so it cannot be applied directly. An IIRS-specific FeO proxy would need calibration against a reference map.
- Open question: would PCA on spatially binned spectra (for example, 4×4 pixels) raise block-split stability above 0.8? Test this before adding more scenes.
