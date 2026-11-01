import json
import os
import unittest

from essais.aides import CasAvecDossier, fiche
from pole.cycle import ConfigGeneration
from pole.fiche import charger_fiches
from pole.memoire import Memoire, brier, jaccard
from pole.pole import executer_pole
from pole.simulation import AdaptateurSimule, MondeSimule

ICI = os.path.dirname(os.path.abspath(__file__))
EXEMPLES = os.path.join(os.path.dirname(ICI), "exemples")
ELIMINEE = "Le centrage des exemplaires améliore l'information de la mémoire spectrale"


def memoire_avec_eliminee():
    m = Memoire(seuil_redite=0.5)
    e = fiche("E1", enonce=ELIMINEE)
    e.statut = "eliminee"
    m.indexer(e, {"verdict_final": "eliminee", "motif": "statistique sous le seuil (réfutée)"}, 0)
    return m


class Redite(unittest.TestCase):
    def test_jaccard_cas_connu(self):
        self.assertEqual(jaccard("chat", "chats"), 0.5)
        self.assertEqual(jaccard("Évaluation", "evaluation"), 1.0)

    def test_redite_refusee(self):
        m = memoire_avec_eliminee()
        verdict = m.garde_redite(fiche("N1", enonce=ELIMINEE + " (reformulé)"))
        self.assertFalse(verdict["accepte"])
        self.assertEqual(verdict["proches"][0][0], "E1")

    def test_redite_meme_prediction_refusee(self):
        m = memoire_avec_eliminee()
        f = fiche("N1", enonce=ELIMINEE, ce_qui_change={"E1": "nouvelle population"})
        self.assertFalse(m.garde_redite(f)["accepte"])

    def test_redite_a_prediction_nouvelle_acceptee(self):
        m = memoire_avec_eliminee()
        f = fiche("N1", enonce=ELIMINEE, ce_qui_change={"E1": "effet prédit deux fois plus fort, seuil plus sévère"},
                  prediction={"signe": "+", "valeur": 1.0, "texte": "effet fort"})
        self.assertTrue(m.garde_redite(f)["accepte"])

    def test_fiche_eloignee_acceptee_et_memoire_inactive(self):
        m = memoire_avec_eliminee()
        self.assertTrue(m.garde_redite(fiche("N2", enonce="Un pas plus petit stabilise la descente"))["accepte"])
        m.active = False
        self.assertTrue(m.garde_redite(fiche("N1", enonce=ELIMINEE))["accepte"])


class BibliothequeEtCalibration(unittest.TestCase):
    def indexer(self, m, identifiant, statut, severite, **modifs):
        f = fiche(identifiant, severite_attendue=severite, protocole=f"protocole {identifiant}, n=400", **modifs)
        f.statut = statut
        m.indexer(f, {"verdict_final": statut}, 0)

    def test_gabarit_servi_avec_sa_severite(self):
        m = Memoire(seuil_severe=0.05)
        self.indexer(m, "S1", "survit", 0.01)
        self.indexer(m, "S2", "survit", 0.2)
        self.indexer(m, "T1", "survit", 0.001, temoin="vraie")
        texte = m.texte_consigne("experimentateur")
        self.assertIn("protocole S1, n=400", texte)
        self.assertIn("sévérité annoncée 0.01", texte)
        self.assertNotIn("protocole S2", texte)
        self.assertNotIn("protocole T1", texte, "un témoin n'est jamais servi aux agents")

    def test_brier_cas_connu(self):
        self.assertAlmostEqual(brier([(0.2, 0), (0.5, 1), (0.9, 1)]), 0.1)
        m = Memoire()
        for i, (s, statut) in enumerate([(0.2, "eliminee"), (0.5, "survit"), (0.9, "survit")]):
            self.indexer(m, f"F{i}", statut, s)
        registre = m.registre_calibration()["par_source"]["population-initiale"]
        self.assertAlmostEqual(registre["brier"], 0.1)
        self.assertEqual(registre["nombre_de_fiches"], 3)


class SecretDansUnAgent(AdaptateurSimule):
    """Un agent de synthèse qui recopie une clé (factice) dans ses leçons : elle ne doit jamais entrer dans la mémoire."""

    def _synthese(self, dossier):
        bloc = {"lecons": "Leçons : protocoles sévères utiles ; api_key=sk-ant-api03-FAUXFAUXFAUXFAUX"}
        return "Leçons écrites.\n```json\n" + json.dumps(bloc) + "\n```\n", "ok"


class Lecons(CasAvecDossier):
    def lancer(self, adaptateur_classe=AdaptateurSimule, generations=2):
        population = charger_fiches(os.path.join(EXEMPLES, "population-demo-v1.json"))
        temoins = charger_fiches(os.path.join(EXEMPLES, "temoins-demo-v1.json"))
        with open(os.path.join(EXEMPLES, "monde-demo-v1.json"), encoding="utf-8") as f:
            verites = json.load(f)["verites"]
        verites.update({t.enonce: t.temoin == "vraie" for t in temoins})
        adaptateur = adaptateur_classe(graine=5, monde=MondeSimule(5, verites))
        racine = os.path.join(self.tmp, "pole")
        executer_pole(population, temoins, adaptateur, ConfigGeneration(budget_generation_usd=10), generations, 30, racine)
        return adaptateur, racine

    def test_lecons_servies_a_la_generation_suivante(self):
        adaptateur, racine = self.lancer()
        with open(os.path.join(racine, "journal", "generation-00.json"), encoding="utf-8") as f:
            lecon = json.load(f)["memoire"]["lecons_ecrites"]
        self.assertTrue(lecon)
        g0 = [a for a in adaptateur.appels if a["role"] == "experimentateur" and "generation-00" in a["dossier"]]
        g1 = [a for a in adaptateur.appels if a["role"] == "experimentateur" and "generation-01" in a["dossier"]]
        reco0 = [a for a in adaptateur.appels if a["role"] == "recombinaison" and "generation-00" in a["dossier"]]
        self.assertTrue(g0 and g1)
        self.assertTrue(all("Leçons de la génération" not in a["consigne"] for a in g0))
        self.assertTrue(all(lecon in a["consigne"] for a in g1))
        self.assertTrue(all(lecon in a["consigne"] for a in reco0))

    def test_aucune_cle_dans_la_memoire(self):
        _, racine = self.lancer(SecretDansUnAgent, generations=1)
        for dossier, _, fichiers in os.walk(racine):
            for nom in fichiers:
                with open(os.path.join(dossier, nom), encoding="utf-8", errors="replace") as f:
                    self.assertNotIn("sk-ant-api03-FAUX", f.read(), os.path.join(dossier, nom))
        with open(os.path.join(racine, "memoire", "memoire-generation-00.json"), encoding="utf-8") as f:
            self.assertIn("[CAVIARDÉ]", f.read())


if __name__ == "__main__":
    unittest.main()
