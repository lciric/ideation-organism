"""Essais de la v57 — verdict des tests de mort calculé par le noyau depuis le fichier brut (décision du directeur R-1057,
1er novembre 2026 ; `pole/tests_de_mort_v4.py`). Hors ligne, sans bac à sable ni réseau : les sorties d'une fiche sont posées
dans un dossier temporaire comme l'étage v2 les écrit (`prereg-court.json` scellé, `execution-NN/produits/<nom_copie>` scellés,
inventaire `fichiers_produits` de chaque exécution). Chaque garde : un cas sain et un artefact (R5). Graines dérivées par
`numpy.random.SeedSequence` (R9). Aucun fichier hors de l'arbre n'est lu ; tout est écrit dans le dossier d'essai."""

import hashlib
import itertools
import json
import os
import shutil
import sys
import types
import unittest

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from aides import CasAvecDossier  # noqa: E402
from pole import tests_de_mort_v2 as v2  # noqa: E402
from pole import tests_de_mort_v3 as v3  # noqa: E402
from pole import tests_de_mort_v4 as v4  # noqa: E402
from pole.outils import EcrasementInterdit, ecrire_json_scelle, ecrire_scelle, verifier_scelle  # noqa: E402

GRAINE_V57 = 20261101  # graine maîtresse des essais v57 ; une graine fille par statistique (R9)
SEUIL = "au moins 0,30"
BLOC = {"fichier": "scores.csv", "colonne": "score", "statistique": "moyenne"}
EPISODES = "episode,score\n1,0.1\n2,0.2\n"
SURVIT, ELIMINEE = [0.3, 0.5, 0.46], [0.1, 0.2, 0.24]  # moyennes 0,42 et 0,18 autour du seuil 0,30
BLOCS_MAL_FORMES = [  # (bloc, fragment du motif)
    (None, "absent"),
    ("moyenne de scores.csv", "absent"),
    ({"fichier": "scores.csv", "colonne": "score"}, "exactement"),
    (dict(BLOC, seuil="0,3"), "exactement"),
    (dict(BLOC, statistique="quantile"), "inconnue"),
    (dict(BLOC, statistique="proportion"), "inconnue"),  # la proportion de valeurs positives s'appelle part_positive (v2)
    (dict(BLOC, fichier="../scores.csv"), "chemin relatif propre"),
    (dict(BLOC, fichier="/racine/scores.csv"), "chemin relatif propre"),
    (dict(BLOC, fichier="tranche/episodes.csv"), "produit par le script"),
    (dict(BLOC, fichier="script.py"), "produit par le script"),
    (dict(BLOC, fichier="r" * 201 + ".csv"), "octets"),
    (dict(BLOC, colonne=""), "colonne"),
    (dict(BLOC, colonne=" score"), "colonne"),
    (dict(BLOC, colonne=3), "colonne"),
]


def csv_scores(valeurs, colonne="score"):
    return f"episode,{colonne}\n" + "".join(f"{i},{float(v)!r}\n" for i, v in enumerate(valeurs, 1))


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


class Base(CasAvecDossier):
    def setUp(self):
        super().setUp()
        self._numeros = itertools.count(1)

    def tranche(self):
        return types.SimpleNamespace(fichiers={"episodes.csv": {"texte": EPISODES, "sha256": hashlib.sha256(EPISODES.encode()).hexdigest()}},
                                     index_sha256="0" * 64)

    def fiche(self, seuil=SEUIL, signe="+", bloc=BLOC, sans_bloc=False):
        test = {"seuil": seuil, "test": "statistique des scores par épisode, calculée depuis episodes.csv", "donnees": ["episodes.csv"]}
        if not sans_bloc:
            test["statistique"] = dict(bloc) if isinstance(bloc, dict) else bloc
        return {"identifiant_auteur": "f1", "nom": "Une", "empreinte": "e" * 64, "type": "méthode",
                "enonce": "Hypothèse d'essai : le score moyen par épisode dépasse le seuil",
                "loi_predictive": {"prediction": "score moyen de 0,4", "signe": signe, "metrique": "score moyen par épisode"},
                "test_de_mort": test}

    def prereg(self, **kw):
        p, motif = v4.extraire_prereg_court_v4(self.fiche(**kw), self.tranche(), 1, {"executions": 3})
        self.assertIsNone(motif)
        return p

    def dossier_fiche(self, prereg, sceller=True):
        d = self.sous_dossier(f"fiche-{next(self._numeros):03d}")
        if sceller:
            ecrire_json_scelle(os.path.join(d, v4.NOM_PREREG), prereg)
        return d

    def execution(self, dossier, numero, produits=None, stdout="", statut="réussie", copier=True):
        """Une exécution comme l'étage v2 la consigne : copies scellées sous `execution-NN/produits/`, inventaire."""
        d_exec = os.path.join(dossier, f"execution-{numero:02d}")
        os.makedirs(d_exec, exist_ok=True)
        fichiers = []
        for chemin, contenu in sorted((produits or {}).items()):
            octets = contenu.encode("utf-8") if isinstance(contenu, str) else contenu
            copie = "produits/" + v4.nom_copie(chemin) if copier else None
            if copier:
                ecrire_scelle(os.path.join(d_exec, copie), octets)
            fichiers.append({"chemin": chemin, "sha256": hashlib.sha256(octets).hexdigest(), "copie_scellee": copier, "copie": copie})
        return {"numero": numero, "tour": numero, "statut": statut, "code": 0 if statut == "réussie" else 1,
                "lignes_resultat": v2.lignes_resultat(stdout), "lignes_calcul": v2.lignes_calcul(stdout), "fichiers_produits": fichiers}

    def jouer(self, contenu, stdout="", **kw):
        """Une fiche, une exécution réussie qui écrit scores.csv : le verdict du noyau (dossier dans `self.dossier`)."""
        p = self.prereg(**kw)
        d = self.dossier = self.dossier_fiche(p)
        texte = contenu if isinstance(contenu, (str, bytes)) else csv_scores(contenu)
        e = self.execution(d, 1, {"scores.csv": texte}, stdout=stdout)
        return v4.verdict_du_noyau(p, d, [e])

    def copie(self, dossier, numero=1, fichier="scores.csv"):
        return os.path.join(dossier, f"execution-{numero:02d}", "produits", v4.nom_copie(fichier))


# --- empilement (R12) -----------------------------------------------------------------------------------------------------


class TestEmpilementV4(unittest.TestCase):
    def test_v4_rend_les_objets_de_la_v3_et_de_la_v2(self):
        """La version 4 réutilise la version 3 (et, par elle, la version 2) telles quelles : mêmes objets."""
        for nom in ("ExecuteurBacASable", "MEMOIRE_BAC_MIN_MO", "comparer", "statistique_de_colonne", "chiffre_lu",
                    "nom_copie", "lire_regulier", "STATISTIQUES", "recalcul_noyau", "executer_tests_de_mort"):
            self.assertIs(getattr(v4, nom), getattr(v3, nom), nom)
        self.assertIs(v4.comparer, v2.comparer)
        self.assertIs(v4.statistique_de_colonne, v2.statistique_de_colonne)
        self.assertEqual(v4.MEMOIRE_BAC_MIN_MO, 768)
        # dit au docstring : l'étage de la v2 n'est pas encore câblé sur le verdict du noyau
        self.assertIs(v4.executer_tests_de_mort, v2.executer_tests_de_mort)
        self.assertIn("Non fait dans cette version", v4.__doc__)


# --- contrat du préenregistrement ------------------------------------------------------------------------------------------


class TestPreregV4(Base):
    def test_cas_sain_bloc_dans_le_preregistrement(self):
        p = self.prereg()
        self.assertEqual(p["statistique"], BLOC)
        self.assertEqual((p["seuil"]["valeur"], p["seuil"]["comparateur"]), (0.3, "≥"))
        self.assertEqual(p["plan_d_analyse"], p["regle_de_lecture"])
        for mot in ("le noyau calcule", "scores.csv", "jamais décisifs", "non concluant < éliminée < survit"):
            self.assertIn(mot, p["regle_de_lecture"])
        self.assertEqual(p["version_etage"], v4.VERSION_ETAGE)
        canon = v4.valider_champ_test_v4(self.fiche()["test_de_mort"])
        self.assertEqual(canon["statistique"], BLOC)
        self.assertEqual(canon["donnees"], ["episodes.csv"])

    def test_artefact_bloc_absent_ou_mal_forme(self):
        p, motif = v4.extraire_prereg_court_v4(self.fiche(sans_bloc=True), self.tranche(), 1, {})
        self.assertIsNone(p)
        self.assertIn("statistique", motif)
        self.assertIn("aucun repli", motif)
        with self.assertRaises(v4.ChampTestInvalide):
            v4.valider_champ_test_v4(self.fiche(sans_bloc=True)["test_de_mort"])
        for bloc, mot in BLOCS_MAL_FORMES:
            with self.subTest(bloc=bloc):
                p, motif = v4.extraire_prereg_court_v4(self.fiche(bloc=bloc), self.tranche(), 1, {})
                self.assertIsNone(p)
                self.assertIn(mot, motif)
                with self.assertRaises(v4.ChampTestInvalide):
                    v4.valider_champ_test_v4(self.fiche(bloc=bloc)["test_de_mort"])
        # le reste du préenregistrement est celui de la v2 : une donnée hors de la tranche est refusée à l'étage
        f = self.fiche()
        f["test_de_mort"]["donnees"] = ["ailleurs.csv"]
        self.assertIn("hors de la tranche", v4.extraire_prereg_court_v4(f, self.tranche(), 1, {})[1])
        # dit au docstring : la validation des fiches de la v2 refuse encore la clé `statistique` (câblage à faire)
        with self.assertRaises(v2.ChampTestInvalide):
            v2.valider_champ_test(self.fiche()["test_de_mort"])


# --- cas sain : le noyau calcule, des deux côtés du seuil -------------------------------------------------------------------


class TestVerdictCasSain(Base):
    def test_des_deux_cotes_du_seuil(self):
        r = self.jouer(SURVIT)
        self.assertEqual(r["verdict"], "survit")
        self.assertAlmostEqual(r["valeur_noyau"], 0.42)
        self.assertEqual(r["etiquette"], "verdict calculé par le noyau depuis le fichier brut")
        self.assertEqual(r["declaration"], BLOC)
        self.assertEqual(r["seuil"], {"valeur": 0.3, "comparateur": "≥"})
        self.assertEqual(r["execution"], 1)
        self.assertEqual(r["fichier_brut"]["copie"], "execution-01/produits/scores.csv.copie")
        self.assertEqual(r["fichier_brut"]["sha256"], hashlib.sha256(csv_scores(SURVIT).encode()).hexdigest())
        with open(os.path.join(self.dossier, v4.NOM_PREREG), "rb") as f:
            self.assertEqual(r["prereg_sha256"], hashlib.sha256(f.read()).hexdigest())
        self.assertEqual((r["chiffre_script"], r["concordance_script"], r["verdict_selon_chiffre_script"], r["calcul_du_script"]),
                         (None, None, None, []))
        self.assertIn("0.42 ≥ 0.3 : vrai", r["motif"])
        r = self.jouer(ELIMINEE)
        self.assertEqual(r["verdict"], "éliminée")
        self.assertAlmostEqual(r["valeur_noyau"], 0.18)
        self.assertIn("0.18 ≥ 0.3 : faux", r["motif"])

    def test_fichier_dans_un_sous_dossier_et_chemin_objet(self):
        """Le nom de la copie suit `nom_copie` de la v2 composant par composant ; le dossier peut être un `os.PathLike`."""
        import pathlib
        bloc = dict(BLOC, fichier="sorties/scores.csv")
        p = self.prereg(bloc=bloc)
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"sorties/scores.csv": csv_scores(SURVIT)})
        r = v4.verdict_du_noyau(p, pathlib.Path(d), [e])
        self.assertEqual(r["verdict"], "survit")
        self.assertEqual(r["fichier_brut"]["copie"], "execution-01/produits/sorties.copie/scores.csv.copie")

    def test_bornes_et_comparateurs(self):
        """Seuil atteint exactement, comparateur large ou strict, sens « au plus », et |x| ≤ (signe 0)."""
        for valeurs, seuil, signe, attendu in (([0.3, 0.3], "au moins 0,30", "+", "survit"),
                                               ([0.3, 0.3], "plus de 0,30", "+", "éliminée"),
                                               (ELIMINEE, "au plus 0,30", "-", "survit"),
                                               (SURVIT, "au plus 0,30", "-", "éliminée"),
                                               ([0.3, 0.3], "moins de 0,30", "-", "éliminée"),
                                               ([-0.02, 0.0, -0.01], "0,05", "0", "survit"),
                                               ([-0.2, -0.1], "0,05", "0", "éliminée")):
            with self.subTest(seuil=seuil, valeurs=valeurs):
                r = self.jouer(valeurs, seuil=seuil, signe=signe)
                self.assertEqual(r["verdict"], attendu)

    def test_le_chiffre_concordant_reste_un_temoin(self):
        r = self.jouer(SURVIT, stdout="calcul fini\nRESULTAT: 0.42\n")
        self.assertEqual(r["verdict"], "survit")
        self.assertEqual((r["chiffre_script"], r["ligne_script"], r["concordance_script"], r["verdict_selon_chiffre_script"]),
                         (0.42, "RESULTAT: 0.42", True, "survit"))
        self.assertIs(self.jouer(SURVIT, stdout="RESULTAT: 0.4\n")["concordance_script"], True)  # arrondi d'affichage (v2)
        r = self.jouer(SURVIT, stdout="RESULTAT: 0.43\n")
        self.assertEqual(r["verdict"], "survit")
        self.assertIs(r["concordance_script"], False)

    def test_oracle_independant_numpy_graines_seedsequence(self):
        """Huit statistiques, trois tirages chacune, seuil alternativement au-dessus et au-dessous de la valeur : la valeur du
        noyau est celle de numpy (oracle indépendant de `statistics`), le verdict suit le seuil (R9 : graines par SeedSequence)."""
        oracles = {"moyenne": np.mean, "mediane": np.median, "somme": np.sum, "minimum": np.min, "maximum": np.max,
                   "nombre": len, "part_positive": lambda x: np.mean(x > 0), "ecart_type": lambda x: np.std(x, ddof=1)}
        self.assertEqual(set(oracles), set(v4.STATISTIQUES))
        for stat, enfant in zip(v4.STATISTIQUES, np.random.SeedSequence(GRAINE_V57).spawn(len(v4.STATISTIQUES))):
            rng = np.random.default_rng(enfant)
            for k in range(3):
                x = rng.normal(0.2, 1.0, size=int(rng.integers(5, 40)))
                attendu = float(oracles[stat](x))
                seuil = round(attendu + float(rng.uniform(0.05, 0.5)) * (1 if k % 2 == 0 else -1), 6)
                with self.subTest(statistique=stat, tirage=k):
                    r = self.jouer([float(v) for v in x], seuil=f"au moins {seuil}", bloc=dict(BLOC, statistique=stat))
                    self.assertAlmostEqual(r["valeur_noyau"], attendu, delta=1e-9 * max(1.0, abs(attendu)))
                    self.assertEqual(r["verdict"], "survit" if attendu >= seuil else "éliminée")


# --- artefact 1 : le script imprime un chiffre qui « survit », le fichier dit « éliminée » --------------------------------------


class TestArtefact1ChiffreDuScript(Base):
    def test_chiffre_imprime_survit_fichier_elimine(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(ELIMINEE)}, stdout="RESULTAT: 0.9\n")
        r = v4.verdict_du_noyau(p, d, [e])
        self.assertEqual(r["verdict"], "éliminée")
        self.assertAlmostEqual(r["valeur_noyau"], 0.18)
        self.assertIs(r["concordance_script"], False)
        self.assertEqual((r["chiffre_script"], r["ligne_script"], r["verdict_selon_chiffre_script"]), (0.9, "RESULTAT: 0.9", "survit"))
        self.assertIn("DISCORDANT", r["motif"])
        self.assertIn("témoin seulement", r["motif"])
        # le défaut fermé : la lecture mécanique de la v2 aurait pris le chiffre imprimé
        self.assertEqual(v2.verdict_mecanique(p, [e])["verdict"], "survit")

    def test_symetrie_chiffre_imprime_elimine_fichier_survit(self):
        """R4 : un chiffre faux dans l'autre sens n'est pas plus décisif."""
        r = self.jouer(SURVIT, stdout="RESULTAT: 0.1\n")
        self.assertEqual(r["verdict"], "survit")
        self.assertIs(r["concordance_script"], False)
        self.assertEqual(r["verdict_selon_chiffre_script"], "éliminée")


# --- artefact 2 : le script déclare une autre statistique ou une autre colonne ----------------------------------------------


class TestArtefact2CalculDuScript(Base):
    VALEURS = [0.05, 0.1, 0.45]  # moyenne 0,2 (éliminée au seuil 0,30), maximum 0,45 (survivrait)

    def test_autre_statistique_declaree_ignoree(self):
        r = self.jouer(self.VALEURS, stdout="CALCUL: fichier=scores.csv; colonne=score; statistique=maximum\nRESULTAT: 0.45\n")
        self.assertEqual(r["verdict"], "éliminée")
        self.assertAlmostEqual(r["valeur_noyau"], 0.2)
        self.assertEqual(r["declaration"], BLOC)
        (c,) = r["calcul_du_script"]
        self.assertEqual((c["lu"]["statistique"], c["differe_du_prereg"], c["statut"]), ("maximum", True, v4.STATUT_CALCUL_DU_SCRIPT))
        self.assertIn("ignorée", r["motif"])

    def test_autre_fichier_autre_colonne_declares_ignores(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(self.VALEURS), "autre.csv": "x\n5\n"},
                           stdout="CALCUL: fichier=autre.csv; colonne=x; statistique=somme\nRESULTAT: 5\n")
        r = v4.verdict_du_noyau(p, d, [e])
        self.assertEqual(r["verdict"], "éliminée")
        self.assertEqual(r["fichier_brut"]["copie"], "execution-01/produits/scores.csv.copie")
        self.assertEqual((r["calcul_du_script"][0]["lu"]["fichier"], r["calcul_du_script"][0]["differe_du_prereg"]), ("autre.csv", True))

    def test_meme_declaration_toujours_temoin(self):
        r = self.jouer(SURVIT, stdout="CALCUL: fichier=scores.csv; colonne=score; statistique=moyenne\nRESULTAT: 0.42\n")
        self.assertEqual(r["verdict"], "survit")
        self.assertEqual((r["calcul_du_script"][0]["differe_du_prereg"], r["calcul_du_script"][0]["statut"]),
                         (False, v4.STATUT_CALCUL_DU_SCRIPT))


# --- artefact 3 : fichier absent, non copié, ou aucune exécution réussie -------------------------------------------------------


class TestArtefact3FichierAbsent(Base):
    def test_fichier_attendu_non_produit(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"autre.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.99\n")
        r = v4.verdict_du_noyau(p, d, [e])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("fichier attendu absent", r["motif"])
        self.assertEqual((r["valeur_noyau"], r["fichier_brut"], r["execution"]), (None, None, 1))
        self.assertEqual((r["chiffre_script"], r["verdict_selon_chiffre_script"], r["concordance_script"]), (0.99, "survit", None))

    def test_aucune_execution_reussie(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        for statut in ("échouée (code 1)", "tuée (délai)", "échouée (données altérées)", "refusée"):
            with self.subTest(statut=statut):
                e = self.execution(d, 1 + len(statut), {"scores.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.99\n", statut=statut)
                r = v4.verdict_du_noyau(p, d, [e])
                self.assertEqual(r["verdict"], "non concluant")
                self.assertIn("aucune exécution réussie", r["motif"])
                self.assertIsNone(r["execution"])
        r = v4.verdict_du_noyau(p, d, [])
        self.assertEqual((r["verdict"], r["execution"]), ("non concluant", None))

    def test_produit_non_copie_par_le_noyau(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.99\n", copier=False)
        r = v4.verdict_du_noyau(p, d, [e])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("non copié", r["motif"])

    def test_copie_disparue_ou_remplacee_par_un_lien(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.99\n")
        os.remove(self.copie(d))
        r = v4.verdict_du_noyau(p, d, [e])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("absente, lien", r["motif"])
        # lien : la cible a le bon contenu et le compagnon le bon sceau, mais le noyau ne suit jamais un lien
        d2 = self.dossier_fiche(p)
        e2 = self.execution(d2, 1, {"scores.csv": csv_scores(SURVIT)})
        cible = os.path.join(self.tmp, "cible-hors-sortie.csv")
        shutil.move(self.copie(d2), cible)
        os.symlink(cible, self.copie(d2))
        r = v4.verdict_du_noyau(p, d2, [e2])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("lien", r["motif"])
        # copie au-delà de la borne de copie du noyau (1 Mo), empreintes cohérentes : jamais lue
        d3 = self.dossier_fiche(p)
        e3 = self.execution(d3, 1, {"scores.csv": csv_scores(SURVIT)})
        gros = csv_scores(SURVIT).encode() + b"#" * v4.TAILLE_MAX_COPIE_PRODUIT
        os.remove(self.copie(d3))
        os.remove(self.copie(d3) + ".sha256")
        ecrire_scelle(self.copie(d3), gros)
        e3["fichiers_produits"][0]["sha256"] = hashlib.sha256(gros).hexdigest()
        r = v4.verdict_du_noyau(p, d3, [e3])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("trop grosse", r["motif"])


# --- artefact 4 : colonne absente, valeur illisible ----------------------------------------------------------------------


class TestArtefact4FichierIllisible(Base):
    CAS = [  # (nom, contenu du fichier brut, bloc, fragment du motif)
        ("colonne absente", "episode,valeur\n1,0.9\n", BLOC, "introuvable"),
        ("cellule non numérique", "episode,score\n1,abc\n", BLOC, "non numérique"),
        ("cellule non finie", "episode,score\n1,nan\n", BLOC, "non finie"),
        ("ligne trop courte", "episode,score\n1\n", BLOC, "trop courte"),
        ("fichier vide", "", BLOC, "vide"),
        ("en-tête seul", "episode,score\n", BLOC, "aucune valeur"),
        ("UTF-8 invalide", b"episode,score\n1,\xff\xfe\n", BLOC, "UTF-8"),
        ("champ CSV au-delà de la borne du lecteur", "episode,score\n1," + "9" * 200_000 + "\n", BLOC, "illisible (CSV)"),
        ("somme qui déborde", "episode,score\n1,1e308\n2,1e308\n", dict(BLOC, statistique="somme"), "dépassement"),
        ("médiane infinie", "episode,score\n1,1e308\n2,1e308\n", dict(BLOC, statistique="mediane"), "non finie"),
        ("écart type d'une seule valeur", "episode,score\n1,0.9\n", dict(BLOC, statistique="ecart_type"), "deux valeurs"),
    ]

    def test_non_concluant_avec_motif_jamais_le_chiffre_du_script(self):
        for nom, contenu, bloc, mot in self.CAS:
            with self.subTest(cas=nom):
                r = self.jouer(contenu, stdout="RESULTAT: 0.99\n", bloc=bloc)
                self.assertEqual(r["verdict"], "non concluant")
                self.assertIn(mot, r["motif"])
                self.assertEqual((r["valeur_noyau"], r["chiffre_script"], r["verdict_selon_chiffre_script"]), (None, 0.99, "survit"))
                self.assertIsNotNone(r["fichier_brut"])  # la copie a été lue : c'est son contenu qui est illisible


# --- artefact 5 : préenregistrement sans bloc statistique, ou sans seuil -------------------------------------------------------


class TestArtefact5PreregSansStatistique(Base):
    def test_prereg_de_la_v2_sans_bloc_refuse(self):
        p, motif = v2.extraire_prereg_court(self.fiche(sans_bloc=True), self.tranche(), 1, {"executions": 3})
        self.assertIsNone(motif)
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.9\n")
        with self.assertRaises(v4.PreregSansStatistique) as cm:
            v4.verdict_du_noyau(p, d, [e])
        self.assertIn("aucun repli sur le chiffre du script", str(cm.exception))
        self.assertIsInstance(cm.exception, v4.PreregRefuse)
        self.assertEqual(v2.verdict_mecanique(p, [e])["verdict"], "survit")  # ce que la v2 aurait rendu

    def test_bloc_mal_forme_refuse(self):
        for bloc, mot in BLOCS_MAL_FORMES:
            with self.subTest(bloc=bloc):
                p = self.prereg()
                p["statistique"] = bloc
                d = self.dossier_fiche(p)  # scellé tel quel : le refus ne vient pas du sceau
                e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.9\n")
                with self.assertRaises(v4.PreregSansStatistique) as cm:
                    v4.verdict_du_noyau(p, d, [e])
                self.assertIn(mot, str(cm.exception))
        for pas_un_prereg in (None, [], "prereg"):
            with self.subTest(prereg=pas_un_prereg), self.assertRaises(v4.PreregSansStatistique):
                v4.verdict_du_noyau(pas_un_prereg, self.tmp, [])

    def test_seuil_inutilisable_refuse(self):
        for seuil in ({"valeur": "0.3", "comparateur": "≥"}, {"valeur": True, "comparateur": "≥"}, {"valeur": None, "comparateur": "≥"},
                      {"valeur": float("nan"), "comparateur": "≥"}, {"valeur": float("inf"), "comparateur": "≥"},
                      {"valeur": 0.3, "comparateur": "≈"}, {"valeur": 0.3}, "au moins 0,3", None):
            with self.subTest(seuil=seuil):
                p = self.prereg()
                p["seuil"] = seuil
                d = self.dossier_fiche(p, sceller=False)  # le seuil est lu avant le sceau
                with self.assertRaises(v4.PreregSansSeuil):
                    v4.verdict_du_noyau(p, d, [])


# --- le préenregistrement est le préenregistrement scellé ---------------------------------------------------------------------


class TestPreregScelle(Base):
    def test_cas_sain_et_prereg_absent(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        self.assertEqual(v4.prereg_scelle(p, d)[0], json.loads(json.dumps(p)))
        with self.assertRaises(v4.PreregNonScelle) as cm:
            v4.verdict_du_noyau(p, self.dossier_fiche(p, sceller=False), [])
        self.assertIn("absent", str(cm.exception))

    def test_sceau_faux(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        with open(os.path.join(d, v4.NOM_PREREG + ".sha256"), "w", encoding="utf-8") as f:
            f.write("0" * 64 + "  " + v4.NOM_PREREG + "\n")
        with self.assertRaises(v4.PreregNonScelle) as cm:
            v4.verdict_du_noyau(p, d, [])
        self.assertIn("sceau", str(cm.exception))

    def test_prereg_change_apres_scellement(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)})
        change = json.loads(json.dumps(p))
        change["statistique"]["statistique"] = "maximum"
        with self.assertRaises(v4.PreregNonScelle) as cm:
            v4.verdict_du_noyau(change, d, [e])
        self.assertIn("diffère", str(cm.exception))
        # dans l'autre sens : le fichier scellé a été réécrit (et rescellé) après coup
        d2 = self.dossier_fiche(change)
        e2 = self.execution(d2, 1, {"scores.csv": csv_scores(SURVIT)})
        with self.assertRaises(v4.PreregNonScelle):
            v4.verdict_du_noyau(p, d2, [e2])

    def test_prereg_lien_refuse(self):
        p = self.prereg()
        source = self.dossier_fiche(p)
        d = self.dossier_fiche(p, sceller=False)
        os.symlink(os.path.join(source, v4.NOM_PREREG), os.path.join(d, v4.NOM_PREREG))
        shutil.copy(os.path.join(source, v4.NOM_PREREG + ".sha256"), os.path.join(d, v4.NOM_PREREG + ".sha256"))
        with self.assertRaises(v4.PreregNonScelle) as cm:
            v4.verdict_du_noyau(p, d, [])
        self.assertIn("lien", str(cm.exception))


# --- l'exécution lue ------------------------------------------------------------------------------------------------------------


class TestExecutionLue(Base):
    def test_la_derniere_execution_reussie_fait_foi(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e1 = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)})
        e2 = self.execution(d, 2, {"scores.csv": csv_scores(ELIMINEE)})
        r = v4.verdict_du_noyau(p, d, [e1, e2])
        self.assertEqual(r["verdict"], "éliminée")
        self.assertEqual(r["execution"], 2)

    def test_une_execution_echouee_n_est_jamais_lue(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e1 = self.execution(d, 1, {"scores.csv": csv_scores(ELIMINEE)})
        for numero, statut in ((2, "échouée (code 1)"), (3, "échouée (données altérées)"), (4, "tuée (délai)")):
            with self.subTest(statut=statut):
                e = self.execution(d, numero, {"scores.csv": csv_scores(SURVIT)}, statut=statut)
                r = v4.verdict_du_noyau(p, d, [e1, e])
                self.assertEqual(r["verdict"], "éliminée")
                self.assertEqual(r["execution"], 1)

    def test_execution_reussie_sans_numero_utilisable(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.42\n")
        self.assertEqual(v4.verdict_du_noyau(p, d, [e])["verdict"], "survit")  # cas sain
        for numero in (None, "1", True, -1, 1.0):
            with self.subTest(numero=numero):
                r = v4.verdict_du_noyau(p, d, [dict(e, numero=numero)])
                self.assertEqual(r["verdict"], "non concluant")
                self.assertIn("numéro", r["motif"])
        r = v4.verdict_du_noyau(p, d, [{k: x for k, x in e.items() if k != "numero"}])
        self.assertEqual(r["verdict"], "non concluant")
        # la lecture du fichier brut garde sa propre garde (fonction publique)
        self.assertEqual(v4.lire_fichier_brut(d, e, BLOC)[1], None)
        for numero in ("1", -1):
            with self.subTest(lecture=numero):
                valeur, motif, info = v4.lire_fichier_brut(d, dict(e, numero=numero), BLOC)
                self.assertEqual((valeur, info), (None, None))
                self.assertIn("numéro", motif)

    def test_aucun_repli_sur_une_execution_anterieure(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e1 = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)})
        e2 = self.execution(d, 2, {"autre.csv": csv_scores(SURVIT)}, stdout="RESULTAT: 0.42\n")
        r = v4.verdict_du_noyau(p, d, [e1, e2])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertEqual(r["execution"], 2)


# --- la copie lue est la copie scellée de l'inventaire ------------------------------------------------------------------------


class TestCopieScellee(Base):
    def test_copie_alteree_puis_rescellee(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(ELIMINEE)})
        os.remove(self.copie(d))
        os.remove(self.copie(d) + ".sha256")
        ecrire_scelle(self.copie(d), csv_scores(SURVIT))  # contenu et compagnon cohérents, mais pas ceux de l'inventaire
        r = v4.verdict_du_noyau(p, d, [e])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("altérée", r["motif"])

    def test_inventaire_incoherent(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)})
        self.assertEqual(v4.verdict_du_noyau(p, d, [e])["verdict"], "survit")  # cas sain
        (entree,) = e["fichiers_produits"]
        for nom, fichiers in (("fichier inscrit deux fois", [entree, dict(entree)]),
                              ("copie inscrite sous un autre nom", [dict(entree, copie="produits/autre.csv.copie")])):
            with self.subTest(cas=nom):
                r = v4.verdict_du_noyau(p, d, [dict(e, fichiers_produits=fichiers)])
                self.assertEqual(r["verdict"], "non concluant")
                self.assertIn("incohérent", r["motif"])

    def test_sceau_de_la_copie_faux(self):
        p = self.prereg()
        d = self.dossier_fiche(p)
        e = self.execution(d, 1, {"scores.csv": csv_scores(SURVIT)})
        with open(self.copie(d) + ".sha256", "w", encoding="utf-8") as f:
            f.write("0" * 64 + "  scores.csv.copie\n")
        r = v4.verdict_du_noyau(p, d, [e])
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("sceau de la copie", r["motif"])


# --- ordre total et sélection --------------------------------------------------------------------------------------------------


class TestRangEtSelection(Base):
    def test_ordre_total(self):
        rang = v4.rang_verdict
        self.assertLessEqual(rang("non concluant"), rang("éliminée"))
        self.assertLess(rang("éliminée"), rang("survit"))
        self.assertLess(rang("non concluant"), rang("survit"))
        self.assertEqual(sorted(v4.VERDICTS, key=rang), list(v4.ORDRE_DES_VERDICTS))
        self.assertEqual(sorted(v4.ORDRE_DES_VERDICTS), sorted(v4.VERDICTS))
        for inconnu in ("Survit", "éliminé", "eliminee", "", None, "non-concluant", 2):
            with self.subTest(verdict=inconnu), self.assertRaises(v4.VerdictInconnu):
                rang(inconnu)

    def test_selection_ne_retient_que_survit(self):
        s1 = self.jouer(SURVIT)
        el = self.jouer(ELIMINEE)
        nc = self.jouer("episode,valeur\n1,0.9\n", stdout="RESULTAT: 0.99\n")  # colonne absente, chiffre imprimé « survit »
        s2 = self.jouer([0.9])
        self.assertEqual([x["verdict"] for x in (s1, el, nc, s2)], ["survit", "éliminée", "non concluant", "survit"])
        retenus = v4.selectionner([s1, el, nc, s2])
        self.assertEqual(retenus, [s1, s2])
        self.assertIs(retenus[0], s1)
        self.assertEqual(v4.selectionner([nc]), [])
        self.assertEqual(v4.selectionner([el]), [])
        self.assertEqual(v4.selectionner([nc, el]), [])

    def test_selection_refuse_un_verdict_hors_noyau(self):
        s1 = self.jouer(SURVIT)
        v2_style = {"verdict": "survit", "fiabilite_du_chiffre": v2.ETIQUETTE_NON_RECALCULE, "etiquette": v2.ETIQUETTE_NON_RECALCULE}
        for mauvais in (v2_style, {"verdict": "survit"}, "survit"):
            with self.subTest(entree=mauvais), self.assertRaises(v4.VerdictNonNoyau):
                v4.selectionner([s1, mauvais])
        with self.assertRaises(v4.VerdictInconnu):
            v4.selectionner([dict(s1, verdict="peut-être")])
        self.assertEqual(v4.selectionner([s1]), [s1])


# --- consignation ------------------------------------------------------------------------------------------------------------


class TestConsignation(Base):
    def test_verdict_consigne_scelle_sans_ecrasement(self):
        r = self.jouer(ELIMINEE, stdout="RESULTAT: 0.9\n")
        sha = v4.ecrire_verdict_du_noyau(self.dossier, r)
        chemin = os.path.join(self.dossier, v4.NOM_VERDICT)
        self.assertTrue(verifier_scelle(chemin))
        with open(chemin, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), sha)
        self.assertEqual(lire(chemin), json.loads(json.dumps(r)))
        with self.assertRaises(EcrasementInterdit):
            v4.ecrire_verdict_du_noyau(self.dossier, dict(r, verdict="survit"))
        self.assertEqual(lire(chemin)["verdict"], "éliminée")
        with self.assertRaises(v4.VerdictNonNoyau):
            v4.ecrire_verdict_du_noyau(self.sous_dossier("autre"), dict(r, etiquette=v2.ETIQUETTE_RECALCULE))
        with self.assertRaises(v4.VerdictInconnu):
            v4.ecrire_verdict_du_noyau(self.sous_dossier("autre"), dict(r, verdict="survit ?"))


# --- R12 ------------------------------------------------------------------------------------------------------------------------


class TestR12V57(unittest.TestCase):
    ESSENTIELS = ("pole/tests_de_mort.py", "pole/tests_de_mort_v2.py", "pole/tests_de_mort_v3.py", "essais/aides_v56.py",
                  "essais/mutations_v55.py", "essais/mutations_v56.py", "essais/test_v56_corrections.py")

    def test_aucun_fichier_de_la_v56_present_dans_l_arbre_modifie(self):
        """Tout fichier de la liste d'empreintes v56 présent dans l'arbre garde son empreinte ; l'étage v2 et v3 et les bancs et
        essais v56 doivent y être (les entrées absentes sont les archives non publiées dans cet arbre, comptées)."""
        liste = os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v56.txt")
        self.assertTrue(verifier_scelle(liste))
        presents, absents = [], []
        with open(liste, encoding="utf-8") as f:
            for ligne in f:
                sha, rel = ligne.rstrip("\n").split("  ", 1)
                chemin = os.path.join(RACINE, rel)
                if not os.path.exists(chemin):
                    absents.append(rel)
                    continue
                with open(chemin, "rb") as g:
                    self.assertEqual(hashlib.sha256(g.read()).hexdigest(), sha, rel)
                presents.append(rel)
        for rel in self.ESSENTIELS:
            self.assertIn(rel, presents)
        self.assertNotIn("pole/tests_de_mort_v4.py", presents + absents)
        self.assertEqual(len(presents) + len(absents), 422)


if __name__ == "__main__":
    unittest.main()
