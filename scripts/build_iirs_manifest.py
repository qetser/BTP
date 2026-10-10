#!/usr/bin/env python3
"""Build a reproducible inventory and integrity manifest for local IIRS products."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


CHUNK_SIZE = 8 * 1024 * 1024


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def first_text(root: ET.Element, name: str, parent: ET.Element | None = None) -> str:
    scope = parent if parent is not None else root
    for element in scope.iter():
        if local_name(element.tag) == name and element.text:
            return element.text.strip()
    return ""


def first_attr(root: ET.Element, name: str, attribute: str) -> str:
    for element in root.iter():
        if local_name(element.tag) == name and attribute in element.attrib:
            return element.attrib[attribute]
    return ""


def all_text(root: ET.Element, name: str) -> list[str]:
    return [element.text.strip() for element in root.iter() if local_name(element.tag) == name and element.text]


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_hdr(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().lower().replace(" ", "_")] = value.strip()
    return values


def parse_product(zip_path: Path, product_dir: Path) -> dict[str, str]:
    xml_paths = sorted(product_dir.glob("data/*/*/*.xml"))
    qub_paths = sorted(product_dir.glob("data/*/*/*.qub"))
    hdr_paths = sorted(product_dir.glob("data/raw/*/*.hdr"))
    if len(xml_paths) != 1 or len(qub_paths) != 1:
        raise ValueError(f"expected one data label and cube in {product_dir}")

    xml_path = xml_paths[0]
    qub_path = qub_paths[0]
    hdr = parse_hdr(hdr_paths[0]) if len(hdr_paths) == 1 else {}
    root = ET.parse(xml_path).getroot()

    axes: dict[str, str] = {}
    for axis in root.iter():
        if local_name(axis.tag) != "Axis_Array":
            continue
        axis_name = first_text(axis, "axis_name")
        elements = first_text(axis, "elements")
        if axis_name:
            axes[axis_name.lower()] = elements

    coords = {}
    for key in ("upper_left_latitude", "upper_right_latitude", "lower_left_latitude", "lower_right_latitude", "upper_left_longitude", "upper_right_longitude", "lower_left_longitude", "lower_right_longitude"):
        coords[key] = first_text(root, key)
    latitudes = [float(value) for key, value in coords.items() if "latitude" in key and value]
    longitudes = [float(value) for key, value in coords.items() if "longitude" in key and value]

    declared_bytes = first_text(root, "file_size")
    declared_md5 = first_text(root, "md5_checksum")
    data_type = first_text(root, "data_type")
    item_bytes = {"UnsignedLSB2": 2, "IEEE754LSBSingle": 4}.get(data_type, "")
    expected_bytes = ""
    if item_bytes and all(axis in axes for axis in ("band", "line", "sample")):
        expected_bytes = str(int(axes["band"]) * int(axes["line"]) * int(axes["sample"]) * item_bytes)

    with zipfile.ZipFile(zip_path) as archive:
        archive_entry = next((item for item in archive.infolist() if item.filename.endswith(qub_path.name)), None)
        archive_cube_bytes = str(archive_entry.file_size) if archive_entry else ""

    qub_bytes = qub_path.stat().st_size
    return {
        "product_kind": "calibrated" if "/calibrated/" in str(xml_path) else "raw",
        "product_id": first_text(root, "logical_identifier"),
        "version_id": first_text(root, "version_id"),
        "start_time": first_text(root, "start_date_time"),
        "stop_time": first_text(root, "stop_date_time"),
        "processing_level": first_text(root, "processing_level"),
        "job_id": first_text(root, "job_id"),
        "imaging_orbit": first_text(root, "imaging_orbit_number"),
        "dumping_orbit": first_text(root, "dumping_orbit_number"),
        "gain": first_text(root, "gain"),
        "exposure": first_text(root, "exposure"),
        "detector_temperature_k": first_text(root, "detector_temperature"),
        "pixel_resolution_m": first_text(root, "pixel_resolution"),
        "sun_elevation_deg": first_text(root, "sun_elevation"),
        "solar_incidence_deg": first_text(root, "solar_incidence"),
        "area": first_text(root, "area"),
        "upper_left_latitude_deg": coords["upper_left_latitude"],
        "upper_right_latitude_deg": coords["upper_right_latitude"],
        "lower_left_latitude_deg": coords["lower_left_latitude"],
        "lower_right_latitude_deg": coords["lower_right_latitude"],
        "latitude_min_deg": str(min(latitudes)) if latitudes else "",
        "latitude_max_deg": str(max(latitudes)) if latitudes else "",
        "longitude_min_deg": str(min(longitudes)) if longitudes else "",
        "longitude_max_deg": str(max(longitudes)) if longitudes else "",
        "band_count": axes.get("band", ""),
        "line_count": axes.get("line", ""),
        "sample_count": axes.get("sample", ""),
        "data_type": data_type,
        "data_unit": first_text(root, "unit"),
        "axis_index_order": first_text(root, "axis_index_order"),
        "first_wavelength_nm": (all_text(root, "center_wavelength") or [""])[0],
        "last_wavelength_nm": (all_text(root, "center_wavelength") or [""])[-1],
        "wavelength_count": str(len(all_text(root, "center_wavelength"))),
        "first_band_width_nm": (all_text(root, "band_width") or [""])[0],
        "last_band_width_nm": (all_text(root, "band_width") or [""])[-1],
        "declared_file_bytes": declared_bytes,
        "expected_file_bytes_from_axes": expected_bytes,
        "extracted_qub_bytes": str(qub_bytes),
        "archive_qub_bytes": archive_cube_bytes,
        "declared_md5": declared_md5,
        "computed_qub_md5": digest(qub_path, "md5"),
        "zip_bytes": str(zip_path.stat().st_size),
        "zip_sha256": digest(zip_path, "sha256"),
        "zip_path": str(zip_path),
        "label_path": str(xml_path),
        "cube_path": str(qub_path),
        "hdr_dimensions": f"{hdr.get('samples', '')}x{hdr.get('lines', '')}x{hdr.get('bands', '')}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--extracted-root", type=Path, default=Path("data/extracted"))
    parser.add_argument("--output", type=Path, default=Path("results/phase-1/m1-inventory/iirs_inventory.csv"))
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for zip_path in sorted(args.data_root.rglob("*.zip")):
        if not re.match(r"^ch2_iir_n[cr]i_\d{8}T\d{10}_d_img_[a-z0-9]+\.zip$", zip_path.name, re.IGNORECASE):
            continue
        scene_key = re.sub(r"^ch2_iir_n[cr]i_", "", zip_path.stem)
        kind_prefix = "calibrated_" if "_nci_" in zip_path.stem else "raw_"
        matches = sorted(args.extracted_root.glob(f"{kind_prefix}{scene_key}"))
        if len(matches) != 1:
            raise SystemExit(f"expected one extracted directory for {zip_path.name}, found {len(matches)}")
        rows.append(parse_product(zip_path, matches[0]))
    if not rows:
        raise SystemExit(f"no IIRS ZIP archives found under {args.data_root}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} products to {args.output}")
    print(f"generated_utc={datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
