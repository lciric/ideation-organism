# Contre-lecture R2 n° 1 — préenregistrement de la validation des juges d'idéation v2 (brouillon 1) et code `juges_idees_v2`

2 novembre 2026, de 19:06 à 19:47 UTC environ (heures de `date -u`). Contre-lecteur neuf : je n'ai écrit ni le brouillon 1, ni son
rapport, ni `pole/juges_idees_v2.py`, ni le lanceur, ni les essais, ni le banc, ni l'étage des juges existant ni ses consignes.
Lecture seule du dépôt public `ideation-organism` (tête `e58cfec` au début, `08b1f17` à la fin par les commits d'autres agents ; les
six fichiers relus, suivis depuis `c15a073`, ont les mêmes empreintes aux deux têtes) ; aucun
commit, aucun compagnon `.sha256`, aucun fichier existant modifié, rien sous `donnees/`, aucun `git fetch`, aucun réseau, aucun
modèle ; Python sous `nice -n 10 python3 -I -B` (sauf quatre lectures de fichiers JSON d'une seconde, sans `nice`), pytest avec
`-p no:cacheprovider`, `TMPDIR` dans le bloc-notes de la session. Mes sondes, sorties et le constructeur des couples sont sous
`/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/cl-juges-v2/` (empreintes en annexe). Pour vérifier les
décisions de Lazar, j'ai lu sans rien y écrire `registres/go.md`, `registres/decisions.md` et `registres/etat.md` du dépôt de travail
(`/home/claude/controle-ia-travail`).

**Verdict : non scellable.** Les décisions de Lazar ne sont ni dans le texte ni dans le code (60 USD refusés par
`PLAFOND_MAX_USD = 30`, durée de 6 h, bras « ancien sans dossier » absent d'`etapes_v1`) ; deux défauts de fond : les témoins se
laissent classer sans lire une seule table (B1 : un juge scripté « sans tables » obtient l'issue I1a 16 fois sur 20), et le chemin
réel lit les statuts du relais comme des réponses du juge (B2 : A2 ne s'arrête pas, un refus de dépense devient un prix fictif) ;
Astra est hors du périmètre écrit du GO (B6) ; sept gardes de la liste d'arrêt n'ont pas d'essai d'artefact (B7). Le reste tient :
essais et banc rejoués à l'identique, statistiques recalculées à l'identique, vérité des 24 fiches juste, devis et puissance
reproduits. 40 couples (texte seul) ; le code doit changer, puis un brouillon 2 et une contre-lecture neuve du delta.

## 1. Fichiers lus, empreintes

| pièce (depuis `orchestrator/`) | sha256 | état |
|---|---|---|
| `prereg/preenregistrement-juges-idees-v2-brouillon1.md` | `d72750747c1d07b8fd5fe388e9c6208a150bc60f9eece0140efc76645fb307ef` | égale au rapport et à `c15a073` ; lu en entier (437 lignes) |
| `prereg/rapport-redaction-juges-idees-v2.md` | `31a8654c976f1e0ec16290096a903952819f4fd856e7151dd1e0aa88229bd82d` | égale à `c15a073` ; lu en entier, « dix points » d'abord |
| `pole/juges_idees_v2.py` | `604c217b41e7b427e19a521c29cc1464844417c115ff4e6a97f214a535b58a3d` | égale au rapport ; lu en entier (2 063 lignes) |
| `demonstrations/validation_juges_idees_v2.py` | `1539d32425cbd7f2f5fefd64a7ba065c4078827a168df581f77560fcfa75129b` | égale au rapport ; lu en entier |
| `essais/test_juges_idees_v2.py` | `086ca4a49633b81858e10e875ee3413cd531e657fc19cc9e4b83ea962de728ea` | égale au rapport ; lu en entier |
| `essais/mutations_juges_idees_v2.py` | `677f95c29b0608b1f2d968af52430d4bfaac0b3ed6890603daae7baab4952237` | égale au rapport ; lu en entier |
| `pole/juges_croises_v53.py` | `c4c6ab12dc471eef078c116a4205a22d9b498da720ce71e37a0a6edae6c4239b` | égale au texte ; `lire_verdict` l. 39-48, `classement` l. 117-127, `kappa_cohen` l. 133-140 |
| `../README.md` | `a5e6b8622fbd7b319d74a01b9d2208c13a1e89dc17cdc37c4f1d99db6dd4b298` | égale au texte ; ligne 125 dit bien 11 sur 12, 12/12 et 11/12, accord 0,92, kappa 0 |
| fonctions appelées | `fiches_v53.entree_une_fiche`, `fiches_v54.garde` (mode « préfixe », l. 25-45), `adaptateurs.AdaptateurCommandeExterne.lancer` (l. 721-775), `adaptateurs_v56.AdaptateurCommandeExterneV56.lancer` (l. 81-95) et `PortePlafondEnvironnement` (l. 120-139), `configuration_v55.verifier_go_v55` (l. 72-100), `ideation_v8.adaptateurs_reels_v56` (l. 59-81), `pole/attaque_goodhart_v3.py` à `e58cfec` (l. 64-74) | lues |

Arbre de travail : d'autres agents modifient `*tour_ferme_v63*` et ajoutent `*attaque_goodhart_v4*` ; aucun des fichiers ci-dessus
n'est touché (`git status --porcelain`).

## 2. Ce qui a été rejoué

- **Essais** : `TMPDIR=… nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py` → **52 réussis,
  36 sous-essais réussis**, 9,18 s, 19:06:51 à 19:07:00 UTC (Python 3.13.18, numpy 2.5.3, pytest 9.1.1). Égal au rapport.
- **Banc** : `TMPDIR=… nice -n 10 python3 -I -B essais/mutations_juges_idees_v2.py` → **46 mutations, 46 tuées pour la raison
  attendue**, 0 pour une autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin 48 essais, 0 échec avant et après ;
  19:07:07 à 19:08:12 UTC (sortie : `mutations.txt` du bloc-notes). Égal au rapport.
- **Mutations supplémentaires** (mécanique du banc du dépôt, essais visés : tout le module, 52 essais), sur des gardes de la liste
  d'arrêt que le banc ne vise pas : **7 survivantes sur 8** (B7), 19:22 à 19:26 UTC (`scripts/mutations_extra.py`).
- **Courses à blanc** (`--a-blanc --graine 20261102`, stratégies bruite/bruite et indulgent/parfait) : lectures scellées **égales à
  l'octet** à celles du rapport (`90cb4e43…`, `face6c0a…`), sceaux vérifiés par `sha256sum -c` ; mesures égales à la ligne
  « bruité » du rapport (ancien A 0,55 ; 0,665 ; 0,40 ; v2 A 0,59, p 0,264 ; Δ −0,075, p 0,661 ; tirage 2 0,87 ; Spearman 0,254 ;
  part du premier 0,5625 ; bascule 0,370 ; kappa ancien 0,0625 ; kappa des paires mélangées −0,091 sur 22 paires ; I3b).
- **Puissance** : cases du brouillon reproduites (10 contre 10 : U critique 73, niveau exact 0,0446, puissance 0,782, D1 0,730 ; aire
  0,9 : 0,982 et 0,972 ; aire 0,5 : 0,043 et 0,031) ; tailles 12 à 20 calculées (section 10).
- **Recalcul indépendant** (scipy 1.18.1 et énumération) de Bradley et Terry, Mann et Whitney exact et approché, DeLong, Spearman,
  kappa des paires, sur la course bruite/bruite : section 11.
- **Chemin réel avec commandes factices locales** (aucun réseau ; montage de l'essai `LanceurCheminReel`) : modèle servi différent
  et refus de dépense du relais (B2).
- **Matériaux** : les deux dossiers et les 24 fiches relus (`materiaux.txt`) ; indices de forme et juges « sans tables » (B1).

## 3. Décisions de Lazar : vérification

| décision | brouillon 1 | code | couples | reste à faire |
|---|---|---|---|---|
| GO de calcul `GO-2026-11-02-24`, **60 USD** exactement, parts à recalculer, « plafonds très larges » | absent : `<<GO>>` (l. 9, 151, 170), plafond 30 (l. 165, 222, 289, 415), parts 12 et 18 (l. 166-167) | **refuse 60** : `PLAFOND_MAX_USD = 30.0` (`demonstrations/validation_juges_idees_v2.py:67`, contrôle l. 190-191) ; vérifié : le bloc des couples est refusé « plafond 60.0 USD hors de ]0 ; 30] » (`scripts/plan_apercu.py`) | C2, C12 à C16, C28, C36, C38, C40 : plafond 60, parts **24 (Argon) et 36 (Astra)** | constante 60, docstring (l. 21), essai « plafond au-dessus de 30 » (`essais/test_juges_idees_v2.py:798`) et mutation à porter à 60 |
| registre | — | — | — | ligne 70 de `registres/go.md` : calcul, 60 USD, Lazar, du 2 au 16 novembre ; **périmètre écrit « relais Kimi et Argon »** (B6) |
| **aucun budget de temps qui coupe la mesure** | absent : `duree_max_h: 6` (l. 168), l. 293, 296, 419 | accepte toute valeur > 0 (l. 189-195) ; `verifier_devis` compare la durée haute (l. 335-336) | C14, C16, C29, C30, C37 : **garde de 48 h** | rien (le délai par appel de 1 800 s est dit, C37) |
| **bras « ancien sans dossier » ajouté** | absent (proposé en suite d'I2, l. 269-270) | absent : `etapes_v1` (`pole/juges_idees_v2.py:1273-1331`) ; `jouer_etape(…, avec_dossier_ancien=True)` (l. 1437-1438) n'est jamais appelé à `False` (l. 1524-1526) ; `_mesures_ancien` (l. 1547-1559) mêlerait les deux bras (aucun champ ne les distingue) | C4 à C6, C10, C11, C17, C23, C26, C27, C32, C34, C35 | code, essais, banc (B4) |

Pourquoi 48 h et non 24 h : la durée haute du devis est 4,4 h (4,7 h au maximum) mais la durée par appel d'Astra n'est pas mesurée
(10 à 120 s est une hypothèse ; Kimi mesure 16 min) ; les attentes sur relais injoignable demandées en B2 ajoutent du temps ; le
plafond de dépense borne seul le coût ; le nul v9 a pris 48 h, l'attaque v3 72 h (`registres/decisions.md` du dépôt de travail,
lignes 1240 et 1245). Pourquoi 24/36 : au maximum du plan (lot réel de 13 fiches, 26 paires mélangées), Argon 210 appels = 13,02 USD
et Astra 72 appels = 18,00 USD au prix du plan ; les parts laissent 1,8 et 2 fois ces montants ; elles couvrent aussi le plan à trois
mondes de I1 (18,72 et 23,75 USD).

## 4. Points bloquants

**B1 — Les témoins ne demandent pas de lire le dossier : le gabarit et l'a priori suffisent à les classer.**
Constat. Le texte dit « Les gabarits sont communs à toutes les classes, sauf le texte long » et « aucun indice de forme simple ne
favorise les bons témoins » (l. 97-99). C'est faux pour les matériaux du code : toutes les caractéristiques sans effet sont binaires
(`pole/juges_idees_v2.py:211-216`, `255-260`) ; toutes les lois fausses, ancres comprises, sont des `binaire_fausse`
(l. 229-230, 234, 273, 278) rédigées au gabarit de deux groupes (`_fiche_binaire`, l. 465-493) ; huit bonnes fiches d'évaluation
sur dix sont des lois graduées sur trois niveaux (`_fiche_monotone`, l. 428-462) ou des interactions. Mesures
(`scripts/forme.py`) : l'indice « loi graduée ou interaction » a une **aire de 0,80** entre bons et mauvais témoins d'évaluation,
l'indice « caractéristique non binaire » 0,70, au-dessus du seuil 0,65 de `controle_forme` (l. 680, 708-717), qui ne mesure que la
longueur et les chiffres. Un juge scripté qui **ne lit aucune table** — il préfère la loi graduée à la comparaison de deux groupes et
au texte long, écarte les fiches qui citent les deux caractéristiques des lois établies et celles qu'énonce la phrase de contexte
(« classe suspects », « score dépasse 70 ») — joue le plan entier sur 20 graines de course (`scripts/forme2.py`, ancien protocole
indulgent) : aire v2 moyenne 0,823 (minimum 0,68), **D1 tenu 16 fois sur 20, D4 20 sur 20, issue I1a 16 fois sur 20** ; s'il ajoute
l'a priori de plausibilité des caractéristiques nommées (heure, langue des commentaires, système, jour, navigateur, écran) : aire
0,865, **I1a 20 fois sur 20**. Les lois fausses sont la seule classe dont le constat exige un nombre des tables, et l'a priori les
écarte sans les tables.
Conséquence. D1 ne sépare pas H2 (« adossé à une citation vérifiée … du dossier ») de H0(a) « les juges ne lisent pas le dossier,
ou tranchent par la forme » (l. 52-53), alors que c'est sa raison d'être ; un I1 ne dirait rien de la capacité visée (P3 : « vérifier
un nombre contre une table », l. 65), et ne se transposerait pas aux fiches réelles, qui partagent toutes le même gabarit. La garde
« forme favorable aux bons témoins » de la liste d'arrêt (l. 291) laisse passer son propre artefact.
Correction (code et texte ; couples C7, C13, C29, C32). Rééquilibrer les matériaux : dans chaque monde, au moins une loi fausse au
gabarit gradué sur une caractéristique ordinale sans effet et **plausible** a priori, au moins une bonne loi au gabarit de deux
groupes sur une caractéristique d'effet vrai mais **peu plausible** a priori, une étiquette d'a priori par caractéristique fixée dans
le code ; étendre `controle_forme` (indice de gabarit, indice « caractéristique binaire », aire ≤ 0,65) ; ajouter un **contrôle de
diagnosticité** : le plan joué par un juge scripté « sans tables » (une stratégie de plus de `AdaptateurScripte`) sur 20 graines ne
doit pas tenir D1 plus de 2 fois, sinon refus avant tout appel ; son essai a pour artefact les matériaux du brouillon 1 (16 sur 20) ;
mutation qui retire le contrôle. Nouvelle empreinte des matériaux (marqueur `<<MATERIAUX_SHA256>>`, C13).

**B2 — Chemin réel : les statuts du relais sont lus comme des réponses du juge.**
(i) A2. La commande externe v56 rend le statut « refus » (et non « ok ») quand le modèle servi diffère du modèle demandé
(`pole/adaptateurs_v56.py:90-94` ; `pole/adaptateurs.py:767-771`) ; `appeler` ne contrôle A2 que sur « ok »
(`pole/juges_idees_v2.py:1414`) et lit tout autre statut comme une réponse vide (l. 1417). Vérifié avec une commande factice locale
qui rend `gemini-4-argon-lite` (`scripts/chemin_reel_a2.py`) : **aucun `ArretModeleServi`** ; 20 appels payés au modèle non autorisé,
comptés « réponses inexploitables », puis `ArretValidite` « instrument défaillant », code 3, issue I0. L'essai
`Compteur.test_artefact_modele_servi_different` (`essais/test_juges_idees_v2.py:626-630`) passe par l'adaptateur scripté, qui rend
« ok » : un chemin que l'adaptateur réel ne prend jamais. La garde « modèle servi absent ou différent (A2) » de la liste d'arrêt
(l. 296-297) ne tient donc pas sur le chemin réel.
(ii) Refus de dépense, relais injoignable, délai. Une commande qui sort en code non nul sans ligne de coût est comptée au plafond de
session (« coût inconnu », `pole/adaptateurs.py:751-764`) ; ce coût fictif entre dans le prix observé (`Compteur.prix`, l. 1390-1392).
Vérifié avec une commande factice qui sort en code 4 (refus de dépense avant envoi) : 10 appels, **5,0 USD comptés pour 0 dépensé**,
puis `ArretDevis` « projection 87,5 USD au prix observé », issue I0. Les codes réels du relais Argon comprennent 3 (relais ou
interface), 4 (budget sans envoi), 6 (délai, coût au pire cas), et le relais Argon ne sert qu'un appel à la fois (`registres/decisions.md` du
dépôt de travail, ligne 1241, R-1277) : une panne passagère, ou une autre course sur le même relais, fait perdre l'unique course
payante en I0, ou abaisse la part valide des comparaisons. L'attaque de Goodhart v3 traite déjà ces cas (`pole/attaque_goodhart_v3.py`
à `e58cfec`, l. 64-74 : attentes 15, 30, 60, 120 puis 300 s, au plus 1 800 s par tentative, code 4 lu « budget refusé », coûts
inconnus comptés à part).
(iii) Parts. Le compteur projette contre le reste du plafond total seulement (l. 1394-1401) ; la porte « environnement » donne la
part au relais comme plafond dur (`pole/adaptateurs_v56.py:130-136`) : un dépassement de part arrive comme refus du relais, donc (ii).
Conséquence : des issues I0 « par défaut de conception », contraires à la règle prise sur les mots de Lazar (« je ne veux pas de …
résultats non concluants par défaut de conception », `registres/decisions.md`, ligne 1240, R-1276) ; une garde A2 inopérante.
Correction (code et texte ; couples C9, C24, C30, C40). « refus » pour modèle servi → `ArretModeleServi` au premier appel ; code 4 ou
« budget_depasse » → `ArretDevis`, sans coût fictif dans le prix observé ; code 3 sans coût → même appel repris après attente (bornes
de l'attaque v3), jamais compté comme réponse du juge ; code 6 → appel perdu, compté à part ; projection par juge contre sa part ;
au-delà de 15 % d'appels perdus dans la phase décisive A → arrêt et I0 « infrastructure » ; aucune autre course sur le relais Argon
pendant la course ; un essai du chemin réel par statut (commandes factices, comme `scripts/chemin_reel_a2.py`) et une mutation chacun.

**B3 — Plafond de 60 USD : texte et code.** Voir section 3. Couples C2, C12 à C16, C28, C36, C38, C40 ; code : `PLAFOND_MAX_USD`
(l. 67) à 60, docstring l. 21, défaut à blanc l. 529, essai l. 798 et mutation « plafond au-dessus de 30 USD admis ».

**B4 — Bras « ancien sans dossier » : à écrire dans le texte et le code.** Voir section 3. Ce que portent les couples : une phase
`sans dossier (A)` (20 appels, 1,24 USD au prix du plan) jouée **après** les phases décisives A et B et avant le lot réel, projetée
comme une étape décisive, **hors** de la validité et de l'issue principale (l'issue I0 ne dépend pas d'un bras auxiliaire) ; entrée de
la forme du second tour (`entree_ancienne(…, dossier=None)`, déjà égale octet pour octet à `fiches_v53.entree_une_fiche`, essai
`Entrees.test_entree_ancienne_sans_dossier_identique_a_la_v53`) ; graines propres (`ordre-ancien-sans-dossier|…`,
`anonymisation-sans-dossier|…`) ; prédictions P12 (part de notables sans dossier ≥ 0,80 et aire ≤ 0,65) et P13 (effet du dossier sur
la part de notables ≥ −0,10) ; critère D7 (part de notables sans dossier ≥ 0,80, « non mesuré » sous 18 verdicts lisibles) ; lecture
gelée **S0 à S3**, jointe à l'issue sans la changer (S1 : le dossier lève le plafond ; S2 : sature avec et sans ; S3 : ne sature pas
même sans dossier) ; descriptifs « effet du dossier sur l'ancien » et « gain total » ; suite d'I2 récrite (la course sans dossier
qu'elle proposait est maintenant dans celle-ci). Le seuil de D7 reprend `plafond_ancien_min` et `presents_ancien_min` : la ligne
`seuils` du bloc gelé ne change pas. Code : étape, champ du journal qui distingue les bras, mesures, `lire_validation`,
`predictions_v1`, essais (cas sain : 20 appels, entrée de la v53 ; artefacts : bras incomplet → S0 ; S1 à S3 atteints), mutations.

**B5 — Garde de durée.** Voir section 3 (6 h → 48 h, garde contre une boucle folle). Texte seul (C14, C16, C29, C30, C37).

**B6 — Juge B : Astra est hors du périmètre écrit du GO ; nœud de Lazar avant le scellement.** La ligne du GO dit « course chez
session-depot (relais Kimi et Argon) » (`registres/go.md` du dépôt de travail, ligne 70) ; le plan sert Astra (`gpt-6-astra`,
l. 103-104, 157). Contexte : « n'utiliser les modèles chers que quand on est sûr d'obtenir des résultats positifs » (R-1236, ligne
1200) ; Astra soumis à la règle des trois temps pour A1-bis (R-1266, ligne 1230) ; compte OpenAI sans crédit le 1er novembre (R-1066,
ligne 1030 ; état actuel inconnu ici) ; prix d'Astra « 10/50 supposé » par million de jetons (R-1251, ligne 1215), jamais mesuré. Et
les raisons du brouillon d'écarter Kimi en juge B tombent (l. 426 : « au-dessus du plafond », « 16 à 19 h ») : avec 60 USD et la garde
de 48 h, Kimi en B tient (33,1 à 36,6 USD avec le bras sans dossier) ; il reste sa fiabilité (A1 : 5 appels réussis, 616 en échec,
`registres/etat.md`, ligne 3). Décision (nœud : dépense hors du périmètre écrit) : (a) Astra, avec le mot de Lazar inscrit au registre
et le crédit et le relais d'Astra confirmés par session-depot — avantage : relais fiable a priori, troisième famille ; inconvénient :
modèle cher, prix inconnu ; (b) Kimi — avantage : dans le périmètre écrit ; inconvénient : D6 très probablement « non mesuré » au vu
d'A1. **Recommandation : (a)**, confiance moyenne ; pas de défaut sous 48 h (nœud). Couples C8 (marqueur `<<MOT_DE_LAZAR_ASTRA>>`),
C38, C39, C40.

**B7 — R5 : sept gardes de la liste d'arrêt sans essai d'artefact.** Mutations supplémentaires, toutes survivantes à la suite entière
(52 essais, 0 échec) : durée haute au-dessus de la durée maximale admise (`validation_juges_idees_v2.py:335-336`) ; lot réel non
soumis à la garde A4 de la configuration (l. 366-368) ; pièce de la configuration absente admise (l. 354-356) ; texte au bon nom hors
du dossier fixé admis (l. 210) ; A2 : modèle servi absent admis (`pole/juges_idees_v2.py:1414`) ; `duree_max_h` nulle admise (l. 194) ;
juges A et B sur le même relais admis (l. 174). La huitième (garde A4 de l'entrée complète retirée) est tuée par
`Entrees.test_artefacts_etiquette_et_champ_reserve`. Le texte promet « essais nommés au rapport » (l. 285) ; le rapport nomme des
classes, pas un essai par garde (section 8 ci-dessous). Précédent de la maison : B10 de la contre-lecture 3 du tour fermé
(`prereg/contre-lecture-preenregistrement-tour-ferme-v3.md`). Correction : un essai d'artefact par garde, tué par sa mutation ; la
table de la section 8, complétée, au rapport du brouillon 2.

## 5. Points importants

**I1 — Puissance : un résultat négatif n'est pas concluant à la taille du plan.** Recalcul (`scripts/puissance.py`, graine 20261102,
20 000 répétitions) : à 10 témoins par classe, D1 (aire ≥ 0,75 et p < 0,05) a une puissance de 0,73 à une aire vraie de 0,80 — la
valeur que prédit P3 — : I3 sort une fois sur quatre quand le v2 marche comme prévu ; I3 n'exclut qu'une aire de 0,9 (0,97). D4 a la
même définition sur le tirage 2 : D1 et D4 ensemble sont plus rares encore ; le plan joué par des juges « bruite » justes à 0,75 donne
I1 dans 8 courses sur 40 (I4 dans 27, brouillon l. 231). Pour la « phrase visée » (le v2 discrimine à une aire de 0,8), le test
seul atteint 0,9 à **14 témoins par classe (0,90), 15 (0,93)** ; D1 tel qu'écrit n'atteint 0,9 à 0,8 sous 60 USD pour aucune taille
(0,77 à 20 par classe : le seuil de 0,75 est trop près de 0,8), il l'atteint à une aire de 0,85 dès 14 (0,91). Recommandation :
**15 contre 15 (trois mondes)** — devis maximal ≈ 42,5 USD au prix du plan (Argon 302 appels, 18,72 USD ; Astra 95, 23,75 USD), dans
les parts 24/36 — et **D4 à 0,70** (reproduction, pas découverte : puissance 0,89 à 15 contre 15) ; le troisième monde se construit
avec le rééquilibrage de B1. La règle prise sur les mots de Lazar (« tailles fixées par la décision à permettre », R-1276) plaide pour.
Proposer avec recommandation (périmètre interne), défaut sous 48 h : 15 contre 15 et D4 à 0,70. Dans tous les cas, I3 doit dire sa
portée : couples C20, C21, C22, C25.

**I2 — La consigne v2 nomme exactement les défauts plantés.** `CONSIGNE_PAIRE_V2` (l. 135-145) énumère loi contredite, redite d'une loi
établie, affirmation vraie par définition, texte sans affirmation réfutable, et dit que la longueur ne compte pas : ce sont les quatre
classes mauvaises et la classe « longue » ; le même auteur a écrit la consigne et les témoins. Aucune fuite littérale (ni classe, ni
rôle, ni auteur, ni identifiant interne dans l'entrée : essai `Entrees.test_cas_sain_consigne_et_entree_paire_aveugles` ; la garde A4
en mode préfixe passe sur la consigne et les 24 fiches). Mais la comparaison mesure un protocole dont la consigne vise les défauts
plantés, contre un ancien protocole qui juge des items de forme. À dire dans la portée (C32). Recommandé : une classe de défaut **que
la consigne ne nomme pas** (par exemple : prédiction de signe contraire à son hypothèse, ou loi vraie mais étrangère au domaine du
dossier), une fiche par monde, lue par classe (descriptif).

**I3 — Réglages de raisonnement des juges non dits.** La commande Astra exige `--effort` et `--reflexion` (R-1251, ligne 1215) ;
l'effort décide de la capacité à vérifier une table et du coût ; il n'est gelé que par l'empreinte de la configuration et n'est dit
nulle part. Marqueur `<<REGLAGES_DES_JUGES>>` (C8).

**I4 — La consigne figée de l'ancien juge doit passer la garde des témoins.** `exiger_entrees` sert la consigne privée de la course 2
avec la liste `ETIQUETTES_INTERDITES_TEMOINS` en mode préfixe (l. 88-91, 787-799) : « copie », « fausse », « témoin », « ancre »… y
sont des débuts de mot (« copier », « fausses », « ancrée » sont refusés). Si la consigne privée en porte un, la course est refusée
après le scellement. À faire vérifier par la session qui tient les pièces avant le scellement (C40).

**I5 — Sens de D6.** Sur des paires mélangées, deux juges indépendants justes à p ont un kappa voisin de (2p − 1)² : D6 ≥ 0,30 revient à
une exactitude d'environ 0,77 pour chacun ; c'est une exactitude jointe plus qu'un accord. Les descriptifs « toutes les paires » et
« paires de même qualité » annoncés (l. 194-195) sont respectivement égaux au premier et **vides par construction** (le juge B ne voit
que des paires mélangées ; vérifié : statut « vide », n = 0). Couple C18.

## 6. Points mineurs

- **M1** — `kappa_cohen` : la définition est l. 133, le retour fautif l. 140 (l. 30 du texte ; le module dit « ligne 133 »). C3.
- **M2** — « quelle que soit la taille » (l. 220) : faux en général (0,73 à 10, 0,75 à 15, 0,77 à 20 ; tend vers 1). C21.
- **M3** — Taux de bascule de `position_a` : `biais_position` groupe par paire **tous tirages confondus** (l. 1174, appelé l. 1644) ;
  une paire tirée aux deux tirages a quatre enregistrements et sort du compte. Course bruite/bruite : 9 paires communes, bascule
  20/54 = 0,370 au lieu de 27/72 = 0,375 groupée par (tirage, paire). Touche P8 et le déclencheur d'audit « aucune bascule sur au
  moins 30 paires », pas D5. Code : grouper par (tirage, paire) ; C19.
- **M4** — R6 : prix d'Argon (0,062 USD), de Kimi (0,35 USD, 16 min) et fiabilité de Kimi sans chemin ni empreinte (l. 399-400).
  Marqueur `<<SOURCES_DU_DEVIS>>` (C33).
- **M5** — `lot_reel_depuis` (l. 1233-1254) ne refuse pas un identifiant réel égal à celui d'un témoin ; `_mesures_ancien` filtre par
  identifiant seul (l. 1548). Improbable ; un refus coûte une ligne.
- **M6** — Deux seuils de « saturation » : D2 à 0,80, l'indicateur descriptif `au_plafond` à 0,90 (`SEUIL_PLAFOND`, l. 1228, 1559).
  Sans effet sur la lecture ; à dire ou aligner.
- **M7** — Gardes vérifiées ailleurs mais non nommées : GO d'un autre type, échu, révoqué (`essais/test_v53_instruments.py:95`, et
  les essais v54 et v55) ; porte de plafond qui accuse faux (`essais/test_v56_corrections.py:238`). À citer dans la table du rapport.

## 7. Complétude R1

| élément | où | état |
|---|---|---|
| hypothèse | section 2 (H1 à H3, H0 a à c) | présente ; H2 et H0(a) inséparables par D1 tant que B1 tient |
| prédictions chiffrées et signées | section 3 (P1 à P11) | présentes, ouvertes dans les deux sens ; P12 et P13 pour le bras sans dossier (C6) |
| métriques | section 5 | présentes ; bras sans dossier (C17) ; descriptifs vides dits (C18) |
| seuils | section 6 (D1 à D6) | présents ; D7 (C23) |
| plan d'analyse | sections 5 et 6, `mesurer`, `lire_validation` | présent ; recalculé à l'identique (section 11) |
| critères de lecture gelés, ordre des issues | section 6 (I0, I3, I4, I1, I2) | défendables (voir ci-dessous) ; I3 trop affirmatif (C25) ; lecture S0 à S3 (C27) ; I0 « infrastructure » (C24) |
| liste d'arrêt | section 8 | présente ; statuts du relais absents (B2) ; 7 gardes sans artefact (B7) |
| audit de symétrie (R4) | section 7 | présent, même liste dans les deux sens (`Lecture.test_audit_symetrique`) |
| graines (R9) | section 4 | présentes ; tâches du bras sans dossier (C11) |
| chiffres → chemin et empreinte (R6) | section 12 | manquants pour les prix (C33) |

Seuils et ordre des issues, choisis après les courses à blanc (déclaré, l. 301-307) : défendables pour un **positif** — D1 ne se
déclenche à tort que 3,1 fois sur 100 sous une aire de 0,5, D5 (|part du premier − 0,5| ≤ 0,10) est à plus de trois écarts types
d'un juge sans biais sur 288 comparaisons, D6 est dit fragile et sa défaillance seule se lit « accord non établi » ; l'ordre I0 > I3 >
I4 > I1/I2 est le bon. Pas concluants dans l'autre sens : I3 à 27 % sous l'aire prédite (I1), et un I1 ne prouve pas la lecture du
dossier tant que B1 tient. Aucun seuil n'est trop faible au point de rendre l'issue facile ; c'est l'inverse.

## 8. Liste d'arrêt : gardes et essais (R5)

| garde (texte, section 8) | cas sain | artefact | état |
|---|---|---|---|
| texte hors du chemin fixé | `LanceurCheminReel.test_cas_sain_verifier_seulement_aucune_ecriture` | « brouillon » (bon dossier, mauvais nom) | **bon nom hors du dossier : aucun** (mutation survivante) |
| brouillon ; non scellé ; marqueur ; code ≠ code gelé ; fermeture incomplète | idem ; `Fermeture.test_fichiers_geles_egaux_a_la_fermeture` | `test_artefacts_du_chemin_reel` : « brouillon », « non scellé », « marqueur restant », « code différent », « fermeture incomplète » | essayées |
| plan : clés, valeurs fixes, consigne v2, plafond, parts | idem | « clé de plan manquante », « valeur fixe différente du code », « consigne v2 autre », « plafond au-dessus de 30 » (à porter à 60), « parts au-dessus du plafond » | essayées |
| graine ou option de plan en ligne de commande | idem | « graine en réel », « option de plan en réel » | essayées |
| configuration d'une autre empreinte | idem | « autre configuration » | essayée |
| GO autre ; d'un autre montant ; absent ; autre type, échu, révoqué | idem | « GO autre que celui du texte » ; `test_artefacts_go_et_environnement` (25 USD) ; absent : aucun (masqué par le contrôle « autre ») ; type, échéance, révocation : `essais/test_v53_instruments.py:95` (non nommé) | essayées sauf « absent » |
| variable de clé dans l'environnement | idem | `test_artefacts_go_et_environnement` (`GH_TOKEN`) | essayée |
| matériaux : autre empreinte, vérité non établie, forme, étiquette | `Materiaux.test_cas_sain_deterministe_composition_et_garde` | « matériaux autres » ; `Materiaux.test_artefact_verite_non_etablie`, `…forme_favorable…`, `…etiquette_interdite…` | essayées ; contrôle de forme incomplet (B1) |
| pièce absente ou altérée | — | **aucun** (mutation survivante) | B7 |
| lot réel qui ne passe pas la garde A4 | — | **aucun** (mutation survivante) | B7 |
| juge de la famille des gabarits ; juges de même famille ; même relais | `Plan.test_cas_sain_etapes_v1` | « juge de la famille des gabarits » ; `Plan.test_artefacts_juges_…_de_meme_famille` ; même relais : **aucun** | B7 (même relais) |
| relais absent | idem | « relais du juge absent » | essayée |
| devis au-dessus d'une part ; du plafond | idem | « part sous le devis » ; plafond total : redondant (parts ≤ plafond) | essayée |
| durée haute au-dessus de la durée maximale ; `duree_max_h` > 0 | — | **aucun** (deux mutations survivantes) | B7 |
| porte de plafond qui n'accuse pas sa part | cas sain réel (parts accusées 12 et 18) | `essais/test_v56_corrections.py:238` (non nommé) | essayée ailleurs |
| plafond de dépense ; projection ; durée (pendant) | `Compteur.test_cas_sain_et_artefacts_du_compteur` | idem ; `Compteur.test_arret_par_projection` | essayées |
| modèle servi différent ; absent (A2) | `Compteur.test_artefact_modele_servi_different` (suffixe de date admis) | adaptateur scripté seulement ; absent : **aucun** | **inopérante sur le chemin réel** (B2) ; absent : B7 |
| réponses inexploitables | — | `Mesures.test_artefacts_citations_fausses_ou_reponses_illisibles_arretent` | essayée |
| étiquette interdite dans une entrée | `Entrees.test_cas_sain_consigne_et_entree_paire_aveugles` | `Entrees.test_artefacts_etiquette_et_champ_reserve` | essayée (fonction ; pas en cours de course) |
| erreur d'un relais ; phase descriptive non jouée | — | `Compteur.test_artefact_erreur_d_un_relais_arrete_avec_le_journal` ; `…phase_descriptive_non_jouee…` | essayées |
| statuts du relais (code 3, 4, 6 ; « refus ») | — | **aucun** | B2 |

## 9. Vérité connue des 24 fiches (point 1 du rapport)

Relue sur les deux dossiers (`materiaux.txt` ; `verifier_materiaux` rend une liste vide ; empreinte `c3eeb559…`, tentatives 0 et 5) :
- **Bonnes** (12, ancres comprises) : chaque chiffre affirmé est la table arrondie (par exemple monde-1-02 : 13 % → 24 %, D13 13,1 et
  D15 24,0 ; monde-2-04 : 29 % contre 19 %, D20 28,7 et (207 + 188)/(1 035 + 1 006) = 19,4 %) ; aucune ne porte sur une
  caractéristique des lois établies ; les interactions se lisent sur la table 2 (monde-1 : 14,7 → 35,2 dans les mises à jour de
  dépendances, 13,5 → 15,2 ailleurs ; monde-2 : 17,4 → 42,7 sur les réseaux sociaux, 19,0 → 20,8 ailleurs). Nuance : les lois
  marginales monde-1-01 (fichiers) et monde-2-01 (redirections) sont vraies en marge mais entièrement portées par l'interaction ;
  elles restent bonnes, et le juge peut leur préférer l'interaction (paire de même classe, sans effet sur l'aire). Seule incohérence
  de rédaction : monde-1-03 dit « environ 24 % … environ 12 % …, soit un écart d'environ 13 points » (arrondis séparés de 24,4, 11,7
  et 12,6) ; un juge pointilleux peut la lire comme une erreur de chiffre dans une bonne fiche (le gabarit gradué, variante 2, le
  permet aussi pour monde-2-02, ici cohérente) — bruit qui joue contre le v2, à garder ou corriger au rééquilibrage.
- **Fausses** (5) : l'écart affirmé (6 à 8 points) est contredit par une table plate (heure 18,3 contre 17,1 ; langue 17,4 contre
  18,0 ; système 17,7 et 17,7 ; jour 22,2 contre 22,5 ; navigateur 22,6 contre 22,0) ; le taux de base cité est juste, l'autre faux.
- **Redites** (3) : monde-1-09 et monde-2-08 quantifient R1, monde-2-09 recopie R2 presque mot pour mot. La quantification n'est pas un
  raffinement au sens de la consigne : les bonnes fiches ne font pas plus (elles quantifient une table) ; la classe ne tient qu'au
  critère de nouveauté de la consigne — c'est la classe la plus difficile, comme le dit P10.
- **Vraies par définition** (2) : vraies au vu de la phrase de contexte (alerte exactement quand « suspect » ; quand le score dépasse
  70). Le « 100 % » qu'elles attribuent au dossier n'est sur aucune ligne : il découle de la définition.
- **Textes longs** (2) : identiques d'un monde à l'autre (jamais servis ensemble) ; le critère d'abandon (« aucune configuration à
  plus d'un point ») est pratiquement irréfutable.
Aucune erreur de classe. Le défaut est ailleurs (B1).

## 10. Puissance (modèle binormal, test de Mann et Whitney unilatéral exact à 5 %, graine 20261102, 20 000 répétitions)

| témoins par classe | U critique | niveau exact | test, aire 0,8 | D1 (0,75), aire 0,8 | D1 (0,75), aire 0,85 | D1 (0,70), aire 0,8 | D1 (0,70), aire 0,5 |
|---|---|---|---|---|---|---|---|
| 10 | 73 | 0,0446 | 0,782 | 0,730 | — | 0,782 | 0,043 |
| 12 | 102 | 0,0444 | 0,852 | 0,735 | 0,897 | 0,852 | 0,045 |
| 14 | 135 | 0,0469 | 0,901 | 0,742 | 0,910 | 0,870 | 0,035 |
| 15 | 153 | 0,0488 | 0,928 | 0,749 | 0,916 | 0,891 | 0,032 |
| 16 | 173 | 0,0469 | 0,936 | 0,755 | 0,923 | 0,890 | 0,027 |
| 18 | 215 | 0,0485 | 0,961 | 0,772 | 0,929 | 0,909 | 0,020 |
| 20 | 262 | 0,0482 | 0,973 | 0,774 | 0,941 | 0,917 | 0,015 |

(À 10 contre 10, U critique 73 correspond à une aire de 0,73 > 0,70 : D1 à 0,70 y vaut le test seul.) Taille qui donne ≥ 0,9 sous
60 USD : 15 contre 15 pour le test (0,93) ; pour D1 tel qu'écrit, aucune à une aire de 0,8, 14 à une aire de 0,85.

## 11. Recalcul à la main (course à blanc bruite/bruite, graine 20261102 ; `scripts/recalcul.py`)

- **Bradley et Terry** réajusté par un autre algorithme (L-BFGS de scipy, même vraisemblance pénalisée, crêtes 0,5) sur les 36
  comparaisons valides de chaque lot et chaque tirage du juge A : γ égal à 10⁻⁶ près (monde-1 0,612177, monde-2 0,542026) ; écart
  maximal des forces centrées 1,0 × 10⁻⁸ sur deux lots et deux tirages.
- **Aire** du v2 (A, tirage 1) : 0,59 (U = 59 sur 100). **Mann et Whitney exact** par énumération des 184 756 partitions des 20 rangs :
  p = 0,264424430059105, égal au module et à scipy.
- **Ancien protocole** (égalités) : aire 0,665 ; approximation normale corrigée (égalités, continuité) p = 0,0842467, égal à scipy.
- **DeLong** (composantes structurelles réécrites) : différence −0,075, variance 0,0325278, p = 0,661239 : égaux au module.
- **Spearman** entre tirages : 0,254135, égal à scipy. **Kappa des paires mélangées** recalculé : −0,0909 sur 44 jugements appariés.
- **Position** : part du premier 0,5625 sur 144 ; bascule 20/54 (module) contre 27/72 groupée par tirage (M3).

## 12. Couples

`prereg/couples-contre-lecture-juges-idees-v2-v1.json` : 40 couples `{"ancien", "nouveau"}`, dans l'ordre d'application ; chaque
« ancien » est un texte exact du brouillon 1, présent une seule fois, et le reste au moment de son application (aucun recouvrement) ;
construits et vérifiés par `couples/construire.py` du bloc-notes ; aperçu du texte obtenu : 511 lignes, `f2a7b1a7…`, six marqueurs
(`<<MATERIAUX_SHA256>>`, `<<MOT_DE_LAZAR_ASTRA>>`, `<<REGLAGES_DES_JUGES>>`, `<<SOURCES_DU_DEVIS>>`, `<<CONFIGURATION_SHA256>>`,
`<<EMPREINTE_DU_CODE>>`), plus aucune trace de 30 USD, de 6 heures ni de `<<GO>>`.

| couples | objet | point |
|---|---|---|
| C1, C2 | statut ; marqueurs ; GO-2026-11-02-24 | B3, B6, I3, M4 |
| C3 | lignes de `kappa_cohen` | M1 |
| C4, C5, C6 | bras sans dossier (section 1, H0(b), P12, P13) | B4 |
| C7 | gabarits et a priori, rééquilibrage, contrôle de diagnosticité | B1 |
| C8, C9 | Astra et le GO, Kimi, réglages des juges ; A2 sur « refus » | B6, I3, B2 |
| C10, C11 | étape et graines du bras sans dossier | B4 |
| C12 à C16 | lancement, bloc gelé (matériaux, 60/24/36, 48 h, GO), paragraphe sous le bloc | B1, B3, B5 |
| C17, C18, C19 | mesures du bras ; kappa et descriptifs vides ; bascule par tirage | B4, I5, M3 |
| C20, C21, C22 | puissance à 0,9 ; « quelle que soit la taille » ; portée d'une issue négative | I1, M2 |
| C23 à C27 | D7 ; I0 « infrastructure » ; I3 ; suite d'I2 ; lecture S0 à S3 | B4, B2, I1 |
| C28 à C30 | liste d'arrêt : plafond 60 ; gardes avant tout appel ; statuts du relais, parts, 48 h | B3, B1, B7, I4, B2, B5 |
| C31, C32 | lectures préalables de la contre-lecture ; portée | B4, I2, B1 |
| C33 à C39 | devis : sources, ligne et total du bras, maximum, durée, options | M4, B4, B3, B5, B6 |
| C40 | avant la course : garde A4 de la consigne ancienne, relais Argon seul, GO, mot de Lazar | I4, B2, B6 |

Ce que les couples ne couvrent pas (code, essais, banc, avant un brouillon 2) : B1 (matériaux rééquilibrés, `controle_forme` étendu,
contrôle de diagnosticité et sa stratégie scriptée, nouvelle empreinte) ; B2 (statuts du relais, projection par part, pertes
d'infrastructure, essais du chemin réel) ; B3 (`PLAFOND_MAX_USD`) ; B4 (phase, journal, mesures, lecture S0 à S3, P12, P13) ; B7
(sept essais d'artefact) ; M3 (bascule par tirage) ; puis l'empreinte de la consigne v2 inchangée à revérifier, le bloc de la section
11 à recalculer, essais et banc rejoués. Si I1 est retenu (trois mondes, D4 à 0,70), les sections 3 à 5 et 12 sont à récrire par le
rédacteur (les couples décrivent le plan à deux mondes).

## 13. Avant le scellement, dans l'ordre

1. Mot de Lazar sur le juge B (B6) ; s'il retient Astra : ligne au registre, crédit et relais d'Astra confirmés par session-depot.
2. Code : B1, B2, B3, B4, B7, M3 ; essais, banc, courses à blanc rejoués ; rapport du brouillon 2 avec la table de la section 8
   complétée (un essai par garde).
3. Couples appliqués au brouillon 1 → brouillon 2 ; décision I1 (taille, D4) ; marqueurs remplis sauf ceux de la session qui tient les
   clés.
4. Contre-lecture neuve du delta (matériaux, chemin réel, bras sans dossier) — R2.
5. Session qui tient les pièces : consigne ancienne contre la garde des témoins (I4), configuration (réglages des juges, I3), aucune
   autre course sur le relais Argon ; `--verifier-seulement` ; scellement ; course, une seule fois.

## Annexe — sondes de la contre-lecture (bloc-notes `…/scratchpad/cl-juges-v2/`)

| fichier | sha256 | rôle |
|---|---|---|
| `scripts/materiaux.py` | `e6eb5f76518e300ebe771b0f49f599003c75c3ac5fd753b173465169cdfc9e0f` | dossiers et 24 fiches (`materiaux.txt`, `fee4be35…`) |
| `scripts/puissance.py` | `7c569a37678fde16306038e70508f47f52bdfd6f876f5edbafb3458028387dad` | cases du brouillon et tailles 12 à 20 |
| `scripts/forme.py` | `80e60436b59afdd9f0f443c62017cae1fac0ce4114d3d068b5747204b4675bab` | indices de gabarit ; juge « de forme » |
| `scripts/forme2.py` | `74cd9f17cab8c63a10111b5f051bd073629a0d1a6a1ad1d16e98258fc18ada34` | juge « sans tables », avec et sans a priori (B1) |
| `scripts/recalcul.py` | `739f30ba73d29aeae19d38d82f01d18079ec57be752953e86186b5f5ecef2fd5` | recalcul indépendant (section 11) |
| `scripts/chemin_reel_a2.py` | `685cfae249bf58eedb885beb5fd819daa6663ed1dba1c087c39764c10e8f8892` | chemin réel factice : « refus » et code 4 (B2) |
| `scripts/mutations_extra.py` | `39f584badf0432fdceb74c88ef80f8fe03d0319591ecd25b6d23800e349d0a0d` | huit mutations de gardes (B7) |
| `scripts/plan_apercu.py` | `b1667006767655ad3d591c33f7e2bd2dba1f14c46d1a5c73d34b71dcb6621fb9` | bloc gelé des couples lu par le lanceur actuel (refus à 60 USD) |
| `couples/construire.py` | `a257b3652abb8795e4440541f8b116947b57dc309779c38a57c56ae6846bea12` | construction et contrôle des 40 couples |
| `mutations.txt` | `dfe0dcf9dbf15bb7d9e318d9580e5789199c6c991bb4c60afadeec18e1dd0649` | sortie du banc du dépôt |
| `courses/bruite-bruite/journal-juges-idees-v2.json` | `6a874fea38c4e523fd688091e91ecc52975caa6e3eb6d2f9829ccaa38572569e` | journal de la course recalculée |
