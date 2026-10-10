#!/usr/bin/env python3
"""Test IIRS temperature and reflectance against SLDEM2015 local solar incidence.

Run from the repository root after scripts/run_e1g2_m2_physical_pilot.py:
  uv run --no-project --with numpy --with matplotlib --with opencv-python-headless \
      --with pillow python scripts/run_e1g2_topographic_validation.py

SLDEM2015 is independent of IIRS. For each IIRS pixel, the local cosine of
solar incidence uses SLDEM slopes sampled through the provisional SLDEM-corrected
geometry and the per-line OAT sun azimuth (clockwise from north, the direction
selected by the earlier hillshade registration) and elevation. If IIRS
brightness temperature is physical surface emission, it should rise with local
cos(i) as predicted by radiative equilibrium. Pixels in cast shadow are not
modeled; pixels with local cos(i) <= 0.05 are excluded.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from register_iirs_to_sldem_hillshade import (  # noqa: E402
    LAT_MAX, LON_MIN, LUNAR_RADIUS_M, PIXELS_PER_DEGREE, build_dem_crop,
)

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/e1g2"
MOD = ROOT / "results/phase-1/m2-topographic-validation"
EMISSIVITY, BOND_ALBEDO, S0, SIGMA = 0.95, 0.12, 1361.0, 5.670374e-8
INK2, GRID = "#52514e", "#d9d8d4"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False})


def main():
    (MOD / "metrics").mkdir(parents=True, exist_ok=True)
    (MOD / "figures").mkdir(parents=True, exist_ok=True)
    dem, info = build_dem_crop()
    valid = np.isfinite(dem)
    src = np.where(valid, dem, np.nanmedian(dem)).astype(np.float32)
    gx = cv2.Sobel(src, cv2.CV_32F, 1, 0, ksize=3, scale=1.0 / 8.0)
    gy = cv2.Sobel(src, cv2.CV_32F, 0, 1, ksize=3, scale=1.0 / 8.0)
    top = LAT_MAX - 0.5 / PIXELS_PER_DEGREE
    left = LON_MIN + 0.5 / PIXELS_PER_DEGREE
    lat_dem = top - np.arange(dem.shape[0], dtype=np.float32) / PIXELS_PER_DEGREE
    dy = LUNAR_RADIUS_M * np.pi / (180.0 * PIXELS_PER_DEGREE)
    dz_de = gx / (dy * np.cos(np.deg2rad(lat_dem)))[:, None]
    dz_dn = -gy / dy
    del gx, gy, src

    latlon = np.load(DERIVED / "latlon.npy")
    mx = ((latlon[1] - left) * PIXELS_PER_DEGREE).astype(np.float32)
    my = ((top - latlon[0]) * PIXELS_PER_DEGREE).astype(np.float32)
    se = cv2.remap(dz_de, mx, my, cv2.INTER_LINEAR)
    sn = cv2.remap(dz_dn, mx, my, cv2.INTER_LINEAR)
    vref = cv2.remap(valid.astype(np.uint8), mx, my, cv2.INTER_NEAREST) > 0

    geom = np.loadtxt(DERIVED / "line_geometry.csv", delimiter=",", skiprows=1)
    az, el = np.deg2rad(geom[:, 3])[:, None], np.deg2rad(geom[:, 4])[:, None]
    sun_e, sun_n, sun_u = np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)
    norm = np.sqrt(se ** 2 + sn ** 2 + 1.0)
    cos_local = (-se * sun_e - sn * sun_n + sun_u) / norm
    cos_flat = np.broadcast_to(sun_u, cos_local.shape)
    slope_deg = np.degrees(np.arctan(np.sqrt(se ** 2 + sn ** 2)))

    bt = np.load(DERIVED / "brightness_temperature_K.npy")
    good = np.load(DERIVED / "quality_mask.npy") & vref & (cos_local > 0.05) & np.isfinite(bt)
    refl = np.load(DERIVED / "apparent_reflectance.npy", mmap_mode="r")
    bands = np.loadtxt(DERIVED / "bands.csv", delimiter=",", skiprows=1, usecols=(1,))
    k15 = int(np.argmin(np.abs(bands - 1500)))
    r15_flat = np.asarray(refl[k15])
    iof15 = r15_flat * cos_flat
    r15_topo = iof15 / np.clip(cos_local, 0.05, None)

    d_au = json.loads((ROOT / "results/phase-1/m2-thermal-brightness/metrics/"
                       "e1g2_m2_pilot_summary.json").read_text())["sun_moon_distance_au"]
    t_model = ((1 - BOND_ALBEDO) * S0 / d_au ** 2 * np.clip(cos_local, 0, None)
               / (EMISSIVITY * SIGMA)) ** 0.25

    x, y, ym = cos_local[good], bt[good], t_model[good]
    r_bt = float(np.corrcoef(x, y)[0, 1])
    r_iof = float(np.corrcoef(x, iof15[good])[0, 1])
    # Coefficient of variation of reflectance before and after local-incidence normalization.
    cv_flat = float(np.std(r15_flat[good]) / np.mean(r15_flat[good]))
    cv_topo = float(np.std(r15_topo[good]) / np.mean(r15_topo[good]))
    resid = y - ym
    bins = np.linspace(0.2, 1.0, 17)
    idx = np.digitize(x, bins)
    rows = []
    for i in range(1, len(bins)):
        m = idx == i
        if m.sum() < 500:
            continue
        rows.append([0.5 * (bins[i - 1] + bins[i]), int(m.sum()), float(np.median(y[m])),
                     float(np.quantile(y[m], 0.16)), float(np.quantile(y[m], 0.84)),
                     float(np.median(ym[m])), float(np.median(iof15[good][m]))])
    with (MOD / "metrics/e1g2_bt_vs_local_cos_incidence.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cos_local_incidence_bin_center", "pixels", "median_bt_K", "p16_bt_K",
                    "p84_bt_K", "median_equilibrium_model_K", "median_iof_1500nm"])
        w.writerows(rows)
    rows = np.asarray(rows)
    # Holdout-style check: fit linear BT ~ cos on even lines, evaluate on odd 500-line blocks.
    blk = (np.arange(bt.shape[0]) // 500) % 2
    blk2d = np.broadcast_to(blk[:, None], bt.shape)[good]
    p = np.polyfit(x[blk2d == 0], y[blk2d == 0], 1)
    pred = np.polyval(p, x[blk2d == 1])
    r2_hold = float(1 - np.sum((y[blk2d == 1] - pred) ** 2) / np.sum((y[blk2d == 1] - y[blk2d == 1].mean()) ** 2))
    summary = {
        "pixels_used": int(good.sum()),
        "pixels_excluded_low_or_negative_local_cos_i": int((np.load(DERIVED / "quality_mask.npy") & vref & (cos_local <= 0.05)).sum()),
        "local_slope_deg_p50_p95": [float(v) for v in np.quantile(slope_deg[good], [0.5, 0.95])],
        "pearson_bt_vs_local_cos_i": r_bt,
        "pearson_iof1500_vs_local_cos_i": r_iof,
        "bt_minus_equilibrium_K_p16_p50_p84": [float(v) for v in np.quantile(resid, [0.16, 0.5, 0.84])],
        "linear_fit_bt_vs_cos_even_blocks": {"slope_K": float(p[0]), "intercept_K": float(p[1])},
        "heldout_odd_500line_blocks_r2": r2_hold,
        "reflectance_1500nm_coefficient_of_variation_flat_vs_local_incidence": [cv_flat, cv_topo],
        "model": {"bond_albedo": BOND_ALBEDO, "emissivity": EMISSIVITY, "solar_constant": S0,
                  "sun_moon_distance_au": d_au},
        "dem": "SLDEM2015 512 ppd, tiles 00N_30N_315_360 and 30S_00S_315_360",
        "dem_crop_nodata": info["crop_nodata_total"],
    }
    (MOD / "metrics/e1g2_topographic_validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    step = 4
    lat_line = latlon[0].mean(axis=1)
    fig = plt.figure(figsize=(13, 7.5), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.5])
    for row, (img, cmap, lab, ttl) in enumerate([
            (np.where(vref, cos_local, np.nan), "gray", "cos(local incidence)",
             "Independent: SLDEM2015 local solar illumination, cos(i)"),
            (np.where(good, bt, np.nan), "inferno", "brightness temperature (K)",
             "IIRS brightness temperature, 4.5-4.9 µm")]):
        ax = fig.add_subplot(gs[row, :])
        v = img[::step]
        lo, hi = np.nanquantile(v, [0.01, 0.99])
        im = ax.imshow(v.T, aspect="auto", origin="lower", cmap=cmap, vmin=lo, vmax=hi,
                       extent=[lat_line[0], lat_line[-1], 0, 250], interpolation="nearest")
        ax.grid(False)
        ax.set_ylabel("sample")
        ax.set_title(ttl, loc="left")
        plt.colorbar(im, ax=ax, pad=0.01, fraction=0.03).set_label(lab)
    ax.set_xlabel("latitude (deg)")
    a1 = fig.add_subplot(gs[2, 0])
    sub = np.random.default_rng(0).choice(x.size, 60000, replace=False)
    a1.scatter(x[sub], y[sub], s=1, color=BLUE, alpha=0.08, lw=0)
    a1.fill_between(rows[:, 0], rows[:, 3], rows[:, 4], color=BLUE, alpha=0.2, lw=0)
    a1.plot(rows[:, 0], rows[:, 2], color=BLUE, lw=2, marker="o", ms=4, label="IIRS median (16-84%)")
    a1.plot(rows[:, 0], rows[:, 5], color=INK2, lw=1.5, ls="--", label="radiative equilibrium")
    a1.set_xlim(0.2, 1.0)
    a1.set_ylim(250, 390)
    a1.set_xlabel("cos(local solar incidence) from SLDEM2015")
    a1.set_ylabel("brightness temperature (K)")
    a1.set_title(f"Temperature follows terrain illumination (r = {r_bt:.2f})", loc="left")
    a1.legend(frameon=False, loc="lower right")
    a2 = fig.add_subplot(gs[2, 1])
    a2.hist(r15_flat[good], bins=200, range=(0.03, 0.25), histtype="step", color=ORANGE, lw=1.5,
            label=f"flat-surface incidence (CV {cv_flat:.2f})")
    a2.hist(r15_topo[good], bins=200, range=(0.03, 0.25), histtype="step", color=AQUA, lw=1.5,
            label=f"SLDEM local incidence (CV {cv_topo:.2f})")
    a2.set_xlabel("apparent reflectance at 1.5 µm")
    a2.set_ylabel("pixels")
    a2.set_title("Reflectance spread before and after local-incidence normalization", loc="left")
    a2.legend(frameon=False)
    fig.savefig(MOD / "figures/e1g2_topographic_validation.png", dpi=150)
    plt.close(fig)
    np.save(DERIVED / "cos_local_incidence.npy", cos_local.astype(np.float32))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
