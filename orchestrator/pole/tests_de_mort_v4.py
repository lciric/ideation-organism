"""Étage de tests de mort, **version 4** (orchestrateur v57) : la version 3 (`pole/tests_de_mort_v3.py`, elle-même la version 2
telle quelle plus la borne mémoire de CL16-01) **telle quelle** (R12 : aucun octet changé), plus le **verdict calculé par le
noyau** décidé par le directeur le 1er novembre 2026 (R-1057). Fournit le verdict qui ferme le défaut annoncé à la première ligne
de la table des gardes du LISEZMOI (section 3, « The agent prints its own verdict ») ; l'étage ne l'appelle pas encore (voir
« Non fait » : tant que ce câblage manque, le défaut reste ouvert dans l'étage).

Le défaut (versions 2 et 3, `recalcul_noyau`) : le noyau ne recalculait que la statistique que le script **déclarait** dans une
ligne `CALCUL:` (seul le fichier nommé était contrôlé, et c'était un fichier de la tranche) ; sans ligne `CALCUL:`, le chiffre
imprimé par le script (`RESULTAT:`) faisait le verdict, étiqueté « non recalculé ». Le script choisissait donc ce qui serait
vérifié, et pouvait ne rien faire vérifier.

Décision R-1057, ce que cette version fait :

1. **Le test est lié au préenregistrement.** Fichier, colonne, statistique, seuil et comparateur viennent du préenregistrement
   court **scellé** (`<dossier de la fiche>/prereg-court.json`, sceau `.sha256` vérifié sans suivre de lien, contenu égal à
   celui que l'appelant passe), jamais du script. Une ligne `CALCUL:` du script est lue, consignée (`calcul_du_script`) et
   **ignorée** : le préenregistrement prime.
2. **Le verdict est calculé par le noyau** sur le fichier brut que le script a écrit dans son dossier de travail fermé (bac à
   sable, dossier neuf à chaque exécution), tel que le noyau l'a relevé (fichier régulier, sans lien), copié et scellé :
   `<dossier de la fiche>/execution-NN/produits/<nom_copie(fichier)>`, d'empreinte égale à celle de l'inventaire de
   l'exécution (`fichiers_produits[…]["sha256"]`) et à son compagnon `.sha256`. Le chiffre imprimé par le script n'est qu'un
   **témoin** : consigné (`chiffre_script`, `ligne_script`, `verdict_selon_chiffre_script`), avec sa concordance à la valeur
   du noyau (`concordance_script`, à l'arrondi d'affichage près, comme en v2), **jamais décisif**.
3. **« non concluant » n'est jamais mieux traité qu'« éliminée ».** Ordre total des verdicts (`rang_verdict`) :
   non concluant (0) < éliminée (1) < survit (2) — « non concluant » est rangé **sous** « éliminée », jamais au-dessus ni à
   égalité de « survit » ; la sélection (`selectionner`) ne retient que « survit » : « éliminée » et « non concluant » sortent
   tous deux. Aucune exécution réussie, fichier non produit, non copié, altéré, illisible (UTF-8, CSV), colonne absente,
   cellule non numérique ou non finie, statistique non finie : « non concluant », motif consigné.

Contrat du préenregistrement (clés lues par `verdict_du_noyau`) :

- `prereg["statistique"] = {"fichier": <chemin relatif propre du fichier CSV à en-tête que le script écrit dans son dossier de
  travail, ni sous `tranche/`, ni `script.py`, au plus 200 octets>, "colonne": <nom de colonne (ou rang à partir de 0, comme
  `statistique_de_colonne` de la v2)>, "statistique": <une de `STATISTIQUES` de la v2 : moyenne, mediane, somme, minimum,
  maximum, nombre, part_positive (la proportion de valeurs strictement positives), ecart_type>}` — exactement ces trois clés ;
- `prereg["seuil"] = {"valeur": <nombre fini>, "comparateur": <≥, ≤, >, < ou |x| ≤>, …}` — celui de la v2 (`lire_seuil`).

Sans bloc `statistique` utilisable, `verdict_du_noyau` lève `PreregSansStatistique` ; sans seuil utilisable, `PreregSansSeuil` ;
préenregistrement absent, non scellé ou différent du scellé, `PreregNonScelle` : **jamais** de repli sur le chiffre du script.
Le bloc vient de la fiche gelée, champ `test_de_mort.statistique` (`valider_champ_test_v4`, `extraire_prereg_court_v4`), et
entre dans le préenregistrement scellé avant la première session de l'expérimentateur (R1).

Exécution lue : la **dernière exécution réussie** (statut « réussie » : code 0, non tuée, aucune limite dépassée, données
intactes), comme la règle de lecture de la v2 ; si elle ne produit pas le fichier, « non concluant » (aucun repli sur une
exécution antérieure).

Non fait dans cette version (dit, pour qu'on ne lise pas l'étage comme câblé) : l'étage `executer_tests_de_mort` (v2, v3) n'appelle
pas encore `verdict_du_noyau` (il garde le lecteur, la lecture mécanique et `recalcul_noyau`) ; la consigne de l'expérimentateur
de la v2 dit encore que le chiffre lu est la ligne `RESULTAT:` (seul le préenregistrement servi porte la règle v4) ; la validation
des fiches de `ideation_v2` (`valider_champ_test` de la v2) refuse encore la clé `statistique` ; `selectionner` n'a pas encore
d'appelant. Au câblage, garder la règle de la v2 « tout incident de la fiche → non concluant » : `verdict_du_noyau` ne reçoit
pas les incidents (ceux qui changent le statut d'une exécution l'excluent déjà de la lecture ; « dossier de travail non
retiré » ne le change pas).

Limites dites : le noyau calcule la statistique, mais les lignes du fichier brut sont écrites par le script — un script qui
fabrique ses lignes n'est pas détecté ici ; le fichier brut doit tenir dans la copie du noyau (1 Mo, 20 premiers produits) ;
l'expérimentateur choisit, dans son quota d'exécutions, laquelle est la dernière réussie.

Bibliothèque standard seule ; aucun réseau ; aucune écriture hors du dossier de la fiche (`ecrire_verdict_du_noyau`).
"""

import csv
import hashlib
import json
import math
import os
import re

from . import tests_de_mort_v2 as _v2
from .dossier_ferme import _chemin_relatif_propre
from .outils import ecrire_json_scelle
from .tests_de_mort_v3 import *  # noqa: F401,F403  (la version 3 telle quelle : mêmes objets, version 2 comprise)
from .tests_de_mort_v3 import (CHAMP_TEST, GABARIT_TEST, MAX_COPIES_PRODUITS, STATISTIQUES, SUFFIXE_SCEAU,
                               TAILLE_MAX_COPIE_PRODUIT, TAILLE_MAX_NOM_COPIE, ChampTestInvalide, chiffre_lu, comparer,
                               extraire_prereg_court, lire_ligne_calcul, lire_regulier, nom_copie, statistique_de_colonne,
                               valider_champ_test)

VERSION_ETAGE = "tests_de_mort_v4 (v57, R-1057 : verdict calculé par le noyau)"
ETIQUETTE_NOYAU = "verdict calculé par le noyau depuis le fichier brut"
CLE_STATISTIQUE = "statistique"
CHAMPS_STATISTIQUE = ("fichier", "colonne", "statistique")
COMPARATEURS_CONNUS = ("≥", "≤", ">", "<", "|x| ≤")  # ceux que `comparer` (v2) sait appliquer
ORDRE_DES_VERDICTS = ("non concluant", "éliminée", "survit")  # rang croissant (`rang_verdict`)
NOM_PREREG = "prereg-court.json"  # écrit et scellé par l'étage (v2) dans le dossier de la fiche avant toute session
NOM_VERDICT = "verdict-noyau-v4.json"
TAILLE_MAX_PREREG = 1 << 20
TAILLE_MAX_COLONNE = 200
STATUT_CALCUL_DU_SCRIPT = "ignoré : le préenregistrement prime (R-1057)"
EMPREINTE = re.compile(r"[0-9a-f]{64}")
GABARIT_TEST_V4 = dict(GABARIT_TEST, statistique={
    "fichier": "chemin du fichier CSV à en-tête que le script écrit dans son dossier de travail (ni sous tranche/, ni script.py)",
    "colonne": "nom de la colonne (ou son rang à partir de 0)",
    "statistique": "|".join(STATISTIQUES)})


class PreregRefuse(ValueError):
    """Le préenregistrement ne permet pas au noyau de calculer un verdict : refus explicite, aucun repli (R-1057)."""


class PreregSansStatistique(PreregRefuse):
    """Bloc `statistique` absent ou mal formé : le noyau ne sait pas quoi calculer ; jamais de repli sur le chiffre du script."""


class PreregSansSeuil(PreregRefuse):
    """Seuil du préenregistrement absent, non chiffré ou de comparateur inconnu."""


class PreregNonScelle(PreregRefuse):
    """Le préenregistrement passé n'est pas le préenregistrement scellé du dossier de la fiche (absent, lien, sceau faux,
    contenu différent)."""


class VerdictInconnu(ValueError):
    """Un verdict hors des trois mots (survit, éliminée, non concluant)."""


class VerdictNonNoyau(ValueError):
    """Un verdict qui ne porte pas l'étiquette du noyau (`ETIQUETTE_NOYAU`) : la sélection et la consignation le refusent."""


# --- contrat du préenregistrement -----------------------------------------------------------------------------------------


def lire_bloc_statistique(bloc):
    """({fichier, colonne, statistique}, None) ou (None, motif) : le bloc `statistique` d'un préenregistrement ou d'un champ
    `test_de_mort`, exactement trois clés (voir le contrat du module)."""
    if not isinstance(bloc, dict):
        return None, "bloc absent ou non objet {fichier, colonne, statistique}"
    if set(bloc) != set(CHAMPS_STATISTIQUE):
        return None, ("clés attendues exactement : fichier, colonne, statistique (reçues : "
                      + ", ".join(sorted(str(k) for k in bloc)) + ")")
    fichier, colonne, statistique = (bloc[k] for k in CHAMPS_STATISTIQUE)
    if not _chemin_relatif_propre(fichier):
        return None, f"fichier : chemin relatif propre attendu ({fichier!r})"
    if fichier.split("/")[0] == "tranche" or fichier == "script.py":
        return None, f"fichier {fichier!r} : un fichier produit par le script est attendu (ni les données de tranche/, ni le script)"
    if len(fichier.encode("utf-8")) > TAILLE_MAX_NOM_COPIE:
        return None, f"fichier : nom de plus de {TAILLE_MAX_NOM_COPIE} octets (jamais copié par le noyau)"
    if not isinstance(colonne, str) or not colonne.strip() or colonne != colonne.strip() or len(colonne) > TAILLE_MAX_COLONNE:
        return None, f"colonne : nom non vide, sans espace autour, d'au plus {TAILLE_MAX_COLONNE} caractères attendu ({colonne!r})"
    if statistique not in STATISTIQUES:
        return None, f"statistique inconnue : {statistique!r} (permises : {', '.join(STATISTIQUES)})"
    return {"fichier": fichier, "colonne": colonne, "statistique": statistique}, None


def lire_seuil_du_prereg(prereg):
    """(valeur, comparateur) du seuil gelé du préenregistrement ; `PreregSansSeuil` sinon."""
    s = prereg.get("seuil")
    valeur = s.get("valeur") if isinstance(s, dict) else None
    comparateur = s.get("comparateur") if isinstance(s, dict) else None
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)) or not math.isfinite(valeur):
        raise PreregSansSeuil(f"seuil du préenregistrement non chiffré ou non fini ({valeur!r}) : aucun verdict")
    if comparateur not in COMPARATEURS_CONNUS:
        raise PreregSansSeuil(f"comparateur du seuil inconnu ({comparateur!r} ; permis : {', '.join(COMPARATEURS_CONNUS)}) : aucun verdict")
    return float(valeur), comparateur


def regle_de_lecture_v4(bloc, comparateur, seuil):
    return (f"le noyau calcule la statistique « {bloc['statistique']} » de la colonne « {bloc['colonne']} » du fichier "
            f"« {bloc['fichier']} » (CSV à en-tête, UTF-8) que le script écrit dans son dossier de travail, sur la copie scellée "
            f"par le noyau, à la dernière exécution réussie (code 0, non tuée) ; survit si cette valeur {comparateur} {seuil:g}, "
            "sans arrondi ; éliminée sinon ; non concluant si aucune exécution réussie, fichier non produit, non copié, altéré "
            "ou illisible, colonne absente, cellule non numérique ou valeur non finie ; le chiffre imprimé par le script "
            "(`RESULTAT:`) et toute ligne `CALCUL:` sont consignés comme témoins, jamais décisifs ; ordre des verdicts : non "
            "concluant < éliminée < survit, seule « survit » est retenue (R-1057)")


def valider_champ_test_v4(brut):
    """Le champ `test_de_mort` d'une fiche v4 : {seuil, test, donnees, statistique}, le bloc `statistique` **exigé** ; rend le
    champ canonique ou lève `ChampTestInvalide` (v2). Les trois premières clés sont validées par la v2 telle quelle."""
    if not isinstance(brut, dict) or set(brut) - set(GABARIT_TEST_V4):
        raise ChampTestInvalide("test_de_mort : objet {seuil, test, donnees, statistique} attendu")
    bloc, motif = lire_bloc_statistique(brut.get(CLE_STATISTIQUE))
    if bloc is None:
        raise ChampTestInvalide(f"test_de_mort.statistique : {motif} (v4 : exigé ; aucun repli sur le chiffre du script)")
    canon = valider_champ_test({k: v for k, v in brut.items() if k != CLE_STATISTIQUE})
    canon[CLE_STATISTIQUE] = bloc
    return canon


def extraire_prereg_court_v4(fiche, tranche, rang, quotas):
    """(préenregistrement court v4, None) ou (None, motif de refus à l'étage) : celui de la v2 (`extraire_prereg_court`, tout
    vient de la fiche gelée), plus le bloc `statistique` de `test_de_mort` et la règle de lecture v4. Fiche sans bloc
    utilisable : refusée à l'étage (aucun test), jamais testée sur le chiffre du script."""
    test = fiche.get(CHAMP_TEST) if isinstance(fiche, dict) else None
    if not isinstance(test, dict):
        return None, "fiche sans champ test_de_mort (seuil, test, données, statistique) : aucun test"
    bloc, motif = lire_bloc_statistique(test.get(CLE_STATISTIQUE))
    if bloc is None:
        return None, (f"test_de_mort.statistique : {motif} : aucun test (v4, R-1057 : le verdict se calcule sur le fichier brut "
                      "que le préenregistrement nomme ; aucun repli sur le chiffre du script)")
    prereg, motif = extraire_prereg_court(fiche, tranche, rang, quotas)
    if prereg is None:
        return None, motif
    regle = regle_de_lecture_v4(bloc, prereg["seuil"]["comparateur"], prereg["seuil"]["valeur"])
    prereg.update({CLE_STATISTIQUE: bloc, "plan_d_analyse": regle, "regle_de_lecture": regle, "version_etage": VERSION_ETAGE})
    return prereg, None


# --- lectures sans suivre de lien -----------------------------------------------------------------------------------------


def _empreinte_scellee(racine, relatif):
    """L'empreinte écrite dans le compagnon `<relatif>.sha256` (lu sans suivre de lien), ou None."""
    octets = lire_regulier(racine, relatif + SUFFIXE_SCEAU, 4096)
    if octets is None:
        return None
    try:
        morceaux = octets.decode("ascii").split()
    except UnicodeDecodeError:
        return None
    return morceaux[0] if morceaux and EMPREINTE.fullmatch(morceaux[0]) else None


def prereg_scelle(prereg, dossier_sortie):
    """(préenregistrement scellé, son empreinte) : `<dossier_sortie>/prereg-court.json`, fichier régulier atteint sans suivre
    de lien, d'empreinte égale à son compagnon `.sha256`, et de contenu égal (après passage par JSON) au préenregistrement
    passé. `PreregNonScelle` sinon."""
    octets = lire_regulier(dossier_sortie, NOM_PREREG, TAILLE_MAX_PREREG) if isinstance(dossier_sortie, str) else None
    if octets is None:
        raise PreregNonScelle(f"{NOM_PREREG} absent du dossier de la fiche, lien, non régulier ou au-delà de "
                              f"{TAILLE_MAX_PREREG >> 20} Mo : le verdict ne se calcule que sur le préenregistrement scellé")
    empreinte = hashlib.sha256(octets).hexdigest()
    if _empreinte_scellee(dossier_sortie, NOM_PREREG) != empreinte:
        raise PreregNonScelle(f"sceau de {NOM_PREREG} absent ou faux (compagnon .sha256) : préenregistrement non scellé")
    try:
        scelle = json.loads(octets.decode("utf-8"))
        passe = json.loads(json.dumps(prereg, ensure_ascii=False, sort_keys=True, allow_nan=False))
    except (UnicodeDecodeError, ValueError, TypeError) as x:
        raise PreregNonScelle(f"préenregistrement illisible ou non sérialisable : {x}") from None
    if scelle != passe:
        raise PreregNonScelle(f"le préenregistrement passé diffère de {NOM_PREREG} scellé (empreinte {empreinte[:12]}…) : "
                              "aucun verdict sur un préenregistrement changé après scellement")
    return scelle, empreinte


# --- verdict du noyau -----------------------------------------------------------------------------------------------------


def derniere_execution_reussie(executions):
    """La dernière exécution de statut « réussie » (code 0, non tuée, ni limite dépassée, ni données altérées), ou None."""
    for e in reversed(list(executions or [])):
        if isinstance(e, dict) and e.get("statut") == "réussie":
            return e
    return None


def lire_fichier_brut(dossier_sortie, execution, bloc):
    """(valeur, None, info) ou (None, motif, info) : la statistique du préenregistrement calculée par le noyau sur la copie
    scellée du fichier brut produit par `execution`. `info` = {copie, sha256, octets} dès que la copie est lue, sinon None."""
    numero = execution.get("numero")
    if isinstance(numero, bool) or not isinstance(numero, int) or numero < 0:
        return None, f"exécution sans numéro utilisable ({numero!r}) : copie introuvable", None
    fichier = bloc["fichier"]
    entrees = [p for p in execution.get("fichiers_produits") or [] if isinstance(p, dict) and p.get("chemin") == fichier]
    if not entrees:
        return None, (f"fichier attendu absent : {fichier!r} n'est pas parmi les fichiers réguliers produits par l'exécution "
                      f"{numero} (dernière réussie) ; le préenregistrement le nomme"), None
    if len(entrees) > 1:
        return None, f"inventaire de l'exécution {numero} incohérent : {fichier!r} y figure {len(entrees)} fois", None
    entree, copie = entrees[0], "produits/" + nom_copie(fichier)
    if entree.get("copie_scellee") is not True:
        return None, (f"fichier {fichier!r} produit mais non copié par le noyau (au-delà de {TAILLE_MAX_COPIE_PRODUIT >> 20} Mo, "
                      f"nom trop long ou au-delà des {MAX_COPIES_PRODUITS} premiers produits) : illisible pour le noyau"), None
    if entree.get("copie") != copie:
        return None, (f"inventaire de l'exécution {numero} incohérent : copie de {fichier!r} inscrite sous "
                      f"{entree.get('copie')!r}, attendue sous {copie!r}"), None
    relatif = f"execution-{numero:02d}/{copie}"
    octets = lire_regulier(dossier_sortie, relatif, TAILLE_MAX_COPIE_PRODUIT)
    if octets is None:
        return None, f"copie {relatif} absente, lien, fichier non régulier ou trop grosse : illisible pour le noyau", None
    empreinte = hashlib.sha256(octets).hexdigest()
    info = {"copie": relatif, "sha256": empreinte, "octets": len(octets)}
    if empreinte != entree.get("sha256"):
        return None, (f"copie {relatif} altérée : empreinte {empreinte[:12]}… ≠ empreinte de l'inventaire de l'exécution "
                      f"{str(entree.get('sha256'))[:12]}…"), info
    if _empreinte_scellee(dossier_sortie, relatif) != empreinte:
        return None, f"sceau de la copie {relatif} absent ou faux (compagnon .sha256)", info
    try:
        texte = octets.decode("utf-8")
    except UnicodeDecodeError:
        return None, f"fichier {fichier!r} illisible : UTF-8 attendu", info
    try:
        valeur, motif = statistique_de_colonne(texte, bloc["colonne"], bloc["statistique"])
    except csv.Error as x:
        return None, f"fichier {fichier!r} illisible (CSV) : {x}", info
    except OverflowError as x:
        return None, f"statistique « {bloc['statistique']} » non finie (dépassement : {x})", info
    if valeur is None:
        return None, f"fichier {fichier!r}, colonne {bloc['colonne']!r} : {motif}", info
    if not math.isfinite(valeur):
        return None, f"statistique « {bloc['statistique']} » non finie ({valeur!r})", info
    return valeur, None, info


def concordance_du_temoin(chiffre, ligne, valeur):
    """Vrai si le chiffre imprimé par le script est la valeur du noyau à l'arrondi d'affichage près (tolérance de la v2), faux
    sinon ; None s'il manque l'un des deux. Consignée, jamais décisive."""
    if chiffre is None or valeur is None:
        return None
    tolerance = _v2._tolerance_d_affichage(ligne)
    tolerance = 1e-9 * max(1.0, abs(valeur)) if tolerance is None else tolerance
    return abs(chiffre - valeur) <= tolerance


def calcul_du_script(execution, bloc):
    """Les lignes `CALCUL:` de l'exécution lue, consignées et ignorées : [{ligne, lu, differe_du_prereg, statut}]."""
    sortie = []
    for ligne in execution.get("lignes_calcul") or []:
        lu, _ = lire_ligne_calcul(ligne)
        sortie.append({"ligne": ligne, "lu": lu, "differe_du_prereg": lu != bloc, "statut": STATUT_CALCUL_DU_SCRIPT})
    return sortie


def verdict_du_noyau(prereg, dossier_sortie, executions):
    """Le verdict d'une fiche, calculé par le noyau depuis le fichier brut (R-1057).

    `prereg` : le préenregistrement court (contrat du module) ; `dossier_sortie` : le dossier de la fiche dans la sortie de
    l'étage (`prereg-court.json` scellé, `execution-NN/produits/…` scellés) ; `executions` : les exécutions de la fiche, au
    format de l'étage v2 (`numero`, `statut`, `lignes_resultat`, `lignes_calcul`, `fichiers_produits`).

    Rend {verdict, valeur_noyau, declaration, seuil, execution, fichier_brut, chiffre_script, ligne_script, concordance_script,
    verdict_selon_chiffre_script, calcul_du_script, motif, etiquette, prereg_sha256, version_etage}. Lève `PreregSansStatistique`,
    `PreregSansSeuil` ou `PreregNonScelle` (jamais de repli sur le chiffre du script)."""
    if not isinstance(prereg, dict):
        raise PreregSansStatistique("préenregistrement absent ou non objet : aucun verdict (aucun repli sur le chiffre du script)")
    if isinstance(dossier_sortie, os.PathLike):
        dossier_sortie = os.fspath(dossier_sortie)
    bloc, motif = lire_bloc_statistique(prereg.get(CLE_STATISTIQUE))
    if bloc is None:
        raise PreregSansStatistique(f"préenregistrement sans bloc « statistique » utilisable ({motif}) : aucun verdict, aucun "
                                    "repli sur le chiffre du script (R-1057)")
    seuil, comparateur = lire_seuil_du_prereg(prereg)
    _, prereg_sha256 = prereg_scelle(prereg, dossier_sortie)
    r = {"verdict": "non concluant", "valeur_noyau": None, "declaration": dict(bloc),
         "seuil": {"valeur": seuil, "comparateur": comparateur}, "execution": None, "fichier_brut": None,
         "chiffre_script": None, "ligne_script": None, "concordance_script": None, "verdict_selon_chiffre_script": None,
         "calcul_du_script": [], "motif": None, "etiquette": ETIQUETTE_NOYAU, "prereg_sha256": prereg_sha256,
         "version_etage": VERSION_ETAGE}
    e = derniere_execution_reussie(executions)
    if e is None:
        return dict(r, motif="aucune exécution réussie (code 0, non tuée) : aucun fichier brut à lire")
    numero = e.get("numero")
    if isinstance(numero, bool) or not isinstance(numero, int) or numero < 0:
        return dict(r, motif=f"dernière exécution réussie sans numéro utilisable ({numero!r}) : copie introuvable")
    chiffre, ligne, _ = chiffre_lu([e])  # témoin seulement
    r.update(execution=numero, chiffre_script=chiffre, ligne_script=ligne, calcul_du_script=calcul_du_script(e, bloc))
    if chiffre is not None:
        r["verdict_selon_chiffre_script"] = "survit" if comparer(chiffre, comparateur, seuil) else "éliminée"
    valeur, motif, info = lire_fichier_brut(dossier_sortie, e, bloc)
    r["fichier_brut"] = info
    if valeur is None:
        return dict(r, motif=motif)
    survit = comparer(valeur, comparateur, seuil)
    concordance = concordance_du_temoin(chiffre, ligne, valeur)
    temoin = ("aucun chiffre imprimé" if chiffre is None else
              f"chiffre imprimé {chiffre:g} ({'concordant' if concordance else 'DISCORDANT'}, témoin seulement)")
    r.update(verdict="survit" if survit else "éliminée", valeur_noyau=valeur, concordance_script=concordance,
             motif=(f"{bloc['statistique']} de {bloc['fichier']}[{bloc['colonne']}] (exécution {r['execution']}, copie scellée) "
                    f"= {valeur:g} ; {valeur:g} {comparateur} {seuil:g} : {'vrai' if survit else 'faux'} ; {temoin}"
                    + (" ; ligne CALCUL: du script ignorée" if r["calcul_du_script"] else "")))
    return r


def ecrire_verdict_du_noyau(dossier_sortie, verdict):
    """Consigne le verdict du noyau, scellé, dans `<dossier_sortie>/verdict-noyau-v4.json` (jamais d'écrasement) ; rend
    l'empreinte. Refuse un verdict sans l'étiquette du noyau (`VerdictNonNoyau`) ou hors des trois mots (`VerdictInconnu`)."""
    if not isinstance(verdict, dict) or verdict.get("etiquette") != ETIQUETTE_NOYAU:
        raise VerdictNonNoyau("seul un verdict calculé par le noyau (étiquette du noyau) se consigne ici")
    rang_verdict(verdict.get("verdict"))
    return ecrire_json_scelle(os.path.join(dossier_sortie, NOM_VERDICT), verdict)


# --- ordre et sélection ---------------------------------------------------------------------------------------------------


def rang_verdict(verdict):
    """Ordre total des verdicts : non concluant (0) < éliminée (1) < survit (2). « non concluant » n'est jamais mieux traité
    qu'« éliminée » (R-1057) ; un verdict hors des trois mots lève `VerdictInconnu` (aucun rang par défaut)."""
    if verdict == "survit":
        return 2
    if verdict == "éliminée":
        return 1
    if verdict == "non concluant":
        return 0
    raise VerdictInconnu(f"verdict inconnu : {verdict!r} (permis : {', '.join(ORDRE_DES_VERDICTS)})")


def selectionner(verdicts):
    """Les verdicts retenus pour la génération suivante, dans l'ordre reçu : ceux de verdict « survit » **seulement** ;
    « éliminée » et « non concluant » sortent tous deux. Chaque entrée doit être un verdict du noyau (`verdict_du_noyau` :
    étiquette du noyau, sinon `VerdictNonNoyau`) de verdict connu (sinon `VerdictInconnu`) ; tout est vérifié avant de rendre."""
    retenus = []
    for v in verdicts:
        if not isinstance(v, dict) or v.get("etiquette") != ETIQUETTE_NOYAU:
            raise VerdictNonNoyau("la sélection ne lit que des verdicts calculés par le noyau depuis le fichier brut "
                                  f"(étiquette reçue : {(v.get('etiquette') if isinstance(v, dict) else type(v).__name__)!r})")
        if rang_verdict(v.get("verdict")) == rang_verdict("survit"):
            retenus.append(v)
    return retenus
