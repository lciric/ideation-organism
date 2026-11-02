"""Tour d'idéation, version 59 (fichier neuf, R12 ; tâche A2) — `pole/ideation_v2.py` **avec l'étage de tests de mort v5**.

`pole/ideation_v2.py` importe en dur l'étage de la version 2 (`tests_de_mort_v2` : `executer_tests_de_mort`, dont le verdict
est lu dans le chiffre que le script imprime, `valider_champ_test` sans bloc `statistique`, `ExecuteurBacASable` à 512 Mo).
Ici, une **instance propre** du tour v2 est chargée à part (le fichier v2 n'est pas touché, R12), puis ses noms d'étage sont
remplacés par ceux de la version 5 (`pole/tests_de_mort_v5.py`, R-1057 : verdict calculé par le noyau sur le fichier brut ;
bloc `statistique` exigé ; bac de la v3, 768 Mo) : `executer_tests_de_mort`, `valider_champ_test`, `extraire_prereg_court`,
`GABARIT_TEST`, `consigne_experimentateur_maximale`, `ExecuteurBacASable`. Les fonctions du tour lisent ces noms au moment de
l'appel : la course (`jouer_etage`), l'étage différé (`jouer_etage_apres_bras`), la validation des fiches et le gabarit servi
passent tous par la version 5.

Limite dite : la mesure de la plus grosse consigne du lecteur dans le devis (`pole/ideation_v2.py`, import local de
`consigne_lecteur` et `vue_lecteur` de la v2 dans une fonction) mesure encore la consigne du lecteur de la v2 ; elle ne pèse que
sur le devis (taille), jamais sur un verdict.
"""

import importlib.util
import os

from . import tests_de_mort_v5 as v5

VERSION = "ideation-tour-v59 (tour v2 avec l'étage de tests de mort v5)"
NOMS_REMPLACES = ("executer_tests_de_mort", "valider_champ_test", "extraire_prereg_court", "GABARIT_TEST",
                  "consigne_experimentateur_maximale", "ExecuteurBacASable")

_spec = importlib.util.spec_from_file_location(__package__ + ".ideation_v2_pour_v59",
                                               os.path.join(os.path.dirname(os.path.abspath(__file__)), "ideation_v2.py"))
tour = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tour)  # instance propre du tour v2 (R12 : le fichier n'est pas touché)
for _nom in NOMS_REMPLACES:
    setattr(tour, _nom, getattr(v5, _nom))
tour.VERSION_TOUR_V59 = VERSION

__all__ = ("tour", "VERSION", "NOMS_REMPLACES")
