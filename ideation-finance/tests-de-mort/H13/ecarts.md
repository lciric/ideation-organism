# H13 — écarts à la préinscription

Quatre écarts, tous de forme ou d'outillage. Aucun ne change une règle d'échantillon, une variable ou une formule. Aucune
source n'a été remplacée par une autre.

## Écart 1 — dossier des fichiers bruts : `donnees/` au lieu de `brut/`

- **Préinscription (section 4)** : « L'expérimentateur enregistre chaque fichier brut dans `tests-de-mort/H13/brut/` ».
- **Fait** : les fichiers bruts sont dans `tests-de-mort/H13/donnees/`, avec `donnees/PROVENANCE.md`.
- **Raison** : la consigne de l'orchestrateur à l'expérimentateur nomme `donnees/`. Seul le nom du dossier change.
- **Effet sur les nombres** : aucun.

## Écart 2 — D5 pris avec `curl`, et `SVENY02` porte douze décimales au lieu de quatre

- **Préinscription (section 4, D5)** : l'adresse répond 200 ; `SVENY02` est décrit « pour cent, quatre décimales ».
- **Fait** : la même adresse (`https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv`) a renvoyé cinq fois
  « 403 Forbidden » à `urllib` de Python (agent par défaut), puis 200 à `curl` (agent par défaut), trois fois de suite avec
  la même taille (16 672 370 octets). Le fichier gardé est la dernière copie reçue par `curl`. Dans ce fichier, `SVENY02` a
  jusqu'à douze décimales (par exemple 8,223437582855 le 1990-02-02), non quatre.
- **Lecture retenue** : la plus littérale du schéma (« `SVENY02` à `date_publication`, pour cent ») : la valeur est recopiée
  telle quelle, sans arrondi. Le contrôle n° 9 passe : 8,1466 et 8,2234 à 0,0001 près le 1990-02-01 et le 1990-02-02.
- **Effet sur les nombres** : aucun. `SVENY02` n'entre dans aucune statistique ; il ne sert qu'au contrôle d'alignement.

## Écart 3 — un fichier de plus : le menu des millésimes de `UNRATE`

- **Préinscription (section 4, étape 2)** : « Recoupement : les trois corrections sont les seules dates absentes du menu de
  `UNRATE` ». Ce menu n'est pas dans la liste D1 à D5.
- **Fait** : la page `https://alfred.stlouisfed.org/series/downloaddata?seid=UNRATE` a été téléchargée
  (`donnees/D1b_UNRATE_downloaddata.html`) pour faire ce recoupement et pour écarter le piège signalé pour D3 (une date qui
  n'est pas un millésime ne produit pas d'erreur). Elle l'a été avant l'étape 6, donc avant tout taux. `construire.py` ne
  la lit pas.
- **Résultat du recoupement** : des 438 dates de `PAYEMS` de la fenêtre, les seules absentes du menu de `UNRATE` sont
  2002-12-09, 2003-10-10 et 2020-05-11, comme attendu. (Dans l'autre sens, `UNRATE` a un millésime 2024-01-10 absent de
  `PAYEMS` ; il n'est demandé nulle part.)
- **Effet sur les nombres** : aucun.

## Écart 4 — `d_chomage_pt` arrondi à une décimale à l'écriture

- **Préinscription (sections 4 et 5)** : `d_chomage_pt` = U(m) − U(m − 1), « décimal », points de pourcentage ; la section 6
  demande un calcul « sans arrondi intermédiaire ».
- **Fait** : les deux taux lus ont une décimale ; leur différence en double précision porte un artefact binaire (par exemple
  5,3 − 5,4 = −0,10000000000000053). `construire.py` arrondit cette différence à une décimale avant de l'écrire (−0.1).
- **Raison** : écrire dans le fichier la valeur exacte de la différence de deux nombres à une décimale, et non son
  approximation binaire.
- **Les deux lectures, chiffrées** : écart maximal entre les deux colonnes : 1,8 × 10⁻¹⁵ point. Avec arrondi (fichier
  livré) : β = 2,315513324801481, erreur type = 0,9447525999001786. Sans arrondi : β = 2,3155133248014805, erreur type =
  0,9447525999001783. Différence de l'ordre de 10⁻¹⁵, soit douze ordres de grandeur sous la tolérance de 0,005.

## Points de lecture qui ne sont pas des écarts

Notés pour que le vérificateur sache ce qui a été fait ; la lecture retenue est la lecture littérale et aucune autre lecture
du texte n'a été trouvée.

- **D3** : les dates demandées sont les 435 dates de publication de l'étape 2 (du 1989-12-08 au 2026-03-06), comme l'écrit
  la préinscription ; seules les 431 de la fenêtre 1990-2025 servent.
- **Étape 5** : prec(w) est la publication précédente, jamais un millésime de correction. Une correction qui retouche des
  mois anciens fait donc classer « de révision large » la publication suivante (cas de 2003-01-10 et de 2020-06-05).
- **`temoin.json`** : les neuf champs seulement ; pas de clé `descriptif` (la préinscription la dit facultative, la consigne
  de l'orchestrateur demande exactement les neuf champs). S1 à S3 sont dans `resultats_detail.json` et dans le rapport.
- **Heure de D5** dans `PROVENANCE.md` (19:04:30Z) : c'est l'heure de la copie du fichier dans `donnees/`, moins d'une
  minute après la fin du téléchargement par `curl`.
