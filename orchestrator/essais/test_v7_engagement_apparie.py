"""Essais de l'engagement « apparié » (v7, version 23) : refus, seuils pris au seul calibrage, clé de l'héritage,
scellement, et jugement de bout en bout sur une banque de scores."""

import copy
import random
import unittest

from pole import engagement_apparie as ea
from pole import monde_banque_scores as mbs
from essais.test_v7_monde_banque_scores import banque_synthetique


BLANC_CONTRE_NOIR = {"noir": {"coefficients": {"blanc": 1, "noir": -1}}}


class Construction(unittest.TestCase):
    def setUp(self):
        self.banque = banque_synthetique(random.Random(43), unites_par_partie=(100, 0, 100))
        self.m = mbs.MondeBanqueScores(self.banque, 17)

    def test_refus(self):
        for nom, kw in {
            "règle double": dict(contrastes={"x": {"coefficients": {"blanc": 1, "noir": 1}}}, tau=0.05),
            "cellule inconnue": dict(contrastes={"x": {"coefficients": {"gris": 1}, "constante": -0.5}}, tau=0.05),
            "aucun contraste": dict(contrastes={}, tau=0.05),
            "calibrage comme épreuve": dict(contrastes=BLANC_CONTRE_NOIR, tau=0.05, partie="calibrage"),
            "garde sans δ": dict(contrastes=BLANC_CONTRE_NOIR, tau=0.05, garde={"a": "blanc", "b": "noir"}),
            "calibrage insuffisant": dict(contrastes=BLANC_CONTRE_NOIR, tau=0.0005),
            "m_c": dict(contrastes=BLANC_CONTRE_NOIR, tau=0.05, m_c=0),
        }.items():
            with self.subTest(nom), self.assertRaises(ea.EngagementInvalide):
                ea.construire(self.m, **kw)

    def test_seuils_au_seul_calibrage(self):
        e1 = ea.construire(self.m, BLANC_CONTRE_NOIR, tau=0.05)
        autre = copy.deepcopy(self.banque)
        for ep in autre["episodes"]:
            if ep["partie"] == "epreuve":
                ep["scores"]["blanc"] += 10.0  # l'épreuve change ; le calibrage non
        e2 = ea.construire(mbs.MondeBanqueScores(autre, 17), BLANC_CONTRE_NOIR, tau=0.05)
        self.assertEqual(e1["cle_heritage"]["seuils"], e2["cle_heritage"]["seuils"])

    def test_cle_de_l_heritage(self):
        base = ea.construire(self.m, BLANC_CONTRE_NOIR, tau=0.05)
        self.assertEqual(base["empreinte_cle"], ea.construire(self.m, BLANC_CONTRE_NOIR, tau=0.05)["empreinte_cle"])
        variantes = [dict(tau=0.10), dict(tau=0.05, m_max=10), dict(tau=0.05, strate={"mode": "cout"}),
                     dict(tau=0.05, partie="developpement"),
                     dict(tau=0.05, population="vivier-2"), dict(tau=0.05, garde={"a": "blanc", "b": "noir", "delta": 0.1}),
                     dict(tau=0.05, plan_tranches={1: sorted(self.m.unites("epreuve"))[:50], 2: sorted(self.m.unites("epreuve"))[50:]})]
        cles = {ea.construire(self.m, BLANC_CONTRE_NOIR, **kw)["empreinte_cle"] for kw in variantes}
        self.assertEqual(len(cles | {base["empreinte_cle"]}), len(variantes) + 1)
        # le budget d'entrée n'est pas dans la clé (même affirmation), mais dans l'engagement
        b2 = ea.construire(self.m, BLANC_CONTRE_NOIR, tau=0.05, alpha_c=0.01, m_c=3)
        self.assertEqual(b2["empreinte_cle"], base["empreinte_cle"])
        self.assertNotEqual(b2["empreinte"], base["empreinte"])
        # version 28 (K9-3) : le nom du contraste n'est pas dans la clé — renommer n'est pas une autre affirmation
        renomme = ea.construire(self.m, {"autre_nom": {"coefficients": {"blanc": 1, "noir": -1}}}, tau=0.05)
        self.assertEqual(renomme["empreinte_cle"], base["empreinte_cle"])
        # K9-3 : deux contrastes de même forme dans une fiche : refusés
        with self.assertRaises(ea.EngagementInvalide):
            ea.construire(self.m, {"a": {"coefficients": {"blanc": 1, "noir": -1}}, "b": {"coefficients": {"noir": -1, "blanc": 1}}}, tau=0.05)
        # K8-4, K9-4 : la version de l'e-processus est dans la clé
        self.assertEqual(base["cle_heritage"]["e_processus"]["version"], 28)
        import pole.pari_apparie as pa
        ancien = pa.E_PROCESSUS
        try:
            pa.E_PROCESSUS = dict(ancien, version=99)
            self.assertNotEqual(ea.construire(self.m, BLANC_CONTRE_NOIR, tau=0.05)["empreinte_cle"], base["empreinte_cle"])
        finally:
            pa.E_PROCESSUS = ancien
        # K10-10 : Λ changée ⇒ clé changée
        ancien_l = pa.LAMBDAS
        try:
            pa.LAMBDAS = (0.1, 0.5)
            self.assertNotEqual(ea.construire(self.m, BLANC_CONTRE_NOIR, tau=0.05)["empreinte_cle"], base["empreinte_cle"])
        finally:
            pa.LAMBDAS = ancien_l
        # K9-5 : plan de tranches non disjoint, hors partie, ou vide : refusé
        u = sorted(self.m.unites("epreuve"))
        for plan in ({1: u[:10], 2: u[5:20]}, {1: u[:10] + ["cal-0"]}, {1: []}, {0: u[:10]}):
            with self.subTest(plan=str(plan)[:40]), self.assertRaises(ea.EngagementInvalide):
                ea.construire(self.m, BLANC_CONTRE_NOIR, tau=0.05, plan_tranches=plan)


class Jugement(unittest.TestCase):
    def test_bout_en_bout(self):
        m = mbs.MondeBanqueScores(banque_synthetique(random.Random(47), unites_par_partie=(100, 0, 100)), 19)
        e = ea.construire(m, BLANC_CONTRE_NOIR, tau=0.05, garde={"a": "blanc", "b": "noir", "delta": 0.10})
        r = ea.evaluer(m, e, essai=True)
        self.assertTrue(r["promue"])
        self.assertEqual(r["unites_lues"], 100)
        self.assertGreater(r["bornes_basses"]["noir"], 0.0)
        self.assertEqual(r["empreinte_cle"], e["empreinte_cle"])
        from pole import pari_apparie as pa
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["f"], 0.05)
        c.ajouter_trajectoire("f", [0.0], unites=r["identifiants_unites"])
        c.lire()
        with self.assertRaises(ValueError):  # K7-2, K8-1 : la même lecture ne compte pas deux fois
            c.ajouter_trajectoire("f", [0.0], unites=ea.evaluer(m, e, essai=True)["identifiants_unites"])
        # version 28 : plusieurs gardes (K9-9) ; identité stable de la banque dans les identifiants (K9-2)
        e2 = ea.construire(m, BLANC_CONTRE_NOIR, tau=0.05, garde=[{"a": "blanc", "b": "noir", "delta": 0.10}, {"a": "noir", "b": "blanc", "delta": 0.10}])
        r2 = ea.evaluer(m, e2, essai=True)
        self.assertEqual(sorted(r2["log_gardes_finales"]), ["blanc-noir", "noir-blanc"])
        self.assertEqual(r["identifiants_unites"][0][0], m.identite)
        self.assertEqual(len(r["identifiants_unites"]), 100)
        self.assertEqual(r["identifiants_unites"][0][1], "epreuve")
        nul = mbs.MondeBanqueScores(banque_synthetique(random.Random(53), unites_par_partie=(100, 0, 100), mu=(1.0, 1.0)), 19)
        e0 = ea.construire(nul, {"blanc": {"coefficients": {"blanc": 1}, "constante": -0.9}}, tau=0.05)  # rappel ≥ 0,9 : faux
        self.assertFalse(ea.evaluer(nul, e0, essai=True)["promue"])

    def test_scellement(self):
        m = mbs.MondeBanqueScores(banque_synthetique(random.Random(59), unites_par_partie=(100, 0, 30)), 23)
        e = ea.construire(m, BLANC_CONTRE_NOIR, tau=0.05)
        altere = copy.deepcopy(e)
        altere["cle_heritage"]["seuils"]["blanc"] -= 1.0
        with self.assertRaises(ea.EngagementInvalide):
            ea.evaluer(m, altere, essai=True)
        autre = mbs.MondeBanqueScores(banque_synthetique(random.Random(61), unites_par_partie=(100, 0, 30)), 23)
        with self.assertRaises(ea.EngagementInvalide):
            ea.evaluer(autre, e, essai=True)


if __name__ == "__main__":
    unittest.main()
