# Notes

- Setup, checkpoints and adapters are recorded in [model_inventory.md](model_inventory.md) and [metrics/model_inventory.json](metrics/model_inventory.json). Code and weights live under the ignored `data/models/`.
- Embedding extraction: `uv run --no-project --python 3.11 --with torch==2.5.1 --with torchvision==0.20.1 --with timm==1.0.11 --with einops==0.8.0 --with numpy==1.26.4 python -I scripts/extract_e1g2_foundation_embeddings.py`. The first attempt failed on a read-only memory-mapped slice and was fixed with an explicit copy.
- The benchmark needs `torch==2.5.1`. The default PyTorch 2.14.1 targets CUDA 13.0, which this machine's 12.5 driver does not support, so it fell back to the CPU without error. The CPU run of the HyperFree probe (macro F1 0.48, 37 epochs) was stopped and replaced by the GPU run (0.54, 64 epochs). The difference indicates training variance.
- GPU: one H100 MIG 2g.20gb slice; process-level memory use is not visible to this user.
- Ideas not yet run: zero-shot nearest-prototype classification with RELAB or USGS library spectra; fine-tuning under a fixed budget; a from-scratch 64 px spatial CNN as the matched-capacity control; HyperFree stage-4 (256-d) features; and a `hypersigma_scale` sweep.
