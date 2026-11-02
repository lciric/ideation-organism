"""Course d'idéation : lanceur, version 59 (fichier neuf, R12 ; tâche A2) — le lanceur v8 (`demonstrations/ideation_v8.py`,
chargé à part et inchangé) dont la course 2 est `pole/course2_v59.py` : étage de tests de mort v5 (verdict du noyau), sélection
scellée v57, **lue par la génération suivante** (boucle fermée). Plus d'une génération sans étage de tests de mort est refusé.

Mêmes options, mêmes gardes avant tout appel que le lanceur v8 (configuration v56, É0, machine jetable, GO, moteur réel) ; sans
`--course-2`, la main passe au lanceur v8, qui la passe aux versions précédentes.

  python -I -B demonstrations/ideation_v59.py --course-2 CONF SORTIE --generations N [--verifier-seulement | --moteur simule | …]
"""

import importlib.util
import os
import sys
import types

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

_spec = importlib.util.spec_from_file_location("ideation_v8_lanceur_pour_v59", os.path.join(ICI, "ideation_v8.py"))
v8 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v8)  # instance propre (R12 : le lanceur v8 n'est pas touché)

from pole import course2_v56 as _c56  # noqa: E402
from pole import course2_v59 as c59  # noqa: E402

VERSION = "lanceur-ideation-v59 (course 2 v59 : étage v5, sélection scellée lue par la génération suivante)"

# la course 2 vue par le lanceur v8 : celle de la v56 pour tout (déclaration des bras, vérifications, génération), sauf
# l'exécution de la course, qui est celle de la v59
v8.c2 = types.SimpleNamespace(**{n: getattr(_c56, n) for n in dir(_c56) if not n.startswith("__")})
v8.c2.executer_course_v56 = c59.executer_course_v59
v8.VERSION = VERSION


def principal(argv=None, environnement=None, etage1=None):
    return v8.principal(argv, environnement, etage1)


if __name__ == "__main__":
    raise SystemExit(principal())
