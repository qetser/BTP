"""Make README previews from the two official calibrated IIRS browse images.

Run: uv run --no-project --with pillow python scripts/build_iirs_strip_previews.py

Each preview shows all source rows in four consecutive panels. Both image axes
are resized by the same factor within each panel; no radiance cube is read.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "results/phase-1/m1-inventory/figures"
SOURCES = {
    "m65": ROOT
    / "data/extracted/calibrated_20200208T0057589143_d_img_m65/browse/calibrated/20200208/ch2_iir_nci_20200208T0057589143_b_brw_m65.png",
    "d18": ROOT
    / "data/extracted/calibrated_20200208T1245274109_d_img_d18/browse/calibrated/20200208/ch2_iir_nci_20200208T1245274109_b_brw_d18.png",
}


def font(size):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def make_preview(suffix, source):
    with Image.open(source) as original:
        assert original.format == "PNG"
        assert original.width == 175
        image = original.convert("RGB")

    panel_width = 110
    scale = panel_width / image.width
    bounds = [round(i * image.height / 4) for i in range(5)]
    panels = []
    for start, stop in zip(bounds[:-1], bounds[1:]):
        piece = image.crop((0, start, image.width, stop))
        panel_height = round(piece.height * scale)
        panels.append(piece.resize((panel_width, panel_height), Image.Resampling.LANCZOS))

    left, gap, top, bottom = 22, 14, 80, 48
    width = 2 * left + 4 * panel_width + 3 * gap
    height = top + max(panel.height for panel in panels) + bottom
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    title_font, label_font = font(17), font(11)
    draw.text((left, 14), f"IIRS calibrated browse: {suffix}", fill="#222222", font=title_font)
    draw.text((left, 44), "Four consecutive along-track sections, left to right", fill="#444444", font=label_font)

    for index, (panel, start, stop) in enumerate(zip(panels, bounds[:-1], bounds[1:])):
        x = left + index * (panel_width + gap)
        draw.text((x, 63), f"Part {index + 1}", fill="#222222", font=label_font)
        canvas.paste(panel, (x, top))
        draw.text((x, top + panel.height + 8), f"rows {start + 1}-{stop}", fill="#444444", font=label_font)

    FIGURES.mkdir(parents=True, exist_ok=True)
    output = FIGURES / f"calibrated_browse_{suffix}_four_part_preview.png"
    canvas.save(output, format="PNG", optimize=True)
    print(output.relative_to(ROOT), canvas.size)


def main():
    for suffix, source in SOURCES.items():
        make_preview(suffix, source)


if __name__ == "__main__":
    main()
