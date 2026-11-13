"""The six figures (PNG, 200 dpi): four on the US survey, two comparing the US and the euro area. One idea
per figure; each title states the finding; every figure is labelled 'Descriptive, not preregistered' in
its footnote.
Colours: a colour-blind-safe categorical order (blue, orange) on a near-white surface, checked with a
palette validator (deuteranopia / protanopia / tritanopia separation); text and reference lines stay in
neutral greys, and identity is never carried by colour alone (legends and direct labels)."""
import textwrap

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
    width = int(fig.get_figwidth() * 18)  # characters per line at 7.5 pt
    fig.text(0.01, 0.01, textwrap.fill(f"{NOTE} {text}", width), fontsize=7.5, color=MUTED, ha="left", va="bottom")


def _num(x):
    """'+0.12', '-0.03', and '0.00' rather than '-0.00'."""
    return "0.00" if abs(x) < 0.005 else f"{x:+.2f}"


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
    ax.set_title("Under-reaction is no stronger after large surprises; no variable shows a significant rise", pad=30)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    _footnote(fig, "US SPF mean consensus, 1 004 variable-quarter rows, targets 1969-2026. Positive slope = under-reaction. Bars: 90% intervals (Driscoll-Kraay, 4 lags). By variable: preregistered secondary regression S1 (one extra slope per variable); pooled: mean of the five base slopes and that mean plus the common extra slope c of the main regression.")
    _save(fig, path)


def fig2_without_episodes(table, c_full, path):
    """Extra slope c with each episode window removed."""
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    y = np.arange(len(table))[::-1]
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axvline(c_full, color=INK, lw=1, ls="--")
    ax.axvline(0.40, color=ORANGE, lw=1.2, ls=":")
    _interval(ax, y, table["estimate"], table["lo90"], table["hi90"], BLUE, horizontal=True)
    ax.text(c_full - 0.005, len(table) - 0.35, f"all rows: c = {_num(c_full)}", fontsize=8, color=INK, ha="right")
    ax.text(0.395, len(table) - 0.35, "predicted c = +0.40", fontsize=8, color=MUTED, ha="right")
    ax.set_yticks(y)
    ax.set_yticklabels([f"without {r.label} ({r.window}, {r.rows_removed} rows)" for r in table.itertuples()],
                       fontsize=8.5)
    ax.set_ylim(-0.7, len(table) + 0.1)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"extra slope after large surprises, c ({UNITS})")
    ax.set_title(f"Without any one episode, c stays between {_num(table['estimate'].min())} and "
                 f"{_num(table['estimate'].max())}")
    _footnote(fig, "Windows: each NBER recession from peak to trough + 4 quarters (E7 adds the 2021-2023 inflation surge). The estimates are the preregistered fields c_sans_E1..E7 (a guard of the verdict rule); the intervals are added here. Bars: 90% intervals (Driscoll-Kraay, 4 lags).")
    _save(fig, path)


def fig3_sorts(data_sorts, sims, path):
    """Left: c in the data under three definitions of 'large'. Right: c in simulated panels with no true
    size effect, under the surprise sort and the revision sort, for two noise models."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.9), gridspec_kw={"width_ratios": [1, 1]})
    colours = [BLUE, ORANGE, ORANGE]
    labels = ["top third of\n|surprise|\n(preregistered)", "|revision|\n> 1 s.d.\n(card, S7)", "top third of\n|revision|"]
    for i, (r, colour) in enumerate(zip(data_sorts.itertuples(), colours)):
        _interval(a1, i, r.estimate, r.lo90, r.hi90, colour)
        a1.annotate(_num(r.estimate), (i, r.estimate), xytext=(7, -3), textcoords="offset points", fontsize=8)
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
            a2.annotate(_num(s["mean"]), (g + shift, s["mean"]), xytext=(-7 if shift < 0 else 7, 3),
                        textcoords="offset points", fontsize=8, ha="right" if shift < 0 else "left")
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
    fig.suptitle("Sorting on the size of the revision pushes c up, as consensus noise predicts; the preregistered "
                 "sort on the lagged surprise does not", fontsize=11, fontweight="bold", x=0.01, ha="left")
    _footnote(fig, "Left: 1 004 rows; the surprise sort is the preregistered test, the card's sort is the preregistered secondary S7, the top-third revision sort is added here. Right: 300 panels of 5 x 200 rows each (src/snu/simulation.py): constant true slope, consensus noise in both surveys, fat-tailed news; the same estimator as for the data.")
    _save(fig, path, bottom=0.15)


def fig4_by_decade(table, pooled_full, path):
    """Pooled base slope (no size split) by decade of target."""
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    x = np.arange(len(table))
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axhline(pooled_full, color=INK, lw=1, ls="--")
    ax.text(0.5, pooled_full + 0.005, f"all decades: {pooled_full:.2f}", fontsize=8, color=INK,
            ha="center", va="bottom")
    _interval(ax, x, table["estimate"], table["lo90"], table["hi90"], BLUE)
    for i, r in enumerate(table.itertuples()):
        ax.annotate(f"{r.estimate:.2f}", (i, r.estimate), xytext=(7, -3), textcoords="offset points", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r.label}\n{r.n} rows" for r in table.itertuples()], fontsize=8.5)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("decade of the target quarter")
    ax.set_ylabel(f"slope of error on revision\n({UNITS})")
    ax.set_title("Under-reaction is not stable over time: clearly positive only in 1990-2009")
    _footnote(fig, "US SPF mean consensus, five variables (CPI and T-bill from 1982). One constant per variable, one common slope, no split by surprise size; standardisation constants of the full sample. Bars: 90% intervals (Driscoll-Kraay, 4 lags).")
    _save(fig, path)


EA_NAMES = {"HICP": "HICP inflation", "RGDP": "real GDP growth", "UNEM": "unemployment rate"}
US_NAMES = {"PGDP": "GDP deflator inflation", "RGDP": "real GDP growth", "UNEMP": "unemployment rate",
            "CPI": "CPI inflation", "TBILL": "3-month T-bill rate"}


def fig5_forest_c(us_pooled, us_vars, ea_pooled, ea_vars, path):
    """Forest plot of the extra slope c after large news, with 90% intervals: pooled and by variable, for the
    US SPF (K20) and the ECB SPF (K20-ZE). Each table has columns label, estimate, lo90, hi90."""
    rows = ([("US SPF, all five variables (K20)", us_pooled, BLUE, True)]
            + [(f"   {US_NAMES[r.label]}", r, BLUE, False) for r in us_vars.itertuples()]
            + [("ECB SPF, all three variables (K20-ZE)", ea_pooled, ORANGE, True)]
            + [(f"   {EA_NAMES[r.label]}", r, ORANGE, False) for r in ea_vars.itertuples()])
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    y = np.arange(len(rows))[::-1].astype(float)
    y[len(us_vars) + 1:] -= 0.6          # a gap between the two surveys
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axvline(0.40, color=INK, lw=1.2, ls=":")
    ax.text(0.395, y[0] + 0.55, "predicted c = +0.40", fontsize=8, color=INK, ha="right", va="bottom")
    for yi, (label, r, colour, pooled) in zip(y, rows):
        est, lo, hi = (r["estimate"], r["lo90"], r["hi90"]) if isinstance(r, dict) else (r.estimate, r.lo90, r.hi90)
        _interval(ax, yi, est, lo, hi, colour, horizontal=True, size=70 if pooled else 36)
        ax.annotate(_num(est), (hi, yi), xytext=(5, -3), textcoords="offset points", fontsize=8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    for tick, (_, _, _, pooled) in zip(ax.get_yticklabels(), rows):
        tick.set_fontweight("bold" if pooled else "normal")
    ax.set_ylim(y[-1] - 0.7, y[0] + 1.1)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"extra slope after large news, c ({UNITS})")
    ax.set_title("In both surveys the extra slope after large news is near zero; +0.40 is excluded")
    _footnote(fig, "The figure is new; its estimates are preregistered: pooled c is each test's primary statistic, the "
                   "per-variable c its secondary analysis S1. Bars: 90% intervals, Driscoll-Kraay standard errors (US: 4 lags "
                   "by target quarter, critical value 1.645; euro area: 8 lags by survey round, critical value 1.708). "
                   "Large news: top third of the data surprise of each variable.")
    _save(fig, path, bottom=0.12)


def fig6_base_vs_c(table, c_pandemic, se_pandemic, path):
    """Base under-reaction slope (no size split) and extra slope c after large news, for each survey.
    `table` has one row per survey and quantity: survey, quantity ('base' or 'c'), estimate, lo90, hi90."""
    surveys = list(dict.fromkeys(table["survey"]))
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    ax.axhline(0, color=MUTED, lw=0.8)
    for q, colour, shift, label in (("base", BLUE, -0.14, "base under-reaction slope (no split by news size)"),
                                    ("c", ORANGE, 0.14, "extra slope after large news, c")):
        t = table[table["quantity"] == q].set_index("survey").loc[surveys]
        x = np.arange(len(surveys)) + shift
        _interval(ax, x, t["estimate"], t["lo90"], t["hi90"], colour, label, size=60)
        for xi, est in zip(x, t["estimate"]):
            ax.annotate(_num(est), (xi, est), xytext=(8, -3), textcoords="offset points", fontsize=8.5, color=INK)
    for i in range(len(surveys)):
        ax.hlines(0.40, i + 0.02, i + 0.30, color=INK, lw=1.2, ls=":")
    ax.text(len(surveys) - 1 + 0.31, 0.40, "predicted\nc = +0.40", fontsize=8, color=INK, va="center")
    ax.set_xticks(range(len(surveys)))
    ax.set_xticklabels(surveys)
    ax.set_xlim(-0.6, len(surveys) - 0.25)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel(f"slope of error on revision\n({UNITS})")
    ax.set_title("Under-reaction yes, size-dependence no: the same answer in two surveys", pad=30)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    _footnote(fig, "Base slope: one constant per series and one common slope (US: descriptive, not preregistered; "
                   "euro area: the preregistered positive control b_commun). c: each test's primary statistic. Bars: 90% "
                   "intervals (US: Driscoll-Kraay 4 lags, 1.645; euro area: 8 lags, 1.708). Euro area: pandemic rows of "
                   f"GDP and unemployment excluded, as preregistered; with them c = {_num(c_pandemic)} (se {se_pandemic:.2f}).")
    _save(fig, path)
