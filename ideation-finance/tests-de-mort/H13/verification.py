"""Vérification indépendante H13 — écrite à partir du seul texte de preenregistrement.md.
Lit uniquement H13_analyse.csv. Écrit verification.json (9 champs) et affiche les diagnostics."""
import csv, json, math, sys, statistics
from datetime import date
from pathlib import Path
import numpy as np

ICI = Path(__file__).resolve().parent
FICHIER = ICI / "H13_analyse.csv"

COLONNES = ["date_publication", "mois_reference", "n_mois_nouveaux", "date_millesime_precedent",
            "date_millesime_3e", "emploi_1re_k", "emploi_3e_k", "rev_m1_k", "rev_m2_k", "tendance_12m_k",
            "d_chomage_pt", "revision_large", "extreme", "date_veille", "date_avant_veille", "dgs2_j",
            "dgs2_veille", "dgs2_avant_veille", "sveny02_j", "sveny02_veille", "complet", "principal"]
DATES = ["date_publication", "date_millesime_precedent", "date_millesime_3e", "date_veille", "date_avant_veille"]
ENTIERS = ["n_mois_nouveaux", "emploi_1re_k", "emploi_3e_k", "rev_m1_k", "rev_m2_k",
           "revision_large", "extreme", "complet", "principal"]
DECIMAUX = ["tendance_12m_k", "d_chomage_pt", "dgs2_j", "dgs2_veille", "dgs2_avant_veille",
            "sveny02_j", "sveny02_veille"]

echecs = []          # contrôles de schéma en échec
anomalies = []       # remarques hors schéma


def echec(n, msg):
    echecs.append(f"contrôle {n}: {msg}")


with open(FICHIER, newline="", encoding="utf-8") as f:
    lecteur = csv.reader(f)
    entete = next(lecteur)
    brut = [r for r in lecteur]

# --- contrôle 1 : colonnes
if entete != COLONNES:
    echec(1, f"en-tête différent: {entete}")
for i, r in enumerate(brut):
    if len(r) != len(COLONNES):
        echec(1, f"ligne {i+2}: {len(r)} champs")


def conv(col, s):
    if s == "":
        return None
    if col in DATES:
        return date.fromisoformat(s)
    if col in ENTIERS:
        v = float(s)
        if v != int(v) or not s.lstrip("-").isdigit():
            echec(4 if col in ("n_mois_nouveaux", "revision_large", "extreme", "complet", "principal") else 1,
                  f"{col}={s} n'est pas un entier écrit comme tel")
        return int(v)
    if col in DECIMAUX:
        return float(s)
    return s


lignes = []
for r in brut:
    d = {c: conv(c, v) for c, v in zip(COLONNES, r)}
    lignes.append(d)
n_lignes = len(lignes)

# --- contrôle 2
if not (425 <= n_lignes <= 435):
    echec(2, f"{n_lignes} lignes")
dp = [l["date_publication"] for l in lignes]
if any(x is None for x in dp):
    echec(2, "date_publication vide")
if len(set(dp)) != len(dp):
    echec(2, "date_publication non unique")
for a, b in zip(dp, dp[1:]):
    if not a < b:
        echec(2, f"non strictement croissant {a} {b}")
if min(dp) < date(1990, 1, 1) or max(dp) > date(2025, 12, 31):
    echec(2, "hors période")

# --- contrôle 3
def mois(s):
    a, m = s.split("-")
    return int(a), int(m)

mr = [mois(l["mois_reference"]) for l in lignes]
for a, b in zip(mr, mr[1:]):
    if not a < b:
        echec(3, f"mois_reference non croissant {a} {b}")
for l, (a, m) in zip(lignes, mr):
    e = (l["date_publication"] - date(a, m, 1)).days
    if not (28 <= e <= 110):
        echec(3, f"{l['date_publication']} écart {e} j")

# --- contrôle 4
for l in lignes:
    if l["n_mois_nouveaux"] not in (1, 2):
        echec(4, f"{l['date_publication']} n_mois_nouveaux={l['n_mois_nouveaux']}")
    for c in ("revision_large", "extreme", "complet", "principal"):
        if l[c] not in (0, 1):
            echec(4, f"{l['date_publication']} {c}={l[c]}")

# --- contrôle 5 (lecture littérale : une comparaison avec une date vide échoue, sauf date_millesime_3e)
for l in lignes:
    d = l["date_publication"]
    if l["date_millesime_precedent"] is None or not l["date_millesime_precedent"] < d:
        echec(5, f"{d} date_millesime_precedent")
    if l["date_millesime_3e"] is not None and not l["date_millesime_3e"] > d:
        echec(5, f"{d} date_millesime_3e")
    if l["date_veille"] is None or l["date_avant_veille"] is None or \
            not (l["date_avant_veille"] < l["date_veille"] < d):
        echec(5, f"{d} veille/avant-veille")

# --- contrôle 6
for l in lignes:
    a1, a3 = l["emploi_1re_k"], l["emploi_3e_k"]
    ext = 1 if (a1 is not None and abs(a1) > 1000) or (a3 is not None and a1 is not None and abs(a1 - a3) > 500) else 0
    comp = 1 if all(l[c] is not None for c in ("emploi_3e_k", "rev_m1_k", "rev_m2_k", "tendance_12m_k",
                                                "d_chomage_pt", "dgs2_j", "dgs2_veille", "dgs2_avant_veille")) else 0
    princ = 1 if (l["complet"] == 1 and l["n_mois_nouveaux"] == 1 and l["revision_large"] == 0 and l["extreme"] == 0) else 0
    if a1 is None:
        echec(6, f"{l['date_publication']} emploi_1re_k vide")
    if ext != l["extreme"]:
        echec(6, f"{l['date_publication']} extreme {l['extreme']} attendu {ext}")
    if comp != l["complet"]:
        echec(6, f"{l['date_publication']} complet {l['complet']} attendu {comp}")
    if princ != l["principal"]:
        echec(6, f"{l['date_publication']} principal {l['principal']} attendu {princ}")

# --- contrôle 7
for l in lignes:
    if l["emploi_1re_k"] is not None and abs(l["emploi_1re_k"]) > 25000:
        echec(7, f"{l['date_publication']} emploi_1re_k")
    if l["d_chomage_pt"] is not None and abs(l["d_chomage_pt"]) > 11:
        echec(7, f"{l['date_publication']} d_chomage_pt")
    for c in ("dgs2_j", "dgs2_veille", "dgs2_avant_veille", "sveny02_j", "sveny02_veille"):
        if l[c] is not None and not (0 <= l[c] <= 12):
            echec(7, f"{l['date_publication']} {c}={l[c]}")

# --- contrôle 8
l8 = [l for l in lignes if l["date_publication"] == date(1990, 2, 2)]
if len(l8) != 1:
    echec(8, "ligne 1990-02-02 absente")
else:
    l8 = l8[0]
    if not (l8["mois_reference"] == "1990-01" and l8["emploi_1re_k"] == 275
            and l8["date_millesime_3e"] == date(1990, 4, 6) and l8["emploi_3e_k"] == 361):
        echec(8, f"valeurs {l8}")

# --- contrôle 9
for l in lignes:
    if l["dgs2_j"] is not None and l["sveny02_j"] is not None and abs(l["dgs2_j"] - l["sveny02_j"]) > 0.75:
        echec(9, f"{l['date_publication']} j écart {l['dgs2_j'] - l['sveny02_j']:.3f}")
    if l["dgs2_veille"] is not None and l["sveny02_veille"] is not None and \
            abs(l["dgs2_veille"] - l["sveny02_veille"]) > 0.75:
        echec(9, f"{l['date_publication']} veille écart")
if isinstance(l8, dict):
    if l8["sveny02_veille"] is not None and abs(l8["sveny02_veille"] - 8.1466) > 0.0001:
        echec(9, f"sveny02_veille 1990-02-02 = {l8['sveny02_veille']}")
    if l8["sveny02_j"] is not None and abs(l8["sveny02_j"] - 8.2234) > 0.0001:
        echec(9, f"sveny02_j 1990-02-02 = {l8['sveny02_j']}")

schema_ok = 0 if echecs else 1

# ======================= Statistique =======================
P = [l for l in lignes if l["principal"] == 1]
n = len(P)


def matrices(rows, dep="j"):
    X = np.array([[1.0,
                   (l["emploi_1re_k"] - l["emploi_3e_k"]) / 100.0,
                   l["rev_m1_k"] / 100.0,
                   l["rev_m2_k"] / 100.0,
                   l["d_chomage_pt"],
                   l["tendance_12m_k"] / 100.0] for l in rows], dtype=float)
    if dep == "j":
        y = np.array([100.0 * (l["dgs2_j"] - l["dgs2_veille"]) for l in rows])
    else:
        y = np.array([100.0 * (l["dgs2_veille"] - l["dgs2_avant_veille"]) for l in rows])
    return X, y


def ols_hc3(X, y):
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    h = np.einsum("ij,jk,ik->i", X, XtX_inv, X)
    u = e / (1.0 - h)
    meat = (X * (u ** 2)[:, None]).T @ X
    V = XtX_inv @ meat @ XtX_inv
    return b, V, e, h


X, y = matrices(P, "j")
b, V, e, h = ols_hc3(X, y)
beta = float(b[1]); et = float(math.sqrt(V[1, 1])); t = beta / et
binf = beta - 1.96 * et; bsup = beta + 1.96 * et
marge = min(1.96 - t, bsup - 1)

Xp, yp = matrices(P, "veille")
bp, Vp, _, _ = ols_hc3(Xp, yp)
t_plac = abs(bp[1] / math.sqrt(Vp[1, 1]))

resultat = {
    "schema_ok": schema_ok,
    "n_publications": n,
    "beta_pb_par_100k": beta,
    "erreur_type_pb": et,
    "t_stat": t,
    "borne_inf_95_pb": binf,
    "borne_sup_95_pb": bsup,
    "marge_zone_grise": marge,
    "t_placebo_abs": float(t_plac),
}
(ICI / "verification.json").write_text(json.dumps(resultat, indent=2) + "\n", encoding="utf-8")

# ======================= Diagnostics (rapport) =======================
print("=== verification.json ===")
for k, v in resultat.items():
    print(k, v)
print("\n=== échecs de schéma ===")
for x in echecs:
    print(x)

# recoupement statsmodels
try:
    import statsmodels.api as sm
    r = sm.OLS(y, X).fit(cov_type="HC3")
    rp = sm.OLS(yp, Xp).fit(cov_type="HC3")
    print("\nstatsmodels beta", r.params[1], "et", r.bse[1], "t placebo", abs(rp.tvalues[1]))
except Exception as exc:
    print("statsmodels indisponible", exc)

print("\n=== anomalies ===")
# jours de semaine
from collections import Counter
jours = Counter(d.weekday() for d in dp)
print("jours de semaine (0=lundi):", dict(sorted(jours.items())))
for l in lignes:
    if l["date_publication"].weekday() != 4:
        print("  pas un vendredi:", l["date_publication"], l["date_publication"].strftime("%A"), "principal", l["principal"])
    if l["date_veille"] and (l["date_publication"] - l["date_veille"]).days > 4:
        print("  veille lointaine:", l["date_publication"], l["date_veille"])
# prec cohérent avec la ligne précédente
for a, bb in zip(lignes, lignes[1:]):
    if bb["date_millesime_precedent"] != a["date_publication"]:
        print("  prec != ligne précédente:", bb["date_publication"], bb["date_millesime_precedent"], a["date_publication"])
# n_mois_nouveaux vs écart de mois_reference
for (a, ma), (bb, mb) in zip(zip(lignes, mr), zip(lignes[1:], mr[1:])):
    ecart = (mb[0] - ma[0]) * 12 + mb[1] - ma[1]
    if ecart != bb["n_mois_nouveaux"]:
        print("  n_mois_nouveaux incohérent:", bb["date_publication"], ecart, bb["n_mois_nouveaux"])
# doublons de contenu
cle = Counter((l["emploi_1re_k"], l["emploi_3e_k"], l["rev_m1_k"], l["rev_m2_k"]) for l in lignes)
for k, c in cle.items():
    if c > 1:
        print("  contenu d'emploi dupliqué:", k, c)
cle2 = Counter((l["dgs2_j"], l["dgs2_veille"], l["dgs2_avant_veille"]) for l in lignes)
for k, c in cle2.items():
    if c > 1:
        print("  taux dupliqués:", k, c)
# v3 : première publication postérieure dont mois_reference >= m+2
idx = {l["date_publication"]: i for i, l in enumerate(lignes)}
def mnum(t): return t[0] * 12 + t[1]
for i, l in enumerate(lignes):
    m = mnum(mr[i]); attendu = None
    for j in range(i + 1, n_lignes):
        if mnum(mr[j]) >= m + 2:
            attendu = lignes[j]["date_publication"]; break
    if attendu is not None and attendu != l["date_millesime_3e"]:
        print("  v3 incohérent:", l["date_publication"], l["date_millesime_3e"], "attendu", attendu)
    if attendu is None and l["date_millesime_3e"] is not None and l["date_millesime_3e"] <= date(2025, 12, 31):
        print("  v3 inattendu:", l["date_publication"], l["date_millesime_3e"])
    if attendu is None:
        print("  v3 hors fichier (normal en fin de période):", l["date_publication"], l["date_millesime_3e"])
# identité A3 = A1 + rev_m1(suivante) + rev_m2(celle d'après) quand mois simples
nid = 0; ko = []
for i in range(n_lignes - 2):
    l, l1, l2 = lignes[i], lignes[i + 1], lignes[i + 2]
    if l1["n_mois_nouveaux"] == 1 and l2["n_mois_nouveaux"] == 1 and l["date_millesime_3e"] == l2["date_publication"] \
            and None not in (l["emploi_3e_k"], l1["rev_m1_k"], l2["rev_m2_k"]):
        nid += 1
        if l["emploi_1re_k"] + l1["rev_m1_k"] + l2["rev_m2_k"] != l["emploi_3e_k"]:
            ko.append((str(l["date_publication"]), l["emploi_1re_k"] + l1["rev_m1_k"] + l2["rev_m2_k"], l["emploi_3e_k"]))
print(f"  identité A3 = A1 + rev_m1(v+1) + rev_m2(v+2): {nid} testées, {len(ko)} en défaut")
for k in ko:
    print("    ", k)
# revision_large : cohérence de fenêtre (0 => toutes les w de [v, v3] non larges)
non_larges = set()
for l in lignes:
    if l["revision_large"] == 0 and l["date_millesime_3e"]:
        for w in dp:
            if l["date_publication"] <= w <= l["date_millesime_3e"]:
                non_larges.add(w)
for l in lignes:
    if l["revision_large"] == 1 and l["date_millesime_3e"]:
        fen = [w for w in dp if l["date_publication"] <= w <= l["date_millesime_3e"]]
        if all(w in non_larges for w in fen):
            print("  revision_large=1 sans publication large possible:", l["date_publication"])
# publications larges déduites (les w qui ne sont pas dans non_larges)
larges_possibles = sorted(w for w in dp if w not in non_larges)
print("  publications pouvant être larges:", len(larges_possibles))
mois_larges = Counter(w.month for w in larges_possibles)
print("  par mois calendaire:", dict(sorted(mois_larges.items())))
# comptes de filtres
print("\n  lignes:", n_lignes, "complet=0:", sum(l["complet"] == 0 for l in lignes),
      "n_mois=2:", sum(l["n_mois_nouveaux"] == 2 for l in lignes),
      "revision_large=1:", sum(l["revision_large"] == 1 for l in lignes),
      "extreme=1:", sum(l["extreme"] == 1 for l in lignes), "principal:", n)
for l in lignes:
    if l["complet"] == 0:
        vides = [c for c in COLONNES if l[c] is None]
        print("  incomplet:", l["date_publication"], vides)
    if l["extreme"] == 1:
        print("  extreme:", l["date_publication"], l["emploi_1re_k"], l["emploi_3e_k"])
    if l["n_mois_nouveaux"] == 2:
        print("  double:", l["date_publication"], l["mois_reference"])
# valeurs implausibles
print("\n  max |y| sur P:", np.abs(y).max(), "à", P[int(np.abs(y).argmax())]["date_publication"])
print("  sd N:", X[:, 1].std(ddof=1), "sd y:", y.std(ddof=1))
for l in lignes:
    if l["dgs2_j"] is not None and l["dgs2_veille"] is not None and abs(l["dgs2_j"] - l["dgs2_veille"]) > 0.4:
        print("  grande variation du jour:", l["date_publication"], l["dgs2_veille"], l["dgs2_j"])
    if l["d_chomage_pt"] is not None and abs(l["d_chomage_pt"]) > 1:
        print("  grande variation du chômage:", l["date_publication"], l["d_chomage_pt"])
    if l["rev_m1_k"] is not None and abs(l["rev_m1_k"]) > 300 and l["principal"] == 1:
        print("  grande révision m1 dans P:", l["date_publication"], l["rev_m1_k"])
    if l["dgs2_j"] is not None and l["sveny02_j"] is not None and abs(l["dgs2_j"] - l["sveny02_j"]) > 0.3:
        print("  écart DGS2-SVENY02 > 0,3:", l["date_publication"], l["dgs2_j"], l["sveny02_j"])
print("  sveny02_j vides:", [str(l["date_publication"]) for l in lignes if l["sveny02_j"] is None])

# ======================= Fragilité =======================
print("\n=== fragilité ===")
XtX_inv = np.linalg.inv(X.T @ X)
dfbeta = (XtX_inv @ X.T)[1] * e / (1 - h)       # variation de beta quand on retire i
cook = (e ** 2 / (6 * (e @ e) / (n - 6))) * h / (1 - h) ** 2
ordre = np.argsort(-np.abs(dfbeta))[:5]
for i in ordre:
    keep = np.ones(n, bool); keep[i] = False
    bi, Vi, _, _ = ols_hc3(X[keep], y[keep])
    print(f"  sans {P[i]['date_publication']} (N={X[i,1]:.2f}, y={y[i]:.1f}, h={h[i]:.3f}, cook={cook[i]:.3f}):"
          f" beta={bi[1]:.3f} t={bi[1]/math.sqrt(Vi[1,1]):.2f}")
keep = np.ones(n, bool); keep[ordre] = False
bi, Vi, _, _ = ols_hc3(X[keep], y[keep])
print(f"  sans les cinq: beta={bi[1]:.3f} t={bi[1]/math.sqrt(Vi[1,1]):.2f}")
ordre_c = np.argsort(-cook)[:5]
print("  cinq plus grands Cook:", [str(P[i]["date_publication"]) for i in ordre_c])
dec = np.array([P[i]["date_publication"].year // 10 * 10 for i in range(n)])
for d in sorted(set(dec)):
    s = dec == d
    bi, Vi, _, _ = ols_hc3(X[s], y[s])
    bo, Vo, _, _ = ols_hc3(X[~s], y[~s])
    print(f"  décennie {d}: n={s.sum()} beta={bi[1]:.3f} t={bi[1]/math.sqrt(Vi[1,1]):.2f} | "
          f"sans elle: beta={bo[1]:.3f} t={bo[1]/math.sqrt(Vo[1,1]):.2f}")
