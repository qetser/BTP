# M1 literature review findings

- **Thermal mode:** Verma et al. (2022) state that their Level 1 radiance data use exposure period 1, gain 2 (E1G2), and infrared bands from 2.5–5 µm for thermal correction. The official local workbook marks E1G2 bands 226–248 (4504.1–4874.9 nm) valid. This directly identifies the next candidate mode.
- **Temperature sensitivity:** Gou et al. (2026) report that temperatures from 4504–4875 nm are more stable than those from 2566–2937 nm. Their example reports a 14.39% reflectance difference at 3156 nm for a 4 K temperature difference. M2 must report temperature uncertainty and its effect on corrected reflectance.
- **Existing correction chain:** Chauhan et al. (2025) describe thermal correction beyond 2.5 µm, apparent reflectance, empirical-line adjustment, standard geometry, and M³ comparison. The abstract describes the resulting corrected range as 0.8–3.3 µm. This provides a recent processing reference but not a substitute for local quality checks.
- **Photometric correction scope:** Bose et al. (2024) derive photometrically corrected IIRS reflectance from calibrated radiance over 800–2000 nm and compare it with M³. Its stated spectral scope does not validate thermal correction near 3 µm.
- **Alternative temperature evidence:** Chauhan et al. (2021) report physics-based thermal correction using co-located temperature measurements. This is a possible independent reference path, but it does not establish that an E3G2-only spectrum can support the longwave temperature retrieval.
- **Implementation reference:** The public CH2IIRS repository says its thermal and phase tools follow the 2022 and 2025 papers. Its code must be audited for units, mode validity, masks, assumptions, and license before any reuse.
- **Local validity check:** In `band_validity_by_mode.csv`, all E1G2 bands from 226 through 248 are flagged valid, with centers from 4504.1 through 4874.9 nm. E3G2 marks these channels invalid. This is instrument metadata, not a per-pixel quality mask.
- **Decision:** Prioritize an E1G2 pair for the thermal pilot. Keep the saturation-unit conflict and pixel mask unresolved. Do not start 3 µm reflectance processing until unit, mask, and correction validation pass.

## Sources

- [Verma et al. 2022, Icarus](https://doi.org/10.1016/j.icarus.2022.115075)
- [Gou et al. 2026, Advances in Space Research](https://doi.org/10.1016/j.asr.2026.06.090)
- [Chauhan et al. 2025, Meteoritics & Planetary Science](https://doi.org/10.1111/maps.70037)
- [Bose et al. 2024, Advances in Space Research](https://doi.org/10.1016/j.asr.2023.12.019)
- [Chauhan et al. 2021, Current Science](https://doi.org/10.18520/cs/v121/i3/391-401)
- [ISRO PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml)
- [CH2IIRS processing repository](https://github.com/prabhakaralok/CH2IIRS)
