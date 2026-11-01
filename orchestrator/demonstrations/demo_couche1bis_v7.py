"""Couche 1 bis, lecture P3 (ii) (v7, version 16) : le pôle en simulation d'agents (zéro dépense) sur la **banque v3**
(`exemples/construire_banque_t05_v3.py`) et ses témoins — vrais établis par confirmation croisée, faux par permutation
dans la tâche et par bruit — avec le proposeur mécanique sur la partie de développement, une tranche d'épreuve par
génération, la règle e-BH, le nul informé et le nul d'archive ajusté.

Ce qu'on lit (fixé ici, avant la course) :
- **L1** validité : aucun témoin faux promu (permutation, bruit) ; promues sans lien rapportées ;
- **L2** dents : au moins un témoin vrai établi promu (« dents »), sinon « pas de dents » (les témoins vrais sont lus au seuil
  m/α hors famille, v11) ; « dents non mesurées » si la banque n'a établi aucun témoin vrai ;
- **L3** ce que le pôle trouve : fiches réelles promues, par moniteur, avec leur forme et leurs traits ; lien à un témoin
  vrai établi (mêmes traits, même moniteur) ou nouveauté.

Usage : python -I -B demonstrations/demo_couche1bis_v7.py BANQUE.json TEMOINS.json DOSSIER_NEUF [--generations 3]
        [--propositions 12] [--graine 20261027] [--sans-exploration]
"""

import argparse
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole.cycle import ConfigGeneration  # noqa: E402
from pole.fiche import charger_fiches  # noqa: E402
from pole.monde_banque import MondeBanque  # noqa: E402
from pole.outils import ecrire_json_scelle, graine_derivee  # noqa: E402
from pole.pole import executer_pole  # noqa: E402
from pole.proposeur import valider_proposition  # noqa: E402
from pole.proposeurs_references import propositions_aleatoires  # noqa: E402
from pole.simulation import AdaptateurSimule, MondeSimule  # noqa: E402


def traits_de(loi):
    if not isinstance(loi, dict):
        return set()
    if loi.get("type") == "softmax":
        return {j for ligne in loi["poids"] for j, w in enumerate(ligne) if abs(w) > 1e-9}
    sortie = set()
    for cle in ("si", "sinon", "loi", "base", "defaut"):
        sortie |= traits_de(loi.get(cle))
    for cle in ("lois", "composantes"):
        sous = loi.get(cle)
        if isinstance(sous, dict):
            for s in sous.values():
                sortie |= traits_de(s)
        elif isinstance(sous, list):
            for s in sous:
                sortie |= traits_de(s)
    if loi.get("type") == "si_sinon" and isinstance(loi.get("condition"), dict) and "trait" in loi["condition"]:
        sortie.add(int(loi["condition"]["trait"]))
    return sortie


def executer(chemin_banque, chemin_temoins, dossier, generations=3, propositions=12, graine=20261027, exploration=True,
             nul_informe=True, population_initiale="aleatoire", temoins_par_generation=3):
    monde = MondeBanque(chemin_banque, graine, nul_informe=nul_informe, tranches=generations)
    description = monde.description_publique()
    temoins = charger_fiches(chemin_temoins)
    if population_initiale == "mecanique":
        # v17 : population initiale = les meilleures lois du chercheur mécanique sur le développement, **sans** le filtre de
        # la pénalité de Schwarz (à 48 instances de développement, rien ne le passe) ; le juge décide sur l'épreuve
        import math
        from pole.proposeurs_references import propositions_mecaniques
        props = propositions_mecaniques(description, monde.donnees_developpement(), propositions, score_minimum=-math.inf)
        population = [valider_proposition(p, monde, 0.05, f"P{i:02d}", "reference-mecanique", references=True)
                      for i, p in enumerate(props, 1)]
    else:
        population = [valider_proposition(p, monde, 0.05, f"P{i:02d}", "reference-aleatoire", references=True)
                      for i, p in enumerate(propositions_aleatoires(description, 6, graine_derivee(graine, "population"), 0), 1)]
    n_epreuve = sum(1 for l in monde.banque["instances"] if l.get("partie") == "epreuve")
    taille_plan = max(20, min(120, n_epreuve // generations))
    if not any(t.temoin == "vraie" for t in temoins):
        # la banque n'a établi aucun témoin vrai (constat C8 du socle) : la course ne mesure pas les dents ; on le dit,
        # on ne lance rien (le pôle exige au moins un témoin de chaque sorte)
        lecture = {"generations": 0, "arret": "aucun témoin vrai établi par la banque : course non lancée",
                   "instances_epreuve": n_epreuve, "temoins": {"vrais": 0, "faux": sum(t.temoin == "fausse" for t in temoins)},
                   "L1_temoins_faux_promus": [], "L2_etat_dents": "dents non mesurées", "L2_vrais_promus": [],
                   "L3_promues": [], "L3_nombre_promues": 0, "L3_promues_liees_a_un_temoin_vrai": 0}
        os.makedirs(dossier, exist_ok=True)
        ecrire_json_scelle(os.path.join(dossier, "lecture-couche1bis.json"), lecture)
        return lecture
    config = ConfigGeneration(selection="pari", juge="v1", nul_filles="v2", urne=False, graine=graine, taille_plan=taille_plan,
                              taille_plan_filles=taille_plan, instants_filles=6, part_calibrage=12, budget_generation_usd=500.0,
                              multiplicite="e-bh", temoins_sans_agent=True, nul_archive=True, nul_archive_ajuste=True,
                              propositions_par_generation=propositions, exploration_developpement=exploration,
                              proposeur="mecanique").valider()
    nb_temoins = max(1, min(sum(t.temoin == "vraie" for t in temoins) or 1, sum(t.temoin == "fausse" for t in temoins) or 1))
    bilan = executer_pole(population, temoins, AdaptateurSimule(graine, MondeSimule(graine)), config, generations, 5000.0,
                          dossier, memoire_active=True, horodatage_fourni="couche 1 bis, banque v3",
                          temoins_par_generation=max(1, min(temoins_par_generation, nb_temoins)), k_recombinaison=4, max_paires=2,
                          monde_noyau=monde)
    with open(os.path.join(dossier, "archive", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    vrais_etablis = {t.identifiant: (t.espace_instances["moniteur"], traits_de(t.loi_predictive)) for t in temoins if t.temoin == "vraie"}
    promues, temoins_statut = [], {}
    for ident in sorted(index, key=lambda i: (int(i.split("-")[0][1:]), i)):
        e = index[ident]
        if e["temoin"]:
            temoins_statut.setdefault(e["source"].split(":", 1)[1], e["statut"])
            continue
        if e["statut"] != "survit":
            continue
        with open(os.path.join(dossier, "archive", "fiches", ident, "etat-final.json"), encoding="utf-8") as f:
            etat = json.load(f)
        moniteur = (etat.get("espace_instances") or {}).get("moniteur")
        traits = traits_de(etat["loi_predictive"])
        lien = sorted(k for k, (m, tr) in vrais_etablis.items() if m == moniteur and tr and tr <= traits)
        promues.append({"identifiant": ident, "moniteur": moniteur, "traits": sorted(traits), "source": e["source"],
                        "lien_temoin_vrai": lien, "forme": (etat["loi_predictive"] or {}).get("type")})
    vrais = [t for t in temoins if t.temoin == "vraie"]
    faux = [t for t in temoins if t.temoin == "fausse"]
    faux_promus = [t.identifiant for t in faux if temoins_statut.get(t.identifiant) == "survit"]
    vrais_promus = [t.identifiant for t in vrais if temoins_statut.get(t.identifiant) == "survit"]
    dents = "dents non mesurées" if not vrais else ("dents" if vrais_promus else "pas de dents")
    lecture = {"generations": bilan["generations_executees"], "arret": bilan["arret"], "taille_plan": taille_plan,
               "instances_epreuve": n_epreuve, "temoins": {"vrais": len(vrais), "faux": len(faux), "statuts": temoins_statut},
               "L1_temoins_faux_promus": faux_promus, "L2_etat_dents": dents, "L2_vrais_promus": vrais_promus,
               "L3_promues": promues, "L3_nombre_promues": len(promues),
               "L3_promues_liees_a_un_temoin_vrai": sum(bool(p["lien_temoin_vrai"]) for p in promues),
               "qualite_cumulee": bilan.get("qualite_cumulee"), "depense_simulee_usd": bilan.get("depense_totale")}
    ecrire_json_scelle(os.path.join(dossier, "lecture-couche1bis.json"), lecture)
    return lecture


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("banque")
    a.add_argument("temoins")
    a.add_argument("dossier")
    a.add_argument("--generations", type=int, default=3)
    a.add_argument("--propositions", type=int, default=12)
    a.add_argument("--graine", type=int, default=20261027)
    a.add_argument("--sans-exploration", action="store_true")
    a.add_argument("--nul-aveugle", action="store_true", help="sans le prédicteur connu dans le nul (le connu devient trouvable)")
    a.add_argument("--population", choices=("aleatoire", "mecanique"), default="aleatoire")
    a.add_argument("--temoins-par-generation", type=int, default=3)
    args = a.parse_args(argv)
    lecture = executer(args.banque, args.temoins, args.dossier, args.generations, args.propositions, args.graine,
                       exploration=not args.sans_exploration, nul_informe=not args.nul_aveugle,
                       population_initiale=args.population, temoins_par_generation=args.temoins_par_generation)
    print(json.dumps({k: v for k, v in lecture.items() if k != "L3_promues"}, ensure_ascii=False, indent=1))
    print(json.dumps(lecture["L3_promues"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
