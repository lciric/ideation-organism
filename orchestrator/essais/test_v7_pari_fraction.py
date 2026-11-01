"""Essais du pari à fraction (v7, version 5) : levier de puissance du juge, garantie inchangée.

Numérateur de la richesse = mélange bayésien, sur la grille λ ∈ {0,25 ; 0,5 ; 0,75 ; 1}, des lois λ·p_h + (1 − λ)·m_t
(m_t : marginale en ligne des issues précédentes, prévisible). Trois contrôles :
1. équivalence : grille {1} = pari plein (v0 à v6), au jeton près ;
2. puissance (cas sain du levier) : une loi juste mais trop confiante, ruinée par le pari plein sur les issues qu'elle
   croyait improbables, est promue bien plus souvent avec la fraction ;
3. **contrôle fatal** (R5) : sous le nul (issues indépendantes des traits, loi i.i.d. quelconque, donc dans la
   bibliothèque nulle par la marginale du maximum de vraisemblance), le taux de promotion reste ≤ α, quelle que soit la
   loi déclarée (ici la plus agressive). S'il le dépasse, le pari à fraction est faux et ne sert pas.
"""

import math
import random
import unittest

from pole import selection_pari as sp
from pole.cycle import ConfigGeneration, preparer_engagement
from essais.aides import fiche

K, D = 3, 2
LOI_VRAIE = {"type": "softmax", "poids": [[-1.0, 0.0], [0.0, 0.0], [1.0, 0.0]], "biais": [0.0, 0.0, 0.0]}
LOI_TROP_CONFIANTE = {"type": "softmax", "poids": [[-4.0, 0.0], [0.0, 0.0], [4.0, 0.0]], "biais": [0.0, 0.0, 0.0]}


def engagement(loi, instances, fractions=None):
    e = sp.construire_engagement("E", loi, instances, nombre_issues=K, alpha=0.05)
    if fractions is not None:
        e["fractions"] = list(fractions)
    return sp.geler_engagement(e)


def issues_du_monde(rng, loi_monde, instances):
    if loi_monde.get("type") == "iid":
        return [sp.tirer_categorie(rng, loi_monde["p"]) for _ in instances]
    return [sp.tirer_categorie(rng, sp.proba(loi_monde, inst, [], t)) for t, inst in enumerate(instances)]


def evaluer(gele, issues):
    return sp.evaluer(gele, {"empreinte_engagement": gele.empreinte, "issues": issues, "plan_execution": "ordre_naturel"})


class Equivalence(unittest.TestCase):
    def test_grille_un_egale_pari_plein(self):
        rng = random.Random(11)
        instances = sp.tirer_instances(rng, 150, D)
        issues = issues_du_monde(rng, LOI_VRAIE, instances)
        plein = sp.trajectoire_loi(LOI_VRAIE, issues, instances)
        un = sp.trajectoire_numerateur({"loi": LOI_VRAIE, "nombre_issues": K, "fractions": [1.0]}, issues, instances)
        self.assertEqual(len(plein), len(un))
        for a, b in zip(plein, un):
            self.assertAlmostEqual(a, b, places=9)
        sans = sp.trajectoire_numerateur({"loi": LOI_VRAIE, "nombre_issues": K}, issues, instances)
        self.assertEqual(sans, plein, "sans grille : le pari plein de v0 à v6, inchangé")

    def test_prix_borne_par_log_du_nombre_de_fractions(self):
        """Le mélange perd au plus log(4) contre la meilleure fraction, à chaque instant."""
        rng = random.Random(12)
        instances = sp.tirer_instances(rng, 120, D)
        issues = issues_du_monde(rng, LOI_VRAIE, instances)
        melange = sp.trajectoire_numerateur({"loi": LOI_VRAIE, "nombre_issues": K, "fractions": list(sp.GRILLE_FRACTIONS)},
                                            issues, instances)
        par_fraction = [sp.trajectoire_numerateur({"loi": LOI_VRAIE, "nombre_issues": K, "fractions": [lam]}, issues,
                                                  instances) for lam in sp.GRILLE_FRACTIONS]
        for t in range(len(issues)):
            meilleure = max(tr[t] for tr in par_fraction)
            self.assertGreaterEqual(melange[t], meilleure - math.log(len(sp.GRILLE_FRACTIONS)) - 1e-9)
            self.assertLessEqual(melange[t], meilleure + 1e-9)


class Puissance(unittest.TestCase):
    def test_loi_juste_mais_trop_confiante(self):
        promues_plein = promues_fraction = 0
        somme_ecart = 0.0
        repetitions = 40
        for r in range(repetitions):
            rng = random.Random(1000 + r)
            instances = sp.tirer_instances(rng, 200, D)
            issues = issues_du_monde(rng, LOI_VRAIE, instances)
            plein = evaluer(engagement(LOI_TROP_CONFIANTE, instances), issues)
            fraction = evaluer(engagement(LOI_TROP_CONFIANTE, instances, sp.GRILLE_FRACTIONS), issues)
            promues_plein += plein["promue"]
            promues_fraction += fraction["promue"]
            somme_ecart += fraction["log_richesse_finale"] - plein["log_richesse_finale"]
        self.assertGreater(promues_fraction, promues_plein + repetitions // 4,
                           (promues_plein, promues_fraction))
        self.assertGreater(somme_ecart / repetitions, 0.0)


class GarantieSousLeNul(unittest.TestCase):
    def test_taux_de_promotion_sous_le_nul_au_plus_alpha(self):
        """Contrôle fatal : 600 répétitions, issues i.i.d. (indépendantes des traits) ; loi déclarée la plus agressive."""
        repetitions, alpha = 600, 0.05
        promues = 0
        for r in range(repetitions):
            rng = random.Random(5000 + r)
            instances = sp.tirer_instances(rng, 120, D)
            issues = issues_du_monde(rng, {"type": "iid", "p": [0.5, 0.3, 0.2]}, instances)
            promues += evaluer(engagement(LOI_TROP_CONFIANTE, instances, sp.GRILLE_FRACTIONS), issues)["promue"]
        borne = alpha + 3 * math.sqrt(alpha * (1 - alpha) / repetitions)
        self.assertLessEqual(promues / repetitions, borne, promues)


class DansLeCycle(unittest.TestCase):
    def test_grille_declaree_sous_l_empreinte_de_l_engagement(self):
        f = fiche("P1", loi_predictive=LOI_VRAIE, severite_attendue=0.05, seuil=20.0,
                  espace_instances={"nombre_issues": K, "dimension": D, "sous_populations": 2})
        sans = preparer_engagement(f, ConfigGeneration(selection="pari", taille_plan=60).valider())
        avec = preparer_engagement(f, ConfigGeneration(selection="pari", taille_plan=60, pari_fraction=True).valider())
        self.assertNotIn("fractions", sans.engagement)
        self.assertEqual(avec.engagement["fractions"], list(sp.GRILLE_FRACTIONS))
        self.assertNotEqual(sans.empreinte, avec.empreinte)


if __name__ == "__main__":
    unittest.main()
