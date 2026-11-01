"""Étage de tests de mort, **version 3** (orchestrateur v52b) : la version 2 (`pole/tests_de_mort_v2.py`) **telle quelle**
(R12 : aucun octet changé), plus la seule correction du constat CL16-01 de la contre-lecture CL16.

CL16-01 — à la borne mémoire minimale que la version 2 autorise (`MEMOIRE_BAC_MIN_MO = 512`), la sonde des privilèges
`disponible()` est tuée par le groupe de contrôle du bac (code 137) et l'étage est refusé : la configuration minimale documentée
ne démarre pas. L'artefact `MEMOIRE-BAC` de la sonde touche délibérément 5/4 de la borne ; sous la borne la plus basse, c'est le
processus racine de la sonde qui meurt, pas seulement ses enfants.

Mesures (sous le vrai `bwrap` 0.9.0, noyau Linux 6.18.44, cgroup v1, noyau superutilisateur, utilisateur dédié 64097) :
CL16 : 512 Mo refusé 3/3 ; 640, 768 et 1 024 Mo acceptés 3/3. Session de la v52b (30 octobre 2026) : 512, 544, 576 et 608 Mo
refusés (2 ou 3 passages chacun, code 137) ; 640, 768 et 1 024 Mo acceptés. Correction retenue (la première de CL16) : la borne
minimale passe à **768 Mo** (la plus basse acceptée, 640, plus une marge de 20 %), et un essai réel joue la sonde **à exactement
cette borne** (`essais/test_v52b_borne_memoire.py`). Le reste de l'étage (sonde, artefact `MEMOIRE-BAC`, filtre, groupe de
contrôle) est celui de la version 2.

SUPPOSÉ : la marge de 768 Mo tient sur la machine louée jetable (autre noyau, peut-être cgroup v2) ; l'essai réel à la borne
minimale est à rejouer là-bas avant tout GO de l'étage.
"""

from . import tests_de_mort_v2 as _v2
from .tests_de_mort_v2 import *  # noqa: F401,F403  (la version 2 telle quelle : mêmes objets)

MEMOIRE_BAC_MIN_MO = 768  # v52b (CL16-01) : la sonde des privilèges tient à cette borne (mesuré : refus jusqu'à 608, accepté dès 640)
MEMOIRE_BAC_MIN_MO_V2 = _v2.MEMOIRE_BAC_MIN_MO  # 512 : la borne de la version 2, à laquelle la sonde s'auto-tue (CL16-01)


class ExecuteurBacASable(_v2.ExecuteurBacASable):
    """Le vrai bac à sable de la version 2, avec la borne mémoire minimale de la version 3 (CL16-01) : en dessous, l'étage est
    refusé **avant** la sonde, motif dit (aucun repli)."""

    def verifier_outils(self):
        if self.borne_memoire_active() and self.memoire_mo < MEMOIRE_BAC_MIN_MO:
            return (f"mémoire du bac {self.memoire_mo} Mo < {MEMOIRE_BAC_MIN_MO} Mo : sous cette borne, la sonde des privilèges est "
                    "tuée par le groupe de contrôle du bac (CL16-01 : refus à 512-608 Mo, mesuré) : étage refusé ; donner au moins "
                    f"{MEMOIRE_BAC_MIN_MO} Mo")
        return super().verifier_outils()

    def description(self):
        d = dict(super().description())
        d["memoire_bac_min_mo"] = MEMOIRE_BAC_MIN_MO
        d["version_etage"] = "tests_de_mort_v3 (v52b, CL16-01)"
        return d
