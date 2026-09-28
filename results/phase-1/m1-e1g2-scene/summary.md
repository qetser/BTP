# E1G2 candidate acquisition summary

**Status:** Matched E1G2 raw/calibrated product pair verified at archive and label level. Numerical radiance scales, pixel masks, and geometry remain to be validated before M2.

**Source data:** PRADAN IIRS product selection generated 2026-09-28. Raw product: `ch2_iir_nri_20260227T1239538758_d_img_d18.zip`. Listed calibrated counterpart: `ch2_iir_nci_20260227T1239538758_d_img_d18.zip`.

**Method:** Downloaded only the selected raw and matching calibrated ZIPs. Both archives passed ZIP CRC validation. Parsed each PDS4 XML label and streamed each embedded QUB to compare its MD5 with the value declared in the label. Extracted only the calibrated browse PNG for visual context; no cube was extracted or analyzed.

**Observation:** Both labels report start `2026-02-27T12:39:53.8758Z`, stop `2026-02-27T12:50:41.6917Z`, job ID `IIRXXD18CHO2904302NNNN26058141632221_V2_1`, imaging orbit `29042`, dumping orbit `29043`, exposure `e1`, gain `g2`, dimensions `12,210 × 250 × 256`, and band centers spanning 712.3–5009.7 nm. The raw QUB is 1,562,880,000 bytes and matches label MD5 `518420609143e6f119fa50038f22f23f`; the calibrated QUB is 3,125,760,000 bytes and matches label MD5 `b5614f39ec0faa3c136f3dd8c7a13eca`. Calibrated radiance units are labeled `µW/cm**2/sr/µm`. Raw and calibrated ZIP SHA-256 values are recorded in [findings](findings.md).

**Limitations:** Matching labels establish product lineage but do not validate the calibrated radiance unit scale, saturation or fill masks, footprint geometry, temperature retrieval, or thermal correction. No cube values were analyzed and no metric was computed. This is not a reflectance or scientific result.

**Next gate:** Validate representative calibrated radiance distributions and geometry; resolve saturation units and fill/per-pixel masks. Confirm E1G2 band-validity coverage and compare temperature and correction behavior with published and independent references before 3 µm interpretation.

See [detailed findings](findings.md) and [acquisition notes](notes.md).
