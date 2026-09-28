# M1–M3 observation checklist

Record measured values alongside the run, source IDs, code revision, and artifact path. `Not measured` is an honest initial state. This is an evidence checklist, not a dashboard claiming results.

| Gate | Measure | Current state |
| --- | --- | --- |
| M1 integrity | Archives and extracted cubes with verified size and checksum | Size checked for four scenes; checksums not yet recorded |
| M1 lineage | Raw scenes paired with calibrated product ID and units | Not measured |
| M1 coverage | Independent orbits/provinces and polar scenes in train/validation/test | Four low-to-mid-latitude raw scenes; split not fixed |
| M2 quality | Invalid-pixel/band fraction, stripe residual, geometry and thermal-correction error | Not measured |
| M2 comparison | Matched IIRS–M³ and official L2 spectral differences | Not measured |
| M3 labels | Reviewed class support and boundary exclusions per split | Not measured |
| M3 baselines | Held-out macro-F1, balanced accuracy, per-class IoU where labels support them | Not measured |
| M3 reliability | Seed spread, track-level uncertainty, and failure examples | Not measured |

Update this table only from a reproducible quality report or run. Refer to `docs/m1_m3_plan.md` for methods and gates.
