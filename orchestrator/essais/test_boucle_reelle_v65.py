"""Essais de la v65 — cœur (`pole/boucle_reelle_v65.py`), lecture gelée (`pole/lecture_boucle_reelle_v65.py`), lanceur
(`demonstrations/boucle_reelle_v65.py`), programme de lecture (`demonstrations/lire_boucle_reelle_v65.py`), bloc du texte
(`demonstrations/bloc_v65_boucle_reelle.py`) et configuration v5 (`exemples/configuration-tour-ferme-v5.json`).

Chaque garde et chaque issue : un cas sain et un artefact (R5). Pièces du brouillon 1 (§ 12) : M1 `HeritageDepart` (garde 17) ;
M2 `JeuPlante`, `ClasseCouverte` (garde 19) ; M3 `JugementAvecArchive` (défaut de la v64 reproduit puis corrigé ; garde 18) ; M4
`BrasReelSeul` (garde 20), `Generation2LitLaSelection`, `CopiesGarde21` (garde 21) ; M5 `LectureGelee` (C1 à C6, A1 à A4, ordre) ;
M6 `ConfigurationV5` (commandes v6 nommées) ; gardes de dépense `GardesDeDepense` ; bac réel `BacReel` (garde 22 et garde 3 ; l'essai
qui exige `bwrap` est déclaré « non joué » sous `POLE_ESSAI_BAC_REEL_NON_JOUE=1`) ; plan et texte scellé `PlanV65`, `Garde6V65` ;
`FermetureV65` (bloc gelé). Les courses passent par le chemin réel (doublures scriptées de la v64, exécuteur factice déclaré) et sont
jouées dans ce processus (lanceur appelé par `principal`) pour que le banc de mutations les atteigne. Aucun réseau, aucun modèle."""

import ast
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
import re
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
from pole import boucle_fermee_v59 as bf  # noqa: E402
from pole import boucle_reelle_v65 as B  # noqa: E402
from pole import lecture_boucle_reelle_v65 as L  # noqa: E402
from pole import tour_ferme_v64 as T  # noqa: E402
from pole.outils import ecrire_json_scelle, ecrire_scelle, json_canonique, sha256_fichier  # noqa: E402


def _charger(nom, fichier):
    if nom in sys.modules:
        return sys.modules[nom]
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, "demonstrations", fichier))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nom] = m  # nommé sous « essais. » : le banc de mutations l'atteint
    spec.loader.exec_module(m)
    return m


LANCEUR = _charger("essais.lanceur_boucle_reelle_v65", "boucle_reelle_v65.py")
LECTEUR = _charger("essais.lecteur_boucle_reelle_v65", "lire_boucle_reelle_v65.py")
BLOC = _charger("essais.bloc_v65_boucle_reelle", "bloc_v65_boucle_reelle.py")
MONDE = A.charger_monde(RACINE)
K1 = BLOC.K1_DU_BROUILLON
with open(LANCEUR.TEXTE_A_BLANC, encoding="utf-8") as _f:
    TEXTE = _f.read()
DEPOT_TRAVAIL = "/home/user/controle-ia-travail"
DOSSIER_V4 = os.path.join(DEPOT_TRAVAIL, "docs/notes/ideation-organisme-v1/tour-ferme-etage1-v1")
REGISTRE_GO = os.path.join(DEPOT_TRAVAIL, "registres/go.md")
COMMIT_COMMANDES = "12f9e0e38f2cf7adb61a9c3ddf0ee4c5c66556d9"
MOTS_INTERDITS = ("temoin", "plantee", "plantée", "jeu-plante", "V1", "V2", "V3", "V4", "F1", "F2", "F3", "F4", "T-ELIM", "T-MAL", "kimi",
                  "argon", "scripte")  # « témoin » (accentué) est un mot de l'étage v5 lui-même (ligne « RESULTAT »)


def courir(sortie, *opts):
    """Le lanceur, dans ce processus ; rend (code, sortie d'erreur)."""
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        code = LANCEUR.principal([sortie, *opts])
    return code, err.getvalue()


def rapport(sortie):
    with open(os.path.join(sortie, LANCEUR.SORTIE), encoding="utf-8") as f:
        return json.load(f)


def texte_avec(plan=None, jeu=None, bloc_jeu=None, **chg):
    """Le texte du mode à blanc avec un plan changé (`chg`) et/ou un jeu changé (bloc recalculé, empreinte du plan mise à jour sauf
    si `chg` la fixe)."""
    m = BLOC.morceaux()
    if jeu is not None:
        bloc_jeu = B.bloc_jeu_plante(jeu)
        chg.setdefault("jeu_plante_sha256", hashlib.sha256(json_canonique(jeu)).hexdigest())
    p = BLOC.texte_plan(chg.pop("configuration_sha256", m["configuration_sha256"]), m["heritage_sha256"], m["jeu_sha256"],
                        m["monde"]["sha256"], **chg)
    return "# essai\n\n" + p + "\n\n" + (bloc_jeu if bloc_jeu is not None else m["bloc_jeu"]) + "\n"


def jeu_du_brouillon():
    return B.jeu_plante_du_brouillon(MONDE, K1)


_COURSE = {}


def course_saine():
    """Une course à blanc complète (deux générations, six cartes par proposeur, exécuteur factice déclaré), jouée une fois."""
    if "r" not in _COURSE:
        d = tempfile.mkdtemp(prefix="essai-v65-course-")
        s = os.path.join(d, "s")
        code, err = courir(s, "--a-blanc", "--graine", "11", "--bac", "factice")
        _COURSE.update(d=d, s=s, code=code, err=err, r=rapport(s) if os.path.isfile(os.path.join(s, LANCEUR.SORTIE)) else None)
    return _COURSE


def tearDownModule():
    if _COURSE.get("d"):
        shutil.rmtree(_COURSE["d"], True)


# --- M1 : héritage de départ (garde 17) ------------------------------------------------------------------------------------------


class HeritageDepart(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v65-heritage-")
        self.addCleanup(shutil.rmtree, self.d, True)

    def ecrire(self, octets, nom="h.json"):
        p = os.path.join(self.d, nom)
        with open(p, "wb") as f:
            f.write(octets)
        return p

    def test_sain_heritage_conforme_accepte(self):
        h = B.lire_heritage_depart(LANCEUR.HERITAGE_DEPART, TEXTE, jeu_du_brouillon())
        self.assertEqual(h["archive"], {"K1": K1})
        self.assertEqual(h["declarees"], {"K1": "connue, déclarée"})
        self.assertEqual(h["bilan_sha256"], sha256_fichier(LANCEUR.HERITAGE_DEPART))
        self.assertEqual((h["retenues"], h["generation_lue"]), ([], 0))
        self.assertEqual(bf.vue_pour_proposeur(h)["lois_retenues"], [{"identifiant": "K1", "loi": K1}])

    def test_artefact_empreinte_absente_ou_differente(self):
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "empreinte"):
            B.lire_heritage_depart(LANCEUR.HERITAGE_DEPART, texte_avec(heritage_depart_sha256="0" * 64))
        sans = TEXTE.replace("heritage_depart_sha256: ", "heritage_depart_sha256_absente: ")
        with self.assertRaises(B.BoucleRefusee):
            B.lire_heritage_depart(LANCEUR.HERITAGE_DEPART, sans)

    def test_artefact_k1_alteree_texte_inchange(self):
        k = copy.deepcopy(K1)
        k["biais"][1] = 0.941699
        p = self.ecrire(B.octets_heritage_depart(k))
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "empreinte"):
            B.lire_heritage_depart(p, TEXTE)

    def test_artefacts_contenu_meme_si_l_empreinte_est_au_texte(self):
        o = B.objet_heritage_depart(K1)
        cas = {"loi plantée sous un autre nom": dict(o, lois=dict(o["lois"], K2={"loi": MONDE["loi"], "statut": "connue, déclarée"})),
               "statut non déclaré": dict(o, lois={"K1": {"loi": K1, "statut": "retenue"}}),
               "génération 1": dict(o, generation=1), "autre version": dict(o, version="heritage-depart-v64")}
        for nom, obj in cas.items():
            with self.subTest(cas=nom):
                octets = (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
                p = self.ecrire(octets, nom.replace(" ", "-") + ".json")
                with self.assertRaises(B.HeritageDepartRefuse):
                    B.lire_heritage_depart(p, texte_avec(heritage_depart_sha256=hashlib.sha256(octets).hexdigest()))
        octets = B.octets_heritage_depart(MONDE["loi"])  # K1 = V1 (loi plantée dans l'héritage)
        p = self.ecrire(octets, "k1-egale-v1.json")
        t = texte_avec(heritage_depart_sha256=hashlib.sha256(octets).hexdigest())
        self.assertEqual(B.lire_heritage_depart(p, t)["archive"], {"K1": MONDE["loi"]})  # sans le jeu, la forme seule
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "loi plantée"):
            B.lire_heritage_depart(p, t, jeu_du_brouillon())

    def test_artefact_lien_symbolique(self):
        lien = os.path.join(self.d, "lien.json")
        os.symlink(LANCEUR.HERITAGE_DEPART, lien)
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "régulier"):
            B.lire_heritage_depart(lien, TEXTE)

    def test_lanceur_code_2_sans_repli(self):
        k = copy.deepcopy(K1)
        k["poids"][1][0] = -0.8
        p = self.ecrire(B.octets_heritage_depart(k))
        s = os.path.join(self.d, "s")
        code, err = courir(s, "--a-blanc", "--graine", "7", "--bac", "factice", "--heritage-depart", p)
        self.assertEqual(code, 2, err)
        self.assertIn("HeritageDepartRefuse", err)
        self.assertFalse(os.path.exists(s))


# --- M2 : jeu planté lu dans le texte (garde 19) ; classe couverte -----------------------------------------------------------------


class ClasseCouverte(unittest.TestCase):
    def test_sain_les_quatre_fausses_du_brouillon(self):
        j = jeu_du_brouillon()
        self.assertEqual({n: B.classer_couverte(j["fausses"][n]["loi"], {"K1": K1}) for n in B.FAUSSES},
                         {"F1": "T17s", "F2": "T03u", "F3": "T03b", "F4": "T05s"})

    def test_artefacts_hors_classe(self):
        """Les fausses de la v64 (S-F1, S-F2, S-F4, T-ANTI : lois inconnues du pôle) et les formes non couvertes du nul v8."""
        v = MONDE["loi"]
        anti = {"type": "softmax", "poids": [[-w for w in l] for l in v["poids"]], "biais": list(v["biais"])}
        unif = {"type": "fixe", "probas": [1.0, 1.0, 1.0]}
        cas = {"S-F1": MONDE["fausses"]["S-F1"], "S-F2": MONDE["fausses"]["S-F2"], "S-F4": MONDE["fausses"]["S-F4"], "T-ANTI": anti,
               "par morceaux": {"type": "si_sinon", "condition": {"indice": 0, "seuil": 0.0}, "si": K1, "sinon": unif},
               "composition": {"type": "transformee", "base": K1, "puissance": 1.2, "melange_aveugle": {"lambda": 0.2, "probas": [1, 1, 1]}},
               "oscillation": {"type": "transformee", "base": K1, "oscillation": {"amplitude": 0.5, "frequence": 1.0, "trait": 0, "issue": 1}},
               "mélange avec une loi inconnue": {"type": "melange", "composantes": [K1, v], "poids": [0.5, 0.5]},
               "tempérée d'une loi inconnue": {"type": "transformee", "base": v, "puissance": 1.2},
               "aveugle seule": unif}
        for nom, loi in cas.items():
            with self.subTest(cas=nom):
                self.assertIsNone(B.classer_couverte(loi, {"K1": K1}))
        self.assertIsNone(B.classer_couverte(K1, {}), "archive vide : rien n'est couvert")


class JeuPlante(unittest.TestCase):
    def test_sain_jeu_lu_a_l_octet(self):
        jeu, sha, octets = B.lire_jeu_plante(TEXTE, {"K1": K1})
        self.assertEqual(jeu, jeu_du_brouillon())
        self.assertEqual(sha, B.lire_plan(TEXTE)["jeu_plante_sha256"])
        self.assertIn(octets.decode("utf-8"), TEXTE)
        self.assertEqual(hashlib.sha256(octets).hexdigest(), sha)
        self.assertTrue(B.exiger_jeu_conforme(jeu, octets))

    def test_artefact_jeu_incomplet(self):
        j = jeu_du_brouillon()
        del j["fausses"]["F4"]
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "incomplet"):
            B.lire_jeu_plante(texte_avec(jeu=j), {"K1": K1})
        j = jeu_du_brouillon()
        del j["instruments"]["T-MAL"]
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "incomplet"):
            B.lire_jeu_plante(texte_avec(jeu=j), {"K1": K1})

    def test_artefact_fausse_hors_classe(self):
        for nom, loi in (("S-F2", MONDE["fausses"]["S-F2"]),
                         ("par morceaux", {"type": "si_sinon", "condition": {"sous_population": 0}, "si": K1, "sinon": MONDE["loi"]})):
            with self.subTest(cas=nom):
                j = jeu_du_brouillon()
                j["fausses"]["F2"]["loi"] = loi
                with self.assertRaises(B.FausseHorsClasse):
                    B.lire_jeu_plante(texte_avec(jeu=j), {"K1": K1})
        with self.assertRaises(B.FausseHorsClasse):  # même jeu, archive de départ autre que K1
            B.lire_jeu_plante(TEXTE, {"K9": MONDE["loi"]})

    def test_artefacts_octet_et_empreinte(self):
        j = jeu_du_brouillon()
        j["vraies"]["V3"]["puissance"] = 0.09
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "garde 19"):  # une loi changée, empreinte du plan inchangée
            B.lire_jeu_plante(texte_avec(bloc_jeu=B.bloc_jeu_plante(j)), {"K1": K1})
        non_canonique = B.DEBUT_JEU + "\n```json\n" + json.dumps(jeu_du_brouillon(), sort_keys=True) + "\n```\n" + B.FIN_JEU
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "canonique"):
            B.lire_jeu_plante(texte_avec(bloc_jeu=non_canonique), {"K1": K1})
        jeu, _, octets = B.lire_jeu_plante(TEXTE, {"K1": K1})
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "garde 19"):
            B.exiger_jeu_conforme(j, octets)
        j = jeu_du_brouillon()
        j["fausses"]["F3"]["ligne_du_banc"] = "T03u"
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "déclarée"):
            B.lire_jeu_plante(texte_avec(jeu=j), {"K1": K1})
        j = jeu_du_brouillon()
        j["instruments"]["T-ELIM"]["seuil"] = T.SEUIL_TEST
        with self.assertRaises(B.JeuPlanteRefuse):
            B.lire_jeu_plante(texte_avec(jeu=j), {"K1": K1})
        with self.assertRaises(B.JeuPlanteRefuse):
            B.lire_jeu_plante(TEXTE + "\n" + B.DEBUT_JEU + "\n" + B.FIN_JEU, {"K1": K1})  # bloc en double

    def test_lanceur_code_2(self):
        d = tempfile.mkdtemp(prefix="essai-v65-jeu-")
        self.addCleanup(shutil.rmtree, d, True)
        j = jeu_du_brouillon()
        j["fausses"]["F1"]["loi"] = MONDE["fausses"]["S-F1"]
        p = os.path.join(d, "texte.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(texte_avec(jeu=j))
        code, err = courir(os.path.join(d, "s"), "--a-blanc", "--graine", "7", "--bac", "factice", "--texte", p)
        self.assertEqual(code, 2)
        self.assertIn("FausseHorsClasse", err)
        self.assertFalse(os.path.exists(os.path.join(d, "s")))


# --- M3 : jugement avec l'archive (garde 18) ---------------------------------------------------------------------------------------


class JugementAvecArchive(unittest.TestCase):
    """Le défaut de la v64 (lois plantées jugées sans l'archive : fausses de la classe couverte promues) reproduit, puis corrigé."""

    def plantees(self, racine, tache):
        return [(n, c) for n, _, c in B.plantees_generation_1(jeu_du_brouillon(), racine, tache) if n in B.FAUSSES]

    def test_defaut_v64_reproduit_puis_corrige(self):
        promues_v64 = 0
        for racine in (20261107, 7, 11):
            tache = f"essai-v65|m3|{racine}"
            pl = self.plantees(racine, tache)
            _, promus, detail, _ = T.juger([], pl, MONDE, {"K1": K1}, racine, tache, 22)
            self.assertEqual({detail[c["identifiant"]]["membres_d_archive"] for _, c in pl}, {0}, "v64 : témoins jugés sans archive")
            promues_v64 += len(promus)
            _, promues, detail65, _ = B.juger_v65([], pl, MONDE, {"K1": K1}, racine, tache, 22)
            self.assertEqual({detail65[c["identifiant"]]["membres_d_archive"] for _, c in pl}, {4}, "M3 : membres d'archive de {K1}")
            self.assertEqual(promues, [], f"M3 : fausse de la classe couverte promue avec l'archive (racine {racine})")
            self.assertTrue(all(detail65[c["identifiant"]]["log_richesse_max"] <= 1e-6 for _, c in pl))
        self.assertGreater(promues_v64, 0, "l'artefact (canal de la v64) doit promouvoir au moins une fausse couverte")

    def test_vraies_promues_avec_l_archive(self):
        racine, tache = 20261107, "essai-v65|m3|vraies"
        pl = [(n, c) for n, _, c in B.plantees_generation_1(jeu_du_brouillon(), racine, tache) if n in ("V1", "V2")]
        _, promues, detail, _ = B.juger_v65([], pl, MONDE, {"K1": K1}, racine, tache, 22)
        self.assertEqual(len(promues), 2)
        self.assertTrue(all(detail[i]["log_e"] >= math.log(22 / 0.05) for i in promues))

    def test_seuil_hors_famille_log_m_sur_alpha(self):
        """Une loi plantée que le juge promeut (richesse ≥ 1/α) sans que son log e atteigne log(m/α) n'est pas promue (M3)."""
        vrai = A.juger_carte

        def juge(loi, monde, archive, racine, tache):
            ev, d = vrai(loi, monde, archive, racine, tache)
            if "|plantee=" in tache:
                ev = dict(ev, promue=True, marge_atteinte=True, trajectoire_log_w=[0.0, 3.5, 4.0])
            return ev, d

        racine, tache = 7, "essai-v65|seuil"
        pl = [(n, c) for n, _, c in B.plantees_generation_1(jeu_du_brouillon(), racine, tache) if n == "V3"]
        with unittest.mock.patch.object(A, "juger_carte", juge):
            _, promues, detail, _ = B.juger_v65([], pl, MONDE, {"K1": K1}, racine, tache, 22)
        i = pl[0][1]["identifiant"]
        self.assertEqual((promues, detail[i]["promue_seule"], detail[i]["log_e"]), ([], True, 4.0))

    def test_garde_18_sain_et_artefact(self):
        detail = {"a": {"membres_d_archive": 4}, "b": {"membres_d_archive": 4}}
        self.assertEqual(B.exiger_archive_des_plantees(detail, ["a", "b"], {"K1": K1}), 4)
        detail["b"]["membres_d_archive"] = 0
        with self.assertRaises(B.ArchiveDesPlanteesAbsente):
            B.exiger_archive_des_plantees(detail, ["a", "b"], {"K1": K1})
        self.assertTrue(issubclass(B.ArchiveDesPlanteesAbsente, T.ArretTour), "garde 18 : arrêt (code 3)")

    def test_garde_18_en_course(self):
        """Un juge des lois plantées sans archive (artefact) arrête la course : code 3, relevé partiel."""
        vrai = A.juger_carte

        def sans_archive(loi, monde, archive, racine, tache):
            return vrai(loi, monde, {} if "|plantee=" in tache else archive, racine, tache)

        d = tempfile.mkdtemp(prefix="essai-v65-g18-")
        self.addCleanup(shutil.rmtree, d, True)
        with unittest.mock.patch.object(A, "juger_carte", sans_archive):
            code, err = courir(os.path.join(d, "s"), "--a-blanc", "--graine", "7", "--bac", "factice", "--cartes-par-proposeur", "1")
        self.assertEqual(code, 3, err)
        self.assertIn("garde 18", rapport(os.path.join(d, "s"))["arret"])


# --- M4 : bras réel seul (garde 20) ; génération 2 ; copies (garde 21) -----------------------------------------------------------------


class BrasReelSeul(unittest.TestCase):
    def test_sain_et_artefacts(self):
        self.assertEqual(B.exiger_bras_reel_seul("reel_seul"), ("reel",))
        for autre in ("reel, recopie_melange, aleatoire", "trois_bras", "reel", None):
            with self.assertRaises(B.BrasRefuse):
                B.exiger_bras_reel_seul(autre)
        with self.assertRaises(B.BrasRefuse):
            B.lire_plan(texte_avec(bras="reel, recopie_melange, aleatoire"))
        d = tempfile.mkdtemp(prefix="essai-v65-bras-")
        self.addCleanup(shutil.rmtree, d, True)
        code, err = courir(os.path.join(d, "s"), "--a-blanc", "--graine", "7", "--bac", "factice", "--bras", "reel_et_references")
        self.assertEqual(code, 2)
        self.assertIn("BrasRefuse", err)
        self.assertFalse(os.path.exists(os.path.join(d, "s")))


class CourseSaine(unittest.TestCase):
    def test_course_complete(self):
        c = course_saine()
        self.assertEqual(c["code"], 0, c["err"][-2000:])
        r = c["r"]["releve"]
        self.assertEqual((r["version"], r["bras"], r["generations_jouees"], r["arret"]), (B.VERSION, "reel_seul", [1, 2], None))
        self.assertEqual(len(c["r"]["appels_proposeurs"][0]) + len(c["r"]["appels_proposeurs"][1]), 4, "D2 : deux appels par génération")
        self.assertEqual(sorted(os.listdir(os.path.join(c["s"]))), sorted(["bras-reel", "manifeste.json", "manifeste.json.sha256", "proposeurs",
                                                                           LANCEUR.SORTIE, LANCEUR.SORTIE + ".sha256"]),
                         "bras réel seul : aucun dossier d'un autre bras")
        man = json.load(open(os.path.join(c["s"], "manifeste.json"), encoding="utf-8"))
        self.assertEqual((man["bac"], man["bac_factice_declare"], man["version"]), ("factice", True, B.VERSION))
        self.assertEqual(sorted(man["code_sha256"]), sorted(LANCEUR.FICHIERS_GELES))
        self.assertEqual(r["recherche_loi_plantee"]["touches"], [], "aucun paramètre de L* dans les contextes servis")
        self.assertEqual(r["recherche_loi_plantee"]["lignes_de_tranche_dans_les_contextes"], [])
        g1 = {p["nom"]: p for p in r["plantees"] if p["generation"] == 1}
        self.assertEqual(sorted(g1), sorted(B.PLANTEES_G1))
        self.assertEqual((g1["T-MAL"]["gardien"], g1["T-ELIM"]["verdict"]), ("refuse", "éliminée"))
        self.assertTrue(all(not g1[n]["promue"] for n in B.FAUSSES))
        self.assertTrue(g1["V1"]["promue"] and g1["V1"]["verdict"] == "survit")
        self.assertFalse(any(p["testee"] for p in r["plantees"] if p["generation"] == 2), "§ 3.7 : aucune loi plantée testée en g2")

    def test_recherche_de_la_loi_plantee_dans_l_etage(self):
        """§ 7.6 : sain — aucun paramètre de L* hors de la loi gelée servie, et la recherche voit ceux de la loi gelée (V1 = L*) ;
        artefact — un paramètre de L* écrit ailleurs dans une consigne est touché."""
        et = course_saine()["r"]["releve"]["recherche_loi_plantee"]["etage"]
        self.assertGreater(et["consignes_cherchees"], 0)
        self.assertEqual(et["touches_hors_loi_gelee"], [])
        self.assertGreater(et["touches_dans_la_loi_gelee"], 0)
        L_ = MONDE["loi"]
        texte = "Loi gelée L (JSON canonique) : " + json.dumps(json_canonique(L_).decode(), ensure_ascii=False)[1:-1]
        self.assertEqual(B.chercher_dans_un_texte_d_etage(MONDE, texte, L_, "essai")[0], [])
        hors, _ = B.chercher_dans_un_texte_d_etage(MONDE, texte + f" ; indice : {L_['poids'][1][1]!r}", L_, "essai")
        self.assertTrue(hors)

    def test_aveugle_aucun_mot_du_dessin_servi(self):
        c = course_saine()
        servis = []
        for base, _, noms in os.walk(c["s"]):
            for n in noms:
                if (n == "consigne.md" and os.sep + "experimentateur" in base) or n.startswith("servi-"):  # le vérificateur se dit « témoin »
                    with open(os.path.join(base, n), encoding="utf-8") as f:
                        servis.append(f.read())
        self.assertTrue(servis)
        reels = {p["identifiant"] for p in c["r"]["releve"]["plantees"]}
        self.assertTrue(all(i.startswith("P-") for i in reels))
        for t in servis:
            for mot in MOTS_INTERDITS + tuple(sorted(reels)):
                self.assertNotIn(mot, t, f"mot du dessin servi : {mot!r}")


class Generation2LitLaSelection(unittest.TestCase):
    def test_contenu_de_l_heritage_dans_ce_que_recoit_la_generation_2(self):
        c = course_saine()
        r = c["r"]["releve"]
        ret = sorted(r["retenues"]["1"])
        self.assertTrue(ret, "la course saine retient des cartes en génération 1")
        lect = {str(x["generation"]): x for x in r["boucle"]["lectures"]}
        self.assertEqual(lect["2"]["attendu"], lect["2"]["lu"])
        self.assertEqual(sorted(lect["2"]["retenues_lues"]), ret)
        vue2 = next(v for v in r["vues"] if v["generation"] == 2)
        self.assertEqual(sorted(vue2["lois"]), sorted(ret + ["K1"]))
        arch2 = r["archives_de_jugement"]["2"]
        lois_g1 = {x["identifiant_servi"]: x["loi"] for x in r["cartes"] if x["generation"] == 1 and x.get("loi")}
        self.assertEqual(arch2, dict({"K1": K1}, **{i: lois_g1[i] for i in ret}))
        n2 = B.membres_attendus(arch2)
        self.assertEqual(r["membres_attendus"]["2"], n2)
        self.assertTrue(all(x["membres_d_archive"] == n2 for x in r["cartes"] + r["plantees"] if x["generation"] == 2 and x["gardien"] == "passe"))
        copies = {p["source"]: p for p in r["plantees"] if p["groupe"] == "copie"}
        self.assertEqual(len(copies), min(4, len(ret)))
        for src, p in copies.items():
            self.assertEqual(p["loi"], lois_g1[src], "la copie porte la loi retenue lue")
            self.assertFalse(p["promue"], "P5 : copie refusée par construction")

    def test_heritage_altere_refuse_ou_sortie_changee(self):
        c = course_saine()
        g1 = os.path.join(c["s"], "bras-reel", "generation-1")
        lect = next(x for x in c["r"]["releve"]["boucle"]["lectures"] if x["generation"] == 2)
        depart = B.lire_heritage_depart(LANCEUR.HERITAGE_DEPART, TEXTE)
        h = B.lire_heritage_v65(g1, lect["attendu"], depart["archive"], depart)  # sain
        d = tempfile.mkdtemp(prefix="essai-v65-alt-")
        self.addCleanup(shutil.rmtree, d, True)
        alt = os.path.join(d, "generation-1")
        shutil.copytree(g1, alt)
        with open(os.path.join(alt, bf.NOM_BILAN), "a", encoding="utf-8") as f:
            f.write(" ")
        with self.assertRaises(bf.SelectionNonVerifiee):  # bilan altéré : refus
            B.lire_heritage_v65(alt, lect["attendu"], depart["archive"], depart)
        shutil.rmtree(alt)
        shutil.copytree(g1, alt)
        bilan = json.load(open(os.path.join(g1, bf.NOM_BILAN), encoding="utf-8"))
        bilan["archive"]["F-loi-glissee"] = MONDE["loi"]  # une loi de plus, bilan rescellé
        os.remove(os.path.join(alt, bf.NOM_BILAN))
        os.remove(os.path.join(alt, bf.NOM_BILAN + ".sha256"))
        sha = ecrire_json_scelle(os.path.join(alt, bf.NOM_BILAN), bilan)
        bf.lire_heritage(alt, sha)  # la lecture v59 seule l'accepte (retenues inchangées)…
        with self.assertRaisesRegex(bf.HeritageRefuse, "archive"):  # … la v65 la refuse
            B.lire_heritage_v65(alt, sha, depart["archive"], depart)
        h2 = copy.deepcopy(h)  # héritage dont une retenue porte une autre loi : la vue, le contexte et les copies changent
        i = sorted(h2["retenues"])[0]
        h2["archive"][i] = MONDE["loi"]
        log_e = {x: 1.0 for x in h["retenues"]}
        tache = "essai-v65|g2"
        self.assertNotEqual(T.contexte_du_proposeur(MONDE, bf.vue_pour_proposeur(h), 11, tache),
                            T.contexte_du_proposeur(MONDE, bf.vue_pour_proposeur(h2), 11, tache))
        self.assertNotEqual(B.copies_de_la_selection(h, log_e), B.copies_de_la_selection(h2, log_e))


class Garde7Plantees(unittest.TestCase):
    def test_sain_et_artefact(self):
        depart = B.lire_heritage_depart(LANCEUR.HERITAGE_DEPART, TEXTE)
        pl = B.plantees_generation_1(jeu_du_brouillon(), 7, "essai-v65|g7")
        ids = {r for _, r, _ in pl} | {c["identifiant"] for _, _, c in pl}
        B.exiger_sans_plantee(depart, ids)
        h = copy.deepcopy(depart)
        h["archive"][pl[0][2]["identifiant"]] = pl[0][2]["loi_predictive"]
        with self.assertRaises(T.TemoinRetenu):
            B.exiger_sans_plantee(h, ids)


class CopiesGarde21(unittest.TestCase):
    def heritage(self, n):
        ret = [f"F-{k:012d}" for k in range(n)]
        return {"retenues": ret, "archive": dict({"K1": K1}, **{i: {"type": "fixe", "probas": [1.0, float(k + 1), 1.0]} for k, i in enumerate(ret)})}

    def test_sain(self):
        h = self.heritage(6)
        log_e = {i: float(k) for k, i in enumerate(h["retenues"])}
        cp = B.copies_de_la_selection(h, log_e)
        self.assertEqual([s for _, s, _ in cp], list(reversed(h["retenues"]))[:4], "quatre premières par log e décroissant")
        self.assertTrue(B.exiger_copies_conformes(cp, h, log_e))
        self.assertEqual(B.copies_de_la_selection(self.heritage(0), {}), [], "aucune copie si rien n'est retenu")
        self.assertEqual(len(B.copies_de_la_selection(self.heritage(2), {})), 2)

    def test_artefacts(self):
        h = self.heritage(6)
        log_e = {i: float(k) for k, i in enumerate(h["retenues"])}
        cp = B.copies_de_la_selection(h, log_e)
        with self.assertRaisesRegex(B.CopieRefusee, "non retenue"):
            B.exiger_copies_conformes(cp[:3] + [("C4", "F-carte-non-retenue", K1)], h, log_e)
        mauvaise = [(n, s, ({"type": "fixe", "probas": [9.0, 1.0, 1.0]} if k == 0 else l)) for k, (n, s, l) in enumerate(cp)]
        with self.assertRaisesRegex(B.CopieRefusee, "loi"):
            B.exiger_copies_conformes(mauvaise, h, log_e)
        with self.assertRaisesRegex(B.CopieRefusee, "quatre premières"):
            B.exiger_copies_conformes(B.copies_de_la_selection(h, {}), h, log_e)
        self.assertTrue(issubclass(B.CopieRefusee, T.ArretTour))


# --- M5 : lecture gelée (C1 à C6, A1 à A4) -------------------------------------------------------------------------------------------


class LectureGelee(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c = course_saine()
        cls.releve, cls.journal = c["r"]["releve"], c["r"]["journal"]

    def lire(self, r=None, rejeux=2):
        return L.lire_boucle(copy.deepcopy(r if r is not None else self.releve), MONDE, rejeux_a2=rejeux, journal=self.journal)

    def r(self):
        return copy.deepcopy(self.releve)

    def plantee(self, r, g, nom):
        return next(p for p in r["plantees"] if p["generation"] == g and p["nom"] == nom)

    def test_C1_sain_et_A1_declenche(self):
        l = self.lire()
        self.assertEqual((l["issue"], l["partielles"]), ("C1", []))
        self.assertTrue(l["audits"]["A1"]["declenche"])
        self.assertFalse(l["audits"]["A1"]["bac_reel"], "à blanc : exécuteur factice, A1 le dit")
        self.assertFalse(any(l["audits"][a]["declenche"] for a in ("A2", "A3", "A4")))
        self.assertTrue(all(c["ok_archive"] for c in l["audits"]["A1"]["vraies_survivantes"]))

    def test_C5_arret_et_partielles(self):
        r = self.r()
        r["arret"] = "ArretTour : essai"
        self.assertEqual(self.lire(r)["issue"], "C5")
        r["generations_jouees"] = [1]
        self.assertEqual(self.lire(r)["issue"], "C5")
        r = self.r()
        r["generations_jouees"] = [1]
        self.assertEqual(self.lire(r)["issue"], "C5", "relevé incomplet sans motif d'arrêt")
        r = self.r()
        r["arret"] = "x"
        self.plantee(r, 1, "F2")["promue"] = True
        l = self.lire(r)
        self.assertEqual((l["issue"], l["partielles"]), ("C5", ["C2 (partielle)"]))
        self.assertTrue(l["audits"]["A2"]["declenche"])
        r = self.r()
        r["arret"] = "x"
        r["boucle"]["lectures"][0]["lu"] = "0" * 64
        self.assertEqual(self.lire(r)["partielles"], ["C4 (partielle)"])

    def test_C4_boucle_non_fermee(self):
        cas = {}
        r = self.r()
        r["boucle"]["lectures"][0]["lu"] = "0" * 64
        cas["empreinte lue ≠ écrite"] = r
        r = self.r()
        next(v for v in r["vues"] if v["generation"] == 2)["lois"].pop()
        cas["vue"] = r
        r = self.r()
        k = sorted(r["archives_de_jugement"]["2"])[0]
        del r["archives_de_jugement"]["2"][k]
        cas["archive"] = r
        r = self.r()
        next(c for c in r["cartes"] if c["generation"] == 2 and c["gardien"] == "passe")["membres_d_archive"] = 4
        cas["membres d'archive"] = r
        r = self.r()
        r["copies"] = r["copies"][1:]
        cas["copies"] = r
        for nom, rr in cas.items():
            with self.subTest(cas=nom):
                self.assertEqual(self.lire(rr)["issue"], "C4")
        r = self.r()
        cp = next(p for p in r["plantees"] if p["groupe"] == "copie")
        cp["promue"] = True
        l = self.lire(r)
        self.assertEqual(l["issue"], "C4")
        self.assertTrue(l["audits"]["A4"]["declenche"])
        self.plantee(r, 1, "F1")["promue"] = True
        self.assertEqual(self.lire(r)["issue"], "C4", "ordre : C4 avant C2")

    def test_C2_breche(self):
        for g in (1, 2):
            with self.subTest(generation=g):
                r = self.r()
                self.plantee(r, g, "F3")["promue"] = True
                l = self.lire(r)
                self.assertEqual(l["issue"], "C2")
                a2 = l["audits"]["A2"]
                self.assertTrue(a2["declenche"])
                self.assertEqual(a2["fausses"][0]["forme"], "couverte (T03b)")
                self.assertEqual(a2["fausses"][0]["promue_au_rejeu"], 0)
        r = self.r()
        self.plantee(r, 1, "F1")["promue"] = True
        for p in r["plantees"]:
            if p["groupe"] == "vraie":
                p["promue"] = False
        self.assertEqual(self.lire(r)["issue"], "C2", "ordre : C2 avant C3")

    def test_C3_sans_dents(self):
        r = self.r()
        for p in r["plantees"]:
            if p["groupe"] == "vraie":
                p["verdict"] = "éliminée" if p["promue"] else None
        l = self.lire(r)
        self.assertEqual(l["issue"], "C3")
        a3 = l["audits"]["A3"]
        self.assertTrue(a3["declenche"])
        self.assertTrue(all(v["rejeu_egal"] for v in a3["vraies"]), "A3 : jugement rejoué à la même graine")
        self.assertIn("promue non survivante", {v["categorie"] for v in a3["vraies"]})

    def test_C6_instrument(self):
        r = self.r()
        self.plantee(r, 1, "T-ELIM")["verdict"] = "survit"
        self.assertEqual(self.lire(r)["issue"], "C6")
        r = self.r()
        self.plantee(r, 1, "T-ELIM")["promue"] = False
        self.assertEqual(self.lire(r)["issue"], "C6")
        r = self.r()
        self.plantee(r, 1, "T-MAL")["gardien"] = "passe"
        self.assertEqual(self.lire(r)["issue"], "C6")

    def test_fausse_decouverte_d_une_carte_reelle_en_tete(self):
        r = self.r()
        c = next(x for x in r["cartes"] if x["generation"] == 2 and x["gardien"] == "passe")
        c.update(promue=True, verdict="survit", loi=dict(K1))  # promue puis survivante, sans gain au-delà de l'archive
        l = self.lire(r)
        self.assertTrue(l["en_tete"] and "fausse découverte" in l["en_tete"][0])
        self.assertTrue(l["audits"]["A2"]["declenche"])
        self.assertEqual(l["issue"], "C1", "une fausse découverte réelle ne change pas l'issue")

    def test_releve_d_une_autre_version_refuse(self):
        r = self.r()
        r["version"] = "tour-ferme-v64"
        with self.assertRaises(L.LectureImpossible):
            self.lire(r)

    def test_aucune_moyenne_ni_mediane_sur_des_jetons(self):
        src = open(L.__file__, encoding="utf-8").read()
        noms = {n.attr if isinstance(n, ast.Attribute) else n.id for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.Attribute, ast.Name))}
        self.assertFalse(noms & {"mean", "median", "statistics", "nanmean", "nanmedian", "jetons"}, noms & {"mean", "median", "statistics"})

    def test_programme_de_lecture(self):
        c = course_saine()
        d = tempfile.mkdtemp(prefix="essai-v65-lecture-")
        self.addCleanup(shutil.rmtree, d, True)
        out = os.path.join(d, "l.json")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(LECTEUR.principal([c["s"], out, "--rejeux-a2", "2"]), 0)
            self.assertEqual(LECTEUR.principal([c["s"], out]), 2, "jamais d'écrasement")
            self.assertEqual(LECTEUR.principal([c["s"], out + "2", "--releve-sha256", "0" * 64]), 2, "autre empreinte")
        self.assertEqual(json.load(open(out, encoding="utf-8"))["issue"], "C1")


class ArretPendantUnEtage(unittest.TestCase):
    """§ 8, C5 : un arrêt ne masque jamais une brèche. Le jugement entre au relevé avant les étages : une fausse promue (artefact : le
    juge la promeut) puis un arrêt à l'étage des cartes (session de l'expérimentateur en échec) → relevé partiel scellé (code 3) qui
    la montre ; lecture C5 avec « C2 (partielle) ». Cas sain : même arrêt sans fausse promue → C5 seule."""

    def courir_arret(self, promouvoir_f2):
        f2 = jeu_du_brouillon()["fausses"]["F2"]["loi"]
        vrai = A.juger_carte

        def juge(loi, monde, archive, racine, tache):
            ev, d = vrai(loi, monde, archive, racine, tache)
            if promouvoir_f2 and "|plantee=" in tache and B._egales(loi, f2):
                ev = dict(ev, promue=True, marge_atteinte=True, trajectoire_log_w=[0.0, 7.0])
            return ev, d

        d = tempfile.mkdtemp(prefix="essai-v65-arret-")
        self.addCleanup(shutil.rmtree, d, True)
        s = os.path.join(d, "s")
        with unittest.mock.patch.object(A, "juger_carte", juge):
            code, err = courir(s, "--a-blanc", "--graine", "7", "--bac", "factice", "--cartes-par-proposeur", "1",
                               "--scenario-experimentateur", "erreur")
        self.assertEqual(code, 3, err)
        return rapport(s)

    def test_artefact_fausse_promue_puis_arret(self):
        r = self.courir_arret(True)
        g1 = {p["nom"]: p for p in r["releve"]["plantees"] if p["generation"] == 1}
        self.assertEqual(sorted(g1), sorted(B.PLANTEES_G1), "le jugement de la génération 1 est au relevé partiel")
        self.assertTrue(g1["F2"]["promue"])
        l = L.lire_boucle(r["releve"], MONDE, rejeux_a2=1, journal=r["journal"])
        self.assertEqual((l["issue"], l["partielles"]), ("C5", ["C2 (partielle)"]))

    def test_sain_arret_sans_breche(self):
        r = self.courir_arret(False)
        l = L.lire_boucle(r["releve"], MONDE, rejeux_a2=1, journal=r["journal"])
        self.assertEqual((l["issue"], l["partielles"]), ("C5", []))


# --- M6 : configuration v5, commandes v6 nommées ---------------------------------------------------------------------------------------


CONFIGURATION_V5 = os.path.join(RACINE, "exemples", "configuration-tour-ferme-v5.json")


class ConfigurationV5(unittest.TestCase):
    def conf(self):
        return json.load(open(CONFIGURATION_V5, encoding="utf-8"))

    def plan(self):
        return B.lire_plan(TEXTE)

    def test_nommee_par_le_plan_plafonds_du_devis(self):
        self.assertEqual(sha256_fichier(CONFIGURATION_V5), self.plan()["configuration_sha256"])
        s = self.conf()["boucle_reelle_v65"]
        self.assertEqual((s["plafond_modeles_usd"], s["parts_usd"], s["plafond_machine_usd"], s["go"]),
                         (40.0, {"kimi": 33.0, "argon": 7.0}, 5.0, "GO-2026-11-08-02"))
        self.assertEqual({n: c["sha256"] for n, c in s["commandes"].items()},
                         {"kimi": "889309305aeb37de9801c2f40c31769fd268abded1ac61ea94196fd0d51195ae",
                          "argon": "5eae1a0468430e243c3c4e099b3969f949f62add688531aafdd7f0f44e036e55"})

    @unittest.skipUnless(os.path.isdir(DOSSIER_V4), "configuration v4 et ses pièces absentes de cette machine")
    def test_lue_par_la_configuration_v56(self):
        from pole import configuration_v56 as cfg
        conf = cfg.lire_configuration_v56(CONFIGURATION_V5, base=DOSSIER_V4)
        self.assertEqual(conf["budget"]["plafond_usd"], 40.0)

    @unittest.skipUnless(os.path.isdir(os.path.join(DEPOT_TRAVAIL, ".git")), "dépôt de travail absent")
    def test_empreintes_egales_aux_commandes_v6_du_commit(self):
        s = self.conf()["boucle_reelle_v65"]
        for n, c in list(s["commandes"].items()) + [("registre", s["dependance_des_commandes"])]:
            rel = os.path.relpath(c["chemin"], DEPOT_TRAVAIL)
            octets = subprocess.run(["git", "-C", DEPOT_TRAVAIL, "show", f"{COMMIT_COMMANDES}:{rel}"], capture_output=True, timeout=60).stdout
            self.assertEqual(hashlib.sha256(octets).hexdigest(), c["sha256"], n)

    def conf_locale(self, d):
        """La configuration v5, ses commandes et sa dépendance remplacées par des fichiers locaux nommés (jamais lancés)."""
        conf = self.conf()
        s = conf["boucle_reelle_v65"]
        for n in ("kimi", "argon"):
            p = os.path.join(d, f"commande_{n}.py")
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"# commande factice {n}\n")
            i = conf["fournisseurs"][n]["commande"].index(s["commandes"][n]["chemin"])
            conf["fournisseurs"][n]["commande"][i] = p
            s["commandes"][n] = {"chemin": p, "sha256": sha256_fichier(p)}
        p = os.path.join(d, "registre.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write("# registre factice\n")
        s["dependance_des_commandes"] = {"chemin": p, "sha256": sha256_fichier(p)}
        return conf

    def test_garde_sain_et_artefacts(self):
        d = tempfile.mkdtemp(prefix="essai-v65-conf-")
        self.addCleanup(shutil.rmtree, d, True)
        conf = self.conf_locale(d)
        s = conf["boucle_reelle_v65"]
        self.assertIs(LANCEUR.exiger_configuration_v65(conf, self.plan()), s)
        for chg, motif in (({"plafond_modeles_usd": 50.0}, "plafond_modeles_usd"), ({"plafond_machine_usd": 0.0}, "plafond_machine_usd"),
                           ({"go": "GO-2026-11-07-11"}, r"\.go"), ({"parts_usd": {"kimi": 30.0, "argon": 10.0}}, "parts_usd")):
            with self.subTest(chg=chg):
                c2 = copy.deepcopy(conf)
                c2["boucle_reelle_v65"].update(chg)
                with self.assertRaisesRegex(B.BoucleRefusee, motif):
                    LANCEUR.exiger_configuration_v65(c2, self.plan())
        c2 = copy.deepcopy(conf)
        c2["budget"]["plafond_usd"] = 50.0
        with self.assertRaisesRegex(B.BoucleRefusee, "budget.plafond_usd"):
            LANCEUR.exiger_configuration_v65(c2, self.plan())
        c2 = copy.deepcopy(conf)
        c2["fournisseurs"]["kimi"]["commande"] = [x for x in c2["fournisseurs"]["kimi"]["commande"] if x != s["commandes"]["kimi"]["chemin"]]
        with self.assertRaisesRegex(B.BoucleRefusee, "ne lance pas"):
            LANCEUR.exiger_configuration_v65(c2, self.plan())
        with open(s["dependance_des_commandes"]["chemin"], "a", encoding="utf-8") as f:
            f.write("# altérée\n")
        with self.assertRaisesRegex(B.BoucleRefusee, "dépendance"):
            LANCEUR.exiger_configuration_v65(conf, self.plan())
        with open(s["commandes"]["kimi"]["chemin"], "a", encoding="utf-8") as f:
            f.write("# altérée\n")
        with self.assertRaisesRegex(B.BoucleRefusee, "empreinte"):
            LANCEUR.exiger_configuration_v65(conf, self.plan())
        os.remove(s["commandes"]["argon"]["chemin"])
        with self.assertRaisesRegex(B.BoucleRefusee, "absente"):  # commande non versée (pièce M6)
            LANCEUR.exiger_configuration_v65(conf, self.plan())
        nommee = self.conf()["boucle_reelle_v65"]["commandes"]["kimi"]
        if not (os.path.isfile(nommee["chemin"]) and sha256_fichier(nommee["chemin"]) == nommee["sha256"]):
            with self.assertRaisesRegex(B.BoucleRefusee, "absente|empreinte"):  # la configuration v5 telle quelle, sur cette machine
                LANCEUR.exiger_configuration_v65(self.conf(), self.plan())


# --- gardes de dépense ------------------------------------------------------------------------------------------------------------------


class AdaptateurCompte:
    ROLES_PERMIS = (T.ROLE_PROPOSEUR,)

    def __init__(self):
        self.appels = 0

    def lancer(self, role, texte, dossier, budget_usd, max_tours, modele=None):
        self.appels += 1
        return T.Resultat("```json\n[]\n```", [], 0.01, "ok")


GO_OK = {"identifiant": "GO-2026-11-08-02", "plafond_lu_usd": 45.0, "montant_requis_usd": 45.0}


class GardesDeDepense(unittest.TestCase):
    def compteur(self):
        return B.CompteurV65(40.0, 3600.0, {"kimi": 33.0, "argon": 7.0}, 5.0)

    def test_compteur_sain(self):
        c = self.compteur()
        c.verifier_avant_appel("kimi", 0.5)
        c.ajouter(32.0, "proposeur", "kimi")
        c.verifier_avant_appel("kimi", 1.0)
        c.ajouter_machine(4.99)
        self.assertEqual(c.etat()["plafond_machine_usd"], 5.0)

    def test_compteur_artefacts(self):
        c = self.compteur()
        c.ajouter(32.6, "proposeur", "kimi")
        with self.assertRaisesRegex(B.PlafondAtteint, "non lancé"):
            c.verifier_avant_appel("kimi", 0.5)  # borne au-delà de la part restante (0,40)
        c.ajouter(0.4, "proposeur", "kimi")
        with self.assertRaises(B.PlafondAtteint):
            c.verifier_avant_appel("kimi", 0.0)  # part épuisée : aucun appel, même de borne nulle
        with self.assertRaises(T.ArretTour):
            c.ajouter(0.01, "proposeur", "kimi")  # part franchie : arrêt
        c2 = self.compteur()
        with self.assertRaises(T.ArretTour):
            c2.ajouter(7.5, "verificateur", "argon")
        with self.assertRaises(B.PlafondAtteint):
            c2.verifier_avant_appel("inconnu", 0.0)
        with self.assertRaises(B.PlafondAtteint):
            c2.ajouter_machine(5.01)
        with self.assertRaises(B.BoucleRefusee):
            B.CompteurV65(40.0, 3600.0, {"kimi": 33.0, "argon": 6.0}, 5.0)

    def test_aucun_appel_sans_go_cite(self):
        c = self.compteur()
        ad = AdaptateurCompte()
        for go in (None, {}, dict(GO_OK, identifiant="GO-2026-11-07-11"), dict(GO_OK, montant_requis_usd=40.0, plafond_lu_usd=40.0)):
            with self.subTest(go=go):
                with self.assertRaises(B.GoNonCite):
                    B.AdaptateurSousGo(ad, "kimi", go, "GO-2026-11-08-02", 45.0, c).lancer(T.ROLE_PROPOSEUR, "x", "/nonexistant", 0.5, 1)
        with self.assertRaises(B.GoNonCite):
            B.AdaptateurSousGo(ad, "kimi", GO_OK, "GO-2026-11-08-02", 45.0, None).lancer(T.ROLE_PROPOSEUR, "x", "/nonexistant", 0.5, 1)
        self.assertEqual(ad.appels, 0, "aucun appel de l'adaptateur enveloppé")
        sous = B.AdaptateurSousGo(ad, "kimi", GO_OK, "GO-2026-11-08-02", 45.0, c)
        self.assertEqual(T.roles_permis(sous), (T.ROLE_PROPOSEUR,))
        self.assertEqual(sous.lancer(T.ROLE_PROPOSEUR, "x", "/nonexistant", 0.5, 1).statut, "ok")
        self.assertEqual(ad.appels, 1)
        c.ajouter(33.0, "proposeur", "kimi")
        with self.assertRaises(B.PlafondAtteint):
            sous.lancer(T.ROLE_PROPOSEUR, "x", "/nonexistant", 0.5, 1)
        self.assertEqual(ad.appels, 1, "arrêt au plafond avant l'appel")

    @unittest.skipUnless(os.path.isfile(REGISTRE_GO), "registre des GO absent de cette machine")
    def test_go_du_registre_au_montant_total(self):
        """La ligne GO-2026-11-08-02 du registre, recopiée telle quelle dans un registre d'essai (le registre entier n'est pas lisible
        par `configuration_v53.lire_registre_go` s'il porte un identifiant en double : constat dit au rendu), lue au montant total
        (45 USD = 40 + 5) ; 40 USD refusé."""
        from pole import configuration_v56 as cfg
        import datetime
        jour = datetime.date(2026, 11, 8)
        lignes = [l for l in open(REGISTRE_GO, encoding="utf-8").read().splitlines() if l.startswith("| GO-2026-11-08-02 |")]
        self.assertEqual(len(lignes), 1)
        d = tempfile.mkdtemp(prefix="essai-v65-go-")
        self.addCleanup(shutil.rmtree, d, True)
        reg = os.path.join(d, "go.md")
        with open(reg, "w", encoding="utf-8") as f:
            f.write("| id | accordé le | type | périmètre | plafond | échéance | accordé par | réf. |\n|---|---|---|---|---|---|---|---|\n" + lignes[0] + "\n")
        g = cfg.verifier_go_v56("GO-2026-11-08-02", reg, 45.0, aujourd_hui=jour)
        self.assertTrue(B.exiger_go_cite(g, "GO-2026-11-08-02", 45.0))
        with self.assertRaises(cfg.GoRefuse):
            cfg.verifier_go_v56("GO-2026-11-08-02", reg, 40.0, aujourd_hui=jour)
        with self.assertRaises(cfg.GoRefuse):
            cfg.verifier_go_v56("GO-2026-11-08-02", reg, 45.0, aujourd_hui=datetime.date(2026, 12, 1))  # échéance passée

    def test_course_arretee_au_plafond(self):
        d = tempfile.mkdtemp(prefix="essai-v65-plafond-")
        self.addCleanup(shutil.rmtree, d, True)
        s = os.path.join(d, "s")
        code, err = courir(s, "--a-blanc", "--graine", "7", "--bac", "factice", "--cartes-par-proposeur", "1", "--plafond-kimi-usd", "0.05",
                           "--plafond-argon-usd", "0.05", "--cout-simule-usd", "0.06")
        self.assertEqual(code, 3, err)
        r = rapport(s)
        self.assertIn("arrêt au plafond", r["arret"], "l'appel dont la borne dépasse la part n'est pas lancé")
        self.assertEqual((r["depense"]["par_relais_usd"]["kimi"], r["depense"]["appels"]), (0.0, 0), "aucun appel, aucune dépense")
        self.assertEqual(r["appels_proposeurs"], [[], []])


# --- chemin réel jusqu'à --verifier-seulement (GO au montant total, configuration v5, commandes nommées) -------------------------------


def preparer_chemin_reel(dossier, go_montant="45 USD", alterer_commande=False):
    """Texte scellé (dans `dossier/prereg`), configuration v56 d'essai à section v65 (relais par commandes factices locales, nommées
    avec leurs empreintes), registre de GO d'essai ; rend (argv sans --verifier-seulement, dossier prereg). Aucun réseau, aucune clé."""
    import aides_v54 as A54
    import aides_v56 as A56
    conf = A56.configuration(dossier)
    conf["budget"]["plafond_usd"], conf["budget"]["arret_etape_usd"] = 40.0, 39.0
    ck = A56.commande_factice(dossier, "kimi", {"texte": "x", "cout_usd": 0.001, "modele_servi": "kimi-k3.1-pro"})
    ca = A56.commande_factice(dossier, "argon", {"texte": "x", "cout_usd": 0.001, "modele_servi": "gemini-4-argon"})
    conf["fournisseurs"] = {
        "kimi": {"type": "commande_externe", "porte_plafond": {"type": "environnement"}, "commande": ck + ["--registre", "{REGISTRE}"],
                 "prix_entree_usd_par_million_jetons": 2.0},
        "argon": {"type": "commande_externe", "porte_plafond": {"type": "environnement"},
                  "commande": ca + ["--registre", "{REGISTRE}", "--plafond-cumule-usd", "40"], "prix_entree_usd_par_million_jetons": 10.0}}
    dep = os.path.join(dossier, "registre_depense_cumulee_v1.py")
    with open(dep, "w", encoding="utf-8") as f:
        f.write("# registre factice\n")
    conf["boucle_reelle_v65"] = {"plafond_modeles_usd": 40.0, "parts_usd": {"kimi": 33.0, "argon": 7.0}, "plafond_machine_usd": 5.0,
                                 "go": "GO-2026-11-08-02", "commandes": {"kimi": {"chemin": ck[-1], "sha256": sha256_fichier(ck[-1])},
                                                                        "argon": {"chemin": ca[-1], "sha256": sha256_fichier(ca[-1])}},
                                 "dependance_des_commandes": {"chemin": dep, "sha256": sha256_fichier(dep)}}
    if alterer_commande:
        with open(ck[-1], "a", encoding="utf-8") as f:
            f.write("# altérée après nommage\n")
    chemin_conf = os.path.join(dossier, "conf.json")
    with open(chemin_conf, "w", encoding="utf-8") as f:
        json.dump(conf, f)
    dp = os.path.join(dossier, "prereg")
    os.makedirs(dp)
    emp = "\n".join(f"{sha256_fichier(os.path.join(RACINE, r))}  {r}" for r in LANCEUR.FICHIERS_GELES)
    texte = ("# essai\n" + LANCEUR.DEBUT_EMPREINTES + "\n" + emp + "\n" + LANCEUR.FIN_EMPREINTES + "\n"
             + texte_avec(configuration_sha256=sha256_fichier(chemin_conf)))
    pr = os.path.join(dp, "preenregistrement-boucle-reelle-organisme-v1-v1.md")
    ecrire_scelle(pr, texte)
    reg = A54.registre_go(dossier, A54.ligne_go("GO-2026-11-08-02", go_montant, perimetre="boucle réelle (essai)"))
    argv = [os.path.join(dossier, "sortie"), "--preenregistrement", pr, "--configuration", chemin_conf, "--moteur", "reel",
            "--confirmer-moteur-reel", "--registre-go", reg, "--go", "GO-2026-11-08-02", "--bac", "reel", "--utilisateur-bac", "64097"]
    return argv, dp


class CheminReelVerifierSeulement(unittest.TestCase):
    ENV = {"PATH": os.environ.get("PATH", os.defpath), "POLE_MACHINE_JETABLE_V56": "1"}

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v65-reel-")
        self.addCleanup(shutil.rmtree, self.d, True)
        self.tmp = os.path.join(self.d, "tmp")
        os.makedirs(self.tmp)
        self.vraie = A.choisir_executeur

    def jouer(self, argv, dp, env=None):
        err = io.StringIO()
        with unittest.mock.patch.dict(os.environ, dict(env or self.ENV, HOME=self.d), clear=True), \
                unittest.mock.patch.object(LANCEUR, "DOSSIER_PREREG", dp), unittest.mock.patch.object(tempfile, "tempdir", self.tmp), \
                unittest.mock.patch.object(LANCEUR, "version_bwrap", lambda which=None: (0, 9, 0)), \
                unittest.mock.patch.object(A, "choisir_executeur", lambda bac, **kw: self.vraie("factice")), \
                contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(err):
            code = LANCEUR.principal(argv + ["--verifier-seulement"])
        return code, out.getvalue(), err.getvalue()

    def test_sain_verification_conforme_rien_ecrit(self):
        argv, dp = preparer_chemin_reel(self.d)
        code, out, err = self.jouer(argv, dp)
        self.assertEqual(code, 0, err[-1500:])
        o = json.loads(out)
        self.assertEqual((o["verification"], o["plan"]["plafond_modeles_usd"], o["plan"]["plafond_machine_usd"]), ("conforme", 40.0, 5.0))
        self.assertEqual(o["configuration"]["adaptateurs"]["kimi"]["sous_go"], "GO-2026-11-08-02")
        self.assertEqual(o["configuration"]["parts_des_relais_usd"], {"kimi": 33.0, "argon": 7.0})
        self.assertFalse(os.path.exists(argv[0]))
        self.assertEqual(os.listdir(self.tmp), [])

    def test_artefacts(self):
        for nom, kw, motif in (("GO à 40 USD (modèles seuls)", {"go_montant": "40 USD"}, "pas exactement"),
                               ("commande altérée après nommage", {"alterer_commande": True}, "empreinte")):
            with self.subTest(cas=nom):
                d = os.path.join(self.d, nom.split()[0] + str(len(kw)))
                os.makedirs(d)
                argv, dp = preparer_chemin_reel(d, **kw)
                code, _, err = self.jouer(argv, dp)
                self.assertEqual(code, 2, err[-800:])
                self.assertIn(motif, err)
                self.assertFalse(os.path.exists(argv[0]))
        d = os.path.join(self.d, "sans-utilisateur")
        os.makedirs(d)
        argv, dp = preparer_chemin_reel(d)
        i = argv.index("--utilisateur-bac")
        code, _, err = self.jouer(argv[:i] + argv[i + 2:], dp)
        self.assertEqual(code, 2)
        self.assertIn("utilisateur dédié", err)
        d = os.path.join(self.d, "cle")
        os.makedirs(d)
        argv, dp = preparer_chemin_reel(d)
        code, _, err = self.jouer(argv, dp, env=dict(self.ENV, GEMINI_API_KEY="x"))
        self.assertEqual(code, 2)
        self.assertEqual(os.listdir(self.tmp), [])


# --- bac réel (gardes 3 et 22) -----------------------------------------------------------------------------------------------------------


class BacReel(unittest.TestCase):
    def test_garde_22(self):
        self.assertIsNone(LANCEUR.exiger_machine_du_bac("factice", False, None, None))
        self.assertEqual(LANCEUR.exiger_machine_du_bac("reel", True, 64097, (0, 9, 0)), (0, 9, 0))
        self.assertEqual(LANCEUR.exiger_machine_du_bac("reel", False, None, (0, 11)), (0, 11))
        with self.assertRaises(A.BacASableIndisponible):
            LANCEUR.exiger_machine_du_bac("reel", False, None, None)
        for args in (("reel", False, None, (0, 8, 0)), ("reel", True, None, (0, 9, 0)), ("reel", True, 0, (0, 9, 0)), ("factice", True, None, None)):
            with self.subTest(args=args):
                with self.assertRaises(B.BoucleRefusee):
                    LANCEUR.exiger_machine_du_bac(*args)

    @unittest.skipIf(LANCEUR.version_bwrap() is not None, "bwrap présent : l'artefact « bwrap absent » ne se joue pas ici")
    def test_bwrap_absent_refus_code_2_sans_repli(self):
        d = tempfile.mkdtemp(prefix="essai-v65-bac-")
        self.addCleanup(shutil.rmtree, d, True)
        s = os.path.join(d, "s")
        code, err = courir(s, "--a-blanc", "--graine", "7", "--bac", "reel")
        self.assertEqual(code, 2)
        self.assertIn("bwrap absent", err)
        self.assertIn("aucun repli", err)
        self.assertFalse(os.path.exists(s))

    def test_course_dans_le_vrai_bac(self):
        if os.environ.get("POLE_ESSAI_BAC_REEL_NON_JOUE") == "1":
            self.skipTest("ESSAI RÉEL NON JOUÉ (POLE_ESSAI_BAC_REEL_NON_JOUE=1)")
        if LANCEUR.version_bwrap() is None:
            self.skipTest("ESSAI RÉEL NON JOUÉ : bwrap absent de cette machine")
        uid = ["--utilisateur-bac", "64097"] if os.geteuid() == 0 else []
        d = tempfile.mkdtemp(prefix="essai-v65-bac-reel-")
        self.addCleanup(shutil.rmtree, d, True)
        r = subprocess.run([sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "boucle_reelle_v65.py"), os.path.join(d, "s"),
                            "--a-blanc", "--graine", "12", "--bac", "reel", *uid, "--cartes-par-proposeur", "1"],
                           capture_output=True, text=True, timeout=1800, cwd=RACINE)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        rap = rapport(os.path.join(d, "s"))
        et = [l for l in rap["journal"] if l["evenement"] == "etage-tests-de-mort"]
        self.assertTrue(et and all(l["bac_a_sable"] == "bwrap" and l["factice"] is False for l in et))


# --- plan, texte scellé (garde 6), fermeture -------------------------------------------------------------------------------------------------


class PlanV65(unittest.TestCase):
    def test_sain_et_artefacts(self):
        p = B.lire_plan(TEXTE)
        self.assertEqual((p["generations"], p["bras"], p["m_e_bh"], p["plafond_modeles_usd"], p["plafond_kimi_usd"], p["plafond_argon_usd"],
                          p["plafond_machine_usd"], p["go"]), (2, "reel_seul", 22, 40.0, 33.0, 7.0, 5.0, "GO-2026-11-08-02"))
        for chg in ({"generations": 3}, {"m_e_bh": 19}, {"plafond_kimi_usd": 34}, {"duree_h": 24}, {"d9": "aiguilleur"}, {"go": "oui"},
                    {"heritage_depart_sha256": "x"}, {"jeu_plante_sha256": None}, {"cartes_par_proposeur": 7, "m_e_bh": 24},
                    {"plafond_machine_usd": 0}):
            with self.subTest(chg=chg):
                with self.assertRaises(B.BoucleRefusee):
                    B.lire_plan(texte_avec(**chg))
        self.assertEqual(B.m_impose(6), 22)


class Garde6V65(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v65-prereg-")
        self.addCleanup(shutil.rmtree, self.d, True)

    def texte(self, marqueur=False, code=None):
        emp = "\n".join(f"{(code or {}).get(r) or sha256_fichier(os.path.join(RACINE, r))}  {r}" for r in LANCEUR.FICHIERS_GELES)
        return ("# essai\n" + ("<<BLOC-V65>>\n" if marqueur else "") + LANCEUR.DEBUT_EMPREINTES + "\n" + emp + "\n" + LANCEUR.FIN_EMPREINTES
                + "\n" + texte_avec())

    def ecrire(self, texte, nom="preenregistrement-boucle-reelle-organisme-v1-v1.md"):
        p = os.path.join(self.d, nom)
        ecrire_scelle(p, texte)
        return p

    def test_sain(self):
        e, sha, gelees, plan, texte = LANCEUR.lire_preenregistrement(self.ecrire(self.texte()), self.d)
        self.assertGreaterEqual(e, 2 ** 64)
        self.assertEqual(set(gelees), set(LANCEUR.FICHIERS_GELES))
        self.assertEqual(plan["go"], "GO-2026-11-08-02")
        self.assertEqual(B.lire_jeu_plante(texte, {"K1": K1})[0], jeu_du_brouillon())

    def test_artefacts(self):
        p = self.ecrire(self.texte())
        with open(p, "a", encoding="utf-8") as f:
            f.write("ajout\n")
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(p, self.d)
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(self.ecrire(self.texte(marqueur=True), "preenregistrement-boucle-reelle-organisme-v1-v2.md"), self.d)
        r = LANCEUR.FICHIERS_GELES[5]
        with self.assertRaisesRegex(LANCEUR.PreenregistrementRefuse, "code différent"):
            LANCEUR.lire_preenregistrement(self.ecrire(self.texte(code={r: "0" * 64}), "preenregistrement-boucle-reelle-organisme-v1-v3.md"), self.d)
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(self.ecrire(self.texte(), "preenregistrement-boucle-reelle-organisme-v1-brouillon1.md"), self.d)
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(os.path.join(self.d, "preenregistrement-boucle-reelle-organisme-v1-v1.md"))  # hors de prereg/
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.entropie_decisive("0" * 48 + "f" * 16)

    def test_mode_reel_refus_avant_tout_appel(self):
        s = os.path.join(self.d, "s")
        for opts in (["--preenregistrement", os.path.join(self.d, "absent.md"), "--bac", "factice"],
                     ["--preenregistrement", os.path.join(self.d, "absent.md"), "--bac", "factice", "--moteur", "reel"],
                     ["--a-blanc", "--bac", "factice"], ["--a-blanc", "--graine", str(2 ** 64), "--bac", "factice"],
                     ["--a-blanc", "--graine", "7", "--bac", "factice", "--go", "GO-2026-11-08-02"]):
            with self.subTest(opts=opts):
                self.assertEqual(courir(s, *opts)[0], 2)
                self.assertFalse(os.path.exists(s))


class BlocV65(unittest.TestCase):
    """Les fichiers de données livrés (héritage de départ, texte du mode à blanc) sont ceux que produit le générateur du bloc ; le bloc
    qui remplace `<<BLOC-V65>>` porte les empreintes du code gelé, le plan, le jeu planté et les commandes."""

    def test_fichiers_egaux_au_generateur(self):
        m = BLOC.morceaux()
        with open(LANCEUR.HERITAGE_DEPART, "rb") as f:
            self.assertEqual(f.read(), m["octets_heritage"])
        self.assertEqual(TEXTE, BLOC.texte_a_blanc(m))
        self.assertEqual(B.lire_plan(TEXTE)["heritage_depart_sha256"], sha256_fichier(LANCEUR.HERITAGE_DEPART))

    def test_bloc(self):
        t = BLOC.bloc_v65(BLOC.morceaux())
        self.assertEqual(sorted(re.findall(r"^[0-9a-f]{64}  (\S+)$", t, re.M)), sorted(LANCEUR.FICHIERS_GELES))
        self.assertEqual(B.lire_plan(t)["go"], "GO-2026-11-08-02")
        self.assertEqual(B.lire_jeu_plante(t, {"K1": K1})[0], jeu_du_brouillon())
        self.assertNotRegex(t, r"<<[A-Z0-9_-]+>>")


def imports_de(rel):
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


class FermetureV65(unittest.TestCase):
    def test_bloc_gele_egal_a_la_fermeture_statique(self):
        ferm, pile = set(), ["demonstrations/boucle_reelle_v65.py", "demonstrations/lire_boucle_reelle_v65.py"]
        while pile:
            x = pile.pop()
            if x not in ferm:
                ferm.add(x)
                pile += sorted(imports_de(x) - ferm)
        geles = set(LANCEUR.FICHIERS_GELES)
        self.assertEqual(len(geles), len(LANCEUR.FICHIERS_GELES))
        self.assertEqual((sorted(ferm - geles), sorted(geles - ferm)), ([], []))
        self.assertEqual(len(geles), 93)
        self.assertTrue({"pole/boucle_reelle_v65.py", "pole/lecture_boucle_reelle_v65.py", "pole/tour_ferme_v64.py", "pole/nul_v8.py"} <= geles)


if __name__ == "__main__":
    unittest.main()
