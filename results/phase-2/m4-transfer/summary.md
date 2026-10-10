# M4 Earth-to-Moon transfer: frozen linear probes (exploratory)

**Status:** Exploratory, pre-gate. The project plan starts M4 only after M3 passes, and that has not happened. This study was run early for the October review, on the same proxy labels, split and metrics as M3. The frozen Earth models transfer usefully: HyperSIGMA spatial reaches macro F1 0.67, the highest single result. A classical random forest on 64-pixel context spectra reaches 0.63 (0.66 with the 64-line guard), and the confidence intervals overlap heavily. **There is therefore no measurable gain from Earth pretraining beyond spatial context on these labels.** Only the linear-probe condition was run. Zero-shot and fine-tuning were not.

## Source and run

- Models: HyperFree-b (Li et al., CVPR 2025) and HyperSIGMA ViT-B spatial and spectral encoders (Wang et al., TPAMI 2025). Official Hugging Face weights, Apache-2.0. See the [model inventory](model_inventory.md) for hashes, licences and adapters.
- Input: the same provisional E1G2 reflectance as M3 (83 bands, 845–2460 nm). Masked pixels were filled with the scene-median spectrum before encoding and excluded from scoring.
- Adapters:
  - HyperFree uses its native wavelength-indexed weights.
  - HyperSIGMA input is linearly interpolated to 100 bands. Its spectral encoder gives one vector per 64 px tile.
- Embeddings: `scripts/extract_e1g2_foundation_embeddings.py`, float16 (12210, 250, 768) per model. On an H100 MIG slice this took 63 s (HyperFree), 92 s (HyperSIGMA spatial) and 81 s (spectral).
- Probe: one linear layer on standardized frozen embeddings, AdamW at 1e-3, early stopping on validation blocks, on the GPU.
- Split, labels, contact buffer and metrics are identical to [M3 supervised baselines](../../phase-1/m3-supervised-baselines/summary.md).
- Command: `uv run --no-project --python 3.11 --with numpy --with scipy --with matplotlib --with scikit-learn --with torch==2.5.1 python scripts/run_e1g2_m3_m4_benchmark.py --methods m4 --m4-features "HyperFree=data/derived/e1g2/emb_hyperfree.npy,HyperSIGMA spatial=data/derived/e1g2/emb_hypersigma.npy,HyperSIGMA spectral (tile-level)=data/derived/e1g2/emb_hypersigma_spec.npy"`.
- Code baseline `304c5e8`; scripts uncommitted at run time.
- Figure: [M3/M4 benchmark](figures/e1g2_m3_m4_benchmark.png).
- Values: [M4 CSV](metrics/e1g2_benchmark_m4.csv), [M4 JSON](metrics/e1g2_benchmark_m4.json), [64-line guard run, all methods](metrics/e1g2_benchmark_m3_ctx_m4_guard64.csv).

## Result

| Method | Macro F1 [95% CI] | Balanced acc. | Macro F1, 64-line guard |
|---|---|---|---|
| HyperFree frozen + linear probe | 0.54 [0.39, 0.63] | 0.62 | 0.52 |
| HyperSIGMA spatial frozen + linear probe | **0.67** [0.52, 0.76] | 0.73 | 0.67 |
| HyperSIGMA spectral (tile-level) + linear probe | 0.57 [0.40, 0.69] | 0.60 | 0.61 |
| *Reference: random forest, per-pixel spectra* | 0.50 [0.35, 0.62] | 0.57 | 0.51 |
| *Reference: random forest, 64 px context spectra* | 0.63 [0.47, 0.71] | 0.65 | 0.66 |

## Limits and next gate

- Only frozen linear probes were run on one scene, with proxy 1:5M labels, provisional reflectance and provisional geometry.
- HyperSIGMA never saw reflectance in pretraining, and its spectral encoder is band-order blind.
- An earlier HyperFree probe run on the CPU stopped earlier and scored 0.48, which shows probe-training variance of about 0.07.
- **The transfer gap is not yet quantified**, because labels and inputs are not validated.

Next gate: reviewed labels and more scenes; then zero-shot with spectral-library prototypes, controlled fine-tuning, and a matched-capacity spatial baseline trained from scratch.
