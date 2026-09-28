# Research results

Organize results by phase and module. Each module stores a summary, findings, notes, and supporting evidence. This index reports the current M1 results and links to the detailed [project README](../README.md#M1-results-at-a-glance).

## Current status

The M1 modules record the product inventory and initial quality checks. M1 is still in progress. The project has not produced reflectance, a model baseline, or a mineral, hydration, or ice detection. M2 and M3 remain gated by the unresolved items below.

## M1 results

| Work | Result | Evidence and status |
| --- | --- | --- |
| Product inventory | Three matched raw/calibrated pairs: two 2020 E3G2 observations and one 2026 E1G2 observation. | [E1G2 record](phase-1/m1-e1g2-scene/summary.md), [inventory findings](phase-1/m1-inventory/findings.md). |
| Product integrity | The E1G2 pair matches on product metadata. Both ZIP CRC and embedded QUB MD5 checks pass. | [E1G2 findings](phase-1/m1-e1g2-scene/findings.md). |
| Mode validity | E3G2 has no valid 4–5 µm bands. E1G2 bands 226–248 are valid from 4504.1 to 4874.9 nm. | [Band-validity CSV](phase-1/m1-inventory/metrics/band_validity_by_mode.csv), [mode figure](phase-1/m1-inventory/figures/band_validity_by_mode.svg). |
| 2020 E3G2 scans | All values are finite. The `m65` cube has 2,809 zeros and 26 negative band-pixels across valid bands. The `d18` cube has 3,059 zeros and 26 negative band-pixels. | [Per-band CSV](phase-1/m1-inventory/metrics/pilot_radiance_quality_by_band.csv), [quality figure](phase-1/m1-inventory/figures/pilot_radiance_quality_by_band.png). We have not classified zero or negative values as fill. |
| 2026 E1G2 scan and LUT comparison | The calibrated cube has 781,440,000 finite values. Its 222 valid bands contain 4,829 zeros and 42,081 negative band-pixels. Median calibrated/LUT ratio is 1.00375 and median per-band correlation is 0.922. | [Per-band CSV](phase-1/m1-e1g2-scene/metrics/e1g2_radiance_by_band.csv), [audit script](../scripts/analyze_iirs_e1g2_scene.py). This supports internal scale consistency, not independent calibration validation. |
| Saturation and fill gate | 99.878921% of valid-band values meet the threshold under the table's declared unit. Under the alternate mW interpretation, 12 values exceed. No valid-band raw count reaches `dynamic_range`. | [E1G2 findings](phase-1/m1-e1g2-scene/findings.md). The interpretations conflict. We did not create a pixel mask. |
| Geometry | 1,476 sparse points across 246 scan lines cover about 5.47°W–3.50°W and 6.53°S–26.86°N. | [Audit figure](phase-1/m1-e1g2-scene/figures/e1g2_radiance_and_footprint.png). This is coarse low-latitude coverage, not full-resolution geometry. |

### E1G2 audit figure

![E1G2 calibrated radiance medians, calibrated-to-LUT consistency by band, and sparse geolocation grid.](phase-1/m1-e1g2-scene/figures/e1g2_radiance_and_footprint.png)

This figure compares calibrated radiance with the official lookup table and displays the product's sparse geometry. The threshold comparison does not provide a valid saturation mask.

### M1 workflow and gates

```mermaid
flowchart LR
    A[Three matched raw/calibrated pairs] --> B[Read PDS4 labels and verify identity]
    C[Official IIRS archive: SIS, LUT, validity, saturation] --> D[Set mode validity and calibration references]
    B --> E[Check ZIP CRC and QUB MD5]
    D --> F[Compare E3G2 and E1G2 valid bands]
    E --> G[E1G2 pair passes integrity checks]
    F --> H[Scan two 2020 E3G2 calibrated cubes]
    H --> I[All finite; zeros 2809 and 3059; negatives 26 and 26]
    F --> J[Scan matched 2026 E1G2 raw and calibrated cubes]
    G --> J
    J --> K[781440000 calibrated values; all finite]
    K --> L[Compare official LUT: ratio 1.00375; correlation 0.922]
    L --> M[Internal radiance scale consistency supported]
    K --> N[Compare saturation and dynamic-range fields]
    N --> O[Threshold meanings conflict; no mask assigned]
    K --> P[Inspect sparse geometry: 1476 points, low-latitude strip]
    I --> Q[Save CSVs, figures, and findings]
    M --> Q
    O --> Q
    P --> Q
    Q --> R[M1 next: authoritative fill and threshold rules]
    R --> S[Independent radiance validation and full-resolution geometry]
    S --> T[M2 thermal correction and reflectance only after gates pass]
    T --> U[M3 independent tracks, reviewed labels, fixed split]
```

## Current plan

- `phase-1/m1-inventory`: record product metadata, dimensions, checksums, mode validity, coverage, and acquisition gaps.
- `phase-1/m1-e1g2-scene`: audit the matched E1G2 pair, LUT consistency, threshold semantics, and coarse geometry.
- `phase-1/m2-calibration`: establish calibrated units, corrections, masks, and analysis-ready patches after M1 gates pass.
- `phase-1/m3-baselines`: freeze labels and splits, then run physical, clustering, and from-scratch baselines after M2 passes.

Quantitative results must include machine-readable values in `metrics/` and a PNG or SVG figure in `figures/`. Find the M1 audit values and figures in their module directories. No M2 reflectance result or M3 model score exists yet.
