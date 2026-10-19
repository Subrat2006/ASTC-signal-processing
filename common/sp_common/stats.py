"""Statistics helpers needed in nearly every problem: confidence intervals, fits, error measures."""
import numpy as np
from scipy import optimize, stats as sps


def wilson_interval(k, n, conf=0.95):
    """Wilson score interval for a binomial proportion k/n (good for small false-alarm rates)."""
    z = sps.norm.ppf(0.5 + conf / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


def bootstrap_ci(data, stat=np.mean, n_boot=2000, conf=0.95, rng=None):
    """Percentile bootstrap confidence interval of statistic `stat` of 1-D `data`."""
    rng = np.random.default_rng(0) if rng is None else rng
    data = np.asarray(data)
    boots = np.array([stat(rng.choice(data, size=data.size, replace=True)) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [50 * (1 - conf), 100 - 50 * (1 - conf)])
    return lo, hi


def fit_with_ci(f, x, y, p0, sigma=None, conf=0.95, **kw):
    """curve_fit wrapper returning (popt, half-width of the confidence interval of each parameter)."""
    popt, pcov = optimize.curve_fit(f, x, y, p0=p0, sigma=sigma, absolute_sigma=sigma is not None, **kw)
    dof = max(1, len(x) - len(popt))
    t = sps.t.ppf(0.5 + conf / 2, dof)
    return popt, t * np.sqrt(np.diag(pcov))


def rel_error(measured, exact):
    return np.abs(np.asarray(measured) - np.asarray(exact)) / np.abs(exact)


def rmse(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.sqrt(np.mean((a - b) ** 2)))


def snr_db(clean, estimate):
    """Output SNR in dB of an estimate against the known clean signal: 10 log10(sum clean^2 / sum err^2)."""
    clean, estimate = np.asarray(clean, dtype=float), np.asarray(estimate, dtype=float)
    return float(10 * np.log10(np.sum(clean**2) / np.sum((estimate - clean) ** 2)))


def fit_slope(x, y):
    """Slope of log10(y) versus log10(x): scaling exponents, convergence orders, spectral slopes."""
    return float(np.polyfit(np.log10(x), np.log10(y), 1)[0])
