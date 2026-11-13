# K20-LIV — Rapport du vérificateur

Rédigé le 2026-11-13 par le vérificateur de K20-LIV. Ce rapport donne des chiffres. Il ne donne pas de verdict, et
`verdict.py` n'a pas été lancé.

## 0. Ce que j'ai lu, ce que j'ai écrit

**Lu, et rien d'autre :** `K20-LIV/preenregistrement.md` (en entier, après vérification du sceau),
`K20-LIV/preenregistrement.md.sha256`, `K20-LIV/K20-LIV_analyse.csv`, `tests-de-mort/protocole.md`,
`tests-de-mort/verdict.py`.

**Pas ouverts :** les scripts de l'expérimentateur, `temoin.json`, ses rapports, `ecarts.md`, les journaux, la figure, la
simulation, le dossier `donnees/`, les autres dossiers de tests, `projects/`, l'historique git. Je n'ai pas vu les chiffres de
l'expérimentateur. Le seul contact avec git a été un `git status` du dossier, en fin de travail, pour voir les fichiers modifiés.
Il indique qu'une première version de mon `verification.py` a été versionnée pendant mon travail, et pas par moi. Je n'ai
pas ouvert l'historique.

**Écrit :**
- `verification.py` : mon code, écrit de zéro à partir du texte. Il refait le sceau et les contrôles de schéma, calcule
  tous les champs et écrit `verification.json`. Il imprime le détail. Commande : `python3 -B verification.py`.
- `verification.json` : les 63 champs de `champs_verification`, dans l'ordre de la section 12, tous numériques. Les comptes
  et les indicateurs sont des entiers (`episode_t_min` = 6 pour E6).
- `verification_controle.py` : une seconde implémentation indépendante, avec pandas, statsmodels et linearmodels (section 5
  ci-dessous).
- ce rapport.

Je n'ai modifié aucun fichier existant.

## 1. Sceau

| | sha256 |
|---|---|
| calculé sur `preenregistrement.md` | `e3afba764025ed5cd33b3caa8959d742f1d7d4e7616e28b4edaf153be811e505` |
| scellé (`preenregistrement.md.sha256`) | `e3afba764025ed5cd33b3caa8959d742f1d7d4e7616e28b4edaf153be811e505` |

**Les deux sont identiques.** Le sceau a été vérifié avant toute lecture du texte, puis à nouveau dans `verification.py`.

## 2. Contrôles de schéma (section 5)

**Portée.** La portée est formée des lignes où `principal` = 1 dans le fichier, plus les lignes que la définition de la
section 4, recalculée à partir des colonnes du fichier, met à 1. Ce sont 548 lignes dans les deux cas, et ce sont les mêmes :
la réunion fait 548 lignes. Les 7 autres lignes servent aux anomalies hors des lignes principales. Elles sont comptées à part
et n'entrent pas dans `n_violations_schema`.

| N° | Contrôle | Ce que j'ai vérifié sur le fichier | Résultat (548 lignes principales) |
|---|---|---|---|
| 1 | Colonnes | les 40 noms, dans l'ordre, rien d'autre ; chaque ligne a 40 cellules | passé |
| 2 | Clés | `variable` parmi les 5 codes ; couple (`variable`, `cible`) unique dans tout le fichier ; mois 06 ou 12 ; cible dans la plage de la variable (tableau de la section 5) | passé |
| 3 | Dates d'enquête | `enquete_1` et `enquete_2` parmi les 161 dates 1946-06 → 2026-06 ; `enquete_2` est la date qui suit `enquete_1` ; `cible` = `enquete_2` + 6 mois ; `enquete_1` = même mois que la cible, un an avant ; `mois_ancre_k` = avril (enquête de juin) ou octobre (enquête de décembre) de la même année ; `semestre` = 2 × année + 0 ou 1, écrit comme un entier | passé |
| 4 | Présence | les 24 cellules exigées sont présentes ; `bp_1`, `bp_2` présentes si et seulement si `CPI` | passé |
| 5 | Séries et jours | `serie_realise` conforme (IPC : `CPIAUCNS` si `enquete_2` ≤ 2004-06, sinon `CPIAUCSL`) ; année-mois des trois `jour_*` = `cible`, `mois_ancre_1`, `mois_ancre_2` ; jour 01 pour les quatre séries mensuelles | passé |
| 6 | Plages des entrées | prévisions et `bp` dans les plages de prévision ; les trois `*_niv` dans les plages de réalisation | passé (0 cellule hors plage) |
| 7 | Formules | les 11 colonnes calculées égales à leur formule à 10⁻⁶ près ; une cellule vide où la formule donne une valeur, ou l'inverse, compte comme un échec | passé (écart maximal 1,8·10⁻¹⁵) |
| 8 | Bruit | `n_rep_1`, `n_rep_2` écrits comme des entiers, ≥ 2 ; `var_rep_1`, `var_rep_2` ≥ 0 | passé |
| 9 | Indicateurs | `complete` = 1 ; `principal` = définition recalculée | passé |
| 10 | Épisodes | `episode` = `Ek` si et seulement si `cible` est dans la fenêtre k (table de l'étape 8) ; sinon vide | passé |
| 11 | Grande nouvelle | `grande_nouvelle` ∈ {0, 1}, écrit comme un entier, et = 1 si et seulement si \|`surprise`\| > Q_v (Q_v calculé sur la colonne `surprise` du fichier) | passé |

**`n_violations_schema` = 0.**

**Anomalies hors des lignes principales** (contrôles 3 à 8 sur les cellules présentes des 7 autres lignes ; contrôles 10 et 11
appliqués aussi) : **0**.

Les cellules vides de ces 7 lignes sont exactement celles que donnent les règles de vide de la section 4 :
- `CPI` 2005-06 : `y_prev_1`, `y_prev6_1`, `revision`, `surprise`, `revision_med` sont vides par règle. `serie_realise` vaut
  `CPIAUCSL`. `episode` et `grande_nouvelle` sont vides, ce qui est conforme.
- `CPI` 2026-06 : octobre 2025 manque, donc `jour_ancre_2`, `ancre_niv_2`, `y_ancre_2` et `y_prev_2` sont vides, puis
  `revision`, `erreur`, `surprise`, `revision_med` et `erreur_med`. Les autres cellules présentes passent les contrôles 3 à 8.
- `UNPR` 2026-06 : octobre 2025 manque, donc `jour_ancre_2`, `ancre_niv_2`, `y_ancre_2` et `surprise` sont vides.
  `revision` et `erreur` sont présentes et conformes.
- `UNPR` 2020-06, 2020-12, 2021-06, 2021-12 : ces lignes sont complètes et seuls `bp_1` et `bp_2` sont vides. Leur
  `grande_nouvelle` est conforme au Q_v des lignes principales.

**Points de forme hors des 11 contrôles.** Ils n'entrent pas dans `n_violations_schema`, qui compte les contrôles 1 à 11.
- 555 lignes, comme attendu. Le tri suit la variable puis la cible. Les comptes par variable sont ceux de la section 5 :
  158/156/156, 129/128/124, 89/89/89, 67/67/67 et 112/112/112.
- « Au moins 10 chiffres significatifs » : beaucoup de cellules en ont moins. C'est le cas de toutes les valeurs lues
  (par exemple `138.68` ou `23.4`) et de certains résultats exacts (une `revision` d'UNPR de `-1.08`). J'ai vérifié chaque
  cellule décimale : elle est écrite exactement sous sa représentation la plus courte qui se relit à l'identique (`repr` de
  Python). Le nombre relu est donc le même double que le nombre écrit, et aucune précision n'est perdue. L'écart à la lettre
  de la section 5 reste formel ; je le signale sans le compter.

**Ce qui n'est pas fait, pour garder l'aveuglement.** Je n'ai rien comparé aux fichiers bruts (`means.xlsx`, `medians.xlsx`,
`individualdata.xlsx`, FRED) :
- je n'ai pas vérifié que les prévisions, les médianes, les `bp`, les niveaux réalisés, `n_rep` et `var_rep` sont bien ceux
  des sources ;
- pour `DPRIME` et `DTB3`, je n'ai pas vérifié que le jour lu est la dernière observation non vide du mois. Les jours lus
  vont du 28 au 31 (minimum 28), ce qui va dans le sens de la section 3.3 ;
- je n'ai pas lu la colonne `Date` publiée : la liste des 161 dates vient du texte (section 3.1) ;
- je n'ai vérifié ni les sha256 des fichiers bruts ni la présence des fichiers.

Le contrôle 7 garantit la cohérence interne du fichier, pas la justesse des valeurs lues.

## 3. Échantillon

- **n_principal = 548** : `CPI` 156, `UNPR` 124, `PRIME` 89, `TBILL` 67, `TPHS` 112.
- Semestres : de 3895 (1947-12) à 4052 (2026-06). **158 semestres distincts sur 158**, sans trou.
- Lignes principales par épisode : E1 5, E2 4, E3 4, E4 4, E5 13, E6 15, E7 28, E8 12, E9 20, E10 30, E11 36. Il en reste
  377 hors épisode. Ce sont exactement les comptes de la section 5.
- Q_v, tiers supérieur de \|surprise\| : `CPI` 0,72876, `UNPR` 0,3225, `PRIME` 0,45333, `TBILL` 0,35, `TPHS` 9,6288. Lignes
  avec L = 1 : 52, 41, 30, 22 et 37, soit **n_grands = 182**. **n_dates_grands = 110** semestres ont au moins une ligne L = 1.

## 4. Les chiffres

Calculs en double précision, sans arrondi intermédiaire. Les valeurs complètes sont dans `verification.json` ; ici, elles
sont arrondies pour la lecture.

**Réduction (étape 1)**, écarts-types de diviseur n_v − 1, sur les lignes principales :

| | s_r | s_e | k_v | b̂_v | δ̂_v | ν_v |
|---|---|---|---|---|---|---|
| CPI | 1,9217 | 1,4852 | 1,2938 | 0,5581 | 0,2253 | 0,009839 |
| UNPR | 0,5445 | 0,5499 | 0,9902 | 0,4270 | 0,0141 | 0,018618 |
| PRIME | 0,9470 | 0,9649 | 0,9814 | 0,2314 | −0,3362 | 0,011727 |
| TBILL | 0,8021 | 0,7040 | 1,1394 | 0,5940 | −0,0560 | 0,012848 |
| TPHS | 10,848 | 16,169 | 0,6709 | 0,4047 | 0,0689 | 0,024760 |

**Test principal (étapes 3 à 5)**, 16 paramètres, Driscoll-Kraay à 2 retards par semestre :

| Champ | Valeur |
|---|---|
| `c` | **−0,122191** |
| `et_c_dk2` | 0,139088 |
| `t_c` | −0,8785 |
| `borne_basse_ic90` | **−0,350991** |
| `borne_haute_ic90` | **+0,106608** |
| `b_moyen` | 0,443050 |
| `k_moyen` | 1,015167 |
| `pente_moyenne_grandes` | 0,320859 |

**Contrôle positif (étape 6)**, 6 paramètres :

| Champ | Valeur |
|---|---|
| `b_regroupe` | **0,372772** |
| `et_b_regroupe_dk2` | 0,066811 |
| `borne_basse_b_ic90` | 0,262867 |
| `controle_positif_ok` | **1** |

**Biais mécanique et plancher (étape 7)** : a = 0,218501 et A = 2,206842 (moyennes regroupées, voir 6.8).

| Champ | Valeur |
|---|---|
| `rapport_variance_revision` | 10,0999 |
| `nu_mesure` | 0,0155585 |
| `biais_mecanique_mesure` | 0,121977 |
| `biais_mecanique_nu20` | 0,783990 |
| `seuil_survie_bas` | 0,121977 |
| `borne_basse_moins_seuil` | −0,472968 |

**Garde des épisodes (étape 8)** :

| Exclu | n restant | ĉ sans l'épisode | écart-type DK2 | t |
|---|---|---|---|---|
| E1 | 543 | −0,05635 | 0,12888 | −0,437 |
| E2 | 544 | −0,12330 | 0,13926 | −0,885 |
| E3 | 544 | −0,11846 | 0,13958 | −0,849 |
| E4 | 544 | −0,12467 | 0,13919 | −0,896 |
| E5 | 535 | −0,13062 | 0,14840 | −0,880 |
| E6 | 533 | −0,12882 | 0,14000 | **−0,920** |
| E7 | 520 | −0,06933 | 0,13932 | −0,498 |
| E8 | 536 | −0,10259 | 0,13693 | −0,749 |
| E9 | 528 | −0,09191 | 0,13697 | −0,671 |
| E10 | 518 | −0,11142 | 0,13038 | −0,855 |
| E11 | 512 | −0,11243 | 0,14851 | −0,757 |

`t_min_sans_episode` = −0,920191 ; `episode_t_min` = 6 ; `c_min_sans_episode` = −0,130619 (sans E5).

**Champs dérivés (étape 9)** : `marge_indecision` = −0,293392 ; `conflit_robustesse` = 0.

**Précision (étape 10)** : `et_c_iid` = 0,114833 ; `n_effectif` = 373,54 ; `n_dates` = 158.

**Analyses secondaires** (z et L de l'échantillon principal, DK2) :

| Analyse | Champ | ĉ | écart-type | n |
|---|---|---|---|---|
| S2 | `et_c_dk4` ; `et_c_dk0` | — | 0,140598 ; 0,141365 | 548 |
| S3 avec la pandémie | `c_avec_pandemie` | −0,319861 | 0,149000 | 552 |
| S4 depuis 1985 | `c_depuis_1985` | −0,039352 | 0,152662 | 392 |
| S5 avant 2020 | `c_avant_2020` | −0,161160 | 0,154395 | 489 |
| S6 médianes | `c_mediane` | −0,094777 | 0,123396 | 548 |
| S7 coupure \|z_r\| > 1 (110 lignes L' = 1) | `c_coupure_revision` | −0,184106 | 0,112630 | 548 |
| S1 CPI | `c_CPI` | −0,223521 | 0,392299 | 156 |
| S1 UNPR | `c_UNPR` | +0,378362 | 0,286092 | 124 |
| S1 PRIME | `c_PRIME` | −0,442084 | 0,255337 | 89 |
| S1 TBILL | `c_TBILL` | −0,025774 | 0,269999 | 67 |
| S1 TPHS | `c_TPHS` | −0,469007 | 0,293076 | 112 |

S1 est une seule régression jointe à 20 paramètres. Les écarts-types sont ceux de Driscoll-Kraay, calculés sur les scores
de cette régression jointe.

**Hors règle**, demandé par la section 6 :
- les cinq ν_v sont dans le tableau de réduction ci-dessus ;
- anomalies hors des lignes principales : aucune ;
- base de l'IPC : 2 lignes principales sur 152 évaluées ont \|ln(`ancre_niv_2`/`bp_2`) − ln(`ancre_niv_1`/`bp_1`)\| > 0,005.
  Ce sont `CPI` 1951-12 (écart 0,0069) et `CPI` 1954-06 (écart 0,514). La lecture de ce second cas est en 6.12.

## 5. Contrôle croisé indépendant (`verification_controle.py`)

Cette seconde implémentation n'importe pas `verification.py`. Elle lit le fichier avec pandas (`float_precision="round_trip"`)
et construit les matrices avec pandas. Elle recalcule `principal`, les z, Q_v et L par une autre écriture, puis estime les
modèles avec statsmodels (`OLS`, `cov_type="hac-groupsum"` sans correction, et `cluster` pour DK0) et avec linearmodels
(`PanelOLS`, `cov_type="kernel"`, noyau de Bartlett, `debiased=False`).
- **statsmodels** : 62 champs recalculés (tous sauf `n_violations_schema`). Écart maximal à `verification.json` :
  1,2·10⁻¹² (sur `n_effectif`) ; tous les autres sont sous 5·10⁻¹⁵. Les entiers sont identiques.
- **linearmodels** : `c`, `et_c_dk2`, `et_c_dk4`, `et_c_dk0`, `b_regroupe`, `et_b_regroupe_dk2` concordent à moins de
  10⁻¹⁵. Les t sans épisode concordent à 1,4·10⁻¹⁴.

**Deux pièges, notés pour qui refait le calcul.** Ni l'un ni l'autre ne touche mes chiffres.
1. Les deux bibliothèques comptent les retards par position dans la suite des dates présentes, comme le dit la section 6.
   Sans E7, cela donne un écart-type de 0,139714 au lieu de 0,139315 en semestres calendaires. Pour obtenir les retards
   calendaires, j'ai ajouté une ligne nulle (X = 0, y = 0) par semestre vide : elle n'entre ni dans X'X ni dans les scores.
2. Avec statsmodels, le code de temps brut (`semestre`, 3895 à 4052) donne un faux résultat. Comme ces codes dépassent 2n,
   statsmodels les renumérote avec `pd.factorize`, dans l'ordre de première apparition. Les semestres 2005-06 et 2026-06
   n'apparaissent qu'avec les lignes UNPR, puisque leurs lignes IPC ne sont pas principales : l'ordre chronologique est
   rompu. On obtient alors `et_c_dk2` = 0,138704 au lieu de 0,139088. Avec des codes 0…157 (semestre − minimum), le résultat
   est juste.

## 6. Ambiguïtés du texte et lecture retenue (la plus proche de la lettre)

1. **Lignes principales.** La lettre de la section 5 prend la réunion des lignes à `principal` = 1 et des lignes que la
   définition recalculée met à 1. Ici, les deux ensembles sont identiques (548 lignes) : la question ne se pose pas.
2. **Les 161 dates publiées (contrôle 3)** viennent de la description de la section 3.1 : 1er juin et 1er décembre, de
   1946-06 à 2026-06, sans trou. La colonne `Date` des fichiers bruts n'a pas été lue (aveuglement).
3. **Contrôle 6 et médianes.** Le texte du contrôle cite `prev_12m_1`, `prev_6m_2`, `prev_6m_1` (et `bp`), mais la colonne
   « vérifié avant scellement » compte 1 096 cellules médianes. J'applique le contrôle à la lettre, et je vérifie les médianes
   à part : 0 hors plage. Les deux lectures donnent le même résultat.
4. **Contrôle 7, opérandes.** Chaque formule est évaluée sur ses opérandes tels qu'écrits dans le fichier (lettre : « égales
   à leur formule »). J'ai aussi recalculé toute la chaîne depuis les valeurs lues. Les deux passent, avec un écart maximal de
   3,6·10⁻¹⁵ ; la tolérance de 10⁻⁶ est lue comme un écart absolu.
5. **`revision_med` et `erreur_med`** sont dans le contrôle 7 mais pas dans la liste de présence du contrôle 4. Sur les
   lignes principales, elles sont toutes présentes et conformes : sans objet.
6. **Coupure stricte et égalités.** Pour `UNPR` (n = 124), `TBILL` (67) et `TPHS` (112), (n_v − 1) × 2/3 est un entier. Le
   quantile linéaire vaut donc exactement une valeur observée. Trois lignes sont exactement sur le seuil : `UNPR` 1988-06,
   `TBILL` 2018-12 et `TPHS` 1978-12. La coupure stricte de l'étape 2 leur donne L = 0, et le fichier fait de même.
   Pour information, hors règle : avec ces trois lignes en L = 1, c vaudrait −0,1156 (écart-type 0,1396) au lieu de
   −0,1222. Le résultat est donc peu sensible à ce point.
7. **Coupure de la grande nouvelle** : calculée, comme l'écrit le texte, sur la colonne `surprise` du fichier, et non sur une
   surprise recalculée. Le contrôle 7 montre d'ailleurs que les deux coïncident.
8. **a et A (étape 7)** : ce sont des moyennes regroupées sur toutes les variables, exactement comme écrit. Chaque ligne est
   centrée sur la moyenne m_{v,ℓ} de sa variable et de sa classe, et le diviseur est le nombre de lignes de la classe
   (366 pour L = 0, 182 pour L = 1). Ce n'est ni une moyenne des cinq rapports par variable, ni un diviseur n − 1.
9. **`biais_mecanique_nu20`** : le facteur est 0,10, comme écrit, c'est-à-dire ν/2 avec ν = 0,20. Le nom du champ évoque
   20 %, la formule donne 0,10.
10. **`episode_t_min`** est codé par le nombre k (6 pour E6), puisque le texte dit « le k qui le donne » et que `verdict.py`
    exige un nombre.
11. **Exclusion d'un épisode** : faite sur la cible, avec les fenêtres de la table de l'étape 8, bornes comprises. Le
    résultat est identique à la colonne `episode`, puisque le contrôle 10 passe. Les semestres retirés deviennent des
    semestres sans ligne ; aucune exclusion ne change le premier ni le dernier semestre.
12. **Diagnostic de base de l'IPC (hors règle).** Le texte exclut les paires dont `enquete_2` vaut 1953-06, 1962-06, 1971-06
    ou 1988-06. Le fichier montre bien un changement de base à 1962-06, 1971-06 et 1988-06. Pour 1953, en revanche, le
    rapport `bp`/réalisé passe de 7,15 (190,1/26,6) à 4,27 (115,4/27,0) entre les enquêtes 1953-06 et 1953-12 : la paire à cheval est donc
    `enquete_2` = 1953-12 (cible 1954-06), et non 1953-06. À la lettre, le compte vaut 2. Si l'on exclut la paire où la
    base change vraiment, il vaut 1 (`CPI` 1951-12, écart 0,0069).
    Cela ne touche aucune formule : la remise en base se fait questionnaire par questionnaire, et le contrôle 7 passe sur
    cette ligne.
13. **DK0** : groupement par semestre, Ω = Σ H_τ H_τ', sans retard ni correction. **DK4** : poids 1 − j/5.
14. **S3** : les quatre lignes pandémiques reçoivent les z (constantes de l'étape 1) et le L (Q_v de l'étape 2) de
    l'échantillon principal. **S6** : `revision_med` et `erreur_med` sont réduites par leurs propres moyennes et écarts-types,
    par variable, sur les 548 lignes, et L ne change pas.
15. **Convention n < 50 ou X'X singulière** : jamais déclenchée. Toutes les matrices sont de plein rang.

## 7. Ce qui paraît anormal ou notable dans le fichier

Rien ne fait échouer un contrôle. À noter, sans jugement sur le test :
- **Les dispersions de Livingston ne ressemblent pas à celles de K20.** Le rapport des variances de la révision vaut 10,1
  (3,06 dans K20 ; la section 8 imaginait environ 5 dans le scénario S-b). k_moyen vaut 1,02 (0,29 dans K20, environ 1 dans
  S-b). b_moyen vaut 0,44 et b_regroupe 0,37 (0,19 dans K20). Le biais mesuré, 0,122, dépasse 0,10 : le plancher est donc
  0,122. `biais_mecanique_nu20` vaut 0,78, parce que 1/a − 1/A = 4,12.
- **Les deux premières lignes IPC (cibles 1947-12 et 1948-06)** sont très extrêmes : \|z_r\| jusqu'à 7,65 et \|z_e\| jusqu'à
  6,83, avec l'inflation d'après-guerre. Elles ne tombent dans aucune fenêtre d'épisode, puisque E1 commence en 1948-11 :
  la garde des épisodes ne les retire jamais. Hors IPC, aucune ligne ne dépasse \|z\| = 3,81.
- **`CPI` 1951-12** : le rapport `bp`/réalisé du questionnaire bouge de 0,69 % entre deux enquêtes de même base (1935-39),
  plus que l'arrondi du réalisé à une décimale ne l'explique. La limite 4 en parle déjà (mois de la valeur de base incertain).
- **La date de 1953** dans la liste des changements de base du diagnostic, déjà décrite en 6.12.
- **Le format des nombres**, sans perte de précision, déjà décrit en section 2.

## 8. Ce que je n'ai pas fait

Je n'ai écrit aucun verdict et je n'ai pas lancé `verdict.py`. Je n'ai pas comparé mes chiffres à ceux de l'expérimentateur,
que je n'ai pas lus : la comparaison de tolérance revient à `verdict.py`.
