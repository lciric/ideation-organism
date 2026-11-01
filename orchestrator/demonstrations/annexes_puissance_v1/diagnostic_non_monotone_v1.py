"""Diagnostic hors banc : pourquoi la puissance du juge gelé baisse quand N grandit (forte force) ?"""
import sys, os, json, tempfile, collections, statistics, math
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # orchestrator/
sys.path.insert(0, os.path.join(RACINE, 'demonstrations'))
sys.path.insert(0, RACINE)
import puissance_juge_banque_v1 as pj
from pole import selection_pari as sp
from pole.cycle import preparer_engagement
from pole.monde_banque import MondeBanque
from pole.outils import graine_derivee
noms = ["log_jetons", "actions", "ecart_type"]
s = pj.structure_reelle()
Z = [ep["z"] for t in s["taches"] for ep in t]
def corr(a, b):
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    return sum((x-ma)*(y-mb) for x, y in zip(a, b)) / math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
print("corrélations des traits réels :", {f"{noms[i]}~{noms[j]}": round(corr([z[i] for z in Z], [z[j] for z in Z]), 2) for i in range(3) for j in range(i+1, 3)})
print("asymétrie (part des |z| > 1,5 du côté positif) :", {noms[i]: round(sum(1 for z in Z if z[i] > 1.5)/max(1, sum(1 for z in Z if abs(z[i]) > 1.5)), 2) for i in range(3)})
def diag(N, force_cible, reps, plan_taille):
    rows = []
    for r in range(reps):
        g = pj.graines_de(4242, N, r)
        banque, temoins, _ = pj.banque_de_repetition(s, N, pj.FORCES, g)
        t = next(t for t in temoins if t["force"] == force_cible)
        config = pj.config_du_juge(plan_taille)
        with tempfile.TemporaryDirectory() as tmp:
            ch = os.path.join(tmp, "b.json"); json.dump(banque, open(ch, "w"))
            monde = MondeBanque(ch, pj.GRAINE_DU_JUGE, nul_informe=True)
            fiche = t["fiches"]["tv"]
            gn = graine_derivee(config.graine, "noyau", 0)
            sup = list(monde.membres_informes(fiche))
            gele = preparer_engagement(fiche, config, None, reservoir=monde.reservoir(fiche, 0), membres_supplementaires=sup, moniteur=monde.moniteur_de(fiche))
            mes = monde.mesures(fiche.enonce, gele, gn, 0)
            ev = sp.evaluer(gele, mes, graine_noyau=gn)
        plan = gele.engagement["instances"]
        pred = [max(range(3), key=lambda c: sp.proba(fiche.loi_predictive, x, [], 0)[c]) for x in plan]
        part_majo = collections.Counter(pred).most_common(1)[0][1] / len(pred)
        distincts = len({json.dumps(x["z"]) for x in plan})
        rows.append({"lw": ev["log_richesse_max"], "dom": ev["membre_dominant_final"], "ij": f"{noms[t['i']]}|{noms[t['j']]}", "homog": part_majo, "distincts": distincts})
    return rows
for N, plan_taille in ((120, 120), (600, 120), (600, 600)):
    rows = diag(N, 0.8, 60, plan_taille)
    bas = [x for x in rows if x["lw"] < 5.83]; haut = [x for x in rows if x["lw"] >= 5.83]
    def resume(xs):
        if not xs: return "—"
        return (f"n={len(xs)}, homogénéité médiane du plan (part de la classe prédite majoritaire) {statistics.median(x['homog'] for x in xs):.2f}, "
                f"épisodes distincts médians {statistics.median(x['distincts'] for x in xs)}, membres dominants {dict(collections.Counter(x['dom'].split(':')[0] for x in xs))}, "
                f"paires {dict(collections.Counter(x['ij'] for x in xs))}")
    print(f"\nN = {N}, plan = {plan_taille}, force 0,8 : log W max < 5,83 → {resume(bas)}\n   log W max ≥ 5,83 → {resume(haut)}")
