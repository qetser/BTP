# Project charter: IIRS lunar hyperspectral transfer

**Last updated:** 2026-10-08
**Status:** Active, M1–M3 setup

## What this is

A research pipeline to measure whether Earth-pretrained hyperspectral models can transfer to Chandrayaan-2 IIRS lunar observations. The first release must establish trustworthy IIRS data, physical corrections, labels, and from-scratch/classical baselines before foundation-model comparison.

## Why it exists

The proposed transfer study is only interpretable if raw detector counts become validated reflectance and the comparison uses geographically independent evaluation. The local pilot now contains three matched low-latitude raw/calibrated pairs: two 2020 E3G2 strips and one 2026 E1G2 strip. E1G2 and E3G2 LUT comparisons are internal stage checks only. The V6 guide documents destriping and radiance post-processing after LUT correction and attributes differences from direct LUT calculations to those steps; the exact E3G2 ratio has not been reproduced. The guide states calibrated radiance units as mW, while the matched E1G2 PDS4 label states µW, so the scale remains unresolved. Published alternatives now include a normalized IIRS–M³ shape comparison, an Apollo 16/RELAB 62231 empirical-line reflectance route requiring another scene, and Diviner temperature comparison matched by ground control points and acquisition time. None resolves current-scene Level-1 units or masks. Saturation and fill semantics and independent scale validation remain open. A WAC tie grid failed the candidate relative-registration limits. A subsequent SLDEM2015 hillshade match passed those limits with 34 held-out ties (median 0.375 px, p95 1.487 px). Its training-fitted offset field has been applied to a separate sparse-geometry candidate and checked against held-out ties; this fit-consistency result does not establish absolute geolocation. A footprint query identified five M³ Level-2 candidates, and a sparse geometry-grid screen ranks one candidate for pixel-coverage review. Actual common valid-pixel coverage remains unknown. ODE label retrieval succeeded, but binary retrieval is currently blocked: the JPL host fails strict TLS validation and the documented USGS PDS4 path returns 404. See the [E3G2 audit](results/phase-1/m1-e3g2-lineage-check/summary.md), [M1 gate follow-up](results/phase-1/m1-gate-followup-20261010/summary.md), [WAC tie record](results/phase-1/m1-wac-2d-grid/summary.md), [SLDEM hillshade record](results/phase-1/m1-sldem-hillshade/summary.md), [SLDEM candidate correction](results/phase-1/m1-sldem-correction-candidate/summary.md), [reference-data record](results/phase-1/m1-reference-data/summary.md), [research README](README.md), and [scientific plan](docs/m1_m3_plan.md).

## Who uses it

| User | Need | Project output |
| --- | --- | --- |
| BTP research team | Reproducible, scientifically defensible M1–M3 experiments | Verified inventory, corrected patches, baseline scoreboard |
| Planetary-science reviewers | Traceable observations and calibrated interpretations | Product lineage, quality reports, uncertainty and failure cases |

## Stack decisions

| Layer | Current choice | Reason | Status |
| --- | --- | --- | --- |
| Source data | Chandrayaan-2 IIRS PDS4 products | Primary instrument for the question | Two complete 2020 pairs; one 2026 E1G2 pair verified by labels and checksums; LUT-stage comparison recorded; independent validation, geometry, and masks pending |
| Comparison data | LROC WAC, M³ L2, USGS geologic map and spectral library | Spatial registration, cross-checks, and weak contextual labels | WAC crop acquired; preliminary browse-scale tie residuals computed; M³ candidates label-reviewed; usable M³ overlap remains unknown |
| Processing language | Python | Suitable for chunked scientific I/O and reproducible analysis | Proposed; packages not selected |
| Model framework | Undecided | Select after baseline task and compute budget are fixed | Open |
| Deployment | None | Research pipeline rather than a service | No deploy target |

## Core technical risks

1. **Invalid reflectance** — Raw counts and thermal emission can masquerade as absorption. Mitigation: official calibrated products, published correction chain, and spectral validation.
2. **Weak or leaking labels** — Geologic polygons are coarse and neighboring pixels correlate. Mitigation: reviewed labels, boundary exclusion, orbit/province splits.
3. **Insufficient coverage** — Three current low-latitude strips do not test polar feasibility or independent generalization. Mitigation: expand geographically distinct IIRS scenes before claims.
4. **Mode-limited thermal evidence** — The active `E3G2` strips lack valid 4–5 µm bands under the official mask. The matched `E1G2` pair has valid 4504.1–4874.9 nm mode bands. Applying saturation fields directly flags nearly all values in both modes, while raw counts almost never meet `Dynamic_Range`. The V6 guide documents destriping and radiance post-processing after LUT correction and attributes differences from direct LUT calculations to those steps; the observed E3G2 ratio has not been reproduced. The guide states calibrated units as mW, while the E1G2 PDS4 label states µW, leaving the numeric scale unresolved. Saturation and fill semantics also remain unresolved. Published alternatives include normalized IIRS–M³ spectral-shape comparison, Apollo 16/RELAB 62231 empirical-line reflectance on a separate scene, and Diviner temperature checks matched by ground control points and acquisition time. These do not resolve current-scene units or pixel masks. Mitigation: pursue the PDS M³ overlap check, identify an Apollo 16 IIRS strip for the published reflectance route, and retain all unit/mask/thermal gates before interpretation. See [M1 gate follow-up](results/phase-1/m1-gate-followup-20261010/summary.md), [sample and table results](results/phase-1/m1-saturation-sample/summary.md), and [E3G2 lineage results](results/phase-1/m1-e3g2-lineage-check/summary.md).

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
| 2026-09-29 | Screened five M³ footprints against sparse E1G2 geometry | Rank a candidate before acquiring large images; valid-pixel overlap remains open |
| 2026-09-29 | Matched full-resolution E1G2 band 40 to WAC | Residuals vary and are larger than the browse result; full-resolution geolocation remains unvalidated |
| 2026-09-29 | Compared E1G2 browse image with WAC on held-out spatial tie windows | Initial residuals are promising but provisional; full-resolution geolocation remains open |
| 2026-09-29 | Acquired footprint-sized WAC crop by TIFF byte ranges | Prepare the independent geometry reference; registration residuals remain unmeasured |
| 2026-09-29 | Reviewed the five candidate M³ L2 labels | Product dimensions and special-pixel values are documented; usable overlap still needs checking |
| 2026-09-29 | Queried footprint-intersecting M³ Level-2 candidates and defined WAC registration path | Five orbit-1080 M³ labels returned; geometry validation still requires held-out residuals |
| 2026-10-08 | Compared full-resolution E1G2 morphology with SLDEM2015 hillshade | Fresh held-out relative-registration criteria pass; absolute geolocation remains provisional |
| 2026-10-08 | Applied the training-fitted SLDEM relative offset model to a separate sparse geometry copy | Candidate correction validated on existing held-out morphology ties; absolute geolocation remains provisional |
| 2026-09-28 | Added literature-backed E1G2 acquisition target and temperature-uncertainty gate | Published thermal work and the official mode table identify valid 4.5–4.9 µm bands in E1G2 |
| 2026-09-28 | Confirmed the PRADAN scene table requires sign-in and updated the acquisition flow | The public Browse and Download route redirects to account authentication |
| 2026-09-28 | Recorded the supplied V6 product guide and verified a raw E1G2 candidate label | The guide clarifies filename fields; the raw XML reports exposure e1 and gain g2 |
| 2026-09-28 | Verified the matched 2026 E1G2 raw/calibrated pair and cube checksums | Both XML labels match on pair identity and mode; embedded QUB MD5 values match |
| 2026-09-28 | Audited the E1G2 cube against saturation and geometry metadata | The threshold comparison conflicts with the paired raw dynamic-range field; no mask was assigned |
| 2026-09-28 | Reviewed official IIRS SIS and mode validity | Identify the `E3G2` thermal-correction constraint |
| 2026-09-28 | Updated active pilot to two raw/calibrated pairs and recorded the guide access gate | Keep the charter aligned with the verified local inventory |
| 2026-09-28 | Initial charter for M1–M3 | Adapted the supplied setup to the existing IIRS repo |
