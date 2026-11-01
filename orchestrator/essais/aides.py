"""Aides communes aux essais : fiches valides, dossiers temporaires sous `sortie/essais/_tmp` (jamais hors de `sortie/`)."""

import copy
import os
import shutil
import statistics
import tempfile
import unittest

from pole.fiche import Fiche

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp")


def seuil_pour(alpha):
    return round(statistics.NormalDist().inv_cdf(1 - alpha), 6)


def fiche_dict(identifiant="F1", **modifs):
    d = {"identifiant": identifiant, "enonce": f"Hypothèse d'essai {identifiant} : l'effet mesuré est positif",
         "prediction": {"signe": "+", "valeur": 0.5, "texte": "effet positif"}, "metrique": "moyenne (z)",
         "nul": "moyenne nulle", "seuil": seuil_pour(0.01), "severite_attendue": 0.01, "cout_borne": 1.0,
         "protocole": "test z unilatéral, n=400", "domaines": ["statistique"], "operateurs": ["moyenne"],
         "contraintes": ["independant"]}
    d.update(copy.deepcopy(modifs))
    return d


def fiche(identifiant="F1", **modifs):
    return Fiche.depuis_dict(fiche_dict(identifiant, **modifs)).valider()


class CasAvecDossier(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True)
        self.tmp = tempfile.mkdtemp(dir=BASE)
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def sous_dossier(self, *noms):
        chemin = os.path.join(self.tmp, *noms)
        os.makedirs(chemin, exist_ok=True)
        return chemin
