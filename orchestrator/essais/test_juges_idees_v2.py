"""Essais de l'étage des juges d'idéation v2 (`pole/juges_idees_v2.py`) et de son lanceur de validation
(`demonstrations/validation_juges_idees_v2.py`) — R5 : chaque garde sur un cas sain et sur un artefact. Hors ligne : juges
scriptés, commandes externes factices (scripts Python locaux, aucun réseau), aucune clé, aucun appel de modèle.

  python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py     (depuis le dossier orchestrator)
"""

import copy
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
for _p in (RACINE, ICI):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pole import fiches_v53 as fv53  # noqa: E402
from pole import juges_croises_v53 as jc53  # noqa: E402
from pole import juges_idees_v2 as J  # noqa: E402
from pole.graines_v53 import Graines  # noqa: E402
from pole.outils import empreinte_objet, ecrire_scelle, sha256_fichier  # noqa: E402


def _charger_lanceur():
    nom = "lanceur_validation_juges_idees_v2"
    if nom in sys.modules:
        return sys.modules[nom]
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, "demonstrations", "validation_juges_idees_v2.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nom] = m
    spec.loader.exec_module(m)
    return m


lanceur = _charger_lanceur()
MATERIAUX = J.construire_materiaux()
A = dict(lanceur.JUGES_A_BLANC["juge_a"])
B = dict(lanceur.JUGES_A_BLANC["juge_b"])
CORRESP = dict(lanceur.CORRESPONDANCE_A_BLANC)
CONSIGNES = {"ancien": J.CONSIGNE_ANCIENNE_SUBSTITUTION, "v2": J.CONSIGNE_PAIRE_V2}


def materiaux():
    return copy.deepcopy(MATERIAUX)


def resceller(m):
    m["empreinte"] = empreinte_objet({k: v for k, v in m.items() if k != "empreinte"})
    return m


def lot_reel(graine=3):
    objet, qualites = J.lot_reel_substitution(graine)
    return J.lot_reel_depuis(objet, J.QUESTION_SUBSTITUTION, CORRESP), qualites


def course(strategie_a, strategie_b, *, graine=11, avec_reel=False, couts=(0.0, 0.0), plafond=1e9, duree=1e9, horloge=None,
           modele_servi_a=None, adaptateurs=None, **kw):
    """Une course complète à juges scriptés ; rend (journal, mesures, lecture, étapes) ou lève l'arrêt."""
    m = MATERIAUX
    reel, qualites = lot_reel() if avec_reel else (None, None)
    g = Graines(graine)
    etapes, _ = J.etapes_v1(m, A, B, g, lot_reel=reel)
    oracle = J.oracle_depuis(m, reel, qualites)
    ad = adaptateurs or {A["fournisseur"]: J.AdaptateurScripte(strategie_a, oracle, graine=graine, cout_par_appel_usd=couts[0],
                                                               modele_servi=modele_servi_a, **kw),
                         B["fournisseur"]: J.AdaptateurScripte(strategie_b, oracle, graine=graine + 1, cout_par_appel_usd=couts[1], **kw)}
    c = J.Compteur(plafond, duree, horloge or time.monotonic, {A["etiquette"]: A["prix_usd"], B["etiquette"]: B["prix_usd"]})
    journal = J.executer_validation(etapes, materiaux=m, juges={A["etiquette"]: A, B["etiquette"]: B}, adaptateurs=ad, consignes=CONSIGNES,
                                    items=J.ITEMS_SUBSTITUTION, graines=g, compteur=c, plafond_session=0.5,
                                    interdites=J.ETIQUETTES_INTERDITES_TEMOINS, dossier_appel=lambda j, e: os.devnull, lot_reel=reel)
    mes = J.mesurer(journal, m, A, B, etapes=etapes, lot_reel=reel)
    return journal, mes, J.lire_validation(mes), etapes


_COURSES = {}


def course_memo(a, b):
    if (a, b) not in _COURSES:
        _COURSES[(a, b)] = course(a, b)
    return _COURSES[(a, b)]


def fiche(ident, **contenu):
    c = {"titre": f"Titre {ident}", "hypothese": f"Hypothèse propre à la fiche {ident} : le taux d'alerte croît nettement.",
         "prediction": "Sur 600 nouveaux épisodes, l'écart sera d'au moins 4 points.", "signe": "+",
         "metrique": "écart de taux d'alerte, en points", "test_de_mort": "Abandon si l'écart est inférieur à 2 points."}
    c.update(contenu)
    return {"ident": ident, "contenu": c}


# --- matériaux -----------------------------------------------------------------------------------------------------------------


class Materiaux(unittest.TestCase):
    def test_cas_sain_deterministe_composition_et_garde(self):
        self.assertEqual(J.construire_materiaux()["empreinte"], MATERIAUX["empreinte"])
        self.assertEqual(J.verifier_materiaux(MATERIAUX), [])
        forme = J.exiger_materiaux(materiaux(), MATERIAUX["empreinte"])
        self.assertTrue(forme["conforme"])
        self.assertEqual([len(l["fiches"]) for l in MATERIAUX["lots"]], [12, 12])
        ev = [f for l in MATERIAUX["lots"] for f in l["fiches"] if f["role"] == "evaluation"]
        classes = {}
        for f in ev:
            classes[f["classe"]] = classes.get(f["classe"], 0) + 1
        self.assertEqual(classes, {"vraie_neuve": 10, "fausse_redigee": 3, "copie_archive": 3, "tautologie": 2, "verbeuse": 2})
        for l in MATERIAUX["lots"]:
            self.assertEqual(sorted(f["role"] for f in l["fiches"] if f["role"] != "evaluation"), ["ancre_bonne", "ancre_mauvaise"])
            self.assertTrue(J.dossier_a_preuves(l["dossier"]))

    def test_artefact_materiaux_alteres_ou_autre_empreinte(self):
        m = materiaux()
        m["lots"][0]["fiches"][0]["contenu"]["hypothese"] += " Ajout."
        with self.assertRaisesRegex(J.ProtocoleRefuse, "empreinte interne fausse"):
            J.exiger_materiaux(m)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "le texte scellé gèle"):
            J.exiger_materiaux(resceller(m), MATERIAUX["empreinte"])
        with self.assertRaisesRegex(J.ProtocoleRefuse, "graine des matériaux"):
            J.construire_materiaux(-1)

    def test_artefact_verite_non_etablie(self):
        """Table altérée : la caractéristique sans effet d'une loi fausse montre l'effet affirmé → vérité connue perdue."""
        m = materiaux()
        lot = m["lots"][0]
        lot["tables"]["table1"]["heure"][1]["taux"] = lot["tables"]["table1"]["heure"][0]["taux"] + 7.0
        ecarts = J.verifier_materiaux(m)
        self.assertTrue(any("heure" in e for e in ecarts), ecarts)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "vérité connue non établie"):
            J.exiger_materiaux(resceller(m))
        m2 = materiaux()
        bonne = next(f for f in m2["lots"][1]["fiches"] if f["classe"] == "vraie_neuve" and f["loi"]["type"] == "monotone")
        bonne["loi"]["affirme"] = [bonne["loi"]["affirme"][0] + 5, bonne["loi"]["affirme"][1]]
        self.assertTrue(any("chiffres affirmés" in e for e in J.verifier_materiaux(m2)))
        m3 = materiaux()
        fausse = next(f for f in m3["lots"][0]["fiches"] if f["classe"] == "fausse_redigee")
        fausse["loi"]["affirme"] = [fausse["loi"]["affirme"][1] + 1, fausse["loi"]["affirme"][1]]  # écart affirmé trop petit
        self.assertTrue(any("loi fausse non contredite" in e for e in J.verifier_materiaux(m3)))

    def test_artefact_forme_favorable_aux_bons_temoins(self):
        m = materiaux()
        for l in m["lots"]:
            for f in l["fiches"]:
                if f["classe"] == "vraie_neuve":
                    f["contenu"]["hypothese"] += " Précision : " + "détail " * 200 + "1234567890" * 5
        forme = J.controle_forme(m)
        self.assertFalse(forme["conforme"])
        with self.assertRaisesRegex(J.ProtocoleRefuse, "indice de forme"):
            J.exiger_materiaux(resceller(m))

    def test_artefact_etiquette_interdite_dans_un_temoin(self):
        m = materiaux()
        m["lots"][1]["fiches"][3]["contenu"]["titre"] = "Un témoin de la loi"
        with self.assertRaisesRegex(J.ProtocoleRefuse, "étiquette interdite"):
            J.exiger_materiaux(resceller(m))

    def test_bons_temoins_hors_des_lois_etablies_et_mauvais_contredits(self):
        specs = {s["nom"]: s for s in J.MONDES_V1}
        for l in MATERIAUX["lots"]:
            for f in l["fiches"]:
                if f["loi"]["type"] in ("monotone", "binaire", "categorie"):
                    role = J._caracteristique(specs[l["nom"]], f["loi"]["caracteristique"])["role"]
                    self.assertEqual(role == "etablie", f["classe"] == "copie_archive", f["ident"])


# --- consigne, entrées servies ---------------------------------------------------------------------------------------------------


class Entrees(unittest.TestCase):
    def test_cas_sain_consigne_et_entree_paire_aveugles(self):
        self.assertEqual(J.EMPREINTE_CONSIGNE_PAIRE_V2, __import__("hashlib").sha256(J.CONSIGNE_PAIRE_V2.encode()).hexdigest())
        lot = MATERIAUX["lots"][0]
        f1, f2 = lot["fiches"][0], lot["fiches"][6]
        e = J.entree_paire(J.CONSIGNE_PAIRE_V2, lot["dossier"], ("FAAAA", f1), ("FBBBB", f2), J.ETIQUETTES_INTERDITES_TEMOINS)
        self.assertIn("## Fiche FAAAA (présentée en premier)", e)
        self.assertIn("## Fiche FBBBB (présentée en second)", e)
        self.assertIn(lot["dossier"].strip(), e)
        for interdit in (f1["ident"], f2["ident"], "vraie_neuve", "fausse_redigee", "evaluation", "qualite"):
            self.assertNotIn(interdit, e)
        self.assertTrue(J.exiger_entrees(MATERIAUX["lots"], CONSIGNES))

    def test_entree_ancienne_sans_dossier_identique_a_la_v53(self):
        f = fiche("x")
        attendu = fv53.entree_une_fiche("Consigne figée.", {"contenu": f["contenu"]}, ["témoin"], identifiant_servi="F123")
        self.assertEqual(J.entree_ancienne("Consigne figée.", f, "F123", ["témoin"]), attendu)

    def test_artefacts_etiquette_et_champ_reserve(self):
        lot = MATERIAUX["lots"][0]
        with self.assertRaises(fv53.EtiquetteDansEntree):
            J.entree_paire(J.CONSIGNE_PAIRE_V2, lot["dossier"], ("F1", fiche("a", titre="Une ancre")), ("F2", fiche("b")),
                           J.ETIQUETTES_INTERDITES_TEMOINS)
        with self.assertRaises(J.ProtocoleRefuse):
            J.vue_servie(fiche("a", identifiant="X"), "F1")
        with self.assertRaisesRegex(J.ProtocoleRefuse, "garde A4"):
            J.exiger_entrees(MATERIAUX["lots"], {"ancien": "Consigne qui parle d'un témoin.", "v2": J.CONSIGNE_PAIRE_V2})
        with self.assertRaisesRegex(J.ProtocoleRefuse, "garde A4"):
            J.exiger_entrees(MATERIAUX["lots"], {"ancien": J.CONSIGNE_ANCIENNE_SUBSTITUTION, "v2": "Consigne v2 qui parle d'un témoin."})


# --- lecture des comparaisons (preuve citée) -------------------------------------------------------------------------------------


def reponse(**c):
    corps = {"preferee": "F1", "critere": "verite", "citation_fiche": "Hypothèse propre à la fiche a",
             "citation_dossier": "D01 · part des commandes réseau"}
    corps.update(c)
    return "```json\n" + json.dumps({"comparaison": corps}, ensure_ascii=False) + "\n```"


class Citations(unittest.TestCase):
    def setUp(self):
        self.p, self.s = ("F1", fiche("a")), ("F2", fiche("b"))
        self.dossier = MATERIAUX["lots"][0]["dossier"]

    def test_cas_sain(self):
        lu = J.lire_comparaison(reponse(), self.p, self.s, self.dossier)
        self.assertTrue(lu["valide"], lu)
        self.assertTrue(lu["premier_gagne"])
        lu = J.lire_comparaison(reponse(preferee="F2", citation_fiche="« Hypothèse propre à la fiche b »"), self.p, self.s, self.dossier)
        self.assertTrue(lu["valide"] and lu["premier_gagne"] is False, lu)
        sans_faits = "## Dossier\n\nLa question posée, sans ligne de faits.\n"
        self.assertTrue(J.lire_comparaison(reponse(citation_dossier=""), self.p, self.s, sans_faits)["valide"])

    def test_cas_sain_normalisation_typographique(self):
        f = fiche("c", hypothese="Les épisodes que le moniteur classe « suspects » reçoivent l’alerte plus souvent.")
        lu = J.lire_comparaison(reponse(citation_fiche='classe "suspects" reçoivent L\'ALERTE plus souvent...'), ("F1", f),
                                self.s, self.dossier)
        self.assertTrue(lu["valide"], lu)

    def test_artefacts(self):
        cas = {"identifiant inconnu": (reponse(preferee="F9"), "aucun des deux"),
               "critère hors liste": (reponse(critere="style"), "critère"),
               "citation inventée": (reponse(citation_fiche="une phrase absente de la fiche choisie"), "introuvable"),
               "citation prise dans l'autre fiche": (reponse(citation_fiche="Hypothèse propre à la fiche b"), "introuvable"),
               "citation commune aux deux fiches": (reponse(citation_fiche="Sur 600 nouveaux épisodes, l'écart"), "commune"),
               "citation trop courte": (reponse(citation_fiche="fiche a"), "trop courte"),
               "citation du dossier absente": (reponse(citation_dossier=""), "dossier"),
               "citation du dossier inventée": (reponse(citation_dossier="D99 · ligne qui n'existe pas"), "dossier")}
        for nom, (texte, motif) in cas.items():
            with self.subTest(cas=nom):
                lu = J.lire_comparaison(texte, self.p, self.s, self.dossier)
                self.assertFalse(lu["valide"], lu)
                self.assertIn(motif, lu["motif"])
        self.assertIsNone(J.lire_comparaison("je préfère la première", self.p, self.s, self.dossier))


# --- plan des comparaisons, règle de famille, devis ---------------------------------------------------------------------------


class Plan(unittest.TestCase):
    def test_cas_sain_graphe_regulier_connexe_deterministe(self):
        ids = [f"c{k}" for k in range(12)]
        for d in (2, 3, 4, 5):
            g = J.graphe_circulant(ids, d, Graines(5).generateur("g"))
            self.assertEqual(set(J.degres(g["paires"]).values()), {d})
            self.assertEqual(len(g["paires"]), 12 * d // 2)
            self.assertEqual(len(set(g["paires"])), len(g["paires"]))
            vus, pile = {ids[0]}, [ids[0]]
            while pile:
                x = pile.pop()
                for a, b in g["paires"]:
                    for y in ((b,) if a == x else (a,) if b == x else ()):
                        if y not in vus:
                            vus.add(y)
                            pile.append(y)
            self.assertEqual(vus, set(ids))
        self.assertEqual(J.graphe_circulant(ids, 3, Graines(5).generateur("g")), J.graphe_circulant(ids, 3, Graines(5).generateur("g")))

    def test_artefacts_graphe(self):
        for ids, d in ((["a", "b", "c"], 3), (["a", "b", "c", "d"], 1), (["a", "b", "c", "d", "e"], 3), (["a", "a", "b", "c"], 2)):
            with self.subTest(n=len(ids), d=d), self.assertRaises(J.ProtocoleRefuse):
                J.graphe_circulant(ids, d, Graines(1).generateur("g"))

    def test_appels_deux_ordres_ou_un(self):
        paires = [("a", "b"), ("b", "c"), ("a", "c")]
        appels = J.appels_paires(paires, True, Graines(2).generateur("o"))
        self.assertEqual(len(appels), 6)
        for a, b in paires:
            self.assertEqual({x for x in appels if set(x) == {a, b}}, {(a, b), (b, a)})
        self.assertEqual(len(J.appels_paires(paires, False, Graines(2).generateur("o"))), 3)

    def test_cas_sain_etapes_v1(self):
        reel, _ = lot_reel()
        etapes, graphes = J.etapes_v1(MATERIAUX, A, B, Graines(9), lot_reel=reel)
        self.assertEqual([e["phase"] for e in etapes], sorted([e["phase"] for e in etapes], key=J.PHASES_V1.index))
        n = {}
        for e in etapes:
            n[(e["phase"], e["juge"], e["protocole"])] = n.get((e["phase"], e["juge"], e["protocole"]), 0) + J.nombre_appels(e)
        self.assertEqual(n[("decisive-a", A["etiquette"], "ancien")], 20)
        self.assertEqual(n[("decisive-a", A["etiquette"], "v2")], 144)
        self.assertEqual(n[("decisive-b", B["etiquette"], "ancien")], 20)
        self.assertLessEqual(n[("decisive-b", B["etiquette"], "v2")], 2 * J.PAIRES_B_MAX_PAR_LOT)
        q = {f["ident"]: f["qualite"] for l in MATERIAUX["lots"] for f in l["fiches"]}
        for e in etapes:
            if e["phase"] == "decisive-b" and e["protocole"] == "v2":
                self.assertTrue(all(q[x] != q[y] for x, y in e["appels"]))
        d = J.devis(etapes, {A["etiquette"]: A, B["etiquette"]: B})
        self.assertLessEqual(d["total_usd"], 30.0)

    def test_artefacts_juges_de_la_famille_des_gabarits_ou_de_meme_famille(self):
        with self.assertRaisesRegex(J.ProtocoleRefuse, "auteur des gabarits"):
            J.etapes_v1(MATERIAUX, dict(A, famille="claude"), B, Graines(1))
        with self.assertRaisesRegex(J.ProtocoleRefuse, "distinctes"):
            J.etapes_v1(MATERIAUX, A, dict(B, famille=A["famille"]), Graines(1))

    def test_regle_de_famille_sur_le_lot_reel(self):
        reel, _ = lot_reel()
        fam = {f["ident"]: set(f["familles"]) for f in reel["fiches"]}
        self.assertEqual(fam["reel-12"], {"kimi", "gemini"})  # une fusion : les familles de ses parents aussi
        etapes, _ = J.etapes_v1(MATERIAUX, A, B, Graines(9), lot_reel=reel)
        for e in etapes:
            if e["lot"] == "reel":
                ids = e["fiches"] if e["protocole"] == "ancien" else [i for p in e["appels"] for i in p]
                juge = A if e["juge"] == A["etiquette"] else B
                self.assertTrue(all(juge["famille"] not in fam[i] for i in ids), e["juge"])
        artefact = {"phase": "reel-ancien", "protocole": "ancien", "lot": "reel", "juge": A["etiquette"], "tirage": 1,
                    "fiches": ["reel-02"]}  # fiche d'auteur argon (famille du juge A)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "règle de famille"):
            J.jouer_etape(artefact, lots={"reel": reel}, juges={A["etiquette"]: A}, adaptateurs={A["fournisseur"]: None},
                          consignes=CONSIGNES, items=J.ITEMS_SUBSTITUTION, graines=Graines(1), compteur=None, plafond_session=1,
                          interdites=J.ETIQUETTES_INTERDITES_TEMOINS, dossier_appel=None, journal={"ancien": [], "v2": []})
        with self.assertRaisesRegex(J.ProtocoleRefuse, "correspondance"):
            J.lot_reel_depuis({"fiches": [{"ident": "x", "contenu": {}, "meta": {"fournisseur": "inconnu"}}]}, "Q", CORRESP)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "fiches >"):
            J.lot_reel_depuis({"fiches": [{"ident": f"x{k}", "contenu": {}, "meta": {"fournisseur": "kimi"}} for k in range(14)]},
                              "Q", CORRESP)


# --- Bradley et Terry, verdicts ----------------------------------------------------------------------------------------------------


class BradleyTerry(unittest.TestCase):
    def test_cas_sain_retrouve_les_forces_et_la_position(self):
        rng = Graines(4).generateur("bt")
        ids = [f"c{k}" for k in range(10)]
        vrai = {i: 0.6 * k - 2.7 for k, i in enumerate(ids)}
        comps = []
        for _ in range(40):
            for a, b in J.graphe_circulant(ids, 4, rng)["paires"]:
                p, s = (a, b) if rng.random() < 0.5 else (b, a)
                comps.append((p, s, bool(rng.random() < 1 / (1 + math.exp(-(vrai[p] - vrai[s] + 0.4))))))
        bt = J.ajuster_bt(ids, comps, ridge=0.01, ridge_position=0.01)
        self.assertTrue(bt["converge"])
        self.assertGreater(J.spearman([vrai[i] for i in ids], [bt["forces"][i] for i in ids]), 0.95)
        self.assertAlmostEqual(bt["position"], 0.4, delta=0.2)
        self.assertAlmostEqual(sum(bt["forces"].values()), 0.0, places=7)

    def test_juge_de_position_pure_forces_egales(self):
        ids = ["a", "b", "c", "d"]
        comps = [(x, y, True) for x in ids for y in ids if x != y]  # deux ordres, la première gagne toujours
        bt = J.ajuster_bt(ids, comps)
        self.assertLess(max(abs(v) for v in bt["forces"].values()), 1e-6)
        self.assertGreater(bt["position"], 1.0)

    def test_artefacts(self):
        bt = J.ajuster_bt(["a", "b"], [])
        self.assertEqual(bt["forces"], {"a": 0.0, "b": 0.0})
        self.assertEqual(bt["sans_comparaison"], ["a", "b"])
        with self.assertRaises(J.ProtocoleRefuse):
            J.ajuster_bt(["a", "b"], [("a", "z", True)])


class Verdicts(unittest.TestCase):
    def test_cas_sain_budget_et_plancher(self):
        forces = {"e1": 3.0, "e2": 2.5, "e3": 2.0, "e4": 1.9, "e5": -1.0, "e6": -2.0, "e7": 0.1, "e8": 0.2, "ab": 1.0, "am": -1.0}
        ev = [f"e{k}" for k in range(1, 9)]
        v = J.verdicts_lot(forces, ev, "ab", "am")
        self.assertEqual(v["k"], 2)
        self.assertEqual(sorted(i for i, x in v["verdicts"].items() if x), ["e1", "e2"])
        self.assertEqual(v["plancher"], 0.0)
        bas = dict(forces, e1=-0.5, e2=-0.4, e3=-0.3, e4=-0.2)
        self.assertEqual(sorted(i for i, x in J.verdicts_lot(bas, ev, "ab", "am")["verdicts"].items() if x), ["e7", "e8"])
        tous_bas = {k: (-5.0 + 0.1 * n if k.startswith("e") else v) for n, (k, v) in enumerate(forces.items())}
        self.assertFalse(any(J.verdicts_lot(tous_bas, ev, "ab", "am")["verdicts"].values()))  # plafond, pas quota

    def test_artefacts_ancres_inversees_egalites_et_ancre_seule(self):
        forces = {"e1": 3.0, "e2": 2.0, "e3": 2.0, "e4": 1.0, "ab": -1.0, "am": 1.0}
        v = J.verdicts_lot(forces, ["e1", "e2", "e3", "e4"], "ab", "am")
        self.assertEqual(v["statut"], "ancres inversées")
        self.assertFalse(any(v["verdicts"].values()))
        egal = J.verdicts_lot({"e1": 2.0, "e2": 2.0, "e3": 2.0, "e4": 0.0, "e5": 0.0}, ["e1", "e2", "e3", "e4", "e5"])
        self.assertFalse(any(egal["verdicts"].values()))  # égalité à la limite du budget : aucune retenue
        with self.assertRaises(J.ProtocoleRefuse):
            J.verdicts_lot(forces, ["e1"], "ab", None)


# --- statistiques ----------------------------------------------------------------------------------------------------------------


class Statistiques(unittest.TestCase):
    def test_aire_et_mann_whitney(self):
        self.assertEqual(J.aire([3, 4], [1, 2]), 1.0)
        self.assertEqual(J.aire([1, 1], [1, 1]), 0.5)
        self.assertIsNone(J.aire([], [1]))
        self.assertEqual(sum(J.loi_u(4, 5)), math.comb(9, 4))
        for m, n in ((6, 6), (10, 10), (8, 12)):
            e = J.loi_u(m, n)
            t = sum(e)
            uc = J.seuil_u(m, n, 0.05)
            self.assertLessEqual(sum(e[uc:]) / t, 0.05)
            self.assertGreater(sum(e[uc - 1:]) / t, 0.05)
        r = J.test_mann_whitney([4, 5, 6], [1, 2, 3])
        self.assertAlmostEqual(r["p"], 1 / 20)
        self.assertEqual(r["methode"], "loi exacte")
        self.assertEqual(J.test_mann_whitney([1, 1, 1], [1, 1, 1])["p"], 1.0)

    def test_delong(self):
        pos, neg = ["p1", "p2", "p3", "p4"], ["n1", "n2", "n3", "n4"]
        bon = {"p1": 4, "p2": 3.5, "p3": 3, "p4": 2.5, "n1": 2, "n2": 1.5, "n3": 1, "n4": 0.5}
        plat = {k: 1.0 for k in bon}
        r = J.delong_difference(bon, plat, pos, neg)
        self.assertAlmostEqual(r["difference"], 0.5)
        self.assertEqual(r["p"], 0.0)
        self.assertIn("variance nulle", r["statut"])
        bruit = {"p1": 4, "p2": 1.2, "p3": 3, "p4": 0.7, "n1": 2, "n2": 1.5, "n3": 1, "n4": 3.2}
        r2 = J.delong_difference(bon, bruit, pos, neg)
        self.assertGreater(r2["difference"], 0)
        self.assertLess(r2["p"], 0.5)
        self.assertEqual(J.delong_difference(bon, bon, pos, neg)["difference"], 0.0)

    def test_kappa_convention_v54_et_artefact_v53(self):
        k = J.kappa_cohen([True, True, False, False], [True, False, False, False])
        self.assertAlmostEqual(k["kappa"], 0.5)
        plafond = J.kappa_cohen([True] * 12, [True] * 12)
        self.assertIsNone(plafond["kappa"])
        self.assertIn("non défini", plafond["statut"])
        self.assertEqual(jc53.kappa_cohen([True] * 12, [True] * 12), 1.0)  # l'artefact de la v53, que la v2 ne reproduit pas
        self.assertAlmostEqual(J.kappa_cohen([True] * 12, [True] * 11 + [False])["kappa"], 0.0)  # le second tour : 12/12 et 11/12

    def test_spearman_et_plafond_binaire(self):
        self.assertAlmostEqual(J.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(J.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertIsNone(J.spearman([1, 1, 1], [1, 2, 3]))
        self.assertAlmostEqual(J.plafond_spearman_binaire((10, 10)), 1 - 2 * 990 / 7980)

    def test_puissance(self):
        nul = J.puissance_aire(10, 10, 0.5, repetitions=4000, graine=1)
        self.assertLessEqual(nul["alpha_exact"], 0.05)
        self.assertLessEqual(nul["puissance_test"], 0.065)
        p = [J.puissance_aire(10, 10, a, repetitions=4000, graine=1)["puissance_test"] for a in (0.65, 0.8, 0.9)]
        self.assertTrue(p[0] < p[1] < p[2], p)
        with self.assertRaises(J.ProtocoleRefuse):
            J.puissance_aire(10, 10, 1.0)


# --- mesures sur des courses à juges scriptés -------------------------------------------------------------------------------------


class Mesures(unittest.TestCase):
    def test_juge_toujours_notable_detecte_au_plafond(self):
        _, mes, lec, _ = course_memo("plafond", "plafond")
        a = mes["ancien"][A["etiquette"]]["1"]
        self.assertTrue(a["au_plafond"])
        self.assertEqual(a["part_notables"], 1.0)
        self.assertIsNone(mes["accord"]["kappa_ancien"]["kappa"])
        self.assertIn("non défini", mes["accord"]["kappa_ancien"]["statut"])
        self.assertTrue(any("trop propre" in x for x in lec["audit"]["motifs"]))
        _, sain, _, _ = course_memo("parfait", "parfait")
        self.assertFalse(sain["ancien"][A["etiquette"]]["1"]["au_plafond"])

    def test_juge_parfait_atteint_la_discrimination(self):
        _, mes, lec, _ = course_memo("indulgent", "parfait")
        v = mes["v2"][A["etiquette"]]["1"]
        self.assertGreaterEqual(v["aire"], 0.85)  # graphe 3-régulier : une bonne fiche peut ne rencontrer que de bonnes fiches
        self.assertLess(v["p_mann_whitney"], 0.01)
        self.assertLessEqual(v["faux_notables"], 0.1)  # une mauvaise fiche qui ne rencontre que des mauvaises peut passer (limite dite)
        self.assertEqual(v["validite"], 1.0)
        self.assertTrue(lec["criteres"]["D1"]["tenu"])
        self.assertEqual(mes["ancien"][A["etiquette"]]["1"]["aire"], 0.5)  # indulgent : l'ancien ne départage rien
        self.assertGreaterEqual(mes["comparaison_a"]["difference"], 0.35)
        self.assertLess(mes["comparaison_a"]["p"], 0.01)
        self.assertLessEqual(mes["v2"][A["etiquette"]]["1"]["part_notables"], 0.3)

    def test_juge_biaise_de_position_mesure(self):
        _, mes, lec, _ = course_memo("position", "parfait")
        pos = mes["position_a"]
        self.assertEqual(pos["part_premier"], 1.0)
        self.assertEqual(pos["taux_bascule"], 1.0)
        self.assertGreater(mes["v2"][A["etiquette"]]["1"]["position_par_lot"]["monde-1"], 1.0)
        self.assertFalse(lec["criteres"]["D5"]["tenu"])
        self.assertLess(mes["v2"][A["etiquette"]]["1"]["aire"], 0.7)
        _, sain, _, _ = course_memo("parfait", "parfait")
        self.assertEqual(sain["position_a"]["part_premier"], 0.5)
        self.assertEqual(sain["position_a"]["taux_bascule"], 0.0)

    def test_kappa_des_paires_pas_gonfle_par_la_position(self):
        _, mes, _, _ = course_memo("position", "position")
        self.assertAlmostEqual(mes["accord"]["kappa_paires_v2"]["kappa"], 0.0, delta=0.05)
        _, sain, _, _ = course_memo("parfait", "parfait")
        self.assertEqual(sain["accord"]["kappa_paires_v2"]["kappa"], 1.0)

    def test_juge_verbeux_mesure(self):
        _, mes, lec, _ = course_memo("verbeux", "parfait")
        self.assertGreater(mes["classes"]["rang_v2_a1"]["verbeuse"], 0.8)
        cle = next(k for k in lec["predictions"] if k.startswith("P9"))
        self.assertFalse(lec["predictions"][cle]["tenue"])

    def test_artefacts_citations_fausses_ou_reponses_illisibles_arretent(self):
        for strategie in ("citations_fausses", "illisible"):
            with self.subTest(strategie=strategie), self.assertRaises(J.ArretValidite) as e:
                course(strategie, "parfait")
            self.assertEqual(len(e.exception.partiel["ancien"]) + len(e.exception.partiel["v2"]), 20 if strategie == "illisible" else 40)

    def test_lot_reel_decrit_seulement(self):
        _, mes, lec, _ = course("indulgent", "parfait", avec_reel=True)
        r = mes["reel"]
        self.assertEqual(r["fiches"], 12)
        self.assertEqual(r[B["etiquette"]]["ancien_joues"], 12)
        self.assertEqual(r[A["etiquette"]]["ancien_joues"], 6)  # les six fiches d'auteur kimi ; la fusion (kimi et argon) exclue
        self.assertIn("sans ancre", r[B["etiquette"]]["v2_statut"])
        self.assertEqual(lec["issue"], "I1")


# --- lecture gelée --------------------------------------------------------------------------------------------------------------


class Lecture(unittest.TestCase):
    def test_issues_atteignables(self):
        self.assertEqual(course_memo("indulgent", "parfait")[2]["issue"], "I1")
        self.assertEqual(course_memo("parfait", "parfait")[2]["issue"], "I2")
        self.assertEqual(course_memo("plafond", "plafond")[2]["issue"], "I3")
        _, mes, _, _ = course_memo("indulgent", "parfait")
        m = copy.deepcopy(mes)
        m["v2"][A["etiquette"]]["2"]["aire"] = 0.6
        self.assertEqual(J.lire_validation(m)["issue"], "I4")
        m = copy.deepcopy(mes)
        m["completude"][f"decisive-a/{A['etiquette']}"]["complet"] = False
        self.assertEqual(J.lire_validation(m)["issue"], "I0")
        m = copy.deepcopy(mes)
        m["completude"][f"decisive-b/{B['etiquette']}"]["complet"] = False
        lec = J.lire_validation(m)
        self.assertEqual(lec["issue"], "I1")
        self.assertIsNone(lec["criteres"]["D6"]["tenu"])
        self.assertTrue(lec["reserves"])

    def test_audit_symetrique(self):
        beau = course("indulgent", "parfait", graine=12)[2]["audit"]  # tirage où l'aire v2 atteint 1
        decevant = course_memo("plafond", "plafond")[2]["audit"]
        self.assertTrue(beau["declenche"] and decevant["declenche"])
        self.assertTrue(any(x.startswith("trop beau : aire v2") for x in beau["motifs"]))
        self.assertTrue(any(x.startswith("décevant : aire v2") for x in decevant["motifs"]))
        self.assertEqual(beau["verifications"], decevant["verifications"])

    def test_seuils_du_texte_egaux_au_code(self):
        self.assertEqual(lanceur.PLAN_FIXE["seuils"], ", ".join(f"{k}={v}" for k, v in J.SEUILS_LECTURE_V1.items()))


# --- compteur, arrêts --------------------------------------------------------------------------------------------------------------


class Horloge:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        self.t += 1.0
        return self.t


class Compteur(unittest.TestCase):
    def test_cas_sain_et_artefacts_du_compteur(self):
        c = J.Compteur(1.0, 100, Horloge(), {"x": 0.1})
        self.assertEqual(c.budget_appel(0.5), 0.5)
        for _ in range(3):
            c.noter("x", 0.3)
        self.assertAlmostEqual(c.prix("x"), 0.3)
        self.assertAlmostEqual(c.budget_appel(0.5), 0.1)
        with self.assertRaises(J.ArretDevis):
            c.exiger_projection({"x": 1}, "essai")
        c.noter("x", 0.1)
        with self.assertRaises(J.ArretDevis):
            c.budget_appel(0.5)
        with self.assertRaises(J.ArretDevis):
            J.Compteur(1.0, 100, Horloge(), {"x": 0.1}).noter("x", float("nan"))
        h = Horloge()
        d = J.Compteur(1.0, 5, h, {"x": 0.1})
        h.t = 10.0
        with self.assertRaises(J.ArretDuree):
            d.verifier_duree()

    def test_arret_par_projection(self):
        """Plan décisif au-dessus du plafond aux prix du plan : arrêt avant tout appel. Prix observé du juge B au-dessus du prix du
        plan : arrêt dès que la projection au prix observé (3 appels) dépasse le reste, avant la suite des étapes de B."""
        with self.assertRaises(J.ArretDevis) as e:
            course("parfait", "parfait", couts=(0.062, 0.25), plafond=15.0)
        self.assertEqual(len(e.exception.partiel["ancien"]) + len(e.exception.partiel["v2"]), 0)
        with self.assertRaises(J.ArretDevis) as e:
            course("parfait", "parfait", couts=(0.062, 0.6), plafond=21.0)
        partiel = e.exception.partiel
        par_juge = {}
        for x in partiel["ancien"] + partiel["v2"]:
            par_juge[x["juge"]] = par_juge.get(x["juge"], 0) + 1
        self.assertEqual(par_juge, {A["etiquette"]: 164, B["etiquette"]: 10})
        self.assertIn("projection", str(e.exception))

    def test_phase_descriptive_non_jouee_si_le_reste_ne_suffit_pas(self):
        journal, _, lec, _ = course("indulgent", "parfait", avec_reel=True, couts=(0.062, 0.25), plafond=21.0)
        self.assertEqual([p["phase"] for p in journal["phases"] if not p["jouee"]], ["reel-ancien", "reel-v2"])
        self.assertEqual(lec["issue"], "I1")

    def test_artefact_erreur_d_un_relais_arrete_avec_le_journal(self):
        class RelaisEnPanne(J.AdaptateurScripte):
            def lancer(self, *a, **kw):
                if self.appels >= 3:
                    raise OSError("relais injoignable")
                return super().lancer(*a, **kw)
        oracle = J.oracle_depuis(MATERIAUX)
        ad = {A["fournisseur"]: RelaisEnPanne("parfait", oracle), B["fournisseur"]: J.AdaptateurScripte("parfait", oracle)}
        with self.assertRaisesRegex(J.ArretJuges, "relais injoignable") as e:
            course("parfait", "parfait", adaptateurs=ad)
        self.assertEqual(len(e.exception.partiel["ancien"]), 3)

    def test_lot_reel_sous_forme_de_liste(self):
        objet, _ = J.lot_reel_substitution(3)
        self.assertEqual(len(J.lot_reel_depuis(objet["fiches"], "Q", CORRESP)["fiches"]), 12)

    def test_artefact_modele_servi_different(self):
        with self.assertRaises(J.ArretModeleServi):
            course("parfait", "parfait", modele_servi_a="gemini-4-argon-lite")
        journal, _, _, _ = course("parfait", "parfait", modele_servi_a="gemini-4-argon-20261101")
        self.assertTrue(journal["ancien"])


# --- lanceur ------------------------------------------------------------------------------------------------------------------------


class LanceurABlanc(unittest.TestCase):
    def test_a_blanc_de_bout_en_bout(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7"]), 0)
            self.assertEqual(sorted(os.listdir(d)), ["s"])
            fichiers = sorted(os.listdir(sortie))
            for nom in lanceur.SORTIES.values():
                self.assertIn(nom, fichiers)
                self.assertIn(nom + ".sha256", fichiers)
            with open(os.path.join(sortie, lanceur.SORTIES["lecture"]), encoding="utf-8") as f:
                lec = json.load(f)
            self.assertEqual(lec["issue"], "I1")
            self.assertFalse(lec["partielle"])
            with open(os.path.join(sortie, lanceur.SORTIES["manifeste"]), encoding="utf-8") as f:
                m = json.load(f)
            self.assertEqual(sorted(m["code_sha256"]), sorted(lanceur.FICHIERS_GELES))
            self.assertEqual(m["materiaux_empreinte"], MATERIAUX["empreinte"])

    def test_refus_avant_toute_ecriture(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            for argv in ([sortie, "--a-blanc", "--graine", str(2 ** 64)], [sortie, "--a-blanc"],
                         [sortie, "--a-blanc", "--graine", "7", "--strategie-a", "inconnue"],
                         [sortie, "--a-blanc", "--graine", "7", "--go", "GO-2026-11-02-01"]):
                with self.subTest(argv=argv[1:]):
                    self.assertEqual(lanceur.principal(argv), 2)
                    self.assertFalse(os.path.exists(sortie))
            os.makedirs(sortie)
            open(os.path.join(sortie, "f"), "w").close()
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7"]), 2)

    def test_arret_ecrit_un_journal_partiel_scelle(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--plafond-usd", "5"]), 3)
            with open(os.path.join(sortie, lanceur.SORTIES["lecture"]), encoding="utf-8") as f:
                lec = json.load(f)
            self.assertTrue(lec["partielle"])
            self.assertEqual(lec["issue"], "I0")
            self.assertTrue(os.path.isfile(os.path.join(sortie, lanceur.SORTIES["journal"] + ".sha256")))


def texte_preenregistrement(*, conf_sha, go="GO-2026-11-02-09", marqueur="", empreintes=None, plafond="30", parts=("12", "18"),
                            consigne=None, materiaux_sha=None, juge_b="etiquette=juge-b, fournisseur=astra, modele=gpt-6-astra, famille=gpt, "
                                                                   "prix_usd=0.25, secondes=10-120", sans=None, en_plus="", remplace=None):
    lignes = {"juge_a": "etiquette=juge-a, fournisseur=argon, modele=gemini-4-argon, famille=gemini, prix_usd=0.062, secondes=8-40",
              "juge_b": juge_b, "correspondance_auteurs": "kimi=kimi, argon=gemini", "graine_materiaux": str(J.GRAINE_MATERIAUX_V1),
              "materiaux_sha256": materiaux_sha or MATERIAUX["empreinte"],
              "consigne_paire_sha256": consigne or J.EMPREINTE_CONSIGNE_PAIRE_V2, "piece_consigne_ancienne": "consigne_juge",
              "piece_question": "question_course_2", "piece_lot_reel": "lot_reel_juges_idees_v2", "plafond_usd": plafond,
              "plafond_juge_a_usd": parts[0], "plafond_juge_b_usd": parts[1], "duree_max_h": "6", "configuration_sha256": conf_sha,
              "go": go}
    lignes.update(lanceur.PLAN_FIXE)
    lignes.update(remplace or {})
    if sans:
        lignes.pop(sans)
    if empreintes is None:
        empreintes = {r: sha256_fichier(os.path.join(RACINE, r)) for r in lanceur.FICHIERS_GELES}
    bloc_e = "\n".join(f"{h}  {r}" for r, h in sorted(empreintes.items()))
    bloc_p = "\n".join(f"{k}: {v}" for k, v in lignes.items()) + en_plus
    return (f"# Préenregistrement d'essai (aucune valeur réelle)\n\n{marqueur}\n\n{lanceur.DEBUT_EMPREINTES}\n{bloc_e}\n"
            f"{lanceur.FIN_EMPREINTES}\n\n{lanceur.DEBUT_PLAN}\n{bloc_p}\n{lanceur.FIN_PLAN}\n")


class LanceurCheminReel(unittest.TestCase):
    """Le mode réel jusqu'aux relais, avec des commandes externes factices (scripts locaux) : aucune clé, aucun réseau."""

    def setUp(self):
        import aides_v54 as A54
        import aides_v56 as A56
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        self.env = unittest.mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", os.defpath), "HOME": self.tmp}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.prereg_dir = os.path.join(self.tmp, "prereg")
        os.makedirs(self.prereg_dir)
        p = unittest.mock.patch.object(lanceur, "DOSSIER_PREREG", self.prereg_dir)
        p.start()
        self.addCleanup(p.stop)
        conf = A56.configuration(self.tmp)
        objet, _ = J.lot_reel_substitution(3)
        conf["pieces"]["question_course_2"] = A56.ecrire(os.path.join(self.tmp, "p", "question.md"), J.QUESTION_SUBSTITUTION)
        conf["pieces"]["lot_reel_juges_idees_v2"] = A56.ecrire(os.path.join(self.tmp, "p", "lot.json"), json.dumps(objet, ensure_ascii=False))
        items = {"texte": "```json\n" + json.dumps({"items": {k: True for k in conf["items_juge"]}}) + "\n```", "cout_usd": 0.001}
        conf["fournisseurs"] = {
            "argon": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                      "commande": A56.commande_factice(self.tmp, "argon", dict(items, modele_servi="gemini-4-argon"))
                      + ["--registre", "{REGISTRE}", "--plafond-cumule-usd", "1"]},
            "astra": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                      "commande": A56.commande_factice(self.tmp, "astra", dict(items, modele_servi="gpt-6-astra"))}}
        self.conf = conf
        self.chemin_conf = os.path.join(self.tmp, "conf.json")
        with open(self.chemin_conf, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        self.prereg = os.path.join(self.prereg_dir, "preenregistrement-juges-idees-v2-v1.md")
        ecrire_scelle(self.prereg, texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf)))
        self.registre = A54.registre_go(self.tmp, A54.ligne_go("GO-2026-11-02-09", "30 USD", perimetre="juges v2"),
                                        A54.ligne_go("GO-2026-11-02-10", "30 USD", perimetre="juges v2"),
                                        A54.ligne_go("GO-2026-11-02-11", "25 USD", perimetre="juges v2"))
        self.sortie = os.path.join(self.tmp, "sortie")

    def argv(self, *plus, prereg=None, conf=None, go="GO-2026-11-02-09"):
        return [self.sortie, "--preenregistrement", prereg or self.prereg, "--configuration", conf or self.chemin_conf, "--moteur", "reel",
                "--confirmer-moteur-reel", "--registre-go", self.registre, "--go", go, *plus]

    def ecrire_prereg(self, nom, texte, sceller=True):
        chemin = os.path.join(self.prereg_dir, nom)
        if sceller:
            ecrire_scelle(chemin, texte)
        else:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        return chemin

    def test_cas_sain_verifier_seulement_aucune_ecriture(self):
        self.assertEqual(lanceur.principal(self.argv("--verifier-seulement")), 0)
        self.assertFalse(os.path.exists(self.sortie))

    def test_cas_sain_course_reelle_factice_arretee_par_la_garde_de_validite(self):
        """Les commandes factices rendent toujours un bloc d'items : l'ancien protocole est lu, les comparaisons v2 sont nulles
        (aucun bloc « comparaison ») ; la garde de validité arrête la course après 20 comparaisons (code 3, journal scellé)."""
        self.assertEqual(lanceur.principal(self.argv()), 3)
        with open(os.path.join(self.sortie, lanceur.SORTIES["journal"]), encoding="utf-8") as f:
            journal = json.load(f)
        self.assertEqual(len(journal["ancien"]), 20)
        self.assertTrue(all(e["valide"] for e in journal["ancien"]))
        self.assertEqual(len(journal["v2"]), 20)
        self.assertIn("ArretValidite", journal["arret"])
        self.assertTrue(all(e["modele_servi"] == "gemini-4-argon" for e in journal["ancien"]))
        with open(os.path.join(self.sortie, lanceur.SORTIES["manifeste"]), encoding="utf-8") as f:
            m = json.load(f)
        self.addCleanup(__import__("shutil").rmtree, m["dossier_des_sessions"], True)
        self.assertEqual(m["preenregistrement"]["sha256"], sha256_fichier(self.prereg))
        self.assertEqual(m["entropie_racine"], str(int(sha256_fichier(self.prereg), 16)))
        self.assertEqual({k: v["plafond_usd"] for k, v in m["configuration"]["accuses_plafond"].items()}, {"juge-a": 12.0, "juge-b": 18.0})

    def test_artefacts_du_chemin_reel(self):
        sha = sha256_fichier(self.chemin_conf)
        autre_conf = os.path.join(self.tmp, "conf-autre.json")
        with open(autre_conf, "w", encoding="utf-8") as f:
            json.dump(dict(self.conf, note="autre"), f)
        faux_code = {r: sha256_fichier(os.path.join(RACINE, r)) for r in lanceur.FICHIERS_GELES}
        faux_code["pole/juges_idees_v2.py"] = "0" * 64
        moins_un = {r: h for r, h in faux_code.items() if r != "pole/outils.py"}
        moins_un["pole/juges_idees_v2.py"] = sha256_fichier(os.path.join(RACINE, "pole/juges_idees_v2.py"))
        juge_claude = "etiquette=juge-b, fournisseur=opus, modele=claude-opus-5-5, famille=claude, prix_usd=0.25, secondes=10-120"
        juge_sans_relais = "etiquette=juge-b, fournisseur=autre, modele=gpt-6-astra, famille=gpt, prix_usd=0.25, secondes=10-120"
        cas = {
            "brouillon": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-brouillon1.md",
                                                              texte_preenregistrement(conf_sha=sha))), "pas"),
            "non scellé": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v2.md",
                                                               texte_preenregistrement(conf_sha=sha), sceller=False)), "non scellé"),
            "marqueur restant": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v3.md",
                                                                     texte_preenregistrement(conf_sha=sha, marqueur="GO : <<GO>>"))), "marqueur"),
            "code différent": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v4.md",
                                                                   texte_preenregistrement(conf_sha=sha, empreintes=faux_code))), "code différent"),
            "fermeture incomplète": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v5.md",
                                                                         texte_preenregistrement(conf_sha=sha, empreintes=moins_un))), "fermeture"),
            "clé de plan manquante": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v6.md",
                                                                          texte_preenregistrement(conf_sha=sha, sans="duree_max_h"))), "clés"),
            "plafond au-dessus de 30": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v7.md",
                                                                            texte_preenregistrement(conf_sha=sha, plafond="31"))), "hors de ]0"),
            "valeur fixe différente du code": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v14.md", texte_preenregistrement(conf_sha=sha, remplace={"degre": "4"}))), "le code gelé dit"),
            "parts au-dessus du plafond": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v8.md",
                                                                               texte_preenregistrement(conf_sha=sha, parts=("15", "16")))), "parts"),
            "part sous le devis": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v9.md",
                                                                       texte_preenregistrement(conf_sha=sha, parts=("20", "10")))), "devis"),
            "consigne v2 autre": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v10.md",
                                                                      texte_preenregistrement(conf_sha=sha, consigne="e" * 64))), "consigne"),
            "matériaux autres": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v11.md",
                                                                     texte_preenregistrement(conf_sha=sha, materiaux_sha="f" * 64))), "matériaux"),
            "juge de la famille des gabarits": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v12.md", texte_preenregistrement(conf_sha=sha, juge_b=juge_claude))), "famille"),
            "relais du juge absent": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v13.md", texte_preenregistrement(conf_sha=sha, juge_b=juge_sans_relais))), "relais"),
            "autre configuration": (self.argv(conf=autre_conf), "empreinte"),
            "GO autre que celui du texte": (self.argv(go="GO-2026-11-02-10"), "nomme"),
            "option de plan en réel": (self.argv("--plafond-usd", "10"), "options refusées"),
            "graine en réel": (self.argv("--graine", "7"), "graine"),
        }
        for nom, (argv, motif) in cas.items():
            with self.subTest(cas=nom), unittest.mock.patch("sys.stderr", new_callable=__import__("io").StringIO) as err:
                self.assertEqual(lanceur.principal(argv + ["--verifier-seulement"]), 2)
                self.assertIn(motif, err.getvalue())
                self.assertFalse(os.path.exists(self.sortie))

    def test_artefacts_go_et_environnement(self):
        texte = texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf), go="GO-2026-11-02-11")
        p = self.ecrire_prereg("preenregistrement-juges-idees-v2-v20.md", texte)
        with unittest.mock.patch("sys.stderr", new_callable=__import__("io").StringIO) as err:
            self.assertEqual(lanceur.principal(self.argv("--verifier-seulement", prereg=p, go="GO-2026-11-02-11")), 2)
        self.assertIn("pas exactement", err.getvalue())
        with unittest.mock.patch.dict(os.environ, {"GH_TOKEN": "x"}), \
                unittest.mock.patch("sys.stderr", new_callable=__import__("io").StringIO) as err:
            self.assertEqual(lanceur.principal(self.argv("--verifier-seulement")), 2)
        self.assertIn("les relais tiennent les clés", err.getvalue())  # la garde du lanceur, avant celle des adaptateurs
        self.assertFalse(os.path.exists(self.sortie))


class Fermeture(unittest.TestCase):
    def test_fichiers_geles_egaux_a_la_fermeture(self):
        """Le code que le chemin réel importe (mesuré dans un processus neuf) est exactement `FICHIERS_GELES`."""
        script = (
            "import importlib.util, json, os, sys\nR = os.path.realpath(sys.argv[1])\nvus = set()\n"
            "def crochet(e, a):\n    if e == 'open' and a and isinstance(a[0], str) and a[0].endswith(('.py', '.pyc')):\n"
            "        vus.add(os.path.realpath(a[0]))\nsys.addaudithook(crochet)\nsys.path.insert(0, R)\n"
            "s = importlib.util.spec_from_file_location('l', os.path.join(R, 'demonstrations', 'validation_juges_idees_v2.py'))\n"
            "m = importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\nm.charger_ideation_v8()\n"
            "import pole.relais, pole.configuration_v56, pole.configuration_v53\n"
            "f = {os.path.realpath(getattr(x, '__file__', '') or '') for x in list(sys.modules.values())} | vus\n"
            "def source(p):\n    if p.endswith('.pyc') and os.path.basename(os.path.dirname(p)) == '__pycache__':\n"
            "        p = os.path.join(os.path.dirname(os.path.dirname(p)), os.path.basename(p).split('.')[0] + '.py')\n    return p\n"
            "print(json.dumps(sorted({os.path.relpath(source(p), R) for p in f if p.startswith(R + os.sep)})))\n")
        sortie = subprocess.run([sys.executable, "-I", "-B", "-c", script, RACINE], capture_output=True, text=True, check=True)
        self.assertEqual(sorted(json.loads(sortie.stdout)), sorted(lanceur.FICHIERS_GELES))
        self.assertIn("pole/juges_idees_v2.py", lanceur.FICHIERS_GELES)


if __name__ == "__main__":
    unittest.main()
