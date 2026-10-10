# E1G2 brightness temperature against Diviner at matched local time

**Status:** Comparison done for 33 latitude bins (6.5°S to 26.5°N). IIRS 4.5–4.9 µm brightness temperature is warmer than the Diviner bolometric temperature by a median of +5.0 K (IQR +3.4 to +7.1 K; range +0.3 to +10.6 K). The bin profiles correlate with r = 0.81. The offset is positive in every bin, and its size lies inside the range expected from surface roughness at 4.7 µm. This closes the "Diviner comparison pending" gate as a consistency check. It is not an absolute calibration of IIRS radiance.

## Source and run

- IIRS: E1G2 `20260227T1239538758` brightness temperature from [the thermal module](../m2-thermal-brightness/summary.md) (4504–4875 nm, ε = 0.95, reflected part removed). Valid pixels from `quality_mask.npy`.
- Reference: Diviner Global Cumulative Product (GCP), `DATA_SET_ID = LRO-L-DLRE-5-GCP-V1.0`, files `global_cumul_avg_cyl_{10s00s,00n10n,10n20n,20n30n}_002.tab` (Williams et al. 2017, Icarus 283, 300–325). Nadir channel 3–9 and bolometric temperatures, 0.5° × 0.5° cells, 0.25 h local-time bins, observations from 2009-07-05 to 2015-04-01. Source, checksums and versions are in [notes](notes.md).
- Local time: subsolar point from each line's solar zenith and azimuth, giving subsolar longitude 52.75–52.82°E and subsolar latitude near 0°. IIRS local time is 8.12–8.24 h (about 08:07–08:15). It decreases from south to north because the strip runs slightly westward.
- Method: per 1° latitude bin, pool the GCP cells inside the bin over the strip longitudes (354.5–356.5°E; 4 to 6 cells). Take the median over cells per 0.25 h bin, then interpolate linearly to the bin's median IIRS local time. The 7.88 h and 8.12 h bins are mostly empty here, so every bin interpolates between 7.62 h and 8.38 h. Sensitivity case: a quadratic in local time fitted to all cell values over 7.0–9.5 h.
- Command: `uv run --no-project --with numpy --with matplotlib python scripts/compare_e1g2_diviner_temperature.py`. Code baseline `304c5e8` plus the new, uncommitted script.
- Split: no train/test split applies. Units: K and hours of lunar local time.
- Figure: [IIRS and Diviner profiles and differences](figures/e1g2_iirs_vs_diviner_temperature.png).
- Values: [per-latitude table](metrics/e1g2_iirs_vs_diviner_by_latitude.csv) and [run summary](metrics/e1g2_iirs_vs_diviner_summary.json).

## Result

| Quantity (over 33 bins) | Median | IQR | Range |
|---|---|---|---|
| IIRS − Diviner bolometric | +5.0 K | +3.4 to +7.1 K | +0.3 to +10.6 K |
| IIRS − Diviner bolometric, quadratic-fit sensitivity | +5.0 K | +2.8 to +7.0 K | −6.2 to +13.4 K |
| IIRS re-expressed with ε = 1 − Diviner bolometric | +3.2 K | +1.6 to +5.4 K | −1.5 to +8.9 K |
| IIRS − Diviner channel 3 (7.8 µm) | +3.2 K | +1.0 to +5.0 K | −3.1 to +8.2 K |
| Diviner channel 3 − bolometric | +2.1 K | +1.8 to +2.7 K | +1.1 to +4.2 K |

- The latitude profiles agree in shape (r = 0.81 for the interpolated case, 0.68 for the quadratic fit). Both instruments show the cold Montes Apenninus bin at 18°N (IIRS 311 K, Diviner 311 K) and the northward cooling past 20°N.
- Diviner reports brightness temperature with emissivity 1. IIRS uses ε = 0.95, which adds about 1.8 K. On a like-for-like ε = 1 basis, IIRS is +3.2 K warmer.
- Spectral bias: a rough surface mixes facets at different temperatures, so a short-wavelength brightness temperature exceeds the bolometric temperature. A Gaussian facet-temperature mix tuned to the observed Diviner channel 3 excess (+2.1 K, spread σ ≈ 46 K) predicts a 4.7 µm excess of about +12 K (IQR +10 to +13 K). This is an upper estimate, because part of the channel 3 excess comes from emissivity differences between channels. The expected 4.7 µm excess is therefore 0 to about +12 K. The observed +3.2 K (ε = 1) lies inside that range and is on the low side.
- The offset is larger in darker bins (r = −0.57 against 1.5 µm reflectance, 18°N excluded). Dark mare bins at 2–3°N, 12–13°N and 19–23°N give +6.5 to +10.6 K. Bright highland bins at 5°S and 14–16°N give +0.3 to +1.6 K.

## Limits and next gate

The GCP is a climatology over 2009–2015 and all seasons. It is not simultaneous with the 2026 observation. Solar distance varies by about ±1.7% over a year, which changes noon temperatures by about ±1.3 K. The morning temperature rises by about 35 K per hour near 08:00 (GCP pooled values: about 305 K at 7.62 h, 330 K at 8.38 h). Diviner has no data at 7.88 h and 8.12 h here, so the linear interpolation over 0.76 h can be wrong by a few kelvin. The quadratic-fit case changes the median by less than 0.1 K but widens the bin spread. The GCP cells (0.5°, about 15 km) are much larger than IIRS pixels, so the comparison is valid only at the bin level. The roughness model is a one-parameter sketch and does not replace a full roughness thermal model (Bandfield et al. 2015). The result supports the IIRS 4.7 µm radiance scale to within roughly ±10 K in temperature, or about ±15% in radiance at 4.7 µm. It cannot separate a radiance bias from roughness or emissivity effects. Next gate: obtain Diviner Level 1 RDR points near 08:10 local time to remove the interpolation gap, and test a published roughness model (Bandfield et al. 2015) for the 4.7 µm excess.
