#!/usr/bin/env python3
"""H03-v2 — les 11 contrôles de schéma de la préinscription (section 5),
refaits sur le fichier d'analyse seul (lu comme du texte).

Utilisé par construire.py et par analyse.py.
controler(chemin) renvoie un dictionnaire {numéro: (ok, détail)} ;
n_violations_schema = nombre de contrôles violés (0 à 11).
"""
import csv
import re

COLONNES = ["millesime", "t_millesime", "mois_titre", "t_premier_F", "horizon", "cible",
            "t_cible", "projection", "millesime_precedent", "projection_precedente",
            "millesime_realise", "t_lecture", "realise", "revision", "erreur"]
LETTRE_TRIM = {"W": 1, "G": 2, "S": 3, "A": 4}
TRIM_LETTRE = {v: k for k, v in LETTRE_TRIM.items()}
T_MAX = 8106


def liste_figee():
    codes = [f"{l}{a % 100:02d}" for a in range(1999, 2026) for l in "WGSA"]
    return codes + ["W26", "G26", "S26"]


def t_du_code(code):
    """Numéro de trimestre tiré du code (lettre + deux chiffres d'année) ; None si code invalide."""
    if not re.fullmatch(r"[WGSA]\d\d", code or ""):
        return None
    yy = int(code[1:])
    annee = 1999 if yy == 99 else 2000 + yy
    return 4 * annee + (LETTRE_TRIM[code[0]] - 1)


def code_du_t(t):
    annee, reste = divmod(t, 4)
    return f"{TRIM_LETTRE[reste + 1]}{annee % 100:02d}"


def periode_du_t(t):
    annee, reste = divmod(t, 4)
    return f"{annee}-Q{reste + 1}"


def _entier(s):
    return int(s) if re.fullmatch(r"-?\d+", s or "") else None


def _decimal(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def controler(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        lecteur = csv.reader(f)
        entete = next(lecteur)
        brut = [ligne for ligne in lecteur]
    res = {}
    figee = set(liste_figee())

    # 1. Les 15 colonnes, dans cet ordre, avec ces noms exacts
    ok1 = entete == COLONNES and all(len(l) == len(COLONNES) for l in brut)
    res[1] = (ok1, f"en-tête lu : {entete}" if not ok1 else "15 colonnes conformes")
    if entete != COLONNES or not all(len(l) == len(COLONNES) for l in brut):
        # sans les bonnes colonnes, les autres contrôles ne peuvent pas être faits : comptés violés
        for n in range(2, 12):
            res[n] = (False, "non évaluable : colonnes non conformes")
        return res
    L = [dict(zip(COLONNES, l)) for l in brut]

    # 2. 444 lignes ; chaque couple (millesime, horizon) une fois ; 111 millésimes de la liste figée
    couples = [(l["millesime"], l["horizon"]) for l in L]
    mills = {l["millesime"] for l in L}
    ok = (len(L) == 444 and len(set(couples)) == len(couples) and len(mills) == 111
          and mills <= figee and all(l["horizon"] in ("1", "2", "3", "4") for l in L)
          and set(couples) == {(m, str(h)) for m in mills for h in (1, 2, 3, 4)})
    res[2] = (ok, f"{len(L)} lignes, {len(set(couples))} couples distincts, {len(mills)} millésimes")

    # 3. t_millesime tiré du code ; t_cible = t_millesime + horizon ; cible cohérente
    mauvais = 0
    for l in L:
        tm, h, tc = _entier(l["t_millesime"]), _entier(l["horizon"]), _entier(l["t_cible"])
        if (tm is None or h is None or tc is None or tm != t_du_code(l["millesime"])
                or tc != tm + h or l["cible"] != periode_du_t(tc)):
            mauvais += 1
    res[3] = (mauvais == 0, f"{mauvais} ligne(s) en défaut")

    # 4. mois_titre, quand il n'est pas vide, vaut 3 × (numéro du trimestre du millésime)
    mauvais = remplies = 0
    for l in L:
        if l["mois_titre"] != "":
            remplies += 1
            tm = t_du_code(l["millesime"])
            m = _entier(l["mois_titre"])
            if tm is None or m is None or m != 3 * (tm % 4 + 1):
                mauvais += 1
    res[4] = (mauvais == 0, f"{mauvais} ligne(s) en défaut sur {remplies} lignes où mois_titre est rempli")

    # 5. t_premier_F, quand il n'est pas vide, entre t_millesime − 2 et t_millesime + 1
    mauvais = remplies = 0
    for l in L:
        if l["t_premier_F"] != "":
            remplies += 1
            tm, tf = _entier(l["t_millesime"]), _entier(l["t_premier_F"])
            if tm is None or tf is None or not (tm - 2 <= tf <= tm + 1):
                mauvais += 1
    res[5] = (mauvais == 0, f"{mauvais} ligne(s) en défaut sur {remplies} lignes où t_premier_F est rempli")

    # 6. projection, projection_precedente, realise : vides, ou nombres entre −5 et 15, au plus une décimale
    mauvais = 0
    for l in L:
        for c in ("projection", "projection_precedente", "realise"):
            s = l[c]
            if s == "":
                continue
            if not re.fullmatch(r"-?\d+(\.\d)?", s) or not (-5 <= float(s) <= 15):
                mauvais += 1
    res[6] = (mauvais == 0, f"{mauvais} cellule(s) en défaut")

    # 7. revision vide ssi projection ou projection_precedente vide ; sinon = différence à 1e-6 près ; idem erreur
    mauvais = 0
    for l in L:
        for cible, a, b in (("revision", "projection", "projection_precedente"),
                            ("erreur", "realise", "projection")):
            manque = l[a] == "" or l[b] == ""
            if manque != (l[cible] == ""):
                mauvais += 1
            elif not manque:
                x, va, vb = _decimal(l[cible]), _decimal(l[a]), _decimal(l[b])
                if x is None or va is None or vb is None or abs(x - (va - vb)) > 1e-6:
                    mauvais += 1
    res[7] = (mauvais == 0, f"{mauvais} cellule(s) en défaut")

    # 8. t_lecture et millesime_realise vides ssi realise vide ; sinon t_lecture = t_cible + 2, 3 ou 4,
    #    ≤ 8106, et correspond au code millesime_realise
    mauvais = 0
    for l in L:
        vide = l["realise"] == ""
        if (l["t_lecture"] == "") != vide or (l["millesime_realise"] == "") != vide:
            mauvais += 1
        elif not vide:
            tl, tc = _entier(l["t_lecture"]), _entier(l["t_cible"])
            if (tl is None or tc is None or tl - tc not in (2, 3, 4) or tl > T_MAX
                    or t_du_code(l["millesime_realise"]) != tl):
                mauvais += 1
    res[8] = (mauvais == 0, f"{mauvais} ligne(s) en défaut")

    # 9. millesime_precedent = code du numéro t_millesime − 1 (vide pour W99 seulement)
    mauvais = 0
    for l in L:
        tm = _entier(l["t_millesime"])
        if l["millesime"] == "W99":
            attendu = ""
        else:
            attendu = code_du_t(tm - 1) if tm is not None else None
        if l["millesime_precedent"] != attendu:
            mauvais += 1
    res[9] = (mauvais == 0, f"{mauvais} ligne(s) en défaut")

    # 10. Même t_cible ⇒ même realise et même t_lecture
    vus, mauvais = {}, 0
    for l in L:
        cle = l["t_cible"]
        val = (_decimal(l["realise"]) if l["realise"] != "" else None, l["t_lecture"])
        if cle in vus and vus[cle] != val:
            mauvais += 1
        vus.setdefault(cle, val)
    res[10] = (mauvais == 0, f"{mauvais} ligne(s) en défaut ; {len(vus)} trimestres cibles distincts")

    # 11. Pour horizon ≤ 3 : projection_precedente de (v, h) = projection de (millésime précédent, h + 1),
    #     ou les deux sont vides
    index = {(l["millesime"], l["horizon"]): l for l in L}
    mauvais = comparees = 0
    for l in L:
        h = _entier(l["horizon"])
        if h is None or h > 3:
            continue
        autre = index.get((l["millesime_precedent"], str(h + 1)))
        a = l["projection_precedente"]
        b = autre["projection"] if autre is not None else ""
        comparees += 1
        if a == "" and b == "":
            continue
        if a == "" or b == "" or abs(float(a) - float(b)) > 1e-9:
            mauvais += 1
    res[11] = (mauvais == 0, f"{mauvais} ligne(s) en défaut sur {comparees} lignes d'horizon ≤ 3")
    return res


def n_violations(res):
    return sum(1 for ok, _ in res.values() if not ok)


if __name__ == "__main__":
    import os
    import sys
    chemin = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "H03-v2_analyse.csv")
    r = controler(chemin)
    for n in sorted(r):
        print(f"contrôle {n:2d} : {'OK    ' if r[n][0] else 'VIOLÉ '} {r[n][1]}")
    print("n_violations_schema =", n_violations(r))
