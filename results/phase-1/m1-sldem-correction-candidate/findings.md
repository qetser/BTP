# SLDEM correction candidate findings

## 2026-10-08 — Apply and validate the relative offset field

- Applied the training-only affine sample/scan offset field from the illumination-matched SLDEM2015 registration to a derived copy of the 1,476-node E1G2 geometry table.
- The candidate median absolute shifts are about 98.8 m east-west and 37.3 m north-south. Maximum absolute shifts are about 232.5 m and 99.4 m, respectively. These are approximate conversions using a spherical lunar radius.
- Independently recomputed offsets on the 34 held-out image ties without refitting or threshold tuning. The residuals reproduce the existing values within `1e-5` pixel: median 0.375 px, p95 1.487 px, RMSE 0.699 px.
- **Gate result:** The candidate is internally consistent with the held-out relative-registration result. It is not an absolute geolocation validation because its controls are DEM hillshade morphology matches, not surveyed points.
- The raw product and original geometry are unchanged. No reflectance or M³ comparison was performed. Preserve the candidate label and geometry uncertainty.
