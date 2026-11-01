"""Essais de la version 0.7.0, pièce 4 : le proposeur (rôle, gabarit, catalogue de stratégies, contexte public) et les
tranches d'épreuve du monde sur banque (exposition adaptative).

Cas sains : le contexte ne contient aucune issue ; une proposition au gabarit devient une fiche complète ; le pôle
continue au-delà de la génération 0 grâce au proposeur et compte les fiches par stratégie ; la stratégie « hors des
bassins déjà promus » évite les couples couverts ; une fiche reste dans la tranche de son premier gel. Artefacts (R5) :
stratégie hors catalogue, moniteur inconnu, poids hors borne, type de loi non permis, mauvaise dimension, champ hors
gabarit — tous refusés avec un motif ; aucun repli silencieux.
"""

import json
import os
import unittest

from essais.test_cycle import CasGeneration
from essais.test_v7_banque import banque_jouet, fiche_banque, loi_trait
from pole.cycle import ConfigGeneration
from pole.monde_banque import MondeBanque
from pole.pole import executer_pole
from pole.proposeur import CATALOGUE, PropositionRefusee, contexte_proposeur, valider_proposition
from pole.simulation import AdaptateurSimule, MondeSimule


def proposition(**modifs):
    p = {"enonce": "L'issue du moniteur A croît avec le premier trait", "strategie": "monotone_un_trait",
         "moniteur": "A", "loi_predictive": loi_trait(0)}
    p.update(modifs)
    return p


class Gabarit(CasGeneration):
    def setUp(self):
        super().setUp()
        self.chemin = os.path.join(self.tmp, "banque.json")
        banque_jouet(self.chemin)
        self.monde = MondeBanque(self.chemin, 7)

    def test_contexte_sans_issues_et_proposition_au_gabarit(self):
        ctx = contexte_proposeur(self.monde, None, 1, 5, 0.05)
        texte = json.dumps(ctx, ensure_ascii=False)
        self.assertNotIn('"issues"', texte)
        self.assertNotIn("richesse", texte)
        self.assertEqual(ctx["monde"]["traits"], ["utile", "bruit"])
        self.assertIn("A", ctx["predicteurs_connus"])
        fiche = valider_proposition(proposition(), self.monde, 0.05, "prop-g01-01", "simule-e")
        self.assertEqual(fiche.espace_instances["moniteur"], "A")
        self.assertEqual(fiche.seuil, 20.0)
        self.assertTrue(fiche.source.startswith("proposeur:monotone_un_trait"))

    def test_artefacts_hors_gabarit_refuses(self):
        cas = {
            "stratégie hors catalogue": proposition(strategie="inventee"),
            "moniteur inconnu": proposition(moniteur="Z"),
            "poids hors borne": proposition(loi_predictive=loi_trait(0, force=5.0)),
            "type non permis": proposition(loi_predictive={"type": "calendrier", "probas": [[1, 1, 1]]}),
            "mauvaise dimension": proposition(loi_predictive={"type": "softmax", "poids": [[1.0], [0.0], [-1.0]],
                                                              "biais": [0, 0, 0]}),
            "champ hors gabarit": proposition(seuil=1.0),
            "mauvais nombre d'issues": proposition(moniteur="B"),
        }
        for nom, p in cas.items():
            with self.assertRaises(PropositionRefusee, msg=nom):
                valider_proposition(p, self.monde, 0.05, "prop-g01-01", "simule-e")

    def test_tranches_fixees_au_premier_gel(self):
        monde = MondeBanque(self.chemin, 7, tranches=3)
        f = fiche_banque("T1", loi_trait(0))
        r0 = monde.reservoir(f, 0)
        r1 = monde.reservoir(f, 1)
        self.assertEqual(r0, r1, "un rejeu reste dans la tranche de son premier gel")
        autre = fiche_banque("T2", loi_trait(0, force=1.0))
        r_autre = monde.reservoir(autre, 1)
        self.assertFalse({json.dumps(x) for x in r0} & {json.dumps(x) for x in r_autre}, "tranches disjointes")


class ProposeurDansLaBoucle(CasGeneration):
    def test_la_course_continue_et_compte_par_strategie(self):
        chemin = os.path.join(self.tmp, "banque.json")
        banque_jouet(chemin, n=360)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        population = [fiche_banque("P1", loi_trait(0)), fiche_banque("P2", loi_trait(1), enonce="L'issue suit le bruit")]
        temoins = [fiche_banque("TV", loi_trait(0, force=1.0), enonce="Témoin vrai", temoin="vraie"),
                   fiche_banque("TF", loi_trait(1, force=1.0), enonce="Témoin faux", temoin="fausse")]
        config = ConfigGeneration(selection="pari", taille_plan=100, taille_plan_filles=100, urne=False, part_calibrage=12,
                                  multiplicite="e-bh", temoins_sans_agent=True, propositions_par_generation=6,
                                  budget_generation_usd=50.0, politique_redite="refus").valider()  # v11 : une tranche
        bilan = executer_pole(population, temoins, AdaptateurSimule(graine=3, monde=MondeSimule(3)), config, 3, 200.0,
                              os.path.join(self.tmp, "course"), monde_noyau=monde)
        self.assertEqual(bilan["generations_executees"], 3, bilan["arret"])
        with open(os.path.join(self.tmp, "course", "journal", "generation-00.json"), encoding="utf-8") as f:
            journal = json.load(f)
        prop = journal["proposeur"]
        self.assertGreater(prop["acceptees"], 0)
        self.assertTrue(set(prop["par_strategie"]) <= set(CATALOGUE))
        self.assertIn("exposition", prop)
        with open(os.path.join(self.tmp, "course", "archive", "index.json"), encoding="utf-8") as f:
            index = json.load(f)
        self.assertTrue(any((e["source"] or "").startswith("proposeur:") for e in index.values()))
        contexte = os.path.join(self.tmp, "course", "archive", "generations", "generation-00", "proposeur",
                                "contexte-proposeur.json")
        with open(contexte, encoding="utf-8") as f:
            self.assertNotIn('"issues"', f.read())

    def test_hors_bassins_promus_evite_les_couples_couverts(self):
        dossier = self.sous_dossier("prop")
        ctx = {"generation": 0, "nombre_de_fiches": 7, "alpha": 0.05,
               "monde": {"nom": "j", "traits": ["t0", "t1", "t2"], "sous_populations": 2,
                         "moniteurs": {"A": {"nombre_issues": 3}, "B": {"nombre_issues": 3}}},
               "predicteurs_connus": {}, "catalogue": CATALOGUE,
               "archive": [{"identifiant": "S1", "enonce": "x", "statut": "survit", "moniteur": "A",
                            "loi_predictive": AdaptateurSimule._loi_monotone(0, 3, 3, 1), "strategie": None,
                            "expliquee_par_le_connu": False}]}
        with open(os.path.join(dossier, "contexte-proposeur.json"), "w", encoding="utf-8") as f:
            json.dump(ctx, f)
        texte, statut = AdaptateurSimule(graine=5)._proposeur(dossier)
        from pole.outils import extraire_bloc_json
        fiches = extraire_bloc_json(texte, "fiches")["fiches"]
        hors = [p for p in fiches if p["strategie"] == "hors_bassins_promus"]
        self.assertTrue(hors)
        for p in hors:
            self.assertNotEqual((p["moniteur"], AdaptateurSimule._trait_principal(p["loi_predictive"])), ("A", 0))




class PhaseExploratoire(CasGeneration):
    def test_developpement_servi_sans_epreuve_et_loi_ajustee_promue_sous_le_nul_informe(self):
        """Banque où l'effet d'un trait change de signe selon la sous-population : le prédicteur connu (linéaire en tous les
        traits) ne le voit pas ; une loi par sous-population ajustée sur le développement le voit."""
        import math
        import random as _r
        rng = _r.Random(13)
        instances = []
        for i in range(480):
            z = [round(rng.gauss(0, 1), 6), round(rng.gauss(0, 1), 6)]
            g = i % 2
            s = 2.4 * z[0] * (1 if g == 0 else -1)
            issue = 1 if rng.random() < 1 / (1 + math.exp(-s)) else 0
            instances.append({"identifiant": f"i{i:03d}", "z": z, "g": g, "issues": {"A": issue},
                              "partie": "calibrage" if i % 3 == 0 else "epreuve"})
        from pole.outils import ecrire_json_scelle
        chemin = os.path.join(self.tmp, "banque-signe.json")
        ecrire_json_scelle(chemin, {"nom": "signe", "traits": ["e0", "bruit"], "sous_populations": 2,
                                    "moniteurs": {"A": {"nombre_issues": 2, "coupes": [0], "instances": 480}},
                                    "instances": instances})
        monde = MondeBanque(chemin, 7, nul_informe=True)
        dev = monde.donnees_developpement()
        epreuve = {l["identifiant"] for l in monde.banque["instances"] if l["partie"] == "epreuve"}
        self.assertTrue(dev["instances"] and not ({x["identifiant"] for x in dev["instances"]} & epreuve))
        from pole.cycle import Budget
        from pole.proposeur import proposer
        config = ConfigGeneration(selection="pari", taille_plan=150, taille_plan_filles=150, urne=False, part_calibrage=12,
                                  propositions_par_generation=8, exploration_developpement=True).valider()
        adaptateur = AdaptateurSimule(graine=21, monde=MondeSimule(21))
        prop = proposer(adaptateur, config, monde, None, 1, self.sous_dossier("proposeur"), Budget(10), 8)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "proposeur", "developpement.json")))
        ajustees = [f for f in prop["fiches"] if f.source.startswith("proposeur:ajustee_sur_developpement")]
        self.assertTrue(ajustees, prop["rapport"])
        from pole.cycle import Generation
        from pole.fiche import RegistreGel
        g = Generation(1, adaptateur, config, self.sous_dossier("course"), RegistreGel(), Budget(20), monde_noyau=monde)
        r = g.executer(ajustees)
        par_sous_pop = [f for f in ajustees if f.loi_predictive["type"] == "par_sous_population"]
        self.assertTrue(par_sous_pop, "à cette graine, le proposeur simulé ajuste une loi par sous-population")
        self.assertTrue(any(f.statut == "survit" for f in par_sous_pop),
                        {f.identifiant: r["issues"][f.identifiant].get("motif") for f in par_sous_pop})
        # Le même énoncé « à l'aveugle » (stratégie difference_sous_populations, sans données) n'a pas cette garantie :
        # la lecture comparée est dans la démonstration, pas dans l'essai.


if __name__ == "__main__":
    unittest.main()
