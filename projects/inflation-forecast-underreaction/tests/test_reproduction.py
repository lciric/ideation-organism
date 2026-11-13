"""Acceptance: every sealed verifier number is reproduced within its preregistered tolerance."""
import json
from pathlib import Path

import pytest

from ifu import h03v2, j02, k01, k20, measures

AUDIT = Path(__file__).resolve().parents[1] / "audit"
CASES = [("H03-v2", h03v2, measures.build_h03v2), ("J02", j02, measures.build_j02),
         ("K01", k01, measures.build_k01), ("K20", k20, measures.build_k20)]


@pytest.mark.parametrize("tid, module, build", CASES, ids=[c[0] for c in CASES])
def test_sealed_numbers_reproduce(tid, module, build):
    sealed = json.loads((AUDIT / tid / "verdict.json").read_text(encoding="utf-8"))
    fields, _ = module.run(build())
    tol = sealed["regle"]["tolerance"]
    bad = {k: (v, fields[k]) for k, v in sealed["chiffres_verificateur"].items() if abs(fields[k] - v) > tol[k]}
    assert not bad
