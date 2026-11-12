"""Contrôle de forme des fiches de la génération 3 (règle scellée regle-generation-3.md), par l'orchestrateur, avant tout jugement.
Ne lit que le titre et le champ « Parent et différence » de chaque fiche."""
import re, json, pathlib, unicodedata
D = pathlib.Path(__file__).parent
ELEMENTS = {"statistique": r"statisti", "echantillon_ou_marche": r"[ée]chantillon|march[ée]|p[ée]riode|[ée]ch[ée]ance",
            "source": r"source|donn[ée]es", "identification": r"identifi"}
def champ(p):
    m = re.search(r"(?ms)^- \*\*Parent et diff[ée]rence[^*]*\*\*\s*:?\s*(.*?)(?=^- \*\*|\Z)", p)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
res, bilan = [], {}
for fam, pre in (("kimi", "4K"), ("gemini", "4G"), ("astra", "4A"), ("claude", "4C")):
    t = (D / "fiches" / f"proposeur-{fam}.md").read_text()
    parts = re.split(r"(?m)^(?=### " + pre + r"[1-5] — )", t)[1:]
    assert len(parts) == 5, (fam, len(parts))
    for p in parts:
        cid = re.match(r"### (\S+) — ", p).group(1); c = champ(p); cl = unicodedata.normalize("NFC", c.lower())
        if re.search(r"parent\s*a\b", cl[:60]): parent = "A"
        elif re.search(r"parent\s*b\b", cl[:60]): parent = "B"
        elif "question ouverte" in cl[:60]: parent = "Q"
        elif cl.startswith("libre") or "libre" in cl[:40]: parent = "libre"
        else: parent = "?"
        changes = [k for k, rx in ELEMENTS.items() if re.search(rx, cl)]
        ok = bool(c) and parent != "?" and (parent == "libre" or bool(changes))
        res.append({"id": cid, "famille": fam, "parent": parent, "elements_cites": changes, "accepte": ok, "champ": c[:400]})
    f = [r for r in res if r["famille"] == fam]
    bilan[fam] = {"filles": sum(r["parent"] in ("A", "B", "Q") for r in f), "libres": sum(r["parent"] == "libre" for r in f), "refusees": [r["id"] for r in f if not r["accepte"]]}
(D / "controle-forme.json").write_text(json.dumps({"bilan": bilan, "fiches": res}, ensure_ascii=False, indent=1))
for r in res: print(r["id"], r["parent"], r["accepte"], r["elements_cites"], "|", r["champ"][:150])
print(bilan)
