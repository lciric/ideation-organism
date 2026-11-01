"""Course d'idéation de l'organisme : lanceur, **version 7** (orchestrateur v55) — course 2 et pré-pilote.

- Sans `--course-2` ni `--pre-pilote` : rend la main au lanceur v6 (`demonstrations/ideation_v6.py`, v54, chargé à part et
  inchangé, R12), qui la rend au v5, puis au v4.
- `--course-2 CONFIGURATION SORTIE_NEUVE --generations N` : la course 2 de la v55 (`pole/course2_v55.py`).
- `--pre-pilote CONFIGURATION SORTIE_NEUVE` : le pré-pilote du brouillon 7 (`pole/prepilote_v55.py`).

  python -I -B demonstrations/ideation_v7.py (--course-2 CONF SORTIE --generations N | --pre-pilote CONF SORTIE) \
      [--verifier-seulement | --moteur simule | --moteur reel --confirmer-moteur-reel --registre-go registres/go.md]

Ordre des gardes, **avant tout appel et toute écriture** : spécification (brouillon 7) recalculée — exigée conforme pour le
moteur réel (CL19-09), rapportée sinon ; configuration v54 ; configuration du plan (v55) ; pré-pilote → analyseur de l'étage
1 exigé (DEP3) ; É0 : déclaration des bras v55 (A19 « source absente » déclaré sans arrêt, A20, I-9, I-10) puis rejeu de
la table R5 v55 (A12) ; étage → machine jetable v55 ; moteur réel → DEP4 (pièce et phrase de confirmation), décisions d'A15
et cohérence de D-g ; ligne de GO v55 (montant entier, un seul nombre) ; puis `--confirmer-moteur-reel`.

Codes : 0 sortie écrite ; 2 refus, arrêt ou nœud (motif sur la sortie d'erreur).
"""

import argparse
import importlib.util
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

_spec = importlib.util.spec_from_file_location("ideation_v6_lanceur_pour_v7", os.path.join(ICI, "ideation_v6.py"))
v6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v6)  # instance propre (R12 : le lanceur v6 n'est pas touché)
base = v6.base

from pole import configuration_v55 as cfg  # noqa: E402
from pole import course2_v55 as c2  # noqa: E402
from pole import gardes_e0_v55 as ge  # noqa: E402
from pole import prepilote_v55 as pp  # noqa: E402
from pole.etage_entre_generations_v55 import exiger_machine_jetable_v55  # noqa: E402

VERSION = "lanceur-ideation-v7 (orchestrateur v55)"
construire_analyseur = v6.construire_analyseur


def adaptateurs_simules(conf, fournisseurs):
    from pole.simulation_v55 import AdaptateurSimuleV55
    s = conf.get("simulation") or {}
    if "cout_par_appel_usd" not in s:
        raise cfg.ConfigurationRefusee("moteur simulé : simulation.cout_par_appel_usd exigé (coût fictif, aucun défaut)")
    return {n: AdaptateurSimuleV55(champs_fiche=conf["champs_fiche"], items=conf["items_juge"], champ_titre=conf["champ_titre"],
                                   cout_par_appel_usd=s["cout_par_appel_usd"]) for n in sorted(fournisseurs)}


def executer(args, environnement=None, etage1=None, depart_specification=None):
    env = os.environ if environnement is None else environnement
    plan = "pre_pilote" if args.pre_pilote else "course"
    conf_chemin, sortie = args.pre_pilote or args.course_2
    spec = cfg.verifier_specification(depart_specification or RACINE)
    if args.moteur == "reel" and spec["conforme"] is not True:
        raise cfg.ConfigurationRefusee(f"spécification {spec['chemin']} introuvable ou à empreinte différente de "
                                       f"{cfg.SPECIFICATION_SHA256[:8]}… : aucun lancement réel (CL19-09)")
    conf = cfg.lire_configuration_v54(conf_chemin)
    if plan == "course":
        if args.generations is None:
            raise cfg.ConfigurationRefusee("--generations N exigé avec --course-2 (aucun défaut)")
        c2.c54.verifier_configuration_generation_v54(conf)
        n = args.generations
    else:
        if args.generations not in (None, 1):
            raise cfg.ConfigurationRefusee("pré-pilote : une seule exécution (--generations sans objet)")
        pp.verifier_configuration_pre_pilote_v55(conf)
        if etage1 is None:
            raise pp.EtageUnAbsent("étage 1 : analyseur (DEP3) non fourni — le pré-pilote ne part pas (garde R5 ligne 6) ; "
                                   "aucun repli")
        n = 1
    decl, params = c2.declarer_bras_v55(conf)
    table_r5 = ge.rejouer_gardes_v55(conf, decl, params, plan=plan, etage1=etage1)
    etage_conf = conf.get("etage_tests_de_mort") if plan == "course" else None
    if etage_conf:
        exiger_machine_jetable_v55(env)
    montant = cfg.montant_requis(conf, n, etage_conf.get("plafond_etage_usd") if etage_conf else None)
    go = None
    if args.moteur == "reel":
        manques = cfg.verifier_dependances_lancement_v55(conf, plan)
        if manques:
            raise cfg.GoRefuse("A15 : aucun lancement :\n- " + "\n- ".join(manques))
        if not args.registre_go:
            raise cfg.GoRefuse("A15 : --registre-go exigé avec le moteur réel")
        go = cfg.verifier_go_v55(env.get("GO_ID"), args.registre_go, montant)
        if not args.confirmer_moteur_reel:
            raise cfg.ConfigurationRefusee("moteur réel : --confirmer-moteur-reel exigé")
    if args.verifier_seulement:
        print(json.dumps({"version": VERSION, "plan": plan, "configuration_sha256": conf["empreinte_configuration"],
                          "specification": spec, "generations": n, "montant_requis_go_usd": montant, "bras": decl,
                          "table_r5_e0": [{k: x[k] for k in ("ligne", "statut")} for x in table_r5], "etage": bool(etage_conf),
                          "go": go, "ecriture": "aucune", "appel": "aucun"}, ensure_ascii=False, indent=1))
        return 0
    if args.moteur is None:
        raise cfg.ConfigurationRefusee("--moteur simule ou --moteur reel exigé (ou --verifier-seulement)")
    classe = pp.PrePiloteV55 if plan == "pre_pilote" else c2.GenerationV55
    fournisseurs = classe.fournisseurs_requis(conf)
    adaptateurs = base.adaptateurs_reels(conf) if args.moteur == "reel" else adaptateurs_simules(conf, fournisseurs)
    go = go or {"moteur": "simule", "go": "sans objet (aucune dépense)"}
    if plan == "pre_pilote":
        res = pp.PrePiloteV55(conf, sortie, adaptateurs, go=go, etage1=etage1, gardes_e0=table_r5).executer()
        print(json.dumps({"version": VERSION, "pre_pilote": "terminé", "m1": bool(res)}, ensure_ascii=False, default=str))
        return 0
    etage = base.reglages_etage(conf, args.moteur, adaptateurs) if etage_conf else None
    bilan = c2.executer_course_v55(conf, sortie, adaptateurs, nombre_generations=n, go=go, etage=etage, environnement=env)
    print(json.dumps({"version": VERSION, "bilan": bilan}, ensure_ascii=False, default=str))
    return 0


def principal(argv=None, environnement=None, etage1=None, depart_specification=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--course-2" not in argv and "--pre-pilote" not in argv:
        return v6.principal(argv)  # la version 6, inchangée (elle rend la main à la v5)
    args = construire_analyseur().parse_args(argv)
    try:
        return executer(args, environnement, etage1, depart_specification)
    except Exception as e:  # noqa: BLE001 — tout refus, arrêt ou nœud rend 2, motif dit
        print(json.dumps({"arret": type(e).__name__ + " : " + str(e)[:3000]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(principal())
