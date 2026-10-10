# M4 transfer: foundation model inventory

Status: both models load and run as frozen feature extractors on this machine. This record covers setup only. No lunar evaluation was run. The record makes no lunar performance claim.

- Date: 2026-10-10
- Repository commit at time of record: `304c5e8` (the wrapper is not committed yet)
- Wrapper: `scripts/m4_foundation_features.py`
- Machine-readable values: `metrics/model_inventory.json`
- No figure: this record contains no computed research metric. The timings only check that the software runs.

Command:

```
/home/anirudhs/.local/bin/uv run --no-project --python 3.11 \
    --with torch==2.5.1 --with torchvision==0.20.1 --with timm==1.0.11 \
    --with einops==0.8.0 --with numpy==1.26.4 \
    python -I scripts/m4_foundation_features.py --selftest
```

API: `extract_features(model_name, cube, wavelengths_nm) -> (H, W, D)` float32. `model_name` is `hyperfree`, `hypersigma`, or `hypersigma_spec`.

## Sources and licenses

| Item | HyperFree | HyperSIGMA |
| --- | --- | --- |
| Repository | github.com/Jingtao-Li-CVer/HyperFree | github.com/WHU-Sigma/HyperSIGMA |
| Commit | `966f3e3c7deb0fbcff54874924174faaabdf182a` | `07e9ea24e3072fcb5c3a92a2bcb8185e43b295b9` |
| Paper | Li et al., CVPR 2025, arXiv:2503.21841 | Wang et al., IEEE TPAMI 2025, arXiv:2406.11519 |
| Code license | MIT | Apache-2.0 |
| Weights license (Hugging Face tag) | apache-2.0 | apache-2.0 |
| Checkpoint used | `HyperFree-b.pth` (ViT-B) | `spat-vit-base-ultra-checkpoint-1599.pth` and `spec-vit-base-ultra-checkpoint-1599.pth` (ViT-B) |
| Hugging Face revision | `69fb1d0bfa05f928ae77730c8277ecda5a0fbfd8` | `e0567395fbdfddbae994695baf5fc73358a1ec3c` |
| SHA-256 | `bf207bf0d6a64e5a5e939cffbb850b0c72e29dda894ef9eda8950958688664c3` | spat `df6584e8124a9916687a21193bad0516439c97ed712ba7a854e1843d3d5fabc7`, spec `662845ed9669c9fc8f39b18b19a10dff61792a9c8700b6bfea439815f7c86d6f` |
| Parameters used | 144.9 M image encoder (58.2 M are spectral weight dictionaries) | 90.0 M spatial encoder, 88.2 M spectral encoder |

All three SHA-256 values match the Hugging Face LFS records. The authors host both sets of weights on Hugging Face, so no login or Baidu download was needed. The files are stored under `data/models/`, which Git ignores.

## Spectral range and input

| Item | HyperFree | HyperSIGMA |
| --- | --- | --- |
| Pretraining data | About 41,900 AVIRIS images (224 channels, 400-2500 nm, 0.6-5 m) plus fMoW and SpaceNet multispectral images | 447,072 patches (64x64 px): EO-1 Hyperion L1Gst radiance (175 channels, 400-2500 nm) and GF-5 L1 DN (150 bands, 0.4-1.0 µm) |
| Data level | Not stated (radiance or reflectance) | Radiance and DN, divided by 4000. Not reflectance. |
| Overlap with 0.8-2.5 µm | Full. IIRS 845-2460 nm is inside the dictionary range. | Hyperion part: full, except the removed water-vapour bands. GF-5 part: 0.8-1.0 µm only. Each sample was 100 contiguous channels (about 1000 nm), so no sample covered the full IIRS range. |
| Wavelength handling | Native. Band centres select weights from an 85-entry key dictionary and a 10 nm grid dictionary (211 entries in the code; the paper says 221), with a 10 nm match tolerance. | None. The spatial patch embedding requires exactly 100 channels. |
| IIRS adapter in wrapper | Pass the IIRS band centres. For 110 bands at 845-2460 nm: 27 key entries and 164 grid entries match, and all 110 bands are used. | Linear interpolation per pixel onto 100 equally spaced wavelengths from 845.0 to 2460.0 nm (step 16.31 nm). This is the overlap of the input range with 400-2500 nm. |
| Image size, patch | Tile (default 256 px) resized so the long side is 1024, patch 16, 64x64 tokens | 64x64 tiles (fixed), spatial patch 8 (8x8 tokens); spectral branch: one token per band |
| Normalization | Each tile divided by its maximum. The GSD (default 80 m, divided by the resize ratio) sets the position embedding. | Pretraining: /4000. Wrapper default: reflectance unchanged (`hypersigma_scale=1.0`). This choice has not been tested. |
| Encoder output | Five maps: blocks 2, 5, 8, 11 (768-d) and neck (256-d). Default is stage 1 (block 5, 768-d), as in the authors' classification demo. | Spatial: 768-d per token, after the final LayerNorm. Spectral: 100 tokens of 768-d, averaged to one vector per tile. |
| Wrapper output D | 768 (256 with `hyperfree_stage=4`) | `hypersigma` 768 per pixel; `hypersigma_spec` 768 per tile, copied to each pixel |

## Selftest (random 64x64x110 cube, 845-2460 nm)

| Model | Output | GPU warm (s) | GPU first call incl. load (s) | CPU warm (s) |
| --- | --- | --- | --- | --- |
| hyperfree | (64, 64, 768) | 0.258 | 5.5 | 19.8 |
| hypersigma | (64, 64, 768) | 0.045 | 29.7 | 8.5 |
| hypersigma_spec | (64, 64, 768) | 0.045 | 0.06 (already loaded) | 7.9 |

GPU: H100 MIG 2g.20gb slice, about 11.7 GB free. Peak allocation was 3.7 GB. All outputs were finite, and repeated calls gave identical results. The HyperSIGMA first call is slow because each checkpoint file is about 1.4 GB and also holds optimizer state.

## Findings

1. The HyperSIGMA encoders were pretrained without a position embedding. The released `forward_encoder` does not add `pos_embed`, and the checkpoint `pos_embed` still has its initial std of 0.0200. The spectral encoder therefore treats the bands as an unordered set. Permuting the 100 input bands changed the tile embedding by at most 1.9e-6, compared with feature values up to 24.5. The spectral embedding therefore does not encode where an absorption band lies, although that position is what identifies a lunar mineral. The spatial encoder mixes all 100 channels in its first convolution, so it does depend on band order.
2. HyperSIGMA was pretrained on radiance and DN, never on reflectance. HyperFree's paper does not state the AVIRIS processing level. Both models are therefore off-domain for lunar reflectance before any Earth-to-Moon gap is considered.
3. HyperFree responds to the wavelength metadata. Shifting all band centres by -400 nm reduced the mean per-pixel cosine similarity to 0.934. Its dictionary matching takes the first input band within 10 nm, so the result depends slightly on band order (cosine 0.998 after a permutation with matching wavelengths).
4. The released code and checkpoints differ in small ways. The HyperFree checkpoint holds `semantic_blocks` and `semantic_neck` tensors, but the code defines `contras_modules`. These modules are not in the encoder forward path, so the extracted features are not affected. The HyperSIGMA fine-tuning notebooks discard the pretrained patch embedding, use PCA input, and add sparse sampling attention layers whose weights are not in the checkpoints. The wrapper uses the full-attention MAE encoders that the checkpoints contain.
5. Only 12 of HyperFree's 85 key wavelengths lie above 1000 nm (1240, 1375, 1575, 1575.5, 1610, 1640, 1650, 2050.25, 2130, 2195, 2217.5, 2500 nm). For IIRS, most of the SWIR is encoded through the 10 nm grid dictionary.

## Limitations and next gate

- The selftest uses random data. It shows that the software runs. It does not show that the features are useful.
- Results depend on several untested choices: the HyperFree tile size and GSD, and the HyperSIGMA scale factor.
- Next gate: run the wrapper on the E1G2 reflectance cube and compare the embeddings with the lunar labels from the separate labelling process. Use a held-out spatial split, and compare against the M3 spectral-parameter baseline.
