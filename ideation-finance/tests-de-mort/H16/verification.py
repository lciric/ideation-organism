"""Vérification indépendante H16 — écrite à partir du seul preenregistrement.md (§ 5, § 6)."""
import json, math, os, sys
from datetime import date, timedelta
import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ICI, "analyse_H16.csv")

COLS = ["rang", "date_reunion", "date_reunion_prec", "d_ois1y_pb", "sigma16_pb", "cible_norm",
        "cible_prec_norm", "act_eu_60j_pct", "brent_60j_pct", "eurusd_60j_pct", "us2a_60j_pp",
        "date_fin_act", "date_fin_brent", "date_fin_eurusd", "date_fin_us2a", "echantillon"]
PRED = ["act_eu_60j_pct", "brent_60j_pct", "eurusd_60j_pct", "us2a_60j_pp", "cible_prec_norm"]
DFIN = ["date_fin_act", "date_fin_brent", "date_fin_eurusd", "date_fin_us2a"]
NUM = ["d_ois1y_pb", "sigma16_pb", "cible_norm", "cible_prec_norm"] + PRED[:4]

raw = pd.read_csv(F, dtype=str, keep_default_na=False)
df = raw.copy()
vide = lambda v: v is None or (isinstance(v, str) and v.strip() == "")


def num(v):
    if vide(v):
        return np.nan
    try:
        return float(v)
    except ValueError:
        return np.nan


def dt(v):
    if vide(v):
        return None
    try:
        return date.fromisoformat(v.strip())
    except ValueError:
        return None


N = len(df)
for c in NUM:
    if c in df.columns:
        df[c + "_f"] = [num(v) for v in df[c]]

echecs = {}
notes = {}

# 1
echecs[1] = not (N == 315 and list(raw.columns) == COLS)

# 2
ok = True
try:
    rang = [int(v) for v in df["rang"]]
    ok &= rang == list(range(1, N + 1))
except Exception:
    ok = False
d = [dt(v) for v in df["date_reunion"]]
ok &= all(x is not None for x in d)
if ok:
    ok &= all(d[i] > d[i - 1] for i in range(1, N))
    rep = {1: date(1999, 1, 7), 168: date(2009, 12, 3), 169: date(2010, 1, 14), 315: date(2025, 10, 30)}
    ok &= all(N >= k and d[k - 1] == v for k, v in rep.items())
echecs[2] = not ok

# 3
ok = vide(df["date_reunion_prec"].iloc[0])
for i in range(1, N):
    ok &= df["date_reunion_prec"].iloc[i].strip() == df["date_reunion"].iloc[i - 1].strip()
echecs[3] = not ok

# 4
x = df["d_ois1y_pb_f"].values
echecs[4] = not (np.all(np.isfinite(x)) and np.all(np.abs(x) < 100))

# 5
ok = True
sig = df["sigma16_pb_f"].values
for i in range(N):
    r = i + 1
    if r <= 16:
        ok &= vide(df["sigma16_pb"].iloc[i])
    else:
        s = np.std(x[i - 16:i], ddof=1)
        ok &= bool(np.isfinite(sig[i]) and abs(sig[i] - max(s, 0.25)) <= 1e-6)
echecs[5] = not ok
n_plancher = int(sum(1 for i in range(16, N) if np.std(x[i - 16:i], ddof=1) < 0.25))

# 6
ok = True
cn = df["cible_norm_f"].values
for i in range(N):
    if i + 1 <= 16:
        ok &= vide(df["cible_norm"].iloc[i])
    else:
        ok &= bool(np.isfinite(cn[i]) and abs(cn[i] - x[i] / sig[i]) <= 1e-6)
echecs[6] = not ok

# 7
ok = True
cp = df["cible_prec_norm_f"].values
for i in range(N):
    if i + 1 <= 17:
        ok &= vide(df["cible_prec_norm"].iloc[i])
    else:
        ok &= bool(np.isfinite(cp[i]) and abs(cp[i] - cn[i - 1]) <= 1e-6)
echecs[7] = not ok

# 8
ok = True
ech = df["echantillon"].str.strip().values
viol8 = []
for i in range(N):
    for c in DFIN:
        v = df[c].iloc[i]
        if not vide(v):
            dv = dt(v)
            if dv is None or not (dv < d[i] and (d[i] - dv).days <= 10):
                ok = False
                viol8.append((i + 1, c, v))
        elif ech[i] in ("estimation", "evaluation"):
            ok = False
            viol8.append((i + 1, c, "vide"))
echecs[8] = not ok

# 9
BORNES = {"act_eu_60j_pct": 100, "brent_60j_pct": 300, "eurusd_60j_pct": 50, "us2a_60j_pp": 5}
ok = True
for i in range(N):
    if ech[i] in ("estimation", "evaluation"):
        for c in PRED + ["cible_norm"]:
            v = df[c + "_f"].iloc[i]
            ok &= bool(np.isfinite(v))
            if c in BORNES:
                ok &= bool(abs(v) < BORNES[c])
echecs[9] = not ok

# 10
ok = True
for i in range(N):
    r = i + 1
    if r <= 17:
        att = "rodage"
    elif any(not np.isfinite(df[c + "_f"].iloc[i]) for c in PRED + ["cible_norm"]):
        att = "exclue"
    elif d[i] <= date(2009, 12, 3):
        att = "estimation"
    else:
        att = "evaluation"
    ok &= ech[i] == att
echecs[10] = not ok

violations = int(sum(echecs.values()))

# ---- § 6.1 prévisions récursives
util = np.isin(ech, ["estimation", "evaluation"])
Y = cn
X = np.column_stack([np.ones(N)] + [df[c + "_f"].values for c in PRED])
dates = np.array(d)
idx_eval = [i for i in range(N) if ech[i] == "evaluation"]
n_estim = int(np.sum(ech == "estimation"))
P = len(idx_eval)
e0, e1, dd, taille = [], [], [], []
for t in idx_eval:
    A = [j for j in range(N) if util[j] and dates[j] < dates[t]]
    taille.append(len(A))
    m = Y[A].mean()
    b, *_ = np.linalg.lstsq(X[A], Y[A], rcond=None)
    p = X[t] @ b
    e0.append(Y[t] - m); e1.append(Y[t] - p); dd.append(p - m)
e0, e1, dd = map(np.array, (e0, e1, dd))

r2 = 1 - np.sum(e1 ** 2) / np.sum(e0 ** 2)
f = e0 ** 2 - e1 ** 2 + dd ** 2
assert np.allclose(f, 2 * e0 * dd)


def cw(fv):
    fb = fv.mean()
    se = math.sqrt(np.sum((fv - fb) ** 2) / (len(fv) - 1)) / math.sqrt(len(fv))
    return fb, se, fb / se


fbar, se, t = cw(f)
loo = np.array([cw(np.delete(f, k))[2] for k in range(P)])
tmin = float(loo.min())
zone = int(t >= 1.282 and not (r2 > 0 and t >= 1.645 and tmin >= 1.282))

out = {"n_eval": P, "n_estim_init": n_estim, "r2_oos": float(r2), "cw_fbar": float(fbar),
       "cw_se": float(se), "cw_t": float(t), "cw_t_min_sans_une": tmin, "zone_grise": zone,
       "violations_schema": violations}
with open(os.path.join(ICI, "verification.json"), "w") as fh:
    json.dump(out, fh, indent=2)

# ---- diagnostics (rapport)
print(json.dumps(out, indent=2))
print("échecs par contrôle:", echecs)
print("viol8 (10 premiers):", viol8[:10], "n=", len(viol8))
print("taille A_t première/dernière:", taille[0], taille[-1])
print("plancher sigma joue (rangs >=17):", n_plancher)
print("doublons de dates:", pd.Series(df["date_reunion"]).duplicated().sum())
ordre = np.argsort(-f)
print("plus fortes contributions f_t (date, f_t, part de Σf, y, p-m, cw_t sans):")
for k in ordre[:8]:
    i = idx_eval[k]
    print(" ", df["date_reunion"].iloc[i], round(f[k], 4), round(f[k] / f.sum(), 3), round(Y[i], 3), round(dd[k], 3), round(loo[k], 3))
print("plus négatives:")
for k in ordre[-5:]:
    i = idx_eval[k]
    print(" ", df["date_reunion"].iloc[i], round(f[k], 4), round(Y[i], 3), round(dd[k], 3))
print("Σ e0², Σ e1², Σ f:", np.sum(e0 ** 2), np.sum(e1 ** 2), f.sum())
print("|cible_norm| max (util):", np.nanmax(np.abs(Y[util])), df["date_reunion"].iloc[int(np.nanargmax(np.where(util, np.abs(Y), -1)))])
print("|d_ois| max:", np.max(np.abs(x)), df["date_reunion"].iloc[int(np.argmax(np.abs(x)))])
desc = df.loc[util, [c + "_f" for c in PRED[:4]] + ["cible_norm_f", "sigma16_pb_f", "d_ois1y_pb_f"]].describe().T
print(desc[["min", "max", "mean", "std"]])
# rodage: valeurs manquantes dans prédicteurs
print("cellules vides rodage préd. marché:", int((df.loc[:16, PRED[:4]] == "").sum().sum()))
# écart date_fin vs date (jours) dist
gaps = [(d[i] - dt(df[c].iloc[i])).days for i in range(N) if util[i] for c in DFIN]
print("écarts jours date_fin -> réunion: min", min(gaps), "max", max(gaps))
print("zéros exacts d_ois:", int(np.sum(x == 0)))
