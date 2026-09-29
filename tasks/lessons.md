# Lessons

- **Data units:** A raw IIRS `.qub` is a detector-count product until the label and calibrated counterpart establish physical units. Do not treat counts as radiance or reflectance.
- **Scientific claims:** Do not turn a 3 µm anomaly into an ice label without signal, thermal, and independent-reference checks.
- **Evaluation:** Split by independent orbit/province; neighboring pixel splits overstate model quality.
- **Geometry axes:** Read the image dimensions and unique `Pixel`/`Scan` field values from the product. A count of sampled scan positions is not the image's sample width or line count.
- **Image scale:** If a browse image is smaller than the cube, one browse pixel spans `cube_dimension / browse_dimension` cube pixels. Multiply browse offsets by that ratio when expressing residuals in cube pixels.
- **Git scope:** Stage only intended files. Keep `data/`, `AGENTS.md`, `codex.md`, `.agents/skills`, and `.codex` untracked, and check the actual remote and branch before pushing.
- **Attribution:** Never include Claude or Codex in co-author attribution.
