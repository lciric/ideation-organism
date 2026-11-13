"""Acceptance for the euro-area replication K20-ZE: every sealed verifier number is reproduced within its
preregistered tolerance, the sealed rule gives the sealed verdict, and the schema checks pass; plus unit
tests of the pieces K20-ZE adds to K20 (tie-aware cut, reference periods, episode membership, year clusters)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from snu import k20ze, stats

ROOT = Path(__file__).resolve().parents[1]
SEALED = json.loads((ROOT / "audit" / "K20-ZE" / "verdict.json").read_text(encoding="utf-8"))
SEALED_FILE = ROOT.parents[1] / "ideation-finance" / "tests-de-mort" / "K20-ZE" / "K20-ZE_analyse.csv"


@pytest.fixture(scope="module")
def k20ze_data():
    raw = k20ze.load_raw()
    df = k20ze.build_k20ze(raw)
    fields, _ = k20ze.run(df, raw)
    return raw, df, fields


def test_all_65_sealed_numbers_reproduce(k20ze_data):
    _, _, fields = k20ze_data
    tol = SEALED["regle"]["tolerance"]
    assert len(SEALED["chiffres_verificateur"]) == 65
    bad = {k: (v, fields[k]) for k, v in SEALED["chiffres_verificateur"].items() if abs(fields[k] - v) > tol[k]}
    assert not bad


def test_sealed_rule_gives_the_sealed_verdict(k20ze_data):
    import run_all
    _, _, fields = k20ze_data
    verdict, held = run_all.verdict_from_rule(SEALED["regle"], fields)
    assert verdict == SEALED["verdict"] == "éliminée" and held == []
    assert fields["borne_haute_ic90"] < 0.40 and fields["controle_positif_ok"] == 1


def test_schema_checks_pass_with_no_anomaly(k20ze_data):
    raw, df, _ = k20ze_data
    n_viol, n_anom, failures = k20ze.schema_checks(df, raw)
    assert (n_viol, n_anom) == (0, 0)
    assert failures[1] and failures[2]


@pytest.mark.skipif(not SEALED_FILE.exists(), reason="sealed analysis file not available")
def test_dataset_is_bit_identical_to_the_sealed_analysis_file(k20ze_data):
    _, df, _ = k20ze_data
    sealed = pd.read_csv(SEALED_FILE, dtype=str, keep_default_na=False)
    assert len(sealed) == len(df) == 624
    for ours, theirs in zip(k20ze.COLUMNS, sealed.columns):
        x = df[ours]
        if pd.api.types.is_numeric_dtype(x):
            y = sealed[theirs].map(lambda s: float(s) if s else np.nan)
            assert ((x == y) | (x.isna() & y.isna())).all(), ours
        else:
            assert (x.astype(str) == sealed[theirs]).all(), ours


def test_tie_aware_cut_takes_the_side_closest_to_a_third():
    # 9 rounds, Q = 0.2 falls inside a group of ties: strict keeps 2/9, broad 5/9 -> strict (closer to 1/3)
    Q, strict = k20ze.tie_aware_cut([0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.5, 0.6])
    assert Q == pytest.approx(0.2) and strict
    # 10 rounds, Q = 0.2 again inside a group: strict keeps 1/10, broad 4/10 -> broad (closer to 1/3)
    Q, strict = k20ze.tie_aware_cut([0, 0, 0, 0, 0, 0, 0.2, 0.2, 0.2, 0.9])
    assert Q == pytest.approx(0.2) and not strict


def test_reference_periods_and_episode_membership():
    q = lambda y, n: 4 * y + n - 1  # noqa: E731
    assert k20ze.reference_period("HICP", q(2007, 1)) == "2006Dec"
    assert k20ze.reference_period("HICP", q(2024, 2)) == "2024Feb"      # listed exception
    assert k20ze.reference_period("RGDP", q(2007, 1)) == "2006Q3"
    assert k20ze.reference_period("UNEM", q(2007, 3)) == "2007May"
    assert k20ze.reference_period("UNEM", q(2000, 1)) == "1999Dec"      # listed exception
    # E1 = 2008Q1-2009Q2: the 2007 target forecast in 2007Q4 contains no information from the window,
    # the 2008 target forecast in 2007Q1 does (its year runs into 2008)
    assert not k20ze.in_episode(q(2007, 4), 2007, k20ze.EPISODES["E1"])
    assert k20ze.in_episode(q(2007, 1), 2008, k20ze.EPISODES["E1"])
    assert not k20ze.in_episode(q(2009, 4), 2010, k20ze.EPISODES["E1"])   # previous round 2009Q3 is after T


def test_year_clusters_match_statsmodels():
    rng = np.random.default_rng(4)
    years = np.repeat(np.arange(2000, 2026), 8)
    x = rng.normal(size=len(years))
    y = 0.4 * x + rng.normal(size=len(years)) + np.repeat(rng.normal(size=26), 8)
    X = sm.add_constant(x)
    ref = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": years, "use_correction": False})
    _, u, _ = stats.ols(X, y)
    assert np.allclose(np.sqrt(np.diag(stats.driscoll_kraay_cov(X, u, years, 0))), ref.bse)
