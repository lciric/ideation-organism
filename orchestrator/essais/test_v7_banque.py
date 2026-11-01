"""Essais de la version 0.7.0, pièces 1 à 3 : monde sur banque, nul informé, configuration sans urne.

Cas sains : une banque jouet où l'issue suit un trait ; la fiche qui le dit est promue (nul aveugle) ; le prédicteur
connu l'explique (nul informé : éliminée) ; le moniteur et le membre « connu » sont sous l'empreinte de l'engagement ;
les instances servies sont toutes d'épreuve. Artefacts (R5) : moniteur inconnu (refus), nombre d'issues faux (refus),
instance sans issue pour le moniteur (exclue, jamais imputée), `urne=False` sans juge v1 (refus), fiche sur un trait de
bruit (éliminée), banque sans champ (refus).
"""

import json
import os
import random
import unittest

from essais.aides import fiche
from essais.test_cycle import CasGeneration
from pole.cycle import Budget, ConfigGeneration, Generation
from pole.fiche import RegistreGel
from pole.monde_banque import BanqueInvalide, MondeBanque, ajuster_softmax
from pole.outils import ecrire_json_scelle
from pole.simulation import AdaptateurSimule, MondeSimule

VRAIE = "L'issue du moniteur A croît avec le premier trait"


def banque_jouet(chemin, n=240, graine=5):
    """Trait 0 informatif (l'issue en suit le signe, avec du bruit), trait 1 de bruit ; moniteur A sur toutes les lignes,
    moniteur B sur la moitié ; un tiers en calibrage."""
    rng = random.Random(graine)
    instances = []
    for i in range(n):
        z = [round(rng.gauss(0, 1), 6), round(rng.gauss(0, 1), 6)]
        p2 = 1 / (1 + pow(2.718281828, -2.5 * z[0]))
        issue = 2 if rng.random() < p2 else (0 if rng.random() < 0.6 else 1)
        issues = {"A": issue}
        if i % 2 == 0:
            issues["B"] = rng.randrange(2)
        instances.append({"identifiant": f"i{i:03d}", "z": z, "g": i % 2, "issues": issues,
                          "partie": "calibrage" if i % 3 == 0 else "epreuve"})
    banque = {"nom": "jouet", "traits": ["utile", "bruit"], "sous_populations": 2,
              "moniteurs": {"A": {"nombre_issues": 3, "coupes": [0, 1], "instances": n},
                            "B": {"nombre_issues": 2, "coupes": [0], "instances": n // 2}},
              "instances": instances}
    ecrire_json_scelle(chemin, banque)
    return banque


def loi_trait(j, k=3, force=1.2):
    poids = [[0.0, 0.0] for _ in range(k)]
    for c in range(k):
        poids[c][j] = force * (c - (k - 1) / 2)
    return {"type": "softmax", "poids": poids, "biais": [0.0] * k}


def fiche_banque(identifiant, loi, moniteur="A", k=3, enonce=VRAIE, **modifs):
    return fiche(identifiant, enonce=enonce, loi_predictive=loi, severite_attendue=0.05, seuil=20.0,
                 espace_instances={"nombre_issues": k, "dimension": 2, "sous_populations": 2, "moniteur": moniteur}, **modifs)


class MondeSurBanque(CasGeneration):
    def setUp(self):
        super().setUp()
        self.chemin = os.path.join(self.tmp, "banque.json")
        self.banque = banque_jouet(self.chemin)
        self.adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: False}))  # son monde est sans objet

    def _generation(self, monde, urne=False, dossier=None):
        cfg = ConfigGeneration(selection="pari", taille_plan=120, taille_plan_filles=120, urne=urne, part_calibrage=12)
        return Generation(0, self.adaptateur, cfg, dossier or self.tmp, RegistreGel(), Budget(10), monde_noyau=monde)

    def test_cas_sain_fiche_vraie_promue_sous_nul_aveugle_et_eliminee_sous_nul_informe(self):
        v = fiche_banque("V1", loi_trait(0))
        r = self._generation(MondeBanque(self.chemin, 7, nul_informe=False), dossier=self.sous_dossier("a")).executer([v])
        self.assertEqual(v.statut, "survit", r["issues"]["V1"].get("motif"))
        v2 = fiche_banque("V1", loi_trait(0))
        g = self._generation(MondeBanque(self.chemin, 7, nul_informe=True), dossier=self.sous_dossier("b"))
        r2 = g.executer([v2])
        self.assertEqual(v2.statut, "eliminee", "le prédicteur connu explique la fiche : elle n'est que du connu")
        self.assertIn("connu:A", r2["issues"]["V1"]["pari"]["membre_dominant_final"])
        engagement = g.engagements["V1"].engagement
        self.assertEqual(engagement["moniteur"], "A")
        self.assertTrue(any(m["nom"] == "connu:A" for m in engagement["bibliotheque"]))
        self.assertFalse(any(m["nom"] == "urne" for m in engagement["bibliotheque"]), "sans urne")
        for inst in engagement["instances"]:
            lignes = [l for l in self.banque["instances"] if l["z"] == inst["z"] and l["g"] == inst["g"]]
            self.assertTrue(lignes and all(l["partie"] == "epreuve" for l in lignes), "jamais une instance de calibrage")
        with open(os.path.join(self.sous_dossier("b"), "archive", "generations", "generation-00", "V1", "experience",
                               "mesures.json"), encoding="utf-8") as f:
            mesures = json.load(f)
        self.assertEqual(len(mesures["issues"]), len(engagement["instances"]))
        self.assertEqual(mesures["plan_execution"], "ordre_secret")

    def test_artefact_fiche_sur_le_bruit_eliminee(self):
        x = fiche_banque("X1", loi_trait(1), enonce="L'issue du moniteur A suit le bruit")
        r = self._generation(MondeBanque(self.chemin, 7, nul_informe=False)).executer([x])
        self.assertEqual(x.statut, "eliminee", r["issues"]["X1"].get("motif"))

    def test_artefacts_refus_sans_repli(self):
        monde = MondeBanque(self.chemin, 7)
        g = self._generation(monde)
        inconnu = fiche_banque("M1", loi_trait(0), moniteur="Z")
        self.assertEqual(g.executer([inconnu])["issues"]["M1"]["verdict_final"], "refusee (invalide)")
        mauvais_k = fiche_banque("M2", loi_trait(0, k=2), moniteur="A", k=2)
        self.assertEqual(self._generation(monde, dossier=self.sous_dossier("k")).executer([mauvais_k])["issues"]["M2"]["verdict_final"],
                         "refusee (invalide)")
        b = fiche_banque("B1", loi_trait(0, k=2), moniteur="B", k=2)
        reservoir = monde.reservoir(b)
        self.assertEqual(len(reservoir), sum(1 for l in self.banque["instances"] if l["partie"] == "epreuve" and "B" in l["issues"]))
        with self.assertRaises(ValueError):
            ConfigGeneration(selection="pari", juge="v0", nul_filles="v0", urne=False).valider()
        with open(os.path.join(self.tmp, "cassee.json"), "w", encoding="utf-8") as f:
            json.dump({"traits": ["a"], "instances": []}, f)
        with self.assertRaises(BanqueInvalide):
            MondeBanque(os.path.join(self.tmp, "cassee.json"), 7)

    def test_ajustement_softmax_retrouve_le_trait_utile(self):
        lignes = [l for l in self.banque["instances"] if l["partie"] == "calibrage"]
        loi = ajuster_softmax([l["z"] for l in lignes], [l["issues"]["A"] for l in lignes], 3, crete=1.0)
        self.assertGreater(loi["poids"][2][0] - loi["poids"][0][0], 1.0, "le poids du trait utile sépare les classes")
        self.assertLess(abs(loi["poids"][2][1] - loi["poids"][0][1]), 0.6, "le trait de bruit pèse peu")


if __name__ == "__main__":
    unittest.main()


class Multiplicite(unittest.TestCase):
    def test_e_bh_retient_les_fortes_et_elimine_les_faibles(self):
        import math
        from pole.cycle import ConfigGeneration, appliquer_multiplicite
        alpha, m = 0.05, 10
        issues = {}
        for i in range(m):
            log_w = {0: math.log(500.0), 1: math.log(250.0), 2: math.log(25.0)}.get(i, -1.0)
            issues[f"F{i}"] = {"verdict_final": "survit" if log_w >= math.log(20) else "eliminee", "motif": "x",
                               "pari": {"log_richesse_finale": log_w, "log_richesse_max": log_w,
                                        "trajectoire_log_w": [0.0, log_w / 2, log_w]}}
        r = appliquer_multiplicite(issues, alpha)
        # seuils : k=1 → 200 ; k=2 → 100 ; k=3 → 66,7 : F0 (500) et F1 (250) retenues, F2 (25, promue par fiche) éliminée
        self.assertEqual(sorted(r["retenues"]), ["F0", "F1"])
        self.assertEqual(issues["F2"]["verdict_final"], "eliminee")
        self.assertIn("multiplicité e-BH", issues["F2"]["motif"])
        self.assertEqual(issues["F0"]["verdict_final"], "survit")
        self.assertEqual(appliquer_multiplicite({"A": {"verdict_final": "indecise"}}, alpha)["m"], 0)
        # Artefact de la première version (R5) : une richesse qui franchit 1/α tôt puis monte très haut doit être retenue ;
        # arrêter l'e-valeur au seuil par fiche (1/α) la plafonnait et e-BH ne retenait rien.
        monte = {f"G{i}": {"verdict_final": "eliminee", "motif": "x",
                           "pari": {"trajectoire_log_w": [-0.5, -1.0, -0.2]}} for i in range(9)}
        monte["H"] = {"verdict_final": "survit", "motif": "x",
                      "pari": {"trajectoire_log_w": [1.0, 3.1, 8.0, 20.0, 34.0]}}
        r2 = appliquer_multiplicite(monte, alpha)
        self.assertEqual(r2["retenues"], ["H"])
        self.assertEqual(monte["H"]["verdict_final"], "survit")
        self.assertAlmostEqual(monte["H"]["pari"]["multiplicite"]["log_e"], 8.0, "arrêtée au premier instant ≥ log(m/α)")
        # Preuve héritée : elle s'ajoute à l'e-valeur arrêtée
        herite = {"A": {"verdict_final": "survit", "motif": "x", "pari": {"trajectoire_log_w": [3.2],
                                                                          "heritage": {"cumul": 2.0}}},
                  "B": {"verdict_final": "eliminee", "motif": "x", "pari": {"trajectoire_log_w": [-1.0]}}}
        self.assertEqual(appliquer_multiplicite(herite, alpha)["retenues"], ["A"], "3,2 + 2,0 ≥ log(2/0,05) = 3,69")
        with self.assertRaises(ValueError):
            ConfigGeneration(multiplicite="bonferroni").valider()


class TemoinsSansAgentEtSansDents(CasGeneration):
    def test_temoins_juges_par_le_noyau_seul_et_signal_sans_dents(self):
        chemin = os.path.join(self.tmp, "banque.json")
        banque_jouet(chemin)
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3))
        cfg = ConfigGeneration(selection="pari", taille_plan=120, taille_plan_filles=120, urne=False, part_calibrage=12,
                               temoins_sans_agent=True)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        vrai = fiche_banque("TV", loi_trait(0), temoin="vraie")
        faux = fiche_banque("TF", loi_trait(1), enonce="Témoin faux sur le bruit", temoin="fausse")
        ordinaire = fiche_banque("O1", loi_trait(0), enonce="Fiche ordinaire sur le trait utile")
        g = Generation(0, adaptateur, cfg, self.tmp, RegistreGel(), Budget(10), monde_noyau=monde)
        r = g.executer([vrai, faux, ordinaire])
        self.assertEqual(vrai.statut, "survit", r["issues"]["TV"].get("motif"))
        self.assertEqual(faux.statut, "eliminee")
        self.assertTrue(r["issues"]["TV"]["sans_agent"] and r["issues"]["TF"]["sans_agent"])
        roles = [(a["role"], os.path.basename(os.path.dirname(a["dossier"]))) for a in adaptateur.appels]
        self.assertEqual(sorted({d for _, d in roles}), ["O1"], "aucun agent lancé pour les témoins")
        self.assertFalse(r["qualite"]["sans_dents"])
        self.assertNotIn("sans_dents", r["issues"]["O1"])
        # artefact : un témoin vrai construit pour être éliminé (loi inversée) → signal « pas de dents » sur la génération
        inverse = fiche_banque("TV2", loi_trait(0, force=-1.2), enonce="Témoin vrai mal déclaré", temoin="vraie")
        o2 = fiche_banque("O2", loi_trait(0), enonce="Fiche ordinaire bis")
        g2 = Generation(1, adaptateur, cfg, self.sous_dossier("g2"), RegistreGel(), Budget(10), monde_noyau=monde)
        r2 = g2.executer([inverse, o2])
        self.assertEqual(inverse.statut, "eliminee")
        self.assertTrue(r2["qualite"]["sans_dents"])
        if o2.statut == "survit":
            self.assertTrue(r2["issues"]["O2"].get("sans_dents"))
