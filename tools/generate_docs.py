#!/usr/bin/env python3
"""Regenerate every derived document of the repository from the problem statements.

Outputs
    README.md                      main entry point
    docs/CURRICULUM.md             theory and hands-on skills per problem
    docs/Curriculum_Roadmap.tex    LaTeX source of the roadmap PDF (built by tools/build_pdfs.sh)
    docs/images/roadmap.png        prerequisite graph
    PROGRESS.md                    progress tracker (created once; never overwritten)
    solutions/README.md            how to organise a solution
    solutions/NN_slug/README.md    per-problem template (only created if missing)

Run:  python tools/generate_docs.py
"""
from pathlib import Path
import textwrap

from problem_meta import ROOT, PARTS, LEVELS, CAPSTONE_ID, load_problems, closure

PROBLEMS = load_problems()
BYID = {p["id"]: p for p in PROBLEMS}
N = len(PROBLEMS)
TOTAL_H = sum(p["hours"] for p in PROBLEMS)

PART_BLURB = {
    "A": ("What a signal is, how a sensor corrupts it, and what sampling does to it.",
          "You learn to describe a signal by its power and noise, to calibrate a sensor, to separate white noise from "
          "drift with the Allan deviation, and to predict, avoid and exploit aliasing. After Part A you can look at any "
          "raw sensor stream and say how good it is and at what rate it must be sampled."),
    "B": ("The mathematics that every later method rests on.",
          "You build convolution and LTI-system thinking, the Fourier transform and its uncertainty principle, the Laplace "
          "and z-transforms with pole-zero reasoning and stability, and the statistics of random signals including power "
          "spectra and Poisson counting. After Part B you can derive, not just use, the formulas of signal processing."),
    "C": ("The electronics in front of the processor.",
          "You design analog filters and verify them with your own circuit solver, size a low-noise sensor front end and "
          "a lock-in detector, choose and test ADCs and DACs, and build the physical layer of a satellite telemetry link "
          "with its Doppler shift, carrier recovery and link budget."),
    "D": ("Digital signal processing, from the FFT to Kalman filtering.",
          "You write the FFT, understand windows and spectral scaling, estimate spectra of noise and of unevenly sampled "
          "data, design FIR and IIR filters for real-time use, resample and down-convert radio signals, analyse chirps in "
          "time and frequency, clean data without biasing it, build matched filters with calibrated false-alarm rates, "
          "and fuse sensors with adaptive filters and Kalman filters."),
    "E": ("Machine learning on signals, done honestly, and a capstone.",
          "You engineer features and avoid the leakage trap, detect anomalies and bursts with clustering and "
          "isolation methods, train convolutional networks and benchmark them against the optimal matched filter, build "
          "autoencoders for denoising and novelty detection, and finally assemble an end-to-end transient-detection "
          "pipeline with calibrated significance and a report."),
}

HANDOFFS = [
    ("01", "20, 22, 24", "Noise densities and Allan parameters (ARW, bias instability) that set Kalman Q and detector baselines"),
    ("02", "10, 14, 16", "Alias prediction, sampling-rate rules, jitter-limited SNR"),
    ("03", "04, 19", "Convolution and correlation code, impulse-response identification, delay estimation"),
    ("04", "12, 13, 17", "Transform pairs, uncertainty principle, harmonic-line reading of rotating machinery"),
    ("05", "06, 08, 15", "Poles and zeros, second-order metrics, the satellite attitude-loop model"),
    ("06", "14, 15, 20", "s-to-z mappings, difference-equation implementations, sample-rate limits of discrete loops"),
    ("07", "09, 13, 18, 19, 22", "PSD scaling, AR and 1/f noise generators, Poisson statistics and tail probabilities"),
    ("08", "09, 10, 15", "Filter families, Sallen-Key design, anti-alias specification"),
    ("09", "10, 20", "Noise-budget method, digital lock-in implementation"),
    ("10", "16, 21", "ENOB and SQNR methods, the sigma-delta modulator (decimated with a CIC filter in 16)"),
    ("11", "16, 17, 19, 25", "Matched-filter BER, Doppler model fit, link-budget calculation"),
    ("12", "13, 14, 17, 21", "Window figures of merit, correct amplitude and PSD scaling, peak interpolation"),
    ("13", "17, 18, 19, 21", "Welch and multitaper estimators, Lomb-Scargle periodogram, confidence intervals"),
    ("14", "15, 16, 20", "FIR design toolbox, overlap-add filtering, delay budgets"),
    ("15", "20, 25", "Real-time causal filtering, apogee detector, fixed-point biquads"),
    ("16", "25", "Digital down-converter chain, polyphase resampling, CIC filters"),
    ("17", "18, 19, 23", "STFT code, whitening pipeline, chirp-law fit"),
    ("18", "21, 22, 24, 25", "Bias-aware cleaning pipeline (clip, flatten, denoise)"),
    ("19", "22, 23, 25", "Matched-filter SNR series, background calibration, trials factor, ROC tools"),
    ("20", "25", "Kalman filter and consistency tests (NIS and NEES)"),
    ("21", "22, 23, 24", "Feature library, group cross-validation, threshold selection"),
    ("22", "24, 25", "Detector comparison at fixed false-alarm rate, injection-recovery harness"),
    ("23", "24", "Training loops and the benchmark against the matched filter"),
    ("24", "25", "Autoencoder detector and the contamination study"),
]

DATASETS = [
    ("01", "`sensor_signal`, `gyro_noise`", "Phyphox smartphone logs; EuRoC MAV IMU", "https://phyphox.org · https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets"),
    ("02", "plain NumPy tones", "Phyphox accelerometer at several rates; Kepler long and short cadence (MAST)", "https://phyphox.org · https://archive.stsci.edu"),
    ("03", "`scipy.signal.max_len_seq`, simulated structure", "Ruler-twang accelerometer record; balloon-pop room impulse response", "recorded by you with Phyphox"),
    ("04", "`bearing_vibration(fault='none')`", "SILSO sunspot number; CWRU normal baseline; your own audio", "https://www.sidc.be/SILSO/ · https://engineering.case.edu/bearingdatacenter"),
    ("05", "analytic systems", "your own ringing or pendulum record (from 03)", "recorded by you"),
    ("06", "`sensor_signal` plus mains tone", "optional microcontroller ADC stream", "recorded by you"),
    ("07", "`grb_event_list`, AR and 1/f noise", "Fermi GBM TTE data; AstroSat CZTI event files; TESS/Kepler photon-noise light curves", "https://heasarc.gsfc.nasa.gov · https://astrobrowse.issdc.gov.in/astro_archive/archive/Home.jsp"),
    ("08", "analytic transfer functions", "bench measurement of your own RC / Sallen-Key filter", "measured by you"),
    ("09", "`lockin_signal`", "optional chopped-photodiode experiment", "measured by you"),
    ("10", "tones through your quantiser", "sound-card loop-back recording", "recorded by you"),
    ("11", "`satellite_doppler_pass`", "SatNOGS observations of 437 MHz beacons", "https://db.satnogs.org"),
    ("12", "`bearing_vibration`", "CWRU normal baseline; fan vibration via Phyphox", "https://engineering.case.edu/bearingdatacenter"),
    ("13", "`uneven_variable_star`, `transit_lightcurve`", "SILSO sunspots; AAVSO photometry; TESS via Lightkurve", "https://www.sidc.be/SILSO/ · https://www.aavso.org · https://lightkurve.github.io/lightkurve/"),
    ("14", "`sensor_signal`, `bearing_vibration`", "smartphone accelerometer while walking; MIT-BIH ECG", "https://physionet.org/content/mitdb/1.0.0/"),
    ("15", "`barometer_rocket`", "smartphone barometer on a staircase", "recorded by you"),
    ("16", "`iq_multiband`", "RTL-SDR capture of broadcast FM", "captured by you"),
    ("17", "`chirp_in_noise`, `satellite_doppler_pass`", "GW150914 strain (GWOSC); SatNOGS waterfall", "https://gwosc.org · https://db.satnogs.org"),
    ("18", "`transit_lightcurve`, `grb_event_list`", "Kepler/TESS light curve (Kepler-10, Kepler-5, WASP-18); MIT-BIH ECG", "https://archive.stsci.edu"),
    ("19", "`chirp_in_noise`, `colored_noise`", "GW150914 H1 and L1 strain", "https://gwosc.org"),
    ("20", "`imu_gps_trajectory`", "EuRoC MAV IMU and ground truth; ADS-B tracks (OpenSky or your own receiver)", "https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets · https://opensky-network.org"),
    ("21", "`bearing_dataset`", "CWRU bearing files; HTRU2 pulsar candidates (UCI)", "https://engineering.case.edu/bearingdatacenter · https://archive.ics.uci.edu"),
    ("22", "`grb_event_list`, `stellar_spectra`", "AstroSat CZTI or Fermi GBM event files", "https://astrobrowse.issdc.gov.in/astro_archive/archive/Home.jsp · https://heasarc.gsfc.nasa.gov"),
    ("23", "`glitch_zoo`, `bearing_dataset`", "Gravity Spy glitch images; CWRU", "https://gravityspy.org"),
    ("24", "`stellar_spectra`, `grb_event_list`", "SDSS spectra; NASA SMAP/MSL telemetry anomalies", "https://skyserver.sdss.org · https://github.com/khundman/telemanom"),
    ("25", "all generators, per track", "your chosen real event (GRB, transit, GW, SatNOGS pass or flight log)", "see problems 07, 13, 17-19, 22"),
]


def pdf_link(p):
    return f"problems/{p['folder']}/{Path(p['pdf']).name}"


def tex_link(p):
    return f"problems/{p['folder']}/{Path(p['tex']).name}"


# ----------------------------------------------------------------------------------------
# roadmap figure
# ----------------------------------------------------------------------------------------
SHORT = {1: "Signals, sensors, noise", 2: "Sampling, aliasing", 3: "Convolution, LTI systems",
         4: "Fourier series, transform", 5: "Laplace, stability", 6: "Z-transform, discrete systems",
         7: "Random signals, PSD", 8: "Analog filters", 9: "Sensor conditioning, noise",
         10: "ADC, DAC, sigma-delta", 11: "Modulation, telemetry links", 12: "DFT, FFT, windows",
         13: "Spectral estimation", 14: "FIR filter design", 15: "IIR, real-time filters",
         16: "Multirate, SDR front end", 17: "Time-frequency analysis", 18: "Denoising, data cleaning",
         19: "Matched filters, detection", 20: "Adaptive filters, Kalman", 21: "Features, classical ML",
         22: "Clustering, anomalies", 23: "Deep learning for signals", 24: "Autoencoders",
         25: "Capstone pipeline"}


def make_roadmap_png():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

    colors = {"A": "#2b6cb0", "B": "#2f855a", "C": "#c05621", "D": "#6b46c1", "E": "#b83280"}

    def pre_of(p):
        return [CAPSTONE_ID - 1] if p["id"] == CAPSTONE_ID else p["prereqs"]

    layer = {}
    for p in PROBLEMS:
        pre = pre_of(p)
        layer[p["id"]] = 0 if not pre else 1 + max(layer[q] for q in pre)
    cols = {}
    for pid, l in layer.items():
        cols.setdefault(l, []).append(pid)
    dx = 1.5
    fig, ax = plt.subplots(figsize=(21, 7.4))
    pos = {}
    for l, ids in cols.items():
        n = len(ids)
        for k, pid in enumerate(sorted(ids)):
            pos[pid] = (l * dx, (n - 1) / 2 - k)
    maxy = max(abs(y) for _, y in pos.values())
    for p in PROBLEMS:
        for q in pre_of(p):
            x0, y0 = pos[q]
            x1, y1 = pos[p["id"]]
            ax.add_patch(FancyArrowPatch((x0 + 0.62, y0), (x1 - 0.62, y1), arrowstyle="-|>", mutation_scale=8,
                                         connectionstyle="arc3,rad=0.08", color="#555", alpha=0.28, lw=0.8))
    for p in PROBLEMS:
        x, y = pos[p["id"]]
        ax.add_patch(FancyBboxPatch((x - 0.66, y - 0.38), 1.32, 0.76, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=colors[p["part"]], ec="white", lw=1.5, zorder=3))
        ax.text(x, y + 0.14, p["nn"], ha="center", va="center", color="white", fontsize=11, fontweight="bold", zorder=4)
        ax.text(x, y - 0.12, textwrap.fill(SHORT[p["id"]], 17), ha="center", va="center", color="white", fontsize=6.2,
                zorder=4, linespacing=0.95)
    ax.legend(handles=[Patch(color=colors[k], label=f"Part {k}: {v}") for k, v in PARTS.items()], loc="upper center",
              bbox_to_anchor=(0.5, 1.06), ncol=3, frameon=False, fontsize=9.5)
    ax.text((max(layer.values()) * dx) / 2, -maxy - 0.85,
            "Arrows point from a prerequisite to the problem that builds on it. The capstone (25) needs at least ten earlier problems.",
            ha="center", fontsize=8.5, color="#444")
    ax.set_xlim(-1, max(layer.values()) * dx + 1)
    ax.set_ylim(-maxy - 1.2, maxy + 1.4)
    ax.axis("off")
    out = ROOT / "docs" / "images" / "roadmap.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


# ----------------------------------------------------------------------------------------
# CURRICULUM.md
# ----------------------------------------------------------------------------------------
def curriculum_md():
    out = []
    out.append("# Curriculum: theory and practical experience\n")
    out.append(
        "This document is the plan behind the problem statements. It was written *first*, before any problem: "
        "for each topic it fixes the **theory** that must be understood and the **hands-on skill** that must be "
        "acquired, and the problems were then designed so that every theory item is *used*, not just read.\n")
    out.append("## Design principles\n")
    out.append(
        "1. **Derive by hand, then verify by code.** Every problem contains short analytic derivations and a "
        "self-check target that the simulation must reproduce before any result is trusted.\n"
        "2. **Real problems, real data, known truth.** Each problem has a synthetic generator with *known ground "
        "truth* (so you can measure bias, error and false alarms) and pointers to *real datasets* (so you can see "
        "what the textbook model leaves out). Develop on the first, confirm on the second.\n"
        "3. **Each problem hands numbers to the next.** Noise densities, filter designs and detectors are reused "
        "later, so the ladder is one connected toolbox, not 25 unrelated exercises. See the hand-off table below.\n"
        "4. **Aerospace first.** Each problem ends with an *Aerospace Application Link*: the signal-processing "
        "result is carried to a number that matters for a satellite, a rocket, a ground station or a detector.\n"
        "5. **Honest statistics.** Error bars, false-alarm rates, injection-recovery curves and bias measurements "
        "are required; a modest, correctly analysed result scores higher than a polished but unvalidated one.\n"
        "6. **From sensors to machine learning, in that order.** Machine learning appears only after the "
        "physics and the classical optimum (the matched filter, the Kalman filter) are understood, so that a "
        "network is always benchmarked against something that is provably good.\n")
    out.append("## Theory and hands-on skills, problem by problem\n")
    out.append("| # | Problem | Theory to master | Hands-on skills gained | Effort |")
    out.append("|---|---|---|---|---|")
    for p in PROBLEMS:
        out.append(f"| {p['nn']} | [{p['title']}]({pdf_link(p).replace('problems/', '../problems/')}) | {p['theory']} | "
                   f"{p['skills']} | {p['effort']} |")
    out.append("")
    out.append("## Tasks in each problem\n")
    for p in PROBLEMS:
        out.append(f"**{p['nn']} {p['title']}** — " + "; ".join(f"{i+1}) {t}" for i, t in enumerate(p["task_titles"])) + "\n")
    out.append("## Number hand-offs between problems\n")
    out.append("| From | Used in | What is handed over |")
    out.append("|---|---|---|")
    for a, b, c in HANDOFFS:
        out.append(f"| {a} | {b} | {c} |")
    out.append("")
    out.append("## What you can do after each part\n")
    for k, (name, desc) in PART_BLURB.items():
        ids = [p["nn"] for p in PROBLEMS if p["part"] == k]
        out.append(f"**Part {k} ({ids[0]}–{ids[-1]}): {name}** {desc}\n")
    out.append("## Level scale\n")
    out.append("| Level | Meaning |\n|---|---|")
    out.append("| 1 Foundations | Needs only basic Python and school mathematics. |")
    out.append("| 2 Core | Uses results of earlier problems; standard textbook methods. |")
    out.append("| 3 Advanced | Combines several earlier problems; open-ended analysis. |")
    out.append("| 4 Expert | Statistical or system-level work; critical assessment expected. |")
    out.append("| 5 Capstone | Integration of the whole ladder on a real event. |")
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------------------
# DATASETS.md
# ----------------------------------------------------------------------------------------
def datasets_md():
    out = ["# Datasets: synthetic generators and real data\n",
           "Every problem can be started offline: `sp_common.synth` contains seeded generators that return the signal *and* "
           "the ground truth. They are models of real instruments, simplified on purpose; say so in your report. The "
           "real datasets in the right column are the final test of every method. Do **not** commit large raw data files "
           "(they are git-ignored under `data/raw/`); record the download recipe and a checksum instead.\n",
           "> **Check links before relying on them.** The links were written from memory of well-known public archives and "
           "could not be opened while this repository was being prepared. If one has moved, search for the dataset name; "
           "the archive itself is real, but the page may have changed.\n",
           "| # | Synthetic generator (`sp_common.synth`) | Real data to use | Where |", "|---|---|---|---|"]
    for nn, syn, real, where in DATASETS:
        out.append(f"| {nn} | {syn} | {real} | {where} |")
    out += ["",
            "## Generators at a glance",
            "",
            "| Function | What it models | Ground truth returned |",
            "|---|---|---|",
            "| `sensor_signal` | tone in white noise, drift, spikes | clean signal |",
            "| `gyro_noise` | rate gyroscope at rest: white noise, bias drift, rate random walk | each noise component |",
            "| `lockin_signal` | 1 mV tone at -40 dB SNR with mains pickup and 1/f noise | amplitude, phase, frequency |",
            "| `grb_event_list` | photon events of a gamma-ray burst on a drifting background (time, energy, quadrant) | burst parameters, true rate function, per-photon burst flag |",
            "| `transit_lightcurve` | Kepler/TESS-like light curve with transits, variability, systematics, outliers, gaps | transit model, in-transit and outlier masks |",
            "| `uneven_variable_star` | irregularly sampled pulsating star | period, amplitude |",
            "| `bearing_vibration`, `bearing_dataset` | rolling-bearing accelerometer data; labelled dataset with per-recording nuisance | fault frequency, class, recording id |",
            "| `chirp_in_noise`, `glitch_zoo`, `toy_ligo_psd`, `newtonian_chirp`, `colored_noise`, `optimal_snr` | inspiral chirp in coloured noise and short transients | injected optimal SNR, merger time, frequency track |",
            "| `satellite_doppler_pass`, `iq_multiband` | LEO beacon with Doppler, wideband SDR capture | Doppler curve, offsets of each signal |",
            "| `barometer_rocket` | model-rocket barometer with drift and an ejection-charge spike | altitude, apogee time and height |",
            "| `imu_gps_trajectory` | planar vehicle with biased accelerometer and GPS with outage | position, velocity, bias, noise parameters |",
            "| `stellar_spectra` | normalised spectra with emission, trough and cosmic-ray anomalies | labels and anomaly type |",
            ""]
    return "\n".join(out)


# ----------------------------------------------------------------------------------------
# roadmap PDF source
# ----------------------------------------------------------------------------------------
def latex_escape(s):
    return s.replace("&", "\\&").replace("_", "\\_").replace("#", "\\#").replace("%", "\\%").replace("–", "--")


def roadmap_tex():
    rows = []
    for p in PROBLEMS:
        rows.append(
            f"{p['nn']} & \\textbf{{{latex_escape(p['title'])}}} & {latex_escape(p['theory'])} & "
            f"{latex_escape(p['skills'])} & {latex_escape(p['effort'])}\\\\\\midrule")
    hand = "\n".join(f"{a} & {latex_escape(b)} & {latex_escape(c)}\\\\" for a, b, c in HANDOFFS)
    parts = "\n".join(
        f"\\textbf{{Part {k}: {latex_escape(PARTS[k])}.}} {latex_escape(PART_BLURB[k][1])}\\par\\smallskip"
        for k in PARTS)
    return textwrap.dedent(r"""
    \documentclass[11pt,a4paper,landscape]{article}
    \usepackage{spl}
    \geometry{left=1.8cm,right=1.8cm,top=2.4cm,bottom=2.0cm}
    \begin{document}
    \fancyhead[L]{\small Signal Processing}\fancyhead[R]{\small Curriculum and Roadmap}
    \begin{center}
      {\LARGE\bfseries Aeronautics and Space Technology Club\par}
      {\Large\bfseries IIT (ISM) Dhanbad\par}\vspace{6pt}
      {\large Signal Processing Ladder: Curriculum, Theory and Hands-On Skills\par}
    \end{center}
    \begin{summarybox}{A Ladder of @@N@@ Problem Statements in Signal Processing}
    Each problem is a self-contained, hands-on problem statement with a synthetic dataset of known truth and pointers to real data.
    Together they take a student from the first noisy sensor reading to an end-to-end transient-detection pipeline, passing
    through sampling, the mathematics of signals and systems, analog and digital electronics, DSP, detection and estimation theory
    and machine learning. Total estimated effort: about @@TOTAL@@ hours.
    \end{summarybox}
    \section*{Roadmap}
    \begin{center}\includegraphics[width=0.98\linewidth]{images/roadmap.png}\end{center}
    \section*{What You Can Do After Each Part}
    @@PARTS@@
    \section*{Theory and Hands-On Skills by Problem}
    {\small\renewcommand{\arraystretch}{1.25}
    \begin{longtable}{@{}p{0.6cm}p{3.7cm}p{8.2cm}p{7.6cm}p{2.0cm}@{}}
    \toprule \textbf{\#} & \textbf{Problem} & \textbf{Theory to master} & \textbf{Hands-on skills gained} & \textbf{Effort}\\\midrule
    \endhead
    @@ROWS@@
    \bottomrule\end{longtable}}
    \section*{Number Hand-Offs Between Problems}
    {\small\renewcommand{\arraystretch}{1.2}
    \begin{longtable}{@{}p{1.6cm}p{3.6cm}p{17cm}@{}}
    \toprule \textbf{From} & \textbf{Used in} & \textbf{What is handed over}\\\midrule\endhead
    @@HAND@@
    \bottomrule\end{longtable}}
    \end{document}
    """).replace("@@N@@", str(N)).replace("@@TOTAL@@", f"{round(TOTAL_H, -1):.0f}").replace("@@PARTS@@", parts) \
        .replace("@@ROWS@@", "\n".join(rows)).replace("@@HAND@@", hand)


# ----------------------------------------------------------------------------------------
# PROGRESS.md + solution templates
# ----------------------------------------------------------------------------------------
def detect_status(p):
    d = ROOT / "solutions" / p["folder"]
    has_nb = any(d.glob("*.ipynb"))
    has_rep = any(d.glob("report.*"))
    if has_nb and has_rep:
        return "Submitted"
    if has_nb or has_rep:
        return "In progress"
    return "Not started"


def progress_md():
    out = ["# Progress tracker\n",
           "Status is detected automatically by `python tools/update_progress.py` (notebook present = *In progress*; "
           "notebook **and** `report.md`/`report.pdf` present = *Submitted*). Fill in the scores and the comment by hand; "
           "they are preserved when this file is refreshed. Comment = the single most surprising thing you learned.\n",
           "| # | Problem | Level | Status | Self-score /100 | Mentor score /100 | Comment |",
           "|---|---|---|---|---|---|---|"]
    for p in PROBLEMS:
        out.append(f"| {p['nn']} | [{p['title']}]({pdf_link(p)}) | {p['level']} | {detect_status(p)} |  |  |  |")
    out.append("")
    out.append(f"Total estimated effort for the whole ladder: about {round(TOTAL_H, -1):.0f} hours.\n")
    return "\n".join(out)


def solution_readme(p):
    deliv = "\n".join(f"- [ ] **{k}**: {t}" for k, t in p["deliverables"])
    tasks = "\n".join(f"- [ ] Task {i+1}: {t}" for i, t in enumerate(p["task_titles"]))
    return f"""# Solution {p['nn']}: {p['title']}

> Problem statement: [`{pdf_link(p).replace('problems/', '../../problems/')}`]({pdf_link(p).replace('problems/', '../../problems/')})
> Level {p['level']} ({LEVELS[p['level']]}) · estimated effort {p['effort']} · prerequisites: {p['prereq_text']}

## Status

- [ ] Stage 1 – Think (derivations done by hand, units and sampling rates written down)
- [ ] Stage 2 – Build (core code working and validated against analytic results)
- [ ] Stage 3 – Experiment (sweeps, stress tests, real data)
- [ ] Stage 4 – Refine (analysis and memo written, folder clean)

## Tasks

{tasks}

## Deliverables

{deliv}

## Files in this folder

| File | Content |
|---|---|
| `{p['nn']}_main.ipynb` | Main notebook (reproducible, fixed seeds, units stated in the first cell) |
| `report.md` or `report.pdf` | Written report with the requested analysis sections |
| `memo.md` | The memo deliverable (D6) |
| `figures/` | All figures used in the report (PNG or PDF, labelled axes with units) |
| `src/` | (optional) reusable Python modules extracted from the notebook |

## Summary of approach (write this last, 5–10 lines)

_What did you build, how did you validate it, and what are the two or three key numbers?_

## Key results

| Quantity | Value (with uncertainty) | Analytic or reference check |
|---|---|---|
|  |  |  |

## What surprised me / what I would do next

## Sources and AI-tool usage (required)

_List every paper, book, package, dataset and AI tool you used and what you used it for._
"""


def solutions_index_md():
    return """# Solutions

One sub-folder per problem, already created for you, each with a README template that lists the tasks and deliverables
of that problem. Work inside the folder of the problem you are solving.

```
solutions/NN_problem_name/
├── README.md              # template: status checklist, key results, sources and AI-tool usage
├── NN_main.ipynb          # main notebook (you create it)
├── report.md | report.pdf # written report (you create it)
├── memo.md                # memo deliverable (D6)
├── figures/               # all figures used in the report
└── src/                   # optional: modules you reuse across notebooks
```

## Rules of the house

1. **Fixed seeds, stated units.** The first cell of every notebook states the unit system (Hz or rad/s, normalised or not) and sets the random seed.
2. **Validate before you trust.** Every notebook has a section "Validation" that reproduces an analytic result or a self-check target.
3. **No cherry-picking.** Show error bars, false-alarm rates and failure cases, not only the best run.
4. **Clear outputs.** Before committing, run *Restart kernel and run all* so the notebook reproduces its own figures.
   Keep notebooks under about 5 MB (clear huge outputs).
5. **No big data in git.** Raw datasets go in `data/raw/` (git-ignored); describe how to download them.
6. **Cite everything,** including AI tools and code snippets, in the README of the problem. You must be able to explain
   every line you submit.

## Helper commands

```bash
python tools/check_submission.py 07     # does solutions/07_* contain notebook, report, memo, figures?
python tools/update_progress.py         # refresh PROGRESS.md from what is in solutions/
```
"""


# ----------------------------------------------------------------------------------------
# README.md
# ----------------------------------------------------------------------------------------
def problems_table():
    out = ["| # | Problem | Level | Effort | Prerequisites | Statement |", "|---|---|---|---|---|---|"]
    last = None
    for p in PROBLEMS:
        if p["part"] != last:
            out.append(f"| | **Part {p['part']}: {PARTS[p['part']]}** | | | | |")
            last = p["part"]
        pre = ", ".join(f"{q:02d}" for q in p["prereqs"]) if p["id"] != CAPSTONE_ID else "any 10 earlier problems"
        pre = pre or "none"
        out.append(f"| {p['nn']} | {p['title']} | {p['level']} | {p['effort']} | {pre} | "
                   f"[PDF]({pdf_link(p)}) · [LaTeX]({tex_link(p)}) |")
    return "\n".join(out)


def part_sections():
    out = []
    for k, name in PARTS.items():
        ps = [p for p in PROBLEMS if p["part"] == k]
        out.append(f"### Part {k}: {name} ({ps[0]['nn']}–{ps[-1]['nn']})\n")
        out.append(f"**{PART_BLURB[k][0]}** {PART_BLURB[k][1]}\n")
        out.append("| # | You will theoretically master | You will practically learn to |\n|---|---|---|")
        for p in ps:
            out.append(f"| {p['nn']} | {p['theory']} | {p['skills']} |")
        out.append("")
    return "\n".join(out)


def track_lines():
    tracks = [
        ("1. Signals and systems core", closure(PROBLEMS, [6, 7]), "want the mathematical foundation first, before any hardware or ML"),
        ("2. Electronics track", closure(PROBLEMS, [9, 10, 11]), "work on sensors, analog front ends, ADCs and radio links"),
        ("3. DSP track", closure(PROBLEMS, [15, 16, 17, 19, 20]), "become strong in filters, spectra, detection and estimation"),
        ("4. Radio and navigation track", closure(PROBLEMS, [11, 16, 20]), "work on ground stations, telemetry, SDR and sensor fusion"),
        ("5. Data and ML track", closure(PROBLEMS, [24]), "go from signals to machine learning (anomaly detection, classification)"),
    ]
    hours = lambda ids: round(sum(BYID[i]["hours"] for i in ids))
    fmt = lambda ids: ", ".join(f"{i:02d}" for i in ids)
    rows = ["| Track | Problems | Approx. hours | Best if you want to... |", "|---|---|---|---|"]
    for name, ids, why in tracks:
        rows.append(f"| **{name}** | {fmt(ids)} | {hours(ids)} | {why} |")
    rows.append(f"| **6. Whole ladder** | 01–{N:02d} | {round(TOTAL_H)} | become a master of the domain (capstone included) |")
    return "\n".join(rows) + """

Every track is closed under prerequisites (checked by `tools/problem_meta.py`), and each can be finished with the capstone (25) on
the topic you chose. Problems 09 (sensor conditioning), 11 (telemetry links) and 16 (multirate and SDR) are the most
hardware-flavoured and can be taken at any time after their prerequisites."""


def schedule_table(hours_per_week=10):
    out = ["| Problem | Hours | Finish by week |", "|---|---|---|"]
    acc = 0.0
    for p in PROBLEMS:
        acc += p["hours"]
        out.append(f"| {p['nn']} {p['title']} | {p['effort']} | {int(-(-acc // hours_per_week))} |")
    return "\n".join(out)


README_TEMPLATE = r"""# Signal Processing Ladder: 25 Hands-On Problem Statements from Sensors to Machine Learning

**Aeronautics and Space Technology Club, IIT (ISM) Dhanbad**

A progressive, hands-on problem set in **signal processing for aerospace**: from the first noisy sensor reading to filters,
spectra, detection theory, Kalman filtering and machine learning on real astronomical and flight-style data. It contains
**25 professionally typeset problem statements** (PDF + LaTeX), a Python helper package with **seeded synthetic datasets of known
ground truth**, a repository structure for pushing your solutions, and tools to track progress. It was built for learning *by
solving*: every problem asks you to derive a result by hand, implement the method yourself, validate it against a known answer,
and carry the result to an engineering decision for a satellite, a rocket, a ground station or a detector.

The problem statements follow a hackathon-style format (Background, Theoretical Framework, Data and Simulation Specification,
Tasks, Aerospace Application Link, Deliverables, Learning Resources, Evaluation), so what you learn here transfers directly to
competition problem solving and to real project work.

---

## Table of contents

1. [Overview](#1-overview)
2. [The ladder at a glance](#2-the-ladder-at-a-glance)
3. [Roadmap](#3-roadmap)
4. [What you will learn: theory and hands-on practice](#4-what-you-will-learn-theory-and-hands-on-practice)
5. [Repository layout](#5-repository-layout)
6. [Getting started](#6-getting-started)
7. [How to work on a problem](#7-how-to-work-on-a-problem)
8. [Data: synthetic and real](#8-data-synthetic-and-real)
9. [Study paths and schedule](#9-study-paths-and-schedule)
10. [Submitting solutions with git](#10-submitting-solutions-with-git)
11. [Self-assessment rubric](#11-self-assessment-rubric)
12. [Rules of the house](#12-rules-of-the-house)
13. [Rebuilding the PDFs](#13-rebuilding-the-pdfs)
14. [Reading list](#14-reading-list)
15. [FAQ and troubleshooting](#15-faq-and-troubleshooting)

---

## 1. Overview

The goal is to make you fundamentally strong in signal processing through problem solving rather than passive reading. Each
problem is designed as a small research project:

| Phase | What you do |
|---|---|
| **Think** | Read the theory, derive the analytic results by hand, write down the model, the units and the sampling rates. |
| **Build** | Implement the method yourself; validate against the analytic results and the self-check targets. |
| **Experiment** | Run sweeps, stress tests and the real data; produce first plots and numbers with error bars. |
| **Refine** | Fix weaknesses, write an honest analysis and a short memo, tidy the folder. |

Five principles run through the whole ladder (details in [`docs/CURRICULUM.md`](docs/CURRICULUM.md)):

1. **Derive by hand, then verify by code.** Each problem has analytic results and self-check numbers that your code must reproduce.
2. **Real problems, real data, known truth.** Every problem has a synthetic generator with ground truth (so you can measure
   bias, error and false alarms) *and* pointers to real datasets (so you see what the textbook model leaves out).
3. **Each problem hands numbers to the next.** The noise densities of problem 01 become the Kalman filter's process noise in 20;
   the windows of 12 become the spectral estimators of 13; the matched filter of 19 is the benchmark for the networks of 23.
4. **Aerospace first.** Every problem ends with an Aerospace Application Link: gyro drift budgets, reaction-wheel aliasing,
   apogee detection, GPS outages, CubeSat link budgets, burst triggers.
5. **Honesty over hype.** Error bars, false-alarm rates and injection–recovery curves are required, and machine learning is
   always compared with a classical optimum.

Total estimated effort: about **@@TOTAL@@ hours** (25 problems; the capstone alone is 35–60 hours).

## 2. The ladder at a glance

@@TABLE@@

Level scale: 1 Foundations · 2 Core · 3 Advanced · 4 Expert · 5 Capstone. The full list of tasks of each problem is in
[`docs/CURRICULUM.md`](docs/CURRICULUM.md); a printable overview is in
[`docs/Curriculum_Roadmap.pdf`](docs/Curriculum_Roadmap.pdf).

## 3. Roadmap

![Prerequisite graph of the 25 problems](docs/images/roadmap.png)

Arrows point from a prerequisite to the problem that builds on it. Blue = Part A (foundations), green = Part B (mathematics),
orange = Part C (electronics), purple = Part D (DSP), pink = Part E (machine learning and capstone).

## 4. What you will learn: theory and hands-on practice

@@PARTS@@

### Numbers handed from one problem to the next

| From | Used in | What is handed over |
|---|---|---|
@@HAND@@

## 5. Repository layout

```
signal-processing-ladder/
├── README.md                  # this file
├── PROGRESS.md                # progress tracker (auto-updated)
├── requirements.txt           # Python packages
├── environment.yml            # conda environment
├── problems/                  # the 25 problem statements
│   └── NN_name/
│       ├── NN_name.pdf        # the problem statement (read this)
│       └── NN_name.tex        # LaTeX source
├── solutions/                 # YOUR WORK GOES HERE: one folder per problem
│   ├── README.md              # how to organise a solution
│   └── NN_name/README.md      # template with tasks, deliverables, status checklist
├── common/                    # shared helpers: constants, units, stats, plotting and synthetic datasets
│   └── sp_common/
├── data/                      # raw data goes in data/raw/ (git-ignored); see data/README.md
├── tests/                     # tests for the helpers and the generators
├── docs/
│   ├── CURRICULUM.md          # theory and hands-on skills per problem
│   ├── Curriculum_Roadmap.pdf # printable roadmap
│   ├── DATASETS.md            # synthetic generators and real data per problem
│   ├── READING_LIST.md        # books and papers by topic
│   ├── SUBMISSION_GUIDE.md    # git workflow and review process
│   └── images/roadmap.png
├── latex/spl.sty              # shared LaTeX style of the problem statements
├── tools/                     # build_pdfs.sh, generate_docs.py, check_submission.py, update_progress.py
└── .github/                   # pull-request and issue templates
```

## 6. Getting started

### 6.1 Requirements

* Python 3.10 or newer; a laptop CPU is enough (no GPU, no lab access, no paid software).
* Core packages: NumPy, SciPy, Matplotlib, Jupyter, pandas. Per problem you may also need scikit-learn, PyWavelets, Astropy,
  Lightkurve, GWpy or PyTorch (each problem statement says which; install them when you reach that problem).
* To rebuild the PDFs: a LaTeX distribution with `pdflatex` (TeX Live or MiKTeX) and the packages `tcolorbox`, `siunitx`,
  `enumitem`, `titlesec`, `fancyhdr`, `microtype`.
* Optional hardware (never required): a smartphone with the free Phyphox app, an RTL-SDR dongle, a microcontroller board.

### 6.2 Environment

```bash
git clone <url-of-this-repository>
cd signal-processing-ladder

# Option A: pip
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Option B: conda
conda env create -f environment.yml && conda activate spladder

# install the shared helpers and check that they work
pip install -e common
pytest -q
```

For the deep-learning problems (23, 24) a CPU build of PyTorch is enough:
`pip install torch --index-url https://download.pytorch.org/whl/cpu`.

### 6.3 Your first hour

1. Read this README and [`docs/CURRICULUM.md`](docs/CURRICULUM.md).
2. Open `problems/01_signals_sensors_and_noise/01_signals_sensors_and_noise.pdf` and read it completely.
3. Open `solutions/01_signals_sensors_and_noise/README.md`, tick off nothing yet, and create `01_main.ipynb`.
4. In the first cell write the units, set the seed and generate the first dataset:

```python
from sp_common.rng import get_rng
from sp_common import synth
rng = get_rng(2026)
d = synth.sensor_signal(fs=1000, duration=1.0, f0=5, amp=1.0, noise_rms=0.2, seed=1)   # dict with t, clean, noisy
```

5. Start with *Stage 1 – Think*: derive the analytic results by hand on paper before writing code.

## 7. How to work on a problem

Every statement has the same sections. How to use them:

| Section | How to use it |
|---|---|
| **Background and Motivation** | Why the topic matters for aerospace; read first. |
| **Theoretical Framework** | The equations you need; re-derive the key results yourself. |
| **Data and Simulation Specification** | A parameter table so that results are comparable and reproducible, with the generator to call and the real data to download. Use these numbers. |
| **Your Task** | The numbered work packages. Do them in order; each builds on the previous. |
| **Self-check targets** (green box) | Analytic numbers your code must reproduce. If it does not, debug before moving on. |
| **Aerospace Application Link** | Carry the result to a design decision. This is the part that makes you an engineer. |
| **Deliverables** | D1 to D6 plus Bonus: exactly what to put in `solutions/NN_.../`. |
| **Learning Resources** | Books and papers, datasets and tools. |
| **Evaluation** | Rubric to score yourself out of 100 (five criteria of 20 marks). |

A recommended weekly rhythm: day 1 theory and by-hand derivations, days 2–3 build and validate, day 4 sweeps, real data and
plots, day 5 write the analysis and memo, then ask for review.

## 8. Data: synthetic and real

* **Synthetic first.** `sp_common.synth` provides seeded generators that return the signal *and* the truth (a burst's true rate
  function, the injected SNR of a chirp, the fault frequency of a bearing). They work offline and let you measure bias, error and
  false-alarm rates. They are models, simplified on purpose; say so in your report.
* **Real second.** Every problem lists real datasets (AstroSat, Fermi, TESS/Kepler, LIGO open data, SatNOGS, EuRoC, CWRU and
  your own smartphone recordings). Repeat the key result on one of them.
* **Never commit big data.** Put raw files in `data/raw/` (git-ignored), and record the source, date and checksum in your report.
* **Check the links.** The dataset links were written from memory of well-known public archives; if one has moved, search for the
  dataset name. See [`docs/DATASETS.md`](docs/DATASETS.md) for the full per-problem table.

## 9. Study paths and schedule

@@TRACKS@@

A schedule at about 10 hours per week (adjust freely):

@@SCHEDULE@@

## 10. Submitting solutions with git

Each problem lives in its own folder, so work from different problems never conflicts.

```bash
# once per problem
git checkout -b solution/07-random-signals
# ... work in solutions/07_random_signals_and_noise_spectra/ ...
git add solutions/07_random_signals_and_noise_spectra
git commit -m "07: PSD scaling verified, Poisson tail table, Fano factors"
git push -u origin solution/07-random-signals
# open a Pull Request into main; your mentor reviews it and writes the score into PROGRESS.md
```

Simpler alternative: commit directly to `main` and push; just keep one problem per commit. Commit often with a message that
says *what was validated*. See [`docs/SUBMISSION_GUIDE.md`](docs/SUBMISSION_GUIDE.md) for details, including what a good report
looks like. Before opening a pull request run:

```bash
python tools/check_submission.py 07
python tools/update_progress.py
```

## 11. Self-assessment rubric

Every problem uses the same rubric (five equally weighted criteria, 20 marks each): conceptual depth, implementation quality,
aerospace-application integration, analysis and critical thinking, communication. Score yourself honestly, then compare with your
mentor's score; the gap between the two is the most useful learning signal.

## 12. Rules of the house

* **Your own work.** Use any reference, library or AI tool, but cite it in the problem README, and be able to explain every line.
* **Validate before you trust.** Reproduce an analytic result or a self-check number in every notebook.
* **Fixed seeds, stated units.** First cell of every notebook. State Hz versus rad/s every time.
* **Report uncertainties.** Error bars, false-alarm rates, convergence studies.
* **Prefer a modest correct result over an impressive wrong one.**

## 13. Rebuilding the PDFs

The PDFs are committed, so you do not need LaTeX to read them. To rebuild all of them (for example after editing a `.tex`):

```bash
bash tools/build_pdfs.sh           # all problems and the roadmap
bash tools/build_pdfs.sh 07        # only problem 07
python tools/generate_docs.py      # regenerate README tables, roadmap figure, curriculum, tracker
```

The shared style is `latex/spl.sty`; each `.tex` file starts with `%% META` lines (id, title, level, effort, prerequisites,
theory, skills) that `tools/generate_docs.py` uses to keep every table consistent.

## 14. Reading list

A curated reading list by topic is in [`docs/READING_LIST.md`](docs/READING_LIST.md). Books that pay off throughout the ladder:
Oppenheim and Willsky (*Signals and Systems*), Oppenheim and Schafer (*Discrete-Time Signal Processing*), Lyons (*Understanding
Digital Signal Processing*), Smith (*The Scientist and Engineer's Guide to DSP*, free online), Horowitz and Hill (*The Art of
Electronics*), Kay (*Fundamentals of Statistical Signal Processing*), and Labbe (*Kalman and Bayesian Filters in Python*, free online).

## 15. FAQ and troubleshooting

**The problems look big. Where do I start?** Problem 01. It is the smallest, and the noise vocabulary of 01 is used all the way
to the capstone.

**I cannot reproduce a self-check number.** First check units (Hz versus rad/s, factors of 2π, one-sided versus two-sided
spectra, a missing 2), then the sampling rate and the frequency axis, then the conventions stated in the theory section. If it
still fails, write down what you expected and what you got and ask your mentor.

**Do I have to do all 25?** No. Use a study track (section 9). The signals-and-systems core (01–07) is the base for everything.

**I have no data and no hardware.** Every problem works with the synthetic generators; real data and hardware tasks are marked
and are never required to complete the 100 marks, though they are strongly recommended.

**A formula in a problem looks wrong.** Tell your mentor or open an issue ("Error in statement"). Bonus (c) of the capstone
rewards a genuine contribution.

**Which numbers are real and which are assumptions?** Parameters in the specification tables are representative values chosen so
that everyone studies the same physics. Where a value is an assumption (for example the toy interferometer noise curve or the
model-rocket parameters) the statement says so; check it against a source before using it in a real design.

---

*Built for the juniors of the Aeronautics and Space Technology Club, IIT (ISM) Dhanbad.*
"""


def readme_md():
    s = README_TEMPLATE
    s = s.replace("@@TOTAL@@", f"{round(TOTAL_H, -1):.0f}")
    s = s.replace("@@TABLE@@", problems_table())
    s = s.replace("@@PARTS@@", part_sections())
    s = s.replace("@@HAND@@", "\n".join(f"| {a} | {b} | {c} |" for a, b, c in HANDOFFS))
    s = s.replace("@@TRACKS@@", track_lines())
    s = s.replace("@@SCHEDULE@@", schedule_table())
    return s


def main():
    make_roadmap_png()
    (ROOT / "docs" / "CURRICULUM.md").write_text(curriculum_md(), encoding="utf-8")
    (ROOT / "docs" / "DATASETS.md").write_text(datasets_md(), encoding="utf-8")
    (ROOT / "docs" / "Curriculum_Roadmap.tex").write_text(roadmap_tex(), encoding="utf-8")
    if not (ROOT / "PROGRESS.md").exists():  # never overwrite scores and comments
        (ROOT / "PROGRESS.md").write_text(progress_md(), encoding="utf-8")
    sol = ROOT / "solutions"
    sol.mkdir(exist_ok=True)
    (sol / "README.md").write_text(solutions_index_md(), encoding="utf-8")
    for p in PROBLEMS:
        d = sol / p["folder"]
        d.mkdir(exist_ok=True)
        r = d / "README.md"
        if not r.exists():
            r.write_text(solution_readme(p), encoding="utf-8")
    (ROOT / "README.md").write_text(readme_md(), encoding="utf-8")
    print("generated README.md, docs/CURRICULUM.md, docs/DATASETS.md, docs/Curriculum_Roadmap.tex, docs/images/roadmap.png, PROGRESS.md, solutions/*")


if __name__ == "__main__":
    main()
