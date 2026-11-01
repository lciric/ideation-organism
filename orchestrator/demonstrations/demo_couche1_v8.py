"""Couche 1, v8, en simulation d'agents : la démonstration v7 (`demonstrations/demo_couche1_v7.py`, chargée à part et
inchangée, R12) jouée sous le **nul v8** du juge (`pole/nul_v8.py` : nul d'archive ajusté imposé, refus nommé sinon).

Seul changement de fond : la configuration du juge. La v7 construit `ConfigGeneration(...)` **sans** nul d'archive (ni
`nul_archive` ni `nul_archive_ajuste`) ; ici, dans l'instance chargée, `ConfigGeneration` est remplacé par
`nul_v8.configuration_nul_v8` (mêmes réglages, nul v8 imposé : nul d'archive et membres ajustés), et `executer_pole` repasse
chaque configuration à la garde `nul_v8.exiger_nul_v8` avant de jouer. Changements de nom seulement : le rapport s'écrit sous
`demo-couche1-v8-v1.json` (avec la provenance du nul et l'empreinte de la v7 chargée) et l'étiquette d'horodatage porte
« v8 ». Même banque réelle (T0.5 v2), mêmes fiches et témoins, mêmes bras, même graine (20261027).

Lecture fixée avant l'exécution (celle de la v7, inchangée, calculée par son code) :
- L1 : aucun témoin faux (loi sur le trait de bruit) promu, dans aucun bras ;
- L2 : les fiches promues sous « informe » sont un sous-ensemble de celles promues sous « aveugle » ;
- L3 : témoins vrais promus sous « aveugle » au moins pour moitié, sinon : pas de dents, pas de conclusion ;
- L4 : « urne » promeut au plus autant que « aveugle » ;
- F1 à F3 (bras « fraction », s'il est demandé) : comme en v7.

Usage : python -I -B demonstrations/demo_couche1_v8.py DOSSIER_NEUF [--generations 3] [--bras informe,aveugle,urne]
"""

import importlib.util
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

_CHEMIN_V7 = os.path.join(ICI, "demo_couche1_v7.py")
_spec = importlib.util.spec_from_file_location("demo_couche1_v7_pour_v8", _CHEMIN_V7)
v7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v7)  # instance propre (R12 : la démonstration v7 n'est pas touchée)

from pole import nul_v8  # noqa: E402  (appelé par attribut : une mutation du module est vue ici)
from pole.outils import sha256_fichier  # noqa: E402

VERSION = "demo-couche1-v8-v1"
RAPPORT_V7, RAPPORT_V8 = "demo-couche1-v7-v3.json", "demo-couche1-v8-v1.json"
_ecrire_v7, _executer_pole_v7 = v7.ecrire_json_scelle, v7.executer_pole


def configuration(**reglages):
    """Remplace `ConfigGeneration` dans l'instance v7 : mêmes réglages, nul v8 imposé (`NulV8Refuse` si contraire)."""
    return nul_v8.configuration_nul_v8(**reglages)


def executer_pole(population, temoins, adaptateur, config, *args, **kw):
    """Garde : aucune course de la démonstration v8 sans le nul v8 ; étiquette d'horodatage en v8."""
    nul_v8.exiger_nul_v8(config)
    if kw.get("horodatage_fourni"):
        kw["horodatage_fourni"] = f"{VERSION}, nul v8 (étiquette de la v7 : {kw['horodatage_fourni']})"
    return _executer_pole_v7(population, temoins, adaptateur, config, *args, **kw)


def ecrire_json_scelle(chemin, objet, ecraser=False):
    """Le rapport de la v7 s'écrit sous le nom de la v8, avec la provenance ; les autres fichiers passent tels quels."""
    if os.path.basename(chemin) == RAPPORT_V7:
        chemin = os.path.join(os.path.dirname(chemin), RAPPORT_V8)
        objet = dict(objet, demonstration=VERSION, nul_du_juge=nul_v8.description(),
                     demonstration_v7_chargee={"chemin": "demonstrations/demo_couche1_v7.py",
                                               "sha256": sha256_fichier(_CHEMIN_V7)})
    return _ecrire_v7(chemin, objet, ecraser=ecraser)


v7.ConfigGeneration = configuration
v7.executer_pole = executer_pole
v7.ecrire_json_scelle = ecrire_json_scelle


def principal(argv=None):
    print(json.dumps({"demonstration": VERSION, "nul_du_juge": nul_v8.description()}, ensure_ascii=False))
    return v7.principal(argv)


if __name__ == "__main__":
    sys.exit(principal())
