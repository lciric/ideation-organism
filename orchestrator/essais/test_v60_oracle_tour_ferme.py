"""Essais de la v60 — oracle et classement des cartes du tour fermé (`pole/oracle_tour_ferme_v60.py`). Préenregistrement
`prereg/preenregistrement-tour-ferme-v1-brouillon1.md`, sections 3 et 4.4.

Hors ligne : aucun réseau, aucun modèle. Monde planté du mode à blanc v59 (S-V1 de `exemples/temoins-pari-demo-v1.json`).
Chaque règle : un cas sain et un artefact (R5)."""

import os
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import oracle_tour_ferme_v60 as O  # noqa: E402

RACINE_ORACLE = 20261102


class Monde(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.monde = A.charger_monde(RACINE)
        cls.v = cls.monde["loi"]
        cls.o = O.Oracle(cls.v, RACINE_ORACLE, A.DIM)
        cls.z1 = {"type": "softmax", "poids": [[0.0, w[1]] for w in cls.v["poids"]], "biais": list(cls.v["biais"])}


class Mesures(Monde):
    def test_concorde_avec_l_oracle_du_mode_a_blanc(self):
        for loi in (self.v, self.monde["fausses"]["S-F2"], self.z1):
            ref = A.oracle(loi, self.monde, RACINE_ORACLE)
            self.assertAlmostEqual(self.o.gain(loi), ref["gain_attendu_nat"], places=5)
            self.assertAlmostEqual(self.o.divergence(loi), ref["divergence_a_la_loi_plantee_nat"], places=5)

    def test_loi_plantee(self):
        self.assertAlmostEqual(self.o.gain(self.v), 0.523, places=2)
        self.assertLess(abs(self.o.divergence(self.v)), 1e-9)
        self.assertEqual(self.o.gain_archive({}), 0.0)

    def test_copie_et_melange_de_l_archive_ne_sont_pas_nouveaux(self):
        archive = {"A1": self.z1, "A2": self.monde["fausses"]["S-F2"]}
        ga = self.o.gain_archive(archive)
        melange = {"type": "melange", "composantes": [self.z1, self.monde["fausses"]["S-F2"]], "poids": [0.7, 0.3]}
        for loi in (self.z1, melange, {"type": "transformee", "base": self.z1, "puissance": 1.3}):
            self.assertLess(self.o.gain(loi) - ga, 1e-4)  # ΔG ≤ 0 à la précision de l'ajustement

    def test_loi_plantee_reste_nouvelle_face_a_une_archive_partielle(self):
        m = self.o.mesurer(self.v, {"Z1": self.z1})
        self.assertGreaterEqual(m["gain_archive_nat"], 0.40)
        self.assertGreater(m["delta_gain_nat"], O.G0)  # L* apporte plus que z1 seul, même tempéré et incliné

    def test_loi_plantee_dans_l_archive_rien_de_nouveau(self):
        m = self.o.mesurer(self.v, {"VRAIE": self.v})
        self.assertLess(m["delta_gain_nat"], 1e-6)

    def test_loi_plantee_trop_confiante_dans_l_archive_rien_de_nouveau(self):
        # l'archive tient L* accentuée (puissance 2) : tempérée (a = 1/2), c'est L* ; la loi plantée n'apporte rien de plus
        m = self.o.mesurer(self.v, {"ACC": {"type": "transformee", "base": self.v, "puissance": 2.0}})
        self.assertLess(m["delta_gain_nat"], 1e-4)

    def test_mise_en_commun_lineaire_de_l_archive_compte(self):
        # monde = ½·S-V2 + ½·S-V3, archive {S-V2, S-V3} : seule la mise en commun linéaire retrouve le monde
        import json
        with open(os.path.join(RACINE, "exemples", "temoins-pari-demo-v1.json"), encoding="utf-8") as f:
            lois = {x["identifiant"]: x["loi_predictive"] for x in json.load(f)["fiches"]}
        monde = {"type": "melange", "composantes": [lois["S-V2"], lois["S-V3"]], "poids": [0.5, 0.5]}
        o = O.Oracle(monde, RACINE_ORACLE, A.DIM)
        archive = {"V2": lois["S-V2"], "V3": lois["S-V3"]}
        self.assertGreater(o.gain(monde), 0.25)
        self.assertGreater(o.gain_archive(archive), o.gain(monde) - 1e-4)
        self.assertLess(max(o.temperee_inclinee(l)[0] for l in archive.values()), o.gain(monde) - 0.1)


class Classement(unittest.TestCase):
    def c(self, **kw):
        base = dict(promue=True, survit=True, gain_nat=0.3, delta_gain_nat=0.1, divergence_nat=0.2, bras="reel")
        base.update(kw)
        return O.classer(**base)

    def test_vraie_decouverte_et_loi_plantee(self):
        self.assertTrue(self.c()["vraie_decouverte"])
        self.assertFalse(self.c()["loi_plantee_retrouvee"])
        self.assertTrue(self.c(divergence_nat=0.01)["loi_plantee_retrouvee"])

    def test_fausse_decouverte_sans_information_ou_sans_nouveaute(self):
        self.assertTrue(self.c(gain_nat=0.01)["fausse_decouverte"])
        self.assertTrue(self.c(delta_gain_nat=0.0)["fausse_decouverte"])
        self.assertFalse(self.c(delta_gain_nat=0.0)["vraie_decouverte"])

    def test_recopie_toujours_fausse(self):
        r = self.c(bras="recopie_melange")
        self.assertTrue(r["fausse_decouverte"])
        self.assertFalse(r["vraie_decouverte"])

    def test_non_survivante_ni_vraie_ni_fausse_mais_fausse_promotion_comptee(self):
        r = self.c(survit=False, gain_nat=-0.1)
        self.assertFalse(r["fausse_decouverte"] or r["vraie_decouverte"])
        self.assertTrue(r["fausse_promotion_du_juge"])
        self.assertFalse(self.c(survit=False)["fausse_promotion_du_juge"])

    def test_nombre_non_fini_refuse(self):
        with self.assertRaises(O.OracleRefuse):
            self.c(gain_nat=float("nan"))


class Intervalles(unittest.TestCase):
    def test_wilson_valeurs_du_preenregistrement(self):
        for (x, n), (lo, hi) in {(0, 36): (0.0, 0.096), (4, 36): (0.044, 0.253), (14, 36): (0.248, 0.551),
                                 (8, 8): (0.676, 1.0), (150, 1200): (0.107, 0.145)}.items():
            a, b = O.wilson(x, n)
            self.assertAlmostEqual(a, lo, places=3)
            self.assertAlmostEqual(b, hi, places=3)
        with self.assertRaises(O.OracleRefuse):
            O.wilson(5, 4)

    def test_newcombe_seuil_de_11_sur_36(self):
        self.assertGreater(O.newcombe(11, 36, 4, 36)[0], 0.0)
        self.assertLess(O.newcombe(10, 36, 4, 36)[0], 0.0)
        self.assertAlmostEqual(O.newcombe(9, 36, 4, 36)[0], -0.042, places=3)


if __name__ == "__main__":
    unittest.main()
