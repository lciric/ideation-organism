"""Essais de la v60 — lecture gelée du tour fermé (`pole/lecture_tour_ferme_v60.py`). Préenregistrement
`prereg/preenregistrement-tour-ferme-v1-brouillon1.md`, sections 4.6, 4.7, 5.6 et 6.

Hors ligne : relevés synthétiques, aucun modèle. Chaque critère : un cas sain et un artefact (R5)."""

import copy
import unittest

from pole import lecture_tour_ferme_v60 as L  # noqa: E402

TEMOINS = {"T-VRAIE": ("passe", True, "survit"), "T-F1": ("passe", False, None), "T-F2": ("passe", True, "éliminée"),
           "T-F4": ("passe", False, None), "T-ANTI": ("passe", False, None), "T-ELIM": ("passe", True, "éliminée"),
           "T-MAL": ("refuse", False, None)}


def carte(bras, g, i, promue=False, verdict=None, gain=-0.3, delta=-0.3, d=1.0, **kw):
    return dict({"bras": bras, "generation": g, "identifiant": f"{bras}-{g}-{i}", "temoin": None, "gardien": "passe",
                 "promue": promue, "verdict": verdict, "contre_calcul_ok": True if verdict else None, "gain_nat": gain,
                 "delta_gain_nat": delta, "divergence_nat": d}, **kw)


def releve_sain(ps_reel=(6, 3, 3), ps_alea=4):
    cartes = []
    for b, gens in (("reel", (1, 2, 3)), ("aleatoire", (1, 2, 3)), ("recopie_melange", (2, 3))):
        for g in gens:
            for t, (gard, pr, v) in TEMOINS.items():
                cartes.append({"bras": b, "generation": g, "identifiant": f"{b}-{g}-{t}", "temoin": t, "gardien": gard,
                               "promue": pr, "verdict": v, "contre_calcul_ok": True if v else None})
    for g, n_ps in zip((1, 2, 3), ps_reel):
        cartes += [carte("reel", g, i, True, "survit", 0.3, 0.3 if g == 1 else 0.05, 0.2) for i in range(n_ps)]
        cartes += [carte("reel", g, 100 + i) for i in range(12 - n_ps)]
    for g in (1, 2, 3):
        k = ps_alea if g == 1 else 0
        cartes += [carte("aleatoire", g, i, True, "survit", 0.2, 0.2, 0.4) for i in range(k)]
        cartes += [carte("aleatoire", g, 100 + i) for i in range(12 - k)]
    for g in (2, 3):
        cartes += [carte("recopie_melange", g, i, gain=0.3, delta=-0.01, d=0.2) for i in range(6)]
    return {"etage": 1, "arret": None, "cartes": cartes,
            "boucle": {"incidents": [], "lectures": [{"attendu": "a" * 64, "lu": "a" * 64}] * 6}}


class Etage1(unittest.TestCase):
    def test_sain_tient_et_discrimine(self):
        r = L.lire_etage1(releve_sain())
        self.assertEqual(r["issue_etage_1"], "tient", r["criteres"])
        self.assertEqual(r["issue_a4"], "discrimine")
        self.assertFalse(r["reserve_majeure_pour_a3"])
        self.assertEqual((r["bras"]["reel"]["ps"], r["bras"]["aleatoire"]["ps"]), (12, 4))
        self.assertGreater(r["newcombe_ps_reel_moins_aleatoire"][0], 0)
        self.assertTrue(r["predictions"]["P1"] and r["predictions"]["P2"] and r["predictions"]["P5"])

    def modifier(self, f):
        rel = releve_sain()
        f(rel)
        return L.lire_etage1(rel)

    def test_T1_incident_de_boucle(self):
        r = self.modifier(lambda rel: rel["boucle"]["incidents"].append("SelectionNonVerifiee"))
        self.assertEqual(r["issue_etage_1"], "ne tient pas (T1)")
        r = self.modifier(lambda rel: rel["boucle"]["lectures"].append({"attendu": "a" * 64, "lu": "b" * 64}))
        self.assertFalse(r["criteres"]["T1"])

    def test_T2_loi_plantee_eliminee(self):
        def f(rel):
            next(c for c in rel["cartes"] if c["temoin"] == "T-VRAIE")["verdict"] = "éliminée"
        self.assertFalse(self.modifier(f)["criteres"]["T2"])

        def g(rel):
            next(c for c in rel["cartes"] if c["temoin"] == "T-VRAIE")["verdict"] = "non concluant"
        self.assertTrue(self.modifier(g)["criteres"]["T2"])  # une passe perdue sur 8 : tolérée

        def h(rel):
            for c in [c for c in rel["cartes"] if c["temoin"] == "T-VRAIE"][:2]:
                c["verdict"] = "non concluant"
        self.assertFalse(self.modifier(h)["criteres"]["T2"])  # deux passes perdues : refus, même sans « éliminée »

    def test_T3_temoins_faux_retenus_ou_carte_mal_formee_passee(self):
        def f(rel):
            for c in [c for c in rel["cartes"] if c["temoin"] == "T-F2"][:2]:
                c["verdict"] = "survit"
        self.assertFalse(self.modifier(f)["criteres"]["T3"])

        def g(rel):
            next(c for c in rel["cartes"] if c["temoin"] == "T-MAL")["gardien"] = "passe"
        self.assertFalse(self.modifier(g)["criteres"]["T3"])

    def test_T4_non_concluant_et_contre_calcul(self):
        def f(rel):
            for c in [c for c in rel["cartes"] if c["bras"] == "reel" and c["verdict"] == "survit" and not c["temoin"]][:5]:
                c["verdict"] = "non concluant"
        self.assertFalse(self.modifier(f)["criteres"]["T4"])

        def g(rel):
            next(c for c in rel["cartes"] if c["verdict"] == "survit")["contre_calcul_ok"] = False
        self.assertFalse(self.modifier(g)["criteres"]["T4"])

    def test_T5_fausses_decouvertes_du_hasard(self):
        def f(rel):
            for c in [c for c in rel["cartes"] if c["bras"] == "aleatoire" and c["verdict"] == "survit"
                      and not c["temoin"]][:2]:
                c["gain_nat"] = 0.01
        r = self.modifier(f)
        self.assertFalse(r["criteres"]["T5"])
        self.assertEqual(r["issue_a4"], "la chaîne ne discrimine pas")

    def test_proposeurs_reels_pas_meilleurs_que_le_hasard(self):
        r = L.lire_etage1(releve_sain(ps_reel=(3, 1, 1)))
        self.assertEqual(r["issue_etage_1"], "tient")
        self.assertTrue(r["issue_a4"].startswith("la chaîne écarte"))
        self.assertTrue(r["reserve_majeure_pour_a3"])

    def test_S1_trop_beau(self):
        rel = releve_sain()
        next(c for c in rel["cartes"] if c["bras"] == "reel" and c["generation"] == 1 and c["verdict"] == "survit"
             and not c["temoin"])["divergence_nat"] = 0.01
        self.assertTrue(L.lire_etage1(rel)["audits"]["S1_trop_beau"])
        self.assertFalse(L.lire_etage1(releve_sain())["audits"]["S1_trop_beau"])

    def test_releve_mal_forme_refuse(self):
        rel = releve_sain()
        rel["cartes"][0]["bras"] = "inconnu"
        with self.assertRaises(L.ReleveInvalide):
            L.lire_etage1(rel)


def releve2(reel_ps_g1=1, alea_ps=0, **kw):
    cartes = [dict(carte("reel", 1, i, True, "survit", **kw), statistique=0.05, log_e=6.0) for i in range(reel_ps_g1)]
    cartes += [carte("reel", g, 100 + i) for g in (1, 2) for i in range(12)]
    cartes += [dict(carte("aleatoire", 1, i, True, "survit"), statistique=0.03, log_e=5.0) for i in range(alea_ps)]
    cartes += [carte("aleatoire", g, 100 + i) for g in (1, 2) for i in range(12)]
    return {"etage": 2, "arret": None, "cartes": cartes, "boucle": {"incidents": [], "lectures": []}}


class Etage2(unittest.TestCase):
    def setUp(self):
        self.l1 = L.lire_etage1(releve_sain())

    def test_promotion_P_et_zero_Z(self):
        r = L.lire_etage2(releve2(), self.l1)
        self.assertEqual(r["issue_a3"], "P")
        self.assertEqual(r["reserves"], [])
        self.assertEqual(L.lire_etage2(releve2(reel_ps_g1=0), self.l1)["issue_a3"], "Z")

    def test_non_jugee_si_l_etage_1_ne_tient_pas(self):
        rel = releve_sain()
        rel["boucle"]["incidents"].append("x")
        r = L.lire_etage2(releve2(), L.lire_etage1(rel))
        self.assertEqual(r["issue_a3"], "N")

    def test_non_jugee_si_trop_de_non_concluant(self):
        rel = releve2(reel_ps_g1=0)
        for c in rel["cartes"][:4]:
            c.update(promue=True, verdict="non concluant")
        self.assertEqual(L.lire_etage2(rel, self.l1)["issue_a3"], "N")

    def test_reserves_automatiques(self):
        l1 = L.lire_etage1(releve_sain(ps_reel=(3, 1, 1)))
        r = L.lire_etage2(releve2(alea_ps=1), l1)
        self.assertEqual([x[0] for x in r["reserves"]], ["a", "b"])

    def test_contre_calcul_en_desaccord_ne_compte_pas(self):
        rel = releve2()
        rel["cartes"][0]["contre_calcul_ok"] = False
        self.assertEqual(L.lire_etage2(rel, self.l1)["issue_a3"], "N")

    def test_generation_2_seule_n_est_pas_decisive(self):
        rel = releve2(reel_ps_g1=0)
        rel["cartes"].append(dict(carte("reel", 2, 999, True, "survit"), statistique=0.05, log_e=6.0))
        r = L.lire_etage2(rel, self.l1)
        self.assertEqual(r["issue_a3"], "Z")
        self.assertEqual(r["survivantes_sur_T_relue_generation_2"], ["reel-2-999"])

    def test_contre_calcul_absent_ne_compte_pas(self):
        rel = releve2()
        rel["cartes"][0]["contre_calcul_ok"] = None
        self.assertEqual(L.lire_etage2(rel, self.l1)["issue_a3"], "Z")

    def test_S3_trop_beau(self):
        rel = releve2()
        rel["cartes"][0]["statistique"] = 0.5
        self.assertTrue(L.lire_etage2(rel, self.l1)["audits"]["S3"])
        self.assertFalse(L.lire_etage2(releve2(), self.l1)["audits"]["S3"])


if __name__ == "__main__":
    unittest.main()
