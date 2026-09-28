# E1G2 candidate acquisition findings

- The PRADAN-generated selection lists raw and calibrated products with the same observation timestamp `20260227T1239538758` and station suffix `d18`.
- The raw product XML identifies logical product `urn:isro:isda:ch2_cho.iir:data_raw:ch2_iir_nri_20260227t1239538758_d_img_d18`.
- The raw XML reports acquisition start `2026-02-27T12:39:53.8758Z`, stop `2026-02-27T12:50:41.6917Z`, `exposure=e1`, and `gain=g2`.
- The downloaded raw archive passed `ZipFile.testzip()` and has SHA-256 `b29cc17233780a973224f7f6742230235052b4b0f5f08652eefd45f8140ca8f1`.
- The matching calibrated archive request returned HTTP 302. No calibrated archive or label was retained, so matching lineage is not yet confirmed.
- The complete raw and calibrated filenames are listed in the [summary](summary.md). Mission data remain under ignored `data/`.

## Gate

The raw candidate passes the E1G2 mode check. The scene pair remains open pending the calibrated XML and geometry comparison. Do not run M2 thermal correction on this candidate yet.
