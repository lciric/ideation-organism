"""Proposeurs de référence, sans modèle et sans dépense (v7, version 7) : le rôle « proposeur » devient enfichable.

Sur l'option 3 du tour du collisionneur « proposeur enfichable » (synthèse `docs/notes/collisionneur-proposeur-enfichable-v1/
synthese-proposeur-enfichable-v1.md` sur `main`, `0a209c33…`, unanime) : avant tout duel payé entre un proposeur Opus et un
chercheur de la littérature, **deux références gratuites** dans la même grammaire :

- « aleatoire » : des lois tirées au hasard au gabarit (moniteur, un ou deux traits, poids gaussiens bornés) ; si un
  proposeur à modèle ne fait pas mieux, la prise « proposeur » tombe ;
- « mecanique » : un chercheur mécanique sans modèle, qui ajuste sur la partie de développement (traits et issues visibles
  en phase exploratoire) une loi par moniteur et par sous-ensemble d'au plus deux traits, sous trois formes de la grammaire
  (softmax, par sous-population, si/sinon sur le signe d'un trait), et garde les meilleures par vraisemblance pénalisée
  (critère de Schwarz) ; si un proposeur à modèle ne fait pas mieux, la prise « exploration » tombe.

Les deux rendent des propositions au gabarit, qui passent par la même porte (`proposeur.valider_proposition`) que celles
d'un agent ; leurs stratégies (« aleatoire_au_gabarit », « mecanique_sur_developpement ») ne sont acceptées que d'un
proposeur de référence. Graines dérivées de la graine du pôle (R9 : `graine_derivee`, documentée).
"""

import itertools
import math
import random

from .outils import graine_derivee

REFERENCES = {
    "aleatoire_au_gabarit": "référence gratuite : loi tirée au hasard au gabarit (moniteur, un ou deux traits, poids bornés)",
    "mecanique_sur_developpement": ("référence gratuite : chercheur mécanique sans modèle — meilleure loi de la grammaire "
                                    "ajustée sur la partie de développement, par vraisemblance pénalisée"),
}
GENRES = ("agent", "aleatoire", "mecanique")
BORNE = 4.0
FORMES = ("softmax", "par_sous_population", "si_sinon")


def _borner(x):
    return max(-BORNE, min(BORNE, round(float(x), 6)))


def _softmax_sur(traits, poids_par_trait, k, d, biais=None):
    """Loi softmax de dimension d dont seuls `traits` portent des poids (poids_par_trait : k listes de len(traits))."""
    poids = [[0.0] * d for _ in range(k)]
    for c in range(k):
        for j, t in enumerate(traits):
            poids[c][t] = _borner(poids_par_trait[c][j])
    return {"type": "softmax", "poids": poids, "biais": [max(-2 * BORNE, min(2 * BORNE, round(float(b), 6)))
                                                         for b in (biais or [0.0] * k)]}


def propositions_aleatoires(description, nombre, graine, generation):
    """`nombre` lois tirées au hasard au gabarit ; aucune donnée lue."""
    rng = random.Random(graine_derivee(graine, "proposeur-aleatoire", generation))
    d = len(description["traits"])
    moniteurs = sorted(description["moniteurs"])
    sortie = []
    for i in range(nombre):
        moniteur = rng.choice(moniteurs)
        k = description["moniteurs"][moniteur]["nombre_issues"]
        traits = sorted(rng.sample(range(d), rng.choice([1, 2]) if d >= 2 else 1))
        poids = [[rng.gauss(0.0, 1.2) for _ in traits] for _ in range(k)]
        noms = ", ".join(description["traits"][t] for t in traits)
        sortie.append({"enonce": f"Référence aléatoire n° {i + 1} : l'issue du moniteur {moniteur} dépend de {noms} "
                                 "(loi tirée au hasard au gabarit)",
                       "strategie": "aleatoire_au_gabarit", "moniteur": moniteur,
                       "loi_predictive": _softmax_sur(traits, poids, k, d)})
    return sortie


def generateur_reference_au_gabarit(description):
    """v7, version 12 (F-C4 iii) : lois de référence pour le seuil de fusion de la mémoire, tirées au même gabarit que les
    propositions aléatoires (softmax sur un ou deux traits, poids gaussiens d'écart-type 1,2) ; `(rng, k, d) -> loi`."""
    d_monde = len(description["traits"])

    def tirer(rng, k, d):
        dd = min(d, d_monde) if d_monde else d
        traits = sorted(rng.sample(range(dd), rng.choice([1, 2]) if dd >= 2 else 1))
        poids = [[rng.gauss(0.0, 1.2) for _ in traits] for _ in range(k)]
        return _softmax_sur(traits, poids, k, d)

    return tirer


def _log_vraisemblance(loi, instances, issues, proba):
    return sum(math.log(max(1e-12, proba(loi, inst, [], 0)[y])) for inst, y in zip(instances, issues))


def propositions_mecaniques(description, developpement, nombre, crete=1.0, score_minimum=0.0):
    """Meilleures lois de la grammaire ajustées sur la partie de développement (vraisemblance pénalisée de Schwarz,
    rapportée à la marginale du développement) ; au plus une par (moniteur, traits, forme) ; seulement celles qui battent
    la marginale après pénalité."""
    from . import selection_pari as sp
    from .monde_banque import ajuster_softmax
    d = len(description["traits"])
    candidats = []
    for moniteur in sorted(description["moniteurs"]):
        k = description["moniteurs"][moniteur]["nombre_issues"]
        lignes = [l for l in developpement["instances"] if moniteur in l["issues"]]
        if len(lignes) < 5 * k:
            continue
        n = len(lignes)
        instances = [{"z": l["z"], "g": l["g"]} for l in lignes]
        issues = [int(l["issues"][moniteur]) for l in lignes]
        frequences = [(issues.count(c) + 0.5) / (n + 0.5 * k) for c in range(k)]
        base = sum(math.log(frequences[y]) for y in issues)
        sous_ensembles = [(t,) for t in range(d)] + list(itertools.combinations(range(d), 2))
        for traits in sous_ensembles:
            for forme in FORMES:
                loi, nb_parametres = _ajuster_forme(forme, traits, instances, issues, k, d, crete, ajuster_softmax)
                if loi is None:
                    continue
                gain = _log_vraisemblance(loi, instances, issues, sp.proba) - base
                score = gain - 0.5 * nb_parametres * math.log(n)
                if score > score_minimum:  # v16 : `score_minimum` réglable (témoins faux par permutation : sans filtre)
                    candidats.append((score, moniteur, traits, forme, loi))
    candidats.sort(key=lambda c: (-c[0], c[1], c[2], c[3]))
    sortie = []
    for score, moniteur, traits, forme, loi in candidats[:nombre]:
        noms = ", ".join(description["traits"][t] for t in traits)
        sortie.append({"enonce": f"Référence mécanique : l'issue du moniteur {moniteur} dépend de {noms} (forme {forme}, "
                                 f"ajustée sur le développement, gain pénalisé {score:.2f} nat)",
                       "strategie": "mecanique_sur_developpement", "moniteur": moniteur, "loi_predictive": loi})
    return sortie


def _ajuster_forme(forme, traits, instances, issues, k, d, crete, ajuster_softmax):
    """(loi au gabarit, nombre de paramètres) ou (None, 0) si les données manquent."""
    def ajuste(sous_inst, sous_issues):
        if len(sous_issues) < 3 * k:
            return None
        zs = [[inst["z"][t] for t in traits] for inst in sous_inst]
        l = ajuster_softmax(zs, sous_issues, k, crete)
        return _softmax_sur(traits, l["poids"], k, d, l["biais"])

    p = k * (len(traits) + 1)
    if forme == "softmax":
        loi = ajuste(instances, issues)
        return (loi, p) if loi else (None, 0)
    if forme == "par_sous_population":
        lois = {}
        for g in sorted({inst["g"] for inst in instances}):
            sel = [i for i, inst in enumerate(instances) if inst["g"] == g]
            l = ajuste([instances[i] for i in sel], [issues[i] for i in sel])
            if l is None:
                return None, 0
            lois[str(g)] = l
        if len(lois) < 2:
            return None, 0
        # v11 (contre-lecture C10) : loi par défaut (la marginale ajustée sur tout le développement) pour une
        # sous-population absente du développement mais présente à l'épreuve ; sans elle, l'évaluation levait TypeError.
        defaut = ajuste(instances, issues)
        return {"type": "par_sous_population", "lois": lois, "defaut": defaut}, p * len(lois)
    if forme == "si_sinon":
        if len(traits) != 2:
            return None, 0
        j = traits[1]
        haut = [i for i, inst in enumerate(instances) if inst["z"][j] > 0.0]
        bas = [i for i, inst in enumerate(instances) if inst["z"][j] <= 0.0]
        si = ajuste([instances[i] for i in haut], [issues[i] for i in haut])
        sinon = ajuste([instances[i] for i in bas], [issues[i] for i in bas])
        if si is None or sinon is None:
            return None, 0
        return {"type": "si_sinon", "condition": {"indice": j, "seuil": 0.0}, "si": si, "sinon": sinon}, 2 * p
    raise ValueError(forme)
