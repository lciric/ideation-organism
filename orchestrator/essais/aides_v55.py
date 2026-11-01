"""Aides des essais de la v55 : configurations d'essai au format v55 (valeurs **d'essai** seulement, aucune recommandée ni
gelée) — annexe du bras méta avec brouillon relu et rapport de contre-lecture (I-9 v55), liste de réduction d'É9 scellée,
résultats externes scellés liés à un script empreinté, nombres ajoutés au rendu (S6), moteur simulé v55."""

import json
import os

import aides_v54 as A54
from pole.outils import ecrire_json_scelle, ecrire_scelle, sha256_fichier
from pole.simulation_v55 import AdaptateurSimuleV55

CHAMPS, ITEMS, SUPPRIMER, INTERDITES = A54.CHAMPS, A54.ITEMS, A54.SUPPRIMER, A54.INTERDITES
ecrire, ligne_go, registre_go, EtageUnFactice = A54.ecrire, A54.ligne_go, A54.registre_go, A54.EtageUnFactice
EXTERNES = ("8", "9", "10", "17", "19")


def annexe_v55(dossier, nom="annexe-bras-meta-essai-v55.md", **modifs):
    """Brouillon relu (champs libres « À REMPLIR »), rapport, puis annexe qui cite les deux empreintes : rend les trois pièces."""
    d = os.path.join(dossier, "annexe-v55")
    os.makedirs(d, exist_ok=True)
    relu = A54.annexe_meta(d, nom="brouillon-relu.md", sceller=False, contre_lecture="À REMPLIR", approbation_lazar="À REMPLIR", **modifs)
    rapport = ecrire(os.path.join(d, "rapport-contre-lecture.md"), "Rapport de contre-lecture d'essai (aucune valeur réelle).")
    annexe = A54.annexe_meta(d, nom=nom, contre_lecture=f"essai : brouillon relu {relu['sha256']} ; rapport {rapport['sha256']}",
                             approbation_lazar="essai : R-901, 2026-10-31", **modifs)
    return annexe, relu, rapport


def avec_annexe_v55(conf, dossier, **modifs):
    annexe, relu, rapport = annexe_v55(dossier, **modifs)
    conf["bisociateur"]["meta"]["annexe"] = dict(annexe, brouillon_relu=relu, rapport_contre_lecture=rapport)
    return conf


def configuration(dossier, **modifs):
    conf = avec_annexe_v55(A54.configuration(dossier), dossier)
    for chemin, valeur in modifs.items():
        d = conf
        morceaux = chemin.split("__")
        for k in morceaux[:-1]:
            d = d[k]
        if valeur is SUPPRIMER:
            d.pop(morceaux[-1], None)
        else:
            d[morceaux[-1]] = valeur
    return conf


def adaptateurs(cout=0.01, **decideurs):
    return {n: AdaptateurSimuleV55(champs_fiche=CHAMPS, items=ITEMS, cout_par_appel_usd=cout, champ_titre="titre",
                                   decider=decideurs.get(n)) for n in ("kimi", "argon", "claude")}


def piece_scellee(dossier, nom, objet):
    chemin = os.path.join(dossier, nom)
    os.makedirs(dossier, exist_ok=True)
    if os.path.exists(chemin):  # même dossier d'essai : réutilisée si le contenu est le même, jamais réécrite autrement
        with open(chemin, encoding="utf-8") as f:
            if json.load(f) != objet:
                raise FileExistsError(f"{chemin} : contenu différent (choisir un autre dossier)")
        return {"chemin": chemin, "sha256": sha256_fichier(chemin)}
    ecrire_json_scelle(chemin, objet)
    return {"chemin": chemin, "sha256": sha256_fichier(chemin)}


def avec_externes(dossier, conf, lignes=EXTERNES, **alterations):
    """Résultats externes d'essai : pièce scellée {ligne, identifiant, cas_sain, artefact, script, script_sha256}."""
    d = os.path.join(dossier, "ext-v55")
    if "script_garde" not in conf["pieces"]:
        conf["pieces"]["script_garde"] = ecrire(os.path.join(d, "script-garde-essai.py"), "# script de garde d'essai\n")
    decl = {}
    for n in lignes:
        res = {"ligne": n, "identifiant": f"R5-{n}-essai", "cas_sain": "passe", "artefact": "arrete", "script": "script_garde",
               "script_sha256": conf["pieces"]["script_garde"]["sha256"]}
        res.update(alterations.get(n, {}))
        nom = f"garde_{n}"
        chemin = os.path.join(d, f"g{n}.json")
        if os.path.exists(chemin):
            os.remove(chemin)
            os.remove(chemin + ".sha256")
        conf["pieces"][nom] = piece_scellee(d, f"g{n}.json", res)
        decl[n] = {"piece": nom, "identifiant": f"R5-{n}-essai"}
    conf["prepilote"]["gardes_externes"] = decl
    return conf


def configuration_pre_pilote(dossier, plafond=60.0, **modifs):
    conf = avec_annexe_v55(A54.configuration_pre_pilote(dossier, plafond=plafond), dossier)
    conf["prepilote"]["s6"]["nombres_ajoutes_max"] = 0
    conf["pieces"]["liste_reduite_e9"] = piece_scellee(os.path.join(dossier, "pp-v55"), "liste-reduite-e9.json", {"idents": ["a0", "a2"]})
    conf["prepilote"]["anteriorite"]["liste_reduite"] = "liste_reduite_e9"
    for chemin, valeur in modifs.items():
        x = conf
        morceaux = chemin.split("__")
        for k in morceaux[:-1]:
            x = x[k]
        if valeur is SUPPRIMER:
            x.pop(morceaux[-1], None)
        else:
            x[morceaux[-1]] = valeur
    return conf


__all__ = ("configuration", "configuration_pre_pilote", "avec_externes", "adaptateurs", "annexe_v55", "piece_scellee")
_ = ecrire_scelle
