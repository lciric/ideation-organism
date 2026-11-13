"""K20-ZE -- verification independante.

Ecrit par le verificateur, a partir de la seule preinscription scellee (preenregistrement.md) et du seul
fichier d'analyse (K20-ZE_analyse.csv). Aucun autre fichier du dossier n'est lu.

Sortie : verification.json (les champs de "champs_verification", en nombres). Le detail des controles de
schema et des calculs intermediaires est imprime sur la sortie standard.
Usage : python3 verification.py
Calculs en double precision, sans arrondi intermediaire (section 6).
"""
import json
import math
import pathlib
import re

import numpy as np
import pandas as pd

ICI = pathlib.Path(__file__).resolve().parent
FICHIER = ICI / "K20-ZE_analyse.csv"

COLONNES = ["variable", "annee_cible", "tour", "t_tour", "rang", "horizon", "tour_prec", "horizon_prec",
            "n_rep", "n_rep_prec", "prev", "prev_prec", "prev_med", "prev_prec_med", "ref_periode", "ref",
            "ref_periode_prec", "ref_prec", "prev_glissante_t4", "realise", "revision", "erreur", "surprise",
            "surprise_consensus", "revision_med", "erreur_med", "complete", "principal", "episode",
            "grande_nouvelle"]
VARIABLES = ["HICP", "RGDP", "UNEM"]
ANNEES = list(range(2000, 2026))
T_PREMIER = 4 * 1999 + 1 - 1  # 1999T1 = 7996
VALEUR_CRITIQUE = 1.708
FENETRES = {1: (8032, 8037), 2: (8046, 8052), 3: (8079, 8095)}
MOIS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PLAGES_PREV = {"HICP": (-3, 12), "RGDP": (-10, 10), "UNEM": (3, 15)}
PLAGES_REF = {"HICP": (-3, 12), "RGDP": (-20, 20), "UNEM": (3, 15)}


# ----------------------------------------------------------------------------------------------------------
# Lecture
# ----------------------------------------------------------------------------------------------------------
def lire():
    brut = pd.read_csv(FICHIER, dtype=str, keep_default_na=False)
    return brut


def est_entier(s):
    return re.fullmatch(r"-?\d+", s) is not None


def flottant(s):
    """Valeur double d'une cellule ; NaN si vide ; None si non numerique."""
    if s == "":
        return float("nan")
    try:
        x = float(s)
    except ValueError:
        return None
    if not math.isfinite(x):
        return None
    return x


def tour_texte(t):
    return f"{t // 4}Q{t % 4 + 1}"


def mois_texte(index_absolu):
    return f"{index_absolu // 12}{MOIS[index_absolu % 12]}"


def periode_reference(v, t):
    """Periode de la valeur de reference du tour t selon la section 3.1."""
    an, q = t // 4, t % 4 + 1
    if v == "HICP":
        if (an, q) == (2024, 2):
            return "2024Feb"
        # dernier mois du trimestre precedant le tour
        return mois_texte(an * 12 + 3 * (q - 1) - 1)
    if v == "RGDP":
        return tour_texte(t - 2)
    if v == "UNEM":
        exceptions = {(2000, 1): "1999Dec", (2023, 1): "2022Oct", (2023, 4): "2023Jul", (2024, 1): "2023Oct",
                      (2024, 2): "2024Jan", (2024, 4): "2024Jul"}
        if (an, q) in exceptions:
            return exceptions[(an, q)]
        # deuxieme mois avant le debut du trimestre du tour
        return mois_texte(an * 12 + 3 * (q - 1) - 2)
    raise ValueError(v)


def nb_decimales(s):
    if "." not in s:
        return 0
    return len(s.split(".")[1].rstrip("0"))


# ----------------------------------------------------------------------------------------------------------
# Controles de schema (section 4.4)
# ----------------------------------------------------------------------------------------------------------
def controles_schema(brut):
    n = len(brut)
    echecs = {k: set() for k in range(1, 13)}  # controle -> indices de lignes en echec
    echec_fichier = {1: [], 2: []}
    observations = []  # constats hors controles (ne comptent pas)

    # --- 1. Colonnes
    if list(brut.columns) != COLONNES:
        echec_fichier[1].append(f"colonnes lues : {list(brut.columns)}")

    # Valeurs numeriques (None si non numerique)
    num_cols = ["prev", "prev_prec", "prev_med", "prev_prec_med", "ref", "ref_prec", "prev_glissante_t4",
                "realise", "revision", "erreur", "surprise", "surprise_consensus", "revision_med", "erreur_med"]
    val = {c: [flottant(s) for s in brut[c]] for c in num_cols}
    ent_cols = ["annee_cible", "t_tour", "rang", "horizon", "horizon_prec", "n_rep", "n_rep_prec", "complete",
                "principal"]
    ent = {c: [int(s) if est_entier(s) else None for s in brut[c]] for c in ent_cols}

    # --- 2. Grille : 624 lignes ; chaque (variable, annee_cible, t_tour) une fois ; tri
    grille = [(v, y, 4 * (y - 1) + j - 1) for v in VARIABLES for y in ANNEES for j in range(1, 9)]
    cles = [(brut.variable[i], ent["annee_cible"][i], ent["t_tour"][i]) for i in range(n)]
    if n != 624:
        echec_fichier[2].append(f"{n} lignes au lieu de 624")
    if cles != grille:  # meme ensemble, chaque cle une fois, et meme ordre (tri conforme)
        if sorted(map(str, cles)) != sorted(map(str, grille)):
            echec_fichier[2].append("ensemble des cles different de la grille")
        elif len(set(cles)) != len(cles):
            echec_fichier[2].append("cles en double")
        else:
            echec_fichier[2].append("tri non conforme")

    # Index des lignes par cle
    pos = {cles[i]: i for i in range(n)}

    for i in range(n):
        v = brut.variable[i]
        y = ent["annee_cible"][i]
        t = ent["t_tour"][i]

        # --- 3. Identifiants
        ok3 = True
        m = re.fullmatch(r"(\d{4})Q([1-4])", brut.tour[i])
        if m is None or None in (y, t, ent["rang"][i], ent["horizon"][i], ent["horizon_prec"][i]):
            ok3 = False
        else:
            an_t, q_t = int(m.group(1)), int(m.group(2))
            rang = ent["rang"][i]
            if t != 4 * an_t + q_t - 1:
                ok3 = False
            if rang != t - 4 * (y - 1) + 1 or not (1 <= rang <= 8):
                ok3 = False
            h = ent["horizon"][i]
            if h != y - an_t or h != (1 if rang <= 4 else 0):
                ok3 = False
            if brut.tour_prec[i] != tour_texte(t - 1):
                ok3 = False
            mp = re.fullmatch(r"(\d{4})Q([1-4])", brut.tour_prec[i])
            hp = ent["horizon_prec"][i]
            if mp is None or hp != y - int(mp.group(1)) or hp not in (0, 1, 2):
                ok3 = False
        if not ok3:
            echecs[3].add(i)

        # --- 4. Effectifs et presence
        ok4 = True
        nr, nrp = ent["n_rep"][i], ent["n_rep_prec"][i]
        if nr is None or nrp is None or nr < 0 or nrp < 0:
            ok4 = False
        else:
            p_present = not math.isnan(val["prev"][i]) if val["prev"][i] is not None else True
            pp_present = not math.isnan(val["prev_prec"][i]) if val["prev_prec"][i] is not None else True
            if p_present != (nr >= 20):
                ok4 = False
            if pp_present != (nrp >= 20):
                ok4 = False
            if brut.principal[i] == "1":
                if nr < 20 or nrp < 20:
                    ok4 = False
                for c in ["prev", "prev_prec", "prev_med", "prev_prec_med"]:
                    if brut[c][i] == "":
                        ok4 = False
        if not ok4:
            echecs[4].add(i)

        # --- 5. Reference
        ok5 = True
        if t is not None and t >= T_PREMIER:
            if brut.ref[i] == "" or brut.ref_periode[i] == "" or val["ref"][i] is None:
                ok5 = False
            elif brut.ref_periode[i] != periode_reference(v, t):
                ok5 = False
            tp = t - 1
            if tp >= T_PREMIER:
                if brut.ref_prec[i] == "" or brut.ref_periode_prec[i] == "" or val["ref_prec"][i] is None:
                    ok5 = False
                elif brut.ref_periode_prec[i] != periode_reference(v, tp):
                    ok5 = False
            else:  # tour precedent avant 1999T1 : vides (section 3.3)
                if brut.ref_prec[i] != "" or brut.ref_periode_prec[i] != "":
                    ok5 = False
        if not ok5:
            echecs[5].add(i)

        # --- 6. Plages
        ok6 = True
        lo, hi = PLAGES_PREV[v] if v in PLAGES_PREV else (None, None)
        for c in ["prev", "prev_prec", "prev_med", "prev_prec_med", "realise"]:
            x = val[c][i]
            if x is None:
                ok6 = False
            elif not math.isnan(x) and lo is not None and not (lo <= x <= hi):
                ok6 = False
        lo, hi = PLAGES_REF[v] if v in PLAGES_REF else (None, None)
        for c in ["ref", "ref_prec"]:
            x = val[c][i]
            if x is None:
                ok6 = False
            elif not math.isnan(x) and lo is not None and not (lo <= x <= hi):
                ok6 = False
        if not ok6:
            echecs[6].add(i)

        # --- 7. Formules
        ok7 = True
        for res, a, b in [("revision", "prev", "prev_prec"), ("erreur", "realise", "prev"),
                          ("surprise", "ref", "ref_prec"), ("surprise_consensus", "ref", "prev_glissante_t4"),
                          ("revision_med", "prev_med", "prev_prec_med"), ("erreur_med", "realise", "prev_med")]:
            xr, xa, xb = val[res][i], val[a][i], val[b][i]
            if xr is None or xa is None or xb is None:
                ok7 = False
                continue
            terme_vide = math.isnan(xa) or math.isnan(xb)
            if terme_vide != math.isnan(xr):
                ok7 = False
            elif not terme_vide and abs(xr - (xa - xb)) > 1e-9:
                ok7 = False
        # prev_glissante_t4 : partie verifiable sur le fichier -- vide si le tour t-4 est avant 1999T1
        if t is not None and t - 4 < T_PREMIER and brut.prev_glissante_t4[i] != "":
            ok7 = False
        if not ok7:
            echecs[7].add(i)

        # --- 8. Coherence entre lignes (la ligne verifiee porte l'echec)
        ok8 = True
        j = pos.get((v, y, t - 1)) if t is not None else None
        if j is not None:
            if brut.prev_prec[i] != brut.prev[j] or brut.n_rep_prec[i] != brut.n_rep[j]:
                ok8 = False
        if not ok8:
            echecs[8].add(i)

        # --- 9. Realise : present (unicite par (variable, annee_cible) testee plus bas)
        if val["realise"][i] is None or math.isnan(val["realise"][i]):
            echecs[9].add(i)

        # --- 10. Appartenance (toutes les lignes)
        ok10 = True
        comp_calc = int(all(val[c][i] is not None and not math.isnan(val[c][i])
                            for c in ["revision", "erreur", "surprise"]))
        if y is not None and t is not None:
            exclu = v in ("RGDP", "UNEM") and (y in (2020, 2021) or 8080 <= t <= 8087)
        else:
            exclu = False
        princ_calc = int(comp_calc == 1 and not exclu)
        if brut.complete[i] not in ("0", "1") or int(brut.complete[i]) != comp_calc:
            ok10 = False
        if brut.principal[i] not in ("0", "1") or int(brut.principal[i]) != princ_calc:
            ok10 = False
        if not ok10:
            echecs[10].add(i)

        # --- 11. Episodes
        if y is not None and t is not None:
            dans = [k for k, (P, T) in FENETRES.items() if t - 1 <= T and 4 * y + 3 >= P]
            attendu = f"E{dans[0]}" if len(dans) == 1 else ("" if not dans else "AMBIGU")
            if attendu == "AMBIGU":
                observations.append(f"ligne {i} dans plusieurs fenetres {dans}")
            if brut.episode[i] != attendu:
                echecs[11].add(i)
        else:
            echecs[11].add(i)

    # --- 8. (suite) constance dans (v, t_tour) et ref_prec(v,t) = ref(v,t-1)
    groupes = {}
    for i in range(n):
        groupes.setdefault((brut.variable[i], ent["t_tour"][i]), []).append(i)
    for (v, t), idx in groupes.items():
        for c in ["ref", "ref_periode", "ref_prec", "surprise", "grande_nouvelle"]:
            if len({brut[c][i] for i in idx}) > 1:
                echecs[8].update(idx)
        if (v, t - 1) in groupes:
            ref_avant = {brut.ref[j] for j in groupes[(v, t - 1)]}
            for i in idx:
                if len(ref_avant) != 1 or flottant(brut.ref_prec[i]) != flottant(next(iter(ref_avant))):
                    echecs[8].add(i)

    # --- 9. (suite) une seule valeur de realise par (variable, annee_cible)
    par_cible = {}
    for i in range(n):
        par_cible.setdefault((brut.variable[i], ent["annee_cible"][i]), []).append(i)
    for (v, y), idx in par_cible.items():
        if len({brut.realise[i] for i in idx}) != 1:
            echecs[9].update(idx)
    for v in VARIABLES:
        for y in ANNEES:
            if (v, y) not in par_cible:
                echec_fichier[2].append(f"cible absente {v} {y}")

    # --- 12. Grande nouvelle : recalcul de Q_v et de la coupure (section 6.2)
    principal = np.array([s == "1" for s in brut.principal])
    surprise = np.array([np.nan if (x is None) else x for x in val["surprise"]], dtype=float)
    L_calc, info_L = grande_nouvelle(brut.variable.values, np.array(ent["t_tour"], dtype=float), surprise,
                                     principal)
    for i in range(n):
        gn = brut.grande_nouvelle[i]
        s_present = not math.isnan(surprise[i])
        if s_present != (gn != ""):
            echecs[12].add(i)
            continue
        if not s_present:
            continue
        if gn not in ("0", "1") or int(gn) != L_calc[i]:
            echecs[12].add(i)
    # constance dans (v, t_tour)
    for (v, t), idx in groupes.items():
        if len({brut.grande_nouvelle[i] for i in idx}) > 1:
            echecs[12].update(idx)

    # Observations supplementaires (hors liste des controles ; ne comptent pas)
    for i in range(n):
        t = ent["t_tour"][i]
        if t is not None and t - 1 < T_PREMIER and (brut.n_rep_prec[i] != "0" or brut.prev_prec[i] != ""):
            observations.append(f"ligne {i}: tour precedent avant 1999T1 mais n_rep_prec/prev_prec non nuls")
        if (brut.prev[i] == "") != (brut.prev_med[i] == "") or (brut.prev_prec[i] == "") != (brut.prev_prec_med[i] == ""):
            observations.append(f"ligne {i}: presence de la moyenne et de la mediane differente")
        for c in ["ref", "ref_prec"]:
            if brut[c][i] != "" and nb_decimales(brut[c][i]) > 1:
                observations.append(f"ligne {i}: {c} a plus d'une decimale ({brut[c][i]})")
        r = brut.realise[i]
        if brut.variable[i] in ("HICP", "RGDP") and nb_decimales(r) > 1:
            observations.append(f"ligne {i}: realise {brut.variable[i]} a plus d'une decimale ({r})")
        if brut.variable[i] == "UNEM":
            x = float(r) * 120.0  # somme des 12 mois en dixiemes : doit etre entiere
            if abs(x - round(x)) > 1e-6:
                observations.append(f"ligne {i}: realise UNEM x 12 n'est pas un nombre a une decimale ({r})")
    for (v, t), idx in groupes.items():
        for c in ["ref_periode_prec", "prev_glissante_t4", "surprise_consensus"]:
            if len({brut[c][i] for i in idx}) > 1:
                observations.append(f"({v},{t}): {c} non constant dans le tour")
                break

    # Comptes de portee
    comptent = set()
    hors_principal = 0
    detail = {}
    for k in range(1, 13):
        if k in (1, 2):
            if echec_fichier[k]:
                comptent.add(k)
            detail[k] = {"portee": "fichier", "echecs": echec_fichier[k]}
            continue
        idx = sorted(echecs[k])
        sur_principal = [i for i in idx if principal[i]]
        sur_autres = [i for i in idx if not principal[i]]
        if k == 10:
            if idx:
                comptent.add(k)
        else:
            if sur_principal:
                comptent.add(k)
            hors_principal += len(sur_autres)
        detail[k] = {"portee": "toutes les lignes" if k == 10 else "lignes",
                     "lignes_en_echec_principal": [int(i) for i in sur_principal],
                     "lignes_en_echec_hors_principal": [int(i) for i in sur_autres]}
    return {
        "n_violations_schema": len(comptent),
        "controles_en_echec": sorted(comptent),
        "n_anomalies_hors_principal": hors_principal,
        "detail": detail,
        "observations": observations,
        "info_grande_nouvelle": info_L,
    }


# ----------------------------------------------------------------------------------------------------------
# Grande nouvelle (section 6.2)
# ----------------------------------------------------------------------------------------------------------
def grande_nouvelle(variable, t_tour, s, echantillon):
    """L par variable. Q_v sur les tours distincts de l'echantillon ; coupure stricte ou large.
    Renvoie L (float, NaN si s absent) et le detail."""
    L = np.full(len(s), np.nan)
    info = {}
    for v in VARIABLES:
        sel = (variable == v) & echantillon & ~np.isnan(s)
        tours = sorted(set(t_tour[sel]))
        abs_s = []
        for tt in tours:
            vals = np.abs(s[sel & (t_tour == tt)])
            abs_s.append(vals[0])  # constante dans le tour (controle 8)
        abs_s = np.array(abs_s)
        Q = float(np.quantile(abs_s, 2 / 3))
        n_strict = int(np.sum(abs_s > Q))
        n_large = int(np.sum(abs_s >= Q))
        T = len(abs_s)
        stricte = abs(n_strict / T - 1 / 3) <= abs(n_large / T - 1 / 3)
        tous = (variable == v) & ~np.isnan(s)
        if stricte:
            L[tous] = (np.abs(s[tous]) > Q).astype(float)
        else:
            L[tous] = (np.abs(s[tous]) >= Q).astype(float)
        info[v] = {"T_v": T, "Q_v": Q, "n_strict": n_strict, "n_large": n_large,
                   "coupure": "stricte" if stricte else "large",
                   "n_tours_grands": n_strict if stricte else n_large}
    return L, info


# ----------------------------------------------------------------------------------------------------------
# Regression et Driscoll-Kraay (sections 6.3, 6.4)
# ----------------------------------------------------------------------------------------------------------
def mco(y, X):
    XtX = X.T @ X
    if np.linalg.matrix_rank(XtX) < X.shape[1]:
        return None
    XtX_inv = np.linalg.inv(XtX)
    beta = XtX_inv @ (X.T @ y)
    u = y - X @ beta
    return beta, u, XtX_inv


def omega_dk(X, u, tours, retards):
    """Scores sommes par numero de tour, tours vides compris ; poids de Bartlett 1 - j/(retards+1)."""
    tours = np.asarray(tours, dtype=np.int64)
    t0, t1 = tours.min(), tours.max()
    H = np.zeros((t1 - t0 + 1, X.shape[1]))
    np.add.at(H, tours - t0, X * u[:, None])
    Om = H.T @ H
    for j in range(1, retards + 1):
        if j >= H.shape[0]:
            break
        w = 1.0 - j / (retards + 1.0)
        G = H[j:].T @ H[:-j]  # somme sur tau de H_tau H_{tau-j}'
        Om += w * (G + G.T)
    return Om


def omega_grappes(X, u, grappes):
    Om = np.zeros((X.shape[1], X.shape[1]))
    for gval in np.unique(grappes):
        h = (X[grappes == gval] * u[grappes == gval][:, None]).sum(axis=0)
        Om += np.outer(h, h)
    return Om


def sandwich(XtX_inv, Om):
    return XtX_inv @ Om @ XtX_inv


def matrice_principale(z_r, L, series, liste_series, par_variable=None):
    """6.3 : constantes, effets de classe, pentes de base (par serie), puis c (ou c_v en S1)."""
    cols = []
    for g in liste_series:
        cols.append((series == g).astype(float))
    for g in liste_series:
        cols.append((series == g).astype(float) * L)
    for g in liste_series:
        cols.append((series == g).astype(float) * z_r)
    if par_variable is None:
        cols.append(z_r * L)
    else:
        variable, liste_v = par_variable
        for v in liste_v:
            cols.append(z_r * L * (variable == v).astype(float))
    return np.column_stack(cols)


def ajuste(z_e, z_r, L, series, tours, sel, retards=8, par_variable=None):
    """Regression 6.3 sur les lignes sel ; renvoie c, son ecart-type DK et le reste. None si convention 6.10."""
    liste_series = sorted(set(series[sel]))
    pv = None
    if par_variable is not None:
        pv = (par_variable[0][sel], par_variable[1])
    X = matrice_principale(z_r[sel], L[sel], series[sel], liste_series, pv)
    y = z_e[sel]
    if sel.sum() < 50:
        return None
    r = mco(y, X)
    if r is None:
        return None
    beta, u, XtX_inv = r
    V = sandwich(XtX_inv, omega_dk(X, u, tours[sel], retards))
    return {"beta": beta, "u": u, "XtX_inv": XtX_inv, "V": V, "X": X, "y": y, "series": liste_series,
            "n": int(sel.sum())}


def main():
    brut = lire()
    schema = controles_schema(brut)

    d = brut.copy()
    for c in ["annee_cible", "t_tour", "horizon", "complete", "principal"]:
        d[c] = d[c].astype(int)
    for c in ["revision", "erreur", "surprise", "surprise_consensus", "revision_med", "erreur_med", "realise",
              "prev_prec"]:
        d[c] = [float("nan") if s == "" else float(s) for s in brut[c]]

    variable = d.variable.values
    series = np.array([f"{v}_h{h}" for v, h in zip(d.variable, d.horizon)])
    tours = d.t_tour.values.astype(np.int64)
    annee = d.annee_cible.values
    P = d.principal.values == 1
    C = d.complete.values == 1
    rev = d.revision.values
    err = d.erreur.values
    s = d.surprise.values

    # --- 6.1 Reduction par serie sur les lignes principales
    liste_series = sorted(set(series))
    z_r = np.full(len(d), np.nan)
    z_e = np.full(len(d), np.nan)
    z_rm = np.full(len(d), np.nan)
    z_em = np.full(len(d), np.nan)
    z_p = np.full(len(d), np.nan)
    p_val = err + rev  # p = erreur + revision
    k_g = {}
    for g in liste_series:
        mg = series == g
        sel = mg & P
        mr, sr = rev[sel].mean(), rev[sel].std(ddof=1)
        me, se = err[sel].mean(), err[sel].std(ddof=1)
        z_r[mg] = (rev[mg] - mr) / sr
        z_e[mg] = (err[mg] - me) / se
        k_g[g] = sr / se
        rm, em = d.revision_med.values, d.erreur_med.values
        z_rm[mg] = (rm[mg] - rm[sel].mean()) / rm[sel].std(ddof=1)
        z_em[mg] = (em[mg] - em[sel].mean()) / em[sel].std(ddof=1)
        z_p[mg] = (p_val[mg] - p_val[sel].mean()) / p_val[sel].std(ddof=1)
    k_moyen = float(np.mean([k_g[g] for g in liste_series]))

    # --- 6.2 Grande nouvelle
    L, info_L = grande_nouvelle(variable, tours.astype(float), s, P)

    # --- 6.3-6.5 Regression principale
    ch = {}
    res = ajuste(z_e, z_r, L, series, tours, P)
    beta, V = res["beta"], res["V"]
    n = res["n"]
    ic = 18  # position de c
    c = float(beta[ic])
    et_c = float(math.sqrt(V[ic, ic]))
    b_g = beta[12:18]
    b_moyen = float(np.mean(b_g))
    w = np.zeros(19)
    w[12:18] = 1 / 6
    et_b_moyen = float(math.sqrt(w @ V @ w))

    ch["n_principal"] = int(P.sum())
    ch["n_tours"] = int(len(set(tours[P])))
    ch["n_annees_cibles"] = int(len(set(annee[P])))
    ch["n_grands"] = int(np.sum(P & (L == 1)))
    ch["n_tours_grands"] = int(len(set(tours[P & (L == 1)])))
    ch["c"] = c
    ch["et_c_dk8"] = et_c
    ch["t_c"] = c / et_c
    ch["borne_basse_ic90"] = c - VALEUR_CRITIQUE * et_c
    ch["borne_haute_ic90"] = c + VALEUR_CRITIQUE * et_c
    ch["b_moyen"] = b_moyen
    ch["et_b_moyen_dk8"] = et_b_moyen
    ch["borne_basse_b_moyen_ic90"] = b_moyen - VALEUR_CRITIQUE * et_b_moyen

    # --- 6.6 Pente commune
    Xb = np.column_stack([(series[P] == g).astype(float) for g in liste_series] + [z_r[P]])
    beta_b, u_b, XtXi_b = mco(z_e[P], Xb)
    Vb = sandwich(XtXi_b, omega_dk(Xb, u_b, tours[P], 8))
    b_commun = float(beta_b[-1])
    et_b_commun = float(math.sqrt(Vb[-1, -1]))
    ch["b_commun"] = b_commun
    ch["et_b_commun_dk8"] = et_b_commun
    ch["borne_basse_b_commun_ic90"] = b_commun - VALEUR_CRITIQUE * et_b_commun
    ch["controle_positif_ok"] = int(ch["borne_basse_b_commun_ic90"] > 0 or ch["borne_basse_b_moyen_ic90"] > 0)
    ch["k_moyen"] = k_moyen
    ch["pente_moyenne_grandes"] = b_moyen + c

    # --- 6.7 Pertinence et biais mecanique
    def rapport(z):
        num0, num1 = [], []
        for g in liste_series:
            for l, acc in ((0, num0), (1, num1)):
                sel = P & (series == g) & (L == l)
                m = z[sel].mean()
                acc.extend(list((z[sel] - m) ** 2))
        a_ = float(np.mean(num0))
        A_ = float(np.mean(num1))
        return a_, A_
    a, A = rapport(z_r)
    ap, Ap = rapport(z_p)
    ch["rapport_variance_revision"] = A / a
    ch["rapport_variance_ecart_prec"] = Ap / ap
    biais = (2 * b_moyen + k_moyen) * 0.10 * (1 / a - 1 / A)
    seuil = max(0.10, biais)
    ch["biais_mecanique_nu20"] = biais
    ch["seuil_survie_bas"] = seuil
    ch["borne_basse_moins_seuil"] = ch["borne_basse_ic90"] - seuil
    ch["pertinence_manquante"] = int(ch["rapport_variance_revision"] < 1.25 and ch["borne_basse_moins_seuil"] <= 0)
    ch["marge_indecision"] = min(seuil - ch["borne_basse_ic90"], ch["borne_haute_ic90"] - 0.40)

    # --- 6.8 Episodes
    ep = d.episode.values
    t_sans, c_sans = {}, {}
    for k in (1, 2, 3):
        sel = P & (ep != f"E{k}")
        r = ajuste(z_e, z_r, L, series, tours, sel)
        if r is None:
            c_sans[k], t_sans[k] = 0.0, 0.0
        else:
            ck = float(r["beta"][-1])
            c_sans[k] = ck
            t_sans[k] = ck / math.sqrt(r["V"][-1, -1])
        ch[f"c_sans_E{k}"] = c_sans[k]
    for k in (1, 2, 3):
        ch[f"t_sans_E{k}"] = t_sans[k]
    t_min = min(t_sans.values())
    ch["t_min_sans_episode"] = t_min
    ch["c_min_sans_episode"] = min(c_sans.values())
    ch["episode_t_min"] = int(min(k for k in (1, 2, 3) if t_sans[k] == t_min))
    ch["conflit_robustesse"] = int(ch["borne_basse_ic90"] > seuil and ch["borne_haute_ic90"] >= 0.40
                                   and t_min < 1 and ch["c_min_sans_episode"] > 0)

    # --- 6.10 iid et n effectif
    sigma2 = float(res["u"] @ res["u"]) / (n - 19)
    et_iid = math.sqrt(sigma2 * res["XtX_inv"][ic, ic])
    ch["et_c_iid"] = et_iid
    ch["n_effectif"] = n * (et_iid / et_c) ** 2

    # --- S2 inference
    X, u, XtXi = res["X"], res["u"], res["XtX_inv"]
    for lag, nom in ((4, "et_c_dk4"), (12, "et_c_dk12"), (0, "et_c_dk0")):
        ch[nom] = float(math.sqrt(sandwich(XtXi, omega_dk(X, u, tours[P], lag))[ic, ic]))
    ch["et_c_grappes_annee"] = float(math.sqrt(sandwich(XtXi, omega_grappes(X, u, annee[P]))[ic, ic]))

    def secondaire(nom, r, pos=-1):
        if r is None:
            ch[f"c_{nom}"], ch[f"et_c_{nom}_dk8"] = 0.0, 0.0
        else:
            ch[f"c_{nom}"] = float(r["beta"][pos])
            ch[f"et_c_{nom}_dk8"] = float(math.sqrt(r["V"][pos, pos]))

    # S3 avec la pandemie : lignes complete = 1
    secondaire("avec_pandemie", ajuste(z_e, z_r, L, series, tours, C))
    # S4 avant 2020
    secondaire("avant_2020", ajuste(z_e, z_r, L, series, tours, P & (annee <= 2019)))
    # S5 par horizon
    hz = d.horizon.values
    secondaire("annee_en_cours", ajuste(z_e, z_r, L, series, tours, P & (hz == 0)))
    secondaire("annee_suivante", ajuste(z_e, z_r, L, series, tours, P & (hz == 1)))
    # S6 medianes
    secondaire("mediane", ajuste(z_em, z_rm, L, series, tours, P))
    # S7 coupure de la fiche
    L7 = (np.abs(z_r) > 1).astype(float)
    secondaire("coupure_revision", ajuste(z_e, z_r, L7, series, tours, P))
    # S8 surprise relative au consensus
    sc = d.surprise_consensus.values
    sel8 = P & ~np.isnan(sc)
    L8, info_L8 = grande_nouvelle(variable, tours.astype(float), sc, sel8)
    ch["n_surprise_consensus"] = int(sel8.sum())
    secondaire("surprise_consensus", ajuste(z_e, z_r, L8, series, tours, sel8))
    # S1 par variable
    r1 = ajuste(z_e, z_r, L, series, tours, P, par_variable=(variable, VARIABLES))
    for j, v in enumerate(VARIABLES):
        pos = 18 + j
        if r1 is None:
            ch[f"c_{v}"], ch[f"et_c_{v}_dk8"] = 0.0, 0.0
        else:
            ch[f"c_{v}"] = float(r1["beta"][pos])
            ch[f"et_c_{v}_dk8"] = float(math.sqrt(r1["V"][pos, pos]))

    # --- Assemblage dans l'ordre de la section 12
    ch["n_violations_schema"] = int(schema["n_violations_schema"])
    ch["n_anomalies_hors_principal"] = int(schema["n_anomalies_hors_principal"])
    texte = (ICI / "preenregistrement.md").read_text(encoding="utf-8")
    bloc = re.findall(r"```json\s*(\{.*?\})\s*```", texte, flags=re.S)[-1]
    champs = json.loads(bloc)["champs_verification"]
    manquants = [f for f in champs if f not in ch]
    assert not manquants, manquants
    sortie = {f: ch[f] for f in champs}
    for f, x in sortie.items():
        assert isinstance(x, (int, float)) and x == x, f
    (ICI / "verification.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n",
                                           encoding="utf-8")

    detail = {
        "schema": {k: v for k, v in schema.items() if k != "info_grande_nouvelle"},
        "grande_nouvelle": info_L,
        "grande_nouvelle_S8": info_L8,
        "k_g": k_g,
        "b_g": {g: float(b) for g, b in zip(res["series"], b_g)},
        "delta_g": {g: float(b) for g, b in zip(res["series"], beta[6:12])},
        "a": a, "A": A, "a_ecart_prec": ap, "A_ecart_prec": Ap,
        "comptes": {
            "principal_par_variable": {v: int(np.sum(P & (variable == v))) for v in VARIABLES},
            "complete_par_variable": {v: int(np.sum(C & (variable == v))) for v in VARIABLES},
            "principal_par_horizon_et_variable": {f"{v}_h{h}": int(np.sum(P & (variable == v) & (hz == h)))
                                                  for v in VARIABLES for h in (0, 1)},
            "episodes_principal": {e: int(np.sum(P & (ep == e))) for e in ("E1", "E2", "E3", "")},
            "episodes_fichier": {e: int(np.sum(ep == e)) for e in ("E1", "E2", "E3", "")},
            "lignes_par_tour_min_max_moy": [int(pd.Series(tours[P]).value_counts().min()),
                                            int(pd.Series(tours[P]).value_counts().max()),
                                            float(pd.Series(tours[P]).value_counts().mean())],
            "tours_principal_min_max": [int(tours[P].min()), int(tours[P].max())],
            "n_grands_par_variable": {v: int(np.sum(P & (L == 1) & (variable == v))) for v in VARIABLES},
            "n_complete": int(C.sum()),
        },
    }
    print(json.dumps(sortie, ensure_ascii=False, indent=1))
    print(json.dumps({k: detail[k] for k in detail if k != "schema"}, ensure_ascii=False, indent=1))
    print(json.dumps(schema["detail"], ensure_ascii=False))
    print("schema:", schema["controles_en_echec"], "hors principal:", schema["n_anomalies_hors_principal"])
    print("observations:", schema["observations"][:50], len(schema["observations"]))


if __name__ == "__main__":
    main()
