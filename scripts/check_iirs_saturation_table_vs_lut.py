#!/usr/bin/env python3
"""Check whether E1G2 saturation table values align with LUT output at Dynamic_Range.

This is an internal metadata consistency diagnostic. It does not establish the
official units or define a pixel mask.
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
ARCHIVE = ROOT / "data/pradan/iir.zip"
VALIDITY = ROOT / "results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv"
MODES = {
    "E1G2": ("E1G2_valid", "e1g2", True),  # saturation rows are numbered 1..256
    "E3G2": ("E3G2_valid", "e3g2", False),  # saturation rows are numbered 0..255
}
OUT = ROOT / "results/phase-1/m1-saturation-sample"
CSV_OUT = OUT / "metrics/iirs_saturation_lut_table_check_by_mode.csv"
JSON_OUT = OUT / "metrics/iirs_saturation_lut_table_check_summary.json"
FIG_OUT = OUT / "figures/iirs_saturation_lut_table_check.png"


def descendants(node, name):
    return [element for element in node.iter() if element.tag.split("}")[-1] == name]


def main():
    (OUT / "metrics").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    valid = {mode: {} for mode in MODES}
    with VALIDITY.open(newline="") as handle:
        for row in csv.DictReader(handle):
            band = int(row["band_number"])
            for mode, (validity_column, _, _) in MODES.items():
                valid[mode][band] = row[validity_column] == "1"

    rows = []
    mode_stats = {}
    with ZipFile(ARCHIVE) as archive:
        for mode, (validity_column, tag, one_based_table_bands) in MODES.items():
            sat_csv = f"iir/calibration/ch2_iirs_cal_{tag}_saturations_radiance.csv"
            sat_xml = f"iir/calibration/ch2_iirs_cal_{tag}_saturations_radiance.xml"
            lut_csv = f"iir/calibration/ch2_iirs_cal_{tag}_lut_coeff.csv"
            sat_rows = list(csv.reader(io.StringIO(archive.read(sat_csv).decode("utf-8"))))
            sat_label = ET.fromstring(archive.read(sat_xml))
            sat_units = [e.text.strip() for e in descendants(sat_label, "unit") if e.text]
            sat_unit = sat_units[0] if sat_units else ""
            lut_rows = [tuple(map(float, row)) for row in csv.reader(
                io.StringIO(archive.read(lut_csv).decode("utf-8")))]
            lut = np.asarray(lut_rows, dtype=np.float64).reshape(256, 250, 2)
            mode_rows = []
            for source_row in sat_rows:
                table_band = int(source_row[0])
                band = table_band if one_based_table_bands else table_band + 1
                if band < 1 or band > 256 or not valid[mode][band]:
                    continue
                threshold, dynamic_range = float(source_row[1]), float(source_row[2])
                lut_band_index = band - 1
                predicted_mw = (dynamic_range * lut[lut_band_index, :, 0]
                                + lut[lut_band_index, :, 1])
                predicted_median = float(np.median(predicted_mw))
                ratio_if_sat_mw = predicted_median / threshold
                row = {
                    "mode": mode,
                    "band_number": band,
                    "saturation_source_row_band_number": table_band,
                    "saturation_table_value": threshold,
                    "saturation_xml_unit": sat_unit,
                    "dynamic_range_count": dynamic_range,
                    "lut_prediction_at_dynamic_range_median_mW_cm2_sr_um": predicted_median,
                    "lut_mW_over_saturation_numeric_counterfactual_mW": ratio_if_sat_mw,
                    "lut_mW_over_saturation_declared_uW_converted_to_mW": ratio_if_sat_mw * 1000.0,
                    "lut_sample_entry_count": int(predicted_mw.size),
                }
                rows.append(row)
                mode_rows.append(row)
            values = np.asarray([r["lut_mW_over_saturation_numeric_counterfactual_mW"]
                                 for r in mode_rows])
            mode_stats[mode] = {
                "saturation_xml_unit": sat_unit,
                "valid_band_count": len(mode_rows),
                "lut_sample_entries": sum(r["lut_sample_entry_count"] for r in mode_rows),
                "ratio_lut_mW_over_saturation_numeric_if_mW": {
                    "median": float(np.median(values)),
                    "q10": float(np.quantile(values, .1)),
                    "q90": float(np.quantile(values, .9)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                },
                "ratio_if_xml_declared_uW_converted_to_mW_median": float(np.median(values) * 1000),
            }

    with CSV_OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    stats = {
        "status": "exploratory internal table check; no mask assigned",
        "method": "For each mode-valid band in E1G2 and E3G2, apply every sample-column LUT gain/offset to that band's Dynamic_Range count. Compare the median predicted LUT radiance (mW) with the Saturation table number, then show both counterfactual numeric-mW and XML-declared-uW conversions.",
        "modes": mode_stats,
        "lut_output_unit_per_sis": "mW/cm**2/sr/um",
        "interpretation": "The E1G2 raw numeric table values are closer in scale to LUT predictions if treated as mW than if treated as XML-declared uW. E3G2 has a very different relation. This mode dependence argues against using a single inferred unit correction.",
        "limits": [
            "The SIS describes LUT output in mW; saturation XML declares uW.",
            "The comparison is an internal table consistency check, not a validation source.",
            "Dynamic_Range may have operational meaning beyond a simple LUT input count.",
            "No pixel-level mask or Level-1 interpretation follows from this ratio.",
        ],
    }
    JSON_OUT.write_text(json.dumps(stats, indent=2) + "\n")

    fig, ax = plt.subplots(figsize=(10, 5.4), constrained_layout=True)
    for mode in MODES:
        group = [row for row in rows if row["mode"] == mode]
        ax.plot([row["band_number"] for row in group],
                [row["lut_mW_over_saturation_numeric_counterfactual_mW"] for row in group],
                marker=".", linewidth=1.1, label=f"{mode}, saturation number treated as mW")
    ax.axhline(1, color="#333333", linestyle="--", linewidth=1, label="Ratio = 1")
    ax.set_yscale("log")
    ax.set_xlabel("Mode-valid band number")
    ax.set_ylabel("Median LUT prediction at Dynamic_Range / saturation value")
    ax.set_title("Internal saturation table and LUT scale check by mode")
    ax.grid(True, which="both", alpha=.25)
    ax.legend(fontsize=8)
    fig.savefig(FIG_OUT, dpi=170)
    plt.close(fig)
    print(json.dumps({"summary": stats, "csv": str(CSV_OUT.relative_to(ROOT)),
                      "figure": str(FIG_OUT.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
