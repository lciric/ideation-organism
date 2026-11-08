"""Bloc du texte scellé de la course réelle minimale de la boucle complète, version 65 (fichier neuf, R12) : écrit d'avance ce qui
remplace le marqueur `<<BLOC-V65>>` du brouillon 1 (empreintes du code gelé, plan gelé, jeu planté, commandes exactes), le fichier de
l'héritage de départ (génération 0, K1 « connue, déclarée ») et le texte du mode à blanc. Aucun appel, aucun réseau, aucune clé.

K1 est la loi gelée du brouillon 1, § 3.2 (ajustée par `essai-a-blanc-v1/ajuster_k1_v1.py`, arrondie à 6 décimales) ; le jeu planté
est construit par `boucle_reelle_v65.jeu_plante_du_brouillon` (§ 3.3, 3.4, 3.6) ; la configuration v5 est celle que nomme le plan.

  python3 -I -B demonstrations/bloc_v65_boucle_reelle.py [--ecrire-heritage] [--ecrire-texte-a-blanc] [--configuration CONF]
Sans option : imprime le bloc (rien n'est écrit). Les fichiers écrits n'ont pas de compagnon `.sha256` : l'empreinte qui fait foi est
celle que porte le plan du texte scellé.
"""

import argparse
import hashlib
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import boucle_reelle_v65 as B  # noqa: E402
from pole.outils import sha256_fichier  # noqa: E402

K1_DU_BROUILLON = {"type": "softmax", "poids": [[0.0, 0.0], [-0.834964, 0.0], [-0.242046, 0.0]], "biais": [0.0, 0.941698, 0.721847]}
GO = "GO-2026-11-08-02"
CONFIGURATION = os.path.join(RACINE, "exemples", "configuration-tour-ferme-v5.json")
PLAN = {"generations": 2, "bras": B.OPTION_BRAS, "cartes_par_proposeur": 6, "m_e_bh": 22, "plafond_modeles_usd": 40, "plafond_kimi_usd": 33,
        "plafond_argon_usd": 7, "plafond_machine_usd": 5, "duree_h": 72, "d9": "mecanique", "go": GO}


def texte_plan(configuration_sha256, heritage_sha256, jeu_sha256, monde_sha256, **chg):
    p = dict(PLAN, configuration_sha256=configuration_sha256, monde_sha256=monde_sha256, heritage_depart_sha256=heritage_sha256,
             jeu_plante_sha256=jeu_sha256)
    p.update(chg)
    return B.DEBUT_PLAN + "\n" + "\n".join(f"{k}: {p[k]}" for k in B.CLES_PLAN if p.get(k) is not None) + "\n" + B.FIN_PLAN


def morceaux(configuration=CONFIGURATION):
    monde = A.charger_monde(RACINE)
    jeu = B.jeu_plante_du_brouillon(monde, K1_DU_BROUILLON)
    octets_h = B.octets_heritage_depart(K1_DU_BROUILLON)
    sha_h = hashlib.sha256(octets_h).hexdigest()
    bloc_jeu = B.bloc_jeu_plante(jeu)
    sha_jeu = hashlib.sha256(B.json_canonique(jeu)).hexdigest()
    sha_conf = sha256_fichier(configuration)
    plan = texte_plan(sha_conf, sha_h, sha_jeu, monde["sha256"])
    return {"monde": monde, "jeu": jeu, "octets_heritage": octets_h, "heritage_sha256": sha_h, "bloc_jeu": bloc_jeu, "jeu_sha256": sha_jeu,
            "configuration_sha256": sha_conf, "plan": plan}


def texte_a_blanc(m):
    return ("# Plan et jeu planté du mode à blanc de la v65 (exploratoire, non scellé)\n\n"
            "Mêmes blocs que ceux du texte scellé de la course (plan gelé, jeu planté) ; lus par les mêmes fonctions.\n\n"
            + m["plan"] + "\n\n" + m["bloc_jeu"] + "\n")


def bloc_v65(m):
    from importlib import util
    spec = util.spec_from_file_location("lanceur_boucle_reelle_v65_pour_bloc", os.path.join(ICI, "boucle_reelle_v65.py"))
    L = util.module_from_spec(spec)
    spec.loader.exec_module(L)
    emp = "\n".join(f"{sha256_fichier(os.path.join(RACINE, r))}  {r}" for r in sorted(L.FICHIERS_GELES))
    commandes = (
        "Commandes exactes (depuis `orchestrator/` de l'organisme, commit qui porte ce code ; machine à `bwrap` ≥ 0.9, utilisateur "
        "dédié 64097 ; relais Kimi et Argon déjà lancés par la session de dépôt, clés chez eux seuls) :\n\n"
        "```bash\n"
        "POLE_ESSAI_BAC_REEL_NON_JOUE= python3 -I -B -m pytest -q -p no:cacheprovider essais/test_boucle_reelle_v65.py "
        "essais/test_tour_ferme_v64.py essais/test_gardes_tour_ferme_v64.py essais/test_v59_boucle_fermee.py essais/test_v57b_cablage_verdict.py\n"
        "python3 -I -B essais/mutations_boucle_reelle_v65.py\n"
        "python3 -I -B demonstrations/boucle_reelle_v65.py /tmp/essai-v65-bac-reel --a-blanc --graine 20261108 --bac reel --utilisateur-bac 64097\n"
        "python3 -I -B demonstrations/boucle_reelle_v65.py SORTIE --preenregistrement prereg/preenregistrement-boucle-reelle-organisme-v1-v1.md "
        "--configuration CONFIGURATION_V5 --moteur reel --confirmer-moteur-reel --registre-go REGISTRE_GO --go " + GO + " --bac reel "
        "--utilisateur-bac 64097 --verifier-seulement\n"
        "python3 -I -B demonstrations/boucle_reelle_v65.py SORTIE --preenregistrement prereg/preenregistrement-boucle-reelle-organisme-v1-v1.md "
        "--configuration CONFIGURATION_V5 --moteur reel --confirmer-moteur-reel --registre-go REGISTRE_GO --go " + GO + " --bac reel "
        "--utilisateur-bac 64097\n"
        "python3 -I -B demonstrations/lire_boucle_reelle_v65.py SORTIE LECTURE.json --releve-sha256 SHA_DU_RAPPORT\n"
        "```\n\n"
        f"Héritage de départ : `orchestrator/exemples/heritage-depart-boucle-reelle-v65.json`, sha256 {m['heritage_sha256']} ; "
        f"configuration v5 : sha256 {m['configuration_sha256']} (à poser à côté de la configuration v4, même dossier `pieces/`) ; "
        f"jeu planté : sha256 {m['jeu_sha256']}.")
    return L.DEBUT_EMPREINTES + "\n" + emp + "\n" + L.FIN_EMPREINTES + "\n\n" + m["plan"] + "\n\n" + m["bloc_jeu"] + "\n\n" + commandes + "\n"



def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--ecrire-heritage", action="store_true")
    a.add_argument("--ecrire-texte-a-blanc", action="store_true")
    a.add_argument("--configuration", default=CONFIGURATION)
    x = a.parse_args(argv)
    m = morceaux(x.configuration)
    if x.ecrire_heritage:
        chemin = os.path.join(RACINE, "exemples", "heritage-depart-boucle-reelle-v65.json")
        if os.path.exists(chemin):
            print(f"refus : {chemin} existe (on n'écrase jamais)", file=sys.stderr)
            return 2
        with open(chemin, "wb") as f:
            f.write(m["octets_heritage"])
    if x.ecrire_texte_a_blanc:
        chemin = os.path.join(RACINE, "exemples", "plan-et-jeu-a-blanc-boucle-reelle-v65.md")
        if os.path.exists(chemin):
            print(f"refus : {chemin} existe (on n'écrase jamais)", file=sys.stderr)
            return 2
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(texte_a_blanc(m))
    if not (x.ecrire_heritage or x.ecrire_texte_a_blanc):
        print(bloc_v65(m))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
