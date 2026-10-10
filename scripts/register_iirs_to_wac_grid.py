#!/usr/bin/env python3
"""Evaluate a spatially blocked 2-D IIRS-to-WAC tie grid.

The result is relative image-registration evidence. It is not surveyed control
or absolute geolocation accuracy.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from register_iirs_to_wac import (
    DEFAULT_IIRS_ZIP,
    DEFAULT_WAC_IMAGE,
    DEFAULT_WAC_METADATA,
    geometry_warp_maps,
    interpolate_grid,
    load_geometry,
)


def subpixel_peak(scores: np.ndarray, x: int, y: int) -> tuple[float, float]:
    """Fit independent parabolas through the peak and adjacent score samples."""
    def delta(minus: float, center: float, plus: float) -> float:
        denom = minus - 2.0 * center + plus
        if not np.isfinite(denom) or abs(denom) < 1e-8:
            return 0.0
        return float(np.clip(0.5 * (minus - plus) / denom, -1.0, 1.0))

    dx = delta(scores[y, x - 1], scores[y, x], scores[y, x + 1]) if 0 < x < scores.shape[1] - 1 else 0.0
    dy = delta(scores[y - 1, x], scores[y, x], scores[y + 1, x]) if 0 < y < scores.shape[0] - 1 else 0.0
    return dx, dy


def make_ties(iirs: np.ndarray, reference: np.ndarray, *, patch_width: int,
              patch_height: int, radius: int, row_step: int,
              block_height: int, guard: int) -> list[dict]:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    a = clahe.apply(iirs)
    b = clahe.apply(reference)
    ax = cv2.Sobel(a, cv2.CV_32F, 1, 0, ksize=3)
    ay = cv2.Sobel(a, cv2.CV_32F, 0, 1, ksize=3)
    bx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3)
    by = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3)

    height, width = iirs.shape
    columns = [25, 75, 125, 175, 225]
    if width != 250:
        columns = np.linspace(radius + patch_width / 2,
                              width - radius - patch_width / 2, 5).round().astype(int).tolist()
    ties: list[dict] = []
    for center_y in range(max(radius + patch_height // 2, row_step // 2),
                          height - radius - patch_height // 2, row_step):
        block = center_y // block_height
        edge_distance = min(center_y % block_height, block_height - center_y % block_height)
        split = "guard" if edge_distance < guard else ("held_out" if block % 3 == 2 else "training")
        for center_x in columns:
            x0 = int(center_x - patch_width // 2)
            y0 = int(center_y - patch_height // 2)
            if x0 - radius < 0 or x0 + patch_width + radius > width:
                continue
            template_x = ax[y0:y0 + patch_height, x0:x0 + patch_width]
            template_y = ay[y0:y0 + patch_height, x0:x0 + patch_width]
            search_x = bx[y0 - radius:y0 + patch_height + radius,
                          x0 - radius:x0 + patch_width + radius]
            search_y = by[y0 - radius:y0 + patch_height + radius,
                          x0 - radius:x0 + patch_width + radius]
            score_map = (cv2.matchTemplate(search_x, template_x, cv2.TM_CCOEFF_NORMED)
                         + cv2.matchTemplate(search_y, template_y, cv2.TM_CCOEFF_NORMED)) / 2.0
            _, score, _, peak = cv2.minMaxLoc(score_map)
            sub_dx, sub_dy = subpixel_peak(score_map, peak[0], peak[1])
            ties.append({
                "tie_id": len(ties) + 1,
                "sample_center_px": float(center_x),
                "line_center_px": float(center_y),
                "ncc_gradient_score": float(score),
                "offset_x_subpixel_px": float(peak[0] - radius + sub_dx),
                "offset_y_subpixel_px": float(peak[1] - radius + sub_dy),
                "spatial_block": int(block),
                "split": split,
            })
    return ties


def robust_affine(points: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    """Fit affine offset fields with Huber reweighting on training points."""
    design = np.column_stack((np.ones(len(points)), points))
    weights = np.ones(len(points), dtype=np.float64)
    coeff = np.zeros((3, offsets.shape[1]), dtype=np.float64)
    for _ in range(30):
        sw = np.sqrt(weights)
        coeff = np.linalg.lstsq(design * sw[:, None], offsets * sw[:, None], rcond=None)[0]
        residual = np.linalg.norm(offsets - design @ coeff, axis=1)
        med = float(np.median(residual))
        scale = max(0.25, 1.4826 * float(np.median(np.abs(residual - med))))
        cutoff = 1.345 * scale
        updated = np.ones_like(weights)
        high = residual > cutoff
        updated[high] = cutoff / residual[high]
        if np.max(np.abs(updated - weights)) < 1e-6:
            break
        weights = updated
    return coeff


def quantile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), q))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iirs-image", type=Path,
                        default=root / "data/reference/lroc_wac_e1g2/e1g2_band040_1369nm.png")
    parser.add_argument("--iirs-zip", type=Path, default=root / DEFAULT_IIRS_ZIP)
    parser.add_argument("--wac-image", type=Path, default=root / DEFAULT_WAC_IMAGE)
    parser.add_argument("--wac-metadata", type=Path, default=root / DEFAULT_WAC_METADATA)
    parser.add_argument("--output-dir", type=Path,
                        default=root / "results/phase-1/m1-wac-2d-grid")
    parser.add_argument("--patch-width", type=int, default=32)
    parser.add_argument("--patch-height", type=int, default=100)
    parser.add_argument("--search-radius", type=int, default=8)
    parser.add_argument("--row-step", type=int, default=250)
    parser.add_argument("--block-height", type=int, default=750)
    parser.add_argument("--guard-lines", type=int, default=150)
    args = parser.parse_args()

    iirs = cv2.imread(str(args.iirs_image), cv2.IMREAD_GRAYSCALE)
    wac = cv2.imread(str(args.wac_image), cv2.IMREAD_GRAYSCALE)
    if iirs is None or wac is None:
        raise FileNotFoundError("Could not read IIRS band or WAC crop image")
    _, scans, pixels, lon_grid, lat_grid, dims = load_geometry(args.iirs_zip)
    lon = interpolate_grid(lon_grid, scans, pixels, dims["lines"], dims["samples"])
    lat = interpolate_grid(lat_grid, scans, pixels, dims["lines"], dims["samples"])
    metadata = json.loads(args.wac_metadata.read_text(encoding="utf-8"))
    map_x, map_y = geometry_warp_maps(lon, lat, metadata)
    reference_native = cv2.remap(wac, map_x, map_y, cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT)
    reference = cv2.resize(reference_native, (iirs.shape[1], iirs.shape[0]),
                           interpolation=cv2.INTER_AREA)

    ties = make_ties(iirs, reference, patch_width=args.patch_width,
                     patch_height=args.patch_height, radius=args.search_radius,
                     row_step=args.row_step, block_height=args.block_height,
                     guard=args.guard_lines)
    training_all = [t for t in ties if t["split"] == "training"]
    heldout_all = [t for t in ties if t["split"] == "held_out"]
    if len(training_all) < 12 or len(heldout_all) < 12:
        raise RuntimeError(f"Too few candidate ties: train={len(training_all)}, heldout={len(heldout_all)}")

    score_cut = quantile([t["ncc_gradient_score"] for t in training_all], 25)
    training = [t for t in training_all if t["ncc_gradient_score"] >= score_cut]
    heldout = [t for t in heldout_all if t["ncc_gradient_score"] >= score_cut]
    if len(training) < 12 or len(heldout) < 12:
        raise RuntimeError(f"Training-only score cutoff left too few ties: train={len(training)}, heldout={len(heldout)}")

    center_x, center_y = iirs.shape[1] / 2.0, iirs.shape[0] / 2.0
    scale_x, scale_y = iirs.shape[1] / 2.0, iirs.shape[0] / 2.0
    def coords(group):
        return np.asarray([[(t["sample_center_px"] - center_x) / scale_x,
                            (t["line_center_px"] - center_y) / scale_y] for t in group])
    train_offsets = np.asarray([[t["offset_x_subpixel_px"], t["offset_y_subpixel_px"]]
                                for t in training])
    coeff = robust_affine(coords(training), train_offsets)
    for group in (training, heldout):
        pred = np.column_stack((np.ones(len(group)), coords(group))) @ coeff
        for tie, fitted in zip(group, pred):
            dx = tie["offset_x_subpixel_px"] - float(fitted[0])
            dy = tie["offset_y_subpixel_px"] - float(fitted[1])
            tie["residual_x_iirs_px"] = dx
            tie["residual_y_iirs_px"] = dy
            tie["residual_iirs_px"] = float(np.hypot(dx, dy))
            tie["fitted_offset_x_px"] = float(fitted[0])
            tie["fitted_offset_y_px"] = float(fitted[1])
    residuals = [t["residual_iirs_px"] for t in heldout]
    held_blocks = sorted({t["spatial_block"] for t in heldout})
    held_columns = sorted({t["sample_center_px"] for t in heldout})
    by_block = {str(block): float(np.median([t["residual_iirs_px"] for t in heldout
                                             if t["spatial_block"] == block]))
                  for block in held_blocks}
    ten_km_bins = {}
    # At 80 m line spacing, 125 lines are approximately 10 km.
    for tie in heldout:
        key = int(tie["line_center_px"] // 125)
        ten_km_bins.setdefault(key, []).append(tie["residual_iirs_px"])
    ten_km_medians = {str(k): float(np.median(v)) for k, v in ten_km_bins.items() if len(v) >= 3}
    worst_ten_km_median = max(ten_km_medians.values()) if ten_km_medians else None

    criteria = {
        "heldout_median_le_1_iirs_px": float(np.median(residuals)) <= 1.0,
        "heldout_p95_le_2_iirs_px": quantile(residuals, 95) <= 2.0,
        "at_least_3_heldout_cross_track_columns": len(held_columns) >= 3,
        "at_least_4_heldout_spatial_blocks": len(held_blocks) >= 4,
        "all_10km_bins_with_3plus_ties_median_le_1_5_iirs_px": (
            worst_ten_km_median is not None and worst_ten_km_median <= 1.5),
    }
    summary = {
        "status": "relative image-registration diagnostic; not absolute geolocation validation",
        "source": {
            "iirs_image": str(args.iirs_image),
            "iirs_image_sha256": __import__("hashlib").sha256(args.iirs_image.read_bytes()).hexdigest(),
            "iirs_band": 40,
            "wavelength_nm": 1369.6,
            "wac_image": str(args.wac_image),
            "wac_source_etag": metadata["source_http"]["etag"],
            "iirs_geometry_records": len(scans) * len(pixels),
        },
        "method": {
            "cross_track_centers_iirs_px": sorted({t["sample_center_px"] for t in ties}),
            "row_step_px": args.row_step,
            "patch_size_px": [args.patch_width, args.patch_height],
            "search_radius_px": args.search_radius,
            "subpixel_refinement": "Independent parabolic fit around the 2D normalized-correlation peak",
            "score_threshold": score_cut,
            "score_threshold_rule": "25th percentile of training candidate scores only; applied unchanged to held-out ties",
            "fit": "Huber-reweighted affine x/y offset field in normalized sample and line coordinates, fit on training blocks only",
            "heldout_split": f"750-line blocks; block index modulo 3 equals 2; {args.guard_lines}-line boundary guard",
        },
        "tie_counts": {
            "candidate_total": len(ties),
            "training_candidates": len(training_all),
            "heldout_candidates": len(heldout_all),
            "training_used": len(training),
            "heldout_used": len(heldout),
            "heldout_cross_track_columns": held_columns,
            "heldout_spatial_blocks": held_blocks,
        },
        "heldout_residual_iirs_px": {
            "median": float(np.median(residuals)),
            "p90": quantile(residuals, 90),
            "p95": quantile(residuals, 95),
            "rmse": float(np.sqrt(np.mean(np.square(residuals)))),
            "maximum": float(max(residuals)),
            "median_by_750_line_block": by_block,
            "median_by_approx_10km_bin_with_minimum_3_ties": ten_km_medians,
            "worst_approx_10km_bin_median": worst_ten_km_median,
        },
        "predeclared_candidate_criteria": criteria,
        "candidate_gate_result": "pass" if all(criteria.values()) else "fail",
        "limitations": [
            "Only 17 held-out matches remain after applying the training-only score cutoff; tail quantiles are uncertain at this sample size.",
            "WAC and IIRS morphology ties are not surveyed ground-control points.",
            "The affine offset model is a first diagnostic, not the final correction model.",
            "WAC 100 m pixels and IIRS 80 m pixels differ in spatial response.",
            "Residuals measure held-out consistency relative to this WAC warp, not absolute selenographic error.",
            "A poor match can reflect illumination and morphology differences as well as geolocation error.",
        ],
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "opencv": cv2.__version__, "matplotlib": matplotlib.__version__},
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics = args.output_dir / "metrics"
    figures = args.output_dir / "figures"
    metrics.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    csv_path = metrics / "iirs_wac_2d_grid_ties.csv"
    json_path = metrics / "iirs_wac_2d_grid_summary.json"
    fig_path = figures / "iirs_wac_2d_grid_residuals.svg"
    fields = list(dict.fromkeys(k for tie in ties for k in tie.keys()))
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ties)
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    for tie in heldout:
        axes[0].scatter(tie["sample_center_px"], tie["line_center_px"],
                        c=tie["residual_iirs_px"], cmap="viridis", vmin=0, vmax=4,
                        s=35, edgecolors="black", linewidths=0.3)
    axes[0].set_xlim(0, iirs.shape[1])
    axes[0].set_ylim(iirs.shape[0], 0)
    axes[0].set_xlabel("IIRS sample (pixel)")
    axes[0].set_ylabel("IIRS line (pixel)")
    axes[0].set_title("Held-out tie locations; color = residual (IIRS px)")
    axes[0].grid(alpha=0.2)
    axes[1].hist(residuals, bins=18, color="#386cb0", edgecolor="white")
    axes[1].axvline(1.0, color="#2ca25f", linestyle="--", label="median target: 1 px")
    axes[1].axvline(2.0, color="#de2d26", linestyle=":", label="p95 target: 2 px")
    axes[1].set_xlabel("Held-out affine residual (IIRS px)")
    axes[1].set_ylabel("Tie count")
    axes[1].set_title("Held-out residual distribution")
    axes[1].legend()
    fig.savefig(fig_path, format="svg")
    plt.close(fig)
    print(json.dumps(summary, indent=2))
    print(f"CSV: {csv_path}\nJSON: {json_path}\nFigure: {fig_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
