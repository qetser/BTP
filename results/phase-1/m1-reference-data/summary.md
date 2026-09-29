# M1 independent reference-data plan

**Status:** Five M³ Level-2 candidates identified and label-reviewed. A sparse control-grid screen ranks `M3G20090206T010833_V01_L2` first for follow-up. No M³ image cube or valid-pixel array was downloaded, and no spectral validation was computed.

**Source data:** Candidate IIRS scene `20260227T1239538758` (E1G2), with local footprint of about 5.47°W–3.50°W and 6.53°S–26.86°N. Its geometry file contains 1,476 sparse coordinate records across 246 of 250 lines.

**Method:** Queried the PDS Orbital Data Explorer REST service for M³ `REFIMG` products using `loc=f` (footprint intersection) and the E1G2 bounds (-7° to 27° latitude, 354.5° to 356.5° east longitude). Reviewed all five PDS3 labels and recorded their IDs, observation times, dimensions, band count, thermal-correction flag, special-pixel value, and reflectance scale in [`m3_label_review.csv`](m3_label_review.csv). Retrieved ODE's geographic footprints in [`m3_ode_footprints.json`](m3_ode_footprints.json). Counted the 1,476 sparse IIRS geometry-table coordinates lying inside each M³ footprint using [`analyze_m3_control_grid_overlap.py`](../../../scripts/analyze_m3_control_grid_overlap.py).

**Observations:** `M3G20090206T010833_V01_L2` contains 1,033 of 1,476 IIRS geometry control points (69.99%) inside its ODE-reported footprint. The next candidate contains 703 (47.63%); the other three contain 259, 5, and 0. This ranks footprints for inspection only. The IIRS geometry grid is sparse and M³ per-pixel validity has not been checked. All five M³ labels describe 304-sample, 85-band Level-2 reflectance cubes, flag thermal correction as applied, declare -999.0 as a special pixel, and define stored 1.0 as 100% reflectance. The LROC archive exposes a 100 m/pixel global morphologic map. No WAC or M³ image cube is currently present under local `data/`.

**Limitations:** Control-point counts are not pixel-area or valid-pixel overlap fractions and cannot establish M³ coverage quality. No train/validation/test split applies to this footprint-screening diagnostic. WAC image matching can assess spatial registration but cannot establish IIRS radiometric calibration. M³ comparison applies to reflectance products, not the current IIRS radiance cube. Spectral response, pixel footprint, acquisition geometry, and residual registration differences must be handled before comparing spectra.

**Data version:** IIRS E1G2 geometry from observation `20260227T1239538758`; PDS ODE M³ footprint metadata queried at `2026-09-29T07:46:07.382` (service timestamp has no timezone suffix). WAC and M³ image product versions must be recorded at retrieval.

**Metric artifacts:** The table reports counts and percent of IIRS geometry control points inside each ODE footprint, from 1,476 source points. Split: not applicable to candidate screening. Machine-readable values: [`metrics/m3_control_grid_overlap.csv`](metrics/m3_control_grid_overlap.csv). Figure: [`figures/m3_control_grid_overlap.svg`](figures/m3_control_grid_overlap.svg). These are screening values, not geolocation residuals or reflectance errors.

**Code commit:** Candidate-query code is in commit `ff1b854`; the control-grid analysis code will be recorded with this result update.

**Next gate:** Review M³ pixel-location products and valid-pixel rules within the candidate 010833 footprint; confirm actual common valid coverage and estimate retrieval size. Then obtain only the selected M³ observation and a footprint-sized WAC reference. Confirm coordinate conventions and product versions before implementing registration or spectral comparisons. Keep mask semantics and independent radiance validation as separate M2 blockers.
