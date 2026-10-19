import numpy as np
import pytest
from scipy import signal
from sp_common import synth, constants as C


def test_sensor_signal_deterministic_and_noise_level():
    a = synth.sensor_signal(seed=3, noise_rms=0.3)
    b = synth.sensor_signal(seed=3, noise_rms=0.3)
    assert np.array_equal(a["noisy"], b["noisy"])
    assert np.std(a["noisy"] - a["clean"]) == pytest.approx(0.3, rel=0.15)


def test_gyro_white_noise_level():
    g = synth.gyro_noise(duration=600.0, seed=5)
    assert np.std(g["white"]) == pytest.approx(0.02, rel=0.05)
    assert g["rate"].shape == g["t"].shape


def test_lockin_input_snr_is_very_negative():
    d = synth.lockin_signal()
    sig_p = d["amp"] ** 2 / 2
    noise_p = np.var(d["x"] - d["amp"] * np.cos(2 * np.pi * d["f_ref"] * d["t"] + d["phase"]))
    assert 10 * np.log10(sig_p / noise_p) < -35


def test_grb_event_list_has_burst_and_energy_range():
    d = synth.grb_event_list(seed=7)
    assert d["energy"].min() >= 20.0 and d["energy"].max() <= 200.0
    counts, edges = np.histogram(d["time"], bins=np.arange(0, 300.5, 1.0))
    t0 = d["truth"]["t0"]
    peak = edges[np.argmax(counts)]
    assert t0 <= peak <= t0 + 6.0                       # peak rate is just after onset
    bkg = counts[:100].mean()
    assert bkg == pytest.approx(250 * 1.0, rel=0.25)    # about 250 counts/s before the burst
    assert counts.max() > bkg + 8 * np.sqrt(bkg)        # burst is clearly significant


def test_grb_burst_is_harder_than_background():
    d = synth.grb_event_list(seed=7)
    e = d["energy"]
    burst = d["truth"]["is_burst"]
    assert e[burst].mean() > e[~burst].mean()


def test_transit_lightcurve_truth_consistent():
    d = synth.transit_lightcurve(seed=11)
    tr = d["truth"]
    assert tr["in_transit"].sum() > 20
    assert d["flux"][tr["in_transit"] & ~tr["outlier"]].mean() < d["flux"][~tr["in_transit"]].mean() - 0.005
    assert np.all(np.diff(d["time"]) > 0)


def test_uneven_sampling_is_uneven():
    d = synth.uneven_variable_star()
    dt = np.diff(d["t"])
    assert dt.max() > 50 * np.median(dt) or dt.max() > 60


def test_bearing_envelope_shows_fault_frequency():
    d = synth.bearing_vibration(fault="outer", duration=10.0, noise=0.2, seed=1)
    x = d["x"]
    # band-pass around the structural resonance, take the envelope spectrum
    sos = signal.butter(4, [2200, 4200], btype="bandpass", fs=d["fs"], output="sos")
    env = np.abs(signal.hilbert(signal.sosfiltfilt(sos, x)))
    env = env - env.mean()
    spec = np.abs(np.fft.rfft(env * np.hanning(env.size)))
    f = np.fft.rfftfreq(env.size, 1 / d["fs"])
    band = (f > 20) & (f < 400)
    peak_f = f[band][np.argmax(spec[band])]
    assert peak_f == pytest.approx(d["f_fault_hz"], abs=1.5)


def test_bearing_none_has_no_fault_frequency():
    assert synth.bearing_vibration(fault="none")["f_fault_hz"] is None


def test_bearing_dataset_shapes_and_groups():
    d = synth.bearing_dataset(n_recordings_per_class=2, segments_per_recording=3, segment_s=0.25)
    assert d["X"].shape == (4 * 2 * 3, 3000)
    assert len(set(d["groups"])) == 8
    for gid in set(d["groups"]):
        assert len(set(d["y"][d["groups"] == gid])) == 1


def test_chirp_injected_snr_matches_target():
    d = synth.chirp_in_noise(target_snr=12.0, seed=2)
    rho = synth.optimal_snr(d["signal"], 4096.0, synth.toy_ligo_psd)
    assert rho == pytest.approx(12.0, rel=1e-6)


def test_chirp_matched_filter_recovers_time():
    d = synth.chirp_in_noise(target_snr=20.0, seed=4)
    fs = 4096.0
    psd = synth.toy_ligo_psd
    n = d["strain"].size
    f = np.fft.rfftfreq(n, 1 / fs)
    tmpl = np.zeros(n)
    tmpl[: d["template"].size] = d["template"]
    s_f, h_f = np.fft.rfft(d["strain"]), np.fft.rfft(tmpl)
    w = 1.0 / psd(f)
    w[f < 20] = 0
    z = np.fft.irfft(s_f * np.conj(h_f) * w, n)
    k = int(np.argmax(np.abs(z)))
    # lag k means template start aligned with t = k/fs; template merger sits at (2 s - 0.05 s) after its start
    t_merger_est = k / fs + (2.0 - 0.05)
    assert t_merger_est == pytest.approx(d["truth"]["t_merger"], abs=0.02)


def test_chirp_frequency_law():
    d = synth.chirp_in_noise()
    f_inst = d["truth"]["f_inst"]
    t = d["t"]
    nz = f_inst > 0
    assert f_inst[nz].min() >= 20.0 and f_inst[nz].max() <= 150.0
    assert np.all(np.diff(f_inst[nz]) > 0)               # frequency sweeps upward


def test_colored_noise_psd_scaling():
    fs, n = 4096.0, 2**18
    x = synth.colored_noise(n, fs, lambda f: np.full_like(f, 2e-4), seed=1)
    f, p = signal.welch(x, fs, nperseg=4096)
    assert np.median(p[5:-5]) == pytest.approx(2e-4, rel=0.1)


def test_glitch_zoo_balanced():
    d = synth.glitch_zoo(n_per_class=10)
    assert d["X"].shape == (40, 2048)
    assert np.bincount(d["y"]).tolist() == [10, 10, 10, 10]


def test_satellite_doppler_sign_and_range():
    d = synth.satellite_doppler_pass(duration_s=120.0, fs=20000.0)
    dop = d["doppler_hz"]
    assert dop[0] > 0 and dop[-1] < 0                    # approaching then receding
    assert abs(dop[len(dop) // 2]) < 50                  # zero at closest approach
    assert abs(dop).max() < 10.5e3
    assert d["iq"].dtype == np.complex64


def test_iq_multiband_spectrum_peaks_at_offsets():
    d = synth.iq_multiband(duration=0.1)
    f = np.fft.fftshift(np.fft.fftfreq(d["iq"].size, 1 / d["fs"]))
    s = np.fft.fftshift(np.abs(np.fft.fft(d["iq"])))
    cw_bin = np.argmin(np.abs(f - 50e3))
    assert s[cw_bin - 5: cw_bin + 5].max() > 20 * np.median(s)


def test_barometer_rocket_apogee_plausible():
    d = synth.barometer_rocket()
    assert 150 < d["truth"]["apogee_m"] < 600
    assert d["alt_true"][0] == 0
    assert d["alt_true"][-1] == pytest.approx(0.0, abs=1.0)
    k = np.argmax(d["alt_true"])
    assert d["t"][k] == pytest.approx(d["truth"]["t_apogee"], abs=0.2)


def test_imu_gps_outage_and_shapes():
    d = synth.imu_gps_trajectory()
    assert d["accel"].shape == (12000, 2)
    assert np.isnan(d["gps"]).any() and not np.isnan(d["gps"][:50]).any()
    # integrating the biased accelerometer drifts away from the truth
    v = np.array([50.0, 0.0]) + np.cumsum(d["accel"], axis=0) / 100.0
    assert np.abs(v - d["truth"]["vel"]).max() > 1.0


def test_stellar_spectra_labels():
    d = synth.stellar_spectra(n_normal=50, n_anomalous=6)
    assert d["X"].shape == (56, 256) and d["y"].sum() == 6
