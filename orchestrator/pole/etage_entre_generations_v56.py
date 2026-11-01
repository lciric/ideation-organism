"""Étage entre générations, version 56 — machine jetable par **liste blanche** (CL20-14), au-dessus de la v55 (inchangée, R12).

La v55 refusait des **motifs** de noms de clé (liste noire) : `NETRC`, `MYSERVICE_APIKEY`, `X_PASSPHRASE`, `KUBECONFIG`,
`DOCKER_CONFIG`, `GIT_ASKPASS`, `KEYFILE`, `JWT`, `CI_JOB_JWT`, `BEARER`, `COOKIE` passaient. En v56, **tout nom** de variable
de l'environnement doit appartenir à la liste blanche fermée `NOMS_PERMIS` (réglages connus, sans secret) ou à la liste
**exacte** `etage_tests_de_mort.environnement_permis` de la configuration (aucun motif) ; un nom ajouté par la configuration
reste refusé s'il ressemble à une clé (liste noire de la v55, seconde barrière). Seuls les noms sont lus, jamais une valeur, sauf
la variable de déclaration.

**Variable de déclaration** : `POLE_MACHINE_JETABLE_V56=1` (posée par l'opérateur sur la machine louée jetable, sans secret,
détruite après chaque série ; déclarative : le devis de location et la destruction restent un contrôle de l'opérateur, au
registre du run). Le suffixe est la version de l'orchestrateur qui la lit ; les variables des versions précédentes
(`POLE_MACHINE_JETABLE_V53`, `_V54`) sont permises (sans effet) mais ne suffisent pas.
"""

import os

from .etage_entre_generations_v53 import MachineNonJetable
from .etage_entre_generations_v55 import nom_de_cle_v55

VERSION = "etage-entre-generations-v56"
VARIABLE_MACHINE_JETABLE = "POLE_MACHINE_JETABLE_V56"
NOMS_PERMIS = frozenset({
    "PATH", "HOME", "USER", "LOGNAME", "SHELL", "PWD", "OLDPWD", "SHLVL", "HOSTNAME", "TERM", "TZ", "_",
    "LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "LC_MESSAGES", "LC_NUMERIC", "LC_COLLATE", "LC_TIME", "LC_MONETARY",
    "TMPDIR", "TMP", "TEMP",
    "PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "PYTHONUTF8", "PYTHONUNBUFFERED",
    "TOKENIZERS_PARALLELISM", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "POLE_MACHINE_JETABLE_V53", "POLE_MACHINE_JETABLE_V54", VARIABLE_MACHINE_JETABLE, "POLE_ESSAI_BAC_REEL_NON_JOUE",
})


def exiger_machine_jetable_v56(environnement=None, permis_en_plus=()):
    env = os.environ if environnement is None else environnement
    if env.get(VARIABLE_MACHINE_JETABLE) != "1":
        raise MachineNonJetable(f"étage de tests de mort refusé : {VARIABLE_MACHINE_JETABLE}=1 absent (R-640 : machine louée jetable, "
                                "sans secret, détruite après chaque série ; contrôle de l'opérateur au registre)")
    en_plus = set(permis_en_plus or ())
    if any(not isinstance(n, str) or not n or any(c in n for c in "*?[]") for n in en_plus):
        raise MachineNonJetable("etage_tests_de_mort.environnement_permis : noms exacts seulement (aucun motif)")
    cles_ajoutees = sorted(n for n in en_plus if nom_de_cle_v55(n))
    if cles_ajoutees:
        raise MachineNonJetable("environnement_permis : nom de clé refusé même ajouté par la configuration (" + ", ".join(cles_ajoutees) + ")")
    inconnus = sorted(n for n in env if n not in NOMS_PERMIS and n not in en_plus)
    if inconnus:
        raise MachineNonJetable("étage de tests de mort refusé : variable hors de la liste blanche (" + ", ".join(inconnus[:20])
                                + ") ; la machine jetable ne porte que des réglages connus (CL20-14)")
    return True


def jouer_etage_v56(adaptateur, dossier_generation, *, reglages, environnement=None, executer=None, permis_en_plus=()):
    exiger_machine_jetable_v56(environnement, permis_en_plus)
    if executer is None:
        from .tests_de_mort_v3 import executer_tests_de_mort as executer
    resume = {}
    executer(adaptateur, dossier_generation, resume_sortie=resume, **reglages)
    return resume


__all__ = ("exiger_machine_jetable_v56", "jouer_etage_v56", "NOMS_PERMIS", "VARIABLE_MACHINE_JETABLE")
