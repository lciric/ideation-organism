"""Essais de la version 0.6.0, pièce 1 : monde tenu par le noyau (option (a) du premier lancement réel).

Cas sain : issues déposées après le gel dans `mesures.json`, rangées par l'agent, promues (fiche vraie) ou éliminées
(fiche fausse) ; le monde lui-même (table des vérités) n'apparaît dans aucun dossier d'agent. Artefacts (R5) : un agent qui
déclare d'autres issues que celles déposées est rejeté avant le vérificateur ; un agent qui change l'engagement est
rejeté ; le monde du noyau refuse la sélection par seuil ; les mesures sont reproductibles à graines égales et changent
avec la graine secrète du noyau.
"""

import json
import os
import random
import unittest

from essais.aides import fiche
from essais.test_cycle import CasGeneration
from pole import selection_pari as sp
from pole.cycle import Budget, ConfigGeneration, Generation
from pole.fiche import RegistreGel
from pole.monde_noyau import MondeNoyau, charger_monde_noyau, issues_conformes
from pole.simulation import AdaptateurSimule, MondeSimule

VRAIE = "La loi engagée prédit les issues des instances d'essai"
FAUSSE = "La loi engagée ne prédit rien : le monde suit la marginale aveugle"


def fiche_pari(identifiant, loi, enonce=VRAIE):
    return fiche(identifiant, enonce=enonce, loi_predictive=loi, severite_attendue=0.05, seuil=20.0,
                 espace_instances={"nombre_issues": 3, "dimension": 2})


def _fichiers(dossier):
    for racine, _, noms in os.walk(dossier):
        for nom in noms:
            yield os.path.join(racine, nom)


class MondeDuNoyau(CasGeneration):
    def setUp(self):
        super().setUp()
        self.loi = sp.loi_softmax_aleatoire(random.Random(8), force=2.0)
        self.monde = MondeNoyau(7, {VRAIE: True, FAUSSE: False})
        self.cfg = ConfigGeneration(selection="pari", taille_plan=120, taille_plan_filles=120)

    def _generation(self, adaptateur, dossier=None, cfg=None):
        return Generation(0, adaptateur, cfg or self.cfg, dossier or self.tmp, RegistreGel(), Budget(10),
                          monde_noyau=self.monde)

    def test_cas_sain_vraie_promue_fausse_eliminee_sans_monde_dans_les_dossiers(self):
        # L'adaptateur simulé reçoit un monde contraire : s'il mesurait lui-même, la vraie serait éliminée et la fausse
        # promue ; sous le monde du noyau, il range les issues déposées, et les verdicts suivent le monde du noyau.
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: False, FAUSSE: True}))
        v, x = fiche_pari("V1", self.loi), fiche_pari("X1", self.loi, enonce=FAUSSE)
        g = self._generation(adaptateur)
        r = g.executer([v, x])
        self.assertEqual(v.statut, "survit", r["issues"]["V1"].get("motif"))
        self.assertEqual(x.statut, "eliminee", r["issues"]["X1"].get("motif"))
        for identifiant in ("V1", "X1"):
            dossier = os.path.join(self.tmp, "archive", "generations", "generation-00", identifiant, "experience")
            with open(os.path.join(dossier, "mesures.json"), encoding="utf-8") as f:
                deposees = json.load(f)
            with open(os.path.join(dossier, "tirages.json"), encoding="utf-8") as f:
                declarees = json.load(f)
            self.assertEqual(deposees["issues"], declarees["issues"])
            self.assertEqual(deposees, g.mesures_noyau[identifiant])
            self.assertEqual(deposees["plan_execution"], "ordre_secret")
            self.assertTrue(r["issues"][identifiant]["mesures_du_noyau"]["conformes"])
            for chemin in _fichiers(os.path.join(self.tmp, "archive", "generations", "generation-00", identifiant)):
                with open(chemin, "rb") as fb:
                    self.assertNotIn(b"verites", fb.read(), chemin)
        self.assertIn("vérifie que `mesures.json` est lié", adaptateur.appels[0]["consigne"])

    def test_artefact_issues_declarees_differentes_rejetees_avant_le_verificateur(self):
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}), profils={"V1": "sans_calcul"})
        v = fiche_pari("V1", self.loi)
        r = self._generation(adaptateur).executer([v])
        self.assertEqual(v.statut, "rejetee (test change)")
        self.assertIn("issues déclarées différentes", r["issues"]["V1"]["motif"])
        self.assertEqual([a["role"] for a in adaptateur.appels], ["experimentateur"], "aucun vérificateur appelé")

    def test_artefact_engagement_change_rejete(self):
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}), profils={"V1": "change_test"})
        v = fiche_pari("V1", self.loi)
        r = self._generation(adaptateur).executer([v])
        self.assertEqual(v.statut, "rejetee (test change)", r["issues"]["V1"].get("motif"))

    def test_artefact_mesures_reecrites_par_l_agent_rejetees(self):
        class AgentQuiReecrit(AdaptateurSimule):
            def _experimentateur_pari(self, dossier, fiche_, empreinte, profil, tag):
                chemin = os.path.join(dossier, "mesures.json")
                with open(chemin, encoding="utf-8") as f:
                    mesures = json.load(f)
                mesures["issues"] = [0] * len(mesures["issues"])
                with open(chemin, "w", encoding="utf-8") as f:
                    json.dump(mesures, f)
                return super()._experimentateur_pari(dossier, fiche_, empreinte, profil, tag)

        adaptateur = AgentQuiReecrit(graine=3, monde=MondeSimule(3, {VRAIE: True}))
        v = fiche_pari("V1", self.loi)
        r = self._generation(adaptateur).executer([v])
        self.assertEqual(v.statut, "rejetee (test change)")
        self.assertIn("monde du noyau", r["issues"]["V1"]["motif"])

    def test_refus_de_la_selection_par_seuil(self):
        with self.assertRaises(ValueError):
            Generation(0, AdaptateurSimule(graine=3), ConfigGeneration(selection="seuil"), self.tmp, RegistreGel(),
                       Budget(10), monde_noyau=self.monde)

    def test_mesures_reproductibles_et_liees_a_la_graine_du_noyau(self):
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}))
        a = self._generation(adaptateur, self.sous_dossier("a"))
        a.executer([fiche_pari("V1", self.loi)])
        b = self._generation(adaptateur, self.sous_dossier("b"))
        b.executer([fiche_pari("V1", self.loi)])
        self.assertEqual(a.mesures_noyau["V1"], b.mesures_noyau["V1"], "mêmes graines : mêmes issues")
        secret = ConfigGeneration(selection="pari", taille_plan=120, taille_plan_filles=120, noyau_secret=True)
        c = self._generation(adaptateur, self.sous_dossier("c"), secret)
        c.executer([fiche_pari("V1", self.loi)])
        self.assertNotEqual(a.mesures_noyau["V1"]["issues"], c.mesures_noyau["V1"]["issues"],
                            "graine secrète : les issues ne sont plus celles de la graine du pôle")
        for chemin in _fichiers(os.path.join(self.sous_dossier("c"), "archive")):
            with open(chemin, "rb") as fb:
                self.assertNotIn(str(c.graine_noyau).encode(), fb.read(), chemin)


class RejeuSansTirageNeuf(CasGeneration):
    """Faille C4 de la contre-lecture d'aptitude : une fiche rejouée ne doit pas recevoir un tirage neuf."""

    def _generation(self, numero, adaptateur, depots, monde):
        cfg = ConfigGeneration(selection="pari", taille_plan=120, taille_plan_filles=120, noyau_secret=True)
        return Generation(numero, adaptateur, cfg, self.tmp, RegistreGel(), Budget(10), monde_noyau=monde, depots=depots)

    def _lire(self, numero, nom):
        with open(os.path.join(self.tmp, "archive", "generations", f"generation-{numero:02d}", "V1", "experience", nom),
                  encoding="utf-8") as f:
            return json.load(f)

    def test_cas_sain_rejeu_meme_ordre_memes_issues_meme_verdict(self):
        loi = sp.loi_softmax_aleatoire(random.Random(8), force=2.0)
        monde = MondeNoyau(7, {VRAIE: True})
        v = fiche_pari("V1", loi)
        depots = {}
        en_panne = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}), p_echec=1.0)
        g0 = self._generation(0, en_panne, depots, monde)
        r0 = g0.executer([v])
        self.assertEqual(v.statut, "indecise", r0["issues"]["V1"].get("motif"))
        sain = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}))
        g1 = self._generation(1, sain, depots, monde)
        self.assertNotEqual(g0.graine_noyau, g1.graine_noyau, "graines secrètes neuves par génération")
        r1 = g1.executer([v])
        self.assertEqual(v.statut, "survit", r1["issues"]["V1"].get("motif"))
        self.assertEqual(self._lire(0, "ordre-execution.json"), self._lire(1, "ordre-execution.json"), "même ordre")
        self.assertEqual(self._lire(0, "mesures.json"), self._lire(1, "mesures.json"), "mêmes issues")
        self.assertEqual(len(depots), 1)

    def test_artefact_sans_depot_partage_le_rejeu_tirerait_a_neuf(self):
        loi = sp.loi_softmax_aleatoire(random.Random(8), force=2.0)
        monde = MondeNoyau(7, {VRAIE: True})
        v = fiche_pari("V1", loi)
        en_panne = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}), p_echec=1.0)
        self._generation(0, en_panne, {}, monde).executer([v])
        self._generation(1, AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True})), {}, monde).executer([v])
        self.assertNotEqual(self._lire(0, "ordre-execution.json")["ordre"], self._lire(1, "ordre-execution.json")["ordre"])
        self.assertNotEqual(self._lire(0, "mesures.json")["issues"], self._lire(1, "mesures.json")["issues"],
                            "sans dépôt partagé, le rejeu serait un second tirage : c'est la faille que le dépôt ferme")


class ModelesReelsPermis(unittest.TestCase):
    def test_seuls_opus_et_fable(self):
        import sys
        from pole.adaptateurs import AdaptateurClaudeSDK, ModeleNonPermis, verifier_modele_reel
        verifier_modele_reel("claude-opus-5-5")
        verifier_modele_reel("claude-fable-5-1-20260601")
        for modele in ("claude-sonnet-5-5", "claude-haiku-5-5", None, "simule-a"):
            with self.assertRaises(ModeleNonPermis):
                verifier_modele_reel(modele)
        adaptateur = AdaptateurClaudeSDK("http://127.0.0.1:8787", environnement={}, arme=True)
        with self.assertRaises(ModeleNonPermis):
            adaptateur.lancer("experimentateur", "consigne", os.getcwd(), 1.0, 3, modele="claude-sonnet-5-5")
        self.assertNotIn("claude_agent_sdk", sys.modules, "refusé avant tout import du moteur")


class IssuesConformes(unittest.TestCase):
    def test_conformite(self):
        deposees = {"empreinte_engagement": "e", "issues": [0, 1, 2], "plan_execution": "ordre_secret", "empreinte_ordre": "o"}
        self.assertTrue(issues_conformes(deposees, dict(deposees))[0])
        self.assertFalse(issues_conformes(deposees, dict(deposees, issues=[0, 1, 1]))[0])
        self.assertFalse(issues_conformes(deposees, dict(deposees, empreinte_engagement="f"))[0])
        self.assertFalse(issues_conformes(deposees, dict(deposees, empreinte_ordre="p"))[0])
        self.assertFalse(issues_conformes(deposees, dict(deposees, plan_execution="ordre_naturel"))[0])
        self.assertFalse(issues_conformes(deposees, None)[0])

    def test_chargement_avec_temoins_et_fichier(self):
        import tempfile
        from essais.aides import BASE
        os.makedirs(BASE, exist_ok=True)
        dossier = tempfile.mkdtemp(dir=BASE)
        chemin = os.path.join(dossier, "monde.json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump({"verites": {"Énoncé déclaré vrai": True}}, f)
        temoins = [fiche("T1", enonce="Témoin faux", temoin="fausse")]
        monde = charger_monde_noyau(chemin, 5, temoins)
        self.assertTrue(monde.verite("Énoncé déclaré vrai"))
        self.assertFalse(monde.verite("Témoin faux"))
        sans = charger_monde_noyau(None, 5, temoins)
        self.assertFalse(sans.verite("Témoin faux"))


if __name__ == "__main__":
    unittest.main()
