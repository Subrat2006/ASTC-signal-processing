# Curriculum: theory and practical experience

This document is the plan behind the problem statements. It was written *first*, before any problem: for each topic it fixes the **theory** that must be understood and the **hands-on skill** that must be acquired, and the problems were then designed so that every theory item is *used*, not just read.

## Design principles

1. **Derive by hand, then verify by code.** Every problem contains short analytic derivations and a self-check target that the simulation must reproduce before any result is trusted.
2. **Real problems, real data, known truth.** Each problem has a synthetic generator with *known ground truth* (so you can measure bias, error and false alarms) and pointers to *real datasets* (so you can see what the textbook model leaves out). Develop on the first, confirm on the second.
3. **Each problem hands numbers to the next.** Noise densities, filter designs and detectors are reused later, so the ladder is one connected toolbox, not 25 unrelated exercises. See the hand-off table below.
4. **Aerospace first.** Each problem ends with an *Aerospace Application Link*: the signal-processing result is carried to a number that matters for a satellite, a rocket, a ground station or a detector.
5. **Honest statistics.** Error bars, false-alarm rates, injection-recovery curves and bias measurements are required; a modest, correctly analysed result scores higher than a polished but unvalidated one.
6. **From sensors to machine learning, in that order.** Machine learning appears only after the physics and the classical optimum (the matched filter, the Kalman filter) are understood, so that a network is always benchmarked against something that is provably good.

## Theory and hands-on skills, problem by problem

| # | Problem | Theory to master | Hands-on skills gained | Effort |
|---|---|---|---|---|
| 01 | [Signals, Sensors and Noise](../problems/01_signals_sensors_and_noise/01_signals_sensors_and_noise.pdf) | Signal classes and measures (energy, power, RMS), decibels, sensor model, noise sources, averaging, Allan variance | NumPy array handling, least-squares calibration, robust statistics, Allan deviation, reading a datasheet noise figure | 8–12 hours |
| 02 | [Sampling, Aliasing and Reconstruction](../problems/02_sampling_aliasing_and_reconstruction/02_sampling_aliasing_and_reconstruction.pdf) | Impulse sampling, spectral replication, Nyquist theorem, aliasing, sinc reconstruction, zero-order hold, bandpass sampling, aperture jitter | Dense-grid simulation of analog signals, alias prediction, interpolation, anti-alias filter selection, jitter Monte Carlo | 8–12 hours |
| 03 | [Complex Numbers, Convolution and LTI Systems](../problems/03_convolution_and_lti_systems/03_convolution_and_lti_systems.pdf) | Complex exponentials and phasors, linearity and time invariance, impulse response, convolution, BIBO stability, correlation, deconvolution | Direct and matrix convolution, numerical LTI tests, system identification from an impulse response, correlation-based ranging, regularised deconvolution | 10–14 hours |
| 04 | [Fourier Series and the Fourier Transform](../problems/04_fourier_series_and_transform/04_fourier_series_and_transform.pdf) | Fourier series, Gibbs phenomenon, Parseval, Fourier transform pairs and properties, convolution theorem, time-bandwidth uncertainty | Numerical Fourier integrals, harmonic analysis and THD, transform-pair verification, uncertainty measurements, spectral reading of rotating machinery | 10–14 hours |
| 05 | [Laplace Transform, Poles and Stability](../problems/05_laplace_transform_and_stability/05_laplace_transform_and_stability.pdf) | Laplace transform and ROC, transfer functions, poles and zeros, second-order step response, Routh–Hurwitz, Bode plots, PD attitude control | Symbolic transforms with SymPy, pole-zero analysis, step-response metrics, Routh array code, Bode plotting, system identification from a ringing record | 10–14 hours |
| 06 | [Z-Transform and Discrete-Time Systems](../problems/06_z_transform_and_discrete_systems/06_z_transform_and_discrete_systems.pdf) | Z-transform and ROC, difference equations, pole-zero analysis, unit-circle frequency response, discretisation by Euler and bilinear mappings, warping, sample-rate effects on control loops | Difference-equation implementation, pole-zero design of resonators and notches, s-to-z mappings, discrete controller stability analysis, block versus sample processing | 10–14 hours |
| 07 | [Random Signals, Noise and Power Spectral Density](../problems/07_random_signals_and_noise_spectra/07_random_signals_and_noise_spectra.pdf) | Probability distributions, stationarity and ergodicity, autocorrelation, Wiener–Khinchin, filtering of random signals, AR processes, 1/f noise, Poisson counting statistics and detection thresholds | Monte Carlo simulation, correlation estimators, PSD scaling, colored-noise synthesis, Poisson versus Gaussian false-alarm calculation, Fano-factor tests on real counts | 12–16 hours |
| 08 | [Analog Filters: From RC to Butterworth and Chebyshev](../problems/08_analog_filters/08_analog_filters.pdf) | First- and second-order filters, Bode response, Butterworth Chebyshev Bessel and elliptic families, group delay, Sallen–Key realisation, component tolerance, anti-alias filter specification | Nodal analysis in NumPy, filter order from specifications, pole placement, Monte Carlo tolerance analysis, anti-alias filter design for a given ADC | 10–14 hours |
| 09 | [Sensor Conditioning and Circuit Noise](../problems/09_sensor_conditioning_and_circuit_noise/09_sensor_conditioning_and_circuit_noise.pdf) | Thermal and shot noise, noise density, op-amp noise, bridge circuits and instrumentation amplifiers, transimpedance amplifiers, lock-in detection, noise budgets | Noise-density to RMS conversion, input-referred noise cascades, bridge and amplifier sizing, digital lock-in implementation, end-to-end noise budgeting | 12–16 hours |
| 10 | [ADC and DAC: Quantisation and Sigma-Delta](../problems/10_adc_dac_and_quantisation/10_adc_dac_and_quantisation.pdf) | Uniform quantisation and SQNR, dither, ENOB and SINAD, INL and DNL, oversampling, noise shaping and sigma-delta modulators, zero-order-hold DAC | Quantiser simulation, spectral SINAD and ENOB measurement, code-density test, sigma-delta modulator coding, DAC droop compensation, data-rate budgeting | 10–14 hours |
| 11 | [Modulation, Demodulation and Telemetry Links](../problems/11_modulation_and_telemetry_links/11_modulation_and_telemetry_links.pdf) | AM and FM, BPSK and matched-filter detection, BER versus Eb/N0, link budget, Doppler shift and rate, carrier recovery with a Costas loop | Modulator and demodulator coding, Monte Carlo BER with confidence intervals, Costas-loop simulation, Doppler curve fitting, link-budget calculation | 14–18 hours |
| 12 | [DFT, FFT and Windowing](../problems/12_dft_fft_and_windowing/12_dft_fft_and_windowing.pdf) | DFT definition and properties, radix-2 FFT, circular convolution, spectral leakage, window figures of merit, resolution, amplitude and PSD scaling, frequency estimation accuracy | FFT implementation, timing and complexity analysis, leakage and scalloping measurement, correct spectral scaling, peak interpolation for frequency estimation | 12–16 hours |
| 13 | [Spectral Estimation: Welch, Multitaper and Lomb–Scargle](../problems/13_spectral_estimation/13_spectral_estimation.pdf) | Periodogram bias and variance, Bartlett and Welch averaging, confidence intervals, multitaper estimation, coloured-noise slopes, Lomb–Scargle periodogram for uneven sampling, false-alarm probability | Welch implementation and confidence intervals, DPSS multitaper, spectral slope fitting, Lomb–Scargle implementation, period search with aliases and false-alarm probability | 12–16 hours |
| 14 | [FIR Filter Design](../problems/14_fir_filter_design/14_fir_filter_design.pdf) | FIR structure and linear phase, window method, Kaiser design formulas, Parks–McClellan equiripple design, filter types I–IV, differentiators and Hilbert transformers, fast FIR filtering, coefficient quantisation | Windowed-sinc design, order estimation, equiripple design with SciPy, overlap-add filtering, band-pass design on real accelerometer data, fixed-point FIR | 12–16 hours |
| 15 | [IIR Filters and Real-Time Implementation](../problems/15_iir_filters_and_real_time_implementation/15_iir_filters_and_real_time_implementation.pdf) | Bilinear transform and prewarping, IIR families, zero-phase filtering, second-order sections and numerical sensitivity, fixed-point arithmetic, causality and detection delay, exponential and complementary filters | Bilinear transform coding, SOS versus direct-form comparison, Q15 biquad implementation, causal event detection with delay and false-alarm statistics | 12–16 hours |
| 16 | [Multirate Processing and SDR Front Ends](../problems/16_multirate_processing/16_multirate_processing.pdf) | Decimation and interpolation, polyphase structures, rational resampling, CIC filters and bit growth, digital down-conversion, FM demodulation from IQ, channelisation | Polyphase filter coding, rational resampling, integer CIC implementation, digital down-converter chain, multi-signal channelisation, computational cost accounting | 12–16 hours |
| 17 | [Time–Frequency Analysis: STFT, Wavelets and Chirps](../problems/17_time_frequency_analysis/17_time_frequency_analysis.pdf) | Short-time Fourier transform and spectrogram, window-length trade-off, chirps and instantaneous frequency, continuous and discrete wavelet transforms, whitening, gravitational-wave chirp law | STFT and inverse STFT coding, ridge extraction, Morlet CWT via FFT, DWT band analysis, noise whitening, power-law chirp fitting to estimate chirp mass | 14–18 hours |
| 18 | [Denoising and Data Cleaning for Instrument Data](../problems/18_denoising_and_data_cleaning/18_denoising_and_data_cleaning.pdf) | Outlier detection, detrending and its bias, Savitzky–Golay smoothing, Wiener filter, wavelet shrinkage, variance-stabilising transforms, gap handling | Robust sigma clipping, Hampel filtering, light-curve flattening with transit masking, Savitzky–Golay coefficient derivation, wavelet thresholding, bias-aware evaluation of cleaning | 14–18 hours |
| 19 | [Matched Filters and Detection Theory](../problems/19_matched_filters_and_detection/19_matched_filters_and_detection.pdf) | Neyman–Pearson detection, correlator and matched filter, ROC curves, coloured-noise whitening, optimal SNR, template banks and match, trials factor and false-alarm rate, pulse compression | Monte Carlo ROC estimation, FFT matched filtering, whitening with an estimated PSD, background calibration from noise-only data, template-bank construction, trials-factor calculation | 14–20 hours |
| 20 | [Adaptive Filters and Kalman State Estimation](../problems/20_adaptive_filters_and_kalman_estimation/20_adaptive_filters_and_kalman_estimation.pdf) | Wiener solution, LMS NLMS and RLS, adaptive noise cancellation, Kalman filter equations, constant-velocity and IMU/GPS models, consistency tests, dead-reckoning drift | LMS and RLS implementation, noise canceller design, Kalman filter coding from scratch, IMU/GPS fusion with bias state, NIS and NEES consistency tests, Allan-variance-based tuning | 16–22 hours |
| 21 | [Feature Engineering and Classical Machine Learning for Signals](../problems/21_features_and_classical_ml/21_features_and_classical_ml.pdf) | Segmentation, time-domain spectral and envelope features, bearing fault frequencies, logistic regression SVM and random forests, cross-validation, group leakage, class imbalance, threshold selection | Feature extraction, envelope-spectrum analysis, scikit-learn pipelines, group-aware cross-validation, learning curves, precision-recall analysis and threshold tuning | 14–18 hours |
| 22 | [Clustering and Anomaly Detection: From n-Sigma to DBSCAN](../problems/22_clustering_and_anomaly_detection/22_clustering_and_anomaly_detection.pdf) | n-sigma exceedance detection, DBSCAN and k-distance, Isolation Forest, PCA reconstruction error, injection–recovery efficiency, false-alarm calibration, detector comparison | Event-list binning, baseline and robust sigma, DBSCAN parameter selection, Isolation Forest, injection-recovery experiments, threshold calibration on null data, anomaly detection on spectra | 16–22 hours |
| 23 | [Deep Learning for Signals: 1D CNNs and Spectrogram Classifiers](../problems/23_deep_learning_for_signals/23_deep_learning_for_signals.pdf) | Neural network training, 1D convolution as learned FIR filtering, receptive field, spectrogram CNNs, augmentation, overfitting and learning curves, optimality limits versus matched filtering, calibration and out-of-distribution inputs | PyTorch training loops, 1D and 2D CNN design, receptive-field and parameter counting, augmentation, learning curves, comparison with a matched-filter bank, saliency analysis | 16–22 hours |
| 24 | [Autoencoders for Denoising and Anomaly Detection](../problems/24_autoencoders_for_denoising_and_anomalies/24_autoencoders_for_denoising_and_anomalies.pdf) | Linear autoencoders and PCA, convolutional and denoising autoencoders, reconstruction-error anomaly scores, threshold selection, training contamination, bottleneck failure, variational autoencoders | PyTorch autoencoders, PCA equivalence check, windowed time-series anomaly detection, threshold from null reconstruction errors, contamination and capacity studies, comparison with classical detectors | 16–22 hours |
| 25 | [Capstone: An End-to-End Transient Detection Pipeline](../problems/25_capstone_transient_detection_pipeline/25_capstone_transient_detection_pipeline.pdf) | Pipeline architecture, calibrated detection statistics, trials factors over timescales, injection–recovery completeness, on/off significance, parameter estimation with uncertainties, reproducible reporting | Data audit, cleaning and detection pipeline assembly, two independent detectors, injection-recovery completeness curves, T90 and fluence estimation with bootstrap errors, red-team stress tests, packaging with tests, circular-style report | 35–60 hours |

## Tasks in each problem

**01 Signals, Sensors and Noise** — 1) Signal measures (Stage 2); 2) Sensor calibration; 3) Noise statistics; 4) Averaging and its limit; 5) Allan deviation of a gyroscope; 6) Real sensor; 7) Dynamic range

**02 Sampling, Aliasing and Reconstruction** — 1) Spectral replication (Stage 2); 2) Alias prediction; 3) Reconstruction; 4) Anti-alias filtering; 5) Zero-order hold; 6) Bandpass sampling; 7) Clock jitter; 8) Real data

**03 Complex Numbers, Convolution and LTI Systems** — 1) Convolution from scratch (Stage 2); 2) Classify systems; 3) Structural identification; 4) Phasors and eigenfunctions; 5) Correlation ranging; 6) Deconvolution; 7) Stability

**04 Fourier Series and the Fourier Transform** — 1) Fourier series by hand and by code (Stage 2); 2) Gibbs phenomenon; 3) Parseval and distortion; 4) Transform pairs; 5) Properties; 6) Uncertainty principle; 7) Rotating machinery

**05 Laplace Transform, Poles and Stability** — 1) Transforms by hand and symbolically (Stage 2); 2) Poles and responses; 3) Second-order metrics; 4) Routh–Hurwitz; 5) Bode plots; 6) Satellite attitude controller; 7) Identification

**06 Z-Transform and Discrete-Time Systems** — 1) Transforms and inversion (Stage 2); 2) Difference equations by hand; 3) Frequency responses; 4) Mappings from s to z; 5) Sample rate and stability; 6) Cascaded sections; 7) Sample-by-sample processing

**07 Random Signals, Noise and Power Spectral Density** — 1) Distributions and the CLT (Stage 2); 2) Autocorrelation estimators; 3) Wiener–Khinchin; 4) Filtering random signals; 5) Colored noise; 6) Poisson statistics; 7) Real or synthetic counts

**08 Analog Filters: From RC to Butterworth and Chebyshev** — 1) First-order response (Stage 2); 2) Your own circuit solver; 3) Butterworth from specification; 4) Comparing the families; 5) Sallen–Key design and tolerance; 6) Anti-alias design; 7) Measurement

**09 Sensor Conditioning and Circuit Noise** — 1) Noise floors (Stage 2); 2) Strain-gauge channel; 3) Cascade noise and optimum source resistance; 4) Transimpedance amplifier; 5) Digital lock-in; 6) Alternatives; 7) Noise budget

**10 ADC and DAC: Quantisation and Sigma-Delta** — 1) Quantiser and SQNR (Stage 2); 2) Spectra, harmonics and dither; 3) ENOB of a non-ideal converter; 4) INL and DNL by code density; 5) Oversampling; 6) Sigma-delta modulator; 7) DAC reconstruction

**11 Modulation, Demodulation and Telemetry Links** — 1) AM and FM (Stage 2); 2) BPSK BER curve; 3) Receiver comparison; 4) Carrier recovery; 5) Doppler tracking; 6) Link budget; 7) Real pass

**12 DFT, FFT and Windowing** — 1) DFT and FFT from scratch (Stage 2); 2) Properties; 3) Leakage and window metrics; 4) Scalloping curve; 5) Resolution; 6) Scaling; 7) Frequency estimation

**13 Spectral Estimation: Welch, Multitaper and Lomb–Scargle** — 1) Periodogram statistics (Stage 2); 2) Welch from scratch; 3) Leakage and dynamic range; 4) Multitaper; 5) Spectral slopes; 6) Lomb–Scargle; 7) Real data

**14 FIR Filter Design** — 1) Windowed-sinc design (Stage 2); 2) Kaiser design; 3) Equiripple design; 4) Linear-phase types; 5) Fast filtering; 6) Pedometer; 7) Coefficient quantisation

**15 IIR Filters and Real-Time Implementation** — 1) Bilinear transform by hand (Stage 2); 2) Warping; 3) IIR versus FIR cost; 4) Numerical stability; 5) Fixed-point biquad; 6) Zero-phase versus real-time; 7) Exponential and complementary filtering

**16 Multirate Processing and SDR Front Ends** — 1) Decimation (Stage 2); 2) Interpolation; 3) Rational resampling; 4) CIC filter; 5) Digital down-converter; 6) Channeliser; 7) Real capture and CPU budget

**17 Time–Frequency Analysis: STFT, Wavelets and Chirps** — 1) Window length and the uncertainty trade-off (Stage 2); 2) STFT from scratch; 3) Chirp in coloured noise; 4) Chirp-law fit; 5) Continuous wavelet transform; 6) Hilbert instantaneous frequency and Doppler; 7) Discrete wavelet analysis and a Campbell diagram; 8) Real data

**18 Denoising and Data Cleaning for Instrument Data** — 1) Characterise the problems (Stage 2); 2) Outlier rejection; 3) Detrending and bias; 4) Savitzky–Golay; 5) Wiener filter; 6) Wavelet denoising; 7) Pipeline and real data

**19 Matched Filters and Detection Theory** — 1) Detection theory by simulation (Stage 2); 2) Matched versus mismatched and energy detectors; 3) FFT matched filter for a chirp; 4) Coloured noise and whitening; 5) False-alarm calibration; 6) Template bank; 7) Real data

**20 Adaptive Filters and Kalman State Estimation** — 1) Wiener, LMS, NLMS, RLS (Stage 2); 2) Noise cancellation; 3) Kalman filter in one dimension; 4) IMU and GPS fusion; 5) Bias estimation and the outage; 6) Tuning and consistency; 7) Real data

**21 Feature Engineering and Classical Machine Learning for Signals** — 1) Feature library (Stage 2); 2) Envelope analysis; 3) Baselines; 4) Feature ablation and importance; 5) Robustness and domain shift; 6) Learning curves and calibration; 7) Real data

**22 Clustering and Anomaly Detection: From n-Sigma to DBSCAN** — 1) From events to a light curve (Stage 2); 2) n-sigma baseline detector; 3) DBSCAN grouping; 4) Several detectors, one yardstick; 5) Spectral anomalies; 6) Threshold calibration; 7) Real data

**23 Deep Learning for Signals: 1D CNNs and Spectrogram Classifiers** — 1) 1D CNN (Stage 2); 2) Spectrogram CNN; 3) Receptive field and learned filters; 4) Robustness and the matched-filter benchmark; 5) Augmentation; 6) Data efficiency and overfitting; 7) Explainability, calibration and out-of-distribution; 8) Real data and cost

**24 Autoencoders for Denoising and Anomaly Detection** — 1) Linear autoencoder versus PCA (Stage 2); 2) Convolutional autoencoder for spectra; 3) Denoising autoencoder; 4) Burst detection in a light curve; 5) Contamination study; 6) Capacity and bottleneck failure; 7) Real data and final verdict

**25 Capstone: An End-to-End Transient Detection Pipeline** — 1) Scope and data audit (Stage 1); 2) Cleaning and preprocessing; 3) Two independent detection methods; 4) Injection–recovery; 5) Characterisation of the real event; 6) Red team; 7) Packaging; 8) Report and presentation

## Number hand-offs between problems

| From | Used in | What is handed over |
|---|---|---|
| 01 | 20, 22, 24 | Noise densities and Allan parameters (ARW, bias instability) that set Kalman Q and detector baselines |
| 02 | 10, 14, 16 | Alias prediction, sampling-rate rules, jitter-limited SNR |
| 03 | 04, 19 | Convolution and correlation code, impulse-response identification, delay estimation |
| 04 | 12, 13, 17 | Transform pairs, uncertainty principle, harmonic-line reading of rotating machinery |
| 05 | 06, 08, 15 | Poles and zeros, second-order metrics, the satellite attitude-loop model |
| 06 | 14, 15, 20 | s-to-z mappings, difference-equation implementations, sample-rate limits of discrete loops |
| 07 | 09, 13, 18, 19, 22 | PSD scaling, AR and 1/f noise generators, Poisson statistics and tail probabilities |
| 08 | 09, 10, 15 | Filter families, Sallen-Key design, anti-alias specification |
| 09 | 10, 20 | Noise-budget method, digital lock-in implementation |
| 10 | 16, 21 | ENOB and SQNR methods, the sigma-delta modulator (decimated with a CIC filter in 16) |
| 11 | 16, 17, 19, 25 | Matched-filter BER, Doppler model fit, link-budget calculation |
| 12 | 13, 14, 17, 21 | Window figures of merit, correct amplitude and PSD scaling, peak interpolation |
| 13 | 17, 18, 19, 21 | Welch and multitaper estimators, Lomb-Scargle periodogram, confidence intervals |
| 14 | 15, 16, 20 | FIR design toolbox, overlap-add filtering, delay budgets |
| 15 | 20, 25 | Real-time causal filtering, apogee detector, fixed-point biquads |
| 16 | 25 | Digital down-converter chain, polyphase resampling, CIC filters |
| 17 | 18, 19, 23 | STFT code, whitening pipeline, chirp-law fit |
| 18 | 21, 22, 24, 25 | Bias-aware cleaning pipeline (clip, flatten, denoise) |
| 19 | 22, 23, 25 | Matched-filter SNR series, background calibration, trials factor, ROC tools |
| 20 | 25 | Kalman filter and consistency tests (NIS and NEES) |
| 21 | 22, 23, 24 | Feature library, group cross-validation, threshold selection |
| 22 | 24, 25 | Detector comparison at fixed false-alarm rate, injection-recovery harness |
| 23 | 24 | Training loops and the benchmark against the matched filter |
| 24 | 25 | Autoencoder detector and the contamination study |

## What you can do after each part

**Part A (01–02): What a signal is, how a sensor corrupts it, and what sampling does to it.** You learn to describe a signal by its power and noise, to calibrate a sensor, to separate white noise from drift with the Allan deviation, and to predict, avoid and exploit aliasing. After Part A you can look at any raw sensor stream and say how good it is and at what rate it must be sampled.

**Part B (03–07): The mathematics that every later method rests on.** You build convolution and LTI-system thinking, the Fourier transform and its uncertainty principle, the Laplace and z-transforms with pole-zero reasoning and stability, and the statistics of random signals including power spectra and Poisson counting. After Part B you can derive, not just use, the formulas of signal processing.

**Part C (08–11): The electronics in front of the processor.** You design analog filters and verify them with your own circuit solver, size a low-noise sensor front end and a lock-in detector, choose and test ADCs and DACs, and build the physical layer of a satellite telemetry link with its Doppler shift, carrier recovery and link budget.

**Part D (12–20): Digital signal processing, from the FFT to Kalman filtering.** You write the FFT, understand windows and spectral scaling, estimate spectra of noise and of unevenly sampled data, design FIR and IIR filters for real-time use, resample and down-convert radio signals, analyse chirps in time and frequency, clean data without biasing it, build matched filters with calibrated false-alarm rates, and fuse sensors with adaptive filters and Kalman filters.

**Part E (21–25): Machine learning on signals, done honestly, and a capstone.** You engineer features and avoid the leakage trap, detect anomalies and bursts with clustering and isolation methods, train convolutional networks and benchmark them against the optimal matched filter, build autoencoders for denoising and novelty detection, and finally assemble an end-to-end transient-detection pipeline with calibrated significance and a report.

## Level scale

| Level | Meaning |
|---|---|
| 1 Foundations | Needs only basic Python and school mathematics. |
| 2 Core | Uses results of earlier problems; standard textbook methods. |
| 3 Advanced | Combines several earlier problems; open-ended analysis. |
| 4 Expert | Statistical or system-level work; critical assessment expected. |
| 5 Capstone | Integration of the whole ladder on a real event. |
