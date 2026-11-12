# F04-bis — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `F04-bis_analyse.csv`, rien d'autre. Je n'ai vu ni le code ni les nombres de
l'expérimentateur. Code : `verification.py` (écrit d'après le texte de la section 5, erreur type groupée codée à la main).
Sortie : `verification.json` (les douze champs de `champs_verification`). Je ne donne pas de verdict.

## Nombres

| Champ | Valeur |
|---|---|
| schema_ok | 1 |
| n_adjudications | 23 |
| n_grappes | 8 |
| ecart_max_hs_fred_pb | 0,0 |
| d_moyen_pb | 0,7826 (= 18/23) |
| d_erreur_type_pb | 0,1411 |
| d_borne_inf_95_pb | 0,4490 |
| d_borne_sup_95_pb | 1,1162 |
| marge_zone_grise | 0,2162 |
| v_hs_moyen_pb | 1,6361 |
| v_mc_moyen_pb | 0,8535 |
| v_mc_erreur_type_pb | 0,3196 |

Contrôle interne : D_i calculé par la formule directe et par V_HS,i − V_MC,i coïncident exactement. Écart-type de D_i
(N − 1) : 0,95 pb.

## Contrôles de schéma

Les contrôles 1 à 9 ont tous été exécutés sur le fichier tel quel ; aucun n'échoue. Format : pas de marque d'ordre
d'octets ; tri par `date_adjudication` puis `echeance` respecté ; pas de doublon (`id_ligne` unique, couples
(cusip, date) uniques ; 91282CAV3, 912810SS8, etc. apparaissent deux fois mais à des dates différentes : réouvertures
successives normales).

Non vérifiable depuis le fichier d'analyse seul (il faudrait A, B ou le calendrier C) : que `id_ligne`, `cusip`,
`terme_api`, dates, `cmt_*`, `gsw_*`, `fenetre_propre` soient bien recopiés de A ; que `hs_*` et `mc_*` soient bien
recopiés de B aux bonnes dates et dans la bonne colonne d'échéance ; que les 24 lignes soient exactement celles de
l'étape 1 de A ; que J − 5 et J + 5 soient les bons jours ouvrés (elles paraissent cohérentes : 2021-07-02 pour le
2021-07-12, à cause du 5 juillet férié ; 2021-01-12 pour le 2021-01-20, à cause du jour de Martin Luther King) ; le
format des dates et le nombre de décimales de B ; l'analyse S3.

## Points ambigus et lecture retenue

1. **« Pour une date hors de l'exercice, `hs_*` et `mc_*` restent vides »** : lu date par date. La ligne du 2020-10-07
   a `hs_jm5`/`mc_jm5` vides (2020-09-30) mais `hs_j`, `hs_jp5`, `mc_j`, `mc_jp5` remplis : conforme à cette lecture.
   Lue ligne par ligne (« ligne hors exercice ⇒ tout vide »), ce serait une violation ; je ne retiens pas cette lecture
   car le texte dit « une date ». Sans effet sur les nombres (la ligne est hors P).
2. **Contrôle 8** appliqué à toutes les lignes du fichier (« pour chaque date où `hs` et `cmt` sont présents ») ;
   `ecart_max_hs_fred_pb` calculé sur P seulement, comme l'écrit la section 5. Les deux donnent 0 : HS est égal à FRED
   au centième près partout, B a deux décimales.
3. **Bornes de l'intervalle d'exercice** prises comme inclusives (« entre 2020-10-01 et 2021-09-30 », « ≥ », « ≤ »).
4. **Erreur type** : formule de la section 5 appliquée telle quelle, sans autre facteur. Pour comparaison seulement, le
   test de Student sur les huit moyennes mensuelles donne une moyenne de 0,8125 et une erreur type de 0,152 ; le texte dit
   que les deux sont « à très peu près » égaux, ce n'est pas la statistique retenue.
5. **Taux pris tels qu'écrits**, sans arrondi ; les résultats ne portent que des erreurs de flottant (~1e-15).

Aucun point ambigu ne donne deux nombres différents pour un champ de `verification.json`.

## Ce qui mérite d'être signalé (sans être une violation)

- **D ne prend que des valeurs entières** (−1, 0, 1 ou 2 pb), puisque HS et MC sont arrondis à 0,01 point : 7 zéros,
  2 valeurs −1, 8 valeurs 1, 6 valeurs 2. L'hypothèse de normalité des moyennes mensuelles est grossière (limite 4 de la
  préinscription).
- **Écart HS − MC systématique, plus grand le jour J** : moyennes sur P de 100 × (hs − mc) : 0,26 pb à J − 5, 0,70 pb à J,
  0,35 pb à J + 5. Sur les 69 paires de P : 24 égales, 32 avec HS > MC (1 ou 2 pb), 13 avec MC > HS (1 pb) ; le plus grand |hs − mc| est de 2 pb, loin de la garde de 25 pb.
- **V_HS = V du premier test** (moyenne recalculée avec `cmt_*` : 1,6361, identique), cohérent avec HS = FRED.
- **Aucun mois ni aucune adjudication ne porte le résultat.** Moyenne de D sans chaque mois : 2020-10 : 0,714 ;
  2020-12 : 0,800 ; 2021-01 : 0,800 ; 2021-03 : 0,850 ; 2021-04 : 0,700 ; 2021-06 : 0,800 ; 2021-07 : 0,850 ;
  2021-09 : 0,750. Sans chaque adjudication : de 0,727 (sans 912810SY5 du 2021-06-15) à 0,864 (sans 912810SX7 du
  2021-06-10). Moyennes mensuelles de D : 1,50 ; 0,67 ; 0,67 ; 0,33 ; 1,33 ; 0,67 ; 0,33 ; 1,00.
- **Analyse S1** (D, V_HS, V_MC) : 10 ans (7 lignes) 0,714 / 1,949 / 1,234 ; 20 ans (8) 0,750 / 1,476 / 0,726 ;
  30 ans (8) 0,875 / 1,523 / 0,648.
- Rien d'impossible : tous les taux entre 0,68 et 2,50 %, |cmt − gsw| < 1 point, 23 lignes dans l'exercice comme attendu,
  dates et échéances conformes au tableau de la section 3.
