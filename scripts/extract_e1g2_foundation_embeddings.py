#!/usr/bin/env python3
"""Extract frozen HyperFree and HyperSIGMA embeddings for the whole E1G2 strip.

Run from the repository root (same environment as the wrapper):
  /home/anirudhs/.local/bin/uv run --no-project --python 3.11 \
      --with torch==2.5.1 --with torchvision==0.20.1 --with timm==1.0.11 \
      --with einops==0.8.0 --with numpy==1.26.4 \
      python -I scripts/extract_e1g2_foundation_embeddings.py [model ...]

Input: data/derived/e1g2/m3_preprocessed_reflectance.npy (83 bands,
845-2460 nm), the same reflectance used by the M3 baselines. Masked pixels are
filled with the scene-median spectrum so they do not distort neighbouring
tokens; they are excluded from scoring by the benchmark. The strip is processed
in 1,024-line chunks (a multiple of the 256 px HyperFree and 64 px HyperSIGMA
tiles). Output: data/derived/e1g2/emb_<model>.npy, float16 (12210, 250, 768).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m4_foundation_features import extract_features, pick_device  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/e1g2"
CHUNK = 1024


def main():
    models = sys.argv[1:] or ["hyperfree", "hypersigma", "hypersigma_spec"]
    cube = np.load(DERIVED / "m3_preprocessed_reflectance.npy", mmap_mode="r")
    good = np.load(DERIVED / "m3_preprocessed_good.npy")
    wl = np.loadtxt(DERIVED / "m3_preprocessed_wavelengths_nm.txt")
    nb, nl, ns = cube.shape
    med = np.nanmedian(np.asarray(cube[:, ::16, ::4]).reshape(nb, -1), axis=1).astype(np.float32)
    device = pick_device()
    for name in models:
        out = np.lib.format.open_memmap(DERIVED / f"emb_{name}.npy", mode="w+", dtype=np.float16,
                                        shape=(nl, ns, 768))
        t0 = time.time()
        for y0 in range(0, nl, CHUNK):
            y1 = min(nl, y0 + CHUNK)
            sub = np.ascontiguousarray(np.transpose(np.array(cube[:, y0:y1, :], dtype=np.float32), (1, 2, 0)))
            bad = ~good[y0:y1] | ~np.all(np.isfinite(sub), axis=2)
            sub[bad] = med
            emb = extract_features(name, sub, wl, device=device)
            out[y0:y1] = emb.astype(np.float16)
            print(f"{name}: lines {y0}-{y1} done, {time.time() - t0:.0f} s", flush=True)
        out.flush()
        del out


if __name__ == "__main__":
    main()
