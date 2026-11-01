"""Aides des essais de la v56 : configurations d'essai au format v56 (valeurs **d'essai** seulement, aucune recommandée ni
gelée) — plan de dépense à plafonds de relais (`plafond_relais_usd`, CL20-02), D-i = 1 (CL20-07), M6b écrite par le rédacteur
en É1 sur une liste scellée de sources (CL20-08), moteur simulé v56, commande externe factice (CL20-01), spécification
scellée d'essai (CL20-03). Tout est écrit dans le dossier d'essai ; rien n'est lu hors de l'arbre."""

import json
import os
import sys

import aides_v55 as A55
from pole.outils import ecrire_json_scelle, ecrire_scelle, sha256_fichier
from pole.simulation_v56 import AdaptateurSimuleV56

CHAMPS, ITEMS, SUPPRIMER, INTERDITES = A55.CHAMPS, A55.ITEMS, A55.SUPPRIMER, A55.INTERDITES
ecrire, ligne_go, registre_go, EtageUnFactice = A55.ecrire, A55.ligne_go, A55.registre_go, A55.EtageUnFactice
piece_scellee, avec_externes, EXTERNES = A55.piece_scellee, A55.avec_externes, A55.EXTERNES


def vers_v56(conf, relais=None):
    """Plan de dépense v56 : `reservation_usd` → `plafond_relais_usd` (même valeur, sauf `relais` = {étape: plafond})."""
    for e in conf["budget"]["etapes"]:
        e["plafond_relais_usd"] = (relais or {}).get(e["nom"], e.pop("reservation_usd"))
        e.pop("reservation_usd", None)
        if isinstance(e.get("reduite"), dict):
            e["reduite"]["plafond_relais_usd"] = e["reduite"].pop("reservation_usd")
    return conf


def _modifier(conf, modifs):
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


def configuration(dossier, **modifs):
    return _modifier(vers_v56(A55.configuration(dossier)), modifs)


def sources_m6b(dossier, n=6, nom="m6b-sources-v56.json"):
    sources = [{"ident": f"s{i}", "titre": f"Titre Source Numéro {i}", "auteurs": [f"Auteur{i}"], "identifiant": f"10.0/src{i}",
                "extrait": f"Extrait servi au rédacteur, source {i} : une idée de méthode.", "pdf_sha256": format(i, "x") * 64}
               for i in range(n)]
    return piece_scellee(os.path.join(dossier, "pp-v56"), nom, {"sources": sources})


def configuration_pre_pilote(dossier, plafond=60.0, **modifs):
    conf = vers_v56(A55.configuration_pre_pilote(dossier, plafond=plafond))
    pp = conf["prepilote"]
    pp["d_i"] = 1
    conf["pieces"]["m6b_liste_sources"] = sources_m6b(dossier)
    conf["pieces"]["m6b_redaction"] = ecrire(os.path.join(dossier, "pp-v56", "redaction-m6b.md"),
                                             "Rédige une fiche d'idée à partir de la source, sans la nommer ; REFERENCES:5 (essai).")
    pp["m6b"] = {"liste_sources": "m6b_liste_sources", "consigne_redaction": "m6b_redaction", "consigne": "consigne_m6b",
                 "nombre": 4, "references_par_fiche": 5}
    return _modifier(conf, modifs)


def adaptateurs(cout=0.01, **decideurs):
    return {n: AdaptateurSimuleV56(champs_fiche=CHAMPS, items=ITEMS, cout_par_appel_usd=cout, champ_titre="titre",
                                   decider=decideurs.get(n)) for n in ("kimi", "argon", "claude")}


def commande_factice(dossier, nom, objet, code=0):
    """Script Python local qui imprime `objet` en JSON sur sa dernière ligne (commande externe factice, aucun réseau) ; rend la
    commande (liste)."""
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".py")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("import json, os, sys\nsys.stdin.read()\no = " + repr(objet) + "\n"
                "o.update({k: os.environ[v] for k, v in (('_etape', 'ETAPE_POLE'), ('_plafond_etape', 'PLAFOND_ETAPE_USD')) "
                "if v in os.environ})\nprint(json.dumps(o))\nsys.exit(" + str(int(code)) + ")\n")
    return [sys.executable, "-I", "-B", chemin]


def porte_factice(dossier, nom, accuse=None, code=0):
    """Commande de porte de plafond factice : accuse l'étape et le plafond reçus dans l'environnement (ou `accuse`)."""
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom + ".py")
    with open(chemin, "w", encoding="utf-8") as f:
        corps = ("o = {'etape': os.environ['ETAPE_POLE'], 'plafond_usd': float(os.environ['PLAFOND_ETAPE_USD'])}" if accuse is None
                 else "o = " + repr(accuse))
        f.write("import json, os, sys\n" + corps + "\nprint(json.dumps(o))\nsys.exit(" + str(int(code)) + ")\n")
    return [sys.executable, "-I", "-B", chemin]


def specification(dossier, *, marqueur=False, cite=True, sceller=True, nom="preenregistrement-essai-v56.md"):
    """Préenregistrement d'essai et sa contre-lecture, scellés ; rend {preenregistrement, contre_lecture}."""
    d = os.path.join(dossier, "spec-v56")
    os.makedirs(d, exist_ok=True)
    cl = os.path.join(d, "contre-lecture-essai.md")
    if not os.path.exists(cl):
        ecrire_scelle(cl, "Contre-lecture d'essai (aucune valeur réelle).\n")
    sha_cl = sha256_fichier(cl)
    texte = "# Préenregistrement d'essai\n\nPlan d'essai.\n" + (f"Contre-lecture : {sha_cl}\n" if cite else "") + \
            ("Seuil : À REMPLIR\n" if marqueur else "")
    p = os.path.join(d, nom)
    if sceller:
        ecrire_scelle(p, texte)
    else:
        with open(p, "w", encoding="utf-8") as f:
            f.write(texte)
    return {"preenregistrement": {"chemin": p, "sha256": sha256_fichier(p)}, "contre_lecture": {"chemin": cl, "sha256": sha_cl}}


__all__ = ("configuration", "configuration_pre_pilote", "vers_v56", "adaptateurs", "commande_factice", "porte_factice",
           "specification", "sources_m6b", "avec_externes", "piece_scellee")
_ = (ecrire_json_scelle, json)
