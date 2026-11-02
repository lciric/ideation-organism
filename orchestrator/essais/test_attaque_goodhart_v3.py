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
            self.assertEqual(set(a), {"essai_d_appel", "statut", "cout_usd", "duree_s", "modele_demande", "modele_servi"})
            self.assertEqual(a["modele_demande"], "claude-opus-5-5")
            self.assertEqual(a["modele_servi"], "claude-opus-5-5" if a["statut"] == "ok" else None)

    def test_essais_avant_repli_borne(self):
        for e in (0, 11, True):
            with self.subTest(e=e), self.assertRaisesRegex(ag.AttaqueRefusee, "essais_avant_repli"):
                self.unite({}, essais=e)


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
        self.assertEqual(v3["issue"], v2["issue"])
        self.assertEqual({k: v for k, v in v3["taux"].items() if "repli" not in k}, v2["taux"])
        self.assertTrue(all(v["unites"] == 0 for k, v in v3["taux"].items() if "repli" in k))
        for k in ("ecarts_goodhart_par_carte", "ecart_par_loi_H3", "predictions", "audits", "instrument_v8_retour", "breche", "dents",
                  "resiste", "eps_resistance", "qualification_breche"):
            self.assertEqual(v3[k], v2[k], k)


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


# --- lanceur ------------------------------------------------------------------------------------------------------------
LIGNES_FOURNISSEURS = {f["nom"]: (f"type={f['type']}, port={f['port']}, modele={f['modele']}" + (f", repli={f['repli']}" if f.get("repli") else "")
                                  + f", fils={f['fils']}, taux_usd={f['taux_usd']}, secondes={f['secondes'][0]:g}-{f['secondes'][1]:g}")
                       for f in QUATRE}


def texte_preenregistrement(mode="course", gel=None, grille="6 cartes par monde, 24 unités par case", cartes="1", mondes="W1 et W2",
                            fournisseurs=("kimi", "astra", "fable", "opus"), lignes_f=None, plafond="1000", duree="60", fixe=None,
                            marqueur="", conf_sha="c" * 64, go="GO-2026-11-02-07", essais="3", appels_max="20", sans=(), plus=""):
    gel = gel if gel is not None else [(sha256_fichier(os.path.join(RACINE, r)), r) for r in lanceur.FICHIERS_GELES]
    lignes = dict(lanceur.PLAN_FIXE[mode], **(fixe or {}))
    lf = dict(LIGNES_FOURNISSEURS, **(lignes_f or {}))
    corps = [f"mode: {mode}", f"grille: {grille}" if mode == "course" else f"cartes: {cartes}", f"mondes: {mondes}",
             "fournisseurs: " + ", ".join(fournisseurs)] + [f"fournisseur_{n}: {lf[n]}" for n in fournisseurs] + \
            [f"essais_avant_repli: {essais}"] + ([f"appels_max_par_fournisseur: {appels_max}"] if mode == "essai" else []) + \
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
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--fournisseurs", "kimi,argon"]), 2)
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
