"""Descriptive analyses (NOT preregistered). They describe the data; none of them enters a verdict.

US (K20): the functions take the standardised main sample (`base`, as returned by k20.run): one row per
variable x target quarter with columns variable, t_target, z_r (standardised revision), z_e (standardised
error) and large (1 after a large surprise). Standard errors are Driscoll-Kraay with 4 lags (scores summed by
target quarter), as in the preregistered test; 90% intervals are estimate +/- 1.645 se.

Euro area (K20-ZE, functions ea_*): the same ideas on k20ze.run's sample, with its six series, 8 lags by
survey round and the critical value 1.708. Livingston (K20-LIV, functions liv_*): k20liv.run's sample, 2 lags
by half-year, 1.645. `comparison` puts the surveys side by side.
"""
import math

import numpy as np
import pandas as pd

from . import k20, stats
from .measures import EPISODE_LABELS, K20_EPISODES, top_third

Z90 = 1.645
DECADES = [("1969-1979", 7879, 7919), ("1980-1989", 7920, 7959), ("1990-1999", 7960, 7999),
           ("2000-2009", 8000, 8039), ("2010-2019", 8040, 8079), ("2020-2026", 8080, 8106)]


def variables_in(D, order=k20.VARS):
    """Variables present in D, in the order of the preregistration."""
    present = set(D["variable"])
    return [v for v in order if v in present] + sorted(present - set(order))


def _fit(D, X, ze="z_e", lags=4):
    beta, u, _ = stats.ols(X, D[ze].values)
    return beta, stats.driscoll_kraay_cov(X, u, D["t_target"].values, lags)


def _row(label, est, se, n, **extra):
    return {"label": label, "estimate": est, "se": se, "lo90": est - Z90 * se, "hi90": est + Z90 * se, "n": n,
            **extra}


# ------------------------------------------------------------------------- 1. base (Coibion-Gorodnichenko) slope
def cg_slopes(D, lags=4, order=k20.VARS):
    """Slope of the standardised error on the standardised revision, with no split by surprise size:
    one constant per variable, and either one slope per variable or one pooled slope.
    Returns a DataFrame with one row per variable and a last row 'pooled'."""
    D = D.dropna(subset=["z_r", "z_e"])
    vs = variables_in(D, order)
    dv = [(D["variable"] == v).astype(float).values for v in vs]
    beta, V = _fit(D, np.column_stack(dv + [d * D["z_r"].values for d in dv]), lags=lags)
    k = len(vs)
    rows = [_row(v, beta[k + i], math.sqrt(V[k + i, k + i]), int((D["variable"] == v).sum()))
            for i, v in enumerate(vs)]
    beta, V = _fit(D, np.column_stack(dv + [D["z_r"].values]), lags=lags)
    rows.append(_row("pooled", beta[-1], math.sqrt(V[-1, -1]), len(D)))
    return pd.DataFrame(rows)


def raw_unit_slopes(cg, consts):
    """Per-variable slopes in the variables' own units (points of error per point of revision):
    standardised slope x s_error / s_revision."""
    out = cg[cg["label"] != "pooled"].copy()
    ratio = out["label"].map(lambda v: consts[(v, "error")] / consts[(v, "revision")])
    for col in ("estimate", "se", "lo90", "hi90"):
        out[col] = out[col] * ratio
    return out


# ------------------------------------------------------------------------- slopes after small / large surprises
def small_large_slopes(main_fit, by_variable_fit, variables=k20.VARS):
    """Slope after small surprises (b_v) and after large ones (b_v + c_v), by variable, from the
    preregistered S1 regression (one c per variable); and pooled: mean of the b_v and that mean + c from
    the main regression. 90% intervals from the DK4 covariance of each regression."""
    rows = []
    k = len(variables)
    beta, V = by_variable_fit["beta"], by_variable_fit[4]
    for i, v in enumerate(variables):
        w_small = np.zeros(len(beta))
        w_small[2 * k + i] = 1
        w_large = w_small.copy()
        w_large[3 * k + i] = 1
        rows.append({"label": v, "class": "small", **dict(zip(("estimate", "se"), stats.combination(beta, V, w_small)))})
        rows.append({"label": v, "class": "large", **dict(zip(("estimate", "se"), stats.combination(beta, V, w_large)))})
    beta, V = main_fit["beta"], main_fit[4]
    w_small = np.zeros(len(beta))
    w_small[2 * k:3 * k] = 1 / k
    w_large = w_small.copy()
    w_large[-1] = 1
    rows.append({"label": "pooled", "class": "small", **dict(zip(("estimate", "se"), stats.combination(beta, V, w_small)))})
    rows.append({"label": "pooled", "class": "large", **dict(zip(("estimate", "se"), stats.combination(beta, V, w_large)))})
    out = pd.DataFrame(rows)
    out["lo90"], out["hi90"] = out["estimate"] - Z90 * out["se"], out["estimate"] + Z90 * out["se"]
    return out


# ------------------------------------------------------------------------- 2. extra slope c, by variable / episode
def c_by_variable(fields, variables=k20.VARS):
    """The preregistered S1 fields c_<v> and et_c_<v>_dk4, as a table."""
    return pd.DataFrame([_row(v, fields[f"c_{v}"], fields[f"et_c_{v}_dk4"], None) for v in variables])


def c_without_episodes(base, without):
    """c with each episode window removed (preregistered fields c_sans_E1..E7) with its DK4 se and t,
    and the number of main rows removed."""
    rows = []
    for k, (name, (w0, w1)) in enumerate(K20_EPISODES.items(), start=1):
        ck, tk, sk = without[k]
        removed = int(base["t_target"].between(w0, w1).sum())
        rows.append(_row(name, ck, sk, len(base) - removed, window=EPISODE_LABELS[name], rows_removed=removed, t=tk))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------- 3. what the sort variable does
def variance_ratio(D, large):
    """Variance of z_r after large news over variance after small news, each around its variable-class mean
    (the preregistered rapport_variance_revision when large = 'large')."""
    dev = D["z_r"] - D.groupby(["variable", large])["z_r"].transform("mean")
    return float(np.mean(dev[D[large] == 1] ** 2) / np.mean(dev[D[large] == 0] ** 2))


def sort_comparison(base):
    """The extra slope c under three definitions of 'large': the preregistered top third of |surprise|
    (K20), the card's |z_r| > 1 (preregistered secondary S7, c_coupure_revision), and the top third of
    |revision| (same share of large rows as K20). Sorting on the revision itself selects on the noise that
    the revision shares with the error (preregistration section 7)."""
    D = base.copy()
    D["large_revision"] = (np.abs(D["z_r"]) > 1).astype(float)
    D["large_revision_third"] = top_third(D, "revision")
    rows = []
    for col, label in (("large", "top third of |surprise| (preregistered)"),
                       ("large_revision", "|revision| > 1 s.d. (card; S7)"),
                       ("large_revision_third", "top third of |revision|")):
        c, se = k20.c_and_se(k20.regress(D, large=col, variables=variables_in(D)))
        rows.append(_row(label, c, se, len(D), share_large=float(D[col].mean()), variance_ratio=variance_ratio(D, col)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------- 4. by decade
def by_decade(D):
    """Pooled base slope (one constant per variable, one common slope, no size split) by decade of target."""
    rows = []
    for label, t0, t1 in DECADES:
        sub = D[D["t_target"].between(t0, t1)]
        r = cg_slopes(sub).iloc[-1]
        rows.append(_row(label, r["estimate"], r["se"], int(r["n"]), quarters=int(sub["t_target"].nunique()),
                         variables=", ".join(variables_in(sub))))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------- euro area (K20-ZE)
# Same ideas for the euro-area replication: six series (variable x horizon), Driscoll-Kraay with 8 lags
# (scores summed by survey round) and the critical value 1.708 of its preregistration.
EA_PERIODS = [("2000-2009", 2000, 2009), ("2010-2019", 2010, 2019), ("2020-2025", 2020, 2025)]


def _ea_row(label, est, se, n, **extra):
    from .k20ze import CRIT
    return {"label": label, "estimate": est, "se": se, "lo90": est - CRIT * se, "hi90": est + CRIT * se, "n": n,
            **extra}


def ea_c_by_variable(fields):
    """The preregistered S1 fields c_<v> and et_c_<v>_dk8 of K20-ZE, with 90% intervals (critical value 1.708)."""
    from .k20ze import VARIABLES
    return pd.DataFrame([_ea_row(v, fields[f"c_{v}"], fields[f"et_c_{v}_dk8"], None) for v in VARIABLES])


def ea_pandemic(fields, data):
    """c without and with the RGDP and UNEM rows of 2020-2021 (preregistered main test and S3), and, added
    here, c by variable on the rows with the pandemic."""
    from . import k20ze
    complete = data[data["complete"] == 1]
    rows = [_ea_row("all variables, main sample (pandemic rows excluded; preregistered test)", fields["c"],
                    fields["et_c_dk8"], fields["n_principal"]),
            _ea_row("all variables, with the pandemic rows (preregistered S3)", fields["c_avec_pandemie"],
                    fields["et_c_avec_pandemie_dk8"], int(len(complete)))]
    R = k20ze.regress(complete, by_variable=True)
    for i, v in enumerate(k20ze.VARIABLES):
        c, se = k20ze.c_and_se(R, 18 + i)
        rows.append(_ea_row(f"{v}, with the pandemic rows", c, se, int((complete["variable"] == v).sum())))
    return pd.DataFrame(rows)


def ea_base_slopes(base):
    """Base under-reaction slope with no size split: one constant per series and either one slope per
    variable (pooled over the two horizons) or one common slope (the preregistered b_commun)."""
    from . import k20ze

    def by_variable(D):
        groups = [g for g in k20ze.SERIES if g in set(D["series"])]
        return np.column_stack([(D["series"] == g).astype(float).values for g in groups]
                               + [(D["variable"] == v).astype(float).values * D["z_r"].values for v in k20ze.VARIABLES])
    R = k20ze.regress(base, X=by_variable)
    k = len(R["beta"]) - 3
    rows = [_ea_row(v, *k20ze.c_and_se(R, k + i), int((base["variable"] == v).sum())) for i, v in enumerate(k20ze.VARIABLES)]
    rows.append(_ea_row("pooled", *k20ze.c_and_se(k20ze.regress(base, X=k20ze.common_slope_design)), len(base)))
    return pd.DataFrame(rows)


def ea_by_period(base):
    """Common base slope by period of the target year (three periods of ten, ten and six target years)."""
    from . import k20ze
    rows = []
    for label, y0, y1 in EA_PERIODS:
        sub = base[base["target_year"].between(y0, y1)]
        c, se = k20ze.c_and_se(k20ze.regress(sub, X=k20ze.common_slope_design))
        rows.append(_ea_row(label, c, se, len(sub), rounds=int(sub["t_round"].nunique()),
                            target_years=int(sub["target_year"].nunique())))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------- Livingston (K20-LIV)
# Same ideas for the Livingston replication: five variables, Driscoll-Kraay with 2 lags of half-years
# (column t_target = half_year after k20liv.standardise) and the critical value 1.645.
def liv_c_by_variable(fields):
    """The preregistered S1 fields c_<v> and et_c_<v>_dk2 of K20-LIV, with 90% intervals."""
    from .k20liv import VARIABLES
    return pd.DataFrame([_row(v, fields[f"c_{v}"], fields[f"et_c_{v}_dk2"], None) for v in VARIABLES])


def liv_samples(fields):
    """c in the main sample and in the preregistered secondary samples S3 (with the four UNPR pandemic
    targets), S4 (targets from 1985-06) and S5 (targets to 2019-12)."""
    return pd.DataFrame([
        _row("main sample (preregistered test)", fields["c"], fields["et_c_dk2"], fields["n_principal"]),
        _row("with the four UNPR targets 2020-06 to 2021-12 (S3)", fields["c_avec_pandemie"],
             fields["et_c_avec_pandemie_dk2"], fields["n_principal"] + 4),
        _row("targets from 1985-06 (S4)", fields["c_depuis_1985"], fields["et_c_depuis_1985_dk2"], None),
        _row("targets to 2019-12 (S5)", fields["c_avant_2020"], fields["et_c_avant_2020_dk2"], None)])


def liv_base_slopes(base):
    """Base slope by variable and pooled (the preregistered b_regroupe), no size split, DK 2 lags."""
    from .k20liv import LAGS, VARIABLES
    return cg_slopes(base, lags=LAGS, order=VARIABLES)


def comparison(us, ea, liv=None):
    """The surveys side by side: the quantities that decide or frame each preregistered test.
    Each argument is (fields, pooled base-slope row); `liv` is optional."""
    from .k20ze import CRIT as CRIT_EA
    (u, ub), (e, eb) = us, ea
    cols = ["quantity", "US SPF (K20)", "ECB SPF (K20-ZE)"] + (["Livingston (K20-LIV)"] if liv else [])
    l, lb = liv if liv else ({}, {})

    def row(name, fu, fe, fl=None):
        return [name, fu, fe] + ([fl] if liv else [])
    rows = [
        row("survey; targets", "Philadelphia Fed SPF, quarterly growth or levels, 1969-2026",
            "ECB SPF, calendar-year averages, 2000-2025",
            "Livingston Survey, June and December levels, 1947-2026" if liv else None),
        row("rows in the main sample", f"{u['n_principal']}", f"{e['n_principal']}",
            f"{l.get('n_principal', '')}"),
        row("dates (clusters for the standard error)", f"{u['n_trimestres']} target quarters",
            f"{e['n_tours']} rounds, {e['n_annees_cibles']} target years",
            f"{l.get('n_dates', '')} half-years" if liv else None),
        row("standard error; critical value of the 90% interval", "Driscoll-Kraay, 4 lags; 1.645",
            f"Driscoll-Kraay, 8 lags; {CRIT_EA}", "Driscoll-Kraay, 2 lags; 1.645" if liv else None),
        row("base slope, no size split (one constant per series, one common slope)",
            f"{ub['estimate']:.3f} (se {ub['se']:.3f})", f"{e['b_commun']:.3f} (se {e['et_b_commun_dk8']:.3f})",
            f"{l['b_regroupe']:.3f} (se {l['et_b_regroupe_dk2']:.3f})" if liv else None),
        row("base slope after small news (mean of the b)", f"{u['b_moyen']:.3f}", f"{e['b_moyen']:.3f}",
            f"{l['b_moyen']:.3f}" if liv else None),
        row("slope after large news (mean b + c)", f"{u['pente_moyenne_grandes']:.3f}",
            f"{e['pente_moyenne_grandes']:.3f}", f"{l['pente_moyenne_grandes']:.3f}" if liv else None),
        row("**extra slope after large news, c (se)**", f"**{u['c']:.3f}** ({u['et_c_dk4']:.3f})",
            f"**{e['c']:.3f}** ({e['et_c_dk8']:.3f})", f"**{l['c']:.3f}** ({l['et_c_dk2']:.3f})" if liv else None),
        row("90% interval of c", f"[{u['borne_basse_ic90']:.3f}, {u['borne_haute_ic90']:.3f}]",
            f"[{e['borne_basse_ic90']:.3f}, {e['borne_haute_ic90']:.3f}]",
            f"[{l['borne_basse_ic90']:.3f}, {l['borne_haute_ic90']:.3f}]" if liv else None),
        row("variance ratio of revisions, large / small news", f"{u['rapport_variance_revision']:.2f}",
            f"{e['rapport_variance_revision']:.2f}", f"{l['rapport_variance_revision']:.2f}" if liv else None),
        row("k = s.d. revision / s.d. error (mean)", f"{u['k_moyen']:.3f}", f"{e['k_moyen']:.3f}",
            f"{l['k_moyen']:.3f}" if liv else None),
        row("noise share of the revision variance, nu", "assumed 0.20", "assumed 0.20",
            f"measured {l['nu_mesure']:.3f} from the individual answers, doubled to {2 * l['nu_mesure']:.3f}" if liv else None),
        row("mechanical bias", f"{u['biais_mecanique_nu20']:.3f}", f"{e['biais_mecanique_nu20']:.3f}",
            f"{l['biais_mecanique_mesure']:.3f} (with the assumed 0.20: {l['biais_mecanique_nu20']:.3f})" if liv else None),
        row("survival floor max(0.10, bias)", f"{u['seuil_survie_bas']:.3f}", f"{e['seuil_survie_bas']:.3f}",
            f"{l['seuil_survie_bas']:.3f}" if liv else None),
        row("c without each episode (range)",
            f"{u['c_min_sans_episode']:.3f} to {max(u[f'c_sans_E{i}'] for i in range(1, 8)):.3f}",
            f"{e['c_min_sans_episode']:.3f} to {max(e[f'c_sans_E{i}'] for i in range(1, 4)):.3f}",
            f"{l['c_min_sans_episode']:.3f} to {max(l[f'c_sans_E{i}'] for i in range(1, 12)):.3f}" if liv else None),
        row("effective observations", f"{u['n_effectif']:.0f}", f"{e['n_effectif']:.0f}",
            f"{l['n_effectif']:.0f}" if liv else None),
    ]
    return pd.DataFrame(rows, columns=cols)
