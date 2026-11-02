"""Essais du nul v9 (`pole/nul_v9.py`) et du banc des tricheurs v9 (`demonstrations/banc_tricheurs_v9.py`).

R5 : chaque garde est éprouvée sur un cas sain et sur un artefact, aucun repli silencieux ; R9 : graines SeedSequence (règle du
banc v8). Fichier neuf (R12) ; aucun fichier existant n'est modifié ; aucun réseau, aucun modèle.
- Membres : présents, lois connues exactes, partitions exactes (cas sain) ; absent, altéré, en trop, membre v8 retiré (artefacts).
- Certificat : la valeur d'un membre domine la vraisemblance de tout monde de sa famille, à chaque instant lu, pour tout seuil
  réel (cas sain) ; référence indépendante (scipy, sur petits échantillons) ; la valeur atteinte seule n'est pas une borne
  (artefact : ce qu'un calcul sans écart de Frank-Wolfe rendrait).
- Évaluateur : identique à `evaluer_v2` sans membre par morceaux ; monotonie v9 ≤ v8 sur les mêmes issues ; gardes d'engagement
  et de tirages ; membre inconnu refusé.
- Tricheurs (banc v9, 20 répétitions, entropie fixée) : le monde W2 de l'attaque est membre du nul v9, sa loi n'est jamais
  promue sous v9 (log W ≤ 0) et l'est sous v8 ; les tricheurs par morceaux M02 à M07 de même ; une loi neuve plantée
  (interaction, loi neuve) reste promue ; artefact : sans les membres par morceaux, M01 passe.
- Lecture gelée, issues, audits, préenregistrement, liste d'arrêt, fermeture des imports.
- Après la contre-lecture R2 n° 1 du préenregistrement de validation : cas sain et refus du mode décisif (B1), monotonie par la
  seule richesse (B1), ordre des issues (I5), valeur certifiée sous optimisation tronquée (I6), description publique séparant
  trous, choix et nature (I2).
Mutations : `essais/mutations_nul_v9.py`. Durée visée : quelques minutes (`nice -n 10`).
"""

import contextlib
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

import numpy as np

from pole import nul_filles_v2 as nf
from pole import nul_v8, nul_v9
from pole import selection_pari as sp
from pole.cycle import instants_reguliers
from pole.outils import ecrire_scelle, sha256_fichier

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
ENTROPIE = 20261102  # entropie racine des essais (mode exploratoire ; la validation décisive aura la sienne, ≥ 2⁶⁴)
REPETITIONS = 20


def _charger(fichier, nom):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(RACINE, "demonstrations", fichier))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


banc = _charger("banc_tricheurs_v9.py", "banc_tricheurs_v9_essai")
K, DIM, ALPHA = banc.K, banc.DIM, banc.ALPHA


def _lois(graine=11):
    rng = random.Random(graine)
    return {n: sp.loi_softmax_aleatoire(rng, K, DIM) for n in ("A", "B", "S1", "S2", "N")}


class Dossier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pole-essais-nul-v9-")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def silence(self):
        pile = contextlib.ExitStack()
        pile.enter_context(contextlib.redirect_stdout(io.StringIO()))
        pile.enter_context(contextlib.redirect_stderr(io.StringIO()))
        self.addCleanup(pile.close)
        return pile


# --- membres -----------------------------------------------------------------------------------------------------------------
class MembresNulV9(unittest.TestCase):
    def test_cas_sain_membres_fiche_fille_et_une_seule_loi(self):
        L = _lois()
        surv = {"S1": L["S1"], "S2": L["S2"]}
        m = nul_v9.membres_archive_v9(surv, None, K, DIM)
        v8 = nul_v8.membres_archive_v8(surv, None, K, DIM)
        self.assertEqual(m[:len(v8)], v8, "les membres du v8 d'abord, intacts")
        morceaux = [x for x in m if x["type"] == nul_v9.TYPE_MORCEAUX]
        self.assertEqual([x["nom"] for x in morceaux], ["morceaux:sous_population", "morceaux:seuil:z0", "morceaux:seuil:z1"])
        self.assertTrue(all(x["lois"] == [L["S1"], L["S2"]] for x in morceaux))
        self.assertEqual([x["partition"] for x in morceaux],
                         [{"type": "sous_population"}, {"type": "seuil", "indice": 0}, {"type": "seuil", "indice": 1}])
        fille = nul_v9.membres_archive_v9(surv, {"B": L["B"], "A": L["A"]}, K, DIM)
        self.assertTrue(all(x["lois"] == [L["A"], L["B"], L["S1"], L["S2"]] for x in fille if x["type"] == nul_v9.TYPE_MORCEAUX))
        une = nul_v9.membres_archive_v9({"S1": L["S1"]}, None, K, DIM)
        self.assertFalse([x for x in une if x["type"] == nul_v9.TYPE_MORCEAUX], "une seule loi connue : aucun membre par morceaux")
        self.assertEqual(nul_v9.membres_archive_v9({}, None, K, DIM), [], "archive vide, sans parent : rien de connu")

    def test_artefact_membre_absent_altere_ou_en_trop_refuse(self):
        L = _lois()
        surv = {"S1": L["S1"], "S2": L["S2"]}
        sain = nul_v9.membres_archive_v9(surv, None, K, DIM)
        def sans(nom):
            return [x for x in sain if x["nom"] != nom]
        def altere(nom, **champs):
            return [dict(x, **champs) if x["nom"] == nom else x for x in sain]
        cas = {"seuil z1 absent": sans("morceaux:seuil:z1"),
               "sous-population absente": sans("morceaux:sous_population"),
               "lois tronquées": altere("morceaux:seuil:z0", lois=[L["S1"]]),
               "lois d'un autre ordre": altere("morceaux:seuil:z0", lois=[L["S2"], L["S1"]]),
               "partition changée": altere("morceaux:seuil:z1", partition={"type": "seuil", "indice": 0}),
               "type changé": altere("morceaux:sous_population", type="ajuste_lineaire"),
               "membre en double": sain + [sain[-1]],
               "membre inattendu": sain + [{"nom": "morceaux:seuil:z5", "type": nul_v9.TYPE_MORCEAUX, "lois": [L["S1"], L["S2"]],
                                            "partition": {"type": "seuil", "indice": 5}}],
               "membre linéaire du v8 retiré": sans("ajuste_lineaire:archive")}
        for libelle, membres in cas.items():
            with self.subTest(libelle), self.assertRaises(nul_v9.NulV9Refuse):
                nul_v9.exiger_membres_v9(membres, surv, None, DIM)
        self.assertIs(nul_v9.exiger_membres_v9(sain, surv, None, DIM), sain)


# --- certificat ----------------------------------------------------------------------------------------------------------------
def _donnees(loi, n, rng, monde=None):
    instances = sp.tirer_instances(rng, n, DIM)
    monde = monde or loi
    issues = [sp.tirer_categorie(rng, sp.proba(monde, x, [], 0)) for x in instances]
    return instances, issues


def _valeurs(membres, instances, issues, instants):
    cache = sp.Cache(issues, instances)
    return nul_v9.detail_morceaux_groupe(membres, cache, issues, instants)


class CertificatMorceaux(unittest.TestCase):
    def test_cas_sain_valeur_domine_la_vraisemblance_de_tout_monde_de_la_famille(self):
        """30 mondes de la famille (sous-population, seuil réel quelconque, avec bruit commun, mélanges propres aux
        morceaux) : à chaque instant lu, valeur du bon membre ≥ log-vraisemblance du monde (aux arrondis près)."""
        instants = [25, 50, 100, 150, 200]
        pire = -math.inf
        for r in range(30):
            rng = random.Random(1000 + r)
            L = _lois(2000 + r)
            S1, S2 = L["S1"], L["S2"]
            j, s = rng.randrange(DIM), rng.uniform(-1.5, 1.5)
            q = {"type": "fixe", "probas": [rng.random() + 0.01 for _ in range(K)]}
            eps = rng.uniform(0.0, 0.4)
            choix = r % 4
            if choix == 0:
                monde, nom = banc._par_sp(S1, S2), "morceaux:sous_population"
            elif choix == 1:
                monde, nom = banc._si_seuil(j, s, S1, S2), f"morceaux:seuil:z{j}"
            elif choix == 2:
                monde, nom = banc._melange([banc._si_seuil(j, s, S2, S1), q], [1 - eps, eps]), f"morceaux:seuil:z{j}"
            else:  # mélange propre à chaque morceau, bruit commun (0,2·q sur les deux morceaux)
                monde = banc._par_sp(banc._melange([S1, S2, q], [0.24, 0.56, 0.2]), banc._melange([S1, S2, q], [0.6, 0.2, 0.2]))
                nom = "morceaux:sous_population"
            instances, issues = _donnees(monde, 200, rng)
            membres = nul_v9.membres_morceaux([S1, S2], DIM)
            d = _valeurs(membres, instances, issues, instants)
            lv = nul_v9.log_vraisemblance(monde, issues, instances)
            for t in instants:
                pire = max(pire, lv[t - 1] - d[nom][t]["valeur"])
                self.assertGreaterEqual(d[nom][t]["valeur"], lv[t - 1] - 1e-9,
                                        f"monde {r} ({nom}), instant {t} : valeur {d[nom][t]['valeur']} < log-vraisemblance "
                                        f"du monde {lv[t - 1]}")
                self.assertLessEqual(d[nom][t]["valeur"], 0.0)
                self.assertGreaterEqual(d[nom][t]["ecart_residuel"], 0.0)
        self.assertLess(pire, 1e-9)

    def test_hors_famille_bruit_propre_au_morceau_non_domine(self):
        """Limite de la famille, dite (R8) : un monde dont le bruit aveugle n'est que sur un morceau (bruit propre au morceau,
        classe non couverte) n'est pas dominé — sur ces 12 tirages, au moins un instant où la valeur du membre est sous la
        vraisemblance du monde. La garantie de Ville ne vaut pas pour lui ; seul le banc (ligne H04) le mesure."""
        sous = 0
        for r in range(12):
            rng = random.Random(3000 + r)
            L = _lois(3100 + r)
            q = {"type": "fixe", "probas": [rng.random() + 0.01 for _ in range(K)]}
            monde = banc._par_sp(banc._melange([L["S1"], L["S2"]], [0.3, 0.7]), banc._melange([L["S1"], L["S2"], q], [0.4, 0.2, 0.4]))
            instances, issues = _donnees(monde, 200, rng)
            d = _valeurs(nul_v9.membres_morceaux([L["S1"], L["S2"]], DIM), instances, issues, [100, 200])
            lv = nul_v9.log_vraisemblance(monde, issues, instances)
            sous += sum(d["morceaux:sous_population"][t]["valeur"] < lv[t - 1] - 1e-6 for t in (100, 200))
        self.assertGreater(sous, 0, "monde hors famille toujours dominé : la limite dite de la famille n'est pas vue")

    def test_seuil_egal_a_une_valeur_observee(self):
        """Le seuil du monde est exactement l'une des valeurs du trait observées (cas limite de la coupe) : couvert."""
        L = _lois(5)
        rng = random.Random(5)
        instances = sp.tirer_instances(rng, 120, DIM)
        s = instances[37]["z"][1]
        monde = banc._si_seuil(1, s, L["S1"], L["S2"])
        issues = [sp.tirer_categorie(rng, sp.proba(monde, x, [], 0)) for x in instances]
        d = _valeurs(nul_v9.membres_morceaux([L["S1"], L["S2"]], DIM), instances, issues, [60, 120])
        lv = nul_v9.log_vraisemblance(monde, issues, instances)
        for t in (60, 120):
            self.assertGreaterEqual(d["morceaux:seuil:z1"][t]["valeur"], lv[t - 1] - 1e-9)

    def test_reference_independante_scipy_petits_echantillons(self):
        """Petits échantillons (t = 14) : pour chaque coupe, le maximum calculé par scipy (SLSQP, plusieurs départs) ;
        la valeur du membre est ≥ ce maximum (certificat) et à moins de 10⁻² au-dessus (précision)."""
        try:
            from scipy.optimize import minimize
        except ImportError:  # pragma: no cover
            self.skipTest("scipy absent : référence indépendante non jouée")
        for r in range(3):
            rng = random.Random(70 + r)
            L = _lois(80 + r)
            instances, issues = _donnees(L["N"], 14, rng)
            membres = nul_v9.membres_morceaux([L["S1"], L["S2"]], DIM)
            d = _valeurs(membres, instances, issues, [14])
            Lm = np.array([[sp.proba(l, x, [], 0)[y] for l in (L["S1"], L["S2"])] for x, y in zip(instances, issues)])
            Y = np.eye(K)[issues]

            def maximum(pieces):
                """max Σ log(a^p·L_i + r_y) sur le polytope, pièces = liste de tableaux d'indices."""
                P, J = len(pieces), 2
                def f(x):
                    tot = 0.0
                    for p, idx in enumerate(pieces):
                        if len(idx):
                            m = Lm[idx] @ x[p * J:(p + 1) * J] + Y[idx] @ x[P * J:]
                            tot += np.log(np.maximum(m, 1e-300)).sum()
                    return -tot
                cons = [{"type": "eq", "fun": (lambda x, p=p: x[p * J:(p + 1) * J].sum() + x[P * J:].sum() - 1.0)} for p in range(P)]
                meilleur = -np.inf
                for depart in range(4):
                    rs = np.random.default_rng(depart)
                    x0 = np.concatenate([rs.dirichlet(np.ones(J)) * 0.5 for _ in range(P)] + [rs.dirichlet(np.ones(K)) * 0.5])
                    res = minimize(f, x0, method="SLSQP", bounds=[(0, 1)] * (P * J + K), constraints=cons,
                                   options={"ftol": 1e-12, "maxiter": 500})
                    if res.success:
                        meilleur = max(meilleur, -res.fun)
                return meilleur
            g = np.array([x["g"] for x in instances])
            ref_sp = maximum([np.flatnonzero(g == v) for v in sorted(set(g))])
            self.assertGreaterEqual(d["morceaux:sous_population"][14]["valeur"], ref_sp - 1e-7)
            self.assertLessEqual(d["morceaux:sous_population"][14]["valeur"], ref_sp + 1e-2)
            for j in range(DIM):
                z = np.array([x["z"][j] for x in instances])
                ref = max(maximum([np.flatnonzero(z <= s), np.flatnonzero(z > s)]) for s in [-np.inf] + sorted(set(z)))
                v = d[f"morceaux:seuil:z{j}"][14]["valeur"]
                self.assertGreaterEqual(v, ref - 1e-7, f"tirage {r}, trait {j} : valeur {v} sous la référence {ref}")
                self.assertLessEqual(v, ref + 1e-2, f"tirage {r}, trait {j} : valeur {v} loin au-dessus de la référence {ref}")

    def test_artefact_valeur_atteinte_au_depart_n_est_pas_une_borne(self):
        """Ce que rendrait un calcul qui prendrait la valeur atteinte au point de départ (sans écart de Frank-Wolfe ni
        optimisation) : en dessous de la vraisemblance du monde W2 (donc pas une borne : la richesse d'une loi vraie de la
        famille passerait au-dessus de 1) ; le certificat, lui, la domine."""
        L = _lois(9)
        rng = random.Random(9)
        monde = banc._par_sp(L["S1"], L["S2"])
        instances, issues = _donnees(monde, 200, rng)
        n = len(issues)
        Lm = np.array([[sp.proba(l, x, [], 0)[y] for l in (L["S1"], L["S2"])] for x, y in zip(instances, issues)])
        Y = np.eye(K)[issues]
        M, _ = nul_v9._coupes({"type": "sous_population"}, instances, n, ["0", "1"])
        w = nul_v9._ajustement_sans_coupure(np.concatenate([Lm, Y], axis=1))
        x0 = nul_v9._depart(2, K, 2, w)[None]
        f0, cert0 = nul_v9._certificats(Lm, Y, M, M.sum(axis=0), x0, 2)
        lv = nul_v9.log_vraisemblance(monde, issues, instances)[-1]
        self.assertLess(float(f0[0]), lv, "la valeur atteinte au départ devrait être sous la vraisemblance du monde")
        self.assertGreaterEqual(float(cert0[0]), lv - 1e-9, "le certificat au même point domine la vraisemblance du monde")

    def test_valeur_certifiee_sous_optimisation_tronquee(self):
        """I6 (contre-lecture R2 n° 1) : sous optimisation tronquée (un palier, un pas), la valeur rendue par le membre domine encore
        la log-vraisemblance de chaque monde de la famille à chaque instant lu (les 30 mondes de l'essai de domination, mêmes
        graines) — la validité ne dépend pas de la convergence ; dents de l'essai : la meilleure valeur atteinte + 10⁻³ passe sous
        la vraisemblance du monde à au moins un instant (ce que rendrait une valeur non certifiée)."""
        instants = [25, 50, 100, 150, 200]
        sous_atteinte = 0
        with unittest.mock.patch.object(nul_v9, "PALIERS_MU", (1e-2,)), unittest.mock.patch.object(nul_v9, "PAS_MAX_PAR_PALIER", 1):
            for r in range(30):  # génération identique à `test_cas_sain_valeur_domine_la_vraisemblance_de_tout_monde_de_la_famille`
                rng = random.Random(1000 + r)
                L = _lois(2000 + r)
                S1, S2 = L["S1"], L["S2"]
                j, s = rng.randrange(DIM), rng.uniform(-1.5, 1.5)
                q = {"type": "fixe", "probas": [rng.random() + 0.01 for _ in range(K)]}
                eps = rng.uniform(0.0, 0.4)
                choix = r % 4
                if choix == 0:
                    monde, nom = banc._par_sp(S1, S2), "morceaux:sous_population"
                elif choix == 1:
                    monde, nom = banc._si_seuil(j, s, S1, S2), f"morceaux:seuil:z{j}"
                elif choix == 2:
                    monde, nom = banc._melange([banc._si_seuil(j, s, S2, S1), q], [1 - eps, eps]), f"morceaux:seuil:z{j}"
                else:
                    monde = banc._par_sp(banc._melange([S1, S2, q], [0.24, 0.56, 0.2]), banc._melange([S1, S2, q], [0.6, 0.2, 0.2]))
                    nom = "morceaux:sous_population"
                instances, issues = _donnees(monde, 200, rng)
                d = _valeurs(nul_v9.membres_morceaux([S1, S2], DIM), instances, issues, instants)
                lv = nul_v9.log_vraisemblance(monde, issues, instances)
                for t in instants:
                    self.assertGreaterEqual(d[nom][t]["valeur"], lv[t - 1] - 1e-9,
                                            f"optimisation tronquée, monde {r} ({nom}), instant {t} : valeur {d[nom][t]['valeur']} "
                                            f"sous la vraisemblance du monde {lv[t - 1]}")
                    sous_atteinte += d[nom][t]["atteinte"] + 1e-3 < lv[t - 1] - 1e-9
        self.assertGreater(sous_atteinte, 0, "dents de l'essai : l'optimisation tronquée devrait laisser la valeur atteinte + 10⁻³ "
                                             "sous la vraisemblance du monde à au moins un instant")

    def test_garde_depart_non_admissible(self):
        L = _lois(3)
        instances, issues = _donnees(L["S1"], 30, random.Random(3))
        Lm = np.array([[sp.proba(l, x, [], 0)[y] for l in (L["S1"], L["S2"])] for x, y in zip(instances, issues)])
        Y = np.eye(K)[issues]
        M, _ = nul_v9._coupes({"type": "sous_population"}, instances, 30, ["0", "1"])
        sain = nul_v9._depart(2, K, 2, np.full(5, 0.2))[None]
        b, a, _ = nul_v9.maximiser_par_lots(Lm, Y, M, [0], sain)
        self.assertTrue(np.all(b >= a - 1e-12))
        for libelle, x in (("hors contraintes", sain * 1.1), ("coordonnée nulle", np.where(np.arange(7) == 0, 0.0, sain)),
                           ("non fini", sain * np.nan)):
            with self.subTest(libelle), self.assertRaises(nul_v9.CalculMorceauxImpossible):
                nul_v9.maximiser_par_lots(Lm, Y, M, [0], x)


# --- évaluateur ----------------------------------------------------------------------------------------------------------------
def _engagement(genre, loi, L, rng, membres):
    q_ent = [0.3, 0.3, 0.4]
    standard = list(sp.BIBLIOTHEQUE_STANDARD) + [{"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}]
    surv = {"S1": L["S1"], "S2": L["S2"]}
    if genre == "fille":
        parents = {"A": L["A"], "B": L["B"]}
        instances = sp.tirer_instances(rng, banc.CALIBRAGE + banc.TIRAGES, DIM)
        biblio = (sp.bibliotheque_fille(parents, DIM, standard, q_ent, nombre_issues=K) + nf.membres_de_variante("v2", parents)
                  + membres(surv, parents, K, DIM))
        return sp.geler_engagement(nf.construire_engagement_v2("fille", loi, instances, K, ALPHA, biblio, banc.CALIBRAGE,
                                                               banc.DELTA0, banc.INSTANTS))
    instances = sp.tirer_instances(rng, banc.TIRAGES, DIM)
    biblio = standard + membres(surv, None, K, DIM)
    return sp.geler_engagement(nf.construire_engagement_v2("fiche", loi, instances, K, ALPHA, biblio, 0, None,
                                                           instants_reguliers(banc.TIRAGES, len(banc.INSTANTS))))


class EvaluateurV9(unittest.TestCase):
    def test_identique_a_v2_sans_morceaux(self):
        """Bibliothèque du v8 (aucun membre par morceaux) : `evaluer_v9` rend exactement `evaluer_v2`, fille et fiche."""
        for r, genre in enumerate(("fiche", "fille", "fiche", "fille")):
            L = _lois(300 + r)
            rng = random.Random(400 + r)
            loi = banc._par_sp(L["S1"], L["N"]) if r % 2 == 0 else L["A"]
            gele = _engagement(genre, loi, L, rng, nul_v8.membres_archive_v8)
            tir = sp.tirer_frais(gele, loi, 500 + r, graine_noyau=600 + r)
            self.assertEqual(nul_v9.evaluer_v9(gele, tir, graine_noyau=600 + r), nf.evaluer_v2(gele, tir, graine_noyau=600 + r))

    def test_departage_des_membres_comme_v2(self):
        """Égalité exacte entre deux membres (deux lois fixes identiques, « a » puis « b ») : le membre dominant est choisi
        comme dans `evaluer_v2` (plus grande valeur, puis plus grand nom) ; artefact visé : un départage par l'ordre de la
        bibliothèque."""
        L = _lois(15)
        rng = random.Random(15)
        instances = sp.tirer_instances(rng, 40, DIM)
        biblio = [{"nom": "a", "type": "fixe", "probas": [1.0, 2.0, 3.0]}, {"nom": "b", "type": "fixe", "probas": [1.0, 2.0, 3.0]}]
        gele = sp.geler_engagement(nf.construire_engagement_v2("fiche", L["N"], instances, K, ALPHA, biblio, 0, None, [20, 40]))
        tir = sp.tirer_frais(gele, L["N"], 3, graine_noyau=4)
        ev9, ev2 = nul_v9.evaluer_v9(gele, tir, graine_noyau=4), nf.evaluer_v2(gele, tir, graine_noyau=4)
        self.assertEqual(ev9["membre_dominant_final"], "b")
        self.assertEqual(ev9, ev2)

    def test_monotonie_v9_sous_v8_sur_les_memes_issues(self):
        for r in range(6):
            L = _lois(700 + r)
            rng = random.Random(800 + r)
            genre = "fille" if r % 3 == 2 else "fiche"
            loi = [L["N"], banc._par_sp(L["S1"], L["S2"]), banc._si_seuil(0, 0.2, L["A"], L["N"])][r % 3]
            gele = _engagement(genre, loi, L, rng, nul_v9.membres_archive_v9)
            tir = sp.tirer_frais(gele, loi, 900 + r, graine_noyau=950 + r)
            ev9 = nul_v9.evaluer_v9(gele, tir, graine_noyau=950 + r)
            ev8 = nul_v9.evaluer_sur_issues(nul_v9.sans_morceaux(gele.engagement), tir["issues"])
            for a, b in zip(ev9["trajectoire_log_w"], ev8["trajectoire_log_w"]):
                self.assertLessEqual(a, b + 1e-6)
            self.assertLessEqual(ev9["promue"], ev8["promue"])
            self.assertEqual(len(nul_v9.sans_morceaux(gele.engagement)["bibliotheque"]),
                             len(gele.engagement["bibliotheque"]) - 3)

    def test_gardes_d_engagement_et_de_tirages(self):
        L = _lois(12)
        rng = random.Random(12)
        gele = _engagement("fiche", L["N"], L, rng, nul_v9.membres_archive_v9)
        tir = sp.tirer_frais(gele, L["N"], 1, graine_noyau=2)
        self.assertIn("promue", nul_v9.evaluer_v9(gele, tir, graine_noyau=2))
        autre = _engagement("fiche", L["S1"], L, random.Random(13), nul_v9.membres_archive_v9)
        with self.assertRaises(sp.TiragesNonLies):
            nul_v9.evaluer_v9(autre, tir, graine_noyau=2)
        gele.engagement["alpha"] = 0.5
        with self.assertRaises(sp.EngagementModifie):
            nul_v9.evaluer_v9(gele, tir, graine_noyau=2)

    def test_membre_inconnu_refuse(self):
        L = _lois(14)
        instances, issues = _donnees(L["N"], 50, random.Random(14))
        cache = sp.Cache(issues, instances)
        sain = nul_v9.membres_morceaux([L["S1"], L["S2"]], DIM)
        self.assertEqual(set(nul_v9.valeurs_ajustees_v9(sain, cache, issues, K, [25, 50])), {m["nom"] for m in sain})
        with self.assertRaises(nul_v9.NulV9Refuse):
            nul_v9.valeurs_ajustees_v9([dict(sain[0], type="ajuste_inconnu")], cache, issues, K, [25, 50])
        with self.assertRaises(nul_v9.NulV9Refuse):
            nul_v9.valeurs_ajustees_v9([dict(sain[1], partition={"type": "oblique"})], cache, issues, K, [25, 50])


# --- tricheurs (banc v9) --------------------------------------------------------------------------------------------------------
class TricheursParMorceaux(unittest.TestCase):
    def test_monde_w2_de_l_attaque_membre_du_nul_v9(self):
        """Le monde W2 de l'attaque (`attaque_goodhart_v2.carte`, cartes 0 à 3) : la loi du monde, et la loi « si/sinon par
        sous-population S1, S2 » trouvée par le proposeur, ne sont jamais promues sous v9 (log W ≤ 0) ; le monde W1 non plus ;
        sous v8, la loi du monde W2 est promue."""
        from pole import attaque_goodhart_v2 as ag
        promues_v8 = 0
        for c in range(4):
            carte = ag.carte(7, c, "W2")
            L = carte["L"]
            for loi in (carte["monde"], {"type": "si_sinon", "condition": {"sous_population": 0}, "si": L["S1"], "sinon": L["S2"]}):
                rng = random.Random(31 + c)
                ev9, ev8 = banc.juger_v9("fraiche", loi, carte["monde"], L, rng, 41 + c, 51 + c)
                self.assertFalse(ev9["promue"])
                self.assertLessEqual(ev9["log_richesse_max"], 1e-6)
                promues_v8 += ev8["promue"]
            w1 = ag.carte(7, c, "W1")
            ev9, _ = banc.juger_v9("fraiche", w1["monde"], w1["monde"], w1["L"], random.Random(61 + c), 71 + c, 81 + c)
            self.assertLessEqual(ev9["log_richesse_max"], 1e-6)
        self.assertGreaterEqual(promues_v8, 6, "sous v8, la loi du monde W2 devrait passer (le trou du v8)")

    def _ligne(self, nom, repetitions=REPETITIONS):
        return banc.jouer_ligne(ENTROPIE, nom, "v9", "fatale", repetitions)

    def test_artefact_m01_jamais_promu_sous_v9_promu_sous_v8(self):
        x = self._ligne("M01")
        self.assertEqual(x["promues"], 0, f"M01|v9 promue {x['promues']}/{REPETITIONS} sous le nul v9")
        self.assertLessEqual(x["log_w_max_max"], 1e-6)
        self.assertGreaterEqual(x["apparie_v8"]["promues"], 16, "M01 sous le v8 apparié : le trou devrait être vu")

    def test_artefact_tricheurs_par_morceaux_m02_a_m07_jamais_promus(self):
        for nom in ("M02", "M03", "M04", "M05", "M06", "M07"):
            with self.subTest(nom):
                x = self._ligne(nom, 8)
                self.assertEqual(x["promues"], 0, f"{nom}|v9 promue {x['promues']}/8 sous le nul v9")
                self.assertLessEqual(x["log_w_max_max"], 1e-6)

    def test_cas_sain_loi_neuve_plantee_reste_promue(self):
        for nom, minimum in (("I01", 15), ("fraiche_neuve", 15)):
            with self.subTest(nom):
                x = banc.jouer_ligne(ENTROPIE, nom, "v9", "puissance", REPETITIONS)
                self.assertGreaterEqual(x["promues"], minimum, f"{nom}|v9 promue {x['promues']}/{REPETITIONS}")
                self.assertLessEqual(x["apparie_v8"]["perdues"], 2)

    def test_perte_appariee_comptee_dans_le_bon_sens(self):
        """La perte appariée compte les répétitions promues sous v8 et non sous v9 (jamais l'inverse, interdit par la
        monotonie) ; la promotion du v8 apparié est comptée à part."""
        def ev(promue, lw):
            return {"promue": promue, "log_richesse_max": lw, "trajectoire_log_w": [lw], "membre_dominant_final": "x"}
        suite = iter([(ev(False, 1.0), ev(True, 4.0)), (ev(True, 4.0), ev(True, 5.0)), (ev(False, 0.0), ev(False, 0.5)),
                      (ev(False, 2.0), ev(True, 3.5))])
        with unittest.mock.patch.object(banc, "juger_v9", side_effect=lambda *a, **k: next(suite)):
            x = banc.jouer_ligne(ENTROPIE, "I01", "v9", "puissance", 4)
        self.assertEqual((x["promues"], x["apparie_v8"]["promues"], x["apparie_v8"]["perdues"]), (1, 3, 2))
        self.assertAlmostEqual(x["apparie_v8"]["perte"], 0.5)

    def test_artefact_sans_membres_par_morceaux_m01_passe(self):
        """Dents de l'essai : le nul v9 privé de ses membres par morceaux (le v8) laisse passer M01."""
        with unittest.mock.patch.object(nul_v9, "membres_morceaux", lambda lois, dimension: []), \
                unittest.mock.patch.object(nul_v9, "exiger_membres_v9", lambda m, *a, **k: m):
            x = self._ligne("M01")
        self.assertGreaterEqual(x["promues"], 16, f"M01|v9 promue {x['promues']}/{REPETITIONS} sous le nul v9 mutilé")


# --- banc : graines, lecture, préenregistrement, liste d'arrêt --------------------------------------------------------------------
def _ligne_synthetique(nom, role, promues, n=1000, v8=None, perdues=0, log_w=-1.0, dominants=None):
    x = {"ligne": nom, "reglage": "v1" if role == "artefact_requis" else "v9", "role": role, "promues": promues,
         "repetitions": n, "taux": promues / n, "clopper_pearson_95_unilaterales": [0, 1], "log_w_max_max": log_w,
         "dominants": dominants or {"morceaux:sous_population": n}}
    if role != "artefact_requis":
        pv8 = promues if v8 is None else v8
        x["apparie_v8"] = {"promues": pv8, "taux": pv8 / n, "perdues": perdues, "perte": perdues / n}
    return x


def _resultats_sains():
    r = [_ligne_synthetique(n, "fatale", 0, v8=950 if n in ("M01", "M02") else 0) for n in banc.FATALES]
    r.append(_ligne_synthetique("T01", "artefact_requis", 450))
    r += [_ligne_synthetique(n, "puissance", 990, v8=995, perdues=5) for n in banc.PUISSANCE]
    r += [_ligne_synthetique(n, "mesure", 300, v8=600) for n in banc.MESUREES]
    return r


def _remplacer(resultats, nom, **champs):
    sortie = []
    for x in resultats:
        if x["ligne"] == nom and x["role"] != "artefact_requis":
            x = json.loads(json.dumps(x))
            for cle, v in champs.items():
                if cle == "apparie_v8":
                    x["apparie_v8"].update(v)
                else:
                    x[cle] = v
        sortie.append(x)
    return sortie


class LectureGelee(unittest.TestCase):
    def test_cas_sain_tout_tenu_confirme(self):
        lec = banc.lire_v9(_resultats_sains(), complet=True)
        self.assertEqual(lec["issue"], "confirmé")
        self.assertFalse(lec["audits"])
        self.assertEqual(set(lec["perte_de_puissance"].values()), {banc.TENUE})

    def test_artefact_ligne_fatale_au_dessus_de_alpha_trou(self):
        r = _remplacer(_resultats_sains(), "M03", promues=90, taux=0.09)
        lec = banc.lire_v9(r, complet=True)
        self.assertEqual(lec["fatales"]["M03|v9"], banc.NON_TENUE)
        self.assertEqual(lec["issue"], "trou")

    def test_artefact_perte_de_puissance(self):
        r = _remplacer(_resultats_sains(), "I02", apparie_v8={"perdues": 120, "perte": 0.12})
        lec = banc.lire_v9(r, complet=True)
        self.assertEqual(lec["perte_de_puissance"]["I02"], banc.NON_TENUE)
        self.assertEqual(lec["issue"], "puissance perdue")

    def test_artefact_banc_sans_dents(self):
        r = _remplacer(_resultats_sains(), "M02", apparie_v8={"promues": 20, "taux": 0.02})
        lec = banc.lire_v9(r, complet=True)
        self.assertEqual(lec["artefact"]["M02|v8 apparié"], banc.NON_TENUE)
        self.assertEqual(lec["issue"], "non concluant (banc sans dents)")

    def test_precision_insuffisante_et_plan_incomplet(self):
        r = _remplacer(_resultats_sains(), "T12a", promues=45, taux=0.045, log_w_max_max=4.0)
        self.assertEqual(banc.lire_v9(r, complet=True)["issue"], "non concluant (précision insuffisante)")
        self.assertEqual(banc.lire_v9(_resultats_sains()[:5], complet=False)["issue"], "partielle (plan incomplet : aucune issue)")

    def test_audits_symetriques(self):
        r = _remplacer(_resultats_sains(), "M01", promues=1, taux=0.001, log_w_max_max=3.2)
        r = _remplacer(r, "M05", log_w_max_max=0.4, dominants={"ajuste_lineaire:archive": 900, "morceaux:seuil:z0": 100})
        r = [dict(x, promues=40, taux=0.04) if x["role"] == "artefact_requis" else x for x in r]
        lec = banc.lire_v9(r, complet=True)
        textes = " | ".join(lec["audits"])
        for motif in ("A1 M01|v9", "A4 M01|v9", "A4 M05|v9", "A3 T01|v1", "A5 M05|v9"):
            self.assertIn(motif, textes)
        self.assertTrue(lec["issue_suspendue_par_audit"])
        r2 = _remplacer(_resultats_sains(), "M01", apparie_v8={"promues": 300, "taux": 0.3})
        self.assertIn("A3 M01|v8 apparié", " | ".join(banc.lire_v9(r2, complet=True)["audits"]))

    def test_issues_ecrites_d_avance(self):
        self.assertEqual(banc.ISSUES, ("confirmé", "trou", "puissance perdue", "non concluant (banc sans dents)",
                                       "non concluant (précision insuffisante)"))

    def test_ordre_des_issues(self):
        """I5 (contre-lecture R2 n° 1) : l'ordre gelé « trou », puis « puissance perdue », puis « banc sans dents » — une ligne
        fatale non tenue avec une perte non tenue se lit « trou » ; une perte non tenue avec un artefact non tenu se lit
        « puissance perdue »."""
        perte_i02 = {"perdues": 120, "perte": 0.12}
        r = _remplacer(_remplacer(_resultats_sains(), "M03", promues=90, taux=0.09), "I02", apparie_v8=perte_i02)
        lec = banc.lire_v9(r, complet=True)
        self.assertEqual((lec["fatales"]["M03|v9"], lec["perte_de_puissance"]["I02"]), (banc.NON_TENUE, banc.NON_TENUE))
        self.assertEqual(lec["issue"], "trou")
        r = _remplacer(_remplacer(_resultats_sains(), "I02", apparie_v8=perte_i02), "M02", apparie_v8={"promues": 20, "taux": 0.02})
        lec = banc.lire_v9(r, complet=True)
        self.assertEqual((lec["perte_de_puissance"]["I02"], lec["artefact"]["M02|v8 apparié"]), (banc.NON_TENUE, banc.NON_TENUE))
        self.assertEqual(lec["issue"], "puissance perdue")


class GrainesEtPreenregistrement(Dossier):
    def test_graines_seedsequence_et_cles_distinctes(self):
        self.assertEqual(banc.graines(5, "M01|v9", 3), banc.v8.graines(5, "M01|v9", 3))
        self.assertNotEqual(banc.graines(5, "M01|v9", 3), banc.graines(5, "M01|v9", 4))
        self.assertEqual(banc.verifier_cles_distinctes(list(banc.LIGNES)), list(banc.LIGNES))
        with self.assertRaises(ValueError):
            banc.verifier_cles_distinctes(list(banc.LIGNES) + [banc.LIGNES[0]])

    def _prereg(self, empreintes, nom="preenregistrement-validation-nul-v9-v1.md", sceller=True):
        dossier = os.path.join(self.tmp, "prereg")
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, nom)
        texte = ("# Préenregistrement d'essai\n\n" + banc.DEBUT_EMPREINTES + "\n```\n"
                 + "".join(f"{h}  {p}\n" for h, p in empreintes) + "```\n" + banc.FIN_EMPREINTES + "\n")
        if sceller:
            ecrire_scelle(chemin, texte)
        else:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        return chemin

    def _gel(self):
        return [(sha256_fichier(os.path.join(RACINE, p)), p) for p in banc.FICHIERS_GELES]

    def test_cas_sain_et_artefacts_preenregistrement(self):
        with unittest.mock.patch.object(banc, "DOSSIER_PREREG", os.path.join(self.tmp, "prereg")):
            p = self._prereg(self._gel())
            entropie, empreinte, gelees = banc.lire_preenregistrement(p)
            self.assertEqual(entropie, int(empreinte, 16))
            self.assertGreaterEqual(entropie, 2 ** 64)
            self.assertEqual(set(gelees), set(banc.FICHIERS_GELES))
            cas = {"brouillon": (self._prereg(self._gel(), nom="preenregistrement-validation-nul-v9-brouillon1.md"), banc.EcartAuPlan),
                   "non scellé": (self._prereg(self._gel(), nom="preenregistrement-validation-nul-v9-v2.md", sceller=False),
                                  banc.PreenregistrementNonScelle),
                   "fichier manquant au gel": (self._prereg(self._gel()[1:], nom="preenregistrement-validation-nul-v9-v3.md"),
                                               banc.EcartAuPlan),
                   "empreinte fausse": (self._prereg([("0" * 64, banc.FICHIERS_GELES[0])] + self._gel()[1:],
                                                     nom="preenregistrement-validation-nul-v9-v4.md"), banc.EcartAuPlan)}
            for libelle, (chemin, erreur) in cas.items():
                with self.subTest(libelle), self.assertRaises(erreur):
                    banc.lire_preenregistrement(chemin)
        with self.assertRaises(banc.EcartAuPlan):  # bon nom, mauvais dossier
            banc.lire_preenregistrement(p)

    def test_refus_du_banc_avant_toute_course(self):
        appels = []

        def bouchon(taches, processus):
            appels.append(len(taches))
            return [], "course interdite dans cet essai"
        plein = os.path.join(self.tmp, "plein")
        os.makedirs(plein)
        open(os.path.join(plein, "x"), "w").close()
        brouillon = os.path.join(RACINE, "prereg", "preenregistrement-validation-nul-v9-brouillon1.md")
        cas = ([os.path.join(self.tmp, "s1"), "--preenregistrement", brouillon],
               [os.path.join(self.tmp, "s2"), "--graine", "1", "--lignes", "M99"],
               [os.path.join(self.tmp, "s3"), "--graine", str(2 ** 64), "--lignes", "M01", "--repetitions", "1"],
               [os.path.join(self.tmp, "s4"), "--graine", "-1"],
               [plein, "--graine", "1"])
        with unittest.mock.patch.object(banc, "jouer_tout", bouchon):
            for argv in cas:
                with self.subTest(argv=argv[1:]), contextlib.redirect_stderr(io.StringIO()), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(banc.principal(argv), 2)
        self.assertEqual(appels, [], "une course a été lancée malgré un refus")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "s1")))

    def test_banc_reduit_et_liste_d_arret(self):
        base = ["--graine", "3", "--lignes", "M01", "--repetitions", "2", "--processus", "1"]
        self.silence()
        sortie = os.path.join(self.tmp, "sain")
        self.assertEqual(banc.principal([sortie] + base), 0)
        with open(os.path.join(sortie, "banc-tricheurs-v9.json"), encoding="utf-8") as f:
            r = json.load(f)
        self.assertEqual(r["lecture"]["issue"], "partielle (plan incomplet : aucune issue)")
        self.assertEqual(r["resultats"][0]["repetitions"], 2)
        self.assertIn("perdues", r["resultats"][0]["apparie_v8"])
        promue = ({"promue": True, "log_richesse_max": 5.0, "trajectoire_log_w": [5.0], "membre_dominant_final": "x"},
                  {"promue": True, "log_richesse_max": 5.0, "trajectoire_log_w": [5.0], "membre_dominant_final": "x"})
        with unittest.mock.patch.object(banc, "juger_v9", return_value=promue):
            self.assertEqual(banc.principal([os.path.join(self.tmp, "fatale-promue")] + base), 1)
        inverse = ({"promue": True, "log_richesse_max": 5.0, "trajectoire_log_w": [5.0], "membre_dominant_final": "x"},
                   {"promue": False, "log_richesse_max": 1.0, "trajectoire_log_w": [1.0], "membre_dominant_final": "x"})
        # B1 (contre-lecture R2 n° 1) : monotonie violée par la seule richesse (log W v9 > log W v8 + 10⁻⁶, aucune promotion)
        richesse = ({"promue": False, "log_richesse_max": 2.0, "trajectoire_log_w": [2.0], "membre_dominant_final": "x"},
                    {"promue": False, "log_richesse_max": 1.0, "trajectoire_log_w": [1.0], "membre_dominant_final": "x"})
        for nom, argv, patch, attendu in (
                ("duree", base + ["--duree-max-s", "1e-9"], None, "ArretDuree"),
                ("erreur", base, unittest.mock.patch.object(banc, "juger_v9", side_effect=RuntimeError("panne simulée")), "panne simulée"),
                ("monotonie", base, unittest.mock.patch.object(banc, "juger_v9", return_value=inverse), "MonotonieViolee"),
                ("monotonie-richesse", base, unittest.mock.patch.object(banc, "juger_v9", return_value=richesse), "MonotonieViolee")):
            with self.subTest(arret=nom):
                arret = os.path.join(self.tmp, "arret-" + nom)
                with (patch or contextlib.nullcontext()):
                    code = banc.principal([arret] + argv)
                self.assertEqual(code, 3)
                with open(os.path.join(arret, "banc-tricheurs-v9.json"), encoding="utf-8") as f:
                    self.assertIn(attendu, json.load(f)["arret"])

    def test_duree_du_mode_decisif_48_h(self):
        """Cas sain : la durée gelée du mode décisif est 48 h (aucun couperet sur la mesure) ; artefact : un texte décisif
        lancé avec l'ancienne durée de 8 h est refusé avant toute course (code 2)."""
        self.assertEqual(banc.DUREE_MAX_S, 48 * 3600.0)
        self.silence()
        sortie = os.path.join(self.tmp, "duree-8h")
        prereg = os.path.join(self.tmp, "preenregistrement-validation-nul-v9-v1.md")
        with open(prereg, "w", encoding="utf-8") as f:
            f.write("texte factice")
        with unittest.mock.patch.object(banc, "lire_preenregistrement") as lu:
            self.assertEqual(banc.principal([sortie, "--preenregistrement", prereg, "--duree-max-s", "28800"]), 2)
        lu.assert_not_called()  # refusé sur la durée, avant même de lire le texte
        self.assertFalse(os.path.exists(os.path.join(sortie, "banc-tricheurs-v9.json")))

    def test_mode_decisif_cas_sain_et_refus(self):
        """B1 (contre-lecture R2 n° 1). Cas sain du mode décisif : texte d'essai scellé au nom décisif, gelant les 14 empreintes
        réelles, sans aucune option de plan → toutes les gardes passent et la course démarre une fois (bouchon de `jouer_tout`,
        qui rend un arrêt : code 3), avec les 31 lignes du plan, 1 000 répétitions chacune, la durée gelée (172 800 s) transmise à
        chaque ligne et l'entropie égale à l'empreinte du texte ; manifeste en mode décisif. Artefacts : en mode décisif,
        `--lignes M01`, puis `--repetitions 999` → code 2, aucune course, texte jamais lu, rien écrit."""
        appels = []

        def bouchon(taches, processus):
            appels.append((list(taches), processus))
            return [], "course interrompue par l'essai (bouchon de jouer_tout)"
        self.silence()
        with unittest.mock.patch.object(banc, "DOSSIER_PREREG", os.path.join(self.tmp, "prereg")), \
                unittest.mock.patch.object(banc, "jouer_tout", bouchon):
            p = self._prereg(self._gel())
            sortie = os.path.join(self.tmp, "decisif-sain")
            self.assertEqual(banc.principal([sortie, "--preenregistrement", p]), 3)
            self.assertEqual(len(appels), 1, "le cas sain du mode décisif doit lancer la course une fois")
            taches, processus = appels[0]
            self.assertEqual([(t[1], t[2], t[3]) for t in taches], [tuple(l) for l in banc.LIGNES])
            self.assertEqual(len(taches), 31)
            self.assertEqual({t[0] for t in taches}, {int(sha256_fichier(p), 16)})
            self.assertEqual({t[4] for t in taches}, {banc.REPETITIONS_DECISIVES})
            self.assertEqual({t[6] for t in taches}, {48 * 3600.0}, "durée transmise à la course ≠ durée gelée")
            with open(os.path.join(sortie, "manifeste.json"), encoding="utf-8") as f:
                m = json.load(f)["reglages"]
            self.assertEqual((m["mode"], m["repetitions"], m["duree_max_s"]), ("decisif", 1000, 48 * 3600.0))
            for nom, plus in (("lignes", ["--lignes", "M01"]), ("repetitions", ["--repetitions", "999"])):
                with self.subTest(refus=nom), unittest.mock.patch.object(banc, "lire_preenregistrement") as lu:
                    s = os.path.join(self.tmp, "decisif-" + nom)
                    self.assertEqual(banc.principal([s, "--preenregistrement", p] + plus), 2)
                    lu.assert_not_called()
                    self.assertFalse(os.path.exists(s))
        self.assertEqual(len(appels), 1, "une course a été lancée malgré un refus du mode décisif")

    def test_fichiers_geles_couvrent_les_imports(self):
        script = ("import importlib.util, json, os, sys\nsys.path.insert(0, sys.argv[1])\n"
                  "s = importlib.util.spec_from_file_location('b', os.path.join(sys.argv[1], 'demonstrations', "
                  "'banc_tricheurs_v9.py'))\nm = importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\n"
                  "r = os.path.realpath(sys.argv[1])\nf = [os.path.realpath(getattr(x, '__file__', '') or '') for x in "
                  "list(sys.modules.values())]\nprint(json.dumps(sorted(os.path.relpath(p, r) for p in f if p.startswith(r + os.sep))))\n")
        sortie = subprocess.run([sys.executable, "-I", "-B", "-c", script, RACINE], capture_output=True, text=True, check=True)
        importes = set(json.loads(sortie.stdout)) | {"demonstrations/banc_tricheurs_v9.py", "demonstrations/banc_tricheurs_v8.py",
                                                     "demonstrations/banc_tricheurs_v7.py"}
        self.assertEqual(importes, set(banc.FICHIERS_GELES), "fermeture des imports ≠ fichiers gelés")


class DescriptionPublique(unittest.TestCase):
    def test_description_dit_la_classe_et_le_non_couvert(self):
        """I2 (contre-lecture R2 n° 1) : les trous (`NON_COUVERT_V9`, recombinaisons de lois connues non couvertes) sont séparés
        des choix (`HORS_DU_NUL_PAR_CHOIX_V9`, dépendances aveugles nouvelles) et de la nature (lois hors de l'archive) ; le poids
        commun du bruit est dit. Artefact : la liste du brouillon 2, qui rangeait un choix parmi les trous, est détectée."""
        d = nul_v9.description()
        self.assertEqual(d["nul"], "nul-v9")
        self.assertEqual(len(d["non_couvert"]), 4)
        trous = " ".join(d["non_couvert"])
        for mot in ("profondeur 2", "aiguillage doux", "tempérées", "produits"):
            self.assertIn(mot, trous)
        choix = " ".join(d["hors_du_nul_par_choix"])
        for mot in ("escalier aveugle", "loi aveugle seule sur un morceau", "bruit aveugle propre à un morceau", "autre poids"):
            self.assertIn(mot, choix)
        self.assertIn("hors de l'archive", " ".join(d["hors_du_nul_par_nature"]))
        self.assertIn("sans mémoire", " ".join(d["reserves"]))
        phrase = nul_v9.PHRASES_MEMBRES_V9[nul_v9.TYPE_MORCEAUX]
        for mot in ("tout seuil réel", "bruit aveugle fixe commun", "même poids"):
            self.assertIn(mot, phrase)

        def choix_parmi_les_trous(trous):
            return [p for p in trous if "aveugle" in p]
        self.assertEqual(choix_parmi_les_trous(nul_v9.NON_COUVERT_V9), [])
        liste_du_brouillon_2 = ("morceaux de morceaux (profondeur 2 : sous-population puis seuil, deux seuils, deux traits) et seuils "
                                "sur une combinaison de traits", "poids de mélange qui varient continûment avec les traits (aiguillage "
                                "doux)", "bruit aveugle propre à chaque morceau, ou loi aveugle seule sur un morceau",
                                "lois connues tempérées ou inclinées différemment selon le morceau, compositions d'étapes",
                                "produits de lois connues, déformations non monotones")
        self.assertEqual(len(choix_parmi_les_trous(liste_du_brouillon_2)), 1)

    def test_description_publique_separe_trous_choix_et_nature(self):
        """La description publique (texte) dit le maximum au dénominateur, la classe couverte avec le poids commun du bruit, la
        garantie, puis, dans cet ordre et sans mélange, les trous, les choix, la nature, et les réserves."""
        t = nul_v9.description_publique()
        self.assertEqual(t, nul_v9.description()["description_publique"])
        self.assertIn("maximum (jamais un mélange a priori)", t)
        self.assertIn("même loi aveugle, même poids", t)
        i_trous, i_choix, i_nature, i_res = (t.index("Hors du nul — trous"), t.index("Hors du nul par choix"),
                                             t.index("Hors du nul par nature"), t.index("Réserves"))
        self.assertLess(i_trous, i_choix)
        self.assertLess(i_choix, i_nature)
        self.assertLess(i_nature, i_res)
        trous, choix = t[i_trous:i_choix], t[i_choix:i_nature]
        for p in nul_v9.NON_COUVERT_V9:
            self.assertIn(p, trous)
        for p in nul_v9.HORS_DU_NUL_PAR_CHOIX_V9:
            self.assertIn(p, choix)
            self.assertNotIn(p, trous, "choix rangé parmi les trous")
        for p in nul_v9.HORS_DU_NUL_PAR_NATURE_V9 + nul_v9.RESERVES_V9:
            self.assertIn(p, t[i_nature:])


if __name__ == "__main__":
    unittest.main()
