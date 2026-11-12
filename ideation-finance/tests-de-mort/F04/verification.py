"""Vérification indépendante F04 — écrite à partir du seul texte de preenregistrement.md.

Lit F04_analyse.csv, exécute les contrôles de schéma de la section 5, calcule la
statistique principale et le placebo de la section 6, écrit verification.json.
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "F04_analyse.csv")
SORTIE = os.path.join(ICI, "verification.json")

COLONNES = [
    "id_ligne", "type_ligne", "cusip", "terme_api", "echeance", "reouverture", "principal",
    "date_adjudication", "mois", "montant_offert_mds", "date_j", "date_jm5", "date_jp5",
    "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5", "complet", "fenetre_propre",
]
RDT = ["cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5"]
TERMES_REOUV = {"9-Year 10-Month", "9-Year 11-Month", "19-Year 10-Month", "19-Year 11-Month",
                "29-Year 10-Month", "29-Year 11-Month"}

# Lecture brute en texte : aucun typage implicite, les champs vides restent vides.
raw = pd.read_csv(FICHIER, dtype=str, keep_default_na=False, encoding="utf-8")
echecs = []
notes = []


def controle(nom, ok, detail=""):
    if not ok:
        echecs.append(f"{nom}: {detail}")


# 1. Colonnes
controle("1-colonnes", list(raw.columns) == COLONNES, f"colonnes lues = {list(raw.columns)}")

df = raw.copy()


def entier(s):
    try:
        f = float(s)
        return int(f) if f == int(f) and s.strip() != "" else None
    except Exception:
        return None


def num(s):
    return np.nan if s.strip() == "" else float(s)


for c in ["echeance", "reouverture", "principal", "complet", "fenetre_propre"]:
    df[c + "_i"] = df[c].map(entier)
for c in RDT + ["montant_offert_mds"]:
    df[c + "_f"] = df[c].map(num)
for c in ["date_adjudication", "date_j", "date_jm5", "date_jp5"]:
    df[c + "_d"] = pd.to_datetime(df[c], format="%Y-%m-%d", errors="coerce")
controle("dates-lisibles",
         not df[[c + "_d" for c in ["date_adjudication", "date_j", "date_jm5", "date_jp5"]]].isna().any().any(),
         "date illisible")

# 2. Unicité et valeurs permises
controle("2-id_unique", df["id_ligne"].is_unique, f"{df['id_ligne'].duplicated().sum()} doublons")
controle("2-type_ligne", df["type_ligne"].isin(["reelle", "placebo"]).all(), "valeur hors {reelle, placebo}")
controle("2-echeance", df["echeance_i"].isin([2, 3, 5, 7, 10, 20, 30]).all(), "valeur hors liste")
for c in ["reouverture", "principal", "complet", "fenetre_propre"]:
    controle(f"2-{c}", df[c + "_i"].isin([0, 1]).all(), "valeur hors {0,1}")

# 3. Dates
controle("3-ordre", ((df.date_jm5_d < df.date_j_d) & (df.date_j_d < df.date_jp5_d)).all(), "jm5<j<jp5 violé")
re = df.type_ligne == "reelle"
pl = df.type_ligne == "placebo"
controle("3-reelle_j", (df.loc[re, "date_j_d"] == df.loc[re, "date_adjudication_d"]).all(), "date_j != date_adj")
controle("3-placebo_j", (df.loc[pl, "date_j_d"] > df.loc[pl, "date_adjudication_d"]).all(), "date_j <= date_adj")

# 4. Période, mois, montant
controle("4-periode", df.date_adjudication_d.between(pd.Timestamp("2010-01-01"), pd.Timestamp("2026-09-30")).all(),
         "date hors période")
controle("4-mois", (df["mois"] == df["date_adjudication"].str[:7]).all(), "mois incohérent")
controle("4-montant", (df["montant_offert_mds_f"] > 0).all(), "montant <= 0 ou vide")

# 5. principal et placebo
attendu = ((df.reouverture_i == 1) & df.echeance_i.isin([10, 20, 30])).astype(int)
controle("5-principal", (df.principal_i == attendu).all(), "principal incohérent")
controle("5-placebo_principal", (df.loc[pl, "principal_i"] == 1).all(), "placebo avec principal != 1")
cle_re = df.loc[re].groupby(["cusip", "date_adjudication"]).size()
n_match = [cle_re.get((c, d), 0) for c, d in zip(df.loc[pl, "cusip"], df.loc[pl, "date_adjudication"])]
controle("5-placebo_apparie", all(n == 1 for n in n_match), "placebo sans reelle unique correspondante")

# 6. complet
present = df[[c + "_f" for c in RDT]].notna().all(axis=1).astype(int)
controle("6-complet", (df.complet_i == present).all(), "complet incohérent")

# 7. Bornes et appariement
vals = df[[c + "_f" for c in RDT]]
controle("7-bornes", ((vals.isna()) | ((vals >= -1) & (vals <= 20))).all().all(), "rendement hors [-1,20]")
ok7 = True
for x in ["jm5", "j", "jp5"]:
    d = (df[f"cmt_{x}_f"] - df[f"gsw_{x}_f"]).abs()
    ok7 &= bool((d.isna() | (d <= 1)).all())
controle("7-appariement", ok7, "|cmt-gsw| > 1")

# 8. Nombre de réouvertures principales réelles
n_pr = int(((df.type_ligne == "reelle") & (df.principal_i == 1)).sum())
controle("8-n_principal", 300 <= n_pr <= 330, f"n = {n_pr}")

schema_ok = int(len(echecs) == 0)


# Statistique (section 6)
def V(sub):
    E = {x: sub[f"cmt_{x}_f"] - sub[f"gsw_{x}_f"] for x in ["jm5", "j", "jp5"]}
    return 100.0 * (2 * E["j"] - E["jm5"] - E["jp5"])


def moyenne_groupee(v, mois):
    N = len(v)
    vbar = v.mean()
    S = (v - vbar).groupby(mois).sum()
    G = S.size
    et = (1.0 / N) * math.sqrt(G / (G - 1) * float((S ** 2).sum()))
    return N, G, float(vbar), et


P = df[(df.type_ligne == "reelle") & (df.principal_i == 1) & (df.complet_i == 1) & (df.fenetre_propre_i == 1)]
vP = V(P)
N, G, vbar, et = moyenne_groupee(vP, P["mois"])
t = vbar / et
B = vbar + 1.96 * et
M = min(2 - t, B - 0.5)

Q = df[(df.type_ligne == "placebo") & (df.complet_i == 1) & (df.fenetre_propre_i == 1)]
vQ = V(Q)
Np, Gp, vbarp, etp = moyenne_groupee(vQ, Q["mois"])
tp = abs(vbarp / etp)

res = {
    "schema_ok": schema_ok,
    "n_adjudications": int(N),
    "n_grappes": int(G),
    "v_moyen_pb": vbar,
    "erreur_type_pb": et,
    "t_stat": t,
    "borne_sup_95_pb": B,
    "marge_zone_grise": M,
    "n_placebo": int(Np),
    "t_placebo_abs": tp,
}
with open(SORTIE, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=2)

print(json.dumps(res, indent=2))
print("ECHECS SCHEMA:", echecs)
print(f"placebo: N={Np} G={Gp} vbar={vbarp:.4f} et={etp:.4f}")
print(f"sd V sur P = {vP.std(ddof=1):.4f}")
