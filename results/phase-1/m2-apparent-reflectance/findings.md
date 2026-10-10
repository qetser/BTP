# Findings

- The first IIRS apparent-reflectance values for this project are physically plausible: the median at 1.5 µm is 0.098, and the dark-to-bright contrast is about 1.9×.
- Spectral steps at about 1.16, 1.30, 1.83, 1.99, and 3.4 µm appear in every pixel class. Treat them as instrument artifacts until a provider or literature source explains them. They limit band-shape interpretation unless they are removed. The M3 module applies a scene-derived polishing step for this reason. CH2IIRS applies a similar empirical "polishing" coefficient.
- Column striping is small (1.4% relative column-median spread at 1.5 µm) but visible in ratio products. One detector column near sample 155 is intermittently bad at the first valid bands.
- Short horizontal white segments in the maps are pixels that fail the finite-and-positive test. They form 0.39% of pixels.
- Failed or open gates recorded as findings:
  - Absolute reflectance scale: no independent validation yet.
  - Photometric correction: not applied.
  - Junction artifacts: not explained by the SIS or guide text available here.
