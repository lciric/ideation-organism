# F04-bis — constats demandés et écarts à la préinscription

Rédigé par l'expérimentateur le 2026-11-12. Préinscription scellée : sha256
`f5f4b98dc3c87fdbc49738e7b0e84992219ace991bb8e1b59191338cafe5c78a` (vérifié avant de commencer, inchangé à la fin).

## A. Constats que la préinscription demande d'écrire avant tout calcul (section 3)

Ces trois constats ont été faits sur le fichier brut B, juste après son téléchargement (2026-11-12T17:31:28Z), en ne
regardant que la forme des cellules (gabarits de chiffres, comptes de lignes). Cette partie A a été écrite dans ce fichier
après l'exécution de `construire.py` (qui recopie les taux et exécute les contrôles de schéma) et **avant** l'écriture et
l'exécution de `analyse.py` : aucune valeur de V ni de D n'existait à ce moment. Voir l'écart E1.

1. **Format des dates.** `M/J/AAAA`, mois d'abord, sans zéro initial (première ligne `10/1/2020`, dernière `9/30/2021`).
   Gabarits rencontrés : `9/99/9999` (133 lignes), `9/9/9999` (56), `99/99/9999` (42), `99/9/9999` (20). Les deux lectures
   ont été essayées par le script : la lecture mois/jour donne 251 dates toutes comprises entre 2020-10-01 et 2021-09-30 ;
   la lecture jour/mois échoue (par exemple `9/24/2021` n'est pas une date). Une seule lecture convient : elle est retenue,
   comme le prévoit la préinscription. Les dates sont en ordre croissant dans le fichier, sans doublon.
2. **Unité et décimales.** Pour cent par an (confirmé par le contrôle 8 : les 71 taux HS du fichier d'analyse sont égaux aux
   taux FRED, écart maximal 0,00). **Deux décimales au plus**, zéros finaux supprimés : sur 251 lignes, la colonne HS 10 ans
   a 231 valeurs à deux décimales et 20 à une ; HS 20 ans 232 / 18 / 1 (zéro décimale) ; HS 30 ans 220 / 29 / 2 ; MC 10 ans
   225 / 26 / 0 ; MC 20 ans 235 / 15 / 1 ; MC 30 ans 228 / 19 / 4. Aucune cellule vide ou non numérique dans les six colonnes
   utilisées. Conséquence annoncée par la préinscription (section 6) : D ne prend que des valeurs entières en points de base
   et l'arrondi à 0,01 point entre dans le bruit de D.
3. **Nombre de dates.** 251 lignes de données, 251 dates distinctes, du 2020-10-01 au 2021-09-30 : c'est le nombre attendu.
   Calendrier C du premier test (dates où `DGS10` n'est pas vide, fichier `F04/donnees/DGS10.csv`) : 251 jours dans
   l'exercice ; **0 jour de C absent du fichier B**, et 0 date de B absente de C.

Autres constats de forme : 35 colonnes, noms identiques à ceux lus par le rédacteur ; marque d'ordre d'octets UTF-8 présente ;
252 fins de ligne, toutes CRLF ; séparateur virgule.

## B. Écarts

Cinq points, E1 à E5 (quatre écarts de procédure ou de périmètre et une ambiguïté de lecture). Aucun ne change un des douze champs de `temoin.json`.

**E1 — Moment d'écriture des constats de la partie A.** La préinscription demande de les écrire dans ce fichier « avant
tout calcul ». Ils ont été constatés avant tout calcul (inspection de la seule forme des cellules du fichier B), mais
écrits ici après l'exécution de `construire.py`, qui recopie les taux et exécute les contrôles de schéma (donc calcule des
écarts `hs − mc` et `hs − cmt`), et avant l'écriture de `analyse.py`. Raison : ordre de travail de l'expérimentateur. Aucun
V ni aucun D n'avait été calculé à ce moment, et le format retenu est le seul qui passe le critère préinscrit.

**E2 — Le fichier A est lu par une copie.** La préinscription nomme `tests-de-mort/F04/F04_analyse.csv`. `construire.py` lit
`donnees/F04_analyse.csv`, copie octet pour octet (sha256 identique, `90d2cabe…cac9`, revérifié par le script à chaque
exécution), pour que tout ce qui entre dans la construction soit dans `F04-bis/donnees/`. De même `donnees/DGS10.csv` est
une copie de `F04/donnees/DGS10.csv` (sha256 `0a191454…5bb4`), utilisée seulement pour compter les jours du calendrier C.

**E3 — S3 : trois points que la préinscription ne fixe pas** (analyse descriptive, sans effet sur le verdict).
- *Dénominateur de l'écart-type* : non précisé. Les deux sont rapportés ; N − 1 est mis en avant, N figure dans
  `resultats_analyse.json`. La différence est à la troisième décimale (par exemple 0,674 contre 0,672 pb à 10 ans).
- *D(t) par échéance ou toutes échéances réunies* : la phrase commence par « pour chaque échéance » ; la lecture retenue est
  que cela vaut aussi pour D(t). Les deux sont rapportés : par échéance (241 dates chacune) et les trois réunies (723 valeurs).
- *« t − 5 » et « t + 5 »* : pris comme cinq lignes avant et cinq lignes après dans le fichier B trié par date. Le fichier B
  ayant exactement les 251 jours du calendrier C, c'est aussi cinq jours de C.

**E4 — Chiffres et fichiers en plus de ce qui est demandé.** Sans effet sur le verdict, tous descriptifs :
`construire_journal.json` (comptes par filtre, constats de forme, résultat des neuf contrôles) et `resultats_analyse.json`
(S1 à S3 et détail par ligne) ; moyennes de D, V_HS et V_MC par mois (les grappes) ; le test de Student sur les huit
moyennes mensuelles de D, que la préinscription cite comme « à très peu près » équivalent, calculé pour contrôler
l'arithmétique de l'erreur type groupée (moyenne 0,81 pb, erreur type 0,15 pb, contre 0,78 et 0,14 pour la statistique
préinscrite) ; écarts-types de V_HS et de V_MC et erreur type groupée de V_HS ; moyenne de HS − MC par échéance sur
l'exercice. La préinscription limite les analyses secondaires à trois : ces chiffres ne sont pas une quatrième analyse
avec une conclusion, mais ils n'étaient pas demandés, donc ils sont déclarés ici.

**E5 — Ambiguïté : la ligne hors exercice (10 ans, 2020-10-07).** La préinscription écrit : « Pour une date hors de
l'exercice, `hs_*` et `mc_*` restent vides. » Lecture retenue, la plus littérale : seule la date hors exercice est vidée
(`hs_jm5` et `mc_jm5`, date 2020-09-30) ; `hs_j`, `hs_jp5`, `mc_j`, `mc_jp5` de cette ligne sont remplis, car leurs dates
(2020-10-07 et 2020-10-15) sont dans l'exercice. Autre lecture possible : vider les six cellules de la ligne. Effet des deux
lectures : aucun sur P (la ligne en est exclue dans les deux cas, `dans_exercice` = 0 et `complet` = 0) ni sur les douze
champs. Seul le nombre de paires examinées par les contrôles 7 et 8 change : 71 paires avec la lecture retenue, 69 avec
l'autre ; les deux paires en question valent HS = MC = FRED (0,81 et 0,74), donc les contrôles passent à l'identique.

## C. Points vérifiés qui ne sont pas des écarts

- 24 lignes à l'étape 1, 23 avec `dans_exercice` = 1, 23 dans P, 8 mois : ce sont les nombres attendus. Les 24 dates
  d'adjudication sont celles du tableau de la préinscription.
- Les colonnes du fichier B sont exactement les 35 lues par le rédacteur. Aucun taux manquant ; aucune valeur cherchée ailleurs.
- Les taux HS et MC sont recopiés « tels qu'écrits » : le fichier B supprime les zéros finaux, donc on lit `1.4` dans `hs_j`
  à côté de `1.40` dans `cmt_j`. Les taux `cmt_*` et `gsw_*` sont recopiés du fichier A caractère pour caractère.
- Le fichier B n'a été téléchargé qu'une fois (HTTP 200 à la première tentative) ; aucune source de remplacement.
- Aucun fichier scellé n'a été modifié (`sha256sum -c preenregistrement.md.sha256` : OK en fin de travail).
