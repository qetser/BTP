# Notes

## Data source

- Archive: PDS Geosciences Node, PDS4 bundle `urn:nasa:pds:lro_diviner_derived1`, collection `data_derived_gcp`.
- Base URL: `https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_gcp/`
- Files (each with `.lbl` PDS3 and `.xml` PDS4 labels): `global_cumul_avg_cyl_10s00s_002.tab`, `global_cumul_avg_cyl_00n10n_002.tab`, `global_cumul_avg_cyl_10n20n_002.tab`, `global_cumul_avg_cyl_20n30n_002.tab`. Each table has 1,382,401 records of 113 bytes (156,211,313 bytes).
- Product: `DATA_SET_ID = LRO-L-DLRE-5-GCP-V1.0`, `PRODUCT_VERSION_ID = 1`, PDS4 `version_id = 1.0`, calibration software 4.0, producer J.-P. Williams (UCLA), creation 2016-05-27.
- Local copy: `data/reference/diviner/gcp/` (git-ignored). SHA-256 values for all 12 files are in `data/reference/diviner/SHA256SUMS`. Table SHA-256:
  - `10s00s`: `b47dd7ee7fe90ade46e376b4aa62bf153e8a9f2aeecd3593a32f3a514d61d981`
  - `00n10n`: `d333fc13b605beff4d977bd78299d3dd4c98905ea9008f69f4ee45073d7bedea`
  - `10n20n`: `9c3fc386357f082f0c4b9b00e64682475478cf9449430832da684384d1f2c4b5`
  - `20n30n`: `e15ea704b50adf16c25210dbc1669b965eb636fa81c90828778c853e8c2e21aa`
- All four table MD5 values match the bundle manifest `urn-nasa-pds-lro_diviner_derived1.md5` (dated 2026-09-21).
- TLS: the system trust store lacks the Sectigo Public Server Authentication Root R46 used by this server. Downloads used `curl --cacert` with the current `certifi` bundle (2026.07.22), so certificate verification stayed on.
- Download command per file: `curl --fail --cacert <certifi cacert.pem> -o <file> <base URL><file>`. Total size about 625 MB.

## Method details

- Table columns: `clon, clat, ltim, t3..t9, tbol`. Value −9999 means an empty bin. Negative values flag radiance below channel sensitivity and are treated as missing.
- Diviner channel 3 covers 7.55–8.05 µm, near the Christiansen feature, where emissivity is close to 1. Channels 6–9 cover 13–400 µm.
- Subsolar point: destination formula from the centre-column pixel, with the solar zenith as the angular distance and the solar azimuth (clockwise from north) as the bearing. It was not checked against a SPICE ephemeris. A 1° error in subsolar longitude changes local time by 4 minutes, or about 2 K in Diviner temperature near 08:00.
- Emissivity conversion: L = 0.95 B(T) gives T(ε = 1) = B⁻¹(0.95 B(T)) at 4.69 µm, which is about 1.8 K lower.
- Roughness sketch: Gaussian facet temperatures with spread σ, mean set so that the mean of σT⁴ equals the Diviner bolometric value. σ is tuned per bin to match the channel 3 excess. The 4.69 µm excess then follows from the Planck mix. This attributes the whole channel 3 excess to anisothermality, so it is an upper estimate.
- Relevant literature: Bandfield et al. (2015, Icarus 248, 357–372) derived lunar roughness from Diviner multi-channel anisothermality; Williams et al. (2017) describe the GCP.

## Reproduction

1. Download the four GCP tiles as above into `data/reference/diviner/gcp/`.
2. Run `uv run --no-project --with numpy --with matplotlib python scripts/compare_e1g2_diviner_temperature.py` from the repository root.
