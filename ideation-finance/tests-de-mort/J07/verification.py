"""Verification independante de J07, ecrite d'apres preenregistrement.md seul.

Lit uniquement J07_analyse.csv. Ecrit verification.json (8 champs) et imprime
les controles de schema, les verifications d'anteriorite et les analyses de fragilite.
"""
import csv
import json
import math
import sys
from datetime import date
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
FICHIER = ICI / "J07_analyse.csv"

COLONNES = [
    "date_publication", "mois_reference", "n_mois_nouveaux", "date_millesime_precedent",
    "date_millesime_3e", "date_info_predicteurs", "emploi_1re_k", "emploi_3e_k", "rev_m1_k",
    "rev_m2_k", "tendance_12m_k", "revision_large", "extreme", "complet", "admissible",
    "cible_N_k", "pred_ecart_tendance_k", "pred_somme_revisions_k",
]
ENTIERS = ["n_mois_nouveaux", "emploi_1re_k", "emploi_3e_k", "rev_m1_k", "rev_m2_k",
           "revision_large", "extreme", "complet", "admissible", "cible_N_k",
           "pred_somme_revisions_k"]
DECIMAUX = ["tendance_12m_k", "pred_ecart_tendance_k"]
DATES = ["date_publication", "date_millesime_precedent", "date_millesime_3e", "date_info_predicteurs"]

echecs = []      # violations des controles numerotes 1 a 8
remarques = []   # autres constats (hors controles numerotes)


def echec(n, msg):
    echecs.append(f"controle {n}: {msg}")


def lire_date(s):
    if len(s) != 10 or s[4] != "-" or s[7] != "-":
        raise ValueError(s)
    return date(int(s[:4]), int(s[5:7]), int(s[8:]))


def lire_entier(s):
    # entier ecrit sans partie decimale
    s2 = s[1:] if s.startswith("-") else s
    if not s2.isdigit():
        raise ValueError(s)
    return int(s)


# ---------------------------------------------------------------- lecture brute
with open(FICHIER, newline="", encoding="utf-8") as fh:
    lecteur = csv.reader(fh)
    entete = next(lecteur)
    brut = [ligne for ligne in lecteur]

# controle 1
if entete != COLONNES:
    echec(1, f"en-tete different: {entete}")

lignes = []
for k, r in enumerate(brut):
    if len(r) != len(COLONNES):
        echec(1, f"ligne {k+2}: {len(r)} champs")
        continue
    d = dict(zip(COLONNES, r))
    v = {}
    for c in COLONNES:
        s = d[c]
        if s == "":
            v[c] = None
            continue
        try:
            if c in DATES:
                v[c] = lire_date(s)
            elif c == "mois_reference":
                if len(s) != 7 or s[4] != "-":
                    raise ValueError(s)
                v[c] = (int(s[:4]), int(s[5:]))
            elif c in ENTIERS:
                v[c] = lire_entier(s)
            else:
                v[c] = float(s)
        except ValueError:
            echec(1, f"ligne {k+2}, colonne {c}: valeur mal typee {s!r}")
            v[c] = None
    lignes.append(v)

n = len(lignes)

# champs obligatoires (jamais vides d'apres la definition)
OBLIG = ["date_publication", "mois_reference", "n_mois_nouveaux", "date_millesime_precedent",
         "date_info_predicteurs", "emploi_1re_k", "revision_large", "extreme", "complet",
         "admissible"]
for k, v in enumerate(lignes):
    for c in OBLIG:
        if v[c] is None:
            echec(1, f"ligne {k+2}: {c} vide")

# controle 2
if not (425 <= n <= 435):
    echec(2, f"{n} lignes")
dp = [v["date_publication"] for v in lignes]
if len(set(dp)) != n:
    echec(2, "date_publication non unique")
for k in range(1, n):
    if not dp[k] > dp[k - 1]:
        echec(2, f"date_publication non strictement croissante en {dp[k]}")
for d_ in dp:
    if not (date(1990, 1, 1) <= d_ <= date(2025, 12, 31)):
        echec(2, f"date_publication hors periode {d_}")

# controle 3
mr = [v["mois_reference"] for v in lignes]
for k in range(1, n):
    if not mr[k] > mr[k - 1]:
        echec(3, f"mois_reference non strictement croissant en {mr[k]}")
for v in lignes:
    ecart = (v["date_publication"] - date(v["mois_reference"][0], v["mois_reference"][1], 1)).days
    if not (28 <= ecart <= 110):
        echec(3, f"{v['date_publication']}: ecart {ecart} jours")

# controle 4
nb2 = 0
for v in lignes:
    if v["n_mois_nouveaux"] not in (1, 2):
        echec(4, f"{v['date_publication']}: n_mois_nouveaux={v['n_mois_nouveaux']}")
    nb2 += v["n_mois_nouveaux"] == 2
    for c in ("revision_large", "extreme", "complet", "admissible"):
        if v[c] not in (0, 1):
            echec(4, f"{v['date_publication']}: {c}={v[c]}")
if nb2 > 2:
    echec(4, f"{nb2} lignes a n_mois_nouveaux=2")

# controle 5
FIN_D2 = date(2026, 3, 31)
for v in lignes:
    p = v["date_publication"]
    if not v["date_millesime_precedent"] < p:
        echec(5, f"{p}: date_millesime_precedent {v['date_millesime_precedent']} >= publication")
    if not v["date_info_predicteurs"] <= p:
        echec(5, f"{p}: date_info_predicteurs {v['date_info_predicteurs']} > publication")
    d3 = v["date_millesime_3e"]
    if d3 is not None and not (d3 > p and d3 <= FIN_D2):
        echec(5, f"{p}: date_millesime_3e {d3} hors bornes")

# controle 6
for v in lignes:
    p = v["date_publication"]
    a1, a3 = v["emploi_1re_k"], v["emploi_3e_k"]
    attendu_N = None if a3 is None else a1 - a3
    if v["cible_N_k"] != attendu_N:
        echec(6, f"{p}: cible_N_k={v['cible_N_k']} attendu {attendu_N}")
    attendu_x1 = None if v["tendance_12m_k"] is None else a1 - v["tendance_12m_k"]
    if v["pred_ecart_tendance_k"] != attendu_x1:
        echec(6, f"{p}: pred_ecart_tendance_k={v['pred_ecart_tendance_k']} attendu {attendu_x1}")
    attendu_x2 = (None if v["rev_m1_k"] is None or v["rev_m2_k"] is None
                  else v["rev_m1_k"] + v["rev_m2_k"])
    if v["pred_somme_revisions_k"] != attendu_x2:
        echec(6, f"{p}: pred_somme_revisions_k={v['pred_somme_revisions_k']} attendu {attendu_x2}")
    ext = int(abs(a1) > 1000 or (a3 is not None and abs(a1 - a3) > 500))
    if v["extreme"] != ext:
        echec(6, f"{p}: extreme={v['extreme']} attendu {ext}")
    comp = int(all(v[c] is not None for c in ("emploi_3e_k", "rev_m1_k", "rev_m2_k", "tendance_12m_k")))
    if v["complet"] != comp:
        echec(6, f"{p}: complet={v['complet']} attendu {comp}")
    adm = int(v["complet"] == 1 and v["n_mois_nouveaux"] == 1
              and v["revision_large"] == 0 and v["extreme"] == 0)
    if v["admissible"] != adm:
        echec(6, f"{p}: admissible={v['admissible']} attendu {adm}")

# controle 7
for v in lignes:
    for c in ("emploi_1re_k", "tendance_12m_k", "rev_m1_k", "rev_m2_k"):
        if v[c] is not None and abs(v[c]) > 25000:
            echec(7, f"{v['date_publication']}: |{c}| > 25000")

# controle 8
l8 = [v for v in lignes if v["date_publication"] == date(1990, 2, 2)]
if len(l8) != 1:
    echec(8, "ligne du 1990-02-02 absente")
else:
    v = l8[0]
    if not (v["mois_reference"] == (1990, 1) and v["emploi_1re_k"] == 275
            and v["date_millesime_3e"] == date(1990, 4, 6) and v["emploi_3e_k"] == 361
            and v["cible_N_k"] == -86):
        echec(8, f"ligne du 1990-02-02 differente: {v}")

schema_ok = int(len(echecs) == 0)

# ------------------------------------- coherences supplementaires (hors controles 1-8)
def mois_plus(m, k):
    t = m[0] * 12 + (m[1] - 1) + k
    return (t // 12, t % 12 + 1)


for k, v in enumerate(lignes):
    p = v["date_publication"]
    # prec(v) doit etre la publication precedente du fichier
    if k > 0 and v["date_millesime_precedent"] != lignes[k - 1]["date_publication"]:
        remarques.append(f"{p}: date_millesime_precedent {v['date_millesime_precedent']} "
                         f"!= publication precedente {lignes[k-1]['date_publication']}")
    # n_mois_nouveaux = ecart de mois avec la ligne precedente
    if k > 0:
        ecart_m = (mr[k][0] * 12 + mr[k][1]) - (mr[k - 1][0] * 12 + mr[k - 1][1])
        if ecart_m != v["n_mois_nouveaux"]:
            remarques.append(f"{p}: n_mois_nouveaux={v['n_mois_nouveaux']} mais ecart de mois {ecart_m}")
    # v3 = premiere publication w > v avec fin(w) >= m+2 (verifiable si w est dans le fichier)
    cible = mois_plus(v["mois_reference"], 2)
    cand = [w for w in lignes[k + 1:] if w["mois_reference"] >= cible]
    if cand:
        if v["date_millesime_3e"] != cand[0]["date_publication"]:
            remarques.append(f"{p}: date_millesime_3e {v['date_millesime_3e']} != "
                             f"publication de fin >= m+2 dans le fichier {cand[0]['date_publication']}")
    elif v["date_millesime_3e"] is not None and v["date_millesime_3e"] <= date(2025, 12, 31):
        remarques.append(f"{p}: date_millesime_3e {v['date_millesime_3e']} en 2025 mais absente du fichier")
    # predicteurs : tous lus dans v ou prec(v) => date_info_predicteurs attendue = date_publication
    if v["date_info_predicteurs"] != p:
        remarques.append(f"{p}: date_info_predicteurs {v['date_info_predicteurs']} != date_publication")
    if v["date_info_predicteurs"] < v["date_millesime_precedent"]:
        remarques.append(f"{p}: date_info_predicteurs anterieure au millesime precedent")
    # T multiple de 0,5
    if v["tendance_12m_k"] is not None and (v["tendance_12m_k"] * 2) != round(v["tendance_12m_k"] * 2):
        remarques.append(f"{p}: tendance_12m_k {v['tendance_12m_k']} pas multiple de 0,5")
    # emploi_3e vide ssi date_millesime_3e vide
    if (v["emploi_3e_k"] is None) != (v["date_millesime_3e"] is None):
        remarques.append(f"{p}: emploi_3e_k et date_millesime_3e pas vides ensemble")
    # R1 = Delta(m';v) - Delta(m';prec(v)) ; R2 sur m'-1. Pour v+1, rev de m = Delta(m;v+1) - A1(v).
    # Coherence partielle: A1(v) + R1(v+1) = 2e estimation de m ; A1(v) + R1(v+1) + R2(v+2) = A3(v)
    if k + 2 < n and v["n_mois_nouveaux"] == 1:
        w1, w2 = lignes[k + 1], lignes[k + 2]
        if (w1["n_mois_nouveaux"] == 1 and w2["n_mois_nouveaux"] == 1
                and v["emploi_3e_k"] is not None and w1["rev_m1_k"] is not None
                and w2["rev_m2_k"] is not None):
            a3_reconstruit = v["emploi_1re_k"] + w1["rev_m1_k"] + w2["rev_m2_k"]
            if a3_reconstruit != v["emploi_3e_k"]:
                remarques.append(f"{p}: A1 + R1(suivante) + R2(suivante+1) = {a3_reconstruit} "
                                 f"!= emploi_3e_k {v['emploi_3e_k']}")

# ------------------------------------------------------------- statistique
A = [v for v in lignes if v["admissible"] == 1]
A.sort(key=lambda v: v["date_publication"])
n_adm = len(A)
y = np.array([v["cible_N_k"] for v in A], dtype=float)
x1 = np.array([v["pred_ecart_tendance_k"] for v in A], dtype=float)
x2 = np.array([v["pred_somme_revisions_k"] for v in A], dtype=float)
d = [v["date_publication"] for v in A]
d3 = [v["date_millesime_3e"] for v in A]


def previsions(y, X, d, d3, minimum=60):
    """Renvoie indices prevus, yhat0, yhat1, tailles d'apprentissage, et controle d'anteriorite."""
    idx, f0, f1, tailles = [], [], [], []
    for i in range(len(y)):
        S = [j for j in range(len(y)) if d3[j] <= d[i]]
        # anteriorite : toute ligne d'apprentissage est anterieure et deja connue
        assert all(j < i for j in S), "ligne d'apprentissage posterieure"
        assert all(d3[j] <= d[i] for j in S)
        if len(S) < minimum:
            continue
        S = np.array(S)
        Xs = X[S]
        b, *_ = np.linalg.lstsq(Xs, y[S], rcond=None)
        idx.append(i)
        f1.append(float(X[i] @ b))
        f0.append(float(y[S].mean()))
        tailles.append(len(S))
    return np.array(idx), np.array(f0), np.array(f1), np.array(tailles)


def cw(yv, f0, f1, L=4):
    e0, e1 = yv - f0, yv - f1
    f = e0 ** 2 - (e1 ** 2 - (f0 - f1) ** 2)
    P = len(f)
    fb = f.mean()
    u = f - fb
    g = [np.sum(u[l:] * u[:P - l]) / P for l in range(L + 1)]
    om = g[0] + 2 * sum((1 - l / (L + 1)) * g[l] for l in range(1, L + 1))
    return fb / math.sqrt(om / P), f


def r2oos(yv, f0, f1):
    return 1 - np.sum((yv - f1) ** 2) / np.sum((yv - f0) ** 2)


X = np.column_stack([np.ones(n_adm), x1, x2])
idx, yh0, yh1, tailles = previsions(y, X, d, d3)
P = len(idx)
yE = y[idx]
cw_stat, f = cw(yE, yh0, yh1)
r2 = r2oos(yE, yh0, yh1)
reqm0 = math.sqrt(np.mean((yE - yh0) ** 2))
reqm1 = math.sqrt(np.mean((yE - yh1) ** 2))
premiere = d[idx[0]]
premiere_int = premiere.year * 10000 + premiere.month * 100 + premiere.day

# verification croisee statsmodels
import statsmodels.api as sm
res = sm.OLS(f, np.ones(P)).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})
cw_sm = float(res.tvalues[0])
# identite algebrique f = 2 (yh1 - yh0)(y - yh0)
f_alt = 2 * (yh1 - yh0) * (yE - yh0)

sortie = {
    "schema_ok": schema_ok,
    "n_admissibles": n_adm,
    "n_previsions": P,
    "premiere_prevision_aaaammjj": premiere_int,
    "cw_stat": round(float(cw_stat), 6),
    "r2_hors_echantillon": round(float(r2), 8),
    "reqm_reference_k": round(reqm0, 6),
    "reqm_modele_k": round(reqm1, 6),
}
(ICI / "verification.json").write_text(json.dumps(sortie, indent=2) + "\n", encoding="utf-8")

# ------------------------------------------------------------ diagnostics
print("=== verification.json ===")
print(json.dumps(sortie, indent=2))
print(f"\nlignes={n}, schema: {len(echecs)} echec(s)")
for e in echecs[:50]:
    print("  ", e)
print(f"remarques hors controles numerotes: {len(remarques)}")
for e in remarques[:60]:
    print("  ", e)
print(f"\ncw statsmodels={cw_sm:.6f}  ecart max identite f={np.max(np.abs(f - f_alt)):.2e}")
print(f"taille apprentissage: premiere {tailles[0]}, derniere {tailles[-1]}")
print(f"non admissibles: complet=0 {sum(v['complet']==0 for v in lignes)}, "
      f"n_mois=2 {sum(v['n_mois_nouveaux']==2 for v in lignes)}, "
      f"revision_large=1 {sum(v['revision_large']==1 for v in lignes)}, "
      f"extreme=1 {sum(v['extreme']==1 for v in lignes)}")
print("dates extreme=1:", [str(v["date_publication"]) for v in lignes if v["extreme"] == 1])
print(f"moyenne y={y.mean():.3f} ecart-type={y.std(ddof=1):.3f}")

# ecart minimal entre d3 et d dans A (le decalage d'apprentissage)
dec = []
for i in range(n_adm):
    S_avant = [j for j in range(i) if d3[j] > d[i]]
    dec.append(len(S_avant))
print("lignes anterieures exclues de S_i (troisieme estimation pas encore publiee): "
      f"min={min(dec[60:])} max={max(dec)}")
egal = sum(1 for i in range(n_adm) for j in range(i) if d3[j] == d[i])
print(f"paires (j,i) avec d3_j == d_i (jour meme, admis par B5): {egal}")

# S1
for nom, Xs in (("x1 seul", np.column_stack([np.ones(n_adm), x1])),
                ("x2 seul", np.column_stack([np.ones(n_adm), x2]))):
    ii, a0, a1_, _ = previsions(y, Xs, d, d3)
    assert np.array_equal(ii, idx)
    c, _ = cw(y[ii], a0, a1_)
    print(f"S1 {nom}: CW={c:.4f} R2oos={r2oos(y[ii], a0, a1_):.5f}")

# S2 et decennies (previsions inchangees)
dE = [d[i] for i in idx]


def sous(masque, etiquette):
    m = np.array(masque)
    if m.sum() < 10:
        print(f"{etiquette}: {m.sum()} prevision(s), trop peu")
        return
    c, _ = cw(yE[m], yh0[m], yh1[m])
    print(f"{etiquette}: P={m.sum()} CW={c:.4f} R2oos={r2oos(yE[m], yh0[m], yh1[m]):.5f}")


sous([x < date(2008, 1, 1) for x in dE], "S2 <2008")
sous([date(2008, 1, 1) <= x <= date(2019, 12, 31) for x in dE], "S2 2008-2019")
sous([x >= date(2020, 1, 1) for x in dE], "S2 >=2020")
for dec0 in (1990, 2000, 2010, 2020):
    sous([dec0 <= x.year < dec0 + 10 for x in dE], f"decennie {dec0}s")

# fragilite : cinq publications les plus influentes (|f_i| le plus grand)
ordre = np.argsort(-np.abs(f))[:5]
print("\nfragilite (5 plus grands |f_i|):")
for r in ordre:
    i_A = idx[r]
    # (a) retrait de l'evaluation seulement
    m = np.ones(P, bool)
    m[r] = False
    c_a, _ = cw(yE[m], yh0[m], yh1[m])
    r2_a = r2oos(yE[m], yh0[m], yh1[m])
    # (b) retrait complet de A (apprentissage et evaluation), tout recalcule
    garder = [j for j in range(n_adm) if j != i_A]
    ii, b0, b1, _ = previsions(y[garder], X[garder], [d[j] for j in garder], [d3[j] for j in garder])
    c_b, _ = cw(y[garder][ii], b0, b1)
    r2_b = r2oos(y[garder][ii], b0, b1)
    print(f"  {d[i_A]} y={y[i_A]:.0f} f={f[r]:.1f}: sans (eval) CW={c_a:.4f} R2={r2_a:.5f} | "
          f"sans (tout, P={len(ii)}) CW={c_b:.4f} R2={r2_b:.5f}")

# variante : lignes a n_mois_nouveaux=2 ou complet=0 dans le fichier (aucune autre lecture possible)
sys.exit(0)
