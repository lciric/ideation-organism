"""Descriptive analyses (NOT preregistered). They describe the K20 data; none of them enters the verdict.

All functions take the standardised main sample (`base`, as returned by k20.run): one row per variable x
target quarter with columns variable, t_target, z_r (standardised revision), z_e (standardised error) and
large (1 after a large surprise). They work for any list of variables, so the same functions can describe
a later replication (for instance the euro-area test K20-ZE).

Standard errors are Driscoll-Kraay with 4 lags (scores summed by target quarter), as in the preregistered
test; 90% intervals are estimate +/- 1.645 se.
"""
import math

import numpy as np
import pandas as pd

from . import k20, stats
from .measures import EPISODE_LABELS, K20_EPISODES, top_third

Z90 = 1.645
DECADES = [("1969-1979", 7879, 7919), ("1980-1989", 7920, 7959), ("1990-1999", 7960, 7999),
           ("2000-2009", 8000, 8039), ("2010-2019", 8040, 8079), ("2020-2026", 8080, 8106)]


def variables_in(D):
    """Variables present in D, in the order of the preregistration."""
    present = set(D["variable"])
    return [v for v in k20.VARS if v in present] + sorted(present - set(k20.VARS))


def _fit(D, X, ze="z_e", lags=4):
    beta, u, _ = stats.ols(X, D[ze].values)
    return beta, stats.driscoll_kraay_cov(X, u, D["t_target"].values, lags)


def _row(label, est, se, n, **extra):
    return {"label": label, "estimate": est, "se": se, "lo90": est - Z90 * se, "hi90": est + Z90 * se, "n": n,
            **extra}


# ------------------------------------------------------------------------- 1. base (Coibion-Gorodnichenko) slope
def cg_slopes(D):
    """Slope of the standardised error on the standardised revision, with no split by surprise size:
    one constant per variable, and either one slope per variable or one pooled slope.
    Returns a DataFrame with one row per variable and a last row 'pooled'."""
    D = D.dropna(subset=["z_r", "z_e"])
    vs = variables_in(D)
    dv = [(D["variable"] == v).astype(float).values for v in vs]
    beta, V = _fit(D, np.column_stack(dv + [d * D["z_r"].values for d in dv]))
    k = len(vs)
    rows = [_row(v, beta[k + i], math.sqrt(V[k + i, k + i]), int((D["variable"] == v).sum()))
            for i, v in enumerate(vs)]
    beta, V = _fit(D, np.column_stack(dv + [D["z_r"].values]))
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
