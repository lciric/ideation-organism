"""Essais de la version 0.7.0, version 6 : loi « transformee » (tricheurs du banc) et nul d'archive ajusté.

Cas sains : une transformation neutre rend la loi de base ; chaque étape fait ce qu'elle dit ; une fiche vraiment nouvelle
reste promue avec le nul d'archive ajusté. Artefacts (R5) : transformation mal formée refusée ; le mélange de deux
survivantes soumis comme fiche fraîche (T04) est promu avec le nul d'archive de v7 et éliminé avec le nul ajusté ; le
proposeur ne peut pas écrire de loi « transformee ».
"""

import math
import os
import unittest

from essais.aides import fiche
from essais.test_cycle import CasGeneration
from essais.test_v7_nul_archive import banque_deux_effets, fiche_a, loi
from pole import selection_pari as sp
from pole.cycle import Budget, ConfigGeneration, Generation, membres_de_l_archive
from pole.fiche import RegistreGel
from pole.memoire import Memoire
from pole.monde_banque import MondeBanque
from pole.simulation import AdaptateurSimule, MondeSimule

BASE = {"type": "softmax", "poids": [[-1.0, 0.5], [0.0, 0.0], [1.0, -0.5]], "biais": [0.1, 0.0, -0.1]}
INSTANCE = {"z": [0.7, -1.2], "g": 0}


class Transformee(unittest.TestCase):
    def test_neutre_et_etapes(self):
        p = sp.proba(BASE, INSTANCE, [], 0)
        neutre = {"type": "transformee", "base": BASE, "puissance": 1.0, "inclinaison": [0.0, 0.0, 0.0]}
        for a, b in zip(sp.proba(neutre, INSTANCE, [], 0), p):
            self.assertAlmostEqual(a, b, places=12)
        aveugle = {"type": "transformee", "base": BASE, "melange_aveugle": {"lambda": 1.0, "probas": [2, 1, 1]}}
        for a, b in zip(sp.proba(aveugle, INSTANCE, [], 0), [0.5, 0.25, 0.25]):
            self.assertAlmostEqual(a, b, places=12)
        froide = sp.proba({"type": "transformee", "base": BASE, "puissance": 6.0}, INSTANCE, [], 0)
        self.assertEqual(froide.index(max(froide)), p.index(max(p)))
        self.assertGreater(max(froide), max(p))
        osc = {"type": "transformee", "base": BASE,
               "oscillation": {"amplitude": 1.0, "frequence": 2.0, "trait": 0, "issue": 1, "phase": 0.0}}
        q = sp.proba(osc, INSTANCE, [], 0)
        facteur = math.exp(math.cos(2.0 * 0.7))
        attendu = [p[0], p[1] * facteur, p[2]]
        s = sum(attendu)
        for a, b in zip(q, attendu):
            self.assertAlmostEqual(a, b / s, places=12)
        sp.valider_loi(osc, 3, 2)

    def test_mal_formees_refusees(self):
        cas = [{"type": "transformee", "base": BASE, "puissance": 0.0},
               {"type": "transformee", "base": BASE, "inclinaison": [0.0, 1.0]},
               {"type": "transformee", "base": BASE, "melange_aveugle": {"lambda": 1.5, "probas": [1, 1, 1]}},
               {"type": "transformee", "base": BASE, "oscillation": {"amplitude": 1.0, "frequence": 2.0, "trait": 5,
                                                                     "issue": 0}},
               {"type": "transformee", "base": {"type": "inconnu"}}]
        for loi_ in cas:
            with self.subTest(loi=loi_), self.assertRaises(sp.LoiInvalide):
                sp.valider_loi(loi_, 3, 2)

    def test_le_proposeur_ne_peut_pas_l_ecrire(self):
        from pole.proposeur import TYPES_PERMIS
        self.assertNotIn("transformee", TYPES_PERMIS)


class NulArchiveAjuste(CasGeneration):
    def _course(self, ajuste, dossier):
        chemin = os.path.join(self.tmp, "banque.json")
        if not os.path.exists(chemin):
            banque_deux_effets(chemin)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3))
        cfg = ConfigGeneration(selection="pari", taille_plan=150, taille_plan_filles=150, urne=False, part_calibrage=12,
                               nul_archive=True, nul_archive_ajuste=ajuste).valider()
        memoire = Memoire(active=True, graine=0)
        registre = RegistreGel()
        s1 = fiche_a("S1", loi(0), "L'issue croît avec le trait e0")
        s2 = fiche_a("S2", loi(2), "L'issue croît avec le trait e2")
        g0 = Generation(0, adaptateur, cfg, os.path.join(self.tmp, dossier), registre, Budget(10), memoire=memoire,
                        monde_noyau=monde)
        r0 = g0.executer([s1, s2])
        for s in (s1, s2):
            memoire.indexer(s, r0["issues"][s.identifiant], 0)
            self.assertEqual(s.statut, "survit", r0["issues"][s.identifiant].get("motif"))
        melange = fiche_a("M1", {"type": "melange", "composantes": [loi(0), loi(2)], "poids": [0.5, 0.5]},
                          "Les deux descripteurs comptent ensemble")
        # La loi exacte du monde (score de l'issue 2 : 1,6·z0 + 1,6·z2 ; issues 0 et 1 dans le rapport 0,6 / 0,4).
        neuve = fiche_a("N1", {"type": "softmax", "poids": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.6, 0.0, 1.6]],
                               "biais": [math.log(0.6), math.log(0.4), 0.0]}, "L'issue suit la somme des deux descripteurs")
        g1 = Generation(1, adaptateur, cfg, os.path.join(self.tmp, dossier), registre, Budget(10), memoire=memoire,
                        monde_noyau=monde)
        r1 = g1.executer([melange, neuve])
        return g1, r1, melange, neuve

    def test_melange_de_survivantes_elimine_par_le_nul_ajuste(self):
        _, r_v7, m_v7, n_v7 = self._course(False, "v7")
        g, r_aj, m_aj, n_aj = self._course(True, "ajuste")
        self.assertEqual(m_v7.statut, "survit", "avec le nul d'archive de v7, le mélange de deux survivantes passe (T04)")
        self.assertEqual(m_aj.statut, "eliminee", r_aj["issues"]["M1"].get("motif"))
        self.assertIn("instants_lecture", g.engagements["M1"].engagement)
        noms = [m["nom"] for m in g.engagements["M1"].engagement["bibliotheque"]]
        self.assertIn("ajuste_lineaire:archive", noms)
        self.assertIn("ajuste_log:archive:S1", noms)
        self.assertEqual(n_aj.statut, "survit", "la loi de la somme (le vrai monde) bat toutes les lois connues")

    def test_options_incoherentes_refusees(self):
        for reglages in ({"nul_archive": False, "nul_archive_ajuste": True},
                         {"nul_archive": True, "nul_archive_ajuste": True, "nul_filles": "v0", "selection": "pari"},
                         {"nul_archive": True, "nul_archive_ajuste": True, "selection": "seuil"}):
            with self.subTest(reglages=reglages), self.assertRaises(ValueError):
                ConfigGeneration(**reglages).valider()

    def test_membres_ajustes_incluent_les_parents_d_une_fille(self):
        memoire = Memoire(active=True, graine=0)
        s = fiche_a("S1", loi(0), "x")
        memoire.index["S1"] = {"statut": "survit", "temoin": False, "loi_predictive": loi(0),
                               "espace_instances": s.espace_instances}
        fille = fiche_a("F1", loi(2), "y")
        membres = membres_de_l_archive(fille, memoire, ajuste=True, lois_parents={"A": loi(1), "B": loi(2)})
        lineaire = [m for m in membres if m["nom"] == "ajuste_lineaire:archive"][0]
        self.assertEqual(lineaire["lois"], [loi(1), loi(2), loi(0)])


if __name__ == "__main__":
    unittest.main()
