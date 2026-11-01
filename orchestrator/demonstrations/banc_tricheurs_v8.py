"""Banc des tricheurs, v8 : le juge sous le **nul v8** (`pole/nul_v8.py`) — banc de la validation préenregistrée.

Fichier neuf (v58, R12). Charge le banc v7 (`demonstrations/banc_tricheurs_v7.py`, instance propre, inchangé) pour ses
scénarios (lois des tricheurs et des mondes), sa marginale d'entraînement, ses membres d'archive de v7 (référence de
puissance) et ses constantes (K = 3 issues, 2 traits ; filles : 50 tirages de calibrage puis 200 d'évaluation ; fiches sans
parent : 200 tirages ; lecture aux instants 25, 50, …, 200 ; marge 2δ₀ = 0,02 ; ordre d'exécution secret partout).
Pourquoi une v8 : le banc v7 ne permet ni de juger sous le nul de production (ses membres d'archive « candidat » sont une copie
locale), ni de dériver la graine de l'empreinte d'un préenregistrement (il dérive ses graines par SHA-256, sans
`SeedSequence`). Trois changements :

1. **Le nul.** Toute ligne fatale est jugée sous le nul v8 : membres d'archive de `nul_v8.membres_archive_v8`, c'est-à-dire
   de `cycle.membres_de_l_archive(..., ajuste=True)`, la fonction du juge de production (identiques membre à membre au
   réglage « candidat » du banc v7, et mêmes évaluations aux mêmes graines : essais `essais/test_v58_nul_v8.py`). « v7 »
   ne sert plus que de référence de puissance, « v1 » que d'artefact requis (T01|v1 : le banc a des dents).
2. **Les graines (R9).** `numpy.random.SeedSequence`. Entropie racine : en mode décisif, l'entier non signé gros-boutiste
   des 32 octets de l'empreinte SHA-256 des octets du fichier de préenregistrement scellé (`int(hexdigest, 16)`) ; en mode
   exploratoire, l'entier `--graine`, **exigé dans [0 ; 2⁶⁴[**, tandis qu'une entropie décisive **inférieure à 2⁶⁴ est
   refusée** : les deux espaces sont disjoints, aucune course exploratoire ne peut tomber sur la graine décisive.
   Répétition r de la ligne « nom|nul » : SeedSequence(entropie, spawn_key=(c, r)), c = entier gros-boutiste des 4 premiers
   octets de SHA-256(« nom|nul » en UTF-8) ; trois enfants (`spawn(3)`) : scénario, noyau, tirages frais ; chacun réduit à
   un entier de 128 bits, s₀ + 2⁶⁴·s₁ où (s₀, s₁) = `generate_state(2, numpy.uint64)`. Le juge de production dérive
   ensuite ses graines internes (ordre secret, tirages frais liés à l'empreinte de l'engagement) par
   `outils.graine_derivee` à partir de ces graines — inchangé.
3. **La lecture gelée** du préenregistrement `prereg/preenregistrement-validation-nul-v8-v2.md` (fonction `lire_v8`), ses
   gardes et ses codes de sortie (ci-dessous).

Lignes (nom|nul ; rôle) :
- fatales sous v8 (taux ≤ α = 0,05) : T01, T02, T03u, T03b, T04, T05s, T09g, T09l, T12a, T17s, nul_exact (11 lignes) ; dans
  les classes linéaire (T01, T02, T03u, T03b, T04, T09l, T17s, nul_exact) et log-linéaire (T05s, T09g), la loi du tricheur
  est elle-même un membre du nul v8 : refus à chaque répétition par construction (classe linéaire : log W ≤ 0 aux
  arrondis près ; classe log-linéaire : à la marge de Newton près, borne au second ordre) ; T12a : le monde est au nul, la
  fiche non (borne de Ville seulement) ;
- artefact requis : T01|v1 (> α) ;
- puissance : fille_neuve et fraiche_neuve sous v8 et sous v7 (référence) ; perte = taux(v7) − taux(v8) ;
- mesurées (lues, sans seuil) : T07|v8 (composition, hors de la classe couverte), T12b|v8 (nouveauté : la fiche dit vrai).
Les lignes de multiplicité du banc v7 (T14 à T16, règle e-BH) ne sont pas rejouées : elles ne portent pas sur le nul.

Lecture gelée (`lire_v8`), α = 0,05 :
- lignes fatales : test binomial exact unilatéral (Clopper-Pearson), H0ᵢ « taux ≥ α » contre « taux < α », famille des
  11 lignes fatales, procédure de Holm au niveau familial 0,05 → « tenue » ; dans l'autre sens, H0ᵢ « taux ≤ α », même
  famille, Holm → « non tenue » ; sinon « non jugeable (précision insuffisante) » ;
- artefact : borne basse unilatérale de Clopper-Pearson à 95 % > α → « tenue » ; borne haute < α → « non tenue » ;
- perte de puissance : critère sur une **borne** de la différence, pas sur l'estimation : borne de Newcombe (méthode 10,
  score hybride à partir des intervalles de Wilson ; approchée), H0 « perte ≥ 0,05 », famille des 2 lignes, Holm → « tenue » ;
  H0 « perte ≤ 0,05 » rejetée (Holm) → « non tenue » ;
- issue : « infirmée (validité) » si une ligne fatale est non tenue ; sinon « infirmée (puissance) » si une perte est non
  tenue ; sinon « non jugeable (banc sans dents) » si l'artefact n'est pas tenu ; sinon « confirmée » si tout est tenu ;
  sinon « non jugeable (précision insuffisante) » ; plan incomplet (`--lignes`) : aucune issue ;
- audits écrits d'avance (R4, symétriques) : A1 promotion sur une ligne refusée par construction ; A2 nul v8 plus puissant
  que v7 (borne haute de la perte < 0) ; A3 artefact hors de [0,10 ; 0,90] ; A4 log W > 10⁻⁶ sur une ligne de la classe
  linéaire. Un audit déclenché suspend l'issue jusqu'à l'audit écrit ;
- prédictions (rapportées, sans effet sur l'issue) : `PREDICTIONS`.

Gardes (R5) : mode décisif refusé si le préenregistrement n'est pas le fichier `PREREG_DECISIF`, n'est pas scellé (compagnon
`.sha256` conforme), ne gèle pas l'empreinte de chacun des `FICHIERS_GELES` (le code que la course importe), ou si une
empreinte gelée diffère du fichier présent ; refusé avec `--lignes`, un autre nombre de répétitions que 1 000 ou une autre
durée maximale que 3 heures ; entropie hors de son espace (ci-dessus) refusée ; dossier de sortie non vide refusé ; nom de
ligne inconnu refusé ; arrêt (code 3, aucun verdict, aucun taux) si une ligne lève une erreur, rend une richesse non finie
ou si la durée dépasse `--duree-max-s` — les lignes déjà en cours dans d'autres processus vont alors à leur terme.

Codes de sortie : 0 course complète, aucune ligne fatale au-dessus de α et tout artefact présent au-dessus de α (taux
observés) ; 1 course complète, une ligne fatale au-dessus de α ou un artefact présent non vu (échec de l'intégration
continue) ; 2 refus avant toute course ; 3 arrêt en cours de course.

Usage : python -I -B demonstrations/banc_tricheurs_v8.py DOSSIER_NEUF (--preenregistrement PREREG.md | --graine G)
        [--repetitions 1000] [--processus 2] [--lignes nom1,nom2] [--duree-max-s 10800]
"""

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import sys
import time
from statistics import NormalDist

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402  (SeedSequence, R9 ; numpy ≥ 1.25, déjà requis par le nul des filles v2)

_spec = importlib.util.spec_from_file_location("banc_tricheurs_v7_pour_v8", os.path.join(ICI, "banc_tricheurs_v7.py"))
v7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v7)  # instance propre (R12 : le banc v7 n'est pas touché)

from pole import nul_filles_v2 as nf  # noqa: E402
from pole import nul_v8  # noqa: E402  (appelé par attribut : une mutation du module est vue ici)
from pole import selection_pari as sp  # noqa: E402
from pole.cycle import instants_reguliers  # noqa: E402
from pole.outils import ecrire_json_scelle, manifeste, sha256_fichier, verifier_scelle  # noqa: E402

VERSION = "banc-tricheurs-v8"
K, DIM, TIRAGES, CALIBRAGE, ALPHA, DELTA0 = v7.K, v7.DIM, v7.TIRAGES, v7.CALIBRAGE, v7.ALPHA, v7.DELTA0
INSTANTS = v7.INSTANTS
REPETITIONS_DECISIVES = 1000
DUREE_MAX_S = 3 * 3600.0
NIVEAU_FAMILLE = 0.05  # erreur familiale de chaque famille de décisions (Holm)
GAMMA = 0.05  # bornes unilatérales à 95 %
MARGE_PERTE = 0.05  # perte de puissance admise
Z_95 = NormalDist().inv_cdf(1 - GAMMA)
GRAINE_EXPLORATOIRE_MAX = 2 ** 64  # exploratoire : [0 ; 2⁶⁴[ ; décisif : empreinte SHA-256 ≥ 2⁶⁴ (espaces disjoints)
PREREG_DECISIF = os.path.join(RACINE, "prereg", "preenregistrement-validation-nul-v8-v2.md")
# Code importé par une course du banc (fermeture des imports mesurée, essai `test_fichiers_geles_couvrent_les_imports`) :
# le préenregistrement doit geler l'empreinte de chacun.
FICHIERS_GELES = ("demonstrations/banc_tricheurs_v7.py", "demonstrations/banc_tricheurs_v8.py", "pole/__init__.py",
                  "pole/caviardage.py", "pole/controles_pari.py", "pole/cycle.py", "pole/fiche.py", "pole/memoire.py",
                  "pole/nul_filles_v2.py", "pole/nul_v8.py", "pole/outils.py", "pole/selection_pari.py")
FATALES = ("T01", "T02", "T03u", "T03b", "T04", "T05s", "T09g", "T09l", "T12a", "T17s", "nul_exact")
CLASSE_LINEAIRE = ("T01", "T02", "T03u", "T03b", "T04", "T09l", "T17s", "nul_exact")  # log W ≤ 0 par construction
CLASSE_LOG_LINEAIRE = ("T05s", "T09g")  # membre du nul ; marge de Newton : borne au second ordre (voir pole/nul_v8.py)
TOLERANCE_LOG_W = 1e-6  # audit A4 : arrondis flottants seulement (de l'ordre de 10⁻¹³)
PUISSANCE = ("fille_neuve", "fraiche_neuve")
# Prédictions chiffrées et signées du préenregistrement (rapportées ; elles ne changent pas l'issue).
PREDICTIONS = {"P1_promotions_par_ligne_refusee_par_construction": 0, "P1_taux_max_T12a": 0.010,
               "P2_perte": (-0.02, 0.04), "P3_artefact": (0.30, 0.60), "P4_taux_max_T07": 0.02, "P4_T12b": (0.80, 0.95),
               "P5_puissance_v8_min": 0.95}
AUDIT_ARTEFACT = (0.10, 0.90)  # hors de cette bande, dans un sens ou dans l'autre : audit du banc (R4)
LIGNES = (tuple((n, "v8", "fatale") for n in FATALES)
          + (("T01", "v1", "artefact_requis"),)
          + tuple((n, nul, "puissance") for n in PUISSANCE for nul in ("v8", "v7"))
          + (("T07", "v8", "mesure"), ("T12b", "v8", "mesure")))
DEBUT_EMPREINTES = "<!-- empreintes-du-code : début -->"
FIN_EMPREINTES = "<!-- empreintes-du-code : fin -->"
TENUE, NON_TENUE, NON_JUGEABLE = "tenue", "non tenue", "non jugeable (précision insuffisante)"


class PreenregistrementNonScelle(Exception):
    """Mode décisif sans préenregistrement scellé (compagnon `.sha256` absent ou non conforme)."""


class EcartAuPlan(Exception):
    """Course décisive qui s'écarte du plan gelé (fichier, empreintes du code, lignes, répétitions, durée, entropie)."""


class ArretDuree(Exception):
    """Durée maximale de la course dépassée : arrêt sans verdict."""


# --- graines (R9) ----------------------------------------------------------------------------------------------------
def cle_ligne(ident):
    return int.from_bytes(hashlib.sha256(ident.encode("utf-8")).digest()[:4], "big")


def verifier_cles_distinctes(lignes):
    """Garde : deux lignes ne partagent jamais leur clé de graines (ValueError sinon)."""
    idents = [f"{n}|{nul}" for n, nul, _ in lignes]
    cles = [cle_ligne(i) for i in idents]
    if len(set(idents)) != len(idents) or len(set(cles)) != len(cles):
        raise ValueError(f"lignes en double ou clés de graines en collision : {idents}")
    return lignes


def graines(entropie, ident, r):
    """(scénario, noyau, tirages frais) de la répétition r de la ligne `ident` (« nom|nul »), entiers de 128 bits."""
    enfants = np.random.SeedSequence(int(entropie), spawn_key=(cle_ligne(ident), int(r))).spawn(3)
    sortie = []
    for e in enfants:
        s = e.generate_state(2, dtype=np.uint64)
        sortie.append(int(s[0]) + (int(s[1]) << 64))
    return tuple(sortie)


def entropie_du_preenregistrement(chemin):
    """Règle du préenregistrement : entropie racine = entier de l'empreinte SHA-256 du fichier scellé."""
    empreinte = sha256_fichier(chemin)
    return int(empreinte, 16), empreinte


def lire_preenregistrement(chemin):
    """Mode décisif : le préenregistrement nommé, scellé, gelant le code présent ; rend (entropie, empreinte, gelées)."""
    if os.path.realpath(chemin) != os.path.realpath(PREREG_DECISIF):
        raise EcartAuPlan(f"mode décisif : le préenregistrement est {os.path.relpath(PREREG_DECISIF, RACINE)}, pas {chemin} "
                          "(la graine est l'empreinte de ce fichier-là)")
    if not os.path.isfile(chemin):
        raise PreenregistrementNonScelle(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(chemin):
        raise PreenregistrementNonScelle(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin} "
                                         "— aucune course décisive avant le scellement")
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    debut, fin = texte.find(DEBUT_EMPREINTES), texte.find(FIN_EMPREINTES)
    if debut < 0 or fin < debut:
        raise EcartAuPlan("le préenregistrement ne gèle aucune empreinte du code (bloc « empreintes-du-code » absent)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", texte[debut:fin], re.M)
    if not gelees:
        raise EcartAuPlan("bloc « empreintes-du-code » vide")
    manquants = sorted(set(FICHIERS_GELES) - {relatif for _, relatif in gelees})
    if manquants:
        raise EcartAuPlan(f"code importé par la course non gelé par le préenregistrement : {manquants}")
    ecarts = []
    for attendue, relatif in gelees:
        chemin_code = os.path.join(RACINE, relatif)
        presente = sha256_fichier(chemin_code) if os.path.isfile(chemin_code) else "absent"
        if presente != attendue:
            ecarts.append(f"{relatif} : gelé {attendue[:12]}…, présent {presente[:12]}…")
    if ecarts:
        raise EcartAuPlan("code différent du code gelé par le préenregistrement : " + " ; ".join(ecarts))
    entropie, empreinte = entropie_du_preenregistrement(chemin)
    if entropie < GRAINE_EXPLORATOIRE_MAX:
        raise EcartAuPlan("entropie décisive dans l'espace des graines exploratoires (< 2⁶⁴) : refusée")
    return entropie, empreinte, {relatif: attendue for attendue, relatif in gelees}


# --- juge ------------------------------------------------------------------------------------------------------------
def juger_v8(genre, loi, monde, L, nul, rng, graine_noyau, graine_frais):
    """Évaluation d'une fiche comme `v7.juger` (ordre secret, tirages frais du monde), graines fournies ; nul « v8 » (nul
    d'archive de `nul_v8`, lecture aux instants fixés pour toute fiche), « v7 » (référence) ou « v1 » (artefact)."""
    if nul not in ("v8", "v7", "v1"):
        raise ValueError(f"nul inconnu : {nul!r}")
    q_ent = v7._marginale_entrainement(rng, monde)
    standard = list(sp.BIBLIOTHEQUE_STANDARD) + [{"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}]
    survivantes = {"S1": L["S1"], "S2": L["S2"]}
    if genre == "fille":
        parents = {"A": L["A"], "B": L["B"]}
        instances = sp.tirer_instances(rng, CALIBRAGE + TIRAGES, DIM)
        biblio = sp.bibliotheque_fille(parents, DIM, standard, q_ent, nombre_issues=K)
        if nul == "v8":
            biblio = biblio + nf.membres_de_variante("v2", parents) + nul_v8.membres_archive_v8(survivantes, parents, K, DIM)
        elif nul == "v7":
            biblio = biblio + nf.membres_de_variante("v2", parents) + v7.membres_archive(L, "v7", parents)
        gele = sp.geler_engagement(nf.construire_engagement_v2("fille", loi, instances, K, ALPHA, biblio, CALIBRAGE, DELTA0,
                                                               INSTANTS))
        tirages = sp.tirer_frais(gele, monde, graine_frais, graine_noyau=graine_noyau)
        return nf.evaluer_v2(gele, tirages, graine_noyau=graine_noyau)
    instances = sp.tirer_instances(rng, TIRAGES, DIM)
    if nul == "v8":
        biblio = standard + nul_v8.membres_archive_v8(survivantes, None, K, DIM)
        gele = sp.geler_engagement(nf.construire_engagement_v2("fiche", loi, instances, K, ALPHA, biblio, 0, None,
                                                               instants_reguliers(TIRAGES, len(INSTANTS))))
        tirages = sp.tirer_frais(gele, monde, graine_frais, graine_noyau=graine_noyau)
        return nf.evaluer_v2(gele, tirages, graine_noyau=graine_noyau)
    biblio = standard + v7.membres_archive(L, nul)
    gele = sp.geler_engagement(sp.construire_engagement("fiche", loi, instances, K, ALPHA, biblio, "continu",
                                                        plan_execution="ordre_secret"))
    tirages = sp.tirer_frais(gele, monde, graine_frais, graine_noyau=graine_noyau)
    return sp.evaluer(gele, tirages, graine_noyau=graine_noyau)


def jouer_ligne(entropie, nom, nul, role, repetitions, debut=None, duree_max=None, cle_graines=None):
    """Une ligne : `repetitions` répétitions indépendantes ; rend comptes, taux, bornes de Clopper-Pearson, richesses,
    dominants. `cle_graines` (essais seulement) : rejouer les graines d'une autre ligne (même scénario, autre nul)."""
    ident = f"{nom}|{nul}"
    depart = time.time()
    promues, maxima, dominants = 0, [], {}
    for r in range(repetitions):
        if debut is not None and duree_max is not None and time.time() - debut > duree_max:
            raise ArretDuree(f"{ident} : durée maximale de {duree_max} s dépassée à la répétition {r}")
        g_scenario, g_noyau, g_frais = graines(entropie, cle_graines or ident, r)
        rng = random.Random(g_scenario)
        genre, loi, monde, L = v7.scenario(nom, rng)
        ev = juger_v8(genre, loi, monde, L, nul, rng, g_noyau, g_frais)
        if not math.isfinite(ev["log_richesse_max"]):
            raise FloatingPointError(f"{ident} : richesse non finie à la répétition {r}")
        promues += bool(ev["promue"])
        maxima.append(ev["log_richesse_max"])
        d = ev.get("membre_dominant_final")
        dominants[d] = dominants.get(d, 0) + 1
    maxima.sort()
    bas, haut = clopper_pearson(promues, repetitions)
    return {"ligne": nom, "reglage": nul, "role": role, "promues": promues, "repetitions": repetitions,
            "taux": promues / repetitions, "clopper_pearson_95_unilaterales": [bas, haut],
            "log_w_max_mediane": round(maxima[len(maxima) // 2], 3), "log_w_max_99e": round(maxima[int(0.99 * (len(maxima) - 1))], 3),
            "log_w_max_max": maxima[-1],
            "dominants": dict(sorted(dominants.items(), key=lambda x: (-x[1], str(x[0])))[:4]),
            "duree_s": round(time.time() - depart, 1)}


def _executer(arguments):
    return jouer_ligne(*arguments)


def jouer_tout(taches, processus):
    """Joue les lignes ; rend (résultats, arrêt). Un seul processus : dans ce processus, l'une après l'autre (aucune
    sérialisation) ; sinon un réservoir de processus. Toute ligne en erreur (durée dépassée comprise) arrête la course."""
    resultats = []
    if processus == 1:
        for t in taches:
            try:
                resultats.append(_executer(t))
            except Exception as e:  # noqa: BLE001 — liste d'arrêt
                return resultats, f"{t[1]}|{t[2]} : {type(e).__name__} : {e}"
        return resultats, None
    with concurrent.futures.ProcessPoolExecutor(max_workers=processus) as pool:
        futurs = {pool.submit(_executer, t): f"{t[1]}|{t[2]}" for t in taches}
        for f in concurrent.futures.as_completed(futurs):
            try:
                resultats.append(f.result())
            except Exception as e:  # noqa: BLE001 — liste d'arrêt
                for autre in futurs:
                    autre.cancel()
                return resultats, f"{futurs[f]} : {type(e).__name__} : {e}"
    return resultats, None


def fatales_au_dessus_de_alpha(resultats):
    """Lignes fatales dont le taux observé dépasse α (critère de l'intégration continue)."""
    return sorted(f"{x['ligne']}|{x['reglage']}" for x in resultats if x["role"] == "fatale" and x["taux"] > ALPHA)


def artefacts_non_vus(resultats):
    """Lignes d'artefact requis présentes dont le taux observé ne dépasse pas α (banc sans dents)."""
    return sorted(f"{x['ligne']}|{x['reglage']}" for x in resultats if x["role"] == "artefact_requis" and x["taux"] <= ALPHA)


def code_de_sortie(resultats):
    """0 : aucune ligne fatale au-dessus de α, tout artefact présent vu ; 1 sinon (l'intégration continue échoue)."""
    return 1 if fatales_au_dessus_de_alpha(resultats) or artefacts_non_vus(resultats) else 0


# --- statistique de la lecture gelée ----------------------------------------------------------------------------------
def _log_pmf(i, n, p):
    return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p)
            + (n - i) * math.log1p(-p))


def binom_cdf(x, n, p):
    """P(X ≤ x), X de loi binomiale (n, p), par la somme exacte des termes."""
    if x < 0:
        return 0.0
    if x >= n or p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    return min(1.0, math.fsum(math.exp(_log_pmf(i, n, p)) for i in range(x + 1)))


def binom_sf(x, n, p):
    """P(X ≥ x), X de loi binomiale (n, p), par la somme exacte des termes."""
    if x <= 0:
        return 1.0
    if x > n or p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    return min(1.0, math.fsum(math.exp(_log_pmf(i, n, p)) for i in range(x, n + 1)))


def _bissection(f, a, b, iterations=100):
    """Racine de f, croissante sur [a ; b], par bissection (f(a) ≤ 0 ≤ f(b))."""
    for _ in range(iterations):
        c = (a + b) / 2
        a, b = (c, b) if f(c) < 0 else (a, c)
    return (a + b) / 2


def clopper_pearson(x, n, gamma=GAMMA):
    """Bornes de Clopper-Pearson (exactes) d'une proportion, chacune unilatérale au niveau de confiance 1 − gamma."""
    bas = 0.0 if x == 0 else _bissection(lambda p: binom_sf(x, n, p) - gamma, 0.0, 1.0)
    haut = 1.0 if x == n else _bissection(lambda p: gamma - binom_cdf(x, n, p), 0.0, 1.0)
    return bas, haut


def p_valeur_exacte(succes, n, seuil, sens):
    """Valeur p du test binomial exact unilatéral : « haute » pour H0 « taux ≥ seuil » (P(X ≤ x) au taux seuil ; rejet au
    niveau a ⇔ borne haute de Clopper-Pearson au niveau a sous le seuil), « basse » pour H0 « taux ≤ seuil » (P(X ≥ x))."""
    if sens == "haute":
        return binom_cdf(succes, n, seuil)
    if sens == "basse":
        return binom_sf(succes, n, seuil)
    raise ValueError(f"sens : « haute » ou « basse », reçu {sens!r}")


def wilson(succes, n, z):
    """Bornes de Wilson (score) d'une proportion, au quantile normal z (unilatérales au niveau Φ(z)) — pour Newcombe."""
    p = succes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - demi), min(1.0, centre + demi)


def newcombe(x1, n1, x2, n2, z):
    """Bornes de Newcombe (méthode 10, score hybride, Wilson) de p1 − p2, au quantile z (unilatérales au niveau Φ(z))."""
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1, z)
    l2, u2 = wilson(x2, n2, z)
    d = p1 - p2
    return d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def p_valeur_newcombe(x1, n1, x2, n2, marge, sens):
    """Valeur p unilatérale par inversion des bornes de Newcombe (bissection sur z) : « haute » pour H0 « p1 − p2 ≥ marge »,
    « basse » pour H0 « p1 − p2 ≤ marge »."""
    d = x1 / n1 - x2 / n2
    if (sens == "haute" and d >= marge) or (sens == "basse" and d <= marge):
        return 1.0

    def rejette(z):
        bas, haut = newcombe(x1, n1, x2, n2, z)
        return haut < marge if sens == "haute" else bas > marge
    if rejette(40.0):
        return 1.0 - NormalDist().cdf(40.0)
    a, b = 0.0, 40.0
    for _ in range(200):
        c = (a + b) / 2
        a, b = (c, b) if rejette(c) else (a, c)
    return 1.0 - NormalDist().cdf(a)


def holm(p_valeurs, niveau=NIVEAU_FAMILLE):
    """Procédure de Holm (descendante) : ensemble des hypothèses rejetées au niveau familial `niveau`."""
    ordre = sorted(p_valeurs, key=lambda c: (p_valeurs[c], c))
    rejetees = set()
    for j, cle in enumerate(ordre):
        if p_valeurs[cle] > niveau / (len(ordre) - j):
            break
        rejetees.add(cle)
    return rejetees


def promotions_max_tenue(n, m, seuil=ALPHA, niveau=NIVEAU_FAMILLE):
    """Pour chaque rang j = 1..m de Holm (valeurs p croissantes), le plus grand nombre de promotions sur n répétitions dont
    la valeur p exacte « haute » passe le seuil de Holm du rang, niveau/(m − j + 1)."""
    sortie = []
    for j in range(1, m + 1):
        a, x = niveau / (m - j + 1), -1
        while binom_cdf(x + 1, n, seuil) <= a:
            x += 1
        sortie.append(x)
    return sortie


def promotions_min_artefact(n, seuil=ALPHA, gamma=GAMMA):
    """Plus petit nombre de promotions dont la borne basse de Clopper-Pearson (1 − gamma) dépasse le seuil."""
    x = 0
    while binom_sf(x, n, seuil) > gamma:
        x += 1
    return x


# --- lecture gelée ---------------------------------------------------------------------------------------------------
def lire_v8(resultats, complet):
    """Lecture gelée du préenregistrement ; `complet` : toutes les lignes du plan sont présentes."""
    par = {f"{x['ligne']}|{x['reglage']}": x for x in resultats}
    fatales = {c: x for c, x in par.items() if x["role"] == "fatale"}
    p_haute = {c: p_valeur_exacte(x["promues"], x["repetitions"], ALPHA, "haute") for c, x in fatales.items()}
    p_basse = {c: p_valeur_exacte(x["promues"], x["repetitions"], ALPHA, "basse") for c, x in fatales.items()}
    tenues, cedees = holm(p_haute), holm(p_basse)
    lecture = {"fatales": {c: TENUE if c in tenues else NON_TENUE if c in cedees else NON_JUGEABLE for c in sorted(fatales)},
               "fatales_valeurs_p": {c: {"H0_taux_au_moins_alpha": p_haute[c], "H0_taux_au_plus_alpha": p_basse[c]}
                                     for c in sorted(fatales)}}
    lecture["artefact"] = {}
    for c, x in sorted(par.items()):
        if x["role"] == "artefact_requis":
            bas, haut = clopper_pearson(x["promues"], x["repetitions"])
            lecture["artefact"][c] = TENUE if bas > ALPHA else NON_TENUE if haut < ALPHA else NON_JUGEABLE
    paires = {n: (par[f"{n}|v7"], par[f"{n}|v8"]) for n in PUISSANCE if f"{n}|v7" in par and f"{n}|v8" in par}
    p_haut = {n: p_valeur_newcombe(a["promues"], a["repetitions"], b["promues"], b["repetitions"], MARGE_PERTE, "haute")
              for n, (a, b) in paires.items()}
    p_bas = {n: p_valeur_newcombe(a["promues"], a["repetitions"], b["promues"], b["repetitions"], MARGE_PERTE, "basse")
             for n, (a, b) in paires.items()}
    tenues_p, cedees_p = holm(p_haut), holm(p_bas)
    lecture["perte_de_puissance"] = {n: TENUE if n in tenues_p else NON_TENUE if n in cedees_p else NON_JUGEABLE
                                     for n in sorted(paires)}
    lecture["pertes_observees"] = {n: round(a["taux"] - b["taux"], 4) for n, (a, b) in sorted(paires.items())}
    lecture["pertes_bornes_newcombe_95_non_corrigees"] = {
        n: list(newcombe(a["promues"], a["repetitions"], b["promues"], b["repetitions"], Z_95)) for n, (a, b) in sorted(paires.items())}
    lecture["mesures"] = {c: {"taux": x["taux"], "clopper_pearson_95_unilaterales": x["clopper_pearson_95_unilaterales"]}
                          for c, x in sorted(par.items()) if x["role"] == "mesure"}
    audits = []
    for c, x in sorted(fatales.items()):
        if x["ligne"] in CLASSE_LINEAIRE + CLASSE_LOG_LINEAIRE and x["promues"] > 0:
            audits.append(f"A1 {c} : {x['promues']} promotion(s) sur une ligne refusée par construction — audit du code (R4)")
        if x["ligne"] in CLASSE_LINEAIRE and x["log_w_max_max"] > TOLERANCE_LOG_W:
            audits.append(f"A4 {c} : log W = {x['log_w_max_max']:.3g} > 0 dans la classe linéaire (borne par construction "
                          "dépassée) — audit du code (R4)")
    for n, (a, b) in sorted(paires.items()):
        if newcombe(a["promues"], a["repetitions"], b["promues"], b["repetitions"], Z_95)[1] < 0:
            audits.append(f"A2 {n} : nul v8 plus puissant que v7 (borne haute de la perte < 0), contraire à l'argument de "
                          "validité — audit (R4)")
    for c, x in sorted(par.items()):
        if x["role"] == "artefact_requis" and not AUDIT_ARTEFACT[0] <= x["taux"] <= AUDIT_ARTEFACT[1]:
            audits.append(f"A3 {c} : taux {x['taux']} hors de [{AUDIT_ARTEFACT[0]} ; {AUDIT_ARTEFACT[1]}] — audit du banc (R4)")
    lecture["audits"] = audits
    P = PREDICTIONS
    lecture["predictions"] = {
        "P1_lignes_fatales": {c: (x["taux"] <= P["P1_taux_max_T12a"] if x["ligne"] == "T12a"
                                  else x["promues"] == P["P1_promotions_par_ligne_refusee_par_construction"])
                              for c, x in sorted(fatales.items())},
        "P2_perte_dans_l_intervalle": {n: P["P2_perte"][0] <= v <= P["P2_perte"][1]
                                       for n, v in lecture["pertes_observees"].items()},
        "P3_artefact_dans_l_intervalle": {c: P["P3_artefact"][0] <= x["taux"] <= P["P3_artefact"][1]
                                          for c, x in sorted(par.items()) if x["role"] == "artefact_requis"},
        "P4_mesures": {c: (x["taux"] <= P["P4_taux_max_T07"] if x["ligne"] == "T07" else P["P4_T12b"][0] <= x["taux"] <= P["P4_T12b"][1])
                       for c, x in sorted(par.items()) if x["role"] == "mesure"},
        "P5_puissance_v8": {c: x["taux"] >= P["P5_puissance_v8_min"] for c, x in sorted(par.items())
                            if x["role"] == "puissance" and x["reglage"] == "v8"}}
    artefacts = list(lecture["artefact"].values())
    if not complet:
        issue = "partielle (plan incomplet : aucune issue)"
    elif NON_TENUE in lecture["fatales"].values():
        issue = "infirmée (validité)"
    elif NON_TENUE in lecture["perte_de_puissance"].values():
        issue = "infirmée (puissance)"
    elif not artefacts or any(v != TENUE for v in artefacts):
        issue = "non jugeable (banc sans dents)"
    elif all(v == TENUE for v in list(lecture["fatales"].values()) + list(lecture["perte_de_puissance"].values())):
        issue = "confirmée"
    else:
        issue = "non jugeable (précision insuffisante)"
    lecture["issue"] = issue
    lecture["issue_suspendue_par_audit"] = bool(audits)
    return lecture


# --- course ----------------------------------------------------------------------------------------------------------
def selection(lignes):
    if not lignes:
        return list(LIGNES)
    noms = [n for n in lignes.split(",") if n]
    inconnus = sorted(set(noms) - {l[0] for l in LIGNES})
    if inconnus or not noms:
        raise ValueError(f"--lignes : nom(s) inconnu(s) {inconnus} ; connus : {sorted({l[0] for l in LIGNES})}")
    return [l for l in LIGNES if l[0] in noms]


def principal(argv=None):
    a = argparse.ArgumentParser(description="Banc des tricheurs sous le nul v8")
    a.add_argument("dossier")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--preenregistrement", help="mode décisif : préenregistrement scellé (graine = son empreinte)")
    g.add_argument("--graine", type=int, help="mode exploratoire, non décisif : entier dans [0 ; 2⁶⁴[")
    a.add_argument("--repetitions", type=int, default=REPETITIONS_DECISIVES)
    a.add_argument("--processus", type=int, default=2)
    a.add_argument("--lignes", help="sous-ensemble : noms séparés par des virgules (exploratoire seulement)")
    a.add_argument("--duree-max-s", type=float, default=DUREE_MAX_S)
    args = a.parse_args(argv)
    try:
        if os.path.exists(args.dossier) and os.listdir(args.dossier):
            raise FileExistsError(f"dossier de sortie non vide : {args.dossier} (on n'écrase jamais)")
        if args.repetitions < 1 or args.processus < 1 or not args.duree_max_s > 0:
            raise ValueError("--repetitions, --processus : entiers ≥ 1 ; --duree-max-s > 0")
        lignes = verifier_cles_distinctes(selection(args.lignes))
        preenregistrement = None
        if args.preenregistrement:
            if args.lignes or args.repetitions != REPETITIONS_DECISIVES or args.duree_max_s != DUREE_MAX_S:
                raise EcartAuPlan(f"mode décisif : toutes les lignes, {REPETITIONS_DECISIVES} répétitions, durée maximale "
                                  f"{DUREE_MAX_S:.0f} s (plan gelé)")
            entropie, empreinte, gelees = lire_preenregistrement(args.preenregistrement)
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE),
                                 "sha256": empreinte, "empreintes_du_code_verifiees": gelees}
            mode = "decisif"
        else:
            if not 0 <= args.graine < GRAINE_EXPLORATOIRE_MAX:
                raise ValueError("--graine : entier dans [0 ; 2⁶⁴[ (au-delà : espace réservé aux graines décisives)")
            entropie, mode = args.graine, "exploratoire (non décisif)"
    except (FileExistsError, ValueError, PreenregistrementNonScelle, EcartAuPlan) as e:
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    os.makedirs(args.dossier, exist_ok=True)
    m = manifeste(banc=VERSION, mode=mode, entropie_racine=str(entropie), repetitions=args.repetitions,
                  processus=args.processus, duree_max_s=args.duree_max_s, lignes=[list(l) for l in lignes],
                  preenregistrement=preenregistrement, nul=nul_v8.description(), numpy=np.__version__,
                  code_du_banc_sha256={relatif: sha256_fichier(os.path.join(RACINE, relatif)) for relatif in FICHIERS_GELES})
    m["regle_des_graines"] = ("numpy.random.SeedSequence (R9) : entropie racine = int(empreinte SHA-256 du préenregistrement "
                              "scellé, 16) en mode décisif, --graine (< 2^64) sinon ; répétition r de la ligne « nom|nul » : "
                              "spawn_key=(4 premiers octets gros-boutistes de SHA-256(« nom|nul »), r), spawn(3) : scénario, "
                              "noyau, tirages frais, chacun s0 + 2^64·s1 de generate_state(2, uint64) ; graines internes du "
                              "juge de production dérivées ensuite par outils.graine_derivee (inchangé)")
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), m)
    debut = time.time()
    resultats, arret = jouer_tout([(entropie, n, nul, role, args.repetitions, debut, args.duree_max_s)
                                   for n, nul, role in lignes], args.processus)
    if arret is not None:
        rapport = {"banc": VERSION, "mode": mode, "arret": arret, "duree_s": round(time.time() - debut, 1),
                   "issue": "non jugeable (arrêt) : aucun verdict, aucun taux rapporté",
                   "lignes_terminees": sorted(f"{x['ligne']}|{x['reglage']}" for x in resultats)}
        ecrire_json_scelle(os.path.join(args.dossier, "banc-tricheurs-v8.json"), rapport)
        print(json.dumps(rapport, ensure_ascii=False, indent=1), file=sys.stderr)
        return 3
    ordre = {f"{n}|{nul}": i for i, (n, nul, _) in enumerate(LIGNES)}
    resultats.sort(key=lambda x: ordre[f"{x['ligne']}|{x['reglage']}"])
    lecture = lire_v8(resultats, complet=len(resultats) == len(LIGNES))
    au_dessus, sans_dents = fatales_au_dessus_de_alpha(resultats), artefacts_non_vus(resultats)
    rapport = {"banc": VERSION, "mode": mode, "preenregistrement": preenregistrement, "repetitions": args.repetitions,
               "duree_s": round(time.time() - debut, 1), "lecture": lecture, "fatales_au_dessus_de_alpha": au_dessus,
               "artefacts_non_vus": sans_dents, "resultats": resultats}
    ecrire_json_scelle(os.path.join(args.dossier, "banc-tricheurs-v8.json"), rapport)
    print(json.dumps({"mode": mode, "issue": lecture["issue"], "fatales": lecture["fatales"],
                      "artefact": lecture["artefact"], "perte_de_puissance": lecture["perte_de_puissance"],
                      "audits": lecture["audits"], "fatales_au_dessus_de_alpha": au_dessus, "artefacts_non_vus": sans_dents,
                      "taux": {f"{x['ligne']}|{x['reglage']}": x["taux"] for x in resultats},
                      "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return code_de_sortie(resultats)


if __name__ == "__main__":
    sys.exit(principal())
