"""Tableau minimal entre sous-sessions (R-598, M8 ; v53).

Après la passe 1, un **programme** (aucun modèle) construit le tableau d'une case (même texte, même bras) : pour chaque fiche
de la passe 1 de cette case **munie d'un passeport** de l'aiguilleur, son titre et un résumé d'une ligne (champ injecté,
`tableau.champ_resume`, retours à la ligne remplacés par une espace, tronqué). Longueurs maximales injectées (S21, aucun
défaut). Jamais la fiche entière ; jamais une entrée d'une autre case. La passe « tableau » reçoit ce tableau au début.

`verifier_tableau` (A18, gardes R5 lignes 13 à 15), jouée sur tout tableau avant de le servir : entrée étiquetée d'une autre
case (la garde vérifie l'étiquette de case, pas la provenance) ; titre d'une fiche sans passeport ; entrée au-delà de S21 ;
champ autre que titre et résumé → `TableauRefuse` (arrêt de la passe « tableau », tableau à reconstruire, incident).
"""

import json

VERSION = "tableau-minimal-v53"


class TableauRefuse(RuntimeError):
    pass


def une_ligne(texte, maximum):
    t = " ".join(str(texte).split())
    return t if len(t) <= maximum else t[:maximum - 1].rstrip() + "…"


def construire(fiches, case, aiguilleur, *, champ_titre, champ_resume, longueur_max_titre, longueur_max_resume):
    for nom, v in (("longueur_max_titre", longueur_max_titre), ("longueur_max_resume", longueur_max_resume)):
        if isinstance(v, bool) or not isinstance(v, int) or v < 2:
            raise TableauRefuse(f"S21 {nom} : entier ≥ 2 exigé, aucun défaut")
    entrees = []
    for f in fiches:
        if list(f["meta"]["case"]) != list(case) or f["meta"]["passe"] != 1 or not aiguilleur.a_passeport(f):
            continue
        entrees.append({"case": list(case), "ident": f["ident"],
                        "titre": une_ligne(f["contenu"].get(champ_titre, ""), longueur_max_titre),
                        "resume": une_ligne(f["contenu"].get(champ_resume, ""), longueur_max_resume)})
    return {"version": VERSION, "case": list(case), "entrees": entrees}


def verifier_tableau(tableau, case, aiguilleur, fiches_par_ident, *, longueur_max_titre, longueur_max_resume):
    for e in tableau["entrees"]:
        if set(e) - {"case", "ident", "titre", "resume"}:
            raise TableauRefuse("A18 : champ hors du tableau minimal (" + ", ".join(sorted(set(e) - {"case", "ident", "titre", "resume"})) + ")")
        if list(e.get("case", [])) != list(case):
            raise TableauRefuse(f"A18 : entrée étiquetée d'une autre case ({e.get('case')!r} ≠ {list(case)!r})")
        f = fiches_par_ident.get(e.get("ident"))
        if f is None or not aiguilleur.a_passeport(f):
            raise TableauRefuse(f"A18 : titre d'une fiche sans passeport de l'aiguilleur ({e.get('ident')!r})")
        if not isinstance(e.get("titre"), str) or len(e["titre"]) > longueur_max_titre:
            raise TableauRefuse(f"A18 : titre au-delà de S21 ({len(str(e.get('titre')))} > {longueur_max_titre})")
        if not isinstance(e.get("resume"), str) or len(e["resume"]) > longueur_max_resume or "\n" in e["resume"]:
            raise TableauRefuse(f"A18 : résumé au-delà de S21 ou sur plusieurs lignes ({len(str(e.get('resume')))} > {longueur_max_resume})")
    return True


def texte_servi(tableau):
    """Ce que la passe « tableau » reçoit : titres et résumés seulement (ni identifiant, ni case)."""
    return json.dumps([{"titre": e["titre"], "resume": e["resume"]} for e in tableau["entrees"]], ensure_ascii=False, indent=1)
