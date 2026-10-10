# Notes

- Reproduction is the same as for [the unit test](../m2-radiance-unit-physics/notes.md), steps 1 and 2. The ignored output `data/derived/e1g2/apparent_reflectance.npy` is float32 (222, 12210, 250).
- Composite in the strip figure: R = 2.05–2.15 µm mean, G = 1.45–1.55 µm, and B = 0.95–1.05 µm, each stretched between its 1st and 99th percentiles. Colors in this composite are relative and must not be read as mineral identification.
- Strip figures plot latitude along x, using the per-line mean latitude of the provisional SLDEM-corrected geometry. The strip is about 18 km wide and about 1,000 km long, so the across-track direction is greatly stretched in the figures.
- Open question: what causes the 1.16/1.30/1.83/1.99 µm steps? Candidates are order-sorting filter boundaries or detector segment gains. Search ISRO IIRS instrument papers (Chowdhury et al. 2020) for the filter layout.
