"""Couche 1, v7 avec proposeur (pièce 4) et phase exploratoire (pièce 4 bis) — simulation d'agents, sans dépense.

Sur le « go » de Lazar du 27 octobre (15:38 heure de Paris : « lance v7 immédiatement après lecture comparaison
d'échelle »). Deux mondes, mêmes réglages du juge (v1 sans urne, nul informé, nul d'archive, règle e-BH, témoins jugés sans
agents, signal « pas de dents ») :
- **réel** : la banque T0.5 v2 (120 épisodes du modèle de 8 milliards, 13 moniteurs) ;
- **planté** : une banque synthétique de même taille où l'effet d'un trait change de signe selon la sous-population
  (structure que le prédicteur connu, linéaire, ne contient pas) — la vérité est connue : c'est le témoin de la méthode.
Trois bras par monde : proposeur aveugle (12 fiches par génération) ; proposeur avec exploration du développement (12) ;
proposeur scripté seul (génération 0 du fichier, aucun proposeur) — le bras de référence.

Lecture fixée avant l'exécution :
- E1 : aucun témoin faux promu, dans aucun bras ni aucun monde ;
- E2 : monde planté : l'exploration promeut au moins une fiche par sous-population ; l'aveugle en promeut moins, ou
  aucune (sinon l'exploration n'apporte rien ici) ;
- E3 : monde réel : on rapporte promues, « pas de dents » et exposition ; aucune conclusion de fond si « pas de dents » ;
- E4 : par stratégie : proposées, acceptées, promues (on lit quelles stratégies produisent des promues).

Usage : python -I -B demonstrations/demo_couche1_proposeur_v7.py DOSSIER_NEUF [--generations 4]
"""

import argparse
import json
import math
import os
import random
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole.cycle import ConfigGeneration  # noqa: E402
from pole.fiche import Fiche, charger_fiches  # noqa: E402
from pole.monde_banque import MondeBanque  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier  # noqa: E402
from pole.pole import executer_pole  # noqa: E402
from pole.simulation import AdaptateurSimule, MondeSimule  # noqa: E402

EXEMPLES = os.path.join(RACINE, "exemples")
BRAS = {"aveugle": {"propositions": 12, "exploration": False},
        "exploration": {"propositions": 12, "exploration": True},
        "reference": {"propositions": 0, "exploration": False}}


def banque_plantee(chemin, n=180, graine=29):
    rng = random.Random(graine)
    instances = []
    for i in range(n):
        z = [round(rng.gauss(0, 1), 6) for _ in range(3)]
        g = i % 2
        s = 2.0 * z[0] * (1 if g == 0 else -1)
        issue = 1 if rng.random() < 1 / (1 + math.exp(-s)) else 0
        instances.append({"identifiant": f"p{i:03d}", "tache": f"t{i // 3:03d}", "z": z, "g": g, "issues": {"M": issue},
                          "partie": "calibrage" if (i // 3) % 3 == 0 else "epreuve"})
    ecrire_json_scelle(chemin, {"nom": "plantee-signe-v1", "traits": ["e0", "e1", "bruit"], "sous_populations": 2,
                                "moniteurs": {"M": {"nombre_issues": 2, "coupes": [0], "instances": n}},
                                "instances": instances})


def fiches_plantees():
    def f(ident, enonce, j, sens, temoin=None):
        poids = [[0.0] * 3, [0.0] * 3]
        poids[1][j] = 1.2 * sens
        d = {"identifiant": ident, "enonce": enonce, "prediction": {"signe": "+", "valeur": 0.1, "texte": "pari"},
             "metrique": "richesse W", "nul": "aveugle et connu", "seuil": 20.0, "severite_attendue": 0.05, "cout_borne": 1.0,
             "protocole": "pari sur la banque", "domaines": ["plantee"], "operateurs": [f"monotone:{j}"], "contraintes": [],
             "loi_predictive": {"type": "softmax", "poids": poids, "biais": [0.0, 0.0]},
             "espace_instances": {"dimension": 3, "nombre_issues": 2, "sous_populations": 2, "moniteur": "M"}}
        if temoin:
            d["temoin"] = temoin
        return Fiche.depuis_dict(d).valider()
    population = [f("Q1", "L'issue croît avec e0", 0, 1), f("Q2", "L'issue croît avec e1", 1, 1)]
    temoins = [f("TF1", "Témoin faux : bruit", 2, 1, "fausse"), f("TF2", "Témoin faux : bruit inverse", 2, -1, "fausse"),
               Fiche.depuis_dict(dict(f("TV1", "x", 0, 1).vers_dict(), identifiant="TV1", temoin="vraie",
                                      enonce="Témoin vrai : e0 positif en sous-population 0",
                                      loi_predictive={"type": "par_sous_population", "lois": {
                                          "0": {"type": "softmax", "poids": [[0, 0, 0], [1.6, 0, 0]], "biais": [0, 0]},
                                          "1": {"type": "softmax", "poids": [[0, 0, 0], [-1.6, 0, 0]], "biais": [0, 0]}}})).valider(),
               Fiche.depuis_dict(dict(f("TV2", "x", 0, 1).vers_dict(), identifiant="TV2", temoin="vraie",
                                      enonce="Témoin vrai bis : signe de e0 selon la sous-population",
                                      loi_predictive={"type": "par_sous_population", "lois": {
                                          "0": {"type": "softmax", "poids": [[0, 0, 0], [1.0, 0, 0]], "biais": [0, 0]},
                                          "1": {"type": "softmax", "poids": [[0, 0, 0], [-1.0, 0, 0]], "biais": [0, 0]}}})).valider()]
    return population, temoins


def executer_bras(monde_nom, banque, population, temoins, nom, dossier, generations, graine=20261027):
    r = BRAS[nom]
    monde = MondeBanque(banque, graine, nul_informe=True)
    adaptateur = AdaptateurSimule(graine, MondeSimule(graine))
    config = ConfigGeneration(selection="pari", juge="v1", nul_filles="v2", urne=False, graine=graine, taille_plan=120,
                              taille_plan_filles=120, instants_filles=6, part_calibrage=12, budget_generation_usd=200.0,
                              concurrence=4, multiplicite="e-bh", temoins_sans_agent=True, nul_archive=True,
                              propositions_par_generation=r["propositions"], exploration_developpement=r["exploration"],
                              # v11 (contre-lecture du socle, C1) : la banque T0.5 est trop petite pour une tranche par
                              # génération ; sans tranches fraîches, l'héritage de la preuve est coupé (redite refusée).
                              politique_redite="refus").valider()
    n_temoins = min(sum(t.temoin == "vraie" for t in temoins), sum(t.temoin == "fausse" for t in temoins))
    bilan = executer_pole(population, temoins, adaptateur, config, generations, 2000.0, dossier, memoire_active=True,
                          horodatage_fourni="demo couche 1 proposeur v7", temoins_par_generation=n_temoins,
                          k_recombinaison=4, max_paires=4, monde_noyau=monde)
    with open(os.path.join(dossier, "archive", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    par_strategie, sans_dents, exposition = {}, {}, None
    for g in range(bilan["generations_executees"]):
        with open(os.path.join(dossier, "journal", f"generation-{g:02d}.json"), encoding="utf-8") as f:
            j = json.load(f)
        sans_dents[g] = j["qualite_generation"].get("sans_dents")
        if j.get("proposeur"):
            exposition = j["proposeur"].get("exposition")
    for e in index.values():
        src = e.get("source") or ""
        strat = src.split(":")[1] if src.startswith("proposeur:") else ("temoin" if e["temoin"] else src.split(":")[0])
        c = par_strategie.setdefault(strat, {"fiches": 0, "promues": 0, "refusees_redite": 0})
        c["fiches"] += 1
        c["promues"] += e["statut"] == "survit"
        c["refusees_redite"] += e["statut"] == "refusee (redite)"
    promues = [{"identifiant": i, "source": e["source"], "enonce": e["enonce"][:120]} for i, e in index.items()
               if e["statut"] == "survit" and not e["temoin"]]
    return {"monde": monde_nom, "bras": nom, "generations": bilan["generations_executees"], "arret": bilan["arret"],
            "qualite": bilan["qualite_cumulee"], "comptes": bilan["comptes_par_statut"], "promues": promues,
            "par_strategie": par_strategie, "sans_dents_par_generation": sans_dents, "exposition": exposition,
            "temoins": {i: (e["temoin"], e["statut"]) for i, e in index.items() if e["temoin"]}}


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("dossier")
    a.add_argument("--generations", type=int, default=4)
    args = a.parse_args(argv)
    if os.path.exists(args.dossier) and os.listdir(args.dossier):
        raise FileExistsError(args.dossier)
    os.makedirs(args.dossier, exist_ok=True)
    debut = time.time()
    plantee = os.path.join(args.dossier, "banque-plantee-v1.json")
    banque_plantee(plantee)
    mondes = {"reel": (os.path.join(EXEMPLES, "banque-t05-v2.json"),
                       charger_fiches(os.path.join(EXEMPLES, "population-banque-t05-v2.json")),
                       charger_fiches(os.path.join(EXEMPLES, "temoins-banque-t05-v2.json"))),
              "plante": (plantee,) + fiches_plantees()}
    resultats = {}
    for monde_nom, (banque, population, temoins) in mondes.items():
        for nom in BRAS:
            resultats[f"{monde_nom}-{nom}"] = executer_bras(monde_nom, banque, population, temoins, nom,
                                                            os.path.join(args.dossier, "courses", f"{monde_nom}-{nom}"),
                                                            args.generations)
    faux_promus = sum(1 for r in resultats.values() for v, s in r["temoins"].values() if v == "fausse" and s == "survit")
    def promues_par(cle, strat=None):
        return [p for p in resultats[cle]["promues"] if strat is None or (p["source"] or "").startswith(f"proposeur:{strat}")]
    lecture = {"E1_aucun_temoin_faux_promu": faux_promus == 0,
               "E2_plante_exploration_promues": len(promues_par("plante-exploration", "ajustee_sur_developpement")),
               "E2_plante_aveugle_promues": len(promues_par("plante-aveugle")),
               "E3_reel": {b: {"promues": len(resultats[f"reel-{b}"]["promues"]),
                               "sans_dents": resultats[f"reel-{b}"]["sans_dents_par_generation"]} for b in BRAS}}
    lecture["E2_tenu"] = lecture["E2_plante_exploration_promues"] >= 1 and \
        lecture["E2_plante_aveugle_promues"] < lecture["E2_plante_exploration_promues"]
    rapport = {"duree_s": round(time.time() - debut, 1), "lecture": lecture, "resultats": resultats,
               "banque_reelle": sha256_fichier(mondes["reel"][0]), "banque_plantee": sha256_fichier(plantee)}
    ecrire_json_scelle(os.path.join(args.dossier, "demo-couche1-proposeur-v7.json"), rapport)
    print(json.dumps({"lecture": lecture, "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
