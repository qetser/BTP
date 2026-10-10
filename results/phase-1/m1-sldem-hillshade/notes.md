# Notes

- Reproduction: install `requirements-research.lock`. Then run `.venv/bin/python scripts/register_iirs_to_sldem_hillshade.py`. The two signed 16-bit JPEG2000 tiles, labels, and auxiliary XML files reside under ignored `data/reference/sldem2015_e1g2/`. The script also needs the existing E1G2 band-40 display image and calibrated geometry archive.
- Tile SHA-256 values appear in `metrics/iirs_sldem_hillshade_summary.json`. The run used Python 3.11.16, NumPy 2.2.6, OpenCV 4.14.0, Matplotlib 3.11.2, and Pillow 12.3.0.
- Working-tree script SHA-256: `969f939350a765350731df264a8f5d104eaf78d19044a9f2cf8b35189fe64eae`. Code baseline commit: `304c5e8bc880d754ecab0b75983c8370b73d033e`.
- JPEG2000 decoding: OpenCV in this environment rejected the signed component. Pillow decoded it as uint16. The script reinterprets that bit pattern as two's-complement int16, consistent with the PDS label's signed sample type and observed elevations. Pillow is an explicit research requirement.
- Candidate held-out ranges are lines 0–999, 2250–2999, 4500–5249, and 9000–9749. Each has 150 guard lines on each side. The script selected sun direction and score threshold without inspecting held-out residuals.
- Candidate matching excludes any IIRS patch whose mapped reference contains DEM nodata or its one-pixel gradient boundary. It also masks candidate peaks when a shifted search window touches invalid terrain. This reduces candidates from 160 to 155 training and from 45 to 40 held-out windows before the training-only NCC cutoff.
