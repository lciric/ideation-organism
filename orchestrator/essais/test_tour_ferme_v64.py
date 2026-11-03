"""Essais de la v64 — cœur (`pole/tour_ferme_v64.py`), commande externe v64 (`pole/adaptateur_commande_v64.py`), évaluateur servi
(`pole/evaluateur_lois_v62.py`, inchangé), lecture gelée (`pole/lecture_tour_ferme_v63.py`, inchangée), lanceur
(`demonstrations/tour_ferme_v64.py`) et programme de lecture (`demonstrations/lire_tour_ferme_v64.py`).

Reprend les essais v63 (B7, B8, B9, C8 à C21 de la contre-lecture 2 ; I26 à I31 de la contre-lecture 3 ; mineurs 29, 30, 34, 35
et 37 ; brouillon 5 : borne de 0,80 USD, rôles des relais), portés sur le code v64, et ajoute ceux de la v64 — décision du directeur
du 3 novembre 2026 sur TF-02 (options (a) et (c)) et décision de Lazar sur la durée (R-1294) :
- **F, TF-02 (a)** : `CommandeCode4` (vraie commande locale en code 4 : « envoye » faux → « budget_depasse », coût 0, marqué ;
  artefacts : lecture inchangée), `EtageRienEnvoye` (l'adaptateur de l'étage v64 rend la session à l'étage ; artefacts : arrêt C13
  gardé, v63 qui arrêtait), `EtageV64CommandesReelles` (étage v5 avec de vraies commandes : carte jugée sur ce qu'elle a exécuté,
  témoin « non concluant », aucun arrêt ; artefact : commande v56 → `EtageInterrompu`), `CourseRienEnvoye` (course à blanc de bout
  en bout), `ProposeurRienEnvoye` (un proposeur arrête toujours la course), `CommandesV64` (remplacement des relais au lanceur) ;
- **G, barème prudent passé à l'étage** : `BaremeDesCommandes`, `VerificationPrealable`, `PrixPasseALEtage` (l. 468 de l'étage
  v5 active ; vérificateur contrôlé par l'adaptateur de l'étage) et `CheminReelVerifierSeulement` (barème absent → code 2) ;
- **H, durée 72 h (R-1294)** : `DureeR1294` (plan à 72 h accepté ; toute autre durée refusée en mode décisif) et
  `CheminReelVerifierSeulement.test_artefact_duree_24_h` ;
- **I, noms** : `CourseSaine` (relevé et manifeste v64), `Fermeture` et `FermetureEnCourse` (bloc gelé de 92 fichiers).
Les gardes 5 (plafond de l'étage), 13 (durée) et 14 (T2 à T5) — B10 — sont dans `essais/test_gardes_tour_ferme_v64.py`.

Chaque garde : un cas sain et un artefact (R5). Les courses passent par **le chemin réel** (`ProposeurAdaptateur`,
`AdaptateurEtageV64`) avec des doublures scriptées qui ne lisent que le texte servi ; elles sont jouées dans ce processus (lanceur
appelé par `principal`) pour que le banc de mutations les atteigne. Aucun réseau, aucun modèle ; les commandes « réelles » des essais
sont des scripts Python locaux."""

import ast
import contextlib
import dataclasses
import importlib.util
import io
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
for _chemin in (ICI, RACINE):
    if _chemin not in sys.path:
        sys.path.insert(0, _chemin)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import etage_entre_generations_v57 as E57  # noqa: E402
from pole import evaluateur_lois_v62 as EV  # noqa: E402
from pole import lecture_tour_ferme_v62 as L62  # noqa: E402
from pole import lecture_tour_ferme_v63 as L  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole import tests_de_mort_v5 as v5  # noqa: E402
from pole import adaptateur_commande_v64 as AC  # noqa: E402
from pole import tour_ferme_v63 as T63  # noqa: E402  (artefacts : la v63)
from pole import tour_ferme_v64 as T  # noqa: E402
from pole.adaptateurs import Resultat  # noqa: E402
from pole.adaptateurs_v56 import AdaptateurCommandeExterneV56  # noqa: E402
from pole.etage_entre_generations_v53 import projeter  # noqa: E402
from pole.fiches_v53 import preparer  # noqa: E402
from pole.outils import ecrire_json_scelle, ecrire_scelle, json_canonique, sha256_fichier  # noqa: E402
from pole.protocole_outils import section_servie  # noqa: E402


def _charger(nom, fichier):
    if nom in sys.modules:
        return sys.modules[nom]
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, "demonstrations", fichier))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nom] = m  # nommé sous « essais. » : le banc de mutations l'atteint
    spec.loader.exec_module(m)
    return m


LANCEUR = _charger("essais.lanceur_tour_ferme_v64", "tour_ferme_v64.py")
LECTEUR = _charger("essais.lecteur_tour_ferme_v64", "lire_tour_ferme_v64.py")
MONDE = A.charger_monde(RACINE)
DEC = {"d7": "archive_du_bras_reel", "d9": "mecanique"}
PETIT = ["--cartes-par-proposeur", "2", "--cartes-reference", "3", "--m-e-bh", "11", "--bac", "factice"]
COURT = ["--generations", "2", "--cartes-par-proposeur", "1", "--cartes-reference", "2", "--m-e-bh", "9", "--bac", "factice"]
MOTS_INTERDITS = ("témoin", "temoin", "ALEA", "COPIE", "kimi", "argon", "scripte", "W-", "G1-", "G2-", "G3-", "aleatoire", "recopie")
GO = "GO-2026-11-02-19"
LOI_REVUE = {"type": "si_sinon", "condition": {"indice": 1.0, "seuil": 0.0}, "si": MONDE["loi"], "sinon": MONDE["loi"]}  # I26


def courir(sortie, *opts):
    """Le lanceur, dans ce processus ; rend (code, sortie d'erreur)."""
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        code = LANCEUR.principal([sortie, "--etage", "1", *opts])
    return code, err.getvalue()


def rapport(sortie):
    with open(os.path.join(sortie, "tour-ferme-v1-etage1.json"), encoding="utf-8") as f:
        return json.load(f)


def rapport_ou_rien(sortie):
    return rapport(sortie) if os.path.isfile(os.path.join(sortie, "tour-ferme-v1-etage1.json")) else None


def consignes(sortie, role="experimentateur"):
    out = []
    for base, _, noms in os.walk(sortie):
        if "consigne.md" in noms and os.sep + role in base:
            with open(os.path.join(base, "consigne.md"), encoding="utf-8") as f:
                out.append(f.read())
    return out


def loi_au_hasard(rng, profondeur=0):
    t = rng.choice(T.TYPES_PERMIS if profondeur < 3 else ("softmax", "fixe"))
    if t == "fixe":
        return {"type": "fixe", "probas": [rng.choice([0.0, rng.random()]) for _ in range(2)] + [rng.random() + 0.1]}
    if t == "softmax":
        return {"type": "softmax", "poids": [[rng.uniform(-4, 4) for _ in range(2)] for _ in range(3)],
                "biais": [rng.uniform(-4, 4) for _ in range(3)]}
    if t == "par_sous_population":
        l = {"type": "par_sous_population", "lois": {"0": loi_au_hasard(rng, profondeur + 1)}}
        if rng.random() < 0.5:
            l["lois"]["1"] = loi_au_hasard(rng, profondeur + 1)
        else:
            l["defaut"] = loi_au_hasard(rng, profondeur + 1)
        return l
    if t == "melange":
        w = rng.random()
        return {"type": "melange", "composantes": [loi_au_hasard(rng, profondeur + 1), loi_au_hasard(rng, profondeur + 1)], "poids": [w, 1 - w]}
    if t == "si_sinon":
        c = {"sous_population": rng.randrange(2)} if rng.random() < 0.5 else {"indice": rng.randrange(2), "seuil": rng.uniform(-1, 1)}
        return {"type": "si_sinon", "condition": c, "si": loi_au_hasard(rng, profondeur + 1), "sinon": loi_au_hasard(rng, profondeur + 1)}
    l = {"type": "transformee", "base": loi_au_hasard(rng, profondeur + 1), "puissance": rng.uniform(0.2, 3.0),
         "inclinaison": [rng.uniform(-2, 2) for _ in range(3)]}
    if rng.random() < 0.5:
        l["melange_aveugle"] = {"lambda": rng.random(), "probas": [rng.random() for _ in range(3)]}
    if rng.random() < 0.5:
        l["oscillation"] = {"amplitude": rng.uniform(-2, 2), "frequence": rng.uniform(-3, 3), "trait": rng.randrange(2),
                            "issue": rng.randrange(3), "phase": rng.uniform(0, 3)}
    return l


class Tranche(unittest.TestCase):
    """Une tranche (celle de la v62, inchangée) dans un dossier temporaire (épisodes et évaluateur)."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v64-")
        self.addCleanup(shutil.rmtree, self.d, True)
        self.tranche = T.creer_tranche(self.d, MONDE, 5, "essai|v63")
        self.ep = os.path.join(self.d, "tranche", "episodes.csv")


class Course(unittest.TestCase):
    """Une ou plusieurs courses à blanc par le chemin réel, jouées une fois pour la classe : {nom: (code, err, rapport)}."""
    COURSES = {}

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v64-course-")
        cls.r = {}
        for nom, opts in cls.COURSES.items():
            s = os.path.join(cls.d, nom)
            code, err = courir(s, *opts)
            cls.r[nom] = (code, err, rapport_ou_rien(s))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, True)


# --- C8 (B7) : loi et évaluateur servis -------------------------------------------------------------------------------------


class EvaluateurDeReference(Tranche):
    def test_egal_a_selection_pari_sur_les_six_types(self):
        rng = random.Random(62)
        instances = sp.tirer_instances(rng, 60, 2)
        for _ in range(120):
            loi = loi_au_hasard(rng)
            self.assertIsNone(T.verifier_loi_servable(loi), loi)
            for x in instances:
                a, b = EV.proba(loi, x), sp.proba(loi, x, [], 0)
                self.assertLessEqual(max(abs(u - v) for u, v in zip(a, b)), 1e-12, loi)
        fixe = {"type": "fixe", "probas": [1.0, 0.0, 0.0]}  # plancher 1e-12
        self.assertEqual(EV.proba(fixe, instances[0]), sp.proba(fixe, instances[0], [], 0))

    def test_gains_egaux_au_contre_calcul_et_tranche_servie(self):
        self.assertIn(T.FICHIER_EVALUATEUR, self.tranche.fichiers)
        self.assertEqual(self.tranche.fichiers[T.FICHIER_EVALUATEUR]["sha256"], sha256_fichier(T.CHEMIN_EVALUATEUR))
        rng = random.Random(7)
        for _ in range(10):
            loi = loi_au_hasard(rng)
            g = EV.gains(loi, self.ep)
            self.assertLessEqual(abs(sum(g) / len(g) - T.statistique_hors_bac(loi, self.ep)), 1e-12)


class ServiceDeLaLoi(Tranche):
    def prereg(self, carte):
        fiche = preparer({k: carte[k] for k in A.CHAMPS_FICHE}, list(A.CHAMPS_FICHE), ident=carte["identifiant"],
                         case=("x", "y"), fournisseur="essai", passe=1)
        p, motif = v5.extraire_prereg_court(projeter(fiche, A.CORRESPONDANCE), self.tranche, 1, {})
        self.assertIsNone(motif)
        return p

    def test_sain_la_loi_arrive_par_le_preenregistrement_court(self):
        for loi in (MONDE["loi"], loi_au_hasard(random.Random(3))):
            p = self.prereg(T.carte_servie("F-000000000001", loi, "reel"))
            consigne = section_servie(v5.TITRE_SECTION_PREREG, p)
            lue, motif = T.lire_loi_de_la_consigne(consigne)
            self.assertIsNotNone(lue, f"C8 : loi absente du préenregistrement court ({motif})")
            self.assertEqual(json_canonique(lue), json_canonique(loi))
            self.assertIn(T.FICHIER_EVALUATEUR, [d["chemin"] for d in p["donnees"]])
            self.assertIn("pleine précision", p["test_de_mort"])
            r = T.AdaptateurExperimentateurScripte().lancer(v5.ROLE_EXPERIMENTATEUR, consigne, "/x/experimentateur/tour-001", 0.5, 2)
            self.assertIn("runpy.run_path", r.texte_final)

    def test_artefact_loi_non_servie_l_experimentateur_scripte_echoue(self):
        c = T.carte_servie("F-000000000002", MONDE["loi"], "reel")
        c["test_de_mort"] = dict(T.pr.TEST_DE_MORT)  # gabarit v61 : aucune loi
        consigne = section_servie(v5.TITRE_SECTION_PREREG, self.prereg(c))
        self.assertEqual(T.lire_loi_de_la_consigne(consigne)[0], None)
        r = T.AdaptateurExperimentateurScripte().lancer(v5.ROLE_EXPERIMENTATEUR, consigne, "/x/experimentateur/tour-001", 0.5, 2)
        self.assertNotIn("executer", r.texte_final)
        self.assertIn("fin", r.texte_final)

    def test_borne_de_taille(self):
        grosse = {"type": "melange", "composantes": [MONDE["loi"]] * 16, "poids": [1 / 16] * 16}
        self.assertGreater(len(json_canonique(grosse)), T.TAILLE_MAX_LOI_SERVIE)
        gabarit = len(T.texte_du_test({"type": "fixe", "probas": [0.1, 0.1, 0.1]})) - len(json_canonique({"type": "fixe", "probas": [0.1, 0.1, 0.1]}))
        self.assertLessEqual(gabarit + T.TAILLE_MAX_LOI_SERVIE, v5._v2.TAILLE_MAX_TEST)  # la plus grande loi servable tient dans le champ
        motif = T.verifier_loi_servable(grosse)
        self.assertIn("trop longue", motif or "")
        carte = T.carte_servie("F-000000000003", grosse, "recopie_melange")
        self.assertIsNone(T.garder(carte, DEC)[0])
        moyenne = {"type": "melange", "composantes": [MONDE["loi"]] * 8, "poids": [0.125] * 8}
        self.assertIsNone(T.verifier_loi_servable(moyenne))
        self.assertLessEqual(len(T.texte_du_test(moyenne)), v5._v2.TAILLE_MAX_TEST)
        self.assertIsNotNone(T.garder(T.carte_servie("F-000000000004", moyenne, "reel"), DEC)[0])


# --- C9 (B8) : grammaire servie et gabarit (garde 8) ---------------------------------------------------------------------------


class GrammaireServie(unittest.TestCase):
    def test_exemples_valides_et_contexte_servi(self):
        for t, g in T.GRAMMAIRE["types"].items():
            self.assertIsNone(T.verifier_loi_servable(g["exemple"], borne_softmax=T.BORNE_GABARIT), t)
            sp.valider_loi(g["exemple"], 3, 2)
            self.assertEqual(g["exemple"]["type"], t)
        self.assertEqual(set(T.GRAMMAIRE["types"]), set(T.TYPES_PERMIS))
        vue = T.bf.vue_pour_proposeur(T.bf.heritage_initial())
        ctx = T.contexte_du_proposeur(MONDE, vue, 5, "essai|c9")
        self.assertIn("grammaire", ctx["gabarit"], "C9 : grammaire absente du contexte servi")
        self.assertEqual(ctx["gabarit"]["grammaire"], json.loads(json.dumps(T.GRAMMAIRE)))
        self.assertIn("grammaire", T.CONSIGNE_PROPOSEUR)
        self.assertIn("entiers JSON", T.GRAMMAIRE["regles"], "I26 : la grammaire servie dit que les indices sont entiers")

    def test_le_proposeur_scripte_ecrit_depuis_la_grammaire_servie(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        vue = T.bf.vue_pour_proposeur(T.bf.heritage_initial())
        p = T.ProposeurAdaptateur("kimi-scripte", "kimi", T.AdaptateurProposeurScripte("kimi-scripte"), d, 0.0, "doublure")
        texte, _ = p.proposer(T.CONSIGNE_PROPOSEUR.format(n=3), T.contexte_du_proposeur(MONDE, vue, 5, "essai|c9"), "essai|c9")
        props, motif = T.extraire_propositions(texte)
        self.assertEqual((len(props), motif), (3, None))
        for i, prop in enumerate(props):
            c, m = T.completer_carte(prop, f"F-00000000000{i}")
            self.assertIsNone(m, f"C9 : grammaire non suivie : {m}")

    def test_artefacts_du_gabarit(self):
        v = MONDE["loi"]
        cas = {"clé en trop": dict(v, note="x"), "type hors grammaire": {"type": "calendrier", "probas": [[1, 1, 1]]},
               "sous-population manquante": {"type": "par_sous_population", "lois": {"0": v}},
               "indice hors traits": {"type": "si_sinon", "condition": {"indice": 2}, "si": v, "sinon": v},
               "inclinaison démesurée": {"type": "transformee", "base": v, "inclinaison": [0.0, 100.0, 0.0]},
               "condition inconnue": {"type": "si_sinon", "condition": {"indice": 0, "x": 1}, "si": v, "sinon": v}}
        for nom, loi in cas.items():
            self.assertIsNotNone(T.verifier_loi_servable(loi), nom)
            self.assertIsNone(T.garder(T.carte_servie("F-0000000000aa", loi, "aleatoire"), DEC)[0], nom)
        hors_borne = {"type": "softmax", "poids": [[4.5, 0.0], [0.0, 0.0], [0.0, 0.0]], "biais": [0.0, 0.0, 0.0]}
        c, m = T.completer_carte({"enonce": "e", "loi_predictive": hors_borne}, "F-0000000000bb")
        self.assertIsNone(c, "C9 : borne ±4 du gabarit non tenue")
        self.assertIn("[−4 ; 4]", m)
        self.assertIsNotNone(T.garder(T.carte_servie("F-0000000000cc", MONDE["fausses"]["S-F4"], "temoin"), DEC)[0])  # témoin à −4,1
        for art in ({"enonce": "e", "loi_predictive": v, "test_de_mort": {"seuil": "au moins 0"}}, {"enonce": "e"},
                    {"enonce": "x" * 401, "loi_predictive": v}, "texte"):
            c, m = T.completer_carte(art, "F-0000000000dd")
            self.assertIsNone(c, f"garde 8 : proposition hors gabarit acceptée : {art!r}"[:200])
        self.assertIn("clés en trop", T.completer_carte({"enonce": "e", "loi_predictive": v, "statistique": "x"}, "F-0000000000de")[1])


# --- I26 : indices entiers, jeu factice du gardien, aucune exception qui remonte ---------------------------------------------


class GardienEntiers(unittest.TestCase):
    """I26 (1) : gabarit et gardien exigent des indices entiers ; motif propre, jamais un plantage."""
    v = MONDE["loi"]

    def test_sain_indices_entiers_acceptes(self):
        v = self.v
        for loi in ({"type": "si_sinon", "condition": {"indice": 1, "seuil": 0.0}, "si": v, "sinon": v},
                    {"type": "si_sinon", "condition": {"indice": 0}, "si": v, "sinon": v},
                    {"type": "si_sinon", "condition": {"sous_population": 1}, "si": v, "sinon": v},
                    {"type": "transformee", "base": v, "oscillation": {"amplitude": 1.0, "frequence": 2.0, "trait": 1, "issue": 2}}):
            self.assertIsNone(T.verifier_loi_servable(loi, borne_softmax=T.BORNE_GABARIT), loi)
            self.assertIsNotNone(T.completer_carte({"enonce": "e", "loi_predictive": loi}, "F-000000000111")[0], loi)
            self.assertIsNotNone(T.garder(T.carte_servie("F-000000000112", loi, "reel"), DEC)[0], loi)

    def test_artefacts_indices_non_entiers_et_seuil_non_fini(self):
        v = self.v
        cas = {"indice 1.0 (loi de la contre-lecture 3)": (LOI_REVUE, "condition.indice entier"),
               "indice True": ({"type": "si_sinon", "condition": {"indice": True}, "si": v, "sinon": v}, "condition.indice entier"),
               "sous_population 1.0": ({"type": "si_sinon", "condition": {"sous_population": 1.0}, "si": v, "sinon": v},
                                       "condition.sous_population entier"),
               "trait 1.0 (déjà refusé par valider_loi)": ({"type": "transformee", "base": v, "oscillation": {
                   "amplitude": 1.0, "frequence": 1.0, "trait": 1.0, "issue": 0}}, "oscillation"),
               "trait True": ({"type": "transformee", "base": v, "oscillation": {"amplitude": 1.0, "frequence": 1.0, "trait": True,
                                                                                  "issue": 0}}, "oscillation.trait entier"),
               "issue True": ({"type": "transformee", "base": v, "oscillation": {"amplitude": 1.0, "frequence": 1.0, "trait": 0,
                                                                                  "issue": True}}, "oscillation.issue entier"),
               "seuil infini": ({"type": "si_sinon", "condition": {"indice": 1, "seuil": float("inf")}, "si": v, "sinon": v},
                                "condition.seuil fini"),
               "seuil NaN": ({"type": "si_sinon", "condition": {"indice": 1, "seuil": float("nan")}, "si": v, "sinon": v},
                             "condition.seuil fini")}
        for nom, (loi, motif) in cas.items():
            with self.subTest(cas=nom):
                m = T.verifier_loi_servable(loi)
                self.assertIn(motif, m or "", f"I26 ({nom}) : motif propre attendu, reçu {m!r}")
                c, mc = T.completer_carte({"enonce": "e", "loi_predictive": loi}, "F-000000000113")
                self.assertIsNone(c, f"I26 ({nom}) : gabarit du proposeur")
                self.assertIn(motif, mc)
        carte = T.carte_servie("F-000000000114", MONDE["loi"], "aleatoire")
        carte["loi_predictive"] = LOI_REVUE  # une carte de référence ou un témoin passeraient aussi par ce gardien
        passeport, motif = T.garder(carte, DEC)
        self.assertIsNone(passeport, "I26 : le gardien laisse passer l'indice 1.0")
        self.assertIn("condition.indice entier", motif)
        with self.assertRaises(TypeError):  # ce que le juge aurait levé (v62 : arrêt de la course payante)
            sp.proba(LOI_REVUE, {"z": [0.1, 0.2], "g": 0}, [], 0)


class GardienJeuFactice(unittest.TestCase):
    """I26 (2) : le gardien évalue chaque loi sur le jeu factice avant le juge ; toute exception ou probabilité anormale →
    refus motivé ; l'évaluateur servi doit rendre la même loi."""

    def test_sain(self):
        self.assertEqual(len(T.JEU_FACTICE_DU_GARDIEN), 98)
        rng = random.Random(63)
        lois = [g["exemple"] for g in T.GRAMMAIRE["types"].values()] + [loi_au_hasard(rng) for _ in range(150)]
        lois += [T.pr.loi_aleatoire(rng) for _ in range(30)]
        for loi in lois:
            self.assertIsNone(T.evaluer_sur_jeu_factice(loi), loi)
            self.assertIsNotNone(T.garder(T.carte_servie("F-000000000121", loi, "aleatoire"), DEC)[0], loi)
        for nom, _, c in T.temoins_du_monde(MONDE, 5, "x"):
            self.assertEqual(T.garder(c, DEC)[0] is None, nom == "T-MAL", nom)
        self.assertEqual(len(T.noeuds_de_la_loi({"type": "melange", "composantes": [MONDE["loi"], LOI_REVUE], "poids": [0.5, 0.5]})), 5)

    def test_artefacts_lois_que_le_juge_ne_sait_pas_evaluer(self):
        v = MONDE["loi"]
        cos_infini = {"type": "transformee", "base": v, "oscillation": {"amplitude": 1.0, "frequence": 1e308, "trait": 0, "issue": 0}}
        somme_infinie = {"type": "fixe", "probas": [1e308, 1e308, 1e308]}
        for nom, loi, motif in (("cos(inf) : math domain error", cos_infini, "loi non évaluable"),
                                ("probabilités nulles (somme infinie)", somme_infinie, "hors du simplexe")):
            with self.subTest(cas=nom):
                self.assertIsNone(T.verifier_loi_servable(loi), "la grammaire seule ne voit pas ce cas (il passe valider_loi)")
                self.assertIn(motif, T.evaluer_sur_jeu_factice(loi) or "")
                passeport, m = T.garder(T.carte_servie("F-000000000122", loi, "reel"), DEC)
                self.assertIsNone(passeport, f"I26 : le gardien laisse passer une loi que le juge ne sait pas évaluer ({nom})")
                self.assertIn("jeu factice du gardien", m)
        self.assertIn("TypeError", T.evaluer_sur_jeu_factice(LOI_REVUE) or "")

    def test_artefact_evaluateur_servi_ecarte(self):
        vrai = EV.proba

        def decale(loi, instance):
            p = vrai(loi, instance)
            return [p[0] + 1e-6, p[1] - 1e-6, p[2]]

        with unittest.mock.patch.object(EV, "proba", decale):
            m = T.evaluer_sur_jeu_factice(MONDE["loi"])
        self.assertIn("l'évaluateur servi s'écarte", m or "", "I26 : écart de l'évaluateur servi non vu au gardien")
        self.assertIsNone(T.evaluer_sur_jeu_factice(MONDE["loi"]))


class AucuneExceptionQuiRemonte(unittest.TestCase):
    """I26 (3) : gabarit, gardien et extraction rendent un refus motivé, jamais une exception (v62 : arrêt de course)."""

    def test_entier_demesure_et_imbrication(self):
        v = MONDE["loi"]
        geant = {"type": "si_sinon", "condition": {"indice": 1, "seuil": 10 ** 400}, "si": v, "sinon": v}  # JSON valide
        m = T.verifier_loi_servable(geant)
        self.assertIsNotNone(m)
        self.assertIn("non vérifiable", m, "I26 : la vérification a levé au lieu de refuser")
        self.assertIsNone(T.completer_carte({"enonce": "e", "loi_predictive": geant}, "F-000000000131")[0])
        profond = v
        for _ in range(3000):
            profond = {"type": "transformee", "base": profond}
        self.assertIsNotNone(T.verifier_loi_servable(profond))
        props, motif = T.extraire_propositions("```json\n" + "[" * 100000 + "\n```")
        self.assertEqual((props, motif), ([], "réponse illisible (JSON)"), "I26 : réponse trop imbriquée")

    def test_carte_avec_nan_au_gardien(self):
        v = MONDE["loi"]
        carte = T.carte_servie("F-000000000132", v, "aleatoire")
        carte["loi_predictive"] = {"type": "si_sinon", "condition": {"indice": 1, "seuil": float("nan")}, "si": v, "sinon": v}
        passeport, motif = T.garder(carte, DEC)  # A.garder lève sur l'empreinte (JSON sans NaN) : refus motivé
        self.assertIsNone(passeport)
        self.assertIn("non vérifiable", motif)


class CourseIndiceFlottant(Course):
    """I26 de bout en bout : un proposeur réel qui écrit `indice: 1.0` (ou un seuil infini) n'arrête plus la course."""
    COURSES = {"indice": ["--a-blanc", "--graine", "11", "--scenario-proposeur", "indice_flottant", *COURT],
               "infini": ["--a-blanc", "--graine", "11", "--scenario-proposeur", "seuil_infini", *COURT]}

    def test_course_au_bout_carte_refusee_au_gabarit(self):
        for nom, motif in (("indice", "condition.indice entier"), ("infini", "condition.seuil fini")):
            code, err, r = self.r[nom]
            self.assertEqual(code, 0, f"I26 ({nom}) : la course s'arrête sur une loi plausible : {err[-800:]}")
            rel = r["releve"]
            self.assertIsNone(rel["arret"])
            refus = [c for c in rel["cartes"] if c["bras"] == "reel" and not c["temoin"] and c["gardien"] == "refuse"]
            self.assertEqual(len(refus), 4, (nom, [c.get("motif") for c in rel["cartes"] if c["gardien"] == "refuse"]))
            self.assertTrue(all(motif in c["motif"] for c in refus), [c["motif"] for c in refus])


# --- C15 (I15) : étage servi à l'aveugle -------------------------------------------------------------------------------------


class Aveugle(unittest.TestCase):
    def test_identifiants_opaques_et_titres_neutres(self):
        t = T.temoins_du_monde(MONDE, 5, "x")
        self.assertEqual([n for n, _, _ in t], list(T.TEMOINS))
        for _, reel, c in t:
            self.assertRegex(c["identifiant"], r"^F-[0-9a-f]{12}$", "C15 : identifiant servi non opaque")
            self.assertNotEqual(c["identifiant"], reel)
            self.assertEqual((c["titre"], c["hypothese"]), (T.TITRE_NEUTRE, T.HYPOTHESE_NEUTRE))
        self.assertRegex(T.identifiant_opaque(5, "x", "G1-kimi-01"), r"^F-[0-9a-f]{12}$", "C15")
        self.assertNotIn("statistique", dict((n, c) for n, _, c in t)["T-MAL"]["test_de_mort"])
        self.assertIn("au moins 2,0", dict((n, c) for n, _, c in t)["T-ELIM"]["test_de_mort"]["seuil"])


# --- garde 7 (I31) : témoins jamais retenus ni servis ---------------------------------------------------------------------------


class Garde7(unittest.TestCase):
    def test_temoin_jamais_dans_archive_ni_vue(self):
        h = {"generation_lue": 1, "bilan_sha256": "a" * 64, "retenues": ["F-000000000001"], "archive": {"F-000000000001": MONDE["loi"]},
             "empreintes_lues": {}}
        T.exiger_sans_temoin(h, {"W-abc", "F-0000000000ff"})
        for intrus in ("W-abc", "F-0000000000ff"):  # identifiant réel ou servi d'un témoin
            h2 = dict(h, archive=dict(h["archive"], **{intrus: MONDE["loi"]}))
            with self.assertRaises(T.TemoinRetenu):
                T.exiger_sans_temoin(h2, {"W-abc", "F-0000000000ff"})


class Garde7Selection(unittest.TestCase):
    """I31 : un témoin entré dans la sélection d'une génération (injecté dans la sélection v57 de l'étage des cartes) →
    `TemoinRetenu` → arrêt scellé (code 3) ; même course sans injection : code 0, aucun témoin dans aucune sélection."""

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v64-g7-")
        temoins = set()
        for b in T.BRAS_ETAGE1:
            for g in (1, 2):
                temoins |= {c["identifiant"] for _, _, c in T.temoins_du_monde(MONDE, 11, f"{T.VERSION}|etage=1|bras={b}|generation={g}")}
        cls.injections = []
        vraie = E57.selection_entre_generations

        def injecter(resume):
            sel = vraie(resume)
            ids = {r.get("identifiant_auteur") for r in resume.get("par_fiche") or []}
            if not cls.injections and ids and not ids & temoins:  # premier étage de cartes : les témoins y entrent
                sel = dict(sel, retenues=list(sel["retenues"]) + sorted(temoins))  # dont ceux de cette génération
                cls.injections.append(len(temoins))
            return sel

        with unittest.mock.patch.object(E57, "selection_entre_generations", injecter):
            cls.art = courir(os.path.join(cls.d, "artefact"), "--a-blanc", "--graine", "11", *COURT)
        cls.sain = courir(os.path.join(cls.d, "sain"), "--a-blanc", "--graine", "11", *COURT)
        cls.r_art, cls.r_sain = rapport_ou_rien(os.path.join(cls.d, "artefact")), rapport_ou_rien(os.path.join(cls.d, "sain"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, True)

    def test_temoin_dans_la_selection_arrete_la_course(self):
        self.assertEqual(len(self.injections), 1, "essai : aucune injection faite (aucun étage de cartes ?)")
        self.assertEqual(self.art[0], 3, f"garde 7 (sélection) : témoin retenu sans arrêt : {self.art[1][-600:]}")
        self.assertIn("témoin dans la sélection", self.r_art["arret"])
        self.assertEqual(L.lire_tour_etage_1(self.r_art["releve"])["etage_1"]["n1"], "arret")

    def test_sain_aucun_temoin_dans_les_selections(self):
        self.assertEqual(self.sain[0], 0, self.sain[1][-600:])
        temoins = {c["identifiant_servi"] for c in self.r_sain["releve"]["cartes"] if c["temoin"]}
        for l in self.r_sain["journal"]:
            if l["evenement"] == "generation":
                self.assertFalse(set(l["retenues"]) & temoins)


class Garde8Course(Course):
    """I31 : garde 8 de bout en bout — un proposeur qui porte son test de mort voit chaque proposition refusée au gabarit,
    sans arrêt ; les deux bras de référence jouent."""
    COURSES = {"hors": ["--a-blanc", "--graine", "11", "--scenario-proposeur", "hors_gabarit", *COURT]}

    def test_propositions_hors_gabarit_refusees(self):
        code, err, r = self.r["hors"]
        self.assertEqual(code, 0, err[-800:])
        reel = [c for c in r["releve"]["cartes"] if c["bras"] == "reel" and not c["temoin"]]
        self.assertEqual(len(reel), 4)
        self.assertTrue(all(c["gardien"] == "refuse" and "clés en trop" in c["motif"] for c in reel), [c.get("motif") for c in reel])
        alea = [c for c in r["releve"]["cartes"] if c["bras"] == "aleatoire" and not c["temoin"]]
        self.assertTrue(alea and all(c["gardien"] == "passe" for c in alea))


class Garde9(unittest.TestCase):
    """I31 : familles séparées — même famille → refus avant toute session (code 2, rien écrit) ; familles distinctes : la
    course joue (CourseSaine)."""

    def test_sain_et_artefact(self):
        T.exiger_familles_separees(("e", "kimi"), ("v", "argon"))
        for exp, ver in ((("e", "kimi"), ("v", "kimi")), (("e", ""), ("v", "argon"))):
            with self.assertRaises(T.FamillesNonSeparees):
                T.exiger_familles_separees(exp, ver)
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        code, err = courir(os.path.join(d, "s"), "--a-blanc", "--graine", "7", "--familles-a-blanc", "a,a", *COURT)
        self.assertEqual(code, 2)
        self.assertIn("familles non séparées", err)
        self.assertFalse(os.path.exists(os.path.join(d, "s")))


# --- C12 (I10) : proposeur en échec, C13 (I12) : parts des relais ; I30 : borne par carte --------------------------------------


class AdaptateurFaux:
    def __init__(self, r):
        self.r = r

    def lancer(self, role, texte, dossier, budget_usd, max_tours, modele=None):
        return self.r


class ProposeurChemin(unittest.TestCase):
    def proposeur(self, r):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        return T.ProposeurAdaptateur("kimi", "kimi", AdaptateurFaux(r), d, 0.1, "kimi-k3")

    def test_sain_et_artefacts(self):
        texte, cout = self.proposeur(Resultat("```json\n[]\n```", [], 0.02, "ok", modele_servi="kimi-k3")).proposer("c", {}, "t")
        self.assertEqual((texte, cout), ("```json\n[]\n```", 0.02))
        refus = {"motif": "autre", "modele_demande": "kimi-k3", "modele_servi": "autre"}
        for r in (Resultat("", [], 0.01, "refus", "refus (R-764)", refus=refus), Resultat("", [], 0.01, "erreur", "panne"),
                  Resultat("x", [], 0.01, "ok", modele_servi="autre-modele"), Resultat("", [], 0.1, "budget_depasse")):
            with self.assertRaises(T.ArretTour) as e:
                self.proposeur(r).proposer("c", {}, "t")
            self.assertGreater(e.exception.cout, 0.0)


class PartsDesRelais(unittest.TestCase):
    def test_compteur(self):
        c = T.Compteur(15.0, 3600.0, {"kimi": 12.0, "argon": 3.0})
        c.ajouter(2.9, "tests_de_mort", "argon")
        with self.assertRaises(T.ArretTour):
            c.ajouter(0.2, "tests_de_mort", "argon")
        c2 = T.Compteur(15.0, 3600.0, {"kimi": 12.0, "argon": 3.0})
        c2.ajouter(9.0, "proposeur", "kimi")
        c2.verifier_parts_avant_etage({"kimi": 2.5, "argon": 0.5})
        with self.assertRaises(T.ArretTour):
            c2.verifier_parts_avant_etage({"kimi": 3.5, "argon": 0.5})

    def test_budget_depasse_d_un_relais(self):
        ok = Resultat("x", [], 0.5, "budget_depasse")  # la fiche a dépensé son plafond : limite de l'étage, pas un arrêt
        e = T.AdaptateurEtageV64(AdaptateurFaux(ok), AdaptateurFaux(ok))
        self.assertIs(e.lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2), ok)
        relais = Resultat("", [], 0.0, "budget_depasse")  # 402 du relais avant toute dépense
        e = T.AdaptateurEtageV64(AdaptateurFaux(relais), AdaptateurFaux(ok))
        with self.assertRaises(T.ArretTour):
            e.lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2)
        e = T.AdaptateurEtageV64(AdaptateurFaux(ok), AdaptateurFaux(ok))
        e.parts = {"kimi": 0.4}
        with self.assertRaises(T.ArretTour):
            e.lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2)


class ReservationI30(unittest.TestCase):
    """I30 : avant un étage, le pire cas réservé est cartes × la borne par carte de chaque rôle (expérimentateur : 0,80 USD au
    brouillon 5, vérificateur : 0,1 USD), ni cartes × 0,5 USD (v62), ni cartes × 0,30 USD (brouillon 4)."""

    class Espion(T.Compteur):
        def verifier_parts_avant_etage(self, besoins):
            self.besoins = dict(besoins)
            raise RuntimeError("espion : arrêt avant l'étage")

    def test_pire_cas_calcule_avec_la_borne(self):
        self.assertEqual((T.BUDGET_EXPERIMENTATEUR_PAR_CARTE_USD, T.BUDGET_VERIFICATEUR_PAR_CARTE_USD), (0.80, 0.1),
                         "I30 (brouillon 5) : bornes par carte")
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        c = self.Espion(15.0, 3600.0, {"kimi": 12.0, "argon": 3.0})
        cartes = [T.carte_servie(f"F-00000000014{i}", MONDE["loi"], "reel") for i in range(3)]
        roles = {"experimentateur": ("e", "fa"), "verificateur": ("v", "fb"), "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
        with self.assertRaisesRegex(RuntimeError, "espion"):
            T.jouer_etage(os.path.join(d, "etage"), cartes, {}, MONDE, 5, "essai|i30", None, None, roles, c, [])
        self.assertAlmostEqual(c.besoins["kimi"], 2.4, msg="I30 : pire cas de l'expérimentateur ≠ 3 × 0,80 USD")
        self.assertAlmostEqual(c.besoins["argon"], 0.3)
        sain = T.Compteur(50.0, 3600.0, {"kimi": 2.4, "argon": 3.0})  # 2,4 USD couvre exactement 3 × 0,80 (permis)
        sain.verifier_parts_avant_etage(c.besoins)
        with self.assertRaises(T.ArretTour):
            T.Compteur(50.0, 3600.0, {"kimi": 2.3, "argon": 3.0}).verifier_parts_avant_etage(c.besoins)


# --- brouillon 5 : rôles joués par les relais (chemin réel) ------------------------------------------------------------------------


class RolesDesRelais(unittest.TestCase):
    """Brouillon 5 (R5) : les rôles que le tour fait jouer sont acceptés par les adaptateurs **réels** du pôle. Cas sain : commande
    externe v56 (une commande locale qui rend le rôle et le modèle reçus) pour le proposeur, l'expérimentateur et le vérificateur ;
    artefacts : Kimi par protocole (ne joue pas l'expérimentateur), adaptateur sans liste de rôles, rôle « proposeur » de la v61 à
    la v63 du brouillon 4, doublures sollicitées hors de leur rôle. Aucun réseau (commande locale, ouvreur factice jamais appelé)."""

    def commande(self):
        from pole.adaptateurs_v56 import AdaptateurCommandeExterneV56
        d = tempfile.mkdtemp(prefix="essai-v64-roles-")
        self.addCleanup(shutil.rmtree, d, True)
        chemin = os.path.join(d, "relais_factice.py")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("import json, os, sys\nsys.stdin.read()\nprint(json.dumps({'texte': 'role=' + os.environ.get('ROLE_POLE', ''), "
                    "'cout_usd': 0.001, 'modele_servi': os.environ.get('MODELE_DEMANDE_POLE', '')}))\n")
        return d, AdaptateurCommandeExterneV56([sys.executable, "-I", "-B", chemin], environnement={"PATH": os.defpath},
                                               exiger_modele_servi=True)

    def test_sain_commandes_externes(self):
        d, ext = self.commande()
        p = T.ProposeurAdaptateur("kimi", "kimi", ext, d, 0.05, "kimi-k3.1-pro")
        self.assertEqual(p.proposer("c", {}, "essai|roles"), ("role=proposeur_ideation", 0.001),
                         "brouillon 5 : rôle du proposeur refusé par la commande externe")
        etage = T.AdaptateurEtageV64(ext, ext, "kimi", "argon")
        for role in (v5.ROLE_EXPERIMENTATEUR, v5.ROLE_LECTEUR):
            dd = os.path.join(d, role, "tour-001")
            os.makedirs(dd)
            r = etage.lancer(role, "c", dd, 0.5, 2, modele="gemini-argon")
            self.assertEqual((r.statut, r.texte_brut, r.modele_servi), ("ok", "role=" + role, "gemini-argon"))
        argon = T.ProposeurAdaptateur("argon", "argon", ext, d, 0.05, "gemini-argon")
        self.assertTrue(T.exiger_roles_joues(T.paires_de_roles([p, argon], etage)))
        self.assertEqual([(x[0], x[2]) for x in T.paires_de_roles([p, argon], etage)],
                         [("kimi", "proposeur_ideation"), ("argon", "proposeur_ideation"), ("kimi", v5.ROLE_EXPERIMENTATEUR),
                          ("argon", v5.ROLE_LECTEUR)])

    def test_artefacts(self):
        from pole.adaptateur_kimi_v53 import AdaptateurKimiProtocole
        d, ext = self.commande()
        kp = AdaptateurKimiProtocole("http://127.0.0.1:9", modele="kimi-k3.1-pro", prix_entree=1.0, prix_sortie=1.0,
                                     max_sortie_jetons=10, sortie_min_jetons=1, delai_s=1.0, ouvreur=object())
        props = [T.ProposeurAdaptateur("kimi", "kimi", kp, d, 0.05, "kimi-k3.1-pro"), T.ProposeurAdaptateur("argon", "argon", ext, d, 0.05, "m")]
        with self.assertRaisesRegex(T.TourRefuse, "experimentateur_test", msg="brouillon 5 : Kimi par protocole accepté comme expérimentateur"):
            T.exiger_roles_joues(T.paires_de_roles(props, T.AdaptateurEtageV64(kp, ext, "kimi", "argon")))
        with self.assertRaises(ValueError):  # sans la garde : l'arrêt au premier étage de la course
            kp.lancer(v5.ROLE_EXPERIMENTATEUR, "c", d, 0.5, 2)

        class SansRoles:
            def lancer(self, *a, **k):
                raise AssertionError("jamais appelé")

        with self.assertRaisesRegex(T.TourRefuse, "rôles permis : None", msg="brouillon 5 : adaptateur sans liste de rôles accepté"):
            T.exiger_roles_joues([("argon", SansRoles(), T.ROLE_PROPOSEUR)])
        with self.assertRaisesRegex(T.TourRefuse, "« proposeur »", msg="brouillon 5 : rôle « proposeur » (v61 à v63 du brouillon 4) accepté"):
            T.exiger_roles_joues([("kimi", ext, "proposeur")])
        with self.assertRaises(ValueError):
            ext.lancer("proposeur", "c", d, 0.05, 1, modele="m")  # ce que la v63 du brouillon 4 faisait au premier appel réel
        for doublure, autre in ((T.AdaptateurProposeurScripte("x"), v5.ROLE_EXPERIMENTATEUR),
                                (T.AdaptateurExperimentateurScripte(), T.ROLE_PROPOSEUR), (T.AdaptateurVerificateurScripte(), "proposeur")):
            with self.subTest(doublure=type(doublure).__name__), self.assertRaises(ValueError):
                doublure.lancer(autre, "c", os.path.join(d, "tour-001"), 0.5, 2)


# --- C14 (I14) : pleine précision et contre-calcul ---------------------------------------------------------------------------


class PleinePrecision(Tranche):
    def resume(self, valeur):
        return {"par_fiche": [{"statut": "testée", "identifiant_auteur": "c", "verdict_noyau": {"valeur_noyau": valeur, "verdict": "survit"}}]}

    def test_evaluateur_en_pleine_precision_et_arrondi(self):
        sortie = os.path.join(self.d, "gains.csv")
        with contextlib.redirect_stdout(io.StringIO()):
            EV.ecrire_gains(MONDE["loi"], self.ep, sortie)
        with open(sortie, encoding="utf-8") as f:
            valeurs = [float(l.split(",")[1]) for l in f.read().splitlines()[1:]]
        exacte = T.statistique_hors_bac(MONDE["loi"], self.ep)
        self.assertLessEqual(abs(sum(valeurs) / len(valeurs) - exacte), 1e-12, "C14 : gains écrits sans la pleine précision")
        self.assertTrue(T.contre_calculer(self.resume(sum(valeurs) / len(valeurs)), {"c": MONDE["loi"]}, self.ep)["c"]["ok"])
        arrondie = sum(round(x, 4) for x in valeurs) / len(valeurs)  # comportement écrit : arrêt si l'écart dépasse 1e-6
        r = T.contre_calculer(self.resume(arrondie), {"c": MONDE["loi"]}, self.ep)["c"]
        self.assertEqual(r["ok"], abs(arrondie - exacte) <= T.TOLERANCE_CONTRE_CALCUL)
        self.assertFalse(T.contre_calculer(self.resume(exacte + 0.01), {"c": MONDE["loi"]}, self.ep)["c"]["ok"])

    def test_copie_de_tranche_verifiee(self):
        sha = self.tranche.fichiers["episodes.csv"]["sha256"]
        T.contre_calculer(self.resume(None), {"c": MONDE["loi"]}, self.ep, sha)
        with self.assertRaises(T.ArretTour):
            T.contre_calculer(self.resume(None), {"c": MONDE["loi"]}, self.ep, "0" * 64)


# --- C21 : moteur de l'étage ; I30 : borne par carte tenue par l'étage ; étage v64 de bout en bout ----------------------------


class EtageV64(Tranche):
    def jouer(self, moteur):
        roles = {"experimentateur": ("e", "fa"), "verificateur": ("v", "fb"), "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
        ad = T.AdaptateurEtageV64(T.AdaptateurExperimentateurScripte(), T.AdaptateurVerificateurScripte())
        carte = T.carte_servie("F-0000000000e1", MONDE["loi"], "reel")
        compteur = T.Compteur(1e9, 3600.0)
        return T.jouer_etage(os.path.join(self.d, moteur, "etage"), [carte], {carte["identifiant"]: MONDE["loi"]}, MONDE, 5, "essai|c21",
                             A.choisir_executeur("factice")[0], ad, roles, compteur, [], moteur=moteur, environnement=T.ENV_A_BLANC), ad

    def test_sain_simule_et_factice_refuse_au_moteur_reel(self):
        self.assertEqual((LANCEUR.moteur_de_l_etage(True), LANCEUR.moteur_de_l_etage(False)), ("claude-sdk", "simule"), "C21")
        (resume, _, _, _, cc), ad = self.jouer("simule")
        self.assertEqual(resume["comptes"]["survit"], 1)
        self.assertTrue(all(x["ok"] and not x["sans_objet"] for x in cc.values()))
        self.assertEqual(resume["quotas"]["memoire_mo"], 768)
        self.assertEqual(resume["quotas"]["budget_test_usd"], 0.80, "I30 : la borne par carte n'est pas passée à l'étage")
        self.assertEqual(resume["quotas"]["budget_lecteur_usd"], 0.1)
        self.assertTrue(all(a["budget_passe_usd"] <= 0.80 for a in ad.appels if a["role"] == v5.ROLE_EXPERIMENTATEUR))
        with self.assertRaises(Exception) as e:
            self.jouer("claude-sdk")
        self.assertIn("factice", str(e.exception))


# --- lanceur : plan de l'étage 1, garde 6 complète (C17), machine jetable (C11), monde (C20) ------------------------------


def texte_plan(**chg):
    p = {"generations_etage_1": 3, "cartes_par_proposeur": 6, "cartes_reference": 12, "m_e_bh_etage_1": 19, "plafond_etage_1_usd": 15,
         "plafond_kimi_usd": 12, "plafond_argon_usd": 3, "duree_etage_1_h": 72, "d7": "archive_du_bras_reel", "d9": "mecanique",
         "configuration_sha256": "a" * 64, "go": GO, "monde_sha256": MONDE["sha256"],
         "ordre_des_bras": "reel, recopie_melange, aleatoire"}
    p.update(chg)
    return LANCEUR.DEBUT_PLAN + "\n" + "\n".join(f"{k}: {v}" for k, v in p.items() if v is not None) + "\n" + LANCEUR.FIN_PLAN


def texte_scellable(marqueur_hors_zone=False, **plan):
    emp = "\n".join(f"{sha256_fichier(os.path.join(RACINE, r))}  {r}" for r in LANCEUR.FICHIERS_GELES)
    return ("# essai\n" + ("<<DECISION_D2>>\n" if marqueur_hors_zone else "") + LANCEUR.DEBUT_ZONE_2 + "\nétage 2 : <<CASE_T>> <<DECISION_D8>>\n"
            + LANCEUR.FIN_ZONE_2 + "\n" + texte_plan(**plan) + "\n" + LANCEUR.DEBUT_EMPREINTES + "\n" + emp + "\n" + LANCEUR.FIN_EMPREINTES + "\n")


class PlanEtage1(unittest.TestCase):
    def test_sain_et_artefacts(self):
        p = LANCEUR.lire_plan(texte_plan())
        self.assertEqual((p["decisions"], p["plafond_kimi_usd"], p["monde_sha256"], p["go"]), (DEC, 12.0, MONDE["sha256"], GO))
        for chg in ({"plafond_kimi_usd": 13}, {"d8": "predicteur_connu"}, {"monde_sha256": None}, {"d9": "aiguilleur"},
                    {"m_e_bh_etage_1": 11}, {"ordre_des_bras": "aleatoire, reel, recopie_melange"}, {"go": "oui"}):
            with self.assertRaises(T.TourRefuse, msg=str(chg)):
                LANCEUR.lire_plan(texte_plan(**chg))


class Garde6Complete(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v64-prereg-")
        self.addCleanup(shutil.rmtree, self.d, True)
        self.ancien = LANCEUR.DOSSIER_PREREG
        LANCEUR.DOSSIER_PREREG = self.d
        self.addCleanup(setattr, LANCEUR, "DOSSIER_PREREG", self.ancien)

    def ecrire(self, texte, nom="preenregistrement-tour-ferme-v1-v1.md"):
        p = os.path.join(self.d, nom)
        ecrire_scelle(p, texte)
        return p

    def test_cas_sain_complet_accepte(self):
        e, sha, gelees, plan = LANCEUR.lire_preenregistrement(self.ecrire(texte_scellable()), self.d)
        self.assertGreaterEqual(e, 2 ** 64)
        self.assertEqual(set(gelees), set(LANCEUR.FICHIERS_GELES))
        self.assertEqual(plan["plafond_etage_1_usd"], 15.0)

    def test_artefacts(self):
        p = self.ecrire(texte_scellable())
        with open(p, "a", encoding="utf-8") as f:
            f.write("ajout après scellement\n")
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(p, self.d)  # sceau faux
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(self.ecrire(texte_scellable(marqueur_hors_zone=True), "preenregistrement-tour-ferme-v1-v2.md"), self.d)
        r = LANCEUR.FICHIERS_GELES[3]
        faux = texte_scellable().replace(f"{sha256_fichier(os.path.join(RACINE, r))}  {r}", f"{'0' * 64}  {r}")
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(self.ecrire(faux, "preenregistrement-tour-ferme-v1-v3.md"), self.d)  # empreinte de code
        ouvert = texte_scellable().replace(LANCEUR.FIN_ZONE_2, "", 1)
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(self.ecrire(ouvert, "preenregistrement-tour-ferme-v1-v4.md"), self.d)  # zone ouverte
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(self.ecrire(texte_scellable(), "preenregistrement-tour-ferme-v1-brouillon5.md"), self.d)
        autre = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, autre, True)
        ecrire_scelle(os.path.join(autre, "preenregistrement-tour-ferme-v1-v1.md"), texte_scellable())
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(os.path.join(autre, "preenregistrement-tour-ferme-v1-v1.md"), self.d)  # hors du dossier
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(os.path.join(self.d, "preenregistrement-tour-ferme-v1-v1.md"))  # hors de prereg/ du dépôt
        manque = texte_scellable().replace(f"{sha256_fichier(os.path.join(RACINE, 'pole/ideation.py'))}  pole/ideation.py\n", "")
        with self.assertRaisesRegex(LANCEUR.PreenregistrementRefuse, "manquants"):  # I27 : bloc sans un module exécuté en course
            LANCEUR.lire_preenregistrement(self.ecrire(manque, "preenregistrement-tour-ferme-v1-v5.md"), self.d)
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.entropie_decisive("0" * 48 + "f" * 16)
        self.assertEqual(LANCEUR.entropie_decisive("f" * 64), int("f" * 64, 16))


class MachineJetable(unittest.TestCase):
    def test_sain_et_artefacts(self):
        env = {"PATH": "/usr/bin", "HOME": "/root", "POLE_MACHINE_JETABLE_V56": "1"}
        self.assertEqual(LANCEUR.exiger_machine_jetable_reel(env, {}), ())
        self.assertEqual(LANCEUR.exiger_machine_jetable_reel(dict(env, HTTPS_PROXY="x"),
                                                             {"etage_tests_de_mort": {"environnement_permis": ["HTTPS_PROXY"]}}), ("HTTPS_PROXY",))
        for mauvais in ({k: v for k, v in env.items() if k != "POLE_MACHINE_JETABLE_V56"}, dict(env, HTTPS_PROXY="x")):
            with self.assertRaises(T.TourRefuse):
                LANCEUR.exiger_machine_jetable_reel(mauvais, {})


class MondeGele(unittest.TestCase):
    def test_sain_et_artefact(self):
        self.assertTrue(LANCEUR.verifier_monde(MONDE, MONDE["sha256"]))
        with self.assertRaises(T.TourRefuse):
            LANCEUR.verifier_monde(MONDE, "0" * 64)
        ancien = LANCEUR.MONDE_SHA256_A_BLANC
        LANCEUR.MONDE_SHA256_A_BLANC = "0" * 64
        try:
            d = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, d, True)
            code, err = courir(os.path.join(d, "s"), "--a-blanc", "--graine", "7", *PETIT)
            self.assertEqual(code, 2)
            self.assertIn("monde planté", err)
        finally:
            LANCEUR.MONDE_SHA256_A_BLANC = ancien


class RefusAvantToutAppel(unittest.TestCase):
    def test_codes_2(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        s = os.path.join(d, "s")
        for opts in (["--a-blanc", "--bac", "factice"], ["--a-blanc", "--graine", "7", "--bac", "factice", "--familles-a-blanc", "a,a"],
                     ["--a-blanc", "--graine", str(2 ** 64), "--bac", "factice"],
                     ["--preenregistrement", "prereg/preenregistrement-tour-ferme-v1-brouillon3.md", "--bac", "reel"]):
            self.assertEqual(courir(s, *opts)[0], 2, opts)
            self.assertFalse(os.path.exists(s))
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(LANCEUR.principal([s, "--etage", "2", "--a-blanc", "--graine", "7", *COURT]), 2, "garde 12 : étage 2 lancé")
        self.assertIn("aucun étage 2", err.getvalue())
        self.assertFalse(os.path.exists(s))


# --- mineurs 34, 35, 37 : sonde du bac, chemin réel jusqu'à --verifier-seulement -------------------------------------------------


class SondeDuBac(unittest.TestCase):
    """Mineur 34 : la sonde du bac refusée ne laisse aucun dossier temporaire ; sonde réussie : dossier de l'identité dédiée."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="essai-v64-sonde-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.p = unittest.mock.patch.object(tempfile, "tempdir", self.tmp)
        self.p.start()
        self.addCleanup(self.p.stop)

    @unittest.skipUnless(os.geteuid() == 0, "le dossier de l'identité dédiée n'est créé que sous le superutilisateur")
    def test_sain_et_artefact(self):
        vraie = A.choisir_executeur

        def refus(bac, **kw):
            raise A.BacASableIndisponible("sonde en échec (essai)")

        with unittest.mock.patch.object(A, "choisir_executeur", refus), self.assertRaises(A.BacASableIndisponible):
            LANCEUR.preparer_bac("reel", 64097)
        self.assertEqual(os.listdir(self.tmp), [], "mineur 34 : la sonde refusée laisse son dossier temporaire")
        with unittest.mock.patch.object(A, "choisir_executeur", lambda bac, **kw: vraie("factice")):
            parent, fabrique = LANCEUR.preparer_bac("reel", 64097)
        self.assertTrue(parent and os.path.isdir(os.path.join(parent, "bac")) and os.path.dirname(parent) == os.path.realpath(self.tmp))
        shutil.rmtree(parent)


def preparer_chemin_reel(dossier, go_montant="15 USD", kimi_par_protocole=False, bareme=(10.0, 10.0), duree=72):
    """Texte scellé (dans `dossier/prereg`), configuration v56 d'essai (relais Kimi et Argon par commandes factices, budget
    15 USD) et registre de GO d'essai ; rend (argv sans --verifier-seulement, dossier prereg). Aucun réseau, aucune clé.
    `kimi_par_protocole` (brouillon 5, artefact) : Kimi déclaré `kimi_protocole` (adaptateur construit, jamais appelé).
    v64 : `bareme` (prix d'entrée de chaque commande, dollars par million de jetons ; None = clé absente, artefact ; la clé est
    portée aussi par l'entrée Kimi par protocole, inerte pour elle, pour que la garde des rôles soit seule à refuser cet artefact) et
    `duree` (plan du texte scellé ; 72 h gelées, R-1294)."""
    import aides_v54 as A54
    import aides_v56 as A56
    conf = A56.configuration(dossier)
    conf["budget"]["plafond_usd"], conf["budget"]["arret_etape_usd"] = 15.0, 14.0
    conf["fournisseurs"] = {
        "kimi": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                 "commande": A56.commande_factice(dossier, "kimi", {"texte": "x", "cout_usd": 0.001, "modele_servi": "kimi-k3.1-pro"})
                 + ["--registre", "{REGISTRE}"]} if not kimi_par_protocole else
                {"type": "kimi_protocole", "url_relais": "http://127.0.0.1:9", "modele": "kimi-k3.1-pro", "prix_entree": 0.6,
                 "prix_sortie": 2.5, "max_sortie_jetons": 4000, "sortie_min_jetons": 16, "delai_s": 60.0,
                 "porte_plafond": {"type": "commande", "commande": A56.porte_factice(dossier, "porte-kimi"), "delai_s": 10.0}},
        "argon": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                  "commande": A56.commande_factice(dossier, "argon", {"texte": "x", "cout_usd": 0.001, "modele_servi": "gemini-4-argon"})
                  + ["--registre", "{REGISTRE}", "--plafond-cumule-usd", "15"]}}
    for nom, prix in zip(("kimi", "argon"), bareme):  # aussi sur l'entrée Kimi par protocole (inerte pour elle) : la garde des
        if prix is not None:                          # rôles reste la seule à refuser l'artefact du brouillon 5
            conf["fournisseurs"][nom]["prix_entree_usd_par_million_jetons"] = prix
    chemin_conf = os.path.join(dossier, "conf.json")
    with open(chemin_conf, "w", encoding="utf-8") as f:
        json.dump(conf, f)
    dp = os.path.join(dossier, "prereg")
    os.makedirs(dp)
    pr = os.path.join(dp, "preenregistrement-tour-ferme-v1-v1.md")
    ecrire_scelle(pr, texte_scellable(configuration_sha256=sha256_fichier(chemin_conf), duree_etage_1_h=duree))
    reg = A54.registre_go(dossier, A54.ligne_go(GO, go_montant, perimetre="tour fermé, étage 1 (essai)"))
    argv = [os.path.join(dossier, "sortie"), "--etage", "1", "--preenregistrement", pr, "--configuration", chemin_conf, "--moteur", "reel",
            "--confirmer-moteur-reel", "--registre-go", reg, "--go", GO, "--bac", "reel", "--utilisateur-bac", "64097"]
    return argv, dp


class CheminReelVerifierSeulement(unittest.TestCase):
    """Mineurs 35 et 37 (garde 15 au lanceur, `--verifier-seulement`) : le chemin réel, texte scellé, configuration et registre
    de GO factices, environnement du processus remplacé, sonde du bac remplacée (aucun bwrap requis) ; rien n'est écrit, aucun
    dossier temporaire ne reste (mineur 34)."""
    ENV = {"PATH": os.environ.get("PATH", os.defpath), "POLE_MACHINE_JETABLE_V56": "1"}

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v64-reel-")
        self.addCleanup(shutil.rmtree, self.d, True)
        self.tmp = os.path.join(self.d, "tmp")
        os.makedirs(self.tmp)
        self.vraie = A.choisir_executeur

    def jouer(self, argv, env, sonde=None, verifier=True):
        sonde = sonde or (lambda bac, **kw: self.vraie("factice"))
        err = io.StringIO()
        with unittest.mock.patch.dict(os.environ, dict(env, HOME=self.d), clear=True), \
                unittest.mock.patch.object(LANCEUR, "DOSSIER_PREREG", self.dp), unittest.mock.patch.object(tempfile, "tempdir", self.tmp), \
                unittest.mock.patch.object(A, "choisir_executeur", sonde), contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(err):
            code = LANCEUR.principal(argv + (["--verifier-seulement"] if verifier else []))
        return code, out.getvalue(), err.getvalue()

    def test_sain_verification_conforme_rien_ecrit(self):
        argv, self.dp = preparer_chemin_reel(self.d)
        code, out, err = self.jouer(argv, self.ENV)
        self.assertEqual(code, 0, err[-1500:])
        self.assertIn('"verification": "conforme"', out)
        conf = json.loads(out)["configuration"]
        for n in ("kimi", "argon"):  # v64 : commandes externes v64 au chemin réel (TF-02 a) et barème lu (G)
            self.assertIn("lecture_code_4", conf["adaptateurs"][n], f"TF-02 (a) : relais {n} resté en commande externe v56")
            self.assertEqual(conf["bareme_des_commandes"][n]["prix_entree_usd_par_million_jetons"], 10.0)
        self.assertEqual(json.loads(out)["plan"]["duree_max_s"], 72 * 3600.0)
        self.assertFalse(os.path.exists(argv[0]), "mineur 37 : --verifier-seulement a écrit la sortie")
        self.assertEqual(os.listdir(self.tmp), [], "mineur 34 : dossiers temporaires restés après --verifier-seulement")

    def test_artefacts_machine_non_jetable(self):
        argv, self.dp = preparer_chemin_reel(self.d)
        for nom, env in (("variable de déclaration absente", {"PATH": self.ENV["PATH"]}),
                         ("variable hors de la liste blanche", dict(self.ENV, HTTPS_PROXY="http://x"))):
            with self.subTest(cas=nom):
                code, _, err = self.jouer(argv, env)
                self.assertEqual(code, 2, f"garde 15 (lanceur, chemin réel) : {nom} accepté")
                self.assertIn("machine jetable", err)
                self.assertFalse(os.path.exists(argv[0]))

    def test_artefact_go_d_un_autre_montant(self):
        argv, self.dp = preparer_chemin_reel(self.d, go_montant="16 USD")
        code, _, err = self.jouer(argv, self.ENV)
        self.assertEqual(code, 2)
        self.assertIn("pas exactement", err)

    def test_artefact_kimi_par_protocole(self):
        """Brouillon 5 : Kimi par protocole ne joue pas l'expérimentateur ; refus avant toute porte et tout appel (code 2) dès le
        passage `--verifier-seulement` (la même fonction, `roles_reels`, sert le lancement), rien écrit, aucun dossier temporaire
        resté. (Le lancement lui-même n'est pas joué ici : sous mutation, il tenterait le relais local factice.)"""
        argv, self.dp = preparer_chemin_reel(self.d, kimi_par_protocole=True)
        code, _, err = self.jouer(argv, self.ENV)
        self.assertEqual(code, 2, f"brouillon 5 (lanceur) : Kimi par protocole accepté ; sortie : {err[-600:]}")
        self.assertIn("rôle « experimentateur_test »", err)
        self.assertFalse(os.path.exists(argv[0]))
        self.assertEqual(os.listdir(self.tmp), [], "mineur 34 : un refus laisse un dossier temporaire")

    def test_artefact_bareme_absent(self):
        """G (R5) : configuration sans le prix d'entrée d'une commande → refus avant toute porte et tout appel (code 2), rien écrit,
        aucun dossier temporaire resté ; le barème n'a aucun défaut."""
        for i, (nom, bareme) in enumerate((("kimi", (None, 10.0)), ("argon", (10.0, None)), ("kimi nul", (0.0, 10.0)))):
            with self.subTest(cas=nom):
                d = os.path.join(self.d, f"b{i}")
                os.makedirs(d)
                argv, self.dp = preparer_chemin_reel(d, bareme=bareme)
                code, _, err = self.jouer(argv, self.ENV)
                self.assertEqual(code, 2, f"G : configuration sans barème acceptée ({nom}) ; sortie : {err[-600:]}")
                self.assertIn("prix_entree_usd_par_million_jetons", err)
                self.assertFalse(os.path.exists(argv[0]))
                self.assertEqual(os.listdir(self.tmp), [], "mineur 34 : un refus laisse un dossier temporaire")

    def test_artefact_duree_24_h(self):
        """H (R-1294, R5) : un texte scellé dont le plan porte 24 h (la valeur v63) est refusé en mode décisif (code 2), rien écrit."""
        argv, self.dp = preparer_chemin_reel(self.d, duree=24)
        code, _, err = self.jouer(argv, self.ENV)
        self.assertEqual(code, 2, f"H : durée de 24 h acceptée en mode décisif ; sortie : {err[-600:]}")
        self.assertIn("R-1294", err)
        self.assertFalse(os.path.exists(argv[0]))

    def test_sonde_refusee_rien_ne_reste(self):
        argv, self.dp = preparer_chemin_reel(self.d)

        def refus(bac, **kw):
            raise A.BacASableIndisponible("sonde en échec (essai)")

        for verifier in (True, False):  # sans --verifier-seulement : seul le refus retire le dossier des sessions
            with self.subTest(verifier_seulement=verifier):
                code, _, err = self.jouer(argv, self.ENV, refus, verifier)
                self.assertEqual(code, 2)
                self.assertIn("sonde en échec", err)
                self.assertEqual(os.listdir(self.tmp), [], "mineur 34 : un refus laisse le dossier du bac ou celui des sessions")
                self.assertFalse(os.path.exists(argv[0]))


# --- courses par le chemin réel (doublures branchées), dans ce processus ---------------------------------------------------------


class CourseSaine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v64-course-")
        cls.s = os.path.join(cls.d, "s")
        cls.code, cls.err = courir(cls.s, "--a-blanc", "--graine", "11", "--generations", "3", *PETIT)
        cls.r = rapport(cls.s) if cls.code == 0 else None

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, True)

    def test_tient_et_releve_complet(self):
        self.assertEqual(self.code, 0, self.err[-2000:])
        l = L.lire_etage1(self.r["releve"])
        self.assertEqual(l["issue_etage_1"], "tient", l["criteres"])
        rec = self.r["releve"]["recherche_loi_plantee"]
        self.assertEqual((rec["contextes_cherches"], rec["touches"], rec["lignes_de_tranche_dans_les_contextes"]), (6, [], []))
        self.assertIsInstance(self.r["releve"]["vd_distinctes"], dict)
        m = json.load(open(os.path.join(self.s, "manifeste.json")))
        self.assertEqual((m["moteur_etage"], set(m["code_sha256"])), ("simule", set(LANCEUR.FICHIERS_GELES)))
        self.assertEqual((m["version"], m["bornes_par_carte_usd"]["experimentateur"]), ("tour-ferme-v64", 0.80))
        self.assertEqual(self.r["releve"]["version"], "tour-ferme-v64")
        self.assertEqual((m["duree_etage_1_h_gelee"], m["plan"]["duree_max_s"]), (72.0, 72 * 3600.0), "H (R-1294)")
        self.assertEqual(m["prix_caractere_usd_etage"], {"kimi": None, "argon": None}, "G : contrôle inactif à blanc sans option, dit")

    def test_C8_chaque_consigne_porte_sa_loi_et_l_experimentateur_la_lit(self):
        cs = consignes(self.s)
        self.assertTrue(cs)
        for c in cs:
            self.assertIsNotNone(T.lire_loi_de_la_consigne(c)[0], "C8 : consigne sans loi")
        testees = [c for c in self.r["releve"]["cartes"] if c.get("verdict")]
        self.assertTrue(testees)
        self.assertFalse([c for c in testees if c["verdict"] == "non concluant"])
        self.assertTrue(all(c["contre_calcul_ok"] is True for c in testees))

    def test_C9_chaque_proposeur_recoit_la_grammaire(self):
        servis = [os.path.join(b, n) for b, _, ns in os.walk(os.path.join(self.s, "proposeurs")) for n in ns if n.startswith("servi-")]
        self.assertEqual(len(servis), 6)
        for p in servis:
            self.assertIn('"grammaire"', open(p, encoding="utf-8").read(), "C9 : grammaire non servie")
        reel = [c for c in self.r["releve"]["cartes"] if c["bras"] == "reel" and not c["temoin"]]
        self.assertTrue(reel and all(c["gardien"] == "passe" for c in reel))

    def test_C15_prereg_servi_a_l_aveugle(self):
        for role in ("experimentateur", "lecteur"):
            for c in consignes(self.s, role):
                prereg = A._section(c, v5.TITRE_SECTION_PREREG)
                corps = json.dumps({k: prereg[k] for k in ("fiche", "hypothese", "prediction", "metrique", "seuil", "test_de_mort")},
                                   ensure_ascii=False)
                self.assertRegex(prereg["fiche"]["identifiant_auteur"], r"^F-[0-9a-f]{12}$", "C15")
                self.assertEqual(prereg["fiche"]["nom"], T.TITRE_NEUTRE, "C15")
                for mot in MOTS_INTERDITS:
                    self.assertNotIn(mot, corps, f"C15 : « {mot} » servi à l'étage")

    def test_C19_recopie_contre_l_archive_reelle_de_g_moins_1(self):
        j = self.r["journal"]
        gen = {(l["bras"], l["generation"]): l for l in j if l["evenement"] == "generation"}
        jouees = [g for (b, g) in gen if b == "recopie_melange"]
        self.assertTrue(jouees, "la recopie n'a pas joué dans cette course d'essai")
        for g in jouees:
            self.assertEqual(gen[("recopie_melange", g)]["archive_de_jugement"], gen[("reel", g)]["archive_de_jugement"], "C19")
            lu = [l for l in j if l["evenement"] == "heritage-lu" and l["bras"] == "recopie_melange" and l["generation"] == g][0]
            self.assertEqual(lu["bilan_sha256"], gen[("reel", g - 1)]["bilan_sha256"], "C19")

    def test_C18_programme_de_lecture(self):
        lec = os.path.join(self.d, "lecture.json")
        sha = sha256_fichier(os.path.join(self.s, "tour-ferme-v1-etage1.json"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(LECTEUR.principal([self.s, lec, "--releve-sha256", sha]), 0)
            self.assertEqual(LECTEUR.principal([self.s, lec]), 2)  # jamais d'écrasement
            self.assertEqual(LECTEUR.principal([self.s, lec + "2", "--releve-sha256", "0" * 64]), 2)
        l = json.load(open(lec))
        self.assertTrue(os.path.isfile(lec + ".sha256"))
        self.assertEqual((l["etage_1"]["issue_etage_1"], l["releve"]["sha256"], l["lecteur"]), ("tient", sha, "lecture-tour-ferme-v63"))
        faux = os.path.join(self.d, "faux")
        shutil.copytree(self.s, faux)
        os.remove(os.path.join(faux, "tour-ferme-v1-etage1.json.sha256"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(LECTEUR.principal([faux, lec + "3"]), 2, "C18 : relevé non scellé lu")
        for i, version in enumerate(("tour-ferme-v62", "tour-ferme-v63")):  # un relevé d'un autre cœur n'est pas lu par le programme v64
            autre = os.path.join(self.d, f"autre-version-{i}")
            os.makedirs(autre)
            ecrire_json_scelle(os.path.join(autre, "tour-ferme-v1-etage1.json"),
                               dict(self.r, version=version, releve=dict(self.r["releve"], version=version)))
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                self.assertEqual(LECTEUR.principal([autre, lec + f"4-{i}"]), 2, "lecture v63 d'un relevé d'une autre version du cœur")
            self.assertIn("autre version", err.getvalue())


class CourseMuette(Course):
    """B9 (C10) : relevés **produits par le cœur**, bras réel muet en génération 1, puis en générations 1 et 2."""
    COURSES = {nom: ["--a-blanc", "--graine", "11", "--generations", "3", "--scenario-proposeur", sc, *PETIT]
               for nom, sc in (("g1", "muet:1"), ("g12", "muet:1,2"))}

    def test_B9_tient_sur_course_saine(self):
        for nom, (code, err, r) in self.r.items():
            self.assertEqual(code, 0, err[-2000:])
            rel = r["releve"]
            self.assertEqual(rel["generations_jouees"]["recopie_melange"], [3] if nom == "g1" else [])
            l = L.lire_etage1(rel)
            self.assertTrue(l["criteres"]["T1"], f"B9 ({nom}) : T1 manque sur une course saine")
            self.assertEqual(l["issue_etage_1"], "tient", (nom, l["criteres"]))
            self.assertEqual(len(rel["boucle"]["lectures"]), 6)


class Arrets(Course):
    """C12, C13, garde 10 de bout en bout : arrêt → code 3, relevé partiel scellé, aucune issue lue (I28 : « non lue (arrêt) »)."""
    COURSES = {nom: ["--a-blanc", "--graine", "11", *COURT, *opts] for nom, opts in (
        ("session", ["--scenario-experimentateur", "erreur"]), ("refus", ["--scenario-proposeur", "refus"]),
        ("arrondi", ["--scenario-experimentateur", "arrondi:2"]), ("fabrique", ["--scenario-experimentateur", "fabrique"]),
        ("part", ["--plafond-usd", "0.4", "--plafond-kimi-usd", "0.2", "--plafond-argon-usd", "0.2"]))}

    def test_arrets_scelles(self):
        attendu = {"session": "EtageInterrompu", "refus": "proposeur", "arrondi": "contre-calcul", "fabrique": "contre-calcul",
                   "part": "part restante"}
        for nom, (code, err, r) in self.r.items():
            self.assertEqual(code, 3, (nom, err[-1500:]))
            self.assertIsNotNone(r, nom)
            self.assertTrue(os.path.isfile(os.path.join(self.d, nom, "tour-ferme-v1-etage1.json.sha256")), nom)
            self.assertIn(attendu[nom], r["arret"], nom)
            rel = r["releve"]
            self.assertIsInstance(rel.get("recherche_loi_plantee"), dict, f"C12 ({nom}) : relevé partiel absent")
            self.assertTrue(rel["arret"], nom)
            l = L.lire_tour_etage_1(rel)["etage_1"]
            self.assertTrue(l["issue_etage_1"].startswith("ne tient pas"), nom)
            self.assertEqual((l["n1"], l["issue_a4"]), ("arret", "non lue (arrêt)"), f"I28 ({nom})")
        self.assertIn("EtageInterrompu", [x.get("type") for x in self.r["session"][2]["releve"]["boucle"]["incidents"]], "C12")


class ArretEnGeneration2(Course):
    """I28 de bout en bout (sonde de la contre-lecture 3) : refus R-764 d'un proposeur en génération 2, après une génération 1
    complète → code 3 ; la lecture v63 ne rend aucune issue A4 (la v62 en rendait une)."""
    COURSES = {"g2": ["--a-blanc", "--graine", "11", "--generations", "3", "--scenario-proposeur", "refus:2", *PETIT]}

    def test_aucune_issue_a4_sur_l_arret(self):
        code, err, r = self.r["g2"]
        self.assertEqual(code, 3, err[-800:])
        rel = r["releve"]
        self.assertEqual(rel["generations_jouees"]["reel"], [1], "l'arrêt n'est pas en génération 2")
        self.assertTrue([c for c in rel["cartes"] if c["bras"] == "reel" and c.get("verdict")], "génération 1 sans carte testée")
        l = L.lire_etage1(rel)
        self.assertEqual((l["issue_a4"], l["cause_a4"], l["n1"], l["chiffres_partiels"]), ("non lue (arrêt)", None, "arret", True),
                         "I28 : une issue A4 est rendue sur un relevé d'arrêt")
        self.assertTrue(l["reserve_majeure_pour_a3"])
        self.assertNotEqual(L62.lire_etage1(rel)["issue_a4"], "non lue (arrêt)")  # la v62 rendait une issue A4 (constat I28)


class FuiteDansLesContextes(unittest.TestCase):
    """I29 de bout en bout : épisodes de développement remplacés par les lignes de la tranche de la même tâche (fuite simulée) →
    le cœur les trouve (`lignes_de_tranche_dans_les_contextes`) et la lecture v63 rend le relevé invalide (défaut, aucune issue
    A4) ; une touche des poids de L* est trouvée et portée à l'audit avant lecture."""

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v64-fuite-")
        vraie = T.episodes_de_developpement

        def fuite(monde, racine, tache, n_dev=200):
            return [{"z": [z0, z1], "g": g, "y": 0} for (z0, z1, g) in sorted(T.lignes_de_tranche(monde, racine, tache))][:n_dev]

        with unittest.mock.patch.object(T, "episodes_de_developpement", fuite):
            cls.code, cls.err = courir(os.path.join(cls.d, "s"), "--a-blanc", "--graine", "11", *COURT)
        cls.r = rapport_ou_rien(os.path.join(cls.d, "s"))
        cls.vraie = vraie

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, True)

    def test_ligne_de_tranche_trouvee_et_releve_invalide(self):
        self.assertEqual(self.code, 0, self.err[-800:])
        rec = self.r["releve"]["recherche_loi_plantee"]
        self.assertEqual(len(rec["lignes_de_tranche_dans_les_contextes"]), 400, "I29 : fuite non trouvée par le cœur")
        l = L.lire_tour_etage_1(self.r["releve"])["etage_1"]
        self.assertTrue(l["issue_etage_1"].startswith("ne tient pas (relevé invalide : défaut"), l["issue_etage_1"])
        self.assertEqual((l["issue_a4"], l["n1"]), ("non lue (relevé invalide)", "critere"))
        self.assertIn("ligne(s) de tranche", l["defaut"])

    def test_touche_de_L_etoile_trouvee(self):
        vue = T.bf.vue_pour_proposeur(T.bf.heritage_initial())
        ctx = T.contexte_du_proposeur(MONDE, vue, 11, "essai|i29")
        self.assertEqual(T.chercher_loi_plantee(MONDE, "consigne", ctx, "essai"), [])
        ctx["note"] = f"poids : {round(MONDE['loi']['poids'][0][0], 2)}"
        touches = T.chercher_loi_plantee(MONDE, "consigne", ctx, "essai")
        self.assertTrue(touches and touches[0]["forme"] == "deux décimales")


# --- lecture gelée v63 sur des relevés synthétiques (C10, C16 ; I28, I29, mineurs 29, 30) --------------------------------------

TEMOINS = {"T-VRAIE": ("passe", True, "survit"), "T-F1": ("passe", False, None), "T-F2": ("passe", True, "éliminée"),
           "T-F4": ("passe", False, None), "T-ANTI": ("passe", False, None), "T-ELIM": ("passe", True, "éliminée"),
           "T-MAL": ("refuse", False, None)}


def carte(bras, g, i, promue=False, verdict=None, gain=-0.3, delta=-0.3, d=1.0, archive=0, **kw):
    return dict({"bras": bras, "generation": g, "identifiant": f"{bras}-{g}-{i}", "temoin": None, "gardien": "passe",
                 "promue": promue, "verdict": verdict, "contre_calcul_ok": True if verdict else None, "gain_nat": gain,
                 "delta_gain_nat": delta, "divergence_nat": d, "archive_de_jugement": archive}, **kw)


def releve_sain(ps_reel=(6, 3, 3), ps_alea=4, recopie=(2, 3), info_reel=None, archive_alea=(0, 5, 5), n_reel=12):
    cartes = []
    jouees = {"reel": [1, 2, 3], "aleatoire": [1, 2, 3], "recopie_melange": list(recopie)}
    for b, gens in jouees.items():
        for g in gens:
            for t, (gard, pr, v) in TEMOINS.items():
                cartes.append({"bras": b, "generation": g, "identifiant": f"{b}-{g}-{t}", "temoin": t, "gardien": gard,
                               "promue": pr, "verdict": v, "contre_calcul_ok": True if v else None})
    for g, n_ps in zip((1, 2, 3), ps_reel):
        n_ps = min(n_ps, n_reel)
        cartes += [carte("reel", g, i, True, "survit", 0.3, 0.3 if g == 1 else 0.05, 0.2) for i in range(n_ps)]
        n_info = (info_reel or (0, 0, 0))[g - 1]
        cartes += [carte("reel", g, 200 + i, False, None, 0.3, 0.3, 0.2) for i in range(n_info)]
        cartes += [carte("reel", g, 100 + i) for i in range(max(0, n_reel - n_ps - n_info))]
    for g in (1, 2, 3):
        k = ps_alea if g == 1 else 0
        cartes += [carte("aleatoire", g, i, True, "survit", 0.2, 0.2, 0.4, archive_alea[g - 1]) for i in range(k)]
        cartes += [carte("aleatoire", g, 100 + i, archive=archive_alea[g - 1]) for i in range(12 - k)]
    for g in recopie:
        cartes += [carte("recopie_melange", g, i, gain=0.3, delta=-0.01, d=0.2) for i in range(6)]
    lectures = [{"bras": b, "generation": g, "attendu": "a" * 64, "lu": "a" * 64} for b in jouees for g in (2, 3)]
    return {"etage": 1, "arret": None, "cartes": cartes, "generations_jouees": jouees, "plan": {"generations": 3},
            "boucle": {"incidents": [], "lectures": lectures},
            "recherche_loi_plantee": {"contextes_cherches": 6, "touches": [], "lignes_de_tranche_dans_les_contextes": []},
            "vd_distinctes": {}}


class LectureV63(unittest.TestCase):
    def test_sain_tient_et_discrimine(self):
        r = L.lire_etage1(releve_sain())
        self.assertEqual((r["issue_etage_1"], r["issue_a4"], r["passes_attendues"], r["lectures_attendues"]), ("tient", "discrimine", 8, 6))
        self.assertEqual((r["chiffres_partiels"], r["audit_avant_lecture"]), (False, []))

    def test_B9_lectures_attendues_jouees_ou_non(self):
        for recopie, passes in (((), 6), ((3,), 7)):
            r = L.lire_etage1(releve_sain(recopie=recopie))
            self.assertEqual((r["issue_etage_1"], r["passes_attendues"]), ("tient", passes), f"B9 : {r['criteres']}")
        rel = releve_sain(recopie=())
        rel["boucle"]["lectures"] = [x for x in rel["boucle"]["lectures"] if not (x["bras"] == "recopie_melange" and x["generation"] == 2)]
        self.assertFalse(L.lire_etage1(rel)["criteres"]["T1"], "B9 : lecture de la recopie muette non exigée")
        rel = releve_sain()
        rel["boucle"]["lectures"][0]["lu"] = "b" * 64
        self.assertFalse(L.lire_etage1(rel)["criteres"]["T1"])

    def test_I17_aucune_carte_reelle_jugee(self):
        rel = releve_sain(n_reel=0, ps_reel=(0, 0, 0))
        r = L.lire_etage1(rel)
        self.assertEqual(r["issue_a4"], L.A4_NON_MESURABLE, "I17 : A4 lue « promeut autant » sans carte réelle")
        self.assertTrue(r["reserve_majeure_pour_a3"])

    def test_I16_P4_par_cas(self):
        r = L.lire_etage1(releve_sain(archive_alea=(0, 0, 0), ps_alea=7))
        self.assertEqual((r["predictions"]["P4"]["cas"], r["predictions"]["P4"]["trois_generations"]), ("vide", True), "I16")
        r = L.lire_etage1(releve_sain(archive_alea=(0, 5, 5), ps_alea=7))
        self.assertEqual((r["predictions"]["P4"]["cas"], r["predictions"]["P4"]["trois_generations"]), ("informative", False), "I16")

    def test_I18_recherche_exigee(self):
        for mauvais in (None, [], {"touches": []}):
            rel = releve_sain()
            rel["recherche_loi_plantee"] = mauvais
            with self.assertRaises(L.ReleveInvalide):
                L.lire_etage1(rel)
            self.assertTrue(L.lire_tour_etage_1(rel)["etage_1"]["issue_etage_1"].startswith("ne tient pas (relevé invalide"))

    def test_S5_non_concluant_par_bras(self):
        rel = releve_sain()
        for c in [c for c in rel["cartes"] if c["bras"] == "aleatoire" and c["verdict"]][:4]:
            c["verdict"] = "non concluant"
        r = L.lire_etage1(rel)
        self.assertTrue(r["audits"]["S5_non_concluant"] and r["audits"]["S5_asymetrie"], "S5 : non concluant par bras ignoré")
        self.assertFalse(L.lire_etage1(releve_sain())["audits"]["S5_asymetrie"])

    def test_arret_et_contre_calcul(self):
        rel = releve_sain()
        rel["arret"] = "plafond"
        r = L.lire_etage1(rel)
        self.assertEqual((r["criteres"]["T1"], r["n1"]), (False, "arret"))
        rel = releve_sain()
        next(c for c in rel["cartes"] if c["verdict"] == "survit" and not c["temoin"])["contre_calcul_ok"] = None
        with self.assertRaises(L.ReleveInvalide):
            L.lire_etage1(rel)

    def test_I28_aucune_issue_a4_sur_un_arret(self):
        rel = releve_sain()
        self.assertEqual(L.lire_etage1(rel)["issue_a4"], "discrimine")
        rel["arret"] = "ArretTour : proposeur kimi : session 'refus'"
        r = L.lire_etage1(rel)
        self.assertEqual((r["issue_a4"], r["cause_a4"], r["chiffres_partiels"]), ("non lue (arrêt)", None, True),
                         "I28 : issue A4 rendue sur un arrêt")
        self.assertTrue(r["reserve_majeure_pour_a3"])
        self.assertIsNotNone(r["newcombe_ps_reel_moins_aleatoire"], "les chiffres partiels restent rapportés")

    def test_I29_ligne_de_tranche_releve_invalide_et_touche_auditee(self):
        rel = releve_sain()
        rel["recherche_loi_plantee"]["lignes_de_tranche_dans_les_contextes"] = [[0.1, -0.2, 1]]
        with self.assertRaises(L.DefautDeCourse):
            L.lire_etage1(rel)
        l = L.lire_tour_etage_1(rel)["etage_1"]
        self.assertTrue(l["issue_etage_1"].startswith("ne tient pas (relevé invalide : défaut"), "I29 : fuite de tranche sans conséquence")
        self.assertEqual((l["issue_a4"], l["n1"]), ("non lue (relevé invalide)", "critere"))
        self.assertIn("ligne(s) de tranche", l["defaut"])
        rel = releve_sain()
        rel["recherche_loi_plantee"]["touches"] = [{"ou": "x", "chemin": "$", "valeur": "1.23", "parametre": ["poids", 0, 0],
                                                   "forme": "deux décimales"}]
        r = L.lire_etage1(rel)
        self.assertEqual(r["issue_etage_1"], "tient")
        self.assertTrue(any("touche(s) des paramètres de L*" in x for x in r["audit_avant_lecture"]), "I29 : touche de L* non auditée")

    def test_mineur_29_releve_invalide_d_arret(self):
        rel = {"version": "tour-ferme-v64", "etage": 1, "arret": "TourRefuse : x", "cartes": [], "recherche_loi_plantee": None,
               "generations_jouees": {b: [] for b in L.BRAS_ETAGE1}, "boucle": {"incidents": [], "lectures": []}, "plan": {"generations": 3}}
        l = L.lire_tour_etage_1(rel)["etage_1"]
        self.assertTrue(l["issue_etage_1"].startswith("ne tient pas (relevé invalide"))
        self.assertEqual((l["n1"], l["issue_a4"]), ("arret", "non lue (arrêt)"), "mineur 29 : relevé d'arrêt invalide lu « critère »")

    def test_mineur_30_P7_et_section_4_5(self):
        rel = releve_sain()
        for c in rel["cartes"]:  # divergences des VD du bras réel : 0,2 en g1, 0,1 en g2, 0,04 en g3
            if c["bras"] == "reel" and not c["temoin"] and c.get("verdict") == "survit":
                c["divergence_nat"] = {1: 0.2, 2: 0.1, 3: 0.04}[c["generation"]]
        p7 = L.lire_etage1(rel)["predictions"]["P7"]
        self.assertEqual(p7["plus_petite_divergence_des_vd_reel_par_generation"], {"1": 0.2, "2": 0.1, "3": 0.04})
        self.assertIs(p7["decroit_de_la_generation_1_a_la_derniere"], True)
        self.assertIs(p7["aucune_vd_etoile_generation_1"], True)
        for c in rel["cartes"]:
            if c["bras"] == "reel" and not c["temoin"] and c.get("verdict") == "survit" and c["generation"] == 3:
                c["divergence_nat"] = 0.2
        self.assertIs(L.lire_etage1(rel)["predictions"]["P7"]["decroit_de_la_generation_1_a_la_derniere"], False, "mineur 30 : P7")
        m = L.lire_etage1(releve_sain())["mesures_sans_critere"]
        self.assertEqual(m["meilleur_gain_reel_par_generation"], {"1": 0.3, "2": 0.3, "3": 0.3})
        self.assertEqual(m["refus_du_gardien_par_bras_et_motif"], {})


# --- I27 : fermeture du code gelé (statique) et fermeture mesurée pendant une course -----------------------------------------------


def imports_de(rel):
    """Fichiers du dépôt importés par `rel` (arbre syntaxique, imports tardifs compris), chargés par chemin (« x.py » du même
    dossier) et `__init__.py` du paquet."""
    paquet = os.path.dirname(rel)
    out = set()
    for n in ast.walk(ast.parse(open(os.path.join(RACINE, rel), encoding="utf-8").read())):
        if isinstance(n, ast.ImportFrom):
            if n.level:
                base = paquet
                for _ in range(n.level - 1):
                    base = os.path.dirname(base)
                mod = os.path.join(base, *(n.module.split(".") if n.module else []))
            else:
                mod = os.path.join(*n.module.split(".")) if n.module else ""
            out |= {c for c in [mod + ".py"] + [os.path.join(mod, a.name) + ".py" for a in n.names] if os.path.isfile(os.path.join(RACINE, c))}
        elif isinstance(n, ast.Import):
            out |= {c for c in (os.path.join(*a.name.split(".")) + ".py" for a in n.names) if os.path.isfile(os.path.join(RACINE, c))}
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.endswith(".py") and "/" not in n.value:
            if os.path.isfile(os.path.join(RACINE, paquet, n.value)):
                out.add(os.path.join(paquet, n.value))
    if os.path.isfile(os.path.join(RACINE, paquet, "__init__.py")):
        out.add(os.path.join(paquet, "__init__.py"))
    return out


def fermeture_statique():
    ferm, pile = set(), ["demonstrations/tour_ferme_v64.py", "demonstrations/lire_tour_ferme_v64.py"]
    while pile:
        x = pile.pop()
        if x not in ferm:
            ferm.add(x)
            pile += sorted(imports_de(x) - ferm)
    return ferm


class Fermeture(unittest.TestCase):
    def test_bloc_gele_egal_a_la_fermeture_statique(self):
        ferm = fermeture_statique()
        geles = set(LANCEUR.FICHIERS_GELES)
        self.assertEqual(len(geles), len(LANCEUR.FICHIERS_GELES))
        self.assertEqual((sorted(ferm - geles), sorted(geles - ferm)), ([], []), "I27 : bloc gelé ≠ fermeture statique des imports")
        self.assertTrue({"pole/ideation.py", "pole/tests_de_mort.py", "pole/evaluateur_lois_v62.py", "pole/adaptateur_commande_v64.py",
                         "pole/lecture_tour_ferme_v63.py"} <= geles)
        self.assertEqual(len(geles), 92, "v64 : 92 fichiers gelés")
        self.assertFalse({"pole/tour_ferme_v63.py", "demonstrations/tour_ferme_v63.py", "demonstrations/lire_tour_ferme_v63.py"} & geles)
        for r in LANCEUR.FICHIERS_GELES:
            self.assertTrue(os.path.isfile(os.path.join(RACINE, r)), r)


CODE_FERMETURE_EN_COURSE = r'''
import contextlib, importlib.util, io, json, os, sys, unittest.mock
R, SORTIE = sys.argv[1], sys.argv[2]
sys.path[:0] = [R, os.path.join(R, "essais")]
sys.dont_write_bytecode = True
vus = set()
orig = importlib.util.spec_from_file_location
def espion(n, l=None, *a, **k):
    if l is not None:
        vus.add(os.path.relpath(os.path.abspath(str(l)), R))
    return orig(n, l, *a, **k)
importlib.util.spec_from_file_location = espion
def charges():
    fs = {os.path.relpath(os.path.abspath(m.__file__), R) for m in list(sys.modules.values())
          if getattr(m, "__file__", None) and os.path.abspath(m.__file__).startswith(R + os.sep)}
    return sorted(x for x in fs | vus if not x.startswith("essais" + os.sep))
def charger(nom, rel):
    s = importlib.util.spec_from_file_location(nom, os.path.join(R, rel)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
ph = {}
L = charger("fermeture_lanceur", "demonstrations/tour_ferme_v64.py")
LT = charger("fermeture_lecteur", "demonstrations/lire_tour_ferme_v64.py")
L.charger_goodhart_v2().charger_ideation_v8()
import pole.configuration_v56, pole.relais
ph["chargement"] = charges()
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    c1 = L.principal([os.path.join(SORTIE, "course"), "--etage", "1", "--a-blanc", "--graine", "11", "--generations", "2",
                      "--cartes-par-proposeur", "1", "--cartes-reference", "2", "--m-e-bh", "9", "--bac", "factice"])
ph["course"] = charges()
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    c2 = LT.principal([os.path.join(SORTIE, "course"), os.path.join(SORTIE, "lecture.json")])
ph["lecture"] = charges()
import essais.test_tour_ferme_v64 as E  # aides d'essai : chargées avant l'instantané, elles ne comptent pas
from pole import a_blanc_v59 as A
aides = charges()
argv, dp = E.preparer_chemin_reel(os.path.join(SORTIE, "reel-" + "x"))
vraie = A.choisir_executeur
with unittest.mock.patch.dict(os.environ, {"PATH": os.environ.get("PATH", os.defpath), "HOME": SORTIE, "POLE_MACHINE_JETABLE_V56": "1"},
                              clear=True), unittest.mock.patch.object(L, "DOSSIER_PREREG", dp), \
        unittest.mock.patch.object(A, "choisir_executeur", lambda bac, **kw: vraie("factice")), \
        contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    c3 = L.principal(argv + ["--verifier-seulement"])
ph["chemin_reel"] = sorted(set(charges()) - (set(aides) - set(ph["lecture"])))
print(json.dumps({"codes": [c1, c2, c3], "phases": ph}))
'''


class FermetureEnCourse(unittest.TestCase):
    """I27 : ce que la course **charge en s'exécutant** (course à blanc par le chemin réel, lecture, `--verifier-seulement` du
    chemin réel), mesuré dans un processus neuf, est dans le bloc gelé ; `pole/ideation.py` et `pole/tests_de_mort.py` y sont
    chargés par la course (absents du bloc v62 : l'artefact)."""

    def test_modules_charges_pendant_la_course(self):
        d = tempfile.mkdtemp(prefix="essai-v64-fermeture-")
        self.addCleanup(shutil.rmtree, d, True)
        os.makedirs(os.path.join(d, "reel-x"))
        out = subprocess.run([sys.executable, "-I", "-B", "-c", CODE_FERMETURE_EN_COURSE, RACINE, d], capture_output=True, text=True,
                             timeout=600, cwd=RACINE)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        m = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(m["codes"], [0, 0, 0], out.stderr[-1500:])
        geles = set(LANCEUR.FICHIERS_GELES)
        tout = set().union(*map(set, m["phases"].values()))
        self.assertEqual(sorted(tout - geles), [], "I27 : module chargé pendant la course hors du bloc gelé")
        en_course = set(m["phases"]["course"]) - set(m["phases"]["chargement"])
        self.assertTrue({"pole/ideation.py", "pole/tests_de_mort.py"} <= en_course, sorted(en_course))
        v62 = set(LANCEUR.FICHIERS_GELES) - {"pole/ideation.py", "pole/tests_de_mort.py"}  # artefact : le bloc de la v62
        self.assertEqual(sorted(tout - v62), ["pole/ideation.py", "pole/tests_de_mort.py"])


class BacReelV64(unittest.TestCase):
    """Une course à blanc dans le vrai bac (`bwrap`, identité dédiée 64097), lanceur en sous-processus. L'identité dédiée doit
    pouvoir traverser le dossier temporaire (sinon : passer TMPDIR=/tmp à ce seul essai, dit au rapport). v64 : sauté, motif dit,
    si `POLE_ESSAI_BAC_REEL_NON_JOUE=1` (une seule course à la fois par identité dédiée : mécanisme de la v51, CL15-04)."""

    def test_a_blanc_dans_le_vrai_bac(self):
        if os.environ.get("POLE_ESSAI_BAC_REEL_NON_JOUE") == "1":
            self.skipTest("ESSAI RÉEL NON JOUÉ (POLE_ESSAI_BAC_REEL_NON_JOUE=1)")
        if not shutil.which("bwrap"):
            self.skipTest("bwrap absent")
        uid = []
        if os.geteuid() == 0:
            ok = shutil.which("setpriv") and subprocess.run(["setpriv", "--reuid", "64097", "--regid", "64097", "--clear-groups", "--no-new-privs",
                                                            "--", "/usr/bin/id", "-u"], capture_output=True, timeout=20).stdout.strip() == b"64097"
            if not ok:
                self.skipTest("superutilisateur sans setpriv utilisable")
            trav = subprocess.run(["setpriv", "--reuid", "64097", "--regid", "64097", "--clear-groups", "--no-new-privs", "--",
                                   "/usr/bin/test", "-x", tempfile.gettempdir()], capture_output=True, timeout=20).returncode == 0
            if not trav:
                self.skipTest(f"l'identité 64097 ne traverse pas {tempfile.gettempdir()} : relancer cet essai avec TMPDIR=/tmp")
            uid = ["--utilisateur-bac", "64097"]
        d = tempfile.mkdtemp(prefix="essai-v64-bac-")
        self.addCleanup(shutil.rmtree, d, True)
        r = subprocess.run([sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "tour_ferme_v64.py"), os.path.join(d, "s"),
                            "--etage", "1", "--a-blanc", "--graine", "12", "--bac", "reel", *uid, "--generations", "2",
                            "--cartes-par-proposeur", "1", "--cartes-reference", "2", "--m-e-bh", "9"],
                           capture_output=True, text=True, timeout=900, cwd=RACINE)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        rap = rapport(os.path.join(d, "s"))
        et = [l for l in rap["journal"] if l["evenement"] == "etage-tests-de-mort"]
        self.assertTrue(et and all(l["bac_a_sable"] == "bwrap" and l["factice"] is False for l in et))
        self.assertTrue(all(c["contre_calcul_ok"] is True for c in rap["releve"]["cartes"] if c.get("verdict")))
        self.assertEqual([x for x in os.listdir(tempfile.gettempdir()) if x.startswith("bac-tour-ferme-v64-")], [],
                         "mineur 34 : dossier du bac resté après la course")


# --- v64, F (TF-02, option a) : code 4 « rien envoyé » lu « budget_depasse » pour cette session ----------------------------------

RIEN = {"texte": "", "cout_usd": 1e-06, "envoye": False}  # la dernière ligne d'une commande qui n'a rien envoyé (plancher déclaré)


def commande_locale(dossier, nom, code, objet=None, ligne=None):
    """Commande externe factice (script Python local, aucun réseau) : lit l'entrée standard, imprime `objet` en JSON (`modele_servi`
    à None : le modèle demandé, `MODELE_DEMANDE_POLE`) ou la ligne brute `ligne` sur sa dernière ligne, sort avec `code`."""
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".py")
    corps = (f"print({ligne!r})" if ligne is not None else
             f"o = {objet!r}\nif 'modele_servi' in o and o['modele_servi'] is None:\n"
             "    o['modele_servi'] = os.environ.get('MODELE_DEMANDE_POLE', '')\nprint(json.dumps(o))")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("import json, os, sys\nsys.stdin.read()\n" + corps + f"\nsys.exit({int(code)})\n")
    return [sys.executable, "-I", "-B", chemin]


class CommandeCode4(unittest.TestCase):
    """F (TF-02, option a), R5 : une vraie commande locale qui sort en code 4 en disant `"envoye": false` → « budget_depasse » pour
    cette session, coût compté 0 (le plancher déclaré est dit au motif), marquée « rien envoyé » ; tout autre cas garde la lecture
    de la v56 (artefacts) ; la commande externe v56 lit le même code 4 « erreur » (la lecture de la v63, qui arrêtait la course)."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v64-code4-")
        self.addCleanup(shutil.rmtree, self.d, True)

    def lancer(self, code, objet=None, ligne=None, classe=None, nom="c", budget=0.1):
        classe = classe or AC.AdaptateurCommandeExterneV64
        ad = classe(commande_locale(self.d, nom, code, objet, ligne), environnement={"PATH": os.defpath}, exiger_modele_servi=True)
        dd = os.path.join(self.d, "session-" + nom)
        os.makedirs(dd, exist_ok=True)
        return ad.lancer(v5.ROLE_LECTEUR, "consigne", dd, budget, 2, modele="gemini-4-argon")

    def test_sain_code_4_rien_envoye(self):
        for nom, objet in (("plancher", RIEN), ("cout_nul", dict(RIEN, cout_usd=0)), ("sans_texte_ni_cout", {"envoye": False})):
            with self.subTest(cas=nom):
                r = self.lancer(4, objet, nom=nom)
                self.assertEqual((r.statut, r.cout_declare_usd), ("budget_depasse", 0.0),
                                 f"TF-02 : code 4 « rien envoyé » mal lu ({r.statut}, {r.erreur})")
                self.assertTrue(AC.rien_envoye(r), "TF-02 : session « rien envoyé » non marquée")
                self.assertIn("rien envoyé", r.erreur)
                self.assertEqual(r.texte_final, "")
        self.assertIn("1e-06", self.lancer(4, RIEN, nom="motif").erreur)  # le plancher déclaré est dit, jamais compté

    def test_artefacts_lecture_inchangee(self):
        cas = (("code 4 sans envoye", 4, {"texte": "", "cout_usd": 1e-06}, "erreur"),
               ("code 4, envoye vrai", 4, dict(RIEN, envoye=True), "erreur"),
               ("code 4, envoye « false » en texte", 4, dict(RIEN, envoye="false"), "erreur"),
               ("code 4, envoye 0", 4, dict(RIEN, envoye=0), "erreur"),
               ("code 3, envoye faux", 3, RIEN, "erreur"),
               ("code 2, envoye faux", 2, RIEN, "erreur"),
               ("code 4, refus dit (R-764)", 4, dict(RIEN, refus=True), "refus"))
        for i, (nom, code, objet, statut) in enumerate(cas):
            with self.subTest(cas=nom):
                r = self.lancer(code, objet, nom=f"a{i}")
                self.assertEqual(r.statut, statut, f"TF-02 : {nom} lu {r.statut!r} ({r.erreur})")
                self.assertFalse(AC.rien_envoye(r), f"TF-02 : {nom} lu « rien envoyé »")
        self.assertEqual(self.lancer(4, ligne="pas du JSON", nom="illisible").statut, "erreur")
        ok = self.lancer(0, {"texte": "VERDICT: survit", "cout_usd": 0.002, "modele_servi": None}, nom="ok")
        self.assertEqual((ok.statut, ok.cout_declare_usd, ok.modele_servi), ("ok", 0.002, "gemini-4-argon"))  # recopie v56 gardée
        v56 = self.lancer(4, RIEN, classe=AdaptateurCommandeExterneV56, nom="v56")
        self.assertEqual(v56.statut, "erreur", "la lecture v56 (celle de la v63) du code 4 a changé")


class EtageRienEnvoye(unittest.TestCase):
    """F (TF-02, option a), R5, à l'unité : `AdaptateurEtageV64` rend à l'étage un « budget_depasse » marqué « rien envoyé » (fin
    des tours de la carte pour ce rôle, rien compté) ; tout autre « budget_depasse » sous le plafond passé, et la part du relais
    épuisée, restent un arrêt (C13) ; l'adaptateur de l'étage v63 arrêtait la course sur le même résultat."""
    RIEN = AC.ResultatV64("", [], 0.0, "budget_depasse", "commande externe : code 4, rien envoyé (essai)", rien_envoye=True)

    def test_sain(self):
        for role in (v5.ROLE_EXPERIMENTATEUR, v5.ROLE_LECTEUR):
            with self.subTest(role=role):
                e = T.AdaptateurEtageV64(AdaptateurFaux(self.RIEN), AdaptateurFaux(self.RIEN))
                self.assertIs(e.lancer(role, "c", "/x/tour-001", 0.05, 2), self.RIEN, f"TF-02 : « rien envoyé » de {role} pris pour un arrêt")
                a = e.appels[-1]
                self.assertEqual((a["rien_envoye"], a["cout_usd"], a["taille_consigne"], a["verification_prealable"]), (True, 0.0, 1, False))
                self.assertEqual(sum(e.depense.values()), 0.0)

    def test_artefacts(self):
        for nom, r in (("Resultat simple (402 d'un relais, coût 0)", Resultat("", [], 0.0, "budget_depasse")),
                       ("ResultatV64 non marqué", dataclasses.replace(self.RIEN, rien_envoye=False))):
            with self.subTest(cas=nom), self.assertRaises(T.ArretTour, msg=f"C13 : {nom} sans arrêt"):
                T.AdaptateurEtageV64(AdaptateurFaux(r), AdaptateurFaux(r)).lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2)
        e = T.AdaptateurEtageV64(AdaptateurFaux(self.RIEN), AdaptateurFaux(self.RIEN))
        e.parts, e.depense["kimi"] = {"kimi": 0.4}, 0.4
        with self.assertRaisesRegex(T.ArretTour, "rien envoyé : True", msg="TF-02 : part du relais épuisée ignorée sur un « rien envoyé »"):
            e.lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2)
        self.assertFalse(AC.rien_envoye(Resultat("", [], 0.0, "budget_depasse", "commande externe : code 4, rien envoyé")))
        with self.assertRaises(T63.ArretTour):  # constat TF-02 : l'adaptateur de l'étage v63 arrêtait la course
            T63.AdaptateurEtageV63(AdaptateurFaux(self.RIEN), AdaptateurFaux(self.RIEN)).lancer(v5.ROLE_LECTEUR, "c", "/x/lecteur", 0.1, 2)


COMMANDE_EXPERIMENTATEUR = r'''
import json, os, sys
sys.path.insert(0, sys.argv[1])
from pole import tour_ferme_v64 as T
consigne = sys.stdin.read()
tour = int(os.path.basename(os.getcwd()).split("-")[1])
if tour >= int(sys.argv[2]):
    print(json.dumps({"texte": "", "cout_usd": 1e-06, "envoye": False}))
    sys.exit(4)
r = T.AdaptateurExperimentateurScripte().lancer("experimentateur_test", consigne, os.getcwd(), 0.8, 2)
print(json.dumps({"texte": r.texte_final, "cout_usd": 0.01, "modele_servi": os.environ.get("MODELE_DEMANDE_POLE", "")}))
'''


class EtageV64CommandesReelles(Tranche):
    """F (TF-02, option a) sur l'étage entier : de vraies commandes locales derrière la commande externe v64 — l'expérimentateur
    exécute au tour 1 puis sort en code 4 « rien envoyé » au tour 2, le vérificateur sort en code 4 à chaque session —, l'étage v5
    et `AdaptateurEtageV64` : la carte est jugée sur ce qu'elle a exécuté (« survit », contre-calcul concordant), le témoin du
    vérificateur est « non concluant », rien n'est compté pour les sessions refusées, aucun arrêt. Artefact : les mêmes commandes
    derrière la commande externe v56 (lecture de la v63) → `EtageInterrompu`, l'arrêt de la course que décrit TF-02."""
    ROLES = {"experimentateur": ("experimentateur-kimi", "kimi-k3.1-pro"), "verificateur": ("verificateur-argon", "gemini-4-argon"),
             "relais": {"experimentateur": "kimi", "verificateur": "argon"}}

    def jouer(self, nom, classe):
        d = os.path.join(self.d, "commandes-" + nom)
        os.makedirs(d)
        exp = os.path.join(d, "experimentateur.py")
        with open(exp, "w", encoding="utf-8") as f:
            f.write(COMMANDE_EXPERIMENTATEUR)
        kimi = classe([sys.executable, "-I", "-B", exp, RACINE, "2"], environnement={"PATH": os.defpath}, exiger_modele_servi=True)
        argon = classe(commande_locale(d, "verificateur", 4, RIEN), environnement={"PATH": os.defpath}, exiger_modele_servi=True)
        prix = AC.prix_caractere_commande(10.0)
        ad = T.AdaptateurEtageV64(kimi, argon, "kimi", "argon", prix_caractere_usd={"kimi": prix, "argon": prix})
        compteur = T.Compteur(50.0, 3600.0, {"kimi": 44.0, "argon": 6.0})
        ad.parts = dict(compteur.parts)
        carte = T.carte_servie("F-0000000000f2", MONDE["loi"], "reel")
        sortie = T.jouer_etage(os.path.join(self.d, nom, "etage"), [carte], {carte["identifiant"]: MONDE["loi"]}, MONDE, 5,
                               f"essai|tf02|{nom}", A.choisir_executeur("factice")[0], ad, self.ROLES, compteur, [], moteur="simule",
                               environnement=T.ENV_A_BLANC)
        return sortie, ad, compteur

    def test_sain_commandes_v64_aucun_arret(self):
        (resume, _, _, _, cc), ad, compteur = self.jouer("v64", AC.AdaptateurCommandeExterneV64)
        f = resume["par_fiche"][0]
        self.assertEqual((f["statut"], f["verdict"], f["tours"]), ("testée", "survit", 2), f.get("fin_des_tours"))
        self.assertIn("budget_depasse", f["fin_des_tours"])
        self.assertEqual(f["lecteur"]["verdict"], "non concluant")
        self.assertTrue(cc and all(x["ok"] and not x["sans_objet"] for x in cc.values()))
        self.assertEqual([(a["role"], a["rien_envoye"]) for a in ad.appels],
                         [(v5.ROLE_EXPERIMENTATEUR, False), (v5.ROLE_EXPERIMENTATEUR, True), (v5.ROLE_LECTEUR, True)])
        self.assertAlmostEqual(compteur.par_relais["kimi"], 0.01, places=9)  # rien compté pour les sessions « rien envoyé »
        self.assertEqual(compteur.par_relais["argon"], 0.0)

    def test_artefact_commandes_v56_arret(self):
        with self.assertRaises(v5.EtageInterrompu) as e:
            self.jouer("v56", AdaptateurCommandeExterneV56)
        self.assertIn("code 4", str(e.exception))


class CourseRienEnvoye(Course):
    """F (TF-02, option a) de bout en bout par le chemin réel (doublures) : « rien envoyé » au tour 2 de chaque carte et à chaque
    session du vérificateur → code 0, aucune carte arrêtée, cartes jugées sur le tour 1 (« tient ») ; « rien envoyé » dès le tour 1
    → code 0, toutes les cartes testées « non concluant », lecture « ne tient pas » par critère, jamais un arrêt (n1 = critère)."""
    COURSES = {"tour2": ["--a-blanc", "--graine", "11", "--scenario-experimentateur", "rien_envoye:2", "--scenario-verificateur",
                         "rien_envoye", *COURT],
               "tour1": ["--a-blanc", "--graine", "11", "--scenario-experimentateur", "rien_envoye:1", *COURT]}

    def test_tour_2_et_verificateur(self):
        code, err, r = self.r["tour2"]
        self.assertEqual(code, 0, f"TF-02 : un « rien envoyé » arrête la course : {err[-800:]}")
        l = L.lire_tour_etage_1(r["releve"])["etage_1"]
        self.assertEqual(l["issue_etage_1"], "tient", l.get("criteres"))
        exp = [a for a in r["appels_etage"] if a["role"] == v5.ROLE_EXPERIMENTATEUR]
        lec = [a for a in r["appels_etage"] if a["role"] == v5.ROLE_LECTEUR]
        self.assertTrue(lec and all(a["rien_envoye"] and a["cout_usd"] == 0.0 for a in lec))
        self.assertTrue(any(a["rien_envoye"] for a in exp) and not all(a["rien_envoye"] for a in exp))

    def test_tour_1_lu_par_critere_jamais_un_arret(self):
        code, err, r = self.r["tour1"]
        self.assertEqual(code, 0, f"TF-02 : un « rien envoyé » au tour 1 arrête la course : {err[-800:]}")
        testees = [c for c in r["releve"]["cartes"] if c.get("verdict")]
        self.assertTrue(testees and all(c["verdict"] == "non concluant" for c in testees))
        l = L.lire_tour_etage_1(r["releve"])["etage_1"]
        self.assertTrue(l["issue_etage_1"].startswith("ne tient pas"), l["issue_etage_1"])
        self.assertEqual(l["n1"], "critere")


class ProposeurRienEnvoye(unittest.TestCase):
    """Ce que la v64 ne change pas, dit (annexe A, A.5) : un « budget_depasse » d'un proposeur, « rien envoyé » compris, arrête la
    course (`ArretTour`, coût compté 0) ; cas sain : réponse ordinaire de la même commande v64 (taille de la consigne consignée)."""

    def test_sain_et_artefact(self):
        d = tempfile.mkdtemp(prefix="essai-v64-prop-")
        self.addCleanup(shutil.rmtree, d, True)
        env = {"PATH": os.defpath}
        ok = AC.AdaptateurCommandeExterneV64(commande_locale(d, "ok", 0, {"texte": "```json\n[]\n```", "cout_usd": 0.003,
                                                                         "modele_servi": None}), environnement=env, exiger_modele_servi=True)
        p = T.ProposeurAdaptateur("kimi", "kimi", ok, d, 0.5, "kimi-k3.1-pro")
        self.assertEqual(p.proposer("c", {}, "t"), ("```json\n[]\n```", 0.003))
        self.assertEqual(p.appels[-1]["taille_consigne"], len("c\n\n```json\n{}\n```\n"))
        rien = AC.AdaptateurCommandeExterneV64(commande_locale(d, "rien", 4, RIEN), environnement=env, exiger_modele_servi=True)
        with self.assertRaisesRegex(T.ArretTour, "budget_depasse") as e:
            T.ProposeurAdaptateur("kimi", "kimi", rien, d, 0.5, "kimi-k3.1-pro").proposer("c", {}, "t2")
        self.assertEqual(e.exception.cout, 0.0)


class CommandesV64(unittest.TestCase):
    """F (TF-02, option a), chemin réel : `commandes_v64` fait passer chaque relais déclaré `commande_externe` à la v64 (même
    commande, modèle servi exigé, modèles servis permis) et refait sa porte « environnement » sur l'adaptateur v64 ; Kimi par
    protocole est laissé tel quel (refusé ensuite par la garde des rôles) ; relais déclaré commande externe mais construit autrement
    → refus."""

    def test_sain_et_artefacts(self):
        from pole.adaptateurs_v56 import porte_depuis_configuration
        d = tempfile.mkdtemp(prefix="essai-v64-relais-")
        self.addCleanup(shutil.rmtree, d, True)
        cmd = commande_locale(d, "c", 0, {"texte": "x", "cout_usd": 0.001, "modele_servi": None})
        f = {"kimi": {"type": "commande_externe", "commande": cmd, "porte_plafond": {"type": "environnement"},
                      "modeles_servis_permis": {"kimi-k3.1-pro": ["kimi-k3.1-pro-x"]}},
             "argon": {"type": "commande_externe", "commande": cmd, "porte_plafond": {"type": "environnement"}}}
        conf = {"fournisseurs": f}
        with unittest.mock.patch.dict(os.environ, {"PATH": os.defpath}, clear=True):
            ads = {n: AdaptateurCommandeExterneV56(cmd, exiger_modele_servi=True, modeles_servis_permis=f[n].get("modeles_servis_permis"))
                   for n in ("kimi", "argon")}
            portes = {n: porte_depuis_configuration(n, {"type": "environnement"}, ads[n]) for n in ads}
            a2, p2 = AC.commandes_v64(conf, ads, portes)
            for n in ("kimi", "argon"):
                self.assertIsInstance(a2[n], AC.AdaptateurCommandeExterneV64)
                self.assertIsNot(a2[n], ads[n])
                self.assertEqual((a2[n].commande, a2[n].exiger_modele_servi), (cmd, True))
                p2[n].transmettre("tour_ferme_v64", 6.0)
                self.assertEqual(a2[n].environnement_commande().get("PLAFOND_ETAPE_USD"), "6.00", "porte non refaite sur l'adaptateur v64")
                self.assertIsNone(ads[n].plafond_etape)
        self.assertEqual(a2["kimi"].modeles_servis_permis, {"kimi-k3.1-pro": ("kimi-k3.1-pro-x",)})
        self.assertIn("lecture_code_4", a2["argon"].description())
        kp = object()
        a3, _ = AC.commandes_v64({"fournisseurs": dict(f, kimi={"type": "kimi_protocole"})}, dict(ads, kimi=kp), portes)
        self.assertIs(a3["kimi"], kp)  # laissé tel quel : la garde des rôles le refuse ensuite (code 2)
        with self.assertRaises(AC.RelaisNonCommande):
            AC.commandes_v64(conf, dict(ads, argon=kp), portes)


# --- v64, G : barème prudent des commandes passé à l'étage (vérification préalable de la l. 468 de l'étage v5) ------------------


class BaremeDesCommandes(unittest.TestCase):
    """G (R5) : prix d'entrée par million de jetons lu dans la configuration, trois caractères par jeton (barème prudent des
    commandes) ; aucun défaut : clé absente, nulle, négative, non finie, booléenne ou texte → `BaremeAbsent`."""

    def test_sain_et_artefacts(self):
        self.assertEqual(AC.CARACTERES_PAR_JETON_COMMANDES, 3)
        self.assertAlmostEqual(AC.prix_caractere_commande(10.0), 10.0 / 1e6 / 3, places=15)
        conf = {"fournisseurs": {"kimi": {"prix_entree_usd_par_million_jetons": 2.5}, "argon": {"prix_entree_usd_par_million_jetons": 10}}}
        b = AC.bareme_depuis_configuration(conf, "argon")
        self.assertEqual(b, {"prix_entree_usd_par_million_jetons": 10.0, "caracteres_par_jeton": 3, "prix_caractere_usd": 10.0 / 1e6 / 3})
        self.assertAlmostEqual(AC.bareme_depuis_configuration(conf, "kimi")["prix_caractere_usd"], 2.5 / 3e6, places=15)
        # mesure (point 3) : 0,10 USD de vérificateur, sortie minimale de 200 jetons à 50 USD par million → 27 000 caractères au barème
        self.assertAlmostEqual((0.10 - 200 * 50e-6) / b["prix_caractere_usd"], 27_000, places=6)
        for nom, v in (("absente", None), ("nulle", 0), ("négative", -1.0), ("NaN", float("nan")), ("infinie", float("inf")),
                       ("booléenne", True), ("texte", "10")):
            with self.subTest(cas=nom), self.assertRaises(AC.BaremeAbsent):
                AC.bareme_depuis_configuration({"fournisseurs": {"argon": {} if v is None else {"prix_entree_usd_par_million_jetons": v}}}, "argon")
        with self.assertRaises(AC.BaremeAbsent):
            AC.bareme_depuis_configuration({"fournisseurs": {}}, "kimi")


class VerificationPrealable(unittest.TestCase):
    """G (R5), à l'unité : consigne × prix d'un caractère > plafond passé → rien n'est lancé (« budget_depasse » marqué « rien
    envoyé ») ; sous le plafond, ou sans prix (à blanc sans option), l'adaptateur est appelé ; prix invalide refusé."""

    class Jamais:
        def lancer(self, *a, **k):
            raise AssertionError("G : commande lancée malgré une consigne au-delà du plafond")

    def test_sain_et_artefacts(self):
        ok = Resultat("VERDICT: survit", [], 0.01, "ok")
        prix = AC.prix_caractere_commande(10.0)
        e = T.AdaptateurEtageV64(AdaptateurFaux(ok), AdaptateurFaux(ok), prix_caractere_usd={"kimi": prix, "argon": prix})
        self.assertIs(e.lancer(v5.ROLE_LECTEUR, "x" * 29_999, "/x/lecteur", 0.1, 2), ok)  # 0,09999 USD ≤ 0,1 : lancée
        e = T.AdaptateurEtageV64(self.Jamais(), self.Jamais(), prix_caractere_usd={"kimi": prix, "argon": prix})
        r = e.lancer(v5.ROLE_LECTEUR, "x" * 30_001, "/x/lecteur", 0.1, 2)  # 0,100003 USD > 0,1 : rien lancé
        self.assertTrue(AC.rien_envoye(r) and e.appels[-1]["verification_prealable"])
        self.assertEqual((r.statut, r.cout_declare_usd, e.appels[-1]["taille_consigne"]), ("budget_depasse", 0.0, 30_001))
        sans = T.AdaptateurEtageV64(AdaptateurFaux(ok), AdaptateurFaux(ok))  # à blanc sans option : contrôle inactif, dit
        self.assertEqual(sans.prix_caractere_usd, {"kimi": None, "argon": None})
        self.assertIs(sans.lancer(v5.ROLE_LECTEUR, "x" * 10 ** 6, "/x/lecteur", 0.1, 2), ok)
        for mauvais in (0.0, -1e-6, float("nan"), float("inf"), True, "1e-6"):
            with self.subTest(prix=mauvais), self.assertRaises(T.TourRefuse):
                T.AdaptateurEtageV64(ok, ok, prix_caractere_usd={"argon": mauvais})


class PrixPasseALEtage(Tranche):
    """G (R5) : `jouer_etage` passe à l'étage v5 le prix d'un caractère du relais de l'expérimentateur, dont la vérification
    préalable (l. 468) joue alors : consigne au-delà du reste de la borne → fin des tours, rien envoyé, carte jugée sur ce qu'elle a
    exécuté (ici rien : « non concluant »), jamais un arrêt ; le vérificateur est contrôlé par l'adaptateur de l'étage v64 ; prix
    d'essai réaliste : rien ne mord ; sans prix (artefact : la v63), la l. 468 ne joue pas."""
    ROLES = {"experimentateur": ("e", "fa"), "verificateur": ("v", "fb"), "relais": {"experimentateur": "kimi", "verificateur": "argon"}}

    def jouer(self, nom, prix):
        exp, ver = T.AdaptateurExperimentateurScripte(), T.AdaptateurVerificateurScripte()
        ad = T.AdaptateurEtageV64(exp, ver, prix_caractere_usd=prix)
        carte = T.carte_servie("F-0000000000f1", MONDE["loi"], "reel")
        resume = T.jouer_etage(os.path.join(self.d, nom, "etage"), [carte], {carte["identifiant"]: MONDE["loi"]}, MONDE, 5,
                               f"essai|g|{nom}", A.choisir_executeur("factice")[0], ad, self.ROLES, T.Compteur(1e9, 3600.0), [],
                               moteur="simule", environnement=T.ENV_A_BLANC)[0]
        return resume, ad, exp, ver

    def test_espion_le_prix_arrive_a_l_etage(self):
        vus = []

        def espion(adaptateur, dossier, *, reglages, **kw):
            vus.append(dict(reglages))
            raise RuntimeError("espion : arrêt après les réglages")

        for i, prix in enumerate(({"kimi": 1e-5, "argon": 2e-5}, None)):
            with unittest.mock.patch.object(T, "jouer_etage_v57", espion), self.assertRaisesRegex(RuntimeError, "espion"):
                self.jouer(f"espion-{i}", prix)
        self.assertEqual([v["prix_caractere_usd"] for v in vus], [1e-5, None], "G : prix de l'expérimentateur non passé à l'étage")

    def test_sain_prix_d_essai_rien_ne_mord(self):
        prix = AC.prix_caractere_commande(10.0)
        resume, ad, exp, ver = self.jouer("sain", {"kimi": prix, "argon": prix})
        self.assertEqual(resume["comptes"]["survit"], 1)
        self.assertTrue(exp.appels and ver.appels)
        self.assertFalse(any(a["rien_envoye"] for a in ad.appels))

    def test_artefact_consignes_au_dela_du_plafond(self):
        resume, ad, exp, ver = self.jouer("cher", {"kimi": 1.0, "argon": 1.0})  # un dollar par caractère : tout dépasse
        f = resume["par_fiche"][0]
        self.assertIn("en entrée seule au prix prudent", f["fin_des_tours"] or "", "G : la vérification préalable de l'étage (l. 468) ne joue pas")
        self.assertIn("rien envoyé", f["fin_des_tours"])
        self.assertEqual((f["statut"], f["verdict"], f["tours"]), ("testée", "non concluant", 0))
        self.assertEqual(exp.appels, [], "G : expérimentateur appelé au-delà du reste de la borne")
        self.assertEqual(ver.appels, [], "G : vérificateur appelé au-delà de son plafond (vérification préalable de l'étage v64)")
        self.assertEqual(f["lecteur"]["verdict"], "non concluant")
        self.assertTrue(ad.appels and all(a["rien_envoye"] and a["verification_prealable"] for a in ad.appels))
        _, _, exp0, _ = self.jouer("sans-prix", None)
        self.assertTrue(exp0.appels)


# --- v64, H : durée de l'étage 1 gelée à 72 heures (décision de Lazar, R-1294) ------------------------------------------------------


class DureeR1294(unittest.TestCase):
    """H (R-1294), R5 : la durée gelée de l'étage 1 vaut 72 h dans le code ; le plan du texte scellé qui porte 72 est accepté (cas
    sain) ; toute autre durée est refusée en mode décisif (artefacts : 24, la valeur v63 ; 71,5 ; 72,5 ; 4 ; 10⁹) ; à blanc, 72 h par
    défaut ; le `Compteur` à 72 h permet l'égalité et arrête une seconde au-delà. Chemin réel : `CheminReelVerifierSeulement`."""

    def test_sain(self):
        self.assertEqual(T.DUREE_ETAGE_1_H, 72.0)
        self.assertEqual(LANCEUR.lire_plan(texte_plan())["duree_etage_1_h"], 72.0)
        self.assertEqual(LANCEUR.lire_plan(texte_plan(duree_etage_1_h="72,0"))["duree_etage_1_h"], 72.0)
        self.assertEqual(LANCEUR.A_BLANC["duree_max_h"], 72.0)
        h = [1000.0]
        c = T.Compteur(1e9, T.DUREE_ETAGE_1_H * 3600.0, None, lambda: h[0])
        h[0] += 72 * 3600.0
        c.verifier_duree()  # 72 h = plafond : permis
        h[0] += 1.0
        with self.assertRaisesRegex(T.ArretTour, "plafond de durée"):
            c.verifier_duree()

    def test_artefacts(self):
        for d in (24, 71.5, 72.5, 4, "1e9"):
            with self.subTest(duree=d), self.assertRaisesRegex(LANCEUR.PreenregistrementRefuse, "R-1294",
                                                                msg=f"H : durée de {d} h acceptée en mode décisif"):
                LANCEUR.lire_plan(texte_plan(duree_etage_1_h=d))


if __name__ == "__main__":
    unittest.main()
