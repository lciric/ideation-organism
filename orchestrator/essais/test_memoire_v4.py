"""Essais de la version 0.4.0 : mémoire prédictive (signature brute, classes, héritage de la preuve) en sélection par pari.
Gardes essayées sur un cas sain et sur des artefacts (R5)."""

import math
import random
import unittest

from essais.aides import fiche
from essais.test_cycle import CasGeneration
from pole import selection_pari as sp
from pole.cycle import Budget, ConfigGeneration, Generation
from pole.fiche import RegistreGel
from pole.memoire import Memoire
from pole.recombinaison import tirage_marchepieds, tirage_stratifie
from pole.simulation import AdaptateurSimule, MondeSimule

VRAIE = "La loi engagée prédit les issues des instances d'essai"


def fiche_pari(identifiant, loi, enonce=VRAIE, **modifs):
    return fiche(identifiant, enonce=enonce, loi_predictive=loi, severite_attendue=0.05, seuil=20.0,
                 espace_instances={"nombre_issues": 3, "dimension": 2}, **modifs)


def issue_testee(log_finale, statut="eliminee"):
    return {"verdict_final": statut, "pari": {"log_richesse_finale": log_finale, "log_richesse_max": max(0.0, log_finale)}}


class SignatureEtClasses(unittest.TestCase):
    def lois(self, n=3, graine=4):
        rng = random.Random(graine)
        return [sp.loi_softmax_aleatoire(rng, force=1.5) for _ in range(n)]

    def test_meme_loi_meme_classe_autre_loi_autre_classe(self):
        a, b, _ = self.lois()
        m = Memoire(graine=1)
        f1 = fiche_pari("F1", a)
        f1.statut = "eliminee"
        m.indexer(f1, issue_testee(-4.0), 0)
        self.assertEqual(m.chercher_classe(fiche_pari("F2", a))[0], "F1")
        self.assertEqual(m.chercher_classe(fiche_pari("F2", a))[1], 0.0)
        self.assertIsNone(m.chercher_classe(fiche_pari("F3", b))[0])
        self.assertTrue(math.isinf(Memoire.divergence_moyenne(None, m.signature(f1))))

    def test_heritage_une_epreuve_par_generation_et_survivante_refusee(self):
        a, b, _ = self.lois()
        m = Memoire(graine=1)
        f1 = fiche_pari("F1", a)
        f1.statut = "eliminee"
        m.indexer(f1, issue_testee(-4.0), 0)
        m.nouvelle_generation()
        g2 = m.garde_redite(fiche_pari("F2", a))
        self.assertTrue(g2["accepte"], g2["motif"])
        self.assertEqual(m.heritage("F2"), {"classe": "F1", "cumul": -4.0, "epreuves": 1})
        self.assertFalse(m.garde_redite(fiche_pari("F3", a))["accepte"], "une épreuve par classe et par génération")
        f2 = fiche_pari("F2", a)
        f2.statut = "eliminee"
        m.indexer(f2, issue_testee(-1.5), 1)
        self.assertEqual(m.classes["F1"]["cumul"], -5.5)
        self.assertEqual(m.classes["F1"]["epreuves"], 2)
        m.nouvelle_generation()
        self.assertTrue(m.garde_redite(fiche_pari("F4", a))["accepte"])
        fb = fiche_pari("B1", b)
        fb.statut = "survit"
        m.indexer(fb, issue_testee(6.0, "survit"), 1)
        m.nouvelle_generation()
        refus = m.garde_redite(fiche_pari("B2", b))
        self.assertFalse(refus["accepte"])
        self.assertIn("survivante", refus["motif"])

    def test_politiques_refus_et_rien(self):
        a, _, _ = self.lois()
        for politique, accepte in (("refus", False), ("rien", True)):
            m = Memoire(graine=1, politique_redite=politique)
            f1 = fiche_pari("F1", a)
            f1.statut = "eliminee"
            m.indexer(f1, issue_testee(-4.0), 0)
            m.nouvelle_generation()
            self.assertEqual(m.garde_redite(fiche_pari("F2", a))["accepte"], accepte, politique)
            self.assertIsNone(m.heritage("F2"))
        with self.assertRaises(ValueError):
            Memoire(politique_redite="oubli")

    def test_temoins_hors_des_classes_et_fiches_sans_loi_par_le_texte(self):
        a, _, _ = self.lois()
        m = Memoire(graine=1)
        t = fiche_pari("T1", a, temoin="vraie")
        t.statut = "survit"
        m.indexer(t, issue_testee(5.0, "survit"), 0)
        self.assertEqual(m.classes, {})
        sans_loi = fiche("S1", enonce="Une hypothèse sans loi engagée")
        self.assertEqual(m.garde_redite(sans_loi)["motif"], "aucune éliminée proche")


class HeritageDansLeCycle(CasGeneration):
    def test_preuve_heritee_appliquee_a_la_promotion(self):
        rng = random.Random(8)
        loi = sp.loi_softmax_aleatoire(rng, force=2.0)
        for cumul, attendu in ((-200.0, "eliminee"), (0.0, "survit")):
            m = Memoire(graine=3)
            ancienne = fiche_pari("A0", loi)
            ancienne.statut = "eliminee"
            m.indexer(ancienne, issue_testee(cumul), 0)
            m.nouvelle_generation()
            redite = fiche_pari("R1", loi)
            self.assertTrue(m.garde_redite(redite)["accepte"])
            adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}))
            g = Generation(1, adaptateur, ConfigGeneration(selection="pari", taille_plan=80), self.sous_dossier(f"c{cumul}"),
                           RegistreGel(), Budget(10), memoire=m)
            r = g.executer([redite])
            ev = r["issues"]["R1"]["pari"]
            self.assertEqual(redite.statut, attendu, r["issues"]["R1"]["motif"])
            self.assertEqual(ev["heritage"]["cumul"], cumul)
            self.assertTrue(ev["heritage"]["promue_sans_heritage"])
            self.assertEqual(ev["promue"], cumul + ev["log_richesse_max"] >= ev["seuil_log"])


class Marchepieds(unittest.TestCase):
    def survivante(self, identifiant, domaine, parents=()):
        plus = {"ce_que_la_fille_predit_de_plus": "un effet joint"} if parents else {}
        f = fiche(identifiant, enonce=f"Énoncé {identifiant} sur {domaine}", domaines=[domaine], operateurs=["projection"],
                  contraintes=[], parents=list(parents), **plus)
        f.statut = "survit"
        return f

    def test_sans_fille_survivante_le_tirage_est_le_stratifie(self):
        fiches = [self.survivante(f"{d}{i}", d) for d in ("alpha", "beta", "gamma") for i in range(2)]
        a, _, m = tirage_marchepieds(fiches, set(), 4, random.Random(5))
        b, _ = tirage_stratifie(fiches, set(), 4, random.Random(5))
        self.assertEqual([p[2] for p in a], [p[2] for p in b])
        self.assertEqual(m, [])

    def test_les_filles_survivantes_servent_d_abord_par_preuve(self):
        fiches = [self.survivante(f"{d}{i}", d) for d in ("alpha", "beta") for i in range(2)]
        f1 = self.survivante("F1", "alpha", parents=["alpha0", "beta0"])
        f2 = self.survivante("F2", "beta", parents=["alpha1", "beta1"])
        preuves = {"F1": 3.0, "F2": 9.0}
        paires, _, marchepieds = tirage_marchepieds(fiches + [f1, f2], set(), 4, random.Random(2), preuves.get)
        self.assertEqual(len(marchepieds), 2)
        self.assertIn("F2", marchepieds[0], "la fille à la plus forte preuve d'abord")
        self.assertIn("F1", marchepieds[1])
        self.assertEqual(len(paires), 4)
        self.assertEqual(len({p[2] for p in paires}), 4)


if __name__ == "__main__":
    unittest.main()
