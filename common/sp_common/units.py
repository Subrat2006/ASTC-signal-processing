"""Conversions used all over signal processing: decibels, rad/s <-> Hz, noise, link-budget helpers.

Frequencies are *ordinary* frequencies f (Hz) unless the function name says 'angular'.
"""
import numpy as np
from . import constants as C


def db10(x):
    """10 log10(x): decibels of a POWER ratio."""
    return 10.0 * np.log10(np.asarray(x, dtype=float))


def db20(x):
    """20 log10(|x|): decibels of an AMPLITUDE ratio."""
    return 20.0 * np.log10(np.abs(np.asarray(x, dtype=float)))


def from_db10(x_db):
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def from_db20(x_db):
    return 10.0 ** (np.asarray(x_db, dtype=float) / 20.0)


def dbm_to_watt(p_dbm):
    return 1e-3 * from_db10(p_dbm)


def watt_to_dbm(p_w):
    return db10(np.asarray(p_w, dtype=float) / 1e-3)


def hz_to_angular(f_hz):
    return 2.0 * np.pi * np.asarray(f_hz, dtype=float)


def angular_to_hz(w_rad_s):
    return np.asarray(w_rad_s, dtype=float) / (2.0 * np.pi)


def normalised_freq(f_hz, fs):
    """Cycles per sample, f / fs (so Nyquist is 0.5). SciPy's `Wn` is f / (fs / 2) instead!"""
    return np.asarray(f_hz, dtype=float) / fs


def thermal_noise_power_w(bandwidth_hz, T_K=C.T0):
    """Available thermal (Johnson) noise power k_B T B in watts."""
    return C.kB * T_K * np.asarray(bandwidth_hz, dtype=float)


def thermal_noise_dbm(bandwidth_hz, T_K=C.T0):
    return watt_to_dbm(thermal_noise_power_w(bandwidth_hz, T_K))


def johnson_voltage_density(R_ohm, T_K=C.T0):
    """Open-circuit thermal noise voltage density sqrt(4 k_B T R) in V / sqrt(Hz)."""
    return np.sqrt(4.0 * C.kB * T_K * np.asarray(R_ohm, dtype=float))


def doppler_shift_hz(f_carrier_hz, range_rate_m_s):
    """First-order Doppler shift. Positive range rate (receding) gives a NEGATIVE shift."""
    return -np.asarray(f_carrier_hz, dtype=float) * np.asarray(range_rate_m_s, dtype=float) / C.c


def free_space_path_loss_db(distance_m, f_hz):
    """Friis free-space path loss 20 log10(4 pi d f / c) in dB."""
    return db20(4.0 * np.pi * np.asarray(distance_m, dtype=float) * np.asarray(f_hz, dtype=float) / C.c)


def baro_altitude_m(p_pa, p_ground_pa=C.p0_std):
    """International-standard-atmosphere altitude above the reference pressure (troposphere formula)."""
    return 44330.77 * (1.0 - (np.asarray(p_pa, dtype=float) / p_ground_pa) ** 0.190263)
