"""Agrégation de la génération 2 selon grille-generation-2.md. Aucun juge n'exécute ce code.
Usage : python3 agreger_course_2.py <dossier jugements> <clé d'anonymat json> <sortie json>"""
import json, sys, itertools, pathlib, statistics

JUGES = ("kimi", "gemini", "astra", "claude")
AXES = ("jury", "recruteurs", "tuable", "interet", "nouveaute", "apport")

def charger(d, n):
    J = {}
    for j in JUGES:
        L = json.loads((d / f"juge-{j}.json").read_text())
        assert len(L) == n and len({x["id"] for x in L}) == n, f"juge {j} : {n} fiches distinctes attendues"
        assert sorted(x["rang"] for x in L) == list(range(1, n + 1)), f"juge {j} : classement incomplet"
        m = [x["mention"] for x in L]
        assert m.count("à retenir") <= 5 and m.count("à écarter") >= 8, f"juge {j} : quotas de mentions non tenus"
        assert all(str(x.get("faille", "")).strip() for x in L), f"juge {j} : faille manquante"
        assert all(isinstance(x[a], int) and 1 <= x[a] <= 5 for x in L for a in AXES), f"juge {j} : note hors de 1..5"
        J[j] = {x["id"]: x for x in L}
    return J

def spearman(a, b):
    ids = sorted(a); n = len(ids)
    return 1 - 6 * sum((a[i]["rang"] - b[i]["rang"]) ** 2 for i in ids) / (n * (n * n - 1))

def main(d, f_cle, sortie):
    cle = json.loads(pathlib.Path(f_cle).read_text())  # {"H01": {"origine": "2K3" | "F04", "famille": "kimi"|"gemini"|"claude"|"course-1"}}
    n = len(cle); J = charger(d, n)
    lignes = []
    for i in sorted(cle):
        rangs = {j: J[j][i]["rang"] for j in JUGES}
        lignes.append({"id": i, **cle[i], "borda": sum(rangs.values()), "rangs": rangs,
                       "jury_recruteurs": sum(J[j][i]["jury"] + J[j][i]["recruteurs"] for j in JUGES),
                       "ecarter": sum(J[j][i]["mention"] == "à écarter" for j in JUGES),
                       "retenir": sum(J[j][i]["mention"] == "à retenir" for j in JUGES),
                       "notes": {a: [J[j][i][a] for j in JUGES] for a in AXES},
                       "failles": {j: J[j][i]["faille"] for j in JUGES}})
    lignes.sort(key=lambda x: (x["borda"], -x["jury_recruteurs"], x["id"]))
    for r, x in enumerate(lignes, 1): x["rang_agrege"] = r
    familles = sorted({x["famille"] for x in lignes})
    rang_moyen = {f: round(statistics.mean(x["rang_agrege"] for x in lignes if x["famille"] == f), 2) for f in familles}
    par_juge = {j: {f: round(statistics.mean(x["rangs"][j] for x in lignes if x["famille"] == f), 2) for f in familles} for j in JUGES}
    propre = {j: {"sa_famille": par_juge[j].get(j),
                  "autres_proposeurs": round(statistics.mean(x["rangs"][j] for x in lignes if x["famille"] in JUGES and x["famille"] != j), 2)} for j in JUGES}
    res = {"accord_spearman": {f"{a}-{b}": round(spearman(J[a], J[b]), 3) for a, b in itertools.combinations(JUGES, 2)},
           "rang_agrege_moyen_par_famille": rang_moyen, "rang_moyen_par_juge_et_famille": par_juge, "propre_famille": propre,
           "retenues": [x["id"] for x in lignes if x["ecarter"] < 2][:5], "classement": lignes}
    json.dump(res, open(sortie, "w"), ensure_ascii=False, indent=1)
    print("accord :", res["accord_spearman"]); print("rang agrégé moyen par famille :", rang_moyen); print("propre famille :", propre)
    for x in lignes:
        print(f'{x["rang_agrege"]:>2} {x["id"]} {x["origine"]:>4} {x["famille"]:<9} borda={x["borda"]:>2} rangs={list(x["rangs"].values())} retenir={x["retenir"]} ecarter={x["ecarter"]}')

if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3])
