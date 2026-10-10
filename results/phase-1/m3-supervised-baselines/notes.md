# Notes

- Run order: preprocessing (`run_e1g2_m3_spectral_units.py`), then labels (`build_e1g2_geologic_labels.py`), then `run_e1g2_m3_m4_benchmark.py --methods m3`, then `--methods ctx`, then `--methods m3,ctx,m4 --guard 64`, then `plot_e1g2_benchmark.py`.
- PyTorch is pinned to 2.5.1 (CUDA 12.4). The newest default wheel (2.14.1, CUDA 13.0) cannot use this machine's 12.5 driver and silently falls back to the CPU.
- Bootstrap: per-test-block confusion matrices are summed over resampled blocks. This is exact and runs in under a second. An earlier version recomputed sklearn metrics on 460,000 pixels per resample and did not finish in 45 minutes; it was stopped and replaced.
- Band parameters: log reflectance at 1.58 µm; IBD 1 µm (continuum 0.85–1.58 µm); IBD 2 µm (1.58–2.45 µm); R2.4/R1.0.
- Spectral features: the spectrum divided by its mean, plus log mean (shape plus albedo), then standardized.
- CNN: three Conv1d blocks (32/64/64 channels), adaptive pooling, dropout 0.2, AdamW at 1e-3, batch 512, early stopping on validation accuracy with patience 5.
- Context control: `scipy.ndimage.uniform_filter` with a 64 px window over valid pixels only (normalized convolution). The window is centred, unlike HyperSIGMA's fixed tile grid.
- Ignored output: `data/derived/e1g2/benchmark_test_predictions_*.npy` (test indices, true labels, predictions per method).
