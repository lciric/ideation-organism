"""Vérification indépendante H03-v2, écrite à partir de preenregistrement.md seul.
Lit H03-v2_analyse.csv, refait les contrôles de schéma, la règle récursive, R̄, ET, gardes, S1-S3.
Écrit verification.json et imprime un détail bloc par bloc."""
import csv, json, math, re, sys
from pathlib import Path
from scipy import stats

ICI = Path(__file__).resolve().parent
FICHIER = ICI / "H03-v2_analyse.csv"

COLONNES = ["millesime", "t_millesime", "mois_titre", "t_premier_F", "horizon", "cible", "t_cible",
            "projection", "millesime_precedent", "projection_precedente", "millesime_realise",
            "t_lecture", "realise", "revision", "erreur"]
LETTRE_TRIM = {"W": 1, "G": 2, "S": 3, "A": 4}
TRIM_LETTRE = {v: k for k, v in LETTRE_TRIM.items()}


def annee_code(yy):
    return 1999 if yy == "99" else 2000 + int(yy)


LISTE = [f"{l}{(str(a)[2:])}" for a in range(1999, 2026) for l in "WGSA"] + ["W26", "G26", "S26"]
assert len(LISTE) == 111


def t_code(code):
    return 4 * annee_code(code[1:]) + LETTRE_TRIM[code[0]] - 1


CODE_DE_T = {t_code(c): c for c in LISTE}


def cible_de_t(t):
    return f"{t // 4}-Q{t % 4 + 1}"


Q95 = {11: 1.8125, 10: 1.8331, 9: 1.8595, 8: 1.8946, 7: 1.9432, 6: 2.0150, 5: 2.1318}

# ---------------------------------------------------------------- lecture
with open(FICHIER, newline="", encoding="utf-8") as f:
    lecteur = csv.reader(f)
    entete = next(lecteur)
    brut = [r for r in lecteur]

violations = {}
notes = []


def num(s):
    return None if s.strip() == "" else float(s)


def ent(s):
    return None if s.strip() == "" else int(s)


# contrôle 1
violations[1] = entete != COLONNES
lignes = [dict(zip(entete, r)) for r in brut]

# contrôle 2
c2 = len(lignes) != 444
couples = [(l["millesime"], l["horizon"]) for l in lignes]
if len(set(couples)) != len(couples):
    c2 = True
mill = set(l["millesime"] for l in lignes)
if len(mill) != 111 or not mill <= set(LISTE):
    c2 = True
for m in LISTE:
    for h in "1234":
        if (m, h) not in set(couples):
            c2 = True
violations[2] = c2

# contrôle 3
c3 = False
for l in lignes:
    try:
        tm = int(l["t_millesime"]); h = int(l["horizon"]); tc = int(l["t_cible"])
        if l["millesime"] in LISTE and tm != t_code(l["millesime"]):
            c3 = True
        if tc != tm + h or l["cible"] != cible_de_t(tc):
            c3 = True
    except Exception:
        c3 = True
violations[3] = c3

# contrôle 4
c4_n = 0
for l in lignes:
    mt = ent(l["mois_titre"])
    if mt is not None and mt != 3 * LETTRE_TRIM[l["millesime"][0]]:
        c4_n += 1
violations[4] = c4_n > 0

# contrôle 5
c5 = False
for l in lignes:
    pf = ent(l["t_premier_F"])
    if pf is not None and not (int(l["t_millesime"]) - 2 <= pf <= int(l["t_millesime"]) + 1):
        c5 = True
violations[5] = c5

# contrôle 6
c6 = False
motif = re.compile(r"^-?\d+(\.\d)?$")
for l in lignes:
    for c in ("projection", "projection_precedente", "realise"):
        s = l[c].strip()
        if s == "":
            continue
        if not motif.match(s) or not (-5 <= float(s) <= 15):
            c6 = True
violations[6] = c6

# contrôle 7
c7 = False
for l in lignes:
    p, pp, re_, rv, er = (num(l[c]) for c in ("projection", "projection_precedente", "realise", "revision", "erreur"))
    if (rv is None) != (p is None or pp is None):
        c7 = True
    elif rv is not None and abs(rv - (p - pp)) > 1e-6:
        c7 = True
    if (er is None) != (re_ is None or p is None):
        c7 = True
    elif er is not None and abs(er - (re_ - p)) > 1e-6:
        c7 = True
violations[7] = c7

# contrôle 8
c8 = False
for l in lignes:
    vide_r = l["realise"].strip() == ""
    if (l["t_lecture"].strip() == "") != vide_r or (l["millesime_realise"].strip() == "") != vide_r:
        c8 = True
        continue
    if not vide_r:
        tl = int(l["t_lecture"]); tc = int(l["t_cible"])
        if tl - tc not in (2, 3, 4) or tl > 8106 or CODE_DE_T.get(tl) != l["millesime_realise"]:
            c8 = True
violations[8] = c8

# contrôle 9
c9 = False
for l in lignes:
    tm = int(l["t_millesime"])
    attendu = CODE_DE_T.get(tm - 1, "")
    if l["millesime"] == "W99":
        attendu = ""
    if l["millesime_precedent"] != attendu:
        c9 = True
violations[9] = c9

# contrôle 10
c10 = False
par_cible = {}
for l in lignes:
    cle = int(l["t_cible"])
    par_cible.setdefault(cle, set()).add((num(l["realise"]), ent(l["t_lecture"])))
for v in par_cible.values():
    if len(v) > 1:
        c10 = True
violations[10] = c10

# contrôle 11
c11 = False
index = {(l["millesime"], int(l["horizon"])): l for l in lignes}
for l in lignes:
    h = int(l["horizon"])
    if h <= 3 and l["millesime_precedent"]:
        prec = index.get((l["millesime_precedent"], h + 1))
        a = num(l["projection_precedente"]); b = num(prec["projection"]) if prec else None
        if not ((a is None and b is None) or (a is not None and b is not None and abs(a - b) < 1e-9)):
            c11 = True
violations[11] = c11

n_violations = sum(1 for v in violations.values() if v)

# tri (hors des 11 contrôles numérotés)
cles_tri = [(int(l["t_millesime"]), int(l["horizon"])) for l in lignes]
tri_ok = cles_tri == sorted(cles_tri)

# ---------------------------------------------------------------- cohérence des millésimes
coh = {"tri_ok": tri_ok, "mois_titre_desaccords": c4_n,
       "mois_titre_vides": sum(1 for l in lignes if l["mois_titre"].strip() == "")}
pf_par_m = {}
for l in lignes:
    pf_par_m[l["millesime"]] = ent(l["t_premier_F"])
coh["premier_F_egal_t_millesime"] = sum(1 for m in LISTE if pf_par_m.get(m) == t_code(m))
coh["premier_F_ecarts"] = {m: (pf_par_m.get(m), t_code(m)) for m in LISTE if pf_par_m.get(m) != t_code(m)}
# successions dans l'ordre du fichier
ordre = []
for l in lignes:
    if l["millesime"] not in ordre:
        ordre.append(l["millesime"])
pas = [(a, b, pf_par_m[b] - pf_par_m[a]) for a, b in zip(ordre, ordre[1:])
       if pf_par_m[a] is not None and pf_par_m[b] is not None]
coh["successions_pas_different_de_1"] = [p for p in pas if p[2] != 1]
# horizon 1 : cible strictement après le premier trimestre F
coh["h1_cible_apres_premier_F"] = sum(1 for l in lignes if l["horizon"] == "1" and pf_par_m[l["millesime"]] is not None
                                     and int(l["t_cible"]) > pf_par_m[l["millesime"]])
coh["h1_lignes"] = sum(1 for l in lignes if l["horizon"] == "1")
coh["h1_projection_vide"] = sum(1 for l in lignes if l["horizon"] == "1" and l["projection"].strip() == "")
coh["projection_vides"] = sum(1 for l in lignes if l["projection"].strip() == "")
coh["proj_prec_vides"] = sum(1 for l in lignes if l["projection_precedente"].strip() == "")
coh["realise_presents"] = sum(1 for l in lignes if l["realise"].strip() != "")
coh["ecart_lecture"] = {}
for l in lignes:
    if l["t_lecture"].strip():
        d = int(l["t_lecture"]) - int(l["t_cible"])
        coh["ecart_lecture"][d] = coh["ecart_lecture"].get(d, 0) + 1

# ---------------------------------------------------------------- statistique
rows = []
for l in lignes:
    rows.append(dict(m=l["millesime"], tm=int(l["t_millesime"]), h=int(l["horizon"]), tc=int(l["t_cible"]),
                     tl=ent(l["t_lecture"]), r=num(l["revision"]), e=num(l["erreur"])))


def pente(r, A):
    """A : liste de (r_j, e_j). Renvoie b ou None si non évaluable."""
    n = len(A)
    if n < 8:
        return None, n
    rb = sum(x for x, _ in A) / n
    eb = sum(y for _, y in A) / n
    srr = sum((x - rb) ** 2 for x, _ in A)
    if not srr > 1e-12:
        return None, n
    return sum((x - rb) * (y - eb) for x, y in A) / srr, n


def regle(rows, rev):
    """rev(i) -> révision utilisée (ou None). Renvoie liste des lignes évaluées (dict + b, c)."""
    complets = [x for x in rows if rev(x) is not None and x["e"] is not None]
    evaluees = []
    for x in complets:
        if not (8016 <= x["tc"] <= 8103):
            continue
        A = [(rev(y), y["e"]) for y in complets if y["h"] == x["h"] and y["tl"] is not None and y["tl"] <= x["tm"]]
        b, n = pente(rev(x), A)
        if b is None:
            continue
        evaluees.append(dict(x, rr=rev(x), b=b, c=b * rev(x), nA=n, k=(x["tc"] - 8016) // 8))
    return evaluees


def blocs(evaluees, min_lignes=16):
    out = {}
    for k in range(11):
        L = [x for x in evaluees if x["k"] == k]
        sce = sum(x["e"] ** 2 for x in L)
        scc = sum(x["c"] ** 2 for x in L)
        sce_ = sum(x["c"] * x["e"] for x in L)
        valide = len(L) >= min_lignes and scc > 1e-12 and sce > 1e-12
        R = sce_ / math.sqrt(scc * sce) if valide else None
        Q = sum((x["e"] - x["c"]) ** 2 for x in L) / sce if valide else None
        out[k] = dict(n=len(L), valide=valide, R=R, Q=Q, sce=sce, scc=scc,
                      bpos=sum(1 for x in L if x["b"] > 0))
    return out


def moyenne_et(B):
    ks = [k for k in sorted(B) if B[k]["valide"]]
    K = len(ks)
    if K < 5:
        return K, None, None
    R = {k: B[k]["R"] for k in ks}
    rbar = sum(R.values()) / K
    g0 = sum((v - rbar) ** 2 for v in R.values()) / (K - 1)
    g1 = sum((R[k] - rbar) * (R[k + 1] - rbar) for k in ks if k + 1 in R) / (K - 1)
    et = math.sqrt((g0 + 2 * max(g1, 0.0)) / K)
    return K, rbar, et, g0, g1


ev = regle(rows, lambda x: x["r"])
B = blocs(ev)
res = moyenne_et(B)
K = res[0]
out = {}
out["n_violations_schema"] = n_violations
out["n_obs_evaluees"] = len(ev)
out["n_blocs"] = K
if K < 5:
    out.update(r_moyen=0, et_r_moyen=0, borne_basse_ic90=0, borne_haute_ic90=0, r_hors_episode=0, rapport_eqm_geo=1)
    g0 = g1 = None
else:
    _, rbar, et, g0, g1 = res
    q = Q95[K]
    out["r_moyen"] = rbar
    out["et_r_moyen"] = et
    out["borne_basse_ic90"] = rbar - q * et
    out["borne_haute_ic90"] = rbar + q * et
    hors = [B[k]["R"] for k in B if B[k]["valide"] and k not in (8, 9)]
    out["r_hors_episode"] = sum(hors) / len(hors) if hors else 0.0
    logs = [math.log(max(B[k]["Q"], 1e-6)) for k in B if B[k]["valide"]]
    out["rapport_eqm_geo"] = math.exp(sum(logs) / len(logs))
out["marge_indecision"] = min(-out["borne_basse_ic90"], out["borne_haute_ic90"] - 0.22)
out["conflit_gardes"] = 1 if (out["borne_basse_ic90"] > 0 and (out["r_hors_episode"] <= 0 or out["rapport_eqm_geo"] >= 1)) else 0

# S1
complets = [x for x in rows if x["r"] is not None and x["e"] is not None]
s1 = []
for x in sorted(complets, key=lambda z: z["tm"]):
    if x["h"] != 4 or x["tm"] < 8080:
        continue
    A = [(y["r"], y["e"]) for y in complets if y["h"] == 4 and y["tl"] is not None and y["tl"] <= x["tm"]]
    b, n = pente(x["r"], A)
    if b is None:
        continue
    s1.append((x["e"], b * x["r"], x["m"], x["tc"]))
n = len(s1)
out["n_obs_h4_2020"] = n
if n == 0:
    out["rapport_eqm_h4_2020"] = 1.0
else:
    out["rapport_eqm_h4_2020"] = sum((e - c) ** 2 for e, c, *_ in s1) / sum(e ** 2 for e, *_ in s1)
p = 1.0
dm_detail = None
if n >= 8:
    d = [e ** 2 - (e - c) ** 2 for e, c, *_ in s1]
    db = sum(d) / n
    gam = [sum((d[i] - db) * (d[i - j] - db) for i in range(j, n)) / n for j in range(4)]
    V = (gam[0] + 2 * (gam[1] + gam[2] + gam[3])) / n
    if V > 0:
        DM = db / math.sqrt(V)
        DMs = DM * math.sqrt((n + 1 - 8 + 12 / n) / n)
        p = float(stats.t.sf(DMs, n - 1))
        dm_detail = dict(dbar=db, V=V, DM=DM, DMstar=DMs)
out["p_dm_hln_h4_2020"] = p

# S2
se2 = sum(x["e"] ** 2 for x in ev)
out["rapport_eqm_global"] = sum((x["e"] - x["c"]) ** 2 for x in ev) / se2
hors = [x for x in ev if not (8084 <= x["tc"] <= 8091)]
out["rapport_eqm_hors_2021_2022"] = sum((x["e"] - x["c"]) ** 2 for x in hors) / sum(x["e"] ** 2 for x in hors)
G = sum(1 for x in ev if abs(x["e"] - x["c"]) < abs(x["e"]) - 1e-9)
P = sum(1 for x in ev if abs(x["e"] - x["c"]) > abs(x["e"]) + 1e-9)
out["taux_amelioration"] = G / (G + P) if G + P else 0.5
out["part_b_positif"] = sum(1 for x in ev if x["b"] > 0) / len(ev)
par_h = {}
for h in range(1, 5):
    Bh = blocs([x for x in ev if x["h"] == h], min_lignes=4)
    Rs = [Bh[k]["R"] for k in Bh if Bh[k]["valide"]]
    out[f"r_moyen_h{h}"] = sum(Rs) / len(Rs) if Rs else 0.0
    par_h[h] = {k: (Bh[k]["n"], Bh[k]["R"]) for k in Bh}

# S3 placebo
idx = {(x["tm"], x["h"]): x for x in rows}


def rev_placebo(x):
    y = idx.get((x["tm"] - 8, x["h"]))
    return None if y is None else y["r"]


evp = regle(rows, rev_placebo)
Bp = blocs(evp)
resp = moyenne_et(Bp)
if resp[0] < 5:
    out["r_moyen_placebo"] = 0.0
    out["et_r_placebo"] = 0.0
else:
    out["r_moyen_placebo"] = resp[1]
    out["et_r_placebo"] = resp[2]
out["n_blocs_placebo"] = resp[0]

CHAMPS = ["n_violations_schema", "n_obs_evaluees", "n_blocs", "r_moyen", "et_r_moyen", "borne_basse_ic90",
          "borne_haute_ic90", "marge_indecision", "r_hors_episode", "rapport_eqm_geo", "conflit_gardes",
          "n_obs_h4_2020", "rapport_eqm_h4_2020", "p_dm_hln_h4_2020", "rapport_eqm_global",
          "rapport_eqm_hors_2021_2022", "taux_amelioration", "part_b_positif", "r_moyen_h1", "r_moyen_h2",
          "r_moyen_h3", "r_moyen_h4", "r_moyen_placebo", "et_r_placebo", "n_blocs_placebo"]
final = {c: out[c] for c in CHAMPS}
(ICI / "verification.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- détail (sortie console)
print("violations par contrôle:", {k: int(v) for k, v in violations.items()}, "désaccords mois:", c4_n)
print("cohérence:", json.dumps(coh, default=str))
print("g0, g1:", g0, g1)
print("bloc  années     n  bpos   R_k      Q_k     sum e2   | placebo n R")
for k in range(11):
    b = B[k]; bp = Bp[k]
    print(f"{k:>3}  {2004+2*k}-{2005+2*k}  {b['n']:>3} {b['bpos']:>4}  "
          f"{(b['R'] if b['R'] is not None else float('nan')):+.4f}  {(b['Q'] if b['Q'] is not None else float('nan')):.4f}  {b['sce']:8.2f}"
          f"   | {bp['n']:>3} {(bp['R'] if bp['R'] is not None else float('nan')):+.4f}")
print("par horizon (n, R):", json.dumps(par_h))
print("S1:", [(m, tc, round(e, 2), round(c, 3)) for e, c, m, tc in s1], dm_detail)
print("lignes évaluées par horizon:", {h: sum(1 for x in ev if x["h"] == h) for h in range(1, 5)})
print("nA min:", min(x["nA"] for x in ev), "première ligne évaluée par h:",
      {h: min((x["tc"] for x in ev if x["h"] == h), default=None) for h in range(1, 5)})
for c in CHAMPS:
    print(c, final[c])
