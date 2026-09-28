# M1 literature review summary

**Status:** Targeted review complete for the next acquisition and processing decision. The literature and official mode table identify E1G2 as the preferred thermal pilot mode. M1 acquisition and validation gates remain open.

**Scope:** Selected Chandrayaan-2 IIRS radiance, thermal correction, reflectance, and photometric correction studies. This is an initial targeted review, not a systematic review.

**Sources:** Primary papers from 2021, 2022, 2024, 2025, and 2026; the official PRADAN IIRS FAQ; the local official SIS and band-validity workbook; and a public GPL-3.0 processing repository.

**Method:** Search paper abstracts and publisher/ISRO pages for IIRS thermal correction, E1G2 use, reflectance retrieval, and validation. Inspect publisher article content for mode, wavelength, and sensitivity details. Compare reported wavelength ranges with the local official mode-validity CSV.

**Main observation:** The 2022 thermal-correction study uses E1G2 and 2.5–5 µm. The local official workbook marks E1G2 bands 226–248 (4504.1–4874.9 nm) valid. A 2026 study reports strong reflectance sensitivity to temperature error. E1G2 is therefore a supported acquisition target, but not yet a validated correction.

**Limitations:** The review does not resolve the saturation-table unit conflict, confirm cube fill rules, identify an exact downloadable E1G2 product, or validate a thermal correction on local data. A live read-only check of the public PRADAN browse route redirected to sign-in; the scene table is not publicly visible. Some full texts are not openly available. The paper-index search had weak coverage for this specialized planetary-science literature, so publisher and official pages were also searched.

**Next gate:** Use authorized PRADAN access to select and acquire a matched E1G2 raw/calibrated pair. Verify its labels, mode, units, validity, checksums, and footprint. Resolve unit and mask rules before correction. Compare corrected temperature and reflectance with the published method and independent references.

See the [initial gap matrix](../../../docs/gap_matrix.md) and detailed [findings](findings.md).
