"""Mode à blanc de la boucle fermée, version 59 (tâches A2 et A4) : ligne de commande de `pole/a_blanc_v59.py`.

Aucun réseau, aucun modèle, aucune clé, aucune dépense. Deux générations (au moins) par bras, bras « scripte », « aleatoire »,
« recopie_melange » ; la génération g+1 lit le bilan scellé de la génération g (empreinte vérifiée) avant de proposer.

  python3 -I -B demonstrations/mode_a_blanc_v59.py SORTIE_NEUVE --graine G --bac reel --utilisateur-bac 64097
  python3 -I -B demonstrations/mode_a_blanc_v59.py SORTIE_NEUVE --graine G --bac factice      (aucune barrière, dit)

`--bac` n'a pas de défaut. `--bac reel` sans `bwrap`, sonde en échec, ou noyau superutilisateur sans `--utilisateur-bac` :
refus (code 2), jamais de repli sur l'exécuteur factice. Codes : 0 journal écrit ; 2 refus (motif sur la sortie d'erreur).
Sortie standard : la synthèse par bras (JSON), l'empreinte du journal scellé `journal-a-blanc-v59.json`.
"""

import argparse
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402


def principal(argv=None):
    a = argparse.ArgumentParser(description="mode à blanc de la boucle fermée (v59)")
    a.add_argument("sortie")
    a.add_argument("--graine", type=int, required=True, help="racine des graines (SeedSequence, R9) ; aucun défaut")
    a.add_argument("--bac", choices=("reel", "factice"), required=True, help="aucun défaut ; « reel » refuse sans bwrap")
    a.add_argument("--utilisateur-bac", type=int, default=None, help="identité sans privilège du bac (noyau superutilisateur)")
    a.add_argument("--generations", type=int, default=2)
    a.add_argument("--cartes-reference", type=int, default=6)
    args = a.parse_args(argv)
    try:
        r = A.jouer_a_blanc(args.sortie, racine_graines=args.graine, racine_orchestrateur=RACINE, bac=args.bac,
                            generations=args.generations, nombre_reference=args.cartes_reference,
                            utilisateur_bac=args.utilisateur_bac)
    except Exception as e:  # noqa: BLE001 — tout refus rend 2, motif dit
        print(json.dumps({"arret": type(e).__name__ + " : " + str(e)[:2000]}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"version": A.VERSION, "journal": os.path.join(args.sortie, "journal-a-blanc-v59.json"),
                      "journal_sha256": r["sha256"], "synthese_par_bras": r["synthese_par_bras"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
