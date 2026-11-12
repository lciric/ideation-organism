"""Essais du lecteur du registre des GO v66 (`pole/registre_go_v66.py`, CLV65-07) : la règle des extensions de la garde de calcul
du dépôt de travail (`.claude/hooks/garde_calcul.py`, `lire_go`), essayée sur des registres artefacts et, **en lecture seule**,
sur le vrai registre `registres/go.md` du dépôt de travail quand il est présent (sinon déclaré non joué) ; équivalence
« admis / refusé » avec la garde elle-même sur chaque registre artefact quand la garde est présente. Aucun réseau.

  python3 -I -B -m pytest -q -p no:cacheprovider essais/test_registre_go_v66.py
"""

import datetime
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import configuration_v53 as c53  # noqa: E402
from pole import registre_go_v66 as R  # noqa: E402

DEPOT_DE_TRAVAIL = "/home/user/controle-ia-travail"
REGISTRE_REEL = os.path.join(DEPOT_DE_TRAVAIL, "registres", "go.md")
GARDE = os.path.join(DEPOT_DE_TRAVAIL, ".claude", "hooks", "garde_calcul.py")
JOUR_DU_REEL = datetime.date(2026, 11, 10)  # jour où les deux GO de la course sont lus (dans leur période de validité)
AUJ = datetime.date.today()
ENTETE = "| id | accordé le | type | périmètre | plafond | échéance | accordé par | référence |\n|---|---|---|---|---|---|---|---|\n"


def _garde():
    if not os.path.isfile(GARDE):
        return None
    spec = importlib.util.spec_from_file_location("garde_calcul_pour_essais_v66", GARDE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


GARDE_MOD = _garde()


def _ligne(ident, accorde, typ, perimetre, plafond, echeance, par="Lazar", ref="réf."):
    return f"| {ident} | {accorde} | {typ} | {perimetre} | {plafond} | {echeance} | {par} | {ref} |\n"


def _registre(*lignes):
    d = tempfile.mkdtemp(prefix="registre-go-v66-")
    p = os.path.join(d, "go.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Registre des GO (essai)\n\n" + ENTETE + "".join(lignes))
    return p


def _garde_admet(chemin):
    """True si la garde de calcul lit le registre sans bloquer ; False si elle bloque (sortie 2)."""
    with redirect_stderr(io.StringIO()):
        try:
            GARDE_MOD.lire_go(Path(chemin))
            return True
        except SystemExit as e:
            if e.code != 2:
                raise
            return False


D0, D1, D9 = AUJ - datetime.timedelta(days=2), AUJ - datetime.timedelta(days=1), AUJ + datetime.timedelta(days=20)
SAIN = _ligne("GO-2026-11-08-02", D0, "calcul", "course de l'organisme", "45 USD", D9)
ENVELOPPE = _ligne("GO-2026-11-10-10", D0, "calcul", "enveloppe", "120 USD (organisme 45, Bailey 75 ; aucun report)", D9)
# registres artefacts : (nom, lignes, la règle de la garde l'admet-elle ?)
CAS = [
    ("sain", (SAIN, ENVELOPPE), True),
    ("doublon sans « extension »", (SAIN, _ligne("GO-2026-11-08-02", D1, "calcul", "autre course", "45 USD", D9)), False),
    ("extension admise", (SAIN, _ligne("GO-2026-11-08-02", D1, "calcul", "Extension : autre objet", "45 USD", D9)), True),
    ("extension d'un autre type", (SAIN, _ligne("GO-2026-11-08-02", D1, "décision", "extension : x", "—", D9)), False),
    ("extension par un autre que Lazar", (SAIN, _ligne("GO-2026-11-08-02", D1, "calcul", "extension : x", "45 USD", D9, par="la mère")), False),
    ("extension antérieure à la première", (SAIN, _ligne("GO-2026-11-08-02", D0 - datetime.timedelta(days=1), "calcul", "extension : x", "45 USD", D9)), False),
    ("extension d'échéance plus lointaine", (SAIN, _ligne("GO-2026-11-08-02", D1, "calcul", "extension : x", "45 USD", D9 + datetime.timedelta(days=1))), False),
    ("extension datée d'un GO sans échéance", (_ligne("GO-2026-10-07-01", D0, "dépôt distant", "dépôt", "—", "—"),
                                               _ligne("GO-2026-10-07-01", D1, "dépôt distant", "extension : x", "—", D9)), False),
    ("extension sans échéance d'un GO sans échéance", (_ligne("GO-2026-10-07-01", D0, "dépôt distant", "dépôt", "—", "—"),
                                                       _ligne("GO-2026-10-07-01", D1, "dépôt distant", "extension : x", "—", "—")), True),
    ("sept colonnes", ("| GO-2026-11-08-02 | 2026-11-08 | calcul | x | 45 USD | 2026-11-30 | Lazar |\n",), False),
    ("date illisible", (_ligne("GO-2026-11-08-02", "8 novembre", "calcul", "x", "45 USD", D9),), False),
    ("GO de calcul sans échéance", (_ligne("GO-2026-11-08-02", D0, "calcul", "x", "45 USD", "—"),), False),
]


class RegleDeLaGarde(unittest.TestCase):
    def test_cas_artefacts_et_sains(self):
        for nom, lignes, admis in CAS:
            with self.subTest(nom):
                p = _registre(*lignes)
                if admis:
                    self.assertIsInstance(R.lire_registre_go_v66(p), dict)
                else:
                    with self.assertRaises(R.GoRefuse):
                        R.lire_registre_go_v66(p)

    @unittest.skipIf(GARDE_MOD is None, f"garde de calcul absente ({GARDE}) : équivalence non jouée sur cette machine")
    def test_equivalence_avec_la_garde_de_calcul(self):
        for nom, lignes, admis in CAS:
            with self.subTest(nom):
                p = _registre(*lignes)
                try:
                    R.lire_registre_go_v66(p)
                    v66 = True
                except R.GoRefuse:
                    v66 = False
                self.assertEqual(v66, _garde_admet(p))
                self.assertEqual(v66, admis)

    def test_registre_absent(self):
        with self.assertRaisesRegex(R.GoRefuse, "absent"):
            R.lire_registre_go_v66(os.path.join(tempfile.mkdtemp(), "go.md"))

    def test_extension_consignee_validite_de_la_premiere(self):
        p = _registre(SAIN, _ligne("GO-2026-11-08-02", D1, "calcul", "extension : x", "50 USD", AUJ))
        g = R.lire_registre_go_v66(p)["GO-2026-11-08-02"]
        self.assertEqual((g["plafond"], g["echeance"], len(g["extensions"])), ("45 USD", D9, 1))

    def test_v53_refusait_l_extension(self):  # le défaut de la v65 (CLV65-07), reproduit sur la lecture v53
        p = _registre(SAIN, _ligne("GO-2026-11-08-02", D1, "calcul", "extension : x", "45 USD", D9))
        with self.assertRaisesRegex(c53.GoRefuse, "en double"):
            c53.lire_registre_go(p)
        self.assertIn("GO-2026-11-08-02", R.lire_registre_go_v66(p))


class Verification(unittest.TestCase):
    def test_sain_montant_seul_et_part_d_enveloppe(self):
        p = _registre(SAIN, ENVELOPPE)
        g = R.verifier_go_v66("GO-2026-11-08-02", p, 45)
        self.assertEqual((g["plafond_lu_usd"], g["forme_du_plafond"]), (45.0, "montant seul"))
        g = R.verifier_go_v66("GO-2026-11-10-10", p, 45)
        self.assertEqual(g["plafond_lu_usd"], 45.0)
        self.assertEqual(g["enveloppe"], {"total_usd": 120.0, "parts_usd": {"organisme": 45.0, "bailey": 75.0}})
        self.assertEqual(R.verifier_go_v66("GO-2026-11-10-10", p, 75, part="Bailey")["plafond_lu_usd"], 75.0)

    def test_artefacts_montant(self):
        p = _registre(SAIN, ENVELOPPE)
        for gid in ("GO-2026-11-08-02", "GO-2026-11-10-10"):
            for m in (40, 50, 120):
                with self.subTest(gid=gid, montant=m), self.assertRaises(R.GoRefuse):
                    R.verifier_go_v66(gid, p, m)

    def test_artefacts_enveloppe(self):
        cas = {"somme fausse": "120 USD (organisme 45, Bailey 70)", "nombre étranger": "120 USD (organisme 45, Bailey 75, 2 alertes)",
               "part en double": "120 USD (organisme 45, organisme 75)", "part absente": "120 USD (bailey 75, autre 45)",
               "total seul déguisé": "120 USD (bailey 120)",
               "approché": "≈ 120 USD (organisme 45, Bailey 75)", "sans parenthèse": "120 USD organisme 45 Bailey 75",
               "total seul": "120 USD"}
        for nom, cellule in cas.items():
            with self.subTest(nom), self.assertRaises(R.GoRefuse):
                R.verifier_go_v66("GO-2026-11-10-10", _registre(_ligne("GO-2026-11-10-10", D0, "calcul", "x", cellule, D9)), 45)

    def test_artefacts_ligne(self):
        cas = {"absent": (_ligne("GO-2026-11-08-03", D0, "calcul", "x", "45 USD", D9),),
               "type": (_ligne("GO-2026-11-08-02", D0, "décision", "x", "45 USD", D9),),
               "accordé par un autre": (_ligne("GO-2026-11-08-02", D0, "calcul", "x", "45 USD", D9, par="la mère"),),
               "pas encore valide": (_ligne("GO-2026-11-08-02", AUJ + datetime.timedelta(days=1), "calcul", "x", "45 USD", D9),),
               "échu": (_ligne("GO-2026-11-08-02", D0 - datetime.timedelta(days=9), "calcul", "x", "45 USD", D1),),
               "révoqué": (SAIN, _ligne("GO-2026-11-09-01", D1, "révocation", "révoque GO-2026-11-08-02", "—", D9)),
               "porte une extension": (SAIN, _ligne("GO-2026-11-08-02", D1, "calcul", "extension : x", "45 USD", D9))}
        for nom, lignes in cas.items():
            with self.subTest(nom), self.assertRaises(R.GoRefuse):
                R.verifier_go_v66("GO-2026-11-08-02", _registre(*lignes), 45)
        with self.assertRaises(R.GoRefuse):
            R.verifier_go_v66("GO-2026-11-08-2", _registre(SAIN), 45)
        with self.assertRaises(R.GoRefuse):
            R.verifier_go_v66("GO-2026-11-08-02", _registre(SAIN), 0)


@unittest.skipIf(not os.path.isfile(REGISTRE_REEL), f"vrai registre absent ({REGISTRE_REEL}) : non joué sur cette machine")
class RegistreReel(unittest.TestCase):
    """Le vrai `registres/go.md` du dépôt de travail, en lecture seule (aucune écriture, aucune copie)."""

    def test_lu_entier(self):
        reg = R.lire_registre_go_v66(REGISTRE_REEL)
        self.assertGreater(len(reg), 0)
        self.assertGreater(sum(len(g["extensions"]) for g in reg.values()), 0)  # le registre porte des extensions (R-389)
        with self.assertRaisesRegex(c53.GoRefuse, "en double"):  # le refus de la v65 (CLV65-07)
            c53.lire_registre_go(REGISTRE_REEL)
        if GARDE_MOD is not None:
            self.assertEqual(sorted(reg), sorted(GARDE_MOD.lire_go(Path(REGISTRE_REEL))))

    def test_les_deux_go_de_la_course(self):
        g = R.verifier_go_v66("GO-2026-11-08-02", REGISTRE_REEL, 45, aujourd_hui=JOUR_DU_REEL)
        self.assertEqual((g["plafond_lu_usd"], g["type"], g["par"], g["echeance"]), (45.0, "calcul", "Lazar", "2026-11-30"))
        g = R.verifier_go_v66("GO-2026-11-10-10", REGISTRE_REEL, 45, aujourd_hui=JOUR_DU_REEL)
        self.assertEqual((g["plafond_lu_usd"], g["enveloppe"]["total_usd"]), (45.0, 120.0))
        for gid in ("GO-2026-11-08-02", "GO-2026-11-10-10"):
            for m in (40, 50, 120):
                with self.subTest(gid=gid, montant=m), self.assertRaises(R.GoRefuse):
                    R.verifier_go_v66(gid, REGISTRE_REEL, m, aujourd_hui=JOUR_DU_REEL)
        with self.assertRaisesRegex(R.GoRefuse, "validité"):
            R.verifier_go_v66("GO-2026-11-08-02", REGISTRE_REEL, 45, aujourd_hui=datetime.date(2026, 12, 1))


if __name__ == "__main__":
    unittest.main()
