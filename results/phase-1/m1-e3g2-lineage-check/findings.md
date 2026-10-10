# E3G2 paired-lineage findings

## 2026-10-03 — Compare both E3G2 raw/LUT/calibrated pairs

- Streamed the two matched 2020 raw/calibrated pairs and scanned all pixels in the 127 mode-valid bands. Product identity and integrity values are in the inventory and JSON summary.
- The calibrated cubes are finite on valid bands. Exact zero/negative band-pixel counts reproduce the existing scan: 2,809/26 for `m65` and 3,059/26 for `d18`.
- Only one raw count in each scene reaches its per-band `Dynamic_Range` field. Raw maxima are 9,533 (`m65`) and 9,367 (`d18`) on valid bands.
- Reading the saturation threshold as XML-declared µW flags 99.99885% of valid band-pixels in `m65` and 99.99877% in `d18`. Reading the numeric threshold counterfactually as mW flags zero in either product. Neither scenario is a validated mask.
- Converted each calibrated product to mW using its own PDS4 unit. Applying the Appendix F LUT formula to fixed-grid raw counts yields median per-band archived-Level-1/LUT-stage ratios 0.000200 (`m65`) and 0.0001999 (`d18`), with median per-band correlations 0.898 and 0.924.
- The V6 user guide attributes differences between direct LUT calculations and archived calibrated products to downstream destriping and radiance post-processing. The measured ratio remains unreproduced because those steps and coefficients were not applied here. The ratio is not evidence of a LUT-scale error.

## Gate decision

This check does not resolve the saturation table or fill-value semantics. The V6 user guide attributes differences between direct LUT calculations and archived calibrated products to downstream destriping and radiance post-processing. The measured ratio remains unreproduced because those steps and coefficients were not applied here. Verify sample/index alignment and reproduce the documented downstream steps before drawing conclusions. Do not assign masks or proceed to reflectance from this result.
- **2026-10-10: the ~5000× gap is largely explained by exposure scaling.** E3G2 Level 1 ≈ E3G2 LUT stage × (E1G2 gain / 10). The median fitted-to-predicted ratio is 0.944 for both products. The E2G2, E3G2 and E4G2 LUT files are not absolute radiance gains. Bands in the 0.50–0.9 ratio tail remain unexplained. This is an inference from data, not a provider rule.
