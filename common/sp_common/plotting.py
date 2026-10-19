"""Matplotlib defaults: readable, labelled figures with units, saved consistently."""
from pathlib import Path
import matplotlib.pyplot as plt


def set_style():
    plt.rcParams.update({
        "figure.figsize": (7.0, 4.0), "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
        "axes.grid": True, "grid.alpha": 0.3, "axes.labelsize": 11, "legend.frameon": False,
        "font.size": 10, "lines.linewidth": 1.4,
    })


def savefig(fig, name, folder="figures"):
    """Save to <folder>/<name>.png and .pdf, creating the folder if needed."""
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}")
    return out / f"{name}.png"
