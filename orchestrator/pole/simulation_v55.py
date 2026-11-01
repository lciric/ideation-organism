"""Moteur simulé de la v55 (aucun appel, aucune dépense) — au-dessus de `simulation_v54` (inchangé, R12).

Seul changement : le metteur en forme simulé n'ajoute plus de nombre au rendu (titre « Titre rendu » suivi de lettres tirées
de l'empreinte de la consigne), pour que le contrôle v55 des nombres ajoutés (S6, CL19-07) passe sur le cas sain ; un essai
qui veut l'artefact l'écrit lui-même.
"""

import json

from .simulation_v54 import AdaptateurSimuleV54, _h

VERSION = "simulation-v55"


class AdaptateurSimuleV55(AdaptateurSimuleV54):
    def description(self):
        return dict(super().description(), version=VERSION)

    def reponse(self, role, consigne, modele):
        t = super().reponse(role, consigne, modele)
        if "## Éléments à mettre en forme" in consigne:
            o = json.loads(t)
            h = _h(consigne)
            o["fiches"][0][self.champ_titre] = "Titre rendu " + "".join("abcdefghij"[int(c)] for c in str(h % 1000))
            t = json.dumps(o, ensure_ascii=False)
        return t
