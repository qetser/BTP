#!/usr/bin/env python3
"""Test whether the E3G2 Level-1 scale follows the E1G2 LUT gain scaled by exposure.

Run from the repository root:
  uv run --no-project --with numpy --with matplotlib python scripts/test_e3g2_lut_exposure_scaling.py

Observation: the official E2G2, E3G2 and E4G2 LUT "Multiplicative_Factor" values
are near 1 (E4G2 may be an identity table), while E1G2 holds absolute gains near
0.0019 mW/cm2/sr/µm per count. E1G2 uses a 1 ms exposure and the 2020 E3G2
products use 10 ms. Hypothesis: E3G2 Level-1 radiance = (E3G2 LUT-stage value)
x (E1G2 gain / exposure ratio 10). Per valid band, fit Level-1 (mW) against the
E3G2 LUT-stage value by least squares through the fixed grid, and compare the
slope with E1G2 gain / 10 (median over samples).
"""
from __future__ import annotations

import csv
import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "data/pradan/iir.zip"
VALIDITY = ROOT / "results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv"
OUT = ROOT / "results/phase-1/m1-e3g2-lineage-check"
PRODUCTS = {"m65": ("20200208T0057589143_d_img_m65", 1.0),        # stored mW
            "d18": ("20200208T1245274109_d_img_d18", 1e-3)}       # stored µW -> mW
BLUE, ORANGE, INK2, GRID = "#2a78d6", "#eb6834", "#52514e", "#d9d8d4"


def lut(z, mode):
    rows = [list(map(float, r)) for r in csv.reader(io.StringIO(
        z.read(f"iir/calibration/ch2_iirs_cal_{mode}_lut_coeff.csv").decode()))]
    return np.asarray(rows).reshape(256, 250, 2)


def axes_of(xml_path):
    root = ET.parse(xml_path).getroot()
    found = {}
    for a in root.iter():
        if a.tag.split("}")[-1] == "Axis_Array":
            kv = {c.tag.split("}")[-1]: c.text for c in a}
            found[kv["axis_name"]] = int(kv["elements"])
    return found["BAND"], found["LINE"], found["SAMPLE"]


def main():
    with ZipFile(OFFICIAL) as z:
        luts = {m: lut(z, m) for m in ("e1g2", "e2g2", "e3g2", "e4g2")}
    with VALIDITY.open(newline="") as fh:
        valid = [int(r["band_number"]) for r in csv.DictReader(fh) if r["E3G2_valid"] == "1"]
    table_rows = [[m, float(np.median(l[:, :, 0])), float(np.median(l[:, :, 1])),
                   bool(np.all(l[:, :, 0] == 1.0) and np.all(l[:, :, 1] == 0.0))]
                  for m, l in luts.items()]
    g1 = np.median(luts["e1g2"][:, :, 0], axis=1)   # per band, mW per count at 1 ms
    out_rows, summary = [], {"lut_tables": {r[0]: {"median_factor": r[1], "median_offset": r[2],
                                                   "identity_table": r[3]} for r in table_rows}}
    for tag, (stem, to_mw) in PRODUCTS.items():
        date = stem[:8]
        cal_dir = ROOT / f"data/extracted/calibrated_{stem}/data/calibrated/{date}"
        raw_dir = ROOT / f"data/extracted/raw_{stem}/data/raw/{date}"
        nb, nl, ns = axes_of(cal_dir / f"ch2_iir_nci_{stem}.xml")
        cal = np.memmap(cal_dir / f"ch2_iir_nci_{stem}.qub", dtype="<f4", mode="r", shape=(nb, nl, ns))
        raw = np.memmap(raw_dir / f"ch2_iir_nri_{stem}.qub", dtype="<u2", mode="r", shape=(nb, nl, ns))
        slopes = []
        for b in valid:
            L1 = np.asarray(cal[b - 1, ::16, ::5], dtype=np.float64) * to_mw
            stage = (np.asarray(raw[b - 1, ::16, ::5], dtype=np.float64) * luts["e3g2"][b - 1, ::5, 0]
                     + luts["e3g2"][b - 1, ::5, 1])
            ok = np.isfinite(L1) & (L1 > 0) & (stage > 0)
            s = float(np.sum(L1[ok] * stage[ok]) / np.sum(stage[ok] ** 2))
            pred = g1[b - 1] / 10.0
            r = float(np.corrcoef(L1[ok], stage[ok])[0, 1])
            slopes.append((b, s, pred, s / pred, r))
            out_rows.append([tag, b, s, pred, s / pred, r])
        sl = np.asarray(slopes)
        summary[tag] = {"median_fitted_slope_mw_per_stage_unit": float(np.median(sl[:, 1])),
                        "median_e1g2_gain_over_10": float(np.median(sl[:, 2])),
                        "median_ratio_fitted_over_predicted": float(np.median(sl[:, 3])),
                        "ratio_p05_p95": [float(v) for v in np.percentile(sl[:, 3], [5, 95])],
                        "median_correlation": float(np.median(sl[:, 4]))}
    with (OUT / "metrics/e3g2_lut_exposure_scaling_test.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "band_number", "fitted_slope_level1_mw_per_e3g2_stage_unit",
                    "e1g2_gain_over_exposure_ratio_10", "ratio_fitted_over_predicted", "correlation"])
        w.writerows(out_rows)
    (OUT / "metrics/e3g2_lut_exposure_scaling_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    r = np.asarray([row[1:] for row in out_rows], dtype=float)
    tags = [row[0] for row in out_rows]
    plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(8, 3.6), constrained_layout=True)
    for tag, col in (("m65", BLUE), ("d18", ORANGE)):
        m = np.array([t == tag for t in tags])
        ax.plot(r[m, 0], r[m, 3], color=col, lw=1.8, label=f"2020 E3G2 {tag}")
    ax.axhline(1.0, color=INK2, lw=1, ls="--")
    ax.set_yscale("log")
    ax.set_xlabel("band number")
    ax.set_ylabel("fitted Level-1 slope / (E1G2 gain / 10)")
    ax.set_title("Does E3G2 Level 1 = E3G2 LUT stage × E1G2 gain / exposure ratio?", loc="left")
    ax.legend(frameon=False)
    fig.savefig(OUT / "figures/e3g2_lut_exposure_scaling_test.png", dpi=160)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
