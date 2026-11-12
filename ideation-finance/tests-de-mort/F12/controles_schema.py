# -*- coding: utf-8 -*-
"""F12 — les dix contrôles de schéma du § 5 de la préinscription, appliqués au fichier CSV tel qu'écrit.

Module partagé par construire.py et analyse.py. Renvoie {numéro: (réussi, détail)}.
"""
import csv
import datetime as dt
import math

COLONNES = ["date_reunion", "pays", "source", "periode", "d_ois2y_pb", "d_rdt_pays_pb",
            "d_rdt_de_pb", "d_ecart_pb", "surprise_restrictive"]
COUPLES = {("IT", "EAMPD"), ("ES", "EAMPD"), ("FR", "EAMPD"),
           ("FR", "RIKSBANK"), ("NL", "RIKSBANK"), ("FI", "RIKSBANK")}
NUM = ["d_ois2y_pb", "d_rdt_pays_pb", "d_rdt_de_pb", "d_ecart_pb"]


def _periode(d):
    if dt.date(2010, 1, 14) <= d <= dt.date(2012, 9, 6):
        return "crise"
    if dt.date(2012, 10, 4) <= d <= dt.date(2022, 6, 9):
        return "avant"
    if d == dt.date(2022, 7, 21):
        return "annonce"
    if dt.date(2022, 9, 8) <= d <= dt.date(2025, 10, 30):
        return "apres"
    return None


def _num(s):
    """Cellule → flottant, None si vide, 'err' si non numérique."""
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return "err"


def controles(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        lecteur = csv.reader(f)
        entetes = next(lecteur)
        brut = [r for r in lecteur]
    res = {}

    # 1. exactement 882 lignes et les 9 colonnes, dans cet ordre
    ok1 = (len(brut) == 882) and (entetes == COLONNES) and all(len(r) == 9 for r in brut)
    res[1] = (ok1, f"{len(brut)} lignes, en-têtes conformes : {entetes == COLONNES}")
    if entetes != COLONNES or not all(len(r) == 9 for r in brut):
        # sans les bonnes colonnes, les contrôles suivants ne sont pas évaluables : tous comptés en échec
        for k in range(2, 11):
            res[k] = (False, "non évaluable (colonnes non conformes)")
        return res
    L = [dict(zip(COLONNES, r)) for r in brut]
    for l in L:
        for c in NUM:
            l["_" + c] = _num(l[c])

    # 2. clé unique ; pour chaque date, exactement les six couples attendus
    cles = [(l["date_reunion"], l["pays"], l["source"]) for l in L]
    par_date = {}
    for l in L:
        par_date.setdefault(l["date_reunion"], []).append((l["pays"], l["source"]))
    ok2 = (len(set(cles)) == len(cles)) and all(len(v) == 6 and set(v) == COUPLES for v in par_date.values())
    res[2] = (ok2, f"{len(set(cles))} clés distinctes")

    # 3. 147 dates, première 2010-01-14, dernière 2025-10-30 ; par période 33, 87, 1, 26 dates
    dates = sorted(par_date)
    n_per = {}
    for p in ("crise", "avant", "annonce", "apres"):
        n_per[p] = len({l["date_reunion"] for l in L if l["periode"] == p})
    ok3 = (len(dates) == 147 and dates[0] == "2010-01-14" and dates[-1] == "2025-10-30"
           and n_per == {"crise": 33, "avant": 87, "annonce": 1, "apres": 26})
    res[3] = (ok3, f"{len(dates)} dates, {dates[0] if dates else None} → {dates[-1] if dates else None}, {n_per}")

    # 4. periode cohérente avec les bornes de dates du § 4.1
    def _ok4(l):
        try:
            return _periode(dt.date.fromisoformat(l["date_reunion"])) == l["periode"]
        except ValueError:
            return False
    n4 = sum(1 for l in L if not _ok4(l))
    res[4] = (n4 == 0, f"{n4} ligne(s) incohérente(s)")

    # 5. d_ois2y_pb jamais vide et identique sur les six lignes d'une même date
    ois_par_date = {}
    for l in L:
        ois_par_date.setdefault(l["date_reunion"], set()).add(l["d_ois2y_pb"])
    n5 = sum(1 for l in L if not isinstance(l["_d_ois2y_pb"], float))
    n5b = sum(1 for v in ois_par_date.values() if len({_num(s) for s in v}) != 1)
    res[5] = (n5 == 0 and n5b == 0, f"{n5} cellule(s) vide(s)/non numérique(s), {n5b} date(s) non constante(s)")

    # 6. lignes EAMPD : aucune cellule vide ; d_rdt_de_pb identique sur les trois lignes EAMPD d'une date
    ea = [l for l in L if l["source"] == "EAMPD"]
    n6 = sum(1 for l in ea for c in COLONNES if l[c] == "")
    de_ea = {}
    for l in ea:
        de_ea.setdefault(l["date_reunion"], set()).add(l["_d_rdt_de_pb"])
    n6b = sum(1 for v in de_ea.values() if len(v) != 1)
    res[6] = (n6 == 0 and n6b == 0, f"{n6} cellule(s) vide(s), {n6b} date(s) où DE diffère")

    # 7. lignes RIKSBANK : trois cellules vides ensemble ou renseignées ensemble ; DE identique par date
    rk = [l for l in L if l["source"] == "RIKSBANK"]
    n7 = sum(1 for l in rk if len({l[c] == "" for c in ("d_rdt_pays_pb", "d_rdt_de_pb", "d_ecart_pb")}) != 1)
    de_rk = {}
    for l in rk:
        if l["d_rdt_de_pb"] != "":
            de_rk.setdefault(l["date_reunion"], set()).add(l["_d_rdt_de_pb"])
    n7b = sum(1 for v in de_rk.values() if len(v) != 1)
    res[7] = (n7 == 0 and n7b == 0, f"{n7} ligne(s) partiellement vide(s), {n7b} date(s) où DE diffère")

    # 8. |d_ecart_pb − (d_rdt_pays_pb − d_rdt_de_pb)| ≤ 1e-6 partout où renseigné
    n8 = 0
    for l in L:
        a, b, c = l["_d_ecart_pb"], l["_d_rdt_pays_pb"], l["_d_rdt_de_pb"]
        if all(isinstance(v, float) for v in (a, b, c)):
            if not abs(a - (b - c)) <= 1e-6:
                n8 += 1
        elif any(v == "err" for v in (a, b, c)):
            n8 += 1
    res[8] = (n8 == 0, f"{n8} ligne(s) en défaut")

    # 9. surprise_restrictive vaut 1 si et seulement si d_ois2y_pb > 0
    n9 = 0
    for l in L:
        x = l["_d_ois2y_pb"]
        if l["surprise_restrictive"] not in ("0", "1") or not isinstance(x, float) \
                or (l["surprise_restrictive"] == "1") != (x > 0):
            n9 += 1
    res[9] = (n9 == 0, f"{n9} ligne(s) en défaut")

    # 10. valeurs numériques renseignées finies et de valeur absolue < 300
    n10 = 0
    for l in L:
        for c in NUM:
            v = l["_" + c]
            if v is None:
                continue
            if v == "err" or not math.isfinite(v) or not abs(v) < 300:
                n10 += 1
    res[10] = (n10 == 0, f"{n10} cellule(s) en défaut")
    return res
