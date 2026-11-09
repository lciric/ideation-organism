"""Essais du script de lecture de l'épreuve « W2 gradué » (`demonstrations/lecture_epreuve_w2g_dose_v1.py`, fichier neuf, R12) :
chaque garde du texte (§ 6) sur un cas sain et sur au moins un artefact (R5), un essai par code de sortie, Wilson contre des
valeurs calculées à la main.

Cas sains : deux **courses de chaîne** réelles du script de l'épreuve (sous-processus, `python3 -I -B`), 2 répétitions, les 11
doses de la grille gelée, `--duree-max-s 6700` (valeur retenue par la mère, R-1926), sous un texte factice scellé dans un dossier
temporaire : l'une à `--processus 1` (chemin séquentiel), l'autre à `--processus 2` (chemin du bassin de processus, celui du
rejeu) ; lues avec 2 répétitions, le nombre de processus de la course et `--duree-max-attendue 6700`. Un **vrai** code 3 : la même
course à `--duree-max-s 0.5` (arrêt écrit par le script). Artefacts : copies de la course séquentielle modifiées puis
**rescellées**, un dossier vide, une console d'autre code, et les sorties exploratoires (si leur dossier de brouillon existe
encore ; sinon l'essai est sauté et le dit). Aucun réseau, aucune clé, aucun proposeur. Durée totale ≈ 30 s.

Usage (depuis `orchestrator/` d'une copie du dépôt public au commit 8947bc8, patch v5 appliqué) :
    python3 -B essais/test_lecture_epreuve_w2g_dose_v1.py
"""

import contextlib
import importlib.util
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]

from pole import attaque_goodhart_v2 as ag  # noqa: E402
from pole import attaque_goodhart_v5 as a5  # noqa: E402
from pole.outils import ecrire_json_scelle, ecrire_scelle, sha256_fichier, verifier_scelle  # noqa: E402


def _charger(nom_fichier, nom):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, "demonstrations", nom_fichier))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


lecteur = _charger("lecture_epreuve_w2g_dose_v1.py", "lecture_epreuve_w2g_dose_v1_essai")

# Sorties exploratoires (texte § 3) : dossiers de brouillon de la session ; empreintes des sorties relevées au texte.
BROUILLON = "/tmp/claude-0/-home-user/86976e6f-3fae-57b1-a905-26802f445363/scratchpad"
EXPLORATOIRES = {"epreuve-w2g-v1-a": "c85e59b3594050e6c7ce162721e42c19b55d890acd752ef39b268617b279b2b9",
                 "epreuve-w2g-v1-b": "a4821262e5b9507d4275c81050af2034b3f9bdb0364b97513d30bdf2cb56748e"}
Z = 1.959963984540054


_COMMUN = {}


DUREE = 6700.0  # --duree-max-s du rejeu retenu par la mère (R-1926), passée au lecteur par --duree-max-attendue


def _course(tmp, texte, nom, processus, duree):
    """Course de chaîne du script de l'épreuve, comme la commande du texte (§ 4) : console avec une ligne « code N », scellée."""
    dossier = os.path.join(tmp, nom)
    commande = [sys.executable, "-I", "-B", os.path.join("demonstrations", "epreuve_w2g_dose_v1.py"), dossier,
                "--entropie-texte", texte, "--repetitions", "2", "--processus", str(processus), "--duree-max-s", str(duree)]
    p = subprocess.run(commande, cwd=RACINE, capture_output=True, text=True, timeout=600)
    console = os.path.join(tmp, nom + "-console.txt")
    ecrire_scelle(console, p.stdout + p.stderr + f"code {p.returncode}\n")
    return dossier, console, p.returncode


def setUpModule():
    """Trois courses de chaîne pour tous les essais ; chaque artefact est une copie rescellée de la course séquentielle."""
    tmp = tempfile.mkdtemp(prefix="lecture-w2g-")
    texte = os.path.join(tmp, "texte-factice-epreuve-w2g-v1.md")
    ecrire_scelle(texte, "Texte factice de la course de chaîne (essais du script de lecture) ; aucun chiffre lu.\n")
    chaine, console, code = _course(tmp, texte, "chaine", 1, DUREE)
    bassin, console_bassin, code_bassin = _course(tmp, texte, "chaine-bassin", 2, DUREE)
    coupee, console_coupee, code_coupee = _course(tmp, texte, "chaine-coupee", 1, 0.5)
    _COMMUN.update(tmp=tmp, texte=texte, chaine=chaine, console=console, code_chaine=code, bassin=bassin,
                   console_bassin=console_bassin, code_bassin=code_bassin, coupee=coupee, console_coupee=console_coupee,
                   code_coupee=code_coupee, n=0)


def tearDownModule():
    shutil.rmtree(_COMMUN["tmp"], ignore_errors=True)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for k in ("tmp", "texte", "chaine", "console", "code_chaine", "bassin", "console_bassin", "code_bassin", "coupee",
                  "console_coupee", "code_coupee"):
            setattr(cls, k, _COMMUN[k])

    def neuf(self, nom):
        _COMMUN["n"] += 1
        return os.path.join(self.tmp, f"{_COMMUN['n']:03d}-{nom}")

    def console_code(self, code):
        c = self.neuf("console.txt")
        ecrire_scelle(c, f"sortie factice\ncode {code}\n")
        return c

    def artefact(self, rapport=None, manifeste=None):
        """Copie de la course de chaîne ; `rapport(r)` et `manifeste(m)` modifient les JSON en place, puis rescellement."""
        d = self.neuf("sortie")
        shutil.copytree(self.chaine, d)
        for nom, f in (("epreuve-w2g-dose-v1.json", rapport), ("manifeste.json", manifeste)):
            if f is None:
                continue
            p = os.path.join(d, nom)
            with open(p, encoding="utf-8") as fh:
                o = json.load(fh)
            f(o)
            os.remove(p)
            os.remove(p + ".sha256")
            ecrire_json_scelle(p, o)
        return d

    def lire(self, dossier, console=None, texte=None, repetitions=2, processus=1, lecture=None, duree=DUREE):
        lecture = lecture or self.neuf("lecture.json")
        argv = [dossier, "--texte", texte or self.texte, "--console", console or self.console, "--lecture", lecture,
                "--repetitions-attendues", str(repetitions), "--processus-attendus", str(processus), "--duree-max-attendue", str(duree)]
        sortie, erreur = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreur):
            code = lecteur.principal(argv)
        contenu = None
        if os.path.isfile(lecture):
            self.assertTrue(verifier_scelle(lecture), "toute lecture écrite est scellée")
            with open(lecture, encoding="utf-8") as fh:
                contenu = json.load(fh)
        return code, contenu, sortie.getvalue() + erreur.getvalue()

    def refuse(self, dossier, garde, motif, premiere=None, **k):
        """Code 2 ; le couple (garde, motif) parmi les motifs rapportés ; la plus petite garde refusante = `premiere` (défaut :
        `garde`)."""
        code, contenu, texte = self.lire(dossier, **k)
        self.assertEqual(code, lecteur.CODE_GARDE, texte)
        self.assertEqual(contenu["garde"], garde if premiere is None else premiere, texte)
        self.assertIn((garde, motif), [(m["garde"], m["motif"]) for m in contenu["motifs"]], texte)
        self.assertEqual(contenu["gardes_refusees"], sorted({m["garde"] for m in contenu["motifs"]}))
        self.assertNotIn("par_dose", contenu, "arrêt de garde : aucun chiffre écrit")
        self.assertNotIn("lambda_etoile", contenu)
        return contenu


def _ligne(r, dose, cle):
    return next(x for x in r["resultats"] if x["dose"] == dose)["lignes"][cle]


def _poser(r, dose, cle, promues):
    x = _ligne(r, dose, cle)
    x["promues"], x["taux"] = promues, promues / x["repetitions"]


# --- Wilson à la main -----------------------------------------------------------------------------------------------------------
class Wilson(unittest.TestCase):
    def test_wilson_egale_le_calcul_a_la_main(self):
        """Formes closes : x = 0 → [0 ; z²/(n + z²)] ; x = n → [n/(n + z²) ; 1] ; x = n/2 → ½ ± z/(2·√(n + z²)) ; et 809/1 000
        contre la table du texte (§ 3, [0,783 ; 0,832] à trois décimales)."""
        z2 = Z * Z
        for n in (2, 200, 1000):
            lo, hi = lecteur.wilson(0, n)
            self.assertAlmostEqual(lo, 0.0, places=15)
            self.assertAlmostEqual(hi, z2 / (n + z2), places=12)
            lo, hi = lecteur.wilson(n, n)
            self.assertAlmostEqual(lo, n / (n + z2), places=12)
            self.assertAlmostEqual(hi, 1.0, places=12)
        lo, hi = lecteur.wilson(500, 1000)
        demi = Z / (2 * math.sqrt(1000 + z2))
        self.assertAlmostEqual(lo, 0.5 - demi, places=12)
        self.assertAlmostEqual(hi, 0.5 + demi, places=12)
        self.assertAlmostEqual(demi, 0.0309304, places=7)  # calcul à la main : 1,959964 / (2 × 31,683457) = 1,959964 / 63,366914
        self.assertEqual([round(v, 3) for v in lecteur.wilson(809, 1000)], [0.783, 0.832])
        self.assertAlmostEqual(lecteur.wilson(0, 1000)[1], 0.0038268, places=7)  # 3,841459 / 1 003,841459 = 0,00382676
        self.assertEqual(lecteur.wilson(3, 7), list(ag.wilson(3, 7)), "le lecteur appelle attaque_goodhart_v2.wilson")


class RegleDeChoix(unittest.TestCase):
    def test_lambda_recalcule_regle_du_texte(self):
        def r(dose, a, b, n=1000, complete=True):
            return {"dose": dose, "complete": complete, "lignes": {"monde|v9": {"promues": a, "repetitions": n},
                                                                    "recombinaison|v9": {"promues": b, "repetitions": n}}}
        self.assertEqual(lecteur.lambda_recalcule([r(0.0, 0, 0), r(0.3, 799, 0), r(0.4, 800, 0), r(0.5, 900, 0)]), 0.4)
        self.assertIsNone(lecteur.lambda_recalcule([r(0.0, 1000, 0)]), "la dose 0 n'est jamais choisissable")
        self.assertEqual(lecteur.lambda_recalcule([r(0.4, 800, 1), r(0.5, 900, 0)]), 0.5, "(b) > 0 : la dose ne convient pas")
        self.assertIsNone(lecteur.lambda_recalcule([r(0.4, 1000, 0, complete=False)]))
        self.assertEqual(lecteur.lambda_recalcule([r(0.5, 2, 0, n=2), r(0.4, 1, 0, n=2)]), 0.5, "1/2 < 0,80 ; ordre indifférent")


# --- cas sain et codes ---------------------------------------------------------------------------------------------------------
class CasSainEtCodes(Base):
    def test_cas_sain_course_de_chaine(self):
        self.assertEqual(self.code_chaine, 0, "la course de chaîne est complète")
        with open(os.path.join(self.chaine, "epreuve-w2g-dose-v1.json"), encoding="utf-8") as fh:
            r = json.load(fh)
        lecture = self.neuf("lecture.json")
        code, contenu, texte = self.lire(self.chaine, lecture=lecture)
        attendu = lecteur.CODE_LAMBDA if r["dose_proposee_par_la_regle"] is not None else lecteur.CODE_AUCUNE_DOSE
        self.assertEqual(code, attendu, texte)
        self.assertEqual(contenu["gardes"], {str(i): "passée" for i in range(1, 7)})
        self.assertEqual(contenu["lambda_recalcule"], r["dose_proposee_par_la_regle"])
        self.assertEqual([d["dose"] for d in contenu["par_dose"]], list(a5.GRILLE_DOSES_W2G))
        for d, x in zip(contenu["par_dose"], r["resultats"]):
            for k in lecteur.LIGNES:
                self.assertEqual(d["lignes"][k]["wilson_95"], list(ag.wilson(x["lignes"][k]["promues"], 2)))
                self.assertEqual(d["lignes"][k]["clopper_pearson_95_imprime"], x["lignes"][k]["clopper_pearson_95"])
        self.assertEqual(contenu["pieces"]["texte"]["sha256"], sha256_fichier(self.texte))
        self.assertEqual(contenu["pieces"]["sortie"]["sha256"], sha256_fichier(os.path.join(self.chaine, "epreuve-w2g-dose-v1.json")))
        self.assertIn(contenu["table"], texte, "la lecture est imprimée")
        # refus d'écraser : même chemin → usage, fichier inchangé
        avant = sha256_fichier(lecture)
        code2, _, _ = self.lire(self.chaine, lecture=lecture)
        self.assertEqual(code2, lecteur.CODE_USAGE)
        self.assertEqual(sha256_fichier(lecture), avant)

    def test_code_0_lambda_lu(self):
        def f(r):
            for d in r["doses"]:
                if d > 0:
                    _poser(r, d, "monde|v9", 2 if d >= 0.10 else 1)
            r["dose_proposee_par_la_regle"] = 0.1
        code, contenu, texte = self.lire(self.artefact(f))
        self.assertEqual(code, 0, texte)
        self.assertEqual((contenu["lambda_etoile"], contenu["lambda_imprime_par_le_script"]), (0.1, 0.1))
        self.assertIn("à la limite", contenu["a_la_limite"]["mention"], "2/2 : borne basse de Wilson 0,34 < 0,80")
        self.assertIn(contenu["p10"]["mention"], ("P10 tenue par l'oracle", "P10 en tension à λ*"))
        self.assertIn("λ* = 0.1", texte)

    def test_code_3_aucune_dose(self):
        def f(r):
            for d in r["doses"]:
                _poser(r, d, "monde|v9", 1 if d > 0 else 0)  # 1/2 < 0,80 partout
            r["dose_proposee_par_la_regle"] = None
        code, contenu, texte = self.lire(self.artefact(f))
        self.assertEqual(code, 3, texte)
        self.assertIsNone(contenu["lambda_etoile"])
        self.assertIn("nœud de Lazar", contenu["statut"])

    def test_code_4_usage(self):
        def argv(lecture=None, sans=(), **k):
            a = {"--texte": self.texte, "--console": self.console, "--lecture": lecture or self.neuf("l.json"),
                 "--repetitions-attendues": "2", "--processus-attendus": "1", "--duree-max-attendue": str(DUREE)}
            a.update(k)
            return [self.chaine] + [x for c, v in a.items() if c not in sans for x in (c, v)]
        with open(os.path.join(self.chaine, "epreuve-w2g-dose-v1.json"), encoding="utf-8") as fh:
            imprime = json.load(fh)["dose_proposee_par_la_regle"]
        sortie, erreur = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreur):
            temoin = lecteur.CODE_LAMBDA if imprime is not None else lecteur.CODE_AUCUNE_DOSE
            self.assertEqual(lecteur.principal(argv(self.neuf("temoin.json"))), temoin, "témoin valide")
            for sans in ("--texte", "--console", "--lecture", "--duree-max-attendue"):
                self.assertEqual(lecteur.principal(argv(sans=(sans,))), 4, f"{sans} absent")
            for k, v in (("--repetitions-attendues", "0"), ("--repetitions-attendues", "deux"), ("--processus-attendus", "0"),
                         ("--duree-max-attendue", "0"), ("--duree-max-attendue", "inf"), ("--duree-max-attendue", "nan")):
                self.assertEqual(lecteur.principal(argv(**{k: v})), 4, f"{k} {v}")
            dedans = os.path.join(self.chaine, "lecture.json")
            self.assertEqual(lecteur.principal(argv(dedans)), 4)
            self.assertFalse(os.path.exists(dedans), "rien n'est écrit dans le dossier scellé")
            pris = self.neuf("l.json")
            ecrire_scelle(pris + ".sha256", "x\n")
            self.assertEqual(lecteur.principal(argv(pris)), 4)
            self.assertFalse(os.path.exists(pris))

    def test_cas_sain_bassin_de_processus(self):
        """Cas sain sur le chemin du bassin de processus (`--processus 2`, celui du rejeu) ; refus si lu avec 1 processus attendu."""
        self.assertEqual(self.code_bassin, 0)
        with open(os.path.join(self.bassin, "epreuve-w2g-dose-v1.json"), encoding="utf-8") as fh:
            r = json.load(fh)
        code, contenu, texte = self.lire(self.bassin, console=self.console_bassin, processus=2)
        self.assertEqual(code, lecteur.CODE_LAMBDA if r["dose_proposee_par_la_regle"] is not None else lecteur.CODE_AUCUNE_DOSE, texte)
        self.assertEqual(contenu["gardes"], {str(i): "passée" for i in range(1, 7)})
        self.assertEqual([d["dose"] for d in contenu["par_dose"]], list(a5.GRILLE_DOSES_W2G))
        self.refuse(self.bassin, 3, "processus", console=self.console_bassin, processus=1)

    def test_code_2_arret_de_garde(self):
        """Un arrêt de garde rend 2 et écrit une lecture sans chiffre (motif nommé)."""
        c = self.refuse(self.artefact(lambda r: r.update(arret="durée maximale dépassée")), 2, "arret")
        self.assertEqual(c["code"], 2)
        self.assertNotIn("table", c)


# --- artefacts : une garde chacun ------------------------------------------------------------------------------------------------
class Garde1SortieAbsente(Base):
    def test_dossier_vide(self):
        d = self.neuf("vide")
        os.makedirs(d)
        self.refuse(d, 1, "sortie_absente")

    def test_manifeste_absent(self):
        d = self.artefact()
        os.remove(os.path.join(d, "manifeste.json"))
        self.refuse(d, 1, "sortie_absente")

    def test_compagnon_non_conforme(self):
        d = self.artefact()
        with open(os.path.join(d, "epreuve-w2g-dose-v1.json"), "a", encoding="utf-8") as fh:
            fh.write(" ")
        self.refuse(d, 1, "compagnon")

    def test_illisible(self):
        d = self.artefact()
        p = os.path.join(d, "epreuve-w2g-dose-v1.json")
        os.remove(p)
        os.remove(p + ".sha256")
        ecrire_scelle(p, '{"epreuve": NaN}\n')
        self.refuse(d, 1, "illisible")

    def test_forme(self):
        self.refuse(self.artefact(lambda r: r["resultats"][2]["lignes"].pop("recombinaison|ancien")), 1, "forme")
        self.refuse(self.artefact(lambda r: _ligne(r, 0.5, "monde|v9").update(taux=0.123)), 1, "forme")

    def test_table_differente(self):
        self.refuse(self.artefact(lambda r: r.update(table=r["table"] + " ")), 1, "table")

    def test_code_de_sortie(self):
        self.refuse(self.chaine, 1, "code_de_sortie", console=self.console_code(2))
        self.refuse(self.chaine, 1, "illisible", console=self.console_code("0\ncode 0"))


class Garde2Duree(Base):
    def test_arret_non_nul(self):
        self.refuse(self.artefact(lambda r: r.update(arret="dose 0.4 : durée maximale dépassée à la répétition 1")), 2, "arret")

    def test_vrai_code_3(self):
        """Course de chaîne à `--duree-max-s 0.5` : code 3 réel, `arret` écrit par le script, doses absentes ou incomplètes."""
        self.assertEqual(self.code_coupee, 3)
        c = self.refuse(self.coupee, 2, "code_3", console=self.console_coupee)
        motifs = {(m["garde"], m["motif"]) for m in c["motifs"]}
        self.assertIn((2, "arret"), motifs)
        self.assertTrue({(2, "dose_absente"), (2, "dose_incomplete")} & motifs, motifs)
        self.assertIn((3, "duree_max"), motifs, "0,5 s ≠ 6 700 s attendues")

    def test_dose_nulle_retiree(self):
        """Artefact « dose 0 retirée de `resultats` » (M-3) : le champ `doses` garde la grille ; la dose est absente."""
        c = self.refuse(self.artefact(lambda r: r["resultats"].pop(0)), 2, "dose_absente")
        self.assertIn("[0.0]", next(m["detail"] for m in c["motifs"] if m["motif"] == "dose_absente"))

    def test_dose_retiree_partout(self):
        """Dose 0,05 retirée de `resultats`, de `doses` et de `reglages.doses` (cohérents entre eux) : absente (2) et grille (3)."""
        def f(r):
            r["doses"] = [d for d in r["doses"] if d != 0.05]
            r["resultats"] = [x for x in r["resultats"] if x["dose"] != 0.05]
        self.refuse(self.artefact(f, lambda m: m["reglages"].update(doses=[d for d in m["reglages"]["doses"] if d != 0.05])),
                    2, "dose_absente")

    def test_repetitions_d_une_ligne(self):
        """Une ligne à `repetitions` différente de sa dose : forme (1) ; dose entière à 3 sur 2 attendues : incomplète (2)."""
        self.refuse(self.artefact(lambda r: _ligne(r, 0.3, "monde|v8_information").update(repetitions=3)), 1, "forme")

        def f(r):
            x = next(y for y in r["resultats"] if y["dose"] == 0.3)
            x["repetitions"] = 3
            for v in x["lignes"].values():
                v["repetitions"], v["taux"] = 3, v["promues"] / 3
        self.refuse(self.artefact(f), 2, "dose_incomplete")

    def test_code_3_et_124(self):
        self.refuse(self.chaine, 2, "code_3", console=self.console_code(3))
        self.refuse(self.chaine, 2, "delai_externe", console=self.console_code(124))

    def test_dose_incomplete(self):
        def f(r):
            x = r["resultats"][4]
            x["complete"] = False
        self.refuse(self.artefact(f), 2, "dose_incomplete")

    def test_dose_manquante(self):
        self.refuse(self.artefact(lambda r: r["resultats"].pop(5)), 2, "dose_manquante")


class Garde3Graine(Base):
    def test_texte_autre(self):
        autre = self.neuf("autre-texte.md")
        ecrire_scelle(autre, "un autre texte\n")
        c = self.refuse(self.chaine, 3, "entropie", texte=autre)
        self.assertIn("texte_sha256", [m["motif"] for m in c["motifs"]])

    def test_texte_non_scelle(self):
        nu = self.neuf("texte-nu.md")
        shutil.copyfile(self.texte, nu)
        self.refuse(self.chaine, 3, "texte_non_scelle", texte=nu)

    def test_mode_exploratoire(self):
        def f(r):
            r["mode"] = "exploratoire (non décisif)"
        self.refuse(self.artefact(f, lambda m: m["reglages"].update(mode="exploratoire (non décisif)")), 3, "mode")

    def test_grille_reduite(self):
        garder = [0.3, 0.4, 0.5, 0.75]

        def f(r):
            r["doses"] = garder
            r["resultats"] = [x for x in r["resultats"] if x["dose"] in garder]
        self.refuse(self.artefact(f, lambda m: m["reglages"].update(doses=garder)), 3, "grille", premiere=2)

    def test_repetitions_et_processus(self):
        self.refuse(self.chaine, 3, "repetitions", premiere=2, repetitions=1000)
        self.refuse(self.chaine, 3, "processus", processus=4)

    def test_coherence_des_deux_fichiers(self):
        """M-4 : chaque champ comparé entre `epreuve-w2g-dose-v1.json` et `manifeste.json` (`reglages.*`)."""
        self.refuse(self.artefact(manifeste=lambda m: m["reglages"].update(entropie_racine=str(2 ** 70))), 3, "incoherence_fichiers")
        self.refuse(self.artefact(lambda r: r.update(repetitions=3)), 3, "incoherence_fichiers")
        self.refuse(self.artefact(manifeste=lambda m: m["reglages"].update(mode="décisif")), 3, "incoherence_fichiers")

    def test_regle_de_choix(self):
        """`regle_de_choix` (0,8 ; 0) comparée au fichier de résultats et à `reglages.regle_de_choix`."""
        def seuil(o, v):
            o["seuil_promotion_monde_v9"] = v
        self.refuse(self.artefact(lambda r: seuil(r["regle_de_choix"], 0.7), lambda m: seuil(m["reglages"]["regle_de_choix"], 0.7)),
                    3, "regle")
        self.refuse(self.artefact(manifeste=lambda m: m["reglages"]["regle_de_choix"].update(promotions_recombinaison_v9_max=1)),
                    3, "regle")
        c = self.refuse(self.artefact(lambda r: r["regle_de_choix"].update(seuil_promotion_monde_v9=True)), 3, "regle")
        self.assertIn("incoherence_fichiers", [m["motif"] for m in c["motifs"]])

    def test_texte_chemin(self):
        self.refuse(self.artefact(manifeste=lambda m: m["reglages"]["texte"].update(chemin="/ailleurs/texte.md")), 3, "texte_chemin")

    def test_empreinte_de_module_changee(self):
        def m(o):
            o["reglages"]["modules_sha256"]["pole/attaque_goodhart_v5.py"] = "0" * 64
        c = self.refuse(self.artefact(manifeste=m), 3, "modules")
        self.assertIn("pole/attaque_goodhart_v5.py", c["motifs"][0]["detail"])

    def test_duree_et_versions(self):
        self.refuse(self.artefact(manifeste=lambda o: o["reglages"].update(duree_max_s=6300.0)), 3, "duree_max")
        self.refuse(self.chaine, 3, "duree_max", duree=6300.0)
        self.refuse(self.artefact(manifeste=lambda o: o["reglages"].update(numpy="2.4.0")), 3, "versions")

    def test_sorties_exploratoires(self):
        """Les sorties exploratoires (texte § 3) refusent : graine non dérivée, grille réduite."""
        vus = 0
        for nom, empreinte in EXPLORATOIRES.items():
            d = os.path.join(BROUILLON, nom)
            if not os.path.isfile(os.path.join(d, "epreuve-w2g-dose-v1.json")):
                continue
            self.assertEqual(sha256_fichier(os.path.join(d, "epreuve-w2g-dose-v1.json")), empreinte)
            vus += 1
            c = self.refuse(d, 3, "mode", premiere=2, console=self.console_code(0), repetitions=1000, processus=2, duree=3300.0)
            motifs = [m["motif"] for m in c["motifs"]]
            for attendu in ("entropie", "texte_sha256", "texte_chemin", "entropie_sous_2_64", "grille"):
                self.assertIn(attendu, motifs, nom)
            self.assertIn("dose_absente", motifs, nom)
        if not vus:
            self.skipTest(f"sorties exploratoires absentes de {BROUILLON} (dossiers de brouillon effacés)")


class Garde4Verite(Base):
    def test_cle_verite(self):
        self.refuse(self.artefact(lambda r: r["resultats"][3].update(verite={"dose": 0.15})), 4, "cle_verite")
        self.refuse(self.artefact(manifeste=lambda m: m.update({"vérité": 1})), 4, "cle_verite")

    def test_egalite_de_nom_pas_sous_chaine(self):
        """Cas sain de la garde 4 : « N » et « vérité » dans des valeurs, ou dans un nom plus long, ne refusent pas."""
        self.assertEqual(lecteur.cles_interdites({"a": "N vérité", "b": ["verite", "N"], "verite_servie": 1, "Nom": 2, "n": 3}), [])
        self.assertEqual([k for k, _ in lecteur.cles_interdites({"x": [{"Vérité": 1}], "y": {"N": 0}})], ["Vérité", "N"])
        with open(os.path.join(self.chaine, "manifeste.json"), encoding="utf-8") as fh:
            m = json.load(fh)
        self.assertIn("N", m["reglages"]["monde_w2g"], "le manifeste contient « N » dans une valeur descriptive")
        self.assertEqual(lecteur.cles_interdites(m), [])

    def test_cle_N(self):
        self.refuse(self.artefact(lambda r: r["resultats"][7]["lignes"]["monde|v9"].update(N={"type": "softmax"})), 4, "cle_N")


class Garde5Certificat(Base):
    def test_recombinaison_promue(self):
        self.refuse(self.artefact(lambda r: _poser(r, 0.5, "recombinaison|v9", 1)), 5, "recombinaison_promue")

    def test_monde_promu_a_dose_nulle(self):
        self.refuse(self.artefact(lambda r: _poser(r, 0.0, "monde|v9", 1)), 5, "monde_promu_dose_0")


class Garde6Instrument(Base):
    def test_dose_nulle_proposee(self):
        """`choisir_dose` n'exclut pas la dose 0 : un λ* imprimé égal à 0 est un désaccord (garde 6)."""
        c = self.refuse(self.artefact(lambda r: r.update(dose_proposee_par_la_regle=0.0)), 6, "lambda_dose_nulle")
        self.assertIn("desaccord_lambda", [m["motif"] for m in c["motifs"]])

    def test_grammaire_refusee(self):
        self.refuse(self.artefact(lambda r: r["resultats"][6].update(grammaire_servie_refusee=1)), 6, "grammaire_refusee")

    def test_desaccord_lambda(self):
        def f(r):
            imprime = r["dose_proposee_par_la_regle"]
            r["dose_proposee_par_la_regle"] = 0.05 if imprime != 0.05 else 0.1
        self.refuse(self.artefact(f), 6, "desaccord_lambda")

    def test_cle_absente_du_cas_sain(self):
        """Cas sain des gardes 4 à 6 : la course de chaîne n'a ni clé de vérité, ni (b) > 0, ni grammaire refusée."""
        with open(os.path.join(self.chaine, "epreuve-w2g-dose-v1.json"), encoding="utf-8") as fh:
            r = json.load(fh)
        self.assertEqual(lecteur.cles_interdites(r), [])
        self.assertTrue(all(x["lignes"]["recombinaison|v9"]["promues"] == 0 for x in r["resultats"]))
        self.assertTrue(all(x["grammaire_servie_refusee"] == 0 for x in r["resultats"]))
        self.assertEqual(lecteur.lambda_recalcule(r["resultats"]), r["dose_proposee_par_la_regle"])


if __name__ == "__main__":
    unittest.main()
