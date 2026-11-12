# F01 — Écarts à la préinscription

Préinscription scellée : sha256 `b795ddbb677f732cbc9b232aa28bc17cc9e6d3d0d7da3dd5264881cc0127f305`, vérifié avant et
après le travail ; ni le texte ni son fichier `.sha256` n'ont été touchés.

## A. Statistique principale, garde `t_avance`, fichier `panel.csv`

**Aucun écart.** Données, schéma, ensembles K, U et T, étapes 1 et 2, agrégation, jackknife par année civile (40 blocs),
constante 2,12, garde : exécutés tels qu'écrits aux § 3, 4, 5.1, 5.2 et 5.3.

## B. Points ambigus de la préinscription : lecture retenue (la plus littérale) et autre lecture

Aucun de ces points ne touche un champ de `temoin.json`. Les points 1 à 3 concernent l'analyse secondaire S3, descriptive.

1. **S3 — sur quoi porte « la moyenne simple des `moy_origine` ».** Le § 5.4 ne dit pas sur quel ensemble la moyenne est prise.
   Lecture retenue (A) : une valeur par anomalie de l'échantillon S3 (moyenne simple entre anomalies, chaque `moy_origine` comptée une fois). Autres lectures calculées : (B) moyenne sur les lignes de l'échantillon
   S3 ; (C) moyenne sur les seules lignes « publiée ». Chiffres (descriptif) : rapport A = −0,0340 (erreur type jackknife
   0,1355) ; B = −0,0346 (0,1377) ; C = −0,0331 (0,1319). Dénominateurs : 0,6859 ; 0,6749 ; 0,7042 % par mois.
2. **S3 — anomalies de moins de 60 lignes `origine`.** Le § 5.4 définit l'échantillon S3 par les statuts sans citer K ; le § 3
   dit qu'une telle anomalie est « exclue de l'estimation ». Lecture retenue : la règle générale du § 3 s'applique (208
   anomalies, 87 594 lignes). Autre lecture (sans restriction, 212 anomalies, 88 724 lignes), descriptif : coefficient
   `attente` −0,2229 (0,0622), coefficient « publiée » −0,2570 (0,1290), différence −0,0340 (0,0927), rapport A −0,0496
   (0,1351), B −0,0503 (0,1372), C −0,0482 (0,1312). Avec la lecture retenue : −0,2410 (0,0642), −0,2643 (0,1332),
   différence −0,0233 (0,0929).
3. **S3 — sens de « leur différence ».** Non précisé. Retenu : coefficient « publiée » moins coefficient `attente`, conforme
   au § 1 (« l'effet propre à la publication est la différence des deux coefficients »). L'autre sens change seulement le signe.
4. **S1(b) — « T inchangé ».** U perd 2 388 lignes `attente` (année P−1) ; la définition de T dépend de U (anomalie et mois
   présents dans U). J'ai réappliqué la règle du § 5.1 au nouveau U. Vérification : l'ensemble T obtenu est **identique**,
   ligne à ligne, à celui de la statistique principale (9 942 lignes, 185 anomalies). Les deux lectures donnent donc les
   mêmes nombres sur l'échantillon complet ; dans les répliques du jackknife, T est redéfini par la même règle (§ 5.2).
5. **S2 — restriction de T dans le jackknife.** « T restreint aux anomalies ayant au moins une ligne `attente` dans U » : dans
   chaque réplique, j'ai pris U réduit (l'effet (anomalie, `attente`) n'existe pas autrement). Sur l'échantillon complet,
   la restriction ne retire aucune ligne (T = 9 942 lignes, 185 anomalies).
6. **« Un rendement mensuel absent (nul, NaN) ».** Lu comme « valeur nulle au sens de manquante (null) ou NaN », pas comme
   « égal à zéro ». Sans conséquence : le Parquet ne contient aucun rendement exactement égal à 0 (ni infini) ; les deux
   lectures donnent le même `panel.csv`.

## C. Ajouts non demandés par la préinscription (rien n'est retiré, rien ne touche le témoin)

7. **Nombres descriptifs supplémentaires**, tous étiquetés « descriptif » dans le rapport : erreur type jackknife de
   `b_attente` et de `tau_bar` (même formule que le § 5.2) ; rapport de `b_attente` à la moyenne des `moy_origine` (trois
   dénominateurs, la préinscription annonçant que la première prédiction de la fiche est « rapportée à titre descriptif »
   sans en fixer la formule) ; nombre effectif de blocs recalculé ; `theta_point` ; lectures B et C et variante sans K de S3
   (points 1 et 2).
8. **Fichiers supplémentaires** dans `F01/` : `construction.json` et `construire.log` (journal de `construire.py`),
   `analyse.log` et `resultats.json` (détail de `analyse.py`, répliques du jackknife comprises),
   `controle_independant.py` (seconde écriture de la statistique principale et de la garde, par projections alternées ;
   usage : `python3 -I controle_independant.py panel.csv` ; sert seulement à contrôler mes propres nombres). `temoin.json` ne contient
   que les quatorze champs préinscrits.

## D. Mentions exigées par le § 3 de la préinscription (ce ne sont pas des écarts)

- **Tailles des fichiers** : 183 100 et 1 439 671 octets, identiques aux tailles préinscrites. HTTP 200 au premier essai.
- **Prédicteur sans colonne dans le Parquet** : aucun. **Année vide** : aucune. 212 prédicteurs gardés dans `panel.csv`.
- **Anomalies de moins de 60 lignes `origine`, exclues de l'estimation, gardées dans `panel.csv`** (quatre) :
  `AnalystRevision` (58 lignes ; échantillon 1975-1980, rendements à partir de 1976-03),
  `ConsRecomm` (50 ; échantillon 1985-1997, rendements à partir de 1993-11),
  `DownRecomm` (49 ; 1985-1997, à partir de 1993-12),
  `UpRecomm` (49 ; 1985-1997, à partir de 1993-12).
  Conséquence sur les effectifs : 185 anomalies traitées au lieu des 189 attendues, 206 anomalies dans U au lieu de 210.
- **Fins de série observées** pour les exceptions citées : `Activism1`, `Activism2`, `Governance` s'arrêtent en 2007-02 ;
  `PatentsRD` en 2008-06 (les notes de version disent que les données de brevets s'arrêtent en 2006) ;
  `ProbInformedTrading` en 2013-12 (les notes disent 2012). Règle appliquée telle qu'écrite : une ligne partout où le
  rendement existe, rien d'ajouté ni de retiré.
