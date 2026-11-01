"""Essais de la v58 : le nul v8 du juge (`pole/nul_v8.py`), le banc des tricheurs v8 et les démonstrations v8.

R5 : chaque garde est éprouvée sur un cas sain et sur un artefact, aucun repli silencieux ; R9 : graines SeedSequence.
- Configuration : cas sain (nul v8 imposé, autres réglages conservés) ; artefacts : toute configuration sans le nul ajusté
  refusée par `NulV8Refuse`, à la construction comme à la garde.
- Membres : identiques à ceux du juge de production (`cycle.membres_de_l_archive`) et au réglage « candidat » du banc v7 ;
  artefacts : membre ajusté absent ou altéré refusé.
- Juge (banc v8, entropie fixée, 20 répétitions) : cas sain, une loi vraie neuve (fille, fiche fraîche) promue ; artefacts,
  T02, T03b, T04 et T05s jamais promus (0/20) ; nul exact ≤ α ; dents : aux mêmes graines, sans le nul ajusté, T02 et T04
  passent, et T01 passe sous le nul v1 ; le juge v8 rend exactement l'évaluation du réglage « candidat » du banc v7.
- Juge de production : une génération du pôle sous `configuration_nul_v8` élimine le mélange de deux survivantes (T04) et
  promeut la loi neuve.
- Lecture gelée du préenregistrement (test binomial exact et Clopper-Pearson, Holm, Newcombe, issues, audits, prédictions)
  sur des comptes construits ; graines et règle du préenregistrement (fichier nommé, scellé, code gelé complet, espaces de
  graines disjoints) ; gardes du banc (refus, arrêt) ; démonstrations v8.
Mutations : `essais/mutations_v58.py`. Durée visée : moins de 3 minutes.
"""

import contextlib
import dataclasses
import functools
import hashlib
import importlib.util
import io
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from statistics import NormalDist

import numpy as np

from essais.test_v7_nul_archive import banque_deux_effets, fiche_a, loi
from pole import nul_v8
from pole.cycle import Budget, ConfigGeneration, Generation, membres_de_l_archive
from pole.fiche import RegistreGel
from pole.memoire import Memoire
from pole.monde_banque import MondeBanque
from pole.outils import ecrire_scelle, graine_derivee, sha256_fichier
from pole.simulation import AdaptateurSimule, MondeSimule

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
ENTROPIE = 20261101  # entropie racine des essais (mode exploratoire du banc ; la validation décisive a la sienne, ≥ 2⁶⁴)
REPETITIONS = 20


def _charger(fichier, nom):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, "demonstrations", fichier))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


banc = _charger("banc_tricheurs_v8.py", "banc_tricheurs_v8_essai_v58")
ALPHA = banc.ALPHA


class Dossier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pole-essais-v58-")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def silence(self):
        pile = contextlib.ExitStack()
        pile.enter_context(contextlib.redirect_stdout(io.StringIO()))
        pile.enter_context(contextlib.redirect_stderr(io.StringIO()))
        self.addCleanup(pile.close)
        return pile


# --- configuration ---------------------------------------------------------------------------------------------------
class ConfigurationNulV8(unittest.TestCase):
    def test_cas_sain_nul_v8_impose_autres_reglages_conserves(self):
        c = nul_v8.configuration_nul_v8(urne=False, graine=7, multiplicite="e-bh", taille_plan=120)
        self.assertIsInstance(c, ConfigGeneration)
        self.assertIs(c.nul_archive_ajuste, True, "nul v8 : nul_archive_ajuste doit être vrai")
        self.assertIs(c.nul_archive, True)
        self.assertEqual((c.selection, c.nul_filles, c.urne, c.graine, c.multiplicite, c.taille_plan),
                         ("pari", "v2", False, 7, "e-bh", 120))
        c2 = nul_v8.configuration_nul_v8(selection="pari", nul_filles="v2", nul_archive=True, nul_archive_ajuste=True)
        self.assertIs(c2.nul_archive_ajuste, True, "nul v8 : nul_archive_ajuste doit être vrai")
        self.assertIs(nul_v8.exiger_nul_v8(c), c)

    def test_artefact_configuration_sans_nul_ajuste_refusee(self):
        for reglages in ({"nul_archive_ajuste": False}, {"nul_archive": False}, {"nul_filles": "v0"},
                         {"nul_filles": "v2_souple"}, {"selection": "seuil"}, {"nul_archive_ajuste": 1},
                         {"nul_archive_ajuste": None}):
            with self.subTest(reglages=reglages):
                with self.assertRaises(nul_v8.NulV8Refuse) as ctx:
                    nul_v8.configuration_nul_v8(**reglages)
                self.assertIn(next(iter(reglages)), str(ctx.exception))

    def test_artefact_garde_refuse_un_juge_construit_sans_nul_v8(self):
        v8 = nul_v8.configuration_nul_v8()
        for config in (ConfigGeneration(selection="pari", nul_archive=True),  # réglage des démonstrations v7
                       ConfigGeneration(selection="pari"),
                       dataclasses.replace(v8, nul_archive_ajuste=False),
                       dataclasses.replace(v8, nul_filles="v2_souple"), {"nul_archive_ajuste": True}):
            with self.subTest(config=config), self.assertRaises(nul_v8.NulV8Refuse):
                nul_v8.exiger_nul_v8(config)
        sain = ConfigGeneration(selection="pari", nul_archive=True, nul_archive_ajuste=True)  # le défaut de pole.py
        self.assertIs(nul_v8.exiger_nul_v8(sain), sain)


# --- membres ---------------------------------------------------------------------------------------------------------
def _lois(graine=11):
    rng = random.Random(graine)
    return {n: banc.sp.loi_softmax_aleatoire(rng, 3, 2) for n in ("A", "B", "S1", "S2")}


class MembresNulV8(unittest.TestCase):
    def test_cas_sain_membres_d_une_fille_et_d_une_fiche_sans_parent(self):
        L = _lois()
        surv, parents = {"S1": L["S1"], "S2": L["S2"]}, {"A": L["A"], "B": L["B"]}
        attendus = ["archive:S1", "archive_couvert:S1", "ajuste_log:archive:S1", "archive:S2", "archive_couvert:S2",
                    "ajuste_log:archive:S2", "ajuste_lineaire:archive"]
        fille = nul_v8.membres_archive_v8(surv, parents)
        self.assertEqual([m["nom"] for m in fille], attendus)
        self.assertEqual(fille[-1]["lois"], [L["A"], L["B"], L["S1"], L["S2"]])
        fraiche = nul_v8.membres_archive_v8(surv)
        self.assertEqual([m["nom"] for m in fraiche], attendus)
        self.assertEqual(fraiche[-1]["lois"], [L["S1"], L["S2"]])
        self.assertEqual(nul_v8.membres_archive_v8({}), [])
        self.assertEqual([m["nom"] for m in nul_v8.membres_archive_v8({}, parents)], ["ajuste_lineaire:archive"])

    def test_identiques_au_juge_de_production(self):
        memoire = Memoire(active=True, graine=0)
        s = fiche_a("S1", loi(0), "x")
        for ident, j in (("S1", 0), ("S2", 2), ("P1", 1)):
            memoire.index[ident] = {"statut": "survit", "temoin": None, "loi_predictive": loi(j),
                                    "espace_instances": s.espace_instances}
        for fiche, parents in ((fiche_a("F1", loi(2), "y"), None),
                               (fiche_a("F2", loi(2), "y", parents=["P1", "Q"], ce_que_la_fille_predit_de_plus="le trait e2"),
                                {"P1": loi(1), "Q": loi(0, force=0.4)})):
            with self.subTest(fiche=fiche.identifiant):
                production = membres_de_l_archive(fiche, memoire, ajuste=True, lois_parents=parents)
                v8 = nul_v8.membres_archive_v8({"S1": loi(0), "S2": loi(2), "P1": loi(1)}, parents, 3, 3, "A")
                self.assertEqual(v8, production)

    def test_identiques_au_candidat_du_banc_v7(self):
        L = _lois(5)
        surv, parents = {"S1": L["S1"], "S2": L["S2"]}, {"A": L["A"], "B": L["B"]}
        self.assertEqual(nul_v8.membres_archive_v8(surv, parents, 3, 2), banc.v7.membres_archive(L, "candidat", parents))
        self.assertEqual(nul_v8.membres_archive_v8(surv, None, 3, 2), banc.v7.membres_archive(L, "candidat"))

    def test_artefact_membre_ajuste_absent_ou_altere_refuse(self):
        L = _lois()
        surv, parents = {"S1": L["S1"], "S2": L["S2"]}, {"A": L["A"], "B": L["B"]}
        sains = nul_v8.membres_archive_v8(surv, parents)
        sans_lin = [m for m in sains if m["nom"] != "ajuste_lineaire:archive"]
        sans_log = [m for m in sains if m["nom"] != "ajuste_log:archive:S1"]
        pool_tronque = [dict(m, lois=m["lois"][:-1]) if m["nom"] == "ajuste_lineaire:archive" else m for m in sains]
        log_change = [dict(m, lois=[L["S2"]]) if m["nom"] == "ajuste_log:archive:S1" else m for m in sains]
        double = sains + [sains[-1]]
        for nom, membres in (("sans ajuste_lineaire:archive", sans_lin), ("sans ajuste_log:archive:S1", sans_log),
                             ("mise en commun tronquée", pool_tronque), ("survivante tempérée changée", log_change),
                             ("membre en double", double)):
            with self.subTest(cas=nom), self.assertRaises(nul_v8.NulV8Refuse):
                nul_v8.exiger_membres_ajustes(membres, surv, parents)
        self.assertIs(nul_v8.exiger_membres_ajustes(sains, surv, parents), sains)
        with self.assertRaises(ValueError):
            nul_v8.membres_archive_v8(surv, {"A": L["A"]})  # un seul parent : ni fille ni fiche sans parent


# --- juge du banc v8 (statistique, entropie fixée) ------------------------------------------------------------------
def _ligne(nom, nul, n=REPETITIONS, cle_graines=None):
    return banc.jouer_ligne(ENTROPIE, nom, nul, "essai", n, cle_graines=cle_graines)


class ArtefactsTricheurs(unittest.TestCase):
    def test_tricheurs_par_recombinaison_refuses_sous_nul_v8(self):
        for nom in ("T02", "T03b", "T04", "T05s"):
            with self.subTest(ligne=nom):
                x = _ligne(nom, "v8")
                self.assertEqual(x["repetitions"], REPETITIONS)
                self.assertEqual(x["promues"], 0, f"{nom}|v8 promue {x['promues']}/{x['repetitions']} sous le nul v8")


class JugeSousNulV8(unittest.TestCase):
    def test_cas_sain_loi_vraie_neuve_promue(self):
        for nom in ("fille_neuve", "fraiche_neuve"):
            with self.subTest(ligne=nom):
                x = _ligne(nom, "v8")
                self.assertGreaterEqual(x["promues"], 16, f"{nom}|v8 promue {x['promues']}/{x['repetitions']} : puissance "
                                                          "perdue sous le nul v8 (garde de régression : ≥ 0,80)")

    def test_nul_exact_sous_alpha(self):
        x = _ligne("nul_exact", "v8")
        self.assertLessEqual(x["taux"], ALPHA, f"nul_exact|v8 promu {x['promues']}/{x['repetitions']}")
        self.assertLessEqual(x["log_w_max_max"], banc.TOLERANCE_LOG_W, "nul exact : log W > 0 alors que la fiche est au nul")

    def test_dents_aux_memes_graines_sans_nul_ajuste(self):
        for nom in ("T02", "T04"):
            with self.subTest(ligne=nom):
                x = _ligne(nom, "v7", cle_graines=f"{nom}|v8")  # mêmes scénarios que la ligne v8 refusée ci-dessus
                self.assertGreater(x["taux"], ALPHA, f"{nom}|v7 promue {x['promues']}/{x['repetitions']} : le banc n'a pas "
                                                     "de dents à ces graines")
        x = _ligne("T01", "v1")
        self.assertGreater(x["taux"], ALPHA, f"T01|v1 promue {x['promues']}/{x['repetitions']} : artefact requis non vu")

    def test_juge_v8_identique_au_banc_v7_aux_memes_graines(self):
        for nom, nul7, nul8 in (("T02", "candidat", "v8"), ("T04", "candidat", "v8"), ("T05s", "candidat", "v8"),
                                ("T02", "v7", "v7"), ("T04", "v7", "v7"), ("T01", "v1", "v1")):
            for r in range(2):
                with self.subTest(ligne=nom, nul=nul7, r=r):
                    cle = f"essai-v58|{nom}|{nul7}"
                    rng = random.Random(graine_derivee(ENTROPIE, cle, r))
                    genre, l_, monde, L = banc.v7.scenario(nom, rng)
                    ev7 = banc.v7.juger(genre, l_, monde, L, nul7, rng, ENTROPIE, cle, r)
                    rng = random.Random(graine_derivee(ENTROPIE, cle, r))
                    genre, l_, monde, L = banc.v7.scenario(nom, rng)
                    ev8 = banc.juger_v8(genre, l_, monde, L, nul8, rng, graine_derivee(ENTROPIE, cle, r, "noyau"),
                                        graine_derivee(ENTROPIE, cle, r, "frais"))
                    self.assertEqual(ev8, ev7)



class ProcessusDuBanc(Dossier):
    def test_resultats_independants_du_nombre_de_processus(self):
        """Le banc joué comme script (point d'entrée réel) rend les mêmes comptes sur 1 et sur 2 processus."""
        sorties = {}
        for p in ("1", "2"):
            d = os.path.join(self.tmp, f"p{p}")
            subprocess.run([sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "banc_tricheurs_v8.py"), d,
                            "--graine", "5", "--lignes", "T04,T03u", "--repetitions", "2", "--processus", p],
                           capture_output=True, text=True, check=True)
            with open(os.path.join(d, "banc-tricheurs-v8.json"), encoding="utf-8") as f:
                sorties[p] = [{k: v for k, v in x.items() if k != "duree_s"} for x in json.load(f)["resultats"]]
        self.assertEqual(sorties["1"], sorties["2"])
        self.assertEqual([x["ligne"] for x in sorties["1"]], ["T03u", "T04"])


class ProductionNulV8(Dossier):
    def test_generation_du_pole_sous_nul_v8(self):
        """Juge de production : survivantes S1, S2 en génération 0 ; en génération 1, leur mélange (T04) est éliminé, la
        loi du monde (neuve) promue ; l'engagement porte les membres ajustés d'archive."""
        chemin = os.path.join(self.tmp, "banque.json")
        banque_deux_effets(chemin)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3))
        cfg = nul_v8.configuration_nul_v8(taille_plan=150, taille_plan_filles=150, urne=False, part_calibrage=12)
        memoire, registre = Memoire(active=True, graine=0), RegistreGel()
        s1, s2 = fiche_a("S1", loi(0), "L'issue croît avec le trait e0"), fiche_a("S2", loi(2), "L'issue croît avec le trait e2")
        r0 = Generation(0, adaptateur, cfg, self.tmp, registre, Budget(10), memoire=memoire, monde_noyau=monde).executer([s1, s2])
        for s in (s1, s2):
            memoire.indexer(s, r0["issues"][s.identifiant], 0)
            self.assertEqual(s.statut, "survit", r0["issues"][s.identifiant].get("motif"))
        melange = fiche_a("M1", {"type": "melange", "composantes": [loi(0), loi(2)], "poids": [0.5, 0.5]},
                          "Les deux descripteurs comptent ensemble")
        neuve = fiche_a("N1", {"type": "softmax", "poids": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.6, 0.0, 1.6]],
                               "biais": [math.log(0.6), math.log(0.4), 0.0]}, "L'issue suit la somme des deux descripteurs")
        g1 = Generation(1, adaptateur, cfg, self.tmp, registre, Budget(10), memoire=memoire, monde_noyau=monde)
        r1 = g1.executer([melange, neuve])
        self.assertEqual(melange.statut, "eliminee", f"M1 {melange.statut} sous le nul v8 : {r1['issues']['M1'].get('motif')}")
        self.assertEqual(neuve.statut, "survit", r1["issues"]["N1"].get("motif"))
        noms = [m["nom"] for m in g1.engagements["M1"].engagement["bibliotheque"]]
        self.assertIn("ajuste_lineaire:archive", noms)
        self.assertIn("ajuste_log:archive:S1", noms)


# --- lecture gelée du préenregistrement ----------------------------------------------------------------------------
_bornes = functools.lru_cache(maxsize=None)(banc.clopper_pearson)  # données d'entrée seulement (la lecture recalcule)


def _l(nom, nul, role, x, n=1000, log_w_max=-0.1):
    return {"ligne": nom, "reglage": nul, "role": role, "promues": x, "repetitions": n, "taux": x / n,
            "clopper_pearson_95_unilaterales": list(_bornes(x, n)), "log_w_max_max": log_w_max}


def _plan(fatales=None, artefact=450, puissance=((1000, 990), (1000, 995)), log_w=None):
    fatales, log_w = fatales or {}, log_w or {}
    lignes = [_l(n, "v8", "fatale", fatales.get(n, 0), log_w_max=log_w.get(n, -0.1)) for n in banc.FATALES]
    lignes.append(_l("T01", "v1", "artefact_requis", artefact))
    for nom, (x7, x8) in zip(banc.PUISSANCE, puissance):
        lignes += [_l(nom, "v8", "puissance", x8), _l(nom, "v7", "puissance", x7)]
    return lignes + [_l("T07", "v8", "mesure", 5), _l("T12b", "v8", "mesure", 900)]


class LectureGelee(unittest.TestCase):
    def test_cas_sain_tout_tenu_confirmee(self):
        lec = banc.lire_v8(_plan(), complet=True)
        self.assertEqual(set(lec["fatales"].values()), {"tenue"})
        self.assertEqual(lec["artefact"], {"T01|v1": "tenue"})
        self.assertEqual(lec["perte_de_puissance"], {"fille_neuve": "tenue", "fraiche_neuve": "tenue"})
        self.assertEqual((lec["issue"], lec["audits"], lec["issue_suspendue_par_audit"]), ("confirmée", [], False))
        self.assertTrue(all(lec["predictions"]["P1_lignes_fatales"].values()))
        self.assertEqual(banc.code_de_sortie(_plan()), 0)

    def test_artefact_ligne_fatale_au_dessus_de_alpha_infirmee(self):
        lec = banc.lire_v8(_plan({"T04": 80}), complet=True)
        self.assertEqual(lec["fatales"]["T04|v8"], "non tenue")
        self.assertEqual(lec["issue"], "infirmée (validité)")
        self.assertEqual(banc.code_de_sortie(_plan({"T04": 80})), 1)

    def test_ligne_fatale_limite_non_jugeable(self):
        lec = banc.lire_v8(_plan({"T12a": 45}), complet=True)
        self.assertEqual(lec["fatales"]["T12a|v8"], banc.NON_JUGEABLE)
        self.assertEqual(lec["issue"], "non jugeable (précision insuffisante)")
        self.assertEqual(lec["audits"], [], "T12a n'est pas refusée par construction : pas d'audit A1")

    def test_correction_de_holm(self):
        """Deux lignes à 37/1000 : la borne de Clopper-Pearson à 95 % sans correction (0,0484) passerait sous α ; Holm ne
        les déclare pas tenues (valeur p exacte 0,031 > 0,05/2 au premier des deux pas). Une seule à 37 : tenue."""
        self.assertLess(banc.clopper_pearson(37, 1000)[1], ALPHA)
        lec = banc.lire_v8(_plan({"T12a": 37, "T02": 37}), complet=True)
        self.assertEqual((lec["fatales"]["T12a|v8"], lec["fatales"]["T02|v8"]), (banc.NON_JUGEABLE,) * 2)
        self.assertEqual(lec["issue"], "non jugeable (précision insuffisante)")
        self.assertEqual(banc.lire_v8(_plan({"T12a": 37}), complet=True)["issue"], "confirmée")

    def test_seuils_de_holm_a_1000_repetitions(self):
        """Tables du préenregistrement : nombre maximal de promotions compatible avec « tenue » par rang de Holm (11 lignes
        fatales), et nombre minimal pour l'artefact."""
        self.assertEqual(banc.promotions_max_tenue(1000, 11), [32, 32, 32, 33, 33, 33, 34, 34, 35, 36, 38])
        self.assertEqual(banc.promotions_min_artefact(1000), 63)
        tous_32 = banc.lire_v8(_plan({n: 32 for n in banc.FATALES}), complet=True)
        self.assertEqual(set(tous_32["fatales"].values()), {"tenue"})
        tous_33 = banc.lire_v8(_plan({n: 33 for n in banc.FATALES}), complet=True)
        self.assertEqual(set(tous_33["fatales"].values()), {banc.NON_JUGEABLE})
        self.assertEqual(banc.lire_v8(_plan({"T12a": 38}), complet=True)["fatales"]["T12a|v8"], "tenue")
        self.assertEqual(banc.lire_v8(_plan({"T12a": 39}), complet=True)["fatales"]["T12a|v8"], banc.NON_JUGEABLE)
        self.assertEqual(banc.lire_v8(_plan(artefact=63), complet=True)["artefact"]["T01|v1"], "tenue")
        self.assertEqual(banc.lire_v8(_plan(artefact=62), complet=True)["artefact"]["T01|v1"], banc.NON_JUGEABLE)

    def test_perte_de_puissance(self):
        trop = banc.lire_v8(_plan(puissance=((1000, 900), (1000, 995))), complet=True)
        self.assertEqual((trop["perte_de_puissance"]["fille_neuve"], trop["issue"]), ("non tenue", "infirmée (puissance)"))
        limite = banc.lire_v8(_plan(puissance=((950, 905), (1000, 995))), complet=True)
        self.assertEqual((limite["perte_de_puissance"]["fille_neuve"], limite["issue"]),
                         (banc.NON_JUGEABLE, "non jugeable (précision insuffisante)"))

    def test_artefact_requis_non_vu_banc_sans_dents(self):
        sans_dents = banc.lire_v8(_plan(artefact=30), complet=True)
        self.assertEqual((sans_dents["artefact"]["T01|v1"], sans_dents["issue"]), ("non tenue", "non jugeable (banc sans dents)"))
        self.assertTrue(any(a.startswith("A3 ") for a in sans_dents["audits"]))
        self.assertTrue(sans_dents["issue_suspendue_par_audit"])
        self.assertEqual(banc.code_de_sortie(_plan(artefact=30)), 1, "artefact non vu sans échec du code de sortie")
        self.assertEqual(banc.lire_v8(_plan()[:3], complet=False)["issue"], "partielle (plan incomplet : aucune issue)")

    def test_audits_symetriques(self):
        self.assertEqual(banc.lire_v8(_plan(log_w={"T04": -1e-9, "T05s": 1e-3}), complet=True)["audits"], [])
        a1 = banc.lire_v8(_plan({"T02": 1}), complet=True)
        self.assertTrue(any(a.startswith("A1 T02|v8") for a in a1["audits"]), "A1 : promotion d'une ligne refusée par construction")
        self.assertEqual((a1["fatales"]["T02|v8"], a1["issue"], a1["issue_suspendue_par_audit"]), ("tenue", "confirmée", True))
        a4 = banc.lire_v8(_plan(log_w={"T04": 1e-3}), complet=True)
        self.assertTrue(any(a.startswith("A4 T04|v8") for a in a4["audits"]), "A4 : log W > 0 dans la classe linéaire")
        trop_beau = banc.lire_v8(_plan(puissance=((900, 990), (1000, 995))), complet=True)
        self.assertTrue(any(a.startswith("A2 fille_neuve") for a in trop_beau["audits"]), "A2 : nul v8 plus puissant que v7")
        self.assertTrue(trop_beau["issue_suspendue_par_audit"])

    def test_predictions_rapportees(self):
        lec = banc.lire_v8(_plan({"T12a": 9}, puissance=((990, 980), (1000, 960))), complet=True)
        p = lec["predictions"]
        self.assertTrue(p["P1_lignes_fatales"]["T12a|v8"])
        self.assertEqual(p["P2_perte_dans_l_intervalle"], {"fille_neuve": True, "fraiche_neuve": True})
        self.assertEqual(p["P5_puissance_v8"], {"fille_neuve|v8": True, "fraiche_neuve|v8": True})
        rate = banc.lire_v8(_plan({"T02": 1, "T12a": 11}), complet=True)["predictions"]["P1_lignes_fatales"]
        self.assertEqual((rate["T02|v8"], rate["T12a|v8"], rate["T04|v8"]), (False, False, True))

    def test_bornes_de_clopper_pearson_et_valeurs_p_exactes(self):
        bas, haut = banc.clopper_pearson(0, 1000)
        self.assertEqual(bas, 0.0)
        self.assertAlmostEqual(haut, 1 - 0.05 ** (1 / 1000), places=12, msg="borne haute de Clopper-Pearson")
        bas, haut = banc.clopper_pearson(1000, 1000)
        self.assertAlmostEqual(bas, 0.05 ** (1 / 1000), places=12, msg="borne basse de Clopper-Pearson")
        self.assertEqual(haut, 1.0)
        self.assertAlmostEqual(banc.p_valeur_exacte(0, 1000, ALPHA, "haute"), 0.95 ** 1000, delta=1e-30)
        self.assertAlmostEqual(banc.p_valeur_exacte(1, 10, 0.5, "basse"), 1 - 0.5 ** 10, places=14)
        self.assertAlmostEqual(banc.p_valeur_exacte(1, 10, 0.5, "haute"), 11 / 1024, places=14)
        for x in (0, 10, 30, 37, 45):  # rejet à un niveau ⇔ borne de Clopper-Pearson à ce niveau sous le seuil
            p = banc.p_valeur_exacte(x, 1000, ALPHA, "haute")
            self.assertAlmostEqual(banc.clopper_pearson(x, 1000, gamma=p)[1], ALPHA, places=9)
        for x in (55, 63, 80):
            p = banc.p_valeur_exacte(x, 1000, ALPHA, "basse")
            self.assertAlmostEqual(banc.clopper_pearson(x, 1000, gamma=p)[0], ALPHA, places=9)
        for x7, x8 in ((970, 940), (1000, 960)):
            p = banc.p_valeur_newcombe(x7, 1000, x8, 1000, 0.05, "haute")
            self.assertAlmostEqual(banc.newcombe(x7, 1000, x8, 1000, NormalDist().inv_cdf(1 - p))[1], 0.05, places=6)
        self.assertEqual(banc.holm({"a": 0.01, "b": 0.02, "c": 0.04}), {"a", "b", "c"})
        self.assertEqual(banc.holm({"a": 0.01, "b": 0.03, "c": 0.04}), {"a"})
        with self.assertRaises(ValueError):
            banc.p_valeur_exacte(1, 10, 0.5, "deux")


# --- graines (R9) et règle du préenregistrement -------------------------------------------------------------------
class GrainesEtPreenregistrement(Dossier):
    def test_graines_seedsequence(self):
        g = banc.graines(ENTROPIE, "T02|v8", 3)
        self.assertEqual(g, banc.graines(ENTROPIE, "T02|v8", 3))
        cle = int.from_bytes(hashlib.sha256(b"T02|v8").digest()[:4], "big")
        enfants = np.random.SeedSequence(ENTROPIE, spawn_key=(cle, 3)).spawn(3)
        attendu = tuple(int(e.generate_state(2, dtype=np.uint64)[0]) + (int(e.generate_state(2, dtype=np.uint64)[1]) << 64)
                        for e in enfants)
        self.assertEqual(g, attendu)
        self.assertEqual(len({g, banc.graines(ENTROPIE, "T02|v8", 4), banc.graines(ENTROPIE, "T04|v8", 3),
                              banc.graines(ENTROPIE + 1, "T02|v8", 3)}), 4)

    def test_cles_de_graines_distinctes(self):
        self.assertEqual(banc.verifier_cles_distinctes(list(banc.LIGNES)), list(banc.LIGNES))
        with self.assertRaises(ValueError):
            banc.verifier_cles_distinctes(list(banc.LIGNES) + [banc.LIGNES[0]])

    def test_fichiers_geles_couvrent_les_imports(self):
        """Le code qu'une course importe (mesuré dans un processus neuf) est dans `FICHIERS_GELES`."""
        script = ("import importlib.util, json, os, sys\nsys.path.insert(0, sys.argv[1])\n"
                  "s = importlib.util.spec_from_file_location('b', os.path.join(sys.argv[1], 'demonstrations', "
                  "'banc_tricheurs_v8.py'))\nm = importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\n"
                  "r = os.path.realpath(sys.argv[1])\nf = [os.path.realpath(getattr(x, '__file__', '') or '') for x in "
                  "list(sys.modules.values())]\nprint(json.dumps(sorted(os.path.relpath(p, r) for p in f if p.startswith(r + os.sep))))\n")
        sortie = subprocess.run([sys.executable, "-I", "-B", "-c", script, RACINE], capture_output=True, text=True, check=True)
        importes = set(json.loads(sortie.stdout)) | {"demonstrations/banc_tricheurs_v8.py", "demonstrations/banc_tricheurs_v7.py"}
        self.assertTrue(importes <= set(banc.FICHIERS_GELES), f"non gelés : {sorted(importes - set(banc.FICHIERS_GELES))}")
        self.assertIn("pole/nul_v8.py", importes)

    def _gel_complet(self):
        return [(sha256_fichier(os.path.join(RACINE, relatif)), relatif) for relatif in banc.FICHIERS_GELES]

    def _prereg(self, empreintes, sceller=True, nom="prereg.md"):
        chemin = os.path.join(self.tmp, nom)
        texte = ("# Préenregistrement d'essai\n\n" + banc.DEBUT_EMPREINTES + "\n```\n"
                 + "".join(f"{h}  {p}\n" for h, p in empreintes) + "```\n" + banc.FIN_EMPREINTES + "\n")
        if sceller:
            ecrire_scelle(chemin, texte)
        else:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        return chemin

    def _lire(self, chemin, nomme=None):
        with unittest.mock.patch.object(banc, "PREREG_DECISIF", nomme or chemin):
            return banc.lire_preenregistrement(chemin)

    def test_cas_sain_preenregistrement_scelle(self):
        chemin = self._prereg(self._gel_complet())
        entropie, empreinte, gelees = self._lire(chemin)
        self.assertEqual((entropie, empreinte), (int(sha256_fichier(chemin), 16), sha256_fichier(chemin)))
        self.assertEqual(set(gelees), set(banc.FICHIERS_GELES))
        self.assertGreaterEqual(entropie, banc.GRAINE_EXPLORATOIRE_MAX)

    def test_artefacts_preenregistrement(self):
        complet = self._gel_complet()
        with self.assertRaises(banc.PreenregistrementNonScelle):
            self._lire(self._prereg(complet, sceller=False, nom="a.md"))
        modifie = self._prereg(complet, nom="b.md")
        with open(modifie, "a", encoding="utf-8") as f:
            f.write("ajout après scellement\n")
        with self.assertRaises(banc.PreenregistrementNonScelle):
            self._lire(modifie)
        faux = [("0" * 64, p) if p == "pole/nul_v8.py" else (h, p) for h, p in complet]
        with self.assertRaisesRegex(banc.EcartAuPlan, "code différent"):
            self._lire(self._prereg(faux, nom="c.md"))
        with self.assertRaisesRegex(banc.EcartAuPlan, "vide"):
            self._lire(self._prereg([], nom="d.md"))
        incomplet = [(h, p) for h, p in complet if p != "demonstrations/banc_tricheurs_v8.py"]
        with self.assertRaisesRegex(banc.EcartAuPlan, "non gelé"):
            self._lire(self._prereg(incomplet, nom="e.md"))
        autre = self._prereg(complet, nom="f.md")
        with self.assertRaisesRegex(banc.EcartAuPlan, "mode décisif : le préenregistrement est"):
            self._lire(autre, nomme=os.path.join(self.tmp, "le-vrai.md"))
        petit = self._prereg(complet, nom="g.md")
        with unittest.mock.patch.object(banc, "entropie_du_preenregistrement", return_value=(5, "0" * 63 + "5")), \
                self.assertRaisesRegex(banc.EcartAuPlan, "espace des graines exploratoires"):
            self._lire(petit)

    def test_refus_du_banc_avant_toute_course(self):
        """Chaque refus tombe avant toute écriture et toute course ; la course est remplacée par un bouchon (une garde
        neutralisée rend alors 3, jamais une vraie course de 1 000 répétitions)."""
        p = self._prereg(self._gel_complet())  # le fichier nommé (PREREG_DECISIF) dans cet essai
        autre = self._prereg(self._gel_complet(), nom="autre.md")  # scellé et complet, mais pas le fichier nommé
        plein = os.path.join(self.tmp, "plein")
        os.makedirs(plein)
        open(os.path.join(plein, "x"), "w").close()
        court = ["--lignes", "T04", "--repetitions", "1", "--processus", "1"]
        appels = []

        def bouchon(taches, processus):
            appels.append(len(taches))
            return [], "course interdite dans cet essai"
        cas = ([os.path.join(self.tmp, "s1"), "--preenregistrement", p, "--lignes", "T02"],
               [os.path.join(self.tmp, "s2"), "--preenregistrement", p, "--repetitions", "20"],
               [os.path.join(self.tmp, "s3"), "--preenregistrement", p, "--duree-max-s", "60"],
               [os.path.join(self.tmp, "s4"), "--preenregistrement", autre],
               [os.path.join(self.tmp, "s5"), "--graine", "1", "--lignes", "T99"],
               [os.path.join(self.tmp, "s6"), "--graine", str(2 ** 64)] + court,
               [os.path.join(self.tmp, "s7"), "--graine", "-1"] + court,
               [plein, "--graine", "1"])
        with unittest.mock.patch.object(banc, "PREREG_DECISIF", p), unittest.mock.patch.object(banc, "jouer_tout", bouchon):
            for argv in cas:
                with self.subTest(argv=argv[1:]), contextlib.redirect_stderr(io.StringIO()) as err, \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(banc.principal(argv), 2, f"refus attendu pour {argv[1:]}")
                    self.assertIn("refus", err.getvalue())
                    if argv[0] != plein:
                        self.assertFalse(os.path.exists(argv[0]), "refus : aucune écriture")
        self.assertEqual(appels, [], "aucune course")

    def test_cas_sain_mode_decisif_de_bout_en_bout_sans_course(self):
        """Mode décisif complet (fichier nommé, scellé, gelant tout le code présent) ; la course est remplacée par des
        comptes construits : la graine transmise est l'empreinte du fichier, 1 000 répétitions, toutes les lignes."""
        chemin = self._prereg(self._gel_complet())
        vues = []
        comptes = {"artefact_requis": 450, "puissance": 990, "mesure": 5}

        def course(taches, processus):
            vues.extend(taches)
            return [_l(n, nul, role, comptes.get(role, 0)) for n, nul, role in banc.LIGNES], None
        sortie = os.path.join(self.tmp, "decisif")
        self.silence()
        with unittest.mock.patch.object(banc, "PREREG_DECISIF", chemin), unittest.mock.patch.object(banc, "jouer_tout", course):
            code = banc.principal([sortie, "--preenregistrement", chemin])
        self.assertEqual(code, 0)
        self.assertEqual(({t[0] for t in vues}, {t[4] for t in vues}, len(vues)),
                         ({int(sha256_fichier(chemin), 16)}, {1000}, len(banc.LIGNES)))
        with open(os.path.join(sortie, "banc-tricheurs-v8.json"), encoding="utf-8") as f:
            r = json.load(f)
        self.assertEqual((r["mode"], r["preenregistrement"]["sha256"], r["lecture"]["issue"]),
                         ("decisif", sha256_fichier(chemin), "confirmée"))
        with open(os.path.join(sortie, "manifeste.json"), encoding="utf-8") as f:
            m = json.load(f)["reglages"]
        self.assertEqual(set(m["code_du_banc_sha256"]), set(banc.FICHIERS_GELES))

    def test_banc_reduit_et_liste_d_arret(self):
        base = ["--graine", "3", "--lignes", "T04", "--repetitions", "3", "--processus", "1"]
        sortie = os.path.join(self.tmp, "sain")
        self.silence()
        self.assertEqual(banc.principal([sortie] + base), 0)
        with open(os.path.join(sortie, "banc-tricheurs-v8.json"), encoding="utf-8") as f:
            r = json.load(f)
        self.assertEqual((r["mode"], r["lecture"]["issue"]), ("exploratoire (non décisif)", "partielle (plan incomplet : aucune issue)"))
        with open(os.path.join(sortie, "manifeste.json"), encoding="utf-8") as f:
            self.assertIn("SeedSequence", json.load(f)["regle_des_graines"])
        promue = {"promue": True, "log_richesse_max": 5.0, "membre_dominant_final": "essai"}
        with unittest.mock.patch.object(banc, "juger_v8", return_value=promue):  # artefact : ligne fatale promue (3/3 > α)
            self.assertEqual(banc.principal([os.path.join(self.tmp, "fatale-promue")] + base), 1,
                             "ligne fatale au-dessus de α sans échec du code de sortie (intégration continue)")
        for nom, argv, attendu in (("duree", base + ["--duree-max-s", "1e-9"], "ArretDuree"), ("erreur", base, "panne simulée")):
            with self.subTest(arret=nom):
                arret = os.path.join(self.tmp, "arret-" + nom)
                if nom == "erreur":
                    with unittest.mock.patch.object(banc, "juger_v8", side_effect=RuntimeError("panne simulée")):
                        code = banc.principal([arret] + argv)
                else:
                    code = banc.principal([arret] + argv)
                self.assertEqual(code, 3)
                with open(os.path.join(arret, "banc-tricheurs-v8.json"), encoding="utf-8") as f:
                    r = json.load(f)
                self.assertIn(attendu, r["arret"])
                self.assertNotIn("resultats", r, "arrêt : aucun taux rapporté")


# --- démonstrations v8 ------------------------------------------------------------------------------------------------
class DemonstrationsV8(Dossier):
    @classmethod
    def setUpClass(cls):
        cls.proposeur = _charger("demo_couche1_proposeur_v8.py", "demo_couche1_proposeur_v8_essai_v58")
        cls.couche1 = _charger("demo_couche1_v8.py", "demo_couche1_v8_essai_v58")

    def test_cas_sain_configuration_remplacee_par_le_nul_v8(self):
        c = self.proposeur.v7.ConfigGeneration(selection="pari", juge="v1", nul_filles="v2", urne=False, graine=1,
                                               nul_archive=True, multiplicite="e-bh")
        self.assertIs(c.nul_archive_ajuste, True, "nul v8 : nul_archive_ajuste doit être vrai")
        c = self.couche1.v7.ConfigGeneration(selection="pari", juge="v1", nul_filles="v2", urne=True, graine=1)
        self.assertEqual((c.nul_archive, c.nul_archive_ajuste), (True, True), "nul v8 : nul_archive_ajuste doit être vrai")
        neuf = _charger("demo_couche1_v7.py", "demo_couche1_v7_essai_v58")  # la v7 elle-même n'est pas touchée (R12)
        self.assertIs(neuf.ConfigGeneration, ConfigGeneration)

    def test_artefact_course_sans_nul_v8_refusee_avant_ecriture(self):
        for module in (self.proposeur, self.couche1):
            sortie = os.path.join(self.tmp, module.VERSION)
            with self.subTest(demo=module.VERSION), self.assertRaises(nul_v8.NulV8Refuse):
                module.v7.executer_pole([], [], None, ConfigGeneration(selection="pari", nul_archive=True), 1, 1.0, sortie)
            self.assertFalse(os.path.exists(sortie))
            with self.assertRaises(nul_v8.NulV8Refuse):
                module.v7.ConfigGeneration(selection="pari", nul_archive_ajuste=False)

    def test_cas_sain_une_course_de_la_demonstration_sous_nul_v8(self):
        banque = os.path.join(self.tmp, "banque-plantee-v1.json")
        self.proposeur.v7.banque_plantee(banque)
        population, temoins = self.proposeur.v7.fiches_plantees()
        dossier = os.path.join(self.tmp, "course")
        r = self.proposeur.v7.executer_bras("plante", banque, population, temoins, "reference", dossier, 1)
        self.assertEqual(r["generations"], 1)
        with open(os.path.join(dossier, "manifeste.json"), encoding="utf-8") as f:
            reglages = json.load(f)["reglages"]
        self.assertEqual((reglages["config"]["nul_archive"], reglages["config"]["nul_archive_ajuste"]), (True, True))
        self.assertIn("nul v8", reglages["horodatage"]["valeur"])


if __name__ == "__main__":
    unittest.main()
