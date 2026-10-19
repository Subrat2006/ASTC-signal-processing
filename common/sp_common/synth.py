"""Seeded synthetic datasets with KNOWN ground truth.

Why synthetic data? (1) the repository works offline, (2) you can check a method against the truth before
you trust it on real data, and (3) you can inject a signal of known strength and measure how often you
recover it. Every generator is a *model of a real instrument or phenomenon*; the real datasets that each
problem statement points to are always the final test. Models are simplified on purpose: say so in your report.

All functions take a ``seed`` (int or numpy Generator) and return a dict whose entries are documented below.
"""
import numpy as np
from scipy import signal as sps_signal

from . import constants as C
from .rng import get_rng


def _rng(seed):
    return seed if isinstance(seed, np.random.Generator) else get_rng(seed)


# ---------------------------------------------------------------------------------------------------------
# 01-02, 09: sensors
# ---------------------------------------------------------------------------------------------------------
def sensor_signal(fs=1000.0, duration=1.0, f0=5.0, amp=1.0, noise_rms=0.2, drift_per_s=0.0,
                  spike_rate=0.0, spike_amp=5.0, seed=1):
    """A sinusoidal quantity measured by a noisy sensor.

    Returns dict(t, clean, noisy, fs). ``noise_rms`` is the std of white Gaussian noise, ``drift_per_s`` a linear
    baseline drift (units per second), ``spike_rate`` the mean number of random +-``spike_amp`` spikes per second.
    """
    rng = _rng(seed)
    n = int(round(fs * duration))
    t = np.arange(n) / fs
    clean = amp * np.sin(2 * np.pi * f0 * t)
    noisy = clean + noise_rms * rng.standard_normal(n) + drift_per_s * t
    if spike_rate > 0:
        hit = rng.random(n) < spike_rate / fs
        noisy[hit] += spike_amp * rng.choice([-1.0, 1.0], hit.sum())
    return dict(t=t, clean=clean, noisy=noisy, fs=fs)


def gyro_noise(fs=100.0, duration=3600.0, sigma_white=0.02, sigma_rrw=1e-4, sigma_bias=0.005,
               tau_bias=200.0, seed=3):
    """Rate-gyroscope output (deg/s) at rest: white noise + slowly wandering bias + rate random walk.

    Returns dict(t, rate, white, bias, rrw, fs). ``sigma_white`` is the per-sample std (deg/s) of the white term,
    ``sigma_bias`` the std (deg/s) of a first-order Gauss-Markov bias with correlation time ``tau_bias`` (s) and
    ``sigma_rrw`` the random-walk strength in (deg/s)/sqrt(s). Use it for the Allan-deviation task.
    """
    rng = _rng(seed)
    n = int(round(fs * duration))
    dt = 1.0 / fs
    t = np.arange(n) * dt
    white = sigma_white * rng.standard_normal(n)
    a = np.exp(-dt / tau_bias)
    drive = sigma_bias * np.sqrt(1 - a**2) * rng.standard_normal(n)
    bias = sps_signal.lfilter([1.0], [1.0, -a], drive)
    rrw = np.cumsum(sigma_rrw * np.sqrt(dt) * rng.standard_normal(n))
    return dict(t=t, rate=white + bias + rrw, white=white, bias=bias, rrw=rrw, fs=fs)


def lockin_signal(fs=10000.0, duration=20.0, f_ref=137.0, amp=1e-3, phase=0.7, noise_rms=0.01,
                  mains_hz=50.0, mains_amp=0.1, flicker_rms=0.01, seed=5):
    """A tiny sinusoid of known frequency buried in white noise, 1/f noise and mains pickup.

    Returns dict(t, x, ref_cos, ref_sin, fs, f_ref, amp, phase). With the defaults the input SNR is about -43 dB
    (signal power amp^2/2 versus a total noise power dominated by the 50 Hz pickup, mains_amp^2/2); a lock-in amplifier
    with a time constant of about a second still recovers ``amp`` to roughly 10 percent.
    """
    rng = _rng(seed)
    n = int(round(fs * duration))
    t = np.arange(n) / fs
    white = noise_rms * rng.standard_normal(n)
    # 1/f noise by spectral shaping of white noise
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / fs)
    f[0] = f[1]
    flick = np.fft.irfft(spec / np.sqrt(f / f[1]), n)
    flick *= flicker_rms / flick.std()
    mains = mains_amp * np.sin(2 * np.pi * mains_hz * t + 1.3)
    x = amp * np.cos(2 * np.pi * f_ref * t + phase) + white + flick + mains
    return dict(t=t, x=x, ref_cos=np.cos(2 * np.pi * f_ref * t), ref_sin=np.sin(2 * np.pi * f_ref * t),
                fs=fs, f_ref=f_ref, amp=amp, phase=phase)


# ---------------------------------------------------------------------------------------------------------
# 07, 13, 18, 22, 25: astronomy time series
# ---------------------------------------------------------------------------------------------------------
def grb_event_list(duration=300.0, bkg_rate=250.0, amp=300.0, t0=120.0, rise=0.5, decay=4.0,
                   emin=20.0, emax=200.0, bkg_index=1.5, burst_index=1.0, drift=0.15, seed=7):
    """A photon-counting detector (think AstroSat/CZTI or Fermi/GBM): an *event list* with a gamma-ray-burst-like
    transient on a slowly drifting background.

    Event times follow an inhomogeneous Poisson process with rate
        lambda(t) = bkg_rate * (1 + drift * sin(2 pi t / 600)) + amp * FRED(t - t0),
    where FRED(x) = (1 - exp(-x/rise)) exp(-x/decay) / peak for x > 0 (fast rise, exponential decay). Photon energies
    (keV) follow truncated power laws dN/dE ~ E^-index, harder for the burst (``burst_index``) than for the
    background (``bkg_index``). Returns dict(time, energy, quad, truth) where ``quad`` in {0,1,2,3} mimics detector
    quadrants and ``truth`` holds the burst parameters and the true rate function ``rate(t)``.
    """
    rng = _rng(seed)

    def fred(x):
        x = np.asarray(x, dtype=float)
        out = np.zeros_like(x)
        pos = x > 0
        out[pos] = (1 - np.exp(-x[pos] / rise)) * np.exp(-x[pos] / decay)
        xp = rise * np.log1p(decay / rise)          # location of the maximum of (1-e^{-x/r}) e^{-x/d}
        peak = (1 - np.exp(-xp / rise)) * np.exp(-xp / decay)
        return out / peak

    def rate(t):
        return bkg_rate * (1 + drift * np.sin(2 * np.pi * np.asarray(t) / 600.0)) + amp * fred(np.asarray(t) - t0)

    lam_max = bkg_rate * (1 + drift) + amp
    n_cand = rng.poisson(lam_max * duration)
    t_cand = np.sort(rng.random(n_cand) * duration)
    keep = rng.random(n_cand) < rate(t_cand) / lam_max
    time = t_cand[keep]
    p_burst = amp * fred(time - t0) / rate(time)
    is_burst = rng.random(time.size) < p_burst

    def powerlaw(index, size):
        u = rng.random(size)
        if abs(index - 1.0) < 1e-9:
            return emin * (emax / emin) ** u
        a = 1.0 - index
        return (emin**a + u * (emax**a - emin**a)) ** (1.0 / a)

    energy = np.where(is_burst, powerlaw(burst_index, time.size), powerlaw(bkg_index, time.size))
    quad = rng.integers(0, 4, time.size)
    truth = dict(t0=t0, amp=amp, rise=rise, decay=decay, bkg_rate=bkg_rate, rate=rate, is_burst=is_burst,
                 duration=duration)
    return dict(time=time, energy=energy, quad=quad, truth=truth)


def transit_lightcurve(days=90.0, cadence_min=30.0, period=3.2, t0=1.1, depth=0.01, duration_h=3.0,
                       noise_ppm=400.0, variability_ppm=3000.0, outlier_frac=0.003, gap_frac=0.05, seed=11):
    """A Kepler/TESS-style stellar light curve: periodic transits + stellar variability + a sawtooth systematic
    (thermal ramps) + white noise + cosmic-ray-like outliers + data gaps.

    Returns dict(time, flux, flux_err, truth) with time in days and flux normalised to 1. ``truth`` contains
    period, t0, depth, duration_h, the clean transit-only model ``transit`` and the boolean mask ``in_transit``
    (both on the returned time stamps) and the boolean mask ``outlier``.
    """
    rng = _rng(seed)
    dt = cadence_min / 1440.0
    time = np.arange(0.0, days, dt)
    keep = np.ones(time.size, bool)
    n_gaps = int(gap_frac * days)
    for _ in range(n_gaps):
        g0 = rng.uniform(0, days - 1.0)
        keep &= ~((time > g0) & (time < g0 + rng.uniform(0.2, 0.8)))
    time = time[keep]
    dur = duration_h / 24.0
    tt = (time - t0 + period / 2) % period - period / 2
    w = 0.15 * dur
    transit = 1.0 - depth * np.clip((dur / 2 - np.abs(tt)) / w, 0, 1)
    var = variability_ppm * 1e-6 * (np.sin(2 * np.pi * time / 11.0 + 0.4) + 0.5 * np.sin(2 * np.pi * time / 5.3 + 1.1))
    ramp = 1.5e-3 * (((time % 30.0) / 30.0) - 0.5)
    sigma = noise_ppm * 1e-6
    flux = transit + var + ramp + sigma * rng.standard_normal(time.size)
    out = rng.random(time.size) < outlier_frac
    flux[out] += sigma * rng.uniform(5, 20, out.sum()) * rng.choice([1.0, -0.3], out.sum())
    return dict(time=time, flux=flux, flux_err=np.full(time.size, sigma),
                truth=dict(period=period, t0=t0, depth=depth, duration_h=duration_h, transit=transit,
                           in_transit=np.abs(tt) < dur / 2, outlier=out))


def uneven_variable_star(n=400, period=0.6, amp=0.25, noise=0.04, baseline_days=800.0, seed=13):
    """Irregularly sampled photometry of a pulsating star (RR-Lyrae-like, non-sinusoidal): nightly sampling with
    random hours, weather losses and a long seasonal gap. Returns dict(t, mag, err, truth) with t in days.
    """
    rng = _rng(seed)
    nights = np.arange(baseline_days)
    nights = nights[~((nights % 365) > 265)]                 # seasonal gap
    nights = nights[rng.random(nights.size) > 0.5]           # weather
    t = np.sort(rng.choice(nights, size=min(n, nights.size), replace=False) + rng.uniform(0.0, 0.4, min(n, nights.size)))
    ph = 2 * np.pi * t / period
    mag = 12.0 + amp * np.sin(ph) + 0.3 * amp * np.sin(2 * ph + 0.7) + noise * rng.standard_normal(t.size)
    return dict(t=t, mag=mag, err=np.full(t.size, noise), truth=dict(period=period, amp=amp))


# ---------------------------------------------------------------------------------------------------------
# 04, 12, 21, 23: machine vibration
# ---------------------------------------------------------------------------------------------------------
BEARING_ORDERS = dict(inner=5.4152, outer=3.5848, ball=2 * 4.7135, cage=0.39828)   # multiples of shaft frequency


def bearing_vibration(fs=12000.0, duration=10.0, shaft_hz=29.95, fault="none", severity=1.0,
                      resonance_hz=3200.0, damping=800.0, noise=0.25, gain=1.0, seed=21):
    """Accelerometer signal from a rolling-element bearing test rig (modelled on the Case Western Reserve University
    experiments; the characteristic-frequency multiples are those of a 6205-type drive-end bearing).

    ``fault`` in {'none','inner','outer','ball'}. A fault produces a train of impacts at the characteristic
    frequency (with ~1 % random slip), each exciting a structural resonance at ``resonance_hz`` that decays with rate
    ``damping`` (1/s); inner-race impacts are amplitude-modulated at the shaft frequency. Always present:
    shaft harmonics (1x, 2x, 3x) and broadband noise. Returns dict(t, x, fs, shaft_hz, fault, f_fault_hz).
    """
    rng = _rng(seed)
    n = int(round(fs * duration))
    t = np.arange(n) / fs
    x = gain * (0.5 * np.sin(2 * np.pi * shaft_hz * t + 0.3) + 0.2 * np.sin(2 * np.pi * 2 * shaft_hz * t + 1.0)
                + 0.1 * np.sin(2 * np.pi * 3 * shaft_hz * t + 2.0))
    x = x + noise * rng.standard_normal(n)
    f_fault = None
    if fault != "none":
        f_fault = BEARING_ORDERS[fault] * shaft_hz
        k = np.arange(int(duration * f_fault) + 2)
        tk = (k + np.cumsum(0.01 * rng.standard_normal(k.size))) / f_fault          # random-walk slip
        amp = severity * np.ones(k.size)
        if fault == "inner":
            amp = amp * (1 + 0.6 * np.cos(2 * np.pi * shaft_hz * tk))
        idx = np.round(tk * fs).astype(int)
        ok = (idx >= 0) & (idx < n)
        imp = np.zeros(n)
        np.add.at(imp, idx[ok], amp[ok])
        tau = np.arange(int(0.02 * fs)) / fs
        resp = np.exp(-damping * tau) * np.sin(2 * np.pi * resonance_hz * tau)
        x = x + gain * sps_signal.fftconvolve(imp, resp)[:n]
    return dict(t=t, x=x, fs=fs, shaft_hz=shaft_hz, fault=fault, f_fault_hz=f_fault)


def bearing_dataset(n_recordings_per_class=8, segments_per_recording=10, segment_s=0.5, fs=12000.0, seed=23):
    """A labelled bearing-fault dataset with *recording-level nuisance variation* (speed, gain, resonance,
    severity), so that you can demonstrate the classic leakage error of random train/test splits.

    Returns dict(X, y, groups, class_names, fs): X (n_segments, segment_len), y integer labels
    (0 none, 1 inner, 2 outer, 3 ball) and ``groups`` = recording id (use GroupKFold on it!).
    """
    rng = _rng(seed)
    names = ["none", "inner", "outer", "ball"]
    X, y, g = [], [], []
    rec = 0
    seg_len = int(segment_s * fs)
    for label, name in enumerate(names):
        for _ in range(n_recordings_per_class):
            r = bearing_vibration(fs=fs, duration=segments_per_recording * segment_s,
                                  shaft_hz=rng.uniform(28.5, 30.5), fault=name,
                                  severity=rng.uniform(0.4, 1.6), resonance_hz=rng.uniform(2800, 3600),
                                  noise=rng.uniform(0.2, 0.4), gain=rng.uniform(0.7, 1.4), seed=rng)
            for s in range(segments_per_recording):
                X.append(r["x"][s * seg_len:(s + 1) * seg_len])
                y.append(label)
                g.append(rec)
            rec += 1
    return dict(X=np.array(X), y=np.array(y), groups=np.array(g), class_names=names, fs=fs)


# ---------------------------------------------------------------------------------------------------------
# 19, 17, 23: gravitational-wave-like chirps in coloured noise
# ---------------------------------------------------------------------------------------------------------
def toy_ligo_psd(f, a=4e-24, f_lo=25.0, f_hi=600.0):
    """One-sided strain PSD S_n(f) in 1/Hz of a TOY ground-based interferometer: a steep seismic wall below
    ``f_lo``, a flat bucket near 100-300 Hz and a shot-noise rise above ``f_hi``. This is NOT the real LIGO PSD;
    estimate the real one from open data in the problem statement.
    """
    f = np.maximum(np.asarray(f, dtype=float), 1.0)
    return a**2 * (1.0 + (f_lo / f) ** 8 + (f / f_hi) ** 2)


def newtonian_chirp(t, t_merger, mchirp_msun, f_low=20.0, f_cut=150.0):
    """Leading-order (Newtonian) inspiral chirp h(t) with unit amplitude scale. Returns (h, f_inst): the waveform
    ~ f^(2/3) cos(Phi) and the instantaneous GW frequency, both zero outside [f_low, f_cut].
    Time to coalescence tau = t_merger - t and chirp-mass time Tc = G Mc / c^3 give
        f(tau) = (1/pi) (5 / (256 tau))^(3/8) Tc^(-5/8),   Phi(tau) = -2 (tau / (5 Tc))^(5/8).
    """
    Tc = mchirp_msun * C.T_sun
    tau = t_merger - np.asarray(t, dtype=float)
    ok = tau > 0
    f = np.zeros_like(tau)
    f[ok] = (1 / np.pi) * (5.0 / (256.0 * tau[ok])) ** (3 / 8) * Tc ** (-5 / 8)
    band = ok & (f >= f_low) & (f <= f_cut)
    phase = np.zeros_like(tau)
    phase[band] = -2.0 * (tau[band] / (5.0 * Tc)) ** (5 / 8)
    h = np.zeros_like(tau)
    h[band] = f[band] ** (2 / 3) * np.cos(phase[band])
    # smooth turn-on and turn-off
    idx = np.where(band)[0]
    if idx.size > 20:
        ramp = int(min(idx.size // 8, 0.05 * 1.0 / max(np.mean(np.diff(np.asarray(t)[idx])), 1e-9)))
        ramp = max(ramp, 2)
        win = np.ones(idx.size)
        win[:ramp] = 0.5 * (1 - np.cos(np.pi * np.arange(ramp) / ramp))
        win[-ramp:] *= 0.5 * (1 + np.cos(np.pi * np.arange(ramp) / ramp))
        h[idx] *= win
    return h, np.where(band, f, 0.0)


def colored_noise(n, fs, psd_fn, seed):
    """Real Gaussian noise of length n with one-sided PSD psd_fn(f) in units^2/Hz (Welch-consistent scaling)."""
    rng = _rng(seed)
    f = np.fft.rfftfreq(n, 1 / fs)
    s = psd_fn(f)
    X = np.sqrt(n * fs * s / 4.0) * (rng.standard_normal(f.size) + 1j * rng.standard_normal(f.size))
    X[0] = 0.0
    if n % 2 == 0:
        X[-1] = X[-1].real * np.sqrt(2)
    return np.fft.irfft(X, n)


def optimal_snr(h, fs, psd_fn):
    """Optimal (matched-filter) SNR rho of a waveform h in noise of one-sided PSD psd_fn:
    rho^2 = 4 * integral_0^inf |h~(f)|^2 / S_n(f) df, with h~(f) the continuous-convention Fourier transform."""
    n = len(h)
    f = np.fft.rfftfreq(n, 1 / fs)
    ht = np.fft.rfft(h) / fs
    df = fs / n
    return float(np.sqrt(4.0 * np.sum(np.abs(ht[1:]) ** 2 / psd_fn(f[1:])) * df))


def chirp_in_noise(fs=4096.0, duration=16.0, t_merger=12.0, mchirp_msun=30.0, target_snr=12.0,
                   f_low=20.0, f_cut=150.0, seed=17):
    """A compact-binary-like chirp of known optimal SNR injected in coloured Gaussian noise (``toy_ligo_psd``).

    Returns dict(t, strain, noise, signal, template, psd_fn, truth). ``template`` is the same chirp (unscaled, the
    waveform ends at its own t=0 merger time shifted to the END of a 2 s array) for matched filtering; ``truth``
    holds t_merger, mchirp_msun, snr_opt and the instantaneous frequency ``f_inst(t)``.
    """
    n = int(round(fs * duration))
    t = np.arange(n) / fs
    h, f_inst = newtonian_chirp(t, t_merger, mchirp_msun, f_low, f_cut)
    scale = target_snr / optimal_snr(h, fs, toy_ligo_psd)
    signal_ = scale * h
    noise = colored_noise(n, fs, toy_ligo_psd, seed)
    tt = np.arange(int(2.0 * fs)) / fs
    template, _ = newtonian_chirp(tt, tt[-1] - 0.05, mchirp_msun, f_low, f_cut)
    return dict(t=t, strain=noise + signal_, noise=noise, signal=signal_, template=template, psd_fn=toy_ligo_psd,
                truth=dict(t_merger=t_merger, mchirp_msun=mchirp_msun, snr_opt=target_snr, f_inst=f_inst,
                           template_merger_index=int(round((tt[-1] - 0.05) * fs))))


def glitch_zoo(n_per_class=100, fs=2048.0, duration=1.0, snr_range=(8.0, 20.0), seed=29):
    """Short white-noise segments that contain nothing (0), a chirp (1), a 'blip' = short sine-Gaussian (2) or a
    narrow-band 'whistle' with a slowly varying frequency (3). Signals are scaled so that their matched-filter SNR
    in unit-variance white noise is drawn uniformly from ``snr_range``. Returns dict(X, y, class_names, fs)."""
    rng = _rng(seed)
    n = int(fs * duration)
    t = np.arange(n) / fs
    names = ["noise", "chirp", "blip", "whistle"]
    X, y = [], []
    for label in range(4):
        for _ in range(n_per_class):
            s = np.zeros(n)
            if label == 1:
                tm = rng.uniform(0.55, 0.9)
                h, _ = newtonian_chirp(t, tm, rng.uniform(20, 45), f_low=25.0, f_cut=rng.uniform(150, 300))
                s = h
            elif label == 2:
                t_c, f0, q = rng.uniform(0.3, 0.7), rng.uniform(100, 400), rng.uniform(5, 12)
                tau = q / (np.sqrt(2) * np.pi * f0)
                s = np.exp(-((t - t_c) / tau) ** 2) * np.sin(2 * np.pi * f0 * (t - t_c))
            elif label == 3:
                t_c, f_c, df = rng.uniform(0.4, 0.6), rng.uniform(200, 500), rng.uniform(30, 120)
                env = np.exp(-0.5 * ((t - t_c) / 0.12) ** 2)
                s = env * np.sin(2 * np.pi * (f_c * t + df * 0.3 * (1 - np.cos(2 * np.pi * 3 * t)) / (2 * np.pi * 3)))
            if label > 0:
                s = s / np.linalg.norm(s) * rng.uniform(*snr_range)
            X.append(s + rng.standard_normal(n))
            y.append(label)
    idx = rng.permutation(len(y))
    return dict(X=np.array(X)[idx], y=np.array(y)[idx], class_names=names, fs=fs)


# ---------------------------------------------------------------------------------------------------------
# 11, 16, 17: radio
# ---------------------------------------------------------------------------------------------------------
def satellite_doppler_pass(f0=437.0e6, d_min_km=700.0, v_rel_kms=7.0, duration_s=120.0, fs=20000.0,
                           snr_db=20.0, seed=37):
    """Complex baseband recording of a LEO beacon during a pass, in the straight-line approximation: the satellite
    moves at ``v_rel_kms`` along a line whose closest approach to the station is ``d_min_km`` (centred on t=0). The slant
    range is r(t) = sqrt(d^2 + (v t)^2) and the Doppler shift  -f0 * (dr/dt) / c  sweeps from positive (approaching)
    to negative (receding). Amplitude falls as 1/r. ``snr_db`` is the SNR at closest approach in the full band fs.
    Returns dict(t, iq (complex64), fs, doppler_hz (truth), range_km (truth)).
    """
    rng = _rng(seed)
    n = int(duration_s * fs)
    t = (np.arange(n) / fs) - duration_s / 2
    d, v = d_min_km * 1e3, v_rel_kms * 1e3
    r = np.sqrt(d**2 + (v * t) ** 2)
    rdot = v**2 * t / r
    doppler = -f0 * rdot / C.c
    phase = 2 * np.pi * np.cumsum(doppler) / fs
    amp = d / r
    sigma = np.sqrt(0.5 * 10 ** (-snr_db / 10))
    iq = amp * np.exp(1j * phase) + sigma * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    return dict(t=t, iq=iq.astype(np.complex64), fs=fs, doppler_hz=doppler, range_km=r / 1e3)


def iq_multiband(fs=2.4e6, duration=0.25, snr_db=15.0, seed=43):
    """An SDR-style wideband IQ capture (complex, ``fs`` samples/s) containing three narrowband signals at known offsets
    from the tuned centre frequency and a DC spike: a 12.5 kHz-wide narrowband-FM voice-like signal at +200 kHz, a
    9.6 kbaud BPSK-like data signal at -350 kHz and a CW tone at +50 kHz. Returns dict(iq, fs, truth).
    """
    rng = _rng(seed)
    n = int(fs * duration)
    t = np.arange(n) / fs
    audio = 0.6 * np.sin(2 * np.pi * 1000 * t) + 0.3 * np.sin(2 * np.pi * 2300 * t)
    fm = np.exp(1j * (2 * np.pi * 200e3 * t + 2 * np.pi * 3e3 * np.cumsum(audio) / fs))
    sps_ = int(fs / 9600)
    bits = rng.integers(0, 2, n // sps_ + 1) * 2 - 1
    nrz = np.repeat(bits, sps_)[:n].astype(float)
    pulse = np.hanning(sps_)
    nrz = sps_signal.fftconvolve(nrz, pulse / pulse.sum(), mode="same")
    bpsk = nrz * np.exp(1j * 2 * np.pi * (-350e3) * t)
    cw = 0.5 * np.exp(1j * 2 * np.pi * 50e3 * t)
    sig = 0.5 * fm + 0.8 * bpsk + cw
    sigma = np.sqrt(0.5 * np.mean(np.abs(sig) ** 2) * 10 ** (-snr_db / 10))
    iq = sig + 0.05 + sigma * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    return dict(iq=iq.astype(np.complex64), fs=fs,
                truth=dict(fm_offset_hz=200e3, fm_audio_hz=(1000.0, 2300.0), bpsk_offset_hz=-350e3,
                           baud=9600.0, cw_offset_hz=50e3))


# ---------------------------------------------------------------------------------------------------------
# 15, 20: flight sensors
# ---------------------------------------------------------------------------------------------------------
def barometer_rocket(fs=20.0, duration=60.0, burn_s=1.8, a_burn=55.0, k_drag=0.002, v_chute=6.0,
                     sigma_pa=12.0, drift_pa=8.0, spike_pa=400.0, seed=41):
    """A model-rocket flight seen by a barometric altimeter: boost, drag-limited coast, apogee, parachute descent.

    Returns dict(t, pressure_pa, alt_true, truth, fs). The sensor adds white noise (``sigma_pa``, about 1 m), a slow
    Gauss-Markov drift (``drift_pa``, 20 s correlation time) and a short positive pressure spike (``spike_pa``) at
    apogee caused by the ejection charge. ``truth`` contains the apogee time and altitude.
    """
    rng = _rng(seed)
    dt = 1e-3
    n_f = int(duration / dt)
    h = np.zeros(n_f)
    v = 0.0
    state = "burn"
    t_apogee = None
    tau_chute = 1.0
    for i in range(1, n_f):
        tcur = i * dt
        if state == "burn":
            acc = a_burn - C.g0 - k_drag * v * abs(v)
            if tcur >= burn_s:
                state = "coast"
        elif state == "coast":
            acc = -C.g0 - k_drag * v * abs(v)
            if v <= 0:
                state, t_apogee = "chute", tcur
        else:
            acc = (-v_chute - v) / tau_chute
        v += acc * dt
        h[i] = max(h[i - 1] + v * dt, 0.0)
        if h[i] == 0.0 and state == "chute":
            v = 0.0
    t_f = np.arange(n_f) * dt
    t = np.arange(int(duration * fs)) / fs
    alt = np.interp(t, t_f, h)
    p = C.p0_std * (1 - 2.25577e-5 * alt) ** 5.25588
    a = np.exp(-(1 / fs) / 20.0)
    drift = sps_signal.lfilter([1.0], [1.0, -a], drift_pa * np.sqrt(1 - a**2) * rng.standard_normal(t.size))
    meas = p + sigma_pa * rng.standard_normal(t.size) + drift
    if t_apogee is not None:
        meas += spike_pa * np.exp(-np.clip(t - t_apogee, 0, None) / 0.1) * (t >= t_apogee)
    return dict(t=t, pressure_pa=meas, alt_true=alt, fs=fs,
                truth=dict(t_apogee=t_apogee, apogee_m=float(h.max()), burn_s=burn_s))


def imu_gps_trajectory(duration=120.0, fs_imu=100.0, fs_gps=1.0, accel_noise=0.15, accel_bias=0.08,
                       gps_noise=3.0, gps_outage=(60.0, 80.0), seed=31):
    """Planar vehicle motion (x, y in metres) with a smooth random acceleration, observed by an accelerometer pair
    (noise + constant-ish bias + slow random walk, units m/s^2, at ``fs_imu``) and a GPS position fix at ``fs_gps``
    (white noise ``gps_noise`` m per axis) which is lost (NaN) during ``gps_outage``.

    Returns dict(t_imu, accel (n,2), t_gps, gps (m,2) with NaN, truth) where truth holds pos, vel, acc at IMU rate,
    the accelerometer bias and the noise parameters (use them for the Kalman-filter Q and R).
    """
    rng = _rng(seed)
    n = int(duration * fs_imu)
    dt = 1.0 / fs_imu
    t = np.arange(n) * dt
    a_ou = np.exp(-dt / 5.0)
    drive = 1.0 * np.sqrt(1 - a_ou**2) * rng.standard_normal((n, 2))
    acc = sps_signal.lfilter([1.0], [1.0, -a_ou], drive, axis=0)
    vel = np.array([50.0, 0.0]) + np.cumsum(acc, axis=0) * dt
    pos = np.cumsum(vel, axis=0) * dt
    bias = accel_bias * np.array([1.0, -0.7]) + np.cumsum(1e-3 * np.sqrt(dt) * rng.standard_normal((n, 2)), axis=0)
    meas = acc + bias + accel_noise * rng.standard_normal((n, 2))
    step = int(fs_imu / fs_gps)
    t_gps = t[::step]
    gps = pos[::step] + gps_noise * rng.standard_normal((t_gps.size, 2))
    out = (t_gps >= gps_outage[0]) & (t_gps < gps_outage[1])
    gps[out] = np.nan
    return dict(t_imu=t, accel=meas, t_gps=t_gps, gps=gps,
                truth=dict(pos=pos, vel=vel, acc=acc, bias=bias, accel_noise=accel_noise, gps_noise=gps_noise,
                           gps_outage=gps_outage))


# ---------------------------------------------------------------------------------------------------------
# 24: spectra
# ---------------------------------------------------------------------------------------------------------
STELLAR_LINES_NM = (656.3, 589.3, 517.3, 486.1, 434.0)


def stellar_spectra(n_normal=500, n_anomalous=10, n_bins=256, noise=0.01, seed=47):
    """Normalised optical spectra (400-700 nm) of 'ordinary' stars (smooth continuum with five absorption lines of
    random depth) plus a few anomalous objects (an emission line, a broad extra absorption trough, or a cosmic-ray
    spike). Returns dict(wavelength_nm, X, y, anomaly_type) with y = 1 for anomalies."""
    rng = _rng(seed)
    wl = np.linspace(400.0, 700.0, n_bins)

    def one(kind=None):
        T = rng.uniform(0.8, 1.2)
        cont = (wl / 550.0) ** (-2.0 * T) * np.exp(-(wl / 900.0) * (T - 1))
        cont = cont / cont.mean()
        flux = cont.copy()
        for lam in STELLAR_LINES_NM:
            depth, width = rng.uniform(0.1, 0.4), rng.uniform(1.5, 3.0)
            flux = flux - depth * cont * np.exp(-0.5 * ((wl - lam) / width) ** 2)
        if kind == "emission":
            lam = rng.uniform(430, 680)
            flux = flux + rng.uniform(0.3, 0.8) * np.exp(-0.5 * ((wl - lam) / 2.0) ** 2)
        elif kind == "trough":
            lam = rng.uniform(430, 680)
            flux = flux - rng.uniform(0.15, 0.35) * np.exp(-0.5 * ((wl - lam) / 12.0) ** 2)
        elif kind == "cosmic":
            flux[rng.integers(0, n_bins, 2)] += rng.uniform(1.0, 3.0)
        return flux + noise * rng.standard_normal(n_bins)

    X = [one() for _ in range(n_normal)]
    kinds = [None] * n_normal
    for k in range(n_anomalous):
        kind = ["emission", "trough", "cosmic"][k % 3]
        X.append(one(kind))
        kinds.append(kind)
    y = np.array([0] * n_normal + [1] * n_anomalous)
    idx = rng.permutation(len(y))
    return dict(wavelength_nm=wl, X=np.array(X)[idx], y=y[idx], anomaly_type=[kinds[i] for i in idx])
