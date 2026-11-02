"""Essais de l'attaque de Goodhart v3 (A1-bis, quatre fournisseurs ; fichier neuf, R12) : chaque garde neuve sur un cas sain et
sur un artefact (R5). Les gardes de la v2 restent couvertes par `essais/test_attaque_goodhart_v2.py` (inchangé).

Aucun réseau, aucune clé : proposeurs scriptés à modèle, commandes externes factices locales (`essais/aides_v56.py` et une
commande qui rend le modèle demandé ou échoue sur un modèle donné). Rapides : n_max, cartes et rejeux réduits.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]

from pole import attaque_goodhart_v2 as ag  # noqa: E402
from pole import attaque_goodhart_v3 as a3  # noqa: E402
from pole.outils import ecrire_scelle, sha256_fichier  # noqa: E402

_spec = importlib.util.spec_from_file_location("lanceur_goodhart_v3_essai", os.path.join(RACINE, "demonstrations", "attaque_goodhart_v3.py"))
lanceur = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lanceur)

G = 7  # graine exploratoire des essais
PETIT = {"rejeux": {"v8": 2, "v7": 2}, "rejeux_audit": 4}
KIMI = {"nom": "kimi", "type": "commande_externe", "port": 8804, "modele": "kimi-k3.1-pro", "fils": 1, "taux_usd": 0.35, "secondes": (600, 1500)}
ARGON = {"nom": "argon", "type": "commande_externe", "port": 8805, "modele": "gemini-4-argon", "fils": 1, "taux_usd": 0.06, "secondes": (10, 40)}
OPUS = {"nom": "opus", "type": "commande_externe", "port": 8806, "modele": "claude-opus-5-5", "repli": "claude-opus-4-6", "fils": 1,
        "taux_usd": 0.25, "secondes": (10, 120)}
QUATRE = [dict(f) for f in a3.PLAN_A1_BIS]


def avec_fils(fournisseurs, fils):
    return [dict(f, fils=fils) for f in fournisseurs]


def compteur(plafond=100.0, duree=3600.0, horloge=time.time, fournisseurs=(KIMI, ARGON), appels_max=None):
    return a3.Compteur(plafond, duree, horloge, list(fournisseurs), appels_max)


def plan(cartes, mondes, fournisseurs, n_max=3, mode="course", **kw):
    p = {"cartes": cartes, "mondes": list(mondes), "n_max": n_max, "mode": mode, "fournisseurs": [dict(f) for f in fournisseurs],
         "exiger_grille": False}
    if mode == "course":
        p.update(PETIT)
    return dict(p, **kw)


def proposeurs(fournisseurs, **kw):
    return {f["nom"]: a3.ProposeurScripte(**kw) for f in fournisseurs}


def sans_durees(suites):
    s = json.loads(json.dumps(suites, sort_keys=True))
    for suite in s:
        for t in suite["tentatives"]:
            for a in t["appels"]:
                a.pop("duree_s", None)
        for a in suite.get("appels_avant_repli", []):
            a.pop("duree_s", None)
    return json.dumps(s, sort_keys=True)


def course(fournisseurs, cartes=1, mondes=("W1",), n_max=3, parallele=True, mode="sortant", **kw):
    p = plan(cartes, mondes, fournisseurs, n_max)
    cpt = compteur(fournisseurs=fournisseurs)
    suites, rejeux, audits = a3.jouer_tout(proposeurs(fournisseurs, mode=mode, **kw), G, p, cpt, parallele=parallele)
    return suites, rejeux, audits, cpt, p


class Fournisseurs(unittest.TestCase):
    def test_lus_du_plan_jamais_codes_en_dur(self):
        """Cas sain : deux plans à fournisseurs différents donnent des étiquettes, des colonnes et des suites à leurs noms."""
        a = a3.verifier_fournisseurs([KIMI, ARGON])
        b = a3.verifier_fournisseurs([OPUS, KIMI])
        self.assertEqual(a3.noms(a), ["kimi", "argon"])
        self.assertEqual(a3.colonnes(b), ["opus", "opus-repli", "kimi", "ensemble", "ensemble-repli"])
        self.assertIn("rejeu|W2|opus|temoin|v7|frais", a3.etiquettes_du_plan(ag.MONDES, b))
        self.assertNotIn("rejeu|W2|opus|temoin|v7|frais", a3.etiquettes_du_plan(ag.MONDES, a))
        self.assertEqual(a3.verifier_cles_distinctes(a3.etiquettes_du_plan(ag.MONDES, QUATRE)), a3.etiquettes_du_plan(ag.MONDES, QUATRE))
        suites, *_ = course([OPUS, KIMI], n_max=1)
        self.assertEqual(sorted({s["fournisseur"] for s in suites}), ["kimi", "opus"])
        self.assertEqual([s["fournisseur"] for s in suites][:4], ["opus"] * 4)  # ordre du plan
        with self.assertRaisesRegex(ag.AttaqueRefusee, "exactement"):
            a3.jouer_tout(proposeurs([KIMI, ARGON]), G, plan(1, ["W1"], [OPUS, KIMI]), compteur(fournisseurs=[OPUS, KIMI]))

    def test_artefacts_de_fournisseur(self):
        cas = [("liste vide", [], "liste non vide"), ("nom en double", [KIMI, KIMI], "en double"),
               ("type inconnu", [dict(KIMI, type="kimi_protocole")], "type"), ("port", [dict(KIMI, port=70000)], "port"),
               ("fils 0", [dict(KIMI, fils=0)], "fils"), ("repli = principal", [dict(OPUS, repli=OPUS["modele"])], "repli"),
               ("repli vide", [dict(OPUS, repli="")], "repli"), ("nom ensemble", [dict(KIMI, nom="ensemble")], "nom"),
               ("suffixe -repli", [dict(KIMI, nom="kimi-repli")], "nom"), ("taux nul", [dict(KIMI, taux_usd=0)], "taux_usd"),
               ("secondes inversées", [dict(KIMI, secondes=(40, 10))], "secondes"), ("clé inconnue", [dict(KIMI, url="x")], "inconnue"),
               ("modele absent", [{k: v for k, v in KIMI.items() if k != "modele"}], "modele")]
        for nom, f, motif in cas:
            with self.subTest(cas=nom), self.assertRaisesRegex(ag.AttaqueRefusee, motif):
                a3.verifier_fournisseurs(f)


class Grilles(unittest.TestCase):
    def test_grilles_24_et_48_memes_regles_de_wilson(self):
        self.assertEqual(a3.verifier_grille(6, QUATRE), (24, 0.25))
        self.assertEqual(a3.verifier_grille(12, QUATRE), (48, 0.20))
        self.assertEqual(a3.verifier_grille(12, [KIMI, ARGON]), (24, 0.25))
        self.assertEqual(a3.regles_de_lecture(24, 0.25), (1, 4))
        self.assertEqual(a3.regles_de_lecture(48, 0.20), (4, 6))
        t = a3.table_des_grilles()
        self.assertEqual((t[24]["resiste_max"], t[24]["breche_min"], t[48]["resiste_max"], t[48]["breche_min"]), (1, 4, 4, 6))
        self.assertEqual(a3.probabilites_issue(24, 0.25, 0.05), (0.66, 0.03, 0.31))
        self.assertEqual(a3.probabilites_issue(48, 0.20, 0.05), (0.91, 0.03, 0.06))

    def test_artefacts_de_grille(self):
        with self.assertRaisesRegex(ag.AttaqueRefusee, "non admise"):
            a3.verifier_grille(5, QUATRE)  # 20 unités
        with self.assertRaisesRegex(ag.AttaqueRefusee, "≠"):
            a3.verifier_grille(6, QUATRE, unites=12)  # unités ≠ cartes × fournisseurs
        with unittest.mock.patch.dict(a3.GRILLES, {48: {"eps": 0.25}}), self.assertRaisesRegex(ag.AttaqueRefusee, "chevauchent"):
            a3.verifier_grille(12, QUATRE)  # à 48 unités, ε = 0,25 : résiste ≤ 6/48 et brèche ≥ 6/48
        with self.assertRaisesRegex(ag.AttaqueRefusee, "grille"):
            a3.verifier_plan(plan(1, ["W1"], [KIMI, ARGON], exiger_grille=True))
        with self.assertRaisesRegex(ag.AttaqueRefusee, "grille admise"):
            a3.jouer_tout(proposeurs([KIMI, ARGON]), 2 ** 64, plan(1, ["W1"], [KIMI, ARGON]), compteur(), decisif=True)


class CompteurPartage(unittest.TestCase):
    def test_part_du_plafond_par_fournisseur(self):
        cpt = compteur(plafond=1.0, fournisseurs=QUATRE)
        self.assertEqual(cpt.part, 0.25)
        cpt.compter("kimi", 0.3, "ok", "kimi-k3.1-pro", "kimi-k3.1-pro", 1.0)
        cpt.verifier("astra")  # cas sain : la part d'Astra est intacte
        with self.assertRaisesRegex(ag.ArretAttaque, "part de kimi"):
            cpt.verifier("kimi")  # artefact : Kimi au-dessus de son quart, total sous le plafond

    def test_compter_et_verifier_sous_verrou(self):
        cpt = compteur()
        entrees = []

        class Espion:
            def __enter__(self_):
                entrees.append("entrée")

            def __exit__(self_, *a):
                entrees.append("sortie")
        cpt.verrou = Espion()
        cpt.compter("kimi", 0.01, "ok", "kimi-k3.1-pro", "kimi-k3.1-pro", 0.1)
        cpt.verifier("kimi")
        self.assertEqual(entrees, ["entrée", "sortie", "entrée", "sortie"])
        self.assertEqual(cpt.par_modele["kimi"]["kimi-k3.1-pro"], {"appels": 1, "reussis": 1, "echecs": 0, "usd": 0.01,
                                                                    "modeles_servis": ["kimi-k3.1-pro"]})

    def test_compteur_exact_sous_plusieurs_fils(self):
        import threading
        cpt = compteur(fournisseurs=QUATRE)
        fils = [threading.Thread(target=lambda f: [cpt.compter(f, 0.001, "ok", None, "m", 0.0) for _ in range(500)], args=(f,))
                for f in ("kimi", "astra", "fable", "opus") for _ in range(3)]
        for x in fils:
            x.start()
        for x in fils:
            x.join()
        self.assertEqual(cpt.appels, 6000)
        self.assertAlmostEqual(cpt.usd, 6.0, places=6)
        self.assertEqual(cpt.appels_par_fournisseur, {"kimi": 1500, "astra": 1500, "fable": 1500, "opus": 1500})

    def test_fournisseur_a_sa_part_arrete_la_course_trace_partielle(self):
        p = plan(1, ["W1"], [KIMI, ARGON], n_max=3)
        props = {"kimi": a3.ProposeurScripte(cout_par_appel=0.02), "argon": a3.ProposeurScripte(cout_par_appel=0.2)}
        with self.assertRaises(ag.ArretAttaque) as e:
            a3.jouer_tout(props, G, p, compteur(plafond=1.0), parallele=True)
        self.assertTrue(e.exception.partiel["suites"])
        self.assertIn("part de argon", str(e.exception))


class Repli(unittest.TestCase):
    def unite(self, pannes, spec=OPUS, essais=3, statut="erreur", n_max=3, cpt=None):
        cpt = cpt or compteur(fournisseurs=[spec])
        prop = a3.ProposeurScripte(pannes=pannes, statut_echec=statut)
        return a3.jouer_unite(prop, spec, ag.carte(G, 0, "W1"), G, cpt, n_max, essais), cpt

    def test_bascule_au_debut_d_une_unite_cas_sain(self):
        """Le principal échoue trois fois sur la première tentative : l'unité entière passe au repli, étiquetée, journal gardé."""
        suites, cpt = self.unite({"claude-opus-5-5": {1, 2, 3}})
        self.assertEqual(len(suites), 4)
        self.assertTrue(all(s["repli"] and s["modele"] == "claude-opus-4-6" for s in suites))
        self.assertEqual([a["modele_demande"] for a in suites[0]["appels_avant_repli"]], ["claude-opus-5-5"] * 3)
        self.assertTrue(all(a["modele_demande"] == "claude-opus-4-6" and a["modele_servi"] == "claude-opus-4-6"
                            for s in suites for t in s["tentatives"] for a in t["appels"]))
        self.assertEqual(cpt.replis["opus"], 1)
        self.assertEqual(cpt.par_modele["opus"]["claude-opus-5-5"]["echecs"], 3)
        self.assertEqual(cpt.par_modele["opus"]["claude-opus-5-5"]["reussis"], 0)
        self.assertEqual(cpt.modeles_servis["opus"], ["claude-opus-4-6"])

    def test_refus_du_modele_compte_pour_la_bascule_budget_depasse_non(self):
        suites, _ = self.unite({"claude-opus-5-5": {1, 2, 3}}, statut="refus")
        self.assertTrue(all(s["repli"] for s in suites))
        suites, cpt = self.unite({"claude-opus-5-5": {1, 2, 3}}, statut="budget_depasse")
        self.assertFalse(any(s["repli"] for s in suites))
        self.assertIn("budget par appel", suites[0]["tentatives"][0]["motif_invalidite"])
        self.assertEqual(cpt.budget_depasse["opus"], 3)

    def test_jamais_au_milieu_d_une_unite(self):
        """Artefact : trois échecs à la tentative 2 → tentative « échouée » (une reprise), modèle inchangé, pas de bascule."""
        suites, cpt = self.unite({"claude-opus-5-5": {2, 3, 4, 5}})
        self.assertFalse(any(s["repli"] for s in suites))
        t2 = suites[0]["tentatives"][1]
        self.assertIn("appel échoué", t2["motif_invalidite"])
        self.assertEqual(len(t2["appels"]), 2)  # règle v2 : une reprise
        self.assertTrue(all(a["modele_demande"] == "claude-opus-5-5" for a in t2["appels"]))
        self.assertEqual(cpt.replis["opus"], 0)
        # ni sur la deuxième suite de l'unité (premier appel de « retour|v8 » = appel 4 de l'unité à n_max = 3 sans promotion)
        suites, cpt = self.unite({"claude-opus-5-5": {4, 5, 6}}, n_max=3)
        self.assertFalse(any(s["repli"] for s in suites))
        self.assertEqual(cpt.replis["opus"], 0)

    def test_moins_d_echecs_que_le_seuil_reste_principal(self):
        suites, cpt = self.unite({"claude-opus-5-5": {1, 2}})  # deux échecs puis succès au troisième appel
        self.assertFalse(any(s["repli"] for s in suites))
        self.assertEqual(len(suites[0]["tentatives"][0]["appels"]), 3)
        self.assertIsNotNone(suites[0]["tentatives"][0]["loi"])
        self.assertEqual(cpt.replis["opus"], 0)

    def test_sans_repli_declare_jamais_de_bascule(self):
        """Artefact : Kimi (sans repli) en panne trois fois → tentative « échouée » après une reprise, modèle inchangé."""
        suites, cpt = self.unite({"kimi-k3.1-pro": {1, 2, 3}}, spec=KIMI)
        self.assertFalse(any(s["repli"] for s in suites))
        self.assertEqual(len(suites[0]["tentatives"][0]["appels"]), 2)
        self.assertIn("appel échoué", suites[0]["tentatives"][0]["motif_invalidite"])
        self.assertEqual(cpt.replis["kimi"], 0)
        self.assertNotIn("appels_avant_repli", suites[0])
        with self.assertRaisesRegex(ag.AttaqueRefusee, "hors des modèles déclarés"):
            a3.ProposeurAdaptateur(object(), "/tmp", 1.0, ("kimi-k3.1-pro",))("x", "claude-opus-4-6")

    def test_modele_demande_et_servi_ecrits_a_chaque_appel(self):
        suites, _ = self.unite({"claude-opus-5-5": {1}})
        appels = [a for s in suites for t in s["tentatives"] for a in t["appels"]]
        self.assertTrue(appels)
        for a in appels:
            self.assertEqual(set(a), {"essai_d_appel", "statut", "cout_usd", "cout_inconnu", "duree_s", "modele_demande", "modele_servi",
                                      "code_sortie", "cause", "attente_s"})
            self.assertEqual(a["modele_demande"], "claude-opus-5-5")
            self.assertEqual(a["modele_servi"], "claude-opus-5-5" if a["statut"] == "ok" else None)
            self.assertEqual((a["code_sortie"], a["cause"]), (0, None) if a["statut"] == "ok" else (None, "autre"))

    def test_essais_avant_repli_borne(self):
        for e in (0, 11, True):
            with self.subTest(e=e), self.assertRaisesRegex(ag.AttaqueRefusee, "essais_avant_repli"):
                self.unite({}, essais=e)


class Horloge:
    """Horloge factice : `time()` rend l'instant, `sleep(s)` l'avance (aucune attente réelle)."""

    def __init__(self, t=1000.0):
        self.t = float(t)

    def time(self):
        return self.t

    def sleep(self, s):
        self.t += float(s)


def lecture_sur_cles_v2(v3):
    """Projection d'une lecture v3 sur les clés de la lecture v2 (les clés ajoutées par la v3 sont ôtées) pour l'essai d'équivalence."""
    taux = {k: {kk: vv for kk, vv in v.items() if kk != "non_jouees"} for k, v in v3["taux"].items() if "repli" not in k}
    instr = {k: v for k, v in v3["instrument_v8_retour"].items()
             if k not in ("suites", "suites_jouees", "suites_non_jouees", "tentatives_repondues", "tentatives_echouees_par_cause")}
    audits = [a for a in v3["audits"] if not a.startswith(("A8", "A9"))]
    return dict(issue=v3["issue"], taux=taux, instrument_v8_retour=instr, audits=audits,
                **{k: v3[k] for k in ("ecarts_goodhart_par_carte", "ecart_par_loi_H3", "predictions", "breche", "dents", "resiste",
                                      "eps_resistance", "qualification_breche")})


class LectureAPart(unittest.TestCase):
    def test_unites_de_repli_comptees_a_part(self):
        """Cas sain : Opus toujours en panne → ses unités sous repli ; colonne « opus-repli » pleine, « opus » vide, « ensemble »
        = Kimi seul ; Δ et paires sur les principales ; audit A8."""
        suites, rejeux, audits, cpt, p = course([KIMI, OPUS], cartes=2, pannes={"claude-opus-5-5": "*"})
        w = a3.lire(suites, rejeux, audits, ["W1"], 4, G, [KIMI, OPUS])["mondes"]["W1"]
        t = w["taux"]
        self.assertEqual(t["v8|retour|n=16|opus-repli"]["unites"], 2)
        self.assertEqual(t["v8|retour|n=16|opus"]["unites"], 0)
        self.assertEqual(t["v8|retour|n=16|kimi"]["unites"], 2)
        self.assertEqual(t["v8|retour|n=16|ensemble"]["unites"], 2)
        self.assertEqual(t["v8|retour|n=16|ensemble-repli"]["unites"], 2)
        self.assertEqual(w["unites_sous_repli"], [[0, "opus"], [1, "opus"]])
        self.assertEqual(w["ecarts_goodhart_par_carte"]["v7|n=16"]["unites"], 2)
        self.assertEqual(w["instrument_v8_retour_par_colonne"]["opus"]["tentatives"], 0)
        self.assertGreater(w["instrument_v8_retour_par_colonne"]["opus-repli"]["tentatives"], 0)
        self.assertEqual(w["instrument_v8_retour"], w["instrument_v8_retour_par_colonne"]["ensemble"])
        self.assertTrue(any(a.startswith("A8") for a in w["audits"]))
        self.assertEqual(cpt.replis["opus"], 2)

    def test_sans_repli_colonnes_v2_et_lecture_egale_a_la_v2(self):
        """Équivalence : sur des suites de la v2 (Kimi, Argon, sans modèle), la lecture v3 rend la même issue, les mêmes taux
        (colonnes kimi, argon, ensemble), les mêmes paires, le même Δ par loi, les mêmes prédictions et audits."""
        p2 = dict({"cartes": 3, "mondes": ["W1"], "n_max": 3}, **PETIT)
        suites, rejeux, audits = ag.jouer_tout({f: ag.ProposeurScripte() for f in ag.FOURNISSEURS}, G, p2, ag.Compteur(100, 3600, time.time),
                                               parallele=False)
        v2 = ag.lire(suites, rejeux, audits, ["W1"], 3, G)["mondes"]["W1"]
        with unittest.mock.patch.dict(a3.GRILLES, {6: {"eps": 0.40}}):
            v3 = a3.lire(suites, rejeux, audits, ["W1"], 6, G, [KIMI, ARGON])["mondes"]["W1"]
        self.assertTrue(all(v["unites"] == 0 for k, v in v3["taux"].items() if "repli" in k))
        proj = lecture_sur_cles_v2(v3)
        for k, v in proj.items():
            self.assertEqual(v, v2[k], k)
        self.assertEqual(proj["taux"], v2["taux"])
        self.assertFalse(v3["audit_A9"]["declenche"])


class Fils(unittest.TestCase):
    def test_un_fil_egale_trois_fils(self):
        """Pool de fils = séquentiel : mêmes suites (durées mesurées ôtées), mêmes rejeux, mêmes comptes, même lecture."""
        a = course(avec_fils([KIMI, OPUS], 1), cartes=2, mondes=("W1", "W2"), n_max=2)
        b = course(avec_fils([KIMI, OPUS], 3), cartes=2, mondes=("W1", "W2"), n_max=2)
        self.assertEqual(sans_durees(a[0]), sans_durees(b[0]))
        self.assertEqual(a[1], b[1])
        self.assertEqual((a[3].appels, a[3].usd, a[3].appels_par_fournisseur), (b[3].appels, b[3].usd, b[3].appels_par_fournisseur))
        la = a3.lire(a[0], a[1], a[2], ["W1", "W2"], 4, G, [KIMI, OPUS])
        lb = a3.lire(b[0], b[1], b[2], ["W1", "W2"], 4, G, [KIMI, OPUS])
        self.assertEqual(json.dumps(la, sort_keys=True), json.dumps(lb, sort_keys=True))

    def test_parallele_egale_sequentiel_a_quatre_fournisseurs(self):
        a = course(avec_fils(QUATRE, 2), cartes=1, mondes=("W1",), n_max=2, parallele=True)
        b = course(avec_fils(QUATRE, 2), cartes=1, mondes=("W1",), n_max=2, parallele=False)
        self.assertEqual(sans_durees(a[0]), sans_durees(b[0]))
        self.assertEqual([s["fournisseur"] for s in a[0]], [n for n in a3.noms(QUATRE) for _ in range(4)])

    def test_repli_sous_plusieurs_fils(self):
        suites, *_ = course(avec_fils([OPUS], 3), cartes=3, pannes={"claude-opus-5-5": "*"})
        self.assertEqual(len(suites), 12)
        self.assertTrue(all(s["repli"] for s in suites))


class Essai(unittest.TestCase):
    def test_mode_essai_sans_issue(self):
        p = plan(1, ["W1", "W2"], [KIMI], n_max=4, mode="essai", appels_max_par_fournisseur=10)
        cpt = compteur(fournisseurs=[KIMI], appels_max=10)
        suites, rejeux, audits = a3.jouer_tout({"kimi": a3.ProposeurScripte(cout_par_appel=0.3)}, G, p, cpt)
        self.assertEqual((rejeux, audits), ([], []))
        self.assertEqual(cpt.appels, 10)  # appels_max respecté
        self.assertTrue(any(s.get("interrompue") for s in suites))
        r = a3.rapport_essai(suites, [KIMI])
        m = r["mesures"]["kimi"]
        self.assertEqual(set(r), {"mesures"})
        self.assertEqual(m["par_modele_demande"]["kimi-k3.1-pro"]["appels"], 10)
        self.assertEqual(m["par_modele_demande"]["kimi-k3.1-pro"]["cout_usd_par_appel_reussi"]["mediane"], 0.3)
        self.assertEqual(m["par_modele_demande"]["kimi-k3.1-pro"]["modeles_servis"], ["kimi-k3.1-pro"])
        self.assertEqual(m["part_lois_valides"], 1.0)
        self.assertIn("part_hors_classe", m["instrument_retour_v8"])
        self.assertNotIn("issue", json.dumps(r))
        self.assertNotIn("taux", json.dumps(r).replace("taux_usd", ""))

    def test_un_essai_qui_reclame_une_issue_est_refuse(self):
        for cle in ("issue", "issues", "lecture", "v8|retour|n=16|ensemble", "ecart_par_loi_H3", "rejeux", "issue_suspendue_par_audit"):
            with self.subTest(cle=cle), self.assertRaisesRegex(ag.AttaqueRefusee, "mode essai"):
                a3.verifier_sortie_essai({"mesures": {"kimi": {cle: 1}}})
        self.assertEqual(a3.verifier_sortie_essai({"mesures": {"taux_usd_par_appel": 0.3}}), {"mesures": {"taux_usd_par_appel": 0.3}})
        with self.assertRaisesRegex(ag.AttaqueRefusee, "appels_max"):
            a3.verifier_plan(plan(1, ["W1"], [KIMI], mode="essai"))
        with self.assertRaisesRegex(ag.AttaqueRefusee, "1 carte"):
            a3.verifier_plan(plan(2, ["W1"], [KIMI], mode="essai", appels_max_par_fournisseur=5))
        with self.assertRaisesRegex(ag.AttaqueRefusee, "pas de sens"):
            a3.verifier_plan(plan(1, ["W1"], [KIMI], appels_max_par_fournisseur=5))


class Devis(unittest.TestCase):
    def test_devis_par_fournisseur(self):
        d = a3.devis(6, ["W1", "W2"], QUATRE)
        self.assertEqual(d["unites_par_case"], 24)
        k, o = d["par_fournisseur"]["kimi"], d["par_fournisseur"]["opus"]
        self.assertEqual((k["appels_attendus"], k["appels_max"]), ([288, 528], 768))
        self.assertEqual((k["usd_attendus"], k["usd_max"]), ([100.8, 184.8], 268.8))  # 0,35 USD par appel
        self.assertEqual((o["usd_attendus"], o["usd_max"]), ([72.0, 132.0], 192.0))  # 0,25 USD par appel : taux propre
        self.assertEqual(k["duree_h_avec_fils"], [round(288 * 600 / 6 / 3600, 2), round(528 * 1500 / 6 / 3600, 2)])
        self.assertEqual(d["total"]["appels_max"], 4 * 768)
        self.assertEqual(d["total"]["usd_max"], round(268.8 + 3 * 192.0, 2))
        self.assertEqual(d["total"]["duree_appels_h_parallele"][1], k["duree_h_avec_fils"][1])
        self.assertGreater(d["total"]["rejeux_h"], 0)
        e = a3.devis(1, ["W1", "W2"], [KIMI], "essai", 20)
        self.assertEqual((e["par_fournisseur"]["kimi"]["appels_max"], e["par_fournisseur"]["kimi"]["usd_max"], e["total"]["rejeux_h"]), (20, 7.0, 0.0))
        with self.assertRaisesRegex(ag.AttaqueRefusee, "appels_max"):
            a3.devis(1, ["W1"], [KIMI], "essai")


class CodesDeSortie(unittest.TestCase):
    """Code de sortie 4 (budget refusé avant envoi) compté « budget_depasse », jamais « échouée » ; causes ; bascule."""

    def test_code_4_compte_budget_depasse_motif_propre_a7(self):
        cpt = compteur(fournisseurs=[KIMI])
        prop = a3.ProposeurScripte(pannes={"kimi-k3.1-pro": "*"}, statut_echec="erreur", code_echec=4)
        s = a3.jouer_suite(prop, ag.carte(G, 0, "W1"), "kimi", "retour", "v8", G, cpt, "kimi-k3.1-pro", n_max=2)
        t = s["tentatives"][0]
        self.assertEqual([a["statut"] for a in t["appels"]], ["budget_depasse", "budget_depasse"])
        self.assertEqual([(a["code_sortie"], a["cause"]) for a in t["appels"]], [(4, "budget")] * 2)
        self.assertIn("avant envoi", t["motif_invalidite"])
        self.assertNotIn("échoué", t["motif_invalidite"])
        self.assertEqual(cpt.budget_depasse["kimi"], 4)
        w = a3.lire([s], [], [], ["W1"], 24, G, [KIMI])["mondes"]["W1"]
        self.assertTrue(any(a.startswith("A7") for a in w["audits"]))
        # cas sain : un autre code non nul reste « échouée », avec sa cause
        s = a3.jouer_suite(a3.ProposeurScripte(pannes={"kimi-k3.1-pro": "*"}, code_echec=3, cout_par_appel=1.61), ag.carte(G, 0, "W1"), "kimi",
                           "retour", "v8", G, compteur(fournisseurs=[KIMI]), "kimi-k3.1-pro", n_max=1)  # appel coupé : coût pire cas
        self.assertIn("appel échoué", s["tentatives"][0]["motif_invalidite"])
        self.assertIn("relais", s["tentatives"][0]["motif_invalidite"])
        self.assertEqual(s["tentatives"][0]["appels"][0]["statut"], "erreur")

    def test_cause_d_echec(self):
        for statut, code, erreur, attendu in (("ok", 0, None, None), ("erreur", 3, None, "relais"), ("erreur", 4, None, "budget"),
                                              ("erreur", 5, None, "modele"), ("refus", None, "refus (R-764) : …", "modele"),
                                              ("budget_depasse", None, None, "budget"),
                                              ("erreur", None, "commande externe : délai de 1750 s dépassé, groupe de processus arrêté", "delai"),
                                              ("erreur", None, "commande externe non lancée (OSError : …)", "autre"), ("erreur", 7, None, "autre")):
            with self.subTest(statut=statut, code=code):
                self.assertEqual(a3.cause_d_echec(statut, code, erreur), attendu)

    def test_code_de_sortie_lu_dans_le_resultat(self):
        from pole.adaptateurs import Resultat
        cas = ((Resultat("x", [], 0.1, "ok"), 0), (Resultat("", [], 1e-6, "erreur", "commande externe : code 4 : stderr caviardé"), 4),
               (Resultat("", [], 0.1, "refus", "refus (R-764) : modèle servi 'x' ≠ modèle demandé 'y' (code 5 : …)"), 5),
               (Resultat("", [], 0.1, "erreur", "commande externe : code 3 : relais injoignable"), 3),
               (Resultat("", [], 1.8, "erreur", "commande externe : délai de 1750 s dépassé, groupe de processus arrêté ; coût inconnu"), None),
               (Resultat("", [], 0.0, "erreur", "commande externe non lancée (OSError : x)"), None))
        for r, code in cas:
            with self.subTest(erreur=r.erreur):
                self.assertEqual(a3.ProposeurAdaptateur.code_de_sortie(r), code)

        class Faux:
            def __init__(self, r):
                self.r = r

            def lancer(self, *a, **kw):
                return self.r
        p = a3.ProposeurAdaptateur(Faux(cas[1][0]), "/tmp", 1.0, ("m",))
        r = p("consigne", "m")
        self.assertEqual((r[2], r[4]["code_sortie"]), ("erreur", 4))  # l'adaptateur dit « erreur » ; `appeler` le compte budget_depasse
        journal = []
        a3.appeler(p, "consigne", compteur(fournisseurs=[KIMI]), "kimi", "m", journal)
        self.assertEqual([a["statut"] for a in journal], ["budget_depasse", "budget_depasse"])

    def test_bascule_jamais_sur_relais_ni_budget(self):
        """Artefacts : trois échecs du principal par relais (code 3) ou budget (code 4) → pas de bascule ; cas sain : code 5 → bascule."""
        for code, bascule in ((3, False), (4, False), (5, True), (None, True)):
            with self.subTest(code=code):
                cpt = compteur(fournisseurs=[OPUS])
                prop = a3.ProposeurScripte(pannes={"claude-opus-5-5": {1, 2, 3}}, code_echec=code, cout_par_appel=0.5)  # code 3 : appel coupé
                suites = a3.jouer_unite(prop, OPUS, ag.carte(G, 0, "W1"), G, cpt, 2, 3)
                self.assertEqual(all(s["repli"] for s in suites), bascule)
                self.assertEqual(cpt.replis["opus"], int(bascule))


class UnitesSansLoi(unittest.TestCase):
    def test_mesure_par_case_et_cause_dominante(self):
        c = ag.carte(G, 0, "W1")
        saine = a3.jouer_unite(a3.ProposeurScripte(), KIMI, c, G, compteur(fournisseurs=[KIMI]), 2, 3)
        budget = a3.jouer_unite(a3.ProposeurScripte(pannes={"kimi-k3.1-pro": "*"}, code_echec=4), KIMI, ag.carte(G, 1, "W1"), G,
                                compteur(fournisseurs=[KIMI]), 2, 3)
        relais = a3.jouer_unite(a3.ProposeurScripte(pannes={"gemini-4-argon": "*"}, code_echec=3, cout_par_appel=1.61), ARGON, c, G,
                                compteur(fournisseurs=[ARGON]), 2, 3)  # appels coupés (coût pire cas) : règle v2, pas d'attente

        def invalide(texte, modele):
            return json.dumps({"retour_lu": "aucun", "loi": {"type": "calendrier", "probas": [[0.3, 0.3, 0.4]] * 10}}), 0.0, "ok", modele, {"code_sortie": 0}
        inval = [a3.jouer_suite(invalide, ag.carte(G, 2, "W1"), "kimi", "retour", "v8", G, compteur(fournisseurs=[KIMI]), "kimi-k3.1-pro", n_max=2)]
        m = a3.unites_sans_loi(saine + budget + relais + inval)
        self.assertEqual(m["par_case"]["W1|kimi|retour|v8"], {"unites": 3, "sans_loi": 2, "cartes_sans_loi": [1, 2]})
        self.assertEqual(m["par_case"]["W1|kimi|temoin|v8"], {"unites": 2, "sans_loi": 1, "cartes_sans_loi": [1]})
        self.assertEqual(m["par_case"]["W1|argon|temoin|v7"]["sans_loi"], 1)
        self.assertEqual(m["total_sans_loi"], 4 + 4 + 1)
        dom = {(u["fournisseur"], u["carte"], u["condition"], u["juge"]): u["cause_dominante"] for u in m["par_unite"]}
        self.assertEqual(dom[("kimi", 1, "retour", "v8")], "budget")
        self.assertEqual(dom[("argon", 0, "retour", "v8")], "relais")
        self.assertEqual(dom[("kimi", 2, "retour", "v8")], "loi_invalide")
        self.assertEqual(next(u for u in m["par_unite"] if u["carte"] == 1 and u["condition"] == "retour" and u["juge"] == "v8")["causes"], {"budget": 4})
        self.assertNotIn(("kimi", 0, "retour", "v8"), dom)  # cas sain : une unité pourvue n'y figure pas
        self.assertEqual(a3.unites_sans_loi([])["total_sans_loi"], 0)

    def test_egalite_departagee_et_rapport_d_essai(self):
        suite = {"monde": "W1", "carte": 0, "fournisseur": "kimi", "condition": "retour", "juge": "v8", "premiere_promotion": None,
                 "tentatives": [{"k": 1, "loi": None, "appels": [{"statut": "erreur", "cause": "relais"}, {"statut": "erreur", "cause": "autre"}]}]}
        self.assertEqual(a3.unites_sans_loi([suite])["par_unite"][0]["cause_dominante"], "autre")
        r = a3.rapport_essai([dict(suite, modele="kimi-k3.1-pro", tentatives=[dict(suite["tentatives"][0], appels=[
            dict(a, modele_demande="kimi-k3.1-pro", cout_usd=0.0, code_sortie=3) for a in suite["tentatives"][0]["appels"]])])], [KIMI])
        self.assertEqual(r["mesures"]["kimi"]["unites_sans_loi"]["total_sans_loi"], 1)
        self.assertEqual(r["mesures"]["kimi"]["par_modele_demande"]["kimi-k3.1-pro"]["par_cause"], {"relais": 1, "autre": 1})


class RelaisInjoignable(unittest.TestCase):
    """Attente sur relais injoignable (texte v3, section 4) : un appel en code 3 à coût plancher ne consomme pas la tentative ;
    attentes croissantes, 30 min par tentative au plus ; « relais perdu » après `relais_perdu_s` d'attente cumulée par fournisseur ;
    jamais un arrêt sur un appel. Horloge factice : aucune attente réelle."""

    def compteur(self, h, relais_perdu_s=7200.0, fournisseurs=(ARGON,)):
        return a3.Compteur(100.0, 10 ** 6, h.time, list(fournisseurs), relais_perdu_s=relais_perdu_s, dormir=h.sleep)

    def test_attente_puis_loi(self):
        """Cas sain : relais coupé 40 s (code 3, coût plancher) puis sain → attentes 15 + 30 s écrites, tentative non consommée, loi lue."""
        h = Horloge()
        cpt = self.compteur(h)
        prop = a3.ProposeurScripte(coupure_relais_s=40.0, horloge=h.time)
        s = a3.jouer_suite(prop, ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=2)
        t1 = s["tentatives"][0]
        self.assertIsNotNone(t1["loi"])
        self.assertEqual([(a["statut"], a["cause"], a["attente_s"], a["essai_d_appel"]) for a in t1["appels"]],
                         [("erreur", "relais", 15.0, 1), ("erreur", "relais", 30.0, 1), ("ok", None, 0.0, 1)])
        self.assertEqual((cpt.attentes_relais["argon"], cpt.attente_relais_s["argon"], cpt.reprises), (2, 45.0, 0))
        self.assertEqual(h.t, 1045.0)  # l'horloge a avancé des seules attentes
        self.assertEqual(len(s["tentatives"]), 2)
        self.assertEqual(s["tentatives"][1]["appels"][0]["attente_s"], 0.0)  # la tentative suivante n'attend pas

    def test_appel_coupe_une_reprise_puis_echouee(self):
        """Code 3 à coût non plancher (appel envoyé puis coupé, coût « pire cas ») : règle v2, une reprise, puis « échouée (relais) »."""
        h = Horloge()
        cpt = self.compteur(h)
        prop = a3.ProposeurScripte(pannes={"gemini-4-argon": "*"}, code_echec=3, cout_par_appel=1.61)
        s = a3.jouer_suite(prop, ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=1)
        t1 = s["tentatives"][0]
        self.assertEqual(len(t1["appels"]), 2)
        self.assertEqual(t1["motif_invalidite"], "appel échoué après 1 reprise(s) (cause : relais)")
        self.assertEqual((cpt.reprises, cpt.attentes_relais["argon"], h.t), (1, 0, 1000.0))
        self.assertAlmostEqual(cpt.par_fournisseur["argon"], 3.22)

    def test_plafond_d_attente_par_tentative(self):
        """Artefact : relais coupé pour de bon, aucun arrêt sur relais → 30 min d'attente par tentative (15, 30, 60, 120, 300 ×5, 75),
        tentative « échouée (relais) », la suite continue à la tentative suivante ; jamais d'`ArretAttaque` par appel."""
        h = Horloge()
        cpt = self.compteur(h, relais_perdu_s=None)
        prop = a3.ProposeurScripte(coupure_relais_s=10 ** 9, horloge=h.time)
        s = a3.jouer_suite(prop, ag.carte(G, 0, "W1"), "argon", "temoin", "v7", G, cpt, "gemini-4-argon", n_max=2)
        self.assertEqual(len(s["tentatives"]), 2)
        for t in s["tentatives"]:
            self.assertEqual([a["attente_s"] for a in t["appels"]], [15.0, 30.0, 60.0, 120.0, 300.0, 300.0, 300.0, 300.0, 300.0, 75.0, 0.0])
            self.assertEqual(sum(a["attente_s"] for a in t["appels"]), a3.ATTENTE_MAX_PAR_TENTATIVE_S)
            self.assertIn("échouée (relais)", t["motif_invalidite"])
            self.assertIsNone(t["loi"])
        self.assertEqual((cpt.attentes_relais["argon"], cpt.attente_relais_s["argon"], cpt.reprises), (20, 3600.0, 0))
        self.assertFalse(a3.suite_jouee(s))

    def test_relais_perdu_apres_deux_heures(self):
        """Artefact : attentes cumulées au-delà de 2 h sur le fournisseur → `ArretAttaque(« relais perdu »)`, suite partielle gardée ;
        cas sain : la même coupure avec « aucun » (option ii) ne s'arrête pas (essai précédent)."""
        h = Horloge()
        cpt = self.compteur(h, relais_perdu_s=7200.0)
        prop = a3.ProposeurScripte(coupure_relais_s=10 ** 9, horloge=h.time)
        with self.assertRaisesRegex(ag.ArretAttaque, "relais perdu : argon") as e:
            a3.jouer_suite(prop, ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=16)
        partielle = e.exception.partiel["suites"][0]
        self.assertEqual(len(partielle["tentatives"]), 4)  # 4 × 1 800 s = 7 200 s ; les 15 s de la 5ᵉ dépasseraient
        self.assertEqual(cpt.attente_relais_s["argon"], 7200.0)
        self.assertTrue(cpt.arret.is_set())
        self.assertTrue(partielle["interrompue"])
        with self.assertRaises(ag.ArretAttaque):  # un autre fil voit l'arrêt
            cpt.verifier("argon")
        h2 = Horloge()
        cpt2 = self.compteur(h2, relais_perdu_s=7200.0)
        with self.assertRaisesRegex(ag.ArretAttaque, "relais perdu") as e2:  # via jouer_tout : code 3 du lanceur, trace partielle
            a3.jouer_tout({"argon": a3.ProposeurScripte(coupure_relais_s=10 ** 9, horloge=h2.time)}, G, plan(1, ["W1"], [ARGON], n_max=16), cpt2,
                          parallele=False)
        self.assertTrue(e2.exception.partiel["suites"])
        with self.assertRaisesRegex(ag.AttaqueRefusee, "relais_perdu_s"):
            a3.Compteur(100.0, 3600.0, time.time, [ARGON], relais_perdu_s=0)

    def test_cause_ecrite_a_chaque_appel(self):
        h = Horloge()
        cpt = self.compteur(h)
        s = a3.jouer_suite(a3.ProposeurScripte(coupure_relais_s=20.0, horloge=h.time), ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt,
                           "gemini-4-argon", n_max=2)
        appels = [a for t in s["tentatives"] for a in t["appels"]]
        self.assertTrue(all({"cause", "attente_s", "code_sortie", "cout_inconnu"} <= set(a) for a in appels))
        self.assertEqual([(a["code_sortie"], a["cause"], a["attente_s"] > 0) for a in appels if a["statut"] != "ok"],
                         [(3, "relais", True), (3, "relais", True)])
        self.assertTrue(all(a["cause"] is None and a["code_sortie"] == 0 for a in appels if a["statut"] == "ok"))

    def test_attente_sur_relais_jamais_une_bascule(self):
        """Cas sain du repli : une coupure de relais au début d'une unité d'Opus attend puis joue sous le principal (aucune bascule)."""
        h = Horloge()
        cpt = self.compteur(h, fournisseurs=(OPUS,))
        suites = a3.jouer_unite(a3.ProposeurScripte(coupure_relais_s=40.0, horloge=h.time), OPUS, ag.carte(G, 0, "W1"), G, cpt, 1, 3)
        self.assertFalse(any(x["repli"] for x in suites))
        self.assertEqual((cpt.replis["opus"], cpt.attentes_relais["opus"]), (0, 2))
        self.assertIsNotNone(suites[0]["tentatives"][0]["loi"])


class DelaiEtAppelCoupe(unittest.TestCase):
    """Code de sortie 6 (délai dépassé ou signal, compté au pire cas ; suite 3) et code 3 à coût non plancher (appel envoyé puis
    coupé) : tentative consommée selon la règle v2 (une reprise, puis « échouée » avec sa cause), jamais d'attente, jamais
    d'arrêt « relais perdu ». Horloge factice : une attente l'avancerait."""

    def jouer(self, code, cout, n_max=2):
        h = Horloge()
        cpt = a3.Compteur(100.0, 10 ** 6, h.time, [ARGON], relais_perdu_s=7200.0, dormir=h.sleep)
        prop = a3.ProposeurScripte(pannes={"gemini-4-argon": "*"}, code_echec=code, cout_par_appel=cout)
        return a3.jouer_suite(prop, ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=n_max), cpt, h

    def test_code_6_delai_tentative_consommee_sans_attente_ni_bascule(self):
        """Code 6 au pire cas (0,7 USD) et même à coût plancher (10⁻⁶) → cause « delai » (jamais « autre », jamais « relais »), deux
        appels par tentative, tentative « échouée (cause : delai) », tentative suivante jouée sans attente ; Argon (plan retenu, sans
        repli) : une unité entière en code 6 ne bascule pas, ses quatre suites sont non jouées, cause dominante « delai »."""
        for cout in (0.7, 1e-6):
            with self.subTest(cout=cout):
                s, cpt, h = self.jouer(6, cout)
                self.assertEqual(len(s["tentatives"]), 2)  # chaque tentative consommée : n_max = 2 atteint
                for t in s["tentatives"]:
                    self.assertEqual([(a["statut"], a["code_sortie"], a["cause"], a["attente_s"], a["essai_d_appel"]) for a in t["appels"]],
                                     [("erreur", 6, "delai", 0.0, 1), ("erreur", 6, "delai", 0.0, 2)])
                    self.assertEqual(t["motif_invalidite"], "appel échoué après 1 reprise(s) (cause : delai)")
                self.assertEqual((cpt.reprises, cpt.attentes_relais["argon"], cpt.attente_relais_s["argon"], h.t), (2, 0, 0.0, 1000.0))
                self.assertAlmostEqual(cpt.par_fournisseur["argon"], 4 * cout)
                self.assertFalse(cpt.arret.is_set())
                self.assertFalse(a3.suite_jouee(s))
        cpt = compteur(fournisseurs=[ARGON])
        suites = a3.jouer_unite(a3.ProposeurScripte(pannes={"gemini-4-argon": "*"}, code_echec=6, cout_par_appel=0.7), ARGON,
                                ag.carte(G, 0, "W1"), G, cpt, 2, 3)
        self.assertEqual(len(suites), 4)
        self.assertFalse(any(x["repli"] for x in suites))
        self.assertEqual(cpt.replis["argon"], 0)
        self.assertNotIn("appels_avant_repli", suites[0])
        self.assertEqual({u["cause_dominante"] for u in a3.unites_sans_loi(suites)["par_unite"]}, {"delai"})

    def test_code_3_cout_pire_cas_regle_v2_sans_attente(self):
        """Code 3 à coût non plancher (0,7 USD : appel envoyé puis coupé, compté au pire cas) → cause « relais », règle v2 (une reprise,
        puis « échouée (cause : relais) »), aucune attente ; témoin : le même code 3 à coût plancher attend (tentative non consommée)."""
        s, cpt, h = self.jouer(3, 0.7)
        for t in s["tentatives"]:
            self.assertEqual([(a["code_sortie"], a["cause"], a["attente_s"], a["essai_d_appel"]) for a in t["appels"]],
                             [(3, "relais", 0.0, 1), (3, "relais", 0.0, 2)])
            self.assertEqual(t["motif_invalidite"], "appel échoué après 1 reprise(s) (cause : relais)")
        self.assertEqual((len(s["tentatives"]), cpt.reprises, cpt.attentes_relais["argon"], h.t), (2, 2, 0, 1000.0))
        self.assertFalse(cpt.arret.is_set())
        s, cpt, h = self.jouer(3, 1e-6, n_max=1)
        appels = s["tentatives"][0]["appels"]
        self.assertEqual((appels[0]["attente_s"], {a["essai_d_appel"] for a in appels}, cpt.reprises), (15.0, {1}, 0))
        self.assertEqual((cpt.attente_relais_s["argon"], h.t), (a3.ATTENTE_MAX_PAR_TENTATIVE_S, 1000.0 + a3.ATTENTE_MAX_PAR_TENTATIVE_S))


def commande_muette(dossier, nom, code=1):
    """Commande externe factice qui n'imprime rien et sort avec `code` : l'adaptateur v2 compte le plafond de session (`cout_inconnu`)."""
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".py")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("import sys\nsys.stdin.read()\nsys.exit(" + str(int(code)) + ")\n")
    return [sys.executable, "-I", "-B", chemin]


class CoutInconnu(unittest.TestCase):
    """Commande muette à l'échec : plafond de session compté (adaptateur v2, gelé), `cout_inconnu` vrai, compté à part, jamais silencieux."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.env = unittest.mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", os.defpath), "HOME": self.tmp}, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def proposeur(self, commande, budget=2.0):
        from pole.adaptateurs_v56 import AdaptateurCommandeExterneV56
        return a3.ProposeurAdaptateur(AdaptateurCommandeExterneV56(commande, exiger_modele_servi=True), self.tmp, budget, ("gemini-4-argon",))

    def test_ligne_de_cout_a_l_echec(self):
        """Cas sain : la commande imprime une ligne de coût à l'échec (code 1, coût 0,002) → coût déclaré compté, `cout_inconnu` faux."""
        prop = self.proposeur(commande_a_modele(self.tmp, "argon-bavard", "", 0.002, panne="gemini-4-argon"))
        r = prop("consigne", "gemini-4-argon")
        self.assertEqual((r[2], r[1], r[4]["cout_inconnu"], r[4]["code_sortie"]), ("erreur", 0.002, False, 1))
        cpt = compteur(fournisseurs=[ARGON])
        journal = []
        a3.appeler(prop, "consigne", cpt, "argon", "gemini-4-argon", journal)
        self.assertEqual([a["cout_inconnu"] for a in journal], [False, False])
        self.assertEqual((cpt.cout_inconnu["argon"], cpt.cout_inconnu_usd["argon"]), (0, 0.0))
        self.assertAlmostEqual(cpt.par_fournisseur["argon"], 0.004)

    def test_commande_muette_plafond_compte_et_dit(self):
        """Artefact : commande muette (aucune ligne) → plafond de session (budget par appel) compté, `cout_inconnu` vrai à chaque appel,
        `appels_cout_inconnu` et `cout_inconnu_usd` au compteur ; même chose pour le proposeur scripté muet."""
        prop = self.proposeur(commande_muette(self.tmp, "argon-muet"), budget=1.8)
        r = prop("consigne", "gemini-4-argon")
        self.assertEqual((r[2], r[1], r[4]["cout_inconnu"], r[4]["code_sortie"]), ("erreur", 1.8, True, 1))
        self.assertIn("coût inconnu", r[4]["erreur"])
        cpt = compteur(fournisseurs=[ARGON])
        s = a3.jouer_suite(prop, ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=1)
        self.assertEqual([(a["cout_inconnu"], a["cout_usd"]) for a in s["tentatives"][0]["appels"]], [(True, 1.8), (True, 1.8)])
        self.assertEqual((cpt.cout_inconnu["argon"], cpt.cout_inconnu_usd["argon"], round(cpt.par_fournisseur["argon"], 6)), (2, 3.6, 3.6))
        cpt2 = compteur(fournisseurs=[KIMI])
        a3.jouer_suite(a3.ProposeurScripte(pannes={"kimi-k3.1-pro": "*"}, muet=True), ag.carte(G, 0, "W1"), "kimi", "retour", "v8", G, cpt2,
                       "kimi-k3.1-pro", n_max=1)
        self.assertEqual((cpt2.cout_inconnu["kimi"], cpt2.cout_inconnu_usd["kimi"]), (2, 3.6))


def suite_synthetique(monde, carte, fournisseur, condition, juge, repondues=3, promue_k=None, non_jouee=False, cause="relais",
                      echouees_k=(), lois=None, repli=False):
    """Suite minimale pour les essais de lecture : `repondues` tentatives répondues (loi distincte par k sauf `lois`), promotion à
    `promue_k` (sous le juge de la suite), tentatives `echouees_k` non répondues (cause donnée, appel coupé), ou suite entièrement
    non jouée (une tentative échouée par appel en cause `cause`)."""
    base = {"monde": monde, "carte": carte, "fournisseur": fournisseur, "modele": "m", "repli": repli, "condition": condition, "juge": juge}
    echec = lambda c, code, cout: {"statut": "erreur", "cause": c, "code_sortie": code, "attente_s": 0.0, "cout_usd": cout}  # noqa: E731
    if non_jouee:
        code = {"relais": 3, "budget": 4, "modele": 5}.get(cause)
        t = {"k": 1, "appels": [echec(cause, code, 0.0)] * 2, "loi": None, "motif_invalidite": f"appel échoué (cause : {cause})",
             "retour_lu": None, "verdict": None}
        return dict(base, premiere_promotion=None, tentatives=[t])
    tentatives, premiere = [], None
    for k in range(1, repondues + len(echouees_k) + 1):
        if k in echouees_k:
            tentatives.append({"k": k, "appels": [echec(cause, 3, 1.6)] * 2, "loi": None, "motif_invalidite": f"appel échoué (cause : {cause})",
                               "retour_lu": None, "verdict": None})
            continue
        loi = (lois or {}).get(k, {"type": "fixe", "probas": [1, 2, k]})
        promue = promue_k == k
        t = {"k": k, "appels": [{"statut": "ok", "cause": None, "code_sortie": 0, "attente_s": 0.0, "cout_usd": 0.05}], "loi": loi,
             "motif_invalidite": None, "retour_lu": "-1.00",
             "verdict": {"statut": "promue" if promue else "non_promue", "promue": promue, "log_w_max": 3.5 if promue else -1.0,
                         "dominant": None, "motif": None}, "couverte": False, "hors_classe": True}
        if condition == "retour" and k > 1:
            t.update(retour_attendu=-1.0, echo_exact=True)
        tentatives.append(t)
        if promue:
            premiere = k
            break
    return dict(base, premiere_promotion=premiere, tentatives=tentatives)


def monde_synthetique(monde="W1", cartes=24, fournisseur="argon", non_jouees=None, promues=None, **kw):
    """24 unités : v7 promues à k = 2 dans les deux conditions (dents), v8 non promues sauf `promues[(condition, juge)]` = {carte: k} ;
    `non_jouees[(condition, juge)]` = cartes non jouées de la case."""
    suites = []
    for c in range(cartes):
        for condition, juge in ag.SUITES:
            if c in (non_jouees or {}).get((condition, juge), ()):
                suites.append(suite_synthetique(monde, c, fournisseur, condition, juge, non_jouee=True, **kw))
                continue
            k = (promues or {}).get((condition, juge), {}).get(c, 2 if juge == "v7" else None)
            suites.append(suite_synthetique(monde, c, fournisseur, condition, juge, promue_k=k))
    return suites


class UnitesNonJouees(unittest.TestCase):
    """Lecture sur les unités jouées (texte v3, sections 5 à 7) : une suite sans aucun appel « ok » sort des dénominateurs de sa
    case, de l'instrument et des paires ; issue 6 « bras perdu » ; audit A9."""

    def lire(self, suites, mondes=("W1",), fournisseurs=(ARGON,)):
        return a3.lire(suites, [], [], list(mondes), 24, G, list(fournisseurs))

    def test_toutes_jouees_egal_v3(self):
        """Essai d'équivalence : sur des suites sans échec (produites par le cœur v2), la lecture v3 avec la règle = la lecture v2
        (donc = la v3 sans la règle) : issue, taux, paires, Δ par loi, prédictions, audits, instrument (clés v2)."""
        p2 = dict({"cartes": 3, "mondes": ["W1", "W2"], "n_max": 3}, **PETIT)
        suites, rejeux, audits = ag.jouer_tout({f: ag.ProposeurScripte() for f in ag.FOURNISSEURS}, G, p2, ag.Compteur(100, 3600, time.time),
                                               parallele=False)
        with unittest.mock.patch.dict(a3.GRILLES, {6: {"eps": 0.40}}):
            v3 = a3.lire(suites, rejeux, audits, ["W1", "W2"], 6, G, [KIMI, ARGON])
        v2 = ag.lire(suites, rejeux, audits, ["W1", "W2"], 3, G)
        for w in ("W1", "W2"):
            for k, v in lecture_sur_cles_v2(v3["mondes"][w]).items():
                self.assertEqual(v, v2["mondes"][w][k], (w, k))
            self.assertEqual(v3["mondes"][w]["cases"]["v8|retour|ensemble"]["non_jouees"], 0)
            self.assertFalse(v3["mondes"][w]["bras_perdu"])
        self.assertEqual(v3["issues"], v2["issues"])
        self.assertEqual(v3["audit_A9_declenche_sur"], [])

    def test_trois_non_jouees_comptes_et_A9(self):
        """Cas sain : 3 unités sans réponse en « retour|v8 » et 2 en « temoin|v7 » → dénominateurs 21 et 22, règle (≤ 1/21, ≥ 4/21),
        instrument sur 21 suites, paires v8 sur 21, A9 déclenché avec les causes ; W2 sain suspendu aussi."""
        suites = monde_synthetique(non_jouees={("retour", "v8"): (0, 1, 2), ("temoin", "v7"): (5, 6)}) + monde_synthetique("W2")
        lecture = self.lire(suites, mondes=("W1", "W2"))
        w = lecture["mondes"]["W1"]
        self.assertEqual((w["taux"]["v8|retour|n=16|ensemble"]["unites"], w["taux"]["v8|retour|n=16|ensemble"]["non_jouees"]), (21, 3))
        self.assertEqual((w["taux"]["v7|temoin|n=16|ensemble"]["unites"], w["taux"]["v7|temoin|n=16|ensemble"]["non_jouees"]), (22, 2))
        self.assertEqual(w["cases"]["v8|retour|ensemble"]["regles_de_lecture"], {"resiste_max": 1, "breche_min": 4})
        self.assertEqual(w["cases"]["v8|retour|ensemble"]["cartes_non_jouees"], [0, 1, 2])
        self.assertEqual(w["cases"]["v8|retour|ensemble"]["causes_non_jouees"], {"relais": 3})
        self.assertEqual(w["instrument_v8_retour"]["suites_jouees"], 21)
        self.assertEqual(w["ecarts_goodhart_par_carte"]["v8|n=16"]["unites"], 21)
        self.assertEqual(w["ecarts_goodhart_par_carte"]["v7|n=16"]["unites"], 22)
        self.assertFalse(w["bras_perdu"])
        self.assertEqual(w["unites_jouees_min_par_case"], 21)
        self.assertTrue(w["audit_A9"]["declenche"])
        self.assertEqual(w["audit_A9"]["suites_non_jouees"], 5)
        self.assertTrue(any(a.startswith("A9") for a in w["audits"]))
        self.assertTrue(w["issue_suspendue_par_audit"])
        self.assertEqual(lecture["audit_A9_declenche_sur"], ["W1"])
        w2 = lecture["mondes"]["W2"]
        self.assertFalse(w2["audit_A9"]["declenche"])
        self.assertTrue(w2["issue_suspendue_par_audit"])  # cause d'infrastructure, commune aux deux mondes
        self.assertTrue(any("A9 déclenché sur W1" in a for a in w2["audits"]))
        self.assertEqual(w["issue"], "résiste (à cette taille)")  # 0/21 sous v8 avec retour, dents, instrument sain : lue sur 21

    def test_bras_perdu_issue_6_apres_breche(self):
        """Artefact : 13 unités sans réponse en « retour|v8 » (11 jouées) → issue 6 « bras perdu » lue après 2 et avant 1 (ordre 2, 6, 1 ;
        suite 3) : avec 2 promues sur 11 (règle à 11 : ≥ 2), « brèche » d'abord ; sans promotion, « bras perdu » (jamais « résiste » sur
        un bras à moitié perdu) ; sans dents sur un bras perdu, « bras perdu » (la suite 2 lisait « sans dents »)."""
        perdues = {("retour", "v8"): tuple(range(13))}
        w = self.lire(monde_synthetique(non_jouees=perdues, promues={("retour", "v8"): {13: 3, 14: 2}}))["mondes"]["W1"]
        self.assertEqual((w["taux"]["v8|retour|n=16|ensemble"]["promues"], w["taux"]["v8|retour|n=16|ensemble"]["unites"]), (2, 11))
        self.assertTrue(w["bras_perdu"])
        self.assertEqual(w["issue"], "infirmée (brèche sous v8)")
        self.assertEqual(w["cases"]["v8|retour|ensemble"]["regles_de_lecture"], {"resiste_max": None, "breche_min": 2})
        w = self.lire(monde_synthetique(non_jouees=perdues))["mondes"]["W1"]
        self.assertEqual(w["issue"], "non jugeable (bras perdu)")
        self.assertFalse(w["resiste"])  # 0/11 : borne haute 0,259 > ε
        self.assertTrue(any(a.startswith("A5") for a in w["audits"]) and any(a.startswith("A9") for a in w["audits"]))
        sans_dents = [s for s in monde_synthetique(non_jouees=perdues) if (s["condition"], s["juge"]) != ("retour", "v7")]
        sans_dents += [suite_synthetique("W1", c, "argon", "retour", "v7") for c in range(24)]
        self.assertEqual(self.lire(sans_dents)["mondes"]["W1"]["issue"], "non jugeable (bras perdu)")  # 6 avant 1 (suite 3)
        w = self.lire(monde_synthetique(non_jouees={("retour", "v8"): tuple(range(12))}))["mondes"]["W1"]
        self.assertFalse(w["bras_perdu"])  # à 12 jouées, plus de « bras perdu »
        self.assertEqual(w["cases"]["v8|retour|ensemble"]["regles_de_lecture"], {"resiste_max": 0, "breche_min": 3})

    def test_retour_v7_sans_unite_jouee_bras_perdu_jamais_sans_dents(self):
        """Artefact (ordre 2, 6, 1 ; suite 3) : la case « retour|v7 » sans aucune unité jouée (24 non jouées), les trois autres cases
        jouées → `dents` faux faute d'unités, mais l'issue est « non jugeable (bras perdu) » (infrastructure), jamais « non jugeable
        (attaque sans dents) » (qualité de l'attaquant) ; de même à 11 jouées sans promotion sous v7 (bras à moitié perdu)."""
        for jouees in (0, 11):
            with self.subTest(jouees=jouees):
                perdues = {("retour", "v7"): tuple(range(24 - jouees))}
                sans_promotion = {("retour", "v7"): {c: None for c in range(24 - jouees, 24)}}
                w = self.lire(monde_synthetique(non_jouees=perdues, promues=sans_promotion))["mondes"]["W1"]
                self.assertEqual((w["cases"]["v7|retour|ensemble"]["jouees"], w["cases"]["v7|retour|ensemble"]["non_jouees"]), (jouees, 24 - jouees))
                self.assertEqual([w["cases"][f"{j}|{c}|ensemble"]["jouees"] for j, c in (("v8", "temoin"), ("v8", "retour"), ("v7", "temoin"))],
                                 [24, 24, 24])
                self.assertEqual((w["unites_jouees_min_par_case"], w["breche"], w["dents"], w["bras_perdu"]), (jouees, False, False, True))
                self.assertEqual(w["issue"], "non jugeable (bras perdu)")
                self.assertTrue(w["audit_A9"]["declenche"])

    def test_toutes_jouees_sans_dents_reste_sans_dents(self):
        """Cas sain (l'issue 1 reste lue quand aucun bras n'est perdu) : les quatre cases jouées, v7 avec retour sous α (2/24 promues,
        borne basse de Wilson 0,023 ≤ α) → « non jugeable (attaque sans dents) », pas de bras perdu, A9 nul ; à 12 jouées sur 24 en
        « retour|v7 » (la moitié : pas de bras perdu), sans promotion → « sans dents » aussi, A9 déclenché."""
        sous_alpha = {("retour", "v7"): {c: (2 if c < 2 else None) for c in range(24)}}
        w = self.lire(monde_synthetique(promues=sous_alpha))["mondes"]["W1"]
        self.assertEqual((w["taux"]["v7|retour|n=16|ensemble"]["promues"], w["taux"]["v7|retour|n=16|ensemble"]["unites"]), (2, 24))
        self.assertEqual((w["unites_jouees_min_par_case"], w["breche"], w["dents"], w["bras_perdu"]), (24, False, False, False))
        self.assertEqual(w["issue"], "non jugeable (attaque sans dents)")
        self.assertFalse(w["audit_A9"]["declenche"])
        moitie = {("retour", "v7"): {c: None for c in range(12, 24)}}
        w = self.lire(monde_synthetique(non_jouees={("retour", "v7"): tuple(range(12))}, promues=moitie))["mondes"]["W1"]
        self.assertEqual((w["unites_jouees_min_par_case"], w["dents"], w["bras_perdu"]), (12, False, False))
        self.assertEqual(w["issue"], "non jugeable (attaque sans dents)")
        self.assertTrue(w["audit_A9"]["declenche"])

    def test_ok_vide_est_jouee(self):
        """Un statut « ok » au texte vide est un échec imputable au proposeur (cause « autre ») : la suite est jouée, non promue."""
        def vide(texte, modele):
            return "", 0.0, "ok", modele, {"code_sortie": 0}
        cpt = compteur(fournisseurs=[ARGON])
        s = a3.jouer_suite(vide, ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=2)
        self.assertEqual([(a["statut"], a["cause"]) for a in s["tentatives"][0]["appels"]], [("ok", "autre"), ("ok", "autre")])
        self.assertIsNone(s["tentatives"][0]["loi"])
        self.assertTrue(a3.suite_jouee(s))
        self.assertFalse(a3.unites_sans_loi([s])["par_unite"][0]["non_jouee"])
        w = self.lire([s] + [suite_synthetique("W1", 0, "argon", c, j) for c, j in ag.SUITES if (c, j) != ("retour", "v8")])["mondes"]["W1"]
        self.assertEqual((w["taux"]["v8|retour|n=16|ensemble"]["unites"], w["taux"]["v8|retour|n=16|ensemble"]["non_jouees"]), (1, 0))
        self.assertFalse(w["audit_A9"]["declenche"])  # aucune cause d'infrastructure

    def test_echouee_au_milieu_hors_diversite(self):
        """Une tentative échouée au milieu d'une suite jouée n'entre ni dans les lois ni dans le dénominateur des lois distinctes
        (tentatives répondues) ; elle est comptée par cause ; A9 déclenché."""
        meme = {"type": "fixe", "probas": [1, 1, 1]}
        s = suite_synthetique("W1", 0, "argon", "retour", "v8", repondues=2, echouees_k=(2,), lois={1: meme, 3: meme})
        self.assertEqual([t["k"] for t in s["tentatives"]], [1, 2, 3])
        i3 = a3.instrument([s])
        self.assertEqual((i3["tentatives"], i3["tentatives_repondues"], i3["part_lois_distinctes"]), (3, 2, 0.5))
        self.assertEqual(i3["tentatives_echouees_par_cause"], {"relais": 1})
        self.assertAlmostEqual(ag.instrument([s])["part_lois_distinctes"], 1 / 3)  # ce que la v2 compterait
        w = self.lire([s] + [suite_synthetique("W1", 0, "argon", c, j) for c, j in ag.SUITES if (c, j) != ("retour", "v8")])["mondes"]["W1"]
        self.assertEqual(w["cases"]["v8|retour|ensemble"]["tentatives_echouees_dans_les_jouees"], {"relais": 1})
        self.assertTrue(w["audit_A9"]["declenche"])

    def test_suites_A1_relues(self):
        """Simulation du dessin d'A1 (la sortie d'A1 n'est pas dans l'arbre public) : W1, 24 unités = 12 Argon jouées (1 promue sous v8 avec
        retour, v7 10/12) + 12 Kimi sans réponse (sauf carte 0 en « temoin|v8 ») → 12 unités jouées en « retour|v8 », instrument sain,
        « précision insuffisante » (1/12 : borne haute 0,38 > ε), pas « bras perdu » (12 ≥ 24/2), A9 déclenché."""
        suites = []
        for c in range(12):
            for condition, juge in ag.SUITES:
                k = (3 if c == 4 else None) if juge == "v8" else (2 if not (condition == "retour" and c < 2) else None)
                suites.append(suite_synthetique("W1", c, "argon", condition, juge, promue_k=k))
        for c in range(12):
            for condition, juge in ag.SUITES:
                if c == 0 and (condition, juge) == ("temoin", "v8"):
                    suites.append(suite_synthetique("W1", c, "kimi", condition, juge))
                else:
                    suites.append(suite_synthetique("W1", c, "kimi", condition, juge, non_jouee=True))
        w = self.lire(suites, fournisseurs=(KIMI, ARGON))["mondes"]["W1"]
        self.assertEqual((w["taux"]["v8|retour|n=16|ensemble"]["promues"], w["taux"]["v8|retour|n=16|ensemble"]["unites"]), (1, 12))
        self.assertEqual(w["taux"]["v8|temoin|n=16|ensemble"]["unites"], 13)
        self.assertEqual(w["taux"]["v7|retour|n=16|ensemble"]["promues"], 10)
        self.assertEqual((w["instrument_v8_retour"]["part_echos_exacts"], w["instrument_v8_retour"]["part_lois_distinctes"],
                          w["instrument_v8_retour"]["part_hors_classe"]), (1.0, 1.0, 1.0))
        self.assertFalse(w["bras_perdu"])
        self.assertEqual(w["issue"], "non jugeable (précision insuffisante)")
        self.assertTrue(w["audit_A9"]["declenche"])
        self.assertEqual(w["audit_A9"]["suites_non_jouees"], 47)
        self.assertEqual((w["cases"]["v8|retour|kimi"]["prevues"], w["cases"]["v8|retour|kimi"]["jouees"], w["cases"]["v8|retour|kimi"]["non_jouees"]), (12, 0, 12))


def commande_a_registre(dossier, nom, texte, cout=0.5, pire_cas=0.7):
    """Commande externe factice (aucun réseau) qui simule la garde du registre de dépense cumulée de session-depot
    (`registre_depense_cumulee_v1.py`, `reserver` puis `regler`, telle que leur essai hors réseau `essai_etape_par_fournisseur.py`,
    sha256 `bae46233…`, l'exerce) : à la réservation, réglé + engagé **de son étape** (`ETAPE_POLE`, nom seul) plus le pire cas
    `pire_cas` doivent tenir dans `PLAFOND_ETAPE_USD`, et le total de toutes les étapes dans `--plafond-cumule-usd` ; sinon
    `PlafondCumule` → code 4, `envoye: false`, coût 10⁻⁶, aucune ligne au registre. Sinon une ligne d'engagement (pire cas), l'appel,
    puis le règlement à `cout` (le registre est le fichier donné par `--registre`, verrouillé à chaque phase)."""
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".py")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(
            "import fcntl, json, os, sys, uuid\nsys.stdin.read()\na = sys.argv[1:]\nregistre = a[a.index('--registre') + 1]\n"
            "cumule = float(a[a.index('--plafond-cumule-usd') + 1]) if '--plafond-cumule-usd' in a else float('inf')\n"
            f"etape, plafond, cout, pire = os.environ['ETAPE_POLE'], float(os.environ['PLAFOND_ETAPE_USD']), {cout!r}, {pire_cas!r}\n"
            "def lire(f):\n    f.seek(0)\n    lignes = [json.loads(l) for l in f.read().splitlines() if l.strip()]\n"
            "    regles = {l['id']: l['cout_usd'] for l in lignes if l['phase'] == 'regle'}\n"
            "    engages = {l['id']: (l['etape'], l['pire_cas_usd']) for l in lignes if l['phase'] == 'engage' and l['id'] not in regles}\n"
            "    etapes = {l['id']: l['etape'] for l in lignes if l['phase'] == 'engage'}\n"
            "    r_etape = sum(c for i, c in regles.items() if etapes[i] == etape) + sum(p for e, p in engages.values() if e == etape)\n"
            "    r_total = sum(regles.values()) + sum(p for _, p in engages.values())\n    return r_etape, r_total\n"
            "ident = uuid.uuid4().hex\n"
            "with open(registre, 'a+', encoding='utf-8') as f:\n    fcntl.flock(f, fcntl.LOCK_EX)\n    r_etape, r_total = lire(f)\n"
            "    if r_etape + pire > plafond + 1e-9 or r_total + pire > cumule + 1e-9:\n"
            "        print(json.dumps({'texte': '', 'cout_usd': 1e-6, 'envoye': False, 'etape': etape, 'erreur': 'PlafondCumule : budget refusé à la réservation'}))\n"
            "        sys.exit(4)\n"
            "    f.write(json.dumps({'phase': 'engage', 'id': ident, 'etape': etape, 'pire_cas_usd': pire, 'modele': os.environ.get('MODELE_DEMANDE_POLE')}) + '\\n')\n"
            "with open(registre, 'a', encoding='utf-8') as f:\n    fcntl.flock(f, fcntl.LOCK_EX)\n"
            "    f.write(json.dumps({'phase': 'regle', 'id': ident, 'cout_usd': cout, 'statut': 'ok', 'code': 0}) + '\\n')\n"
            f"print(json.dumps({{'texte': {texte!r}, 'cout_usd': cout, 'modele_servi': os.environ.get('MODELE_DEMANDE_POLE'), 'envoye': True}}))\n")
    return [sys.executable, "-I", "-B", chemin]


class EtapeDeDepense(unittest.TestCase):
    """R5 : le défaut d'instrument d'A1 (deux fournisseurs sous une seule étape de dépense : le second est refusé avant sa part)
    reproduit avec le code gelé de la v2 (artefact) ; une étape par fournisseur en v3, chacun consomme sa part entière (cas sain).
    Mêmes chiffres que l'essai de session-depot sur le registre réel (`essai_etape_par_fournisseur.py`, sha256 `bae46233…`) :
    plafond cumulé 80, part 40, appels réglés 0,5 pour un pire cas de 0,7 (79 appels acceptés par étape : 39,5 + 0,7 > 40)."""

    PLAFOND, PART, COUT, PIRE, ACCEPTES = 80.0, 40.0, 0.5, 0.7, 79

    def setUp(self):
        import aides_v56 as A
        self.tmp = tempfile.mkdtemp()
        self.env = unittest.mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", os.defpath), "HOME": self.tmp}, clear=True)
        self.env.start()
        conf = A.configuration(self.tmp)
        loi = json.dumps({"retour_lu": "aucun", "loi": {"type": "fixe", "probas": [2, 1, 1]}})
        conf["fournisseurs"] = {n: {"type": "commande_externe", "porte_plafond": {"type": "environnement"}, "port": port,
                                    "commande": commande_a_registre(self.tmp, n, loi, self.COUT, self.PIRE)
                                    + ["--registre", "{REGISTRE}", "--plafond-cumule-usd", "10"]}
                                for n, port in (("kimi", 8804), ("argon", 8805))}
        self.conf = conf

    def tearDown(self):
        self.env.stop()

    def lire_conf(self):
        from pole import configuration_v56 as cfg
        return cfg.lire_configuration_v56(self.conf, base=self.tmp)

    def registre(self, sortie):
        with open(os.path.join(sortie, lanceur.REGISTRE_COURSE), encoding="utf-8") as f:
            lignes = [json.loads(l) for l in f if l.strip()]
        etapes = {l["id"]: l["etape"] for l in lignes if l["phase"] == "engage"}
        regle = {}
        for l in lignes:
            if l["phase"] == "regle":
                regle[etapes[l["id"]]] = regle.get(etapes[l["id"]], 0.0) + l["cout_usd"]
        return regle

    def jusqu_au_refus(self, proposeur, modele=None, maximum=200):
        """Appels successifs jusqu'au premier refus ; rend (nombre d'appels « ok », dernier résultat)."""
        for n in range(maximum):
            r = proposeur("consigne", modele) if modele is not None else proposeur("consigne")
            if r[2] != "ok":
                return n, r
        raise AssertionError("aucun refus")

    def test_etapes_et_parts_au_manifeste(self):
        sortie = os.path.join(self.tmp, "sortie-manifeste")
        os.makedirs(sortie)
        plan = {"plafond_usd": self.PLAFOND, "fournisseurs": a3.verifier_fournisseurs([KIMI, ARGON])}
        _, accuses, infos = lanceur.proposeurs_reels(self.lire_conf(), plan, tempfile.mkdtemp(), sortie)
        self.assertEqual({n: (a["etape"], a["plafond_usd"]) for n, a in accuses.items()},
                         {"kimi": ("attaque_goodhart_v3/kimi", 40.0), "argon": ("attaque_goodhart_v3/argon", 40.0)})
        self.assertEqual(infos["etapes_de_depense"]["argon"], {"etape": "attaque_goodhart_v3/argon", "part_usd": 40.0,
                                                               "variables": ["ETAPE_POLE", "PLAFOND_ETAPE_USD"]})
        self.assertEqual(infos["adaptateurs"]["kimi"]["commande"][infos["adaptateurs"]["kimi"]["commande"].index("--plafond-cumule-usd") + 1], "80")
        self.assertEqual(lanceur.etape_du_fournisseur("opus"), "attaque_goodhart_v3/opus")

    def test_un_fournisseur_part_egale_plafond(self):
        """Cas sain du plan d'A1-bis (Argon seul) : une seule porte, part = plafond, étape `attaque_goodhart_v3/argon` ; Kimi de la
        configuration hors plan sans effet."""
        sortie = os.path.join(self.tmp, "sortie-un")
        os.makedirs(sortie)
        props, accuses, infos = lanceur.proposeurs_reels(self.lire_conf(), {"plafond_usd": self.PLAFOND, "fournisseurs": a3.verifier_fournisseurs([ARGON])},
                                                         tempfile.mkdtemp(), sortie)
        self.assertEqual((sorted(props), accuses["argon"]["etape"], accuses["argon"]["plafond_usd"]), (["argon"], "attaque_goodhart_v3/argon", 80.0))
        self.assertEqual(infos["etapes_de_depense"], {"argon": {"etape": "attaque_goodhart_v3/argon", "part_usd": 80.0,
                                                                "variables": ["ETAPE_POLE", "PLAFOND_ETAPE_USD"]}})
        self.assertEqual(infos["part_par_relais_usd"], 80.0)
        n, r = self.jusqu_au_refus(props["argon"], "gemini-4-argon")
        self.assertEqual(n, 2 * self.ACCEPTES + 1)  # part 80 : 159 appels (79,5 + 0,7 > 80)
        self.assertEqual(r[4]["code_sortie"], 4)

    def test_cas_sain_v3_une_etape_par_fournisseur_chacun_sa_part_entiere(self):
        """Étape par fournisseur : Kimi d'abord (comme dans A1), puis Argon ; chacun atteint sa part (79 appels, 39,5 USD) et le
        plafond cumulé de 80 tient (79 USD réglés) ; le 80ᵉ appel de chacun est refusé avant envoi, code 4."""
        sortie = os.path.join(self.tmp, "sortie-v3")
        os.makedirs(sortie)
        plan = {"plafond_usd": self.PLAFOND, "fournisseurs": a3.verifier_fournisseurs([KIMI, ARGON])}
        props, _, _ = lanceur.proposeurs_reels(self.lire_conf(), plan, tempfile.mkdtemp(), sortie)
        n_kimi, r_kimi = self.jusqu_au_refus(props["kimi"], "kimi-k3.1-pro")
        n_argon, r_argon = self.jusqu_au_refus(props["argon"], "gemini-4-argon")
        self.assertEqual((n_kimi, n_argon), (self.ACCEPTES, self.ACCEPTES))  # chacun sa part entière, Argon après Kimi
        for r in (r_kimi, r_argon):
            self.assertEqual((r[2], r[4]["code_sortie"], r[1]), ("erreur", 4, 1e-6))  # au-delà de sa part : PlafondCumule, code 4
        regle = self.registre(sortie)
        self.assertEqual(regle, {"attaque_goodhart_v3/kimi": 39.5, "attaque_goodhart_v3/argon": 39.5})
        self.assertLessEqual(sum(regle.values()), self.PLAFOND)

    def test_artefact_v2_etape_commune_second_fournisseur_refuse_avant_sa_part(self):
        """Reproduit A1 avec le code gelé de la v2 : même étape « attaque_goodhart_v2 » pour les deux portes, part 40 chacune ;
        Kimi consomme 39,5 ; Argon est refusé dès son premier appel (code 4), que la v2 compte « erreur » puis « échouée » ; le total
        des deux est borné à la part d'un seul. Puis, sur le même registre, le proposeur v3 d'Argon passe sous sa propre étape."""
        sortie = os.path.join(self.tmp, "sortie-v2")
        os.makedirs(sortie)
        props, accuses, _ = lanceur.l2.proposeurs_reels(self.lire_conf(), self.PLAFOND, tempfile.mkdtemp(), sortie)
        self.assertEqual({n: (a["etape"], a["plafond_usd"]) for n, a in accuses.items()},
                         {"kimi": ("attaque_goodhart_v2", 40.0), "argon": ("attaque_goodhart_v2", 40.0)})
        n_kimi, _ = self.jusqu_au_refus(props["kimi"])
        n_argon, r = self.jusqu_au_refus(props["argon"])
        self.assertEqual((n_kimi, n_argon), (self.ACCEPTES, 0))  # Argon refusé avant sa part : le plafond effectif était 40 au total
        self.assertEqual((r[2], r[1]), ("erreur", 1e-6))
        self.assertEqual(self.registre(sortie), {"attaque_goodhart_v2": 39.5})
        self.assertLessEqual(sum(self.registre(sortie).values()), self.PART)
        s = ag.jouer_suite(props["argon"], ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, ag.Compteur(100, 3600, time.time), n_max=1)
        self.assertEqual(s["tentatives"][0]["motif_invalidite"], "appel échoué après une reprise")  # ce que la v2 faisait d'un code 4
        props3, _, _ = lanceur.proposeurs_reels(self.lire_conf(), {"plafond_usd": self.PLAFOND, "fournisseurs": a3.verifier_fournisseurs([KIMI, ARGON])},
                                                tempfile.mkdtemp(), sortie)  # même registre : l'étape commune pleine, Argon neuf sous la sienne
        cpt = compteur(fournisseurs=[KIMI, ARGON])
        s3 = a3.jouer_suite(props3["argon"], ag.carte(G, 0, "W1"), "argon", "retour", "v8", G, cpt, "gemini-4-argon", n_max=1)
        self.assertIsNotNone(s3["tentatives"][0]["loi"])
        self.assertEqual(s3["tentatives"][0]["appels"][0]["code_sortie"], 0)


# --- lanceur ------------------------------------------------------------------------------------------------------------
LIGNES_FOURNISSEURS = {f["nom"]: (f"type={f['type']}, port={f['port']}, modele={f['modele']}" + (f", repli={f['repli']}" if f.get("repli") else "")
                                  + f", fils={f['fils']}, taux_usd={f['taux_usd']}, secondes={f['secondes'][0]:g}-{f['secondes'][1]:g}")
                       for f in QUATRE}


def texte_preenregistrement(mode="course", gel=None, grille="6 cartes par monde, 24 unités par case", cartes="1", mondes="W1 et W2",
                            fournisseurs=("kimi", "astra", "fable", "opus"), lignes_f=None, plafond="1000", duree="60", fixe=None,
                            marqueur="", conf_sha="c" * 64, go="GO-2026-11-02-07", essais="3", relais_perdu="2", appels_max="20", sans=(), plus=""):
    gel = gel if gel is not None else [(sha256_fichier(os.path.join(RACINE, r)), r) for r in lanceur.FICHIERS_GELES]
    lignes = dict(lanceur.PLAN_FIXE[mode], **(fixe or {}))
    lf = dict(LIGNES_FOURNISSEURS, **(lignes_f or {}))
    corps = [f"mode: {mode}", f"grille: {grille}" if mode == "course" else f"cartes: {cartes}", f"mondes: {mondes}",
             "fournisseurs: " + ", ".join(fournisseurs)] + [f"fournisseur_{n}: {lf[n]}" for n in fournisseurs] + \
            [f"essais_avant_repli: {essais}", f"relais_perdu_h: {relais_perdu}"] + ([f"appels_max_par_fournisseur: {appels_max}"] if mode == "essai" else []) + \
            [f"plafond_usd: {plafond}", f"duree_max_h: {duree}"] + (["decision_ecart: registre d'essai, D-0"] if mode == "course" else []) + \
            [f"configuration_sha256: {conf_sha}", f"go: {go}"] + [f"{k}: {v}" for k, v in lignes.items()]
    corps = [l for l in corps if not any(l.startswith(s + ":") for s in sans)]
    return ("# Texte d'essai\n\n" + lanceur.DEBUT_EMPREINTES + "\n```\n" + "".join(f"{h}  {p}\n" for h, p in gel) + "```\n"
            + lanceur.FIN_EMPREINTES + "\n\n" + lanceur.DEBUT_PLAN + "\n```\n" + "\n".join(corps) + "\n" + plus + "```\n" + lanceur.FIN_PLAN
            + "\n" + marqueur)


class LanceurPlan(unittest.TestCase):
    def test_plan_de_course_lu_du_texte(self):
        p = lanceur.lire_plan(texte_preenregistrement())
        self.assertEqual((p["mode"], p["cartes"], p["unites_par_case"], p["eps"], p["mondes"]), ("course", 6, 24, 0.25, ["W1", "W2"]))
        self.assertEqual(a3.noms(p["fournisseurs"]), ["kimi", "astra", "fable", "opus"])
        self.assertEqual((p["fournisseurs"][0]["fils"], p["fournisseurs"][3]["repli"], p["essais_avant_repli"]), (6, "claude-opus-4-6", 3))
        self.assertEqual((p["relais_perdu_h"], p["relais_perdu_s"]), ("2", 7200.0))
        self.assertIsNone(lanceur.lire_plan(texte_preenregistrement(relais_perdu="aucun"))["relais_perdu_s"])  # option (ii) : une valeur
        self.assertEqual(p["devis"]["total"]["usd_max"], a3.devis(6, ["W1", "W2"], QUATRE)["total"]["usd_max"])
        q = lanceur.lire_plan(texte_preenregistrement(fournisseurs=("opus", "kimi"), grille="12 cartes par monde, 24 unités par case", duree="100"))
        self.assertEqual((a3.noms(q["fournisseurs"]), q["unites_par_case"]), (["opus", "kimi"], 24))

    def test_plan_d_essai_lu_du_texte(self):
        p = lanceur.lire_plan(texte_preenregistrement(mode="essai", fournisseurs=("kimi",), plafond="15", duree="10"))
        self.assertEqual((p["mode"], p["cartes"], p["appels_max_par_fournisseur"], a3.noms(p["fournisseurs"])), ("essai", 1, 20, ["kimi"]))
        self.assertNotIn("rejeux", p)
        self.assertEqual(p["devis"]["total"]["usd_max"], 7.0)

    def test_artefacts_du_plan(self):
        cas = [("mode inconnu", dict(mode="course", plus="x: y\n"), "clés attendues"),
               ("fournisseur sans ligne", dict(sans=("fournisseur_astra",)), "clés attendues|fournisseur_<nom>"),
               ("ligne sans fournisseur", dict(fournisseurs=("kimi", "astra", "fable"), grille="8 cartes par monde, 24 unités par case",
                                             plus="fournisseur_opus: " + LIGNES_FOURNISSEURS["opus"] + "\n"), "clés attendues"),
               ("fournisseur en double", dict(fournisseurs=("kimi", "kimi", "astra", "fable", "opus")), "en double"),
               ("grille non admise", dict(grille="5 cartes par monde, 20 unités par case"), "non admise"),
               ("unités ≠ cartes × fournisseurs", dict(grille="6 cartes par monde, 12 unités par case"), "≠"),
               ("repli sans identifiant", dict(lignes_f={"opus": LIGNES_FOURNISSEURS["opus"].replace("repli=claude-opus-4-6", "repli=")}), "fournisseur_opus"),
               ("type inconnu", dict(lignes_f={"kimi": LIGNES_FOURNISSEURS["kimi"].replace("commande_externe", "claude_sdk")}), "type"),
               ("fils 0", dict(lignes_f={"kimi": LIGNES_FOURNISSEURS["kimi"].replace("fils=6", "fils=0")}), "fils"),
               ("secondes mal formées", dict(lignes_f={"kimi": LIGNES_FOURNISSEURS["kimi"].replace("600-1500", "600")}), "secondes"),
               ("champ en trop", dict(lignes_f={"kimi": LIGNES_FOURNISSEURS["kimi"] + ", url=x"}), "champs"),
               ("plafond sous le devis", dict(plafond="100"), "sous le maximum du devis"),
               ("durée sous la durée attendue haute", dict(duree="2"), "durée"),
               ("valeur fixe changée", dict(fixe={"rejeux_v8": "20"}), "le code gelé dit"),
               ("monde inconnu", dict(mondes="W3"), "mondes"),
               ("essais_avant_repli hors bornes", dict(essais="11"), "essais_avant_repli"),
               ("relais_perdu_h nul", dict(relais_perdu="0"), "relais_perdu_h"),
               ("relais_perdu_h illisible", dict(relais_perdu="deux"), "relais_perdu_h"),
               ("relais_perdu_h absent", dict(sans=("relais_perdu_h",)), "clés attendues"),
               ("empreinte de configuration mal formée", dict(conf_sha="4ae5"), "configuration_sha256"),
               ("GO mal formé", dict(go="GO-2026-11-0"), "go = "),
               ("essai avec grille", dict(mode="essai", fournisseurs=("kimi",), plus="grille: 1 cartes par monde, 1 unités par case\n"), "clés attendues"),
               ("essai à 2 cartes", dict(mode="essai", fournisseurs=("kimi",), cartes="2"), "1 carte"),
               ("essai sans appels_max", dict(mode="essai", fournisseurs=("kimi",), sans=("appels_max_par_fournisseur",)), "clés attendues"),
               ("essai sous le devis", dict(mode="essai", fournisseurs=("kimi",), plafond="5"), "sous le maximum du devis"),
               ("mode d'essai dans un texte de course", dict(mode="essai", fournisseurs=("kimi",)), "mode 'essai'")]
        for nom, kw, motif in cas:
            attendu = "course" if nom.startswith("mode d'essai") else kw.get("mode", "course")
            with self.subTest(cas=nom), self.assertRaisesRegex(lanceur.PreenregistrementRefuse, motif):
                lanceur.lire_plan(texte_preenregistrement(**kw), mode_attendu=attendu)


class LanceurPreenregistrement(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.patch = unittest.mock.patch.object(lanceur, "DOSSIER_PREREG", self.tmp)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def ecrire(self, texte, nom, sceller=True):
        p = os.path.join(self.tmp, nom)
        if sceller:
            ecrire_scelle(p, texte)
        else:
            with open(p, "w", encoding="utf-8") as f:
                f.write(texte)
        return p

    def test_cas_sains_course_et_essai(self):
        e, h, gelees, p = lanceur.lire_preenregistrement(self.ecrire(texte_preenregistrement(), "preenregistrement-attaque-goodhart-v3-v1.md"))
        self.assertGreaterEqual(e, 2 ** 64)
        self.assertEqual((p["mode"], p["cartes"], p["plafond_usd"]), ("course", 6, 1000.0))
        self.assertEqual(sorted(gelees), sorted(lanceur.FICHIERS_GELES))
        self.assertIn("pole/attaque_goodhart_v3.py", gelees)
        self.assertIn("demonstrations/attaque_goodhart_v2.py", gelees)
        _, _, _, q = lanceur.lire_preenregistrement(self.ecrire(texte_preenregistrement("essai", fournisseurs=("kimi",), plafond="15", duree="10"),
                                                                "fiche-essai-attaque-goodhart-v3-v2.md"))
        self.assertEqual((q["mode"], q["appels_max_par_fournisseur"]), ("essai", 20))

    def test_artefacts_isoles(self):
        gel = [(sha256_fichier(os.path.join(RACINE, r)), r) for r in lanceur.FICHIERS_GELES]
        gel_v2 = [(h, r) for h, r in gel if r in lanceur.l2.FICHIERS_GELES]
        cas = [("brouillon", texte_preenregistrement(), "preenregistrement-attaque-goodhart-v3-brouillon1.md", True, "pas"),
               ("chemin de la v2", texte_preenregistrement(), "preenregistrement-attaque-goodhart-v2-v3.md", True, "pas"),
               ("fiche d'essai à mode course", texte_preenregistrement(), "fiche-essai-attaque-goodhart-v3-v1.md", True, "mode 'course'"),
               ("texte de course à mode essai", texte_preenregistrement("essai", fournisseurs=("kimi",), plafond="15", duree="10"),
                "preenregistrement-attaque-goodhart-v3-v4.md", True, "mode 'essai'"),
               ("non scellé", texte_preenregistrement(), "preenregistrement-attaque-goodhart-v3-v5.md", False, "non scellé"),
               ("marqueur", texte_preenregistrement(marqueur="Plafond : <<PLAFOND_USD>>\n"), "preenregistrement-attaque-goodhart-v3-v6.md", True, "marqueur"),
               ("bloc de la v2 (fichiers v3 non gelés)", texte_preenregistrement(gel=gel_v2), "preenregistrement-attaque-goodhart-v3-v7.md", True,
                "manquants.*attaque_goodhart_v3"),
               ("empreinte fausse", texte_preenregistrement(gel=[("0" * 64, gel[0][1])] + gel[1:]), "preenregistrement-attaque-goodhart-v3-v8.md",
                True, "code différent"),
               ("grille non admise", texte_preenregistrement(grille="5 cartes par monde, 20 unités par case"),
                "preenregistrement-attaque-goodhart-v3-v9.md", True, "non admise")]
        for nom, texte, fichier, sceller, motif in cas:
            with self.subTest(cas=nom):
                p = self.ecrire(texte, fichier, sceller)
                with self.assertRaisesRegex(lanceur.PreenregistrementRefuse, motif):
                    lanceur.lire_preenregistrement(p)
        autre = tempfile.mkdtemp()
        p = os.path.join(autre, "preenregistrement-attaque-goodhart-v3-v1.md")
        ecrire_scelle(p, texte_preenregistrement())
        with self.assertRaisesRegex(lanceur.PreenregistrementRefuse, "pas"):  # autre dossier
            lanceur.lire_preenregistrement(p)


def commande_a_modele(dossier, nom, texte, cout, panne=None, servi=None):
    """Commande externe factice (aucun réseau) : rend `texte`, `cout_usd` et `modele_servi` = modèle demandé (variable
    MODELE_DEMANDE_POLE) ou `servi` ; échoue (code 1, ligne de coût sans texte) si le modèle demandé est `panne`."""
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".py")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("import json, os, sys\nsys.stdin.read()\nm = os.environ.get('MODELE_DEMANDE_POLE')\n"
                f"if m == {panne!r}:\n    print(json.dumps({{'texte': '', 'cout_usd': {cout}, 'erreur': 'modele indisponible'}}))\n    sys.exit(1)\n"
                f"print(json.dumps({{'texte': {texte!r}, 'cout_usd': {cout}, 'modele_servi': {servi!r} or m, "
                "'_plafond_etape': os.environ.get('PLAFOND_ETAPE_USD')}))\n")
    return [sys.executable, "-I", "-B", chemin]


class LanceurCheminReel(unittest.TestCase):
    """Le mode réel jusqu'aux proposeurs, sans réseau : quatre commandes externes factices, portes « environnement »."""

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
        conf["fournisseurs"] = {}
        for f in QUATRE:
            conf["fournisseurs"][f["nom"]] = {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                                             "commande": commande_a_modele(self.tmp, f["nom"], loi, 0.002,
                                                                           panne="claude-opus-5-5" if f["nom"] == "opus" else None)
                                             + ["--port", str(f["port"]), "--registre", "{REGISTRE}", "--plafond-cumule-usd", "10"]}
        conf["proposeurs"] = [{"etiquette": f"prop-{f['nom']}", "modele": f["modele"], "fournisseur": f["nom"], "consigne": "consigne_proposeur"}
                              for f in QUATRE]
        self.conf = conf
        self.chemin_conf = os.path.join(self.tmp, "conf.json")
        with open(self.chemin_conf, "w", encoding="utf-8") as f:
            json.dump(conf, f)
        self.prereg = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v3-v1.md")
        ecrire_scelle(self.prereg, texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf)))
        self.registre = A54.registre_go(self.tmp, A54.ligne_go("GO-2026-11-02-07", "1000 USD", perimetre="attaque v3"),
                                        A54.ligne_go("GO-2026-11-02-08", "1000 USD", perimetre="attaque v3"))
        self.sortie = os.path.join(self.tmp, "sortie")

    def tearDown(self):
        self.patch.stop()
        self.env.stop()

    def lire_conf(self, conf=None):
        from pole import configuration_v56 as cfg
        return cfg.lire_configuration_v56(conf if conf is not None else self.conf, base=self.tmp)

    def plan(self, **kw):
        return lanceur.lire_plan(texte_preenregistrement(**kw))

    def argv(self, *plus):
        return [self.sortie, "--preenregistrement", self.prereg, "--configuration", self.chemin_conf, "--moteur", "reel",
                "--confirmer-moteur-reel", "--registre-go", self.registre, "--go", "GO-2026-11-02-07", *plus]

    def test_cas_sain_verifier_seulement_aucune_ecriture(self):
        self.assertEqual(lanceur.principal(self.argv("--verifier-seulement")), 0)
        self.assertFalse(os.path.exists(self.sortie))

    def test_cas_sain_quatre_proposeurs_part_repartie_repli_demande_explicitement(self):
        p = self.plan(plafond="1000")
        props, accuses, infos = lanceur.proposeurs_reels(self.lire_conf(), p, tempfile.mkdtemp(), self.sortie)
        self.assertEqual({n: a["plafond_usd"] for n, a in accuses.items()}, {"kimi": 250.0, "astra": 250.0, "fable": 250.0, "opus": 250.0})
        self.assertEqual(infos["budget_appel_usd"], 2.0)
        self.assertEqual(infos["modeles_demandes"], {f["nom"]: f["modele"] for f in QUATRE})
        self.assertEqual(infos["replis_declares"]["opus"], "claude-opus-4-6")
        self.assertEqual(infos["ports"], {"kimi": 8804, "astra": 8807, "fable": 8806, "opus": 8806})
        self.assertEqual(len(infos["substitutions_dans_les_commandes"]), 8)  # {REGISTRE} et --plafond-cumule-usd, quatre commandes
        for n in a3.noms(QUATRE):
            commande = infos["adaptateurs"][n]["commande"]
            self.assertNotIn("{REGISTRE}", json.dumps(commande))
            self.assertEqual(commande[commande.index("--plafond-cumule-usd") + 1], "1000")
            self.assertIn("empreintes", infos["adaptateurs"][n])
        cpt = compteur(fournisseurs=QUATRE)
        c = ag.carte(G, 0, "W1")
        for f in QUATRE:
            s = a3.jouer_unite(props[f["nom"]], f, c, G, cpt, 1, 2)
            self.assertIsNotNone(s[0]["tentatives"][0]["loi"], s[0]["tentatives"][0]["motif_invalidite"])
        self.assertEqual(cpt.modeles_servis, {"kimi": ["kimi-k3.1-pro"], "astra": ["gpt-6-astra"], "fable": ["claude-fable-5-1"],
                                              "opus": ["claude-opus-4-6"]})
        self.assertEqual(cpt.replis, {"kimi": 0, "astra": 0, "fable": 0, "opus": 1})
        self.assertEqual(cpt.par_modele["opus"]["claude-opus-5-5"], {"appels": 2, "reussis": 0, "echecs": 2, "usd": 0.004, "modeles_servis": []})
        self.assertGreater(cpt.par_fournisseur["astra"], 0)

    def test_configuration_deux_fournisseurs_un_au_plan(self):
        """Configuration à quatre fournisseurs, plan à un seul (Astra) : `--verifier-seulement` → 0 sans écriture ; un adaptateur,
        accusé = plafond entier pour la seule porte, étape propre ; les autres relais sans effet."""
        texte = texte_preenregistrement(fournisseurs=("astra",), grille="24 cartes par monde, 24 unités par case", conf_sha=sha256_fichier(self.chemin_conf))
        p = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v3-v2.md")
        ecrire_scelle(p, texte)
        self.assertEqual(lanceur.principal(self.argv()[:2] + [p] + self.argv()[3:] + ["--verifier-seulement"]), 0)
        self.assertFalse(os.path.exists(self.sortie))
        props, accuses, infos = lanceur.proposeurs_reels(self.lire_conf(), lanceur.lire_plan(texte), tempfile.mkdtemp(), self.sortie)
        self.assertEqual((sorted(props), sorted(accuses), sorted(infos["adaptateurs"])), (["astra"], ["astra"], ["astra"]))
        self.assertEqual((accuses["astra"]["etape"], accuses["astra"]["plafond_usd"]), ("attaque_goodhart_v3/astra", 1000.0))

    def test_modele_servi_autre_que_demande_refuse_jamais_un_repli_muet(self):
        """Artefact : la commande d'Opus sert 4.6 quand on lui demande 5.5 → statut « refus », compté en échec ; l'unité bascule
        alors explicitement (repli déclaré), jamais en recopiant le modèle servi."""
        loi = json.dumps({"retour_lu": "aucun", "loi": {"type": "fixe", "probas": [2, 1, 1]}})
        conf = json.loads(json.dumps(self.conf))
        conf["fournisseurs"]["opus"]["commande"] = commande_a_modele(self.tmp, "opus-menteur", loi, 0.002, servi="claude-opus-4-6") + ["--port", "8806"]
        props, _, _ = lanceur.proposeurs_reels(self.lire_conf(conf), self.plan(), tempfile.mkdtemp(), self.sortie)
        r = props["opus"]("consigne", "claude-opus-5-5")
        self.assertEqual((r[2], r[3]), ("refus", "claude-opus-4-6"))
        cpt = compteur(fournisseurs=[OPUS])
        s = a3.jouer_unite(props["opus"], OPUS, ag.carte(G, 0, "W1"), G, cpt, 1, 2)
        self.assertTrue(all(x["repli"] for x in s))
        self.assertEqual([a["statut"] for a in s[0]["appels_avant_repli"]], ["refus", "refus"])

    def test_artefacts_de_configuration(self):
        import aides_v56 as A
        conf = self.conf
        sans_astra = {k: v for k, v in conf["fournisseurs"].items() if k != "astra"}
        cas = {"fournisseur absent": (dict(conf, fournisseurs=sans_astra), {}, "absent de la configuration"),
               "autre type d'adaptateur": (dict(conf, fournisseurs=dict(conf["fournisseurs"], astra={
                   "type": "kimi_protocole", "url_relais": "http://127.0.0.1:1", "modele": "gpt-6-astra", "prix_entree": 1, "prix_sortie": 1,
                   "max_sortie_jetons": 100, "sortie_min_jetons": 10, "delai_s": 1,
                   "porte_plafond": {"type": "commande", "commande": A.porte_factice(self.tmp, "porte-astra"), "delai_s": 30}})), {}, "type"),
               "commande manquante": (dict(conf, fournisseurs=dict(conf["fournisseurs"], astra={
                   "type": "commande_externe", "porte_plafond": {"type": "environnement"}})), {}, "commande.*manque"),
               "port absent de la commande": (dict(conf, fournisseurs=dict(conf["fournisseurs"], astra=dict(
                   conf["fournisseurs"]["astra"], commande=[x for x in conf["fournisseurs"]["astra"]["commande"] if x != "8807"]))), {}, "port 8807"),
               "proposeur d'un autre modèle": (dict(conf, proposeurs=[dict(p, modele="gpt-6-mini") if p["fournisseur"] == "astra" else p
                                                                       for p in conf["proposeurs"]]), {}, "le plan dit"),
               "proposeur absent": (dict(conf, proposeurs=[p for p in conf["proposeurs"] if p["fournisseur"] != "astra"]), {}, "proposeur « astra »"),
               "modeles_servis_permis non vide (repli muet)": (dict(conf, fournisseurs=dict(conf["fournisseurs"], opus=dict(
                   conf["fournisseurs"]["opus"], modeles_servis_permis={"claude-opus-5-5": ["claude-opus-4-6"]}))), {}, "repli muet"),
               "budget absent": (dict(conf, plafonds_session={"juge": 0.5}), {}, "plafonds_session.proposeur")}
        for nom, (c, kw, motif) in cas.items():
            with self.subTest(cas=nom), self.assertRaisesRegex(ag.AttaqueRefusee, motif):
                lanceur.proposeurs_reels(self.lire_conf(c), self.plan(**kw), tempfile.mkdtemp(), self.sortie)
        with unittest.mock.patch.dict(os.environ, {"GH_TOKEN": "x"}), self.assertRaisesRegex(ag.AttaqueRefusee, "clé"):
            lanceur.proposeurs_reels(self.lire_conf(), self.plan(), tempfile.mkdtemp(), self.sortie)
        # cas sain : un fournisseur de la configuration absent du plan n'empêche rien
        props, _, _ = lanceur.proposeurs_reels(self.lire_conf(), self.plan(fournisseurs=("kimi", "opus"), grille="12 cartes par monde, 24 unités par case", duree="100"),
                                               tempfile.mkdtemp(), self.sortie)
        self.assertEqual(sorted(props), ["kimi", "opus"])

    def test_refus_du_lanceur_isoles(self):
        """Chaque refus avec registre et configuration valides par ailleurs ; rien n'est écrit."""
        v2 = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v2-v1.md")
        ecrire_scelle(v2, texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf)))
        fiche = os.path.join(self.prereg_dir, "fiche-essai-attaque-goodhart-v3-v1.md")
        ecrire_scelle(fiche, texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf)))  # mode course sous un nom d'essai
        non_scelle = os.path.join(self.prereg_dir, "preenregistrement-attaque-goodhart-v3-v2.md")
        with open(non_scelle, "w", encoding="utf-8") as f:
            f.write(texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf)))
        autre_conf = os.path.join(self.tmp, "conf-autre.json")
        with open(autre_conf, "w", encoding="utf-8") as f:
            json.dump(dict(self.conf, note="autre"), f)
        for nom, argv in (("autre configuration", self.argv()[:4] + [autre_conf] + self.argv()[5:]),
                          ("GO autre que celui du texte", self.argv()[:-1] + ["GO-2026-11-02-08"]),
                          ("texte au chemin de la v2", self.argv()[:2] + [v2] + self.argv()[3:]),
                          ("fiche d'essai à mode course", self.argv()[:2] + [fiche] + self.argv()[3:]),
                          ("non scellé", self.argv()[:2] + [non_scelle] + self.argv()[3:]),
                          ("option de plan", self.argv("--fils", "2")),
                          ("code de panne en réel", self.argv("--code-panne", "4")),
                          ("mode en ligne de commande", self.argv("--mode", "essai")),
                          ("graine en réel", self.argv("--graine", "7"))):
            with self.subTest(cas=nom):
                self.assertEqual(lanceur.principal(argv + ["--verifier-seulement"]), 2)
                self.assertFalse(os.path.exists(self.sortie))

    def test_essai_reel_de_bout_en_bout_sans_issue(self):
        """Fiche d'essai scellée, Kimi seul, commande factice : code 0, sortie d'essai scellée sans issue, manifeste."""
        import aides_v54 as A54
        fiche = os.path.join(self.prereg_dir, "fiche-essai-attaque-goodhart-v3-v1.md")
        ecrire_scelle(fiche, texte_preenregistrement("essai", fournisseurs=("kimi",), plafond="15", duree="10", go="GO-2026-11-02-11",
                                                     conf_sha=sha256_fichier(self.chemin_conf), appels_max="6"))
        registre = A54.registre_go(self.tmp, A54.ligne_go("GO-2026-11-02-11", "15 USD", perimetre="essai Kimi"), nom="go-essai.md")
        argv = [self.sortie, "--preenregistrement", fiche, "--configuration", self.chemin_conf, "--moteur", "reel", "--confirmer-moteur-reel",
                "--registre-go", registre, "--go", "GO-2026-11-02-11"]
        self.assertEqual(lanceur.principal(argv), 0)
        with open(os.path.join(self.sortie, "essai-attaque-goodhart-v3.json"), encoding="utf-8") as f:
            r = json.load(f)
        self.assertNotIn("issue", r)
        self.assertNotIn("lecture", r)
        self.assertEqual(r["appels"], 6)
        self.assertEqual(r["mesures"]["kimi"]["par_modele_demande"]["kimi-k3.1-pro"]["modeles_servis"], ["kimi-k3.1-pro"])
        self.assertEqual(r["mesures"]["kimi"]["par_modele_demande"]["kimi-k3.1-pro"]["cout_usd_par_appel_reussi"]["maximum"], 0.002)
        self.assertTrue(os.path.isfile(os.path.join(self.sortie, "essai-attaque-goodhart-v3.json.sha256")))
        with open(os.path.join(self.sortie, "manifeste.json"), encoding="utf-8") as f:
            m = json.load(f)
        self.assertEqual(m["reglages"]["plan"]["mode"], "essai")
        self.assertEqual(m["reglages"]["configuration"]["modeles_demandes"], {"kimi": "kimi-k3.1-pro"})


class LanceurABlanc(unittest.TestCase):
    def test_refus_avant_toute_ecriture(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", str(2 ** 64)]), 2)
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--fournisseurs", "kimi,gemini"]), 2)  # nom inconnu à blanc
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--relais-perdu-h", "0"]), 2)
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--panne", "x"]), 2)
            self.assertFalse(os.path.exists(sortie))

    def test_course_a_blanc_avec_repli_sur_une_unite(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--cartes", "1", "--n-max", "2", "--rejeux-v8", "1",
                                                "--rejeux-v7", "1", "--rejeux-audit", "2", "--processus", "1", "--fils", "2",
                                                "--panne", "claude-opus-5-5:1-3"]), 0)
            with open(os.path.join(sortie, "attaque-goodhart-v3.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertEqual(sorted(r["lecture"]["issues"]), ["W1", "W2"])
            self.assertEqual(r["unites_basculees_sur_repli"], {"kimi": 0, "astra": 0, "fable": 0, "opus": 1})
            self.assertEqual(r["lecture"]["mondes"]["W1"]["taux"]["v8|retour|n=16|opus-repli"]["unites"], 1)
            with open(os.path.join(sortie, "manifeste.json"), encoding="utf-8") as f:
                m = json.load(f)
            self.assertEqual(sorted(m["reglages"]["code_sha256"]), sorted(lanceur.FICHIERS_GELES))
            self.assertEqual([x["nom"] for x in m["reglages"]["plan"]["fournisseurs"]], ["kimi", "astra", "fable", "opus"])

    def test_course_a_blanc_code_4_compte_a_part_et_unites_sans_loi(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--cartes", "1", "--mondes", "W1", "--fournisseurs", "kimi,astra",
                                                "--n-max", "2", "--rejeux-v8", "1", "--rejeux-v7", "1", "--rejeux-audit", "2", "--processus", "1",
                                                "--panne", "kimi-k3.1-pro:*", "--code-panne", "4"]), 0)
            with open(os.path.join(sortie, "attaque-goodhart-v3.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertEqual(r["appels_budget_depasse"], {"kimi": 16, "astra": 0})
            u = r["unites_sans_loi"]
            self.assertEqual((u["total_sans_loi"], u["par_case"]["W1|kimi|retour|v8"]["sans_loi"], u["par_case"]["W1|astra|retour|v8"]["sans_loi"]), (4, 1, 0))
            self.assertTrue(all(x["cause_dominante"] == "budget" and x["fournisseur"] == "kimi" for x in u["par_unite"]))
            self.assertTrue(any(a.startswith("A7") for a in r["lecture"]["mondes"]["W1"]["audits"]))
            self.assertEqual(r["lecture"]["issues"]["W1"], "non jugeable (précision insuffisante)")  # la lecture ne change pas
            with self.assertRaises(SystemExit):  # argparse : un code non entier est refusé avant toute écriture
                lanceur.principal([os.path.join(d, "t"), "--a-blanc", "--graine", "7", "--code-panne", "x"])
            self.assertFalse(os.path.exists(os.path.join(d, "t")))

    def test_essai_a_blanc_sans_issue_et_arret_code_3(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--mode", "essai", "--fournisseurs", "kimi", "--appels-max",
                                                "5", "--n-max", "3", "--processus", "1"]), 0)
            with open(os.path.join(sortie, "essai-attaque-goodhart-v3.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertNotIn("issue", r)
            self.assertEqual(r["appels"], 5)
            sortie2 = os.path.join(d, "t")
            self.assertEqual(lanceur.principal([sortie2, "--a-blanc", "--graine", "7", "--cartes", "1", "--n-max", "3", "--plafond-usd", "0.05",
                                                "--cout-simule-usd", "0.01", "--processus", "1"]), 3)
            with open(os.path.join(sortie2, "attaque-goodhart-v3.json"), encoding="utf-8") as f:
                r = json.load(f)
            self.assertTrue(r["suites_partielles"])
            self.assertEqual(r["issue"], "non jugeable (arrêt) : aucun taux lu")


class Fermeture(unittest.TestCase):
    def test_fichiers_geles_egaux_a_la_fermeture(self):
        """Le code que le chemin réel v3 importe (processus neuf, imports et chargements par fichier) est exactement
        `FICHIERS_GELES` : la fermeture de la v2 plus les deux fichiers v3."""
        script = (
            "import importlib.util, json, os, sys\nR = os.path.realpath(sys.argv[1])\nvus = set()\n"
            "def crochet(e, a):\n    if e == 'open' and a and isinstance(a[0], str) and a[0].endswith(('.py', '.pyc')):\n"
            "        vus.add(os.path.realpath(a[0]))\nsys.addaudithook(crochet)\nsys.path.insert(0, R)\n"
            "s = importlib.util.spec_from_file_location('l', os.path.join(R, 'demonstrations', 'attaque_goodhart_v3.py'))\n"
            "m = importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\nm.l2.charger_ideation_v8()\nm.ag.banc()\n"
            "import pole.relais, pole.configuration_v56, pole.adaptateurs_v56\n"
            "f = {os.path.realpath(getattr(x, '__file__', '') or '') for x in list(sys.modules.values())} | vus\n"
            "def source(p):\n    if p.endswith('.pyc') and os.path.basename(os.path.dirname(p)) == '__pycache__':\n"
            "        p = os.path.join(os.path.dirname(os.path.dirname(p)), os.path.basename(p).split('.')[0] + '.py')\n    return p\n"
            "print(json.dumps(sorted({os.path.relpath(source(p), R) for p in f if p.startswith(R + os.sep)})))\n")
        sortie = subprocess.run([sys.executable, "-I", "-B", "-c", script, RACINE], capture_output=True, text=True, check=True)
        self.assertEqual(sorted(json.loads(sortie.stdout)), sorted(lanceur.FICHIERS_GELES))
        self.assertEqual(len(lanceur.FICHIERS_GELES), len(lanceur.l2.FICHIERS_GELES) + 2)


if __name__ == "__main__":
    unittest.main()
