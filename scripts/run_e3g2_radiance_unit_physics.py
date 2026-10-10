#!/usr/bin/env python3
"""Reflected-light radiance-unit test for the two 2020 E3G2 calibrated products.

Run from the repository root:
  uv run --no-project --with numpy --with matplotlib --with pvlib \
      python scripts/run_e3g2_radiance_unit_physics.py

The m65 label declares mW/cm**2/sr/µm and the d18 label declares µW/cm**2/sr/µm.
For each product, I/F = pi * L / (F / d^2) is computed on every 16th line over
the SIS VALID E3G2 bands, using the stored values under both unit readings and
per-line OAT solar zenith. E3G2 has no valid 4.5-4.9 µm bands, so no thermal
test is possible. Same solar spectrum and band model as the E1G2 pilot.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_e1g2_working_cube import descendants, first_text, parse_oat  # noqa: E402
from run_e1g2_m2_physical_pilot import band_solar, solar_spectrum  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "results/phase-1/m2-radiance-unit-physics"
VALIDITY = ROOT / "results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv"
PRODUCTS = {
    "m65": "20200208T0057589143_d_img_m65",
    "d18": "20200208T1245274109_d_img_d18",
}
INK2, GRID = "#52514e", "#d9d8d4"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TO_SI = {"µW": 1e-2, "mW": 10.0}  # per cm2 -> W m^-2 sr^-1 µm^-1


def sun_moon_au(when: datetime, moon_km: np.ndarray) -> float:
    jd = when.timestamp() / 86400.0 + 2440587.5
    n = jd - 2451545.0
    L = math.radians((280.460 + 0.9856474 * n) % 360)
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    r = 1.00014 - 0.01671 * math.cos(g) - 0.00014 * math.cos(2 * g)
    eps = math.radians(23.439 - 4e-7 * n)
    sun = r * np.array([math.cos(lam), math.cos(eps) * math.sin(lam), math.sin(eps) * math.sin(lam)])
    return float(np.linalg.norm(sun - moon_km / 1.495978707e8))


def main():
    lam, f = solar_spectrum()
    with VALIDITY.open(newline="") as fh:
        valid = [int(r["band_number"]) for r in csv.DictReader(fh) if r["E3G2_valid"] == "1"]
    out, rows = {}, []
    for tag, stem in PRODUCTS.items():
        base = ROOT / f"data/extracted/calibrated_{stem}"
        date = stem[:8]
        label = ET.parse(base / f"data/calibrated/{date}/ch2_iir_nci_{stem}.xml").getroot()
        unit = first_text(label, "unit")
        axes = {first_text(a, "axis_name"): int(first_text(a, "elements"))
                for a in descendants(label, "Axis_Array")}
        nb, nl, ns = axes["BAND"], axes["LINE"], axes["SAMPLE"]
        centers = np.array([float(e.text) for e in descendants(label, "center_wavelength")])
        start = datetime.fromisoformat(first_text(label, "start_date_time").replace("Z", "+00:00"))
        line_ms = float(first_text(label, "line_exposure_duration"))
        cube = np.memmap(base / f"data/calibrated/{date}/ch2_iir_nci_{stem}.qub", dtype="<f4",
                         mode="r", shape=(nb, nl, ns))
        oat_text = (base / f"miscellaneous/calibrated/{date}/ch2_iir_nci_{stem}.oat").read_text()
        oat = parse_oat(oat_text)
        mid = oat_text.splitlines()[len(oat_text.splitlines()) // 2]
        moon = np.array([float(mid[46 + 20 * i: 66 + 20 * i]) for i in range(3)])
        d_au = sun_moon_au(start, moon)
        lines = np.arange(0, nl, 16)
        sza = np.interp(start.timestamp() + lines * line_ms / 1000.0, oat[:, 0], oat[:, 1])
        idx = np.array([b - 1 for b in valid])
        F = band_solar(centers[idx], lam, f) / d_au ** 2
        sub = np.asarray(cube[idx][:, lines, :], dtype=np.float64)
        ok = np.all(np.isfinite(sub) & (sub > 0), axis=0)
        med = {}
        for u, s in TO_SI.items():
            iof = math.pi * sub * s / F[:, None, None]
            med[u] = np.array([np.median(iof[k][ok]) for k in range(len(idx))])
        stored = np.array([np.median(sub[k][ok]) for k in range(len(idx))])
        for k, b in enumerate(valid):
            rows.append([tag, unit, b, centers[b - 1], stored[k], med["µW"][k], med["mW"][k]])
        k15 = int(np.argmin(np.abs(centers[idx] - 1500)))
        out[tag] = {"label_unit": unit, "lines_sampled": int(len(lines)),
                    "solar_zenith_deg_range": [float(sza.min()), float(sza.max())],
                    "sun_moon_distance_au": d_au,
                    "median_stored_value_1500nm": float(stored[k15]),
                    "median_iof_1500nm_if_uW": float(med["µW"][k15]),
                    "median_iof_1500nm_if_mW": float(med["mW"][k15]),
                    "physically_plausible_unit": "µW" if 0.01 < med["µW"][k15] < 0.6 else
                    ("mW" if 0.01 < med["mW"][k15] < 0.6 else "neither")}
        out[tag]["label_unit_matches_physics"] = out[tag]["physically_plausible_unit"] in unit
        out[tag]["_wl"], out[tag]["_uw"], out[tag]["_mw"] = centers[idx], med["µW"], med["mW"]
    with (MOD / "metrics/e3g2_iof_by_band_under_unit_hypotheses.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "label_unit", "band_number", "center_nm", "median_stored_value",
                    "median_iof_if_uW", "median_iof_if_mW"])
        w.writerows(rows)
    clean = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in out.items()}
    (MOD / "metrics/e3g2_unit_test_summary.json").write_text(json.dumps(clean, indent=2) + "\n")

    plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True, constrained_layout=True)
    for ax, tag in zip(axs, PRODUCTS):
        o = out[tag]
        ax.plot(o["_wl"], o["_uw"], color=BLUE, lw=2, label="read as µW")
        ax.plot(o["_wl"], o["_mw"], color=ORANGE, lw=2, label="read as mW")
        ax.axhspan(0.02, 0.5, color=AQUA, alpha=0.12, lw=0)
        ax.axhline(1.0, color=INK2, lw=1, ls="--")
        ax.set_yscale("log")
        ax.set_xlabel("wavelength (nm)")
        ax.set_title(f"2020 E3G2 {tag}: label says {o['label_unit'].split('/')[0]}; "
                     f"physics says {o['physically_plausible_unit']}", loc="left")
        ax.legend(frameon=False)
    axs[0].set_ylabel("median I/F (shaded: lunar range 0.02-0.5)")
    fig.savefig(MOD / "figures/e3g2_radiance_unit_physical_test.png", dpi=160)
    print(json.dumps(clean, indent=2))


if __name__ == "__main__":
    main()
