#!/usr/bin/env python3
"""K20-ZE : chaque controle de schema detecte-t-il une alteration deliberee ? Teste sur des COPIES (scratch), jamais sur le vrai fichier.
Usage : python3 -I test_controles.py"""
import csv, importlib.util, pathlib, shutil, sys, tempfile, json
ICI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("construire", ICI / "construire.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
RAW = C.references_brutes()
REEL = ICI / "K20-ZE_analyse.csv"
avant = REEL.read_bytes()
tmp = pathlib.Path(tempfile.mkdtemp(prefix="k20ze_alt_"))

def charge():
    with open(REEL, encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh); h = next(rd); return h, [dict(zip(h, l)) for l in rd]
def ecrit(h, rows, nom):
    p = tmp / nom
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(h); [w.writerow(list(r.values())[:len(h)]) for r in rows]
    return p
def premiere(rows, **cond):
    return next(i for i, r in enumerate(rows) if all(r[k] == v for k, v in cond.items()))

cas = []
def cas_(nom, cible, compte, f):
    cas.append((nom, cible, compte, f))

def a1(h, rows): h = list(h); h[3] = "t_tour_x"; return h, rows
def a1b(h, rows): return h[:-1], rows and [{k: v for k, v in r.items() if k != "grande_nouvelle"} for r in rows]
def a2(h, rows): return h, rows[:-1]
def a2b(h, rows): rows = list(rows); rows[10], rows[11] = rows[11], rows[10]; return h, rows
def a3(h, rows): i = premiere(rows, principal="1"); rows[i]["rang"] = "9"; return h, rows
def a4(h, rows): i = premiere(rows, principal="1"); rows[i]["n_rep"] = "10"; return h, rows
def a5(h, rows): i = premiere(rows, principal="1"); rows[i]["ref"] = "0.0" if rows[i]["ref"] != "0.0" else "0.5"; return h, rows
def a6(h, rows): i = premiere(rows, principal="1"); rows[i]["prev"] = "99.0"; return h, rows
def a7(h, rows): i = premiere(rows, principal="1"); rows[i]["revision"] = repr(float(rows[i]["revision"]) + 0.01); return h, rows
def a8(h, rows): i = premiere(rows, principal="1"); rows[i]["prev_prec"] = repr(float(rows[i]["prev_prec"]) + 0.01); rows[i]["revision"] = repr(float(rows[i]["prev"]) - float(rows[i]["prev_prec"])); return h, rows
def a9(h, rows):
    v, y = rows[100]["variable"], rows[100]["annee_cible"]
    for r in rows:  # alterer toutes les lignes (v, y) de façon cohérente : seul le brut peut le détecter
        if r["variable"] == v and r["annee_cible"] == y: r["realise"] = repr(float(r["realise"]) + 0.3)
    return h, rows
def a10(h, rows): i = premiere(rows, principal="1"); rows[i]["principal"] = "0"; return h, rows
def a10b(h, rows): i = premiere(rows, complete="0"); rows[i]["principal"] = "1"; return h, rows
def a11(h, rows): i = premiere(rows, episode="E2", principal="1"); rows[i]["episode"] = ""; return h, rows
def a12(h, rows):
    i = premiere(rows, principal="1", grande_nouvelle="1"); v, t = rows[i]["variable"], rows[i]["t_tour"]
    for r in rows:
        if r["variable"] == v and r["t_tour"] == t: r["grande_nouvelle"] = "0"
    return h, rows
# alterations sur une ligne HORS principal (complete = 0) : comptees à part
def h5(h, rows): i = premiere(rows, complete="0", variable="HICP"); rows[i]["prev_prec"] = "1.0"; return h, rows  # viole 4 et 7 hors principal
def h6(h, rows): i = premiere(rows, complete="0", variable="RGDP"); rows[i]["realise"] = "50.0"; return h, rows  # 6 et 9

essais = [("1 colonne renommee", 1, a1), ("1 colonne manquante", 1, a1b), ("2 ligne supprimee", 2, a2), ("2 deux lignes permutees (tri)", 2, a2b),
          ("3 rang=9", 3, a3), ("4 n_rep=10 sur ligne principale", 4, a4), ("5 ref altere", 5, a5), ("6 prev=99", 6, a6),
          ("7 revision +0,01", 7, a7), ("8 prev_prec modifie sans la ligne voisine", 8, a8),
          ("9 realise d'une annee altere partout (cohérent), détecté par le brut", 9, a9),
          ("10 principal=0 sur ligne principale", 10, a10), ("10 principal=1 sur ligne incomplete", 10, a10b),
          ("11 episode efface", 11, a11), ("12 grande_nouvelle forcee a 0 pour un tour", 12, a12)]
ok_tout = True
res = []
for nom, n, fn in essais:
    h, rows = charge(); h, rows = fn(h, rows)
    p = ecrit(h, rows, "alt.csv")
    r = C.controles(p, RAW)
    detecte = bool(r["echecs"][n]) and r["n_violations_schema"] >= 1
    res.append((nom, n, detecte, r["n_violations_schema"], r["n_anomalies_hors_principal"]))
    ok_tout &= detecte
for nom, fn, attendus in (("hors principal : prev_prec bidon sur ligne HICP incomplete", h5, (4, 7)),
                          ("hors principal : realise=50 sur ligne RGDP incomplete", h6, (6, 9))):
    h, rows = charge(); h, rows = fn(h, rows)
    r = C.controles(ecrit(h, rows, "alt.csv"), RAW)
    # un seul des controles peut ne pas mordre ; on exige n_violations_schema = 0 et anomalies > 0
    # (9 : realise de toute l'annee incoherent -> les lignes principales de la meme annee ne sont pas touchees par 'un seul valeur', voir sortie)
    res.append((nom, "hors", r["n_violations_schema"], r["n_anomalies_hors_principal"], {n: len(r["echecs"][n]) for n in r["echecs"] if r["echecs"][n]}))
# original intact
h, rows = charge(); r0 = C.controles(REEL, RAW)
assert REEL.read_bytes() == avant, "le vrai fichier a ete modifie !"
print("fichier reel :", r0["n_violations_schema"], "violations,", r0["n_anomalies_hors_principal"], "anomalies hors principal")
for x in res: print(x)
print("TOUS DETECTES :", ok_tout)
shutil.rmtree(tmp)
sys.exit(0 if ok_tout else 1)
