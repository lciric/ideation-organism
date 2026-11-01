"""La boucle du pôle : population initiale, générations, témoins plantés, mémoire, recombinaison, arrêts, journal,
archive complète — et la ligne de commande."""

import argparse
import copy
from dataclasses import asdict
import json
import os
import random
import sys

from .caviardage import caviarder, caviarder_objet
from .cycle import Budget, ConfigGeneration, Generation, cumuler_qualite
from .fiche import RegistreGel, charger_fiches
from .memoire import Memoire
from .outils import (EcrasementInterdit, dossier_traces, ecrire_json_scelle, ecrire_scelle, extraire_bloc_json,
                     graine_derivee, horodatage, manifeste)
from .recombinaison import recombiner


class SortieNonVide(EcrasementInterdit):
    pass


def tirer_temoins(liste, rng, utilises, par_generation=1):
    """Au moins une vraie et une fausse par génération, sans remise tant que la liste le permet."""
    choisis, remises = [], []
    for verite in ("vraie", "fausse"):
        groupe = sorted((t for t in liste if t.temoin == verite), key=lambda t: t.identifiant)
        if not groupe:
            raise ValueError(f"la liste de témoins ne contient aucun témoin « {verite} »")
        libres = [t for t in groupe if t.identifiant not in utilises]
        if len(libres) < par_generation:
            remises.append(verite)
            libres = groupe
        for t in rng.sample(libres, par_generation):
            utilises.add(t.identifiant)
            copie = copy.deepcopy(t)
            copie.source, copie.statut, copie.essais, copie.historique = f"temoin:{t.identifiant}", "proposee", 0, []
            choisis.append(copie)
    return choisis, remises


def _synthese(adaptateur, config, memoire, budget, dossier, generation):
    if not budget.reserver(config.plafond_synthese_usd):
        return None, "budget insuffisant pour la synthèse"
    os.makedirs(dossier, exist_ok=False)
    traces = dossier_traces(dossier)  # v7, version 5 : produits de l'orchestrateur hors du dossier de l'agent
    ecrire_json_scelle(os.path.join(dossier, "resume-index.json"), memoire.resume_pour_synthese(generation))
    consigne = ("Écris les leçons de cette génération (au plus 1 500 caractères) à partir du seul fichier "
                "`resume-index.json` : causes d'élimination fréquentes, protocoles qui ont fonctionné. Les leçons portent "
                "sur la science (hypothèses, protocoles), jamais sur les fichiers ni la plomberie de l'orchestrateur. "
                "Réponds par un bloc ```json {\"lecons\": \"...\"}``` dans ton dernier message, sans écrire de fichier.")
    ecrire_scelle(os.path.join(traces, "consigne.txt"), consigne)
    res = adaptateur.lancer("synthese", consigne, dossier, config.plafond_synthese_usd, config.max_tours_synthese,
                            modele=config.modele_synthese)
    budget.regler(config.plafond_synthese_usd, res.cout_declare_usd)
    ecrire_scelle(os.path.join(traces, "reponse.txt"), caviarder(res.texte_final)[0])
    bloc = extraire_bloc_json(res.texte_final, "lecons") or {}
    texte = memoire.ajouter_lecon(generation, bloc.get("lecons") or res.texte_final)
    ecrire_json_scelle(os.path.join(traces, "lecons.json"), {"generation": generation, "lecons": texte})
    return texte, None


def executer_pole(population, temoins, adaptateur, config, generations, budget_total_usd, racine, memoire_active=True,
                  horodatage_fourni=None, temoins_par_generation=1, k_recombinaison=4, max_paires=3, monde_noyau=None):
    config.valider()
    if monde_noyau is not None and config.selection != "pari":
        raise ValueError("le monde tenu par le noyau suppose la sélection par pari")
    # v11 (contre-lectures C3 et C1 du socle) : sur une banque figée, l'héritage de la preuve entre générations exige une
    # tranche d'épreuve fraîche par génération (sinon produit d'e-valeurs sur les mêmes issues) — vérifié ici, donc aussi
    # pour les bras lancés en mémoire (duel), pas seulement par la ligne de commande.
    tranches = getattr(monde_noyau, "tranches", None)
    if (monde_noyau is not None and tranches is not None and memoire_active and config.politique_redite == "heritage"
            and generations > 1 and tranches < generations):
        raise ValueError(f"banque à {tranches} tranche(s) pour {generations} générations avec héritage de la preuve : "
                         "il faut une tranche par génération (tranches ≥ générations), ou politique_redite refus|rien, "
                         "ou la mémoire inactive")
    # v11 (contre-lecture C10 du socle) : « témoins sans agents » sans monde qui dépose les issues était accepté sans signal
    if config.temoins_sans_agent and monde_noyau is None:
        raise ValueError("temoins_sans_agent exige un monde tenu par le noyau (banque ou monde caché) : ailleurs, "
                         "personne ne dépose d'issue pour les témoins")
    if os.path.exists(racine) and os.listdir(racine):
        raise SortieNonVide(f"le dossier de sortie existe et n'est pas vide : {racine} (on n'écrase jamais)")
    os.makedirs(racine, exist_ok=True)
    quand = horodatage(horodatage_fourni)
    ecrire_json_scelle(os.path.join(racine, "manifeste.json"), manifeste(
        config=asdict(config), generations=generations, budget_total_usd=budget_total_usd, memoire_active=memoire_active,
        temoins_par_generation=temoins_par_generation, k_recombinaison=k_recombinaison, max_paires=max_paires,
        adaptateur=getattr(adaptateur, "nom", type(adaptateur).__name__), horodatage=quand,
        bac_a_sable=getattr(adaptateur, "bac_a_sable", None),
        monde_noyau=None if monde_noyau is None else getattr(monde_noyau, "nom", type(monde_noyau).__name__),
        banque=None if monde_noyau is None else {"chemin": getattr(monde_noyau, "chemin", None),
                                                 "empreinte": getattr(monde_noyau, "empreinte_banque", None),
                                                 "tranches": tranches},  # v11 (C11 du socle) : la banque au manifeste
        population=[f.identifiant for f in population], temoins=[t.identifiant for t in temoins]))
    generateur = None
    if monde_noyau is not None and hasattr(monde_noyau, "description_publique"):
        from .proposeurs_references import generateur_reference_au_gabarit  # v12 : référence au gabarit du monde
        generateur = generateur_reference_au_gabarit(monde_noyau.description_publique())
    memoire = Memoire(active=memoire_active, graine=config.graine, politique_redite=getattr(config, "politique_redite", "heritage"),
                      generateur_reference=generateur)
    registre = RegistreGel()
    rng = random.Random(graine_derivee(config.graine, "pole"))
    toutes, lois_connues, a_reessayer, deja, utilises = {}, {}, [], set(), set()
    depots = {}  # v6 : un dépôt (ordre secret, mesures du noyau) par engagement, pour toute la course
    expliquees = set()  # v7 : fiches éliminées expliquées par le prédicteur connu (drapeau servi au proposeur)
    verdicts_montres = 0  # v7 : exposition adaptative — verdicts montrés au proposeur
    qualites, depense, arret, journaux = [], 0.0, None, []
    nouvelles = []
    for f in population:
        copie = copy.deepcopy(f)
        copie.source = f"population-initiale:{f.identifiant}"
        nouvelles.append(copie)
    for g in range(generations):
        plantes, remises = tirer_temoins(temoins, rng, utilises, temoins_par_generation)
        entrantes = nouvelles + plantes
        rng.shuffle(entrantes)
        alias = {}
        for numero, f in enumerate(entrantes, 1):
            alias[f.identifiant if not f.source.startswith(("population-initiale", "temoin")) else f.source] = f"G{g}-F{numero:02d}"
            f.identifiant = f"G{g}-F{numero:02d}"
        gardes = {}
        memoire.nouvelle_generation()
        for f in entrantes:
            if f.temoin is None:
                garde = memoire.garde_redite(f)
                gardes[f.identifiant] = garde
                if not garde["accepte"]:
                    f.statut = "refusee (redite)"
        for f in a_reessayer:  # v4 : une fiche réessayée repasse la garde prédictive (sa classe a pu changer)
            if f.temoin is None and f.loi_predictive and memoire.active:
                garde = memoire.garde_redite(f)
                gardes[f.identifiant] = garde
                if not garde["accepte"]:
                    f.statut = "refusee (redite)"
        a_reessayer = [f for f in a_reessayer if f.statut != "refusee (redite)"]
        for f in entrantes:
            toutes[f.identifiant] = f
            if f.loi_predictive:
                lois_connues[f.identifiant] = f.loi_predictive
        liste = [f for f in entrantes if f.statut == "proposee"] + a_reessayer
        budget = Budget(max(0.0, min(config.budget_generation_usd, budget_total_usd - depense)))
        texte_servi = memoire.texte_consigne("experimentateur")
        rapport = Generation(g, adaptateur, config, racine, registre, budget, memoire, lois_connues,
                             monde_noyau=monde_noyau, depots=depots).executer(liste)
        for f in entrantes + a_reessayer:
            issue = rapport["issues"].get(f.identifiant) or {"verdict_final": f.statut, "motif": gardes.get(
                f.identifiant, {}).get("motif"), "famille_source": f.famille_source(), "couts": {}}
            memoire.indexer(f, issue, g)
        a_reessayer = [f for f in liste if f.statut in ("indecise", "hors budget")]
        dossier_g = os.path.join(racine, "archive", "generations", f"generation-{g:02d}")
        lecons, motif_lecons = (_synthese(adaptateur, config, memoire, budget, os.path.join(dossier_g, "synthese"), g)
                                if memoire.active else (None, "mémoire inactive"))
        pool = [f for f in toutes.values() if f.statut == "survit" and f.temoin is None]
        os.makedirs(os.path.join(dossier_g, "recombinaison"), exist_ok=True)
        reco = recombiner(pool, adaptateur, config, os.path.join(dossier_g, "recombinaison"), budget, g,
                          k=k_recombinaison, max_paires=max_paires, memoire=memoire if memoire.active else None,
                          deja_fusionnees=deja)
        nouvelles = reco["filles"]
        rapport_proposeur = None
        if getattr(config, "propositions_par_generation", 0) and monde_noyau is not None \
                and hasattr(monde_noyau, "description_publique") and g + 1 < generations:
            from .proposeur import expliquees_par_le_connu, proposer
            expliquees |= expliquees_par_le_connu(rapport["issues"])
            verdicts_montres += sum(1 for i in rapport["issues"].values() if i.get("verdict_final") in ("survit", "eliminee"))
            prop = proposer(adaptateur, config, monde_noyau, memoire if memoire.active else None, g + 1,
                            os.path.join(dossier_g, "proposeur"), budget, config.propositions_par_generation, expliquees)
            nouvelles = nouvelles + prop["fiches"]
            rapport_proposeur = dict(prop["rapport"], fiches=[f.identifiant for f in prop["fiches"]],
                                     exposition={"verdicts_montres_au_proposeur": verdicts_montres,
                                                 "tranches": getattr(monde_noyau, "tranches", 1)})
        depense += budget.depense
        qualites.append(rapport["qualite"])
        restant = budget_total_usd - depense
        cout_minimal = config.plafond_verificateur_usd + min(
            [config.plafond_experimentateur_usd] + [f.cout_borne for f in nouvelles + a_reessayer])
        erreurs = rapport.get("erreurs_orchestrateur") or {"fiches": [], "lancees": 0}
        if len(erreurs["fiches"]) >= 2 and 2 * len(erreurs["fiches"]) >= max(1, erreurs["lancees"]):
            # v7, version 5 : la moitié au moins des fiches lancées en erreur de l'orchestrateur : la plomberie est en
            # cause ; on n'en relance aucune (en (a), cinq sur cinq en génération 1).
            arret = (f"erreurs de l'orchestrateur ({len(erreurs['fiches'])} fiches sur {erreurs['lancees']} lancées) : "
                     "la plomberie est en cause, rien n'est relancé")
        elif g + 1 >= generations:
            arret = "nombre de générations atteint"
        elif restant < cout_minimal:
            arret = "budget épuisé"
        elif not pool and not a_reessayer and not (rapport_proposeur and nouvelles):
            arret = "plus aucune fiche ne survit"
        elif not nouvelles and not a_reessayer:
            arret = "rien de nouveau à tester"
        journal = {
            "generation": g, "horodatage": quand, "selection": config.selection, "memoire_active": memoire.active,
            "alias": alias, "temoins_plantes": [t.identifiant for t in plantes], "temoins_remis_en_jeu": remises,
            "gardes_de_redite": gardes, "fiches": {i: dict(issue, source=toutes[i].source if i in toutes else None,
                                                           temoin=toutes[i].temoin if i in toutes else None)
                                                   for i, issue in rapport["issues"].items()},
            "refusees_avant_gel": [f.identifiant for f in entrantes if f.statut == "refusee (redite)"],
            "qualite_generation": rapport["qualite"], "qualite_cumulee": cumuler_qualite(qualites),
            "budget_generation": budget.etat(), "depense_totale": round(depense, 6), "budget_total": budget_total_usd,
            "memoire": {"texte_servi_aux_experimentateurs": texte_servi, "lecons_ecrites": lecons,
                        "motif_sans_lecons": motif_lecons, "gabarits": memoire.gabarits(),
                        "calibration": memoire.registre_calibration()},
            "recombinaison": dict(reco["rapport"], filles=[f.identifiant for f in reco["filles"]],
                                  refusees=reco["refusees"]),
            "proposeur": rapport_proposeur,
            "erreurs_orchestrateur": erreurs,
            "arret": arret,
        }
        journal = caviarder_objet(journal)[0]
        ecrire_json_scelle(os.path.join(racine, "journal", f"generation-{g:02d}.json"), journal)
        ecrire_json_scelle(os.path.join(racine, "memoire", f"memoire-generation-{g:02d}.json"), memoire.instantane())
        journaux.append(journal)
        if arret:
            break
    index = {}
    for i, f in sorted(toutes.items()):
        etat = dict(f.vers_dict(), aptitude=f.aptitude() if f.statut == "survit" else None,
                    empreinte=registre.empreinte(i) if registre.est_gelee(i) else None)
        index[i] = {k: etat[k] for k in ("identifiant", "source", "temoin", "statut", "essais", "aptitude", "parents",
                                         "empreinte", "historique", "enonce", "severite_attendue")}
        ecrire_json_scelle(os.path.join(racine, "archive", "fiches", i, "etat-final.json"), caviarder_objet(etat)[0])
    ecrire_json_scelle(os.path.join(racine, "archive", "index.json"), caviarder_objet(index)[0])
    bilan = {"horodatage": quand, "generations_executees": len(journaux), "arret": arret, "depense_totale": round(depense, 6),
             "budget_total": budget_total_usd, "qualite_cumulee": cumuler_qualite(qualites),
             "comptes_par_statut": _comptes(toutes), "selection": config.selection, "memoire_active": memoire.active,
             "survivantes": {i: index[i]["aptitude"] for i in index if index[i]["statut"] == "survit"},
             "registre_gel": registre.etat(), "bac_a_sable": getattr(adaptateur, "bac_a_sable", None)}
    ecrire_json_scelle(os.path.join(racine, "bilan.json"), bilan)
    return bilan


def _comptes(toutes):
    comptes = {}
    for f in toutes.values():
        comptes[f.statut] = comptes.get(f.statut, 0) + 1
    return dict(sorted(comptes.items()))


# --- ligne de commande ---------------------------------------------------------------------------------------------
def analyseur():
    a = argparse.ArgumentParser(prog="pole", description="Pôle « scientifique automatique » : générations d'hypothèses "
                                "gelées, testées, vérifiées, sélectionnées, recombinées.")
    a.add_argument("--moteur", choices=("simule", "claude-sdk"), default="simule")
    a.add_argument("--population", help="fichier JSON de la population initiale")
    a.add_argument("--temoins", help="fichier JSON de la liste des témoins (vérité connue)")
    a.add_argument("--generations", type=int, default=3)
    a.add_argument("--budget-usd", type=float, default=30.0, help="budget total du pôle")
    a.add_argument("--budget-generation-usd", type=float, help="plafond par génération (défaut : total / générations)")
    a.add_argument("--sortie", required=True, help="dossier de sortie, absent ou vide (jamais écrasé)")
    a.add_argument("--selection", choices=("seuil", "pari"), default="seuil")
    a.add_argument("--alpha", type=float, default=0.05)
    a.add_argument("--graine", type=int, default=20261026)
    a.add_argument("--concurrence", type=int, default=4)
    a.add_argument("--modele-experimentateur", default="simule-a")
    a.add_argument("--modele-verificateur", default="simule-b")
    a.add_argument("--modele-recombinaison", default="simule-c")
    a.add_argument("--modele-synthese", default="simule-d")
    a.add_argument("--sans-memoire", action="store_true")
    a.add_argument("--horodatage", help="heure UTC lue sur `date -u` dans la commande de lancement")
    a.add_argument("--url-relais", help="moteur réel : relais local du noyau qui ajoute la clé (http://127.0.0.1:PORT)")
    a.add_argument("--confirmer-moteur-reel", action="store_true",
                   help="arme le moteur réel (sans ce drapeau, aucun agent réel n'est jamais lancé)")
    a.add_argument("--roles-reels", default="",
                   help="v7 : avec --moteur claude-sdk, rôles joués par de vrais agents (par exemple « proposeur ») ; "
                        "les autres sont simulés (monde tenu par le noyau : verdict inchangé, coût réduit)")
    a.add_argument("--accepter-sans-bac-a-sable", action="store_true",
                   help="v7 : moteur réel sans bac à sable actif (exception, motif écrit exigé, jamais sous root)")
    a.add_argument("--motif-sans-bac-a-sable", default="", help="raison écrite de l'exception (consignée au manifeste)")
    a.add_argument("--delta0", type=float, default=0.01, help="marge des filles en sélection par pari (nat par tirage)")
    p = a.add_argument_group("sélection par pari (v3 à v6)")
    p.add_argument("--juge", choices=("v0", "v1"), default="v1")
    p.add_argument("--nul-filles", choices=("v0", "v2", "v2_souple"), default="v2")
    p.add_argument("--taille-plan", type=int, default=120, help="instances du plan d'une fiche sans parents")
    p.add_argument("--taille-plan-filles", type=int, default=300, help="instances du plan d'une fille (v4)")
    # v11 (contre-lecture C2) : les réglages du juge que le script du duel fixait en interne pour les bras de référence
    # n'étaient pas accessibles aux bras à modèle lancés par cette ligne de commande (8 contre 6, 40 contre 12, 3 contre 2).
    p.add_argument("--instants-filles", type=int, default=8, help="instants de lecture d'une fille (défaut 8)")
    p.add_argument("--part-calibrage", type=int, default=40, help="instances de calibrage des membres ajustés (défaut 40)")
    p.add_argument("--k-recombinaison", type=int, default=4, help="filles par recombinaison (défaut 4)")
    p.add_argument("--max-paires", type=int, default=3, help="paires de parents par recombinaison (défaut 3)")
    p.add_argument("--tirage-recombinaison", choices=("stratifie", "stratifie_marchepieds", "noyau_corrige"),
                   default="stratifie")
    p.add_argument("--politique-redite", choices=("heritage", "refus", "rien"), default="heritage")
    p.add_argument("--noyau-secret", action="store_true",
                   help="graine du noyau tirée par `secrets` (exécution réelle), écrite après les évaluations sous noyau/")
    p.add_argument("--monde-noyau", nargs="?", const="", metavar="FICHIER",
                   help="monde caché tenu par le noyau (v6, option a) : issues déposées après le gel dans le dossier de "
                        "l'expérience ; FICHIER JSON {\"verites\": {énoncé: vrai|faux}} facultatif (témoins toujours "
                        "connus ; le reste tiré avec --p-vraie-noyau)")
    p.add_argument("--p-vraie-noyau", type=float, default=0.5)
    p.add_argument("--monde-banque", metavar="FICHIER",
                   help="monde sur banque figée (v7, couche 1) : instances réelles à traits visibles et issues cachées ; "
                        "exclut --monde-noyau")
    p.add_argument("--sans-nul-informe", action="store_true", help="monde sur banque sans le membre « connu »")
    p.add_argument("--sans-urne", action="store_true", help="juge v1 sans le membre « urne » (banque figée)")
    p.add_argument("--multiplicite", choices=("aucune", "e-bh"), default="e-bh",
                   help="v7 : « e-bh » (défaut) = taux de fausses découvertes à α par génération (e-valeurs finales)")
    p.add_argument("--temoins-sans-agent", action="store_true",
                   help="v7 : sur un monde qui dépose les issues, les témoins sont jugés par le noyau seul (gratuit)")
    p.add_argument("--temoins-par-generation", type=int, default=1)
    p.add_argument("--propositions-par-generation", type=int, default=0,
                   help="v7 : fiches demandées au proposeur à chaque génération (monde sur banque ; 0 : aucun)")
    p.add_argument("--modele-proposeur", default="simule-e")
    p.add_argument("--proposeur", choices=("agent", "aleatoire", "mecanique"), default="agent",
                   help="v7 : proposeur enfichable — un agent (modèle), ou une référence gratuite sans modèle : lois tirées "
                        "au hasard au gabarit, ou chercheur mécanique sur la partie de développement")
    p.add_argument("--sans-nul-archive", action="store_true",
                   help="v7 : ne pas mettre les survivantes de l'archive au nul des nouvelles fiches (défaut : les y mettre)")
    p.add_argument("--sans-nul-archive-ajuste", action="store_true",
                   help="v7 : sans les membres ajustés sur l'archive (par défaut, en sélection par pari avec le nul "
                        "d'archive : mise en commun linéaire des survivantes et des parents avec toute loi aveugle, et chaque "
                        "survivante tempérée et inclinée, ajustées aux instants de lecture ; banc de tricheurs, lignes T02 à T05)")
    p.add_argument("--pari-fraction", action="store_true",
                   help="v7 : numérateur de la richesse = mélange sur une grille de fractions de mise (puissance)")
    p.add_argument("--exploration-developpement", action="store_true",
                   help="v7 : phase exploratoire — partie de développement (traits et issues) servie au proposeur")
    p.add_argument("--tranches", type=int, default=1,
                   help="v7 : tranches de la partie d'épreuve, une par génération (exposition adaptative)")
    s = a.add_argument_group("moteur simulé seulement")
    s.add_argument("--monde-simule", help="fichier JSON {\"verites\": {énoncé: vrai|faux}} lu par le seul monde simulé")
    s.add_argument("--taux-tricheurs", type=float, default=0.0, help="part de chaque profil tricheur (test changé, sans calcul)")
    s.add_argument("--verificateur-simule", choices=("honnete", "complaisant"), default="honnete")
    s.add_argument("--p-echec", type=float, default=0.0)
    s.add_argument("--p-redite", type=float, default=0.0)
    s.add_argument("--p-sans-prediction", type=float, default=0.0)
    a.add_argument("--ablation-memoire", action="store_true", help="même population, avec et sans mémoire, et comparaison")
    a.add_argument("--ablation-graines", type=int, default=1, help="nombre de graines appariées pour l'ablation")
    a.add_argument("--experience-critere", action="store_true",
                   help="première expérience : contrôles fatals du critère par pari et duel des trois bras (simulation)")
    e = a.add_argument_group("expérience 1 du pôle : juge v1 (ordre d'exécution secret, urne)")
    e.add_argument("--experience-juge-v1", action="store_true",
                   help="contrôles fatals, artefacts et puissance du juge v1 (simulation, processeur)")
    e.add_argument("--graine-maitresse", type=int,
                   help="graine maîtresse de l'expérience 1 (exigée ; tirée au scellement ; jamais 20261026)")
    e.add_argument("--repetitions", type=int, default=1000, help="répétitions par ligne (au moins 1 000 hors essai)")
    e.add_argument("--essai", action="store_true",
                   help="essai non décisif : moins de répétitions permises, rapport marqué « ESSAI », aucune issue prononcée")
    e.add_argument("--familles", help="essai seulement : familles à exécuter, séparées par des virgules "
                   "(T1a, T6, tricheurs, T3, T9, T1b, T1b-fille, puissance)")
    return a


def construire_adaptateur(args, population, temoins):
    if args.moteur == "claude-sdk":
        from .adaptateurs import (AdaptateurClaudeSDK, AdaptateurMixte, MoteurNonArme, exiger_bac_a_sable,
                                  importer_sdk, verifier_modele_reel)
        if not args.confirmer_moteur_reel:
            raise MoteurNonArme("--moteur claude-sdk exige --confirmer-moteur-reel (dépense réelle, relais local requis)")
        roles_reels = [r for r in (args.roles_reels or "").split(",") if r]
        modeles = {"experimentateur": args.modele_experimentateur, "verificateur": args.modele_verificateur,
                   "recombinaison": args.modele_recombinaison, "synthese": args.modele_synthese}
        if args.propositions_par_generation and args.proposeur == "agent":
            modeles["proposeur"] = args.modele_proposeur
        for role, modele in modeles.items():
            if not roles_reels or role in roles_reels:
                verifier_modele_reel(modele)
        # v11 (contre-lectures C6 et C7) : lectures interdites à l'agent sur le dossier de la course ET sur le dossier de
        # la banque (ses issues d'épreuve, et la vérité d'un monde de démonstration rangée à côté)
        interdits = [os.path.abspath(args.sortie)]
        if args.monde_banque:
            interdits.append(os.path.dirname(os.path.abspath(args.monde_banque)))
        adaptateur = AdaptateurClaudeSDK(args.url_relais, arme=True, interdire_lecture=interdits)
        sdk = importer_sdk()
        # v7, version 5 (défaut 7 du premier lancement réel) : aucun agent réel sans bac à sable actif.
        adaptateur.bac_a_sable = exiger_bac_a_sable(sdk, args.accepter_sans_bac_a_sable, args.motif_sans_bac_a_sable)
        if roles_reels:
            # v7, version 9 : vrais agents pour ces rôles seulement, simulation pour les autres (duel des proposeurs).
            from .simulation import AdaptateurSimule, MondeSimule
            return AdaptateurMixte(adaptateur, AdaptateurSimule(args.graine, MondeSimule(args.graine)), roles_reels)
        return adaptateur
    from .simulation import AdaptateurSimule, MondeSimule
    verites = {t.enonce: t.temoin == "vraie" for t in temoins}
    if args.monde_simule:
        with open(args.monde_simule, encoding="utf-8") as f:
            verites.update(json.load(f)["verites"])
    idees = [f.vers_dict() for f in population]
    return AdaptateurSimule(args.graine, MondeSimule(args.graine, verites),
                            taux_tricheurs={"change_test": args.taux_tricheurs, "sans_calcul": args.taux_tricheurs},
                            verificateur=args.verificateur_simule, p_echec=args.p_echec, p_redite=args.p_redite,
                            p_sans_prediction=args.p_sans_prediction, idees_attirantes=idees)


def principal(argv=None):
    args = analyseur().parse_args(argv)
    try:
        if args.experience_critere:
            from .experience_critere import executer_experience_critere
            executer_experience_critere(args.sortie, args.graine, horodatage(args.horodatage))
            return 0
        if args.experience_juge_v1:
            if args.graine_maitresse is None:
                raise ValueError("--experience-juge-v1 exige --graine-maitresse (la graine par défaut n'est jamais prise)")
            if args.familles and not args.essai:
                raise ValueError("--familles n'est permis qu'avec --essai")
            from .experience_juge_v1 import executer_experience_juge_v1
            familles = tuple(f.strip() for f in args.familles.split(",")) if args.familles else None
            verdicts = executer_experience_juge_v1(args.sortie, args.graine_maitresse, horodatage(args.horodatage),
                                                   args.repetitions, essai=args.essai, familles=familles)
            print(json.dumps({"issue": verdicts["issue"], "socle": verdicts["parties"]["socle"]["issue"],
                              "filles": verdicts["parties"]["filles"]["issue"], "ce_qui_a_cede": verdicts["ce_qui_a_cede"]},
                             ensure_ascii=False))
            return 0
        if not args.population or not args.temoins:
            print("erreur : --population et --temoins sont requis", file=sys.stderr)
            return 2
        population, temoins = charger_fiches(args.population), charger_fiches(args.temoins)
        monde_noyau = None
        if args.monde_banque and args.monde_noyau is not None:
            raise ValueError("--monde-banque et --monde-noyau sont exclusifs")
        if args.monde_banque:
            if args.selection != "pari":
                raise ValueError("--monde-banque suppose --selection pari")
            from .monde_banque import charger_monde_banque
            # v11 (contre-lecture C3) : sur une banque figée, l'héritage de la preuve multiplie des e-valeurs calculées
            # sur les MÊMES issues si deux générations lisent la même partie d'épreuve (classe nulle promue 9,5 % en trois
            # générations contre 4,25 % avec des tranches fraîches). Avec la mémoire et l'héritage, une tranche par
            # génération est exigée.
            if (not args.sans_memoire and args.politique_redite == "heritage" and args.generations > 1
                    and args.tranches < args.generations):
                raise ValueError(f"--tranches {args.tranches} < --generations {args.generations} sur une banque avec "
                                 "héritage de la preuve : chaque génération doit lire une tranche fraîche (donner "
                                 "--tranches ≥ générations, ou --politique-redite refus|rien, ou --sans-memoire)")
            monde_noyau = charger_monde_banque(args.monde_banque, args.graine, nul_informe=not args.sans_nul_informe,
                                               tranches=args.tranches)
        elif args.monde_noyau is not None:
            if args.selection != "pari":
                raise ValueError("--monde-noyau suppose --selection pari")
            from .monde_noyau import charger_monde_noyau
            monde_noyau = charger_monde_noyau(args.monde_noyau or None, args.graine, temoins, args.p_vraie_noyau)
        elif args.moteur == "claude-sdk" and args.selection == "pari":
            raise ValueError("moteur réel en sélection par pari : --monde-noyau est requis (les agents réels ne "
                             "mesurent rien seuls ; option (a) du premier lancement réel)")
        roles_reels = [r for r in (args.roles_reels or "").split(",") if r]
        if roles_reels and args.moteur != "claude-sdk":
            raise ValueError("--roles-reels n'a de sens qu'avec --moteur claude-sdk")
        if roles_reels and "experimentateur" not in roles_reels and monde_noyau is None:
            raise ValueError("--roles-reels sans l'expérimentateur suppose un monde tenu par le noyau (--monde-banque ou "
                             "--monde-noyau) : ailleurs, simuler l'expérimentateur changerait les issues")
        adaptateur = construire_adaptateur(args, population, temoins)
        config = ConfigGeneration(
            modele_experimentateur=args.modele_experimentateur, modele_verificateur=args.modele_verificateur,
            modele_recombinaison=args.modele_recombinaison, modele_synthese=args.modele_synthese,
            selection=args.selection, concurrence=args.concurrence, alpha=args.alpha, graine=args.graine, delta0=args.delta0,
            juge=args.juge, nul_filles=args.nul_filles, taille_plan=args.taille_plan,
            taille_plan_filles=args.taille_plan_filles, tirage_recombinaison=args.tirage_recombinaison,
            instants_filles=args.instants_filles, part_calibrage=args.part_calibrage,
            politique_redite=args.politique_redite, noyau_secret=args.noyau_secret, urne=not args.sans_urne,
            multiplicite=args.multiplicite, temoins_sans_agent=args.temoins_sans_agent,
            propositions_par_generation=args.propositions_par_generation, modele_proposeur=args.modele_proposeur,
            nul_archive=not args.sans_nul_archive, exploration_developpement=args.exploration_developpement,
            pari_fraction=args.pari_fraction, proposeur=args.proposeur,
            nul_archive_ajuste=(not args.sans_nul_archive and not args.sans_nul_archive_ajuste and args.selection == "pari"
                                and args.nul_filles != "v0"),
            budget_generation_usd=args.budget_generation_usd or args.budget_usd / max(1, args.generations)).valider()
        if args.ablation_memoire:
            from .ablation import executer_ablation
            executer_ablation(args, population, temoins, config, lambda: construire_adaptateur(args, population, temoins))
            return 0
        bilan = executer_pole(population, temoins, adaptateur, config, args.generations, args.budget_usd, args.sortie,
                              memoire_active=not args.sans_memoire, horodatage_fourni=args.horodatage,
                              monde_noyau=monde_noyau, temoins_par_generation=args.temoins_par_generation,
                              k_recombinaison=args.k_recombinaison, max_paires=args.max_paires)
        print(json.dumps({"generations": bilan["generations_executees"], "arret": bilan["arret"],
                          "depense_totale": bilan["depense_totale"], "qualite": bilan["qualite_cumulee"]},
                         ensure_ascii=False))
        return 0
    except Exception as e:  # noqa: BLE001 — sortie lisible, code non nul
        from .adaptateurs import BacASableInactif, MoteurIndisponible, MoteurNonArme
        from .relais import CleDansEnvironnement, RelaisInvalide
        connues = (MoteurIndisponible, MoteurNonArme, BacASableInactif, CleDansEnvironnement, RelaisInvalide,
                   SortieNonVide, ValueError, OSError)
        if isinstance(e, connues):
            print(f"erreur : {type(e).__name__} : {e}", file=sys.stderr)
            return 2
        raise
