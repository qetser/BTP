#!/usr/bin/env python3
"""Fetch only tiled LROC WAC GeoTIFF blocks surrounding the E1G2 footprint."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import io
import json
import math
import struct
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path


SOURCE_URL = (
    "https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/"
    "LROLRC_2001/EXTRAS/BROWSE/WAC_GLOBAL/"
    "WAC_GLOBAL_O000N0000_100M.PYR.TIF"
)
DEFAULT_IIRS_ZIP = Path(
    "data/pradan/e1g2_candidate_20260227T1239538758/"
    "ch2_iir_nci_20260227T1239538758_d_img_d18.zip"
)
DEFAULT_OUTPUT = Path("data/reference/lroc_wac_e1g2/e1g2_wac_crop.pgm")
DEFAULT_METADATA = Path("results/phase-1/m1-reference-data/wac_crop_metadata.json")


def request_range(url: str, start: int, end: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"Range": "bytes={}-{}".format(start, end), "User-Agent": "IIRS-M1-WAC-crop/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 206:
            raise RuntimeError("Server did not honor byte range {}-{}".format(start, end))
        content_range = response.headers.get("Content-Range", "")
        expected = "bytes {}-{}".format(start, end)
        if not content_range.startswith(expected):
            raise RuntimeError("Unexpected Content-Range: {}".format(content_range))
        return response.read()


def remote_head(url: str) -> dict[str, str]:
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=30) as response:
        headers = response.headers
        if headers.get("Accept-Ranges", "").lower() != "bytes":
            raise RuntimeError("WAC server does not advertise byte-range support")
        return {
            "content_length_bytes": headers.get("Content-Length", ""),
            "last_modified": headers.get("Last-Modified", ""),
            "etag": headers.get("ETag", ""),
            "accept_ranges": headers.get("Accept-Ranges", ""),
        }


def decode_value(data: bytes, byte_order: str, field_type: int, count: int):
    formats = {1: "B", 2: "B", 3: "H", 4: "I", 5: "II", 6: "b", 7: "B", 8: "h", 9: "i", 10: "ii", 11: "f", 12: "d"}
    sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}
    if field_type not in formats:
        raise ValueError("Unsupported TIFF field type {}".format(field_type))
    fmt = formats[field_type]
    if field_type == 5 or field_type == 10:
        values = struct.unpack(byte_order + fmt * count, data[: sizes[field_type] * count])
        return [values[i] / values[i + 1] for i in range(0, len(values), 2)]
    values = struct.unpack(byte_order + fmt * count, data[: sizes[field_type] * count])
    return values[0] if count == 1 else values


def tiff_ifd(url: str) -> tuple[dict[int, object], int, dict[str, object]]:
    header = request_range(url, 0, 7)
    if header[:2] == b"II":
        byte_order = "<"
    elif header[:2] == b"MM":
        byte_order = ">"
    else:
        raise ValueError("Invalid TIFF byte order marker")
    magic = struct.unpack(byte_order + "H", header[2:4])[0]
    if magic != 42:
        raise ValueError("Only classic TIFF is supported; magic is {}".format(magic))
    ifd_offset = struct.unpack(byte_order + "I", header[4:8])[0]
    head = request_range(url, ifd_offset, ifd_offset + 1)
    count = struct.unpack(byte_order + "H", head)[0]
    block = request_range(url, ifd_offset, ifd_offset + 2 + count * 12 + 4 - 1)
    tags = {}
    types = {}
    for i in range(count):
        entry = block[2 + 12 * i:14 + 12 * i]
        tag, field_type, value_count, value_or_offset = struct.unpack(byte_order + "HHII", entry)
        types[tag] = (field_type, value_count)
        byte_count = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}[field_type] * value_count
        if byte_count <= 4:
            raw = entry[8:8 + byte_count]
        else:
            raw = request_range(url, value_or_offset, value_or_offset + byte_count - 1)
        tags[tag] = decode_value(raw, byte_order, field_type, value_count)
    metadata = {
        "ifd_offset": ifd_offset,
        "byte_order": byte_order,
        "tags": {str(k): list(v) if isinstance(v, tuple) else v for k, v in tags.items() if k in (256, 257, 258, 259, 262, 277, 284, 322, 323, 33550, 33922, 33935)},
        "next_ifd_offset": struct.unpack(byte_order + "I", block[2 + count * 12:6 + count * 12])[0],
    }
    return tags, byte_order, metadata


def load_iirs_lonlat(archive_path: Path) -> list[tuple[float, float]]:
    with zipfile.ZipFile(archive_path) as archive:
        name = next(n for n in archive.namelist() if n.endswith("_g_grd_d18.csv"))
        text = archive.read(name).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [(float(row["Longitude"]), float(row["Latitude"])) for row in reader]


def orthographic_sample_line(lon_deg: float, lat_deg: float, radius_m: float, tiepoint, pixel_scale):
    lon = math.radians(lon_deg)
    lat = math.radians(lat_deg)
    x = radius_m * math.cos(lat) * math.sin(lon)
    y = radius_m * math.sin(lat)
    sample = tiepoint[0] + (x - tiepoint[3]) / pixel_scale[0]
    line = tiepoint[1] + (tiepoint[4] - y) / pixel_scale[1]
    return sample, line


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iirs-zip", type=Path, default=DEFAULT_IIRS_ZIP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--margin-km", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    source_headers = remote_head(SOURCE_URL)
    tags, byte_order, tiff_metadata = tiff_ifd(SOURCE_URL)
    width, height = int(tags[256]), int(tags[257])
    bits, compression = int(tags[258]), int(tags[259])
    tile_width, tile_height = int(tags[322]), int(tags[323])
    if bits != 8 or compression != 1 or int(tags[277]) != 1:
        raise RuntimeError("Expected uncompressed, 8-bit, single-channel WAC tiles")
    pixel_scale = tags[33550]
    tiepoint = tags[33922]
    if not isinstance(pixel_scale, tuple) or not isinstance(tiepoint, tuple):
        raise RuntimeError("Expected GeoTIFF ModelPixelScale and ModelTiepoint tags")
    geodoubles = tags.get(34736, ())
    if not geodoubles:
        raise RuntimeError("GeoTIFF has no ellipsoid radius in its GeoDoubleParams")
    radius_m = float(geodoubles[0])

    lonlat = load_iirs_lonlat(args.iirs_zip)
    projected = [orthographic_sample_line(lon, lat, radius_m, tiepoint, pixel_scale) for lon, lat in lonlat]
    margin_px = int(math.ceil(args.margin_km * 1000.0 / pixel_scale[0]))
    sample0 = max(0, int(math.floor(min(point[0] for point in projected))) - margin_px)
    sample1 = min(width, int(math.ceil(max(point[0] for point in projected))) + margin_px + 1)
    line0 = max(0, int(math.floor(min(point[1] for point in projected))) - margin_px)
    line1 = min(height, int(math.ceil(max(point[1] for point in projected))) + margin_px + 1)
    crop_width, crop_height = sample1 - sample0, line1 - line0

    ntiles_x = math.ceil(width / tile_width)
    ntiles_y = math.ceil(height / tile_height)
    ntile = ntiles_x * ntiles_y
    tile_offsets = tags[324]
    tile_counts = tags[325]
    if len(tile_offsets) != ntile or len(tile_counts) != ntile:
        raise RuntimeError("TIFF tile index count does not match raster dimensions")

    tx0, tx1 = sample0 // tile_width, (sample1 - 1) // tile_width
    ty0, ty1 = line0 // tile_height, (line1 - 1) // tile_height
    tile_keys = [(tx, ty) for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)]

    def fetch_tile(key):
        tx, ty = key
        index = ty * ntiles_x + tx
        start = tile_offsets[index]
        size = tile_counts[index]
        raw = request_range(SOURCE_URL, start, start + size - 1)
        expected = tile_width * tile_height
        if len(raw) != expected:
            raise RuntimeError("Tile {} has {} bytes; expected {}".format(key, len(raw), expected))
        return key, raw

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        tile_data = dict(pool.map(fetch_tile, tile_keys))

    crop = bytearray(crop_width * crop_height)
    for (tx, ty), raw in tile_data.items():
        tile = memoryview(raw)
        src_x0 = max(sample0, tx * tile_width)
        src_x1 = min(sample1, (tx + 1) * tile_width)
        src_y0 = max(line0, ty * tile_height)
        src_y1 = min(line1, (ty + 1) * tile_height)
        for src_y in range(src_y0, src_y1):
            src_start = (src_y - ty * tile_height) * tile_width + (src_x0 - tx * tile_width)
            dst_start = (src_y - line0) * crop_width + (src_x0 - sample0)
            count = src_x1 - src_x0
            crop[dst_start:dst_start + count] = tile[src_start:src_start + count]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as handle:
        handle.write("P5\n{} {}\n255\n".format(crop_width, crop_height).encode("ascii"))
        handle.write(crop)

    metadata = {
        "source_url": SOURCE_URL,
        "source_http": source_headers,
        "source_product": "WAC_GLOBAL_O000N0000_100M.PYR.TIF",
        "source_page": "https://data.lroc.im-ldi.com/lroc/view_rdr_product/WAC_GLOBAL_O000N0000_100M",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "crop_file": str(args.output),
        "crop_format": "binary PGM P5, one 8-bit grayscale channel",
        "source_raster_width": width,
        "source_raster_height": height,
        "crop_origin_sample": sample0,
        "crop_origin_line": line0,
        "crop_width": crop_width,
        "crop_height": crop_height,
        "margin_km": args.margin_km,
        "tile_size": [tile_width, tile_height],
        "tiles_fetched": len(tile_keys),
        "bytes_fetched_for_tiles": sum(tile_counts[ty * ntiles_x + tx] for tx, ty in tile_keys),
        "map_projection": "Orthographic centered at 0N, 0E, per source product page",
        "pixel_scale_model_units": list(pixel_scale),
        "model_tiepoint": list(tiepoint),
        "geographic_radius_m": radius_m,
        "tiff_metadata": tiff_metadata,
        "iirs_geometry_archive": str(args.iirs_zip),
        "iirs_geometry_point_count": len(lonlat),
        "iirs_geometry_latlon_bounds": {
            "min_longitude_east_deg": min(p[0] for p in lonlat),
            "max_longitude_east_deg": max(p[0] for p in lonlat),
            "min_latitude_deg": min(p[1] for p in lonlat),
            "max_latitude_deg": max(p[1] for p in lonlat),
        },
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("WAC crop: {} x {} pixels".format(crop_width, crop_height))
    print("Tiles fetched: {} ({} bytes)".format(metadata["tiles_fetched"], metadata["bytes_fetched_for_tiles"]))
    print("Crop: {}".format(args.output))
    print("Metadata: {}".format(args.metadata))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
