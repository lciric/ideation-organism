"""Aides des essais de la v54 : configuration complète au format v54 (valeurs **d'essai** seulement, aucune recommandée ni
gelée), annexe du bras méta d'essai au format de l'annexe réelle (brouillon 1 : identifiants de structures, définitions,
jeu d'essai de non-vacuité, champs de contre-lecture et d'approbation remplis d'un texte d'essai conforme à I-9), moteur
simulé v54."""

import json
import os

import aides_v53 as A53
from pole.outils import ecrire_scelle, sha256_fichier
from pole.simulation_v54 import AdaptateurSimuleV54

CHAMPS = A53.CHAMPS
ITEMS = A53.ITEMS
INTERDITES = ["témoin", "exploratoire", "fusion", "bras méta", "gu et krenn", "gu krenn", "bisociation"]
SUPPRIMER = A53.SUPPRIMER
SHA_A, SHA_B = "a" * 64, "b" * 64
ecrire = A53.ecrire

NICHES = ["n1_seq", "n2_act", "n3_ano"]
STRUCTURES = ["om_martingale", "om_covariance", "me_cusum", "jd_simulateur"]


def parametres_meta(**modifs):
    p = {"version": "annexe d'essai", "niches": list(NICHES), "types_structure": list(STRUCTURES),
         "communication": {"n1_seq|n2_act": 1, "n1_seq|n3_ano": 3, "n2_act|n3_ano": 0}, "seuil_communication_faible": 1,
         "structure_forte": {"nombre_min": 1, "types": ["om_martingale", "om_covariance", "me_cusum"]},
         "eloignement": {"n1_seq|n2_act": 2, "n1_seq|n3_ano": 3, "n2_act|n3_ano": 5}, "bande": [2, 3], "poids": 0.5,
         "repli": "indicateurs_puis_structure",
         "contre_lecture": f"essai : contre-lecture factice ; brouillon relu {SHA_A} ; rapport {SHA_B}",
         "approbation_lazar": "essai : R-901, 2026-10-31",
         "accord_min_niche_kappa": 0.4, "accord_min_structures_jaccard": 0.3,
         "definitions_niches": {n: f"définition de {n}" for n in NICHES},
         "definitions_structures": {s: f"définition de {s}" for s in STRUCTURES}}
    p.update(modifs)
    return p


JEU_ESSAI = {"e1": {"niche": "n1_seq", "structures": ["om_martingale", "me_cusum"]},
             "e2": {"niche": "n2_act", "structures": ["om_martingale"]},
             "e3": {"niche": "n3_ano", "structures": ["om_covariance"]},
             "e4": {"niche": "n1_seq", "structures": ["jd_simulateur"]}}


def annexe_meta(dossier, nom="annexe-bras-meta-essai-v54.md", jeu=JEU_ESSAI, sceller=True, **modifs):
    texte = ("# Annexe d'essai (format du brouillon 1)\n\n```json\n" + json.dumps({"jeu_essai_non_vacuite": jeu}, ensure_ascii=False)
             + "\n```\n\n```json\n" + json.dumps({"parametres_bras_meta": parametres_meta(**modifs)}, ensure_ascii=False) + "\n```\n")
    chemin = os.path.join(dossier, nom)
    if os.path.exists(chemin):  # même dossier : jamais réécrite (R12) ; même contenu exigé
        with open(chemin, encoding="utf-8") as f:
            if f.read() != texte:
                raise FileExistsError(f"{chemin} : contenu différent (choisir un autre nom)")
        return {"chemin": chemin, "sha256": sha256_fichier(chemin)}
    if sceller:
        ecrire_scelle(chemin, texte)
    else:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(texte)
    return {"chemin": chemin, "sha256": sha256_fichier(chemin)}


ARRETS = {"a3_echecs_consecutifs": 3, "a3_delai_s": {"*": 300, "kimi": 1800}, "a14_part_max": 0.25,
          "a11_modeles": ["claude-opus-5-5"]}


def configuration(dossier, **modifs):
    conf = A53.configuration(dossier)
    conf["bisociateur"]["meta"] = {"annexe": annexe_meta(dossier), "regle_divergence": "fiche_ecartee", "structures": "union",
                                   "definitions": "annexe", "s28": "annexe",
                                   "desaccord": {"paires_max": 3, "champ_affirmation": "hypothese", "consigne": "consigne_desaccord"}}
    conf["pieces"]["consigne_desaccord"] = ecrire(os.path.join(dossier, "p", "desaccord.md"),
                                                  "Les deux affirmations se contredisent-elles ? (essai)")
    conf["bisociateur"]["fournisseurs_entree"] = ["*"]
    conf["budget"]["portee_plafond"] = "par_generation"
    conf["garde_kimi"].update(refus_aiguilleur="debordement", arret_metteur_fusion=True)
    conf["tableau"]["juger_passe_tableau"] = True
    conf["a4"] = {"mode": "prefixe", "action": "arret"}
    conf["etiquettes_interdites"] = list(INTERDITES)
    conf["graines"] = {"prefixe": "pp2"}
    conf["arrets"] = json.loads(json.dumps(ARRETS))
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


def ecrire_configuration(dossier, **modifs):
    conf = configuration(dossier, **modifs)
    chemin = os.path.join(dossier, "configuration-essai-v54.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(conf, f, ensure_ascii=False, indent=1)
    return chemin


def adaptateurs(cout=0.01, **decideurs):
    return {n: AdaptateurSimuleV54(champs_fiche=CHAMPS, items=ITEMS, cout_par_appel_usd=cout, champ_titre="titre",
                                   decider=decideurs.get(n)) for n in ("kimi", "argon", "claude")}


def ligne_go(ident, plafond, *, accorde="2026-10-31", echeance="2099-12-31", typ="calcul", par="Lazar", perimetre="essai"):
    """Une ligne au format réel de `registres/go.md` (8 colonnes), reconstituée pour les essais."""
    return f"| {ident} | {accorde} | {typ} | {perimetre} | {plafond} | {echeance} | {par} | essai reconstitué |\n"


def registre_go(dossier, *lignes, nom="go.md"):
    chemin = os.path.join(dossier, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("# Registre des GO (essai)\n\n| id | accordé le | type | périmètre | plafond | échéance | accordé par | référence |\n"
                "|---|---|---|---|---|---|---|---|\n" + "".join(lignes))
    return chemin


# --- pré-pilote ---------------------------------------------------------------------------------------------------------------

PLAN_PP = [("e1_redacteur", "protegee"), ("e2_kimi_passe1", "protegee"), ("e3_rendus", "protegee"), ("e4_aiguillage", "protegee"),
           ("e5_relecteur", "protegee"), ("e6_juges", "protegee"), ("e7a_passe_tableau", "sacrifiable", 4),
           ("e7b_etiquettes", "protegee"), ("e7c_fusions", "sacrifiable", 1), ("e7d_axe7", "sacrifiable", 3),
           ("e8_paraphrases", "protegee"), ("e9_anteriorite", "reductible", 2), ("e9b_m6b", "protegee_hors_porte")]


class EtageUnFactice:
    """Analyseur d'étage 1 d'essai (injecté ; DEP3 n'existe pas) : signale une fiche dont le contenu porte « HELIOS-PAGE-FAUSSE »."""

    def signaler(self, fiche):
        return "HELIOS-PAGE-FAUSSE" in json.dumps(fiche.get("contenu", fiche), ensure_ascii=False)

    def cas_sain(self):
        return {"contenu": {"titre": "P", "hypothese": "chiffres conformes"}}

    def artefact(self):
        return {"contenu": {"titre": "G", "hypothese": "HELIOS-PAGE-FAUSSE"}}


def configuration_pre_pilote(dossier, plafond=60.0, **modifs):
    conf = configuration(dossier)
    P = conf["pieces"]
    d = os.path.join(dossier, "pp")
    for nom, texte in (("consigne_redacteur", "Rédacteur (essai)."), ("consigne_rendu", "Mets ces éléments en forme (essai)."),
                       ("consigne_second_lecteur", "SECOND_LECTEUR consigne figée (essai)."),
                       ("consigne_adjudicateur", "ADJUDICATEUR consigne figée (essai)."), ("consigne_relecteur", "RELECTEUR consigne (essai)."),
                       ("consigne_paraphrase", "Paraphrase (essai)."), ("consigne_verificateur", "VERIFICATEUR antériorité (essai)."),
                       ("consigne_m6b", "VERIFICATEUR M6b (essai)."), ("consigne_axe7", "TABLE_SEULE (essai)."),
                       ("produit_difficiles", "Écris PRODUIT:difficiles:2 (essai)."), ("produit_voisines", "Écris PRODUIT:voisines:2 (essai)."),
                       ("produit_axe7", "Écris PRODUIT:axe7:3 (essai).")):
        P[nom] = ecrire(os.path.join(d, nom + ".md"), texte)
    P["anteriorite_fiches"] = ecrire(os.path.join(d, "ant.json"), json.dumps({"fiches": [
        {"ident": f"a{i}", "references": [{"id": f"r{i}{k}", "titre": f"Référence {i}{k}"} for k in range(5)]} for i in range(4)]}))
    P["anteriorite_cle"] = ecrire(os.path.join(d, "ant-cle.json"), json.dumps({"a0": "inventees", "a1": "inventees", "a2": "alterees",
                                                                              "a3": "sans_defaut"}))
    P["m6b_fiches"] = ecrire(os.path.join(d, "m6b.json"), json.dumps({"fiches": [{"ident": "m0", "texte": "idée reformulée"},
                                                                                 {"ident": "m1", "texte": "idée tirée de Titre Source Un"}]}))
    P["m6b_sources"] = ecrire(os.path.join(d, "m6b-sources.json"), json.dumps({"m0": {"titre": "Titre Source Zéro", "auteurs": ["Durand"],
                                                                                      "identifiant": "10.0/zero"},
                                                                               "m1": {"titre": "Titre Source Un", "auteurs": ["Martin"],
                                                                                      "identifiant": "10.0/un"}}))
    conf["proposeurs"] = [conf["proposeurs"][0]]
    conf["tableau"]["juger_passe_tableau"] = False
    conf["bisociateur"]["fournisseurs_entree"] = ["kimi"]
    conf["plafonds_session"].update(redacteur=1.0, metteur=1.0, relecteur=0.5, verificateur=1.0)
    etapes = []
    for e in PLAN_PP:
        x = {"nom": e[0], "attendu_usd": 0.3, "reservation_usd": 0.6, "role": e[1]}
        if len(e) == 3:
            x["rang"] = e[2]
        if e[1] == "reductible":
            x["reduite"] = {"attendu_usd": 0.1, "reservation_usd": 0.2}
        etapes.append(x)
    conf["budget"] = {"plafond_usd": plafond, "arret_etape_usd": "sans", "portee_plafond": "course", "etapes": etapes}
    clerk = {"etiquette": "redacteur", "modele": "claude-sonnet-5-5", "fournisseur": "claude", "consigne": "consigne_redacteur"}
    conf["prepilote"] = {
        "L1": "oui", "L2": "oui", "d_g": "b",
        "temoins": {"classes": {"P": 4, "N1": 2, "N2": 2, "C": 1, "G": 1}, "axes": ["1", "2"], "par_axe_min": 5, "par_axe_max": 5,
                    "meme_classe_par_axe_max": 3, "essais_max_tirage": 200, "version": 1,
                    "indices": {"longueur": [3500, 5000, 6500], "chiffres": [10, 20], "champs": [4]},
                    "fournisseurs": {"kimi": 3, "argon": 3, "tiers": 4}},
        "redacteur": clerk, "squelette": {"ancres_min": 12, "ancres_max": 16},
        "metteurs": {"kimi": {"etiquette": "metteur-kimi", "modele": "kimi-k3.1-pro", "fournisseur": "kimi"},
                     "argon": {"etiquette": "metteur-argon", "modele": "gemini-4-argon", "fournisseur": "argon"},
                     "tiers": {"etiquette": "metteur-tiers", "modele": "claude-sonnet-5-5", "fournisseur": "claude"}},
        "consigne_rendu": "consigne_rendu", "a8": {"min": 3000, "max": 8000},
        "s6": {"ancres_min": 0.95, "couples_min": 1.0, "defaut_vu_min": 1.0}, "a5_exclus_max": 2,
        "second_lecteur": {"etiquette": "second-lecteur", "modele": "claude-fable-5-1", "fournisseur": "claude",
                           "consigne": "consigne_second_lecteur"},
        "adjudicateur": {"etiquette": "adjudicateur", "modele": "claude-sonnet-5-5", "fournisseur": "claude",
                         "consigne": "consigne_adjudicateur"},
        "relecteur": {"etiquette": "relecteur", "modele": "claude-fable-5-1", "fournisseur": "claude", "consigne": "consigne_relecteur"},
        "s20": {"ambigus_max": 2, "p_min": 2, "n_min": 2},
        "controles_forme": {"s18_aire_max": 0.7, "s18_effectif_min": 6, "s19_aire_max": 0.95, "ridge": 1.0},
        "paraphrases": {"nombre_par_niveau": 1, "niveaux": ["L1", "L2", "L3"], "consigne": "consigne_paraphrase"},
        "produits_redacteur": [{"nom": "difficiles", "consigne": "produit_difficiles", "nombre": 2, "cle_json": "difficiles"},
                               {"nom": "voisines", "consigne": "produit_voisines", "nombre": 2, "cle_json": "voisines"},
                               {"nom": "axe7", "consigne": "produit_axe7", "nombre": 3, "cle_json": "axe7"}],
        "axe7": {"consigne": "consigne_axe7", "lecteur": {"etiquette": "juge-opus-axe7", "modele": "claude-opus-5-5", "fournisseur": "claude"}},
        "anteriorite": {"fiches": "anteriorite_fiches", "cle": "anteriorite_cle", "consigne": "consigne_verificateur",
                        "reduite": {"inventees": 1, "alterees": 1, "sans_defaut": 0},
                        "verificateur": {"etiquette": "verificateur", "modele": "claude-opus-5-5", "fournisseur": "claude",
                                         "role_kit": "proposeur_ideation"}},
        "m6b": {"fiches": "m6b_fiches", "sources": "m6b_sources", "consigne": "consigne_m6b"},
        "seuils_m1": {"exactitude_min": 0.8, "rappel_min": 0.7, "plancher_echec": 0.7, "fleiss_min": 0.45, "cohen_min": 0.35,
                      "accord_plancher": 0.3}}
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
