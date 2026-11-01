import contextlib
import io
import json
import os
import subprocess
import sys
import unittest

from essais.aides import CasAvecDossier, fiche
from pole.cycle import ConfigGeneration
from pole.fiche import charger_fiches
from pole.outils import verifier_scelle
from pole.pole import SortieNonVide, executer_pole, principal
from pole.simulation import AdaptateurSimule, MondeSimule

SORTIE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEMPLES = os.path.join(SORTIE, "exemples")
POPULATION = os.path.join(EXEMPLES, "population-demo-v1.json")
TEMOINS = os.path.join(EXEMPLES, "temoins-demo-v1.json")


def silencieux(argv):
    sortie, erreurs = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreurs):
        code = principal(argv)
    return code, sortie.getvalue(), erreurs.getvalue()


class BoucleEtArchive(CasAvecDossier):
    def adaptateur(self, verites=None):
        temoins = charger_fiches(TEMOINS)
        v = {t.enonce: t.temoin == "vraie" for t in temoins}
        v.update(verites or {})
        return AdaptateurSimule(graine=9, monde=MondeSimule(9, v))

    def test_trois_generations_journal_et_archive_scelles(self):
        racine = os.path.join(self.tmp, "pole")
        with open(os.path.join(EXEMPLES, "monde-demo-v1.json"), encoding="utf-8") as f:
            verites = json.load(f)["verites"]
        bilan = executer_pole(charger_fiches(POPULATION), charger_fiches(TEMOINS), self.adaptateur(verites),
                              ConfigGeneration(budget_generation_usd=10), 3, 30, racine, horodatage_fourni="2026-10-26T00:00:00Z")
        self.assertGreaterEqual(bilan["generations_executees"], 1)
        journaux = sorted(n for n in os.listdir(os.path.join(racine, "journal")) if n.endswith(".json"))
        self.assertEqual(len(journaux), bilan["generations_executees"])
        for chemin in [os.path.join(racine, "journal", j) for j in journaux] + [
                os.path.join(racine, "archive", "index.json"), os.path.join(racine, "bilan.json")]:
            self.assertTrue(verifier_scelle(chemin), chemin)
        with open(os.path.join(racine, "archive", "index.json"), encoding="utf-8") as f:
            index = json.load(f)
        self.assertTrue(any(e["temoin"] == "vraie" for e in index.values()))
        self.assertTrue(any(e["temoin"] == "fausse" for e in index.values()))
        self.assertTrue(any(e["statut"] == "eliminee" for e in index.values()), "l'archive garde les éliminées")

    def test_sortie_non_vide_jamais_ecrasee(self):
        racine = os.path.join(self.tmp, "pole")
        os.makedirs(racine)
        with open(os.path.join(racine, "existant.txt"), "w", encoding="utf-8") as f:
            f.write("x")
        with self.assertRaises(SortieNonVide):
            executer_pole([fiche("P1")], charger_fiches(TEMOINS), self.adaptateur(), ConfigGeneration(), 1, 10, racine)

    def test_arret_quand_plus_rien_ne_survit(self):
        fausses = [fiche(f"P{i}", enonce=f"Hypothèse fausse numéro {i} sur la parité des tris") for i in range(3)]
        verites = {f.enonce: False for f in fausses}
        bilan = executer_pole(fausses, charger_fiches(TEMOINS), self.adaptateur(verites), ConfigGeneration(), 3, 30,
                              os.path.join(self.tmp, "pole"))
        self.assertEqual(bilan["arret"], "plus aucune fiche ne survit")
        self.assertEqual(bilan["generations_executees"], 1)

    def test_arret_sur_budget(self):
        bilan = executer_pole(charger_fiches(POPULATION), charger_fiches(TEMOINS), self.adaptateur(),
                              ConfigGeneration(budget_generation_usd=3.0), 3, 3.0, os.path.join(self.tmp, "pole"))
        self.assertEqual(bilan["arret"], "budget épuisé")
        self.assertLessEqual(bilan["depense_totale"], 3.0)
        self.assertIn("hors budget", bilan["comptes_par_statut"])


class LigneDeCommande(CasAvecDossier):
    def test_simulation_par_la_ligne_de_commande(self):
        racine = os.path.join(self.tmp, "cli")
        code, sortie, _ = silencieux(["--moteur", "simule", "--population", POPULATION, "--temoins", TEMOINS,
                                      "--generations", "1", "--budget-usd", "10", "--sortie", racine])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(sortie)["generations"], 1)

    def test_moteur_reel_jamais_lance_sans_armement(self):
        racine = os.path.join(self.tmp, "reel")
        code, _, erreurs = silencieux(["--moteur", "claude-sdk", "--population", POPULATION, "--temoins", TEMOINS,
                                       "--sortie", racine, "--url-relais", "http://127.0.0.1:8787"])
        self.assertEqual(code, 2)
        self.assertIn("MoteurNonArme", erreurs)
        code, _, erreurs = silencieux(["--moteur", "claude-sdk", "--confirmer-moteur-reel", "--population", POPULATION,
                                       "--temoins", TEMOINS, "--sortie", racine, "--url-relais", "https://distant.exemple"])
        self.assertEqual(code, 2)
        self.assertIn("ModeleNonPermis", erreurs, "v6 : les modèles par défaut (simulés) sont refusés pour le moteur réel")
        modeles = ["--modele-experimentateur", "claude-opus-5-5", "--modele-verificateur", "claude-fable-5-1",
                   "--modele-recombinaison", "claude-opus-5-5", "--modele-synthese", "claude-opus-5-5"]
        code, _, erreurs = silencieux(["--moteur", "claude-sdk", "--confirmer-moteur-reel", "--population", POPULATION,
                                       "--temoins", TEMOINS, "--sortie", racine, "--url-relais", "https://distant.exemple",
                                       "--selection", "pari", "--monde-noyau"] + modeles)
        self.assertEqual(code, 2)
        self.assertIn("RelaisInvalide", erreurs)
        code, _, erreurs = silencieux(["--moteur", "claude-sdk", "--confirmer-moteur-reel", "--population", POPULATION,
                                       "--temoins", TEMOINS, "--sortie", racine, "--url-relais", "http://127.0.0.1:8787",
                                       "--selection", "pari"] + modeles)
        self.assertEqual(code, 2)
        self.assertIn("--monde-noyau est requis", erreurs, "v6 : moteur réel en pari sans monde du noyau refusé")
        self.assertFalse(os.path.exists(racine))

    def test_lancement_isole(self):
        sortie = subprocess.run([sys.executable, "-I", "-B", "pole", "--help"], cwd=SORTIE, env={}, capture_output=True,
                                timeout=60, check=False)
        self.assertEqual(sortie.returncode, 0, sortie.stderr.decode())
        self.assertIn("--moteur", sortie.stdout.decode())


class Ablation(CasAvecDossier):
    def test_ablation_memoire_ecrit_la_comparaison(self):
        racine = os.path.join(self.tmp, "ablation")
        code, _, erreurs = silencieux(["--moteur", "simule", "--population", POPULATION, "--temoins", TEMOINS,
                                       "--monde-simule", os.path.join(EXEMPLES, "monde-demo-v1.json"), "--generations",
                                       "2", "--budget-usd", "20", "--p-redite", "0.5", "--sortie", racine,
                                       "--ablation-memoire"])
        self.assertEqual(code, 0, erreurs)
        with open(os.path.join(racine, "comparaison-memoire-v1.json"), encoding="utf-8") as f:
            comparaison = json.load(f)
        self.assertEqual(set(comparaison["agregat"]), {"avec-memoire", "sans-memoire"})
        self.assertEqual(comparaison["agregat"]["avec-memoire"]["redites_testees"], 0)


if __name__ == "__main__":
    unittest.main()
