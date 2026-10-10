# Findings

- The scene-level label gives sun azimuth 96.319246° and sun elevation 31.690699°. It does not identify the azimuth's positive direction. The clockwise-from-north hillshade hypothesis had training median gradient NCC 0.626. The reverse direction scored 0.203. Training matches selected the direction.
- We excluded candidate patches that touch DEM nodata or its one-pixel gradient boundary. The training-only score cutoff was 0.5039. It retained 116 of 155 training candidates and 34 of 40 held-out candidates.
- Held-out residuals use an affine offset model with Huber reweighting. The median is 0.375 IIRS px, p90 is 1.273 px, p95 is 1.487 px, RMSE is 0.699 px, and maximum is 1.665 px. The 34 matches cover five cross-track columns and four fixed spatial blocks. All five candidate relative-registration criteria pass.
- This improves on the WAC grid diagnostic, whose median and p95 exceeded the same limits. The result is relative image consistency against a DEM-derived illumination-matched morphology image. It does not establish absolute geolocation error, radiance accuracy, or corrected reflectance.
- The sparse IIRS coordinate grid still initializes reference sampling. A successful local fit can therefore coexist with a scene-wide geolocation bias or an error in the sparse-grid interpolation.
- DEM crops contain 6,718 nodata samples, about 0.01% of the local crop. Candidate patches that intersect these areas or their gradient boundary are now omitted. The report does not extrapolate these tie results to the omitted locations.
