# Préenregistrement — étage des juges d'idéation, version 2 : le protocole par paires discrimine-t-il là où l'ancien sature ? (brouillon 2)

Statut : **brouillon 2, non scellé, non contre-lu** (couples de la contre-lecture v1 appliqués ou refaits, section 14) ;
contre-lecture du brouillon 1 : `prereg/contre-lecture-preenregistrement-juges-idees-v2-v1.md` (sha256
`1dc3c1943c5322731efa7deedd97e9cce7fe7746f6cec268bc05c3f980d43977`) et ses 40 couples
`prereg/couples-contre-lecture-juges-idees-v2-v1.json` (`ad48ba2f40287b9a46b79e5e64a243880d0b72b2e95cde06b3dbfc111e55d79a`).
Rédigé du 2 novembre 2026, 23:31 UTC, au 3 novembre 2026, 01:32 UTC (heures lues sur `date -u`) par un concepteur-développeur neuf, qui n'a écrit ni l'étage des juges existant, ni
le brouillon 1, ni sa contre-lecture ; aucun appel de modèle, aucune clé, aucun réseau, aucun commit, aucun compagnon `.sha256`.
Code (R12, fichiers déjà neufs au brouillon 1, modifiés ici) : `pole/juges_idees_v2.py`, `demonstrations/validation_juges_idees_v2.py`,
`essais/test_juges_idees_v2.py`, `essais/mutations_juges_idees_v2.py` ; empreintes, essais et banc au rapport
(`prereg/rapport-redaction-juges-idees-v2-brouillon2.md`). **GO : `GO-2026-11-02-32`** (calcul, 60 USD, accordé par Lazar le
2 novembre 2026, échéance le 16 novembre ; `registres/go.md` du dépôt de travail, ligne 78, sha256 du registre lu
`53985197d3e9780db9bf9738c050c3e746eea149af3e4024649f41db5cedef0a` ; la ligne passe `configuration_v56.verifier_go_v56` au
montant de 60 USD, vérifié le 3 novembre 2026 à 01:27 UTC). Trois marqueurs restent, et le lanceur refuse tout texte qui en porte un :
`<<CONFIGURATION_SHA256>>` (section 4), `<<EMPREINTE_DU_CODE>>` (une ligne par fichier de la fermeture du chemin réel, section
11, à remplir au commit) et `<<EPREUVE_ASTRA_8807>>` (section 4 : la commande Astra n'a jamais servi). Le scellement se fait sur
une version contre-lue, renommée `prereg/preenregistrement-juges-idees-v2-vN.md` (N ≥ 1, sans « brouillon ») ; l'entropie des
graines de la course est l'empreinte de ce fichier-là.

## 1. Question et motivation

**Question.** Sur des fiches dont la qualité est connue par construction (témoins plantés), le protocole v2 des juges —
comparaisons par paires à l'aveugle avec preuve citée, ancres, budget de notables, règle de famille — **discrimine-t-il** les
bonnes fiches des mauvaises, **là où l'ancien protocole sature** (« notable » donné presque partout) ?

**Constat qui motive** (README principal, ligne du « second real round », sha256 du README lu
`a5e6b8622fbd7b319d74a01b9d2208c13a1e89dc17cdc37c4f1d99db6dd4b298`, ligne 125) : au second tour réel du 1er novembre 2026
(Kimi et Argon, 12 fiches), 11 fiches sur 12 « notables » (un juge 12 sur 12, l'autre 11 sur 12), accord brut 0,92, kappa de
Cohen nul. Ces chiffres sont ceux du dépôt public ; la trace agrégée est privée (sha256
`091ff9edefec3faa411ae786a28595c5d3648e1b7aa4c425d290a3e64544338a`), non relue ici.

**Diagnostic** (code cité à l'empreinte `c4c6ab12dc471eef078c116a4205a22d9b498da720ce71e37a0a6edae6c4239b` de
`pole/juges_croises_v53.py`) : (i) « notable » est une conjonction d'items de forme (`lire_verdict`, ligne 48) que toute fiche bien
rédigée satisfait, puisque le proposeur reçoit justement ce gabarit ; (ii) le jugement est absolu, une fiche seule, sans
référence de qualité connue ni plafond au nombre de notables ; (iii) rien n'oblige le juge à toucher le fond : ni dossier de
faits, ni preuve demandée ; (iv) au plafond, le classement (`classement`, lignes 117 à 127) départage par l'identifiant ; (v)
`kappa_cohen` (lignes 133 à 140) rend 1 quand l'accord attendu vaut 1, si bien que deux juges toujours « notable » paraîtraient en
accord parfait (`mesures_v54.kappa_cohen_v54` corrige, la lecture de la course ne l'emploie pas) ; (vi) au second tour, chaque
fiche avait un juge de sa propre famille. Ce diagnostic est un raisonnement sur le code et sur des propriétés connues des juges
fondés sur des modèles de langage (indulgence du jugement absolu, biais de position, préférence pour le texte long et pour sa
propre famille) ; aucun chiffre de la littérature n'est avancé.

**Ce que l'expérience compare.** Les deux protocoles, **sur les mêmes fiches, avec les mêmes juges et la même information** :
pour les lots témoins, l'ancien protocole reçoit sa consigne figée (pièce privée de la course 2), puis le dossier du lot, puis la
fiche ; le v2 reçoit sa consigne figée, le dossier et deux fiches. Sans le dossier, aucun protocole ne pourrait savoir qu'une
loi est fausse ou déjà établie : l'insérer dans l'ancien protocole isole l'effet du protocole de celui de l'information (écart
assumé à la reproduction exacte du second tour, section 10). **Bras sans dossier** (décision de Lazar, GO-2026-11-02-32) : le
juge A juge aussi les 30 témoins d'évaluation par l'ancien protocole **sans dossier** (consigne figée puis fiche seule, octet
pour octet la forme de l'entrée du second tour) ; ce bras sépare l'effet du protocole (v2 contre ancien, même dossier) de l'effet
du dossier sur l'ancien protocole (ancien avec dossier contre ancien sans dossier).

## 2. Hypothèses

- **H1 (l'ancien sature par construction).** Servi avec le même dossier, l'ancien protocole donne « notable » à presque tous
  les témoins, bons comme mauvais : sa part de notables reste haute et ses notes ne séparent pas bons et mauvais.
- **H2 (le v2 discrimine).** Le choix forcé entre deux fiches, adossé à une citation vérifiée de la fiche choisie et du
  dossier, fait remonter les lois vraies et neuves au-dessus des lois fausses, des redites, des affirmations vraies par
  définition, des textes longs sans affirmation réfutable et des prédictions de signe contraire à leur hypothèse.
  **H2b (lecture des tables).** En particulier, les lois fausses — la seule classe que les tables seules réfutent — sont classées
  sous les bonnes lois.
- **H3 (le v2 est fiable).** Sa discrimination se reproduit sur un second tirage (autre graphe de paires, autres ordres,
  autres identifiants), n'est pas pilotée par la position de présentation, et un juge d'une autre famille départage lui aussi
  les paires qui opposent une bonne et une mauvaise fiche.
- **H0, écrites d'avance.** (a) Le v2 ne discrimine pas mieux que le hasard : les juges ne lisent pas le dossier, ou tranchent
  par la forme ; (b) l'ancien ne sature pas sur ces témoins : le plafond du second tour tenait aux fiches réelles (l'ancien ne
  sature pas même sans dossier) ou à l'absence de dossier (il sature sans dossier, pas avec) — le bras sans dossier départage
  les deux branches ; (c) le v2 discrimine mais de façon instable, pilotée par la position, ou propre à un juge.

## 3. Prédictions chiffrées et signées (ouvertes dans les deux sens ; elles ne décident pas l'issue)

Juge A = Argon (`gemini-4-argon`), tirage 1, sur les 30 témoins d'évaluation (15 bons, 15 mauvais), sauf mention. « Aire » =
aire sous la courbe ROC (courbe des taux de vrais et de faux positifs) des notes entre bons et mauvais témoins (égalités comptées
pour moitié).

| | prédiction | justification | sens contraire possible, et ce qu'il dirait |
|---|---|---|---|
| P1 | ancien avec dossier : part de notables ≥ 0,80 | le second tour (11 sur 12) ; les témoins sont rédigés au même standard de forme | < 0,80 : le dossier suffit à l'ancien pour refuser des fiches ; H0(b) |
| P2 | ancien avec dossier : aire ≤ 0,65 | au plafond, presque toutes les notes sont égales | > 0,65 : l'ancien départage avec l'information ; H0(b) |
| P3 | v2 : aire ≥ 0,80 | choix forcé, citation du dossier exigée ; vérifier un nombre contre une table est à la portée d'un juge capable | < 0,80 : le juge ne lit pas la table ou ne la compare pas ; H0(a) |
| P4 | v2 − ancien : différence d'aire ≥ +0,15 | P3 et P2 | < +0,15 : le gain tient à l'information, pas au protocole |
| P5 | v2 : faux notables ≤ 0,10 et vrais notables ≥ 0,30 ; ancien : faux notables ≥ 0,70 | plancher des ancres et budget ; plafond de l'ancien | v2 > 0,10 : le plancher des ancres ne protège pas ; vrais < 0,30 : ancres inversées ou budget trop serré |
| P6 | kappa des paires mélangées (A contre B) ≥ 0,40 ; kappa de l'ancien ≤ 0,20 ou non défini | deux juges qui discriminent s'accordent sur ce qui départage | < 0,40 : la discrimination est propre à un juge (descriptif : sur des paires mélangées, ce kappa vaut à peu près (2p − 1)² pour deux juges indépendants justes à p) |
| P7 | Spearman entre tirages ≥ 0,50 et aire du tirage 2 ≥ 0,80 | plafond de la corrélation de rangs à 0,751 pour deux classes de 15 ordonnées au hasard à l'intérieur (`plafond_spearman_binaire`) | < 0,50 : notes instables même entre classes |
| P8 | part des victoires de la fiche présentée en premier dans [0,40 ; 0,60] et taux de bascule ≤ 0,40 | ordres tirés au hasard ; la bascule mêle biais de position et incertitude sur les paires de même qualité | hors bornes : préférence de position (D5 en tolère plus, section 6) |
| P9 | texte long : rang moyen v2 < 0,5 ; notable à l'ancien | la consigne v2 dit que la longueur ne compte pas ; l'ancien juge la forme | rang ≥ 0,5 : biais de longueur du juge |
| P10 | redites d'une loi établie : rang moyen v2 < 0,5 | la consigne nomme la nouveauté ; les lois établies sont au dossier | ≥ 0,5 : la nouveauté n'est pas vérifiée (classe difficile : la redite est **vraie**) |
| P11 | juge B (Astra), ancien avec dossier : part de notables ≥ 0,80 | même raison que P1 | < 0,80 : le plafond dépend du juge |
| P12 | ancien **sans dossier** (A) : part de notables ≥ 0,80 et aire ≤ 0,65 | le second tour (11 fiches sur 12 « notables », sans dossier) ; sans dossier, aucune fiche ne peut être sue fausse ou redite | < 0,80 : le plafond du second tour ne se reproduit pas sur ces témoins, même dans ses conditions ; H0(b), première branche |
| P13 | effet du dossier sur l'ancien (A) : part de notables avec dossier moins part sans dossier ≥ −0,10 | l'ancien juge la forme ; le dossier change peu ses verdicts | < −0,10 : le dossier suffit à l'ancien pour refuser des fiches ; H0(b), seconde branche |
| P14 | lois fausses contre bonnes (v2, A) : aire ≥ 0,75 | H2b : la table réfute le chiffre affirmé | < 0,75 : le juge ne vérifie pas les nombres ; un succès de D1 viendrait des autres classes |
| P15 | prédictions de signe contraire (classe que la consigne ne nomme pas en propre) : rang moyen v2 < 0,5 | la consigne demande un signe compatible avec le dossier | ≥ 0,5 : le juge ne lit que l'hypothèse (portée, section 10) |
| P16 | juge B, paires mélangées : exactitude ≥ 0,75 | B est un juge capable d'une autre famille | < 0,75 : la discrimination dépend du juge ; avec D6 non tenu, H0(c) |

Le code évalue chacune (`predictions_v2`) ; leur succès ou leur échec est rapporté, jamais lu comme issue.

## 4. Plan

**Matériaux (témoins plantés), gelés avant la course.** `juges_idees_v2.construire_materiaux(20261102)` (jeu « mondes-v2 ») :
**trois mondes** à loi plantée dans le domaine du programme — `monde-1` (agent de code, moniteur qui classe « suspect »),
`monde-2` (agent de navigation, moniteur à score de suspicion), `monde-3` (agent d'assistance qui rédige des courriels et gère
un agenda, moniteur qui classe « hors mandat ») —, chacun de 3 000 épisodes simulés (douze ou treize caractéristiques
indépendantes, alerte tirée selon une loi logistique plantée, avec une interaction), tirés de nouveau jusqu'à ce que le dossier
montre nettement chaque vérité (`contraintes_monde` : effet vrai ≥ 5 points entre niveaux extrêmes, effet nul ≤ 1,5 point entre
niveaux, y compris pour une caractéristique graduée sans effet, interaction ≥ 6 points ; tentatives retenues : 0, 6 et 10).
Chaque monde donne un **dossier** (contexte, deux lois déjà établies, deux tables de taux à lignes numérotées D01…) et **douze
fiches** au format du tour fermé (titre, hypothèse, prédiction, signe, métrique, test de mort) :

| rôle | classe | monde-1 | monde-2 | monde-3 | qualité |
|---|---|---|---|---|---|
| évaluation | loi vraie absente des lois établies, chiffres honnêtes du dossier (dont une décroissante et une de deux groupes sur une caractéristique peu plausible a priori) | 5 | 5 | 5 | bonne |
| évaluation | loi fausse bien rédigée (effet affirmé de 6 à 8 points, la table montre ≤ 1,5) : graduée sur une caractéristique ordinale plausible, ou de deux groupes | 2 | 2 | 3 | mauvaise |
| évaluation | redite d'une loi établie, en d'autres mots (vraie, chiffres honnêtes) | 1 | 1 | 1 | mauvaise |
| évaluation | prédiction de signe contraire à une hypothèse vraie (hypothèse décroissante, prédiction croissante) | 1 | 1 | 1 | mauvaise |
| évaluation | affirmation vraie par définition (le moniteur alerte quand il classe « suspect ») | 1 | 0 | 0 | mauvaise |
| évaluation | texte long sans affirmation réfutable | 0 | 1 | 0 | mauvaise |
| ancre bonne | loi vraie neuve graduée | 1 | 1 | 1 | bonne |
| ancre mauvaise | loi fausse de deux groupes, caractéristique plausible | 1 | 1 | 1 | mauvaise |

**Gabarits, a priori et sens (contre-lecture, B1).** Dans les matériaux du brouillon 1 (deux mondes ; empreinte `c3eeb559…`), les
gabarits n'étaient pas communs aux classes : toutes les lois fausses étaient des comparaisons de deux groupes sur une
caractéristique binaire sans effet et peu plausible a priori, huit bonnes fiches sur dix des lois graduées ou des interactions ;
un juge scripté qui ne lit **aucune** table tenait D1 dans 16 courses à blanc sur 20. Les matériaux de ce texte sont
rééquilibrés : dans chaque monde, au moins une loi fausse au gabarit gradué sur une caractéristique ordinale sans effet et
plausible a priori ; une bonne loi au gabarit de deux groupes sur une caractéristique binaire d'effet vrai mais peu plausible a
priori (heure de lancement, taille de l'écran, police de caractères) ; une bonne loi décroissante et une mauvaise dont
l'hypothèse décroît (signe contraire), pour que le sens de la loi ne sépare pas les classes ; une caractéristique d'effet vrai
reste sans fiche ; chaque caractéristique porte une étiquette d'a priori (plausible ou non) fixée dans le code avant toute course.
**Contrôle de forme** (`controle_forme`, avant tout appel) : aire de six indices entre bons et mauvais témoins d'évaluation, chacune
dans [0,35 ; 0,65], sinon refus — longueur 0,624, nombre de chiffres 0,531, gabarit gradué ou interaction
0,500, caractéristique binaire 0,467, a priori plausible 0,520, loi croissante 0,527 (les matériaux du
brouillon 1, reconstruits par ce code — jeu « mondes-brouillon1 » : mêmes dossiers, mêmes classes, cinq champs de texte différents, deux écarts écrits arrondis comme les taux affichés, deux seuils de prédiction, « dix » au lieu de « 10 » dans les deux textes longs —, sont refusés : gabarit 0,800, a priori 0,850, caractéristique binaire
0,300). **Contrôle de diagnosticité** (`controle_diagnosticite`, avant tout appel) : le plan v2 du juge A au tirage 1 (graphe,
ordres, identifiants, entrées servies, lecture des réponses, Bradley et Terry) est joué sur 20 graines fixes
(`Graines(20261102000 + k)`) par six juges scriptés **de forme**, qui ne lisent rien du dossier (préférences lexicographiques
parmi : a priori de la caractéristique nommée, gabarit, sens de la loi, longueur, brièveté, nombre de chiffres) : chacun doit tenir
D1 dans au plus 2 courses sur 20 et rester sous une aire moyenne de 0,62 ; et par un juge **« dossier sans tables »** (la forme,
plus les lois établies du dossier, son contexte et la cohérence entre hypothèse et prédiction) : il doit tenir D1b (lois fausses
contre bonnes) dans au plus 2 courses sur 20 — sinon refus. Sur les matériaux de ce texte : conformes — les six juges de forme tiennent D1 dans 0 ou 1 course sur 20 (aires moyennes de 0,407 à 0,593, table ci-dessous), le juge « dossier sans tables » tient D1b dans 0 course sur 20 (aire moyenne des bonnes lois contre les lois fausses 0,457). Sur les matériaux du
brouillon 1 (artefact de l'essai) : refusés — juges de forme « a priori, gabarit, sens » : D1 dans 18 courses sur 20 (aire moyenne 0,819), « gabarit, a priori, sens » : 19 sur 20 (0,819), « sens, gabarit, a priori » : 7 sur 20 (0,701) ; juge « dossier sans tables » : D1b dans 17 courses sur 20. Le juge « dossier sans tables » tient D1 dans 15 courses sur 20 (aire
moyenne 0,699) : **D1 mesure la lecture du contenu (dossier ou fiche), pas la lecture des tables** ; c'est D1b qui la
mesure (section 6). `verifier_materiaux` relit la vérité de chaque fiche sur les tables (chiffres affirmés, sens de la prédiction,
champ « signe »). Empreinte des matériaux : bloc `plan-gele` (`materiaux_sha256`) ; le lanceur les reconstruit et refuse tout écart.
Gabarits écrits par un modèle de la famille Claude : aucun juge de cette famille sur les témoins.

**Contrôle de diagnosticité, chiffres** (`controle_diagnosticite`, graines `Graines(20261102000 + k)`, k = 0…19 ; à recalculer sur `construire_materiaux(20261102)` et sur `construire_materiaux(20261102, "mondes-brouillon1")` ; sortie du rédacteur gardée hors dépôt, empreinte au rapport) :

| juge scripté (ne lit aucune table) | ce texte : aire moyenne (maximum) | D1 sur 20 | D1b sur 20 | brouillon 1 : aire moyenne | D1 sur 20 | D1b sur 20 |
|---|---|---|---|---|---|---|
| forme : a priori, puis gabarit, puis sens | 0,524 (0,627) | 0 | 0 | 0,819 | 18 | 20 |
| forme : gabarit, puis a priori, puis sens | 0,542 (0,658) | 0 | 0 | 0,819 | 19 | 20 |
| forme : sens, puis gabarit, puis a priori | 0,518 (0,636) | 0 | 0 | 0,701 | 7 | 3 |
| forme : longueur | 0,593 (0,698) | 1 | 2 | 0,389 | 0 | 1 |
| forme : brièveté | 0,407 (0,520) | 0 | 0 | 0,612 | 1 | 0 |
| forme : nombre de chiffres | 0,523 (0,609) | 0 | 2 | 0,410 | 0 | 0 |
| dossier sans tables | 0,699 (0,844) | 15 | 0 | 0,958 | 20 | 17 |

Seuils (juges de forme : D1 au plus 2 fois sur 20 et aire moyenne au plus 0,62 ; juge « dossier sans tables » : D1b au plus 2 fois sur 20) fixés pendant la rédaction, après les premières mesures (section 9). Le juge sans tables de la contre-lecture (sa fonction de score reprise telle quelle, listes étendues aux trois mondes) rejoué sur ce code : matériaux de ce texte, aire moyenne 0,545 et D1 tenu 0 fois sur 20 (0,533 et 0 avec l'a priori) ; matériaux du brouillon 1 reconstruits, 0,823 et 18 fois sur 20 (0,865 et 20 avec l'a priori). **Limite connue** : le contrôle de forme compare bons et mauvais témoins, pas le sous-ensemble de D1b ; entre les 15 bonnes lois et les 7 lois fausses, la longueur a une aire de 0,657 et le nombre de chiffres 0,638 (les quatre autres indices entre 0,386 et 0,543) ; les juges « longueur » et « chiffres » tiennent D1b 2 fois sur 20 (aire moyenne des lois fausses 0,637 et 0,654). T1 se lit avec cette réserve.

**Juges** (GO-2026-11-02-32, qui nomme les deux et exclut Kimi : trop cher et trop lent pour des comparaisons par paires, 5 appels
réussis sur 621 à A1, `registres/etat.md` du dépôt de travail, ligne 6, sha256 lu `f425a6842d3d711f419670517895f4a0c609b23b60d37873cdf4f31633f637cd`) :
A = Argon (`gemini-4-argon`, famille gemini, commande externe, relais 8805, à un seul fil) ; B = Astra (`gpt-6-astra`, famille gpt,
commande 8807). Chacun passe par sa commande de la configuration (`demonstrations/ideation_v8.adaptateurs_reels_v56`, commande
externe v56 avec modèle servi exigé) ; budget par appel = `plafonds_session.juge`, au moins deux fois le prix de plan le plus haut
(1,00 USD, refus sinon) ; modèle servi contrôlé à chaque appel (A2), y compris quand la commande v56 rend le statut « refus » pour un
autre modèle servi (section 8). **Épreuve de la commande Astra 8807** (elle n'a jamais servi ; elle est chez la machine qui porte les
clés ; à faire avant le scellement par session-depot, et à recopier ici : nombre d'appels, modèle servi, coût et durée par appel,
codes de sortie vus, budget de session minimal accepté, réglages `--effort` et `--reflexion` des commandes Astra et Argon tels que
la configuration les fixe) : `<<EPREUVE_ASTRA_8807>>`.

**Étapes** (fixées par le code, `etapes_v2` ; structure citée par le bloc `plan-gele`, valeurs fixes recopiées), dans l'ordre :

| phase | juge | protocole | fiches ou paires | appels | règle de projection (section 8) |
|---|---|---|---|---|---|
| décisive A | A | ancien avec dossier, tirage 1 | 30 témoins d'évaluation, une fiche par appel | 30 | toutes les étapes de la phase doivent tenir dans la part de A, sinon arrêt |
| décisive A | A | v2, tirage 1 | par lot, graphe 3-régulier tiré au hasard sur les 12 fiches (18 paires), **deux ordres** par paire | 108 | idem |
| décisive A | A | v2, tirage 2 | nouveau graphe, nouveaux ordres, nouveaux identifiants | 108 | idem |
| décisive B | B | v2, tirage 1 | paires **mélangées** (une bonne, une mauvaise) du graphe du tirage 1 de A, au plus 13 par lot, un ordre tiré indépendamment de ceux de A | 24 à 36 sur 60 graines simulées ; 32 à la graine 20261102 ; au plus 39 | étape par étape (les comparaisons de B passent avant son ancien protocole) |
| décisive B | B | ancien avec dossier, tirage 1 | 30 témoins d'évaluation | 30 | étape par étape |
| sans dossier (A) | A | ancien **sans dossier** | les 30 témoins d'évaluation, entrée de la forme du second tour (consigne figée puis fiche) | 30 | toute la phase doit tenir, sinon non jouée |
| réel (descriptif) | B ; A | ancien | fiches réelles où le juge est admis (règle de famille), sans dossier | ≤ 13 ; ≤ 13 | idem |
| réel (descriptif) | B ; A | v2 | un cycle sur ces fiches, un ordre | ≤ 13 ; ≤ 13 | idem |

Le juge B ne voit que des paires mélangées : son rôle est de **départager lui aussi** ce qui départage, et son budget ne couvre pas
tout le graphe ; ce choix de paires par les étiquettes connues n'existe qu'en validation (en production, les paires ne se
choisissent pas sur la qualité ; déclaré). Les ancres sont servies à l'aveugle comme les autres fiches.

**Lot réel.** Les 12 fiches du second tour, privées, tenues par la session qui détient les clés, sont une pièce de la
configuration (`piece_lot_reel`), avec la question de la course (`piece_question`), servie comme dossier du v2 ; elles ne sont lues
que descriptivement (aucun seuil, aucune issue) ; les fusions comptent les familles de leurs parents (toutes, si elles ne sont pas
dites) ; un identifiant de la forme des témoins (« monde-k-nn ») est refusé. Elles passent la garde A4 de la configuration avant
tout appel ; sinon refus.

**Protocole v2, pour chaque comparaison** : consigne figée v2 (`CONSIGNE_PAIRE_V2`, empreinte au bloc `plan-gele`, inchangée depuis
le brouillon 1), dossier, deux fiches anonymes « présentée en premier » et « présentée en second ». Réponse : `{"comparaison":
{preferee, critere, citation_fiche, citation_dossier}}` ; valide seulement si l'identifiant est l'un des deux, le critère dans la
liste (vérité, nouveauté, contenu, prédiction), la citation de la fiche trouvée telle quelle (après normalisation typographique)
dans la fiche **choisie** et **absente de l'autre**, de 15 à 300 caractères, et, quand le dossier a des lignes de faits, la
citation du dossier trouvée telle quelle (10 à 300 caractères). Une comparaison nulle est comptée, jamais lue comme victoire.

**Note continue** : force de Bradley et Terry avec effet de position (`ajuster_bt` : P(première gagne) = σ(θ₁ − θ₂ + γ),
crêtes 0,5 et 0,5, forces centrées, arrondies à 10⁻⁹), ajustée par lot sur les comparaisons valides d'un juge et d'un tirage.
**Verdict** (`verdicts_lot`) : « notable » = parmi les ⌈0,25 × 10⌉ = 3 premières fiches d'évaluation du lot **et**
strictement au-dessus du milieu des forces des deux ancres ; ancres inversées → aucun notable dans le lot ; égalité à la limite
du budget → aucune des fiches à égalité. **Ancien protocole** : `juges_croises_v53.lire_verdict` (items de la configuration,
« notable » = tous vrais), note continue = part d'items vrais.

**Graines (R9).** `graines_v53.Graines(entropie)` : `SeedSequence(entropie, spawn_key=(cle_de_tache(tâche),))`, entropie =
`int(SHA-256 du texte scellé, 16)` ; tâches : `graphe|<lot>|tirage-<t>`, `ordres|<lot>|tirage-<t>|<juge>`, `paires-b|<lot>`,
`ordre-ancien|<lot>|<juge>|tirage-<t>`, `ordre-ancien-sans-dossier|<lot>|<juge>`, `anonymisation|<juge>|tirage-<t>|<lot>|<fiche>`,
`anonymisation-sans-dossier|<juge>|<lot>|<fiche>`, `graphe|reel|<juge>`, `ordres|reel|<juge>` ; matériaux : `Graines(20261102)`,
tâches `materiaux|<monde>|tentative-<k>` et `materiaux|<monde>|fiche-<k>` ; contrôle de diagnosticité : `Graines(20261102000 + k)`,
k = 0…19 (propriété des matériaux, fixée). Tout est écrit au manifeste de la course.

**Lancement** (après scellement, épreuve d'Astra et configuration) :
`python3 -I -B demonstrations/validation_juges_idees_v2.py SORTIE_NEUVE --preenregistrement prereg/preenregistrement-juges-idees-v2-vN.md --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go registres/go.md --go GO-2026-11-02-32`
(d'abord avec `--verifier-seulement` : toutes les gardes, contrôles des matériaux, plafonds accusés, aucun appel, aucune écriture
dans la sortie).

<!-- plan-gele : début -->
```
juge_a: etiquette=juge-a, fournisseur=argon, modele=gemini-4-argon, famille=gemini, prix_usd=0.062, secondes=8-40
juge_b: etiquette=juge-b, fournisseur=astra, modele=gpt-6-astra, famille=gpt, prix_usd=0.5, secondes=10-120
correspondance_auteurs: kimi=kimi, argon=gemini
graine_materiaux: 20261102
materiaux_sha256: 59737a16d4f5250398ac52bc5b1e26952f356cd26fbafa9b1ed9a28afac5284d
consigne_paire_sha256: 6978f0a4778edd87f9059606420577c167a1ff8db2053ab56507d20a355039b4
piece_consigne_ancienne: consigne_juge
piece_question: question_course_2
piece_lot_reel: lot_reel_juges_idees_v2
plafond_usd: 60
plafond_juge_a_usd: 24
plafond_juge_b_usd: 36
duree_max_h: 48
configuration_sha256: <<CONFIGURATION_SHA256>>
go: GO-2026-11-02-32
version_plan: validation-juges-idees-v2-plan-2
jeu_de_mondes: mondes-v2
temoins_par_classe: 15
degre: 3
tirages_a: 2
degre_reel: 2
paires_b_max_par_lot: 13
part_budget: 0.25
ridge_forces: 0.5
ridge_position: 0.5
seuils: alpha=0.05, alpha_reproduction=0.1, plafond_ancien_min=0.8, delta_aire_min=0.15, biais_premier_max=0.15, validite_min=0.85, presents_ancien_min=27, pertes_max_part=0.15, paires_b_min=20
politique_relais: attentes_s=15,30,60,120,300; panne_h=6; reprises_max=2; echecs_couteux_max=5; pertes_max_part=0.15; cout_plancher_usd=1e-05
```
<!-- plan-gele : fin -->

`consigne_paire_sha256` est l'empreinte de la consigne v2 (inchangée) ; `materiaux_sha256` est l'empreinte des matériaux
rééquilibrés de ce brouillon ; si la contre-lecture fait changer les matériaux ou la consigne, elles changent, et le lanceur refuse
l'écart (à recalculer au scellement, avec le bloc de la section 11). Plafond : exactement 60 USD (GO-2026-11-02-32) ; parts : 24 USD
pour Argon, 36 USD pour Astra, au large du pire cas requis du plan (section 12). `duree_max_h` est une garde contre une boucle
folle, jamais une coupe de la mesure (règle prise sur les mots de Lazar du 2 novembre 2026, 18:26 UTC) : 48 heures, huit fois la
durée haute du devis. `politique_relais` gèle les valeurs de la section 8. Les noms de pièces (`consigne_juge`,
`question_course_2`, `lot_reel_juges_idees_v2`) sont ceux que la configuration devra porter ; la configuration est préparée par la
session qui tient les clés.

## 5. Métriques, taille et puissance

**Métriques** (`mesurer`, depuis le seul journal) : aire et test de Mann et Whitney unilatéral (loi exacte sans égalité,
approximation normale corrigée sinon) par protocole, par juge et par tirage ; aire des bonnes lois contre les lois fausses (D1b) ;
différence appariée des aires v2 − ancien (DeLong, unilatéral ; variance nulle → p = 0 si la différence est positive, dit) ; bras
sans dossier (A) : part de notables, aire et Mann et Whitney, effet du dossier sur l'ancien (part de notables et aire, avec dossier
moins sans dossier ; DeLong bilatéral, descriptif) et gain total (aire v2 moins aire de l'ancien sans dossier ; DeLong unilatéral, descriptif) ; part de
notables, faux notables (mauvais témoins notables), vrais notables ; kappa de Cohen sur les verdicts de l'ancien (convention v54 :
non défini si l'accord attendu vaut 1) ; **exactitude du juge B** sur ses paires mélangées (part des comparaisons valides où il
choisit la bonne fiche, test binomial unilatéral exact) ; kappa des choix par paire entre A et B sur ces paires (chaque jugement de
A, un par ordre, en regard du jugement de B ; issue orientée par l'empreinte de l'identifiant, sans lien avec la classe ; le juge B
ne voyant que des paires mélangées, il n'existe aucun kappa « sur les paires de même qualité ») ; fidélité test-retest (aire du
tirage 2 ; Spearman entre forces des deux tirages, avec son plafond binaire 0,751) ; biais de position (part des
victoires de la première présentée sur les deux tirages de A, taux de bascule compté par tirage et par paire, effet γ par lot) ;
part des comparaisons valides et motifs ; rang centile moyen par classe ; complétude (appels prévus, répondus, perdus
définitivement, non joués, par phase et par juge) ; pertes, attentes et dépense du relais par juge (coûts connus, inconnus,
incidents).

**Taille.** 30 témoins d'évaluation (15 bons, 15 mauvais : GO-2026-11-02-32) dont 7 lois fausses ; 6 ancres. **Puissance**
(modèle binormal : mauvais ~ N(0, 1), bons ~ N(√2·Φ⁻¹(aire), 1) ; test de Mann et Whitney unilatéral, loi exacte ; 20 000
répétitions par case, graine 20261102 ; reproduire :
`python3 -I -B demonstrations/validation_juges_idees_v2.py --puissance --graine 20261102 --repetitions 20000 --graines-plan 60`,
sortie gardée hors dépôt, empreinte au rapport) :

**D1** (Mann et Whitney unilatéral exact au niveau 0,05 ; puissance = part des répétitions où D1 est tenu) :

| bons contre mauvais | U critique (aire critique) | niveau exact | aire 0,50 | aire 0,65 | aire 0,70 | aire 0,75 | aire 0,80 | aire 0,85 | aire 0,90 |
|---|---|---|---|---|---|---|---|---|---|
| 10 contre 10 | 73 (0,730) | 0,0446 | 0,045 | 0,284 | 0,440 | 0,611 | 0,782 | 0,910 | 0,979 |
| 12 contre 12 | 102 (0,708) | 0,0444 | 0,044 | 0,329 | 0,501 | 0,689 | 0,854 | 0,951 | 0,992 |
| 14 contre 14 | 135 (0,689) | 0,0469 | 0,049 | 0,380 | 0,571 | 0,757 | 0,900 | 0,976 | 0,998 |
| 15 contre 15 | 153 (0,680) | 0,0488 | 0,053 | 0,410 | 0,611 | 0,791 | 0,927 | 0,985 | 0,999 |
| 16 contre 16 | 173 (0,676) | 0,0469 | 0,050 | 0,417 | 0,628 | 0,815 | 0,938 | 0,988 | 1,000 |
| 18 contre 18 | 215 (0,664) | 0,0485 | 0,050 | 0,459 | 0,683 | 0,856 | 0,960 | 0,994 | 1,000 |
| 20 contre 20 | 262 (0,655) | 0,0482 | 0,047 | 0,500 | 0,723 | 0,888 | 0,973 | 0,997 | 1,000 |

**D4** (tirage 2, niveau 0,10) **et D1 avec D4** (tirages indépendants de même aire vraie), à 15 contre 15 :

| à 15 contre 15 | aire 0,50 | aire 0,65 | aire 0,70 | aire 0,75 | aire 0,80 | aire 0,85 | aire 0,90 |
|---|---|---|---|---|---|---|---|
| D4 (U ≥ 145, aire ≥ 0,644, niveau exact 0,0936) | 0,094 | 0,544 | 0,736 | 0,880 | 0,964 | 0,994 | 1,000 |
| D1 et D4 | 0,004 | 0,223 | 0,448 | 0,697 | 0,894 | 0,979 | 0,998 |

**D1b** (15 bonnes lois contre 7 lois fausses ; U ≥ 77 sur 105, aire ≥ 0,733, niveau exact 0,0455) :

| aire 0,50 | aire 0,70 | aire 0,75 | aire 0,80 | aire 0,85 | aire 0,90 |
|---|---|---|---|---|---|
| 0,046 | 0,426 | 0,602 | 0,771 | 0,900 | 0,975 |

**D6** (exactitude du juge B, test binomial unilatéral exact au niveau 0,10 ; puissance exacte, sans simulation) :

| comparaisons valides de B | k critique | niveau exact | p = 0,65 | p = 0,70 | p = 0,75 | p = 0,80 | p = 0,85 | p = 0,90 |
|---|---|---|---|---|---|---|---|---|
| 20 | 14 | 0,0577 | 0,417 | 0,608 | 0,786 | 0,913 | 0,978 | 0,998 |
| 24 | 16 | 0,0758 | 0,526 | 0,725 | 0,879 | 0,964 | 0,994 | 1,000 |
| 28 | 18 | 0,0925 | 0,616 | 0,809 | 0,932 | 0,985 | 0,998 | 1,000 |
| 32 | 21 | 0,0551 | 0,551 | 0,772 | 0,920 | 0,983 | 0,998 | 1,000 |
| 36 | 23 | 0,0662 | 0,629 | 0,837 | 0,954 | 0,993 | 1,000 | 1,000 |
| 39 | 24 | 0,0998 | 0,736 | 0,906 | 0,980 | 0,998 | 1,000 | 1,000 |

**Le plan joué par des juges scriptés** (« bruite », sans biais de position, juste avec la probabilité donnée sur une paire de
qualités différentes et au hasard sur une paire de même qualité ; ancien protocole indulgent ; même juge A et B ; 60 graines de
course par ligne ; même commande) — c'est la puissance du **plan** (graphe 3-régulier, deux ordres, ancres, tirage 2, paires
mélangées de B), pas celle d'un juge réel, dont l'exactitude par comparaison est inconnue :

| exactitude par comparaison | issues (sur 60) | D1 | D4 | D5 | D6 | D1b | aire v2 moyenne (décile bas) | exactitude de B moyenne | paires de B (min ; moyenne ; max) |
|---|---|---|---|---|---|---|---|---|---|
| 0,60 | I3 43, I4 17 | 0,283 | 0,600 | 1,000 | 0,333 | 0,167 | 0,630 (0,496) | 0,596 | 24 ; 29,8 ; 36 |
| 0,65 | I1 11, I3 23, I4 26 | 0,617 | 0,750 | 1,000 | 0,517 | 0,383 | 0,699 (0,569) | 0,657 | 24 ; 29,8 ; 36 |
| 0,70 | I1 37, I3 10, I4 13 | 0,833 | 0,933 | 1,000 | 0,817 | 0,617 | 0,762 (0,653) | 0,713 | 24 ; 29,8 ; 36 |
| 0,75 | I1 49, I3 6, I4 5 | 0,900 | 0,967 | 1,000 | 0,950 | 0,767 | 0,818 (0,711) | 0,755 | 24 ; 29,8 ; 36 |
| 0,80 | I1 55, I3 3, I4 2 | 0,950 | 0,983 | 1,000 | 0,983 | 0,900 | 0,872 (0,782) | 0,809 | 24 ; 29,8 ; 36 |
| 0,85 | I1 59, I4 1 | 1,000 | 1,000 | 1,000 | 0,983 | 0,983 | 0,914 (0,840) | 0,858 | 24 ; 29,8 ; 36 |
| 0,95 | I1 60 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,976 (0,951) | 0,944 | 24 ; 29,8 ; 36 |

Lecture. À 15 contre 15, D1 seul a une puissance de 0,927 à une aire vraie de 0,8 (au moins 0,9, comme le demande GO-2026-11-02-32 ; 0,782 à 10 contre 10) et de 0,985 à 0,85 ; D1 avec D4, 0,894 à 0,8 (juste sous 0,9) et 0,979 à 0,85. Le plan joué conclut I1 dans 49 courses sur 60 quand le juge est juste à 0,75 par comparaison (aire v2 moyenne 0,818), 55 sur 60 à 0,80, 59 sur 60 à 0,85 (brouillon 1, à 10 contre 10 et D6 au kappa : 8 sur 40 à 0,75, 32 sur 40 à 0,85) ; à 0,60, I3 dans 43 courses sur 60 : un juge à peine meilleur que le hasard donne « ne fait pas mieux ». La variance du plan creux (graphe 3-régulier, ancres, deux ordres) s'ajoute à celle de l'échantillon de témoins : le décile bas de l'aire v2 est à 0,711 quand la moyenne vaut 0,818. D6 est mesurable dans toutes les courses simulées (24 à 36 paires mélangées pour B, au moins 20 exigées) ; D5 est tenu partout (juges sans biais de position). D1b, à 15 contre 7, est moins puissant (0,771 à une aire de 0,8) : un T0 ne prouve pas que les tables ne sont pas lues. Sortie : `puissance-b2.json` du rédacteur, hors dépôt, sha256 `6026cdc3664d627c929cdacf26faca66903b7b1d8e662d7e377ed32612d40fea`.

## 6. Critères de lecture gelés et issues écrites d'avance

Calculés par `lire_validation` sur les mesures, sans autre lecture. Juge A, témoins d'évaluation, sauf mention.

| critère | définition | seuil |
|---|---|---|
| D1 | aire v2, tirage 1 : Mann et Whitney unilatéral exact | p < 0,05 (à 15 contre 15 sans égalité : U ≥ 153 sur 225, aire ≥ 0,68) |
| D2 | part de notables de l'ancien avec dossier, tirage 1 (« l'ancien sature ») | ≥ 0,80 |
| D3 | aire v2 − aire ancien (tirage 1), DeLong unilatéral | ≥ 0,15 et p < 0,05 |
| D4 | la discrimination se reproduit au tirage 2 : Mann et Whitney unilatéral exact | p < 0,10 (reproduction d'un effet que D1 a établi ; aire ≥ 0,644 à 15 contre 15) |
| D5 | biais de position : écart de la part des victoires de la première présentée à 0,5 (deux tirages) | ≤ 0,15 (au plus 30 % des comparaisons tranchées par la position) |
| D6 | juge B : exactitude sur ses paires mélangées, test binomial unilatéral exact contre 0,5 | p < 0,10 ; « non mesuré » sous 20 comparaisons valides de B ou sous 0,85 de validité |
| D7 | part de notables de l'ancien **sans dossier** (bras sans dossier : « l'ancien sature dans les conditions du second tour ») | ≥ 0,80 ; « non mesuré » si le bras rend moins de 27 verdicts lisibles sur 30 |
| D1b | aire v2 des 15 bonnes lois contre les 7 lois fausses (tirage 1) : Mann et Whitney unilatéral exact | p < 0,05 (qualificatif : lecture des tables) |

**Validité de l'instrument** (sinon I0) : phase décisive de A allée à son terme (chaque appel prévu répondu ou perdu
définitivement selon la règle de la section 8) ; au plus 15 % de ses appels prévus perdus définitivement par le relais (jamais
comptés comme réponses du juge), sinon I0 « infrastructure » ; part des comparaisons valides de A ≥ 0,85 à chaque tirage (sur les
réponses ; les pertes n'y entrent pas) ; au moins 27 verdicts lisibles de l'ancien avec dossier sur 30.

**Issues, dans cet ordre :**
- **I0 — non jugeable** : la validité ne tient pas (ou arrêt de la course dans la phase décisive de A). Aucune conclusion sur les
  protocoles ; suite : diagnostic de l'instrument (relais, consigne, citations), nouveau texte.
- **I3 — le v2 ne fait pas mieux au seuil gelé** : D1 non tenu (à 15 contre 15, une aire vraie de 0,8 laisse D1 non tenu dans 7 % des tirages, une aire de 0,9 dans 0,1 % : I3 exclut une aire vraie de 0,9, pas une aire de 0,8 ; section 5). I3a si D2 tenu (les deux protocoles échouent :
  l'outil n'est pas la bonne réponse ou les juges ne lisent pas le dossier) ; I3b sinon (l'ancien n'est même pas au plafond). Suite :
  ne pas adopter le v2 ; examiner les réponses brutes (critère, citations) avant toute retouche.
- **I4 — le v2 discrimine mais n'est pas fiable** : D1 tenu et l'un de D4, D5, D6 (mesuré) non tenu ; les critères manquants sont
  nommés. Suite : pas d'adoption en l'état ; plus de comparaisons ou autre juge, sur nouveau texte.
- **I1 — le v2 discrimine là où l'ancien sature** : D1, D4, D5, D6 (ou non mesuré) tenus et D2 tenu ; I1a si D3 tenu (gain mesuré
  sur l'ancien), I1b sinon. Suite : proposer à Lazar l'adoption du v2 pour le prochain tour (nœud : modification de l'instrument),
  avec les réserves de la section 10.
- **I2 — le v2 discrimine, l'ancien ne sature pas ici** : comme I1 mais D2 non tenu ; I2a / I2b selon D3. Suite : la lecture du
  bras sans dossier dit quelle branche de H0(b) tient (S1 : l'information manquait ; S3 : les témoins ne reproduisent pas le
  plafond du second tour) ; aucune conclusion sur les fiches réelles.

**Lecture du bras sans dossier** (gelée ; jointe à l'issue, ne la change jamais) : S0 « non mesuré » si D7 n'est pas mesuré ;
S1 « le dossier lève le plafond de l'ancien » si D7 est tenu et D2 non tenu ; S2 « l'ancien sature avec et sans dossier » si D7
et D2 sont tenus ; S3 « l'ancien ne sature pas même sans dossier » si D7 n'est pas tenu (avec D2 tenu, l'incohérence est dite en
réserve). Descriptifs joints : effet du dossier sur l'ancien et gain total (section 5).

**Lecture des tables** (gelée ; jointe, ne change jamais l'issue) : T1 si D1b est tenu (« lecture des tables établie ») ; T0 s'il ne
l'est pas ; T- s'il n'est pas mesurable ou si l'issue est I0. Un I1 ou un I2 avec T0 dit que la discrimination vient des classes
lisibles sans les tables (redites, définition, texte long, signe contraire), pas de la vérification des nombres.

**Réserves écrites d'avance** : D6 non mesuré → « accord du juge B non mesuré » joint à I1, I2, I4 ; tout juge arrêté (panne, part,
réponses inexploitables) → nommé, avec la phase et ce qui n'a pas été joué ; part du premier entre 0,10 et 0,15 d'écart à 0,5 →
« préférence de position modérée, absorbée par les deux ordres » ; S3 avec D2 tenu → incohérence dite.

## 7. Audit de symétrie (R4), écrit d'avance

Déclencheurs (`audit_symetrie`), symétriques : aire v2 ≥ 0,98 ou ≤ 0,55 ; Spearman ≥ 0,98 ou ≤ 0,30 ; kappa des paires ≥ 0,90
ou ≤ 0 ; exactitude de B ≥ 0,98 ou ≤ 0,55 ; part de notables de l'ancien = 1 ou ≤ 0,20 ; aucune bascule sur au moins 30 paires vues
dans les deux ordres, ou bascule ≥ 0,75 ; et, pour l'instrument, plus de 5 % de pertes définitives dans une phase, ou un juge
arrêté. Un déclencheur, quel que soit son sens, impose **la même liste** de vérifications, faite par un lecteur neuf avant que
l'issue ne soit lue : recalcul indépendant depuis le journal scellé ; six réponses brutes tirées au hasard par juge et par
protocole ; garde A4 rejouée sur chaque entrée (aucune étiquette de classe, de rôle, d'auteur) ; modèle servi conforme à chaque
appel et appels répondus et pertes égaux au plan, cause par cause ; empreinte des matériaux et contrôles de forme et de
diagnosticité rejoués ; ordres de présentation conformes ; résultat par classe (un résultat porté par une seule classe, par
exemple les textes longs, est dit) ; pertes et attentes du relais relues (aucune perte lue comme une réponse ; reprises dans la
borne). L'issue n'est pas changée par l'audit ; ses constats sont des réserves.

## 8. Liste d'arrêt et règles du relais (chaque garde essayée sur un cas sain et un artefact, R5 ; essais nommés au rapport)

- **Avant tout appel et toute écriture (code 2)** : texte hors du dossier `prereg/` ou d'un autre nom, brouillon, non scellé, à
  marqueur, code ≠ code gelé, fermeture incomplète ; plan non conforme (clés, valeurs fixes dont la politique du relais, consigne v2
  ≠ code, plafond > 60 USD — le GO exige ensuite le montant exact —, parts non positives ou hors du plafond, durée maximale nulle
  ou négative, juges d'une même étiquette, famille ou relais, juge de la famille des gabarits) ; graine ou option de plan en ligne de
  commande ; configuration d'une autre empreinte ; GO autre, absent, d'un autre montant, d'un autre type, échu ou révoqué ; variable
  de clé dans l'environnement ; budget par appel sous deux fois le prix de plan le plus haut ; matériaux d'une autre empreinte, vérité
  connue non établie, forme qui sépare les classes (six indices), classement possible sans les tables (diagnosticité), étiquette
  interdite ; pièce absente ou altérée ; lot réel qui ne passe pas la garde A4 ; consigne figée de l'ancien juge refusée par la garde
  A4 des témoins ; relais absent ; dépense requise (phases décisives et bras sans dossier, au prix du plan) au-dessus de la part d'un
  juge ou du plafond ; durée haute du devis au-dessus de 48 heures ; porte de plafond qui n'accuse pas sa part.
- **Statuts du relais, jamais lus comme une réponse du juge** (`classer_resultat`, `appeler`) :
  - modèle servi absent ou différent sur une réponse « ok », ou statut « refus » que la commande v56 rend pour un autre modèle servi
    (événements `commande.modele_servi`, `commande.modele_servi_absent`, `commande.modele_demande_inconnu`) : **arrêt de la course
    au premier appel** (A2 : aucune bascule sans mot de Lazar) ;
  - refus du modèle lui-même (`commande.refus`) : réponse du juge, **inexploitable** (comparaison nulle ou verdict illisible), jamais
    une victoire, jamais reprise ;
  - **rien d'envoyé** (code 3 relais injoignable, ou code 4 refus avant envoi — plafond de session, registre, 402, 429 —, au coût
    plancher : 10⁻⁶ USD déclaré par la commande, lu « rien d'envoyé » jusqu'à 10⁻⁵ USD) : **le même appel est repris après attente** (15, 30, 60, 120 puis 300 s), sans limite par appel, jusqu'à
    ce que le juge soit déclaré **en panne** : 6 heures sans aucune réponse ;
  - **échec coûteux** (code 3 après envoi, code 5 réponse non conforme, code 6 ou délai de la commande, commande muette au plafond de
    session compté, appel facturé au-dessus du plafond de session, tout autre échec) : l'appel est **perdu**, son coût compté (jamais
    dans le prix observé), puis **repris en fin d'étape** (même entrée, mêmes identifiants), au plus deux fois ; au-delà, **perte
    définitive** ; cinq échecs coûteux de suite d'un juge : juge **en panne** ;
  - **règle écrite d'avance pour les comparaisons perdues** : une perte définitive manque au journal des réponses, comme une
    comparaison nulle elle n'entre pas dans l'ajustement de Bradley et Terry ; elle est comptée à part (complétude, pertes par
    cause) ; au-delà de 15 % des appels prévus de la phase décisive de A, arrêt de la course et I0 « infrastructure ».
- **Pendant la course (code 3 ; journal, mesures et lecture « partielle » scellés)** : plafond de dépense de 60 USD (aucun appel
  dont le budget ne tient plus dans le reste) ; durée de 48 heures (garde contre une boucle folle) ; A2 ; étiquette interdite dans une
  entrée ; et, **dans la phase décisive de A seulement**, tout arrêt de A : projection de la phase au-delà de la part de A (au prix
  observé : moyenne des réponses à coût connu dès trois réponses, prix du plan avant), part de A atteinte, A en panne, pertes
  définitives au-delà de 15 %, plus de la moitié de réponses inexploitables sur les 20 dernières.
- **Arrêt d'un juge seulement (jamais de la course, consigné, réserve)** hors de la phase décisive de A : juge en panne ou part
  atteinte → ses étapes suivantes ne sont pas jouées, celles de l'autre juge continuent ; plus de la moitié de réponses inexploitables
  sur les 20 dernières → ses étapes restantes de la phase ne sont pas jouées. Projection avant chaque étape : phase de B étape par
  étape (une étape qui ne tient pas dans la part de B n'est pas jouée, la suivante est examinée) ; bras sans dossier et phases
  descriptives : toute la phase du juge doit tenir, sinon elle n'est pas jouée.

## 9. Lectures préalables déclarées

Avant le brouillon 1, son rédacteur a joué des courses **à blanc** (juges scriptés, aucun appel) et des simulations du plan, et
en a lu les sorties : elles ont servi à choisir le plan (graphe 3-régulier, paires mélangées pour B, critère de reproduction plutôt
que corrélation de rangs pour D4, biais de position par la part du premier plutôt que par la bascule). La contre-lecture
(`prereg/contre-lecture-preenregistrement-juges-idees-v2-v1.md`) a joué d'autres courses à blanc (juges scriptés, dont un juge qui
ne lit aucune table) et des calculs de puissance, sans appel de modèle ni donnée réelle ; elle a écrit P12 et P13. Pour ce
brouillon 2, le rédacteur a joué, sur le code de ce brouillon : le contrôle de diagnosticité sur les deux jeux de matériaux, les
tables de puissance et le plan joué par des juges scriptés (section 5), et les courses à blanc du rapport (plafond, parfait, bruité,
biaisé de position, juge en panne) ; il les a lues avant d'écrire D1 (test seul, pour la puissance de 0,9 demandée), D4 et D6 (niveau
0,10), D5 (0,15), D6 (exactitude de B), P14 à P16, les seuils du contrôle de diagnosticité (2 courses sur 20, aire moyenne 0,62) et la politique du relais. Aucune donnée réelle n'a été vue ; les 12 fiches réelles
n'ont pas été lues ; aucun appel de modèle n'a été fait. Ces courses à blanc ne disent rien des juges réels.

## 10. Portée (ce que l'expérience ne dit pas)

- Rien sur la qualité des idées réelles : le lot réel est décrit, pas jugé.
- Les témoins sont des gabarits dans trois mondes plantés, servis avec un dossier de faits ; les fiches réelles n'ont ni dossier
  de ce type ni vérité connue. Un succès dit que le protocole **peut** faire départager quand l'information existe, pas qu'il
  départage les fiches réelles.
- Deux juges (Argon, Astra) : rien sur Kimi ni sur Claude comme juges. Le rôle de B est réduit (un tirage, paires mélangées).
- L'ancien protocole est rejoué avec le dossier inséré sur les témoins (ce n'est pas l'entrée exacte du second tour) et, par le
  juge A seul, sans dossier (la forme de l'entrée du second tour, à la consigne et aux items de la configuration près ; un juge,
  Argon, au lieu de Kimi et Argon).
- La consigne v2 nomme exactement les familles de défauts plantées (loi contredite, redite, affirmation vraie par définition,
  texte sans affirmation réfutable), la longueur, et demande un signe compatible avec le dossier ; elle a été écrite par l'auteur des
  témoins. La comparaison porte sur des protocoles complets, consigne comprise : un succès ne dit rien des défauts que la consigne ne
  nomme pas (la classe « signe contraire » n'y est nommée qu'à travers le critère de prédiction).
- Les matériaux sont rééquilibrés pour que ni le gabarit, ni l'a priori de plausibilité, ni le sens de la loi, ni la longueur ne
  séparent les classes ; le contrôle de diagnosticité ne couvre que les indices et les juges scriptés qu'il nomme. D1 mesure la
  lecture du contenu (dossier ou fiche) ; seule D1b mesure la lecture des tables, et sur son sous-ensemble la longueur (aire 0,657) et le nombre de chiffres (0,638) séparent un peu les bonnes lois des lois fausses (section 4).
- Plan creux (graphe 3-régulier) : une fiche qui ne rencontre que des fiches de sa classe garde une force peu informative ; les
  ancres peuvent s'inverser dans un lot.
- D4 et D6 sont jugés au niveau 0,10 (reproduction et accord, une fois D1 établi au niveau 0,05) : un juge dont la discrimination ne
  se reproduit pas du tout passe D4 une fois sur dix ; c'est le prix d'un plan qui ne conclut pas I4 par manque de puissance.
- Les gabarits sont écrits par un modèle de la famille Claude ; aucun juge de cette famille ici, mais une familiarité de style
  entre gabarits et juges d'autres familles n'est pas mesurée.
- Coût du v2 en production : par lot de n fiches et degré d, n·d appels par juge et par tirage (deux ordres) contre n pour
  l'ancien ; non évalué ici au-delà du devis.

## 11. Code gelé

Fermeture des imports du chemin réel (`FICHIERS_GELES` du lanceur, mesurée par l'essai `Fermeture`, inchangée depuis le
brouillon 1 : 62 fichiers) ; le lanceur refuse un bloc qui ne la couvre pas exactement ou dont une empreinte diffère du fichier
présent. À remplir au commit (marqueur).

<!-- empreintes-du-code : début -->
```
<<EMPREINTE_DU_CODE>>  demonstrations/ideation_v2.py
<<EMPREINTE_DU_CODE>>  demonstrations/ideation_v4.py
<<EMPREINTE_DU_CODE>>  demonstrations/ideation_v5.py
<<EMPREINTE_DU_CODE>>  demonstrations/ideation_v6.py
<<EMPREINTE_DU_CODE>>  demonstrations/ideation_v7.py
<<EMPREINTE_DU_CODE>>  demonstrations/ideation_v8.py
<<EMPREINTE_DU_CODE>>  demonstrations/validation_juges_idees_v2.py
<<EMPREINTE_DU_CODE>>  pole/__init__.py
<<EMPREINTE_DU_CODE>>  pole/adaptateur_kimi_v53.py
<<EMPREINTE_DU_CODE>>  pole/adaptateurs.py
<<EMPREINTE_DU_CODE>>  pole/adaptateurs_v56.py
<<EMPREINTE_DU_CODE>>  pole/aiguilleur_v53.py
<<EMPREINTE_DU_CODE>>  pole/bisociateur_v53.py
<<EMPREINTE_DU_CODE>>  pole/bisociateur_v54.py
<<EMPREINTE_DU_CODE>>  pole/bisociateur_v55.py
<<EMPREINTE_DU_CODE>>  pole/budget_v53.py
<<EMPREINTE_DU_CODE>>  pole/budget_v54.py
<<EMPREINTE_DU_CODE>>  pole/budget_v56.py
<<EMPREINTE_DU_CODE>>  pole/caviardage.py
<<EMPREINTE_DU_CODE>>  pole/coffre_v53.py
<<EMPREINTE_DU_CODE>>  pole/coffre_v55.py
<<EMPREINTE_DU_CODE>>  pole/configuration_v53.py
<<EMPREINTE_DU_CODE>>  pole/configuration_v54.py
<<EMPREINTE_DU_CODE>>  pole/configuration_v55.py
<<EMPREINTE_DU_CODE>>  pole/configuration_v56.py
<<EMPREINTE_DU_CODE>>  pole/course2_v53.py
<<EMPREINTE_DU_CODE>>  pole/course2_v54.py
<<EMPREINTE_DU_CODE>>  pole/course2_v55.py
<<EMPREINTE_DU_CODE>>  pole/course2_v56.py
<<EMPREINTE_DU_CODE>>  pole/dossier_ferme.py
<<EMPREINTE_DU_CODE>>  pole/etage_entre_generations_v53.py
<<EMPREINTE_DU_CODE>>  pole/etage_entre_generations_v54.py
<<EMPREINTE_DU_CODE>>  pole/etage_entre_generations_v55.py
<<EMPREINTE_DU_CODE>>  pole/etage_entre_generations_v56.py
<<EMPREINTE_DU_CODE>>  pole/fiches_v53.py
<<EMPREINTE_DU_CODE>>  pole/fiches_v54.py
<<EMPREINTE_DU_CODE>>  pole/garde_outils.py
<<EMPREINTE_DU_CODE>>  pole/gardes_e0_v54.py
<<EMPREINTE_DU_CODE>>  pole/gardes_e0_v55.py
<<EMPREINTE_DU_CODE>>  pole/gardes_e0_v56.py
<<EMPREINTE_DU_CODE>>  pole/graines_v53.py
<<EMPREINTE_DU_CODE>>  pole/ideation_v2.py
<<EMPREINTE_DU_CODE>>  pole/juges_croises_v53.py
<<EMPREINTE_DU_CODE>>  pole/juges_idees_v2.py
<<EMPREINTE_DU_CODE>>  pole/memoire_v53.py
<<EMPREINTE_DU_CODE>>  pole/mesures_v54.py
<<EMPREINTE_DU_CODE>>  pole/moisson.py
<<EMPREINTE_DU_CODE>>  pole/noyau_v54.py
<<EMPREINTE_DU_CODE>>  pole/noyau_v55.py
<<EMPREINTE_DU_CODE>>  pole/noyau_v56.py
<<EMPREINTE_DU_CODE>>  pole/outils.py
<<EMPREINTE_DU_CODE>>  pole/pari_apparie.py
<<EMPREINTE_DU_CODE>>  pole/prepilote_v54.py
<<EMPREINTE_DU_CODE>>  pole/prepilote_v55.py
<<EMPREINTE_DU_CODE>>  pole/prepilote_v56.py
<<EMPREINTE_DU_CODE>>  pole/protocole_outils.py
<<EMPREINTE_DU_CODE>>  pole/relais.py
<<EMPREINTE_DU_CODE>>  pole/relais_reel.py
<<EMPREINTE_DU_CODE>>  pole/suivi_roles_v54.py
<<EMPREINTE_DU_CODE>>  pole/tableau_v53.py
<<EMPREINTE_DU_CODE>>  pole/tests_de_mort_v2.py
<<EMPREINTE_DU_CODE>>  pole/tests_de_mort_v3.py
```
<!-- empreintes-du-code : fin -->

## 12. Devis

**Prix et durées, avec leurs sources (R6).** Argon : **0,062 USD et 7,6 s par appel**, mesurés sur 526 appels d'A1 sur un fil
(`registres/decisions.md` du dépôt de travail, ligne 1230, R-1266, sha256 du registre lu le 3 novembre à 01:32 UTC
`39ef7ecb153ae4af4d599886eecd02d0b6ce7a01e2e59932f7fc75ce01090201` ; le registre ne fait que croître : les lignes citées y ont été relues) ; ces appels n'étaient pas des comparaisons (une entrée de
comparaison porte la consigne, le dossier et deux fiches : environ 8 500 à 9 700 caractères, 8 860 en moyenne sur les 198 paires possibles des trois lots) ; borne de durée du plan 8 à 40 s (celle du plan (b′) d'A1, `pole/attaque_goodhart_v3.py`, ligne 91).
Astra (`gpt-6-astra`) : **non mesuré** (prix « 10/50 supposé » par million de jetons d'entrée et de sortie, `registres/decisions.md`,
ligne 1215, R-1251 ; taux de devis 0,25 USD par appel du plan A1-bis, `pole/attaque_goodhart_v3.py`, lignes 84-85 de ce dépôt, sha256 `b821bdb73a2829a41d519800859bbf10216254ca97228b5a179438eed38a1c6a`) :
le plan prend une **borne prudente de 0,50 USD par appel** (deux fois le taux d'A1-bis ; au prix supposé, 0,50 USD couvre environ
3 000 jetons d'entrée et 9 000 jetons de sortie, raisonnement compris) et 10 à 120 s par appel ; l'épreuve (section 4) le mesure ;
la course projette au prix observé.

| phase | juge | appels | USD au prix du plan | requis ? |
|---|---|---|---|---|
| décisive A | Argon | 246 | 15,25 | oui (sinon arrêt avant tout appel) |
| sans dossier (A) | Argon | 30 | 1,86 | oui |
| décisive B, comparaisons | Astra | 24 à 36 (32 à la graine 20261102 ; au plus 39) | 12,00 à 18,00 (16,00 à la graine 20261102 ; au plus 19,50) | oui |
| décisive B, ancien | Astra | 30 | 15,00 | oui |
| réel, ancien | Astra ; Argon | ≤ 13 ; ≤ 13 (lot de substitution : 12 ; 6) | ≤ 6,50 ; ≤ 0,81 | non : jouée si sa projection tient |
| réel, v2 | Astra ; Argon | ≤ 13 ; ≤ 13 (12 ; 6) | ≤ 6,50 ; ≤ 0,81 | non |

**Requis** : Argon 276 appels, 17,11 USD (part 24 : 1,4 fois) ; Astra au plus 69 appels, 34,50 USD au plus à la borne prudente
(part 36) ; total requis au plus 51,61 USD ≤ 60. **Maximum** (lot réel de 13 fiches toutes admises pour A, 39 paires mélangées) :
Argon 302 appels, 18,72 USD ; Astra 95 appels, 47,50 USD à la borne prudente — au-dessus de sa part : les phases réelles d'Astra ne
sont alors pas jouées (règle de projection, section 8), jamais un arrêt. **Attendu** (graine 20261102 : 32 comparaisons de B ; lot réel de substitution de 12 fiches, 6 admises pour A) : au taux d'A1-bis (0,25 USD par appel
d'Astra), 39,36 USD, toutes phases jouées ; à la borne prudente (0,50), 48,86 USD, les deux phases réelles d'Astra non
jouées (au-dessus de l'attendu de 30 à 43 USD écrit au GO-2026-11-02-32, sous le plafond : la borne est prudente, pas mesurée) ; dans tous les cas ≤ 60 USD par construction (parts portées au relais par la porte de plafond, compteur à parts). Les
incidents du relais (échecs coûteux, coûts inconnus comptés au plafond de session, `plafonds_session.juge`, au moins 1,00 USD) s'ajoutent ; cinq de suite arrêtent
le juge.

**Durée** (séquentielle, bornes du plan, sans attente sur le relais) : 0,88 à 6,07 heures pour le plan de la course à blanc de référence, toutes phases (plan maximal : 0,94 à 6,52 heures) ;
garde de 48 heures contre une boucle folle, jamais une coupe de la mesure ; délai par appel de la commande externe : 1 800 s
(`AdaptateurCommandeExterne.DELAI_COMMANDE_S`), garde contre un appel bloqué ; panne d'un juge déclarée après 6 heures sans réponse.

**Options écartées, pour mémoire** (GO-2026-11-02-32 a tranché) :

| juges | pourquoi pas |
|---|---|
| Argon (A) + Kimi (B) | exclu par GO-2026-11-02-32 : coût et durée (0,35 USD et 600 à 1 500 s par appel au plan A1-bis, `pole/attaque_goodhart_v3.py`, lignes 82-83) et fiabilité du relais Kimi à A1 (5 appels réussis, 616 en échec, `registres/etat.md`, ligne 6) |
| Kimi (A) | idem ; en séquence, les 246 appels de la phase décisive de A prendraient 41 à 103 heures aux bornes du plan A1-bis |
| Argon (A) + Opus 5.5 (B) | famille de l'auteur des gabarits des témoins : refusé par le code |

## 13. Avant la course

Contre-lecture neuve (R2) de ce brouillon, du module, des essais, du banc et du lanceur, d'abord du delta (matériaux rééquilibrés et
contrôle de diagnosticité, statuts du relais et arrêts par juge, bras sans dossier, critères D1, D4, D5, D6 refaits) ; corrections
éventuelles sur un brouillon 3 ; recalcul des empreintes du bloc `plan-gele` et du bloc de la section 11 ; essais et banc de
mutations rejoués sur l'arbre à sceller ; **épreuve de la commande Astra 8807** par session-depot et recopie au marqueur ; configuration
préparée par la session qui tient les clés (commandes `argon` et `astra` avec porte de plafond, `plafonds_session.juge` ≥ 1,00 USD,
pièces `consigne_juge`, `question_course_2`, `lot_reel_juges_idees_v2`) ; avant le scellement, la session qui tient les pièces vérifie
que la consigne figée de l'ancien juge passe la garde A4 des témoins (`exiger_entrees`) ; aucune autre course n'emploie le relais
Argon pendant celle-ci (relais à un seul fil : un second appel attend et peut expirer en code 6) ; GO de Lazar au plafond exact du
texte (GO-2026-11-02-32, 60 USD) ; `--verifier-seulement` ; scellement, commit, poussée ; puis la course chez session-depot, une
seule fois ; sortie scellée avant lecture. La lecture gelée est prononcée par un lecteur neuf (R13), puis soumise à Lazar.

## 14. Couples de la contre-lecture v1 : appliqués, refaits, et changements propres à ce brouillon

Les 40 couples (`prereg/couples-contre-lecture-juges-idees-v2-v1.json`, numérotés dans l'ordre du fichier) ont été écrits
pour le texte du brouillon 1 et les décisions connues alors (GO-2026-11-02-24, 20 témoins, juge B à confirmer). GO-2026-11-02-32 a
tranché depuis (juges, taille, parts) : un couple est **appliqué tel quel** quand son texte nouveau est repris au mot près (ou
précisé sans changer son sens), **appliqué, adapté** quand son sens est repris avec les valeurs de GO-2026-11-02-32 ou du code de ce
brouillon, **refait** quand ce brouillon le remplace par autre chose, pour la raison dite.

| couple | objet | sort | raison |
|---|---|---|---|
| C1 | statut du texte | refait | des couples sont refaits, pas tous appliqués ; le brouillon 2 n'est pas contre-lu |
| C2 | marqueurs restants | refait | la consigne ne permet de marqueurs que pour le GO, la configuration, les empreintes du code et l'épreuve d'Astra : GO-2026-11-02-32 nomme Astra (plus de marqueur MOT_DE_LAZAR_ASTRA) ; les matériaux rééquilibrés sont dans le code et leur empreinte est écrite (plus de marqueur MATERIAUX_SHA256) ; les sources du devis sont écrites avec chemin, ligne et empreinte (plus de marqueur SOURCES_DU_DEVIS) ; les réglages `--effort` et `--reflexion` sont à recopier avec l'épreuve (marqueur EPREUVE_ASTRA_8807, qui remplace REGLAGES_DES_JUGES) |
| C3 | lignes de `kappa_cohen` | tel quel | |
| C4 | bras sans dossier | adapté | 30 témoins (15 contre 15) et GO-2026-11-02-32 au lieu de 20 et du « 2 novembre » |
| C5 | H0(b) en deux branches | tel quel | |
| C6 | P11, P12, P13 | tel quel | P11 précisé « ancien avec dossier » |
| C7 | gabarits et a priori (B1) | refait | le couple décrivait le défaut et laissait l'empreinte en marqueur ; ce brouillon rééquilibre les matériaux (trois mondes, lois fausses graduées sur des caractéristiques plausibles, bonnes lois de deux groupes sur des caractéristiques peu plausibles, sens équilibré par une loi décroissante neuve par monde et par la classe « signe contraire »), étend le contrôle de forme à six indices bornés des deux côtés et ajoute le contrôle de diagnosticité (section 4) |
| C8 | Astra hors du périmètre écrit du GO (B6) | refait | GO-2026-11-02-32 nomme Argon et Astra et exclut Kimi : plus de nœud, plus de marqueur |
| C9 | A2 sur le statut « refus » de la commande v56 | tel quel | |
| C10 | table des étapes | adapté | 30 témoins, trois lots, au plus 39 paires pour B (13 par lot), comparaisons de B avant son ancien protocole, règle de projection par phase |
| C11 | tâches de graines du bras sans dossier | tel quel | |
| C12 | GO de la commande de lancement | refait | GO-2026-11-02-32 (la ligne de 60 USD inscrite plus tôt pour cette course « n'est pas utilisée », dit GO-2026-11-02-32) |
| C13 | `materiaux_sha256` | refait | empreinte calculée sur les matériaux rééquilibrés, au lieu d'un marqueur |
| C14 | plafond 60 USD, parts 24 et 36, durée 48 h | tel quel | |
| C15 | `go` du bloc `plan-gele` | refait | GO-2026-11-02-32 |
| C16 | paragraphe sous le bloc | refait | empreinte des matériaux écrite ; GO-2026-11-02-32 ; politique du relais gelée |
| C17 | métriques du bras sans dossier | tel quel | |
| C18 | kappa des paires (I5) | adapté | D6 devient l'exactitude de B (test binomial) ; le kappa des paires reste descriptif (P6), avec sa relation (2p − 1)² et l'absence de kappa « sur les paires de même qualité » |
| C19 | bascule par tirage et par paire (M3) | tel quel | |
| C20 | puissance à 0,9 | refait | recalcul par ce code (graine 20261102, 20 000 répétitions) à 15 contre 15, D1 réduit au test (section 5) |
| C21 | « quelle que soit la taille » (M2) | refait | sans objet : D1 n'a plus de seuil d'aire |
| C22 | portée d'une issue négative | refait | 15 contre 15 : 7 % et 0,1 % (section 5 et I3) |
| C23 | D6 et D7 | adapté | D7 à 27 verdicts lisibles sur 30 ; D6 redéfini (exactitude de B, niveau 0,10, au moins 20 comparaisons valides) |
| C24 | validité : pertes du relais | adapté | 27 verdicts lisibles sur 30 ; une perte est un échec coûteux repris deux fois en fin d'étape ; ce qui n'a pas été envoyé est attendu et repris, jamais perdu (section 8) |
| C25 | I3 « au seuil gelé » | tel quel | portée chiffrée à 15 contre 15 |
| C26 | suite de I2 | tel quel | |
| C27 | lecture du bras, S0 à S3 | adapté | réserve « accord du juge B non mesuré » au lieu de « accord entre juges non mesuré » (D6 redéfini) |
| C28 | plafond au-dessus de 60 USD refusé | tel quel | |
| C29 | liste d'arrêt avant tout appel | adapté | complétée : budget par appel, dépense requise par juge, contrôle de diagnosticité, politique du relais dans les valeurs fixes |
| C30 | statuts du relais pendant la course (B2) | refait | code 4 (plafond de session, registre, 402, 429) attendu et repris comme un relais injoignable, et non arrêt « dépense » : 429 est passager, et le compteur à parts arrête déjà tout appel qui ne tient plus dans le plafond ou dans la part ; attente sans borne par appel et panne après 6 h sans réponse, au lieu de 30 minutes par appel ; échec coûteux repris en fin d'étape, au plus deux fois ; arrêt d'un juge seulement hors de la phase décisive de A — pour qu'une panne ne rende pas la course non concluante par défaut de conception (mots de Lazar, GO-2026-11-02-32) |
| C31 | lectures préalables | adapté | complété par celles de ce brouillon (section 9) |
| C32 | portée | adapté | trois mondes, deux juges, matériaux rééquilibrés, limite de D1b, D4 et D6 au niveau 0,10 |
| C33 | sources du devis (M4) | refait | sources écrites (chemin, ligne, empreinte) ; prix de Kimi cité au plan A1-bis du code |
| C34 | table du devis | refait | nouvelles tailles : 276 appels requis d'Argon, au plus 69 d'Astra |
| C35 | total | refait | idem |
| C36 | maximum | refait | idem ; borne prudente d'Astra à 0,50 USD par appel |
| C37 | durée | refait | nouvelles bornes (0,88 à 6,07 heures) |
| C38 | option retenue | refait | GO-2026-11-02-32 a tranché |
| C39 | Argon et Kimi | refait | GO-2026-11-02-32 a exclu Kimi |
| C40 | avant la course | adapté | repris (consigne de l'ancien juge passée à la garde A4 des témoins, relais Argon libre), complété par l'épreuve d'Astra ; GO-2026-11-02-32 au lieu du mot de Lazar sur Astra |

**Changements propres à ce brouillon** (au-delà des couples) :
1. Juges Argon et Astra, parts de 24 et 36 USD, plafond de 60 USD, garde de 48 heures, tout depuis GO-2026-11-02-32 ; budget par appel
   au moins deux fois le prix de plan le plus haut ; borne prudente d'Astra à 0,50 USD par appel (non mesuré).
2. Trois mondes, 15 bons et 15 mauvais témoins d'évaluation ; classe « signe contraire » (point I2 de la contre-lecture : un défaut que
   la consigne ne nomme pas en propre) ; P14, P15, P16.
3. Contrôle de forme à six indices (sens de la loi ajouté), bornés des deux côtés ; contrôle de diagnosticité par six juges de forme et
   un juge « dossier sans tables » ; D1b qualificatif et lecture des tables T1, T0, T-.
4. D1 réduit au test (p < 0,05) ; D4 au niveau 0,10 ; D5 à 0,15 ; D6 redéfini : exactitude de B, test binomial au niveau 0,10, mesuré
   à partir de 20 comparaisons valides et 0,85 de validité.
5. Ordre des phases : les comparaisons de B avant son ancien protocole ; règle de projection propre à chaque phase (tout ou arrêt pour
   la phase décisive de A, étape par étape pour B, toute la phase ailleurs).
6. Statuts du relais classés à chaque appel (B2) : rien d'envoyé attendu et repris ; échec coûteux perdu puis repris au plus deux fois ;
   panne ; règle écrite d'avance des comparaisons perdues ; arrêt d'un juge seulement hors de la phase décisive de A.
7. Gardes du lanceur (B7) : chacune essayée sur un cas sain et sur un artefact, une mutation par garde (rapport, section 4).
8. Indicateur descriptif « au plafond » aligné sur D2 (0,80, point M6) ; identifiant réel de la forme des témoins refusé (point M5).
