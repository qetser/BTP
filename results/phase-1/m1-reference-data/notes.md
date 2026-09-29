# M1 reference-data notes

- Review date: 2026-09-29.
- The LROC WAC global morphologic map page reports a 100 m/pixel product and provides a PDS download. Its full listed image is 4.50 GB, so do not download the global image when a cropped or tiled subset can be acquired.
- The PDS M³ Level-2 profile states the archive contains pixel-located, reflectance-calibrated observations from the Chandrayaan-1 mission. Five intersecting label IDs were returned; no image product has yet been selected or downloaded.
- Queried ODE REST on 2026-09-29 with target `moon`, instrument host `CH1-ORB`, instrument `M3`, product type `REFIMG`, `loc=f`, west/east longitudes 354.5/356.5°E, and min/max latitudes -7/27°. It returned five product footprints. The CSV retains the returned observation, orbit, center, label URL, and label product ID. `loc=f` requests footprint intersection; product labels and valid-pixel masks remain to be inspected before acquisition.
- An otherwise identical ODE count query using `loc=b` (bounding-box intersection) returned 145 candidates. The footprint intersection returned five. Use the latter shortlist, then inspect actual labels and valid pixels before treating any pair as usable overlap.
- A search result for the IIRS SIFT registration work is a Preprints.org manuscript, not a peer-reviewed journal article. It describes sparse IIRS coordinate tags and LRO WAC registration; treat it as a method lead only.
- No image cubes were downloaded. The small product metadata response was reduced to the candidate CSV. No geometric or spectral metric was computed. No figure was appropriate.
- Apollo 16 longitude was checked against the E1G2 footprint for planning; the ground-calibration site is outside the footprint. Do not treat that paper's ground comparison as local validation.
