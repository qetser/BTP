#!/usr/bin/env python3
"""Query PDS ODE for M3 reflectance products intersecting the E1G2 footprint box."""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ODE_URL = "https://oderest.rsl.wustl.edu/live2"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/phase-1/m1-reference-data/m3_overlap_candidates.csv"),
    )
    parser.add_argument(
        "--footprints-output",
        type=Path,
        default=Path("results/phase-1/m1-reference-data/m3_ode_footprints.json"),
    )
    args = parser.parse_args()

    # E1G2 geometry bounds converted to ODE's positive-east 0–360 longitude.
    params = {
        "easternlon": "356.5",
        "ihid": "CH1-ORB",
        "iid": "M3",
        "loc": "f",  # Intersect product footprints, not only bounding boxes.
        "maxlat": "27",
        "minlat": "-7",
        "output": "XML",
        "pt": "REFIMG",
        "query": "product",
        "results": "cm",
        "target": "moon",
        "westernlon": "354.5",
    }
    url = ODE_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "IIRS-M1-reference-query/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        root = ET.fromstring(response.read())

    status = root.findtext("Status")
    if status != "Success":
        raise RuntimeError("PDS ODE query did not succeed: {}".format(status))

    rows = []
    footprints = []
    for product in root.findall(".//Product"):
        label_url = product.findtext("External_url", "")
        label_product_id = Path(urllib.parse.urlparse(label_url).path).stem
        rows.append(
            {
                "label_product_id": label_product_id,
                "observation_time_utc": product.findtext("Observation_time", ""),
                "start_orbit": product.findtext("Start_orbit_number", ""),
                "center_latitude_deg": product.findtext("Center_latitude", ""),
                "center_longitude_east_deg": product.findtext("Center_longitude", ""),
                "external_label_url": label_url,
            }
        )
        footprints.append(
            {
                "label_product_id": label_product_id,
                "footprint_gl_geometry": product.findtext("Footprint_GL_geometry", ""),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "label_product_id",
        "observation_time_utc",
        "start_orbit",
        "center_latitude_deg",
        "center_longitude_east_deg",
        "external_label_url",
    ]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    args.footprints_output.parent.mkdir(parents=True, exist_ok=True)
    with args.footprints_output.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "query_date": root.findtext("QuerySummary/Date", ""),
                "query_service": ODE_URL,
                "location_mode": "footprint intersection",
                "product_type": "CH1-ORB/M3/REFIMG",
                "bounds": {
                    "west_longitude_east_deg": float(params["westernlon"]),
                    "east_longitude_east_deg": float(params["easternlon"]),
                    "min_latitude_deg": float(params["minlat"]),
                    "max_latitude_deg": float(params["maxlat"]),
                },
                "footprints": footprints,
            },
            handle,
            indent=2,
        )

    print("ODE status: {}".format(status))
    print("ODE-reported intersecting products: {}".format(root.findtext("Count", "unknown")))
    print("Metadata rows saved: {}".format(len(rows)))
    print("Saved: {}".format(args.output))
    print("Saved: {}".format(args.footprints_output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
