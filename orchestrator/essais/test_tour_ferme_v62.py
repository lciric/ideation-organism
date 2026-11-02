"""Essais de la v62 — cœur (`pole/tour_ferme_v62.py`), évaluateur servi (`pole/evaluateur_lois_v62.py`), lecture gelée
(`pole/lecture_tour_ferme_v62.py`), lanceur (`demonstrations/tour_ferme_v62.py`) et programme de lecture
(`demonstrations/lire_tour_ferme_v62.py`) : corrections B7, B8, B9 et C8 à C21 de la contre-lecture 2 (étage 1). Chaque
correction : un cas sain et un artefact (R5). Les courses passent par **le chemin réel** (`ProposeurAdaptateur`,
`AdaptateurEtageV62`) avec des doublures scriptées qui ne lisent que le texte servi ; elles sont jouées dans ce processus
(lanceur appelé par `principal`) pour que le banc de mutations les atteigne. Aucun réseau, aucun modèle."""

import contextlib
import importlib.util
import io
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import evaluateur_lois_v62 as EV  # noqa: E402
from pole import lecture_tour_ferme_v61 as L61  # noqa: E402
from pole import lecture_tour_ferme_v62 as L  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole import tests_de_mort_v5 as v5  # noqa: E402
from pole import tour_ferme_v62 as T  # noqa: E402
from pole.adaptateurs import Resultat  # noqa: E402
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


LANCEUR = _charger("essais.lanceur_tour_ferme_v62", "tour_ferme_v62.py")
LECTEUR = _charger("essais.lecteur_tour_ferme_v62", "lire_tour_ferme_v62.py")
MONDE = A.charger_monde(RACINE)
DEC = {"d7": "archive_du_bras_reel", "d9": "mecanique"}
PETIT = ["--cartes-par-proposeur", "2", "--cartes-reference", "3", "--m-e-bh", "11", "--bac", "factice"]
MOTS_INTERDITS = ("témoin", "temoin", "ALEA", "COPIE", "kimi", "argon", "scripte", "W-", "G1-", "G2-", "G3-", "aleatoire", "recopie")


def courir(sortie, *opts):
    """Le lanceur, dans ce processus ; rend (code, sortie d'erreur)."""
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        code = LANCEUR.principal([sortie, "--etage", "1", *opts])
    return code, err.getvalue()


def rapport(sortie):
    with open(os.path.join(sortie, "tour-ferme-v1-etage1.json"), encoding="utf-8") as f:
        return json.load(f)


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
    """Une tranche v62 dans un dossier temporaire (épisodes et évaluateur)."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v62-")
        self.addCleanup(shutil.rmtree, self.d, True)
        self.tranche = T.creer_tranche(self.d, MONDE, 5, "essai|v62")
        self.ep = os.path.join(self.d, "tranche", "episodes.csv")


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


# --- C9 (B8) : grammaire servie et gabarit -------------------------------------------------------------------------------------


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
            self.assertIsNone(T.completer_carte(art, "F-0000000000dd")[0], art)


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


class Garde7(unittest.TestCase):
    def test_temoin_jamais_dans_archive_ni_vue(self):
        h = {"generation_lue": 1, "bilan_sha256": "a" * 64, "retenues": ["F-000000000001"], "archive": {"F-000000000001": MONDE["loi"]},
             "empreintes_lues": {}}
        T.exiger_sans_temoin(h, {"W-abc", "F-0000000000ff"})
        for intrus in ("W-abc", "F-0000000000ff"):  # identifiant réel ou servi d'un témoin
            h2 = dict(h, archive=dict(h["archive"], **{intrus: MONDE["loi"]}))
            with self.assertRaises(T.TemoinRetenu):
                T.exiger_sans_temoin(h2, {"W-abc", "F-0000000000ff"})


# --- C12 (I10) : proposeur en échec, C13 (I12) : parts des relais -----------------------------------------------------------


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
        e = T.AdaptateurEtageV62(AdaptateurFaux(ok), AdaptateurFaux(ok))
        self.assertIs(e.lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2), ok)
        relais = Resultat("", [], 0.0, "budget_depasse")  # 402 du relais avant toute dépense
        e = T.AdaptateurEtageV62(AdaptateurFaux(relais), AdaptateurFaux(ok))
        with self.assertRaises(T.ArretTour):
            e.lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2)
        e = T.AdaptateurEtageV62(AdaptateurFaux(ok), AdaptateurFaux(ok))
        e.parts = {"kimi": 0.4}
        with self.assertRaises(T.ArretTour):
            e.lancer(v5.ROLE_EXPERIMENTATEUR, "c", "/x/tour-001", 0.5, 2)


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


# --- C21 : moteur de l'étage ; étage v62 de bout en bout sur une carte --------------------------------------------------------


class EtageV62(Tranche):
    def jouer(self, moteur):
        roles = {"experimentateur": ("e", "fa"), "verificateur": ("v", "fb"), "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
        ad = T.AdaptateurEtageV62(T.AdaptateurExperimentateurScripte(), T.AdaptateurVerificateurScripte())
        carte = T.carte_servie("F-0000000000e1", MONDE["loi"], "reel")
        compteur = T.Compteur(1e9, 3600.0)
        return T.jouer_etage(os.path.join(self.d, moteur, "etage"), [carte], {carte["identifiant"]: MONDE["loi"]}, MONDE, 5, "essai|c21",
                             A.choisir_executeur("factice")[0], ad, roles, compteur, [], moteur=moteur, environnement=T.ENV_A_BLANC)

    def test_sain_simule_et_factice_refuse_au_moteur_reel(self):
        self.assertEqual((LANCEUR.moteur_de_l_etage(True), LANCEUR.moteur_de_l_etage(False)), ("claude-sdk", "simule"), "C21")
        resume, _, _, _, cc = self.jouer("simule")
        self.assertEqual(resume["comptes"]["survit"], 1)
        self.assertTrue(all(x["ok"] and not x["sans_objet"] for x in cc.values()))
        self.assertEqual(resume["quotas"]["memoire_mo"], 768)
        with self.assertRaises(Exception) as e:
            self.jouer("claude-sdk")
        self.assertIn("factice", str(e.exception))


# --- lanceur : plan de l'étage 1, garde 6 complète (C17), machine jetable (C11), monde (C20) ------------------------------


def texte_plan(**chg):
    p = {"generations_etage_1": 3, "cartes_par_proposeur": 6, "cartes_reference": 12, "m_e_bh_etage_1": 19, "plafond_etage_1_usd": 15,
         "plafond_kimi_usd": 12, "plafond_argon_usd": 3, "duree_etage_1_h": 4, "d7": "archive_du_bras_reel", "d9": "mecanique",
         "configuration_sha256": "a" * 64, "go": "GO-2026-11-03-01", "monde_sha256": MONDE["sha256"],
         "ordre_des_bras": "reel, recopie_melange, aleatoire"}
    p.update(chg)
    return LANCEUR.DEBUT_PLAN + "\n" + "\n".join(f"{k}: {v}" for k, v in p.items() if v is not None) + "\n" + LANCEUR.FIN_PLAN


def texte_scellable(marqueur_hors_zone=False):
    emp = "\n".join(f"{sha256_fichier(os.path.join(RACINE, r))}  {r}" for r in LANCEUR.FICHIERS_GELES)
    return ("# essai\n" + ("<<DECISION_D2>>\n" if marqueur_hors_zone else "") + LANCEUR.DEBUT_ZONE_2 + "\nétage 2 : <<CASE_T>> <<DECISION_D8>>\n"
            + LANCEUR.FIN_ZONE_2 + "\n" + texte_plan() + "\n" + LANCEUR.DEBUT_EMPREINTES + "\n" + emp + "\n" + LANCEUR.FIN_EMPREINTES + "\n")


class PlanEtage1(unittest.TestCase):
    def test_sain_et_artefacts(self):
        p = LANCEUR.lire_plan(texte_plan())
        self.assertEqual((p["decisions"], p["plafond_kimi_usd"], p["monde_sha256"]), (DEC, 12.0, MONDE["sha256"]))
        for chg in ({"plafond_kimi_usd": 13}, {"d8": "predicteur_connu"}, {"monde_sha256": None}, {"d9": "aiguilleur"},
                    {"m_e_bh_etage_1": 11}, {"ordre_des_bras": "aleatoire, reel, recopie_melange"}, {"go": "oui"}):
            with self.assertRaises(T.TourRefuse, msg=str(chg)):
                LANCEUR.lire_plan(texte_plan(**chg))


class Garde6Complete(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v62-prereg-")
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
        with contextlib.redirect_stderr(err):
            self.assertEqual(LANCEUR.principal([s, "--etage", "2", "--a-blanc", "--graine", "7", "--bac", "factice"]), 2)
        self.assertIn("aucun étage 2", err.getvalue())


# --- courses par le chemin réel (doublures branchées), dans ce processus ---------------------------------------------------------


class CourseSaine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v62-course-")
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
        self.assertEqual(rec["contextes_cherches"], 6)
        self.assertIsInstance(self.r["releve"]["vd_distinctes"], dict)
        m = json.load(open(os.path.join(self.s, "manifeste.json")))
        self.assertEqual((m["moteur_etage"], set(m["code_sha256"])), ("simule", set(LANCEUR.FICHIERS_GELES)))

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
                # ce que la fiche apporte au préenregistrement court (le reste est le texte gelé de l'étage, le même pour tous)
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
        self.assertEqual((l["etage_1"]["issue_etage_1"], l["releve"]["sha256"]), ("tient", sha))
        faux = os.path.join(self.d, "faux")
        shutil.copytree(self.s, faux)
        os.remove(os.path.join(faux, "tour-ferme-v1-etage1.json.sha256"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(LECTEUR.principal([faux, lec + "3"]), 2, "C18 : relevé non scellé lu")


class CourseMuette(unittest.TestCase):
    """B9 (C10) : relevés **produits par le cœur**, bras réel muet en génération 1, puis en générations 1 et 2."""

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v62-muet-")
        cls.r = {}
        for nom, sc in (("g1", "muet:1"), ("g12", "muet:1,2")):
            s = os.path.join(cls.d, nom)
            code, err = courir(s, "--a-blanc", "--graine", "11", "--generations", "3", "--scenario-proposeur", sc, *PETIT)
            cls.r[nom] = (code, err, rapport(s) if code == 0 else None)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, True)

    def test_B9_tient_sur_course_saine(self):
        for nom, (code, err, r) in self.r.items():
            self.assertEqual(code, 0, err[-2000:])
            rel = r["releve"]
            self.assertEqual(rel["generations_jouees"]["recopie_melange"], [3] if nom == "g1" else [])
            l = L.lire_etage1(rel)
            self.assertTrue(l["criteres"]["T1"], f"B9 ({nom}) : T1 manque sur une course saine")
            self.assertEqual(l["issue_etage_1"], "tient", (nom, l["criteres"]))
            self.assertEqual(len(rel["boucle"]["lectures"]), 6)
        self.assertFalse(L61.lire_etage1(self.r["g12"][2]["releve"])["criteres"]["T1"])  # la lecture v61 disait T1 manqué


class Arrets(unittest.TestCase):
    """C12, C13, garde 10 de bout en bout : arrêt → code 3, relevé partiel scellé, aucune issue lue."""

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v62-arrets-")
        cls.r = {}
        court = ["--generations", "2", "--cartes-par-proposeur", "1", "--cartes-reference", "2", "--m-e-bh", "9", "--bac", "factice"]
        for nom, opts in (("session", ["--scenario-experimentateur", "erreur"]), ("refus", ["--scenario-proposeur", "refus"]),
                          ("arrondi", ["--scenario-experimentateur", "arrondi:2"]), ("fabrique", ["--scenario-experimentateur", "fabrique"]),
                          ("part", ["--plafond-usd", "1.0", "--plafond-kimi-usd", "0.8", "--plafond-argon-usd", "0.2"])):
            s = os.path.join(cls.d, nom)
            code, err = courir(s, "--a-blanc", "--graine", "11", *court, *opts)
            cls.r[nom] = (code, err, rapport(s) if os.path.isfile(os.path.join(s, "tour-ferme-v1-etage1.json")) else None)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, True)

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
            self.assertEqual(l["n1"], "arret", nom)
        self.assertIn("EtageInterrompu", [x.get("type") for x in self.r["session"][2]["releve"]["boucle"]["incidents"]], "C12")


# --- lecture gelée v62 sur des relevés synthétiques (C10, C16) ----------------------------------------------------------------

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


class LectureV62(unittest.TestCase):
    def test_sain_tient_et_discrimine(self):
        r = L.lire_etage1(releve_sain())
        self.assertEqual((r["issue_etage_1"], r["issue_a4"], r["passes_attendues"], r["lectures_attendues"]), ("tient", "discrimine", 8, 6))

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


# --- fermeture du code gelé et vrai bac à sable ---------------------------------------------------------------------------------


class Fermeture(unittest.TestCase):
    def test_fichiers_geles_couvrent_les_imports(self):
        code = ("import sys, importlib.util, os\n"
                f"R = {RACINE!r}\nsys.path.insert(0, R)\nvus = set()\norig = importlib.util.spec_from_file_location\n"
                "def f(n, l=None, *a, **k):\n    vus.add(os.path.relpath(str(l), R)); return orig(n, l, *a, **k)\n"
                "importlib.util.spec_from_file_location = f\n"
                "for n, fi in (('l', 'demonstrations/tour_ferme_v62.py'), ('lt', 'demonstrations/lire_tour_ferme_v62.py')):\n"
                "    s = importlib.util.spec_from_file_location(n, os.path.join(R, fi)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
                "    if n == 'l': m.charger_goodhart_v2().charger_ideation_v8()\n"
                "import pole.configuration_v56, pole.relais\n"
                "fs = {os.path.relpath(x.__file__, R) for x in list(sys.modules.values()) if getattr(x, '__file__', None) and x.__file__.startswith(R + os.sep)}\n"
                "print('\\n'.join(sorted(fs | vus)))")
        out = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True, timeout=120, cwd=RACINE)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        importes = {l for l in out.stdout.splitlines() if l and not l.startswith("essais")}
        self.assertEqual(sorted(importes - set(LANCEUR.FICHIERS_GELES)), [])
        self.assertIn("pole/evaluateur_lois_v62.py", LANCEUR.FICHIERS_GELES)  # servi, jamais importé : gelé quand même
        for r in LANCEUR.FICHIERS_GELES:
            self.assertTrue(os.path.isfile(os.path.join(RACINE, r)), r)


class BacReelV62(unittest.TestCase):
    def test_a_blanc_dans_le_vrai_bac(self):
        if not shutil.which("bwrap"):
            self.skipTest("bwrap absent")
        uid = []
        if os.geteuid() == 0:
            ok = shutil.which("setpriv") and subprocess.run(["setpriv", "--reuid", "64097", "--regid", "64097", "--clear-groups", "--no-new-privs",
                                                            "--", "/usr/bin/id", "-u"], capture_output=True, timeout=20).stdout.strip() == b"64097"
            if not ok:
                self.skipTest("superutilisateur sans setpriv utilisable")
            uid = ["--utilisateur-bac", "64097"]
        d = tempfile.mkdtemp(prefix="essai-v62-bac-")
        self.addCleanup(shutil.rmtree, d, True)
        r = subprocess.run([sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "tour_ferme_v62.py"), os.path.join(d, "s"),
                            "--etage", "1", "--a-blanc", "--graine", "12", "--bac", "reel", *uid, "--generations", "2",
                            "--cartes-par-proposeur", "1", "--cartes-reference", "2", "--m-e-bh", "9"],
                           capture_output=True, text=True, timeout=900, cwd=RACINE)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        rap = rapport(os.path.join(d, "s"))
        et = [l for l in rap["journal"] if l["evenement"] == "etage-tests-de-mort"]
        self.assertTrue(et and all(l["bac_a_sable"] == "bwrap" and l["factice"] is False for l in et))
        self.assertTrue(all(c["contre_calcul_ok"] is True for c in rap["releve"]["cartes"] if c.get("verdict")))


if __name__ == "__main__":
    unittest.main()
