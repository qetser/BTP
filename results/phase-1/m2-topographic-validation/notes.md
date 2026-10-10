# Notes

- Run order: `build_e1g2_working_cube.py`, then `run_e1g2_m2_physical_pilot.py`, then `run_e1g2_topographic_validation.py`. The last step takes about 3 minutes, mostly decoding the two JPEG2000 tiles.
- The script imports `build_dem_crop` and constants from `register_iirs_to_sldem_hillshade.py`, so the DEM crop and the signed int16 decoding match the registration run exactly.
- Slopes use Sobel gradients with 1/8 scaling, giving central differences in metres per DEM pixel. They are converted with the lunar radius 1,737.4 km and the cos(latitude) longitude spacing. Gradient fields are bilinearly resampled to IIRS pixels with `cv2.remap`.
- Ignored output: `data/derived/e1g2/cos_local_incidence.npy`, used by the M3 module.
- Pixel scatter in the figure is a fixed random subsample of 60,000 pixels (seed 0). The binned medians use all retained pixels.
- Open question: a full thermophysical model (for example, the Hayne et al. 2017 heat-conduction model with roughness) would show whether the flatter slope is fully explained physically.
