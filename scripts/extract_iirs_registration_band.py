#!/usr/bin/env python3
"""Extract and display-stretch one IIRS BSQ band for WAC image matching."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import cv2
import numpy as np


DEFAULT_ARCHIVE = Path(
    "data/pradan/e1g2_candidate_20260227T1239538758/"
    "ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
)
DEFAULT_VALIDITY = Path("results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv")
DEFAULT_OUTPUT = Path("data/reference/lroc_wac_e1g2/e1g2_band040_1369nm.png")
DEFAULT_METADATA = Path("data/reference/lroc_wac_e1g2/e1g2_band040_1369nm.json")
LINES, SAMPLES, BANDS = 12210, 250, 256


def find_member(archive: zipfile.ZipFile, suffix: str) -> str:
    matches = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError("Expected one {} entry, found {}".format(suffix, len(matches)))
    return matches[0]


def verify_band_validity(band_number: int, validity_csv: Path):
    with validity_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if int(row["band_number"]) == band_number:
                if row["E1G2_valid"] != "1":
                    raise ValueError("Band {} is not marked valid for E1G2".format(band_number))
                return float(row["wavelength_nm"])
    raise ValueError("Band {} is missing from validity table".format(band_number))


def read_single_band(archive_path: Path, band_number: int):
    if not 1 <= band_number <= BANDS:
        raise ValueError("Band number must be between 1 and {}".format(BANDS))
    plane_size = LINES * SAMPLES * 4
    byte_offset = (band_number - 1) * plane_size
    with zipfile.ZipFile(archive_path) as archive:
        label_root = ElementTree.fromstring(
            archive.read(find_member(archive, "_d_img_d18.xml"))
        )
        data_type = next(
            node.text for node in label_root.iter()
            if node.tag.rsplit("}", 1)[-1] == "data_type"
        )
        if data_type != "IEEE754LSBSingle":
            raise ValueError("Expected IEEE754LSBSingle data, found {}".format(data_type))
        qub = archive.open(find_member(archive, ".qub"))
        remaining = byte_offset
        while remaining:
            discarded = qub.read(min(remaining, 16 * 1024 * 1024))
            if not discarded:
                raise EOFError("QUB ended before selected band {}".format(band_number))
            remaining -= len(discarded)
        raw = qub.read(plane_size)
        qub.close()
    if len(raw) != plane_size:
        raise EOFError("Band has {} bytes; expected {}".format(len(raw), plane_size))
    return np.frombuffer(raw, dtype="<f4").reshape(LINES, SAMPLES)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--validity-csv", type=Path, default=DEFAULT_VALIDITY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--band", type=int, default=40)
    parser.add_argument("--lower-percentile", type=float, default=1.0)
    parser.add_argument("--upper-percentile", type=float, default=99.0)
    args = parser.parse_args()

    wavelength_nm = verify_band_validity(args.band, args.validity_csv)
    plane = read_single_band(args.archive, args.band)
    finite = np.isfinite(plane)
    if not finite.any():
        raise ValueError("Selected band has no finite values")
    low, high = np.percentile(
        plane[finite], [args.lower_percentile, args.upper_percentile]
    )
    if high <= low:
        raise ValueError("Invalid display stretch bounds {} to {}".format(low, high))
    display = np.clip((plane - low) / (high - low), 0.0, 1.0)
    display = np.where(finite, display, 0.0)
    image = np.round(display * 255.0).astype(np.uint8)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), image):
        raise OSError("Could not write {}".format(args.output))
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "source_archive": str(args.archive),
        "source_cube_member": "data/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.qub",
        "band_number_1_based": args.band,
        "wavelength_nm": wavelength_nm,
        "e1g2_validity": "VALID in the official E1G2 band-validity table",
        "dimensions_samples_lines": [SAMPLES, LINES],
        "source_data_type": "IEEE754LSBSingle, little-endian float32, BSQ",
        "finite_pixel_count": int(finite.sum()),
        "display_stretch_percentiles": [args.lower_percentile, args.upper_percentile],
        "display_stretch_source_values": [float(low), float(high)],
        "output_png": str(args.output),
        "output_md5": hashlib.md5(args.output.read_bytes()).hexdigest(),
        "use_note": "Display-stretched radiance band for morphology matching only. It is not a reflectance product and does not validate radiometric scale or masks.",
    }
    args.metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
