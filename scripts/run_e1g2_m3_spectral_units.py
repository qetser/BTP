#!/usr/bin/env python3
"""M3 unsupervised reference: E1G2 spectral parameters and spectral units.

Run from the repository root after the M2 pilot and topographic scripts:
  uv run --no-project --with numpy --with matplotlib --with scikit-learn \
      python scripts/run_e1g2_m3_spectral_units.py

Input: apparent reflectance (I/F / cos i) normalized by SLDEM local incidence,
0.85-2.45 µm. Steps:
1. Column flat field: divide each band by its across-track column median relative
   to the band median (removes detector-column striping; scene-derived).
2. Empirical polishing: divide every spectrum by the ratio of the scene-median
   spectrum to its 4th-order polynomial fit. This removes artifacts common to
   all pixels (for example detector-junction steps) and also any real feature
   shared by the whole scene. Then despiking: a band value more than 6 robust
   sigma from the median of its four nearest bands is replaced by that median;
   pixels with more than 5% replaced bands and columns with more than 50%
   dropped pixels are excluded. Then a 3-band running mean along wavelength.
3. Spectral parameters: 1 µm and 2 µm integrated band depth with linear
   continua anchored at 0.85/1.58 µm and 1.58/2.45 µm (IIRS has no valid band
   below 813 nm, so the M3 699 nm anchor is unavailable), and the 1.58 µm
   albedo.
4. Spectral units: PCA (fit on a random sample) of the continuum-shape vector
   (spectrum / its mean) plus log albedo, then k-means. Stability: models fit
   separately on even and odd 500-line blocks, compared by adjusted Rand index
   on the odd blocks, and across 5 seeds.
Clusters are spectral units, not mineral labels.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/e1g2"
MOD = ROOT / "results/phase-1/m3-spectral-units"
INK2, GRID = "#52514e", "#d9d8d4"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False})
# Approximate IAU feature latitudes near the 3.5-5.5°W strip (research notes, not validated).
FEATURES = [(-3.4, "Flammarion"), (2.0, "Sinus Medii (W edge)"), (11.6, "Rimae Bode DMD"),
            (19.5, "Montes Apenninus"), (25.3, "Montes Archimedes")]
K_RANGE = range(3, 9)


def main():
    for sub in ("metrics", "figures"):
        (MOD / sub).mkdir(parents=True, exist_ok=True)
    nm = np.loadtxt(DERIVED / "bands.csv", delimiter=",", skiprows=1, usecols=(1,))
    sel = np.where((nm >= 845) & (nm <= 2460))[0]
    wl = nm[sel]
    refl = np.load(DERIVED / "apparent_reflectance.npy", mmap_mode="r")
    cos_local = np.load(DERIVED / "cos_local_incidence.npy")
    geom = np.loadtxt(DERIVED / "line_geometry.csv", delimiter=",", skiprows=1)
    mu0 = np.cos(np.deg2rad(geom[:, 2]))[:, None]
    good = np.load(DERIVED / "quality_mask.npy") & (cos_local > 0.2)
    latlon = np.load(DERIVED / "latlon.npy")
    lat_line = latlon[0].mean(axis=1)
    nl, ns = good.shape

    # Topographic normalization, column flat field, spectral smoothing.
    scale = (mu0 / np.clip(cos_local, 0.2, None)).astype(np.float32)
    cube = np.empty((len(sel), nl, ns), dtype=np.float32)
    stripe_before, stripe_after = [], []
    for j, k in enumerate(sel):
        b = np.asarray(refl[k]) * scale
        b[~good] = np.nan
        col = np.nanmedian(b, axis=0)
        stripe_before.append(np.nanstd(col / np.nanmedian(col)))
        b /= (col / np.nanmedian(col))[None, :]
        stripe_after.append(np.nanstd(np.nanmedian(b, axis=0) / np.nanmedian(b)))
        cube[j] = b
    # Empirical polishing: remove artifacts shared by all pixels (e.g. junction steps).
    x_um = wl / 1000.0
    med = np.nanmedian(cube[:, ::7, ::3].reshape(len(sel), -1), axis=1)
    polish = med / np.polyval(np.polyfit(x_um, med, 4), x_um)
    cube /= polish[:, None, None].astype(np.float32)
    # Despike: a band value more than 6 robust sigma (per band) from the median
    # of its four nearest bands is replaced by that median. A pixel is
    # dropped when more than 5% of its bands were replaced; a column is dropped
    # when more than 50% of its pixels were dropped.
    n_spiked = np.zeros((nl, ns), dtype=np.int16)
    nbands = len(sel)
    for j in range(nbands):
        # Edge bands use the four nearest bands on one side.
        nbr = [i for i in sorted(range(nbands), key=lambda i: abs(i - j)) if i != j][:4]
        nb_med = np.median(np.stack([cube[i] for i in nbr]), axis=0)
        dev = np.log(np.clip(cube[j] / nb_med, 1e-3, None))
        sub = dev[::9, ::3]
        sub = sub[np.isfinite(sub)]
        sig = 1.4826 * np.median(np.abs(sub - np.median(sub)))
        hit = np.abs(dev - np.median(sub)) > 6.0 * sig
        cube[j] = np.where(hit, nb_med, cube[j])
        n_spiked += hit
    spike = good & (n_spiked > 0.05 * len(sel))
    col_bad = spike.mean(axis=0) > 0.50
    replaced_values = int(n_spiked[good].sum())
    good_before = int(good.sum())
    good &= ~spike
    good[:, col_bad] = False
    cube[:, ~good] = np.nan
    cube = (np.concatenate([cube[:1], cube[:-1]]) + cube + np.concatenate([cube[1:], cube[-1:]])) / 3.0
    # Shared input for the binned-stability, supervised M3, and M4 runs.
    np.save(DERIVED / "m3_preprocessed_reflectance.npy", cube)
    np.save(DERIVED / "m3_preprocessed_good.npy", good)
    np.savetxt(DERIVED / "m3_preprocessed_wavelengths_nm.txt", wl)

    def at(w):
        return cube[int(np.argmin(np.abs(wl - w)))]

    def ibd(lo, hi):
        s = (wl > lo) & (wl < hi)
        r_lo, r_hi = at(lo), at(hi)
        total = np.zeros((nl, ns), dtype=np.float32)
        for w, j in zip(wl[s], np.where(s)[0]):
            c = r_lo + (r_hi - r_lo) * (w - lo) / (hi - lo)
            total += 1.0 - cube[j] / c
        return total / s.sum()
    ibd1 = ibd(850, 1580)
    ibd2 = ibd(1580, 2450)
    alb = at(1580)

    # Feature matrix.
    rows_good = np.where(good.ravel())[0]
    X = cube.reshape(len(sel), -1)[:, rows_good].T
    ok = np.all(np.isfinite(X), axis=1) & np.all(X > 0, axis=1)
    rows_good, X = rows_good[ok], X[ok]
    shape = X / X.mean(axis=1, keepdims=True)
    feats = np.hstack([shape, np.log(X.mean(axis=1, keepdims=True))]).astype(np.float32)
    feats = (feats - feats.mean(0)) / feats.std(0)
    line_of = rows_good // ns
    block = (line_of // 500) % 2
    rng = np.random.default_rng(42)
    fit_idx = rng.choice(len(feats), 200_000, replace=False)
    pca = PCA(n_components=4, random_state=0).fit(feats[fit_idx])
    Z = pca.transform(feats)

    k_rows = []
    for k in K_RANGE:
        sub = rng.choice(len(Z), 20_000, replace=False)
        km = KMeans(k, n_init=4, random_state=0).fit(Z[fit_idx])
        sil = silhouette_score(Z[sub], km.predict(Z[sub]))
        even = rng.choice(np.where(block == 0)[0], 150_000, replace=False)
        odd_all = np.where(block == 1)[0]
        odd = rng.choice(odd_all, 150_000, replace=False)
        km_e = KMeans(k, n_init=4, random_state=1).fit(Z[even])
        km_o = KMeans(k, n_init=4, random_state=2).fit(Z[odd])
        test = rng.choice(odd_all, 100_000, replace=False)
        ari_split = adjusted_rand_score(km_e.predict(Z[test]), km_o.predict(Z[test]))
        seeds = [KMeans(k, n_init=1, random_state=s).fit(Z[fit_idx]).predict(Z[test]) for s in range(5)]
        ari_seed = np.mean([adjusted_rand_score(seeds[0], s) for s in seeds[1:]])
        k_rows.append([k, float(sil), float(ari_split), float(ari_seed)])
    with (MOD / "metrics/e1g2_kmeans_model_selection.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k", "silhouette_20k_sample", "ari_even_vs_odd_block_models_on_odd",
                    "mean_ari_across_5_seeds"])
        w.writerows(k_rows)
    k_rows = np.asarray(k_rows)
    # Choose the largest k whose split ARI >= 0.8; fall back to best split ARI.
    stable = k_rows[k_rows[:, 2] >= 0.8]
    k_sel = int(stable[-1, 0]) if len(stable) else int(k_rows[np.argmax(k_rows[:, 2]), 0])
    rule = ("largest k with even/odd block-model ARI >= 0.8" if len(stable) else
            "no k reached block-model ARI 0.8; fallback to the k with the highest block-model ARI")
    km = KMeans(k_sel, n_init=8, random_state=0).fit(Z[fit_idx])
    lab = km.predict(Z)
    # Order clusters by mean albedo so colors are reproducible.
    mean_alb = np.array([X[lab == c].mean() for c in range(k_sel)])
    order = np.argsort(mean_alb)
    remap = np.empty(k_sel, int)
    remap[order] = np.arange(k_sel)
    lab = remap[lab]
    lab_map = np.full(nl * ns, -1, np.int16)
    lab_map[rows_good] = lab
    lab_map = lab_map.reshape(nl, ns)
    np.save(DERIVED / "spectral_units.npy", lab_map)

    unit_rows, spectra = [], []
    for c in range(k_sel):
        m = lab == c
        mm = lab_map == c
        spec = np.median(X[m], axis=0)
        spectra.append(spec)
        unit_rows.append([c + 1, int(m.sum()), float(m.mean()), float(np.median(alb[mm])),
                          float(np.median(ibd1[mm])), float(np.median(ibd2[mm])),
                          float(np.median(latlon[0][mm]))])
    with (MOD / "metrics/e1g2_spectral_unit_summary.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["unit", "pixels", "fraction", "median_reflectance_1580nm", "median_ibd_1um",
                    "median_ibd_2um", "median_latitude_deg"])
        w.writerows(unit_rows)
    with (MOD / "metrics/e1g2_spectral_unit_median_spectra.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["center_nm"] + [f"unit_{c + 1}" for c in range(k_sel)])
        for i, wv in enumerate(wl):
            w.writerow([wv] + [float(s[i]) for s in spectra])
    with (MOD / "metrics/e1g2_polishing_coefficients.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["center_nm", "scene_median_over_poly4_fit"])
        w.writerows([[float(a), float(b)] for a, b in zip(wl, polish)])
    summary = {
        "spike_screen": {"pixels_before": good_before, "pixels_flagged_spike": int(spike.sum()),
                         "band_values_replaced": replaced_values,
                         "columns_dropped": [int(c) for c in np.where(col_bad)[0]]},
        "polishing_coefficient_min_max": [float(polish.min()), float(polish.max())],
        "input": "E1G2 apparent reflectance / SLDEM local incidence, 845-2460 nm, column flat-fielded, polished, despiked, 3-band smoothed",
        "pixels_clustered": int(len(lab)),
        "column_stripe_relative_std_median_before_after": [float(np.median(stripe_before)),
                                                           float(np.median(stripe_after))],
        "pca_explained_variance_ratio": [float(v) for v in pca.explained_variance_ratio_],
        "selected_k": k_sel,
        "selection_rule": rule,
        "stability_gate_ari_0p8_passed": bool(len(stable)),
        "ibd_1um_p05_p50_p95": [float(v) for v in np.nanquantile(ibd1[good], [0.05, 0.5, 0.95])],
        "ibd_2um_p05_p50_p95": [float(v) for v in np.nanquantile(ibd2[good], [0.05, 0.5, 0.95])],
        "pearson_ibd1_vs_ibd2": float(np.corrcoef(ibd1[good & np.isfinite(ibd1) & np.isfinite(ibd2)],
                                                  ibd2[good & np.isfinite(ibd1) & np.isfinite(ibd2)])[0, 1]),
    }
    (MOD / "metrics/e1g2_spectral_units_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    step = 4
    ext = [lat_line[0], lat_line[-1], 0, 250]
    fig = plt.figure(figsize=(13, 9), constrained_layout=True)
    gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1, 1.5])
    panels = [(alb, "gray", "reflectance 1.58 µm", "Albedo at 1.58 µm (topography-normalized, destriped)"),
              (ibd1, "viridis", "IBD 1 µm", "1 µm integrated band depth (0.85-1.58 µm continuum)"),
              (ibd2, "viridis", "IBD 2 µm", "2 µm integrated band depth (1.58-2.45 µm continuum)")]
    for r, (img, cmap, lbl, ttl) in enumerate(panels):
        ax = fig.add_subplot(gs[r, :])
        v = np.where(good, img, np.nan)[::step]
        lo, hi = np.nanquantile(v, [0.02, 0.98])
        im = ax.imshow(v.T, aspect="auto", origin="lower", cmap=cmap, vmin=lo, vmax=hi,
                       extent=ext, interpolation="nearest")
        ax.grid(False)
        ax.set_ylabel("sample")
        ax.set_title(ttl, loc="left")
        plt.colorbar(im, ax=ax, pad=0.01, fraction=0.03).set_label(lbl)
        if r == 0:
            for la, name in FEATURES:
                ax.axvline(la, color="#e34948", lw=0.8, ls=":")
                ax.text(la, 238, name, ha="center", va="top", fontsize=7, color="#0b0b0b",
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1})
    ax.set_xlabel("latitude (deg)")
    a1 = fig.add_subplot(gs[3, 0])
    for c in range(k_sel):
        a1.plot(wl, spectra[c] / spectra[c][int(np.argmin(np.abs(wl - 1580)))], color=CAT[c], lw=2,
                label=f"unit {c + 1} ({unit_rows[c][2] * 100:.0f}%)")
    a1.set_xlabel("wavelength (nm)")
    a1.set_ylabel("reflectance / reflectance at 1.58 µm")
    a1.set_title("Median spectrum of each unit (shape)", loc="left")
    a1.legend(frameon=False, fontsize=8, ncol=2)
    a2 = fig.add_subplot(gs[3, 1])
    a2.plot(k_rows[:, 0], k_rows[:, 2], color=CAT[0], lw=2, marker="o", ms=5, label="even vs odd block models (ARI)")
    a2.plot(k_rows[:, 0], k_rows[:, 3], color=CAT[1], lw=2, marker="o", ms=5, label="seed stability (ARI)")
    a2.plot(k_rows[:, 0], k_rows[:, 1], color=CAT[2], lw=2, marker="o", ms=5, label="silhouette")
    a2.axvline(k_sel, color=INK2, lw=1, ls="--")
    a2.set_ylim(0, 1.02)
    a2.set_xlabel("number of units k")
    a2.set_ylabel("score")
    a2.axhline(0.8, color="#e34948", lw=1, ls=":")
    a2.set_title(f"Model selection: k = {k_sel}" + ("" if len(stable) else
                 " (fallback: no k reached block ARI 0.8)"), loc="left")
    a2.legend(frameon=False, fontsize=8)
    fig.savefig(MOD / "figures/e1g2_spectral_parameters_and_unit_spectra.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(13, 2.6), constrained_layout=True)
    show = np.where(lab_map >= 0, lab_map, np.nan)[::step]
    ax.imshow(show.T, aspect="auto", origin="lower", extent=ext, interpolation="nearest",
              cmap=ListedColormap(CAT[:k_sel]), vmin=-0.5, vmax=k_sel - 0.5)
    ax.grid(False)
    ax.set_ylabel("sample")
    ax.set_xlabel("latitude (deg)")
    for la, name in FEATURES:
        ax.axvline(la, color="#0b0b0b", lw=0.8, ls=":")
        ax.text(la, 238, name, ha="center", va="top", fontsize=7, color="#0b0b0b",
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1})
    ax.set_title(f"Unsupervised spectral units (k = {k_sel}); units ordered by albedo, darkest = 1; "
                 "white = masked", loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=CAT[c]) for c in range(k_sel)]
    ax.legend(handles, [f"unit {c + 1}" for c in range(k_sel)], frameon=False, ncol=k_sel,
              loc="upper left", bbox_to_anchor=(0, -0.28), fontsize=8)
    fig.savefig(MOD / "figures/e1g2_spectral_unit_map.png", dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))
    print(k_rows)


if __name__ == "__main__":
    main()
