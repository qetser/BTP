# M1–M3 observation checklist

Record measured values alongside the run, source IDs, code revision, and artifact path. `Not measured` is an honest initial state. This is an evidence checklist, not a dashboard claiming results. Module records live under [`results/`](../results/).

| Gate | Measure | Current state |
| --- | --- | --- |
| M1 integrity | Archives and extracted cubes with verified size and checksum | Historical four-scene raw inventory passed. Current four pilot ZIPs passed HTTP and Python ZIP integrity checks; extraction and label checks remain pending. Evidence: `results/phase-1/m1-inventory/summary.md` |
| M1 lineage | Raw scenes paired with calibrated product ID and units | **Measured for three pairs:** exact timestamp, job ID, orbit, dimensions, and wavelengths match. The 2020 E3G2 pairs' units are in `results/phase-1/m1-inventory/pilot_lineage.md`; 2026 E1G2 radiance, threshold, and geometry QA are in `results/phase-1/m1-e1g2-scene/`. |
| M1 coverage | Independent orbits/provinces and polar scenes in train/validation/test | Two low-latitude pilot pairs from 2020-02-08; split not fixed and no polar coverage |
| M2 quality | Invalid-pixel/band fraction, stripe residual, geometry and thermal-correction error | Not measured |
| M2 comparison | Matched IIRS–M³ and official L2 spectral differences | Not measured |
| M3 labels | Reviewed class support and boundary exclusions per split | Not measured |
| M3 baselines | Held-out macro-F1, balanced accuracy, per-class IoU where labels support them | Not measured |
| M3 reliability | Seed spread, track-level uncertainty, and failure examples | Not measured |

Update this table only from a reproducible quality report or run. Refer to `docs/m1_m3_plan.md` for methods and gates.
