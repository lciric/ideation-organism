"""Course d'idéation de l'organisme : lanceur, **version 5** (orchestrateur v53) — course 2 et son pré-pilote.

- Sans `--course-2`, ce lanceur rend la main au lanceur de la version 4 (`demonstrations/ideation_v4.py`, v52b), chargé à
  part et inchangé (R12) : mêmes arguments, mêmes sorties. Le mode « juges seulement » reste au lanceur v3.
- Avec `--course-2 CONFIGURATION SORTIE_NEUVE` : la course 2 de la v53 (`pole/course2_v53.py`), paramètres **injectés** par
  la configuration JSON (aucun seuil codé ; refus de partir si un paramètre obligatoire manque ou porte « À REMPLIR »).

  python -I -B demonstrations/ideation_v5.py --course-2 CONF.json SORTIE --generations N \
      [--verifier-seulement | --moteur simule | --moteur reel --confirmer-moteur-reel --registre-go registres/go.md]

Ordre des gardes, **avant tout appel et toute écriture** : configuration (manques listés en une fois ; pièces à leur
empreinte) ; configuration de génération (étapes du plan, plafonds de session, lecteurs) ; étage entre générations demandé →
machine jetable (`POLE_MACHINE_JETABLE_V53=1`, aucun nom de clé dans l'environnement) ; moteur réel → **A15** : `GO_ID`
(variable d'environnement, identifiant public, comme la garde `.claude/hooks/garde_calcul.py`) présent, ligne de GO de type
« calcul », accordée par Lazar, en cours de validité, non révoquée, dont le plafond couvre la somme des plafonds de la course
(S17 par génération, plus l'étage) ; puis `--confirmer-moteur-reel`. `--verifier-seulement` : aucune écriture, aucun appel ;
imprime l'empreinte de la configuration, la somme des plafonds, la déclaration des bras (A19, A20).

Codes : 0 génération(s) écrite(s) ; 2 refus ou arrêt (motif sur la sortie d'erreur).
"""

import argparse
import importlib.util
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

_spec = importlib.util.spec_from_file_location("ideation_v4_lanceur_pour_v5", os.path.join(ICI, "ideation_v4.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)  # instance propre à ce lanceur (R12 : le lanceur v4 n'est pas touché)

from pole import configuration_v53 as cfg  # noqa: E402
from pole import course2_v53 as c2  # noqa: E402
from pole import etage_entre_generations_v53 as etg  # noqa: E402

VERSION = "lanceur-ideation-v5 (orchestrateur v53)"


def construire_analyseur():
    a = argparse.ArgumentParser(prog="ideation_v5.py", description="course 2 (v53) ; sans --course-2 : lanceur v4")
    a.add_argument("--course-2", nargs=2, metavar=("CONFIGURATION", "SORTIE"), required=True)
    a.add_argument("--generations", type=int, required=True)
    a.add_argument("--moteur", choices=("simule", "reel"))
    a.add_argument("--verifier-seulement", action="store_true")
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    return a


def adaptateurs_reels(conf):
    from pole.adaptateur_kimi_v53 import AdaptateurKimiProtocole
    from pole.adaptateurs import AdaptateurClaudeSDK, AdaptateurCommandeExterne
    sortie = {}
    for nom, f in (conf.get("fournisseurs") or {}).items():
        t = f.get("type")
        if t == "kimi_protocole":
            sortie[nom] = AdaptateurKimiProtocole(f["url_relais"], modele=f["modele"], prix_entree=f["prix_entree"],
                                                  prix_sortie=f["prix_sortie"], max_sortie_jetons=f["max_sortie_jetons"],
                                                  sortie_min_jetons=f["sortie_min_jetons"], delai_s=f["delai_s"])
        elif t == "commande_externe":
            sortie[nom] = AdaptateurCommandeExterne(f["commande"], exiger_modele_servi=True,
                                                    modeles_servis_permis=f.get("modeles_servis_permis"))
        elif t == "claude_sdk":
            sortie[nom] = AdaptateurClaudeSDK(f["url_relais"], arme=True)
        else:
            raise cfg.ConfigurationRefusee(f"fournisseurs.{nom}.type inconnu : {t!r} (kimi_protocole, commande_externe, claude_sdk)")
    return sortie


def adaptateurs_simules(conf):
    from pole.simulation_v53 import AdaptateurSimuleCourse2
    s = conf.get("simulation") or {}
    if "cout_par_appel_usd" not in s:
        raise cfg.ConfigurationRefusee("moteur simulé : simulation.cout_par_appel_usd exigé (coût fictif, aucun défaut)")
    noms = {p["fournisseur"] for p in conf["proposeurs"]} | {j["fournisseur"] for j in conf["juges"]} | \
        {l["fournisseur"] for l in conf["lecteurs_etiquettes"]} | {conf["aiguilleur"]["fournisseur"]}
    if conf["bisociateur"].get("metteur_fusion"):
        noms.add(conf["bisociateur"]["metteur_fusion"]["fournisseur"])
    return {n: AdaptateurSimuleCourse2(champs_fiche=conf["champs_fiche"], items=conf["items_juge"], champ_titre=conf["champ_titre"],
                                       cout_par_appel_usd=s["cout_par_appel_usd"]) for n in sorted(noms)}


def reglages_etage(conf, moteur, adaptateurs):
    """L'étage entre générations (`etage_tests_de_mort` de la configuration), ou None."""
    e = conf.get("etage_tests_de_mort")
    if not e:
        return None
    from pole import ideation_v2 as idn
    from pole import tests_de_mort_v3 as tdm
    exiges = ("nombre", "tranche", "liste_blanche", "experimentateur", "lecteur", "budget_test_usd", "budget_lecteur_usd",
              "executions_par_fiche", "delai_execution_s", "memoire_mo", "correspondance", "plafond_etage_usd", "fournisseur")
    manques = [k for k in exiges if k not in e]
    if manques:
        raise cfg.ConfigurationRefusee("etage_tests_de_mort : manquent " + ", ".join(manques) + " (aucun défaut)")
    tranche = tdm.charger_tranche(cfg.chemin_piece(conf, e["tranche"]), idn.charger_liste_blanche(cfg.chemin_piece(conf, e["liste_blanche"])))
    if moteur == "reel":
        executeur = tdm.ExecuteurBacASable(delai_s=e["delai_execution_s"], memoire_mo=e["memoire_mo"],
                                           utilisateur_bac=e.get("utilisateur_bac"), racine_travail=e.get("dossier_travail_bac"))
    else:
        executeur = tdm.ExecuteurFactice(delai_s=e["delai_execution_s"], memoire_mo=e["memoire_mo"])
    reglages = {"tranche": tranche, "nombre": e["nombre"], "experimentateur": tuple(e["experimentateur"]),
                "lecteur": tuple(e["lecteur"]), "budget_test_usd": e["budget_test_usd"], "budget_lecteur_usd": e["budget_lecteur_usd"],
                "executions_par_fiche": e["executions_par_fiche"], "delai_execution_s": e["delai_execution_s"],
                "memoire_mo": e["memoire_mo"], "executeur": executeur, "moteur": "claude-sdk" if moteur == "reel" else "simule",
                "plafond_total_usd": e["plafond_etage_usd"]}
    return {"adaptateur": adaptateurs[e["fournisseur"]], "reglages": reglages, "nombre": e["nombre"],
            "tranche_index_sha256": tranche.index_sha256, "correspondance": e["correspondance"],
            "plafond_etage_usd": e["plafond_etage_usd"]}


def course_2(args, environnement=None):
    env = os.environ if environnement is None else environnement
    conf_chemin, sortie = args.course_2
    conf = cfg.lire_configuration(conf_chemin)
    c2.verifier_configuration_generation(conf)
    decl, _ = c2.declarer_bras(conf)
    etage_demande = bool(conf.get("etage_tests_de_mort"))
    if etage_demande:
        etg.exiger_machine_jetable(env)
    plafond = c2.plafond_course(conf, args.generations, conf.get("etage_tests_de_mort") or None)
    go = None
    if args.moteur == "reel":
        if not args.registre_go:
            raise cfg.GoRefuse("A15 : --registre-go exigé avec le moteur réel")
        go = cfg.verifier_go(env.get("GO_ID"), args.registre_go, plafond)
        if not args.confirmer_moteur_reel:
            raise cfg.ConfigurationRefusee("moteur réel : --confirmer-moteur-reel exigé")
    if args.verifier_seulement:
        print(json.dumps({"version": VERSION, "configuration_sha256": conf["empreinte_configuration"], "generations": args.generations,
                          "somme_des_plafonds_usd": plafond, "bras": decl, "etage": etage_demande, "go": go,
                          "ecriture": "aucune", "appel": "aucun"}, ensure_ascii=False, indent=1))
        return 0
    if args.moteur is None:
        raise cfg.ConfigurationRefusee("--moteur simule ou --moteur reel exigé (ou --verifier-seulement)")
    adaptateurs = adaptateurs_reels(conf) if args.moteur == "reel" else adaptateurs_simules(conf)
    etage = reglages_etage(conf, args.moteur, adaptateurs)
    bilan = c2.executer_course(conf, sortie, adaptateurs, nombre_generations=args.generations,
                               go=go or {"moteur": "simule", "go": "sans objet (aucune dépense)"}, etage=etage, environnement=env)
    print(json.dumps({"version": VERSION, "bilan": bilan}, ensure_ascii=False, default=str))
    return 0


def principal(argv=None, environnement=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--course-2" not in argv:
        return base.principal(argv)  # la version 4, inchangée
    args = construire_analyseur().parse_args(argv)
    try:
        return course_2(args, environnement)
    except Exception as e:  # noqa: BLE001 — tout refus ou arrêt rend 2, motif dit
        print(json.dumps({"arret": type(e).__name__ + " : " + str(e)[:2000]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(principal())
