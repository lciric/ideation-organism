"""Acceptance for the Livingston replication K20-LIV: every sealed verifier number is reproduced within its
preregistered tolerance, the sealed rule gives the sealed verdict, the schema checks pass and the analysis
dataset is bit-identical to the sealed one; plus unit tests of the pieces K20-LIV adds (dates, episodes,
the surprise on the expected path, the CPI rebasing)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from snu import k20liv

ROOT = Path(__file__).resolve().parents[1]
SEALED = json.loads((ROOT / "audit" / "K20-LIV" / "verdict.json").read_text(encoding="utf-8"))
SEALED_FILE = ROOT.parents[1] / "ideation-finance" / "tests-de-mort" / "K20-LIV" / "K20-LIV_analyse.csv"


@pytest.fixture(scope="module")
def k20liv_data():
    df = k20liv.build_k20liv()
    fields, extra = k20liv.run(df)
    return df, fields, extra


def test_all_63_sealed_numbers_reproduce(k20liv_data):
    _, fields, _ = k20liv_data
    tol = SEALED["regle"]["tolerance"]
    assert len(SEALED["chiffres_verificateur"]) == 63
    bad = {k: (v, fields[k]) for k, v in SEALED["chiffres_verificateur"].items() if abs(fields[k] - v) > tol[k]}
    assert not bad


def test_sealed_rule_gives_the_sealed_verdict(k20liv_data):
    import run_all
    _, fields, _ = k20liv_data
    verdict, held = run_all.verdict_from_rule(SEALED["regle"], fields)
    assert verdict == SEALED["verdict"] == "éliminée" and held == []
    assert fields["borne_haute_ic90"] < 0.40 and fields["controle_positif_ok"] == 1


def test_schema_checks_pass_on_the_main_rows(k20liv_data):
    df, _, _ = k20liv_data
    n_viol, n_anom, _ = k20liv.schema_checks(df)
    assert (n_viol, n_anom) == (0, 0)
    counts = df.groupby("variable", sort=False)[["complete", "main"]].sum()
    assert counts["main"].to_dict() == {"CPI": 156, "UNPR": 124, "PRIME": 89, "TBILL": 67, "TPHS": 112}
    assert len(df) == 555 and df["complete"].sum() == 552


@pytest.mark.skipif(not SEALED_FILE.exists(), reason="sealed analysis file not available")
def test_dataset_is_bit_identical_to_the_sealed_analysis_file(k20liv_data):
    df, _, _ = k20liv_data
    sealed = pd.read_csv(SEALED_FILE, dtype=str, keep_default_na=False)
    assert len(sealed) == len(df)
    for ours, theirs in zip(k20liv.COLUMNS, sealed.columns):
        x = df[ours]
        if pd.api.types.is_numeric_dtype(x):
            y = sealed[theirs].map(lambda s: float(s) if s else np.nan)
            assert ((x == y) | (x.isna() & y.isna())).all(), ours
        else:
            assert (x.astype(str) == sealed[theirs]).all(), ours


def test_dates_and_episodes():
    assert k20liv.month_add("2020-06", 6) == "2020-12" and k20liv.month_add("2020-06", -12) == "2019-06"
    assert k20liv.base_month("1990-06") == "1990-04" and k20liv.base_month("1990-12") == "1990-10"
    assert k20liv.episode_of("2009-12") == "E10" and k20liv.episode_of("2010-12") == ""
    assert k20liv.outturn_series("CPI", "2004-06") == "CPIAUCNS" and k20liv.outturn_series("CPI", "2004-12") == "CPIAUCSL"


def test_surprise_is_the_gap_to_the_path_expected_three_quarters_of_the_way():
    # a rate: base 5.0 in April, survey expects 6.0 for December (8 months later); in October (6 months, 3/4 of
    # the way) the path says 5.75; the October figure is 6.25, so the surprise is +0.5
    r = {"outturn_level": 7.0, "base_level_1": 5.0, "base_level_2": 6.25, "f12_1": 6.5, "f6_2": 6.8, "f6_1": 6.0,
         "bp_1": np.nan, "bp_2": np.nan, "f12_1_med": 6.5, "f6_2_med": 6.8}
    o = k20liv.derived("UNPR", r)
    assert o["surprise"] == pytest.approx(0.5)
    assert o["revision"] == pytest.approx(0.3) and o["error"] == pytest.approx(0.2)


def test_cpi_forecast_is_rebased_with_the_questionnaire_base_value():
    # a forecast 2% above the questionnaire's base value, written in an old index base (base value 150), is 2%
    # above the outturn series' base-month level, whatever that level is
    r = {"outturn_level": 300.0, "base_level_1": 250.0, "base_level_2": 260.0, "f12_1": 153.0, "f6_2": 156.0,
         "f6_1": 151.5, "bp_1": 150.0, "bp_2": 154.0, "f12_1_med": 153.0, "f6_2_med": 156.0}
    o = k20liv.derived("CPI", r)
    assert o["y_f_1"] == pytest.approx(100 * np.log(250.0 * 1.02))
