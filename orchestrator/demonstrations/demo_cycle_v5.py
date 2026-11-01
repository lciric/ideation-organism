"""Démonstrations du cycle v5 — le pôle complet en simulation (processeur, sans dépense) ; exploratoire, lues dans les deux
sens (préenregistrement levé pour l'exploratoire, mot de Lazar du 27 octobre, 12:02 heure de Paris ; ses « go » de
13:32 et 13:52 : plus de tirages et de traits, la mémoire dans le cycle, un seuil de signature par fiche, un vivier plus
grand pour les marchepieds). Reprend `../orchestrateur-pole-v4/demonstrations/demo_cycle_v4.py` ; ce qui change : seuil
de la signature par fiche (v5) ; B sur un vivier de 60 fiches à 4 traits (`exemples/population-pari-vivier60-4traits-v1.json`),
six paires par génération, cinq générations ; C avec un bras « sans mémoire » ; option `--bras` (exécutions en parallèle).

Socle commun : sélection par pari, juge v1, nul des filles v2 (option stricte), mémoire v4 (signature, héritage),
population et témoins de démonstration (`exemples/`, à 2 ou à 4 traits), quatre générations, graines 1 à 20.

- **A — puissance des filles** (`p_triviale` 0,4, tirage stratifié) : dimension 2 ou 4 × 120 ou 500 tirages par fille.
  Lecture : (A1) aucune fille triviale promue dans les quatre bras ; (A2) la part des autres filles vraies promues monte
  avec les tirages et avec les traits (attendu : de 0,75 environ à 0,9 ou plus) ; (A3) aucune fausse découverte.
- **B — marchepieds** (vivier de 60 fiches, 4 traits, 500 tirages, six paires par génération, cinq générations, sans
  triviales) : tirage stratifié contre stratifié avec marchepieds, dans un monde à lignées fécondes (une fille d'une fille
  est vraie avec la probabilité 0,85, sinon 0,35) et dans un monde plat (vérité d'une fille au hasard, 0,5). Lecture (deux
  faces, comme la piste 3) : (B1) monde fécond : plus de vraies filles promues avec marchepieds ; (B2) monde plat : pas
  d'avantage (au plus un écart de 10 % du total) ; (B3) aucune fausse découverte.
- **C — redites** (2 traits, 120 tirages, `p_redite` 0,5, six générations ; 0,9 dans un premier essai de fumée, déclaré :
  presque toutes les fusions devenaient des redites refusées à la validation et les courses s'arrêtaient à la génération
  0) : politiques héritage, refus, rien, et **sans mémoire** (mémoire inactive : aucune garde). Lecture : (C1) héritage et
  refus : aucune découverte en double ; sans mémoire : au moins une (sinon pas de dents) ; (C2) fausses parmi les redites :
  héritage au plus sans mémoire.
- **A — mesure ajoutée** : filles refusées par la garde prédictive (v4 à deux traits : 31 et 39 sur 20 courses ; attendu
  en v5 : bien moins, de l'ordre de quelques unités).

Essais de fumée déclarés : A, B, C sur 2 graines ; B sur 3 graines après avoir rendu uniques les énoncés des filles (un
même énoncé tronqué partagé par deux filles leur donnait la même vérité déclarée, d'où une « fausse » découverte
apparente : défaut du monde simulé, corrigé dans `simulation.py`).

Usage : python -I -B demonstrations/demo_cycle_v5.py DOSSIER_NEUF --experience A|B|C [--courses N] [--generations G]
        [--bras nom1,nom2]
"""

import argparse
import json
import os
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))

from pole.cycle import ConfigGeneration  # noqa: E402
from pole.fiche import charger_fiches  # noqa: E402
from pole.outils import ecrire_json_scelle, manifeste, normaliser_texte, sha256_fichier  # noqa: E402
from pole.pole import executer_pole  # noqa: E402
from pole.simulation import AdaptateurSimule, MondeSimule  # noqa: E402

EXEMPLES = os.path.join(os.path.dirname(ICI), "exemples")
TESTES = ("survit", "eliminee", "indecise", "retiree", "rejetee (test change)")
SUFFIXE_REDITE = " (reformulé)"

EXPERIENCES = {
    "A": {f"d{d}-n{n}": {"traits": d, "config": {"taille_plan_filles": n}, "adaptateur": {"p_fille_triviale": 0.4}}
          for d in (2, 4) for n in (120, 500)},
    "B": {f"{monde}-{tirage}": {"traits": 4, "vivier": True, "max_paires": 6, "generations": 5,
                                "config": {"taille_plan_filles": 500, "tirage_recombinaison": tirage,
                                           "budget_generation_usd": 40.0},
                                "adaptateur": {"fecondite_lignees": monde == "feconde"}}
          for monde in ("feconde", "plat") for tirage in ("stratifie", "stratifie_marchepieds")},
    "C": dict({politique: {"traits": 2, "config": {"taille_plan_filles": 120, "politique_redite": politique},
                           "adaptateur": {"p_redite": 0.5}}
               for politique in ("heritage", "refus", "rien")},
              sans_memoire={"traits": 2, "memoire_inactive": True, "config": {"taille_plan_filles": 120},
                            "adaptateur": {"p_redite": 0.5}}),
}


def charger(traits, vivier=False):
    suffixe = "-4traits" if traits == 4 else ""
    if vivier:
        population = charger_fiches(os.path.join(EXEMPLES, "population-pari-vivier60-4traits-v1.json"))
    else:
        population = charger_fiches(os.path.join(EXEMPLES, f"population-pari-demo{suffixe}-v1.json"))
    temoins = charger_fiches(os.path.join(EXEMPLES, f"temoins-pari-demo{suffixe}-v1.json"))
    with open(os.path.join(EXEMPLES, "monde-pari-vivier60-v1.json" if vivier else "monde-pari-demo-v1.json"),
              encoding="utf-8") as f:
        verites = json.load(f)["verites"]
    verites.update({t.enonce: t.temoin == "vraie" for t in temoins})
    return population, temoins, verites


def une_course(graine, bras, racine, generations, horodatage):
    population, temoins, verites = charger(bras["traits"], bras.get("vivier", False))
    generations = bras.get("generations", generations)
    monde = MondeSimule(graine, verites)
    reglages = dict(bras["adaptateur"])
    if reglages.get("p_redite"):
        reglages["idees_attirantes"] = [f.vers_dict() for f in population]
    adaptateur = AdaptateurSimule(graine, monde, **reglages)
    reglages_config = dict({"budget_generation_usd": 10.0}, **bras["config"])
    config = ConfigGeneration(selection="pari", graine=graine, **reglages_config).valider()
    bilan = executer_pole(population, temoins, adaptateur, config, generations,
                          reglages_config["budget_generation_usd"] * generations, racine,
                          memoire_active=not bras.get("memoire_inactive", False), horodatage_fourni=horodatage,
                          max_paires=bras.get("max_paires", 3))
    with open(os.path.join(racine, "archive", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    promues_originales = {normaliser_texte(e["enonce"]) for e in index.values()
                          if e.get("statut") == "survit" and not e["enonce"].endswith(SUFFIXE_REDITE)}
    m = {k: 0 for k in ("triviales_testees", "triviales_promues", "filles_testees", "filles_vraies_testees",
                        "filles_vraies_promues", "filles_fausses_promues", "redites_proposees", "redites_refusees",
                        "redites_testees", "decouvertes_en_double", "fausses_parmi_les_redites", "vraies_redites_promues")}
    for e in sorted(index.values(), key=lambda e: e["identifiant"]):
        redite = e["enonce"].endswith(SUFFIXE_REDITE)
        if redite:
            m["redites_proposees"] += 1
            if e.get("statut") == "refusee (redite)":
                m["redites_refusees"] += 1
                continue
        if not e.get("parents") or e.get("statut") not in TESTES:
            continue
        promue = e["statut"] == "survit"
        if redite:
            m["redites_testees"] += 1
            if promue:
                if normaliser_texte(e["enonce"][:-len(SUFFIXE_REDITE)]) in promues_originales:
                    m["decouvertes_en_double"] += 1
                elif not monde.verite(e["enonce"]):
                    m["fausses_parmi_les_redites"] += 1
                else:
                    m["vraies_redites_promues"] += 1
            continue
        if normaliser_texte(e["enonce"]) in adaptateur.filles_triviales:
            m["triviales_testees"] += 1
            m["triviales_promues"] += promue
            continue
        vraie = monde.verite(e["enonce"])
        m["filles_testees"] += 1
        m["filles_vraies_testees"] += vraie
        m["filles_vraies_promues"] += promue and vraie
        m["filles_fausses_promues"] += promue and not vraie
    m["refusees_par_la_garde"] = 0
    for journal in sorted(n for n in os.listdir(os.path.join(racine, "journal")) if n.endswith(".json")):
        with open(os.path.join(racine, "journal", journal), encoding="utf-8") as f:
            m["refusees_par_la_garde"] += sum(not g["accepte"] for g in json.load(f)["gardes_de_redite"].values())
    q = bilan["qualite_cumulee"]
    m.update({k: q[k] for k in ("temoins_faux_testes", "temoins_vrais_testes", "fausses_gardees", "vraies_eliminees")})
    m["generations"] = bilan["generations_executees"]
    return m


def resumer(experience, par):
    total = {}
    for nom, liste in par.items():
        s = {k: sum(x[k] for x in liste) for k in liste[0]}
        s["part_vraies_promues"] = s["filles_vraies_promues"] / s["filles_vraies_testees"] if s["filles_vraies_testees"] else None
        s["part_triviales_promues"] = s["triviales_promues"] / s["triviales_testees"] if s["triviales_testees"] else None
        total[nom] = s
    t = total
    if experience == "A":
        lecture = {"A1_aucune_triviale_promue": all(v["triviales_promues"] == 0 for v in t.values()),
                   "A2_parts_vraies_promues": {k: v["part_vraies_promues"] for k, v in t.items()},
                   "A3_aucune_fausse": all(v["filles_fausses_promues"] == 0 and v["fausses_gardees"] == 0 for v in t.values())}
    elif experience == "B":
        f_s, f_m = t["feconde-stratifie"]["filles_vraies_promues"], t["feconde-stratifie_marchepieds"]["filles_vraies_promues"]
        p_s, p_m = t["plat-stratifie"]["filles_vraies_promues"], t["plat-stratifie_marchepieds"]["filles_vraies_promues"]
        lecture = {"B1_feconde_marchepieds_superieur": f_m > f_s, "B1_vraies_promues_feconde": [f_s, f_m],
                   "B2_plat_sans_avantage": abs(p_m - p_s) <= 0.1 * max(p_s, p_m, 1), "B2_vraies_promues_plat": [p_s, p_m],
                   "B3_aucune_fausse": all(v["filles_fausses_promues"] == 0 and v["fausses_gardees"] == 0 for v in t.values())}
    else:
        lecture = {"C1_aucun_double_heritage_et_refus": t["heritage"]["decouvertes_en_double"] == 0
                                                       and t["refus"]["decouvertes_en_double"] == 0,
                   "C1_doubles_sans_memoire": t["sans_memoire"]["decouvertes_en_double"],
                   "C2_fausses_heritage_au_plus_sans_memoire": t["heritage"]["fausses_parmi_les_redites"]
                                                                <= t["sans_memoire"]["fausses_parmi_les_redites"]}
    return total, lecture


def resumer_partiel(par):
    return {nom: {k: sum(x[k] for x in liste) for k in liste[0]} for nom, liste in par.items()}


def principal():
    a = argparse.ArgumentParser()
    a.add_argument("sortie")
    a.add_argument("--experience", choices=sorted(EXPERIENCES), required=True)
    a.add_argument("--courses", type=int, default=20)
    a.add_argument("--generations", type=int, default=4)
    a.add_argument("--bras", default=None, help="noms de bras séparés par des virgules (exécutions en parallèle)")
    args = a.parse_args()
    if os.path.exists(args.sortie) and os.listdir(args.sortie):
        sys.exit(f"dossier non vide : {args.sortie}")
    os.makedirs(args.sortie, exist_ok=True)
    quand = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    bras = {n: b for n, b in EXPERIENCES[args.experience].items() if not args.bras or n in args.bras.split(",")}
    p = {"experience": args.experience, "courses": args.courses, "generations": args.generations,
         "graines": list(range(1, args.courses + 1)), "bras": bras, "script_sha256": sha256_fichier(os.path.abspath(__file__))}
    ecrire_json_scelle(os.path.join(args.sortie, "manifeste.json"), dict(manifeste(**p), horodatage=quand))
    debut = time.monotonic()
    par = {nom: [] for nom in bras}
    for graine in p["graines"]:
        for nom, reglage in bras.items():
            racine = os.path.join(args.sortie, "courses", f"graine-{graine:02d}-{nom}")
            par[nom].append(une_course(graine, reglage, racine, args.generations, quand))
    total, lecture = (resumer(args.experience, par) if set(par) == set(EXPERIENCES[args.experience])
                      else (resumer_partiel(par), {"partiel": "bras choisis par --bras : lecture à faire sur la réunion"}))
    r = {"parametres": p, "horodatage": quand, "total_par_bras": total, "lecture": lecture, "par_course": par,
         "duree_s": round(time.monotonic() - debut, 1)}
    suffixe = "" if not args.bras else "-" + "-".join(sorted(bras))
    ecrire_json_scelle(os.path.join(args.sortie, f"demo-cycle-v5-{args.experience}{suffixe}.json"), r)
    print(json.dumps({"total_par_bras": total, "lecture": lecture, "duree_s": r["duree_s"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    principal()
