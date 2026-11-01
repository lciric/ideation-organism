"""Essais du juge v1 (ordre d'exécution secret, urne, loi « sans remise », garde du plan) et de l'expérience 1."""

import collections
import contextlib
import io
import itertools
import json
import math
import os
import random
import unittest

from essais.aides import CasAvecDossier
from pole import selection_pari as sp
from pole import controles_pari_v1 as cv1
from pole.controles_pari_v1 import (GRAINE_ESSAI_FUMEE, GRAINE_EXPLORATION_V0, ISSUE_ESSAI, ISSUE_INCOMPLETE, JUGES,
                                    ROSTER_V1, STRUCTURES, executer_controles_v1, juger_v1, monde_structure, partie_de)
from pole.outils import empreinte_objet, verifier_scelle
from pole.pole import principal

GRAINE_ESSAI = GRAINE_ESSAI_FUMEE  # graine des essais de fumée, refusée pour l'expérience décisive


def _proba_suite(loi, suite, k):
    """Probabilité d'une suite sous une loi prédictive aveugle (instances sans traits utiles)."""
    instance = {"z": [0.0, 0.0], "g": 0}
    logp = 0.0
    for t, x in enumerate(suite):
        logp += math.log(sp.proba(loi, instance, list(suite), t)[x])
    return math.exp(logp)


def _polya(alpha0, suite):
    compte, p = [0] * len(alpha0), 1.0
    for t, x in enumerate(suite):
        p *= (alpha0[x] + compte[x]) / (sum(alpha0) + t)
        compte[x] += 1
    return p


def _iid(p, suite):
    return math.prod(p[x] for x in suite)


def _gele_deterministe(y, plan="ordre_secret", loi=None, bibliotheque=sp.BIBLIOTHEQUE_STANDARD_V1, graine=3, k=3):
    rng = random.Random(graine)
    instances = sp.tirer_instances(rng, len(y))
    loi = loi or {"type": "fixe", "probas": [1.0] * k}
    gele = sp.geler_engagement(sp.construire_engagement("h", loi, instances, k, 0.05, bibliotheque, "continu",
                                                        plan_execution=plan))
    return gele, {"type": "deterministe", "nombre_issues": k, "issues": list(y)}


class Urne(unittest.TestCase):
    def test_trajectoire_contre_enumeration_exhaustive(self):
        for k in (2, 3):
            for n in range(1, 7):
                for suite in itertools.product(range(k), repeat=n):
                    traj = sp.trajectoire_membre({"nom": "urne", "type": "urne"}, list(suite), [None] * n, k)
                    for t in range(1, n + 1):
                        prefixe = collections.Counter(suite[:t])
                        meme_composition = sum(1 for autre in itertools.product(range(k), repeat=t)
                                               if collections.Counter(autre) == prefixe)
                        self.assertAlmostEqual(traj[t - 1], -math.log(meme_composition), places=10)

    def test_urne_domine_les_lois_echangeables_et_atteint_la_borne(self):
        rng = random.Random(5)
        k, n = 3, 6
        for _ in range(20):
            p = [rng.random() + 0.01 for _ in range(k)]
            p = [x / sum(p) for x in p]
            alpha0 = [rng.random() * 2 + 0.05 for _ in range(k)]
            composition = [0] * k
            for _ in range(n):
                composition[rng.randrange(k)] += 1
            hyper = {"type": "sans_remise", "composition": composition}
            for suite in itertools.product(range(k), repeat=n):
                traj = sp.trajectoire_membre({"nom": "urne", "type": "urne"}, list(suite), [None] * n, k)
                for t in range(1, n + 1):
                    borne = math.exp(traj[t - 1]) * (1 + 1e-9)
                    prefixe = suite[:t]
                    self.assertLessEqual(_iid(p, prefixe), borne)
                    self.assertLessEqual(_polya(alpha0, prefixe), borne)
                    self.assertLessEqual(_proba_suite(hyper, prefixe, k), borne)
                if [suite.count(j) for j in range(k)] == composition:  # borne atteinte à t = n (au plancher 1e-12 près)
                    self.assertAlmostEqual(_proba_suite(hyper, suite, k), math.exp(traj[-1]), delta=1e-10)

    def test_urne_domine_la_marginale_ajustee(self):
        rng = random.Random(6)
        for _ in range(50):
            issues = [rng.randrange(3) for _ in range(rng.randrange(1, 300))]
            urne = sp.trajectoire_membre({"nom": "urne", "type": "urne"}, issues, [None] * len(issues), 3)
            marginale = sp.trajectoire_membre({"nom": "m", "type": "marginale_mv"}, issues, [None] * len(issues), 3)
            for u, m in zip(urne, marginale):
                self.assertGreaterEqual(u, m - 1e-9)

    def test_loi_composition_jamais_promue_par_le_juge_v1(self):
        rng = random.Random(7)
        for _ in range(30):
            oracle, y = monde_structure(rng, "calendrier_deterministe", 200)
            loi = {"type": "sans_remise", "composition": [y.count(j) for j in range(3)]}
            gele, monde = _gele_deterministe(y, loi=loi, graine=rng.randrange(10 ** 6))
            noyau = rng.randrange(10 ** 9)
            ev = sp.evaluer(gele, sp.tirer_frais(gele, monde, 1, graine_noyau=noyau), graine_noyau=noyau)
            self.assertLessEqual(ev["log_richesse_max"], 1e-9)
            self.assertFalse(ev["promue"])

    def test_bibliotheque_v1_garde_les_membres_de_v0(self):
        self.assertEqual(sp.BIBLIOTHEQUE_STANDARD_V1[:len(sp.BIBLIOTHEQUE_STANDARD)], sp.BIBLIOTHEQUE_STANDARD)
        self.assertEqual(sp.BIBLIOTHEQUE_STANDARD_V1[-1], {"nom": "urne", "type": "urne"})


class OrdreSecret(unittest.TestCase):
    def test_issues_rangees_par_indice_du_plan(self):
        rng = random.Random(8)
        y = [rng.randrange(3) for _ in range(120)]
        gele, monde = _gele_deterministe(y)
        tirages = sp.tirer_frais(gele, monde, 1, graine_noyau=42)
        pi = sp.ordre_execution(42, gele.empreinte, len(y))
        self.assertEqual(sorted(pi), list(range(len(y))))
        self.assertNotEqual(pi, list(range(len(y))))
        for s, i in enumerate(pi):
            self.assertEqual(tirages["issues"][i], y[s])
        self.assertEqual(tirages["empreinte_ordre"], empreinte_objet(pi))
        self.assertEqual(tirages["plan_execution"], "ordre_secret")

    def test_ordre_naturel_garde_l_ordre_du_plan(self):
        rng = random.Random(9)
        y = [rng.randrange(3) for _ in range(50)]
        gele, monde = _gele_deterministe(y, plan="ordre_naturel", bibliotheque=sp.BIBLIOTHEQUE_STANDARD)
        tirages = sp.tirer_frais(gele, monde, 1)
        self.assertEqual(tirages["issues"], y)
        self.assertNotIn("empreinte_ordre", tirages)

    def test_ordre_depend_du_noyau_et_de_l_engagement(self):
        a = sp.ordre_execution(1, "e" * 64, 100)
        self.assertEqual(a, sp.ordre_execution(1, "e" * 64, 100))
        self.assertNotEqual(a, sp.ordre_execution(2, "e" * 64, 100))
        self.assertNotEqual(a, sp.ordre_execution(1, "f" * 64, 100))
        with self.assertRaises(sp.PlanExecutionNonConforme):
            sp.ordre_execution(None, "e" * 64, 100)

    def test_le_monde_voit_le_temps_et_l_instance_permutee(self):
        vus = []
        rng = random.Random(10)
        instances = sp.tirer_instances(rng, 30)
        for i, x in enumerate(instances):
            x["z"][0] = float(i)  # l'indice du plan, lisible dans le premier trait (essai seulement)
        gele = sp.geler_engagement(sp.construire_engagement("h", {"type": "fixe", "probas": [1, 1, 1]}, instances, 3,
                                                            0.05, sp.BIBLIOTHEQUE_STANDARD_V1, plan_execution="ordre_secret"))
        original = sp.proba

        def proba_espion(loi, instance, historique, t):
            if loi.get("type") == "espion":
                vus.append((int(instance["z"][0]), t, len(historique)))
                return [1 / 3] * 3
            return original(loi, instance, historique, t)

        sp.proba = proba_espion
        try:
            sp.tirer_frais(gele, {"type": "espion"}, 1, graine_noyau=11)
        finally:
            sp.proba = original
        pi = sp.ordre_execution(11, gele.empreinte, 30)
        self.assertEqual(vus, [(pi[s], s, s) for s in range(30)])

    def test_heure_jamais_trait_d_instance_sous_ordre_secret(self):
        rng = random.Random(12)
        instances = sp.tirer_instances(rng, 10)
        instances[3]["t"] = 3
        loi = {"type": "fixe", "probas": [1, 1, 1]}
        with self.assertRaises(ValueError):
            sp.construire_engagement("h", loi, instances, 3, plan_execution="ordre_secret")
        sp.construire_engagement("h", loi, instances, 3, plan_execution="ordre_naturel")  # v0 inchangé
        with self.assertRaises(ValueError):
            sp.construire_engagement("h", loi, sp.tirer_instances(rng, 5), 3, plan_execution="ordre_au_hasard")


class GardeDuPlanExecution(unittest.TestCase):
    """R5 : la garde est essayée sur un cas sain et sur des artefacts."""

    def setUp(self):
        rng = random.Random(13)
        self.y = [rng.randrange(3) for _ in range(80)]
        self.gele, self.monde = _gele_deterministe(self.y)
        self.tirages = sp.tirer_frais(self.gele, self.monde, 1, graine_noyau=99)

    def test_cas_sain_accepte(self):
        ev = sp.evaluer(self.gele, self.tirages, graine_noyau=99)
        self.assertEqual(ev["plan_execution"], "ordre_secret")

    def test_artefacts_refuses(self):
        def variante(**modifs):
            t = dict(self.tirages)
            for cle, valeur in modifs.items():
                if valeur is None:
                    t.pop(cle, None)
                else:
                    t[cle] = valeur
            return t

        cas = {
            "issues déclarées sous l'ordre naturel": (variante(plan_execution="ordre_naturel"), 99),
            "plan absent des tirages": (variante(plan_execution=None), 99),
            "empreinte d'ordre absente": (variante(empreinte_ordre=None), 99),
            "empreinte d'ordre fausse": (variante(empreinte_ordre="0" * 64), 99),
            "graine du noyau absente": (self.tirages, None),
            "graine du noyau différente": (self.tirages, 98),
        }
        for nom, (tirages, noyau) in cas.items():
            with self.subTest(cas=nom), self.assertRaises(sp.PlanExecutionNonConforme):
                sp.evaluer(self.gele, tirages, graine_noyau=noyau)

    def test_ordre_naturel_refuse_des_issues_declarees_sous_ordre_secret(self):
        gele, monde = _gele_deterministe(self.y, plan="ordre_naturel", bibliotheque=sp.BIBLIOTHEQUE_STANDARD)
        tirages = sp.tirer_frais(gele, monde, 1)
        sp.evaluer(gele, tirages)
        sp.evaluer(gele, {k: v for k, v in tirages.items() if k != "plan_execution"})  # v0 : champ absent = naturel
        with self.assertRaises(sp.PlanExecutionNonConforme):
            sp.evaluer(gele, dict(tirages, plan_execution="ordre_secret"))

    def test_refus_rattrape_comme_tirages_non_lies_par_le_cycle(self):
        self.assertTrue(issubclass(sp.PlanExecutionNonConforme, sp.TiragesNonLies))


class LoisNouvelles(unittest.TestCase):
    def test_sans_remise(self):
        loi = sp.valider_loi({"type": "sans_remise", "composition": [2, 1, 0]}, 3)
        p = sp.proba(loi, None, [0, 1], 2)
        self.assertAlmostEqual(p[0], 1.0, places=9)
        p = sp.proba(loi, None, [0], 1)
        self.assertAlmostEqual(p[0], 0.5, places=9)
        self.assertAlmostEqual(p[1], 0.5, places=9)
        p = sp.proba(loi, None, [0, 0, 1], 3)  # composition épuisée : plancher, donc uniforme
        self.assertAlmostEqual(p[2], 1 / 3, places=9)
        for mauvaise in ({"type": "sans_remise", "composition": [1, 1]}, {"type": "sans_remise", "composition": [0, 0, 0]},
                         {"type": "sans_remise", "composition": [1, -1, 1]}, {"type": "sans_remise", "composition": [1.5, 1, 1]}):
            with self.subTest(loi=mauvaise), self.assertRaises(sp.LoiInvalide):
                sp.valider_loi(mauvaise, 3)

    def test_calendrier_et_deterministe(self):
        cal = sp.valider_loi({"type": "calendrier", "probas": [[1, 0, 0], [0.2, 0.3, 0.5]]}, 3)
        self.assertAlmostEqual(sp.proba(cal, None, [], 1)[2], 0.5, places=9)
        with self.assertRaises(sp.LoiInvalide):
            sp.proba(cal, None, [], 2)
        det = sp.valider_loi({"type": "deterministe", "nombre_issues": 3, "issues": [2, 0]}, 3)
        self.assertGreater(sp.proba(det, None, [], 0)[2], 1 - 1e-9)
        for mauvaise in ({"type": "calendrier", "probas": []}, {"type": "calendrier", "probas": [[1, 1]]},
                         {"type": "deterministe", "nombre_issues": 3, "issues": [3]},
                         {"type": "deterministe", "nombre_issues": 2, "issues": [0]}):
            with self.subTest(loi=mauvaise), self.assertRaises(sp.LoiInvalide):
                sp.valider_loi(mauvaise, 3)

    def test_mondes_de_la_batterie(self):
        rng = random.Random(14)
        for structure in STRUCTURES:
            with self.subTest(structure=structure):
                oracle, y = monde_structure(rng, structure, 200)
                self.assertEqual(len(y), 200)
                self.assertTrue(all(x in (0, 1, 2) for x in y))
                sp.valider_loi(oracle, 3)
        _, y = monde_structure(random.Random(1), "calendrier_deterministe", 200)
        self.assertEqual(sorted(collections.Counter(y).values()), [60, 60, 80])
        with self.assertRaises(ValueError):
            monde_structure(rng, "inconnue", 10)


class ExperienceEtLecture(CasAvecDossier):
    def test_gardes_de_l_experience_decisive(self):
        with self.assertRaises(ValueError):
            executer_controles_v1(GRAINE_ESSAI, repetitions=999)
        with self.assertRaises(ValueError):
            executer_controles_v1(GRAINE_EXPLORATION_V0, repetitions=1000)
        with self.assertRaises(ValueError):
            executer_controles_v1(GRAINE_ESSAI_FUMEE, repetitions=1000)
        with self.assertRaises(ValueError):
            executer_controles_v1(GRAINE_ESSAI, repetitions=1000, familles=("T1b",))

    def test_fumee_batterie_t1b(self):
        """Essai de fumée (graine d'essai, 40 répétitions, 60 tirages) : il éprouve le code, il ne mesure rien."""
        r = executer_controles_v1(GRAINE_ESSAI, repetitions=40, tirages=60, essai=True, familles=("T1b",))
        lignes = {(l["controle"], l["juge"]): l for l in r["lignes"]}
        self.assertEqual(r["verdicts"]["issue"], ISSUE_ESSAI)
        for structure in STRUCTURES:
            composition = lignes[(f"T1b-{structure}-loi-composition", "v1")]
            self.assertEqual(composition["promotions"], 0)
            self.assertLessEqual(composition["log_richesse_max_observee"], 1e-9)
            self.assertEqual(composition["plan_execution_observe"], {"ordre_secret": 40})
            self.assertEqual(composition["empreintes_ordre_distinctes"], 40)
            self.assertEqual(len(composition["promotions_par_repetition"]), 40)
            self.assertEqual(composition["promotions_par_repetition"].count("1"), composition["promotions"])
        self.assertGreaterEqual(lignes[("T1b-calendrier_deterministe-loi-composition", "v1_sans_urne")]["taux"], 0.8)
        self.assertGreaterEqual(lignes[("T1b-calendrier_deterministe-loi-calendrier", "v0")]["taux"], 0.8)
        self.assertGreaterEqual(lignes[("artefact-permutation-de-l-ordre-d-evaluation", "v1_permutation_evaluation")]["taux"], 0.8)
        self.assertLessEqual(max(l["taux"] for l in r["lignes"] if l["role"] == "fatal"), 0.2)

    def test_lecture_gelee(self):
        def ligne(nom, juge, role, taux, **extra):
            return dict({"controle": nom, "juge": juge, "role": role, "taux": taux}, **extra)

        def issues(lignes, complet=True):
            v = juger_v1({"lignes": lignes}, 0.05, complet)
            return v["issue"], v["parties"]["socle"]["issue"], v["parties"]["filles"]["issue"]

        base = [ligne("T1a-nul-marginale", "v1", "fatal", 0.01),
                ligne("T1b-derive_lineaire-loi-calendrier", "v1", "fatal", 0.0),
                ligne("T1b-derive_lineaire-loi-calendrier", "v0", "artefact_requis", 0.6),
                ligne("T3-couvert-eps0.2-net-vrai", "v1", "puissance_decisive", 0.97),
                ligne("T9-disjonction-partitionnee", "v1", "fatal", 0.0, passe=True),
                ligne("T1b-fille", "v1", "fatal", 0.01),
                ligne("artefact-fille-sans-parents-dans-le-nul-forme", "v1", "artefact_requis", 0.4),
                ligne("puissance-fille-neuve", "v1", "puissance_decisive", 0.95),
                ligne("puissance-fille-neuve", "v0", "descriptif", 0.99)]
        self.assertEqual(issues(base), ("adopté", "adopté", "adopté"))

        def modifie(nom, juge="v1", **champs):
            return [dict(l, **champs) if (l["controle"], l["juge"]) == (nom, juge) else l for l in base]

        self.assertEqual(issues(modifie("T1b-fille", taux=0.06)), ("non adopté", "adopté", "non adopté"))
        self.assertEqual(juger_v1({"lignes": modifie("T1b-fille", taux=0.06)}, 0.05)["ce_qui_a_cede"], ["T1b-fille"])
        self.assertEqual(issues(modifie("T1a-nul-marginale", taux=0.06)), ("non adopté", "non adopté", "adopté"))
        self.assertEqual(issues(modifie("T9-disjonction-partitionnee", passe=False)), ("non adopté", "adopté", "non adopté"))
        self.assertEqual(issues(modifie("puissance-fille-neuve", taux=0.89)), ("non adopté", "adopté", "non adopté"))
        self.assertEqual(issues(modifie("T3-couvert-eps0.2-net-vrai", taux=0.89)), ("non adopté", "non adopté", "adopté"))
        self.assertEqual(issues(modifie("T1b-derive_lineaire-loi-calendrier", "v0", taux=0.05)),
                         ("non concluant", "non concluant", "adopté"))
        self.assertEqual(issues(base, complet=False), (ISSUE_ESSAI,) * 3)
        self.assertAlmostEqual(juger_v1({"lignes": base}, 0.05)["perte_de_puissance_fille_neuve"]["v0_moins_v1"], 0.04)
        self.assertEqual([partie_de(n) for n in ("tricheur-parent_et_loi_aveugle", "T1b-fille", "T1b-rupture-loi-calendrier",
                                                 "artefact-permutation-de-l-ordre-d-evaluation", "T9-disjonction-partitionnee")],
                         ["filles", "filles", "socle", "socle", "filles"])

    def test_ligne_de_commande(self):
        sortie = self.sous_dossier("experience")
        erreurs = io.StringIO()
        with contextlib.redirect_stderr(erreurs):
            self.assertEqual(principal(["--experience-juge-v1", "--sortie", sortie]), 2)
            self.assertEqual(principal(["--experience-juge-v1", "--sortie", sortie, "--graine-maitresse", "5",
                                        "--familles", "T9"]), 2)
            self.assertEqual(principal(["--experience-juge-v1", "--sortie", sortie, "--graine-maitresse",
                                        str(GRAINE_EXPLORATION_V0)]), 2)
        self.assertEqual(os.listdir(sortie), [], "un lancement refusé n'écrit rien")
        sortie_essai = os.path.join(self.tmp, "essai")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(principal(["--experience-juge-v1", "--sortie", sortie_essai, "--graine-maitresse",
                                        str(GRAINE_ESSAI), "--essai", "--repetitions", "20", "--familles", "T9",
                                        "--horodatage", "2026-10-27T00:00:00Z"]), 0)
        noms = sorted(os.listdir(sortie_essai))
        self.assertEqual(noms, sorted(["manifeste.json", "manifeste.json.sha256", "experience-1-juge-v1-ESSAI.json",
                                       "experience-1-juge-v1-ESSAI.json.sha256", "experience-1-juge-v1-ESSAI.md",
                                       "experience-1-juge-v1-ESSAI.md.sha256"]))
        for nom in ("manifeste.json", "experience-1-juge-v1-ESSAI.json", "experience-1-juge-v1-ESSAI.md"):
            self.assertTrue(verifier_scelle(os.path.join(sortie_essai, nom)))
        with open(os.path.join(sortie_essai, "manifeste.json"), encoding="utf-8") as f:
            self.assertIn("controles_pari_v1.py", json.load(f)["code_sha256"])
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(principal(["--experience-juge-v1", "--sortie", sortie_essai, "--graine-maitresse",
                                        str(GRAINE_ESSAI), "--essai", "--repetitions", "20", "--familles", "T9"]), 2)

    def test_juges_declares(self):
        self.assertEqual(JUGES["v1"]["plan_execution"], "ordre_secret")
        self.assertIn({"nom": "urne", "type": "urne"}, JUGES["v1"]["bibliotheque"])
        self.assertNotIn({"nom": "urne", "type": "urne"}, JUGES["v1_sans_urne"]["bibliotheque"])
        self.assertEqual(JUGES["v0"]["plan_execution"], "ordre_naturel")


class TraitementContreLectureCl1(unittest.TestCase):
    """Corrections de la contre-lecture cl1 : CJ1-02 (conformité), CJ1-03 (plan observé), CJ1-04 (appariement),
    CJ1-05 (limite de la garde), CJ1-13 et CJ1-16 (paramètres refusés), déclencheurs de l'audit de symétrie."""

    @staticmethod
    def _rapport_complet(repetitions=1000):
        lignes = []
        for nom, juge in sorted(ROSTER_V1):
            role = "descriptif"
            lignes.append({"controle": nom, "juge": juge, "role": role, "taux": 0.0, "promotions": 0,
                           "repetitions": repetitions})
        return {"lignes": lignes}

    def test_inventaire_des_70_lignes_egal_au_code(self):
        r = executer_controles_v1(GRAINE_ESSAI, repetitions=2, tirages=40, part_calibrage=15, essai=True)
        self.assertEqual({(l["controle"], l["juge"]) for l in r["lignes"]}, ROSTER_V1)
        self.assertEqual(len(r["lignes"]), 70)

    def test_conformite_cas_sain_et_artefacts(self):
        sain = self._rapport_complet()
        v = juger_v1(sain, 0.05, complet=True, roster=ROSTER_V1, repetitions_attendues=1000)
        self.assertTrue(v["conformite"]["conforme"])
        self.assertNotEqual(v["issue"], ISSUE_INCOMPLETE)
        vide = {"lignes": []}
        self.assertEqual(juger_v1(vide, 0.05, complet=True, roster=ROSTER_V1, repetitions_attendues=1000)["issue"],
                         ISSUE_INCOMPLETE)
        manque = {"lignes": sain["lignes"][1:]}
        v = juger_v1(manque, 0.05, complet=True, roster=ROSTER_V1, repetitions_attendues=1000)
        self.assertEqual((v["issue"], v["parties"]["socle"]["issue"], v["parties"]["filles"]["issue"]), (ISSUE_INCOMPLETE,) * 3)
        self.assertEqual(len(v["conformite"]["lignes_manquantes"]), 1)
        courte = {"lignes": [dict(l, repetitions=7) if i == 0 else l for i, l in enumerate(sain["lignes"])]}
        self.assertEqual(juger_v1(courte, 0.05, complet=True, roster=ROSTER_V1, repetitions_attendues=1000)["issue"],
                         ISSUE_INCOMPLETE)
        double = {"lignes": sain["lignes"] + sain["lignes"][:1]}
        self.assertEqual(juger_v1(double, 0.05, complet=True, roster=ROSTER_V1, repetitions_attendues=1000)["issue"],
                         ISSUE_INCOMPLETE)

    def test_plan_observe_controle_cas_sain_et_artefact(self):
        def scenario_conforme(rng, juge):
            loi = sp.loi_softmax_aleatoire(rng)
            instances = sp.tirer_instances(rng, 40)
            return cv1._geler(loi, instances, 3, 0.05, juge), {"type": "fixe", "probas": [1, 1, 1]}

        def scenario_naturel_sous_v1(rng, juge):
            loi = sp.loi_softmax_aleatoire(rng)
            instances = sp.tirer_instances(rng, 40)
            gele = sp.geler_engagement(sp.construire_engagement("h", loi, instances, 3, 0.05, sp.BIBLIOTHEQUE_STANDARD_V1,
                                                                "continu", plan_execution="ordre_naturel"))
            return gele, {"type": "fixe", "probas": [1, 1, 1]}

        ligne = cv1._executer("essai", "v1", "fatal", 5, 6, scenario_conforme, "essai")
        self.assertEqual(ligne["plan_execution_observe"], {"ordre_secret": 6})
        self.assertEqual(ligne["empreintes_ordre_distinctes"], 6)
        with self.assertRaises(cv1.PlanObserveNonConforme):
            cv1._executer("essai", "v1", "fatal", 5, 6, scenario_naturel_sous_v1, "essai")

    def test_limite_documentee_de_la_garde_du_plan(self):
        """CJ1-05 : la garde refuse un étiquetage non conforme, pas une provenance ; une empreinte d'ordre recopiée est
        acceptée. C'est une limite écrite (l'imposition de l'ordre par le noyau réel n'est pas codée), pas un refus."""
        rng = random.Random(15)
        y = [rng.randrange(3) for _ in range(60)]
        gele, monde = _gele_deterministe(y)
        produites_sous_8 = sp.tirer_frais(gele, monde, 1, graine_noyau=8)
        sous_7 = sp.tirer_frais(gele, monde, 1, graine_noyau=7)
        maquillees = dict(produites_sous_8, empreinte_ordre=sous_7["empreinte_ordre"])
        sp.evaluer(gele, maquillees, graine_noyau=7)  # acceptée : limite documentée

    def test_appariement_et_declencheurs_r4(self):
        def l(nom, juge, role="descriptif", promotions=0, chaine=None, **extra):
            d = {"controle": nom, "juge": juge, "role": role, "taux": promotions / 4, "promotions": promotions,
                 "repetitions": 4}
            if chaine is not None:
                d["promotions_par_repetition"] = chaine
            d.update(extra)
            return d

        lignes = [l("puissance-fille-neuve", "v0", chaine="1111", promotions=4),
                  l("puissance-fille-neuve", "v1", chaine="1101", promotions=3),
                  l("T1b-rupture-loi-composition", "v1", "fatal", 1, log_richesse_max_observee=3.5,
                    membre_dominant_final={"urne": 4}, plan_execution_observe={"ordre_secret": 4},
                    empreintes_ordre_distinctes=4),
                  l("T1a-nul-marginale", "v1", "fatal", 0, membre_dominant_final={"marginale_empirique": 4},
                    plan_execution_observe={"ordre_naturel": 4}, empreintes_ordre_distinctes=0)]
        v = juger_v1({"lignes": lignes}, 0.05)
        self.assertEqual(v["appariement_v0_v1_repetitions_differentes"], {"puissance-fille-neuve": 1})
        texte = " | ".join(v["declencheurs_R4"])
        self.assertIn("composition promue", texte)
        self.assertIn("urne jamais dominante", texte)
        self.assertIn("plan observé autre que l'ordre secret", texte)
        egal = [l("puissance-fille-neuve", "v0", chaine="1101"), l("puissance-fille-neuve", "v1", chaine="1101")]
        self.assertIn("égales une à une", " ".join(juger_v1({"lignes": egal}, 0.05)["declencheurs_R4"]))
        sain = [l("puissance-fille-neuve", "v0", chaine="1111"), l("puissance-fille-neuve", "v1", chaine="1101"),
                l("T1a-nul-marginale", "v1", "fatal", 1, membre_dominant_final={"urne": 4},
                  plan_execution_observe={"ordre_secret": 4}, empreintes_ordre_distinctes=4)]
        self.assertEqual(juger_v1({"lignes": sain}, 0.05)["declencheurs_R4"], [])

    def test_parametres_refuses_cj1_13_et_cj1_16(self):
        for graine in (4242, 31337, 2718, 170141183460469231731687303715884204893, 20261027, 20261028):
            with self.subTest(graine=graine), self.assertRaises(ValueError):
                cv1.verifier_parametres(graine, 1000)
        with self.assertRaises(ValueError):
            cv1.verifier_parametres(123456789, 1500)
        cv1.verifier_parametres(123456789, 1000)  # cas sain


if __name__ == "__main__":
    unittest.main()
