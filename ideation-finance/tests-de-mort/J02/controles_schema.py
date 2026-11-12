"""J02 - les 11 controles de schema de la section 5 de la preinscription, appliques au seul fichier J02_analyse.csv.
Renvoie le detail par controle ; n_violations_schema = nombre de controles violes (un controle est viole s'il echoue sur
une seule ligne)."""
import csv, math, pathlib, re

COLONNES = ["cible", "t_cible", "annee_cible", "millesime_h2", "t_millesime_h2", "mois_titre_h2", "annee_titre_h2",
            "t_premier_F_h2", "statut_h2", "projection_h2", "millesime_h3", "t_millesime_h3", "mois_titre_h3",
            "annee_titre_h3", "t_premier_F_h3", "statut_h3", "projection_h3", "indice_m1", "indice_m2", "indice_m3",
            "indice_an_avant_m1", "indice_an_avant_m2", "indice_an_avant_m3", "realise", "revision", "erreur"]
LETTRE_TRIM = {"W": 1, "G": 2, "S": 3, "A": 4}


def liste_millesimes():
    out = [f"{l}{an % 100:02d}" for an in range(1999, 2026) for l in "WGSA"] + ["W26"]
    assert len(out) == 109
    return out


def annee_code(code):
    yy = int(code[1:])
    return 1900 + yy if yy >= 99 else 2000 + yy


def t_code(code):
    return 4 * annee_code(code) + LETTRE_TRIM[code[0]] - 1


def _f(x):
    return None if x == "" else float(x)


def _i(x):
    if x == "" or not re.fullmatch(r"-?\d+", x):
        return None
    return int(x)


def controler(chemin):
    with open(chemin, encoding="utf-8", newline="") as fh:
        lignes = list(csv.reader(fh))
    entete, corps = lignes[0], lignes[1:]
    res = {}
    res[1] = entete == COLONNES
    if not res[1]:
        return {"n_violations_schema": 11, "detail": {str(k): False for k in range(1, 12)}}
    rows = [dict(zip(COLONNES, r)) for r in corps]
    ok_len = all(len(r) == 26 for r in corps)
    ts = [_i(r["t_cible"]) for r in rows]
    res[2] = ok_len and len(rows) == 108 and ts == list(range(7999, 8107))
    ok3 = True
    for r, t in zip(rows, ts):
        if t is None:
            ok3 = False; continue
        an, q = divmod(t, 4)
        ok3 &= r["cible"] == f"{an}-Q{q + 1}" and _i(r["annee_cible"]) == an
    res[3] = ok3
    codes = set(liste_millesimes())
    ok4 = ok5 = ok6 = ok7 = ok8 = ok9 = ok10 = True
    for r, t in zip(rows, ts):
        for h in (2, 3):
            c = r[f"millesime_h{h}"]; tm = _i(r[f"t_millesime_h{h}"])
            ok4 &= t is not None and tm == t - h and c in codes and t_code(c) == tm
            if c in codes:
                ok5 &= _i(r[f"mois_titre_h{h}"]) == 3 * LETTRE_TRIM[c[0]] and _i(r[f"annee_titre_h{h}"]) == annee_code(c)
            else:
                ok5 = False
            ok6 &= tm is not None and _i(r[f"t_premier_F_h{h}"]) == tm
            p = r[f"projection_h{h}"]
            if p != "":
                ok7 &= r[f"statut_h{h}"] == "F"
                ok8 &= bool(re.fullmatch(r"-?\d+(\.\d)?", p)) and -5 <= float(p) <= 15
        ind = [_f(r[c]) for c in COLONNES[17:23]]
        for v in ind:
            if v is not None:
                ok8 &= 20 <= v <= 300
        rea = _f(r["realise"])
        if rea is not None:
            ok8 &= -5 <= rea <= 15
        if any(v is None for v in ind):
            ok9 &= rea is None
        else:
            att = 100 * ((ind[0] + ind[1] + ind[2]) / (ind[3] + ind[4] + ind[5]) - 1)
            ok9 &= rea is not None and abs(rea - att) <= 1e-6
        p2, p3, rev, err = _f(r["projection_h2"]), _f(r["projection_h3"]), _f(r["revision"]), _f(r["erreur"])
        if p2 is None or p3 is None:
            ok10 &= rev is None
        else:
            ok10 &= rev is not None and abs(rev - (p2 - p3)) <= 1e-6
        if rea is None or p2 is None:
            ok10 &= err is None
        else:
            ok10 &= err is not None and abs(err - (rea - p2)) <= 1e-6
    res[4], res[5], res[6], res[7], res[8], res[9], res[10] = ok4, ok5, ok6, ok7, ok8, ok9, ok10
    par_t = {t: r for r, t in zip(rows, ts) if t is not None}
    ok11 = True
    for t, r in par_t.items():
        if t - 4 in par_t:
            for k in (1, 2, 3):
                a, b = _f(r[f"indice_an_avant_m{k}"]), _f(par_t[t - 4][f"indice_m{k}"])
                if a is not None and b is not None:
                    ok11 &= a == b
    res[11] = ok11
    n = sum(1 for k in range(1, 12) if not res[k])
    return {"n_violations_schema": n, "detail": {str(k): bool(v) for k, v in res.items()}}


if __name__ == "__main__":
    import sys, json
    print(json.dumps(controler(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "J02_analyse.csv")))
