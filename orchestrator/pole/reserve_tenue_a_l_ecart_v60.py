"""Réserve par empreinte des données tenues à l'écart, version 60 (fichier neuf, R12 ; tâche A3 du tour fermé).

Préenregistrement : `prereg/preenregistrement-tour-ferme-v1-brouillon1.md`, section 5.2. La réserve est faite **avant** la
course et **avant** le scellement du préenregistrement, par la session qui garde les données privées ; elle ne dépend ni de la
graine scellée ni d'aucune issue :

    une tâche t est réservée  ⇔  int(sha256(ETIQUETTE + t).hexdigest(), 16) % MODULE == 0

(ETIQUETTE = « tour-ferme-v1|tenue-a-l-ecart| », MODULE = 3 : environ un tiers des tâches). Tous les épisodes d'une tâche
réservée vont aux données tenues à l'écart (« T ») ; les autres au reste. Tâches entières d'un même côté : aucune tâche de T
n'apparaît dans ce que voient les proposeurs ou le juge.

Sorties (dossier neuf, chaque fichier scellé par son compagnon `.sha256`) : `tenue-a-l-ecart.json`, `reste.json`,
`taches-reservees.json`, `manifeste-reserve-v60.json` (règle, empreintes de l'entrée et des sorties, comptes). **Aucun contenu
n'est imprimé** : la ligne de commande rend les empreintes et les comptes seulement (ce que le préenregistrement recopie).

Gardes (R5 ; essais `essais/test_v60_reserve_tenue_a_l_ecart.py`) : sortie existante, entrée qui n'est pas un fichier régulier
(lien compris), épisode sans tâche ou sans identifiant, identifiant en double, réserve vide ou reste vide → `ReserveRefusee`
(aucun repli). `verifier_reserve` (au montage de T dans le bac à sable) relit le manifeste à l'empreinte attendue, vérifie le
sceau et l'empreinte de chaque sortie, puis **recalcule la règle** sur chaque tâche des deux côtés ; tout écart → refus.
`taches_reservees_dans` cherche les tâches réservées dans un contexte servi (garde 11 du préenregistrement).

Bibliothèque standard seule ; aucun réseau.
"""

import argparse
import hashlib
import json
import os
import stat
import sys

from .outils import ecrire_json_scelle, verifier_scelle

VERSION = "reserve-tenue-a-l-ecart-v60"
ETIQUETTE = "tour-ferme-v1|tenue-a-l-ecart|"
MODULE = 3
NOM_T, NOM_RESTE, NOM_TACHES, NOM_MANIFESTE = ("tenue-a-l-ecart.json", "reste.json", "taches-reservees.json",
                                               "manifeste-reserve-v60.json")


class ReserveRefusee(ValueError):
    """Entrée, sortie ou vérification de la réserve refusée (motif dit ; aucun repli)."""


def tache_reservee(tache):
    """Vrai si la tâche est réservée (règle gelée, indépendante de toute graine et de toute issue)."""
    if not isinstance(tache, str) or not tache:
        raise ReserveRefusee(f"tâche : texte non vide attendu (reçu {tache!r})")
    return int(hashlib.sha256((ETIQUETTE + tache).encode("utf-8")).hexdigest(), 16) % MODULE == 0


def _lire_entree(chemin):
    try:
        st = os.lstat(chemin)
    except OSError as e:
        raise ReserveRefusee(f"entrée absente : {chemin} ({type(e).__name__})") from None
    if not stat.S_ISREG(st.st_mode):
        raise ReserveRefusee(f"entrée : pas un fichier régulier (lien ou autre) : {chemin}")
    with open(chemin, "rb") as f:
        octets = f.read()
    try:
        return json.loads(octets.decode("utf-8")), hashlib.sha256(octets).hexdigest()
    except (UnicodeDecodeError, ValueError) as e:
        raise ReserveRefusee(f"entrée : JSON illisible ({type(e).__name__})") from None


def _episodes(objet, cle_instances):
    if isinstance(objet, list):
        return objet
    if isinstance(objet, dict) and isinstance(objet.get(cle_instances), list):
        return objet[cle_instances]
    raise ReserveRefusee(f"entrée : liste d'épisodes, ou objet portant la liste « {cle_instances} », attendus")


def _comptes(episodes, cle_tache):
    par_moniteur = {}
    for e in episodes:
        issues = e.get("issues")
        if isinstance(issues, dict):
            for m in issues:
                par_moniteur[m] = par_moniteur.get(m, 0) + 1
    return {"episodes": len(episodes), "taches": len({e[cle_tache] for e in episodes}),
            "episodes_par_moniteur": dict(sorted(par_moniteur.items()))}


def reserver(entree, sortie, *, cle_tache="tache", cle_identifiant="identifiant", cle_instances="instances"):
    """Fait la réserve ; écrit les quatre fichiers scellés dans `sortie` (neuve) ; rend le résumé (empreintes et comptes,
    aucun contenu), dont `manifeste_sha256`."""
    if os.path.lexists(sortie):
        raise ReserveRefusee(f"sortie {sortie} déjà présente (R12 : on n'écrase jamais)")
    objet, sha_entree = _lire_entree(entree)
    episodes = _episodes(objet, cle_instances)
    vus = set()
    for k, e in enumerate(episodes):
        if not isinstance(e, dict):
            raise ReserveRefusee(f"épisode n° {k} : objet attendu")
        if not isinstance(e.get(cle_tache), str) or not e.get(cle_tache):
            raise ReserveRefusee(f"épisode n° {k} : champ « {cle_tache} » absent ou vide (la réserve se fait par tâche)")
        ident = e.get(cle_identifiant)
        if not isinstance(ident, str) or not ident:
            raise ReserveRefusee(f"épisode n° {k} : champ « {cle_identifiant} » absent ou vide")
        if ident in vus:
            raise ReserveRefusee(f"identifiant d'épisode en double (n° {k}) : refus")
        vus.add(ident)
    t = [e for e in episodes if tache_reservee(e[cle_tache])]
    reste = [e for e in episodes if not tache_reservee(e[cle_tache])]
    if not t or not reste:
        raise ReserveRefusee(f"réserve dégénérée ({len(t)} épisodes réservés, {len(reste)} au reste) : refus, aucun repli")
    taches = sorted({e[cle_tache] for e in t})
    os.makedirs(sortie)
    shas = {"tenue_a_l_ecart": ecrire_json_scelle(os.path.join(sortie, NOM_T), {"version": VERSION, "episodes": t}),
            "reste": ecrire_json_scelle(os.path.join(sortie, NOM_RESTE), {"version": VERSION, "episodes": reste}),
            "taches_reservees": ecrire_json_scelle(os.path.join(sortie, NOM_TACHES), {"version": VERSION, "taches": taches})}
    manifeste = {"version": VERSION, "regle": {"etiquette": ETIQUETTE, "module": MODULE,
                                               "enonce": "tâche réservée ⇔ int(sha256(etiquette + tâche), 16) % module == 0"},
                 "cles": {"tache": cle_tache, "identifiant": cle_identifiant, "instances": cle_instances},
                 "entree_sha256": sha_entree,
                 "fichiers": {NOM_T: shas["tenue_a_l_ecart"], NOM_RESTE: shas["reste"], NOM_TACHES: shas["taches_reservees"]},
                 "comptes": {"entree": _comptes(episodes, cle_tache), "tenue_a_l_ecart": _comptes(t, cle_tache),
                             "reste": _comptes(reste, cle_tache)}}
    sha_m = ecrire_json_scelle(os.path.join(sortie, NOM_MANIFESTE), manifeste)
    return {"version": VERSION, "manifeste_sha256": sha_m, "entree_sha256": sha_entree, "fichiers": manifeste["fichiers"],
            "comptes": manifeste["comptes"]}


def _lire_verifie(chemin, sha_attendue, quoi):
    try:
        st = os.lstat(chemin)
    except OSError:
        raise ReserveRefusee(f"{quoi} : fichier absent ({chemin})") from None
    if not stat.S_ISREG(st.st_mode):
        raise ReserveRefusee(f"{quoi} : pas un fichier régulier : {chemin}")
    if not verifier_scelle(chemin):
        raise ReserveRefusee(f"{quoi} : sceau compagnon absent ou faux")
    with open(chemin, "rb") as f:
        octets = f.read()
    sha = hashlib.sha256(octets).hexdigest()
    if sha != sha_attendue:
        raise ReserveRefusee(f"{quoi} : empreinte {sha[:16]}… ≠ empreinte attendue {str(sha_attendue)[:16]}… : refus")
    return json.loads(octets.decode("utf-8"))


def verifier_reserve(dossier, manifeste_sha256):
    """Vérification au montage : manifeste à l'empreinte attendue (celle du préenregistrement), sceau et empreinte de chaque
    sortie, puis la règle recalculée sur chaque tâche des deux côtés et la liste des tâches réservées. Rend le manifeste."""
    m = _lire_verifie(os.path.join(dossier, NOM_MANIFESTE), manifeste_sha256, "manifeste de la réserve")
    if m.get("version") != VERSION or m.get("regle", {}).get("etiquette") != ETIQUETTE or m["regle"].get("module") != MODULE:
        raise ReserveRefusee("manifeste d'une autre version ou d'une autre règle : refus")
    cle = m["cles"]["tache"]
    t = _lire_verifie(os.path.join(dossier, NOM_T), m["fichiers"][NOM_T], "données tenues à l'écart")["episodes"]
    reste = _lire_verifie(os.path.join(dossier, NOM_RESTE), m["fichiers"][NOM_RESTE], "reste")["episodes"]
    taches = _lire_verifie(os.path.join(dossier, NOM_TACHES), m["fichiers"][NOM_TACHES], "tâches réservées")["taches"]
    if any(not tache_reservee(e[cle]) for e in t):
        raise ReserveRefusee("un épisode des données tenues à l'écart appartient à une tâche non réservée : refus")
    if any(tache_reservee(e[cle]) for e in reste):
        raise ReserveRefusee("un épisode du reste appartient à une tâche réservée : refus")
    if sorted({e[cle] for e in t}) != list(taches):
        raise ReserveRefusee("liste des tâches réservées incohérente avec les données tenues à l'écart : refus")
    return m


def taches_reservees_dans(texte, taches):
    """Tâches réservées présentes dans un texte servi (contexte d'un proposeur, monde du juge) ; liste vide si aucune."""
    return sorted(t for t in set(taches) if t and t in texte)


def principal(argv=None):
    a = argparse.ArgumentParser(description="réserve par empreinte des données tenues à l'écart (v60) ; aucun contenu imprimé")
    a.add_argument("entree")
    a.add_argument("sortie")
    a.add_argument("--cle-tache", default="tache")
    a.add_argument("--cle-identifiant", default="identifiant")
    a.add_argument("--cle-instances", default="instances")
    args = a.parse_args(argv)
    try:
        r = reserver(args.entree, args.sortie, cle_tache=args.cle_tache, cle_identifiant=args.cle_identifiant,
                     cle_instances=args.cle_instances)
    except ReserveRefusee as e:
        print(json.dumps({"arret": str(e)[:2000]}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


__all__ = ("reserver", "verifier_reserve", "tache_reservee", "taches_reservees_dans", "principal", "ReserveRefusee",
           "VERSION", "ETIQUETTE", "MODULE")
