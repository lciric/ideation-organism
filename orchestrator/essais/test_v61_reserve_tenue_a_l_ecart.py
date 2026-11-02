"""Essais de la v61 — réserve durcie (`pole/reserve_tenue_a_l_ecart_v61.py`, changement C4, constat I3) : orthographe des
tâches, forme normalisée, identifiants et traits de T dans un contexte, disjonction M2 ∩ R = ∅. Cas sain et artefact (R5)."""

import unittest

from pole import reserve_tenue_a_l_ecart_v61 as R  # noqa: E402

T_EP = [{"identifiant": "t001/e1", "tache": "2506.01290v2", "z": [0.123456, -0.2]}, {"identifiant": "t001/e2", "tache": "2506.01290v2", "z": [1.5, 2.5]}]
TACHES = ["2506.01290v2", "2507.00001v1"]


class Orthographe(unittest.TestCase):
    def test_normaliser(self):
        self.assertEqual(R.normaliser("2506.01290v2"), "2506.01290")
        self.assertEqual(R.normaliser("tache-003"), "tache-003")
        with self.assertRaises(R.ReserveRefusee):
            R.normaliser("")

    def test_sain_et_artefact(self):
        self.assertEqual(R.verifier_orthographe(["2506.01290v2", "x"], ["2506.01290v2", "y"]), ["2506.01290v2"])
        with self.assertRaises(R.ReserveRefusee):
            R.verifier_orthographe(["2506.01290v2"], ["2506.01290"])
        with self.assertRaises(R.ReserveRefusee):
            R.verifier_orthographe(["2506.01290v2"], ["2506.01290v3"])


class Contexte(unittest.TestCase):
    def test_taches_exactes_ou_normalisees(self):
        self.assertEqual(R.taches_reservees_dans("rien ici", TACHES), [])
        self.assertEqual(R.taches_reservees_dans("voir 2506.01290v2", TACHES), ["2506.01290v2"])
        self.assertEqual(R.taches_reservees_dans("voir 2506.01290 sans version", TACHES), ["2506.01290v2"])

    def test_identifiants_et_traits(self):
        self.assertEqual(R.fuites_dans("contexte propre", TACHES, T_EP), {"taches": [], "identifiants": [], "traits": []})
        f = R.fuites_dans("épisode t001/e2 servi", TACHES, T_EP)
        self.assertEqual(f["identifiants"], ["t001/e2"])
        f = R.fuites_dans('"z": [0.1235, -0.2]', TACHES, T_EP)
        self.assertEqual(f["traits"], ["t001/e1"])
        f = R.fuites_dans("[1.5,2.5]", TACHES, T_EP)
        self.assertEqual(f["traits"], ["t001/e2"])


class Disjonction(unittest.TestCase):
    def test_sain_et_artefacts(self):
        m2 = [{"identifiant": "p1", "tache": "2508.0v1"}, {"identifiant": "p2", "tache": "autre"}]
        self.assertEqual(R.verifier_disjonction(m2, T_EP, TACHES)["episodes_m2"], 2)
        with self.assertRaises(R.ReserveRefusee):
            R.verifier_disjonction(m2 + [{"identifiant": "p3", "tache": "2506.01290"}], T_EP, TACHES)  # tâche réservée, autre orthographe
        with self.assertRaises(R.ReserveRefusee):
            R.verifier_disjonction(m2 + [{"identifiant": "t001/e1", "tache": "autre"}], T_EP, TACHES)  # épisode de T servi sans sa tâche

    def test_v60_reexportee(self):
        self.assertTrue(callable(R.reserver) and callable(R.verifier_reserve) and R.MODULE == 3)


if __name__ == "__main__":
    unittest.main()
