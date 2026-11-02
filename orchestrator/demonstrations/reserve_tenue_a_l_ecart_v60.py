"""Ligne de commande de `pole/reserve_tenue_a_l_ecart_v60.py` (fichier neuf, R12 ; tâche A3 du tour fermé).

  python3 -I -B demonstrations/reserve_tenue_a_l_ecart_v60.py ENTREE.json SORTIE_NEUVE [--cle-tache tache] [--cle-identifiant identifiant]

Rend sur la sortie standard les empreintes et les comptes seulement (aucun contenu d'épisode). Codes : 0 réserve écrite ;
2 refus (motif sur la sortie d'erreur).
"""

import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))

from pole.reserve_tenue_a_l_ecart_v60 import principal  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(principal())
