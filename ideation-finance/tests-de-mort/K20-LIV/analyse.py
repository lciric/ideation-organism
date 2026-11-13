"""K20-LIV : calcule temoin.json depuis K20-LIV_analyse.csv seul (préinscription, section 6). N'écrit aucun verdict."""
import sys, pathlib, json
import numpy as np, pandas as pd
R = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(R))
from controles import VARS, EPISODES, controles, n_violations
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

df = pd.read_csv(R / "K20-LIV_analyse.csv", dtype={"episode": str})
viol, anom = controles(df)
T = {"n_violations_schema": int(n_violations(viol))}
P = df[df.principal == 1].copy()
T["n_principal"] = int(len(P))
THR = 1.645

# étape 1 : réduction
cst = {}
for v in VARS:
    m = P[P.variable == v]
    cst[v] = dict(mr=m.revision.mean(), sr=m.revision.std(ddof=1), me=m.erreur.mean(), se=m.erreur.std(ddof=1),
                  mrm=m.revision_med.mean(), srm=m.revision_med.std(ddof=1), mem=m.erreur_med.mean(), sem=m.erreur_med.std(ddof=1))
k_v = {v: cst[v]["sr"] / cst[v]["se"] for v in VARS}
T["k_moyen"] = float(np.mean(list(k_v.values())))
def reduit(d, med=False):
    d = d.copy()
    rc, ec = ("revision_med", "erreur_med") if med else ("revision", "erreur")
    sfx = "m" if med else ""
    d["zr"] = [(r - cst[v]["mr"+sfx]) / cst[v]["sr"+sfx] for r, v in zip(d[rc], d.variable)]
    d["ze"] = [(e - cst[v]["me"+sfx]) / cst[v]["se"+sfx] for e, v in zip(d[ec], d.variable)]
    return d
df = reduit(df); P = df[df.principal == 1].copy()
dfm = reduit(df, True)

# étape 2 : grande nouvelle
Q = {v: float(np.quantile(np.abs(P.loc[P.variable == v, "surprise"].values), 2/3)) for v in VARS}
df["L"] = np.where(df.surprise.notna(), (np.abs(df.surprise) > df.variable.map(Q)).astype(float), np.nan)
P = df[df.principal == 1].copy(); dfm["L"] = df["L"]
assert (P.L == P.grande_nouvelle).all()

# --- régression et Driscoll-Kraay
def design(d, L, par_variable=False):
    cols = []
    D = [(d.variable == v).astype(float).values for v in VARS]
    zr = d.zr.values; L = np.asarray(L, float)
    cols += D; cols += [x * L for x in D]; cols += [x * zr for x in D]
    cols += [zr * L * x for x in D] if par_variable else [zr * L]
    return np.column_stack(cols)
def dk(X, u, sem, lags):
    """Driscoll-Kraay : somme par semestre, y compris semestres vides entre le plus petit et le plus grand ; poids de Bartlett 1 - j/(lags+1)."""
    h = X * u[:, None]
    s0, s1 = sem.min(), sem.max()
    H = np.zeros((s1 - s0 + 1, X.shape[1]))
    np.add.at(H, sem - s0, h)
    Om = H.T @ H
    for j in range(1, lags + 1):
        G = H[j:].T @ H[:-j]
        Om += (1 - j / (lags + 1)) * (G + G.T)
    XtXi = np.linalg.inv(X.T @ X)
    return XtXi @ Om @ XtXi
def ols(X, y, sem, lags=2):
    XtXi = np.linalg.inv(X.T @ X); b = XtXi @ X.T @ y; u = y - X @ b
    V = dk(X, u, sem, lags)
    return b, V, u, XtXi
def reg(d, L, lags=2, par_variable=False, zecol="ze"):
    X = design(d, L, par_variable); y = d[zecol].values; sem = d.semestre.values.astype(int)
    b, V, u, XtXi = ols(X, y, sem, lags)
    return dict(b=b, V=V, u=u, XtXi=XtXi, n=len(y), p=X.shape[1], X=X)

R0 = reg(P, P.L)
c = float(R0["b"][15]); se2 = float(np.sqrt(R0["V"][15, 15]))
T.update(c=c, et_c_dk2=se2, t_c=c / se2, borne_basse_ic90=c - THR * se2, borne_haute_ic90=c + THR * se2)
bv = R0["b"][10:15]
T["b_moyen"] = float(bv.mean()); T["pente_moyenne_grandes"] = T["b_moyen"] + c
# étape 6 : contrôle positif
Xp = np.column_stack([(P.variable == v).astype(float).values for v in VARS] + [P.zr.values])
bp_, Vp, up, _ = ols(Xp, P.ze.values, P.semestre.values.astype(int))
T["b_regroupe"] = float(bp_[5]); T["et_b_regroupe_dk2"] = float(np.sqrt(Vp[5, 5]))
T["borne_basse_b_ic90"] = T["b_regroupe"] - THR * T["et_b_regroupe_dk2"]
T["controle_positif_ok"] = int(T["borne_basse_b_ic90"] > 0 or T["borne_haute_ic90"] < 0)

# étape 7 : biais mécanique
m0 = {v: P[(P.variable == v) & (P.L == 0)].zr.mean() for v in VARS}; m1 = {v: P[(P.variable == v) & (P.L == 1)].zr.mean() for v in VARS}
P0 = P[P.L == 0]; P1 = P[P.L == 1]
a = float(np.mean((P0.zr - P0.variable.map(m0)) ** 2)); A = float(np.mean((P1.zr - P1.variable.map(m1)) ** 2))
T["rapport_variance_revision"] = A / a
nu_i = (P.var_rep_1 / P.n_rep_1 + P.var_rep_2 / P.n_rep_2) / P.variable.map({v: cst[v]["sr"] ** 2 for v in VARS})
nu_v = {v: float(np.median(nu_i[P.variable == v])) for v in VARS}
T["nu_mesure"] = float(np.mean(list(nu_v.values())))
coef = 2 * T["b_moyen"] + T["k_moyen"]
T["biais_mecanique_mesure"] = coef * T["nu_mesure"] * (1 / a - 1 / A)
T["biais_mecanique_nu20"] = coef * 0.10 * (1 / a - 1 / A)
T["seuil_survie_bas"] = max(0.10, T["biais_mecanique_mesure"])
T["borne_basse_moins_seuil"] = T["borne_basse_ic90"] - T["seuil_survie_bas"]

# étape 8 : épisodes
ts, cs = {}, {}
for k in EPISODES:
    d = P[P.episode.fillna("") != k]
    r = reg(d, d.L)
    ck = float(r["b"][15]); sk = float(np.sqrt(r["V"][15, 15])); cs[k] = ck; ts[k] = ck / sk
    T[f"c_sans_{k}"] = ck
ks = list(EPISODES)
tmin = min(ts.values())
T["t_min_sans_episode"] = float(tmin); T["episode_t_min"] = int(min(int(k[1:]) for k in ks if ts[k] == tmin))
T["c_min_sans_episode"] = float(min(cs.values()))
# étape 9
T["marge_indecision"] = min(T["seuil_survie_bas"] - T["borne_basse_ic90"], T["borne_haute_ic90"] - 0.40)
T["conflit_robustesse"] = int(T["borne_basse_ic90"] > T["seuil_survie_bas"] and T["borne_haute_ic90"] >= 0.40 and T["t_min_sans_episode"] < 1 and T["c_min_sans_episode"] > 0)
# étape 10
n = len(P)
sig2 = float(R0["u"] @ R0["u"]) / (n - 16)
T["et_c_iid"] = float(np.sqrt(sig2 * R0["XtXi"][15, 15]))
T["n_effectif"] = float(n * (T["et_c_iid"] / se2) ** 2)
T["n_grands"] = int((P.L == 1).sum()); T["n_dates"] = int(P.semestre.nunique()); T["n_dates_grands"] = int(P[P.L == 1].semestre.nunique())
# S2
for lg in (4, 0):
    T[f"et_c_dk{lg}"] = float(np.sqrt(dk(R0["X"], R0["u"], P.semestre.values.astype(int), lg)[15, 15]))
# S1
r = reg(P, P.L, par_variable=True)
for i, v in enumerate(VARS):
    T[f"c_{v}"] = float(r["b"][15 + i]); T[f"et_c_{v}_dk2"] = float(np.sqrt(r["V"][15 + i, 15 + i]))
def sec(nom, d, L=None, zecol="ze"):
    r = reg(d, d.L if L is None else L, zecol=zecol)
    T[f"c_{nom}"] = float(r["b"][15]); T[f"et_c_{nom}_dk2"] = float(np.sqrt(r["V"][15, 15]))
# S3 : avec la pandémie (lignes principales + 4 lignes UNPR complètes), constantes de réduction inchangées
pand = df[(df.variable == "UNPR") & df.cible.isin(["2020-06", "2020-12", "2021-06", "2021-12"]) & (df.complete == 1) & (df.principal == 0)]
assert len(pand) == 4
sec("avec_pandemie", pd.concat([P, pand]).sort_values(["variable", "cible"]))
sec("depuis_1985", P[P.cible >= "1985-06"])
sec("avant_2020", P[P.cible <= "2019-12"])
Pm = dfm[dfm.principal == 1].copy(); Pm["ze"] = Pm.ze; Pm["zr"] = Pm.zr
sec("mediane", Pm)
Pc = P.copy(); sec("coupure_revision", Pc, L=(np.abs(Pc.zr) > 1).astype(float))

# types : entiers pour les comptes et indicateurs
ENT = {"n_violations_schema","n_principal","controle_positif_ok","episode_t_min","conflit_robustesse","n_grands","n_dates","n_dates_grands"}
reglej = json.loads(__import__("re").findall(r"```json\s*(\{.*?\})\s*```", (R / "preenregistrement.md").read_text(), flags=__import__("re").S)[-1])
out = {}
for ch in reglej["champs_verification"]:
    x = T[ch]; out[ch] = int(x) if ch in ENT else float(x)
assert set(out) == set(reglej["champs_verification"])
(R / "temoin.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))

# diagnostics hors règle
diag = {"nu_v": nu_v, "k_v": k_v, "Q_v": Q, "a": a, "A": A, "pente_mat": {}, "anomalies_hors_principal": [list(map(str, x)) for x in anom],
        "n_par_variable": P.variable.value_counts().to_dict(), "n_grands_par_variable": P[P.L == 1].variable.value_counts().to_dict()}
cp = P[(P.variable == "CPI") & ~P.enquete_2.isin(["1953-06", "1962-06", "1971-06", "1988-06"])]
dev = np.abs(np.log(cp.ancre_niv_2 / cp.bp_2) - np.log(cp.ancre_niv_1 / cp.bp_1))
diag["ipc_base_instable_n"] = int((dev > 0.005).sum()); diag["ipc_lignes_testees"] = int(len(cp))
# lecture alternative de a et A : par variable, puis moyenne
av = {v: float(np.mean((P0[P0.variable == v].zr - m0[v]) ** 2)) for v in VARS}; Av = {v: float(np.mean((P1[P1.variable == v].zr - m1[v]) ** 2)) for v in VARS}
diag["alt_rapport_par_variable"] = {v: Av[v] / av[v] for v in VARS}
diag["alt_rapport_moyenne"] = float(np.mean([Av[v] / av[v] for v in VARS]))
diag["alt_biais_mesure_par_variable"] = float(np.mean([coef * nu_v[v] * (1 / av[v] - 1 / Av[v]) for v in VARS]))
diag["c_sans_E_t"] = ts; diag["b_par_variable"] = dict(zip(VARS, map(float, bv)))
diag["b_regroupe_t"] = T["b_regroupe"] / T["et_b_regroupe_dk2"]
json.dump(diag, open(R / "analyse_diagnostics.json", "w"), ensure_ascii=False, indent=1, default=float)

# figure : c et intervalle à 90 %, par variable, avec la valeur de la fiche et le plancher
fig, ax = plt.subplots(figsize=(7, 4))
lab = ["Toutes\nvariables"] + VARS; vals = [c] + [T[f"c_{v}"] for v in VARS]; es = [se2] + [T[f"et_c_{v}_dk2"] for v in VARS]
ax.errorbar(range(6), vals, yerr=[THR * e for e in es], fmt="o", capsize=4, color="#1f4e79")
ax.axhline(0, color="grey", lw=.8); ax.axhline(0.40, color="#b03a2e", ls="--", lw=1, label="prédiction +0,40")
ax.axhline(T["seuil_survie_bas"], color="#2e7d32", ls=":", lw=1, label=f"plancher {T['seuil_survie_bas']:.2f}")
ax.set_xticks(range(6)); ax.set_xticklabels(lab); ax.set_ylabel("supplément de pente c (grandes surprises)")
ax.set_title("K20-LIV : c et intervalle à 90 % (Driscoll-Kraay, 2 semestres)"); ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(R / "figure.png", dpi=130)
print(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(diag, indent=1, ensure_ascii=False, default=float)[:3500])
