"""K20-LIV : construit K20-LIV_analyse.csv à partir de donnees/ (préinscription, sections 3 à 5), puis lance les contrôles de schéma."""
import sys, pathlib, json
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from controles import *

R = pathlib.Path(__file__).resolve().parent; D = R / "donnees"
FEUILLES = VARS
def lire(fichier):
    return pd.read_excel(D / fichier, sheet_name=FEUILLES)
means, meds, indiv = lire("means.xlsx"), lire("medians.xlsx"), lire("individualdata.xlsx")

def indexe(df, v):
    d = df.copy(); d["ym"] = pd.to_datetime(d["Date"]).dt.strftime("%Y-%m")
    for c in d.columns:
        if c not in ("Date", "ym", "ID", "Category"): d[c] = pd.to_numeric(d[c], errors="coerce")
    return d
M = {v: indexe(means[v], v).set_index("ym") for v in VARS}
MED = {v: indexe(meds[v], v).set_index("ym") for v in VARS}
I = {v: indexe(indiv[v], v) for v in VARS}
# dates d'enquête publiées : vérifiées contre le fichier
for v in VARS:
    assert list(M[v].index) == DATES_ENQUETE and list(MED[v].index) == DATES_ENQUETE, v
    assert set(I[v]["ym"]) <= set(DATES_ENQUETE)
    assert all(pd.to_datetime(M[v]["Date"]).dt.day == 1)

# FRED : dernière observation non vide du mois
def fred(s):
    t = pd.read_csv(D / f"FRED_{s}.csv"); t.columns = ["d", "x"]
    t["x"] = pd.to_numeric(t["x"], errors="coerce"); t["ym"] = t["d"].str[:7]
    out = {}
    for ym, grp in t.groupby("ym", sort=True):
        gg = grp.dropna(subset=["x"])
        out[ym] = (gg.iloc[-1]["d"], float(gg.iloc[-1]["x"])) if len(gg) else ("", np.nan)
    return out
F = {s: fred(s) for s in ["CPIAUCNS","CPIAUCSL","UNRATE","DPRIME","DTB3","HOUST"]}
def lis(serie, ym):
    j, x = F[serie].get(ym, ("", np.nan))
    if serie == "HOUST" and not np.isnan(x): x = x/1000.0
    return j, x

def bruit(v, enq, col):
    s = pd.to_numeric(I[v].loc[I[v]["ym"] == enq, f"{v}_{col}"], errors="coerce").dropna()
    n = int(len(s)); 
    if n < 2: return n, np.nan
    return n, float(np.var(g(v, s.values.astype(float)), ddof=1))

rows = []
for v in VARS:
    # première cible : enquête s a 12M et s+1 a 6M
    cibles = []
    T = "1947-06"
    for t in [ym_add("1946-06", 6*k) for k in range(0, 170)]:
        if t[5:] not in ("06", "12") or t > "2026-06": continue
        s, s1 = ym_add(t, -12), ym_add(t, -6)
        if s in M[v].index and s1 in M[v].index and pd.notna(M[v].at[s, f"{v}_12M"]) and pd.notna(M[v].at[s1, f"{v}_6M"]):
            cibles.append(t)
    first = cibles[0]
    t = first
    while t <= "2026-06":
        s, s1 = ym_add(t, -12), ym_add(t, -6)
        a1, a2 = ancre(s), ancre(s1)
        r = dict(variable=v, cible=t, semestre=2*int(t[:4]) + (0 if t[5:] == "06" else 1), enquete_1=s, enquete_2=s1, mois_ancre_1=a1, mois_ancre_2=a2)
        r["prev_12m_1"] = M[v].at[s, f"{v}_12M"]; r["prev_6m_2"] = M[v].at[s1, f"{v}_6M"]; r["prev_6m_1"] = M[v].at[s, f"{v}_6M"]
        r["bp_1"] = M["CPI"].at[s, "CPI_BP"] if v == "CPI" else np.nan
        r["bp_2"] = M["CPI"].at[s1, "CPI_BP"] if v == "CPI" else np.nan
        r["prev_12m_1_med"] = MED[v].at[s, f"{v}_12M"]; r["prev_6m_2_med"] = MED[v].at[s1, f"{v}_6M"]
        ser = ("CPIAUCNS" if s1 <= "2004-06" else "CPIAUCSL") if v == "CPI" else SERIE[v]
        r["serie_realise"] = ser
        for nom, ym in (("realise", t), ("ancre_1", a1), ("ancre_2", a2)):
            j, x = lis(ser, ym)
            r[f"jour_{nom}"] = j if not np.isnan(x) else ""
            r[f"{nom}_niv" if nom == "realise" else f"ancre_niv_{nom[-1]}"] = x
        straddle = (v == "CPI" and s == "2004-06")
        f = formules({k: r[k] for k in ("realise_niv","ancre_niv_1","ancre_niv_2","prev_12m_1","prev_6m_2","prev_6m_1","bp_1","bp_2","prev_12m_1_med","prev_6m_2_med")}, v)
        for k in ("y_prev_1","y_prev_2","y_prev6_1","y_realise","y_ancre_1","y_ancre_2","revision","erreur","surprise","revision_med","erreur_med"):
            r[k] = f.get(k, np.nan)
        if straddle:
            for k in ("y_prev_1","y_prev6_1","revision","surprise","revision_med"): r[k] = np.nan
        r["n_rep_1"], r["var_rep_1"] = bruit(v, s, "12M"); r["n_rep_2"], r["var_rep_2"] = bruit(v, s1, "6M")
        r["episode"] = episode_de(t)
        rows.append(r)
        t = ym_add(t, 6)
df = pd.DataFrame(rows)
df["complete"] = (df["revision"].notna() & df["erreur"].notna() & df["surprise"].notna()).astype(int)
df["principal"] = principal_recalcule(df)
# grande nouvelle (Q_v : tiers supérieur de |surprise| sur les lignes principales de la variable)
df["grande_nouvelle"] = np.nan
for v in VARS:
    m = df["variable"] == v
    Q = np.quantile(np.abs(df.loc[m & (df["principal"] == 1), "surprise"].values), 2/3)
    sm = m & df["surprise"].notna()
    df.loc[sm, "grande_nouvelle"] = (np.abs(df.loc[sm, "surprise"]) > Q).astype(int)
df["variable"] = pd.Categorical(df["variable"], VARS, ordered=True)
df = df.sort_values(["variable", "cible"]).reset_index(drop=True); df["variable"] = df["variable"].astype(str)
for c in ("semestre","n_rep_1","n_rep_2","grande_nouvelle"): df[c] = df[c].astype("Int64")
df = df[COLS]
df.to_csv(R / "K20-LIV_analyse.csv", index=False, encoding="utf-8", lineterminator="\n")

# --- contrôles sur le fichier ÉCRIT, relu
chk = pd.read_csv(R / "K20-LIV_analyse.csv", keep_default_na=True, dtype={"episode": str})
viol, anom = controles(chk)
print("lignes", len(chk), "complete", int(chk.complete.sum()), "principal", int(chk.principal.sum()))
print(chk.groupby("variable", sort=False).agg(lignes=("cible","size"), complete=("complete","sum"), principal=("principal","sum")))
print("violations par contrôle (lignes principales):", {n: len(x) for n, x in viol.items() if x}, "n_violations_schema =", n_violations(viol))
for n, x in viol.items():
    for m in x[:10]: print("  viol", n, m)
print("anomalies hors principal:", len(anom))
for a in anom[:60]: print("  anom", a)
cnt = chk[chk.principal == 1].episode.fillna("").value_counts().to_dict()
print("épisodes (principal):", dict(sorted(cnt.items())))
json.dump({"n_violations_schema": n_violations(viol), "violations": {str(n): x for n, x in viol.items()}, "anomalies_hors_principal": [list(map(str, a)) for a in anom]},
          open(R / "controles_resultat.json", "w"), ensure_ascii=False, indent=1)
