# Notes

- Reproduction:
  1. `uv run --no-project --with numpy --with scipy python scripts/build_e1g2_working_cube.py` (writes ignored `data/derived/e1g2/`, about 2.7 GB).
  2. `uv run --no-project --with numpy --with scipy --with matplotlib --with pvlib python scripts/run_e1g2_m2_physical_pilot.py` (about 9 minutes).
  3. `uv run --no-project --with numpy --with scipy --with matplotlib --with pvlib python scripts/run_e3g2_radiance_unit_physics.py`.
- Environment: Python 3.11.16, NumPy 2.2.6, SciPy 1.17.1, Matplotlib 3.11.2, pvlib 0.16.1.
- Script SHA-256 values at run time:
  - `build_e1g2_working_cube.py`: `42e101d3…0132de`
  - `run_e1g2_m2_physical_pilot.py`: `6e71ab08…5bd0`
  - `run_e3g2_radiance_unit_physics.py`: `93c3a51e…2adefd2a`
  - Code baseline commit: `304c5e8`.
- Solar spectrum: the NREL and LASP (TSIS-1 HSRS) endpoints timed out from this host, so the ASTM G173-03 extraterrestrial column bundled with pvlib was used. It is cached at ignored `data/reference/solar/astm_g173_extraterrestrial.csv`. A TSIS-1 or Thuillier spectrum would change band irradiance by a few percent. That does not affect the 1000× discrimination.
- OAT parsing: fixed-width fields from the product's `miscellaneous/readme.txt`. Field 31 is the solar zenith angle at the sub-satellite point. E1G2 spans 56.79–61.75°; E3G2 `m65` spans 42.8–50.7° and `d18` spans 43.3–51.3°. The emission angle is 0° (nadir) throughout E1G2.
- The plausibility rule in `e3g2_unit_test_summary.json` accepts a median I/F at 1.5 µm between 0.01 and 0.6. The two hypotheses differ by 1000×, so any reasonable interval gives the same decision.
- Open question: whether other station suffixes or processing versions also store mW. Check each new product with `run_e3g2_radiance_unit_physics.py` before analysis.
