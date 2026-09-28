# E1G2 candidate acquisition notes

- Check date: 2026-09-28.
- Candidate selected from user-provided PRADAN download-script paths. Raw product: `ch2_iir_nri_20260227T1239538758_d_img_d18.zip`; calibrated counterpart: `ch2_iir_nci_20260227T1239538758_d_img_d18.zip`.
- Both archives are stored under ignored `data/pradan/e1g2_candidate_20260227T1239538758/`. Only these two ZIPs were downloaded from the bulk selection.
- Both ZIP CRC checks passed. XML labels were read in place. Each QUB was streamed from its ZIP and its actual MD5 matched the PDS4 label. Cube files were not extracted to disk.
- The first calibrated request with the earlier session returned HTTP 302. A refreshed PRADAN session later allowed the single calibrated product transfer.
- Extracted only the official calibrated browse PNG to `figures/20260227_e1g2_calibrated_browse.png`; the guide describes it as a subsampled band 40 browse image. It is for visual orientation, not spectral interpretation.
- No metric was computed. The PNG is a source browse figure, not a plotted metric, so no CSV/JSON metric artifact was created.
- The follow-up E1G2 audit is reproducible with `uv run --no-project --with numpy --with matplotlib python scripts/analyze_iirs_e1g2_scene.py`. It creates the per-band CSV and a descriptive figure while streaming the two QUB objects from their ZIPs. Counts are exact; quantiles are fixed-grid samples. The LUT comparison supports internal radiance-scale consistency, not independent validation. The saturation comparison is unresolved and must not be used as a mask.
