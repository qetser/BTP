# Project charter: IIRS lunar hyperspectral transfer

**Last updated:** 2026-09-28
**Status:** Active, M1–M3 setup

## What this is

A research pipeline to measure whether Earth-pretrained hyperspectral models can transfer to Chandrayaan-2 IIRS lunar observations. The first release must establish trustworthy IIRS data, physical corrections, labels, and from-scratch/classical baselines before foundation-model comparison.

## Why it exists

The proposed transfer study is only interpretable if raw detector counts become validated reflectance and the comparison uses geographically independent evaluation. The local pilot now contains three matched low-latitude raw/calibrated pairs: two 2020 E3G2 strips and one 2026 E1G2 strip. The E1G2 LUT comparison supports the numeric radiance scale internally. Saturation and fill semantics, independent scale validation, and full-resolution geometry remain open. See the [research README](README.md) and [scientific plan](docs/m1_m3_plan.md).

## Who uses it

| User | Need | Project output |
| --- | --- | --- |
| BTP research team | Reproducible, scientifically defensible M1–M3 experiments | Verified inventory, corrected patches, baseline scoreboard |
| Planetary-science reviewers | Traceable observations and calibrated interpretations | Product lineage, quality reports, uncertainty and failure cases |

## Stack decisions

| Layer | Current choice | Reason | Status |
| --- | --- | --- | --- |
| Source data | Chandrayaan-2 IIRS PDS4 products | Primary instrument for the question | Two complete 2020 pairs; one 2026 E1G2 pair verified by labels and checksums; internal LUT scale check passed; independent validation, geometry, and masks pending |
| Comparison data | M³ L2, USGS geologic map and spectral library | Cross-check and weak contextual labels | Not yet acquired |
| Processing language | Python | Suitable for chunked scientific I/O and reproducible analysis | Proposed; packages not selected |
| Model framework | Undecided | Select after baseline task and compute budget are fixed | Open |
| Deployment | None | Research pipeline rather than a service | No deploy target |

## Core technical risks

1. **Invalid reflectance** — Raw counts and thermal emission can masquerade as absorption. Mitigation: official calibrated products, published correction chain, and spectral validation.
2. **Weak or leaking labels** — Geologic polygons are coarse and neighboring pixels correlate. Mitigation: reviewed labels, boundary exclusion, orbit/province splits.
3. **Insufficient coverage** — Three current low-latitude strips do not test polar feasibility or independent generalization. Mitigation: expand geographically distinct IIRS scenes before claims.
4. **Mode-limited thermal evidence** — The active `E3G2` strips lack valid 4–5 µm bands under the official mask. The matched `E1G2` pair is acquired and has valid 4504.1–4874.9 nm mode bands, and its LUT comparison supports internal radiance-scale consistency. The official saturation XML declares units of µW/cm²/sr/µm and dynamic range in counts, but applying those fields conflicts with the paired cube values. Mitigation: clarify field application and fill rules, validate radiance scale independently and register geometry against a reference, then validate thermal correction before 3 µm interpretation.

## Version 1 definition

Version 1 is M1–M3: a verified scene manifest; an analysis-ready reflectance patch set with masks and provenance; a reviewed limited label set; and a held-out scoreboard for physical, clustering, and from-scratch baselines. The acceptance gates are in `docs/m1_m3_plan.md`. Later M4–M7 transfer, self-supervised adaptation, abundance maps, and polar ice claims remain future phases.

## Working preferences

- Commit verified logical units and keep mission data untracked.
- Use direct evidence and state uncertainty in scientific conclusions.
- Role: implementation and scientific review partner (inferred from prior requests; confirm if different).
- Preferred testing style, review cadence, and compute budget: not yet specified.
- No Claude or Codex co-author attribution anywhere.

## Change log

| Date | Change | Reason |
| --- | --- | --- |
| 2026-09-28 | Added literature-backed E1G2 acquisition target and temperature-uncertainty gate | Published thermal work and the official mode table identify valid 4.5–4.9 µm bands in E1G2 |
| 2026-09-28 | Confirmed the PRADAN scene table requires sign-in and updated the acquisition flow | The public Browse and Download route redirects to account authentication |
| 2026-09-28 | Recorded the supplied V6 product guide and verified a raw E1G2 candidate label | The guide clarifies filename fields; the raw XML reports exposure e1 and gain g2 |
| 2026-09-28 | Verified the matched 2026 E1G2 raw/calibrated pair and cube checksums | Both XML labels match on pair identity and mode; embedded QUB MD5 values match |
| 2026-09-28 | Audited the E1G2 cube against saturation and geometry metadata | The threshold comparison conflicts with the paired raw dynamic-range field; no mask was assigned |
| 2026-09-28 | Reviewed official IIRS SIS and mode validity | Identify the `E3G2` thermal-correction constraint |
| 2026-09-28 | Updated active pilot to two raw/calibrated pairs and recorded the guide access gate | Keep the charter aligned with the verified local inventory |
| 2026-09-28 | Initial charter for M1–M3 | Adapted the supplied setup to the existing IIRS repo |
