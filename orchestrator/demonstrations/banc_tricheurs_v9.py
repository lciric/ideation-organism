"""Banc des tricheurs, v9 : le juge sous le **nul v9** (`pole/nul_v9.py`) — banc de la validation préenregistrée (brouillon).

Fichier neuf (R12). Charge le banc v8 (`demonstrations/banc_tricheurs_v8.py`, instance propre, inchangé), qui charge le banc v7 :
scénarios des tricheurs du v8, marginale d'entraînement, juge v8 et v1 (`juger_v8`), statistique de la lecture (test binomial
exact, Clopper-Pearson, Holm), constantes (K = 3 issues, 2 traits, 2 sous-populations ; filles : 50 tirages de calibrage puis
200 d'évaluation ; fiches sans parent : 200 tirages ; lecture aux instants 25, 50, …, 200 ; marge 2δ₀ = 0,02 ; ordre secret).
Préenregistrement : `prereg/preenregistrement-validation-nul-v9-brouillon1.md` (brouillon, non scellé ; le banc n'accepte en
mode décisif qu'un texte scellé nommé `prereg/preenregistrement-validation-nul-v9-v<N>.md`).

Trois changements par rapport au banc v8 :
1. **Le nul.** Toute ligne est jugée sous le nul v9 (`nul_v9.membres_archive_v9`, `nul_v9.evaluer_v9`) ; le nul v1 ne sert qu'à
   l'artefact T01|v1 (repris du v8).
2. **Le nul v8 apparié.** Dans chaque répétition d'une ligne v9, la **même** fiche est aussi évaluée sous le nul v8 sur **les
   mêmes issues** (`nul_v9.evaluer_sur_issues(nul_v9.sans_morceaux(engagement), issues)` : la bibliothèque v9 moins ses membres
   par morceaux est exactement celle du v8). D'où : (a) la perte de puissance mesurée **par paires** (part des répétitions
   promues sous v8 et non sous v9, proportion binomiale, Clopper-Pearson) au lieu de deux échantillons indépendants ;
   (b) les dents du banc sur la classe nouvelle (M01 et M02 promus sous v8 au-dessus de α) ; (c) la monotonie vérifiée à chaque
   répétition (log W v9 ≤ log W v8 à chaque instant lu ; aucune promotion sous v9 sans promotion sous v8).
3. **Les lignes nouvelles** (scénarios `scenario_v9`, tirés comme ceux du v7 : A, B parents ; S1, S2 survivantes ; N loi
   neuve ; softmax au hasard ; q loi aveugle de Dirichlet ; monde = loi du tricheur, sauf mention).

Lignes (nom|nul ; rôle) :
- fatales sous v9 (taux ≤ α) : les 11 du v8 (T01, T02, T03u, T03b, T04, T05s, T09g, T09l, T12a, T17s, nul_exact) et 7 tricheurs
  par morceaux : M01 S1 sur g = 0, S2 sur g = 1 (le monde W2 de l'attaque) ; M02 si z_j > s alors S1 sinon S2 (j au hasard,
  s uniforme dans [−1 ; 1]) ; M03 M01 avec bruit (mélange commun à une loi aveugle q, ε dans [0,05 ; 0,30]) ; M04 M02 avec
  bruit ; M05 un mélange de S1 et S2 propre à chaque sous-population ; M06 fille, A au-dessus d'un seuil, S1 en dessous ;
  M07 seuil extrême (s dans [1,5 ; 2,5], quelques instances au-dessus) ;
- artefacts requis (taux > α) : T01|v1 (repris du v8), et, sur les mêmes répétitions, M01 et M02 sous le nul v8 apparié ;
- puissance appariée (v9 et v8 sur les mêmes issues ; perte = part promue sous v8 et non sous v9) : fille_neuve, fraiche_neuve
  (reprises du v8), I01 interaction forte (loi qui ne dépend que du signe de z0·z1 : ni l'archive ni ses morceaux ne la
  décrivent), I02 interaction faible, F03 loi neuve faible (N, poids × 0,3) ;
- mesurées sous v9 (lues, sans seuil ; hors de la classe couverte) : T07, T12b (du v8), H01 profondeur 2, H02 escalier (trois
  seuils sur un trait), H03 produit de deux survivantes, H04 bruit propre à chaque morceau, H05 morceau tempéré.

Lecture gelée (`lire_v9`), α = 0,05 : voir le préenregistrement (sections 5 à 7) ; issues « confirmé », « trou »,
« puissance perdue », « non concluant (banc sans dents) », « non concluant (précision insuffisante) ».

Gardes (R5) : mode décisif refusé si le préenregistrement n'est pas un fichier `prereg/preenregistrement-validation-nul-v9-v<N>.md`
(N entier ≥ 1), n'est pas scellé, ne gèle pas chacun des `FICHIERS_GELES`, ou si une empreinte gelée diffère ; refusé avec
`--lignes`, un autre nombre de répétitions que 1 000, une autre durée maximale que 8 heures ; entropie hors de son espace
refusée ; dossier de sortie non vide refusé ; arrêt (code 3, aucun taux) sur une erreur, une richesse non finie ou la durée.

Codes de sortie : 0 course complète, aucune ligne fatale au-dessus de α et tout artefact au-dessus de α ; 1 sinon ; 2 refus avant
toute course ; 3 arrêt en cours de course. **Le code ne décide rien** : seule la lecture gelée décide.

Usage : python -I -B demonstrations/banc_tricheurs_v9.py DOSSIER_NEUF (--preenregistrement PREREG.md | --graine G)
        [--repetitions 1000] [--processus 2] [--lignes nom1,nom2] [--duree-max-s 28800]
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

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402  (SeedSequence, R9)

_spec = importlib.util.spec_from_file_location("banc_tricheurs_v8_pour_v9", os.path.join(ICI, "banc_tricheurs_v8.py"))
v8 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v8)  # instance propre (R12 : le banc v8 n'est pas touché)
v7 = v8.v7

from pole import nul_filles_v2 as nf  # noqa: E402
from pole import nul_v9  # noqa: E402  (appelé par attribut : une mutation du module est vue ici)
from pole import selection_pari as sp  # noqa: E402
from pole.controles_pari import _dirichlet, _fixe  # noqa: E402
from pole.cycle import instants_reguliers  # noqa: E402
from pole.outils import ecrire_json_scelle, manifeste, sha256_fichier, verifier_scelle  # noqa: E402

VERSION = "banc-tricheurs-v9"
K, DIM, TIRAGES, CALIBRAGE, ALPHA, DELTA0 = v8.K, v8.DIM, v8.TIRAGES, v8.CALIBRAGE, v8.ALPHA, v8.DELTA0
INSTANTS = v8.INSTANTS
REPETITIONS_DECISIVES = 1000
DUREE_MAX_S = 8 * 3600.0
NIVEAU_FAMILLE = 0.05
GAMMA = 0.05
MARGE_PERTE = 0.05  # perte de puissance appariée admise sur chaque ligne de puissance (préenregistrement, section 5)
GRAINE_EXPLORATOIRE_MAX = 2 ** 64
MOTIF_PREREG = re.compile(r"^preenregistrement-validation-nul-v9-v[1-9][0-9]*\.md$")
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
FICHIERS_GELES = ("demonstrations/banc_tricheurs_v7.py", "demonstrations/banc_tricheurs_v8.py",
                  "demonstrations/banc_tricheurs_v9.py", "pole/__init__.py", "pole/caviardage.py", "pole/controles_pari.py",
                  "pole/cycle.py", "pole/fiche.py", "pole/memoire.py", "pole/nul_filles_v2.py", "pole/nul_v8.py",
                  "pole/nul_v9.py", "pole/outils.py", "pole/selection_pari.py")
FATALES_V8 = ("T01", "T02", "T03u", "T03b", "T04", "T05s", "T09g", "T09l", "T12a", "T17s", "nul_exact")
MORCEAUX = ("M01", "M02", "M03", "M04", "M05", "M06", "M07")
FATALES = FATALES_V8 + MORCEAUX
CLASSE_LINEAIRE = ("T01", "T02", "T03u", "T03b", "T04", "T09l", "T17s", "nul_exact")  # log W ≤ 0 par construction
CLASSE_MORCEAUX = MORCEAUX  # log W ≤ 0 par construction (certificat exact du membre par morceaux)
CLASSE_LOG_LINEAIRE = ("T05s", "T09g")  # membre du nul ; marge de Newton : borne au second ordre (réserve du v8)
ARTEFACTS_APPARIES = ("M01", "M02")  # dents du banc sur la classe nouvelle : promus sous le nul v8 apparié
PUISSANCE = ("fille_neuve", "fraiche_neuve", "I01", "I02", "F03")
MESUREES = ("T07", "T12b", "H01", "H02", "H03", "H04", "H05")
TOLERANCE_LOG_W = 1e-6
TOLERANCE_MONOTONIE = 1e-9
SEUIL_ECART_RESIDUEL = 1e-2  # audit A7 : optimisation des membres par morceaux restée lâche (prix en puissance seulement)
AUDIT_ARTEFACT_V1 = (0.10, 0.90)
AUDIT_ARTEFACT_MORCEAUX_MIN = 0.50
# Prédictions chiffrées et signées du brouillon 1 (rapportées ; elles ne changent pas l'issue ; préenregistrement, section 4).
PREDICTIONS = {"P1_promotions_par_ligne_refusee_par_construction": 0, "P1_taux_max_T12a": 0.010,
               "P2_dents_morceaux_v8_min": {"M01": 0.95, "M02": 0.90}, "P3_artefact_v1": (0.30, 0.60),
               "P4_perte_appariee": {"fille_neuve": (0.01, 0.08), "fraiche_neuve": (0.00, 0.03), "I01": (0.02, 0.09),
                                     "I02": (0.06, 0.17), "F03": (0.01, 0.07)},
               "P5_puissance_v9": {"fille_neuve": (0.90, 1.0), "fraiche_neuve": (0.88, 1.0), "I01": (0.80, 1.0),
                                   "I02": (0.30, 0.52), "F03": (0.60, 0.82)},
               "P6_mesurees_v9": {"T07": (0.0, 0.03), "T12b": (0.65, 0.88), "H01": (0.80, 0.96), "H02": (0.12, 0.32),
                                  "H03": (0.82, 0.96), "H04": (0.16, 0.38), "H05": (0.04, 0.18)},
               "P7_issue": "puissance perdue"}
LIGNES = (tuple((n, "v9", "fatale") for n in FATALES)
          + (("T01", "v1", "artefact_requis"),)
          + tuple((n, "v9", "puissance") for n in PUISSANCE)
          + tuple((n, "v9", "mesure") for n in MESUREES))
DEBUT_EMPREINTES = v8.DEBUT_EMPREINTES
FIN_EMPREINTES = v8.FIN_EMPREINTES
TENUE, NON_TENUE, NON_JUGEABLE = v8.TENUE, v8.NON_TENUE, v8.NON_JUGEABLE
ISSUES = ("confirmé", "trou", "puissance perdue", "non concluant (banc sans dents)", "non concluant (précision insuffisante)")


class PreenregistrementNonScelle(Exception):
    """Mode décisif sans préenregistrement scellé (compagnon `.sha256` absent ou non conforme)."""


class EcartAuPlan(Exception):
    """Course décisive qui s'écarte du plan gelé (fichier, empreintes du code, lignes, répétitions, durée, entropie)."""


class ArretDuree(Exception):
    """Durée maximale de la course dépassée : arrêt sans verdict."""


class MonotonieViolee(Exception):
    """Une répétition où le nul v9 promeut sans le v8, ou rend une richesse au-dessus de celle du v8 : défaut du code."""


# --- graines (R9) : celles du banc v8, inchangées ---------------------------------------------------------------------------
cle_ligne = v8.cle_ligne
graines = v8.graines


def verifier_cles_distinctes(lignes):
    idents = [f"{n}|{nul}" for n, nul, _ in lignes]
    cles = [cle_ligne(i) for i in idents]
    if len(set(idents)) != len(idents) or len(set(cles)) != len(cles):
        raise ValueError(f"lignes en double ou clés de graines en collision : {idents}")
    return lignes


# --- scénarios ---------------------------------------------------------------------------------------------------------------
def _par_sp(l0, l1):
    return {"type": "par_sous_population", "lois": {"0": l0, "1": l1}}


def _si_seuil(j, s, si, sinon):
    return {"type": "si_sinon", "condition": {"indice": j, "seuil": s}, "si": si, "sinon": sinon}


def _melange(lois, poids):
    return {"type": "melange", "composantes": list(lois), "poids": list(poids)}


def _poids(a):
    a = round(a, 6)
    return [a, round(1.0 - a, 6)]


def _xor(q1, q2):
    """Interaction pure : q1 si z0 et z1 sont du même côté de 0, q2 sinon (aucun trait seul ne dit rien)."""
    return _si_seuil(0, 0.0, _si_seuil(1, 0.0, q1, q2), _si_seuil(1, 0.0, q2, q1))


def _loi_contraste(rng, force):
    """Loi aveugle fixe tirée au hasard, de contraste réglé par `force` (logits gaussiens d'écart type `force`)."""
    u = [rng.gauss(0.0, force) for _ in range(K)]
    m = max(u)
    e = [math.exp(x - m) for x in u]
    return _fixe([round(x / sum(e), 9) for x in e])


def scenario_v9(nom, rng):
    """(genre, loi de la fiche, loi du monde, lois) ; genre « fille » (parents A, B) ou « fraiche » (sans parent)."""
    if nom in FATALES_V8 or nom in ("T07", "T12b", "fille_neuve", "fraiche_neuve"):
        return v7.scenario(nom, rng)
    L = v7._monde_lois(rng)
    A, S1, S2, N = L["A"], L["S1"], L["S2"], L["N"]
    q = _fixe(_dirichlet(rng, K, 1.0))
    if nom == "M01":
        loi = _par_sp(S1, S2)
    elif nom == "M02":
        loi = _si_seuil(rng.randrange(DIM), round(rng.uniform(-1.0, 1.0), 6), S1, S2)
    elif nom == "M03":
        eps = rng.uniform(0.05, 0.30)
        loi = _melange([_par_sp(S1, S2), q], _poids(1.0 - eps))
    elif nom == "M04":
        eps = rng.uniform(0.05, 0.30)
        loi = _melange([_si_seuil(rng.randrange(DIM), round(rng.uniform(-1.0, 1.0), 6), S1, S2), q], _poids(1.0 - eps))
    elif nom == "M05":
        loi = _par_sp(_melange([S1, S2], _poids(rng.uniform(0.0, 1.0))), _melange([S1, S2], _poids(rng.uniform(0.0, 1.0))))
    elif nom == "M06":
        loi = _si_seuil(rng.randrange(DIM), round(rng.uniform(-1.0, 1.0), 6), A, S1)
        return "fille", loi, loi, L
    elif nom == "M07":
        loi = _si_seuil(rng.randrange(DIM), round(rng.uniform(1.5, 2.5), 6), S1, S2)
    elif nom == "H01":
        loi = _par_sp(_si_seuil(rng.randrange(DIM), round(rng.uniform(-1.0, 1.0), 6), S1, S2), S2)
    elif nom == "H02":
        j = rng.randrange(DIM)
        loi = _si_seuil(j, 0.5, S1, _si_seuil(j, 0.0, _melange([S1, S2], [0.75, 0.25]),
                                              _si_seuil(j, -0.5, _melange([S1, S2], [0.25, 0.75]), S2)))
    elif nom == "H03":
        loi = {"type": "softmax", "poids": [[a + b for a, b in zip(la, lb)] for la, lb in zip(S1["poids"], S2["poids"])],
               "biais": [a + b for a, b in zip(S1["biais"], S2["biais"])]}
    elif nom == "H04":
        q1 = _fixe(_dirichlet(rng, K, 1.0))
        loi = _par_sp(_melange([S1, q], _poids(1.0 - rng.uniform(0.1, 0.4))),
                      _melange([S2, q1], _poids(1.0 - rng.uniform(0.1, 0.4))))
    elif nom == "H05":
        loi = _par_sp({"type": "transformee", "base": S1, "puissance": round(rng.uniform(0.5, 1.5), 6)}, S2)
    elif nom == "I01":
        loi = _xor(_loi_contraste(rng, 1.2), _loi_contraste(rng, 1.2))
    elif nom == "I02":
        loi = _xor(_loi_contraste(rng, 0.45), _loi_contraste(rng, 0.45))
    elif nom == "F03":
        loi = {"type": "softmax", "poids": [[0.3 * w for w in ligne] for ligne in N["poids"]], "biais": list(N["biais"])}
    else:
        raise ValueError(nom)
    return "fraiche", loi, loi, L


# --- juge --------------------------------------------------------------------------------------------------------------------
def engagement_v9(genre, loi, monde, L, rng):
    """Engagement gelé sous le nul v9, comme `banc_tricheurs_v8.juger_v8` sous le v8 (même ordre de tirage du générateur :
    marginale d'entraînement, puis instances)."""
    q_ent = v7._marginale_entrainement(rng, monde)
    standard = list(sp.BIBLIOTHEQUE_STANDARD) + [{"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}]
    survivantes = {"S1": L["S1"], "S2": L["S2"]}
    if genre == "fille":
        parents = {"A": L["A"], "B": L["B"]}
        instances = sp.tirer_instances(rng, CALIBRAGE + TIRAGES, DIM)
        biblio = (sp.bibliotheque_fille(parents, DIM, standard, q_ent, nombre_issues=K) + nf.membres_de_variante("v2", parents)
                  + nul_v9.membres_archive_v9(survivantes, parents, K, DIM))
        return sp.geler_engagement(nf.construire_engagement_v2("fille", loi, instances, K, ALPHA, biblio, CALIBRAGE, DELTA0,
                                                               INSTANTS))
    instances = sp.tirer_instances(rng, TIRAGES, DIM)
    biblio = standard + nul_v9.membres_archive_v9(survivantes, None, K, DIM)
    return sp.geler_engagement(nf.construire_engagement_v2("fiche", loi, instances, K, ALPHA, biblio, 0, None,
                                                           instants_reguliers(TIRAGES, len(INSTANTS))))


def juger_v9(genre, loi, monde, L, rng, graine_noyau, graine_frais):
    """(évaluation sous v9, évaluation sous v8 **sur les mêmes issues**). La première passe par le juge (`evaluer_v9`, gardes
    comprises) ; la seconde par `evaluer_sur_issues` sur la bibliothèque v9 privée de ses membres par morceaux."""
    gele = engagement_v9(genre, loi, monde, L, rng)
    tirages = sp.tirer_frais(gele, monde, graine_frais, graine_noyau=graine_noyau)
    ev9 = nul_v9.evaluer_v9(gele, tirages, graine_noyau=graine_noyau)
    ev8 = nul_v9.evaluer_sur_issues(nul_v9.sans_morceaux(gele.engagement), tirages["issues"], None)
    return ev9, ev8


def verifier_monotonie(ev9, ev8, ident, r):
    """Garde : à chaque instant lu, log W(v9) ≤ log W(v8) (à 10⁻⁹ près), et pas de promotion sous v9 sans promotion sous v8."""
    ecarts = [a - b for a, b in zip(ev9["trajectoire_log_w"], ev8["trajectoire_log_w"])]
    if max(ecarts) > TOLERANCE_MONOTONIE + 1e-6 or (ev9["promue"] and not ev8["promue"]):
        raise MonotonieViolee(f"{ident} répétition {r} : log W v9 − v8 = {max(ecarts):.3g}, promue v9 {ev9['promue']}, "
                              f"v8 {ev8['promue']}")


def jouer_ligne(entropie, nom, nul, role, repetitions, debut=None, duree_max=None):
    """Une ligne : `repetitions` répétitions indépendantes. Ligne v9 : décisions sous v9 et sous v8 apparié, monotonie gardée
    à chaque répétition ; ligne v1 (artefact T01|v1) : juge v1 du banc v8."""
    ident = f"{nom}|{nul}"
    depart = time.time()
    promues = promues_v8 = perdues = 0
    maxima, maxima_v8, dominants = [], [], {}
    for r in range(repetitions):
        if debut is not None and duree_max is not None and time.time() - debut > duree_max:
            raise ArretDuree(f"{ident} : durée maximale de {duree_max} s dépassée à la répétition {r}")
        g_scenario, g_noyau, g_frais = graines(entropie, ident, r)
        rng = random.Random(g_scenario)
        genre, loi, monde, L = scenario_v9(nom, rng)
        if nul == "v1":
            ev, ev8 = v8.juger_v8(genre, loi, monde, L, "v1", rng, g_noyau, g_frais), None
        elif nul == "v9":
            ev, ev8 = juger_v9(genre, loi, monde, L, rng, g_noyau, g_frais)
            verifier_monotonie(ev, ev8, ident, r)
        else:
            raise ValueError(f"nul inconnu : {nul!r}")
        if not math.isfinite(ev["log_richesse_max"]) or (ev8 is not None and not math.isfinite(ev8["log_richesse_max"])):
            raise FloatingPointError(f"{ident} : richesse non finie à la répétition {r}")
        promues += bool(ev["promue"])
        maxima.append(ev["log_richesse_max"])
        d = ev.get("membre_dominant_final")
        dominants[d] = dominants.get(d, 0) + 1
        if ev8 is not None:
            promues_v8 += bool(ev8["promue"])
            perdues += bool(ev8["promue"]) and not ev["promue"]
            maxima_v8.append(ev8["log_richesse_max"])
    maxima.sort()
    bas, haut = v8.clopper_pearson(promues, repetitions)
    sortie = {"ligne": nom, "reglage": nul, "role": role, "promues": promues, "repetitions": repetitions,
              "taux": promues / repetitions, "clopper_pearson_95_unilaterales": [bas, haut],
              "log_w_max_mediane": round(maxima[len(maxima) // 2], 3),
              "log_w_max_99e": round(maxima[int(0.99 * (len(maxima) - 1))], 3), "log_w_max_max": maxima[-1],
              "dominants": dict(sorted(dominants.items(), key=lambda x: (-x[1], str(x[0])))[:4]),
              "duree_s": round(time.time() - depart, 1)}
    if nul == "v9":
        maxima_v8.sort()
        sortie["apparie_v8"] = {"promues": promues_v8, "taux": promues_v8 / repetitions,
                                "clopper_pearson_95_unilaterales": list(v8.clopper_pearson(promues_v8, repetitions)),
                                "perdues": perdues, "perte": perdues / repetitions,
                                "perte_clopper_pearson_95_unilaterales": list(v8.clopper_pearson(perdues, repetitions)),
                                "log_w_max_mediane": round(maxima_v8[len(maxima_v8) // 2], 3)}
    return sortie


def _executer(arguments):
    return jouer_ligne(*arguments)


def jouer_tout(taches, processus):
    """Comme le banc v8 : un processus, l'une après l'autre ; sinon un réservoir ; toute ligne en erreur arrête la course."""
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
    return sorted(f"{x['ligne']}|{x['reglage']}" for x in resultats if x["role"] == "fatale" and x["taux"] > ALPHA)


def artefacts_non_vus(resultats):
    """Artefacts requis présents dont le taux observé ne dépasse pas α : T01|v1, et M01, M02 sous le v8 apparié."""
    non_vus = [f"{x['ligne']}|{x['reglage']}" for x in resultats if x["role"] == "artefact_requis" and x["taux"] <= ALPHA]
    non_vus += [f"{x['ligne']}|v8 apparié" for x in resultats
                if x["ligne"] in ARTEFACTS_APPARIES and "apparie_v8" in x and x["apparie_v8"]["taux"] <= ALPHA]
    return sorted(non_vus)


def code_de_sortie(resultats):
    return 1 if fatales_au_dessus_de_alpha(resultats) or artefacts_non_vus(resultats) else 0


# --- lecture gelée -------------------------------------------------------------------------------------------------------------
def lire_v9(resultats, complet):
    """Lecture gelée du préenregistrement (brouillon 1, sections 5 à 7) ; `complet` : toutes les lignes du plan présentes."""
    par = {f"{x['ligne']}|{x['reglage']}": x for x in resultats}
    fatales = {c: x for c, x in par.items() if x["role"] == "fatale"}
    p_haute = {c: v8.p_valeur_exacte(x["promues"], x["repetitions"], ALPHA, "haute") for c, x in fatales.items()}
    p_basse = {c: v8.p_valeur_exacte(x["promues"], x["repetitions"], ALPHA, "basse") for c, x in fatales.items()}
    tenues, cedees = v8.holm(p_haute, NIVEAU_FAMILLE), v8.holm(p_basse, NIVEAU_FAMILLE)
    lecture = {"fatales": {c: TENUE if c in tenues else NON_TENUE if c in cedees else NON_JUGEABLE for c in sorted(fatales)},
               "fatales_valeurs_p": {c: {"H0_taux_au_moins_alpha": p_haute[c], "H0_taux_au_plus_alpha": p_basse[c]}
                                     for c in sorted(fatales)}}
    artefacts = {}
    for c, x in sorted(par.items()):
        if x["role"] == "artefact_requis":
            artefacts[c] = (x["promues"], x["repetitions"])
        if x["ligne"] in ARTEFACTS_APPARIES and "apparie_v8" in x:
            artefacts[f"{x['ligne']}|v8 apparié"] = (x["apparie_v8"]["promues"], x["repetitions"])
    lecture["artefact"] = {}
    for c, (k, n) in sorted(artefacts.items()):
        bas, haut = v8.clopper_pearson(k, n)
        lecture["artefact"][c] = TENUE if bas > ALPHA else NON_TENUE if haut < ALPHA else NON_JUGEABLE
    puissance = {x["ligne"]: x for x in resultats if x["role"] == "puissance" and "apparie_v8" in x}
    # Perte appariée d = part des répétitions promues sous v8 et non sous v9 (binomiale) : « tenue » si H0 « d ≥ marge » est
    # rejetée (test exact, Holm sur la famille des lignes de puissance) ; « non tenue » si H0 « d ≤ marge » est rejetée.
    p_haut = {n: v8.p_valeur_exacte(x["apparie_v8"]["perdues"], x["repetitions"], MARGE_PERTE, "haute") for n, x in puissance.items()}
    p_bas = {n: v8.p_valeur_exacte(x["apparie_v8"]["perdues"], x["repetitions"], MARGE_PERTE, "basse") for n, x in puissance.items()}
    tenues_p, cedees_p = v8.holm(p_haut, NIVEAU_FAMILLE), v8.holm(p_bas, NIVEAU_FAMILLE)
    lecture["perte_de_puissance"] = {n: TENUE if n in tenues_p else NON_TENUE if n in cedees_p else NON_JUGEABLE
                                     for n in sorted(puissance)}
    lecture["pertes_observees"] = {n: x["apparie_v8"]["perte"] for n, x in sorted(puissance.items())}
    lecture["puissances_observees"] = {n: {"v9": x["taux"], "v8": x["apparie_v8"]["taux"]} for n, x in sorted(puissance.items())}
    lecture["mesures"] = {c: {"taux_v9": x["taux"], "clopper_pearson_95_unilaterales": x["clopper_pearson_95_unilaterales"],
                              "taux_v8_apparie": x.get("apparie_v8", {}).get("taux")}
                          for c, x in sorted(par.items()) if x["role"] == "mesure"}
    audits = []
    for c, x in sorted(fatales.items()):
        if x["ligne"] in CLASSE_LINEAIRE + CLASSE_MORCEAUX + CLASSE_LOG_LINEAIRE and x["promues"] > 0:
            audits.append(f"A1 {c} : {x['promues']} promotion(s) sur une ligne refusée par construction — audit du code (R4)")
        if x["ligne"] in CLASSE_LINEAIRE + CLASSE_MORCEAUX and x["log_w_max_max"] > TOLERANCE_LOG_W:
            audits.append(f"A4 {c} : log W = {x['log_w_max_max']:.3g} > 0 dans une classe refusée par construction — audit du "
                          "code (R4)")
    for c, (k, n) in sorted(artefacts.items()):
        taux = k / n
        if c.startswith("T01|v1") and not AUDIT_ARTEFACT_V1[0] <= taux <= AUDIT_ARTEFACT_V1[1]:
            audits.append(f"A3 {c} : taux {taux} hors de [{AUDIT_ARTEFACT_V1[0]} ; {AUDIT_ARTEFACT_V1[1]}] — audit du banc (R4)")
        if c.endswith("v8 apparié") and taux < AUDIT_ARTEFACT_MORCEAUX_MIN:
            audits.append(f"A3 {c} : taux {taux} sous {AUDIT_ARTEFACT_MORCEAUX_MIN} (le trou du v8 se ferme sans le v9 ?) — "
                          "audit du banc (R4)")
    for c, x in sorted(fatales.items()):
        if x["ligne"] in CLASSE_MORCEAUX:
            par_morceaux = sum(v for d, v in x["dominants"].items() if str(d).startswith(nul_v9.PREFIXE_MORCEAUX))
            if par_morceaux < x["repetitions"] / 2:
                audits.append(f"A5 {c} : un membre par morceaux ne domine qu'à {par_morceaux}/{x['repetitions']} répétitions "
                              "(refus qui ne viendrait pas du nul v9 ?) — audit (R4)")
    for n, x in sorted(puissance.items()):
        if x["apparie_v8"]["taux"] - x["taux"] < 0:
            audits.append(f"A2 {n} : taux v9 au-dessus du taux v8 apparié — contraire à la monotonie, audit du code (R4)")
    lecture["audits"] = audits
    P = PREDICTIONS
    lecture["predictions"] = {
        "P1_lignes_fatales": {c: (x["taux"] <= P["P1_taux_max_T12a"] if x["ligne"] == "T12a"
                                  else x["promues"] == P["P1_promotions_par_ligne_refusee_par_construction"])
                              for c, x in sorted(fatales.items())},
        "P2_dents_morceaux_v8": {c: k / n >= P["P2_dents_morceaux_v8_min"][c.split("|")[0]] for c, (k, n) in artefacts.items()
                                 if c.endswith("v8 apparié")},
        "P3_artefact_v1": {c: P["P3_artefact_v1"][0] <= k / n <= P["P3_artefact_v1"][1] for c, (k, n) in artefacts.items()
                           if c.startswith("T01|v1")},
        "P4_perte_appariee": {n: P["P4_perte_appariee"][n][0] <= v <= P["P4_perte_appariee"][n][1]
                              for n, v in lecture["pertes_observees"].items() if n in P["P4_perte_appariee"]},
        "P5_puissance_v9": {n: P["P5_puissance_v9"][n][0] <= x["taux"] <= P["P5_puissance_v9"][n][1]
                            for n, x in sorted(puissance.items()) if n in P["P5_puissance_v9"]},
        "P6_mesurees_v9": {c: P["P6_mesurees_v9"][x["ligne"]][0] <= x["taux"] <= P["P6_mesurees_v9"][x["ligne"]][1]
                           for c, x in sorted(par.items()) if x["role"] == "mesure" and x["ligne"] in P["P6_mesurees_v9"]}}
    valeurs_art = list(lecture["artefact"].values())
    if not complet:
        issue = "partielle (plan incomplet : aucune issue)"
    elif NON_TENUE in lecture["fatales"].values():
        issue = "trou"
    elif NON_TENUE in lecture["perte_de_puissance"].values():
        issue = "puissance perdue"
    elif not valeurs_art or any(v != TENUE for v in valeurs_art):
        issue = "non concluant (banc sans dents)"
    elif all(v == TENUE for v in list(lecture["fatales"].values()) + list(lecture["perte_de_puissance"].values())):
        issue = "confirmé"
    else:
        issue = "non concluant (précision insuffisante)"
    lecture["issue"] = issue
    lecture["issue_suspendue_par_audit"] = bool(audits)
    lecture["predictions"]["P7_issue"] = issue == P["P7_issue"]
    return lecture


# --- préenregistrement ---------------------------------------------------------------------------------------------------------
def lire_preenregistrement(chemin):
    """Mode décisif : un fichier `prereg/preenregistrement-validation-nul-v9-v<N>.md`, scellé, gelant le code présent ; rend
    (entropie, empreinte, gelées)."""
    if (os.path.realpath(os.path.dirname(os.path.abspath(chemin))) != os.path.realpath(DOSSIER_PREREG)
            or not MOTIF_PREREG.match(os.path.basename(chemin))):
        raise EcartAuPlan(f"mode décisif : le préenregistrement est prereg/preenregistrement-validation-nul-v9-v<N>.md, pas {chemin}")
    if not os.path.isfile(chemin):
        raise PreenregistrementNonScelle(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(chemin):
        raise PreenregistrementNonScelle(f"préenregistrement non scellé : {chemin} — aucune course décisive avant le scellement")
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    debut, fin = texte.find(DEBUT_EMPREINTES), texte.find(FIN_EMPREINTES)
    if debut < 0 or fin < debut:
        raise EcartAuPlan("le préenregistrement ne gèle aucune empreinte du code (bloc « empreintes-du-code » absent)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", texte[debut:fin], re.M)
    manquants = sorted(set(FICHIERS_GELES) - {relatif for _, relatif in gelees})
    if not gelees or manquants:
        raise EcartAuPlan(f"code importé par la course non gelé par le préenregistrement : {manquants or 'bloc vide'}")
    ecarts = []
    for attendue, relatif in gelees:
        chemin_code = os.path.join(RACINE, relatif)
        presente = sha256_fichier(chemin_code) if os.path.isfile(chemin_code) else "absent"
        if presente != attendue:
            ecarts.append(f"{relatif} : gelé {attendue[:12]}…, présent {presente[:12]}…")
    if ecarts:
        raise EcartAuPlan("code différent du code gelé par le préenregistrement : " + " ; ".join(ecarts))
    empreinte = sha256_fichier(chemin)
    entropie = int(empreinte, 16)
    if entropie < GRAINE_EXPLORATOIRE_MAX:
        raise EcartAuPlan("entropie décisive dans l'espace des graines exploratoires (< 2⁶⁴) : refusée")
    return entropie, empreinte, {relatif: attendue for attendue, relatif in gelees}


# --- course --------------------------------------------------------------------------------------------------------------------
def selection(lignes):
    if not lignes:
        return list(LIGNES)
    noms = [n for n in lignes.split(",") if n]
    inconnus = sorted(set(noms) - {l[0] for l in LIGNES})
    if inconnus or not noms:
        raise ValueError(f"--lignes : nom(s) inconnu(s) {inconnus} ; connus : {sorted({l[0] for l in LIGNES})}")
    return [l for l in LIGNES if l[0] in noms]


def principal(argv=None):
    a = argparse.ArgumentParser(description="Banc des tricheurs sous le nul v9")
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
                  preenregistrement=preenregistrement, nul=nul_v9.description(), numpy=np.__version__,
                  code_du_banc_sha256={relatif: sha256_fichier(os.path.join(RACINE, relatif)) for relatif in FICHIERS_GELES})
    m["regle_des_graines"] = ("numpy.random.SeedSequence (R9), règle du banc v8 inchangée : entropie racine = int(empreinte "
                              "SHA-256 du préenregistrement scellé, 16) en mode décisif, --graine (< 2^64) sinon ; répétition "
                              "r de la ligne « nom|nul » : spawn_key=(4 premiers octets gros-boutistes de SHA-256(« nom|nul »), "
                              "r), spawn(3) : scénario, noyau, tirages frais ; le nul v8 apparié est évalué sur les issues de "
                              "la ligne v9 (aucune graine propre)")
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), m)
    debut = time.time()
    resultats, arret = jouer_tout([(entropie, n, nul, role, args.repetitions, debut, args.duree_max_s)
                                   for n, nul, role in lignes], args.processus)
    if arret is not None:
        rapport = {"banc": VERSION, "mode": mode, "arret": arret, "duree_s": round(time.time() - debut, 1),
                   "issue": "non concluant (arrêt) : aucun verdict, aucun taux rapporté",
                   "lignes_terminees": sorted(f"{x['ligne']}|{x['reglage']}" for x in resultats)}
        ecrire_json_scelle(os.path.join(args.dossier, "banc-tricheurs-v9.json"), rapport)
        print(json.dumps(rapport, ensure_ascii=False, indent=1), file=sys.stderr)
        return 3
    ordre = {f"{n}|{nul}": i for i, (n, nul, _) in enumerate(LIGNES)}
    resultats.sort(key=lambda x: ordre[f"{x['ligne']}|{x['reglage']}"])
    lecture = lire_v9(resultats, complet=len(resultats) == len(LIGNES))
    au_dessus, sans_dents = fatales_au_dessus_de_alpha(resultats), artefacts_non_vus(resultats)
    rapport = {"banc": VERSION, "mode": mode, "preenregistrement": preenregistrement, "repetitions": args.repetitions,
               "duree_s": round(time.time() - debut, 1), "lecture": lecture, "fatales_au_dessus_de_alpha": au_dessus,
               "artefacts_non_vus": sans_dents, "resultats": resultats}
    ecrire_json_scelle(os.path.join(args.dossier, "banc-tricheurs-v9.json"), rapport)
    print(json.dumps({"mode": mode, "issue": lecture["issue"], "fatales": lecture["fatales"], "artefact": lecture["artefact"],
                      "perte_de_puissance": lecture["perte_de_puissance"], "audits": lecture["audits"],
                      "taux": {f"{x['ligne']}|{x['reglage']}": x["taux"] for x in resultats},
                      "taux_v8_apparie": {x["ligne"]: x["apparie_v8"]["taux"] for x in resultats if "apparie_v8" in x},
                      "pertes": lecture["pertes_observees"], "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return code_de_sortie(resultats)


if __name__ == "__main__":
    sys.exit(principal())
