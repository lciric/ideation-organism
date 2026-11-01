"""Aides des essais de la v53 : pièces factices empreintées, annexe du bras méta scellée, source du substitut, configuration
complète (toutes valeurs **d'essai**, aucune n'est une recommandation ni un seuil gelé)."""

import json
import os

from pole.outils import ecrire_scelle, sha256_fichier

CHAMPS = ["titre", "hypothese", "axe", "methode"]
ITEMS = ["K1", "K2", "K3", "K4", "K5"]
INTERDITES = ["témoin", "exploratoire", "fusion", "bras méta", "gu krenn", "bisociation"]


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)
    return {"chemin": chemin, "sha256": sha256_fichier(chemin)}


def annexe_meta(dossier, sceller=True, **modifs):
    p = {"niches": ["n1", "n2", "n3"], "types_structure": ["objet_mathematique", "methode", "jeu_de_donnees"],
         "communication": {"n1|n2": 0.1, "n1|n3": 0.9, "n2|n3": 0.2}, "seuil_communication_faible": 0.3,
         "structure_forte": {"nombre_min": 1, "types": ["objet_mathematique", "methode"]},
         "eloignement": {"n1|n2": 2.0, "n1|n3": 5.0, "n2|n3": 1.0}, "bande": [1.5, 3.0], "poids": 0.5,
         "repli": "indicateurs_puis_structure", "contre_lecture": "essai : contre-lecture factice",
         "approbation_lazar": "essai : approbation factice"}
    p.update(modifs)
    texte = "# Annexe du bras méta (ESSAI)\n\n```json\n" + json.dumps({"parametres_bras_meta": p}, ensure_ascii=False) + "\n```\n"
    chemin = os.path.join(dossier, "annexe-bras-meta-essai.md")
    if os.path.exists(chemin) and not modifs:  # même dossier, même annexe : jamais réécrite (R12)
        return {"chemin": chemin, "sha256": sha256_fichier(chemin)}
    if sceller:
        ecrire_scelle(chemin, texte)
    else:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(texte)
    return {"chemin": chemin, "sha256": sha256_fichier(chemin)}


def source_gk(dossier):
    oeuvres = []
    concepts = ["c1", "c2", "c3", "c4", "c5", "c6"]
    for i in range(30):
        oeuvres.append({"date": "2025-01-0%d" % (1 + i % 9), "concepts": [concepts[i % 3]]})
        oeuvres.append({"date": "2025-02-0%d" % (1 + i % 9), "concepts": [concepts[3 + i % 3]]})
    oeuvres.append({"date": "2024-05-01", "concepts": ["c1", "c4"]})  # c1 et c4 reliés
    chemin = os.path.join(dossier, "source-gk-essai.json")
    return ecrire(chemin, json.dumps({"oeuvres": oeuvres}))


def configuration(dossier, **modifs):
    pieces = {
        "consigne_proposeur": ecrire(os.path.join(dossier, "p", "proposeur.md"), "Consigne proposeur (essai)."),
        "consigne_passe_tableau": ecrire(os.path.join(dossier, "p", "tableau.md"), "Consigne passe tableau (essai)."),
        "consigne_aiguilleur": ecrire(os.path.join(dossier, "p", "aiguilleur.md"), "AIGUILLEUR consigne figée (essai)."),
        "consigne_juge": ecrire(os.path.join(dossier, "p", "juge.md"), "JUGE consigne figée (essai)."),
        "consigne_fusion": ecrire(os.path.join(dossier, "p", "fusion.md"), "Consigne de fusion (essai)."),
        "consigne_lecteur": ecrire(os.path.join(dossier, "p", "lecteur.md"), "Consigne lecteur d'étiquettes (essai)."),
        "liste_concepts": ecrire(os.path.join(dossier, "p", "concepts.json"), json.dumps(["a", "b", "c", "d", "e"])),
    }
    conf = {
        "racine_graines": 20261101, "champs_fiche": CHAMPS, "champ_titre": "titre", "champ_axe": "axe",
        "budget": {"plafond_usd": 50.0, "arret_etape_usd": 45.0, "etapes": [
            {"nom": "proposition", "attendu_usd": 0.5, "reservation_usd": 1.0, "role": "protegee"},
            {"nom": "aiguillage", "attendu_usd": 0.5, "reservation_usd": 1.0, "role": "protegee"},
            {"nom": "juges", "attendu_usd": 1.0, "reservation_usd": 2.0, "role": "protegee"},
            {"nom": "passe_tableau", "attendu_usd": 0.5, "reservation_usd": 1.0, "role": "sacrifiable", "rang": 2},
            {"nom": "etiquettes", "attendu_usd": 0.5, "reservation_usd": 1.0, "role": "protegee"},
            {"nom": "fusions", "attendu_usd": 0.5, "reservation_usd": 1.0, "role": "sacrifiable", "rang": 1}]},
        "juges": [{"etiquette": "juge-kimi", "modele": "kimi-k3.1-pro", "fournisseur": "kimi", "consigne": "consigne_juge"},
                  {"etiquette": "juge-argon", "modele": "gemini-4-argon", "fournisseur": "argon", "consigne": "consigne_juge"},
                  {"etiquette": "juge-opus", "modele": "claude-opus-5-5", "fournisseur": "claude", "consigne": "consigne_juge"}],
        "items_juge": ITEMS, "agregation": {"regle": "au_moins", "q": 2},
        "aiguilleur": {"etiquette": "aiguilleur", "modele": "claude-opus-5-5", "fournisseur": "claude", "consigne": "consigne_aiguilleur"},
        "garde_kimi": {"debordement_max": 0.10},
        "tableau": {"longueur_max_titre": 40, "longueur_max_resume": 60, "champ_resume": "hypothese", "consigne_passe": "consigne_passe_tableau"},
        "memoire": {"methode": "bardeaux", "taille_bardeau": 3, "seuil": 0.6},
        "bisociateur": {"bras": ["meta", "gu_krenn", "basique"], "k_paires": 1,
                        "meta": {"annexe": annexe_meta(dossier)},
                        "gu_krenn": dict({"mode": "substitut", "source": source_gk(dossier), "oeuvres_min_vocabulaire": 5,
                                          "date_debut": "2015-01-01", "date_coupure": "2026-06-30", "actif_depuis": "2023-07-01",
                                          "actif_min_oeuvres": 5}),
                        "basique": {"exposant": 8.5, "decalage": 0.05, "liste_concepts": "liste_concepts"},
                        "consigne_fusion": "consigne_fusion", "consigne_lecteur_etiquettes": "consigne_lecteur",
                        "metteur_fusion": {"etiquette": "fusion-kimi", "modele": "kimi-k3.1-pro", "fournisseur": "kimi"}},
        "proposeurs": [{"etiquette": "prop-kimi", "modele": "kimi-k3.1-pro", "fournisseur": "kimi", "consigne": "consigne_proposeur"},
                       {"etiquette": "prop-argon", "modele": "gemini-4-argon", "fournisseur": "argon", "consigne": "consigne_proposeur"}],
        "cases": [["texte-I", "defense"]],
        "plafonds_session": {"proposeur": 2.0, "aiguilleur": 0.5, "juge": 0.5, "fusion": 1.0, "lecteur": 0.5},
        "etiquettes_interdites": INTERDITES,
        "lecteurs_etiquettes": [{"etiquette": "lecteur-1", "modele": "claude-sonnet-5-5", "fournisseur": "claude"},
                                {"etiquette": "lecteur-2", "modele": "claude-fable-5-1", "fournisseur": "claude"}],
        "pieces": pieces,
        "simulation": {"cout_par_appel_usd": 0.01},
    }
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


SUPPRIMER = object()


def ecrire_configuration(dossier, **modifs):
    conf = configuration(dossier, **modifs)
    chemin = os.path.join(dossier, "configuration-essai.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(conf, f, ensure_ascii=False, indent=1)
    return chemin
