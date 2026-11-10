"""Essais du code v66 (corrections de la contre-lecture du code v65, `contre-lecture-code-v65-v2.md`, `c4ddfc7f…`) : cœur, lanceur
et gardes, chacune sur un cas sain et sur un artefact (R5). Aucun réseau, aucune clé, aucun appel de modèle. Les essais qui
exigent `bwrap` sont déclarés non joués quand `POLE_ESSAI_BAC_REEL_NON_JOUE=1` ou que `bwrap` manque ; l'artefact « bwrap absent »
se joue partout (`LANCEUR.WHICH` remplacée, CLV65-06).

  POLE_ESSAI_BAC_REEL_NON_JOUE=1 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_boucle_reelle_v66.py
"""

import copy
import datetime
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import boucle_fermee_v59 as bf  # noqa: E402
from pole import boucle_reelle_v65 as B65  # noqa: E402
from pole import boucle_reelle_v66 as B  # noqa: E402
from pole import lecture_boucle_reelle_v66 as L  # noqa: E402
from pole import tour_ferme_v64 as T  # noqa: E402
from pole.outils import ecrire_json_scelle, ecrire_scelle, sha256_fichier  # noqa: E402


def _charger(nom, rel):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LANCEUR = _charger("lanceur_boucle_reelle_v66_essais", "demonstrations/boucle_reelle_v66.py")
LECTEUR = _charger("lecteur_boucle_reelle_v66_essais", "demonstrations/lire_boucle_reelle_v66.py")
MONDE = A.charger_monde(RACINE)
JEU = B65.jeu_du_dessin(MONDE)
RACINE_GRAINES = 20261110
BAC_NON_JOUE = os.environ.get("POLE_ESSAI_BAC_REEL_NON_JOUE") == "1" or not shutil.which("bwrap")


def _lancer(module, argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = module.principal(argv)
    return code, out.getvalue(), err.getvalue()


def _roles_a_blanc(scenario_proposeur=None, cout=0.0, scenario_experimentateur=None, familles=None):
    ns = type("Args", (), {"cout_simule_usd": cout, "scenario_proposeur": scenario_proposeur, "cout_simule_etage_usd": 0.0,
                           "scenario_experimentateur": scenario_experimentateur, "scenario_verificateur": None,
                           "familles_a_blanc": familles, "prix_entree_kimi_usd_par_million_jetons": None,
                           "prix_entree_argon_usd_par_million_jetons": None})()
    return LANCEUR.L64.roles_a_blanc(ns, tempfile.mkdtemp(prefix="roles-v66-"))


def _depart():
    d = tempfile.mkdtemp(prefix="depart-essai-v66-")
    sha = B65.ecrire_heritage_depart(d, JEU)
    return B65.lire_heritage_depart(os.path.join(d, B65.NOM_HERITAGE_DEPART), sha, JEU)


def jouer(sortie=None, lire=None, juger=None, archive_des_plantees=None, parts=None, cout=0.0, scenario=None,
          scenario_experimentateur=None, plan_en_plus=None, budget_appel=None, familles=None, apres_roles=None):
    """La boucle à blanc par le chemin du cœur v66 (doublures, exécuteur factice déclaré) ; rend (relevé, journal) ou lève."""
    proposeurs, etage, roles = _roles_a_blanc(scenario, cout, scenario_experimentateur, familles)
    for p in proposeurs:
        p.budget = p.budget if budget_appel is None else budget_appel
    if apres_roles:
        apres_roles(proposeurs, etage, roles)
    plan = {"generations": 2, "cartes_par_proposeur": 6, "m_e_bh": 22, "bras": ["reel"], **(plan_en_plus or {})}
    return B.jouer_boucle(sortie or tempfile.mkdtemp(prefix="course-v66-"), monde=MONDE, jeu=JEU, heritage_depart=_depart(),
                          racine=RACINE_GRAINES, plan=plan, decisions={"d7": "archive_propre", "d9": "mecanique"},
                          proposeurs=proposeurs, adaptateur_etage=etage, roles=roles,
                          fabrique_executeur=lambda: A.choisir_executeur("factice"), compteur=T.Compteur(1e9, 72 * 3600.0, parts or {}),
                          lire=lire, juger=juger, archive_des_plantees=archive_des_plantees, environnement=dict(T.ENV_A_BLANC))


def arret(**kw):
    """Joue la boucle, exige un arrêt, rend le relevé partiel."""
    try:
        jouer(**kw)
    except B.ArretTour as e:
        return e.partiel["releve"]
    raise AssertionError("la boucle devait s'arrêter")


class Course:
    """Une course à blanc saine partagée (≈ 20 s), jouée une fois par processus."""
    _releve = None

    @classmethod
    def releve(cls):
        if cls._releve is None:
            cls._releve = jouer()[0]
        return copy.deepcopy(cls._releve)


def _plantee_servie(generation, nom):
    pl = B65.plantees_de_la_generation(JEU, generation, RACINE_GRAINES, B.tache_de(generation))
    return next(c for n, _, c, _ in pl if n == nom)


# --- juge v66 : équivalence avec la v64 et la v65, garde 18, seuil hors famille --------------------------------------------------


class JugeV66(unittest.TestCase):
    def _jeu(self, tache):
        pl = [(n, c) for n, _, c, _ in B65.plantees_de_la_generation(JEU, 1, RACINE_GRAINES, tache)]
        cartes = [T.carte_servie(T.identifiant_opaque(RACINE_GRAINES, tache, f"c{k}"), loi, "essai")
                  for k, loi in enumerate([JEU["vraies"]["V1"], JEU["vraies"]["V2"], JEU["fausses"]["F2"]])]
        return cartes, pl

    def test_sain_meme_calcul_que_v64_et_v65_membre_dominant_garde(self):
        tache = "essai-juge-v66"
        cartes, pl = self._jeu(tache)
        archive = JEU["archive_de_depart"]
        p66, pp66, d66, m66, a66 = B.juger_v66(cartes, pl, MONDE, archive, RACINE_GRAINES, tache, 22)
        p64, _, d64, m64 = T.juger(cartes, [], MONDE, archive, RACINE_GRAINES, tache, 22)
        _, pp65, d65, m65, a65 = B65.juger_v65(cartes, pl, MONDE, archive, RACINE_GRAINES, tache, 22)
        self.assertEqual((p66, pp66, m66, a66), (p64, pp65, m64, a65))
        for i, d in d65.items():
            self.assertEqual({k: v for k, v in d66[i].items() if k != "membre_dominant_final"}, d)
        for i in d66:
            if d66[i].get("membres_d_archive") is not None:
                self.assertIsInstance(d66[i]["membre_dominant_final"], str)
                self.assertTrue(d66[i]["empreinte_engagement"])
        self.assertTrue(p66)  # au moins une carte promue (V1 et V2 portent bien plus que {K1})

    def test_artefact_garde_18(self):
        _, pl = self._jeu("essai-g18-v66")
        with self.assertRaises(B.PlanteeSansArchive):
            B.juger_v66([], pl, MONDE, JEU["archive_de_depart"], RACINE_GRAINES, "essai-g18-v66", 22, archive_des_plantees={})
        with self.assertRaises(B.TourRefuse):
            B.juger_v66([{"identifiant": str(k), "loi_predictive": {}} for k in range(23)], [], MONDE, {}, RACINE_GRAINES, "x", 22)

    def test_seuil_hors_famille_log_m_sur_alpha(self):
        import math
        seuil = math.log(22 / 0.05)
        vu = None
        for k in range(40):
            tache = f"essai-seuil-v66|{k}"
            pl = [(n, c) for n, _, c, _ in B65.plantees_de_la_generation(JEU, 1, RACINE_GRAINES, tache) if n in ("V3", "V4")]
            _, promues_p, detail, _, _ = B.juger_v66([], pl, MONDE, JEU["archive_de_depart"], RACINE_GRAINES, tache, 22)
            for i, d in detail.items():
                self.assertEqual(d["promue"], i in promues_p)
                if d["promue_seule"] and not d["promue"]:
                    vu = d
            if vu:
                break
        self.assertIsNotNone(vu, "aucun cas « promue seule, log e < log(m/α) » en 40 tâches")
        self.assertLess(vu["log_e"], seuil)


# --- CLV65-02 : jugements au relevé avant les étages ; héritage refusé consigné --------------------------------------------------


def juge_qui_promeut(nom, generation=1):
    def juger(cartes, plantees, monde, archive, racine, tache, m, archive_des_plantees=None):
        promues, promues_p, detail, m, attendus = B.juger_v66(cartes, plantees, monde, archive, racine, tache, m, archive_des_plantees)
        if tache == B.tache_de(generation):
            for n, c in plantees:
                if n == nom:
                    detail[c["identifiant"]]["promue"] = True
                    if c["identifiant"] not in promues_p:
                        promues_p.append(c["identifiant"])
        return promues, promues_p, detail, m, attendus
    return juger


class JugementsAuReleve(unittest.TestCase):
    def test_sain_jugements_puis_verdicts(self):
        r = Course.releve()
        self.assertTrue(all(c["etage"] in ("joué", "sans objet (refusée au gardien)") for c in r["cartes"]))
        self.assertTrue(all(p["etage"] in ("joué", "sans objet (refusée au gardien)") for p in r["plantees"]))
        self.assertTrue(all(c["retenue"] is not None for c in r["cartes"]))

    def test_artefact_arret_pendant_l_etage_jugements_presents(self):
        r = arret(scenario_experimentateur="fabrique")  # contre-calcul en désaccord (garde 10), pendant l'étage de la génération 1
        self.assertIn("contre-calcul", r["arret"])
        g1 = [p for p in r["plantees"] if p["generation"] == 1]
        self.assertEqual(sorted(p["nom"] for p in g1), sorted(B.VRAIES + B.FAUSSES + B.INSTRUMENTS))
        self.assertTrue(all(p["etage"] in ("en attente", "sans objet (refusée au gardien)") for p in g1))
        self.assertEqual(len([c for c in r["cartes"] if c["generation"] == 1]), 12)
        self.assertTrue(any(c["promue"] for c in r["cartes"]))
        self.assertEqual(r["membres_attendus"], {"1": 4})
        self.assertEqual(L.lire_criteres(r)["code"], "C5")

    def test_artefact_arret_ne_masque_pas_une_fausse_promue(self):
        r = arret(scenario_experimentateur="fabrique", juger=juge_qui_promeut("F2"))
        f2 = next(p for p in r["plantees"] if p["nom"] == "F2" and p["generation"] == 1)
        self.assertTrue(f2["promue"])
        lu = L.lire_criteres(r)
        self.assertEqual((lu["code"], lu["aussi"]), ("C5", ["C2 (partielle)"]))

    def test_artefact_heritage_altere_C4_partielle(self):
        def lire_altere(dossier, sha):
            chemin = os.path.join(dossier, bf.DOSSIER_ETAGE, T.NOM_SELECTION)
            with open(chemin, encoding="utf-8") as f:
                sel = json.load(f)
            sel["retenues"] = sel["retenues"][1:]
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(sel, f)
            return bf.lire_heritage(dossier, sha)
        r = arret(lire=lire_altere)
        self.assertIn("SelectionNonVerifiee", r["arret"])
        self.assertEqual(r["lecture_selection"]["refus"]["type"], "SelectionNonVerifiee")
        lu = L.lire_criteres(r)
        self.assertEqual(lu["code"], "C5")
        self.assertIn("C4 (partielle)", lu["aussi"])

    def test_artefact_empreinte_lue_differente_de_l_ecrite(self):
        def lire_bilan_altere(dossier, sha):
            p = os.path.join(dossier, bf.NOM_BILAN)
            with open(p, encoding="utf-8") as f:
                obj = json.load(f)
            obj["comptes"]["altere_apres_le_sceau"] = True
            os.remove(p)
            os.remove(p + ".sha256")
            ecrire_json_scelle(p, obj)  # sceau juste, empreinte ≠ celle que la génération 1 a rendue
            return bf.lire_heritage(dossier, sha)
        s = tempfile.mkdtemp(prefix="bilan-altere-v66-")
        r = arret(sortie=s, lire=lire_bilan_altere)
        ls = r["lecture_selection"]
        self.assertNotEqual(ls["lu"], ls["attendu"])
        self.assertEqual(ls["lu"], sha256_fichier(os.path.join(s, "generation-1", bf.NOM_BILAN)))  # l'empreinte sur disque, pas l'écho
        ecarts = L.p6_ecarts(r)
        self.assertTrue(any("empreinte lue" in e for e in ecarts))
        self.assertIn("C4 (partielle)", L.lire_criteres(r)["aussi"])

    def test_artefact_relecture_finale_refusee(self):
        def lire_finale(dossier, sha):
            if dossier.endswith("generation-2"):
                raise bf.SelectionNonVerifiee("bilan de la génération 2 : sceau faux (essai)")
            return bf.lire_heritage(dossier, sha)
        r = arret(lire=lire_finale)
        self.assertEqual(r["generations_jouees"], [1, 2])
        self.assertEqual(r["selection_finale"]["refus"]["type"], "SelectionNonVerifiee")
        lu = L.lire_criteres(r)
        self.assertEqual(lu["code"], "C5")
        self.assertIn("C4 (partielle)", lu["aussi"])


# --- CLV65-03 : vue servie (garde 23) --------------------------------------------------------------------------------------------


class ProposeurTronque(T.ProposeurAdaptateur):
    """Artefact : sert aux proposeurs une vue réduite à sa première loi (« ne sert que K1 »), après la garde d'avant l'appel."""

    def proposer(self, consigne, contexte, tache):
        return super().proposer(consigne, dict(contexte, lois_retenues=contexte["lois_retenues"][:1]), tache)


class VueServie(unittest.TestCase):
    def test_sain_vues_servies_au_releve(self):
        r = Course.releve()
        v = r["vues_servies"]
        self.assertEqual(v["1"]["identifiants"], ["K1"])
        self.assertEqual(v["2"]["identifiants"], sorted({"K1"} | set(r["retenues"]["1"])))
        self.assertEqual(v["2"]["attendus"], v["2"]["identifiants"])
        for g in ("1", "2"):
            self.assertEqual(len(v[g]["appels"]), 2)
            self.assertTrue(all(a["texte_recu_sha256"] == v[g]["texte_sha256"] for a in v[g]["appels"]))
        self.assertEqual(L.p6_ecarts(r), [])

    def test_artefacts_garde_23_avant_l_appel(self):
        archive = {"K1": JEU["archive_de_depart"]["K1"], "a": {"type": "fixe", "probas": [1.0, 2.0, 1.0]}}
        ctx = {"lois_retenues": [{"identifiant": i, "loi": l} for i, l in sorted(archive.items())]}
        self.assertEqual(B.exiger_vue_servie(ctx, ["K1", "a"], archive, set())["identifiants"], ["K1", "a"])
        cas = {"ne sert que K1": (dict(ctx, lois_retenues=ctx["lois_retenues"][:1]), ["K1", "a"], archive, set()),
               "loi en trop": (ctx, ["K1"], archive, set()),
               "loi servie différente": (ctx, ["K1", "a"], dict(archive, a={"type": "fixe", "probas": [1.0, 1.0, 1.0]}), set()),
               "loi plantée servie": (ctx, ["K1", "a"], archive, {"a"}),
               "contexte sans lois": ({}, ["K1"], archive, set())}
        for nom, (c, ids, arch, pl) in cas.items():
            with self.subTest(nom), self.assertRaises(B.VueServieRefusee):
                B.exiger_vue_servie(c, ids, arch, pl)

    def test_artefacts_garde_23_apres_l_appel(self):
        p = type("P", (), {"nom": "p", "appels": [{"consigne_sha256": "a" * 64}]})()
        self.assertEqual(B.exiger_texte_recu(p, 0, "a" * 64), "a" * 64)
        for avant, sha in ((1, "a" * 64), (0, "b" * 64)):
            with self.subTest(avant=avant, sha=sha[0]), self.assertRaises(B.VueServieRefusee):
                B.exiger_texte_recu(p, avant, sha)
        with self.assertRaises(B.VueServieRefusee):
            B.exiger_texte_recu(type("Q", (), {"nom": "q"})(), 0, "a" * 64)

    def test_artefact_la_generation_2_ne_sert_que_K1(self):
        def tronquer(proposeurs, etage, roles):
            for p in proposeurs:
                p.__class__ = ProposeurTronque
        r = arret(apres_roles=tronquer)
        self.assertIn("VueServieRefusee", r["arret"])
        self.assertEqual([i["garde"] for i in r["incidents"]], [23])
        self.assertEqual(r["generations_jouees"], [1])
        lu = L.lire_criteres(r)
        self.assertEqual((lu["code"], lu["aussi"]), ("C5", ["C4 (partielle)"]))

    def test_artefact_heritage_d_un_autre_contenu(self):
        """Un héritage lu qui ne retient pas ce que la génération 1 a écrit (une retenue ôtée) : la vue servie ne serait plus
        {K1} ∪ retenues écrites ; la garde 23 arrête avant tout appel de la génération 2 ; lu C5 et C4 (partielle)."""
        def lire_autre(dossier, sha):
            h = bf.lire_heritage(dossier, sha)
            if h["retenues"] and dossier.endswith("generation-1"):
                x = sorted(h["retenues"])[0]
                h = dict(h, retenues=[i for i in h["retenues"] if i != x], archive={k: v for k, v in h["archive"].items() if k != x})
            return h
        r = arret(lire=lire_autre)
        self.assertEqual([i["garde"] for i in r["incidents"]], [23])
        self.assertTrue(any("retenues lues" in e for e in L.p6_ecarts(r)))
        self.assertIn("C4 (partielle)", L.lire_criteres(r)["aussi"])


# --- garde 7 (CLV65-05 et X01), garde 21 câblée (X04) ---------------------------------------------------------------------------


class Garde7EtCopies(unittest.TestCase):
    def test_unitaire_selection(self):
        self.assertTrue(B.exiger_selection_sans_plantee(["F-a"], {"F-b", "P-c"}, "t"))
        with self.assertRaises(T.TemoinRetenu):
            B.exiger_selection_sans_plantee(["F-a", "P-c"], {"F-b", "P-c"}, "t")

    def test_artefact_loi_plantee_dans_la_selection(self):
        f1 = _plantee_servie(1, "F1")["identifiant"]
        origine = T.jouer_etage

        def etage(dossier_etage, cartes, *a, **k):
            resume, chemin, sha, tranche, cc = origine(dossier_etage, cartes, *a, **k)
            if os.path.basename(dossier_etage) == bf.DOSSIER_ETAGE and "generation-1" in dossier_etage:
                with open(chemin, encoding="utf-8") as f:
                    sel = json.load(f)
                sel["retenues"] = sel["retenues"] + [f1]
                os.chmod(chemin, 0o644)
                with open(chemin, "w", encoding="utf-8") as f:
                    json.dump(sel, f)
            return resume, chemin, sha, tranche, cc
        with mock.patch.object(T, "jouer_etage", etage):
            r = arret()
        self.assertIn("TemoinRetenu", r["arret"])
        self.assertEqual([(i["garde"], i["generation"]) for i in r["incidents"]], [(7, 1)])
        self.assertIn("C4 (partielle)", L.lire_criteres(r)["aussi"])

    def test_artefact_loi_plantee_dans_l_heritage_lu(self):
        f1 = _plantee_servie(1, "F1")

        def lire(dossier, sha):
            h = bf.lire_heritage(dossier, sha)
            if dossier.endswith("generation-1"):
                h = dict(h, archive=dict(h["archive"], **{f1["identifiant"]: f1["loi_predictive"]}))
            return h
        r = arret(lire=lire)
        self.assertIn("TemoinRetenu", r["arret"])
        self.assertEqual([(i["garde"], i["generation"]) for i in r["incidents"]], [(7, 2)])

    def test_artefact_loi_plantee_a_la_relecture_finale(self):
        f1 = _plantee_servie(2, "F1")

        def lire(dossier, sha):
            h = bf.lire_heritage(dossier, sha)
            if dossier.endswith("generation-2"):
                h = dict(h, archive=dict(h["archive"], **{f1["identifiant"]: f1["loi_predictive"]}))
            return h
        r = arret(lire=lire)
        self.assertIn("TemoinRetenu", r["arret"])
        self.assertEqual([(i["garde"], i["generation"]) for i in r["incidents"]], [(7, "finale")])
        self.assertIn("C4 (partielle)", L.lire_criteres(r)["aussi"])

    def test_sain_copies_des_quatre_premieres_retenues_par_log_e(self):
        r = Course.releve()
        par = {c["identifiant_servi"]: c for c in r["cartes"] if c["generation"] == 1 and c.get("retenue")}
        attendues = sorted(par, key=lambda i: (-float(par[i]["log_e"]), i))[:4]
        copies = sorted((p for p in r["plantees"] if p["generation"] == 2 and p["source"]), key=lambda p: p["nom"])
        self.assertEqual([p["source"] for p in copies], attendues)
        self.assertEqual([p["nom"] for p in copies], ["C1", "C2", "C3", "C4"][:len(attendues)])
        self.assertTrue(all(p["loi"] == par[p["source"]]["loi"] for p in copies))

    def test_artefact_copie_d_une_carte_non_retenue(self):
        def copies(h, log_e, n=4):
            return [("C1", "F-000000000000", json.loads(json.dumps(h["archive"]["K1"])))]
        with mock.patch.object(B65, "copies_de_la_selection", copies):
            r = arret()
        self.assertIn("CopieNonRetenue", r["arret"])
        self.assertEqual([i["garde"] for i in r["incidents"]], [21])
        self.assertIn("C4 (partielle)", L.lire_criteres(r)["aussi"])


# --- bras, générations, familles, dépense, GO --------------------------------------------------------------------------------------


class BrasGenerationsFamilles(unittest.TestCase):
    def test_garde_20_et_D2(self):
        self.assertEqual(B.exiger_bras(["reel"]), ("reel",))
        with self.assertRaises(B.BrasRefuse):
            B.exiger_bras(["reel", "aleatoire"])
        with self.assertRaisesRegex(B.TourRefuse, "D2"):
            jouer(plan_en_plus={"generations": 3})
        for opt in (["--bras", "aleatoire"], ["--generations", "3"]):
            with self.subTest(opt):
                code, _, err = _lancer(LANCEUR, [tempfile.mkdtemp() + "/x", "--a-blanc", "--graine", "1", "--bac", "factice", *opt])
                self.assertEqual(code, 2, err)

    def test_familles_dans_le_coeur(self):
        with self.assertRaises(T.FamillesNonSeparees):
            jouer(familles="a,a")

    def test_familles_dans_le_lanceur(self):
        sortie = tempfile.mkdtemp() + "/x"
        code, _, err = _lancer(LANCEUR, [sortie, "--a-blanc", "--graine", "1", "--bac", "factice", "--familles-a-blanc", "a,a"])
        self.assertEqual(code, 2, err)
        self.assertIn("FamillesNonSeparees", err)
        self.assertFalse(os.path.exists(sortie))


class Depense(unittest.TestCase):
    def test_sain_parts_suffisantes(self):
        r, _ = jouer(parts={"kimi": 33.0, "argon": 7.0}, cout=0.3, scenario="muet:1,2,3,4", budget_appel=0.5)
        self.assertEqual(r["depense"]["par_relais_usd"], {"kimi": 0.6, "argon": 0.6})

    def test_artefact_arret_avant_l_appel_sous_la_part(self):
        r = arret(parts={"kimi": 0.4, "argon": 7.0}, cout=0.3, scenario="muet:1,2,3,4", budget_appel=0.5)
        self.assertIn("arrêt avant l'appel", r["arret"])
        self.assertEqual(r["depense"]["appels"], 0)

    def test_artefact_plafond_restant_avant_l_appel(self):
        c = T.Compteur(1.0, 3600.0, {})
        c.ajouter(0.8, "proposeur", "kimi")
        B.exiger_part_avant_appel(c, "kimi", 0.1)
        with self.assertRaisesRegex(B.ArretTour, "plafond restant"):
            B.exiger_part_avant_appel(c, "kimi", 0.5)

    def test_artefact_cout_d_un_appel_qui_s_arrete_compte(self):
        r = arret(cout=0.3, scenario="refus:2")  # deuxième appel de chaque proposeur : refus R-764, coût déclaré 0,3
        self.assertIn("refus", r["arret"])
        self.assertEqual(r["depense"]["appels"], 3)
        self.assertAlmostEqual(r["depense"]["par_relais_usd"]["kimi"], 0.6)

    def test_artefact_arret_au_plafond(self):
        c = T.Compteur(1.0, 3600.0, {"kimi": 0.5, "argon": 0.5})
        c.ajouter(0.4, "proposeur", "kimi")
        with self.assertRaises(T.ArretTour):
            c.ajouter(0.2, "proposeur", "kimi")

    def test_go(self):
        self.assertTrue(B.exiger_go(True, {"identifiant": "GO-2026-11-08-02", "plafond_lu_usd": 45.0}))
        for go in (None, {}, {"identifiant": "GO-2026-11-08-02"}):
            with self.subTest(go), self.assertRaises(B.GoAbsent):
                B.exiger_go(True, go)
        with self.assertRaises(B.GoAbsent):  # le cœur refuse, avant tout appel, une course réelle sans GO
            B.jouer_boucle(tempfile.mkdtemp(), monde=MONDE, jeu=JEU, heritage_depart={"archive": {}}, racine=1,
                           plan={"bras": ["reel"]}, decisions={}, proposeurs=[], adaptateur_etage=None, roles={},
                           fabrique_executeur=None, compteur=None, reel=True, go=None)


# --- gardes 17 et 19 (fonctions v65 réutilisées par la v66) -------------------------------------------------------------------------


def _texte_avec(jeu):
    return "# texte\n\n" + B65.texte_du_bloc(jeu) + "\n\nfin\n"


class Gardes17Et19(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="heritage-v66-")
        self.sha = B65.ecrire_heritage_depart(self.d, JEU)
        self.chemin = os.path.join(self.d, B65.NOM_HERITAGE_DEPART)

    def _reecrire(self, f):
        with open(self.chemin, encoding="utf-8") as x:
            obj = json.load(x)
        f(obj)
        os.remove(self.chemin)
        os.remove(self.chemin + ".sha256")
        return ecrire_json_scelle(self.chemin, obj)

    def test_garde_17(self):
        self.assertEqual(B65.lire_heritage_depart(self.chemin, self.sha, JEU)["generation_lue"], 0)
        with self.assertRaisesRegex(B.HeritageDepartRefuse, "empreinte"):
            B65.lire_heritage_depart(self.chemin, "0" * 64, JEU)
        cas = {"K1 altérée": lambda o: o["archive"]["K1"]["biais"].__setitem__(1, 0.9417),
               "statut": lambda o: o["statut"].__setitem__("K1", "survit"),
               "clés": lambda o: (o["archive"].__setitem__("V1", JEU["vraies"]["V1"]), o["statut"].__setitem__("V1", B65.STATUT_K1)),
               "version": lambda o: o.__setitem__("version", "heritage-depart-boucle-reelle-v64"),
               "génération": lambda o: o.__setitem__("generation", 1)}
        for nom, f in cas.items():
            with self.subTest(nom):
                self.setUp()
                sha = self._reecrire(f)
                with self.assertRaises(B.HeritageDepartRefuse):
                    B65.lire_heritage_depart(self.chemin, sha, JEU)

    def test_garde_19(self):
        t = _texte_avec(JEU)
        self.assertEqual(B65.lire_jeu_plante(t, B65.empreinte_du_bloc(t))[0], JEU)
        with self.assertRaisesRegex(B.JeuPlanteRefuse, "empreinte"):
            B65.lire_jeu_plante(t, "0" * 64)
        k1 = JEU["archive_de_depart"]["K1"]
        cas = {"incomplet": lambda j: j["fausses"].pop("F4"),
               "hors grammaire": lambda j: j["vraies"].__setitem__("V3", {"type": "logistique", "weights": [[0.0, 0.0]] * 3}),
               "mélange avec une loi non fixe": lambda j: j["fausses"].__setitem__("F2", {"type": "melange", "composantes": [k1, JEU["vraies"]["V1"]], "poids": [0.5, 0.5]}),
               "composition": lambda j: j["fausses"].__setitem__("F4", {"type": "transformee", "base": k1, "puissance": 1.2,
                                                                        "melange_aveugle": {"lambda": 0.2, "probas": [1.0, 1.0, 1.0]}}),
               "loi inconnue": lambda j: j["fausses"].__setitem__("F1", MONDE["fausses"]["S-F2"])}
        for nom, f in cas.items():
            with self.subTest(nom):
                j = copy.deepcopy(JEU)
                f(j)
                tt = _texte_avec(j)
                with self.assertRaises(B.JeuPlanteRefuse):
                    B65.lire_jeu_plante(tt, B65.empreinte_du_bloc(tt))


# --- plan gelé, texte scellé ----------------------------------------------------------------------------------------------------


PLAN_SAIN = {"generations": "2", "cartes_par_proposeur": "6", "m_e_bh": "22", "bras": "reel_seul", "d9": "mecanique",
             "plafond_modeles_usd": "40", "plafond_kimi_usd": "33", "plafond_argon_usd": "7", "plafond_machine_usd": "5",
             "go": "GO-2026-11-08-02", "go_montant_usd": "45", "duree_h": "72", "configuration_sha256": "a" * 64,
             "monde_sha256": LANCEUR.MONDE_SHA256, "jeu_plante_sha256": B65.empreinte_du_bloc(_texte_avec(JEU)),
             "heritage_depart_sha256": "b" * 64}


def _plan(**chg):
    p = dict(PLAN_SAIN, **chg)
    return LANCEUR.DEBUT_PLAN + "\n" + "\n".join(f"{k}: {v}" for k, v in p.items() if v is not None) + "\n" + LANCEUR.FIN_PLAN


def _ecrire_texte(dossier, nom="preenregistrement-boucle-reelle-organisme-v1-v1.md", plan=None, jeu=JEU, sceau=True, en_plus="",
                  empreintes=None):
    gel = empreintes or {r: sha256_fichier(os.path.join(RACINE, r)) for r in LANCEUR.FICHIERS_GELES}
    t = ("# préenregistrement (essai)\n\n" + LANCEUR.DEBUT_EMPREINTES + "\n" + "\n".join(f"{h}  {r}" for r, h in sorted(gel.items()))
         + "\n" + LANCEUR.FIN_EMPREINTES + "\n\n" + (plan or _plan()) + "\n\n" + B65.texte_du_bloc(jeu) + "\n" + en_plus)
    chemin = os.path.join(dossier, nom)
    if sceau:
        ecrire_scelle(chemin, t)
    else:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(t)
    return chemin


class PlanEtTexte(unittest.TestCase):
    def test_plan_sain(self):
        p = LANCEUR.lire_plan(_plan())
        self.assertEqual((p["plafond_modeles_usd"], p["plafond_kimi_usd"], p["plafond_argon_usd"], p["plafond_machine_usd"]), (40.0, 33.0, 7.0, 5.0))
        self.assertEqual(LANCEUR.lire_plan(_plan(go="GO-2026-11-10-10"))["go"], "GO-2026-11-10-10")

    def test_plan_artefacts(self):
        cas = {"bras": dict(bras="reel_et_references"), "générations": dict(generations="3"), "m": dict(m_e_bh="19"),
               "parts": dict(plafond_kimi_usd="34"), "GO": dict(go_montant_usd="40"), "durée": dict(duree_h="24"),
               "clé manquante": dict(go=None), "empreinte": dict(jeu_plante_sha256="xyz"),
               "machine nulle": dict(plafond_machine_usd="0", go_montant_usd="40"),
               "montants négatifs": dict(plafond_kimi_usd="-1", plafond_argon_usd="-1", plafond_modeles_usd="-2", plafond_machine_usd="2",
                                         go_montant_usd="0"),
               "go mal formé": dict(go="GO-2026-11-08-2")}
        for nom, chg in cas.items():
            with self.subTest(nom), self.assertRaises(LANCEUR.PreenregistrementRefuse):
                LANCEUR.lire_plan(_plan(**chg))

    def test_texte_sain(self):
        d = tempfile.mkdtemp(prefix="prereg-v66-")
        e, sha, gel, plan, jeu = LANCEUR.lire_preenregistrement(_ecrire_texte(d), d)
        self.assertGreaterEqual(e, 2 ** 64)
        self.assertEqual(jeu, JEU)
        self.assertEqual(set(gel), set(LANCEUR.FICHIERS_GELES))

    def test_texte_artefacts(self):
        tout = {r: sha256_fichier(os.path.join(RACINE, r)) for r in LANCEUR.FICHIERS_GELES}
        cas = {"brouillon": dict(nom="preenregistrement-boucle-reelle-organisme-v1-brouillon2.md"),
               "non scellé": dict(sceau=False), "marqueur": dict(en_plus="<<BLOC-V66>>\n"),
               "code différent": dict(empreintes=dict(tout, **{"pole/boucle_reelle_v66.py": "0" * 64})),
               "fermeture incomplète": dict(empreintes={r: h for r, h in tout.items() if r != "pole/registre_go_v66.py"})}
        for k, kw in cas.items():
            with self.subTest(k):
                d = tempfile.mkdtemp(prefix="prereg-art-v66-")
                with self.assertRaises(LANCEUR.PreenregistrementRefuse):
                    LANCEUR.lire_preenregistrement(_ecrire_texte(d, **kw), d)
        d = tempfile.mkdtemp(prefix="prereg-art-v66-")
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):  # bon nom, mauvais dossier
            LANCEUR.lire_preenregistrement(_ecrire_texte(d), tempfile.mkdtemp())


# --- configuration v6 (CLV65-10) -------------------------------------------------------------------------------------------------


CONF_V6 = os.path.join(RACINE, "exemples", "configuration-boucle-reelle-v6.json")


def _dossier_de_configuration(dossier, retouche=None):
    """Un dossier de course complet pour les essais : configuration v6 dont pièces et commandes v6 sont des doublures (leurs
    empreintes réécrites), aux mêmes chemins relatifs ; rend le chemin de la configuration."""
    with open(CONF_V6, encoding="utf-8") as f:
        conf = json.load(f)
    for nom, piece in conf["pieces"].items():
        p = os.path.join(dossier, piece["chemin"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(f"pièce doublure {nom}\n")
        piece["sha256"] = sha256_fichier(p)
    for n in LANCEUR.COMMANDES_V6:
        e = conf["boucle_reelle_v66"]["commandes_v6"][n]
        p = os.path.join(dossier, e["chemin"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(f"# doublure de la commande {n}\n")
        e["sha256"] = sha256_fichier(p)
    if retouche:
        retouche(conf)
    chemin = os.path.join(dossier, "configuration-boucle-reelle-v6.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(conf, f, ensure_ascii=False, indent=1)
    return chemin


class ConfigurationV6(unittest.TestCase):
    PLAN = LANCEUR.lire_plan(_plan())

    def test_fichier_v6_chemins_relatifs_et_empreintes_nommees(self):
        with open(CONF_V6, encoding="utf-8") as f:
            conf = json.load(f)
        s = conf["boucle_reelle_v66"]
        self.assertEqual(set(s), LANCEUR.CLES_SECTION)
        c = s["commandes_v6"]
        self.assertEqual(c["kimi"]["sha256"], "889309305aeb37de9801c2f40c31769fd268abded1ac61ea94196fd0d51195ae")
        self.assertEqual(c["argon"]["sha256"], "5eae1a0468430e243c3c4e099b3969f949f62add688531aafdd7f0f44e036e55")
        self.assertEqual(c["registre_depense_cumulee"]["sha256"], "8ba92066b358ffb8206dea9e70251388c30620484fab1ac578778d9f21e578ff")
        self.assertEqual(c["source"]["commit"], "12f9e0e38f2cf7adb61a9c3ddf0ee4c5c66556d9")
        for n in LANCEUR.COMMANDES_V6:
            self.assertFalse(os.path.isabs(c[n]["chemin"]))
        for p in conf["pieces"].values():
            self.assertFalse(os.path.isabs(p["chemin"]))
        self.assertEqual((conf["budget"]["plafond_usd"], s["parts_usd"], s["plafond_machine_usd"]), (40.0, {"kimi": 33.0, "argon": 7.0}, 5.0))
        self.assertNotIn("/home/", json.dumps(conf))

    def test_sain_dossier_complet(self):
        d = tempfile.mkdtemp(prefix="conf-v66-")
        chemin = _dossier_de_configuration(d)
        from pole import configuration_v56 as cfg
        conf = cfg.lire_configuration_v56(chemin)
        s, res = LANCEUR.verifier_configuration_v66(conf, self.PLAN, d)
        self.assertEqual(s["parts_usd"], {"kimi": 33.0, "argon": 7.0})
        k = res["fournisseurs"]["kimi"]["commande"]
        self.assertIn(os.path.realpath(os.path.join(d, "commandes-v6", "commande_kimi_v6.py")), k)
        self.assertEqual(conf["fournisseurs"]["kimi"]["commande"][3], "commandes-v6/commande_kimi_v6.py")  # la configuration lue n'est pas touchée

    def test_artefacts(self):
        from pole import configuration_v56 as cfg
        dehors = tempfile.mkdtemp(prefix="dehors-v66-")
        with open(os.path.join(dehors, "x.py"), "w") as f:
            f.write("x\n")
        cas = {"commande altérée": None,
               "chemin absolu": lambda c: c["boucle_reelle_v66"]["commandes_v6"]["kimi"].__setitem__("chemin", "/usr/bin/true"),
               "chemin avec ..": lambda c: c["boucle_reelle_v66"]["commandes_v6"]["argon"].__setitem__("chemin", "../dehors/x.py"),
               "chemin avec .. qui reste dedans": lambda c: c["boucle_reelle_v66"]["commandes_v6"]["registre_depense_cumulee"].__setitem__(
                   "chemin", "commandes-v6/../commandes-v6/registre_depense_cumulee_v1.py"),
               "chemin absolu qui reste dedans": "absolu-dedans",
               "pièce absolue": lambda c: c["pieces"]["consigne_juge"].__setitem__("chemin", "/etc/hostname"),
               "part": lambda c: c["boucle_reelle_v66"]["parts_usd"].__setitem__("kimi", 34.0),
               "plafond": lambda c: c["budget"].__setitem__("plafond_usd", 50.0),
               "machine": lambda c: c["boucle_reelle_v66"].__setitem__("plafond_machine_usd", 10.0),
               "GO dans la configuration": lambda c: c["boucle_reelle_v66"].__setitem__("go", "GO-2026-11-08-02"),
               "commande lancée": lambda c: c["fournisseurs"]["argon"].__setitem__("commande", ["/bin/true"])}
        for nom, f in cas.items():
            with self.subTest(nom):
                d = tempfile.mkdtemp(prefix="conf-art-v66-")
                if f == "absolu-dedans":
                    f = (lambda dd: lambda c: c["boucle_reelle_v66"]["commandes_v6"]["registre_depense_cumulee"].__setitem__(
                        "chemin", os.path.join(os.path.realpath(dd), "commandes-v6", "registre_depense_cumulee_v1.py")))(d)
                chemin = _dossier_de_configuration(d, f)
                if f is None:
                    with open(os.path.join(d, "commandes-v6", "commande_kimi_v6.py"), "a", encoding="utf-8") as x:
                        x.write("# altérée\n")
                with self.assertRaises((LANCEUR.ConfigurationRefusee, cfg.ConfigurationRefusee)):
                    LANCEUR.verifier_configuration_v66(cfg.lire_configuration_v56(chemin) if nom != "pièce absolue" else json.load(open(chemin)),
                                                       self.PLAN, d)
        d = tempfile.mkdtemp(prefix="conf-lien-v66-")
        chemin = _dossier_de_configuration(d)
        cible = os.path.join(d, "commandes-v6", "commande_kimi_v6.py")
        shutil.move(cible, os.path.join(dehors, "k.py"))
        os.symlink(os.path.join(dehors, "k.py"), cible)  # lien qui sort du dossier
        with self.assertRaisesRegex(LANCEUR.ConfigurationRefusee, "hors du dossier"):
            LANCEUR.verifier_configuration_v66(cfg.lire_configuration_v56(chemin), self.PLAN, d)


# --- garde 22 (CLV65-09) et bac à sable (CLV65-06) ---------------------------------------------------------------------------------


DESCRIPTION_SAINE = {"nom": "bac-a-sable-bwrap", "factice": False, "demande": "reel", "sonde": "OK",
                     "identite_du_script_sur_l_hote": {"utilisateur_dedie": {"uid": 64097, "gid": 64097, "nom": None}}}


class Machine(unittest.TestCase):
    def test_garde_22_avant_la_sonde(self):
        self.assertTrue(LANCEUR.exiger_machine(64097, (0, 9), 0))
        self.assertTrue(LANCEUR.exiger_machine(64097, (1, 0), 0))
        for u, v, e in ((64097, None, 0), (64097, (0, 8), 0), (0, (0, 9), 0), (None, (0, 9), 0), (64097, (0, 9), 1000)):
            with self.subTest(u=u, v=v, e=e), self.assertRaises(LANCEUR.MachineRefusee):
                LANCEUR.exiger_machine(u, v, e)

    def test_garde_22_apres_la_sonde(self):
        self.assertTrue(LANCEUR.exiger_utilisateur_du_bac(DESCRIPTION_SAINE, 64097))
        cas = {"factice": dict(DESCRIPTION_SAINE, factice=True), "demande factice": dict(DESCRIPTION_SAINE, demande="factice"),
               "sans sonde": {k: v for k, v in DESCRIPTION_SAINE.items() if k != "sonde"},
               "sans utilisateur dédié": dict(DESCRIPTION_SAINE, identite_du_script_sur_l_hote={"utilisateur_dedie": None}),
               "autre utilisateur": dict(DESCRIPTION_SAINE, identite_du_script_sur_l_hote={"utilisateur_dedie": {"uid": 1000}})}
        for nom, d in cas.items():
            with self.subTest(nom), self.assertRaises(LANCEUR.MachineRefusee):
                LANCEUR.exiger_utilisateur_du_bac(d, 64097)

    def test_version_bwrap(self):
        ok = lambda *a, **k: subprocess.CompletedProcess(a, 0, "bubblewrap 0.9.0\n", "")  # noqa: E731
        self.assertEqual(LANCEUR.version_bwrap(ok, lambda n: "/usr/bin/bwrap"), (0, 9))
        self.assertIsNone(LANCEUR.version_bwrap(ok, lambda n: None))
        self.assertIsNone(LANCEUR.version_bwrap(lambda *a, **k: subprocess.CompletedProcess(a, 0, "?", ""), lambda n: "/x"))

    def test_artefact_bwrap_absent_refus_code_2_sans_repli_partout(self):
        """CLV65-06 : joué même sur une machine qui a `bwrap` (`WHICH` remplacée) ; aucun repli sur l'exécuteur factice."""
        sortie = tempfile.mkdtemp() + "/x"
        which = mock.Mock(return_value=None)
        with mock.patch.object(LANCEUR, "WHICH", which):
            code, _, err = _lancer(LANCEUR, [sortie, "--a-blanc", "--graine", "1", "--bac", "reel", "--utilisateur-bac", "64097"])
        which.assert_called_with("bwrap")
        self.assertEqual(code, 2)
        self.assertIn("BacASableIndisponible", err)
        self.assertIn("aucun repli", err)
        self.assertFalse(os.path.exists(sortie))

    @unittest.skipIf(BAC_NON_JOUE, "vrai bac à sable : non joué sur cette machine (bwrap absent ou POLE_ESSAI_BAC_REEL_NON_JOUE=1)")
    def test_sain_bac_reel_essai_a_blanc(self):
        sortie = tempfile.mkdtemp() + "/x"
        argv = [sortie, "--a-blanc", "--graine", "7", "--bac", "reel"]
        if os.geteuid() == 0:
            argv += ["--utilisateur-bac", os.environ.get("POLE_UTILISATEUR_BAC", "64097")]
        code, out, err = _lancer(LANCEUR, argv)
        self.assertEqual(code, 0, err)
        with open(os.path.join(sortie, LANCEUR.SORTIE), encoding="utf-8") as f:
            r = json.load(f)["releve"]
        self.assertTrue(all(not e["factice"] for e in r["etages"]))


# --- branche réelle du lanceur (CLV65-04 : X05, X06 ; CLV65-07 ; CLV65-09) --------------------------------------------------------


def _registre_sain(dossier, montant="45 USD"):
    """Registre d'essai : GO-2026-11-08-02 (`montant`), GO-2026-11-10-10 (enveloppe, part « organisme » 45 USD), et un autre GO
    qui porte une ligne d'extension (que la lecture v53 refusait : CLV65-07)."""
    a, e = datetime.date.today() - datetime.timedelta(days=2), datetime.date.today() + datetime.timedelta(days=20)
    p = os.path.join(dossier, "go.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("| id | accordé le | type | périmètre | plafond | échéance | accordé par | référence |\n|---|---|---|---|---|---|---|---|\n"
                f"| GO-2026-10-24-07 | {a} | calcul | préparatifs (essai) | 200 USD | {e} | Lazar | essai |\n"
                f"| GO-2026-10-24-07 | {a} | calcul | extension au pilote (essai) | 40 USD | {e} | Lazar | essai |\n"
                f"| GO-2026-11-08-02 | {a} | calcul | course (essai) | {montant} | {e} | Lazar | essai |\n"
                f"| GO-2026-11-10-10 | {a} | calcul | enveloppe (essai) | 120 USD (organisme 45, Bailey 75 ; aucun report) | {e} | Lazar | essai |\n")
    return p


class BrancheReelle(unittest.TestCase):
    """Le mode réel de `principal`, dossier des textes remplacé (`DOSSIER_PREREG`), texte d'essai scellé gelant le code présent,
    configuration v6 à doublures, héritage de départ de l'essai, registre d'essai ; aucun appel, aucune porte posée."""

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="reel-v66-")
        cls.prereg = os.path.join(cls.d, "prereg")
        os.makedirs(cls.prereg)
        cls.conf_dir = os.path.join(cls.d, "conf")
        os.makedirs(cls.conf_dir)
        cls.conf = _dossier_de_configuration(cls.conf_dir)
        cls.depart = os.path.join(cls.d, "depart")
        os.makedirs(cls.depart)
        sha_dep = B65.ecrire_heritage_depart(cls.depart, JEU)
        cls.heritage = os.path.join(cls.depart, B65.NOM_HERITAGE_DEPART)
        cls.registre = _registre_sain(cls.d)
        cls.texte = _ecrire_texte(cls.prereg, plan=_plan(configuration_sha256=sha256_fichier(cls.conf), heritage_depart_sha256=sha_dep))

    def lancer(self, *en_plus, sans=(), **remplace):
        v = {"--preenregistrement": self.texte, "--heritage-depart": self.heritage, "--configuration": self.conf, "--moteur": "reel",
             "--registre-go": self.registre, "--go": "GO-2026-11-08-02", "--bac": "reel", "--utilisateur-bac": "64097"}
        v.update({k.replace("_", "-") if k.startswith("--") else "--" + k.replace("_", "-"): x for k, x in remplace.items()})
        argv = [tempfile.mkdtemp() + "/sortie"]
        for k, x in v.items():
            if k not in sans:
                argv += [k, x]
        if "--confirmer-moteur-reel" not in sans:
            argv.append("--confirmer-moteur-reel")
        argv += list(en_plus)
        with mock.patch.object(LANCEUR, "DOSSIER_PREREG", self.prereg), mock.patch.object(LANCEUR, "WHICH", lambda nom: None):
            code, out, err = _lancer(LANCEUR, argv)
        self.assertFalse(os.path.exists(argv[0]), "aucune sortie ne doit être écrite par un refus")
        return code, err

    def test_refus_nommes(self):
        autre_conf = _dossier_de_configuration(tempfile.mkdtemp(prefix="conf2-v66-"),
                                               lambda c: c.__setitem__("_lisez_moi", "autre"))
        autre_dep = tempfile.mkdtemp(prefix="dep2-v66-")
        ecrire_json_scelle(os.path.join(autre_dep, "h.json"), {"version": "x"})
        cas = {"sans --go": (dict(sans=("--go",)), "GoAbsent"),
               "autre GO que celui du texte (présent au registre)": (dict(go="GO-2026-11-10-10"), "celui du texte scellé"),
               "registre à 40 USD": (dict(registre_go=_registre_sain(tempfile.mkdtemp(), "40 USD")), "pas exactement"),
               "registre absent": (dict(registre_go=os.path.join(tempfile.mkdtemp(), "go.md")), "absent"),
               "configuration d'une autre empreinte": (dict(configuration=autre_conf), "ConfigurationRefusee"),
               "bac factice": (dict(bac="factice"), "bac « reel » exigé"),
               "option de plan": ((["--plafond-usd", "10"], {}), "options refusées"),
               "graine": ((["--graine", "3"], {}), "options refusées"),
               "sans confirmation": (dict(sans=("--confirmer-moteur-reel",)), "confirmer"),
               "héritage d'une autre empreinte": (dict(heritage_depart=os.path.join(autre_dep, "h.json")), "HeritageDepartRefuse"),
               "machine sans bwrap": ({}, "MachineRefusee")}
        for nom, (kw, motif) in cas.items():
            with self.subTest(nom):
                if isinstance(kw, tuple):
                    code, err = self.lancer(*kw[0], **kw[1])
                else:
                    code, err = self.lancer(**kw)
                self.assertEqual(code, 2, err)
                self.assertIn(motif, err)

    def test_ordre_configuration_puis_garde_17_puis_garde_22(self):
        autre_dep = tempfile.mkdtemp(prefix="dep3-v66-")
        ecrire_json_scelle(os.path.join(autre_dep, "h.json"), {"version": "x"})
        code, err = self.lancer(heritage_depart=os.path.join(autre_dep, "h.json"))  # garde 17 avant la garde 22 (bwrap absent)
        self.assertIn("HeritageDepartRefuse", err)
        autre_conf = _dossier_de_configuration(tempfile.mkdtemp(prefix="conf3-v66-"), lambda c: c.__setitem__("_lisez_moi", "autre"))
        code, err = self.lancer(heritage_depart=os.path.join(autre_dep, "h.json"), configuration=autre_conf)
        self.assertIn("ConfigurationRefusee", err)  # la configuration avant la garde 17

    def test_garde_22_cablee_identite_du_bac_puis_garde_15_avant_les_portes(self):
        appels_roles = []

        def roles_reels(*a, **k):
            appels_roles.append(a)
            raise AssertionError("portes posées avant les gardes")

        def bac(description):
            return lambda b, u, which=None: (None, lambda: (None, description), description)
        sentinelle = RuntimeError("SENTINELLE-GARDE-15")
        with mock.patch.object(LANCEUR, "version_bwrap", lambda *a, **k: (0, 9)), \
                mock.patch.object(LANCEUR.L64, "roles_reels", roles_reels), \
                mock.patch.object(LANCEUR.L64, "exiger_machine_jetable_reel", mock.Mock(side_effect=sentinelle)):
            with mock.patch.object(LANCEUR, "preparer_bac_v66", bac(dict(DESCRIPTION_SAINE, identite_du_script_sur_l_hote={"utilisateur_dedie": {"uid": 12345}}))), \
                    mock.patch.object(os, "geteuid", lambda: 0):
                code, err = self.lancer()
            self.assertEqual(code, 2)
            self.assertIn("identité du bac", err)
            with mock.patch.object(LANCEUR, "preparer_bac_v66", bac(DESCRIPTION_SAINE)), mock.patch.object(os, "geteuid", lambda: 0):
                code, err = self.lancer()
            self.assertEqual(code, 2)
            self.assertIn("SENTINELLE-GARDE-15", err)
            with mock.patch.object(LANCEUR, "preparer_bac_v66", bac(DESCRIPTION_SAINE)), mock.patch.object(os, "geteuid", lambda: 1000):
                code, err = self.lancer()
            self.assertIn("superutilisateur", err)
        self.assertEqual(appels_roles, [])

    def test_verifier_seulement_roles_en_dernier_jetons_branches(self):
        """La branche réelle jusqu'à `--verifier-seulement`, gardes 22 et 15 remplacées par des doublures (aucun `bwrap` ici) et
        rôles réels remplacés par les doublures à blanc : rôles construits en dernier, sans porte (`transmettre` faux), jetons
        relevés sur chaque adaptateur (CLV65-08)."""
        appels = []

        def roles_reels(conf, plan, base, sortie, transmettre=True):
            appels.append({"transmettre": transmettre, "commande_kimi": conf["fournisseurs"]["kimi"]["commande"][3]})
            p, e, r = _roles_a_blanc()
            return p, e, r, {"doublures": True}
        with mock.patch.object(LANCEUR, "version_bwrap", lambda *a, **k: (0, 9)), mock.patch.object(os, "geteuid", lambda: 0), \
                mock.patch.object(LANCEUR, "preparer_bac_v66", lambda b, u, which=None: (None, lambda: (None, DESCRIPTION_SAINE), DESCRIPTION_SAINE)), \
                mock.patch.object(LANCEUR.L64, "exiger_machine_jetable_reel", lambda env, conf: ()), \
                mock.patch.object(LANCEUR.L64, "roles_reels", roles_reels), \
                mock.patch.object(B.ReleveDeJetons, "instrumenter", autospec=True, side_effect=lambda self, ad, relais: appels.append(relais) or ad):
            code, err = self.lancer("--verifier-seulement")
        self.assertEqual(code, 0, err)
        self.assertEqual(appels[0], {"transmettre": False, "commande_kimi": os.path.realpath(os.path.join(self.conf_dir, "commandes-v6", "commande_kimi_v6.py"))})
        self.assertEqual(sorted(appels[1:]), ["argon", "argon", "kimi", "kimi"])  # deux proposeurs, expérimentateur et vérificateur

    def test_go_enveloppe_lu_par_le_lanceur(self):
        """Texte qui cite GO-2026-11-10-10 : la part « organisme » (45 USD) est lue ; la chaîne passe le GO et s'arrête à la garde 22."""
        prereg = tempfile.mkdtemp(prefix="prereg-env-v66-")
        texte = _ecrire_texte(prereg, plan=_plan(go="GO-2026-11-10-10", configuration_sha256=sha256_fichier(self.conf),
                                                 heritage_depart_sha256=sha256_fichier(self.heritage)))
        argv = [tempfile.mkdtemp() + "/s", "--preenregistrement", texte, "--heritage-depart", self.heritage, "--configuration", self.conf,
                "--moteur", "reel", "--confirmer-moteur-reel", "--registre-go", self.registre, "--go", "GO-2026-11-10-10", "--bac", "reel",
                "--utilisateur-bac", "64097"]
        with mock.patch.object(LANCEUR, "DOSSIER_PREREG", prereg), mock.patch.object(LANCEUR, "WHICH", lambda nom: None):
            code, _, err = _lancer(LANCEUR, argv)
        self.assertEqual(code, 2)
        self.assertIn("MachineRefusee", err)

    @unittest.skipIf(not os.path.isfile("/home/user/controle-ia-travail/registres/go.md"), "vrai registre absent : non joué")
    def test_vrai_registre_lu(self):
        """CLV65-07 : le vrai `registres/go.md` (lecture seule) passe la lecture du GO ; la chaîne s'arrête ensuite à la garde 22
        (bwrap absent), jamais au registre ; au-delà du 30 novembre 2026 le GO est échu (refus nommé)."""
        code, err = self.lancer(registre_go="/home/user/controle-ia-travail/registres/go.md")
        if datetime.date.today() <= datetime.date(2026, 11, 30):
            self.assertIn("MachineRefusee", err)
        else:
            self.assertIn("validité", err)


# --- fermeture du code gelé -------------------------------------------------------------------------------------------------------


class Fermeture(unittest.TestCase):
    def test_bloc_gele_egal_a_la_fermeture_statique(self):
        t64 = _charger("essais_tour_ferme_v64_pour_v66", "essais/test_tour_ferme_v64.py")
        ferm, pile = set(), ["demonstrations/boucle_reelle_v66.py", "demonstrations/lire_boucle_reelle_v66.py"]
        while pile:
            x = pile.pop()
            if x not in ferm:
                ferm.add(x)
                pile += sorted(t64.imports_de(x) - ferm)
        ferm |= {"demonstrations/tour_ferme_v64.py"} | t64.fermeture_statique()  # lanceur v64 chargé par chemin
        self.assertEqual(sorted(ferm), sorted(LANCEUR.FICHIERS_GELES))


# --- mesures promises par le brouillon (CLV65-08) ---------------------------------------------------------------------------------


class Mesures(unittest.TestCase):
    def test_sain_mesures_au_releve(self):
        r = Course.releve()
        rl = r["recherche_loi_plantee"]
        self.assertEqual(rl["proposeurs"]["contextes_cherches"], 4)
        self.assertEqual(rl["proposeurs"]["touches"], [])
        e = rl["experimentateur_et_verificateur"]
        self.assertGreater(e["par_role"].get("experimentateur_test", 0), 0)
        self.assertGreater(e["par_role"].get("lecteur_test", 0), 0)
        self.assertEqual(e["touches_hors_loi_gelee"], [])
        self.assertGreater(e["touches_dans_la_loi_gelee"], 0)  # V1 (= L*) passe à l'étage : l'expérimentateur voit la loi gelée
        self.assertEqual(r["lignes_de_tranche_dans_les_contextes"]["communes"], [])
        self.assertEqual(r["lignes_de_tranche_dans_les_contextes"]["taches_comparees"], 2)
        for x in [c for c in r["cartes"] if c["gardien"] == "passe"] + [p for p in r["plantees"] if p["gardien"] == "passe"]:
            self.assertTrue(x["membre_dominant_final"] and x["empreinte_engagement"] and x["graines"])
        self.assertIn("non mesurés", r["jetons"]["source"])

    def test_consigne_sans_loi_gelee(self):
        loi = JEU["vraies"]["V1"]
        canon = json.dumps(loi, sort_keys=True, separators=(",", ":"))
        echappee = json.dumps(canon)[1:-1]
        for texte in (T.MARQUE_LOI + canon + " fin", json.dumps({"test": T.MARQUE_LOI + canon}, ensure_ascii=False),
                      json.dumps({"test": T.MARQUE_LOI + canon}, ensure_ascii=False) + "\nécho : LOI = '" + echappee + "'"):
            with self.subTest(texte[:30]):
                hors, dans = B.consigne_sans_loi_gelee(texte)
                self.assertEqual(T.chercher_loi_plantee(MONDE, hors, {}, "x"), [])
                self.assertTrue(T.chercher_loi_plantee(MONDE, dans, {}, "x"))
        fuite = json.dumps({"test": T.MARQUE_LOI + canon}, ensure_ascii=False) + f"\nindice : {loi['biais'][1]!r}"
        hors, _ = B.consigne_sans_loi_gelee(fuite)
        self.assertEqual(len(T.chercher_loi_plantee(MONDE, hors, {}, "x")), 1)

    def test_etage_mesure_artefact_fuite_vers_l_experimentateur(self):
        appels = []
        ad = type("Ad", (), {"depense": {}, "lancer": lambda self, *a, **k: appels.append(a) or "r"})()
        m = {"consignes_cherchees": 0, "par_role": {}, "touches_hors_loi_gelee": [], "touches_dans_la_loi_gelee": 0}
        e = B.EtageMesure(ad, MONDE, m)
        e.tache = "t"
        e.parts = {"kimi": 1.0}
        self.assertEqual(ad.parts, {"kimi": 1.0})
        self.assertIs(e.depense, ad.depense)
        loi = JEU["vraies"]["V1"]
        self.assertEqual(e.lancer("experimentateur_test", f"indice {loi['poids'][0][0]!r}", "d", 0.8, 1), "r")
        self.assertEqual(len(m["touches_hors_loi_gelee"]), 1)
        self.assertEqual((m["consignes_cherchees"], m["par_role"]), (1, {"experimentateur_test": 1}))
        self.assertEqual(len(appels), 1)

    def test_jetons(self):
        class AdCommande:
            def __init__(self, ligne):
                self.ligne = ligne

            def lire_derniere_ligne(self, octets):
                return json.loads(octets.decode()), None

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                self.lire_derniere_ligne(self.ligne)
                return "r"
        j = B.ReleveDeJetons()
        k = j.instrumenter(AdCommande(b'{"texte": "", "usage": {"prompt_tokens": 100, "completion_tokens": 20}}'), "kimi")
        a = j.instrumenter(AdCommande(b'{"usage": {"promptTokenCount": 50, "candidatesTokenCount": 5, "thoughtsTokenCount": 7}}'), "argon")
        sans = j.instrumenter(AdCommande(b'{"texte": ""}'), "argon")
        self.assertIs(j.instrumenter(k, "kimi"), k)  # une seule enveloppe par adaptateur
        for ad in (k, k, a, sans):
            self.assertEqual(ad.lancer("proposeur_ideation", "c", "d", 0.5, 1), "r")
        r = j.rendu()
        self.assertEqual(r["sommes_par_relais"]["kimi"], {"entree": 200, "sortie": 40, "appels_avec_usage": 2, "appels_sans_usage": 0})
        self.assertEqual(r["sommes_par_relais"]["argon"], {"entree": 50, "sortie": 12, "appels_avec_usage": 1, "appels_sans_usage": 1})

    def test_lignes_de_tranche_artefact(self):
        x = next(iter(T.lignes_de_tranche(MONDE, RACINE_GRAINES, B.tache_de(1))))
        r = B.lignes_de_tranche_servies(MONDE, RACINE_GRAINES, [B.tache_de(1)], {(round(x[0], 6), round(x[1], 6), x[2])})
        self.assertEqual(len(r["communes"]), 1)


# --- essai à blanc de bout en bout, programme de lecture -----------------------------------------------------------------------------


class EssaiABlanc(unittest.TestCase):
    def test_bout_en_bout_et_lecture(self):
        sortie = tempfile.mkdtemp(prefix="ab-v66-") + "/sortie"
        code, out, err = _lancer(LANCEUR, [sortie, "--a-blanc", "--graine", "20261110", "--bac", "factice"])
        self.assertEqual(code, 0, err)
        releve = os.path.join(sortie, LANCEUR.SORTIE)
        sha = sha256_fichier(releve)
        self.assertEqual(json.loads(out)["releve_sha256"], sha)
        lecture = sortie + "-lecture.json"
        code, o, e = _lancer(LECTEUR, [sortie, lecture, "--releve-sha256", sha])
        self.assertEqual(code, 0, e)
        with open(lecture, encoding="utf-8") as f:
            lu = json.load(f)
        self.assertEqual(lu["code"], "C1")
        self.assertFalse(lu["audits"]["A1"]["bac_reel_partout"])  # exécuteur factice déclaré : l'audit A1 le dit
        self.assertIn("exécuteur factice", lu["phrase"])
        self.assertIn("à blanc", lu["phrase"])
        self.assertEqual(_lancer(LECTEUR, [sortie, lecture, "--releve-sha256", sha])[0], 2)  # jamais d'écrasement
        self.assertEqual(_lancer(LECTEUR, [sortie, lecture + "2"])[0], 2)  # empreinte exigée
        self.assertEqual(_lancer(LECTEUR, [sortie, lecture + "3", "--releve-sha256", "0" * 64])[0], 2)  # autre empreinte
        code, o, e = _lancer(LECTEUR, [sortie, lecture + "4", "--releve-sha256", sha, "--sans-oracle"])
        self.assertEqual(code, 0, e)
        with open(lecture + "4", encoding="utf-8") as f:
            self.assertIn("oracle non lu", json.load(f)["phrase"])
        with open(releve, encoding="utf-8") as f:
            rapport = json.load(f)
        rapport["releve"]["monde_sha256"] = "0" * 64  # autre monde, sceau refait : refus
        os.remove(releve)
        os.remove(releve + ".sha256")
        sha2 = ecrire_json_scelle(releve, rapport)
        code, o, e = _lancer(LECTEUR, [sortie, lecture + "5", "--releve-sha256", sha2])
        self.assertEqual(code, 2)
        self.assertIn("monde", e)
        with open(releve, "a", encoding="utf-8") as f:
            f.write(" ")
        self.assertEqual(_lancer(LECTEUR, [sortie, lecture + "6", "--releve-sha256", sha256_fichier(releve)])[0], 2)  # sceau faux

    def test_dossier_non_vide_refuse(self):
        d = tempfile.mkdtemp()
        open(os.path.join(d, "x"), "w").close()
        self.assertEqual(_lancer(LANCEUR, [d, "--a-blanc", "--graine", "1", "--bac", "factice"])[0], 2)

    def test_arret_code_3_releve_partiel_scelle(self):
        sortie = tempfile.mkdtemp() + "/x"
        code, _, err = _lancer(LANCEUR, [sortie, "--a-blanc", "--graine", "3", "--bac", "factice", "--scenario-proposeur", "erreur"])
        self.assertEqual(code, 3)
        lecture = sortie + "-l.json"
        code, o, e = _lancer(LECTEUR, [sortie, lecture, "--sans-oracle", "--releve-sha256", sha256_fichier(os.path.join(sortie, LANCEUR.SORTIE))])
        self.assertEqual(code, 0, e)
        with open(lecture, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["code"], "C5")


if __name__ == "__main__":
    unittest.main()
