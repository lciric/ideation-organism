# M01 — Préinscription du test de mort : la pression d'adjudication a-t-elle disparu du marché après 2021, ou seulement de la courbe du Trésor ?

Rédigé le 2026-11-13 par le rédacteur de préinscription. Le rédacteur n'a lancé aucune analyse : aucun rendement, aucun écart
à une courbe, aucun V, aucune moyenne n'a été calculé sur des données. Ce qu'il a vu est listé en section 1.4. Ce texte est
figé une fois scellé (sha256) ; toute déviation ira dans `tests-de-mort/M01/ecarts.md`. Seul fichier joint :
`simulation_decision.py` (section 9), qui n'utilise aucune donnée.

**En une phrase.** Sur les mêmes réouvertures et les mêmes jours, on mesure la pression de deux façons : avec la courbe du
Trésor (V_cmt, la mesure de F04) et avec le prix de marché du titre rouvert lui-même (V_own, sans aucune courbe du Trésor). On
vérifie d'abord que V_own voit la pression en 2010-2021, où tout le monde s'accorde à dire qu'elle existait ; puis on regarde si,
après 2021, V_own a baissé comme V_cmt (le marché a changé) ou nettement moins (la mesure a changé).

## 1. Ce qui a déjà été vu

### 1.1 Les quatre tests scellés

| Test | Mesure | Chiffres du vérificateur | Verdict |
|---|---|---|---|
| F04 | V_cmt = 100·[2E(J) − E(J−5) − E(J+5)], E = taux à échéance constante du Trésor (FRED `DGS`) − rendement au pair de la courbe GSW de la Fed (`SVENPY`) ; 321 réouvertures à 10, 20 et 30 ans, 2010-01 à 2026-09 | moyenne 0,906 pb, ET groupée par mois 0,161 (134 mois), t = 5,6 ; placebo \|t\| = 0,27 | survit |
| F04-bis | même V sur les 23 réouvertures de l'exercice 2021, ancienne méthode du Trésor (HS) contre nouvelle (MC, en service le 6 décembre 2021) | D = V_HS − V_MC = 0,78 pb, ET 0,141, IC à 95 % [0,45 ; 1,12] (8 mois) ; V_HS = 1,64 ; V_MC = 0,85 (ET 0,32) ; écart HS/FRED : 0 | non concluant (l'IC contient 0,9) |
| J05 | K = concession au rendement limite de 13 h, nette de l'écart du même titre à la courbe GSW à J−5 (prix FedInvest) | K = 0,68 pb (206 réouvertures 2010-2021, 96 mois) et 1,10 pb (116, 39 mois) ; baisse −0,66, ET 0,373, IC à 90 % [−1,27 ; −0,04] | non concluant (contrôle n° 5 : garde « 7 à 9 jours civils » cassée par trois lundis qui suivent un lundi férié) ; sans ce contrôle, « éliminée » |
| K11 | V contre la moyenne de trois titres témoins de la même famille (2e à 4e ancien), prix FedInvest, aucune courbe | après 2021 : −0,01 pb, IC à 90 % [−0,11 ; 0,09] ; avant 2022 (10 et 30 ans) : −0,03 ; baisse −0,07 (borne basse −0,24) | non concluant (alerte d'instrument : mesure muette même avant 2022 ; contrôle n° 5 en échec sur 8 lignes hors statistique) |

Écart-type de V_cmt par adjudication dans F04 : 2,573 pb (dénominateur n − 1 ; `F04/ecarts.md`, E6). Facteur de groupement
de F04 : 0,1614 / (2,573/√321) = 1,12.

### 1.2 Découpes descriptives, faites après les verdicts

Sources : `projects/treasury-auction-pressure/results/RESULTS.md`, les cinq figures de `results/figures/`,
`F04/controle-orchestrateur.md`, les lectures après coup de J05 et K11.

- **F04 par période** : 1,375 pb en 2010-2021 (ET 0,125 ; 207 réouvertures ; 96 mois) ; 0,054 pb en 2022-2026 (ET 0,360 ;
  114 ; 38 mois) ; baisse 1,32 pb. Sous-périodes S3 : 1,056 (2010-2014), 1,122 (2015-01 à 2024-07), −0,132 (2024-08 à 2026-09) ;
  1,10 avant août 2024 et −0,13 depuis (contrôle de l'orchestrateur). Par échéance, toute la période : 10 ans 1,17 ; 20 ans
  −0,13 ; 30 ans 1,04. Environ 1,4 pb aux 10 et 30 ans avant 2022 (lecture après coup de K11).
- **F04 par année** : 2010 0,29 ; 2011 1,01 ; 2012 1,59 ; 2013 1,01 ; 2014 1,39 ; 2015 1,31 ; 2016 1,36 ; 2017 2,15 ;
  2018 1,37 ; 2019 1,04 ; 2020 1,92 ; 2021 1,72 ; puis, avec leurs IC à 95 % : 2022 0,30 [−1,10 ; 1,70] ; 2023 −0,03
  [−2,69 ; 2,64] ; 2024 0,23 [−0,74 ; 1,21] ; 2025 −0,54 [−1,41 ; 0,33] ; 2026 0,39 [−1,24 ; 2,01]. 2023 est de loin l'année
  la plus dispersée.
- **Figure 1 du projet** (trajet moyen de CMT − GSW autour de J, mesuré depuis J−5). Avant 2022, l'écart est presque plat
  jusqu'à J−1 (environ +0,2 pb), **saute à environ +0,77 pb le jour J**, retombe à environ +0,24 pb dès J+1 et reste vers +0,2
  jusqu'à J+10 : le V de F04 avant 2022 est presque entièrement un pic d'un jour, le jour de l'adjudication. Après 2021 :
  montée jusqu'à environ +0,55 pb à J−1, +0,34 à J, puis remontée vers +0,6 à +0,7 de J+4 à J+10 ; aucune forme en V ;
  intervalles larges.
- **F04-bis par échéance** : D = 0,71 / 0,75 / 0,87 pb (10 / 20 / 30 ans) ; V_HS = 1,95 / 1,48 / 1,52 ; V_MC = 1,23 / 0,73 /
  0,65. La nouvelle méthode retire 0,78 des 1,64 pb, soit 48 %.
- **J05** : sans les trois lundis, −0,71 [−1,33 ; −0,09] ; sans 2023, −0,04 [−0,55 ; 0,48] ; sans le 30 ans, −0,22
  [−0,94 ; 0,51] ; K moyen de 2023 : 3,34 pb ; valeur extrême : 30 ans du 2020-03-12, K = −25,9 pb. Analyses secondaires :
  concession en niveau, baisse 3,56 (ET 0,72) ; prime du titre à J−5, baisse 4,22 (ET 0,70) ; **R = montée de l'écart du
  titre à la courbe GSW entre J−5 et la clôture de J : « baisse » −0,64 pb (ET 0,28 ; IC à 90 % [−1,10 ; −0,18]), donc R a
  monté de 0,64 pb après 2021** ; A = K − R (décote et après-midi) : −0,02 (ET 0,27) ; variante à la formule exacte du
  Trésor : −0,68.
- **K11** : mesure de la fiche (rendement limite contre les témoins) 0,87 pb (ET 0,22) avant et 0,56 (ET 0,23) après ;
  montée 0,12 / 0,11 et redescente −0,15 / −0,12 contre les témoins ; V du premier ancien −0,08 / 0,02. Lecture : les témoins
  de la même famille bougent avec le titre rouvert.
- Figures 2 à 5 : les mêmes chiffres par année (F04 ; F04-bis apparié, 23 points ; K de J05 ; V de K11 avec F04 en référence).

### 1.3 Ce que cela implique pour M01, à dire franchement

1. **La moitié « montée » de V_own a déjà été vue, sous forme de différence entre périodes.** Le R de J05 est exactement
   E_own(J) − E_own(J−5) de M01 : même prix FedInvest, même courbe GSW évaluée aux mêmes flux, même règlement au jour même ;
   les J−5 de J05 (calendrier des dates GSW) sont ceux de M01, sauf peut-être pour les quelques fenêtres qui contiennent un
   Vendredi saint. On sait donc que cette montée n'a pas baissé après 2021 (+0,64 pb, ET 0,28). Ses niveaux par période
   n'ont pas été vus par le rédacteur (ils ne figurent dans aucun document lu). Ce qui est neuf dans M01 : la seconde jambe
   (de J à J+5), donc V_own entier ; le niveau de V_own avant 2022 (contrôle positif) ; l'appariement exact avec V_cmt sur le
   même calendrier.
2. **V_cmt est déjà connu à peu près** (environ 1,38 pb avant 2022, 0,05 après, sur un échantillon presque identique). Ce qui
   est inconnu, c'est V_own, donc l'écart entre les deux mesures.
3. **F04-bis place peut-être la vérité au milieu.** Si la méthode retire environ la moitié de V (48 % en 2021), la part
   « mesure » de la baisse d'après 2021 pourrait être proche de la moitié, là où toute règle à deux issues est la moins sûre
   (section 9).
4. Le pic d'un jour à J (figure 1) est ce que V_own doit retrouver dans les prix de marché pour que le contrôle positif passe.

### 1.4 Ce que le rédacteur a fait et vu pour écrire ce texte

- Lu en entier : `protocole.md`, `verdict.py` ; les préinscriptions, verdicts, contrôle de l'orchestrateur et lectures après
  coup de F04, F04-bis, J05 et K11 ; `README.md` et `results/RESULTS.md` du projet ; les cinq figures de `results/figures/`.
  Lu le code (pas les données) de `src/tap/calendar.py` et `src/tap/bonds.py`. Une ligne de `F04/ecarts.md` (l'écart-type
  2,573) s'est affichée lors d'une recherche.
- Téléchargé le 2026-11-13 les métadonnées d'adjudication D1 (section 5.1), **sans aucun champ de rendement ni de prix** :
  sélection, comptes, dates, coupons, échéances, calendrier.
- Téléchargé le 2026-11-13 douze pages FedInvest (section 5.2) et n'en a imprimé que des booléens (présence du titre,
  coupon, échéance, date affichée, prix > 0, prix dans [30 ; 200], prix multiple de 1/32, prix de J différent de ceux de J−5
  et de J+5). **Aucun prix ni aucun rendement n'a été affiché ou calculé.**
- N'a ouvert aucun fichier d'analyse (CSV), aucun jeu de données, aucun dossier `donnees/` ou `data/` ; n'a téléchargé ni
  le fichier GSW ni les séries FRED.
- Les seuls calculs chiffrés de ce texte sont ceux de la simulation (section 9), sur des chiffres déjà publiés.

## 2. Question, hypothèses rivales et prédictions chiffrées

**Question.** Aux réouvertures des titres nominaux à 10, 20 et 30 ans (2010-01 à 2026-10), la pression d'adjudication mesurée
sur le prix de marché du titre rouvert lui-même a-t-elle baissé après 2021 autant que celle mesurée avec la courbe à échéance
constante du Trésor ?

**Ce que le test fait.** Pour chaque réouverture, aux mêmes trois dates (J−5, J, J+5) :
- **V_own** : V de l'écart entre le rendement du titre rouvert (tiré de son prix FedInvest de fin de journée) et le rendement
  du même titre évalué sur la courbe GSW de la Fed ;
- **V_cmt** : V de l'écart entre le taux à échéance constante du Trésor et le rendement au pair GSW (la mesure de F04).
Les deux mesures ne diffèrent que par ce qu'on compare à GSW : le titre lui-même, ou la courbe du Trésor. Seule V_cmt dépend de
la méthode du Trésor. Le test est apparié : mêmes adjudications, mêmes jours, deux mesures.

**Les deux hypothèses rivales.**
- **« Mesure » (artefact de la courbe)** : la pression n'a pas baissé sur le marché ; la courbe du Trésor l'a perdue en
  changeant de méthode. V_own reste au même niveau après 2021 ; V_cmt baisse seul.
- **« Marché »** : la pression a baissé sur le marché ; la courbe du Trésor l'a seulement enregistré. V_own baisse autant que
  V_cmt.

**Hypothèse mise à mort.** « Mesure ». **Survit** = la disparition de la pression après 2021 est pour l'essentiel un artefact
de la courbe du Trésor ; **éliminée** = elle est pour l'essentiel un changement du marché.

**Prédictions chiffrées** (pb ; V_cmt fixé aux chiffres déjà vus ; D et m définis en 4.4 ; « baisse » = moyenne 2010-2021 −
moyenne 2022-2026) :

| Lecture | V_own 2010-2021 | V_own 2022-2026 | Baisse de V_cmt | Baisse de V_own | D | m |
|---|---|---|---|---|---|---|
| **Mesure** | ≈ 1,38 | ≈ 1,38 | ≈ 1,32 | ≈ 0 | ≈ −1,32 | ≈ −0,66 |
| **Marché** | ≈ 1,38 | ≈ 0,05 | ≈ 1,32 | ≈ 1,32 | ≈ 0 | ≈ +0,66 |
| Mixte, moitié | ≈ 1,38 | ≈ 0,72 | ≈ 1,32 | ≈ 0,66 | ≈ −0,66 | ≈ 0 |
| Mixte, F04-bis lu comme un effet additif de 0,78 | ≈ 1,38 | ≈ 0,83 | ≈ 1,32 | ≈ 0,54 | ≈ −0,78 | ≈ −0,12 |

La frontière de la règle (m = 0) passe à V_own après 2021 ≈ 1,38 − 0,66 = 0,72 pb.

**D'où viennent ces chiffres.**
- V_cmt : 1,375 et 0,054 pb (F04, découpe descriptive), baisse 1,32 pb.
- V_own avant 2022 ≈ V_cmt avant 2022 : avant décembre 2021, la courbe du Trésor passait par les cotations du titre le plus
  récemment adjugé, qui est ici le titre rouvert ; les deux mesures comparaient alors le même titre à la même courbe GSW.
  C'est l'hypothèse d'un instrument non atténué. La section 9 simule aussi un instrument atténué (0,85 pb avant 2022, le
  niveau de V_MC dans F04-bis).
- « Mesure » : V_own après = V_own avant. « Marché » : V_own après = V_cmt après.
- D = baisse de V_own − baisse de V_cmt (identité exacte, section 4.4).

**Avis du rédacteur, sans effet sur la règle.** La montée de V_own n'a pas baissé (R de J05 : +0,64 pb) et F04-bis montre que
la méthode retire la moitié de V en 2021 : « survit » paraît plus probable que « éliminée ». Deux choses peuvent le démentir :
la redescente (de J à J+5) peut avoir changé ; et le pic d'un jour de la figure 1 peut ne pas se retrouver dans les prix
FedInvest, auquel cas le contrôle positif échouera ou V_own sera atténué.

## 3. Pourquoi ce plan

| Ce qui a fait échouer ou douter | Réponse de M01 |
|---|---|
| K11 : les témoins de la même famille partagent la pression ; mesure muette même en 2010-2021 | Pas de témoins. Référence = la courbe GSW, lisse et ajustée sur les titres anciens de toutes les échéances ; F04 (1,38 pb) et J05 (0,68 pb) ont vu la pression contre elle avant 2022. **Contrôle positif obligatoire** sur 2010-2021. |
| J05 : rendement limite de 13 h mêlé à des prix de fin de journée (bruit de l'après-midi, écart de règlement) | Tout en fin de journée, mêmes dates, règlement au jour même ; aucun rendement d'adjudication. |
| J05 : garde « 7 à 9 jours civils » cassée par les lundis qui suivent un lundi férié | Aucun contrôle en jours civils. J±5 = 5 rangs dans le calendrier des jours ouvrés fédéraux, que le vérificateur reconstruit. |
| K11 : un contrôle de schéma portant sur des lignes hors statistique a rendu le test non concluant | Tous les contrôles ligne à ligne ne portent que sur les lignes de l'échantillon P ; les lignes exclues sont seulement comptées. |
| F04 et F04-bis : V_cmt dépend de la méthode du Trésor | V_own n'utilise du Trésor que les métadonnées d'adjudication et les prix FedInvest ; V_cmt est gardé pour l'appariement. |
| F04-bis, J05, K11 : précision insuffisante pour trancher | Statistique appariée ; règle construite pour départager les deux lectures et simulée avant scellement (section 9) : 0,89 et 0,88 au scénario de référence. |

## 4. Les mesures

### 4.1 V_own, sans courbe du Trésor

Pour la réouverture i (titre de coupon c, d'échéance M) et une date x ∈ {J−5, J, J+5} :
- f_i(x) = rendement du titre tiré de son prix FedInvest `END OF DAY` du jour x, pour règlement le jour x : f = Y(prix, x) ;
- g_i(x) = rendement du même titre évalué sur la courbe GSW du jour x : prix plein = somme des flux postérieurs à x actualisés
  par la courbe du jour x ; prix pied de coupon = prix plein − coupon couru à x ; g = Y(prix pied de coupon, x) ;
- E_own,i(x) = 100 × [f_i(x) − g_i(x)], en pb : de combien le titre rouvert est moins cher que la courbe des titres anciens ;
- **V_own,i = 2·E_own,i(J) − E_own,i(J−5) − E_own,i(J+5)** = montée [E(J) − E(J−5)] + redescente [E(J) − E(J+5)].

V_own > 0 : le titre se déprécie par rapport à la courbe avant l'adjudication et se rattrape après. Le niveau propre du titre
(prime du titre courant, effet de coupon) s'annule (poids 2 − 1 − 1 = 0), ainsi qu'une dérive linéaire de cette prime sur les
dix jours.

**Choix fixé : la courbe GSW évaluée aux mêmes flux, et non le rendement au pair GSW à l'échéance résiduelle exacte.**
1. Comparaison à l'identique : mêmes coupons, mêmes dates. Un titre de coupon 1,125 % qui cote 60 n'a pas le rendement d'un
   titre au pair de même échéance ; cet écart de coupon (plusieurs pb, qui varie avec le niveau et la pente des taux) s'annule
   exactement avec les mêmes flux, alors qu'avec le rendement au pair sa variation sur dix jours resterait dans V comme un
   bruit lié aux mouvements de la courbe.
2. Déjà mis en œuvre deux fois de façon indépendante dans J05 (écart entre expérimentateur et vérificateur : 6·10⁻¹¹ pb) ; la
   formule de la courbe redonne `SVENY` à 10⁻⁶ près (J05, section 5.2 ; tests du projet).
3. Le rendement au pair à une échéance fractionnaire demande de toute façon les paramètres de la courbe (`SVENPY` n'existe
   qu'aux années entières) : l'autre choix ne simplifierait rien.

**Convention de rendement** : celle de J05 et K11 (section 6.2, période fractionnaire composée). La variante exacte du
31 CFR 356 (intérêt simple sur la période fractionnaire) n'est pas retenue : la même fonction Y s'applique aux deux termes de
E, à la même date, et la différence de convention s'y retrouve presque à l'identique, donc s'annule à l'ordre un. Garder la
convention de J05 permet de réutiliser un code déjà vérifié deux fois.

**Règlement au jour même** pour f et g : la convention de règlement propre à FedInvest ne joue pas sur E (argument de J05).

### 4.2 V_cmt, la mesure de F04, aux mêmes dates

E_cmt,i(x) = 100 × [`DGS<m>`(x) − `SVENPY<m>`(x)], m = 10, 20 ou 30 selon l'échéance du titre ;
**V_cmt,i = 2·E_cmt,i(J) − E_cmt,i(J−5) − E_cmt,i(J+5)**. C'est la formule de F04. Seule différence : le calendrier (4.3).
Sur les fenêtres qui contiennent un jour sans `DGS10` mais présent dans C (18 fenêtres contiennent un Vendredi saint), J−5 ou
J+5 peut différer d'un jour de celui de F04 ; V_cmt est donc recalculé, jamais recopié de F04.

### 4.3 Calendrier C et dates J±5

C = jours du lundi au vendredi du 2009-06-01 au 2026-12-31, moins :
1. les jours fériés fédéraux observés (5 U.S.C. 6103) : 1er janvier, 3e lundi de janvier, 3e lundi de février, dernier lundi
   de mai, 19 juin (à partir de 2021), 4 juillet, 1er lundi de septembre, 2e lundi d'octobre, 11 novembre, 4e jeudi de
   novembre, 25 décembre ; un férié tombant un samedi est observé le vendredi précédent (le 1er janvier 2011 et le 1er janvier
   2022 sont donc observés les 2010-12-31 et 2021-12-31), un dimanche le lundi suivant ;
2. deux jours sans tableau FedInvest ni marché, vérifiés par K11 : **2012-10-30** et **2018-12-05**.

C'est le calendrier de K11. Mise en œuvre de référence : `projects/treasury-auction-pressure/src/tap/calendar.py`,
`k11_calendar()`, testée sur les trois lundis qui ont fait échouer J05.

J = `auction_date`. **J−5 = la date de C de rang rang(J) − 5 ; J+5 = la date de C de rang rang(J) + 5.** Aucune règle ni
aucun contrôle en jours civils.

Constaté sur les métadonnées (2026-11-13) : J ∈ C pour les 324 réouvertures ; aucune extrémité de fenêtre ne tombe un Vendredi
saint ; deux extrémités tombent une veille de Noël (J+5 des 20 ans du 2024-12-17 et du 2025-12-17 ; pages FedInvest remplies,
vérifié par K11). Pour information seulement, aucune règle n'en dépend : J − (J−5) vaut 7 jours civils (261 lignes), 8 (60) ou
10 (3 : 2016-09-12, 2021-07-12, 2022-09-12) ; (J+5) − J vaut 7 (272) ou 8 (52).

### 4.4 L'écart apparié, D et la marge m

Pour chaque ligne : écart_i = V_cmt,i − V_own,i et h_i = ½·V_cmt,i − V_own,i.
- **D = moyenne de l'écart en 2022-2026 − moyenne de l'écart en 2010-2021** : la statistique principale. Sur les mêmes lignes,
  D = baisse de V_own − baisse de V_cmt, exactement. « Mesure » prédit D ≈ −1,32 ; « marché » D ≈ 0.
- **m = D + ½ × baisse de V_cmt = baisse de V_own − ½ × baisse de V_cmt** (c'est aussi la moyenne de h après 2021 moins sa
  moyenne avant). m ≤ 0 : le prix du titre a perdu au plus la moitié de ce qu'a perdu la courbe du Trésor ; m > 0 : plus de la
  moitié. « Mesure » prédit m ≈ −0,66 ; « marché » m ≈ +0,66. m compare D au milieu des deux prédictions (−½ × baisse de V_cmt),
  calculé sur l'échantillon même du test plutôt que fixé d'après la découpe descriptive de F04.

### 4.5 Échantillon

**Population.** Les lignes nominales de D1 (`inflation_index_security` ≠ "Yes", `floating_rate` ≠ "Yes") avec `reopening` =
"Yes", `auction_date` du 2010-01-01 au 2026-10-31 et `security_term` commençant par « 9-Year » (échéance 10), « 19-Year » (20)
ou « 29-Year » (30). Constaté : **324 lignes** ; `avant` (J ≤ 2021-12-31) : 97 à 10 ans, 14 à 20 ans, 96 à 30 ans ; `apres` :
39, 39, 39.

**Exclusions, dans cet ordre de priorité** (colonne `motif_exclusion`) :
1. `fenetre_chevauchee` : une autre adjudication du même CUSIP dans D1 (émission d'origine ou réouverture) a lieu à 10 rangs
   de J ou moins dans C, si bien que les fenêtres [J−5 ; J+5] des deux adjudications se touchent. Constaté : **3 lignes** —
   2019-06-12 et 2019-06-21 (9128286T2, deux réouvertures à 7 rangs l'une de l'autre ; celle du 21, close à 11 h, est
   l'opération hors calendrier qu'excluent Fleming, Liu et Nguyen et K11) ; 2021-12-02 (912810TC2, à 10 rangs de son émission
   d'origine du 2021-11-17).
2. `titre_non_emis_a_jm5` : l'`issue_date` de la première adjudication du CUSIP est postérieure à J−5. Constaté : seulement
   2021-12-02, déjà exclue en 1.
3. `valeur_manquante` : une valeur d'entrée des colonnes 15 à 42 manque, ou `identite_fi_ok` = 0.

**Échantillon principal P** : `motif_exclusion` vide. Attendu : **321 lignes** — 204 avant (95 à 10 ans, 13 à 20 ans, 96 à
30 ans ; 96 mois) et 117 après (39, 39, 39 ; 39 mois), dont 24 en 2023 (8 mois). Sans 2023 : 93 lignes après (31 mois). Sans
le 30 ans : 108 avant (95 mois) et 78 après (39 mois).

Gardées : 2012-09-13 et 2012-12-12, closes à 11 h 30 (comme K11) ; les 8 réouvertures à 20 ans du 2020-06-17 au 2021-04-21,
que K11 perdait faute de témoins et qui n'en ont pas besoin ici.

## 5. Données

Toutes publiques, sans compte. L'expérimentateur enregistre chaque fichier brut (réponse de l'API, fichiers CSV, chaque page
HTML de FedInvest) dans `tests-de-mort/M01/donnees/`, avec la date de téléchargement et le sha256. Aucune source de
remplacement n'est permise. Note pratique tirée de `projects/treasury-auction-pressure/src/tap/data.py` : utiliser l'agent par
défaut de curl ; FRED renvoie parfois un corps vide (réessayer) ; federalreserve.gov refuse l'agent par défaut de Python.

### 5.1 D1. Adjudications (Fiscal Data, API v1)

Une requête, testée le 2026-11-13 (HTTP 200, 2 793 lignes, une page) :

```
https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?fields=cusip,auction_date,issue_date,maturity_date,security_type,security_term,original_security_term,reopening,inflation_index_security,floating_rate,closing_time_comp,int_rate&filter=security_type:in:(Note,Bond),auction_date:lte:2026-10-31&sort=auction_date&page%5Bsize%5D=10000
```

Valeur manquante : la chaîne `null`. Champs utilisés : `cusip`, `auction_date`, `issue_date`, `maturity_date`,
`security_term`, `reopening`, `inflation_index_security`, `floating_rate`, `int_rate` (`closing_time_comp` est seulement
recopié dans `ecarts.md` pour les trois lignes closes avant 13 h). La première adjudication d'un CUSIP est sa ligne nominale
avec `reopening` = "No". Constaté pour les 324 lignes : une et une seule première adjudication par CUSIP ; `int_rate` et
`maturity_date` égaux à ceux de la première adjudication ; toutes les échéances tombent le 15 du mois.

### 5.2 D2. Prix de fin de journée par titre (FedInvest, Bureau of the Fiscal Service)

Procédure (celle de K11, section 4.2, refaite le 2026-11-13), une date par session, client par défaut, pause d'une seconde :
1. `GET https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate` : HTTP 200 ; garder le témoin de session et le
   champ caché `_csrf` (96 caractères).
2. `POST` à la même adresse, corps `priceDate=AAAA-MM-JJ&submit=Show+Prices&_csrf=<jeton>`, avec le témoin : HTTP 302. Ne pas
   suivre la redirection automatiquement (403 avec `curl -L`, constaté par J05).
3. `GET https://www.treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail` avec le témoin : HTTP 200 ; page portant
   « Prices For: <Mois jour, année> » et un tableau d'en-tête exact `CUSIP, SECURITY TYPE, RATE, MATURITY DATE, CALL DATE, BUY,
   SELL, END OF DAY`.

Champs utilisés : `CUSIP` ; `SECURITY TYPE` (« MARKET BASED NOTE » ou « MARKET BASED BOND ») ; `RATE` (forme « 1.125% ») ;
`MATURITY DATE` (forme « MM/JJ/AAAA ») ; `END OF DAY` (prix pied de coupon pour 100 de nominal, vérifié par J05 autour du
coupon du 15 mai 2016). Une page dont la date affichée diffère de la date demandée, ou dont le tableau est vide, est traitée
comme absente.

Dates à télécharger : J−5, J et J+5 des 321 lignes non exclues par les métadonnées, soit **923 dates distinctes** du
2010-01-06 au 2026-10-28, dont 316 après 2021 (environ une heure, une seule fois).

**Pages vérifiées sur données réelles.**
- K11 (2026-11-12) : 80 dates, dont tous les cas limites de calendrier — trois lundis qui suivent un lundi férié, 2012-10-29
  et 30, 2018-12-04 et 05, fermetures budgétaires d'octobre 2013, de 2018-2019 et d'octobre 2025, veilles et lendemains de
  Noël 2020, 2024 et 2025, deuil national du 2025-01-09, Vendredis saints 2021 et 2023, Juneteenth 2021, Columbus Day 2025.
  Tableau vide le 2012-10-30, le 2016-09-05 (Labor Day) et le 2018-12-05 ; rempli partout ailleurs. 22 réouvertures vérifiées
  sur leurs trois dates (titre rouvert et témoins).
- Rédacteur de M01 (2026-11-13) : 12 pages pour des cas que K11 n'avait pas couverts.

| Titre | Réouverture J | Dates J−5, J, J+5 | Cas | Résultat |
|---|---|---|---|---|
| 912810SR0 (20 ans, 1,125 %, 2040-05-15) | 2020-06-17 | 2020-06-10, 06-17, 06-24 | première réouverture du 20 ans ; absente de K11 | 3/3 |
| 912810ST6 (20 ans, 1,375 %, 2040-11-15) | 2020-12-21 | 2020-12-14, 12-21, 12-29 | fenêtre qui contient la veille de Noël 2020 | 3/3 |
| 912810SW9 (20 ans, 1,875 %, 2041-02-15) | 2021-03-16 | 2021-03-09, 03-16, 03-23 | 20 ans de 2021 absent de K11 | 3/3 |
| 91282CRF0 (10 ans, 4,625 %, 2036-08-15) | 2026-10-07 | 2026-09-30, 10-07, 10-15 | fin d'échantillon ; la procédure fonctionne encore | 3/3 |

« 3/3 » : pour chacune des trois dates, HTTP 302 puis 200, jeton de 96 caractères, date affichée égale à la date demandée,
en-tête exact, 420 à 464 lignes de 8 colonnes, titre présent, type note ou obligation, `RATE` et `MATURITY DATE` égaux à D1,
`END OF DAY` > 0, compris dans [30 ; 200] et multiple exact de 1/32 ; prix de J différent de ceux de J−5 et de J+5.
L'arrondi au 1/32 vaut au plus 1/64 de point de prix, soit environ 0,2 pb de rendement à 10 ans par date (moins à 30 ans) :
de l'ordre de 0,1 à 0,3 pb d'écart-type sur V, petit devant 2,6 pb.

### 5.3 D3. Courbe GSW (Réserve fédérale)

`https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` (16,7 Mo, utilisé par F04 et J05). Neuf lignes de
préambule ; en-tête à la ligne 10, commençant par `Date`. Colonnes utilisées : `Date`, `BETA0`, `BETA1`, `BETA2`, `BETA3`,
`TAU1`, `TAU2` (pour V_own) et `SVENPY10`, `SVENPY20`, `SVENPY30` (pour V_cmt, pour cent). Valeur manquante : `NA`. Une date x
sans ligne dans le fichier : valeurs manquantes.

### 5.4 D4. Taux à échéance constante du Trésor (FRED)

`https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10`, puis `?id=DGS20` et `?id=DGS30` (utilisés par F04). Colonnes
`observation_date,DGS<m>`, pour cent, deux décimales ; champ vide = manquant.

**Disponibilité de D3 et D4 aux dates de M01 : non vérifiée par le rédacteur**, qui ne devait télécharger que D1 et quelques
pages FedInvest. Ce qui est connu : F04 a obtenu ses six valeurs pour 321 réouvertures (calendrier de `DGS10`) ; J05 a obtenu
les paramètres GSW à J et J−5 pour ses 322 lignes ; les extrémités de fenêtre de M01 sont toutes des jours ouvrés ordinaires
(aucune n'est un Vendredi saint, un jour férié ou un jour de fermeture du marché). Une valeur absente rend la ligne
`valeur_manquante` ; elle est comptée, et les minimums de la section 10 tolèrent environ 10 % de pertes.

## 6. Fichier d'analyse

Nom : `tests-de-mort/M01/M01_analyse.csv`. UTF-8 sans marque d'ordre d'octets, virgule, point décimal, une ligne d'en-tête,
champ vide pour une valeur manquante ; nombres calculés écrits sans arrondi (au moins 10 chiffres significatifs), valeurs
recopiées telles qu'écrites dans leur source. **Une ligne par réouverture de la population de 4.5 (324 attendues)**, triée par
`date_adjudication` puis `echeance`. Aucune autre ligne.

### 6.1 Colonnes

| N° | Colonne | Type | Unité, contenu |
|---|---|---|---|
| 1 | `id_ligne` | texte | `<cusip>_<date_adjudication>`, unique |
| 2 | `cusip` | texte | 9 caractères, `cusip` de D1 |
| 3 | `terme_api` | texte | `security_term` de D1, recopié |
| 4 | `echeance` | entier | 10, 20 ou 30 selon que `terme_api` commence par « 9-Year », « 19-Year » ou « 29-Year » |
| 5 | `date_adjudication` | date AAAA-MM-JJ | `auction_date` (= J) |
| 6 | `mois` | texte AAAA-MM | sept premiers caractères de J |
| 7 | `annee` | entier | année de J |
| 8 | `periode` | texte | `avant` si J ≤ 2021-12-31, sinon `apres` |
| 9 | `date_emission_origine` | date | `issue_date` de la première adjudication du CUSIP |
| 10 | `date_echeance` | date | `maturity_date` |
| 11 | `taux_coupon_pct` | décimal | `int_rate`, pour cent par an |
| 12 | `date_jm5` | date | C[rang(J) − 5] |
| 13 | `date_jp5` | date | C[rang(J) + 5] |
| 14 | `motif_exclusion` | texte | vide, `fenetre_chevauchee`, `titre_non_emis_a_jm5` ou `valeur_manquante` (4.5) |
| 15-17 | `prix_fi_jm5`, `prix_fi_j`, `prix_fi_jp5` | décimal | `END OF DAY` du CUSIP à J−5, J, J+5, pour 100 |
| 18 | `identite_fi_ok` | entier | 1 si, aux trois dates, la page porte la date demandée, le CUSIP y figure, `SECURITY TYPE` est une note ou une obligation, `RATE` et `MATURITY DATE` égalent les colonnes 11 et 10, et `END OF DAY` > 0 ; sinon 0 |
| 19-24 | `beta0_jm5`, `beta1_jm5`, `beta2_jm5`, `beta3_jm5`, `tau1_jm5`, `tau2_jm5` | décimal | paramètres de la ligne de D3 dont `Date` = `date_jm5`, recopiés |
| 25-30 | `beta0_j`, `beta1_j`, `beta2_j`, `beta3_j`, `tau1_j`, `tau2_j` | décimal | paramètres D3 à J |
| 31-36 | `beta0_jp5`, `beta1_jp5`, `beta2_jp5`, `beta3_jp5`, `tau1_jp5`, `tau2_jp5` | décimal | paramètres D3 à J+5 |
| 37-39 | `cmt_jm5`, `cmt_j`, `cmt_jp5` | décimal | `DGS<echeance>` de D4 aux trois dates, pour cent, recopié |
| 40-42 | `gswpar_jm5`, `gswpar_j`, `gswpar_jp5` | décimal | `SVENPY<echeance>` de D3 aux trois dates, pour cent, recopié |
| 43-45 | `rdt_fi_jm5_pct`, `rdt_fi_j_pct`, `rdt_fi_jp5_pct` | décimal | f(x) = Y(prix FedInvest, x), pour cent (6.2) |
| 46-48 | `rdt_gsw_jm5_pct`, `rdt_gsw_j_pct`, `rdt_gsw_jp5_pct` | décimal | g(x), pour cent (6.2) |
| 49-51 | `e_own_jm5_pb`, `e_own_j_pb`, `e_own_jp5_pb` | décimal | 100 × (`rdt_fi_x_pct` − `rdt_gsw_x_pct`), pb |
| 52-54 | `e_cmt_jm5_pb`, `e_cmt_j_pb`, `e_cmt_jp5_pb` | décimal | 100 × (`cmt_x` − `gswpar_x`), pb |
| 55 | `v_own_pb` | décimal | 2 × `e_own_j_pb` − `e_own_jm5_pb` − `e_own_jp5_pb`, pb |
| 56 | `v_cmt_pb` | décimal | 2 × `e_cmt_j_pb` − `e_cmt_jm5_pb` − `e_cmt_jp5_pb`, pb |
| 57 | `ecart_pb` | décimal | `v_cmt_pb` − `v_own_pb`, pb |
| 58 | `complet` | entier | 1 si les colonnes 15 à 42 sont toutes remplies et `identite_fi_ok` = 1 ; sinon 0 |
| 59 | `dans_p` | entier | 1 si `motif_exclusion` est vide ; sinon 0 |

Une valeur dérivée (colonnes 43 à 57) est vide si l'une de ses entrées l'est. Pour les lignes exclues par les métadonnées
(deux premiers motifs), les colonnes 15 à 57 peuvent rester vides. `motif_exclusion` vaut `valeur_manquante` si et seulement si
`complet` = 0 et qu'aucun motif antérieur ne s'applique.

### 6.2 Conventions de calcul (identiques pour l'expérimentateur et le vérificateur ; reprises de J05, section 5.2)

Notations : c = `taux_coupon_pct` ; M = `date_echeance` ; d = date de règlement ; durées en jours civils.
- **Dates de coupon** : T_k = M reculée de 6·k mois (k = 0, 1, 2, …), même jour du mois (dernier jour du mois si ce jour
  n'existe pas) ; dates nominales, sans report au jour ouvré.
- **Flux après d** : c/2 à chaque T_k strictement postérieur à d, plus 100 à M. Un coupon qui tombe le jour d n'est pas reçu.
- **Coupon couru** : L(d) = dernier T_k ≤ d ; N(d) = premier T_k > d ; AI(d) = (c/2) × (d − L)/(N − L).
- **Rendement d'un prix pied de coupon P pour règlement d**, Y(P, d) : y, en pour cent, est l'unique solution de
  P + AI(d) = Σ_{j=1..n} F_j × (1 + y/200)^−[(j − 1) + (N − d)/(N − L)], où n est le nombre de T_k > d, F_j = c/2 pour j < n et
  c/2 + 100 pour j = n ; résolution numérique à 10⁻⁹ point de pourcentage près.
- **Courbe GSW du jour x** : pour m > 0 (années),
  z_x(m) = β0 + β1·(1 − e^(−m/τ1))/(m/τ1) + β2·[(1 − e^(−m/τ1))/(m/τ1) − e^(−m/τ1)] + β3·[(1 − e^(−m/τ2))/(m/τ2) − e^(−m/τ2)],
  en pour cent, composition continue ; facteur d'actualisation D_x(m) = exp(−z_x(m)·m/100), avec m = (date du flux − x)/365,25.
- **g(x)** (colonnes 46-48) : prix plein = Σ des flux postérieurs à x × D_x(m_flux) ; P = prix plein − AI(x) ; g(x) = Y(P, x).
- **f(x)** (colonnes 43-45) : Y(`END OF DAY` du jour x, x).

## 7. Contrôles de schéma

Le vérificateur les exécute et rapporte `schema_ok` = 1 si tous passent, 0 sinon. **Les contrôles 1 et 2 portent sur le
fichier (son format, la liste de ses lignes) ; tous les autres ne portent que sur les lignes `dans_p` = 1, c'est-à-dire celles
qui entrent dans un calcul.** Aucune ligne exclue n'est contrôlée : ses motifs sont seulement comptés (section 8, S4). Aucun
contrôle n'utilise un nombre de jours civils.

| N° | Contrôle | Porte sur | Vérifié sur données réelles |
|---|---|---|---|
| 1 | Les 59 colonnes de 6.1, dans cet ordre, et aucune autre | fichier | — (format) |
| 2 | `id_ligne` unique ; l'ensemble des `id_ligne` est exactement l'ensemble des réouvertures de la population de 4.5, que le vérificateur reconstruit à partir de D1 (une requête) | fichier | D1 du 2026-11-13 : 324 lignes (97, 14, 96 ; 39, 39, 39) |
| 3 | `id_ligne` = `<cusip>_<date_adjudication>` ; `cusip` de 9 caractères ; `echeance` conforme au préfixe de `terme_api` ; `mois`, `annee` et `periode` conformes à J ; `taux_coupon_pct`, `date_echeance` et `date_emission_origine` égaux à ceux de la première adjudication du CUSIP dans D1 ; `complet` = 1 ; colonnes 18, 58 et 59 dans {0, 1} | P | D1 : une première adjudication par CUSIP, coupon et échéance identiques pour les 324 lignes |
| 4 | **Calendrier, au rang** : J ∈ C ; `date_jm5` = C[rang(J) − 5] et `date_jp5` = C[rang(J) + 5], C reconstruit par le vérificateur selon 4.3 | P | les 324 lignes (J ∈ C partout) ; pages réelles des cas limites (5.2), dont les trois lundis qui ont fait échouer J05, 2018-12-12 (J−5 = 2018-12-04, le 05 étant retiré de C), Juneteenth 2021 et les veilles de Noël |
| 5 | Aucune autre adjudication du même CUSIP dans D1 à 10 rangs de J ou moins dans C ; `date_emission_origine` ≤ `date_jm5` | P | D1 : exactement 3 lignes violent la première condition et 1 la seconde (4.5) ; elles portent un motif, donc ne sont pas dans P |
| 6 | `identite_fi_ok` = 1 | P | 12 consultations du rédacteur de M01 et 264 de K11 (22 réouvertures × 4 titres × 3 dates) : toutes conformes là où la page existe |
| 7 | Plages : prix (colonnes 15-17) dans [30 ; 200] ; `tau1_*` et `tau2_*` > 0 ; `cmt_*`, `gswpar_*` et `rdt_*` dans [−1 ; 20] ; `taux_coupon_pct` dans [0 ; 15] | P | prix : 12 consultations du rédacteur et 24 réouvertures à J−5 (K11, booléens) ; `DGS` et `SVENPY` : 1 926 valeurs de F04 (son contrôle 7, passé) |
| 8 | Garde contre un mauvais appariement, aux trois dates : \|`rdt_fi_x_pct` − `rdt_gsw_x_pct`\| ≤ 0,60 et \|`cmt_x` − `gswpar_x`\| ≤ 1 (points de pourcentage) | P | première partie : à J−5 sur les 322 lignes de J05 (son contrôle 7, passé) ; seconde partie : 1 926 valeurs de F04 (son contrôle 7, passé). À J et J+5, la première partie n'a pas été vérifiée par le rédacteur (il aurait fallu calculer des écarts de rendement) ; l'écart d'un même titre à la courbe bouge de quelques pb en cinq jours (écart-type de V : 2,6 pb), loin de 60 pb |
| 9 | Colonnes 49 à 57 égales à leur formule appliquée aux colonnes du fichier, à 10⁻⁶ pb près ; colonnes 15 à 42 toutes remplies | P | — (arithmétique) |

Le recalcul indépendant des rendements (colonnes 43 à 48) n'est pas un contrôle de schéma : c'est le champ `ecart_max_rdt_pb`
(section 8), qui a son propre seuil.

## 8. Statistiques

**Notations.** A = lignes de P avec `periode` = `avant` ; B = lignes de P avec `periode` = `apres`. Pour un ensemble S de N
lignes réparties en G mois (colonne `mois`) et une colonne x :
- moyenne : x̄_S = (1/N) Σ x_i ;
- erreur type groupée par mois : ET_S(x) = (1/N) × racine[ G/(G − 1) × Σ_g ( Σ_{i ∈ S, mois g} (x_i − x̄_S) )² ] (formule de
  F04, aucun autre facteur de correction).

Pour une différence entre B et A, qui n'ont aucun mois commun : ET = racine(ET_A² + ET_B²). Borne basse à 90 % = estimation −
1,645 × ET ; borne haute = estimation + 1,645 × ET (1,645 exactement). Pas de bootstrap, pas de tirage : le calcul est
déterministe.

**Recalcul.** Le vérificateur recalcule avec son propre code, selon 6.2, les six rendements (colonnes 43 à 48) de chaque ligne
de P à partir des prix, paramètres, coupons, échéances et dates du fichier, puis E, V et l'écart. Il rapporte
`ecart_max_rdt_pb` = 100 × le plus grand écart absolu entre ses rendements et ceux du fichier. L'expérimentateur rapporte le
même champ avec un second code à lui (attendu : 0). Chacun calcule ensuite toutes les statistiques avec ses propres valeurs,
sur l'échantillon P défini par les colonnes du fichier.

**Champs de la règle** (en pb, sauf les comptes et les indicateurs) :

| Champ | Définition |
|---|---|
| `n_avant`, `n_apres` | nombre de lignes de A, de B |
| `n_grappes_avant`, `n_grappes_apres` | nombre de mois distincts de A, de B |
| `v_own_avant_pb`, `et_v_own_avant_pb` | moyenne et ET de `v_own_pb` sur A |
| `borne_inf_90_v_own_avant_pb` | `v_own_avant_pb` − 1,645 × `et_v_own_avant_pb` |
| `controle_positif_ok` | 1 si `borne_inf_90_v_own_avant_pb` > 0, sinon 0 |
| `v_cmt_avant_pb`, `v_cmt_apres_pb` | moyenne de `v_cmt_pb` sur A, sur B |
| `baisse_cmt_pb`, `et_baisse_cmt_pb` | `v_cmt_avant_pb` − `v_cmt_apres_pb` ; racine(ET_A(v_cmt)² + ET_B(v_cmt)²) |
| `borne_inf_90_baisse_cmt_pb` | `baisse_cmt_pb` − 1,645 × `et_baisse_cmt_pb` |
| `controle_cassure_ok` | 1 si `borne_inf_90_baisse_cmt_pb` > 0, sinon 0 |
| `v_own_apres_pb`, `et_v_own_apres_pb` | moyenne et ET de `v_own_pb` sur B |
| `borne_inf_90_v_own_apres_pb` | `v_own_apres_pb` − 1,645 × `et_v_own_apres_pb` |
| `baisse_own_pb`, `et_baisse_own_pb` | `v_own_avant_pb` − `v_own_apres_pb` ; racine(ET_A(v_own)² + ET_B(v_own)²) |
| `borne_inf_90_baisse_own_pb` | `baisse_own_pb` − 1,645 × `et_baisse_own_pb` |
| `d_pb`, `et_d_pb` | **statistique principale D** : moyenne de `ecart_pb` sur B − moyenne sur A ; racine(ET_A(écart)² + ET_B(écart)²) |
| `borne_inf_90_d_pb`, `borne_sup_90_d_pb` | `d_pb` − 1,645 × `et_d_pb` ; `d_pb` + 1,645 × `et_d_pb` |
| `marge_moitie_pb` | m = `d_pb` + 0,5 × `baisse_cmt_pb` |
| `et_marge_moitie_pb` | racine(ET_A(h)² + ET_B(h)²), avec h = 0,5 × `v_cmt_pb` − `v_own_pb` |
| `marge_moitie_sans_2023_pb` | m recalculé (D et baisse de V_cmt) sur P privé des lignes d'`annee` = 2023 |
| `marge_moitie_sans_30_pb` | m recalculé sur P privé des lignes d'`echeance` = 30 |
| `indecis` | 0 si le profil (S) ou le profil (E) ci-dessous tient, 1 sinon |

- **(S) profil « mesure »** : `borne_inf_90_v_own_apres_pb` > 0 et `marge_moitie_pb` ≤ 0 et `marge_moitie_sans_2023_pb` ≤ 0
  et `marge_moitie_sans_30_pb` ≤ 0.
- **(E) profil « marché »** : `borne_inf_90_baisse_own_pb` > 0 et `marge_moitie_pb` > 0 et `marge_moitie_sans_2023_pb` > 0
  et `marge_moitie_sans_30_pb` > 0.

(S) et (E) s'excluent (signe de m). Contrôle arithmétique pour les deux rôles : `d_pb` = `baisse_own_pb` − `baisse_cmt_pb` à
10⁻⁹ près.

**Pourquoi le groupement par mois** : les réouvertures à 10 et 30 ans ont lieu deux jours de suite et celle à 20 ans la semaine
suivante ; leurs fenêtres se chevauchent et partagent la même courbe et les mêmes nouvelles. **Pourquoi l'appariement** :
l'écart est calculé ligne par ligne ; ce qui touche les deux mesures le même jour (erreur d'ajustement de la courbe GSW,
journées extrêmes comme mars 2020 ou mars 2023) s'annule dans l'écart, et son ET en tient compte sans hypothèse.

**Analyses secondaires, descriptives, sans effet sur le verdict** (dans `verification.json` sous la clé `descriptif` ; ni
comparées ni lues par le verdict) :
- **S1. Par échéance** : moyennes et ET de V_own et de V_cmt sur A et sur B, D et m, pour 10, 20 et 30 ans séparément.
- **S2. Les deux jambes** : montée (`e_own_j_pb` − `e_own_jm5_pb`) et redescente (`e_own_j_pb` − `e_own_jp5_pb`) de V_own, et
  les mêmes pour V_cmt, moyennes et ET sur A et B. La montée de V_own est le R de J05, à lire à côté de sa baisse de −0,64 pb.
- **S3. Par année** : moyennes et ET de V_own et V_cmt par année ; m sans 2023 **et** sans le 30 ans à la fois.
- **S4. Hypothèses de la simulation et comptes** : écart-type (dénominateur n − 1) de V_own et de V_cmt sur A, sur B et sur
  2023 ; corrélation de V_own et V_cmt sur A et sur B ; nombre de lignes exclues par motif ; nombre de lignes de P dont le prix
  FedInvest est identique à deux des trois dates.

## 9. Simulation de la décisivité (faite avant scellement, sans données)

**But.** Vérifier que la règle de la section 10 rend le bon verdict au moins 8 fois sur 10 sous chacune des deux hypothèses
rivales, à la taille qu'elles prédisent, avec des dispersions tirées de chiffres déjà scellés ou publiés.

**Code.** `tests-de-mort/M01/simulation_decision.py` (Python 3 et numpy). Graine 20261113 ; 5 000 tirages par cas ; environ une
minute ; commande `python3 simulation_decision.py`. Il ne lit aucun fichier.

**Entrées, toutes déjà vues (section 1).** Écart-type de V par adjudication : 2,573 pb ; ET groupée : 0,16135 (F04 : N = 321,
134 mois). V_cmt : 1,375 pb avant 2022 (ET 0,125 ; 207 ; 96 mois) et 0,054 après (ET 0,360 ; 114 ; 38 mois). Intervalles annuels
de F04 de 2022 à 2026. Comptes de J05 : 206 réouvertures avant 2022 en 96 mois, 116 après en 39 mois ; 24 en 2023 en 8 mois
(K11). ET de la baisse de R dans J05 : 0,280.

**Modèle.**
1. *Plan d'échantillon* : avant 2022, 96 mois comptant chacun une réouverture à 10 ans et une à 30 ans (8 mois par an de 2010
   à 2021), une réouverture à 10 ans de plus en 2019, et des 20 ans dans les 13 derniers mois (206 lignes) ; après 2021, 39 mois
   (8 par an de 2022 à 2025, 7 en 2026) à trois échéances, moins un 20 ans le dernier mois (116 lignes).
2. *Tirage* : pour la ligne i du mois g, V_cmt,i = μ_cmt(période) + σ_c,i × [√ICC · a_g + √(1 − ICC) · e_i] et
   V_own,i = μ_own(période) + σ_o,i × [√ICC · b_g + √(1 − ICC) · f_i], où a, b, e, f sont des normales centrées réduites avec
   corr(a_g, b_g) = corr(e_i, f_i) = ρ. ICC = 0,188 est la corrélation intra-mois qui redonne le facteur de groupement de F04 :
   (0,16135 / (2,573/√321))² = 1 + (321/134 − 1) × ICC.
3. *Statistiques et règle* : exactement celles des sections 8 et 10 (moyennes, ET groupées par mois avec le facteur G/(G − 1),
   bornes à 1,645, m sur l'échantillon entier, sans 2023 et sans le 30 ans, contrôles positif et de cassure), gardes de données
   mises à part (échantillon complet, schéma valide).
4. *Vérités simulées* : μ_cmt = 1,375 avant et 0,054 après dans tous les cas. **Mesure** : μ_own = 1,375 avant et après.
   **Marché** : μ_own = 1,375 avant et 0,054 après. Cas intermédiaires : « mixte, moitié » (μ_own après = 0,715) ; « mixte,
   F04-bis additif » (μ_own après = 0,054 + 0,78) ; instrument atténué (μ_own avant = 0,85, le niveau de V_MC dans F04-bis),
   avec μ_own après = 0,85 (mesure) ou 0,054 (marché).
5. *Scénarios de dispersion* :
   - **A, scénario de référence** (celui de la consigne) : σ = 2,573 pb pour les deux mesures et les deux périodes ; ρ = 0,
     c'est-à-dire aucun bruit commun aux deux mesures. C'est l'hypothèse la plus défavorable plausible : les deux mesures
     retranchent la même courbe GSW, ce qui crée une corrélation positive. A' : ρ = 0,5.
   - **B, hétéroscédastique** : σ tiré des ET groupées déjà vues, ramenées à une adjudication par division par
     √(1 + (taille du mois − 1) × ICC) : 1,63 pb avant 2022 ; 2,50 pb après 2021 hors 2023 (années 2022, 2024, 2025 et 2026 de
     F04) ; 5,68 pb en 2023. ρ = 0 ; B' : ρ = 0,5.
   - **C, stress** : B avec V_own 1,18 fois plus dispersé que V_cmt. 1,18 = écart-type efficace de V_own déduit de R dans J05
     (0,280/√(1/206 + 1/116) × √2 = 3,41 pb, V ayant deux jambes) divisé par celui de V_cmt dans F04 (0,16135 × √321 = 2,89).
     ρ = 0 ; C' : ρ = 0,5.

**Résultats** (fréquence de chaque verdict sur 5 000 tirages) :

| Scénario | Vérité simulée | survit | éliminée | non concluant |
|---|---|---|---|---|
| **A (référence)** | **mesure** | **0,894** | 0,016 | 0,089 |
| **A (référence)** | **marché** | 0,015 | **0,884** | 0,101 |
| A | mixte, moitié | 0,351 | 0,359 | 0,290 |
| A | mixte, F04-bis additif | 0,469 | 0,243 | 0,288 |
| A | mesure, instrument atténué | 0,844 | 0,016 | 0,139 |
| A | marché, instrument atténué | 0,059 | 0,491 | 0,450 |
| A' (ρ = 0,5) | mesure | 0,949 | 0,005 | 0,046 |
| A' (ρ = 0,5) | marché | 0,006 | 0,945 | 0,049 |
| B | mesure | 0,842 | 0,009 | 0,148 |
| B | marché | 0,011 | 0,821 | 0,167 |
| B' (ρ = 0,5) | mesure | 0,889 | 0,001 | 0,110 |
| B' (ρ = 0,5) | marché | 0,003 | 0,885 | 0,112 |
| C | mesure | 0,786 | 0,016 | 0,198 |
| C | marché | 0,018 | 0,761 | 0,221 |
| C' (ρ = 0,5) | mesure | 0,825 | 0,006 | 0,169 |
| C' (ρ = 0,5) | marché | 0,008 | 0,824 | 0,168 |

Avec les comptes attendus de M01 (204 et 117 au lieu de 206 et 116), scénario A : 0,898 et 0,886.

**Les deux probabilités demandées** (scénario A) : **P(survit | mesure) = 0,89 ; P(éliminée | marché) = 0,88.** Les deux
dépassent 0,80. Verdicts à tort : survit sous « marché » 1,5 % ; éliminée sous « mesure » 1,6 % ; au plus 1,8 % dans tous les
scénarios.

**Lecture, sans enjoliver.**
- La décisivité dépasse 0,80 dans tous les scénarios sauf C, qui cumule trois hypothèses défavorables (après-2021 aussi
  dispersé que la découpe annuelle de F04, V_own 18 % plus bruité que V_cmt, aucun bruit commun aux deux mesures) : 0,79 et 0,76.
- Sous une vérité intermédiaire, le test rend souvent un verdict : « mixte, moitié » donne survit ou éliminée environ une fois
  sur trois chacun. C'est le prix d'une règle faite pour trancher : survit et éliminée y veulent dire « plus » ou « moins de la
  moitié », pas « tout » ou « rien ». La phrase de conclusion donnera m et son ET pour qu'on voie la distance au milieu.
- Un instrument atténué (V_own à 0,85 au lieu de 1,38 avant 2022) garde 0,84 sous « mesure ». Sous « marché » avec instrument
  atténué, le monde est en fait mixte (la courbe perd 0,53 pb de plus que le prix du titre) et le test rend surtout éliminée ou
  non concluant, rarement survit (5,9 %).

**Pourquoi la règle lit l'estimation de m, et non l'intervalle de D.** Au scénario A, l'ET attendue de D est d'environ 0,48 pb
(ET de V_own : environ 0,20 avant et 0,28 après ; ρ = 0), et les deux prédictions de D sont à 1,32 pb l'une de l'autre. Exiger
que l'intervalle à 90 % de D soit entièrement d'un côté du milieu ne donnerait le bon verdict qu'environ 4 fois sur 10
(Φ(0,66/0,48 − 1,645) ≈ 0,39). La règle protège autrement contre l'erreur : chaque verdict exige que la prédiction de
l'hypothèse rivale sur V_own soit rejetée au seuil unilatéral de 5 %, et que m soit du bon côté du milieu sur l'échantillon
entier comme sur les deux sous-échantillons. La simulation montre des verdicts à tort sous 2 %. Deux variantes plus prudentes
ont été essayées avec le même modèle (essais exploratoires de 3 000 à 4 000 tirages, hors du script joint) et écartées parce
qu'elles passent sous 0,80 dès le scénario B : exiger en plus que l'intervalle à 90 % de D exclue la prédiction rivale (0 pour
survit, −baisse de V_cmt pour éliminée) donne 0,73 et 0,76 ; une zone grise (survit sous 40 % de la baisse, éliminée au-dessus
de 60 %) donne 0,78 et 0,73.

## 10. Règle de verdict

Le verdict s'applique aux nombres du vérificateur. La règle est écrite pour que l'ordre d'évaluation ne change rien.

**En mots.**
- **Non concluant** si : le contrôle positif échoue (la borne basse à 90 % de V_own sur 2010-2021 n'est pas au-dessus de 0 :
  l'instrument ne voit pas la pression là où tout le monde la voyait, il ne peut pas arbitrer) ; ou la cassure à expliquer
  n'est pas là (la borne basse à 90 % de la baisse de V_cmt, sur ces mêmes adjudications, n'est pas au-dessus de 0) ; ou une
  garde de données se déclenche (schéma, échantillon sous le minimum, recalcul en désaccord) ; ou ni le profil « mesure » ni le
  profil « marché » ne tient (`indecis` = 1).
- **Survit (= artefact de mesure)** : la pression est toujours dans le prix du titre après 2021 (borne basse à 90 % de V_own
  après 2021 au-dessus de 0) **et** le prix du titre a perdu au plus la moitié de ce qu'a perdu la courbe du Trésor (m ≤ 0,
  c'est-à-dire D ≤ −½ × baisse de V_cmt), **et** cela reste vrai sans 2023 et sans le 30 ans.
- **Éliminée (= changement de marché)** : la pression dans le prix du titre a baissé significativement (borne basse à 90 % de
  la baisse de V_own au-dessus de 0) **et** de plus de la moitié de ce qu'a perdu la courbe du Trésor (m > 0), **et** cela reste
  vrai sans 2023 et sans le 30 ans.

**Conditions** (champs de la section 8) :
- *Non concluant* si l'une tient : `schema_ok` < 1 ; `n_avant` < 185 ; `n_apres` < 105 ; `n_grappes_avant` < 88 ;
  `n_grappes_apres` < 35 ; `ecart_max_rdt_pb` > 0,05 ; `controle_positif_ok` < 1 ; `controle_cassure_ok` < 1 ; `indecis` ≥ 1 ;
  (protocole) une donnée nommée manque, ou l'expérimentateur et le vérificateur diffèrent de plus que la tolérance.
- *Survit* si toutes tiennent : `borne_inf_90_v_own_apres_pb` > 0 ; `marge_moitie_pb` ≤ 0 ; `marge_moitie_sans_2023_pb` ≤ 0 ;
  `marge_moitie_sans_30_pb` ≤ 0 ; `controle_positif_ok` ≥ 1 ; `controle_cassure_ok` ≥ 1 ; `indecis` < 1 ; `schema_ok` ≥ 1 ;
  `n_avant` ≥ 185 ; `n_apres` ≥ 105 ; `n_grappes_avant` ≥ 88 ; `n_grappes_apres` ≥ 35 ; `ecart_max_rdt_pb` ≤ 0,05.
- *Éliminée* sinon : gardes et contrôles passés, `indecis` = 0 et `marge_moitie_pb` > 0, donc le profil (E) tient.

(Vérification des cas. Profil (S) : aucune condition de non-conclusion ne tient et toutes celles de survie tiennent → survit.
Profil (E) : `indecis` = 0, mais `marge_moitie_pb` > 0 fait échouer la survie → éliminée. Ni (S) ni (E) : `indecis` = 1 → non
concluant. (S) et (E) ne peuvent tenir ensemble, puisque m ne peut être à la fois ≤ 0 et > 0.)

**Justification de chaque seuil.**
- **La moitié (m = 0).** Les deux lectures prédisent m ≈ −0,66 et m ≈ +0,66 : zéro est à égale distance et traite les deux de
  la même façon. En mots, « survit » veut dire que la mesure explique la plus grande part de la disparition, « éliminée » que
  le marché l'explique. La moitié est aussi la part que F04-bis attribue à la méthode sur l'exercice 2021 (0,78 sur 1,64, soit
  48 %) : le test dit de quel côté de ce point d'incertitude tombe la baisse d'après 2021. Le milieu est calculé sur
  l'échantillon même (½ × baisse de V_cmt mesurée), non fixé d'après la découpe descriptive de F04 ; il vaudra environ 0,66 pb.
- **0 pour la borne basse de V_own après 2021.** « Marché » prédit V_own après ≈ V_cmt après ≈ 0,05. Survivre exige de
  rejeter cette prédiction au seuil unilatéral de 5 %.
- **0 pour la borne basse de la baisse de V_own.** « Mesure » prédit une baisse nulle. Être éliminée exige de rejeter cette
  prédiction au seuil unilatéral de 5 %.
- **1,645 (90 % bilatéral).** Deux tests unilatéraux à 5 %, un contre chaque lecture, comme J05 et K11. Avec 39 mois après
  2021, la valeur de Student à 38 degrés de liberté (1,686) déplacerait les bornes d'environ 0,01 pb : négligeable.
- **Contrôle positif à 0** (borne basse à 90 % de V_own sur 2010-2021) : consigne du responsable du projet. Au scénario A il
  passe presque toujours (V_own avant 1,38, ET ≈ 0,20).
- **Contrôle de la cassure à 0** : si V_cmt ne baisse pas sur ces adjudications, il n'y a rien à attribuer, et m n'a plus de
  sens. Au scénario A il passe environ 98 fois sur 100 (baisse 1,32, ET ≈ 0,34).
- **Sans 2023 et sans le 30 ans.** 2023 est l'année la plus dispersée de F04 (ET d'environ 1,36 pb pour 24 adjudications ; la
  faillite de SVB tombe dans la fenêtre de mars) et elle portait à elle seule le résultat de J05 (K = 3,34 pb) ; sans le 30 ans,
  J05 devenait incertain. Un verdict qui ne tiendrait que par une année ou une échéance n'en serait pas un. La condition est
  symétrique (elle vaut pour survit comme pour éliminée) et porte sur l'estimation de m, car une condition d'intervalle sur un
  sous-échantillon ôterait toute décisivité. Le détail par échéance (S1) reste descriptif : 39 réouvertures par échéance après
  2021 ne suffisent pas.
- **185, 105, 88, 35.** Attendus : 204 et 117 réouvertures, 96 et 39 mois. On tolère environ 10 % de pertes (pages ou valeurs
  absentes) et quelques mois. Au-delà, la perte ne serait plus accidentelle et la simulation ne vaudrait plus. Mêmes minimums
  de mois que J05 et K11.
- **0,05 pb d'écart de recalcul.** Deux mises en œuvre correctes de 6.2 s'accordent à 10⁻⁴ pb près (J05 : 6·10⁻¹¹) ; 0,05 pb
  reste dix fois sous les écarts en jeu.

**Tolérances entre expérimentateur et vérificateur.** 0 sur les comptes, `schema_ok`, `controle_positif_ok`,
`controle_cassure_ok` et `indecis` ; 0,005 pb sur les moyennes, les ET, les baisses, D et les marges ; 0,01 pb sur les bornes ;
0,05 pb sur `ecart_max_rdt_pb`.

## 11. Limites

1. **FedInvest donne un prix de fin de journée dont la source et l'heure ne sont pas documentées**, et l'instrument n'est
   validé que sur 2010-2021 (contrôle positif). Si la façon dont FedInvest produit ses prix avait changé après 2021, V_own
   changerait pour une raison de mesure et le test le prendrait pour un changement du marché (ou l'inverse). Rien dans les
   données publiques ne permet de le vérifier ; les prix sont des multiples exacts de 1/32, ce qui ressemble à des cotations
   plutôt qu'à une évaluation par modèle. **C'est la limite la plus sérieuse.**
2. **La moitié « montée » de V_own a déjà été vue** (R de J05 : pas de baisse, +0,64 pb). Le test n'est pas aveugle et
   « survit » est le verdict le plus attendu. Ce qui est neuf : la redescente, le niveau avant 2022, l'appariement.
3. **Une vérité au milieu rend le verdict fragile.** F04-bis attribue à la méthode environ la moitié de V en 2021. Si la vraie
   part est proche de la moitié, survit et éliminée sortent chacun environ une fois sur trois (section 9) et ne disent alors que
   « un peu plus » ou « un peu moins de la moitié ». La conclusion écrite donnera m et son ET.
4. **La décisivité repose sur des dispersions supposées**, tirées de V_cmt et de R. Dans le scénario le plus défavorable (C),
   elle tombe à 0,79 et 0,76. S4 dira après coup quel scénario était le bon.
5. **Décalage d'heure.** La courbe du Trésor part de cotations acheteuses relevées vers 15 h 30 ; FedInvest et GSW sont des
   fins de journée d'heure inconnue. Le pic d'un jour à J (figure 1) peut dépendre de l'heure de relevé ; le contrôle positif
   dira si V_own le voit.
6. **V_own est mesuré contre une courbe ajustée sur les titres anciens.** Si la pression s'étend à toute une zone d'échéance
   (leçon de K11), la courbe GSW en absorbe peut-être une petite partie. C'est commun aux deux mesures et aux deux périodes, et
   le contrôle positif vérifie qu'il en reste assez avant 2022.
7. **« Survit » ne dit pas laquelle des deux méthodes du Trésor a raison** (l'ancienne grossissait-elle V, ou la nouvelle
   l'efface-t-elle ?), et **« éliminée » ne dit pas pourquoi le marché a changé**.
8. **Composition.** Le 20 ans pèse un tiers des réouvertures après 2021 et 6 % avant ; D est apparié, mais les niveaux de V_own
   de chaque période mélangent les échéances. S1 donne le détail.
9. **Moyenne sensible aux valeurs extrêmes** (30 ans du 2020-03-12 dans J05 ; mars 2023). On garde la moyenne pour rester
   comparable à F04 et J05 ; la condition « sans 2023 » couvre la seconde.
10. **Disponibilité de GSW et FRED aux dates de M01 non vérifiée** par le rédacteur (section 5.4) ; une absence fait perdre la
    ligne, pas le test, sauf au-delà des minimums.
11. **Champ** : réouvertures nominales à 10, 20 et 30 ans seulement ; rien sur les nouvelles émissions ni sur les échéances de
    2 à 7 ans.

## 12. Ce qu'on écrira dans chaque cas

- **Survit.** « Mesurée sur le prix de fin de journée du titre rouvert lui-même, contre la courbe GSW de la Fed et sans aucune
  courbe du Trésor, la pression des réouvertures à 10, 20 et 30 ans vaut A pb en 2010-2021 (l'instrument la voit) et encore
  B pb en 2022-2026 (IC à 90 % : de B1 à B2, au-dessus de 0). Sur les mêmes adjudications et les mêmes jours, la mesure fondée
  sur la courbe du Trésor perd C pb, celle fondée sur le prix du titre E pb seulement (D = X pb, IC à 90 % de X1 à X2 ;
  m = Y pb, ET Z) : moins de la moitié, y compris sans 2023 et sans le 30 ans. La disparition de la pression après 2021 est donc
  pour l'essentiel un artefact de la courbe du Trésor, dont la méthode a changé le 6 décembre 2021 ; ce test ne dit pas
  laquelle des deux méthodes mesure juste [si |m| < Z : et la part de la mesure ne dépasse la moitié que de peu]. »
- **Éliminée.** « Mesurée de la même façon, la pression vaut A pb en 2010-2021 et B pb en 2022-2026 : elle a baissé de E pb
  (borne basse à 90 % au-dessus de 0), plus de la moitié des C pb perdus par la mesure fondée sur la courbe du Trésor (D = X pb,
  IC à 90 % de X1 à X2 ; m = Y pb, ET Z), y compris sans 2023 et sans le 30 ans. La disparition de la pression après 2021 est
  donc pour l'essentiel un changement du marché, que la courbe du Trésor a enregistré [si la borne basse de B est au-dessus de
  0 : il reste une pression de B pb] [si |m| < Z : la part du marché ne dépasse la moitié que de peu] ; il reste à expliquer
  pourquoi F04-bis trouvait un effet de la méthode en 2021. »
- **Non concluant.** « Le test ne tranche pas, pour la raison suivante : [l'instrument ne voit pas la pression en 2010-2021
  (borne basse de V_own avant 2022 ≤ 0) et ne peut donc pas arbitrer / la mesure fondée sur la courbe du Trésor ne baisse pas
  significativement sur ces adjudications : rien à expliquer / après 2021, la pression sur le prix du titre n'est ni
  significativement présente ni significativement en baisse : imprécision / le côté de la moitié change sans 2023 ou sans le
  30 ans / lecture mixte : la pression est encore présente mais a baissé de plus de la moitié sans que cette baisse soit
  significative, ou a baissé de moins de la moitié sans être significativement présente / échantillon sous le minimum /
  schéma violé / recalcul en désaccord / désaccord entre expérimentateur et vérificateur] ; on ne conclut ni que la pression a
  disparu du marché, ni qu'elle n'a disparu que de la courbe du Trésor. »

## 13. Règle lisible par machine

```json
{
  "id": "M01",
  "fichier_analyse": "M01_analyse.csv",
  "champs_verification": [
    "schema_ok",
    "n_avant",
    "n_apres",
    "n_grappes_avant",
    "n_grappes_apres",
    "ecart_max_rdt_pb",
    "v_own_avant_pb",
    "et_v_own_avant_pb",
    "borne_inf_90_v_own_avant_pb",
    "controle_positif_ok",
    "v_cmt_avant_pb",
    "v_cmt_apres_pb",
    "baisse_cmt_pb",
    "et_baisse_cmt_pb",
    "borne_inf_90_baisse_cmt_pb",
    "controle_cassure_ok",
    "v_own_apres_pb",
    "et_v_own_apres_pb",
    "borne_inf_90_v_own_apres_pb",
    "baisse_own_pb",
    "et_baisse_own_pb",
    "borne_inf_90_baisse_own_pb",
    "d_pb",
    "et_d_pb",
    "borne_inf_90_d_pb",
    "borne_sup_90_d_pb",
    "marge_moitie_pb",
    "et_marge_moitie_pb",
    "marge_moitie_sans_2023_pb",
    "marge_moitie_sans_30_pb",
    "indecis"
  ],
  "survit_si": [
    {"champ": "borne_inf_90_v_own_apres_pb", "operateur": ">", "seuil": 0},
    {"champ": "marge_moitie_pb", "operateur": "<=", "seuil": 0},
    {"champ": "marge_moitie_sans_2023_pb", "operateur": "<=", "seuil": 0},
    {"champ": "marge_moitie_sans_30_pb", "operateur": "<=", "seuil": 0},
    {"champ": "controle_positif_ok", "operateur": ">=", "seuil": 1},
    {"champ": "controle_cassure_ok", "operateur": ">=", "seuil": 1},
    {"champ": "indecis", "operateur": "<", "seuil": 1},
    {"champ": "schema_ok", "operateur": ">=", "seuil": 1},
    {"champ": "n_avant", "operateur": ">=", "seuil": 185},
    {"champ": "n_apres", "operateur": ">=", "seuil": 105},
    {"champ": "n_grappes_avant", "operateur": ">=", "seuil": 88},
    {"champ": "n_grappes_apres", "operateur": ">=", "seuil": 35},
    {"champ": "ecart_max_rdt_pb", "operateur": "<=", "seuil": 0.05}
  ],
  "non_concluant_si": [
    {"champ": "schema_ok", "operateur": "<", "seuil": 1},
    {"champ": "n_avant", "operateur": "<", "seuil": 185},
    {"champ": "n_apres", "operateur": "<", "seuil": 105},
    {"champ": "n_grappes_avant", "operateur": "<", "seuil": 88},
    {"champ": "n_grappes_apres", "operateur": "<", "seuil": 35},
    {"champ": "ecart_max_rdt_pb", "operateur": ">", "seuil": 0.05},
    {"champ": "controle_positif_ok", "operateur": "<", "seuil": 1},
    {"champ": "controle_cassure_ok", "operateur": "<", "seuil": 1},
    {"champ": "indecis", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "schema_ok": 0,
    "n_avant": 0,
    "n_apres": 0,
    "n_grappes_avant": 0,
    "n_grappes_apres": 0,
    "ecart_max_rdt_pb": 0.05,
    "v_own_avant_pb": 0.005,
    "et_v_own_avant_pb": 0.005,
    "borne_inf_90_v_own_avant_pb": 0.01,
    "controle_positif_ok": 0,
    "v_cmt_avant_pb": 0.005,
    "v_cmt_apres_pb": 0.005,
    "baisse_cmt_pb": 0.005,
    "et_baisse_cmt_pb": 0.005,
    "borne_inf_90_baisse_cmt_pb": 0.01,
    "controle_cassure_ok": 0,
    "v_own_apres_pb": 0.005,
    "et_v_own_apres_pb": 0.005,
    "borne_inf_90_v_own_apres_pb": 0.01,
    "baisse_own_pb": 0.005,
    "et_baisse_own_pb": 0.005,
    "borne_inf_90_baisse_own_pb": 0.01,
    "d_pb": 0.005,
    "et_d_pb": 0.005,
    "borne_inf_90_d_pb": 0.01,
    "borne_sup_90_d_pb": 0.01,
    "marge_moitie_pb": 0.005,
    "et_marge_moitie_pb": 0.005,
    "marge_moitie_sans_2023_pb": 0.005,
    "marge_moitie_sans_30_pb": 0.005,
    "indecis": 0
  }
}
```
