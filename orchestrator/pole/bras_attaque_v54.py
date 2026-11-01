"""Lots du bras d'attaque au pré-pilote (12 fiches « trop concrètes », classes C1 à C4 ; brouillon 7, « Bras d'attaque »,
DEP5) — **squelette qui refuse**, version 54.

Pourquoi ce n'est pas codé : les 12 fiches sont écrites chez session-depot sous scellés (schéma n° 208), selon ce que sa revue
de sécurité permet ; seuls reviennent des identifiants opaques, l'état « aiguillé » et la classe. L'orchestrateur de
conv-audit ne doit ni lire ni copier leur contenu (A9, A10, R-575) ; l'interface par laquelle session-depot les servirait à
l'aiguilleur (dans une session isolée, sans passer par la mémoire de l'orchestrateur) n'est pas spécifiée, et le mot de
Lazar sur l'étalonnage de l'aiguilleur (DEP5 ; défaut R-819 : pas d'étalonnage, qui ferme C7) est « À REMPLIR ».

Sans lot : M4 est déclarée « non étalonné (M4 sans témoins concrets) », état prévu par le brouillon 7 (Critères de lecture).
Avec une clé `prepilote.concrets` dans la configuration : refus de partir, motif exact ci-dessous (aucun repli silencieux).
"""

VERSION = "bras-attaque-v54 (squelette)"
MOTIF = ("prepilote.concrets : lots du bras d'attaque non branchés en v54 — interface de service par session-depot non "
         "spécifiée (schéma n° 208) et mot de Lazar sur l'étalonnage de l'aiguilleur (DEP5) absent ; retirer la clé (M4 « non "
         "étalonné ») ou attendre une version qui la branche")


def refuser_lots():
    return MOTIF
