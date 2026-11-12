"""Essais du code v67 (écart 1 au texte scellé de la course réelle, option 2 : délai de la configuration passé à l'adaptateur,
garde 24, blocs v67) : chaque garde touchée sur un cas sain et sur un artefact (R5). Aucun réseau, aucune clé, aucun appel de
modèle.

Deux parties :
1. **La suite du lanceur v66 rejouée contre le lanceur v67** : `essais/test_boucle_reelle_v66.py` est chargé une seconde fois sous
   un autre nom (le module des essais v66 lui-même reste intact et lié au lanceur v66), son `LANCEUR` remplacé par le lanceur
   v67 et sa configuration d'exemple par la v8 ; toutes ses classes sont rejouées ici **sous leurs noms v66** (les sélections `-k` du banc v66 s'y appliquent telles quelles), sauf trois essais remplacés parce qu'ils
   visent un nom que la v67 change (`L64.roles_reels` → `roles_reels_v67` ; fermeture partant du lanceur v67).
2. **Essais neufs** : garde 24, `commandes_v67`, délai effectivement passé au processus, rôles réels v67, branche réelle avec la
   garde 24, blocs v66 et v67 non interchangeables, fichier d'exemple v8.

  POLE_ESSAI_BAC_REEL_NON_JOUE=1 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_boucle_reelle_v67.py
"""

import copy
import importlib.util
import io
import json
import os
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

from pole import adaptateur_commande_v64 as AC64  # noqa: E402
from pole import adaptateur_commande_v67 as AC67  # noqa: E402
from pole import adaptateurs as AD  # noqa: E402
from pole import boucle_reelle_v65 as B65  # noqa: E402
from pole import boucle_reelle_v66 as B  # noqa: E402
from pole.adaptateurs_v56 import AdaptateurCommandeExterneV56, porte_depuis_configuration  # noqa: E402
from pole.outils import sha256_fichier  # noqa: E402


def _charger(nom, rel):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LANCEUR = _charger("lanceur_boucle_reelle_v67_essais", "demonstrations/boucle_reelle_v67.py")
LANCEUR_V66 = _charger("lanceur_boucle_reelle_v66_pour_essais_v67", "demonstrations/boucle_reelle_v66.py")
CONF_V8 = os.path.join(RACINE, "exemples", "configuration-boucle-reelle-v8.json")
CONF_V6 = os.path.join(RACINE, "exemples", "configuration-boucle-reelle-v6.json")

# --- 1. la suite du lanceur v66, rejouée contre le lanceur v67 -----------------------------------------------------------------

E66 = _charger("essais_boucle_reelle_v66_pour_v67", "essais/test_boucle_reelle_v66.py")
E66.LANCEUR = LANCEUR
E66.CONF_V6 = CONF_V8
_lancer, _plan, _ecrire_texte, _dossier_de_configuration = E66._lancer, E66._plan, E66._ecrire_texte, E66._dossier_de_configuration
_roles_a_blanc, DESCRIPTION_SAINE = E66._roles_a_blanc, E66.DESCRIPTION_SAINE

JugeV66 = E66.JugeV66
JugementsAuReleve = E66.JugementsAuReleve
VueServie = E66.VueServie
Garde7EtCopies = E66.Garde7EtCopies
BrasGenerationsFamilles = E66.BrasGenerationsFamilles
Depense = E66.Depense
Gardes17Et19 = E66.Gardes17Et19
PlanEtTexte = E66.PlanEtTexte
Machine = E66.Machine
Mesures = E66.Mesures
EssaiABlanc = E66.EssaiABlanc


class ConfigurationV6(E66.ConfigurationV6):
    """Les essais de la configuration v6, sur l'exemple v8 (mêmes commandes v6, mêmes pièces, mêmes chemins relatifs)."""


class BrancheReelle(E66.BrancheReelle):
    """La branche réelle v66 rejouée ; les deux essais qui remplaçaient `L64.roles_reels` visent `roles_reels_v67`."""

    def test_garde_22_cablee_identite_du_bac_puis_garde_15_avant_les_portes(self):
        appels_roles = []

        def roles_reels(*a, **k):
            appels_roles.append(a)
            raise AssertionError("portes posées avant les gardes")

        def bac(description):
            return lambda b, u, which=None: (None, lambda: (None, description), description)
        sentinelle = RuntimeError("SENTINELLE-GARDE-15")
        with mock.patch.object(LANCEUR, "version_bwrap", lambda *a, **k: (0, 9)), \
                mock.patch.object(LANCEUR, "roles_reels_v67", roles_reels), \
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
        appels = []

        def roles_reels(conf, plan, base, sortie, transmettre=True):
            appels.append({"transmettre": transmettre, "commande_kimi": conf["fournisseurs"]["kimi"]["commande"][3]})
            p, e, r = _roles_a_blanc()
            return p, e, r, {"doublures": True}
        with mock.patch.object(LANCEUR, "version_bwrap", lambda *a, **k: (0, 9)), mock.patch.object(os, "geteuid", lambda: 0), \
                mock.patch.object(LANCEUR, "preparer_bac_v66", lambda b, u, which=None: (None, lambda: (None, DESCRIPTION_SAINE), DESCRIPTION_SAINE)), \
                mock.patch.object(LANCEUR.L64, "exiger_machine_jetable_reel", lambda env, conf: ()), \
                mock.patch.object(LANCEUR, "roles_reels_v67", roles_reels), \
                mock.patch.object(B.ReleveDeJetons, "instrumenter", autospec=True, side_effect=lambda self, ad, relais: appels.append(relais) or ad):
            code, err = self.lancer("--verifier-seulement")
        self.assertEqual(code, 0, err)
        self.assertEqual(appels[0], {"transmettre": False, "commande_kimi": os.path.realpath(os.path.join(self.conf_dir, "commandes-v6", "commande_kimi_v6.py"))})
        self.assertEqual(sorted(appels[1:]), ["argon", "argon", "kimi", "kimi"])


class Fermeture(unittest.TestCase):
    def test_bloc_gele_egal_a_la_fermeture_statique(self):
        t64 = _charger("essais_tour_ferme_v64_pour_v67", "essais/test_tour_ferme_v64.py")
        ferm, pile = set(), ["demonstrations/boucle_reelle_v67.py", "demonstrations/lire_boucle_reelle_v66.py"]
        while pile:
            x = pile.pop()
            if x not in ferm:
                ferm.add(x)
                pile += sorted(t64.imports_de(x) - ferm)
        ferm |= {"demonstrations/tour_ferme_v64.py"} | t64.fermeture_statique()  # lanceur v64 chargé par chemin
        self.assertEqual(sorted(ferm), sorted(LANCEUR.FICHIERS_GELES))
        self.assertIn("pole/adaptateur_commande_v67.py", LANCEUR.FICHIERS_GELES)
        self.assertNotIn("demonstrations/boucle_reelle_v66.py", LANCEUR.FICHIERS_GELES)
        self.assertEqual(len(LANCEUR.FICHIERS_GELES), 99)


# --- 2. essais neufs -----------------------------------------------------------------------------------------------------------


def _conf(chemin=CONF_V8):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def _poser_delai_commande(conf, nom, valeur):
    c = conf["fournisseurs"][nom]["commande"]
    c[c.index("--delai-s") + 1] = valeur


class Garde24(unittest.TestCase):
    def test_sain_v8(self):
        self.assertEqual(AC67.verifier_delais_v67(_conf()), {"kimi": {"adaptateur_s": 7200.0, "commande_s": 7150.0},
                                                              "argon": {"adaptateur_s": 1800.0, "commande_s": 1750.0}})

    def test_sain_bornes_exactes(self):
        conf = _conf()
        conf["fournisseurs"]["kimi"]["delai_s"] = 7200
        _poser_delai_commande(conf, "kimi", "7170")  # marge de 30 s exactement
        self.assertEqual(AC67.verifier_delais_v67(conf)["kimi"], {"adaptateur_s": 7200.0, "commande_s": 7170.0})

    def test_sain_entree_d_un_autre_type_ignoree(self):
        conf = _conf()
        conf["fournisseurs"]["argon"] = {"type": "kimi_protocole"}
        self.assertEqual(set(AC67.verifier_delais_v67(conf)), {"kimi"})

    def test_artefacts(self):
        def k(f):
            def g(conf):
                f(conf["fournisseurs"]["kimi"])
            return g

        def sans_option(f):
            i = f["commande"].index("--delai-s")
            del f["commande"][i:i + 2]
        cas = {
            "délai absent": k(lambda f: f.pop("delai_s")),
            "délai nul": k(lambda f: f.__setitem__("delai_s", 0)),
            "délai négatif": k(lambda f: f.__setitem__("delai_s", -5)),
            "délai booléen": k(lambda f: f.__setitem__("delai_s", True)),
            "délai en chaîne": k(lambda f: f.__setitem__("delai_s", "7200")),
            "délai infini": k(lambda f: f.__setitem__("delai_s", float("inf"))),
            "délai au-delà de 7 200 s": k(lambda f: f.__setitem__("delai_s", 7201)),
            "option absente": k(sans_option),
            "option en double": k(lambda f: f["commande"].extend(["--delai-s", "10"])),
            "option sans valeur": k(lambda f: (sans_option(f), f["commande"].append("--delai-s"))),
            "valeur non numérique": lambda c: _poser_delai_commande(c, "kimi", "beaucoup"),
            "valeur nan": lambda c: _poser_delai_commande(c, "kimi", "nan"),
            "valeur nulle": lambda c: _poser_delai_commande(c, "kimi", "0"),
            "valeur non chaîne": lambda c: _poser_delai_commande(c, "kimi", 7150),
            "commande égale à l'adaptateur": lambda c: _poser_delai_commande(c, "kimi", "7200"),
            "commande au-delà de l'adaptateur": lambda c: _poser_delai_commande(c, "kimi", "9000"),
            "marge de 29 s": lambda c: _poser_delai_commande(c, "kimi", "7171"),
            "Argon : commande à la valeur de l'adaptateur": lambda c: _poser_delai_commande(c, "argon", "1800"),
            "commande absente": k(lambda f: f.pop("commande")),
        }
        for nom, f in cas.items():
            with self.subTest(nom):
                conf = _conf()
                f(conf)
                with self.assertRaises(AC67.DelaiRefuse):
                    AC67.verifier_delais_v67(conf)


def _adaptateurs_v56(conf):
    ads = {n: AdaptateurCommandeExterneV56(conf["fournisseurs"][n]["commande"], delai_s=float(conf["fournisseurs"][n]["delai_s"]),
                                           exiger_modele_servi=True) for n in ("kimi", "argon")}
    portes = {n: porte_depuis_configuration(n, conf["fournisseurs"][n].get("porte_plafond"), ads[n]) for n in ads}
    return ads, portes


class CommandesV67(unittest.TestCase):
    def test_sain_delai_de_la_configuration(self):
        conf = _conf()
        ads, portes = _adaptateurs_v56(conf)
        a2, p2 = AC67.commandes_v67(conf, ads, portes)
        self.assertIsInstance(a2["kimi"], AC64.AdaptateurCommandeExterneV64)
        self.assertEqual((a2["kimi"].delai_s, a2["argon"].delai_s), (7200.0, 1800.0))
        self.assertEqual(a2["kimi"].description()["delai_s"], 7200.0)
        self.assertTrue(a2["kimi"].exiger_modele_servi)
        self.assertEqual(a2["kimi"].commande, conf["fournisseurs"]["kimi"]["commande"])
        self.assertEqual(set(p2), {"kimi", "argon"})
        self.assertIsNot(a2["kimi"], ads["kimi"])

    def test_constat_la_v64_ignorait_le_delai(self):
        """Le défaut que corrige la v67 (écart 1, section 2), joué : la v64 rend 1 800 s quel que soit le délai de la configuration."""
        conf = _conf()
        ads, portes = _adaptateurs_v56(conf)
        a64, _ = AC64.commandes_v64(conf, ads, portes)
        self.assertEqual(a64["kimi"].delai_s, float(AD.AdaptateurCommandeExterne.DELAI_COMMANDE_S))
        self.assertEqual(a64["kimi"].delai_s, 1800.0)

    def test_artefact_garde_24_avant_tout_remplacement(self):
        conf = _conf()
        ads, portes = _adaptateurs_v56(conf)
        _poser_delai_commande(conf, "kimi", "7190")
        with self.assertRaises(AC67.DelaiRefuse):
            AC67.commandes_v67(conf, ads, portes)

    def test_artefact_relais_non_commande(self):
        conf = _conf()
        ads, portes = _adaptateurs_v56(conf)
        ads["kimi"] = object()
        with self.assertRaises(AC64.RelaisNonCommande):
            AC67.commandes_v67(conf, ads, portes)

    def test_entree_d_un_autre_type_laissee(self):
        conf = _conf()
        ads, portes = _adaptateurs_v56(conf)
        conf["fournisseurs"]["argon"] = {"type": "kimi_protocole"}
        a2, _ = AC67.commandes_v67(conf, ads, portes)
        self.assertIs(a2["argon"], ads["argon"])
        self.assertEqual(a2["kimi"].delai_s, 7200.0)


ENV_PROPRE = {"PATH": "/usr/bin:/bin", "HOME": "/root", "LANG": "C.UTF-8", "TMPDIR": tempfile.gettempdir()}


class DelaiPasseAuProcessus(unittest.TestCase):
    """Le délai de la configuration arrive jusqu'à `Popen.communicate(timeout=…)` de la classe gelée (`pole/adaptateurs.py`)."""

    def _lancer_avec(self, ad):
        vus = []

        class FauxProcessus:
            pid, returncode = 999999, 0

            def __init__(self, *a, **k):
                pass

            def communicate(self, input=None, timeout=None):
                vus.append(timeout)
                ligne = {"texte": "ok", "cout_usd": 0.001, "modele_servi": "kimi-k3.1-pro"}
                return (json.dumps(ligne) + "\n").encode(), b""
        with mock.patch.object(subprocess, "Popen", FauxProcessus), mock.patch.dict(os.environ, ENV_PROPRE, clear=True):
            r = ad.lancer("proposeur_ideation", "consigne", tempfile.mkdtemp(), 1.5, 1, modele="kimi-k3.1-pro")
        return vus, r

    def test_sain_7200_pour_kimi_1800_pour_argon(self):
        conf = _conf()
        a2, _ = AC67.commandes_v67(conf, *_adaptateurs_v56(conf))
        vus, r = self._lancer_avec(a2["kimi"])
        self.assertEqual(vus, [7200.0])
        self.assertEqual(r.statut, "ok")
        vus, _ = self._lancer_avec(a2["argon"])
        self.assertEqual(vus, [1800.0])

    def test_artefact_v64_1800(self):
        conf = _conf()
        a64, _ = AC64.commandes_v64(conf, *_adaptateurs_v56(conf))
        vus, _ = self._lancer_avec(a64["kimi"])
        self.assertEqual(vus, [1800.0])

    def test_sain_vraie_commande_courte_sous_le_delai(self):
        """Une vraie commande locale (aucun réseau) sous un délai de configuration de 40 s : réponse lue, aucun arrêt."""
        script = os.path.join(tempfile.mkdtemp(), "c.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write("import json,sys\nsys.stdin.read()\nprint(json.dumps({'texte':'ok','cout_usd':0.001,'modele_servi':'kimi-k3.1-pro'}))\n")
        conf = _conf()
        conf["fournisseurs"]["kimi"]["commande"] = [sys.executable, "-I", "-B", script, "--delai-s", "5"]
        conf["fournisseurs"]["kimi"]["delai_s"] = 40
        a2, _ = AC67.commandes_v67(conf, *_adaptateurs_v56(conf))
        self.assertEqual(a2["kimi"].delai_s, 40.0)
        with mock.patch.dict(os.environ, ENV_PROPRE, clear=True):
            r = a2["kimi"].lancer("proposeur_ideation", "consigne", tempfile.mkdtemp(), 1.5, 1, modele="kimi-k3.1-pro")
        self.assertEqual(r.statut, "ok", r.erreur)

    def test_artefact_vraie_commande_tuee_au_delai_de_l_adaptateur(self):
        """La classe gelée tue la commande au délai reçu (ici 1 s, posé directement : la garde 24 refuserait cette configuration)."""
        script = os.path.join(tempfile.mkdtemp(), "c.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write("import time,sys\nsys.stdin.read()\ntime.sleep(20)\n")
        ad = AC64.AdaptateurCommandeExterneV64([sys.executable, "-I", "-B", script], delai_s=1.0, exiger_modele_servi=True)
        with mock.patch.dict(os.environ, ENV_PROPRE, clear=True):
            r = ad.lancer("proposeur_ideation", "consigne", tempfile.mkdtemp(), 1.5, 1, modele="kimi-k3.1-pro")
        self.assertEqual(r.statut, "erreur")
        self.assertIn("délai de 1 s dépassé", r.erreur)


class RolesReelsV67(unittest.TestCase):
    PLAN = {"plafond_usd": 40.0, "parts": {"kimi": 33.0, "argon": 7.0}}

    def _roles(self, retouche=None, environ=None):
        d = tempfile.mkdtemp(prefix="roles-reels-v67-")
        chemin = _dossier_de_configuration(d, retouche)
        from pole import configuration_v56 as cfg
        conf = cfg.lire_configuration_v56(chemin)
        _, resolue = LANCEUR.verifier_configuration_v66(conf, LANCEUR.lire_plan(_plan()), d)
        env = environ or ENV_PROPRE
        with mock.patch.dict(os.environ, env, clear=True):
            return resolue, LANCEUR.roles_reels_v67(resolue, self.PLAN, tempfile.mkdtemp(), tempfile.mkdtemp(), transmettre=False)

    def test_sain_delais_aux_adaptateurs_aucune_porte(self):
        _, (proposeurs, etage, roles, infos) = self._roles()
        self.assertEqual(infos["adaptateurs"]["kimi"]["delai_s"], 7200.0)
        self.assertEqual(infos["adaptateurs"]["argon"]["delai_s"], 1800.0)
        self.assertEqual(infos["commandes"], AC67.VERSION)
        self.assertEqual(infos["accuses_plafond"], "non relancées (vérification seule)")
        self.assertEqual(infos["budget_appel_usd"], 1.5)
        self.assertEqual([p.ad.delai_s for p in proposeurs], [7200.0, 1800.0])
        self.assertEqual(etage.roles[LANCEUR.T.v5.ROLE_EXPERIMENTATEUR][0].delai_s, 7200.0)

    def test_constat_roles_reels_v64_1800(self):
        resolue, _ = self._roles()
        with mock.patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}, clear=True):
            _, _, _, infos = LANCEUR.L64.roles_reels(resolue, self.PLAN, tempfile.mkdtemp(), tempfile.mkdtemp(), transmettre=False)
        self.assertEqual(infos["adaptateurs"]["kimi"]["delai_s"], 1800.0)

    def test_artefact_garde_24_dans_les_roles(self):
        with self.assertRaisesRegex(LANCEUR.T.TourRefuse, "garde 24"):
            self._roles(lambda c: _poser_delai_commande(c, "kimi", "7199"))

    def test_artefact_variable_de_cle(self):
        with self.assertRaisesRegex(LANCEUR.T.TourRefuse, "variables de clé"):
            self._roles(environ=dict(ENV_PROPRE, OPENAI_API_KEY="factice"))


class ConfigurationEtGarde24AuLanceur(unittest.TestCase):
    PLAN = LANCEUR.lire_plan(_plan())

    def test_sain_v8(self):
        from pole import configuration_v56 as cfg
        d = tempfile.mkdtemp(prefix="conf-v67-")
        chemin = _dossier_de_configuration(d)
        s, res, delais = LANCEUR.verifier_configuration_v67(cfg.lire_configuration_v56(chemin), self.PLAN, d)
        self.assertEqual(delais["kimi"], {"adaptateur_s": 7200.0, "commande_s": 7150.0})

    def test_artefact_garde_24(self):
        from pole import configuration_v56 as cfg
        d = tempfile.mkdtemp(prefix="conf-art-v67-")
        chemin = _dossier_de_configuration(d, lambda c: c["fournisseurs"]["kimi"].__setitem__("delai_s", 9000))
        with self.assertRaisesRegex(LANCEUR.ConfigurationRefusee, "garde 24"):
            LANCEUR.verifier_configuration_v67(cfg.lire_configuration_v56(chemin), self.PLAN, d)

    def test_artefact_v66_d_abord(self):
        from pole import configuration_v56 as cfg
        d = tempfile.mkdtemp(prefix="conf-art2-v67-")
        chemin = _dossier_de_configuration(d, lambda c: c["boucle_reelle_v66"]["parts_usd"].__setitem__("kimi", 34.0))
        with self.assertRaisesRegex(LANCEUR.ConfigurationRefusee, "plan gelé"):
            LANCEUR.verifier_configuration_v67(cfg.lire_configuration_v56(chemin), self.PLAN, d)


class BrancheReelleGarde24(unittest.TestCase):
    """Branche réelle : configuration dont l'empreinte est celle du texte mais qui manque la garde 24 → code 2, avant toute porte ;
    `--verifier-seulement` : délais au manifeste imprimé. Mêmes pièces d'essai que la branche réelle v66."""

    @classmethod
    def setUpClass(cls):
        E66.BrancheReelle.setUpClass.__func__(cls)
        d = tempfile.mkdtemp(prefix="conf-g24-v67-")
        cls.conf_g24 = _dossier_de_configuration(d, lambda c: _poser_delai_commande(c, "kimi", "7180"))
        cls.texte_g24 = _ecrire_texte(tempfile.mkdtemp(prefix="pr-g24-"), plan=_plan(
            configuration_sha256=sha256_fichier(cls.conf_g24), heritage_depart_sha256=sha256_fichier(cls.heritage)))

    def test_artefact_garde_24_code_2(self):
        prereg = os.path.dirname(self.texte_g24)
        argv = [tempfile.mkdtemp() + "/s", "--preenregistrement", self.texte_g24, "--heritage-depart", self.heritage,
                "--configuration", self.conf_g24, "--moteur", "reel", "--confirmer-moteur-reel", "--registre-go", self.registre,
                "--go", "GO-2026-11-08-02", "--bac", "reel", "--utilisateur-bac", "64097"]
        with mock.patch.object(LANCEUR, "DOSSIER_PREREG", prereg), mock.patch.object(LANCEUR, "WHICH", lambda nom: None):
            code, _, err = _lancer(LANCEUR, argv)
        self.assertEqual(code, 2)
        self.assertIn("garde 24", err)
        self.assertNotIn("MachineRefusee", err)  # la garde 24 (configuration) avant la garde 22

    def test_sain_verifier_seulement_delais_au_manifeste(self):
        def roles_reels(conf, plan, base, sortie, transmettre=True):
            p, e, r = _roles_a_blanc()
            return p, e, r, {"doublures": True}
        argv = [tempfile.mkdtemp() + "/sortie", "--preenregistrement", self.texte, "--heritage-depart", self.heritage,
                "--configuration", self.conf, "--moteur", "reel", "--confirmer-moteur-reel", "--registre-go", self.registre,
                "--go", "GO-2026-11-08-02", "--bac", "reel", "--utilisateur-bac", "64097", "--verifier-seulement"]
        with mock.patch.object(LANCEUR, "DOSSIER_PREREG", self.prereg), mock.patch.object(LANCEUR, "version_bwrap", lambda *a, **k: (0, 9)), \
                mock.patch.object(os, "geteuid", lambda: 0), \
                mock.patch.object(LANCEUR, "preparer_bac_v66", lambda b, u, which=None: (None, lambda: (None, DESCRIPTION_SAINE), DESCRIPTION_SAINE)), \
                mock.patch.object(LANCEUR.L64, "exiger_machine_jetable_reel", lambda env, conf: ()), \
                mock.patch.object(LANCEUR, "roles_reels_v67", roles_reels):
            code, out, err = _lancer(LANCEUR, argv)
        self.assertEqual(code, 0, err)
        conf_info = json.loads(out)["configuration"]
        self.assertEqual(conf_info["delais_v67"]["kimi"], {"adaptateur_s": 7200.0, "commande_s": 7150.0})


class BlocsNonInterchangeables(unittest.TestCase):
    def test_texte_v66_refuse_par_v67(self):
        d = tempfile.mkdtemp(prefix="prereg-v66-pour-v67-")
        E66.LANCEUR = LANCEUR_V66
        try:
            chemin = _ecrire_texte(d)
            LANCEUR_V66.lire_preenregistrement(chemin, d)  # sain pour la v66
        finally:
            E66.LANCEUR = LANCEUR
        with self.assertRaisesRegex(LANCEUR.PreenregistrementRefuse, "empreintes-du-code-v67"):
            LANCEUR.lire_preenregistrement(chemin, d)

    def test_texte_v67_refuse_par_v66(self):
        d = tempfile.mkdtemp(prefix="prereg-v67-pour-v66-")
        chemin = _ecrire_texte(d)
        LANCEUR.lire_preenregistrement(chemin, d)  # sain pour la v67
        with self.assertRaisesRegex(LANCEUR_V66.PreenregistrementRefuse, "empreintes-du-code-v66"):
            LANCEUR_V66.lire_preenregistrement(chemin, d)

    def test_plan_v66_dans_un_texte_v67_refuse(self):
        plan66 = _plan().replace(LANCEUR.DEBUT_PLAN, LANCEUR_V66.DEBUT_PLAN).replace(LANCEUR.FIN_PLAN, LANCEUR_V66.FIN_PLAN)
        with self.assertRaisesRegex(LANCEUR.PreenregistrementRefuse, "plan-gele-v67"):
            LANCEUR.lire_plan(plan66)


class ExempleV8(unittest.TestCase):
    def test_v8_egale_v6_sauf_les_changements_dits(self):
        v6, v8 = _conf(CONF_V6), _conf(CONF_V8)
        attendu = copy.deepcopy(v6)
        attendu["_lisez_moi"] = v8["_lisez_moi"]
        attendu["plafonds_session"]["proposeur"] = 1.5
        attendu["fournisseurs"]["kimi"]["delai_s"] = 7200
        attendu["arrets"]["a3_delai_s"]["kimi"] = 7200
        c = attendu["fournisseurs"]["kimi"]["commande"]
        c[c.index("--max-sortie-proposeur") + 1] = "131072"
        c[c.index("--delai-s") + 1] = "7150"
        self.assertEqual(v8, attendu)

    def test_empreinte_de_l_exemple(self):
        self.assertEqual(sha256_fichier(CONF_V8), "eb6262890927bfc351bf2a32c21d0dcf121445256a5ebe6c4eaee70b9265b31d")


class ManifesteV67(unittest.TestCase):
    def test_lanceur_au_manifeste(self):
        self.assertEqual(LANCEUR.manifeste()["lanceur"], "boucle-reelle-v67")
        self.assertEqual(LANCEUR.manifeste()["version"], B.VERSION)  # le cœur v66, inchangé


if __name__ == "__main__":
    unittest.main()
