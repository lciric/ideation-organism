"""Attaque de Goodhart contre le juge statistique, v1 : lanceur (fichier neuf, R12). Cœur : `pole/attaque_goodhart_v1.py`.

Deux modes, exclusifs :
- **à blanc** (`--a-blanc --graine G`, G dans [0 ; 2⁶⁴[) : proposeurs scriptés qui imitent l'optimisation, aucun réseau,
  aucune clé ; exploratoire, ne décide rien (essais, mesure de durée) ;
- **réel** (`--preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID`) :
  Kimi et Argon par les adaptateurs du pôle (`demonstrations/ideation_v8.adaptateurs_reels_v56` : adaptateur Kimi v53,
  commande externe v56 ; porte de plafond d'étape A15 transmise avant le premier appel). Graine = empreinte SHA-256 du
  préenregistrement scellé (≥ 2⁶⁴). Le plan est gelé : 3 cartes, 16 tentatives, 20 rejeux, plafond 6 USD, 3 heures.

Gardes avant tout appel et toute écriture (code 2) : dossier de sortie non vide ; mode réel sans préenregistrement scellé
(compagnon `.sha256` conforme), sans `--confirmer-moteur-reel`, sans ligne de GO présente dans le registre nommé, avec un
réglage hors du plan gelé, ou sans adaptateurs nommés « kimi » et « argon » dans la configuration.
Codes : 0 course complète (sortie écrite ; le code ne décide rien, seule la lecture gelée décide) ; 2 refus ; 3 arrêt (liste
d'arrêt : plafond de dépense ou de durée, richesse non finie ; aucun taux n'est lu).

Usage : python3 -I -B demonstrations/attaque_goodhart_v1.py DOSSIER_NEUF --a-blanc --graine 7 [--cartes 3] [--rejeux 20]
"""

import argparse
import json
import os
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole import attaque_goodhart_v1 as ag  # noqa: E402
from pole.outils import ecrire_json_scelle, manifeste, sha256_fichier, verifier_scelle  # noqa: E402

PLAN_GELE = {"cartes": 3, "n_max": 16, "rejeux": 20, "plafond_usd": 6.0, "duree_max_s": 10800.0}
PREFIXE_PREREG = "preenregistrement-attaque-goodhart-v1"
ETAPE = "attaque_goodhart_v1"


def entropie_du_preenregistrement(chemin):
    nom = os.path.basename(chemin)
    if not nom.startswith(PREFIXE_PREREG) or "brouillon" in nom:
        raise ag.AttaqueRefusee(f"mode réel : préenregistrement « {PREFIXE_PREREG}-v<N>.md » scellé, pas {nom}")
    if not os.path.isfile(chemin) or not verifier_scelle(chemin):
        raise ag.AttaqueRefusee(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    empreinte = sha256_fichier(chemin)
    return ag.verifier_entropie(int(empreinte, 16), decisif=True), empreinte


def verifier_go(registre, go):
    if not go or not registre or not os.path.isfile(registre):
        raise ag.AttaqueRefusee("mode réel : --registre-go et --go exigés (GO de Lazar sur devis)")
    with open(registre, encoding="utf-8") as f:
        if go not in f.read():
            raise ag.AttaqueRefusee(f"ligne de GO {go} absente du registre {registre}")
    return go


def proposeurs_reels(args, sortie):
    spec_v8 = __import__("importlib.util").util.spec_from_file_location("ideation_v8_pour_goodhart",
                                                                        os.path.join(ICI, "ideation_v8.py"))
    v8 = __import__("importlib.util").util.module_from_spec(spec_v8)
    spec_v8.loader.exec_module(v8)  # instance propre (R12)
    conf = v8.cfg.lire_configuration_v56(args.configuration)
    base = os.path.join(sortie, "sessions")
    os.makedirs(base, exist_ok=True)
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf, sortie, base)
    if sorted(n for n in adaptateurs if n in ag.FOURNISSEURS) != sorted(ag.FOURNISSEURS):
        raise ag.AttaqueRefusee(f"configuration : adaptateurs « kimi » et « argon » exigés, trouvés {sorted(adaptateurs)}")
    accuses = {n: portes[n].transmettre(ETAPE, PLAN_GELE["plafond_usd"]) for n in ag.FOURNISSEURS}
    budget_appel = float(conf.get("attaque_goodhart", {}).get("budget_appel_usd", 0.10))
    return ({n: ag.ProposeurAdaptateur(adaptateurs[n], os.path.join(base, n), budget_appel) for n in ag.FOURNISSEURS},
            accuses)


def principal(argv=None):
    a = argparse.ArgumentParser(description="Attaque de Goodhart contre le juge statistique (v1)")
    a.add_argument("dossier")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true", help="proposeurs scriptés, sans réseau (exploratoire)")
    g.add_argument("--preenregistrement", help="mode réel : préenregistrement scellé (graine = son empreinte)")
    a.add_argument("--graine", type=int)
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--cartes", type=int, default=PLAN_GELE["cartes"])
    a.add_argument("--n-max", type=int, default=PLAN_GELE["n_max"])
    a.add_argument("--rejeux", type=int, default=PLAN_GELE["rejeux"])
    a.add_argument("--plafond-usd", type=float, default=PLAN_GELE["plafond_usd"])
    a.add_argument("--duree-max-s", type=float, default=PLAN_GELE["duree_max_s"])
    args = a.parse_args(argv)
    try:
        if os.path.exists(args.dossier) and os.listdir(args.dossier):
            raise FileExistsError(f"dossier de sortie non vide : {args.dossier} (on n'écrase jamais)")
        reglages = {"cartes": args.cartes, "n_max": args.n_max, "rejeux": args.rejeux, "plafond_usd": args.plafond_usd,
                    "duree_max_s": args.duree_max_s}
        if args.a_blanc:
            if args.graine is None or args.preenregistrement or args.moteur:
                raise ag.AttaqueRefusee("à blanc : --graine G seulement (ni préenregistrement ni moteur réel)")
            entropie, mode, preenregistrement = ag.verifier_entropie(args.graine, decisif=False), "a-blanc (exploratoire)", None
        else:
            if args.graine is not None:
                raise ag.AttaqueRefusee("mode réel : la graine est l'empreinte du préenregistrement, --graine refusée")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration:
                raise ag.AttaqueRefusee("mode réel : --configuration, --moteur reel et --confirmer-moteur-reel exigés")
            if reglages != PLAN_GELE:
                raise ag.AttaqueRefusee(f"mode réel : plan gelé {PLAN_GELE}, reçu {reglages}")
            verifier_go(args.registre_go, args.go)
            entropie, empreinte = entropie_du_preenregistrement(args.preenregistrement)
            mode, preenregistrement = "reel (decisif)", {"chemin": args.preenregistrement, "sha256": empreinte, "go": args.go}
    except (FileExistsError, ag.AttaqueRefusee) as e:
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    os.makedirs(args.dossier, exist_ok=True)
    accuses = None
    if args.a_blanc:
        proposeurs = {f: ag.ProposeurScripte("optimiseur") for f in ag.FOURNISSEURS}
    else:
        try:
            proposeurs, accuses = proposeurs_reels(args, args.dossier)
        except Exception as e:  # noqa: BLE001 — refus nommé, jamais de repli
            print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
            return 2
    m = manifeste(attaque=ag.VERSION, mode=mode, entropie_racine=str(entropie), reglages=reglages,
                  preenregistrement=preenregistrement, accuses_plafond=accuses, coeur=ag.description(),
                  code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in (
                      "pole/attaque_goodhart_v1.py", "demonstrations/attaque_goodhart_v1.py", "demonstrations/banc_tricheurs_v8.py",
                      "demonstrations/banc_tricheurs_v7.py", "pole/nul_v8.py", "pole/nul_filles_v2.py", "pole/selection_pari.py",
                      "pole/cycle.py", "pole/outils.py")})
    m["regle_des_graines"] = ("SeedSequence (R9) : entropie = int(SHA-256 du préenregistrement scellé, 16) en mode réel, "
                              "--graine (< 2^64) à blanc ; monde de la carte c : spawn_key=(cle('monde'), c) ; données de "
                              "développement : (cle('developpement'), c) ; évaluation : (cle('<fournisseur>|<condition>|"
                              "<juges>|<juge>|scenario|noyau|frais'), c, k) ; rejeu r : (…, c, k, 1 + r)")
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), m)
    compteur = ag.Compteur(args.plafond_usd, args.duree_max_s, time.time)
    try:
        suites, mesures = ag.jouer_tout(proposeurs, entropie, args.cartes, compteur, args.n_max, args.rejeux,
                                        decisif=not args.a_blanc)
    except ag.ArretAttaque as e:
        rapport = {"attaque": ag.VERSION, "mode": mode, "arret": str(e), "appels": compteur.appels,
                   "depense_usd": round(compteur.usd, 4), "issue": "non jugeable (arrêt) : aucun taux lu"}
        ecrire_json_scelle(os.path.join(args.dossier, "attaque-goodhart-v1.json"), rapport)
        print(json.dumps(rapport, ensure_ascii=False), file=sys.stderr)
        return 3
    lecture = ag.lire(suites, mesures)
    rapport = {"attaque": ag.VERSION, "mode": mode, "preenregistrement": preenregistrement, "appels": compteur.appels,
               "reprises": compteur.reprises, "depense_usd": round(compteur.usd, 4),
               "duree_s": round(time.time() - compteur.debut, 1), "lecture": lecture, "suites": suites,
               "rejeux_hors_ligne": mesures}
    ecrire_json_scelle(os.path.join(args.dossier, "attaque-goodhart-v1.json"), rapport)
    print(json.dumps({"mode": mode, "issue": lecture["issue"], "audits": lecture["audits"], "appels": compteur.appels,
                      "depense_usd": rapport["depense_usd"], "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
