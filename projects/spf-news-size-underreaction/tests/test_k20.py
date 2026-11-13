"""Acceptance: every sealed verifier number of K20 is reproduced within its preregistered tolerance, the
sealed rule gives the sealed verdict, and the one schema failure is the documented one."""
import json
from pathlib import Path

import pytest

from snu import k20, measures

ROOT = Path(__file__).resolve().parents[1]
SEALED = json.loads((ROOT / "audit" / "K20" / "verdict.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def k20_data():
    df = measures.build_k20()
    fields, _ = k20.run(df)
    return df, fields


def test_all_53_sealed_numbers_reproduce(k20_data):
    _, fields = k20_data
    tol = SEALED["regle"]["tolerance"]
    assert len(SEALED["chiffres_verificateur"]) == 53
    bad = {k: (v, fields[k]) for k, v in SEALED["chiffres_verificateur"].items() if abs(fields[k] - v) > tol[k]}
    assert not bad


def test_sealed_rule_gives_the_sealed_verdict(k20_data):
    import run_all
    _, fields = k20_data
    verdict, held = run_all.verdict_from_rule(SEALED["regle"], fields)
    assert verdict == SEALED["verdict"] == "non concluant"
    assert [c["champ"] for c in held] == ["n_violations_schema"]


def test_only_schema_check_9_fails_on_one_row_outside_every_regression(k20_data):
    df, _ = k20_data
    checks = k20.schema_violations(df)
    assert [k for k, ok in checks.items() if not ok] == [9]
    bad = k20.check9_failures(df)
    assert list(zip(bad["variable"], bad["target"])) == [("CPI", "2026-Q1")]
    assert bad["complete"].iloc[0] == 0 and bad["main"].iloc[0] == 0


def test_estimate_does_not_depend_on_the_failing_row(k20_data):
    """Dropping CPI 2026-Q1 breaks the grid check instead, but leaves every estimate identical."""
    df, fields = k20_data
    without = df.drop(index=k20.check9_failures(df).index)
    other, _ = k20.run(without)
    for key in ("c", "et_c_dk4", "b_moyen", "c_avec_pandemie", "c_mediane", "c_TBILL"):
        assert other[key] == pytest.approx(fields[key], abs=1e-12)
