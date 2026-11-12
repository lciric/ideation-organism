"""Vérification indépendante H03 — écrite à partir de preenregistrement.md seul.
Lit uniquement H03_analyse.csv ; écrit verification.json et imprime un détail par bloc."""
import csv, json, math, re, sys
from pathlib import Path
import numpy as np
from scipy import stats

ICI = Path(__file__).resolve().parent
FICHIER = ICI / "H03_analyse.csv"

COLONNES = ["millesime", "t_millesime", "mois_titre", "t_premier_F", "horizon", "cible", "t_cible",
            "projection", "millesime_precedent", "projection_precedente", "millesime_realise",
            "t_lecture", "realise", "revision", "erreur"]
LETTRE_TRIM = {"W": 1, "S": 2, "G": 3, "A": 4}
TRIM_LETTRE = {v: k for k, v in LETTRE_TRIM.items()}


def an_code(yy):
    return 1999 if yy == "99" else 2000 + int(yy)


def t_code(code):
    return 4 * an_code(code[1:]) + LETTRE_TRIM[code[0]] - 1


def code_t(t):
    an, tr = divmod(t, 4)
    return f"{TRIM_LETTRE[tr + 1]}{an % 100:02d}"


LISTE = [f"{l}{a % 100:02d}" for a in range(1999, 2026) for l in "WSGA"] + ["W26", "S26", "G26"]
assert len(LISTE) == 111
T_LISTE = {t_code(c) for c in LISTE}


def fnum(s):
    return None if s == "" else float(s)


def inum(s):
    if s == "":
        return None
    f = float(s)
    if f != int(f):
        raise ValueError(s)
    return int(f)


def lire():
    with open(FICHIER, encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        entete = next(rd)
        lignes = [dict(zip(entete, r)) for r in rd]
    return entete, lignes


# ------------------------------------------------------------------ schéma
def controles(entete, L):
    v = {}
    anomalies = []
    v[1] = entete != COLONNES
    # 2
    couples = [(r.get("millesime"), r.get("horizon")) for r in L]
    mill = {r.get("millesime") for r in L}
    ok2 = (len(L) == 444 and len(set(couples)) == 444 and len(mill) == 111 and mill <= set(LISTE)
           and all(h in {"1", "2", "3", "4"} for _, h in couples))
    v[2] = not ok2
    # 3
    ok3 = True
    for r in L:
        try:
            tm, h, tc = int(r["t_millesime"]), int(r["horizon"]), int(r["t_cible"])
            an, tr = divmod(tc, 4)
            ok3 &= (tm == t_code(r["millesime"]) and tc == tm + h and r["cible"] == f"{an}-Q{tr + 1}")
        except Exception:
            ok3 = False
    v[3] = not ok3
    # 4
    ok4 = True
    for r in L:
        if r["mois_titre"] != "":
            try:
                ok4 &= inum(r["mois_titre"]) == 3 * LETTRE_TRIM[r["millesime"][0]]
            except Exception:
                ok4 = False
    v[4] = not ok4
    # 5
    ok5 = True
    for r in L:
        if r["t_premier_F"] != "":
            try:
                tf, tm = inum(r["t_premier_F"]), int(r["t_millesime"])
                ok5 &= tm - 2 <= tf <= tm + 1
            except Exception:
                ok5 = False
    v[5] = not ok5
    # 6
    ok6 = True
    pat = re.compile(r"^-?\d+(\.\d)?$")
    for r in L:
        for c in ("projection", "projection_precedente", "realise"):
            s = r[c]
            if s != "":
                ok6 &= bool(pat.match(s)) and -5 <= float(s) <= 15
    v[6] = not ok6
    # 7
    ok7 = True
    for r in L:
        for res, a, b in (("revision", "projection", "projection_precedente"), ("erreur", "realise", "projection")):
            vide_attendu = r[a] == "" or r[b] == ""
            if vide_attendu:
                ok7 &= r[res] == ""
            else:
                ok7 &= r[res] != "" and abs(float(r[res]) - (float(r[a]) - float(r[b]))) <= 1e-6
    v[7] = not ok7
    # 8
    ok8 = True
    for r in L:
        vide = r["realise"] == ""
        if vide:
            ok8 &= r["t_lecture"] == "" and r["millesime_realise"] == ""
        else:
            try:
                tl, tc = inum(r["t_lecture"]), int(r["t_cible"])
                ok8 &= (tl - tc in (2, 3, 4) and tl <= 8106 and r["millesime_realise"] in LISTE
                        and t_code(r["millesime_realise"]) == tl)
            except Exception:
                ok8 = False
    v[8] = not ok8
    # 9
    ok9 = True
    for r in L:
        if r["millesime"] == "W99":
            ok9 &= r["millesime_precedent"] == ""
        else:
            ok9 &= r["millesime_precedent"] == code_t(int(r["t_millesime"]) - 1)
    v[9] = not ok9
    # 10
    par_cible = {}
    ok10 = True
    for r in L:
        cle = (fnum(r["realise"]), inum(r["t_lecture"]))
        tc = r["t_cible"]
        if tc in par_cible:
            ok10 &= par_cible[tc] == cle
        else:
            par_cible[tc] = cle
    v[10] = not ok10
    # 11
    idx = {(r["millesime"], int(r["horizon"])): r for r in L}
    ok11 = True
    for r in L:
        h = int(r["horizon"])
        if h <= 3 and r["millesime"] != "W99":
            p = idx.get((r["millesime_precedent"], h + 1))
            a = fnum(r["projection_precedente"])
            b = fnum(p["projection"]) if p else None
            ok11 &= (a is None and b is None) or (a is not None and b is not None and abs(a - b) < 1e-9)
    v[11] = not ok11
    return v


# ------------------------------------------------------------------ statistique
def preparer(L):
    R = []
    for r in L:
        R.append(dict(m=r["millesime"], tm=int(r["t_millesime"]), h=int(r["horizon"]), tc=int(r["t_cible"]),
                      tl=inum(r["t_lecture"]), r=fnum(r["revision"]), e=fnum(r["erreur"])))
    return R


def regle(R, rev_key="r"):
    """Étape 2. Renvoie la liste des lignes évaluées avec b_i, c_i."""
    comp = [x for x in R if x[rev_key] is not None and x["e"] is not None]
    out = []
    for x in comp:
        if not (8016 <= x["tc"] <= 8103):
            continue
        A = [j for j in comp if j["h"] == x["h"] and j["tl"] is not None and j["tl"] <= x["tm"] and j is not x]
        n = len(A)
        if n < 8:
            continue
        rr = np.array([j[rev_key] for j in A]); ee = np.array([j["e"] for j in A])
        srr = float(((rr - rr.mean()) ** 2).sum())
        if not srr > 1e-12:
            continue
        b = float(((rr - rr.mean()) * (ee - ee.mean())).sum()) / srr
        out.append(dict(x, b=b, c=b * x[rev_key], nA=n, rv=x[rev_key]))
    return out


def blocs(ev, nmin=16):
    B = {}
    for k in range(11):
        l = [x for x in ev if (x["tc"] - 8016) // 8 == k]
        c = np.array([x["c"] for x in l]); e = np.array([x["e"] for x in l])
        scc, see = float((c * c).sum()), float((e * e).sum())
        valide = len(l) >= nmin and scc > 1e-12 and see > 1e-12
        info = dict(n=len(l), valide=valide)
        if valide:
            info["R"] = float((c * e).sum()) / math.sqrt(scc * see)
            info["Q"] = max(float(((e - c) ** 2).sum()) / see, 1e-6)
            info["see"] = see; info["sec"] = float(((e - c) ** 2).sum())
        B[k] = info
    return B


QUANT = {11: 1.8125, 10: 1.8331, 9: 1.8595, 8: 1.8946, 7: 1.9432, 6: 2.0150, 5: 2.1318}


def moyenne_et(B):
    ks = [k for k in B if B[k]["valide"]]
    K = len(ks)
    if K < 5:
        return K, 0.0, 0.0, 0.0, 0.0
    Rk = {k: B[k]["R"] for k in ks}
    rb = sum(Rk.values()) / K
    g0 = sum((Rk[k] - rb) ** 2 for k in ks) / (K - 1)
    g1 = sum((Rk[k] - rb) * (Rk[k + 1] - rb) for k in ks if k + 1 in Rk) / (K - 1)
    et = math.sqrt((g0 + 2 * max(g1, 0.0)) / K)
    return K, rb, et, g0, g1


def main():
    entete, L = lire()
    v = controles(entete, L)
    nviol = sum(1 for k in v if v[k])
    R = preparer(L)
    ev = regle(R)
    B = blocs(ev)
    K, rb, et, g0, g1 = moyenne_et(B)
    if K >= 5:
        q = QUANT.get(K, float(stats.t.ppf(0.95, K - 1)))
        bb, bh = rb - q * et, rb + q * et
        hors = [B[k]["R"] for k in B if B[k]["valide"] and k not in (8, 9)]
        r_hors = sum(hors) / len(hors) if hors else 0.0
        geo = math.exp(sum(math.log(B[k]["Q"]) for k in B if B[k]["valide"]) / K)
    else:
        q = float("nan"); bb = bh = r_hors = 0.0; geo = 1.0
    marge = min(-bb, bh - 0.22)
    conflit = 1 if (bb > 0 and (r_hors <= 0 or geo >= 1)) else 0

    # S1
    s1 = sorted([x for x in ev if False], key=lambda x: x["tm"])  # placeholder
    comp = [x for x in R if x["r"] is not None and x["e"] is not None]
    s1 = []
    for x in comp:
        if x["h"] != 4 or x["tm"] < 8080:
            continue
        A = [j for j in comp if j["h"] == 4 and j["tl"] is not None and j["tl"] <= x["tm"] and j is not x]
        if len(A) < 8:
            continue
        rr = np.array([j["r"] for j in A]); ee = np.array([j["e"] for j in A])
        srr = float(((rr - rr.mean()) ** 2).sum())
        if not srr > 1e-12:
            continue
        b = float(((rr - rr.mean()) * (ee - ee.mean())).sum()) / srr
        s1.append(dict(x, b=b, c=b * x["r"]))
    s1.sort(key=lambda x: x["tm"])
    n1 = len(s1)
    if n1 == 0:
        rap1, p1 = 1.0, 1.0
    else:
        e = np.array([x["e"] for x in s1]); c = np.array([x["c"] for x in s1])
        rap1 = float(((e - c) ** 2).sum() / (e * e).sum())
        d = e ** 2 - (e - c) ** 2
        db = d.mean()
        gam = [float(((d[j:] - db) * (d[:n1 - j] - db)).sum() / n1) for j in range(4)]
        V = (gam[0] + 2 * (gam[1] + gam[2] + gam[3])) / n1
        if n1 < 8 or V <= 0:
            p1 = 1.0
        else:
            dm = db / math.sqrt(V)
            dms = dm * math.sqrt((n1 + 1 - 8 + 12 / n1) / n1)
            p1 = float(stats.t.sf(dms, n1 - 1))

    # S2
    e = np.array([x["e"] for x in ev]); c = np.array([x["c"] for x in ev])
    rap_glob = float(((e - c) ** 2).sum() / (e * e).sum())
    m = np.array([not (8084 <= x["tc"] <= 8091) for x in ev])
    rap_hors = float(((e[m] - c[m]) ** 2).sum() / (e[m] ** 2).sum())
    G = int((np.abs(e - c) < np.abs(e) - 1e-9).sum()); P = int((np.abs(e - c) > np.abs(e) + 1e-9).sum())
    taux = G / (G + P) if G + P > 0 else 0.5
    part_b = float(np.mean([x["b"] > 0 for x in ev]))
    rh = {}
    rh_det = {}
    for h in range(1, 5):
        Bh = blocs([x for x in ev if x["h"] == h], nmin=4)
        vals = [Bh[k]["R"] for k in Bh if Bh[k]["valide"]]
        rh[h] = sum(vals) / len(vals) if vals else 0.0
        rh_det[h] = {k: (round(Bh[k]["R"], 3) if Bh[k]["valide"] else None) for k in Bh}

    # S3 placebo
    idx = {(x["tm"], x["h"]): x for x in R}
    for x in R:
        y = idx.get((x["tm"] - 8, x["h"]))
        x["rp"] = y["r"] if y is not None else None
    evp = regle(R, "rp")
    Bp = blocs(evp)
    Kp, rbp, etp, _, _ = moyenne_et(Bp)

    res = dict(
        n_violations_schema=nviol, n_obs_evaluees=len(ev), n_blocs=K, r_moyen=rb, et_r_moyen=et,
        borne_basse_ic90=bb, borne_haute_ic90=bh, marge_indecision=marge, r_hors_episode=r_hors,
        rapport_eqm_geo=geo, conflit_gardes=conflit, n_obs_h4_2020=n1, rapport_eqm_h4_2020=rap1,
        p_dm_hln_h4_2020=p1, rapport_eqm_global=rap_glob, rapport_eqm_hors_2021_2022=rap_hors,
        taux_amelioration=taux, part_b_positif=part_b, r_moyen_h1=rh[1], r_moyen_h2=rh[2],
        r_moyen_h3=rh[3], r_moyen_h4=rh[4], r_moyen_placebo=rbp, et_r_placebo=etp, n_blocs_placebo=Kp)
    (ICI / "verification.json").write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")

    # ---- détail (sortie console, pour le rapport)
    print("controles violes:", [k for k in v if v[k]])
    print(f"K={K} R={rb:.4f} ET={et:.4f} g0={g0:.5f} g1={g1:.5f} q={q}")
    for k in range(11):
        b = B[k]
        ann = 2004 + 2 * k
        bs = [x["b"] for x in ev if (x["tc"] - 8016) // 8 == k]
        print(f"bloc {k:2d} {ann}-{ann + 1}: n={b['n']:2d} valide={int(b['valide'])}",
              f"R={b.get('R', float('nan')):+.3f} Q={b.get('Q', float('nan')):.3f}",
              f"see={b.get('see', float('nan')):.2f} b_moy={np.mean(bs) if bs else float('nan'):+.3f}",
              f"Rp={Bp[k].get('R', float('nan')):+.3f} np={Bp[k]['n']}")
    print("R par horizon et bloc:", rh_det)
    print("G,P", G, P, "S1 n", n1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
