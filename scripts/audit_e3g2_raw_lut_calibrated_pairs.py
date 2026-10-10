#!/usr/bin/env python3
"""Audit the paired 2020 E3G2 raw/LUT/calibrated path by valid band.

Run from the repository root:
  uv run --no-project --with numpy --with matplotlib python scripts/audit_e3g2_raw_lut_calibrated_pairs.py

This reports threshold comparisons as candidate diagnostics only. It does not
assign saturation or fill masks and does not create reflectance.
"""
from __future__ import annotations

import csv
import io
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "results/phase-1/m1-inventory/iirs_inventory.csv"
VALIDITY = ROOT / "results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv"
OFFICIAL = ROOT / "data/pradan/iir.zip"
SAT_CSV = "iir/calibration/ch2_iirs_cal_e3g2_saturations_radiance.csv"
SAT_XML = "iir/calibration/ch2_iirs_cal_e3g2_saturations_radiance.xml"
LUT_CSV = "iir/calibration/ch2_iirs_cal_e3g2_lut_coeff.csv"
OUT = ROOT / "results/phase-1/m1-e3g2-lineage-check"
CSV_OUT = OUT / "metrics/e3g2_raw_lut_calibrated_by_band.csv"
JSON_OUT = OUT / "metrics/e3g2_raw_lut_calibrated_summary.json"
FIG_OUT = OUT / "figures/e3g2_raw_lut_calibrated_diagnostics.png"


def descendants(node, name):
    return [element for element in node.iter() if element.tag.split("}")[-1] == name]


def first_text(node, name):
    found = descendants(node, name)
    return found[0].text.strip() if found and found[0].text else ""


def read_products():
    with INVENTORY.open(newline="") as handle:
        entries = list(csv.DictReader(handle))
    selected = [r for r in entries if r["product_kind"] in {"raw", "calibrated"}
                and "20200208" in r["product_id"]]
    products = {kind: {} for kind in ("raw", "calibrated")}
    for item in selected:
        suffix = "m65" if item["product_id"].endswith("_m65") else "d18"
        products[item["product_kind"]][suffix] = item
    if any(set(products[k]) != {"m65", "d18"} for k in products):
        raise ValueError("Expected the matched 2020 E3G2 raw and calibrated m65/d18 products")
    return products


def main():
    (OUT / "metrics").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    products = read_products()

    valid = {}
    centers = {}
    with VALIDITY.open(newline="") as handle:
        for row in csv.DictReader(handle):
            band = int(row["band_number"])
            valid[band] = row["E3G2_valid"] == "1"
            centers[band] = float(row["wavelength_nm"])

    with ZipFile(OFFICIAL) as official:
        sat_rows = list(csv.reader(io.StringIO(official.read(SAT_CSV).decode("ascii"))))
        # E3G2 saturation rows are 0-based; map row n to spectral band n+1.
        saturation = np.asarray([float(row[1]) for row in sat_rows], dtype=np.float64)
        dynamic_range = np.asarray([float(row[2]) for row in sat_rows], dtype=np.float64)
        sat_label = ET.fromstring(official.read(SAT_XML))
        table_units = [e.text.strip() for e in descendants(sat_label, "unit") if e.text]
        sat_unit = table_units[0] if table_units else ""
        lut_rows = [tuple(map(float, row)) for row in csv.reader(
            io.StringIO(official.read(LUT_CSV).decode("ascii")))]
    lut = np.asarray(lut_rows, dtype=np.float64).reshape(256, 250, 2)

    rows = []
    scene_summaries = {}
    plot_data = {}
    for suffix in ("m65", "d18"):
        raw_item = products["raw"][suffix]
        cal_item = products["calibrated"][suffix]
        raw_label = ET.parse(ROOT / raw_item["label_path"]).getroot()
        cal_label = ET.parse(ROOT / cal_item["label_path"]).getroot()
        raw_shape = (256, int(raw_item["line_count"]), int(raw_item["sample_count"]))
        cal_shape = (256, int(cal_item["line_count"]), int(cal_item["sample_count"]))
        if raw_shape != cal_shape:
            raise ValueError(f"Raw/calibrated dimensions differ for {suffix}: {raw_shape} vs {cal_shape}")
        raw_type, cal_type = first_text(raw_label, "data_type"), first_text(cal_label, "data_type")
        if raw_type != "UnsignedLSB2" or cal_type != "IEEE754LSBSingle":
            raise ValueError(f"Unexpected data types for {suffix}: {raw_type}, {cal_type}")
        unit = first_text(cal_label, "unit")
        if unit == "mW/cm**2/sr/µm":
            cal_to_mw = 1.0
        elif unit == "µW/cm**2/sr/µm":
            cal_to_mw = 0.001
        else:
            raise ValueError(f"Unrecognized calibrated radiance unit for {suffix}: {unit!r}")
        shape = raw_shape
        raw_cube = np.memmap(ROOT / raw_item["cube_path"], dtype="<u2", mode="r", shape=shape, order="C")
        cal_cube = np.memmap(ROOT / cal_item["cube_path"], dtype="<f4", mode="r", shape=shape, order="C")
        scene_rows = []
        pixel_count = shape[1] * shape[2]

        for band in range(1, 257):
            if not valid[band]:
                continue
            raw_plane = raw_cube[band - 1]
            cal_plane = cal_cube[band - 1]
            finite = np.isfinite(cal_plane)
            positive = finite & (cal_plane > 0)
            raw_limit = dynamic_range[band - 1]
            sat_value = saturation[band - 1]
            raw_hits = raw_plane >= raw_limit
            cal_mw = cal_plane.astype(np.float64) * cal_to_mw
            # Candidate comparisons: table units as labeled (uW) and numeric
            # table values counterfactually read as mW.
            sat_declared_hits = finite & (cal_plane > 0) & (cal_mw >= sat_value * 0.001)
            sat_numeric_mw_hits = finite & (cal_plane > 0) & (cal_mw >= sat_value)

            # Fixed-grid samples match the earlier project audit convention.
            sampled_raw = raw_plane[::32, ::5].astype(np.float64)
            sampled_cal = cal_mw[::32, ::5]
            predicted_lut = (sampled_raw * lut[band - 1, ::5, 0][None, :]
                             + lut[band - 1, ::5, 1][None, :])
            comparable = (np.isfinite(sampled_cal) & np.isfinite(predicted_lut)
                          & (sampled_cal > 0) & (predicted_lut > 0))
            if comparable.any():
                ratio = sampled_cal[comparable] / predicted_lut[comparable]
                median_ratio = float(np.median(ratio))
                median_abs_ratio_error = float(np.median(np.abs(ratio - 1.0)))
                correlation = float(np.corrcoef(sampled_cal[comparable], predicted_lut[comparable])[0, 1])
                sample_n = int(comparable.sum())
            else:
                median_ratio = median_abs_ratio_error = correlation = math.nan
                sample_n = 0

            row = {
                "scene": suffix,
                "raw_product_id": raw_item["product_id"],
                "calibrated_product_id": cal_item["product_id"],
                "band_number": band,
                "wavelength_nm": centers[band],
                "valid_band": 1,
                "cube_unit": unit,
                "cube_to_mW_scale": cal_to_mw,
                "total_spatial_pixels": pixel_count,
                "finite_calibrated_pixels": int(finite.sum()),
                "zero_calibrated_pixels": int((finite & (cal_plane == 0)).sum()),
                "negative_calibrated_pixels": int((finite & (cal_plane < 0)).sum()),
                "raw_count_min": int(raw_plane.min()),
                "raw_count_max": int(raw_plane.max()),
                "dynamic_range_count_threshold": raw_limit,
                "raw_at_or_above_dynamic_range_count": int(raw_hits.sum()),
                "raw_at_or_above_dynamic_range_fraction": float(raw_hits.mean()),
                "saturation_value": sat_value,
                "saturation_xml_unit": sat_unit,
                "calibrated_at_or_above_xml_uW_threshold_count": int(sat_declared_hits.sum()),
                "calibrated_at_or_above_xml_uW_threshold_fraction": float(sat_declared_hits.mean()),
                "calibrated_at_or_above_numeric_mW_threshold_count": int(sat_numeric_mw_hits.sum()),
                "calibrated_at_or_above_numeric_mW_threshold_fraction": float(sat_numeric_mw_hits.mean()),
                "sampled_lut_points": sample_n,
                "sampled_median_level1_over_lut_stage_ratio": median_ratio,
                "sampled_median_absolute_ratio_error": median_abs_ratio_error,
                "sampled_level1_lut_stage_correlation": correlation,
            }
            rows.append(row)
            scene_rows.append(row)

        finite_total = sum(r["finite_calibrated_pixels"] for r in scene_rows)
        denom = sum(r["total_spatial_pixels"] for r in scene_rows)
        scene_summaries[suffix] = {
            "raw_product_id": raw_item["product_id"],
            "calibrated_product_id": cal_item["product_id"],
            "raw_archive_sha256": raw_item["zip_sha256"],
            "calibrated_archive_sha256": cal_item["zip_sha256"],
            "raw_cube_md5": raw_item["computed_qub_md5"],
            "calibrated_cube_md5": cal_item["computed_qub_md5"],
            "cube_unit": unit,
            "dimensions_bands_lines_samples": list(shape),
            "valid_band_count": len(scene_rows),
            "finite_calibrated_fraction_over_valid_bands": finite_total / denom,
            "zero_calibrated_band_pixels": sum(r["zero_calibrated_pixels"] for r in scene_rows),
            "negative_calibrated_band_pixels": sum(r["negative_calibrated_pixels"] for r in scene_rows),
            "maximum_raw_count_on_valid_bands": max(r["raw_count_max"] for r in scene_rows),
            "raw_dynamic_range_hits_over_valid_band_pixels": sum(r["raw_at_or_above_dynamic_range_count"] for r in scene_rows),
            "raw_dynamic_range_fraction_over_valid_band_pixels": sum(r["raw_at_or_above_dynamic_range_count"] for r in scene_rows) / denom,
            "declared_uW_saturation_candidate_hits": sum(r["calibrated_at_or_above_xml_uW_threshold_count"] for r in scene_rows),
            "declared_uW_saturation_candidate_fraction": sum(r["calibrated_at_or_above_xml_uW_threshold_count"] for r in scene_rows) / denom,
            "numeric_mW_saturation_candidate_hits": sum(r["calibrated_at_or_above_numeric_mW_threshold_count"] for r in scene_rows),
            "numeric_mW_saturation_candidate_fraction": sum(r["calibrated_at_or_above_numeric_mW_threshold_count"] for r in scene_rows) / denom,
            "median_of_per_band_sampled_level1_over_lut_stage_ratios": float(np.nanmedian([r["sampled_median_level1_over_lut_stage_ratio"] for r in scene_rows])),
            "per_band_sampled_level1_over_lut_stage_ratio_min": float(np.nanmin([r["sampled_median_level1_over_lut_stage_ratio"] for r in scene_rows])),
            "per_band_sampled_level1_over_lut_stage_ratio_max": float(np.nanmax([r["sampled_median_level1_over_lut_stage_ratio"] for r in scene_rows])),
            "median_of_per_band_sampled_level1_lut_stage_correlations": float(np.nanmedian([r["sampled_level1_lut_stage_correlation"] for r in scene_rows])),
        }
        plot_data[suffix] = scene_rows
        del raw_cube, cal_cube

    with CSV_OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "status": "exploratory paired-product QA; no mask assigned",
        "data_version": "2020-02-08 paired E3G2 products; identities, archive hashes, and embedded QUB MD5 values from current M1 inventory",
        "method": "Full-cube exact counts by valid band for finite/zero/negative calibrated values and raw Dynamic_Range exceedances; two candidate saturation comparisons; fixed-grid raw/LUT-stage/Level-1 comparison every 32nd line and every fifth sample. Appendix F defines the LUT output as an intermediate radiance stage; later destriping and post-processing are omitted here.",
        "split": "Not applicable: single-scene product QA, not model evaluation.",
        "units": {"lut": "mW/cm**2/sr/µm", "saturation_xml": sat_unit,
                  "calibrated_products": {k: products["calibrated"][k]["data_unit"] for k in ("m65", "d18")}},
        "scene_summaries": scene_summaries,
        "limits": [
            "Saturation and Dynamic_Range comparisons are candidate flags, not validated detector masks.",
            "The XML-declared and counterfactual numeric-mW thresholds are both diagnostic scenarios.",
            "The LUT-stage to Level-1 comparison omits documented destriping and radiance post-processing and is not a complete reconstruction or independent calibration validation.",
            "Finite, zero, and negative values are not assigned fill or validity meanings here.",
            "No reflectance, thermal correction, or scientific retrieval was computed.",
        ],
    }
    JSON_OUT.write_text(json.dumps(summary, indent=2) + "\n")

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.5), sharex=True, constrained_layout=True)
    colors = {"m65": "#245a83", "d18": "#b35425"}
    for scene, group in plot_data.items():
        x = [r["band_number"] for r in group]
        axes[0, 0].plot(x, [r["raw_at_or_above_dynamic_range_fraction"] for r in group],
                        marker=".", ms=3, lw=1, color=colors[scene], label=scene)
        axes[0, 1].plot(x, [r["calibrated_at_or_above_xml_uW_threshold_fraction"] for r in group],
                        marker=".", ms=3, lw=1, color=colors[scene], label=f"{scene}, XML µW")
        axes[0, 1].plot(x, [r["calibrated_at_or_above_numeric_mW_threshold_fraction"] for r in group],
                        marker=".", ms=3, lw=1, ls="--", color=colors[scene], label=f"{scene}, numeric mW")
        axes[1, 0].plot(x, [r["sampled_median_level1_over_lut_stage_ratio"] for r in group],
                        marker=".", ms=3, lw=1, color=colors[scene], label=scene)
        axes[1, 1].plot(x, [r["sampled_level1_lut_stage_correlation"] for r in group],
                        marker=".", ms=3, lw=1, color=colors[scene], label=scene)
    axes[0, 0].set_title("Raw count ≥ Dynamic_Range")
    axes[0, 0].set_ylabel("Fraction of spatial pixels")
    axes[0, 1].set_title("Calibrated radiance ≥ candidate saturation threshold")
    axes[0, 1].set_ylabel("Fraction of spatial pixels")
    axes[1, 0].axhline(1, color="#444", linestyle=":", linewidth=1)
    axes[1, 0].set_yscale("log")
    axes[1, 0].set_title("Level-1 / LUT-stage radiance (later steps omitted)")
    axes[1, 0].set_ylabel("Ratio")
    axes[1, 1].set_ylim(-1.05, 1.05)
    axes[1, 1].set_title("Level-1 / LUT-stage correlation")
    axes[1, 1].set_ylabel("Pearson r")
    for ax in axes.flat:
        ax.grid(True, alpha=.22)
        ax.legend(fontsize=8)
        ax.set_xlabel("E3G2-valid band number")
    fig.suptitle("2020 E3G2 paired raw–LUT-stage–Level-1 diagnostic", fontsize=14)
    fig.savefig(FIG_OUT, dpi=170)
    plt.close(fig)
    print(json.dumps({"summary": summary, "csv": str(CSV_OUT.relative_to(ROOT)),
                      "figure": str(FIG_OUT.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
