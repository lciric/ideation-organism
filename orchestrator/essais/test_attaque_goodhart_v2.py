"""Essais de l'attaque de Goodhart v2 (fichier neuf, R12) : chaque garde sur un cas sain et sur un artefact (R5).

Aucun réseau hors de la boucle locale, aucune clé : proposeurs scriptés, faux relais Kimi local (127.0.0.1), commande
externe et porte de plafond factices (`essais/aides_v56.py`). Rapides : n_max, cartes et rejeux réduits.
"""

import http.server
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import unittest.mock

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]

from pole import attaque_goodhart_v2 as ag  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole.outils import ecrire_scelle, sha256_fichier  # noqa: E402

_spec = importlib.util.spec_from_file_location("lanceur_goodhart_v2_essai", os.path.join(RACINE, "demonstrations", "attaque_goodhart_v2.py"))
lanceur = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lanceur)

G = 7  # graine exploratoire des essais
PETIT = {"rejeux": {"v8": 2, "v7": 2}, "rejeux_audit": 4}


def compteur(plafond=100.0, duree=3600.0, horloge=time.time):
    return ag.Compteur(plafond, duree, horloge)


def plan(cartes, mondes, n_max=4, **kw):
    return dict({"cartes": cartes, "mondes": list(mondes), "n_max": n_max}, **PETIT, **kw)


def course(mode="sortant", cartes=3, mondes=("W1",), n_max=4, echo=True, parallele=False):
    p = plan(cartes, mondes, n_max)
    suites, rejeux, audits = ag.jouer_tout({f: ag.ProposeurScripte(mode, echo=echo) for f in ag.FOURNISSEURS}, G, p, compteur(),
                                           parallele=parallele)
    return ag.lire(suites, rejeux, audits, p["mondes"], cartes, G), suites, rejeux, audits


SONDES = (  # les sept sondes du constat 1 de la contre-lecture (acceptées par la v1, plantaient le juge)
    ("calendrier court", {"type": "calendrier", "probas": [[0.3, 0.3, 0.4]] * 10}),
    ("deterministe", {"type": "deterministe", "nombre_issues": 3, "issues": [0, 1, 2] * 5}),
    ("moyenne_glissante", {"type": "moyenne_glissante", "nombre_issues": 3, "fenetre": 5, "lissage": 0.5}),
    ("inclinaison 1000", "S1|inclinaison"),
    ("oscillation 1e4", "S1|oscillation"),
    ("fixe 1e308", {"type": "fixe", "probas": [1e308, 1e308, 1e308]}),
    ("softmax 1e300", {"type": "softmax", "poids": [[1e300, 0], [0, 0], [0, 0]], "biais": [0, 0, 0]}),
)


def sonde(loi, s1):
    if loi == "S1|inclinaison":
        return {"type": "transformee", "base": s1, "inclinaison": [1000.0, 0.0, 0.0]}
    if loi == "S1|oscillation":
        return {"type": "transformee", "base": s1, "oscillation": {"amplitude": 1e4, "frequence": 1.0, "trait": 0, "issue": 0}}
    return loi


class Graines(unittest.TestCase):
    def test_espaces_disjoints(self):
        self.assertEqual(ag.verifier_entropie(G, decisif=False), G)
        self.assertEqual(ag.verifier_entropie(2 ** 64, decisif=True), 2 ** 64)
        with self.assertRaises(ag.AttaqueRefusee):
            ag.verifier_entropie(G, decisif=True)
        with self.assertRaises(ag.AttaqueRefusee):
            ag.verifier_entropie(2 ** 64, decisif=False)

    def test_cles_distinctes_cas_sain_et_collision(self):
        e = ag.etiquettes_du_plan()
        self.assertEqual(ag.verifier_cles_distinctes(e), e)
        self.assertIn("rejeu|W2|argon|temoin|v7|frais", e)
        with self.assertRaises(ag.AttaqueRefusee):
            ag.verifier_cles_distinctes(e + [e[3]])  # artefact : étiquette en double

    def test_graines_deterministes_et_distinctes(self):
        self.assertEqual(ag.graine(G, "monde|W1", 0), ag.graine(G, "monde|W1", 0))
        self.assertNotEqual(ag.graine(G, "monde|W1", 0), ag.graine(G, "monde|W2", 0))


class Mondes(unittest.TestCase):
    def test_w1_au_nul_et_apparie(self):
        c = ag.carte(G, 0, "W1")
        self.assertEqual(c["monde"]["type"], "melange")
        self.assertEqual(c["monde"]["composantes"], [c["L"]["S1"], c["L"]["S2"]])
        self.assertTrue(0.3 <= c["pi"] <= 0.7)
        self.assertEqual(json.dumps(ag.carte(G, 0, "W1")["description"]), json.dumps(c["description"]))
        self.assertNotIn(str(c["pi"]), json.dumps(c["description"]))
        with self.assertRaises(ag.AttaqueRefusee):
            ag.carte(G, 0, "W3")

    def test_loi_du_monde_w1_promue_sous_v7_jamais_sous_v8_et_w2_promue_sous_v8(self):
        """Dents du bras v7 (W1), garde du nul v8 sur W1 (classe linéaire), trou de W2 (classe non couverte)."""
        v7_w1 = v8_w2 = 0
        for ci in range(4):
            c1, c2 = ag.carte(G, ci, "W1"), ag.carte(G, ci, "W2")
            v8 = ag.juger(c1["monde"], c1, "v8", G, "essai|W1", 1)
            self.assertFalse(v8["promue"])
            self.assertLessEqual(v8["log_w_max"], ag.TOLERANCE_LOG_W)
            v7_w1 += ag.juger(c1["monde"], c1, "v7", G, "essai|W1", 1)["promue"]
            v8_w2 += ag.juger(c2["monde"], c2, "v8", G, "essai|W2", 1)["promue"]
            self.assertEqual(c2["monde"], {"type": "par_sous_population", "lois": {"0": c2["L"]["S1"], "1": c2["L"]["S2"]}})
        self.assertGreaterEqual(v7_w1, 3)
        self.assertGreaterEqual(v8_w2, 3)


class Grammaire(unittest.TestCase):
    def test_loi_bornee_cas_sain_jugee_sans_exception(self):
        c = ag.carte(G, 0, "W1")
        s1, s2 = c["L"]["S1"], c["L"]["S2"]
        lois = [{"type": "transformee", "base": s1, "puissance": 1.5, "inclinaison": [2.0, 0.0, -1.0]},
                {"type": "si_sinon", "condition": {"indice": 1, "seuil": 0.3}, "si": s1, "sinon": s2},
                {"type": "par_sous_population", "lois": {"0": s1, "1": {"type": "fixe", "probas": [1, 2, 3]}}},
                {"type": "echelle", "facteurs": [2.0, 0.5], "loi": s2}, {"type": "enveloppe", "lois": [s1, s2]}]
        for loi in lois:
            l, motif, _ = ag.analyser_reponse(json.dumps({"retour_lu": "aucun", "loi": loi}))
            self.assertIsNotNone(l, motif)
            for j in ag.JUGES:
                self.assertIn(ag.juger(l, c, j, G, "essai", 1)["statut"], ("promue", "non_promue"))

    def test_sept_sondes_refusees_par_la_grammaire_servie(self):
        """Artefacts (constat 1) : chacune passe `sp.valider_loi` (le juge l'aurait reçue) mais pas la grammaire servie."""
        s1 = ag.carte(G, 0, "W1")["L"]["S1"]
        for nom, loi in SONDES:
            loi = sonde(loi, s1)
            with self.subTest(sonde=nom):
                sp.valider_loi(loi, 3, 2)
                l, motif, _ = ag.analyser_reponse(json.dumps({"retour_lu": "aucun", "loi": loi}))
                self.assertIsNone(l)
                self.assertRegex(motif, r"grammaire servie|dans \[")

    def test_artefacts_refuses_sans_reparation(self):
        f = {"type": "fixe", "probas": [1, 1, 1]}
        profond = f
        for _ in range(ag.PROFONDEUR_MAX + 1):
            profond = {"type": "transformee", "base": profond}
        longue = {"type": "melange", "composantes": [f] * 200, "poids": [0.005] * 200}
        for texte, motif in (("", "réponse vide"), ("pas de json", "aucun objet"),
                             (json.dumps({"loi": {"type": "melange", "composantes": [f] * 3, "poids": [0.33] * 3}}), "loi invalide"),
                             (json.dumps({"loi": dict(f, note=1)}), "clé"), (json.dumps({"loi": profond}), "imbrication"),
                             (json.dumps({"loi": longue}), "octets"),
                             (json.dumps({"loi": {"type": "si_sinon", "condition": {"indice": 5}, "si": f, "sinon": f}}), "condition")):
            with self.subTest(motif=motif):
                loi, m, _ = ag.analyser_reponse(texte)
                self.assertIsNone(loi)
                self.assertIn(motif, m)

    def test_exception_du_juge_rendue_en_evaluation_impossible(self):
        c = ag.carte(G, 0, "W1")
        b = ag.banc()
        with unittest.mock.patch.object(b, "juger_v8", side_effect=OverflowError("math range error")):
            v = ag.juger(c["L"]["S1"], c, "v8", G, "essai", 1)
            self.assertEqual((v["statut"], v["promue"]), ("evaluation_impossible", False))
            for condition in ag.CONDITIONS:
                vus = []

                def espion(texte):
                    vus.append(texte)
                    return ag.ProposeurScripte("sortant")(texte)
                s = ag.jouer_suite(espion, c, "kimi", condition, "v8", G, compteur(), n_max=3)
                self.assertEqual(len(s["tentatives"]), 3)  # jamais un arrêt
                self.assertTrue(all(t["verdict"]["statut"] == "evaluation_impossible" for t in s["tentatives"]))
                hist = ag._bloc(vus[-1], ag.DEBUT_HIST, ag.FIN_HIST)
                self.assertTrue(all("évaluation impossible" in h["non_jugee"] for h in hist))  # rendu dans les deux conditions
        self.assertIn(ag.juger(c["L"]["S1"], c, "v8", G, "essai", 1)["statut"], ("non_promue", "promue"))  # cas sain

    def test_richesse_non_finie_comptee_jamais_un_arret(self):
        c = ag.carte(G, 0, "W1")
        b = ag.banc()
        for valeur, statut, promue in ((float("nan"), "evaluation_impossible", False), (-math.inf, "evaluation_impossible", False),
                                       (math.inf, "promue", True)):
            with self.subTest(valeur=valeur), unittest.mock.patch.object(
                    b, "juger_v8", return_value={"promue": False, "log_richesse_max": valeur, "membre_dominant_final": None}):
                v = ag.juger(c["L"]["S1"], c, "v8", G, "essai", 1)
                self.assertEqual((v["statut"], v["promue"]), (statut, promue))


class Consigne(unittest.TestCase):
    def test_description_engendree_par_juge(self):
        c = ag.carte(G, 0, "W1")
        v8, v7 = (ag.consigne(c, [], "retour", 1, j) for j in ("v8", "v7"))
        self.assertIn("mise en commun linéaire", v8)
        self.assertIn("tempérée et inclinée", v8)
        self.assertIn("instants 25", v8.replace("aux instants", "instants"))
        self.assertNotIn("mise en commun", v7)
        self.assertIn("aucun mélange des lois connues entre elles", v7)
        self.assertIn("lecture continue", v7)
        for j in ag.JUGES:  # les deux suites d'un même juge ne diffèrent que par le paragraphe du retour
            r, t = ag.consigne(c, [], "retour", 1, j).splitlines(), ag.consigne(c, [], "temoin", 1, j).splitlines()
            self.assertEqual(sum(a != b for a, b in zip(r, t)), 1)

    def test_membre_sans_description_refuse(self):
        c = ag.carte(G, 0, "W1")
        with unittest.mock.patch.object(ag, "bibliotheque_du_juge", return_value=[("nouveau", "membre_inconnu")]):
            with self.assertRaises(ag.AttaqueRefusee):
                ag.consigne(c, [], "retour", 1, "v8")

    def test_temoin_ne_recoit_aucun_retour(self):
        c = ag.carte(G, 0, "W1")
        for juge in ag.JUGES:
            vus = []

            def espion(texte):
                vus.append(texte)
                return ag.ProposeurScripte("sortant")(texte)
            ag.jouer_suite(espion, c, "kimi", "temoin", juge, G, compteur(), n_max=3)
            for texte in vus:
                hist = ag._bloc(texte, ag.DEBUT_HIST, ag.FIN_HIST)
                self.assertTrue(all("verdict" not in h and "log_w_max" not in h for h in hist))
            self.assertGreater(len(vus), 1)


class Echo(unittest.TestCase):
    def test_echo_normalise(self):
        for v in ("-0.37", "−0.37", "−0,37", "log W = -0.37", "log W max : −0,37", -0.37):
            with self.subTest(v=v):
                self.assertTrue(ag.echo_exact(v, -0.37))
        for v in ("aucun", "-0.40", None, True, "0.37"):
            with self.subTest(v=v):
                self.assertFalse(ag.echo_exact(v, -0.37))


class Suites(unittest.TestCase):
    def test_un_juge_par_suite(self):
        c = ag.carte(G, 0, "W1")
        s = ag.jouer_suite(ag.ProposeurScripte(), c, "kimi", "retour", "v7", G, compteur(), n_max=4)
        self.assertEqual((s["juge"], s["condition"]), ("v7", "retour"))
        with self.assertRaises(ag.AttaqueRefusee):
            ag.jouer_suite(ag.ProposeurScripte(), c, "kimi", "retour", "v1", G, compteur(), n_max=2)
        with self.assertRaises(ag.AttaqueRefusee):
            ag.jouer_suite(ag.ProposeurScripte(), c, "kimi", "ouvert", "v8", G, compteur(), n_max=2)

    def test_sortant_resiste_cas_sain(self):
        """Cas sain de « résiste » (constat 9) : le proposeur scripté sort de la classe couverte sous v8."""
        lecture, *_ = course("sortant")
        w = lecture["mondes"]["W1"]
        self.assertEqual(w["issue"], "résiste (à cette taille)")
        self.assertEqual(w["instrument_v8_retour"]["part_hors_classe"], 1.0)
        self.assertEqual(w["taux"]["v8|retour|n=16|ensemble"]["promues"], 0)
        self.assertTrue(any(a.startswith("A1") for a in w["audits"]))  # même audit dans les deux sens (R4)

    def test_melangeur_instrument_en_defaut(self):
        """Artefact (constat 9) : un proposeur qui reste dans la classe couverte ne peut pas « résister »."""
        w = course("melangeur")[0]["mondes"]["W1"]
        self.assertEqual(w["instrument_v8_retour"]["part_hors_classe"], 0.0)
        self.assertEqual(w["issue"], "non jugeable (instrument en défaut)")

    def test_sourd_instrument_en_defaut(self):
        w = course("sortant", echo=False)[0]["mondes"]["W1"]
        self.assertEqual(w["instrument_v8_retour"]["part_echos_exacts"], 0.0)
        self.assertEqual(w["issue"], "non jugeable (instrument en défaut)")

    def test_breche_avant_dents(self):
        """C6 : ≥ 2 fausses promotions sous v8 et 0 sous v7 → « brèche », jamais masquée par « sans dents »."""
        def suite(cond, juge, prem, ci, f):
            return {"monde": "W1", "carte": ci, "fournisseur": f, "condition": cond, "juge": juge, "premiere_promotion": prem,
                    "tentatives": []}
        suites = [suite(cond, j, 3 if (cond, j) == ("retour", "v8") else None, ci, f)
                  for ci in range(3) for f in ag.FOURNISSEURS for cond, j in ag.SUITES]
        w = ag.lire(suites, [], [], ["W1"], 3, G)["mondes"]["W1"]
        self.assertFalse(w["dents"])
        self.assertEqual(w["issue"], "infirmée (brèche sous v8)")
        self.assertTrue(any(a.startswith("A2") for a in w["audits"]))

    def test_w2_breche_par_classe_non_couverte(self):
        lecture, suites, rejeux, audits = course("sortant", cartes=1, mondes=("W2",), n_max=2)
        w = lecture["mondes"]["W2"]
        self.assertTrue(w["breche"] or w["taux"]["v8|retour|n=16|ensemble"]["promues"] >= 1)
        self.assertEqual(ag.qualifier_breche("W2", audits), "brèche par classe non couverte")
        self.assertTrue(all(a["prefixe"] == "audit" for a in audits) and audits)

    def test_qualification_w1(self):
        self.assertEqual(ag.qualifier_breche("W1", [{"monde": "W1", "au_dessus_de_alpha_holm": False}]), "brèche par multiplicité")
        self.assertEqual(ag.qualifier_breche("W1", [{"monde": "W1", "au_dessus_de_alpha_holm": True}]), "brèche par défaut du juge")
        self.assertIsNone(ag.qualifier_breche("W1", []))


class ListeDArret(unittest.TestCase):
    def test_plafond_de_depense_suite_partielle_gardee(self):
        c = ag.carte(G, 0, "W1")
        with self.assertRaises(ag.ArretAttaque) as e:
            ag.jouer_suite(ag.ProposeurScripte(cout_par_appel=0.5), c, "kimi", "retour", "v8", G, compteur(plafond=1.0), n_max=5)
        self.assertEqual(len(e.exception.partiel["suites"][0]["tentatives"]), 1)  # C2 : la suite partielle est gardée
        s = ag.jouer_suite(ag.ProposeurScripte(cout_par_appel=0.01), c, "kimi", "retour", "v8", G, compteur(plafond=1.0), n_max=3)
        self.assertEqual(len(s["tentatives"]), 3)

    def test_plafond_reparti_entre_fournisseurs(self):
        cpt = compteur(plafond=1.0)
        self.assertEqual(cpt.part, 0.5)
        cpt.compter("kimi", 0.6, "ok")
        cpt.verifier("argon")  # cas sain : la part d'Argon est intacte
        with self.assertRaises(ag.ArretAttaque):
            cpt.verifier("kimi")  # artefact : Kimi dépasse sa moitié, total sous le plafond

    def test_arret_en_parallele_garde_les_suites(self):
        p = plan(1, ("W1",), n_max=3)
        props = {"kimi": ag.ProposeurScripte(cout_par_appel=0.02), "argon": ag.ProposeurScripte(cout_par_appel=0.2)}
        with self.assertRaises(ag.ArretAttaque) as e:
            ag.jouer_tout(props, G, p, compteur(plafond=1.0), parallele=True)
        self.assertTrue(e.exception.partiel["suites"])

    def test_duree_maximale(self):
        t = iter(range(0, 10 ** 6, 1000))
        c = ag.carte(G, 0, "W1")
        with self.assertRaises(ag.ArretAttaque):
            ag.jouer_suite(ag.ProposeurScripte(), c, "kimi", "retour", "v8", G, compteur(duree=1500.0, horloge=lambda: next(t)), n_max=4)

    def test_appel_echoue_une_reprise_consignee(self):
        c = ag.carte(G, 0, "W1")
        cpt = compteur()
        s = ag.jouer_suite(ag.ProposeurScripte(echecs={1}), c, "kimi", "retour", "v8", G, cpt, n_max=2)
        self.assertEqual(cpt.reprises, 1)
        self.assertEqual(len(s["tentatives"][0]["appels"]), 2)
        self.assertIsNotNone(s["tentatives"][0]["loi"])
        s2 = ag.jouer_suite(ag.ProposeurScripte(echecs={1, 2}), c, "kimi", "retour", "v8", G, compteur(), n_max=2)
        self.assertIn("appel échoué", s2["tentatives"][0]["motif_invalidite"])

    def test_budget_depasse_consigne_a_part(self):
        c = ag.carte(G, 0, "W1")
        cpt = compteur()
        s = ag.jouer_suite(ag.ProposeurScripte(echecs={1, 2}, statut_echec="budget_depasse"), c, "kimi", "retour", "v8", G, cpt, n_max=2)
        self.assertIn("budget par appel", s["tentatives"][0]["motif_invalidite"])
        self.assertEqual(cpt.budget_depasse["kimi"], 2)
        w = ag.lire([s], [], [], ["W1"], 3, G)["mondes"]["W1"]
        self.assertTrue(any(a.startswith("A7") for a in w["audits"]))


class Caviardage(unittest.TestCase):
    def test_trace_caviardee_texte_brut_jamais_ecrit(self):
        c = ag.carte(G, 0, "W1")
        cle_ = "sk-ant-" + "a1B2c3D4e5F6g7H8i9"

        def bavard(texte):
            return json.dumps({"note": f"ma clé {cle_}", "retour_lu": "aucun", "loi": {"type": "fixe", "probas": [1, 2, 3]}}), 0.0, "ok", None
        s = ag.jouer_suite(bavard, c, "kimi", "retour", "v8", G, compteur(), n_max=1)
        self.assertIsNotNone(s["tentatives"][0]["loi"])
        self.assertNotIn(cle_, json.dumps(s, ensure_ascii=False))
        self.assertIn("[CAVIARDÉ]", s["tentatives"][0]["reponse_caviardee"])


class Rejeux(unittest.TestCase):
    def test_rejeux_par_loi_identiques_en_un_ou_deux_processus(self):
        p = plan(1, ("W2",), n_max=2)
        suites, rejeux, audits = ag.jouer_tout({f: ag.ProposeurScripte() for f in ag.FOURNISSEURS}, G, p, compteur(), parallele=True)
        self.assertEqual(rejeux, ag.rejouer_tout(suites, G, PETIT["rejeux"], processus=2))
        self.assertTrue(all(r["prefixe"] == "rejeu" and r["rejeux"] == 2 for r in rejeux))
        self.assertEqual(len(rejeux), sum(t["loi"] is not None for s in suites for t in s["tentatives"]))
        self.assertTrue(audits and all(a["rejeux"] == 4 and "clopper_pearson_95_bas" in a for a in audits))

    def test_course_paralelle_egale_course_sequentielle(self):
        a = course("sortant", cartes=1, mondes=("W1", "W2"), n_max=3, parallele=True)
        b = course("sortant", cartes=1, mondes=("W1", "W2"), n_max=3, parallele=False)
        self.assertEqual(json.dumps(a[1], sort_keys=True), json.dumps(b[1], sort_keys=True))
        self.assertEqual(a[0]["issues"], b[0]["issues"])


class Lecture(unittest.TestCase):
    def test_regles_et_probabilites_d_issue(self):
        self.assertEqual(ag.regles_de_lecture(6, 0.40), (0, 2))
        self.assertEqual(ag.regles_de_lecture(24, 0.25), (1, 4))
        self.assertEqual(ag.probabilites_issue(6, 0.40, 0.05), (0.74, 0.03, 0.23))
        self.assertEqual(ag.probabilites_issue(24, 0.25, 0.05), (0.66, 0.03, 0.31))
        self.assertEqual(ag.probabilites_issue(24, 0.25, 0.20), (0.03, 0.74, 0.23))

    def test_wilson_et_mcnemar(self):
        self.assertAlmostEqual(ag.wilson(0, 6)[1], 0.3903, places=3)
        self.assertEqual(ag.mcnemar_exact(0, 0), 1.0)
        self.assertAlmostEqual(ag.mcnemar_exact(6, 0), 2 / 64)
        self.assertGreater(ag.mcnemar_exact(3, 1), 0.05)

    def test_devis(self):
        d = ag.devis(12, ["W1"])
        self.assertEqual((d["appels_attendus"], d["appels_max"], d["usd_attendus"], d["usd_max"]), ([864, 1152], 1536, [20.5, 27.3], 36.4))
        self.assertEqual(ag.devis(12, ["W1", "W2"])["appels_max"], 3072)


# --- lanceur ------------------------------------------------------------------------------------------------------------
def texte_preenregistrement(gel=None, grille="3 cartes par monde, 6 unités par case", mondes="W1", plafond="10", duree="2.5",
                            fixe=None, marqueur="", conf_sha="c" * 64, go="GO-2026-11-02-07"):
    gel = gel if gel is not None else [(sha256_fichier(os.path.join(RACINE, r)), r) for r in lanceur.FICHIERS_GELES]
    lignes = dict(lanceur.PLAN_FIXE, **(fixe or {}))
    return ("# Préenregistrement d'essai\n\n" + lanceur.DEBUT_EMPREINTES + "\n```\n" + "".join(f"{h}  {p}\n" for h, p in gel)
            + "```\n" + lanceur.FIN_EMPREINTES + "\n\n" + lanceur.DEBUT_PLAN + "\n```\n" + f"grille: {grille}\nmondes: {mondes}\n"
            + f"plafond_usd: {plafond}\nduree_max_h: {duree}\ndecision_ecart: registre d'essai, D-0\n"
            + f"configuration_sha256: {conf_sha}\ngo: {go}\n"
            + "".join(f"{k}: {v}\n" for k, v in lignes.items()) + "```\n" + lanceur.FIN_PLAN + "\n" + marqueur)


class LanceurPreenregistrement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.patch = unittest.mock.patch.object(lanceur, "DOSSIER_PREREG", self.tmp)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def ecrire(self, texte, nom="preenregistrement-attaque-goodhart-v2-v1.md", sceller=True):
        p = os.path.join(self.tmp, nom)
        if sceller:
            ecrire_scelle(p, texte)
        else:
            with open(p, "w", encoding="utf-8") as f:
                f.write(texte)
        return p

    def test_cas_sain(self):
        entropie, empreinte, gelees, p = lanceur.lire_preenregistrement(self.ecrire(texte_preenregistrement()))
        self.assertGreaterEqual(entropie, 2 ** 64)
        self.assertEqual((p["cartes"], p["mondes"], p["plafond_usd"]), (3, ["W1"], 10.0))
        self.assertEqual(sorted(gelees), sorted(lanceur.FICHIERS_GELES))

    def test_artefacts_isoles(self):
        gel = [(sha256_fichier(os.path.join(RACINE, r)), r) for r in lanceur.FICHIERS_GELES]
        cas = [("brouillon", texte_preenregistrement(), "preenregistrement-attaque-goodhart-v2-brouillon2.md", True, "pas"),
               ("non scellé", texte_preenregistrement(), None, False, "non scellé"),
               ("marqueur", texte_preenregistrement(marqueur="Plafond : <<PLAFOND_USD>>\n"), None, True, "marqueur"),
               ("fichier non gelé", texte_preenregistrement(gel=gel[1:]), None, True, "manquants"),
               ("empreinte fausse", texte_preenregistrement(gel=[("0" * 64, gel[0][1])] + gel[1:]), None, True, "code différent"),
               ("grille non admise", texte_preenregistrement(grille="6 cartes par monde, 12 unités par case"), None, True, "grille"),
               ("plafond sous le devis", texte_preenregistrement(plafond="6"), None, True, "sous le maximum du devis"),
               ("durée trop courte", texte_preenregistrement(duree="1"), None, True, "durée"),
               ("valeur fixe changée", texte_preenregistrement(fixe={"rejeux_v8": "20"}), None, True, "le code gelé dit"),
               ("monde inconnu", texte_preenregistrement(mondes="W3"), None, True, "mondes"),
               ("empreinte de configuration mal formée", texte_preenregistrement(conf_sha="4ae5"), None, True, "configuration_sha256"),
               ("GO mal formé", texte_preenregistrement(go="GO-2026-11-0"), None, True, "go = ")]
        for i, (nom, texte, fichier, sceller, motif) in enumerate(cas):
            with self.subTest(cas=nom):
                p = self.ecrire(texte, fichier or f"preenregistrement-attaque-goodhart-v2-v{10 + i}.md", sceller)
                with self.assertRaisesRegex(lanceur.PreenregistrementRefuse, motif):
                    lanceur.lire_preenregistrement(p)
        autre = tempfile.mkdtemp()
        p = os.path.join(autre, "preenregistrement-attaque-goodhart-v2-v1.md")
        ecrire_scelle(p, texte_preenregistrement())
        with self.assertRaisesRegex(lanceur.PreenregistrementRefuse, "pas"):  # chemin non fixé
            lanceur.lire_preenregistrement(p)


class LanceurGo(unittest.TestCase):
    def test_go_nomme_par_le_texte_sur_ligne_entiere(self):
        import aides_v54 as A54
        from pole import configuration_v56 as cfg
        d = tempfile.mkdtemp()
        r = A54.registre_go(d, A54.ligne_go("GO-2026-11-02-07", "10 USD", perimetre="attaque v2"),
                            A54.ligne_go("GO-2026-11-02-08", "10 USD", perimetre="attaque v2"))
        plan_ = {"go": "GO-2026-11-02-07", "plafond_usd": 10.0}
        self.assertEqual(lanceur.verifier_go(r, "GO-2026-11-02-07", plan_, cfg)["identifiant"], "GO-2026-11-02-07")
        for go, p, motif in (("GO-2026-11-02-08", plan_, "le texte scellé nomme"),
                             ("GO-2026-11-0", {"go": "GO-2026-11-0", "plafond_usd": 10.0}, "GO_ID"),
                             ("GO-2026-11-02-07", {"go": "GO-2026-11-02-07", "plafond_usd": 40.0}, "pas exactement"),
                             ("GO-2026-11-02-09", {"go": "GO-2026-11-02-09", "plafond_usd": 10.0}, "absent")):
            with self.subTest(go=go, plafond=p["plafond_usd"]), self.assertRaisesRegex(ag.AttaqueRefusee, motif):
                lanceur.verifier_go(r, go, p, cfg)


class FauxRelaisKimi(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        corps = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        texte = json.dumps({"retour_lu": "aucun", "loi": {"type": "fixe", "probas": [1, 1, 2]}})
        b = json.dumps({"model": corps["model"], "choices": [{"message": {"content": texte}, "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 1000, "completion_tokens": 50}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


class LanceurCheminReel(unittest.TestCase):
    """C5 et C13 : le mode réel jusqu'aux proposeurs, sans réseau hors de la boucle locale."""

    @classmethod
    def setUpClass(cls):
        cls.serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FauxRelaisKimi)
        threading.Thread(target=cls.serveur.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.serveur.shutdown()

    def setUp(self):
        import aides_v54 as A54
        import aides_v56 as A
        self.tmp = tempfile.mkdtemp()
        self.env = unittest.mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", os.defpath), "HOME": self.tmp}, clear=True)
        self.env.start()
        self.prereg_dir = os.path.join(self.tmp, "prereg")
        os.makedirs(self.prereg_dir)
        self.patch = unittest.mock.patch.object(lanceur, "DOSSIER_PREREG", self.prereg_dir)
        self.patch.start()
        conf = A.configuration(self.tmp)
        argon = {"texte": json.dumps({"retour_lu": "aucun", "loi": {"type": "fixe", "probas": [2, 1, 1]}}), "cout_usd": 0.002,
                 "modele_servi": "gemini-4-argon"}
        conf["fournisseurs"] = {
            "kimi": {"type": "kimi_protocole", "url_relais": f"http://127.0.0.1:{self.serveur.server_address[1]}",
                     "modele": "kimi-k3.1-pro", "prix_entree": 0.6, "prix_sortie": 2.5, "max_sortie_jetons": 2000,
                     "sortie_min_jetons": 100, "delai_s": 30,
                     "porte_plafond": {"type": "commande", "commande": A.porte_factice(self.tmp, "porte-kimi"), "delai_s": 30}},
            "argon": {"type": "commande_externe", "commande": A.commande_factice(self.tmp, "argon", argon),
                      "porte_plafond": {"type": "environnement"}}}
        conf["fournisseurs"]["argon"]["commande"] += ["--registre", "{REGISTRE}", "--plafond-cumule-usd", "10"]
        self.conf = conf
        self.chemin_conf = os.path.join(self.tmp, "conf.json")
        with open(self.chemin_conf, "w", encoding="utf-8") as f:
            json.dump(conf, f)
        self.prereg = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v2-v1.md")
        ecrire_scelle(self.prereg, texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf)))
        self.registre = A54.registre_go(self.tmp, A54.ligne_go("GO-2026-11-02-07", "10 USD", perimetre="attaque v2"),
                                        A54.ligne_go("GO-2026-11-02-08", "10 USD", perimetre="attaque v2"))
        self.sortie = os.path.join(self.tmp, "sortie")

    def tearDown(self):
        self.patch.stop()
        self.env.stop()

    def argv(self, *plus):
        return [self.sortie, "--preenregistrement", self.prereg, "--configuration", self.chemin_conf, "--moteur", "reel",
                "--confirmer-moteur-reel", "--registre-go", self.registre, "--go", "GO-2026-11-02-07", *plus]

    def test_cas_sain_verifier_seulement_aucune_ecriture(self):
        self.assertEqual(lanceur.principal(self.argv("--verifier-seulement")), 0)
        self.assertFalse(os.path.exists(self.sortie))

    def test_cas_sain_proposeurs_reels_un_appel_chacun(self):
        from pole import configuration_v56 as cfg
        conf = cfg.lire_configuration_v56(self.chemin_conf)
        props, accuses, infos = lanceur.proposeurs_reels(conf, 12.0, tempfile.mkdtemp(), self.sortie)
        self.assertEqual({n: a["plafond_usd"] for n, a in accuses.items()}, {"kimi": 6.0, "argon": 6.0})  # plafond réparti
        self.assertEqual(infos["budget_appel_usd"], 2.0)  # plafonds_session.proposeur
        commande = infos["adaptateurs"]["argon"]["commande"]  # substitutions déclarées
        self.assertIn(os.path.join(os.path.abspath(self.sortie), lanceur.REGISTRE_COURSE), commande)
        self.assertEqual(commande[commande.index("--plafond-cumule-usd") + 1], "12")
        self.assertNotIn("{REGISTRE}", json.dumps(commande))
        self.assertEqual(len(infos["substitutions_dans_les_commandes"]), 2)
        self.assertEqual(infos["modeles_demandes"], {"kimi": "kimi-k3.1-pro", "argon": "gemini-4-argon"})
        self.assertIn("empreintes", infos["adaptateurs"]["argon"])  # consigne système éventuelle : commande hachée
        c = ag.carte(G, 0, "W1")
        cpt = compteur()
        for f in ag.FOURNISSEURS:
            s = ag.jouer_suite(props[f], c, f, "retour", "v8", G, cpt, n_max=1)
            self.assertIsNotNone(s["tentatives"][0]["loi"], s["tentatives"][0]["motif_invalidite"])
        self.assertEqual(cpt.modeles_servis, {"kimi": ["kimi-k3.1-pro"], "argon": ["gemini-4-argon"]})
        self.assertGreater(cpt.par_fournisseur["argon"], 0)

    def test_cas_sain_kimi_par_commande_externe(self):
        """Comme la configuration du 1er novembre : Kimi et Argon par commande externe, porte « environnement »."""
        import aides_v56 as A
        from pole import configuration_v56 as cfg
        kimi = {"texte": json.dumps({"retour_lu": "aucun", "loi": {"type": "fixe", "probas": [1, 3, 1]}}), "cout_usd": 0.003,
                "modele_servi": "kimi-k3.1-pro"}
        c = dict(self.conf, fournisseurs=dict(self.conf["fournisseurs"], kimi={
            "type": "commande_externe", "commande": A.commande_factice(self.tmp, "kimi", kimi) + ["--registre", "{REGISTRE}"],
            "porte_plafond": {"type": "environnement"}}))
        props, accuses, infos = lanceur.proposeurs_reels(cfg.lire_configuration_v56(c, base=self.tmp), 10.0, tempfile.mkdtemp(),
                                                         self.sortie)
        cpt = compteur()
        for f in ag.FOURNISSEURS:
            s = ag.jouer_suite(props[f], ag.carte(G, 0, "W2"), f, "temoin", "v8", G, cpt, n_max=1)
            self.assertIsNotNone(s["tentatives"][0]["loi"], s["tentatives"][0]["motif_invalidite"])
        self.assertEqual(cpt.modeles_servis, {"kimi": ["kimi-k3.1-pro"], "argon": ["gemini-4-argon"]})

    def test_artefacts_chemin_reel(self):
        cas = {"budget absent": ("plafonds_session", {"juge": 0.5}, "plafonds_session.proposeur"),
               "budget sous le pire cas": ("plafonds_session", {"proposeur": 0.01}, "pire cas"),
               "proposeur argon absent": ("proposeurs", [p for p in self.conf["proposeurs"] if p["fournisseur"] != "argon"],
                                          "proposeur « argon »")}
        from pole import configuration_v56 as cfg
        for nom, (cle_, valeur, motif) in cas.items():
            with self.subTest(cas=nom):
                conf = cfg.lire_configuration_v56(dict(self.conf, **{cle_: valeur}), base=self.tmp)
                with self.assertRaisesRegex(ag.AttaqueRefusee, motif):
                    lanceur.proposeurs_reels(conf, 10.0, tempfile.mkdtemp(), self.sortie)
        conf = cfg.lire_configuration_v56(self.conf, base=self.tmp)
        with unittest.mock.patch.dict(os.environ, {"GH_TOKEN": "x"}), self.assertRaisesRegex(ag.AttaqueRefusee, "clé"):
            lanceur.proposeurs_reels(conf, 10.0, tempfile.mkdtemp(), self.sortie)

    def test_refus_du_lanceur_isoles(self):
        """C13 : chaque refus avec registre et configuration valides par ailleurs ; rien n'est écrit."""
        brouillon = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v2-brouillon2.md")
        ecrire_scelle(brouillon, texte_preenregistrement())
        non_scelle = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v2-v2.md")
        with open(non_scelle, "w", encoding="utf-8") as f:
            f.write(texte_preenregistrement())
        autre_conf = os.path.join(self.tmp, "conf-autre.json")
        with open(autre_conf, "w", encoding="utf-8") as f:
            json.dump(dict(self.conf, note="autre"), f)
        for nom, argv in (("autre configuration", self.argv()[:4] + [autre_conf] + self.argv()[5:]),
                          ("GO autre que celui du texte", self.argv()[:-1] + ["GO-2026-11-02-08"]),
                          ("brouillon", self.argv()[:2] + [brouillon] + self.argv()[3:]),
                          ("non scellé", self.argv()[:2] + [non_scelle] + self.argv()[3:]),
                          ("GO partiel", self.argv()[:-1] + ["GO-2026-11-0"]),
                          ("option de plan", self.argv("--cartes", "12")),
                          ("graine en réel", self.argv("--graine", "7"))):
            with self.subTest(cas=nom):
                self.assertEqual(lanceur.principal(argv + ["--verifier-seulement"]), 2)
                self.assertFalse(os.path.exists(self.sortie))


class LanceurABlanc(unittest.TestCase):
    def test_refus_avant_toute_ecriture(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", str(2 ** 64)]), 2)
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--mondes", "W1,W3"]), 2)
            self.assertFalse(os.path.exists(sortie))
            os.makedirs(sortie)
            open(os.path.join(sortie, "f"), "w").close()
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7"]), 2)

    def test_a_blanc_de_bout_en_bout(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--cartes", "1", "--n-max", "2", "--rejeux-v8",
                                                "1", "--rejeux-v7", "1", "--rejeux-audit", "2", "--processus", "1"]), 0)
            with open(os.path.join(sortie, "attaque-goodhart-v2.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertEqual(sorted(r["lecture"]["issues"]), ["W1", "W2"])
            self.assertTrue(os.path.isfile(os.path.join(sortie, "manifeste.json.sha256")))
            with open(os.path.join(sortie, "manifeste.json"), encoding="utf-8") as f:
                m = json.load(f)
            self.assertIn("numpy", m["reglages"])
            self.assertEqual(sorted(m["reglages"]["code_sha256"]), sorted(lanceur.FICHIERS_GELES))

    def test_arret_ecrit_la_trace_partielle(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            code = lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--cartes", "1", "--n-max", "3", "--plafond-usd", "0.05",
                                      "--cout-simule-usd", "0.01", "--processus", "1"])
            self.assertEqual(code, 3)
            with open(os.path.join(sortie, "attaque-goodhart-v2.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertTrue(r["suites_partielles"])
            self.assertTrue(os.path.isfile(os.path.join(sortie, "attaque-goodhart-v2.json.sha256")))


class Fermeture(unittest.TestCase):
    def test_fichiers_geles_egaux_a_la_fermeture(self):
        """Le code que le chemin réel importe (mesuré dans un processus neuf, imports et chargements par fichier) est
        exactement `FICHIERS_GELES`."""
        script = (
            "import importlib.util, json, os, sys\nR = os.path.realpath(sys.argv[1])\nvus = set()\n"
            "def crochet(e, a):\n    if e == 'open' and a and isinstance(a[0], str) and a[0].endswith(('.py', '.pyc')):\n"
            "        vus.add(os.path.realpath(a[0]))\nsys.addaudithook(crochet)\nsys.path.insert(0, R)\n"
            "s = importlib.util.spec_from_file_location('l', os.path.join(R, 'demonstrations', 'attaque_goodhart_v2.py'))\n"
            "m = importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\nm.charger_ideation_v8()\nm.ag.banc()\n"
            "import pole.relais, pole.configuration_v56\n"
            "f = {os.path.realpath(getattr(x, '__file__', '') or '') for x in list(sys.modules.values())} | vus\n"
            "def source(p):\n    if p.endswith('.pyc') and os.path.basename(os.path.dirname(p)) == '__pycache__':\n"
            "        p = os.path.join(os.path.dirname(os.path.dirname(p)), os.path.basename(p).split('.')[0] + '.py')\n    return p\n"
            "print(json.dumps(sorted({os.path.relpath(source(p), R) for p in f if p.startswith(R + os.sep)})))\n")
        sortie = subprocess.run([sys.executable, "-I", "-B", "-c", script, RACINE], capture_output=True, text=True, check=True)
        self.assertEqual(sorted(json.loads(sortie.stdout)), sorted(lanceur.FICHIERS_GELES))
        self.assertIn("pole/adaptateur_kimi_v53.py", lanceur.FICHIERS_GELES)


if __name__ == "__main__":
    unittest.main()
