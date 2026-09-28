#!/usr/bin/env python3
"""Audit E1G2 calibrated radiance values and coarse PDS geometry.

Run from the repository root:
  uv run --no-project --with numpy --with matplotlib python scripts/analyze_iirs_e1g2_scene.py

The script streams the compressed QUB by BSQ band from the immutable PRADAN ZIP.
Counts are exact over the cube. Quantiles use a fixed grid (every 32nd line,
every fifth sample). This is an instrument-data audit, not reflectance processing.
The SIS V17 says the LUT output is in mW and describes a factor of 1000 for
Level 1 archive values. The saturation CSV XML declares µW, so both threshold
readings are retained pending resolution of that metadata conflict.
"""
from __future__ import annotations

import csv
import io
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "data/pradan/e1g2_candidate_20260227T1239538758/ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
RAW_PRODUCT = ROOT / "data/pradan/e1g2_candidate_20260227T1239538758/ch2_iir_nri_20260227T1239538758_d_img_d18.zip"
OFFICIAL = ROOT / "data/pradan/iir.zip"
RESULTS = ROOT / "results/phase-1/m1-e1g2-scene"
CSV_OUT = RESULTS / "metrics/e1g2_radiance_by_band.csv"
FIG_OUT = RESULTS / "figures/e1g2_radiance_and_footprint.png"
VALIDITY = ROOT / "results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv"
SAT_CSV = "iir/calibration/ch2_iirs_cal_e1g2_saturations_radiance.csv"
SAT_XML = "iir/calibration/ch2_iirs_cal_e1g2_saturations_radiance.xml"
LUT_CSV = "iir/calibration/ch2_iirs_cal_e1g2_lut_coeff.csv"
LUT_XML = "iir/calibration/ch2_iirs_cal_e1g2_lut_coeff.xml"
GEOM_PART = "geometry/calibrated/20260227/ch2_iir_nci_20260227T1239538758_g_grd_d18.csv"
QUB_PART = "data/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.qub"
RAW_QUB_PART = "data/raw/20260227/ch2_iir_nri_20260227T1239538758_d_img_d18.qub"
RAW_LABEL_PART = "data/raw/20260227/ch2_iir_nri_20260227T1239538758_d_img_d18.xml"
LABEL_PART = "data/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.xml"


def descendants(root, name):
    return [e for e in root.iter() if e.tag.split("}")[-1] == name]


def first_text(root, name):
    found = descendants(root, name)
    return found[0].text.strip() if found and found[0].text else ""


def main():
    RESULTS.joinpath("metrics").mkdir(parents=True, exist_ok=True)
    RESULTS.joinpath("figures").mkdir(parents=True, exist_ok=True)
    with ZipFile(PRODUCT) as product, ZipFile(RAW_PRODUCT) as raw_product, ZipFile(OFFICIAL) as archive:
        label = ET.fromstring(product.read(LABEL_PART))
        axes = {first_text(a, "axis_name"): int(first_text(a, "elements"))
                for a in descendants(label, "Axis_Array")}
        bands, lines, samples = axes["BAND"], axes["LINE"], axes["SAMPLE"]
        assert (bands, lines, samples) == (256, 12210, 250), axes
        assert first_text(label, "data_type") == "IEEE754LSBSingle"
        raw_label = ET.fromstring(raw_product.read(RAW_LABEL_PART))
        assert first_text(raw_label, "data_type") == "UnsignedLSB2"
        raw_axes = {first_text(a, "axis_name"): int(first_text(a, "elements"))
                    for a in descendants(raw_label, "Axis_Array")}
        assert raw_axes == axes, (raw_axes, axes)
        unit = first_text(label, "unit")
        assert unit == "µW/cm**2/sr/µm", unit
        centers = [float(e.text) for e in descendants(label, "center_wavelength")]
        assert len(centers) == bands

        validity = {}
        with VALIDITY.open(newline="") as f:
            for row in csv.DictReader(f):
                validity[int(row["band_number"])] = row["E1G2_valid"] == "1"
        assert len(validity) == bands
        sat, dynamic_range = {}, {}
        sat_rows = list(csv.reader(io.StringIO(archive.read(SAT_CSV).decode("utf-8"))))
        for row in sat_rows:
            if len(row) >= 2:
                sat[int(row[0])] = float(row[1])
                dynamic_range[int(row[0])] = float(row[2])
        sat_label = ET.fromstring(archive.read(SAT_XML))
        sat_unit = first_text(sat_label, "unit")
        assert sat_unit == unit, (sat_unit, unit)
        assert len(sat) == bands and len(dynamic_range) == bands
        lut_label = ET.fromstring(archive.read(LUT_XML))
        lut_records = int(first_text(lut_label, "records"))
        assert lut_records == bands * samples, lut_records
        lut_rows = [tuple(map(float, row)) for row in csv.reader(
            io.StringIO(archive.read(LUT_CSV).decode("utf-8")))]
        assert len(lut_rows) == lut_records and all(len(row) == 2 for row in lut_rows)
        # The 64,000-row official LUT is stored band-major with 250 sample entries per band.
        lut = np.asarray(lut_rows, dtype=np.float64).reshape(bands, samples, 2)
        lut_gain, lut_offset = lut[:, :, 0], lut[:, :, 1]

        # Labels declare BSQ: BAND, LINE, SAMPLE, with sample fastest.
        plane_bytes = lines * samples * 4
        rows = []
        with product.open(QUB_PART) as stream, raw_product.open(RAW_QUB_PART) as raw_stream:
            for b in range(1, bands + 1):
                raw = stream.read(plane_bytes)
                if len(raw) != plane_bytes:
                    raise IOError(f"short QUB plane at band {b}")
                plane = np.frombuffer(raw, dtype="<f4").reshape(lines, samples)
                raw_bytes = raw_stream.read(lines * samples * 2)
                if len(raw_bytes) != lines * samples * 2:
                    raise IOError(f"short raw QUB plane at band {b}")
                raw_plane = np.frombuffer(raw_bytes, dtype="<u2").reshape(lines, samples)
                finite = np.isfinite(plane)
                positive = finite & (plane > 0)
                zeros = finite & (plane == 0)
                negative = finite & (plane < 0)
                threshold = sat[b]
                at_sat = finite & (plane >= threshold)
                threshold_if_sis_mw_uW = threshold * 1000.0
                at_sat_if_sis_mw = finite & (plane >= threshold_if_sis_mw_uW)
                # Fixed sample grid for distribution summaries only.
                qsample = plane[::32, ::5].ravel()
                qsample = qsample[np.isfinite(qsample) & (qsample > 0)]
                q = np.quantile(qsample, [0.01, 0.50, 0.99]) if qsample.size else [math.nan] * 3
                sampled_raw = raw_plane[::32, ::5].astype(np.float64)
                sampled_cal_mw = plane[::32, ::5].astype(np.float64) / 1000.0
                predicted_lut_mw = (sampled_raw * lut_gain[b - 1, ::5][None, :]
                                    + lut_offset[b - 1, ::5][None, :])
                lut_ok = (np.isfinite(sampled_cal_mw) & np.isfinite(predicted_lut_mw)
                          & (sampled_cal_mw > 0) & (predicted_lut_mw > 0))
                if lut_ok.any():
                    ratio_values = sampled_cal_mw[lut_ok] / predicted_lut_mw[lut_ok]
                    lut_ratio = float(np.median(ratio_values))
                    lut_mape = float(np.median(np.abs(ratio_values - 1.0)))
                    lut_corr = float(np.corrcoef(sampled_cal_mw[lut_ok], predicted_lut_mw[lut_ok])[0, 1])
                    lut_n = int(lut_ok.sum())
                else:
                    lut_ratio, lut_mape, lut_corr, lut_n = math.nan, math.nan, math.nan, 0
                rows.append({
                    "band_number": b,
                    "wavelength_nm": centers[b - 1],
                    "mode_valid": int(validity[b]),
                    "finite_count": int(finite.sum()),
                    "zero_count": int(zeros.sum()),
                    "negative_count": int(negative.sum()),
                    "positive_count": int(positive.sum()),
                    "sampled_positive_q01_uW_cm2_sr_um": float(q[0]),
                    "sampled_positive_median_uW_cm2_sr_um": float(q[1]),
                    "sampled_positive_q99_uW_cm2_sr_um": float(q[2]),
                    "saturation_threshold_as_csv_xml_uW_cm2_sr_um": threshold,
                    "count_at_or_above_threshold": int(at_sat.sum()) if validity[b] else "",
                    "fraction_at_or_above_threshold": float(at_sat.mean()) if validity[b] else "",
                    "saturation_threshold_if_sis_mW_converted_to_uW": threshold_if_sis_mw_uW,
                    "count_at_or_above_threshold_if_sis_mW": int(at_sat_if_sis_mw.sum()) if validity[b] else "",
                    "fraction_at_or_above_threshold_if_sis_mW": float(at_sat_if_sis_mw.mean()) if validity[b] else "",
                    "official_dynamic_range_count_threshold": dynamic_range[b],
                    "raw_count_at_or_above_dynamic_range": int((raw_plane >= dynamic_range[b]).sum()) if validity[b] else "",
                    "raw_fraction_at_or_above_dynamic_range": float((raw_plane >= dynamic_range[b]).mean()) if validity[b] else "",
                    "fixed_grid_lut_points": lut_n,
                    "fixed_grid_median_calibrated_over_lut_radiance": lut_ratio,
                    "fixed_grid_median_absolute_ratio_error": lut_mape,
                    "fixed_grid_calibrated_lut_correlation": lut_corr,
                })
                del plane, raw_plane

        with CSV_OUT.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

        # Geometry file is the official sparse grid, not a pixel-level map.
        geom_text = product.read(GEOM_PART).decode("utf-8")
        geom = list(csv.DictReader(io.StringIO(geom_text)))
        lon = np.array([float(r["Longitude"]) for r in geom])
        lat = np.array([float(r["Latitude"]) for r in geom])
        scan = np.array([int(r["Scan"]) for r in geom])
        pixel = np.array([int(r["Pixel"]) for r in geom])
        # Unwrap near 0° so the dateline-crossing convention is readable.
        lon_plot = np.where(lon > 180, lon - 360, lon)
        lat_span = (float(lat.min()), float(lat.max()))
        lon_span = (float(lon_plot.min()), float(lon_plot.max()))
        scan_lines = sorted(set(scan.tolist()))
        assert len(geom) == 1476

    fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(17.2, 5.4), constrained_layout=True)
    valid_rows = [r for r in rows if r["mode_valid"]]
    ax0.plot([r["wavelength_nm"] for r in valid_rows],
             [r["sampled_positive_median_uW_cm2_sr_um"] for r in valid_rows],
             color="#245a83", marker=".", linewidth=1, label="Calibrated sampled median")
    ax0.plot([r["wavelength_nm"] for r in valid_rows],
             [r["saturation_threshold_as_csv_xml_uW_cm2_sr_um"] for r in valid_rows],
             color="#b23b32", linestyle="--", linewidth=1.2, label="CSV XML unit: µW")
    ax0.plot([r["wavelength_nm"] for r in valid_rows],
             [r["saturation_threshold_if_sis_mW_converted_to_uW"] for r in valid_rows],
             color="#4f8a55", linestyle=":", linewidth=1.2, label="SIS LUT unit: mW × 1000")
    ax0.set_yscale("log")
    ax0.set_xlabel("Wavelength (nm)")
    ax0.set_ylabel("Sampled positive median (µW cm⁻² sr⁻¹ µm⁻¹)")
    ax0.set_title("E1G2 radiance and saturation readings")
    ax0.grid(True, which="both", alpha=.25)
    ax0.legend(fontsize=8)
    ax1.plot([r["wavelength_nm"] for r in valid_rows],
             [r["fixed_grid_median_calibrated_over_lut_radiance"] for r in valid_rows],
             color="#245a83", marker=".", linewidth=1)
    ax1.axhline(1.0, color="#555555", linestyle="--", linewidth=1)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("Median calibrated / LUT-predicted radiance")
    ax1.set_title("Internal LUT consistency (fixed sample grid)")
    ax1.grid(True, alpha=.25)
    sc = ax2.scatter(lon_plot, lat, c=scan, s=8, cmap="viridis", linewidths=0)
    ax2.set_xlabel("Longitude (degrees, wrapped to −180…180)")
    ax2.set_ylabel("Latitude (degrees)")
    ax2.set_title("Official sparse geometry grid (color = scan line)")
    ax2.set_aspect("equal", adjustable="datalim")
    ax2.grid(True, alpha=.25)
    fig.colorbar(sc, ax=ax2, label="Scan line")
    fig.suptitle("2026-02-27 E1G2: radiance and geolocation audit", fontsize=14)
    fig.savefig(FIG_OUT, dpi=170)
    plt.close(fig)

    valid = [r for r in rows if r["mode_valid"]]
    hit = sum(int(r["count_at_or_above_threshold"]) for r in valid)
    total = sum(r["finite_count"] for r in valid)
    hit_if_sis_mw = sum(int(r["count_at_or_above_threshold_if_sis_mW"]) for r in valid)
    raw_hit = sum(int(r["raw_count_at_or_above_dynamic_range"]) for r in valid)
    print(f"shape bands,lines,samples={bands},{lines},{samples}; unit={unit}; valid bands={len(valid)}")
    print(f"all-cube finite values={sum(r['finite_count'] for r in rows):,}/{bands*lines*samples:,}; zeros={sum(r['zero_count'] for r in valid):,}; negatives={sum(r['negative_count'] for r in valid):,}")
    print(f"saturation CSV XML unit={sat_unit}; direct-unit candidates={hit:,}/{total:,} ({hit/total:.6%}); if SIS LUT mW values are converted to µW={hit_if_sis_mw:,}/{total:,} ({hit_if_sis_mw/total:.6%})")
    print(f"raw-count values at/above official dynamic-range field on valid bands={raw_hit:,}/{total:,} ({raw_hit/total:.6%})")
    ratios = [r["fixed_grid_median_calibrated_over_lut_radiance"] for r in valid]
    correlations = [r["fixed_grid_calibrated_lut_correlation"] for r in valid]
    print(f"fixed-grid valid-band calibrated/LUT median ratio={np.median(ratios):.6g}; median per-band correlation={np.median(correlations):.6g}")
    print(f"valid-band sampled positive median range={min(r['sampled_positive_median_uW_cm2_sr_um'] for r in valid):.6g}–{max(r['sampled_positive_median_uW_cm2_sr_um'] for r in valid):.6g} µW/cm²/sr/µm")
    print(f"sparse geometry records={len(geom)}; scan lines={len(scan_lines)}; longitude={lon_span}; latitude={lat_span}")
    print(f"outputs: {CSV_OUT.relative_to(ROOT)}, {FIG_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
