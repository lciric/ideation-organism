#!/usr/bin/env python3
"""F01 — construction de panel.csv a partir de donnees/ seulement.

Suit le preenregistrement scelle (sections 3 et 4). Ne telecharge rien.
Usage : python3 -I construire.py
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
F_DOC = os.path.join(DONNEES, "SignalDoc.csv")
F_RET = os.path.join(DONNEES, "PredictorLSretWide.parquet")
F_PANEL = os.path.join(ICI, "panel.csv")
F_JOURNAL = os.path.join(ICI, "construction.json")

TAILLES_ATTENDUES = {F_DOC: 183100, F_RET: 1439671}
COLONNES = ["signal", "date", "annee", "ret", "annee_pub", "annee_debut_ech",
            "annee_fin_ech", "statut", "dans_fenetre", "moy_origine"]
AN_MIN, AN_MAX = 1974, 2013
MIN_ORIGINE = 60


def sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def statut_regle(annee, D, F, P):
    """Regle du tableau du § 4, vectorisee."""
    annee, D, F, P = map(np.asarray, (annee, D, F, P))
    s = np.full(annee.shape, "", dtype=object)
    s[annee < D] = "avant"
    s[(annee >= D) & (annee <= F)] = "origine"
    s[(annee > F) & (annee < P)] = "attente"
    s[annee == P] = "annee_pub"
    s[(annee >= P + 1) & (annee <= P + 5)] = "publie"
    s[annee > P + 5] = "apres"
    return s


def construire():
    journal = {"fichiers": {}, "filtres": {}, "exclusions": {}}
    for f in (F_DOC, F_RET):
        if not os.path.isfile(f):
            sys.exit(f"DONNEE MANQUANTE : {f}")
        taille = os.path.getsize(f)
        journal["fichiers"][os.path.basename(f)] = {
            "octets": taille, "octets_attendus": TAILLES_ATTENDUES[f],
            "taille_conforme": int(taille == TAILLES_ATTENDUES[f]), "sha256": sha256(f)}

    # --- table des signaux -------------------------------------------------
    doc = pd.read_csv(F_DOC)
    journal["filtres"]["lignes_SignalDoc"] = int(len(doc))
    pred = doc[doc["Cat.Signal"] == "Predictor"].copy()
    journal["filtres"]["predicteurs_table"] = int(len(pred))

    # --- rendements --------------------------------------------------------
    large = pq.read_table(F_RET).to_pandas()
    journal["filtres"]["mois_parquet"] = int(len(large))
    journal["filtres"]["colonnes_rendement_parquet"] = int(large.shape[1] - 1)
    dates = pd.to_datetime(large["date"])
    large["date"] = dates.dt.strftime("%Y-%m")
    if large["date"].duplicated().any():
        sys.exit("Deux lignes du Parquet tombent dans le meme mois.")

    # predicteur sans colonne, ou dont une des trois annees est vide : exclu
    sans_colonne = sorted(a for a in pred["Acronym"] if a not in large.columns)
    annees = pred[["Year", "SampleStartYear", "SampleEndYear"]].apply(pd.to_numeric, errors="coerce")
    annee_vide = sorted(pred.loc[annees.isna().any(axis=1), "Acronym"])
    journal["exclusions"]["sans_colonne_parquet"] = sans_colonne
    journal["exclusions"]["annee_vide"] = annee_vide
    garde = pred[~pred["Acronym"].isin(sans_colonne + annee_vide)].copy()
    journal["filtres"]["predicteurs_gardes"] = int(len(garde))
    journal["exclusions"]["colonnes_parquet_hors_table"] = sorted(
        c for c in large.columns if c != "date" and c not in set(pred["Acronym"]))

    # --- format long : une ligne par anomalie x mois ou le rendement existe --
    long = large.melt(id_vars="date", value_vars=list(garde["Acronym"]),
                      var_name="signal", value_name="ret")
    journal["filtres"]["cases_anomalie_mois"] = int(len(long))
    existe = long["ret"].notna() & np.isfinite(long["ret"].astype(float))
    journal["filtres"]["cases_sans_rendement"] = int((~existe).sum())
    long = long[existe].copy()
    journal["filtres"]["rendements_exactement_zero_gardes"] = int((long["ret"] == 0).sum())

    meta = garde.set_index("Acronym")
    long["annee"] = long["date"].str[:4].astype(int)
    long["annee_pub"] = long["signal"].map(meta["Year"]).astype(int)
    long["annee_debut_ech"] = long["signal"].map(meta["SampleStartYear"]).astype(int)
    long["annee_fin_ech"] = long["signal"].map(meta["SampleEndYear"]).astype(int)
    long["statut"] = statut_regle(long["annee"], long["annee_debut_ech"],
                                  long["annee_fin_ech"], long["annee_pub"])
    long["dans_fenetre"] = ((long["annee"] >= AN_MIN) & (long["annee"] <= AN_MAX)).astype(int)
    moy = long[long["statut"] == "origine"].groupby("signal")["ret"].mean()
    long["moy_origine"] = long["signal"].map(moy)
    long = long.sort_values(["signal", "date"], kind="mergesort")[COLONNES]
    long.to_csv(F_PANEL, index=False, encoding="utf-8", lineterminator="\n")
    journal["filtres"]["lignes_panel"] = int(len(long))
    journal["filtres"]["signaux_panel"] = int(long["signal"].nunique())
    journal["filtres"]["lignes_par_statut"] = {k: int(v) for k, v in long["statut"].value_counts().items()}
    return journal


def ensembles(p):
    """K, U, T du § 5.1 sur l'echantillon complet."""
    n_or = p[p["statut"] == "origine"].groupby("signal").size()
    K = set(n_or[n_or >= MIN_ORIGINE].index)
    U = p[(p["dans_fenetre"] == 1) & p["statut"].isin(["origine", "attente"]) & p["signal"].isin(K)]
    T = p[(p["dans_fenetre"] == 1) & (p["statut"] == "publie")
          & p["signal"].isin(set(U["signal"])) & p["date"].isin(set(U["date"]))]
    return K, U, T


def controles(journal):
    """Les dix controles de schema du § 4, refaits sur le fichier relu."""
    p = pd.read_csv(F_PANEL, dtype={"signal": str, "date": str, "statut": str})
    c = {}
    c["1_colonnes"] = list(p.columns) == COLONNES
    c["2_cle_unique"] = not p.duplicated(["signal", "date"]).any()
    c["3_au_plus_212_signaux"] = p["signal"].nunique() <= 212
    fmt = p["date"].str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])")
    c["4_date_annee"] = bool(fmt.all() and (p["annee"] == p["date"].str[:4].astype(int)).all()
                             and p["annee"].between(1926, 2025).all())
    mediane = float(np.median(np.abs(p["ret"])))
    c["5_ret_fini_unite"] = bool(p["ret"].notna().all() and np.isfinite(p["ret"]).all()
                                 and 0.5 <= mediane <= 10)
    g = p.groupby("signal")[["annee_pub", "annee_debut_ech", "annee_fin_ech"]].nunique()
    D, F, P = p["annee_debut_ech"], p["annee_fin_ech"], p["annee_pub"]
    c["6_annees"] = bool((g == 1).all().all() and (D <= F).all() and (F < P).all()
                         and P.between(1973, 2016).all())
    c["7_statut"] = bool((p["statut"].values == statut_regle(p["annee"], D, F, P)).all())
    c["8_dans_fenetre"] = bool((p["dans_fenetre"] == p["annee"].between(AN_MIN, AN_MAX).astype(int)).all())
    moy = p[p["statut"] == "origine"].groupby("signal")["ret"].mean()
    att = p["signal"].map(moy)
    const = p.groupby("signal")["moy_origine"].agg(lambda s: s.nunique(dropna=False)).eq(1).all()
    egal = ((p["moy_origine"] - att).abs() <= 1e-8) | (p["moy_origine"].isna() & att.isna())
    c["9_moy_origine"] = bool(const and egal.all())

    # 10 : rang de la matrice de l'etape 1 sur U complet
    K, U, T = ensembles(p)
    sig = pd.Categorical(U["signal"])
    mois = pd.Categorical(U["date"], categories=sorted(U["date"].unique()))
    n, ns, nm = len(U), len(sig.categories), len(mois.categories)
    X = np.zeros((n, ns + nm - 1 + 1))
    X[np.arange(n), sig.codes] = 1.0
    mc = mois.codes
    X[np.arange(n)[mc > 0], ns + mc[mc > 0] - 1] = 1.0       # premier mois omis
    X[:, -1] = (U["statut"].values == "attente").astype(float)
    rang = int(np.linalg.matrix_rank(X))
    c["10_plein_rang"] = rang == X.shape[1]

    journal["controles"] = {k: int(v) for k, v in c.items()}
    journal["n_violations_schema"] = int(sum(not v for v in c.values()))
    journal["mediane_abs_ret"] = mediane
    journal["etape1"] = {"lignes": n, "colonnes": int(X.shape[1]), "rang": rang,
                         "anomalies": ns, "mois": nm}
    n_or = p[p["statut"] == "origine"].groupby("signal").size().reindex(sorted(p["signal"].unique()), fill_value=0)
    journal["exclusions"]["moins_de_60_lignes_origine"] = {k: int(v) for k, v in n_or[n_or < MIN_ORIGINE].items()}
    journal["effectifs"] = {
        "anomalies_K": len(K),
        "U_lignes": int(len(U)),
        "U_origine": int((U["statut"] == "origine").sum()),
        "U_attente": int((U["statut"] == "attente").sum()),
        "U_anomalies": int(U["signal"].nunique()),
        "U_mois": int(U["date"].nunique()),
        "publie_dans_fenetre_avant_conditions": int(((p["dans_fenetre"] == 1) & (p["statut"] == "publie")).sum()),
        "T_lignes": int(len(T)),
        "T_anomalies": int(T["signal"].nunique()),
        "attendus_preenregistrement": {"U_origine": 57204, "U_attente": 8904, "T_lignes": 10296,
                                       "T_anomalies": 189, "U_anomalies": 210},
    }
    journal["panel_sha256"] = sha256(F_PANEL)
    return journal


if __name__ == "__main__":
    j = controles(construire())
    with open(F_JOURNAL, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=2)
    print(json.dumps(j, ensure_ascii=False, indent=2))
