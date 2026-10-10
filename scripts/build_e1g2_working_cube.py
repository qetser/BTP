#!/usr/bin/env python3
"""Build an ignored working copy of the E1G2 scene for the M2 pilot analyses.

Run from the repository root:
  uv run --no-project --with numpy --with scipy python scripts/build_e1g2_working_cube.py

Outputs go to data/derived/e1g2/ (ignored by Git). The source ZIP is read only.
- radiance_valid.npy: float32 (valid bands, lines, samples), values as stored in
  the Level-1 QUB (label unit µW/cm**2/sr/µm; no unit conversion applied).
- bands.csv: band number, center wavelength (nm), and FWHM for valid bands.
- line_geometry.csv: per-line UTC offset, solar zenith, solar azimuth, emission
  and phase angle interpolated in time from the OAT file.
- latlon.npy: float32 (2, lines, samples) latitude and east longitude from
  bilinear interpolation of the SLDEM relative-geometry candidate grid.
The geometry is a provisional relative correction, not validated geolocation.
"""
from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "data/pradan/e1g2_candidate_20260227T1239538758/ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
QUB_PART = "data/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.qub"
LABEL_PART = "data/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.xml"
OAT_PART = "miscellaneous/calibrated/20260227/ch2_iir_nci_20260227T1239538758_d_img_d18.oat"
VALIDITY = ROOT / "results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv"
GEOMETRY = ROOT / "results/phase-1/m1-sldem-correction-candidate/metrics/iirs_sldem_relative_geometry_candidate.csv"
OUT = ROOT / "data/derived/e1g2"

# OAT fixed-width layout from miscellaneous/readme.txt (field widths in bytes).
OAT_WIDTHS = [8, 6, 4, 28, 20, 20, 20, 20, 20, 20, 12, 12, 12, 56, 56, 56,
              14, 14, 14, 14, 14, 14, 12, 12, 1, 9, 9, 9, 10, 5, 9, 9]
OAT_FIELDS = {3: "utc", 18: "solar_azimuth", 19: "solar_elevation", 25: "emission",
              26: "phase", 30: "solar_zenith"}


def descendants(root, name):
    return [e for e in root.iter() if e.tag.split("}")[-1] == name]


def first_text(root, name):
    found = descendants(root, name)
    return found[0].text.strip() if found and found[0].text else ""


def parse_utc(text):
    y, mo, d, h, mi, s, ms = (int(v) for v in text.split())
    return datetime(y, mo, d, h, mi, s, ms * 1000, tzinfo=timezone.utc)


def parse_oat(text):
    rows = []
    for line in text.splitlines():
        if not line.startswith("ORBTATTD"):
            continue
        pos, rec = 0, {}
        for i, w in enumerate(OAT_WIDTHS):
            if i in OAT_FIELDS:
                rec[OAT_FIELDS[i]] = line[pos:pos + w]
            pos += w
        rows.append((parse_utc(rec["utc"]).timestamp(),
                     *(float(rec[k]) for k in ("solar_zenith", "solar_azimuth",
                                                "solar_elevation", "emission", "phase"))))
    return np.asarray(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(PRODUCT) as product:
        label = ET.fromstring(product.read(LABEL_PART))
        axes = {first_text(a, "axis_name"): int(first_text(a, "elements"))
                for a in descendants(label, "Axis_Array")}
        bands, lines, samples = axes["BAND"], axes["LINE"], axes["SAMPLE"]
        assert first_text(label, "unit") == "µW/cm**2/sr/µm"
        centers = [float(e.text) for e in descendants(label, "center_wavelength")]
        fwhm = [float(e.text) for e in descendants(label, "full_width_half_max")] or [np.nan] * bands
        start = datetime.fromisoformat(first_text(label, "start_date_time").replace("Z", "+00:00"))
        line_ms = float(first_text(label, "line_exposure_duration"))

        with VALIDITY.open(newline="") as f:
            valid = [int(r["band_number"]) for r in csv.DictReader(f) if r["E1G2_valid"] == "1"]
        cube = np.empty((len(valid), lines, samples), dtype=np.float32)
        plane_bytes = lines * samples * 4
        k = 0
        with product.open(QUB_PART) as stream:
            for b in range(1, bands + 1):
                raw = stream.read(plane_bytes)
                if len(raw) != plane_bytes:
                    raise IOError(f"short plane at band {b}")
                if b in valid:
                    cube[k] = np.frombuffer(raw, dtype="<f4").reshape(lines, samples)
                    k += 1
        np.save(OUT / "radiance_valid.npy", cube)
        with (OUT / "bands.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["band_number", "center_nm", "fwhm_nm"])
            for b in valid:
                w.writerow([b, centers[b - 1], fwhm[b - 1] if len(fwhm) == bands else ""])

        oat = parse_oat(product.read(OAT_PART).decode())
        t_line = start.timestamp() + np.arange(lines) * line_ms / 1000.0
        with (OUT / "line_geometry.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["line", "seconds_from_start", "solar_zenith_deg", "solar_azimuth_deg",
                        "solar_elevation_deg", "emission_deg", "phase_deg"])
            cols = [np.interp(t_line, oat[:, 0], oat[:, j]) for j in range(1, 6)]
            for i in range(lines):
                w.writerow([i, f"{t_line[i] - t_line[0]:.3f}", *(f"{c[i]:.4f}" for c in cols)])

    grid = {}
    with GEOMETRY.open(newline="") as f:
        for r in csv.DictReader(f):
            grid[(int(r["source_scan"]), int(r["source_pixel"]))] = (
                float(r["candidate_latitude_deg"]), float(r["candidate_longitude_east_deg"]))
    scans = sorted({s for s, _ in grid})
    pixels = sorted({p for _, p in grid})
    lat = np.array([[grid[(s, p)][0] for p in pixels] for s in scans])
    lon = np.array([[grid[(s, p)][1] for p in pixels] for s in scans])
    yy, xx = np.meshgrid(np.arange(lines), np.arange(samples), indexing="ij")
    pts = np.stack([yy.ravel(), xx.ravel()], axis=1)
    latlon = np.empty((2, lines, samples), dtype=np.float32)
    for i, arr in enumerate((lat, lon)):
        latlon[i] = RegularGridInterpolator((scans, pixels), arr)(pts).reshape(lines, samples)
    np.save(OUT / "latlon.npy", latlon)
    print(f"valid bands {len(valid)}; OAT records {len(oat)}; "
          f"SZA {oat[:, 1].min():.2f}-{oat[:, 1].max():.2f} deg; "
          f"lat {latlon[0].min():.2f}-{latlon[0].max():.2f}")


if __name__ == "__main__":
    main()
