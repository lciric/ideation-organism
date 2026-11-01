"""Recombinaison bisociative des survivantes — forme corrigée (relecture méta-conception v6.3, brique 2).

Diversité de domaine dans le noyau, S_ij = ⟨d_i, d_j⟩² (produit de Schur d'une matrice de Gram par elle-même : semi-défini
positif), qualité dans la diagonale, q_i = aptitude, L = diag(q) S diag(q) + γI (défini positif pour γ > 0, vérifié par
une décomposition de Cholesky en pur Python), tirage glouton du déterminant maximal de taille k ; puis, pour chaque paire
tirée qui partage un opérateur (le pont) et passe le filtre de compatibilité des contraintes, une consigne de fusion.
La fille doit porter ses deux parents et prédire plus qu'eux (`ce_que_la_fille_predit_de_plus` non vide, prédiction
différente de celles des parents). Les témoins n'entrent jamais dans la recombinaison.

Version 0.3.0 : tirage **stratifié** par défaut (décision R-527, après l'essai des ponts plantés `72cff8a0…` où la forme
corrigée perd de 4,8 et 2,2 points contre lui) : paires valides (pont d'opérateur commun, contraintes compatibles, jamais
fusionnées), strates = paire de domaines estimés (premier domaine de chaque fiche), tour des strates dans un ordre tiré,
une paire tirée au hasard dans chaque strate, abstention s'il n'y a aucune paire valide. `tirage="noyau_corrige"` rend v0.

Version 0.4.0 : `tirage="stratifie_marchepieds"` — la moitié des paires (arrondie au-dessus) bâtie sur les **marchepieds** :
les survivantes qui sont elles-mêmes des filles (des recombinaisons qui ont réussi), de la plus forte preuve à la plus
faible (log W cumulé de leur classe dans la mémoire), chacune avec un partenaire valide tiré au hasard ; le reste par
strates. Essai de la mémoire, piste 3 : les marchepieds n'aident que si les vraies associations se regroupent (ici :
si les lignées sont fécondes) ; sans cela, ils ne doivent rien coûter de plus que le hasard.
"""

import itertools
import json
import math
import os
import random
import re

from .caviardage import caviarder
from .fiche import Fiche, FicheInvalide
from .memoire import signature_prediction
from .outils import dossier_traces, ecrire_scelle, extraire_bloc_json, graine_derivee, json_canonique, normaliser_texte

MARQUEURS = {
    "lineaire": r"(?<!non )\blineaires?\b",
    "non lineaire": r"\bnon lineaires?\b",
    "stationnaire": r"(?<!non )\bstationnaires?\b",
    "transitoire": r"\btransitoires?\b|\bnon stationnaires?\b",
    "discret": r"\bdiscrete?s?\b",
    "continu": r"\bcontinue?s?\b",
    "convexe": r"(?<!non )\bconvexes?\b",
    "non convexe": r"\bnon convexes?\b",
    "independant": r"\bindependante?s?\b|\bnon dependante?s?\b",
    "dependant": r"(?<!non )\bdependante?s?\b",
}
PAIRES_CONTRADICTOIRES = (("lineaire", "non lineaire"), ("stationnaire", "transitoire"), ("discret", "continu"),
                          ("convexe", "non convexe"), ("independant", "dependant"))


class NonDefiniePositive(ValueError):
    pass


# --- filtre de compatibilité ------------------------------------------------------------------------------------
def marqueurs(contraintes):
    texte = " | ".join(normaliser_texte(c) for c in contraintes)
    return {nom for nom, motif in MARQUEURS.items() if re.search(motif, texte)}


def conflits(contraintes_a, contraintes_b):
    ma, mb = marqueurs(contraintes_a), marqueurs(contraintes_b)
    return [(p, q) for p, q in PAIRES_CONTRADICTOIRES if (p in ma and q in mb) or (q in ma and p in mb)]


def compatibles(a, b):
    return not conflits(a.contraintes, b.contraintes)


# --- noyau corrigé, Cholesky, tirage glouton --------------------------------------------------------------------
def vecteurs_domaine(listes):
    vocabulaire = sorted({normaliser_texte(x) for liste in listes for x in liste})
    position = {v: i for i, v in enumerate(vocabulaire)}
    vecteurs = []
    for liste in listes:
        v = [0.0] * len(vocabulaire)
        etiquettes = {normaliser_texte(x) for x in liste}
        for e in etiquettes:
            v[position[e]] = 1.0 / math.sqrt(len(etiquettes))
        vecteurs.append(v)
    return vecteurs


def produit(u, v):
    return sum(a * b for a, b in zip(u, v))


def noyau_diversite(vecteurs):
    return [[produit(u, v) ** 2 for v in vecteurs] for u in vecteurs]


def noyau_corrige(s, q, gamma=1e-3):
    n = len(s)
    return [[q[i] * s[i][j] * q[j] + (gamma if i == j else 0.0) for j in range(n)] for i in range(n)]


def noyau_fautif(vecteurs_operateurs, vecteurs_domaines):
    """Forme du rapport relu (« DPP bilinéaire ») : ⟨o_i,o_j⟩² ∘ (1 − ⟨d_i,d_j⟩²) — non garantie semi-définie positive."""
    return [[produit(oi, oj) ** 2 * (1 - produit(di, dj) ** 2) for oj, dj in zip(vecteurs_operateurs, vecteurs_domaines)]
            for oi, di in zip(vecteurs_operateurs, vecteurs_domaines)]


def cholesky(a, tolerance=0.0):
    """Facteur triangulaire inférieur ; lève NonDefiniePositive si un pivot n'est pas strictement positif."""
    n = len(a)
    for i in range(n):
        for j in range(i):
            if abs(a[i][j] - a[j][i]) > 1e-12 * max(1.0, abs(a[i][j])):
                raise NonDefiniePositive("matrice non symétrique")
    bas = [[0.0] * n for _ in range(n)]
    for j in range(n):
        pivot = a[j][j] - sum(bas[j][k] ** 2 for k in range(j))
        if not pivot > tolerance:
            raise NonDefiniePositive(f"pivot {j} = {pivot:.3e}")
        bas[j][j] = math.sqrt(pivot)
        for i in range(j + 1, n):
            bas[i][j] = (a[i][j] - sum(bas[i][k] * bas[j][k] for k in range(j))) / bas[j][j]
    return bas


def est_definie_positive(a):
    try:
        cholesky(a)
    except NonDefiniePositive:
        return False
    return True


def log_determinant(a):
    return 2.0 * sum(math.log(bas[i]) for i, bas in enumerate(cholesky(a)))


def tirage_glouton(noyau, k):
    """Sélection gloutonne du déterminant maximal de taille k (égalités départagées par l'indice)."""
    choisis = []
    for _ in range(min(k, len(noyau))):
        meilleur, valeur = None, -math.inf
        for i in range(len(noyau)):
            if i in choisis:
                continue
            indices = choisis + [i]
            try:
                v = log_determinant([[noyau[a][b] for b in indices] for a in indices])
            except NonDefiniePositive:
                continue
            if v > valeur + 1e-12:
                meilleur, valeur = i, v
        if meilleur is None:
            break
        choisis.append(meilleur)
    return choisis


# --- paires, consigne de fusion, validation de la fille ---------------------------------------------------------
def ponts(a, b):
    return sorted({normaliser_texte(x) for x in a.operateurs} & {normaliser_texte(x) for x in b.operateurs})


def consigne_fusion(a, b, ponts_communs, texte_memoire="", selection="seuil", alpha=0.05):
    morceaux = [
        "Tu es l'agent de recombinaison du pôle. Fusionne les deux fiches survivantes ci-dessous (fichier `parents.json`) "
        f"par le pont commun « {', '.join(ponts_communs)} », en reliant leurs domaines ({', '.join(a.domaines)} ; "
        f"{', '.join(b.domaines)}).",
        "Fiche A :\n" + json.dumps(a.vue_publique(), ensure_ascii=False, sort_keys=True, indent=1),
        "Fiche B :\n" + json.dumps(b.vue_publique(), ensure_ascii=False, sort_keys=True, indent=1),
        "Exigences : la fille prédit plus que ses parents — champ `ce_que_la_fille_predit_de_plus` non vide, prédiction "
        "signée et chiffrée différente de celles de A et de B, seuil qui peut échouer, sévérité attendue dans ]0 ; 1[ ; "
        "ses contraintes ne contredisent pas celles des parents. Réponds par un bloc ```json {\"fille\": {...}}``` avec "
        "les champs de la fiche (sans identifiant ni parents : l'orchestrateur les pose).",
    ]
    if selection == "pari":
        morceaux.append(f"Sélection par pari : la fille engage une loi prédictive (`loi_predictive`) ; sa sévérité est "
                        f"l'α du pôle ({alpha}) ; elle ne sera promue que si elle bat ses parents et leurs enveloppes "
                        "(mélange, enveloppe harmonique, concaténations si/sinon) avec une marge par tirage.")
    if texte_memoire:
        morceaux.append("Mémoire du pôle :\n" + texte_memoire)
    return "\n\n".join(morceaux)


def valider_fille(donnees, a, b, identifiant, source):
    """Rend (Fiche, None) si la fille est recevable, sinon (None, motif)."""
    if not isinstance(donnees, dict):
        return None, "bloc « fille » absent"
    champs = {k: v for k, v in donnees.items() if k not in ("identifiant", "parents", "statut", "temoin", "source")}
    champs.update(identifiant=identifiant, parents=[a.identifiant, b.identifiant], source=source, statut="proposee")
    try:
        fille = Fiche.depuis_dict(champs).valider()
    except (FicheInvalide, TypeError) as e:
        return None, str(e)
    if not fille.ce_que_la_fille_predit_de_plus.strip():
        return None, "la fille ne dit pas ce qu'elle prédit de plus"
    if signature_prediction(fille.vers_dict()) in (signature_prediction(a.vers_dict()), signature_prediction(b.vers_dict())):
        return None, "la prédiction de la fille est celle d'un parent"
    if conflits(fille.contraintes, a.contraintes) or conflits(fille.contraintes, b.contraintes):
        return None, "contraintes de la fille contradictoires avec un parent"
    return fille, None


def _domaine_estime(f):
    return normaliser_texte(f.domaines[0]) if f.domaines else ""


def _paires_valides(candidates, deja):
    valides, ecartees = [], []
    for a, b in itertools.combinations(candidates, 2):
        cle = tuple(sorted((a.identifiant, b.identifiant)))
        pont, contradiction = ponts(a, b), conflits(a.contraintes, b.contraintes)
        if cle in deja or not pont or contradiction:
            ecartees.append({"paire": cle, "deja_fusionnee": cle in deja, "pont": pont, "conflits": contradiction})
            continue
        valides.append((0.0, -a.aptitude() * b.aptitude(), cle, a, b, pont))
    return valides, ecartees


def tirage_stratifie(candidates, deja, max_paires, rng, valides=None):
    """Rend (paires choisies [(similarité, −qq, clé, a, b, pont)], paires écartées) : R-527, voir l'en-tête."""
    ecartees = []
    if valides is None:
        valides, ecartees = _paires_valides(candidates, deja)
    strates = {}
    for p in valides:
        strates.setdefault(tuple(sorted((_domaine_estime(p[3]), _domaine_estime(p[4])))), []).append(p)
    ordre = sorted(strates)
    rng.shuffle(ordre)
    choisies = []
    while len(choisies) < max_paires and any(strates[s] for s in ordre):
        for s in ordre:
            if strates[s] and len(choisies) < max_paires:
                choisies.append(strates[s].pop(rng.randrange(len(strates[s]))))
    return choisies, ecartees


def tirage_marchepieds(candidates, deja, max_paires, rng, preuve=None, part=0.5):
    """Marchepieds (v4) puis strates ; `preuve(identifiant)` rend la preuve d'une survivante (log W cumulé)."""
    valides, ecartees = _paires_valides(candidates, deja)
    preuve = preuve or (lambda ident: 0.0)
    marchepieds = sorted((f for f in candidates if f.parents), key=lambda f: (-preuve(f.identifiant), f.identifiant))
    voulues, choisies = math.ceil(max_paires * part), []
    for m in marchepieds:
        if len(choisies) >= voulues:
            break
        options = [p for p in valides if m.identifiant in p[2] and p not in choisies]
        if options:
            choisies.append(options[rng.randrange(len(options))])
    reste = [p for p in valides if p not in choisies]
    autres, _ = tirage_stratifie(candidates, deja, max_paires - len(choisies), rng, valides=reste)
    return choisies + autres, ecartees, [p[2] for p in choisies]


def recombiner(pool, adaptateur, config, dossier, budget, generation, k=4, max_paires=3, gamma=1e-3, memoire=None,
               deja_fusionnees=None, tirage=None):
    """Tire, filtre, fait fusionner ; rend {"filles": [...], "refusees": [...], "rapport": {...}}."""
    deja = deja_fusionnees if deja_fusionnees is not None else set()
    tirage = tirage or getattr(config, "tirage_recombinaison", "noyau_corrige")
    candidates = sorted((f for f in pool if f.temoin is None and f.statut == "survit"), key=lambda f: f.identifiant)
    rapport = {"candidates": [f.identifiant for f in candidates], "paires": [], "ecartees": [], "tirage_methode": tirage}
    if len(candidates) < 2:
        return {"filles": [], "refusees": [], "rapport": dict(rapport, motif="moins de deux survivantes")}
    if tirage == "stratifie_marchepieds":
        rng = random.Random(graine_derivee(config.graine, "recombinaison-marchepieds", generation))

        def preuve(ident):
            if memoire is None or ident not in memoire.classe_de:
                return 0.0
            return memoire.classes[memoire.classe_de[ident]]["cumul"]
        paires, rapport["ecartees"], rapport["marchepieds"] = tirage_marchepieds(candidates, deja, max_paires, rng, preuve)
        rapport["tirage"] = sorted({p[2][0] for p in paires} | {p[2][1] for p in paires})
        if not paires:
            rapport["motif"] = "abstention : aucune paire valide"
        return _fusionner(paires, adaptateur, config, dossier, budget, generation, memoire, deja, rapport)
    if tirage == "stratifie":
        rng = random.Random(graine_derivee(config.graine, "recombinaison-stratifiee", generation))
        paires, rapport["ecartees"] = tirage_stratifie(candidates, deja, max_paires, rng)
        rapport["tirage"] = sorted({p[2][0] for p in paires} | {p[2][1] for p in paires})
        if not paires:
            rapport["motif"] = "abstention : aucune paire valide"
        return _fusionner(paires, adaptateur, config, dossier, budget, generation, memoire, deja, rapport)
    if tirage != "noyau_corrige":
        raise ValueError(f"tirage de recombinaison inconnu : {tirage!r}")
    q = [f.aptitude() for f in candidates]
    s = noyau_diversite(vecteurs_domaine([f.domaines for f in candidates]))
    noyau = noyau_corrige(s, q, gamma)
    cholesky(noyau)
    choisis = tirage_glouton(noyau, k)
    rapport["tirage"] = [candidates[i].identifiant for i in choisis]
    paires = []
    for i, j in itertools.combinations(sorted(choisis), 2):
        a, b = candidates[i], candidates[j]
        cle = tuple(sorted((a.identifiant, b.identifiant)))
        pont, contradiction = ponts(a, b), conflits(a.contraintes, b.contraintes)
        if cle in deja or not pont or contradiction:
            rapport["ecartees"].append({"paire": cle, "deja_fusionnee": cle in deja, "pont": pont,
                                        "conflits": contradiction})
            continue
        paires.append((s[i][j], -q[i] * q[j], cle, a, b, pont))
    paires.sort(key=lambda p: p[:3])
    return _fusionner(paires[:max_paires], adaptateur, config, dossier, budget, generation, memoire, deja, rapport)


def _fusionner(paires, adaptateur, config, dossier, budget, generation, memoire, deja, rapport):
    filles, refusees, texte_memoire = [], [], (memoire.texte_consigne("recombinaison") if memoire else "")
    for numero, (sij, _, cle, a, b, pont) in enumerate(paires, 1):
        if not budget.reserver(config.plafond_recombinaison_usd):
            rapport["arret_budget"] = True
            break
        sous = os.path.join(dossier, f"paire-{numero:02d}")
        os.makedirs(sous, exist_ok=False)
        ecrire_scelle(os.path.join(sous, "parents.json"), json_canonique(
            {"a": a.vue_publique(), "b": b.vue_publique(), "ponts": pont, "generation": generation,
             "selection": config.selection, "alpha": config.alpha}))
        consigne = consigne_fusion(a, b, pont, texte_memoire, config.selection, config.alpha)
        traces = dossier_traces(sous)  # v7, version 5 : traces de l'orchestrateur hors du dossier de l'agent
        ecrire_scelle(os.path.join(traces, "consigne.txt"), consigne)
        res = adaptateur.lancer("recombinaison", consigne, sous, config.plafond_recombinaison_usd,
                                config.max_tours_recombinaison, modele=config.modele_recombinaison)
        budget.regler(config.plafond_recombinaison_usd, res.cout_declare_usd)
        ecrire_scelle(os.path.join(traces, "reponse.txt"), caviarder(res.texte_final)[0])
        deja.add(cle)
        bloc = extraire_bloc_json(res.texte_final, "fille") or {}
        fille, motif = valider_fille(bloc.get("fille"), a, b, f"fille-g{generation:02d}-{numero:02d}",
                                     f"recombinaison:{config.modele_recombinaison}")
        entree = {"paire": cle, "pont": pont, "similarite_domaine": round(sij, 6), "consigne": os.path.relpath(
            os.path.join(traces, "consigne.txt"), os.path.abspath(dossier)), "cout": res.cout_declare_usd}
        if fille is None:
            refusees.append(dict(entree, motif=motif, proposition=bloc.get("fille")))
        else:
            filles.append(fille)
            entree["fille"] = fille.identifiant
        rapport["paires"].append(entree)
    return {"filles": filles, "refusees": refusees, "rapport": rapport}
