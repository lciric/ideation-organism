"""Essais de la lecture gelée v65 (pièce M5) : chaque issue C1 à C6 et chaque audit A1 à A4 essayés sur un cas sain (le relevé
d'une course à blanc, issue C1) et sur un artefact (le même relevé altéré pour porter la condition), R5 ; ordre gelé des
critères ; un arrêt ne masque jamais une brèche. Aucun réseau, aucun appel de modèle.

  python3 -I -B -m pytest -q -p no:cacheprovider essais/test_lecture_boucle_reelle_v65.py
"""

import copy
import importlib.util
import os
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import lecture_boucle_reelle_v65 as L  # noqa: E402

_spec = importlib.util.spec_from_file_location("essais_boucle_reelle_v65_pour_lecture", os.path.join(ICI, "test_boucle_reelle_v65.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
_SAIN = []


def sain():
    if not _SAIN:
        _SAIN.append(E.jouer(tempfile.mkdtemp(prefix="lecture-v65-"))[0])
    return copy.deepcopy(_SAIN[0])


def _p(r, nom, generation=None, copie=False):
    return next(p for p in r["plantees"] if p["nom"] == nom and (generation is None or p["generation"] == generation)
                and bool(p["source"]) == copie)


class Issues(unittest.TestCase):
    def test_C1_sain(self):
        lu = L.lire_criteres(sain())
        self.assertEqual(lu["code"], "C1")
        self.assertTrue(lu["constats"]["p1"] and lu["constats"]["p4"] and lu["constats"]["p6_tenue"])
        self.assertEqual(lu["aussi"], [])

    def test_C5_arret(self):
        r = sain()
        r["arret"], r["complet"] = "ArretTour : part du relais kimi franchie", False
        lu = L.lire_criteres(r)
        self.assertEqual((lu["code"], lu["aussi"]), ("C5", []))

    def test_C5_ne_masque_pas_une_breche(self):
        r = sain()
        r["arret"], r["complet"] = "ArretTour : x", False
        _p(r, "F2", 1)["promue"] = True
        self.assertEqual(L.lire_criteres(r)["aussi"], ["C2 (partielle)"])
        r = sain()
        r["arret"], r["complet"] = "ArretTour : x", False
        _p(r, "C1", 2, True)["promue"] = True
        self.assertEqual(L.lire_criteres(r)["aussi"], ["C4 (partielle)"])
        r = sain()
        r["complet"] = False  # relevé incomplet sans motif : C5 aussi
        self.assertEqual(L.lire_criteres(r)["code"], "C5")

    def test_C4_copie_promue(self):
        r = sain()
        _p(r, "C2", 2, True)["promue"] = True
        self.assertEqual(L.lire_criteres(r)["code"], "C4")

    def test_C4_lecture_de_selection(self):
        cas = {"empreinte": lambda r: r["lecture_selection"].__setitem__("lu", "0" * 64),
               "vue": lambda r: r["lecture_selection"].__setitem__("vue", r["lecture_selection"]["vue"][1:]),
               "membres des cartes": lambda r: next(c for c in r["cartes"] if c["generation"] == 2 and c["gardien"] == "passe").__setitem__("membres_d_archive", 4),
               "membres des plantées": lambda r: _p(r, "F3", 2).__setitem__("membres_d_archive", 0),
               "copie non retenue": lambda r: r["lecture_selection"]["copies"].append({"nom": "C9", "source": "F-000000000000"}),
               "retenues lues": lambda r: r["lecture_selection"].__setitem__("retenues_lues", [])}
        for nom, f in cas.items():
            with self.subTest(nom):
                r = sain()
                f(r)
                self.assertEqual(L.lire_criteres(r)["code"], "C4")

    def test_C4_prime_sur_C2(self):
        r = sain()
        _p(r, "F1", 1)["promue"] = True
        r["lecture_selection"]["lu"] = "0" * 64
        self.assertEqual(L.lire_criteres(r)["code"], "C4")

    def test_C2_fausse_promue(self):
        for g in (1, 2):
            with self.subTest(generation=g):
                r = sain()
                _p(r, "F4", g)["promue"] = True
                lu = L.lire_criteres(r)
                self.assertEqual(lu["code"], "C2")
                self.assertFalse(lu["constats"]["p1"])

    def test_C3_sans_dents(self):
        r = sain()
        for n in L.VRAIES:
            _p(r, n, 1)["promue"] = False
        self.assertEqual(L.lire_criteres(r)["code"], "C3")
        r = sain()
        for n in L.VRAIES:
            _p(r, n, 1)["verdict"] = "non concluant"
        self.assertEqual(L.lire_criteres(r)["code"], "C3")

    def test_C6_instrument(self):
        cas = {"T-ELIM survivante": lambda r: _p(r, "T-ELIM").__setitem__("verdict", "survit"),
               "T-ELIM non promue": lambda r: _p(r, "T-ELIM").__setitem__("promue", False),
               "T-MAL jugée": lambda r: _p(r, "T-MAL").__setitem__("gardien", "passe")}
        for nom, f in cas.items():
            with self.subTest(nom):
                r = sain()
                f(r)
                self.assertEqual(L.lire_criteres(r)["code"], "C6")

    def test_C3_prime_sur_C6(self):
        r = sain()
        for n in L.VRAIES:
            _p(r, n, 1)["promue"] = False
        _p(r, "T-ELIM")["verdict"] = "survit"
        self.assertEqual(L.lire_criteres(r)["code"], "C3")

    def test_releve_d_une_autre_version(self):
        r = sain()
        r["version"] = "tour-ferme-v64"
        with self.assertRaises(L.ReleveInvalide):
            L.lire_criteres(r)
        r = sain()
        del r["plantees"][0]["membres_d_archive"]
        with self.assertRaises(L.ReleveInvalide):
            L.lire_criteres(r)


class Audits(unittest.TestCase):
    def test_A1_d_office_sous_C1(self):
        r = sain()
        a = L.audits(r, L.lire_criteres(r))
        self.assertEqual(a["A1"]["declenche"], "d'office (issue C1)")
        self.assertTrue(a["A1"]["vraies_survivantes_membres_justes"] and a["A1"]["fausses_log_w_max_au_plus_0"]
                        and a["A1"]["vue_g2_sans_loi_plantee"] and a["A1"]["contre_calcul_egal"])
        self.assertFalse(a["A1"]["bac_reel_partout"])  # course à blanc : exécuteur factice, dit
        self.assertIsNone(a["A2"])
        self.assertIsNone(a["A3"])
        self.assertIsNone(a["A4"])

    def test_A1_artefacts(self):
        r = sain()
        _p(r, "V1", 1)["membres_d_archive"] = 0
        _p(r, "F1", 1)["log_richesse_max"] = 0.5
        r["lecture_selection"]["vue"].append("V2")
        r["lecture_selection"]["vue_attendue"].append("V2")
        a = L.audits(r, L.lire_criteres(r))["A1"]
        self.assertFalse(a["vraies_survivantes_membres_justes"])
        self.assertFalse(a["fausses_log_w_max_au_plus_0"])
        self.assertFalse(a["vue_g2_sans_loi_plantee"])

    def test_A2_fausse_promue(self):
        r = sain()
        f = _p(r, "F2", 1)
        f["promue"], f["membres_d_archive"] = True, 0
        a = L.audits(r, L.lire_criteres(r))["A2"]
        self.assertEqual(a["lois"][0]["diagnostic"], "jugée sans archive : défaut de chaîne")
        r = sain()
        _p(r, "F3", 2)["promue"] = True
        self.assertEqual(L.audits(r, L.lire_criteres(r))["A2"]["lois"][0]["diagnostic"], "membre du nul promu : défaut numérique")

    def test_A2_rejeu_dans_la_lecture(self):
        r = sain()
        _p(r, "F1", 1)["promue"] = True
        n = L.N_REJEU_A2
        try:
            L.N_REJEU_A2 = 2
            lu = L.lire_boucle(r, A.charger_monde(RACINE))
        finally:
            L.N_REJEU_A2 = n
        self.assertEqual(lu["code"], "C2")
        self.assertEqual(lu["audits"]["A2"]["lois"][0]["rejeu"], {"promues": 0, "n": 2, "membres_d_archive": [4]})

    def test_A2_rejeu(self):
        m = A.charger_monde(RACINE)
        x = L.rejouer_a2(E.JEU["fausses"]["F1"], m, E.JEU["archive_de_depart"], 20261110, n=3)
        self.assertEqual((x["promues"], x["n"], x["membres_d_archive"]), (0, 3, [4]))

    def test_A3_sans_dents(self):
        r = sain()
        _p(r, "V1", 1)["promue"] = False
        for n in ("V2", "V3", "V4"):
            _p(r, n, 1)["promue"], _p(r, n, 1)["verdict"] = True, "éliminée"
        a = L.audits(r, L.lire_criteres(r))["A3"]
        self.assertEqual(a["vraies"]["V1"], "non promue")
        self.assertEqual(a["vraies"]["V2"], "promue non survivante")

    def test_A4_copie_promue(self):
        r = sain()
        _p(r, "C1", 2, True)["promue"] = True
        a = L.audits(r, L.lire_criteres(r))["A4"]
        self.assertTrue(a["copies"][0]["promue"])
        self.assertTrue(all(c["source_retenue"] for c in a["copies"]))


class Oracle(unittest.TestCase):
    def test_mesures_et_fausse_decouverte_en_tete(self):
        m = A.charger_monde(RACINE)
        r = sain()
        o = L.mesures_oracle(r, m)
        self.assertEqual(o["fausses_decouvertes_reelles"], [])
        self.assertEqual(sum(f["proposees"] for f in o["par_fournisseur"].values()), len(r["cartes"]))
        c = next(c for c in r["cartes"] if c["generation"] == 1 and c["promue"])
        c["loi"], c["verdict"] = E.JEU["fausses"]["F2"], "survit"  # une carte réelle qui n'apporte rien au-delà de {K1}
        o = L.mesures_oracle(r, m)
        self.assertEqual(len(o["fausses_decouvertes_reelles"]), 1)
        self.assertEqual(o["fausses_decouvertes_reelles"][0]["forme"], "mélange")

    def test_lire_boucle_phrase_apres_audits(self):
        lu = L.lire_boucle(sain())
        self.assertEqual(list(lu)[:2], ["version", "audits"])
        self.assertTrue(lu["phrase"].startswith("Issue C1"))


if __name__ == "__main__":
    unittest.main()
