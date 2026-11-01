"""Essais de la v57b — câblage du verdict calculé par le noyau (décision du directeur R-1057, 1er novembre 2026) : étage de
tests de mort v5 (`pole/tests_de_mort_v5.py`), point de sélection entre générations (`pole/etage_entre_generations_v57.py`),
course 2 v57 (`pole/course2_v57.py`).

Hors ligne. Exécution **simulée** : l'exécuteur factice de l'étage (`ExecuteurFactice` : le python du système dans un processus
à part, avec un prélude qui refuse le réseau et l'écriture hors du dossier de travail ; **sans `bwrap`, aucune barrière** — le
vrai bac à sable n'est pas joué ici). Adaptateur scripté : aucun appel de modèle, aucun coût réel ; aucun réseau. Chaque garde :
un cas sain et un artefact (R5). Tout est écrit dans des dossiers d'essai ; aucun fichier de l'arbre n'est modifié. Aucun tirage
aléatoire (R9 sans objet ici)."""

import hashlib
import inspect
import itertools
import json
import os
import re
import shutil
import sys
import tempfile
import types
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides  # noqa: E402  (`aides.BASE` lu à l'appel : redirigé par conftest ou par le banc de mutations)
import aides_v56 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import configuration_v56 as cfg  # noqa: E402
from pole import course2_v56 as c56  # noqa: E402
from pole import course2_v57 as c57  # noqa: E402
from pole import dossier_ferme as dfm  # noqa: E402
from pole import etage_entre_generations_v53 as e53  # noqa: E402
from pole import etage_entre_generations_v57 as e57  # noqa: E402
from pole import fiches_v53 as fv  # noqa: E402
from pole import ideation_v2 as idn  # noqa: E402
from pole import tests_de_mort_v2 as v2  # noqa: E402
from pole import tests_de_mort_v3 as v3  # noqa: E402
from pole import tests_de_mort_v4 as v4  # noqa: E402
from pole import tests_de_mort_v5 as v5  # noqa: E402
from pole.adaptateurs import Resultat  # noqa: E402
from pole.etage_entre_generations_v53 import MachineNonJetable  # noqa: E402
from pole.outils import EcrasementInterdit, ecrire_json_scelle, ecrire_scelle, sha256_fichier, verifier_scelle  # noqa: E402
from pole.protocole_outils import DEBUT_DONNEES, FIN_DONNEES  # noqa: E402

SEUIL = "au moins 0,30"
BLOC = {"fichier": "scores.csv", "colonne": "score", "statistique": "moyenne"}
EPISODES = "episode,valeur\n1,0.2\n2,0.4\n3,0.5\n"
SURVIT, ELIMINEE = [0.3, 0.5, 0.46], [0.1, 0.2, 0.24]  # moyennes 0,42 et 0,18 autour du seuil 0,30
CHAMPS_FICHE = ["titre", "hypothese", "prediction", "signe", "metrique", "test_de_mort"]
CORRESPONDANCE = {"nom": "titre", "enonce": "hypothese", "prediction": "prediction", "signe": "signe", "metrique": "metrique",
                  "test_de_mort": "test_de_mort"}
JETABLE = {"PATH": "/usr/bin:/bin", "POLE_MACHINE_JETABLE_V56": "1"}
EXPERIMENTATEUR, LECTEUR = ("exp", "claude-opus-5-5"), ("lec", "claude-fable-5-1")
FIN = "```json\n" + json.dumps({"fin": "fini"}) + "\n```"


# --- aides ---------------------------------------------------------------------------------------------------------------------


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def csv_scores(valeurs):
    return "episode,score\n" + "".join(f"{i},{float(v)!r}\n" for i, v in enumerate(valeurs, 1))


def script(valeurs=None, imprime=None, alterer=False):
    """Un script d'expérimentateur : lit la donnée de la tranche ; `alterer` y écrit (incident « données altérées ») ; écrit le
    fichier brut `scores.csv` si `valeurs` est donné ; imprime `RESULTAT: <imprime>` (le témoin) si `imprime` est donné."""
    lignes = ["donnees = open('tranche/episodes.csv', encoding='utf-8').read().splitlines()", "print('lignes lues :', len(donnees))"]
    if alterer:
        lignes.append("open('tranche/episodes.csv', 'a', encoding='utf-8').write('9,9.9\\n')")
    if valeurs is not None:
        lignes.append(f"open('scores.csv', 'w', encoding='utf-8').write({csv_scores(valeurs)!r})")
    if imprime is not None:
        lignes.append(f"print('RESULTAT: {imprime}')")
    return "\n".join(lignes) + "\n"


def bloc_exp(texte_script):
    return "```json\n" + json.dumps({"experience": [{"executer": {"script": texte_script}}]}, ensure_ascii=False) + "\n```"


SCENARIOS = {  # fiche → réponses de l'expérimentateur, tour par tour (puis « fin »)
    "fA": [bloc_exp(script(SURVIT, imprime="0.42"))],  # saine : le fichier brut dit « survit »
    "fB": [bloc_exp(script(ELIMINEE, imprime="0.9"))],  # le chiffre imprimé dit « survit », le fichier « éliminée »
    "fC": [bloc_exp(script(None, imprime="0.9"))],  # aucun fichier brut produit, chiffre « survit » imprimé
    "fD": [bloc_exp(script(SURVIT, imprime="0.42", alterer=True)),  # incident (exécution 1 : données altérées), puis…
           bloc_exp(script(SURVIT, imprime="0.42"))],  # … une exécution réussie dont le fichier dit « survit »
}


def section_de(consigne, debut_titre):
    """L'objet JSON de la section de données (`section_servie`) dont le titre commence par `debut_titre`, ou None."""
    m = re.search(r"## " + re.escape(debut_titre) + r"[^\n]*\n.*?" + re.escape(DEBUT_DONNEES) + r"\s*```json\n(.*?)\n```\s*"
                  + re.escape(FIN_DONNEES), consigne, re.S)
    return json.loads(m.group(1)) if m else None


def lecteur_temoin(consigne):
    """Le lecteur scripté (témoin honnête du chiffre imprimé) : applique le seuil gelé à la dernière ligne `RESULTAT:` de la
    dernière exécution réussie."""
    prereg = section_de(consigne, v5.TITRE_SECTION_PREREG)
    vue = section_de(consigne, "Sortie scellée des exécutions")
    reussies = [e for e in vue if e["statut"] == "réussie" and e["lignes_resultat"]]
    if not reussies:
        return "VERDICT: non concluant ; chiffre: aucun ; ligne: aucune"
    ligne = reussies[-1]["lignes_resultat"][-1]
    valeur = float(ligne.split(":", 1)[1])
    survit = v5.comparer(valeur, prereg["seuil"]["comparateur"], prereg["seuil"]["valeur"])
    return f"VERDICT: {'survit' if survit else 'éliminée'} ; chiffre: {valeur} ; ligne: {ligne}"


class AdaptateurScripte:
    """Expérimentateur et lecteur scriptés (aucun appel de modèle). `alterer_prereg` : fiches dont l'expérimentateur, à son
    premier tour, altère `prereg-court.json` (artefact : préenregistrement changé après scellement)."""
    nom = "scripte-v57b"

    def __init__(self, scenarios, alterer_prereg=()):
        self.scenarios, self.alterer_prereg, self.appels = scenarios, set(alterer_prereg), []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        if role == v5.ROLE_EXPERIMENTATEUR:
            d_fiche = os.path.dirname(os.path.dirname(dossier))
            fiche, tour = os.path.basename(d_fiche), int(os.path.basename(dossier).split("-")[1])
            if fiche in self.alterer_prereg and tour == 1:
                with open(os.path.join(d_fiche, v5.NOM_PREREG), "a", encoding="utf-8") as f:
                    f.write(" ")
            reponses = self.scenarios.get(fiche, [])
            texte = reponses[tour - 1] if tour <= len(reponses) else FIN
        elif role == v5.ROLE_LECTEUR:
            fiche, texte = os.path.basename(os.path.dirname(dossier)), lecteur_temoin(consigne)
        else:
            raise AssertionError(f"rôle inattendu : {role}")
        self.appels.append({"role": role, "fiche": fiche, "consigne": consigne})
        return Resultat(texte, [], 0.01, "ok")


def contenu(ident, bloc=BLOC):
    test = {"seuil": SEUIL, "test": "score moyen par épisode, calculé depuis episodes.csv", "donnees": ["episodes.csv"]}
    if bloc is not None:
        test["statistique"] = dict(bloc)
    return {"titre": f"Fiche {ident}", "hypothese": f"Hypothèse d'essai {ident} : le score moyen par épisode dépasse le seuil",
            "prediction": "score moyen de 0,4", "signe": "+", "metrique": "score moyen par épisode", "test_de_mort": test}


def fiche_projetee(ident="f1", bloc=BLOC):
    """Une fiche telle que l'étage la lit (`etage_entre_generations_v53.projeter`)."""
    c = contenu(ident, bloc)
    return {"identifiant_auteur": ident, "empreinte": "e" * 64, "nom": c["titre"], "enonce": c["hypothese"],
            "loi_predictive": {"prediction": c["prediction"], "signe": c["signe"], "metrique": c["metrique"]},
            "test_de_mort": c["test_de_mort"]}


TRANCHE_NS = types.SimpleNamespace(fichiers={"episodes.csv": {"texte": EPISODES, "sha256": hashlib.sha256(EPISODES.encode()).hexdigest()}},
                                   index_sha256="0" * 64, vue_index=lambda: [{"chemin": "episodes.csv", "titre": "Épisodes d'essai"}])


def creer_tranche(dossier):
    tr = os.path.join(dossier, "tranche")
    os.makedirs(tr)
    with open(os.path.join(tr, "episodes.csv"), "w", encoding="utf-8") as f:
        f.write(EPISODES)
    dfm.ecrire_index(tr, [{"chemin": "episodes.csv", "titre": "Épisodes d'essai", "resume": "épisodes d'essai (v57b)"}])
    lb = os.path.join(dossier, "liste-blanche.json")
    idn.construire_liste_blanche([os.path.join(tr, "index.json")], lb)
    return v5.charger_tranche(tr, idn.charger_liste_blanche(lb))


def generation(dossier, tranche, idents, sans_bloc=()):
    """Un dossier de génération au format de l'étage (`preparer_generation` de la v53) : toutes les fiches éligibles, dans
    l'ordre donné."""
    fiches = {i: fv.preparer(contenu(i, None if i in sans_bloc else BLOC), CHAMPS_FICHE, ident=i, case=("t", "b"),
                             fournisseur="essai", passe=1) for i in idents}
    classement = [{"ident": i, "notable": True, "rang": k} for k, i in enumerate(idents, 1)]
    return e53.preparer_generation(dossier, classement, fiches, nombre=len(idents), tranche_index_sha256=tranche.index_sha256,
                                   correspondance=CORRESPONDANCE, lisible=True)


def reglages(tranche, nombre):
    return {"tranche": tranche, "nombre": nombre, "experimentateur": EXPERIMENTATEUR, "lecteur": LECTEUR,
            "executeur": v5.ExecuteurFactice(delai_s=30.0), "moteur": "simule"}


def resume_scelle(dossier_generation):
    """Le résumé de l'étage tel que son manifeste scellé le porte (écrit même si l'étage ou la sélection s'arrête)."""
    chemin = os.path.join(dossier_generation, "manifeste-tests-de-mort.json")
    if not verifier_scelle(chemin):
        return {"par_fiche": []}
    return lire(chemin)["reglages"]["resume"]


class AvecDossierDeClasse(unittest.TestCase):
    """Un dossier d'essai par classe (l'étage est joué une fois par classe, dans `setUpClass`)."""

    @classmethod
    def dossier_de_classe(cls):
        os.makedirs(aides.BASE, exist_ok=True)
        d = tempfile.mkdtemp(dir=aides.BASE)
        cls.addClassCleanup(shutil.rmtree, d, True)
        return d


# --- de bout en bout : machine jetable, étage v5, sélection entre générations ----------------------------------------------------


class TestBoutEnBoutV57b(AvecDossierDeClasse):
    """Cinq fiches projetées dans un dossier de génération ; `jouer_etage_v57` par son chemin par défaut (machine jetable v56,
    étage v5 avec l'exécuteur factice, sélection). fA saine ; fB imprime « survit », son fichier dit « éliminée » ; fC n'écrit
    aucun fichier brut ; fD a un incident puis une exécution réussie dont le fichier dit « survit » ; fE n'a pas de bloc."""

    @classmethod
    def setUpClass(cls):
        d = cls.dossier_de_classe()
        cls.tranche = creer_tranche(d)
        cls.gen = generation(os.path.join(d, "gen"), cls.tranche, ["fA", "fB", "fC", "fD", "fE"], sans_bloc=("fE",))
        cls.ad = AdaptateurScripte(SCENARIOS)
        cls.erreur, cls.retour = None, None
        try:
            cls.retour = e57.jouer_etage_v57(cls.ad, cls.gen, reglages=reglages(cls.tranche, 5), environnement=JETABLE)
        except Exception as x:  # noqa: BLE001 — jamais avalée : `test_selection_ne_retient_que_la_fiche_saine` la montre
            cls.erreur = x
        cls.resume = resume_scelle(cls.gen)
        cls.par = {r["identifiant_auteur"]: r for r in cls.resume["par_fiche"]}

    def test_selection_ne_retient_que_la_fiche_saine(self):
        self.assertIsNone(self.erreur)
        sel = self.retour["selection"]
        self.assertEqual(sel["retenues"], ["fA"])
        self.assertEqual([(x["identifiant_auteur"], x["verdict"]) for x in sel["exclues"]],
                         [("fB", "éliminée"), ("fC", "non concluant"), ("fD", "non concluant"), ("fE", None)])
        self.assertIn("non testée", sel["exclues"][3]["motif"])
        self.assertEqual(sel["version_etage"], v5.VERSION_ETAGE_V5)
        chemin = os.path.join(self.gen, e57.NOM_SELECTION)
        self.assertTrue(verifier_scelle(chemin))
        self.assertEqual(lire(chemin), {k: v for k, v in sel.items() if k not in ("fichier", "sha256")})
        self.assertEqual(sel["sha256"], sha256_fichier(chemin))

    def test_fiche_saine_survit(self):
        r = self.par["fA"]
        self.assertEqual((r["statut"], r["verdict"]), ("testée", "survit"))
        n = r["verdict_noyau"]
        self.assertEqual(n["etiquette"], v4.ETIQUETTE_NOYAU)
        self.assertAlmostEqual(n["valeur_noyau"], 0.42)
        self.assertEqual(n["fichier_brut"]["copie"], "execution-01/produits/scores.csv.copie")
        self.assertEqual(n["fichier_brut"]["sha256"], hashlib.sha256(csv_scores(SURVIT).encode()).hexdigest())
        self.assertIs(n["concordance_script"], True)
        self.assertIsNone(r["desaccord"])
        self.assertEqual(r["motif_verdict"], n["motif"])
        chemin = os.path.join(self.gen, "noyau", "tests-de-mort", "fA", v5.NOM_VERDICT_V5)
        self.assertTrue(verifier_scelle(chemin))
        self.assertEqual(lire(chemin), n)
        self.assertEqual(r["verdict_noyau_sha256"], sha256_fichier(chemin))

    def test_chiffre_imprime_survit_fichier_elimine(self):
        r = self.par["fB"]
        self.assertEqual(r["verdict"], "éliminée")
        n = r["verdict_noyau"]
        self.assertAlmostEqual(n["valeur_noyau"], 0.18)
        self.assertEqual((n["chiffre_script"], n["verdict_selon_chiffre_script"], n["concordance_script"]), (0.9, "survit", False))
        self.assertEqual((r["lecture_mecanique"]["verdict"], r["lecteur"]["verdict"]), ("survit", "survit"))  # témoins
        self.assertIn("chiffre imprimé par le script", r["desaccord"])
        self.assertIn("lecteur neuf", r["desaccord"])
        self.assertIn("jamais décisifs", r["desaccord"])

    def test_aucun_fichier_produit_non_concluant(self):
        r = self.par["fC"]
        self.assertEqual(r["verdict"], "non concluant")
        self.assertIn("fichier attendu absent", r["motif_verdict"])
        self.assertEqual((r["verdict_noyau"]["chiffre_script"], r["verdict_noyau"]["valeur_noyau"]), (0.9, None))

    def test_incident_non_concluant_meme_si_le_fichier_dit_survit(self):
        r = self.par["fD"]
        n = r["verdict_noyau"]
        self.assertEqual([e["statut"] for e in r["executions"]], ["échouée (données altérées)", "réussie"])
        self.assertEqual((n["execution"], n["verdict_sur_le_fichier"]), (2, "survit"))
        self.assertEqual(r["verdict"], "non concluant")
        self.assertEqual([x["type"] for x in n["incidents"]], ["données de la tranche altérées pendant une exécution"])
        self.assertIn("incident de la fiche", r["motif_verdict"])
        self.assertLessEqual(v5.rang_verdict(r["verdict"]), v5.rang_verdict(n["verdict_sur_le_fichier"]))

    def test_fiche_sans_bloc_refusee_a_l_etage(self):
        r = self.par["fE"]
        self.assertEqual(r["statut"], "refusée à l'étage")
        self.assertIn("statistique", r["motif"])
        self.assertIn("aucun repli", r["motif"])
        self.assertIsNone(r["verdict"])
        self.assertNotIn("fE", [a["fiche"] for a in self.ad.appels])  # aucune session pour une fiche sans bloc
        self.assertTrue(verifier_scelle(os.path.join(self.gen, "noyau", "tests-de-mort", "fE", "refus.json")))

    def test_consignes_servies(self):
        exp = [a["consigne"] for a in self.ad.appels if a["fiche"] == "fA" and a["role"] == v5.ROLE_EXPERIMENTATEUR]
        self.assertTrue(exp)
        for mot in ("`scores.csv`", "`score`", "« moyenne »", "≥ 0.3", "dernière exécution réussie", "n'est qu'un témoin",
                    "`CALCUL:` est ignorée"):
            self.assertIn(mot, exp[0])
        self.assertNotIn("est le chiffre lu", exp[0])  # la phrase de la v2 : le chiffre imprimé n'est plus lu
        lec = [a["consigne"] for a in self.ad.appels if a["fiche"] == "fA" and a["role"] == v5.ROLE_LECTEUR]
        self.assertEqual(len(lec), 1)
        self.assertIn("témoin, jamais décisive", lec[0])

    def test_verdict_scelle_avant_le_lecteur_comptes_et_materiau(self):
        self.assertEqual(self.resume["version_etage"], v5.VERSION_ETAGE_V5)
        self.assertEqual(self.resume["comptes"], {"survit": 1, "éliminée": 1, "non concluant": 2})
        self.assertEqual(self.resume["refusees_a_l_etage"], 1)
        ev = lire(os.path.join(self.gen, "manifeste-tests-de-mort.json"))["reglages"]["journal"]["evenements"]
        for ident in ("fA", "fB", "fC", "fD"):
            n = {e["evenement"] + ("/" + e.get("role", "") if e["evenement"] == "session" else ""): e["n"]
                 for e in ev if e.get("fiche") == ident}
            self.assertLess(n["sortie-scellee"], n["verdict-noyau-scelle"], ident)
            self.assertLess(n["verdict-noyau-scelle"], n["session/" + v5.ROLE_LECTEUR], ident)
        with open(os.path.join(self.gen, "noyau", "tests-de-mort", "materiau-tests-de-mort.md"), encoding="utf-8") as f:
            materiau = f.read()
        self.assertIn(f"Fiche fA (rang 1) : survit ({v4.ETIQUETTE_NOYAU})", materiau)
        self.assertIn("Fiche fD (rang 4) : non concluant (incident de la fiche ; sur le fichier : survit", materiau)
        self.assertIn("Fiche fE (rang 5) : non testée (", materiau)


# --- le défaut de la v56 fermé ; le chemin d'exécution est celui de la v3 ---------------------------------------------------------


class TestDefautFermeEtMemeChemin(AvecDossierDeClasse):
    """Les mêmes quatre fiches et les mêmes scripts, joués par l'étage v3 (v56) et par l'étage v5 (v57b)."""

    @classmethod
    def setUpClass(cls):
        d = cls.dossier_de_classe()
        tranche = creer_tranche(d)
        cls.par, cls.resumes = {}, {}
        for nom, module in (("v3", v3), ("v5", v5)):
            g = generation(os.path.join(d, "gen-" + nom), tranche, ["fA", "fB", "fC", "fD"])
            r = {}
            module.executer_tests_de_mort(AdaptateurScripte(SCENARIOS), g, resume_sortie=r, **reglages(tranche, 4))
            cls.resumes[nom] = r
            cls.par[nom] = {x["identifiant_auteur"]: x for x in r["par_fiche"]}

    def test_le_defaut_de_la_v56_est_ferme(self):
        v56 = {i: self.par["v3"][i]["verdict"] for i in ("fA", "fB", "fC", "fD")}
        self.assertEqual(v56, {"fA": "survit", "fB": "survit", "fC": "survit", "fD": "non concluant"})  # le chiffre imprimé décidait
        v57b = {i: self.par["v5"][i]["verdict"] for i in ("fA", "fB", "fC", "fD")}
        self.assertEqual(v57b, {"fA": "survit", "fB": "éliminée", "fC": "non concluant", "fD": "non concluant"})

    def test_meme_chemin_d_execution(self):
        """Mêmes exécutions (statuts, codes, empreintes des scripts et des sorties, fichiers produits et copies scellées,
        incidents), au temps d'exécution près."""
        for ident in ("fA", "fB", "fC", "fD"):
            a, b = self.par["v3"][ident], self.par["v5"][ident]
            sans_duree = [[{k: v for k, v in e.items() if k != "duree_s"} for e in x["executions"]] for x in (a, b)]
            self.assertTrue(sans_duree[0], ident)
            self.assertEqual(sans_duree[0], sans_duree[1], ident)
            self.assertEqual(a["incidents"], b["incidents"], ident)

    def test_la_selection_v57_refuse_le_resume_de_la_v56(self):
        with self.assertRaises(v4.VerdictNonNoyau):
            e57.selection_entre_generations(self.resumes["v3"])
        self.assertEqual(e57.selection_entre_generations(self.resumes["v5"])["retenues"], ["fA"])


# --- préenregistrement refusé par le noyau : arrêt de l'étage, aucun repli ---------------------------------------------------------


class TestPreregAltere(CasAvecDossier):
    def test_prereg_change_apres_scellement_arrete_l_etage(self):
        tranche = creer_tranche(self.tmp)
        g = generation(os.path.join(self.tmp, "gen"), tranche, ["fA"])
        ad = AdaptateurScripte(SCENARIOS, alterer_prereg=("fA",))
        with self.assertRaises(v5.EtageInterrompu) as cm:
            v5.executer_tests_de_mort(ad, g, **reglages(tranche, 1))
        self.assertIn("PreregNonScelle", str(cm.exception))
        self.assertIn("aucun repli", str(cm.exception))
        self.assertIn("PreregNonScelle", resume_scelle(g)["arret"])
        self.assertFalse(os.path.exists(os.path.join(g, "noyau", "tests-de-mort", "fA", v5.NOM_VERDICT_V5)))
        self.assertNotIn(v5.ROLE_LECTEUR, [a["role"] for a in ad.appels])


# --- unités : verdict du noyau v5, consignation, validateur, consignes ----------------------------------------------------------


class TestVerdictDuNoyauV5(CasAvecDossier):
    def setUp(self):
        super().setUp()
        self._n = itertools.count(1)

    def jouer(self, contenu_brut, incidents, bloc=BLOC):
        p, motif = v5.extraire_prereg_court(fiche_projetee(bloc=bloc), TRANCHE_NS, 1, {"executions": 3})
        self.assertIsNone(motif)
        d = self.sous_dossier(f"f-{next(self._n)}")
        ecrire_json_scelle(os.path.join(d, v5.NOM_PREREG), p)
        octets = contenu_brut.encode("utf-8")
        ecrire_scelle(os.path.join(d, "execution-01", "produits", v5.nom_copie("scores.csv")), octets)
        e = {"numero": 1, "statut": "réussie", "lignes_resultat": [], "lignes_calcul": [],
             "fichiers_produits": [{"chemin": "scores.csv", "sha256": hashlib.sha256(octets).hexdigest(), "copie_scellee": True,
                                    "copie": "produits/" + v5.nom_copie("scores.csv")}]}
        return v5.verdict_du_noyau_v5(p, d, [e], incidents)

    def test_sans_incident_le_verdict_de_la_v4(self):
        for valeurs, attendu in ((SURVIT, "survit"), (ELIMINEE, "éliminée")):
            with self.subTest(attendu=attendu):
                r = self.jouer(csv_scores(valeurs), [])
                self.assertEqual((r["verdict"], r["verdict_sur_le_fichier"]), (attendu, attendu))
                self.assertEqual((r["etiquette"], r["incidents"], r["version_etage"], r["calcul_sur_le_fichier"]),
                                 (v4.ETIQUETTE_NOYAU, [], v5.VERSION_ETAGE_V5, v4.VERSION_ETAGE))
                self.assertEqual(r["motif"], r["motif_sur_le_fichier"])

    def test_incident_jamais_mieux_que_le_verdict_sur_le_fichier(self):
        incident = {"type": "dossier de travail non retiré", "fiche": "f1", "execution": 1, "motif": "essai"}
        for brut, sur_fichier in ((csv_scores(SURVIT), "survit"), (csv_scores(ELIMINEE), "éliminée"),
                                  ("episode,valeur\n1,0.9\n", "non concluant")):
            with self.subTest(sur_fichier=sur_fichier):
                r = self.jouer(brut, [incident])
                self.assertEqual((r["verdict"], r["verdict_sur_le_fichier"]), ("non concluant", sur_fichier))
                self.assertLessEqual(v5.rang_verdict(r["verdict"]), v5.rang_verdict(r["verdict_sur_le_fichier"]))
                self.assertIn("incident de la fiche (dossier de travail non retiré)", r["motif"])
                self.assertEqual(r["incidents"], [incident])
                self.assertEqual(r["etiquette"], v4.ETIQUETTE_NOYAU)

    def test_incidents_mal_donnes_refuses(self):
        for mauvais in (None, "incident", {"type": "x"}):
            with self.subTest(incidents=mauvais), self.assertRaises(TypeError):
                self.jouer(csv_scores(SURVIT), mauvais)

    def test_prereg_sans_bloc_refuse_sans_repli(self):
        p, _ = v2.extraire_prereg_court(fiche_projetee(bloc=None), TRANCHE_NS, 1, {})
        d = self.sous_dossier("sans-bloc")
        ecrire_json_scelle(os.path.join(d, v5.NOM_PREREG), p)
        with self.assertRaises(v4.PreregSansStatistique):
            v5.verdict_du_noyau_v5(p, d, [], [])


class TestConsignationV5(CasAvecDossier):
    def test_verdict_scelle_sans_ecrasement_et_artefacts(self):
        v = {"etiquette": v4.ETIQUETTE_NOYAU, "verdict": "éliminée", "motif": "essai"}
        sha = v5.ecrire_verdict_du_noyau_v5(self.tmp, v)
        chemin = os.path.join(self.tmp, v5.NOM_VERDICT_V5)
        self.assertTrue(verifier_scelle(chemin))
        self.assertEqual((lire(chemin), sha256_fichier(chemin)), (v, sha))
        with self.assertRaises(EcrasementInterdit):
            v5.ecrire_verdict_du_noyau_v5(self.tmp, dict(v, verdict="survit"))
        with self.assertRaises(v4.VerdictNonNoyau):
            v5.ecrire_verdict_du_noyau_v5(self.sous_dossier("a"), dict(v, etiquette=v2.ETIQUETTE_NON_RECALCULE))
        with self.assertRaises(v4.VerdictInconnu):
            v5.ecrire_verdict_du_noyau_v5(self.sous_dossier("b"), dict(v, verdict="survit ?"))


class TestValidateurEtPreregV5(unittest.TestCase):
    def test_cas_sain_bloc_accepte(self):
        canon = v5.valider_champ_test(contenu("f1")["test_de_mort"])
        self.assertEqual(canon["statistique"], BLOC)
        self.assertEqual(canon["donnees"], ["episodes.csv"])
        self.assertIn("statistique", v5.GABARIT_TEST)
        self.assertNotIn("statistique", v2.GABARIT_TEST)
        p, motif = v5.extraire_prereg_court(fiche_projetee(), TRANCHE_NS, 1, {})
        self.assertIsNone(motif)
        self.assertEqual(p["statistique"], BLOC)

    def test_artefact_fiche_sans_bloc_refusee(self):
        with self.assertRaises(v5.ChampTestInvalide) as cm:
            v5.valider_champ_test(contenu("f1", bloc=None)["test_de_mort"])
        self.assertIn("aucun repli", str(cm.exception))
        for mauvais in (dict(BLOC, statistique="quantile"), dict(BLOC, fichier="tranche/episodes.csv"), {"fichier": "scores.csv"}):
            with self.subTest(bloc=mauvais), self.assertRaises(v5.ChampTestInvalide):
                v5.valider_champ_test(contenu("f1", bloc=mauvais)["test_de_mort"])
        with self.assertRaises(v5.ChampTestTropLong):  # les bornes de taille de la v2 tiennent
            v5.valider_champ_test(dict(contenu("f1")["test_de_mort"], seuil="x" * (v2.TAILLE_MAX_SEUIL + 1)))
        p, motif = v5.extraire_prereg_court(fiche_projetee(bloc=None), TRANCHE_NS, 1, {})
        self.assertIsNone(p)
        self.assertIn("aucun repli", motif)

    def test_ideation_v2_inchangee_refuse_encore_le_bloc(self):
        """Dit au rendu : `ideation_v2` importe en dur le validateur de la v2 (non câblé en v57b)."""
        self.assertIs(idn.valider_champ_test, v2.valider_champ_test)
        with self.assertRaises(v2.ChampTestInvalide):
            idn.valider_champ_test(contenu("f1")["test_de_mort"])


class TestConsignesV5(unittest.TestCase):
    def prereg(self, bloc=BLOC):
        p, _ = (v5.extraire_prereg_court if bloc else v2.extraire_prereg_court)(fiche_projetee(bloc=bloc), TRANCHE_NS, 1, {})
        return p

    def test_consigne_de_l_experimentateur(self):
        c = v5.consigne_experimentateur(self.prereg(), "a" * 64, TRANCHE_NS, None, [], {"executions": 3, "tours": 12, "plafond_usd": 0.5},
                                        3, 120.0, 1024)
        for mot in ("`scores.csv`", "`score`", "« moyenne »", "≥ 0.3", "n'est qu'un témoin", "`CALCUL:` est ignorée",
                    "le noyau lit le fichier brut de ta dernière exécution réussie"):
            self.assertIn(mot, c)
        self.assertNotIn("est le chiffre lu", c)
        self.assertIn("est le chiffre lu", v2.consigne_experimentateur(self.prereg(), "a" * 64, TRANCHE_NS, None, [],
                                                                         {"executions": 3, "tours": 12, "plafond_usd": 0.5}, 3, 120.0, 1024))
        m = v5.consigne_experimentateur_maximale(self.prereg(), "a" * 64, TRANCHE_NS, None)
        self.assertGreater(len(m), len(c))
        self.assertIn("n'est qu'un témoin", m)

    def test_artefact_consigne_sans_bloc_refusee(self):
        with self.assertRaises(v4.PreregSansStatistique):
            v5.consigne_experimentateur(self.prereg(bloc=None), "a" * 64, TRANCHE_NS, None, [],
                                        {"executions": 3, "tours": 12, "plafond_usd": 0.5}, 3, 120.0, 1024)

    def test_consigne_du_lecteur_temoin(self):
        c = v5.consigne_lecteur(self.prereg(), "a" * 64, [], "b" * 64)
        self.assertIn("témoin, jamais décisive", c)
        self.assertIn("calculé par le noyau sur le fichier brut", c)


# --- la sélection entre générations (unités) --------------------------------------------------------------------------------------


def fiche_testee(ident, verdict, etiquette=v4.ETIQUETTE_NOYAU, verdict_noyau=None):
    vn = {"etiquette": etiquette, "verdict": verdict if verdict_noyau is None else verdict_noyau, "motif": f"motif {ident}"}
    return {"identifiant_auteur": ident, "statut": "testée", "verdict": verdict, "verdict_noyau": vn}


class TestSelectionEntreGenerations(unittest.TestCase):
    def test_cas_sain_survit_seulement_dans_l_ordre(self):
        resume = {"version_etage": v5.VERSION_ETAGE_V5, "par_fiche": [
            fiche_testee("f1", "non concluant"), fiche_testee("f2", "survit"), {"identifiant_auteur": "f3", "statut": "refusée à l'étage",
                                                                     "motif": "sans bloc"},
            fiche_testee("f4", "éliminée"), fiche_testee("f5", "survit")]}
        sel = e57.selection_entre_generations(resume)
        self.assertEqual(sel["retenues"], ["f2", "f5"])
        self.assertEqual([(x["identifiant_auteur"], x["verdict"]) for x in sel["exclues"]],
                         [("f1", "non concluant"), ("f3", None), ("f4", "éliminée")])
        self.assertIn("sans bloc", sel["exclues"][1]["motif"])
        self.assertEqual(e57.selection_entre_generations({"par_fiche": []})["retenues"], [])

    def test_artefacts_verdict_sans_etiquette_du_noyau_refuse(self):
        sain = fiche_testee("f1", "survit")
        v3_style = {"identifiant_auteur": "f2", "statut": "testée", "verdict": "survit", "fiabilite_du_chiffre": v2.ETIQUETTE_NON_RECALCULE}
        for nom, mauvais in (("étage v3 : aucun verdict du noyau", v3_style),
                             ("étiquette de la v2", fiche_testee("f2", "survit", etiquette=v2.ETIQUETTE_RECALCULE)),
                             ("verdict du noyau non objet", dict(fiche_testee("f2", "survit"), verdict_noyau="survit"))):
            with self.subTest(cas=nom), self.assertRaises(v4.VerdictNonNoyau):
                e57.selection_entre_generations({"par_fiche": [sain, mauvais]})
        with self.assertRaises(v4.VerdictInconnu):
            e57.selection_entre_generations({"par_fiche": [sain, fiche_testee("f2", "peut-être")]})
        for pas_un_resume in (None, {}, {"par_fiche": "f1"}):
            with self.subTest(resume=pas_un_resume), self.assertRaises(v4.VerdictNonNoyau):
                e57.selection_entre_generations(pas_un_resume)

    def test_artefact_verdict_affiche_different_du_verdict_du_noyau(self):
        with self.assertRaises(v4.VerdictNonNoyau) as cm:
            e57.selection_entre_generations({"par_fiche": [fiche_testee("f1", "survit", verdict_noyau="éliminée")]})
        self.assertIn("≠ verdict du noyau", str(cm.exception))


class TestJouerEtageV57(CasAvecDossier):
    def gen(self):
        return generation(os.path.join(self.tmp, "gen"), TRANCHE_NS, ["fA"])

    def test_artefact_machine_non_jetable_avant_tout_appel(self):
        g, ad = self.gen(), AdaptateurScripte(SCENARIOS)
        for env in ({"PATH": "/usr/bin"}, dict(JETABLE, CLE_API_ESSAI="x")):
            with self.subTest(env=sorted(env)), self.assertRaises(MachineNonJetable):
                e57.jouer_etage_v57(ad, g, reglages={}, environnement=env)
        self.assertEqual(ad.appels, [])
        self.assertFalse(os.path.exists(os.path.join(g, "noyau")))

    def test_artefact_etage_injecte_sans_verdict_du_noyau_rien_d_ecrit(self):
        def etage_v3_style(adaptateur, sortie, resume_sortie, **r):
            resume_sortie.update(par_fiche=[{"identifiant_auteur": "fA", "statut": "testée", "verdict": "survit"}], termine=True)
        g = self.gen()
        with self.assertRaises(v4.VerdictNonNoyau):
            e57.jouer_etage_v57(None, g, reglages={}, environnement=JETABLE, executer=etage_v3_style)
        self.assertFalse(os.path.exists(os.path.join(g, e57.NOM_SELECTION)))


# --- la course 2 v57 : l'étage entre générations passe par la sélection ----------------------------------------------------------


def double_etage(verdict_noyau):
    """Un double de l'étage (essai du câblage de la course) : chaque fiche du classement « testée » ; `verdict_noyau` (rang →
    verdict) donne un verdict à l'étiquette du noyau, ou None pour un verdict à la manière de la v3 (chiffre imprimé)."""
    def executer(adaptateur, sortie, resume_sortie, **reglages):
        lignes = lire(os.path.join(sortie, "classement.json"))["lignes"]
        par_fiche = []
        for k, l in enumerate(lignes):
            v = verdict_noyau(k)
            r = {"identifiant_auteur": l["identifiant_auteur"], "statut": "testée", "verdict": v or "survit"}
            if v is not None:
                r["verdict_noyau"] = {"etiquette": v4.ETIQUETTE_NOYAU, "verdict": v, "motif": "double de l'étage"}
            par_fiche.append(r)
        resume_sortie.update(par_fiche=par_fiche, termine=True, version_etage="double")
    return executer


class TestCourse2V57(CasAvecDossier):
    def conf(self):
        return cfg.lire_configuration_v56(A.configuration(self.tmp), base=self.tmp)

    def etage(self, **en_plus):
        if not hasattr(self, "_tranche"):
            self._tranche = creer_tranche(self.tmp)
        tr = self._tranche
        corr = {"nom": "titre", "enonce": "hypothese", "prediction": "hypothese", "signe": "axe", "metrique": "methode",
                "test_de_mort": "methode"}
        e = {"adaptateur": AdaptateurScripte({}), "reglages": reglages(tr, 2), "nombre": 2, "tranche_index_sha256": tr.index_sha256,
             "correspondance": corr, "plafond_etage_usd": 1.0}
        e.update(en_plus)
        return e

    def course(self, module, etage, nom="c"):
        fonction = c57.executer_course_v57 if module is c57 else c56.executer_course_v56
        return fonction(self.conf(), os.path.join(self.tmp, nom), A.adaptateurs(), nombre_generations=2, go={"essai": True},
                        etage=etage, environnement=JETABLE, racine_sessions=os.path.join(self.tmp, "sess-" + nom))

    def test_cas_sain_etage_v5_puis_selection_scellee(self):
        """L'étage réel v5 (chemin par défaut) sur la génération simulée : les fiches simulées n'ont pas de bloc
        `statistique` (ni de champ test_de_mort objet) : refusées à l'étage ; la sélection est écrite, vide, scellée."""
        bilan = self.course(c57, self.etage())
        self.assertEqual([l["generation"] for l in bilan], [1, 2])
        et = bilan[0]["etage"]
        self.assertEqual((et["version_etage"], et["termine"]), (v5.VERSION_ETAGE_V5, True))
        self.assertTrue(et["candidates"])
        self.assertEqual(et["selection"]["retenues"], [])
        self.assertEqual([x["identifiant_auteur"] for x in et["selection"]["exclues"]], et["candidates"])
        self.assertTrue(all("non testée" in x["motif"] and "statistique" in x["motif"] for x in et["selection"]["exclues"]))
        self.assertTrue(verifier_scelle(os.path.join(self.tmp, "c", "etage-apres-generation-1", e57.NOM_SELECTION)))
        b = lire(os.path.join(self.tmp, "c", "bilan-course.json"))
        self.assertEqual((b["version"], b["arret"]), (c57.VERSION, None))

    def test_survivante_retenue_au_bilan(self):
        bilan = self.course(c57, self.etage(executer=double_etage(lambda k: "survit" if k == 0 else "non concluant")))
        sel = bilan[0]["etage"]["selection"]
        premiere = lire(os.path.join(self.tmp, "c", "etage-apres-generation-1", "classement.json"))["lignes"][0]["identifiant_auteur"]
        self.assertEqual(sel["retenues"], [premiere])
        self.assertTrue(all(x["verdict"] == "non concluant" for x in sel["exclues"]))

    def test_artefact_verdict_de_l_etage_v3_refuse_course_arretee(self):
        with self.assertRaises(v4.VerdictNonNoyau):
            self.course(c57, self.etage(executer=double_etage(lambda k: None)))
        b = lire(os.path.join(self.tmp, "c", "bilan-course.json"))
        self.assertIn("VerdictNonNoyau", b["arret"])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "c", "generation-2")))
        # ce que la v56 faisait du même étage : aucun refus, aucune sélection
        bilan = self.course(c56, self.etage(executer=double_etage(lambda k: None)), nom="c56")
        self.assertEqual([l["generation"] for l in bilan], [1, 2])
        self.assertNotIn("selection", bilan[0]["etage"])


# --- empilement, sources (même chemin), R12 -------------------------------------------------------------------------------------


class TestEmpilementEtSources(unittest.TestCase):
    REDEFINIS = ("valider_champ_test", "GABARIT_TEST", "extraire_prereg_court", "consigne_experimentateur",
                 "consigne_experimentateur_maximale", "consigne_lecteur", "etiquette_materiau", "REGLE_ETAGE", "executer_tests_de_mort")

    def test_v5_rend_les_objets_de_la_v4_sauf_les_neuf_redefinis(self):
        publics = [n for n in vars(v4) if not n.startswith("_") and not isinstance(getattr(v4, n), types.ModuleType)]
        autres = [n for n in publics if n not in self.REDEFINIS]
        self.assertEqual([n for n in autres if getattr(v5, n) is not getattr(v4, n)], [])
        self.assertEqual([n for n in self.REDEFINIS if getattr(v5, n) is getattr(v4, n)], [])
        self.assertIs(v5.ExecuteurBacASable, v3.ExecuteurBacASable)  # le bac par défaut de l'étage v5 : celui de la v3
        self.assertEqual(v5.MEMOIRE_BAC_MIN_MO, 768)
        self.assertIs(v5.extraire_prereg_court, v4.extraire_prereg_court_v4)
        self.assertIs(v5.GABARIT_TEST, v4.GABARIT_TEST_V4)

    def test_meme_chemin_d_execution_que_la_v2_ligne_pour_ligne(self):
        a, b = inspect.getsource(v2.executer_tests_de_mort), inspect.getsource(v5.executer_tests_de_mort)
        for debut, fin in (('    valider_reglages(nombre, "x"', "    resume = resume_sortie if resume_sortie is not None else {}\n"),
                           ("    def lancer(role, etiquette", "    def jouer_fiche(ligne):\n"),
                           ("        # 1. préenregistrement court scellé AVANT", '        resultat["fin_des_tours"] = fin\n'),
                           ("    def ecrire_manifeste(erreur=None):", "        # matériau pour la génération suivante")):
            with self.subTest(bloc=debut.strip()[:40]):
                bloc = a[a.index(debut):a.index(fin) + len(fin)]
                self.assertGreater(bloc.count("\n"), 3)
                self.assertIn(bloc, b)
        self.assertNotIn("recalcul_noyau(", b)
        self.assertIn('resultat["verdict"] = noyau["verdict"]', b)

    def test_course_v57_est_la_v56_sauf_le_point_entre_generations(self):
        a, b = inspect.getsource(c56.executer_course_v56), inspect.getsource(c57.executer_course_v57)
        debut = "    if isinstance(nombre_generations, bool)"
        self.assertEqual(a[a.index(debut):].replace("jouer_etage_v56(", "jouer_etage_v57("), b[b.index(debut):])


class TestR12V57b(unittest.TestCase):
    def test_fichiers_publies_inchanges(self):
        """La v57 publiée garde ses sceaux ; les fichiers de la v56 sur lesquels la v57b s'appuie gardent leur empreinte de la
        liste v56."""
        for rel in ("pole/tests_de_mort_v4.py", "essais/test_v57_verdict_noyau.py", "essais/mutations_v57.py"):
            self.assertTrue(verifier_scelle(os.path.join(RACINE, rel)), rel)
        liste = {}
        with open(os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v56.txt"), encoding="utf-8") as f:
            for ligne in f:
                sha, rel = ligne.rstrip("\n").split("  ", 1)
                liste[rel] = sha
        for rel in ("pole/tests_de_mort_v2.py", "pole/tests_de_mort_v3.py", "pole/ideation_v2.py", "pole/course2_v56.py",
                    "pole/etage_entre_generations_v53.py", "pole/etage_entre_generations_v56.py"):
            self.assertEqual(sha256_fichier(os.path.join(RACINE, rel)), liste[rel], rel)
        for rel in ("pole/tests_de_mort_v5.py", "pole/etage_entre_generations_v57.py", "pole/course2_v57.py"):
            self.assertNotIn(rel, liste)


if __name__ == "__main__":
    unittest.main()
