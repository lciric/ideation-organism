"""Essais de la version 0.3.0 : juge v1 (ordre d'exécution secret imposé par le noyau, urne) et nul des filles v2 dans
le cycle du pôle, en sélection par pari (gardes essayées sur un cas sain et sur des artefacts, R5)."""

import json
import os
import random
import unittest

from essais.aides import fiche
from essais.test_cycle import FAUSSE, VRAIE, CasGeneration
from pole import selection_pari as sp
from pole.cycle import Budget, ConfigGeneration, Generation, instants_reguliers, preparer_engagement
from pole.fiche import RegistreGel
from pole.recombinaison import tirage_stratifie
from pole.simulation import AdaptateurSimule, MondeSimule, executer_python

FILLE_TRIVIALE = "Le parent A corrigé par les taux de base observés prédit les mesures d'essai"


class AdaptateurOrdreTriche(AdaptateurSimule):
    """Artefact : l'expérimentateur déclare l'ordre naturel au lieu de l'ordre imposé, ou recopie une empreinte d'ordre
    fausse ; le code rejoué redonne la même déclaration (le vérificateur confirme) : seul le noyau peut refuser."""

    def __init__(self, triche, **reglages):
        super().__init__(**reglages)
        self.triche = triche

    def _experimentateur_pari(self, dossier, fiche_d, empreinte, profil, tag):
        texte, statut = super()._experimentateur_pari(dossier, fiche_d, empreinte, profil, tag)
        chemin = os.path.join(dossier, "mesures.json")
        with open(chemin, encoding="utf-8") as f:
            mesures = json.load(f)
        if self.triche == "ordre_naturel":
            mesures["plan_execution"] = "ordre_naturel"
            mesures.pop("empreinte_ordre", None)
        else:
            mesures["empreinte_ordre"] = "0" * 64
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(mesures, f)
        executer_python(dossier, "experience.py")
        return texte, statut


class JugeV1DansLeCycle(CasGeneration):
    def fiche_pari(self, identifiant, enonce, loi, **modifs):
        return fiche(identifiant, enonce=enonce, loi_predictive=loi, severite_attendue=0.05, seuil=20.0,
                     espace_instances={"nombre_issues": 3, "dimension": 2}, **modifs)

    def lois(self):
        rng = random.Random(8)
        return sp.loi_softmax_aleatoire(rng, force=2.0), sp.loi_softmax_aleatoire(rng, force=2.0)

    def test_ordre_secret_impose_puis_recalcule(self):
        a, b = self.lois()
        v, f = self.fiche_pari("V1", VRAIE, a), self.fiche_pari("F1", FAUSSE, b)
        self.registre, self.budget = RegistreGel(), Budget(20)
        g = Generation(0, self.adaptateur(), ConfigGeneration(selection="pari", taille_plan=80, taille_plan_filles=80), self.tmp, self.registre,
                       self.budget)
        r = g.executer([v, f])
        self.assertEqual((v.statut, f.statut), ("survit", "eliminee"))
        dossier = os.path.join(self.tmp, "archive", "generations", "generation-00", "V1", "experience")
        with open(os.path.join(dossier, "ordre-execution.json"), encoding="utf-8") as fo:
            fichier = json.load(fo)
        gele = g.engagements["V1"]
        self.assertEqual(fichier["ordre"], sp.ordre_execution(g.graine_noyau, gele.empreinte, 80))
        self.assertEqual(r["issues"]["V1"]["pari"]["plan_execution"], "ordre_secret")
        self.assertIn("urne", [m["nom"] for m in gele.engagement["bibliotheque"]])
        with open(os.path.join(os.path.dirname(dossier), "traces-experience", "consigne.txt"), encoding="utf-8") as fc:
            self.assertIn("ordre-execution.json", fc.read())
        for nom in os.listdir(dossier):  # la graine du noyau n'est écrite nulle part dans le dossier de l'agent
            with open(os.path.join(dossier, nom), "rb") as fb:
                self.assertNotIn(str(g.graine_noyau).encode(), fb.read())

    def test_ordre_ignore_ou_empreinte_fausse_rejetes_par_le_noyau(self):
        a, _ = self.lois()
        for triche in ("ordre_naturel", "empreinte_fausse"):
            v = self.fiche_pari("V1", VRAIE, a)
            adaptateur = AdaptateurOrdreTriche(triche, graine=3, monde=MondeSimule(3, {VRAIE: True}))
            self.registre = RegistreGel()
            r = self.generation([v], adaptateur, selection="pari", taille_plan=80)
            self.assertEqual(v.statut, "rejetee (test change)", (triche, r["issues"]["V1"].get("motif")))
            self.assertIn("PlanExecutionNonConforme", r["issues"]["V1"]["motif"])
            self.tmp = self.sous_dossier(f"suite-{triche}")

    def test_juge_v0_garde_l_ordre_naturel(self):
        a, _ = self.lois()
        v = self.fiche_pari("V1", VRAIE, a)
        self.registre = RegistreGel()
        r = self.generation([v], self.adaptateur(), selection="pari", taille_plan=80, juge="v0", nul_filles="v0")
        dossier = os.path.join(self.tmp, "archive", "generations", "generation-00", "V1", "experience")
        self.assertFalse(os.path.exists(os.path.join(dossier, "ordre-execution.json")))
        self.assertEqual(r["issues"]["V1"]["pari"]["plan_execution"], "ordre_naturel")

    def test_engagement_d_une_fille_sous_le_nul_v2(self):
        a, b = self.lois()
        fille = self.fiche_pari("C1", VRAIE, a, parents=["PA", "PB"], ce_que_la_fille_predit_de_plus="x")
        cfg = ConfigGeneration(selection="pari", taille_plan=80, taille_plan_filles=80)
        e = preparer_engagement(fille, cfg, {"PA": a, "PB": b}).engagement
        self.assertEqual(e["instants_lecture"], instants_reguliers(80, 8))
        self.assertEqual(e["instants_lecture"][-1], 80)
        noms = [m["nom"] for m in e["bibliotheque"]]
        for attendu in ("urne", "ajuste_lineaire", "ajuste_log:PA", "ajuste_log:PB", "ajuste_log:PAPB"):
            self.assertIn(attendu, noms)
        self.assertEqual(e["plan_execution"], "ordre_secret")
        e0 = preparer_engagement(fille, ConfigGeneration(selection="pari", taille_plan=80, taille_plan_filles=80, nul_filles="v0"),
                                 {"PA": a, "PB": b}).engagement
        self.assertNotIn("instants_lecture", e0)
        self.assertNotIn("ajuste_lineaire", [m["nom"] for m in e0["bibliotheque"]])
        souple = preparer_engagement(fille, ConfigGeneration(selection="pari", taille_plan=80, taille_plan_filles=80, nul_filles="v2_souple"),
                                     {"PA": a, "PB": b}).engagement
        self.assertNotIn("ajuste_log:PAPB", [m["nom"] for m in souple["bibliotheque"]])

    def test_configuration_refusee(self):
        with self.assertRaises(ValueError):
            ConfigGeneration(juge="v0", nul_filles="v2").valider()
        with self.assertRaises(ValueError):
            ConfigGeneration(juge="v2").valider()
        with self.assertRaises(ValueError):
            ConfigGeneration(nul_filles="v3").valider()
        ConfigGeneration(juge="v0", nul_filles="v0").valider()

    def test_fille_parent_plus_loi_aveugle_eliminee_sous_le_nul_v2(self):
        """Le trou du nul de v0 : fille = parent A mélangé à une loi aveugle, et le monde suit exactement cette fille."""
        a, b = self.lois()
        loi = {"type": "melange", "composantes": [a, {"type": "fixe", "probas": [0.7, 0.2, 0.1]}], "poids": [0.5, 0.5]}
        fille = self.fiche_pari("C1", FILLE_TRIVIALE, loi, parents=["PA", "PB"], ce_que_la_fille_predit_de_plus="x")
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {FILLE_TRIVIALE: True}))
        g = Generation(0, adaptateur, ConfigGeneration(selection="pari", taille_plan=80, taille_plan_filles=80), self.tmp, RegistreGel(),
                       Budget(10), lois_connues={"PA": a, "PB": b})
        r = g.executer([fille])
        self.assertEqual(fille.statut, "eliminee", r["issues"]["C1"].get("motif"))
        self.assertLessEqual(r["issues"]["C1"]["pari"]["log_richesse_max"], 1e-6)


class RecombinaisonStratifiee(unittest.TestCase):
    """R-527 : tirage stratifié par paire de domaines estimés, abstention ; le noyau corrigé reste disponible."""

    def survivante(self, identifiant, domaine, operateurs=("projection",), contraintes=()):
        f = fiche(identifiant, enonce=f"Énoncé {identifiant} sur {domaine}", domaines=[domaine], operateurs=list(operateurs),
                  contraintes=list(contraintes))
        f.statut = "survit"
        return f

    def test_tour_des_strates_avant_toute_repetition(self):
        fiches = [self.survivante(f"{d}{i}", d) for d in ("alpha", "beta", "gamma") for i in range(3)]
        paires, ecartees = tirage_stratifie(fiches, set(), 6, random.Random(1))
        strates = [tuple(sorted((a.domaines[0], b.domaines[0]))) for _, _, _, a, b, _ in paires]
        self.assertEqual(len(set(strates)), 6, "six strates distinctes (trois intra, trois inter) avant toute répétition")
        self.assertEqual(ecartees, [])

    def test_abstention_sans_paire_valide(self):
        a = self.survivante("A", "alpha", ("projection",), ("linéaire",))
        b = self.survivante("B", "beta", ("seuillage",))
        c = self.survivante("C", "gamma", ("projection",), ("non linéaire",))
        paires, ecartees = tirage_stratifie([a, b, c], set(), 3, random.Random(1))
        self.assertEqual(paires, [])
        self.assertEqual(len(ecartees), 3)

    def test_deja_fusionnees_ecartees_et_configuration(self):
        a, b = self.survivante("A", "alpha"), self.survivante("B", "beta")
        paires, ecartees = tirage_stratifie([a, b], {("A", "B")}, 3, random.Random(1))
        self.assertEqual(paires, [])
        self.assertTrue(ecartees[0]["deja_fusionnee"])
        self.assertEqual(ConfigGeneration().tirage_recombinaison, "stratifie")
        with self.assertRaises(ValueError):
            ConfigGeneration(tirage_recombinaison="dpp").valider()


if __name__ == "__main__":
    unittest.main()
