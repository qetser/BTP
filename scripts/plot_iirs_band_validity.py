"""Export the official IIRS band-validity table and a compact mode plot.

Run: uv run --no-project --with xlrd python scripts/plot_iirs_band_validity.py
"""

import csv
from pathlib import Path
import zipfile

import xlrd


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/pradan/iir.zip"
RESULTS = ROOT / "results/phase-1/m1-inventory"
CSV = RESULTS / "metrics/band_validity_by_mode.csv"
SVG = RESULTS / "figures/band_validity_by_mode.svg"
MODES = ("E1G2", "E2G2", "E3G2", "E4G2")


def main():
    with zipfile.ZipFile(ARCHIVE) as archive:
        workbook = xlrd.open_workbook(
            file_contents=archive.read("iir/miscellaneous/ch2_iirs_band_validity_list.xls")
        )
    flags = workbook.sheet_by_name("Sheet1")
    reasons = workbook.sheet_by_name("Sheet2")
    assert flags.nrows == reasons.nrows == 257
    assert tuple(flags.row_values(0)[1:5]) == MODES
    assert tuple(reasons.row_values(0)[2:6]) == MODES

    rows = []
    for row_index in range(1, 257):
        band = int(flags.cell_value(row_index, 0))
        assert band == int(reasons.cell_value(row_index, 0)) == row_index
        row = {"band_number": band, "wavelength_nm": reasons.cell_value(row_index, 1)}
        for column, mode in enumerate(MODES, 1):
            valid = int(flags.cell_value(row_index, column))
            reason = str(reasons.cell_value(row_index, column + 1)).strip()
            assert valid in (0, 1)
            assert (reason == "VALID") == bool(valid), (band, mode, valid, reason)
            row[f"{mode}_valid"] = valid
            row[f"{mode}_reason"] = reason
        rows.append(row)

    CSV.parent.mkdir(parents=True, exist_ok=True)
    with CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    # Each column is one measured band. The horizontal coordinate is band number.
    left, top, cell, row_height = 85, 40, 4, 34
    width, height = left + 256 * cell + 25, top + 4 * row_height + 62
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font:13px sans-serif;fill:#222}.small{font-size:11px}</style>',
        '<text x="85" y="22">IIRS official band validity by exposure and gain mode</text>',
    ]
    for mode_index, mode in enumerate(MODES):
        y = top + mode_index * row_height
        parts.append(f'<text x="15" y="{y + 19}">{mode}</text>')
        for row in rows:
            x = left + (row["band_number"] - 1) * cell
            color = "#287d5a" if row[f"{mode}_valid"] else "#ccd0d5"
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="24" fill="{color}"/>')
    for band in (1, 50, 100, 150, 200, 256):
        x = left + (band - 1) * cell
        parts.append(f'<text class="small" x="{x}" y="{top + 4 * row_height + 2}">{band}</text>')
    parts += [
        f'<text class="small" x="{left}" y="{height - 15}">Band number (green: valid; gray: invalid or low confidence)</text>',
        "</svg>",
    ]
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text("\n".join(parts) + "\n")
    print(f"Saved {CSV.relative_to(ROOT)} and {SVG.relative_to(ROOT)}")
    for mode in MODES:
        print(mode, sum(row[f"{mode}_valid"] for row in rows), "valid bands")


if __name__ == "__main__":
    main()
