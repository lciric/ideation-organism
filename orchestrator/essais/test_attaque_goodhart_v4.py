"""Essais de l'attaque de Goodhart v4 (contre le juge v9 ; fichier neuf, R12) : chaque garde neuve sur un cas sain et sur un
artefact (R5). Les gardes de la v3 et de la v2 restent couvertes par `essais/test_attaque_goodhart_v3.py` et
`essais/test_attaque_goodhart_v2.py` (inchangés).

Aucun réseau, aucune clé : proposeurs scriptés, commande externe factice locale. Évaluations sous v9 coûteuses (≈ 0,2 à 0,3 s) :
cartes, tentatives et rejeux réduits.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]

from pole import attaque_goodhart_v2 as ag  # noqa: E402
from pole import attaque_goodhart_v3 as a3  # noqa: E402
from pole import attaque_goodhart_v4 as a4  # noqa: E402
from pole import nul_v9  # noqa: E402
from pole.outils import ecrire_scelle, sha256_fichier  # noqa: E402


def _charger(nom_fichier, nom):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, "demonstrations", nom_fichier))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


lanceur = _charger("attaque_goodhart_v4.py", "lanceur_goodhart_v4_essai")
lanceur_v3 = lanceur.l3  # l'instance du lanceur v3 que charge le lanceur v4 (inchangée)

G = 7  # graine exploratoire des essais
ARGON = {"nom": "argon", "type": "commande_externe", "port": 8805, "modele": "gemini-4-argon", "fils": 1, "taux_usd": 0.062,
         "secondes": (7.6, 40.0)}


def carte(c, w):
    return a4.carte(G, c, w)


def w2_par_sous_population(L):
    """La loi « si/sinon par sous-population S1, S2 » que le proposeur sortant de la v2 propose d'abord : le trou du v8."""
    return {"type": "si_sinon", "condition": {"sous_population": 0}, "si": L["S1"], "sinon": L["S2"]}


# --- juges -----------------------------------------------------------------------------------------------------------------------
class Juges(unittest.TestCase):
    def test_juge_ancien_par_monde(self):
        """Cas sain : « ancien » = v7 sur W1, v8 sur W2 ; artefact : un juge v3 (« v8 ») ou inconnu est refusé."""
        self.assertEqual((a4.nul_du_juge("ancien", "W1"), a4.nul_du_juge("ancien", "W2"), a4.nul_du_juge("v9", "W1")), ("v7", "v8", "v9"))
        self.assertEqual(a4.JUGES, ("v9", "ancien"))
        for juge in ("v8", "v7", "x"):
            with self.subTest(juge=juge), self.assertRaises(a4.AttaqueRefusee):
                a4.nul_du_juge(juge, "W1")
        with self.assertRaises(a4.AttaqueRefusee):
            a4.nul_du_juge("ancien", "W3")
        c1, c2 = carte(0, "W1"), carte(0, "W2")
        self.assertIn("lecture continue", a4.consigne(c1, [], "retour", 1, "ancien"))
        self.assertIn("mise en commun linéaire", a4.consigne(c2, [], "retour", 1, "ancien"))
        self.assertEqual(a4.consigne(c1, [], "temoin", 2, "ancien"), ag.consigne(c1, [], "temoin", 2, "v7"))
        self.assertEqual(a4.consigne(c2, [], "temoin", 2, "ancien"), ag.consigne(c2, [], "temoin", 2, "v8"))
        v1 = a4.juger(c1["monde"], c1, "ancien", G, "W1|argon|retour|ancien", 1)
        v2 = a4.juger(c2["monde"], c2, "ancien", G, "W2|argon|retour|ancien", 1)
        self.assertEqual((v1["nul"], v2["nul"]), ("v7", "v8"))
        self.assertEqual(v1, dict(ag.juger(c1["monde"], c1, "v7", G, "W1|argon|retour|ancien", 1), nul="v7"))
        self.assertTrue(v2["promue"], "le monde W2 doit être promu sous v8 (dents)")

    def test_w2_sortant_de_v8_refuse_par_v9(self):
        """Le monde W2 et la loi par sous-population du proposeur sortant de la v2 : promus sous l'ancien juge (v8) et jamais
        sous v9 (log W ≤ 10⁻⁶), cartes 0 à 2 ; le v8 apparié au journal les promeut aussi (sans effet)."""
        promues_ancien = 0
        for ci in range(3):
            c = carte(ci, "W2")
            for loi in (c["monde"], w2_par_sous_population(c["L"])):
                v = a4.juger(loi, c, "v9", G, "W2|argon|retour|v9", 1)
                self.assertEqual((v["statut"], v["nul"]), ("non_promue", "v9"))
                self.assertLessEqual(v["log_w_max"], 1e-6)
                self.assertTrue(v["v8_apparie"]["promue"])
                promues_ancien += a4.juger(loi, c, "ancien", G, "W2|argon|retour|ancien", 1)["promue"]
        self.assertGreaterEqual(promues_ancien, 5)

    def test_loi_neuve_plantee_promue_sous_v9(self):
        """Cas sain du juge (il n'est pas muet) : sur un monde à loi neuve N hors de l'archive, la loi N est promue sous v9 (au
        moins 3 cartes sur 4), et la décision ne dépend pas de l'appariement."""
        promues = 0
        for ci in range(4):
            c = carte(ci, "W1")
            N = ag.banc().v7._monde_lois(__import__("random").Random(100 + ci))["N"]
            cn = dict(c, monde=N)
            v = a4.juger(N, cn, "v9", G, "W1|argon|retour|v9", 1)
            w = a4.juger(N, cn, "v9", G, "W1|argon|retour|v9", 1, apparie=False)
            self.assertEqual({k: v[k] for k in ("statut", "promue", "log_w_max", "dominant")}, {k: w[k] for k in ("statut", "promue", "log_w_max", "dominant")})
            self.assertNotIn("v8_apparie", w)
            promues += v["promue"]
        self.assertGreaterEqual(promues, 3)

    def test_monotonie_violee_evaluation_impossible(self):
        """Artefact : un banc qui rendrait une promotion sous v9 sans promotion sous v8 → « évaluation impossible »
        (MonotonieViolee), jamais une promotion ; lu par la lecture (A6, violations comptées)."""
        c = carte(0, "W2")
        faux = ({"promue": True, "log_richesse_max": 5.0, "trajectoire_log_w": [5.0], "membre_dominant_final": "x"},
                {"promue": False, "log_richesse_max": 1.0, "trajectoire_log_w": [1.0], "membre_dominant_final": "x"})
        with unittest.mock.patch.object(a4.banc_v9(), "juger_v9", return_value=faux):
            v = a4.juger(c["monde"], c, "v9", G, "W2|argon|retour|v9", 1)
        self.assertEqual(v["statut"], "evaluation_impossible")
        self.assertFalse(v["promue"])
        self.assertIn("MonotonieViolee", v["motif"])


# --- description et consigne ---------------------------------------------------------------------------------------------------
class Description(unittest.TestCase):
    def test_description_v9_dit_les_membres_et_le_non_couvert(self):
        L = carte(0, "W2")["L"]
        types = {t for _, t in a4.bibliotheque_du_juge("v9", L)}
        self.assertIn(nul_v9.TYPE_MORCEAUX, types)
        self.assertIn("ajuste_lineaire", types)
        d = a4.description_du_juge("v9", L)
        self.assertIn(nul_v9.PHRASES_MEMBRES_V9[nul_v9.TYPE_MORCEAUX], d)
        self.assertIn("mise en commun linéaire", d)
        self.assertIn(a4.MARQUE_NON_COUVERT, d)
        for phrase in nul_v9.NON_COUVERT_V9:
            self.assertIn(phrase, d)
        self.assertIn("instants 25, 50", d)
        self.assertEqual(a4.description_du_juge("v8", L), ag.description_du_juge("v8", L))

    def test_artefact_membre_sans_phrase_refuse(self):
        L = carte(0, "W1")["L"]
        with unittest.mock.patch.dict(a4.PHRASES_MEMBRES, clear=True, **{k: v for k, v in a4.PHRASES_MEMBRES.items() if k != nul_v9.TYPE_MORCEAUX}):
            with self.assertRaises(a4.AttaqueRefusee):
                a4.description_du_juge("v9", L)

    def test_consigne_v9_ne_differe_que_par_le_juge(self):
        c = carte(1, "W1")
        hist = [{"tentative": 1, "loi": {"type": "fixe", "probas": [1, 1, 1]}, "verdict": "non promue", "log_w_max": -1.2}]
        for cond in ("temoin", "retour"):
            v9 = a4.consigne(c, hist, cond, 2, "v9")
            self.assertNotEqual(v9, ag.consigne(c, hist, cond, 2, "v8"))
            self.assertEqual(v9.replace(a4.description_du_juge("v9", c["L"]), ag.description_du_juge("v8", c["L"])),
                             ag.consigne(c, hist, cond, 2, "v8"))


# --- classe couverte -----------------------------------------------------------------------------------------------------------
def _si(j, s, a, b):
    return {"type": "si_sinon", "condition": {"indice": j, "seuil": s}, "si": a, "sinon": b}


def _par(a, b):
    return {"type": "par_sous_population", "lois": {"0": a, "1": b}}


def _mel(lois, poids):
    return {"type": "melange", "composantes": lois, "poids": poids}


class ClasseCouverte(unittest.TestCase):
    def setUp(self):
        self.L = carte(0, "W2")["L"]
        self.S1, self.S2 = self.L["S1"], self.L["S2"]
        self.q = {"type": "fixe", "probas": [2, 1, 1]}

    def test_cas_sain_lois_de_la_classe_du_v9(self):
        S1, S2, q = self.S1, self.S2, self.q
        couvertes = {"W2": carte(0, "W2")["monde"], "type W1 (mélange π·S1 + (1 − π)·S2)": _mel([S1, S2], [0.43, 0.57]), "si/sinon g": w2_par_sous_population(self.L),
                     "seuil": _si(1, 0.37, S2, S1), "M03 bruit commun": _mel([_par(S1, S2), q], [0.8, 0.2]),
                     "M05": _par(_mel([S1, S2], [0.3, 0.7]), _mel([S1, S2], [0.9, 0.1])),
                     "bruit commun dans chaque morceau": _par(_mel([S1, q], [0.7, 0.3]), _mel([S2, q], [0.7, 0.3])),
                     "même partition imbriquée": _par(_par(S1, S2), S2), "même seuil imbriqué": _si(0, 0.5, _si(0, 0.5, S1, S2), S2),
                     "mélange de deux lois sur la même partition": _mel([_par(S1, S2), _par(S2, S1)], [0.5, 0.5]),
                     "identités": {"type": "transformee", "base": {"type": "echelle", "facteurs": [1, 1], "loi": {"type": "enveloppe", "lois": [_par(S1, S2)]}}, "puissance": 1},
                     "fixe": q, "S1": S1}
        for nom, loi in couvertes.items():
            with self.subTest(nom):
                self.assertTrue(a4.structurellement_couverte(loi, self.L))
                self.assertFalse(a4.hors_classe(loi, self.L, -0.5))
        # la classe de la v2 est contenue dans celle de la v4
        for loi in ag.ProposeurScripte.candidats_hors_classe(S1, S2) + [S1, S2, q, _mel([S1, S2], [0.4, 0.6])]:
            if ag.structurellement_couverte(loi, self.L):
                self.assertTrue(a4.structurellement_couverte(loi, self.L))

    def test_artefacts_lois_hors_de_la_classe(self):
        S1, S2, q = self.S1, self.S2, self.q
        hors = {"bruit propre au morceau (H04)": _par(_mel([S1, q], [0.8, 0.2]), _mel([S2, {"type": "fixe", "probas": [1, 1, 2]}], [0.8, 0.2])),
                "loi aveugle seule sur un morceau": _par(q, S2), "profondeur 2 (H01)": _par(_si(0, 0.0, S1, S2), S2),
                "deux seuils (H02)": _si(0, 0.5, S1, _si(0, -0.5, S2, S1)), "deux traits": _si(1, 0.0, _si(0, 0.0, S1, S2), S2),
                "mélange de deux partitions": _mel([_si(0, 0.0, S1, S2), _par(S1, S2)], [0.5, 0.5]),
                "morceau tempéré (H05)": _par({"type": "transformee", "base": S1, "puissance": 1.5}, S2)}
        for nom, loi in hors.items():
            with self.subTest(nom):
                self.assertFalse(a4.structurellement_couverte(loi, self.L))
                self.assertTrue(a4.hors_classe(loi, self.L, -0.5))
        for i, loi in enumerate(a4.candidats_hors_classe_v9(S1, S2)):
            with self.subTest(candidat=i):
                ag.grammaire_servie(loi)
                self.assertFalse(a4.structurellement_couverte(loi, self.L))
        self.assertTrue(a4.hors_classe(S1, self.L, 1.0), "une loi couverte à log W > 10⁻⁶ est comptée hors classe (R13)")


# --- proposeur scripté ------------------------------------------------------------------------------------------------------------
class ProposeurScripte(unittest.TestCase):
    def test_sortant_v9_sous_v9_et_v2_sous_l_ancien(self):
        c = carte(0, "W2")
        p = a4.ProposeurScripte("sortant_v9")
        t9 = json.loads(p(a4.consigne(c, [], "retour", 1, "v9"), "m")[0])
        self.assertEqual(t9["loi"], a4.candidats_hors_classe_v9(c["L"]["S1"], c["L"]["S2"])[0])
        ta = json.loads(p(a4.consigne(c, [], "retour", 1, "ancien"), "m")[0])
        self.assertEqual(ta["loi"], ag.ProposeurScripte.candidats_hors_classe(c["L"]["S1"], c["L"]["S2"])[0])
        m = json.loads(a4.ProposeurScripte("melangeur")(a4.consigne(c, [], "retour", 1, "v9"), "m")[0])
        self.assertTrue(a4.structurellement_couverte(m["loi"], c["L"]))
        with self.assertRaises(a4.AttaqueRefusee):
            a4.ProposeurScripte("autre")


# --- suites, plan, grille, étiquettes -------------------------------------------------------------------------------------------
class SuitesEtPlan(unittest.TestCase):
    def test_suite_v9_journal_nul_et_classe(self):
        """Une suite sous v9 (proposeur sortant de la v2 sur W2, 2 tentatives) : nul écrit, v8 apparié au journal, lois couvertes
        par le v9 comptées dans la classe (hors classe faux), jamais promues ; la suite « ancien » sous v8 est promue à k = 1."""
        c = carte(0, "W2")
        cpt = a3.Compteur(100.0, 3600.0, __import__("time").time, [ARGON])
        s = a4.jouer_suite(a4.ProposeurScripte("sortant"), c, "argon", "retour", "v9", G, cpt, "gemini-4-argon", n_max=2)
        self.assertEqual((s["juge"], s["nul"], s["premiere_promotion"]), ("v9", "v9", None))
        self.assertEqual([t["hors_classe"] for t in s["tentatives"]], [False, False])
        self.assertTrue(all("v8_apparie" in t["verdict"] for t in s["tentatives"]))
        sa = a4.jouer_suite(a4.ProposeurScripte("sortant"), c, "argon", "retour", "ancien", G, cpt, "gemini-4-argon", n_max=2)
        self.assertEqual((sa["nul"], sa["premiere_promotion"]), ("v8", 1))
        with self.assertRaises(a4.AttaqueRefusee):
            a4.jouer_suite(a4.ProposeurScripte(), c, "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=1)

    def test_etiquettes_distinctes_et_roles(self):
        e = a4.etiquettes_du_plan(["W1", "W2"], [ARGON])
        self.assertEqual(a4.verifier_cles_distinctes(e), e)
        self.assertEqual(len(e), 77)
        self.assertIn("W2|argon|retour|ancien|scenario", e)
        self.assertIn("rejeu|W1|argon|temoin|v9|frais", e)
        self.assertFalse(set(e) & set(a3.etiquettes_du_plan(["W1", "W2"], [ARGON])) - {"bootstrap", "monde|W1", "monde|W2",
                                                                                         "developpement|W1", "developpement|W2"})

    def test_plan_cas_sain_et_artefacts(self):
        p = a4.verifier_plan({"mode": "course", "cartes": 24, "mondes": ["W1", "W2"], "fournisseurs": [ARGON], "rejeux": dict(a4.REJEUX)})
        self.assertEqual((p["unites_par_case"], p["eps"]), (24, 0.25))
        cas = {"grille 48": dict(cartes=48), "grille 6": dict(cartes=6), "rejeux d'un plan v3": dict(rejeux={"v8": 200, "v7": 20}),
               "mode essai": dict(mode="essai"), "monde inconnu": dict(mondes=["W3"])}
        for nom, kw in cas.items():
            base = {"mode": "course", "cartes": 24, "mondes": ["W1", "W2"], "fournisseurs": [ARGON], "rejeux": dict(a4.REJEUX)}
            with self.subTest(nom), self.assertRaises(a4.AttaqueRefusee):
                a4.verifier_plan(dict(base, **kw))
        r, b = a4.regles_de_lecture(24, 0.25)
        self.assertEqual((r, b), (1, 4))
        self.assertAlmostEqual(ag.wilson(0, 24)[1], 0.138, places=3)

    def test_devis_du_plan_decide(self):
        d = a4.devis(24, ["W1", "W2"], [ARGON])["total"]
        self.assertEqual((d["appels_attendus"], d["appels_max"], d["usd_max"]), ([1680, 2112], 3072, 190.46))
        self.assertEqual(d["evaluations_v9_rejeux"], 307200)
        self.assertAlmostEqual(d["rejeux_h"], 307200 * 0.5 / 7200 + (24 * 32 * 20 * 0.011 + 24 * 8 * 20 * 0.056) / 7200, places=2)
        self.assertLess(d["duree_attendue_haute_h"], 72)
        self.assertLess(d["duree_max_h"], 72)
        self.assertGreater(d["duree_attendue_haute_h"], 23.47 + d["rejeux_h"])
        self.assertLessEqual(d["usd_max"], 200)


# --- lecture -----------------------------------------------------------------------------------------------------------------------
def suite_synth(monde, carte_, condition, juge, promue_k=None, n=3, motif=None):
    tent = []
    for k in range(1, (promue_k or n) + 1):
        promue = k == promue_k
        v = {"statut": "promue" if promue else "non_promue", "promue": promue, "log_w_max": 5.0 if promue else -1.0, "dominant": "x",
             "motif": None, "nul": a4.nul_du_juge(juge, monde)}
        if motif and k == 1:
            v = dict(v, statut="evaluation_impossible", promue=False, log_w_max=None, motif=motif)
        t = {"k": k, "appels": [{"statut": "ok", "cause": None, "attente_s": 0.0}], "loi": {"type": "fixe", "probas": [k, 1, 1]},
             "verdict": v, "hors_classe": True, "couverte": False}
        if condition == "retour" and k > 1:
            t.update(retour_attendu=-1.0, echo_exact=True)
        tent.append(t)
    return {"monde": monde, "carte": carte_, "fournisseur": "argon", "modele": "gemini-4-argon", "repli": False, "condition": condition,
            "juge": juge, "nul": a4.nul_du_juge(juge, monde), "premiere_promotion": promue_k, "tentatives": tent}


def monde_synth(monde, promues_v9=0, promues_ancien=24, motif=None):
    s = []
    for c in range(24):
        for cond, j in a4.SUITES:
            k = 1 if (j == "v9" and cond == "retour" and c < promues_v9) or (j == "ancien" and c < promues_ancien) else None
            s.append(suite_synth(monde, c, cond, j, k, motif=motif if (c == 0 and j == "v9" and cond == "retour") else None))
    return s


class Lecture(unittest.TestCase):
    def lire(self, suites, rejeux=(), audits=(), monde="W2"):
        return a4.lire_monde(list(suites), list(rejeux), list(audits), monde, 24, G, [ARGON])

    def test_w1_et_w2_lus_en_resistance(self):
        for w in ("W1", "W2"):
            with self.subTest(w):
                m = self.lire(monde_synth(w), monde=w)
                self.assertEqual(m["issue"], "résiste (à cette taille)")
                self.assertEqual((m["juge_ancien"], m["breche"], m["dents"]), (a4.JUGE_ANCIEN[w], False, True))
                self.assertTrue(all(m["predictions"].values()), m["predictions"])
                self.assertIn("v9|retour|n=16|ensemble", m["taux"])

    def test_artefacts_breche_sans_dents_et_qualification(self):
        m = self.lire(monde_synth("W2", promues_v9=4), audits=[{"monde": "W2", "au_dessus_de_alpha_holm": False, "rejeux": 200}])
        self.assertEqual((m["issue"], m["qualification_breche"]), ("infirmée (brèche sous v9)", "brèche par multiplicité"))
        m = self.lire(monde_synth("W2", promues_v9=4), audits=[{"monde": "W2", "au_dessus_de_alpha_holm": True, "rejeux": 200}])
        self.assertEqual(m["qualification_breche"], "brèche par défaut du juge")
        self.assertFalse(m["predictions"]["P6"])
        m = self.lire(monde_synth("W1", promues_ancien=0), monde="W1")
        self.assertEqual(m["issue"], "non jugeable (attaque sans dents)")
        self.assertEqual(self.lire(monde_synth("W2", promues_v9=2))["issue"], "non jugeable (précision insuffisante)")

    def test_a3_sur_w2_et_monotonie_comptee(self):
        r = [{"monde": "W2", "juge": "v9", "prefixe": "rejeu", "rejeux": 200, "promues": 40, "etiquette": "W2|argon|retour|v9", "carte": 3, "k": 2}]
        m = self.lire(monde_synth("W2"), rejeux=r)
        self.assertTrue(any(a.startswith("A3") for a in m["audits"]))
        m = self.lire(monde_synth("W2", motif="MonotonieViolee : W2|argon|retour|v9 répétition 1"))
        self.assertEqual(m["violations_de_monotonie"], 1)
        self.assertFalse(m["predictions"]["P4"])
        self.assertTrue(any(a.startswith("A6") and "monotonie" in a for a in m["audits"]))


# --- rejeux et audit A2 ------------------------------------------------------------------------------------------------------------
class Rejeux(unittest.TestCase):
    def test_rejeux_sous_v9_un_ou_deux_processus_et_audit_des_promues_v9(self):
        c = carte(0, "W2")
        s9 = suite_synth("W2", 0, "retour", "v9", promue_k=1)
        s9["tentatives"][0]["loi"] = c["monde"]
        sa = suite_synth("W2", 0, "retour", "ancien", promue_k=1)
        sa["tentatives"][0]["loi"] = c["monde"]
        r1 = a4.rejouer_tout([s9, sa], G, {"v9": 2, "ancien": 2}, processus=1)
        r2 = a4.rejouer_tout([s9, sa], G, {"v9": 2, "ancien": 2}, processus=2)
        self.assertEqual(r1, r2)
        self.assertEqual({(r["juge"], r["nul"], r["promues"]) for r in r1}, {("v9", "v9", 0), ("ancien", "v8", 2)})
        audits = a4.auditer_promues([s9, sa], G, rejeux=3)
        self.assertEqual([(a["juge"], a["rejeux"], a["promues"], a["au_dessus_de_alpha_holm"]) for a in audits], [("v9", 3, 0, False)])
        self.assertEqual([a["etiquette"] for a in audits], ["W2|argon|retour|v9"], "audit A2 : les lois promues sous v9, jamais sous l'ancien juge")


# --- lanceur : texte, plan, refus croisés v3/v4 --------------------------------------------------------------------------------
LIGNE_ARGON = "type=commande_externe, port=8805, modele=gemini-4-argon, fils=1, taux_usd=0.062, secondes=7.6-40"


def texte_v4(gel=None, grille="24 cartes par monde, 24 unités par case", plafond="200", duree="72", fixe=None, conf_sha="c" * 64,
             go="GO-2026-11-02-22", sans=(), plus="", marqueur="", ligne_argon=LIGNE_ARGON, mode="course"):
    gel = gel if gel is not None else [(sha256_fichier(os.path.join(RACINE, r)), r) for r in lanceur.FICHIERS_GELES]
    corps = [f"mode: {mode}", f"grille: {grille}", "mondes: W1 et W2", "fournisseurs: argon", f"fournisseur_argon: {ligne_argon}",
             "essais_avant_repli: 3", "relais_perdu_h: aucun", f"plafond_usd: {plafond}", f"duree_max_h: {duree}",
             "decision_ecart: registre d'essai, D-0", f"configuration_sha256: {conf_sha}", f"go: {go}"]
    corps += [f"{k}: {v}" for k, v in dict(lanceur.PLAN_FIXE, **(fixe or {})).items()]
    corps = [l for l in corps if not any(l.startswith(s + ":") for s in sans)]
    return ("# Texte d'essai v4\n\n" + lanceur.DEBUT_EMPREINTES + "\n```\n" + "".join(f"{h}  {p}\n" for h, p in gel) + "```\n"
            + lanceur.FIN_EMPREINTES + "\n\n" + lanceur.DEBUT_PLAN + "\n```\n" + "\n".join(corps) + "\n" + plus + "```\n" + lanceur.FIN_PLAN
            + "\n" + marqueur)


class LanceurPlan(unittest.TestCase):
    def test_plan_decide_lu_du_texte(self):
        p = lanceur.lire_plan(texte_v4())
        self.assertEqual((p["cartes"], p["unites_par_case"], p["eps"], p["mondes"], p["relais_perdu_s"], p["plafond_usd"]),
                         (24, 24, 0.25, ["W1", "W2"], None, 200.0))
        self.assertEqual((p["fournisseurs"][0]["fils"], p["rejeux"], p["rejeux_audit"]), (1, {"v9": 200, "ancien": 20}, 200))
        self.assertEqual(p["devis"]["total"]["usd_max"], 190.46)

    def test_artefacts_du_plan(self):
        cas = [("bloc de la v3 (rejeux_v8, rejeux_v7)", dict(sans=("rejeux_v9", "rejeux_ancien", "juge_ancien"), plus="rejeux_v8: 200\nrejeux_v7: 20\n"), "clés attendues"),
               ("juge ancien changé", dict(fixe={"juge_ancien": "W1=v8, W2=v8"}), "le code gelé dit"),
               ("rejeux v9 réduits", dict(fixe={"rejeux_v9": "20"}), "le code gelé dit"),
               ("grille 48", dict(grille="48 cartes par monde, 48 unités par case", plafond="400", duree="200"), "non admise"),
               ("grille 6", dict(grille="6 cartes par monde, 6 unités par case"), "non admise"),
               ("mode essai", dict(mode="essai"), "mode = course"),
               ("plafond sous le devis", dict(plafond="190"), "sous le maximum du devis"),
               ("durée sous la durée attendue haute", dict(duree="40"), "durée"),
               ("configuration non levée", dict(conf_sha="<<CASE_CONFIGURATION>>"), "configuration_sha256"),
               ("GO mal formé", dict(go="GO-22"), "go = ")]
        for nom, kw, motif in cas:
            with self.subTest(cas=nom), self.assertRaisesRegex(lanceur.PreenregistrementRefuse, motif):
                lanceur.lire_plan(texte_v4(**kw))


class LanceurPreenregistrement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.p4 = unittest.mock.patch.object(lanceur, "DOSSIER_PREREG", self.tmp)
        self.p3 = unittest.mock.patch.object(lanceur_v3, "DOSSIER_PREREG", self.tmp)
        self.p4.start()
        self.p3.start()

    def tearDown(self):
        self.p4.stop()
        self.p3.stop()

    def ecrire(self, texte, nom, sceller=True):
        p = os.path.join(self.tmp, nom)
        if sceller:
            ecrire_scelle(p, texte)
        else:
            with open(p, "w", encoding="utf-8") as f:
                f.write(texte)
        return p

    def test_cas_sain(self):
        e, h, gelees, p = lanceur.lire_preenregistrement(self.ecrire(texte_v4(), "preenregistrement-attaque-goodhart-v4-v1.md"))
        self.assertGreaterEqual(e, 2 ** 64)
        self.assertEqual(sorted(gelees), sorted(lanceur.FICHIERS_GELES))
        for f in ("pole/nul_v9.py", "demonstrations/banc_tricheurs_v9.py", "pole/attaque_goodhart_v4.py", "pole/attaque_goodhart_v3.py"):
            self.assertIn(f, gelees)
        self.assertEqual(p["go"], "GO-2026-11-02-22")

    def test_refus_croises_v3_et_v4(self):
        """Le lanceur v4 refuse un texte de la v3 (nom ; et, renommé v4, son bloc) ; le lanceur v3 refuse un texte de la v4 (nom ;
        et, renommé v3, son bloc)."""
        gel3 = [(sha256_fichier(os.path.join(RACINE, r)), r) for r in lanceur_v3.FICHIERS_GELES]
        texte3 = texte_v4(gel=gel3, sans=("rejeux_v9", "rejeux_ancien", "juge_ancien"), plus="rejeux_v8: 200\nrejeux_v7: 20\n",
                          plafond="200", duree="72")
        cas4 = [("nom de la v3", texte_v4(), "preenregistrement-attaque-goodhart-v3-v1.md", "pas"),
                ("brouillon", texte_v4(), "preenregistrement-attaque-goodhart-v4-brouillon1.md", "pas"),
                ("texte v3 renommé v4 (fermeture de la v3)", texte3, "preenregistrement-attaque-goodhart-v4-v2.md", "manquants"),
                ("fermeture de la v3, bloc v4", texte_v4(gel=gel3), "preenregistrement-attaque-goodhart-v4-v7.md", "manquants"),
                ("texte v3 renommé v4, bloc v3, code v4 gelé", texte_v4(sans=("rejeux_v9", "rejeux_ancien", "juge_ancien"), plus="rejeux_v8: 200\nrejeux_v7: 20\n"),
                 "preenregistrement-attaque-goodhart-v4-v3.md", "clés attendues"),
                ("marqueur", texte_v4(marqueur="<<EMPREINTES_AU_COMMIT>>\n"), "preenregistrement-attaque-goodhart-v4-v4.md", "marqueur")]
        for nom, texte, fichier, motif in cas4:
            with self.subTest(lanceur="v4", cas=nom), self.assertRaisesRegex(lanceur.PreenregistrementRefuse, motif):
                lanceur.lire_preenregistrement(self.ecrire(texte, fichier))
        p = self.ecrire(texte_v4(), "preenregistrement-attaque-goodhart-v4-v5.md", sceller=False)
        with self.assertRaisesRegex(lanceur.PreenregistrementRefuse, "non scellé"):
            lanceur.lire_preenregistrement(p)
        cas3 = [("nom de la v4", texte_v4(), "preenregistrement-attaque-goodhart-v4-v6.md", "pas"),
                ("texte v4 renommé v3", texte_v4(), "preenregistrement-attaque-goodhart-v3-v2.md", "en trop|clés attendues")]
        for nom, texte, fichier, motif in cas3:
            with self.subTest(lanceur="v3", cas=nom), self.assertRaisesRegex(lanceur_v3.PreenregistrementRefuse, motif):
                lanceur_v3.lire_preenregistrement(self.ecrire(texte, fichier))
        with self.assertRaisesRegex(lanceur_v3.PreenregistrementRefuse, "clés attendues"):  # bloc v4 sous la lecture de la v3
            lanceur_v3.lire_plan(texte_v4(), mode_attendu="course")


def commande_argon(dossier, texte, cout=0.002):
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, "argon.py")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("import json, os, sys\nsys.stdin.read()\n"
                f"print(json.dumps({{'texte': {texte!r}, 'cout_usd': {cout}, 'modele_servi': os.environ.get('MODELE_DEMANDE_POLE')}}))\n")
    return [sys.executable, "-I", "-B", chemin]


class LanceurCheminReel(unittest.TestCase):
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
        loi = json.dumps({"retour_lu": "aucun", "loi": {"type": "fixe", "probas": [2, 1, 1]}})
        conf["fournisseurs"] = {"argon": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                                          "commande": commande_argon(self.tmp, loi) + ["--port", "8805", "--registre", "{REGISTRE}",
                                                                                       "--plafond-cumule-usd", "80"]}}
        conf["proposeurs"] = [{"etiquette": "prop-argon", "modele": "gemini-4-argon", "fournisseur": "argon", "consigne": "consigne_proposeur"}]
        self.conf = conf
        self.chemin_conf = os.path.join(self.tmp, "conf.json")
        with open(self.chemin_conf, "w", encoding="utf-8") as f:
            json.dump(conf, f)
        self.prereg = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v4-v1.md")
        ecrire_scelle(self.prereg, texte_v4(conf_sha=sha256_fichier(self.chemin_conf)))
        self.registre = A54.registre_go(self.tmp, A54.ligne_go("GO-2026-11-02-22", "200 USD", perimetre="attaque v4"),
                                        A54.ligne_go("GO-2026-11-02-17", "191 USD", perimetre="attaque v3"))
        self.sortie = os.path.join(self.tmp, "sortie")

    def tearDown(self):
        self.patch.stop()
        self.env.stop()

    def argv(self, *plus):
        return [self.sortie, "--preenregistrement", self.prereg, "--configuration", self.chemin_conf, "--moteur", "reel",
                "--confirmer-moteur-reel", "--registre-go", self.registre, "--go", "GO-2026-11-02-22", *plus]

    def test_verifier_seulement_etape_v4_aucune_ecriture(self):
        from pole import configuration_v56 as cfg
        self.assertEqual(lanceur.principal(self.argv("--verifier-seulement")), 0)
        self.assertFalse(os.path.exists(self.sortie))
        plan = lanceur.lire_plan(texte_v4(conf_sha=sha256_fichier(self.chemin_conf)))
        sortie = os.path.join(self.tmp, "s-etape")
        os.makedirs(sortie)
        props, accuses, infos = lanceur.proposeurs_reels(cfg.lire_configuration_v56(self.conf, base=self.tmp), plan, tempfile.mkdtemp(), sortie)
        self.assertEqual((accuses["argon"]["etape"], accuses["argon"]["plafond_usd"]), ("attaque_goodhart_v4/argon", 200.0))
        self.assertEqual(infos["etapes_de_depense"]["argon"]["etape"], "attaque_goodhart_v4/argon")
        self.assertNotEqual(lanceur.etape_du_fournisseur("argon"), lanceur_v3.etape_du_fournisseur("argon"))

    def test_refus_du_lanceur_isoles(self):
        v3 = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v3-v1.md")
        ecrire_scelle(v3, texte_v4(conf_sha=sha256_fichier(self.chemin_conf)))
        for nom, argv in (("GO de la v3", self.argv()[:-1] + ["GO-2026-11-02-17"]), ("texte au nom de la v3", self.argv()[:2] + [v3] + self.argv()[3:]),
                          ("option de plan", self.argv("--fils", "2")), ("graine en réel", self.argv("--graine", "7")),
                          ("rejeux en ligne de commande", self.argv("--rejeux-v9", "2"))):
            with self.subTest(cas=nom):
                self.assertEqual(lanceur.principal(argv + ["--verifier-seulement"]), 2)
                self.assertFalse(os.path.exists(self.sortie))


class LanceurABlanc(unittest.TestCase):
    def test_refus_avant_toute_ecriture(self):
        with tempfile.TemporaryDirectory() as d:
            s = os.path.join(d, "s")
            for argv in (["--graine", str(2 ** 64)], ["--graine", "7", "--fournisseurs", "gemini"], ["--graine", "7", "--relais-perdu-h", "0"],
                         ["--graine", "7", "--rejeux-v9", "-1"]):
                with self.subTest(argv=argv):
                    self.assertEqual(lanceur.principal([s, "--a-blanc", *argv]), 2)
            self.assertFalse(os.path.exists(s))

    def test_a_blanc_de_bout_en_bout(self):
        with tempfile.TemporaryDirectory() as d:
            s = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([s, "--a-blanc", "--graine", "7", "--cartes", "1", "--n-max", "2", "--rejeux-v9", "1",
                                                "--rejeux-ancien", "1", "--rejeux-audit", "2", "--processus", "1"]), 0)
            with open(os.path.join(s, "attaque-goodhart-v4.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertEqual(sorted(r["lecture"]["issues"]), ["W1", "W2"])
            self.assertEqual({x["juge"] for x in r["suites"]}, {"v9", "ancien"})
            self.assertEqual({(x["monde"], x["nul"]) for x in r["suites"] if x["juge"] == "ancien"}, {("W1", "v7"), ("W2", "v8")})
            with open(os.path.join(s, "manifeste.json"), encoding="utf-8") as f:
                m = json.load(f)
            self.assertEqual(sorted(m["reglages"]["code_sha256"]), sorted(lanceur.FICHIERS_GELES))
            self.assertTrue(os.path.isfile(os.path.join(s, "attaque-goodhart-v4.json.sha256")))


class Fermeture(unittest.TestCase):
    def test_fichiers_geles_egaux_a_la_fermeture(self):
        """Le code que le chemin réel v4 importe (processus neuf, imports et chargements par fichier, bancs v8 et v9 chargés) est
        exactement `FICHIERS_GELES` : la fermeture de la v3 plus les deux fichiers v4, le nul v9 et le banc v9."""
        script = (
            "import importlib.util, json, os, sys\nR = os.path.realpath(sys.argv[1])\nvus = set()\n"
            "def crochet(e, a):\n    if e == 'open' and a and isinstance(a[0], str) and a[0].endswith(('.py', '.pyc')):\n"
            "        vus.add(os.path.realpath(a[0]))\nsys.addaudithook(crochet)\nsys.path.insert(0, R)\n"
            "s = importlib.util.spec_from_file_location('l', os.path.join(R, 'demonstrations', 'attaque_goodhart_v4.py'))\n"
            "m = importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\nm.l2.charger_ideation_v8()\nm.ag.banc()\nm.a4.banc_v9()\n"
            "import pole.relais, pole.configuration_v56, pole.adaptateurs_v56\n"
            "f = {os.path.realpath(getattr(x, '__file__', '') or '') for x in list(sys.modules.values())} | vus\n"
            "def source(p):\n    if p.endswith('.pyc') and os.path.basename(os.path.dirname(p)) == '__pycache__':\n"
            "        p = os.path.join(os.path.dirname(os.path.dirname(p)), os.path.basename(p).split('.')[0] + '.py')\n    return p\n"
            "print(json.dumps(sorted({os.path.relpath(source(p), R) for p in f if p.startswith(R + os.sep)})))\n")
        sortie = subprocess.run([sys.executable, "-I", "-B", "-c", script, RACINE], capture_output=True, text=True, check=True)
        self.assertEqual(sorted(json.loads(sortie.stdout)), sorted(lanceur.FICHIERS_GELES))
        self.assertEqual(len(lanceur.FICHIERS_GELES), len(lanceur_v3.FICHIERS_GELES) + 4)


if __name__ == "__main__":
    unittest.main()
