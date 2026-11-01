"""Nul des filles v2 — membres ajustés par maximum de vraisemblance sur les tirages frais, lus à des instants fixés d'avance.

Note de conception : `conception-nul-des-filles-v2-v1.md` (`35fe3f7f…`). Exploratoire (R-522) ; sans préenregistrement
(mot de Lazar du 27 octobre 2026, 12:02 heure de Paris). S'appuie sur le juge v1 de `../orchestrateur-pole-v2` (ordre
d'exécution secret, urne), inchangé ; numpy pour les ajustements (l'orchestrateur, lui, reste en bibliothèque standard).

Membres ajoutés au nul d'une fille de parents A et B, en plus de 𝓛 v1, des parents et des formes de v0
(`selection_pari.bibliotheque_fille`) :
- « ajuste_lineaire » : π_A·A + π_B·B + Σ_k ρ_k·δ_k (poids sur le simplexe ; δ_k, la loi certaine de l'issue k). La famille
  contient chaque parent seul, chaque parent mélangé à **toute** loi aveugle fixe, le mélange des parents et le mélange
  des parents avec une loi aveugle. Maximum par espérance-maximisation (problème concave), arrêté sur l'écart de
  Frank-Wolfe, qui borne ce qui manque au maximum ; cet écart est **ajouté** à la valeur : le dénominateur ne descend
  jamais sous le vrai maximum de la famille.
- « ajuste_log:A », « ajuste_log:B » : parent tempéré et incliné, p(k) ∝ P(k)^a·exp(β_k) (a réel, β_0 = 0).
- « ajuste_log:AB » (variante stricte, décision n° 1 de la note) : produit des parents, tempéré et incliné,
  p(k) ∝ A(k)^a·B(k)^b·exp(β_k). Logit conditionnel, concave : méthode de Newton amortie ; le décrément de Newton au carré
  est ajouté à la valeur (marge de prudence).
Lecture : aux seuls instants fixés dans l'engagement (`instants_lecture`, sous son empreinte, le dernier = n),
W_t = numérateur(t) − max(membres ordinaires à t ; membres ajustés à leur maximum sur les t premières issues de la part
d'évaluation) en logarithme. Validité : si la loi vraie est dans une famille du nul, ce maximum la domine à chaque instant
de lecture ; W reste sous un rapport de vraisemblance, martingale positive d'espérance 1 ; Ville vaut pour la suite des
instants de lecture. Règle de marge des filles (v0) : les membres ajustés comptent parmi les enveloppes.
"""

import copy
import math

import numpy as np  # requis pour les membres ajustés (numpy ≥ 1.25)

from . import selection_pari as sp
from .outils import empreinte_objet

TYPES_AJUSTES = ("ajuste_lineaire", "ajuste_log")
INSTANTS_PAR_DEFAUT = (25, 50, 75, 100, 125, 150, 175, 200)
TOLERANCE_EM, ITERATIONS_EM = 1e-5, 20000
ITERATIONS_NEWTON, BORNE_PARAMETRES = 60, 60.0
# v7, version 6 : marge de Newton admise seulement près de l'optimum (décrément² ≤ 0,25, où il borne l'écart à l'optimum
# d'une fonction autoconcordante) ; au-delà — données séparables en début de lecture, maximum à l'infini — on prend la
# borne triviale 0 (une log-vraisemblance est toujours ≤ 0), et l'instant suivant repart du point de départ par défaut.
# Défaut trouvé par un essai sur banque (instances choisies par divergence) : une valeur de 5·10⁹ au premier instant de
# lecture, propagée aux suivants par le départ à chaud, éliminait la loi exacte du monde.
DECREMENT_ADMIS = 0.25
VARIANTES = {
    "v2": {"lineaire": True, "logarithmique": True, "strict": True},
    "v2_souple": {"lineaire": True, "logarithmique": True, "strict": False},
    "v2_sans_log": {"lineaire": True, "logarithmique": False, "strict": False},
    "v2_sans_lineaire": {"lineaire": False, "logarithmique": True, "strict": True},
    "v1": None,
}


class InstantsInvalides(ValueError):
    """Instants de lecture absents, non croissants, hors de la part d'évaluation, ou sans l'instant final."""


def membres_ajustes(lois_parents, lineaire=True, logarithmique=True, strict=True):
    noms = sorted(lois_parents)
    membres = []
    if lineaire:
        membres.append({"nom": "ajuste_lineaire", "type": "ajuste_lineaire", "lois": [lois_parents[n] for n in noms],
                        "enveloppe": True})
    if logarithmique:
        for n in noms:
            membres.append({"nom": f"ajuste_log:{n}", "type": "ajuste_log", "lois": [lois_parents[n]], "enveloppe": True})
        if strict and len(noms) == 2:
            membres.append({"nom": "ajuste_log:" + "".join(noms), "type": "ajuste_log",
                            "lois": [lois_parents[n] for n in noms], "enveloppe": True})
    return membres


def membres_de_variante(variante, lois_parents):
    options = VARIANTES[variante]
    return [] if options is None else membres_ajustes(lois_parents, **options)


def construire_engagement_v2(identifiant, loi, instances, nombre_issues, alpha, bibliotheque, part_calibrage=0,
                             delta0=None, instants=INSTANTS_PAR_DEFAUT, plan_execution="ordre_secret"):
    """Engagement du juge v1 (ordre secret), avec les instants de lecture sous l'empreinte."""
    e = sp.construire_engagement(identifiant, loi, instances, nombre_issues, alpha, bibliotheque, "continu",
                                 part_calibrage=part_calibrage, delta0=delta0, plan_execution=plan_execution)
    n = len(instances) - part_calibrage
    instants = list(instants)
    if (not instants or any(not isinstance(t, int) or isinstance(t, bool) for t in instants)
            or instants != sorted(set(instants)) or instants[0] < 1 or instants[-1] != n):
        raise InstantsInvalides(f"instants de lecture strictement croissants dans [1 ; {n}], le dernier égal à {n}")
    e["instants_lecture"] = instants
    return e


# --- ajustements -----------------------------------------------------------------------------------------------------
def _lineaire(G, w0=None):
    """max_w Σ_s log(G_s·w) sur le simplexe ; rend (valeur + écart de Frank-Wolfe, w, écart)."""
    t, J = G.shape
    w = np.full(J, 1.0 / J) if w0 is None else np.maximum(w0, 1e-6) / np.maximum(w0, 1e-6).sum()
    ecart = math.inf
    for _ in range(ITERATIONS_EM):
        m = G @ w
        grad = G.T @ (1.0 / m)
        ecart = float(grad.max() - t)
        if ecart < TOLERANCE_EM:
            break
        w = w * grad / t
        w /= w.sum()
    m = G @ w
    grad = G.T @ (1.0 / m)
    ecart = max(0.0, float(grad.max() - t))
    # L'écart de Frank-Wolfe borne l'écart à l'optimum (problème concave) ; une log-vraisemblance reste ≤ 0 (v7, version 6).
    return min(0.0, float(np.log(m).sum()) + ecart), w, ecart


def _logit(X, y, theta0):
    """max_θ Σ_s [θ·X[s, y_s] − log Σ_k exp(θ·X[s, k])] ; X : (t, K, p). Newton amorti ; rend (valeur + décrément², θ)."""
    t, K, p = X.shape
    idx = np.arange(t)

    def valeur(theta):
        sc = X @ theta
        mx = sc.max(axis=1, keepdims=True)
        lse = (mx[:, 0] + np.log(np.exp(sc - mx).sum(axis=1)))
        return float((sc[idx, y] - lse).sum()), sc, mx

    theta = np.array(theta0, dtype=float)
    f, sc, mx = valeur(theta)
    decrement = math.inf
    for _ in range(ITERATIONS_NEWTON):
        pr = np.exp(sc - mx)
        pr /= pr.sum(axis=1, keepdims=True)
        moy = np.einsum("sk,skp->sp", pr, X)
        g = (X[idx, y] - moy).sum(axis=0)
        centre = X - moy[:, None, :]
        H = -np.einsum("sk,skp,skq->pq", pr, centre, centre) - 1e-9 * np.eye(p)
        try:
            pas = np.linalg.solve(H, -g)
        except np.linalg.LinAlgError:
            pas = np.linalg.lstsq(H, -g, rcond=None)[0]
        decrement = float(max(0.0, g @ pas))  # λ² = gᵀ(−H)⁻¹g, positif à une montée
        if decrement < 1e-12:
            break
        u = 1.0
        while u > 1e-8:
            essai = np.clip(theta + u * pas, -BORNE_PARAMETRES, BORNE_PARAMETRES)
            f2, sc2, mx2 = valeur(essai)
            if f2 >= f + 1e-4 * u * float(g @ pas) or f2 > f:
                break
            u *= 0.5
        if u <= 1e-8:
            break
        theta, f, sc, mx = essai, f2, sc2, mx2
    if decrement <= DECREMENT_ADMIS:
        return min(0.0, f + decrement), theta, True
    return 0.0, theta, False


def valeurs_ajustees(membre, cache, issues, nombre_issues, instants):
    """Valeur maximale (log-vraisemblance, plus la marge d'optimisation) du membre ajusté à chaque instant de lecture."""
    y = np.array(issues, dtype=int)
    tables = [np.array(cache.probas(l), dtype=float) for l in membre["lois"]]  # (n, K) chacune
    n, K = tables[0].shape
    sortie = {}
    if membre["type"] == "ajuste_lineaire":
        F = np.stack([tab[np.arange(n), y] for tab in tables], axis=1)  # (n, J)
        D = np.zeros((n, K))
        D[np.arange(n), y] = 1.0
        G_tout = np.concatenate([F, D], axis=1)
        w = None
        for t in instants:
            v, w, _ = _lineaire(G_tout[:t], w)
            sortie[t] = v
        return sortie
    if membre["type"] == "ajuste_log":
        J = len(tables)
        logs = np.stack([np.log(np.maximum(tab, sp.PLANCHER)) for tab in tables], axis=2)  # (n, K, J)
        indic = np.zeros((n, K, K - 1))
        for k in range(1, K):
            indic[:, k, k - 1] = 1.0
        X_tout = np.concatenate([logs, indic], axis=2)
        # Problème concave : un seul départ suffit (le parent lui-même, ou la moyenne des parents ; puis l'ajustement
        # de l'instant de lecture précédent).
        depart = np.concatenate([np.full(J, 1.0 / J), np.zeros(K - 1)])
        theta = depart
        for t in instants:
            sortie[t], theta, converge = _logit(X_tout[:t], y[:t], theta)
            if not converge:
                theta = depart  # jamais de départ à chaud depuis un ajustement qui n'a pas convergé
        return sortie
    raise sp.LoiInvalide(f"membre ajusté inconnu : {membre['type']!r}")


# --- évaluation --------------------------------------------------------------------------------------------------------
def evaluer_v2(gele, tirages, graine_noyau=None):
    """Comme `selection_pari.evaluer` (mêmes gardes), avec les membres ajustés et la lecture aux instants fixés."""
    if empreinte_objet(gele.engagement) != gele.empreinte:
        raise sp.EngagementModifie("le test a changé depuis son gel")
    if not isinstance(tirages, dict) or tirages.get("empreinte_engagement") != gele.empreinte:
        raise sp.TiragesNonLies("tirages sans lien avec l'empreinte de cet engagement")
    sp.verifier_plan_execution(gele, tirages, graine_noyau)
    e = gele.engagement
    instants = e.get("instants_lecture")
    k, instances, issues = e["nombre_issues"], e["instances"], tirages.get("issues")
    if not isinstance(issues, list) or len(issues) != len(instances) or not all(
            isinstance(x, int) and not isinstance(x, bool) and 0 <= x < k for x in issues):
        raise sp.TiragesNonLies("issues absentes, mal formées ou en nombre différent du plan gelé")
    c = e.get("part_calibrage", 0)
    n = len(instances) - c
    if not instants or instants[-1] != n or instants != sorted(set(instants)) or instants[0] < 1:
        raise InstantsInvalides("instants de lecture absents ou non conformes dans l'engagement")
    bibliotheque = sp.calibrer(e["bibliotheque"], issues[:c], instances[:c])
    ordinaires = [m for m in bibliotheque if m["type"] not in TYPES_AJUSTES]
    ajustes = [m for m in bibliotheque if m["type"] in TYPES_AJUSTES]
    issues, instances = issues[c:], instances[c:]
    cache = sp.Cache(issues, instances)
    numerateur = sp.trajectoire_numerateur(e, issues, instances, cache)
    par_membre = sp.trajectoires(ordinaires, issues, instances, k, cache)
    par_ajuste = {m["nom"]: valeurs_ajustees(m, cache, issues, k, instants) for m in ajustes}
    log_w, dominants = [], []
    for t in instants:
        candidats = [(traj[t - 1], nom) for nom, traj in par_membre.items()] + [(v[t], nom) for nom, v in par_ajuste.items()]
        meilleur, nom = max(candidats, key=lambda c: (c[0], c[1]))
        log_w.append(numerateur[t - 1] - meilleur)
        dominants.append(nom)
    seuil = math.log(1.0 / e["alpha"])
    i_promotion = next((i for i, v in enumerate(log_w) if v >= seuil), None)
    promue = i_promotion is not None
    resultat = {"log_richesse_finale": log_w[-1], "log_richesse_max": max(log_w), "seuil_log": seuil,
                "log_richesse_arretee": log_w[i_promotion] if promue else log_w[-1],
                "trajectoire_log_w": [round(v, 6) for v in log_w],  # v7 : aux instants de lecture (règle e-BH)
                "t_promotion": instants[i_promotion] if promue else None, "instants_lecture": list(instants),
                "nombre_tirages": n, "part_calibrage": c, "membre_dominant_final": dominants[-1],
                "plan_execution": sp.plan_execution_de(e), "empreinte_engagement": gele.empreinte}
    enveloppes = {m["nom"]: par_membre[m["nom"]][-1] for m in ordinaires if m.get("enveloppe")}
    enveloppes.update({nom: v[n] for nom, v in par_ajuste.items()})
    if e.get("delta0") is not None and enveloppes:
        meilleure = max(enveloppes, key=lambda nom: (enveloppes[nom], nom))
        gain = (numerateur[-1] - enveloppes[meilleure]) / n
        resultat.update(meilleure_enveloppe=meilleure, gain_moyen_sur_meilleure_enveloppe=gain,
                        marge_requise=2 * e["delta0"], marge_atteinte=gain >= 2 * e["delta0"])
        promue = promue and gain >= 2 * e["delta0"]
    resultat["promue"] = promue
    if not promue:
        resultat["t_promotion"] = None
    return resultat


def copie_engagement(gele):
    return copy.deepcopy(gele.engagement)
