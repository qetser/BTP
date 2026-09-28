---
name: verify
description: Validate IIRS code, documentation, manifests, or scientific outputs with checks suited to the changed artifact.
---

# Verify

Choose checks that test the actual claim. For documentation, check links, paths, contradictory status, and `git diff --check`. For data inventory, compare PDS4 label fields with archive entries, extracted sizes, and checksums. For calibrated products, verify units, masks, correction provenance, and representative spectra. For models, use fixed independent splits, labels, seeds, and task metrics from `docs/m1_m3_plan.md`.

Report what ran, its output, and what remains unverified. Do not run a large suite that does not reduce a concrete risk. A failed scientific quality gate is a finding, not a score to smooth over.
