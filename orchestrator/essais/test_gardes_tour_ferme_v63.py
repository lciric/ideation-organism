"""Essais de B10 (contre-lecture 3, bloquant ; règle R5) sur le code v63 seul, et justification de I30 par le devis.

- **Garde 5, plafond de dépense de l'étage** (`pole/tour_ferme_v63.Compteur.ajouter`) : à l'unité (sans parts, et avec des parts
  dont la somme dépasse le plafond : le filet derrière les parts) et de bout en bout (course à blanc par le chemin réel, coût
  simulé des proposeurs : code 3, relevé partiel scellé, motif « plafond de dépense de l'étage franchi », lecture N1 d'arrêt sans
  issue A4) ; cas sain : même course sous un plafond large, code 0.
- **Garde 13, durée** (`Compteur.verifier_duree`, appelée après chaque appel et chaque étage) : horloge factice (égalité permise,
  dépassement → arrêt) et de bout en bout (`--duree-max-h` minuscule : code 3, relevé partiel scellé) ; cas sain : `--duree-max-h 24`.
- **Garde 14, critères T2 à T5** (`pole/lecture_tour_ferme_v63.lire_etage1`) : relevés synthétiques de `releve_sain` modifiés, au
  bord exact de chaque seuil (cas sain : le bord tient ; artefact : un pas au-delà → « ne tient pas (Tk) », Tk seul).
- **I30** : le devis (tailles moyennes de la section 12) rejoué étage par étage dans l'ordre du code sur le `Compteur` gelé et la
  borne par carte du cœur v63 : la course va au bout à 6,5 tours par carte (et quel que soit le nombre de tours), parts inchangées
  (12 et 3 USD), plafond 15 USD ; la règle v62 (0,5 USD par carte) s'y arrête.

Les six mutations survivantes des sondes de la contre-lecture 3 (T2, T3, T4, T5, plafond de l'étage, durée) et une mutation de bord
par critère sont au banc `essais/mutations_tour_ferme_v63.py`. Aucun réseau, aucun modèle."""

import os
import shutil
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
for _chemin in (ICI, RACINE):
    if _chemin not in sys.path:
        sys.path.insert(0, _chemin)

from essais.test_tour_ferme_v63 import COURT, courir, rapport_ou_rien, releve_sain  # noqa: E402  (fonctions seulement)
from pole import lecture_tour_ferme_v63 as L  # noqa: E402
from pole import tour_ferme_v63 as T  # noqa: E402


class _Courses(unittest.TestCase):
    COURSES = {}

    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="essai-v63-b10-")
        cls.r = {}
        for nom, opts in cls.COURSES.items():
            s = os.path.join(cls.d, nom)
            code, err = courir(s, *opts)
            cls.r[nom] = (code, err, rapport_ou_rien(s))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, True)

    def arret_scelle(self, nom, motif):
        code, err, r = self.r[nom]
        self.assertEqual(code, 3, f"{nom} : arrêt attendu (code 3) ; sortie : {err[-600:]}")
        self.assertIsNotNone(r, f"{nom} : relevé partiel absent")
        self.assertTrue(os.path.isfile(os.path.join(self.d, nom, "tour-ferme-v1-etage1.json.sha256")), f"{nom} : relevé non scellé")
        self.assertIn(motif, r["arret"])
        l = L.lire_tour_etage_1(r["releve"])["etage_1"]
        self.assertEqual((l["issue_etage_1"].startswith("ne tient pas"), l["n1"], l["issue_a4"]), (True, "arret", "non lue (arrêt)"))
        return r


# --- garde 5 : plafond de dépense de l'étage -------------------------------------------------------------------------------------


class Garde5PlafondEtage(unittest.TestCase):
    def test_unite_sain_et_artefact(self):
        c = T.Compteur(1.0, 3600.0)  # sans parts : le plafond de l'étage est la seule garde de dépense
        c.ajouter(0.4, "proposeur", "kimi")
        c.ajouter(0.6, "tests_de_mort", "argon")  # 1,0 USD = plafond : permis
        self.assertEqual(c.etat()["depense_usd"], 1.0)
        with self.assertRaisesRegex(T.ArretTour, "plafond de dépense de l'étage franchi", msg="garde 5 : plafond de l'étage franchi sans arrêt"):
            c.ajouter(0.01, "proposeur", "kimi")

    def test_unite_filet_derriere_les_parts(self):
        c = T.Compteur(1.0, 3600.0, {"kimi": 0.8, "argon": 0.5})  # parts de somme > plafond : aucune part franchie ici
        c.ajouter(0.7, "proposeur", "kimi")
        c.ajouter(0.3, "tests_de_mort", "argon")
        with self.assertRaisesRegex(T.ArretTour, "plafond de dépense de l'étage franchi", msg="garde 5 : plafond de l'étage franchi sans arrêt"):
            c.ajouter(0.1, "tests_de_mort", "argon")


class Garde5DeBoutEnBout(_Courses):
    COURSES = {"artefact": ["--a-blanc", "--graine", "11", "--cout-simule-usd", "0.5", "--plafond-usd", "0.9", *COURT],
               "sain": ["--a-blanc", "--graine", "11", "--cout-simule-usd", "0.5", "--plafond-usd", "50", *COURT]}

    def test_artefact_plafond_franchi_arret_scelle(self):
        r = self.arret_scelle("artefact", "plafond de dépense de l'étage franchi")
        self.assertEqual(r["releve"]["depense"]["depense_usd"], 1.0)
        self.assertEqual(r["releve"]["generations_jouees"]["reel"], [])

    def test_sain_plafond_large_course_au_bout(self):
        code, err, r = self.r["sain"]
        self.assertEqual(code, 0, err[-600:])
        self.assertEqual(r["releve"]["depense"]["depense_usd"], 2.0)
        self.assertEqual(L.lire_etage1(r["releve"])["issue_etage_1"], "tient")


# --- garde 13 : durée ----------------------------------------------------------------------------------------------------------


class Horloge:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class Garde13Duree(unittest.TestCase):
    def test_unite_sain_et_artefact(self):
        h = Horloge()
        c = T.Compteur(1e9, 10.0, None, h)
        h.t += 10.0
        c.verifier_duree()  # 10 s = plafond : permis
        c.ajouter(0.0, "proposeur", "kimi")
        h.t += 0.5
        with self.assertRaisesRegex(T.ArretTour, "plafond de durée de l'étage franchi", msg="garde 13 : durée franchie sans arrêt"):
            c.verifier_duree()
        with self.assertRaisesRegex(T.ArretTour, "plafond de durée", msg="garde 13 : durée non vérifiée après un appel"):
            c.ajouter(0.0, "proposeur", "kimi")


class Garde13DeBoutEnBout(_Courses):
    COURSES = {"artefact": ["--a-blanc", "--graine", "11", "--duree-max-h", "1e-9", *COURT],
               "sain": ["--a-blanc", "--graine", "11", "--duree-max-h", "24", *COURT]}

    def test_artefact_duree_franchie_arret_scelle(self):
        self.arret_scelle("artefact", "plafond de durée de l'étage franchi")

    def test_sain(self):
        code, err, r = self.r["sain"]
        self.assertEqual(code, 0, err[-600:])
        self.assertIsNone(r["releve"]["arret"])


# --- garde 14 : critères T2 à T5 de la lecture gelée, au bord de chaque seuil ----------------------------------------------------


def temoins(rel, nom, bras=None):
    return [c for c in rel["cartes"] if c["temoin"] == nom and (bras is None or c["bras"] == bras)]


def cartes_testees(rel, bras):
    return [c for c in rel["cartes"] if c["bras"] == bras and c.get("verdict")]


class _Lecture(unittest.TestCase):
    def tient(self, rel, k):
        r = L.lire_etage1(rel)
        self.assertTrue(r["criteres"][k], f"garde 14 : {k} manque au bord du seuil ({r['criteres']})")
        self.assertEqual(r["issue_etage_1"], "tient")
        return r

    def manque(self, rel, k, cas):
        r = L.lire_etage1(rel)
        self.assertFalse(r["criteres"][k], f"garde 14 : {k} tient sur l'artefact « {cas} »")
        self.assertEqual(r["issue_etage_1"], f"ne tient pas ({k})", f"{cas} : {r['criteres']}")
        return r


class Garde14T2(_Lecture):
    def test_sain_une_passe_manquee_au_plus(self):
        rel = releve_sain()
        temoins(rel, "T-VRAIE")[0]["verdict"] = "non concluant"
        self.tient(rel, "T2")

    def test_artefacts(self):
        rel = releve_sain()
        for c in temoins(rel, "T-VRAIE")[:2]:
            c["verdict"] = "non concluant"
        self.manque(rel, "T2", "deux passes de T-VRAIE sans « survit »")
        rel = releve_sain()
        temoins(rel, "T-VRAIE")[0]["verdict"] = "éliminée"
        self.manque(rel, "T2", "T-VRAIE « éliminée » une fois")
        rel = releve_sain()
        rel["cartes"].remove(temoins(rel, "T-VRAIE")[0])
        self.manque(rel, "T2", "une passe de T-VRAIE absente")


class Garde14T3(_Lecture):
    def test_sain_une_fausse_retenue_et_une_passe_de_T_ELIM_manquee(self):
        rel = releve_sain()
        temoins(rel, "T-F2")[0]["verdict"] = "survit"
        temoins(rel, "T-ELIM")[0]["verdict"] = "non concluant"
        self.tient(rel, "T3")

    def test_artefacts(self):
        cas = {}
        rel = releve_sain()
        for c in temoins(rel, "T-F2")[:2]:
            c["verdict"] = "survit"
        cas["deux passes de témoin faux promues puis survivantes"] = rel
        rel = releve_sain()
        temoins(rel, "T-ELIM")[0]["verdict"] = "survit"
        cas["T-ELIM « survit »"] = rel
        rel = releve_sain()
        for c in temoins(rel, "T-ELIM")[:2]:
            c["verdict"] = "non concluant"
        cas["T-ELIM « éliminée » dans deux passes de moins"] = rel
        rel = releve_sain()
        temoins(rel, "T-MAL")[0]["gardien"] = "passe"
        cas["T-MAL passé au gardien"] = rel
        rel = releve_sain()
        rel["cartes"].remove(temoins(rel, "T-MAL")[0])
        cas["T-MAL absent d'une passe"] = rel
        rel = releve_sain()
        rel["cartes"].remove(temoins(rel, "T-ELIM")[0])
        cas["T-ELIM absent d'une passe"] = rel
        for nom, rel in cas.items():
            with self.subTest(cas=nom):
                self.manque(rel, "T3", nom)


class Garde14T4(_Lecture):
    def test_sain_au_bord_des_deux_seuils(self):
        rel = releve_sain()  # testées : réel 21, aléatoire 13, recopie 6, en tout 40
        self.assertEqual((len(cartes_testees(rel, "reel")), len(cartes_testees(rel, "aleatoire")), len(cartes_testees(rel, "recopie_melange"))), (21, 13, 6))
        cartes_alea = [c for c in cartes_testees(rel, "aleatoire") if not c["temoin"]]
        for c in [c for c in cartes_testees(rel, "reel") if not c["temoin"]][:3] + cartes_alea[:4] + temoins(rel, "T-F2", "recopie_melange")[:1]:
            c["verdict"] = "non concluant"  # 8 / 40 = 0,20 en tout ; aléatoire 4 / 13 ≤ 0,40
        r = self.tient(rel, "T4")
        self.assertEqual(sum(b["non_concluant"] for b in r["bras"].values()), 8)
        rel = releve_sain()
        for c in [c for c in cartes_testees(rel, "aleatoire") if not c["temoin"]] + temoins(rel, "T-F2", "aleatoire")[:1]:
            c["verdict"] = "non concluant"  # aléatoire 5 / 13 = 0,385 ≤ 0,40
        self.tient(rel, "T4")

    def test_artefacts(self):
        rel = releve_sain()
        cartes_alea = [c for c in cartes_testees(rel, "aleatoire") if not c["temoin"]]
        for c in [c for c in cartes_testees(rel, "reel") if not c["temoin"]][:4] + cartes_alea[:4] + temoins(rel, "T-F2", "recopie_melange")[:1]:
            c["verdict"] = "non concluant"  # 9 / 40 > 0,20 ; chaque bras ≤ 0,40
        self.manque(rel, "T4", "« non concluant » au-delà de 0,20 sur les trois bras")
        rel = releve_sain()
        for c in [c for c in cartes_testees(rel, "aleatoire") if not c["temoin"]] + temoins(rel, "T-F2", "aleatoire")[:2]:
            c["verdict"] = "non concluant"  # aléatoire 6 / 13 > 0,40 ; en tout 6 / 40
        self.manque(rel, "T4", "« non concluant » au-delà de 0,40 dans un bras")
        rel = releve_sain()
        for nom in ("T-VRAIE", "T-ELIM", "T-F2"):
            temoins(rel, nom, "recopie_melange")[0]["verdict"] = "non concluant"  # recopie 3 / 6 > 0,40
        self.manque(rel, "T4", "« non concluant » au-delà de 0,40 dans le bras recopie-mélange")
        rel = releve_sain()
        next(c for c in cartes_testees(rel, "reel") if not c["temoin"])["contre_calcul_ok"] = False
        self.manque(rel, "T4", "un contre-calcul en désaccord")


class Garde14T5(_Lecture):
    @staticmethod
    def fd_aleatoire(rel, n):
        for c in [c for c in rel["cartes"] if c["bras"] == "aleatoire" and not c["temoin"] and c.get("verdict") == "survit"][:n]:
            c["delta_gain_nat"] = 0.0  # promue, survivante, sans nouveauté : fausse découverte

    @staticmethod
    def fd_recopie(rel, n):
        for c in [c for c in rel["cartes"] if c["bras"] == "recopie_melange" and not c["temoin"]][:n]:
            c.update(promue=True, verdict="survit", contre_calcul_ok=True)  # toute PS du bras recopie-mélange est une FD

    def test_sain_une_fausse_decouverte_par_bras(self):
        rel = releve_sain()
        self.fd_aleatoire(rel, 1)
        self.fd_recopie(rel, 1)
        r = self.tient(rel, "T5")
        self.assertEqual((r["bras"]["aleatoire"]["fd"], r["bras"]["recopie_melange"]["fd"]), (1, 1))

    def test_artefacts(self):
        rel = releve_sain()
        self.fd_aleatoire(rel, 2)
        r = self.manque(rel, "T5", "deux fausses découvertes du bras aléatoire")
        self.assertEqual(r["issue_a4"], "la chaîne ne discrimine pas")
        rel = releve_sain()
        self.fd_recopie(rel, 2)
        self.manque(rel, "T5", "deux fausses découvertes du bras recopie-mélange")


# --- I30 : le devis rejoué sur le Compteur gelé ------------------------------------------------------------------------------------


def jouer_devis(tours, prix=0.06, parts=(12.0, 3.0), borne=None, cartes_reelles=(4, 2, 2), carte_alea=1.5, temoins_par_passe=2.4,
                verif=0.02, en_plus=0.0, proposeur=0.024):
    """Le devis (section 12 : tailles moyennes) étage par étage dans l'ordre du code (par génération : réel, recopie-mélange,
    aléatoire ; par bras : étage des cartes puis étage des témoins ; contrôle du pire cas avant chaque étage, dépense après) sur le
    `Compteur` gelé. Coût d'une carte pour l'expérimentateur : tours × prix, borné par la borne par carte que l'étage tient.
    Rend (motif d'arrêt ou None, marge de Kimi au-delà du pire cas au dernier étage contrôlé, compteur)."""
    borne = T.BUDGET_EXPERIMENTATEUR_PAR_CARTE_USD if borne is None else borne
    c = T.Compteur(15.0, 1e9, {"kimi": parts[0], "argon": parts[1]})
    cout_carte, marge = min(tours * prix, borne), None
    try:
        for g in (1, 2, 3):
            for bras in ("reel", "recopie_melange", "aleatoire"):
                if bras == "recopie_melange" and g == 1:
                    continue  # archive du bras réel vide : la recopie ne joue pas en génération 1
                if bras == "reel":
                    c.ajouter(proposeur, "proposeur", "kimi")
                    c.ajouter(proposeur, "proposeur", "argon")
                n_cartes = {"reel": cartes_reelles[g - 1] + (en_plus if g == 1 else 0.0), "recopie_melange": 0.0, "aleatoire": carte_alea}[bras]
                for n in (n_cartes, temoins_par_passe):
                    if n <= 0:
                        continue
                    marge = c.parts["kimi"] - c.par_relais["kimi"] - n * borne
                    c.verifier_parts_avant_etage({"kimi": n * borne, "argon": n * T.BUDGET_VERIFICATEUR_PAR_CARTE_USD})
                    c.ajouter(n * cout_carte, "tests_de_mort", "kimi")
                    c.ajouter(n * verif, "tests_de_mort", "argon")
    except T.ArretTour as e:
        return str(e), marge, c
    return None, marge, c


class DevisI30(unittest.TestCase):
    def test_v63_tient_a_6_5_tours_par_carte_sous_15_USD(self):
        for tours in (2, 4, 5, 6, 6.5, 8, 12):
            arret, marge, c = jouer_devis(tours, prix=0.04 if tours == 2 else 0.06)
            self.assertIsNone(arret, f"I30 : la course s'arrête à {tours} tours par carte : {arret}")
            self.assertLessEqual(c.usd, 15.0)
            self.assertLessEqual(c.par_relais["kimi"], 12.0)
        arret, marge, c = jouer_devis(6.5)
        self.assertGreater(marge, 2.0, "I30 : marge de Kimi au dernier étage")
        self.assertAlmostEqual(c.par_relais["kimi"], 0.072 + 31.7 * 0.30, places=6)

    def test_v63_pire_cas_toutes_les_cartes_a_leur_borne(self):
        self.assertIsNone(jouer_devis(100, en_plus=8)[0], "I30 : huit cartes de plus que le devis, toutes à leur borne")
        self.assertIsNotNone(jouer_devis(100, en_plus=9)[0])  # la limite écrite : au-delà, arrêt avant l'étage, sans dépassement
        self.assertIsNone(jouer_devis(6.5, verif=0.05)[0], "I30 : vérificateur à 2,5 fois le prix supposé")

    def test_regle_v62_casse_a_6_5_tours(self):
        arret, marge, _ = jouer_devis(6.0, borne=0.5)
        self.assertIsNone(arret)
        self.assertAlmostEqual(marge, 0.18, places=2)  # contre-lecture 3, I30 : « ≈ 0,18 USD de marge »
        arret, _, _ = jouer_devis(6.5, borne=0.5)
        self.assertIsNotNone(arret, "la règle v62 devait s'arrêter à 6,5 tours par carte (constat I30)")
        self.assertIsNotNone(jouer_devis(6.0, borne=0.5, en_plus=1)[0], "v62 : une carte de plus et la course s'arrête")


if __name__ == "__main__":
    unittest.main()
