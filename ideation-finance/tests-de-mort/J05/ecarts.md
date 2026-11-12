# J05 — Écarts à la préinscription

## ⚠ Deux points où la préinscription énonce un fait inexact sur les données (exécutée telle qu'écrite)

### E1. Contrôle de schéma n° 5 : « écart de 7 à 9 jours civils » entre `date_jm5` et `date_adjudication` — faux pour trois lignes

La préinscription définit J−5 comme « la date située 5 rangs avant J dans C » (C = dates de D2 où les six paramètres sont
présents) et affirme, au contrôle 5.3-5, que cet écart vaut 7 à 9 jours civils (« cinq jours ouvrés, au plus deux fériés »).
C'est inexact : quand J est un lundi et que le lundi précédent est férié, cinq rangs de C en arrière tombent le vendredi
d'il y a dix jours. Dans les données, trois lignes `avant`/`apres` sont dans ce cas :

| Ligne | J (lundi) | Férié (ligne D2 à `NA`) | J−5 dans C | Écart |
|---|---|---|---|---|
| `9128282A7_2016-09-12` | 2016-09-12 | 2016-09-05 (Labor Day) | 2016-09-02 | 10 jours |
| `91282CCB5_2021-07-12` | 2021-07-12 | 2021-07-05 (4 juillet observé) | 2021-07-02 | 10 jours |
| `91282CFF3_2022-09-12` | 2022-09-12 | 2022-09-05 (Labor Day) | 2022-09-02 | 10 jours |

Répartition des écarts sur les 324 lignes `avant`/`apres` : 7 jours (260), 8 jours (61), 10 jours (3). Aucun J−5 n'est
postérieur à J ni tombé un week-end ; il n'y a aucun regard vers l'avenir. Le défaut est dans la plage écrite, pas dans les
dates.

**Exécution telle qu'écrite.** J−5 est calculé exactement selon la définition (5 rangs avant J dans C) ; le contrôle 5 est
appliqué avec la plage 7 à 9 jours ; il échoue sur ces trois lignes, donc **`schema_ok` = 0** dans `temoin.json` et dans
`construire_journal.json`. Tous les autres contrôles (1, 2, 3, 4, 6, 7, 8) passent. Les trois lignes restent dans le fichier
et dans P (`dans_p` ne dépend pas du contrôle de schéma) ; la statistique est calculée sur P tel que défini, sans autre
lecture. Je n'ai calculé aucune statistique sous une lecture corrigée ; je note seulement que `dans_p`, P et donc Δ ne
dépendent pas de ce contrôle.

### E2. La formule de rendement de 5.2, attribuée à « 31 CFR partie 356, annexe B », n'est pas exactement celle du Trésor

La préinscription actualise la période fractionnaire jusqu'au premier coupon en composition : (1 + y/200)^−(N−d)/(N−L).
Les données de D1 montrent que le Trésor (qui fixe `high_price` à partir de `high_yield`) actualise cette période en
**intérêt simple**, 1/(1 + ((N−d)/(N−L))·y/200). Constat (diagnostic, sur les 323 lignes `avant`/`apres` avec un prix) :
- avec la formule préinscrite, |Y(`prix_limite`, s) − `high_yield`| va de 0,00001 à **0,00098** point de pourcentage
  (moyenne 0,00012 en `avant`, 0,00036 en `apres`, toujours positif, croissant avec le niveau des taux) ;
- avec l'intérêt simple sur la période fractionnaire, l'écart maximal est de 0,00000012 (arrondi de `high_price` à 6 décimales).

**Exécution telle qu'écrite.** Toutes les colonnes de rendement (33 à 38) utilisent la formule préinscrite. Comme l'écart
reste sous la tolérance de 0,001, `convention_ok` = 1 sur toutes les lignes `avant`/`apres` ayant un prix (la plus proche du
seuil : `91282CRF0_2026-10-07`, 0,000983) et `n_echec_convention` = 0. Conséquence possible, non chiffrée sur la
statistique : `high_yield` (convention du Trésor) est comparé à `g_terme(J)` (convention préinscrite), ce qui abaisse C, et
donc K, de l'ordre de 0,01 pb en moyenne avant 2022 et 0,04 pb après (ordre de grandeur de l'écart ci-dessus × 100). Aucune
statistique n'a été recalculée sous la convention du Trésor.

## Autres écarts et lectures

### E3. Contrôle 4 : « postérieure … d'au plus 20 jours »
Lu comme 0 < `date_reglement` − `date_adjudication` ≤ 20 jours. Observé : 1 à 15 jours. Sans effet.

### E4. Valeurs recopiées de D1 et D2 écrites comme nombres
Les colonnes « recopiées » (`taux_coupon_pct`, `rdt_limite_pct`, `prix_limite`, paramètres GSW) sont écrites par
`repr(float(chaîne))` : « 5.125000 » de l'API devient « 5.125 », « 3.754 » reste « 3.754 ». Valeur numérique identique ;
aucune perte de chiffres.

### E5. `ecart_max_rdt_pb` non nul (3,6·10⁻¹¹ pb) au lieu de 0
La préinscription attend 0 « par construction ». J'ai recalculé les colonnes 16 et 33 à 38 dans `analyse.py` avec un code
distinct de `construire.py` (autre génération des dates de coupon, résolution par Brent au lieu d'une bissection, courbe
vectorisée) ; l'écart résiduel est de l'ordre de la précision des solveurs. La statistique est calculée avec les rendements
de `analyse.py` ; avec les `k_pb` du fichier, Δ diffère de 2·10⁻¹² pb.

### E6. Session FedInvest
Les trois étapes (GET, POST, GET) sont refaites pour chaque date avec une session neuve (témoin et `_csrf` nouveaux), client
`curl` sans suivi automatique de la redirection ; pause d'une seconde entre deux dates, en plus du temps des requêtes
(environ 3 s par date au total). Jusqu'à 5 tentatives avec attente croissante étaient prévues ; aucune n'a servi
(630 dates sur 630 obtenues du premier coup). Je le note parce que la préinscription ne dit pas si le témoin doit être
renouvelé à chaque date.

### E7. Fichiers en plus de ceux que nomme la préinscription
`telecharger_fedinvest.py` (téléchargement D3), `donnees/fedinvest_journal.csv` (journal des requêtes, écrit par ce script ;
ce n'est pas une réponse de serveur), `construire_journal.json` (comptes et contrôles), `resultats_analyse.json` (sorties
complètes, dont `descriptif`). Ils n'entrent pas dans le fichier d'analyse.

### E8. Lecture de `complet_k`
La définition liste les colonnes 13, 14, 18-23 et 25-31 ; `construire.py` exige en plus `date_jm5` (colonne 24). C'est
équivalent : les colonnes 25-31 ne sont remplies que si `date_jm5` l'est. Aucune ligne n'est classée différemment.

### E9. Figure
Les intervalles par année sont des IC à 90 % (± 1,645 ET groupée par mois, facteur G/(G − 1), 7 à 8 mois par année) autour de
la moyenne simple de K de l'année. Les lignes horizontales sont les moyennes simples de chaque période, pas le Δ à effets
fixes. Choix descriptif, la préinscription ne fixant pas la figure.
