# Préenregistrement — étage des juges d'idéation, version 2 : le protocole par paires discrimine-t-il là où l'ancien sature ? (brouillon 1)

Statut : **brouillon 1, non scellé, non contre-lu**. Rédigé le 2 novembre 2026 (de 17:32 à 18:50 UTC, heures lues sur
`date -u`) par un sous-agent concepteur neuf, qui n'a écrit ni l'étage des juges existant (`pole/juges_croises_v53.py`) ni ses
consignes ; aucun appel de modèle, aucune clé, aucun réseau, aucun commit, aucun compagnon `.sha256`, aucun fichier existant
modifié. Code neuf (R12) : `pole/juges_idees_v2.py`, `demonstrations/validation_juges_idees_v2.py`,
`essais/test_juges_idees_v2.py`, `essais/mutations_juges_idees_v2.py` ; empreintes au rapport
(`prereg/rapport-redaction-juges-idees-v2.md`). Trois marqueurs restent, et le lanceur refuse tout texte qui en porte un :
`<<GO>>`, `<<CONFIGURATION_SHA256>>` et `<<EMPREINTE_DU_CODE>>` (une ligne par fichier de la fermeture du chemin réel,
section 11). Le scellement se fait sur une version contre-lue, renommée `prereg/preenregistrement-juges-idees-v2-vN.md`
(N ≥ 1, sans « brouillon ») ; l'entropie des graines de la course est l'empreinte de ce fichier-là.

## 1. Question et motivation

**Question.** Sur des fiches dont la qualité est connue par construction (témoins plantés), le protocole v2 des juges —
comparaisons par paires à l'aveugle avec preuve citée, ancres, budget de notables, règle de famille — **discrimine-t-il** les
bonnes fiches des mauvaises, **là où l'ancien protocole sature** (« notable » donné presque partout) ?

**Constat qui motive** (README principal, ligne du « second real round », sha256 du README lu
`a5e6b8622fbd7b319d74a01b9d2208c13a1e89dc17cdc37c4f1d99db6dd4b298`, ligne 125) : au second tour réel du 1er novembre 2026
(Kimi et Argon, 12 fiches), 11 fiches sur 12 « notables » (un juge 12 sur 12, l'autre 11 sur 12), accord brut 0,92, kappa de
Cohen nul. Ces chiffres sont ceux du dépôt public ; la trace agrégée est privée (sha256
`091ff9edefec3faa411ae786a28595c5d3648e1b7aa4c425d290a3e64544338a`), non relue ici.

**Diagnostic** (détaillé au rapport, section 1 ; code cité à l'empreinte `c4c6ab12dc471eef078c116a4205a22d9b498da720ce71e37a0a6edae6c4239b`
de `pole/juges_croises_v53.py`) : (i) « notable » est une conjonction d'items de forme (`lire_verdict`, ligne 48) que toute
fiche bien rédigée satisfait, puisque le proposeur reçoit justement ce gabarit ; (ii) le jugement est absolu, une fiche seule,
sans référence de qualité connue ni plafond au nombre de notables ; (iii) rien n'oblige le juge à toucher le fond : ni dossier
de faits, ni preuve demandée ; (iv) au plafond, le classement (`classement`, ligne 117) départage par l'identifiant ; (v)
`kappa_cohen` (ligne 140) rend 1 quand l'accord attendu vaut 1, si bien que deux juges toujours « notable » paraîtraient en
accord parfait (`mesures_v54.kappa_cohen_v54` corrige, la lecture de la course ne l'emploie pas) ; (vi) au second tour, chaque
fiche avait un juge de sa propre famille. Ce diagnostic est un raisonnement sur le code et sur des propriétés connues des juges
fondés sur des modèles de langage (indulgence du jugement absolu, biais de position, préférence pour le texte long et pour sa
propre famille) ; aucun chiffre de la littérature n'est avancé.

**Ce que l'expérience compare.** Les deux protocoles, **sur les mêmes fiches, avec les mêmes juges et la même information** :
pour les lots témoins, l'ancien protocole reçoit sa consigne figée (pièce privée de la course 2), puis le dossier du lot, puis la
fiche ; le v2 reçoit sa consigne figée, le dossier et deux fiches. Sans le dossier, aucun protocole ne pourrait savoir qu'une
loi est fausse ou déjà établie : l'insérer dans l'ancien protocole isole l'effet du protocole de celui de l'information (écart
assumé à la reproduction exacte du second tour, section 10).

## 2. Hypothèses

- **H1 (l'ancien sature par construction).** Servi avec le même dossier, l'ancien protocole donne « notable » à presque tous
  les témoins, bons comme mauvais : sa part de notables reste haute et ses notes ne séparent pas bons et mauvais.
- **H2 (le v2 discrimine).** Le choix forcé entre deux fiches, adossé à une citation vérifiée de la fiche choisie et du
  dossier, fait remonter les lois vraies et neuves au-dessus des lois fausses, des redites, des affirmations vraies par
  définition et des textes longs sans affirmation réfutable.
- **H3 (le v2 est fiable).** Sa discrimination se reproduit sur un second tirage (autre graphe de paires, autres ordres,
  autres identifiants), n'est pas pilotée par la position de présentation, et deux juges de familles différentes s'accordent
  sur les paires qui départagent.
- **H0, écrites d'avance.** (a) Le v2 ne discrimine pas mieux que le hasard : les juges ne lisent pas le dossier, ou tranchent
  par la forme ; (b) l'ancien ne sature pas sur ces témoins : le plafond du second tour tenait aux fiches réelles ou à
  l'absence de dossier, pas au protocole ; (c) le v2 discrimine mais de façon instable ou pilotée par la position.

## 3. Prédictions chiffrées et signées (ouvertes dans les deux sens ; elles ne décident pas l'issue)

Juge A = Argon (`gemini-4-argon`), tirage 1, sur les 20 témoins d'évaluation, sauf mention. « Aire » = aire sous la courbe ROC
(courbe des taux de vrais et de faux positifs) des notes entre bons et mauvais témoins (égalités comptées pour moitié).

| | prédiction | justification | sens contraire possible, et ce qu'il dirait |
|---|---|---|---|
| P1 | ancien : part de notables ≥ 0,80 | le second tour (11 sur 12) ; les témoins sont rédigés au même standard de forme | < 0,80 : le dossier suffit à l'ancien pour refuser des fiches ; H0(b) |
| P2 | ancien : aire ≤ 0,65 | au plafond, presque toutes les notes sont égales | > 0,65 : l'ancien départage avec l'information ; H0(b) |
| P3 | v2 : aire ≥ 0,80 | choix forcé, citation du dossier exigée ; vérifier un nombre contre une table est à la portée d'un juge capable | < 0,80 : le juge ne lit pas la table ou ne la compare pas ; H0(a) |
| P4 | v2 − ancien : différence d'aire ≥ +0,15 | P3 et P2 | < +0,15 : le gain tient à l'information, pas au protocole |
| P5 | v2 : faux notables ≤ 0,10 et vrais notables ≥ 0,30 ; ancien : faux notables ≥ 0,70 | plancher des ancres et budget ; plafond de l'ancien | v2 > 0,10 : le plancher des ancres ne protège pas ; vrais < 0,30 : ancres inversées ou budget trop serré |
| P6 | kappa des paires mélangées (A contre B) ≥ 0,40 ; kappa de l'ancien ≤ 0,20 ou non défini | deux juges qui discriminent s'accordent sur ce qui départage | < 0,40 : la discrimination est propre à un juge |
| P7 | Spearman entre tirages ≥ 0,50 et aire du tirage 2 ≥ 0,80 | plafond de la corrélation de rangs à 0,75 pour deux classes de 10 ordonnées au hasard à l'intérieur (`plafond_spearman_binaire`) | < 0,50 : notes instables même entre classes |
| P8 | part des victoires de la fiche présentée en premier dans [0,40 ; 0,60] et taux de bascule ≤ 0,40 | ordres tirés au hasard ; la bascule mêle biais de position et incertitude sur les paires de même qualité (≈ 0,37 en simulation pour un juge juste à 0,85, section 5) | hors bornes : pilotage par la position |
| P9 | textes longs : rang moyen v2 < 0,5 ; notables à l'ancien | la consigne v2 dit que la longueur ne compte pas ; l'ancien juge la forme | rang ≥ 0,5 : biais de longueur du juge |
| P10 | redites d'une loi établie : rang moyen v2 < 0,5 | la consigne nomme la nouveauté ; les lois établies sont au dossier | ≥ 0,5 : la nouveauté n'est pas vérifiée (classe la plus difficile : la redite est **vraie**) |
| P11 | juge B (Astra), ancien : part de notables ≥ 0,80 | même raison que P1 | < 0,80 : le plafond dépend du juge |

Le code évalue chacune (`predictions_v1`) ; leur succès ou leur échec est rapporté, jamais lu comme issue.

## 4. Plan

**Matériaux (témoins plantés), gelés avant la course.** `juges_idees_v2.construire_materiaux(20261102)` : deux mondes à loi
plantée dans le domaine du programme — `monde-1` (agent de code, moniteur qui classe « suspect ») et `monde-2` (agent de
navigation, moniteur à score de suspicion) —, chacun de 3 000 épisodes simulés (dix caractéristiques indépendantes, alerte
tirée selon une loi logistique plantée, avec une interaction), tirés de nouveau jusqu'à ce que le dossier montre nettement
chaque vérité (`contraintes_monde` : effet vrai ≥ 5 points entre niveaux extrêmes, effet nul ≤ 1,5 point, interaction ≥ 6
points). Chaque monde donne un **dossier** (contexte, deux lois déjà établies, deux tables de taux à lignes numérotées D01…)
et **douze fiches** au format du tour fermé (titre, hypothèse, prédiction, signe, métrique, test de mort) :

| rôle | classe | monde-1 | monde-2 | qualité |
|---|---|---|---|---|
| évaluation | loi vraie absente des lois établies, chiffres honnêtes du dossier | 5 | 5 | bonne |
| évaluation | loi fausse bien rédigée (effet affirmé de 6 à 8 points, la table montre ≤ 1,5) | 2 | 1 | mauvaise |
| évaluation | redite d'une loi établie, en d'autres mots (vraie, chiffres honnêtes) | 1 | 2 | mauvaise |
| évaluation | affirmation vraie par définition (le moniteur alerte quand il classe « suspect » ; score > 70) | 1 | 1 | mauvaise |
| évaluation | texte long sans affirmation réfutable | 1 | 1 | mauvaise |
| ancre bonne | loi vraie neuve | 1 | 1 | bonne |
| ancre mauvaise | loi fausse bien rédigée | 1 | 1 | mauvaise |

Les gabarits sont communs à toutes les classes, sauf le texte long (long par construction, pour mesurer la préférence pour la
longueur). `controle_forme` : aire de la longueur 0,38 et du nombre de chiffres 0,415 entre bons et mauvais témoins (seuil
0,65 : aucun indice de forme simple ne favorise les bons témoins). `verifier_materiaux` relit la vérité de chaque fiche sur les
tables. Empreinte des matériaux : section 4, bloc `plan-gele` (`materiaux_sha256`) ; le lanceur les reconstruit et refuse tout
écart. Gabarits écrits par un modèle de la famille Claude : aucun juge de cette famille sur les témoins.

**Juges.** A = Argon (`gemini-4-argon`, famille gemini, 0,062 USD par appel mesuré le 2 novembre) ; B = Astra (`gpt-6-astra`,
famille gpt, prix non mesuré, taux de devis 0,25 USD par appel, section 12). Kimi est exclu des comparaisons par paires (coût et
durée, section 12). Chacun passe par son relais de la configuration (`demonstrations/ideation_v8.adaptateurs_reels_v56`) ;
budget par appel = `plafonds_session.juge` ; modèle servi contrôlé à chaque appel (A2).

**Étapes** (fixées par le code, `etapes_v1` ; structure citée par le bloc `plan-gele`, valeurs fixes recopiées) :

| phase | juge | protocole | fiches ou paires | appels |
|---|---|---|---|---|
| décisive A | A | ancien, tirage 1 | 20 témoins d'évaluation, une fiche par appel, dossier du lot inséré | 20 |
| décisive A | A | v2, tirage 1 | par lot, graphe 3-régulier tiré au hasard sur les 12 fiches (18 paires), **deux ordres** par paire | 72 |
| décisive A | A | v2, tirage 2 | nouveau graphe, nouveaux ordres, nouveaux identifiants | 72 |
| décisive B | B | ancien, tirage 1 | 20 témoins d'évaluation | 20 |
| décisive B | B | v2, tirage 1 | paires **mélangées** (une bonne, une mauvaise) du graphe du tirage 1 de A, au plus 13 par lot, un ordre tiré indépendamment de ceux de A | 12 à 26 |
| réel (descriptif) | B ; A | ancien | fiches réelles où le juge est admis (règle de famille) | ≤ 13 ; ≤ 13 |
| réel (descriptif) | B ; A | v2 | un cycle sur ces fiches, un ordre | ≤ 13 ; ≤ 13 |

Le juge B ne voit que des paires mélangées : son rôle est l'**accord** sur ce qui départage, et son budget ne couvre pas tout le
graphe ; ce choix de paires par les étiquettes connues n'existe qu'en validation (en production, les paires ne se choisissent
pas sur la qualité ; déclaré). Les ancres sont servies à l'aveugle comme les autres fiches.

**Lot réel.** Les 12 fiches du second tour, privées, tenues par la session qui détient les clés, sont une pièce de la
configuration (`piece_lot_reel`), avec la question de la course (`piece_question`), servie comme dossier ; elles ne sont lues
que descriptivement (aucun seuil, aucune issue) ; les fusions comptent les familles de leurs parents (toutes, si elles ne sont
pas dites). Elles passent la garde A4 de la configuration avant tout appel ; sinon refus. Phase jouée seulement si sa
projection de dépense tient dans le reste du plafond, sinon consignée « non jouée (budget) ».

**Protocole v2, pour chaque comparaison** : consigne figée v2 (`CONSIGNE_PAIRE_V2`, empreinte au bloc `plan-gele`), dossier,
deux fiches anonymes « présentée en premier » et « présentée en second ». Réponse : `{"comparaison": {preferee, critere,
citation_fiche, citation_dossier}}` ; valide seulement si l'identifiant est l'un des deux, le critère dans la liste (vérité,
nouveauté, contenu, prédiction), la citation de la fiche trouvée telle quelle (après normalisation typographique) dans la fiche
**choisie** et **absente de l'autre**, de 15 à 300 caractères, et, quand le dossier a des lignes de faits, la citation du
dossier trouvée telle quelle (10 à 300 caractères). Une comparaison nulle est comptée, jamais lue comme victoire.

**Note continue** : force de Bradley et Terry avec effet de position (`ajuster_bt` : P(première gagne) = σ(θ₁ − θ₂ + γ),
crêtes 0,5 et 0,5, forces centrées, arrondies à 10⁻⁹), ajustée par lot sur les comparaisons valides d'un juge et d'un tirage.
**Verdict** (`verdicts_lot`) : « notable » = parmi les ⌈0,25 × 10⌉ = 3 premières fiches d'évaluation du lot **et**
strictement au-dessus du milieu des forces des deux ancres ; ancres inversées → aucun notable dans le lot ; égalité à la limite
du budget → aucune des fiches à égalité. **Ancien protocole** : `juges_croises_v53.lire_verdict` (items de la configuration,
« notable » = tous vrais), note continue = part d'items vrais.

**Graines (R9).** `graines_v53.Graines(entropie)` : `SeedSequence(entropie, spawn_key=(cle_de_tache(tâche),))`, entropie =
`int(SHA-256 du texte scellé, 16)` ; tâches : `graphe|<lot>|tirage-<t>`, `ordres|<lot>|tirage-<t>|<juge>`, `paires-b|<lot>`,
`ordre-ancien|<lot>|<juge>|tirage-<t>`, `anonymisation|<juge>|tirage-<t>|<lot>|<fiche>`, `graphe|reel|<juge>`,
`ordres|reel|<juge>` ; matériaux : `Graines(20261102)`, tâches `materiaux|<monde>|tentative-<k>` et `materiaux|<monde>|fiche-<k>`.
Tout est écrit au manifeste de la course.

**Lancement** (après scellement, GO et configuration) :
`python3 -I -B demonstrations/validation_juges_idees_v2.py SORTIE_NEUVE --preenregistrement prereg/preenregistrement-juges-idees-v2-vN.md --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go registres/go.md --go <<GO>>`
(d'abord avec `--verifier-seulement` : toutes les gardes, plafonds accusés, aucun appel, aucune écriture dans la sortie).

<!-- plan-gele : début -->
```
juge_a: etiquette=juge-a, fournisseur=argon, modele=gemini-4-argon, famille=gemini, prix_usd=0.062, secondes=8-40
juge_b: etiquette=juge-b, fournisseur=astra, modele=gpt-6-astra, famille=gpt, prix_usd=0.25, secondes=10-120
correspondance_auteurs: kimi=kimi, argon=gemini
graine_materiaux: 20261102
materiaux_sha256: c3eeb559f6ead1035f8a73a1daa5a5c16163ca635199327b34eeae95fc1f8479
consigne_paire_sha256: 6978f0a4778edd87f9059606420577c167a1ff8db2053ab56507d20a355039b4
piece_consigne_ancienne: consigne_juge
piece_question: question_course_2
piece_lot_reel: lot_reel_juges_idees_v2
plafond_usd: 30
plafond_juge_a_usd: 12
plafond_juge_b_usd: 18
duree_max_h: 6
configuration_sha256: <<CONFIGURATION_SHA256>>
go: <<GO>>
degre: 3
tirages_a: 2
degre_reel: 2
paires_b_max_par_lot: 13
part_budget: 0.25
ridge_forces: 0.5
ridge_position: 0.5
seuils: alpha=0.05, aire_v2_min=0.75, plafond_ancien_min=0.8, delta_aire_min=0.15, aire_retest_min=0.75, biais_premier_max=0.1, kappa_paires_min=0.3, validite_min=0.85, presents_ancien_min=18
```
<!-- plan-gele : fin -->

Les deux empreintes `materiaux_sha256` et `consigne_paire_sha256` sont celles du code de ce brouillon ; si la contre-lecture
fait changer le code, elles changent et le lanceur refuse l'écart (à recalculer au scellement, avec le bloc de la section 11).
Les noms de pièces (`consigne_juge`, `question_course_2`, `lot_reel_juges_idees_v2`) sont ceux que la configuration devra
porter ; la configuration est préparée par la session qui tient les clés.

## 5. Métriques, taille et puissance

**Métriques** (`mesurer`, depuis le seul journal) : aire et test de Mann et Whitney unilatéral (loi exacte sans égalité,
approximation normale corrigée sinon) par protocole, par juge et par tirage ; différence appariée des aires v2 − ancien
(DeLong, unilatéral ; variance nulle → p = 0 si la différence est positive, dit) ; part de notables, faux notables (mauvais
témoins notables), vrais notables ; kappa de Cohen sur les verdicts de l'ancien (convention v54 : non défini si l'accord
attendu vaut 1) ; kappa des choix par paire entre A et B, sur les paires mélangées (chaque jugement de A, un par ordre, en
regard du jugement de B ; issue orientée par l'empreinte de l'identifiant, sans lien avec la classe), et, descriptifs, sur
toutes les paires et sur les paires de même qualité ; fidélité test-retest (aire du tirage 2 ; Spearman entre forces des deux
tirages, avec son plafond binaire 0,752) ; biais de position (part des victoires de la première présentée sur les deux tirages
de A, taux de bascule, effet γ par lot) ; part des comparaisons valides et motifs ; rang centile moyen par classe ; complétude
(appels joués contre appels prévus, par phase et par juge).

**Taille.** 20 témoins d'évaluation (10 bons, 10 mauvais) ; 4 ancres. **Puissance** (modèle binormal ; test de Mann et
Whitney unilatéral à 5 %, loi exacte ; 20 000 répétitions par case ; `--puissance --graine 20261102`) : voir le tableau ci-dessous
(section 5 bis). Le critère D1 exige l'aire ≥ 0,75 **et** p < 0,05.

**5 bis. Tables de puissance** (exploratoires, calculées par le code de ce brouillon ; reproduire :
`python3 -I -B demonstrations/validation_juges_idees_v2.py --puissance --graine 20261102 --repetitions 20000 --graines-plan 40`,
sortie gardée hors dépôt). Modèle binormal (mauvais ~ N(0, 1), bons ~ N(√2·Φ⁻¹(aire), 1)), autant de bons que de mauvais :

| bons = mauvais | aire vraie | valeur critique de U | niveau exact | puissance du test (p < 0,05) | P(aire estimée ≥ 0,75) | critère D1 (les deux) |
|---|---|---|---|---|---|---|
| 6 | 0,5 / 0,8 / 0,9 | 29 | 0,0465 | 0,047 / 0,568 / 0,867 | 0,089 / 0,710 / 0,937 | 0,047 / 0,568 / 0,867 |
| 8 | 0,5 / 0,8 / 0,9 | 49 | 0,0415 | 0,042 / 0,676 / 0,944 | 0,053 / 0,720 / 0,957 | 0,042 / 0,676 / 0,944 |
| **10** | 0,5 / 0,8 / 0,9 | 73 | 0,0446 | 0,043 / **0,782** / 0,982 | 0,031 / 0,730 / 0,972 | **0,031 / 0,730 / 0,972** |
| 12 | 0,5 / 0,8 / 0,9 | 102 | 0,0444 | 0,045 / 0,852 / 0,992 | 0,018 / 0,735 / 0,978 | 0,018 / 0,735 / 0,978 |
| 16 | 0,5 / 0,8 / 0,9 | 173 | 0,0469 | 0,048 / 0,936 / 1,000 | 0,009 / 0,755 / 0,990 | 0,009 / 0,755 / 0,990 |

(Les cases 0,65 et 0,75 sont dans la sortie : à 10 contre 10, puissance du test 0,285 et 0,607.) **Combien de témoins pour
distinguer une discrimination de 0,8 de 0,5 ?** Avec le test seul, il faut environ 10 à 12 témoins par classe pour une
puissance de 0,8 à une aire de 0,8 (0,78 à 10, 0,85 à 12), au niveau exact de 0,045. Le critère D1 ajoute un seuil de 0,75 sur
l'aire estimée : il protège contre une conclusion sur une aire faible mais significative, et plafonne la puissance à une aire
vraie de 0,8 vers 0,73 à 0,76 quelle que soit la taille (le seuil est proche de la valeur visée) ; il atteint 0,97 à une aire de
0,9 et ne se déclenche à tort que dans 3,1 % des tirages quand l'aire vraie vaut 0,5. Le plan retient 10 contre 10 : au-delà,
le devis (section 12) ne tient plus dans 30 USD avec le juge B.

**Le plan joué par des juges scriptés** (« bruite », sans biais de position ; ancien protocole indulgent ; 40 graines de course
par ligne ; même commande) — c'est la puissance du **plan** (graphe 3-régulier, deux ordres, ancres, tirage 2, paires mélangées
de B), pas celle d'un juge réel, dont l'exactitude par comparaison est inconnue :

| exactitude par comparaison (les deux juges) | aire v2 moyenne (décile bas) | D1 | D4 | D5 | D6 | issues sur 40 |
|---|---|---|---|---|---|---|
| 0,65 | 0,725 (0,61) | 0,375 | 0,45 | 1,0 | 0,10 | I3 : 25, I4 : 14, I1 : 1 |
| 0,75 | 0,838 (0,73) | 0,875 | 0,70 | 1,0 | 0,325 | I4 : 27, I1 : 8, I3 : 5 |
| 0,85 | 0,933 (0,84) | 1,0 | 0,975 | 1,0 | 0,825 | I1 : 32, I4 : 8 |
| 0,95 | 0,974 (0,93) | 1,0 | 1,0 | 1,0 | 1,0 | I1 : 40 |

Lecture : le plan conclut I1 de façon fiable si les juges ont une exactitude par comparaison d'au moins 0,85 sur les paires
mélangées ; entre 0,75 et 0,85, le critère d'accord D6 (16 à 25 paires mélangées pour B dans ces 40 tirages, kappa imprécis)
fait basculer souvent vers I4 : **un I4 porté par D6 seul, avec D1 et D4 tenus, se lit comme « accord non établi »**, pas comme
un échec de discrimination. À ces effectifs (au plus 26 paires mélangées), le kappa des paires est imprécis ; D6 est le critère le plus fragile du plan.

## 6. Critères de lecture gelés et issues écrites d'avance

Calculés par `lire_validation` sur les mesures, sans autre lecture. Juge A, témoins d'évaluation.

| critère | définition | seuil |
|---|---|---|
| D1 | aire v2, tirage 1, et Mann et Whitney unilatéral | aire ≥ 0,75 et p < 0,05 |
| D2 | part de notables de l'ancien, tirage 1 (« l'ancien sature ») | ≥ 0,80 |
| D3 | aire v2 − aire ancien (tirage 1), DeLong unilatéral | ≥ 0,15 et p < 0,05 |
| D4 | la discrimination se reproduit au tirage 2 | aire ≥ 0,75 et p < 0,05 |
| D5 | biais de position : écart de la part des victoires de la première présentée à 0,5 (deux tirages) | ≤ 0,10 |
| D6 | kappa des paires mélangées entre A et B | ≥ 0,30 ; « non mesuré » si la phase de B est incomplète ou à moins de 0,85 de comparaisons valides |

**Validité de l'instrument** (sinon I0) : phase décisive de A complète ; part des comparaisons valides de A ≥ 0,85 à chaque
tirage ; au moins 18 verdicts lisibles de l'ancien sur 20.

**Issues, dans cet ordre :**
- **I0 — non jugeable** : la validité ne tient pas (ou arrêt avant la fin de la phase de A). Aucune conclusion sur les
  protocoles ; suite : diagnostic de l'instrument (relais, consigne, citations), nouveau texte.
- **I3 — le v2 ne fait pas mieux** : D1 non tenu. I3a si D2 tenu (les deux protocoles échouent : l'outil n'est pas la
  bonne réponse ou les juges ne lisent pas le dossier) ; I3b sinon (l'ancien n'est même pas au plafond). Suite : ne pas adopter
  le v2 ; examiner les réponses brutes (critère, citations) avant toute retouche.
- **I4 — le v2 discrimine mais n'est pas fiable** : D1 tenu et l'un de D4, D5, D6 (mesuré) non tenu ; les critères manquants
  sont nommés. Suite : pas d'adoption en l'état ; plus de comparaisons ou autre juge, sur nouveau texte.
- **I1 — le v2 discrimine là où l'ancien sature** : D1, D4, D5, D6 (ou non mesuré) tenus et D2 tenu ; I1a si D3 tenu (gain
  mesuré sur l'ancien), I1b sinon. Suite : proposer à Lazar l'adoption du v2 pour le prochain tour (nœud : modification de
  l'instrument), avec les réserves de la section 10.
- **I2 — le v2 discrimine, l'ancien ne sature pas ici** : comme I1 mais D2 non tenu ; I2a / I2b selon D3. Lecture : sur ces
  témoins servis avec leur dossier, le plafond du second tour ne se reproduit pas ; ce qui manquait peut être l'information
  plutôt que le protocole. Suite : pas de conclusion sur le second tour ; proposer une course où l'ancien protocole est servi
  avec la question seule (sans dossier), sur nouveau texte.

Réserve écrite d'avance : D6 non mesuré → « accord entre juges non mesuré » joint à I1, I2, I4.

## 7. Audit de symétrie (R4), écrit d'avance

Déclencheurs (`audit_symetrie`), symétriques : aire v2 ≥ 0,98 ou ≤ 0,55 ; Spearman ≥ 0,98 ou ≤ 0,30 ; kappa des paires ≥ 0,90
ou ≤ 0 ; part de notables de l'ancien = 1 ou ≤ 0,20 ; aucune bascule sur au moins 30 paires vues dans les deux ordres, ou
bascule ≥ 0,75. Un déclencheur, quel que soit son sens, impose **la même liste** de vérifications, faite par un lecteur neuf
avant que l'issue ne soit lue : recalcul indépendant depuis le journal scellé ; six réponses brutes tirées au hasard par juge et
par protocole ; garde A4 rejouée sur chaque entrée (aucune étiquette de classe, de rôle, d'auteur) ; modèle servi et nombre
d'appels conformes au plan ; empreinte des matériaux et contrôle de forme rejoués ; ordres de présentation conformes ; résultat
par classe (un résultat porté par une seule classe, par exemple les textes longs, est dit). L'issue n'est pas changée par
l'audit ; ses constats sont des réserves.

## 8. Liste d'arrêt (chaque garde essayée sur un cas sain et un artefact, R5 ; essais nommés au rapport)

- **Avant tout appel et toute écriture (code 2)** : texte hors du chemin fixé, brouillon, non scellé, à marqueur, code ≠ code
  gelé, fermeture incomplète ; plan non conforme (clés, valeurs fixes, consigne v2 ≠ code, plafond > 30 USD, parts hors du
  plafond) ; graine ou option de plan en ligne de commande ; configuration d'une autre empreinte ; GO autre, absent, d'un autre
  montant, d'un autre type, échu ou révoqué ; variable de clé dans l'environnement ; matériaux d'une autre empreinte, vérité
  connue non établie, forme favorable aux bons témoins, étiquette interdite ; pièce absente ou altérée ; lot réel qui ne passe
  pas la garde A4 ; juge de la famille des gabarits, juges de même famille ; relais absent ; devis au-dessus de la part d'un juge
  ou du plafond ; durée haute au-dessus de 6 heures ; porte de plafond qui n'accuse pas sa part.
- **Pendant la course (code 3 ; journal, mesures et lecture « partielle » scellés)** : plafond de dépense (aucun appel dont le
  budget ne tient plus dans le reste) ; **projection** des étapes décisives restantes au prix observé (moyenne des appels du
  juge dès trois appels, prix du plan avant) au-delà du reste, vérifiée avant chaque étape décisive ; durée de 6 heures ; modèle
  servi absent ou différent (A2) ; plus de la moitié de réponses inexploitables sur les 20 derniers appels d'un juge dans un
  protocole ; étiquette interdite dans une entrée.
- Phase descriptive : non jouée (consigné) si sa projection dépasse le reste ; jamais un arrêt.

## 9. Lectures préalables déclarées

Avant ce brouillon, le rédacteur a joué des courses **à blanc** (juges scriptés, aucun appel) et des simulations du plan
(section 5), et a lu les sorties de ces courses : elles ont servi à choisir le plan (graphe 3-régulier, paires mélangées pour
B, critère de reproduction plutôt que corrélation de rangs pour D4, biais de position par la part du premier plutôt que par la
bascule, seuil de D6 à 0,30). Aucune donnée réelle n'a été vue ; les 12 fiches réelles n'ont pas été lues ; aucun appel de
modèle n'a été fait. Les prédictions ont été écrites après ces courses à blanc, qui ne disent rien des juges réels.

## 10. Portée (ce que l'expérience ne dit pas)

- Rien sur la qualité des idées réelles : le lot réel est décrit, pas jugé.
- Les témoins sont des gabarits dans deux mondes plantés, servis avec un dossier de faits ; les fiches réelles n'ont ni dossier
  de ce type ni vérité connue. Un succès dit que le protocole **peut** faire départager quand l'information existe, pas qu'il
  départage les fiches réelles.
- Deux juges (Argon, Astra) : rien sur Kimi ni sur Claude comme juges. Le rôle de B est réduit (un tirage, paires mélangées).
- L'ancien protocole est rejoué avec le dossier inséré sur les témoins : ce n'est pas l'entrée exacte du second tour.
- Plan creux (graphe 3-régulier) : une fiche qui ne rencontre que des fiches de sa classe garde une force peu informative ; les
  ancres peuvent s'inverser dans un lot (en simulation, à exactitude 0,85, 4 lots sur 60). Une variante « ancres en étoile »
  (chaque fiche contre les deux ancres) a été simulée : gain faible pour environ 2,5 USD de plus (rapport, section 2).
- Les gabarits sont écrits par un modèle de la famille Claude ; aucun juge de cette famille ici, mais une familiarité de style
  entre gabarits et juges d'autres familles n'est pas mesurée.
- Coût du v2 en production : par lot de n fiches et degré d, n·d appels par juge et par tirage (deux ordres) contre n pour
  l'ancien ; non évalué ici au-delà du devis.

## 11. Code gelé

Fermeture des imports du chemin réel (`FICHIERS_GELES` du lanceur, mesurée par l'essai `Fermeture`) ; le lanceur refuse un
bloc qui ne la couvre pas exactement ou dont une empreinte diffère du fichier présent. À remplir au scellement (marqueur).

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

**Prix.** Argon 0,062 USD par appel et environ 8 s ; Kimi 0,35 USD et environ 16 min (mesurés le 2 novembre, chiffres
transmis par la session ; non revérifiés ici). Astra (`gpt-6-astra`) et Opus 5.5 : **non mesurés** ; le devis prend pour Astra
le taux de plan 0,25 USD par appel du plan A1-bis de l'attaque de Goodhart v3 (`pole/attaque_goodhart_v3.py` du commit
`d15f489c`, sha256 `447024a84b7eb87f6c8ae7acb8e0657353b89f935de364990f975ca4f0dca77c`, lignes 80-81 ; fichier en cours chez un
autre agent, modifié depuis dans l'arbre de travail), qui est un taux de devis, pas une mesure. Un appel par paire porte deux fiches au lieu d'une : le devis compte « appels × prix
par appel » comme demandé ; l'écart réel est surveillé par la projection au prix observé (section 8).

| phase | juge | appels | USD (prix de devis) |
|---|---|---|---|
| décisive A | Argon | 164 | 10,17 |
| décisive B | Astra | 20 + au plus 26 paires (42 dans la course à blanc de référence ; 36 à 45 sur 40 tirages simulés) | au plus 11,50 |
| réel, ancien | Astra ; Argon | 12 ; 6 (lot de substitution : 6 fiches d'auteur Kimi hors fusion) | 3,00 ; 0,37 |
| réel, v2 | Astra ; Argon | 12 ; 6 | 3,00 ; 0,37 |
| **total** | | au plus 246 (242 dans la course à blanc de référence) | **au plus 28,41** (27,41 dans la course à blanc de référence) |

**Maximum** (lot réel de 13 fiches, 26 paires mélangées pour B) : Argon 190 appels (11,78 USD, part 12), Astra 72 appels
(18,00 USD, part 18) : **29,78 USD ≤ plafond 30 USD**. Le lanceur recalcule ce devis sur les étapes réelles (après le tirage des
graines) et refuse de partir s'il dépasse une part ou le plafond.

**Durée** (séquentielle, bornes de temps par appel du plan : Argon 8 à 40 s, Astra 10 à 120 s) : 0,57 à 4,2 heures pour la
course à blanc de référence ; plafond 6 heures.

**Options écartées, pour la décision de GO :**

| juges | appels du plan | devis | pourquoi pas |
|---|---|---|---|
| Argon (A) + Astra (B), retenue | au plus 246 | au plus 28,41 USD (lot réel de 12 fiches) | prix d'Astra à confirmer (projection au prix observé) |
| Argon (A) + Kimi (B) | B : 20 + 16 à 26 paires + 24 | B seul 21,0 à 24,5 USD ; total 31,9 à 35,4 | au-dessus du plafond ; 60 à 70 appels d'environ 16 min : 16 à 19 h séquentielles |
| Kimi (A) | A : 164 + 12 | ≥ 61,6 USD | hors plafond ; 47 h séquentielles |
| Argon (A) + Opus 5.5 (B) | comme Astra | comme Astra (taux de plan identique) | famille de l'auteur des gabarits des témoins : refusé par le code |

## 13. Avant la course

Contre-lecture neuve (R2) de ce brouillon, du module, des essais et du lanceur ; corrections éventuelles sur un brouillon 2 ;
recalcul des deux empreintes du bloc `plan-gele` et du bloc de la section 11 ; essais et banc de mutations rejoués sur l'arbre à
sceller ; configuration préparée par la session qui tient les clés (relais `argon` et `astra` avec porte de plafond,
`plafonds_session.juge`, pièces `consigne_juge`, `question_course_2`, `lot_reel_juges_idees_v2`) ; GO de Lazar au plafond exact
du texte ; `--verifier-seulement` ; puis la course, une seule fois. La lecture gelée est prononcée par un sous-agent neuf (R13),
puis soumise à Lazar.
