"""Configuration de la course 2 et de son pré-pilote, version 54 — au-dessus de `configuration_v53` (inchangé, R12).

Ce que la v54 ajoute (contre-lecture CL18 et annexe du bras méta, brouillon 1) :

1. **Choix de code remontés à Lazar, rendus configurables** (aucun n'est figé dans le code ; un champ qui porte encore « À
   REMPLIR » fait refuser la configuration avant tout appel, comme en v53) :
   - `budget.portee_plafond` ∈ {`par_generation`, `course`} (choix 1, CL18-11) : S17 par génération (la ligne de GO doit
     porter N × S17 + (N − 1) × étage) ou S17 pour toute la course (la ligne de GO porte S17) ;
   - `garde_kimi.refus_aiguilleur` ∈ {`debordement`, `technique`} (choix 6, CL18-10) : un refus ou une réponse illisible de
     l'aiguilleur sur une fiche de Kimi compte au débordement (S12) ou seulement aux échecs techniques (A14) ;
   - `garde_kimi.arret_metteur_fusion` booléen (choix 7, CL18-10) : un débordement arrête aussi Kimi metteur en fusion ;
   - `bisociateur.meta.regle_divergence` ∈ {`fiche_ecartee`, `premier_lecteur`} et `bisociateur.meta.structures` ∈
     {`union`, `intersection`} (choix 10, annexe I-5) ;
   - `tableau.juger_passe_tableau` booléen (choix 11, CL18-08 b) ;
   - `bisociateur.fournisseurs_entree` : liste de fournisseurs dont la passe 1 entre au bisociateur, ou `["*"]` (CL18-08 a :
     le brouillon 7 dit « passe 1 de Kimi ») ;
   - `a4.mode` ∈ {`mot_entier`, `prefixe`} et `a4.action` ∈ {`arret`, `fiche_exclue`} (CL18-06) ;
   - `graines.prefixe` (CL18-07) : préfixe des tâches de graines ; « pp2 » donne exactement les noms du brouillon 7 ;
   - `arrets` (A3, A11, A14) : nombre d'échecs consécutifs, délais par fournisseur (clé « * » obligatoire), part maximale
     d'appels sans sortie exploitable, modèles soumis à A11.
2. **A15 refaite (CL18-03)** : `verifier_go_v54` exige, en plus des contrôles de la garde du dépôt, que la cellule « plafond »
   de la ligne citée porte **un seul montant**, en USD, **égal** au montant requis (S17 ; N × S17 + étage si la portée est
   « par génération » et N > 1) ; une cellule qui porte plusieurs montants (« 10 USD par lancement, dans les 150 USD… »),
   un montant « par lancement », un autre montant (plus petit **ou plus grand**) ou un identifiant non exact est refusée.
3. **DEP4 (CL18-09)** : la confirmation de session-depot (le relais accepte une réservation dépassée jusqu'à S17 − cumul et
   coupe à S17 seulement) est une pièce empreintée (`dependances.dep4` = nom d'une pièce) exigée pour tout lancement réel.
4. **Décisions d'A15** (pré-pilote) : `decisions_a15` porte les mots de Lazar exigés au lancement (confidentialité, D-f, D-g à
   D-j…) ; une valeur absente ou « À REMPLIR » refuse le lancement réel.

Spécification citée : préenregistrement du pré-pilote, **brouillon 7** (`799b9ca9…`), seul fichier de spécification de la v54.
"""

import datetime
import re

from . import configuration_v53 as c53
from .configuration_v53 import ConfigurationRefusee, GoRefuse, entier, reel

VERSION = "configuration-course-2-v54"
MARQUEUR = c53.MARQUEUR
SPECIFICATION = ("brouillons/canal-reprise-releve-v1/envois/pole-scientifique-automatique-v1/pre-pilote-course-2-v1/"
                 "preenregistrement-pre-pilote-course-2-brouillon7.md")
SPECIFICATION_SHA256 = "799b9ca9c4ec30d8ab2c782496643b64cdbfcd8ca09eb08b9b8694b0c8ece6f5"
PORTEES = ("par_generation", "course")
MONTANT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(USD|\$|dollars?|€|EUR|euros?)", re.I)


def _get(d, chemin):
    return c53._get(d, chemin)


def _bool(v):
    return isinstance(v, bool)


def _chaine(v):
    return isinstance(v, str) and bool(v)


CHOIX_V54 = (
    ("budget.portee_plafond", lambda v: v in PORTEES, "choix 1 (CL18-11) : portée de S17 (par_generation | course)"),
    ("garde_kimi.refus_aiguilleur", lambda v: v in ("debordement", "technique"),
     "choix 6 (CL18-10) : refus de l'aiguilleur sur une fiche de Kimi (debordement | technique)"),
    ("garde_kimi.arret_metteur_fusion", _bool, "choix 7 (CL18-10) : débordement → arrêt de Kimi metteur en fusion (booléen)"),
    ("tableau.juger_passe_tableau", _bool, "choix 11 (CL18-08 b) : fiches de la passe « tableau » jugées (booléen)"),
    ("bisociateur.fournisseurs_entree", lambda v: isinstance(v, list) and v and all(_chaine(x) for x in v),
     "CL18-08 a : fournisseurs dont la passe 1 entre au bisociateur (liste ; [\"*\"] = tous)"),
    ("a4.mode", lambda v: v in ("mot_entier", "prefixe"), "CL18-06 : correspondance des étiquettes interdites"),
    ("a4.action", lambda v: v in ("arret", "fiche_exclue"), "CL18-06 : étiquette dans une fiche (arret | fiche_exclue)"),
    ("graines.prefixe", lambda v: isinstance(v, str) and re.fullmatch(r"[a-z0-9]+", v or ""), "CL18-07 : préfixe des tâches"),
    ("arrets.a3_echecs_consecutifs", lambda v: entier(v, 1), "A3 : échecs consécutifs d'un rôle avant son arrêt"),
    ("arrets.a3_delai_s", lambda v: isinstance(v, dict) and "*" in v and all(reel(x, 0, strict_mini=True) for x in v.values()),
     "A3 : délai par fournisseur (secondes ; clé « * » obligatoire)"),
    ("arrets.a14_part_max", lambda v: reel(v, 0, 1), "A14 : part maximale d'appels sans sortie exploitable d'un rôle"),
    ("arrets.a11_modeles", lambda v: isinstance(v, list) and all(_chaine(x) for x in v),
     "A11 : modèles dont le refus ou la limite est compté sans bascule"),
)

CHOIX_META = (
    ("bisociateur.meta.regle_divergence", lambda v: v in ("fiche_ecartee", "premier_lecteur"),
     "choix 10 / I-5 : niches divergentes des deux lecteurs"),
    ("bisociateur.meta.structures", lambda v: v in ("union", "intersection"), "choix 10 / I-5 : structures des deux lecteurs"),
    ("bisociateur.meta.definitions", lambda v: v in ("annexe", "consigne"),
     "I-4 : définitions des niches servies (annexe : clés definitions_* ; consigne : vérifiées dans la consigne figée)"),
    ("bisociateur.meta.s28", lambda v: v == "annexe" or (isinstance(v, dict) and reel(v.get("kappa_min"), -1, 1)
                                                          and reel(v.get("jaccard_min"), 0, 1)),
     "I-3 : seuils S28 (« annexe » ou {kappa_min, jaccard_min})"),
    ("bisociateur.meta.desaccord.paires_max", lambda v: entier(v, 0), "I-2 : paires lues pour le désaccord"),
    ("bisociateur.meta.desaccord.champ_affirmation", _chaine, "I-2 : champ de la fiche servi comme affirmation centrale"),
    ("bisociateur.meta.desaccord.consigne", _chaine, "I-2 : pièce : consigne figée de la lecture du désaccord"),
)


def verifier_choix_v54(conf):
    """Liste des manques des clés v54 (vide si tout est là)."""
    manques = []
    controles = list(CHOIX_V54)
    if "meta" in (_get(conf, "bisociateur.bras")[0] or []):
        controles += list(CHOIX_META)
    for chemin, controle, quoi in controles:
        v, present = _get(conf, chemin)
        if not present:
            manques.append(f"{chemin} manquant ({quoi} ; aucun défaut)")
        elif not controle(v):
            manques.append(f"{chemin} invalide ({quoi}) : {v!r}")
    pieces = conf.get("pieces") or {}
    if "meta" in (_get(conf, "bisociateur.bras")[0] or []):
        nom, present = _get(conf, "bisociateur.meta.desaccord.consigne")
        if present and _chaine(nom) and nom not in pieces:
            manques.append(f"pièce {nom!r} (consigne du désaccord) absente de « pieces »")
    return manques


def lire_configuration_v54(chemin_ou_objet, base=None):
    """La lecture v53 (marqueurs, obligatoires, pièces à leur empreinte), puis les clés v54 ; tous les manques en une fois."""
    manques = []
    try:
        conf = c53.lire_configuration(chemin_ou_objet, base=base)
    except ConfigurationRefusee as e:
        conf = None
        manques.append(str(e))
    if conf is not None:
        manques += verifier_choix_v54(conf)
    else:
        import json
        brut = chemin_ou_objet if isinstance(chemin_ou_objet, dict) else json.load(open(chemin_ou_objet, encoding="utf-8"))
        manques += verifier_choix_v54(brut)
    if manques:
        raise ConfigurationRefusee("configuration v54 refusée avant tout appel :\n- " + "\n- ".join(manques))
    conf["version_configuration"] = VERSION
    return conf


# --- A15 (CL18-03) ------------------------------------------------------------------------------------------------------


def montants(cellule):
    """Tous les montants écrits dans une cellule (valeur, unité)."""
    return [(float(m.group(1).replace(",", ".")), m.group(2)) for m in MONTANT.finditer(cellule or "")]


def montant_requis(conf, nombre_generations, plafond_etage_usd=None):
    """Montant que la ligne de GO doit porter **exactement** (choix 1 : `budget.portee_plafond`)."""
    s17 = float(conf["budget"]["plafond_usd"])
    if isinstance(nombre_generations, bool) or not isinstance(nombre_generations, int) or nombre_generations < 1:
        raise ConfigurationRefusee("nombre de générations : entier ≥ 1, aucun défaut")
    portee = conf["budget"].get("portee_plafond")
    if portee == "course":
        return s17
    if portee != "par_generation":
        raise ConfigurationRefusee(f"budget.portee_plafond : {PORTEES} exigé (reçu {portee!r})")
    total = nombre_generations * s17
    if plafond_etage_usd is not None and nombre_generations > 1:
        total += (nombre_generations - 1) * float(plafond_etage_usd)
    return total


def verifier_go_v54(go_id, registre, montant_requis_usd, aujourd_hui=None):
    """A15 (brouillon 7 : « ligne de GO au plafond gelé S17, aucun lancement à un autre plafond ») : les contrôles de la garde
    du dépôt (lus par `configuration_v53.lire_registre_go`), puis la cellule « plafond » : un seul montant, en USD, égal au
    montant requis, sans « par lancement ». Rend la ligne ; lève `GoRefuse` sinon."""
    if not isinstance(go_id, str) or not c53.GO_ID.fullmatch(go_id):
        raise GoRefuse("A15 : aucun lancement sans identifiant de GO exact (GO_ID=GO-AAAA-MM-JJ-NN)")
    if not reel(montant_requis_usd, 0, strict_mini=True):
        raise GoRefuse(f"A15 : montant requis invalide {montant_requis_usd!r}")
    aujourd_hui = aujourd_hui or datetime.datetime.now(datetime.timezone.utc).date()
    reg = c53.lire_registre_go(registre)
    g = reg.get(go_id)
    if g is None:
        raise GoRefuse(f"A15 : {go_id} absent du registre {registre}")
    if g["type"] != "calcul":
        raise GoRefuse(f"A15 : {go_id} est un GO de type {g['type']!r}, pas « calcul »")
    if g["par"] != "Lazar":
        raise GoRefuse(f"A15 : {go_id} n'est pas accordé par Lazar")
    if not (g["accorde"] <= aujourd_hui <= g["echeance"]):
        raise GoRefuse(f"A15 : {go_id} hors de sa période de validité ({g['accorde']} → {g['echeance']})")
    revocations = sorted(k for k, r in reg.items() if r["type"] == "révocation" and (go_id in r["perimetre"] or go_id in r["ref"]))
    if revocations:
        raise GoRefuse(f"A15 : {go_id} révoqué par {', '.join(revocations)}")
    cellule = g["plafond"]
    ms = montants(cellule)
    distincts = sorted({(v, u.upper().rstrip("S")) for v, u in ms})
    if not ms:
        raise GoRefuse(f"A15 : la ligne {go_id} ne porte aucun montant lisible (« {cellule} »)")
    if len(distincts) != 1:
        raise GoRefuse(f"A15 : la ligne {go_id} porte plusieurs montants (« {cellule} ») : un seul plafond exigé, égal à "
                       f"{montant_requis_usd:g} USD")
    valeur, unite = ms[0]
    if unite.upper() not in ("USD", "$", "DOLLAR", "DOLLARS"):
        raise GoRefuse(f"A15 : la ligne {go_id} porte un montant en {unite} : USD exigé")
    if re.search(r"par\s+(lancement|run|appel|session|jour|instance)", cellule, re.I):
        raise GoRefuse(f"A15 : la ligne {go_id} porte un plafond « par lancement » (« {cellule} ») : plafond total exigé")
    if abs(valeur - float(montant_requis_usd)) > 1e-9:
        raise GoRefuse(f"A15 : la ligne {go_id} porte {valeur:g} USD, pas exactement le plafond requis {float(montant_requis_usd):g} "
                       "USD : aucun lancement à un autre plafond (plus petit ou plus grand)")
    return dict(g, accorde=g["accorde"].isoformat(), echeance=g["echeance"].isoformat(), identifiant=go_id,
                plafond_lu_usd=valeur, montant_requis_usd=float(montant_requis_usd))


def verifier_dependances_lancement(conf, plan="course"):
    """Lancement réel seulement : DEP4 (pièce empreintée, CL18-09) ; au pré-pilote, les décisions d'A15. Rend la liste des
    manques (vide = conforme)."""
    manques = []
    nom, present = _get(conf, "dependances.dep4")
    if not present or not _chaine(nom):
        manques.append("dependances.dep4 manquant : confirmation de DEP4 par session-depot exigée (A15, VB6-04)")
    elif nom not in (conf.get("pieces") or {}):
        manques.append(f"dependances.dep4 : pièce {nom!r} absente de « pieces »")
    else:
        try:
            c53.texte_piece(conf, nom)
        except (ConfigurationRefusee, OSError) as e:
            manques.append(f"dependances.dep4 : {e}")
    if plan == "pre_pilote":
        dec = conf.get("decisions_a15")
        attendues = ("confidentialite", "d_f", "d_g", "d_h", "d_i", "d_j", "go_lancement")
        if not isinstance(dec, dict):
            manques.append("decisions_a15 manquant (A15 : confidentialité, D-f, D-g à D-j, GO de lancement)")
        else:
            for k in attendues:
                if not _chaine(dec.get(k)) or MARQUEUR in dec.get(k, ""):
                    manques.append(f"decisions_a15.{k} : mot de Lazar absent (A15 : aucun lancement)")
    return manques
