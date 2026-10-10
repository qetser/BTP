#!/usr/bin/env python3
"""E1G2 M2 physical pilot: radiance-unit test, apparent reflectance, thermal tail.

Run from the repository root after scripts/build_e1g2_working_cube.py:
  uv run --no-project --with numpy --with scipy --with matplotlib --with pvlib \
      python scripts/run_e1g2_m2_physical_pilot.py

Method (all steps are provisional and use documented assumptions):
1. Solar spectrum: ASTM G173-03 extraterrestrial column (280-4000 nm, via pvlib),
   extended beyond 4000 nm with a 5778 K blackbody scaled to the 3800-4000 nm
   mean. Each band is a Gaussian with FWHM equal to the local band spacing,
   because the label gives no FWHM.
2. Sun-Moon distance: low-precision solar ephemeris plus the OAT geocentric
   lunar position.
3. Unit test: I/F = pi * L / (F / d^2) under the label unit (µW/cm2/sr/µm) and
   under the guide unit (mW/cm2/sr/µm). Apparent reflectance = I/F / cos(i)
   with per-line solar zenith from the OAT file (no topographic correction).
4. Thermal: brightness temperature in bands 4504-4875 nm after removing a
   reflected component with the 2.3-2.5 µm apparent reflectance held flat
   (emissivity 0.95). A linear 1.6-2.5 µm slope extrapolation is the
   sensitivity case.
5. Exploratory thermal removal over 2.5-3.6 µm and a 2.9 µm band depth. This is
   not a hydration result: the method is unvalidated and has no independent
   reference.
Large intermediates go to data/derived/e1g2/ (ignored by Git).
"""
from __future__ import annotations

import csv
import json
import math
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/e1g2"
SOLAR_CSV = ROOT / "data/reference/solar/astm_g173_extraterrestrial.csv"
OAT_ZIP = ROOT / "data/pradan/e1g2_candidate_20260227T1239538758/ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
OAT_PART = "miscellaneous/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.oat"
MOD_UNIT = ROOT / "results/phase-1/m2-radiance-unit-physics"
MOD_REFL = ROOT / "results/phase-1/m2-apparent-reflectance"
MOD_THERM = ROOT / "results/phase-1/m2-thermal-brightness"

C1 = 1.191042e8   # W µm^4 m^-2 sr^-1
C2 = 1.438777e4   # µm K
SIGMA = 5.670374e-8
EMISSIVITY = 0.95
BOND_ALBEDO = 0.12
S0 = 1361.0
JD_MID = 2461099.0277  # 2026-02-27 12:45 UTC
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.5,
                     "axes.spines.top": False, "axes.spines.right": False})


def planck(lam_um, t):
    return C1 / (lam_um ** 5 * (np.exp(C2 / (lam_um * t)) - 1.0))


def brightness_t(lam_um, rad):
    with np.errstate(invalid="ignore", divide="ignore"):
        return C2 / (lam_um * np.log1p(C1 / (lam_um ** 5 * rad)))


def solar_spectrum():
    if not SOLAR_CSV.exists():
        from pvlib.spectrum import get_reference_spectra
        s = get_reference_spectra(standard="ASTM G173-03")["extraterrestrial"]
        SOLAR_CSV.parent.mkdir(parents=True, exist_ok=True)
        s.to_csv(SOLAR_CSV, header=["extraterrestrial_W_m2_nm"], index_label="wavelength_nm")
    d = np.loadtxt(SOLAR_CSV, delimiter=",", skiprows=1)
    lam, f = d[:, 0], d[:, 1]
    tail = np.arange(4005.0, 5600.0, 5.0)
    bb = planck(tail / 1000.0, 5778.0)
    ref = planck(np.arange(3800.0, 4001.0, 5.0) / 1000.0, 5778.0).mean()
    scale = f[(lam >= 3800) & (lam <= 4000)].mean() / ref
    return np.concatenate([lam, tail]), np.concatenate([f, bb * scale])


def band_solar(centers_nm, lam, f):
    spacing = np.gradient(centers_nm)
    out = []
    for c, w in zip(centers_nm, spacing):
        sig = w / 2.3548
        g = np.exp(-0.5 * ((lam - c) / sig) ** 2)
        out.append(np.trapezoid(g * f, lam) / np.trapezoid(g, lam))
    return np.asarray(out) * 1000.0  # W m^-2 µm^-1 at 1 AU


def sun_moon_distance_au():
    from zipfile import ZipFile
    with ZipFile(OAT_ZIP) as z:
        rec = z.read(OAT_PART).decode().splitlines()[len(z.read(OAT_PART).decode().splitlines()) // 2]
    moon = np.array([float(rec[46 + 20 * i: 66 + 20 * i]) for i in range(3)]) / 1.495978707e8
    n = JD_MID - 2451545.0
    L = math.radians((280.460 + 0.9856474 * n) % 360)
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    r = 1.00014 - 0.01671 * math.cos(g) - 0.00014 * math.cos(2 * g)
    eps = math.radians(23.439 - 4e-7 * n)
    sun = r * np.array([math.cos(lam), math.cos(eps) * math.sin(lam), math.sin(eps) * math.sin(lam)])
    return float(np.linalg.norm(sun - moon)), float(r)


def strip_axes(fig, rows):
    return fig.subplots(rows, 1, sharex=True)


def show_strip(ax, img, lat_line, cmap, vmin, vmax, label):
    extent = [lat_line[0], lat_line[-1], 0, 250]
    im = ax.imshow(img.T, aspect="auto", origin="lower", extent=extent, cmap=cmap,
                   vmin=vmin, vmax=vmax, interpolation="nearest")
    ax.set_ylabel("sample")
    ax.grid(False)
    cb = plt.colorbar(im, ax=ax, pad=0.01, fraction=0.03)
    cb.set_label(label)
    return im


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                            text=True, cwd=ROOT).stdout.strip()
    for m in (MOD_UNIT, MOD_REFL, MOD_THERM):
        (m / "metrics").mkdir(parents=True, exist_ok=True)
        (m / "figures").mkdir(parents=True, exist_ok=True)
    bands = np.loadtxt(DERIVED / "bands.csv", delimiter=",", skiprows=1, usecols=(0, 1))
    band_no, nm = bands[:, 0].astype(int), bands[:, 1]
    um = nm / 1000.0
    geom = np.loadtxt(DERIVED / "line_geometry.csv", delimiter=",", skiprows=1)
    sza = geom[:, 2]
    mu0 = np.cos(np.radians(sza))
    latlon = np.load(DERIVED / "latlon.npy")
    lat_line = latlon[0].mean(axis=1)
    cube = np.load(DERIVED / "radiance_valid.npy", mmap_mode="r")
    nb, nl, ns = cube.shape

    lam, f = solar_spectrum()
    d_au, d_earth = sun_moon_distance_au()
    F = band_solar(nm, lam, f) / d_au ** 2  # W m^-2 µm^-1 at the Moon
    UW_TO_SI = 1e-2  # µW cm^-2 sr^-1 µm^-1 -> W m^-2 sr^-1 µm^-1

    # ---------- radiance (SI, label unit) and data-driven quality mask ----------
    rad = np.empty((nb, nl, ns), dtype=np.float32)
    for k in range(nb):
        rad[k] = cube[k] * UW_TO_SI
    finite_pos = np.all(np.isfinite(rad) & (rad > 0), axis=0)
    iof = np.empty_like(rad)
    for k in range(nb):
        iof[k] = math.pi * rad[k] / F[k]
    refl = iof / mu0[None, :, None].astype(np.float32)

    # ---------- module: radiance-unit physics ----------
    grid = (slice(None, None, 8), slice(None, None, 5))
    unit_rows = []
    for k in range(nb):
        v = iof[k][grid][finite_pos[grid]]
        q = np.quantile(v, [0.05, 0.5, 0.95])
        unit_rows.append([band_no[k], nm[k], F[k], *q, *(q * 1000.0)])
    write_csv(MOD_UNIT / "metrics/e1g2_iof_by_band_under_unit_hypotheses.csv",
              ["band_number", "center_nm", "solar_irradiance_W_m2_um_at_moon",
               "iof_p05_label_uW", "iof_median_label_uW", "iof_p95_label_uW",
               "iof_p05_guide_mW", "iof_median_guide_mW", "iof_p95_guide_mW"], unit_rows)
    unit_rows = np.asarray(unit_rows, dtype=float)

    # ---------- thermal brightness temperature ----------
    sel_t = (nm >= 4500) & (nm <= 4880)
    sel_flat = (nm >= 2300) & (nm <= 2500)
    sel_slope = (nm >= 1600) & (nm <= 2500)
    r_flat = refl[sel_flat].mean(axis=0)
    # Per-pixel linear slope over 1.6-2.5 µm for the sensitivity case.
    x = um[sel_slope] - um[sel_slope].mean()
    rs = refl[sel_slope]
    slope = np.tensordot(x, rs - rs.mean(axis=0), axes=(0, 0)) / np.sum(x ** 2)
    r_mean = rs.mean(axis=0)

    def bt_cube(rad_scale, refl_model):
        temps = []
        for k in np.where(sel_t)[0]:
            r_l = refl_model(um[k])
            reflected = r_l * F[k] * mu0[:, None] / math.pi
            thermal = rad[k] * rad_scale - reflected
            temps.append(brightness_t(um[k], np.where(thermal > 0, thermal / EMISSIVITY, np.nan)))
        return np.nanmedian(np.stack(temps), axis=0)

    bt = bt_cube(1.0, lambda l: r_flat)
    bt_slope = bt_cube(1.0, lambda l: r_mean + slope * (l - um[sel_slope].mean()))
    bt_mw = bt_cube(1000.0, lambda l: r_flat * 1000.0)
    t_eq_line = ((1 - BOND_ALBEDO) * S0 / d_au ** 2 * mu0 / (EMISSIVITY * SIGMA)) ** 0.25
    good = finite_pos & np.isfinite(bt)

    # ---------- exploratory thermal removal 2.5-3.6 µm ----------
    sel_tc = (nm >= 2450) & (nm <= 3650)
    tc_idx = np.where(sel_tc)[0]
    refl_tc = np.empty((len(tc_idx), nl, ns), dtype=np.float32)
    for j, k in enumerate(tc_idx):
        thermal = EMISSIVITY * planck(um[k], np.where(good, bt, 300.0))
        refl_tc[j] = math.pi * (rad[k] - thermal) / (F[k] * mu0[:, None])
    tc_nm = nm[tc_idx]
    np.save(DERIVED / "apparent_reflectance.npy", refl)
    np.save(DERIVED / "brightness_temperature_K.npy", bt.astype(np.float32))
    np.save(DERIVED / "thermally_corrected_reflectance_2450_3650.npy", refl_tc)
    np.save(DERIVED / "quality_mask.npy", good)

    def band_mean(arr, wl, lo, hi):
        s = (wl >= lo) & (wl <= hi)
        return arr[s].mean(axis=0)
    cont_lo = band_mean(refl_tc, tc_nm, 2450, 2600)
    cont_hi = band_mean(refl_tc, tc_nm, 3450, 3650)
    trough = band_mean(refl_tc, tc_nm, 2850, 2950)
    w = (2.9 - 2.525) / (3.55 - 2.525)
    bd29 = 1.0 - trough / ((1 - w) * cont_lo + w * cont_hi)

    # ---------- metrics: reflectance ----------
    r15 = band_mean(refl, nm, 1450, 1550)
    r075 = refl[0]
    lab = finite_pos
    q_dark, q_bright = np.quantile(r15[lab], [0.10, 0.90])
    dark = lab & (r15 <= q_dark)
    bright = lab & (r15 >= q_bright)
    spec_rows = []
    for k in range(nb):
        spec_rows.append([band_no[k], nm[k], float(np.median(refl[k][lab])),
                          float(np.median(refl[k][dark])), float(np.median(refl[k][bright])),
                          float(np.quantile(refl[k][lab], 0.05)), float(np.quantile(refl[k][lab], 0.95))])
    write_csv(MOD_REFL / "metrics/e1g2_apparent_reflectance_spectra.csv",
              ["band_number", "center_nm", "median_all", "median_darkest10pct_r1500",
               "median_brightest10pct_r1500", "p05_all", "p95_all"], spec_rows)
    col = r15.copy()
    col[~lab] = np.nan
    col_profile = np.nanmedian(col, axis=0)
    stripe = float(np.nanstd(col_profile / np.nanmedian(col_profile)))
    lat_bins = np.arange(-6.5, 27.5, 1.0)
    lat_idx = np.digitize(lat_line, lat_bins)
    lat_rows = []
    for i in range(1, len(lat_bins)):
        rows_i = lat_idx == i
        if not rows_i.any():
            continue
        m = good[rows_i]
        lat_rows.append([lat_bins[i - 1] + 0.5, float(sza[rows_i].mean()),
                         float(np.median(r15[rows_i][lab[rows_i]])),
                         float(np.median(bt[rows_i][m])), float(np.median(bt_slope[rows_i][m])),
                         float(np.quantile(bt[rows_i][m], 0.05)), float(np.quantile(bt[rows_i][m], 0.95)),
                         float(t_eq_line[rows_i].mean()),
                         float(np.nanmedian(bt_mw[rows_i])),
                         float(np.median(bd29[rows_i][m]))])
    write_csv(MOD_THERM / "metrics/e1g2_temperature_by_latitude.csv",
              ["lat_center_deg", "solar_zenith_deg", "median_reflectance_1500nm",
               "median_bt_flat_K", "median_bt_slope_K", "p05_bt_flat_K", "p95_bt_flat_K",
               "equilibrium_model_K", "median_bt_if_guide_mW_K", "median_bd2900_exploratory"],
              lat_rows)
    lat_rows = np.asarray(lat_rows)
    tc_rows = []
    for j in range(len(tc_idx)):
        k = tc_idx[j]
        tc_rows.append([band_no[k], nm[k], float(np.median(refl[k][good])),
                        float(np.median(refl_tc[j][good])),
                        float(np.median((EMISSIVITY * planck(um[k], bt[good])) / rad[k][good]))])
    write_csv(MOD_THERM / "metrics/e1g2_thermal_removal_spectrum.csv",
              ["band_number", "center_nm", "median_apparent_reflectance_before",
               "median_reflectance_after_thermal_removal", "median_thermal_fraction_of_radiance"],
              tc_rows)
    tc_rows = np.asarray(tc_rows)

    summary = {
        "data": "ch2_iir_nci_20260227T1239538758_d_img_d18 (E1G2), 222 SIS VALID bands",
        "code_commit_base": commit,
        "sun_moon_distance_au": d_au, "sun_earth_distance_au": d_earth,
        "solar_zenith_range_deg": [float(sza.min()), float(sza.max())],
        "pixels_total": int(nl * ns),
        "pixels_all_valid_bands_finite_positive": int(finite_pos.sum()),
        "pixels_with_brightness_temperature": int(good.sum()),
        "iof_median_1500nm_label_uW": float(np.median(band_mean(iof, nm, 1450, 1550)[lab])),
        "reflectance_1500nm_p05_p50_p95": [float(v) for v in np.quantile(r15[lab], [0.05, 0.5, 0.95])],
        "reflectance_813nm_median": float(np.median(r075[lab])),
        "reflectance_1500nm_darkest10_brightest10_thresholds": [float(q_dark), float(q_bright)],
        "across_track_column_relative_std_1500nm": stripe,
        "bt_flat_K_p05_p50_p95": [float(v) for v in np.quantile(bt[good], [0.05, 0.5, 0.95])],
        "bt_slope_minus_flat_K_median": float(np.median((bt_slope - bt)[good & np.isfinite(bt_slope)])),
        "bt_if_guide_mW_K_median": float(np.nanmedian(bt_mw)),
        "equilibrium_model_K_range": [float(t_eq_line.min()), float(t_eq_line.max())],
        "model_parameters": {"bond_albedo": BOND_ALBEDO, "emissivity": EMISSIVITY,
                             "solar_constant_W_m2": S0},
        "bd2900_exploratory_p05_p50_p95": [float(v) for v in np.quantile(bd29[good], [0.05, 0.5, 0.95])],
    }
    for m in (MOD_UNIT, MOD_REFL, MOD_THERM):
        (m / "metrics/e1g2_m2_pilot_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # ---------- figures ----------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    a1.fill_between(unit_rows[:, 1], unit_rows[:, 3], unit_rows[:, 5], color=BLUE, alpha=0.18, lw=0)
    a1.plot(unit_rows[:, 1], unit_rows[:, 4], color=BLUE, lw=2, label="label unit µW (as archived)")
    a1.fill_between(unit_rows[:, 1], unit_rows[:, 6], unit_rows[:, 8], color=ORANGE, alpha=0.18, lw=0)
    a1.plot(unit_rows[:, 1], unit_rows[:, 7], color=ORANGE, lw=2, label="guide unit mW (×1000)")
    a1.axhspan(0.02, 0.5, color=AQUA, alpha=0.12, lw=0)
    a1.axhline(1.0, color=INK2, lw=1, ls="--")
    a1.text(900, 1.25, "I/F = 1: perfect diffuser", color=INK2, fontsize=8)
    a1.text(900, 0.025, "lunar I/F range (0.02-0.5)", color=INK2, fontsize=8)
    a1.set_yscale("log")
    a1.set_xlim(800, 2600)
    a1.set_xlabel("wavelength (nm)")
    a1.set_ylabel("I/F (median, 5-95% band)")
    a1.set_title("Reflected-light test, 0.8-2.6 µm", loc="left")
    a1.legend(frameon=False, loc="center right")
    a2.plot(lat_rows[:, 0], lat_rows[:, 3], color=BLUE, lw=2, marker="o", ms=4, label="label unit µW")
    a2.plot(lat_rows[:, 0], lat_rows[:, 8], color=ORANGE, lw=2, marker="o", ms=4, label="guide unit mW")
    a2.plot(lat_rows[:, 0], lat_rows[:, 7], color=INK2, lw=1.5, ls="--", label="radiative equilibrium")
    a2.set_yscale("log")
    a2.set_xlabel("latitude (deg)")
    a2.set_ylabel("brightness temperature, 4.5-4.9 µm (K)")
    a2.set_title("Thermal-emission test", loc="left")
    a2.legend(frameon=False)
    fig.suptitle("E1G2 2026-02-27: which radiance unit is physically plausible?", x=0.01, ha="left")
    fig.savefig(MOD_UNIT / "figures/e1g2_radiance_unit_physical_test.png", dpi=160)
    plt.close(fig)

    step = 4
    fig = plt.figure(figsize=(13, 6.2), constrained_layout=True)
    ax = strip_axes(fig, 3)
    lo, hi = np.nanquantile(r15[lab], [0.01, 0.99])
    show_strip(ax[0], np.where(lab, r15, np.nan)[::step], lat_line[::step], "gray", lo, hi,
               "reflectance 1.5 µm")
    ax[0].set_title("Apparent reflectance at 1.5 µm (I/F / cos i)", loc="left")
    rgb_b = [band_mean(refl, nm, 2050, 2150), band_mean(refl, nm, 1450, 1550), band_mean(refl, nm, 950, 1050)]
    rgb = np.stack([np.clip((c - np.nanquantile(c[lab], 0.01)) /
                            (np.nanquantile(c[lab], 0.99) - np.nanquantile(c[lab], 0.01)), 0, 1)
                    for c in rgb_b], axis=-1)
    ax[1].imshow(np.transpose(rgb[::step], (1, 0, 2)), aspect="auto", origin="lower",
                 extent=[lat_line[0], lat_line[-1], 0, 250], interpolation="nearest")
    ax[1].set_ylabel("sample")
    ax[1].grid(False)
    ax[1].set_title("Composite R = 2.1 µm, G = 1.5 µm, B = 1.0 µm (each stretched 1-99%)", loc="left")
    ratio = band_mean(refl, nm, 950, 1050) / band_mean(refl, nm, 813, 870)
    lo, hi = np.nanquantile(ratio[lab], [0.02, 0.98])
    show_strip(ax[2], np.where(lab, ratio, np.nan)[::step], lat_line[::step], "cividis", lo, hi,
               "R(1.0 µm) / R(0.84 µm)")
    ax[2].set_title("1 µm absorption proxy: lower ratio = deeper mafic band", loc="left")
    ax[2].set_xlabel("latitude (deg); strip is ~18 km wide, along-track compressed")
    fig.savefig(MOD_REFL / "figures/e1g2_apparent_reflectance_strip_maps.png", dpi=150)
    plt.close(fig)

    sp = np.asarray(spec_rows, dtype=float)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    s = sp[:, 1] <= 2600
    a1.fill_between(sp[s, 1], sp[s, 5], sp[s, 6], color=INK2, alpha=0.12, lw=0, label="all pixels 5-95%")
    a1.plot(sp[s, 1], sp[s, 4], color=ORANGE, lw=2, label="brightest 10% at 1.5 µm")
    a1.plot(sp[s, 1], sp[s, 2], color=INK2, lw=1.5, label="all pixels median")
    a1.plot(sp[s, 1], sp[s, 3], color=BLUE, lw=2, label="darkest 10% at 1.5 µm")
    a1.set_xlabel("wavelength (nm)")
    a1.set_ylabel("apparent reflectance")
    a1.set_title("Reflected-light spectra, 0.8-2.6 µm", loc="left")
    a1.legend(frameon=False)
    a2.plot(sp[:, 1], sp[:, 4], color=ORANGE, lw=2, label="brightest 10%")
    a2.plot(sp[:, 1], sp[:, 3], color=BLUE, lw=2, label="darkest 10%")
    a2.set_yscale("log")
    a2.set_xlabel("wavelength (nm)")
    a2.set_ylabel("apparent reflectance (log)")
    a2.set_title("Full range: rise beyond ~3 µm is thermal emission", loc="left")
    a2.legend(frameon=False)
    fig.savefig(MOD_REFL / "figures/e1g2_apparent_reflectance_spectra.png", dpi=160)
    plt.close(fig)

    fig = plt.figure(figsize=(13, 6.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.3])
    a0 = fig.add_subplot(gs[0, :])
    lo, hi = np.nanquantile(bt[good], [0.01, 0.99])
    show_strip(a0, np.where(good, bt, np.nan)[::step], lat_line[::step], "inferno", lo, hi,
               "brightness temperature (K)")
    a0.set_title("Brightness temperature from 4.5-4.9 µm (emissivity 0.95, reflected part removed)", loc="left")
    a0.set_xlabel("latitude (deg)")
    a1 = fig.add_subplot(gs[1, 0])
    a1.fill_between(lat_rows[:, 0], lat_rows[:, 5], lat_rows[:, 6], color=BLUE, alpha=0.18, lw=0)
    a1.plot(lat_rows[:, 0], lat_rows[:, 3], color=BLUE, lw=2, marker="o", ms=4, label="IIRS median (5-95%)")
    a1.plot(lat_rows[:, 0], lat_rows[:, 4], color=AQUA, lw=1.5, label="IIRS, sloped reflectance case")
    a1.plot(lat_rows[:, 0], lat_rows[:, 7], color=INK2, lw=1.5, ls="--", label="radiative equilibrium")
    a1.set_xlabel("latitude (deg)")
    a1.set_ylabel("temperature (K)")
    a1.set_title("Temperature along the strip", loc="left")
    a1.legend(frameon=False)
    a2 = fig.add_subplot(gs[1, 1])
    a2.plot(tc_rows[:, 1], tc_rows[:, 2], color=ORANGE, lw=2, label="before thermal removal")
    a2.plot(tc_rows[:, 1], tc_rows[:, 3], color=BLUE, lw=2, label="after (exploratory)")
    a2.axvspan(2850, 2950, color=GRID, alpha=0.6, lw=0)
    a2.set_xlabel("wavelength (nm)")
    a2.set_ylabel("median apparent reflectance")
    a2.set_title("2.5-3.6 µm before and after thermal removal", loc="left")
    a2.legend(frameon=False)
    fig.savefig(MOD_THERM / "figures/e1g2_brightness_temperature_and_thermal_removal.png", dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
