# Rapport de rédaction — étage des juges d'idéation, version 2 (protocole, code, essais, préenregistrement brouillon 1)

Rédigé le 2 novembre 2026, de 17:32 à 18:50 UTC (heures lues sur `date -u`), par un sous-agent concepteur neuf qui n'a écrit
ni `pole/juges_croises_v53.py`, ni `pole/juges_seulement_v1.py`, ni leurs consignes. Aucun commit, aucun compagnon `.sha256`
dans le dépôt, aucun fichier existant modifié (`git status --porcelain` : seuls des fichiers non suivis, les miens et ceux
d'autres agents), rien lu ni écrit sous `donnees/`, aucun `git fetch`, aucun appel de réseau ni de modèle ; Python lancé en
`nice -n 10 python3 -I -B`, pytest avec `-p no:cacheprovider`, `TMPDIR` dans le dossier temporaire de la session. Fichiers des
autres agents (`*attaque_goodhart_v3*`, `*tour_ferme_v63*`, `*nul_v9*`, `*brouillon4*`) : lus pour deux d'entre eux
(`demonstrations/attaque_goodhart_v3.py`, `pole/attaque_goodhart_v3.py`, comme modèles de lanceur et pour un taux de devis),
jamais touchés.

## 1. Diagnostic : pourquoi l'ancien protocole sature

Constat (README principal, ligne 125) : au second tour réel, 11 fiches sur 12 « notables », accord brut 0,92, kappa de Cohen nul.
Ce que le code montre (`pole/juges_croises_v53.py`, sha256 `c4c6ab12dc471eef078c116a4205a22d9b498da720ce71e37a0a6edae6c4239b`) :

1. **Critère conjonctif de forme.** « Notable » = tous les items vrais (`lire_verdict`, l. 48). Les items vérifient la présence
   de ce que le gabarit du proposeur demande (hypothèse, prédiction, test de mort…) : une fiche bien rédigée les satisfait
   tous. Le plafond est construit, pas observé par hasard.
2. **Jugement absolu, une fiche seule** (`entree_une_fiche`) : aucune référence de qualité connue dans le champ du juge, aucune
   contrainte de rareté (rien ne limite le nombre de notables), aucun choix forcé. Les juges fondés sur des modèles de langage
   sont connus pour être indulgents en notation absolue ; le protocole ne leur oppose rien.
3. **Forme plutôt que fond.** Le juge ne reçoit ni faits ni lois déjà établies ; il ne peut pas savoir qu'une loi est fausse ou
   redite. Aucune preuve n'est demandée : rien ne distingue un « vrai » réfléchi d'un « vrai » par défaut.
4. **Classement sans information au plafond** (`classement`, l. 117) : notable, nombre de juges notables, somme des parts
   d'items, puis l'identifiant — au plafond, le rang est l'ordre des identifiants.
5. **Accord mal mesuré au plafond** : `kappa_cohen` (l. 140) rend 1 quand l'accord attendu vaut 1 (deux juges toujours
   « notable » paraîtraient en accord parfait). La v54 corrige (`mesures_v54.kappa_cohen_v54`) ; la lecture de la course passe
   par la v53. Le kappa nul du second tour est, lui, juste : 12/12 contre 11/12 donne exactement 0 (essai
   `Statistiques.test_kappa_convention_v54_et_artefact_v53`).
6. **Même famille que l'auteur** : au second tour, chaque fiche avait un juge de sa famille (README, même ligne : 1,00 contre
   0,91 de notables).
7. **Étalonnage sur témoins de forme** (`etalonner_juges`, témoins « P » et « N » du pré-pilote, défauts plantés détectables par
   la forme) : réussir l'étalonnage ne dit rien de la capacité à juger le fond.

Ce diagnostic ne cite aucun chiffre de la littérature ; les propriétés générales invoquées (indulgence du jugement absolu, biais
de position et de longueur, préférence pour sa propre famille) sont des hypothèses que l'expérience mesure.

## 2. Choix du protocole v2 et motifs

Retenu (`pole/juges_idees_v2.py`) : **(a) comparaisons par paires à l'aveugle** sur un graphe 3-régulier tiré au hasard,
chaque paire servie dans les deux ordres pour le juge principal (biais de position mesuré, puis corrigé par l'effet γ du modèle) ;
note continue = **force de Bradley et Terry** avec effet de position, maximum de vraisemblance pénalisé ; **(b) ancres** : une
bonne et une mauvaise fiche de qualité connue par lot, servies à l'aveugle ; le verdict exige d'être au-dessus du milieu de
leurs forces ; **(c) témoins plantés** : deux mondes à loi plantée, 10 bons et 10 mauvais témoins d'évaluation (loi vraie neuve
honnête ; loi fausse bien rédigée, redite d'une loi établie, affirmation vraie par définition, texte long sans affirmation) ;
**(d) budget** : au plus le premier quart du lot est notable (plafond, pas quota) ; **(e) preuve citée** : le juge cite mot pour
mot un passage de la fiche choisie, absent de l'autre, et une ligne du dossier ; vérification mécanique, comparaison nulle sinon ;
**(f) famille** : un juge n'est jamais admis sur une fiche d'un auteur de sa famille (les gabarits des témoins sont d'un modèle
Claude : pas de juge Claude sur les témoins ; les fusions comptent les familles de leurs parents).

Motifs : le choix forcé rend le plafond impossible par construction (une des deux fiches gagne) ; la preuve citée oblige à
ancrer le choix dans le texte et le dossier ; les ancres donnent une échelle et un plancher (un lot sans bonne fiche ne produit
pas de notable) ; le budget borne les notables ; la règle de famille retire un biais connu ; Bradley et Terry donne une note
continue, comparable entre fiches d'un lot, et absorbe le biais de position moyen. Le dossier est servi **aux deux protocoles**
sur les témoins : sans lui aucun protocole ne peut savoir qu'une loi est fausse, et la comparaison mesurerait l'information,
pas le protocole.

Choix faits **après simulation** (courses à blanc, section 5), déclarés au texte (section 9) :
- **D4** = la discrimination se reproduit au second tirage (aire ≥ 0,75, p < 0,05), et non une corrélation de Spearman ≥ 0,70 :
  sur des témoins à deux niveaux de qualité, un juge qui sépare parfaitement les classes mais ordonne au hasard à l'intérieur
  plafonne à 0,752 (`plafond_spearman_binaire`) ; en simulation, un juge parfait n'atteignait 0,70 qu'environ 8 fois sur 10.
- **D5** = part des victoires de la première présentée (|écart à 0,5| ≤ 0,10, deux tirages de A), et non le taux de bascule : la
  bascule mêle biais de position et incertitude honnête sur les paires de même qualité (≈ 0,37 pour un juge juste à 0,85).
- **Juge B sur les paires mélangées seulement** (une bonne, une mauvaise ; au plus 13 par lot) et **kappa des paires orienté par
  l'empreinte de l'identifiant** : sur toutes les paires, l'accord est dominé par des pile-ou-face sur les paires de même classe ;
  orienté par l'ordre des identifiants, il est indéfini (les bons témoins portent les petits identifiants). Seuil de D6 à 0,30
  (au plus 26 paires : kappa imprécis).
- **Kimi exclu** des comparaisons (0,35 USD et 16 minutes par appel : hors plafond, section 6). Juge B = Astra (`gpt-6-astra`),
  troisième famille, prix non mesuré : protégé par la projection au prix observé.
- Une variante « ancres en étoile » (chaque fiche contre les deux ancres, cycle entre fiches) a été simulée sur 30 graines par
  point : aire 0,921 contre 0,918, lots aux ancres inversées 2 sur 60 contre 4 sur 60, issue I1 0,90 contre 0,80 à exactitude
  0,85 ; +24 appels d'Argon et +4 d'Astra (environ 2,5 USD) qui portent le devis maximal au-dessus de 30 USD. Écartée ici,
  proposée pour une version suivante.

Écarté : le classement de listes entières (positions plus fortes, contexte long) ; une échelle ancrée absolue (l'indulgence
reste possible) ; le jugement par juge de la famille de l'auteur.

## 3. Fichiers neufs et empreintes

| fichier (neuf) | rôle | lignes | sha256 |
|---|---|---|---|
| `pole/juges_idees_v2.py` | cœur pur : matériaux des témoins, consigne v2, entrées, citations, plan des paires, Bradley et Terry, verdicts, statistiques, compteur, jeu des deux protocoles, mesures, lecture gelée, audit, puissance, juges scriptés | 2 063 | `604c217b41e7b427e19a521c29cc1464844417c115ff4e6a97f214a535b58a3d` |
| `demonstrations/validation_juges_idees_v2.py` | lanceur : à blanc, puissance, réel (gardes, GO, configuration, relais, sorties scellées) | 598 | `1539d32425cbd7f2f5fefd64a7ba065c4078827a168df581f77560fcfa75129b` |
| `essais/test_juges_idees_v2.py` | 52 essais (36 sous-essais) | 858 | `086ca4a49633b81858e10e875ee3413cd531e657fc19cc9e4b83ea962de728ea` |
| `essais/mutations_juges_idees_v2.py` | banc de 46 mutations | 240 | `677f95c29b0608b1f2d968af52430d4bfaac0b3ed6890603daae7baab4952237` |
| `prereg/preenregistrement-juges-idees-v2-brouillon1.md` | préenregistrement, brouillon 1 (marqueurs `<<GO>>`, `<<CONFIGURATION_SHA256>>`, `<<EMPREINTE_DU_CODE>>`) | 437 | `d72750747c1d07b8fd5fe388e9c6208a150bc60f9eece0140efc76645fb307ef` |
| `prereg/rapport-redaction-juges-idees-v2.md` | ce rapport | — | (donnée dans le message de remise) |

Empreintes produites par le code : consigne v2 `6978f0a4778edd87f9059606420577c167a1ff8db2053ab56507d20a355039b4` ; matériaux
(graine 20261102) `c3eeb559f6ead1035f8a73a1daa5a5c16163ca635199327b34eeae95fc1f8479` (tentatives retenues : monde-1 0, monde-2
5) ; contrôle de forme : aire de la longueur 0,38, du nombre de chiffres 0,415 (seuil 0,65).

Sorties produites hors dépôt (dossier temporaire de la session) : `…/scratchpad/juges-v2/courses/` (quatre courses à blanc,
scellées par le lanceur), `…/scratchpad/juges-v2/puissance-v2.json` (tables du préenregistrement).

## 4. Essais et banc de mutations

`nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py` : **52 réussis, 36 sous-essais
réussis**, environ 8 s (Python 3.13.18, numpy 2.5.3, pytest 9.1.1). Suites voisines rejouées sans changement
(`test_v53_instruments.py`, `test_v56_corrections.py`) : 102 réussis, 1 ignoré (celui de l'arbre publié).

| classe | gardes et mesures (cas sain → artefact) |
|---|---|
| `Materiaux` | déterminisme, composition, vérité relue, forme → matériaux altérés, autre empreinte, table qui ne montre plus la vérité, loi fausse dont l'écart affirmé est trop petit, forme favorable aux bons témoins, étiquette « témoin » dans une fiche |
| `Entrees` | entrée de paire aveugle (ni identifiant interne, ni classe, ni rôle) ; ancienne entrée sans dossier identique octet pour octet à `fiches_v53.entree_une_fiche` → « ancre » dans une fiche, champ `identifiant` réservé, consigne ancienne ou v2 portant « témoin » (refus avant tout appel) |
| `Citations` | réponse valide, citation typographiquement différente (guillemets, apostrophe, espace insécable, casse) → identifiant inconnu, critère hors liste, citation inventée, prise dans l'autre fiche, commune aux deux, trop courte, citation du dossier absente ou inventée, aucun bloc |
| `Plan` | graphe régulier, connexe, sans doublon, déterministe ; deux ordres ; étapes v1 (20 + 144 appels pour A ; paires mélangées pour B) ; devis ≤ 30 → degrés impossibles, juge de la famille des gabarits, juges de même famille, juge A sur une fiche d'auteur Argon, fournisseur inconnu, lot réel de 14 fiches |
| `BradleyTerry` | forces et effet de position retrouvés sur données simulées ; juge de position pure → forces égales, γ > 1 → aucune comparaison, fiche hors du lot |
| `Verdicts` | budget, plancher des ancres, plafond et non quota → ancres inversées, égalité à la limite, ancre seule |
| `Statistiques` | aire, loi exacte de U, Mann et Whitney, DeLong, kappa (convention v54 ; la v53 rend 1 au plafond : constaté), Spearman et plafond binaire, puissance (niveau sous 5 %, monotone) |
| `Mesures` | **juge toujours « notable » détecté au plafond** (part 1,0, kappa non défini, audit) ; **juge parfait** (aire v2 ≥ 0,85, p < 0,01, gain sur l'ancien ≥ 0,35) ; **juge biaisé de position mesuré** (part du premier 1,0, bascule 1,0, γ > 1, D5 non tenu, aire < 0,7) ; kappa des paires non gonflé par la position ; juge verbeux mesuré ; citations fausses ou réponses illisibles → arrêt de validité ; lot réel décrit |
| `Lecture` | issues I0 à I4 atteintes ; D6 non mesuré → réserve ; audit symétrique (même liste de vérifications) ; seuils du texte = code |
| `Compteur` | dépense, prix observé, projection, durée, coût illisible ; arrêt par projection avant tout appel ou avant la suite de B ; phase descriptive non jouée ; erreur de relais → arrêt avec journal ; lot réel en liste ; modèle servi différent (A2) et suffixe de date admis |
| `LanceurABlanc` | course complète, six sorties scellées, rien hors de la sortie → graine hors bornes, absente, stratégie inconnue, GO à blanc, sortie non vide (rien écrit) ; arrêt → journal partiel scellé, lecture « partielle » I0 |
| `LanceurCheminReel` | `--verifier-seulement` (aucune écriture) ; course réelle avec commandes factices locales arrêtée par la garde de validité (20 verdicts anciens lus, 20 comparaisons nulles, modèle servi, entropie = empreinte du texte, parts accusées 12 et 18) → brouillon, non scellé, marqueur, code différent, fermeture incomplète, clé manquante, plafond > 30, parts > plafond, part sous le devis, consigne v2 autre, matériaux autres, valeur fixe autre, juge de famille Claude, relais absent, autre configuration, autre GO, option de plan, graine en réel, GO d'un autre montant, variable de clé |
| `Fermeture` | `FICHIERS_GELES` (62 fichiers) = imports du chemin réel mesurés dans un processus neuf |

**Banc de mutations** (`TMPDIR=… nice -n 10 python3 -I -B essais/mutations_juges_idees_v2.py`, environ 2 min) : **46 mutations,
46 tuées pour la raison attendue**, 0 tuée pour une autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin
avant et après : 48 essais visés, 0 en échec. Familles : preuve citée (6), gardes A4 et matériaux (4), plan et famille (4),
Bradley et Terry et verdicts (5), statistiques (7), compteur et arrêts (7), lecture et audit (3), lanceur (10). Trois mutations
d'un premier passage survivaient parce qu'une garde plus profonde (garde des adaptateurs pour les clés, contrôle des tables
avant celui des lois fausses, règle d'égalité avant le plancher) masquait la garde visée ; des essais ciblés les tuent
maintenant pour la bonne raison. Le banc recompile les fonctions dans les globales du module lui-même (une copie des globales
masquait les substitutions faites par les essais) et oublie les courses mémorisées avant chaque mutation.

## 5. Courses à blanc de bout en bout

Commande (graine 20261102, coûts fictifs égaux aux prix du devis, lot réel de substitution de 12 fiches factices) :
`python3 -I -B demonstrations/validation_juges_idees_v2.py SORTIE --a-blanc --graine 20261102 --strategie-a S_A --strategie-b S_B`.
Chaque course : 242 appels scriptés, 27,41 USD fictifs, six sorties scellées par le lanceur (sceaux vérifiés par `sha256sum -c`).

| scénario (A / B) | issue | ancien A : notables ; aire ; faux notables | v2 A : aire (p) ; notables ; faux notables | Δ aire (p) | tirage 2 : aire ; Spearman | position : part du premier ; bascule | kappa ancien | kappa paires mélangées (22) | prédictions tenues |
|---|---|---|---|---|---|---|---|---|---|
| **au plafond** : plafond / plafond | I3a | 1,00 ; 0,50 ; 1,00 | 0,50 (1,0) ; 0,00 ; 0,00 (ancres inversées dans les deux lots) | 0,00 (1,0) | 0,50 ; non défini | 1,00 ; 1,00 | non défini | 0,00 | 3 : P1, P2, P11 |
| **parfait** : parfait / parfait | I2b | 0,50 ; 1,00 ; 0,00 | 0,98 (< 0,001) ; 0,30 ; 0,00 | −0,02 (0,80) | 1,00 ; 0,84 | 0,50 ; 0,00 | 1,00 | 1,00 | 4 : P3, P7, P8, P10 |
| **bruité** : bruite / bruite (juste à 0,75, 10 % de penchant pour la première) | I3b | 0,55 ; 0,665 ; 0,40 | 0,59 (0,26) ; 0,25 ; 0,10 | −0,075 (0,66) | 0,87 ; 0,25 | 0,56 ; 0,37 | 0,06 | −0,09 | 2 : P8, P9 |
| juge indulgent dans l'absolu, exact par paires : indulgent / parfait | I1a | 1,00 ; 0,50 ; 1,00 | 0,98 (< 0,001) ; 0,30 ; 0,00 | 0,48 (< 0,001) | 1,00 ; 0,84 | 0,50 ; 0,00 | 0,00 | 1,00 | 10 : P1 à P10 |

Audit déclenché dans les quatre : « décevant » pour le plafond (aire 0,50, kappa 0, bascule 1,0) et le bruité (Spearman 0,25,
kappa −0,09), « trop beau » pour le parfait et l'indulgent (aire 0,98, kappa 1, aucune bascule) — même liste de vérifications.
Lecture : le juge au plafond est vu des deux côtés (l'ancien à 1,0 de notables, kappa non défini ; le v2 par la position,
forces égales, ancres inversées, aucun notable) ; le juge parfait fait discriminer les deux protocoles (I2 : rien à gagner du v2
quand le juge est déjà exigeant dans l'absolu) ; l'indulgent-mais-exact est le cas que le v2 vise (I1a, gain 0,48 sur
l'ancien) ; le bruité à 0,75 ne passe pas D1 sur ce tirage (aire 0,59), conformément à la table du plan (D1 tenu 7 fois sur 8 à
cette exactitude, sans penchant). Lot réel de substitution : décrit (12 fiches, B sur 12, A sur les 6 fiches d'auteur Kimi
hors fusion, v2 sans ancre). Empreintes des lectures scellées : plafond `9e4cddcc…`, parfait `0318ea50…`, bruité `90cb4e43…`,
indulgent `face6c0a…` (dossier `…/scratchpad/juges-v2/courses/`).

## 6. Devis

Argon 0,062 USD par appel (mesuré le 2 novembre, transmis) ; Astra 0,25 USD par appel (taux de devis du plan A1-bis,
`pole/attaque_goodhart_v3.py` du commit `d15f489c`, sha256 `447024a8…`, l. 80-81, **non mesuré**). Plan : Argon 176 appels (164 décisifs), Astra 20 + au plus 26 paires
+ 24 réels ; **devis 27,41 USD** dans la course de référence, **au plus 28,41 USD** pour un lot réel de 12 fiches, **29,78 USD**
au pire (13 fiches, 26 paires) ; plafond **30 USD** (parts 12 et 18). Durée séquentielle 0,57 à 4,2 heures ; plafond 6 heures.
Kimi en juge B : 31,9 à 35,4 USD et 16 à 19 heures ; en juge A : au moins 61,6 USD et 47 heures. Le prix réel d'un appel par
paire (deux fiches) d'Astra est inconnu ; la course s'arrête avant toute étape décisive dont la projection au prix observé dépasse
le reste du plafond.

## 7. Ce qu'une contre-lecture neuve doit vérifier en premier

1. **Vérité connue des témoins** : relire les deux dossiers et les 24 fiches (`materiaux-temoins-juges-idees-v2.json` de
   n'importe quelle course à blanc) : chaque bonne loi est-elle appuyée par sa table et absente des lois établies ; chaque loi
   fausse contredite ; chaque redite bien une redite (et non un raffinement) ; l'interaction lisible ; l'affirmation « vraie par
   définition » l'est-elle au vu du contexte du dossier ? `verifier_materiaux` refait ces contrôles, mais il est du même auteur
   que les gabarits.
2. **Indices hors dossier** : un juge peut-il séparer bons et mauvais **sans lire les tables** ? Les lois fausses portent toutes
   sur des caractéristiques peu plausibles a priori (heure, langue des commentaires, jour, système, navigateur) : un juge guidé
   par ses a priori réussirait sans vérifier un nombre. Le contrôle de forme (longueur, chiffres) ne couvre pas cette
   plausibilité ; une variante avec des lois fausses plausibles et des lois vraies surprenantes est peut-être nécessaire.
3. **Consigne v2** (`CONSIGNE_PAIRE_V2`) : ordre des critères, choix forcé, règle des citations (absente de l'autre fiche),
   aucune fuite (classe, existence de témoins) ; usage sur le lot réel, où le dossier est la question sans lignes de faits.
4. **Dossier inséré dans l'ancien protocole** : écart assumé (information égale) contre reproduction exacte du second tour ;
   conséquence sur I2 ; faut-il un bras « ancien sans dossier » (20 appels de A, environ 1,24 USD) ?
5. **Critères, seuils et ordre des issues** : D1 (0,75 et p), D4 (reproduction plutôt que Spearman), D5 (part du premier), D6
   (paires mélangées, 0,30, critère le plus fragile : à exactitude 0,85, I4 dans 8 tirages sur 40, D6 non tenu dans 7) — tous
   choisis après les courses à blanc (déclaré, section 9 du texte) ; un critère plus faible rendrait-il l'issue trop facile ?
6. **Paires du juge B choisies sur les étiquettes connues** (paires mélangées) : licite en validation, impossible en production ;
   effet sur le sens du kappa ; orientation de l'issue par l'empreinte de l'identifiant (`kappa_paires`).
7. **Devis et prix d'Astra** : taux de plan, non mesuré ; un appel par paire porte deux fiches et le dossier ; la projection au
   prix observé n'est vérifiée qu'avant chaque étape décisive (pas à chaque appel) ; parts 12 et 18 ; le maximum 29,78 USD
   suppose un lot réel d'au plus 13 fiches (garde `LOT_REEL_MAX`).
8. **Chemin réel du lanceur** : fermeture de 62 fichiers (chaîne `ideation_v8` incluse) ; substitutions `{REGISTRE}` et
   `--plafond-cumule-usd` ; étape de dépense par juge `juges_idees_v2/<étiquette>` à faire confirmer par la session qui tient
   les relais (comme pour l'attaque v3) ; seul un essai à commandes factices locales a été joué.
9. **Statistiques à recalculer à la main** : Bradley et Terry (crêtes 0,5, Newton avec recherche linéaire, arrondi à 10⁻⁹),
   DeLong (variance nulle → p = 0 si la différence est positive), Mann et Whitney exact ou approché avec égalités (l'ancien
   protocole produit surtout des égalités), kappa v54, plafond binaire de Spearman.
10. **Lot réel** : format attendu (liste ou `{fiches}`, `meta.fournisseur`, `origine`, `parents_fournisseurs`) ; une fusion sans
    parents dits prend toutes les familles (Argon n'y est jamais admis) ; garde A4 de la configuration avant tout appel ; v2 sans
    ancre (verdict relatif) ; aucune lecture décisive — vérifier que rien dans la lecture gelée ne dépend du lot réel.

Incident à déclarer : pendant le second passage du banc de mutations, une variable de chemin vide (erreur de ma commande, pas du
banc) a écrit sa sortie dans `/mutations-v1.txt`, à la racine du système de fichiers de la machine de session ; le fichier a été
déplacé dans le dossier temporaire de la session environ deux minutes plus tard (18:46 UTC). Rien d'autre n'a été écrit hors du
dossier temporaire et des six fichiers neufs. Hors de mon fait : `demonstrations/attaque_goodhart_v3.py` et
`pole/attaque_goodhart_v3.py` apparaissent modifiés dans l'arbre de travail depuis 18:40 UTC (agent en cours ; je ne les ai que
lus, et le texte cite la version du commit `d15f489c`).
