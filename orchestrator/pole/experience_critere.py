"""Première expérience du pôle : valider le critère de sélection par pari avant tout choix de moteur (simulation).

Écrit `controles-fatals-v1.{json,md}` et `duel-trois-bras-v1.{json,md}`, chacun avec son compagnon `.sha256`.
"""

import os

from .controles_pari import executer_controles, rapport_markdown as rapport_controles
from .duel_pari import executer_duel, rapport_markdown as rapport_duel
from .outils import EcrasementInterdit, ecrire_json_scelle, ecrire_scelle, manifeste


def executer_experience_critere(dossier, graine, quand, repetitions=1000):
    if os.path.exists(dossier) and os.listdir(dossier):
        raise EcrasementInterdit(f"le dossier de sortie existe et n'est pas vide : {dossier}")
    os.makedirs(dossier, exist_ok=True)
    ecrire_json_scelle(os.path.join(dossier, "manifeste.json"), manifeste(graine=graine, repetitions=repetitions,
                                                                          horodatage=quand))
    controles = executer_controles(graine, repetitions)
    ecrire_json_scelle(os.path.join(dossier, "controles-fatals-v1.json"), dict(controles, horodatage=quand))
    ecrire_scelle(os.path.join(dossier, "controles-fatals-v1.md"), rapport_controles(controles, quand))
    duel = executer_duel(graine)
    ecrire_json_scelle(os.path.join(dossier, "duel-trois-bras-v1.json"), dict(duel, horodatage=quand))
    ecrire_scelle(os.path.join(dossier, "duel-trois-bras-v1.md"), rapport_duel(duel, quand))
    return {"controles": controles["verdicts"], "duel": duel["regle_d_arret"]}
