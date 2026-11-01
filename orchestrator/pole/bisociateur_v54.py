"""Bisociateur à trois bras, version 54 — au-dessus de `bisociateur_v53` (scores, substitut de Gu et Krenn, bras basique
inchangés). Corrections exigées par l'annexe du bras méta (brouillon 1, section 10) et par CL18-17 :

- **I-6** `lire_annexe_meta_v54` contrôle types et signes : niches et structures (identifiants uniques, chaînes), tables
  `communication` et `eloignement` (réels finis pour chaque paire), seuil (réel), bande (deux réels, min ≤ max), poids
  (réel ≥ 0), `structure_forte` (`nombre_min` entier ≥ 1, `types` ⊆ structures).
- **I-9** `contre_lecture` doit citer **deux** empreintes SHA-256 distinctes (brouillon relu et rapport, annexe § 9.5) ;
  `approbation_lazar` un identifiant de décision `R-NNN` (au moins trois chiffres).
- **I-4** définitions servies : clé de configuration `bisociateur.meta.definitions` = `annexe` (le bloc porte
  `definitions_niches` et `definitions_structures` pour **chaque** identifiant ; elles sont servies au lecteur avec la
  liste fermée) ou `consigne` (la consigne figée du lecteur, pièce empreintée, doit contenir chaque identifiant ; vérifié).
- **I-3** S28 : seuils lus dans l'annexe (`accord_min_niche_kappa`, `accord_min_structures_jaccard`) ou injectés ;
  `accord_s28` calcule kappa (règle des marges constantes, `kappa_niches` v53) et Jaccard des structures (règle de S24).
- **I-10** non-vacuité revérifiée à É0 : le bloc `jeu_essai_non_vacuite` de l'annexe (scellée) est rejoué par
  `verifier_non_vacuite` (au moins une paire dans le profil, au moins une hors profil, argmax dans le profil) ; sinon A20.
- **I-1** `valider_niche_v54` : chaque structure doit être un identifiant de la liste fermée **et** son nom doit recopier
  l'identifiant (option A de l'annexe) ; un nom différent est **refusé** (pas de baisse silencieuse de s), compté.
- **I-2** le champ « affirmation centrale » du lecteur est conservé ; le désaccord est lu **par paire, après** le choix des
  paires (`lire_desaccord_entree`, `valider_desaccord`), journalisé à part ; `garde_desaccord_v54` éprouve qu'il n'entre
  jamais dans le score (signature **et** valeur : une fonction de score qui varie avec le désaccord est un arrêt).
- **I-7** cause « aucune paire éligible » et « niches indistinctes sur ce lot » comptées (C12).
- **I-8** n = 2 : la paire va au **bras de priorité 1** (tirage) ; s'il ne peut pas la noter, il est « non produit (paire non
  notable par le bras de priorité 1) » et les deux autres « non produits (effectif) ». Garde « trois paires revendiquées à
  n = 2 » (R5 ligne 16).
- **CL18-17** n est compté **par case** (les paires sont intra-case) ; un bras sans clé de départage est refusé nommément.
"""

import itertools
import json
import math
import re

from . import bisociateur_v53 as b53
from .bisociateur_v53 import (BisociationRefusee, cle_paire, indicateurs_meta, kappa_niches, score_meta, score_repli,  # noqa: F401
                              verifier_paire)
from .outils import extraire_bloc_json

VERSION = "bisociateur-v54"
SHA = re.compile(r"\b[0-9a-f]{64}\b")
DECISION = re.compile(r"\bR-\d{3,}\b")
REPONSES_DESACCORD = ("oui", "non", "indecidable")


def _reel(v):
    return not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(v)


def _identifiants(v, quoi):
    if not isinstance(v, list) or not v or not all(isinstance(x, str) and x for x in v) or len(set(v)) != len(v):
        raise BisociationRefusee(f"A20/I-6 : {quoi} : liste d'identifiants uniques (chaînes) attendue")
    return v


def lire_annexe_meta_v54(chemin, sha256_attendu, *, definitions, texte_consigne_lecteur=None):
    """A20 (v53) + I-6, I-9, I-4. Rend (paramètres, jeu d'essai de non-vacuité ou None)."""
    p = b53.lire_annexe_meta(chemin, sha256_attendu)
    niches = _identifiants(p["niches"], "niches")
    types = _identifiants(p["types_structure"], "types_structure")
    for table in ("communication", "eloignement"):
        if not isinstance(p[table], dict):
            raise BisociationRefusee(f"A20/I-6 : {table} : table attendue")
        for a, b in itertools.combinations(niches, 2):
            if not _reel(p[table].get(b53._niche_cle(a, b))):
                raise BisociationRefusee(f"A20/I-6 : {table} [{a} | {b}] : réel fini exigé")
    if not _reel(p["seuil_communication_faible"]):
        raise BisociationRefusee("A20/I-6 : seuil_communication_faible : réel exigé")
    if not (isinstance(p["bande"], list) and len(p["bande"]) == 2 and all(_reel(x) for x in p["bande"])):
        raise BisociationRefusee("A20/I-6 : bande : deux réels exigés")
    if not _reel(p["poids"]) or p["poids"] < 0:
        raise BisociationRefusee(f"A20/I-6 : poids : réel ≥ 0 exigé (reçu {p['poids']!r}) — un poids négatif ferait sortir du "
                                 "profil des paires qui y sont")
    sf = p["structure_forte"]
    if isinstance(sf["nombre_min"], bool) or not isinstance(sf["nombre_min"], int) or sf["nombre_min"] < 1:
        raise BisociationRefusee("A20/I-6 : structure_forte.nombre_min : entier ≥ 1 exigé")
    if not set(sf["types"]) <= set(types) or not all(isinstance(t, str) for t in sf["types"]):
        raise BisociationRefusee("A20/I-6 : structure_forte.types : sous-ensemble des structures de la grille exigé")
    shas = set(SHA.findall(p["contre_lecture"]))
    if len(shas) < 2:
        raise BisociationRefusee("A20/I-9 : contre_lecture doit citer deux empreintes SHA-256 distinctes (brouillon relu, rapport)")
    if not DECISION.search(p["approbation_lazar"]):
        raise BisociationRefusee("A20/I-9 : approbation_lazar doit citer un identifiant de décision R-NNN")
    if definitions == "annexe":
        for cle, ids in (("definitions_niches", niches), ("definitions_structures", types)):
            d = p.get(cle)
            if not isinstance(d, dict) or not all(isinstance(d.get(i), str) and d[i].strip() for i in ids):
                raise BisociationRefusee(f"A20/I-4 : {cle} : une définition non vide par identifiant exigée")
    elif definitions == "consigne":
        if not isinstance(texte_consigne_lecteur, str):
            raise BisociationRefusee("A20/I-4 : consigne du lecteur absente")
        manquants = [i for i in niches + types if i not in texte_consigne_lecteur]
        if manquants:
            raise BisociationRefusee("A20/I-4 : identifiants absents de la consigne figée du lecteur : " + ", ".join(manquants[:8]))
    else:
        raise BisociationRefusee(f"I-4 : bisociateur.meta.definitions inconnu : {definitions!r}")
    with open(chemin, "r", encoding="utf-8") as f:
        jeu = (extraire_bloc_json(f.read(), "jeu_essai_non_vacuite") or {}).get("jeu_essai_non_vacuite")
    return p, jeu


def liste_servie(p, definitions):
    """Ce que le lecteur de niches reçoit : identifiants, et les définitions si elles viennent de l'annexe (I-4)."""
    servi = {"niches": list(p["niches"]), "structures": list(p["types_structure"])}
    if definitions == "annexe":
        servi["definitions_niches"] = {i: p["definitions_niches"][i] for i in p["niches"]}
        servi["definitions_structures"] = {i: p["definitions_structures"][i] for i in p["types_structure"]}
    return servi


def seuils_s28(p, s28):
    if s28 == "annexe":
        k, j = p.get("accord_min_niche_kappa"), p.get("accord_min_structures_jaccard")
        if not _reel(k) or not _reel(j):
            raise BisociationRefusee("A20/I-3 : S28 lue dans l'annexe : accord_min_niche_kappa et accord_min_structures_jaccard exigés")
        return {"kappa_min": float(k), "jaccard_min": float(j), "source": "annexe"}
    return {"kappa_min": float(s28["kappa_min"]), "jaccard_min": float(s28["jaccard_min"]), "source": "configuration"}


# --- lecture d'un lecteur de niches (I-1, I-2) --------------------------------------------------------------------------------


def valider_niche_v54(lecture, niches, structures):
    """Rend (niche, frozenset de structures, affirmation centrale ou None). Refus nommé (`BisociationRefusee`) : niche hors
    grille, deux niches, structure hors liste, nom de structure différent de son identifiant (I-1, option A)."""
    if not isinstance(lecture, dict) or not isinstance(lecture.get("niche"), str):
        raise BisociationRefusee("lecture de niche : {niche, structures} attendu, une niche par fiche")
    if lecture["niche"] not in niches:
        raise BisociationRefusee(f"niche hors grille (rejetée) : {lecture['niche']!r}")
    st = lecture.get("structures", [])
    if not isinstance(st, list):
        raise BisociationRefusee("structures : liste attendue")
    sortie = set()
    for s in st:
        if isinstance(s, str):
            ident, nom = s, s
        elif isinstance(s, dict):
            ident, nom = s.get("type"), s.get("nom", s.get("type"))
        else:
            raise BisociationRefusee(f"structure illisible (rejetée) : {s!r}")
        if ident not in structures:
            raise BisociationRefusee(f"structure hors liste fermée (rejetée) : {ident!r}")
        if nom != ident:
            raise BisociationRefusee(f"I-1 : nom de structure {nom!r} différent de son identifiant {ident!r} (rejeté, jamais baissé "
                                     "en silence)")
        sortie.add((ident, ident))
    aff = lecture.get("affirmation_centrale")
    return lecture["niche"], frozenset(sortie), (aff if isinstance(aff, str) and aff.strip() else None)


def accord_s28(lectures_1, lectures_2, seuils):
    """S28 sur les fiches lues par les deux lecteurs : kappa de Cohen sur la niche (marges constantes : règle v53), Jaccard
    moyen des structures (règle de S24). Rend {kappa, degenere, jaccard, lisible, ...}."""
    communs = sorted(set(lectures_1) & set(lectures_2))
    k = kappa_niches({i: lectures_1[i][0] for i in communs}, {i: lectures_2[i][0] for i in communs})
    j = b53.accord_jaccard({i: [s[0] for s in lectures_1[i][1]] for i in communs},
                           {i: [s[0] for s in lectures_2[i][1]] for i in communs})
    lisible = (k["kappa"] is not None and j["jaccard_moyen"] is not None and k["kappa"] + 1e-12 >= seuils["kappa_min"]
               and j["jaccard_moyen"] + 1e-12 >= seuils["jaccard_min"])
    return {"n": len(communs), "kappa": k["kappa"], "degenere": k["degenere"], "jaccard": j["jaccard_moyen"],
            "jaccard_exclues": j["exclues"], "seuils": seuils, "lisible": bool(lisible),
            "marque": None if lisible else "niches non lisibles (bras gardé, R-638)"}


def retenir_meta(l1, l2, regle_divergence, regle_structures):
    """Niche et structures retenues pour une fiche (choix 10 / I-5) ; None si la fiche est écartée."""
    if l1 is None or (l2 is None and regle_divergence == "fiche_ecartee"):
        return None
    if l2 is None or l1[0] != l2[0]:
        if regle_divergence == "fiche_ecartee":
            return None
        return l1[0], l1[1]  # premier lecteur
    s = (l1[1] | l2[1]) if regle_structures == "union" else (l1[1] & l2[1])
    return l1[0], s


# --- non-vacuité (I-10, garde 22a rejouée à É0) ----------------------------------------------------------------------------------


def verifier_non_vacuite(p, jeu):
    """Rejoue le jeu d'essai de l'annexe : au moins une paire dans le profil, au moins une hors profil (paires de niches
    différentes), argmax dans le profil. Rend un résumé ; lève `BisociationRefusee` (A20) sinon."""
    if not isinstance(jeu, dict) or len(jeu) < 2:
        raise BisociationRefusee("A20/I-10 : jeu_essai_non_vacuite absent de l'annexe")
    lus = {}
    for ident, f in jeu.items():
        n, s, _ = valider_niche_v54({"niche": f.get("niche"), "structures": f.get("structures", [])}, p["niches"], p["types_structure"])
        lus[ident] = (n, s)
    dans, hors, meme = [], [], 0
    for a, b in itertools.combinations(sorted(lus), 2):
        (na, sa), (nb, sb) = lus[a], lus[b]
        if na == nb:
            meme += 1
            continue
        sc = score_meta(p, na, nb, sa, sb)
        (dans if sc > 0 else hors).append(((1, sc) if sc > 0 else (0,) + score_repli(p, na, nb, sa, sb), (a, b)))
    if not dans:
        raise BisociationRefusee("A20/I-10 : profil vide sur le jeu d'essai (bande de e et seuil de c qui ne se recoupent pas)")
    if not hors:
        raise BisociationRefusee("A20/I-10 : toutes les paires du jeu d'essai sont dans le profil (le profil ne distingue rien)")
    meilleure = max(dans + hors, key=lambda x: x[0])
    if meilleure[0][0] != 1:
        raise BisociationRefusee("A20/I-10 : une paire hors profil est choisie avant une paire du profil")
    return {"dans_profil": len(dans), "hors_profil": len(hors), "meme_niche": meme, "argmax": list(meilleure[1]),
            "score_argmax": meilleure[0][1]}


# --- désaccord, par paire, après le choix (I-2 ; garde R5 ligne 24) ------------------------------------------------------------


def garde_desaccord_v54(fonction_score, p, na, nb, sa, sb):
    """La même paire avec d = oui, non, indécidable reçoit le même score ; la garde v53 (signature) puis l'appel effectif :
    une fonction qui accepte un argument de désaccord (quel que soit son nom : `desaccord`, `d`, ou `**kw`) et en dépend est
    un arrêt."""
    import inspect
    b53.garde_desaccord_hors_score(fonction_score, p, na, nb, sa, sb)
    params = inspect.signature(fonction_score).parameters
    accepte = [n for n, q in params.items() if q.kind == q.VAR_KEYWORD] or [n for n in params if "desaccord" in n or n == "d"]
    if accepte:
        valeurs = set()
        for d in REPONSES_DESACCORD:
            try:
                valeurs.add(fonction_score(p, na, nb, sa, sb, desaccord=d))
            except TypeError:
                valeurs.add(fonction_score(p, na, nb, sa, sb, d=d))
        if len(valeurs) > 1:
            raise BisociationRefusee("R-638 / I-2 : le désaccord entre dans le score du bras méta (scores différents) : arrêt")
    return True


def paires_pour_desaccord(notes_meta, departage, paire_retenue, paires_max):
    """La paire méta retenue puis les suivantes du classement méta (profil d'abord), au plus `paires_max`."""
    ordre = sorted(notes_meta, key=lambda q: (notes_meta[q][0], departage.get(q, 0.0)), reverse=True)
    if paire_retenue in ordre:
        ordre.remove(paire_retenue)
        ordre.insert(0, paire_retenue)
    return ordre[:paires_max]


def entree_desaccord(consigne, aff_a, aff_b):
    return (consigne.rstrip() + "\n\n## Deux affirmations (anonymes)\n```json\n"
            + json.dumps({"a": aff_a, "b": aff_b}, ensure_ascii=False, indent=1) + "\n```\n")


def valider_desaccord(texte):
    bloc = extraire_bloc_json(texte, "desaccord")
    r = (bloc or {}).get("desaccord")
    return r if r in REPONSES_DESACCORD else None


# --- choix des paires (I-7, I-8, CL18-17) -------------------------------------------------------------------------------------


def choisir_paires_v54(fiches, notes_par_bras, ordre_bras, k, aiguilleur, departage, causes_vides=None):
    """Comme v53, avec n compté par case, n = 2 au bras de priorité 1, départage exigé par bras, et causes de non-production
    explicites (`causes_vides` : {bras: cause} quand le bras n'a aucune paire éligible, par exemple « niches indistinctes »)."""
    manquants = [b for b in ordre_bras if b in notes_par_bras and b not in departage]
    if manquants:
        raise BisociationRefusee("clé de départage absente pour le bras : " + ", ".join(manquants))
    par_ident = {f["ident"]: f for f in fiches}
    par_case = {}
    for f in fiches:
        par_case.setdefault(tuple(f["meta"]["case"]), []).append(f["ident"])
    n_max = max((len(v) for v in par_case.values()), default=0)
    choix, non_produits = {b: [] for b in ordre_bras}, {}
    if n_max < 2:
        return choix, {b: "non produit (effectif)" for b in ordre_bras}
    if n_max == 2:  # plusieurs cases à 2 fiches (course) : une seule paire en tout, la mieux notée du bras de priorité 1
        paires = [cle_paire(*v) for v in par_case.values() if len(v) == 2]
        premier = ordre_bras[0] if ordre_bras else None
        for b in ordre_bras:
            non_produits[b] = "non produit (effectif)"
        if premier is not None:
            notees = [q for q in paires if q in notes_par_bras.get(premier, {})]
            notees.sort(key=lambda q: (notes_par_bras[premier][q][0], departage[premier].get(q, 0.0)), reverse=True)
            if notees:
                q = notees[0]
                verifier_paire(par_ident[q[0]], par_ident[q[1]], aiguilleur)
                choix[premier] = [q]
                del non_produits[premier]
            else:
                non_produits[premier] = (causes_vides or {}).get(premier) or "non produit (paire non notable par le bras de priorité 1)"
        verifier_paires_globales(choix, n_max)
        return choix, non_produits
    prises = set()
    for b in ordre_bras:
        notes = notes_par_bras.get(b, {})
        candidates = sorted((q for q in notes if q not in prises), key=lambda q: (notes[q][0], departage[b].get(q, 0.0)), reverse=True)
        for q in candidates[:k]:
            verifier_paire(par_ident[q[0]], par_ident[q[1]], aiguilleur)
            prises.add(q)
            choix[b].append(q)
        if not choix[b]:
            non_produits[b] = (causes_vides or {}).get(b) or ("non produit (aucune paire éligible)" if not notes
                                                              else "non produit (paires éligibles toutes prises)")
    verifier_paires_globales(choix, n_max)
    return choix, non_produits


def verifier_paires_globales(choix, n_max):
    """Garde R5 ligne 16 : deux bras jamais sur la même paire ; à n = 2, une seule paire en tout."""
    toutes = [q for ps in choix.values() for q in ps]
    if len(toutes) != len(set(toutes)):
        raise BisociationRefusee("deux bras sur la même paire")
    if n_max == 2 and len(toutes) > 1:
        raise BisociationRefusee(f"n = 2 : {len(toutes)} paires revendiquées (une seule permise)")
    return True


def compter_c12(bras_decl, non_produits):
    """C12 : bras non produits et leur cause, comptés (I-7)."""
    causes = {}
    for b, d in bras_decl.items():
        cause = d.get("cause") if not d.get("produit") else non_produits.get(b)
        if cause:
            causes[cause] = causes.get(cause, 0) + 1
    return {"bras_non_produits": sum(causes.values()), "causes": causes}
