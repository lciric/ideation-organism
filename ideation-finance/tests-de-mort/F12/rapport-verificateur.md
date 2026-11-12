# F12 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `analyse_F12.csv`, rien d'autre (ni code, ni résultats, ni journaux de l'expérimentateur).
Code : `verification.py` (écrit d'après le § 6.1, HC3 en formule fermée) ; sortie : `verification.json`.
Contrôle croisé : statsmodels `OLS(...).fit(cov_type="HC3")` redonne les mêmes pentes et erreurs types par régime
(se_b_avant = 0,3083, se_b_apres = 0,0687) à la précision machine.

## Lecture des points ambigus (lecture la plus littérale)

1. **Contrôle 1** : « dans cet ordre » porte sur les colonnes ; l'ordre des lignes n'est pas contrôlé (il est par ailleurs chronologique).
2. **Contrôle 3** : les effectifs 33/87/1/26 sont comptés en dates distinctes par valeur de `periode` ; les dates doivent être au format ISO `AAAA-MM-JJ`.
3. **Contrôle 4** : chaque ligne doit avoir une `periode` dont les bornes (§ 4.1) contiennent sa date ; une date entre deux plages (ex. entre 2012-09-06 et 2012-10-04) serait une violation.
4. **Contrôle 9** : appliqué à toutes les lignes, y compris `RIKSBANK`.
5. **Contrôle 10** : « inférieure à 300 » lu comme strict (`|v| < 300`), sur les cinq colonnes numériques, cellules renseignées seulement.
6. La règle « au moins quatre décimales » (§ 5) ne figure pas parmi les dix contrôles : non comptée dans `violations_schema`. Vérifiée quand même : toutes les cellules renseignées ont au moins quatre décimales (dix, en fait).
7. **`d_max_sans_une`** : retrait d'une réunion à la fois parmi les 113 réunions `avant` + `apres` ; seule la pente du régime touché est recalculée, l'autre reste celle de l'échantillon complet.
8. **`t_b_avant`** : `b_avant / sqrt(V_avant)` avec la variance HC3 du § 6.1 (pas d'autre correction de petits échantillons).
9. **Donnée manquante** : la règle du § 4.1 est codée (réunion retirée si x, IT ou ES manque) mais ne s'applique pas : aucune cellule `EAMPD` n'est vide.

## Contrôles de schéma

Les dix contrôles passent : `violations_schema = 0`. 882 lignes, 9 colonnes dans l'ordre, clé unique, six couples par date,
147 dates du 2010-01-14 au 2025-10-30, 33/87/1/26 dates par période, périodes cohérentes avec les bornes.

## Observations sur le fichier

- **Pas de doublon** : aucune réunion `EAMPD` n'a le même vecteur (OIS, DE, IT, ES, FR) qu'une autre. Quelques valeurs
  identiques de `d_ois2y_pb` entre réunions différentes (ex. −4,5 le 2013-07-04 et le 2014-09-04), avec des écarts différents :
  plausible (valeurs arrondies au dixième de point dans la base), pas une copie de lignes.
- **Riksbank** : 12 cellules vides exactement aux quatre dates annoncées (2012-06-06, 2013-06-06, 2019-06-06, 2024-06-06) ;
  85 réunions `avant` et 25 `apres` utilisables, comme attendu au § 4.2.
- **Valeurs extrêmes** : maximum 45,6 pb (IT, 2020-03-12), toutes bien sous 300. Écart entre réunions consécutives de 21 à
  57 jours : compatible avec un calendrier de réunions de politique monétaire (pas de réunion manifestement absente ou en trop,
  dans la mesure où le fichier seul permet d'en juger ; la liste des dates n'a pas pu être confrontée à une source externe).
- **Une réunion pèse lourd sur `b_avant` : le 2020-03-12** (surprise +6,56 pb, écart IT +45,8 pb, ES +16,95 pb ; la réunion de
  la phrase « nous ne sommes pas là pour resserrer les écarts »). Valeur plausible, pas une erreur, mais : sans elle,
  `b_avant` passe de 0,561 à 0,339 et `d` de −0,348 à −0,125. C'est elle qui donne `d_max_sans_une = −0,125`
  (au-dessus du seuil de taille −0,15, mais toujours négatif). Son poids passe par le résidu, pas par le levier
  (levier modeste) ; elle gonfle aussi fortement `se_b_avant` (HC3), donc `se_d`.
- **Après le TPI, deux réunions portent plus de la moitié de la variance du régresseur** : 2022-10-27 (x = −19,5) et
  2022-12-15 (x = +18,45), leviers 0,29 et 0,32 ; nombre effectif `(Σx²)²/Σx⁴` ≈ 6,3 (≈ 14,7 avant), conforme à la crainte du § 7.
- **`se_d` = 0,316**, nettement au-dessus de la fourchette supposée au § 7 (0,13 à 0,22) ; l'essentiel vient de la période
  d'avant (se_b_avant = 0,308 contre 0,11 à 0,18 supposé), en grande partie à cause du 2020-03-12.
