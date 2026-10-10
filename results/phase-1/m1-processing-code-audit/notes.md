# Notes

- SIS version: V17, March 2026. Relevant text is Appendix H, pages 115–126; Appendix F and Appendix J provide calibration context and the Level-0/Level-1 disclaimer.
- SIS product-format and archive sections (pp. 25, 28, 45) identify `.oat`, `.oath`, `.lbr`, and `.spm` as orbit/attitude, orbit/attitude header, lunar libration angle, and Sun-parameter files. They are ancillary geometry/illumination inputs, not pixel quality flags.
- Public implementation: [CH2IIRS](https://github.com/prabhakaralok/CH2IIRS), inspected at commit `cd84557b67317aa70cfdd7aa552d701861dc1a7b`. The repository README links the thermal algorithm to Verma et al. (2022) and phase correction to Chauhan et al. (2025).
- Files inspected: `README.md`, `ThermalInci.py`, and `TempC.py`. The code expects all 256 bands and reads the longwave range around 4500–4874 nm. It applies a hard-coded radiance scaling and coefficient array and contains no explicit pixel mask logic in the inspected paths.
- SIS band validity values and existing figure are in `results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv` and `results/phase-1/m1-inventory/figures/band_validity_by_mode.svg`. No new metric or plot was warranted.
- External processing code is a hypothesis/reference for method implementation only. The SIS remains the source for archive band-validity interpretation, while per-pixel fill/saturation semantics remain unresolved.
