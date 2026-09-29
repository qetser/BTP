# M1 independent reference-data plan

**Status:** Five M³ Level-2 reflectance candidates identified by product-footprint intersection with the E1G2 bounding box. No image product was downloaded and no validation was computed.

**Source data:** Candidate IIRS scene `20260227T1239538758` (E1G2), with local footprint of about 5.47°W–3.50°W and 6.53°S–26.86°N. Its geometry file contains 1,476 sparse coordinate records across 246 of 250 lines.

**Method:** Queried the PDS Orbital Data Explorer REST service for M³ `REFIMG` products using `loc=f` (footprint intersection) and the E1G2 bounds (-7° to 27° latitude, 354.5° to 356.5° east longitude). Saved the five returned label IDs, observation times, orbits, center coordinates, and label URLs in [`m3_overlap_candidates.csv`](m3_overlap_candidates.csv). The query can be rerun with [`query_m3_overlap.py`](../../../scripts/query_m3_overlap.py). Separately, use LROC WAC global imagery as an external spatial reference and assess IIRS-to-WAC registration on held-out control points, reporting errors in projected metres and IIRS pixels.

**Observations:** The query found five M³ Level-2 product footprints intersecting the E1G2 bounding box. The candidates are from orbit 1080 and were observed on 2009-02-05/06. The LROC archive exposes a 100 m/pixel global morphologic map. No WAC or M³ image product is currently present under local `data/`. The M³ list is an acquisition shortlist, not a validated overlap or spectral result.

**Limitations:** WAC image matching can assess spatial registration but cannot establish IIRS radiometric calibration. M³ comparison applies to reflectance products, not the current IIRS radiance cube. Spectral response, pixel footprint, acquisition geometry, and residual registration differences must be handled before comparing spectra. Apollo 16 calibration sites discussed in Chauhan et al. (2025) are not within this E1G2 footprint.

**Data version:** IIRS pair acquired 2026-02-27; candidate WAC and M³ archival product versions must be recorded at retrieval.

**Code commit:** No commit yet. The query script is [`query_m3_overlap.py`](../../../scripts/query_m3_overlap.py); it writes the candidate CSV. No geometric or reflectance metric was produced.

**Figure:** None. No metric or spatial comparison was computed.

**Next gate:** Inspect candidate M³ labels and usable pixel footprints to select the best common coverage; then obtain only the relevant M³ observation. Obtain a footprint-sized WAC reference. Confirm coordinate conventions and product versions before implementing registration or spectral comparisons. Keep mask semantics and independent radiance validation as separate M2 blockers.
