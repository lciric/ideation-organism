"""Couche 1 en simulation d'agents (v7, sans dépense) : le pôle sur la **banque réelle** du pilote de T0.5 (épisodes du
modèle de 8 milliards, notes des deux juges), avec des agents simulés — ils ne font que ranger les issues déposées par le
noyau, exactement ce que feraient de vrais agents sur une banque : le contenu scientifique (quelles fiches sont promues)
est donc le vrai, seul le coût des agents manque. Proposeur scripté (`exemples/proposeur_scripte_banque_v1.py`).

Bras (lus dans les deux sens, exploratoire, R-546) :
- « informe » : bibliothèque aveugle + prédicteur connu (ajusté par le noyau sur la partie de calibrage), sans urne ;
- « aveugle » : bibliothèque aveugle seule, sans urne (le juge d'aujourd'hui, sans la perte de l'urne) ;
- « urne » : bibliothèque aveugle avec urne (le juge v1 tel quel).

Lecture fixée avant l'exécution :
- L1 : aucun témoin faux (loi sur le trait de bruit) promu, dans aucun bras ;
- L2 : les fiches promues sous « informe » sont un sous-ensemble de celles promues sous « aveugle » (le nul informé ne
  peut que retirer) ; la différence est « ce qui n'est que du connu » ;
- L3 : les témoins vrais (lien de rang ≥ 0,35 en calibrage) : promus sous « aveugle » au moins pour moitié, sinon la
  banque est trop petite pour la puissance du juge (lecture : pas de dents, pas de conclusion) ;
- L4 : « urne » promeut au plus autant que « aveugle » (prix de l'urne mesuré sur données réelles).
Aucune fiche n'a été lue avant l'exécution ; les corrélations de rang servent seulement à déclarer les témoins vrais.

v3 de la démonstration (27 octobre, 15:25 UTC, v7 version 5) : bras « fraction » = « aveugle » avec le pari à fraction
(numérateur = mélange sur la grille de fractions de mise ; essais `essais/test_v7_pari_fraction.py`). Lecture fixée
avant l'exécution :
- F1 : aucun témoin faux promu sous « fraction » ;
- F2 : témoins vrais promus sous « fraction » contre « aveugle » (le levier de puissance sur la banque réelle ; s'il ne
  change rien, la banque reste trop petite et le levier n'y suffit pas) ;
- F3 : fiches de la population promues sous « fraction » qui ne le sont pas sous « aveugle », listées (à lire, pas à
  croire : une seule course).

Usage : python -I -B demonstrations/demo_couche1_v7.py DOSSIER_NEUF [--generations 3] [--bras informe,aveugle,urne]
"""

import argparse
import json
import os
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole.cycle import ConfigGeneration  # noqa: E402
from pole.fiche import charger_fiches  # noqa: E402
from pole.monde_banque import MondeBanque  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier  # noqa: E402
from pole.pole import executer_pole  # noqa: E402
from pole.simulation import AdaptateurSimule, MondeSimule  # noqa: E402

EXEMPLES = os.path.join(RACINE, "exemples")
BANQUE = os.path.join(EXEMPLES, "banque-t05-v2.json")
POPULATION = os.path.join(EXEMPLES, "population-banque-t05-v2.json")
TEMOINS = os.path.join(EXEMPLES, "temoins-banque-t05-v2.json")
# v2 de la démonstration (décisions de Lazar du 27 octobre, 15:11) : banque v2 (trait redondant retiré), règle de
# multiplicité e-BH par défaut, témoins jugés sans agents et tous servis dès la génération 0, signal « pas de dents ».
# Le bras « par-fiche » garde la garantie par fiche seule, pour mesurer ce que la multiplicité retire.
BRAS = {"informe": {"nul_informe": True, "urne": False, "multiplicite": "e-bh"},
        "aveugle": {"nul_informe": False, "urne": False, "multiplicite": "e-bh"},
        "urne": {"nul_informe": False, "urne": True, "multiplicite": "e-bh"},
        "par-fiche": {"nul_informe": False, "urne": False, "multiplicite": "aucune"},
        "fraction": {"nul_informe": False, "urne": False, "multiplicite": "e-bh", "pari_fraction": True}}


def executer_bras(nom, dossier, generations, graine=20261027):
    reglages = BRAS[nom]
    population, temoins = charger_fiches(POPULATION), charger_fiches(TEMOINS)
    monde = MondeBanque(BANQUE, graine, nul_informe=reglages["nul_informe"])
    adaptateur = AdaptateurSimule(graine, MondeSimule(graine))  # son monde propre est sans objet : issues déposées
    config = ConfigGeneration(selection="pari", juge="v1", nul_filles="v2", urne=reglages["urne"], graine=graine,
                              taille_plan=120, taille_plan_filles=120, instants_filles=6, part_calibrage=12,
                              budget_generation_usd=200.0, concurrence=4, multiplicite=reglages["multiplicite"],
                              temoins_sans_agent=True, pari_fraction=reglages.get("pari_fraction", False),
                              politique_redite="refus").valider()  # v11 : banque trop petite pour des tranches : héritage coupé
    bilan = executer_pole(population, temoins, adaptateur, config, generations, 600.0, dossier, memoire_active=True,
                          horodatage_fourni="demo couche 1 v7 (v2)",
                          temoins_par_generation=min(sum(t.temoin == "vraie" for t in temoins), sum(t.temoin == "fausse" for t in temoins)),
                          k_recombinaison=4, max_paires=4, monde_noyau=monde)
    with open(os.path.join(dossier, "archive", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    promues, journal_promotions = [], {}
    for g in range(bilan["generations_executees"]):
        with open(os.path.join(dossier, "journal", f"generation-{g:02d}.json"), encoding="utf-8") as f:
            journal = json.load(f)
        for ident, issue in journal["fiches"].items():
            if issue.get("verdict_final") == "survit" and issue.get("pari"):
                journal_promotions[ident] = {"generation": g, "log_richesse_max": round(issue["pari"]["log_richesse_max"], 3),
                                             "membre_dominant": issue["pari"].get("membre_dominant_final"),
                                             "tirages": issue["pari"].get("nombre_tirages")}
    sans_dents = {}
    for g in range(bilan["generations_executees"]):
        with open(os.path.join(dossier, "journal", f"generation-{g:02d}.json"), encoding="utf-8") as f:
            sans_dents[g] = json.load(f)["qualite_generation"].get("sans_dents")
    for ident, e in index.items():
        if e["statut"] == "survit":
            promues.append({"identifiant": ident, "source": e["source"], "temoin": e["temoin"], "enonce": e["enonce"],
                            **journal_promotions.get(ident, {})})
    temoins_detail = {i: e for i, e in index.items() if e["temoin"]}
    return {"bras": nom, "reglages": reglages, "generations": bilan["generations_executees"], "arret": bilan["arret"],
            "comptes": bilan["comptes_par_statut"], "qualite": bilan["qualite_cumulee"],
            "promues": sorted(promues, key=lambda p: -(p.get("log_richesse_max") or 0)),
            "temoins": {i: {"verite": e["temoin"], "statut": e["statut"], "enonce": e["enonce"]} for i, e in temoins_detail.items()},
            "refusees_redite": [i for i, e in index.items() if e["statut"] == "refusee (redite)"],
            "sans_dents_par_generation": sans_dents, "depense_simulee": bilan["depense_totale"]}


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("dossier")
    a.add_argument("--generations", type=int, default=3)
    a.add_argument("--bras", default="informe,aveugle,urne,par-fiche")
    args = a.parse_args(argv)
    if os.path.exists(args.dossier) and os.listdir(args.dossier):
        raise FileExistsError(args.dossier)
    os.makedirs(args.dossier, exist_ok=True)
    debut = time.time()
    resultats = {}
    for nom in args.bras.split(","):
        resultats[nom] = executer_bras(nom, os.path.join(args.dossier, "courses", nom), args.generations)
    promues = {nom: {p["identifiant"] for p in r["promues"] if not p["temoin"]} for nom, r in resultats.items()}
    lecture = {}
    lecture["L1_aucun_temoin_faux_promu"] = all(
        t["statut"] != "survit" for r in resultats.values() for t in r["temoins"].values() if t["verite"] == "fausse")
    if "informe" in promues and "aveugle" in promues:
        lecture["L2_informe_sous_ensemble_de_aveugle"] = promues["informe"] <= promues["aveugle"]
        lecture["L2_que_du_connu"] = sorted(promues["aveugle"] - promues["informe"])
    if "aveugle" in resultats:
        vrais = [t for t in resultats["aveugle"]["temoins"].values() if t["verite"] == "vraie"]
        lecture["L3_temoins_vrais_promus_aveugle"] = [sum(t["statut"] == "survit" for t in vrais), len(vrais)]
    if "urne" in promues and "aveugle" in promues:
        lecture["L4_urne_au_plus_autant"] = len(promues["urne"]) <= len(promues["aveugle"])
        lecture["L4_promues"] = {"urne": len(promues["urne"]), "aveugle": len(promues["aveugle"]),
                                 "informe": len(promues.get("informe", set()))}
    if "fraction" in resultats and "aveugle" in resultats:
        lecture["F1_aucun_temoin_faux_promu_fraction"] = all(
            t["statut"] != "survit" for t in resultats["fraction"]["temoins"].values() if t["verite"] == "fausse")
        vrais_f = [t for t in resultats["fraction"]["temoins"].values() if t["verite"] == "vraie"]
        lecture["F2_temoins_vrais_promus"] = {"fraction": [sum(t["statut"] == "survit" for t in vrais_f), len(vrais_f)],
                                              "aveugle": lecture.get("L3_temoins_vrais_promus_aveugle")}
        lecture["F3_promues_fraction_seulement"] = sorted(promues["fraction"] - promues["aveugle"])
    rapport = {"banque": sha256_fichier(BANQUE), "population": sha256_fichier(POPULATION), "temoins": sha256_fichier(TEMOINS),
               "generations": args.generations, "duree_s": round(time.time() - debut, 1), "lecture": lecture,
               "resultats": resultats}
    ecrire_json_scelle(os.path.join(args.dossier, "demo-couche1-v7-v3.json"), rapport)
    print(json.dumps({"lecture": lecture, "duree_s": rapport["duree_s"],
                      "promues_par_bras": {n: sorted(p) for n, p in promues.items()}}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
