"""Étage entre générations, version 57 (orchestrateur v57b) — le **point de sélection** entre deux générations, au-dessus de la
v56 (`pole/etage_entre_generations_v56.py`, inchangée, R12 : machine jetable par liste blanche, CL20-14, reprise telle quelle).

Constat (v57b, en cherchant où les survivantes sont choisies) : jusqu'à la v56, **aucun code ne choisissait sur le verdict des
tests de mort**. `jouer_etage_v56` rendait le résumé de l'étage v3 ; `course2_v56.executer_course_v56` le rangeait dans le bilan
de la course ; l'héritage servi à la génération suivante (`texte_heritage`) vient du classement des juges, écrit **avant**
l'étage. `selectionner` (v4) n'avait donc aucun appelant, et aucun point n'existait où l'appeler : la v57 le crée ici.

Ce que la version 57 fait :

1. **L'étage joué** entre deux générations est la version 5 (`tests_de_mort_v5.executer_tests_de_mort`, R-1057 : verdict
   calculé par le noyau depuis le fichier brut, incidents compris), après la machine jetable de la v56 (`exiger_machine_jetable_v56`).
2. **La sélection** (`selection_entre_generations`) : les verdicts du noyau des fiches testées passent par `selectionner` (v4)
   et **par lui seulement** ; seules les fiches de verdict « survit » sont retenues ; « éliminée », « non concluant » et les
   fiches non testées (refusées à l'étage) sortent, motif dit. **Tout verdict sans l'étiquette du noyau est refusé**
   (`VerdictNonNoyau`, levé par `selectionner` : un résumé de l'étage v3, dont le verdict vient du chiffre imprimé, est refusé),
   ainsi que toute fiche dont le verdict affiché diffère du verdict du noyau qu'elle porte (`VerdictNonNoyau`). Un refus arrête
   l'appelant : aucune sélection partielle, aucun repli.
3. La sélection est écrite, scellée, dans le dossier de génération de l'étage (`selection-entre-generations-v57.json`, jamais
   d'écrasement) et rendue dans le résumé (`resume["selection"]`, avec son empreinte).

Non fait (dit, pour qu'on ne lise pas la boucle comme fermée) : la génération suivante **ne lit pas** la sélection — l'héritage
de `course2_v57` reste celui de la v56 (classement des juges, toutes fiches classées) ; faire entrer les seules survivantes (ou
leur verdict) dans ce que lit la génération suivante change ce que voient les proposeurs : c'est une décision du directeur.
"""

import os

from .etage_entre_generations_v56 import exiger_machine_jetable_v56
from .outils import ecrire_json_scelle
from .tests_de_mort_v4 import VerdictNonNoyau, selectionner

VERSION = "etage-entre-generations-v57"
NOM_SELECTION = "selection-entre-generations-v57.json"
REGLE_SELECTION = ("R-1057 : seules les fiches testées dont le verdict calculé par le noyau est « survit » sont retenues, par "
                   "`selectionner` seulement ; « éliminée », « non concluant » et les fiches non testées sortent (ordre : non "
                   "concluant < éliminée < survit) ; tout verdict sans l'étiquette du noyau, ou différent du verdict du noyau que "
                   "porte la fiche, est refusé (arrêt, aucune sélection partielle, aucun repli) ; la génération suivante ne lit "
                   "pas encore cette sélection (v57b)")


def selection_entre_generations(resume):
    """La sélection pour la génération suivante depuis le résumé de l'étage (v5) : {version, version_etage, retenues
    (identifiants, dans l'ordre du classement), exclues [{identifiant_auteur, verdict, motif}], regle}. Les verdicts des fiches
    testées passent par `selectionner` seulement (qui lève `VerdictNonNoyau` sans l'étiquette du noyau, `VerdictInconnu` hors des
    trois mots) ; une fiche testée dont `verdict` diffère de `verdict_noyau["verdict"]` lève `VerdictNonNoyau`."""
    if not isinstance(resume, dict) or not isinstance(resume.get("par_fiche"), list):
        raise VerdictNonNoyau("résumé de l'étage absent ou sans « par_fiche » : aucune sélection (aucun repli)")
    verdicts, lignes = [], []  # lignes : (identifiant, verdict du noyau ou None si non testée, motif de non-test)
    for r in resume["par_fiche"]:
        ident = r.get("identifiant_auteur")
        if r.get("statut") != "testée":
            lignes.append((ident, None, f"non testée ({r.get('statut')} : {r.get('motif')})"))
            continue
        v = r.get("verdict_noyau")
        if isinstance(v, dict) and r.get("verdict") != v.get("verdict"):
            raise VerdictNonNoyau(f"fiche {ident} : verdict « {r.get('verdict')} » ≠ verdict du noyau qu'elle porte "
                                  f"(« {v.get('verdict')} ») : refusé, aucune sélection")
        verdicts.append(v)
        lignes.append((ident, v, None))
    retenus = {id(v) for v in selectionner(verdicts)}  # « survit » seulement ; étiquette du noyau exigée de chaque verdict
    return {"version": VERSION, "version_etage": resume.get("version_etage"),
            "retenues": [i for i, v, _ in lignes if v is not None and id(v) in retenus],
            "exclues": [{"identifiant_auteur": i, "verdict": None if v is None else v["verdict"],
                         "motif": m if v is None else v.get("motif")} for i, v, m in lignes if v is None or id(v) not in retenus],
            "regle": REGLE_SELECTION}


def jouer_etage_v57(adaptateur, dossier_generation, *, reglages, environnement=None, executer=None, permis_en_plus=()):
    """Machine jetable (v56), puis l'étage v5 (`executer` : injectable, essais), puis la sélection ; rend le résumé de l'étage
    augmenté de `selection` (la sélection, son fichier et son empreinte). Une sélection refusée lève (`VerdictNonNoyau`,
    `VerdictInconnu`) après l'étage, sans rien écrire de la sélection."""
    exiger_machine_jetable_v56(environnement, permis_en_plus)
    if executer is None:
        from .tests_de_mort_v5 import executer_tests_de_mort as executer
    resume = {}
    executer(adaptateur, dossier_generation, resume_sortie=resume, **reglages)
    selection = selection_entre_generations(resume)
    sha256 = ecrire_json_scelle(os.path.join(dossier_generation, NOM_SELECTION), selection)
    resume["selection"] = dict(selection, fichier=NOM_SELECTION, sha256=sha256)
    return resume


__all__ = ("selection_entre_generations", "jouer_etage_v57", "NOM_SELECTION", "REGLE_SELECTION", "VERSION")
