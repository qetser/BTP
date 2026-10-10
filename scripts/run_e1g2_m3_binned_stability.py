#!/usr/bin/env python3
"""Re-test E1G2 spectral-unit stability on spatially binned spectra.

Run from the repository root after scripts/run_e1g2_m3_spectral_units.py:
  uv run --no-project --with numpy --with matplotlib --with scikit-learn \
      python scripts/run_e1g2_m3_binned_stability.py

The pixel-scale run failed the geographic stability gate (block-split ARI at or
below 0.60 against a 0.8 target). This test averages the same preprocessed
reflectance over B x B pixel bins (B = 1, 2, 4, 8; a bin is kept when at least
half its pixels are valid), then repeats the same features, PCA (4 components),
k-means (k = 3-8), and the same stability tests. Even/odd blocks are 500 source
lines. The 0.8 target and selection rule are unchanged from the pixel run.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/e1g2"
MOD = ROOT / "results/phase-1/m3-spectral-units"
BINS = [1, 2, 4, 8]
K_RANGE = range(3, 9)
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK2, GRID = "#52514e", "#d9d8d4"


def bin_cube(cube, good, b):
    nb, nl, ns = cube.shape
    L, S = nl // b * b, ns // b * b
    c = np.where(good[None, :L, :S], cube[:, :L, :S], np.nan)
    c = c.reshape(nb, L // b, b, S // b, b)
    frac = good[:L, :S].reshape(L // b, b, S // b, b).mean(axis=(1, 3))
    with np.errstate(invalid="ignore"):
        out = np.nanmean(c, axis=(2, 4))
    return out, frac >= 0.5


def main():
    cube = np.load(DERIVED / "m3_preprocessed_reflectance.npy")
    good = np.load(DERIVED / "m3_preprocessed_good.npy")
    rows = []
    for b in BINS:
        cb, gb = bin_cube(cube, good, b)
        nl_b, ns_b = gb.shape
        idx = np.where(gb.ravel())[0]
        X = cb.reshape(cb.shape[0], -1)[:, idx].T
        ok = np.all(np.isfinite(X), axis=1) & np.all(X > 0, axis=1)
        idx, X = idx[ok], X[ok]
        f = np.hstack([X / X.mean(1, keepdims=True), np.log(X.mean(1, keepdims=True))])
        f = (f - f.mean(0)) / f.std(0)
        block = ((idx // ns_b) * b // 500) % 2
        rng = np.random.default_rng(42)
        n_fit = min(200_000, len(f))
        fit = rng.choice(len(f), n_fit, replace=False)
        Z = PCA(4, random_state=0).fit(f[fit]).transform(f)
        ev, od = np.where(block == 0)[0], np.where(block == 1)[0]
        n_half = min(150_000, len(ev), len(od))
        for k in K_RANGE:
            sub = rng.choice(len(Z), min(20_000, len(Z)), replace=False)
            km = KMeans(k, n_init=4, random_state=0).fit(Z[fit])
            sil = silhouette_score(Z[sub], km.predict(Z[sub]))
            km_e = KMeans(k, n_init=4, random_state=1).fit(Z[rng.choice(ev, n_half, replace=False)])
            km_o = KMeans(k, n_init=4, random_state=2).fit(Z[rng.choice(od, n_half, replace=False)])
            test = rng.choice(od, min(100_000, len(od)), replace=False)
            ari = adjusted_rand_score(km_e.predict(Z[test]), km_o.predict(Z[test]))
            seeds = [KMeans(k, n_init=1, random_state=s).fit(Z[fit]).predict(Z[test]) for s in range(5)]
            ari_seed = float(np.mean([adjusted_rand_score(seeds[0], s) for s in seeds[1:]]))
            rows.append([b, k, len(Z), float(sil), float(ari), ari_seed])
            print(rows[-1], flush=True)
    with (MOD / "metrics/e1g2_binned_stability.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["bin_px", "k", "samples", "silhouette", "ari_even_vs_odd_block_models",
                    "mean_ari_across_5_seeds"])
        w.writerows(rows)
    r = np.asarray(rows)
    passed = r[r[:, 4] >= 0.8]
    summary = {
        "target": "block-split ARI >= 0.8 (unchanged from pixel run)",
        "best_block_split_ari_by_bin": {int(b): float(r[r[:, 0] == b, 4].max()) for b in BINS},
        "best_k_by_bin": {int(b): int(r[r[:, 0] == b][np.argmax(r[r[:, 0] == b, 4]), 1]) for b in BINS},
        "configurations_passing": [[int(a), int(c)] for a, c in passed[:, :2]],
        "gate_passed": bool(len(passed)),
    }
    (MOD / "metrics/e1g2_binned_stability_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True, constrained_layout=True)
    for i, b in enumerate(BINS):
        m = r[:, 0] == b
        a1.plot(r[m, 1], r[m, 4], color=CAT[i], lw=2, marker="o", ms=5, label=f"{b}×{b} px bins")
        a2.plot(r[m, 1], r[m, 5], color=CAT[i], lw=2, marker="o", ms=5, label=f"{b}×{b} px bins")
    for a, t in ((a1, "Geographic stability: even vs odd block models"), (a2, "Seed stability")):
        a.axhline(0.8, color="#e34948", lw=1, ls=":")
        a.set_xlabel("number of units k")
        a.set_title(t, loc="left")
        a.set_ylim(0, 1.02)
        a.legend(frameon=False, fontsize=8)
    a1.set_ylabel("adjusted Rand index")
    fig.savefig(MOD / "figures/e1g2_binned_stability.png", dpi=160)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
