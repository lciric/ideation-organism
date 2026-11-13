"""The five figures (PNG, 200 dpi). One idea per figure; titles state the finding.
Colours: a colour-blind-safe categorical order (blue, orange, aqua) on a near-white surface;
text and reference lines stay in neutral greys."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dcdbd5"

plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "legend.frameon": False})


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def fig1_ecb_scatter(sample, beta_z, beta_z_without, path):
    """J02 sample: standardised error against standardised revision, 2021-2023 targets marked,
    fitted lines with and without 2021-2023 (in the same full-sample standard units)."""
    r, e = sample["revision"].values, sample["error"].values
    z, y = (r - r.mean()) / r.std(ddof=1), (e - e.mean()) / e.std(ddof=1)
    surge = sample["t_target"].between(8084, 8095).values
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.scatter(z[~surge], y[~surge], s=28, color=BLUE, edgecolor="#fcfcfb", lw=1,
               label="target quarters 1999-2020 and 2024-2026")
    ax.scatter(z[surge], y[surge], s=36, color=ORANGE, edgecolor="#fcfcfb", lw=1, label="target quarters 2021-2023")
    grid = np.linspace(z.min(), z.max(), 50)
    b_all = np.polyfit(z, y, 1)
    b_out = np.polyfit(z[~surge], y[~surge], 1)
    ax.plot(grid, np.polyval(b_all, grid), color=INK, lw=2, label=f"fit, all targets (correlation {beta_z:.2f})")
    ax.plot(grid, np.polyval(b_out, grid), color=BLUE, lw=2, ls="--",
            label=f"fit, without 2021-2023 (correlation {beta_z_without:.2f})")
    for i in np.where(surge)[0]:
        if abs(y[i]) > 2 or abs(z[i]) > 2:
            ax.annotate(sample["target"].iloc[i], (z[i], y[i]), xytext=(4, 3), textcoords="offset points",
                        fontsize=7, color=MUTED)
    ax.set_xlabel("revision of the 2-quarter-ahead projection (standard deviations)")
    ax.set_ylabel("projection error, outturn minus projection (standard deviations)")
    ax.set_title("ECB staff errors follow revisions mainly because of the 2021-2023 surge")
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, path)


def fig2_leave_out(drop_one, drop_two, beta_z, path):
    """J02 correlation when each calendar year, or each pair of consecutive years, of targets is removed."""
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharey=True)
    for ax, values, label in ((axes[0], drop_one, "one year removed"),
                              (axes[1], drop_two, "years Y and Y+1 removed; Y shown")):
        years = np.array(sorted(values))
        v = np.array([values[y] for y in years])
        colours = [ORANGE if 2022 in (y, y + (label != "one year removed")) else BLUE for y in years]
        ax.vlines(years, 0, v, color=colours, lw=2)
        ax.scatter(years, v, color=colours, s=30, zorder=3)
        ax.axhline(beta_z, color=INK, lw=1, ls="--")
        ax.text(years[0] - 0.5, 0.56, f"dashed line: all targets ({beta_z:.2f}); orange: 2022 removed", fontsize=8,
                color=MUTED)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_ylabel("correlation of error\nwith revision")
        ax.set_xlabel(f"calendar year of targets removed ({label})")
        low = years[np.argmin(v)]
        ax.annotate(f"{v.min():.2f}", (low, v.min()), xytext=(6, -2), textcoords="offset points", fontsize=8,
                    color=INK)
    axes[0].set_ylim(-0.02, 0.65)
    axes[0].set_title("Removing 2022 (or 2021-2022) erases most of the ECB staff error-revision correlation")
    _save(fig, path)


def fig3_h03_blocks(blocks, rbar, lo, hi, path):
    """H03-v2: uncentred correlation between the real-time correction and the error, by two-year block."""
    b = blocks[blocks["valid"]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axhspan(lo, hi, color=BLUE, alpha=0.12, lw=0, label=f"90% interval of the mean [{lo:.2f}, {hi:.2f}]")
    ax.axhline(rbar, color=BLUE, lw=2, label=f"mean over blocks {rbar:.2f}")
    ax.axhline(0.22, color=ORANGE, lw=1.5, ls="--", label="smallest effect the card predicted (0.22)")
    ax.axhline(0, color=MUTED, lw=0.8)
    colours = [ORANGE if k in (8, 9) else INK for k in b["block"]]
    ax.scatter(b["block"], b["R"], color=colours, s=40, zorder=3)
    ax.set_xticks(b["block"])
    ax.set_xticklabels([f"{y[:4]}-{y[-2:]}" for y in b["years"]], fontsize=8)  # '2004-05'
    ax.set_xlabel("target years (two-year blocks; 2020-2023 in orange)")
    ax.set_ylabel("correlation of correction\nwith later error")
    ax.set_title("A real-time revision-based correction rule would not have predicted ECB staff errors")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8)
    _save(fig, path)


def fig4_k01_slopes(table, path, crit=1.714):
    """K01: individual 2SLS slope vs naive slopes vs consensus and ECB staff slopes, with 90% intervals."""
    names = list(dict.fromkeys(table["estimate"]))
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for k, (sample, colour, shift) in enumerate((("full sample", BLUE, -0.15), ("excluding 2021-2023", ORANGE, 0.15))):
        t = table[table["sample"] == sample].set_index("estimate").loc[names]
        ypos = np.arange(len(names)) + shift
        ax.hlines(ypos, t["b"] - crit * t["se"], t["b"] + crit * t["se"], color=colour, lw=2)
        ax.scatter(t["b"], ypos, color=colour, s=36, zorder=3, label="target years 2002-2025" if sample == "full sample"
                   else "excluding target years 2021-2023")
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axvline(-0.15, color=MUTED, lw=1, ls=":")
    ax.text(-0.17, -0.45, "predicted\nover-reaction\n(-0.15)", fontsize=7, color=MUTED, ha="right", va="top")
    ax.set_yticks(np.arange(len(names)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("slope of error on revision (points per point; 90% interval, Driscoll-Kraay)")
    ax.set_title("ECB SPF: the predicted individual over-reaction is excluded", pad=28)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    _save(fig, path)


def fig5_k20_by_variable(per_var, path):
    """K20: base slope (small surprises) and slope after large surprises, by variable, 90% intervals."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(per_var))
    for col, se, colour, shift, label in (("b_small", "se_small", BLUE, -0.12, "after small surprises (bottom two thirds)"),
                                          ("b_large", "se_large", ORANGE, 0.12, "after large surprises (top third)")):
        ax.vlines(x + shift, per_var[col] - 1.645 * per_var[se], per_var[col] + 1.645 * per_var[se], color=colour, lw=2)
        ax.scatter(x + shift, per_var[col], color=colour, s=36, zorder=3, label=label)
    ax.axhline(0, color=MUTED, lw=0.8)
    names = {"PGDP": "GDP deflator", "RGDP": "real GDP", "UNEMP": "unemployment", "CPI": "CPI inflation",
             "TBILL": "3-month T-bill"}
    ax.set_xticks(x)
    ax.set_xticklabels([names[v] for v in per_var["variable"]])
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("slope of error on revision\n(s.d. of error per s.d. of revision)")
    ax.set_title("US SPF consensus: under-reaction does not grow after large surprises", pad=28)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8)
    _save(fig, path)
