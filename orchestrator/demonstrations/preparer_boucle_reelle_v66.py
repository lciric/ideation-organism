"""Outil de préparation du texte scellé de la boucle réelle v66 (fichier neuf, R12) — hors du code gelé, jamais joué par une course.

Écrit dans DOSSIER (neuf) : `heritage-depart-v65.json` scellé (le même que la v65 : génération 0 déclarée, archive {K1}, K1
« connue, déclarée » ; écrit par `boucle_reelle_v65.ecrire_heritage_depart`, déterministe) et `blocs-pour-le-texte-v66.md`, qui
porte les trois blocs à recopier tels quels dans le texte à sceller : `empreintes-du-code-v66` (sha256 de chaque fichier de
`FICHIERS_GELES`, lus sur disque), `plan-gele-v66` (valeurs du devis ; GO cité, par défaut GO-2026-11-08-02 ; empreintes du jeu
planté, de l'héritage de départ, du monde et de la configuration v6) et `jeu-plante-v65` (le jeu du brouillon 1, inchangé).
Aucun appel, aucun réseau.

  python3 -I -B demonstrations/preparer_boucle_reelle_v66.py DOSSIER_NEUF [--configuration exemples/configuration-boucle-reelle-v6.json]
                                                            [--go GO-2026-11-08-02 | --go GO-2026-11-10-10]
"""

import argparse
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

import importlib.util  # noqa: E402

from pole import a_blanc_v59 as A  # noqa: E402
from pole import boucle_reelle_v65 as B65  # noqa: E402
from pole.outils import sha256_fichier  # noqa: E402

_spec = importlib.util.spec_from_file_location("lanceur_boucle_reelle_v66_preparation", os.path.join(ICI, "boucle_reelle_v66.py"))
LANCEUR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LANCEUR)


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("dossier")
    a.add_argument("--configuration", default=os.path.join(RACINE, "exemples", "configuration-boucle-reelle-v6.json"))
    a.add_argument("--go", default="GO-2026-11-08-02", choices=("GO-2026-11-08-02", "GO-2026-11-10-10"))
    x = a.parse_args(argv)
    if os.path.exists(x.dossier) and os.listdir(x.dossier):
        print(f"refus : {x.dossier} non vide (on n'écrase jamais)", file=sys.stderr)
        return 2
    os.makedirs(x.dossier, exist_ok=True)
    monde = A.charger_monde(RACINE)
    jeu = B65.jeu_du_dessin(monde)
    bloc = B65.texte_du_bloc(jeu)
    sha_jeu = B65.empreinte_du_bloc(bloc)
    sha_dep = B65.ecrire_heritage_depart(x.dossier, jeu)
    empreintes = "\n".join(f"{sha256_fichier(os.path.join(RACINE, r))}  {r}" for r in LANCEUR.FICHIERS_GELES)
    plan = {"generations": 2, "cartes_par_proposeur": 6, "m_e_bh": 22, "bras": "reel_seul", "d9": "mecanique",
            "plafond_modeles_usd": 40, "plafond_kimi_usd": 33, "plafond_argon_usd": 7, "plafond_machine_usd": 5,
            "go": x.go, "go_montant_usd": 45, "duree_h": 72, "configuration_sha256": sha256_fichier(x.configuration),
            "monde_sha256": monde["sha256"], "jeu_plante_sha256": sha_jeu, "heritage_depart_sha256": sha_dep}
    texte = (LANCEUR.DEBUT_EMPREINTES + "\n" + empreintes + "\n" + LANCEUR.FIN_EMPREINTES + "\n\n" + LANCEUR.DEBUT_PLAN + "\n"
             + "\n".join(f"{k}: {v}" for k, v in plan.items()) + "\n" + LANCEUR.FIN_PLAN + "\n\n" + bloc + "\n")
    LANCEUR.lire_plan(texte)  # le plan écrit passe les gardes du lanceur
    B65.lire_jeu_plante(texte, sha_jeu)
    with open(os.path.join(x.dossier, "blocs-pour-le-texte-v66.md"), "w", encoding="utf-8") as f:
        f.write(texte)
    print(f"jeu_plante_sha256 {sha_jeu}\nheritage_depart_sha256 {sha_dep}\nconfiguration_sha256 {plan['configuration_sha256']}\n"
          f"go {x.go}\nfichiers gelés {len(LANCEUR.FICHIERS_GELES)}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
