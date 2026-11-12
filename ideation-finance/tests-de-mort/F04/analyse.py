#!/usr/bin/env python3
"""F04 — statistique principale, garde placebo et analyses secondaires S1 à S3.

Lit uniquement F04_analyse.csv (préinscription, sections 5 et 6). Déterministe.
Écrit temoin.json (champs_verification), resultats_analyse.json (détail) et figure.png.
Usage : python3 -I analyse.py
"""
import csv
import json
import math
import os
from collections import Counter, defaultdict
from datetime import date

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "F04_analyse.csv")
COLONNES = ["id_ligne", "type_ligne", "cusip", "terme_api", "echeance", "reouverture",
            "principal", "date_adjudication", "mois", "montant_offert_mds", "date_j",
            "date_jm5", "date_jp5", "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j",
            "gsw_jp5", "complet", "fenetre_propre"]
REND = ("cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5")

with open(FICHIER, newline="", encoding="utf-8") as f:
    rd = csv.DictReader(f)
    ENTETE = rd.fieldnames
    T = list(rd)


# ------------------------------------------------------------------ contrôles de schéma
def schema(T, entete):
    c = {}
    c["1"] = entete == COLONNES
    ids = [r["id_ligne"] for r in T]
    c["2"] = (len(ids) == len(set(ids))
              and all(r["type_ligne"] in ("reelle", "placebo") for r in T)
              and all(r["echeance"] in ("2", "3", "5", "7", "10", "20", "30") for r in T)
              and all(r[k] in ("0", "1") for r in T
                      for k in ("reouverture", "principal", "complet", "fenetre_propre")))
    c["3"] = all(r["date_jm5"] != "" and r["date_jm5"] < r["date_j"] < r["date_jp5"]
                 and (r["date_j"] == r["date_adjudication"] if r["type_ligne"] == "reelle"
                      else r["date_j"] > r["date_adjudication"]) for r in T)
    c["4"] = all("2010-01-01" <= r["date_adjudication"] <= "2026-09-30"
                 and r["mois"] == r["date_adjudication"][:7]
                 and float(r["montant_offert_mds"]) > 0 for r in T)
    nr = Counter((r["cusip"], r["date_adjudication"]) for r in T if r["type_ligne"] == "reelle")
    c["5"] = (all((r["principal"] == "1") == (r["reouverture"] == "1" and r["echeance"] in ("10", "20", "30"))
                  for r in T)
              and all(r["principal"] == "1" and nr[(r["cusip"], r["date_adjudication"])] == 1
                      for r in T if r["type_ligne"] == "placebo"))
    c["6"] = all((r["complet"] == "1") == all(r[k] != "" for k in REND) for r in T)
    ok = True
    for r in T:
        for k in REND:
            if r[k] != "" and not (-1 <= float(r[k]) <= 20):
                ok = False
        for s in ("jm5", "j", "jp5"):
            a, b = r["cmt_" + s], r["gsw_" + s]
            if a != "" and b != "" and abs(float(a) - float(b)) > 1:
                ok = False
    c["7"] = ok
    n = sum(1 for r in T if r["type_ligne"] == "reelle" and r["principal"] == "1")
    c["8"] = 300 <= n <= 330
    return {k: int(v) for k, v in c.items()}


CTL = schema(T, ENTETE)
SCHEMA_OK = int(all(CTL.values()))


# ------------------------------------------------------------------ formules de la section 6
def V_ecart(r):
    e = lambda s: float(r["cmt_" + s]) - float(r["gsw_" + s])
    return 100.0 * (2.0 * e("j") - e("jm5") - e("jp5"))


def V_brut(r):
    return 100.0 * (2.0 * float(r["gsw_j"]) - float(r["gsw_jm5"]) - float(r["gsw_jp5"]))


def moyenne_groupee(v, mois):
    """V̄, ET = (1/N)·racine(G/(G−1)·Σ_g S_g²), t, N, G."""
    v = np.asarray(v, dtype=float)
    N = len(v)
    if N == 0:
        return {"n": 0, "g": 0, "moyenne": None, "et": None, "t": None}
    vbar = float(v.sum() / N)
    S = defaultdict(float)
    for x, m in zip(v, mois):
        S[m] += x - vbar
    G = len(S)
    if G < 2:
        return {"n": N, "g": G, "moyenne": vbar, "et": None, "t": None}
    et = (1.0 / N) * math.sqrt(G / (G - 1.0) * sum(s * s for s in S.values()))
    return {"n": N, "g": G, "moyenne": vbar, "et": et, "t": vbar / et}


# ------------------------------------------------------------------ statistique principale
P = [r for r in T if r["type_ligne"] == "reelle" and r["principal"] == "1"
     and r["complet"] == "1" and r["fenetre_propre"] == "1"]
vP = np.array([V_ecart(r) for r in P])
mP = [r["mois"] for r in P]
princ = moyenne_groupee(vP, mP)
vbar, et, t = princ["moyenne"], princ["et"], princ["t"]
borne_sup = vbar + 1.96 * et
borne_inf = vbar - 1.96 * et
marge = min(2.0 - t, borne_sup - 0.5)

# ------------------------------------------------------------------ garde placebo
PL = [r for r in T if r["type_ligne"] == "placebo" and r["complet"] == "1" and r["fenetre_propre"] == "1"]
vPL = np.array([V_ecart(r) for r in PL])
plac = moyenne_groupee(vPL, [r["mois"] for r in PL])

temoin = {
    "schema_ok": SCHEMA_OK,
    "n_adjudications": princ["n"],
    "n_grappes": princ["g"],
    "v_moyen_pb": vbar,
    "erreur_type_pb": et,
    "t_stat": t,
    "borne_sup_95_pb": borne_sup,
    "marge_zone_grise": marge,
    "n_placebo": plac["n"],
    "t_placebo_abs": abs(plac["t"]),
}
with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
    json.dump(temoin, f, indent=1)

# ------------------------------------------------------------------ filtres successifs
R = [r for r in T if r["type_ligne"] == "reelle"]
Rp = [r for r in R if r["principal"] == "1"]
Rpc = [r for r in Rp if r["complet"] == "1"]
PLall = [r for r in T if r["type_ligne"] == "placebo"]
PLc = [r for r in PLall if r["complet"] == "1"]
filtres = {
    "lignes_fichier": len(T),
    "reelle": len(R),
    "reelle_principal": len(Rp),
    "reelle_principal_complet": len(Rpc),
    "reelle_principal_complet_fenetre_propre_P": len(P),
    "mois_distincts_P": princ["g"],
    "P_par_echeance": dict(sorted(Counter(int(r["echeance"]) for r in P).items())),
    "placebo": len(PLall),
    "placebo_complet": len(PLc),
    "placebo_complet_fenetre_propre": len(PL),
    "mois_distincts_placebo": plac["g"],
}

# ------------------------------------------------------------------ descriptifs sur P
desc = {
    "ecart_type_V_P_n_moins_1": float(vP.std(ddof=1)),
    "ecart_type_V_P_n": float(vP.std(ddof=0)),
    "mediane_V_P": float(np.median(vP)),
    "min_V_P": float(vP.min()), "max_V_P": float(vP.max()),
    "quartiles_V_P": [float(x) for x in np.percentile(vP, [25, 75])],
    "borne_inf_95_pb": borne_inf,
    "moyenne_placebo_pb": plac["moyenne"], "et_placebo_pb": plac["et"], "t_placebo": plac["t"],
    "ecart_type_V_placebo_n_moins_1": float(vPL.std(ddof=1)),
    "moyenne_V_P_par_echeance_sans_et": {
        str(e): float(np.mean([v for v, r in zip(vP, P) if r["echeance"] == str(e)])) for e in (10, 20, 30)},
    "taille_moyenne_grappe_P": princ["n"] / princ["g"],
    "et_naif_sans_groupement": float(vP.std(ddof=1) / math.sqrt(len(vP))),
}

# ------------------------------------------------------------------ S1 : hors échantillon, rendement brut
S1L = [r for r in R if r["date_adjudication"] >= "2024-08-01"
       and all(r[k] != "" for k in ("gsw_jm5", "gsw_j", "gsw_jp5"))]
vS1 = np.array([V_brut(r) for r in S1L])
s1 = moyenne_groupee(vS1, [r["mois"] for r in S1L])
s1["lignes_avant_filtre_gsw"] = sum(1 for r in R if r["date_adjudication"] >= "2024-08-01")
s1["ecart_type_n_moins_1"] = float(vS1.std(ddof=1))
s1["moyenne_par_echeance_sans_et"] = {}
s1["n_par_echeance"] = {}
for e in (2, 3, 5, 7, 10, 20, 30):
    x = [v for v, r in zip(vS1, S1L) if r["echeance"] == str(e)]
    s1["moyenne_par_echeance_sans_et"][str(e)] = float(np.mean(x)) if x else None
    s1["n_par_echeance"][str(e)] = len(x)

# ------------------------------------------------------------------ S2 : taille
def jour(s):
    return date.fromisoformat(s)


par_ech = defaultdict(list)
for r in R:
    par_ech[r["echeance"]].append((jour(r["date_adjudication"]), float(r["montant_offert_mds"])))


def calcule_s2(P_, vP_, exclure_ids=()):
    rr = []
    for r in P_:
        d = jour(r["date_adjudication"])
        ant = [m for (dd, m) in par_ech[r["echeance"]] if 1 <= (d - dd).days <= 1096]
        rr.append(float(r["montant_offert_mds"]) / (sum(ant) / len(ant)) if len(ant) >= 12 else None)
    idx = [i for i, x in enumerate(rr) if x is not None and P_[i]["id_ligne"] not in exclure_ids]
    rv = np.array([rr[i] for i in idx])
    z = (rv - rv.mean()) / rv.std(ddof=1)
    y = np.array([vP_[i] for i in idx])
    X = np.column_stack([z] + [np.array([1.0 if P_[i]["echeance"] == str(e) else 0.0 for i in idx])
                               for e in (10, 20, 30)])
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ X.T @ y
    u = y - X @ beta
    grappes = defaultdict(list)
    for k, i in enumerate(idx):
        grappes[P_[i]["mois"]].append(k)
    G = len(grappes)
    viande = np.zeros((4, 4))
    for ks in grappes.values():
        s = X[ks].T @ u[ks]
        viande += np.outer(s, s)
    Vb = XtXi @ (G / (G - 1.0) * viande) @ XtXi
    se = np.sqrt(np.diag(Vb))
    return {
        "n_P": len(P_), "n_r_manquant": sum(1 for x in rr if x is None), "n_regression": len(idx), "g": G,
        "r_moyenne": float(rv.mean()), "r_ecart_type_n_moins_1": float(rv.std(ddof=1)),
        "r_min": float(rv.min()), "r_max": float(rv.max()),
        "z_min": float(z.min()), "z_max": float(z.max()),
        "pente_pb_par_ecart_type": float(beta[0]), "et_pente": float(se[0]),
        "t_pente": float(beta[0] / se[0]),
        "indicatrices_10_20_30": [float(b) for b in beta[1:]],
        "et_indicatrices_10_20_30": [float(x) for x in se[1:]],
        "n_regression_par_echeance": {str(e): int(X[:, j + 1].sum()) for j, e in enumerate((10, 20, 30))},
    }


s2 = calcule_s2(P, vP)
# Sensibilité HORS PRÉINSCRIPTION, à titre d'information seulement : sans les lignes de moins de 1 Md$.
petites = [r["id_ligne"] for r in P if float(r["montant_offert_mds"]) < 1.0]
s2_sans_petites = calcule_s2(P, vP, exclure_ids=set(petites))

# ------------------------------------------------------------------ S3 : sous-périodes
s3 = {}
for nom, a, b in (("2010-01-01_2014-12-31", "2010-01-01", "2014-12-31"),
                  ("2015-01-01_2024-07-31", "2015-01-01", "2024-07-31"),
                  ("2024-08-01_2026-09-30", "2024-08-01", "2026-09-30")):
    sel = [i for i, r in enumerate(P) if a <= r["date_adjudication"] <= b]
    s3[nom] = moyenne_groupee(vP[sel], [mP[i] for i in sel])

# Information hors préinscription : statistique principale sans les lignes de moins de 1 Md$.
sel = [i for i, r in enumerate(P) if r["id_ligne"] not in set(petites)]
hors_pre = {
    "lignes_moins_de_1_md": petites,
    "V_des_lignes_moins_de_1_md": [float(vP[i]) for i, r in enumerate(P) if r["id_ligne"] in set(petites)],
    "principale_sans_ces_lignes": moyenne_groupee(vP[sel], [mP[i] for i in sel]),
    "S2_sans_ces_lignes": s2_sans_petites,
}

resultats = {"temoin": temoin, "controles_schema": CTL, "filtres": filtres, "descriptif_P": desc,
             "S1": s1, "S2": s2, "S3": s3, "information_hors_preinscription": hors_pre}
with open(os.path.join(ICI, "resultats_analyse.json"), "w", encoding="utf-8") as f:
    json.dump(resultats, f, ensure_ascii=False, indent=1)
print(json.dumps(resultats, ensure_ascii=False, indent=1))

# ------------------------------------------------------------------ figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FOND, ENCRE, ENCRE2, GRILLE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLEU, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": ENCRE,
                     "axes.edgecolor": GRILLE, "axes.labelcolor": ENCRE2,
                     "xtick.color": ENCRE2, "ytick.color": ENCRE2})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1.0, 1.15]})
fig.patch.set_facecolor(FOND)
for ax in (ax1, ax2):
    ax.set_facecolor(FOND)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# Panneau A : distribution des V_i sur P, toutes valeurs montrées.
lo, hi = math.floor(vP.min()) - 0.5, math.ceil(vP.max()) + 0.5
ax1.hist(vP, bins=np.arange(lo, hi + 0.5, 0.5), color=BLEU, edgecolor=FOND, linewidth=0.8)
ax1.axvline(0, color=ENCRE2, linewidth=1)
ax1.axvline(vbar, color=ENCRE, linewidth=1.5, linestyle="--")
ax1.set_xlabel("V par réouverture (points de base)")
ax1.set_ylabel("Nombre de réouvertures")
ax1.set_title("A. Distribution de V sur l'échantillon principal\n(N = %d, écart-type = %.2f pb ; tiret : moyenne)"
              % (len(vP), vP.std(ddof=1)), loc="left", fontsize=10.5, color=ENCRE)
ax1.grid(axis="y", color=GRILLE, linewidth=0.8)
ax1.set_axisbelow(True)

# Panneau B : moyennes et intervalles à 95 % (± 1,96 ET groupée par mois).
lignes_fig = [("Principal : réouvertures 10, 20, 30 ans", princ, BLEU, "o"),
              ("Placebo : J + 10 jours ouvrés", plac, ORANGE, "s"),
              ("S3 : 2010-01 à 2014-12", s3["2010-01-01_2014-12-31"], BLEU, "o"),
              ("S3 : 2015-01 à 2024-07", s3["2015-01-01_2024-07-31"], BLEU, "o"),
              ("S3 : 2024-08 à 2026-09", s3["2024-08-01_2026-09-30"], BLEU, "o")]
ys = [4.6, 3.6, 2.2, 1.2, 0.2]
ax2.axvspan(0.5, 1.5, color=GRILLE, alpha=0.9, zorder=0)
ax2.axvline(0, color=ENCRE2, linewidth=1, zorder=1)
for (nom, res, coul, marq), y in zip(lignes_fig, ys):
    plein = y in (4.6, 3.6)
    ax2.errorbar(res["moyenne"], y, xerr=1.96 * res["et"], fmt=marq, color=coul, markersize=8,
                 markerfacecolor=coul if plein else FOND, markeredgewidth=2, elinewidth=2, capsize=4, zorder=3)
    ax2.text(-0.02, y, "%s\nN = %d, %d mois" % (nom, res["n"], res["g"]), transform=ax2.get_yaxis_transform(),
             ha="right", va="center", fontsize=9, color=ENCRE)
    ax2.text(1.02, y, "%+.2f pb\n[%+.2f ; %+.2f]" % (res["moyenne"], res["moyenne"] - 1.96 * res["et"],
                                                     res["moyenne"] + 1.96 * res["et"]),
             transform=ax2.get_yaxis_transform(), ha="left", va="center", fontsize=9, color=ENCRE)
xs = [r["moyenne"] + s * 1.96 * r["et"] for _, r, _, _ in lignes_fig for s in (-1, 1)]
ax2.set_xlim(min(min(xs), -0.2) - 0.15, max(max(xs), 1.5) + 0.15)
ax2.set_ylim(-0.5, 5.4)
ax2.set_yticks([])
ax2.spines["left"].set_visible(False)
ax2.text(1.0, 5.25, "fourchette prédite\n0,5 à 1,5 pb", ha="center", va="top", fontsize=8.5, color=ENCRE2)
ax2.set_xlabel("Moyenne de V (points de base), barre : ± 1,96 erreur type groupée par mois")
ax2.set_title("B. Moyenne de V et intervalle à 95 %\n(statistique principale, garde placebo, sous-périodes descriptives)",
              loc="left", fontsize=10.5, color=ENCRE)
ax2.grid(axis="x", color=GRILLE, linewidth=0.8)
ax2.set_axisbelow(True)
fig.suptitle("F04 — Écart rendement à échéance constante − courbe ajustée (GSW) autour des réouvertures, 2010-2026",
             x=0.01, ha="left", fontsize=12, color=ENCRE)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.subplots_adjust(wspace=0.75)
fig.savefig(os.path.join(ICI, "figure.png"), dpi=150, facecolor=FOND)
