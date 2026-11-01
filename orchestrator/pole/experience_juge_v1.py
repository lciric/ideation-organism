"""Expérience 1 du pôle : le juge v1 contre la dérive non modélisée (simulation à vérité connue, processeur).

Écrit, dans un dossier absent ou vide, `manifeste.json`, `experience-1-juge-v1.json` et `experience-1-juge-v1.md`, chacun
avec son compagnon `.sha256` (R6 ; rien n'est jamais écrasé, R12). Le manifeste est écrit **avant** tout calcul.
"""

import os
import time

from .controles_pari_v1 import executer_controles_v1, rapport_markdown, verifier_parametres
from .outils import EcrasementInterdit, ecrire_json_scelle, ecrire_scelle, manifeste


def executer_experience_juge_v1(dossier, graine, quand, repetitions=1000, essai=False, familles=None):
    verifier_parametres(graine, repetitions, essai, familles)
    if os.path.exists(dossier) and os.listdir(dossier):
        raise EcrasementInterdit(f"le dossier de sortie existe et n'est pas vide : {dossier}")
    os.makedirs(dossier, exist_ok=True)
    nom = "experience-1-juge-v1" + ("-ESSAI" if essai else "")
    ecrire_json_scelle(os.path.join(dossier, "manifeste.json"), manifeste(
        experience="expérience 1 du pôle — juge v1", graine_maitresse=graine, repetitions=repetitions, essai=essai,
        familles=sorted(familles) if familles else "toutes", horodatage=quand))
    debut = time.monotonic()
    r = executer_controles_v1(graine, repetitions, essai=essai, familles=familles)
    r["duree_calcul_s"] = round(time.monotonic() - debut, 1)
    ecrire_json_scelle(os.path.join(dossier, f"{nom}.json"), dict(r, horodatage=quand))
    ecrire_scelle(os.path.join(dossier, f"{nom}.md"), rapport_markdown(r, quand))
    return r["verdicts"]
