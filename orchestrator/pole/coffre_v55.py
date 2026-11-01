"""Coffre de la v55 (CL19-03, partie code sans décision) — au-dessus de `coffre_v53` (inchangé, R12).

En v54, la boîte d'É5 lisait une **copie en mémoire** de la clé des classes : le journal d'accès du coffre (garde R5 ligne 30)
ne voyait pas cette lecture. En v55, le programme ne garde aucune copie : toute lecture d'une clé avant la fin d'É9 passe
par `lire_pour_garde(nom, role, raison)`, qui :

- n'est permise que pour un couple (nom, rôle) **déclaré à la construction** (`lectures_permises`, liste fermée tenue par
  le code et écrite au manifeste) ; tout autre couple est un **incident** (comme `ouvrir`), puis `LectureAvantFinE9` ;
- inscrit au journal d'accès une ligne `lecture_par_programme` : horodatage UTC, nom, rôle, raison — **jamais le contenu** ;
- exige ensuite `noter_sortie_garde(jeton, comptes)` : la sortie de la garde (décision et comptes entiers ou réels,
  **aucun identifiant**) est jointe à la ligne du journal ; une sortie qui porte autre chose qu'un nombre, un booléen ou
  `None` est refusée.

La question de fond (l'amendement d'A21 et de la ligne 30 du brouillon 7, ou une boîte tenue par session-depot qui ne livre
jamais la clé à l'orchestrateur) reste à Lazar : ce module ne fait que rendre la lecture visible et bornée.
"""

import datetime
import json
import os

from .coffre_v53 import Coffre, LectureAvantFinE9
from .outils import verifier_scelle

VERSION = "coffre-a21-v55"


class SortieDeGardeRefusee(ValueError):
    pass


def _maintenant():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="microseconds")


class CoffreV55(Coffre):
    def __init__(self, dossier, lectures_permises=()):
        super().__init__(dossier)
        self.lectures_permises = {(n, r) for n, r in lectures_permises}
        self._en_attente = {}

    def permettre(self, nom, role):
        """Déclare un couple (nom de dépôt, rôle de lecture par programme) ; consigné au journal."""
        self.lectures_permises.add((nom, role))
        self._acces("lecture_par_programme_declaree", nom, role=role)

    def lire_pour_garde(self, nom, role, raison):
        """Rend (jeton, contenu). Journalisée ; jamais après la fin d'É9 (`ouvrir` suffit alors) ; couple non déclaré : incident."""
        if not isinstance(raison, str) or not raison.strip():
            raise ValueError("lecture par programme : raison exigée")
        if (nom, role) not in self.lectures_permises:
            incident = {"quoi": "lecture par programme non déclarée (A21)", "nom": nom, "role": role, "n_acces": len(self.acces) + 1}
            self.incidents.append(incident)
            self._acces("tentative_lecture_non_declaree", nom, role=role, raison=raison, horodatage=_maintenant())
            raise LectureAvantFinE9(f"A21 : lecture par programme de {nom!r} par le rôle {role!r} non déclarée : incident consigné")
        chemin = os.path.join(self.dossier, nom + ".json")
        if not verifier_scelle(chemin):
            raise LectureAvantFinE9(f"dépôt {nom!r} : sceau absent ou faux")
        self._acces("lecture_par_programme", nom, role=role, raison=raison, horodatage=_maintenant(), sortie=None)
        jeton = len(self.acces)
        self._en_attente[jeton] = nom
        with open(chemin, "r", encoding="utf-8") as f:
            return jeton, json.load(f)

    def noter_sortie_garde(self, jeton, comptes):
        if jeton not in self._en_attente:
            raise SortieDeGardeRefusee(f"jeton de lecture {jeton!r} inconnu ou déjà soldé")
        if not isinstance(comptes, dict):
            raise SortieDeGardeRefusee("sortie de garde : dictionnaire de comptes exigé")
        for k, v in comptes.items():
            if not isinstance(k, str) or not (v is None or isinstance(v, (bool, int, float))):
                raise SortieDeGardeRefusee(f"sortie de garde : seuls des comptes sortent (clé {k!r} : {type(v).__name__} refusé)")
        ligne = self.acces[jeton - 1]
        ligne["sortie"] = dict(comptes)
        del self._en_attente[jeton]
        return True

    def lectures_non_soldees(self):
        return sorted(self._en_attente.items())

    def journal(self):
        j = super().journal()
        j["version"] = VERSION
        j["lectures_permises"] = sorted([n, r] for n, r in self.lectures_permises)
        j["lectures_non_soldees"] = [n for _, n in self.lectures_non_soldees()]
        return j


__all__ = ("CoffreV55", "LectureAvantFinE9", "SortieDeGardeRefusee")
