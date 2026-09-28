"""Scan the two calibrated IIRS cubes without treating them as reflectance.

Run: uv run --no-project --with numpy --with matplotlib python scripts/analyze_iirs_radiance_pilot.py

The PDS4 axis sequence is BAND, LINE, SAMPLE with Last Index Fastest, so the
on-disk layout is band sequential: (band, line, sample). The scan counts value
classes over every pixel. Quantiles use a fixed grid of every 32nd line and
every 5th sample to limit memory use. Saturation comparisons are hypotheses,
not validated pixel masks.
"""

import csv
import io
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/phase-1/m1-inventory"
OUTPUT_CSV = RESULTS / "metrics/pilot_radiance_quality_by_band.csv"
OUTPUT_FIGURE = RESULTS / "figures/pilot_radiance_quality_by_band.png"
VALIDITY_CSV = RESULTS / "metrics/band_validity_by_mode.csv"
INVENTORY_CSV = RESULTS / "iirs_inventory.csv"
SUPPORT_ZIP = ROOT / "data/pradan/iir.zip"


def label_layout(label_path):
    root = ET.parse(label_path).getroot()
    cube = root.find(".//{*}Array_3D_Spectrum")
    assert cube is not None
    assert cube.find("{*}axis_index_order").text.strip() == "Last Index Fastest"
    axes = sorted(
        (
            int(axis.find("{*}sequence_number").text),
            axis.find("{*}axis_name").text.strip(),
            int(axis.find("{*}elements").text),
        )
        for axis in cube.findall("{*}Axis_Array")
    )
    assert [name for _, name, _ in axes] == ["BAND", "LINE", "SAMPLE"]
    assert cube.find(".//{*}data_type").text.strip() == "IEEE754LSBSingle"
    return tuple(size for _, _, size in axes)


def read_support():
    with zipfile.ZipFile(SUPPORT_ZIP) as archive:
        text = archive.read(
            "iir/calibration/ch2_iirs_cal_e3g2_saturations_radiance.csv"
        ).decode("ascii")
    saturation = np.empty(256, dtype=np.float64)
    for index, value, _dynamic_range in csv.reader(io.StringIO(text)):
        saturation[int(index)] = float(value)
    with VALIDITY_CSV.open(newline="") as handle:
        validity = list(csv.DictReader(handle))
    assert len(validity) == 256
    return saturation, validity


def unit_scale(unit):
    if unit == "mW/cm**2/sr/µm":
        return 1.0
    if unit == "µW/cm**2/sr/µm":
        return 0.001
    raise ValueError(f"unrecognized calibrated radiance unit: {unit!r}")


def scan_scene(scene, saturation, validity):
    suffix = "m65" if "_m65" in scene["product_id"] else "d18"
    cube_path = ROOT / scene["cube_path"]
    shape = label_layout(ROOT / scene["label_path"])
    assert shape == (256, int(scene["line_count"]), int(scene["sample_count"]))
    assert cube_path.stat().st_size == np.prod(shape) * 4
    cube = np.memmap(cube_path, dtype="<f4", mode="r", shape=shape, order="C")
    scale = unit_scale(scene["data_unit"])
    pixel_count = shape[1] * shape[2]
    output = []

    for band in range(256):
        plane = cube[band]
        finite = np.isfinite(plane)
        positive = finite & (plane > 0)
        threshold = saturation[band]
        # The saturation XML says µW; the SIS describes radiance in mW.
        # Compare both readings without accepting either as a pixel mask.
        above_xml = ""
        above_sis = ""
        if threshold > 0:
            above_xml = int(np.count_nonzero(positive & (plane >= threshold * 0.001 / scale)))
            above_sis = int(np.count_nonzero(positive & (plane >= threshold / scale)))

        sample = np.asarray(plane[::32, ::5], dtype=np.float64)
        sample = sample[np.isfinite(sample) & (sample > 0)] * scale
        quantiles = np.quantile(sample, [0.1, 0.5, 0.9]) if len(sample) else [np.nan] * 3
        output.append(
            {
                "scene": suffix,
                "product_id": scene["product_id"],
                "band_number": band + 1,
                "wavelength_nm": validity[band]["wavelength_nm"],
                "e3g2_valid": validity[band]["E3G2_valid"],
                "total_pixels": pixel_count,
                "finite_pixels": int(np.count_nonzero(finite)),
                "nonfinite_pixels": int(pixel_count - np.count_nonzero(finite)),
                "zero_pixels": int(np.count_nonzero(finite & (plane == 0))),
                "negative_pixels": int(np.count_nonzero(finite & (plane < 0))),
                "positive_pixels": int(np.count_nonzero(positive)),
                "at_or_above_xml_unit_threshold_pixels": above_xml,
                "at_or_above_sis_unit_threshold_pixels": above_sis,
                "threshold_numeric_value": threshold,
                "source_cube_unit": scene["data_unit"],
                "sampled_positive_pixels": len(sample),
                "sample_q10_mw_cm2_sr_um": quantiles[0],
                "sample_median_mw_cm2_sr_um": quantiles[1],
                "sample_q90_mw_cm2_sr_um": quantiles[2],
            }
        )
    del cube
    return output


def plot(rows):
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True, layout="constrained")
    colors = {"m65": "#1b6ca8", "d18": "#b35425"}
    for scene in ("m65", "d18"):
        group = [row for row in rows if row["scene"] == scene]
        x = np.array([float(row["wavelength_nm"]) for row in group])
        n = np.array([int(row["total_pixels"]) for row in group])
        valid = np.array([row["e3g2_valid"] == "1" for row in group])
        zero = np.array([int(row["zero_pixels"]) for row in group]) / n
        nonfinite = np.array([int(row["nonfinite_pixels"]) for row in group]) / n
        positive = np.array([int(row["positive_pixels"]) for row in group])
        above_xml = np.array(
            [float(row["at_or_above_xml_unit_threshold_pixels"] or "nan") for row in group]
        )
        above_sis = np.array(
            [float(row["at_or_above_sis_unit_threshold_pixels"] or "nan") for row in group]
        )
        median = np.array([float(row["sample_median_mw_cm2_sr_um"]) for row in group])
        median[~valid] = np.nan
        axes[0].plot(x, zero, label=f"{scene} zero", color=colors[scene])
        axes[0].plot(x, nonfinite, label=f"{scene} nonfinite", color=colors[scene], linestyle=":")
        axes[1].plot(x, np.divide(above_xml, positive, out=np.full(256, np.nan), where=positive > 0),
                     label=f"{scene}, threshold XML µW", color=colors[scene])
        axes[1].plot(x, np.divide(above_sis, positive, out=np.full(256, np.nan), where=positive > 0),
                     label=f"{scene}, threshold SIS mW", color=colors[scene], linestyle="--")
        axes[2].plot(x, median, label=scene, color=colors[scene])

    axes[0].set_ylabel("Fraction of all pixels")
    axes[0].set_title("Exact zero and nonfinite counts; zero is not yet a confirmed fill code")
    axes[1].set_ylabel("Fraction of positive pixels")
    axes[1].set_title("Two readings of E3G2 saturation-table units (candidate thresholds only)")
    axes[2].set_ylabel("Median radiance\n(mW cm⁻² sr⁻¹ µm⁻¹)")
    axes[2].set_xlabel("Band center wavelength (nm)")
    axes[2].set_title("Fixed-grid positive-pixel medians on officially valid E3G2 bands")
    for ax in axes:
        ax.grid(alpha=0.2)
        ax.legend(loc="best", fontsize=8)
    axes[2].set_yscale("log")
    OUTPUT_FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FIGURE, dpi=160)
    plt.close(fig)


def main():
    saturation, validity = read_support()
    with INVENTORY_CSV.open(newline="") as handle:
        scenes = [row for row in csv.DictReader(handle) if row["product_kind"] == "calibrated"]
    assert len(scenes) == 2
    rows = []
    for scene in scenes:
        print("Scanning", scene["product_id"], flush=True)
        rows.extend(scan_scene(scene, saturation, validity))
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    plot(rows)
    print("Saved", OUTPUT_CSV.relative_to(ROOT), OUTPUT_FIGURE.relative_to(ROOT))


if __name__ == "__main__":
    main()
