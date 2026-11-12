# H16 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `analyse_H16.csv`, rien d'autre. Code : `verification.py` (écrit d'après le § 5
et le § 6 du préenregistrement). Je n'ai vu ni le code ni les nombres de l'expérimentateur.

## Nombres (`verification.json`)

| champ | valeur |
|---|---|
| n_eval | 147 |
| n_estim_init | 151 |
| r2_oos | −0,004554 |
| cw_fbar | 0,047940 |
| cw_se | 0,081081 |
| cw_t | 0,5913 |
| cw_t_min_sans_une | 0,1629 |
| zone_grise | 0 |
| violations_schema | 0 |

Contrôle interne : l'identité `f_t = 2 · e0_t · d_t` est vérifiée numériquement. Tailles de `A_t` : 151 pour la
première réunion d'évaluation, 297 pour la dernière, comme annoncé.

## Lecture des points ambigus

1. **« 315 lignes »** (contrôle 1) : lu comme 315 lignes de données plus l'en-tête (le fichier compte 316 lignes physiques).
2. **Écart-type des « 16 rangs précédents »** (contrôle 5) : rangs `t−16 … t−1` du fichier, rodage compris, dénominateur 15,
   sans exclure les zéros exacts.
3. **Contrôle 8, « partout où une colonne `date_fin_*` est renseignée »** : appliqué à toutes les lignes, y compris le rodage.
   Aucun effet : toutes les dates renseignées sont antérieures de 1 à 7 jours.
4. **Contrôle 10, « un prédicteur manque »** : cellule vide ou non numérique. Aucune ligne n'est concernée.
5. **`A_t` « de date strictement antérieure »** : appliqué aux dates. Comme les dates sont strictement croissantes, cela revient
   à prendre les rangs antérieurs.
6. **`cw_t_min_sans_une`** : les prévisions ne sont pas refaites, on retire seulement `f_t`, comme le texte l'exige.

Aucune ambiguïté ne donne deux nombres différents.

## Contrôles de schéma

Les 10 contrôles ont pu être faits sur le fichier tel qu'il est, et aucun n'échoue. Le contrôle 8 ne vérifie que les dates
déclarées dans le fichier. Je n'ai pas pu vérifier la construction des prédicteurs à partir des séries brutes, car cela
demande `donnees/`, que je n'ai pas le droit d'ouvrir.

## Anomalies et points à signaler

- **Pas de doublon de réunion ; aucune date de prédicteur le jour de la réunion ou après** (écart de 1 à 7 jours).
- **Le plancher de 0,25 pb ne joue jamais** (0 réunion). Il passe toutefois très près au printemps 2019 :
  `sigma16_pb` = 0,280 le 2019-04-10 et 0,284 le 2019-06-06.
- **Cibles extrêmes dues à une petite volatilité passée** :
  - **2019-06-06** : 2,68 pb / 0,284 = **9,42 écarts-types**, le maximum de l'échantillon ;
  - **2015-12-03** : 9,88 pb / 1,28 = **7,72** ;
  - **2019-09-12** : **7,38** ;
  - **2011-03-03** : **6,23**.

  C'est l'effet de la normalisation annoncé au § 9.4, pas une erreur d'échelle. `d_ois1y_pb` reste en pb plausibles
  (de −17,6 à 20,3).
- **Réunions qui pèsent le plus.** `Σ f_t` vaut 7,05 au total.
  - **2015-12-03** apporte +5,31, soit 75 % du total ; sans elle, `cw_t` = 0,16, et c'est ce minimum.
  - **2019-06-06** apporte +4,68 (66 %).
  - Suivent 2016-01-21 (+2,30), 2022-10-27 (+1,80) et 2011-05-05 (+1,33).
  - En sens inverse, **2019-07-25** retire −7,45. La prévision s'y écarte fortement de la moyenne
    (`p − m` = −1,54) parce que `cible_prec_norm` = 9,42 hérite de la réunion du 2019-06-06. Viennent ensuite 2019-09-12
    (−2,46) et 2011-03-03 (−1,87).

  Le résultat dépend donc de quelques réunions extrêmes après normalisation.
- **Prédicteurs extrêmes, sans être des erreurs** : `brent_60j_pct` = −110,6 le 2020-04-30, +92,9 le 2020-07-16 et
  −80,1 le 2008-12-04. Ils sont plausibles (effondrement du Brent en 2020 et en 2008) et respectent les bornes.
- Le fichier compte 26 zéros exacts dans `d_ois1y_pb`, cohérent avec les cotations figées signalées. Il y a 5 cellules vides
  dans les prédicteurs de marché du rodage, ce que le préenregistrement autorise.
