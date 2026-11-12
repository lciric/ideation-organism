"""Vérification indépendante de J02, écrite à partir du seul preenregistrement.md.

Lit uniquement J02_analyse.csv, refait les contrôles de schéma (section 5), la statistique principale,
la garde de robustesse et les analyses secondaires (section 6), et écrit verification.json.
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "J02_analyse.csv")
SORTIE = os.path.join(ICI, "verification.json")

COLONNES = ["cible", "t_cible", "annee_cible", "millesime_h2", "t_millesime_h2", "mois_titre_h2",
            "annee_titre_h2", "t_premier_F_h2", "statut_h2", "projection_h2", "millesime_h3",
            "t_millesime_h3", "mois_titre_h3", "annee_titre_h3", "t_premier_F_h3", "statut_h3",
            "projection_h3", "indice_m1", "indice_m2", "indice_m3", "indice_an_avant_m1",
            "indice_an_avant_m2", "indice_an_avant_m3", "realise", "revision", "erreur"]
LETTRE_TRIM = {"W": 1, "G": 2, "S": 3, "A": 4}
LISTE_FIGEE = [f"{l}{a % 100:02d}" for a in range(1999, 2026) for l in "WGSA"] + ["W26"]
assert len(LISTE_FIGEE) == 109


def num_t(annee, trim):
    return 4 * annee + (trim - 1)


def annee_code(code):
    aa = int(code[1:])
    return 1900 + aa if aa >= 90 else 2000 + aa


def t_code(code):
    return num_t(annee_code(code), LETTRE_TRIM[code[0]])


def vide(s):
    return s is None or s.strip() == ""


def f(s):
    return None if vide(s) else float(s)


def entier(s):
    if vide(s):
        return None
    if not re.fullmatch(r"-?\d+", s.strip()):
        raise ValueError(f"pas un entier : {s!r}")
    return int(s)


# --------------------------------------------------------------------------------------------
# Lecture brute
with open(FICHIER, newline="", encoding="utf-8") as fh:
    lecteur = csv.reader(fh)
    entete = next(lecteur)
    lignes_brutes = [r for r in lecteur]
lignes = [dict(zip(entete, r)) for r in lignes_brutes]

controles = {}
details = {}


def echec(k, msg):
    controles[k] = False
    details.setdefault(k, []).append(msg)


for k in range(1, 12):
    controles[k] = True

# 1. Colonnes
if entete != COLONNES:
    echec(1, f"entête {entete}")
if any(len(r) != len(entete) for r in lignes_brutes):
    echec(1, "ligne de longueur différente de l'entête")

# 2. Lignes
ts = []
for L in lignes:
    try:
        ts.append(entier(L["t_cible"]))
    except Exception as ex:
        echec(2, str(ex))
if len(lignes) != 108:
    echec(2, f"{len(lignes)} lignes")
if ts != list(range(7999, 8107)):
    echec(2, "t_cible n'est pas 7999..8106 croissant")

# 3. Cible
for L in lignes:
    t = entier(L["t_cible"])
    an, tr = t // 4, t % 4 + 1
    if L["cible"] != f"{an}-Q{tr}" or entier(L["annee_cible"]) != an:
        echec(3, L["cible"])

# 4. Millésimes ; 5. Lettre et titre ; 6. Premier F ; 7. Projection précède la réalisation
for L in lignes:
    t = entier(L["t_cible"])
    for h in (2, 3):
        code = L[f"millesime_h{h}"]
        tm = entier(L[f"t_millesime_h{h}"])
        if tm != t - h:
            echec(4, f"{L['cible']} h{h} t_millesime={tm}")
        if code not in LISTE_FIGEE:
            echec(4, f"{L['cible']} h{h} code {code} hors liste")
        elif t_code(code) != tm:
            echec(4, f"{L['cible']} h{h} code {code} -> {t_code(code)} != {tm}")
        # 5
        mois = entier(L[f"mois_titre_h{h}"])
        at = entier(L[f"annee_titre_h{h}"])
        if code and code[0] in LETTRE_TRIM:
            if mois is None or mois != 3 * LETTRE_TRIM[code[0]]:
                echec(5, f"{L['cible']} h{h} {code} mois_titre={mois}")
            if at is None or at != annee_code(code):
                echec(5, f"{L['cible']} h{h} {code} annee_titre={at}")
        else:
            echec(5, f"{L['cible']} h{h} code illisible {code}")
        # 6
        if entier(L[f"t_premier_F_h{h}"]) != tm:
            echec(6, f"{L['cible']} h{h} premier F={L[f't_premier_F_h{h}']} != {tm}")
        # 7
        if not vide(L[f"projection_h{h}"]) and L[f"statut_h{h}"] != "F":
            echec(7, f"{L['cible']} h{h} statut={L[f'statut_h{h}']}")
        # 7 (contrôle complémentaire, implicite) : le trimestre de l'exercice précède la cible
        if tm is not None and not tm < t:
            echec(7, f"{L['cible']} h{h} exercice {tm} non antérieur à la cible {t}")

# 8. Valeurs
IND = ["indice_m1", "indice_m2", "indice_m3", "indice_an_avant_m1", "indice_an_avant_m2", "indice_an_avant_m3"]
for L in lignes:
    for c in ("projection_h2", "projection_h3"):
        s = L[c]
        if vide(s):
            continue
        x = float(s)
        if not (-5 <= x <= 15):
            echec(8, f"{L['cible']} {c}={s}")
        if not re.fullmatch(r"-?\d+(\.\d)?", s.strip()):  # au plus une décimale écrite
            echec(8, f"{L['cible']} {c}={s} plus d'une décimale")
        if abs(x * 10 - round(x * 10)) > 1e-9:
            echec(8, f"{L['cible']} {c}={s} pas un multiple de 0,1")
    for c in IND:
        x = f(L[c])
        if x is not None and not (20 <= x <= 300):
            echec(8, f"{L['cible']} {c}={x}")
    x = f(L["realise"])
    if x is not None and not (-5 <= x <= 15):
        echec(8, f"{L['cible']} realise={x}")

# 9. Réalisation
for L in lignes:
    v = [f(L[c]) for c in IND]
    a = f(L["realise"])
    if any(x is None for x in v):
        if a is not None:
            echec(9, f"{L['cible']} realise présente avec indice manquant")
    else:
        attendu = 100 * ((v[0] + v[1] + v[2]) / (v[3] + v[4] + v[5]) - 1)
        if a is None or abs(a - attendu) > 1e-6:
            echec(9, f"{L['cible']} realise={a} attendu={attendu}")

# 10. Révision et erreur
for L in lignes:
    p2, p3, a = f(L["projection_h2"]), f(L["projection_h3"]), f(L["realise"])
    r, e = f(L["revision"]), f(L["erreur"])
    if p2 is None or p3 is None:
        if r is not None:
            echec(10, f"{L['cible']} revision présente")
    elif r is None or abs(r - (p2 - p3)) > 1e-6:
        echec(10, f"{L['cible']} revision={r}")
    if a is None or p2 is None:
        if e is not None:
            echec(10, f"{L['cible']} erreur présente")
    elif e is None or abs(e - (a - p2)) > 1e-6:
        echec(10, f"{L['cible']} erreur={e}")

# 11. Cohérence entre lignes
par_t = {entier(L["t_cible"]): L for L in lignes}
for t, L in par_t.items():
    if t - 4 in par_t:
        L4 = par_t[t - 4]
        for k in (1, 2, 3):
            x, y = f(L[f"indice_an_avant_m{k}"]), f(L4[f"indice_m{k}"])
            if x is not None and y is not None and x != y:
                echec(11, f"{L['cible']} m{k} {x} != {y}")

n_violations_schema = sum(1 for k in controles if not controles[k])

# Contrôles hors liste (format, observés mais non comptés)
hors_liste = []
for L in lignes:
    for c, d in (("realise", 8), ("revision", 6), ("erreur", 6)):
        s = L[c]
        if not vide(s):
            dec = len(s.split(".")[1]) if "." in s else 0
            if dec < d:
                hors_liste.append(f"{L['cible']} {c} {dec} décimales < {d}")
# Cohérence des millésimes entre lignes : le millésime h2 de la cible t est le millésime h3 de t+1
for t, L in par_t.items():
    if t + 1 in par_t and par_t[t + 1]["millesime_h3"] != L["millesime_h2"]:
        hors_liste.append(f"{L['cible']} millésime h2 {L['millesime_h2']} != h3 de la cible suivante")
    if t_code(L["millesime_h2"]) - t_code(L["millesime_h3"]) != 1:
        hors_liste.append(f"{L['cible']} exercices non consécutifs")

# --------------------------------------------------------------------------------------------
# Statistiques
comp = [L for L in lignes if not vide(L["revision"]) and not vide(L["erreur"])]
comp.sort(key=lambda L: entier(L["t_cible"]))
T_ALL = np.array([entier(L["t_cible"]) for L in comp])
Y_ALL = np.array([entier(L["annee_cible"]) for L in comp])
R_ALL = np.array([float(L["revision"]) for L in comp])
E_ALL = np.array([float(L["erreur"]) for L in comp])


def pente(t, r, e, L=4, couples="t"):
    """Étapes 1 à 9. couples='t' : couples par écart de t_cible (lecture littérale de l'étape 5) ;
    couples='pos' : couples par écart de position (série mise bout à bout)."""
    n = len(r)
    out = dict(n=n, beta_z=0.0, et=0.0, t=0.0, s_r=0.0, s_e=0.0, beta_brut=0.0, et_brut=0.0)
    if n < 10:
        return out
    s_r, s_e = r.std(ddof=1), e.std(ddof=1)
    if s_r == 0 or s_e == 0:
        return out
    z = (r - r.mean()) / s_r
    y = (e - e.mean()) / s_e
    szz = (z * z).sum()
    b = (z * y).sum() / szz
    u = y - b * z
    v = z * u
    idx = t if couples == "t" else np.arange(n)
    S = (v * v).sum()
    for j in range(1, L + 1):
        g = 0.0
        for a_ in range(n):
            for b_ in range(n):
                if idx[a_] - idx[b_] == j:
                    g += v[a_] * v[b_]
        S += 2 * (1 - j / (L + 1)) * g
    et = math.sqrt(S) / szz
    out.update(beta_z=b, et=et, t=b / et, s_r=s_r, s_e=s_e,
               beta_brut=b * s_e / s_r, et_brut=et * s_e / s_r)
    return out


def pearson(r, e):
    if len(r) < 10 or r.std() == 0 or e.std() == 0:
        return 0.0
    return float(np.corrcoef(r, e)[0, 1])


P = pente(T_ALL, R_ALL, E_ALL, 4)
P8 = pente(T_ALL, R_ALL, E_ALL, 8)
n = P["n"]
lo, hi = P["beta_z"] - 1.645 * P["et"], P["beta_z"] + 1.645 * P["et"]
marge = min(-lo, hi - 0.40)

# Contrôle croisé statsmodels (aucune cible ne manque)
try:
    import statsmodels.api as sm
    z = (R_ALL - R_ALL.mean()) / R_ALL.std(ddof=1)
    yv = (E_ALL - E_ALL.mean()) / E_ALL.std(ddof=1)
    fit = sm.OLS(yv, sm.add_constant(z)).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})
    sm_check = dict(beta=float(fit.params[1]), et=float(fit.bse[1]))
except Exception as ex:  # pragma: no cover
    sm_check = dict(erreur=str(ex))

# Garde : deux années consécutives
gardes = {}
for Y in range(1999, 2026):
    m = ~np.isin(Y_ALL, [Y, Y + 1])
    gardes[Y] = pearson(R_ALL[m], E_ALL[m])
bmin2 = min(gardes.values())
annee_min = min(Y for Y, v in gardes.items() if v == bmin2)
conflit = 1 if (lo > 0 and hi >= 0.40 and bmin2 <= 0) else 0

# S1
m1 = T_ALL <= 8079
P1 = pente(T_ALL[m1], R_ALL[m1], E_ALL[m1], 4)

# S2 bootstrap
def bootstrap(r, e, B=9999, seed=20261112, bloc=8):
    nn = len(r)
    if nn < 10:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    k = math.ceil(nn / bloc)
    vals = []
    while len(vals) < B:
        debuts = rng.integers(0, nn - 7, size=k)
        idx = np.concatenate([np.arange(s, s + bloc) for s in debuts])[:nn]
        rb, eb = r[idx], e[idx]
        if np.all(rb == rb[0]) or np.all(eb == eb[0]):
            continue
        vals.append(np.corrcoef(rb, eb)[0, 1])
    vals = np.array(vals)
    return float(np.percentile(vals, 5)), float(np.percentile(vals, 95))


bb_lo, bb_hi = bootstrap(R_ALL, E_ALL)

# S3
m3 = ~((T_ALL >= 8084) & (T_ALL <= 8095))
P3 = pente(T_ALL[m3], R_ALL[m3], E_ALL[m3], 4, couples="t")
P3pos = pente(T_ALL[m3], R_ALL[m3], E_ALL[m3], 4, couples="pos")
sans_un = {Y: pearson(R_ALL[Y_ALL != Y], E_ALL[Y_ALL != Y]) for Y in range(1999, 2027)}
bmin1 = min(sans_un.values())

res = {
    "n_violations_schema": n_violations_schema,
    "n_cibles": n,
    "beta_z": P["beta_z"],
    "et_beta_z_nw4": P["et"],
    "t_nw4": P["t"],
    "borne_basse_ic90": lo,
    "borne_haute_ic90": hi,
    "marge_indecision": marge,
    "beta_z_min_sans_deux_ans": bmin2,
    "annee_debut_min": annee_min,
    "conflit_robustesse": conflit,
    "beta_brut": P["beta_brut"],
    "et_beta_brut_nw4": P["et_brut"],
    "ecart_type_revision": P["s_r"],
    "ecart_type_erreur": P["s_e"],
    "n_avant_2020": P1["n"],
    "beta_z_avant_2020": P1["beta_z"],
    "beta_brut_avant_2020": P1["beta_brut"],
    "et_beta_brut_avant_2020_nw4": P1["et_brut"],
    "et_beta_z_nw8": P8["et"],
    "bb_borne_basse_ic90": bb_lo,
    "bb_borne_haute_ic90": bb_hi,
    "n_hors_2021_2023": P3["n"],
    "beta_z_hors_2021_2023": P3["beta_z"],
    "et_beta_z_hors_2021_2023_nw4": P3["et"],
    "beta_z_min_sans_une_annee": bmin1,
}

with open(SORTIE, "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=2)

# Diagnostics à l'écran (non écrits dans verification.json)
if "--diag" in sys.argv:
    print("controles", controles)
    print("details", details)
    print("hors_liste", hors_liste)
    print("statsmodels", sm_check, "vs", P["beta_z"], P["et"])
    print("S3 couples par position : et =", P3pos["et"])
    print("S1 et_beta_z nw4 =", P1["et"], "t =", P1["t"])
    print("gardes", {k: round(v, 4) for k, v in gardes.items()})
    print("sans_une_annee", {k: round(v, 4) for k, v in sans_un.items()})
    print("corr hors 2021-2022 :", pearson(R_ALL[~np.isin(Y_ALL, [2021, 2022])], E_ALL[~np.isin(Y_ALL, [2021, 2022])]))
    for k, v in res.items():
        print(k, v)
