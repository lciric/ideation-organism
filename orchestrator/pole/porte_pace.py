"""Porte PACE (arXiv 2606.08106v1) — **bras de référence** du juge figé ; **jamais une sélection d'agent (N-053)** ;
**exploratoire, non préenregistré**.

Décision de Lazar du 29 octobre 2026 (01:15, heure de Paris) : « porte PACE comme bras de référence du juge figé ». Ce module
écrit la porte de validation de PACE **telle que l'extrait la décrit** (`../corpus-primaire-v4/extrait-2606.08106-v1.md`,
seule source ; pages du PDF entre crochets), et la met côte à côte avec notre pari apparié borné (`pari_apparie`) et avec
l'« acceptation gloutonne », sur les mêmes données. Aucun score rendu ici ne sert à choisir, classer ou garder un agent : les
décisions sont rendues dans l'ordre d'entrée, sans rang ni « meilleur » ; elles mesurent des règles d'acceptation.

Repris de l'extrait (page citée) :

- **appariement** [p.4] : titulaire (ici la *référence*) et candidat sont notés sur les mêmes instances ; w = 1 si le
  candidat a juste et la référence faux, w = 0 dans le cas inverse, égalités écartées (paires de McNemar) ;
- **règle de pari** [p.4, équation (2)] : richesse E₀ = 1, puis E ← E·(1 + λ(2w − 1)) après chaque paire discordante,
  λ ∈ [0 ; 1) ; **mise par défaut λ = 0,5, niveau α = 0,05** [p.4] ;
- **seuil 1/α et arrêt à tout instant** [p.4-5] : validation dès que E ≥ 1/α ; évaluation incrémentale, arrêt au premier
  franchissement ; **rejet** si le budget d'évaluation s'épuise avant le seuil [p.4] ; garantie par candidat (inégalité de
  Ville), « not a run-level familywise bound » [p.5, p.9 tableau 3] ;
- **témoin planté à gain connu** comme contrôle positif [p.6, régime « contrôlé », « a unit test for acceptors »] ;
- **jeu d'audit neuf**, jamais vu de la règle, qui étiquette après coup : fausse validation si l'écart audité est ≤ 0,
  nuisible s'il est < 0 [p.6, « Metrics »] ;
- **acceptation gloutonne** comme référence : « keep it if the score went up » [p.1], « keeps any candidate whose reused dev
  score ticks up » [p.2, légende de la figure 1].

**Réduction à nos briques.** Avec v = (candidat juste) − (référence juste) ∈ {−1 ; 0 ; 1}, le facteur 1 + λ(2w − 1) vaut
1 + λ·v sur une paire discordante, et 1 + λ·0 = 1 sur une égalité (« écartée » revient à multiplier par 1). La règle de PACE
est donc exactement `pari_apparie.trajectoire_log_richesse(v, lambdas=(λ,))` : un seul λ au lieu du mélange sur Λ, lue
contre log(1/α) au lieu de log(m/α), sans garde δ ni lecture e-BH. Seul écart de domaine : PACE admet λ = 0 (richesse
constante, jamais de validation), que `trajectoire_log_richesse` refuse ; λ = 0 est traité à part ici.

Choix que l'extrait ne fixe pas — **[INFÉRÉ]**, page la plus proche :

- **[INFÉRÉ, p.4]** taille de lot : « a fixed batch size unless noted », valeur absente de l'extrait (l'algorithme 1, p.5,
  est coupé) ; défaut 10 ici. Le franchissement est testé **après chaque paire** (« after each discordant pair we update »,
  « commit as soon as E ≥ 1/α », p.4) ; le lot ne change que le **coût** (instances notées, arrondi au lot entamé).
- **[INFÉRÉ, p.4 et p.6]** budget d'évaluation = tout le jeu de développement fourni (n = 40 dans les expériences, p.6),
  sauf `budget` explicite.
- **[INFÉRÉ, p.1-2 ; équation (1) coupée, p.4]** glouton : validation si le score du candidat sur le jeu de développement
  est **strictement** supérieur à celui de la référence (« went up », « ticks up ») ; égalité = rejet.
- **[INFÉRÉ, p.3]** référence **fixe** : dans PACE le titulaire devient le candidat validé (c_{t+1} = c′_t, p.3) ; dans le
  bras de référence du juge figé, aucun candidat ne devient la référence (N-053 : rien n'est sélectionné), donc chaque
  candidat est comparé à la même référence. C'est un écart assumé à la boucle de PACE, pas une lecture de l'extrait.
- **[INFÉRÉ, p.6]** monde simulé (`simuler_suite`) : exactitudes Bernoulli par instance, corrélation entre référence et
  candidat par un aléa d'instance partagé avec probabilité ρ ; jeu de développement **réutilisé** pour tous les candidats
  d'une suite (option, défaut vrai, comme le « small reused dev » de p.6) ; le régime « nul » de PACE (p.6, stochastique)
  est remplacé par un nul exact (exactitude du candidat = exactitude de la référence).

Notre bras (`pari_apparie_binaire`, dans `comparer`) : mêmes contrastes v, mélange sur Λ = {0,1 ; 0,3 ; 0,6 ; 0,9},
e-processus arrêté à log(m/α) avec m = taille de la suite déclarée avant lecture, lecture **e-BH** sur la suite entière
(budgets α/m, `pari_apparie.ebh_pondere`) — la borne porte sur la suite, pas sur chaque candidat — et garde δ facultative
(`ecarts_faux_positifs`, `delta`). Simplification dite : une famille unique de taille connue, non la `Course` à générations
(dépense α_g, héritage, journal), qui reste le seul chemin du pôle.

**Puissance de la garde δ (version 40, relecture CL6 de session-depot, CL39-10).** Le refus du tricheur ne montre pas que
la garde discrimine : il faut aussi qu'elle laisse passer un témoin **honnête** (gain 0,35, écarts de faux positifs
d'espérance nulle), régime « honnete_garde » de `simuler_suite`. Dans le monde par défaut (écart g ∈ {−1 ; 0 ; 1},
P(±1) = 0,1, δ = 0,05, m = 20), notre bras ne valide ce témoin que dans quelques pour cent des suites, même à n = 400. Lecture,
vérifiée par simulation de la garde seule (200 répétitions) et par le calcul :

- **la marge δ contre le bruit de l'écart** est la cause première. Le témoin honnête n'est qu'à δ − E[g] = 0,05 du nul de la
  garde « E[g] ≥ δ », contre un écart-type de g de 0,45 par unité (rapport 0,11). Le taux de croissance espéré du log de la
  richesse, E[log(1 + λ(δ − g))], vaut au mieux ≈ 0,006 par unité (λ = 0,3 ; il est négatif pour λ = 0,6 et 0,9) : il
  faut de l'ordre de mille unités honnêtes pour atteindre log(m/α) + log 4 ≈ 7,4 (mesuré : 7 % à 400 unités, 42 % à 1 000,
  75 % à 2 000). **Même sans bruit** (g ≡ 0), le facteur par unité est au plus 1 + 0,9·0,05 = 1,045 : la garde ne peut
  franchir m/α = 400 avant 166 unités (93 pour m = 1, 133 pour m = 5) ; à n = 40 ou 120 elle est **structurellement
  incapable** de valider, sauf excursions favorables du bruit ;
- **le seuil m/α** (arrêt de l'e-processus et e-BH) coûte ensuite : avec un seul témoin vrai dans la suite, l'e-BH exige
  e ≥ m/α comme un seuil par candidat ; à 1/α par candidat, la même garde validerait 29 % à 400 unités au lieu de 7 % — ce
  qui ne serait plus une borne de suite ;
- **la mise n'est pas en cause** : la mise optimale pour ce bruit est ≈ (δ − E[g])/Var(g) ≈ 0,25, et Λ contient 0,3 ; la
  garde à λ = 0,3 seul ne fait pas mieux que le mélange à 400 unités (10 % contre 7 %), le mélange ne coûte que log 4.

Conséquence : la garde δ = 0,05 est un instrument de **mille unités honnêtes**, pas de quarante ; avec moins, elle refuse
tout le monde, tricheur compris, et ce refus n'est pas une preuve de discrimination. La démonstration rapporte donc la
puissance de la garde (témoin honnête validé) à côté du refus du tricheur. La règle de production (`pari_apparie`) est
inchangée ; le monde simulé gagne `bruit_fp` (P(±1)) et `n_garde` (unités de la garde) pour montrer un cas sain où la garde
discrimine (bruit 0,02, 600 unités : témoin honnête validé, tricheur refusé).

Python pur ; numpy n'est importé que par `graines` (dérivation des graines par `numpy.random.SeedSequence` si disponible,
sinon SHA-256 par `pole.outils.graine_derivee`).
"""

import math

from . import pari_apparie as pa

ALPHA_PACE = 0.05        # p.4
LAMBDA_PACE = 0.5        # p.4
TAILLE_LOT_PACE = 10     # [INFÉRÉ, p.4] : « a fixed batch size », valeur absente de l'extrait
USAGE = "bras de référence ; jamais une sélection d'agent (N-053) ; exploratoire, non préenregistré"
SOURCE = "arXiv 2606.08106v1, extrait ../corpus-primaire-v4/extrait-2606.08106-v1.md"


class PorteInvalide(ValueError):
    """Base des refus nommés de ce module (R5 : aucun repli silencieux)."""


class ResultatInvalide(PorteInvalide):
    """Issue d'instance absente du domaine {0 ; 1} (NaN, 0,5, 2, chaîne…), ou écart de garde non fini."""


class LongueursDifferentes(PorteInvalide):
    """Référence et candidat ne portent pas sur le même nombre d'instances."""


class NiveauInvalide(PorteInvalide):
    """α hors de ]0 ; 1[."""


class MiseInvalide(PorteInvalide):
    """λ hors de [0 ; 1) (PACE, p.4-5), ou grille Λ invalide pour notre bras."""


class JeuVide(PorteInvalide):
    """Jeu de développement vide, ou budget hors de [1 ; n]."""


class JeuAuditVide(PorteInvalide):
    """Jeu d'audit vide : la décision ne peut être étiquetée (p.6)."""


class SuiteInvalide(PorteInvalide):
    """Suite de candidats vide, noms en double, champ manquant, réglage de lot invalide."""


# --- vérifications ------------------------------------------------------------------------------------------------------

def _nombre(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def verifier_niveau(alpha):
    if not _nombre(alpha) or not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise NiveauInvalide(f"α dans ]0 ; 1[ : {alpha!r}")
    return float(alpha)


def verifier_mise(lam):
    """PACE : λ ∈ [0 ; 1) (p.4, p.5 « any λ ∈ [0, 1) »)."""
    if not _nombre(lam) or not math.isfinite(lam) or not 0.0 <= lam < 1.0:
        raise MiseInvalide(f"mise λ dans [0 ; 1) : {lam!r}")
    return float(lam)


def _issue(x, ou):
    if isinstance(x, bool):
        return int(x)
    if _nombre(x) and math.isfinite(x) and x in (0, 1):
        return int(x)
    raise ResultatInvalide(f"{ou} : issue hors de {{0 ; 1}} : {x!r}")


def paires(reference, candidat, ou="développement"):
    """Issues appariées (référence, candidat), instance par instance, dans l'ordre d'évaluation."""
    reference, candidat = list(reference), list(candidat)
    if len(reference) != len(candidat):
        raise LongueursDifferentes(f"{ou} : {len(reference)} issues de référence contre {len(candidat)} du candidat")
    return [(_issue(r, f"{ou}, référence, instance {i}"), _issue(c, f"{ou}, candidat, instance {i}"))
            for i, (r, c) in enumerate(zip(reference, candidat))]


def contrastes_binaires(liste_paires):
    """v = candidat − référence ∈ {−1 ; 0 ; 1} ; v = 0 sur une égalité (paire « écartée », facteur 1)."""
    return [c - r for r, c in liste_paires]


def _verifier_ecarts(ecarts):
    sortie = []
    for i, g in enumerate(ecarts):
        if not _nombre(g) or not math.isfinite(g):
            # `pari_apparie.trajectoire_log_garde` borne δ − g par min/max : un NaN y deviendrait +1 (le plus favorable)
            raise ResultatInvalide(f"garde : écart de faux positifs non fini à l'unité {i} : {g!r}")
        sortie.append(float(g))
    return sortie


# --- la porte de PACE ---------------------------------------------------------------------------------------------------

def trajectoire_pace(liste_paires, lam=LAMBDA_PACE):
    """log E après chaque instance (équation (2), p.4) ; égalités : facteur 1. Se ramène à
    `pari_apparie.trajectoire_log_richesse(v, (λ,))` pour λ ∈ ]0 ; 1[ ; λ = 0 : richesse constante 1."""
    lam = verifier_mise(lam)
    v = contrastes_binaires(liste_paires)
    if lam == 0.0:
        return [0.0] * len(v)
    return pa.trajectoire_log_richesse(v, lambdas=(lam,))


def porte_pace(reference, candidat, alpha=ALPHA_PACE, lam=LAMBDA_PACE, budget=None, taille_lot=TAILLE_LOT_PACE):
    """Une décision de la porte de PACE pour un candidat (p.4-5).

    Validation au premier instant où E ≥ 1/α ; rejet si `budget` instances sont notées sans franchissement. Rend l'étape
    d'arrêt (instances lues à la décision), le coût (arrondi au lot entamé, [INFÉRÉ, p.4]), le nombre de paires discordantes
    lues et la trajectoire jusqu'à l'arrêt."""
    alpha = verifier_niveau(alpha)
    lam = verifier_mise(lam)
    if not (isinstance(taille_lot, int) and not isinstance(taille_lot, bool) and taille_lot >= 1):
        raise SuiteInvalide(f"taille de lot : entier ≥ 1 : {taille_lot!r}")
    lp = paires(reference, candidat)
    n = len(lp)
    if n == 0:
        raise JeuVide("jeu de développement vide : la porte n'a rien à lire")
    if budget is None:
        budget = n
    if not (isinstance(budget, int) and not isinstance(budget, bool) and 1 <= budget <= n):
        raise JeuVide(f"budget dans [1 ; {n}] : {budget!r}")
    traj = trajectoire_pace(lp[:budget], lam)
    seuil = math.log(1.0 / alpha)
    arret = next((t + 1 for t, lw in enumerate(traj) if lw >= seuil - 1e-12), None)
    etape = arret if arret is not None else budget
    cout = min(budget, -(-etape // taille_lot) * taille_lot)
    return {"validee": arret is not None, "etape_arret": etape, "cout": cout,
            "discordantes": sum(1 for r, c in lp[:etape] if r != c), "log_richesse": traj[etape - 1], "seuil_log": seuil,
            "trajectoire_log": traj[:etape], "alpha": alpha, "lambda": lam}


def glouton(reference, candidat):
    """Acceptation gloutonne (p.1-2) : validation si le score du candidat sur le jeu de développement dépasse
    **strictement** celui de la référence ([INFÉRÉ] : équation (1) coupée, p.4). Lit tout le jeu."""
    lp = paires(reference, candidat)
    n = len(lp)
    if n == 0:
        raise JeuVide("jeu de développement vide")
    ecart = sum(c - r for r, c in lp) / n
    return {"validee": ecart > 0, "etape_arret": n, "cout": n, "ecart_dev": ecart}


# --- notre pari apparié sur les mêmes données --------------------------------------------------------------------------

def pari_apparie_binaire(reference, candidat, alpha=ALPHA_PACE, m=1, lambdas=pa.LAMBDAS, ecarts_faux_positifs=None,
                         delta=None):
    """Notre e-processus sur les mêmes contrastes binaires : mélange sur Λ, arrêt à log(m/α), garde δ facultative
    (`pari_apparie.evaluer`). La décision de famille (e-BH) se prend dans `comparer`."""
    alpha = verifier_niveau(alpha)
    if not (isinstance(m, int) and not isinstance(m, bool) and m >= 1):
        raise SuiteInvalide(f"m : entier ≥ 1 : {m!r}")
    try:
        pa._verifier_lambdas(lambdas)
    except ValueError as e:
        raise MiseInvalide(str(e)) from None
    lp = paires(reference, candidat)
    if not lp:
        raise JeuVide("jeu de développement vide")
    if ecarts_faux_positifs is not None:
        ecarts_faux_positifs = _verifier_ecarts(ecarts_faux_positifs)
        if not ecarts_faux_positifs:
            raise JeuVide("garde : liste d'écarts vide")
        if delta is None or not _nombre(delta) or not math.isfinite(delta) or not 0.0 < delta < 1.0:
            raise PorteInvalide(f"garde : δ dans ]0 ; 1[ : {delta!r}")
    elif delta is not None:
        # v40 : un δ sans écarts était ignoré en silence (R5)
        raise PorteInvalide(f"garde : δ = {delta!r} fourni sans écarts de faux positifs")
    r = pa.evaluer({"reference": contrastes_binaires(lp)}, ecarts_faux_positifs=ecarts_faux_positifs, delta=delta,
                   alpha=alpha, m=m, lambdas=tuple(lambdas))
    return {"arretee_au_seuil": r["promue"], "etape_arret": r["instant_d_arret"] or len(lp), "cout": r["instant_d_arret"] or len(lp),
            "log_e": r["log_e_valeur"], "seuil_log": r["seuil_log"], "log_garde_finale": r["log_garde_finale"]}


# --- comparaison côte à côte -------------------------------------------------------------------------------------------

CHAMPS = ("nom", "dev_reference", "dev_candidat", "audit_reference", "audit_candidat")
BRAS = ("pace", "pari_apparie", "glouton")


def _compteurs_vides():
    return {"validations": 0, "fausses_audit": 0, "nuisibles_audit": 0, "vraies_audit": 0, "fausses_verite": 0,
            "vraies_verite": 0, "temoins": 0, "temoins_valides": 0, "cout_total": 0, "etapes_des_validees": []}


def comparer(candidats, alpha=ALPHA_PACE, lam=LAMBDA_PACE, budget=None, taille_lot=TAILLE_LOT_PACE, lambdas=pa.LAMBDAS,
             m=None):
    """Sur la même suite de candidats et le même jeu d'audit : décision de la porte PACE, de notre pari apparié (e-BH sur
    la suite) et de l'acceptation gloutonne, côte à côte, avec les compteurs.

    `candidats` : liste de dictionnaires `{"nom", "dev_reference", "dev_candidat", "audit_reference", "audit_candidat"}`
    (issues 0/1 ; développement : ce que lisent les trois règles ; audit : étiquetage seul, jamais lu par une règle, p.6),
    plus, facultatifs : `"gain_reel"` (vérité connue du simulateur), `"temoin"` (vrai : gain planté connu, contrôle positif,
    p.6), `"ecarts_faux_positifs"` et `"delta"` (garde de **notre** bras seulement ; PACE et le glouton l'ignorent).
    `m` : taille de la famille de notre bras (défaut : nombre de candidats, déclaré avant lecture).

    Compteurs par bras : validations ; fausses (écart audité ≤ 0) et nuisibles (< 0) selon l'audit [p.6] ; vraies selon
    l'audit (> 0) ; fausses et vraies selon la vérité si `gain_reel` est donné (fausse : gain réel ≤ 0) ; témoins validés ;
    coût total (instances notées) ; étapes d'arrêt des validées. Les décisions sont rendues dans l'ordre d'entrée : aucun
    rang, aucun choix (N-053)."""
    alpha = verifier_niveau(alpha)
    lam = verifier_mise(lam)
    if not isinstance(candidats, (list, tuple)) or not candidats:
        raise SuiteInvalide("suite de candidats vide")
    noms = [c.get("nom") if isinstance(c, dict) else None for c in candidats]
    for c in candidats:
        if not isinstance(c, dict) or any(k not in c for k in CHAMPS):
            raise SuiteInvalide(f"candidat incomplet : champs requis {CHAMPS}")
    if len(set(map(str, noms))) != len(noms):
        raise SuiteInvalide("noms de candidats en double")
    m = len(candidats) if m is None else m
    if not (isinstance(m, int) and not isinstance(m, bool) and m >= len(candidats)):
        raise SuiteInvalide(f"m : entier ≥ nombre de candidats ({len(candidats)}) : {m!r}")
    decisions, log_e = [], {}
    for c in candidats:
        nom = c["nom"]
        audit = paires(c["audit_reference"], c["audit_candidat"], ou=f"audit de {nom!r}")
        if not audit:
            raise JeuAuditVide(f"candidat {nom!r} : jeu d'audit vide (étiquetage impossible, p.6)")
        ecart_audit = sum(cc - r for r, cc in audit) / len(audit)
        gain = c.get("gain_reel")
        if gain is not None and (not _nombre(gain) or not math.isfinite(gain)):
            raise ResultatInvalide(f"candidat {nom!r} : gain réel non fini : {gain!r}")
        d_pace = porte_pace(c["dev_reference"], c["dev_candidat"], alpha, lam, budget, taille_lot)
        d_glouton = glouton(c["dev_reference"], c["dev_candidat"])
        d_pari = pari_apparie_binaire(c["dev_reference"], c["dev_candidat"], alpha, m, lambdas,
                                      c.get("ecarts_faux_positifs"), c.get("delta"))
        log_e[nom] = d_pari["log_e"]
        decisions.append({"nom": nom, "temoin": bool(c.get("temoin", False)), "gain_reel": gain, "ecart_audit": ecart_audit,
                          "pace": {k: d_pace[k] for k in ("validee", "etape_arret", "cout", "discordantes", "log_richesse")},
                          "pari_apparie": d_pari, "glouton": d_glouton})
    retenues = pa.ebh_pondere(log_e, {n: alpha / m for n in log_e}, alpha)  # budgets α/m, somme ≤ α
    for d in decisions:
        d["pari_apparie"]["validee"] = d["nom"] in retenues
    compteurs = {b: _compteurs_vides() for b in BRAS}
    for d in decisions:
        for b in BRAS:
            k = compteurs[b]
            k["cout_total"] += d[b]["cout"]
            k["temoins"] += d["temoin"]
            if not d[b]["validee"]:
                continue
            k["validations"] += 1
            k["etapes_des_validees"].append(d[b]["etape_arret"])
            k["fausses_audit"] += d["ecart_audit"] <= 0
            k["nuisibles_audit"] += d["ecart_audit"] < 0
            k["vraies_audit"] += d["ecart_audit"] > 0
            if d["gain_reel"] is not None:
                k["fausses_verite"] += d["gain_reel"] <= 0
                k["vraies_verite"] += d["gain_reel"] > 0
            k["temoins_valides"] += d["temoin"]
    for k in compteurs.values():
        k["controle_positif_reussi"] = (k["temoins_valides"] == k["temoins"]) if k["temoins"] else None
    return {"usage": USAGE, "source": SOURCE, "decisions": decisions, "bras": compteurs,
            "reglages": {"alpha": alpha, "lambda_pace": lam, "budget": budget, "taille_lot": taille_lot,
                         "lambdas_pari": list(lambdas), "m": m, "candidats": len(candidats)}}


# --- monde simulé et graines -------------------------------------------------------------------------------------------

def graines(racine, n):
    """n graines entières dérivées de `racine` : `numpy.random.SeedSequence(racine).spawn(n)` si numpy est importable
    (R9), sinon SHA-256 (`pole.outils.graine_derivee`). Rend (graines, méthode)."""
    try:
        import numpy as np
        return ([int(s.generate_state(1, dtype=np.uint64)[0]) for s in np.random.SeedSequence(racine).spawn(n)],
                f"numpy.random.SeedSequence (numpy {np.__version__})")
    except ImportError:
        from .outils import graine_derivee
        return [graine_derivee(racine, "porte_pace", i) for i in range(n)], "SHA-256 (pole.outils.graine_derivee)"


def _issues(rng, latents, s, rho):
    """Issue Bernoulli(s) par instance ; avec probabilité ρ, l'aléa de l'instance est partagé (`latents`)."""
    return [int((u if rng.random() < rho else rng.random()) < s) for u in latents]


REGIMES = ("nulle", "gain", "honnete_garde", "tricheur")


def simuler_suite(rng, regime="nulle", m=20, n_dev=40, n_audit=120, s_ref=0.35, rho=0.5, gain_temoin=0.35,
                  bruit=(-0.10, 0.0), dev_reutilise=True, fp_tricheur=0.15, delta=0.05, bruit_fp=0.1, n_garde=None):
    """Une suite de m candidats contre une référence fixe ([INFÉRÉ, p.6], voir l'en-tête).

    `regime` : « nulle » (tous les candidats ont l'exactitude de la référence, gain 0), « gain » (un témoin planté à
    `gain_temoin`, les autres à un gain tiré dans `bruit`, aucun meilleur que la référence), « tricheur » (comme « gain »,
    mais le témoin gagne en exactitude **et** tire plus de faux positifs que la référence d'en moyenne `fp_tricheur`
    > δ ; tous les candidats portent la garde, que seul notre bras lit), « honnete_garde » (version 40 : comme
    « tricheur », mais **sans excès** : le témoin et les autres tirent autant de faux positifs que la référence, E[g] = 0 ;
    cas sain de la garde, qui mesure sa puissance). Écarts de faux positifs : g ∈ {−1 ; 0 ; 1} par unité, P(+1) =
    `bruit_fp` + excès, P(−1) = `bruit_fp`, sur `n_garde` unités (défaut : `n_dev`). Jeu d'audit : mêmes instances pour
    tous les candidats, issues de la référence fixées. `dev_reutilise` : mêmes instances de développement et issues de la
    référence fixées pour toute la suite (sinon tirées à neuf pour chaque candidat : nul exact par candidat)."""
    if regime not in REGIMES:
        raise SuiteInvalide(f"régime inconnu : {regime!r}")
    if not (0.0 <= s_ref <= 1.0 and 0.0 <= rho <= 1.0) or n_dev < 1 or n_audit < 1 or m < 1:
        raise SuiteInvalide("réglages du monde simulé hors domaine")
    n_garde = n_dev if n_garde is None else n_garde
    if not (isinstance(n_garde, int) and not isinstance(n_garde, bool) and n_garde >= 1):
        raise SuiteInvalide(f"n_garde : entier ≥ 1 : {n_garde!r}")
    if not all(_nombre(x) and math.isfinite(x) for x in (bruit_fp, fp_tricheur)) or not (
            bruit_fp >= 0.0 and fp_tricheur >= 0.0 and 2 * bruit_fp + fp_tricheur <= 1.0):
        raise SuiteInvalide(f"faux positifs : bruit_fp ≥ 0, fp_tricheur ≥ 0, 2·bruit_fp + fp_tricheur ≤ 1 : "
                            f"{bruit_fp!r}, {fp_tricheur!r}")

    def jeu(n):
        lat = [rng.random() for _ in range(n)]
        return lat, [int(u < s_ref) for u in lat]

    dev_lat, dev_ref = jeu(n_dev)
    aud_lat, aud_ref = jeu(n_audit)
    temoin = None if regime == "nulle" else rng.randrange(m)
    suite = []
    for j in range(m):
        if not dev_reutilise:
            dev_lat, dev_ref = jeu(n_dev)
        gain = 0.0 if regime == "nulle" else (gain_temoin if j == temoin else rng.uniform(*bruit))
        s_c = min(1.0, max(0.0, s_ref + gain))
        c = {"nom": f"c{j:02d}", "dev_reference": list(dev_ref), "dev_candidat": _issues(rng, dev_lat, s_c, rho),
             "audit_reference": list(aud_ref), "audit_candidat": _issues(rng, aud_lat, s_c, rho), "gain_reel": gain,
             "temoin": j == temoin}
        if regime in ("tricheur", "honnete_garde"):
            exces = fp_tricheur if (regime == "tricheur" and j == temoin) else 0.0
            # écart de faux positifs par unité g ∈ {−1 ; 0 ; 1} : P(+1) = bruit + excès, P(−1) = bruit → E[g] = excès
            c["ecarts_faux_positifs"] = [(1 if x < bruit_fp + exces else (-1 if x < 2 * bruit_fp + exces else 0))
                                         for x in (rng.random() for _ in range(n_garde))]
            c["delta"] = delta
        suite.append(c)
    return suite


def agreger(resultats):
    """Somme des compteurs de plusieurs `comparer` (une ligne par bras) ; « suites_avec_fausse » : suites où le bras a
    validé au moins un candidat de gain réel ≤ 0 (taux de famille observé)."""
    total = {b: {"suites": 0, "suites_avec_fausse": 0, **{k: 0 for k in _compteurs_vides() if k != "etapes_des_validees"},
                 "etapes": []} for b in BRAS}
    for r in resultats:
        for b in BRAS:
            k, t = r["bras"][b], total[b]
            t["suites"] += 1
            t["suites_avec_fausse"] += k["fausses_verite"] > 0
            for cle in t:
                if cle in k and cle not in ("etapes_des_validees",) and isinstance(k[cle], (int, float)) and not isinstance(k[cle], bool):
                    t[cle] += k[cle]
            t["etapes"] += k["etapes_des_validees"]
    return total
