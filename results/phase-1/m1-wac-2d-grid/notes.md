# Notes

- The source image is calibrated E1G2 band 40, but the 1st-to-99th percentile display stretch is used only to match morphology.
- The registered reference is the local WAC crop acquired from the LROC global mosaic. Its 100 m pixels differ from IIRS's nominal 80 m scale.
- Subpixel offsets come from a parabolic fit around the 2D normalized-correlation peak; this is a local peak refinement, not a full sensor-model solution.
- The 750-line blocks are about 60 km at nominal 80 m line spacing. Approximate 10 km summaries use 125-line bins and only report bins with at least three held-out ties.
- A second run produced byte-identical tie CSV and summary JSON files.
- M3 products remain absent from local `data/`; exact valid-pixel overlap was not attempted in this module.
