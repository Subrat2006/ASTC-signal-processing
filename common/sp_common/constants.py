"""Physical and engineering constants in SI units (CODATA via SciPy)."""
from scipy import constants as _c

c = _c.c                      # m / s, speed of light
kB = _c.k                     # J / K, Boltzmann constant
h = _c.h                      # J s
e = _c.e                      # C
G = _c.G                      # m^3 kg^-1 s^-2
g0 = 9.80665                  # m / s^2, standard gravity
M_sun = 1.98847e30            # kg
T_sun = G * M_sun / c**3      # s, GM_sun/c^3 (about 4.925e-6 s): the natural time unit of gravitational waves
R_earth = 6.371e6             # m, mean Earth radius
mu_earth = 3.986004418e14     # m^3 / s^2, Earth's gravitational parameter
T0 = 290.0                    # K, IEEE reference noise temperature
kB_dBW_per_K_Hz = 10 * __import__("math").log10(kB)   # about -228.6 dBW / K / Hz
p0_std = 101325.0             # Pa, standard sea-level pressure
