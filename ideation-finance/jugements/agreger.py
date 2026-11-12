"""Agrégation des trois juges selon la règle scellée dans grille.md. Aucun juge n'exécute ce code.
Usage : python3 agreger.py <dossier jugements> <sortie json>"""
import json, sys, itertools, pathlib

def charger(d):
    juges = {}
    for n in (1, 2, 3):
        L = json.loads((d / f"juge-{n}.json").read_text())
        ids = sorted(x["id"] for x in L)
        assert len(L) == 20 and len(set(ids)) == 20, f"juge {n} : 20 fiches distinctes attendues"
        assert sorted(x["rang"] for x in L) == list(range(1, 21)), f"juge {n} : classement incomplet"
        m = [x["mention"] for x in L]
        assert m.count("à retenir") <= 4 and m.count("à écarter") >= 8, f"juge {n} : quotas de mentions non tenus"
        assert all(x.get("faille", "").strip() for x in L), f"juge {n} : faille manquante"
        juges[n] = {x["id"]: x for x in L}
    return juges

def spearman(a, b):
    ids = sorted(a); n = len(ids)
    return 1 - 6 * sum((a[i]["rang"] - b[i]["rang"]) ** 2 for i in ids) / (n * (n * n - 1))

def main(d, sortie):
    J = charger(d); ids = sorted(J[1])
    lignes = []
    for i in ids:
        rangs = [J[n][i]["rang"] for n in (1, 2, 3)]
        lignes.append({
            "id": i, "borda": sum(rangs), "rangs": rangs,
            "jury_recruteurs": sum(J[n][i]["jury"] + J[n][i]["recruteurs"] for n in (1, 2, 3)),
            "ecarter": sum(J[n][i]["mention"] == "à écarter" for n in (1, 2, 3)),
            "retenir": sum(J[n][i]["mention"] == "à retenir" for n in (1, 2, 3)),
            "notes": {k: [J[n][i][k] for n in (1, 2, 3)] for k in ("jury", "recruteurs", "tuable", "ia", "nouveaute")},
            "failles": [J[n][i]["faille"] for n in (1, 2, 3)],
        })
    lignes.sort(key=lambda x: (x["borda"], -x["jury_recruteurs"], x["id"]))
    for r, x in enumerate(lignes, 1):
        x["rang_agrege"] = r
    vers_nouveaute = [x["id"] for x in lignes if x["ecarter"] < 2][:6]
    accord = {f"{a}-{b}": round(spearman(J[a], J[b]), 3) for a, b in itertools.combinations((1, 2, 3), 2)}
    json.dump({"regle": "Borda, départage jury+recruteurs puis identifiant ; écartée par >= 2 juges : retirée",
               "accord_spearman": accord, "vers_nouveaute": vers_nouveaute, "classement": lignes},
              open(sortie, "w"), ensure_ascii=False, indent=1)
    print("accord (Spearman) :", accord)
    for x in lignes:
        print(f'{x["rang_agrege"]:>2} {x["id"]} borda={x["borda"]:>2} rangs={x["rangs"]} retenir={x["retenir"]} ecarter={x["ecarter"]}')
    print("vers la nouveauté :", vers_nouveaute)

if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]), sys.argv[2])
