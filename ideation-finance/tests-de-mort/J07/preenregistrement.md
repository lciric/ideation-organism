# J07 — Préinscription du test de mort

Rédigé le 2026-11-12 par le rédacteur de préinscription. Ce texte est figé une fois scellé. Le rédacteur n'a lancé aucune
analyse et n'a calculé aucune révision, aucune moyenne, aucune régression sur des données réelles ; ce qu'il a vu des données
est listé à la fin de la section 4. Il n'a ouvert ni le fichier d'analyse, ni les données, ni les scripts, ni les rapports du
test parent H13 : seulement sa préinscription et son `verdict.json`.

## 1. Ce que ce test peut dire, et ce qu'il ne peut pas dire

Le test parent H13 a survécu (n = 309 publications) : le jour de la publication de l'emploi américain, le taux à 2 ans bouge
dans le sens de la partie du premier chiffre qui sera effacée par les révisions des deux mois suivants. Sa préinscription le
dit : ce signe est aussi celui d'un marché rationnel qui **ne peut pas voir** l'erreur ce jour-là. J07 pose la question qui
reste ouverte : **l'erreur était-elle visible ce jour-là avec de l'information publique ?**

Ce que le test mesure : **si une règle publique simple, fixée d'avance et réestimée chaque mois avec la seule information
disponible, aurait prévu la révision (première moins troisième estimation) mieux que le biais historique moyen.** C'est une
condition nécessaire, pas suffisante, pour dire que le marché du parent traite mal l'information :

- si la révision est prévisible avec ces deux variables, un marché qui ne s'en sert pas laisse de l'information publique de
  côté ; mais J07 ne vérifie pas si le taux s'en sert ou non (limite 1, section 10) ;
- si elle ne l'est pas, le coefficient du parent est compatible avec un marché rationnel aveugle au bruit — **avec ces deux
  variables seulement**. Un échec ne montre pas que le bruit est imprévisible ; il montre que ces deux prédicteurs, dans ce
  schéma, ne battent pas la moyenne historique.

## 2. Question, hypothèse et prédiction chiffrée

### Notations

Pour une publication v qui annonce pour la première fois l'emploi du mois m :

- A1 : première estimation de la variation mensuelle de l'emploi salarié (milliers d'emplois) ;
- A3 : troisième estimation de la même variation, publiée environ deux mois plus tard ;
- **N = A1 − A3** : la révision à prévoir (milliers). N > 0 : le premier chiffre était trop haut ;
- **x1 = A1 − T**, où T est la médiane des douze dernières variations mensuelles lues dans la publication précédente :
  écart du chiffre initial à sa tendance récente (premier prédicteur de la fiche) ;
- **x2 = R1 + R2**, somme des révisions, annoncées le jour même, des variations des deux mois précédents (second prédicteur
  de la fiche).

T, R1 et R2 sont exactement les variables `tendance_12m_k`, `rev_m1_k`, `rev_m2_k` de la préinscription H13 ; x1 est sa
« surprise naïve » Sn exprimée en milliers.

### Question

Une régression linéaire de N sur une constante, x1 et x2, réestimée chaque mois en fenêtre croissante sur les seules
publications dont la troisième estimation était déjà connue, prévoit-elle N hors échantillon mieux que la moyenne historique
de N calculée sur les mêmes publications ?

### Hypothèse (celle de la fiche)

Oui : une partie de la révision est prévisible avec ces deux variables publiques.

Sens attendu des coefficients, sans effet sur le verdict (le test compare des erreurs de prévision, pas des signes) :
- **x2 : coefficient négatif attendu.** Si les mois précédents viennent d'être révisés à la hausse, les réponses tardives
  des entreprises sont plus fortes que les premières ; le mois courant sera lui aussi révisé à la hausse, donc A3 > A1 et
  N < 0. C'est la persistance des révisions décrite par Quinlan et Pinheiro (2025) et Decker (2026) d'après la note de
  nouveauté.
- **x1 : signe incertain.** La fiche suppose un retour vers la tendance (premier chiffre loin de la tendance, puis ramené :
  coefficient positif). Mais des révisions procycliques (premier chiffre trop bas quand l'emploi accélère) donnent le signe
  contraire. Krueger et Fortson (2003) trouvent que les estimations successives se suivent comme une marche au hasard, ce qui
  suggère un coefficient proche de zéro. Le test est valable quel que soit ce signe, puisque la régression l'estime.

### Prédiction chiffrée, positionnée contre Neumark et Wascher (1991)

Neumark et Wascher (1991) trouvent, **dans l'échantillon**, que la première estimation de l'emploi salarié n'est pas une
prévision efficiente des chiffres révisés et peut être améliorée avec l'information du jour ; d'après leur résumé, le gain le
plus fort porte sur la **révision de référence annuelle**, dont la part non anticipée baisse de plus de 22 %. J07 diffère sur
trois points qui doivent tous réduire le gain : la cible exclut les révisions de référence (c'est là que leur gain est le
plus fort) ; l'évaluation est hors échantillon, donc l'erreur d'estimation des coefficients est payée ; seules deux variables
sont permises. Krueger et Fortson (2003, marche au hasard d'une estimation à la suivante), Faust, Rogers et Wright (2005,
révisions américaines du PIB difficiles à prévoir) et Cajner et al. (2018, gain « quantitativement modeste » même avec ADP)
vont dans le même sens.

Prédiction du rédacteur, écrite sans avoir vu aucune révision :

- part de la variance de N vraiment prévisible par x1 et x2 (R² de population) : **environ 3 %**, entre 1 % et 6 % ;
- **R² hors échantillon observé : environ +2 %**, entre −1 % et +5 % (la section 7 montre que l'erreur d'estimation retire
  environ 1,5 point au R² de population) ;
- **statistique de Clark-West : environ 2**, entre 0,5 et 3,5 ;
- probabilité de survie que le rédacteur s'attribue : **environ 60 %**.

C'est un ordre de grandeur dix fois plus petit que le gain de Neumark et Wascher sur la révision de référence, et cinq fois
plus petit que les 15 % de la fiche, que le rédacteur juge irréalistes (amendement B1).

## 3. Amendements déclarés

| N° | Fiche | Test préinscrit | Raison |
|---|---|---|---|
| B1 | Prédiction : la correction réduit d'environ **15 %** l'erreur quadratique de prévision de la troisième estimation | Prédiction : R² hors échantillon d'environ **+2 %** (−1 % à +5 %) ; R² de population d'environ 3 % | Faille relevée par les quatre juges : 15 % est très optimiste face à une prévisibilité connue mais faible (section 2). La quantité est la même : prévoir A3 par A1 − N̂ donne exactement les mêmes erreurs que prévoir N par N̂, donc la réduction d'erreur quadratique de la troisième estimation **est** le R² hors échantillon |
| B2 | Survie si R² hors échantillon **≥ 5 %** et Clark-West **> 1,645** | Survie si R² hors échantillon **> 0** et Clark-West **≥ 1,645** | Barre standard de la prévision hors échantillon (Campbell et Thompson pour le R², Clark et West pour la significativité). Le seuil de 5 % confond « petit » et « absent » : avec un R² de population de 5 %, la règle de la fiche ne survit qu'une fois sur trois (section 7), et un échec dirait alors « imprévisible » à tort. Or le parent a besoin de savoir si une prévisibilité **utilisable en temps réel** existe, pas si elle est grande. La taille est rapportée et jugée dans la phrase de conclusion (section 11), qui dit si les 5 % de la fiche sont atteints |
| B3 | « Sinon, abandon de l'hypothèse d'un bruit publiquement prévisible avec cette spécification » | Même sens, écrit plus étroitement : un échec veut dire que **ces deux prédicteurs linéaires, dans ce schéma récursif**, ne battent pas la moyenne historique. Il ne veut pas dire que le bruit est imprévisible, ni que le marché est rationnel | Failles des juges (Kimi, Astra, Claude) : un nul bien obtenu ne conclut que sur cette règle |
| B4 | « Évaluer chronologiquement les publications restantes du parent » | Les publications sont reconstruites de zéro depuis ALFRED, avec les règles de construction de H13 (ses amendements A4 à A7, recopiés en section 4), **sans** la condition sur les taux d'intérêt. L'expérimentateur n'ouvre rien du dossier `tests-de-mort/H13/` sauf sa préinscription | Le test doit rester aveugle aux données du parent. J07 n'a pas besoin des taux : une publication sans taux (par exemple le Vendredi saint 1994-04-01) reste admissible. L'échantillon est donc celui du parent, à quelques lignes près |
| B5 | « Après 60 publications d'apprentissage » | Première prévision : la première publication admissible dont l'ensemble d'apprentissage compte au moins 60 publications admissibles **dont la troisième estimation est publiée au plus tard le jour de cette publication** (le jour même compris) | Rend la règle mécanique. Le jour même est permis : la troisième estimation du mois m − 2 est publiée dans le même communiqué que A1 du mois m, à la même heure ; elle fait partie de l'information disponible à la première publication |
| B6 | Rien sur les publications exclues dans l'apprentissage | Une publication non admissible (révision large, extrême, publication double, ligne incomplète) n'entre ni dans l'évaluation ni dans l'apprentissage | Même échantillon pour estimer et évaluer. Pour une publication d'apprentissage, ces drapeaux sont connus en temps réel : elle n'entre dans l'apprentissage qu'une fois sa troisième estimation publiée, donc après la dernière date qui sert à les calculer. Pour la publication prévue, le drapeau sélectionne l'échantillon d'évaluation de la même façon pour le modèle et pour la référence (limite 3) |
| B7 | « Correction HAC de quatre publications » | Erreur type de Newey-West, noyau de Bartlett, 4 retards, sans correction de petit échantillon, formule écrite en section 6 ; test unilatéral, ≥ 1,645 | Deux personnes doivent obtenir le même nombre. Unilatéral parce que l'alternative de Clark-West est unilatérale (le grand modèle prévoit mieux) ; 1,645 est la valeur qu'ils recommandent à 5 % |
| B8 | « L'évaluateur complètera par simulations scellées, utilisant uniquement l'apprentissage » | Les simulations sont faites maintenant, par le rédacteur, sur des données **synthétiques** seulement ; résultats en section 7. Aucune simulation après lecture des données | Une simulation faite après coup sur l'apprentissage est un choix de plus. Faite avant, elle ne peut rien orienter |
| B9 | « Chaque prévision est écrite et hachée avant déblocage du troisième millésime » | Sans objet : c'est un rejeu historique. Remplacé par (i) un contrôle de schéma qui vérifie que chaque prédicteur est daté au plus tard du jour de publication, (ii) la règle d'apprentissage appliquée par le vérificateur à partir des dates du fichier | Les troisièmes estimations de 1990-2025 sont toutes publiées ; un hachage par prévision ne prouverait rien que les dates du fichier ne prouvent pas |
| B10 | Deux prédicteurs, nommés en mots | Les deux mêmes, définis exactement (section 4). **Aucun autre prédicteur**, aucune transformation, aucune autre fenêtre, ni avant ni après la lecture des données. L'effet de calendrier (révisions d'août et de septembre) signalé par la note de nouveauté n'est **pas** ajouté | La fiche a gelé deux variables ; en ajouter une après la note serait un degré de liberté de plus. L'effet de calendrier est une limite (section 10), à tester ailleurs avec sa propre préinscription |
| B11 | Rien sur l'échantillon minimal ni sur le schéma | Non concluant si le schéma est violé, si moins de 250 publications sont admissibles, ou si moins de 185 prévisions sont faites | Règles du protocole, chiffrées en section 8 |

Inchangés : la cible (première moins troisième estimation), la période (publications du 1990-01-01 au 2025-12-31), les deux
prédicteurs, les moindres carrés ordinaires en fenêtre croissante, la référence (moyenne historique sur les mêmes publications),
les 60 publications d'apprentissage, Clark-West avec HAC à 4 retards, le seuil de 1,645.

## 4. Données

Une seule série, publique, sans compte : l'emploi salarié non agricole `PAYEMS`, en millésimes ALFRED. Aucun taux, aucun
consensus, aucune autre série. L'expérimentateur enregistre chaque fichier brut dans `tests-de-mort/J07/brut/`, avec la date
de téléchargement et son sha256. Il ne réutilise **aucun** fichier du dossier `tests-de-mort/H13/`.

**D1. Liste des dates de millésime.** `https://alfred.stlouisfed.org/series/downloaddata?seid=PAYEMS` (HTML, environ 100 ko,
HTTP 200 d'après la note de nouveauté). Les dates sont les balises `<option value="AAAA-MM-JJ">` du menu
`form[selected_vintage_dates][]`. On garde les dates du 1989-12-01 au 2026-03-31 : **438 attendues** (chiffre de H13), la
première étant 1989-12-08. Les millésimes de 2026 servent seulement à lire les troisièmes estimations de fin 2025.

**D2. Niveaux de `PAYEMS` par millésime.** Syntaxe exacte, un millésime par requête :

```
https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS&vintage_date=AAAA-MM-JJ
```

Testée le 2026-11-12 avec `vintage_date=1990-02-02` : HTTP 200, 10 494 octets, en-tête `observation_date,PAYEMS_19900202`,
première ligne `1939-01-01,29750`. Réponse : une ligne par mois depuis 1939 (`observation_date` = premier jour du mois), une
colonne `PAYEMS_AAAAMMJJ`, en milliers d'emplois, entiers, corrigés des variations saisonnières ; champ vide pour un mois pas
encore publié.

Requête groupée admise, **12 millésimes au plus** :
`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS,PAYEMS,…&vintage_date=AAAA-MM-JJ,AAAA-MM-JJ,…` (même nombre
d'identifiants que de dates ; testée sur deux millésimes, en-tête `observation_date,PAYEMS_19900202,PAYEMS_19900309`).
Contrôles à chaque requête, repris de H13 :
- l'en-tête compte exactement une colonne par millésime demandé, dans l'ordre demandé (au-delà de 12, la réponse est
  tronquée sans message) ;
- ne jamais utiliser `fred.stlouisfed.org/graph/fredgraph.csv` : il ignore `vintage_date` et rend le millésime courant ;
- ne demander que des dates de D1 (une date qui n'est pas un millésime ne produit pas d'erreur).

Une requête qui échoue est retentée jusqu'à trois fois. Si un millésime de D1 reste introuvable, le fichier n'est pas
construit et le test est non concluant.

### Procédure de reconstruction (identique à H13, étapes 1 à 3 et 5)

Notations : L(j ; v) est le niveau du mois j lu dans le millésime v ; Δ(j ; v) = L(j ; v) − L(j − 1 ; v), variation calculée
**à l'intérieur du seul millésime v** ; fin(v) est le dernier mois non vide de v.

1. **Millésimes.** Télécharger D1, puis D2 pour les 438 dates.
2. **Publications.** Parcourir les millésimes dans l'ordre. Le premier (1989-12-08) est une publication. Ensuite, un millésime
   v est une publication si fin(v) est postérieur à fin du millésime qui le précède dans la liste complète ; sinon c'est une
   correction, écartée. Attendu : 3 corrections (2002-12-09, 2003-10-10, 2020-05-11), 435 publications, dont **431** datées
   du 1990-01-01 au 2025-12-31. La date de publication est la date du millésime. prec(v) est la publication qui précède v.
   Tout autre décompte est écrit dans `ecarts.md` ; le fichier est construit tel que la règle le donne.
3. **Pour chaque publication v datée du 1990-01-01 au 2025-12-31**, avec m = fin(v) et m′ = fin(prec(v)) :
   - nombre de mois nouveaux : nombre de mois de m′ + 1 à m (1 en temps normal ; 2 pour la publication double du 2025-12-16) ;
   - A1 = Δ(m ; v) ;
   - v3 = la première publication w postérieure à v telle que fin(w) ≥ m + 2 ; A3 = Δ(m ; v3) ;
   - R1 = Δ(m′ ; v) − Δ(m′ ; prec(v)) ; R2 = Δ(m′ − 1 ; v) − Δ(m′ − 1 ; prec(v)) ;
   - T = médiane des douze valeurs Δ(j ; prec(v)), j = m′ − 11, …, m′ (moyenne de la 6ᵉ et de la 7ᵉ valeur triée).
4. **Millésimes de révision large.** Une publication w est « de révision large » si, pour au moins un des dix mois
   j = m′ − 11, …, m′ − 2 (m′ = fin(prec(w))), L(j ; w) ≠ L(j ; prec(w)). La publication v reçoit `revision_large` = 1 si une
   publication w de révision large vérifie date(v) ≤ date(w) ≤ date(v3). Ainsi N ne contient jamais une révision de
   référence, de coefficients saisonniers ou une correction.
5. **Extrêmes de 2020** (règle A7 de H13, inchangée) : `extreme` = 1 si |A1| > 1 000 milliers, ou si A3 existe et
   |A1 − A3| > 500 milliers.
6. **Publication double** : la publication du 2025-12-16 (octobre et novembre 2025 ensemble) a `n_mois_nouveaux` = 2 et
   sort de l'échantillon, comme dans H13. Octobre 2025 n'a pas de première estimation isolée et n'apparaît pas.

Exemple de contrôle (note de nouveauté, déjà dans H13) : publication du 1990-02-02, mois de janvier 1990. A1 = 109 823 −
109 548 = +275. v3 = 1990-04-06, A3 = 109 931 − 109 570 = +361. N = −86.

**Ce qui compte comme manquant.**
- Une publication dont A3, R1, R2 ou T ne peut pas être calculé : `complet` = 0, hors apprentissage et hors évaluation,
  comptée dans le fichier. Attendu : aucune pour 1990-2025, puisque les millésimes vont jusqu'au 2026-03-31.
- D1 ou un millésime de D2 introuvable, ou de colonnes différentes de celles décrites : test non concluant.
- Moins de 250 publications admissibles, ou moins de 185 prévisions : non concluant (section 8).

**Ce que le rédacteur a vu.** L'en-tête et la première ligne (janvier 1939) des millésimes `PAYEMS` du 1990-02-02 et du
1990-03-09, par les deux requêtes ci-dessus. Les seules valeurs d'emploi de la période étudiée qu'il connaît sont celles de la
note de nouveauté (janvier 1990 ; quelques niveaux de 1989 et de 2025 cités par elle). Du parent, il connaît le verdict
(« survit »), n = 309 et le coefficient du taux, lus dans `H13/verdict.json` ; rien de la prévisibilité de N n'y figure. Sa
connaissance des chiffres de 2020 vient de sa mémoire. Aucune révision, aucune moyenne, aucune régression, aucune statistique
n'a été calculée sur des données réelles ; la section 7 est calculée sur des données synthétiques.

## 5. Fichier d'analyse

Nom : `tests-de-mort/J07/J07_analyse.csv`. UTF-8, virgule, point décimal, une ligne d'en-tête, champ vide pour une valeur
manquante, dates au format AAAA-MM-JJ. **Une ligne par publication** datée du 1990-01-01 au 2025-12-31, triée par
`date_publication`. Attendu : 431 lignes. Toutes les quantités d'emploi sont en **milliers d'emplois**.

| N° | Colonne | Type | Unité, contenu |
|---|---|---|---|
| 1 | `date_publication` | date | date du millésime de publication v ; unique |
| 2 | `mois_reference` | texte AAAA-MM | m = fin(v) |
| 3 | `n_mois_nouveaux` | entier | 1 ou 2 |
| 4 | `date_millesime_precedent` | date | date de prec(v) |
| 5 | `date_millesime_3e` | date | date de v3 ; vide si v3 n'existe pas dans D2 |
| 6 | `date_info_predicteurs` | date | date du plus récent millésime lu pour calculer `emploi_1re_k`, `rev_m1_k`, `rev_m2_k` et `tendance_12m_k`, prise dans l'en-tête `PAYEMS_AAAAMMJJ` des colonnes effectivement lues |
| 7 | `emploi_1re_k` | entier | A1, milliers |
| 8 | `emploi_3e_k` | entier | A3, milliers ; vide si `date_millesime_3e` est vide |
| 9 | `rev_m1_k` | entier | R1, milliers |
| 10 | `rev_m2_k` | entier | R2, milliers |
| 11 | `tendance_12m_k` | décimal | T, milliers par mois ; multiple de 0,5 |
| 12 | `revision_large` | entier | 0 ou 1 (étape 4) |
| 13 | `extreme` | entier | 0 ou 1 (étape 5) |
| 14 | `complet` | entier | 1 si `emploi_3e_k`, `rev_m1_k`, `rev_m2_k`, `tendance_12m_k` sont tous présents ; sinon 0 |
| 15 | `admissible` | entier | 1 si `complet` = 1, `n_mois_nouveaux` = 1, `revision_large` = 0 et `extreme` = 0 ; sinon 0 |
| 16 | `cible_N_k` | entier | N = `emploi_1re_k` − `emploi_3e_k` ; vide si `emploi_3e_k` est vide |
| 17 | `pred_ecart_tendance_k` | décimal | x1 = `emploi_1re_k` − `tendance_12m_k` |
| 18 | `pred_somme_revisions_k` | entier | x2 = `rev_m1_k` + `rev_m2_k` |

**Contrôles de schéma** (le vérificateur les exécute ; `schema_ok` = 1 si tous passent, 0 sinon) :
1. Les 18 colonnes ci-dessus, dans cet ordre, et aucune autre.
2. Entre 425 et 435 lignes ; `date_publication` unique, strictement croissante, entre 1990-01-01 et 2025-12-31.
3. `mois_reference` strictement croissant ; l'écart entre `date_publication` et le premier jour de `mois_reference` est de 28
   à 110 jours civils.
4. `n_mois_nouveaux` ∈ {1, 2}, au plus deux lignes à 2 ; `revision_large`, `extreme`, `complet`, `admissible` ∈ {0, 1}.
5. **Datation des prédicteurs (pas d'information future)** : sur chaque ligne, `date_millesime_precedent` <
   `date_publication` ; `date_info_predicteurs` ≤ `date_publication` ; si elle est présente, `date_millesime_3e` >
   `date_publication` et `date_millesime_3e` ≤ 2026-03-31.
6. `cible_N_k`, `pred_ecart_tendance_k`, `pred_somme_revisions_k`, `extreme`, `complet` et `admissible` valent exactement ce
   que leur définition donne à partir des autres colonnes.
7. Bornes : |`emploi_1re_k`| ≤ 25 000 ; |`tendance_12m_k`| ≤ 25 000 ; |`rev_m1_k`| et |`rev_m2_k`| ≤ 25 000.
8. Ligne du 1990-02-02 : `mois_reference` = 1990-01, `emploi_1re_k` = 275, `date_millesime_3e` = 1990-04-06, `emploi_3e_k`
   = 361, `cible_N_k` = −86.

## 6. Statistique

### Échantillon

A = les lignes où `admissible` = 1, triées par `date_publication` ; `n_admissibles` = leur nombre. Pour une ligne i de A :
y_i = `cible_N_k`, x1_i = `pred_ecart_tendance_k`, x2_i = `pred_somme_revisions_k`, d_i = `date_publication`,
d3_i = `date_millesime_3e`. Double précision, sans arrondi intermédiaire.

### Prévisions récursives

Pour chaque ligne i de A, l'ensemble d'apprentissage est **S_i = { j dans A : d3_j ≤ d_i }** (troisième estimation publiée au
plus tard le jour de la publication i ; on a toujours j avant i). Si S_i compte moins de 60 lignes, la ligne i ne sert qu'à
l'apprentissage. Sinon, on fait une prévision :

- **modèle** : moindres carrés ordinaires de y sur (1, x1, x2) sur les lignes de S_i, coefficients b(i) ; prévision
  ŷ1_i = b0(i) + b1(i)·x1_i + b2(i)·x2_i ;
- **référence** : ŷ0_i = moyenne de y sur S_i (le biais historique, estimé sur exactement les mêmes lignes).

E est l'ensemble des lignes prévues, dans l'ordre chronologique ; `n_previsions` = P = son nombre ;
`premiere_prevision_aaaammjj` = date de la première ligne de E écrite comme un entier AAAAMMJJ. Attendu : P ≈ 248, première
prévision vers 1996.

Erreurs : e0_i = y_i − ŷ0_i, e1_i = y_i − ŷ1_i. Prévoir la troisième estimation par A1 − ŷ donne exactement ces mêmes
erreurs ; ce qui suit vaut donc aussi pour la prévision de A3.

### Statistique principale : Clark-West (une seule)

f_i = e0_i² − [ e1_i² − (ŷ0_i − ŷ1_i)² ], pour i dans E. (Algébriquement, f_i = 2 (ŷ1_i − ŷ0_i)(y_i − ŷ0_i) : f est positif
en moyenne si l'écart du modèle à la moyenne va dans le sens de l'écart réel.)

- f̄ = (1/P) Σ f_i ;
- autocovariances, pour l = 0, 1, 2, 3, 4 : γ_l = (1/P) Σ_{k = l+1}^{P} (f_(k) − f̄)(f_(k−l) − f̄), où f_(k) est la k-ième
  valeur de E dans l'ordre chronologique (les retards comptent les positions dans E, pas les mois du calendrier) ;
- variance de long terme de Newey-West, noyau de Bartlett, 4 retards : Ω = γ_0 + 2 Σ_{l=1}^{4} (1 − l/5) γ_l ;
- **`cw_stat` = f̄ / racine(Ω / P).** Aucune correction de petit échantillon.

Avec `statsmodels` : `OLS(f, ones(P)).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})` doit redonner
la même valeur ; en cas d'écart, la formule ci-dessus fait foi.

### Taille de l'effet (seconde condition de survie)

- **`r2_hors_echantillon`** = 1 − Σ_E e1_i² / Σ_E e0_i² (fraction, pas pour cent) ;
- `reqm_reference_k` = racine((1/P) Σ_E e0_i²) et `reqm_modele_k` = racine((1/P) Σ_E e1_i²), en milliers d'emplois.

Pourquoi ces choix :
- **Fenêtre croissante** (récursive) : c'est le schéma de la fiche, et il n'a aucun paramètre à choisir ; une fenêtre
  glissante demanderait une longueur, donc un choix de plus.
- **Clark-West plutôt que Diebold-Mariano** : les deux modèles sont emboîtés (la référence est le modèle avec b1 = b2 = 0).
  Sous l'hypothèse nulle, le grand modèle estime deux coefficients nuls et paie ce bruit ; Diebold-Mariano est alors trop
  conservateur. Clark-West ajoute le terme (ŷ0 − ŷ1)² pour retirer ce bruit attendu.
- **4 retards** : chiffre de la fiche. Il couvre la dépendance attendue : la publication t + 2 révise à la fois le mois m
  (deuxième révision) et le mois m + 1 (première révision), donc N_t, N_{t+1} et N_{t+2} partagent des chocs. La règle
  usuelle ⌊4 (P/100)^{2/9}⌋ donne aussi 4 pour P entre 185 et 270.
- **R² hors échantillon > 0** en plus de Clark-West : Clark-West teste si les coefficients de population sont non nuls ; il
  peut rejeter alors que la règle estimée **perd** contre la moyenne dans l'échantillon. Pour la question du parent, ce qui
  compte est qu'un utilisateur en temps réel aurait **réellement** amélioré sa prévision.

### Analyses secondaires, descriptives, sans effet sur le verdict (trois au plus)

- **S1. Chaque prédicteur seul.** Même procédure, mêmes lignes E, avec (1, x1) puis (1, x2) : rapporter R² hors échantillon
  et Clark-West de chacun. Dit lequel des deux porte la prévisibilité.
- **S2. Stabilité dans le temps.** Prévisions inchangées ; R² hors échantillon et Clark-West recalculés sur trois morceaux de
  E : `date_publication` < 2008-01-01 ; de 2008-01-01 à 2019-12-31 ; ≥ 2020-01-01. Plus la figure de la fiche : somme
  cumulée de e0_i² − e1_i² en fonction de la date. Répond au risque « régime ancien » de la fiche.
- **S3. Version dans l'échantillon, à la Neumark et Wascher.** Moindres carrés de y sur (1, x1, x2) sur toutes les lignes de
  A ; rapporter les trois coefficients et leurs erreurs types Newey-West (Bartlett, 4 retards), le R² dans l'échantillon, la
  moyenne et l'écart-type de y, et les coefficients b(i) de la dernière prévision. Montre l'écart entre prévisibilité dans
  l'échantillon et hors échantillon.

L'expérimentateur rapporte aussi le nombre de lignes écartées par chaque filtre (`complet`, `n_mois_nouveaux`,
`revision_large`, `extreme`) et la liste des dates où `extreme` = 1.

`temoin.json` et `verification.json` sont des objets JSON plats portant les huit champs de la règle (section 12). S1 à S3
peuvent y figurer sous une clé `descriptif` ; elles ne sont ni comparées ni lues par le verdict.

## 7. Arithmétique de puissance

Aucune donnée réelle n'a été lue pour cette section.

**Nombre de prévisions.** 431 publications ; H13 en a gardé 309 avec en plus la condition sur les taux, qui ne retirait
qu'environ une ligne. Attendu : environ 310 publications admissibles. Les 60 premières (avec le décalage de deux mois pour que
leur troisième estimation soit publiée, environ 62) ne servent qu'à apprendre : **P ≈ 248**. Cas prudent (fiche) : P ≈ 220.

**Intuition.** Soit q la part de la variance de N vraiment prévisible par x1 et x2. Sous l'alternative, f a une moyenne
d'environ 2q·σ² et le rapport signal sur bruit de Clark-West est d'environ √P · q / √(q + s), où s est le bruit d'estimation
des deux pentes (environ 2 divisé par la taille moyenne d'apprentissage, soit à peu près 0,013). Le R² hors échantillon a lui
une moyenne d'environ q − s : **si moins d'environ 1,5 % de la variance est prévisible, la règle estimée perd contre la
moyenne en temps réel**, même si la prévisibilité existe dans la population.

**Simulation, données synthétiques.** x1 et x2 normaux de corrélation 0,3 ; N = constante + partie prévisible de variance q +
bruit ; bruit normal ou de Student à 4 degrés de liberté (queues épaisses) ; 310 ou 280 publications ; décalage d'apprentissage
de 2 ; 60 publications d'apprentissage minimum ; exactement la statistique de la section 6 ; 1 000 tirages par case
(graines 20261112 et 7). Probabilité de **survie** (Clark-West ≥ 1,645 et R² hors échantillon > 0) :

| q (R² de population) | P = 249, bruit normal | P = 249, queues épaisses | P = 219, bruit normal | P = 219, queues épaisses | R² hors échantillon médian (P = 249, normal) |
|---|---|---|---|---|---|
| 0 | 4,1 % | 3,0 % | 4,2 % | 2,3 % | −1,3 % |
| 1 % | 23 % | 26 % | 20 % | 23 % | −0,6 % |
| 2 % | 46 % | 49 % | 40 % | 44 % | +0,4 % |
| 3 % | 68 % | 67 % | 58 % | 60 % | +1,7 % |
| 5 % | 89 % | 88 % | 85 % | 85 % | +3,3 % |
| 8 % | 99 % | 98 % | 97 % | 96 % | +6,4 % |
| 15 % | 100 % | 100 % | 100 % | 100 % | +13,5 % |

Même simulation, règle de la fiche (R² hors échantillon ≥ 5 % et Clark-West > 1,645), P = 249, bruit normal : survie 8 % à
q = 3 %, 32 % à q = 5 %, 68 % à q = 8 %, 99 % à q = 15 %.

**Ce que le test peut détecter.** Une prévisibilité de 5 % de la variance ou plus est détectée environ neuf fois sur dix ; de
3 %, deux fois sur trois. Le risque de survie à tort, sans aucune prévisibilité, est de 2 à 4 % (Clark-West est légèrement
conservateur en schéma récursif).

**Ce qu'il ne peut pas détecter.** Une prévisibilité de 2 % ou moins : l'issue est alors à pile ou face ou pire. Ce n'est pas
seulement un défaut de puissance : à ce niveau, la règle estimée sur 60 à 300 publications perd contre la moyenne en temps
réel (R² médian ≤ 0,4 %), donc ni le chercheur ni le marché n'auraient pu s'en servir avec ces deux variables.

**Limites de ce calcul.** Prédicteurs indépendants dans le temps et relation stable ; or les révisions sont persistantes et
peut-être plus fortes en 2020-2025 (Decker, 2026). Un effet concentré sur une période récente est moins bien détecté par une
fenêtre croissante. S2 le décrit sans changer le verdict.

Coût : environ 438 requêtes légères (ou 37 groupées) et 250 régressions à trois coefficients. Quelques minutes sur un
portable, téléchargement compris.

## 8. Règle de verdict

Le verdict s'applique aux nombres du vérificateur. On regarde d'abord « non concluant », puis « survit ».

**Non concluant** si l'une de ces conditions tient :
- `schema_ok` < 1 ;
- `n_admissibles` < 250 ;
- `n_previsions` < 185 ;
- (protocole) une donnée nommée manque, un champ n'est pas calculable, ou l'expérimentateur et le vérificateur diffèrent de
  plus que la tolérance.

**Survit** (la révision est prévisible hors échantillon avec ces deux variables) si toutes ces conditions tiennent :
`cw_stat` ≥ 1,645 ; `r2_hors_echantillon` > 0 ; `schema_ok` ≥ 1 ; `n_admissibles` ≥ 250 ; `n_previsions` ≥ 185.

**Éliminée** sinon : échantillon et schéma valides, et Clark-West < 1,645 ou R² hors échantillon ≤ 0. La phrase de
conclusion distingue ces deux cas.

**Justification des seuils.**
- **1,645** : valeur critique unilatérale à 5 % de la loi normale, recommandée par Clark et West (2007) ; c'est aussi celle de
  la fiche. La simulation donne un risque réel de survie à tort de 2 à 4 %.
- **R² hors échantillon > 0** : la règle doit battre la référence en erreur quadratique sur les prévisions effectivement
  faites. C'est la barre usuelle (Campbell et Thompson, 2008). Aucun seuil économique n'est ajouté au verdict : la question
  du parent est qualitative (une information publique utilisable existait-elle ?), et un seuil de 5 % ferait dire
  « imprévisible » à une prévisibilité de 5 % deux fois sur trois (section 7). La taille est jugée dans la phrase de
  conclusion, qui dit si le R² atteint les 5 % de la fiche et donne le gain en milliers d'emplois (`reqm_reference_k` −
  `reqm_modele_k`).
- **250 publications admissibles** : le minimum du parent ; l'attendu est d'environ 310. En dessous, la construction ne s'est
  pas passée comme prévu.
- **185 prévisions** : 250 moins environ 65 publications d'apprentissage. Au minimum (P = 185), la puissance à q = 5 % reste
  d'environ quatre sur cinq d'après l'interpolation de la section 7.

**Tolérances** entre expérimentateur et vérificateur : 0 sur `schema_ok`, `n_admissibles`, `n_previsions` et
`premiere_prevision_aaaammjj` (comptes et dates : aucun arrondi possible) ; 0,0005 sur `r2_hors_echantillon` ; 0,02 sur
`cw_stat` ; 0,05 millier sur les deux REQM. Les deux calculent sur le même fichier avec des formules fermées : un écart plus
grand signale une erreur, pas un arrondi.

## 9. Ce qui relie le résultat au parent

- **Survie** : avec deux variables publiques du jour, une règle simple prévoyait une partie de N. Le coefficient de H13 n'est
  donc pas **forcément** celui d'un marché aveugle à un bruit invisible : une part du bruit était visible. Pour dire que le
  marché ne s'en est pas servi, il faudrait un autre test (régresser la variation du taux sur la partie prévue et la partie
  imprévue de N), qui demande les taux et n'est pas fait ici.
- **Élimination** : ces deux variables ne permettaient pas, en temps réel, de mieux prévoir N que le biais moyen. La lecture
  « marché rationnel aveugle au bruit » du coefficient de H13 reste possible ; elle n'est pas démontrée, car d'autres
  informations publiques (inscriptions au chômage, ADP, consensus, calendrier) n'ont pas été testées.

## 10. Limites

1. **J07 mesure la prévisibilité, pas l'usage qu'en fait le marché.** Même en cas de survie, rien ne dit que le taux à 2 ans
   ignore la partie prévisible ; le lien avec l'efficience du marché du parent reste une condition nécessaire, pas une preuve.
2. **Un échec ne vaut que pour deux prédicteurs linéaires, dans un schéma récursif.** Inscriptions hebdomadaires au chômage,
   ADP (depuis 2006), consensus des économistes, effets de calendrier d'août et de septembre, taux de réponse : non testés.
3. **L'échantillon d'évaluation est choisi avec de l'information future** : les drapeaux `revision_large` et `extreme`
   d'une publication prévue dépendent de ce qui se passe jusqu'à sa troisième estimation (et pour `extreme`, de N lui-même,
   ce qui écarte au moins mars 2020, de mémoire). La sélection est la même pour le modèle et la référence ; elle définit la
   question (révisions d'échantillon hors crise), mais le résultat ne vaut pas pour les mois écartés (environ un quart).
4. **Puissance faible sous 3 % de variance prévisible** (section 7).
5. **Instabilité possible.** Si la prévisibilité n'existe qu'en 2020-2025, la fenêtre croissante la dilue. Aucune fenêtre
   glissante n'est testée, pour ne pas ajouter de choix ; S2 décrit les sous-périodes sans effet sur le verdict.
6. **Approximation de Clark-West.** La loi normale de la statistique est une approximation, établie surtout pour les fenêtres
   glissantes ; en fenêtre croissante elle est légèrement conservatrice (2 à 4 % de fausses survies en simulation).
7. **La troisième estimation n'est pas la vérité.** Elle sera encore révisée par les révisions de référence ; N ne mesure que
   la correction apportée par les réponses tardives en deux mois.
8. **Dates de publication déduites d'ALFRED**, sans recoupement avec le calendrier du BLS (limite 9 de H13). Une erreur de
   date d'un jour ne change pas l'information disponible ici, puisque toutes les variables viennent du même communiqué.
9. **Les ordres de grandeur de la section 7 sont supposés** : données synthétiques, prédicteurs indépendants dans le temps.

## 11. Ce qu'on écrira dans chaque cas

- **Survit.** « Sur P publications de l'emploi américain de 1996 à 2025, hors révisions de référence et hors 2020, une
  régression réestimée chaque mois sur l'écart du premier chiffre à sa tendance et sur les révisions annoncées le jour même a
  prévu la révision des deux mois suivants mieux que le biais historique (R² hors échantillon de X %, Clark-West de Y,
  erreur quadratique moyenne ramenée de Z0 à Z1 milliers d'emplois ; X atteint / n'atteint pas les 5 % de la fiche) : une
  partie du bruit lu par le marché dans H13 était visible le jour même, sans que ce test dise si le marché l'a utilisée. »
- **Éliminée, Clark-West sous 1,645.** « Sur les mêmes publications, ces deux variables publiques n'ont pas prévu la révision
  mieux que le biais historique (R² hors échantillon de X %, Clark-West de Y) : avec cette règle, le bruit du premier chiffre
  n'était pas visible le jour même, ce qui laisse possible, sans la démontrer, la lecture du coefficient de H13 comme celle
  d'un marché rationnel aveugle au bruit, et ne dit rien des informations publiques non testées. »
- **Éliminée, Clark-West ≥ 1,645 mais R² hors échantillon ≤ 0.** « Les deux variables sont liées à la révision dans la
  population (Clark-West de Y), mais la règle estimée en temps réel n'a pas battu le biais historique (R² hors échantillon de
  X %) : un prévisionniste, ou un marché, qui s'en serait servi n'aurait rien gagné, et cette prévisibilité n'est pas
  exploitable avec cette règle. »
- **Non concluant.** « Le test ne tranche pas, pour la raison suivante : [schéma violé / moins de 250 publications
  admissibles / moins de 185 prévisions / donnée manquante / désaccord entre expérimentateur et vérificateur] ; on ne conclut
  ni à la prévisibilité de la révision ni à son absence. »

## 12. Règle lisible par machine

```json
{
  "id": "J07",
  "fichier_analyse": "J07_analyse.csv",
  "champs_verification": [
    "schema_ok",
    "n_admissibles",
    "n_previsions",
    "premiere_prevision_aaaammjj",
    "cw_stat",
    "r2_hors_echantillon",
    "reqm_reference_k",
    "reqm_modele_k"
  ],
  "survit_si": [
    {"champ": "cw_stat", "operateur": ">=", "seuil": 1.645},
    {"champ": "r2_hors_echantillon", "operateur": ">", "seuil": 0},
    {"champ": "schema_ok", "operateur": ">=", "seuil": 1},
    {"champ": "n_admissibles", "operateur": ">=", "seuil": 250},
    {"champ": "n_previsions", "operateur": ">=", "seuil": 185}
  ],
  "non_concluant_si": [
    {"champ": "schema_ok", "operateur": "<", "seuil": 1},
    {"champ": "n_admissibles", "operateur": "<", "seuil": 250},
    {"champ": "n_previsions", "operateur": "<", "seuil": 185}
  ],
  "tolerance": {
    "schema_ok": 0,
    "n_admissibles": 0,
    "n_previsions": 0,
    "premiere_prevision_aaaammjj": 0,
    "cw_stat": 0.02,
    "r2_hors_echantillon": 0.0005,
    "reqm_reference_k": 0.05,
    "reqm_modele_k": 0.05
  }
}
```
