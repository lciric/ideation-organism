"""K01 - verification independante, ecrite a partir du seul preenregistrement.md (sections 6 et 7).

Lit uniquement K01_analyse.csv. Ecrit verification.json (champs "champs_verification") ; imprime en console le detail des
controles de schema et les analyses de fragilite (hors verdict).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parent
FICHIER = ICI / "K01_analyse.csv"
C = 1.714
LAGS = 8

COLONNES = ["source", "id_prev", "tour", "t_tour", "millesime", "statut", "mois_titre", "annee_titre",
            "annee_cible", "horizon", "rang", "prevision", "prevision_prec", "revision", "autre_cible",
            "prevision_autre", "prevision_autre_prec", "instrument", "realise", "erreur",
            "nb_tours_complets", "echantillon_iv"]

raw = pd.read_csv(FICHIER, dtype=str, keep_default_na=False, encoding="utf-8")


def num(col):
    s = raw[col]
    out = pd.to_numeric(s.where(s != "", None), errors="coerce")
    return out


# ---------------------------------------------------------------- controles de schema
checks = {}
details = {}


def record(k, bad_mask_or_list, msg):
    if isinstance(bad_mask_or_list, (pd.Series, np.ndarray)):
        idx = list(np.where(np.asarray(bad_mask_or_list))[0])
    else:
        idx = list(bad_mask_or_list)
    details.setdefault(k, [])
    if idx:
        details[k].append({"probleme": msg, "n": len(idx), "lignes_fichier": [int(i) + 2 for i in idx[:20]]})
    return len(idx) == 0


def setmsg(k, ok, msg):
    details.setdefault(k, [])
    if not ok:
        details[k].append({"probleme": msg})
    return ok


# 1 colonnes
checks[1] = setmsg(1, list(raw.columns) == COLONNES, f"colonnes = {list(raw.columns)}")

src = raw["source"]
spf = src == "SPF"
bce = src == "BCE"

# 2 cle
ok = True
key = raw[["source", "id_prev", "t_tour", "annee_cible"]]
ok &= record(2, key.duplicated(keep=False), "cle dupliquee")
ok &= record(2, ~src.isin(["SPF", "BCE"]), "source hors {SPF,BCE}")
ok &= record(2, spf & ~raw["id_prev"].str.fullmatch(r"\d{3}"), "id_prev SPF pas trois chiffres")
ok &= record(2, bce & (raw["id_prev"] != "BCE"), "id_prev BCE != 'BCE'")
checks[2] = ok

# 3 tours
ok = True
m = raw["tour"].str.extract(r"^(\d{4})Q([1-4])$")
badfmt = m[0].isna()
ok &= record(3, badfmt, "tour mal forme")
AAAA = pd.to_numeric(m[0], errors="coerce")
n_q = pd.to_numeric(m[1], errors="coerce")
tt = num("t_tour")
ok &= record(3, ~badfmt & ~raw["t_tour"].str.fullmatch(r"-?\d+"), "t_tour non entier")
ok &= record(3, ~badfmt & (tt != 4 * AAAA + n_q - 1), "t_tour != 4*AAAA+n-1")
ok &= record(3, ~((tt >= 8007) & (tt <= 8103)), "t_tour hors [8007;8103]")
attendu = set(range(8007, 8104))
ok &= setmsg(3, set(tt[spf].dropna().astype(int)) == attendu, "SPF ne couvre pas exactement 8007..8103")
ok &= setmsg(3, set(tt[bce].dropna().astype(int)) == attendu, "BCE ne couvre pas exactement 8007..8103")
checks[3] = ok

# 4 cibles
ok = True
ac = num("annee_cible")
hz = num("horizon")
rg = num("rang")
ok &= record(4, (hz != ac - AAAA) | ~hz.isin([0, 1, 2]), "horizon != annee_cible-AAAA ou hors {0,1,2}")
ok &= record(4, rg != tt - 4 * (ac - 1) + 1, "rang ne suit pas sa formule")
checks[4] = ok

# 5 millesimes BCE
ok = True
cols5 = ["millesime", "statut", "mois_titre", "annee_titre"]
ok &= record(5, bce & (raw[cols5] == "").any(axis=1), "colonne millesime vide sur ligne BCE")
ok &= record(5, spf & (raw[cols5] != "").any(axis=1), "colonne millesime non vide sur ligne SPF")
mm = raw["millesime"].str.extract(r"^([WGSA])(\d{2})$")
lettre_q = mm[0].map({"W": 1, "G": 2, "S": 3, "A": 4})
an_mil = 2000 + pd.to_numeric(mm[1], errors="coerce")
ok &= record(5, bce & ((lettre_q != n_q) | (an_mil != AAAA)), "lettre/annee du millesime != tour")
ok &= record(5, bce & (num("mois_titre") != 3 * n_q), "mois_titre != 3*trimestre")
ok &= record(5, bce & (num("annee_titre") != AAAA), "annee_titre != annee")
liste = ["A01"] + [f"{l}{y:02d}" for y in range(2, 26) for l in "WGSA"]
vc = raw.loc[bce, "millesime"].value_counts()
ok &= setmsg(5, set(vc.index) == set(liste) and (vc == 3).all() and len(liste) == 97,
             "liste figee des 97 codes x 3 lignes non respectee")
checks[5] = ok

# 6 statut
checks[6] = record(6, bce & (raw["statut"] != "F"), "statut != F")

# 7 valeurs
ok = True
pv = num("prevision")
rl = num("realise")
ok &= record(7, pv.isna() | (pv < -5) | (pv > 15), "prevision vide ou hors [-5;15]")
ok &= record(7, rl.isna() != (ac > 2025), "realise vide ssi annee_cible>2025 non respecte")
dec_r = raw["realise"].str.split(".").str[1].fillna("").str.len()
ok &= record(7, rl.notna() & ((rl < -5) | (rl > 15) | (dec_r > 1)), "realise hors bornes ou >1 decimale")
checks[7] = ok

# index des previsions
pidx = {}
for s_, i_, t_, y_, p_ in zip(src, raw["id_prev"], tt, ac, pv):
    if pd.notna(t_) and pd.notna(y_):
        pidx[(s_, i_, int(t_), int(y_))] = p_


def look(s_, i_, t_, y_):
    return pidx.get((s_, i_, int(t_), int(y_)), np.nan)


# 8 prevision precedente
pp = num("prevision_prec")
exp_pp = np.array([look(s_, i_, t_ - 1, y_) if t_ >= 8008 else np.nan
                   for s_, i_, t_, y_ in zip(src, raw["id_prev"], tt, ac)])
bad8 = (pp.isna().values != np.isnan(exp_pp)) | (pp.notna().values & ~np.isnan(exp_pp)
                                                  & (np.abs(pp.values - exp_pp) > 1e-12))
checks[8] = record(8, bad8, "prevision_prec != prevision (t-1, meme cible) ou presence incoherente")
exact8 = int(np.sum(pp.notna().values & ~np.isnan(exp_pp) & (pp.values != exp_pp)))

# 9 autre cible
ok = True
oc = num("autre_cible")
exp_oc = np.where(hz == 0, ac + 1, np.where(hz == 1, ac - 1, np.nan))
ok &= record(9, ~((oc.isna().values & np.isnan(exp_oc)) | (oc.values == exp_oc)), "autre_cible ne suit pas sa definition")
pa = num("prevision_autre")
pap = num("prevision_autre_prec")
exp_pa = np.array([look(s_, i_, t_, o_) if not np.isnan(o_) else np.nan
                   for s_, i_, t_, o_ in zip(src, raw["id_prev"], tt, exp_oc)])
exp_pap = np.array([look(s_, i_, t_ - 1, o_) if (not np.isnan(o_) and t_ >= 8008) else np.nan
                    for s_, i_, t_, o_ in zip(src, raw["id_prev"], tt, exp_oc)])
for col, obs, ex in [("prevision_autre", pa, exp_pa), ("prevision_autre_prec", pap, exp_pap)]:
    b = (obs.isna().values != np.isnan(ex)) | (obs.notna().values & ~np.isnan(ex) & (np.abs(obs.values - ex) > 1e-12))
    ok &= record(9, b, f"{col} incoherent avec la ligne designee")
checks[9] = ok

# 10 calculs
ok = True
for col, a, b_ in [("revision", pv, pp), ("instrument", pa, pap), ("erreur", rl, pv)]:
    v = num(col)
    d = a - b_
    pres = d.notna()
    ok &= record(10, v.isna() != ~pres, f"{col} vide ssi un terme vide non respecte")
    ok &= record(10, pres & v.notna() & ((v - d).abs() > 1e-9), f"{col} != difference a 1e-9")
checks[10] = ok

# 11 realise unique par annee
g = pd.DataFrame({"y": ac, "r": raw["realise"]}).groupby("y")["r"].nunique()
bady = list(g[g > 1].index)
checks[11] = record(11, ac.isin(bady), "realise non unique pour l'annee cible")

# 12 echantillon
rv = num("revision")
ins = num("instrument")
er = num("erreur")
complet = spf & hz.isin([0, 1]) & (tt >= 8008) & (tt <= 8103) & rv.notna() & ins.notna() & er.notna()
ntc = pd.DataFrame({"i": raw["id_prev"], "t": tt})[complet].groupby("i")["t"].nunique()
exp_ntc = raw["id_prev"].map(ntc).fillna(0)
ntc_obs = num("nb_tours_complets")
ok = True
ok &= record(12, spf & (ntc_obs != exp_ntc), "nb_tours_complets SPF ne suit pas sa definition")
ok &= record(12, bce & ntc_obs.notna(), "nb_tours_complets non vide sur ligne BCE")
exp_ech = (complet & (exp_ntc >= 8)).astype(int)
ok &= record(12, raw["echantillon_iv"] != exp_ech.astype(str), "echantillon_iv ne suit pas sa definition")
checks[12] = ok

n_violations = sum(1 for v in checks.values() if not v)

# controles supplementaires (hors des 12, signales seulement)
autres = {}
tri = raw.assign(_t=tt, _y=ac).sort_values(["source", "id_prev", "_t", "_y"], kind="stable").index
autres["tri_conforme"] = bool((tri == raw.index).all())
autres["n_SPF"] = int(spf.sum())
autres["n_BCE"] = int(bce.sum())
autres["prevision_prec_egalite_exacte_echecs"] = exact8
autres["horizon_negatif"] = int((hz < 0).sum())

# ---------------------------------------------------------------- statistiques
df = pd.DataFrame({"src": src, "id": raw["id_prev"], "t": tt, "y": ac, "h": hz, "p": pv,
                   "x": rv, "z": ins, "e": er, "r": rl, "ech": raw["echantillon_iv"].astype(int)})


def lrv(S):
    """S : pandas Series indexee par t_tour (tours presents)."""
    S = S.astype(float)
    tot = float((S ** 2).sum())
    d = S.to_dict()
    for j in range(1, LAGS + 1):
        w = 1 - j / (LAGS + 1)
        tot += 2 * w * sum(v * d[t - j] for t, v in d.items() if (t - j) in d)
    return tot


def demean_h(D, cols):
    out = {}
    for c in cols:
        out[c] = D[c] - D.groupby("h")[c].transform("mean")
    return out


def iv(D, full=True, resid=None):
    if resid is None:
        R = demean_h(D, ["e", "x", "z"])
    else:
        R = resid
    et, xt, zt = R["e"].values, R["x"].values, R["z"].values
    szx = np.sum(zt * xt)
    szz = np.sum(zt * zt)
    res = {"n": len(D)}
    if len(D) < 100 or szx == 0 or szz == 0:
        return {k: 0.0 for k in ["n", "b", "et", "t", "bl", "bh", "pi", "F", "trf", "et_tour", "et_cible", "szx"]}
    b = np.sum(zt * et) / szx
    res["b"] = b
    res["szx"] = szx
    if not full:
        return res
    u = et - b * xt
    S = pd.Series(zt * u, index=D.index).groupby(D["t"].values).sum()
    se = np.sqrt(lrv(S)) / abs(szx)
    res.update(et=se, t=b / se, bl=b - C * se, bh=b + C * se)
    pi = szx / szz
    v = xt - pi * zt
    Sf = pd.Series(zt * v).groupby(D["t"].values).sum()
    se_pi = np.sqrt(lrv(Sf)) / szz
    res.update(pi=pi, F=(pi / se_pi) ** 2)
    rho = np.sum(zt * et) / szz
    w = et - rho * zt
    Sr = pd.Series(zt * w).groupby(D["t"].values).sum()
    res["trf"] = rho / (np.sqrt(lrv(Sr)) / szz)
    res["et_tour"] = np.sqrt(np.sum(S.values ** 2)) / abs(szx)
    Sg = pd.Series(zt * u).groupby(D["y"].values).sum()
    res["et_cible"] = np.sqrt(np.sum(Sg.values ** 2)) / abs(szx)
    return res


def resid_fe(D, cols):
    ids = pd.get_dummies(D["id"]).astype(float).values
    hdum = (D["h"].values == 1).astype(float)[:, None]
    X = np.hstack([ids, hdum])
    out = {}
    for c in cols:
        yv = D[c].values.astype(float)
        beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
        out[c] = pd.Series(yv - X @ beta, index=D.index)
    return out


def ols_dk(D, R):
    et, xt = R["e"].values, R["x"].values
    sxx = np.sum(xt * xt)
    if sxx == 0:
        return 0.0, 0.0, None, 0.0
    b = np.sum(xt * et) / sxx
    S = pd.Series(xt * (et - b * xt)).groupby(D["t"].values).sum()
    return b, np.sqrt(lrv(S)) / sxx, S, sxx


E = df[df.ech == 1].copy()
out = {}
out["n_violations_schema"] = n_violations
out["n_obs_iv"] = len(E)
out["n_previsionnistes_iv"] = E["id"].nunique()
out["n_tours_iv"] = E["t"].nunique()
r = iv(E)
out.update(b_iv=r["b"], et_b_iv_dk8=r["et"], t_iv=r["t"], borne_basse_ic90=r["bl"], borne_haute_ic90=r["bh"])
out["marge_indecision"] = min(-0.15 - r["bl"], r["bh"])
out.update(coef_premiere_etape=r["pi"], f_premiere_etape=r["F"], t_forme_reduite=r["trf"],
           et_b_iv_grappes_tour=r["et_tour"], et_b_iv_grappes_cible=r["et_cible"])
szx_full = r["szx"]

Ep = E[~E.y.isin([2021, 2022, 2023])]
rp = iv(Ep)
out.update(n_obs_iv_hors_2021_2023=len(Ep), b_iv_hors_2021_2023=rp["b"], et_b_iv_hors_2021_2023_dk8=rp["et"],
           borne_haute_ic90_hors_2021_2023=rp["bh"], f_premiere_etape_hors_2021_2023=rp["F"])
out["conflit_episode"] = int(out["borne_haute_ic90"] >= 0 and out["borne_haute_ic90_hors_2021_2023"] < 0)

sans_une = {int(y): iv(E[E.y != y], full=False)["b"] for y in range(2002, 2026)}
out["b_iv_max_sans_une_annee"] = max(sans_une.values())

rfe = iv(E, resid=resid_fe(E, ["e", "x", "z"]))
out["b_iv_ef_prev"] = rfe["b"]
out["et_b_iv_ef_prev_dk8"] = rfe["et"]

Rn = demean_h(E, ["e", "x", "z"])
bm, sem, _, sxx = ols_dk(E, Rn)
out["b_mco_naif"] = bm
out["et_b_mco_naif_dk8"] = sem

cell = [E["t"], E["y"]]
ee = E["e"] - E.groupby(cell)["e"].transform("mean")
xx = E["x"] - E.groupby(cell)["x"].transform("mean")
bi = np.sum(xx * ee) / np.sum(xx * xx)
ui = ee - bi * xx
Si = (xx * ui).groupby(E["t"]).sum()
out["b_intra_tour_naif"] = bi
out["et_b_intra_tour_naif_grappes_tour"] = np.sqrt(np.sum(Si ** 2)) / np.sum(xx * xx)

n = len(E)
out["sigma_bruit_necessaire_mco"] = np.sqrt(max(0, -bm) * sxx / n)
out["sigma_bruit_commun_necessaire_iv"] = np.sqrt(max(0, -out["b_iv"]) * max(0, szx_full / n))

Ea = E[E.y <= 2019]
ra = iv(Ea)
out["n_obs_avant_2020"] = len(Ea)
out["b_iv_avant_2020"] = ra["b"]
out["et_b_iv_avant_2020_dk8"] = ra["et"]
bfe, sefe, _, _ = ols_dk(Ea, resid_fe(Ea, ["e", "x"]))
out["b_mco_ef_avant_2020"] = bfe
out["et_b_mco_ef_avant_2020_dk8"] = sefe

# consensus et BCE
S_ = df[df.src == "SPF"]
Cm = S_.groupby(["t", "y"])["p"].mean()
realise_y = df.dropna(subset=["r"]).groupby("y")["r"].first()
rows = []
for (t_, y_), c_ in Cm.items():
    t_, y_ = int(t_), int(y_)
    yr = t_ // 4  # annee du tour : t = 4*A + q - 1, q-1 dans 0..3
    if not (8008 <= t_ <= 8103 and y_ in (yr, yr + 1) and y_ <= 2025):
        continue
    if (t_ - 1, y_) not in Cm.index or y_ not in realise_y.index:
        continue
    rows.append({"t": t_, "y": y_, "h": y_ - yr, "x": c_ - Cm[(t_ - 1, y_)], "e": realise_y[y_] - c_})
CONS = pd.DataFrame(rows)
B_ = df[(df.src == "BCE")].copy()
B_["yr"] = B_["t"] // 4
BCE = B_[(B_.t >= 8008) & (B_.t <= 8103) & ((B_.y == B_.yr) | (B_.y == B_.yr + 1)) & (B_.y <= 2025)]
BCE = BCE.dropna(subset=["x", "e"])[["t", "y", "h", "x", "e"]].reset_index(drop=True)


def agg_slope(D):
    if len(D) < 20:
        return 0.0, 0.0, None, 0.0
    R = demean_h(D, ["e", "x"])
    return ols_dk(D, R)


bc, sec, Sc, Dc = agg_slope(CONS)
bb, seb, Sb, Db = agg_slope(BCE)
out.update(n_consensus=len(CONS), b_consensus=bc, et_b_consensus_dk8=sec, n_bce=len(BCE), b_bce=bb, et_b_bce_dk8=seb)
out["diff_bce_moins_consensus"] = bb - bc
psi = (Sb / Db).reindex(sorted(set(Sb.index) | set(Sc.index)), fill_value=0) - \
      (Sc / Dc).reindex(sorted(set(Sb.index) | set(Sc.index)), fill_value=0)
out["et_diff_dk8"] = np.sqrt(lrv(psi))
out["b_consensus_hors_2021_2023"] = agg_slope(CONS[~CONS.y.isin([2021, 2022, 2023])].reset_index(drop=True))[0]
out["b_bce_hors_2021_2023"] = agg_slope(BCE[~BCE.y.isin([2021, 2022, 2023])].reset_index(drop=True))[0]

ORDRE = ["n_violations_schema", "n_obs_iv", "n_previsionnistes_iv", "n_tours_iv", "b_iv", "et_b_iv_dk8", "t_iv",
         "borne_basse_ic90", "borne_haute_ic90", "marge_indecision", "coef_premiere_etape", "f_premiere_etape",
         "t_forme_reduite", "et_b_iv_grappes_tour", "et_b_iv_grappes_cible", "n_obs_iv_hors_2021_2023",
         "b_iv_hors_2021_2023", "et_b_iv_hors_2021_2023_dk8", "borne_haute_ic90_hors_2021_2023",
         "f_premiere_etape_hors_2021_2023", "conflit_episode", "b_iv_max_sans_une_annee", "b_iv_ef_prev",
         "et_b_iv_ef_prev_dk8", "b_mco_naif", "et_b_mco_naif_dk8", "b_intra_tour_naif",
         "et_b_intra_tour_naif_grappes_tour", "sigma_bruit_necessaire_mco", "sigma_bruit_commun_necessaire_iv",
         "n_obs_avant_2020", "b_iv_avant_2020", "et_b_iv_avant_2020_dk8", "b_mco_ef_avant_2020",
         "et_b_mco_ef_avant_2020_dk8", "n_consensus", "b_consensus", "et_b_consensus_dk8", "n_bce", "b_bce",
         "et_b_bce_dk8", "diff_bce_moins_consensus", "et_diff_dk8", "b_consensus_hors_2021_2023",
         "b_bce_hors_2021_2023"]
ENTIERS = {"n_violations_schema", "n_obs_iv", "n_previsionnistes_iv", "n_tours_iv", "n_obs_iv_hors_2021_2023",
           "conflit_episode", "n_obs_avant_2020", "n_consensus", "n_bce"}
final = {k: (int(out[k]) if k in ENTIERS else float(out[k])) for k in ORDRE}
(ICI / "verification.json").write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- fragilite (hors verdict, sortie console)
frag = {"controles": {str(k): bool(v) for k, v in checks.items()}, "details_controles": details, "autres": autres}
frag["sans_une_annee"] = {}
for y in range(2002, 2026):
    rr = iv(E[E.y != y])
    frag["sans_une_annee"][y] = {"b": rr["b"], "et": rr["et"], "bl": rr["bl"], "bh": rr["bh"], "F": rr["F"],
                                 "marge": min(-0.15 - rr["bl"], rr["bh"])}
# lecture alternative : pentes agregees hors 2021-2023 avec les moyennes d'horizon de l'echantillon complet
for nom, D in [("consensus", CONS), ("bce", BCE)]:
    R = demean_h(D, ["e", "x"])
    keep = ~D.y.isin([2021, 2022, 2023])
    frag[f"b_{nom}_hors_2021_2023_moyennes_completes"] = float(
        np.sum(R["x"][keep] * R["e"][keep]) / np.sum(R["x"][keep] ** 2))
    bb_, se_, _, _ = agg_slope(D[~D.y.isin([2021, 2022, 2023])].reset_index(drop=True))
    frag[f"et_b_{nom}_hors_2021_2023_dk8"] = se_
for h in (0, 1):
    rr = iv(E[E.h == h])
    frag[f"horizon_{h}"] = {"n": rr["n"], "b": rr["b"], "et": rr["et"], "bl": rr["bl"], "bh": rr["bh"], "F": rr["F"]}
    rr = iv(Ep[Ep.h == h])
    frag[f"horizon_{h}_hors_2021_2023"] = {"n": rr["n"], "b": rr["b"], "et": rr["et"], "bh": rr["bh"], "F": rr["F"]}
frag["hors_2021_2023"] = {"b": rp["b"], "et": rp["et"], "bl": rp["bl"], "bh": rp["bh"], "F": rp["F"],
                          "et_cible": rp["et_cible"], "n_tours": int(Ep.t.nunique())}
frag["avant_2020"] = {"b": ra["b"], "et": ra["et"], "bh": ra["bh"], "F": ra["F"]}
frag["comptes"] = {"n_h0": int((E.h == 0).sum()), "n_h1": int((E.h == 1).sum()),
                   "n_cibles": int(E.y.nunique()), "lignes_par_tour_min_med_max":
                   [int(E.groupby("t").size().min()), float(E.groupby("t").size().median()),
                    int(E.groupby("t").size().max())],
                   "n_bce_h": BCE.h.value_counts().to_dict(), "n_cons_h": CONS.h.value_counts().to_dict()}
print(json.dumps(final, indent=1))
print(json.dumps(frag, indent=1, default=float))
