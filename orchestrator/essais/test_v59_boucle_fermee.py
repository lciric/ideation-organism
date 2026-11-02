"""Essais de la v59 — boucle fermée entre générations (`pole/boucle_fermee_v59.py`), mode à blanc (`pole/a_blanc_v59.py`),
proposeurs de référence de A4 (`pole/proposeurs_references_v59.py`), câblage de l'étage v5 dans la course, le tour et le
lanceur (`pole/course2_v59.py`, `pole/ideation_v59.py`, `demonstrations/ideation_v59.py`).

Hors ligne : aucun réseau, aucun modèle, aucune clé. Chaque garde : un cas sain et un artefact (R5). Le mode à blanc est joué
avec l'exécuteur factice **demandé explicitement** (aucune barrière) ; l'essai du vrai bac à sable exige `bwrap` (et, sous un
noyau superutilisateur, `setpriv` pour l'identité sans privilège 64097) : sans eux il **échoue**, sauf
`POLE_ESSAI_BAC_REEL_NON_JOUE=1`, qui le fait ignorer avec le motif « ESSAI RÉEL NON JOUÉ » (mécanisme de la v51, CL15-04).
Graines : `SeedSequence` dérivées par tâche (R9)."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides  # noqa: E402
from pole import a_blanc_v59 as A  # noqa: E402
from pole import boucle_fermee_v59 as bf  # noqa: E402
from pole import proposeurs_references_v59 as pr  # noqa: E402
from pole import tests_de_mort_v4 as v4  # noqa: E402
from pole.etage_entre_generations_v57 import NOM_SELECTION  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

GRAINE = 20261102
VARIABLE_NON_JOUE = "POLE_ESSAI_BAC_REEL_NON_JOUE"
UID_ESSAI = 64097


def exiger_essai_reel(test, motif):
    if os.environ.get(VARIABLE_NON_JOUE) == "1":
        test.skipTest(f"ESSAI RÉEL NON JOUÉ ({VARIABLE_NON_JOUE}=1, demande explicite) : {motif}")
    test.fail(f"essai réel impossible ici : {motif} (jamais ignoré en silence ; {VARIABLE_NON_JOUE}=1 pour le déclarer non joué)")


def dossier_neuf(cls):
    os.makedirs(aides.BASE, exist_ok=True)
    d = tempfile.mkdtemp(dir=aides.BASE)
    cls.addClassCleanup(shutil.rmtree, d, True)
    return d


def generations_du_journal(rapport, bras):
    return {l["generation"]: l for l in rapport["journal"] if l["evenement"] == "generation" and l["bras"] == bras}


def jouer(sortie, bac="factice", **kw):
    return A.jouer_a_blanc(sortie, racine_graines=GRAINE, racine_orchestrateur=RACINE, bac=bac, **kw)


# --- graines (R9) ---------------------------------------------------------------------------------------------------------------


class TestGrainesV59(unittest.TestCase):
    def test_cas_sain_derivee_de_la_tache(self):
        import numpy as np
        from pole.graines_v53 import cle_de_tache
        a, b = bf.graine_de_tache(GRAINE, "tache-a"), bf.graine_de_tache(GRAINE, "tache-b")
        self.assertNotEqual(a, b)
        attendu = int(np.random.SeedSequence(GRAINE, spawn_key=(cle_de_tache("tache-a"),)).generate_state(1, dtype=np.uint64)[0])
        self.assertEqual(a, attendu)
        self.assertEqual(a, bf.graine_de_tache(GRAINE, "tache-a"))
        self.assertNotEqual(a, bf.graine_de_tache(GRAINE + 1, "tache-a"))

    def test_artefacts_racine_ou_tache_refusees(self):
        for racine, tache in ((-1, "t"), (True, "t"), ("1", "t"), (1, ""), (1, None)):
            with self.subTest(racine=racine, tache=tache), self.assertRaises(bf.GraineRefusee):
                bf.graine_de_tache(racine, tache)


# --- vue servie aux proposeurs, survivantes -------------------------------------------------------------------------------------


class TestVueEtSurvivantes(unittest.TestCase):
    def test_vue_saine_lois_seules(self):
        h = {"generation_lue": 1, "archive": {"G1-VRAIE": {"type": "fixe", "probas": [1, 1, 1]}}, "retenues": ["G1-VRAIE"]}
        vue = bf.vue_pour_proposeur(h)
        self.assertEqual(vue, {"generation_lue": 1, "lois_retenues": [{"identifiant": "G1-VRAIE", "loi": {"type": "fixe",
                                                                                                         "probas": [1, 1, 1]}}]})

    def test_artefact_vue_avec_verdict_refusee(self):
        for mauvaise in ({"lois_retenues": [], "verdict": "survit"}, {"lois_retenues": [{"identifiant": "x", "loi": {},
                                                                                       "promue": True}]},
                         {"a": [{"b": {"log_richesse_max": 3.0}}]}, {"juge": {}}):
            with self.subTest(vue=mauvaise), self.assertRaises(bf.VueAvecVerdict):
                bf.exiger_vue_sans_verdict(mauvaise)
        for proposer in (pr.proposer_aleatoire, pr.proposer_recopie_melange):
            with self.subTest(proposeur=proposer.__name__), self.assertRaises(bf.VueAvecVerdict):
                proposer({"lois_retenues": [], "evaluations": {"x": {"promue": True}}}, 3, GRAINE, "t|generation=2")

    def test_survivantes_des_verdicts(self):
        n = v4.ETIQUETTE_NOYAU
        verdicts = {"a": {"etiquette": n, "verdict": "survit"}, "b": {"etiquette": n, "verdict": "éliminée"},
                    "c": {"etiquette": n, "verdict": "non concluant"}, "d": {"etiquette": "autre", "verdict": "survit"},
                    "e": {"etiquette": n, "verdict": "survit"}}
        self.assertEqual(bf.survivantes_des_verdicts(verdicts), ["a", "e"])
        with self.assertRaises(v4.VerdictInconnu):
            bf.survivantes_des_verdicts({"x": {"etiquette": n, "verdict": "peut-être"}})


# --- proposeurs de référence (A4) -----------------------------------------------------------------------------------------------


class TestProposeursReferencesV59(unittest.TestCase):
    VUE = {"generation_lue": 1, "lois_retenues": [{"identifiant": "G1-VRAIE", "loi": {"type": "softmax", "poids": [[1, 0], [0, 1],
                                                                                                                   [0, 0]],
                                                                                         "biais": [0, 0, 0]}}]}

    def test_aleatoire_graine_de_la_tache_grammaire_du_monde(self):
        a, _ = pr.proposer_aleatoire(self.VUE, 4, GRAINE, "x|generation=2")
        b, _ = pr.proposer_aleatoire(self.VUE, 4, GRAINE, "x|generation=2")
        c, _ = pr.proposer_aleatoire(self.VUE, 4, GRAINE, "y|generation=2")
        self.assertEqual(a, b)
        self.assertNotEqual([x["loi_predictive"] for x in a], [x["loi_predictive"] for x in c])
        for x in a:
            loi = x["loi_predictive"]
            self.assertEqual((loi["type"], len(loi["poids"]), len(loi["poids"][0])), ("softmax", pr.K, pr.DIM))
            self.assertTrue(all(abs(w) <= pr.BORNE for l in loi["poids"] for w in l))
            self.assertEqual(A.garder(x)[1], None)

    def test_recopie_melange_seulement_l_archive(self):
        cartes, motif = pr.proposer_recopie_melange(self.VUE, 6, GRAINE, "x|generation=2")
        self.assertIsNone(motif)
        loi = self.VUE["lois_retenues"][0]["loi"]
        self.assertEqual(cartes[0]["loi_predictive"], loi)  # copie sous un autre nom
        self.assertEqual(cartes[1]["loi_predictive"]["composantes"][0], loi)
        self.assertEqual(cartes[2]["loi_predictive"]["base"], loi)
        vide, motif = pr.proposer_recopie_melange({"generation_lue": None, "lois_retenues": []}, 6, GRAINE, "x|generation=1")
        self.assertEqual(vide, [])
        self.assertIn("héritage vide", motif)


# --- bac à sable : aucun repli silencieux ----------------------------------------------------------------------------------------


class TestBacASableV59(unittest.TestCase):
    def test_artefact_bac_reel_sans_bwrap_refuse(self):
        with self.assertRaises(A.BacASableIndisponible) as cm:
            A.choisir_executeur("reel", utilisateur_bac=UID_ESSAI, racine_travail="/inexistant", which=lambda nom: None)
        self.assertIn("aucun repli", str(cm.exception))
        for mauvais in (None, "", "auto"):
            with self.subTest(bac=mauvais), self.assertRaises(A.BacASableIndisponible):
                A.choisir_executeur(mauvais)

    def test_artefact_superutilisateur_sans_utilisateur_dedie(self):
        if os.geteuid() != 0:
            self.skipTest("noyau non superutilisateur : la garde de l'utilisateur dédié est sans objet ici (dit)")
        with self.assertRaises(A.BacASableIndisponible):
            A.choisir_executeur("reel", which=lambda nom: "/usr/bin/bwrap")

    def test_cas_sain_factice_explicite_et_dit(self):
        e, d = A.choisir_executeur("factice")
        self.assertTrue(d["factice"])
        self.assertIn("aucune barrière", d["demande"])

    def test_artefact_sortie_existante_ou_une_generation(self):
        d = tempfile.mkdtemp(dir=aides.BASE) if os.path.isdir(aides.BASE) else tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        with self.assertRaises(FileExistsError):
            jouer(d)
        with self.assertRaises(ValueError):
            jouer(os.path.join(d, "x"), generations=1)


# --- de bout en bout, exécuteur factice explicite ---------------------------------------------------------------------------------


class TestBoutEnBoutABlanc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = dossier_neuf(cls)
        cls.rapport = jouer(os.path.join(cls.d, "a-blanc"))
        cls.scripte = generations_du_journal(cls.rapport, "scripte")

    def test_generation_1_chaine_complete(self):
        g1 = self.scripte[1]
        self.assertEqual(list(g1["refusees_au_gardien"]), ["G1-MALFORMEE"])
        self.assertIn("statistique", g1["refusees_au_gardien"]["G1-MALFORMEE"])
        for ident in ("G1-VRAIE", "G1-INCONCLUSIVE", "G1-ELIMINEE"):
            self.assertIn(ident, g1["promues"])
        for ident in ("G1-FAUSSE-1", "G1-FAUSSE-3"):
            self.assertNotIn(ident, g1["promues"])
        self.assertEqual((g1["verdicts"]["G1-VRAIE"], g1["verdicts"]["G1-INCONCLUSIVE"], g1["verdicts"]["G1-ELIMINEE"]),
                         ("survit", "non concluant", "éliminée"))
        self.assertEqual(g1["retenues"], ["G1-VRAIE"])
        self.assertEqual(g1["comptes"]["survivantes"], 1)
        self.assertEqual(g1["comptes"]["promues_puis_survivantes"], 1)
        self.assertEqual(g1["heritage_lu"], None)

    def test_generation_2_lit_la_selection_scellee(self):
        g1, g2 = self.scripte[1], self.scripte[2]
        self.assertEqual(g2["heritage_lu"], g1["bilan_sha256"])
        self.assertEqual(g2["archive_lue"], ["G1-VRAIE"])  # seulement la retenue : ni l'inconclusive ni l'éliminée promues
        lus = [l for l in self.rapport["journal"] if l["evenement"] == "heritage-lu" and l["bras"] == "scripte" and l["generation"] == 2]
        self.assertEqual(lus[0]["retenues_lues"], ["G1-VRAIE"])
        self.assertEqual(g2["juge"]["G2-COPIE-G1-VRAIE"]["membres_d_archive"] > 0, True)
        self.assertNotIn("G2-COPIE-G1-VRAIE", g2["promues"])  # copie d'une loi retenue : le nul v8 la contient
        self.assertNotIn("G2-MELANGE-G1-VRAIE", g2["promues"])
        bilan = json.load(open(os.path.join(self.d, "a-blanc", "bras-scripte", "generation-2", bf.NOM_BILAN), encoding="utf-8"))
        self.assertEqual(bilan["heritage_lu"]["bilan_sha256"], g1["bilan_sha256"])

    def test_bras_de_reference_par_toute_la_chaine(self):
        for bras in ("aleatoire", "recopie_melange"):
            gens = generations_du_journal(self.rapport, bras)
            with self.subTest(bras=bras):
                self.assertEqual(sorted(gens), [1, 2])
                self.assertEqual(gens[2]["heritage_lu"], gens[1]["bilan_sha256"])
                self.assertEqual(gens[2]["archive_lue"], sorted(gens[1]["retenues"]))
                for cle in ("proposees", "refusees_au_gardien", "jugees", "promues", "testees", "survivantes", "retenues",
                            "promues_puis_survivantes", "sessions_experimentateur", "sessions_verificateur"):
                    self.assertIn(cle, gens[2]["comptes"])
        rm = generations_du_journal(self.rapport, "recopie_melange")
        self.assertIn("héritage vide", " ".join(rm[1]["comptes"]["motifs_du_proposeur"]))
        self.assertTrue(rm[2]["comptes"]["proposees"] > 0)
        al = generations_du_journal(self.rapport, "aleatoire")
        self.assertTrue(any(i.startswith("G2-ALEA-") for i in al[2]["juge"]))

    def test_selection_ne_retient_que_survit(self):
        for l in self.rapport["journal"]:
            if l["evenement"] == "generation":
                with self.subTest(bras=l["bras"], generation=l["generation"]):
                    self.assertEqual(sorted(l["retenues"]), sorted(i for i, v in l["verdicts"].items() if v == "survit"))

    def test_journal_scelle_graines_et_empreintes(self):
        chemin = os.path.join(self.d, "a-blanc", "journal-a-blanc-v59.json")
        self.assertTrue(verifier_scelle(chemin))
        self.assertEqual(sha256_fichier(chemin), self.rapport["sha256"])
        g1 = self.scripte[1]
        graines = json.load(open(os.path.join(self.d, "a-blanc", "bras-scripte", "generation-1", bf.NOM_BILAN),
                                 encoding="utf-8"))["graines"]
        t = "a-blanc-v59|bras=scripte|generation=1|carte=G1-VRAIE"
        self.assertEqual(graines["par_carte"]["G1-VRAIE"]["noyau"], bf.graine_de_tache(GRAINE, t + "|noyau"))
        self.assertEqual(graines["par_carte"]["G1-VRAIE"]["frais"],
                         bf.graine_de_tache(GRAINE, t + "|frais|" + g1["juge"]["G1-VRAIE"]["empreinte_engagement"]))
        depart = self.rapport["journal"][0]
        self.assertEqual((depart["bac"], depart["reseau"]), ("factice", "aucun"))


# --- lecture vérifiée de l'héritage (R5 : cas sain et artefacts) -------------------------------------------------------------------


class TestLectureHeritageV59(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = dossier_neuf(cls)
        cls.rapport = jouer(os.path.join(cls.d, "a-blanc"), bras=("scripte",))
        cls.g1 = generations_du_journal(cls.rapport, "scripte")[1]
        cls.source = os.path.join(cls.d, "a-blanc", "bras-scripte", "generation-1")

    def copie(self):
        d = tempfile.mkdtemp(dir=self.d)
        cible = os.path.join(d, "generation-1")
        shutil.copytree(self.source, cible, symlinks=True)
        return cible

    def selection(self, g):
        return os.path.join(g, bf.DOSSIER_ETAGE, NOM_SELECTION)

    def resceller(self, chemin, objet):
        os.remove(chemin)
        os.remove(chemin + ".sha256")
        return ecrire_json_scelle(chemin, objet)

    def test_cas_sain(self):
        h = bf.lire_heritage(self.copie(), self.g1["bilan_sha256"])
        self.assertEqual(h["retenues"], ["G1-VRAIE"])
        self.assertEqual(sorted(h["archive"]), ["G1-VRAIE"])
        self.assertEqual(h["empreintes_lues"]["selection"], self.g1["selection_sha256"])

    def test_artefact_selection_reecrite_avec_sceau(self):
        g = self.copie()
        sel = json.load(open(self.selection(g), encoding="utf-8"))
        self.resceller(self.selection(g), dict(sel, note="réécrite après coup"))
        self.assertTrue(verifier_scelle(self.selection(g)))  # le sceau compagnon est juste : seule l'empreinte consignée la trahit
        with self.assertRaises(bf.SelectionNonVerifiee) as cm:
            bf.lire_heritage(g, self.g1["bilan_sha256"])
        self.assertIn("empreinte", str(cm.exception))

    def test_artefact_selection_alteree_sans_sceau(self):
        g = self.copie()
        with open(self.selection(g), "a", encoding="utf-8") as f:
            f.write(" ")
        with self.assertRaises(bf.SelectionNonVerifiee):
            bf.lire_heritage(g, self.g1["bilan_sha256"])

    def test_artefact_bilan_d_une_autre_empreinte_ou_absent(self):
        g = self.copie()
        with self.assertRaises(bf.SelectionNonVerifiee):
            bf.lire_heritage(g, "0" * 64)
        with self.assertRaises(bf.SelectionNonVerifiee):
            bf.lire_heritage(g, None)
        os.remove(self.selection(g))
        with self.assertRaises(bf.SelectionNonVerifiee):
            bf.lire_heritage(g, self.g1["bilan_sha256"])

    def test_artefact_lien_symbolique(self):
        g = self.copie()
        vraie = self.selection(g) + ".vrai"
        os.rename(self.selection(g), vraie)
        os.symlink(vraie, self.selection(g))
        with self.assertRaises(bf.SelectionNonVerifiee) as cm:
            bf.lire_heritage(g, self.g1["bilan_sha256"])
        self.assertIn("régulier", str(cm.exception))

    def test_artefact_retenue_non_survivante_contre_verifiee(self):
        """Sélection et bilan réécrits de façon cohérente (sceaux et empreinte justes) pour retenir l'éliminée : la
        contre-vérification sur les verdicts scellés du noyau refuse."""
        g = self.copie()
        sel = json.load(open(self.selection(g), encoding="utf-8"))
        sha_sel = self.resceller(self.selection(g), dict(sel, retenues=sel["retenues"] + ["G1-ELIMINEE"]))
        chemin_bilan = os.path.join(g, bf.NOM_BILAN)
        bilan = json.load(open(chemin_bilan, encoding="utf-8"))
        bilan["selection"]["sha256"] = sha_sel
        cartes = json.load(open(os.path.join(g, bf.NOM_CARTES), encoding="utf-8"))["cartes"]
        bilan["archive"]["G1-ELIMINEE"] = [c for c in cartes if c["identifiant"] == "G1-ELIMINEE"][0]["loi_predictive"]
        sha_bilan = self.resceller(chemin_bilan, bilan)  # archive cohérente aussi : seule la contre-vérification la trahit
        with self.assertRaises(bf.HeritageRefuse) as cm:
            bf.lire_heritage(g, sha_bilan)
        self.assertIn("contre-vérification", str(cm.exception))


# --- le vrai bac à sable --------------------------------------------------------------------------------------------------------


class TestBacReelV59(unittest.TestCase):
    def test_a_blanc_dans_le_vrai_bac_a_sable(self):
        if not shutil.which("bwrap"):
            exiger_essai_reel(self, "bwrap absent de cette machine")
        uid = None
        if os.geteuid() == 0:
            ok = shutil.which("setpriv") and subprocess.run(
                ["setpriv", "--reuid", str(UID_ESSAI), "--regid", str(UID_ESSAI), "--clear-groups", "--no-new-privs", "--",
                 "/usr/bin/id", "-u"], capture_output=True, timeout=20).stdout.strip() == str(UID_ESSAI).encode()
            if not ok:
                exiger_essai_reel(self, f"noyau superutilisateur sans setpriv utilisable pour l'identité {UID_ESSAI}")
            uid = UID_ESSAI
        d = tempfile.mkdtemp(dir=aides.BASE) if os.path.isdir(aides.BASE) else tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reel = jouer(os.path.join(d, "reel"), bac="reel", utilisateur_bac=uid, bras=("scripte",))
        factice = jouer(os.path.join(d, "factice"), bras=("scripte",))
        etages = [l for l in reel["journal"] if l["evenement"] == "etage-tests-de-mort"]
        self.assertTrue(etages)
        self.assertTrue(all(l["bac_a_sable"] == "bwrap" and l["factice"] is False for l in etages))
        r, f = generations_du_journal(reel, "scripte"), generations_du_journal(factice, "scripte")
        for g in (1, 2):
            self.assertEqual((r[g]["promues"], r[g]["verdicts"], r[g]["retenues"]), (f[g]["promues"], f[g]["verdicts"], f[g]["retenues"]))
        self.assertEqual(r[1]["retenues"], ["G1-VRAIE"])
        self.assertEqual(r[1]["comptes"]["executions"], len(r[1]["promues"]))  # une exécution par carte promue, sous bwrap


# --- câblage de l'étage v5 : course, tour, lanceur --------------------------------------------------------------------------------


class TestCablageV59(unittest.TestCase):
    def test_tour_v59_appelle_l_etage_v5(self):
        from pole import ideation_v2 as idn
        from pole import ideation_v59 as i59
        from pole import tests_de_mort_v2 as v2
        from pole import tests_de_mort_v5 as v5
        self.assertIs(idn.executer_tests_de_mort, v2.executer_tests_de_mort)  # le tour v2, inchangé (R12)
        for nom in ("executer_tests_de_mort", "valider_champ_test", "extraire_prereg_court", "GABARIT_TEST",
                    "consigne_experimentateur_maximale", "ExecuteurBacASable"):
            with self.subTest(nom=nom):
                self.assertIs(getattr(i59.tour, nom), getattr(v5, nom))
        with self.assertRaises(v5.ChampTestInvalide):  # artefact : un champ sans bloc statistique est refusé par le tour v59
            i59.tour.valider_champ_test({"seuil": "au moins 0,3", "test": "x", "donnees": ["a.csv"]})
        self.assertIn("statistique", i59.tour.gabarit(tests_de_mort=True)["test_de_mort"])

    def test_lanceur_v59_appelle_la_course_v59(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("lanceur_ideation_v59_essai", os.path.join(RACINE, "demonstrations",
                                                                                                  "ideation_v59.py"))
        L = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(L)
        from pole import course2_v59 as c59
        self.assertIs(L.v8.c2.executer_course_v56, c59.executer_course_v59)
        self.assertIsNot(L.v8.c2.executer_course_v56, __import__("pole.course2_v56", fromlist=["x"]).executer_course_v56)

    def test_course_v59_sans_etage_refusee(self):
        from pole import course2_v59 as c59
        from pole.configuration_v53 import ConfigurationRefusee
        d = tempfile.mkdtemp(dir=aides.BASE) if os.path.isdir(aides.BASE) else tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        with self.assertRaises(ConfigurationRefusee) as cm:
            c59.executer_course_v59({}, os.path.join(d, "course"), {}, nombre_generations=2, go={}, etage=None)
        self.assertFalse(os.path.exists(os.path.join(d, "course")))
        self.assertIn("sélection scellée", str(cm.exception))

    def test_heritage_de_la_course_lit_la_selection(self):
        from pole import course2_v59 as c59
        d = tempfile.mkdtemp(dir=aides.BASE) if os.path.isdir(aides.BASE) else tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        os.makedirs(os.path.join(d, "etage"))
        ecrire_json_scelle(os.path.join(d, "etage", "fiches-validees.json"),
                           [{"identifiant_auteur": "f1", "nom": "Fiche une", "enonce": "énoncé un"},
                            {"identifiant_auteur": "f2", "nom": "Fiche deux", "enonce": "énoncé deux"}])
        from pole.etage_entre_generations_v57 import VERSION as V57
        sha = ecrire_json_scelle(os.path.join(d, "etage", NOM_SELECTION), {"version": V57, "retenues": ["f2"], "exclues": [],
                                                                            "regle": "essai"})
        texte = c59.heritage_depuis_selection(os.path.join(d, "etage"), sha)
        self.assertIn("Fiche deux", texte)
        self.assertNotIn("Fiche une", texte)
        with self.assertRaises(bf.SelectionNonVerifiee):
            c59.heritage_depuis_selection(os.path.join(d, "etage"), "1" * 64)


class TestR12V59(unittest.TestCase):
    def test_fichiers_scelles_inchanges(self):
        for rel in ("pole/tests_de_mort_v5.py", "pole/etage_entre_generations_v57.py", "pole/course2_v57.py", "pole/nul_v8.py",
                    "essais/test_v57b_cablage_verdict.py", "essais/test_v58_nul_v8.py"):
            self.assertTrue(verifier_scelle(os.path.join(RACINE, rel)), rel)


if __name__ == "__main__":
    unittest.main()
