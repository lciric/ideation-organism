"""Why the preregistered design sorts on the lagged data surprise and not on the revision itself.

A simulated panel with NO true size effect (the true slope of error on revision is the same for every
size of news) but with measurement error in the published consensus:

  volatility of the quarter   h = exp(N(0, vol_sd^2))          (turbulent and calm quarters)
  true revision               r* = h u,  u ~ Student t(3), unit variance (news has fat tails)
  true error                  e* = beta r* + h eta,  eta ~ N(0, error_sd^2)
  consensus noise             eps3, eps4 ~ N(0, noise_sd^2) x h   ('scaled': disagreement rises with turbulence)
                                                    or x rms(h) ('fixed': noise of the same size in every quarter)
  observed revision           r = r* + eps3 - eps4   (noise of the two surveys)
  observed error              e = e* - eps3          (the noise of survey t-3 enters the error with the other sign)
  lagged data surprise        s = h w,  w ~ N(0, 1)  (tells how turbulent the quarter is; it does not
                                                      contain the noise of survey t-3)

Sorting 'large' on |revision| also sorts on |eps3 - eps4|: small revisions are mostly noise, whose slope is
pulled down, large ones mostly signal, so c > 0 although the true slope is constant (preregistration
section 7, effect 2). Sorting on |s| does not select on the noise. With 'scaled' noise its share of the
revision is the same in calm and turbulent quarters and the surprise sort is unbiased; with 'fixed' noise a
small differential attenuation remains (section 7, effect 1), which the preregistered floor max(0.10, bias)
is there to absorb.

The simulated panel goes through the same functions as the data (k20.standardise, measures.top_third,
k20.regress).
"""
import numpy as np
import pandas as pd

from . import k20
from .measures import top_third

SIM_VARIABLES = ["v1", "v2", "v3", "v4", "v5"]
DEFAULTS = {"beta": 0.6, "noise_sd": 0.25, "vol_sd": 0.6, "error_sd": 2.5, "df": 3}


def simulate_panel(n_quarters, seed, noise="scaled", **params):
    """One simulated panel: 5 variables x n_quarters target quarters, columns variable, t_target, revision,
    error, surprise, main (= 1) and noise (= eps3 - eps4, the noise in the revision, kept to measure its share).
    The quarter's volatility has a common and a variable-specific part."""
    p = {**DEFAULTS, **params}
    rng = np.random.default_rng(seed)
    n = len(SIM_VARIABLES) * n_quarters
    t = np.tile(np.arange(n_quarters), len(SIM_VARIABLES))
    common = rng.normal(0, p["vol_sd"] / np.sqrt(2), n_quarters)[t]
    h = np.exp(common + rng.normal(0, p["vol_sd"] / np.sqrt(2), n))
    u = rng.standard_t(p["df"], n) / np.sqrt(p["df"] / (p["df"] - 2))
    scale = h if noise == "scaled" else np.sqrt(np.mean(h ** 2))
    eps3, eps4 = rng.normal(0, p["noise_sd"], n) * scale, rng.normal(0, p["noise_sd"], n) * scale
    true_revision = h * u
    true_error = p["beta"] * true_revision + h * rng.normal(0, p["error_sd"], n)
    return pd.DataFrame({"variable": np.repeat(SIM_VARIABLES, n_quarters), "t_target": t,
                         "revision": true_revision + eps3 - eps4, "error": true_error - eps3,
                         "surprise": h * rng.normal(0, 1, n), "main": 1,
                         "noise": eps3 - eps4})


def interaction_by_sort(panel, lags=(4,)):
    """Extra slope c (and its DK4 se when lags contains 4) with 'large' = top third of |surprise|
    (the preregistered sort) and with 'large' = |z_r| > 1 (the card's sort on the revision)."""
    D, _ = k20.standardise(panel, pairs=(("revision", "z_r"), ("error", "z_e")))
    D["large"] = top_third(D, "surprise")
    D["large_revision"] = (np.abs(D["z_r"]) > 1).astype(float)
    out = {}
    for key, col in (("surprise_sort", "large"), ("revision_sort", "large_revision")):
        R = k20.regress(D, large=col, lags=lags, variables=SIM_VARIABLES)
        out[key] = k20.c_and_se(R) if 4 in lags else (float(R["beta"][-1]), np.nan)
    return out


def replicate(n_reps=300, n_quarters=200, seed=20261113, noise="scaled"):
    """c under both sorts in n_reps panels of the size of K20 (5 x 200 = 1 000 rows).
    Returns a DataFrame with columns rep, surprise_sort, revision_sort."""
    rows = []
    for rep in range(n_reps):
        res = interaction_by_sort(simulate_panel(n_quarters, seed + rep, noise), lags=())
        rows.append({"rep": rep, "surprise_sort": res["surprise_sort"][0], "revision_sort": res["revision_sort"][0]})
    return pd.DataFrame(rows)


def summarise(reps):
    """Mean and 5th / 95th percentiles of c across replications, for each sort."""
    return {k: {"mean": float(reps[k].mean()), "p05": float(reps[k].quantile(0.05)),
                "p95": float(reps[k].quantile(0.95))} for k in ("surprise_sort", "revision_sort")}


def noise_share(n_quarters=40000, seed=20261113, noise="scaled"):
    """Share of the variance of the observed revision that is consensus noise (nu in section 7)."""
    panel = simulate_panel(n_quarters, seed, noise)
    return float(panel["noise"].var() / panel["revision"].var())
