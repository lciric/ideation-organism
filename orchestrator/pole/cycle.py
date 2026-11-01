"""Une génération : (a) gel, (b) expérimentateurs en parallèle, (c) vérificateurs d'un autre modèle, (d) sélection,
(e) mesure de qualité sur les témoins.

Deux modes de sélection :
- « seuil » (brief) : l'expérimentateur rend {verdict, statistique, seuil, code, empreinte_fiche} ; le vérificateur rejoue ;
- « pari » (second ajout) : l'expérimentateur ne rend que des tirages frais liés à l'engagement gelé ; le vérificateur
  rejoue leur production ; la richesse et la promotion sont calculées ici, par l'orchestrateur (`selection_pari`).

Version 0.3.0 (`orchestrateur-pole-v3`) : en sélection par pari, juge v1 par défaut (`juge="v1"` : ordre d'exécution secret
tiré par le noyau après le gel, écrit pour l'expérimentateur dans `ordre-execution.json`, recalculé à l'évaluation ;
urne dans 𝓛), adopté par l'expérience 1 pour les fiches sans parents ; nul des filles v2 par défaut (`nul_filles="v2"` :
membres ajustés, lecture aux instants fixés), adopté par l'expérience 2. La graine du noyau ne quitte jamais
l'orchestrateur (en simulation, elle dérive de la graine du pôle). `juge="v0"` et `nul_filles="v0"` rendent v0.

Version 0.6.0 (`orchestrateur-pole-v6`) : monde tenu par le noyau (`monde_noyau`, option (a) du premier lancement réel) :
après le gel, le noyau dépose les issues du monde caché dans `mesures.json` (ordre imposé) ; l'agent les range par un code
rejouable ; le noyau compare les issues déclarées aux issues déposées avant même d'appeler le vérificateur.
"""

import concurrent.futures
import json
import math
import os
import random
import shutil
import threading
from dataclasses import asdict, dataclass

from . import selection_pari as sp
from .caviardage import caviarder
from .fiche import STATUTS, FicheModifieeApresGel, ecrire_fiche_gelee, verifier_fichier_fiche
from .outils import (chemin_dans, dossier_traces, ecrire_json_scelle, ecrire_scelle, extraire_bloc_json,
                     graine_derivee, json_canonique, nombre_fini, sha256_fichier)

VERDICTS = ("survit", "eliminee", "indecise")
# Fichiers de l'expérience jamais copiés dans le dossier du vérificateur ; **leurs compagnons `.sha256` non plus** (v7,
# version 5, défaut 5 du premier lancement réel : des empreintes orphelines égaraient le vérificateur).
EXCLUS_DU_REJEU = {"fiche.json", "engagement.json", "resultat.json", "tirages.json", "reponse.txt", "consigne.txt"}
PHRASE_REPONSE = ("Ta réponse est ton dernier message : l'orchestrateur l'archive lui-même, hors de ton dossier ; "
                  "n'écris aucun fichier de réponse.")


@dataclass
class ConfigGeneration:
    modele_experimentateur: str = "simule-a"
    modele_verificateur: str = "simule-b"
    modele_recombinaison: str = "simule-c"
    modele_synthese: str = "simule-d"
    selection: str = "seuil"
    concurrence: int = 4
    budget_generation_usd: float = 10.0
    plafond_experimentateur_usd: float = 1.0
    plafond_verificateur_usd: float = 0.5
    plafond_recombinaison_usd: float = 0.3
    plafond_synthese_usd: float = 0.2
    max_tours_experimentateur: int = 40
    max_tours_verificateur: int = 30
    max_tours_recombinaison: int = 10
    max_tours_synthese: int = 5
    alpha: float = 0.05
    taille_plan: int = 120
    reservoir: int = 600
    lecture: str = "continu"
    delta0: float = 0.01
    part_calibrage: int = 40
    graine: int = 20261026
    taille_max_rejeu_octets: int = 20_000_000
    juge: str = "v1"
    nul_filles: str = "v2"
    instants_filles: int = 8
    tirage_recombinaison: str = "stratifie"
    taille_plan_filles: int = 300
    politique_redite: str = "heritage"
    noyau_secret: bool = False
    urne: bool = True  # v7 : juge v1 sans le membre « urne » (banque figée : pas de dérive dans le temps)
    # v7 : règle de multiplicité, « aucune » (garantie par fiche : la sémantique des essais du juge) ou « e-bh » (taux de
    # fausses découvertes à α par génération ; **défaut de la ligne de commande et des démonstrations**, décision de
    # Lazar du 27 octobre, 15:11 heure de Paris).
    multiplicite: str = "aucune"
    temoins_sans_agent: bool = False  # v7 : sur un monde qui dépose les issues, les témoins sont jugés par le noyau seul
    propositions_par_generation: int = 0  # v7 : fiches demandées au proposeur à chaque génération (0 : aucun proposeur)
    nul_archive: bool = False  # v7 : lois des survivantes de l'archive et leurs mélanges aveugles au nul de toute fiche
    # v7, version 6 (banc de tricheurs, lignes T02 à T05) : membres **ajustés** sur l'archive — mise en commun linéaire
    # des survivantes (et des parents d'une fille) avec toute loi aveugle fixe, et chaque survivante tempérée et inclinée,
    # au maximum de vraisemblance aux instants de lecture (nul des filles v2 étendu). Lecture aux instants pour toute fiche.
    nul_archive_ajuste: bool = False
    # v7, version 7 : proposeur enfichable — « agent » (un modèle, par l'adaptateur), « aleatoire » ou « mecanique »
    # (références gratuites, sans modèle ; synthèse du collisionneur « proposeur enfichable », option 3).
    proposeur: str = "agent"
    exploration_developpement: bool = False  # v7, pièce 4 bis : partie de développement (traits et issues) au proposeur
    pari_fraction: bool = False  # v7 : numérateur = mélange sur une grille de fractions de mise (levier de puissance valide)
    modele_proposeur: str = "simule-e"
    plafond_proposeur_usd: float = 0.5
    max_tours_proposeur: int = 15

    def valider(self):
        if self.modele_verificateur == self.modele_experimentateur:
            raise ValueError("le vérificateur doit être d'un autre modèle que l'expérimentateur")
        if self.selection not in ("seuil", "pari"):
            raise ValueError("selection : « seuil » ou « pari »")
        if not (isinstance(self.concurrence, int) and self.concurrence >= 1):
            raise ValueError("concurrence : entier ≥ 1")
        for nom in ("budget_generation_usd", "plafond_experimentateur_usd", "plafond_verificateur_usd",
                    "plafond_recombinaison_usd", "plafond_synthese_usd", "plafond_proposeur_usd"):
            if not (nombre_fini(getattr(self, nom)) and getattr(self, nom) > 0):
                raise ValueError(f"{nom} : nombre fini strictement positif")
        if not (0 < self.alpha < 1):
            raise ValueError("alpha dans ]0 ; 1[")
        if self.juge not in ("v0", "v1"):
            raise ValueError("juge : « v0 » ou « v1 »")
        if self.nul_filles not in ("v0", "v2", "v2_souple"):
            raise ValueError("nul_filles : « v0 », « v2 » ou « v2_souple »")
        if self.nul_filles != "v0" and self.juge != "v1":
            raise ValueError("le nul des filles v2 suppose le juge v1 (ordre secret, urne)")
        if not (isinstance(self.instants_filles, int) and 1 <= self.instants_filles <= self.taille_plan):
            raise ValueError("instants_filles : entier dans [1 ; taille_plan]")
        if self.tirage_recombinaison not in ("stratifie", "stratifie_marchepieds", "noyau_corrige"):
            raise ValueError("tirage_recombinaison : « stratifie » (R-527), « stratifie_marchepieds » (v4) ou "
                             "« noyau_corrige » (v0)")
        if not (isinstance(self.taille_plan_filles, int) and self.instants_filles <= self.taille_plan_filles
                and self.taille_plan_filles + self.part_calibrage <= self.reservoir):
            raise ValueError("taille_plan_filles : entier ≥ instants_filles, et taille_plan_filles + part_calibrage ≤ reservoir")
        if self.politique_redite not in ("heritage", "refus", "rien"):
            raise ValueError("politique_redite : « heritage », « refus » ou « rien »")
        if not isinstance(self.noyau_secret, bool):
            raise ValueError("noyau_secret : vrai ou faux")
        if not isinstance(self.urne, bool):
            raise ValueError("urne : vrai ou faux")
        if not self.urne and self.juge != "v1":
            raise ValueError("urne=False : seulement avec le juge v1 (l'ordre secret reste, l'urne seule est retirée)")
        if self.multiplicite not in ("aucune", "e-bh"):
            raise ValueError("multiplicite : « aucune » ou « e-bh »")
        if not isinstance(self.temoins_sans_agent, bool):
            raise ValueError("temoins_sans_agent : vrai ou faux")
        if not (isinstance(self.propositions_par_generation, int) and 0 <= self.propositions_par_generation <= 40):
            raise ValueError("propositions_par_generation : entier dans [0 ; 40]")
        if self.propositions_par_generation and self.selection != "pari":
            raise ValueError("le proposeur suppose la sélection par pari")
        if not isinstance(self.nul_archive, bool):
            raise ValueError("nul_archive : vrai ou faux")
        if self.proposeur not in ("agent", "aleatoire", "mecanique"):
            raise ValueError("proposeur : « agent », « aleatoire » ou « mecanique »")
        if self.proposeur == "mecanique" and not self.exploration_developpement:
            raise ValueError("proposeur mécanique : exploration_developpement requise (il lit la partie de développement)")
        if not isinstance(self.nul_archive_ajuste, bool) or (self.nul_archive_ajuste and (
                not self.nul_archive or self.nul_filles == "v0" or self.selection != "pari")):
            raise ValueError("nul_archive_ajuste : vrai ou faux, et seulement avec nul_archive, la sélection par pari et "
                             "un nul des filles ajusté (pas v0)")
        if not isinstance(self.exploration_developpement, bool):
            raise ValueError("exploration_developpement : vrai ou faux")
        if not isinstance(self.pari_fraction, bool):
            raise ValueError("pari_fraction : vrai ou faux")
        return self


class Budget:
    """Plafond de dépense d'une génération : réservation avant chaque lancement, règlement au coût déclaré."""

    def __init__(self, plafond):
        self.plafond, self.engage, self.depense, self.depassements = float(plafond), 0.0, 0.0, 0.0
        self._verrou = threading.Lock()

    def reserver(self, montant):
        with self._verrou:
            if self.depense + self.engage + montant > self.plafond + 1e-9:
                return False
            self.engage += montant
            return True

    def regler(self, reserve, cout):
        with self._verrou:
            self.engage -= reserve
            self.depense += cout
            self.depassements += max(0.0, cout - reserve)

    def etat(self):
        return {"plafond": self.plafond, "depense": round(self.depense, 6), "restant": round(self.plafond - self.depense, 6),
                "depassements_declares": round(self.depassements, 6)}


def suit_le_seuil(verdict, statistique, seuil, signe):
    passe = statistique >= seuil if signe == "+" else statistique <= seuil
    return verdict == ("survit" if passe else "eliminee")


def consigne_experimentateur(fiche, empreinte, texte_memoire, mode, empreinte_engagement=None, ordre_secret=False,
                             mesures_du_noyau=False):
    morceaux = [
        "Tu es expérimentateur. Le test ci-dessous est gelé : son empreinte SHA-256 est " + empreinte + ".",
        "La fiche est dans `fiche.json` (son SHA-256 doit rester égal à l'empreinte). Ne la modifie jamais.",
        "Fiche publique :\n" + json.dumps(fiche.vue_publique(), ensure_ascii=False, indent=1, sort_keys=True),
    ]
    if mode == "seuil":
        morceaux.append("Écris le code de l'expérience dans ce dossier, exécute-le, et termine ta réponse par un bloc "
                        "```json {\"verdict\": \"survit\"|\"eliminee\"|\"indecise\", \"statistique\": <nombre>, "
                        "\"seuil\": <le seuil gelé>, \"code\": \"<chemin relatif>\", \"empreinte_fiche\": \"<sha256>\"}```.")
    else:
        morceaux.append(f"Sélection par pari : l'engagement gelé (`engagement.json`, empreinte {empreinte_engagement}) fixe "
                        "la loi prédictive, la bibliothèque nulle et le plan d'instances. Produis les issues aux instances "
                        "du plan par un code rejouable, écris-les dans `tirages.json` ({empreinte_engagement, issues}) et "
                        "termine par un bloc ```json {\"tirages\": \"tirages.json\", \"code\": \"<chemin>\", "
                        "\"empreinte_fiche\": \"<sha256>\", \"empreinte_engagement\": \"<sha256>\"}```. Tu ne calcules "
                        "aucune richesse : l'orchestrateur la calcule.")
        if ordre_secret:
            morceaux.append("Ordre d'exécution imposé par le noyau (`ordre-execution.json`, écrit après le gel) : au temps s, "
                            "traite l'instance d'indice ordre[s] du plan ; range chaque issue à l'indice de son instance ; "
                            "écris aussi dans `tirages.json` le plan (« ordre_secret ») et l'empreinte de l'ordre.")
        if mesures_du_noyau:
            morceaux.append("Monde tenu par le noyau : tu ne mesures rien toi-même (ni réseau ni clé). Les issues du "
                            "monde aux instances du plan, déjà produites dans l'ordre imposé, sont déposées dans "
                            "`mesures.json` ({empreinte_engagement, issues, plan_execution, empreinte_ordre}). Écris un "
                            "code rejouable qui vérifie que `mesures.json` est lié à l'engagement gelé (même empreinte) "
                            "et range ces issues telles quelles dans `tirages.json` (mêmes champs). Toute issue "
                            "différente de celles déposées sera rejetée par le noyau.")
    morceaux.append(PHRASE_REPONSE)
    if texte_memoire:
        morceaux.append("Mémoire du pôle (à titre d'aide, le test gelé prime) :\n" + texte_memoire)
    return "\n\n".join(morceaux)


def consigne_verificateur(empreinte, declaration, mode):
    if mode == "seuil":
        quoi = "rejoue le code déclaré et compare la statistique et le verdict au seuil gelé"
        pari = ""
    else:
        quoi = "rejoue le code déclaré et compare les tirages produits à `tirages-declares.json`"
        # v7, version 5 (défaut 5 du premier lancement réel) : deux vérificateurs ont refusé de confirmer faute d'un
        # « verdict chiffré » que, par construction, seul le noyau calcule, après eux.
        pari = (" Sélection par pari : il n'y a **aucun verdict chiffré à confirmer** ; la richesse est calculée par le "
                "noyau après ta confirmation. Tu confirmes seulement que le rejeu reproduit exactement les tirages "
                "déclarés et que le test exécuté est le test gelé. Rejoue dans ce dossier (tu ne peux pas écrire "
                "ailleurs) et garde du budget pour le rejeu.")
    return ("Tu es vérificateur, d'un autre modèle que l'expérimentateur. Le dossier contient la fiche gelée "
            f"(`fiche.json`, empreinte {empreinte}), le code et les données de l'expérience, et la déclaration "
            f"(`declaration.json`) : {json.dumps(declaration, ensure_ascii=False, sort_keys=True)}. Tu {quoi}, tu vérifies "
            "que le test exécuté est le test gelé et tu cherches les raccourcis." + pari + " " + PHRASE_REPONSE
            + " Termine par un bloc ```json {\"confirme\": true|false, \"test_conforme\": true|false, \"motif\": \"...\"}```.")


def _exclu_du_rejeu(relatif):
    base = relatif[:-len(".sha256")] if relatif.endswith(".sha256") else relatif
    return base in EXCLUS_DU_REJEU


def _copier_pour_rejeu(source, cible, limite):
    os.makedirs(cible, exist_ok=False)
    total = 0
    for racine, _, fichiers in os.walk(source):
        for nom in fichiers:
            relatif = os.path.relpath(os.path.join(racine, nom), source)
            if _exclu_du_rejeu(relatif) or os.path.islink(os.path.join(racine, nom)):
                continue
            total += os.path.getsize(os.path.join(racine, nom))
            if total > limite:
                raise OverflowError("artefacts trop volumineux pour le rejeu")
            os.makedirs(os.path.dirname(os.path.join(cible, relatif)), exist_ok=True)
            shutil.copyfile(os.path.join(racine, nom), os.path.join(cible, relatif))


def membres_de_l_archive(fiche, memoire, ajuste=False, lois_parents=None):
    """v7 (« go » de Lazar du 27 octobre, 15:27) : le nul des filles étendu à la mémoire. Pour une fiche non témoin, chaque
    survivante de l'archive de même espace (moniteur, nombre d'issues, dimension), hors elle-même et ses parents, entre au
    nul avec sa loi seule et ses mélanges à la loi uniforme (grille) : une fiche nouvelle doit prédire plus que ce que le
    pôle a déjà trouvé. Agrandir le nul ne fait que diminuer la richesse : la garantie reste valide."""
    if memoire is None or not getattr(memoire, "active", False):
        return []
    espace = fiche.espace_instances or {}
    k, d, moniteur = int(espace.get("nombre_issues", 3)), int(espace.get("dimension", 2)), espace.get("moniteur")
    membres = []
    for ident, e in sorted(memoire.index.items()):
        if e.get("statut") != "survit" or e.get("temoin") or ident == fiche.identifiant or ident in (fiche.parents or []):
            continue
        loi, esp = e.get("loi_predictive"), e.get("espace_instances") or {}
        if not loi or int(esp.get("nombre_issues", 3)) != k or int(esp.get("dimension", 2)) != d or esp.get("moniteur") != moniteur:
            continue
        membres.append({"nom": f"archive:{ident}", "type": "loi", "loi": loi})
        membres.append({"nom": f"archive_couvert:{ident}", "type": "melange_lois",
                        "lois": [loi, {"type": "fixe", "probas": [1.0] * k}], "grille": list(sp.GRILLE_MELANGE)})
        if ajuste:
            membres.append({"nom": f"ajuste_log:archive:{ident}", "type": "ajuste_log", "lois": [loi]})
    if ajuste:
        lois = [membre["loi"] for membre in membres if membre["type"] == "loi"]
        lois = [lois_parents[n] for n in sorted(lois_parents or {})] + lois
        if lois:
            # Mise en commun linéaire de toutes les lois connues (parents et survivantes) avec toute loi aveugle fixe :
            # ferme la copie cachée (T02), la survivante plus une loi aveugle (T03), le mélange de survivantes (T04).
            membres.append({"nom": "ajuste_lineaire:archive", "type": "ajuste_lineaire", "lois": lois})
    return membres


def a_des_membres_ajustes(membres):
    return any(m.get("type") in ("ajuste_lineaire", "ajuste_log") for m in membres or ())


def instants_reguliers(n, nombre):
    """`nombre` instants de lecture régulièrement espacés dans [1 ; n], le dernier égal à n."""
    return sorted({max(1, round(n * (i + 1) / nombre)) for i in range(nombre)} | {n})


def preparer_engagement(fiche, config, lois_parents=None, reservoir=None, membres_supplementaires=None, moniteur=None):
    """Plan d'instances choisi ex ante par le sélecteur mécanique, bibliothèque nulle, seuil : tout est gelé ici.

    Fiche fille (deux parents à loi connue) : nul augmenté des parents et de leurs enveloppes, part de calibrage en tête
    du plan, marge 2·delta0 sur le gain moyen de score logarithmique (troisième ajout au brief) ; sous le nul des filles
    v2, membres ajustés et instants de lecture sous l'empreinte. Juge v1 : ordre d'exécution secret, urne dans 𝓛.
    v7 : `reservoir` fourni par un monde sur banque (instances réelles, traits seulement) à la place du tirage gaussien ;
    `membres_supplementaires` (nul informé) ajoutés à la bibliothèque ; `moniteur` déclaré dans l'engagement (sous son
    empreinte) ; `config.urne=False` retire le membre « urne » (l'ordre secret reste).
    """
    espace = fiche.espace_instances or {}
    k, d = int(espace.get("nombre_issues", 3)), int(espace.get("dimension", 2))
    rng = random.Random(graine_derivee(config.graine, "plan", fiche.empreinte()))
    if reservoir is None:
        reservoir = sp.tirer_instances(rng, config.reservoir, d, int(espace.get("sous_populations", 2)))
    else:
        reservoir = [dict(i) for i in reservoir]
        rng.shuffle(reservoir)
    v1 = config.juge == "v1"
    if v1 and not config.urne:
        # v7, version 11 (contre-lecture du socle, C4) : sans le membre « urne », une loi qui lit l'historique des
        # issues (« sans_remise » avec la composition exacte de l'épreuve : log W de 3,8 à 4,2 sans aucun trait ;
        # « moyenne_glissante ») n'est plus bornée par la bibliothèque : refusée au gel.
        lisant = sp.types_de_la_loi(fiche.loi_predictive) & set(sp.TYPES_LISANT_L_HISTORIQUE)
        if lisant:
            raise sp.LoiInvalide("sans le membre « urne » (banque figée), une loi qui lit l'historique des issues "
                                 f"({', '.join(sorted(lisant))}) n'est pas jugeable : la composition de l'épreuve "
                                 "la ferait promouvoir sans aucun trait")
    standard = sp.BIBLIOTHEQUE_STANDARD_V1 if (v1 and config.urne) else sp.BIBLIOTHEQUE_STANDARD
    standard = tuple(standard) + tuple(membres_supplementaires or ())
    plan_execution = "ordre_secret" if v1 else "ordre_naturel"
    if lois_parents:
        part = min(config.part_calibrage, max(0, len(reservoir) // 4)) if len(reservoir) < config.taille_plan_filles + config.part_calibrage else config.part_calibrage
        n_filles = min(getattr(config, "taille_plan_filles", config.taille_plan), len(reservoir) - part)
        plan = sp.selection_divergence(fiche.loi_predictive, reservoir, [1.0 / k] * k, n_filles + part)
        rng.shuffle(plan)
        bibliotheque = sp.bibliotheque_fille(lois_parents, d, standard, nombre_issues=k)
        if config.nul_filles != "v0":
            from . import nul_filles_v2 as nf  # numpy, importé seulement ici
            bibliotheque = bibliotheque + nf.membres_de_variante(config.nul_filles, lois_parents)
            engagement = nf.construire_engagement_v2(fiche.identifiant, fiche.loi_predictive, plan, k, config.alpha,
                                                     bibliotheque, part, config.delta0,
                                                     instants_reguliers(n_filles, min(config.instants_filles, n_filles)),
                                                     plan_execution)
            engagement["empreinte_fiche"] = fiche.empreinte()
        else:
            engagement = sp.construire_engagement(fiche.identifiant, fiche.loi_predictive, plan, k, config.alpha, bibliotheque,
                                                  config.lecture, fiche.empreinte(), part_calibrage=part,
                                                  delta0=config.delta0, plan_execution=plan_execution)
    else:
        plan = sp.selection_divergence(fiche.loi_predictive, reservoir, [1.0 / k] * k, min(config.taille_plan, len(reservoir)))
        if a_des_membres_ajustes(membres_supplementaires):
            # v7, version 6 : membres ajustés sur l'archive → lecture aux instants fixés (évaluateur du nul v2)
            from . import nul_filles_v2 as nf
            n = len(plan)
            engagement = nf.construire_engagement_v2(fiche.identifiant, fiche.loi_predictive, plan, k, config.alpha,
                                                     standard, 0, None, instants_reguliers(n, min(config.instants_filles, n)),
                                                     plan_execution)
            engagement["empreinte_fiche"] = fiche.empreinte()
        else:
            engagement = sp.construire_engagement(fiche.identifiant, fiche.loi_predictive, plan, k, config.alpha,
                                                  standard, config.lecture, fiche.empreinte(), plan_execution=plan_execution)
    if moniteur is not None:
        engagement["moniteur"] = moniteur
    if getattr(config, "pari_fraction", False):
        engagement["fractions"] = list(sp.GRILLE_FRACTIONS)  # sous l'empreinte : déclaré avant le gel
    return sp.geler_engagement(engagement)


class Generation:
    def __init__(self, numero, adaptateur, config, racine, registre_gel, budget, memoire=None, lois_connues=None,
                 monde_noyau=None, depots=None):
        self.numero, self.adaptateur, self.config, self.racine = numero, adaptateur, config.valider(), racine
        self.registre_gel, self.budget, self.memoire = registre_gel, budget, memoire
        self.lois_connues = lois_connues or {}
        self.dossier = os.path.join(racine, "archive", "generations", f"generation-{numero:02d}")
        self.engagements = {}
        # v6 : monde tenu par le noyau (sélection par pari seulement) ; les mesures déposées restent en mémoire pour la
        # comparaison avec les issues déclarées. Jamais le monde lui-même dans un dossier d'agent.
        if monde_noyau is not None and config.selection != "pari":
            raise ValueError("le monde tenu par le noyau suppose la sélection par pari")
        self.monde_noyau, self.mesures_noyau = monde_noyau, {}
        # v6 : dépôt unique par engagement, partagé entre les générations (dictionnaire tenu par la boucle du pôle) :
        # une fiche rejouée (indécise, hors budget) reçoit le même ordre secret et, sous le monde du noyau, les mêmes
        # issues que la première fois. Sans cela, un agent qui voit des issues défavorables pourrait planter pour obtenir
        # un tirage neuf à la génération suivante (censure stratégique, contre-lecture d'aptitude, faille C4).
        self.depots = depots if depots is not None else {}
        # Graine du noyau (ordre d'exécution secret) : jamais écrite dans un dossier d'agent. En simulation, elle dérive de
        # la graine du pôle (reproductible) ; avec `noyau_secret` (exécution réelle, v5), elle est tirée par `secrets`,
        # tenue en mémoire, et n'est écrite qu'après les évaluations de la génération, sous `noyau/` à la racine du pôle.
        if config.noyau_secret:
            import secrets
            self.graine_noyau = secrets.randbits(128)
        else:
            self.graine_noyau = graine_derivee(config.graine, "noyau", numero)

    # (a) gel ---------------------------------------------------------------------------------------------------
    def geler(self, fiche):
        """Rend None si la fiche est gelée et prête, sinon le motif du refus (statut déjà posé)."""
        gele = None
        try:
            if self.config.selection == "pari":
                self._controler_pari(fiche)
                # v7 : l'engagement (plan, bibliothèque, moniteur) est préparé avant le gel ; un monde sur banque peut le
                # refuser (moniteur inconnu, nombre d'issues faux, aucune instance d'épreuve) : la fiche est refusée
                # sans qu'aucun dossier ne soit créé.
                parents = {p: self.lois_connues[p] for p in fiche.parents if p in self.lois_connues}
                monde = self.monde_noyau
                supplementaires = list(monde.membres_informes(fiche)) if hasattr(monde, "membres_informes") else []
                if self.config.nul_archive and fiche.temoin is None:
                    supplementaires += membres_de_l_archive(fiche, self.memoire, self.config.nul_archive_ajuste,
                                                            parents if len(parents) == 2 else None)
                gele = preparer_engagement(
                    fiche, self.config, parents if len(parents) == 2 else None,
                    reservoir=monde.reservoir(fiche, self.numero) if hasattr(monde, "reservoir") else None,
                    membres_supplementaires=supplementaires or None,
                    moniteur=monde.moniteur_de(fiche) if hasattr(monde, "moniteur_de") else None)
            empreinte = self.registre_gel.geler(fiche)
        except FicheModifieeApresGel as e:
            fiche.statut = "refusee (modifiee apres gel)"
            return str(e)
        except (ValueError, sp.LoiInvalide) as e:
            fiche.statut = "refusee (invalide)"
            return str(e)
        dossier_exp = os.path.join(self.dossier, fiche.identifiant, "experience")
        os.makedirs(dossier_exp, exist_ok=False)
        ecrire_fiche_gelee(fiche, dossier_exp)
        ecrire_json_scelle(os.path.join(self.racine, "archive", "fiches", fiche.identifiant,
                                        f"gel-generation-{self.numero:02d}.json"),
                           dict(fiche.vue_complete_gelee(), empreinte=empreinte, empreinte_complete=fiche.empreinte_complete()))
        if self.config.selection == "pari":
            self.engagements[fiche.identifiant] = gele
            ecrire_scelle(os.path.join(dossier_exp, "engagement.json"), json_canonique(gele.engagement))
            depot = self.depots.setdefault(gele.empreinte, {"graine_noyau": self.graine_noyau, "generation": self.numero})
            if sp.plan_execution_de(gele.engagement) == "ordre_secret":
                ordre = sp.ordre_execution(depot["graine_noyau"], gele.empreinte, len(gele.engagement["instances"]))
                ecrire_json_scelle(os.path.join(dossier_exp, "ordre-execution.json"),
                                   {"empreinte_engagement": gele.empreinte, "ordre": ordre})
            if self.monde_noyau is not None:  # v6 : issues du monde caché déposées après le gel, dans l'ordre imposé
                if "mesures" not in depot:
                    depot["mesures"] = self.monde_noyau.mesures(fiche.enonce, gele, depot["graine_noyau"],
                                                                depot["generation"])
                self.mesures_noyau[fiche.identifiant] = depot["mesures"]
                ecrire_json_scelle(os.path.join(dossier_exp, "mesures.json"), depot["mesures"])
        fiche.statut = "gelee"
        return None

    def _controler_pari(self, fiche):
        if fiche.loi_predictive is None:
            raise ValueError("sélection par pari : la fiche doit engager une loi prédictive")
        if abs(fiche.severite_attendue - self.config.alpha) > 1e-12:
            raise ValueError(f"sélection par pari : la sévérité est l'α du pôle ({self.config.alpha})")
        espace = fiche.espace_instances or {}
        sp.valider_loi(fiche.loi_predictive, int(espace.get("nombre_issues", 3)), int(espace.get("dimension", 2)))

    # (b) et (c) : un expérimentateur puis un vérificateur par fiche ---------------------------------------------
    @staticmethod
    def issue_vierge(fiche):
        return {"identifiant": fiche.identifiant, "famille_source": fiche.famille_source(), "desaccord": False,
                "couts": {}, "verdict_declare": None, "code": {}}

    def traiter(self, fiche, issue=None):
        """`issue` (facultatif) est rempli en place : les coûts réglés avant une erreur de l'orchestrateur y restent
        (v7, version 5, défaut 4 du premier lancement réel : sinon la réservation était libérée deux fois)."""
        issue = self.issue_vierge(fiche) if issue is None else issue
        try:
            self.registre_gel.verifier(fiche)
        except FicheModifieeApresGel as e:
            return dict(issue, verdict_final="refusee (modifiee apres gel)", motif=str(e))
        empreinte = self.registre_gel.empreinte(fiche.identifiant)
        dossier_exp = os.path.join(self.dossier, fiche.identifiant, "experience")
        traces_exp = dossier_traces(dossier_exp)
        gele = self.engagements.get(fiche.identifiant)
        texte_memoire = self.memoire.texte_consigne("experimentateur") if self.memoire else ""
        consigne = consigne_experimentateur(fiche, empreinte, texte_memoire, self.config.selection,
                                            gele.empreinte if gele else None,
                                            ordre_secret=bool(gele) and sp.plan_execution_de(gele.engagement) == "ordre_secret",
                                            mesures_du_noyau=fiche.identifiant in self.mesures_noyau)
        ecrire_scelle(os.path.join(traces_exp, "consigne.txt"), consigne)
        plafond_exp = min(fiche.cout_borne, self.config.plafond_experimentateur_usd)
        res = self.adaptateur.lancer("experimentateur", consigne, dossier_exp, plafond_exp,
                                     self.config.max_tours_experimentateur, modele=self.config.modele_experimentateur)
        self.budget.regler(self._reserve_role("experimentateur", plafond_exp), res.cout_declare_usd)
        issue["couts"]["experimentateur"] = res.cout_declare_usd
        ecrire_scelle(os.path.join(traces_exp, "reponse.txt"), caviarder(res.texte_final)[0])
        cle = "verdict" if self.config.selection == "seuil" else "tirages"
        bloc = extraire_bloc_json(res.texte_final, cle)
        if res.statut != "ok" or bloc is None:
            return dict(issue, verdict_final="indecise", motif="exécution en échec ou bloc JSON absent")
        issue["verdict_declare"] = bloc.get("verdict", "tirages") if cle == "verdict" else "tirages"
        if bloc.get("empreinte_fiche") != empreinte or not verifier_fichier_fiche(os.path.join(dossier_exp, "fiche.json"), empreinte):
            return dict(issue, verdict_final="rejetee (test change)", motif="empreinte de fiche différente de l'empreinte gelée")
        if gele and (bloc.get("empreinte_engagement") != gele.empreinte
                     or sha256_fichier(os.path.join(dossier_exp, "engagement.json")) != gele.empreinte):
            return dict(issue, verdict_final="rejetee (test change)", motif="engagement différent de l'engagement gelé")
        if cle == "verdict":
            if bloc.get("seuil") != fiche.seuil:
                return dict(issue, verdict_final="rejetee (test change)", motif="seuil déclaré différent du seuil gelé")
            if bloc.get("verdict") not in VERDICTS or not nombre_fini(bloc.get("statistique")):
                return dict(issue, verdict_final="indecise", motif="bloc JSON incomplet")
            if bloc["verdict"] != "indecise" and not suit_le_seuil(bloc["verdict"], bloc["statistique"], fiche.seuil,
                                                                  fiche.prediction["signe"]):
                return dict(issue, verdict_final="indecise", motif="verdict incohérent avec la statistique et le seuil")
        code = bloc.get("code")
        if not isinstance(code, str) or not chemin_dans(dossier_exp, code) or not os.path.isfile(os.path.join(dossier_exp, code)):
            return dict(issue, verdict_final="indecise", motif="code introuvable dans le dossier de l'expérience")
        issue["code"] = {"chemin": os.path.relpath(os.path.join(dossier_exp, code), self.racine),
                         "sha256": sha256_fichier(os.path.join(dossier_exp, code))}
        tirages = None
        if gele:
            chemin_t = bloc.get("tirages")
            if not isinstance(chemin_t, str) or not chemin_dans(dossier_exp, chemin_t) or not os.path.isfile(os.path.join(dossier_exp, chemin_t)):
                return dict(issue, verdict_final="indecise", motif="tirages introuvables")
            with open(os.path.join(dossier_exp, chemin_t), encoding="utf-8") as f:
                tirages = json.load(f)
            if fiche.identifiant in self.mesures_noyau:  # v6 : les issues déclarées sont celles que le noyau a déposées
                from .monde_noyau import issues_conformes
                conformes, motif = issues_conformes(self.mesures_noyau[fiche.identifiant], tirages)
                issue["mesures_du_noyau"] = {"conformes": conformes, "motif": motif}
                if not conformes:
                    return dict(issue, verdict_final="rejetee (test change)", motif="monde du noyau : " + motif)
        return self._verifier(fiche, issue, bloc, dossier_exp, empreinte, gele, tirages)

    def _verifier(self, fiche, issue, bloc, dossier_exp, empreinte, gele, tirages):
        dossier_v = os.path.join(self.dossier, fiche.identifiant, "verification")
        try:
            _copier_pour_rejeu(dossier_exp, dossier_v, self.config.taille_max_rejeu_octets)
        except OverflowError as e:
            return dict(issue, verdict_final="indecise", motif=str(e))
        ecrire_fiche_gelee(fiche, dossier_v)
        if gele:
            ecrire_scelle(os.path.join(dossier_v, "engagement.json"), json_canonique(gele.engagement))
            ecrire_scelle(os.path.join(dossier_v, "tirages-declares.json"), json_canonique(tirages))
        ecrire_scelle(os.path.join(dossier_v, "declaration.json"), json_canonique(bloc))
        consigne = consigne_verificateur(empreinte, bloc, self.config.selection)
        traces_v = dossier_traces(dossier_v)
        ecrire_scelle(os.path.join(traces_v, "consigne.txt"), consigne)
        res = self.adaptateur.lancer("verificateur", consigne, dossier_v, self.config.plafond_verificateur_usd,
                                     self.config.max_tours_verificateur, modele=self.config.modele_verificateur)
        self.budget.regler(self._reserve_role("verificateur", self.config.plafond_verificateur_usd), res.cout_declare_usd)
        issue["couts"]["verificateur"] = res.cout_declare_usd
        ecrire_scelle(os.path.join(traces_v, "reponse.txt"), caviarder(res.texte_final)[0])
        bloc_v = extraire_bloc_json(res.texte_final, "confirme")
        issue["verification"] = bloc_v
        if bloc_v is None:
            return dict(issue, verdict_final="indecise", desaccord=True, motif="vérification sans conclusion")
        if bloc_v.get("test_conforme") is False:
            return dict(issue, verdict_final="rejetee (test change)", desaccord=True,
                        motif="vérificateur : test exécuté différent du test gelé")
        if bloc_v.get("confirme") is not True:
            return dict(issue, verdict_final="indecise", desaccord=True,
                        motif="verdict non confirmé par le vérificateur : " + str(bloc_v.get("motif", "")))
        if gele:
            return self._juger_pari(fiche, issue, gele, tirages)
        issue["statistique"], issue["seuil"] = bloc["statistique"], bloc["seuil"]
        motifs = {"survit": "seuil franchi, verdict confirmé", "eliminee": "statistique sous le seuil (réfutée)",
                  "indecise": "l'expérimentateur déclare l'expérience indécise"}
        return dict(issue, verdict_final=bloc["verdict"], motif=motifs[bloc["verdict"]])

    def _juger_pari(self, fiche, issue, gele, tirages):
        """Le noyau juge : richesse contre le nul, héritage de la preuve, verdict (commun aux fiches avec agents et aux
        témoins jugés sans agents)."""
        graine_noyau = self.depots.get(gele.empreinte, {}).get("graine_noyau", self.graine_noyau)
        try:
            if gele.engagement.get("instants_lecture"):
                from . import nul_filles_v2 as nf
                ev = nf.evaluer_v2(gele, tirages, graine_noyau=graine_noyau)
            else:
                ev = sp.evaluer(gele, tirages, graine_noyau=graine_noyau)
        except (sp.EngagementModifie, sp.TiragesNonLies, ValueError) as e:  # plan d'exécution non conforme compris
            return dict(issue, verdict_final="rejetee (test change)", motif=f"{type(e).__name__} : {e}")
        heritage = self.memoire.heritage(fiche.identifiant) if self.memoire is not None and self.memoire.active else None
        if heritage is not None:
            # Héritage de la preuve (v4) : la classe repart de son log W cumulé ; promue si cumul + log W ≥ log 1/α
            # à un instant de lecture (et, pour une fille, si la marge est atteinte). Valide : produit d'e-valeurs.
            promue = (heritage["cumul"] + ev["log_richesse_max"] >= ev["seuil_log"]) and ev.get("marge_atteinte", True)
            ev = dict(ev, heritage=dict(heritage, promue_sans_heritage=ev["promue"]), promue=promue)
        issue["pari"] = ev
        issue["statistique"], issue["seuil"] = ev["log_richesse_max" if ev.get("mode", "continu") == "continu"
                                                 else "log_richesse_finale"], ev["seuil_log"]
        verdict = "survit" if ev["promue"] else "eliminee"
        motif = "richesse au seuil 1/α" if ev["promue"] else "richesse sous le seuil 1/α (réfutée par le pari)"
        if heritage is not None:
            motif += f" ; preuve héritée de la classe {heritage['classe']} (log W cumulé {round(heritage['cumul'], 4)})"
        return dict(issue, verdict_final=verdict, motif=motif)

    def _reserve_role(self, role, plafond):
        """v11 (C1) : montant réservé (et réglé) pour un rôle ; 0 pour un rôle simulé d'un adaptateur mixte (il ne dépense
        rien, v10) ; le plafond sinon (simulation pure comprise : ses coûts simulés comptent dans son propre budget)."""
        roles_reels = getattr(self.adaptateur, "roles_reels", None)
        if roles_reels is not None and role not in roles_reels:
            return 0.0
        return plafond

    def _juger_temoin_sans_agent(self, fiche):
        """v7 : témoin jugé par le noyau seul, sur les issues qu'il a déposées (aucun agent, aucune dépense)."""
        issue = {"identifiant": fiche.identifiant, "famille_source": fiche.famille_source(), "desaccord": False,
                 "couts": {}, "verdict_declare": "tirages", "code": {}, "sans_agent": True}
        gele = self.engagements.get(fiche.identifiant)
        mesures = self.mesures_noyau.get(fiche.identifiant)
        if gele is None or mesures is None:
            return dict(issue, verdict_final="indecise", motif="témoin sans agent : aucune mesure déposée par le noyau")
        return self._juger_pari(fiche, issue, gele, mesures)

    # ordonnancement : vagues bornées par la concurrence, budget réservé avant chaque lancement ------------------
    def executer(self, fiches):
        ordre = sorted(fiches, key=lambda f: (f.temoin is None, f.identifiant))
        issues, a_lancer = {}, []
        for fiche in ordre:
            refus = self.geler(fiche)
            if refus is not None:
                issues[fiche.identifiant] = {"identifiant": fiche.identifiant, "verdict_final": fiche.statut, "motif": refus,
                                             "famille_source": fiche.famille_source(), "couts": {}, "desaccord": False}
            else:
                a_lancer.append(fiche)
        temoins_faux_sans_agent = 0
        if self.config.temoins_sans_agent and self.monde_noyau is not None:  # v7 : témoins jugés par le noyau seul
            for fiche in [f for f in a_lancer if f.temoin is not None]:
                issues[fiche.identifiant] = self._juger_temoin_sans_agent(fiche)
                temoins_faux_sans_agent += fiche.temoin == "fausse"
            a_lancer = [f for f in a_lancer if f.temoin is None]
        # v11 (contre-lectures C5 et C2 du socle) : m de la règle e-BH fixé AVANT toute issue : fiches à lancer (hors
        # budget comprises, e = 0 si non jugées) plus témoins faux jugés sans agent. Les témoins VRAIS sont hors de la
        # famille : découvertes sûres, ils abaissaient le seuil m/(α·k) des fiches réelles (16 % de fausses découvertes
        # réelles avec 3 témoins vrais parmi 24, contre 5 %) ; ils sont lus à part, au même seuil m/α.
        m_fixe = sum(1 for f in a_lancer if f.temoin != "vraie") + temoins_faux_sans_agent
        for debut in range(0, len(a_lancer), self.config.concurrence):
            vague = []
            for fiche in a_lancer[debut:debut + self.config.concurrence]:
                # v11 (contre-lecture C1) : la réservation suit le rôle effectif (0 pour un rôle simulé de l'adaptateur
                # mixte, comme son règlement en v10) ; et un refus ne condamne plus toute la suite de la génération :
                # chaque fiche tente sa réservation (une réservation libérée par la vague précédente peut revenir).
                reserve = (self._reserve_role("experimentateur", min(fiche.cout_borne, self.config.plafond_experimentateur_usd))
                           + self._reserve_role("verificateur", self.config.plafond_verificateur_usd))
                if not self.budget.reserver(reserve):
                    fiche.statut = "hors budget"
                    issues[fiche.identifiant] = {"identifiant": fiche.identifiant, "verdict_final": "hors budget",
                                                 "motif": "plafond de la génération atteint", "couts": {},
                                                 "famille_source": fiche.famille_source(), "desaccord": False}
                    continue
                vague.append((fiche, reserve))
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.concurrence) as pool:
                futurs = {pool.submit(self._traiter_sur, f): f for f, _ in vague}
                for futur in concurrent.futures.as_completed(futurs):
                    fiche = futurs[futur]
                    issue = futur.result()
                    if "experimentateur" not in issue["couts"]:
                        self.budget.regler(self._reserve_role("experimentateur",
                                                              min(fiche.cout_borne, self.config.plafond_experimentateur_usd)), 0.0)
                    if "verificateur" not in issue["couts"]:
                        self.budget.regler(self._reserve_role("verificateur", self.config.plafond_verificateur_usd), 0.0)
                    issues[fiche.identifiant] = issue
        for fiche in ordre:  # v11 : la nature de témoin accompagne l'issue (la règle e-BH exclut les témoins vrais)
            if fiche.identifiant in issues and isinstance(issues[fiche.identifiant], dict):
                issues[fiche.identifiant]["temoin"] = fiche.temoin
        if self.config.multiplicite == "e-bh":  # v7 : règle de multiplicité sur la génération entière
            appliquer_multiplicite(issues, self.config.alpha, m_fixe=m_fixe)
        for fiche in ordre:
            self.selectionner(fiche, issues[fiche.identifiant])
        if self.config.noyau_secret:  # v5 : la graine ne quitte le noyau qu'après toutes les évaluations
            ecrire_json_scelle(os.path.join(self.racine, "noyau", f"graine-noyau-generation-{self.numero:02d}.json"),
                               {"generation": self.numero, "graine_noyau": self.graine_noyau,
                                "ecrite_apres_les_evaluations": True})
        qualite = mesure_qualite(ordre, self.registre_gel, issues)
        # v7 : signal « pas de dents » : des témoins vrais ont été jugés par le pari et **aucun** n'est promu ; les
        # promotions de la génération sont alors étiquetées (le verdict ne change pas ; la lecture doit en tenir compte).
        # v7, version 5 (défaut 3 du premier lancement réel) : un témoin vrai indécis ou en erreur n'est pas « jugé » ;
        # si aucun ne l'est, l'état est « dents non mesurées », et les promotions sont étiquetées de même.
        sans_dents = qualite["etat_dents"] == "pas de dents"
        qualite["sans_dents"] = sans_dents
        if qualite["etat_dents"] != "dents":
            for issue in issues.values():
                if issue.get("verdict_final") == "survit":
                    if sans_dents:
                        issue["sans_dents"] = True
                    elif qualite["etat_dents"] == "dents non mesurées":
                        issue["dents_non_mesurees"] = True
        erreurs = sorted(i for i, issue in issues.items() if issue.get("erreur_orchestrateur"))
        arret_budget = any(f.statut == "hors budget" for f in a_lancer)  # v11 : au moins une fiche sans réservation
        return {"generation": self.numero, "issues": {i: issues[i] for i in sorted(issues)},
                "arret_budget": arret_budget, "budget": self.budget.etat(), "qualite": qualite,
                "erreurs_orchestrateur": {"fiches": erreurs, "lancees": len(a_lancer)}}

    def _traiter_sur(self, fiche):
        """Une erreur de l'orchestrateur sur une fiche la rend indécise, motif écrit, marquée `erreur_orchestrateur` ;
        elle n'arrête pas la génération, ne compte pas comme un essai (la fiche reste rejouable) et garde ses coûts déjà
        réglés (v7, version 5, défauts 2 et 4 du premier lancement réel)."""
        issue = self.issue_vierge(fiche)
        try:
            return self.traiter(fiche, issue)
        except Exception as e:  # noqa: BLE001 — consigné dans l'issue, jamais avalé en silence
            return dict(issue, verdict_final="indecise", erreur_orchestrateur=True,
                        motif=f"erreur de l'orchestrateur : {type(e).__name__} : {caviarder(str(e))[0][:300]}")

    # (d) sélection ---------------------------------------------------------------------------------------------
    @staticmethod
    def selectionner(fiche, issue):
        verdict = issue["verdict_final"]
        if issue.get("erreur_orchestrateur"):
            # v7, version 5 : une fiche ne perd jamais sa chance par la plomberie (S-V1, témoin vrai, retiré en (a)).
            fiche.statut = "indecise"
            fiche.historique.append({"verdict": verdict, "motif": issue.get("motif"), "erreur_orchestrateur": True})
            issue["statut"] = fiche.statut
            return
        if verdict in ("survit", "eliminee", "indecise", "rejetee (test change)"):
            fiche.essais += 1
        if verdict == "survit":
            fiche.statut = "survit"
            issue["aptitude"] = fiche.aptitude()
        elif verdict == "indecise":
            fiche.statut = "retiree" if fiche.essais >= 2 else "indecise"
        elif verdict in STATUTS:
            fiche.statut = verdict
        fiche.historique.append({"verdict": verdict, "motif": issue.get("motif")})
        issue["statut"] = fiche.statut


def appliquer_multiplicite(issues, alpha, m_fixe=None):
    """Règle e-BH (Wang et Ramdas, 2022) sur les fiches jugées de la génération.

    e-valeur d'une fiche : sa richesse **arrêtée au premier instant de lecture où elle atteint m/α** (m = nombre de fiches
    jugées de la génération, fixé avant toute issue), sinon sa richesse au dernier instant ; c'est un temps d'arrêt du
    processus de la fiche, donc une e-valeur valide (arrêt optionnel d'une surmartingale positive) ; la preuve héritée de
    la classe (log W cumulé) s'y ajoute (produit d'e-valeurs). Les e-valeurs triées par ordre décroissant, k* = le plus
    grand k tel que e_(k) ≥ m / (α · k) ; les k* premières sont retenues, les autres survivantes sont éliminées (motif
    écrit). Taux de fausses découvertes ≤ α sur la génération, quelle que soit la dépendance entre fiches. Les témoins
    comptent dans m.

    **Correction du 27 octobre (14:47 UTC)** : la version précédente arrêtait la richesse au seuil **par fiche** 1/α ;
    l'e-valeur était alors plafonnée vers 1/α, et e-BH ne pouvait rien retenir dès que m > 1 (erreur relevée par la course
    du monde planté : deux témoins vrais à log W 34 et 28 éliminés). Erratum : `../erratum-multiplicite-e-bh-v1.md`.

    **v11 (contre-lecture du code, C5)** : (i) `m_fixe`, fixé par l'appelant avant toute issue (fiches lancées, hors
    budget comprises, plus témoins jugés sans agent), remplace `len(jugees)` compté après coup ; une fiche non jugée
    vaut e = 0 ; (ii) une fille dont la marge `delta0` n'est pas atteinte (`marge_atteinte` faux) reçoit e = 0 AVANT le
    tri — e' = e·1{marge} reste une e-valeur — au lieu d'entrer dans k* puis d'être rétrogradée après la règle (ce qui
    rétrécissait le dénominateur après coup ; enjeu mesuré nul sur 2 000 générations, preuve rompue tout de même)."""
    jugees = [(i, issue) for i, issue in issues.items() if isinstance(issue.get("pari"), dict)
              and issue["pari"].get("trajectoire_log_w") and issue.get("temoin") != "vraie"]
    temoins_vrais = [(i, issue) for i, issue in issues.items() if isinstance(issue.get("pari"), dict)
                     and issue["pari"].get("trajectoire_log_w") and issue.get("temoin") == "vraie"]
    m = len(jugees) if m_fixe is None else int(m_fixe)
    if m < len(jugees):
        raise ValueError(f"m_fixe ({m}) < fiches jugées ({len(jugees)}) : m doit compter toutes les fiches lancées")
    if m == 0:
        return {"m": 0, "retenues": []}
    seuil_arret = math.log(m / alpha)

    def log_e(issue):
        ev = issue["pari"]
        if ev.get("marge_atteinte") is False:
            return -math.inf
        traj = ev["trajectoire_log_w"]
        arretee = next((v for v in traj if v >= seuil_arret), traj[-1])
        return arretee + float((ev.get("heritage") or {}).get("cumul", 0.0))

    valeurs = {i: log_e(issue) for i, issue in jugees}
    for i, issue in temoins_vrais:  # hors famille : lus au seuil m/α de la génération, sans peser sur k*
        v = log_e(issue)
        retenu = v >= seuil_arret
        issue["pari"]["multiplicite"] = {"regle": "hors famille (témoin vrai), seuil m/α", "m": m, "retenue": retenu,
                                         "log_e": None if math.isinf(v) else round(v, 6), "seuil_log_arret": round(seuil_arret, 6)}
        if issue["verdict_final"] == "survit" and not retenu:
            issue["verdict_final"] = "eliminee"
            issue["motif"] = (issue.get("motif") or "") + f" ; témoin vrai sous le seuil m/α de la génération (m = {m})"
    ordre = sorted(jugees, key=lambda x: -valeurs[x[0]])
    k_etoile = 0
    for k, (i, _) in enumerate(ordre, 1):
        if valeurs[i] >= math.log(m / (alpha * k)):
            k_etoile = k
    retenues = [i for i, _ in ordre[:k_etoile]]
    for i, issue in jugees:
        issue["pari"]["multiplicite"] = {"regle": "e-bh", "m": m, "retenue": i in retenues,
                                         "log_e": None if math.isinf(valeurs[i]) else round(valeurs[i], 6),
                                         "seuil_log_arret": round(seuil_arret, 6),
                                         "seuil_log_retenue": math.log(m / (alpha * max(1, k_etoile))) if k_etoile else None}
        if issue["verdict_final"] == "survit" and i not in retenues:
            issue["verdict_final"] = "eliminee"
            issue["motif"] = (issue.get("motif") or "") + f" ; règle de multiplicité e-BH (m = {m}) : non retenue"
    return {"m": m, "retenues": retenues}


# (e) mesure de qualité ---------------------------------------------------------------------------------------------
def _etat_dents(vraies_jugees, vraies_promues):
    if vraies_promues:
        return "dents"
    return "pas de dents" if vraies_jugees else "dents non mesurées"


def mesure_qualite(fiches, registre_gel, issues=None):
    """Qualité mesurée sur les témoins ; vérité revérifiée par empreinte.

    Clés historiques (« testés » = servis et tranchés au sens large, indécis et retirés compris) gardées pour les lecteurs
    existants. v7, version 5 (défaut 3 du premier lancement réel : « vrais testés 3, éliminés 0 » pour **aucun** jugé) :
    « jugés » = verdict du pari (survit ou éliminée) **dans cette génération** ; vraies promues (puissance) ; témoins en
    erreur de l'orchestrateur à part ; état des dents : « dents » (au moins un témoin vrai promu), « pas de dents »
    (témoins vrais jugés, aucun promu), « dents non mesurées » (aucun témoin vrai jugé)."""
    temoins = [f for f in fiches if f.temoin is not None and registre_gel.est_gelee(f.identifiant)]
    for f in temoins:
        registre_gel.verifier(f)
    testes = [f for f in temoins if f.statut in ("survit", "eliminee", "indecise", "retiree", "rejetee (test change)")]
    fausses = [f for f in testes if f.temoin == "fausse"]
    vraies = [f for f in testes if f.temoin == "vraie"]
    gardees = sum(f.statut == "survit" for f in fausses)
    eliminees = sum(f.statut == "eliminee" for f in vraies)
    issues = issues or {}

    def verdict(f):
        issue = issues.get(f.identifiant)
        return issue.get("verdict_final") if issue is not None else f.statut

    def en_erreur(f):
        return bool((issues.get(f.identifiant) or {}).get("erreur_orchestrateur"))

    jugees_v = [f for f in temoins if f.temoin == "vraie" and verdict(f) in ("survit", "eliminee")]
    jugees_f = [f for f in temoins if f.temoin == "fausse" and verdict(f) in ("survit", "eliminee")]
    promues = sum(verdict(f) == "survit" for f in jugees_v)
    return {"temoins_faux_testes": len(fausses), "temoins_vrais_testes": len(vraies),
            "fausses_gardees": gardees, "taux_fausses_gardees": gardees / len(fausses) if fausses else None,
            "vraies_eliminees": eliminees, "taux_vraies_eliminees": eliminees / len(vraies) if vraies else None,
            "temoins_servis": len(temoins), "temoins_vrais_juges": len(jugees_v), "temoins_faux_juges": len(jugees_f),
            "vraies_promues": promues, "taux_vraies_promues": promues / len(jugees_v) if jugees_v else None,
            "temoins_en_erreur": sum(en_erreur(f) for f in temoins),
            "temoins_non_juges": len(temoins) - len(jugees_v) - len(jugees_f),
            "etat_dents": _etat_dents(len(jugees_v), promues),
            "detail": {f.identifiant: {"verite": f.temoin, "statut": f.statut, "verdict": verdict(f),
                                       "erreur_orchestrateur": en_erreur(f)} for f in temoins}}


CLES_CUMULEES = ("temoins_faux_testes", "temoins_vrais_testes", "fausses_gardees", "vraies_eliminees", "temoins_servis",
                 "temoins_vrais_juges", "temoins_faux_juges", "vraies_promues", "temoins_en_erreur", "temoins_non_juges")


def cumuler_qualite(mesures):
    total = {cle: 0 for cle in CLES_CUMULEES}
    for m in mesures:
        for cle in total:
            total[cle] += m.get(cle, 0)
    total["taux_fausses_gardees"] = total["fausses_gardees"] / total["temoins_faux_testes"] if total["temoins_faux_testes"] else None
    total["taux_vraies_eliminees"] = total["vraies_eliminees"] / total["temoins_vrais_testes"] if total["temoins_vrais_testes"] else None
    total["taux_vraies_promues"] = (total["vraies_promues"] / total["temoins_vrais_juges"]
                                    if total["temoins_vrais_juges"] else None)
    total["etat_dents"] = _etat_dents(total["temoins_vrais_juges"], total["vraies_promues"])
    return total
