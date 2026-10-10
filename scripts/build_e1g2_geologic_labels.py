#!/usr/bin/env python3
"""Assign USGS Unified Geologic Map of the Moon units to every E1G2 IIRS pixel.

Run from the repository root:
  uv run --no-project --with numpy --with geopandas --with pyogrio --with shapely --with matplotlib python scripts/build_e1g2_geologic_labels.py

Source map: Fortezzo, Spudis, and Harrel (2020), Unified Geologic Map of the
Moon, 1:5,000,000 scale, GIS version 2 (March 2020). The zip is downloaded to
data/reference/usgs_unified_geology/ (ignored by Git) and extracted to
data/reference/usgs_unified_geology/extracted/.

Map coordinate system: Moon2000 equidistant cylindrical, central meridian 0,
sphere radius 1,737,400 m, metres. Map x spans -pi R to +pi R, so longitude is
-180 to 180. The IIRS east longitude (0-360) is wrapped to -180..180 and both
coordinates are converted to map metres with x = R lon_rad, y = R lat_rad.

Labels are assigned by point-in-polygon on pixel centres from latlon.npy. When
a centre falls in more than one polygon, the smallest polygon wins (crater
polygons sit on top of the units they cut). The labels are proxy labels from a
1:5M map. They are not reviewed ground truth.

Outputs (ignored by Git) in data/derived/e1g2/:
- geologic_unit_labels.npy: int16 (lines, samples), class id, -1 for none.
- geologic_group_labels.npy: int16 (lines, samples), coarse group id, -1 for none.
Outputs (tracked) in results/phase-1/m3-geologic-labels/:
- metrics/e1g2_geologic_unit_classes.csv: class id, unit code, name, age, group, counts, latitudes.
- metrics/e1g2_geologic_group_classes.csv: the same for coarse groups.
- metrics/e1g2_geologic_boundary_sensitivity.csv: label change under map shifts.
- metrics/e1g2_geologic_labels_summary.json
- figures/e1g2_geologic_unit_labels_strip.png
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapely
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data/reference/usgs_unified_geology"
ZIP = REF / "Unified_Geologic_Map_of_the_Moon_GIS_v2.zip"
GIS = REF / "extracted/Unified_Geologic_Map_of_the_Moon_GIS/Lunar_GIS"
SHP = GIS / "Shapefiles/GeoUnits.shp"
DOMU = GIS / "Symbol_LayerDefinitions/Unified_Geologic_Map_of_the_Moon_DOMU_descriptions.csv"
COLORS = GIS / "Symbol_LayerDefinitions/GeologyUnit_colors.csv"
DERIVED = ROOT / "data/derived/e1g2"
OUT = ROOT / "results/phase-1/m3-geologic-labels"
URL = "https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2.zip"
R_MOON = 1_737_400.0
MIN_PIXELS = 50_000
# Figure colours. The official USGS colours make several units in this strip
# nearly identical (Nt, Nbl, Nbm; Em, Id), so a distinct palette grouped by
# coarse group is used. Units not listed fall back to the official USGS colour.
FIG_COLORS = {"Em": "#1f4e9c", "Im1": "#3d6fb6", "Im2": "#6fa8dc", "Imd": "#9fc5e8",
              "Id": "#111111", "Ip": "#d8c27a", "Nt": "#8c6d2c", "It": "#b89b4f",
              "pNt": "#6b5220", "Cc": "#ffe600", "Ec": "#f28e2b", "Ic2": "#b5651d",
              "Ic1": "#d4884a", "Nc": "#e15759", "pNc": "#9c2f31", "Ib": "#59a14f",
              "Iiap": "#7b3f9e", "Iif": "#c39bd3", "Iia": "#5b2a75", "Nbl": "#2a9d8f",
              "Nbm": "#a0d6b4", "Nb": "#1b6b61"}

GROUPS = ["mare basalt", "pyroclastic/dark mantle", "highland/terra",
          "crater material", "basin material", "other"]
GROUP_COLORS = ["#3b4a6b", "#1b1b1b", "#d9c48c", "#e8a33d", "#8c5a9e", "#9e9e9e"]
MARE = {"Em", "Im1", "Im2", "Imd"}
DARK = {"Id"}
TERRA = {"It", "Itd", "INt", "Nt", "Ntp", "pNt", "Ip", "INp", "Np", "EIp"}
CRATER = {"Cc", "Ccc", "Csc", "Ec", "Ecc", "Esc", "Ic", "Ic1", "Ic2", "Icc",
          "Isc", "Icf", "Nc", "pNc"}
BASIN = {"Ib", "Ibm", "Ig", "Iia", "Iiap", "Iic", "Iif", "Iohi", "Ioho", "Ios",
         "Iom", "Iork", "Iorm", "Nb", "Nbl", "Nbm", "Nbsc", "Nnj", "pNb", "pNbm"}


def group_of(code: str) -> str:
    for name, members in zip(GROUPS[:5], [MARE, DARK, TERRA, CRATER, BASIN]):
        if code in members:
            return name
    return "other"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def to_map_xy(lat: np.ndarray, lon_east: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lon = ((lon_east.astype(np.float64) + 180.0) % 360.0) - 180.0
    return R_MOON * np.deg2rad(lon), R_MOON * np.deg2rad(lat.astype(np.float64))


def assign(x: np.ndarray, y: np.ndarray, polys: gpd.GeoDataFrame) -> tuple[np.ndarray, int]:
    """Return the polygon row index for each point (-1 for none) and the overlap count.

    Polygons are visited from largest to smallest area, so the smallest polygon
    containing a point wins. Each polygon is prepared and tested only against
    points inside its bounding box.
    """
    out = np.full(len(x), -1, dtype=np.int64)
    hits = np.zeros(len(x), dtype=np.int16)
    order = np.argsort(-polys["AREA_GEO"].to_numpy())
    for gi in order:
        geom = polys.geometry.values[gi]
        x0, y0, x1, y1 = geom.bounds
        cand = np.flatnonzero((x >= x0) & (x <= x1) & (y >= y0) & (y <= y1))
        if cand.size == 0:
            continue
        inside = cand[shapely.contains_xy(geom, x[cand], y[cand])]
        out[inside] = gi
        hits[inside] += 1
    return out, int((hits > 1).sum())


def main() -> None:
    latlon = np.load(DERIVED / "latlon.npy")
    quality = np.load(DERIVED / "quality_mask.npy")
    lat, lon_e = latlon[0], latlon[1]
    nl, ns = lat.shape
    x, y = to_map_xy(lat.ravel(), lon_e.ravel())

    gdf = gpd.read_file(SHP)
    crs_wkt = gdf.crs.to_wkt()
    pad = 20_000.0
    sub = gdf.cx[x.min() - pad:x.max() + pad, y.min() - pad:y.max() + pad].reset_index(drop=True)
    # Clip to the strip bounding box to drop far-away vertices, then prepare.
    clip = shapely.box(x.min() - pad, y.min() - pad, x.max() + pad, y.max() + pad)
    sub["geometry"] = shapely.intersection(shapely.make_valid(sub.geometry.values), clip)
    shapely.prepare(sub.geometry.values)

    poly_idx, n_multi = assign(x, y, sub)
    codes_px = np.where(poly_idx >= 0, sub["FIRST_Unit"].to_numpy()[np.maximum(poly_idx, 0)], "")

    domu = {}
    with open(DOMU, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            domu[r["Unit"]] = r["Name"]
    colors = {}
    with open(COLORS, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            colors[r["unit"]] = r["color_hex"]
    age_of = dict(zip(sub["FIRST_Unit"], sub["FIRST_Un_1"]))
    mapname_of = dict(zip(sub["FIRST_Unit"], sub["FIRST_Un_2"]))

    present = sorted({c for c in codes_px if c},
                     key=lambda c: (GROUPS.index(group_of(c)), c))
    code_to_id = {c: i for i, c in enumerate(present)}
    unit = np.full(x.size, -1, dtype=np.int16)
    group = np.full(x.size, -1, dtype=np.int16)
    for c, i in code_to_id.items():
        m = codes_px == c
        unit[m] = i
        group[m] = GROUPS.index(group_of(c))
    unit = unit.reshape(nl, ns)
    group = group.reshape(nl, ns)
    np.save(DERIVED / "geologic_unit_labels.npy", unit)
    np.save(DERIVED / "geologic_group_labels.npy", group)

    (OUT / "metrics").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    q = quality
    n_q = int(q.sum())
    line_lat = np.median(lat, axis=1)

    def runs(mask2d: np.ndarray) -> int:
        """Number of separate along-track line runs where the class occupies any pixel."""
        any_line = mask2d.any(axis=1).astype(np.int8)
        return int(np.sum(np.diff(np.r_[0, any_line]) == 1))

    def class_rows(labels: np.ndarray, names: list[dict]) -> list[dict]:
        rows = []
        for i, meta in enumerate(names):
            m = labels == i
            mq = m & q
            la = lat[mq] if mq.any() else lat[m]
            n_poly = len(np.unique(poly_idx.reshape(nl, ns)[m])) if m.any() else 0
            rows.append({
                "class_id": i, **meta,
                "pixels_all": int(m.sum()),
                "pixels_quality": int(mq.sum()),
                "share_of_quality_pct": round(100.0 * mq.sum() / n_q, 3),
                "lat_min_deg": round(float(la.min()), 3) if la.size else "",
                "lat_p05_deg": round(float(np.percentile(la, 5)), 3) if la.size else "",
                "lat_median_deg": round(float(np.median(la)), 3) if la.size else "",
                "lat_p95_deg": round(float(np.percentile(la, 95)), 3) if la.size else "",
                "lat_max_deg": round(float(la.max()), 3) if la.size else "",
                "map_polygons_hit": n_poly,
                "along_track_runs": runs(m),
                "meets_50k_quality_pixels": bool(mq.sum() >= MIN_PIXELS),
            })
        return rows

    unit_meta = [{"unit_code": c, "unit_name": domu.get(c, mapname_of.get(c, "")),
                  "map_unit_description": mapname_of.get(c, ""), "age": age_of.get(c, ""),
                  "group": group_of(c)} for c in present]
    unit_rows = class_rows(unit, unit_meta)
    group_rows = class_rows(group, [{"group": g} for g in GROUPS])

    def write_csv(path: Path, rows: list[dict]) -> None:
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    write_csv(OUT / "metrics/e1g2_geologic_unit_classes.csv", unit_rows)
    write_csv(OUT / "metrics/e1g2_geologic_group_classes.csv", group_rows)

    # Boundary sensitivity: shift the pixel centres by d km in 4 directions on a
    # 5x5 subsample and count how often the unit label changes.
    sl = (slice(None, None, 5), slice(None, None, 5))
    xs, ys = to_map_xy(lat[sl].ravel(), lon_e[sl].ravel())
    base = unit[sl].ravel()
    base_g = group[sl].ravel()
    qs = q[sl].ravel()
    sens = []
    for d_km in (1.0, 2.0, 5.0):
        d = d_km * 1000.0
        changed_u, changed_g = np.zeros(xs.size, bool), np.zeros(xs.size, bool)
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            pidx, _ = assign(xs + dx, ys + dy, sub)
            c = np.where(pidx >= 0, sub["FIRST_Unit"].to_numpy()[np.maximum(pidx, 0)], "")
            u = np.array([code_to_id.get(v, -2) if v else -1 for v in c], dtype=np.int16)
            g = np.array([GROUPS.index(group_of(v)) if v else -1 for v in c], dtype=np.int16)
            changed_u |= u != base
            changed_g |= g != base_g
        sens.append({"shift_km": d_km, "directions": 4, "subsample": "every 5th line and sample",
                     "pixels_evaluated": int(qs.sum()),
                     "unit_label_changed_pct": round(100.0 * changed_u[qs].mean(), 3),
                     "group_label_changed_pct": round(100.0 * changed_g[qs].mean(), 3)})
    write_csv(OUT / "metrics/e1g2_geologic_boundary_sensitivity.csv", sens)

    unlabeled = int(((unit < 0) & q).sum())
    summary = {
        "source_url": URL,
        "source_zip": str(ZIP.relative_to(ROOT)),
        "source_zip_sha256": sha256(ZIP),
        "source_shapefile_sha256": sha256(SHP),
        "map_version": "Unified Geologic Map of the Moon 1:5M, GIS v2, 2020-03-02",
        "map_crs_wkt": crs_wkt,
        "map_lon_convention": "-180..180 (x = R*lon_rad, R = 1737400 m, central meridian 0)",
        "iirs_lon_convention": "0..360 east, wrapped to -180..180",
        "polygons_total": int(len(gdf)),
        "polygons_in_strip_bbox": int(len(sub)),
        "lines": nl, "samples": ns,
        "pixels_total": int(nl * ns), "pixels_quality": n_q,
        "pixels_quality_unlabeled": unlabeled,
        "points_in_multiple_polygons": n_multi,
        "overlap_rule": "smallest polygon (AREA_GEO) wins",
        "unit_classes_present": len(present),
        "unit_classes_meeting_50k_quality_pixels": int(sum(r["meets_50k_quality_pixels"] for r in unit_rows)),
        "group_classes_present": int(sum(r["pixels_all"] > 0 for r in group_rows)),
        "group_classes_meeting_50k_quality_pixels": int(sum(r["meets_50k_quality_pixels"] for r in group_rows)),
        "boundary_sensitivity": sens,
        "geometry": "SLDEM relative-corrected candidate (provisional, not absolute geolocation)",
        "label_status": "proxy labels from 1:5M map, not reviewed ground truth",
        "script_sha256": sha256(Path(__file__)),
    }
    with open(OUT / "metrics/e1g2_geologic_labels_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Figure: unit labels along the strip (latitude on x, sample on y), plus group strip.
    cols = [FIG_COLORS.get(c, colors.get(c, "#cccccc")) for c in present]
    fig, axes = plt.subplots(2, 1, figsize=(13, 3.8), sharex=True,
                             gridspec_kw={"height_ratios": [2.6, 1.0]})
    lat_edges = np.r_[line_lat[0], 0.5 * (line_lat[1:] + line_lat[:-1]), line_lat[-1]]
    s_edges = np.arange(ns + 1)
    for ax, lab, cmap_cols, title in (
            (axes[0], unit, cols, "USGS 1:5M map unit"),
            (axes[1], group, GROUP_COLORS, "coarse group")):
        arr = np.ma.masked_less(lab.astype(float), 0)
        arr = np.ma.masked_where(~q, arr)
        cmap = ListedColormap(cmap_cols)
        cmap.set_bad("white")
        ax.pcolormesh(lat_edges, s_edges, arr.T, cmap=cmap, vmin=-0.5,
                      vmax=len(cmap_cols) - 0.5, shading="flat", rasterized=True)
        ax.set_ylabel("sample")
        ax.set_ylim(0, ns)
        ax.set_title(title, loc="left", fontsize=9)
    axes[1].set_xlabel("latitude (deg N), SLDEM relative-corrected geometry (provisional)")
    handles = [Patch(facecolor=cols[i], edgecolor="0.3", linewidth=0.3,
                     label=f"{c} ({r['share_of_quality_pct']:.1f}%)")
               for i, (c, r) in enumerate(zip(present, unit_rows))]
    axes[0].legend(handles=handles, loc="upper left", bbox_to_anchor=(1.005, 1.0),
                   fontsize=7, ncol=2 if len(handles) > 12 else 1, frameon=False)
    ghandles = [Patch(facecolor=GROUP_COLORS[i], label=g) for i, g in enumerate(GROUPS)
                if group_rows[i]["pixels_all"] > 0]
    axes[1].legend(handles=ghandles, loc="upper left", bbox_to_anchor=(1.005, 1.15),
                   fontsize=7, frameon=False)
    fig.suptitle("E1G2 IIRS strip: proxy geologic labels from the USGS Unified Geologic Map "
                 "of the Moon (1:5M, v2). White = no unit or quality-masked.", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "figures/e1g2_geologic_unit_labels_strip.png", dpi=150)
    print(json.dumps({k: summary[k] for k in summary if k not in ("map_crs_wkt",)}, indent=1))
    for r in unit_rows:
        print(r["class_id"], r["unit_code"], r["group"], r["pixels_quality"],
              r["share_of_quality_pct"], r["lat_min_deg"], r["lat_max_deg"], r["along_track_runs"])


if __name__ == "__main__":
    main()
