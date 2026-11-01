"""Sélection par pari (tests par pari, e-processus) — l'évaluateur est du code de l'orchestrateur, hors des agents.

Une fiche engage une loi prédictive p_h sur K issues. Le nul est composite : une bibliothèque 𝓛 de prédicteurs aveugles
au domaine (ils ne voient que l'historique des issues, jamais les traits des instances). La richesse est

    W_t = Π_{s≤t} p_h(x_s) / max_{q∈𝓛} Π_{s≤t} q(x_s),

calculée sur des tirages frais, tirés après l'engagement (leur graine dérive de l'empreinte de l'engagement).

Choix documenté (inférence universelle) : le dénominateur est le **maximum de vraisemblance a posteriori sur 𝓛, ajusté
sur les tirages frais eux-mêmes** (pour la marginale : les fréquences des tirages ; pour les moyennes glissantes : la
meilleure fenêtre). La loi p_h, écrite avant les tirages, tient lieu de numérateur ajusté sur une part séparée. Validité :
si les issues suivent une loi q* de 𝓛, alors W_t ≤ Π p_h/Π q* à tout t, martingale positive d'espérance 1 sous q* ;
l'inégalité de Ville donne P(sup_t W_t ≥ 1/α) ≤ α : la promotion peut être lue à tout instant (« continu »).
Les deux autres ajustements (sur une part séparée d'entraînement, ou en ligne) sont gardés comme variantes à éprouver :
le contrôle T6 montre qu'ils laissent passer un parasite de Kelly.

Juge v1 (dossier `orchestrateur-pole-v2`, note de conception `conception-experience-1-juge-v1.md`) = juge v0 + **ordre
d'exécution secret** + membre **« urne »** dans 𝓛 (`BIBLIOTHEQUE_STANDARD_V1`). Le noyau tire une permutation π après le
gel (graine maîtresse du noyau, jamais dans la vue d'un agent, et empreinte de l'engagement) ; le monde traite au temps s
l'instance π[s] du plan ; chaque issue est rangée à l'indice de son instance ; l'évaluation suit l'ordre du plan. Sous le
nul « issues indépendantes des traits », quelle que soit la structure temporelle (dérive, rupture, autocorrélation,
calendrier), la suite des issues dans l'ordre du plan est échangeable et indépendante des traits ; l'urne vaut, à chaque
instant, le maximum sur les lois échangeables de la probabilité des t premières issues, Π_k c_k(t)! / t! ; elle domine
donc la loi vraie et W_t reste sous une martingale positive d'espérance 1 : Ville borne la promotion par α, sans modéliser
la dérive. L'évaluateur refuse des issues produites sous un autre plan d'exécution que celui de l'engagement, et, sous
l'ordre secret, des issues dont l'empreinte d'ordre n'est pas celle que le noyau recalcule.
"""

import collections
import copy
import math
import random

from .outils import empreinte_objet, graine_derivee, nombre_fini

PLANCHER = 1e-12
BIBLIOTHEQUE_STANDARD = (
    {"nom": "marginale_empirique", "type": "marginale_mv"},
    {"nom": "uniforme", "type": "uniforme"},
    {"nom": "moyenne_glissante", "type": "moyennes_glissantes", "fenetres": [5, 10, 20, 50], "lissage": 0.5},
)
# Juge v1 : les membres de v0, inchangés, plus l'urne (maximum sur les lois échangeables).
BIBLIOTHEQUE_STANDARD_V1 = BIBLIOTHEQUE_STANDARD + ({"nom": "urne", "type": "urne"},)
TYPES_LOI = ("fixe", "softmax", "par_sous_population", "melange", "si_sinon", "moyenne_glissante", "derive_lineaire",
             "echelle", "enveloppe", "calendrier", "deterministe", "sans_remise", "transformee")
# v7, version 6 (banc de tricheurs) : « transformee » = transformation aveugle d'une loi de base, étapes facultatives dans
# cet ordre : mélange à une loi aveugle fixe (λ, b) ; puissance γ (température) ; inclinaison par issue (β_k) ; oscillation
# non monotone p_k ← p_k·exp(η·cos(ω·z_j + φ)) sur une issue k. Elle sert à écrire les tricheurs T05 à T09 et T12 ; le
# gabarit du proposeur ne la permet pas.
# Plans d'exécution : « ordre_naturel » (v0 : l'instance d'indice t du plan est traitée au temps t) ; « ordre_secret »
# (v1 : permutation tirée par le noyau après le gel). Sous l'ordre secret, une instance ne porte que ses traits « z » et
# sa sous-population « g » : l'heure d'exécution n'est jamais un trait d'instance.
PLANS_EXECUTION = ("ordre_naturel", "ordre_secret")
CLES_INSTANCE_ORDRE_SECRET = frozenset({"z", "g"})


TYPES_LISANT_L_HISTORIQUE = ("sans_remise", "moyenne_glissante")


def types_de_la_loi(loi):
    """Ensemble des types présents dans une loi composée (parcours des sous-lois : lois, composantes, si, sinon, loi, base)."""
    if not isinstance(loi, dict):
        return set()
    types = {loi.get("type")} if loi.get("type") else set()
    for cle in ("si", "sinon", "loi", "base", "defaut"):
        types |= types_de_la_loi(loi.get(cle))
    for cle in ("lois", "composantes"):
        sous = loi.get(cle)
        if isinstance(sous, dict):
            for s in sous.values():
                types |= types_de_la_loi(s)
        elif isinstance(sous, (list, tuple)):
            for s in sous:
                types |= types_de_la_loi(s)
    return types


class LoiInvalide(ValueError):
    pass


class EngagementModifie(RuntimeError):
    """Le test (loi, bibliothèque, seuil, plan) a changé après son gel : évaluation refusée."""


class TiragesNonLies(RuntimeError):
    """Les tirages ne sont pas liés à cet engagement (tirés avant, ou pour un autre test) : évaluation refusée."""


class PlanExecutionNonConforme(TiragesNonLies):
    """Issues produites sous un autre plan d'exécution que celui de l'engagement, ou sous un ordre que le noyau ne
    retrouve pas : évaluation refusée."""


# --- lois prédictives -----------------------------------------------------------------------------------------
def _normaliser(p):
    p = [max(PLANCHER, float(x)) for x in p]
    s = sum(p)
    return [x / s for x in p]


def _condition(condition, instance):
    if "sous_population" in condition:
        return instance.get("g") == condition["sous_population"]
    return instance["z"][condition["indice"]] > condition.get("seuil", 0.0)


def proba(loi, instance, historique, t):
    """Loi prédictive de l'issue t (indice à partir de 0), sachant l'instance et les issues historique[:t]."""
    genre = loi["type"]
    if genre == "fixe":
        return _normaliser(loi["probas"])
    if genre == "softmax":
        z = instance["z"]
        scores = [b + sum(w * x for w, x in zip(ligne, z)) for ligne, b in zip(loi["poids"], loi["biais"])]
        m = max(scores)
        return _normaliser([math.exp(s - m) for s in scores])
    if genre == "par_sous_population":
        sous_loi = loi["lois"].get(str(instance.get("g")), loi.get("defaut"))
        return proba(sous_loi, instance, historique, t)
    if genre == "melange":
        mix = [0.0] * len(proba(loi["composantes"][0], instance, historique, t))
        for poids, composante in zip(loi["poids"], loi["composantes"]):
            for k, p in enumerate(proba(composante, instance, historique, t)):
                mix[k] += poids * p
        return _normaliser(mix)
    if genre == "si_sinon":
        branche = loi["si"] if _condition(loi["condition"], instance) else loi["sinon"]
        return proba(branche, instance, historique, t)
    if genre == "moyenne_glissante":
        k, w, lam = loi["nombre_issues"], loi["fenetre"], loi["lissage"]
        recents = historique[max(0, t - w):t]
        compte = collections.Counter(recents)
        return _normaliser([(compte[i] + lam) / (len(recents) + k * lam) for i in range(k)])
    if genre == "enveloppe":
        tables = [proba(l, instance, historique, t) for l in loi["lois"]]
        return _normaliser([max(table[k] for table in tables) for k in range(len(tables[0]))])
    if genre == "echelle":
        reechelonnee = dict(instance, z=[x / f for x, f in zip(instance["z"], loi["facteurs"])])
        return proba(loi["loi"], reechelonnee, historique, t)
    if genre == "derive_lineaire":
        s = min(1.0, t / max(1, loi["horizon"] - 1))
        return _normaliser([(1 - s) * a + s * b for a, b in zip(loi["debut"], loi["fin"])])
    if genre == "calendrier":
        # Un vecteur de probabilités par instant t (indice de l'appel : le temps pour un monde, l'indice du plan pour une
        # loi prédictive), fixé d'avance.
        if not 0 <= t < len(loi["probas"]):
            raise LoiInvalide(f"calendrier : aucun vecteur pour l'instant {t} (longueur {len(loi['probas'])})")
        return _normaliser(loi["probas"][t])
    if genre == "deterministe":
        # Issue fixée d'avance pour chaque instant (calendrier déterministe), au plancher près.
        if not 0 <= t < len(loi["issues"]):
            raise LoiInvalide(f"deterministe : aucune issue pour l'instant {t} (longueur {len(loi['issues'])})")
        return _normaliser([1.0 if k == loi["issues"][t] else 0.0 for k in range(loi["nombre_issues"])])
    if genre == "sans_remise":
        # Composition déclarée c ; prédiction « sans remise » : p_k ∝ c_k − (issues k déjà vues), plancher.
        vus = collections.Counter(historique[:t])
        return _normaliser([max(0, c - vus[k]) for k, c in enumerate(loi["composition"])])
    if genre == "transformee":
        p = proba(loi["base"], instance, historique, t)
        if loi.get("melange_aveugle"):
            lam, b = loi["melange_aveugle"]["lambda"], _normaliser(loi["melange_aveugle"]["probas"])
            p = [(1 - lam) * x + lam * y for x, y in zip(p, b)]
        if loi.get("puissance") is not None:
            p = _normaliser([max(x, PLANCHER) ** loi["puissance"] for x in p])
        if loi.get("inclinaison"):
            p = _normaliser([x * math.exp(beta) for x, beta in zip(p, loi["inclinaison"])])
        if loi.get("oscillation"):
            o = loi["oscillation"]
            facteur = math.exp(o["amplitude"] * math.cos(o["frequence"] * instance["z"][o["trait"]] + o.get("phase", 0.0)))
            p = _normaliser([x * facteur if k == o["issue"] else x for k, x in enumerate(p)])
        return _normaliser(p)
    raise LoiInvalide(f"type de loi inconnu : {genre!r}")


def valider_loi(loi, nombre_issues, dimension=None):
    """Lève LoiInvalide si la spécification n'est pas une loi bien formée sur `nombre_issues` issues."""
    if not isinstance(loi, dict) or loi.get("type") not in TYPES_LOI:
        raise LoiInvalide(f"loi : objet avec un type parmi {TYPES_LOI}")
    genre = loi["type"]
    if genre == "fixe":
        p = loi.get("probas")
        if not isinstance(p, list) or len(p) != nombre_issues or not all(nombre_fini(x) and x >= 0 for x in p) or sum(p) <= 0:
            raise LoiInvalide("loi fixe : probas positives, une par issue")
    elif genre == "softmax":
        poids, biais = loi.get("poids"), loi.get("biais")
        if not isinstance(poids, list) or len(poids) != nombre_issues or not isinstance(biais, list) or len(biais) != nombre_issues:
            raise LoiInvalide("softmax : une ligne de poids et un biais par issue")
        largeurs = {len(l) if isinstance(l, list) else -1 for l in poids}
        if len(largeurs) != 1 or (dimension is not None and largeurs != {dimension}) or not all(
                nombre_fini(x) for l in poids for x in l) or not all(nombre_fini(b) for b in biais):
            raise LoiInvalide("softmax : poids et biais finis, de largeur égale à la dimension des instances")
    elif genre == "par_sous_population":
        if not isinstance(loi.get("lois"), dict) or not loi["lois"]:
            raise LoiInvalide("par_sous_population : objet « lois » non vide")
        for sous in list(loi["lois"].values()) + ([loi["defaut"]] if "defaut" in loi else []):
            valider_loi(sous, nombre_issues, dimension)
    elif genre == "melange":
        comp, poids = loi.get("composantes"), loi.get("poids")
        if not isinstance(comp, list) or not comp or not isinstance(poids, list) or len(poids) != len(comp) \
                or not all(nombre_fini(w) and w >= 0 for w in poids) or abs(sum(poids) - 1) > 1e-9:
            raise LoiInvalide("mélange : composantes et poids positifs de somme 1")
        for c in comp:
            valider_loi(c, nombre_issues, dimension)
    elif genre == "si_sinon":
        cond = loi.get("condition")
        if not isinstance(cond, dict) or not ("sous_population" in cond or "indice" in cond):
            raise LoiInvalide("si_sinon : condition sur la sous-population ou sur un trait")
        valider_loi(loi.get("si"), nombre_issues, dimension)
        valider_loi(loi.get("sinon"), nombre_issues, dimension)
    elif genre == "moyenne_glissante":
        if loi.get("nombre_issues") != nombre_issues or not isinstance(loi.get("fenetre"), int) or loi["fenetre"] < 1:
            raise LoiInvalide("moyenne_glissante : nombre_issues et fenêtre entière ≥ 1")
    elif genre == "enveloppe":
        if not isinstance(loi.get("lois"), list) or len(loi["lois"]) < 2:
            raise LoiInvalide("enveloppe : au moins deux lois")
        for l in loi["lois"]:
            valider_loi(l, nombre_issues, dimension)
    elif genre == "echelle":
        f = loi.get("facteurs")
        if not isinstance(f, list) or not all(nombre_fini(x) and x > 0 for x in f) or (dimension is not None and len(f) != dimension):
            raise LoiInvalide("echelle : un facteur strictement positif par trait")
        valider_loi(loi.get("loi"), nombre_issues, dimension)
    elif genre == "derive_lineaire":
        for cle in ("debut", "fin"):
            if not isinstance(loi.get(cle), list) or len(loi[cle]) != nombre_issues:
                raise LoiInvalide("derive_lineaire : debut et fin, une probabilité par issue")
        if not isinstance(loi.get("horizon"), int) or loi["horizon"] < 1:
            raise LoiInvalide("derive_lineaire : horizon entier ≥ 1")
    elif genre == "calendrier":
        p = loi.get("probas")
        if not isinstance(p, list) or not p or not all(
                isinstance(v, list) and len(v) == nombre_issues and all(nombre_fini(x) and x >= 0 for x in v) and sum(v) > 0
                for v in p):
            raise LoiInvalide("calendrier : liste non vide de vecteurs de probabilités, un par instant, une par issue")
    elif genre == "deterministe":
        issues = loi.get("issues")
        if loi.get("nombre_issues") != nombre_issues or not isinstance(issues, list) or not issues or not all(
                isinstance(x, int) and not isinstance(x, bool) and 0 <= x < nombre_issues for x in issues):
            raise LoiInvalide("deterministe : nombre_issues et liste non vide d'issues entières dans [0 ; K[")
    elif genre == "sans_remise":
        c = loi.get("composition")
        if not isinstance(c, list) or len(c) != nombre_issues or not all(
                isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in c) or sum(c) < 1:
            raise LoiInvalide("sans_remise : composition, un effectif entier ≥ 0 par issue, de somme ≥ 1")
    elif genre == "transformee":
        valider_loi(loi.get("base"), nombre_issues, dimension)
        m = loi.get("melange_aveugle")
        if m is not None and not (isinstance(m, dict) and nombre_fini(m.get("lambda")) and 0 <= m["lambda"] <= 1
                                  and isinstance(m.get("probas"), list) and len(m["probas"]) == nombre_issues
                                  and all(nombre_fini(x) and x >= 0 for x in m["probas"]) and sum(m["probas"]) > 0):
            raise LoiInvalide("transformee : melange_aveugle = {lambda dans [0 ; 1], probas, une par issue}")
        g = loi.get("puissance")
        if g is not None and not (nombre_fini(g) and g > 0):
            raise LoiInvalide("transformee : puissance finie strictement positive")
        b = loi.get("inclinaison")
        if b is not None and not (isinstance(b, list) and len(b) == nombre_issues and all(nombre_fini(x) for x in b)):
            raise LoiInvalide("transformee : inclinaison, un réel fini par issue")
        o = loi.get("oscillation")
        if o is not None and not (isinstance(o, dict) and all(nombre_fini(o.get(c)) for c in ("amplitude", "frequence"))
                                  and isinstance(o.get("trait"), int) and isinstance(o.get("issue"), int)
                                  and 0 <= o["issue"] < nombre_issues and nombre_fini(o.get("phase", 0.0))
                                  and (dimension is None or 0 <= o["trait"] < dimension)):
            raise LoiInvalide("transformee : oscillation = {amplitude, frequence, trait, issue, phase facultative}")
    return loi


def tirer_categorie(rng, p):
    u, cumul = rng.random(), 0.0
    for k, pk in enumerate(p):
        cumul += pk
        if u < cumul:
            return k
    return len(p) - 1


def tirer_instances(rng, nombre, dimension=2, sous_populations=2):
    return [{"z": [round(rng.gauss(0.0, 1.0), 6) for _ in range(dimension)], "g": rng.randrange(sous_populations)}
            for _ in range(nombre)]


def loi_softmax_aleatoire(rng, nombre_issues=3, dimension=2, force=1.5):
    return {"type": "softmax",
            "poids": [[round(rng.gauss(0.0, force), 6) for _ in range(dimension)] for _ in range(nombre_issues)],
            "biais": [round(rng.gauss(0.0, 0.3), 6) for _ in range(nombre_issues)]}


def moyenne_loi(loi, instances):
    """Marginale moyenne de p_h sur des instances : le nul le plus trompeur (mêmes fréquences, aucun lien aux traits)."""
    total = None
    for t, inst in enumerate(instances):
        p = proba(loi, inst, [], t)
        total = p if total is None else [a + b for a, b in zip(total, p)]
    return [round(x / len(instances), 9) for x in total]


def divergence(p, q):
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q) if pi > 0)


# --- bibliothèque 𝓛 : trajectoires de log-vraisemblance (maximum a posteriori sur chaque famille) ------------------
def _traj_marginale_mv(issues, k):
    compte, sortie = [0] * k, []
    for t, x in enumerate(issues, 1):
        compte[x] += 1
        sortie.append(sum(c * math.log(c / t) for c in compte if c))
    return sortie


def _traj_cumulee(logs):
    cumul, sortie = 0.0, []
    for v in logs:
        cumul += v
        sortie.append(cumul)
    return sortie


def _traj_moyennes_glissantes(issues, k, fenetres, lissage):
    meilleure = None
    for w in fenetres:
        compte, file, cumul, sortie = [0] * k, collections.deque(), 0.0, []
        for x in issues:
            cumul += math.log((compte[x] + lissage) / (len(file) + k * lissage))
            sortie.append(cumul)
            file.append(x)
            compte[x] += 1
            if len(file) > w:
                compte[file.popleft()] -= 1
        meilleure = sortie if meilleure is None else [max(a, b) for a, b in zip(meilleure, sortie)]
    return meilleure


def _traj_urne(issues, k):
    """Urne : ln max_{Q échangeable} Q(x_1..x_t) = Σ_k ln c_k(t)! − ln t!, pour t = 1..n (math.lgamma).

    Toute loi échangeable donne la même probabilité aux t!/Π_k c_k(t)! suites de même composition ; la composition
    observée a une probabilité ≤ 1 : d'où la borne, atteinte par l'urne sans remise de composition c(t). Les lois
    indépendantes et identiquement distribuées étant échangeables, l'urne domine aussi la marginale ajustée.
    """
    compte, sortie = [0] * k, []
    for t, x in enumerate(issues, 1):
        compte[x] += 1
        sortie.append(sum(math.lgamma(c + 1) for c in compte) - math.lgamma(t + 1))
    return sortie


def _traj_marginale_en_ligne(issues, k, lissage):
    compte, logs = [0] * k, []
    for t, x in enumerate(issues):
        logs.append(math.log((compte[x] + lissage) / (t + k * lissage)))
        compte[x] += 1
    return _traj_cumulee(logs)


class Cache:
    """Probabilités par pas de chaque loi (calculées une fois par évaluation)."""

    def __init__(self, issues, instances):
        self.issues, self.instances, self._lois = issues, instances, {}

    def probas(self, loi):
        cle = empreinte_objet(loi)
        if cle not in self._lois:
            self._lois[cle] = [proba(loi, self.instances[t], self.issues, t) for t in range(len(self.issues))]
        return self._lois[cle]


def trajectoire_loi(loi, issues, instances, cache=None):
    cache = cache or Cache(issues, instances)
    return _traj_cumulee([math.log(p[x]) for p, x in zip(cache.probas(loi), issues)])


GRILLE_FRACTIONS = (0.25, 0.5, 0.75, 1.0)


def trajectoire_numerateur(engagement, issues, instances, cache=None):
    """Numérateur de la richesse. Sans `fractions` : la vraisemblance de la loi engagée (pari plein, v0 à v6). Avec
    `fractions` (v7, pari à fraction) : la vraisemblance du **mélange bayésien** sur la grille des fractions λ (a priori
    uniforme) des lois prédictives λ·p_h + (1 − λ)·m_t, où m_t est la marginale en ligne (Laplace 0,5) des issues
    précédentes du plan — une suite prévisible : le rapport à tout membre du nul reste une martingale de test sous ce
    membre (inférence universelle), donc la garantie de Ville tient. Gain : une loi juste mais trop confiante ne se ruine
    plus sur les issues qu'elle croyait improbables ; prix : au plus log(nombre de fractions) contre la meilleure fraction."""
    cache = cache or Cache(issues, instances)
    fractions = engagement.get("fractions")
    if not fractions:
        return trajectoire_loi(engagement["loi"], issues, instances, cache)
    k = engagement["nombre_issues"]
    p = cache.probas(engagement["loi"])
    compte, cumuls, traj = [0] * k, [0.0] * len(fractions), []
    for t, x in enumerate(issues):
        m = (compte[x] + 0.5) / (t + 0.5 * k)
        for i, lam in enumerate(fractions):
            cumuls[i] += math.log(max(PLANCHER, lam * p[t][x] + (1.0 - lam) * m))
        compte[x] += 1
        haut = max(cumuls)
        traj.append(haut + math.log(sum(math.exp(c - haut) for c in cumuls) / len(fractions)))
    return traj


def _traj_melange(membre, issues, cache):
    pa, pb = (cache.probas(l) for l in membre["lois"])
    meilleure = None
    for w in sorted(set(membre["grille"])):
        traj = _traj_cumulee([math.log(max(PLANCHER, w * a[x] + (1 - w) * b[x])) for a, b, x in zip(pa, pb, issues)])
        meilleure = traj if meilleure is None else [max(u, v) for u, v in zip(meilleure, traj)]
    return meilleure


def _traj_enveloppe(membre, issues, cache):
    tables = [cache.probas(l) for l in membre["lois"]]
    logs = []
    for t, x in enumerate(issues):
        m = [max(table[t][k] for table in tables) for k in range(len(tables[0][t]))]
        logs.append(math.log(m[x] / sum(m)))
    return _traj_cumulee(logs)


def trajectoire_membre(membre, issues, instances, k, cache=None):
    genre = membre["type"]
    cache = cache or Cache(issues, instances)
    if genre == "marginale_mv":
        return _traj_marginale_mv(issues, k)
    if genre == "uniforme":
        return [-t * math.log(k) for t in range(1, len(issues) + 1)]
    if genre == "moyennes_glissantes":
        return _traj_moyennes_glissantes(issues, k, membre["fenetres"], membre.get("lissage", 0.5))
    if genre == "marginale_en_ligne":
        return _traj_marginale_en_ligne(issues, k, membre.get("lissage", 0.5))
    if genre == "urne":
        return _traj_urne(issues, k)
    if genre == "fixe":
        p = _normaliser(membre["probas"])
        return _traj_cumulee([math.log(p[x]) for x in issues])
    if genre == "loi":
        return trajectoire_loi(membre["loi"], issues, instances, cache)
    if genre == "melange_lois":
        return _traj_melange(membre, issues, cache)
    if genre == "enveloppe_harmonique":
        return _traj_enveloppe(membre, issues, cache)
    raise LoiInvalide(f"membre de bibliothèque inconnu : {genre!r}")


def trajectoires(bibliotheque, issues, instances, k, cache=None):
    cache = cache or Cache(issues, instances)
    return {m["nom"]: trajectoire_membre(m, issues, instances, k, cache) for m in bibliotheque}


def trajectoire_denominateur(bibliotheque, issues, instances, k, cache=None, deja=None):
    par_membre = deja or trajectoires(bibliotheque, issues, instances, k, cache)
    meilleure, dominant = None, None
    for nom, traj in par_membre.items():
        if meilleure is None:
            meilleure, dominant = list(traj), [nom] * len(traj)
            continue
        for t, v in enumerate(traj):
            if v > meilleure[t]:
                meilleure[t], dominant[t] = v, nom
    return meilleure, dominant


# --- engagement, gel, tirages frais, évaluation ------------------------------------------------------------------
def construire_engagement(identifiant, loi, instances, nombre_issues=3, alpha=0.05, bibliotheque=BIBLIOTHEQUE_STANDARD,
                          mode="continu", empreinte_fiche=None, part_calibrage=0, delta0=None,
                          plan_execution="ordre_naturel"):
    """Engagement à geler. `plan_execution` (déclaré dans l'engagement, donc sous son empreinte) : « ordre_naturel »
    (v0) ou « ordre_secret » (v1 : le noyau tire l'ordre d'exécution après le gel ; voir `ordre_execution`)."""
    if not (nombre_fini(alpha) and 0 < alpha < 1):
        raise ValueError("alpha dans ]0 ; 1[")
    if mode not in ("continu", "horizon"):
        raise ValueError("mode : « continu » (lecture à tout instant, Ville) ou « horizon »")
    if not instances or not (isinstance(part_calibrage, int) and 0 <= part_calibrage < len(instances)):
        raise ValueError("plan d'instances vide, ou part de calibrage hors du plan")
    if delta0 is not None and not (nombre_fini(delta0) and delta0 >= 0):
        raise ValueError("delta0 : nombre fini positif ou nul")
    if plan_execution not in PLANS_EXECUTION:
        raise ValueError(f"plan d'exécution : un parmi {PLANS_EXECUTION}")
    if plan_execution == "ordre_secret":
        for instance in instances:
            if not isinstance(instance, dict) or not set(instance) <= CLES_INSTANCE_ORDRE_SECRET or "z" not in instance:
                raise ValueError("ordre secret : une instance ne porte que « z » (traits) et « g » (sous-population) ; "
                                 "l'heure d'exécution n'est jamais un trait d'instance")
    noms = [m["nom"] for m in bibliotheque]
    if len(set(noms)) != len(noms):
        raise ValueError("noms de membres de bibliothèque en double")
    dimension = len(instances[0]["z"])
    valider_loi(loi, nombre_issues, dimension)
    for membre in bibliotheque:
        for l in ([membre["loi"]] if membre.get("type") == "loi" else membre.get("lois", [])):
            valider_loi(l, nombre_issues, dimension)
    return {"identifiant": identifiant, "loi": copy.deepcopy(loi), "bibliotheque": copy.deepcopy(list(bibliotheque)),
            "alpha": alpha, "seuil_richesse": 1.0 / alpha, "instances": copy.deepcopy(instances),
            "nombre_issues": nombre_issues, "mode": mode, "empreinte_fiche": empreinte_fiche,
            "part_calibrage": part_calibrage, "delta0": delta0, "plan_execution": plan_execution}


class EngagementGele:
    def __init__(self, engagement):
        self.engagement = copy.deepcopy(engagement)
        self.empreinte = empreinte_objet(self.engagement)


def geler_engagement(engagement):
    return EngagementGele(engagement)


def plan_execution_de(engagement):
    """Plan d'exécution déclaré par un engagement (absent : « ordre_naturel », comportement de v0)."""
    return engagement.get("plan_execution", "ordre_naturel")


def ordre_execution(graine_noyau, empreinte_engagement, nombre):
    """Permutation π tirée par le noyau après le gel : au temps s, le monde traite l'instance d'indice π[s] du plan.

    Sa graine dérive de la graine maîtresse du noyau (jamais dans la vue d'un agent) et de l'empreinte de l'engagement
    gelé : π n'existe pas avant le gel, et le noyau la recalcule pour vérifier les tirages.
    """
    if graine_noyau is None:
        raise PlanExecutionNonConforme("ordre secret : la graine du noyau est requise pour tirer ou recalculer l'ordre")
    pi = list(range(nombre))
    random.Random(graine_derivee(graine_noyau, "ordre-execution", empreinte_engagement)).shuffle(pi)
    return pi


def tirer_frais(gele, loi_monde, graine, graine_noyau=None):
    """Tirages frais, liés à l'engagement : leur graine dérive de son empreinte, ils n'existent pas avant le gel.

    Ordre naturel (v0) : l'instance t est traitée au temps t. Ordre secret (v1) : le monde voit, au temps s, l'instance
    π[s], son propre passé dans l'ordre du temps et s ; l'issue est rangée à l'indice π[s] du plan ; l'empreinte de π est
    consignée (le noyau la recalcule à l'évaluation).
    """
    rng = random.Random(graine_derivee(graine, "tirages-frais", gele.empreinte))
    instances = gele.engagement["instances"]
    plan = plan_execution_de(gele.engagement)
    if plan == "ordre_naturel":
        issues = []
        for t, instance in enumerate(instances):
            issues.append(_issue_monde(rng, loi_monde, instance, issues, t))
        return {"empreinte_engagement": gele.empreinte, "issues": issues, "plan_execution": plan}
    pi = ordre_execution(graine_noyau, gele.empreinte, len(instances))
    dans_le_temps, issues = [], [None] * len(instances)
    for s, i in enumerate(pi):
        y = _issue_monde(rng, loi_monde, instances[i], dans_le_temps, s)
        dans_le_temps.append(y)
        issues[i] = y
    return {"empreinte_engagement": gele.empreinte, "issues": issues, "plan_execution": plan,
            "empreinte_ordre": empreinte_objet(pi)}


def tirer_frais_selon_ordre(gele, loi_monde, graine, ordre):
    """Comme `tirer_frais` sous l'ordre secret, l'ordre étant fourni par le noyau (fichier `ordre-execution.json` du
    dossier de l'expérience, écrit après le gel) au lieu de sa graine : c'est ce que voit un expérimentateur. Le noyau
    recalcule l'ordre à l'évaluation (`verifier_plan_execution`) : un ordre faux est refusé."""
    instances = gele.engagement["instances"]
    if plan_execution_de(gele.engagement) != "ordre_secret":
        raise PlanExecutionNonConforme("ordre fourni pour un engagement qui n'est pas sous l'ordre secret")
    if sorted(ordre) != list(range(len(instances))):
        raise PlanExecutionNonConforme("l'ordre fourni n'est pas une permutation du plan")
    rng = random.Random(graine_derivee(graine, "tirages-frais", gele.empreinte))
    dans_le_temps, issues = [], [None] * len(instances)
    for s, i in enumerate(ordre):
        y = _issue_monde(rng, loi_monde, instances[i], dans_le_temps, s)
        dans_le_temps.append(y)
        issues[i] = y
    return {"empreinte_engagement": gele.empreinte, "issues": issues, "plan_execution": "ordre_secret",
            "empreinte_ordre": empreinte_objet(list(ordre))}


def _issue_monde(rng, loi_monde, instance, passe, s):
    """Issue du monde au temps s. Un monde « deterministe » rend exactement son issue fixée (pas de tirage au plancher)."""
    if loi_monde.get("type") == "deterministe":
        if not 0 <= s < len(loi_monde["issues"]):
            raise LoiInvalide(f"monde deterministe : aucune issue pour l'instant {s}")
        return loi_monde["issues"][s]
    return tirer_categorie(rng, proba(loi_monde, instance, passe, s))


def verifier_plan_execution(gele, tirages, graine_noyau=None):
    """Garde du plan d'exécution (R5 : essayée sur un cas sain et sur des artefacts, `essais/test_juge_v1.py`).

    Refuse : un plan déclaré par les tirages différent de celui de l'engagement ; sous l'ordre secret, l'absence de
    graine du noyau, ou une empreinte d'ordre différente de celle de la permutation que le noyau recalcule.
    """
    plan = plan_execution_de(gele.engagement)
    declare = tirages.get("plan_execution", "ordre_naturel")
    if declare != plan:
        raise PlanExecutionNonConforme(f"issues produites sous le plan {declare!r}, engagement sous le plan {plan!r}")
    if plan == "ordre_secret":
        attendue = empreinte_objet(ordre_execution(graine_noyau, gele.empreinte, len(gele.engagement["instances"])))
        if tirages.get("empreinte_ordre") != attendue:
            raise PlanExecutionNonConforme("ordre secret : l'empreinte d'ordre des tirages n'est pas celle du noyau")


def calibrer(bibliotheque, issues, instances):
    """Poids des mélanges marqués « calibrer » ajusté sur la part de calibrage, ajouté à leur grille."""
    sortie = []
    for membre in bibliotheque:
        membre = copy.deepcopy(membre)
        if membre.get("type") == "melange_lois" and membre.get("calibrer") and issues:
            cache = Cache(issues, instances)
            pa, pb = (cache.probas(l) for l in membre["lois"])
            meilleur = max(sorted(set(membre["grille"])), key=lambda w: sum(
                math.log(max(PLANCHER, w * a[x] + (1 - w) * b[x])) for a, b, x in zip(pa, pb, issues)))
            membre["poids_calibre"] = meilleur
            membre["grille"] = sorted(set(membre["grille"]) | {meilleur})
        sortie.append(membre)
    return sortie


def evaluer(gele, tirages, graine_noyau=None):
    """Richesse et promotion, calculées par l'orchestrateur à partir du test gelé et de tirages liés.

    Fille (bibliothèque avec enveloppes et `delta0`) : promotion si W ≥ 1/α **et** si le gain moyen de score
    logarithmique sur la part d'évaluation dépasse celui de la meilleure enveloppe d'au moins 2·delta0.
    Ordre secret : `graine_noyau` est la graine maîtresse du noyau, qui recalcule l'ordre d'exécution (garde du plan).
    """
    if empreinte_objet(gele.engagement) != gele.empreinte:
        raise EngagementModifie("le test a changé depuis son gel")
    if not isinstance(tirages, dict) or tirages.get("empreinte_engagement") != gele.empreinte:
        raise TiragesNonLies("tirages sans lien avec l'empreinte de cet engagement")
    verifier_plan_execution(gele, tirages, graine_noyau)
    e = gele.engagement
    k, instances, issues = e["nombre_issues"], e["instances"], tirages.get("issues")
    if not isinstance(issues, list) or len(issues) != len(instances) or not all(
            isinstance(x, int) and not isinstance(x, bool) and 0 <= x < k for x in issues):
        raise TiragesNonLies("issues absentes, mal formées ou en nombre différent du plan gelé")
    c = e.get("part_calibrage", 0)
    bibliotheque = calibrer(e["bibliotheque"], issues[:c], instances[:c])
    issues, instances = issues[c:], instances[c:]
    cache = Cache(issues, instances)
    numerateur = trajectoire_numerateur(e, issues, instances, cache)
    par_membre = trajectoires(bibliotheque, issues, instances, k, cache)
    denominateur, dominant = trajectoire_denominateur(bibliotheque, issues, instances, k, deja=par_membre)
    log_w = [a - b for a, b in zip(numerateur, denominateur)]
    seuil = math.log(1.0 / e["alpha"])
    t_promotion = next((t + 1 for t, v in enumerate(log_w) if v >= seuil), None)
    promue = t_promotion is not None if e["mode"] == "continu" else log_w[-1] >= seuil
    resultat = {"log_richesse_finale": log_w[-1], "log_richesse_max": max(log_w), "seuil_log": seuil,
                "log_richesse_arretee": log_w[t_promotion - 1] if t_promotion else log_w[-1],
                "trajectoire_log_w": [round(v, 6) for v in log_w],  # v7 : pour la règle e-BH (arrêt au seuil m/α)
                "t_promotion": t_promotion, "nombre_tirages": len(issues), "part_calibrage": c,
                "membre_dominant_final": dominant[-1], "mode": e["mode"], "empreinte_engagement": gele.empreinte,
                "plan_execution": plan_execution_de(e)}
    enveloppes = [m["nom"] for m in bibliotheque if m.get("enveloppe")]
    if e.get("delta0") is not None and enveloppes:
        meilleure = max(enveloppes, key=lambda n: par_membre[n][-1])
        gain = (numerateur[-1] - par_membre[meilleure][-1]) / len(issues)
        resultat.update(meilleure_enveloppe=meilleure, gain_moyen_sur_meilleure_enveloppe=gain,
                        marge_requise=2 * e["delta0"], marge_atteinte=gain >= 2 * e["delta0"])
        promue = promue and gain >= 2 * e["delta0"]
    resultat["promue"] = promue
    if not promue:
        resultat["t_promotion"] = None
    return resultat


# --- sélecteur mécanique ex ante (bras 1) et nul augmenté des filles ---------------------------------------------
def selection_divergence(loi, candidats, q_reference, nombre):
    """Les `nombre` instances où p_h s'écarte le plus (divergence de Kullback-Leibler) de la référence aveugle."""
    scores = [(divergence(proba(loi, c, [], 0), q_reference), i) for i, c in enumerate(candidats)]
    scores.sort(key=lambda s: (-s[0], s[1]))
    return [candidats[i] for _, i in scores[:nombre]]


GRILLE_MELANGE = [round(i / 20, 2) for i in range(21)]


def bibliotheque_fille(lois_parents, dimension, bibliotheque=BIBLIOTHEQUE_STANDARD, marginale_entrainement=None,
                       grille=GRILLE_MELANGE, nombre_issues=3):
    """Nul composite d'une fille : 𝓛, augmentée de ses parents et de leurs enveloppes (membres marqués « enveloppe »).

    Chaque parent seul ; le mélange des parents (poids : maximum a posteriori sur la grille, plus le poids ajusté sur la
    part de calibrage) ; l'enveloppe harmonique (en chaque issue le meilleur des parents, renormalisée) ; les
    concaténations si/sinon sur les partitions déclarées (sous-population, signe de chaque trait) ; chaque parent mélangé
    à une loi aveugle (uniforme, et marginale d'entraînement si fournie). Une fille qui n'est qu'une de ces formes est
    dans son propre nul : sa richesse reste ≤ 1.
    """
    membres = list(copy.deepcopy(bibliotheque))
    noms = sorted(lois_parents)
    for nom in noms:
        membres.append({"nom": f"parent:{nom}", "type": "loi", "loi": lois_parents[nom], "enveloppe": True})
        aveugles = [("uniforme", {"type": "fixe", "probas": [1.0] * nombre_issues})]
        if marginale_entrainement is not None:
            aveugles.append(("marginale_entrainement", {"type": "fixe", "probas": list(marginale_entrainement)}))
        for nom_a, aveugle in aveugles:
            membres.append({"nom": f"parent_couvert:{nom}|{nom_a}", "type": "melange_lois", "lois": [lois_parents[nom], aveugle],
                            "grille": list(grille), "enveloppe": True})
    if len(noms) == 2:
        la, lb = lois_parents[noms[0]], lois_parents[noms[1]]
        membres.append({"nom": "melange_parents", "type": "melange_lois", "lois": [la, lb], "grille": list(grille),
                        "calibrer": True, "enveloppe": True})
        membres.append({"nom": "enveloppe_harmonique", "type": "enveloppe_harmonique", "lois": [la, lb], "enveloppe": True})
        conditions = [{"sous_population": 0}] + [{"indice": j, "seuil": 0.0} for j in range(dimension)]
        for c in conditions:
            for (n1, l1), (n2, l2) in (((noms[0], la), (noms[1], lb)), ((noms[1], lb), (noms[0], la))):
                membres.append({"nom": f"si_sinon:{n1}|{n2}|{empreinte_objet(c)[:8]}", "type": "loi", "enveloppe": True,
                                "loi": {"type": "si_sinon", "condition": c, "si": l1, "sinon": l2}})
    return membres
