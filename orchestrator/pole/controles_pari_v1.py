"""Expérience 1 du pôle : valider le juge v1 avant le moteur — simulation à vérité connue, sur processeur (voie (c)).

Juge v1 = juge v0 + ordre d'exécution secret + membre « urne » (`selection_pari`, `BIBLIOTHEQUE_STANDARD_V1`). Trois juges
passent dans les mêmes scénarios (mêmes graines de scénario ; les tirages frais et l'ordre dérivent en plus de
l'empreinte de chaque engagement) :

- « v1 » : ordre secret, bibliothèque v0 + urne — le juge à valider ;
- « v0 » : ordre naturel, bibliothèque v0 — artefact de référence (la dérive non modélisée le trompe : T1b de v0) ;
- « v1_sans_urne » : ordre secret, bibliothèque v0 — artefact (une loi qui connaît la composition des issues le trompe).

Rôles des lignes du rapport (les critères sont dans `juger_v1`) :
- « fatal » (juge v1 ; taux de promotion ≤ α chacun) : T1a (trois nuls), T6, les sept tricheurs, T3 à composante nette
  fausse, T9, batterie T1b (lois aveugles « calendrier » et « composition » sous six structures absentes de 𝓛), T1b-fille,
  et un huitième tricheur ajouté après l'essai de fumée (déclaré) : « parent et loi aveugle » (parent mélangé à une loi
  aveugle fixe, sans dérive) ;
- « artefact requis » (taux > α, sinon le contrôle n'a pas de dents, R5) : juge v0 sous dérive linéaire (oracle
  « calendrier ») ; juge v1 sans urne sous calendrier déterministe (loi « composition ») ; permutation de l'ordre
  d'évaluation au lieu de l'ordre d'exécution (loi qui retrouve l'heure par l'instance) ; critères cassés de v0 rejoués sous
  l'ordre secret (𝓛 réduite à l'uniforme, dénominateur ajusté à part ou en ligne, filles sans parents dans le nul) ;
- « puissance décisive » (juge v1 ; taux ≥ 0,90) : fille réellement neuve ; T3 à composante nette vraie, ε = 0,2 ;
- « descriptif » : tout le reste (juge v0 et v1 sans urne sur toute la batterie, T1b-fille sous v0, puissances appariées).

Lecture en deux parties, plus l'issue globale de la note : le **socle** (fiches sans parents : T1a, T6, T3, batterie T1b
et leurs artefacts) et le **critère des filles** (tricheurs, fille neuve, filles sans parents dans le nul, T9, T1b-fille).

Chaque contrôle compte au moins 1 000 répétitions (sauf en mode `essai`, marqué non décisif) ; chaque répétition a ses
graines dérivées de la graine maîtresse (règle : `outils.graine_derivee`, étiquettes écrites au rapport).
"""

import collections
import math
import random
import statistics

from . import selection_pari as sp
from .controles_pari import (MONDES_FILLES, TRICHEURS, _dirichlet, _fixe, _frequences, _monde_fille, borne_wilson,
                             loi_tricheur)
from .outils import graine_derivee

GRAINE_EXPLORATION_V0 = 20261026  # graine de l'exploration de v0 : refusée pour l'expérience décisive
GRAINE_ESSAI_FUMEE = 777  # graine des essais de fumée et de l'exploration de conception (déclarés) : refusée aussi
# Graines refusées pour l'expérience décisive : exploration de v0, essais de fumée, graines des essais non décisifs du
# contre-lecteur cl1 (CJ1-16), graines des essais exploratoires « Boucle d'or » et mémoire du 27 octobre.
GRAINES_REFUSEES = (GRAINE_EXPLORATION_V0, GRAINE_ESSAI_FUMEE, 4242, 31337, 2718,
                    170141183460469231731687303715884204893, 20261027, 20261028)
REPETITIONS_DECISIVES = 1000
JUGES = {
    "v1": {"bibliotheque": sp.BIBLIOTHEQUE_STANDARD_V1, "plan_execution": "ordre_secret",
           "description": "ordre d'exécution secret ; bibliothèque v0 + urne (juge à valider)"},
    "v0": {"bibliotheque": sp.BIBLIOTHEQUE_STANDARD, "plan_execution": "ordre_naturel",
           "description": "ordre naturel ; bibliothèque v0 (artefact de référence)"},
    "v1_sans_urne": {"bibliotheque": sp.BIBLIOTHEQUE_STANDARD, "plan_execution": "ordre_secret",
                     "description": "ordre d'exécution secret ; bibliothèque v0 sans urne (artefact)"},
}
STRUCTURES = ("derive_lineaire", "rupture", "sinusoide", "marche_aleatoire", "calendrier_deterministe", "auto_excite")
LOIS_AVEUGLES = ("calendrier", "composition")
AMPLITUDE_SINUS, ECART_MARCHE, LONGUEUR_BLOC = 1.5, 0.15, 20
FENETRE_AUTO, LISSAGE_AUTO = 10, 0.1
LAMBDA_FILLE, LAMBDA_PUISSANCE = 0.5, 0.3
SEUIL_PUISSANCE, PERTE_PUISSANCE_PREDITE = 0.90, 0.05
# Les 70 couples (contrôle, juge) de l'expérience décisive (CJ1-02 ; identiques à l'annexe A du rapport cl1).
ROSTER_V1 = frozenset({
    ('T1a-nul-marginale', 'v1'),
    ('T1a-nul-moyenne_glissante', 'v1'),
    ('T1a-nul-uniforme', 'v1'),
    ('T1b-auto_excite-loi-calendrier', 'v0'),
    ('T1b-auto_excite-loi-calendrier', 'v1'),
    ('T1b-auto_excite-loi-calendrier', 'v1_sans_urne'),
    ('T1b-auto_excite-loi-composition', 'v0'),
    ('T1b-auto_excite-loi-composition', 'v1'),
    ('T1b-auto_excite-loi-composition', 'v1_sans_urne'),
    ('T1b-calendrier_deterministe-loi-calendrier', 'v0'),
    ('T1b-calendrier_deterministe-loi-calendrier', 'v1'),
    ('T1b-calendrier_deterministe-loi-calendrier', 'v1_sans_urne'),
    ('T1b-calendrier_deterministe-loi-composition', 'v0'),
    ('T1b-calendrier_deterministe-loi-composition', 'v1'),
    ('T1b-calendrier_deterministe-loi-composition', 'v1_sans_urne'),
    ('T1b-derive_lineaire-loi-calendrier', 'v0'),
    ('T1b-derive_lineaire-loi-calendrier', 'v1'),
    ('T1b-derive_lineaire-loi-calendrier', 'v1_sans_urne'),
    ('T1b-derive_lineaire-loi-composition', 'v0'),
    ('T1b-derive_lineaire-loi-composition', 'v1'),
    ('T1b-derive_lineaire-loi-composition', 'v1_sans_urne'),
    ('T1b-fille', 'v0'),
    ('T1b-fille', 'v1'),
    ('T1b-marche_aleatoire-loi-calendrier', 'v0'),
    ('T1b-marche_aleatoire-loi-calendrier', 'v1'),
    ('T1b-marche_aleatoire-loi-calendrier', 'v1_sans_urne'),
    ('T1b-marche_aleatoire-loi-composition', 'v0'),
    ('T1b-marche_aleatoire-loi-composition', 'v1'),
    ('T1b-marche_aleatoire-loi-composition', 'v1_sans_urne'),
    ('T1b-rupture-loi-calendrier', 'v0'),
    ('T1b-rupture-loi-calendrier', 'v1'),
    ('T1b-rupture-loi-calendrier', 'v1_sans_urne'),
    ('T1b-rupture-loi-composition', 'v0'),
    ('T1b-rupture-loi-composition', 'v1'),
    ('T1b-rupture-loi-composition', 'v1_sans_urne'),
    ('T1b-sinusoide-loi-calendrier', 'v0'),
    ('T1b-sinusoide-loi-calendrier', 'v1'),
    ('T1b-sinusoide-loi-calendrier', 'v1_sans_urne'),
    ('T1b-sinusoide-loi-composition', 'v0'),
    ('T1b-sinusoide-loi-composition', 'v1'),
    ('T1b-sinusoide-loi-composition', 'v1_sans_urne'),
    ('T3-couvert-eps0.05-net-faux', 'v1'),
    ('T3-couvert-eps0.05-net-vrai', 'v0'),
    ('T3-couvert-eps0.05-net-vrai', 'v1'),
    ('T3-couvert-eps0.2-net-faux', 'v1'),
    ('T3-couvert-eps0.2-net-vrai', 'v0'),
    ('T3-couvert-eps0.2-net-vrai', 'v1'),
    ('T6-parasite-de-Kelly', 'v1'),
    ('T9-disjonction-partitionnee', 'v1'),
    ('artefact-T1a-bibliotheque-uniforme-seule', 'v1'),
    ('artefact-T6-denominateur-en-ligne', 'v1'),
    ('artefact-T6-denominateur-part-separee', 'v1'),
    ('artefact-fille-sans-parents-dans-le-nul-enveloppe_aveugle', 'v1'),
    ('artefact-fille-sans-parents-dans-le-nul-forme', 'v1'),
    ('artefact-permutation-de-l-ordre-d-evaluation', 'v1_permutation_evaluation'),
    ('puissance-fille-neuve', 'v0'),
    ('puissance-fille-neuve', 'v1'),
    ('puissance-loi-de-domaine-vraie', 'v0'),
    ('puissance-loi-de-domaine-vraie', 'v1'),
    ('puissance-loi-vraie-plus-derive', 'v0'),
    ('puissance-loi-vraie-plus-derive', 'v1'),
    ('tricheur-adimensionnement', 'v1'),
    ('tricheur-copie_renommee', 'v1'),
    ('tricheur-enveloppe_aveugle', 'v1'),
    ('tricheur-fille_constante', 'v1'),
    ('tricheur-forme', 'v1'),
    ('tricheur-jargon_rare', 'v1'),
    ('tricheur-parent_et_loi_aveugle', 'v0'),
    ('tricheur-parent_et_loi_aveugle', 'v1'),
    ('tricheur-pari_couvert', 'v1'),
})
DESCRIPTION_STRUCTURES = {
    "derive_lineaire": "a = permutation tirée de (0,6 ; 0,3 ; 0,1) ; p_t va linéairement de a à a renversé sur les n instants",
    "rupture": "p_t = a pour t < n/2, a renversé ensuite",
    "sinusoide": f"logits_k(t) = {AMPLITUDE_SINUS}·sin(2πt/(n/3) + φ + 2πk/K), φ uniforme sur [0 ; 2π[",
    "marche_aleatoire": f"logits partis de 0, pas gaussiens indépendants d'écart {ECART_MARCHE} par composante et par instant",
    "calendrier_deterministe": f"blocs de {LONGUEUR_BLOC} instants, issues cycliques dans un ordre des catégories tiré",
    "auto_excite": f"moyenne glissante de fenêtre {FENETRE_AUTO}, lissage {LISSAGE_AUTO} (𝓛 n'a que le lissage 0,5)",
}


# --- mondes de la batterie T1b ------------------------------------------------------------------------------------
def _softmax(logits):
    m = max(logits)
    e = [math.exp(v - m) for v in logits]
    s = sum(e)
    return [x / s for x in e]


def _calendrier_derive_lineaire(rng, n):
    a = [0.6, 0.3, 0.1]
    rng.shuffle(a)
    b = list(reversed(a))
    probas = []
    for t in range(n):
        s = t / max(1, n - 1)
        probas.append([(1 - s) * x + s * y for x, y in zip(a, b)])
    return {"type": "calendrier", "probas": probas}


def monde_structure(rng, structure, n, k=3):
    """Monde nul (issues indépendantes des traits) d'une structure absente de 𝓛.

    Rend (loi que connaît l'oracle aveugle « calendrier », suite des issues dans l'ordre du temps). Pour le monde
    auto-excité, l'oracle connaît la règle du monde (une moyenne glissante sur son propre passé).
    """
    if k != 3 and structure in ("derive_lineaire", "rupture"):
        raise ValueError("dérive linéaire et rupture : K = 3")
    if structure == "derive_lineaire":
        oracle = _calendrier_derive_lineaire(rng, n)
    elif structure == "rupture":
        a = [0.6, 0.3, 0.1]
        rng.shuffle(a)
        b = list(reversed(a))
        oracle = {"type": "calendrier", "probas": [list(a) if t < n // 2 else list(b) for t in range(n)]}
    elif structure == "sinusoide":
        phi = rng.uniform(0.0, 2 * math.pi)
        oracle = {"type": "calendrier", "probas": [
            _softmax([AMPLITUDE_SINUS * math.sin(2 * math.pi * t / (n / 3) + phi + 2 * math.pi * j / k) for j in range(k)])
            for t in range(n)]}
    elif structure == "marche_aleatoire":
        logits, probas = [0.0] * k, []
        for _ in range(n):
            probas.append(_softmax(logits))
            logits = [v + rng.gauss(0.0, ECART_MARCHE) for v in logits]
        oracle = {"type": "calendrier", "probas": probas}
    elif structure == "calendrier_deterministe":
        ordre = list(range(k))
        rng.shuffle(ordre)
        y = [ordre[(t // LONGUEUR_BLOC) % k] for t in range(n)]
        return {"type": "calendrier", "probas": [[1.0 if j == x else 0.0 for j in range(k)] for x in y]}, y
    elif structure == "auto_excite":
        regle = {"type": "moyenne_glissante", "nombre_issues": k, "fenetre": FENETRE_AUTO, "lissage": LISSAGE_AUTO}
        y = []
        for t in range(n):
            y.append(sp.tirer_categorie(rng, sp.proba(regle, None, y, t)))
        return regle, y
    else:
        raise ValueError(f"structure inconnue : {structure!r}")
    y = [sp.tirer_categorie(rng, sp.proba(oracle, None, [], t)) for t in range(n)]
    return oracle, y


def composition(issues, k):
    return [issues.count(j) for j in range(k)]


# --- engagement, tirages, évaluation sous un juge -----------------------------------------------------------------
def _geler(loi, instances, k, alpha, juge, bibliotheque=None, part_calibrage=0, delta0=None, identifiant="controle"):
    j = JUGES[juge]
    return sp.geler_engagement(sp.construire_engagement(
        identifiant, loi, instances, k, alpha, j["bibliotheque"] if bibliotheque is None else bibliotheque, "continu",
        part_calibrage=part_calibrage, delta0=delta0, plan_execution=j["plan_execution"]))


class PlanObserveNonConforme(RuntimeError):
    """Une évaluation n'a pas tourné sous le plan d'exécution du juge de sa ligne (CJ1-03) : le contrôle s'arrête."""


def _tirer_et_evaluer(gele, monde, graine, cle, r):
    """Le noyau tient sa graine (étiquette « noyau ») ; le monde tire avec la sienne (étiquette « frais »).

    L'empreinte de l'ordre d'exécution observée (ordre secret) est recopiée dans le résultat de l'évaluation."""
    noyau = graine_derivee(graine, cle, r, "noyau")
    tirages = sp.tirer_frais(gele, monde, graine_derivee(graine, cle, r, "frais"), graine_noyau=noyau)
    ev = sp.evaluer(gele, tirages, graine_noyau=noyau)
    ev["empreinte_ordre"] = tirages.get("empreinte_ordre")
    return ev, tirages


class _Suivi:
    """Ce qu'une ligne consigne de chaque répétition (CJ1-03, CJ1-04) : promotion (chaîne de « 0 » et « 1 »), plan
    d'exécution observé dans l'évaluation (contrôlé contre celui du juge : sinon arrêt), empreintes d'ordre distinctes."""

    def __init__(self, juge):
        self.juge, self.chaine, self.plans, self.ordres = juge, [], collections.Counter(), set()

    def noter(self, ev, compter=True):
        attendu = JUGES[self.juge]["plan_execution"] if self.juge in JUGES else None
        plan = ev.get("plan_execution")
        if attendu is not None and plan != attendu:
            raise PlanObserveNonConforme(f"juge {self.juge} : évaluation sous le plan {plan!r}, attendu {attendu!r}")
        if not compter:
            return
        self.plans[plan] += 1
        if ev.get("empreinte_ordre"):
            self.ordres.add(ev["empreinte_ordre"])
        self.chaine.append("1" if ev["promue"] else "0")

    def champs(self):
        return {"plan_execution_observe": dict(sorted(self.plans.items())), "empreintes_ordre_distinctes": len(self.ordres),
                "promotions_par_repetition": "".join(self.chaine)}


def _ligne(nom, juge, role, promotions, repetitions, finales=None, maxima=None, dominants=None, **extra):
    ligne = {"controle": nom, "juge": juge, "role": role, "repetitions": repetitions, "promotions": promotions,
             "taux": promotions / repetitions, "borne_haute_95": borne_wilson(promotions, repetitions)}
    if juge in JUGES:
        ligne.update(plan_execution_du_juge=JUGES[juge]["plan_execution"])
    if finales:
        ligne.update(log_richesse_finale_mediane=statistics.median(finales), log_richesse_max_observee=max(maxima))
    if dominants is not None:
        ligne["membre_dominant_final"] = dict(sorted(dominants.items()))
    ligne.update(extra)
    return ligne


def _executer(nom, juge, role, graine, repetitions, scenario, cle, **extra):
    """`scenario(rng, juge)` rend (engagement gelé, loi du monde) ; graines de scénario partagées entre juges (`cle`)."""
    promotions, finales, maxima, dominants, suivi = 0, [], [], collections.Counter(), _Suivi(juge)
    for r in range(repetitions):
        rng = random.Random(graine_derivee(graine, cle, r))
        gele, monde = scenario(rng, juge)
        ev, _ = _tirer_et_evaluer(gele, monde, graine, cle, r)
        suivi.noter(ev)
        promotions += ev["promue"]
        finales.append(ev["log_richesse_finale"])
        maxima.append(ev["log_richesse_max"])
        dominants[ev["membre_dominant_final"].split(":")[0]] += 1
    return _ligne(nom, juge, role, promotions, repetitions, finales, maxima, dominants, etiquette_graines=cle,
                  **suivi.champs(), **extra)


# --- scénarios ------------------------------------------------------------------------------------------------------
def _scenario_t1a(monde_nom, tirages, k, dimension, alpha):
    def scenario(rng, juge):
        loi = sp.loi_softmax_aleatoire(rng, k, dimension)
        instances = sp.tirer_instances(rng, tirages, dimension)
        mondes = {"marginale": _fixe(sp.moyenne_loi(loi, instances)), "uniforme": _fixe([1 / k] * k),
                  "moyenne_glissante": {"type": "moyenne_glissante", "nombre_issues": k, "fenetre": 10, "lissage": 0.5}}
        return _geler(loi, instances, k, alpha, juge), mondes[monde_nom]
    return scenario


def _scenario_t1a_artefact(tirages, k, dimension, alpha):
    def scenario(rng, juge):
        pi = _dirichlet(rng, k, 1.0)
        instances = sp.tirer_instances(rng, tirages, dimension)
        return _geler(_fixe(pi), instances, k, alpha, juge, bibliotheque=[{"nom": "uniforme", "type": "uniforme"}]), _fixe(pi)
    return scenario


def _scenario_t6(variante, tirages, k, dimension, alpha):
    def scenario(rng, juge):
        pi = _dirichlet(rng, k, 2.0)
        entrainement = [sp.tirer_categorie(rng, pi) for _ in range(50)]
        pi_ent = _frequences(entrainement, k)
        parasite = {"type": "melange", "composantes": [_fixe(pi), _fixe(pi_ent)], "poids": [0.95, 0.05]}
        membre_ent = {"nom": "marginale_entrainement", "type": "fixe", "probas": pi_ent}
        glissantes = dict(sp.BIBLIOTHEQUE_STANDARD[2])
        bibliotheques = {
            "correct": list(JUGES[juge]["bibliotheque"]) + [membre_ent],
            # Critères cassés (sans marginale ajustée sur les tirages frais, ni urne) :
            "part_separee": [{"nom": "uniforme", "type": "uniforme"}, membre_ent, glissantes],
            "en_ligne": [{"nom": "uniforme", "type": "uniforme"},
                         {"nom": "marginale_en_ligne", "type": "marginale_en_ligne", "lissage": 0.5}, glissantes],
        }
        instances = sp.tirer_instances(rng, tirages, dimension)
        return _geler(parasite, instances, k, alpha, juge, bibliotheque=bibliotheques[variante]), _fixe(pi)
    return scenario


def _scenario_t3(epsilon, net_vrai, tirages, k, dimension, alpha):
    def scenario(rng, juge):
        net = sp.loi_softmax_aleatoire(rng, k, dimension)
        instances = sp.tirer_instances(rng, tirages, dimension)
        pi = sp.moyenne_loi(net, instances)
        couvert = {"type": "melange", "composantes": [_fixe(pi), net], "poids": [1 - epsilon, epsilon]}
        return _geler(couvert, instances, k, alpha, juge), (net if net_vrai else _fixe(pi))
    return scenario


def _scenario_t1b(structure, loi_aveugle, tirages, k, dimension, alpha):
    def scenario(rng, juge):
        instances = sp.tirer_instances(rng, tirages, dimension)
        oracle, y = monde_structure(rng, structure, tirages, k)
        loi = oracle if loi_aveugle == "calendrier" else {"type": "sans_remise", "composition": composition(y, k)}
        return _geler(loi, instances, k, alpha, juge), {"type": "deterministe", "nombre_issues": k, "issues": y}
    return scenario


def _scenario_domaine_vrai(avec_derive, tirages, k, dimension, alpha):
    """Puissance : loi de domaine vraie (softmax tirée) ; avec dérive : monde = (1−λ)·loi + λ·dérive linéaire, fiche =
    (1−λ)·loi + λ·moyenne de la dérive (ce qu'une fiche honnête peut connaître sans l'heure)."""
    def scenario(rng, juge):
        loi = sp.loi_softmax_aleatoire(rng, k, dimension)
        instances = sp.tirer_instances(rng, tirages, dimension)
        if not avec_derive:
            return _geler(loi, instances, k, alpha, juge), loi
        derive = _calendrier_derive_lineaire(rng, tirages)
        moyenne = [sum(p[j] for p in derive["probas"]) / tirages for j in range(k)]
        monde = {"type": "melange", "composantes": [loi, derive], "poids": [1 - LAMBDA_PUISSANCE, LAMBDA_PUISSANCE]}
        fiche = {"type": "melange", "composantes": [loi, _fixe(moyenne)], "poids": [1 - LAMBDA_PUISSANCE, LAMBDA_PUISSANCE]}
        return _geler(fiche, instances, k, alpha, juge), monde
    return scenario


# --- filles : tricheurs, fille neuve, T1b-fille ------------------------------------------------------------------------
def _membre_entrainement(q_ent):
    return {"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}


def _essai_fille(graine, nom, r, juge, tirages, alpha, k, dimension, delta0, part_calibrage, nul_augmente=True):
    cle = f"fille|{nom}" + ("" if nul_augmente else "|sans-parents")
    rng = random.Random(graine_derivee(graine, cle, r))
    p1, p2, p3 = (sp.loi_softmax_aleatoire(rng, k, dimension) for _ in range(3))
    instances = sp.tirer_instances(rng, part_calibrage + tirages, dimension)
    monde_nom = rng.choice(MONDES_FILLES)
    if nom == "fille_neuve":
        monde_nom = "parent_A_vrai_et_loi_neuve"
        monde = {"type": "par_sous_population", "lois": {"0": p1, "1": p3}}
        loi = {"type": "si_sinon", "condition": {"sous_population": 0}, "si": p1, "sinon": p3}
    else:
        monde = _monde_fille(monde_nom, p1, p2, instances)
    entrainement = sp.tirer_instances(rng, 100, dimension)
    q_ent = _frequences([sp.tirer_categorie(rng, sp.proba(monde, x, [], 0)) for x in entrainement], k)
    if nom != "fille_neuve":
        loi = loi_tricheur(nom, p1, p2, q_ent, rng)
    standard = list(JUGES[juge]["bibliotheque"]) + [_membre_entrainement(q_ent)]
    if nul_augmente:
        biblio = sp.bibliotheque_fille({"A": p1, "B": p2}, dimension, standard, q_ent, nombre_issues=k)
        gele = _geler(loi, instances, k, alpha, juge, biblio, part_calibrage, delta0, identifiant="fille")
    else:
        gele = _geler(loi, instances[part_calibrage:], k, alpha, juge, standard, identifiant="fille")
    ev, _ = _tirer_et_evaluer(gele, monde, graine, cle, r)
    return monde_nom, ev


def _essai_t1b_fille(graine, r, juge, tirages, alpha, k, dimension, delta0, part_calibrage):
    """Fille = parent A + connaissance de la dérive ; monde = parent A + dérive (λ = 0,5, dérive linéaire sur l'horizon
    d'exécution) ; nul augmenté des parents. La fille indexe sa dérive sur l'ordre du plan, partie d'évaluation : sous
    l'ordre naturel, elle est exactement la loi vraie ; sous l'ordre secret, l'heure lui échappe."""
    cle = "T1b-fille"
    rng = random.Random(graine_derivee(graine, cle, r))
    p1, p2 = (sp.loi_softmax_aleatoire(rng, k, dimension) for _ in range(2))
    horizon = part_calibrage + tirages
    instances = sp.tirer_instances(rng, horizon, dimension)
    derive = _calendrier_derive_lineaire(rng, horizon)
    poids = [1 - LAMBDA_FILLE, LAMBDA_FILLE]
    monde = {"type": "melange", "composantes": [p1, derive], "poids": poids}
    fille = {"type": "melange", "composantes": [p1, {"type": "calendrier", "probas": derive["probas"][part_calibrage:]}],
             "poids": poids}
    entrainement = sp.tirer_instances(rng, 100, dimension)
    issues_ent = []
    for x in entrainement:
        instant = rng.randrange(horizon)
        issues_ent.append(sp.tirer_categorie(rng, sp.proba(monde, x, [], instant)))
    q_ent = _frequences(issues_ent, k)
    standard = list(JUGES[juge]["bibliotheque"]) + [_membre_entrainement(q_ent)]
    biblio = sp.bibliotheque_fille({"A": p1, "B": p2}, dimension, standard, q_ent, nombre_issues=k)
    gele = _geler(fille, instances, k, alpha, juge, biblio, part_calibrage, delta0, identifiant="fille")
    ev, _ = _tirer_et_evaluer(gele, monde, graine, cle, r)
    return ev


def _essai_parent_et_loi_aveugle(graine, r, juge, tirages, alpha, k, dimension, delta0, part_calibrage):
    """Tricheur ajouté après l'essai de fumée (déclaré) : fille = parent A mélangé à une loi aveugle fixe q (λ = 0,5, q
    tirée d'une loi de Dirichlet(1, 1, 1)), monde = la même loi — aucune dérive, aucun contenu nouveau sur les traits.
    Le nul augmenté de v0 ne contient le parent mélangé qu'à l'uniforme et à la marginale d'entraînement."""
    cle = "fille|parent_et_loi_aveugle"
    rng = random.Random(graine_derivee(graine, cle, r))
    p1, p2 = (sp.loi_softmax_aleatoire(rng, k, dimension) for _ in range(2))
    instances = sp.tirer_instances(rng, part_calibrage + tirages, dimension)
    q = _dirichlet(rng, k, 1.0)
    monde = {"type": "melange", "composantes": [p1, _fixe(q)], "poids": [1 - LAMBDA_FILLE, LAMBDA_FILLE]}
    entrainement = sp.tirer_instances(rng, 100, dimension)
    q_ent = _frequences([sp.tirer_categorie(rng, sp.proba(monde, x, [], 0)) for x in entrainement], k)
    standard = list(JUGES[juge]["bibliotheque"]) + [_membre_entrainement(q_ent)]
    biblio = sp.bibliotheque_fille({"A": p1, "B": p2}, dimension, standard, q_ent, nombre_issues=k)
    gele = _geler(monde, instances, k, alpha, juge, biblio, part_calibrage, delta0, identifiant="fille")
    ev, _ = _tirer_et_evaluer(gele, monde, graine, cle, r)
    return ev


def _executer_filles(nom_ligne, juge, role, graine, repetitions, essai, **extra):
    promotions, par_monde, finales, maxima, suivi = 0, {}, [], [], _Suivi(juge)
    for r in range(repetitions):
        monde_nom, ev = essai(r)
        suivi.noter(ev)
        promotions += ev["promue"]
        finales.append(ev["log_richesse_finale"])
        maxima.append(ev["log_richesse_max"])
        compte = par_monde.setdefault(monde_nom, [0, 0])
        compte[0] += ev["promue"]
        compte[1] += 1
    return _ligne(nom_ligne, juge, role, promotions, repetitions, finales, maxima,
                  par_monde={m: {"promotions": c[0], "repetitions": c[1]} for m, c in sorted(par_monde.items())},
                  **suivi.champs(), **extra)


# --- T9 et artefact « permutation de l'ordre d'évaluation » -----------------------------------------------------------
def controle_t9_v1(graine, repetitions, tirages, alpha, k, dimension, juge="v1"):
    """Fille = concaténation si/sinon de deux parents, contre le nul augmenté : aucune promotion, log W ≤ 0 ; témoin :
    fille qui prédit du neuf sur une partie."""
    bib = JUGES[juge]["bibliotheque"]
    gains_naifs, promotions_concat, max_logw_concat, promotions_neuve, suivi = [], 0, -math.inf, 0, _Suivi(juge)
    for r in range(repetitions):
        rng = random.Random(graine_derivee(graine, "T9", r))
        p1, p2, p3 = (sp.loi_softmax_aleatoire(rng, k, dimension) for _ in range(3))
        instances = sp.tirer_instances(rng, tirages, dimension)
        nul_fille = sp.bibliotheque_fille({"A": p1, "B": p2}, dimension, bib, nombre_issues=k)
        for neuve in (False, True):
            monde = {"type": "par_sous_population", "lois": {"0": p1, "1": p3 if neuve else p2}}
            fille = {"type": "si_sinon", "condition": {"sous_population": 0}, "si": p1, "sinon": p3 if neuve else p2}
            gele = _geler(fille, instances, k, alpha, juge, nul_fille, identifiant="T9")
            ev, tirages_frais = _tirer_et_evaluer(gele, monde, graine, f"T9|{neuve}", r)
            suivi.noter(ev, compter=not neuve)
            if neuve:
                promotions_neuve += ev["promue"]
                continue
            promotions_concat += ev["promue"]
            max_logw_concat = max(max_logw_concat, ev["log_richesse_max"])
            issues = tirages_frais["issues"]
            den, _ = sp.trajectoire_denominateur(bib, issues, instances, k)
            naif = {nom: sp.trajectoire_loi(l, issues, instances)[-1] - den[-1] for nom, l in
                    (("fille", fille), ("A", p1), ("B", p2))}
            gains_naifs.append(naif["fille"] - max(naif["A"], naif["B"]))
    ligne = _ligne("T9-disjonction-partitionnee", juge, "fatal", promotions_concat, repetitions,
                   log_richesse_max_observee=max_logw_concat, etiquette_graines="T9",
                   gain_naif_sur_meilleur_parent_median=statistics.median(gains_naifs),
                   part_gain_naif_positif=sum(g > 0 for g in gains_naifs) / repetitions,
                   temoin_positif_fille_neuve_taux_promotion=promotions_neuve / repetitions,
                   regle="règle de v0 : W seule, 200 instances, sans part de calibrage ni marge 2δ₀ (CJ1-11)",
                   **suivi.champs())
    ligne["passe"] = ligne["taux"] <= alpha and max_logw_concat <= 1e-9
    return ligne


def artefact_permutation_evaluation(graine, repetitions, tirages, alpha, k, dimension):
    """Critère cassé : le monde exécute dans l'ordre du plan (calendrier déterministe par blocs) et l'évaluateur permute
    les couples (instance, issue) au lieu de l'ordre d'exécution. La loi « retrouve l'heure par l'instance » (le plan est
    dans l'engagement : l'indice d'une instance dans le plan est son heure) et prédit le calendrier à cette heure.
    Dénominateur : bibliothèque du juge v1 (urne comprise) sur la suite permutée."""
    cle, seuil, promotions, maxima, chaine = "artefact-permutation-evaluation", math.log(1 / alpha), 0, [], []
    for r in range(repetitions):
        rng = random.Random(graine_derivee(graine, cle, r))
        instances = sp.tirer_instances(rng, tirages, dimension)
        oracle, y = monde_structure(rng, "calendrier_deterministe", tirages, k)
        sigma = list(range(tirages))
        random.Random(graine_derivee(graine, cle, r, "permutation-evaluation")).shuffle(sigma)
        issues_permutees = [y[j] for j in sigma]
        instances_permutees = [instances[j] for j in sigma]
        numerateur, cumul = [], 0.0
        for j in sigma:  # l'heure de l'instance j est j (ordre d'exécution naturel)
            cumul += math.log(sp.proba(oracle, instances[j], [], j)[y[j]])
            numerateur.append(cumul)
        den, _ = sp.trajectoire_denominateur(sp.BIBLIOTHEQUE_STANDARD_V1, issues_permutees, instances_permutees, k)
        log_w = [a - b for a, b in zip(numerateur, den)]
        promotions += max(log_w) >= seuil
        chaine.append("1" if max(log_w) >= seuil else "0")
        maxima.append(max(log_w))
    return _ligne("artefact-permutation-de-l-ordre-d-evaluation", "v1_permutation_evaluation", "artefact_requis",
                  promotions, repetitions, finales=None, log_richesse_max_observee=max(maxima),
                  log_richesse_max_mediane=statistics.median(maxima), etiquette_graines=cle,
                  plan_execution_observe={"ordre_naturel, couples (instance, issue) permutés à l'évaluation": repetitions},
                  promotions_par_repetition="".join(chaine),
                  structure="calendrier_deterministe", loi_aveugle="heure retrouvée par l'instance")


# --- expérience ---------------------------------------------------------------------------------------------------------
FAMILLES = ("T1a", "T6", "tricheurs", "T3", "T9", "T1b", "T1b-fille", "puissance")


def verifier_parametres(graine, repetitions, essai=False, familles=None, k=3):
    """Refuse, avant toute écriture, une exécution décisive mal paramétrée."""
    if not isinstance(graine, int) or isinstance(graine, bool):
        raise ValueError("graine maîtresse entière exigée")
    if not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError("répétitions : entier ≥ 1")
    if familles is not None and not set(familles) <= set(FAMILLES):
        raise ValueError(f"familles : parmi {FAMILLES}")
    if not essai:
        if repetitions != REPETITIONS_DECISIVES:
            raise ValueError(f"exactement {REPETITIONS_DECISIVES} répétitions par contrôle hors mode essai (CJ1-13)")
        if graine in GRAINES_REFUSEES:
            raise ValueError(f"graines {GRAINES_REFUSEES} (exploration de v0, essais de fumée) refusées : graine maîtresse "
                             "neuve exigée")
        if familles is not None:
            raise ValueError("l'expérience décisive exécute toutes les familles")
    if k != 3:
        raise ValueError("expérience définie pour K = 3")


def executer_controles_v1(graine, repetitions=1000, tirages=200, alpha=0.05, k=3, dimension=2, delta0=0.01,
                          part_calibrage=50, essai=False, familles=None):
    """Toutes les lignes de l'expérience 1. `essai` permet moins de 1 000 répétitions (rapport marqué non décisif) ;
    `familles` restreint les familles exécutées (essais seulement)."""
    verifier_parametres(graine, repetitions, essai, familles, k)
    tout = familles is None
    veut = (lambda f: tout or f in familles)
    lignes = []
    if veut("T1a"):
        for m in ("marginale", "uniforme", "moyenne_glissante"):
            lignes.append(_executer(f"T1a-nul-{m}", "v1", "fatal", graine, repetitions,
                                    _scenario_t1a(m, tirages, k, dimension, alpha), f"T1a|{m}"))
        lignes.append(_executer("artefact-T1a-bibliotheque-uniforme-seule", "v1", "artefact_requis", graine, repetitions,
                                _scenario_t1a_artefact(tirages, k, dimension, alpha), "T1a|artefact"))
    if veut("T6"):
        lignes.append(_executer("T6-parasite-de-Kelly", "v1", "fatal", graine, repetitions,
                                _scenario_t6("correct", tirages, k, dimension, alpha), "T6"))
        for v in ("part_separee", "en_ligne"):
            lignes.append(_executer(f"artefact-T6-denominateur-{v.replace('_', '-')}", "v1", "artefact_requis", graine,
                                    repetitions, _scenario_t6(v, tirages, k, dimension, alpha), "T6"))
    if veut("tricheurs"):
        for nom in TRICHEURS:
            lignes.append(_executer_filles(f"tricheur-{nom}", "v1", "fatal", graine, repetitions,
                                           lambda r, nom=nom: _essai_fille(graine, nom, r, "v1", tirages, alpha, k, dimension,
                                                                           delta0, part_calibrage),
                                           etiquette_graines=f"fille|{nom}"))
        for juge, role in (("v1", "fatal"), ("v0", "descriptif")):
            lignes.append(_executer_filles("tricheur-parent_et_loi_aveugle", juge, role, graine, repetitions,
                                           lambda r, juge=juge: ("parent_A_plus_loi_aveugle", _essai_parent_et_loi_aveugle(
                                               graine, r, juge, tirages, alpha, k, dimension, delta0, part_calibrage)),
                                           etiquette_graines="fille|parent_et_loi_aveugle", lambda_loi_aveugle=LAMBDA_FILLE,
                                           ajoute_apres_essai_de_fumee=True))
        for juge, role in (("v1", "puissance_decisive"), ("v0", "descriptif")):
            lignes.append(_executer_filles("puissance-fille-neuve", juge, role, graine, repetitions,
                                           lambda r, juge=juge: _essai_fille(graine, "fille_neuve", r, juge, tirages, alpha,
                                                                             k, dimension, delta0, part_calibrage),
                                           etiquette_graines="fille|fille_neuve"))
        for nom in ("forme", "enveloppe_aveugle"):
            lignes.append(_executer_filles(f"artefact-fille-sans-parents-dans-le-nul-{nom}", "v1", "artefact_requis", graine,
                                           repetitions,
                                           lambda r, nom=nom: _essai_fille(graine, nom, r, "v1", tirages, alpha, k, dimension,
                                                                           delta0, part_calibrage, nul_augmente=False),
                                           etiquette_graines=f"fille|{nom}|sans-parents"))
    if veut("T3"):
        for e in (0.05, 0.2):
            for vrai in (False, True):
                juges = ("v1",) if not vrai else ("v1", "v0")
                for juge in juges:
                    if not vrai:
                        role = "fatal"
                    elif juge == "v1" and e == 0.2:
                        role = "puissance_decisive"
                    else:
                        role = "descriptif"
                    lignes.append(_executer(f"T3-couvert-eps{e}-net-{'vrai' if vrai else 'faux'}", juge, role, graine,
                                            repetitions, _scenario_t3(e, vrai, tirages, k, dimension, alpha),
                                            f"T3|{e}|{vrai}", epsilon=e, composante_nette_vraie=vrai))
    if veut("T9"):
        lignes.append(controle_t9_v1(graine, repetitions, tirages, alpha, k, dimension, "v1"))
    if veut("T1b"):
        for structure in STRUCTURES:
            for loi in LOIS_AVEUGLES:
                for juge in ("v1", "v0", "v1_sans_urne"):
                    if juge == "v1":
                        role = "fatal"
                    elif juge == "v0" and structure == "derive_lineaire" and loi == "calendrier":
                        role = "artefact_requis"
                    elif juge == "v1_sans_urne" and structure == "calendrier_deterministe" and loi == "composition":
                        role = "artefact_requis"
                    else:
                        role = "descriptif"
                    lignes.append(_executer(f"T1b-{structure}-loi-{loi}", juge, role, graine, repetitions,
                                            _scenario_t1b(structure, loi, tirages, k, dimension, alpha),
                                            f"T1b|{structure}|{loi}", structure=structure, loi_aveugle=loi))
        lignes.append(artefact_permutation_evaluation(graine, repetitions, tirages, alpha, k, dimension))
    if veut("T1b-fille"):
        for juge, role in (("v1", "fatal"), ("v0", "descriptif")):
            lignes.append(_executer_filles("T1b-fille", juge, role, graine, repetitions,
                                           lambda r, juge=juge: ("parent_A_plus_derive", _essai_t1b_fille(
                                               graine, r, juge, tirages, alpha, k, dimension, delta0, part_calibrage)),
                                           etiquette_graines="T1b-fille", lambda_derive=LAMBDA_FILLE))
    if veut("puissance"):
        for avec_derive in (False, True):
            nom = "puissance-loi-vraie-plus-derive" if avec_derive else "puissance-loi-de-domaine-vraie"
            for juge in ("v1", "v0"):
                lignes.append(_executer(nom, juge, "descriptif", graine, repetitions,
                                        _scenario_domaine_vrai(avec_derive, tirages, k, dimension, alpha),
                                        f"puissance|{avec_derive}",
                                        **({"lambda_derive": LAMBDA_PUISSANCE} if avec_derive else {})))
    parametres = {"graine_maitresse": graine, "repetitions": repetitions, "tirages_par_repetition": tirages, "alpha": alpha,
                  "seuil_richesse": 1 / alpha, "nombre_issues": k, "dimension": dimension, "delta0_filles": delta0,
                  "part_calibrage_filles": part_calibrage, "essai": essai, "familles": sorted(familles) if familles else "toutes",
                  "lecture": "continue (promotion dès que W_t ≥ 1/α, inégalité de Ville)",
                  "juges": {n: {"plan_execution": j["plan_execution"], "bibliotheque": [m["nom"] for m in j["bibliotheque"]],
                                "description": j["description"]} for n, j in JUGES.items()},
                  "structures_T1b": DESCRIPTION_STRUCTURES, "lambda_T1b_fille": LAMBDA_FILLE,
                  "lambda_puissance_derive": LAMBDA_PUISSANCE, "seuil_puissance": SEUIL_PUISSANCE,
                  "perte_puissance_predite_max": PERTE_PUISSANCE_PREDITE,
                  "regle_des_graines": "graine_derivee(graine_maîtresse, étiquette, répétition[, 'frais' | 'noyau']) ; "
                                       "tirages frais : graine_derivee(graine 'frais', 'tirages-frais', empreinte de "
                                       "l'engagement) ; ordre secret : graine_derivee(graine 'noyau', 'ordre-execution', "
                                       "empreinte de l'engagement)"}
    r = {"parametres": parametres, "lignes": lignes}
    decisive = tout and not essai
    r["verdicts"] = juger_v1(r, alpha, complet=decisive, roster=ROSTER_V1 if decisive else None,
                             repetitions_attendues=repetitions if decisive else None)
    return r


# --- lecture gelée ------------------------------------------------------------------------------------------------------
def _passe(ligne, alpha):
    return ligne["passe"] if "passe" in ligne else ligne["taux"] <= alpha


PREFIXES_FILLES = ("tricheur-", "puissance-fille-neuve", "artefact-fille-sans-parents", "T9-", "T1b-fille")
ISSUE_ESSAI = "ESSAI OU EXÉCUTION PARTIELLE — aucune issue n'est prononcée"
ISSUE_INCOMPLETE = "EXÉCUTION INCOMPLÈTE OU NON CONFORME — aucune issue n'est prononcée"


def partie_de(nom):
    """« filles » : le critère des filles (nul augmenté des parents, marge 2δ₀) ; « socle » : tout le reste."""
    return "filles" if nom.startswith(PREFIXES_FILLES) else "socle"


def _lecture(lignes, alpha, complet, issue_forcee=None):
    fatals = [l for l in lignes if l["role"] == "fatal"]
    artefacts = [l for l in lignes if l["role"] == "artefact_requis"]
    puissances = [l for l in lignes if l["role"] == "puissance_decisive"]
    echecs = [l["controle"] for l in fatals if not _passe(l, alpha)]
    non_vus = [l["controle"] + f" ({l['juge']})" for l in artefacts if l["taux"] <= alpha]
    faibles = [l["controle"] for l in puissances if l["taux"] < SEUIL_PUISSANCE]
    if issue_forcee is not None:
        issue = issue_forcee
    elif not complet:
        issue = ISSUE_ESSAI
    elif echecs or faibles:
        issue = "non adopté"
    elif non_vus:
        issue = "non concluant"
    else:
        issue = "adopté"
    return {"issue": issue,
            "fatals": {"critere": f"taux de promotion ≤ α = {alpha} pour chaque contrôle fatal (T9 : et log W max ≤ 10⁻⁹)",
                       "nombre": len(fatals), "echecs": echecs,
                       "taux_max": max((l["taux"] for l in fatals), default=None),
                       "controle_au_taux_max": max(fatals, key=lambda l: l["taux"])["controle"] if fatals else None},
            "artefacts_requis": {"critere": f"taux > α = {alpha} (sinon le contrôle n'a pas de dents, R5)",
                                 "nombre": len(artefacts), "non_vus": non_vus},
            "puissance_decisive": {"critere": f"taux ≥ {SEUIL_PUISSANCE} (juge v1)",
                                   "lignes": {l["controle"]: l["taux"] for l in puissances}, "insuffisantes": faibles},
            "ce_qui_a_cede": echecs + faibles + ["artefact non vu : " + n for n in non_vus]}


def conformite(lignes, roster, repetitions_attendues):
    """CJ1-02 : l'exécution décisive doit produire exactement les 70 couples (contrôle, juge) de `ROSTER_V1`, chacun à
    `repetitions_attendues` répétitions ; sinon aucune issue n'est prononcée."""
    presents = [(l["controle"], l["juge"]) for l in lignes]
    manquants = sorted(set(roster) - set(presents))
    en_trop = sorted(set(presents) - set(roster))
    doubles = sorted({c for c in presents if presents.count(c) > 1})
    mal_repetees = sorted((l["controle"], l["juge"], l["repetitions"]) for l in lignes
                          if repetitions_attendues is not None and l["repetitions"] != repetitions_attendues)
    return {"conforme": not (manquants or en_trop or doubles or mal_repetees), "lignes_manquantes": manquants,
            "lignes_en_trop": en_trop, "lignes_en_double": doubles, "lignes_mal_repetees": mal_repetees}


LIGNES_DE_PUISSANCE_APPARIEES = ("puissance-fille-neuve", "T3-couvert-eps0.05-net-vrai", "T3-couvert-eps0.2-net-vrai",
                                 "puissance-loi-de-domaine-vraie", "puissance-loi-vraie-plus-derive")


def appariement_v0_v1(lignes):
    """CJ1-04 : nombre de répétitions où v0 et v1 diffèrent, par ligne de puissance appariée par scénario."""
    par_couple = {(l["controle"], l["juge"]): l for l in lignes}
    sortie = {}
    for nom in LIGNES_DE_PUISSANCE_APPARIEES:
        a, b = par_couple.get((nom, "v0")), par_couple.get((nom, "v1"))
        if a and b and "promotions_par_repetition" in a and "promotions_par_repetition" in b:
            sa, sb = a["promotions_par_repetition"], b["promotions_par_repetition"]
            sortie[nom] = sum(x != y for x, y in zip(sa, sb)) if len(sa) == len(sb) else None
    return sortie


def declencheurs_r4(lignes, alpha, appariement):
    """Déclencheurs de l'audit de symétrie, évalués mécaniquement sur le rapport (CJ1-03, CJ1-04, CJ1-07, CJ1-09)."""
    d = []
    for l in lignes:
        nom, juge = l["controle"], l["juge"]
        if juge == "v1" and nom.endswith("-loi-composition") and (
                l.get("promotions", 0) > 0 or l.get("log_richesse_max_observee", 0.0) > 1e-9):
            d.append(f"composition promue ou log W max > 10⁻⁹ : {nom}")
        if juge == "v1" and l["role"] == "fatal" and nom.startswith(("T1a-nul-", "T1b-")) and not nom.startswith("T1b-fille"):
            if l.get("membre_dominant_final", {}).get("urne", 0) == 0:
                d.append(f"urne jamais dominante sur les {l.get('repetitions')} répétitions : {nom}")
        if juge == "v1" and "plan_execution_observe" in l:
            if set(l["plan_execution_observe"]) != {"ordre_secret"}:
                d.append(f"plan observé autre que l'ordre secret : {nom}")
            elif l.get("empreintes_ordre_distinctes") != l.get("repetitions"):
                d.append(f"empreintes d'ordre non toutes distinctes : {nom}")
    if appariement and all(n == 0 for n in appariement.values()):
        d.append("promotions de v0 et de v1 égales une à une sur toutes les lignes de puissance appariées")
    fatales_socle = [l for l in lignes if l["role"] == "fatal" and partie_de(l["controle"]) == "socle"]
    if fatales_socle and all(l.get("promotions", 0) == 0 for l in fatales_socle):
        d.append("toutes les fatales du socle à 0 (attendu probable, CJ1-07 : vérifier répétitions et log W max finis)")
    cedage = {l["controle"]: l["taux"] for l in lignes if l["juge"] == "v1"
              and l["controle"] in ("T1b-fille", "tricheur-parent_et_loi_aveugle")}
    if cedage and all(t <= alpha for t in cedage.values()):
        d.append("prédictions de cédage des filles contredites (T1b-fille et « parent et loi aveugle » ≤ α)")
    return d


def juger_v1(r, alpha, complet=True, roster=None, repetitions_attendues=None):
    """Lecture gelée (préenregistrement de l'expérience 1).

    Issue globale (règle de la note de conception) : adopté si tous les contrôles fatals passent, si tous les artefacts
    requis sont vus et si chaque puissance décisive atteint 0,90 ; non adopté si un contrôle fatal échoue ou si une
    puissance décisive manque ; non concluant sinon. La même règle est lue séparément sur le socle (fiches sans parents)
    et sur le critère des filles ; l'issue globale est « adopté » si et seulement si les deux parties le sont.
    Exécution décisive : `roster` et `repetitions_attendues` donnés ; un rapport non conforme ne reçoit aucune issue.
    """
    lignes = r["lignes"]
    forcee, conf = None, None
    if complet and roster is not None:
        conf = conformite(lignes, roster, repetitions_attendues)
        if not conf["conforme"]:
            forcee = ISSUE_INCOMPLETE
    v = _lecture(lignes, alpha, complet, forcee)
    v["parties"] = {p: _lecture([l for l in lignes if partie_de(l["controle"]) == p], alpha, complet, forcee)
                    for p in ("socle", "filles")}
    v["conformite"] = conf
    neuve = {l["juge"]: l["taux"] for l in lignes if l["controle"] == "puissance-fille-neuve"}
    perte = neuve["v0"] - neuve["v1"] if {"v0", "v1"} <= set(neuve) else None
    v["perte_de_puissance_fille_neuve"] = {"v0_moins_v1": perte, "predite_au_plus": PERTE_PUISSANCE_PREDITE,
                                           "prediction_tenue": None if perte is None else perte <= PERTE_PUISSANCE_PREDITE}
    v["appariement_v0_v1_repetitions_differentes"] = appariement_v0_v1(lignes)
    v["declencheurs_R4"] = declencheurs_r4(lignes, alpha, v["appariement_v0_v1_repetitions_differentes"])
    return v


def rapport_markdown(r, horodatage):
    p, v = r["parametres"], r["verdicts"]
    lignes = [f"# Expérience 1 du pôle — juge v1 : {v['issue']} (socle : {v['parties']['socle']['issue']} ; "
              f"critère des filles : {v['parties']['filles']['issue']})\n"]
    if p["essai"]:
        lignes.append("**ESSAI — non décisif** (moins de répétitions ou familles partielles ; graine d'essai).\n")
    lignes.append(f"Horodatage : {horodatage['valeur']} ({horodatage['source']}). Graine maîtresse {p['graine_maitresse']} ; "
                  f"{p['repetitions']} répétitions par ligne ; {p['tirages_par_repetition']} tirages frais par répétition ; "
                  f"α = {p['alpha']} (seuil de richesse {p['seuil_richesse']:.0f}) ; lecture {p['lecture']}.")
    lignes.append("Simulation seulement : ces taux valent pour les mondes synthétiques décrits, rien au-delà.\n")
    for titre, w in (("Global", v), ("Socle (fiches sans parents)", v["parties"]["socle"]),
                     ("Critère des filles", v["parties"]["filles"])):
        lignes.append(f"- **{titre}** — {w['issue']}. Contrôles fatals : {w['fatals']['nombre']}, échecs : "
                      f"{w['fatals']['echecs'] or 'aucun'}, taux max {w['fatals']['taux_max']} "
                      f"({w['fatals']['controle_au_taux_max']}) ; artefacts requis : {w['artefacts_requis']['nombre']}, "
                      f"non vus : {w['artefacts_requis']['non_vus'] or 'aucun'} ; puissance décisive : "
                      f"{w['puissance_decisive']['lignes']} (insuffisantes : {w['puissance_decisive']['insuffisantes'] or 'aucune'}).")
    pf = v["perte_de_puissance_fille_neuve"]
    lignes.append(f"- Perte de puissance sur la fille neuve (v0 − v1) : {pf['v0_moins_v1']} (prédite ≤ {pf['predite_au_plus']}).")
    lignes.append(f"- Ce qui a cédé : {v['ce_qui_a_cede'] or 'rien'}.")
    if v.get("conformite") is not None:
        c = v["conformite"]
        lignes.append(f"- Conformité du rapport (70 couples, {p['repetitions']} répétitions chacun) : "
                      + ("conforme" if c["conforme"] else f"NON CONFORME ({ {k: x for k, x in c.items() if k != 'conforme' and x} })")
                      + ".")
    lignes.append(f"- Appariement v0/v1 (répétitions différentes par ligne de puissance) : "
                  f"{v.get('appariement_v0_v1_repetitions_differentes')}.")
    lignes.append(f"- Déclencheurs de l'audit de symétrie (R4) : {v.get('declencheurs_R4') or 'aucun'}.\n")
    lignes.append("| partie | rôle | contrôle | juge | promotions | taux | borne haute 95 % | log W max observé |")
    lignes.append("|---|---|---|---|---|---|---|---|")
    ordre = {"fatal": 0, "puissance_decisive": 1, "artefact_requis": 2, "descriptif": 3}
    for l in sorted(r["lignes"], key=lambda l: (partie_de(l["controle"]), ordre[l["role"]], l["controle"], l["juge"])):
        maximum = l.get("log_richesse_max_observee")
        lignes.append(f"| {partie_de(l['controle'])} | {l['role']} | {l['controle']} | {l['juge']} | "
                      f"{l['promotions']}/{l['repetitions']} | {l['taux']:.4f} | {l['borne_haute_95']:.4f} | "
                      f"{'—' if maximum is None else format(maximum, '.3f')} |")
    return "\n".join(lignes) + "\n"
