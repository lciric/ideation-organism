"""Essais de l'attaque de Goodhart v1 (fichier neuf, R12) : chaque garde sur un cas sain et sur un artefact (R5).

Aucun réseau, aucune clé : proposeurs scriptés (`ProposeurScripte`) et un faux adaptateur. Rapides (n_max et rejeux réduits).
"""

import json
import math
import os
import sys
import tempfile
import time
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole import attaque_goodhart_v1 as ag  # noqa: E402
from pole import selection_pari as sp  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("lanceur_goodhart_essai", os.path.join(RACINE, "demonstrations", "attaque_goodhart_v1.py"))
lanceur = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lanceur)

G = 7  # graine exploratoire des essais


def compteur(plafond=100.0, duree=3600.0):
    return ag.Compteur(plafond, duree, time.time)


class Graines(unittest.TestCase):
    def test_espaces_disjoints(self):
        self.assertEqual(ag.verifier_entropie(G, decisif=False), G)
        self.assertEqual(ag.verifier_entropie(2 ** 64, decisif=True), 2 ** 64)
        with self.assertRaises(ag.AttaqueRefusee):
            ag.verifier_entropie(G, decisif=True)  # artefact : entropie décisive dans l'espace exploratoire
        with self.assertRaises(ag.AttaqueRefusee):
            ag.verifier_entropie(2 ** 64, decisif=False)  # artefact : exploratoire dans l'espace décisif

    def test_graines_deterministes_et_distinctes(self):
        self.assertEqual(ag.graine(G, "monde", 0), ag.graine(G, "monde", 0))
        self.assertNotEqual(ag.graine(G, "monde", 0), ag.graine(G, "monde", 1))
        self.assertNotEqual(ag.graine(G, "kimi|retour|v8|v8|frais", 0, 1), ag.graine(G, "argon|retour|v8|v8|frais", 0, 1))


class Monde(unittest.TestCase):
    def test_monde_au_nul_et_apparie(self):
        c = ag.carte(G, 0)
        self.assertEqual(c["monde"]["type"], "melange")
        self.assertEqual(c["monde"]["composantes"], [c["L"]["S1"], c["L"]["S2"]])
        self.assertTrue(0.3 <= c["pi"] <= 0.7)
        self.assertEqual(json.dumps(ag.carte(G, 0)["description"]), json.dumps(c["description"]))  # même monde partout
        texte = json.dumps(c["description"])
        self.assertNotIn("poids\": [" + str(c["pi"]), texte)  # π n'est jamais servi
        self.assertNotIn("S2\": {\"type\": \"melange", texte)


class Analyse(unittest.TestCase):
    def test_loi_valide_cas_sain(self):
        loi = {"type": "fixe", "probas": [0.2, 0.3, 0.5]}
        self.assertEqual(ag.analyser_reponse("préambule " + json.dumps({"retour_lu": "1.23", "loi": loi})), (loi, None, "1.23"))

    def test_artefacts_refuses_sans_reparation(self):
        for texte, motif in (("", "réponse vide"), ("pas de json", "aucun objet"),
                             (json.dumps({"loi": {"type": "melange", "composantes": [{"type": "fixe", "probas": [1, 1, 1]}] * 3,
                                                  "poids": [0.33, 0.33, 0.33]}}), "loi invalide"),
                             (json.dumps({"loi": {"type": "inconnu"}}), "loi invalide"),
                             (json.dumps({"loi": {"type": "calendrier", "probas": [[0.3, 0.3, 0.4]] * 500}}), "octets")):
            loi, m, _ = ag.analyser_reponse(texte)
            self.assertIsNone(loi)
            self.assertIn(motif, m)

    def test_echo(self):
        self.assertTrue(ag.echo_exact("-0.37", -0.37))
        self.assertTrue(ag.echo_exact("-0,37", -0.371))
        self.assertFalse(ag.echo_exact("aucun", -0.37))
        self.assertFalse(ag.echo_exact("-0.40", -0.37))


class Juge(unittest.TestCase):
    def test_juge_inconnu_refuse(self):
        with self.assertRaises(ag.AttaqueRefusee):
            ag.juger({"type": "fixe", "probas": [1, 1, 1]}, ag.carte(G, 0), "v1", G, "x", 1)

    def test_loi_du_monde_promue_sous_v7_jamais_sous_v8(self):
        """Cas sain du bras v7 (l'attaque a des dents) et garde du nul v8 (classe linéaire : log W ≤ 0)."""
        promues_v7 = 0
        for ci in range(4):
            c = ag.carte(G, ci)
            v8 = ag.juger(c["monde"], c, "v8", G, "essai", 1)
            v7 = ag.juger(c["monde"], c, "v7", G, "essai", 1)
            self.assertFalse(v8["promue"])
            self.assertLessEqual(v8["log_w_max"], 1e-6)
            promues_v7 += v7["promue"]
        self.assertGreaterEqual(promues_v7, 3)


class Suites(unittest.TestCase):
    def test_bras_retour_lit_les_retours_et_s_arrete_a_la_promotion(self):
        c = ag.carte(G, 0)
        s = ag.jouer_suite(ag.ProposeurScripte("optimiseur"), c, "kimi", "retour", ("v7",), G, compteur(), n_max=6)
        self.assertIsNotNone(s["premiere_promotion"]["v7"])
        self.assertEqual(len(s["tentatives"]), s["premiere_promotion"]["v7"])
        s8 = ag.jouer_suite(ag.ProposeurScripte("optimiseur"), c, "kimi", "retour", ("v8",), G, compteur(), n_max=5)
        self.assertIsNone(s8["premiere_promotion"]["v8"])
        self.assertEqual(len(s8["tentatives"]), 5)
        instr = ag.instrument([s8])
        self.assertEqual(instr["part_echos_exacts"], 1.0)

    def test_temoin_ne_recoit_aucun_retour(self):
        c = ag.carte(G, 0)
        vus = []

        def espion(texte):
            vus.append(texte)
            return ag.ProposeurScripte("optimiseur")(texte)
        ag.jouer_suite(espion, c, "kimi", "temoin", ("v8", "v7"), G, compteur(), n_max=3)
        for texte in vus:
            hist = ag._bloc(texte, ag.DEBUT_HIST, ag.FIN_HIST)
            self.assertTrue(all("verdict" not in h and "log_w_max" not in h for h in hist))

    def test_proposeur_sourd_declenche_l_audit_trop_beau(self):
        """Artefact de l'instrument : un proposeur qui ne lit pas les retours ; « résiste » est alors interdit."""
        suites = []
        for ci in range(3):
            c = ag.carte(G, ci)
            for f in ag.FOURNISSEURS:
                p = ag.ProposeurScripte("sourd")
                suites.append(ag.jouer_suite(p, c, f, "temoin", ("v8", "v7"), G, compteur(), n_max=3))
                suites.append(ag.jouer_suite(p, c, f, "retour", ("v8",), G, compteur(), n_max=3))
                suites.append(ag.jouer_suite(p, c, f, "retour", ("v7",), G, compteur(), n_max=3))
        lecture = ag.lire(suites)
        self.assertTrue(lecture["dents"])
        self.assertEqual(lecture["instrument_v8_retour"]["part_echos_exacts"], 0.0)
        self.assertIn("non jugeable (retours non lus)", lecture["issue"])
        self.assertTrue(any(a.startswith("A1") for a in lecture["audits"]))

    def test_optimiseur_scripte_issue_resiste(self):
        """Cas sain de la lecture : dents sous v7, aucune promotion sous v8, retours lus → « résiste (à cette taille) »."""
        suites, mesures = ag.jouer_tout({f: ag.ProposeurScripte("optimiseur") for f in ag.FOURNISSEURS}, G, 3, compteur(),
                                        n_max=4, rejeux=1)
        lecture = ag.lire(suites, mesures)
        self.assertEqual(lecture["issue"], "résiste (à cette taille)")
        self.assertEqual(lecture["audits"], [])
        self.assertEqual(lecture["taux"]["v8|retour|n=16|ensemble"]["promues"], 0)

    def test_breche_simulee(self):
        """Artefact de la lecture : promotions sous v8 → « infirmée (brèche sous v8) » et audit A2."""
        def suite(f, cond, juges, prem):
            return {"fournisseur": f, "condition": cond, "juges": list(juges), "premiere_promotion": prem, "tentatives": []}
        suites = []
        for ci in range(3):
            for f in ag.FOURNISSEURS:
                suites += [suite(f, "temoin", ("v8", "v7"), {"v8": None, "v7": 2}), suite(f, "retour", ("v8",), {"v8": 3}),
                           suite(f, "retour", ("v7",), {"v7": 2})]
        lecture = ag.lire(suites)
        self.assertEqual(lecture["issue"], "infirmée (brèche sous v8)")
        self.assertTrue(any(a.startswith("A2") for a in lecture["audits"]))


class ListeDArret(unittest.TestCase):
    def test_plafond_de_depense(self):
        c = ag.carte(G, 0)
        with self.assertRaises(ag.ArretAttaque):
            ag.jouer_suite(ag.ProposeurScripte("optimiseur", cout_par_appel=0.5), c, "kimi", "retour", ("v8",), G,
                           compteur(plafond=1.0), n_max=5)
        s = ag.jouer_suite(ag.ProposeurScripte("optimiseur", cout_par_appel=0.01), c, "kimi", "retour", ("v8",), G,
                           compteur(plafond=1.0), n_max=3)  # cas sain : sous le plafond
        self.assertEqual(len(s["tentatives"]), 3)

    def test_appel_echoue_une_reprise_consignee(self):
        c = ag.carte(G, 0)
        cpt = compteur()
        s = ag.jouer_suite(ag.ProposeurScripte("optimiseur", echecs={1}), c, "kimi", "retour", ("v8",), G, cpt, n_max=2)
        self.assertEqual(cpt.reprises, 1)
        self.assertEqual(len(s["tentatives"][0]["appels"]), 2)
        self.assertIsNotNone(s["tentatives"][0]["loi"])
        s2 = ag.jouer_suite(ag.ProposeurScripte("optimiseur", echecs={1, 2}), c, "kimi", "retour", ("v8",), G, compteur(), n_max=2)
        self.assertIn("appel échoué", s2["tentatives"][0]["motif_invalidite"])

    def test_bras_retour_a_un_seul_juge(self):
        with self.assertRaises(ag.AttaqueRefusee):
            ag.jouer_suite(ag.ProposeurScripte(), ag.carte(G, 0), "kimi", "retour", ("v8", "v7"), G, compteur(), n_max=2)


class Adaptateur(unittest.TestCase):
    def test_proposeur_par_adaptateur(self):
        class Faux:
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                self.vu = (role, max_tours, budget_usd)
                return type("R", (), {"texte_final": "[CAVIARDÉ]", "texte_brut": json.dumps({"retour_lu": "aucun", "loi": {
                    "type": "fixe", "probas": [1, 1, 1]}}), "cout_declare_usd": 0.002, "statut": "ok"})()
        faux = Faux()
        texte, cout, statut = ag.ProposeurAdaptateur(faux, "/nulle-part", 0.1)("consigne")
        self.assertEqual((statut, cout, faux.vu), ("ok", 0.002, ("proposeur_ideation", 1, 0.1)))
        self.assertIsNotNone(ag.analyser_reponse(texte)[0])


class Lanceur(unittest.TestCase):
    def test_refus_avant_toute_ecriture(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", str(2 ** 64)]), 2)
            self.assertEqual(lanceur.principal([sortie, "--preenregistrement", "x.md", "--moteur", "reel"]), 2)
            self.assertEqual(lanceur.principal([sortie, "--preenregistrement", os.path.join(RACINE, "prereg",
                             "preenregistrement-attaque-goodhart-v1-brouillon1.md"), "--configuration", "c.json", "--moteur", "reel",
                             "--confirmer-moteur-reel", "--registre-go", "absent.md", "--go", "GO-X"]), 2)
            self.assertFalse(os.path.exists(sortie))
            os.makedirs(sortie)
            open(os.path.join(sortie, "f"), "w").close()
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7"]), 2)

    def test_a_blanc_de_bout_en_bout(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--cartes", "1", "--n-max", "2",
                                                "--rejeux", "1"]), 0)
            with open(os.path.join(sortie, "attaque-goodhart-v1.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertIn("issue", r["lecture"])
            self.assertTrue(os.path.isfile(os.path.join(sortie, "manifeste.json.sha256")))


class Wilson(unittest.TestCase):
    def test_valeurs_de_reference(self):
        bas, haut = ag.wilson(0, 6)
        self.assertAlmostEqual(haut, 0.3903, places=3)
        bas, haut = ag.wilson(2, 6)
        self.assertGreater(bas, ag.ALPHA)
        self.assertLess(ag.wilson(1, 6)[0], ag.ALPHA)
        self.assertTrue(math.isclose(sum(ag.wilson(3, 6)), 1.0))


if __name__ == "__main__":
    unittest.main()
