import random
import unittest

from essais.aides import CasAvecDossier, fiche
from pole.cycle import Budget, ConfigGeneration
from pole.outils import graine_derivee
from pole.recombinaison import (cholesky, conflits, est_definie_positive, marqueurs, noyau_corrige, noyau_diversite,
                                noyau_fautif, recombiner, tirage_glouton, valider_fille, vecteurs_domaine)
from pole.simulation import AdaptateurSimule

VOCABULAIRE = ["memoire", "spectre", "graphes", "morphologie", "arret", "hachage", "optimisation", "mesure"]


def tirage(r):
    rng = random.Random(graine_derivee(20261026, "noyau", r))
    n = rng.randint(2, 12)
    domaines = [rng.sample(VOCABULAIRE, rng.randint(1, 3)) for _ in range(n)]
    operateurs = [rng.sample(VOCABULAIRE, rng.randint(1, 3)) for _ in range(n)]
    q = [rng.uniform(0.0, 7.0) for _ in range(n)]
    return domaines, operateurs, q


class Noyau(unittest.TestCase):
    def test_noyau_corrige_defini_positif_sur_1000_tirages(self):
        reussites = 0
        for r in range(1000):
            domaines, _, q = tirage(r)
            s = noyau_diversite(vecteurs_domaine(domaines))
            reussites += est_definie_positive(noyau_corrige(s, q, 1e-3))
            self.assertTrue(est_definie_positive([[v + (1e-9 if i == j else 0) for j, v in enumerate(l)]
                                                  for i, l in enumerate(s)]))
        self.assertEqual(reussites, 1000)

    def test_noyau_fautif_du_rapport_detecte(self):
        echecs = 0
        for r in range(1000):
            domaines, operateurs, _ = tirage(r)
            k = noyau_fautif(vecteurs_domaine(operateurs), vecteurs_domaine(domaines))
            echecs += not est_definie_positive([[v + (1e-3 if i == j else 0) for j, v in enumerate(l)]
                                                for i, l in enumerate(k)])
        self.assertGreater(echecs, 0)

    def test_tirage_glouton_diversifie(self):
        s = noyau_diversite(vecteurs_domaine([["memoire"], ["memoire"], ["graphes"]]))
        choisis = tirage_glouton(noyau_corrige(s, [2.0, 2.0, 2.0]), 2)
        self.assertIn(2, choisis)
        self.assertEqual(len(set(choisis) & {0, 1}), 1)

    def test_cholesky_refuse_non_symetrique(self):
        with self.assertRaises(ValueError):
            cholesky([[1.0, 0.5], [0.0, 1.0]])


class Compatibilite(unittest.TestCase):
    CONTRADICTIONS = [(["linéaire"], ["non-linéaire"]), (["stationnaire"], ["non stationnaire"]),
                      (["stationnaire"], ["régime transitoire"]), (["temps discret"], ["temps continu"]),
                      (["convexe"], ["non convexe"]), (["variables indépendantes"], ["bruit dépendant"]),
                      (["Linéaires"], ["non linéaires"]), (["discrète"], ["continue"])]
    SAINS = [(["linéaire"], ["linéaire"]), (["non linéaire"], ["non-linéaire"]), (["convexe"], ["stationnaire"]),
             (["indépendant"], ["indépendante"]), (["discret"], ["linéaire"]), ([], ["continu"])]

    def test_contradictions_plantees_detectees(self):
        for a, b in self.CONTRADICTIONS:
            with self.subTest(a=a, b=b):
                self.assertTrue(conflits(a, b))
                self.assertTrue(conflits(b, a))

    def test_couples_sains_gardes(self):
        for a, b in self.SAINS:
            with self.subTest(a=a, b=b):
                self.assertEqual(conflits(a, b), [])

    def test_independant_n_est_pas_dependant(self):
        self.assertEqual(marqueurs(["indépendant"]), {"independant"})


class Fusion(CasAvecDossier):
    def survivante(self, identifiant, domaines, operateurs, contraintes, **modifs):
        f = fiche(identifiant, enonce=f"Énoncé {identifiant} sur {domaines[0]}", domaines=domaines,
                  operateurs=operateurs, contraintes=contraintes, **modifs)
        f.statut = "survit"
        return f

    def test_paires_filtrees_et_filles_a_deux_parents(self):
        a = self.survivante("A", ["memoire"], ["projection"], ["linéaire"])
        b = self.survivante("B", ["graphes"], ["projection"], ["stationnaire"])
        c = self.survivante("C", ["hachage"], ["projection"], ["non linéaire"])
        d = self.survivante("D", ["arret"], ["seuillage"], ["continu"])
        t = self.survivante("T", ["mesure"], ["projection"], [], temoin="vraie")
        r = recombiner([a, b, c, d, t], AdaptateurSimule(graine=1), ConfigGeneration(), self.tmp, Budget(10), 0, k=4,
                       max_paires=6)
        self.assertNotIn("T", r["rapport"]["candidates"], "un témoin n'entre jamais dans la recombinaison")
        ecartees = {tuple(e["paire"]): e for e in r["rapport"]["ecartees"]}
        self.assertTrue(ecartees[("A", "C")]["conflits"])
        self.assertFalse(ecartees[("A", "D")]["pont"])
        self.assertTrue(r["filles"])
        for fille in r["filles"]:
            self.assertEqual(len(fille.parents), 2)
            self.assertTrue(fille.ce_que_la_fille_predit_de_plus.strip())
        with open(f"{self.tmp}/traces-paire-01/consigne.txt", encoding="utf-8") as f:
            self.assertIn("ce_que_la_fille_predit_de_plus", f.read())

    def test_fille_sans_prediction_nouvelle_refusee(self):
        a = self.survivante("A", ["memoire"], ["projection"], ["linéaire"])
        b = self.survivante("B", ["graphes"], ["projection"], ["stationnaire"])
        base = {k: v for k, v in fiche("X").vers_dict().items() if k not in ("identifiant", "parents", "statut")}
        base["prediction"] = {"signe": "+", "valeur": 0.7, "texte": "effet joint"}
        recevable, motif = valider_fille(dict(base, ce_que_la_fille_predit_de_plus="effet joint absent des parents"),
                                         a, b, "fille-1", "recombinaison:m")
        self.assertIsNotNone(recevable, motif)
        self.assertEqual(recevable.parents, ["A", "B"])
        self.assertIsNone(valider_fille(dict(base, ce_que_la_fille_predit_de_plus=""), a, b, "fille-2", "r")[0])
        copie = dict(base, prediction=a.prediction, ce_que_la_fille_predit_de_plus="rien")
        self.assertIsNone(valider_fille(copie, a, b, "fille-3", "r")[0])


if __name__ == "__main__":
    unittest.main()
