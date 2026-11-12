# F04-bis — rapport de l'expérimentateur

Rédigé le 2026-11-12. L'expérimentateur exécute la préinscription scellée (sha256 `f5f4b98d…c78a`, vérifié au début et à la
fin) ; il n'écrit pas le verdict. Les chiffres ci-dessous sont un témoin : le vérificateur recalcule tout à partir du
fichier d'analyse, et le verdict est calculé par `verdict.py` sur ses chiffres à lui.

## 1. Ce qui a été fait

1. Lecture de `protocole.md` et de la préinscription en entier. Du premier test F04, seuls ont été ouverts : son fichier
   d'analyse (fichier A), `F04/donnees/DGS10.csv` (calendrier C), la ligne `DGS10` de `F04/donnees/PROVENANCE.md` et la ligne
   de `F04/preenregistrement.md` qui définit le calendrier C. Aucun rapport, verdict ou autre test n'a été lu.
2. Téléchargement du fichier des deux méthodes (fichier B) depuis `home.treasury.gov` : HTTP 200 à la première tentative, le
   2026-11-12T17:31:28Z, après le scellement (17:31:07Z). Fichier conservé tel quel dans `donnees/`, avec `PROVENANCE.md`.
3. Constat de la forme du fichier B (format des dates, décimales, nombre de dates), noté dans `ecarts.md`, partie A.
4. `construire.py` : construit `F04-bis_analyse.csv` à partir des fichiers de `donnees/` seulement, puis relit le fichier
   écrit et exécute les neuf contrôles de schéma. Journal : `construire_journal.json`.
5. `analyse.py` : statistique principale, estimations d'accompagnement, analyses S1 à S3, `temoin.json`,
   `resultats_analyse.json`, `figure.png`. Calcul déterministe, aucun tirage.

Commandes : `python3 -I construire.py` puis `python3 -I analyse.py`, depuis ce dossier.

## 2. Le fichier des deux méthodes, tel que reçu

| Point | Constat |
|---|---|
| Taille | 47 599 octets ; 1 ligne d'en-tête et 251 lignes de données ; 35 colonnes, aux noms attendus |
| Encodage | UTF-8 avec marque d'ordre d'octets ; fins de ligne CRLF ; virgule |
| Dates | `M/J/AAAA` sans zéro initial, du 2020-10-01 au 2021-09-30 ; seule la lecture mois/jour place toutes les dates dans l'exercice |
| Nombre de dates | 251, toutes distinctes, en ordre croissant ; calendrier C dans l'exercice : 251 jours ; 0 jour de C absent du fichier, 0 date du fichier absente de C |
| Unité | pour cent par an |
| Décimales | deux au plus, zéros finaux supprimés (`1.4` pour 1,40) ; aucune cellule vide ou non numérique dans les six colonnes utilisées |

Conséquence prévue par la préinscription : le fichier étant arrondi à 0,01 point, D ne prend que des valeurs entières en
points de base, et l'arrondi fait partie du bruit de D.

## 3. Échantillon à chaque filtre

| Étape | Lignes | Attendu |
|---|---|---|
| Fichier A, toutes lignes | 1 606 | — |
| Étape 1 : `type_ligne` = `reelle`, `principal` = 1, adjudication du 2020-10-01 au 2021-09-30 | 24 | 24 |
| Étape 2 : `dans_exercice` = 1 | 23 | 23 |
| … et `complet` = 1 (les douze taux présents) | 23 | — |
| Étape 3, échantillon P : … et `fenetre_propre` = 1 | **23** | 23 |

- Ligne hors de P : la réouverture à 10 ans du 2020-10-07, dont le J − 5 est le 2020-09-30, la veille du début du fichier B
  (`dans_exercice` = 0, `complet` = 0). C'est la ligne annoncée par la préinscription.
- Mois dans P : **8** (2020-10, 2020-12, 2021-01, 2021-03, 2021-04, 2021-06, 2021-07, 2021-09) ; trois adjudications par
  mois, deux en octobre 2020.
- Par échéance dans P : 7 à 10 ans, 8 à 20 ans, 8 à 30 ans.
- Les 24 dates d'adjudication sont celles du tableau de la préinscription. Aucun taux manquant dans l'exercice.

Contrôles de schéma, exécutés sur le fichier d'analyse relu depuis le disque : les neuf passent (`schema_ok` = 1).

| Contrôle | Résultat |
|---|---|
| 1. 24 colonnes dans l'ordre, sans marque d'ordre d'octets | passe |
| 2. `id_ligne` unique, domaines | passe |
| 3. Ordre et bornes des dates, `mois` | passe |
| 4. `dans_exercice` | passe |
| 5. `complet` | passe |
| 6. Taux entre −1 et 20 ; \|`cmt` − `gsw`\| ≤ 1 | passe ; plus grand écart 0,086 point |
| 7. \|`hs` − `mc`\| ≤ 0,25 point et au moins une paire différente | passe ; plus grand écart 0,02 point ; 45 paires différentes sur 71 |
| 8. Ancienne méthode = FRED, \|`hs` − `cmt`\| ≤ 0,0051 point | passe ; **écart maximal 0,00** sur les 71 paires, aucun dépassement |
| 9. 24 lignes ; 20 à 24 avec `dans_exercice` = 1 | passe ; 24 et 23 |

## 4. Statistique principale et estimations d'accompagnement (`temoin.json`)

| Champ | Valeur |
|---|---|
| `schema_ok` | 1 |
| `n_adjudications` | 23 |
| `n_grappes` | 8 |
| `ecart_max_hs_fred_pb` | 0,000 |
| `d_moyen_pb` | 0,7826 |
| `d_erreur_type_pb` | 0,1411 |
| `d_borne_inf_95_pb` | 0,4490 |
| `d_borne_sup_95_pb` | 1,1162 |
| `marge_zone_grise` | 0,2162 |
| `v_hs_moyen_pb` | 1,6361 |
| `v_mc_moyen_pb` | 0,8535 |
| `v_mc_erreur_type_pb` | 0,3196 |

En mots, sans conclure : sur les 23 réouvertures, V vaut en moyenne 1,64 pb avec l'ancienne méthode et 0,85 pb avec la
nouvelle ; la différence appariée moyenne est de 0,78 pb, erreur type groupée par mois 0,14 pb, intervalle à 95 % de 0,45 à
1,12 pb (demi-largeur 2,365 × 0,1411 = 0,334 pb). Le seuil préinscrit de 0,9 pb est à l'intérieur de cet intervalle
(`marge_zone_grise` = 0,216, positive). Repères de la préinscription pour situer ces chiffres : cassure à expliquer
1,75 pb ; seuil 0,9 pb ; demi-largeur de 0,45 pb comme limite entre « imprécis » et « précis » dans la section 6.

Vérification à la main : la somme des 23 valeurs de D est 18 pb (2 fois −1, 7 fois 0, 8 fois 1, 6 fois 2), soit
18/23 = 0,7826. Sommes de D par mois : 3, 2, 2, 1, 4, 2, 1, 3 ; Σ S_g² = 9,210 ; (1/23) × √(8/7 × 9,210) = 0,1411.
L'identité V_MC moyen = V_HS moyen − D moyen tient à 10⁻¹⁶ près.

Écart-type de D sur P (dénominateur N − 1) : **0,951 pb**. La section 6 de la préinscription supposait 1,0 pb au centre
(fourchette 0,3 à 2,6) et une erreur type centrale de 0,26 pb ; l'erreur type obtenue est 0,141 pb.

### Détail par adjudication (points de base)

| Adjudication | Échéance | V_HS | V_MC | D |
|---|---|---|---|---|
| 2020-10-08 | 30 | 1,82 | −0,18 | 2 |
| 2020-10-21 | 20 | 1,23 | 0,23 | 1 |
| 2020-12-09 | 10 | 2,44 | 2,44 | 0 |
| 2020-12-10 | 30 | 1,69 | −0,31 | 2 |
| 2020-12-21 | 20 | 0,69 | 0,69 | 0 |
| 2021-01-12 | 10 | −0,63 | −2,63 | 2 |
| 2021-01-13 | 30 | 0,30 | 0,30 | 0 |
| 2021-01-20 | 20 | 0,72 | 0,72 | 0 |
| 2021-03-10 | 10 | 1,85 | 1,85 | 0 |
| 2021-03-11 | 30 | 3,02 | 3,02 | 0 |
| 2021-03-16 | 20 | 3,64 | 2,64 | 1 |
| 2021-04-12 | 10 | 3,04 | 1,04 | 2 |
| 2021-04-13 | 30 | 2,51 | 1,51 | 1 |
| 2021-04-21 | 20 | 1,16 | 0,16 | 1 |
| 2021-06-09 | 10 | 3,40 | 2,40 | 1 |
| 2021-06-10 | 30 | 0,63 | 1,63 | −1 |
| 2021-06-15 | 20 | 0,67 | −1,33 | 2 |
| 2021-07-12 | 10 | 0,97 | 1,97 | −1 |
| 2021-07-13 | 30 | 2,06 | 0,06 | 2 |
| 2021-07-21 | 20 | 1,81 | 1,81 | 0 |
| 2021-09-08 | 10 | 2,57 | 1,57 | 1 |
| 2021-09-09 | 30 | 0,15 | −0,85 | 1 |
| 2021-09-21 | 20 | 1,89 | 0,89 | 1 |

### Par mois (les grappes ; chiffres non demandés par la préinscription, voir `ecarts.md` E4)

| Mois | Adjudications | D moyen | V_HS moyen | V_MC moyen |
|---|---|---|---|---|
| 2020-10 | 2 | 1,50 | 1,52 | 0,02 |
| 2020-12 | 3 | 0,67 | 1,61 | 0,94 |
| 2021-01 | 3 | 0,67 | 0,13 | −0,54 |
| 2021-03 | 3 | 0,33 | 2,84 | 2,50 |
| 2021-04 | 3 | 1,33 | 2,24 | 0,90 |
| 2021-06 | 3 | 0,67 | 1,57 | 0,90 |
| 2021-07 | 3 | 0,33 | 1,61 | 1,28 |
| 2021-09 | 3 | 1,00 | 1,54 | 0,54 |

D moyen est positif dans les huit mois. Contrôle d'arithmétique : le test de Student sur ces huit moyennes donne 0,81 pb,
erreur type 0,15 pb, proche de la statistique préinscrite (0,78 et 0,14) comme la préinscription l'annonce.

## 5. Figure

`figure.png`. À gauche, V de chacune des 23 réouvertures sous l'ancienne méthode (rond bleu) et sous la nouvelle (losange
orange), reliés par un trait ; quand les deux coïncident (D = 0, sept adjudications), le losange est posé sur le rond. Les
lignes verticales donnent les deux moyennes. À droite, D par adjudication, puis en bas la moyenne de D avec son intervalle à
95 % et le seuil préinscrit de 0,9 pb. Les deux panneaux ont chacun leur axe, en points de base ; les traits horizontaux
fins séparent les mois.

## 6. Analyses secondaires — descriptives, sans effet sur le verdict

**S1. Par échéance** (moyennes sur P, sans erreur type).

| Échéance | Adjudications | D moyen | V_HS moyen | V_MC moyen |
|---|---|---|---|---|
| 10 ans | 7 | 0,71 | 1,95 | 1,23 |
| 20 ans | 8 | 0,75 | 1,48 | 0,73 |
| 30 ans | 8 | 0,87 | 1,52 | 0,65 |

**S2. D'où vient D.** Moyenne sur P de 100 × (HS − MC) : 0,26 pb à J − 5 ; 0,70 pb à J ; 0,35 pb à J + 5. On retrouve
D moyen = 2 × 0,696 − 0,261 − 0,348 = 0,78. Moyenne sur P du V du premier test, recalculé avec `cmt_*` : 1,6361 pb, égal à
`v_hs_moyen_pb` (1,6361) puisque les taux HS du fichier B sont identiques aux taux FRED sur toutes les dates utilisées.

**S3. Les jours ordinaires** (fichier brut B, les 251 dates ; écarts-types avec dénominateur N − 1, ceux avec N diffèrent
à la troisième décimale).

| Échéance | Moyenne de HS − MC | Écart-type de HS − MC | Dates avec 5 avant et 5 après | Moyenne de D(t) | Écart-type de D(t) |
|---|---|---|---|---|---|
| 10 ans | 0,22 pb | 0,67 pb | 241 | 0,00 pb | 1,05 pb |
| 20 ans | 0,48 pb | 0,91 pb | 241 | −0,02 pb | 1,22 pb |
| 30 ans | 0,36 pb | 0,95 pb | 241 | 0,00 pb | 1,17 pb |
| Les trois réunies | — | — | 723 | −0,01 pb | 1,15 pb |

- Les écarts-types de HS − MC (0,67 à 0,95 pb) tombent dans la fourchette de 0,2 à 1,0 pb annoncée par le Trésor ; les
  moyennes (0,22 à 0,48 pb) dans sa fourchette de −0,1 à 0,5 pb, avec le sens HS − MC.
- La moyenne de D(t) sur toutes les dates est presque nulle par construction : les poids 2, −1, −1 se compensent quand on
  somme sur des dates consécutives, il ne reste que des termes de bord. Elle sert de point de comparaison : sur les jours
  d'adjudication de P, D moyen vaut 0,71 ; 0,75 ; 0,87 pb selon l'échéance (S1), 0,78 pb au total.
- L'écart-type de D(t) un jour quelconque (1,05 à 1,22 pb) est du même ordre que l'écart-type de D sur les 23 adjudications
  (0,95 pb).
- Aucun test n'est fait sur cette comparaison : la préinscription n'en prévoit pas.

## 7. Difficultés et points à connaître

1. **Aucune difficulté de données.** Le fichier B a répondu du premier coup, a les 35 colonnes attendues et les 251 dates
   attendues ; aucun taux manquant ; aucune source de remplacement utilisée. FRED n'a pas été réinterrogé (la préinscription
   reprend tout du premier test).
2. **Arrondi.** Le fichier B est à deux décimales : D ne prend que les valeurs −1, 0, 1 et 2 pb. La limite 4 de la
   préinscription (hypothèse de normalité « grossière ») s'applique donc pleinement.
3. **V_HS moyen = 1,64 pb**, un peu sous l'ordre de grandeur de 1,7 à 1,9 pb que la préinscription attendait d'après les
   années 2020 et 2021 ; la garde préinscrite porte sur 0,9 pb.
4. **Ordre d'écriture des constats** : notés dans `ecarts.md` après la construction du fichier d'analyse et avant le calcul
   de V et de D (écart E1).
5. **Lecture de la ligne hors exercice** : seule la cellule de la date hors exercice est vide ; l'autre lecture ne change
   aucun chiffre (écart E5).
6. **Ce que le vérificateur ne peut pas refaire** : S3 (fichier brut) et le compte des jours du calendrier C, comme prévu.

Écarts à la préinscription : cinq points dans `ecarts.md` (E1 à E5), aucun n'affecte les douze champs.

## 8. Fichiers

| Fichier | Contenu |
|---|---|
| `donnees/fy2021-mc-vs-hs-combined.csv` | fichier B brut (sha256 `d1111ffb…695d`) |
| `donnees/F04_analyse.csv`, `donnees/DGS10.csv` | copies octet pour octet des fichiers du premier test |
| `donnees/PROVENANCE.md` | URL, date et heure, sha256, nombre de lignes |
| `construire.py`, `construire_journal.json` | construction et son journal |
| `F04-bis_analyse.csv` | fichier d'analyse, 24 lignes, 24 colonnes (sha256 `86ecfc2a…b5b1`) |
| `analyse.py`, `resultats_analyse.json` | analyse et tous ses chiffres, dont S1 à S3 |
| `temoin.json` | les douze champs de la règle |
| `figure.png` | figure du résultat principal |
| `ecarts.md` | constats demandés et écarts |
