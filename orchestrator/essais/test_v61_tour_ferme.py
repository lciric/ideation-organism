"""Essais de la v61 — cœur du tour fermé (`pole/tour_ferme_v61.py`) et lanceur (`demonstrations/tour_ferme_v61.py`) : gardes 5
à 10, 12 et 13 du préenregistrement (brouillon 2, section 7), décisions D7 à D9 en paramètres, fermeture du code gelé, course à
blanc de bout en bout (exécuteur factice ici ; le vrai bac est joué par `TestBacReelV61`, sauté sans `bwrap`). Cas sain et
artefact pour chaque garde (R5). Aucun réseau, aucun modèle."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import lecture_tour_ferme_v61 as L  # noqa: E402
from pole import tour_ferme_v61 as T  # noqa: E402
from pole.outils import ecrire_json_scelle  # noqa: E402

spec = importlib.util.spec_from_file_location("lanceur_tour_ferme_v61", os.path.join(RACINE, "demonstrations", "tour_ferme_v61.py"))
LANCEUR = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LANCEUR)
DEC = {"d7": "archive_du_bras_reel", "d8": "predicteur_connu", "d9": "mecanique"}
MONDE = A.charger_monde(RACINE)
PLAN = "\n".join(f"{k}: {v}" for k, v in {"generations_etage_1": 3, "generations_etage_2": 2, "cartes_par_proposeur": 6, "cartes_reference": 12,
                                            "m_e_bh_etage_1": 19, "m_e_bh_etage_2": 14, "plafond_etage_1_usd": 15, "plafond_etage_2_usd": 5,
                                            "duree_etage_1_h": 4, "duree_etage_2_h": 2, "d7": "archive_du_bras_reel", "d8": "predicteur_connu",
                                            "d9": "mecanique", "configuration_sha256": "a" * 64, "go": "GO-2026-11-03-01",
                                            "reserve_manifeste_sha256": "b" * 64, "ordre_des_bras": "reel, recopie_melange, aleatoire"}.items())
TEXTE_PLAN = LANCEUR.DEBUT_PLAN + "\n" + PLAN + "\n" + LANCEUR.FIN_PLAN


class Decisions(unittest.TestCase):
    def test_sain_et_artefacts(self):
        self.assertEqual(T.verifier_decisions(DEC), DEC)
        with self.assertRaises(T.TourRefuse):
            T.verifier_decisions(dict(DEC, d7="autre"))
        with self.assertRaises(T.TourRefuse):
            T.verifier_decisions(dict(DEC, d9="aiguilleur"))  # non écrit : refus avant tout appel
        with self.assertRaises(T.TourRefuse):
            T.verifier_decisions({k: v for k, v in DEC.items() if k != "d8"})


class Garde5Et13(unittest.TestCase):
    def test_plafond_de_depense(self):
        c = T.Compteur(0.05, 3600.0)
        c.ajouter(0.03, "proposeur")
        with self.assertRaises(T.ArretTour):
            c.ajouter(0.03, "proposeur")

    def test_duree(self):
        t = [0.0]
        c = T.Compteur(10.0, 100.0, horloge=lambda: t[0])
        c.ajouter(0.0, "x")
        t[0] = 101.0
        with self.assertRaises(T.ArretTour):
            c.verifier_duree()


class Garde6(unittest.TestCase):
    def test_plan_sain(self):
        p = LANCEUR.lire_plan(TEXTE_PLAN)
        self.assertEqual((p["decisions"], p["go"], p["m_e_bh_etage_1"]), (DEC, "GO-2026-11-03-01", 19))

    def test_plan_artefacts(self):
        for mauvais in (TEXTE_PLAN.replace("d7: archive_du_bras_reel", "d7: autre"), TEXTE_PLAN.replace("m_e_bh_etage_1: 19", "m_e_bh_etage_1: 11"),
                        TEXTE_PLAN.replace("go: GO-2026-11-03-01", "go: oui"), TEXTE_PLAN.replace("reel, recopie_melange, aleatoire", "aleatoire, reel, recopie_melange"),
                        TEXTE_PLAN.replace("configuration_sha256: " + "a" * 64, "configuration_sha256: x"), TEXTE_PLAN.replace("d9: mecanique\n", "")):
            with self.assertRaises(T.TourRefuse):  # PreenregistrementRefuse ou TourRefuse (décisions)
                LANCEUR.lire_plan(mauvais)

    def test_prereg_hors_chemin_brouillon_ou_non_scelle(self):
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(os.path.join(RACINE, "prereg", "preenregistrement-tour-ferme-v1-brouillon2.md"))
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        p = os.path.join(d, "preenregistrement-tour-ferme-v1-v1.md")
        open(p, "w").write("x")
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(p)  # hors de prereg/
        with self.assertRaises(LANCEUR.PreenregistrementRefuse):
            LANCEUR.lire_preenregistrement(os.path.join(RACINE, "prereg", "preenregistrement-tour-ferme-v1-v999.md"))  # absent


class Garde7(unittest.TestCase):
    def test_temoin_jamais_dans_archive_ni_vue(self):
        h = {"generation_lue": 1, "bilan_sha256": "a" * 64, "retenues": ["c1"], "archive": {"c1": MONDE["loi"]}, "empreintes_lues": {}}
        T.exiger_sans_temoin(h, {"W-abc"})
        h["archive"]["W-abc"] = MONDE["loi"]
        with self.assertRaises(T.TemoinRetenu):
            T.exiger_sans_temoin(h, {"W-abc"})

    def test_temoins_du_monde(self):
        t = T.temoins_du_monde(MONDE, 1, "x")
        self.assertEqual([n for n, _ in t], list(T.TEMOINS))
        self.assertTrue(all(c["identifiant"].startswith("W-") for _, c in t))
        self.assertNotIn("statistique", dict(t)["T-MAL"]["test_de_mort"])
        self.assertEqual(dict(t)["T-ELIM"]["test_de_mort"]["seuil"], "au moins 2,0")
        self.assertIsNone(A.garder(dict(t)["T-MAL"])[0])


class Garde8(unittest.TestCase):
    def test_gabarit(self):
        c, m = T.completer_carte({"enonce": "e", "loi_predictive": MONDE["loi"]}, "G1-x-01", "reel")
        self.assertIsNone(m)
        self.assertEqual(c["test_de_mort"], T.pr.TEST_DE_MORT)
        for art in ({"enonce": "e", "loi_predictive": MONDE["loi"], "test_de_mort": {"seuil": "au moins 0"}},
                    {"enonce": "e", "loi_predictive": MONDE["loi"], "statistique": "moyenne"}, {"enonce": "e"},
                    {"enonce": "x" * 401, "loi_predictive": MONDE["loi"]}, "texte"):
            c, m = T.completer_carte(art, "G1-x-02", "reel")
            self.assertIsNone(c, art)
            self.assertTrue(m)


class Garde9(unittest.TestCase):
    def test_familles(self):
        T.exiger_familles_separees(("e", "kimi"), ("v", "argon"))
        with self.assertRaises(T.FamillesNonSeparees):
            T.exiger_familles_separees(("e", "kimi"), ("v", "kimi"))
        with self.assertRaises(T.FamillesNonSeparees):
            T.exiger_familles_separees(("e", ""), ("v", "argon"))


class Garde10(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, True)
        tr = A.creer_tranche(self.d, MONDE, 5, "essai|garde10")
        self.ep = os.path.join(self.d, "tranche", "episodes.csv")
        self.vrai = T.statistique_hors_bac(MONDE["loi"], self.ep)

    def resume(self, valeur, verdict="survit"):
        return {"par_fiche": [{"statut": "testée", "identifiant_auteur": "c", "verdict_noyau": {"valeur_noyau": valeur, "verdict": verdict}}]}

    def test_concordance_desaccord_et_sans_objet(self):
        self.assertTrue(T.contre_calculer(self.resume(self.vrai), {"c": MONDE["loi"]}, self.ep)["c"]["ok"])
        r = T.contre_calculer(self.resume(self.vrai + 0.01), {"c": MONDE["loi"]}, self.ep)["c"]  # gains fabriqués
        self.assertFalse(r["ok"])
        r = T.contre_calculer(self.resume(None, "non concluant"), {"c": MONDE["loi"]}, self.ep)["c"]
        self.assertTrue(r["ok"] is True and r["sans_objet"])


class Garde12(unittest.TestCase):
    def test_lecture_etage_1_exigee(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        p = os.path.join(d, "lecture.json")
        sha = ecrire_json_scelle(p, {"etage_1": {"issue_etage_1": "tient"}})
        self.assertTrue(LANCEUR.lire_lecture_etage_1(p, sha))
        with self.assertRaises(T.TourRefuse):
            LANCEUR.lire_lecture_etage_1(p, "0" * 64)
        with self.assertRaises(T.TourRefuse):
            LANCEUR.lire_lecture_etage_1(None, None)
        p2 = os.path.join(d, "lecture2.json")
        sha2 = ecrire_json_scelle(p2, {"etage_1": {"issue_etage_1": "ne tient pas (T2)"}})
        with self.assertRaises(T.TourRefuse):
            LANCEUR.lire_lecture_etage_1(p2, sha2)


class Fermeture(unittest.TestCase):
    def test_fichiers_geles_couvrent_les_imports(self):
        code = ("import sys, importlib.util, os\n"
                f"sys.path.insert(0, {RACINE!r})\n"
                f"spec = importlib.util.spec_from_file_location('l', {os.path.join(RACINE, 'demonstrations', 'tour_ferme_v61.py')!r})\n"
                "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
                "m.charger_goodhart_v2().charger_ideation_v8()\n"
                "import pole.configuration_v56\n"
                "print('\\n'.join(sorted(os.path.relpath(x.__file__, " + repr(RACINE) + ") for x in list(sys.modules.values()) "
                "if getattr(x, '__file__', None) and x.__file__.startswith(" + repr(RACINE + os.sep) + "))))")
        out = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True, timeout=120, cwd=RACINE)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        importes = {l for l in out.stdout.splitlines() if l and not l.startswith("essais")}
        manquants = sorted(importes - set(LANCEUR.FICHIERS_GELES))
        self.assertEqual(manquants, [], f"fichiers importés hors du code gelé : {manquants}")
        for r in LANCEUR.FICHIERS_GELES:
            self.assertTrue(os.path.isfile(os.path.join(RACINE, r)), r)


def lancer(sortie, *args):
    return subprocess.run([sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "tour_ferme_v61.py"), sortie, *args],
                          capture_output=True, text=True, timeout=900, cwd=RACINE)


class LanceurABlanc(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v61-lanceur-")
        self.addCleanup(shutil.rmtree, self.d, True)

    def test_refus_avant_tout_appel(self):
        s = os.path.join(self.d, "s")
        r = lancer(s, "--etage", "1", "--a-blanc", "--bac", "factice")  # sans graine
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertFalse(os.path.exists(s))
        r = lancer(s, "--etage", "1", "--a-blanc", "--graine", "7", "--bac", "factice", "--familles-a-blanc", "a,a")
        self.assertEqual(r.returncode, 2)
        self.assertIn("FamillesNonSeparees", r.stderr)
        r = lancer(s, "--etage", "1", "--preenregistrement", "x.md", "--bac", "factice")
        self.assertEqual(r.returncode, 2)
        r = lancer(s, "--etage", "2", "--a-blanc", "--graine", "7", "--bac", "factice")
        self.assertEqual(r.returncode, 2)
        r = lancer(s, "--etage", "1", "--a-blanc", "--graine", str(2 ** 64), "--bac", "factice")
        self.assertEqual(r.returncode, 2)

    def test_course_courte_puis_lecture_et_artefacts(self):
        s = os.path.join(self.d, "sain")
        r = lancer(s, "--etage", "1", "--a-blanc", "--graine", "11", "--bac", "factice", "--generations", "2",
                   "--cartes-par-proposeur", "2", "--cartes-reference", "4", "--m-e-bh", "7")
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        rapport = json.load(open(os.path.join(s, "tour-ferme-v1-etage1.json")))
        lecture = L.lire_etage1(rapport["releve"])
        self.assertIn("T1", lecture["criteres"])
        self.assertEqual(lecture["passes_attendues"], sum(len(v) for v in rapport["releve"]["generations_jouees"].values()))
        self.assertTrue(all(isinstance(c["contre_calcul_ok"], bool) for c in rapport["releve"]["cartes"] if c["verdict"]))
        self.assertTrue(all(c["gardien"] == "refuse" for c in rapport["releve"]["cartes"] if c["temoin"] == "T-MAL"))
        m = json.load(open(os.path.join(s, "manifeste.json")))
        self.assertEqual(m["decisions"], DEC)
        self.assertEqual(set(m["code_sha256"]), set(LANCEUR.FICHIERS_GELES))
        # artefact garde 8 : proposeur hors gabarit → toutes ses cartes refusées au gardien, course valide
        s2 = os.path.join(self.d, "gabarit")
        r = lancer(s2, "--etage", "1", "--a-blanc", "--graine", "11", "--bac", "factice", "--generations", "2", "--cartes-par-proposeur", "2",
                   "--cartes-reference", "4", "--m-e-bh", "7", "--scenario-proposeur", "hors_gabarit")
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        rel = json.load(open(os.path.join(s2, "tour-ferme-v1-etage1.json")))["releve"]
        reel = [c for c in rel["cartes"] if c["bras"] == "reel" and not c["temoin"]]
        self.assertTrue(reel and all(c["gardien"] == "refuse" and "gabarit" in c["motif"] for c in reel))
        # artefact garde 5 : plafond franchi → code 3, sortie scellée, aucune issue
        s3 = os.path.join(self.d, "plafond")
        r = lancer(s3, "--etage", "1", "--a-blanc", "--graine", "11", "--bac", "factice", "--generations", "2", "--cartes-par-proposeur", "2",
                   "--cartes-reference", "4", "--m-e-bh", "7", "--cout-simule-usd", "0.3", "--plafond-usd", "0.5")
        self.assertEqual(r.returncode, 3, r.stderr[-2000:])
        rapport3 = json.load(open(os.path.join(s3, "tour-ferme-v1-etage1.json")))
        self.assertIn("plafond", rapport3["arret"])
        self.assertTrue(os.path.isfile(os.path.join(s3, "tour-ferme-v1-etage1.json.sha256")))
        self.assertTrue(rapport3["releve"]["arret"])
        self.assertFalse(L.lire_etage1(rapport3["releve"])["criteres"]["T1"])


class TestBacReelV61(unittest.TestCase):
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
        d = tempfile.mkdtemp(prefix="essai-v61-bac-")
        self.addCleanup(shutil.rmtree, d, True)
        r = lancer(os.path.join(d, "s"), "--etage", "1", "--a-blanc", "--graine", "12", "--bac", "reel", *uid, "--generations", "2",
                   "--cartes-par-proposeur", "2", "--cartes-reference", "3", "--m-e-bh", "7")
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        j = json.load(open(os.path.join(d, "s", "tour-ferme-v1-etage1.json")))["journal"]
        et = [l for l in j if l["evenement"] == "etage-tests-de-mort"]
        self.assertTrue(et and all(l["bac_a_sable"] == "bwrap" and l["factice"] is False for l in et))


if __name__ == "__main__":
    unittest.main()
