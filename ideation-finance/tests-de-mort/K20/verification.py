"""K20 -- vérification indépendante, écrite à partir du seul texte de preenregistrement.md.

Lit uniquement K20_analyse.csv. Écrit verification.json (champs "champs_verification", nombres seulement)
et imprime le détail des contrôles de schéma et des lectures alternatives sur la sortie standard.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parent
FICHIER = ICI / "K20_analyse.csv"
SORTIE = ICI / "verification.json"

VARS = ["PGDP", "RGDP", "UNEMP", "CPI", "TBILL"]
COLONNES = ["variable", "cible", "t_cible", "annee_cible", "t_enquete_h3", "t_enquete_h4", "prev_h3", "prev_h4",
            "nowcast_q4", "prev_h3_med", "prev_h4_med", "millesime_realise", "niveau_cible", "niveau_avant",
            "realise", "millesime_realise_q4", "niveau_q4", "niveau_avant_q4", "realise_q4", "revision", "erreur",
            "surprise", "revision_med", "erreur_med", "complete", "principal", "episode", "grande_nouvelle"]
NUM = ["t_cible", "annee_cible", "t_enquete_h3", "t_enquete_h4", "prev_h3", "prev_h4", "nowcast_q4", "prev_h3_med",
       "prev_h4_med", "niveau_cible", "niveau_avant", "realise", "niveau_q4", "niveau_avant_q4", "realise_q4",
       "revision", "erreur", "surprise", "revision_med", "erreur_med", "complete", "principal", "grande_nouvelle"]
FENETRES = {1: (7879, 7887), 2: (7895, 7904), 3: (7920, 7935), 4: (7962, 7968), 5: (8004, 8011),
            6: (8031, 8041), 7: (8079, 8095)}
TOL = 1e-6


def tnum(annee, q):
    return 4 * annee + (q - 1)


def libelle(t):
    return f"{t // 4}-Q{t % 4 + 1}"


# ---------------------------------------------------------------- lecture
brut = pd.read_csv(FICHIER, dtype=str, keep_default_na=False, encoding="utf-8")
d = brut.copy()
for col in NUM:
    if col in d.columns:
        d[col] = pd.to_numeric(d[col].replace("", np.nan), errors="coerce")
vide = {c: (brut[c] == "") for c in brut.columns}

violations = {}   # n° contrôle -> liste de messages


def viol(k, msg):
    violations.setdefault(k, []).append(msg)


def ident(i):
    return f"{brut.at[i, 'variable']} {brut.at[i, 'cible']} (ligne {i + 2})"


# valeurs présentes mais non numériques
for col in NUM:
    if col in brut.columns:
        bad = (~vide[col]) & d[col].isna()
        for i in np.where(bad)[0]:
            viol(7, f"{ident(i)} : {col} non numérique '{brut.at[i, col]}'")

# ---------------------------------------------------------------- contrôle 1 : colonnes
if list(brut.columns) != COLONNES:
    viol(1, f"colonnes {list(brut.columns)}")

# ---------------------------------------------------------------- contrôle 2 : grille
grille = [(v, t) for v in VARS for t in (range(7879, 8107) if v in ("PGDP", "RGDP", "UNEMP") else range(7930, 8107))]
if len(d) != 1038:
    viol(2, f"{len(d)} lignes au lieu de 1038")
paires = list(zip(d["variable"], d["t_cible"].astype("Int64")))
if paires != grille:
    if sorted(map(str, paires)) == sorted(map(str, grille)):
        viol(2, "grille complète mais tri non conforme")
    else:
        viol(2, "grille non conforme")

# ---------------------------------------------------------------- contrôle 3 : identifiants
for i, r in d.iterrows():
    t = int(r["t_cible"])
    if brut.at[i, "cible"] != libelle(t):
        viol(3, f"{ident(i)} : cible != {libelle(t)}")
    if r["annee_cible"] != t // 4:
        viol(3, f"{ident(i)} : annee_cible")
    if r["t_enquete_h3"] != t - 3:
        viol(3, f"{ident(i)} : t_enquete_h3")
    if r["t_enquete_h4"] != t - 4:
        viol(3, f"{ident(i)} : t_enquete_h4")

# ---------------------------------------------------------------- contrôle 4 : présence des prévisions
manq_h4 = {(v, tnum(a, q)) for v in ("PGDP", "RGDP", "UNEMP") for (a, q) in
           [(1970, 1), (1970, 2), (1970, 3), (1971, 1), (1975, 3)]}
for i, r in d.iterrows():
    cle = (r["variable"], int(r["t_cible"]))
    for col in ("prev_h4", "prev_h4_med"):
        if vide[col][i] != (cle in manq_h4):
            viol(4, f"{ident(i)} : {col} {'vide' if vide[col][i] else 'présent'}")
    for col in ("prev_h3", "prev_h3_med", "nowcast_q4"):
        if vide[col][i]:
            viol(4, f"{ident(i)} : {col} vide")

# ---------------------------------------------------------------- contrôle 5 : millésimes
PREF = {"PGDP": "P", "RGDP": "ROUTPUT"}
EXC_REAL = {tnum(1995, 4), tnum(2025, 3), tnum(2025, 4)}
EXC_Q4 = {tnum(1996, 4), tnum(2026, 3)}
viol5_hors_texte = []   # millésime non vide alors que realise vide (définition de colonne, pas le contrôle 5)


def num_millesime(code, pref):
    m = re.fullmatch(pref + r"(\d{2})Q([1-4])", code)
    if not m:
        return None
    aa, n = int(m.group(1)), int(m.group(2))
    annee = 1900 + aa if aa >= 60 else 2000 + aa
    return 4 * annee + n - 1


for i, r in d.iterrows():
    v, t = r["variable"], int(r["t_cible"])
    for colm, colr, attendu, exc in (("millesime_realise", "realise", t + 1, t in EXC_REAL),
                                      ("millesime_realise_q4", "realise_q4", t - 3, t in EXC_Q4)):
        code = brut.at[i, colm]
        if vide[colr][i]:
            if code != "":
                viol5_hors_texte.append(f"{ident(i)} : {colm}='{code}' alors que {colr} est vide")
            continue
        if v in PREF:
            nm = num_millesime(code, PREF[v])
            cible_num = attendu + 1 if exc else attendu
            if nm is None or nm != cible_num:
                viol(5, f"{ident(i)} : {colm}='{code}' (numéro {nm}, attendu {cible_num})")
        else:
            if code != "FRED":
                viol(5, f"{ident(i)} : {colm}='{code}' au lieu de FRED")

# ---------------------------------------------------------------- contrôle 6 : plages
PL_TAUX = {"PGDP": (-10, 25), "RGDP": (-40, 40), "UNEMP": (2, 16), "CPI": (-15, 25), "TBILL": (-0.5, 20)}
PL_NIV = {"PGDP": (50, 300), "RGDP": (500, 40000), "CPI": (20, 400), "UNEMP": (2, 16), "TBILL": (-0.5, 20)}
for i, r in d.iterrows():
    v = r["variable"]
    for col in ("prev_h3", "prev_h4", "nowcast_q4", "prev_h3_med", "prev_h4_med", "realise", "realise_q4"):
        x = r[col]
        if not np.isnan(x) and not (PL_TAUX[v][0] <= x <= PL_TAUX[v][1]):
            viol(6, f"{ident(i)} : {col}={x}")
    for col in ("niveau_cible", "niveau_avant", "niveau_q4", "niveau_avant_q4"):
        x = r[col]
        if not np.isnan(x) and not (PL_NIV[v][0] <= x <= PL_NIV[v][1]):
            viol(6, f"{ident(i)} : {col}={x}")

# ---------------------------------------------------------------- contrôle 7 : formules
for i, r in d.iterrows():
    v = r["variable"]
    for colr, cn, cav in (("realise", "niveau_cible", "niveau_avant"), ("realise_q4", "niveau_q4", "niveau_avant_q4")):
        comps = [cn, cav] if v in ("PGDP", "RGDP", "CPI") else [cn]
        comp_vide = any(np.isnan(r[c]) for c in comps)
        if np.isnan(r[colr]) != comp_vide:
            viol(7, f"{ident(i)} : {colr} vide={np.isnan(r[colr])}, composante vide={comp_vide}")
            continue
        if not comp_vide:
            calc = 100 * ((r[cn] / r[cav]) ** 4 - 1) if len(comps) == 2 else r[cn]
            if abs(calc - r[colr]) > TOL:
                viol(7, f"{ident(i)} : {colr}={r[colr]} != {calc}")
    for col, a, b in (("revision", "prev_h3", "prev_h4"), ("erreur", "realise", "prev_h3"),
                      ("surprise", "realise_q4", "nowcast_q4"), ("revision_med", "prev_h3_med", "prev_h4_med"),
                      ("erreur_med", "realise", "prev_h3_med")):
        op_vide = np.isnan(r[a]) or np.isnan(r[b])
        if np.isnan(r[col]) != op_vide:
            viol(7, f"{ident(i)} : {col} vide={np.isnan(r[col])}, opérande vide={op_vide}")
        elif not op_vide and abs((r[a] - r[b]) - r[col]) > TOL:
            viol(7, f"{ident(i)} : {col}={r[col]} != {r[a] - r[b]}")

# ---------------------------------------------------------------- contrôle 8 : cohérence entre lignes
idx = {(r["variable"], int(r["t_cible"])): i for i, r in d.iterrows()}
for i, r in d.iterrows():
    j = idx.get((r["variable"], int(r["t_cible"]) - 4))
    if j is None:
        continue
    a, b = r["realise_q4"], d.at[j, "realise"]
    if not np.isnan(a) and not np.isnan(b) and abs(a - b) > TOL:
        viol(8, f"{ident(i)} : realise_q4={a} != realise(t-4)={b}")
    ma, mb = brut.at[i, "millesime_realise_q4"], brut.at[j, "millesime_realise"]
    if ma != "" and mb != "" and ma != mb:
        viol(8, f"{ident(i)} : millesime_realise_q4={ma} != {mb}")

# ---------------------------------------------------------------- contrôle 9 : niveaux
for i, r in d.iterrows():
    v = r["variable"]
    for cn, cav in (("niveau_cible", "niveau_avant"), ("niveau_q4", "niveau_avant_q4")):
        if v in ("UNEMP", "TBILL"):
            if not vide[cav][i]:
                viol(9, f"{ident(i)} : {cav} présent")
        elif not np.isnan(r[cn]) and np.isnan(r[cav]):
            viol(9, f"{ident(i)} : {cav} vide alors que {cn} présent")

# ---------------------------------------------------------------- contrôle 10 : indicateurs
comp = (~d["revision"].isna() & ~d["erreur"].isna() & ~d["surprise"].isna()).astype(int)
pand = d["variable"].isin(["RGDP", "UNEMP"]) & d["t_cible"].between(8080, 8087)
princ = ((comp == 1) & ~pand).astype(int)
for i in np.where(comp.values != d["complete"].values)[0]:
    viol(10, f"{ident(i)} : complete={d.at[i, 'complete']} au lieu de {comp[i]}")
for i in np.where(princ.values != d["principal"].values)[0]:
    viol(10, f"{ident(i)} : principal={d.at[i, 'principal']} au lieu de {princ[i]}")

# ---------------------------------------------------------------- contrôle 11 : épisodes
for i, r in d.iterrows():
    t = int(r["t_cible"])
    att = ""
    for k, (lo, hi) in FENETRES.items():
        if lo <= t <= hi:
            att = f"E{k}"
    if brut.at[i, "episode"] != att:
        viol(11, f"{ident(i)} : episode='{brut.at[i, 'episode']}' au lieu de '{att}'")

# ---------------------------------------------------------------- étapes 1-2 (sur la colonne principal du fichier)
P = d["principal"] == 1
n_principal = int(P.sum())
const = {}
d["z_r"] = np.nan
d["z_e"] = np.nan
d["z_rm"] = np.nan
d["z_em"] = np.nan
d["L"] = np.nan
Q = {}
for v in VARS:
    mv = d["variable"] == v
    pv = mv & P
    mr, sr = d.loc[pv, "revision"].mean(), d.loc[pv, "revision"].std(ddof=1)
    me, se = d.loc[pv, "erreur"].mean(), d.loc[pv, "erreur"].std(ddof=1)
    const[v] = (mr, sr, me, se)
    d.loc[mv, "z_r"] = (d.loc[mv, "revision"] - mr) / sr
    d.loc[mv, "z_e"] = (d.loc[mv, "erreur"] - me) / se
    # S6 : médianes réduites de la même façon sur les mêmes lignes
    mrm, srm = d.loc[pv, "revision_med"].mean(), d.loc[pv, "revision_med"].std(ddof=1)
    mem, sem = d.loc[pv, "erreur_med"].mean(), d.loc[pv, "erreur_med"].std(ddof=1)
    d.loc[mv, "z_rm"] = (d.loc[mv, "revision_med"] - mrm) / srm
    d.loc[mv, "z_em"] = (d.loc[mv, "erreur_med"] - mem) / sem
    Q[v] = float(np.quantile(np.abs(d.loc[pv, "surprise"].values), 2 / 3))
    ms = mv & d["surprise"].notna()
    d.loc[ms, "L"] = (np.abs(d.loc[ms, "surprise"]) > Q[v]).astype(float)
k_v = {v: const[v][1] / const[v][3] for v in VARS}
k_moyen = float(np.mean([k_v[v] for v in VARS]))

# ---------------------------------------------------------------- contrôle 12 : grande nouvelle
for i, r in d.iterrows():
    if vide["grande_nouvelle"][i] != np.isnan(r["surprise"]):
        viol(12, f"{ident(i)} : présence de grande_nouvelle")
    elif not np.isnan(r["surprise"]) and r["grande_nouvelle"] != r["L"]:
        viol(12, f"{ident(i)} : grande_nouvelle={r['grande_nouvelle']} au lieu de {r['L']}")


# ---------------------------------------------------------------- estimateur et Driscoll-Kraay
def matrice(df, Lcol="L", zr="z_r", par_variable=False):
    cols = []
    for v in VARS:
        cols.append((df["variable"] == v).astype(float).values)
    for v in VARS:
        cols.append(((df["variable"] == v) * df[Lcol]).astype(float).values)
    for v in VARS:
        cols.append(((df["variable"] == v) * df[zr]).astype(float).values)
    if par_variable:
        for v in VARS:
            cols.append(((df["variable"] == v) * df[zr] * df[Lcol]).astype(float).values)
    else:
        cols.append((df[zr] * df[Lcol]).astype(float).values)
    return np.column_stack(cols)


def mco(df, Lcol="L", zr="z_r", ze="z_e", par_variable=False, retards=(4,)):
    df = df.dropna(subset=[zr, ze, Lcol])
    X = matrice(df, Lcol, zr, par_variable)
    y = df[ze].values.astype(float)
    n, p = X.shape
    if n < 50 or np.linalg.matrix_rank(X.T @ X) < p:
        return None
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ X.T @ y
    u = y - X @ beta
    h = X * u[:, None]
    t = df["t_cible"].astype(int).values
    t0, t1 = t.min(), t.max()
    H = np.zeros((t1 - t0 + 1, p))
    np.add.at(H, t - t0, h)
    out = {"beta": beta, "n": n, "df": df, "X": X, "u": u}
    for Lg in retards:
        Om = H.T @ H
        for j in range(1, Lg + 1):
            G = H[j:].T @ H[:-j]
            Om += (1 - j / (Lg + 1)) * (G + G.T)
        V = XtXi @ Om @ XtXi
        out[f"V{Lg}"] = V
    s2 = (u @ u) / (n - p)
    out["Viid"] = s2 * XtXi
    return out


base = d[P].copy()
R = mco(base, retards=(4, 8, 0))
c = float(R["beta"][15])
et_dk4 = float(np.sqrt(R["V4"][15, 15]))
et_dk8 = float(np.sqrt(R["V8"][15, 15]))
et_dk0 = float(np.sqrt(R["V0"][15, 15]))
et_iid = float(np.sqrt(R["Viid"][15, 15]))
b_v = R["beta"][10:15]
b_moyen = float(np.mean(b_v))
t_c = c / et_dk4
bb = c - 1.645 * et_dk4
bh = c + 1.645 * et_dk4
n_eff = n_principal * (et_iid / et_dk4) ** 2

# biais mécanique
num0 = den0 = num1 = den1 = 0.0
sq0, sq1 = [], []
for v in VARS:
    pv = base[base["variable"] == v]
    for ell, lst in ((0, sq0), (1, sq1)):
        zz = pv.loc[pv["L"] == ell, "z_r"].values
        lst.extend(list((zz - zz.mean()) ** 2))
a_var = float(np.mean(sq0))
A_var = float(np.mean(sq1))
rapport = A_var / a_var
biais = (2 * b_moyen + k_moyen) * 0.10 * (1 / a_var - 1 / A_var)
seuil = max(0.10, biais)
bb_moins_seuil = bb - seuil
marge = min(seuil - bb, bh - 0.40)

n_grands = int((base["L"] == 1).sum())
n_trim = int(base["t_cible"].nunique())
n_trim_grands = int(base.loc[base["L"] == 1, "t_cible"].nunique())

# épisodes
c_sans, t_sans = {}, {}
for k, (lo, hi) in FENETRES.items():
    sub = base[~base["t_cible"].between(lo, hi)]
    Rk = mco(sub)
    if Rk is None:
        c_sans[k], t_sans[k] = 0.0, 0.0
        continue
    c_sans[k] = float(Rk["beta"][15])
    t_sans[k] = c_sans[k] / float(np.sqrt(Rk["V4"][15, 15]))
t_min = min(t_sans.values())
ep_t_min = min(k for k in FENETRES if t_sans[k] == t_min)
c_min = min(c_sans.values())
conflit = int(bb > seuil and bh >= 0.40 and t_min < 1 and c_min > 0)


def c_et(Rx, j=15):
    if Rx is None:
        return 0.0, 0.0
    return float(Rx["beta"][j]), float(np.sqrt(Rx["V4"][j, j]))


# S1
R1 = mco(base, par_variable=True)
s1 = {v: c_et(R1, 15 + i) for i, v in enumerate(VARS)}
# S3
S3 = mco(d[d["complete"] == 1].copy())
# S4, S5
S4 = mco(base[base["t_cible"] >= 7940])
S5 = mco(base[base["t_cible"] <= 8079])
# S6
S6 = mco(base, zr="z_rm", ze="z_em")
# S7
base["Lp"] = (np.abs(base["z_r"]) > 1).astype(float)
S7 = mco(base, Lcol="Lp")

n_violations = len(violations)

res = {
    "n_violations_schema": n_violations,
    "n_principal": n_principal,
    "c": c,
    "et_c_dk4": et_dk4,
    "t_c": t_c,
    "borne_basse_ic90": bb,
    "borne_haute_ic90": bh,
    "rapport_variance_revision": rapport,
    "b_moyen": b_moyen,
    "k_moyen": k_moyen,
    "pente_moyenne_grandes": b_moyen + c,
    "biais_mecanique_nu20": biais,
    "seuil_survie_bas": seuil,
    "borne_basse_moins_seuil": bb_moins_seuil,
    "marge_indecision": marge,
    "t_min_sans_episode": t_min,
    "c_min_sans_episode": c_min,
    "episode_t_min": ep_t_min,
    "conflit_robustesse": conflit,
    "n_grands": n_grands,
    "n_trimestres": n_trim,
    "n_trimestres_grands": n_trim_grands,
    "et_c_iid": et_iid,
    "n_effectif": n_eff,
}
for k in FENETRES:
    res[f"c_sans_E{k}"] = c_sans[k]
res["et_c_dk8"] = et_dk8
res["et_c_dk0"] = et_dk0
res["c_avec_pandemie"], res["et_c_avec_pandemie_dk4"] = c_et(S3)
res["c_depuis_1985"], res["et_c_depuis_1985_dk4"] = c_et(S4)
res["c_avant_2020"], res["et_c_avant_2020_dk4"] = c_et(S5)
res["c_mediane"], res["et_c_mediane_dk4"] = c_et(S6)
res["c_coupure_revision"], res["et_c_coupure_revision_dk4"] = c_et(S7)
for v in VARS:
    res[f"c_{v}"] = s1[v][0]
for v in VARS:
    res[f"et_c_{v}_dk4"] = s1[v][1]

res = {k: (int(v) if isinstance(v, (int, np.integer)) else float(v)) for k, v in res.items()}
SORTIE.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- détail (sortie standard)
if "--detail" in sys.argv:
    print("== contrôles violés :", sorted(violations))
    for k in sorted(violations):
        print(f"-- contrôle {k} : {len(violations[k])} échec(s)")
        for m in violations[k][:40]:
            print("   ", m)
    print("== hors texte du contrôle 5 :", len(viol5_hors_texte))
    for m in viol5_hors_texte[:20]:
        print("   ", m)
    print("== Q_v :", Q)
    print("== k_v :", k_v)
    print("== b_v :", dict(zip(VARS, b_v)))
    print("== a, A :", a_var, A_var)
    print("== t sans épisode :", t_sans)
    print("== n par variable principal :", base["variable"].value_counts().to_dict())
    print("== n principal par épisode :", {k: int(base["t_cible"].between(*w).sum()) for k, w in FENETRES.items()})
    print("== L=1 par variable :", base.groupby("variable")["L"].sum().to_dict())
    print(json.dumps(res, indent=1))
