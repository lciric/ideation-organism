"""K20-ZE, the euro-area replication of K20, is reproduced in the sibling project (projects/spf-news-size-underreaction/).
Here: the byte-for-byte audit copies match the seal, and the sealed rule applied to the sealed numbers gives the sealed
verdict for the reason stated in the paper (upper bound of c below the predicted +0.40)."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "audit" / "K20-ZE"
SEAL = "91c3f919cbf571abfeee2e087b387b4962960e183f832a7e4983de7bb802e63a"


def _run_all():
    spec = importlib.util.spec_from_file_location("run_all", ROOT / "run_all.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_k20ze_seal():
    sha = hashlib.sha256((FOLDER / "preenregistrement.md").read_bytes()).hexdigest()
    assert sha == SEAL == (FOLDER / "preenregistrement.md.sha256").read_text().split()[0]
    assert json.loads((FOLDER / "verdict.json").read_text(encoding="utf-8"))["sceau_preenregistrement"] == SEAL


def test_k20ze_verdict_from_sealed_rule():
    sealed = json.loads((FOLDER / "verdict.json").read_text(encoding="utf-8"))
    fields = sealed["chiffres_verificateur"]
    assert fields == json.loads((FOLDER / "verification.json").read_text(encoding="utf-8"))
    verdict, held = _run_all().verdict_from_rule(sealed["regle"], fields)
    assert (verdict, held) == ("éliminée", []) and sealed["verdict"] == "éliminée"
    assert fields["controle_positif_ok"] == 1 and fields["borne_basse_b_commun_ic90"] > 0
    assert fields["borne_haute_ic90"] < 0.40 and fields["c"] < 0
    assert max(fields[f"c_sans_E{i}"] for i in (1, 2, 3)) < 0
