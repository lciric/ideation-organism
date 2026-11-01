"""Essais du cœur du pari apparié borné (v7, version 20) : règle double, validité sous nuls asymétriques de moyenne nulle,
intersection-union, garde, arrêt au seuil, sans remise, borne basse de confiance."""

import math
import random
import unittest

from pole import pari_apparie as pa


def tirer(rng, valeurs, probas, n):
    return [rng.choices(valeurs, probas)[0] for _ in range(n)]


class RegleDouble(unittest.TestCase):
    def test_coefficients(self):
        self.assertTrue(pa.verifier_coefficients({"A": 1, "B": -1}))
        self.assertTrue(pa.verifier_coefficients({"Af": 0.5, "Bf": -0.5, "An": -0.5, "Bn": 0.5}))  # interaction (C11)
        self.assertTrue(pa.verifier_coefficients({"A": 1}, constante=-0.4))  # rappel ≥ x
        for coefs, c in (({"A": 1, "B": 1}, 0.0), ({"A": 1, "B": -1}, 0.5), ({"A": -1, "B": -1}, 0.0), ({}, 0.0)):
            with self.subTest(coefs=coefs, c=c), self.assertRaises(pa.ContrasteInvalide):
                pa.verifier_coefficients(coefs, c)

    def test_contraste_et_bornes(self):
        self.assertAlmostEqual(pa.contraste({"A": 0.6, "B": 0.4}, {"A": 1, "B": -1}), 0.2)
        with self.assertRaises(pa.ContrasteInvalide):
            pa.contraste({"A": 1.2, "B": 0.4}, {"A": 1, "B": -1})
        with self.assertRaises(pa.ContrasteInvalide):
            pa.trajectoire_log_richesse([0.5, 1.5])


class Validite(unittest.TestCase):
    def test_nuls_asymetriques_de_moyenne_nulle(self):
        """S1 (90 % à +0,1, 10 % à −0,9) et S2 (80 % à +0,1, 20 % à −0,4) : promotion ≤ α (borne large : 0,08)."""
        rng = random.Random(20261027)
        for valeurs, probas in (([0.1, -0.9], [0.9, 0.1]), ([0.1, -0.4], [0.8, 0.2])):
            promus = sum(pa.evaluer({"B": tirer(rng, valeurs, probas, 150)})["promue"] for _ in range(300))
            self.assertLessEqual(promus / 300, 0.08, (valeurs, promus))

    def test_puissance_vingt_points(self):
        rng = random.Random(7)
        promus = 0
        for _ in range(100):
            v = [(sum(rng.random() < 0.6 for _ in range(10)) - sum(rng.random() < 0.4 for _ in range(10))) / 10 for _ in range(60)]
            promus += pa.evaluer({"B": v})["promue"]
        self.assertGreaterEqual(promus, 90)  # simulation v2 : 1,00 à 60 unités

    def test_intersection_union(self):
        """Un comparateur au nul (moyenne nulle) et un battu largement : la fiche ne doit pas être promue (≤ α)."""
        rng = random.Random(11)
        promus = 0
        for _ in range(300):
            facile = [0.6] * 80
            nul = tirer(rng, [0.1, -0.9], [0.9, 0.1], 80)
            promus += pa.evaluer({"facile": facile, "nul": nul})["promue"]
        self.assertLessEqual(promus / 300, 0.08)
        self.assertTrue(pa.evaluer({"a": [0.6] * 40, "b": [0.5] * 40})["promue"])

    def test_garde_bloque_le_tricheur(self):
        """A rappelle plus mais tire plus que B de 10 points (E[g] = 0,10 ≥ δ = 0,05) : jamais promu."""
        rng = random.Random(13)
        promus = 0
        for _ in range(200):
            v = [0.5] * 80
            g = [0.1 + rng.uniform(-0.02, 0.02) for _ in range(150)]
            promus += pa.evaluer({"B": v}, ecarts_faux_positifs=g, delta=0.05)["promue"]
        self.assertEqual(promus, 0)
        g_sain = [0.0] * 150
        self.assertTrue(pa.evaluer({"B": [0.5] * 80}, ecarts_faux_positifs=g_sain, delta=0.05)["promue"])

    def test_arret_au_seuil_m_sur_alpha(self):
        r1 = pa.evaluer({"B": [1.0] * 30}, m=1)
        r10 = pa.evaluer({"B": [1.0] * 30}, m=10)
        self.assertEqual(r1["instant_d_arret"], 7)  # moyenne de 1,1^t, 1,3^t, 1,6^t, 1,9^t ≥ 20 dès t = 7
        self.assertGreater(r10["instant_d_arret"], r1["instant_d_arret"])
        self.assertAlmostEqual(r1["log_e_valeur"], r1["trajectoire_log_min"][6])

    def test_sans_remise(self):
        """Banque figée de moyenne exactement nulle, lue dans des ordres uniformes : promotion ≤ α (borne large)."""
        rng = random.Random(17)
        banque = [0.1] * 90 + [-0.9] * 10
        promus = 0
        for _ in range(300):
            rng.shuffle(banque)
            promus += max(pa.trajectoire_log_sans_remise(banque)) >= math.log(20)
        self.assertLessEqual(promus / 300, 0.08)

    def test_borne_basse(self):
        rng = random.Random(19)
        couvertes = 0
        for _ in range(100):
            v = [rng.choice([0.4, 0.0]) for _ in range(200)]  # moyenne 0,2
            b = pa.borne_basse(v)
            couvertes += b <= 0.2
            self.assertGreater(b, -1.0)
        self.assertGreaterEqual(couvertes, 92)


def ebh_ordinaire(e, alpha):
    """Référence : règle e-BH ordinaire (m fiches, niveau α), écrite indépendamment."""
    m = len(e)
    ordre = sorted(e, key=lambda i: -e[i])
    k_etoile = max([k for k in range(1, m + 1) if e[ordre[k - 1]] >= m / (alpha * k)], default=0)
    return set(ordre[:k_etoile])


def marche_a_prime(rng, pas):
    """Monde A′ de la contre-lecture v5 : martingale ×1,5 / ×0,5 à pile ou face ; trajectoire du log."""
    lw, traj = 0.0, []
    for _ in range(pas):
        lw += math.log(1.5) if rng.random() < 0.5 else math.log(0.5)
        traj.append(lw)
    return traj


class PlafondDS27(unittest.TestCase):
    def test_bornes_et_coincidence(self):
        self.assertEqual(pa.ponderation_plafonnee(5, 20), 0.25)
        self.assertEqual(pa.ponderation_plafonnee(100, 20), 1.0)
        v = pa.contraste({"A": 0.2, "B": 0.9}, {"A": 1, "B": -1})
        self.assertAlmostEqual(pa.contraste_plafonne({"A": 0.2, "B": 0.9}, {"A": 1, "B": -1}, 0.0, 10, 20), 0.5 * v)
        self.assertAlmostEqual(pa.contraste_plafonne({"A": 0.2, "B": 0.9}, {"A": 1, "B": -1}, 0.0, 400, 20), v)
        for args in ((-1, 20), (5, 0), (2.5, 20)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                pa.ponderation_plafonnee(*args)


class HeritageDS25bis(unittest.TestCase):
    def test_ebh_pondere_egale_l_ordinaire_pour_une_famille(self):
        rng = random.Random(23)
        for _ in range(300):
            m = rng.randint(1, 8)
            e = {i: math.exp(rng.uniform(-2, 7)) for i in range(m)}
            attendu = ebh_ordinaire(e, 0.05)
            obtenu = pa.ebh_pondere({i: math.log(x) for i, x in e.items()}, {i: 0.05 / m for i in e})
            self.assertEqual(obtenu, attendu, e)
        self.assertEqual(pa.ebh_pondere({"a": math.log(100), "b": math.log(50), "c": math.log(10), "d": 0.0},
                                        {k: 0.0125 for k in "abcd"}), {"a", "b"})

    def test_budgets_refuses(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b"], 0.03)
        with self.assertRaises(ValueError):
            c.entrer("g2", ["c"], 0.03)  # 0,06 > α
        with self.assertRaises(ValueError):
            c.entrer("g2", ["a"], 0.01)  # une relance n'entre pas une seconde fois
        with self.assertRaises(ValueError):
            pa.ebh_pondere({"a": 0.0}, {"a": 1.5})

    def test_budget_garde_quand_les_soeurs_sont_abandonnees(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b", "c", "d"], 0.04)
        for f in "bcd":
            c.abandonner(f, avant_partie=True)  # abandonnées avant toute partie : la décision n'a vu aucune issue
        self.assertAlmostEqual(c.seuil_log("a"), math.log(4 / 0.04))  # 100, jamais 1/0,04 = 25
        c.ajouter_trajectoire("a", [math.log(30)], unites={(c.generation, "a", i) for i in range(3)})
        self.assertEqual(c.lire(), set())  # 30 < 100 : la lecture « seule » l'aurait promue (30 ≥ 25)
        c.ajouter_trajectoire("a", [math.log(2), math.log(5)], unites={(c.generation, "a", i) for i in range(3)})  # 30 × 5 = 150 ≥ 100 : arrêt au seuil
        self.assertAlmostEqual(c.log_e["a"], math.log(150))
        self.assertIn("a", c.arretees)
        self.assertEqual(c.lire(), {"a"})
        self.assertEqual(c.bonferroni(), {"a"})

    def test_promotion_une_seule_fois_et_gel(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b"], 0.03)
        c.ajouter_trajectoire("a", [math.log(80)], unites={(c.generation, "a", i) for i in range(3)})
        self.assertEqual(c.lire(sans_partie={"b": "non lancée"}), {"a"})
        avant = c.log_e["a"]
        c.ajouter_trajectoire("a", [math.log(0.01)], unites={(c.generation, "a", i) for i in range(3)})  # gelée : rien ne change
        self.assertEqual(c.log_e["a"], avant)
        c.entrer("g2", ["e"], 0.01)
        self.assertEqual(c.lire(sans_partie={"b": "non lancée", "e": "non lancée"}), set())  # « a » reste promue
        self.assertEqual(c.promues, {"a"})

    def test_nul_complet_lecture_valide_contre_lecture_seule(self):
        """Monde A′ (contre-lecture v5, section 7 H) : cohorte de 4 nulles entrée à la génération 1 et relancée,
        3 nouvelles par génération (lues une génération), 10 générations de 20 pas, suite 6/(π²g²), α = 0,05.
        Lecture valide (D-S25 bis) : au plus α ; lecture « seule » de la cohorte à 1/α_1 : plus haut (mécanisme de K5-1 ;
        ici la lecture « seule » vaut dès la génération 1, simplification qui la majore un peu)."""
        rng = random.Random(29)
        alpha, generations, pas, rep = 0.05, 10, 20, 400
        a_g = [alpha * 6 / (math.pi ** 2 * g * g) for g in range(1, generations + 1)]
        fausses_valides = fausses_seules = 0
        for _ in range(rep):
            c = pa.Course(alpha=alpha, essai=True)
            c.entrer("cohorte", [f"c{i}" for i in range(4)], a_g[0])
            cohorte_seule = {f"c{i}": 0.0 for i in range(4)}
            seule_promue = False
            for g in range(generations):
                if g > 0:
                    c.entrer(f"g{g + 1}", [f"n{g}-{j}" for j in range(3)], a_g[g])
                for i in range(4):
                    traj = marche_a_prime(rng, pas)
                    c.ajouter_trajectoire(f"c{i}", traj, unites={(c.generation, f"c{i}", i) for i in range(3)})
                    base = cohorte_seule[f"c{i}"]
                    if base + max(traj) >= -math.log(a_g[0]):
                        seule_promue = True
                    cohorte_seule[f"c{i}"] = base + traj[-1]
                if g > 0:
                    for j in range(3):
                        c.ajouter_trajectoire(f"n{g}-{j}", marche_a_prime(rng, pas), unites={(c.generation, f"n{g}-{j}", i) for i in range(3)})
                c.lire()
                if g > 0:
                    for j in range(3):
                        c.abandonner(f"n{g}-{j}", avant_partie=True)  # après la lecture, avant la génération suivante
            fausses_valides += bool(c.promues)
            fausses_seules += seule_promue
        self.assertLessEqual(fausses_valides / rep, alpha + 0.01)
        self.assertGreaterEqual(fausses_valides, 3)  # K6-6 : la lecture promeut bien quelque chose (attendu ≈ 11)
        self.assertGreater(fausses_seules, fausses_valides)
        self.assertGreater(fausses_seules / rep, 0.04)


class CorrectionsV7(unittest.TestCase):
    """Conception v7 du pari (contre-lecture de la v6) : contrat d'abandon (K6-2), retrait (K6-1), budgets (K6-5),
    ex æquo et abandonnée promue plus tard (K6-6)."""

    def test_contrat_d_abandon(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b", "c", "d"], 0.04)
        c.ajouter_trajectoire("a", [math.log(2)], unites={(c.generation, "a", i) for i in range(3)})
        c.abandonner("a")  # cas sain : la partie de la génération est ajoutée, puis la fiche gelée
        with self.assertRaises(ValueError):
            c.abandonner("b")  # artefact : abandon sans la partie de la génération courante → refus
        c.abandonner("b", trajectoire_log=[math.log(0.5)], unites={(c.generation, "b", i) for i in range(3)})  # la partie passée avec la décision
        self.assertAlmostEqual(c.log_e["b"], math.log(0.5))
        c.abandonner("c", avant_partie=True)
        with self.assertRaises(ValueError):
            c.ajouter_trajectoire("c", [math.log(3)], unites={(c.generation, "c", i) for i in range(3)})  # partie pour une gelée : refus, jamais ignorée
        c.ajouter_trajectoire("d", [math.log(2)], unites={(c.generation, "d", i) for i in range(3)})
        with self.assertRaises(ValueError):
            c.ajouter_trajectoire("d", [math.log(2)], unites={(c.generation, "d", i) for i in range(3)})  # une seule partie par génération
        c.lire()
        c.ajouter_trajectoire("d", [math.log(2)], unites={(c.generation, "d", i) for i in range(3)})  # génération 2 : permis
        self.assertAlmostEqual(c.log_e["d"], math.log(4))

    def test_retrait(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b", "c"], 0.03)
        for f, e in (("a", 200.0), ("b", 200.0), ("c", 60.0)):
            c.ajouter_trajectoire(f, [math.log(e)], unites={(c.generation, f, i) for i in range(3)})
        self.assertEqual(c.lire(), {"a", "b", "c"})  # k* = 3 : c (b·E = 0,6 ≥ 1/3) promue avec ses sœurs
        c.retirer("a", "panne confirmée de la strate")
        self.assertEqual(c.promues, {"a", "b", "c"})  # l'union garantie est celle d'avant les retraits
        self.assertEqual(c.promues_rapportees(), {"b", "c"})
        self.assertNotIn("a", c.bonferroni())
        c.entrer("g2", ["d"], 0.01)
        c.ajouter_trajectoire("d", [math.log(26)], unites={(c.generation, "d", i) for i in range(3)})  # b·E = 0,26 : promue à k = 4 si « a » comptait, pas à k = 3
        self.assertEqual(c.lire(), set())  # « a », retirée, est exclue de la lecture : k* = 2, « d » non promue
        with self.assertRaises(ValueError):
            c.retirer("b", "")

    def test_budgets_au_dessus_de_alpha(self):
        self.assertEqual(pa.ebh_pondere({"a": 0.0, "b": 0.0}, {"a": 0.3, "b": 0.2}), set())  # somme 0,5 ≤ 1 acceptée
        with self.assertRaises(ValueError):
            pa.ebh_pondere({"a": 0.0, "b": 0.0}, {"a": 0.3, "b": 0.2}, alpha=0.05)

    def test_ex_aequo_au_bord_et_abandonnee_promue_plus_tard(self):
        b = 0.05 / 3
        trois = {f: math.log(1 / (3 * b)) for f in "xyz"}  # b·E = 1/3 exactement pour les trois
        self.assertEqual(pa.ebh_pondere(trois, {f: b for f in "xyz"}), {"x", "y", "z"})
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b", "c", "d"], 0.05)  # b = 0,0125
        c.ajouter_trajectoire("d", [math.log(32)], unites={(c.generation, "d", i) for i in range(3)})  # b·E = 0,4
        for f in "abc":
            c.ajouter_trajectoire(f, [0.0], unites={(c.generation, f, i) for i in range(3)})
        self.assertEqual(c.lire(), set())
        c.abandonner("d", avant_partie=True)
        for f in "abc":
            c.ajouter_trajectoire(f, [math.log(80)], unites={(c.generation, f, i) for i in range(3)})  # b·E = 1 : arrêtées au seuil
        self.assertEqual(c.lire(), {"a", "b", "c", "d"})  # k* = 4 : la gelée à 0,4 ≥ 1/4 est promue (voulu, valide)


class CorrectionsV8(unittest.TestCase):
    """Conception v8 du pari (contre-lecture de la v7) : partie sautée (K7-1), unités relues (K7-2), abandon d'une gelée
    et traces (K7-5)."""

    def test_partie_sautee_refusee_a_la_lecture(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b"], 0.04)
        c.ajouter_trajectoire("a", [math.log(3)], unites={(c.generation, "a", i) for i in range(3)})
        with self.assertRaises(ValueError):
            c.lire()  # « b » active sans partie ni déclaration : l'artefact « j'ajoute si ça monte » est refusé
        self.assertEqual(c.lire(sans_partie={"b": "monde indisponible"}), set())  # cas sain : déclaré et tracé
        self.assertEqual(c.sans_partie[(1, "b")], "monde indisponible")

    def test_unites_deja_lues_refusees(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a"], 0.04)
        c.ajouter_trajectoire("a", [math.log(2)], unites={"u-1", "u-2", "u-3"})
        c.lire()
        with self.assertRaises(ValueError):
            c.ajouter_trajectoire("a", [math.log(2)], unites={"u-3", "u-4"})  # K8-1 : une unité en commun suffit au refus
        with self.assertRaises(ValueError):
            c.ajouter_trajectoire("a", [math.log(2)])  # K8-1 : sans identité ni déclaration → refus
        c.ajouter_trajectoire("a", [math.log(2)], unites={"u-4", "u-5"})  # disjointes : acceptées
        c.lire()
        c.ajouter_trajectoire("a", [0.0], sans_identite=True)  # déclaré : accepté et tracé
        self.assertEqual(c.parties_sans_identite, [(3, "a")])

    def test_abandon_d_une_gelee_et_traces(self):
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a", "b"], 0.04)
        c.abandonner("a", avant_partie=True, motif="hors sujet")
        with self.assertRaises(ValueError):
            c.abandonner("a", trajectoire_log=[math.log(5)], unites={(c.generation, "a", i) for i in range(3)})  # partie pour une gelée : refus, plus jamais en silence
        c.abandonner("a", motif="redite")  # sans partie : sans effet, mais tracé (K8-3)
        self.assertEqual(c.abandons["a"], (1, "avant_partie", "hors sujet"))
        self.assertEqual(c.abandons[("redite", "a")], [(1, "redite")])
        c.ajouter_trajectoire("b", [math.log(2)], unites={(c.generation, "b", i) for i in range(3)})
        c.abandonner("b")
        self.assertEqual(c.abandons["b"][1], "apres_partie")
        c.retirer("b", "panne")
        c.retirer("b", "panne confirmée")
        self.assertEqual([m for _, m in c.retirees["b"]], ["panne", "panne confirmée"])


class TestGardeNonFinie(unittest.TestCase):
    """v39 (R5) : un écart de faux positifs NaN ou infini est refusé ; il valait +1 (favorable) avant."""

    def test_nan_et_infini_refuses(self):
        from pole.pari_apparie import ContrasteInvalide, trajectoire_log_garde
        for g in (float("nan"), float("inf"), -float("inf"), None, "0.1", True):
            with self.assertRaises((ContrasteInvalide, TypeError)):
                trajectoire_log_garde([0.0, g, 0.0], 0.05)
        self.assertEqual(len(trajectoire_log_garde([0.0, 0.1, -0.2], 0.05)), 3)


NAN, INF = float("nan"), float("inf")
NON_FINIS = (NAN, INF, -INF, True, False, None, "0.1")


class TestValeursNonFiniesV40(unittest.TestCase):
    """v40 (CL39-09, relecture CL6 de session-depot) : chaque entrée du juge apparié refuse NaN, ±∞, booléen (et, pour les
    valeurs de contraste, le hors-borne) par `ContrasteInvalide` ; chaque refus a son cas sain, et le comportement sur des
    entrées finies valides ne change pas. Les effets d'avant (v = +1, tri e-BH dérangé, seuil NaN…) sont rappelés."""

    def test_fini(self):
        for x in (0, 1, -3, 0.5, -1e300, 10 ** 400 // 10 ** 399):
            self.assertTrue(pa._fini(x), x)
        for x in NON_FINIS + ([1.0], 10 ** 400):
            self.assertFalse(pa._fini(x), x)
        try:
            import numpy as np
            self.assertTrue(pa._fini(np.float64(0.3)) and pa._fini(np.int64(2)))
            self.assertFalse(pa._fini(np.float64("nan")) or pa._fini(np.bool_(True)))
        except ImportError:
            pass

    def test_verifier_coefficients_constante(self):
        for c in NON_FINIS:  # avant : constante NaN acceptée (comparaisons fausses)
            with self.subTest(constante=c), self.assertRaises(pa.ContrasteInvalide):
                pa.verifier_coefficients({"A": 1}, constante=c)
        self.assertTrue(pa.verifier_coefficients({"A": 1}, constante=-0.4))  # sain
        self.assertTrue(pa.verifier_coefficients({"A": 0.5}, constante=0))  # sain : entier

    def test_contraste_constante_coefficients_et_v(self):
        parts, coefs = {"A": 0.6, "B": 0.4}, {"A": 1, "B": -1}
        for c in NON_FINIS:  # avant : constante NaN → v = +1
            with self.subTest(constante=c), self.assertRaises(pa.ContrasteInvalide):
                pa.contraste(parts, coefs, c)
        for a in (NAN, INF, -INF, True):  # avant : coefficient NaN ou ±∞ → v = +1
            with self.subTest(coefficient=a), self.assertRaises(pa.ContrasteInvalide):
                pa.contraste(parts, {"A": a, "B": -1})
        with self.assertRaises(pa.ContrasteInvalide):  # v avant la borne non fini (dépassement), coefficients finis
            pa.contraste({"A": 1.0}, {"A": 1e308}, 1e308)
        self.assertAlmostEqual(pa.contraste(parts, coefs), 0.2)  # sain
        self.assertAlmostEqual(pa.contraste(parts, coefs, -0.1), 0.1)  # sain : constante finie
        self.assertEqual(pa.contraste({"A": 1.0}, {"A": 2}), 1.0)  # inchangé : v fini hors borne toujours borné

    def test_contraste_plafonne(self):
        parts, coefs = {"A": 0.2, "B": 0.9}, {"A": 1, "B": -1}
        for c in (NAN, INF, -INF, True):
            with self.subTest(constante=c), self.assertRaises(pa.ContrasteInvalide):
                pa.contraste_plafonne(parts, coefs, c, 10, 20)
        for a in (NAN, INF, -INF):
            with self.subTest(coefficient=a), self.assertRaises(pa.ContrasteInvalide):
                pa.contraste_plafonne(parts, {"A": a, "B": -1}, 0.0, 10, 20)
        # l'effet d'avant : douze unités à coefficient NaN valaient v = +1 et la fiche était promue ; désormais refusées
        with self.assertRaises(pa.ContrasteInvalide):
            pa.evaluer({"B": [pa.contraste_plafonne(parts, {"A": NAN, "B": -1}, 0.0, 20, 20) for _ in range(12)]})
        self.assertAlmostEqual(pa.contraste_plafonne(parts, coefs, 0.0, 10, 20), 0.5 * (0.2 - 0.9))  # sain

    def test_ebh_pondere_log_e_et_budgets(self):
        b = {k: 0.05 / 3 for k in "abc"}
        for x in (NAN, INF, -INF, True, None):  # avant : [0 ; NaN ; 3,0] → trois retenues au lieu d'aucune
            with self.subTest(log_e=x), self.assertRaises(pa.ContrasteInvalide):
                pa.ebh_pondere({"a": 0.0, "b": x, "c": 3.0}, b, 0.05)
        for x in (NAN, INF, True):
            with self.subTest(budget=x), self.assertRaises(ValueError):
                pa.ebh_pondere({"a": 0.0, "b": 0.0, "c": 3.0}, {**b, "b": x}, 0.05)
        self.assertEqual(pa.ebh_pondere({"a": 0.0, "b": 0.0, "c": 3.0}, b, 0.05), set())  # sain : aucune
        self.assertEqual(pa.ebh_pondere({"a": 0.0, "b": 0.0, "c": 5.0}, b, 0.05), {"c"})  # sain : 148·0,0167 ≥ 1

    def test_course_ajouter_trajectoire(self):
        for x in (NAN, INF, -INF, True, None):  # avant : +∞ promouvait, NaN était ignoré sans erreur
            with self.subTest(valeur=x):
                c = pa.Course(alpha=0.05, essai=True)
                c.entrer("g1", ["a"], 0.05)
                u = {(1, "a", i) for i in range(3)}
                with self.assertRaises(pa.ContrasteInvalide):
                    c.ajouter_trajectoire("a", [math.log(2), x], unites=u)
                # refus avant tout changement d'état : ni partie comptée, ni unités lues, ni valeur changée
                self.assertEqual((c.log_e["a"], c.derniere_partie, c.unites_lues, c.premiere_lecture), (0.0, {}, {}, {}))
                self.assertAlmostEqual(c.ajouter_trajectoire("a", [math.log(2), math.log(3)], unites=u), math.log(3))  # sain
                self.assertEqual(c.lire(), set())
        c = pa.Course(alpha=0.05, essai=True)
        c.entrer("g1", ["a"], 0.05)
        with self.assertRaises(pa.ContrasteInvalide):  # aussi par l'abandon qui passe la partie
            c.abandonner("a", trajectoire_log=[INF], unites={"u"})
        self.assertNotIn("a", c.gelees)

    def test_sans_remise_valeurs(self):
        for x in (NAN, INF, -INF, 5.0, -1.5, True, None):  # avant : NaN → −690, +∞ → NaN, 5,0 accepté
            with self.subTest(valeur=x), self.assertRaises(pa.ContrasteInvalide):
                pa.trajectoire_log_sans_remise([0.1, x, -0.1])
        sain = pa.trajectoire_log_sans_remise([0.1, -1.0, 1.0, 0])
        self.assertEqual(len(sain), 4)
        self.assertTrue(all(math.isfinite(x) for x in sain))

    def test_borne_basse_valeurs_et_alpha(self):
        v = [0.4, 0.0] * 100
        for x in (NAN, INF, -INF, 5.0, -1.5, True, None):  # avant : NaN → −0,98, 5,0 → 0,99 (favorable)
            with self.subTest(valeur=x), self.assertRaises(pa.ContrasteInvalide):
                pa.borne_basse(v + [x])
        for a in (NAN, INF, 0, 1, True):
            with self.subTest(alpha=a), self.assertRaises(pa.ContrasteInvalide):
                pa.borne_basse(v, alpha=a)
        b = pa.borne_basse(v)  # sain : moyenne 0,2
        self.assertTrue(-1.0 < b <= 0.2, b)
        self.assertTrue(-1.0 <= pa.borne_basse([1.0, -1.0, 0]) < 1.0)  # sain : bornes de [−1 ; 1] admises

    def test_evaluer_alpha_et_m(self):
        for a in (NAN, INF, -INF, 0, 1, 1.5, True, None):  # avant : α NaN → seuil NaN, jamais promue, sans erreur
            with self.subTest(alpha=a), self.assertRaises(pa.ContrasteInvalide):
                pa.evaluer({"B": [1.0] * 30}, alpha=a)
        for m in (NAN, INF, -INF, 0, 0.5, True, None):
            with self.subTest(m=m), self.assertRaises(pa.ContrasteInvalide):
                pa.evaluer({"B": [1.0] * 30}, m=m)
        self.assertEqual(pa.evaluer({"B": [1.0] * 30}, alpha=0.05, m=1)["instant_d_arret"], 7)  # sain, inchangé
        self.assertTrue(pa.evaluer({"B": [1.0] * 30}, m=10.0)["promue"])  # sain : m réel fini ≥ 1


class TestV41(unittest.TestCase):
    """v41 (CL40-06, relecture CL7 de session-depot) : α de `ebh_pondere` exigé fini dans ]0 ; 1[ ; valeurs de
    `trajectoire_log_richesse` et parts de `contraste` refusant `True` ; un seul prédicat `_fini` (un entier de numpy admis
    par `verifier_coefficients` comme par `contraste`, et par la garde) ; `ponderation_plafonnee` refuse un booléen."""

    def test_ebh_pondere_alpha(self):
        b = {k: 0.3 for k in "abc"}  # somme 0,9 : avant, α NaN, +∞ ou True désarmaient la garde de la somme
        for a in (NAN, INF, -INF, True, 0, 1, 1.5):
            with self.subTest(alpha=a), self.assertRaises(pa.ContrasteInvalide):
                pa.ebh_pondere({"a": 0.0, "b": 0.0, "c": 3.0}, b, a)
        with self.assertRaises(ValueError):  # sain : somme 0,9 > α = 0,05 refusée
            pa.ebh_pondere({"a": 0.0, "b": 0.0, "c": 3.0}, b, 0.05)
        self.assertEqual(pa.ebh_pondere({"a": 0.0, "b": 0.0, "c": 5.0}, {k: 0.05 / 3 for k in "abc"}, 0.05), {"c"})
        self.assertEqual(pa.ebh_pondere({"a": 0.0}, {"a": 0.9}), set())  # sain : sans α, plafond 1 inchangé

    def test_richesse_et_parts_refusent_les_booleens(self):
        for v in (True, False, None, NAN, INF, 1.5):  # avant : True valait 1
            with self.subTest(valeur=v), self.assertRaises(pa.ContrasteInvalide):
                pa.trajectoire_log_richesse([0.1, v])
        with self.assertRaises(pa.ContrasteInvalide):
            pa.evaluer({"B": [True] * 30})  # avant : promue (True = +1)
        self.assertEqual(len(pa.trajectoire_log_richesse([0.1, -1, 1, 0])), 4)  # sain : entiers des bornes admis
        for r in (True, None, NAN):
            with self.subTest(part=r), self.assertRaises(pa.ContrasteInvalide):
                pa.contraste({"A": r, "B": 0.5}, {"A": 1, "B": -1})
        self.assertAlmostEqual(pa.contraste({"A": 1, "B": 0.5}, {"A": 1, "B": -1}), 0.5)  # sain : part entière 1

    def test_un_seul_predicat(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy absent")
        coefs = {"A": np.int64(1), "B": np.float64(-0.5)}
        self.assertTrue(pa.verifier_coefficients(coefs))  # avant : refusé ici, admis par `contraste`
        self.assertAlmostEqual(pa.contraste({"A": 0.5, "B": 0.5}, coefs), 0.25)
        self.assertEqual(len(pa.trajectoire_log_garde([np.float64(0.1), np.int64(0)], 0.05)), 2)
        with self.assertRaises(pa.ContrasteInvalide):
            pa.verifier_coefficients({"A": np.bool_(True)})

    def test_ponderation_plafonnee_booleen(self):
        for m_t, m_max in ((True, 5), (3, True)):
            with self.subTest(m_t=m_t, m_max=m_max), self.assertRaises(ValueError):
                pa.ponderation_plafonnee(m_t, m_max)
        self.assertEqual(pa.ponderation_plafonnee(3, 5), 0.6)  # sain


if __name__ == "__main__":
    unittest.main()
