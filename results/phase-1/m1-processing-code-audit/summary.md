# M1 public processing-code audit

**Status:** Completed as an implementation-reference review; it does not close any calibration or mask gate.

**Source data:** Official IIRS SIS V17 (`docs/ch2_iirs_pds_dp_archive_sis.pdf`, Appendix H, pages 115–126) and public CH2IIRS repository at commit `cd84557b67317aa70cfdd7aa552d701861dc1a7b`.

**Method:** Read the SIS validity definitions and mode table, then inspected the repository README, `ThermalInci.py`, and `TempC.py`. No local science data were changed and no metric was computed.

**Observation:** The SIS explicitly says that only `VALID` bands are valid; `SATURATION`, `OSF`, and `INVALID` are invalid or low-confidence spectral bands. It defines `OSF` as an order-sorting-filter location with less confidence in radiance, and says `INVALID` regions are replaced using neighboring bands except for bands 1–5. This is a spectral-band rule, not a per-pixel quality mask. The SIS identifies the `.oat`, `.oath`, `.lbr`, and `.spm` files as orbit/attitude, orbit/attitude header, lunar libration angle, and Sun-parameter ancillary data. The public thermal-correction plugin documents 256-band radiance/solar-flux inputs and uses bands selected around 4500–4874 nm for its temperature estimate. The inspected routines do not implement an explicit per-pixel fill or saturation mask.

**Limits:** The code is an external research implementation, not an ISRO archive definition. The inspected routines contain hard-coded scaling and correction assumptions and do not document per-pixel validity handling. Do not reuse their scale factors or treat lack of a code mask as proof that the archive has no mask.

**Next gate:** Apply the SIS `VALID` band list when defining spectral analysis inputs. For pixel validity, continue seeking archive/provider guidance and test independent checks against overlapping Level-2/M³ data only after radiance and geometry validation. No mask, reflectance, or correction was produced here.
