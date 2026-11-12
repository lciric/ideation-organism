# H03 — course annulée pour erreur de préinscription (12 novembre 2026)

**Ce qui s'est passé.** La préinscription scellée (sha256 ea611aca…) associe la lettre `S` des millésimes de la base des
projections de la BCE à l'exercice de juin et la lettre `G` à celui de septembre. L'expérimentateur a constaté, dans les titres
des 111 fichiers et dans le premier trimestre projeté de chacun, que c'est l'inverse : `G` = juin, `S` = septembre.
Exécutée comme écrite, l'analyse range donc chaque année les exercices de juin et de septembre à l'envers : trois des quatre
révisions annuelles ne comparent pas deux exercices consécutifs, et l'une remonte le temps.

**Pourquoi aucune garde ne l'a arrêté.** Le contrôle de schéma n° 4 de la préinscription devait justement comparer le mois du
titre à la lettre. Il lit la colonne `TITLE`, vide dans la source ; le texte est dans `TITLE_COMPL`. Lu sur `TITLE_COMPL`, il est
violé sur 224 lignes.

**Décision de l'orchestrateur.** Les chiffres de cette course (corrélation moyenne de −0,06) mesurent un plan mal codé, pas
l'hypothèse. La course est **annulée** : son `verdict.json`, s'il est calculé, n'est pas le verdict de l'idée et n'entre ni dans
le registre des résultats ni dans la sélection. L'expérimentateur n'a pas calculé la statistique sous la bonne correspondance,
pour laisser aveugle la préinscription corrigée.

**Suite.** Une préinscription v2 (`tests-de-mort/H03-v2/`) reprend la v1 mot pour mot, sauf la correspondance des lettres et la
colonne lue par le contrôle n° 4. Elle est scellée, puis rejouée par un expérimentateur et un vérificateur neufs. Ce qui a été vu
avant de la sceller : les chiffres de la course annulée ci-dessus, et rien sous la bonne correspondance.

**Confirmation indépendante.** Le vérificateur, qui n'a lu que la préinscription et le fichier d'analyse, a relevé la même
anomalie sans connaître le constat de l'expérimentateur : dans le fichier, chaque millésime `S` a son premier trimestre projeté
un trimestre après son rang, chaque `G` un trimestre avant, et les lignes `S` à l'horizon 1 ont 54 % d'erreurs exactement nulles
(ce sont des estimations du trimestre en cours). Ses chiffres sont identiques à ceux de l'expérimentateur. `verdict.py` n'a pas
été lancé sur cette course : il n'y a pas de `verdict.json` pour H03 v1.
