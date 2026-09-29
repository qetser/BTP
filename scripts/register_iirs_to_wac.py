#!/usr/bin/env python3
"""Register the E1G2 IIRS browse image to a georeferenced LROC WAC crop.

The sparse IIRS longitude/latitude grid provides an initial orthographic warp.
Local image patches then provide tie-point offsets. Spatially separated training
patches estimate an affine offset field; held-out patches measure residuals.
"""

from __future__ import annotations

import argparse
import hashlib
import csv
import io
import json
import platform
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import cv2
import matplotlib.pyplot as plt
import numpy as np


DEFAULT_IIRS_ZIP = Path(
    "data/pradan/e1g2_candidate_20260227T1239538758/"
    "ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
)
DEFAULT_WAC_IMAGE = Path("data/reference/lroc_wac_e1g2/e1g2_wac_crop.pgm")
DEFAULT_WAC_METADATA = Path("results/phase-1/m1-reference-data/wac_crop_metadata.json")
DEFAULT_OUTPUT_DIR = Path("results/phase-1/m1-reference-data")
LUNAR_RADIUS_M = 1_737_400.0
SPATIAL_BLOCK_HEIGHT = 1000


def read_archive_product(archive_path: Path, suffix: str) -> bytes:
    with zipfile.ZipFile(archive_path) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise ValueError("Expected one {} product; found {}".format(suffix, len(matches)))
        return archive.read(matches[0])


def archive_label_values(archive_path: Path, suffix: str):
    root = ElementTree.fromstring(read_archive_product(archive_path, suffix))
    values = {}
    for element in root.iter():
        name = element.tag.rsplit("}", 1)[-1]
        if name in {"creation_date_time", "md5_checksum"} and element.text:
            values[name] = element.text.strip()
    return values


def load_geometry(archive_path: Path):
    csv_bytes = read_archive_product(archive_path, "_g_grd_d18.csv")
    rows = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
    scans = np.array(sorted({int(row["Scan"]) for row in rows}), dtype=np.float64)
    pixels = np.array(sorted({int(row["Pixel"]) for row in rows}), dtype=np.float64)
    lookup = {
        (int(row["Scan"]), int(row["Pixel"])): (
            float(row["Longitude"]), float(row["Latitude"])
        )
        for row in rows
    }
    longitude_grid = np.empty((len(scans), len(pixels)), dtype=np.float64)
    latitude_grid = np.empty_like(longitude_grid)
    for i, scan in enumerate(scans.astype(int)):
        for j, pixel in enumerate(pixels.astype(int)):
            longitude_grid[i, j], latitude_grid[i, j] = lookup[(scan, pixel)]

    dims = read_archive_product(archive_path, ".hdr").decode("ascii", errors="replace")
    dimensions = {}
    for key in ("samples", "lines"):
        for line in dims.splitlines():
            if line.lower().startswith(key + " ="):
                dimensions[key] = int(line.split("=", 1)[1].strip())
                break
    if set(dimensions) != {"samples", "lines"}:
        raise ValueError("Could not read IIRS samples and lines from ENVI header")

    return rows, scans, pixels, longitude_grid, latitude_grid, dimensions


def interpolate_grid(values, scans, pixels, lines_count, samples_count):
    line_coordinates = np.arange(lines_count, dtype=np.float64)
    sample_coordinates = np.arange(samples_count, dtype=np.float64)
    by_sample = np.stack(
        [np.interp(sample_coordinates, pixels, row) for row in values], axis=0
    )
    return np.stack(
        [np.interp(line_coordinates, scans, by_sample[:, j]) for j in range(samples_count)],
        axis=1,
    )


def geometry_warp_maps(longitude_deg, latitude_deg, wac_metadata):
    longitude = np.deg2rad(longitude_deg)
    latitude = np.deg2rad(latitude_deg)
    x_m = LUNAR_RADIUS_M * np.cos(latitude) * np.sin(longitude)
    y_m = LUNAR_RADIUS_M * np.sin(latitude)
    tiepoint = wac_metadata["model_tiepoint"]
    scale = wac_metadata["pixel_scale_model_units"]
    crop_x0 = wac_metadata["crop_origin_sample"]
    crop_y0 = wac_metadata["crop_origin_line"]
    map_x = ((x_m - tiepoint[3]) / scale[0] - crop_x0).astype(np.float32)
    map_y = ((tiepoint[4] - y_m) / scale[1] - crop_y0).astype(np.float32)
    return map_x, map_y


def local_ties(iirs_image, wac_image, image_to_cube_scale_x, image_to_cube_scale_y, patch_height, patch_width, radius):
    """Estimate local WAC-pixel shifts by matching image gradients."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    iirs_equalized = clahe.apply(iirs_image)
    wac_equalized = clahe.apply(wac_image)
    iirs_dx = cv2.Sobel(iirs_equalized, cv2.CV_32F, 1, 0, ksize=3)
    iirs_dy = cv2.Sobel(iirs_equalized, cv2.CV_32F, 0, 1, ksize=3)
    wac_dx = cv2.Sobel(wac_equalized, cv2.CV_32F, 1, 0, ksize=3)
    wac_dy = cv2.Sobel(wac_equalized, cv2.CV_32F, 0, 1, ksize=3)

    image_height, image_width = iirs_image.shape
    x0 = max(radius + 1, (image_width - patch_width) // 2)
    last_y = image_height - radius - patch_height - 1
    candidates = []
    # Spatial blocks separate training patches from validation regions.
    for y0 in range(radius + 1, last_y, 100):
        x_start = x0 - radius
        y_start = y0 - radius
        search_dx = wac_dx[y_start:y0 + patch_height + radius, x_start:x0 + patch_width + radius]
        search_dy = wac_dy[y_start:y0 + patch_height + radius, x_start:x0 + patch_width + radius]
        template_dx = iirs_dx[y0:y0 + patch_height, x0:x0 + patch_width]
        template_dy = iirs_dy[y0:y0 + patch_height, x0:x0 + patch_width]
        if search_dx.shape[0] < patch_height or search_dx.shape[1] < patch_width:
            continue
        corr_dx = cv2.matchTemplate(search_dx, template_dx, cv2.TM_CCOEFF_NORMED)
        corr_dy = cv2.matchTemplate(search_dy, template_dy, cv2.TM_CCOEFF_NORMED)
        scores = (corr_dx + corr_dy) / 2.0
        _, score, _, location = cv2.minMaxLoc(scores)
        dx_browse = float(location[0] - radius)
        dy_browse = float(location[1] - radius)
        block = int((y0 + patch_height / 2) // SPATIAL_BLOCK_HEIGHT)
        split = "held_out" if block % 4 == 3 else "training"
        guard = 1.5 * patch_height
        distance_to_boundary = min(
            ((y0 + patch_height / 2) % SPATIAL_BLOCK_HEIGHT),
            SPATIAL_BLOCK_HEIGHT - ((y0 + patch_height / 2) % SPATIAL_BLOCK_HEIGHT),
        )
        if distance_to_boundary < guard:
            split = "guard"
        in_search_interior = abs(dx_browse) < radius - 1 and abs(dy_browse) < radius - 1
        accepted = bool(score >= 0.15 and in_search_interior and split != "guard")
        candidates.append(
            {
                "tie_id": len(candidates) + 1,
                "image_center_x_px": x0 + patch_width / 2,
                "image_center_y_px": y0 + patch_height / 2,
                "image_to_cube_sample_scale": image_to_cube_scale_x,
                "image_to_cube_line_scale": image_to_cube_scale_y,
                "ncc_gradient_score": float(score),
                "offset_x_image_px": dx_browse,
                "offset_y_image_px": dy_browse,
                "offset_x_iirs_cube_px": dx_browse * image_to_cube_scale_x,
                "offset_y_iirs_cube_px": dy_browse * image_to_cube_scale_y,
                "block_id": block,
                "split": split,
                "accepted_tie": accepted,
            }
        )
    return candidates


def robust_along_track_fit(points, values):
    """Fit linear x/y offset trends against along-track browse line."""
    design = np.column_stack((np.ones(len(points)), points[:, 1]))
    weights = np.ones(len(points), dtype=np.float64)
    coefficients = np.zeros((3, values.shape[1]), dtype=np.float64)
    for _ in range(20):
        root_weights = np.sqrt(weights)
        coefficients = np.linalg.lstsq(
            design * root_weights[:, None], values * root_weights[:, None], rcond=None
        )[0]
        residuals = np.linalg.norm(values - design @ coefficients, axis=1)
        scale = max(0.5, 1.4826 * np.median(np.abs(residuals - np.median(residuals))))
        cutoff = 1.345 * scale
        new_weights = np.ones_like(weights)
        large = residuals > cutoff
        new_weights[large] = cutoff / residuals[large]
        if np.max(np.abs(new_weights - weights)) < 1e-5:
            break
        weights = new_weights
    return design, coefficients, residuals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iirs-zip", type=Path, default=DEFAULT_IIRS_ZIP)
    parser.add_argument("--iirs-image", type=Path, help="Optional full-resolution grayscale IIRS band image")
    parser.add_argument("--iirs-image-metadata", type=Path)
    parser.add_argument("--image-description", default="Official IIRS browse image")
    parser.add_argument("--artifact-suffix", default="browse")
    parser.add_argument("--wac-image", type=Path, default=DEFAULT_WAC_IMAGE)
    parser.add_argument("--wac-metadata", type=Path, default=DEFAULT_WAC_METADATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--patch-height", type=int, default=192)
    parser.add_argument("--patch-width", type=int, default=100)
    parser.add_argument("--search-radius", type=int, default=30)
    args = parser.parse_args()

    browse_label = None
    if args.iirs_image is None:
        browse_bytes = read_archive_product(args.iirs_zip, "_b_brw_d18.png")
        browse_label = archive_label_values(args.iirs_zip, "_b_brw_d18.xml")
        image_md5 = hashlib.md5(browse_bytes).hexdigest()
        if browse_label.get("md5_checksum") != image_md5:
            raise ValueError("IIRS browse checksum does not match its PDS label")
        image_array = np.frombuffer(browse_bytes, dtype=np.uint8)
        iirs_image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
        image_description = args.image_description
    else:
        iirs_image = cv2.imread(str(args.iirs_image), cv2.IMREAD_GRAYSCALE)
        image_md5 = hashlib.md5(args.iirs_image.read_bytes()).hexdigest()
        image_description = args.image_description
    image_source_metadata = (
        json.loads(args.iirs_image_metadata.read_text(encoding="utf-8"))
        if args.iirs_image_metadata
        else None
    )
    if iirs_image is None:
        raise ValueError("Could not decode the selected IIRS image")

    rows, scans, pixels, longitude_grid, latitude_grid, dimensions = load_geometry(args.iirs_zip)
    wac_metadata = json.loads(args.wac_metadata.read_text(encoding="utf-8"))
    wac_image = cv2.imread(str(args.wac_image), cv2.IMREAD_GRAYSCALE)
    if wac_image is None:
        raise ValueError("Could not read WAC crop: {}".format(args.wac_image))

    lines_count, samples_count = dimensions["lines"], dimensions["samples"]
    scale_x = samples_count / iirs_image.shape[1]
    scale_y = lines_count / iirs_image.shape[0]
    if args.iirs_image is None and abs(scale_x - scale_y) > 0.01:
        raise ValueError("Browse image has unequal sample and line scaling")

    longitude = interpolate_grid(
        longitude_grid, scans, pixels, lines_count, samples_count
    )
    latitude = interpolate_grid(latitude_grid, scans, pixels, lines_count, samples_count)
    map_x, map_y = geometry_warp_maps(longitude, latitude, wac_metadata)
    reference_native = cv2.remap(
        wac_image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT
    )
    reference_browse = cv2.resize(
        reference_native,
        (iirs_image.shape[1], iirs_image.shape[0]),
        interpolation=cv2.INTER_AREA,
    )

    ties = local_ties(
        iirs_image,
        reference_browse,
        scale_x,
        scale_y,
        args.patch_height,
        args.patch_width,
        args.search_radius,
    )
    accepted = [tie for tie in ties if tie["accepted_tie"]]
    train = [tie for tie in accepted if tie["split"] == "training"]
    heldout = [tie for tie in accepted if tie["split"] == "held_out"]
    if len(train) < 6 or len(heldout) < 4:
        raise RuntimeError(
            "Insufficient tie points: {} training, {} held out; inspect texture or adjust patch settings".format(
                len(train), len(heldout)
            )
        )

    train_points = np.array(
        [[tie["image_center_x_px"], tie["image_center_y_px"]] for tie in train]
    )
    train_offsets = np.array(
        [[tie["offset_x_image_px"], tie["offset_y_image_px"]] for tie in train]
    )
    _, coefficients, _ = robust_along_track_fit(train_points, train_offsets)
    for tie in accepted:
        point = np.array([1.0, tie["image_center_y_px"]], dtype=np.float64)
        observed = np.array(
            [tie["offset_x_image_px"], tie["offset_y_image_px"]], dtype=np.float64
        )
        predicted = point @ coefficients
        residual = observed - predicted
        tie["fitted_correction_x_image_px"] = float(predicted[0])
        tie["fitted_correction_y_image_px"] = float(predicted[1])
        tie["fit_residual_x_image_px"] = float(residual[0])
        tie["fit_residual_y_image_px"] = float(residual[1])
        tie["fit_residual_image_px"] = float(np.linalg.norm(residual))
        residual_cube_px = np.array([residual[0] * scale_x, residual[1] * scale_y])
        tie["fit_residual_iirs_px"] = float(np.linalg.norm(residual_cube_px))
        sample = int(np.clip(round(tie["image_center_x_px"] * scale_x), 1, samples_count - 2))
        line = int(np.clip(round(tie["image_center_y_px"] * scale_y), 1, lines_count - 2))
        local_wac_px_per_sample = np.array(
            [
                (map_x[line, sample + 1] - map_x[line, sample - 1]) / 2.0,
                (map_y[line, sample + 1] - map_y[line, sample - 1]) / 2.0,
            ]
        )
        local_wac_px_per_line = np.array(
            [
                (map_x[line + 1, sample] - map_x[line - 1, sample]) / 2.0,
                (map_y[line + 1, sample] - map_y[line - 1, sample]) / 2.0,
            ]
        )
        map_scale = np.array(wac_metadata["pixel_scale_model_units"][:2], dtype=np.float64)
        residual_map_m = np.array(
            [
                residual_cube_px[0] * local_wac_px_per_sample[0] * map_scale[0]
                + residual_cube_px[1] * local_wac_px_per_line[0] * map_scale[0],
                -residual_cube_px[0] * local_wac_px_per_sample[1] * map_scale[1]
                -residual_cube_px[1] * local_wac_px_per_line[1] * map_scale[1],
            ]
        )
        tie["fit_residual_wac_projected_m"] = float(np.linalg.norm(residual_map_m))

    heldout_residuals = np.array(
        [tie["fit_residual_image_px"] for tie in heldout], dtype=np.float64
    )
    heldout_iirs_residuals = np.array(
        [tie["fit_residual_iirs_px"] for tie in heldout], dtype=np.float64
    )
    heldout_map_m = np.array(
        [tie["fit_residual_wac_projected_m"] for tie in heldout], dtype=np.float64
    )
    heldout_scores = np.array([tie["ncc_gradient_score"] for tie in heldout])
    summary = {
        "status": "provisional registration diagnostic; not a calibration validation",
        "iirs_observation": "20260227T1239538758",
        "iirs_archive": str(args.iirs_zip),
        "iirs_image_description": image_description,
        "iirs_image_path": str(args.iirs_image) if args.iirs_image else "browse product stored in IIRS archive",
        "iirs_image_md5": image_md5,
        "iirs_image_source_metadata": image_source_metadata,
        "iirs_browse_label": browse_label,
        "iirs_dimensions_samples_lines": [samples_count, lines_count],
        "iirs_geometry_record_count": len(rows),
        "iirs_geometry_sample_positions": len(pixels),
        "iirs_geometry_scan_positions": len(scans),
        "analysis_image_dimensions_width_height": [iirs_image.shape[1], iirs_image.shape[0]],
        "analysis_image_to_cube_sample_scale": scale_x,
        "analysis_image_to_cube_line_scale": scale_y,
        "wac_image": str(args.wac_image),
        "wac_metadata": str(args.wac_metadata),
        "wac_source_etag": wac_metadata["source_http"]["etag"],
        "wac_source_last_modified": wac_metadata["source_http"]["last_modified"],
        "software_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "opencv": cv2.__version__,
            "matplotlib": plt.matplotlib.__version__,
        },
        "initial_transform": "Interpolate sparse IIRS lon/lat grid; project to WAC orthographic GeoTIFF coordinates; remap WAC into the IIRS image grid",
        "tie_method": "Patch matching on x/y Sobel gradients after CLAHE, OpenCV TM_CCOEFF_NORMED",
        "training_split": "Spatial blocks 0-2 modulo 4, with 1.5 patch-height guard near block boundaries",
        "heldout_split": "Every fourth 1000-image-line block, separated from training ties by guard zones",
        "accepted_tie_rule": "Mean gradient NCC >= 0.15 and match peak at least 1 pixel inside search radius",
        "candidate_ties": len(ties),
        "accepted_training_ties": len(train),
        "accepted_heldout_ties": len(heldout),
        "heldout_spatial_blocks": len({tie["block_id"] for tie in heldout}),
        "heldout_ncc_median": float(np.median(heldout_scores)),
        "heldout_ncc_min": float(np.min(heldout_scores)),
        "heldout_residual_median_image_px": float(np.median(heldout_residuals)),
        "heldout_residual_rmse_image_px": float(np.sqrt(np.mean(heldout_residuals**2))),
        "heldout_residual_p95_image_px": float(np.percentile(heldout_residuals, 95)),
        "heldout_residual_rmse_iirs_px": float(np.sqrt(np.mean(heldout_iirs_residuals**2))),
        "heldout_residual_p95_iirs_px": float(np.percentile(heldout_iirs_residuals, 95)),
        "heldout_residual_rmse_wac_projected_m": float(np.sqrt(np.mean(heldout_map_m**2))),
        "heldout_residual_p95_wac_projected_m": float(np.percentile(heldout_map_m, 95)),
        "correction_model": "Robust linear along-track trend of horizontal and vertical tie offsets, fit on training blocks only",
        "correction_coefficients": {
            "image_pixel_intercept_xy": coefficients[0].tolist(),
            "image_pixel_slope_per_line_xy": coefficients[1].tolist(),
        },
        "units_note": "Image offsets are multiplied by the image-to-cube scale. Map metres use the local interpolated IIRS-to-WAC GeoTIFF-coordinate Jacobian and GeoTIFF map scale; these are projected map distances, not lunar surface ground distances.",
        "limitations": [
            "Image tie offsets use a display-stretched IIRS raster. Radiance validation and masks remain open.",
            "Patch matches are image tie points, not surveyed ground control points.",
            "LROC WAC is a morphology reference only and cannot validate IIRS radiometry.",
            "Matched patches are spatially distributed but not statistically independent observations.",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "metrics/iirs_wac_registration_{}_ties.csv".format(args.artifact_suffix)
    json_path = args.output_dir / "metrics/iirs_wac_registration_{}_summary.json".format(args.artifact_suffix)
    fig_path = args.output_dir / "figures/iirs_wac_registration_{}_residuals.svg".format(args.artifact_suffix)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(key for tie in ties for key in tie.keys()))
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ties)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    train_y = [tie["image_center_y_px"] for tie in train]
    train_shift = [tie["offset_x_image_px"] for tie in train]
    held_y = [tie["image_center_y_px"] for tie in heldout]
    held_shift = [tie["offset_x_image_px"] for tie in heldout]
    axes[0].scatter(train_y, train_shift, label="Training ties", s=24, alpha=0.8)
    axes[0].scatter(held_y, held_shift, label="Held-out ties", s=30, marker="x")
    axes[0].set_ylabel("Observed horizontal offset (image pixels)")
    axes[0].set_title("WAC-to-IIRS image tie offsets")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    for group, marker, label in ((train, "o", "Training ties"), (heldout, "x", "Held-out ties")):
        axes[1].scatter(
            [tie["image_center_y_px"] for tie in group],
            [tie["fit_residual_image_px"] for tie in group],
            marker=marker,
            label=label,
            s=28,
        )
    axes[1].set_xlabel("IIRS image line")
    axes[1].set_ylabel("Residual after training offset fit (image pixels)")
    axes[1].grid(alpha=0.25)
    axes[1].legend()
    fig.savefig(fig_path, format="svg")
    plt.close(fig)
    svg_lines = fig_path.read_text(encoding="utf-8").splitlines()
    fig_path.write_text("\n".join(line.rstrip() for line in svg_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print("Tie table: {}".format(csv_path))
    print("Summary: {}".format(json_path))
    print("Figure: {}".format(fig_path))


if __name__ == "__main__":
    main()
