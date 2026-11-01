"""Essais de la version 0.5.0 : seuil de la signature par fiche (calibré sur la taille de l'archive) ; graine du noyau
tirée par `secrets` (`noyau_secret`), jamais écrite dans un dossier d'agent, écrite après les évaluations (R5 : cas sain
et artefact)."""

import json
import os
import random
import unittest

from essais.aides import fiche
from essais.test_cycle import CasGeneration
from pole import selection_pari as sp
from pole.cycle import Budget, ConfigGeneration, Generation
from pole.fiche import RegistreGel
from pole.memoire import SEUIL_SIGNATURE, Memoire
from pole.outils import graine_derivee
from pole.simulation import AdaptateurSimule, MondeSimule

VRAIE = "La loi engagée prédit les issues des instances d'essai"


def fiche_pari(identifiant, loi, enonce=VRAIE):
    return fiche(identifiant, enonce=enonce, loi_predictive=loi, severite_attendue=0.05, seuil=20.0,
                 espace_instances={"nombre_issues": 3, "dimension": 2})


class SeuilParFiche(unittest.TestCase):
    def test_le_seuil_se_resserre_quand_l_archive_grandit(self):
        m = Memoire(graine=2)
        rng = random.Random(3)
        self.assertEqual(m.seuil_effectif(3, 2), SEUIL_SIGNATURE)  # archive vide
        seuils = []
        for i in range(60):
            f = fiche_pari(f"F{i}", sp.loi_softmax_aleatoire(rng, force=1.5), enonce=f"Hypothèse {i} sur les instances")
            f.statut = "eliminee"
            m.indexer(f, {"verdict_final": "eliminee", "pari": {"log_richesse_finale": -3.0, "log_richesse_max": 0.0}}, 0)
            if i in (0, 9, 59):
                seuils.append(m.seuil_effectif(3, 2))
        self.assertLessEqual(seuils[0], SEUIL_SIGNATURE)
        self.assertGreater(seuils[0], seuils[1])
        self.assertGreater(seuils[1], seuils[2])
        self.assertGreater(seuils[2], 0.0)
        copie = fiche_pari("C1", m.index["F5"]["loi_predictive"])
        self.assertEqual(m.chercher_classe(copie)[0], "F5", "une copie exacte reste reconnue")

    def test_fausses_fusions_par_fiche_tenues_sur_lois_neuves(self):
        m = Memoire(graine=4)
        rng = random.Random(5)
        for i in range(40):
            f = fiche_pari(f"F{i}", sp.loi_softmax_aleatoire(rng, force=1.5), enonce=f"Hypothèse {i}")
            f.statut = "eliminee"
            m.indexer(f, {"verdict_final": "eliminee", "pari": {"log_richesse_finale": -3.0, "log_richesse_max": 0.0}}, 0)
        fusions = sum(m.chercher_classe(fiche_pari(f"N{j}", sp.loi_softmax_aleatoire(rng, force=1.5)))[0] is not None
                      for j in range(200))
        self.assertLessEqual(fusions, 25, "au plus de l'ordre de 5 % (borne large : 12,5 %) de lois neuves fusionnées")


class NoyauSecret(CasGeneration):
    def test_graine_tiree_hors_du_pole_et_ecrite_apres_les_evaluations(self):
        rng = random.Random(8)
        loi = sp.loi_softmax_aleatoire(rng, force=2.0)
        v = fiche_pari("V1", loi)
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3, {VRAIE: True}))
        cfg = ConfigGeneration(selection="pari", taille_plan=80, taille_plan_filles=80, noyau_secret=True)
        g = Generation(0, adaptateur, cfg, self.tmp, RegistreGel(), Budget(10))
        self.assertNotEqual(g.graine_noyau, graine_derivee(cfg.graine, "noyau", 0))
        r = g.executer([v])
        self.assertEqual(v.statut, "survit", r["issues"]["V1"].get("motif"))
        with open(os.path.join(self.tmp, "noyau", "graine-noyau-generation-00.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["graine_noyau"], g.graine_noyau)
        dossier = os.path.join(self.tmp, "archive", "generations", "generation-00", "V1")
        for racine, _, fichiers in os.walk(dossier):
            for nom in fichiers:
                with open(os.path.join(racine, nom), "rb") as fb:
                    self.assertNotIn(str(g.graine_noyau).encode(), fb.read(), nom)
        autre = Generation(0, adaptateur, cfg, self.sous_dossier("b"), RegistreGel(), Budget(10))
        self.assertNotEqual(autre.graine_noyau, g.graine_noyau, "une graine neuve à chaque génération")
        with self.assertRaises(ValueError):
            ConfigGeneration(noyau_secret="oui").valider()


if __name__ == "__main__":
    unittest.main()
