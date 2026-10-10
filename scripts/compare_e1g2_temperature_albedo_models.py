#!/usr/bin/env python3
"""Compare E1G2 brightness temperature with two radiative-equilibrium albedo laws.

Run from the repository root after scripts/run_e1g2_topographic_validation.py:
  uv run --no-project --with numpy --with matplotlib python scripts/compare_e1g2_temperature_albedo_models.py

Model T = [(1 - A) S cos(i) / (d^2 eps sigma)]^(1/4), with S = 1361 W/m2 and
eps = 0.95. Albedo laws:
- constant A = 0.12 (the pilot model);
- Hayne et al. (2017, JGR) incidence-dependent A(i) = A0 + a (i/45°)^3 + b (i/90°)^8,
  with a = 0.06, b = 0.25, evaluated for A0 = 0.07 (mare), 0.12 (average) and
  0.16 (highland) (A0 by terrain from Vasavada et al. 2012).
Inputs are the saved median brightness temperatures by SLDEM local cos(i) bin.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TOPO = ROOT / "results/phase-1/m2-topographic-validation/metrics"
MOD = ROOT / "results/phase-1/m2-thermal-brightness"
S0, EPS, SIGMA = 1361.0, 0.95, 5.670374e-8
INK2, GRID = "#52514e", "#d9d8d4"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"


def t_eq(cos_i, albedo, d_au):
    return ((1 - albedo) * S0 / d_au ** 2 * cos_i / (EPS * SIGMA)) ** 0.25


def hayne_albedo(cos_i, a0):
    inc = np.degrees(np.arccos(np.clip(cos_i, 0, 1)))
    return a0 + 0.06 * (inc / 45.0) ** 3 + 0.25 * (inc / 90.0) ** 8


def main():
    d_au = json.loads((TOPO / "e1g2_topographic_validation_summary.json").read_text())["model"]["sun_moon_distance_au"]
    data = np.loadtxt(TOPO / "e1g2_bt_vs_local_cos_incidence.csv", delimiter=",", skiprows=1)
    c, n, med, p16, p84 = data[:, 0], data[:, 1], data[:, 2], data[:, 3], data[:, 4]
    models = {"constant A=0.12": t_eq(c, 0.12, d_au)}
    for name, a0 in (("Hayne A0=0.07 (mare)", 0.07), ("Hayne A0=0.12 (average)", 0.12),
                     ("Hayne A0=0.16 (highland)", 0.16)):
        models[name] = t_eq(c, hayne_albedo(c, a0), d_au)
    w = n / n.sum()
    summary = {}
    rows = []
    for name, t in models.items():
        resid = med - t
        summary[name] = {"pixel_weighted_mean_residual_K": float(np.sum(w * resid)),
                         "pixel_weighted_rms_residual_K": float(np.sqrt(np.sum(w * resid ** 2)))}
    for i in range(len(c)):
        rows.append([c[i], int(n[i]), med[i]] + [float(models[k][i]) for k in models])
    with (MOD / "metrics/e1g2_temperature_vs_albedo_models.csv").open("w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["cos_local_incidence_bin_center", "pixels", "median_bt_K"] + [f"model_{k}" for k in models])
        wr.writerows(rows)
    (MOD / "metrics/e1g2_temperature_vs_albedo_models_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(7.5, 4.2), constrained_layout=True)
    ax.fill_between(c, p16, p84, color=BLUE, alpha=0.18, lw=0)
    ax.plot(c, med, color=BLUE, lw=2.2, marker="o", ms=4, label="IIRS median (16-84%)")
    for (name, t), col, ls in zip(models.items(), [INK2, AQUA, ORANGE, YELLOW], ["--", "-", "-", "-"]):
        ax.plot(c, t, color=col, lw=1.6, ls=ls,
                label=f"{name}: mean resid {summary[name]['pixel_weighted_mean_residual_K']:+.1f} K")
    ax.set_xlabel("cos(local solar incidence) from SLDEM2015")
    ax.set_ylabel("temperature (K)")
    ax.set_title("IIRS temperature against radiative-equilibrium albedo laws", loc="left")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.savefig(MOD / "figures/e1g2_temperature_vs_albedo_models.png", dpi=160)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
