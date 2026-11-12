# F04 — Écarts à la préinscription

Six écarts ou points de lecture, tous sans effet sur les dix nombres de `temoin.json`. Aucune ligne de D1 n'a été écartée pour
valeur de `security_term` inattendue ; aucune source n'a manqué ; aucune source de remplacement n'a été utilisée.

## E1. Dossier des fichiers bruts : `donnees/` au lieu de `brut/`

- **Préinscription (section 4)** : les fichiers bruts vont dans `tests-de-mort/F04/brut/`.
- **Fait** : ils sont dans `tests-de-mort/F04/donnees/`, avec `donnees/PROVENANCE.md`.
- **Raison** : la consigne donnée à l'expérimentateur par l'orchestrateur nomme `donnees/`. Contenu identique à ce que demande
  la préinscription (fichiers non modifiés, date et heure, sha256). Aucun effet sur les nombres.

## E2. Précision des valeurs de la courbe ajustée (D3)

- **Préinscription (section 4)** : colonnes SVENPY « rendement au pair, pour cent, quatre décimales ».
- **Constaté** : dans le fichier téléchargé, les lignes anciennes portent jusqu'à 15 décimales (exemple, 2010-01-12, SVENPY03 :
  `1.47749996185303`) ; dans le fichier d'analyse, les valeurs à plus de quatre décimales vont de 2010-01 à 2020-10, celles à
  quatre décimales ou moins de 2011-07 à 2026-09. Les colonnes sont les mêmes ; seule la description de la précision diffère.
- **Lecture retenue (la plus littérale)** : section 5, « recopiée sans arrondi ». Les chaînes de caractères du fichier source
  sont recopiées telles quelles dans `gsw_*`. Aucun arrondi à quatre décimales n'a été appliqué.
- **Autre lecture, non retenue** : arrondir `gsw_*` à quatre décimales avant le calcul. Nombres des deux lectures :

  | Nombre | Sans arrondi (retenu, `temoin.json`) | Arrondi à quatre décimales |
  |---|---|---|
  | `v_moyen_pb` | 0,9061063 | 0,9061059 |
  | `erreur_type_pb` | 0,1613530 | 0,1613530 |
  | `t_stat` | 5,615676 | 5,615674 |
  | `borne_sup_95_pb` | 1,2223582 | 1,2223578 |
  | `t_placebo_abs` | 0,270997 | 0,271003 |

  L'écart entre les deux lectures est inférieur à 0,000001 pb sur la moyenne, très en dessous des tolérances préinscrites.

## E3. `fenetre_propre` pour une ligne placebo : sens de « autre »

- **Préinscription (section 5)** : « aucune **autre** adjudication `reelle` de même `echeance` » dans [`date_jm5`, `date_jp5`].
- **Ambiguïté** : pour une ligne `reelle`, « autre » exclut la ligne elle-même. Pour une ligne `placebo`, le texte ne dit pas si
  « autre » exclut l'adjudication dont le placebo dérive.
- **Lecture retenue** : pour un placebo, toute adjudication `reelle` de même échéance dans la fenêtre compte, sans exception.
- **Les deux lectures donnent le même fichier** : l'adjudication d'origine est en J − 10 jours ouvrés du placebo, donc toujours
  avant `date_jm5` (J − 5). Résultat identique : 318 placebos à fenêtre propre sur 321.

## E4. Tri : ordre de `type_ligne` et départage

- **Préinscription (section 5)** : « trié par `date_adjudication`, `echeance`, `type_ligne` », sans préciser l'ordre de
  `type_ligne` ni un départage.
- **Fait** : `echeance` triée comme un entier ; `type_ligne` en ordre alphabétique (`placebo` avant `reelle`) ; `cusip` ajouté
  comme quatrième clé de départage. Ce départage n'a jamais servi (aucune paire de lignes n'a les trois mêmes clés). L'ordre
  des lignes n'a aucun effet sur les statistiques.

## E5. Compléments rapportés hors préinscription (descriptifs, hors `temoin.json`)

Le rapport contient quelques nombres que la préinscription ne demande pas. Ils sont étiquetés « hors préinscription » et
n'entrent ni dans `temoin.json` ni dans aucun champ de vérification :

- la moyenne de V sur P par échéance (10, 20, 30 ans), sans erreur type ;
- la borne basse de l'intervalle à 95 % (V̄ − 1,96 × ET), la médiane, les extrêmes et les quartiles de V ;
- la statistique principale et la pente S2 recalculées sans les deux réouvertures de 25 millions de dollars
  (`9128286T2_2019-06-21`, `912810TC2_2021-12-02`), que la préinscription inclut dans les 321 lignes et que le calcul
  préinscrit garde. **Raison** : ces deux lignes ont un montant mille fois plus petit que les autres ; dans S2 elles forment
  deux valeurs extrêmes de z (minimum −5,89). Le lecteur doit pouvoir voir ce qu'elles pèsent. Les nombres préinscrits restent
  ceux calculés avec les 321 lignes.

Fichiers ajoutés, non demandés : `construire_journal.json` (comptes et contrôles imprimés par `construire.py`) et
`resultats_analyse.json` (détail imprimé par `analyse.py`).

## E6. Points que la préinscription ne fixe pas, dans les analyses descriptives

Sans effet sur le verdict (analyses S1 à S3 et écart-type de V) :

- **Écart-type de V sur P** : la préinscription ne dit pas le dénominateur. Rapporté avec n − 1 (2,573 pb) ; avec n : 2,569 pb.
- **S2, fenêtre de référence** : « dans les 1 096 jours civils strictement avant » lu comme 1 ≤ (date de i − date de la ligne
  de référence) ≤ 1 096 jours. Les lignes de référence sont toutes les lignes `reelle` de même `echeance` du fichier d'analyse
  (nouvelles émissions et réouvertures, sans condition sur `complet` ni `fenetre_propre`), y compris les deux lignes de
  25 millions de dollars.
- **S2, nombre de grappes** : G = nombre de mois distincts parmi les lignes de la régression (126), pas parmi P entier (134).
- **S2, unité de la pente** : points de base de V par écart-type de r (z est centré-réduit).
