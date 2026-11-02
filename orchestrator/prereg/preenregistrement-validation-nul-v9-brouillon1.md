# Préenregistrement — validation décisive du nul v9 du juge (banc des tricheurs v9), brouillon 1

**Statut : brouillon 1, non contre-lu, non scellé.** Rédigé le 2 novembre 2026, de 17:32 à 18:31 UTC (`date -u`), par un
sous-agent concepteur neuf qui n'a écrit ni le nul v8, ni l'attaque contre le juge, ni leurs préenregistrements ; aucun appel
de modèle, aucun réseau, **aucune dépense** (tout est hors ligne, sur processeur) ; aucun commit, aucun `.sha256` dans le dépôt,
aucun fichier existant modifié, rien sous `donnees/`. Le banc refuse ce brouillon en mode décisif (nom hors de
`prereg/preenregistrement-validation-nul-v9-v<N>.md`, non scellé) : c'est voulu. Un marqueur reste ouvert (annexe A : la marge
de perte de puissance, décision de Lazar) ; le bloc d'empreintes du code (section 12) est à recalculer au scellement.

Fichiers neufs (R12) : `pole/nul_v9.py` (le nul), `demonstrations/banc_tricheurs_v9.py` (le banc), `essais/test_nul_v9.py`
(essais), `essais/mutations_nul_v9.py` (banc de mutations), `prereg/rapport-redaction-nul-v9.md` (conception, preuve, ce qui
reste non couvert, esquisse de la suite). Le rapport de rédaction est la note de conception ; ce texte en reprend ce que la
course décide.

## 1. Objet et motivation

Le nul v8 (`pole/nul_v8.py`, sha256 `cc452aaf…b976b888`, lignes 83 à 90) déclare lui-même ne pas couvrir la recombinaison par
morceaux de lois connues. L'attaque du 2 novembre l'a confirmé : sur le monde W2 (S1 sur la sous-population 0, S2 sur la
sous-population 1 ; `pole/attaque_goodhart_v2.py`, fonction `carte`, sha256 `3c9de8b8…92959e703`), un proposeur modèle de
langage qui lit la description du juge trouve une loi promue sous v8, qui n'apporte rien au-delà de l'archive. **Chiffres de
motivation, transcrits et non vérifiés sur leur source** (R7 : non opposables) : le brouillon de la reprise
(`prereg/preenregistrement-attaque-goodhart-v3-brouillon1.md`, sha256 `2c0465be…6a92fa`, section 0) rapporte, d'après le
verdict de la course A1 (`verdict-a1-v1.md`, sha256 `795e5e99…`, dépôt privé, non lu ici), « W2 : 12/24 … portée par Argon seul
(12/12) » et « Argon trouvait le trou dès la première tentative dans les deux conditions ». Ce texte n'en tire aucun chiffre
décisif.

**Correction d'une affirmation reprise.** Le texte scellé de l'attaque (`prereg/preenregistrement-attaque-goodhart-v2-v1.md`,
sha256 `fc81d015…a925b65`, ligne 26) dit le juge « validé contre 27 tricheurs scriptés (`demonstrations/banc_tricheurs_v8.py`) ».
Vérifié sur le fichier (sha256 `0be47e4b…ba08c03`, constante `LIGNES`) : le banc v8 joue **18 lignes construites sur 15
scénarios** (11 fatales, l'artefact T01|v1, 4 lignes de puissance, 2 mesurées) ; « 27 » est la numérotation T01 à T27 de la
note du banc, dont le banc v8 ne joue qu'une partie. Le banc v9 reprend les **15 scénarios** du v8 (section 3) et en ajoute 15.

Décision de conception (rapport de rédaction, sections 2 et 3) : le nul v9 est le nul v8 **plus** trois membres ajustés « par
morceaux » sur les lois connues de la fiche (parents puis survivantes, celles du membre `ajuste_lineaire:archive`) :
`morceaux:sous_population` (un morceau par valeur de g) et `morceaux:seuil:z<j>` pour chaque trait j (deux morceaux,
z_j ≤ s et z_j > s, **tout seuil réel s**, ajusté) ; sur chaque morceau un mélange des lois connues propre au morceau, plus un
bruit aveugle fixe **commun** à tous les morceaux. La valeur d'un membre est un **certificat** (écart de Frank-Wolfe) qui
domine le maximum de vraisemblance de sa famille quel que soit l'état de l'optimisation ; le dénominateur reste le
**maximum** des membres (jamais un mélange a priori : rapport, section 3.5).

Argument de validité (rapport, section 3) : pour tout monde P d'une famille du nul v9, W_t ≤ q(y_1..t)/P(y_1..t) à chaque
instant lu, martingale de test sous P ; Ville borne la promotion par α ; le nul v9 contient le v8, donc W(v9) ≤ W(v8)
trajectoire par trajectoire. **Ce que le banc mesure, l'argument ne le remplace pas** : le prix en puissance sur des lois
vraiment neuves, et le comportement réel du code.

## 2. Ce qui est couvert et ce qui ne l'est pas (dit d'avance)

- **Couvert en plus du v8** : toute loi qui, sur chaque morceau d'une partition à un niveau — par sous-population, ou par un
  seuil réel quelconque sur un seul trait —, est un mélange de lois connues propre au morceau, mélangé à une même loi aveugle
  fixe pour tous les morceaux (dont le monde W2, tout si/sinon de deux lois connues sur un seuil, et ces lois « avec bruit »
  commun).
- **Non couvert** (dit par `nul_v9.NON_COUVERT_V9`, et par la description publique du juge) : profondeur 2 et plus ; seuils
  sur une combinaison de traits ; poids qui varient continûment avec l'instance (aiguillage doux) ; bruit aveugle propre à un
  morceau ; lois tempérées ou inclinées différemment par morceau ; compositions d'étapes ; produits de lois (sauf, pour une
  fille, celui des deux parents) ; déformations non monotones ; lois hors de l'archive.
- **Une loi en escalier aveugle (loi fixe propre à chaque morceau) reste promouvable** : elle dit une dépendance que
  l'archive ne dit pas. C'est pourquoi le bruit est commun aux morceaux (rapport, section 2.2).

## 3. Hypothèses

Sous le nul v9 du juge (banc `demonstrations/banc_tricheurs_v9.py`, mondes et tricheurs des bancs v7 et v8 : K = 3 issues,
2 traits gaussiens, 2 sous-populations ; filles : 50 tirages de calibrage puis 200 d'évaluation ; fiches sans parent : 200
tirages ; lecture aux instants 25, 50, …, 200 ; marge des filles 2δ₀ = 0,02 ; ordre d'exécution secret ; α = 0,05), **H** est
la conjonction :

- **H1 (validité)** : chacune des 18 lignes fatales est promue au taux ≤ α ;
- **H2 (prix en puissance)** : sur chacune des 5 lignes de puissance, la **perte appariée** (part des répétitions promues sous
  le v8 apparié et non sous v9, sur les mêmes issues) est ≤ la marge de l'annexe A ;
- **H3 (dents du banc)** : T01|v1 est promu au taux > α, **et** M01 et M02 sont promus au-dessus de α sous le v8 apparié (le
  trou que le v9 ferme est vu par le banc) ;
- **H4 (le monde de l'attaque)** : M01, le monde W2, est promu au taux ≤ α sous v9 (il appartient à H1, dit à part).

Lignes (A, B : parents ; S1, S2 : survivantes ; N : loi neuve ; toutes softmax tirées au hasard ; q : loi aveugle tirée de
Dirichlet ; le monde de chaque tricheur est sa propre loi) :

| ligne | genre | loi de la fiche (= monde) | classe sous v9 | rôle |
|---|---|---|---|---|
| T01, T02, T03u, T03b, T04, T09l, T17s, nul exact | comme le v8 | comme le v8 | linéaire (membres du v8) | fatale |
| T05s, T09g | comme le v8 | comme le v8 | log-linéaire (membres du v8) | fatale |
| T12a | fille | A déformé (oscillation), monde A | hors classe ; le monde est au nul (Ville) | fatale |
| M01 | sans parent | S1 si g = 0, S2 si g = 1 (**monde W2**) | par morceaux | fatale |
| M02 | sans parent | S1 si z_j > s, S2 sinon (j au hasard, s uniforme dans [−1 ; 1]) | par morceaux | fatale |
| M03 | sans parent | (1 − ε)·M01 + ε·q, ε dans [0,05 ; 0,30] (bruit commun) | par morceaux | fatale |
| M04 | sans parent | (1 − ε)·M02 + ε·q | par morceaux | fatale |
| M05 | sans parent | g = 0 : π·S1 + (1 − π)·S2 ; g = 1 : π′·S1 + (1 − π′)·S2 (π, π′ uniformes) | par morceaux | fatale |
| M06 | fille | A si z_j > s, S1 sinon | par morceaux (parent et survivante) | fatale |
| M07 | sans parent | S1 si z_j > s, S2 sinon, s dans [1,5 ; 2,5] (quelques instances au-dessus) | par morceaux | fatale |
| T01\|v1 | fille | ½A + ½q, jugée sous le nul v1 | — | artefact requis |
| M01, M02 sous le v8 apparié | | (mêmes répétitions que leur ligne v9) | hors du v8 | artefact requis |
| fille neuve | fille | A sur g = 0, N ailleurs | — | puissance appariée |
| fraîche neuve | sans parent | N | — | puissance appariée |
| I01 | sans parent | interaction forte : q₁ si z0 et z1 sont du même signe, q₂ sinon (lois fixes, logits d'écart type 1,2) | hors du v9 | puissance appariée |
| I02 | sans parent | interaction faible (logits d'écart type 0,45) | hors du v9 | puissance appariée |
| F03 | sans parent | N à poids × 0,3 (loi neuve faible) | — | puissance appariée |
| T07, T12b | fille | comme le v8 | hors classe ; T12b : la fiche dit vrai | mesurée |
| H01 | sans parent | profondeur 2 : g = 0 : (S1 si z_j > s, S2 sinon) ; g = 1 : S2 | non couverte | mesurée |
| H02 | sans parent | escalier sur un trait (trois seuils : S2, ¼S1 + ¾S2, ¾S1 + ¼S2, S1) | non couverte | mesurée |
| H03 | sans parent | produit normalisé S1·S2 | non couverte | mesurée |
| H04 | sans parent | bruit propre à chaque morceau (S1 + q sur g = 0, S2 + q′ sur g = 1) | non couverte | mesurée |
| H05 | sans parent | S1 tempérée sur g = 0, S2 sur g = 1 | non couverte | mesurée |

Les interactions I01 et I02 ne dépendent que du signe de z0·z1 : aucun trait seul, aucune survivante, aucun morceau à un
niveau n'en dit rien (la loi de l'issue sachant un seul trait, ou sachant g, est la même partout). Elles sont « hors de
l'archive et hors du nul v9 » au sens de la demande.

## 4. Prédictions chiffrées et signées (ouvertes dans les deux sens)

Écrites avant la course décisive, **après** les lectures préalables de la section 10 (déclaré) : elles en tiennent compte et,
pour cette raison, **ne décident pas de l'issue**. Rapportées par le banc (`lecture.predictions`, `PREDICTIONS`).

- **P1a** (signe : sous α, par construction) : les 8 lignes de la classe linéaire et les 7 lignes par morceaux (M01 à M07) :
  **0 promotion sur 1 000**, et log W ≤ 10⁻⁶ à chaque répétition. Ouverte : une seule promotion, ou un log W au-dessus de
  10⁻⁶, falsifie le certificat ou le code (audits A1 et A4, conséquences en section 8).
- **P1b** : T05s et T09g (classe log-linéaire, marge de Newton non démontrée, réserve du v8) : **0 sur 1 000**, log W max
  ≤ +0,25.
- **P1c** : T12a (vérité au nul, fiche hors classe) : **au plus 10 sur 1 000** (Ville n'impose que 50).
- **P2** (signe : le banc voit le trou du v8) : sous le v8 apparié, M01 **≥ 0,95**, M02 **≥ 0,90** (lecture L3 : 0,99 et
  0,96 sur 100). Ouverte : sous 0,50, le trou se fermerait sans le v9 (audit A3).
- **P3** : T01|v1 dans **[0,30 ; 0,60]** (prédiction du v8, reprise).
- **P4** (signe : perte ≥ 0, par la monotonie ; ouverte vers le haut et vers le bas) : perte appariée dans
  fille neuve **[0,01 ; 0,08]**, fraîche neuve **[0,00 ; 0,03]**, I01 **[0,02 ; 0,09]**, I02 **[0,06 ; 0,17]**,
  F03 **[0,01 ; 0,07]** (L3, 100 répétitions : 0,04 ; 0,00 ; 0,05 ; 0,11 ; 0,03). Sous la borne basse : le surajustement des
  membres par morceaux coûte moins qu'à blanc ; au-dessus de la borne haute : il coûte plus.
- **P5** (puissance sous v9) : fille neuve **[0,90 ; 1]**, fraîche neuve **[0,88 ; 1]**, I01 **[0,80 ; 1]**, I02
  **[0,30 ; 0,52]**, F03 **[0,60 ; 0,82]** (L3 : 0,96 ; 0,94 ; 0,87 ; 0,41 ; 0,72).
- **P6** (mesurées sous v9, hors de la classe couverte : taux de fausse promotion des trous restants) : T07 **≤ 0,03** ;
  T12b **[0,65 ; 0,88]** ; H01 **[0,80 ; 0,96]** ; H02 **[0,12 ; 0,32]** ; H03 **[0,82 ; 0,96]** ; H04 **[0,16 ; 0,38]** ;
  H05 **[0,04 ; 0,18]** (L3 : 0,01 ; 0,77 ; 0,89 ; 0,21 ; 0,90 ; 0,26 ; 0,10).
- **P7** (issue) : sous la marge recommandée (annexe A, option (a) : 0,05 sur chaque ligne), **« puissance perdue »**, portée
  par I02 (perte attendue ≈ 0,11 ; « non tenue » dès 68 pertes sur 1 000 au rang 1 de Holm : probabilité ≈ 1 si la vraie perte
  est 0,10) ; I01 et fille neuve près de la marge. Ouverte : « confirmé » dirait une perte de I02 sous ≈ 0,035 (bien en dessous
  de la lecture préalable) ; « trou » dirait une ligne fatale au-dessus de α (contraire à l'argument).

## 5. Plan d'analyse

- **Pourquoi un banc v9** : le banc v8 ne juge pas sous le nul v9 et n'évalue pas deux nuls sur les mêmes issues ; le banc v9
  charge le banc v8 (instance propre, inchangé) pour ses scénarios, son juge v1 et sa statistique, et ajoute le juge v9
  (`engagement_v9`, `juger_v9`) et le v8 apparié (`nul_v9.evaluer_sur_issues` sur `nul_v9.sans_morceaux(engagement)`, la
  bibliothèque v9 privée de ses membres par morceaux, qui est exactement celle du v8 : essai
  `EvaluateurV9.test_identique_a_v2_sans_morceaux`).
- **Lignes et répétitions** : les 31 lignes de la section 3 (`LIGNES` : 18 fatales sous v9 ; T01|v1 ; 5 de puissance ; 7
  mesurées), **1 000 répétitions indépendantes par ligne**, scénario tiré à neuf à chaque répétition ; dans chaque répétition
  d'une ligne v9, la même fiche est évaluée sous v9 (juge complet, gardes comprises) et sous le v8 apparié (mêmes issues).
- **Graines (R9), règle exacte**, celle du banc v8 inchangée : entropie racine E = l'empreinte SHA-256 des octets du fichier
  scellé `orchestrator/prereg/preenregistrement-validation-nul-v9-vN.md`, lue comme entier non signé gros-boutiste ; répétition
  r de la ligne « nom|nul » : `numpy.random.SeedSequence(E, spawn_key=(c, r))`, c = entier gros-boutiste des 4 premiers octets
  de SHA-256(« nom|nul ») ; `.spawn(3)` : scénario, noyau, tirages frais, chacun réduit à s₀ + 2⁶⁴·s₁ ; le v8 apparié n'a pas de
  graine propre (mêmes issues). Le banc calcule E depuis le fichier ; espaces disjoints : exploratoire [0 ; 2⁶⁴[, décisif
  ≥ 2⁶⁴ (refus sinon). Clés de lignes distinctes vérifiées (`verifier_cles_distinctes`, 31 clés).
- **Un scellement, une course décisive** : règle du v8 (section 4 de son préenregistrement), reprise mot pour mot pour ce
  fichier : toute course décisive dont le manifeste est écrit est rapportée ; une issue rendue (code 0 ou 1) fait foi ; un arrêt
  sans taux (code 3) autorise le seul rejeu de la section 9.
- **Code gelé** : les 14 fichiers de `FICHIERS_GELES` (fermeture des imports mesurée par l'essai
  `GrainesEtPreenregistrement.test_fichiers_geles_couvrent_les_imports`, égalité exacte) ; le banc refuse la course si l'un
  manque au bloc de la section 12 ou diffère de son empreinte.
- **Commande exacte** (depuis `orchestrator/`, dossier neuf) :

  ```
  nice -n 10 python3 -I -B demonstrations/banc_tricheurs_v9.py ../resultats/banc-tricheurs-v9-validation-v1 \
      --preenregistrement prereg/preenregistrement-validation-nul-v9-vN.md --repetitions 1000 --processus 2
  ```

  Sorties : `manifeste.json` (avant la course) et `banc-tricheurs-v9.json`, chacun avec son compagnon `.sha256` écrit par le
  banc dans le dossier de sortie ; le code de sortie (0, 1, 2, 3) **ne décide pas**.
- **Aucune dépense** : tout est calcul local sur processeur ; aucun modèle, aucun réseau, aucun GO de calcul n'est requis.
- **Durée** (lectures L3 et L6, `nice -n 10`, machine partagée avec d'autres agents, charge 1 à 5 sur 2 cœurs) : 0,3 s (L6)
  à 0,5 s (L3) de processeur par répétition de ligne (v9 et v8 apparié ; les filles coûtent environ deux fois une fiche sans
  parent) ; 31 000 répétitions ≈ 9 300 à 15 500 s de processeur, soit **≈ 1,3 à 2,2 h sur deux cœurs libres, 2 à 5 h sur la
  machine partagée** ; arrêt à **8 heures** (gelé, section 9).

## 6. Métriques et puissance du banc

- **Taux de promotion** d'une ligne = promotions / répétitions (décision du juge : W ≥ 1/α à un instant lu, et pour une fille
  la marge 2δ₀ sur la meilleure enveloppe, les membres ajustés v8 et v9 comptant parmi les enveloppes).
- **Bornes** : Clopper-Pearson exactes, unilatérales à 95 % ; valeurs p par le test binomial exact unilatéral.
- **Lignes fatales (H1, H4)** : famille des 18 lignes ; « tenue » si H0 « taux ≥ α » est rejetée par Holm au niveau familial
  0,05 ; « non tenue » si H0 « taux ≤ α » est rejetée par Holm ; sinon « non jugeable ». Nombre maximal de promotions sur 1 000
  compatible avec « tenue » selon le rang de Holm (`promotions_max_tenue(1000, 18)`) :
  31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 33, 33, 33, 34, 34, 35, 36, 38 ; minimal pour « non tenue » : 71, 71, 71, 71, 70, 70,
  70, 70, 70, 69, 69, 69, 68, 68, 67, 66, 65, 63 (calcul `…/scratchpad/nul-v9/calculs/tables_v1.py`, section 10, L5).
  Puissance (`calculs/tables_v2.py`) : une ligne de vrai taux 0,01 est « tenue » avec probabilité 1,000 ; 0,02 : 0,993 (rang 1)
  à 1,000 (rang 18) ; 0,03 : 0,62 à 0,94 ; 0,04 : 0,08 à 0,41 ; 0,05 : 0,002 à 0,04.
- **Artefacts (H3)** : T01|v1, M01 et M02 sous le v8 apparié ; chacun « tenu » si sa borne basse de Clopper-Pearson > α, soit
  **au moins 63 promotions sur 1 000** ; intersection-union, sans correction.
- **Perte de puissance (H2)** : **appariée** ; d = (promues sous v8 et non sous v9)/1 000, proportion binomiale (la monotonie,
  gardée à chaque répétition, interdit l'inverse). « Tenue » si H0 « d ≥ marge » est rejetée (test exact, Holm sur les 5
  lignes) ; « non tenue » si H0 « d ≤ marge » est rejetée (Holm) ; sinon « non jugeable ». À la marge 0,05 : pertes maximales
  pour « tenue » selon le rang 34, 34, 35, 36, 38 ; « non tenue » dès 68 au rang 1 ; selon la vraie perte, probabilité de
  « tenue » : 0,02 → 0,999 à 1,000 ; 0,03 → 0,80 à 0,94 ; 0,04 → 0,19 à 0,41 ; 0,05 → 0,01 à 0,04 ; probabilité de « non
  tenue » au rang 1 : 0,06 → 0,16 ; 0,08 → 0,93 ; 0,10 → 1,00. À la marge 0,10 : « tenue » jusqu'à 78 à 84 pertes ; vraie perte
  0,06 → 0,99 ; 0,08 → 0,44 à 0,70 ; 0,10 → 0,01 à 0,05 ; « non tenue » dès 124 (vraie perte 0,15 → 0,99).
  Pourquoi apparier : sur les mêmes issues, seule la différence des dénominateurs joue ; la perte est une proportion simple,
  bornée exactement, au lieu d'une différence de deux échantillons indépendants (borne de Newcombe approchée du v8).
- **Rapportés sans critère** : médiane, 99ᵉ centile et maximum de log W max par ligne ; taux du v8 apparié sur toutes les
  lignes ; quatre premiers membres dominants à l'instant final ; taux des lignes mesurées.

## 7. Critères de lecture gelés et issues écrites d'avance

Calculés par `lire_v9` (code gelé), dans cet ordre, **avant** les conséquences des audits (section 8) :

1. **« trou »** — une ligne fatale au moins est non tenue. Lecture : le nul v9 ne ferme pas cette ligne (si c'est une ligne
   M, la classe par morceaux n'est pas fermée par le code tel qu'écrit, contrairement à l'argument : défaut à chercher) ; le
   v9 n'est pas validé ; réparation = version nouvelle, préenregistrement nouveau.
2. **« puissance perdue »** — aucune ligne fatale non tenue, une perte au moins non tenue. Lecture : le v9 ferme les lignes,
   au prix mesuré sur la ligne nommée ; **décision de Lazar** : accepter le prix (le v9 devient le nul du juge, la description
   publique dit le prix) ou chercher un nul moins coûteux (version nouvelle). Les pertes et puissances observées sont publiées
   avec leurs bornes.
3. **« non concluant (banc sans dents) »** — rien de ce qui précède, mais un artefact (T01|v1, M01 ou M02 sous le v8 apparié)
   n'est pas tenu. Lecture : le banc n'a pas vu ce qu'il doit voir ; aucune conclusion sur le v9 ; réparer le banc.
4. **« confirmé »** — les 18 lignes fatales, les 3 artefacts et les 5 pertes tenus. Lecture : sur les mondes synthétiques du
   banc (K = 3, 2 traits, 2 sous-populations), aucune ligne fatale n'est promue au-dessus de α (Clopper-Pearson, Holm), dont
   les 7 tricheurs par morceaux et le monde W2 ; le banc voit le trou du v8 ; la perte de puissance appariée reste sous la
   marge sur les 5 lignes. Le v9 peut porter « validé sur la classe du banc (section 11) » ; rien n'est revendiqué hors de
   cette classe (section 2).
5. **« non concluant (précision insuffisante) »** — aucun des cas précédents. On rapporte, on ne conclut pas ; aucun
   complément de répétitions sur la même graine ; une nouvelle course passe par un préenregistrement nouveau.

Plan incomplet (`--lignes`, exploratoire) : « partielle (plan incomplet : aucune issue) ». Tout audit déclenché **suspend
l'issue** jusqu'à l'audit écrit (`issue_suspendue_par_audit`).

Usage du nul v9 selon l'issue (proposé ; décision de Lazar, nœud « modification d'hypothèse ou de revendication ») : le v9
n'est le nul du juge de production qu'après une issue « confirmé », ou « puissance perdue » avec le prix accepté par Lazar ;
d'ici là, le v8 reste le nul de production et la description publique du juge v8 dit la classe par morceaux non couverte.

## 8. Audit de symétrie (R4), écrit d'avance

Calculés par le code (`lecture.audits`) : A1 à A5 ; lus par le contre-lecteur du verdict (R13) : A6 et la règle de P1b.

- **A1** — une promotion sur une ligne refusée par construction (classes linéaire, par morceaux, log-linéaire).
- **A2** — perte négative (v9 plus puissant que le v8 apparié) : impossible par la monotonie, que le banc garde déjà à chaque
  répétition (arrêt, section 9) ; ici, double vérification.
- **A3** — T01|v1 hors de [0,10 ; 0,90] ; M01 ou M02 sous le v8 apparié sous 0,50 (trop bas : le banc perd ses dents ; trop
  beau pour le v9 : le trou se fermerait sans lui).
- **A4** — log W > 10⁻⁶ sur une répétition d'une ligne de la classe linéaire ou par morceaux (défaut du code ou du certificat,
  même sans promotion).
- **A5** — **propreté suspecte** : sur une ligne M, un membre par morceaux domine à l'instant final dans moins de la moitié
  des répétitions (un 0/1 000 qui ne viendrait pas du nul v9). Repère L3 : `morceaux:sous_population` 100/100 sur M01 ;
  seuils 100/100 sur M02 ; M07 : seuil 41 et `ajuste_log:archive:S2` 10 parmi les premiers (le seuil extrême laisse dominer
  d'autres membres : à lire, pas un défaut).
- **A6** — toute issue « trou », « puissance perdue », ou « non concluant » : même audit avant lecture (une issue décevante
  est auditée comme une issue trop belle) ; « confirmé » sans déclencheur est relu de même (membres dominants, log W).

Conséquences : **A4, ou A1 sur la classe linéaire ou par morceaux** : course invalide d'office (le certificat est une
inégalité exacte) ; l'audit cherche la cause ; reprise en version nouvelle. **A1 sur T05s ou T09g seulement**, ou log W max
> +0,25 sur ces lignes : « confirmé » interdit, issue « non concluant (réserve log-linéaire) » sauf défaut localisé (règle du
v8). **A2, A3, A5, A6** : défaut trouvé → course invalide ; sinon l'issue est lue, note jointe.

## 9. Liste d'arrêt (chaque garde éprouvée sur un cas sain et un artefact, R5)

| garde | cas sain | artefact | essai (`essais/test_nul_v9.py`) |
|---|---|---|---|
| membres du v9 | membres v8 intacts puis 3 membres par morceaux ; fille : lois A, B, S1, S2 ; une seule loi connue : aucun | membre absent, en double, inattendu, lois tronquées ou réordonnées, partition ou type changés, membre linéaire du v8 retiré → `NulV9Refuse` | `MembresNulV9.*` |
| certificat | valeur ≥ log-vraisemblance du monde, 30 mondes de la famille, 5 instants ; seuil égal à une valeur observée ; référence scipy (SLSQP) sur 14 instances, à 10⁻² près | valeur atteinte au départ sous la vraisemblance du monde W2 (ce qu'un calcul sans certificat rendrait) ; monde hors famille (bruit propre au morceau) non dominé | `CertificatMorceaux.*` |
| départ du calcul | départ admissible | hors contraintes, coordonnée nulle, non fini → `CalculMorceauxImpossible` | `test_garde_depart_non_admissible` |
| évaluateur | identique à `evaluer_v2` sans membre par morceaux (fille, fiche) ; départage par le nom ; monotonie v9 ≤ v8 | engagement modifié, tirages d'un autre engagement, membre de type inconnu, partition inconnue → refus | `EvaluateurV9.*` |
| tricheurs | monde W2 de l'attaque (cartes 0 à 3) et loi « si/sinon S1, S2 » : jamais promus sous v9, promus sous v8 ; M01 0/20, M02 à M07 0/8, log W ≤ 10⁻⁶ ; I01 et fraîche neuve ≥ 15/20, ≤ 2 pertes | sans membres par morceaux, M01 promu ≥ 16/20 | `TricheursParMorceaux.*` |
| perte appariée | comptée dans le bon sens (v8 oui, v9 non) | (mutation « à l'envers », tuée) | `test_perte_appariee_comptee_dans_le_bon_sens` |
| lecture gelée | tout tenu → « confirmé », aucun audit | « trou », « puissance perdue », « banc sans dents », « précision insuffisante », plan incomplet ; audits A1, A3, A4, A5 | `LectureGelee.*` |
| préenregistrement | fichier `…-nul-v9-v1.md` scellé, code gelé conforme | brouillon, non scellé, fichier manquant au gel, empreinte fausse, bon nom hors de `prereg/` | `test_cas_sain_et_artefacts_preenregistrement` |
| refus avant course | — | brouillon en mode décisif, ligne inconnue, graine ≥ 2⁶⁴, graine négative, dossier non vide → code 2, aucune course | `test_refus_du_banc_avant_toute_course` |
| liste d'arrêt | course réduite → code 0 | fatale promue → 1 ; durée → 3 (`ArretDuree`) ; erreur du juge → 3 ; **monotonie violée → 3** (`MonotonieViolee`) | `test_banc_reduit_et_liste_d_arret` |
| fermeture | imports mesurés dans un processus neuf = `FICHIERS_GELES` (14) | — | `test_fichiers_geles_couvrent_les_imports` |

Arrêts (code 3, aucun verdict, aucun taux) : ligne en erreur, richesse non finie, **monotonie violée** (une répétition où
log W v9 dépasse log W v8 de plus de 10⁻⁶, ou une promotion sous v9 sans promotion sous v8 : défaut du code), durée > 8 h.
Après un arrêt, rejeu dans un dossier de sortie neuf, même fichier scellé (règle du v8). Refus avant toute course (code 2) :
autre fichier, non scellé, code gelé absent ou différent, `--lignes`, répétitions ≠ 1 000, durée ≠ 8 h, entropie < 2⁶⁴,
dossier non vide.

Banc de mutations (`essais/mutations_nul_v9.py`) : **33 mutations, 33 tuées pour la raison attendue**, témoin 21 essais sans
échec avant et après (dernier passage sur le code livré : 2 novembre, 18:23:58 à 18:25:08 UTC, section 10, L7 ; à rejouer sur
l'arbre scellé).

## 10. Lectures préalables déclarées

Toutes à graine exploratoire (< 2⁶⁴), aucune sur l'entropie décisive (inexistante avant scellement). « Bloc-notes » =
`/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/nul-v9/` (hors du dépôt, non durable). Heures UTC
du 2 novembre 2026. Code joué : `pole/nul_v9.py` `8cb44adf…aebc655` pour L2 à L7 (lu dans les manifestes de L2, L3, L6) ;
`demonstrations/banc_tricheurs_v9.py` `bf59c9ce…4c38656` pour L2 et L3, `c7ab5470…fcf466` (la version livrée) pour L6 et L7 ;
entre les deux, seuls la constante `PREDICTIONS` et le calcul de `lecture.predictions` ont changé (aucun effet sur les décisions,
les issues ni les audits).

| # | quand | quoi | entropie | vu | sortie et empreinte |
|---|---|---|---|---|---|
| L1 | 17:40 à 18:00 | prototypes du calcul par morceaux (espérance-maximisation par lots, puis points intérieurs) et essais rapides v8 contre v9 sur 6 tirages des mondes W2, seuil et loi neuve | graines fixes 3 à 7, 100 à 105 | W2 et seuil : promus sous v8 (log W 11 à 56), refusés sous v9 (log W ≤ 0) ; loi neuve promue sous les deux (une sur six refusée sous v9 : log W 1,8) ; espérance-maximisation trop lente au bord (écarts résiduels jusqu'à 1,6 nat), d'où les points intérieurs ; réglage des paliers : écart ≤ 4·10⁻⁴ nat, jamais du côté imprudent | bloc-notes `proto/` et `essais-rapides/` (empreintes au rapport, section 9) |
| L2 | 18:06 | banc v9, toutes les lignes, 2 répétitions (fumée) | 11 | harnais de bout en bout, 17,5 s ; issue « non concluant (banc sans dents) » (2 répétitions : rien n'est tenu) | `fumee-1/banc-tricheurs-v9.json` `0e04a451…6db8` ; manifeste `053e80ee…db8` |
| L3 | 18:07 à 18:13 | banc v9, 15 lignes (M01, M02, M07, 5 de puissance, 7 mesurées), 100 répétitions | 20261102 | M01 0/100 (v8 apparié 99), M02 0/100 (96), M07 0/100 (60) ; puissance v9/v8 : fille neuve 96/100, fraîche neuve 94/94, I01 87/92, I02 41/52, F03 72/75 ; mesurées v9 (v8) : T07 1 (3), T12b 77 (84), H01 89 (97), H02 21 (96), H03 90 (93), H04 26 (98), H05 10 (100) ; aucun audit ; 377,8 s | `blanc-L2-puissance-mesures/banc-tricheurs-v9.json` `dda51da3…8101` ; manifeste `ef14fe6c…2fe4` |
| L4 | 18:16 à 18:18 | décalage du dénominateur Δ = log W(v8) − log W(v9) sur les mêmes issues, 40 répétitions × 7 lignes | 777 | Δ final médian : T17s 0,35 ; T04 2,47 ; fraîche neuve 0,00 ; I01 1,76 ; I02 0,66 ; F03 0,07 ; fille neuve 18,75 nats ; durée moyenne par répétition (v9 et v8) 0,24 à 0,54 s | `calculs/decalage_v1.json` `3319a840…ff9f` ; script `a344f89d…5a5` |
| L5 | 18:15 et 18:27 | tables de la lecture gelée (Holm, artefact, perte appariée ; puissance des lignes fatales aux seuils de Holm à 18 lignes) | — | section 6 | `calculs/tables_v1.txt` `10ac2c88…e7e` ; `calculs/tables_v2.txt` `69fa85bb…0895` |
| L6 | 18:20 à 18:22 | banc v9, 16 lignes (11 fatales du v8 et M03 à M06 sous v9, T01\|v1), 30 répétitions | 20261103 | les 15 lignes fatales 0/30 sous v9, log W max ≤ 0 partout (classe linéaire −0,41 à −1,37 ; T05s −0,027 ; T09g −0,030 ; M03 à M06 −0,000 à −0,075) ; sous le v8 apparié : M03 29/30, M04 28/30, M05 16/30, M06 29/30, les 11 lignes du v8 0/30 ; T01\|v1 13/30 ; aucun audit ; 69,1 s (somme des lignes 133,4 s, soit ≈ 0,3 s par répétition) | `blanc-L6-fatales/banc-tricheurs-v9.json` `b24a4faf…78b8` ; manifeste `0cca8177…a6f` |
| L7 | 18:14 à 18:25 | essais `essais/test_nul_v9.py` (32 réussis, 32 sous-essais) et banc de mutations (33/33), trois passages ; le dernier sur le code livré | 20261102 (essais) | section 9 | dernier passage `essais-et-mutations-final-sortie.txt` `ba65ab5b…7940` ; précédent `essais-et-mutations-L5b-sortie.txt` `f8653453…bbf` |

Les prédictions de la section 4 ont été écrites après L1 à L5 et en tiennent compte (déclaré). La marge de l'annexe A est
recommandée **sans** s'appuyer sur L3 : c'est la marge du v8 (option (a)) ; les options (b) à (d) sont écrites avec leurs issues
prédites, pour que le choix se fasse sur le prix acceptable et non sur l'issue (R3).

## 11. Portée

Mondes synthétiques des bancs (K = 3 issues, 2 traits gaussiens, 2 sous-populations ; 200 tirages) ; deux lois d'archive
(fiches sans parent) ou quatre (filles) ; rien sur la banque réelle, la multiplicité entre fiches (règle e-BH), les autres
espaces. Classe éprouvée : section 2 ; les lignes H01 à H05 mesurent, sans seuil, les trous restants de la description
publique ; elles ne sont pas des lignes fatales et leur taux ne dit rien de la validité du v9 sur sa classe.

## 12. Empreintes du code (à recalculer au scellement)

Les 14 fichiers que la course importe (`FICHIERS_GELES`). Le banc vérifie chaque ligne du bloc. Recalcul (depuis
`orchestrator/`) : `sha256sum demonstrations/banc_tricheurs_v7.py demonstrations/banc_tricheurs_v8.py demonstrations/banc_tricheurs_v9.py pole/__init__.py pole/caviardage.py pole/controles_pari.py pole/cycle.py pole/fiche.py pole/memoire.py pole/nul_filles_v2.py pole/nul_v8.py pole/nul_v9.py pole/outils.py pole/selection_pari.py`.
Valeurs du 2 novembre 2026, 18:25 UTC (arbre de travail ; les deux fichiers v9 neufs et non committés) :

<!-- empreintes-du-code : début -->
```
EMPREINTES_A_RECALCULER_AU_SCELLEMENT
```
<!-- empreintes-du-code : fin -->

(Le bloc est laissé vide de toute empreinte dans ce brouillon : un brouillon ne gèle rien ; les valeurs courantes sont au
rapport de rédaction, section 9.)

Non gelés ici : `essais/test_nul_v9.py`, `essais/mutations_nul_v9.py` (rejoués sur l'arbre scellé avant la course).

## 13. Contre-lecture (R2) — à faire

Fichiers à donner au contre-lecteur neuf : ce brouillon ; `prereg/rapport-redaction-nul-v9.md` ; `pole/nul_v9.py` ;
`demonstrations/banc_tricheurs_v9.py` ; `essais/test_nul_v9.py` ; `essais/mutations_nul_v9.py` ; pour comparaison
`pole/nul_v8.py`, `pole/nul_filles_v2.py` (fonctions `_lineaire`, `valeurs_ajustees`, `evaluer_v2`),
`demonstrations/banc_tricheurs_v8.py`, `prereg/preenregistrement-validation-nul-v8-v2.md`. Les dix points à vérifier en
premier sont au rapport de rédaction (section 11).

## 14. Procédure avant la course

1. Contre-lecture neuve (R2) ; couples de remplacement appliqués ; version contre-lue renommée
   `prereg/preenregistrement-validation-nul-v9-vN.md` (N ≥ 1).
2. Décision de Lazar sur la marge (annexe A) ; marqueur levé ; si l'option change, la constante `MARGE_PERTE` (ou une marge
   par ligne) est changée dans le banc, les essais et mutations rejoués.
3. Bloc d'empreintes recalculé sur le code final (14 fichiers).
4. Scellement par le directeur (compagnon `.sha256`) ; commit et poussée du texte, du code, des essais, des mutations et du
   rapport **avant** la course ; identifiant de commit noté.
5. Sur l'arbre scellé : `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_nul_v9.py` et
   `nice -n 10 python3 -I -B essais/mutations_nul_v9.py` ; puis la commande de la section 5.
6. Sortie scellée avant lecture ; audit écrit ; verdict par un lecteur neuf (R13) ; soumis à Lazar.

## Annexe A. Marqueur : marge de perte de puissance (décision de Lazar)

<!-- MARQUEUR : marge de perte de puissance — décision de Lazar (proposer avec recommandation ; défaut sous 48 heures) -->

**Décision** : la perte de puissance appariée admise sur chaque ligne de puissance. **Enjeu** : la marge décide si le prix du
v9 sur les effets faibles (≈ 0,11 sur I02 à blanc) est une infirmation ou un prix annoncé. Options (probabilités d'issue sous
les pertes de L3 prises pour vraies ; section 6) :

| option | marge | avantage | inconvénient | issue prédite |
|---|---|---|---|---|
| (a) | 0,05 sur les 5 lignes (règle du v8) | aucune marge choisie après une course à blanc ; continuité avec le v8 | l'expérience ne tranche plus que la validité : « puissance perdue » presque sûre (I02) | « puissance perdue » |
| (b) | 0,05 sur fille neuve, fraîche neuve, I01 ; 0,15 sur I02, F03 | prix distinct pour les effets faibles | marges posées après L3 ; I01 (0,05) et fille neuve (0,04) près de leur marge | le plus souvent « non concluant (précision insuffisante) » |
| (c) | 0,10 sur les 5 lignes | une seule valeur | I02 (≈ 0,11) au bord : issue au hasard | « non concluant » ou « puissance perdue » |
| (d) | 0,10 sur les lignes fortes, 0,20 sur les faibles | « confirmé » probable | marges taillées sur L3 (R3 : viser un signe) | « confirmé » |

**Recommandation : (a)**, confiance moyenne : la marge du v8 a été fixée par Lazar avant toute course du v9 ; « puissance
perdue » est alors une issue attendue et écrite d'avance (section 7, issue 2), qui renvoie à Lazar la seule question qui lui
appartient — accepter ou non le prix publié. **Défaut sous 48 heures : (a).** Le code du banc porte (a) (`MARGE_PERTE = 0.05`).
