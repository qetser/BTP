# Notes

## Search and source review

- Exa skill workflow used: natural-language primary-source searches, followed by fetching the full text of key conference abstracts and the PDS archive index.
- Earlier literature-review pass: 147 search-result slots. Additional Exa queries for P1 data-access routes were run afterward and are not included in that count. Searches can return overlapping pages, so neither count is a deduplicated source count.
- Primary sources reviewed:
  - [LPSC 2021 abstract 2436](https://www.hou.usra.edu/meetings/lpsc2021/pdf/2436.pdf), IIRS/M³ radiance-shape comparison normalized at 810 nm.
  - [LPSC 2025 abstract 1876](https://www.hou.usra.edu/meetings/lpsc2025/pdf/1876.pdf), Level-2 reflectance processing and Apollo 16/RELAB 62231 empirical-line calibration.
  - [LPSC 2025 abstract 1644](https://www.hou.usra.edu/meetings/lpsc2025/pdf/1644.pdf), independent Level-0 recalibration workflow and differences from ISRO Level-1.
  - [PDS Imaging Node M³ volume index](https://pds-imaging.jpl.nasa.gov/volumes/m3.html), official access-site index for M³ volumes.
  - [EGU 2025 abstract EGU25-691](https://doi.org/10.5194/egusphere-egu25-691), IIRS-derived temperature comparison with Diviner using matched ground control points and acquisition local time.
  - [Official PDS Imaging Node M³ volume index](https://pds-imaging.jpl.nasa.gov/volumes/m3.html) and [JPL data-node volume directory](https://planetarydata.jpl.nasa.gov/img/data/m3/CH1M3_0004/). Exa confirmed the official volume directory. A strict-TLS fetch in this environment failed with the same self-signed certificate-chain error, so the alternate node is identified but data retrieval remains blocked here.

## P1 retrieval attempt

- Used the official ODE REST manual ([PDS Geosciences Node](https://oderest.rsl.wustl.edu/ODE_REST_V2.1.6.pdf)). Its product query can return full label lines (`results=l`), product file URLs (`results=f`), or both (`results=fl`).
- Reproduction query for the selected product: `https://oderest.rsl.wustl.edu/live2?query=product&target=moon&ihid=CH1-ORB&iid=M3&pt=REFIMG&pdsid=M3G20090206T010833_V01_RFL&results=fl&output=JSON`.
- ODE returned status `Success` at `2026-10-10T11:38:07.006`. Saved the retrieved product facts and file inventory in [`m3_candidate_ode_metadata.json`](m3_candidate_ode_metadata.json).
- ODE's file inventory lists `M3G20090206T010833_V01_RFL.IMG` as 2,700,001 KiB and the companion `M3G20090206T010833_V01_SUP.IMG` as 97,001 KiB. The Level-2 label references source `M3G20090206T010833_V03_LOC.IMG`, which is required for per-pixel geolocation.
- ODE serves metadata and links but lists the binary URLs on `planetarydata.jpl.nasa.gov`. Python `urllib` and `curl` with normal certificate verification both failed with `self signed certificate in certificate chain`; no TLS bypass was used. The alternate JPL hostname therefore did not unblock binary retrieval.
- Exa located the USGS-hosted PDS4 bundle access route documented in the conversion repository. Requests to `https://pdsimage2.wr.usgs.gov/Chandrayaan_1/`, `CH1M3_0004/`, and candidate top-level M3 directory names returned 404; the NASA Open Data listing also has no resource downloads. The JPL server presents a leaf certificate for `planetarydata.jpl.nasa.gov` chaining to Entrust OV TLS Issuing RSA CA 2 and Sectigo Public Server Authentication Root R46, but the root is absent from the local trust store. An HTTPS download of that root from Sectigo failed handshake validation, so no ad hoc trust anchor was installed and no TLS check was bypassed.
- No raster cube or location image was downloaded. No overlap value or figure was produced. P1 is blocked pending a valid official binary route, a corrected local trust chain, or user-supplied archive files.

## Alternative checks and gates

1. **Current scene, low-cost relative check:** fetch the top official M³ candidate via a PDS-listed endpoint. Decode and compare only overlapping 0.8–3.0 µm spectral shape after applying valid masks, wavelength-response matching, spatial support matching, and acquisition-geometry review. Unity normalization at 810 nm removes absolute-scale information. First measure true geolocated valid-pixel overlap; sparse grid-node screening is not sufficient.
2. **Separate scene, absolute reflectance route:** acquire an IIRS strip over Apollo 16. Reproduce the published thermal correction, apparent reflectance, photometric normalization, and RELAB 62231 empirical-line calibration; compare with co-located M³. Record that this validates the resulting reflectance procedure under its assumptions, not the present E1G2 QUB’s absolute radiance by itself.
3. **E1G2 longwave physical check:** once units, masks, and geometry pass, compare derived temperatures against Diviner data matched by ground control points and local acquisition time. This checks derived temperatures, not radiance units independently.
4. **Internal processing comparator:** reproduce the published Level-0/LUT recalibration only as a sensitivity analysis against Level-1. It omits documented ISRO processing and cannot establish the correct Level-1 mask or fill semantics.

## Prior evidence retained

- The V6 guide (p. 14) describes dark subtraction, LUT correction, destriping, radiance conversion, then keystone and radiance post-processing. It attributes differences between direct LUT calculations and Level-1 to post-processing.
- The guide says calibrated data use mW cm⁻² sr⁻¹ µm⁻¹; the matched E1G2 label says µW cm⁻² sr⁻¹ µm⁻¹. Keep the factor-of-1000 conflict unresolved; do not alter cube values based on either interpretation.
- The candidate PDS label request previously failed TLS validation. Do not disable certificate verification. Use a PDS-listed trusted mirror or another trusted PDS access route.
- The user has already tried contacting the IIRS team and received no response. Do not make further contact the next action.

No new metrics, figures, or cube modifications were produced in this source review.
