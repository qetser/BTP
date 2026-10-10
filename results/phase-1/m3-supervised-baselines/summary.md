# M3 supervised baselines on proxy geologic labels (exploratory)

**Status:** Exploratory, pre-gate. Five baselines and three spatial-context controls were trained and scored on one frozen geographic split of the E1G2 strip. All beat the majority class clearly. Per-pixel spectral methods reach macro F1 0.46–0.50. Adding 64-pixel spatial context raises the best classical result to 0.63. The labels are proxy groups from the USGS 1:5M geologic map, not reviewed ground truth, so these scores measure agreement with coarse map units in one scene.

## Source and run

- Input: provisional E1G2 apparent reflectance, 845–2460 nm, 83 bands. It is topography-normalized, destriped, polished and despiked (`data/derived/e1g2/m3_preprocessed_reflectance.npy`, from [the spectral-units module](../m3-spectral-units/summary.md)).
- Labels: the five coarse groups from [the proxy geologic labels](../m3-geologic-labels/notes.md): mare, dark mantle, highland/terra, crater, basin. A pixel is used only when every pixel within 25 px (about 2 km) has the same label, because a 2 km map shift changes 21% of unit labels.
- Split: frozen before scoring. Lines are cut into 250-line blocks in the repeating order train, train, val, test. 25 lines at each block edge are dropped (a 64-line leakage control was also run). At most 20,000 training pixels per class are used. Validation is used only for CNN early stopping.
- Test pixels per class: mare 144,974; dark mantle 10,209; highland 60,514; crater 10,790; basin 236,387.
- Metrics: macro F1 and balanced accuracy on all test pixels, with 95% intervals from 1,000 resamples of the test blocks.
- Commands: `uv run --no-project --python 3.11 --with numpy --with scipy --with matplotlib --with scikit-learn --with torch==2.5.1 python scripts/run_e1g2_m3_m4_benchmark.py --methods m3` (and `--methods ctx`), then `scripts/plot_e1g2_benchmark.py`. The CNN ran on the GPU (CUDA).
- Code baseline `304c5e8`; scripts uncommitted at run time.
- Figure: [benchmark](figures/e1g2_m3_m4_benchmark.png).
- Values: [M3 CSV](metrics/e1g2_benchmark_m3.csv), [M3 JSON](metrics/e1g2_benchmark_m3.json), [context control CSV](metrics/e1g2_benchmark_ctx.csv), and [64-line guard run](../../phase-2/m4-transfer/metrics/e1g2_benchmark_m3_ctx_m4_guard64.csv).

## Result

| Method | Family | Macro F1 [95% CI] | Balanced acc. | Macro F1, 64-line guard |
|---|---|---|---|---|
| Majority class | reference | 0.10 [0.03, 0.17] | 0.20 | 0.10 |
| Band parameters + nearest centroid | physical | 0.40 [0.31, 0.51] | 0.45 | 0.42 |
| Spectra PCA20 + logistic regression | classical | 0.46 [0.34, 0.56] | 0.53 | 0.48 |
| Spectra + random forest | classical | 0.50 [0.35, 0.62] | 0.57 | 0.51 |
| 1D spectral CNN (from scratch, GPU) | learned | 0.49 [0.35, 0.61] | 0.56 | 0.52 |
| 64 px context, band parameters | context control | 0.48 [0.33, 0.63] | 0.51 | 0.52 |
| 64 px context, logistic regression | context control | 0.58 [0.43, 0.69] | 0.59 | 0.57 |
| 64 px context, random forest | context control | **0.63** [0.47, 0.71] | 0.65 | 0.66 |

## Limits and next gate

The labels are 1:5M map units with uncertain boundaries, so a perfect score is not expected or meaningful. There is one scene, so classes are spatially clustered, and the confidence intervals are wide (about ±0.12). The from-scratch CNN does not beat the random forest. The context controls show that spatial averaging, not model capacity, gives the largest gain. Next gate: reviewed labels, scenes from other provinces with scene-level splits, and photometrically corrected reflectance.
