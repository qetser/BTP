#!/usr/bin/env python3
"""Apply the training-fitted SLDEM relative offset model to sparse IIRS geometry.

This creates a separate correction candidate. It does not edit the source
archive or establish absolute geolocation accuracy.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path
from zipfile import ZipFile

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from register_iirs_to_wac import DEFAULT_IIRS_ZIP, interpolate_grid, load_geometry  # noqa: E402

INPUT_SUMMARY = ROOT / "results/phase-1/m1-sldem-hillshade/metrics/iirs_sldem_hillshade_summary.json"
INPUT_TIES = ROOT / "results/phase-1/m1-sldem-hillshade/metrics/iirs_sldem_hillshade_ties.csv"
OUTPUT = ROOT / "results/phase-1/m1-sldem-correction-candidate"
LUNAR_RADIUS_M = 1_737_400.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iirs-zip", type=Path, default=ROOT / DEFAULT_IIRS_ZIP)
    parser.add_argument("--summary", type=Path, default=INPUT_SUMMARY)
    parser.add_argument("--ties", type=Path, default=INPUT_TIES)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()

    prior = json.loads(args.summary.read_text(encoding="utf-8"))
    if prior["status"] != "illumination-matched relative registration diagnostic; not absolute geolocation validation":
        raise ValueError("Unexpected source registration status")
    selected = prior["selected_run"]
    if selected["gate_result"] != "pass":
        raise ValueError("The source held-out relative-registration gate did not pass")
    coeff = np.asarray(selected["coefficients"], dtype=np.float64)
    if coeff.shape != (3, 2):
        raise ValueError(f"Expected a 3x2 affine offset model, got {coeff.shape}")

    rows, scans, pixels, lon_grid, lat_grid, dims = load_geometry(args.iirs_zip)
    lon_dense = interpolate_grid(lon_grid, scans, pixels, dims["lines"], dims["samples"])
    lat_dense = interpolate_grid(lat_grid, scans, pixels, dims["lines"], dims["samples"])
    sample_mesh, scan_mesh = np.meshgrid(pixels, scans)
    norm_sample = (sample_mesh - dims["samples"] / 2.0) / (dims["samples"] / 2.0)
    norm_scan = (scan_mesh - dims["lines"] / 2.0) / (dims["lines"] / 2.0)
    model_input = np.stack((np.ones_like(norm_sample), norm_sample, norm_scan), axis=-1)
    offsets = model_input @ coeff
    corrected_sample = (sample_mesh + offsets[..., 0]).astype(np.float32)
    corrected_scan = (scan_mesh + offsets[..., 1]).astype(np.float32)
    corrected_lon = cv2.remap(lon_dense.astype(np.float32), corrected_sample, corrected_scan,
                              cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    corrected_lat = cv2.remap(lat_dense.astype(np.float32), corrected_sample, corrected_scan,
                              cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if not np.all(np.isfinite(corrected_lon)) or not np.all(np.isfinite(corrected_lat)):
        raise ValueError("Non-finite corrected coordinates")

    out = args.output_dir
    metrics_dir, figures_dir = out / "metrics", out / "figures"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    csv_path = metrics_dir / "iirs_sldem_relative_geometry_candidate.csv"
    east_m = LUNAR_RADIUS_M * np.cos(np.deg2rad(lat_grid)) * np.deg2rad(corrected_lon - lon_grid)
    north_m = LUNAR_RADIUS_M * np.deg2rad(corrected_lat - lat_grid)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["source_scan", "source_pixel", "original_longitude_east_deg",
                  "original_latitude_deg", "predicted_sample_offset_px",
                  "predicted_scan_offset_px", "candidate_longitude_east_deg",
                  "candidate_latitude_deg", "candidate_east_shift_m",
                  "candidate_north_shift_m"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for i, source_row in enumerate(rows):
            si = int(np.searchsorted(scans, int(source_row["Scan"])))
            pi = int(np.searchsorted(pixels, int(source_row["Pixel"])))
            writer.writerow({
                "source_scan": int(source_row["Scan"]),
                "source_pixel": int(source_row["Pixel"]),
                "original_longitude_east_deg": float(lon_grid[si, pi]),
                "original_latitude_deg": float(lat_grid[si, pi]),
                "predicted_sample_offset_px": float(offsets[si, pi, 0]),
                "predicted_scan_offset_px": float(offsets[si, pi, 1]),
                "candidate_longitude_east_deg": float(corrected_lon[si, pi]),
                "candidate_latitude_deg": float(corrected_lat[si, pi]),
                "candidate_east_shift_m": float(east_m[si, pi]),
                "candidate_north_shift_m": float(north_m[si, pi]),
            })

    # Recompute fit residuals from held-out observations without fitting or tuning.
    with args.ties.open(newline="", encoding="utf-8") as handle:
        ties = [row for row in csv.DictReader(handle)
                if row["azimuth_hypothesis"] == prior["selected_azimuth_hypothesis"]
                and row["split"] == "held_out" and row["residual_iirs_px"]]
    points = np.asarray([[(float(t["sample_center_iirs_px"]) - dims["samples"] / 2.0)
                          / (dims["samples"] / 2.0),
                          (float(t["line_center_iirs_px"]) - dims["lines"] / 2.0)
                          / (dims["lines"] / 2.0)] for t in ties])
    predicted = np.column_stack((np.ones(len(points)), points)) @ coeff
    observed = np.asarray([[float(t["offset_x_subpixel_px"]),
                            float(t["offset_y_subpixel_px"])] for t in ties])
    residual = np.linalg.norm(observed - predicted, axis=1)
    saved = np.asarray([float(t["residual_iirs_px"]) for t in ties])
    if len(ties) != selected["heldout_used"] or not np.allclose(residual, saved, atol=1e-5):
        raise ValueError("Held-out residual reproduction does not match the saved registration record")

    summary = {
        "status": "relative geolocation correction candidate; absolute geolocation remains unvalidated",
        "data_version": prior["source"]["iirs_observation"],
        "source_iirs_zip_sha256": sha256(args.iirs_zip),
        "source_registration_summary": str(args.summary.relative_to(ROOT)),
        "source_registration_ties": str(args.ties.relative_to(ROOT)),
        "split": "Training-fitted 2D affine offset field; validation uses the predeclared held-out morphology ties only.",
        "units": {"offset": "IIRS image pixels", "coordinates": "degrees east/degrees north",
                  "shift": "approximate lunar metres using a 1,737,400 m sphere"},
        "method": "Evaluate the saved training-only affine sample/scan offset model at each sparse geometry node, then sample the original dense interpolated geolocation grid at the shifted image coordinate. Source ZIP and coordinates are unchanged.",
        "model_coefficients_sample_scan": coeff.tolist(),
        "sparse_geometry_node_count": len(rows),
        "candidate_shift_summary": {
            "sample_offset_median_px": float(np.median(offsets[..., 0])),
            "sample_offset_min_px": float(offsets[..., 0].min()),
            "sample_offset_max_px": float(offsets[..., 0].max()),
            "scan_offset_median_px": float(np.median(offsets[..., 1])),
            "scan_offset_min_px": float(offsets[..., 1].min()),
            "scan_offset_max_px": float(offsets[..., 1].max()),
            "east_shift_median_abs_m": float(np.median(np.abs(east_m))),
            "east_shift_max_abs_m": float(np.max(np.abs(east_m))),
            "north_shift_median_abs_m": float(np.median(np.abs(north_m))),
            "north_shift_max_abs_m": float(np.max(np.abs(north_m))),
        },
        "heldout_validation": {
            "tie_count": len(residual),
            "median_residual_px": float(np.median(residual)),
            "p95_residual_px": float(np.percentile(residual, 95)),
            "rmse_px": float(np.sqrt(np.mean(residual ** 2))),
            "max_residual_px": float(np.max(residual)),
            "saved_residuals_reproduced_within_1e-5_px": True,
        },
        "outputs": {"csv": str(csv_path.relative_to(ROOT))},
        "limits": [
            "The validation ties are image morphology matches to a DEM-derived hillshade, not surveyed ground controls.",
            "Held-out checks validate the relative offset model against withheld ties; they do not independently establish absolute position accuracy.",
            "The result is a separate sparse geolocation candidate and has not been inserted into the IIRS archive or used for reflectance analysis.",
            "The correction is scene-specific and does not validate radiance, masks, reflectance, or thermal correction.",
        ],
        "code_base_commit": __import__("subprocess").check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_script": "scripts/apply_sldem_relative_geometry_candidate.py",
        "script_sha256": sha256(Path(__file__).resolve()),
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "opencv": cv2.__version__, "matplotlib": matplotlib.__version__},
    }
    json_path = metrics_dir / "iirs_sldem_relative_geometry_candidate_summary.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    axes[0].plot(scans, np.median(offsets[..., 0], axis=1), label="sample offset")
    axes[0].plot(scans, np.median(offsets[..., 1], axis=1), label="scan offset")
    axes[0].set(xlabel="IIRS scan coordinate (pixel)", ylabel="Predicted correction (IIRS pixels)",
                title="Training-fitted correction field")
    axes[0].grid(alpha=0.25)
    axes[0].legend()
    axes[1].scatter(east_m.ravel(), north_m.ravel(), s=5, alpha=0.5)
    axes[1].axhline(0, color="0.5", lw=0.7)
    axes[1].axvline(0, color="0.5", lw=0.7)
    axes[1].set(xlabel="East shift (m)", ylabel="North shift (m)",
                title="Candidate sparse-node displacement")
    axes[1].grid(alpha=0.25)
    fig.suptitle("SLDEM-based relative geolocation candidate, not absolute validation")
    figure_path = figures_dir / "iirs_sldem_relative_geometry_candidate.svg"
    fig.savefig(figure_path, format="svg")
    plt.close(fig)
    summary["outputs"]["figure"] = str(figure_path.relative_to(ROOT))
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"csv": str(csv_path), "summary": str(json_path),
                      "figure": str(figure_path),
                      "heldout_validation": summary["heldout_validation"],
                      "shift_summary": summary["candidate_shift_summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
