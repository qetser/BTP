# Findings

- The five-column tie grid is feasible with the current full-resolution E1G2 band and WAC crop.
- The training-only score cutoff was 0.2261. It retained 41 of 55 training candidates and 17 of 25 held-out candidates.
- Held-out residuals do not meet the candidate limits of median <= 1 IIRS pixel and p95 <= 2 pixels. The median is 2.236 px; p95 is 6.343 px.
- Held-out ties span all five cross-track columns and five spatial blocks. This improves spatial coverage over the earlier x=125-only tie set, but does not solve the residual error.
- Only 17 held-out ties pass the training-derived score threshold; p95 and local-bin summaries are therefore uncertain.
- Approximate 10 km bins with at least three held-out ties have a worst median residual of 5.619 px, above the candidate 1.5 px limit.
- The run is relative registration against WAC. It cannot establish absolute geolocation accuracy, radiometric calibration, or mask validity.
- Keep the geometry gate open. Do not tune on this holdout; evaluate the hillshade/ISRO-tool route with new held-out regions or control points.
