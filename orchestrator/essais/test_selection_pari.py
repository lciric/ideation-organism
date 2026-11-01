import copy
import random
import unittest

from pole import selection_pari as sp
from pole.controles_pari import executer_controles, loi_tricheur
from pole.duel_pari import executer_duel


def engagement_simple(graine=1, tirages=80):
    rng = random.Random(graine)
    loi = sp.loi_softmax_aleatoire(rng)
    return loi, sp.geler_engagement(sp.construire_engagement("h", loi, sp.tirer_instances(rng, tirages)))


class Gardes(unittest.TestCase):
    def test_test_gele_et_tirages_lies_evalues(self):
        loi, gele = engagement_simple()
        ev = sp.evaluer(gele, sp.tirer_frais(gele, loi, 7))
        self.assertTrue(ev["promue"])
        self.assertEqual(ev["empreinte_engagement"], gele.empreinte)

    def test_test_modifie_apres_gel_refuse(self):
        loi, gele = engagement_simple()
        tirages = sp.tirer_frais(gele, loi, 7)
        gele.engagement["alpha"] = 0.5
        with self.assertRaises(sp.EngagementModifie):
            sp.evaluer(gele, tirages)

    def test_tirages_non_lies_refuses(self):
        loi, gele = engagement_simple()
        _, autre = engagement_simple(graine=2)
        with self.assertRaises(sp.TiragesNonLies):
            sp.evaluer(gele, sp.tirer_frais(autre, loi, 7))
        tirages = sp.tirer_frais(gele, loi, 7)
        tirages["issues"] = tirages["issues"][:-1]
        with self.assertRaises(sp.TiragesNonLies):
            sp.evaluer(gele, tirages)

    def test_lois_validees(self):
        rng = random.Random(3)
        sp.valider_loi(sp.loi_softmax_aleatoire(rng), 3, 2)
        for mauvaise in ({"type": "fixe", "probas": [1, 2]}, {"type": "softmax", "poids": [[1, 2]], "biais": [0]},
                         {"type": "melange", "composantes": [{"type": "fixe", "probas": [1, 1, 1]}], "poids": [0.7]},
                         {"type": "inconnu"}):
            with self.subTest(loi=mauvaise), self.assertRaises(sp.LoiInvalide):
                sp.valider_loi(mauvaise, 3, 2)

    def test_adimensionnement_identique_au_parent(self):
        rng = random.Random(4)
        p1, p2 = sp.loi_softmax_aleatoire(rng), sp.loi_softmax_aleatoire(rng)
        cachee = loi_tricheur("adimensionnement", p1, p2, [0.3, 0.3, 0.4], rng)
        for x in sp.tirer_instances(rng, 20):
            for a, b in zip(sp.proba(p1, x, [], 0), sp.proba(cachee, x, [], 0)):
                self.assertAlmostEqual(a, b, places=12)


class CritereDesFilles(unittest.TestCase):
    """Troisième ajout : nul augmenté des parents et enveloppes, part de calibrage, marge 2·delta0."""

    def preparer(self, delta0, graine=21):
        rng = random.Random(graine)
        p1, p2, p3 = (sp.loi_softmax_aleatoire(rng, force=2.0) for _ in range(3))
        fille = {"type": "si_sinon", "condition": {"sous_population": 0}, "si": p1, "sinon": p3}
        monde = {"type": "par_sous_population", "lois": {"0": p1, "1": p3}}
        bib = sp.bibliotheque_fille({"A": p1, "B": p2}, 2)
        gele = sp.geler_engagement(sp.construire_engagement("fille", fille, sp.tirer_instances(rng, 240), 3, 0.05, bib,
                                                            "continu", part_calibrage=40, delta0=delta0))
        return gele, monde

    def test_fille_neuve_promue_avec_marge_raisonnable(self):
        gele, monde = self.preparer(0.01)
        ev = sp.evaluer(gele, sp.tirer_frais(gele, monde, 3))
        self.assertTrue(ev["promue"])
        self.assertTrue(ev["marge_atteinte"])

    def test_marge_non_atteinte_bloque_la_promotion(self):
        gele, monde = self.preparer(10.0)
        ev = sp.evaluer(gele, sp.tirer_frais(gele, monde, 3))
        self.assertGreaterEqual(ev["log_richesse_max"], ev["seuil_log"], "la richesse seule aurait promu la fille")
        self.assertFalse(ev["marge_atteinte"])
        self.assertFalse(ev["promue"])

    def test_poids_du_melange_ajuste_sur_la_part_de_calibrage(self):
        rng = random.Random(4)
        p1, p2 = sp.loi_softmax_aleatoire(rng, force=3.0), sp.loi_softmax_aleatoire(rng, force=3.0)
        membres = sp.calibrer([m for m in sp.bibliotheque_fille({"A": p1, "B": p2}, 2) if m["nom"] == "melange_parents"],
                              *self.tirages_melange(rng, p1, p2, 0.3))
        self.assertAlmostEqual(membres[0]["poids_calibre"], 0.3, delta=0.1)

    @staticmethod
    def tirages_melange(rng, p1, p2, w):
        instances = sp.tirer_instances(rng, 3000)
        monde = {"type": "melange", "composantes": [p1, p2], "poids": [w, 1 - w]}
        return [sp.tirer_categorie(rng, sp.proba(monde, x, [], 0)) for x in instances], instances


class ControlesFatals(unittest.TestCase):
    """Priorité (2) : T1a, T6 et la batterie de tricheurs, 1 000 répétitions chacun (tirages courts pour la durée)."""

    @classmethod
    def setUpClass(cls):
        cls.r = executer_controles(graine=11, repetitions=1000, tirages=40, part_calibrage=15,
                                   controles=("T1a", "T6", "tricheurs"))
        # Le parasite de Kelly ne gagne que ~0,02 nat par tirage contre une marginale ajustée à part : il faut un horizon
        # de l'ordre de 200 tirages pour que le contrôle voie le critère cassé (constat noté au LISEZMOI).
        cls.artefacts = executer_controles(graine=11, repetitions=1000, tirages=200, controles=("artefacts",))

    def test_critere_correct_passe(self):
        v = self.r["verdicts"]
        self.assertTrue(v["T1a"]["passe"], v["T1a"])
        self.assertTrue(v["T6"]["passe"], v["T6"])
        self.assertTrue(v["tricheurs"]["passe"], v["tricheurs"])
        self.assertFalse(v["critere_invalide"])

    def test_criteres_casses_detectes(self):
        self.assertTrue(all(self.artefacts["verdicts"]["artefacts_detectes"].values()), self.artefacts["verdicts"])
        tricheurs = {a["controle"]: a["taux"] > 0.05 for a in self.r["tricheurs"]["artefacts"]}
        self.assertTrue(all(tricheurs.values()), tricheurs)

    def test_fille_neuve_promue(self):
        self.assertGreater(self.r["verdicts"]["tricheurs"]["puissance_fille_neuve"], 0.5)

    def test_moins_de_1000_repetitions_refuse(self):
        with self.assertRaises(ValueError):
            executer_controles(repetitions=999, controles=("T1a",))


class Duel(unittest.TestCase):
    def test_duel_et_regle_d_arret(self):
        d = executer_duel(graine=5, par_type=6, tirages=60, reservoir=200, entrainement=60)
        self.assertEqual(set(d["bras"]), {1, 2, 3})
        self.assertIn("refutateur_superflu", d["regle_d_arret"])
        self.assertGreaterEqual(d["bras"][1]["fausses_eliminees"], d["bras"][3]["fausses_eliminees"])


if __name__ == "__main__":
    unittest.main()
