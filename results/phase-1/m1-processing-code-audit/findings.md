# Findings

- The authoritative SIS makes the mode-dependent band-validity interpretation explicit. Only bands tagged `VALID` are valid; `SATURATION`, `OSF`, and `INVALID` bands are excluded from use as valid spectral measurements.
- The validity table already saved in `m1-inventory/metrics/band_validity_by_mode.csv` gives 222 valid E1G2 bands and 127 valid E3G2 bands. E1G2 bands 226–248 span 4504.1–4874.9 nm; these are the current longwave temperature-estimation candidates.
- This table operates at band level. It does not classify individual pixels within a band, so it does not answer the unresolved fill and pixel-saturation question.
- CH2IIRS provides a reproducible public implementation path for later algorithm review, but its inspected temperature and reflectance routines contain no explicit per-pixel fill or saturation masking. It is not authoritative for interpreting the archive fields.
- The SIS identifies the recurring `.oat`, `.oath`, `.lbr`, and `.spm` ancillary files as orbit/attitude, orbit/attitude header, lunar libration angle, and Sun-parameter data. Their presence does not provide the missing pixel mask.
- Failed quality gate: the public code audit found no validated per-pixel mask rule. No pixel mask was inferred.
