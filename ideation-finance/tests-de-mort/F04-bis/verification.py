"""Vérification indépendante F04-bis, écrite d'après preenregistrement.md seul.
Lit uniquement F04-bis_analyse.csv ; écrit verification.json."""
import csv, json, math, os
from collections import OrderedDict

ICI = os.path.dirname(os.path.abspath(__file__))
CHEMIN = os.path.join(ICI, "F04-bis_analyse.csv")

COLONNES = ["id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois",
            "date_j", "date_jm5", "date_jp5",
            "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5",
            "hs_jm5", "hs_j", "hs_jp5", "mc_jm5", "mc_j", "mc_jp5",
            "dans_exercice", "complet", "fenetre_propre"]
X = ["jm5", "j", "jp5"]
TAUX = [f"{s}_{x}" for s in ("cmt", "gsw", "hs", "mc") for x in X]
DEB, FIN = "2020-10-01", "2021-09-30"

brut = open(CHEMIN, "rb").read()
echecs = []
if brut.startswith(b"\xef\xbb\xbf"):
    echecs.append("format: marque d'ordre d'octets présente")
texte = brut.decode("utf-8")
lignes = list(csv.reader(texte.splitlines()))
entete, rows = lignes[0], [r for r in lignes[1:] if r != []]
rows = [dict(zip(entete, r)) for r in rows]


def num(v):
    if v is None or v.strip() == "":
        return None
    try:
        f = float(v)
    except ValueError:
        return None
    return f if math.isfinite(f) else None


# 1. colonnes
if entete != COLONNES:
    echecs.append(f"c1: colonnes {entete}")
# 2.
ids = [r["id_ligne"] for r in rows]
if len(set(ids)) != len(ids):
    echecs.append("c2: id_ligne non unique")
for r in rows:
    if r["echeance"] not in ("10", "20", "30"):
        echecs.append(f"c2: echeance {r['id_ligne']}")
    for c in ("dans_exercice", "complet", "fenetre_propre"):
        if r[c] not in ("0", "1"):
            echecs.append(f"c2: {c} {r['id_ligne']}")
# 3.
for r in rows:
    if not (r["date_jm5"] < r["date_j"] < r["date_jp5"]):
        echecs.append(f"c3: ordre des dates {r['id_ligne']}")
    if r["date_j"] != r["date_adjudication"]:
        echecs.append(f"c3: date_j != date_adjudication {r['id_ligne']}")
    if not (DEB <= r["date_adjudication"] <= FIN):
        echecs.append(f"c3: date hors exercice {r['id_ligne']}")
    if r["mois"] != r["date_adjudication"][:7]:
        echecs.append(f"c3: mois {r['id_ligne']}")
# 4.
for r in rows:
    att = "1" if (r["date_jm5"] >= DEB and r["date_jp5"] <= FIN) else "0"
    if r["dans_exercice"] != att:
        echecs.append(f"c4: dans_exercice {r['id_ligne']}")
# 5.
for r in rows:
    att = "1" if all(num(r[c]) is not None for c in TAUX) else "0"
    if r["complet"] != att:
        echecs.append(f"c5: complet {r['id_ligne']}")
    for c in TAUX:  # cellule non vide mais non numérique
        if r[c].strip() != "" and num(r[c]) is None:
            echecs.append(f"c5: valeur non numérique {c} {r['id_ligne']}")
# 6.
for r in rows:
    for c in TAUX:
        v = num(r[c])
        if v is not None and not (-1 <= v <= 20):
            echecs.append(f"c6: {c} hors [-1,20] {r['id_ligne']}")
    for x in X:
        a, b = num(r[f"cmt_{x}"]), num(r[f"gsw_{x}"])
        if a is not None and b is not None and abs(a - b) > 1:
            echecs.append(f"c6: |cmt-gsw|>1 {x} {r['id_ligne']}")
# 7.
differe = False
for r in rows:
    for x in X:
        a, b = num(r[f"hs_{x}"]), num(r[f"mc_{x}"])
        if a is not None and b is not None:
            if abs(a - b) > 0.25:
                echecs.append(f"c7: |hs-mc|>0.25 {x} {r['id_ligne']}")
            if a != b:
                differe = True
if not differe:
    echecs.append("c7: aucune paire hs/mc ne diffère")
# 8. (toutes les lignes du fichier)
ecart_max_tout = 0.0
for r in rows:
    for x in X:
        a, b = num(r[f"hs_{x}"]), num(r[f"cmt_{x}"])
        if a is not None and b is not None:
            e = abs(a - b)
            ecart_max_tout = max(ecart_max_tout, e)
            if e > 0.0051:
                echecs.append(f"c8: |hs-cmt|>0.0051 {x} {r['id_ligne']}")
# 9.
n_de = sum(r["dans_exercice"] == "1" for r in rows)
if len(rows) != 24:
    echecs.append(f"c9: {len(rows)} lignes")
if not (20 <= n_de <= 24):
    echecs.append(f"c9: {n_de} lignes dans_exercice")

# Hors contrôles numérotés : tri (section 4, format)
cles = [(r["date_adjudication"], int(r["echeance"])) for r in rows]
tri_ok = cles == sorted(cles)

schema_ok = 1 if not echecs else 0

# ---- Statistique (section 5)
P = [r for r in rows if r["dans_exercice"] == "1" and r["complet"] == "1" and r["fenetre_propre"] == "1"]


def f(r, c):
    return float(r[c])


def V(r, s):
    return 100 * (2 * (f(r, f"{s}_j") - f(r, "gsw_j")) - (f(r, f"{s}_jm5") - f(r, "gsw_jm5"))
                  - (f(r, f"{s}_jp5") - f(r, "gsw_jp5")))


def Dv(r):
    return 100 * (2 * (f(r, "hs_j") - f(r, "mc_j")) - (f(r, "hs_jm5") - f(r, "mc_jm5"))
                  - (f(r, "hs_jp5") - f(r, "mc_jp5")))


def et_groupee(vals, mois):
    N = len(vals)
    m = sum(vals) / N
    S = OrderedDict()
    for v, g in zip(vals, mois):
        S[g] = S.get(g, 0.0) + (v - m)
    G = len(S)
    return m, (1 / N) * math.sqrt(G / (G - 1) * sum(s * s for s in S.values()))


mois = [r["mois"] for r in P]
D = [Dv(r) for r in P]
Dalt = [V(r, "hs") - V(r, "mc") for r in P]  # contrôle de l'identité D = V_HS - V_MC
vhs = [V(r, "hs") for r in P]
vmc = [V(r, "mc") for r in P]
N, G = len(P), len(set(mois))
dm, det = et_groupee(D, mois)
binf, bsup = dm - 2.365 * det, dm + 2.365 * det
marge = min(0.9 - binf, bsup - 0.9)
vmc_m, vmc_et = et_groupee(vmc, mois)
ecart_max_P = 100 * max(abs(f(r, f"hs_{x}") - f(r, f"cmt_{x}")) for r in P for x in X)

out = OrderedDict([
    ("schema_ok", schema_ok),
    ("n_adjudications", N),
    ("n_grappes", G),
    ("ecart_max_hs_fred_pb", ecart_max_P),
    ("d_moyen_pb", dm),
    ("d_erreur_type_pb", det),
    ("d_borne_inf_95_pb", binf),
    ("d_borne_sup_95_pb", bsup),
    ("marge_zone_grise", marge),
    ("v_hs_moyen_pb", sum(vhs) / N),
    ("v_mc_moyen_pb", vmc_m),
    ("v_mc_erreur_type_pb", vmc_et),
])
with open(os.path.join(ICI, "verification.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

# ---- Diagnostics (console seulement)
print(json.dumps(out, indent=2))
print("echecs schema:", echecs)
print("tri ok:", tri_ok, "| ecart max hs-cmt toutes lignes (pb):", 100 * ecart_max_tout)
print("max |D - (Vhs-Vmc)|:", max(abs(a - b) for a, b in zip(D, Dalt)))
sd = math.sqrt(sum((d - dm) ** 2 for d in D) / (N - 1))
print("sd D (N-1):", sd)
for r, d, a, b in zip(P, D, vhs, vmc):
    print(r["id_ligne"], r["echeance"], f"D={d:.4f} Vhs={a:.4f} Vmc={b:.4f}")
print("moyennes mensuelles de D:")
for g in sorted(set(mois)):
    v = [d for d, m in zip(D, mois) if m == g]
    print(" ", g, len(v), round(sum(v) / len(v), 4))
print("moyenne de D sans chaque mois:")
for g in sorted(set(mois)):
    v = [d for d, m in zip(D, mois) if m != g]
    print(" ", g, round(sum(v) / len(v), 4))
print("moyenne de D sans chaque adjudication (extrêmes):")
loo = [(r["id_ligne"], sum(D[:i] + D[i + 1:]) / (N - 1)) for i, r in enumerate(P)]
print(" ", min(loo, key=lambda t: t[1]), max(loo, key=lambda t: t[1]))
for e in (10, 20, 30):
    idx = [i for i, r in enumerate(P) if r["echeance"] == str(e)]
    print("S1", e, len(idx), *(round(sum(L[i] for i in idx) / len(idx), 4) for L in (D, vhs, vmc)))
for x in X:
    print("S2", x, round(sum(100 * (f(r, f"hs_{x}") - f(r, f"mc_{x}")) for r in P) / N, 4))
print("S2 V cmt", round(sum(V(r, "cmt") for r in P) / N, 4))
# t-test sur les moyennes mensuelles, pour comparaison
mm = [sum(d for d, m in zip(D, mois) if m == g) / mois.count(g) for g in sorted(set(mois))]
mmm = sum(mm) / len(mm)
print("Student sur moyennes mensuelles: moy", mmm, "ET", math.sqrt(sum((a - mmm) ** 2 for a in mm) / (len(mm) - 1) / len(mm)))
# doublons
print("doublons (cusip,date):", len({(r['cusip'], r['date_adjudication']) for r in rows}) != len(rows))
