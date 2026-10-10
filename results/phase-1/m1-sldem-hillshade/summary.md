# SLDEM2015 hillshade registration diagnostic

**Status:** Candidate relative-registration criteria pass for the 2026 E1G2 scene. This does not validate absolute geolocation or radiometry.

## Source and run

- Observation: `20260227T1239538758`, calibrated band 40 (1,369.6 nm), display image used only for morphology matching.
- Reference: NASA/GSFC SLDEM2015, north and south 512-pixel/degree tiles for 315–360°E, acquired from the [official tile index](https://imbrium.mit.edu/DATA/SLDEM2015/TILES/JP2/). The product description is available from [NASA/GSFC PGDA](https://pgda.gsfc.nasa.gov/products/54).
- Run command: `.venv/bin/python scripts/register_iirs_to_sldem_hillshade.py`
- Split: training matches sit outside four fixed held-out line blocks. Each block has a 150-line guard. Thirty-four accepted held-out matches span five cross-track columns and all four blocks. We excluded candidate patches that touch DEM nodata or its one-pixel gradient boundary.
- Units: residuals use IIRS pixels (80 m nominal image sampling). DEM spacing is about 59 m/pixel. We interpolate its hillshade into the initial sparse-geometry map.
- Code baseline commit: `304c5e8bc880d754ecab0b75983c8370b73d033e`. The registration script had no commit at run time. Script SHA-256: `969f939350a765350731df264a8f5d104eaf78d19044a9f2cf8b35189fe64eae`.
- Figure: [held-out tie residuals and matched images](figures/iirs_sldem_hillshade_tie_residuals.svg).
- Machine-readable values: [all candidate tie rows](metrics/iirs_sldem_hillshade_ties.csv) and [run summary](metrics/iirs_sldem_hillshade_summary.json).

## Result

We evaluated both possible sun-azimuth directions. Training scores selected the clockwise-from-north direction (median NCC 0.626 versus 0.203). We set the match-score cutoff at the 25th percentile of training scores. The held-out median residual was 0.375 px, p95 was 1.487 px, and RMSE was 0.699 px. All five prewritten relative-registration criteria passed. The largest qualifying 10 km-bin median was 1.089 px. The cutoff retained 116 of 155 training candidates and 34 of 40 held-out candidates.

## Limits and next gate

The tie residual is the difference between each matched offset and an affine offset field fit with Huber reweighting on training ties. It measures whether held-out image matches agree with that field. It is not a surveyed absolute position error. This run does not write offset-adjusted coordinates to an IIRS product. The sparse IIRS geometry initializes DEM sampling. The sun angles are scene-level values, and the selected azimuth is an image-match hypothesis. Absolute geolocation remains provisional. The script rejects template patches and candidate search windows that touch nodata or its gradient boundary. Compare absolute locations with the independent ISRO correction output or other controls before using them for M³ or physical geometry. Radiance, saturation/fill, reflectance, and thermal gates remain open.
