"""Course 2, version 59 (fichier neuf, R12 ; tâche A2) — `course2_v57` avec **la boucle fermée** : la génération g+1 lit la
sélection scellée de la génération g.

En v57, l'héritage servi à la génération suivante était `GenerationV56.texte_heritage` (classement des juges, écrit avant
l'étage) et la sélection n'était lue par personne. En v59 :

1. Plus d'une génération **exige** l'étage de tests de mort (`etage`) : sans étage, aucune sélection n'existe, la course est
   refusée avant toute génération (`ConfigurationRefusee`) — aucun héritage du classement des juges.
2. Après la génération g, l'étage v57 (machine jetable v56, étage v5, sélection scellée) est joué ; l'héritage de la génération
   g+1 est `heritage_depuis_selection` : le fichier de sélection (`selection-entre-generations-v57.json`) lu **après
   vérification** de son sceau et de l'empreinte que l'étage de la génération g a consignée (`boucle_fermee_v59.
   lire_scelle_verifie`), puis les fiches de l'étage (`fiches-validees.json`, sceau vérifié) ; seules les retenues
   (« survit », verdict du noyau) sont servies, par nom et énoncé. Une sélection refusée arrête la course (motif au bilan).
3. Le bilan de la course porte, par génération, l'empreinte de la sélection lue par la suivante (`heritage_lu`).

Inchangé : les générations (`GenerationV56`), la mémoire, les refus d'avant toute génération de la v57.
"""

import os

from .boucle_fermee_v59 import HeritageRefuse, lire_scelle_verifie
from .configuration_v53 import ConfigurationRefusee
from .course2_v56 import GenerationV56
from .noyau_v54 import NoeudArret
from .noyau_v56 import ArretSurSignal, motif_arret
from .outils import EcrasementInterdit, ecrire_json_scelle, verifier_scelle

VERSION = "course-2-generation-v59"


def heritage_depuis_selection(dossier_etage, sha256_selection):
    """Le texte d'héritage de la génération suivante, depuis la sélection scellée de l'étage (empreinte vérifiée avant
    lecture) : les seules fiches retenues, par nom et énoncé. Lève `SelectionNonVerifiee` ou `HeritageRefuse`."""
    from .etage_entre_generations_v57 import NOM_SELECTION
    from .etage_entre_generations_v57 import VERSION as VERSION_SELECTION
    selection = lire_scelle_verifie(os.path.join(dossier_etage, NOM_SELECTION), sha256_selection, "sélection de l'étage")
    if selection.get("version") != VERSION_SELECTION or not isinstance(selection.get("retenues"), list):
        raise HeritageRefuse("sélection d'une autre version que l'étage entre générations v57 : refus")
    chemin_fiches = os.path.join(dossier_etage, "fiches-validees.json")
    if not verifier_scelle(chemin_fiches):
        raise HeritageRefuse("fiches de l'étage : sceau absent ou faux : refus")
    import json
    with open(chemin_fiches, encoding="utf-8") as f:
        fiches = {x["identifiant_auteur"]: x for x in json.load(f)}
    absentes = [i for i in selection["retenues"] if i not in fiches]
    if absentes:
        raise HeritageRefuse(f"retenue(s) absente(s) des fiches de l'étage : {absentes} : refus")
    lignes = ["# Héritage : fiches retenues par la sélection scellée de la génération précédente (tests de mort : « survit », "
              f"verdict calculé par le noyau ; empreinte de la sélection {sha256_selection})\n"]
    lignes += [f"- {fiches[i].get('nom')} : {fiches[i].get('enonce')}" for i in selection["retenues"]] or ["- (aucune fiche retenue)"]
    return "\n".join(lignes) + "\n"


def executer_course_v59(conf, sortie, adaptateurs, *, nombre_generations, go, etage=None, environnement=None, horloge=None,
                        racine_sessions=None, portes=None, specification=None):
    """Comme `course2_v57.executer_course_v57`, mais l'héritage de la génération g+1 est lu dans la sélection scellée de la
    génération g (`heritage_depuis_selection`) ; plus d'une génération sans étage est refusé."""
    from .etage_entre_generations_v53 import preparer_generation
    from .etage_entre_generations_v56 import exiger_machine_jetable_v56
    from .etage_entre_generations_v57 import jouer_etage_v57
    if isinstance(nombre_generations, bool) or not isinstance(nombre_generations, int) or nombre_generations < 1:
        raise ConfigurationRefusee("nombre de générations : entier ≥ 1, aucun défaut")
    if nombre_generations > 1 and etage is None:
        raise ConfigurationRefusee("course v59 : plus d'une génération exige l'étage de tests de mort — la génération suivante lit "
                                   "la sélection scellée de la précédente ; aucun héritage du classement des juges (aucun repli)")
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
                         "c13_satisfaite": gen.budget.etat()["c13_satisfaite"], "noeud": gen.noeud, "heritage_lu": None}
                if gen.noeud:
                    noeud = f"génération {g} : {gen.noeud}"
                    bilan.append(ligne)
                    break
                memoire = gen.memoire
                if g < nombre_generations:
                    d = preparer_generation(os.path.join(sortie, f"etage-apres-generation-{g}"), resultat, gen.fiches,
                                            nombre=etage["nombre"], tranche_index_sha256=etage["tranche_index_sha256"],
                                            correspondance=etage["correspondance"], lisible=gen.arret is None)
                    ligne["etage"] = jouer_etage_v57(etage["adaptateur"], d, reglages=etage["reglages"], environnement=environnement,
                                                     executer=etage.get("executer"), permis_en_plus=permis)
                    sha = ligne["etage"]["selection"]["sha256"]
                    heritage = heritage_depuis_selection(d, sha)  # la génération g+1 lit la sélection scellée (vérifiée)
                    ligne["heritage_servi_a_la_suivante"] = {"selection_sha256": sha, "retenues": ligne["etage"]["selection"]["retenues"]}
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


__all__ = ("executer_course_v59", "heritage_depuis_selection", "VERSION")
