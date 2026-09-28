# E1G2 candidate acquisition summary

**Status:** Raw candidate verified as E1G2. Matched calibrated product is listed by PRADAN but has not been downloaded or label-checked.

**Source data:** PRADAN IIRS product selection generated 2026-09-28. Raw product: `ch2_iir_nri_20260227T1239538758_d_img_d18.zip`. Listed calibrated counterpart: `ch2_iir_nci_20260227T1239538758_d_img_d18.zip`.

**Method:** Downloaded only the selected raw ZIP. Checked its ZIP CRC and parsed the product XML directly from the archive. Requested the matching calibrated ZIP separately; PRADAN returned HTTP 302 to sign-in, and no calibrated response was saved.

**Observation:** The raw label gives start time `2026-02-27T12:39:53.8758Z`, exposure `e1`, and gain `g2`. The raw archive is 715,581,464 bytes and passed CRC validation. SHA-256: `b29cc17233780a973224f7f6742230235052b4b0f5f08652eefd45f8140ca8f1`.

**Limitations:** A raw label alone does not establish raw-to-calibrated lineage, radiance units, calibrated checksum, valid-pixel fractions, footprint suitability, or a working thermal correction. No cube values or metrics were computed. This is not a reflectance or scientific result.

**Next gate:** Renew PRADAN access and retrieve only the listed NCI counterpart. Verify its XML identity, exposure/gain, timestamps, dimensions, wavelengths, units, geometry, and checksums against the raw product. Then resolve saturation and pixel masks before any thermal correction.

See [detailed findings](findings.md) and [acquisition notes](notes.md).
