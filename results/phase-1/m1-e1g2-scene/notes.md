# E1G2 candidate acquisition notes

- Check date: 2026-09-28.
- Candidate selected from user-provided PRADAN download-script paths. Only the matching raw ZIP was downloaded during the first request.
- The raw archive was written to ignored path `data/pradan/e1g2_candidate_20260227T1239538758/ch2_iir_nri_20260227T1239538758_d_img_d18.zip`.
- Inspection opened the ZIP archive and parsed its data/raw PDS4 XML label in memory. No image cube was extracted for analysis.
- The separate request for `ch2_iir_nci_20260227T1239538758_d_img_d18.zip` returned HTTP 302 to PRADAN sign-in. The attempted response body was not saved.
- Do not reuse session cookies from chat. Renew the account session and select only the calibrated counterpart for the next transfer.
- No metric was computed, so no CSV/JSON metric or figure was created.
