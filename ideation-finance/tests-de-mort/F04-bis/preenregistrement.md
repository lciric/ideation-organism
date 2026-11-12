**PROJET NON SCELLÉ — brouillon à lire, amender et sceller par la personne qui dirige le projet ; tant qu'il n'est pas scellé, aucune ligne de données du fichier des deux méthodes ne doit être ouverte.**

# F04-bis — Projet de préinscription du test de mort : la cassure de 2021 vient-elle de la mesure ?

Rédigé le 2026-11-12 par le rédacteur de préinscription. Le rédacteur n'a lancé aucune analyse et n'a lu aucune ligne de
données du fichier des deux méthodes. Pour sceller : relire, trancher les choix de la section 11, retirer la première ligne,
enregistrer sous `tests-de-mort/F04-bis/preenregistrement.md` (nom lu par `verdict.py`), puis calculer le sha256.

Vérification demandée avant d'écrire : l'en-tête du fichier des deux méthodes contient bien ce qu'il faut (une colonne `date`,
et pour chaque méthode les taux nominaux à 10, 20 et 30 ans). Le test est donc faisable tel que prévu.

## 1. Ce qui a déjà été vu, et ce qui n'a pas été vu

**Déjà vu (résultats).**
- Premier test (F04, scellé, verdict « survit ») : moyenne de V = 0,91 pb, t = 5,6, sur 321 réouvertures de 2010 à 2026.
- Découpe par année faite **après** le verdict : V vaut 1,0 à 2,2 pb par an de 2011 à 2021 (2020 : 1,92 ; 2021 : 1,72), puis
  0,30 ; −0,03 ; 0,23 ; −0,54 ; 0,39 de 2022 à 2026 (moyenne simple de ces cinq chiffres : 0,07).
- Autre découpe faite après le verdict (`F04/controle-orchestrateur.md`) : 1,10 pb avant août 2024 (erreur type 0,16 ; 270
  adjudications), −0,13 pb depuis (0,33 ; 51) ; −0,13 pb sur le 20 ans (52 adjudications).
- Écart-type de V sur les 321 réouvertures : 2,57 pb (`F04/ecarts.md`, point E6).
- Conséquence à dire franchement : les adjudications de ce test font partie de celles des années 2020 et 2021 déjà regardées.
  Le V calculé avec l'ancienne méthode sur cet échantillon est donc déjà à peu près connu (de l'ordre de 1,7 à 1,9 pb). Ce
  qui est neuf, c'est uniquement le V calculé avec la nouvelle méthode, donc la différence entre les deux.

**Déjà vu (faits sur la mesure).** Pages du Trésor relues le 2026-11-12 (HTTP 200) :
- `https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology` :
  la méthode « monotone convexe » (MC) a remplacé la spline d'Hermite quasi cubique (HS) le 6 décembre 2021.
- `https://home.treasury.gov/policy-issues/financing-the-government/yield-curve-methodology-change-information-sheet` : du
  1er octobre 2020 au 30 septembre 2021, les écarts moyens « entre MC et HS » vont de −0,1 à 0,5 pb selon l'échéance, avec des
  écarts-types de 0,2 à 1,0 pb. Le texte ne dit pas quelle échéance est à quel bout de ces fourchettes, ni le sens exact de la
  soustraction. Il dit aussi que HS prend les rendements de marché comme s'ils étaient au pair, alors que MC part des prix.

**Déjà vu (pour écrire ce projet).**
- La première ligne du fichier des deux méthodes (noms de colonnes, section 3). Rien d'autre de ce fichier.
- La première ligne de `F04/F04_analyse.csv` (noms de colonnes). Aucune autre ligne.
- `F04/preenregistrement.md`, `F04/ecarts.md`, `F04/construire_journal.json` (comptes de lignes), la liste des fichiers de `F04/`.
- Pour compter les adjudications : les dates et échéances des adjudications (`F04/donnees/auctions_query.json`) et la liste
  des dates où `DGS10` n'est pas vide (`F04/donnees/DGS10.csv`). Le petit script de comptage a seulement testé si la valeur
  de `DGS10` était vide et n'a affiché que des dates ; aucun rendement n'a été affiché ni utilisé dans un calcul.

**Pas vu.** Toutes les lignes de données du fichier des deux méthodes : aucune valeur, aucune date, pas même le nombre de
lignes, le format des dates ou le nombre de décimales. Pas vu non plus : les lignes de `F04/F04_analyse.csv`, les rapports de
l'expérimentateur et du vérificateur de F04, la figure par année (seuls ses chiffres cités ci-dessus sont connus).

## 2. Question, hypothèses rivales et prédiction chiffrée

**Question.** La disparition de V après 2021 vient-elle du changement de méthode de la courbe du Trésor (la mesure) plutôt que
d'un changement du marché ?

**Ce que le test fait.** Sur les mêmes adjudications, aux mêmes dates, avec la même courbe ajustée (GSW), on calcule V deux
fois : une fois avec le taux de l'ancienne méthode (V_HS), une fois avec celui de la nouvelle (V_MC). On étudie la différence
appariée D = V_HS − V_MC. D dit de combien de points de base le V d'une adjudication baisse quand on passe de l'ancienne
méthode à la nouvelle, tout le reste étant identique.

**La cassure à expliquer.** 1,75 pb : moyenne de V en 2020 et 2021 (1,92 et 1,72, soit 1,82) moins moyenne des cinq années
2022 à 2026 (0,07). Ce chiffre vient de la découpe exploratoire ; il est fixé ici et ne sera pas recalculé.

**Deux lectures rivales, et ce que chacune prédit.**

| Lecture | Moyenne de D | Moyenne de V_MC |
|---|---|---|
| « La mesure a changé » : l'ancienne méthode produit le V, la nouvelle non | proche de la cassure : environ 1,75 pb (disons 1,3 à 2,2) | proche de zéro, comme en 2022-2026 (−0,5 à 0,5 pb) |
| « Le marché a changé » : la méthode n'y est pour rien | proche de zéro (−0,3 à 0,3 pb) | proche de V_HS, attendu vers 1,7 à 1,9 pb |
| Entre les deux | 0,5 à 1,3 pb | 0,5 à 1,3 pb |

Dans l'échantillon, moyenne de V_MC = moyenne de V_HS − moyenne de D, exactement. Les deux colonnes disent donc la même chose
de deux façons ; la moyenne de V_MC n'apporte pas d'information indépendante, elle aide à lire le résultat.

**Hypothèse mise à mort.** « La mesure explique la cassure » : le changement de méthode retire en moyenne plus de la moitié
de la cassure, soit plus de 0,9 pb. « Survit » veut dire que cette hypothèse tient ; « éliminée » qu'elle tombe.

**Quel résultat serait le plus intéressant.** « Survit ». Ce serait un résultat net et facile à raconter : une statistique
officielle très utilisée fabrique ou efface, selon sa méthode, un effet de la taille de celui qu'on mesure, à une date précise.
C'est aussi le résultat que le bilan appelle « la piste la plus intéressante ». La règle ne doit pas le favoriser : elle est
symétrique autour d'un seul seuil (même valeur critique, même exigence des deux côtés), et le risque de conclure à tort est au
plus de 2,5 % dans chaque sens (section 6).

**Avis du rédacteur, sans effet sur la règle.** Le Trésor écrit que le changement « n'affecte pas matériellement » les taux,
et un écart constant entre les deux méthodes s'annule dans V. Pour que D vaille 1,75 pb, il faudrait que l'écart entre méthodes
monte d'environ 0,9 pb le jour de l'adjudication par rapport aux jours J − 5 et J + 5, de façon répétée. Le rédacteur ne
connaît pas de mécanisme qui le ferait. Il trouve « éliminée » plus probable que « survit ».

## 3. Données

Le seul ingrédient nouveau est le fichier des deux méthodes. Tout le reste est repris du premier test, sans retéléchargement.

**A. Fichier d'analyse du premier test.** `tests-de-mort/F04/F04_analyse.csv` (construit selon la préinscription scellée de
F04 ; ses 1 926 valeurs de rendement des lignes principales ont été contrôlées contre les fichiers bruts par l'orchestrateur).
On y prend : la sélection des adjudications, les trois dates de chaque fenêtre, les taux FRED (`cmt_*`) et les taux de la
courbe ajustée (`gsw_*`). L'expérimentateur note son sha256.

**B. Fichier des deux méthodes (Trésor).**
`https://home.treasury.gov/system/files/221/fy2021-mc-vs-hs-combined.csv` (HTTP 200 le 2026-11-12). Fichier brut enregistré
dans `tests-de-mort/F04-bis/donnees/` avec la date de téléchargement et le sha256. En-tête lu le 2026-11-12 : 35 colonnes,
séparateur virgule, marque d'ordre d'octets UTF-8 au début, fins de ligne CRLF. Colonnes utilisées :

| Colonne du fichier | Usage |
|---|---|
| `date` | date du taux |
| `nominal_hs_cmt_10yr`, `nominal_hs_cmt_20yr`, `nominal_hs_cmt_30yr` | taux à échéance constante, ancienne méthode (HS) |
| `nominal_mc_cmt_10yr`, `nominal_mc_cmt_20yr`, `nominal_mc_cmt_30yr` | taux à échéance constante, nouvelle méthode (MC) |

Les 28 autres colonnes (autres échéances nominales, taux réels) ne sont pas utilisées.

Ce qui n'est pas connu et que l'expérimentateur doit constater et écrire dans `ecarts.md` avant tout calcul :
- **Le format des dates.** Il doit donner des dates toutes comprises entre 2020-10-01 et 2021-09-30. Si deux lectures sont
  possibles (jour/mois ou mois/jour), on retient celle pour laquelle toutes les dates tombent dans cet intervalle ; si aucune
  ou plusieurs lectures conviennent, le fichier d'analyse n'est pas construit.
- **L'unité et le nombre de décimales.** Supposé : pour cent par an. Le contrôle 8 de la section 4 (égalité avec FRED) détecte
  une autre unité. Le nombre de décimales est noté : il compte pour lire le bruit (section 6).
- **Le nombre de dates.** Attendu : 251, le nombre de jours du calendrier C du premier test dans l'exercice. L'expérimentateur
  rapporte le nombre de dates du fichier et le nombre de jours de C absents du fichier.

**Règle d'échantillon.**
1. Départ : les lignes de A avec `type_ligne` = `reelle`, `principal` = 1 et `date_adjudication` entre 2020-10-01 et
   2021-09-30. Attendu : 24 lignes, soit 8 mois de réouverture (octobre et décembre 2020, janvier, mars, avril, juin, juillet
   et septembre 2021), trois échéances par mois.
2. `dans_exercice` = 1 si `date_jm5` ≥ 2020-10-01 et `date_jp5` ≤ 2021-09-30. Attendu : 23 lignes. La réouverture à 10 ans du
   2020-10-07 sort, car son J − 5 est le 2020-09-30, la veille du début du fichier.
3. Échantillon principal P : `dans_exercice` = 1, `complet` = 1, `fenetre_propre` = 1.

Dates d'adjudication attendues (à confirmer par le fichier A ; elles viennent du comptage du rédacteur) :

| Mois | 10 ans | 30 ans | 20 ans |
|---|---|---|---|
| 2020-10 | 2020-10-07 (hors exercice) | 2020-10-08 | 2020-10-21 |
| 2020-12 | 2020-12-09 | 2020-12-10 | 2020-12-21 |
| 2021-01 | 2021-01-12 | 2021-01-13 | 2021-01-20 |
| 2021-03 | 2021-03-10 | 2021-03-11 | 2021-03-16 |
| 2021-04 | 2021-04-12 | 2021-04-13 | 2021-04-21 |
| 2021-06 | 2021-06-09 | 2021-06-10 | 2021-06-15 |
| 2021-07 | 2021-07-12 | 2021-07-13 | 2021-07-21 |
| 2021-09 | 2021-09-08 | 2021-09-09 | 2021-09-21 |

**Ce qui compte comme manquant.**
- Une date de la fenêtre absente du fichier B, ou une cellule vide ou non numérique : le taux est manquant, `complet` = 0, la
  ligne est exclue des calculs et comptée.
- Aucune valeur n'est cherchée ailleurs. En particulier, on ne remplace pas un taux HS manquant par le taux FRED, et on
  n'utilise aucune date hors de l'exercice, même si le fichier B en contient.
- Fichier A ou B injoignable, ou colonnes de B différentes de celles listées ci-dessus : pas de source de remplacement, le
  fichier d'analyse n'est pas construit, le test est non concluant.
- Moins de 20 adjudications dans P, ou moins de 8 mois : non concluant (section 7).

## 4. Fichier d'analyse

Nom : `tests-de-mort/F04-bis/F04-bis_analyse.csv`. UTF-8 sans marque d'ordre d'octets, virgule, point décimal, une ligne
d'en-tête, champ vide pour une valeur manquante. Trié par `date_adjudication`, puis `echeance`.

**Une ligne par adjudication** : les 24 lignes de l'étape 1 de la règle d'échantillon. Pas de ligne placebo.

| Colonne | Type | Unité, contenu |
|---|---|---|
| `id_ligne` | texte | `id_ligne` de A, recopié ; unique |
| `cusip` | texte | recopié de A |
| `terme_api` | texte | recopié de A |
| `echeance` | entier | 10, 20 ou 30 (ans), recopié de A |
| `date_adjudication` | date AAAA-MM-JJ | recopié de A |
| `mois` | texte AAAA-MM | recopié de A |
| `date_j` | date | recopié de A |
| `date_jm5` | date | recopié de A |
| `date_jp5` | date | recopié de A |
| `cmt_jm5`, `cmt_j`, `cmt_jp5` | décimal | pour cent ; taux FRED du premier test, recopiés de A sans arrondi |
| `gsw_jm5`, `gsw_j`, `gsw_jp5` | décimal | pour cent ; courbe ajustée, recopiés de A sans arrondi |
| `hs_jm5`, `hs_j`, `hs_jp5` | décimal | pour cent ; colonne `nominal_hs_cmt_<echeance>yr` de B aux trois dates, recopiée telle qu'écrite |
| `mc_jm5`, `mc_j`, `mc_jp5` | décimal | pour cent ; colonne `nominal_mc_cmt_<echeance>yr` de B aux trois dates, recopiée telle qu'écrite |
| `dans_exercice` | entier | 1 si `date_jm5` ≥ 2020-10-01 et `date_jp5` ≤ 2021-09-30, sinon 0 |
| `complet` | entier | 1 si les douze taux sont présents, sinon 0 |
| `fenetre_propre` | entier | recopié de A |

Pour une date hors de l'exercice, `hs_*` et `mc_*` restent vides.

**Contrôles de schéma** (le vérificateur les exécute sur le fichier d'analyse et rapporte `schema_ok` = 1 si tous passent, 0 sinon) :
1. Les 24 colonnes ci-dessus, dans cet ordre, et aucune autre.
2. `id_ligne` unique ; `echeance` dans {10, 20, 30} ; `dans_exercice`, `complet`, `fenetre_propre` dans {0, 1}.
3. `date_jm5` < `date_j` < `date_jp5` ; `date_j` = `date_adjudication` ; `date_adjudication` entre 2020-10-01 et 2021-09-30 ;
   `mois` = ses sept premiers caractères.
4. `dans_exercice` = 1 si et seulement si `date_jm5` ≥ 2020-10-01 et `date_jp5` ≤ 2021-09-30.
5. `complet` = 1 si et seulement si les douze taux sont non vides.
6. Tout taux non vide est entre −1 et 20 ; pour chaque date, |`cmt` − `gsw`| ≤ 1 (comme dans F04).
7. Pour chaque date où `hs` et `mc` sont présents : |`hs` − `mc`| ≤ 0,25 point de pourcentage (garde contre une colonne mal
   appariée : un écart de 25 pb contredirait à lui seul l'écart-type d'au plus 1,0 pb annoncé par le Trésor). De plus, au
   moins une paire (`hs`, `mc`) du fichier diffère (garde contre deux fois la même colonne).
8. **Ancienne méthode = FRED.** Pour chaque date où `hs` et `cmt` sont présents : |`hs` − `cmt`| ≤ 0,0051 point de pourcentage
   (0,51 pb). Raison de la tolérance : FRED arrondit à 0,01 point ; un taux juste mais écrit avec plus de décimales s'en
   écarte d'au plus 0,5 pb ; 0,01 pb de marge couvre l'arithmétique flottante. Si le fichier B a deux décimales, l'égalité
   attendue est exacte. Un seul dépassement fait échouer le contrôle, donc rend le test non concluant : il voudrait dire que
   le fichier B ne redonne pas ce qui a été publié et utilisé par le premier test.
9. Exactement 24 lignes ; entre 20 et 24 lignes avec `dans_exercice` = 1 (attendu : 23 ; tout autre nombre est expliqué dans `ecarts.md`).

## 5. Statistique

**Mesures, pour une ligne i.** Avec x dans {J − 5, J, J + 5} :

- V_HS,i = 100 × [ 2·(`hs_j` − `gsw_j`) − (`hs_jm5` − `gsw_jm5`) − (`hs_jp5` − `gsw_jp5`) ], en points de base ;
- V_MC,i = même formule avec `mc_*` à la place de `hs_*` ;
- D_i = V_HS,i − V_MC,i = 100 × [ 2·(`hs_j` − `mc_j`) − (`hs_jm5` − `mc_jm5`) − (`hs_jp5` − `mc_jp5`) ].

C'est la formule de V du premier test, où le taux FRED est remplacé par le taux du fichier B. La courbe ajustée disparaît de
D : D ne dépend que de l'écart entre les deux méthodes aux trois dates. Les taux sont pris tels qu'écrits dans le fichier,
sans arrondi.

**Échantillon P** (section 3). N = nombre de lignes de P (`n_adjudications`). G = nombre de valeurs distinctes de `mois` dans
P (`n_grappes`).

**Statistique principale (une seule) : la moyenne de D, avec erreur type groupée par mois.**

- `d_moyen_pb` : D̄ = (1/N) Σ_i D_i.
- Pour chaque mois g : S_g = Σ_{i dans g} (D_i − D̄).
- `d_erreur_type_pb` : ET = (1/N) × racine( G/(G − 1) × Σ_g S_g² ). Même formule que F04, aucun autre facteur.
- `d_borne_inf_95_pb` : B_inf = D̄ − 2,365 × ET. `d_borne_sup_95_pb` : B_sup = D̄ + 2,365 × ET.
- `marge_zone_grise` : M = min( 0,9 − B_inf , B_sup − 0,9 ). M > 0 veut dire : l'intervalle à 95 % contient 0,9 pb.

**Les adjudications d'un même mois forment une seule grappe.** Raison : les réouvertures à 10 et 30 ans ont lieu deux jours
de suite, celle à 20 ans une à deux semaines après ; leurs fenêtres se recouvrent et partagent la même courbe. Les traiter
comme 23 observations indépendantes donnerait une erreur type trop petite. Avec trois adjudications par mois (deux en octobre
2020), ce calcul est, à très peu près, le test de Student sur les huit moyennes mensuelles de D.

**Pourquoi 2,365 et pas 1,96.** Avec 8 grappes, l'erreur type est elle-même mal connue. On prend la valeur critique de la loi
de Student à G − 1 = 7 degrés de liberté (2,365 pour 95 % bilatéral). Le minimum de 8 mois (section 7) garantit que G = 8, la
seule valeur possible puisqu'il n'y a que 8 mois de réouverture dans l'exercice. Pas de bootstrap, pas de tirage : le calcul
est déterministe.

**Estimations d'accompagnement** (dans `verification.json` ; seule la première sert de garde dans la règle) :
- `v_hs_moyen_pb` : moyenne simple de V_HS,i sur P.
- `v_mc_moyen_pb` : moyenne simple de V_MC,i sur P ; `v_mc_erreur_type_pb` : son erreur type, même formule groupée par mois.
- `ecart_max_hs_fred_pb` : 100 × le plus grand |`hs_x` − `cmt_x`| sur les lignes de P et les trois dates.

**Analyses secondaires, descriptives, sans effet sur le verdict** (au plus trois) :
- **S1. Par échéance.** Moyennes de D, V_HS et V_MC sur P pour 10, 20 et 30 ans (attendu : 7, 8 et 8 lignes), sans erreur type.
- **S2. D'où vient D.** Moyennes sur P de 100 × (`hs_x` − `mc_x`) pour x = J − 5, J et J + 5 ; et moyenne sur P du V du premier
  test, recalculé avec `cmt_*`, à lire à côté de `v_hs_moyen_pb`.
- **S3. Les jours ordinaires.** À partir du fichier brut B (l'expérimentateur seul ; le vérificateur ne peut pas le refaire
  depuis le fichier d'analyse) : pour chaque échéance, écart-type sur l'exercice de 100 × (HS − MC), à comparer aux 0,2 à
  1,0 pb du Trésor ; moyenne et écart-type de D(t) = 100 × [2·d(t) − d(t − 5) − d(t + 5)] sur toutes les dates t du fichier
  ayant cinq dates avant et cinq après, d étant HS − MC. Sert à voir si les jours d'adjudication sortent du lot.

L'expérimentateur rapporte aussi l'écart-type de D_i sur P (dénominateur N − 1), pour le comparer à la section suivante.

## 6. Arithmétique de puissance

Aucune ligne du fichier B n'a été lue : l'écart-type de D est une supposition, déclarée comme telle.

**Observations.** 23 adjudications attendues, dans 8 mois. Nombre d'observations réellement indépendantes : entre 8 (si les
adjudications d'un mois bougent ensemble) et 23.

**Pourquoi l'appariement aide.** V_MC seul est aussi bruité que V : écart-type d'environ 2,6 pb, donc une erreur type de 0,5 à
0,9 pb sur 23 adjudications. Ce n'est pas assez pour séparer 0 de 1,75 pb avec assurance. Dans D, le bruit du marché et celui
de la courbe ajustée s'annulent : il ne reste que le bruit de l'écart entre méthodes.

**Écart-type de D : fourchette plausible.**
- *Ce que dit le Trésor.* L'écart entre méthodes, pris un jour donné, a un écart-type σ de 0,2 à 1,0 pb selon l'échéance.
- *Pourquoi D peut être plus ou moins dispersé qu'un seul taux.* D combine trois dates avec les poids 2, −1, −1. Si l'écart
  entre méthodes était indépendant d'un jour à l'autre, l'écart-type de D serait σ × √6 ≈ 2,4 σ. S'il est persistant (il
  change peu en cinq jours), sa partie lente s'annule dans la différence et l'écart-type de D tombe sous σ : la formule est
  σ × √(6 − 8ρ₅ + 2ρ₁₀), où ρ₅ et ρ₁₀ sont les corrélations à 5 et 10 jours ; elle donne 1,6 σ pour ρ₅ = 0,5 et 0,6 σ pour
  ρ₅ = 0,9. D'où une fourchette de 0,1 à 2,4 pb.
- *L'arrondi.* Si le fichier B est arrondi à 0,01 point comme les taux publiés, l'arrondi seul ajoute jusqu'à 1,0 pb
  d'écart-type à D (0,41 pb par écart entre deux taux arrondis, fois √6), et D ne prend que des valeurs entières en pb.
- *Au total.* Écart-type de D entre 0,3 et 2,6 pb ; supposition centrale : 1,0 pb.

**Erreur type attendue de la moyenne de D.** Favorable : 0,3/√23 = 0,06 pb. Centrale : 1,0/√15 = 0,26 pb. Défavorable :
2,6/√8 = 0,92 pb.

Probabilité de chaque verdict (loi de Student non centrée à 7 degrés de liberté, gardes mises à part) :

| Erreur type | Vraie moyenne de D | survit | éliminée | non concluant |
|---|---|---|---|---|
| 0,06 (favorable) | 0 | 0 % | 100 % | 0 % |
| 0,06 | 1,75 | 100 % | 0 % | 0 % |
| 0,26 (central) | 0 | 0 % | 84 % | 16 % |
| 0,26 | 0,5 | 0 % | 27 % | 73 % |
| 0,26 | 0,9 (pile au seuil) | 2,5 % | 2,5 % | 95 % |
| 0,26 | 1,3 | 27 % | 0 % | 73 % |
| 0,26 | 1,75 | 80 % | 0 % | 20 % |
| 0,37 | 0 | 0 % | 55 % | 45 % |
| 0,37 | 1,75 | 51 % | 0 % | 49 % |
| 0,50 | 0 | 0 % | 34 % | 66 % |
| 0,50 | 1,75 | 31 % | 0 % | 69 % |
| 0,92 (défavorable) | 0 | 0 % | 13 % | 86 % |
| 0,92 | 1,75 | 12 % | 0 % | 87 % |

**Lecture.**
- Le test peut trancher entre les deux lectures pures (D proche de 0 ou proche de 1,75) environ quatre fois sur cinq si
  l'écart-type de D ne dépasse pas 1,0 pb environ, presque toujours s'il est sous 0,5 pb.
- Il ne peut pas trancher si l'écart-type de D dépasse environ 1,5 pb : il rend alors « non concluant » plus d'une fois sur deux.
- Il ne peut pas non plus trancher si la vérité est entre les deux (D entre 0,5 et 1,3 pb) : c'est voulu, une explication
  partielle n'est ni « la mesure explique » ni « la mesure n'explique pas ».
- Un verdict à tort (survie quand D est sous le seuil, élimination quand il est au-dessus) arrive au plus 2,5 % du temps.

**Ce que « non concluant » voudra dire.** Deux cas à distinguer dans la phrase de conclusion, d'après la demi-largeur de
l'intervalle, 2,365 × ET : si elle dépasse 0,45 pb, le test est trop imprécis pour dire quoi que ce soit ; si elle est
inférieure, le test est précis et la réponse est « en partie » (la mesure retire à peu près la moitié de la cassure).

Coût de calcul : un fichier de quelques dizaines de kilo-octets et 24 lignes ; moins d'une minute sur un portable.

## 7. Règle de verdict

Le verdict s'applique aux nombres du vérificateur. La règle est écrite pour que l'ordre d'évaluation ne change rien.

**En mots.**
- **Survit** = la mesure explique la cassure : tout l'intervalle à 95 % de la moyenne de D est au-dessus de 0,9 pb. Le
  changement de méthode retire, sur les mêmes adjudications, plus de la moitié de ce qui a disparu après 2021.
- **Éliminée** = la mesure n'explique pas la cassure : tout l'intervalle à 95 % est en dessous de 0,9 pb. Le changement de
  méthode retire moins de la moitié de la cassure.
- **Non concluant** = tout le reste : l'intervalle contient 0,9 pb, ou une garde ci-dessous se déclenche.

**Non concluant** si l'une de ces conditions tient :
- `schema_ok` < 1 (dont le contrôle 8 : ancienne méthode différente de FRED) ;
- `ecart_max_hs_fred_pb` > 0,51 (même contrôle, rapporté à part pour que la raison se lise dans `verdict.json`) ;
- `n_adjudications` < 20 ou `n_grappes` < 8 ;
- `v_hs_moyen_pb` < 0,9 ;
- `marge_zone_grise` > 0 ;
- (protocole) une donnée nommée manque, ou l'expérimentateur et le vérificateur diffèrent de plus que la tolérance.

**Survit** si toutes ces conditions tiennent : `d_borne_inf_95_pb` ≥ 0,9 ; `schema_ok` ≥ 1 ; `ecart_max_hs_fred_pb` ≤ 0,51 ;
`n_adjudications` ≥ 20 ; `n_grappes` ≥ 8 ; `v_hs_moyen_pb` ≥ 0,9.

**Éliminée** sinon, c'est-à-dire : gardes passées et `d_borne_sup_95_pb` ≤ 0,9.

**Justification de chaque seuil.**
- **0,9 pb.** La moitié de la cassure de 1,75 pb (section 2), arrondie au dixième. « Expliquer la cassure » est pris au sens
  ordinaire : en expliquer la plus grande part. Un seul seuil, au milieu des deux prédictions (0 et 1,75), traite les deux
  lectures de la même façon. Il est fixé d'après des chiffres déjà vus, pas d'après l'échantillon du test.
- **95 % et 2,365.** Niveau usuel ; valeur de Student à 7 degrés de liberté parce qu'il y a 8 grappes (section 5).
- **`v_hs_moyen_pb` ≥ 0,9.** Le test n'a de sens que si l'effet « d'avant » est présent dans l'échantillon. Si V_HS moyen était
  sous 0,9 pb, D ne pourrait dépasser 0,9 qu'avec un V_MC négatif : « éliminée » deviendrait presque automatique, ce qui
  favoriserait un résultat. D'après les années 2020 et 2021 déjà vues, cette garde devrait passer ; risque estimé qu'elle se
  déclenche : environ 5 %.
- **20 adjudications, 8 mois.** 23 attendues ; on tolère la perte de trois adjudications isolées (dates absentes du fichier
  B). On ne tolère pas la perte d'un mois entier : elle voudrait dire que le fichier B a un trou, et la valeur 2,365 suppose
  8 grappes.
- **0,51 pb pour l'égalité avec FRED.** Voir le contrôle 8 de la section 4.

**Tolérances entre expérimentateur et vérificateur.** 0,005 pb sur les moyennes, les erreurs types et `ecart_max_hs_fred_pb` ;
0,02 pb sur les deux bornes et sur la marge (elles contiennent 2,365 fois l'erreur type) ; 0 sur les comptes et sur
`schema_ok`. Les analyses S1 à S3 peuvent figurer dans `verification.json` sous une clé `descriptif` ; elles ne sont ni
comparées ni lues par le verdict.

## 8. Limites

1. **Une seule année.** Le test dit ce que le changement de méthode fait d'octobre 2020 à septembre 2021. Il ne montre pas ce
   qu'il fait de 2022 à 2026, où seule la nouvelle méthode existe. Passer de l'un à l'autre est un raisonnement, pas une mesure.
2. **Le fichier des deux méthodes n'est peut-être pas ce qui a été publié jour après jour.** Les taux MC de cet exercice ont
   été calculés pour la comparaison, avant la mise en service du 6 décembre 2021 ; rien ne garantit les mêmes entrées ni les
   mêmes réglages que ceux utilisés ensuite. Pour HS, le contrôle 8 vérifie l'égalité avec FRED ; pour MC, aucun contrôle
   n'est possible. C'est la limite la plus sérieuse.
3. **Une année particulière.** Achats massifs de la Réserve fédérale, forte hausse des taux longs au premier trimestre 2021,
   titre à 20 ans réintroduit en mai 2020 et mal placé sur la courbe. La courbe ajustée ne joue pas dans D, mais le niveau de
   V_HS et de V_MC cette année-là peut ne pas ressembler aux autres.
4. **Peu d'observations.** 23 adjudications, 8 mois. L'erreur type groupée est fragile avec 8 grappes ; la valeur 2,365 corrige
   en partie, sous l'hypothèse que les moyennes mensuelles sont à peu près normales. Si le fichier est arrondi à 0,01 point, D
   ne prend que des valeurs entières en pb et cette hypothèse est grossière.
5. **Un échantillon déjà en partie regardé.** V_HS sur ces adjudications est connu d'avance à peu de chose près ; seul D est
   neuf. Le seuil de 0,9 pb vient lui-même de la découpe exploratoire.
6. **« Survit » ne dit pas quelle méthode a raison.** Si la mesure explique la cassure, cela peut vouloir dire que l'ancienne
   méthode fabriquait le V, ou que la nouvelle l'efface. Le test ne les départage pas, et il ne propose aucun mécanisme.
7. **« Éliminée » ne prouve pas que le marché a changé.** Il resterait deux lectures : le marché, et le hasard d'une découpe
   par année choisie après avoir vu les données. Ce test ne dit rien de la seconde.
8. **Limites du premier test qui se transmettent.** V ne mesure que la pression propre au titre adjugé, pas la pression sur le
   niveau des taux ; seulement les réouvertures à 10, 20 et 30 ans ; le taux à échéance exacte est interpolé ; les deux
   sources ne sont pas relevées à la même heure ; la sélection des réouvertures dans l'API n'a pas été contrôlée.

## 9. Ce qu'on écrira dans chaque cas

- **Survit.** « Sur les 23 réouvertures de l'exercice 2021, calculer V avec la nouvelle méthode du Trésor plutôt qu'avec
  l'ancienne le fait baisser de X pb en moyenne (intervalle à 95 % : de Y à Z pb, au-dessus de 0,9 pb), de A pb avec
  l'ancienne méthode à B pb avec la nouvelle : le changement de méthode du 6 décembre 2021 explique plus de la moitié de la
  disparition de V après 2021, sans que ce test dise laquelle des deux méthodes mesure juste, ni ce qui se passe hors de
  cette année. »
- **Éliminée.** « Sur les mêmes réouvertures, passer de l'ancienne à la nouvelle méthode ne change V que de X pb en moyenne
  (intervalle à 95 % : de Y à Z pb, sous 0,9 pb), et V vaut encore B pb avec la nouvelle méthode : le changement de méthode
  n'explique pas la disparition de V après 2021 ; il reste un changement du marché ou le hasard d'une découpe choisie après
  coup, que ce test ne départage pas. »
- **Non concluant.** « Le test ne tranche pas, pour la raison suivante : [ancienne méthode du fichier différente des taux
  publiés / échantillon sous le minimum / schéma violé / V_HS moyen sous 0,9 pb / intervalle de Y à Z pb qui contient 0,9 pb,
  soit par imprécision, soit parce que la mesure explique environ la moitié / désaccord entre expérimentateur et
  vérificateur] ; on ne conclut ni que la mesure explique la cassure, ni qu'elle ne l'explique pas. »

## 10. Fichiers à produire après scellement

`ecarts.md` (format des dates, décimales, toute déviation), `donnees/` (fichier brut B et sha256), `F04-bis_analyse.csv`,
`temoin.json` (expérimentateur) et `verification.json` (vérificateur), tous deux avec les douze champs de la règle ci-dessous.

## 11. Choix à valider ou à changer avant de sceller

Ce sont les choix du rédacteur les plus discutables ; chacun se défend, aucun n'est imposé par les données.
1. **Un seuil unique à 0,9 pb.** Variante plus sévère : deux seuils (survit au-dessus de 1,3 pb, éliminée en dessous de
   0,45 pb), au prix de plus de « non concluant ».
2. **La garde `v_hs_moyen_pb` ≥ 0,9.** On peut la retirer si l'on préfère juger D seul.
3. **Un seul écart avec FRED suffit à rendre le test non concluant.** Variante : tolérer un nombre fixé de dépassements.
4. **Pas de ligne placebo**, pour garder une ligne par adjudication ; S3 en tient lieu, à titre descriptif.
5. **Les taux du fichier B pris sans arrondi**, même s'ils ont plus de décimales que les taux publiés.

## 12. Règle lisible par machine

```json
{
  "id": "F04-bis",
  "fichier_analyse": "F04-bis_analyse.csv",
  "champs_verification": [
    "schema_ok",
    "n_adjudications",
    "n_grappes",
    "ecart_max_hs_fred_pb",
    "d_moyen_pb",
    "d_erreur_type_pb",
    "d_borne_inf_95_pb",
    "d_borne_sup_95_pb",
    "marge_zone_grise",
    "v_hs_moyen_pb",
    "v_mc_moyen_pb",
    "v_mc_erreur_type_pb"
  ],
  "survit_si": [
    {"champ": "d_borne_inf_95_pb", "operateur": ">=", "seuil": 0.9},
    {"champ": "schema_ok", "operateur": ">=", "seuil": 1},
    {"champ": "ecart_max_hs_fred_pb", "operateur": "<=", "seuil": 0.51},
    {"champ": "n_adjudications", "operateur": ">=", "seuil": 20},
    {"champ": "n_grappes", "operateur": ">=", "seuil": 8},
    {"champ": "v_hs_moyen_pb", "operateur": ">=", "seuil": 0.9}
  ],
  "non_concluant_si": [
    {"champ": "schema_ok", "operateur": "<", "seuil": 1},
    {"champ": "ecart_max_hs_fred_pb", "operateur": ">", "seuil": 0.51},
    {"champ": "n_adjudications", "operateur": "<", "seuil": 20},
    {"champ": "n_grappes", "operateur": "<", "seuil": 8},
    {"champ": "v_hs_moyen_pb", "operateur": "<", "seuil": 0.9},
    {"champ": "marge_zone_grise", "operateur": ">", "seuil": 0}
  ],
  "tolerance": {
    "schema_ok": 0,
    "n_adjudications": 0,
    "n_grappes": 0,
    "ecart_max_hs_fred_pb": 0.005,
    "d_moyen_pb": 0.005,
    "d_erreur_type_pb": 0.005,
    "d_borne_inf_95_pb": 0.02,
    "d_borne_sup_95_pb": 0.02,
    "marge_zone_grise": 0.02,
    "v_hs_moyen_pb": 0.005,
    "v_mc_moyen_pb": 0.005,
    "v_mc_erreur_type_pb": 0.005
  }
}
```
