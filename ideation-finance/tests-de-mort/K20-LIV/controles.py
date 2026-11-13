"""K20-LIV : constantes et contrôles de schéma (préinscription, sections 5 et 6). Ne lit aucune donnée : tout vient du fichier d'analyse."""
import numpy as np, pandas as pd

COLS = ["variable","cible","semestre","enquete_1","enquete_2","mois_ancre_1","mois_ancre_2","prev_12m_1","prev_6m_2","prev_6m_1",
        "bp_1","bp_2","prev_12m_1_med","prev_6m_2_med","serie_realise","jour_realise","realise_niv","jour_ancre_1","ancre_niv_1",
        "jour_ancre_2","ancre_niv_2","y_prev_1","y_prev_2","y_prev6_1","y_realise","y_ancre_1","y_ancre_2","revision","erreur",
        "surprise","revision_med","erreur_med","n_rep_1","var_rep_1","n_rep_2","var_rep_2","complete","principal","episode","grande_nouvelle"]
assert len(COLS) == 40
VARS = ["CPI","UNPR","PRIME","TBILL","TPHS"]
PLAGE_CIBLE = {"CPI":("1947-12","2026-06"),"UNPR":("1962-06","2026-06"),"PRIME":("1982-06","2026-06"),"TBILL":("1993-06","2026-06"),"TPHS":("1970-12","2026-06")}
EPISODES = {"E1":("1948-11","1950-12"),"E2":("1953-07","1955-07"),"E3":("1957-08","1959-06"),"E4":("1960-04","1962-04"),
            "E5":("1969-12","1972-01"),"E6":("1973-11","1976-05"),"E7":("1980-01","1984-01"),"E8":("1990-07","1992-05"),
            "E9":("2001-03","2003-01"),"E10":("2007-12","2010-08"),"E11":("2020-02","2023-12")}
PANDEMIE = {"2020-06","2020-12","2021-06","2021-12"}
PLAGE_PREV = {"CPI":(50,500),"UNPR":(1,20),"PRIME":(1,25),"TBILL":(-1,20),"TPHS":(0.2,3.5)}
PLAGE_REAL = {"CPI":(15,500),"UNPR":(1,20),"PRIME":(1,25),"TBILL":(-1,20),"TPHS":(0.2,3.5)}
SERIE = {"UNPR":"UNRATE","PRIME":"DPRIME","TBILL":"DTB3","TPHS":"HOUST"}
MENSUELLE = {"CPIAUCNS","CPIAUCSL","UNRATE","HOUST"}
DATES_ENQUETE = [f"{y}-{m:02d}" for y in range(1946, 2027) for m in (6, 12)][:-1]  # 161 dates, 1946-06 à 2026-06
assert len(DATES_ENQUETE) == 161

def ym_add(ym, n):
    y, m = int(ym[:4]), int(ym[5:7]); t = y*12 + (m-1) + n
    return f"{t//12}-{t%12+1:02d}"
def ancre(enq): return f"{enq[:4]}-04" if enq[5:] == "06" else f"{enq[:4]}-10"
def episode_de(cible):
    for k, (a, b) in EPISODES.items():
        if a <= cible <= b: return k
    return ""
def g(v, x): return 100*np.log(x) if v in ("CPI","TPHS") else x
def ok(x): return x is not None and not pd.isna(x)

def formules(r, v):
    """Recalcule les colonnes dérivées depuis les colonnes d'entrée d'une ligne (dict). Renvoie un dict ; NaN si un opérande manque."""
    nan = np.nan
    def yp(prev, bp, anc):
        if v == "CPI": return 100*np.log(prev) - 100*np.log(bp) + g(v, anc)
        return g(v, prev)
    o = {}
    try:
        o["y_realise"] = g(v, r["realise_niv"]); o["y_ancre_1"] = g(v, r["ancre_niv_1"]); o["y_ancre_2"] = g(v, r["ancre_niv_2"])
        o["y_prev_1"] = yp(r["prev_12m_1"], r["bp_1"], r["ancre_niv_1"])
        o["y_prev_2"] = yp(r["prev_6m_2"], r["bp_2"], r["ancre_niv_2"])
        o["y_prev6_1"] = yp(r["prev_6m_1"], r["bp_1"], r["ancre_niv_1"])
        y1m = yp(r["prev_12m_1_med"], r["bp_1"], r["ancre_niv_1"]); y2m = yp(r["prev_6m_2_med"], r["bp_2"], r["ancre_niv_2"])
    except Exception:
        return {}
    o["revision"] = o["y_prev_2"] - o["y_prev_1"]
    o["erreur"] = o["y_realise"] - o["y_prev_2"]
    o["surprise"] = o["y_ancre_2"] - (o["y_ancre_1"] + 0.75*(o["y_prev6_1"] - o["y_ancre_1"]))
    o["revision_med"] = y2m - y1m
    o["erreur_med"] = o["y_realise"] - y2m
    return o

def principal_recalcule(df):
    comp = df["revision"].notna() & df["erreur"].notna() & df["surprise"].notna()
    return (comp & (df["n_rep_1"] >= 2) & (df["n_rep_2"] >= 2) & df["var_rep_1"].notna() & df["var_rep_2"].notna()
            & ~((df["variable"] == "UNPR") & df["cible"].isin(PANDEMIE))).astype(int)

def _cell_ok(x, strict): return ok(x)

def controles(df):
    """Renvoie (violations, anomalies). violations[n] = liste de messages pour les lignes de portée (principal=1 ou recalculé=1) ;
    anomalies = liste (n, ligne, message) des contrôles 3 à 8 sur les autres lignes (cellules présentes)."""
    viol = {n: [] for n in range(1, 12)}; anom = []
    # 1 colonnes
    if list(df.columns) != COLS: viol[1].append("colonnes différentes")
    if viol[1]: return viol, anom   # le reste suppose le schéma
    rec = principal_recalcule(df)
    portee = (df["principal"] == 1) | (rec == 1)
    # grande nouvelle : Q_v depuis les lignes de portée
    Q = {v: np.quantile(np.abs(df.loc[portee & (df["variable"] == v), "surprise"].dropna().astype(float)), 2/3) for v in VARS if (portee & (df["variable"] == v)).any()}
    sc = df[portee]
    # 2 clés
    for i, r in sc.iterrows():
        if r["variable"] not in VARS: viol[2].append(f"ligne {i}: variable {r['variable']}"); continue
        lo, hi = PLAGE_CIBLE[r["variable"]]
        if not (isinstance(r["cible"], str) and r["cible"][5:] in ("06", "12") and lo <= r["cible"] <= hi): viol[2].append(f"ligne {i}: cible {r['cible']}")
    if sc.duplicated(["variable", "cible"]).any(): viol[2].append("couple (variable, cible) dupliqué")
    if df.duplicated(["variable", "cible"]).any(): anom.append((2, -1, "couple (variable, cible) dupliqué dans le fichier entier"))
    def run(n, i, r, msg):
        (viol[n].append(f"ligne {i}: {msg}") if portee[i] else anom.append((n, i, msg)))
    for i, r in df.iterrows():
        v = r["variable"]
        if v not in VARS: continue
        # 3 dates
        e1, e2, c = r["enquete_1"], r["enquete_2"], r["cible"]
        try:
            bad = (e1 not in DATES_ENQUETE or e2 not in DATES_ENQUETE or DATES_ENQUETE.index(e2) != DATES_ENQUETE.index(e1) + 1
                   or c != ym_add(e2, 6) or e1 != f"{int(c[:4])-1}-{c[5:]}" or r["mois_ancre_1"] != ancre(e1) or r["mois_ancre_2"] != ancre(e2)
                   or r["semestre"] != 2*int(c[:4]) + (0 if c[5:] == "06" else 1))
        except Exception: bad = True
        if bad: run(3, i, r, "dates d'enquête / cible / mois de base / semestre")
        # 4 présence
        must = ["prev_12m_1","prev_6m_2","prev_6m_1","serie_realise","jour_realise","jour_ancre_1","jour_ancre_2","realise_niv","ancre_niv_1","ancre_niv_2",
                "y_prev_1","y_prev_2","y_prev6_1","y_realise","y_ancre_1","y_ancre_2","revision","erreur","surprise","n_rep_1","var_rep_1","n_rep_2","var_rep_2","grande_nouvelle"]
        if portee[i]:
            miss = [m for m in must if not ok(r[m]) or r[m] == ""]
            if miss: viol[4].append(f"ligne {i}: absent {miss}")
        if (v == "CPI") != (ok(r["bp_1"]) and ok(r["bp_2"])) or (v != "CPI" and (ok(r["bp_1"]) or ok(r["bp_2"]))):
            if portee[i] or v != "CPI" or ok(r["bp_1"]) or ok(r["bp_2"]): run(4, i, r, "bp_1/bp_2 présentes ssi CPI")
        # 5 séries et jours
        att = ("CPIAUCNS" if r["enquete_2"] <= "2004-06" else "CPIAUCSL") if v == "CPI" else SERIE[v]
        b5 = False
        if ok(r["serie_realise"]) and r["serie_realise"] != att: b5 = True
        for jc, ref in (("jour_realise", c), ("jour_ancre_1", r["mois_ancre_1"]), ("jour_ancre_2", r["mois_ancre_2"])):
            j = r[jc]
            if ok(j) and j != "":
                if str(j)[:7] != ref: b5 = True
                if att in MENSUELLE and str(j)[8:] != "01": b5 = True
        if b5: run(5, i, r, "série ou jour de lecture")
        # 6 plages
        b6 = False
        lo, hi = PLAGE_PREV[v]
        for cn in ("prev_12m_1","prev_6m_2","prev_6m_1","prev_12m_1_med","prev_6m_2_med") + (("bp_1","bp_2") if v == "CPI" else ()):
            if ok(r[cn]) and not (lo <= r[cn] <= hi) and (cn.endswith("_med") is False or True): b6 = True
        lo, hi = PLAGE_REAL[v]
        for cn in ("realise_niv","ancre_niv_1","ancre_niv_2"):
            if ok(r[cn]) and not (lo <= r[cn] <= hi): b6 = True
        if b6: run(6, i, r, "plage des entrées")
        # 7 formules
        f = formules({k: (np.nan if not ok(r[k]) else r[k]) for k in ("realise_niv","ancre_niv_1","ancre_niv_2","prev_12m_1","prev_6m_2","prev_6m_1","bp_1","bp_2","prev_12m_1_med","prev_6m_2_med")}, v) if True else {}
        b7 = False
        for cn, val in f.items():
            if cn in ("revision_med","erreur_med") or True:
                if ok(val) and ok(r[cn]) and abs(val - r[cn]) > 1e-6: b7 = True
                if ok(val) and not ok(r[cn]) and cn in ("y_realise","y_ancre_1","y_ancre_2","y_prev_1","y_prev_2","y_prev6_1","revision","erreur","surprise") and portee[i]: b7 = True
        if b7: run(7, i, r, "formule")
        # 8 bruit
        b8 = False
        for nc, vc in (("n_rep_1","var_rep_1"),("n_rep_2","var_rep_2")):
            if ok(r[nc]) and (r[nc] != int(r[nc]) or r[nc] < 2): b8 = True
            if ok(r[vc]) and r[vc] < 0: b8 = True
            if portee[i] and (not ok(r[nc]) or not ok(r[vc])): b8 = True
        if b8: run(8, i, r, "bruit")
        # 9 indicateurs (portée seulement)
        if portee[i]:
            comp = int(ok(r["revision"]) and ok(r["erreur"]) and ok(r["surprise"]))
            if r["complete"] != 1 or comp != 1 or r["principal"] != rec[i]: viol[9].append(f"ligne {i}: indicateurs")
            # 10 épisode
            if (r["episode"] if ok(r["episode"]) else "") != episode_de(c): viol[10].append(f"ligne {i}: épisode")
            # 11 grande nouvelle
            gn = r["grande_nouvelle"]
            if not ok(gn) or gn not in (0, 1) or (ok(r["surprise"]) and gn != int(abs(r["surprise"]) > Q[v])): viol[11].append(f"ligne {i}: grande_nouvelle")
    return viol, anom

def n_violations(viol): return sum(1 for n in viol if viol[n])
