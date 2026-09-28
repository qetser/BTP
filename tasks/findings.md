# Findings

## 2026-09-28 — Local IIRS data and first-phase gates

- Four IIRS ZIP archives and extracted products are available locally. Each raw PDS4 label describes a 256-band `UnsignedLSB2` detector-count cube. Band centers in these labels range from 712.3 to 5009.7 nm. Source: `data/*/data/raw/*/*.xml` and the inventory in [`README.md`](../README.md).
- The four label-corner latitude ranges are approximately 30.9°S to 23.3°N. None is polar. Source: the same PDS4 labels.
- ISRO distinguishes raw and calibrated IIRS products and points to its product guide under `Other Downloads` → `iir.zip`. Source: [PRADAN IIRS FAQ](https://pradan.issdc.gov.in/ch2/faq.xhtml).
- Published IIRS Level-2 work includes thermal correction beyond about 2.5 µm before reflectance interpretation. Source: [Chauhan et al. 2025](https://onlinelibrary.wiley.com/doi/abs/10.1111/maps.70037).
- The USGS unified lunar map is a 1:5M geologic-unit map and cannot be assumed to provide per-pixel mineral abundance labels. Source: [USGS map release](https://astrogeology.usgs.gov/search/map/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2/).

## Unresolved

- Whether corresponding calibrated products are downloadable for all four scenes.
- Which high-confidence labels and additional tracks can support M3 evaluation.
- Whether polar IIRS shadowed observations have enough indirect-light signal for a 3 µm measurement.
