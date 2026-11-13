"""The four figures (PNG, 200 dpi). One idea per figure; each title states the finding; every figure is
labelled 'Descriptive, not preregistered' in its footnote.
Colours: a colour-blind-safe categorical order (blue, orange) on a near-white surface, checked with a
palette validator (deuteranopia / protanopia / tritanopia separation); text and reference lines stay in
neutral greys, and identity is never carried by colour alone (legends and direct labels)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#dcdbd5", "#fcfcfb"
Z90 = 1.645
NAMES = {"PGDP": "GDP deflator\ninflation", "RGDP": "real GDP\ngrowth", "UNEMP": "unemployment\nrate",
         "CPI": "CPI\ninflation", "TBILL": "3-month\nT-bill rate", "pooled": "pooled\n(mean of five)"}
NOTE = "Descriptive, not preregistered."

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "legend.frameon": False})


def _footnote(fig, text):
    fig.text(0.01, 0.01, f"{NOTE} {text}", fontsize=7.5, color=MUTED, ha="left", va="bottom", wrap=True)


def _save(fig, path, bottom=0.16):
    fig.tight_layout(rect=(0, bottom, 1, 1))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def _interval(ax, x, est, lo, hi, colour, label=None, horizontal=False, size=40):
    if horizontal:
        ax.hlines(x, lo, hi, color=colour, lw=2)
        ax.scatter(est, x, color=colour, s=size, zorder=3, edgecolor=SURFACE, lw=1, label=label)
    else:
        ax.vlines(x, lo, hi, color=colour, lw=2)
        ax.scatter(x, est, color=colour, s=size, zorder=3, edgecolor=SURFACE, lw=1, label=label)


UNITS = "s.d. of error per s.d. of revision"


def fig1_small_large(slopes, path):
    """Slope of error on revision after small and after large surprises, by variable and pooled."""
    labels = list(dict.fromkeys(slopes["label"]))
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    x = np.arange(len(labels)) + np.array([0.4 if l == "pooled" else 0 for l in labels])
    for cls, colour, shift, text in (("small", BLUE, -0.13, "after small surprises (bottom two thirds of |surprise|)"),
                                     ("large", ORANGE, 0.13, "after large surprises (top third)")):
        t = slopes[slopes["class"] == cls].set_index("label").loc[labels]
        _interval(ax, x + shift, t["estimate"], t["lo90"], t["hi90"], colour, text)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvline(x[-1] - 0.7, color=GRID, lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels([NAMES[l] for l in labels])
    ax.grid(axis="x", visible=False)
    ax.set_ylabel(f"slope of error on revision\n({UNITS})")
    ax.set_title("Under-reaction is no stronger after large surprises, for any variable", pad=30)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    _footnote(fig, "US SPF mean consensus, 1 004 variable-quarter rows, targets 1969-2026. Positive slope = "
                   "under-reaction. Bars: 90% intervals (Driscoll-Kraay, 4 lags). By variable: preregistered\n"
                   "secondary regression S1 (one extra slope per variable); pooled: mean of the five base slopes "
                   "and that mean plus the common extra slope c of the main regression.")
    _save(fig, path)


def fig2_without_episodes(table, c_full, path):
    """Extra slope c with each episode window removed."""
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    y = np.arange(len(table))[::-1]
    ax.axvspan(-1, 0, color=GRID, alpha=0.0)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axvline(c_full, color=INK, lw=1, ls="--")
    ax.axvline(0.40, color=ORANGE, lw=1.2, ls=":")
    _interval(ax, y, table["estimate"], table["lo90"], table["hi90"], BLUE, horizontal=True)
    ax.text(c_full, len(table) - 0.35, f"all rows: c = {c_full:.2f}", fontsize=8, color=INK, ha="center")
    ax.text(0.40, len(table) - 0.35, "predicted c = +0.40", fontsize=8, color=MUTED, ha="center")
    ax.set_yticks(y)
    ax.set_yticklabels([f"without {r.label} ({r.window}, {r.rows_removed} rows)" for r in table.itertuples()],
                       fontsize=8.5)
    ax.set_ylim(-0.7, len(table) + 0.1)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"extra slope after large surprises, c ({UNITS})")
    ax.set_title("No single episode hides a positive size effect: c stays near zero")
    _footnote(fig, "Windows: each NBER recession from peak to trough + 4 quarters (E7 adds the 2021-2023 "
                   "inflation surge). The estimates are the preregistered fields c_sans_E1..E7 (a guard of\n"
                   "the verdict rule); the intervals are added here. Bars: 90% intervals (Driscoll-Kraay, 4 lags).")
    _save(fig, path)


def fig3_sorts(data_sorts, sims, path):
    """Left: c in the data under three definitions of 'large'. Right: c in simulated panels with no true
    size effect, under the surprise sort and the revision sort, for two noise models."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.9), gridspec_kw={"width_ratios": [1, 1]})
    colours = [BLUE, ORANGE, ORANGE]
    labels = ["top third of\n|surprise|\n(preregistered)", "|revision|\n> 1 s.d.\n(card, S7)", "top third of\n|revision|"]
    for i, (r, colour) in enumerate(zip(data_sorts.itertuples(), colours)):
        _interval(a1, i, r.estimate, r.lo90, r.hi90, colour)
        a1.annotate(f"{r.estimate:+.2f}", (i, r.estimate), xytext=(7, -3), textcoords="offset points", fontsize=8)
    a1.set_xticks(range(len(labels)))
    a1.set_xticklabels(labels, fontsize=8)
    a1.set_xlim(-0.5, 2.6)
    a1.axhline(0, color=MUTED, lw=0.8)
    a1.grid(axis="x", visible=False)
    a1.set_ylabel(f"extra slope after large news, c\n({UNITS})")
    a1.set_title("US SPF data: c by sort variable\n(90% intervals)", fontsize=10)
    groups = [("scaled", "noise grows\nwith turbulence"), ("fixed", "noise of\nfixed size")]
    for g, (noise, glabel) in enumerate(groups):
        for k, (sort, colour, shift, lab) in enumerate((("surprise_sort", BLUE, -0.15, "sort on lagged |surprise| (K20)"),
                                                        ("revision_sort", ORANGE, 0.15, "sort on |revision| > 1 s.d."))):
            s = sims[noise][sort]
            _interval(a2, g + shift, s["mean"], s["p05"], s["p95"], colour, lab if g == 0 else None)
            a2.annotate(f"{s['mean']:+.2f}", (g + shift, s["mean"]), xytext=(6, -3), textcoords="offset points",
                        fontsize=8)
    a2.axhline(0, color=INK, lw=1, ls="--")
    a2.text(1.45, 0.004, "true c = 0", fontsize=8, color=INK, ha="right", va="bottom")
    a2.set_xticks([0, 1])
    a2.set_xticklabels([g[1] for g in groups], fontsize=8)
    a2.set_xlim(-0.5, 1.5)
    a2.grid(axis="x", visible=False)
    a2.set_title("Simulated panels with no size effect:\nmean c and 5-95% range", fontsize=10)
    a2.legend(loc="upper left", fontsize=8)
    lo = min(a1.get_ylim()[0], a2.get_ylim()[0])
    hi = max(a1.get_ylim()[1], a2.get_ylim()[1])
    a1.set_ylim(lo, hi)
    a2.set_ylim(lo, hi)
    fig.suptitle("Sorting on the revision itself biases c upwards; the preregistered sort on the lagged surprise "
                 "does not", fontsize=11, fontweight="bold", x=0.01, ha="left")
    _footnote(fig, "Left: 1 004 rows; the surprise sort is the preregistered test, the card's sort is the "
                   "preregistered secondary S7, the top-third revision sort is added here. Right: 300 panels of\n"
                   "5 x 200 rows each (src/snu/simulation.py): constant true slope, consensus noise in both "
                   "surveys, fat-tailed news; the same estimator as for the data.")
    _save(fig, path, bottom=0.15)


def fig4_by_decade(table, pooled_full, path):
    """Pooled base slope (no size split) by decade of target."""
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    x = np.arange(len(table))
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axhline(pooled_full, color=INK, lw=1, ls="--")
    ax.text(len(table) - 0.5, pooled_full, f"all decades: {pooled_full:.2f}", fontsize=8, color=INK,
            ha="right", va="bottom")
    _interval(ax, x, table["estimate"], table["lo90"], table["hi90"], BLUE)
    for i, r in enumerate(table.itertuples()):
        ax.annotate(f"{r.estimate:.2f}", (i, r.estimate), xytext=(7, -3), textcoords="offset points", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r.label}\n{r.n} rows" for r in table.itertuples()], fontsize=8.5)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("decade of the target quarter")
    ax.set_ylabel(f"slope of error on revision\n({UNITS})")
    ax.set_title("Under-reaction is present in most decades but varies widely from one to the next")
    _footnote(fig, "US SPF mean consensus, five variables (CPI and T-bill from 1982). One constant per variable, "
                   "one common slope, no split by surprise size; standardisation constants of the full\n"
                   "sample. Bars: 90% intervals (Driscoll-Kraay, 4 lags).")
    _save(fig, path)
