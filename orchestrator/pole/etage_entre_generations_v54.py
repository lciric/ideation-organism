"""Étage de tests de mort entre deux générations, version 54 — machine jetable durcie (CL18-13).

L'étage lui-même et la préparation du dossier sont ceux de la v53 (`etage_entre_generations_v53`, inchangé) et de la v52b
(`tests_de_mort_v3`, inchangé). La v54 change seulement le contrôle de la machine jetable :

- variable `POLE_MACHINE_JETABLE_V54` = `1` (posée par l'opérateur ; **déclarative** : elle ne prouve rien par elle-même ;
  le devis de location et la destruction après chaque série restent un contrôle de l'opérateur, consigné au registre du run) ;
- refus si **un nom** de variable de l'environnement ressemble à une clé : liste du relais, `KIMI_API_KEY`,
  `MOONSHOT_API_KEY`, et tout nom qui contient `SECRET`, `TOKEN`, `PASSWORD`, `PASSWD`, `CREDENTIAL`, `API_KEY`,
  `ACCESS_KEY`, `PRIVATE_KEY`, ou qui finit par `_KEY` (couvre `AWS_ACCESS_KEY_ID`, `GOOGLE_APPLICATION_CREDENTIALS`,
  `*_PASSWORD`, que la liste v53 laissait passer). Aucune valeur n'est lue, sauf celle de la variable de la machine jetable.
"""

import os

from .etage_entre_generations_v53 import MachineNonJetable, NOMS_DE_CLE_EN_PLUS
from .relais import noms_de_cle_presents

VERSION = "etage-entre-generations-v54"
VARIABLE_MACHINE_JETABLE = "POLE_MACHINE_JETABLE_V54"
MORCEAUX_DE_CLE = ("SECRET", "TOKEN", "PASSWORD", "PASSWD", "CREDENTIAL", "API_KEY", "ACCESS_KEY", "PRIVATE_KEY")


def nom_de_cle(nom):
    n = nom.upper()
    return n in NOMS_DE_CLE_EN_PLUS or any(m in n for m in MORCEAUX_DE_CLE) or n.endswith("_KEY")


def exiger_machine_jetable_v54(environnement=None):
    env = os.environ if environnement is None else environnement
    if env.get(VARIABLE_MACHINE_JETABLE) != "1":
        raise MachineNonJetable(f"étage de tests de mort refusé : {VARIABLE_MACHINE_JETABLE}=1 absent (R-640 : machine louée "
                                "jetable, sans secret, détruite après chaque série ; contrôle de l'opérateur au registre)")
    presents = set(noms_de_cle_presents(env)) | {n for n in env if nom_de_cle(n)}
    if presents:
        raise MachineNonJetable("étage de tests de mort refusé : nom de variable de clé présent (" + ", ".join(sorted(presents))
                                + ") ; la machine jetable ne porte aucun secret")
    return True


def jouer_etage_v54(adaptateur, dossier_generation, *, reglages, environnement=None, executer=None):
    """Machine jetable vérifiée (v54), puis l'étage v3 inchangé."""
    exiger_machine_jetable_v54(environnement)
    if executer is None:
        from .tests_de_mort_v3 import executer_tests_de_mort as executer
    resume = {}
    executer(adaptateur, dossier_generation, resume_sortie=resume, **reglages)
    return resume
