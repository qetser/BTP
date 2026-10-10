# E1G2 saturation sample findings

## 2026-10-03 — Fixed-line sample probe

- Sampled 16 scan lines spread across the complete 12,210-line E1G2 strip. At each line, included all 250 spatial samples across each of the 222 mode-valid bands: 888,000 band-pixel observations.
- The calibrated cube and table XML both declare radiance in `µW/cm**2/sr/µm`. Of the sample, 868,507 values (97.8048%) meet or exceed the saturation field as labeled. The result is close to, but below, the full-cube figure of 99.878921%; the mismatch persists in this sample.
- None of the paired raw counts reaches the official `Dynamic_Range` value. Sampled raw counts range from 0 to 8,439.
- The median of per-band sampled calibrated/LUT median ratios is 1.00139, but the per-band ratios range from 0.9060 to 1.0960. A single aggregate near one does not rule out band-dependent differences.
- Sampled saturation fractions are 96.35% to 99.70% by band. This range demonstrates why the aggregate sample percentage should not be treated as an instrument-wide estimate.
- These are candidate comparisons only. No threshold was converted into a mask, and zero, negative, or finite values were not assigned fill or validity meanings.

## Gate decision

The small sample reproduces the mismatch seen in the full-cube scan. It does not resolve the table's operational meaning, identify fill encoding, or justify a Level-1 mask. Keep M1 saturation/fill semantics and the downstream M2 processing gate open.

## 2026-10-03 — Compare saturation values with the LUT at Dynamic_Range by mode

- For each of 222 E1G2-valid and 127 E3G2-valid bands, applied all 250 sample-column LUT gain/offset coefficients to the saturation table's `Dynamic_Range` count. The E1G2 saturation table numbers use 1-based band rows; E3G2 uses 0-based rows. The analysis maps both to 1-based band numbers for comparison.
- The median predicted E1G2 LUT radiance divided by the saturation number is 1.559 if that number is treated counterfactually as mW (10th–90th percentile 1.028–1.856). For E3G2 the same counterfactual median is 5,118 (10th–90th percentile 1,029–8,993). Both saturation XML labels declare µW.
- E1G2 therefore has a closer numeric scale under the counterfactual mW reading, but that reading does not generalize across modes. The check does not prove a label error. Predicted values vary by band and the operational meaning of `Dynamic_Range` is not fully established.
- The table check uses official calibration metadata only. It does not resolve fill encoding, classify cube pixels, or authorize a Level-1 mask.
- Next local check: compare actual raw E3G2 counts and LUT predictions with both available calibrated products, preserving their distinct `m65` and `d18` unit declarations. Keep the mask and M2 gates open.
