#!/usr/bin/env python3
"""Run a small, fixed-grid diagnostic for E1G2 saturation fields.

Run from the repository root with:
  uv run --no-project --with numpy --with matplotlib python scripts/probe_iirs_saturation_sample.py

Samples 16 scan lines spread across the scene and all 250 samples on each line.
It compares candidate table flags and raw-to-LUT radiance behavior. The output
does not define or apply a pixel mask.
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
PAIR = ROOT / "data/pradan/e1g2_candidate_20260227T1239538758"
CAL_ZIP = PAIR / "ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
RAW_ZIP = PAIR / "ch2_iir_nri_20260227T1239538758_d_img_d18.zip"
OFFICIAL_ZIP = ROOT / "data/pradan/iir.zip"
CAL_PART = "data/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.qub"
RAW_PART = "data/raw/20260227/ch2_iir_nri_20260227T1239538758_d_img_d18.qub"
SAT_CSV = "iir/calibration/ch2_iirs_cal_e1g2_saturations_radiance.csv"
SAT_XML = "iir/calibration/ch2_iirs_cal_e1g2_saturations_radiance.xml"
LUT_CSV = "iir/calibration/ch2_iirs_cal_e1g2_lut_coeff.csv"
VALID_CSV = ROOT / "results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv"
OUT = ROOT / "results/phase-1/m1-saturation-sample"


def descendants(node, name):
    return [element for element in node.iter() if element.tag.split("}")[-1] == name]


def text(node, name):
    found = descendants(node, name)
    return found[0].text.strip() if found and found[0].text else ""


def main():
    (OUT / "metrics").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    with ZipFile(CAL_ZIP) as cal_zip, ZipFile(RAW_ZIP) as raw_zip, ZipFile(OFFICIAL_ZIP) as official:
        label = ET.fromstring(cal_zip.read("data/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.xml"))
        axes = {text(axis, "axis_name"): int(text(axis, "elements"))
                for axis in descendants(label, "Axis_Array")}
        bands, lines, samples = axes["BAND"], axes["LINE"], axes["SAMPLE"]
        if (bands, lines, samples) != (256, 12210, 250):
            raise ValueError(f"Unexpected calibrated dimensions: {axes}")
        raw_label = ET.fromstring(raw_zip.read("data/raw/20260227/ch2_iir_nri_20260227T1239538758_d_img_d18.xml"))
        if text(raw_label, "data_type") != "UnsignedLSB2" or text(label, "data_type") != "IEEE754LSBSingle":
            raise ValueError("Unexpected paired raw or calibrated data type")
        unit = text(label, "unit")

        valid = {}
        with VALID_CSV.open(newline="") as handle:
            for row in csv.DictReader(handle):
                valid[int(row["band_number"])] = row["E1G2_valid"] == "1"
        sat_rows = list(csv.reader(io.StringIO(official.read(SAT_CSV).decode("utf-8"))))
        saturation = {int(row[0]): float(row[1]) for row in sat_rows if len(row) >= 3}
        dynamic_range = {int(row[0]): float(row[2]) for row in sat_rows if len(row) >= 3}
        sat_label = ET.fromstring(official.read(SAT_XML))
        sat_unit = text(sat_label, "unit")
        lut_rows = [tuple(map(float, row)) for row in csv.reader(
            io.StringIO(official.read(LUT_CSV).decode("utf-8")))]
        lut = np.asarray(lut_rows, dtype=np.float64).reshape(bands, samples, 2)

        # 0-based scan-line indices are fixed and span the full observation.
        sampled_lines = np.linspace(0, lines - 1, 16, dtype=int)
        sampled_line_set = set(sampled_lines.tolist())
        plane_bytes = lines * samples * 4
        raw_plane_bytes = lines * samples * 2
        rows = []
        with cal_zip.open(CAL_PART) as cal_stream, raw_zip.open(RAW_PART) as raw_stream:
            for band in range(1, bands + 1):
                cal_bytes = cal_stream.read(plane_bytes)
                raw_bytes = raw_stream.read(raw_plane_bytes)
                if len(cal_bytes) != plane_bytes or len(raw_bytes) != raw_plane_bytes:
                    raise IOError(f"Short QUB plane at band {band}")
                if not valid[band]:
                    continue
                cal_plane = np.frombuffer(cal_bytes, dtype="<f4").reshape(lines, samples)
                raw_plane = np.frombuffer(raw_bytes, dtype="<u2").reshape(lines, samples)
                cal = cal_plane[sampled_lines, :].astype(np.float64)
                counts = raw_plane[sampled_lines, :].astype(np.float64)
                finite = np.isfinite(cal)
                sat_flag = finite & (cal >= saturation[band])
                range_flag = counts >= dynamic_range[band]
                predicted_mw = (counts * lut[band - 1, :, 0][None, :]
                                + lut[band - 1, :, 1][None, :])
                cal_mw = cal / 1000.0
                comparable = finite & np.isfinite(predicted_mw) & (cal_mw > 0) & (predicted_mw > 0)
                ratios = cal_mw[comparable] / predicted_mw[comparable]
                rows.append({
                    "band_number": band,
                    "sampled_band_pixels": int(cal.size),
                    "nonfinite_radiance": int((~finite).sum()),
                    "zero_radiance": int((finite & (cal == 0)).sum()),
                    "negative_radiance": int((finite & (cal < 0)).sum()),
                    "radiance_at_or_above_csv_xml_saturation": int(sat_flag.sum()),
                    "radiance_saturation_candidate_fraction": float(sat_flag.mean()),
                    "raw_count_at_or_above_dynamic_range": int(range_flag.sum()),
                    "raw_dynamic_range_candidate_fraction": float(range_flag.mean()),
                    "both_candidates_flagged": int((sat_flag & range_flag).sum()),
                    "sampled_raw_count_min": int(counts.min()),
                    "sampled_raw_count_max": int(counts.max()),
                    "sampled_calibrated_radiance_median_uW_cm2_sr_um": float(np.median(cal[finite])) if finite.any() else float("nan"),
                    "sampled_lut_ratio_median_calibrated_over_predicted": float(np.median(ratios)) if ratios.size else float("nan"),
                    "lut_comparable_pixel_count": int(ratios.size),
                })

    csv_path = OUT / "metrics/e1g2_saturation_sample_by_band.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    valid_pixels = sum(row["sampled_band_pixels"] for row in rows)
    sat_hits = sum(row["radiance_at_or_above_csv_xml_saturation"] for row in rows)
    raw_hits = sum(row["raw_count_at_or_above_dynamic_range"] for row in rows)
    overlap = sum(row["both_candidates_flagged"] for row in rows)
    ratios = [row["sampled_lut_ratio_median_calibrated_over_predicted"]
              for row in rows if np.isfinite(row["sampled_lut_ratio_median_calibrated_over_predicted"])]
    summary = {
        "status": "exploratory sample; no mask assigned",
        "sample_design": {
            "line_index_base": 0,
            "line_indices": sampled_lines.tolist(),
            "samples_per_line": samples,
            "valid_band_count": len(rows),
            "valid_band_pixel_observations": valid_pixels,
        },
        "units": {"calibrated_cube": unit, "saturation_table_xml": sat_unit},
        "candidate_counts": {
            "radiance_at_or_above_saturation": sat_hits,
            "raw_count_at_or_above_dynamic_range": raw_hits,
            "both_candidates_flagged": overlap,
            "sampled_valid_band_pixels": valid_pixels,
        },
        "candidate_fractions": {
            "radiance_saturation": sat_hits / valid_pixels,
            "raw_dynamic_range": raw_hits / valid_pixels,
        },
        "median_per_band_lut_ratio_median": float(np.median(ratios)),
        "source_pair": {
            "calibrated_zip": str(CAL_ZIP.relative_to(ROOT)),
            "raw_zip": str(RAW_ZIP.relative_to(ROOT)),
            "official_archive": str(OFFICIAL_ZIP.relative_to(ROOT)),
        },
        "limits": [
            "This deterministic sample is not a random or independent sample.",
            "Threshold flags are diagnostic candidates, not verified saturation labels.",
            "Finite values or zero values are not classified as valid or fill from this test.",
            "Agreement with the LUT is internal consistency, not independent calibration validation.",
        ],
    }
    json_path = OUT / "metrics/e1g2_saturation_sample_summary.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n")

    bands_x = np.array([row["band_number"] for row in rows])
    fig, ax = plt.subplots(figsize=(10, 5.4), constrained_layout=True)
    ax.plot(bands_x, [row["radiance_saturation_candidate_fraction"] for row in rows],
            marker=".", linewidth=1.2, label="Calibrated radiance ≥ saturation field")
    ax.plot(bands_x, [row["raw_dynamic_range_candidate_fraction"] for row in rows],
            marker=".", linewidth=1.2, label="Raw count ≥ Dynamic_Range field")
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("E1G2-valid band number")
    ax.set_ylabel("Fraction of sampled pixels flagged")
    ax.set_title("Fixed-line E1G2 sample: candidate table flags")
    ax.grid(True, alpha=.25)
    ax.legend()
    fig.savefig(OUT / "figures/e1g2_saturation_sample_flags.png", dpi=170)
    plt.close(fig)
    print(json.dumps({"summary": summary, "csv": str(csv_path.relative_to(ROOT)),
                      "figure": "results/phase-1/m1-saturation-sample/figures/e1g2_saturation_sample_flags.png"}, indent=2))


if __name__ == "__main__":
    main()
