"""Course 2, version 57 (orchestrateur v57b) — `course2_v56` inchangé (R12), sauf **l'étage entre deux générations** : la
course joue `etage_entre_generations_v57.jouer_etage_v57` (machine jetable de la v56, puis l'étage de tests de mort v5 — verdict
calculé par le noyau depuis le fichier brut, R-1057 —, puis la sélection par `selectionner`, qui refuse tout verdict sans
l'étiquette du noyau) au lieu de `jouer_etage_v56` (étage v3, verdict lu dans le chiffre imprimé). Les générations sont celles
de la v56 (`GenerationV56`), telles quelles.

Le bilan de la course (`bilan-course.json`, scellé) porte, pour chaque génération suivie d'un étage, le résumé de l'étage et sa
sélection (`etage.selection` : retenues, exclues, empreinte du fichier scellé). Une sélection refusée (`VerdictNonNoyau`,
`VerdictInconnu`) arrête la course après l'étage, motif au bilan (`arret`), aucune génération suivante.

Non fait : l'héritage servi à la génération suivante reste celui de la v56 (`texte_heritage` : classement des juges, écrit avant
l'étage) ; la sélection est calculée, scellée et consignée, mais **aucune génération ne la lit encore** (décision du directeur) ;
le lanceur `demonstrations/ideation_v8.py` appelle toujours `course2_v56`.
"""

import os

from .configuration_v53 import ConfigurationRefusee
from .course2_v56 import GenerationV56
from .noyau_v54 import NoeudArret
from .noyau_v56 import ArretSurSignal, motif_arret
from .outils import EcrasementInterdit, ecrire_json_scelle

VERSION = "course-2-generation-v57"


def executer_course_v57(conf, sortie, adaptateurs, *, nombre_generations, go, etage=None, environnement=None, horloge=None,
                        racine_sessions=None, portes=None, specification=None):
    """Comme `course2_v56.executer_course_v56` (mêmes arguments, mêmes refus avant toute génération, nœud : ni génération
    suivante, ni étage), avec l'étage entre générations de la v57 (`jouer_etage_v57` : étage v5 et sélection)."""
    from .etage_entre_generations_v53 import preparer_generation
    from .etage_entre_generations_v56 import exiger_machine_jetable_v56
    from .etage_entre_generations_v57 import jouer_etage_v57
    if isinstance(nombre_generations, bool) or not isinstance(nombre_generations, int) or nombre_generations < 1:
        raise ConfigurationRefusee("nombre de générations : entier ≥ 1, aucun défaut")
    permis = (conf.get("etage_tests_de_mort") or {}).get("environnement_permis") or ()
    if etage is not None:
        exiger_machine_jetable_v56(environnement, permis_en_plus=permis)
        for c in ("adaptateur", "reglages", "nombre", "tranche_index_sha256", "correspondance", "plafond_etage_usd"):
            if c not in etage:
                raise ConfigurationRefusee(f"étage entre générations : {c} manquant (aucun défaut)")
    if os.path.exists(sortie):
        raise EcrasementInterdit(f"sortie {sortie} déjà présente (R12)")
    os.makedirs(sortie)
    memoire, heritage, bilan, noeud, arret = None, None, [], None, None
    with ArretSurSignal() as garde:
        try:
            for g in range(1, nombre_generations + 1):
                rs = None if racine_sessions is None else os.path.join(racine_sessions, f"generation-{g}")
                gen = GenerationV56(conf, os.path.join(sortie, f"generation-{g}"), adaptateurs, numero=g, memoire=memoire,
                                    heritage_texte=heritage, go=go, horloge=horloge, racine_sessions=rs, portes=portes,
                                    specification=specification)
                resultat = gen.executer()
                ligne = {"generation": g, "fiches_classees": len(resultat), "notables": sum(l["notable"] for l in resultat),
                         "c13_satisfaite": gen.budget.etat()["c13_satisfaite"], "noeud": gen.noeud}
                if gen.noeud:
                    noeud = f"génération {g} : {gen.noeud}"
                    bilan.append(ligne)
                    break
                memoire, heritage = gen.memoire, gen.texte_heritage(resultat)
                if etage is not None and g < nombre_generations:
                    d = preparer_generation(os.path.join(sortie, f"etage-apres-generation-{g}"), resultat, gen.fiches,
                                            nombre=etage["nombre"], tranche_index_sha256=etage["tranche_index_sha256"],
                                            correspondance=etage["correspondance"], lisible=gen.arret is None)
                    ligne["etage"] = jouer_etage_v57(etage["adaptateur"], d, reglages=etage["reglages"], environnement=environnement,
                                                     executer=etage.get("executer"), permis_en_plus=permis)
                bilan.append(ligne)
        except BaseException as e:
            arret = motif_arret(e)
            raise
        finally:
            garde.nettoyage()
            ecrire_json_scelle(os.path.join(sortie, "bilan-course.json"), {"version": VERSION, "go": go, "generations": bilan,
                                                                           "noeud": noeud, "arret": arret, "signaux": garde.etat()})
    if noeud:
        raise NoeudArret(noeud)
    return bilan


__all__ = ("executer_course_v57", "VERSION")
