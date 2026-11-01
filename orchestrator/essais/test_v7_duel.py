"""Essais du pari apparié borné du duel des proposeurs (forme « parts » seule, conception v2)."""

import math
import os
import random
import sys
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "demonstrations"))

from duel_proposeurs_v7 import ALPHA, LAMBDAS, pari_apparie  # noqa: E402


def _pari_signe_v1(valeurs):
    """L'ancienne forme « signe » (v1), gardée ici comme artefact : elle doit promouvoir là où la forme parts ne le fait pas."""
    ws = [1.0] * len(LAMBDAS)
    for v in valeurs:
        s = (v > 0) - (v < 0)
        ws = [w * (1 + lam * s) for w, lam in zip(ws, LAMBDAS)]
        if sum(ws) / len(LAMBDAS) >= 1 / ALPHA:
            return True
    return False


class PariApparieParts(unittest.TestCase):
    def test_contraste_plein_promu_au_septieme_instant(self):
        r = pari_apparie([1.0] * 10)
        self.assertTrue(r["promu"])
        self.assertEqual(r["instant_de_promotion"], 7)  # moyenne de 1,1^t, 1,3^t, 1,6^t, 1,9^t ≥ 20 dès t = 7
        self.assertAlmostEqual(r["seuil_log"], math.log(20))

    def test_nul_asymetrique_de_moyenne_nulle_non_promu(self):
        # Banque figée de moyenne exactement nulle : 90 contrastes à +0,1 et 10 à −0,9 (constat C1 de la contre-lecture).
        banque = [0.1] * 90 + [-0.9] * 10
        rng = random.Random(20261027)
        promus_parts, promus_signe = 0, 0
        for _ in range(50):
            rng.shuffle(banque)
            promus_parts += pari_apparie(list(banque))["promu"]
            promus_signe += _pari_signe_v1(banque)
        self.assertEqual(promus_parts, 0)  # richesse finale de la forme parts indépendante de l'ordre : Π(1 + λ v) ≤ 1 ici
        self.assertEqual(promus_signe, 50)  # l'artefact : la forme signe promeut dans tous les ordres

    def test_richesse_finale_sous_le_nul_figé(self):
        banque = [0.1] * 90 + [-0.9] * 10
        r = pari_apparie(banque)
        # Π(1 + λ·0,1)^90 · (1 − 0,9 λ)^10 < 1 pour chaque λ de la grille : la richesse finale est < 1.
        self.assertLess(r["trajectoire_log_w"][-1], 0.0)

    def test_contraste_hors_bornes_refuse(self):
        with self.assertRaises(ValueError):
            pari_apparie([0.5, 1.2])

    def test_sequence_vide(self):
        r = pari_apparie([])
        self.assertFalse(r["promu"])
        self.assertEqual(r["n"], 0)


if __name__ == "__main__":
    unittest.main()
