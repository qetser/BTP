# M1 literature review findings

- **Thermal mode:** Verma et al. (2022) state that their Level 1 radiance data use exposure period 1, gain 2 (E1G2), and infrared bands from 2.5–5 µm for thermal correction. The official local workbook marks E1G2 bands 226–248 (4504.1–4874.9 nm) valid. This directly identifies the next candidate mode.
- **Temperature sensitivity:** Gou et al. (2026) report that temperatures from 4504–4875 nm are more stable than those from 2566–2937 nm. Their example reports a 14.39% reflectance difference at 3156 nm for a 4 K temperature difference. M2 must report temperature uncertainty and its effect on corrected reflectance.
- **Existing correction chain:** Chauhan et al. (2025) describe thermal correction beyond 2.5 µm, apparent reflectance, empirical-line adjustment, standard geometry, and M³ comparison. The abstract describes the resulting corrected range as 0.8–3.3 µm. This provides a recent processing reference but not a substitute for local quality checks.
- **Photometric correction scope:** Bose et al. (2024) derive photometrically corrected IIRS reflectance from calibrated radiance over 800–2000 nm and compare it with M³. Its stated spectral scope does not validate thermal correction near 3 µm.
- **Alternative temperature evidence:** Chauhan et al. (2021) report physics-based thermal correction using co-located temperature measurements. This is a possible independent reference path, but it does not establish that an E3G2-only spectrum can support the longwave temperature retrieval.
- **Implementation reference:** The public CH2IIRS repository says its thermal and phase tools follow the 2022 and 2025 papers. Its code must be audited for units, mode validity, masks, assumptions, and license before any reuse.
- **Local validity check:** In `band_validity_by_mode.csv`, all E1G2 bands from 226 through 248 are flagged valid, with centers from 4504.1 through 4874.9 nm. E3G2 marks these channels invalid. This is instrument metadata, not a per-pixel quality mask.
- **Decision:** The matched 2026-02-27 E1G2 pair has now been acquired and verified by XML identity and checksums. It is a candidate thermal pilot, not a validated correction. Its radiance unit is declared and the LUT check supports internal consistency, but independent validation, saturation-table application, fill rules, geometry registration, and pixel masks remain open. Do not start 3 µm reflectance processing until those and correction checks pass.

## 2026-10-03 — Check published evidence on saturation and fill semantics

- **2020 instrument characterization:** Chowdhury et al. describe laboratory tests from 0.8–2.5 µm and 2.5–5 µm. The tests characterize count-to-radiance response, linearity, noise, and saturation radiance. They report 14-bit quantization. The paper does not define fill values or pixel masks for archived Level-1 cubes. ([Current Science, 2020](https://doi.org/10.18520/cs/v118/i3/368-375))
- **2021 Level-1 processing:** Chauhan et al. describe Level-1 radiance products as dark-noise corrected. Their thermal method uses longwave IIRS radiance. It does not specify saturation-table use or fill encoding. ([Current Science, 2021](https://doi.org/10.18520/cs/v121/i3/391-401))
- **2023 in-orbit check:** The IIRS team reports that deep-space observations support dark calibration and dark-offset removal. The conference paper does not define fill values or Level-1 saturation masks. ([LPSC 2023 abstract 1572](https://www.hou.usra.edu/meetings/lpsc2023/pdf/1572.pdf))
- **2025 raw-count recalibration:** Laferriere and Bramson use the ISRO non-uniformity LUT. They then convert linearized Level-0 data to radiance using saturation radiance and CCD dynamic range. Their radiance differs from ISRO Level 1, especially around order-sorting filters and beyond 4 µm. They attribute some differences to omitted order-sorting-filter adjustments and keystone correction. This shows that both fields can enter a raw-count calibration path. It does not establish the Level-1 threshold test, a saturation mask, or fill encoding. Their low-radiance exclusion selects shadowed pixels for thermal analysis. It does not define instrument fill. ([LPSC 2025 abstract 1644](https://www.hou.usra.edu/meetings/lpsc2025/pdf/1644.pdf))
- **Other processing papers:** Verma et al. (2022) and Chauhan et al. (2025) describe thermal and reflectance processing from Level-1 radiance, but the reviewed text does not document the archive's saturation-table application or fill constants. A 2025 preprint on IIRS/WAC registration says it masks invalid pixels, but does not define how it identifies them. This preprint does not resolve the local cube's mask semantics. ([Bose et al., 2025 preprint](https://doi.org/10.20944/preprints202511.1090.v1))
- **Assessment:** The 2025 recalibration abstract makes it plausible that `Saturation` and `Dynamic_Range` are paired calibration inputs, not independent Level-1 pixel cutoffs. This is an inference from the abstract, not an official interpretation. Do not apply that inference to the E1G2 cube. The existing result remains: 99.878921% of valid-band Level-1 values meet the declared radiance value, while paired raw counts do not reach `Dynamic_Range`; the calibrated label declares no missing-value constant. No mask can be assigned from this literature review.

## 2026-10-08 — Check public official guidance

- The [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml) directs users to the IIRS SIS and data product guide. Its public text gives no Level-1 saturation-mask or cube fill rule.
- ISRO's [public Chandrayaan-2 science and processing description](https://www.isro.gov.in/media_isro/pdf/science/science_results_from_ch.pdf) describes Level 1 as radiometrically corrected, geometrically tagged radiance, with thermal and photometric correction in Level 2. It does not specify application of the saturation or dynamic-range fields to Level-1 pixels, or state a fill encoding.
- The [Laferriere and Bramson LPSC 2025 abstract](https://www.hou.usra.edu/meetings/lpsc2025/pdf/1644.pdf) describes using the ISRO LUT, saturation radiance, and detector dynamic range to recalibrate linearized Level-0 counts. It reports differences from archived Level 1, including effects from omitted order-sorting-filter adjustments and keystone correction. It does not document the archived Level-1 mask or fill rules.
- **Gate result:** No authoritative pixel mask or fill rule found in the checked public sources. Do not infer one from the raw-count recalibration method. Keep calibration and mask gates open.

## Sources

- [Verma et al. 2022, Icarus](https://doi.org/10.1016/j.icarus.2022.115075)
- [Gou et al. 2026, Advances in Space Research](https://doi.org/10.1016/j.asr.2026.06.090)
- [Chauhan et al. 2025, Meteoritics & Planetary Science](https://doi.org/10.1111/maps.70037)
- [Bose et al. 2024, Advances in Space Research](https://doi.org/10.1016/j.asr.2023.12.019)
- [Chauhan et al. 2021, Current Science](https://doi.org/10.18520/cs/v121/i3/391-401)
- [ISRO PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml)
- [CH2IIRS processing repository](https://github.com/prabhakaralok/CH2IIRS)
- [Chowdhury et al. 2020, IIRS instrument and radiometric performance](https://doi.org/10.18520/cs/v118/i3/368-375)
- [Laferriere and Bramson, LPSC 2025 abstract 1644](https://www.hou.usra.edu/meetings/lpsc2025/pdf/1644.pdf)
- [Vijayasree et al., LPSC 2023 abstract 1572](https://www.hou.usra.edu/meetings/lpsc2023/pdf/1572.pdf)
- [Bose et al. 2025, SIFT-based IIRS/WAC registration preprint](https://doi.org/10.20944/preprints202511.1090.v1)
