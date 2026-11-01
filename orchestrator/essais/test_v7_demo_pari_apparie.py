"""Essais des versions 27, 28 et 29 : tranches d'épreuve dans `engagement_apparie.evaluer` (plan scellé, ordre dérivé de la
génération), mémoire des lignées de clé et journal des parties (`Lignees`), fraîcheur par rapport à la course, clés tenues par
la course, et la démonstration de bout en bout du pari apparié (`demonstrations/demo_pari_apparie_v7.py`) : cas sains et
artefacts (R5), lecture L1 / L2 / L3 à graine fixée, nul répété."""

import importlib.util
import os
import random
import unittest

from pole import engagement_apparie as ea
from pole import monde_banque_scores as mbs
from pole import pari_apparie as pa
from essais.test_v7_monde_banque_scores import banque_synthetique

ICI = os.path.dirname(os.path.abspath(__file__))


def charger_demo():
    chemin = os.path.join(os.path.dirname(ICI), "demonstrations", "demo_pari_apparie_v7.py")
    spec = importlib.util.spec_from_file_location("demo_pari_apparie_v7", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRASTE = {"noir": {"coefficients": {"blanc": 1, "noir": -1}}}


class Tranches(unittest.TestCase):
    def setUp(self):
        self.m = mbs.MondeBanqueScores(banque_synthetique(random.Random(51), unites_par_partie=(100, 0, 60)), 23)
        self.e = ea.construire(self.m, CONTRASTE, tau=0.05)
        self.unites = sorted(self.m.unites("epreuve"))

    def test_tranche_lue_puis_fraicheur(self):
        t1, t2 = self.unites[:30], self.unites[30:]
        r1 = ea.evaluer(self.m, self.e, generation=1, unites=t1, essai=True)
        r2 = ea.evaluer(self.m, self.e, generation=2, unites=t2, essai=True)
        self.assertEqual({u for _, _, u in r1["identifiants_unites"]}, set(t1))
        self.assertEqual(r1["unites"], 30)
        self.assertNotEqual(r1["empreinte_unites"], r2["empreinte_unites"])
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["f", "g"], 0.05)
        c.ajouter_trajectoire("f", r1["trajectoire_log_min"], unites=r1["identifiants_unites"])
        c.ajouter_trajectoire("g", r1["trajectoire_log_min"], unites=r1["identifiants_unites"])  # même tranche, même génération : accepté
        c.lire()
        c.ajouter_trajectoire("f", r2["trajectoire_log_min"], unites=r2["identifiants_unites"])  # tranche disjointe : acceptée
        with self.assertRaises(ValueError):  # K9-1 : g lit en génération 2 des unités lues par la course en génération 1
            c.ajouter_trajectoire("g", r1["trajectoire_log_min"][:5], unites=r1["identifiants_unites"][:5])
        c.lire(sans_partie=({"g": "non lancée"} if "g" not in (c.arretees | c.promues) else None))
        with self.assertRaises(ValueError):  # une unité commune aux deux tranches de f : refusée
            c.ajouter_trajectoire("f", r1["trajectoire_log_min"][:5], unites=r1["identifiants_unites"][:5])

    def test_plan_de_tranches_scelle(self):
        plan = {1: self.unites[:30], 2: self.unites[30:]}
        e = ea.construire(self.m, CONTRASTE, tau=0.05, plan_tranches=plan)
        r1 = ea.evaluer(self.m, e, generation=1, essai=True)
        self.assertEqual({u for _, _, u in r1["identifiants_unites"]}, set(plan[1]))
        for kw in (dict(), dict(generation=3), dict(generation=1, unites=self.unites[:5])):
            with self.subTest(kw=str(kw)), self.assertRaises(ea.EngagementInvalide):
                ea.evaluer(self.m, e, **kw, essai=True)
        self.assertNotEqual(e["empreinte_cle"], self.e["empreinte_cle"])  # le plan est dans la clé

    def test_tranche_hors_partie_refusee(self):
        with self.assertRaises(ea.EngagementInvalide):
            ea.evaluer(self.m, self.e, generation=1, unites=self.unites[:10] + ["cal-0"], essai=True)
        with self.assertRaises(ea.EngagementInvalide):  # tranche libre sans génération : refusée (K9-5)
            ea.evaluer(self.m, self.e, unites=self.unites[:10], essai=True)

    def test_ordre_derive_de_la_generation(self):
        t = self.unites[:30]
        r_1 = ea.evaluer(self.m, self.e, generation=1, unites=t, essai=True)
        r_2 = ea.evaluer(self.m, self.e, generation=2, unites=t, essai=True)
        self.assertEqual(r_1["empreinte_unites"], r_2["empreinte_unites"])  # mêmes unités…
        self.assertNotEqual(r_1["trajectoire_log_min"], r_2["trajectoire_log_min"])  # … autre ordre secret (dérivé de g)
        self.assertEqual(r_1["trajectoire_log_min"], ea.evaluer(self.m, self.e, generation=1, unites=t, essai=True)["trajectoire_log_min"])

    def test_partie_entiere_inchangee(self):
        self.assertEqual(ea.evaluer(self.m, self.e, essai=True)["empreinte_unites"],
                         ea.evaluer(self.m, self.e, generation=1, unites=self.unites, essai=True)["empreinte_unites"])

    def test_cle_tenue_par_la_course(self):
        autre = ea.construire(self.m, CONTRASTE, tau=0.10)
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["f"], 0.05, cles={"f": self.e["empreinte_cle"]})
        r = ea.evaluer(self.m, autre, essai=True)
        with self.assertRaises(ValueError):  # K9-2 : partie d'une autre clé
            c.ajouter_trajectoire("f", r["trajectoire_log_min"], unites=r["identifiants_unites"], empreinte_cle=r["empreinte_cle"])
        with self.assertRaises(ValueError):  # deux fiches, même clé
            c.entrer("g2", ["h"], 1e-6, cles={"h": self.e["empreinte_cle"]})
        r = ea.evaluer(self.m, self.e, essai=True)
        c.ajouter_trajectoire("f", r["trajectoire_log_min"], unites=r["identifiants_unites"], empreinte_cle=r["empreinte_cle"])


class LigneesEtJournal(unittest.TestCase):
    def setUp(self):
        self.m = mbs.MondeBanqueScores(banque_synthetique(random.Random(53), unites_par_partie=(100, 0, 40)), 29)
        self.e = ea.construire(self.m, CONTRASTE, tau=0.05)

    def test_relance_sous_autre_nom_refusee(self):
        lg = ea.Lignees()
        lg.entrer("f", self.e)
        lg.entrer("f", self.e)  # la même fiche peut se représenter
        with self.assertRaises(ea.EngagementInvalide):
            lg.entrer("f-bis", self.e)
        autre = ea.construire(self.m, CONTRASTE, tau=0.10)  # autre clé : autre affirmation
        lg.entrer("f-bis", autre)

    def test_journal_confronte_sans_partie(self):
        lg = ea.Lignees()
        r = ea.evaluer(self.m, self.e, fiche="f", journal=lg)  # version 28 : `evaluer` journalise lui-même
        self.assertEqual(lg.parties_calculees(None), {"f"})
        with self.assertRaises(ea.EngagementInvalide):  # seconde évaluation de f dans la même génération : refusée (K9-6)
            ea.evaluer(self.m, self.e, fiche="f", journal=lg)
        with self.assertRaises(ea.EngagementInvalide):  # journal sans fiche
            ea.evaluer(self.m, self.e, journal=lg)
        with self.assertRaises(ea.EngagementInvalide):  # K10-5 : marquer vide une partie qui ne l'est pas
            lg.marquer_vide(None, "f")
        lg.verifier_sans_partie(None, {"g": "aucune unité"})  # vraie : acceptée
        with self.assertRaises(ea.EngagementInvalide):  # artefact : la partie de f est au journal
            lg.verifier_sans_partie(None, {"f": "prétendue absence"})
        # la course confronte elle-même (K9-6) et refuse une partie absente du journal ou d'une autre empreinte
        lg2 = ea.Lignees()
        c = pa.Course(alpha=0.05, journal=lg2)
        with self.assertRaises(ValueError):  # K10-7 : entrée sans clés refusée hors essai
            c.entrer("g1", ["f", "g"], 0.05)
        c.entrer("g1", ["f", "g"], 0.05, cles={"f": self.e["empreinte_cle"], "g": self.e["empreinte_cle"] + "x"})
        with self.assertRaises(ValueError):  # aucune partie au journal
            c.ajouter_trajectoire("f", r["trajectoire_log_min"], unites=r["identifiants_unites"], empreinte_unites=r["empreinte_unites"])
        r2 = ea.evaluer(self.m, self.e, generation=1, fiche="f", journal=lg2)
        with self.assertRaises(ValueError):  # empreinte des unités ≠ journal
            c.ajouter_trajectoire("f", r2["trajectoire_log_min"], unites=r2["identifiants_unites"], empreinte_unites="autre", empreinte_cle=r2["empreinte_cle"])
        c.ajouter_trajectoire("f", r2["trajectoire_log_min"], unites=r2["identifiants_unites"], empreinte_unites=r2["empreinte_unites"], empreinte_cle=r2["empreinte_cle"])
        ea.evaluer(self.m, self.e, generation=1, fiche="g", journal=lg2)
        with self.assertRaises(ValueError):  # « sans partie » pour g, dont la partie est au journal
            c.lire(sans_partie={"g": "prétendue absence"})
        with self.assertRaises(ValueError):  # « sans partie » pour f, qui a sa partie (K9-10 c)
            c.lire(sans_partie={"f": "x", "g": "y"})

    def test_une_fiche_une_cle(self):
        lg = ea.Lignees()
        lg.entrer("f", self.e)
        with self.assertRaises(ea.EngagementInvalide):  # K9-2 : seconde affirmation pour la même fiche
            lg.entrer("f", ea.construire(self.m, CONTRASTE, tau=0.10))
        # K10-6 : même affirmation sous une autre population ou un autre plan → même affirmation, refusée pour une autre fiche
        autre_pop = ea.construire(self.m, CONTRASTE, tau=0.05, population="autre")
        self.assertNotEqual(autre_pop["empreinte_cle"], self.e["empreinte_cle"])
        self.assertEqual(autre_pop["empreinte_affirmation"], self.e["empreinte_affirmation"])
        with self.assertRaises(ea.EngagementInvalide):
            lg.entrer("espion", autre_pop)

    def test_journal_en_lecture_seule_et_generation_entiere(self):
        lg = ea.Lignees()
        r = ea.evaluer(self.m, self.e, generation=1, fiche="f", journal=lg)
        with self.assertRaises(AttributeError):  # K10-4 : le journal est un tuple pour l'appelant
            lg.journal.append({})
        self.assertEqual(lg.journal[0]["identifiants_unites"][0][1], "epreuve")
        with self.assertRaises(ea.EngagementInvalide):  # génération en chaîne refusée
            ea.evaluer(self.m, self.e, generation="2", fiche="f", journal=lg)
        # jouer_generation : décisions avant toute issue en entrée, aucune trajectoire rendue
        lg2 = ea.Lignees()
        plan = {1: sorted(self.m.unites("epreuve"))[:20], 2: sorted(self.m.unites("epreuve"))[20:]}
        e1 = ea.construire(self.m, CONTRASTE, tau=0.05, plan_tranches=plan)
        e2 = ea.construire(self.m, {"x": {"coefficients": {"noir": 1, "blanc": -1}}}, tau=0.05, plan_tranches=plan)
        lg2.entrer("f", e1); lg2.entrer("g", e2)
        c = pa.Course(alpha=0.05, journal=lg2)
        c.entrer("g1", ["f", "g"], 0.05, cles={"f": e1["empreinte_cle"], "g": e2["empreinte_cle"]})
        compte = ea.jouer_generation(c, self.m, {"f": e1, "g": e2}, non_lancees={"g": "pas cette fois"})
        self.assertEqual(compte["generation"], 1)
        self.assertIn("f", compte["parties"]); self.assertNotIn("g", compte["parties"])
        self.assertNotIn("trajectoire_log_min", str(compte))
        self.assertEqual(c.generation, 2)
        compte2 = ea.jouer_generation(c, self.m, {"f": e1, "g": e2}, abandons_avant={"g": "retiré avant toute issue"})
        self.assertIn("g", compte2["abandons_avant"])
        with self.assertRaises(ea.EngagementInvalide):  # non-lancement d'une fiche non active
            ea.jouer_generation(c, self.m, {"f": e1, "g": e2}, non_lancees={"g": "x"})

    def test_version_30_gardes(self):
        # K11-3 : trajectoire fabriquée, clé déclarée autre, fiche fantôme, unités journalisées non ajoutées, abandon avant partie
        # alors que la partie est au journal ; K11-1 : abandon « après partie » appliqué après toutes les parties ; K11-4 : interruption tracée
        plan = {1: sorted(self.m.unites("epreuve"))[:20], 2: sorted(self.m.unites("epreuve"))[20:]}
        e1 = ea.construire(self.m, CONTRASTE, tau=0.05, plan_tranches=plan)
        e2 = ea.construire(self.m, {"x": {"coefficients": {"noir": 1, "blanc": -1}}}, tau=0.05, plan_tranches=plan)
        lg = ea.Lignees(); lg.entrer("f", e1); lg.entrer("g", e2)
        c = pa.Course(alpha=0.05, journal=lg)
        c.entrer("g1", ["f", "g"], 0.05, cles={"f": e1["empreinte_cle"], "g": e2["empreinte_cle"]})
        with self.assertRaises(ea.EngagementInvalide):  # évaluation sans journal hors essai : refusée
            ea.evaluer(self.m, e1, generation=1)
        r = ea.evaluer(self.m, e1, generation=1, fiche="f", journal=lg)
        with self.assertRaises(ValueError):  # trajectoire fabriquée
            c.ajouter_trajectoire("f", [5.0] * len(r["trajectoire_log_min"]), unites=r["identifiants_unites"], empreinte_cle=r["empreinte_cle"], empreinte_unites=r["empreinte_unites"])
        with self.assertRaises(ValueError):  # abandon « avant partie » alors que la partie est au journal
            c.abandonner("f", avant_partie=True, motif="x")
        c.ajouter_trajectoire("f", r["trajectoire_log_min"], unites=r["identifiants_unites"], empreinte_cle=r["empreinte_cle"], empreinte_unites=r["empreinte_unites"])
        ea.evaluer(self.m, e2, generation=1, fiche="g", journal=lg)  # calculée, non ajoutée
        ea.evaluer(self.m, e2, generation=1, fiche="fantome", journal=lg)
        with self.assertRaises(ValueError):  # fiche fantôme au journal
            c.lire(sans_partie={"g": "x"})
        lg2 = ea.Lignees(); lg2.entrer("f", e1); lg2.entrer("g", e2)
        c2 = pa.Course(alpha=0.05, journal=lg2)
        c2.entrer("g1", ["f", "g"], 0.05, cles={"f": e1["empreinte_cle"], "g": e2["empreinte_cle"]})
        rf = ea.evaluer(self.m, e1, generation=1, fiche="f", journal=lg2)
        c2.ajouter_trajectoire("f", rf["trajectoire_log_min"], unites=rf["identifiants_unites"], empreinte_cle=rf["empreinte_cle"], empreinte_unites=rf["empreinte_unites"])
        ea.evaluer(self.m, e2, generation=1, fiche="g", journal=lg2)  # calculée, non ajoutée
        with self.assertRaises(ValueError):  # « sans partie » pour g alors que g est calculée (K9-6)
            c2.lire(sans_partie={"g": "x"})
        # K11-3 : une partie journalisée pour une fiche promue ou gelée (non ajoutable) marque quand même ses unités comme lues
        c2.retirer("g", "panne")
        c2.lire()
        self.assertTrue(all(tuple(u) in c2.premiere_lecture or u in c2.premiere_lecture for u in lg2.journal[1]["identifiants_unites"]))
        # abandon après partie : la règle ne voit les issues qu'après toutes les parties ; interruption tracée
        lg3 = ea.Lignees(); lg3.entrer("f", e1); lg3.entrer("g", e2)
        c3 = pa.Course(alpha=0.05, journal=lg3)
        c3.entrer("g1", ["f", "g"], 0.05, cles={"f": e1["empreinte_cle"], "g": e2["empreinte_cle"]})
        vus = []
        compte = ea.jouer_generation(c3, self.m, {"f": e1, "g": e2}, abandon_apres=lambda f, v: (vus.append(f) or None))
        self.assertEqual(len(lg3.journal), 2)  # les deux parties calculées avant que la règle ne voie quoi que ce soit
        self.assertEqual(compte["interruptions"], [])
        lg4 = ea.Lignees(); lg4.entrer("f", e1); lg4.entrer("g", e2)
        c4 = pa.Course(alpha=0.05, journal=lg4)
        c4.entrer("g1", ["f", "g"], 0.05, cles={"f": e1["empreinte_cle"], "g": e2["empreinte_cle"]})
        with self.assertRaises(ea.EngagementInvalide):  # engagement manquant → interruption tracée
            ea.jouer_generation(c4, self.m, {"f": e1})
        self.assertEqual(len(lg4.interruptions(1)), 1)

    def test_ordre_derive_de_la_cle(self):
        # K10-3 : même clé, autre nom ou autre budget → même ordre secret, même trajectoire
        t = sorted(self.m.unites("epreuve"))[:30]
        e_a = ea.construire(self.m, {"a": {"coefficients": {"blanc": 1, "noir": -1}}}, tau=0.05, alpha_c=0.05)
        e_b = ea.construire(self.m, {"autre": {"coefficients": {"noir": -1, "blanc": 1}}}, tau=0.05, alpha_c=0.01, m_c=3)
        self.assertNotEqual(e_a["empreinte"], e_b["empreinte"])
        self.assertEqual(ea.evaluer(self.m, e_a, generation=1, unites=t, essai=True)["trajectoire_log_min"],
                         ea.evaluer(self.m, e_b, generation=1, unites=t, essai=True)["trajectoire_log_min"])


class Demonstration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = charger_demo()
        rng = random.Random(cls.demo.graine_derivee(20261028, "banque"))
        cls.b = cls.demo.banque(rng, 3, 30)
        cls.monde = mbs.MondeBanqueScores(cls.b, 7)

    def test_banque(self):
        d = self.monde.description_publique()
        self.assertEqual(sorted(self.b["cellules"]), sorted(self.demo.CELLULES))
        self.assertEqual(self.monde.identite, self.b["identite"])
        self.assertEqual(len(self.monde.unites("epreuve")), 90)
        self.assertEqual(self.demo.unites_de_tranche(self.monde, 1)[:1], ["epr-1-0"])
        self.assertEqual(len(self.demo.unites_de_tranche(self.monde, 2)), 30)
        self.assertEqual(d["effectifs"]["calibrage"]["sabote"], 0)

    def test_esperance_connue(self):
        self.assertGreater(self.demo.esperance_connue({"blanc": 1, "juge": -1}), 0)
        self.assertEqual(self.demo.esperance_connue({"blanc": 1, "blanc_jumeau": -1}), 0)
        self.assertLess(self.demo.esperance_connue({"juge": 1, "blanc": -1}), 0)
        # K9-7 : l'espérance conditionnelle aux seuils scellés diffère de zéro pour les jumeaux dès que les seuils diffèrent
        self.assertAlmostEqual(self.demo.esperance_conditionnelle({"blanc": 1, "blanc_jumeau": -1}, {"blanc": 1.0, "blanc_jumeau": 1.0}), 0.0)
        self.assertGreater(self.demo.esperance_conditionnelle({"blanc": 1, "blanc_jumeau": -1}, {"blanc": 1.0, "blanc_jumeau": 1.2}), 0.0)
        self.assertAlmostEqual(self.demo.esperance_conditionnelle({"blanc": 1, "juge": -1}, {"blanc": 1.0, "juge": 1.0}, nul=True), 0.0)

    def test_course_et_lecture(self):
        etat = self.demo.course(self.monde, 3, 0.05, 0.05, 11, n_hasard=3)
        lec = self.demo.lecture(etat)
        self.assertTrue(lec["L1_validite"]["tenue"], lec["L1_validite"])
        self.assertIn("lecture", lec["controle_12_calibrage"])
        self.assertTrue(lec["L2_dents"]["temoin-vrai-fort"]["promue"])
        self.assertFalse(lec["L2_dents"]["temoin-vrai-tenu"]["promue"])  # écart 0,1 : hors de portée à 90 unités
        self.assertEqual(len(etat["journal"]), 3)
        self.assertAlmostEqual(etat["alpha_engage"], 0.05)
        # génération 1 : la fiche stratifiée « concentré » n'a aucune unité (tranche 1 toute « diffus ») → déclarée
        self.assertIn("temoin-vrai-concentre", etat["journal"][0]["sans_partie"])
        self.assertNotIn("temoin-vrai-concentre", etat["journal"][0]["parties"])
        # génération 2 : abandon avant partie du témoin inversé, tracé par la course
        self.assertIn(("temoin-faux-inverse", "avant_partie"), [tuple(a) for a in etat["journal"][1]["abandons"]])
        self.assertEqual(etat["abandons"]["temoin-faux-inverse"][1], "avant_partie")
        # le journal des parties contient les parties calculées ; une partie vide y est marquée vide (K10-5), jamais effacée
        for j in etat["journal_parties"]:
            self.assertEqual(j["unites"] == 0, bool(j.get("vide")))
        self.assertTrue(any(j.get("vide") for j in etat["journal_parties"]))
        # L3 : la fiche de forme G1 est rapportée avec sa sortie e-Bonferroni et des richesses descriptives
        self.assertIn("sortie_e_bonferroni", lec["L3_forme_G1"])
        self.assertEqual(sorted(lec["L3_forme_G1"]["parties"][0]["contrastes"]), sorted(self.demo.COMPARATEURS_G1))
        self.assertTrue(all(p["processus_minimal"] for p in lec["L3_forme_G1"]["parties"]))  # K10-8 : le processus qui fixe l'e-valeur est dit
        # K9-3 : autant d'affirmations distinctes que de fiches entrées (les redites sont refusées)
        self.assertEqual(lec["fiches"], lec["affirmations_distinctes"])
        # le journal des parties est tenu par `evaluer` : une entrée par (fiche, génération) ajoutée
        for g in etat["journal"]:
            for n in g["parties"]:
                self.assertEqual(sum(1 for j in etat["journal_parties"] if j["generation"] == g["generation"] and j["fiche"] == n), 1)

    def test_artefacts(self):
        a = self.demo.artefacts(self.monde, 0.05, 0.05, 11)
        for nom in ("relecture_tranche", "tranche_anterieure_par_autre_fiche", "sans_partie_mensonger", "relance_sous_autre_nom",
                    "partie_d_une_autre_cle", "fiche_espionne_autre_population", "course_sans_journal"):
            self.assertTrue(a[nom].startswith("refus"), (nom, a[nom]))

    def test_nul_repete(self):
        class Args:
            nul, generations, unites_par_tranche, graine, alpha, tau = 8, 2, 20, 20261028, 0.05, 0.05
        n = self.demo.repetitions_nulles(Args)
        self.assertEqual(n["repetitions"], 8)
        self.assertLessEqual(n["au_moins_une_promotion"], 2)
        self.assertLessEqual(n["au_moins_une_bonferroni"], n["au_moins_une_promotion"])  # K9-10 d : Bonferroni ⊂ e-BH
        self.assertEqual(len(n["wilson_95"]), 2)


if __name__ == "__main__":
    unittest.main()
