"""Course d'idéation de l'organisme : lanceur, **version 3** (orchestrateur v52 ; les versions 1 et 2, `ideation_v1.py` et
`ideation_v2.py`, restent telles quelles, R12). Sans `--juges-seulement`, ce lanceur **est** la version 2 : il rend la main à
`demonstrations/ideation_v2.py` avec les mêmes arguments (mêmes sorties, octet pour octet).

Nouveau : le mode « juges seulement » (décision du directeur R-805, 30 octobre 2026) — noter les fiches **validées** d'une course
arrêtée, scellées par elle, sans refaire les proposeurs (cœur : `pole/juges_seulement_v1.py`) :

  python -I -B demonstrations/ideation_v3.py SORTIE_NEUVE --juges-seulement COURSE_ARRETEE \\
      --empreinte-manifeste-fin SHA256 --empreinte-fiches-validees SHA256 \\
      --liste-blanche LISTE.json --question Q.md --temoins TEMOINS.json --piece-juge A1.md … \\
      --juge juge-opus=claude-opus-5-5 --juge-externe argon-juge=gemini-4-argon \\
      [--bascule-declaree claude-opus-5-5=claude-opus-4-6] \\
      --budget 'juge_ideation|claude-opus-5-5=4' --budget 'juge_ideation|claude-opus-4-6=4' \\
      --budget 'juge_ideation|gemini-4-argon=3.5' --budget-total-usd 8.4 --budget-externe-usd 3.7 [--budget-controle-usd 0.2] \\
      [--moteur simule | --moteur claude-sdk --url-relais URL --confirmer-moteur-reel --commande-externe "…"
       --attestation-lecture-humaine ATTEST.json] [--horodatage "date -u"] [--prix-entree-usd-par-million-jetons P]

- les empreintes du manifeste de fin et des fiches validées sont **données** (fixées dans le lanceur) : une empreinte qui
  diffère, un sceau faux, une fiche qui ne repasse pas le gabarit à la même empreinte : refus, avant tout appel ;
- `--juge` et `--juge-externe` : liste **explicite** (au moins un juge), étiquettes et modèles de la course (l'anonymisation dépend
  de l'étiquette) ; Fable n'est pas rejoué s'il n'est pas donné ;
- mêmes témoins, mêmes pièces des juges, même question, même liste blanche, même graine : empreintes du manifeste de départ de la
  course ; mêmes consignes : la consigne de juge écrite par la course (même mise à l'écart) doit avoir l'empreinte de sa
  reconstruction ;
- `--bascule-declaree DÉCLARÉ=REPLI` (répétable) : seulement `claude-opus-5-5=claude-opus-4-6` (R-805) ; sur un refus dit par le
  modèle déclaré, et seulement alors, session neuve du même juge sur le modèle de repli (plafond `juge_ideation|REPLI`, à
  donner) ; refus initial, bascule et modèle servi consignés. Toute autre bascule, et tout refus sans bascule déclarée : arrêt ;
- budgets : par rôle (`--budget juge_ideation|MODÈLE=…`), total Claude (`--budget-total-usd`, contrôles et sessions de repli
  déclarées compris), total externe (`--budget-externe-usd`) ; contrôles courts à `--budget-controle-usd` (0,2) par modèle ;
- moteur réel : relais Claude lancé avec `--modeles-permis` = exactement les modèles Claude du mode (juges et replis), relais v2
  (`pole/relais_reel_v2.py`) dès qu'une bascule est déclarée ; juge externe : attestation de lecture humaine scellée (empreinte
  des fiches validées et de la consigne de chaque juge externe), comme au bras différé ;
- `--verifier-seulement` : tout ce qui se vérifie sans appel ni écriture (SORTIE non requise) ; imprime les empreintes et tailles
  des consignes, la reconstruction, les sommes, et les empreintes à porter dans l'attestation. Jamais le contenu d'une fiche ;
- sortie : un dossier **neuf** (R12), manifestes de départ et de fin, notes, classement, lecture, liste des empreintes ; tout scellé.

Codes de sortie : 0 classement lisible ; 4 témoin mal classé chez un juge (classement écrit, marqué illisible) ; 2 refus ou arrêt
(empreinte, réglage, refus d'un modèle sans bascule déclarée, bascule non déclarée, refus d'Argon, toute exception).
"""

import argparse
import importlib.util
import json
import os
import signal
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

_spec = importlib.util.spec_from_file_location("ideation_v2_lanceur", os.path.join(ICI, "ideation_v2.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

from pole import juges_seulement_v1 as js  # noqa: E402
from pole.outils import horodatage  # noqa: E402

OPTIONS_DE_COURSE_REFUSEES = (("proposeur", "--proposeur"), ("proposeur_externe", "--proposeur-externe"), ("piece", "--piece"),
                              ("materiau", "--materiau"), ("seconde_passe", "--seconde-passe"),
                              ("attestation_materiau", "--attestation-materiau"),
                              ("bras_rapporte_differe", "--bras-rapporte-differe"), ("mesurer_consignes", "--mesurer-consignes"),
                              ("construire_liste_blanche", "--construire-liste-blanche"), ("tests_de_mort", "--tests-de-mort"),
                              ("dossier_ferme", "--dossier-ferme"), ("taille_max_consigne_externe", "--taille-max-consigne-externe"),
                              ("budget_passe_2_externe_usd", "--budget-passe-2-externe-usd"))


def construire_analyseur():
    a = base.construire_analyseur()
    a.description = __doc__
    a.add_argument("--juges-seulement", metavar="DOSSIER_COURSE_ARRETEE", default=None,
                   help="v52 (R-805) : note les fiches validées de cette course arrêtée, sans refaire les proposeurs")
    a.add_argument("--empreinte-manifeste-fin", default=None, metavar="SHA256",
                   help="v52 : empreinte attendue du manifeste de fin de la course arrêtée (obligatoire avec --juges-seulement)")
    a.add_argument("--empreinte-fiches-validees", default=None, metavar="SHA256",
                   help="v52 : empreinte attendue de fiches-validees.json (obligatoire avec --juges-seulement)")
    a.add_argument("--bascule-declaree", action="append", default=[], metavar="DÉCLARÉ=REPLI",
                   help="v52 (R-805) : bascule déclarée, sur un refus dit par le modèle déclaré seulement (claude-opus-5-5=claude-opus-4-6)")
    a.add_argument("--verifier-seulement", action="store_true",
                   help="v52 : avec --juges-seulement, vérifie tout sans appel ni écriture et imprime le plan (empreintes, tailles)")
    return a


def lire_bascules(textes, a):
    bascules = {}
    for t in textes:
        if t.count("=") != 1:
            a.error(f"--bascule-declaree : DÉCLARÉ=REPLI attendu (reçu {t!r})")
        declare, repli = (x.strip() for x in t.split("="))
        if declare in bascules:
            a.error(f"--bascule-declaree : deux replis pour {declare!r}")
        bascules[declare] = repli
    return bascules


def fabriquer_adaptateurs(args, plan, sortie):
    """Rend (adaptateur des juges Claude, {étiquette: adaptateur externe}, lecteur du relais ou None, versions, description de
    la commande externe). Fonction de module : les essais la remplacent pour jouer des scénarios de refus."""
    versions = {"python": sys.version.split()[0], "lanceur": "ideation_v3 (v52)", "mode": js.VERSION_MODE}
    lire_relais = None
    if args.moteur == "claude-sdk":
        from pole.adaptateurs import (DELAI_SESSION_S, MoteurNonArme, etat_bac_a_sable_detaille, importer_sdk,
                                      verifier_modele_reel)
        from pole.adaptateurs_v2 import AdaptateurClaudeSDKBascule
        from pole import ideation_v2 as idn
        if not args.confirmer_moteur_reel:
            raise MoteurNonArme("--moteur claude-sdk exige --confirmer-moteur-reel (dépense réelle, relais local requis)")
        if not args.url_relais:
            raise MoteurNonArme("--moteur claude-sdk exige --url-relais")
        idn.valider_url_relais_ideation(args.url_relais)
        for _, m in plan["juges"]:
            verifier_modele_reel(m)
        sdk = importer_sdk()
        versions["claude_agent_sdk"] = getattr(sdk, "__version__", "inconnue")
        versions["outil_ligne_de_commande"] = base.version_outil_ligne_de_commande(sdk)
        etat_bac = etat_bac_a_sable_detaille()
        if not etat_bac["actif"]:
            raise js.JugesSeulementRefuse("bac à sable inactif : " + etat_bac["motif"])
        if not etat_bac["proc_neuf"] and os.geteuid() == 0:
            raise js.JugesSeulementRefuse("le bac à sable ne monte pas un /proc neuf et l'orchestrateur tourne sous root (CL31-15)")
        versions["bac_a_sable"] = etat_bac
        racine, origine = base.racine_depot(args.racine_depot)
        versions["racine_depot"] = {"chemin": racine, "origine": origine}
        interdits = [sortie, plan["course"]["dossier"], racine, os.path.expanduser("~")]
        versions["lectures_interdites"] = interdits
        adaptateur = AdaptateurClaudeSDKBascule(args.url_relais, replis=[b["repli"] for b in plan["bascules"].values()],
                                                arme=True, interdire_lecture=interdits,
                                                delai_s=args.delai_session_s or DELAI_SESSION_S)
        adaptateur.bac_a_sable = etat_bac
        lire_relais = base.lecteur_relais(args.url_relais)
    else:
        adaptateur = base.AdaptateurIdeationSimule(plan["graine"])
    externes, commande = {}, None
    if plan["juges_externes"]:
        if args.commande_externe:
            base.verifier_commande_externe_reelle(args, [], list(plan["juges_externes"]))
            externe = base.adaptateur_commande_externe(args)
            commande = externe.description()
        elif args.moteur == "simule":
            externe = base.AdaptateurIdeationSimule(plan["graine"] + 1)
        else:
            raise js.JugesSeulementRefuse("--juge-externe exige --commande-externe avec le moteur réel")
        externes = {e: externe for e, _ in plan["juges_externes"]}
    return adaptateur, externes, lire_relais, versions, commande


def _juges_seulement(args, a):
    for dest, nom in OPTIONS_DE_COURSE_REFUSEES:
        if getattr(args, dest, None):
            a.error(f"{nom} ne vaut pas avec --juges-seulement (aucun proposeur n'est rejoué)")
    if args.moisson != "aucune":
        a.error("--moisson ne vaut pas avec --juges-seulement")
    for nom in ("liste_blanche", "question", "temoins", "empreinte_manifeste_fin", "empreinte_fiches_validees"):
        if not getattr(args, nom):
            a.error(f"--{nom.replace('_', '-')} est requis avec --juges-seulement")
    if not args.sortie and not args.verifier_seulement:
        a.error("SORTIE est requis (dossier neuf), sauf avec --verifier-seulement")
    if not (args.juge or args.juge_externe):
        a.error("--juges-seulement exige une liste explicite de juges (--juge, --juge-externe)")
    if args.commande_externe and not args.juge_externe:
        a.error("--commande-externe n'a d'usage qu'avec --juge-externe")
    if args.commande_externe_lit_modele and not args.commande_externe:
        a.error("--commande-externe-lit-modele ne se donne qu'avec --commande-externe")
    if args.delai_session_s is not None and not args.delai_session_s > 0:
        a.error("--delai-session-s doit être strictement positif")
    bascules = lire_bascules(args.bascule_declaree, a)
    _p, juges, juges_ext, _x, budgets = base.roles_et_budgets(args)
    juges = [base.paire(j, f"juge-{i + 1}") for i, j in enumerate(args.juge)]  # liste explicite : aucun juge par défaut
    controle = 0.2 if args.budget_controle_usd is None else args.budget_controle_usd
    plan = js.preparer_juges_seulement(
        args.juges_seulement, empreinte_manifeste_fin=args.empreinte_manifeste_fin,
        empreinte_fiches_validees=args.empreinte_fiches_validees, liste_blanche=args.liste_blanche, question=args.question,
        pieces_juge=args.piece_juge, temoins=args.temoins, juges=juges, juges_externes=juges_ext, budgets=budgets,
        budget_total_usd=args.budget_total_usd, budget_externe_usd=args.budget_externe_usd, budget_controle_usd=controle,
        bascules=bascules, prix_caractere_usd=base.idn.prix_caractere(args.prix_entree_usd_par_million_jetons),
        taille_max_consigne_externe=args.taille_max_consigne_externe_bras)
    if args.verifier_seulement:
        print(json.dumps(js.resume_du_plan(plan), ensure_ascii=False, indent=1))
        return 0
    sortie = os.path.abspath(args.sortie)
    if os.path.exists(sortie):
        raise js.JugesSeulementRefuse(f"SORTIE existe déjà : {sortie} (jamais écrasée, R12)")
    adaptateur, externes, lire_relais, versions, commande = fabriquer_adaptateurs(args, plan, sortie)
    res = js.executer_juges_seulement(
        plan, sortie, adaptateur, externes, moteur=args.moteur, lire_etat_relais=lire_relais,
        horodatage=horodatage(args.horodatage), versions=versions, commande_externe=commande,
        attestation_lecture_humaine=args.attestation_lecture_humaine, exiger_attestation=(args.moteur == "claude-sdk"),
        exiger_modele_servi_claude=(args.moteur == "claude-sdk"), max_tours=args.max_tours)
    j = res["journal"]
    bilan = {"sortie": sortie, "classement_lisible_L2_L4": res["lisible"], "fiches_notees": len(plan["fiches"]),
             "juges": sorted(j["modele_servi_par_juge"]), "modele_servi_par_juge": j["modele_servi_par_juge"],
             "bascules": [{k: b.get(k) for k in ("etiquette", "modele_declare", "modele_repli", "modele_servi")} for b in j["bascules"]],
             "temoins_ok_par_juge": res["lecture"]["temoins_ok_par_juge"],
             "cout_total_usd": round(j["cout_total_usd"], 4), "cout_externe_usd": round(j["cout_externe_usd"], 4),
             "cout_fictif": j["cout_fictif"]}
    if res["lisible"]:
        bilan["retenues"] = [(l["rang"], l["identifiant_auteur"], l["total"]) for l in res["classement"] if l["eligible"]][:5]
    print(json.dumps(bilan, ensure_ascii=False, indent=1))
    return 0 if res["lisible"] else 4


def principal(argv=None):
    a = construire_analyseur()
    args = a.parse_args(argv)
    if not args.juges_seulement:
        for nom, valeur in (("--empreinte-manifeste-fin", args.empreinte_manifeste_fin),
                            ("--empreinte-fiches-validees", args.empreinte_fiches_validees),
                            ("--bascule-declaree", args.bascule_declaree), ("--verifier-seulement", args.verifier_seulement)):
            if valeur:
                a.error(f"{nom} ne se donne qu'avec --juges-seulement")
        return base.principal(argv)  # la version 2, inchangée

    def interrompre(num, _cadre):
        raise KeyboardInterrupt(f"signal {num}")
    for sig in (signal.SIGTERM, signal.SIGHUP):
        try:
            signal.signal(sig, interrompre)
        except (ValueError, OSError):
            pass
    try:
        return _juges_seulement(args, a)
    except KeyboardInterrupt as e:
        print(json.dumps({"arret": "interruption : " + str(e)[:200] + " ; session en cours comptée à son plafond, manifeste de "
                          "fin écrit"}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 — tout refus ou arrêt rend 2, motif dit
        print(json.dumps({"arret": type(e).__name__ + " : " + str(e)[:1000]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(principal())
