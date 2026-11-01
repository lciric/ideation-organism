"""Pari apparié borné (v7, versions 20 à 41) — le second type d'engagement du pôle, pour les affirmations globales (H1, H2, H3,
G1), selon la conception v5 (`../../pari-de-signe/conception-pari-de-signe-v5.md` et les versions qu'elle amende).

Ce module ne contient que le **cœur statistique**, sans lien encore avec le cycle des générations (à faire : monde sur
banque de scores, engagement, mémoire avec la clé complète de l'héritage) :

- un **contraste** v(t) = a₀ + Σ a_c·r_c(t) sur des parts r_c ∈ [0 ; 1], borné dans [−1 ; 1] par la **règle double**
  (somme des coefficients positifs plus la constante ≤ 1 ; somme des valeurs absolues des négatifs moins la constante ≤ 1) ;
- la **richesse** en forme « parts » seule : W_n = moyenne sur Λ de Π (1 + λ·v(t)), surmartingale positive sous
  « E[v] ≤ 0, unités indépendantes et de même loi » (inégalité de Ville) ; la forme « signe » n'existe pas ici ;
- la **garde** appariée sur les faux positifs : processus de 1 + λ·(δ − g(t)) contre « E[g] ≥ δ » ;
- l'**e-valeur de la fiche** = minimum des processus (contraste contre chaque comparateur — intersection-union — et
  garde), **arrêtée** au premier instant où elle atteint le seuil (m_g/α_g pour la règle e-BH de la génération) ;
- la variante **sans remise** (banque entière) ;
- une **borne basse** de confiance à tout instant pour E[v] (rapport), par inversion des paris sur une grille de θ ;
- (version 21, conception v6) la **règle de l'héritage** D-S25 bis : budget d'entrée α_c/m_c gardé à vie, une lecture
  e-BH **pondérée** par fin de génération sur toutes les fiches entrées (valeurs gelées pour les abandonnées et les
  promues), promotion une seule fois, arrêt à m_c/α_c, garantie sur l'union des promotions (`ebh_pondere`, `Course`) ;
- (version 21) le **plafond** de D-S27 : v′ = (min(m_t, m_max)/m_max)·v (`ponderation_plafonnee`, `contraste_plafonne`) ;
- (version 28, contre-lecture de la conception v9) : fraîcheur des unités **par rapport à toute la course** (K9-1 : une
  unité n'est lue qu'à la génération de sa première lecture, par quelque fiche que ce soit) ; lien fiche ↔ clé tenu par la
  course (K9-2) ; journal des parties reçu par la course et confronté à la lecture (K9-6) ; déclaration « sans partie »
  refusée pour une fiche gelée ou qui a sa partie (K9-10 c) ; plusieurs gardes (une par comparateur, K9-9) dans `evaluer` ;
- (version 29, contre-lecture de la conception v10) : **gardes obligatoires** — une `Course` sans journal, ou une entrée sans
  clés, est refusée sauf `essai=True` (K10-7) ; une partie **vide** (journalisée vide par celui qui calcule) vaut déclaration
  « sans partie » acceptée (K10-5) ; la génération courante est fournie par la course à qui calcule (`generation`), jamais
  par l'appelant (K10-4) ; la lecture d'une génération entière se fait par `engagement_apparie.jouer_generation`, qui ne rend
  aucune trajectoire à l'orchestrateur (K10-1, K10-2) ;
- (version 30, contre-lecture de la conception v11, K11-1 à K11-7) : la trajectoire ajoutée doit porter l'**empreinte** que le
  journal a enregistrée (trajectoire fabriquée refusée) et la **clé** que le journal a enregistrée (clé déclarée par l'appelant
  ignorée) ; un abandon « avant partie » est refusé si la partie est au journal ; à la lecture, toute unité **journalisée**
  dans la génération est enregistrée comme lue (une partie calculée et non ajoutée ne laisse pas ses unités « fraîches »), et
  une entrée du journal pour une fiche inconnue de la course (**fiche fantôme**) ou une génération autre que la courante est
  refusée ; la génération ne peut être lue qu'une fois toutes les entrées du journal confrontées ;
- (version 40, relecture CL6 de session-depot, CL39-09) : **valeurs non finies refusées à chaque entrée** — `_fini(x)` (nombre
  réel fini, ni booléen) et un refus nommé `ContrasteInvalide` (sous-classe de `ValueError`) pour la constante
  (`verifier_coefficients`, `contraste`), les coefficients et la valeur v avant la borne (`contraste`, `contraste_plafonne`),
  les log e-valeurs et les budgets (`ebh_pondere`), la trajectoire (`Course.ajouter_trajectoire`, avant tout changement
  d'état), les valeurs dans [−1 ; 1] (`trajectoire_log_sans_remise`, `borne_basse`, avec α de `borne_basse`) et α, m
  (`evaluer`). Avant : un NaN ou un ±∞ devenait la valeur la plus favorable (v = +1 par le jeu de min/max), dérangeait le tri
  de l'e-BH, ou laissait un seuil NaN (jamais promue, sans erreur). La statistique est inchangée sur les entrées finies
  valides ;
- (version 41, relecture CL7 de session-depot, CL40-06) : **un seul prédicat** `_fini` partout (coefficients de
  `verifier_coefficients`, écarts de la garde : un entier de numpy y est désormais admis comme dans `contraste`) ; α de
  `ebh_pondere` exigé fini dans ]0 ; 1[ (NaN, +∞ ou `True` désarmaient la garde de la somme des budgets) ; chaque valeur
  de `trajectoire_log_richesse` passe `_exiger_valeur` et chaque part de cellule de `contraste` `_exiger_fini` (`True`
  y valait 1) ; `ponderation_plafonnee` refuse un booléen.

Tout est en Python pur (aucune dépendance) ; les instants de lecture sont les unités (une unité = un instant).
"""

import math
import numbers

LAMBDAS = (0.1, 0.3, 0.6, 0.9)


class ContrasteInvalide(ValueError):
    pass


def _fini(x):
    """Vrai si x est un nombre réel fini qui n'est pas un booléen (version 40, CL39-09). `numbers.Real` admet les flottants
    et entiers de numpy ; NaN, ±∞, booléens, chaînes, None et entiers trop grands pour un flottant sont refusés."""
    if not isinstance(x, numbers.Real) or isinstance(x, bool):
        return False
    try:
        return math.isfinite(x)
    except OverflowError:
        return False


def _exiger_fini(x, quoi):
    if not _fini(x):
        raise ContrasteInvalide(f"{quoi} : nombre réel fini attendu (ni NaN, ni ±∞, ni booléen) : {x!r}")
    return x


def _exiger_valeur(v, quoi):
    """Valeur de contraste : réel fini dans [−1 ; 1] (version 40)."""
    _exiger_fini(v, quoi)
    if not -1.0 <= v <= 1.0:
        raise ContrasteInvalide(f"{quoi} : valeur hors de [−1 ; 1] : {v!r}")
    return v


def verifier_coefficients(coefficients, constante=0.0):
    """Règle double (conception v2, constat C11 de sa contre-lecture) : v ∈ [−1 ; 1] pour toutes parts dans [0 ; 1]."""
    if not coefficients:
        raise ContrasteInvalide("contraste sans cellule")
    _exiger_fini(constante, "constante du contraste")  # v40 : une constante NaN passait la règle double (comparaisons fausses)
    for cellule, a in coefficients.items():
        if not _fini(a):  # v41 (CL40-06) : le même prédicat que `contraste` (un entier de numpy est admis des deux côtés)
            raise ContrasteInvalide(f"coefficient non numérique ou non fini pour {cellule!r} : {a!r}")
    positifs = sum(a for a in coefficients.values() if a > 0)
    negatifs = sum(-a for a in coefficients.values() if a < 0)
    if positifs + constante > 1 + 1e-12 or negatifs - constante > 1 + 1e-12:
        raise ContrasteInvalide(f"règle double violée : positifs + constante = {positifs + constante:.6g}, "
                                f"négatifs − constante = {negatifs - constante:.6g} (chacun ≤ 1)")
    return True


def contraste(parts, coefficients, constante=0.0):
    """v = a₀ + Σ a_c·r_c pour une unité ; `parts` : cellule → part dans [0 ; 1].

    Version 40 (CL39-09) : constante, coefficients et v avant la borne doivent être des réels finis ; sinon refus
    (`ContrasteInvalide`). Avant, min(1, NaN) rendait 1 : un NaN ou un +∞ donnait v = +1, la valeur la plus favorable."""
    v = _exiger_fini(constante, "constante du contraste")
    for cellule, a in coefficients.items():
        _exiger_fini(a, f"coefficient de {cellule!r}")
        r = _exiger_fini(parts[cellule], f"part de {cellule!r}")  # v41 (CL40-06) : `True` valait 1
        if not 0.0 <= r <= 1.0:
            raise ContrasteInvalide(f"part hors de [0 ; 1] pour {cellule!r} : {r}")
        v += a * r
    _exiger_fini(v, "contraste avant la borne")
    return max(-1.0, min(1.0, v))


def _verifier_lambdas(lambdas):
    if not lambdas or any(not 0.0 < l < 1.0 for l in lambdas):
        raise ValueError("Λ : mises dans ]0 ; 1[")


def trajectoire_log_richesse(valeurs, lambdas=LAMBDAS):
    """log de la richesse mélangée (moyenne sur Λ de Π (1 + λ·v)) après chaque unité ; v dans [−1 ; 1]."""
    _verifier_lambdas(lambdas)
    logs = [0.0] * len(lambdas)
    sortie = []
    for i, v in enumerate(valeurs):
        _exiger_valeur(v, f"richesse, unité {i}")  # v41 (CL40-06) : `True` valait 1, None levait TypeError
        logs = [lw + math.log1p(l * v) for lw, l in zip(logs, lambdas)]
        m = max(logs)
        sortie.append(m + math.log(sum(math.exp(lw - m) for lw in logs) / len(lambdas)))
    return sortie


def trajectoire_log_garde(ecarts_faux_positifs, delta, lambdas=LAMBDAS):
    """Garde appariée : processus de 1 + λ·(δ − g) contre « E[g] ≥ δ » (A tire plus que B d'au moins δ)."""
    if not 0.0 < delta < 1.0:
        raise ValueError("δ dans ]0 ; 1[")
    # v39 : un écart non fini (NaN, ±∞) devenait +1 par le jeu de min/max, la valeur la plus favorable à la promotion
    # (défaut relevé par le sous-agent de la porte PACE, 29 octobre) ; refus explicite
    for g in ecarts_faux_positifs:
        if not _fini(g):  # v41 (CL40-06) : un seul prédicat
            raise ContrasteInvalide(f"écart de faux positifs non fini ou non numérique : {g!r}")
    return trajectoire_log_richesse([max(-1.0, min(1.0, delta - g)) for g in ecarts_faux_positifs], lambdas)


def trajectoire_log_sans_remise(valeurs, lambdas=LAMBDAS):
    """Variante « banque entière » : facteur 1 + λ_t·(v(t) − μ_t), μ_t = −(Σ passé)/(n − t + 1), λ_t ≤ λ·(n − t + 1)/n ;
    nul « moyenne des v de la banque ≤ 0 », l'ordre de lecture étant tiré uniformément (ordre secret du noyau).
    Version 40 : chaque v est un réel fini dans [−1 ; 1], vérifié avant toute lecture (un NaN donnait −690 par le plancher
    1e-300 puis empoisonnait la moyenne ; +∞ donnait NaN ; 5,0 était accepté)."""
    _verifier_lambdas(lambdas)
    valeurs = list(valeurs)
    for i, v in enumerate(valeurs):
        _exiger_valeur(v, f"sans remise, unité {i}")
    n = len(valeurs)
    logs = [0.0] * len(lambdas)
    somme, sortie = 0.0, []
    for t, v in enumerate(valeurs, 1):
        mu = -somme / (n - t + 1)
        for i, l in enumerate(lambdas):
            lt = l * (n - t + 1) / n
            logs[i] += math.log(max(1e-300, 1.0 + lt * (v - mu)))
        somme += v
        m = max(logs)
        sortie.append(m + math.log(sum(math.exp(lw - m) for lw in logs) / len(lambdas)))
    return sortie


E_PROCESSUS = {"combinaison": "moyenne sur Λ", "arret": "premier franchissement de log(m/α) ou de −log b_i", "module": "pari_apparie",
               "version": 28}


def evaluer(contrastes_par_comparateur, ecarts_faux_positifs=None, delta=None, alpha=0.05, m=1, lambdas=LAMBDAS):
    """E-valeur d'une fiche appariée.

    `contrastes_par_comparateur` : {comparateur: [v(t) par unité]} — l'affirmation « bat chaque comparateur »
    (intersection-union : promotion si **tous** les processus atteignent le seuil ; sous le nul « il existe un comparateur
    k avec E[v_k] ≤ 0 », le minimum est dominé par la surmartingale de ce k : niveau α sans correction de multiplicité).
    `ecarts_faux_positifs` et `delta` : la garde (facultative) ; elle entre dans le minimum. Version 28 (K9-9) : plusieurs
    gardes, une par comparateur, en passant un dictionnaire {nom: [g(t)]} et `delta` (commun) ou {nom: δ} ; le minimum porte
    sur tous les contrastes et toutes les gardes.
    Les suites sont lues en parallèle, unité par unité (même ordre, même longueur pour les contrastes ; la garde peut avoir
    sa propre longueur : ses unités sont les unités honnêtes, révélées dans le même ordre secret).
    Le processus est **arrêté** au premier instant où le minimum atteint log(m/α) (temps d'arrêt : e-valeur valide sous la
    règle e-BH au niveau α avec m fiches). Version 21 (conception v6, K5-3) : m et α sont ceux de la famille **nouvelle**
    de la génération (m_g, α_g) ; pour une fiche **relancée**, passer par `Course`, qui multiplie la valeur héritée et
    arrête au seuil d'entrée 1/b_i = m_c/α_c, gardé à vie."""
    if not contrastes_par_comparateur:
        raise ValueError("au moins un comparateur")
    # v40 (CL39-09) : α ou m NaN donnait un seuil NaN, jamais franchi, sans erreur
    if not _fini(alpha) or not 0.0 < alpha < 1.0:
        raise ContrasteInvalide(f"α : réel fini dans ]0 ; 1[ : {alpha!r}")
    if not _fini(m) or m < 1:
        raise ContrasteInvalide(f"m : réel fini ≥ 1 : {m!r}")
    longueurs = {len(v) for v in contrastes_par_comparateur.values()}
    if len(longueurs) != 1:
        raise ValueError("les contrastes des comparateurs doivent porter sur les mêmes unités")
    seuil = math.log(m / alpha)
    trajs = {k: trajectoire_log_richesse(v, lambdas) for k, v in contrastes_par_comparateur.items()}
    gardes = {}
    if ecarts_faux_positifs is not None:
        if delta is None:
            raise ValueError("garde sans δ")
        if isinstance(ecarts_faux_positifs, dict):
            for nom, g in ecarts_faux_positifs.items():
                d = delta[nom] if isinstance(delta, dict) else delta
                gardes[nom] = trajectoire_log_garde(g, d, lambdas)
        else:
            gardes["garde"] = trajectoire_log_garde(ecarts_faux_positifs, delta, lambdas)
    garde = gardes.get("garde") if len(gardes) == 1 and "garde" in gardes else None
    n = longueurs.pop()
    n_total = max([n] + [len(g) for g in gardes.values()])
    minimum, arret = [], None
    for t in range(n_total):
        valeurs = [traj[min(t, n - 1)] if n else 0.0 for traj in trajs.values()]
        for g in gardes.values():
            valeurs.append(g[min(t, len(g) - 1)] if g else 0.0)
        mt = min(valeurs)
        minimum.append(mt)
        if arret is None and mt >= seuil:
            arret = t + 1
    log_e = minimum[arret - 1] if arret else (minimum[-1] if minimum else 0.0)
    return {"trajectoire_log_min": minimum, "seuil_log": seuil, "promue": arret is not None, "instant_d_arret": arret,
            "log_e_valeur": log_e, "log_richesse_finale_par_comparateur": {k: (v[-1] if v else 0.0) for k, v in trajs.items()},
            "log_garde_finale": (garde[-1] if garde else None),
            "log_gardes_finales": {nom: (g[-1] if g else None) for nom, g in gardes.items()}, "unites": n}


def borne_basse(valeurs, alpha=0.05, lambdas=LAMBDAS, pas=0.01):
    """Borne basse de confiance, valide à tout instant, pour E[v] (v dans [−1 ; 1]) : le plus grand θ de la grille dont le
    nul « E[v] ≤ θ » est rejeté (richesse de 1 + λ_θ·(v − θ) ≥ 1/α à un instant), avec λ_θ = λ/(1 + θ) pour garder le
    facteur positif. Rapportée, jamais une condition de promotion à elle seule.
    Version 40 : chaque v est un réel fini dans [−1 ; 1] et α un réel fini dans ]0 ; 1[, sinon refus (un NaN donnait
    −0,98, une valeur 5,0 donnait 0,99, la borne la plus favorable)."""
    _verifier_lambdas(lambdas)
    if not _fini(alpha) or not 0.0 < alpha < 1.0:
        raise ContrasteInvalide(f"borne basse : α réel fini dans ]0 ; 1[ : {alpha!r}")
    valeurs = list(valeurs)
    for i, v in enumerate(valeurs):
        _exiger_valeur(v, f"borne basse, unité {i}")
    seuil = math.log(1 / alpha)
    meilleur = -1.0
    theta = -1.0 + pas
    while theta < 1.0 - 1e-9:
        logs = [0.0] * len(lambdas)
        rejete = False
        for v in valeurs:
            for i, l in enumerate(lambdas):
                logs[i] += math.log1p((l / (1.0 + theta)) * (v - theta))
            m = max(logs)
            if m + math.log(sum(math.exp(lw - m) for lw in logs) / len(lambdas)) >= seuil:
                rejete = True
                break
        if rejete:
            meilleur = theta
        else:
            break  # le nul E[v] ≤ θ n'est pas rejeté : aucun θ plus grand ne le sera (monotonie en θ)
        theta = round(theta + pas, 10)
    return meilleur


# --- Version 21 (conception v6) : plafond de D-S27 ---------------------------------------------------------------------

def ponderation_plafonnee(m_t, m_max):
    """Poids min(m_t, m_max)/m_max d'une unité de m_t épisodes (D-S27 réécrite) ; estimande « rappel par épisode
    plafonné à m_max ». Pour G1, m_max = maximum de la banque gelée : rien n'est plafonné."""
    if not (isinstance(m_t, int) and isinstance(m_max, int)) or isinstance(m_t, bool) or isinstance(m_max, bool) \
            or m_t < 0 or m_max < 1:  # v41 : un booléen n'est pas un nombre d'épisodes
        raise ValueError("m_t entier ≥ 0, m_max entier ≥ 1")
    return min(m_t, m_max) / m_max


def contraste_plafonne(parts, coefficients, constante, m_t, m_max):
    """v′ = (min(m_t, m_max)/m_max)·v, v calculé sur **tous** les épisodes de l'unité ; reste dans [−1 ; 1]."""
    return ponderation_plafonnee(m_t, m_max) * contraste(parts, coefficients, constante)


# --- Version 21 (conception v6) : règle de l'héritage D-S25 bis ---------------------------------------------------------

def ebh_pondere(log_e, budgets, alpha=None):
    """Règle e-BH pondérée : `log_e` et `budgets` indexés par fiche ; tri par b_i·E_i décroissant, k* le plus grand k
    tel que la k-ième valeur atteigne 1/k ; renvoie l'ensemble des k* premières (les ex æquo au bord y sont tous). Avec
    b_i = α/m pour toutes, c'est la règle e-BH ordinaire. Refuse des budgets dont la somme dépasse α si `alpha` est
    donné, 1 sinon (version 24, K6-5 : la somme ≤ α se contrôle aussi à l'entrée, `Course.entrer`)."""
    if set(log_e) != set(budgets):
        raise ValueError("mêmes fiches pour les e-valeurs et les budgets")
    # v40 (CL39-09) : une log e-valeur NaN dérangeait le tri ([0 ; NaN ; 3,0] → trois retenues au lieu d'aucune)
    for i, x in log_e.items():
        _exiger_fini(x, f"e-BH : log e-valeur de {i!r}")
    for i, b in budgets.items():
        _exiger_fini(b, f"e-BH : budget de {i!r}")
    if alpha is not None:  # v41 (CL40-06) : α NaN, +∞ ou True désarmait la garde de la somme des budgets
        _exiger_fini(alpha, "e-BH : α")
        if not 0.0 < alpha < 1.0:
            raise ContrasteInvalide(f"e-BH : α dans ]0 ; 1[ : {alpha!r}")
    plafond = 1.0 if alpha is None else alpha
    if any(not (b > 0) for b in budgets.values()) or sum(budgets.values()) > plafond + 1e-12:
        raise ValueError(f"budgets positifs, de somme ≤ {plafond}")
    scores = sorted(((math.log(budgets[i]) + log_e[i], i) for i in log_e), key=lambda x: (-x[0], str(x[1])))
    k_etoile = 0
    for k, (s_, _) in enumerate(scores, 1):
        if s_ >= -math.log(k) - 1e-12:
            k_etoile = k
    return {i for _, i in scores[:k_etoile]}


def _empreinte_trajectoire(trajectoire_log):
    """Empreinte d'une trajectoire (valeurs arrondies à 1e-12), partagée par le journal et la course (K11-3)."""
    import hashlib
    return hashlib.sha256(",".join(f"{float(v):.12e}" for v in trajectoire_log).encode()).hexdigest()


class Course:
    """Une course de l'organisme sous D-S25 bis (conception v6), avec les corrections de la conception v7 (K6-1, K6-2).

    - `entrer(famille, fiches, alpha_c)` : chaque fiche reçoit le budget α_c/m_c (m_c = taille de la famille, fixée
      à l'entrée), **gardé à vie** ; plusieurs familles d'une même génération se partagent α_g ; la somme des α_c sur
      les familles entrées ne doit pas dépasser α (refus sinon) — **tenue par le code au total, par l'orchestrateur
      génération par génération** (la suite de dépense D-S24, K7-9).
    - `ajouter_trajectoire(fiche, trajectoire_log)` : **une** partie par fiche et par génération ; la trajectoire (log,
      unité par unité) est multipliée à la valeur héritée et **arrêtée** au premier instant où le produit atteint
      1/b_i = m_c/α_c ; une partie pour une fiche **gelée** est refusée (erreur, jamais ignorée en silence).
    - `abandonner(fiche, trajectoire_log=None, avant_partie=False)` : **contrat de D-S25 bis (2)** — la valeur gelée est
      celle d'après la dernière partie observée avant la décision : on passe la partie de la génération courante (elle
      est ajoutée puis la fiche gelée), ou elle a déjà été ajoutée, ou l'on déclare `avant_partie=True` (la décision n'a
      vu aucune issue de la génération courante) ; sinon refus.
    - `lire(sans_partie=None)` : **une** lecture e-BH pondérée par génération sur toutes les fiches entrées non exclues ;
      les promues le restent (promotion une seule fois) ; ferme la génération ; renvoie les nouvelles promotions.
      Version 25 (K7-1) : **refus** tant qu'une fiche active (ni gelée, ni arrêtée, ni promue, ni exclue) n'a ni partie
      dans la génération ni déclaration `sans_partie[fiche] = motif` (tracée) — une partie calculée et sautée ne passe
      plus en silence ; ce que le code ne voit pas reste à l'orchestrateur : **toute partie calculée par le monde est
      ajoutée avant toute lecture ou décision**.
    - `ajouter_trajectoire(..., unites=…)` (K7-2, K8-1 ; version 26) : les **identifiants** des unités lues (banque, partie,
      unité) sont obligatoires ; toute **intersection** avec les unités déjà lues par la fiche est refusée (fraîcheur, et
      non seulement répétition exacte) ; une partie sans identité n'est acceptée qu'avec `sans_identite=True`, tracée
      (`parties_sans_identite`) — jamais en silence. La disjonction **entre fiches** d'une même lignée de clé reste à la
      mémoire (hors de cette classe).
    - `retirer(fiche, motif)` (D-S26 bis, panne confirmée) : la fiche est marquée, gelée et **exclue** des lectures
      suivantes ; si elle était promue, elle reste dans `promues` — **l'union garantie est celle d'avant les retraits** —
      et sort de `promues_rapportees()`, qui porte la réserve de D-S26 bis.
    - `bonferroni()` : pour ce qui sort du pôle, les fiches dont l'e-processus atteint 1/b_i (seuil jamais abaissé).
    - Version 28 (contre-lecture de la conception v9) : **fraîcheur par rapport à la course** (K9-1) — `premiere_lecture`
      : unité → génération de sa première lecture par quelque fiche ; une unité lue à une génération antérieure est refusée
      à toute fiche (une tranche se partage dans sa génération, jamais ensuite) ; **clés** (K9-2) — `entrer(..., cles=…)`
      fixe l'empreinte de clé de chaque fiche, `ajouter_trajectoire(..., empreinte_cle=…)` refuse un résultat d'une autre
      clé ; **journal** (K9-6) — `Course(alpha, journal=…)` reçoit l'objet qui journalise les parties calculées
      (`engagement_apparie.Lignees`) : `ajouter_trajectoire` refuse une partie absente du journal ou une seconde évaluation
      de la fiche dans la génération, `lire` refuse une déclaration « sans partie » contredite par le journal ; **« sans
      partie »** refusée pour une fiche gelée, arrêtée, promue ou qui a sa partie (K9-10 c).
    """

    def __init__(self, alpha=0.05, journal=None, essai=False):
        if not 0.0 < alpha < 1.0:
            raise ValueError("α dans ]0 ; 1[")
        if journal is None and not essai:
            raise ValueError("course sans journal des parties : les gardes K9-6 ne tiennent pas ; passer essai=True pour un essai "
                             "sans garde, jamais en production (K10-7)")
        self.alpha = alpha
        self.essai = essai
        self.journal = journal
        self.premiere_lecture = {}
        self.cle_de = {}
        self.alpha_engage = 0.0
        self.budgets = {}
        self.log_e = {}
        self.famille_de = {}
        self.gelees = set()
        self.arretees = set()
        self.promues = set()
        self.retirees = {}
        self.exclues = set()
        self.lectures = []
        self.generation = 1
        self.derniere_partie = {}
        self.unites_lues = {}
        self.parties_sans_identite = []
        self.abandons = {}
        self.sans_partie = {}

    def entrer(self, famille, fiches, alpha_c, cles=None):
        fiches = list(fiches)
        if cles is None and not self.essai:
            raise ValueError("entrée sans clés de l'héritage : la garde K9-2 ne tient pas (K10-7) ; passer cles={fiche: empreinte_cle}")
        if cles is not None and set(fiches) - set(cles):
            raise ValueError("chaque fiche entrée porte sa clé (K10-7)")
        cles = dict(cles or {})
        if cles and set(cles) - set(fiches):
            raise ValueError("clés de fiches non entrées")
        if len(set(cles.values())) != len(cles):
            raise ValueError("deux fiches portent la même clé (une affirmation, une fiche, D-S25 bis (5))")
        if set(cles.values()) & set(self.cle_de.values()):
            raise ValueError("clé déjà portée par une fiche de la course (relance sous un autre nom refusée)")
        if not fiches or len(set(fiches)) != len(fiches):
            raise ValueError("famille vide ou fiche en double")
        if any(f in self.budgets for f in fiches):
            raise ValueError("une fiche n'entre qu'une fois (une relance garde son budget d'entrée)")
        if not alpha_c > 0 or self.alpha_engage + alpha_c > self.alpha + 1e-12:
            raise ValueError(f"niveau de famille refusé : {self.alpha_engage:.6g} déjà engagé, {alpha_c:.6g} demandé, "
                             f"α = {self.alpha}")
        self.alpha_engage += alpha_c
        for f in fiches:
            self.budgets[f] = alpha_c / len(fiches)
            self.log_e[f] = 0.0
            self.famille_de[f] = famille
            if f in cles:
                self.cle_de[f] = cles[f]

    def seuil_log(self, fiche):
        return -math.log(self.budgets[fiche])

    def ajouter_trajectoire(self, fiche, trajectoire_log, unites=None, sans_identite=False, empreinte_cle=None,
                            empreinte_unites=None):
        if fiche not in self.budgets:
            raise KeyError(f"fiche non entrée : {fiche!r}")
        if fiche in self.gelees:
            raise ValueError(f"fiche gelée {fiche!r} : partie refusée (contrat de D-S25 bis (2))")
        if self.derniere_partie.get(fiche) == self.generation:
            raise ValueError(f"fiche {fiche!r} : une seule partie par génération")
        # v40 (CL39-09) : +∞ promouvait, NaN était ignoré sans erreur ; refus avant tout changement d'état
        trajectoire_log = list(trajectoire_log)
        for t, lw in enumerate(trajectoire_log):
            _exiger_fini(lw, f"fiche {fiche!r} : trajectoire, instant {t + 1}")
        if fiche in self.cle_de and empreinte_cle != self.cle_de[fiche]:
            raise ValueError(f"fiche {fiche!r} : partie d'une autre clé de l'héritage que celle de la fiche (K9-2)")
        if self.journal is not None:
            entrees = [j for j in self.journal.journal if j["generation"] == self.generation and j["fiche"] == fiche]
            if len(entrees) != 1:
                raise ValueError(f"fiche {fiche!r} : {len(entrees)} partie(s) au journal pour la génération {self.generation} "
                                 f"(exactement une évaluation par fiche et par génération, K9-6)")
            if empreinte_unites is None or entrees[0]["empreinte_unites"] != empreinte_unites:
                raise ValueError(f"fiche {fiche!r} : la partie ajoutée n'est pas celle du journal (empreinte des unités, K9-6)")
            # version 30 (K11-3) : la trajectoire et la clé sont celles que le journal a enregistrées, pas celles que déclare l'appelant
            if entrees[0].get("empreinte_trajectoire") is not None and _empreinte_trajectoire(trajectoire_log) != entrees[0]["empreinte_trajectoire"]:
                raise ValueError(f"fiche {fiche!r} : trajectoire différente de celle que le journal a enregistrée (K11-3)")
            if entrees[0].get("empreinte_cle") is not None and entrees[0]["empreinte_cle"] != empreinte_cle:
                raise ValueError(f"fiche {fiche!r} : clé déclarée différente de celle du journal (K11-3)")
        if unites is None:
            if not sans_identite:
                raise ValueError(f"fiche {fiche!r} : partie sans identifiants d'unités (passer `unites`, ou déclarer "
                                 f"sans_identite=True, tracé) — K8-1")
            self.parties_sans_identite.append((self.generation, fiche))
        else:
            nouvelles = set(unites)
            if not nouvelles:
                raise ValueError(f"fiche {fiche!r} : liste d'unités vide")
            deja = self.unites_lues.setdefault(fiche, set())
            commun = nouvelles & deja
            if commun:
                raise ValueError(f"fiche {fiche!r} : {len(commun)} unité(s) déjà lue(s) (unités fraîches, D-S25 bis (5)) : "
                                 f"{sorted(map(str, commun))[:3]}")
            anciennes = {u for u in nouvelles if self.premiere_lecture.get(u, self.generation) < self.generation}
            if anciennes:
                raise ValueError(f"fiche {fiche!r} : {len(anciennes)} unité(s) lue(s) par la course à une génération antérieure "
                                 f"(fraîcheur par rapport à la course, K9-1) : {sorted(map(str, anciennes))[:3]}")
            for u in nouvelles:
                self.premiere_lecture.setdefault(u, self.generation)
            deja |= nouvelles
        self.derniere_partie[fiche] = self.generation
        if fiche in self.promues or fiche in self.arretees:
            return self.log_e[fiche]  # processus arrêté : la suite est ignorée (temps d'arrêt, valide)
        base, seuil = self.log_e[fiche], self.seuil_log(fiche)
        valeur = base
        for lw in trajectoire_log:
            valeur = base + lw
            if valeur >= seuil:
                self.arretees.add(fiche)
                break
        self.log_e[fiche] = valeur
        return valeur

    def abandonner(self, fiche, trajectoire_log=None, avant_partie=False, motif="", unites=None, sans_identite=False,
                   empreinte_cle=None, empreinte_unites=None):
        if fiche not in self.budgets:
            raise KeyError(f"fiche non entrée : {fiche!r}")
        if fiche in self.gelees:
            if trajectoire_log is not None:
                raise ValueError(f"fiche {fiche!r} déjà gelée : partie refusée (K7-5)")
            self.abandons.setdefault(("redite", fiche), []).append((self.generation, motif))  # K8-3 : tracé, sans effet
            return
        if trajectoire_log is not None:
            self.ajouter_trajectoire(fiche, trajectoire_log, unites, sans_identite, empreinte_cle, empreinte_unites)
            mode = "partie_passee"
        elif avant_partie:
            if self.journal is not None and any(j["generation"] == self.generation and j["fiche"] == fiche and not j.get("vide")
                                                for j in self.journal.journal):
                raise ValueError(f"abandon « avant partie » de {fiche!r} refusé : sa partie de la génération {self.generation} est au "
                                 f"journal (K11-3) — passer la partie, ou abandonner après")
            mode = "avant_partie"
        elif fiche in self.promues or fiche in self.arretees or self.derniere_partie.get(fiche) == self.generation:
            mode = "apres_partie"
        else:
            raise ValueError(f"abandon de {fiche!r} sans la partie de la génération {self.generation} : passer la partie, "
                             f"ou déclarer avant_partie=True si la décision n'a vu aucune issue de cette génération")
        self.abandons[fiche] = (self.generation, mode, motif)
        self.gelees.add(fiche)

    def lire(self, sans_partie=None):
        sans_partie = dict(sans_partie or {})
        actives = [f for f in self.budgets if f not in self.gelees and f not in self.arretees and f not in self.promues
                   and f not in self.exclues]
        manquantes = sorted(str(f) for f in actives
                            if self.derniere_partie.get(f) != self.generation and not sans_partie.get(f))
        if manquantes:
            raise ValueError(f"génération {self.generation} : fiches actives sans partie ni déclaration : {manquantes[:5]} "
                             f"(K7-1 : toute partie calculée est ajoutée ; sinon déclarer sans_partie[fiche] = motif)")
        for f in sans_partie:
            if f not in self.budgets:
                raise KeyError(f"déclaration « sans partie » pour une fiche non entrée : {f!r}")
            if f not in actives or self.derniere_partie.get(f) == self.generation:
                raise ValueError(f"déclaration « sans partie » refusée pour {f!r} : fiche gelée, arrêtée, promue, exclue ou qui a sa "
                                 f"partie dans la génération {self.generation} (K9-10 c)")
        if self.journal is not None:
            entrees_g = [j for j in self.journal.journal if j["generation"] == self.generation]
            fantomes = sorted(str(j["fiche"]) for j in entrees_g if j["fiche"] not in self.budgets)
            if fantomes:
                raise ValueError(f"génération {self.generation} : le journal porte des parties pour des fiches inconnues de la course "
                                 f"(fiches fantômes, K11-3) : {fantomes[:5]}")
            futures = [j for j in self.journal.journal if isinstance(j["generation"], int) and j["generation"] > self.generation]
            if futures:
                raise ValueError(f"génération {self.generation} : le journal porte des parties d'une génération à venir (K11-3)")
            calculees = {j["fiche"] for j in entrees_g if not j.get("vide")}
            menteuses = sorted(str(f) for f in sans_partie if f in calculees)
            if menteuses:
                raise ValueError(f"génération {self.generation} : déclaration « sans partie » contredite par le journal des "
                                 f"parties pour {menteuses[:5]} (K8-2, K9-6)")
            # K11-3 : toute unité journalisée dans la génération est lue par la course, ajoutée ou non
            for j in entrees_g:
                for u in j.get("identifiants_unites", []):
                    self.premiere_lecture.setdefault(tuple(u) if isinstance(u, list) else u, self.generation)
        for f, m in sans_partie.items():
            self.sans_partie[(self.generation, f)] = m
        pool = [f for f in self.budgets if f not in self.exclues]
        retenues = ebh_pondere({f: self.log_e[f] for f in pool}, {f: self.budgets[f] for f in pool}, self.alpha)
        nouvelles = retenues - self.promues
        self.promues |= nouvelles
        self.lectures.append(sorted(map(str, nouvelles)))
        self.generation += 1
        return nouvelles

    def retirer(self, fiche, motif):
        if fiche not in self.budgets:
            raise KeyError(f"fiche non entrée : {fiche!r}")
        if not motif:
            raise ValueError("un retrait porte son motif")
        self.retirees.setdefault(fiche, []).append((self.generation, motif))  # K7-5 : motifs gardés, jamais écrasés
        self.gelees.add(fiche)
        self.exclues.add(fiche)

    def promues_rapportees(self):
        return self.promues - set(self.retirees)

    def bonferroni(self):
        return {f for f in self.budgets if f not in self.exclues and self.log_e[f] >= self.seuil_log(f) - 1e-12}
