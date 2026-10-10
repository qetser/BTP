# SLDEM correction candidate notes

- Reproduction command: `.venv/bin/python scripts/apply_sldem_relative_geometry_candidate.py`.
- Inputs: verified local calibrated E1G2 ZIP; `results/phase-1/m1-sldem-hillshade/metrics/iirs_sldem_hillshade_summary.json`; `results/phase-1/m1-sldem-hillshade/metrics/iirs_sldem_hillshade_ties.csv`.
- The affine coefficients were fit using training ties in the prior registration. This script does not fit a model or select a threshold.
- Corrected sparse coordinates are computed by evaluating the model at each source scan/pixel node, shifting that image coordinate by the predicted offset, and interpolating the original sparse geometry grid at the shifted location.
- Validation filters the saved tie CSV to the selected azimuth and held-out split, recomputes residuals from the observed offsets and saved coefficients, and checks them against stored residuals. This is a reproducibility check on the held-out result, not a new independent control set.
- Output CSV preserves source coordinates and adds candidate coordinates and approximate east/north shifts. JSON records model, source hashes, validation split, units, and limits. SVG plots the correction field and sparse-node displacements.
- No source data were modified. No mask, radiance correction, reflectance, or scientific label was produced.
