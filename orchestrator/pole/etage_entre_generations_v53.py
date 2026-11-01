"""Étage de tests de mort **dans** la course, entre deux générations (R-636, R-640) — v53.

L'étage lui-même est **inchangé** : `pole/tests_de_mort_v3.py` (v52b, la version 2 avec la borne mémoire de 768 Mo) et sa
fonction `executer_tests_de_mort`. La v53 ajoute seulement :

1. **Machine jetable exigée (R-640, option (b))** : l'étage n'est lancé que si la variable d'environnement
   `POLE_MACHINE_JETABLE_V53` vaut exactement `1` (posée par l'opérateur sur la machine louée jetable, sans aucun secret,
   détruite après chaque série). Aucune valeur de variable n'est lue d'autre que celle-là ; les **noms** des variables de
   l'environnement sont parcourus pour refuser l'étage si un nom de clé y figure (`relais.noms_de_cle_presents` : noms
   seulement, jamais une valeur). Sinon `MachineNonJetable`, avant tout appel et toute écriture.
2. **Format de l'étage** : la génération est écrite dans un dossier neuf au format que l'étage lit (`manifeste-depart.json`
   avec `reglages.tests_de_mort`, `classement.json`, `fiches-validees.json`, tous scellés) ; les fiches du texte I sont
   **projetées** sur les champs que l'étage lit (`nom`, `enonce`, `loi_predictive.prediction|signe|metrique`,
   `test_de_mort`) par une **correspondance injectée** (aucun champ inventé : un champ absent laisse la fiche sans test,
   l'étage la refuse avec son motif). Les fiches retenues sont les mieux classées (`eligible` = notable selon la règle
   d'agrégation de la configuration), dans l'ordre du classement, prises par l'étage lui-même (N-053 : aucune sélection
   sur le verdict de l'étage).
"""

import os

from .outils import EcrasementInterdit, ecrire_json_scelle
from .relais import noms_de_cle_presents

VERSION = "etage-entre-generations-v53"
VARIABLE_MACHINE_JETABLE = "POLE_MACHINE_JETABLE_V53"
NOMS_DE_CLE_EN_PLUS = ("KIMI_API_KEY", "MOONSHOT_API_KEY")
SUFFIXES_DE_CLE = ("_API_KEY", "_TOKEN", "_SECRET", "_SECRET_KEY")  # noms seulement, jamais une valeur
CHAMPS_CORRESPONDANCE = ("nom", "enonce", "prediction", "signe", "metrique", "test_de_mort")


class MachineNonJetable(RuntimeError):
    pass


class CorrespondanceRefusee(ValueError):
    pass


def exiger_machine_jetable(environnement=None):
    env = os.environ if environnement is None else environnement
    if env.get(VARIABLE_MACHINE_JETABLE) != "1":
        raise MachineNonJetable(f"étage de tests de mort refusé : {VARIABLE_MACHINE_JETABLE}=1 absent (R-640 : l'étage ne tourne "
                                "que sur une machine louée jetable, sans secret, détruite après chaque série)")
    presents = set(noms_de_cle_presents(env)) | {n for n in env if n in NOMS_DE_CLE_EN_PLUS or n.endswith(SUFFIXES_DE_CLE)}
    if presents:
        raise MachineNonJetable("étage de tests de mort refusé : un nom de variable de clé est présent dans l'environnement ("
                                + ", ".join(sorted(presents)) + ") ; la machine jetable ne porte aucun secret")
    return True


def valider_correspondance(corr):
    if not isinstance(corr, dict) or set(corr) != set(CHAMPS_CORRESPONDANCE) or not all(isinstance(v, str) and v for v in corr.values()):
        raise CorrespondanceRefusee(f"correspondance des champs pour l'étage : exactement {CHAMPS_CORRESPONDANCE} (chemins dans la "
                                    "fiche du texte I), aucun défaut")
    return corr


def _lire(contenu, chemin):
    v = contenu
    for k in chemin.split("."):
        if not isinstance(v, dict) or k not in v:
            return None
        v = v[k]
    return v


def projeter(fiche, corr):
    c = fiche["contenu"]
    p = {"identifiant_auteur": fiche["ident"], "empreinte": fiche["empreinte"], "nom": _lire(c, corr["nom"]),
         "enonce": _lire(c, corr["enonce"]),
         "loi_predictive": {"prediction": _lire(c, corr["prediction"]), "signe": _lire(c, corr["signe"]),
                            "metrique": _lire(c, corr["metrique"])}}
    t = _lire(c, corr["test_de_mort"])
    if t is not None:
        p["test_de_mort"] = t
    return p


def preparer_generation(dossier, classement, fiches_par_ident, *, nombre, tranche_index_sha256, correspondance, lisible):
    """Écrit le dossier de génération au format de l'étage ; rend son chemin. `classement` : lignes du classement agrégé."""
    valider_correspondance(correspondance)
    if os.path.exists(dossier):
        raise EcrasementInterdit(f"dossier de génération pour l'étage {dossier} déjà présent (R12)")
    os.makedirs(dossier)
    ecrire_json_scelle(os.path.join(dossier, "manifeste-depart.json"), {
        "version": VERSION, "reglages": {"tests_de_mort": {"nombre": nombre, "tranche_index_sha256": tranche_index_sha256}}})
    lignes = [{"identifiant_auteur": l["ident"], "eligible": bool(l["notable"]), "rang": l["rang"],
               "empreinte": fiches_par_ident[l["ident"]]["empreinte"]} for l in classement]
    ecrire_json_scelle(os.path.join(dossier, "classement.json"), {"lisible_L2_L4": bool(lisible), "lignes": lignes,
                                                                   "regle": "classement agrégé de la génération (v53)"})
    ecrire_json_scelle(os.path.join(dossier, "fiches-validees.json"),
                       [projeter(fiches_par_ident[l["ident"]], correspondance) for l in classement])
    return dossier


def jouer_etage(adaptateur, dossier_generation, *, reglages, environnement=None, executer=None):
    """Machine jetable vérifiée, puis l'étage v3 inchangé. `reglages` : arguments nommés de `executer_tests_de_mort`
    (tranche chargée, nombre, expérimentateur, lecteur, plafonds, exécuteur…), tous injectés."""
    exiger_machine_jetable(environnement)
    if executer is None:
        from .tests_de_mort_v3 import executer_tests_de_mort as executer
    resume = {}
    executer(adaptateur, dossier_generation, resume_sortie=resume, **reglages)
    return resume
