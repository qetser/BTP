# SLDEM relative geolocation correction candidate

**Status:** A training-fitted image-offset field was applied to a separate copy of the E1G2 sparse geometry table. The 34 predeclared held-out morphology ties reproduce their saved residuals. This validates relative fit consistency only; absolute geolocation remains provisional.

**Source data:** E1G2 observation `20260227T1239538758`, matched calibrated archive `ch2_iir_nci_20260227T1239538758_d_img_d18.zip`, SHA-256 `669465771c3b6e092b7da251c5e2c5b5041e57d5578cd25216e4aa818334d5d8`. Source geometry is the 1,476-node sparse grid from the calibrated product. The offset field and holdout ties come from the [SLDEM hillshade registration](../m1-sldem-hillshade/summary.md). No train/validation/test split applies; training ties fit the affine model and predeclared held-out ties validate it.

**Method:** Run `.venv/bin/python scripts/apply_sldem_relative_geometry_candidate.py`. The script reads the previously selected, training-fitted affine sample/scan offset model, evaluates it at each sparse geometry node, and samples the original interpolated geolocation grid at the shifted image coordinates. It does not modify the IIRS archive. It independently recomputes the held-out residuals from the saved offsets and requires agreement with the prior result within `1e-5` IIRS pixel.

**Units and data version:** Offsets are in IIRS image pixels. Coordinates are degrees east and north. Approximate shifts in metres use a 1,737,400 m lunar sphere. Data version is the 2026-02-27 E1G2 observation. Code base commit: `304c5e8bc880d754ecab0b75983c8370b73d033e`; script SHA-256: `8d1285459efe6a8c8d8efc5b284a496a5e32c52a7ac4b9f13cfd2bab0eab0220`.

**Observations:** The candidate predicts sample offsets from -3.135 to 3.100 pixels and scan offsets from -0.874 to 1.170 pixels across the sparse grid. Median absolute east and north shifts are about 98.8 m and 37.3 m; maximum absolute shifts are about 232.5 m and 99.4 m. For the 34 held-out ties, median residual is 0.375 pixel, p95 is 1.487 pixels, and RMSE is 0.699 pixel. These are the unchanged, previously reported held-out registration residuals, reproduced from stored observations.

See the [candidate coordinates](metrics/iirs_sldem_relative_geometry_candidate.csv), [summary values](metrics/iirs_sldem_relative_geometry_candidate_summary.json), and [shift figure](figures/iirs_sldem_relative_geometry_candidate.svg).

**Limitations:** The controls are image-morphology ties to a DEM-derived hillshade, not surveyed ground controls. Reproducing held-out residuals demonstrates that the saved model is applied consistently; it does not independently establish absolute position accuracy. The candidate has not been applied to an IIRS raster or used for M³ overlap or reflectance. This geometry result does not resolve radiance, saturation/fill, thermal-correction, or reflectance gates.

**Next gate:** Compare corrected coordinates with an independent correction product or independent absolute controls. Use the candidate for downstream spatial screening only when its provisional status is retained and geometry uncertainty is propagated.
