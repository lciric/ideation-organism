"""Réserve par empreinte des données tenues à l'écart, version 61 (fichier neuf, R12 ; tâche A3) — la v60 durcie (changement
C4 de la contre-lecture, constat I3 : deux voies de fuite).

La règle, la réserve, le manifeste et `verifier_reserve` sont ceux de `pole/reserve_tenue_a_l_ecart_v60.py` (inchangée,
importée). La v61 ajoute, pour la garde 11 :

1. **Orthographe des tâches** (`verifier_orthographe`) : les tâches communes à l'entrée de la réserve (E0) et à la banque
   publique doivent y être écrites à l'identique ; une tâche de l'une qui n'a dans l'autre qu'un homonyme sous forme
   normalisée (même identifiant sans suffixe de version `vN`) est un refus.
2. **Forme normalisée** (`normaliser`, `taches_reservees_dans`) : la recherche d'une tâche réservée dans un texte servi se fait
   sur la chaîne exacte **et** sur la forme normalisée.
3. **Épisodes de T** (`fuites_dans`) : on cherche aussi, dans un texte servi, chaque identifiant d'épisode de T et chaque
   vecteur de traits de T arrondi à 4 décimales (sous deux écritures JSON).
4. **Disjonction par la structure** (`verifier_disjonction`) : M2 ∩ R = ∅ sur les tâches (forme exacte et normalisée) et sur
   les identifiants d'épisodes, épisodes publics compris.
"""

import json
import re

from .reserve_tenue_a_l_ecart_v60 import (ETIQUETTE, MODULE, VERSION as VERSION_V60, ReserveRefusee, reserver, tache_reservee,
                                          verifier_reserve)

VERSION = "reserve-tenue-a-l-ecart-v61"
SUFFIXE_VERSION = re.compile(r"v\d+$")
DECIMALES = 4


def normaliser(tache):
    """Identifiant de tâche sans suffixe de version (« 2506.01290v2 » → « 2506.01290 »), espaces de bord retirés."""
    if not isinstance(tache, str) or not tache:
        raise ReserveRefusee(f"tâche : texte non vide attendu (reçu {tache!r})")
    return SUFFIXE_VERSION.sub("", tache.strip())


def verifier_orthographe(taches_entree, taches_banque):
    """Refus si une tâche de l'un des deux ensembles n'existe dans l'autre que sous une autre orthographe de même forme
    normalisée ; rend les tâches communes (forme exacte)."""
    a, b = set(taches_entree), set(taches_banque)
    na = {normaliser(t): t for t in a}
    nb = {normaliser(t): t for t in b}
    ecarts = sorted(f"{na[n]} ≠ {nb[n]}" for n in set(na) & set(nb) if na[n] != nb[n])
    if ecarts:
        raise ReserveRefusee(f"orthographe des tâches différente entre l'entrée et la banque publique : {ecarts[:10]} : refus")
    return sorted(a & b)


def taches_reservees_dans(texte, taches):
    """Tâches réservées présentes dans un texte servi, sous leur forme exacte ou normalisée ; liste vide si aucune."""
    trouvees = set()
    for t in set(taches):
        if t and (t in texte or normaliser(t) in texte):
            trouvees.add(t)
    return sorted(trouvees)


def _ecritures(vecteur):
    arrondi = [round(float(x), DECIMALES) for x in vecteur]
    return {json.dumps(arrondi), json.dumps(arrondi, separators=(",", ":")), ", ".join(repr(x) for x in arrondi)}


def fuites_dans(texte, taches, episodes_t, *, cle_identifiant="identifiant", cle_traits="z"):
    """Garde 11 sur un contexte servi : tâches réservées (exactes ou normalisées), identifiants d'épisodes de T, vecteurs de
    traits de T arrondis à 4 décimales. Rend {taches, identifiants, traits} (listes vides si rien)."""
    ids = sorted(e[cle_identifiant] for e in episodes_t if isinstance(e.get(cle_identifiant), str) and e[cle_identifiant] in texte)
    traits = sorted({e.get(cle_identifiant) or "?" for e in episodes_t if isinstance(e.get(cle_traits), (list, tuple))
                     and any(w in texte for w in _ecritures(e[cle_traits]))})
    return {"taches": taches_reservees_dans(texte, taches), "identifiants": ids, "traits": traits}


def verifier_disjonction(monde_2, episodes_t, taches_reservees, *, cle_tache="tache", cle_identifiant="identifiant"):
    """M2 ∩ R = ∅ par la structure : aucune tâche réservée (exacte ou normalisée) ni aucun identifiant d'épisode de T dans
    le monde de l'étage 2, épisodes publics compris ; rend les comptes."""
    reservees = set(taches_reservees) | {normaliser(t) for t in taches_reservees}
    ids_t = {e.get(cle_identifiant) for e in episodes_t}
    fuites_t = sorted(e.get(cle_identifiant) or "?" for e in monde_2 if e.get(cle_tache) in reservees or normaliser(e.get(cle_tache)) in reservees)
    fuites_i = sorted(e.get(cle_identifiant) for e in monde_2 if e.get(cle_identifiant) in ids_t)
    if fuites_t or fuites_i:
        raise ReserveRefusee(f"monde de l'étage 2 non disjoint de la réserve : tâches réservées {fuites_t[:10]}, épisodes de T {fuites_i[:10]} : refus")
    return {"episodes_m2": len(monde_2), "episodes_t": len(episodes_t), "taches_reservees": len(set(taches_reservees))}


__all__ = ("normaliser", "verifier_orthographe", "taches_reservees_dans", "fuites_dans", "verifier_disjonction", "reserver",
           "verifier_reserve", "tache_reservee", "ReserveRefusee", "VERSION", "VERSION_V60", "ETIQUETTE", "MODULE")
