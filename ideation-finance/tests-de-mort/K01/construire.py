"""K01 — construction du fichier d'analyse K01_analyse.csv à partir de donnees/ seul.

Suit la préinscription (sections 5 et 6) : sources, filtres, 22 colonnes dans l'ordre, tri, 12 contrôles de schéma.
Imprime les effectifs à chaque filtre et écrit construire_controles.json (contrôles et comptes).
Aucune statistique de résultat n'est calculée ici.
"""
import io
import json
import os
import re
import sys
import zipfile
from decimal import Decimal

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "K01_analyse.csv")
CONTROLES = os.path.join(ICI, "construire_controles.json")

COLONNES = ["source", "id_prev", "tour", "t_tour", "millesime", "statut", "mois_titre", "annee_titre",
            "annee_cible", "horizon", "rang", "prevision", "prevision_prec", "revision", "autre_cible",
            "prevision_autre", "prevision_autre_prec", "instrument", "realise", "erreur",
            "nb_tours_complets", "echantillon_iv"]
TYPES_SPF = ["A_YEAR_0_AHEAD", "A_YEAR_1_AHEAD", "A_YEAR_2_AHEAD"]
LETTRE_TRIM = {"W": 1, "G": 2, "S": 3, "A": 4}
MILLESIMES = ["A01"] + [f"{l}{a % 100:02d}" for a in range(2002, 2026) for l in "WGSA"]
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"]
T_MIN, T_MAX = 8007, 8103          # 2001Q4 … 2025Q4
DERNIERE_CIBLE_REALISEE = 2025


def t_de_tour(tour):
    m = re.fullmatch(r"(\d{4})Q([1-4])", tour)
    return 4 * int(m.group(1)) + int(m.group(2)) - 1


# ----------------------------------------------------------------------------- écriture des nombres
def fmt_diff(v):
    """Différence écrite sans arrondi (représentation décimale la plus courte qui redonne le double exact),
    complétée à au moins 6 décimales."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    s = format(Decimal(repr(float(v))), "f")
    if "." not in s:
        s += "."
    entier, dec = s.split(".")
    if len(dec) < 6:
        dec = dec + "0" * (6 - len(dec))
    return f"{entier}.{dec}"


def fmt_int(v):
    if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NA:
        return ""
    return str(int(v))


# ----------------------------------------------------------------------------- lecture des sources
def lire_spf(journal_filtres):
    with zipfile.ZipFile(os.path.join(DONNEES, "SPF_microdata_by_variable.zip")) as z:
        brut = z.read("1_HICP.csv")          # copie à la racine de l'archive
    d = pd.read_csv(io.BytesIO(brut), dtype=str, keep_default_na=False)
    journal_filtres["spf_lignes_1_HICP"] = len(d)
    d = d[d["table_name"] == "Point"]
    journal_filtres["spf_point"] = len(d)
    d = d[d["forecaster_id"].str.fullmatch(r"\d+")]
    journal_filtres["spf_point_id_numerique"] = len(d)
    d = d[d["target_period_type"].isin(TYPES_SPF)]
    journal_filtres["spf_point_id_numerique_types_annuels"] = len(d)
    d = d.assign(t_tour=d["ref_round"].map(t_de_tour))
    d = d[(d["t_tour"] >= T_MIN) & (d["t_tour"] <= T_MAX)]
    journal_filtres["spf_fenetre_2001Q4_2025Q4"] = len(d)
    out = pd.DataFrame({
        "source": "SPF",
        "id_prev": d["forecaster_id"].values,
        "tour": d["ref_round"].values,
        "t_tour": d["t_tour"].values,
        "millesime": "", "statut": "", "mois_titre": np.nan, "annee_titre": np.nan,
        "annee_cible": d["target_period"].astype(int).values,
        "prevision_txt": d["value"].values,
    })
    return out


def lire_bce(journal_filtres):
    lignes = []
    for code in MILLESIMES:
        f = os.path.join(DONNEES, f"MPD_A.U2.HIC.A.{code}.0000.csv")
        b = pd.read_csv(f, dtype=str, keep_default_na=False)
        annee = 2000 + int(code[1:])
        trim = LETTRE_TRIM[code[0]]
        titre = b["TITLE_COMPL"].iloc[0] if len(b) else ""
        noms = re.findall(r"\b(" + "|".join(MOIS) + r")\b", titre)
        ans = re.findall(r"(?<!\d)(\d{4})(?!\d)", titre)
        b = b[b["TIME_PERIOD"].astype(int).isin([annee, annee + 1, annee + 2]) & (b["OBS_STATUS"] == "F")]
        for _, r in b.iterrows():
            lignes.append({
                "source": "BCE", "id_prev": "BCE", "tour": f"{annee}Q{trim}", "t_tour": 4 * annee + trim - 1,
                "millesime": code, "statut": r["OBS_STATUS"],
                "mois_titre": MOIS.index(noms[-1]) + 1 if noms else np.nan,
                "annee_titre": int(ans[-1]) if ans else np.nan,
                "annee_cible": int(r["TIME_PERIOD"]), "prevision_txt": r["OBS_VALUE"],
            })
    out = pd.DataFrame(lignes)
    journal_filtres["bce_lignes_Y_Y1_Y2_statut_F"] = len(out)
    return out


def lire_eurostat():
    e = pd.read_csv(os.path.join(DONNEES, "prc_hicp_ainr_A.RCH_A_AVG.TOTAL.EA.csv"), dtype=str,
                    keep_default_na=False)
    e = e[(e["unit"] == "RCH_A_AVG") & (e["coicop18"] == "TOTAL") & (e["geo"] == "EA") & (e["freq"] == "A")]
    return {int(a): v for a, v in zip(e["TIME_PERIOD"], e["OBS_VALUE"]) if v != ""}


# ----------------------------------------------------------------------------- construction
def construire():
    jf = {}
    spf = lire_spf(jf)
    bce = lire_bce(jf)
    real = lire_eurostat()
    d = pd.concat([spf, bce], ignore_index=True)
    d["prevision"] = d["prevision_txt"].astype(float)
    annee_tour = d["tour"].str[:4].astype(int)
    d["horizon"] = d["annee_cible"] - annee_tour
    d["rang"] = d["t_tour"] - 4 * (d["annee_cible"] - 1) + 1

    cle = d.set_index(["source", "id_prev", "t_tour", "annee_cible"])["prevision"]
    assert cle.index.is_unique

    def chercher(t, cible):
        idx = pd.MultiIndex.from_arrays([d["source"], d["id_prev"], t, cible])
        return np.array(cle.reindex(idx).to_numpy(), dtype=float, copy=True)

    prec = chercher(d["t_tour"] - 1, d["annee_cible"])
    prec[d["t_tour"].to_numpy() == T_MIN] = np.nan
    d["prevision_prec"] = prec
    d["revision"] = d["prevision"] - d["prevision_prec"]

    autre = np.where(d["horizon"] == 0, d["annee_cible"] + 1,
                     np.where(d["horizon"] == 1, d["annee_cible"] - 1, -1))
    d["autre_cible"] = pd.array(np.where(autre == -1, pd.NA, autre), dtype="Int64")
    autre_s = pd.Series(autre)
    pa = chercher(d["t_tour"], autre_s)
    pa[autre == -1] = np.nan
    pap = chercher(d["t_tour"] - 1, autre_s)
    pap[(autre == -1) | (d["t_tour"].to_numpy() == T_MIN)] = np.nan
    d["prevision_autre"] = pa
    d["prevision_autre_prec"] = pap
    d["instrument"] = d["prevision_autre"] - d["prevision_autre_prec"]

    d["realise_txt"] = [real.get(int(y), "") if y <= DERNIERE_CIBLE_REALISEE else "" for y in d["annee_cible"]]
    d["realise"] = pd.to_numeric(d["realise_txt"].replace("", np.nan))
    d["erreur"] = d["realise"] - d["prevision"]

    complet = ((d["source"] == "SPF") & d["horizon"].isin([0, 1]) & (d["t_tour"] >= 8008) & (d["t_tour"] <= T_MAX)
               & d["revision"].notna() & d["instrument"].notna() & d["erreur"].notna())
    nb = d[complet].groupby("id_prev")["t_tour"].nunique()
    d["nb_tours_complets"] = np.where(d["source"] == "SPF", d["id_prev"].map(nb).fillna(0), np.nan)
    d["echantillon_iv"] = (complet & (d["nb_tours_complets"] >= 8)).astype(int)

    d = d.sort_values(["source", "id_prev", "t_tour", "annee_cible"], kind="mergesort").reset_index(drop=True)

    sortie = pd.DataFrame({
        "source": d["source"], "id_prev": d["id_prev"], "tour": d["tour"],
        "t_tour": d["t_tour"].map(fmt_int),
        "millesime": d["millesime"], "statut": d["statut"],
        "mois_titre": d["mois_titre"].map(fmt_int), "annee_titre": d["annee_titre"].map(fmt_int),
        "annee_cible": d["annee_cible"].map(fmt_int), "horizon": d["horizon"].map(fmt_int),
        "rang": d["rang"].map(fmt_int),
        "prevision": d["prevision_txt"],
        "prevision_prec": d["prevision_prec"].map(fmt_diff),
        "revision": d["revision"].map(fmt_diff),
        "autre_cible": d["autre_cible"].map(fmt_int),
        "prevision_autre": d["prevision_autre"].map(fmt_diff),
        "prevision_autre_prec": d["prevision_autre_prec"].map(fmt_diff),
        "instrument": d["instrument"].map(fmt_diff),
        "realise": d["realise_txt"],
        "erreur": d["erreur"].map(fmt_diff),
        "nb_tours_complets": d["nb_tours_complets"].map(fmt_int),
        "echantillon_iv": d["echantillon_iv"].map(fmt_int),
    })[COLONNES]
    sortie.to_csv(SORTIE, index=False, encoding="utf-8", lineterminator="\n")
    return jf


# ----------------------------------------------------------------------------- contrôles de schéma
def controles(chemin=SORTIE):
    """Refait les 12 contrôles de la section 6 sur le fichier écrit. Renvoie {n°: (ok, détail)}."""
    with open(chemin, encoding="utf-8") as f:
        entete = f.readline().rstrip("\n").split(",")
    s = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    r = {}

    def num(col):
        return pd.to_numeric(s[col].replace("", np.nan))

    spf = s["source"] == "SPF"
    bce = s["source"] == "BCE"
    t = num("t_tour")
    cible = num("annee_cible")
    hor = num("horizon")
    prev = num("prevision")

    # 1 colonnes
    r[1] = (entete == COLONNES, f"{len(entete)} colonnes")
    # 2 clé
    dup = s.duplicated(["source", "id_prev", "t_tour", "annee_cible"]).sum()
    src_ok = s["source"].isin(["SPF", "BCE"]).all()
    id_ok = (s.loc[spf, "id_prev"].str.fullmatch(r"\d{3}").all() and (s.loc[bce, "id_prev"] == "BCE").all())
    r[2] = (bool(dup == 0 and src_ok and id_ok), f"doublons {dup}")
    # 3 tours
    fm = s["tour"].str.fullmatch(r"\d{4}Q[1-4]")
    t_calc = s["tour"].str[:4].astype(int) * 4 + s["tour"].str[5].astype(int) - 1 if fm.all() else None
    ok3 = bool(fm.all() and (t_calc == t).all() and t.between(T_MIN, T_MAX).all()
               and set(t[spf].astype(int)) == set(range(T_MIN, T_MAX + 1))
               and set(t[bce].astype(int)) == set(range(T_MIN, T_MAX + 1)))
    r[3] = (ok3, f"tours SPF {t[spf].nunique()}, BCE {t[bce].nunique()}")
    # 4 cibles
    an_tour = s["tour"].str[:4].astype(int)
    rang_calc = t - 4 * (cible - 1) + 1
    ok4 = bool((hor == cible - an_tour).all() and hor.isin([0, 1, 2]).all() and (num("rang") == rang_calc).all())
    r[4] = (ok4, "")
    # 5 millésimes
    b = s[bce]
    ok5 = True
    for c in ["millesime", "statut", "mois_titre", "annee_titre"]:
        ok5 &= bool((b[c] != "").all()) and bool((s.loc[spf, c] == "").all())
    if ok5:
        trim = b["millesime"].str[0].map(LETTRE_TRIM)
        an = 2000 + b["millesime"].str[1:].astype(int)
        ok5 &= bool((trim == b["tour"].str[5].astype(int)).all() and (an == b["tour"].str[:4].astype(int)).all())
        ok5 &= bool((b["mois_titre"].astype(int) == 3 * trim).all() and (b["annee_titre"].astype(int) == an).all())
        vc = b["millesime"].value_counts()
        ok5 &= bool(set(vc.index) == set(MILLESIMES) and (vc == 3).all())
    r[5] = (bool(ok5), f"{b['millesime'].nunique()} millésimes, {len(b)} lignes")
    # 6 statut
    r[6] = (bool((b["statut"] == "F").all()), "")
    # 7 valeurs
    real = s["realise"]
    ok7 = bool((s["prevision"] != "").all() and prev.between(-5, 15).all())
    vide_ssi = ((real == "") == (cible > DERNIERE_CIBLE_REALISEE)).all()
    rv = pd.to_numeric(real[real != ""])
    ok7 &= bool(vide_ssi and rv.between(-5, 15).all()
                and real[real != ""].str.fullmatch(r"-?\d+(\.\d)?").all())
    r[7] = (ok7, "")
    # index de recherche
    cle = dict(zip(zip(s["source"], s["id_prev"], t.astype(int), cible.astype(int)), prev))

    def attendu(tt, cc):
        return [cle.get((so, i, int(a), int(c)), np.nan) if not (pd.isna(a) or pd.isna(c)) else np.nan
                for so, i, a, c in zip(s["source"], s["id_prev"], tt, cc)]

    def egal(col, att):
        v = num(col).to_numpy()
        att = np.asarray(att, dtype=float)
        return bool(np.all((np.isnan(v) & np.isnan(att)) | (np.abs(v - att) <= 1e-12)))

    # 8 prévision précédente
    att8 = np.array(attendu(t - 1, cible), dtype=float)
    att8[(t == T_MIN).to_numpy()] = np.nan
    r[8] = (egal("prevision_prec", att8), "")
    # 9 autre cible
    ac_att = np.where(hor == 0, cible + 1, np.where(hor == 1, cible - 1, np.nan))
    ac = num("autre_cible").to_numpy()
    ok9 = bool(np.all((np.isnan(ac) & np.isnan(ac_att)) | (ac == ac_att)))
    att_a = np.array(attendu(t, pd.Series(ac_att)), dtype=float)
    att_ap = np.array(attendu(t - 1, pd.Series(ac_att)), dtype=float)
    att_ap[(t == T_MIN).to_numpy()] = np.nan
    ok9 &= egal("prevision_autre", att_a) and egal("prevision_autre_prec", att_ap)
    r[9] = (bool(ok9), "")
    # 10 calculs
    ok10 = True
    for col, a, bb in [("revision", "prevision", "prevision_prec"), ("instrument", "prevision_autre",
                                                                     "prevision_autre_prec"),
                       ("erreur", "realise", "prevision")]:
        v, va, vb = num(col), num(a), num(bb)
        vide_att = va.isna() | vb.isna()
        ok10 &= bool((v.isna() == vide_att).all())
        diff = (v - (va - vb)).abs()
        ok10 &= bool((diff[~vide_att] <= 1e-9).all())
    r[10] = (bool(ok10), "")
    # 11 réalisé unique par année cible
    r[11] = (bool((s.groupby("annee_cible")["realise"].nunique(dropna=False) <= 1).all()), "")
    # 12 échantillon
    rev, ins, err = num("revision"), num("instrument"), num("erreur")
    comp = spf & hor.isin([0, 1]) & t.between(8008, T_MAX) & rev.notna() & ins.notna() & err.notna()
    nb = s[comp].groupby("id_prev")["t_tour"].nunique()
    nb_att = s["id_prev"].map(nb).fillna(0).where(spf)
    nb_lu = num("nb_tours_complets")
    ok12 = bool(((nb_lu.isna() & nb_att.isna()) | (nb_lu == nb_att)).all())
    ech_att = (comp & (nb_att >= 8)).astype(int)
    ok12 &= bool((s["echantillon_iv"] == ech_att.astype(str)).all())
    r[12] = (ok12, "")
    return r


def comptes(chemin=SORTIE):
    s = pd.read_csv(chemin, dtype={"id_prev": str, "millesime": str, "statut": str})
    spf = s[s["source"] == "SPF"]
    c = {"lignes_SPF": len(spf), "lignes_BCE": int((s["source"] == "BCE").sum())}
    base = spf[spf["horizon"].isin([0, 1]) & spf["t_tour"].between(8008, 8103) & (spf["annee_cible"] <= 2025)]
    c["spf_h01_tours_2002_2025_cible_le_2025"] = len(base)
    c["dont_avec_revision"] = int(base["revision"].notna().sum())
    rx = base[base["revision"].notna() & base["instrument"].notna()]
    c["dont_avec_revision_et_instrument"] = len(rx)
    c["identifiants_revision_et_instrument"] = int(rx["id_prev"].nunique())
    e = s[s["echantillon_iv"] == 1]
    c["echantillon_iv_lignes"] = len(e)
    c["echantillon_iv_previsionnistes"] = int(e["id_prev"].nunique())
    c["echantillon_iv_tours"] = int(e["t_tour"].nunique())
    c["echantillon_iv_annees_cibles"] = int(e["annee_cible"].nunique())
    c["echantillon_iv_horizon0"] = int((e["horizon"] == 0).sum())
    c["echantillon_iv_horizon1"] = int((e["horizon"] == 1).sum())
    pt = e.groupby("t_tour").size()
    c["lignes_par_tour_min_mediane_max"] = [int(pt.min()), float(pt.median()), int(pt.max())]
    h = e[~e["annee_cible"].isin([2021, 2022, 2023])]
    c["hors_2021_2023_lignes"] = len(h)
    c["hors_2021_2023_tours"] = int(h["t_tour"].nunique())
    c["cibles_2002_2019_lignes"] = int((e["annee_cible"] <= 2019).sum())
    c["identifiants_retires_par_regle_8_tours"] = int(rx["id_prev"].nunique() - e["id_prev"].nunique())
    c["lignes_retirees_par_regle_8_tours"] = int(len(rx) - len(e))
    return c


def main():
    jf = construire()
    r = controles()
    n_viol = sum(1 for ok, _ in r.values() if not ok)
    c = comptes()
    res = {"effectifs_aux_filtres": jf, "comptes": c,
           "controles": {str(k): {"ok": bool(ok), "detail": det} for k, (ok, det) in r.items()},
           "n_violations_schema": n_viol}
    with open(CONTROLES, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
