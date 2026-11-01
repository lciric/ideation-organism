"""Ablation de la mémoire : la même population, les mêmes témoins, la même graine, avec et sans mémoire (simulation).

Mesures (identiques dans les deux bras, calculées après coup sur l'archive) : taux de redites parmi les fiches nouvelles
(Jaccard des 3-grammes ≥ seuil avec une fiche non témoin éliminée à une génération antérieure), redites testées,
survie des fiches nouvelles, qualité sur les témoins, dépense. Les agents simulés ne lisent pas la mémoire : la
différence mesure le seul mécanisme (garde de redite) et rien de la conduite d'agents réels.
"""

import copy
import json
import os

from .memoire import jaccard
from .outils import EcrasementInterdit, ecrire_json_scelle, ecrire_scelle

TESTES = ("survit", "eliminee", "indecise", "retiree", "rejetee (test change)")


def mesurer_bras(racine, seuil_redite=0.5):
    with open(os.path.join(racine, "archive", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    with open(os.path.join(racine, "bilan.json"), encoding="utf-8") as f:
        bilan = json.load(f)
    journaux = sorted(os.listdir(os.path.join(racine, "journal")))
    eliminees_avant, par_generation = [], []
    nouvelles = redites = redites_testees = redites_survivantes = testees = survivantes = 0
    for nom in (j for j in journaux if j.endswith(".json")):
        with open(os.path.join(racine, "journal", nom), encoding="utf-8") as f:
            journal = json.load(f)
        g = journal["generation"]
        filles = [i for i, e in index.items() if i.startswith(f"G{g}-") and e["source"].startswith("recombinaison")]
        stats = {"generation": g, "nouvelles": len(filles), "redites": 0, "redites_testees": 0, "testees": 0, "survivantes": 0}
        for i in filles:
            est_redite = any(jaccard(index[i]["enonce"], e) >= seuil_redite for e in eliminees_avant)
            statut_g = journal["fiches"].get(i, {}).get("statut", index[i]["statut"])
            teste = statut_g in TESTES
            stats["redites"] += est_redite
            stats["redites_testees"] += est_redite and teste
            stats["testees"] += teste
            stats["survivantes"] += statut_g == "survit"
            redites_survivantes += est_redite and statut_g == "survit"
        par_generation.append(stats)
        nouvelles += stats["nouvelles"]
        redites += stats["redites"]
        redites_testees += stats["redites_testees"]
        testees += stats["testees"]
        survivantes += stats["survivantes"]
        eliminees_avant += [index[i]["enonce"] for i, e in journal["fiches"].items()
                            if e.get("statut") == "eliminee" and not index[i]["temoin"]]
    return {"fiches_nouvelles_proposees": nouvelles, "redites_proposees": redites,
            "taux_de_redites": redites / nouvelles if nouvelles else None, "redites_testees": redites_testees,
            "redites_survivantes": redites_survivantes, "nouvelles_testees": testees,
            "survie_des_nouvelles": survivantes / testees if testees else None, "par_generation": par_generation,
            "qualite_temoins": bilan["qualite_cumulee"], "depense_totale": bilan["depense_totale"],
            "generations_executees": bilan["generations_executees"], "arret": bilan["arret"]}


def _moyenne(valeurs):
    valeurs = [v for v in valeurs if v is not None]
    return sum(valeurs) / len(valeurs) if valeurs else None


def executer_ablation(args, population, temoins, config, fabrique_adaptateur):
    """Les deux bras sur `--ablation-graines` graines appariées (graine, graine + 1, …) ; agrégats et détail par graine."""
    from .pole import executer_pole
    if os.path.exists(args.sortie) and os.listdir(args.sortie):
        raise EcrasementInterdit(f"le dossier de sortie existe et n'est pas vide : {args.sortie}")
    graines = [args.graine + i for i in range(max(1, getattr(args, "ablation_graines", 1)))]
    detail = {}
    for graine in graines:
        args.graine = graine
        detail[graine] = {}
        for nom, active in (("avec-memoire", True), ("sans-memoire", False)):
            racine = os.path.join(args.sortie, f"graine-{graine}", nom)
            cfg = copy.deepcopy(config)
            cfg.graine = graine
            executer_pole(population, temoins, fabrique_adaptateur(), cfg, args.generations, args.budget_usd, racine,
                          memoire_active=active, horodatage_fourni=args.horodatage)
            detail[graine][nom] = mesurer_bras(racine)
    args.graine = graines[0]
    cles = ("fiches_nouvelles_proposees", "redites_proposees", "redites_testees", "redites_survivantes",
            "nouvelles_testees", "depense_totale")
    agregat = {}
    for nom in ("avec-memoire", "sans-memoire"):
        bras = [detail[g][nom] for g in graines]
        a = {cle: sum(b[cle] for b in bras) for cle in cles}
        a["taux_de_redites"] = a["redites_proposees"] / a["fiches_nouvelles_proposees"] if a["fiches_nouvelles_proposees"] else None
        a["survie_des_nouvelles"] = _moyenne([b["survie_des_nouvelles"] for b in bras])
        q = [b["qualite_temoins"] for b in bras]
        faux, vrais = sum(x["temoins_faux_testes"] for x in q), sum(x["temoins_vrais_testes"] for x in q)
        a["temoins"] = {"faux_testes": faux, "vrais_testes": vrais,
                        "taux_fausses_gardees": sum(x["fausses_gardees"] for x in q) / faux if faux else None,
                        "taux_vraies_eliminees": sum(x["vraies_eliminees"] for x in q) / vrais if vrais else None}
        agregat[nom] = a
    comparaison = {"graines": graines, "agregat": agregat, "detail": {str(g): d for g, d in detail.items()},
                   "reglages": {"generations": args.generations, "budget_usd": args.budget_usd, "p_redite": args.p_redite,
                                "taux_tricheurs": args.taux_tricheurs, "p_echec": args.p_echec,
                                "p_sans_prediction": args.p_sans_prediction},
                   "lecture": ("Simulation : les agents simulés ne lisent pas la mémoire ; l'écart entre bras mesure le "
                               "mécanisme (redites refusées avant gel, budget épargné), sous l'hypothèse simulée qu'un "
                               "agent de recombinaison repropose des idées déjà présentes avec la probabilité p_redite. "
                               "Aucune conclusion sur des agents réels.")}
    ecrire_json_scelle(os.path.join(args.sortie, "comparaison-memoire-v1.json"), comparaison)
    lignes = ["# Ablation de la mémoire (simulation)\n", comparaison["lecture"] + "\n",
              f"Graines appariées : {graines[0]} à {graines[-1]} ({len(graines)}) ; {args.generations} générations ; "
              f"p_redite = {args.p_redite}.\n", "| mesure (somme sur les graines, sauf taux) | avec mémoire | sans mémoire |",
              "|---|---|---|"]
    for cle in cles + ("taux_de_redites", "survie_des_nouvelles"):
        a, s_ = agregat["avec-memoire"][cle], agregat["sans-memoire"][cle]
        lignes.append(f"| {cle} | {a if not isinstance(a, float) else round(a, 4)} | "
                      f"{s_ if not isinstance(s_, float) else round(s_, 4)} |")
    for cle in ("faux_testes", "vrais_testes", "taux_fausses_gardees", "taux_vraies_eliminees"):
        lignes.append(f"| témoins : {cle} | {agregat['avec-memoire']['temoins'][cle]} | {agregat['sans-memoire']['temoins'][cle]} |")
    ecrire_scelle(os.path.join(args.sortie, "comparaison-memoire-v1.md"), "\n".join(lignes) + "\n")
    return comparaison
