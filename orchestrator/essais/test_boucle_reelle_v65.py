"""Essais du code v65 (plus petite course réelle de la boucle complète) : pièces M1 à M5, gardes 17 à 22, gardes de dépense, bac
à sable, fermeture du code gelé, essai à blanc de bout en bout. Chaque garde est essayée sur un cas sain et sur un artefact (R5).
Aucun réseau, aucune clé, aucun appel de modèle. Les essais qui exigent `bwrap` sont déclarés non joués quand
`POLE_ESSAI_BAC_REEL_NON_JOUE=1` ou que `bwrap` manque.

  POLE_ESSAI_BAC_REEL_NON_JOUE=1 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_boucle_reelle_v65.py
"""

import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import boucle_fermee_v59 as bf  # noqa: E402
from pole import boucle_reelle_v65 as B  # noqa: E402
from pole import lecture_boucle_reelle_v65 as L  # noqa: E402
from pole import tour_ferme_v64 as T  # noqa: E402
from pole.outils import ecrire_json_scelle, ecrire_scelle, sha256_fichier  # noqa: E402

import importlib.util  # noqa: E402


def _charger(nom, rel):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LANCEUR = _charger("lanceur_boucle_reelle_v65_essais", "demonstrations/boucle_reelle_v65.py")
LECTEUR = _charger("lecteur_boucle_reelle_v65_essais", "demonstrations/lire_boucle_reelle_v65.py")
MONDE = A.charger_monde(RACINE)
JEU = B.jeu_du_dessin(MONDE)
BAC_NON_JOUE = os.environ.get("POLE_ESSAI_BAC_REEL_NON_JOUE") == "1" or not shutil.which("bwrap")


def _texte_avec(jeu):
    return "# texte\n\n" + B.texte_du_bloc(jeu) + "\n\nfin\n"


def _lancer(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = LANCEUR.principal(argv)
    return code, out.getvalue(), err.getvalue()


def _roles_a_blanc(scenario_proposeur=None, cout=0.0):
    ns = type("Args", (), {"cout_simule_usd": cout, "scenario_proposeur": scenario_proposeur, "cout_simule_etage_usd": 0.0,
                           "scenario_experimentateur": None, "scenario_verificateur": None, "familles_a_blanc": None,
                           "prix_entree_kimi_usd_par_million_jetons": None, "prix_entree_argon_usd_par_million_jetons": None})()
    return LANCEUR.L64.roles_a_blanc(ns, tempfile.mkdtemp(prefix="roles-v65-"))


def jouer(sortie, racine=20261110, lire=None, archive_des_plantees=None, parts=None, cout=0.0, scenario=None, plan_en_plus=None,
          budget_appel=None):
    """La boucle à blanc par le chemin du cœur (doublures, exécuteur factice déclaré) ; rend (relevé, journal) ou lève ArretTour."""
    d = tempfile.mkdtemp(prefix="depart-essai-v65-")
    sha = B.ecrire_heritage_depart(d, JEU)
    h0 = B.lire_heritage_depart(os.path.join(d, B.NOM_HERITAGE_DEPART), sha, JEU)
    proposeurs, etage, roles = _roles_a_blanc(scenario, cout)
    for p in proposeurs:  # budget d'un appel de proposeur (mode réel : plafonds_session.proposeur, 0,5 USD)
        p.budget = p.budget if budget_appel is None else budget_appel
    plan = {"generations": 2, "cartes_par_proposeur": 6, "m_e_bh": 22, "bras": ["reel"], **(plan_en_plus or {})}
    compteur = T.Compteur(1e9, 72 * 3600.0, parts or {})
    return B.jouer_boucle(sortie, monde=MONDE, jeu=JEU, heritage_depart=h0, racine=racine, plan=plan,
                          decisions={"d7": "archive_propre", "d9": "mecanique"}, proposeurs=proposeurs, adaptateur_etage=etage,
                          roles=roles, fabrique_executeur=lambda: A.choisir_executeur("factice"), compteur=compteur, lire=lire,
                          archive_des_plantees=archive_des_plantees, environnement=dict(T.ENV_A_BLANC))


class Course:
    """Une course à blanc partagée (≈ 12 s), jouée une fois pour les essais de M4 et de M5."""
    _releve = None

    @classmethod
    def releve(cls):
        if cls._releve is None:
            cls._releve = jouer(tempfile.mkdtemp(prefix="course-v65-"))[0]
        return copy.deepcopy(cls._releve)


# --- M2 : jeu planté --------------------------------------------------------------------------------------------------------


class JeuPlante(unittest.TestCase):
    def test_sain_jeu_lu_a_l_octet(self):
        t = _texte_avec(JEU)
        octets, jeu = B.bloc_du_jeu(t)
        self.assertEqual(octets, json.dumps(JEU, ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8"))
        lu, sha = B.lire_jeu_plante(t, hashlib.sha256(octets).hexdigest())
        self.assertEqual(lu, JEU)
        self.assertEqual(sorted(lu["vraies"]), list(B.VRAIES))
        self.assertEqual(sorted(lu["fausses"]), list(B.FAUSSES))

    def test_sain_fichier_a_blanc_egal_au_dessin(self):
        with open(LANCEUR.JEU_A_BLANC, encoding="utf-8") as f:
            t = f.read()
        self.assertEqual(B.lire_jeu_plante(t, B.empreinte_du_bloc(t))[0], JEU)

    def test_artefact_loi_changee_empreinte_du_texte(self):
        sha = B.empreinte_du_bloc(_texte_avec(JEU))
        j = copy.deepcopy(JEU)
        j["vraies"]["V3"]["puissance"] = 0.09
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "empreinte"):
            B.lire_jeu_plante(_texte_avec(j), sha)

    def test_artefact_jeu_incomplet(self):
        j = copy.deepcopy(JEU)
        del j["fausses"]["F4"]
        t = _texte_avec(j)
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "incomplet"):
            B.lire_jeu_plante(t, B.empreinte_du_bloc(t))
        j = copy.deepcopy(JEU)
        j["instruments"]["T-ANTI"] = JEU["vraies"]["V1"]
        t = _texte_avec(j)
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "incomplet"):
            B.lire_jeu_plante(t, B.empreinte_du_bloc(t))

    def test_artefact_fausse_hors_classe_couverte(self):
        k1 = JEU["archive_de_depart"]["K1"]
        hors = {"par morceaux": {"type": "si_sinon", "condition": {"sous_population": 0}, "si": k1,
                                 "sinon": {"type": "fixe", "probas": [1.0, 1.0, 1.0]}},
                "composition": {"type": "transformee", "base": k1, "puissance": 1.2,
                                "melange_aveugle": {"lambda": 0.2, "probas": [1.0, 1.0, 1.0]}},
                "loi inconnue": MONDE["fausses"]["S-F2"],
                "mélange avec une loi non fixe": {"type": "melange", "composantes": [k1, JEU["vraies"]["V1"]], "poids": [0.5, 0.5]}}
        for nom, loi in hors.items():
            with self.subTest(nom):
                self.assertIsNone(B.classe_couverte(loi, JEU["archive_de_depart"]))
                j = copy.deepcopy(JEU)
                j["fausses"]["F2"] = loi
                t = _texte_avec(j)
                with self.assertRaisesRegex(B.JeuPlanteRefuse, "classe que couvre"):
                    B.lire_jeu_plante(t, B.empreinte_du_bloc(t))

    def test_sain_formes_couvertes(self):
        formes = {n: B.classe_couverte(l, JEU["archive_de_depart"]) for n, l in JEU["fausses"].items()}
        self.assertEqual(formes["F1"], "copie d'une loi de l'archive")
        self.assertEqual(formes["F2"], formes["F3"])
        self.assertEqual(formes["F4"], "loi de l'archive tempérée et inclinée")

    def test_artefact_bloc_en_double_ou_absent(self):
        t = _texte_avec(JEU)
        with self.assertRaises(B.JeuPlanteRefuse):
            B.bloc_du_jeu(t + t)
        with self.assertRaises(B.JeuPlanteRefuse):
            B.bloc_du_jeu("rien")

    def test_artefact_vraie_egale_a_K1(self):
        j = copy.deepcopy(JEU)
        j["vraies"]["V4"] = JEU["archive_de_depart"]["K1"]
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "archive de départ"):
            B.verifier_jeu_plante(j)


# --- M1 : héritage de départ -----------------------------------------------------------------------------------------------


class HeritageDepart(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="heritage-v65-")
        self.sha = B.ecrire_heritage_depart(self.d, JEU)
        self.chemin = os.path.join(self.d, B.NOM_HERITAGE_DEPART)

    def tearDown(self):
        shutil.rmtree(self.d, True)

    def _reecrire(self, f):
        with open(self.chemin, encoding="utf-8") as x:
            obj = json.load(x)
        f(obj)
        os.remove(self.chemin)
        os.remove(self.chemin + ".sha256")
        return ecrire_json_scelle(self.chemin, obj)

    def test_sain_accepte(self):
        h = B.lire_heritage_depart(self.chemin, self.sha, JEU)
        self.assertEqual(h["archive"], JEU["archive_de_depart"])
        self.assertEqual(h["generation_lue"], 0)
        self.assertEqual(bf.vue_pour_proposeur(h)["lois_retenues"], [{"identifiant": "K1", "loi": JEU["archive_de_depart"]["K1"]}])

    def test_artefact_autre_empreinte(self):
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "empreinte"):
            B.lire_heritage_depart(self.chemin, "0" * 64, JEU)

    def test_artefact_sceau_faux(self):
        with open(self.chemin, "a", encoding="utf-8") as f:
            f.write(" ")
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "sceau"):
            B.lire_heritage_depart(self.chemin, self.sha, JEU)

    def test_artefact_K1_alteree(self):
        sha = self._reecrire(lambda o: o["archive"]["K1"]["biais"].__setitem__(1, 0.9417))
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "altérée"):
            B.lire_heritage_depart(self.chemin, sha, JEU)

    def test_artefact_loi_plantee_dans_l_heritage(self):
        sha = self._reecrire(lambda o: (o["archive"].__setitem__("V1", JEU["vraies"]["V1"]), o["statut"].__setitem__("V1", B.STATUT_K1)))
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "archive"):
            B.lire_heritage_depart(self.chemin, sha, JEU)
        sha = self._reecrire(lambda o: (o["archive"].pop("V1"), o["statut"].pop("V1"), o["archive"].__setitem__("K1", JEU["vraies"]["V2"])))
        with self.assertRaises(B.HeritageDepartRefuse):
            B.lire_heritage_depart(self.chemin, sha, JEU)

    def test_artefact_statut_non_declare(self):
        sha = self._reecrire(lambda o: o["statut"].__setitem__("K1", "survit"))
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "déclarée"):
            B.lire_heritage_depart(self.chemin, sha, JEU)


# --- M3 : juge avec l'archive, garde 18 -----------------------------------------------------------------------------------


class JugeAvecArchive(unittest.TestCase):
    def _fausses(self, tache):
        return [(n, c) for n, _, c, _ in B.plantees_de_la_generation(JEU, 1, 20261110, tache) if n in B.FAUSSES]

    def test_defaut_de_la_v64_reproduit_puis_corrige(self):
        """La v64 juge ses lois plantées sans archive : F1 à F4 (classe couverte) y sont promues (au moins une, ≈ 994 fois sur
        1 000 au brouillon) ; la v65 les juge avec {K1} : aucune promue, log W max ≤ 0 aux marges près."""
        archive = JEU["archive_de_depart"]
        vu_v64 = None
        for k in range(6):
            tache = f"essai-m3|{k}"
            fausses = self._fausses(tache)
            _, promus_v64, detail_v64, _ = T.juger([], fausses, MONDE, archive, 20261110, tache, 22)
            if promus_v64:
                vu_v64 = (tache, promus_v64, [detail_v64[i]["membres_d_archive"] for i in promus_v64])
                break
        self.assertIsNotNone(vu_v64, "la v64 n'a promu aucune fausse sur six tâches : défaut non reproduit")
        self.assertEqual(set(vu_v64[2]), {0})  # canal des témoins de la v64 : 0 membre d'archive
        tache = vu_v64[0]
        _, promues_p, detail, _, attendus = B.juger_v65([], self._fausses(tache), MONDE, archive, 20261110, tache, 22)
        self.assertEqual(promues_p, [])
        self.assertEqual(attendus, 4)
        for i, d in detail.items():
            self.assertEqual(d["membres_d_archive"], 4)
            self.assertLessEqual(d["log_richesse_max"], 1e-6)

    def test_seuil_hors_famille_log_m_sur_alpha(self):
        """Une loi plantée que le juge promeut seule (richesse ≥ 1/α) mais dont le log e reste sous log(m/α) n'est pas promue."""
        import math
        seuil = math.log(22 / 0.05)
        vu = None
        for k in range(40):
            tache = f"essai-seuil|{k}"
            pl = [(n, c) for n, _, c, _ in B.plantees_de_la_generation(JEU, 1, 20261110, tache) if n in ("V3", "V4")]
            _, promues_p, detail, _, _ = B.juger_v65([], pl, MONDE, JEU["archive_de_depart"], 20261110, tache, 22)
            for i, d in detail.items():
                self.assertEqual(d["promue"], i in promues_p)
                if d["promue"]:
                    self.assertGreaterEqual(d["log_e"], seuil)
                if d["promue_seule"] and not d["promue"]:
                    vu = d
            if vu:
                break
        self.assertIsNotNone(vu, "aucun cas « promue seule, log e < log(m/α) » en 40 tâches")
        self.assertLess(vu["log_e"], seuil)

    def test_artefact_garde_18_plantee_jugee_sans_archive(self):
        with self.assertRaises(B.PlanteeSansArchive):
            B.juger_v65([], self._fausses("essai-g18"), MONDE, JEU["archive_de_depart"], 20261110, "essai-g18", 22,
                        archive_des_plantees={})

    def test_artefact_garde_18_archive_plus_petite(self):
        archive = dict(JEU["archive_de_depart"], X=JEU["vraies"]["V2"])
        with self.assertRaises(B.PlanteeSansArchive):
            B.juger_v65([], self._fausses("essai-g18b"), MONDE, archive, 20261110, "essai-g18b", 22,
                        archive_des_plantees=JEU["archive_de_depart"])


# --- M4 : bras réel seul, génération 2 ----------------------------------------------------------------------------------------


class BrasEtGeneration2(unittest.TestCase):
    def test_sain_bras_reel(self):
        self.assertEqual(B.exiger_bras(["reel"]), ("reel",))

    def test_artefact_garde_20(self):
        for b in (["reel", "aleatoire"], ["recopie_melange"], "aleatoire"):
            with self.subTest(b), self.assertRaises(B.BrasRefuse):
                B.exiger_bras(b)
        code, _, err = _lancer([tempfile.mkdtemp() + "/x", "--a-blanc", "--graine", "1", "--bac", "factice", "--bras", "aleatoire"])
        self.assertEqual(code, 2)
        self.assertIn("BrasRefuse", err)

    def test_artefact_deux_generations_exigees(self):
        code, _, err = _lancer([tempfile.mkdtemp() + "/x", "--a-blanc", "--graine", "1", "--bac", "factice", "--generations", "3"])
        self.assertEqual(code, 2)
        with self.assertRaisesRegex(B.TourRefuse, "D2"):
            jouer(tempfile.mkdtemp(), plan_en_plus={"generations": 3})

    def test_sain_la_generation_2_lit_la_selection(self):
        r = Course.releve()
        ls = r["lecture_selection"]
        self.assertEqual(ls["attendu"], ls["lu"])
        self.assertEqual(ls["vue"], sorted({"K1"} | set(r["retenues"]["1"])))
        self.assertEqual(ls["vue"], ls["vue_attendue"])
        self.assertEqual(r["archives_de_jugement"]["2"].keys(), set(["K1"]) | set(r["retenues"]["1"]))
        self.assertEqual(r["membres_attendus"]["2"], B.membres_attendus(r["archives_de_jugement"]["2"]))
        self.assertTrue(all(c["membres_d_archive"] == r["membres_attendus"]["2"] for c in r["cartes"] if c["generation"] == 2 and c["gardien"] == "passe"))
        copies = [p for p in r["plantees"] if p["generation"] == 2 and p["source"]]
        self.assertEqual(len(copies), min(4, len(r["retenues"]["1"])))
        self.assertTrue(all(p["source"] in r["retenues"]["1"] and not p["promue"] for p in copies))
        self.assertEqual(sorted(p["nom"] for p in r["plantees"] if p["generation"] == 2 and not p["source"]), list(B.FAUSSES))

    def test_artefact_heritage_altere_refuse(self):
        def lire_altere(dossier, sha):
            chemin = os.path.join(dossier, bf.DOSSIER_ETAGE, T.NOM_SELECTION)
            with open(chemin, encoding="utf-8") as f:
                sel = json.load(f)
            sel["retenues"] = sel["retenues"][1:]
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(sel, f)
            return bf.lire_heritage(dossier, sha)
        with self.assertRaises(B.ArretTour) as cm:
            jouer(tempfile.mkdtemp(prefix="alt-v65-"), lire=lire_altere)
        rel = cm.exception.partiel["releve"]
        self.assertIn("SelectionNonVerifiee", rel["arret"])
        self.assertEqual(rel["generations_jouees"], [1])
        self.assertEqual(L.lire_criteres(rel)["code"], "C5")

    def test_artefact_heritage_d_un_autre_contenu_change_la_sortie(self):
        """Un héritage lu qui ne retient pas ce que la génération 1 a écrit (une retenue ôtée, cohérent par ailleurs) change la vue,
        l'archive de jugement et les copies de la génération 2 ; la lecture gelée le voit (C4)."""
        def lire_autre(dossier, sha):
            h = bf.lire_heritage(dossier, sha)
            if h["retenues"]:
                x = sorted(h["retenues"])[0]
                h = dict(h, retenues=[i for i in h["retenues"] if i != x], archive={k: v for k, v in h["archive"].items() if k != x})
            return h
        r, _ = jouer(tempfile.mkdtemp(prefix="autre-v65-"), lire=lire_autre)
        sain = Course.releve()
        self.assertNotEqual(r["lecture_selection"]["vue"], sain["lecture_selection"]["vue"])
        self.assertNotEqual(r["membres_attendus"]["2"], sain["membres_attendus"]["2"])
        self.assertEqual(L.lire_criteres(r)["code"], "C4")

    def test_copies_garde_21(self):
        h = {"retenues": ["a", "b", "c", "d", "e"], "archive": {x: {"type": "fixe", "probas": [1.0, 1.0, float(i + 1)]}
                                                                 for i, x in enumerate("abcde")}}
        copies = B.copies_de_la_selection(h, {"a": 1.0, "b": 9.0, "c": 5.0, "d": 7.0, "e": 3.0})
        self.assertEqual([s for _, s, _ in copies], ["b", "d", "c", "e"])
        self.assertTrue(B.exiger_copies_de_la_selection(copies, h))
        self.assertEqual(B.copies_de_la_selection({"retenues": [], "archive": {}}, {}), [])
        with self.assertRaises(B.CopieNonRetenue):
            B.exiger_copies_de_la_selection([("C1", "z", {"type": "fixe", "probas": [1.0, 1.0, 1.0]})], h)
        with self.assertRaises(B.CopieNonRetenue):
            B.exiger_copies_de_la_selection([("C1", "a", h["archive"]["b"])], h)
        with self.assertRaises(B.CopieNonRetenue):
            B.copies_de_la_selection(h, {"a": 1.0})


# --- gardes de dépense, GO ----------------------------------------------------------------------------------------------------


class Depense(unittest.TestCase):
    def test_sain_parts_suffisantes(self):
        r, _ = jouer(tempfile.mkdtemp(prefix="dep-v65-"), parts={"kimi": 33.0, "argon": 7.0}, cout=0.3, scenario="muet:1,2,3,4",
                     budget_appel=0.5)
        self.assertEqual(r["depense"]["par_relais_usd"], {"kimi": 0.6, "argon": 0.6})

    def test_artefact_arret_avant_l_appel_sous_la_part(self):
        with self.assertRaises(B.ArretTour) as cm:
            jouer(tempfile.mkdtemp(prefix="dep2-v65-"), parts={"kimi": 0.4, "argon": 7.0}, cout=0.3, scenario="muet:1,2,3,4",
                  budget_appel=0.5)
        rel = cm.exception.partiel["releve"]
        self.assertIn("arrêt avant l'appel", rel["arret"])
        self.assertEqual(rel["depense"]["appels"], 0)

    def test_artefact_arret_au_plafond(self):
        c = T.Compteur(1.0, 3600.0, {"kimi": 0.5, "argon": 0.5})
        c.ajouter(0.4, "proposeur", "kimi")
        with self.assertRaises(T.ArretTour):
            c.ajouter(0.2, "proposeur", "kimi")

    def test_go(self):
        self.assertTrue(B.exiger_go(False, None))
        self.assertTrue(B.exiger_go(True, {"identifiant": "GO-2026-11-08-02", "plafond_lu_usd": 45.0}))
        for go in (None, {}, {"identifiant": "GO-2026-11-08-02"}):
            with self.subTest(go), self.assertRaises(B.GoAbsent):
                B.exiger_go(True, go)
        with self.assertRaises(B.GoAbsent):  # le cœur refuse aussi, avant tout appel, une course réelle sans GO
            B.jouer_boucle(tempfile.mkdtemp(), monde=MONDE, jeu=JEU, heritage_depart={"archive": {}}, racine=1,
                           plan={"bras": ["reel"]}, decisions={}, proposeurs=[], adaptateur_etage=None, roles={},
                           fabrique_executeur=None, compteur=None, reel=True, go=None)


# --- plan gelé, texte scellé, configuration v5 ----------------------------------------------------------------------------------


PLAN_SAIN = {"generations": "2", "cartes_par_proposeur": "6", "m_e_bh": "22", "bras": "reel_seul", "d9": "mecanique",
             "plafond_modeles_usd": "40", "plafond_kimi_usd": "33", "plafond_argon_usd": "7", "plafond_machine_usd": "5",
             "go": "GO-2026-11-08-02", "go_montant_usd": "45", "duree_h": "72", "configuration_sha256": "a" * 64,
             "monde_sha256": LANCEUR.MONDE_SHA256, "jeu_plante_sha256": B.empreinte_du_bloc(_texte_avec(JEU)),
             "heritage_depart_sha256": "b" * 64}


def _plan(**chg):
    p = dict(PLAN_SAIN, **chg)
    return LANCEUR.DEBUT_PLAN + "\n" + "\n".join(f"{k}: {v}" for k, v in p.items() if v is not None) + "\n" + LANCEUR.FIN_PLAN


class PlanGele(unittest.TestCase):
    def test_sain(self):
        p = LANCEUR.lire_plan(_plan())
        self.assertEqual((p["plafond_modeles_usd"], p["plafond_kimi_usd"], p["plafond_argon_usd"], p["plafond_machine_usd"]), (40.0, 33.0, 7.0, 5.0))
        self.assertEqual(p["bras"], ["reel"])

    def test_artefacts(self):
        cas = {"bras": dict(bras="reel_et_references"), "générations": dict(generations="3"), "m": dict(m_e_bh="19"),
               "parts": dict(plafond_kimi_usd="34"), "GO": dict(go_montant_usd="40"), "durée": dict(duree_h="24"),
               "clé manquante": dict(go=None), "empreinte": dict(jeu_plante_sha256="xyz")}
        for nom, chg in cas.items():
            with self.subTest(nom), self.assertRaises(LANCEUR.PreenregistrementRefuse):
                LANCEUR.lire_plan(_plan(**chg))


class TexteScelle(unittest.TestCase):
    def _ecrire(self, dossier, nom, plan=None, jeu=JEU, sceau=True, en_plus="", empreintes=None):
        gel = empreintes or {r: sha256_fichier(os.path.join(RACINE, r)) for r in LANCEUR.FICHIERS_GELES}
        t = ("# préenregistrement (essai)\n\n" + LANCEUR.DEBUT_EMPREINTES + "\n" + "\n".join(f"{h}  {r}" for r, h in sorted(gel.items()))
             + "\n" + LANCEUR.FIN_EMPREINTES + "\n\n" + (plan or _plan()) + "\n\n" + B.texte_du_bloc(jeu) + "\n" + en_plus)
        chemin = os.path.join(dossier, nom)
        if sceau:
            ecrire_scelle(chemin, t)
        else:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(t)
        return chemin

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="prereg-v65-")

    def test_sain(self):
        c = self._ecrire(self.d, "preenregistrement-boucle-reelle-organisme-v1-v1.md")
        e, sha, gel, plan, jeu = LANCEUR.lire_preenregistrement(c, self.d)
        self.assertGreaterEqual(e, 2 ** 64)
        self.assertEqual(jeu, JEU)
        self.assertEqual(set(gel), set(LANCEUR.FICHIERS_GELES))

    def test_artefacts(self):
        nom = "preenregistrement-boucle-reelle-organisme-v1-v1.md"
        cas = {"brouillon": dict(nom="preenregistrement-boucle-reelle-organisme-v1-brouillon2.md"),
               "non scellé": dict(sceau=False), "marqueur": dict(en_plus="<<BLOC-V65>>\n"),
               "code différent": dict(empreintes=dict({r: sha256_fichier(os.path.join(RACINE, r)) for r in LANCEUR.FICHIERS_GELES},
                                                      **{"pole/boucle_reelle_v65.py": "0" * 64})),
               "fermeture incomplète": dict(empreintes={r: sha256_fichier(os.path.join(RACINE, r)) for r in LANCEUR.FICHIERS_GELES[1:]})}
        for k, kw in cas.items():
            with self.subTest(k):
                d = tempfile.mkdtemp(prefix="prereg-art-")
                c = self._ecrire(d, kw.pop("nom", nom), **kw)
                with self.assertRaises(LANCEUR.PreenregistrementRefuse):
                    LANCEUR.lire_preenregistrement(c, d)
        d = tempfile.mkdtemp(prefix="prereg-art-")
        j = copy.deepcopy(JEU)
        j["fausses"]["F1"] = MONDE["fausses"]["S-F1"]
        c = self._ecrire(d, nom, plan=_plan(jeu_plante_sha256=B.empreinte_du_bloc(_texte_avec(j))), jeu=j)
        with self.assertRaises(B.JeuPlanteRefuse):
            LANCEUR.lire_preenregistrement(c, d)


class ConfigurationV5(unittest.TestCase):
    PLAN = LANCEUR.lire_plan(_plan())

    def _conf(self):
        with open(os.path.join(RACINE, "exemples", "configuration-boucle-reelle-v5.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_commandes_v6_nommees_avec_leurs_empreintes(self):
        c = self._conf()["boucle_reelle_v65"]["commandes_v6"]
        self.assertEqual(c["kimi"]["sha256"], "889309305aeb37de9801c2f40c31769fd268abded1ac61ea94196fd0d51195ae")
        self.assertEqual(c["argon"]["sha256"], "5eae1a0468430e243c3c4e099b3969f949f62add688531aafdd7f0f44e036e55")
        self.assertEqual(c["registre_depense_cumulee"]["sha256"], "8ba92066b358ffb8206dea9e70251388c30620484fab1ac578778d9f21e578ff")
        self.assertEqual(c["source"]["commit"], "12f9e0e38f2cf7adb61a9c3ddf0ee4c5c66556d9")
        conf = self._conf()
        self.assertEqual(conf["budget"]["plafond_usd"], 40.0)
        self.assertEqual(conf["boucle_reelle_v65"]["parts_usd"], {"kimi": 33.0, "argon": 7.0})
        self.assertEqual(conf["boucle_reelle_v65"]["plafond_machine_usd"], 5.0)

    def _avec_fausses_commandes(self):
        conf, d = self._conf(), tempfile.mkdtemp(prefix="cmd-v65-")
        s = conf["boucle_reelle_v65"]["commandes_v6"]
        for n in ("kimi", "argon", "registre_depense_cumulee"):
            p = os.path.join(d, os.path.basename(s[n]["chemin"]))
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"# doublure de {n}\n")
            for f in conf["fournisseurs"].values():
                f["commande"] = [p if x == s[n]["chemin"] else x for x in f["commande"]]
            s[n] = {"chemin": p, "sha256": sha256_fichier(p)}
        return conf

    def test_sain(self):
        self.assertTrue(LANCEUR.verifier_configuration_v65(self._avec_fausses_commandes(), self.PLAN))

    def test_artefacts(self):
        conf = self._avec_fausses_commandes()
        with open(conf["boucle_reelle_v65"]["commandes_v6"]["kimi"]["chemin"], "a", encoding="utf-8") as f:
            f.write("# altérée\n")
        with self.assertRaisesRegex(LANCEUR.ConfigurationRefusee, "empreinte"):
            LANCEUR.verifier_configuration_v65(conf, self.PLAN)
        for nom, f in {"part": lambda c: c["boucle_reelle_v65"]["parts_usd"].__setitem__("kimi", 34.0),
                       "plafond": lambda c: c["budget"].__setitem__("plafond_usd", 50.0),
                       "GO": lambda c: c["boucle_reelle_v65"].__setitem__("go", "GO-2026-11-02-23"),
                       "machine": lambda c: c["boucle_reelle_v65"].__setitem__("plafond_machine_usd", 10.0),
                       "commande lancée": lambda c: c["fournisseurs"]["argon"].__setitem__("commande", ["/bin/true"])}.items():
            with self.subTest(nom):
                c = self._avec_fausses_commandes()
                f(c)
                with self.assertRaises(LANCEUR.ConfigurationRefusee):
                    LANCEUR.verifier_configuration_v65(c, self.PLAN)


# --- bac à sable, garde 22 -------------------------------------------------------------------------------------------------


class Bac(unittest.TestCase):
    @unittest.skipIf(shutil.which("bwrap"), "bwrap présent : l'artefact « bwrap absent » ne se joue pas ici")
    def test_artefact_bwrap_absent_refus_code_2_sans_repli(self):
        sortie = tempfile.mkdtemp() + "/x"
        code, _, err = _lancer([sortie, "--a-blanc", "--graine", "1", "--bac", "reel"])
        self.assertEqual(code, 2)
        self.assertIn("BacASableIndisponible", err)
        self.assertIn("aucun repli", err)
        self.assertFalse(os.path.exists(sortie))

    def test_garde_22(self):
        self.assertTrue(LANCEUR.exiger_machine(64097, (0, 9)))
        self.assertTrue(LANCEUR.exiger_machine(64097, (1, 0)))
        for u, v in ((64097, None), (64097, (0, 8)), (0, (0, 9)), (None, (0, 9))):
            with self.subTest(u=u, v=v), self.assertRaises(LANCEUR.MachineRefusee):
                LANCEUR.exiger_machine(u, v)

    def test_version_bwrap(self):
        ok = lambda *a, **k: subprocess.CompletedProcess(a, 0, "bubblewrap 0.9.0\n", "")  # noqa: E731
        self.assertEqual(LANCEUR.version_bwrap(ok, lambda n: "/usr/bin/bwrap"), (0, 9))
        self.assertIsNone(LANCEUR.version_bwrap(ok, lambda n: None))
        self.assertIsNone(LANCEUR.version_bwrap(lambda *a, **k: subprocess.CompletedProcess(a, 0, "?", ""), lambda n: "/x"))

    @unittest.skipIf(BAC_NON_JOUE, "vrai bac à sable : non joué sur cette machine (bwrap absent ou POLE_ESSAI_BAC_REEL_NON_JOUE=1)")
    def test_sain_bac_reel_essai_a_blanc(self):
        sortie = tempfile.mkdtemp() + "/x"
        argv = [sortie, "--a-blanc", "--graine", "7", "--bac", "reel"]
        if os.geteuid() == 0:
            argv += ["--utilisateur-bac", os.environ.get("POLE_UTILISATEUR_BAC", "64097")]
        code, out, err = _lancer(argv)
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, LANCEUR.SORTIE), encoding="utf-8") as f:
            r = json.load(f)["releve"]
        self.assertTrue(all(not e["factice"] for e in r["etages"]))


# --- fermeture du code gelé ----------------------------------------------------------------------------------------------------


class Fermeture(unittest.TestCase):
    def test_bloc_gele_egal_a_la_fermeture_statique(self):
        t64 = _charger("essais_tour_ferme_v64_pour_v65", "essais/test_tour_ferme_v64.py")
        ferm, pile = set(), ["demonstrations/boucle_reelle_v65.py", "demonstrations/lire_boucle_reelle_v65.py"]
        while pile:
            x = pile.pop()
            if x not in ferm:
                ferm.add(x)
                pile += sorted(t64.imports_de(x) - ferm)
        ferm |= {"demonstrations/tour_ferme_v64.py"} | t64.fermeture_statique()  # lanceur v64 chargé par chemin
        self.assertEqual(sorted(ferm), sorted(LANCEUR.FICHIERS_GELES))


# --- essai à blanc de bout en bout, lecture -----------------------------------------------------------------------------------


class EssaiABlanc(unittest.TestCase):
    def test_bout_en_bout_et_lecture(self):
        sortie = tempfile.mkdtemp(prefix="ab-v65-") + "/sortie"
        code, out, err = _lancer([sortie, "--a-blanc", "--graine", "20261110", "--bac", "factice"])
        self.assertEqual(code, 0, err)
        lecture = sortie + "-lecture.json"
        o, e = io.StringIO(), io.StringIO()
        with redirect_stdout(o), redirect_stderr(e):
            self.assertEqual(LECTEUR.principal([sortie, lecture]), 0, e.getvalue())
        with open(lecture, encoding="utf-8") as f:
            lu = json.load(f)
        self.assertEqual(lu["code"], "C1")
        self.assertIsNotNone(lu["audits"]["A1"])
        self.assertFalse(lu["audits"]["A1"]["bac_reel_partout"])  # exécuteur factice déclaré : l'audit A1 le dit
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(LECTEUR.principal([sortie, lecture]), 2)  # jamais d'écrasement
        with open(os.path.join(sortie, LANCEUR.SORTIE), "a", encoding="utf-8") as f:
            f.write(" ")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(LECTEUR.principal([sortie, lecture + "2"]), 2)  # sceau faux

    def test_dossier_non_vide_refuse(self):
        d = tempfile.mkdtemp()
        open(os.path.join(d, "x"), "w").close()
        self.assertEqual(_lancer([d, "--a-blanc", "--graine", "1", "--bac", "factice"])[0], 2)

    def test_arret_code_3_releve_partiel_scelle(self):
        sortie = tempfile.mkdtemp() + "/x"
        code, _, err = _lancer([sortie, "--a-blanc", "--graine", "3", "--bac", "factice", "--scenario-proposeur", "erreur"])
        self.assertEqual(code, 3)
        lecture = sortie + "-l.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(LECTEUR.principal([sortie, lecture, "--sans-oracle"]), 0)
        with open(lecture, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["code"], "C5")


if __name__ == "__main__":
    unittest.main()
