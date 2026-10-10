# M1 WAC 2D tie-grid diagnostic

**Status:** Geometry quality gate failed. This is relative image-registration evidence, not absolute geolocation validation.

## Source and method

- **IIRS:** 2026-02-27 E1G2 observation `20260227T1239538758`, calibrated band 40 at 1369.6 nm, 250 samples by 12,210 lines. The display-stretched band was used for morphology matching only.
- **Reference:** LROC WAC global morphology crop, 100 m/pixel, source ETag `"e2137517b2bb1afa7232c407ebbd1ada"`.
- **Method:** 2D gradient normalized-correlation matching at five sample columns, with parabolic subpixel peak refinement. A 25th-percentile score cutoff was computed from training candidates only. A robust affine 2D offset model was fit on training blocks and evaluated on held-out 750-line blocks with 150-line guards.
- **Split:** 41 training ties; 17 held-out ties across five held-out blocks and all five cross-track columns. Scores and residuals are in IIRS pixels.
- **Software:** Python 3.11.16, NumPy 2.2.6, OpenCV 4.14.0, Matplotlib 3.11.2. Environment requirements and lock are in the repository root.
- **Code state:** generated from the working tree based on repository HEAD `304c5e8bc880d754ecab0b75983c8370b73d033e`; the new script was uncommitted at run time.

## Result

Held-out median residual was **2.236 px**, p95 **6.343 px**, and RMSE **3.572 px**. The held-out median residual exceeded 1 px and p95 exceeded 2 px. All five cross-track columns and five spatial blocks were represented. Approximate 10 km line bins with at least three ties included medians up to 5.619 px. Only 17 held-out matches remain after the score cutoff, so tail quantiles are uncertain at this sample size.

The candidate criteria therefore fail. The result does not establish absolute geolocation error because the ties are image matches against WAC, not surveyed controls. Illumination and morphology differences can also reduce match quality.

A second run with the same inputs and environment reproduced the tie CSV and summary JSON byte-for-byte.

## Artifacts

- [Per-tie CSV](metrics/iirs_wac_2d_grid_ties.csv)
- [Metric JSON](metrics/iirs_wac_2d_grid_summary.json)
- [Residual figure](figures/iirs_wac_2d_grid_residuals.svg)
- [Implementation](../../../scripts/register_iirs_to_wac_grid.py)

## Next gate

Do not tune the affine model against these held-out ties. Pursue the illumination-matched hillshade or the independent ISRO correction tool, then evaluate with a fresh spatial holdout or independent controls. Keep reflectance and M3 scoring gated on validated geometry and masks.
