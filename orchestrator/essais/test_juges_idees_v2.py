"""Essais de l'étage des juges d'idéation v2 (`pole/juges_idees_v2.py`) et de son lanceur de validation
(`demonstrations/validation_juges_idees_v2.py`), brouillon 2 — R5 : chaque garde sur un cas sain et sur un artefact. Hors ligne :
juges scriptés, relais scriptés en panne, horloge virtuelle, commandes externes factices (scripts Python locaux, aucun réseau),
aucune clé, aucun appel de modèle.

  python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py     (depuis le dossier orchestrator)
"""

import copy
import importlib.util
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
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
from pole.adaptateurs import Adaptateur, Resultat  # noqa: E402
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
_MATERIAUX_B1 = {}


def materiaux():
    return copy.deepcopy(MATERIAUX)


def materiaux_brouillon1():
    if "m" not in _MATERIAUX_B1:
        _MATERIAUX_B1["m"] = J.construire_materiaux(jeu="mondes-brouillon1")
    return copy.deepcopy(_MATERIAUX_B1["m"])


def resceller(m):
    m["empreinte"] = empreinte_objet({k: v for k, v in m.items() if k != "empreinte"})
    return m


def lot_reel(graine=3):
    objet, qualites = J.lot_reel_substitution(graine)
    return J.lot_reel_depuis(objet, J.QUESTION_SUBSTITUTION, CORRESP), qualites


def course(strategie_a, strategie_b, *, graine=11, avec_reel=False, couts=(0.0, 0.0), plafond=60.0, parts=None, duree=48 * 3600.0,
           adaptateurs=None, pannes=(None, None), **kw):
    """Une course complète à juges scriptés, horloge virtuelle (aucune attente réelle) ; rend (journal, mesures, lecture,
    étapes) ou lève l'arrêt de la course."""
    m = MATERIAUX
    reel, qualites = lot_reel() if avec_reel else (None, None)
    g = Graines(graine)
    etapes, _ = J.etapes_v2(m, A, B, g, lot_reel=reel)
    oracle = J.oracle_depuis(m, reel, qualites)
    h = J.HorlogeVirtuelle()
    if adaptateurs is None:
        bases = (J.AdaptateurScripte(strategie_a, oracle, graine=graine, cout_par_appel_usd=couts[0], horloge=h, secondes_par_appel=8.0, **kw),
                 J.AdaptateurScripte(strategie_b, oracle, graine=graine + 1, cout_par_appel_usd=couts[1], horloge=h,
                                     secondes_par_appel=30.0, **kw))
        adaptateurs = {j["fournisseur"]: (J.AdaptateurPanneScripte(b, p, horloge=h, secondes_par_echec=5.0) if p else b)
                       for j, b, p in ((A, bases[0], pannes[0]), (B, bases[1], pannes[1]))}
    parts = parts or {A["etiquette"]: plafond * 0.4, B["etiquette"]: plafond * 0.6}
    c = J.Compteur(plafond, duree, h, {A["etiquette"]: A["prix_usd"], B["etiquette"]: B["prix_usd"]}, parts=parts, dormir=h.avancer)
    journal = J.executer_validation(etapes, materiaux=m, juges={A["etiquette"]: A, B["etiquette"]: B}, adaptateurs=adaptateurs,
                                    consignes=CONSIGNES, items=J.ITEMS_SUBSTITUTION, graines=g, compteur=c, plafond_session=1.0,
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


# --- matériaux, contrôles de forme et de diagnosticité ----------------------------------------------------------------------------


class Materiaux(unittest.TestCase):
    def test_cas_sain_deterministe_composition_et_gardes(self):
        self.assertEqual(J.construire_materiaux()["empreinte"], MATERIAUX["empreinte"])
        self.assertEqual(MATERIAUX["jeu_de_mondes"], "mondes-v2")
        self.assertEqual(J.verifier_materiaux(MATERIAUX), [])
        controles = J.exiger_materiaux(materiaux(), MATERIAUX["empreinte"])
        self.assertTrue(controles["forme"]["conforme"])
        self.assertTrue(controles["diagnosticite"]["conforme"])
        self.assertEqual([len(l["fiches"]) for l in MATERIAUX["lots"]], [12, 12, 12])
        ev = [f for l in MATERIAUX["lots"] for f in l["fiches"] if f["role"] == "evaluation"]
        classes = {}
        for f in ev:
            classes[f["classe"]] = classes.get(f["classe"], 0) + 1
        self.assertEqual(classes, {"vraie_neuve": 15, "fausse_redigee": 7, "copie_archive": 3, "signe_contraire": 3,
                                   "tautologie": 1, "verbeuse": 1})
        for l in MATERIAUX["lots"]:
            self.assertEqual(sorted(f["role"] for f in l["fiches"] if f["role"] != "evaluation"), ["ancre_bonne", "ancre_mauvaise"])
            self.assertTrue(J.dossier_a_preuves(l["dossier"]))

    def test_sens_des_lois_et_champ_signe(self):
        for l in MATERIAUX["lots"]:
            for f in l["fiches"]:
                loi = f["loi"]
                if loi["type"] in ("monotone", "signe_contraire"):
                    self.assertEqual(f["contenu"]["signe"], loi["signe_prediction"], f["ident"])
                    self.assertEqual(loi["signe_prediction"] != loi["signe"], f["classe"] == "signe_contraire", f["ident"])
        sens = {q: sorted(f["sens"] or "0" for l in MATERIAUX["lots"] for f in l["fiches"] if f["role"] == "evaluation" and f["qualite"] == q)
                for q in (0, 1)}
        self.assertEqual(sens[1].count("-"), 3)
        self.assertEqual(sens[0].count("-"), 3)

    def test_artefact_materiaux_alteres_ou_autre_empreinte(self):
        m = materiaux()
        m["lots"][0]["fiches"][0]["contenu"]["hypothese"] += " Ajout."
        with self.assertRaisesRegex(J.ProtocoleRefuse, "empreinte interne fausse"):
            J.exiger_materiaux(m)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "le texte scellé gèle"):
            J.exiger_materiaux(resceller(m), MATERIAUX["empreinte"])
        with self.assertRaisesRegex(J.ProtocoleRefuse, "graine des matériaux"):
            J.construire_materiaux(-1)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "jeu de mondes inconnu"):
            J.construire_materiaux(jeu="mondes-v9")

    def test_artefact_verite_non_etablie(self):
        """Table altérée : la caractéristique sans effet d'une loi fausse montre l'effet affirmé → vérité connue perdue ; chiffres
        affirmés d'une bonne loi changés ; loi fausse à l'écart affirmé trop petit ; champ « signe » contraire à la prédiction."""
        m = materiaux()
        lot = m["lots"][0]
        lot["tables"]["table1"]["langue"][1]["taux"] = lot["tables"]["table1"]["langue"][0]["taux"] + 7.0
        self.assertTrue(any("langue" in e for e in J.verifier_materiaux(m)))
        with self.assertRaisesRegex(J.ProtocoleRefuse, "vérité connue non établie"):
            J.exiger_materiaux(resceller(m))
        m2 = materiaux()
        bonne = next(f for f in m2["lots"][1]["fiches"] if f["classe"] == "vraie_neuve" and f["loi"]["type"] == "monotone")
        bonne["loi"]["affirme"] = [bonne["loi"]["affirme"][0] + 5, bonne["loi"]["affirme"][1]]
        self.assertTrue(any("chiffres affirmés" in e for e in J.verifier_materiaux(m2)))
        m3 = materiaux()
        fausse = next(f for f in m3["lots"][0]["fiches"] if f["classe"] == "fausse_redigee" and f["loi"]["type"] == "binaire")
        fausse["loi"]["affirme"] = [fausse["loi"]["affirme"][1] + 1, fausse["loi"]["affirme"][1]]
        self.assertTrue(any("loi fausse non contredite" in e for e in J.verifier_materiaux(m3)))
        m4 = materiaux()
        sc = next(f for f in m4["lots"][2]["fiches"] if f["classe"] == "signe_contraire")
        sc["contenu"]["signe"] = sc["loi"]["signe"]
        self.assertTrue(any("champ « signe »" in e for e in J.verifier_materiaux(m4)))
        m5 = materiaux()
        m5["jeu_de_mondes"] = "inconnu"
        self.assertTrue(J.verifier_materiaux(m5))
        m6 = materiaux()
        graduee = next(f for f in m6["lots"][2]["fiches"] if f["classe"] == "fausse_redigee" and f["loi"]["type"] == "monotone")
        graduee["loi"]["affirme"] = [graduee["loi"]["affirme"][0], graduee["loi"]["affirme"][0] + 1]
        self.assertTrue(any(graduee["ident"] in e and "loi fausse non contredite" in e for e in J.verifier_materiaux(m6)))
        m7 = materiaux()
        sc = next(f for f in m7["lots"][1]["fiches"] if f["classe"] == "signe_contraire")
        sc["loi"]["signe_prediction"] = sc["loi"]["signe"]
        sc["contenu"]["signe"] = sc["loi"]["signe"]
        self.assertTrue(any("prédiction du même signe" in e for e in J.verifier_materiaux(m7)))

    def test_artefacts_forme(self):
        """Les matériaux du brouillon 1 (gabarit, caractéristique binaire et a priori séparent les classes) sont refusés par le
        contrôle de forme étendu ; un indice de longueur favorable aux bons témoins aussi."""
        b1 = J.controle_forme(materiaux_brouillon1())
        self.assertFalse(b1["conforme"])
        self.assertGreater(b1["aires"]["gabarit_gradue"], 0.65)
        self.assertGreater(b1["aires"]["a_priori_plausible"], 0.65)
        self.assertLess(b1["aires"]["caracteristique_binaire"], 0.35)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "indice de forme"):
            J.exiger_materiaux(materiaux_brouillon1(), diagnosticite=False)
        m = materiaux()
        for l in m["lots"]:
            for f in l["fiches"]:
                if f["classe"] == "vraie_neuve":
                    f["contenu"]["hypothese"] += " Précision : " + "détail " * 200 + "1234567890" * 5
        self.assertFalse(J.controle_forme(m)["conforme"])
        with self.assertRaisesRegex(J.ProtocoleRefuse, "indice de forme"):
            J.exiger_materiaux(resceller(m), diagnosticite=False)
        court = materiaux()  # bons témoins raccourcis : l'indice de longueur favorise les mauvais (aire sous 0,35)
        for l in court["lots"]:
            for f in l["fiches"]:
                if f["classe"] == "vraie_neuve":
                    f["contenu"]["metrique"] = "écart, en points"
                    f["contenu"]["test_de_mort"] = "Abandon sous 1 point."
        aires = J.controle_forme(court)
        self.assertLess(aires["aires"]["longueur"], 0.35)
        self.assertFalse(aires["conforme"])


    def test_artefact_etiquette_interdite_dans_un_temoin(self):
        m = materiaux()
        m["lots"][1]["fiches"][3]["contenu"]["titre"] = "Un témoin de la loi"
        with self.assertRaisesRegex(J.ProtocoleRefuse, "étiquette interdite"):
            J.exiger_materiaux(resceller(m), diagnosticite=False)

    def test_bons_temoins_hors_des_lois_etablies_et_redites_dessus(self):
        specs = {s["nom"]: s for s in J.MONDES_V2}
        for l in MATERIAUX["lots"]:
            for f in l["fiches"]:
                if f["loi"]["type"] in ("monotone", "binaire", "categorie", "signe_contraire"):
                    role = J._caracteristique(specs[l["nom"]], f["loi"]["caracteristique"])["role"]
                    self.assertEqual(role == "etablie", f["classe"] == "copie_archive", f["ident"])


class Diagnosticite(unittest.TestCase):
    def test_artefact_diagnosticite_brouillon1(self):
        """Contrôle de diagnosticité : sur les matériaux du brouillon 1, des juges scriptés qui ne lisent pas les tables tiennent
        D1 (forme) et D1b (dossier sans tables) : refus ; sur les matériaux de ce texte, aucun ne passe."""
        d = J.controle_diagnosticite(materiaux_brouillon1())
        self.assertFalse(d["conforme"])
        self.assertGreater(d["forme"]["a_priori+gabarit+sens"]["d1_tenus"], J.DIAGNOSTICITE_D1_MAX)
        self.assertGreater(d["dossier_sans_tables"]["d1b_tenus"], J.DIAGNOSTICITE_D1B_MAX)
        self.assertTrue(any(x.startswith("juge de forme") for x in d["motifs"]), d["motifs"])
        self.assertTrue(any("dossier sans tables" in x for x in d["motifs"]), d["motifs"])
        sain = J.controle_diagnosticite(MATERIAUX)
        self.assertTrue(sain["conforme"])
        self.assertTrue(all(v["d1_tenus"] <= J.DIAGNOSTICITE_D1_MAX for v in sain["forme"].values()))
        self.assertLessEqual(sain["dossier_sans_tables"]["d1b_tenus"], J.DIAGNOSTICITE_D1B_MAX)
        forme_ok = {"conforme": True, "aires": {}, "seuil": J.SEUIL_FORME}
        with unittest.mock.patch.object(J, "controle_forme", lambda m: forme_ok), \
                self.assertRaisesRegex(J.ProtocoleRefuse, "ne lit pas les tables"):
            J.exiger_materiaux(materiaux_brouillon1())


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
        for interdit in (f1["ident"], f2["ident"], "vraie_neuve", "fausse_redigee", "evaluation", "qualite", "plausible", "gradue"):
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

    def test_artefact_etiquette_dans_une_entree_pendant_la_course(self):
        m = materiaux()
        m["lots"][0]["fiches"][0]["contenu"]["titre"] = "Une ancre glissée dans la fiche"
        etape = {"phase": "decisive-a", "protocole": "v2", "lot": "monde-1", "juge": A["etiquette"], "tirage": 1,
                 "appels": [("monde-1-01", "monde-1-07")]}
        h = J.HorlogeVirtuelle()
        c = J.Compteur(10.0, 1e6, h, {A["etiquette"]: 0.0}, dormir=h.avancer)
        with self.assertRaisesRegex(J.ArretJuges, "étiquette interdite"):
            J.jouer_etape(etape, lots={l["nom"]: l for l in m["lots"]}, juges={A["etiquette"]: A},
                          adaptateurs={A["fournisseur"]: J.AdaptateurScripte("parfait", {})}, consignes=CONSIGNES,
                          items=J.ITEMS_SUBSTITUTION, graines=Graines(1), compteur=c, plafond_session=1.0,
                          interdites=J.ETIQUETTES_INTERDITES_TEMOINS, dossier_appel=lambda j, e: os.devnull, journal=J.journal_vide())


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
        f = fiche("c", hypothese="Les épisodes que le moniteur classe « suspects » reçoivent l’alerte plus souvent.")
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

    def test_cas_sain_etapes_v2(self):
        reel, _ = lot_reel()
        etapes, graphes = J.etapes_v2(MATERIAUX, A, B, Graines(9), lot_reel=reel)
        self.assertEqual([e["phase"] for e in etapes], sorted([e["phase"] for e in etapes], key=J.PHASES_V2.index))
        n = {}
        for e in etapes:
            n[(e["phase"], e["juge"], e["protocole"])] = n.get((e["phase"], e["juge"], e["protocole"]), 0) + J.nombre_appels(e)
        self.assertEqual(n[("decisive-a", A["etiquette"], "ancien")], 30)
        self.assertEqual(n[("decisive-a", A["etiquette"], "v2")], 216)
        self.assertEqual(n[("decisive-b", B["etiquette"], "ancien")], 30)
        self.assertLessEqual(n[("decisive-b", B["etiquette"], "v2")], 3 * J.PAIRES_B_MAX_PAR_LOT)
        self.assertEqual(n[("sans-dossier-a", A["etiquette"], "ancien")], 30)
        self.assertTrue(all(e["dossier"] is False for e in etapes if e["phase"] == "sans-dossier-a"))
        b = [e["protocole"] for e in etapes if e["phase"] == "decisive-b"]
        self.assertEqual(b, sorted(b, key=("v2", "ancien").index))  # priorité : comparaisons de B d'abord
        q = {f["ident"]: f["qualite"] for l in MATERIAUX["lots"] for f in l["fiches"]}
        for e in etapes:
            if e["phase"] == "decisive-b" and e["protocole"] == "v2":
                self.assertTrue(all(q[x] != q[y] for x, y in e["appels"]))
        d = J.devis(etapes, {A["etiquette"]: A, B["etiquette"]: B})
        self.assertLessEqual(d["requis_usd"][A["etiquette"]], 24.0)
        self.assertLessEqual(d["requis_usd"][B["etiquette"]], 36.0)
        self.assertLessEqual(d["duree_h"][1], 48.0)

    def test_artefacts_juges_de_la_famille_des_gabarits_de_meme_famille_ou_de_meme_relais(self):
        with self.assertRaisesRegex(J.ProtocoleRefuse, "auteur des gabarits"):
            J.etapes_v2(MATERIAUX, dict(A, famille="claude"), B, Graines(1))
        with self.assertRaisesRegex(J.ProtocoleRefuse, "distincts"):
            J.etapes_v2(MATERIAUX, A, dict(B, famille=A["famille"]), Graines(1))
        with self.assertRaisesRegex(J.ProtocoleRefuse, "distincts"):
            J.etapes_v2(MATERIAUX, A, dict(B, fournisseur=A["fournisseur"]), Graines(1))

    def test_regle_de_famille_sur_le_lot_reel(self):
        reel, _ = lot_reel()
        fam = {f["ident"]: set(f["familles"]) for f in reel["fiches"]}
        self.assertEqual(fam["reel-12"], {"kimi", "gemini"})  # une fusion : les familles de ses parents aussi
        etapes, _ = J.etapes_v2(MATERIAUX, A, B, Graines(9), lot_reel=reel)
        for e in etapes:
            if e["lot"] == "reel":
                ids = e["fiches"] if e["protocole"] == "ancien" else [i for p in e["appels"] for i in p]
                juge = A if e["juge"] == A["etiquette"] else B
                self.assertTrue(all(juge["famille"] not in fam[i] for i in ids), e["juge"])
        artefact = {"phase": "reel-ancien", "protocole": "ancien", "lot": "reel", "juge": A["etiquette"], "tirage": 1,
                    "fiches": ["reel-02"], "dossier": False}  # fiche d'auteur argon (famille du juge A)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "règle de famille"):
            J.jouer_etape(artefact, lots={"reel": reel}, juges={A["etiquette"]: A}, adaptateurs={A["fournisseur"]: None},
                          consignes=CONSIGNES, items=J.ITEMS_SUBSTITUTION, graines=Graines(1), compteur=None, plafond_session=1,
                          interdites=J.ETIQUETTES_INTERDITES_TEMOINS, dossier_appel=None, journal=J.journal_vide())
        with self.assertRaisesRegex(J.ProtocoleRefuse, "correspondance"):
            J.lot_reel_depuis({"fiches": [{"ident": "x", "contenu": {}, "meta": {"fournisseur": "inconnu"}}]}, "Q", CORRESP)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "fiches >"):
            J.lot_reel_depuis({"fiches": [{"ident": f"x{k}", "contenu": {}, "meta": {"fournisseur": "kimi"}} for k in range(14)]},
                              "Q", CORRESP)
        with self.assertRaisesRegex(J.ProtocoleRefuse, "forme des témoins"):
            J.lot_reel_depuis({"fiches": [{"ident": "monde-1-01", "contenu": {}, "meta": {"fournisseur": "kimi"}}]}, "Q", CORRESP)


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
        for m, n in ((6, 6), (10, 10), (15, 15), (15, 7)):
            e = J.loi_u(m, n)
            t = sum(e)
            uc = J.seuil_u(m, n, 0.05)
            self.assertLessEqual(sum(e[uc:]) / t, 0.05)
            self.assertGreater(sum(e[uc - 1:]) / t, 0.05)
        self.assertEqual(J.seuil_u(15, 15, 0.05), 153)
        r = J.test_mann_whitney([4, 5, 6], [1, 2, 3])
        self.assertAlmostEqual(r["p"], 1 / 20)
        self.assertEqual(r["methode"], "loi exacte")
        self.assertEqual(J.test_mann_whitney([1, 1, 1], [1, 1, 1])["p"], 1.0)

    def test_binomial_exact(self):
        self.assertAlmostEqual(J.test_binomial_unilateral(3, 3), 0.125)
        self.assertAlmostEqual(J.test_binomial_unilateral(0, 5), 1.0)
        self.assertIsNone(J.test_binomial_unilateral(0, 0))
        for n in (20, 29, 39):
            kc = J.seuil_binomial(n, 0.10)
            self.assertLessEqual(J.test_binomial_unilateral(kc, n), 0.10)
            self.assertGreater(J.test_binomial_unilateral(kc - 1, n), 0.10)
        p = [J.puissance_binomiale(28, x, 0.10)["puissance"] for x in (0.5, 0.7, 0.8)]
        self.assertLessEqual(p[0], 0.10)
        self.assertTrue(p[0] < p[1] < p[2], p)

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
        self.assertAlmostEqual(J.plafond_spearman_binaire((15, 15)), 1 - 2 * 15 * 224 / (30 * 899))

    def test_puissance(self):
        nul = J.puissance_aire(15, 15, 0.5, repetitions=4000, graine=1)
        self.assertLessEqual(nul["alpha_exact"], 0.05)
        self.assertLessEqual(nul["puissance_d1"], 0.065)
        self.assertEqual(nul["u_critique"], 153)
        p = [J.puissance_aire(15, 15, a, repetitions=4000, graine=1)["puissance_d1"] for a in (0.65, 0.8, 0.9)]
        self.assertTrue(p[0] < p[1] < p[2], p)
        with self.assertRaises(J.ProtocoleRefuse):
            J.puissance_aire(10, 10, 1.0)

    def test_bascule_comptee_par_tirage_et_par_paire(self):
        """Contre-lecture v1, M3 : une paire tirée aux deux tirages, vue dans les deux ordres à chacun, compte deux fois."""
        def e(t, premier, second, gagnant):
            return {"valide": True, "tirage": t, "paire": sorted((premier, second)), "premier": premier, "gagnant": gagnant,
                    "premier_gagne": gagnant == premier}
        recs = [e(1, "a", "b", "a"), e(1, "b", "a", "b"), e(2, "a", "b", "a"), e(2, "b", "a", "a")]
        r = J.biais_position(recs)
        self.assertEqual(r["paires_deux_ordres"], 2)
        self.assertEqual(r["bascules"], 1)
        self.assertEqual(r["taux_bascule"], 0.5)


# --- statuts du relais, appels, reprises (contre-lecture v1, B2) ------------------------------------------------------------------


class Suite(Adaptateur):
    """Adaptateur d'essai : rend les résultats donnés, dans l'ordre (le dernier se répète) ; aucun appel."""

    def __init__(self, *resultats, horloge=None, secondes=0.0):
        self.resultats, self.appels, self.horloge, self.secondes = list(resultats), 0, horloge, secondes

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        self.appels += 1
        if self.horloge is not None:
            self.horloge.avancer(self.secondes)
        r = self.resultats[min(self.appels, len(self.resultats)) - 1]
        return r(budget_usd, modele) if callable(r) else r


def ok(texte="```json\n{\"items\": {\"K1\": true, \"K2\": true, \"K3\": true, \"K4\": true, \"K5\": true}}\n```", cout=0.05,
       servi="__demande__"):
    return lambda b, m: Resultat(texte, [], cout, "ok", texte_brut=texte, modele_servi=m if servi == "__demande__" else servi)


PLANCHER_3 = Resultat("", [], 1e-6, "erreur", "commande externe : code 3 : relais injoignable")
PLANCHER_4 = Resultat("", [], 1e-6, "erreur", "commande externe : code 4 : 429")
DELAI = Resultat("", [], 1.0, "erreur", "commande externe : délai de 1800 s dépassé, groupe de processus arrêté ; coût inconnu, "
                 "plafond de session compté", cout_inconnu=True)


class Relais(unittest.TestCase):
    def appeler(self, adaptateur, h=None, plafond=10.0, parts=None):
        h = h or J.HorlogeVirtuelle()
        c = J.Compteur(plafond, 48 * 3600.0, h, {"j": 0.05}, parts=parts or {"j": plafond}, dormir=h.avancer)
        journal = J.journal_vide()
        texte, info = J.appeler(adaptateur, {"etiquette": "j", "modele": "gemini-4-argon"}, "entrée", os.devnull, c, 1.0, journal, {})
        return texte, info, c, journal, h

    def test_classement_des_statuts(self):
        def r(statut, erreur=None, **kw):
            return Resultat("", [], 0.01, statut, erreur, **kw)
        cas = [(ok()(1, "m"), "reponse"), (r("ok", modele_servi="m-lite"), "a2"), (r("ok", modele_servi=None), "a2"),
               (r("refus", "refus", refus={"evenement": "commande.modele_servi"}), "a2"),
               (r("refus", "refus", refus={"evenement": "commande.modele_servi_absent"}), "a2"),
               (r("refus", "refus", refus={"evenement": "commande.refus"}), "refus_modele"),
               (r("erreur", "commande externe : code 3 : x"), "relais"), (r("erreur", "commande externe : code 4 : 429"), "quota"),
               (r("erreur", "commande externe : code 5 : tronquée"), "non_conforme"), (r("erreur", "commande externe : code 6 : x"), "delai"),
               (r("erreur", "commande externe : code 2 : réglage"), "reglage"),
               (r("erreur", "commande externe : délai de 1800 s dépassé, groupe de processus arrêté"), "delai"),
               (r("refus", "refus (R-764) : x (code 5 : y)", refus={"evenement": "commande.modele_servi"}), "a2"),
               (r("budget_depasse", "coût déclaré au-dessus du plafond de session"), "depassement"),
               (r("erreur", "commande externe non lancée (OSError : x)"), "autre")]
        for res, genre in cas:
            with self.subTest(statut=res.statut, erreur=res.erreur, genre=genre):
                self.assertEqual(J.classer_resultat(res, "m")["genre"], genre)

    def test_cas_sain_reponse_prix_observe(self):
        texte, info, c, journal, _ = self.appeler(Suite(ok()))
        self.assertIn("items", texte)
        self.assertEqual(info["issue_appel"], "reponse")
        self.assertEqual(c.couts["j"], [0.05])

    def test_a2_modele_servi_different_absent_ou_refus_au_premier_appel(self):
        refus = Resultat("", [], 0.02, "refus", "refus (R-764) : modèle servi", refus={"evenement": "commande.modele_servi"},
                         modele_servi="gemini-4-argon-lite")
        for nom, res in (("différent", ok(servi="gemini-4-argon-lite")), ("absent", ok(servi=None)), ("vide", ok(servi="")),
                         ("statut refus de la commande v56", refus)):
            with self.subTest(cas=nom):
                s = Suite(res)
                with self.assertRaises(J.ArretModeleServi):
                    self.appeler(s)
                self.assertEqual(s.appels, 1)
        texte, info, *_ = self.appeler(Suite(ok(servi="gemini-4-argon-20261101")))  # suffixe de date strict admis
        self.assertEqual(info["issue_appel"], "reponse")

    def test_refus_du_modele_jamais_lu_comme_verdict(self):
        refus = Resultat("", [], 0.02, "refus", "refus (R-764) : refus", refus={"evenement": "commande.refus"},
                         texte_brut="```json\n{\"comparaison\": {\"preferee\": \"F1\"}}\n```")
        texte, info, c, *_ = self.appeler(Suite(refus))
        self.assertIsNone(texte)
        self.assertEqual(info["issue_appel"], "refus_modele")

    def test_rien_d_envoye_attente_puis_reprise_sans_perte(self):
        for nom, echec in (("relais injoignable", PLANCHER_3), ("quota", PLANCHER_4)):
            with self.subTest(cas=nom):
                s = Suite(echec, echec, echec, ok())
                texte, info, c, journal, h = self.appeler(s)
                self.assertEqual(info["issue_appel"], "reponse")
                self.assertEqual(s.appels, 4)
                self.assertEqual([a["attente_s"] for a in journal["attentes"]], [15.0, 30.0, 60.0])
                self.assertEqual(h(), 105.0)
                self.assertEqual(c.couts["j"], [0.05])  # le coût plancher n'entre pas dans le prix observé

    def test_artefact_relais_injoignable_trop_longtemps_juge_en_panne(self):
        s = Suite(PLANCHER_3)
        with self.assertRaises(J.ArretPanne) as e:
            self.appeler(s)
        self.assertIn("en panne", str(e.exception))
        self.assertGreater(s.appels, 70)  # 6 h d'attentes (300 s à partir de la sixième)

    def test_echec_couteux_perdu_hors_du_prix_observe(self):
        for nom, echec, cause in (("délai", DELAI, "delai"),
                                  ("réponse tronquée", Resultat("", [], 0.3, "erreur", "commande externe : code 5 : tronquée"), "non_conforme"),
                                  ("relais après envoi", Resultat("", [], 0.3, "erreur", "commande externe : code 3 : interface"), "relais"),
                                  ("dépassement", Resultat("```json\n{}\n```", [], 1.6, "budget_depasse", "coût au-dessus",
                                                           texte_brut="```json\n{}\n```"), "depassement"),
                                  ("commande muette", Resultat("", [], 1.0, "erreur", "commande externe : dernière ligne non JSON ; "
                                                               "coût inconnu", cout_inconnu=True), "autre")):
            with self.subTest(cas=nom):
                h = J.HorlogeVirtuelle()
                c = J.Compteur(100.0, 1e9, h, {"j": 0.05}, dormir=h.avancer)
                s, journal, juge = Suite(ok(), ok(), ok(), echec), J.journal_vide(), {"etiquette": "j", "modele": "gemini-4-argon"}
                for _ in range(3):
                    J.appeler(s, juge, "entrée", os.devnull, c, 1.0, journal, {})
                texte, info = J.appeler(s, juge, "entrée", os.devnull, c, 1.0, journal, {})
                self.assertIsNone(texte)
                self.assertEqual((info["issue_appel"], info["cause"]), ("perte", cause))
                self.assertEqual(c.couts["j"], [0.05] * 3)  # jamais dans le prix observé
                self.assertAlmostEqual(c.prix("j"), 0.05)
                self.assertGreater(c.depense, 0.15 + 0.2)  # mais compté dans la dépense

    def test_artefact_echecs_couteux_consecutifs_juge_en_panne(self):
        h = J.HorlogeVirtuelle()
        c = J.Compteur(100.0, 1e9, h, {"j": 0.05}, dormir=h.avancer)
        for k in range(J.ECHECS_COUTEUX_MAX - 1):
            c.echec_couteux("j")
            c.verifier_echecs_couteux("j")
        c.echec_couteux("j")
        with self.assertRaises(J.ArretPanne):
            c.verifier_echecs_couteux("j")
        c.succes("j")
        c.verifier_echecs_couteux("j")

    def etape(self, adaptateur, appels=(("monde-1-01", "monde-1-07"), ("monde-1-02", "monde-1-08"), ("monde-1-03", "monde-1-09")),
              phase="decisive-a", prevus=None):
        etape = {"phase": phase, "protocole": "v2", "lot": "monde-1", "juge": A["etiquette"], "tirage": 1, "appels": list(appels)}
        h = J.HorlogeVirtuelle()
        c = J.Compteur(100.0, 1e9, h, {A["etiquette"]: 0.05}, dormir=h.avancer)
        journal = J.journal_vide()
        J.jouer_etape(etape, lots={l["nom"]: l for l in MATERIAUX["lots"]}, juges={A["etiquette"]: A},
                      adaptateurs={A["fournisseur"]: adaptateur}, consignes=CONSIGNES, items=J.ITEMS_SUBSTITUTION, graines=Graines(3),
                      compteur=c, plafond_session=1.0, interdites=J.ETIQUETTES_INTERDITES_TEMOINS,
                      dossier_appel=lambda j, e: os.devnull, journal=journal, prevus=prevus or {})
        return journal

    def test_reprise_bornee_puis_perte_definitive(self):
        parfait = J.AdaptateurScripte("parfait", J.oracle_depuis(MATERIAUX))
        une_fois = J.AdaptateurPanneScripte(parfait, [(2, 2, "delai")])
        journal = self.etape(une_fois)
        self.assertEqual(len(journal["v2"]), 3)
        self.assertEqual([p["definitive"] for p in journal["pertes"]], [False])
        self.assertEqual(journal["v2"][-1]["essai"], 2)  # l'appel perdu, repris en fin d'étape
        trois_fois = J.AdaptateurPanneScripte(parfait, [(2, 2, "delai"), (4, 4, "delai"), (5, 5, "delai")])
        journal = self.etape(trois_fois)
        self.assertEqual(len(journal["v2"]), 2)
        self.assertEqual([p["definitive"] for p in journal["pertes"]], [False, False, True])
        self.assertEqual(J._completude(journal, [{"phase": "decisive-a", "juge": A["etiquette"], "protocole": "v2",
                                                  "appels": [1, 2, 3]}])[f"decisive-a/{A['etiquette']}"],
                         {"prevus": 3, "repondus": 2, "pertes_definitives": 1, "non_joues": 0, "complet": True})

    def test_artefact_pertes_definitives_au_dela_de_15_pour_cent(self):
        parfait = J.AdaptateurScripte("parfait", J.oracle_depuis(MATERIAUX))
        toujours = J.AdaptateurPanneScripte(parfait, [(1, None, "delai")])
        with self.assertRaises(J.ArretPanne):  # cinq échecs coûteux de suite : panne, avant même la part de pertes
            self.etape(toujours, prevus={f"decisive-a/{A['etiquette']}": 3})
        alterne = J.AdaptateurPanneScripte(parfait, [(1, 3, "delai"), (5, 5, "delai")])
        with self.assertRaises(J.ArretInfrastructure):
            self.etape(alterne, appels=(("monde-1-01", "monde-1-07"),), prevus={f"decisive-a/{A['etiquette']}": 3})


# --- compteur, parts, projections ---------------------------------------------------------------------------------------------------


class Compteur(unittest.TestCase):
    def test_cas_sain_et_artefacts_du_compteur(self):
        h = J.HorlogeVirtuelle()
        c = J.Compteur(1.0, 100, h, {"x": 0.1}, parts={"x": 1.0}, dormir=h.avancer)
        self.assertEqual(c.budget_appel(0.5, "x"), 0.5)
        for _ in range(3):
            c.noter("x", 0.3)
        self.assertAlmostEqual(c.prix("x"), 0.3)
        self.assertAlmostEqual(c.budget_appel(0.5, "x"), 0.1)
        with self.assertRaises(J.ArretDevis):
            c.exiger_projection({"x": 1}, "essai")
        large = J.Compteur(1.0, 100, h, {"x": 0.1}, parts={"x": 5.0}, dormir=h.avancer)
        for _ in range(3):
            large.noter("x", 0.3)
        with self.assertRaises(J.ArretDevis):  # le reste du plafond lie, pas la part
            large.exiger_projection({"x": 1}, "essai")
        c.noter("x", 0.1)
        with self.assertRaises(J.ArretDevis):
            c.budget_appel(0.5, "x")
        with self.assertRaises(J.ArretDevis):
            J.Compteur(1.0, 100, h, {"x": 0.1}).noter("x", float("nan"))
        d = J.Compteur(1.0, 5, h, {"x": 0.1})
        h.avancer(10.0)
        with self.assertRaises(J.ArretDuree):
            d.verifier_duree()
        for duree in (0, -1, float("inf")):
            with self.subTest(duree=duree), self.assertRaises(J.ProtocoleRefuse):
                J.Compteur(1.0, duree, h, {"x": 0.1})

    def test_parts_des_juges(self):
        h = J.HorlogeVirtuelle()
        c = J.Compteur(60.0, 1e6, h, {"a": 0.062, "b": 0.5}, parts={"a": 24.0, "b": 36.0}, dormir=h.avancer)
        c.noter("b", 35.999)
        with self.assertRaises(J.ArretPart):  # part de B atteinte : arrêt du juge B, pas de la course
            c.budget_appel(1.0, "b")
        self.assertEqual(c.budget_appel(1.0, "a"), 1.0)
        self.assertFalse(c.tient({"b": 1})[0])  # dans le reste du plafond, pas dans le reste de la part de B
        neuf = J.Compteur(60.0, 1e6, h, {"a": 0.062, "b": 0.5}, parts={"a": 24.0, "b": 36.0}, dormir=h.avancer)
        self.assertFalse(neuf.tient({"a": 400})[0])  # 400 × 0,062 = 24,8 > part de 24, sous le plafond de 60
        self.assertTrue(neuf.tient({"a": 300})[0])
        with self.assertRaises(J.ProtocoleRefuse):
            J.Compteur(60.0, 1e6, h, {"a": 0.062}, parts={"a": 0})


# --- courses à juges scriptés : mesures, pannes, arrêts ---------------------------------------------------------------------------


class Mesures(unittest.TestCase):
    def test_juge_toujours_notable_detecte_au_plafond(self):
        _, mes, lec, _ = course_memo("plafond", "plafond")
        a = mes["ancien"][A["etiquette"]]["avec_dossier"]
        self.assertTrue(a["au_plafond"])
        self.assertEqual(a["part_notables"], 1.0)
        self.assertIsNone(mes["accord"]["kappa_ancien"]["kappa"])
        self.assertIn("non défini", mes["accord"]["kappa_ancien"]["statut"])
        self.assertTrue(any("trop propre" in x for x in lec["audit"]["motifs"]))
        _, sain, _, _ = course_memo("parfait", "parfait")
        self.assertFalse(sain["ancien"][A["etiquette"]]["avec_dossier"]["au_plafond"])

    def test_juge_parfait_atteint_la_discrimination(self):
        _, mes, lec, _ = course_memo("indulgent", "parfait")
        v = mes["v2"][A["etiquette"]]["1"]
        self.assertGreaterEqual(v["aire"], 0.85)  # graphe 3-régulier : une bonne fiche peut ne rencontrer que de bonnes fiches
        self.assertLess(v["p_mann_whitney"], 0.01)
        self.assertGreaterEqual(v["aire_lois_fausses"], 0.8)
        self.assertLessEqual(v["faux_notables"], 0.1)
        self.assertEqual(v["validite"], 1.0)
        self.assertTrue(lec["criteres"]["D1"]["tenu"] and lec["criteres"]["D1b"]["tenu"])
        self.assertEqual(mes["ancien"][A["etiquette"]]["avec_dossier"]["aire"], 0.5)  # indulgent : l'ancien ne départage rien
        self.assertGreaterEqual(mes["comparaison_a"]["difference"], 0.3)
        self.assertLessEqual(v["part_notables"], 0.3)
        self.assertEqual(mes["accord"]["exactitude_b"]["exactitude"], 1.0)

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
        self.assertAlmostEqual(mes["accord"]["kappa_paires_v2"]["kappa"], 0.0, delta=0.05)  # deux ordres chez A : 0 par construction
        self.assertLess(abs(mes["accord"]["exactitude_b"]["exactitude"] - 0.5), 0.25)
        _, sain, _, _ = course_memo("parfait", "parfait")
        self.assertEqual(sain["accord"]["kappa_paires_v2"]["kappa"], 1.0)

    def test_juge_verbeux_mesure(self):
        _, mes, lec, _ = course_memo("verbeux", "parfait")
        self.assertGreater(mes["classes"]["rang_v2_a1"]["verbeuse"], 0.8)
        cle = next(k for k in lec["predictions"] if k.startswith("P9"))
        self.assertFalse(lec["predictions"][cle]["tenue"])

    def test_artefacts_citations_fausses_ou_reponses_illisibles_arretent_la_phase_decisive_de_a(self):
        for strategie in ("citations_fausses", "illisible"):
            with self.subTest(strategie=strategie), self.assertRaises(J.ArretValidite) as e:
                course(strategie, "parfait")
            self.assertEqual(len(e.exception.partiel["ancien"]) + len(e.exception.partiel["v2"]), 20 if strategie == "illisible" else 50)

    def test_bras_sans_dossier_mesure(self):
        _, mes, lec, _ = course_memo("indulgent", "parfait")
        bras = mes["bras_sans_dossier"]
        self.assertEqual(bras["presents"], 30)
        self.assertEqual(bras["part_notables"], 1.0)
        self.assertEqual(lec["bras_sans_dossier"]["lecture"], "S2")
        self.assertTrue(all(e["bras"] == "sans_dossier" for e in course_memo("indulgent", "parfait")[0]["ancien"]
                            if e["phase"] == "sans-dossier-a"))

    def test_lot_reel_decrit_seulement(self):
        _, mes, lec, _ = course("indulgent", "parfait", avec_reel=True, couts=(0.062, 0.25))
        r = mes["reel"]
        self.assertEqual(r["fiches"], 12)
        self.assertEqual(r[B["etiquette"]]["ancien_repondus"], 12)
        self.assertEqual(r[A["etiquette"]]["ancien_repondus"], 6)  # les six fiches d'auteur kimi ; la fusion (kimi et argon) exclue
        self.assertIn("sans ancre", r[B["etiquette"]]["v2_statut"])
        self.assertEqual(lec["issue"], "I1")


class Pannes(unittest.TestCase):
    """Une panne d'un juge ne rend pas la course non concluante par défaut de conception (décision de Lazar)."""

    def test_panne_passagere_de_a_sans_aucune_perte_meme_resultat(self):
        sain = course_memo("indulgent", "parfait")
        journal, mes, lec, _ = course("indulgent", "parfait", pannes=([(10, 40, "relais_plancher"), (100, 103, "quota")], None))
        self.assertEqual(journal["pertes"], [])
        self.assertEqual(len(journal["attentes"]), 35)
        self.assertEqual(mes["v2"][A["etiquette"]]["1"]["forces"], sain[1]["v2"][A["etiquette"]]["1"]["forces"])
        self.assertEqual(lec["issue"], sain[2]["issue"])

    def test_b_hors_service_n_arrete_que_b(self):
        journal, mes, lec, _ = course("indulgent", "parfait", pannes=(None, [(1, None, "relais_plancher")]))
        self.assertEqual([x["type"] for x in journal["arrets_juges"]], ["ArretPanne"])
        self.assertEqual(journal["arrets_juges"][0]["juge"], B["etiquette"])
        self.assertTrue(all(e["juge"] == A["etiquette"] for e in journal["ancien"] + journal["v2"]))
        self.assertEqual(sum(1 for e in journal["ancien"] if e["phase"] == "sans-dossier-a"), 30)  # le bras de A joué ensuite
        self.assertIsNone(lec["criteres"]["D6"]["tenu"])
        self.assertEqual(lec["issue"], "I1")
        self.assertTrue(any("accord du juge B non mesuré" in r for r in lec["reserves"]))
        self.assertTrue(any("instrument" in x for x in lec["audit"]["motifs"]))

    def test_artefact_a_hors_service_arrete_la_course_issue_i0(self):
        with self.assertRaises(J.ArretPanne) as e:
            course("indulgent", "parfait", pannes=([(50, None, "relais_plancher")], None))
        partiel = e.exception.partiel
        mes = J.mesurer(partiel, MATERIAUX, A, B, etapes=J.etapes_v2(MATERIAUX, A, B, Graines(11))[0])
        self.assertEqual(J.lire_validation(mes)["issue"], "I0")

    def test_b_illisible_n_arrete_que_b_pour_la_phase(self):
        journal, mes, lec, _ = course("indulgent", "illisible")
        self.assertEqual([x["type"] for x in journal["arrets_juges"]], ["ArretValidite"])
        self.assertEqual(sum(1 for e in journal["ancien"] if e["phase"] == "sans-dossier-a"), 30)
        self.assertIsNone(lec["criteres"]["D6"]["tenu"])

    def test_part_de_b_trop_chere_etapes_non_jouees_sans_arret(self):
        journal, mes, lec, _ = course("indulgent", "parfait", couts=(0.062, 1.0))
        non_jouees = [x for x in journal["etapes"] if x["etat"] == "non_jouee"]
        self.assertTrue(non_jouees and all(x["juge"] == B["etiquette"] for x in non_jouees))
        self.assertTrue(all(x["protocole"] == "ancien" for x in non_jouees))  # les comparaisons de B d'abord
        self.assertLessEqual(journal["compteur"]["depense_par_juge_usd"][B["etiquette"]], 36.0)
        self.assertTrue(lec["criteres"]["D6"]["tenu"])

    def test_artefact_phase_decisive_de_a_au_dessus_de_sa_part_arret_avant_tout_appel(self):
        with self.assertRaises(J.ArretDevis) as e:
            course("parfait", "parfait", couts=(0.062, 0.5), plafond=30.0)
        self.assertEqual(len(e.exception.partiel["ancien"]) + len(e.exception.partiel["v2"]), 0)

    def test_phase_descriptive_non_jouee_si_la_part_ne_suffit_pas(self):
        journal, _, lec, _ = course("indulgent", "parfait", avec_reel=True, couts=(0.062, 0.5))
        non_jouees = [x["juge"] for x in journal["etapes"] if x["etat"] == "non_jouee" and x["phase"].startswith("reel")]
        self.assertTrue(non_jouees)
        self.assertEqual(set(non_jouees), {B["etiquette"]})
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

    def test_artefact_a2_pendant_la_course(self):
        with self.assertRaises(J.ArretModeleServi):
            course("parfait", "parfait", pannes=([(5, 5, "autre_modele")], None))
        journal, _, _, _ = course("parfait", "parfait", pannes=([(5, 5, "refus_modele")], None))
        refus = [e for e in journal["ancien"] if e.get("genre") == "refus_modele"]
        self.assertEqual(len(refus), 1)
        self.assertFalse(refus[0]["valide"])  # jamais un verdict

    def test_artefact_duree_maximale(self):
        with self.assertRaises(J.ArretDuree):
            course("parfait", "parfait", duree=600.0)


# --- lecture gelée --------------------------------------------------------------------------------------------------------------


class Lecture(unittest.TestCase):
    def test_issues_atteignables(self):
        self.assertEqual(course_memo("indulgent", "parfait")[2]["issue"], "I1")
        self.assertEqual(course_memo("parfait", "parfait")[2]["issue"], "I2")
        self.assertEqual(course_memo("plafond", "plafond")[2]["issue"], "I3")
        _, mes, _, _ = course_memo("indulgent", "parfait")
        m = copy.deepcopy(mes)
        m["v2"][A["etiquette"]]["2"]["p_mann_whitney"] = 0.4
        self.assertEqual(J.lire_validation(m)["issue"], "I4")
        m = copy.deepcopy(mes)
        m["accord"]["exactitude_b"].update(exactitude=0.5, p=0.6)
        self.assertEqual(J.lire_validation(m)["issue"], "I4")
        m = copy.deepcopy(mes)
        m["completude"][f"decisive-a/{A['etiquette']}"]["complet"] = False
        self.assertEqual(J.lire_validation(m)["issue"], "I0")
        m = copy.deepcopy(mes)
        m["completude"][f"decisive-a/{A['etiquette']}"]["pertes_definitives"] = 40
        lec = J.lire_validation(m)
        self.assertEqual(lec["issue"], "I0")
        self.assertIn("infrastructure", lec["sous_issue"])
        m = copy.deepcopy(mes)
        m["accord"]["exactitude_b"]["n"] = 19
        lec = J.lire_validation(m)
        self.assertEqual(lec["issue"], "I1")
        self.assertIsNone(lec["criteres"]["D6"]["tenu"])
        self.assertTrue(lec["reserves"])

    def test_lectures_jointes_bras_et_tables(self):
        _, mes, _, _ = course_memo("indulgent", "parfait")
        lectures = {}
        for d2, d7, presents in ((1.0, 1.0, 30), (0.5, 1.0, 30), (0.5, 0.5, 30), (1.0, 1.0, 20)):
            m = copy.deepcopy(mes)
            m["ancien"][A["etiquette"]]["avec_dossier"]["part_notables"] = d2
            m["ancien"][A["etiquette"]]["sans_dossier"].update(part_notables=d7, presents=presents)
            lectures[(d2, d7, presents)] = J.lire_validation(m)["bras_sans_dossier"]["lecture"]
        self.assertEqual(list(lectures.values()), ["S2", "S1", "S3", "S0"])
        m = copy.deepcopy(mes)
        m["v2"][A["etiquette"]]["1"]["p_lois_fausses"] = 0.3
        self.assertEqual(J.lire_validation(m)["lecture_des_tables"]["lecture"], "T0")
        self.assertEqual(course_memo("indulgent", "parfait")[2]["lecture_des_tables"]["lecture"], "T1")

    def test_audit_symetrique(self):
        beau = course_memo("indulgent", "parfait")[2]["audit"]
        decevant = course_memo("plafond", "plafond")[2]["audit"]
        self.assertTrue(beau["declenche"] and decevant["declenche"])
        self.assertTrue(any(x.startswith("trop beau") for x in beau["motifs"]))
        self.assertTrue(any(x.startswith("décevant : aire v2") for x in decevant["motifs"]))
        self.assertEqual(beau["verifications"], decevant["verifications"])

    def test_seuils_du_texte_egaux_au_code(self):
        self.assertEqual(lanceur.PLAN_FIXE["seuils"], ", ".join(f"{k}={v}" for k, v in J.SEUILS_LECTURE_V2.items()))
        self.assertEqual(lanceur.PLAN_FIXE["politique_relais"], J.politique_relais())


# --- lanceur ------------------------------------------------------------------------------------------------------------------------


class LanceurABlanc(unittest.TestCase):
    def test_a_blanc_de_bout_en_bout(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
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
            self.assertTrue(m["controles_des_materiaux"]["diagnosticite"]["conforme"])

    def test_a_blanc_juge_b_en_panne(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--panne-b", "relais_plancher:1-"]), 0)
            with open(os.path.join(sortie, lanceur.SORTIES["lecture"]), encoding="utf-8") as f:
                lec = json.load(f)
            self.assertEqual(lec["issue"], "I1")
            self.assertIsNone(lec["criteres"]["D6"]["tenu"])

    def test_refus_avant_toute_ecriture(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            for argv in ([sortie, "--a-blanc", "--graine", str(2 ** 64)], [sortie, "--a-blanc"],
                         [sortie, "--a-blanc", "--graine", "7", "--strategie-a", "inconnue"],
                         [sortie, "--a-blanc", "--graine", "7", "--panne-a", "orage:1-3"],
                         [sortie, "--a-blanc", "--graine", "7", "--go", "GO-2026-11-02-01"]):
                with self.subTest(argv=argv[1:]), unittest.mock.patch("sys.stderr", new_callable=io.StringIO):
                    self.assertEqual(lanceur.principal(argv), 2)
                    self.assertFalse(os.path.exists(sortie))
            os.makedirs(sortie)
            open(os.path.join(sortie, "f"), "w").close()
            with unittest.mock.patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7"]), 2)

    def test_arret_ecrit_un_journal_partiel_scelle(self):
        with tempfile.TemporaryDirectory() as d:
            sortie = os.path.join(d, "s")
            with unittest.mock.patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(lanceur.principal([sortie, "--a-blanc", "--graine", "7", "--plafond-usd", "5"]), 3)
            with open(os.path.join(sortie, lanceur.SORTIES["lecture"]), encoding="utf-8") as f:
                lec = json.load(f)
            self.assertTrue(lec["partielle"])
            self.assertEqual(lec["issue"], "I0")
            self.assertTrue(os.path.isfile(os.path.join(sortie, lanceur.SORTIES["journal"] + ".sha256")))


def texte_preenregistrement(*, conf_sha, go="GO-2026-11-02-09", marqueur="", empreintes=None, plafond="60", parts=("24", "36"),
                            consigne=None, materiaux_sha=None, juge_b="etiquette=juge-b, fournisseur=astra, modele=gpt-6-astra, famille=gpt, "
                                                                   "prix_usd=0.5, secondes=10-120", sans=None, en_plus="", remplace=None):
    lignes = {"juge_a": "etiquette=juge-a, fournisseur=argon, modele=gemini-4-argon, famille=gemini, prix_usd=0.062, secondes=8-40",
              "juge_b": juge_b, "correspondance_auteurs": "kimi=kimi, argon=gemini", "graine_materiaux": str(J.GRAINE_MATERIAUX),
              "materiaux_sha256": materiaux_sha or MATERIAUX["empreinte"],
              "consigne_paire_sha256": consigne or J.EMPREINTE_CONSIGNE_PAIRE_V2, "piece_consigne_ancienne": "consigne_juge",
              "piece_question": "question_course_2", "piece_lot_reel": "lot_reel_juges_idees_v2", "plafond_usd": plafond,
              "plafond_juge_a_usd": parts[0], "plafond_juge_b_usd": parts[1], "duree_max_h": "48", "configuration_sha256": conf_sha,
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


JUGE_FACTICE = r'''import json, os, re, sys
entree = sys.stdin.read()
d = os.path.dirname(os.path.abspath(__file__))
nom = os.path.basename(__file__)[:-3]
compte = os.path.join(d, nom + ".compte")
n = int(open(compte).read()) + 1 if os.path.exists(compte) else 1
open(compte, "w").write(str(n))
scenario = SCENARIO
action = scenario[min(n, len(scenario)) - 1] if scenario else {"code": 0, "type": "repondre"}
def norm(t):
    return re.sub(r"\s+", " ", t).strip().lower()
def repondre():
    blocs = re.findall(r"## Fiche (\S+) \(présentée en (premier|second)\)\n```json\n(.*?)\n```", entree, re.S)
    if blocs:
        (i1, _, j1), (i2, _, j2) = blocs[0], blocs[1]
        c1, c2 = json.loads(j1), json.loads(j2)
        autre = norm(" ".join(str(v) for k, v in c2.items() if k != "identifiant"))
        cit = None
        for k, v in c1.items():
            if k == "identifiant" or not isinstance(v, str):
                continue
            for i in range(0, max(1, len(v) - 20), 7):
                m = v[i:i + 60]
                if len(norm(m)) >= 15 and norm(m) not in autre:
                    cit = m
                    break
            if cit:
                break
        dossier = re.search(r"(?m)^- (D\d{2,} · .+)$", entree)
        corps = {"comparaison": {"preferee": i1, "critere": "verite", "citation_fiche": cit or "",
                                 "citation_dossier": dossier.group(1) if dossier else ""}}
    else:
        corps = {"items": {k: True for k in ITEMS}, "note": 5}
    return "```json\n" + json.dumps(corps, ensure_ascii=False) + "\n```"
t = action.get("type", "repondre")
if t == "repondre":
    o = {"texte": repondre(), "cout_usd": COUT, "modele_servi": action.get("modele_servi", MODELE)}
elif t == "refus":
    o = {"texte": "", "cout_usd": COUT, "refus": True, "modele_servi": MODELE}
elif t == "ligne":
    o = action["ligne"]
else:
    o = None
if o is not None:
    print(json.dumps(o, ensure_ascii=False))
if action.get("stderr"):
    sys.stderr.write(action["stderr"])
sys.exit(action.get("code", 0))
'''


def commande_juge_factice(dossier, nom, modele, items, scenario=None, cout=0.001):
    """Commande externe factice (script Python local, aucun réseau) : répond comme un juge (bloc d'items pour l'ancien protocole,
    comparaison valide qui choisit toujours la première fiche pour le v2) ou rend, au n-ième appel, l'action n du scénario
    ({"type": "repondre" | "refus" | "ligne" | "rien", "code": …, "ligne": {…}, "stderr": …, "modele_servi": …})."""
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".py")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(JUGE_FACTICE.replace("SCENARIO", repr(scenario or [])).replace("ITEMS", repr(list(items)))
                .replace("COUT", repr(cout)).replace("MODELE", repr(modele)))
    return [sys.executable, "-I", "-B", chemin]


class _CheminReel(unittest.TestCase):
    """Le mode réel jusqu'aux relais, avec des commandes externes factices (scripts locaux) : aucune clé, aucun réseau."""

    def setUp(self):
        import aides_v54 as A54
        import aides_v56 as A56
        self.A56 = A56
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = unittest.mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", os.defpath), "HOME": self.tmp}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.prereg_dir = os.path.join(self.tmp, "prereg")
        os.makedirs(self.prereg_dir)
        p = unittest.mock.patch.object(lanceur, "DOSSIER_PREREG", self.prereg_dir)
        p.start()
        self.addCleanup(p.stop)
        conf = A56.configuration(self.tmp)
        conf["plafonds_session"]["juge"] = 1.0
        objet, _ = J.lot_reel_substitution(3)
        conf["pieces"]["question_course_2"] = A56.ecrire(os.path.join(self.tmp, "p", "question.md"), J.QUESTION_SUBSTITUTION)
        conf["pieces"]["lot_reel_juges_idees_v2"] = A56.ecrire(os.path.join(self.tmp, "p", "lot.json"), json.dumps(objet, ensure_ascii=False))
        self.conf = conf
        self.fournisseurs()
        self.registre = A54.registre_go(self.tmp, A54.ligne_go("GO-2026-11-02-09", "60 USD", perimetre="juges v2"),
                                        A54.ligne_go("GO-2026-11-02-10", "60 USD", perimetre="juges v2"),
                                        A54.ligne_go("GO-2026-11-02-11", "25 USD", perimetre="juges v2"))
        self.sortie = os.path.join(self.tmp, "sortie")

    def fournisseurs(self, scenario_a=None, scenario_b=None):
        items = self.conf["items_juge"]
        self.conf["fournisseurs"] = {
            "argon": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                      "commande": commande_juge_factice(os.path.join(self.tmp, "cmd"), "argon", "gemini-4-argon", items, scenario_a)
                      + ["--registre", "{REGISTRE}", "--plafond-cumule-usd", "1"]},
            "astra": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                      "commande": commande_juge_factice(os.path.join(self.tmp, "cmd"), "astra", "gpt-6-astra", items, scenario_b)}}
        for nom in ("argon", "astra"):
            c = os.path.join(self.tmp, "cmd", nom + ".compte")
            if os.path.exists(c):
                os.remove(c)
        self.chemin_conf = os.path.join(self.tmp, "conf.json")
        with open(self.chemin_conf, "w", encoding="utf-8") as f:
            json.dump(self.conf, f, ensure_ascii=False)
        self.prereg = os.path.join(self.prereg_dir, "preenregistrement-juges-idees-v2-v1.md")
        for x in (self.prereg, self.prereg + ".sha256"):
            if os.path.exists(x):
                os.remove(x)
        ecrire_scelle(self.prereg, texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf)))

    def argv(self, *plus, prereg=None, conf=None, go="GO-2026-11-02-09"):
        return [self.sortie, "--preenregistrement", prereg or self.prereg, "--configuration", conf or self.chemin_conf, "--moteur", "reel",
                "--confirmer-moteur-reel", "--registre-go", self.registre, "--go", go, *plus]

    def ecrire_prereg(self, nom, texte, sceller=True, dossier=None):
        chemin = os.path.join(dossier or self.prereg_dir, nom)
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        if sceller:
            ecrire_scelle(chemin, texte)
        else:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        return chemin

    def lancer(self, argv):
        with unittest.mock.patch("sys.stderr", new_callable=io.StringIO) as err, \
                unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            code = lanceur.principal(argv)
        return code, err.getvalue(), out.getvalue()

    def lire(self, cle):
        with open(os.path.join(self.sortie, lanceur.SORTIES[cle]), encoding="utf-8") as f:
            return json.load(f)

    def nettoyer_sessions(self):
        m = self.lire("manifeste")
        self.addCleanup(shutil.rmtree, m["dossier_des_sessions"], True)
        return m


class LanceurCheminReel(_CheminReel):
    def test_cas_sain_verifier_seulement_aucune_ecriture(self):
        code, err, out = self.lancer(self.argv("--verifier-seulement"))
        self.assertEqual(code, 0, err)
        self.assertFalse(os.path.exists(self.sortie))
        rapport = json.loads(out)
        self.assertEqual({k: v["plafond_usd"] for k, v in rapport["configuration"]["accuses_plafond"].items()},
                         {"juge-a": 24.0, "juge-b": 36.0})

    def test_artefacts_du_chemin_reel(self):
        sha = sha256_fichier(self.chemin_conf)
        autre_conf = os.path.join(self.tmp, "conf-autre.json")
        with open(autre_conf, "w", encoding="utf-8") as f:
            json.dump(dict(self.conf, note="autre"), f)
        faux_code = {r: sha256_fichier(os.path.join(RACINE, r)) for r in lanceur.FICHIERS_GELES}
        faux_code["pole/juges_idees_v2.py"] = "0" * 64
        moins_un = {r: h for r, h in faux_code.items() if r != "pole/outils.py"}
        moins_un["pole/juges_idees_v2.py"] = sha256_fichier(os.path.join(RACINE, "pole/juges_idees_v2.py"))
        juge_claude = "etiquette=juge-b, fournisseur=opus, modele=claude-opus-5-5, famille=claude, prix_usd=0.5, secondes=10-120"
        juge_sans_relais = "etiquette=juge-b, fournisseur=autre, modele=gpt-6-astra, famille=gpt, prix_usd=0.5, secondes=10-120"
        meme_relais = "etiquette=juge-b, fournisseur=argon, modele=gpt-6-astra, famille=gpt, prix_usd=0.5, secondes=10-120"
        b_cher = "etiquette=juge-b, fournisseur=astra, modele=gpt-6-astra, famille=gpt, prix_usd=0.55, secondes=10-120"
        b_lent = "etiquette=juge-b, fournisseur=astra, modele=gpt-6-astra, famille=gpt, prix_usd=0.5, secondes=10-3000"
        txt = lambda **kw: texte_preenregistrement(conf_sha=sha, **kw)  # noqa: E731
        cas = {
            "brouillon": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-brouillon2.md", txt())), "pas"),
            "bon nom hors du dossier fixé": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v2.md", txt(), dossier=os.path.join(self.tmp, "ailleurs"))), "pas"),
            "non scellé": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v3.md", txt(), sceller=False)), "non scellé"),
            "marqueur restant": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v4.md",
                                                                     txt(marqueur="Épreuve : <<EPREUVE_ASTRA_8807>>"))), "marqueur"),
            "code différent": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v5.md", txt(empreintes=faux_code))),
                               "code différent"),
            "fermeture incomplète": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v6.md",
                                                                         txt(empreintes=moins_un))), "fermeture"),
            "clé de plan manquante": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v7.md",
                                                                          txt(sans="duree_max_h"))), "clés"),
            "plafond au-dessus de 60": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v8.md",
                                                                            txt(plafond="61", parts=("24", "37")))), "hors de ]0"),
            "valeur fixe différente du code": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v9.md", txt(remplace={"degre": "4"}))), "le code gelé dit"),
            "politique du relais différente": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v10.md", txt(remplace={"politique_relais": "aucune"}))), "le code gelé dit"),
            "parts au-dessus du plafond": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v11.md",
                                                                               txt(parts=("30", "31")))), "parts"),
            "durée maximale nulle": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v12.md",
                                                                         txt(remplace={"duree_max_h": "0"}))), "duree_max_h > 0"),
            "juges sur le même relais": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v13.md",
                                                                             txt(juge_b=meme_relais))), "plan-gele : juges A et B"),
            "part sous le devis requis": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v14.md",
                                                                              txt(parts=("40", "20")))), "devis"),
            "durée haute au-dessus de la durée maximale": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v15.md", txt(juge_b=b_lent, remplace={"duree_max_h": "48"}))), "durée haute"),
            "budget par appel sous deux fois le prix de plan": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v16.md", txt(juge_b=b_cher))), "plafonds_session.juge"),
            "consigne v2 autre": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v17.md", txt(consigne="e" * 64))),
                                  "consigne"),
            "matériaux autres": (self.argv(prereg=self.ecrire_prereg("preenregistrement-juges-idees-v2-v18.md",
                                                                     txt(materiaux_sha="f" * 64))), "matériaux"),
            "juge de la famille des gabarits": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v19.md", txt(juge_b=juge_claude))), "plan-gele : juge juge-b de la famille"),
            "relais du juge absent": (self.argv(prereg=self.ecrire_prereg(
                "preenregistrement-juges-idees-v2-v20.md", txt(juge_b=juge_sans_relais))), "relais"),
            "autre configuration": (self.argv(conf=autre_conf), "empreinte"),
            "GO autre que celui du texte": (self.argv(go="GO-2026-11-02-10"), "nomme"),
            "option de plan en réel": (self.argv("--plafond-usd", "10"), "options refusées"),
            "graine en réel": (self.argv("--graine", "7"), "graine"),
        }
        for nom, (argv, motif) in cas.items():
            with self.subTest(cas=nom):
                code, err, _ = self.lancer(argv + ["--verifier-seulement"])
                self.assertEqual(code, 2, err)
                self.assertIn(motif, err)
                self.assertFalse(os.path.exists(self.sortie))

    def test_artefacts_pieces_et_lot_reel(self):
        conf = copy.deepcopy(self.conf)
        conf["pieces"].pop("question_course_2")
        sans_piece = os.path.join(self.tmp, "conf-sans-piece.json")
        with open(sans_piece, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        p1 = self.ecrire_prereg("preenregistrement-juges-idees-v2-v30.md", texte_preenregistrement(conf_sha=sha256_fichier(sans_piece)))
        code, err, _ = self.lancer(self.argv("--verifier-seulement", prereg=p1, conf=sans_piece))
        self.assertEqual(code, 2, err)
        self.assertIn("absente", err)
        objet, _ = J.lot_reel_substitution(3)
        objet["fiches"][0]["contenu"]["titre"] = "Fiche qui nomme un témoin planté"
        conf = copy.deepcopy(self.conf)
        conf["pieces"]["lot_reel_juges_idees_v2"] = self.A56.ecrire(os.path.join(self.tmp, "p2", "lot.json"),
                                                                    json.dumps(objet, ensure_ascii=False))
        lot_a4 = os.path.join(self.tmp, "conf-lot-a4.json")
        with open(lot_a4, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        p2 = self.ecrire_prereg("preenregistrement-juges-idees-v2-v31.md", texte_preenregistrement(conf_sha=sha256_fichier(lot_a4)))
        code, err, _ = self.lancer(self.argv("--verifier-seulement", prereg=p2, conf=lot_a4))
        self.assertEqual(code, 2, err)
        self.assertIn("A4", err)
        self.assertIn("réelle", err)

    def test_artefacts_go_et_environnement(self):
        texte = texte_preenregistrement(conf_sha=sha256_fichier(self.chemin_conf), go="GO-2026-11-02-11")
        p = self.ecrire_prereg("preenregistrement-juges-idees-v2-v40.md", texte)
        code, err, _ = self.lancer(self.argv("--verifier-seulement", prereg=p, go="GO-2026-11-02-11"))
        self.assertEqual(code, 2)
        self.assertIn("pas exactement", err)
        with unittest.mock.patch.dict(os.environ, {"GH_TOKEN": "x"}):
            code, err, _ = self.lancer(self.argv("--verifier-seulement"))
        self.assertEqual(code, 2)
        self.assertIn("les relais tiennent les clés", err)  # la garde du lanceur, avant celle des adaptateurs
        self.assertFalse(os.path.exists(self.sortie))

    def test_course_reelle_factice_arretee_par_la_garde_de_validite(self):
        """Commande factice qui rend des comparaisons sans citation de fiche (citation vide) : l'ancien protocole est lu, les
        comparaisons v2 sont nulles ; la garde de validité arrête la phase décisive de A, donc la course (code 3, journal
        scellé, issue I0)."""
        self.fournisseurs(scenario_a=[{"type": "repondre"}] * 30 + [{"type": "ligne", "ligne": {
            "texte": "```json\n{\"comparaison\": {\"preferee\": \"F0\", \"critere\": \"verite\", \"citation_fiche\": \"\"}}\n```",
            "cout_usd": 0.001, "modele_servi": "gemini-4-argon"}}])
        code, err, _ = self.lancer(self.argv())
        self.assertEqual(code, 3, err)
        journal = self.lire("journal")
        self.nettoyer_sessions()
        self.assertEqual(len(journal["ancien"]), 30)
        self.assertTrue(all(e["valide"] for e in journal["ancien"]))
        self.assertEqual(len(journal["v2"]), 20)
        self.assertIn("ArretValidite", journal["arret"])
        self.assertEqual(self.lire("lecture")["issue"], "I0")

    def test_statuts_du_relais_par_la_vraie_commande_externe(self):
        """Par l'adaptateur réel (`AdaptateurCommandeExterneV56`) : code 4 au coût plancher puis code 3 au coût plancher → même
        appel repris après attente ; code 3 sans ligne (coût inconnu, plafond de session compté) → perte reprise en fin d'étape,
        hors du prix observé ; refus du modèle → réponse inexploitable ; autre modèle servi → arrêt A2 au premier appel."""
        plancher = {"texte": "", "cout_usd": 1e-6}
        self.fournisseurs(scenario_a=[{"type": "ligne", "ligne": plancher, "code": 4, "stderr": "429"},
                                      {"type": "ligne", "ligne": plancher, "code": 3, "stderr": "relais injoignable"},
                                      {"type": "repondre"}, {"type": "rien", "code": 3, "stderr": "interface"},
                                      {"type": "repondre"}, {"type": "refus"},
                                      {"type": "repondre", "modele_servi": "gemini-4-argon-lite"}])
        with unittest.mock.patch.object(J, "ATTENTES_RELAIS_S", (0.01, 0.01)):
            code, err, _ = self.lancer(self.argv())
        self.assertEqual(code, 3, err)
        journal = self.lire("journal")
        self.nettoyer_sessions()
        self.assertIn("ArretModeleServi", journal["arret"])
        self.assertEqual([a["genre"] for a in journal["attentes"]], ["quota", "relais"])
        self.assertEqual([(p["cause"], p["cout_inconnu"], p["definitive"]) for p in journal["pertes"]], [("relais", True, False)])
        self.assertEqual([e.get("genre") for e in journal["ancien"]], ["reponse", "reponse", "refus_modele"])
        self.assertEqual([e["valide"] for e in journal["ancien"]], [True, True, False])
        bilan = journal["compteur"]
        self.assertEqual(bilan["reponses_a_cout_connu"]["juge-a"], 3)
        self.assertEqual(bilan["cout_inconnu"]["juge-a"]["appels"], 1)
        self.assertAlmostEqual(bilan["cout_inconnu"]["juge-a"]["usd"], 1.0)


class LanceurCheminReelComplet(_CheminReel):
    def test_cas_sain_course_reelle_factice_complete(self):
        """Toute la course par les commandes factices (aucune panne) : phases jouées dans l'ordre, parts accusées 24 et 36 USD,
        entropie = empreinte du texte, dépense comptée par juge, sorties scellées (code 0)."""
        code, err, out = self.lancer(self.argv())
        self.assertEqual(code, 0, err)
        journal, m = self.lire("journal"), self.nettoyer_sessions()
        self.assertEqual(m["preenregistrement"]["sha256"], sha256_fichier(self.prereg))
        self.assertEqual(m["entropie_racine"], str(int(sha256_fichier(self.prereg), 16)))
        self.assertEqual({k: v["plafond_usd"] for k, v in m["configuration"]["accuses_plafond"].items()}, {"juge-a": 24.0, "juge-b": 36.0})
        self.assertEqual([p["phase"] for p in journal["phases"]], list(J.PHASES_V2))
        self.assertEqual(journal["pertes"], [])
        self.assertEqual(sum(1 for e in journal["ancien"] if e["phase"] == "sans-dossier-a"), 30)
        self.assertTrue(all(e["modele_servi"] in ("gemini-4-argon", "gpt-6-astra") for e in journal["ancien"] + journal["v2"]))
        lec = self.lire("lecture")
        self.assertFalse(lec["partielle"])
        self.assertFalse(lec["criteres"]["D5"]["tenu"])  # la commande factice choisit toujours la première fiche


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
