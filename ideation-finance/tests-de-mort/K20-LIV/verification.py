#!/usr/bin/env python3
"""K20-LIV -- vérification indépendante.

Écrit par le vérificateur, à partir du seul texte scellé (preenregistrement.md) et du seul fichier d'analyse
(K20-LIV_analyse.csv). N'ouvre aucun autre fichier. N'écrit aucun verdict.

Sortie : verification.json (tous les champs de « champs_verification », en nombres) ; le détail des contrôles de schéma
et les diagnostics hors règle sont imprimés sur la sortie standard.

Usage : python3 -B verification.py
"""
import csv
import hashlib
import json
import math
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ICI = pathlib.Path(__file__).resolve().parent
FICHIER = ICI / "K20-LIV_analyse.csv"
PRE = ICI / "preenregistrement.md"
SCEAU = ICI / "preenregistrement.md.sha256"

# ----------------------------------------------------------------------------------------------------------------------
# Constantes recopiées du texte scellé
# ----------------------------------------------------------------------------------------------------------------------
COLONNES = [
    "variable", "cible", "semestre", "enquete_1", "enquete_2", "mois_ancre_1", "mois_ancre_2",
    "prev_12m_1", "prev_6m_2", "prev_6m_1", "bp_1", "bp_2", "prev_12m_1_med", "prev_6m_2_med",
    "serie_realise", "jour_realise", "realise_niv", "jour_ancre_1", "ancre_niv_1", "jour_ancre_2", "ancre_niv_2",
    "y_prev_1", "y_prev_2", "y_prev6_1", "y_realise", "y_ancre_1", "y_ancre_2",
    "revision", "erreur", "surprise", "revision_med", "erreur_med",
    "n_rep_1", "var_rep_1", "n_rep_2", "var_rep_2", "complete", "principal", "episode", "grande_nouvelle",
]
assert len(COLONNES) == 40

VARS = ["CPI", "UNPR", "PRIME", "TBILL", "TPHS"]  # ordre de la section 6, étape 3
PLAGE_CIBLE = {"CPI": ("1947-12", "2026-06"), "UNPR": ("1962-06", "2026-06"), "PRIME": ("1982-06", "2026-06"),
               "TBILL": ("1993-06", "2026-06"), "TPHS": ("1970-12", "2026-06")}  # section 5
SERIE = {"UNPR": "UNRATE", "PRIME": "DPRIME", "TBILL": "DTB3", "TPHS": "HOUST"}  # section 3.3 (IPC à part)
MENSUELLES = {"CPIAUCNS", "CPIAUCSL", "UNRATE", "HOUST"}
PLAGE_PREV = {"CPI": (50.0, 500.0), "UNPR": (1.0, 20.0), "PRIME": (1.0, 25.0), "TBILL": (-1.0, 20.0),
              "TPHS": (0.2, 3.5)}  # contrôle 6
PLAGE_REAL = {"CPI": (15.0, 500.0), "UNPR": (1.0, 20.0), "PRIME": (1.0, 25.0), "TBILL": (-1.0, 20.0),
              "TPHS": (0.2, 3.5)}  # contrôle 6
EPISODES = [  # section 6, étape 8 : fenêtres en mois cibles, bornes comprises
    ("E1", "1948-11", "1950-12"), ("E2", "1953-07", "1955-07"), ("E3", "1957-08", "1959-06"),
    ("E4", "1960-04", "1962-04"), ("E5", "1969-12", "1972-01"), ("E6", "1973-11", "1976-05"),
    ("E7", "1980-01", "1984-01"), ("E8", "1990-07", "1992-05"), ("E9", "2001-03", "2003-01"),
    ("E10", "2007-12", "2010-08"), ("E11", "2020-02", "2023-12"),
]
PANDEMIE_UNPR = {"2020-06", "2020-12", "2021-06", "2021-12"}  # section 4
CHANGEMENT_BASE_IPC = {"1953-06", "1962-06", "1971-06", "1988-06"}  # section 6, diagnostic hors règle
Z90 = 1.645
TOL_FORMULE = 1e-6


def ym(s):
    """'AAAA-MM' -> nombre de mois (entier). Lève ValueError si la forme est mauvaise."""
    if not re.fullmatch(r"\d{4}-\d{2}", s or ""):
        raise ValueError(f"forme AAAA-MM attendue : {s!r}")
    a, m = int(s[:4]), int(s[5:7])
    if not 1 <= m <= 12:
        raise ValueError(f"mois impossible : {s!r}")
    return 12 * a + (m - 1)


def ym_txt(n):
    return f"{n // 12:04d}-{n % 12 + 1:02d}"


# Les 161 dates publiées de l'enquête (section 3.1) : 1er juin et 1er décembre, de 1946-06 à 2026-06, sans trou.
DATES_ENQUETE = [ym_txt(ym("1946-06") + 6 * i) for i in range(161)]
assert DATES_ENQUETE[0] == "1946-06" and DATES_ENQUETE[-1] == "2026-06"
RANG_ENQUETE = {d: i for i, d in enumerate(DATES_ENQUETE)}


def fenetre(cible):
    """Code d'épisode dont la fenêtre contient le mois cible, ou '' (les fenêtres ne se chevauchent pas)."""
    t = ym(cible)
    codes = [k for k, a, b in EPISODES if ym(a) <= t <= ym(b)]
    assert len(codes) <= 1
    return codes[0] if codes else ""


def dec(s):
    """Cellule -> float double précision (lecture exacte du texte décimal) ; vide -> nan."""
    s = s.strip()
    if s == "":
        return math.nan
    return float(s)


def present(x):
    return not (isinstance(x, float) and math.isnan(x))


def entier(s):
    """-> (valeur entière ou None, écrit comme un entier ?)."""
    s = s.strip()
    if re.fullmatch(r"-?\d+", s):
        return int(s), True
    try:
        x = float(s)
    except ValueError:
        return None, False
    if math.isfinite(x) and x == int(x):
        return int(x), False
    return None, False


def chiffres_significatifs(s):
    s = s.strip().lstrip("+-")
    if "e" in s.lower():
        s = s.lower().split("e")[0]
    s = s.replace(".", "").lstrip("0")
    return len(s)


# ----------------------------------------------------------------------------------------------------------------------
# Lecture
# ----------------------------------------------------------------------------------------------------------------------
def lire():
    with open(FICHIER, newline="", encoding="utf-8") as f:
        lignes = list(csv.reader(f))
    entete, corps = lignes[0], lignes[1:]
    return entete, corps


# ----------------------------------------------------------------------------------------------------------------------
# Formules de la section 4
# ----------------------------------------------------------------------------------------------------------------------
def g(v, x):
    if not present(x):
        return math.nan
    if v in ("CPI", "TPHS"):
        return 100.0 * math.log(x) if x > 0 else math.nan
    return x


def ln100(x):
    return 100.0 * math.log(x) if present(x) and x > 0 else math.nan


def formules(r, src):
    """Valeurs attendues des 11 colonnes calculées.
    src='entrees' : toute la chaîne depuis les valeurs lues (prévisions, bases, niveaux réalisés).
    src='fichier' : chaque formule évaluée sur ses opérandes tels qu'écrits dans le fichier (lettre du contrôle 7)."""
    v = r["variable"]
    e = {}
    e["y_realise"] = g(v, r["realise_niv"])
    e["y_ancre_1"] = g(v, r["ancre_niv_1"])
    e["y_ancre_2"] = g(v, r["ancre_niv_2"])
    ya1 = e["y_ancre_1"] if src == "entrees" else r["y_ancre_1"]
    ya2 = e["y_ancre_2"] if src == "entrees" else r["y_ancre_2"]
    if v == "CPI":
        e["y_prev_1"] = ln100(r["prev_12m_1"]) - ln100(r["bp_1"]) + ya1
        e["y_prev_2"] = ln100(r["prev_6m_2"]) - ln100(r["bp_2"]) + ya2
        e["y_prev6_1"] = ln100(r["prev_6m_1"]) - ln100(r["bp_1"]) + ya1
        yp1_med = ln100(r["prev_12m_1_med"]) - ln100(r["bp_1"]) + ya1
        yp2_med = ln100(r["prev_6m_2_med"]) - ln100(r["bp_2"]) + ya2
    else:
        e["y_prev_1"] = g(v, r["prev_12m_1"])
        e["y_prev_2"] = g(v, r["prev_6m_2"])
        e["y_prev6_1"] = g(v, r["prev_6m_1"])
        yp1_med = g(v, r["prev_12m_1_med"])
        yp2_med = g(v, r["prev_6m_2_med"])
    yp1 = e["y_prev_1"] if src == "entrees" else r["y_prev_1"]
    yp2 = e["y_prev_2"] if src == "entrees" else r["y_prev_2"]
    yp61 = e["y_prev6_1"] if src == "entrees" else r["y_prev6_1"]
    yr = e["y_realise"] if src == "entrees" else r["y_realise"]
    e["revision"] = yp2 - yp1
    e["erreur"] = yr - yp2
    e["surprise"] = ya2 - (ya1 + 0.75 * (yp61 - ya1))
    e["revision_med"] = yp2_med - yp1_med
    e["erreur_med"] = yr - yp2_med
    # Règle de vide : ligne IPC 2005-06 (paire 2004-06 / 2004-12)
    if v == "CPI" and r["cible"] == "2005-06":
        for c in ("y_prev_1", "y_prev6_1", "revision", "surprise", "revision_med"):
            e[c] = math.nan
    return e


COL_FORMULES = ["y_prev_1", "y_prev_2", "y_prev6_1", "y_realise", "y_ancre_1", "y_ancre_2",
                "revision", "erreur", "surprise", "revision_med", "erreur_med"]


def comparer(attendu, lu):
    """-> (échec ?, écart). Échec si une seule des deux valeurs est présente, ou écart > 1e-6."""
    pa, pl = present(attendu), present(lu)
    if not pa and not pl:
        return False, 0.0
    if pa != pl:
        return True, math.inf
    d = abs(attendu - lu)
    return d > TOL_FORMULE, d


# ----------------------------------------------------------------------------------------------------------------------
# Statistique (section 6)
# ----------------------------------------------------------------------------------------------------------------------
class Singuliere(Exception):
    pass


def mco(y, X):
    n, k = X.shape
    if n < 50:
        raise Singuliere(f"n = {n} < 50")
    XtX = X.T @ X
    if np.linalg.matrix_rank(X) < k:
        raise Singuliere("X'X singulière")
    XtXi = np.linalg.inv(XtX)
    beta = XtXi @ (X.T @ y)
    u = y - X @ beta
    return beta, u, XtXi


def driscoll_kraay(X, u, sem, XtXi, retards):
    """Section 6, étape 4 : H_tau sommé par semestre, du plus petit au plus grand semestre de l'échantillon utilisé,
    semestres sans ligne compris (vecteur nul) ; poids de Bartlett 1 - j/(retards+1) ; sans correction."""
    h = X * u[:, None]
    t0, t1 = int(sem.min()), int(sem.max())
    H = np.zeros((t1 - t0 + 1, X.shape[1]))
    np.add.at(H, sem - t0, h)
    Om = H.T @ H
    for j in range(1, retards + 1):
        w = 1.0 - j / (retards + 1.0)
        G = H[j:].T @ H[:-j]  # somme sur tau de H_tau H_{tau-j}'
        Om = Om + w * (G + G.T)
    return XtXi @ Om @ XtXi


def regresseurs_principaux(var, zr, L):
    D = np.column_stack([(var == v).astype(float) for v in VARS])
    return np.column_stack([D, D * L[:, None], D * zr[:, None], zr * L])  # 16 colonnes, c en dernier


def regresseurs_par_variable(var, zr, L):
    D = np.column_stack([(var == v).astype(float) for v in VARS])
    return np.column_stack([D, D * L[:, None], D * zr[:, None], D * (zr * L)[:, None]])  # 20 colonnes


def regression_c(ze, zr, L, var, sem, retards=2, X=None, indice=-1):
    if X is None:
        X = regresseurs_principaux(var, zr, L)
    beta, u, XtXi = mco(ze, X)
    V = driscoll_kraay(X, u, sem, XtXi, retards)
    return beta, u, XtXi, V, X


# ----------------------------------------------------------------------------------------------------------------------
def main():
    sortie = []

    def dire(*a):
        s = " ".join(str(x) for x in a)
        sortie.append(s)
        print(s)

    # Sceau (refait ici pour la trace ; vérifié aussi avant toute lecture)
    sceau_lu = SCEAU.read_text().split()[0]
    sceau_calc = hashlib.sha256(PRE.read_bytes()).hexdigest()
    dire(f"Sceau : calculé {sceau_calc} ; scellé {sceau_lu} ; {'IDENTIQUES' if sceau_calc == sceau_lu else 'DIFFÉRENTS'}")
    if sceau_calc != sceau_lu:
        sys.exit("Sceau différent : arrêt.")

    entete, corps = lire()
    dire(f"Fichier : {len(corps)} lignes de données, {len(entete)} colonnes d'en-tête.")

    # ------------------------------------------------------------------ contrôle 1 (niveau fichier)
    echec1 = entete != COLONNES
    lignes_mal_formees = [i for i, l in enumerate(corps) if len(l) != len(entete)]
    if lignes_mal_formees:
        echec1 = True
    dire(f"Contrôle 1 (colonnes) : {'ÉCHEC' if echec1 else 'passé'} ; lignes de longueur fausse : {len(lignes_mal_formees)}")

    idx = {c: i for i, c in enumerate(entete)}
    TEXTE = {"variable", "cible", "enquete_1", "enquete_2", "mois_ancre_1", "mois_ancre_2", "serie_realise",
             "jour_realise", "jour_ancre_1", "jour_ancre_2", "episode"}
    ENTIERS = {"semestre", "n_rep_1", "n_rep_2", "complete", "principal", "grande_nouvelle"}
    DECIMAUX = [c for c in COLONNES if c not in TEXTE and c not in ENTIERS]

    R = []  # lignes analysées
    format_anomalies = []
    peu_chiffres = Counter()
    for i, l in enumerate(corps):
        brut = {c: l[idx[c]] if c in idx and idx[c] < len(l) else "" for c in COLONNES}
        r = {"_i": i, "_brut": brut}
        for c in TEXTE:
            r[c] = brut[c].strip()
        for c in DECIMAUX:
            try:
                r[c] = dec(brut[c])
            except ValueError:
                r[c] = math.nan
                format_anomalies.append((i, c, brut[c]))
            if brut[c].strip() != "" and chiffres_significatifs(brut[c]) < 10:
                peu_chiffres[c] += 1
        for c in ENTIERS:
            if brut[c].strip() == "":
                r[c] = None
                r["_fmt_" + c] = True
            else:
                val, fmt = entier(brut[c])
                r[c] = val
                r["_fmt_" + c] = fmt
                if val is None:
                    format_anomalies.append((i, c, brut[c]))
        R.append(r)

    def nom(r):
        return f"{r['variable']} {r['cible']}"

    # ------------------------------------------------------------------ indicateurs recalculés (section 4)
    for r in R:
        r["complete_calc"] = int(all(present(r[c]) for c in ("revision", "erreur", "surprise")))
        n1, n2 = r["n_rep_1"], r["n_rep_2"]
        r["principal_calc"] = int(
            r["complete_calc"] == 1
            and n1 is not None and n1 >= 2 and n2 is not None and n2 >= 2
            and present(r["var_rep_1"]) and present(r["var_rep_2"])
            and not (r["variable"] == "UNPR" and r["cible"] in PANDEMIE_UNPR)
        )
    PORTEE = [r for r in R if r["principal"] == 1 or r["principal_calc"] == 1]  # section 5 : règle de portée
    portee_ids = {r["_i"] for r in PORTEE}
    AUTRES = [r for r in R if r["_i"] not in portee_ids]
    n_fichier = sum(1 for r in R if r["principal"] == 1)
    n_calc = sum(1 for r in R if r["principal_calc"] == 1)
    dire(f"Lignes principales : principal=1 dans le fichier {n_fichier} ; définition recalculée {n_calc} ; "
         f"réunion (portée des contrôles) {len(PORTEE)} ; autres lignes {len(AUTRES)}")

    # Q_v et L (section 6, étape 2) : sur les lignes principales, à partir de la colonne surprise du fichier
    Q = {}
    for v in VARS:
        s = np.array([abs(r["surprise"]) for r in PORTEE if r["variable"] == v], dtype=float)
        Q[v] = float(np.quantile(s, 2.0 / 3.0)) if s.size else math.nan
    for r in R:
        r["L_calc"] = (1 if abs(r["surprise"]) > Q.get(r["variable"], math.nan) else 0) if present(r["surprise"]) \
            and r["variable"] in Q else None

    # ------------------------------------------------------------------ contrôles 2 à 11, ligne par ligne
    cles = Counter((r["variable"], r["cible"]) for r in R)
    echecs = defaultdict(list)  # (n° contrôle) -> [(ligne, message)] pour les lignes de la portée
    hors = defaultdict(list)  # anomalies des contrôles 3 à 8 hors des lignes principales
    ecart_max = {"fichier": defaultdict(float), "entrees": defaultdict(float)}
    jours_quotidiens = []

    for r in R:
        dans = r["_i"] in portee_ids
        v = r["variable"]
        f = defaultdict(list)  # contrôle -> messages (sur cellules présentes pour les autres lignes)

        # 2. clés
        if v not in VARS:
            f[2].append(f"variable inconnue {v!r}")
        if cles[(v, r["cible"])] != 1:
            f[2].append("couple (variable, cible) non unique")
        try:
            tc = ym(r["cible"])
            if r["cible"][5:] not in ("06", "12"):
                f[2].append("mois cible ni 06 ni 12")
            if v in PLAGE_CIBLE and not (ym(PLAGE_CIBLE[v][0]) <= tc <= ym(PLAGE_CIBLE[v][1])):
                f[2].append("cible hors de la plage de la variable")
        except ValueError as ex:
            f[2].append(str(ex))
            tc = None

        # 3. dates d'enquête
        try:
            e1, e2 = r["enquete_1"], r["enquete_2"]
            if e1 not in RANG_ENQUETE or e2 not in RANG_ENQUETE:
                f[3].append("enquête hors des 161 dates publiées")
            else:
                if RANG_ENQUETE[e2] != RANG_ENQUETE[e1] + 1:
                    f[3].append("enquete_2 n'est pas la date qui suit enquete_1")
            if tc is not None:
                if ym(e2) + 6 != tc:
                    f[3].append("cible n'est pas le juin/décembre qui suit enquete_2")
                if ym(e1) != tc - 12:
                    f[3].append("enquete_1 n'a pas le mois de la cible l'année précédente")
                sem_att = 2 * (tc // 12) + (0 if r["cible"][5:] == "06" else 1)
                if r["semestre"] != sem_att or not r["_fmt_semestre"]:
                    f[3].append(f"semestre {r['_brut']['semestre']!r} au lieu de {sem_att}")
            for k, e in ((1, e1), (2, e2)):
                att = ym_txt(ym(e) - 2) if e[5:] in ("06", "12") else None
                if att is None or r[f"mois_ancre_{k}"] != att:
                    f[3].append(f"mois_ancre_{k} {r[f'mois_ancre_{k}']!r} au lieu de {att!r}")
        except ValueError as ex:
            f[3].append(str(ex))

        # 4. présence
        req = ["prev_12m_1", "prev_6m_2", "prev_6m_1", "serie_realise", "jour_realise", "jour_ancre_1",
               "jour_ancre_2", "realise_niv", "ancre_niv_1", "ancre_niv_2", "y_prev_1", "y_prev_2", "y_prev6_1",
               "y_realise", "y_ancre_1", "y_ancre_2", "revision", "erreur", "surprise", "n_rep_1", "var_rep_1",
               "n_rep_2", "var_rep_2", "grande_nouvelle"]
        absentes = [c for c in req if r["_brut"][c].strip() == ""]
        bp_pres = [r["_brut"][c].strip() != "" for c in ("bp_1", "bp_2")]
        if dans:
            if absentes:
                f[4].append("absentes : " + ", ".join(absentes))
            if v == "CPI" and not all(bp_pres):
                f[4].append("bp_1/bp_2 absente sur une ligne CPI")
        if v != "CPI" and any(bp_pres):
            f[4].append("bp_1/bp_2 présente sur une ligne non CPI")
        r["_absentes"] = absentes

        # 5. séries et jours
        if r["serie_realise"] != "":
            if v == "CPI":
                try:
                    s_att = "CPIAUCNS" if ym(r["enquete_2"]) <= ym("2004-06") else "CPIAUCSL"
                except ValueError:
                    s_att = None
            else:
                s_att = SERIE.get(v)
            if r["serie_realise"] != s_att:
                f[5].append(f"serie_realise {r['serie_realise']!r} au lieu de {s_att!r}")
        for jc, mc in (("jour_realise", "cible"), ("jour_ancre_1", "mois_ancre_1"), ("jour_ancre_2", "mois_ancre_2")):
            j = r[jc]
            if j == "":
                continue
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", j):
                f[5].append(f"{jc} mal formé {j!r}")
                continue
            if j[:7] != r[mc]:
                f[5].append(f"{jc} {j} n'est pas dans {mc} {r[mc]}")
            if r["serie_realise"] in MENSUELLES and j[8:] != "01":
                f[5].append(f"{jc} {j} : jour différent de 01 pour une série mensuelle")
            if r["serie_realise"] in ("DPRIME", "DTB3"):
                jours_quotidiens.append((nom(r), jc, j))

        # 6. plages
        if v in PLAGE_PREV:
            lo, hi = PLAGE_PREV[v]
            cols6 = ["prev_12m_1", "prev_6m_2", "prev_6m_1"] + (["bp_1", "bp_2"] if v == "CPI" else [])
            for c in cols6:
                x = r[c]
                if present(x) and not (lo <= x <= hi):
                    f[6].append(f"{c} = {x} hors [{lo} ; {hi}]")
            for c in ("prev_12m_1_med", "prev_6m_2_med"):  # hors lettre du contrôle 6 : rapporté à part
                x = r[c]
                if present(x) and not (lo <= x <= hi):
                    f["6m"].append(f"{c} = {x} hors [{lo} ; {hi}] (médiane)")
            lo, hi = PLAGE_REAL[v]
            for c in ("realise_niv", "ancre_niv_1", "ancre_niv_2"):
                x = r[c]
                if present(x) and not (lo <= x <= hi):
                    f[6].append(f"{c} = {x} hors [{lo} ; {hi}]")

        # 7. formules (lettre : opérandes du fichier ; et chaîne complète depuis les entrées, rapportée)
        for src in ("fichier", "entrees"):
            att = formules(r, src)
            for c in COL_FORMULES:
                lu = r[c]
                if not dans and not present(lu):
                    continue  # hors lignes principales : cellules présentes seulement
                ech, d = comparer(att[c], lu)
                if present(att[c]) and present(lu):
                    ecart_max[src][c] = max(ecart_max[src][c], d)
                if ech:
                    f[7 if src == "fichier" else "7e"].append(
                        f"{c} : lu {lu!r}, formule {att[c]!r}" + ("" if math.isinf(d) else f" (écart {d:.3g})"))

        # 8. bruit
        for c in ("n_rep_1", "n_rep_2"):
            if r["_brut"][c].strip() == "":
                continue
            if r[c] is None or not r["_fmt_" + c] or r[c] < 2:
                f[8].append(f"{c} = {r['_brut'][c]!r} n'est pas un entier >= 2")
        for c in ("var_rep_1", "var_rep_2"):
            if present(r[c]) and not r[c] >= 0:
                f[8].append(f"{c} = {r[c]} < 0")

        # 9. indicateurs (portée seulement)
        if dans:
            if r["complete"] != 1 or not r["_fmt_complete"]:
                f[9].append(f"complete = {r['_brut']['complete']!r}")
            if r["principal"] != r["principal_calc"] or not r["_fmt_principal"]:
                f[9].append(f"principal = {r['_brut']['principal']!r}, définition = {r['principal_calc']}")

        # 10. épisodes
        try:
            ep_att = fenetre(r["cible"])
            if r["episode"] != ep_att:
                f[10].append(f"episode {r['episode']!r} au lieu de {ep_att!r}")
        except ValueError as ex:
            f[10].append(str(ex))

        # 11. grande nouvelle
        gn = r["grande_nouvelle"]
        if r["_brut"]["grande_nouvelle"].strip() != "" or dans:
            if gn not in (0, 1) or not r["_fmt_grande_nouvelle"]:
                f[11].append(f"grande_nouvelle = {r['_brut']['grande_nouvelle']!r}")
            elif r["L_calc"] is None or gn != r["L_calc"]:
                f[11].append(f"grande_nouvelle = {gn}, |surprise| > Q_v donne {r['L_calc']}")

        r["_echecs"] = f
        for k, msgs in f.items():
            for m in msgs:
                if dans and k in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11):
                    echecs[k].append((nom(r), m))
                elif not dans and k in (3, 4, 5, 6, 7, 8):
                    hors[k].append((nom(r), m))
                else:
                    hors[k].append((nom(r), m))

    viole = {1: echec1}
    for k in range(2, 12):
        viole[k] = len(echecs[k]) > 0
    n_violations_schema = int(sum(viole.values()))
    dire("")
    dire("Contrôles de schéma sur les lignes principales :")
    for k in range(1, 12):
        dire(f"  contrôle {k:2d} : {'VIOLÉ' if viole[k] else 'passé'}"
             + (f" ({len(echecs[k])} échec(s), ex. {echecs[k][:3]})" if k > 1 and echecs[k] else ""))
    dire(f"n_violations_schema = {n_violations_schema}")
    dire(f"Contrôle 7, chaîne complète depuis les entrées (rapporté) : {len(echecs.get('7e', []))} échec(s) dans la portée")
    for src in ("fichier", "entrees"):
        dire(f"  écart maximal formule/fichier ({src}) : "
             + ", ".join(f"{c} {ecart_max[src][c]:.2e}" for c in COL_FORMULES))
    dire(f"Médianes hors des plages du contrôle 6 (hors lettre) : {len(echecs.get('6m', [])) + len(hors.get('6m', []))}")
    dire("")
    dire("Anomalies hors des lignes principales (contrôles 3 à 8, cellules présentes) :")
    nb_hors = 0
    for k in sorted(hors, key=str):
        for nm, m in hors[k]:
            nb_hors += 1
            dire(f"  [{k}] {nm} : {m}")
    dire(f"  total : {nb_hors}")
    dire("Cellules vides des lignes hors principal (comparées aux règles de vide de la section 4) :")
    for r in AUTRES:
        vides = [c for c in COLONNES if r["_brut"][c].strip() == ""]
        dire(f"  {nom(r)} (complete={r['_brut']['complete']}, principal={r['_brut']['principal']}) : vides = {vides}")

    # Points de forme hors des 11 contrôles
    dire("")
    dire(f"Forme : {len(R)} lignes (555 attendues) ; anomalies de lecture numérique : {format_anomalies}")
    ordre = [(VARS.index(r["variable"]) if r["variable"] in VARS else 99, r["cible"]) for r in R]
    dire(f"Tri variable puis cible : {'conforme' if ordre == sorted(ordre) else 'NON conforme'}")
    for v in VARS:
        rv = [r for r in R if r["variable"] == v]
        dire(f"  {v}: lignes {len(rv)}, {rv[0]['cible'] if rv else '-'} -> {rv[-1]['cible'] if rv else '-'}, "
             f"complete=1 {sum(r['complete'] == 1 for r in rv)}, principal=1 {sum(r['principal'] == 1 for r in rv)}")
    dire(f"Cellules décimales écrites avec moins de 10 chiffres significatifs (par colonne) : {dict(peu_chiffres)}")
    jq = Counter(int(j[8:]) for _, _, j in jours_quotidiens)
    dire(f"Jours lus pour DPRIME/DTB3 (sur toutes les lignes) : minimum {min(jq) if jq else '-'}, "
         f"répartition {dict(sorted(jq.items()))}")

    # ------------------------------------------------------------------ statistique
    P = sorted(PORTEE, key=lambda r: r["_i"])
    n_principal = len(P)
    var_all = np.array([r["variable"] for r in R])

    # Étape 1 : réduction par variable sur les lignes principales
    cst = {}
    for v in VARS:
        rv = np.array([r["revision"] for r in P if r["variable"] == v], dtype=float)
        ev = np.array([r["erreur"] for r in P if r["variable"] == v], dtype=float)
        rmv = np.array([r["revision_med"] for r in P if r["variable"] == v], dtype=float)
        emv = np.array([r["erreur_med"] for r in P if r["variable"] == v], dtype=float)
        cst[v] = dict(n=rv.size, mr=rv.mean(), sr=rv.std(ddof=1), me=ev.mean(), se=ev.std(ddof=1),
                      mrm=rmv.mean(), srm=rmv.std(ddof=1), mem=emv.mean(), sem=emv.std(ddof=1),
                      nan_med=int(np.isnan(rmv).sum() + np.isnan(emv).sum()))
    for r in R:
        c = cst[r["variable"]]
        r["zr"] = (r["revision"] - c["mr"]) / c["sr"]
        r["ze"] = (r["erreur"] - c["me"]) / c["se"]
        r["zrm"] = (r["revision_med"] - c["mrm"]) / c["srm"]
        r["zem"] = (r["erreur_med"] - c["mem"]) / c["sem"]
    k_v = {v: cst[v]["sr"] / cst[v]["se"] for v in VARS}
    k_moyen = float(np.mean([k_v[v] for v in VARS]))

    def tableau(lignes, Lname="L_calc", zr="zr", ze="ze"):
        var = np.array([r["variable"] for r in lignes])
        sem = np.array([r["semestre"] for r in lignes], dtype=int)
        Z_r = np.array([r[zr] for r in lignes], dtype=float)
        Z_e = np.array([r[ze] for r in lignes], dtype=float)
        L = np.array([r[Lname] for r in lignes], dtype=float)
        return var, sem, Z_r, Z_e, L

    var, sem, zr, ze, L = tableau(P)
    assert not np.isnan(zr).any() and not np.isnan(ze).any() and not np.isnan(L).any()

    # Étape 3 : régression principale (16 paramètres)
    beta, u, XtXi, V2, X = regression_c(ze, zr, L, var, sem, 2)
    c_hat = float(beta[15])
    b_v = {v: float(beta[10 + j]) for j, v in enumerate(VARS)}
    b_moyen = float(np.mean([b_v[v] for v in VARS]))
    pente_moyenne_grandes = b_moyen + c_hat
    # Étape 4-5
    et_c_dk2 = float(math.sqrt(V2[15, 15]))
    t_c = c_hat / et_c_dk2
    borne_basse_ic90 = c_hat - Z90 * et_c_dk2
    borne_haute_ic90 = c_hat + Z90 * et_c_dk2
    # S2
    et_c_dk4 = float(math.sqrt(driscoll_kraay(X, u, sem, XtXi, 4)[15, 15]))
    et_c_dk0 = float(math.sqrt(driscoll_kraay(X, u, sem, XtXi, 0)[15, 15]))
    # Étape 10
    n = len(P)
    sigma2 = float(u @ u) / (n - 16)
    et_c_iid = float(math.sqrt(sigma2 * XtXi[15, 15]))
    n_effectif = n * (et_c_iid / et_c_dk2) ** 2
    n_grands = int(L.sum())
    n_dates = int(len(set(sem.tolist())))
    n_dates_grands = int(len(set(sem[L == 1].tolist())))

    # Étape 6 : contrôle positif (6 paramètres)
    D = np.column_stack([(var == v).astype(float) for v in VARS])
    X6 = np.column_stack([D, zr])
    beta6, u6, XtXi6 = mco(ze, X6)
    V6 = driscoll_kraay(X6, u6, sem, XtXi6, 2)
    b_regroupe = float(beta6[5])
    et_b_regroupe_dk2 = float(math.sqrt(V6[5, 5]))
    borne_basse_b_ic90 = b_regroupe - Z90 * et_b_regroupe_dk2
    controle_positif_ok = int(borne_basse_b_ic90 > 0 or borne_haute_ic90 < 0)

    # Étape 7 : biais mécanique (moyennes regroupées, telles qu'écrites)
    m = {}
    for v in VARS:
        for l in (0, 1):
            sel = (var == v) & (L == l)
            m[(v, l)] = float(zr[sel].mean())
    dev0 = [(zr[i] - m[(var[i], 0)]) ** 2 for i in range(n) if L[i] == 0]
    dev1 = [(zr[i] - m[(var[i], 1)]) ** 2 for i in range(n) if L[i] == 1]
    a = float(np.mean(dev0))
    A = float(np.mean(dev1))
    rapport_variance_revision = A / a
    nu_v = {}
    for v in VARS:
        s2 = cst[v]["sr"] ** 2
        nus = [(r["var_rep_1"] / r["n_rep_1"] + r["var_rep_2"] / r["n_rep_2"]) / s2 for r in P if r["variable"] == v]
        nu_v[v] = float(np.median(nus))
    nu_mesure = float(np.mean([nu_v[v] for v in VARS]))
    facteur = (2 * b_moyen + k_moyen) * (1.0 / a - 1.0 / A)
    biais_mecanique_mesure = facteur * nu_mesure
    biais_mecanique_nu20 = facteur * 0.10
    seuil_survie_bas = max(0.10, biais_mecanique_mesure)
    borne_basse_moins_seuil = borne_basse_ic90 - seuil_survie_bas

    # Étape 8 : garde des épisodes
    c_sans, t_sans, et_sans, n_sans = {}, {}, {}, {}
    for k, (code, _, _) in enumerate(EPISODES, start=1):
        sous = [r for r in P if fenetre(r["cible"]) != code]
        vk, sk, zrk, zek, Lk = tableau(sous)
        bk, uk, XtXik, Vk, _ = regression_c(zek, zrk, Lk, vk, sk, 2)
        c_sans[k] = float(bk[15])
        et_sans[k] = float(math.sqrt(Vk[15, 15]))
        t_sans[k] = c_sans[k] / et_sans[k]
        n_sans[k] = len(sous)
    t_min_sans_episode = min(t_sans.values())
    episode_t_min = min(k for k in t_sans if t_sans[k] == t_min_sans_episode)
    c_min_sans_episode = min(c_sans.values())

    # Étape 9
    marge_indecision = min(seuil_survie_bas - borne_basse_ic90, borne_haute_ic90 - 0.40)
    conflit_robustesse = int(borne_basse_ic90 > seuil_survie_bas and borne_haute_ic90 >= 0.40
                             and t_min_sans_episode < 1 and c_min_sans_episode > 0)

    # Secondaires
    # S1 : par variable (20 paramètres)
    X20 = regresseurs_par_variable(var, zr, L)
    b20, u20, XtXi20 = mco(ze, X20)
    V20 = driscoll_kraay(X20, u20, sem, XtXi20, 2)
    c_par_v = {v: float(b20[15 + j]) for j, v in enumerate(VARS)}
    et_par_v = {v: float(math.sqrt(V20[15 + j, 15 + j])) for j, v in enumerate(VARS)}

    def secondaire(lignes, **kw):
        vs, ss, zrs, zes, Ls = tableau(lignes, **kw)
        assert not (np.isnan(zrs).any() or np.isnan(zes).any() or np.isnan(Ls).any()), "valeur manquante"
        bs, us, XtXis, Vs, _ = regression_c(zes, zrs, Ls, vs, ss, 2)
        return float(bs[15]), float(math.sqrt(Vs[15, 15])), len(lignes)

    # S3 : avec la pandémie
    pand = [r for r in R if r["variable"] == "UNPR" and r["cible"] in PANDEMIE_UNPR and r["complete_calc"] == 1]
    c_avec_pandemie, et_c_avec_pandemie_dk2, n_s3 = secondaire(sorted(P + pand, key=lambda r: r["_i"]))
    # S4, S5
    c_depuis_1985, et_c_depuis_1985_dk2, n_s4 = secondaire([r for r in P if ym(r["cible"]) >= ym("1985-06")])
    c_avant_2020, et_c_avant_2020_dk2, n_s5 = secondaire([r for r in P if ym(r["cible"]) <= ym("2019-12")])
    # S6 : médianes
    c_mediane, et_c_mediane_dk2, n_s6 = secondaire(P, zr="zrm", ze="zem")
    # S7 : coupure sur la révision
    for r in R:
        r["Lp"] = (1 if abs(r["zr"]) > 1 else 0) if present(r["zr"]) else None
    c_coupure_revision, et_c_coupure_revision_dk2, n_s7 = secondaire(P, Lname="Lp")

    # Diagnostic hors règle : stabilité de la base IPC
    nb_base = 0
    nb_base_eval = 0
    for r in P:
        if r["variable"] != "CPI" or r["enquete_2"] in CHANGEMENT_BASE_IPC:
            continue
        nb_base_eval += 1
        dlt = abs(math.log(r["ancre_niv_2"] / r["bp_2"]) - math.log(r["ancre_niv_1"] / r["bp_1"]))
        if dlt > 0.005:
            nb_base += 1

    res = {
        "n_violations_schema": n_violations_schema,
        "n_principal": int(n_principal),
        "c": c_hat,
        "et_c_dk2": et_c_dk2,
        "t_c": t_c,
        "borne_basse_ic90": borne_basse_ic90,
        "borne_haute_ic90": borne_haute_ic90,
        "rapport_variance_revision": rapport_variance_revision,
        "b_moyen": b_moyen,
        "k_moyen": k_moyen,
        "pente_moyenne_grandes": pente_moyenne_grandes,
        "b_regroupe": b_regroupe,
        "et_b_regroupe_dk2": et_b_regroupe_dk2,
        "borne_basse_b_ic90": borne_basse_b_ic90,
        "controle_positif_ok": controle_positif_ok,
        "nu_mesure": nu_mesure,
        "biais_mecanique_mesure": biais_mecanique_mesure,
        "biais_mecanique_nu20": biais_mecanique_nu20,
        "seuil_survie_bas": seuil_survie_bas,
        "borne_basse_moins_seuil": borne_basse_moins_seuil,
        "marge_indecision": marge_indecision,
        "t_min_sans_episode": t_min_sans_episode,
        "c_min_sans_episode": c_min_sans_episode,
        "episode_t_min": int(episode_t_min),
        "conflit_robustesse": conflit_robustesse,
        "n_grands": n_grands,
        "n_dates": n_dates,
        "n_dates_grands": n_dates_grands,
        "et_c_iid": et_c_iid,
        "n_effectif": n_effectif,
    }
    for k in range(1, 12):
        res[f"c_sans_E{k}"] = c_sans[k]
    res.update({
        "et_c_dk4": et_c_dk4,
        "et_c_dk0": et_c_dk0,
        "c_avec_pandemie": c_avec_pandemie,
        "et_c_avec_pandemie_dk2": et_c_avec_pandemie_dk2,
        "c_depuis_1985": c_depuis_1985,
        "et_c_depuis_1985_dk2": et_c_depuis_1985_dk2,
        "c_avant_2020": c_avant_2020,
        "et_c_avant_2020_dk2": et_c_avant_2020_dk2,
        "c_mediane": c_mediane,
        "et_c_mediane_dk2": et_c_mediane_dk2,
        "c_coupure_revision": c_coupure_revision,
        "et_c_coupure_revision_dk2": et_c_coupure_revision_dk2,
    })
    for v in VARS:
        res[f"c_{v}"] = c_par_v[v]
    for v in VARS:
        res[f"et_c_{v}_dk2"] = et_par_v[v]

    # Contrôle de complétude par rapport au bloc json de la section 12
    regle = json.loads(re.findall(r"```json\s*(\{.*?\})\s*```", PRE.read_text(encoding="utf-8"), flags=re.S)[-1])
    manquants = [c for c in regle["champs_verification"] if c not in res]
    en_trop = [c for c in res if c not in regle["champs_verification"]]
    assert not manquants and not en_trop, (manquants, en_trop)
    ordonne = {c: res[c] for c in regle["champs_verification"]}
    for c, x in ordonne.items():
        assert isinstance(x, (int, float)) and x == x and math.isfinite(x), c
    (ICI / "verification.json").write_text(json.dumps(ordonne, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ impression du détail
    dire("")
    dire("Échantillon principal : n =", n_principal, "; par variable :",
         {v: int((var == v).sum()) for v in VARS}, "; semestres :", sem.min(), "->", sem.max(),
         f"({n_dates} distincts sur {sem.max() - sem.min() + 1})")
    ep_compte = Counter(fenetre(r["cible"]) or "hors" for r in P)
    dire("Lignes principales par épisode :", {k: ep_compte.get(k, 0) for k, _, _ in EPISODES}, "hors", ep_compte["hors"])
    dire("Q_v :", {v: Q[v] for v in VARS})
    dire("n grands par variable :", {v: int(L[var == v].sum()) for v in VARS})
    dire("Réduction :", {v: {kk: cst[v][kk] for kk in ("n", "mr", "sr", "me", "se")} for v in VARS})
    dire("k_v :", k_v)
    dire("Coefficients (16) :", dict(zip([f"a_{v}" for v in VARS] + [f"d_{v}" for v in VARS]
                                          + [f"b_{v}" for v in VARS] + ["c"], beta.tolist())))
    dire("a =", a, "; A =", A, "; m_v,l =", m)
    dire("nu_v :", nu_v)
    dire("Épisodes : ", {f"E{k}": (n_sans[k], c_sans[k], et_sans[k], t_sans[k]) for k in range(1, 12)})
    dire("Secondaires n :", dict(S3=n_s3, S4=n_s4, S5=n_s5, S6=n_s6, S7=n_s7),
         "; L' (S7) = 1 :", int(sum(r["Lp"] for r in P)))
    dire(f"Diagnostic base IPC (hors règle) : {nb_base} lignes principales sur {nb_base_eval} évaluées "
         f"avec |ln(ancre_niv_2/bp_2) - ln(ancre_niv_1/bp_1)| > 0,005")
    dire(f"Médianes manquantes sur les lignes principales : {sum(cst[v]['nan_med'] for v in VARS)}")
    dire("")
    for c, x in ordonne.items():
        dire(f"  {c:28s} {x!r}")
    return ordonne


if __name__ == "__main__":
    main()
