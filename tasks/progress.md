# Progress

## 2026-09-28 — Official IIRS archive inspected

- Received `data/pradan/iir.zip`, verified all ZIP entries, and recorded SHA-256 `5afe64c3efe445e6d0334e8a374756ecab45698494dcee0d19616bf5dcb80720`. The archive contains the 149-page SIS V17, LUTs, saturation tables, solar flux, and band-validity workbook. The separate user guide is absent.
- The SIS confirms Level 1 calibrated radiance and places thermal and photometric correction in Level 2 processing. Both pilots are `E3G2`; the official mask has no valid 4–5 µm bands for that mode.
- Saved source band flags in `results/phase-1/m1-inventory/metrics/band_validity_by_mode.csv` and a plot in `figures/band_validity_by_mode.svg`.
- Next work: validate each cube's unit scale and pixel masks, then assess a suitable mode or method for thermal correction. No reflectance claim was made.

## 2026-09-28 — M1 pilot dictionary and guide access check

- Corrected the M1 summary to reflect completed extraction, integrity checks, and XML pairing.
- Added a provisional data dictionary from the four active PDS4 labels. Both calibrated labels call their cubes radiance spectral images; their declared units differ by a factor of 1000 in prefix.
- Confirmed the official `iir.zip` guide/SIS is listed by the PRADAN IIRS FAQ, while its `Other Downloads` page redirects unauthenticated requests to ISSDC sign-in. No guide-based calibration, fill, saturation, or band-validity claim was made.
- Next work: obtain the guide through authorized access, validate the unit conventions and representative values, then select independent scenes. M2 correction remains gated.

## 2026-09-28 — Local tooling removed from Git

- Kept `.agents/skills` and `.codex` on disk while removing them from Git tracking.
- Added ignore rules and corrected the setup guide to show these are local-only files.

## 2026-09-28 — Codex setup

- Adapted the supplied project workflow to Codex's local instruction, skill, hook, and custom-agent locations.
- Created a charter, current task plan, findings, lessons, changelog, error registry, improvement ledger, research prompt, and observation checklist.
- Kept `AGENTS.md` and `codex.md` local and ignored. Added a Git commit-message check for the no-co-author rule.
- Next work: create and verify an M1 manifest for the four raw scenes, then obtain the official IIRS product guide and calibrated counterparts.

## 2026-09-28 — Research result protocol

- Added a phase and module result structure under `results/`.
- Required concise summaries, findings, and notes for every module.
- Required machine-readable metric values plus PNG or SVG figures whenever metrics or graphs are produced.
- No metric figures were created because M1 inventory metrics have not yet been computed.
- Active next step: finish the M1 manifest and integrity checks for the four local scenes.
- M1 manifest and integrity verification completed for all four local scenes. The next M1 unit is product-guide and calibrated-counterpart identification, followed by acquisition of independent scenes.
- The supplied PRADAN URL list was checked before download. It contains no exact timestamp match for the four raw scenes; the interrupted partial transfer was removed. A new PRADAN selection is required.
- HyperFree and HyperSIGMA are now explicitly scheduled for Phase 4 (M4), after the M1–M3 quality gates. M5 adaptation and M6 scientific tasks follow reproducible M4 transfer results.
- Replaced the old `data/` contents with four selected pilot archives: raw and calibrated pairs for `20200208T1245274109_d_img_d18` and `20200208T0057589143_d_img_m65`. All four downloads completed and passed Python ZIP integrity checks. Next: extract and inspect their XML labels.
- Extracted all four pilot archives and regenerated the active manifest. Both raw-to-calibrated pairs match on timestamp, job ID, orbit, dimensions, and wavelengths. The calibrated unit strings differ by product and are now recorded as an M2 conversion gate.

## Earlier work

- Researched M1–M3, documented scientific gates in `docs/m1_m3_plan.md`, and inventoried four raw IIRS strips.
- Extracted all four ZIP archives locally and checked the expected file counts and sizes.
- Pushed the initial documentation to `main`; mission data remain untracked.
