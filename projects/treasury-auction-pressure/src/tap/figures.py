"""The five figures (PNG, 200 dpi). One idea per figure; Okabe-Ito colour-blind-safe colours."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BEFORE, AFTER, REFERENCE, INK = "#0072B2", "#D55E00", "#8C8C8C", "#333333"

plt.rcParams.update({
    "figure.figsize": (7.5, 4.4), "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#999999",
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#E6E6E6", "grid.linewidth": 0.8,
    "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def _finish(fig, ax, path, note):
    ax.axhline(0, color=INK, linewidth=0.8)
    fig.text(0.01, -0.02, note, fontsize=8, color="#555555", ha="left", va="top", wrap=True)
    fig.savefig(path)
    plt.close(fig)


def _by_year(ax, table, cutoff=2022, label_suffix=""):
    """Points with interval whiskers, coloured by period (before / from `cutoff`)."""
    for name, colour, mask in (("2010-2021", BEFORE, table.group < cutoff),
                               ("2022-2026", AFTER, table.group >= cutoff)):
        t = table[mask]
        ax.errorbar(t.group, t["mean"], yerr=[t["mean"] - t.low, t.high - t["mean"]], fmt="o", ms=6,
                    color=colour, ecolor=colour, elinewidth=1.5, capsize=0, label=name + label_suffix)
    ax.set_xticks(list(table.group))
    ax.set_xticklabels([str(y) if y % 2 == 0 else "" for y in table.group])
    ax.set_xlabel("Year of the auction")


def event_path(path_table, out):
    """Figure 1: average spread path around reopenings, by period (descriptive)."""
    fig, ax = plt.subplots()
    for period, colour in (("2010-2021", BEFORE), ("2022-2026", AFTER)):
        t = path_table[path_table.period == period]
        ax.fill_between(t.k, t.low, t.high, color=colour, alpha=0.15, linewidth=0)
        ax.plot(t.k, t["mean"], color=colour, linewidth=2, marker="o", ms=4,
                label=f"{period} ({int(t.n.iloc[0])} reopenings)")
    ax.axvline(0, color=INK, linewidth=0.8, linestyle=":")
    ax.text(0.2, ax.get_ylim()[1] * 0.95, "auction day J", fontsize=8, color=INK, va="top")
    ax.set_xticks(range(-10, 11, 5))
    ax.set_xlabel("Trading days relative to the auction (DGS10 calendar)")
    ax.set_ylabel("CMT minus GSW par yield,\nchange since J-5 (bp)")
    ax.set_title("Before 2022 the spread spikes on auction day and reverses; after 2021 it does not")
    ax.legend(loc="upper left")
    _finish(fig, ax, out, "Descriptive, not preregistered. 10-, 20- and 30-year reopenings of F04's sample P with all "
            "21 days available; spread = Treasury constant-maturity yield minus Fed GSW par yield. "
            "Bands: 95% intervals, standard errors clustered by month.")


def v_by_year(table, out):
    """Figure 2: F04's V by year, method change marked."""
    fig, ax = plt.subplots()
    _by_year(ax, table)
    ax.axvline(2021.5, color=INK, linewidth=1, linestyle="--")
    ax.text(2021.6, ax.get_ylim()[1] * 0.97, "Treasury curve method\nchange, 6 Dec 2021", fontsize=8, va="top")
    ax.set_ylabel("V, mean per year (bp)")
    ax.set_title("Pressure measured against the Treasury curve vanishes after 2021")
    ax.legend(loc="lower left")
    n = int(table.n.sum())
    _finish(fig, ax, out, f"F04's V = 100[2E(J) - E(J-5) - E(J+5)], E = CMT - GSW par yield, sample P ({n} "
            "reopenings). Yearly means with 95% intervals (standard errors clustered by month). "
            "The year split is descriptive.")


def fy2021_pairs(df, d_mean, d_low, d_high, out):
    """Figure 3: V under the old (HS) and new (MC) Treasury methods, same auctions."""
    fig, ax = plt.subplots(figsize=(5.5, 4.6))
    for _, r in df.iterrows():
        ax.plot([0, 1], [r.v_hs, r.v_mc], color=REFERENCE, linewidth=0.8, alpha=0.8)
    ax.scatter([0] * len(df), df.v_hs, color=BEFORE, s=28, zorder=3)
    ax.scatter([1] * len(df), df.v_mc, color=AFTER, s=28, zorder=3)
    means = (df.v_hs.mean(), df.v_mc.mean())
    ax.plot([0, 1], means, color=INK, linewidth=2.5, marker="D", ms=7, zorder=4)
    for x, m in zip((0, 1), means):
        ax.text(x + (-0.08 if x == 0 else 0.08), m, f"mean {m:.2f} bp", ha="right" if x == 0 else "left",
                va="center", fontsize=9, fontweight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Old method (HS)", "New method (MC)"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel("V, per auction (bp)")
    ax.set_title(f"Same 23 auctions: the new method lowers V by {d_mean:.2f} bp")
    _finish(fig, ax, out, f"F04-bis, fiscal 2021 (Oct 2020 - Sep 2021). Mean difference {d_mean:.2f} bp, "
            f"95% interval [{d_low:.2f}, {d_high:.2f}] (t with 7 df, clustered by month).")


def k_by_year(table, means, out):
    """Figure 4: J05's concession K by year against the GSW curve."""
    fig, ax = plt.subplots()
    _by_year(ax, table)
    for (name, colour, lo, hi) in (("2010-2021", BEFORE, 2009.6, 2021.4), ("2022-2026", AFTER, 2021.6, 2026.4)):
        ax.hlines(means[name], lo, hi, color=colour, linewidth=1, linestyle="--",
                  label=f"{name} mean: {means[name]:.2f} bp")
    ax.set_ylabel("K, mean per year (bp)")
    ax.set_title("Measured on market prices against the GSW curve, the concession did not fall")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    _finish(fig, ax, out, "J05's K = 100{[auction high yield - g(J)] - [f(J-5) - g(J-5)]}, g = the security on the GSW "
            f"curve, f = its FedInvest yield; sample P ({int(table.n.sum())} reopenings). 95% intervals clustered by month.")


def k11_by_year(table, f04_table, out):
    """Figure 5: K11's V by year (flat), with F04's V by year as reference."""
    fig, ax = plt.subplots()
    ax.plot(f04_table.group, f04_table["mean"], color=REFERENCE, linewidth=1.5, marker="s", ms=4,
            label="Reference: V against the Treasury curve (F04)")
    _by_year(ax, table, label_suffix=": V against matched controls (K11)")
    ax.set_ylabel("V, mean per year (bp)")
    ax.set_title("Against matched off-the-run controls, V stays near zero before and after 2022")
    ax.legend(loc="lower left", fontsize=8)
    _finish(fig, ax, out, "K11: E = reopened security minus the mean of its 2nd-4th off-the-run controls, all from "
            f"FedInvest end-of-day prices; V = 2E(J) - E(J-5) - E(J+5); sample P ({int(table.n.sum())} reopenings). 95% intervals "
            "clustered by month. The controls move with the reopened bond, so the instrument cannot see the pressure.")
