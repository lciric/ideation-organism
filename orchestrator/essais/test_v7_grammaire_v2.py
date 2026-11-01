"""Essais de la version 0.7.0, version 8 : mondes de la grammaire v2 (formes hors de l'espace du chercheur mécanique).

Cas sains : chaque forme produit une banque aux trois parties et des témoins valides au gabarit ; les témoins exacts
(seuil décalé, trois traits) reproduisent la loi du monde ; les approchés (quadratique, produit) sont déclarés tels.
Artefact (R5) : le chercheur mécanique ne propose aucune loi à trois traits (il s'arrête à deux) — c'est ce qui rend la
grammaire v2 hors de son espace.
"""

import math
import os
import random
import sys
import unittest

from pole import selection_pari as sp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exemples"))
import generer_monde_grammaire_v2 as g2  # noqa: E402


class GrammaireV2(unittest.TestCase):
    def test_formes_parties_et_temoins(self):
        for forme in g2.STRUCTURES:
            with self.subTest(forme=forme):
                banque, temoins, verite = g2.generer_monde(7, structures=[forme] * 3)
                parties = [l["partie"] for l in banque["instances"]]
                self.assertEqual((parties.count("calibrage"), parties.count("developpement"), parties.count("epreuve")),
                                 (150, 300, 450))
                for t in temoins:
                    sp.valider_loi(t["loi"], 3, 4)
                self.assertEqual(verite["M0"]["temoin_exact"], forme in ("seuil_decale", "trois_traits"))

    def test_temoins_exacts_egaux_a_la_loi_du_monde(self):
        rng = random.Random(3)
        for forme in ("seuil_decale", "trois_traits"):
            _, temoins, verite = g2.generer_monde(11, structures=[forme] * 3)
            v = verite["M0"]
            monde = g2.loi_monde(forme, v["i"], v["j"], v["k"], v["a"], v["tau"], 3)
            for _ in range(200):
                z = [rng.gauss(0, 1) for _ in range(4)]
                for a, b in zip(sp.proba(v["loi"], {"z": z, "g": 0}, [], 0), monde(z)):
                    self.assertAlmostEqual(a, b, places=5)

    def test_le_mecanique_ne_propose_jamais_trois_traits(self):
        from pole.proposeurs_references import propositions_mecaniques
        banque, _, _ = g2.generer_monde(13, structures=["trois_traits"] * 3)
        description = {"traits": banque["traits"], "sous_populations": 2,
                       "moniteurs": {m: {"nombre_issues": 3} for m in banque["moniteurs"]}}
        dev = {"instances": [l for l in banque["instances"] if l["partie"] == "developpement"]}
        for p in propositions_mecaniques(description, dev, 20):
            loi = p["loi_predictive"]
            traits = set()
            pile = [loi]
            while pile:
                l = pile.pop()
                if l["type"] == "softmax":
                    traits |= {t for t in range(4) if any(abs(r[t]) > 1e-9 for r in l["poids"])}
                elif l["type"] == "si_sinon":
                    traits.add(l["condition"]["indice"])
                    pile += [l["si"], l["sinon"]]
                elif l["type"] == "par_sous_population":
                    pile += list(l["lois"].values())
            self.assertLessEqual(len(traits), 2, p["enonce"])


if __name__ == "__main__":
    unittest.main()
