"""Essais de la v61 — lecture gelée du tour fermé (`pole/lecture_tour_ferme_v61.py`), corrections C1 et C2 de la contre-lecture
(B3, B4, B5, I5). Hors ligne : relevés synthétiques, aucun modèle. Chaque critère : un cas sain et un artefact (R5)."""

import unittest

from pole import lecture_tour_ferme_v61 as L  # noqa: E402

TEMOINS = {"T-VRAIE": ("passe", True, "survit"), "T-F1": ("passe", False, None), "T-F2": ("passe", True, "éliminée"),
           "T-F4": ("passe", False, None), "T-ANTI": ("passe", False, None), "T-ELIM": ("passe", True, "éliminée"),
           "T-MAL": ("refuse", False, None)}


def carte(bras, g, i, promue=False, verdict=None, gain=-0.3, delta=-0.3, d=1.0, **kw):
    return dict({"bras": bras, "generation": g, "identifiant": f"{bras}-{g}-{i}", "temoin": None, "gardien": "passe",
                 "promue": promue, "verdict": verdict, "contre_calcul_ok": True if verdict else None, "gain_nat": gain,
                 "delta_gain_nat": delta, "divergence_nat": d}, **kw)


def releve_sain(ps_reel=(6, 3, 3), ps_alea=4, recopie=(2, 3), info_reel=None):
    cartes = []
    jouees = {"reel": [1, 2, 3], "aleatoire": [1, 2, 3], "recopie_melange": list(recopie)}
    for b, gens in jouees.items():
        for g in gens:
            for t, (gard, pr, v) in TEMOINS.items():
                cartes.append({"bras": b, "generation": g, "identifiant": f"{b}-{g}-{t}", "temoin": t, "gardien": gard,
                               "promue": pr, "verdict": v, "contre_calcul_ok": True if v else None})
    for g, n_ps in zip((1, 2, 3), ps_reel):
        cartes += [carte("reel", g, i, True, "survit", 0.3, 0.3 if g == 1 else 0.05, 0.2) for i in range(n_ps)]
        n_info = (info_reel or (0, 0, 0))[g - 1]
        cartes += [carte("reel", g, 200 + i, False, None, 0.3, 0.3, 0.2) for i in range(n_info)]
        cartes += [carte("reel", g, 100 + i) for i in range(12 - n_ps - n_info)]
    for g in (1, 2, 3):
        k = ps_alea if g == 1 else 0
        cartes += [carte("aleatoire", g, i, True, "survit", 0.2, 0.2, 0.4) for i in range(k)]
        cartes += [carte("aleatoire", g, 100 + i) for i in range(12 - k)]
    for g in recopie:
        cartes += [carte("recopie_melange", g, i, gain=0.3, delta=-0.01, d=0.2) for i in range(6)]
    lectures = [{"bras": b, "generation": g, "attendu": "a" * 64, "lu": "a" * 64} for b, gens in jouees.items() for g in gens if g >= 2]
    return {"etage": 1, "arret": None, "cartes": cartes, "generations_jouees": jouees,
            "boucle": {"incidents": [], "lectures": lectures}}


class Etage1(unittest.TestCase):
    def test_sain_tient_et_discrimine(self):
        r = L.lire_etage1(releve_sain())
        self.assertEqual(r["issue_etage_1"], "tient", r["criteres"])
        self.assertEqual((r["passes_attendues"], r["lectures_attendues"]), (8, 6))
        self.assertEqual(r["issue_a4"], "discrimine")
        self.assertIsNone(r["cause_a4"])
        self.assertGreater(r["newcombe_ps_reel_moins_aleatoire"][0], 0)
        self.assertIsNotNone(r["newcombe_ps_generation_1_seule"])

    def modifier(self, f, **kw):
        rel = releve_sain(**kw)
        f(rel)
        return L.lire_etage1(rel)

    def test_B4_recopie_en_generation_3_seule_sept_passes_tient(self):
        r = L.lire_etage1(releve_sain(recopie=(3,)))
        self.assertEqual(r["passes_attendues"], 7)
        self.assertTrue(r["criteres"]["T2"] and r["criteres"]["T3"], r["criteres"])
        self.assertEqual(r["issue_etage_1"], "tient")

    def test_T1_lectures_manquantes_ou_fausses(self):
        self.assertFalse(self.modifier(lambda rel: rel["boucle"]["lectures"].pop())["criteres"]["T1"])
        self.assertFalse(self.modifier(lambda rel: rel["boucle"]["lectures"][0].update(lu="b" * 64))["criteres"]["T1"])
        self.assertFalse(self.modifier(lambda rel: rel["boucle"]["incidents"].append("HeritageRefuse"))["criteres"]["T1"])
        self.assertFalse(self.modifier(lambda rel: rel.update(arret="plafond"))["criteres"]["T1"])

    def test_T2_passes_comptees_sur_le_journal(self):
        def f(rel):
            next(c for c in rel["cartes"] if c["temoin"] == "T-VRAIE")["verdict"] = "non concluant"
        self.assertTrue(self.modifier(f)["criteres"]["T2"])

        def h(rel):
            for c in [c for c in rel["cartes"] if c["temoin"] == "T-VRAIE"][:2]:
                c["verdict"] = "non concluant"
        self.assertFalse(self.modifier(h)["criteres"]["T2"])

        def e(rel):
            next(c for c in rel["cartes"] if c["temoin"] == "T-VRAIE")["verdict"] = "éliminée"
        self.assertFalse(self.modifier(e)["criteres"]["T2"])

        def manque(rel):
            rel["cartes"].remove(next(c for c in rel["cartes"] if c["temoin"] == "T-VRAIE"))
        self.assertFalse(self.modifier(manque)["criteres"]["T2"])

    def test_T3_I5_elim_non_teste_et_mal_absent(self):
        def f(rel):
            for c in [c for c in rel["cartes"] if c["temoin"] == "T-ELIM"][:2]:
                c.update(promue=False, verdict=None)
        self.assertFalse(self.modifier(f)["criteres"]["T3"])

        def un(rel):
            next(c for c in rel["cartes"] if c["temoin"] == "T-ELIM").update(verdict="non concluant")
        self.assertTrue(self.modifier(un)["criteres"]["T3"])

        def g(rel):
            rel["cartes"].remove(next(c for c in rel["cartes"] if c["temoin"] == "T-MAL"))
        self.assertFalse(self.modifier(g)["criteres"]["T3"])

        def h(rel):
            next(c for c in rel["cartes"] if c["temoin"] == "T-MAL")["gardien"] = "passe"
        self.assertFalse(self.modifier(h)["criteres"]["T3"])

        def faux(rel):
            for c in [c for c in rel["cartes"] if c["temoin"] == "T-F2"][:2]:
                c["verdict"] = "survit"
        self.assertFalse(self.modifier(faux)["criteres"]["T3"])

    def test_T4_reunis_et_par_bras(self):
        def f(rel):  # 2 « non concluant » sur 6 testées au bras recopie : 0,33 > 0,20 du bras, mais ≤ 0,40 du bras et 2/40 réunis
            for c in [c for c in rel["cartes"] if c["bras"] == "recopie_melange" and c["verdict"]][:2]:
                c["verdict"] = "non concluant"
        self.assertTrue(self.modifier(f)["criteres"]["T4"])

        def g(rel):  # 4 sur 6 au bras recopie : 0,67 > 0,40 du bras (réunis 4/40 = 0,10)
            for c in [c for c in rel["cartes"] if c["bras"] == "recopie_melange" and c["verdict"]][:4]:
                c["verdict"] = "non concluant"
        self.assertFalse(self.modifier(g)["criteres"]["T4"])

        def h(rel):  # 5 sur 21 au réel (0,24) et 4 sur 13 à l'aléatoire (0,31) : chaque bras ≤ 0,40, réunis 9/40 = 0,225 > 0,20
            for c in [c for c in rel["cartes"] if c["bras"] == "reel" and c["verdict"] == "survit"][:5]:
                c["verdict"] = "non concluant"
            for c in [c for c in rel["cartes"] if c["bras"] == "aleatoire" and c["verdict"] == "survit"][:4]:
                c["verdict"] = "non concluant"
        self.assertFalse(self.modifier(h)["criteres"]["T4"])

        def d(rel):
            next(c for c in rel["cartes"] if c["verdict"] == "survit")["contre_calcul_ok"] = False
        self.assertFalse(self.modifier(d)["criteres"]["T4"])

    def test_B5_contre_calcul_absent_releve_invalide(self):
        rel = releve_sain()
        next(c for c in rel["cartes"] if c["verdict"] == "survit" and not c["temoin"])["contre_calcul_ok"] = None
        with self.assertRaises(L.ReleveInvalide):
            L.lire_etage1(rel)
        r = L.lire_tour(rel, None)
        self.assertTrue(r["etage_1"]["issue_etage_1"].startswith("ne tient pas"))
        self.assertEqual((r["etage_2"]["issue_a3"], r["etage_2"]["n"]), ("N", "N1"))

    def test_T5_fausses_decouvertes_du_hasard(self):
        def f(rel):
            for c in [c for c in rel["cartes"] if c["bras"] == "aleatoire" and c["verdict"] == "survit" and not c["temoin"]][:2]:
                c["gain_nat"] = 0.01
        r = self.modifier(f)
        self.assertFalse(r["criteres"]["T5"])
        self.assertEqual(r["issue_a4"], "la chaîne ne discrimine pas")

    def test_B3_cause_lue_a_l_oracle(self):
        r = L.lire_etage1(releve_sain(ps_reel=(3, 1, 1)))
        self.assertEqual(r["issue_etage_1"], "tient")
        self.assertEqual(r["issue_a4"], L.A4_EGAL)
        self.assertEqual(r["cause_a4"], L.A4_TAILLE)
        self.assertTrue(r["reserve_majeure_pour_a3"])
        r2 = L.lire_etage1(releve_sain(ps_reel=(3, 1, 1), info_reel=(8, 8, 8)))
        self.assertEqual(r2["issue_a4"], L.A4_EGAL)
        self.assertEqual(r2["cause_a4"], L.A4_SENSIBILITE)
        self.assertGreater(r2["newcombe_informatives_reel_moins_aleatoire"][0], 0)
        self.assertNotIn("ne battent pas", r2["issue_a4"] + str(r2["cause_a4"]))

    def test_releve_sans_generations_jouees_refuse(self):
        rel = releve_sain()
        del rel["generations_jouees"]
        with self.assertRaises(L.ReleveInvalide):
            L.lire_etage1(rel)


def releve2(reel_ps_g1=1, alea_ps=0):
    cartes = [dict(carte("reel", 1, i, True, "survit"), statistique=0.05, log_e=6.0) for i in range(reel_ps_g1)]
    cartes += [carte("reel", g, 100 + i) for g in (1, 2) for i in range(12)]
    cartes += [dict(carte("aleatoire", 1, i, True, "survit"), statistique=0.03, log_e=5.0) for i in range(alea_ps)]
    cartes += [carte("aleatoire", g, 100 + i) for g in (1, 2) for i in range(12)]
    return {"etage": 2, "arret": None, "cartes": cartes, "generations_jouees": {"reel": [1, 2], "aleatoire": [1, 2]},
            "boucle": {"incidents": [], "lectures": []}}


class Etage2(unittest.TestCase):
    def setUp(self):
        self.l1 = L.lire_etage1(releve_sain())

    def test_P_Z_et_N(self):
        self.assertEqual(L.lire_etage2(releve2(), self.l1)["issue_a3"], "P")
        self.assertEqual(L.lire_etage2(releve2(reel_ps_g1=0), self.l1)["issue_a3"], "Z")
        rel = releve_sain()
        rel["boucle"]["incidents"].append("x")
        r = L.lire_etage2(releve2(), L.lire_etage1(rel))
        self.assertEqual((r["issue_a3"], r["n"]), ("N", "N1"))

    def test_N2_contre_calcul_absent_ou_en_desaccord(self):
        rel = releve2()
        rel["cartes"][0]["contre_calcul_ok"] = None
        r = L.lire_etage2(rel, self.l1)
        self.assertEqual((r["issue_a3"], r["n"]), ("N", "N2"))
        rel = releve2()
        rel["cartes"][0]["contre_calcul_ok"] = False
        self.assertEqual(L.lire_etage2(rel, self.l1)["n"], "N2")

    def test_reserve_a_reprend_la_cause(self):
        l1 = L.lire_etage1(releve_sain(ps_reel=(3, 1, 1)))
        r = L.lire_etage2(releve2(alea_ps=1), l1)
        self.assertEqual([x[0] for x in r["reserves"]], ["a", "b"])
        self.assertIn(L.A4_TAILLE, r["reserves"][0][1])

    def test_generation_2_seule_n_est_pas_decisive(self):
        rel = releve2(reel_ps_g1=0)
        rel["cartes"].append(dict(carte("reel", 2, 999, True, "survit"), statistique=0.05, log_e=6.0))
        r = L.lire_etage2(rel, self.l1)
        self.assertEqual((r["issue_a3"], r["survivantes_sur_T_relue_generation_2"]), ("Z", ["reel-2-999"]))


if __name__ == "__main__":
    unittest.main()
