#!/usr/bin/env python3
"""Match full-resolution IIRS band 40 to an illumination-matched SLDEM hillshade.

Azimuth orientation is selected from training match scores only. Held-out line
ranges are fixed in the code and are not used for selection or fitting.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from register_iirs_to_wac import (
    DEFAULT_IIRS_ZIP,
    interpolate_grid,
    load_geometry,
)
from register_iirs_to_wac_grid import robust_affine, subpixel_peak


ROOT = Path(__file__).resolve().parents[1]
DEM_DIR = ROOT / "data/reference/sldem2015_e1g2"
NORTH_DEM = DEM_DIR / "SLDEM2015_512_00N_30N_315_360.JP2"
SOUTH_DEM = DEM_DIR / "SLDEM2015_512_30S_00S_315_360.JP2"
NORTH_LBL = DEM_DIR / "SLDEM2015_512_00N_30N_315_360_JP2.LBL"
SOUTH_LBL = DEM_DIR / "SLDEM2015_512_30S_00S_315_360_JP2.LBL"
OUTPUT = ROOT / "results/phase-1/m1-sldem-hillshade"
LUNAR_RADIUS_M = 1_737_400.0
PIXELS_PER_DEGREE = 512
LON_MIN = 352.0
LON_MAX = 359.0
LAT_MAX = 28.5
LAT_MIN = -8.5
X_CROP_START = int((LON_MIN - 315.0) * PIXELS_PER_DEGREE)
X_CROP_STOP = int((LON_MAX - 315.0) * PIXELS_PER_DEGREE)
NORTH_Y_START = int((30.0 - LAT_MAX) * PIXELS_PER_DEGREE)
SOUTH_Y_STOP = int((0.0 - LAT_MIN) * PIXELS_PER_DEGREE)
SUN_AZIMUTH_DEG = 96.319246
SUN_ELEVATION_DEG = 31.690699
# These four ranges do not overlap the held-out ranges from the earlier WAC runs.
HELDOUT_RANGES = [(0, 1000), (2250, 3000), (4500, 5250), (9000, 9750)]
PATCH_WIDTH = 24
PATCH_HEIGHT = 100
SEARCH_RADIUS = 12
ROW_STEP = 250
BLOCK_GUARD = 150
CROSS_TRACK_CENTERS = [25, 75, 125, 175, 225]


def label_value(path: Path, key: str) -> float:
    for line in path.read_text(encoding="ascii", errors="replace").splitlines():
        if line.strip().startswith(key):
            return float(line.split("=", 1)[1].split("<", 1)[0].strip().strip("\""))
    raise ValueError(f"{key} is absent from {path}")


def read_dem_crop(path: Path, row_start: int, row_stop: int) -> tuple[np.ndarray, dict]:
    """Decode one full JP2 tile, keep only the E1G2 local crop, and apply 0.5 m/DN."""
    # SLDEM tiles use signed 16-bit JPEG2000 components. OpenCV's decoder in
    # this environment rejects signed components; Pillow decodes the bit
    # pattern as uint16, so reinterpret it as two's-complement int16 here.
    Image.MAX_IMAGE_PIXELS = None  # These trusted NASA tiles are 354 MP each.
    with Image.open(path) as image:
        raster = np.asarray(image)
    if raster.shape != (15360, 23040) or raster.ndim != 2:
        raise ValueError(f"Unexpected DEM dimensions for {path}: {raster.shape}")
    if raster.dtype == np.uint16:
        raster = raster.view(np.int16)
    if raster.dtype != np.int16:
        raise TypeError(f"Expected signed 16-bit DEM values, got {raster.dtype}")
    crop = raster[row_start:row_stop, X_CROP_START:X_CROP_STOP].astype(np.float32)
    nodata = crop == -32768
    values = crop * 0.5
    values[nodata] = np.nan
    metadata = {
        "decoded_shape_lines_samples": list(raster.shape),
        "decoded_dtype": str(raster.dtype),
        "crop_shape_lines_samples": list(values.shape),
        "crop_nodata_count": int(nodata.sum()),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    del raster, crop, nodata
    return values, metadata


def build_dem_crop() -> tuple[np.ndarray, dict]:
    ppd_n = label_value(NORTH_LBL, "MAP_RESOLUTION")
    ppd_s = label_value(SOUTH_LBL, "MAP_RESOLUTION")
    scale_n = label_value(NORTH_LBL, "MAP_SCALE")
    scale_s = label_value(SOUTH_LBL, "MAP_SCALE")
    if ppd_n != PIXELS_PER_DEGREE or ppd_s != PIXELS_PER_DEGREE or scale_n != scale_s:
        raise ValueError("North/south SLDEM labels do not match the expected grid")
    north, north_meta = read_dem_crop(NORTH_DEM, NORTH_Y_START, 15360)
    south, south_meta = read_dem_crop(SOUTH_DEM, 0, SOUTH_Y_STOP + 1)
    dem = np.concatenate((north, south), axis=0)
    dem_top_lat = LAT_MAX - 0.5 / PIXELS_PER_DEGREE
    dem_left_lon = LON_MIN + 0.5 / PIXELS_PER_DEGREE
    info = {
        "north_tile": north_meta,
        "south_tile": south_meta,
        "projection": "PDS3 simple cylindrical, positive-east longitude",
        "resolution_pixels_per_degree": PIXELS_PER_DEGREE,
        "label_map_scale_km_per_pixel": scale_n,
        "elevation_scale_m_per_stored_count": 0.5,
        "crop_lon_edges_east_deg": [LON_MIN, LON_MAX],
        "crop_lat_edges_deg": [LAT_MAX, LAT_MIN],
        "crop_pixel_center_top_latitude_deg": dem_top_lat,
        "crop_pixel_center_left_longitude_east_deg": dem_left_lon,
        "dem_shape_lines_samples": list(dem.shape),
        "crop_nodata_total": int(np.count_nonzero(~np.isfinite(dem))),
    }
    return dem, info


def make_hillshade(dem: np.ndarray, dem_top_lat: float, azimuth_deg: float) -> np.ndarray:
    """Create a grayscale hillshade with lunar east/north solar-vector components."""
    valid = np.isfinite(dem)
    if not np.all(valid):
        fill = float(np.nanmedian(dem))
        source = np.where(valid, dem, fill).astype(np.float32)
    else:
        source = dem.astype(np.float32, copy=False)
    # Sobel scale 1/8 gives a central finite difference in elevation per pixel.
    dz_de_px = cv2.Sobel(source, cv2.CV_32F, 1, 0, ksize=3, scale=1.0 / 8.0)
    dz_ds_px = cv2.Sobel(source, cv2.CV_32F, 0, 1, ksize=3, scale=1.0 / 8.0)
    lat = dem_top_lat - np.arange(dem.shape[0], dtype=np.float32) / PIXELS_PER_DEGREE
    dy_m = LUNAR_RADIUS_M * np.pi / (180.0 * PIXELS_PER_DEGREE)
    dx_m = dy_m * np.cos(np.deg2rad(lat))
    dz_de = dz_de_px / dx_m[:, None]
    dz_dn = -dz_ds_px / dy_m  # raster rows increase southward

    az = np.deg2rad(azimuth_deg)
    el = np.deg2rad(SUN_ELEVATION_DEG)
    sun_e = np.sin(az) * np.cos(el)
    sun_n = np.cos(az) * np.cos(el)
    sun_u = np.sin(el)
    normal_norm = np.sqrt(dz_de * dz_de + dz_dn * dz_dn + 1.0)
    shade = np.clip((-dz_de * sun_e - dz_dn * sun_n + sun_u) / normal_norm, 0.0, 1.0)
    out = np.round(shade * 255.0).astype(np.uint8)
    out[~valid] = 0
    return out


def hillshade_to_iirs(hillshade: np.ndarray, dem_valid: np.ndarray,
                      lon: np.ndarray, lat: np.ndarray,
                      dem_top_lat: float, dem_left_lon: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    map_x = ((lon - dem_left_lon) * PIXELS_PER_DEGREE).astype(np.float32)
    map_y = ((dem_top_lat - lat) * PIXELS_PER_DEGREE).astype(np.float32)
    in_bounds = ((map_x >= 0) & (map_x < hillshade.shape[1] - 1)
                 & (map_y >= 0) & (map_y < hillshade.shape[0] - 1))
    reference = cv2.remap(hillshade, map_x, map_y, cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT)
    valid_reference = cv2.remap(dem_valid.astype(np.uint8), map_x, map_y,
                                cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT) > 0
    # Gradients at a nodata boundary use filled elevations. Exclude a one-pixel
    # perimeter around nodata from tie matching as well.
    valid_reference = cv2.erode(valid_reference.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    return reference, in_bounds, valid_reference


def classify_line(line: int) -> tuple[str, int | None]:
    for index, (start, stop) in enumerate(HELDOUT_RANGES):
        if start - BLOCK_GUARD <= line < stop + BLOCK_GUARD:
            if start + BLOCK_GUARD <= line < stop - BLOCK_GUARD:
                return "held_out", index
            return "guard", index
    return "training", None


def match_ties(iirs: np.ndarray, reference: np.ndarray, valid_reference: np.ndarray,
               azimuth_hypothesis: str) -> list[dict]:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    a = clahe.apply(iirs)
    b = clahe.apply(reference)
    ax = cv2.Sobel(a, cv2.CV_32F, 1, 0, ksize=3)
    ay = cv2.Sobel(a, cv2.CV_32F, 0, 1, ksize=3)
    bx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3)
    by = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3)
    ties = []
    for y in range(200, iirs.shape[0] - PATCH_HEIGHT, ROW_STEP):
        split, block = classify_line(y)
        for center_x in CROSS_TRACK_CENTERS:
            x0 = center_x - PATCH_WIDTH // 2
            y0 = y - PATCH_HEIGHT // 2
            template_x = ax[y0:y0 + PATCH_HEIGHT, x0:x0 + PATCH_WIDTH]
            template_y = ay[y0:y0 + PATCH_HEIGHT, x0:x0 + PATCH_WIDTH]
            valid_patch = valid_reference[y0:y0 + PATCH_HEIGHT, x0:x0 + PATCH_WIDTH]
            if not np.all(valid_patch):
                continue
            xstart, ystart = x0 - SEARCH_RADIUS, y0 - SEARCH_RADIUS
            search_x = bx[ystart:y0 + PATCH_HEIGHT + SEARCH_RADIUS,
                          xstart:x0 + PATCH_WIDTH + SEARCH_RADIUS]
            search_y = by[ystart:y0 + PATCH_HEIGHT + SEARCH_RADIUS,
                          xstart:x0 + PATCH_WIDTH + SEARCH_RADIUS]
            valid_search = valid_reference[
                ystart:y0 + PATCH_HEIGHT + SEARCH_RADIUS,
                xstart:x0 + PATCH_WIDTH + SEARCH_RADIUS]
            score_map = (cv2.matchTemplate(search_x, template_x, cv2.TM_CCOEFF_NORMED)
                         + cv2.matchTemplate(search_y, template_y, cv2.TM_CCOEFF_NORMED)) / 2.0
            valid_scores = cv2.matchTemplate(
                valid_search.astype(np.float32),
                np.ones((PATCH_HEIGHT, PATCH_WIDTH), dtype=np.float32),
                cv2.TM_CCORR)
            score_map[valid_scores < PATCH_HEIGHT * PATCH_WIDTH] = -1.0
            _, score, _, peak = cv2.minMaxLoc(score_map)
            sub_dx, sub_dy = subpixel_peak(score_map, peak[0], peak[1])
            ties.append({
                "azimuth_hypothesis": azimuth_hypothesis,
                "sample_center_iirs_px": center_x,
                "line_center_iirs_px": y,
                "ncc_gradient_score": float(score),
                "dem_valid_fraction_in_patch": 1.0,
                "offset_x_subpixel_px": float(peak[0] - SEARCH_RADIUS + sub_dx),
                "offset_y_subpixel_px": float(peak[1] - SEARCH_RADIUS + sub_dy),
                "split": split,
                "heldout_block": block,
            })
    return ties


def fit_and_score(ties: list[dict], width: int, height: int) -> dict:
    train_all = [t for t in ties if t["split"] == "training"]
    held_all = [t for t in ties if t["split"] == "held_out"]
    score_cut = float(np.percentile([t["ncc_gradient_score"] for t in train_all], 25))
    train = [t for t in train_all if t["ncc_gradient_score"] >= score_cut]
    held = [t for t in held_all if t["ncc_gradient_score"] >= score_cut]
    if len(train) < 12 or len(held) < 12:
        raise RuntimeError(f"Too few accepted ties at training-only cutoff: train={len(train)}, held={len(held)}")
    points = np.asarray([[(t["sample_center_iirs_px"] - width / 2) / (width / 2),
                          (t["line_center_iirs_px"] - height / 2) / (height / 2)] for t in train])
    offsets = np.asarray([[t["offset_x_subpixel_px"], t["offset_y_subpixel_px"]] for t in train])
    coeff = robust_affine(points, offsets)
    for group in (train, held):
        xy = np.asarray([[(t["sample_center_iirs_px"] - width / 2) / (width / 2),
                          (t["line_center_iirs_px"] - height / 2) / (height / 2)] for t in group])
        pred = np.column_stack((np.ones(len(group)), xy)) @ coeff
        for tie, p in zip(group, pred):
            tie["residual_iirs_px"] = float(np.hypot(tie["offset_x_subpixel_px"] - p[0],
                                                     tie["offset_y_subpixel_px"] - p[1]))
            tie["fit_offset_x_px"] = float(p[0])
            tie["fit_offset_y_px"] = float(p[1])
    residuals = np.asarray([t["residual_iirs_px"] for t in held])
    bins: dict[int, list[float]] = {}
    for tie in held:
        bins.setdefault(int(tie["line_center_iirs_px"] // 125), []).append(tie["residual_iirs_px"])
    bin_medians = {str(k): float(np.median(v)) for k, v in bins.items() if len(v) >= 3}
    worst_bin = max(bin_medians.values()) if bin_medians else None
    held_blocks = sorted({t["heldout_block"] for t in held})
    columns = sorted({t["sample_center_iirs_px"] for t in held})
    criteria = {
        "heldout_median_le_1_iirs_px": float(np.median(residuals)) <= 1,
        "heldout_p95_le_2_iirs_px": float(np.percentile(residuals, 95)) <= 2,
        "at_least_3_cross_track_columns": len(columns) >= 3,
        "at_least_4_heldout_blocks": len(held_blocks) >= 4,
        "all_approx_10km_bins_median_le_1_5_iirs_px": worst_bin is not None and worst_bin <= 1.5,
    }
    return {
        "score_cut": score_cut,
        "score_cut_rule": "25th percentile of training candidate NCC scores; applied unchanged to held-out ties",
        "training_candidates": len(train_all),
        "heldout_candidates": len(held_all),
        "training_used": len(train),
        "heldout_used": len(held),
        "heldout_blocks": held_blocks,
        "heldout_columns_px": columns,
        "median_px": float(np.median(residuals)),
        "p90_px": float(np.percentile(residuals, 90)),
        "p95_px": float(np.percentile(residuals, 95)),
        "rmse_px": float(np.sqrt(np.mean(residuals ** 2))),
        "max_px": float(np.max(residuals)),
        "approx_10km_bin_medians_px": bin_medians,
        "worst_approx_10km_bin_median_px": worst_bin,
        "criteria": criteria,
        "gate_result": "pass" if all(criteria.values()) else "fail",
        "coefficients": coeff.tolist(),
        "training_median_ncc": float(np.median([t["ncc_gradient_score"] for t in train_all])),
        "heldout_ties": held,
        "all_ties": ties,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iirs-image", type=Path,
                        default=ROOT / "data/reference/lroc_wac_e1g2/e1g2_band040_1369nm.png")
    parser.add_argument("--iirs-zip", type=Path, default=ROOT / DEFAULT_IIRS_ZIP)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if not all(p.exists() for p in (NORTH_DEM, SOUTH_DEM, NORTH_LBL, SOUTH_LBL)):
        raise FileNotFoundError("Download the two local SLDEM2015 tiles and their PDS labels first")
    iirs = cv2.imread(str(args.iirs_image), cv2.IMREAD_GRAYSCALE)
    if iirs is None or iirs.shape != (12210, 250):
        raise ValueError(f"Expected the full-resolution 250 x 12210 IIRS band, got {None if iirs is None else iirs.shape}")
    _, scans, pixels, lon_grid, lat_grid, dims = load_geometry(args.iirs_zip)
    lon = interpolate_grid(lon_grid, scans, pixels, dims["lines"], dims["samples"])
    lat = interpolate_grid(lat_grid, scans, pixels, dims["lines"], dims["samples"])
    dem, dem_source = build_dem_crop()
    dem_top = float(dem_source["crop_pixel_center_top_latitude_deg"])
    dem_left = float(dem_source["crop_pixel_center_left_longitude_east_deg"])
    row_lat = dem_top - np.arange(dem.shape[0], dtype=np.float32) / PIXELS_PER_DEGREE
    dy = LUNAR_RADIUS_M * np.pi / (180.0 * PIXELS_PER_DEGREE)
    dx = dy * np.cos(np.deg2rad(row_lat))
    dem_source["nominal_ground_pixel_spacing_m"] = {
        "north_south": dy,
        "east_west_at_scene_mean_latitude": float(np.median(dx[(row_lat >= -7) & (row_lat <= 27)])),
    }
    in_scene = ((lon >= LON_MIN) & (lon <= LON_MAX) & (lat >= LAT_MIN) & (lat <= LAT_MAX))
    if float(in_scene.mean()) < 0.99:
        raise ValueError("More than 1% of IIRS geometry points fall outside the downloaded DEM crop")

    hypotheses = {
        "clockwise_from_north": SUN_AZIMUTH_DEG,
        "reverse_azimuth": (SUN_AZIMUTH_DEG + 180.0) % 360.0,
    }
    runs = {}
    for name, azimuth in hypotheses.items():
        hillshade = make_hillshade(dem, dem_top, azimuth)
        reference, in_bounds, valid_reference = hillshade_to_iirs(
            hillshade, np.isfinite(dem), lon, lat, dem_top, dem_left)
        if not np.all(in_bounds):
            raise ValueError("IIRS geometry extends beyond the local DEM hillshade")
        candidates = match_ties(iirs, reference, valid_reference, name)
        runs[name] = fit_and_score(candidates, iirs.shape[1], iirs.shape[0])
        runs[name]["azimuth_deg"] = azimuth
        runs[name]["scene_geometry_pixel_coverage_fraction"] = float(np.mean(in_scene))
        if name == "clockwise_from_north":
            selected_reference = reference
            selected_hillshade = hillshade
        del hillshade, reference

    # Select orientation from training NCC only. Do not inspect either holdout residual here.
    selected_name = max(runs, key=lambda key: runs[key]["training_median_ncc"])
    chosen = runs[selected_name]
    # Recreate the chosen hillshade for saved diagnostics if reverse orientation won.
    if selected_name != "clockwise_from_north":
        selected_hillshade = make_hillshade(dem, dem_top, hypotheses[selected_name])
        selected_reference, _, _ = hillshade_to_iirs(
            selected_hillshade, np.isfinite(dem), lon, lat, dem_top, dem_left)

    # Save a compact check image that shows the IIRS image and selected warped hillshade.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir = args.output_dir / "metrics"
    figures_dir = args.output_dir / "figures"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_path = figures_dir / "iirs_sldem_hillshade_tie_residuals.svg"
    csv_path = metrics_dir / "iirs_sldem_hillshade_ties.csv"
    json_path = metrics_dir / "iirs_sldem_hillshade_summary.json"

    fieldnames = list(dict.fromkeys(k for run in runs.values() for tie in run["all_ties"] for k in tie))
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for run in runs.values():
            writer.writerows(run["all_ties"])

    public_runs = {}
    for name, run in runs.items():
        public_runs[name] = {key: value for key, value in run.items()
                             if key not in {"all_ties", "heldout_ties"}}
    summary = {
        "status": "illumination-matched relative registration diagnostic; not absolute geolocation validation",
        "source": {
            "iirs_observation": "20260227T1239538758",
            "iirs_band": 40,
            "iirs_wavelength_nm": 1369.6,
            "iirs_image_sha256": hashlib.sha256(args.iirs_image.read_bytes()).hexdigest(),
            "iirs_sun_azimuth_deg": SUN_AZIMUTH_DEG,
            "iirs_sun_elevation_deg": SUN_ELEVATION_DEG,
            "sun_angles_scope": "Scene-level Product_Parameters in the calibrated PDS4 label",
            "dem": "SLDEM2015 512 pixels/degree north/south tile pair",
            "dem_source_page": "https://pgda.gsfc.nasa.gov/products/54",
            "dem_tile_index": "https://imbrium.mit.edu/DATA/SLDEM2015/TILES/JP2/",
            "dem_tiles": dem_source,
            "code_base_commit": __import__("subprocess").check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "working_tree_script": "scripts/register_iirs_to_sldem_hillshade.py",
        },
        "method": {
            "dem_hillshade": "Central-gradient surface normals and Lambertian hillshade; 0.5 m per stored DEM count; elevation ignored in reflectance",
            "azimuth_hypotheses": hypotheses,
            "azimuth_selection": "Choose the direction with the higher median training candidate NCC score only",
            "tie_grid": {"cross_track_centers_iirs_px": CROSS_TRACK_CENTERS,
                         "line_step_px": ROW_STEP,
                         "patch_size_px": [PATCH_WIDTH, PATCH_HEIGHT],
                         "search_radius_px": SEARCH_RADIUS,
            "subpixel_peak_fit": "Independent parabolic fit around the 2D gradient NCC maximum"},
            "heldout_ranges_iirs_lines": HELDOUT_RANGES,
            "heldout_guard_lines": BLOCK_GUARD,
            "heldout_selection_note": "These ranges avoid the earlier WAC held-out line ranges; no held-out scores selected the azimuth or model.",
            "offset_model": "Huber-reweighted affine 2D offset field fit on training matches only",
            "threshold_rule": "For the selected azimuth, use training candidate score q25 and apply unchanged to held-out ties",
        },
        "orientation_training_comparison": {
            name: {"azimuth_deg": run["azimuth_deg"],
                   "training_median_ncc": run["training_median_ncc"],
                   "training_candidates": run["training_candidates"]}
            for name, run in runs.items()
        },
        "selected_azimuth_hypothesis": selected_name,
        "selected_run": public_runs[selected_name],
        "candidate_acceptance_limits": {
            "heldout_median_le_1_iirs_px": 1.0,
            "heldout_p95_le_2_iirs_px": 2.0,
            "minimum_cross_track_columns": 3,
            "minimum_heldout_blocks": 4,
            "approx_10km_bin_median_max_iirs_px": 1.5,
        },
        "limitations": [
            "The IIRS label gives a scene-level sun azimuth but does not state its positive direction; both orientations were tested, with selection based on training NCC only.",
            "Only the selected orientation's held-out residuals evaluate the candidate gate; the other orientation is retained as a training-selected alternative comparison.",
            "The IIRS geometry table is sparse and its interpolation is the initial map for hillshade sampling.",
            "These are morphology matches to a DEM-derived hillshade, not surveyed ground controls or absolute geolocation error.",
            "Only the local 2026 E1G2 strip was tested; the result does not validate radiance, masks, reflectance, or thermal correction.",
            "The DEM grid is finer than IIRS and may contain different spatial detail; WAC and IIRS image formation also differ.",
        ],
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "opencv": cv2.__version__, "matplotlib": matplotlib.__version__},
    }
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    held = chosen["heldout_ties"]
    residuals = [t["residual_iirs_px"] for t in held]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    axes[0, 0].imshow(iirs, cmap="gray", aspect="auto")
    axes[0, 0].set_title("IIRS band 40, display stretch")
    axes[0, 1].imshow(selected_reference, cmap="gray", aspect="auto")
    axes[0, 1].set_title(f"SLDEM hillshade warped to IIRS; {selected_name}")
    sc = axes[1, 0].scatter([t["sample_center_iirs_px"] for t in held],
                            [t["line_center_iirs_px"] for t in held],
                            c=[t["residual_iirs_px"] for t in held], cmap="magma", vmin=0, vmax=5,
                            s=35, edgecolors="white", linewidths=0.3)
    axes[1, 0].set_xlim(0, iirs.shape[1])
    axes[1, 0].set_ylim(iirs.shape[0], 0)
    axes[1, 0].set_title("Held-out ties; residual in IIRS pixels")
    axes[1, 0].set_xlabel("Sample")
    axes[1, 0].set_ylabel("Line")
    fig.colorbar(sc, ax=axes[1, 0], label="Residual (IIRS px)")
    axes[1, 1].hist(residuals, bins=16, color="#4c78a8", edgecolor="white")
    axes[1, 1].axvline(1, color="#2ca25f", linestyle="--", label="median limit 1 px")
    axes[1, 1].axvline(2, color="#d62728", linestyle=":", label="p95 limit 2 px")
    axes[1, 1].set_title(f"Held-out residuals: median {chosen['median_px']:.2f}, p95 {chosen['p95_px']:.2f} px")
    axes[1, 1].set_xlabel("Residual (IIRS px)")
    axes[1, 1].set_ylabel("Tie count")
    axes[1, 1].legend()
    fig.savefig(figure_path, format="svg")
    plt.close(fig)
    print(json.dumps({"selected_azimuth": selected_name,
                      "orientation_training_comparison": summary["orientation_training_comparison"],
                      "heldout_result": {k: public_runs[selected_name][k] for k in
                                         ("heldout_used", "heldout_blocks", "heldout_columns_px",
                                          "median_px", "p95_px", "rmse_px", "gate_result")},
                      "csv": str(csv_path), "json": str(json_path), "figure": str(figure_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
