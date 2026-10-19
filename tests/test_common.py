import numpy as np
import pytest
from sp_common import constants as C, units, stats, rng


def test_boltzmann_dbw():
    assert C.kB_dBW_per_K_Hz == pytest.approx(-228.6, abs=0.05)


def test_gm_sun_over_c3():
    assert C.T_sun == pytest.approx(4.925e-6, rel=1e-3)


def test_db_roundtrip():
    assert units.db10(100.0) == pytest.approx(20.0)
    assert units.db20(10.0) == pytest.approx(20.0)
    assert units.from_db10(units.db10(3.7)) == pytest.approx(3.7)
    assert units.from_db20(units.db20(0.42)) == pytest.approx(0.42)


def test_dbm():
    assert units.watt_to_dbm(1e-3) == pytest.approx(0.0)
    assert units.dbm_to_watt(30.0) == pytest.approx(1.0)


def test_thermal_noise_floor():
    assert units.thermal_noise_dbm(1.0, 290.0) == pytest.approx(-174.0, abs=0.1)


def test_johnson_noise_1kohm():
    assert units.johnson_voltage_density(1e3, 290.0) == pytest.approx(4.0e-9, rel=0.02)


def test_leo_max_doppler():
    assert abs(units.doppler_shift_hz(437e6, 7.0e3)) == pytest.approx(10.2e3, rel=0.02)


def test_fspl_leo_uhf():
    assert units.free_space_path_loss_db(1000e3, 437e6) == pytest.approx(145.2, abs=0.3)


def test_baro_altitude_1000m():
    p = 101325.0 * (1 - 2.25577e-5 * 1000.0) ** 5.25588
    assert units.baro_altitude_m(p) == pytest.approx(1000.0, abs=1.0)


def test_wilson_contains_p():
    lo, hi = stats.wilson_interval(5, 1000)
    assert lo < 0.005 < hi


def test_fit_slope_exact_power_law():
    x = np.array([1.0, 10.0, 100.0])
    assert stats.fit_slope(x, 3 * x**-2.0) == pytest.approx(-2.0)


def test_snr_db_known():
    x = np.ones(100)
    assert stats.snr_db(x, x + 0.1) == pytest.approx(20.0)


def test_fit_with_ci_recovers_slope():
    r = rng.get_rng(1)
    x = np.linspace(0, 1, 50)
    y = 2 * x + 1 + 0.01 * r.standard_normal(50)
    popt, ci = stats.fit_with_ci(lambda x, a, b: a * x + b, x, y, p0=[1, 0])
    assert abs(popt[0] - 2) < ci[0] * 2
