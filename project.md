# Project charter: IIRS lunar hyperspectral transfer

**Last updated:** 2026-09-28
**Status:** Active, M1–M3 setup

## What this is

A research pipeline to measure whether Earth-pretrained hyperspectral models can transfer to Chandrayaan-2 IIRS lunar observations. The first release must establish trustworthy IIRS data, physical corrections, labels, and from-scratch/classical baselines before foundation-model comparison.

## Why it exists

The proposed transfer study is only interpretable if raw detector counts become validated reflectance and the comparison uses geographically independent evaluation. The four currently available local strips are raw, low-to-mid-latitude scenes. See the [research README](README.md) and [scientific plan](docs/m1_m3_plan.md).

## Who uses it

| User | Need | Project output |
| --- | --- | --- |
| BTP research team | Reproducible, scientifically defensible M1–M3 experiments | Verified inventory, corrected patches, baseline scoreboard |
| Planetary-science reviewers | Traceable observations and calibrated interpretations | Product lineage, quality reports, uncertainty and failure cases |

## Stack decisions

| Layer | Current choice | Reason | Status |
| --- | --- | --- | --- |
| Source data | Chandrayaan-2 IIRS PDS4 products | Primary instrument for the question | Four raw archives local |
| Comparison data | M³ L2, USGS geologic map and spectral library | Cross-check and weak contextual labels | Not yet acquired |
| Processing language | Python | Suitable for chunked scientific I/O and reproducible analysis | Proposed; packages not selected |
| Model framework | Undecided | Select after baseline task and compute budget are fixed | Open |
| Deployment | None | Research pipeline rather than a service | No deploy target |

## Core technical risks

1. **Invalid reflectance** — Raw counts and thermal emission can masquerade as absorption. Mitigation: official calibrated products, published correction chain, and spectral validation.
2. **Weak or leaking labels** — Geologic polygons are coarse and neighboring pixels correlate. Mitigation: reviewed labels, boundary exclusion, orbit/province splits.
3. **Insufficient coverage** — Four current strips do not test polar feasibility or independent generalization. Mitigation: expand geographically distinct IIRS scenes before claims.

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
| 2026-09-28 | Initial charter for M1–M3 | Adapted the supplied setup to the existing IIRS repo |
