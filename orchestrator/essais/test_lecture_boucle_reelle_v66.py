"""Essais de la lecture gelée v66 (`pole/lecture_boucle_reelle_v66.py`) : chaque issue C1 à C6 et chaque audit A1 à A4 sur un cas
sain (le relevé d'une course à blanc v66, issue C1) et sur un artefact (le même relevé altéré), R5 ; ordre gelé des critères ;
**complétude exigée** (CLV65-01) : chaque relevé artefact de la contre-lecture (fausses refusées au gardien, absentes, copies
manquantes, génération 2 absente, aucun étage) se lit C5 ; un arrêt ne masque jamais une brèche (CLV65-02) ; vue servie
(CLV65-03) ; mesures sans issue (CLV65-08). Aucun réseau, aucun appel de modèle.

  python3 -I -B -m pytest -q -p no:cacheprovider essais/test_lecture_boucle_reelle_v66.py
"""

import copy
import importlib.util
import os
import sys
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import lecture_boucle_reelle_v66 as L  # noqa: E402

_spec = importlib.util.spec_from_file_location("essais_boucle_reelle_v66_pour_lecture", os.path.join(ICI, "test_boucle_reelle_v66.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)


def sain():
    return E.Course.releve()


def _p(r, nom, generation=None, copie=False):
    return next(p for p in r["plantees"] if p["nom"] == nom and (generation is None or p["generation"] == generation)
                and bool(p["source"]) == copie)


def _code(r):
    return L.lire_criteres(r)["code"]


class Issues(unittest.TestCase):
    def test_C1_sain(self):
        lu = L.lire_criteres(sain())
        self.assertEqual(lu["code"], "C1")
        self.assertTrue(lu["constats"]["p1"] and lu["constats"]["p4"] and lu["constats"]["p6_tenue"])
        self.assertEqual((lu["aussi"], lu["constats"]["manques"]), ([], []))

    def test_C5_arret(self):
        r = sain()
        r["arret"], r["complet"] = "ArretTour : part du relais kimi franchie", False
        lu = L.lire_criteres(r)
        self.assertEqual((lu["code"], lu["aussi"]), ("C5", []))
        self.assertIn("arrêt", lu["constats"]["cause_c5"])

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
        r["arret"], r["complet"] = "ArretTour : x", False
        r["lecture_selection"]["lu"] = "0" * 64
        self.assertEqual(L.lire_criteres(r)["aussi"], ["C4 (partielle)"])
        r = sain()
        r["complet"] = False  # relevé incomplet sans motif : C5 aussi
        self.assertEqual(_code(r), "C5")

    def test_C5_releve_incomplet_artefacts_de_la_contre_lecture(self):
        def refusees_au_gardien(r):
            for n in L.FAUSSES:
                p = _p(r, n, 1)
                p.update(gardien="refuse", promue=False, membres_d_archive=None, log_richesse_max=None)

        def absentes(generations):
            return lambda r: r.__setitem__("plantees", [p for p in r["plantees"] if not (p["nom"] in L.FAUSSES and p["generation"] in generations)])
        cas = {"F1 à F4 refusées au gardien, jamais jugées": refusees_au_gardien,
               "F1 à F4 absentes de la génération 2": absentes((2,)),
               "F1 à F4 absentes des deux générations": absentes((1, 2)),
               "aucune copie": lambda r: r.__setitem__("plantees", [p for p in r["plantees"] if not p["source"]]),
               "une seule copie": lambda r: r.__setitem__("plantees", [p for p in r["plantees"] if p["nom"] not in ("C2", "C3", "C4")]),
               "génération 2 absente": lambda r: r.__setitem__("generations_jouees", [1]),
               "aucun étage": lambda r: r.__setitem__("etages", []),
               "un étage seulement": lambda r: r.__setitem__("etages", r["etages"][:1]),
               "membres attendus absents": lambda r: r["membres_attendus"].pop("1"),
               "log W absent": lambda r: _p(r, "F3", 2).__setitem__("log_richesse_max", None),
               "F1 en double": lambda r: r["plantees"].append(copy.deepcopy(_p(r, "F1", 1))),
               "V2 absente": lambda r: r.__setitem__("plantees", [p for p in r["plantees"] if p["nom"] != "V2"]),
               "T-MAL absente": lambda r: r.__setitem__("plantees", [p for p in r["plantees"] if p["nom"] != "T-MAL"]),
               "V1 en génération 2": lambda r: r["plantees"].append(dict(copy.deepcopy(_p(r, "V1", 1)), generation=2)),
               "copie d'une carte non retenue": lambda r: _p(r, "C1", 2, True).__setitem__("source", "F-000000000000"),
               "fausse de la génération 1 jugée sans archive": lambda r: _p(r, "F1", 1).__setitem__("membres_d_archive", 0),
               "V3 passée mais non jugée": lambda r: _p(r, "V3", 1).__setitem__("log_richesse_max", None),
               "vue servie non consignée": lambda r: r["vues_servies"].pop("2"),
               "sélection finale non relue": lambda r: r.__setitem__("selection_finale", None)}
        for nom, f in cas.items():
            with self.subTest(nom):
                r = sain()
                f(r)
                lu = L.lire_criteres(r)
                self.assertEqual(lu["code"], "C5")
                self.assertTrue(lu["constats"]["manques"])
                self.assertIn("relevé incomplet", lu["constats"]["cause_c5"])

    def test_C4_copie_promue(self):
        r = sain()
        _p(r, "C2", 2, True)["promue"] = True
        self.assertEqual(_code(r), "C4")

    def test_C4_lecture_de_selection_et_vue_servie(self):
        def retenue_plantee(r):
            x = _p(r, "F1", 1)["identifiant_servi"]
            r["retenues"]["1"].append(x)
            r["vues_servies"]["2"]["identifiants"] = sorted(r["vues_servies"]["2"]["identifiants"] + [x])
            r["archives_de_jugement"]["2"][x] = _p(r, "F1", 1)["loi"]
            ls = r["lecture_selection"]
            for k in ("vue", "vue_attendue", "retenues_ecrites_g1", "retenues_lues"):
                ls[k] = sorted(ls[k] + [x])

        g2 = lambda r: next(c for c in r["cartes"] if c["generation"] == 2 and c["gardien"] == "passe")  # noqa: E731
        cas = {"empreinte": lambda r: r["lecture_selection"].__setitem__("lu", "0" * 64),
               "vue lue": lambda r: r["lecture_selection"].__setitem__("vue", r["lecture_selection"]["vue"][1:]),
               "vue servie en génération 2": lambda r: r["vues_servies"]["2"].__setitem__("identifiants", ["K1"]),
               "vue servie en génération 1": lambda r: r["vues_servies"]["1"].__setitem__("identifiants", []),
               "loi plantée servie": lambda r: r["vues_servies"]["1"].__setitem__("identifiants", ["K1", _p(r, "V1", 1)["identifiant_servi"]]),
               "archive de jugement de la génération 2": lambda r: r["archives_de_jugement"]["2"].pop("K1"),
               "membres des cartes": lambda r: g2(r).__setitem__("membres_d_archive", 4),
               "membres des plantées": lambda r: _p(r, "F3", 2).__setitem__("membres_d_archive", 0),
               "copie non retenue (lecture)": lambda r: r["lecture_selection"]["copies"].append({"nom": "C9", "source": "F-000000000000"}),
               "retenues lues": lambda r: r["lecture_selection"].__setitem__("retenues_lues", []),
               "incident de garde": lambda r: r["incidents"].append({"garde": 23, "generation": 2, "type": "VueServieRefusee", "motif": "x"}),
               "loi plantée retenue (et servie, de façon cohérente)": retenue_plantee}
        for nom, f in cas.items():
            with self.subTest(nom):
                r = sain()
                f(r)
                self.assertEqual(_code(r), "C4")

    def test_C4_heritage_refuse_sous_C5(self):
        r = sain()
        r["arret"], r["complet"] = "ArretTour : héritage refusé", False
        r["lecture_selection"] = {"attendu": "a" * 64, "lu": "b" * 64, "refus": {"type": "SelectionNonVerifiee", "motif": "x"},
                                  "retenues_ecrites_g1": r["retenues"]["1"]}
        lu = L.lire_criteres(r)
        self.assertEqual((lu["code"], lu["aussi"]), ("C5", ["C4 (partielle)"]))
        self.assertTrue(any("refusé" in e for e in lu["constats"]["ecarts_p6"]))
        self.assertTrue(any("empreinte lue" in e for e in lu["constats"]["ecarts_p6"]))

    def test_C4_prime_sur_C2(self):
        r = sain()
        _p(r, "F1", 1)["promue"] = True
        r["lecture_selection"]["lu"] = "0" * 64
        self.assertEqual(_code(r), "C4")

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
        self.assertEqual(_code(r), "C3")
        r = sain()
        for n in L.VRAIES:
            _p(r, n, 1)["verdict"] = "non concluant"
        self.assertEqual(_code(r), "C3")

    def test_C6_instrument(self):
        cas = {"T-ELIM survivante": lambda r: _p(r, "T-ELIM").__setitem__("verdict", "survit"),
               "T-ELIM non promue": lambda r: _p(r, "T-ELIM").__setitem__("promue", False),
               "T-MAL jugée": lambda r: _p(r, "T-MAL").update(gardien="passe", membres_d_archive=4, log_richesse_max=-1.0)}
        for nom, f in cas.items():
            with self.subTest(nom):
                r = sain()
                f(r)
                self.assertEqual(_code(r), "C6")

    def test_C3_prime_sur_C6(self):
        r = sain()
        for n in L.VRAIES:
            _p(r, n, 1)["promue"] = False
        _p(r, "T-ELIM")["verdict"] = "survit"
        self.assertEqual(_code(r), "C3")

    def test_releve_d_une_autre_version(self):
        r = sain()
        r["version"] = "boucle-reelle-v65"
        with self.assertRaises(L.ReleveInvalide):
            L.lire_criteres(r)
        for k in ("vues_servies", "incidents"):
            r = sain()
            del r[k]
            with self.subTest(k), self.assertRaises(L.ReleveInvalide):
                L.lire_criteres(r)
        r = sain()
        del r["plantees"][0]["log_richesse_max"]
        with self.assertRaises(L.ReleveInvalide):
            L.lire_criteres(r)


def _lecture_C1(r):
    return {"code": "C1", "constats": {"copies_promues": [], "ecarts_p6": []}}


class Audits(unittest.TestCase):
    def test_A1_d_office_sous_C1(self):
        r = sain()
        a = L.audits(r, L.lire_criteres(r))
        self.assertEqual(a["A1"]["declenche"], "d'office (issue C1)")
        self.assertTrue(a["A1"]["vraies_survivantes_membres_justes"] and a["A1"]["fausses_log_w_max_au_plus_0"]
                        and a["A1"]["vue_g2_sans_loi_plantee"] and a["A1"]["contre_calcul_egal"])
        self.assertFalse(a["A1"]["bac_reel_partout"])  # course à blanc : exécuteur factice, dit
        self.assertEqual((a["A2"], a["A3"], a["A4"]), (None, None, None))

    def test_A1_artefacts(self):
        cas = {"vraies_survivantes_membres_justes": lambda r: _p(r, "V1", 1).__setitem__("membres_d_archive", 0),
               "fausses_log_w_max_au_plus_0": lambda r: _p(r, "F1", 1).__setitem__("log_richesse_max", 0.5),
               "vue_g2_sans_loi_plantee": lambda r: r["vues_servies"]["2"]["identifiants"].append(_p(r, "F2", 2)["identifiant_servi"]),
               "contre_calcul_egal": lambda r: _p(r, "V1", 1).__setitem__("contre_calcul_ok", False)}
        for champ, f in cas.items():
            with self.subTest(champ):
                r = sain()
                f(r)
                self.assertFalse(L.audits(r, _lecture_C1(r))["A1"][champ])
        r = sain()
        _p(r, "F2", 2)["log_richesse_max"] = None  # un log W absent n'est jamais « ≤ 0 » (CLV65-01)
        self.assertFalse(L.audits(r, _lecture_C1(r))["A1"]["fausses_log_w_max_au_plus_0"])
        r = sain()
        _p(r, "V2", 1)["contre_calcul_ok"] = None  # testée sans contre-calcul : pas « égal »
        self.assertFalse(L.audits(r, _lecture_C1(r))["A1"]["contre_calcul_egal"])

    def test_A1_bac_reel_partout(self):
        r = sain()
        for e in r["etages"]:
            e["factice"] = False
        self.assertTrue(L.audits(r, _lecture_C1(r))["A1"]["bac_reel_partout"])
        r["etages"][1]["factice"] = True
        self.assertFalse(L.audits(r, _lecture_C1(r))["A1"]["bac_reel_partout"])
        r["etages"] = r["etages"][:1]
        r["etages"][0]["factice"] = False
        self.assertFalse(L.audits(r, _lecture_C1(r))["A1"]["bac_reel_partout"])

    def test_A2_fausse_promue(self):
        r = sain()
        f = _p(r, "F2", 1)
        f["promue"], f["membres_d_archive"] = True, 0
        a = L.audits(r, L.lire_criteres(r))["A2"]
        self.assertEqual(a["lois"][0]["diagnostic"], "jugée sans archive : défaut de chaîne")
        self.assertTrue(a["lois"][0]["membre_dominant_final"])
        r = sain()
        _p(r, "F3", 2)["promue"] = True
        self.assertEqual(L.audits(r, L.lire_criteres(r))["A2"]["lois"][0]["diagnostic"], "membre du nul promu : défaut numérique")
        r = sain()
        g = _p(r, "F4", 2)
        g["promue"], g["membres_d_archive"] = True, 4
        self.assertEqual(L.audits(r, L.lire_criteres(r))["A2"]["lois"][0]["diagnostic"], "membres d'archive en écart : défaut de chaîne")

    def test_A2_rejeu_dans_la_lecture(self):
        r = sain()
        _p(r, "F1", 1)["promue"] = True
        n = L.N_REJEU_A2
        try:
            L.N_REJEU_A2 = 2
            lu = L.lire_boucle(r, A.charger_monde(RACINE), "a-blanc (exploratoire)")
        finally:
            L.N_REJEU_A2 = n
        self.assertEqual(lu["code"], "C2")
        self.assertEqual(lu["audits"]["A2"]["lois"][0]["rejeu"], {"promues": 0, "n": 2, "membres_d_archive": [4]})

    def test_A3_sans_dents(self):
        r = sain()
        _p(r, "V1", 1)["promue"] = False
        for n in ("V2", "V3", "V4"):
            _p(r, n, 1)["promue"], _p(r, n, 1)["verdict"] = True, "éliminée"
        _p(r, "V3", 1)["verdict"] = "non concluant"
        a = L.audits(r, L.lire_criteres(r))["A3"]
        self.assertEqual((a["vraies"]["V1"], a["vraies"]["V2"], a["vraies"]["V3"]), ("non promue", "promue non survivante", "non concluante"))

    def test_A4_copie_promue_et_ecarts(self):
        r = sain()
        _p(r, "C1", 2, True)["promue"] = True
        a = L.audits(r, L.lire_criteres(r))["A4"]
        self.assertTrue(a["copies"][0]["promue"])
        self.assertTrue(all(c["source_retenue"] for c in a["copies"]))
        r = sain()
        r["lecture_selection"]["lu"] = "0" * 64
        self.assertTrue(L.audits(r, L.lire_criteres(r))["A4"]["ecarts_p6"])


class MesuresEtPhrase(unittest.TestCase):
    def test_wilson(self):
        self.assertIsNone(L.wilson(0, 0))
        lo, hi = L.wilson(6, 6)
        self.assertEqual(hi, 1.0)
        self.assertAlmostEqual(lo, 0.609666, places=5)
        lo, hi = L.wilson(0, 12)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.242494, places=5)

    def test_oracle_mesures_wilson_et_fausse_decouverte_en_tete(self):
        m = A.charger_monde(RACINE)
        r = sain()
        o = L.mesures_oracle(r, m)
        self.assertEqual(o["fausses_decouvertes_reelles"], [])
        self.assertEqual(sum(f["proposees"] for f in o["par_fournisseur"].values()), len(r["cartes"]))
        for f in o["par_fournisseur"].values():
            self.assertEqual(f["wilson_95"]["promues/proposees"], L.wilson(f["promues"], f["proposees"]))
        c = next(c for c in r["cartes"] if c["generation"] == 1 and c["promue"])
        c["loi"], c["verdict"] = E.JEU["fausses"]["F2"], "survit"  # une carte réelle qui n'apporte rien au-delà de {K1}
        lu = L.lire_boucle(r, m, "reel (decisif)")
        self.assertEqual(len(lu["oracle"]["fausses_decouvertes_reelles"]), 1)
        self.assertEqual(lu["oracle"]["fausses_decouvertes_reelles"][0]["forme"], "mélange")
        self.assertTrue(lu["phrase"].startswith("EN TÊTE : 1 fausse(s) découverte(s)"))

    def test_phrase_mode_oracle_et_ordre(self):
        lu = L.lire_boucle(sain(), None, "a-blanc (exploratoire)")
        self.assertEqual(list(lu)[:2], ["version", "audits"])
        self.assertTrue(lu["phrase"].startswith("Issue C1"))
        for mot in ("à blanc", "exécuteur factice", "oracle non lu"):
            self.assertIn(mot, lu["phrase"])
        self.assertIn("non lu", lu["oracle"])
        self.assertIn("jetons", lu["mesures_sans_issue"])
        self.assertIn("recherche_loi_plantee", lu["mesures_sans_issue"])


if __name__ == "__main__":
    unittest.main()
