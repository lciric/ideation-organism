"""Étage entre générations, version 55 — machine jetable (CL19-11), au-dessus de la v54 (inchangée, R12).

La v54 refusait à tort `TOKENIZERS_PARALLELISM` (« TOKEN » dans le nom) et laissait passer `GH_PAT`, `OPENAI_KEY_FILE`,
`SSH_AUTH_SOCK`, `AUTH`, `NPM_CONFIG__AUTH`. En v55, un nom est une clé s'il l'était en v54 **ou** s'il finit par `_PAT`,
contient `_KEY_` ou finit par `_KEY_FILE`, est `SSH_AUTH_SOCK`, vaut `AUTH` ou finit par `_AUTH` ; sauf les noms de la liste
fermée `NOMS_SANS_SECRET` (réglages connus qui ne portent aucun secret). Seuls les noms sont lus (aucune valeur, sauf celle
de la variable de la machine jetable). Contrôle **déclaratif** : le devis et la destruction restent un contrôle de
l'opérateur, au registre.
"""

import os

from .etage_entre_generations_v53 import MachineNonJetable
from .etage_entre_generations_v54 import VARIABLE_MACHINE_JETABLE
from .etage_entre_generations_v54 import nom_de_cle as nom_de_cle_v54
from .relais import noms_de_cle_presents

VERSION = "etage-entre-generations-v55"
NOMS_SANS_SECRET = frozenset({"TOKENIZERS_PARALLELISM"})


def nom_de_cle_v55(nom):
    n = nom.upper()
    if n in NOMS_SANS_SECRET:
        return False
    return (nom_de_cle_v54(nom) or n.endswith("_PAT") or "_KEY_" in n or n == "SSH_AUTH_SOCK" or n == "AUTH"
            or n.endswith("_AUTH"))


def exiger_machine_jetable_v55(environnement=None):
    env = os.environ if environnement is None else environnement
    if env.get(VARIABLE_MACHINE_JETABLE) != "1":
        raise MachineNonJetable(f"étage de tests de mort refusé : {VARIABLE_MACHINE_JETABLE}=1 absent (R-640 : machine louée "
                                "jetable, sans secret, détruite après chaque série ; contrôle de l'opérateur au registre)")
    presents = (set(noms_de_cle_presents(env)) - NOMS_SANS_SECRET) | {n for n in env if nom_de_cle_v55(n)}
    if presents:
        raise MachineNonJetable("étage de tests de mort refusé : nom de variable de clé présent (" + ", ".join(sorted(presents))
                                + ") ; la machine jetable ne porte aucun secret")
    return True


def jouer_etage_v55(adaptateur, dossier_generation, *, reglages, environnement=None, executer=None):
    exiger_machine_jetable_v55(environnement)
    if executer is None:
        from .tests_de_mort_v3 import executer_tests_de_mort as executer
    resume = {}
    executer(adaptateur, dossier_generation, resume_sortie=resume, **reglages)
    return resume


__all__ = ("nom_de_cle_v55", "exiger_machine_jetable_v55", "jouer_etage_v55", "NOMS_SANS_SECRET")
