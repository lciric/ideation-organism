"""Point d'entrée.

Sous `python -I`, le dossier courant n'est pas sur le chemin d'import (option `-P` impliquée depuis Python 3.11) : on lance
donc `python -I pole …` depuis le dossier qui contient `pole/` ; ce fichier remplace alors le dossier du paquet par son
parent dans le chemin d'import. `python -m pole …` reste possible quand ce parent est déjà sur le chemin.
"""

import os
import sys

if not __package__:
    ICI = os.path.dirname(os.path.abspath(__file__))
    sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.curdir) != ICI]
    sys.path.insert(0, os.path.dirname(ICI))
    from pole.pole import principal
else:
    from .pole import principal

sys.exit(principal())
