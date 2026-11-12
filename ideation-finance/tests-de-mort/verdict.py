"""Verdict d'un test de mort, calculé par l'orchestrateur. Aucun agent n'exécute ni n'écrit ce verdict.
Entrées : la préinscription scellée (bloc json final), verification.json (vérificateur), temoin.json (expérimentateur).
Usage : python3 verdict.py <dossier de la fiche>"""
import json, re, sys, hashlib, pathlib, operator

OPS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt}

def regle(texte):
    blocs = re.findall(r"```json\s*(\{.*?\})\s*```", texte, flags=re.S)
    assert blocs, "préinscription sans bloc json de règle"
    return json.loads(blocs[-1])

def tient(c, v):
    x = v[c["champ"]]
    assert isinstance(x, (int, float)) and x == x, f"champ {c['champ']} non numérique"
    return OPS[c["operateur"]](x, c["seuil"])

def main(d):
    d = pathlib.Path(d)
    pre = d / "preenregistrement.md"
    sceau = (d / "preenregistrement.md.sha256").read_text().split()[0]
    assert hashlib.sha256(pre.read_bytes()).hexdigest() == sceau, "préinscription modifiée après scellement"
    r = regle(pre.read_text())
    raisons = []
    try:
        v = json.loads((d / "verification.json").read_text())
        t = json.loads((d / "temoin.json").read_text())
        manquants = [c for c in r["champs_verification"] if c not in v]
        if manquants:
            raisons.append(f"champs absents de la vérification : {manquants}")
        else:
            for champ, tol in r.get("tolerance", {}).items():
                if champ not in t:
                    raisons.append(f"témoin de l'expérimentateur absent pour {champ}")
                elif abs(v[champ] - t[champ]) > tol:
                    raisons.append(f"écart expérimentateur/vérificateur sur {champ} : {t[champ]} contre {v[champ]} (tolérance {tol})")
            for c in r.get("non_concluant_si", []):
                if tient(c, v):
                    raisons.append(f"condition de non-conclusion tenue : {c}")
    except Exception as e:  # tout incident rend la fiche non concluante, jamais « survit »
        raisons.append(f"incident : {type(e).__name__}: {e}")
        v = {}
    if raisons:
        verdict = "non concluant"
    else:
        verdict = "survit" if all(tient(c, v) for c in r["survit_si"]) else "éliminée"
    sortie = {"id": r["id"], "verdict": verdict, "raisons": raisons, "sceau_preenregistrement": sceau,
              "chiffres_verificateur": {c: v.get(c) for c in r["champs_verification"]}, "regle": r,
              "etiquette": "verdict calculé par l'orchestrateur"}
    (d / "verdict.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1))
    print(r["id"], "->", verdict, raisons or "")

if __name__ == "__main__":
    main(sys.argv[1])
