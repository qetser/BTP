#!/usr/bin/env python3
"""Compare E1G2 IIRS brightness temperature with Diviner GCP at matched local time.

Run from the repository root after the GCP tiles are downloaded (see
results/phase-1/m2-diviner-temperature/notes.md) and after
scripts/run_e1g2_m2_physical_pilot.py has written the per-pixel arrays:
  uv run --no-project --with numpy --with matplotlib python scripts/compare_e1g2_diviner_temperature.py

Reference: Diviner Global Cumulative Product (GCP), DATA_SET_ID LRO-L-DLRE-5-GCP-V1.0,
file version 002 (Williams et al. 2017, Icarus 283, 300-325). It holds nadir
brightness temperatures for channels 3-9 and the bolometric temperature, binned at
0.5 deg latitude/longitude and 0.25 h local time, from 2009-07-05 to 2015-04-01.

Method:
1. Per IIRS line, the subsolar point is computed from the centre-column latitude and
   longitude, solar zenith and solar azimuth (clockwise from north) by the spherical
   destination formula. Local time per pixel is 12 h + (lon - subsolar lon) / 15.
2. Per 1 deg IIRS latitude bin [c - 0.5, c + 0.5), the GCP 0.5 deg cells inside that
   latitude range and touched by valid IIRS pixels are pooled. Primary estimate: the
   median over cells for each 0.25 h local-time bin, then linear interpolation to the
   bin's median IIRS local time. Near 08:00 the GCP cells along this longitude are
   sparse (the 7.88 h and 8.12 h bins are mostly empty), so a sensitivity estimate
   fits a quadratic in local time to all cell values over 7.0-9.5 h.
3. IIRS uses the median of valid pixels in the same latitude bin (pixel latitude),
   with the saved per-line table (median_bt_flat_K) reported as a consistency check.
4. Spectral bias: IIRS BT is also re-expressed with emissivity 1 (Diviner convention).
   A Gaussian facet-temperature mix that conserves sigma T^4 is tuned per bin so its
   7.8 um BT excess equals the observed Diviner ch3 minus bolometric value; its 4.69 um
   excess is the expected IIRS minus bolometric offset from anisothermality alone.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DER = ROOT / "data/derived/e1g2"
GCP = ROOT / "data/reference/diviner/gcp"
TILES = ["10s00s", "00n10n", "10n20n", "20n30n"]
IIRS_CSV = ROOT / "results/phase-1/m2-thermal-brightness/metrics/e1g2_temperature_by_latitude.csv"
OUT = ROOT / "results/phase-1/m2-diviner-temperature"
CHANNELS = ["t3", "t4", "t5", "t6", "t7", "t8", "t9", "tbol"]
LON_MIN, LON_MAX = -6.0, -3.0  # signed east longitude window read from the GCP
FIT_LT = (7.0, 9.5)
INK, INK2, GRID = "#1f1e1c", "#52514e", "#d9d8d4"
C_IIRS, C_BOL, C_T3 = "#c4502a", "#2a6fb0", "#7a5aa6"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def load_gcp():
    """Return lat centres, lon centres, lt centres, and cube[channel, lat, lon, lt]."""
    rows = []
    for tile in TILES:
        with open(GCP / f"global_cumul_avg_cyl_{tile}_002.tab", "rb") as f:
            f.readline()  # header record
            for line in f:
                if LON_MIN < float(line[:7]) < LON_MAX:
                    rows.append([float(v) for v in line.split(b",")])
    a = np.asarray(rows)
    lons, lats, lts = (np.unique(a[:, k]) for k in range(3))
    cube = np.full((len(CHANNELS), lats.size, lons.size, lts.size), np.nan)
    io, ia, it = (np.searchsorted(u, a[:, k]) for k, u in enumerate((lons, lats, lts)))
    for c in range(len(CHANNELS)):
        v = a[:, 3 + c].copy()
        v[(v == -9999) | (v <= 0)] = np.nan  # -9999 empty; negative = below sensitivity
        cube[c, ia, io, it] = v
    return lats, lons, lts, cube


C1, C2, EPS_IIRS, W_IIRS, W_CH3 = 1.191042e8, 1.438777e4, 0.95, 4.69, 7.8


def planck(w, t):
    return C1 / w ** 5 / np.expm1(C2 / (w * t))


def planck_inv(w, rad):
    return C2 / (w * np.log1p(C1 / (w ** 5 * rad)))


def gaussian_mix_excess(tbol, sigma):
    """Spectral BT minus bolometric T at (W_IIRS, W_CH3) for a Gaussian facet-temperature mix."""
    x = np.linspace(-4, 4, 401); wts = np.exp(-x ** 2 / 2); wts /= wts.sum()
    lo, hi = tbol - 3 * sigma - 50, tbol + 50
    for _ in range(80):  # bisection so the mix conserves sigma T^4
        tm = 0.5 * (lo + hi)
        if (wts * np.clip(tm + sigma * x, 1, None) ** 4).sum() > tbol ** 4:
            hi = tm
        else:
            lo = tm
    t = np.clip(tm + sigma * x, 1, None)
    return [float(planck_inv(w, (wts * planck(w, t)).sum()) - tbol) for w in (W_IIRS, W_CH3)]


def sigma_for_ch3_excess(tbol, excess):
    """Facet-temperature spread that reproduces the observed Diviner ch3 minus bolometric excess."""
    lo, hi = 0.0, 120.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if gaussian_mix_excess(tbol, mid)[1] > excess:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def subsolar(lat, lon, sza, az):
    p, l, d, t = map(np.radians, (lat, lon, sza, az))
    lat2 = np.arcsin(np.sin(p) * np.cos(d) + np.cos(p) * np.sin(d) * np.cos(t))
    lon2 = l + np.arctan2(np.sin(t) * np.sin(d) * np.cos(p), np.cos(d) - np.sin(p) * np.sin(lat2))
    return np.degrees(lat2), np.degrees(lon2) % 360


def pooled_interp(cells, lts, lt0):
    """cells: (n_cells, n_lt). Median per LT bin, then linear interpolation to lt0."""
    prof = np.full(lts.size, np.nan)
    has = np.isfinite(cells).any(axis=0)
    prof[has] = np.nanmedian(cells[:, has], axis=0)
    ok = np.isfinite(prof)
    below = np.where(ok & (lts <= lt0))[0]; above = np.where(ok & (lts > lt0))[0]
    if not below.size or not above.size:
        return np.nan, np.nan, np.nan
    i0, i1 = below[-1], above[0]
    w = (lt0 - lts[i0]) / (lts[i1] - lts[i0])
    return float(prof[i0] + w * (prof[i1] - prof[i0])), float(lts[i0]), float(lts[i1])


def quad_fit(cells, lts, lt0):
    """Quadratic in local time fitted to all cell values within FIT_LT; value and residual RMS."""
    sel = (lts >= FIT_LT[0]) & (lts <= FIT_LT[1])
    x = np.broadcast_to(lts[sel], cells[:, sel].shape).ravel(); y = cells[:, sel].ravel()
    ok = np.isfinite(y)
    if ok.sum() < 6:
        return np.nan, np.nan
    co = np.polyfit(x[ok] - 8.0, y[ok], 2)
    res = y[ok] - np.polyval(co, x[ok] - 8.0)
    return float(np.polyval(co, lt0 - 8.0)), float(np.sqrt(np.mean(res ** 2)))


def main() -> None:
    (OUT / "metrics").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    latlon = np.load(DER / "latlon.npy")
    bt = np.load(DER / "brightness_temperature_K.npy").astype(float)
    q = np.load(DER / "quality_mask.npy")
    geom = np.genfromtxt(DER / "line_geometry.csv", delimiter=",", names=True)
    lat, lon = latlon[0].astype(float), latlon[1].astype(float)
    c = lat.shape[1] // 2
    ss_lat, ss_lon = subsolar(lat[:, c], lon[:, c], geom["solar_zenith_deg"], geom["solar_azimuth_deg"])
    lt = 12.0 + (((lon - ss_lon[:, None] + 180) % 360) - 180) / 15.0

    lats, lons, lts, cube = load_gcp()
    slon = ((lon + 180) % 360) - 180
    ia = np.floor((lat - (lats[0] - 0.25)) / 0.5).astype(int)
    io = np.floor((slon - (lons[0] - 0.25)) / 0.5).astype(int)
    valid = q & np.isfinite(bt)

    iirs_tab, refl_tab = {}, {}
    with open(IIRS_CSV) as f:
        for r in csv.DictReader(f):
            iirs_tab[float(r["lat_center_deg"])] = float(r["median_bt_flat_K"])
            refl_tab[float(r["lat_center_deg"])] = float(r["median_reflectance_1500nm"])

    rows = []
    for lc in sorted(iirs_tab):
        m = valid & (lat >= lc - 0.5) & (lat < lc + 0.5)
        if m.sum() < 100:
            continue
        lt0 = float(np.median(lt[m]))
        a_set = [i for i in np.unique(ia[m]) if lc - 0.5 < lats[i] < lc + 0.5]
        o_set = list(np.unique(io[m]))
        r = {"lat_center_deg": lc, "n_pixels": int(m.sum()), "local_time_h_median": lt0,
             "local_time_h_min": float(lt[m].min()), "local_time_h_max": float(lt[m].max()),
             "diviner_cells": len(a_set) * len(o_set),
             "iirs_bt_median_K": float(np.median(bt[m])),
             "iirs_bt_median_K_saved_table": iirs_tab[lc],
             "iirs_reflectance_1500nm_median": refl_tab[lc]}
        r["iirs_p05_K"], r["iirs_p95_K"] = (float(x) for x in np.percentile(bt[m], [5, 95]))
        for k, ch in enumerate(CHANNELS):
            cells = cube[k][np.ix_(a_set, o_set)].reshape(-1, lts.size)
            v, l0, l1 = pooled_interp(cells, lts, lt0)
            r[f"diviner_{ch}_K"] = v
            if ch == "tbol":
                r["interp_lt_lower_h"], r["interp_lt_upper_h"] = l0, l1
                r["diviner_tbol_quadfit_K"], r["diviner_tbol_quadfit_rms_K"] = quad_fit(cells, lts, lt0)
                i0 = int(np.argmin(np.abs(lts - l0))); i1 = int(np.argmin(np.abs(lts - l1)))
                r["diviner_tbol_cells_lower"] = int(np.isfinite(cells[:, i0]).sum())
                r["diviner_tbol_cells_upper"] = int(np.isfinite(cells[:, i1]).sum())
                both = np.concatenate([cells[:, i0], cells[:, i1]])
                r["diviner_tbol_cell_std_K"] = float(np.nanstd(both))
            if ch == "t3":
                r["diviner_t3_quadfit_K"], _ = quad_fit(cells, lts, lt0)
        r["iirs_minus_tbol_K"] = r["iirs_bt_median_K"] - r["diviner_tbol_K"]
        r["iirs_minus_tbol_quadfit_K"] = r["iirs_bt_median_K"] - r["diviner_tbol_quadfit_K"]
        r["iirs_minus_t3_K"] = r["iirs_bt_median_K"] - r["diviner_t3_K"]
        r["diviner_t3_minus_tbol_K"] = r["diviner_t3_K"] - r["diviner_tbol_K"]
        r["diviner_t3_minus_tbol_quadfit_K"] = r["diviner_t3_quadfit_K"] - r["diviner_tbol_quadfit_K"]
        # IIRS BT re-expressed with emissivity 1 (Diviner convention)
        r["iirs_bt_eps1_K"] = float(planck_inv(W_IIRS, EPS_IIRS * planck(W_IIRS, r["iirs_bt_median_K"])))
        r["iirs_eps1_minus_tbol_K"] = r["iirs_bt_eps1_K"] - r["diviner_tbol_K"]
        # rough-surface expectation: Gaussian facet spread tuned to Diviner ch3 - tbol
        if np.isfinite(r["diviner_t3_minus_tbol_K"]) and r["diviner_t3_minus_tbol_K"] > 0:
            sg = sigma_for_ch3_excess(r["diviner_tbol_K"], r["diviner_t3_minus_tbol_K"])
            r["facet_sigma_K"] = sg
            r["expected_4p7um_minus_tbol_K"] = gaussian_mix_excess(r["diviner_tbol_K"], sg)[0]
        else:
            r["facet_sigma_K"] = r["expected_4p7um_minus_tbol_K"] = float("nan")
        r["iirs_eps1_minus_expected_K"] = r["iirs_eps1_minus_tbol_K"] - r["expected_4p7um_minus_tbol_K"]
        rows.append(r)

    with open(OUT / "metrics/e1g2_iirs_vs_diviner_by_latitude.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    def stats(key):
        v = np.array([r[key] for r in rows]); v = v[np.isfinite(v)]
        p = np.percentile(v, [5, 25, 75, 95])
        return {"median": float(np.median(v)), "mean": float(np.mean(v)), "std": float(np.std(v, ddof=1)),
                "p05": float(p[0]), "iqr": [float(p[1]), float(p[2])], "p95": float(p[3]),
                "min": float(v.min()), "max": float(v.max()), "n_bins": int(v.size)}

    col = lambda k: np.array([r[k] for r in rows])
    lat_c, iirs_v, bol_v, bolq_v, t3_v = (col(k) for k in ("lat_center_deg", "iirs_bt_median_K",
                                                          "diviner_tbol_K", "diviner_tbol_quadfit_K", "diviner_t3_K"))
    ok = np.isfinite(bol_v)
    summary = {
        "iirs_product": "ch2_iir_nci_20260227T1239538758_d_img_d18 (E1G2), 4504-4875 nm brightness temperature, emissivity 0.95, reflected term removed",
        "reference_product": "Diviner GCP, DATA_SET_ID LRO-L-DLRE-5-GCP-V1.0, files global_cumul_avg_cyl_{10s00s,00n10n,10n20n,20n30n}_002.tab, PDS4 urn:nasa:pds:lro_diviner_derived1:data_derived_gcp, observations 2009-07-05 to 2015-04-01",
        "reference_sha256": {t: sha256(GCP / f"global_cumul_avg_cyl_{t}_002.tab") for t in TILES},
        "subsolar_lat_deg_range": [float(ss_lat.min()), float(ss_lat.max())],
        "subsolar_lon_east_deg_range": [float(ss_lon.min()), float(ss_lon.max())],
        "local_time_h_range_valid_pixels": [float(lt[valid].min()), float(lt[valid].max())],
        "latitude_bins": len(rows),
        "iirs_minus_tbol_K": stats("iirs_minus_tbol_K"),
        "iirs_minus_tbol_quadfit_K": stats("iirs_minus_tbol_quadfit_K"),
        "iirs_minus_t3_K": stats("iirs_minus_t3_K"),
        "diviner_t3_minus_tbol_K": stats("diviner_t3_minus_tbol_K"),
        "diviner_t3_minus_tbol_quadfit_K": stats("diviner_t3_minus_tbol_quadfit_K"),
        "iirs_eps1_minus_tbol_K": stats("iirs_eps1_minus_tbol_K"),
        "facet_sigma_K": stats("facet_sigma_K"),
        "expected_4p7um_minus_tbol_K": stats("expected_4p7um_minus_tbol_K"),
        "iirs_eps1_minus_expected_K": stats("iirs_eps1_minus_expected_K"),
        "anisothermal_model_note": "Upper-bound style estimate: assumes all of Diviner ch3 minus bolometric is from a Gaussian spread of facet temperatures (emissivity 1); ignores emissivity differences between channels.",
        "pearson_r_iirs_vs_tbol_bins": float(np.corrcoef(iirs_v[ok], bol_v[ok])[0, 1]),
        "pearson_r_iirs_vs_tbol_quadfit_bins": float(np.corrcoef(iirs_v, bolq_v)[0, 1]),
        "offset_vs_reflectance_1500nm_excluding_18N": dict(zip(("pearson_r", "slope_K_per_unit_reflectance"), (
            float(np.corrcoef(col("iirs_reflectance_1500nm_median")[(lat_c != 18) & ok], (iirs_v - bol_v)[(lat_c != 18) & ok])[0, 1]),
            float(np.polyfit(col("iirs_reflectance_1500nm_median")[(lat_c != 18) & ok], (iirs_v - bol_v)[(lat_c != 18) & ok], 1)[0])))),
        "saved_table_minus_pixel_bin_iirs_max_abs_K": float(np.max(np.abs(col("iirs_bt_median_K_saved_table") - iirs_v))),
        "units": "K, hours of lunar local time", "split": "none (single strip, no train/test split)",
    }
    with open(OUT / "metrics/e1g2_iirs_vs_diviner_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 6.4), sharey=True,
                                   gridspec_kw={"width_ratios": [1.6, 1]})
    ax1.fill_betweenx(lat_c, col("iirs_p05_K"), col("iirs_p95_K"), color=C_IIRS, alpha=0.15, lw=0)
    ax1.plot(iirs_v, lat_c, color=C_IIRS, lw=2, label="IIRS 4.5–4.9 µm BT (median, p05–p95)")
    ax1.plot(t3_v, lat_c, color=C_T3, lw=1.5, ls="--", label="Diviner ch3 (7.8 µm) BT")
    ax1.plot(bol_v, lat_c, color=C_BOL, lw=2, label="Diviner bolometric T, interpolated")
    ax1.plot(bolq_v, lat_c, color=C_BOL, lw=1.2, ls=":", label="Diviner bolometric T, quadratic fit")
    ax1.set_xlabel("Temperature (K)"); ax1.set_ylabel("Latitude (°N)")
    ax1.set_title("E1G2 strip and Diviner GCP at matched local time", color=INK, fontsize=11, loc="left")
    ax1.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0, -0.11), ncol=2)
    ax2.axvline(0, color=INK2, lw=0.8)
    ax2.plot(iirs_v - bol_v, lat_c, "o-", color=C_BOL, ms=3.5, lw=1.4, label="IIRS − Diviner bolometric")
    ax2.plot(iirs_v - bolq_v, lat_c, ":", color=C_BOL, lw=1.2, label="IIRS − bolometric (quadratic fit)")
    ax2.plot(iirs_v - t3_v, lat_c, "s--", color=C_T3, ms=3, lw=1.2, label="IIRS − Diviner ch3")
    ax2.set_xlabel("Difference (K)")
    ax2.set_title("Per 1° latitude bin", color=INK, fontsize=11, loc="left")
    ax2.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0, -0.11))
    for ax in (ax1, ax2):
        ax.grid(color=GRID, lw=0.6); ax.tick_params(colors=INK2)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    lo, hi = summary["local_time_h_range_valid_pixels"]
    fig.text(0.01, 0.01, f"IIRS local time {lo:.2f}–{hi:.2f} h. Diviner GCP 0.5° × 0.25 h cells (2009–2015), "
             "pooled per 1° latitude over 354.5–356.5°E.", fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "figures/e1g2_iirs_vs_diviner_temperature.png", dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
