# M1 literature review summary

**Status:** Targeted review complete for the acquisition decision. Literature and official mode validity identify E1G2 as a candidate thermal mode. Its matched scene is now acquired, but the full-cube audit failed the saturation-threshold gate, so E1G2 is not yet a validated processing input.

**Scope:** Selected Chandrayaan-2 IIRS radiance, thermal correction, reflectance, and photometric correction studies. This is an initial targeted review, not a systematic review.

**Sources:** Primary papers from 2021, 2022, 2024, 2025, and 2026; the official PRADAN IIRS FAQ; the local official SIS and band-validity workbook; and a public GPL-3.0 processing repository.

**Method:** Search paper abstracts and publisher/ISRO pages for IIRS thermal correction, E1G2 use, reflectance retrieval, and validation. Inspect publisher article content for mode, wavelength, and sensitivity details. Compare reported wavelength ranges with the local official mode-validity CSV.

**Main observation:** The 2022 thermal-correction study uses E1G2 and 2.5–5 µm. The local official workbook marks E1G2 bands 226–248 (4504.1–4874.9 nm) valid. A 2026 study reports strong reflectance sensitivity to temperature error. E1G2 is therefore a supported acquisition target, but not yet a validated correction.

**Limitations:** The literature review did not resolve saturation-table semantics or cube fill rules, provide independent radiometric validation, or validate a thermal correction on local data. A subsequent authenticated PRADAN selection produced a matched E1G2 pair, documented in the [acquisition record](../m1-e1g2-scene/summary.md). A live read-only check of the public PRADAN browse route redirected to sign-in; the scene table is not publicly visible without authentication. Some full texts are not openly available. The paper-index search had weak coverage for this specialized planetary-science literature, so publisher and official pages were also searched.

**Next gate:** Resolve saturation-table semantics and cube fill/per-pixel validity rules for the acquired pair; validate radiance scale independently and review full-resolution geometry. Only after those gates pass should the published thermal method be tested against independent temperature and reflectance references.

See the [initial gap matrix](../../../docs/gap_matrix.md) and detailed [findings](findings.md).
