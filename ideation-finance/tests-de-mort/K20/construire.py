"""K20 — construction du fichier d'analyse K20_analyse.csv (section 5 de la préinscription).

Lit uniquement donnees/ ; écrit K20_analyse.csv ; refait les 12 contrôles de schéma et
imprime les comptes. Usage : python3 -I construire.py
"""
import os
import re
import sys
import warnings

import numpy as np
import pandas as pd
import openpyxl.reader.excel as ex

ex.ExcelReader.read_properties = lambda self: None  # contournement préinscrit (section 4.2)
warnings.filterwarnings("ignore", category=UserWarning)

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "K20_analyse.csv")

VARS = ["PGDP", "RGDP", "UNEMP", "CPI", "TBILL"]
DEBUT = {"PGDP": 7879, "RGDP": 7879, "UNEMP": 7879, "CPI": 7930, "TBILL": 7930}
FIN = 8106
PANDEMIE = (8080, 8087)
EPISODES = {
    "E1": (7879, 7887), "E2": (7895, 7904), "E3": (7920, 7935), "E4": (7962, 7968),
    "E5": (8004, 8011), "E6": (8031, 8041), "E7": (8079, 8095),
}
# (fichier moyen, fichier médian, feuille, nom de colonne pour l'horizon h)
SOURCE_PREV = {
    "PGDP": ("meanGrowth.xlsx", "medianGrowth.xlsx", "PGDP", "dpgdp{}"),
    "RGDP": ("meanGrowth.xlsx", "medianGrowth.xlsx", "RGDP", "drgdp{}"),
    "UNEMP": ("meanLevel.xlsx", "medianLevel.xlsx", "UNEMP", "UNEMP{}"),
    "CPI": ("meanLevel.xlsx", "medianLevel.xlsx", "CPI", "CPI{}"),
    "TBILL": ("meanLevel.xlsx", "medianLevel.xlsx", "TBILL", "TBILL{}"),
}
RTD = {"PGDP": ("pQvQd.xlsx", "P", "P"), "RGDP": ("routputQvQd.xlsx", "ROUTPUT", "ROUTPUT")}
FRED = {"UNEMP": "UNRATE", "CPI": "CPIAUCSL", "TBILL": "TB3MS"}

COLONNES = [
    "variable", "cible", "t_cible", "annee_cible", "t_enquete_h3", "t_enquete_h4",
    "prev_h3", "prev_h4", "nowcast_q4", "prev_h3_med", "prev_h4_med",
    "millesime_realise", "niveau_cible", "niveau_avant", "realise",
    "millesime_realise_q4", "niveau_q4", "niveau_avant_q4", "realise_q4",
    "revision", "erreur", "surprise", "revision_med", "erreur_med",
    "complete", "principal", "episode", "grande_nouvelle",
]
DECIMAUX = ["prev_h3", "prev_h4", "nowcast_q4", "prev_h3_med", "prev_h4_med",
            "niveau_cible", "niveau_avant", "realise", "niveau_q4", "niveau_avant_q4",
            "realise_q4", "revision", "erreur", "surprise", "revision_med", "erreur_med"]
ENTIERS = ["t_cible", "annee_cible", "t_enquete_h3", "t_enquete_h4", "complete", "principal"]
FMT = "%.12f"


def tnum(annee, trimestre):
    return 4 * int(annee) + int(trimestre) - 1


def nom_trim(t):
    return f"{t // 4}-Q{t % 4 + 1}"


def num_millesime(code, prefixe):
    m = re.fullmatch(prefixe + r"(\d\d)Q([1-4])", code)
    if not m:
        return None
    aa = int(m.group(1))
    annee = 1900 + aa if aa >= 60 else 2000 + aa
    return 4 * annee + int(m.group(2)) - 1


def arrondi(x):
    """Valeur telle qu'elle sera écrite dans le fichier (FMT)."""
    return np.nan if pd.isna(x) else float(FMT % x)


# ---------------------------------------------------------------- lectures
def lire_enquete(fichier, feuille, gabarit):
    d = pd.read_excel(os.path.join(DON, fichier), sheet_name=feuille)
    d["t"] = [tnum(a, q) for a, q in zip(d["YEAR"], d["QUARTER"])]
    d = d.set_index("t")
    out = {}
    for h in (2, 5, 6):
        out[h] = pd.to_numeric(d[gabarit.format(h)], errors="coerce").to_dict()
    return out


def lire_rtd(fichier, feuille, prefixe):
    d = pd.read_excel(os.path.join(DON, fichier), sheet_name=feuille)
    d["t"] = [tnum(s[:4], s[-1]) for s in d["DATE"].astype(str)]
    d = d.set_index("t")
    mill = []
    for col in d.columns:
        if col in ("DATE",):
            continue
        n = num_millesime(str(col), prefixe)
        if n is not None:
            mill.append((n, str(col)))
    mill.sort()
    vals = {code: pd.to_numeric(d[code], errors="coerce") for _, code in mill}
    return mill, vals


def premiere_publication(t, mill, vals):
    """Premier millésime de numéro > t où les lignes t et t-1 sont remplies."""
    for n, code in mill:
        if n <= t:
            continue
        s = vals[code]
        if t in s.index and (t - 1) in s.index and pd.notna(s.get(t)) and pd.notna(s.get(t - 1)):
            niv, avant = float(s[t]), float(s[t - 1])
            return code, niv, avant, 100.0 * ((niv / avant) ** 4 - 1.0)
    return None, np.nan, np.nan, np.nan


def lire_fred(serie):
    d = pd.read_csv(os.path.join(DON, serie + ".csv"), dtype=str)
    d.columns = ["date", "valeur"]
    d["valeur"] = pd.to_numeric(d["valeur"].replace(".", np.nan), errors="coerce")
    d["date"] = pd.to_datetime(d["date"])
    d["t"] = [tnum(x.year, (x.month - 1) // 3 + 1) for x in d["date"]]
    moy = {}
    for t, g in d.groupby("t"):
        v = g["valeur"].to_numpy()
        moy[t] = float(np.mean(v)) if len(v) == 3 and not np.isnan(v).any() else np.nan
    return moy


def realise_fred(var, t, moy):
    niv = moy.get(t, np.nan)
    if var == "CPI":
        avant = moy.get(t - 1, np.nan)
        a = 100.0 * ((niv / avant) ** 4 - 1.0) if pd.notna(niv) and pd.notna(avant) else np.nan
    else:
        avant = np.nan
        a = niv
    code = "FRED" if pd.notna(a) else ""
    return code, niv, avant, a


# ---------------------------------------------------------------- construction
def construire():
    lignes = []
    for v in VARS:
        fm, fmed, feuille, gab = SOURCE_PREV[v]
        moy = lire_enquete(fm, feuille, gab)
        med = lire_enquete(fmed, feuille, gab)
        if v in RTD:
            mill, vals = lire_rtd(*RTD[v])
            real = lambda t: premiere_publication(t, mill, vals)  # noqa: E731
        else:
            fr = lire_fred(FRED[v])
            real = lambda t, fr=fr, v=v: realise_fred(v, t, fr)  # noqa: E731
        for t in range(DEBUT[v], FIN + 1):
            r = {"variable": v, "cible": nom_trim(t), "t_cible": t, "annee_cible": t // 4,
                 "t_enquete_h3": t - 3, "t_enquete_h4": t - 4}
            r["prev_h3"] = moy[5].get(t - 3, np.nan)
            r["prev_h4"] = moy[6].get(t - 4, np.nan)
            r["nowcast_q4"] = moy[2].get(t - 4, np.nan)
            r["prev_h3_med"] = med[5].get(t - 3, np.nan)
            r["prev_h4_med"] = med[6].get(t - 4, np.nan)
            code, niv, avant, a = real(t)
            r.update(millesime_realise=code or "", niveau_cible=niv, niveau_avant=avant, realise=a)
            code4, niv4, avant4, a4 = real(t - 4)
            r.update(millesime_realise_q4=code4 or "", niveau_q4=niv4, niveau_avant_q4=avant4,
                     realise_q4=a4)
            if v in RTD and pd.isna(a):
                r["millesime_realise"] = ""
            if v in RTD and pd.isna(a4):
                r["millesime_realise_q4"] = ""
            lignes.append(r)
    d = pd.DataFrame(lignes)
    for c in ["prev_h3", "prev_h4", "nowcast_q4", "prev_h3_med", "prev_h4_med", "niveau_cible",
              "niveau_avant", "realise", "niveau_q4", "niveau_avant_q4", "realise_q4"]:
        d[c] = d[c].astype(float).map(arrondi)
    d["revision"] = (d["prev_h3"] - d["prev_h4"]).map(arrondi)
    d["erreur"] = (d["realise"] - d["prev_h3"]).map(arrondi)
    d["surprise"] = (d["realise_q4"] - d["nowcast_q4"]).map(arrondi)
    d["revision_med"] = (d["prev_h3_med"] - d["prev_h4_med"]).map(arrondi)
    d["erreur_med"] = (d["realise"] - d["prev_h3_med"]).map(arrondi)
    d["complete"] = (d[["revision", "erreur", "surprise"]].notna().all(axis=1)).astype(int)
    pand = d["variable"].isin(["RGDP", "UNEMP"]) & d["t_cible"].between(*PANDEMIE)
    d["principal"] = ((d["complete"] == 1) & ~pand).astype(int)
    d["episode"] = ""
    for k, (a, b) in EPISODES.items():
        d.loc[d["t_cible"].between(a, b), "episode"] = k
    d["grande_nouvelle"] = pd.array([pd.NA] * len(d), dtype="Int64")
    for v in VARS:
        mp = (d["variable"] == v) & (d["principal"] == 1)
        q = np.quantile(np.abs(d.loc[mp, "surprise"].to_numpy()), 2 / 3)
        ms = (d["variable"] == v) & d["surprise"].notna()
        d.loc[ms, "grande_nouvelle"] = (np.abs(d.loc[ms, "surprise"]) > q).astype(int).to_numpy()
    return d[COLONNES]


def ecrire(d):
    d.to_csv(SORTIE, index=False, float_format=FMT, encoding="utf-8", lineterminator="\n")


# ---------------------------------------------------------------- contrôles (section 5)
PLAGES_TAUX = {"PGDP": (-10, 25), "RGDP": (-40, 40), "UNEMP": (2, 16), "CPI": (-15, 25),
               "TBILL": (-0.5, 20)}
PLAGES_NIV = {"PGDP": (50, 300), "RGDP": (500, 40000), "CPI": (20, 400),
              "UNEMP": (2, 16), "TBILL": (-0.5, 20)}
TOL = 1e-6


def lire_fichier(chemin=SORTIE):
    return pd.read_csv(chemin, dtype={"variable": str, "cible": str, "millesime_realise": str,
                                      "millesime_realise_q4": str, "episode": str},
                       keep_default_na=False, na_values={c: [""] for c in DECIMAUX + ENTIERS
                                                        + ["grande_nouvelle"]})


def _vide(s):
    return s.isna() | (s.astype(str) == "")


def controles(d, lecture_9="appariement"):
    """Renvoie {numéro: liste de messages} ; un contrôle est violé si sa liste est non vide.

    lecture_9 = "appariement" (littérale : niveau_avant présent quand niveau_cible l'est ;
    niveau_avant_q4 quand niveau_q4 l'est) ou "trimestre_precedent" (niveau_avant présent quand
    le niveau du trimestre précédent existe dans la source) — voir ecarts.md.
    """
    err = {k: [] for k in range(1, 13)}
    # 1 colonnes
    if list(d.columns) != COLONNES:
        err[1].append(f"colonnes {list(d.columns)}")
    # 2 grille
    attendu = [(v, t) for v in VARS for t in range(DEBUT[v], FIN + 1)]
    obs = list(zip(d["variable"], d["t_cible"]))
    if len(d) != 1038 or obs != attendu:
        err[2].append(f"grille : {len(d)} lignes, conforme={obs == attendu}")
    # 3 identifiants
    for i, r in d.iterrows():
        t = int(r["t_cible"])
        if r["cible"] != nom_trim(t) or int(r["annee_cible"]) != t // 4 \
                or int(r["t_enquete_h3"]) != t - 3 or int(r["t_enquete_h4"]) != t - 4:
            err[3].append(f"ligne {i}")
    # 4 présence des prévisions
    manq = {(v, nom_trim(t)) for v in ["PGDP", "RGDP", "UNEMP"]
            for t in [tnum(1970, 1), tnum(1970, 2), tnum(1970, 3), tnum(1971, 1), tnum(1975, 3)]}
    for i, r in d.iterrows():
        cle = (r["variable"], r["cible"])
        for c in ("prev_h4", "prev_h4_med"):
            if pd.isna(r[c]) != (cle in manq):
                err[4].append(f"{cle} {c}")
        for c in ("prev_h3", "prev_h3_med", "nowcast_q4"):
            if pd.isna(r[c]):
                err[4].append(f"{cle} {c} vide")
    # 5 millésimes
    retard = {nom_trim(t) for t in [tnum(1995, 4), tnum(2025, 3), tnum(2025, 4)]}
    retard_q4 = {nom_trim(t) for t in [tnum(1996, 4), tnum(2026, 3)]}
    for i, r in d.iterrows():
        v, t = r["variable"], int(r["t_cible"])
        for col, rc, tt, ret in (("millesime_realise", "realise", t, retard),
                                 ("millesime_realise_q4", "realise_q4", t - 4, retard_q4)):
            code = r[col] if isinstance(r[col], str) else ""
            if v in RTD:
                if pd.notna(r[rc]):
                    n = num_millesime(code, RTD[v][2])
                    att = tt + (2 if r["cible"] in ret else 1)
                    if n is None or n != att:
                        err[5].append(f"{v} {r['cible']} {col}={code}")
                elif code != "":
                    err[5].append(f"{v} {r['cible']} {col} non vide sans réalisé")
            else:
                if pd.notna(r[rc]) and code != "FRED":
                    err[5].append(f"{v} {r['cible']} {col}={code}")
                if pd.isna(r[rc]) and code != "":
                    err[5].append(f"{v} {r['cible']} {col} non vide sans réalisé")
    # 6 plages
    for i, r in d.iterrows():
        v = r["variable"]
        lo, hi = PLAGES_TAUX[v]
        for c in ("prev_h3", "prev_h4", "nowcast_q4", "prev_h3_med", "prev_h4_med", "realise",
                  "realise_q4"):
            if pd.notna(r[c]) and not (lo <= r[c] <= hi):
                err[6].append(f"{v} {r['cible']} {c}={r[c]}")
        lo, hi = PLAGES_NIV[v]
        for c in ("niveau_cible", "niveau_avant", "niveau_q4", "niveau_avant_q4"):
            if pd.notna(r[c]) and not (lo <= r[c] <= hi):
                err[6].append(f"{v} {r['cible']} {c}={r[c]}")
    # 7 formules
    for i, r in d.iterrows():
        v = r["variable"]
        for rc, nc, ac in (("realise", "niveau_cible", "niveau_avant"),
                           ("realise_q4", "niveau_q4", "niveau_avant_q4")):
            if v in ("PGDP", "RGDP", "CPI"):
                comp_vide = pd.isna(r[nc]) or pd.isna(r[ac])
                f = np.nan if comp_vide else 100 * ((r[nc] / r[ac]) ** 4 - 1)
            else:
                comp_vide = pd.isna(r[nc])
                f = r[nc]
            if pd.isna(r[rc]) != comp_vide or (not comp_vide and abs(r[rc] - f) > TOL):
                err[7].append(f"{v} {r['cible']} {rc}")
        for res, a, b in (("revision", "prev_h3", "prev_h4"), ("erreur", "realise", "prev_h3"),
                          ("surprise", "realise_q4", "nowcast_q4"),
                          ("revision_med", "prev_h3_med", "prev_h4_med"),
                          ("erreur_med", "realise", "prev_h3_med")):
            ov = pd.isna(r[a]) or pd.isna(r[b])
            if pd.isna(r[res]) != ov or (not ov and abs(r[res] - (r[a] - r[b])) > TOL):
                err[7].append(f"{v} {r['cible']} {res}")
    # 8 cohérence entre lignes
    idx = {(r["variable"], int(r["t_cible"])): r for _, r in d.iterrows()}
    for (v, t), r in idx.items():
        if (v, t - 4) in idx:
            p = idx[(v, t - 4)]
            if pd.notna(r["realise_q4"]) and pd.notna(p["realise"]) \
                    and abs(r["realise_q4"] - p["realise"]) > TOL:
                err[8].append(f"{v} {r['cible']} realise_q4")
            c1, c2 = r["millesime_realise_q4"], p["millesime_realise"]
            if isinstance(c1, str) and c1 and isinstance(c2, str) and c2 and c1 != c2:
                err[8].append(f"{v} {r['cible']} millesime")
    # 9 niveaux
    for i, r in d.iterrows():
        v = r["variable"]
        if v in ("UNEMP", "TBILL"):
            if pd.notna(r["niveau_avant"]) or pd.notna(r["niveau_avant_q4"]):
                err[9].append(f"{v} {r['cible']} niveau_avant non vide")
        else:
            for ac, nc, decal in (("niveau_avant", "niveau_cible", 0),
                                  ("niveau_avant_q4", "niveau_q4", 4)):
                if lecture_9 == "appariement":
                    exige = pd.notna(r[nc])
                else:  # niveau du trimestre précédent disponible dans la source
                    exige = _niveau_precedent_existe(v, int(r["t_cible"]) - decal, r[nc])
                if exige and pd.isna(r[ac]):
                    err[9].append(f"{v} {r['cible']} {ac} vide alors que {nc} présent")
    # 10 indicateurs
    comp = d[["revision", "erreur", "surprise"]].notna().all(axis=1).astype(int)
    pand = d["variable"].isin(["RGDP", "UNEMP"]) & d["t_cible"].between(*PANDEMIE)
    princ = ((comp == 1) & ~pand).astype(int)
    if not (d["complete"].astype(int) == comp).all() or not (d["principal"].astype(int) == princ).all():
        err[10].append("indicateurs")
    # 11 épisodes
    for i, r in d.iterrows():
        att = ""
        for k, (a, b) in EPISODES.items():
            if a <= int(r["t_cible"]) <= b:
                att = k
        if (r["episode"] if isinstance(r["episode"], str) else "") != att:
            err[11].append(f"{r['variable']} {r['cible']}")
    # 12 grande nouvelle
    for v in VARS:
        mp = (d["variable"] == v) & (d["principal"] == 1)
        q = np.quantile(np.abs(d.loc[mp, "surprise"].to_numpy(dtype=float)), 2 / 3)
        for i in d.index[d["variable"] == v]:
            s, g = d.at[i, "surprise"], d.at[i, "grande_nouvelle"]
            if pd.isna(s) != pd.isna(g):
                err[12].append(f"{v} ligne {i} présence")
            elif pd.notna(s) and int(g) != int(abs(s) > q):
                err[12].append(f"{v} ligne {i} valeur")
    return err


_FRED_CACHE = {}


def _niveau_precedent_existe(v, t, niveau):
    """Lecture alternative du contrôle 9 : le niveau du trimestre t-1 existe-t-il dans la source ?"""
    if v in RTD:
        return pd.notna(niveau)  # même millésime : t et t-1 remplis par construction
    if v not in _FRED_CACHE:
        _FRED_CACHE[v] = lire_fred(FRED[v])
    return pd.notna(niveau) and pd.notna(_FRED_CACHE[v].get(t - 1, np.nan))


def main():
    d = construire()
    ecrire(d)
    f = lire_fichier()
    print("lignes", len(f), "colonnes", f.shape[1])
    tab = f.groupby("variable", sort=False).agg(lignes=("t_cible", "size"),
                                                 complete=("complete", "sum"),
                                                 principal=("principal", "sum"))
    print(tab, "\ntotal", tab.sum().to_dict())
    p = f[f["principal"] == 1]
    print("trimestres principaux distincts", p["t_cible"].nunique())
    print("principal par épisode", p["episode"].replace("", "hors").value_counts().sort_index().to_dict())
    # manquants
    for c in ("realise", "realise_q4", "prev_h4", "surprise"):
        m = f[f[c].isna()]
        print("vide", c, list(zip(m["variable"], m["cible"])))
    err = controles(f)
    n = sum(1 for k in err if err[k])
    for k in err:
        print(f"contrôle {k}: {'VIOLÉ' if err[k] else 'ok'}", err[k][:10])
    print("n_violations_schema (lecture littérale)", n)
    err2 = controles(f, lecture_9="trimestre_precedent")
    print("n_violations_schema (lecture alternative du contrôle 9)",
          sum(1 for k in err2 if err2[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
