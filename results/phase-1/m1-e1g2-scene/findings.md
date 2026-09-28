# E1G2 candidate acquisition findings

- Raw and calibrated labels have the same timestamp `20260227T1239538758`, station suffix `d18`, job ID `IIRXXD18CHO2904302NNNN26058141632221_V2_1`, imaging orbit `29042`, dumping orbit `29043`, exposure `e1`, and gain `g2`.
- Both XML labels match on start/stop times, dimensions (`12,210 × 250 × 256`), and all 256 band centers (712.3–5009.7 nm). The calibrated label declares radiance units `µW/cm**2/sr/µm`. Numerical radiance-scale validation remains open.
- Raw archive: 715,581,464 bytes; ZIP CRC passed; ZIP SHA-256 `b29cc17233780a973224f7f6742230235052b4b0f5f08652eefd45f8140ca8f1`. Its 1,562,880,000-byte QUB matches XML MD5 `518420609143e6f119fa50038f22f23f`.
- Calibrated archive: 2,632,046,972 bytes; ZIP CRC passed; ZIP SHA-256 `669465771c3b6e092b7da251c5e2c5b5041e57d5578cd25216e4aa818334d5d8`. Its 3,125,760,000-byte QUB matches XML MD5 `b5614f39ec0faa3c136f3dd8c7a13eca`.
- The calibrated label includes refined geometry coordinates; geometry and footprint suitability still need assessment.
- The official mode-validity workbook marks E1G2 bands 226–248 valid, covering 4504.1–4874.9 nm. This is mode-level validity, not a per-pixel quality mask.
- The official calibrated browse PNG (1,009,135 bytes) is saved at `figures/20260227_e1g2_calibrated_browse.png`; its MD5 `8f8c9caabf07e346bd2afa38383c34a4` matches the browse XML label. It is for visual orientation only. No cube values or metrics were computed. Mission archives remain under ignored `data/`.

## Gate

The raw/calibrated pair passes identity, mode, archive CRC, and declared QUB checksum checks. The scene is not ready for M2 because radiance scale, geometry, saturation/fill masks, and correction quality remain unverified.
