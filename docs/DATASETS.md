# Datasets: synthetic generators and real data

Every problem can be started offline: `sp_common.synth` contains seeded generators that return the signal *and* the ground truth. They are models of real instruments, simplified on purpose; say so in your report. The real datasets in the right column are the final test of every method. Do **not** commit large raw data files (they are git-ignored under `data/raw/`); record the download recipe and a checksum instead.

> **Check links before relying on them.** The links were written from memory of well-known public archives and could not be opened while this repository was being prepared. If one has moved, search for the dataset name; the archive itself is real, but the page may have changed.

| # | Synthetic generator (`sp_common.synth`) | Real data to use | Where |
|---|---|---|---|
| 01 | `sensor_signal`, `gyro_noise` | Phyphox smartphone logs; EuRoC MAV IMU | https://phyphox.org · https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets |
| 02 | plain NumPy tones | Phyphox accelerometer at several rates; Kepler long and short cadence (MAST) | https://phyphox.org · https://archive.stsci.edu |
| 03 | `scipy.signal.max_len_seq`, simulated structure | Ruler-twang accelerometer record; balloon-pop room impulse response | recorded by you with Phyphox |
| 04 | `bearing_vibration(fault='none')` | SILSO sunspot number; CWRU normal baseline; your own audio | https://www.sidc.be/SILSO/ · https://engineering.case.edu/bearingdatacenter |
| 05 | analytic systems | your own ringing or pendulum record (from 03) | recorded by you |
| 06 | `sensor_signal` plus mains tone | optional microcontroller ADC stream | recorded by you |
| 07 | `grb_event_list`, AR and 1/f noise | Fermi GBM TTE data; AstroSat CZTI event files; TESS/Kepler photon-noise light curves | https://heasarc.gsfc.nasa.gov · https://astrobrowse.issdc.gov.in/astro_archive/archive/Home.jsp |
| 08 | analytic transfer functions | bench measurement of your own RC / Sallen-Key filter | measured by you |
| 09 | `lockin_signal` | optional chopped-photodiode experiment | measured by you |
| 10 | tones through your quantiser | sound-card loop-back recording | recorded by you |
| 11 | `satellite_doppler_pass` | SatNOGS observations of 437 MHz beacons | https://db.satnogs.org |
| 12 | `bearing_vibration` | CWRU normal baseline; fan vibration via Phyphox | https://engineering.case.edu/bearingdatacenter |
| 13 | `uneven_variable_star`, `transit_lightcurve` | SILSO sunspots; AAVSO photometry; TESS via Lightkurve | https://www.sidc.be/SILSO/ · https://www.aavso.org · https://lightkurve.github.io/lightkurve/ |
| 14 | `sensor_signal`, `bearing_vibration` | smartphone accelerometer while walking; MIT-BIH ECG | https://physionet.org/content/mitdb/1.0.0/ |
| 15 | `barometer_rocket` | smartphone barometer on a staircase | recorded by you |
| 16 | `iq_multiband` | RTL-SDR capture of broadcast FM | captured by you |
| 17 | `chirp_in_noise`, `satellite_doppler_pass` | GW150914 strain (GWOSC); SatNOGS waterfall | https://gwosc.org · https://db.satnogs.org |
| 18 | `transit_lightcurve`, `grb_event_list` | Kepler/TESS light curve (Kepler-10, Kepler-5, WASP-18); MIT-BIH ECG | https://archive.stsci.edu |
| 19 | `chirp_in_noise`, `colored_noise` | GW150914 H1 and L1 strain | https://gwosc.org |
| 20 | `imu_gps_trajectory` | EuRoC MAV IMU and ground truth; ADS-B tracks (OpenSky or your own receiver) | https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets · https://opensky-network.org |
| 21 | `bearing_dataset` | CWRU bearing files; HTRU2 pulsar candidates (UCI) | https://engineering.case.edu/bearingdatacenter · https://archive.ics.uci.edu |
| 22 | `grb_event_list`, `stellar_spectra` | AstroSat CZTI or Fermi GBM event files | https://astrobrowse.issdc.gov.in/astro_archive/archive/Home.jsp · https://heasarc.gsfc.nasa.gov |
| 23 | `glitch_zoo`, `bearing_dataset` | Gravity Spy glitch images; CWRU | https://gravityspy.org |
| 24 | `stellar_spectra`, `grb_event_list` | SDSS spectra; NASA SMAP/MSL telemetry anomalies | https://skyserver.sdss.org · https://github.com/khundman/telemanom |
| 25 | all generators, per track | your chosen real event (GRB, transit, GW, SatNOGS pass or flight log) | see problems 07, 13, 17-19, 22 |

## Generators at a glance

| Function | What it models | Ground truth returned |
|---|---|---|
| `sensor_signal` | tone in white noise, drift, spikes | clean signal |
| `gyro_noise` | rate gyroscope at rest: white noise, bias drift, rate random walk | each noise component |
| `lockin_signal` | 1 mV tone at -40 dB SNR with mains pickup and 1/f noise | amplitude, phase, frequency |
| `grb_event_list` | photon events of a gamma-ray burst on a drifting background (time, energy, quadrant) | burst parameters, true rate function, per-photon burst flag |
| `transit_lightcurve` | Kepler/TESS-like light curve with transits, variability, systematics, outliers, gaps | transit model, in-transit and outlier masks |
| `uneven_variable_star` | irregularly sampled pulsating star | period, amplitude |
| `bearing_vibration`, `bearing_dataset` | rolling-bearing accelerometer data; labelled dataset with per-recording nuisance | fault frequency, class, recording id |
| `chirp_in_noise`, `glitch_zoo`, `toy_ligo_psd`, `newtonian_chirp`, `colored_noise`, `optimal_snr` | inspiral chirp in coloured noise and short transients | injected optimal SNR, merger time, frequency track |
| `satellite_doppler_pass`, `iq_multiband` | LEO beacon with Doppler, wideband SDR capture | Doppler curve, offsets of each signal |
| `barometer_rocket` | model-rocket barometer with drift and an ejection-charge spike | altitude, apogee time and height |
| `imu_gps_trajectory` | planar vehicle with biased accelerometer and GPS with outage | position, velocity, bias, noise parameters |
| `stellar_spectra` | normalised spectra with emission, trough and cosmic-ray anomalies | labels and anomaly type |
