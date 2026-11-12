# Course 2 — écarts

1. **Appel de Kimi en flux (12 novembre 2026).** Le premier appel du proposeur Kimi, sans flux, s'est terminé par une connexion
   fermée sans réponse (`RemoteDisconnected`) ; aucune fiche n'a été reçue ni lue. `appeler.py` a été modifié après son
   scellement pour appeler Kimi en flux et pour réessayer sur une coupure de connexion. La consigne, le modèle demandé, la garde
   du modèle servi et la borne de sortie sont inchangés. Nouveau sha256 de `appeler.py` dans `SCEAUX-apres-ecart-1.sha256`.

2. **Apostrophes normalisées dans le lot anonyme.** Un proposeur écrit avec l'apostrophe typographique, les autres avec
   l'apostrophe droite : ce signe trahissait la famille. Il a été remplacé par l'apostrophe droite dans le lot des juges, et
   seulement là ; les fichiers de fiches d'origine sont intacts. Limite qui reste : les six fiches de la course 1 citent des
   codes HTTP de sources testées, ce que les proposeurs sans outils de la course 2 ne pouvaient pas faire ; un juge attentif
   peut donc deviner de quelle course vient une fiche.
