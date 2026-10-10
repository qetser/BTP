# Notes

- Download, 2026-10-10: the product page <https://astrogeology.usgs.gov/search/map/unified_geologic_map_of_the_moon_1_5m_2020> links the GIS zip at `https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2.zip`. The older `astropedia.astrogeology.usgs.gov/download/...` path returned nothing. The zip was extracted with Python `zipfile` to `data/reference/usgs_unified_geology/extracted/` (297 MB). Both are ignored by Git.
- Zip contents used: `Lunar_GIS/Shapefiles/GeoUnits.shp` (attributes `FIRST_Unit` = unit code, `FIRST_Un_1` = age, `FIRST_Un_2` = map unit description, `AREA_GEO`), the unit names in `Symbol_LayerDefinitions/Unified_Geologic_Map_of_the_Moon_DOMU_descriptions.csv`, and the official colours in `GeologyUnit_colors.csv`. The zip also holds a file geodatabase with the same layers.
- Version 2 notes (from the bundled readme): polygon offsets from contacts were fixed, and every crater is now a separate polygon (about 1,000 more units than version 1).
- Coarse groups, as defined in the script:
  - mare basalt: Em, Im1, Im2, Imd
  - pyroclastic/dark mantle: Id
  - highland/terra: It, Itd, INt, Nt, Ntp, pNt, Ip, INp, Np, EIp (terra and plains units)
  - crater material: Cc, Ccc, Csc, Ec, Ecc, Esc, Ic, Ic1, Ic2, Icc, Isc, Icf, Nc, pNc
  - basin material: Ib, Ibm, Ig, Iia, Iiap, Iic, Iif, Orientale units, Nb, Nbl, Nbm, Nbsc, Nnj, pNb, pNbm
  - other: any other code (none in this strip)
- Grouping choice to revisit: Ip (Imbrian Plains) is placed in highland/terra. Plains near Sinus Medii and Mare Vaporum could be cryptomare, so this group is less certain than the others.
- Class ids are ordered by group, then by unit code. They are fixed for this strip only. Another strip will produce a different id list, so join on `unit_code`, not on `class_id`.
- The figure uses a distinct palette grouped by coarse group. The official USGS colours make Nt, Nbl and Nbm, and also Em and Id, nearly identical in this strip. White in the figure means quality-masked.
- Environment: geopandas 1.2.0, shapely 2.2.0, pyogrio 0.13.0, NumPy 2.2.6, matplotlib 3.11.2.
- Open question: would a contact buffer (for example 2 km) plus line-block splits leave enough pixels per class? Measure this with the saved label arrays before the M3 supervised run.
