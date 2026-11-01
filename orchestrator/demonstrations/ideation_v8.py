"""Course d'idéation de l'organisme : lanceur, **version 8** (orchestrateur v56) — course 2 et pré-pilote.

- Sans `--course-2` ni `--pre-pilote` : rend la main au lanceur v7 (`demonstrations/ideation_v7.py`, v55, chargé à part et
  inchangé, R12), qui la rend au v6, puis au v5 et au v4.
- `--course-2 CONFIGURATION SORTIE_NEUVE --generations N` : la course 2 de la v56 (`pole/course2_v56.py`).
- `--pre-pilote CONFIGURATION SORTIE_NEUVE` : le pré-pilote (`pole/prepilote_v56.py`), selon le préenregistrement nommé par
  `specification` (brouillon 10 à ce jour, version gelée après la contre-lecture 5).

  python -I -B demonstrations/ideation_v8.py (--course-2 CONF SORTIE --generations N | --pre-pilote CONF SORTIE) \
      [--verifier-seulement | --moteur simule | --moteur reel --confirmer-moteur-reel --registre-go registres/go.md]

Ordre des gardes, **avant tout appel et toute écriture dans la sortie** : configuration v56 (plan de dépense à plafonds de
relais, Gu-Krenn « substitut », DEP4 sans phrase « réservation ») ; spécification nommée (`specification`, CL20-03) — exigée
conforme pour le moteur réel, rapportée sinon ; configuration du plan (v56 : D-i, M6b, interrupteur A21 en attente de N5) ;
pré-pilote → analyseur de l'étage 1 exigé (DEP3) ; É0 : déclaration des bras v56 (CL20-10) puis table R5 v56 (lignes 1, 5,
11a, 11b, 29 ; A12) ; étage → machine jetable v56 (liste blanche) ; moteur réel → DEP4 et A15 (porte de plafond par relais),
décisions d'A15 (D-g, D-i) ; ligne de GO ; `--confirmer-moteur-reel`. Moteur réel : commande externe v56 (recopie du modèle
servi, CL20-01) ; kit d'agent avec lecture interdite sur la base des sessions **et** la sortie (CL20-06) ; une porte de
plafond d'étape par relais (CL20-02).

Codes : 0 sortie écrite ; 2 refus, arrêt (signal compris) ou nœud (motif sur la sortie d'erreur).
"""

import importlib.util
import json
import os
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

_spec = importlib.util.spec_from_file_location("ideation_v7_lanceur_pour_v8", os.path.join(ICI, "ideation_v7.py"))
v7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v7)  # instance propre (R12 : le lanceur v7 n'est pas touché)
base = v7.base

from pole import configuration_v56 as cfg  # noqa: E402
from pole import course2_v56 as c2  # noqa: E402
from pole import gardes_e0_v56 as ge  # noqa: E402
from pole import prepilote_v56 as pp  # noqa: E402
from pole.etage_entre_generations_v56 import exiger_machine_jetable_v56  # noqa: E402
from pole.noyau_v56 import ArretParSignal  # noqa: E402

VERSION = "lanceur-ideation-v8 (orchestrateur v56)"
construire_analyseur = v7.construire_analyseur


def adaptateurs_simules(conf, fournisseurs):
    from pole.simulation_v56 import AdaptateurSimuleV56
    s = conf.get("simulation") or {}
    if "cout_par_appel_usd" not in s:
        raise cfg.ConfigurationRefusee("moteur simulé : simulation.cout_par_appel_usd exigé (coût fictif, aucun défaut)")
    return {n: AdaptateurSimuleV56(champs_fiche=conf["champs_fiche"], items=conf["items_juge"], champ_titre=conf["champ_titre"],
                                   cout_par_appel_usd=s["cout_par_appel_usd"]) for n in sorted(fournisseurs)}


def adaptateurs_reels_v56(conf, sortie, base_sessions):
    """Adaptateurs du moteur réel et leurs portes de plafond d'étape. Commande externe : v56 (CL20-01) ; kit : lecture interdite
    sur [base des sessions, sortie] (CL20-06) ; chaque relais : `fournisseurs.<nom>.porte_plafond` (A15, CL20-02)."""
    from pole.adaptateur_kimi_v53 import AdaptateurKimiProtocole
    from pole.adaptateurs import AdaptateurClaudeSDK
    from pole.adaptateurs_v56 import AdaptateurCommandeExterneV56, porte_depuis_configuration
    adaptateurs, portes = {}, {}
    interdits = [os.path.realpath(base_sessions), os.path.realpath(os.path.abspath(sortie))]
    for nom, f in sorted((conf.get("fournisseurs") or {}).items()):
        t = f.get("type")
        if t == "kimi_protocole":
            ad = AdaptateurKimiProtocole(f["url_relais"], modele=f["modele"], prix_entree=f["prix_entree"], prix_sortie=f["prix_sortie"],
                                         max_sortie_jetons=f["max_sortie_jetons"], sortie_min_jetons=f["sortie_min_jetons"],
                                         delai_s=f["delai_s"])
        elif t == "commande_externe":
            ad = AdaptateurCommandeExterneV56(f["commande"], exiger_modele_servi=True, modeles_servis_permis=f.get("modeles_servis_permis"))
        elif t == "claude_sdk":
            ad = AdaptateurClaudeSDK(f["url_relais"], arme=True, interdire_lecture=interdits)
        else:
            raise cfg.ConfigurationRefusee(f"fournisseurs.{nom}.type inconnu : {t!r} (kimi_protocole, commande_externe, claude_sdk)")
        adaptateurs[nom] = ad
        portes[nom] = porte_depuis_configuration(nom, f.get("porte_plafond"), ad)
    return adaptateurs, portes


def executer(args, environnement=None, etage1=None):
    env = os.environ if environnement is None else environnement
    plan = "pre_pilote" if args.pre_pilote else "course"
    conf_chemin, sortie = args.pre_pilote or args.course_2
    conf = cfg.lire_configuration_v56(conf_chemin)
    spec = cfg.verifier_specification_v56(conf)
    if args.moteur == "reel" and spec["conforme"] is not True:
        raise cfg.ConfigurationRefusee(f"spécification non conforme ({spec['motif']}) : aucun lancement réel (CL20-03)")
    if plan == "course":
        if args.generations is None:
            raise cfg.ConfigurationRefusee("--generations N exigé avec --course-2 (aucun défaut)")
        c2.verifier_configuration_generation_v56(conf)
        n = args.generations
    else:
        if args.generations not in (None, 1):
            raise cfg.ConfigurationRefusee("pré-pilote : une seule exécution (--generations sans objet)")
        pp.verifier_configuration_pre_pilote_v56(conf)
        if etage1 is None:
            raise pp.EtageUnAbsent("étage 1 : analyseur (DEP3) non fourni — le pré-pilote ne part pas (garde R5 ligne 6) ; "
                                   "aucun repli")
        n = 1
    decl, params = c2.declarer_bras_v56(conf)
    table_r5 = ge.rejouer_gardes_v56(conf, decl, params, plan=plan, etage1=etage1, specification=spec)
    etage_conf = conf.get("etage_tests_de_mort") if plan == "course" else None
    permis = (etage_conf or {}).get("environnement_permis") or ()
    if etage_conf:
        exiger_machine_jetable_v56(env, permis_en_plus=permis)
    montant = cfg.montant_requis(conf, n, etage_conf.get("plafond_etage_usd") if etage_conf else None)
    go = None
    if args.moteur == "reel":
        manques = cfg.verifier_dependances_lancement_v56(conf, plan)
        if manques:
            raise cfg.GoRefuse("A15 : aucun lancement :\n- " + "\n- ".join(manques))
        if not args.registre_go:
            raise cfg.GoRefuse("A15 : --registre-go exigé avec le moteur réel")
        go = cfg.verifier_go_v56(env.get("GO_ID"), args.registre_go, montant)
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
    classe = pp.PrePiloteV56 if plan == "pre_pilote" else c2.GenerationV56
    fournisseurs = classe.fournisseurs_requis(conf)
    base_sessions = tempfile.mkdtemp(prefix="pole-sessions-v56-")  # hors de la sortie (CL19-04), créée avant les adaptateurs (CL20-06)
    if args.moteur == "reel":
        adaptateurs, portes = adaptateurs_reels_v56(conf, sortie, base_sessions)
    else:
        adaptateurs, portes = adaptateurs_simules(conf, fournisseurs), None
    go = go or {"moteur": "simule", "go": "sans objet (aucune dépense)"}
    if plan == "pre_pilote":
        res = pp.PrePiloteV56(conf, sortie, adaptateurs, go=go, etage1=etage1, gardes_e0=table_r5, racine_sessions=base_sessions,
                              portes=portes, specification=spec).executer()
        print(json.dumps({"version": VERSION, "pre_pilote": "terminé", "m1": bool(res)}, ensure_ascii=False, default=str))
        return 0
    etage = base.reglages_etage(conf, args.moteur, adaptateurs) if etage_conf else None
    bilan = c2.executer_course_v56(conf, sortie, adaptateurs, nombre_generations=n, go=go, etage=etage, environnement=env,
                                   racine_sessions=base_sessions, portes=portes, specification=spec)
    print(json.dumps({"version": VERSION, "bilan": bilan}, ensure_ascii=False, default=str))
    return 0


def principal(argv=None, environnement=None, etage1=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--course-2" not in argv and "--pre-pilote" not in argv:
        return v7.principal(argv)  # la version 7, inchangée (elle rend la main à la v6)
    args = construire_analyseur().parse_args(argv)
    try:
        return executer(args, environnement, etage1)
    except (Exception, ArretParSignal, KeyboardInterrupt) as e:  # noqa: BLE001 — tout refus, arrêt (signal compris) ou nœud rend 2
        print(json.dumps({"arret": type(e).__name__ + " : " + str(e)[:3000]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(principal())
