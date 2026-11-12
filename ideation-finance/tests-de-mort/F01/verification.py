"""F01 - vérificateur indépendant. Recalcule les champs_verification du préenregistrement à partir de panel.csv seul."""
import json, re, sys
import numpy as np
import pandas as pd
import scipy.sparse as sp

ICI = "/home/user/ideation-organism/ideation-finance/tests-de-mort/F01/"
COLS = ["signal", "date", "annee", "ret", "annee_pub", "annee_debut_ech", "annee_fin_ech",
        "statut", "dans_fenetre", "moy_origine"]

raw = pd.read_csv(ICI + "panel.csv", dtype=str, keep_default_na=False)
diag = {}

# ---------------- contrôles de schéma ----------------
echecs = []
# 1
c1 = list(raw.columns) == COLS
echecs.append(not c1)
df = raw.copy()
num = lambda s: pd.to_numeric(s.replace("", np.nan), errors="coerce")
df["annee"] = num(raw["annee"]); df["ret"] = num(raw["ret"])
for c in ["annee_pub", "annee_debut_ech", "annee_fin_ech", "dans_fenetre"]:
    df[c] = num(raw[c])
df["moy_origine"] = num(raw["moy_origine"])
# 2
dup = df.duplicated(["signal", "date"]).sum(); diag["doublons_signal_date"] = int(dup)
echecs.append(dup > 0)
# 3
nsig = df["signal"].nunique(); diag["n_signaux"] = int(nsig)
echecs.append(nsig > 212)
# 4
fmt = raw["date"].str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])")
an_ok = raw["annee"] == raw["date"].str[:4]
c4 = fmt.all() and an_ok.all() and df["annee"].between(1926, 2025).all()
echecs.append(not c4)
# 5
fin = np.isfinite(df["ret"]).all()
med = float(np.nanmedian(np.abs(df["ret"]))); diag["mediane_abs_ret"] = med
echecs.append(not (fin and 0.5 <= med <= 10))
# 6
g = df.groupby("signal")
const = all(g[c].nunique(dropna=False).max() == 1 for c in ["annee_pub", "annee_debut_ech", "annee_fin_ech"])
P, D, F = df["annee_pub"], df["annee_debut_ech"], df["annee_fin_ech"]
ordre = ((D <= F) & (F < P) & P.between(1973, 2016)).all()
echecs.append(not (const and ordre))
# 7
a = df["annee"]
st = np.select([a < D, (a >= D) & (a <= F), (a > F) & (a < P), a == P, (a >= P + 1) & (a <= P + 5), a > P + 5],
               ["avant", "origine", "attente", "annee_pub", "publie", "apres"], default="?")
n_st = int((df["statut"] != st).sum()); diag["statut_faux"] = n_st
echecs.append(n_st > 0)
# 8
dfen = ((a >= 1974) & (a <= 2013)).astype(int)
n_fen = int((df["dans_fenetre"] != dfen).sum()); diag["dans_fenetre_faux"] = n_fen
echecs.append(n_fen > 0)
# 9 (statut recalculé utilisé pour la moyenne)
mo = df.assign(st=st)[st == "origine"].groupby("signal")["ret"].mean()
attendu = df["signal"].map(mo)
const9 = g["moy_origine"].nunique(dropna=False).max() == 1
both_nan = attendu.isna() & df["moy_origine"].isna()
ok9 = both_nan | (np.abs(attendu - df["moy_origine"]) <= 1e-8)
n9 = int((~ok9).sum()); diag["moy_origine_faux"] = n9
echecs.append(not (const9 and n9 == 0))

# ---------------- échantillons ----------------
n_orig = df[df["statut"] == "origine"].groupby("signal").size()
K = set(n_orig[n_orig >= 60].index)
diag["K"] = len(K); diag["exclus_moins_60_origine"] = sorted(set(df["signal"]) - K)
fen = df["dans_fenetre"] == 1
U0 = df[fen & df["statut"].isin(["origine", "attente"]) & df["signal"].isin(K)].copy()
P0 = df[fen & (df["statut"] == "publie")].copy()


def ols(U, avance=False):
    """MCO sur U : a[i] + l[t] (premier mois omis) + b*att (+ d*av). Retourne coefficients et index."""
    sig = pd.Categorical(U["signal"]); mois = pd.Categorical(U["date"])
    n = len(U); ni = len(sig.categories); nt = len(mois.categories)
    rows = np.arange(n)
    A = sp.csr_matrix((np.ones(n), (rows, sig.codes)), shape=(n, ni))
    mc = mois.codes
    keep = mc > 0  # omettre le premier mois (ordre AAAA-MM = ordre chronologique)
    L = sp.csr_matrix((np.ones(keep.sum()), (rows[keep], mc[keep] - 1)), shape=(n, nt - 1))
    att = (U["statut"] == "attente").to_numpy(float)
    extra = [att]
    if avance:
        extra.append(((U["statut"] == "attente") & (U["annee"] == U["annee_pub"] - 1)).to_numpy(float))
    X = sp.hstack([A, L, sp.csr_matrix(np.column_stack(extra))]).tocsc()
    y = U["ret"].to_numpy(float)
    XtX = (X.T @ X).toarray(); Xty = X.T @ y
    coef = np.linalg.solve(XtX, Xty)
    ahat = pd.Series(coef[:ni], index=sig.categories)
    lhat = pd.Series(np.r_[0.0, coef[ni:ni + nt - 1]], index=mois.categories)
    return ahat, lhat, coef[ni + nt - 1:], X


def theta_de(U, Pp):
    ahat, lhat, bb, _ = ols(U)
    T = Pp[Pp["signal"].isin(set(U["signal"])) & Pp["date"].isin(set(U["date"]))]
    tau = T["ret"].to_numpy() - (T["signal"].map(ahat).to_numpy() + T["date"].map(lhat).to_numpy() + bb[0])
    tb = tau.mean(); mb = T["moy_origine"].mean()
    return tb / mb, tb, mb, bb[0], T


theta, tau_bar, m_bar, b_att, T = theta_de(U0, P0)

# 10 identifiabilité : rang colonne sur l'échantillon complet
_, _, _, X = ols(U0)
rang = np.linalg.matrix_rank(X.toarray())
diag["rang"] = int(rang); diag["colonnes"] = int(X.shape[1])
echecs.append(rang < X.shape[1])

# garde
_, _, cd, _ = ols(U0, avance=True)
d_hat = cd[1]

# ---------------- jackknife ----------------
annees = [y for y in range(1974, 2014) if ((U0["annee"] == y).any() or (T["annee"] == y).any())]
G = len(annees)
th_g, d_g = [], []
for y in annees:
    Ug = U0[U0["annee"] != y]; Pg = P0[P0["annee"] != y]
    th_g.append(theta_de(Ug, Pg)[0])
    d_g.append(ols(Ug, avance=True)[2][1])
th_g = np.array(th_g); d_g = np.array(d_g)
se_theta = float(np.sqrt((G - 1) / G * ((th_g - th_g.mean()) ** 2).sum()))
se_d = float(np.sqrt((G - 1) / G * ((d_g - d_g.mean()) ** 2).sum()))
bb_ = theta - 2.12 * se_theta; bh_ = theta + 2.12 * se_theta

out = {
    "theta": float(theta), "se_theta": se_theta,
    "borne_basse_ic95": float(bb_), "borne_haute_ic95": float(bh_),
    "marge_ambiguite": float(min(bh_, -0.30 - bb_)),
    "tau_bar": float(tau_bar), "m_bar": float(m_bar), "b_attente": float(b_att),
    "t_avance": float(d_hat / se_d),
    "n_lignes_traitees": int(len(T)), "n_anomalies_traitees": int(T["signal"].nunique()),
    "n_lignes_attente": int((U0["statut"] == "attente").sum()),
    "n_blocs": int(G), "n_violations_schema": int(sum(bool(e) for e in echecs)),
}
json.dump(out, open(ICI + "verification.json", "w"), indent=2)

# diagnostics (non écrits dans verification.json)
diag.update(echecs=[i + 1 for i, e in enumerate(echecs) if e], d_hat=float(d_hat), se_d=se_d,
            theta_point=float(th_g.mean()), n_U=len(U0), n_origine_U=int((U0["statut"] == "origine").sum()),
            n_anom_U=int(U0["signal"].nunique()))
diag["theta_g"] = {y: round(float(v), 4) for y, v in zip(annees, th_g)}
diag["T_par_annee"] = T.groupby("annee").size().to_dict()
print(json.dumps(out, indent=2)); print(json.dumps(diag, indent=1, default=str))
