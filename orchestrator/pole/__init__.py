"""Pôle « scientifique automatique », version 0 : fiches gelées, expérimentateurs et vérificateurs, sélection par
sévérité ou par pari, mesure de qualité sur témoins, mémoire, recombinaison bisociative corrigée.

Version 0.2.0 (dossier `orchestrateur-pole-v2`) : juge v1 de la sélection par pari (ordre d'exécution secret,
membre « urne », loi « sans remise », garde du plan d'exécution) et contrôles de l'expérience 1 du pôle
(`controles_pari_v1.py`, `experience_juge_v1.py`). La version 0 reste dans `orchestrateur-v0` (jamais écrasée).

Version 0.3.0 (dossier `orchestrateur-pole-v3`) : le cycle du pôle juge par défaut avec le juge v1 (expérience 1 :
socle adopté) et le nul des filles v2 (`nul_filles_v2.py`, expérience 2 : adopté) ; l'ordre d'exécution secret est tiré
par le noyau après le gel et imposé à l'expérimentateur (`ordre-execution.json`). v2 reste dans `orchestrateur-pole-v2`.

Version 0.4.0 (dossier `orchestrateur-pole-v4`) : mémoire prédictive en sélection par pari (signature brute sur une
sonde fixe, classes, héritage de la preuve ; essais de la mémoire, pistes 1 et 2) ; filles éprouvées sur 300 tirages par
défaut (`taille_plan_filles`). v3 reste dans `orchestrateur-pole-v3`.

Version 0.5.0 (dossier `orchestrateur-pole-v5`) : seuil de la signature à 5 % de fausses fusions par fiche (calibré sur la
taille de l'archive) ; graine du noyau tirée par `secrets` pour une exécution réelle (`noyau_secret`) ; vivier de
démonstration de 30 fiches. v4 reste dans `orchestrateur-pole-v4`.

Version 0.6.0 (dossier `orchestrateur-pole-v6`) : premier lancement réel préparé sans dépense — monde tenu par le noyau
(`monde_noyau.py` : issues déposées après le gel, comparées aux issues déclarées), relais de clé réel (`relais_reel.py` :
serveur local qui remplace le jeton factice par la clé lue dans son seul environnement, plafond de dépense côté relais),
répétition générale avec un faux moteur (`essais/faux_sdk/`), ligne de commande complète. v5 reste dans
`orchestrateur-pole-v5`.

Cœur en bibliothèque standard ; numpy n'est importé que par le nul des filles v2 (membres ajustés) ; `claude_agent_sdk`
n'est importé que par l'adaptateur réel, au premier lancement.
"""

__version__ = "0.7.0"
