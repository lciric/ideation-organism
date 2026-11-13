#!/usr/bin/env python3
"""K20-ZE : construction de K20-ZE_analyse.csv (preinscription, sections 3.3 et 4) puis controles de schema (4.4).
Usage : python3 -I construire.py          (ecrit K20-ZE_analyse.csv, construire_journal.json, controles_schema.json)
Les controles (fonction controles) lisent le fichier ECRIT, pas les structures en memoire."""
import csv, json, math, hashlib, pathlib, re, sys
import numpy as np
import pandas as pd

ICI = pathlib.Path(__file__).resolve().parent
D = ICI / "donnees"
SORTIE = ICI / "K20-ZE_analyse.csv"

COLONNES = ["variable", "annee_cible", "tour", "t_tour", "rang", "horizon", "tour_prec", "horizon_prec", "n_rep",
            "n_rep_prec", "prev", "prev_prec", "prev_med", "prev_prec_med", "ref_periode", "ref", "ref_periode_prec",
            "ref_prec", "prev_glissante_t4", "realise", "revision", "erreur", "surprise", "surprise_consensus",
            "revision_med", "erreur_med", "complete", "principal", "episode", "grande_nouvelle"]
ENTIERS = {"annee_cible", "t_tour", "rang", "horizon", "horizon_prec", "n_rep", "n_rep_prec", "complete", "principal",
           "grande_nouvelle"}
TEXTES = {"variable", "tour", "tour_prec", "ref_periode", "ref_periode_prec", "episode"}
VARS = ["HICP", "RGDP", "UNEM"]
FICHIER_SPF = {"HICP": "1_HICP.csv", "RGDP": "3_RGDP.csv", "UNEM": "5_UNEM.csv"}
TYPE_REF = {"HICP": "M_REFERENCE", "RGDP": "Q_REFERENCE", "UNEM": "M_REFERENCE"}
TYPE_GLISS = {"HICP": "M_YEAR_1_AHEAD", "RGDP": "Q_YEAR_1_AHEAD", "UNEM": "M_YEAR_1_AHEAD"}
EUROSTAT = {"HICP": "eurostat_prc_hicp_ainr.csv", "RGDP": "eurostat_nama_10_gdp.csv", "UNEM": "eurostat_une_rt_m.csv"}
FENETRES = {"E1": (8032, 8037), "E2": (8046, 8052), "E3": (8079, 8095)}
PLAGE_PREV = {"HICP": (-3, 12), "RGDP": (-10, 10), "UNEM": (3, 15)}
PLAGE_REF = {"HICP": (-3, 12), "RGDP": (-20, 20), "UNEM": (3, 15)}
MOIS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
T_MIN = 4 * 1999 + 1 - 1  # 7996
LIGNES_ATTENDUES = 624

def tnum(annee, q): return 4 * annee + q - 1
def tlabel(t): return f"{t // 4}Q{t % 4 + 1}"
def tparse(s):
    m = re.fullmatch(r"(\d{4})Q([1-4])", s)
    return tnum(int(m.group(1)), int(m.group(2))) if m else None

def f(x):
    """cellule texte -> float ou None"""
    return None if x == "" or x is None else float(x)

# ---------------------------------------------------------------- lecture des sources
def lire_spf(v):
    d = pd.read_csv(D / FICHIER_SPF[v], dtype=str, keep_default_na=False)
    d = d[d.table_name == "Point"]
    d["t"] = [tparse(s) for s in d.ref_round]
    assert d.t.notna().all(), "ref_round hors format AAAAQn"
    return d

def realises():
    out = {}
    for v in ("HICP", "RGDP"):
        e = pd.read_csv(D / EUROSTAT[v], dtype=str, keep_default_na=False)
        out[v] = {int(r.TIME_PERIOD): float(r.OBS_VALUE) for r in e.itertuples()}
    e = pd.read_csv(D / EUROSTAT["UNEM"], dtype=str, keep_default_na=False)
    mois = {}
    for r in e.itertuples():
        mois.setdefault(int(r.TIME_PERIOD[:4]), []).append(float(r.OBS_VALUE))
    out["UNEM"] = {y: float(np.mean(m)) for y, m in mois.items() if len(m) == 12}
    return out

# ---------------------------------------------------------------- construction (3.3)
def construire():
    real = realises()
    lignes = []
    for v in VARS:
        d = lire_spf(v)
        indiv = d[d.forecaster_id.str.fullmatch(r"\d{3}")]
        ecb = d[(d.forecaster_id == "ECB") & (d.target_period_type == TYPE_REF[v])]
        assert len(ecb) == ecb.t.nunique() == 112, f"{v}: lignes ECB de reference {len(ecb)}"
        refs = {int(r.t): (r.target_period, float(r.value)) for r in ecb.itertuples()}
        # consensus annuels : (t, type, cible) -> valeurs
        ann = indiv[indiv.target_period_type.isin(["A_YEAR_0_AHEAD", "A_YEAR_1_AHEAD", "A_YEAR_2_AHEAD"])]
        cells = {}
        for (t, typ, cib), g in ann.groupby(["t", "target_period_type", "target_period"], sort=False):
            vals = g.value.astype(float).to_numpy()
            cells[(int(t), typ, cib)] = (len(vals), float(np.mean(vals)), float(np.median(vals)))
        gl = indiv[indiv.target_period_type == TYPE_GLISS[v]]
        glis = {}
        for (t, cib), g in gl.groupby(["t", "target_period"], sort=False):
            vals = g.value.astype(float).to_numpy()
            glis[(int(t), cib)] = (len(vals), float(np.mean(vals)))
        for y in range(2000, 2026):
            for j in range(1, 9):
                t = 4 * (y - 1) + j - 1
                hz = 1 if j <= 4 else 0
                tp = t - 1
                hzp = y - tp // 4
                r = dict.fromkeys(COLONNES)
                r.update(variable=v, annee_cible=y, tour=tlabel(t), t_tour=t, rang=j, horizon=hz,
                         tour_prec=tlabel(tp), horizon_prec=hzp)
                c = cells.get((t, f"A_YEAR_{hz}_AHEAD", str(y)))
                r["n_rep"] = c[0] if c else 0
                if c and c[0] >= 20: r["prev"], r["prev_med"] = c[1], c[2]
                cp = cells.get((tp, f"A_YEAR_{hzp}_AHEAD", str(y))) if tp >= T_MIN else None
                r["n_rep_prec"] = cp[0] if cp else 0
                if cp and cp[0] >= 20: r["prev_prec"], r["prev_prec_med"] = cp[1], cp[2]
                if t in refs: r["ref_periode"], r["ref"] = refs[t]
                if tp in refs: r["ref_periode_prec"], r["ref_prec"] = refs[tp]
                if r["ref_periode"] is not None and t - 4 >= T_MIN:
                    g = glis.get((t - 4, r["ref_periode"]))
                    if g and g[0] >= 20: r["prev_glissante_t4"] = g[1]
                r["realise"] = real[v][y]
                def diff(a, b):
                    return None if r[a] is None or r[b] is None else r[a] - r[b]
                r["revision"] = diff("prev", "prev_prec")
                r["erreur"] = diff("realise", "prev")
                r["surprise"] = diff("ref", "ref_prec")
                r["surprise_consensus"] = diff("ref", "prev_glissante_t4")
                r["revision_med"] = diff("prev_med", "prev_prec_med")
                r["erreur_med"] = diff("realise", "prev_med")
                r["complete"] = int(r["revision"] is not None and r["erreur"] is not None and r["surprise"] is not None)
                pand = v in ("RGDP", "UNEM") and (y in (2020, 2021) or 8080 <= t <= 8087)
                r["principal"] = int(r["complete"] == 1 and not pand)
                ep = [k for k, (P, T) in FENETRES.items() if t - 1 <= T and 4 * y + 3 >= P]
                assert len(ep) <= 1
                r["episode"] = ep[0] if ep else None
                lignes.append(r)
    # grande nouvelle (6.2)
    for v in VARS:
        L = [r for r in lignes if r["variable"] == v]
        par_tour = {}
        for r in L:
            if r["principal"] == 1: par_tour[r["t_tour"]] = abs(r["surprise"])
        a = np.array(list(par_tour.values()))
        Q, gl = grande_coupure(a)
        for r in L:
            if r["surprise"] is not None:
                s = abs(r["surprise"])
                r["grande_nouvelle"] = int(s > Q if gl == "stricte" else s >= Q)
    return lignes

def grande_coupure(a):
    """6.2 : Q = quantile 2/3, coupure stricte ou large (celle qui approche le mieux le tiers)."""
    Q = float(np.quantile(a, 2 / 3))
    N = len(a)
    ns, nl = int((a > Q).sum()), int((a >= Q).sum())
    return Q, ("stricte" if abs(ns / N - 1 / 3) <= abs(nl / N - 1 / 3) else "large")

def cellule(c, x):
    if x is None: return ""
    if c in ENTIERS: return str(int(x))
    if c in TEXTES: return str(x)
    return repr(float(x))

def ecrire(lignes, chemin=SORTIE):
    with open(chemin, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLONNES)
        for r in lignes:
            w.writerow([cellule(c, r[c]) for c in COLONNES])

# ---------------------------------------------------------------- contrôles de schéma (4.4), sur le fichier écrit
def regle_ref_periode(v, t):
    """periode attendue de la valeur de reference au tour t (3.1)"""
    Y, q = t // 4, t % 4 + 1
    if v == "HICP":
        if (Y, q) == (2024, 2): return "2024Feb"
        a, m = (Y - 1, 12) if q == 1 else (Y, 3 * (q - 1))
        return f"{a}{MOIS[m - 1]}"
    if v == "RGDP":
        u = t - 2
        return f"{u // 4}Q{u % 4 + 1}"
    exc = {(2000, 1): (1999, 12), (2023, 1): (2022, 10), (2023, 4): (2023, 7), (2024, 1): (2023, 10),
           (2024, 2): (2024, 1), (2024, 4): (2024, 7)}
    if (Y, q) in exc:
        a, m = exc[(Y, q)]
    else:  # deuxieme mois avant le debut du trimestre du tour : debut = mois 3(q-1)+1 ; moins 2 mois
        m0 = 3 * (q - 1) + 1 - 2
        a, m = (Y, m0) if m0 >= 1 else (Y - 1, m0 + 12)
    return f"{a}{MOIS[m - 1]}"

def references_brutes():
    """index calcules a partir des fichiers bruts, pour les controles"""
    ecb, glis = {}, {}
    for v in VARS:
        d = lire_spf(v)
        e = d[(d.forecaster_id == "ECB") & (d.target_period_type == TYPE_REF[v])]
        ecb[v] = {int(r.t): (r.target_period, float(r.value)) for r in e.itertuples()}
        ind = d[d.forecaster_id.str.fullmatch(r"\d{3}") & (d.target_period_type == TYPE_GLISS[v])].copy()
        ind["x"] = ind.value.astype(float)
        g = ind.groupby(["t", "target_period"])["x"].agg(["count", "mean"])
        glis[v] = {(int(t), p): (int(n), float(m)) for (t, p), (n, m) in g.iterrows()}
    return ecb, glis, realises()

def controles(chemin, raw=None):
    """Retourne {'echecs': {n: [indices de lignes]}, 'fichier': {1: bool, 2: bool}, 'n_violations_schema', 'n_anomalies_hors_principal'}.
    Un controle de fichier echoue => entree vide dans 'echecs' avec index -1."""
    ecb, glis, real = raw if raw else references_brutes()
    with open(chemin, encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh)
        entete = next(rd)
        rows = [dict(zip(entete, l)) for l in rd if l]
    ech = {n: set() for n in range(1, 13)}
    # 1 colonnes
    if entete != COLONNES: ech[1].add(-1)
    # 2 grille
    grille = [(v, y, 4 * (y - 1) + j - 1) for v in VARS for y in range(2000, 2026) for j in range(1, 9)]
    try:
        cles = [(r["variable"], int(r["annee_cible"]), int(r["t_tour"])) for r in rows]
    except Exception:
        cles = None
    if len(rows) != LIGNES_ATTENDUES or cles != grille: ech[2].add(-1)
    if ech[1] or ech[2]:  # fichier mal forme : les contrôles de ligne n'ont plus de sens
        return resume(ech, rows)
    P = lambda r: r["principal"] == "1"
    idx = {(r["variable"], int(r["annee_cible"]), int(r["t_tour"])): i for i, r in enumerate(rows)}
    close = lambda a, b: abs(a - b) <= 1e-9
    for i, r in enumerate(rows):
        v, y, t = r["variable"], int(r["annee_cible"]), int(r["t_tour"])
        try:
            # 3 identifiants
            ok = re.fullmatch(r"\d{4}Q[1-4]", r["tour"]) is not None and tparse(r["tour"]) == t
            rang = t - 4 * (y - 1) + 1
            ok &= 1 <= rang <= 8 and int(r["rang"]) == rang
            ok &= int(r["horizon"]) == y - t // 4 == (1 if rang <= 4 else 0)
            ok &= r["tour_prec"] == tlabel(t - 1) and int(r["horizon_prec"]) == y - (t - 1) // 4 and int(r["horizon_prec"]) in (0, 1, 2)
            if not ok: ech[3].add(i)
            # 4 effectifs
            nr, nrp = int(r["n_rep"]), int(r["n_rep_prec"])
            ok = (r["prev"] != "") == (nr >= 20) and (r["prev_prec"] != "") == (nrp >= 20)
            ok &= (r["prev_med"] != "") == (nr >= 20) and (r["prev_prec_med"] != "") == (nrp >= 20)
            if P(r):
                ok &= nr >= 20 and nrp >= 20 and all(r[c] != "" for c in ("prev", "prev_prec", "prev_med", "prev_prec_med"))
            if not ok: ech[4].add(i)
            # 5 reference
            ok = True
            for tt, cp, cv in ((t, "ref_periode", "ref"), (t - 1, "ref_periode_prec", "ref_prec")):
                if tt >= T_MIN:
                    per, val = ecb[v][tt]
                    ok &= r[cp] == per and r[cv] != "" and float(r[cv]) == val and r[cp] == regle_ref_periode(v, tt)
                else:
                    ok &= r[cp] == "" and r[cv] == ""
            if not ok: ech[5].add(i)
            # 6 plages
            ok = True
            for c in ("prev", "prev_prec", "prev_med", "prev_prec_med", "realise"):
                x = f(r[c])
                if x is not None: ok &= PLAGE_PREV[v][0] <= x <= PLAGE_PREV[v][1]
            for c in ("ref", "ref_prec"):
                x = f(r[c])
                if x is not None: ok &= PLAGE_REF[v][0] <= x <= PLAGE_REF[v][1]
            if not ok: ech[6].add(i)
            # 7 formules
            ok = True
            for res, a, b in (("revision", "prev", "prev_prec"), ("erreur", "realise", "prev"), ("surprise", "ref", "ref_prec"),
                              ("surprise_consensus", "ref", "prev_glissante_t4"), ("revision_med", "prev_med", "prev_prec_med"),
                              ("erreur_med", "realise", "prev_med")):
                xa, xb, xr = f(r[a]), f(r[b]), f(r[res])
                if xa is None or xb is None: ok &= xr is None
                else: ok &= xr is not None and close(xr, xa - xb)
            g = glis[v].get((t - 4, r["ref_periode"])) if t - 4 >= T_MIN else None
            ok &= (r["prev_glissante_t4"] != "") == (g is not None and g[0] >= 20)
            if g and g[0] >= 20 and r["prev_glissante_t4"] != "": ok &= close(float(r["prev_glissante_t4"]), g[1])
            if not ok: ech[7].add(i)
            # 8 coherence entre lignes
            ok = True
            j = idx.get((v, y, t - 1))
            if j is not None:
                ok &= rows[j]["prev"] == r["prev_prec"] and rows[j]["n_rep"] == r["n_rep_prec"]
            for c in ("ref", "ref_periode", "ref_prec", "surprise", "grande_nouvelle"):
                ok &= all(rows[idx[(v, yy, t)]][c] == r[c] for yy in range(2000, 2026) if (v, yy, t) in idx)
            tr = [rows[k]["ref"] for (vv, yy, tt), k in idx.items() if vv == v and tt == t - 1][:1]
            if tr: ok &= tr[0] == r["ref_prec"]
            if not ok: ech[8].add(i)
            # 9 realise
            ok = r["realise"] != "" and close(float(r["realise"]), real[v][y])
            ok &= len({rows[k]["realise"] for (vv, yy, tt), k in idx.items() if vv == v and yy == y}) == 1
            if not ok: ech[9].add(i)
            # 10 appartenance
            comp = int(all(r[c] != "" for c in ("revision", "erreur", "surprise")))
            pand = v in ("RGDP", "UNEM") and (y in (2020, 2021) or 8080 <= t <= 8087)
            if r["complete"] != str(comp) or r["principal"] != str(int(comp == 1 and not pand)): ech[10].add(i)
            # 11 episodes
            ep = [k for k, (Pk, Tk) in FENETRES.items() if t - 1 <= Tk and 4 * y + 3 >= Pk]
            if r["episode"] != (ep[0] if ep else ""): ech[11].add(i)
        except Exception:
            for n in (3,): ech[n].add(i)
    # 12 grande nouvelle, recalculee depuis 'surprise'
    for v in VARS:
        par_tour = {}
        for r in rows:
            if r["variable"] == v and P(r) and r["surprise"] != "": par_tour[int(r["t_tour"])] = abs(float(r["surprise"]))
        if len(par_tour) < 5:
            for i, r in enumerate(rows):
                if r["variable"] == v: ech[12].add(i)
            continue
        Q, gl = grande_coupure(np.array(list(par_tour.values())))
        for i, r in enumerate(rows):
            if r["variable"] != v: continue
            if (r["surprise"] == "") != (r["grande_nouvelle"] == ""): ech[12].add(i); continue
            if r["surprise"] != "":
                s = abs(float(r["surprise"]))
                att = int(s > Q if gl == "stricte" else s >= Q)
                if r["grande_nouvelle"] != str(att): ech[12].add(i)
    return resume(ech, rows)

def resume(ech, rows):
    nv, anom, detail = 0, 0, {}
    for n, s in sorted(ech.items()):
        if not s: continue
        if n in (1, 2, 10) or -1 in s:
            nv += 1; detail[n] = {"compte_verdict": True, "lignes": len(s)}
            continue
        sur_p = [i for i in s if rows[i]["principal"] == "1"]
        hors = len(s) - len(sur_p)
        anom += hors
        if sur_p: nv += 1
        detail[n] = {"compte_verdict": bool(sur_p), "lignes_principales": len(sur_p), "lignes_hors_principal": hors}
    return {"echecs": {n: sorted(s) for n, s in ech.items()}, "n_violations_schema": nv,
            "n_anomalies_hors_principal": anom, "detail": detail}

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

if __name__ == "__main__":
    lignes = construire()
    ecrire(lignes)
    res = controles(SORTIE)
    # journal (3) : sha256, date, HTTP, LAST UPDATE
    prov = {}
    for l in (D / "PROVENANCE.md").read_text().splitlines():
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 6 and c[3] == "200": prov[c[0]] = {"date": c[2], "http": int(c[3])}
    journal = {}
    for nom in sorted(p.name for p in D.iterdir() if p.is_file() and p.name != "PROVENANCE.md"):
        e = {"sha256": sha(D / nom)}
        e.update(prov.get(nom, {}))
        if nom.startswith("eurostat_"):
            e["last_update"] = list(csv.DictReader(open(D / nom, encoding="utf-8")))[0]["LAST UPDATE"]
        journal[nom] = e
    journal["K20-ZE_analyse.csv"] = {"sha256": sha(SORTIE)}
    (ICI / "construire_journal.json").write_text(json.dumps(journal, indent=1, ensure_ascii=False))
    (ICI / "controles_schema.json").write_text(json.dumps(
        {k: v for k, v in res.items() if k != "echecs"} | {"echecs_par_controle": {str(n): len(s) for n, s in res["echecs"].items()}},
        indent=1, ensure_ascii=False))
    df = pd.read_csv(SORTIE)
    print("lignes", len(df), "complete", df.complete.sum(), "principal", df.principal.sum())
    print(df.groupby("variable")[["complete", "principal"]].sum().to_string())
    print("episodes (principal):", df[df.principal == 1].episode.fillna("hors").value_counts().to_dict())
    print("episodes (tout):", df.episode.fillna("hors").value_counts().to_dict())
    print("tours principaux:", df[df.principal == 1].t_tour.nunique())
    print(json.dumps({k: v for k, v in res.items() if k != "echecs"}, indent=1))
    print("echecs par controle:", {n: len(s) for n, s in res["echecs"].items() if s})
