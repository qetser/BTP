#!/usr/bin/env python3
"""Plot the exploratory E1G2 M3/M4 benchmark (macro F1 and balanced accuracy with 95% CIs).

Run from the repository root after scripts/run_e1g2_m3_m4_benchmark.py (m3, ctx and m4; guard 25):
  uv run --no-project --with numpy --with matplotlib python scripts/plot_e1g2_benchmark.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
M3 = ROOT / "results/phase-1/m3-supervised-baselines/metrics/e1g2_benchmark_m3.csv"
CTX = ROOT / "results/phase-1/m3-supervised-baselines/metrics/e1g2_benchmark_ctx.csv"
M4 = ROOT / "results/phase-2/m4-transfer/metrics/e1g2_benchmark_m4.csv"
OUTS = [ROOT / "results/phase-2/m4-transfer/figures/e1g2_m3_m4_benchmark.png",
        ROOT / "results/phase-1/m3-supervised-baselines/figures/e1g2_m3_m4_benchmark.png"]
FAMILY_COLOR = {"M3 reference": "#52514e", "M3 physical": "#1baf7a", "M3 classical": "#2a78d6",
                "M3 learned": "#6250d6", "M3 context control": "#eda100",
                "M4 transfer": "#eb6834"}
GRID = "#d9d8d4"


def read(path):
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    rows = read(M3) + (read(CTX) if CTX.exists() else []) + (read(M4) if M4.exists() else [])
    plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 0.45 * len(rows) + 1.6), sharey=True, constrained_layout=True)
    y = np.arange(len(rows))[::-1]
    for ax, key, lo, hi, title in ((axes[0], "macro_f1", "macro_f1_ci_lo", "macro_f1_ci_hi", "Macro F1"),
                                   (axes[1], "balanced_accuracy", "ba_ci_lo", "ba_ci_hi", "Balanced accuracy")):
        for yi, r in zip(y, rows):
            v, a, b = float(r[key]), float(r[lo]), float(r[hi])
            col = FAMILY_COLOR.get(r["family"], "#52514e")
            ax.plot([a, b], [yi, yi], color=col, lw=2, alpha=0.5)
            ax.plot(v, yi, "o", color=col, ms=8, mec="white", mew=1.5)
            ax.text(b + 0.01, yi, f"{v:.2f}", va="center", fontsize=8, color="#0b0b0b")
        ax.set_xlim(0, 1)
        ax.set_title(f"{title} (test blocks, 95% CI)", loc="left")
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([f"{r['method']}  [{r['family']}]" for r in rows])
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, ms=8, label=f) for f, c in FAMILY_COLOR.items()]
    fig.legend(handles=handles, frameon=False, fontsize=8, loc="outside lower center", ncol=len(handles))
    fig.suptitle("Exploratory E1G2 benchmark: 5 proxy geologic groups (USGS 1:5M), "
                 "frozen 250-line block split, 2 km contact buffer", x=0.01, ha="left")
    for out in OUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=160)


if __name__ == "__main__":
    main()
