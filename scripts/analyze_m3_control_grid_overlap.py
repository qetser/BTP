#!/usr/bin/env python3
"""Count sparse IIRS geometry points within candidate M3 product footprints."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from pathlib import Path


DEFAULT_IIRS_ZIP = Path(
    "data/pradan/e1g2_candidate_20260227T1239538758/"
    "ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
)
DEFAULT_METRICS = Path("results/phase-1/m1-reference-data/metrics/m3_control_grid_overlap.csv")
DEFAULT_FIGURE = Path("results/phase-1/m1-reference-data/figures/m3_control_grid_overlap.svg")
DEFAULT_FOOTPRINTS = Path("results/phase-1/m1-reference-data/m3_ode_footprints.json")


def parse_rings(wkt: str) -> list[list[tuple[float, float]]]:
    """Read coordinate rings from Polygon or MultiPolygon WKT."""
    rings = []
    for ring_text in re.findall(r"\(([^()]*)\)", wkt):
        points = []
        for coordinate in ring_text.split(","):
            values = coordinate.strip().split()
            if len(values) >= 2:
                try:
                    points.append((float(values[0]), float(values[1])))
                except ValueError:
                    continue
        if len(points) >= 3:
            rings.append(points)
    return rings


def point_on_segment(x: float, y: float, a: tuple[float, float], b: tuple[float, float]) -> bool:
    cross = (x - a[0]) * (b[1] - a[1]) - (y - a[1]) * (b[0] - a[0])
    if abs(cross) > 1e-9:
        return False
    return (
        min(a[0], b[0]) - 1e-9 <= x <= max(a[0], b[0]) + 1e-9
        and min(a[1], b[1]) - 1e-9 <= y <= max(a[1], b[1]) + 1e-9
    )


def in_ring(x: float, y: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        if point_on_segment(x, y, a, b):
            return True
        if (a[1] > y) != (b[1] > y):
            crossing_x = (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]
            if x < crossing_x:
                inside = not inside
    return inside


def in_footprint(x: float, y: float, rings: list[list[tuple[float, float]]]) -> bool:
    # Even-odd ring parity handles holes and disjoint polygon components.
    return sum(1 for ring in rings if in_ring(x, y, ring)) % 2 == 1


def load_iirs_points(archive_path: Path) -> list[tuple[float, float]]:
    with zipfile.ZipFile(archive_path) as archive:
        csv_name = next(name for name in archive.namelist() if name.endswith("_g_grd_d18.csv"))
        text = archive.read(csv_name).decode("utf-8-sig")
    rows = csv.DictReader(text.splitlines())
    return [(float(row["Longitude"]), float(row["Latitude"])) for row in rows]


def write_svg(path: Path, rows: list[dict[str, object]]) -> None:
    width, height = 900, 390
    left, right, top, bottom = 250, 50, 70, 65
    plot_width = width - left - right
    plot_height = height - top - bottom
    max_count = max((int(row["control_points_inside"]) for row in rows), default=1) or 1
    row_height = plot_height / max(len(rows), 1)
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" viewBox="0 0 {} {}">'.format(width, height, width, height),
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="{}" y="30" font-family="sans-serif" font-size="20" font-weight="bold">IIRS geometry control points inside M³ footprints</text>'.format(left),
        '<text x="{}" y="51" font-family="sans-serif" font-size="12" fill="#444">E1G2 sparse control grid: {} points. Count only; not an image-pixel overlap measure.</text>'.format(left, rows[0]["control_points_total"] if rows else 0),
        '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#333"/>'.format(left, top + plot_height, left + plot_width, top + plot_height),
    ]
    for tick in range(0, 5):
        value = max_count * tick / 4
        x = left + plot_width * tick / 4
        pieces.append('<line x1="{:.1f}" y1="{}" x2="{:.1f}" y2="{}" stroke="#dddddd"/>'.format(x, top, x, top + plot_height))
        pieces.append('<text x="{:.1f}" y="{}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#444">{:.0f}</text>'.format(x, top + plot_height + 18, value))
    for i, row in enumerate(rows):
        y = top + i * row_height + row_height * 0.18
        bar_height = row_height * 0.58
        count = int(row["control_points_inside"])
        bar_width = plot_width * count / max_count
        label = str(row["label_product_id"]).replace("_V01_L2", "")
        pieces.append('<text x="{}" y="{:.1f}" text-anchor="end" font-family="monospace" font-size="11">{}</text>'.format(left - 10, y + bar_height * 0.78, label))
        pieces.append('<rect x="{}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="#3976a8"/>'.format(left, y, bar_width, bar_height))
        pieces.append('<text x="{:.1f}" y="{:.1f}" font-family="sans-serif" font-size="11">{}</text>'.format(left + bar_width + 5, y + bar_height * 0.78, count))
    pieces.append('<text x="{}" y="{}" text-anchor="middle" font-family="sans-serif" font-size="12">IIRS geometry grid points inside M³ footprint (points)</text>'.format(left + plot_width / 2, height - 12))
    pieces.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(pieces), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iirs-zip", type=Path, default=DEFAULT_IIRS_ZIP)
    parser.add_argument("--footprints", type=Path, default=DEFAULT_FOOTPRINTS)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    args = parser.parse_args()

    points = load_iirs_points(args.iirs_zip)
    if not points:
        raise RuntimeError("IIRS geometry table contains no coordinate points")
    source = json.loads(args.footprints.read_text(encoding="utf-8"))
    rows = []
    for item in source["footprints"]:
        rings = parse_rings(item["footprint_gl_geometry"])
        if not rings:
            raise RuntimeError("No rings parsed for {}".format(item["label_product_id"]))
        inside = sum(1 for lon, lat in points if in_footprint(lon, lat, rings))
        rows.append(
            {
                "label_product_id": item["label_product_id"],
                "control_points_inside": inside,
                "control_points_outside": len(points) - inside,
                "control_points_total": len(points),
                "inside_fraction_percent": 100.0 * inside / len(points) if points else 0.0,
            }
        )
    rows.sort(key=lambda row: (-int(row["control_points_inside"]), str(row["label_product_id"])))

    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label_product_id", "control_points_inside", "control_points_outside", "control_points_total", "inside_fraction_percent"]
    with args.metrics.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_svg(args.figure, rows)
    print("IIRS control points: {}".format(len(points)))
    for row in rows:
        print("{}: {} points ({:.2f}%)".format(row["label_product_id"], row["control_points_inside"], row["inside_fraction_percent"]))
    print("Metrics: {}".format(args.metrics))
    print("Figure: {}".format(args.figure))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
