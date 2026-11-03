Scellable après couples (18, `prereg/couples-contre-lecture-attaque-goodhart-v3-brouillon4.json` : texte seulement ; plan gelé, bloc d'empreintes, code, essais et banc inchangés), le marqueur `<<COMMIT_V3_1>>` restant à remplir par le directeur avec `9776ed0efee97146182ff2c4b409e5ec224a0bbf` (vérifié : les 73 empreintes du bloc sont celles de ce commit et du disque).
Aucun bloquant : B1, VL-01, VL-02 et VL-04 sont levés, chacun avec un essai sur un cas sain et sur un artefact et une mutation tuée pour la bonne raison ; « arrêt sur tout code 4 » est juste pour ce plan (aucune source de code 4 n'y est passagère ; le quota de l'interface revient en code 3, non en code 4) ; la configuration gelée passe VL-01 ; brouillon 4 = brouillon 3 + 42 couples + v3.1, rien d'autre.
Importants I1 à I4 — écriture au pire cas des erreurs de l'interface (plafond encore atteint après ≈ 6 à 12 h de panne, ou ≈ 4 à 20 % d'appels en échec, ou une erreur permanente attendue jusqu'au plafond), réglages propres du relais non chiffrés, empreinte de la commande non exigée au lancement, contrôle du relais promis par la section 0.4 mais absent du point 7 — couverts par les couples (déclaration et alerte écrite d'avance) ; mineurs M1 à M9 ; le texte de la v4 doit changer (section 6).

# Contre-lecture courte R2 n° 2 — A1-v3 : code v3.1 (commit `9776ed0`) et brouillon 4 du préenregistrement

3 novembre 2026, de 00:57 à 01:35 UTC (heures de `date -u`). Contre-lecteur neuf : je n'ai écrit ni le code de l'attaque v3 ou v3.1,
ni son lanceur, ni ses préenregistrements, ni les contre-lectures précédentes, ni la vérification du lanceur. Lecture seule des deux
dépôts ; aucun commit, aucun `.sha256`, aucun fichier existant modifié, rien sous `donnees/`, aucun `git fetch`, `checkout` ni
`stash`, aucun appel de réseau ni de modèle ; calculs sous `nice -n 10 python3 -I -B`. Le dossier de la course décisive
(`resultats/banc-tricheurs-v9-validation-v1/`) n'a été ni ouvert ni listé ; aucun essai n'a lancé de course factice longue (banc
entier en 76 s). Deux fichiers neufs dans le dépôt : celui-ci et le fichier des couples ; scripts et sorties dans le bloc-notes
`/tmp/cl-a1v3-1-b4/` (empreintes en section 10).

Abréviations : **B3**, **B4** = brouillons 3 et 4 (`prereg/preenregistrement-attaque-goodhart-v3-brouillon3.md`, `…-brouillon4.md`) ;
**B3c** = B3 avec les 42 couples ; **C31**, **L31** = `pole/attaque_goodhart_v3.py` et `demonstrations/attaque_goodhart_v3.py` au
commit `9776ed0` ; **VL** = vérification du lanceur (`verification-lanceur-a1v3-v1.md`) ; **T** = texte scellé d'A1.

## 0. Pièces lues, empreintes vérifiées

| pièce | sha256 (vérifié) | lu |
|---|---|---|
| B4 | `6841b6c4c7eeca73279168d85b8dc3abfc5e998aa9923597d7240612170b32c3` | en entier |
| B3 ; couples n° 1 | `e2c28eed…` ; `e5f669e4…` | par application et différence |
| contre-lecture n° 1 et rapport privé de son auteur | `01a2041a…` ; — | en entier (B1, I1 à I7, M1 à M10) |
| rapport v3.1 (`prereg/rapport-redaction-attaque-goodhart-v3-1.md`) | `6b30c04bf6f8f8ee8cd3b280286c6a901153205d056e217526806d14478d2e52` | en entier (dix points, incident du banc) |
| VL ; n° 294 de session-depot | `7ffe45ab…` ; `81e601fa…` | en entier (VL-01 à VL-09 ; section 3) |
| C31, L31 | `cb9cffe7…`, `87d52ace…` | `git diff e58cfec 9776ed0` en entier, fonctions touchées en entier |
| essais, banc v3.1 | `8ab42fe0…`, `96ade331…` | différence en entier |
| v4 : cœur, lanceur, texte (brouillon 2) | texte `7be8589e…` | ce qui touche la v3 |
| configuration v3 de session-depot | `e5306c47…` | en entier (section 5) |
| registres privés | — | lignes de GO-2026-11-02-21 et -22 ; R-1286, R-1293, R-1294, R-1299 |
| T | `fc81d015…` | lignes 119 à 127 |
| cœur et lanceur v2, `pole/adaptateurs.py`, `demonstrations/ideation_v8.py`, `essais/test_attaque_goodhart_v2.py` | — | lignes citées par B4 |

Les quatre fichiers v3.1 et B4 sont identiques au commit `9776ed0`, à la tête `63ed933` et sur disque (`git diff` vide).

## 1. Rejoué

- `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_attaque_goodhart_v3.py essais/test_attaque_goodhart_v4.py` :
  **101 réussis, 199 sous-essais, 0 échec** (01:01:46 à 01:02:54 UTC) : 74 essais v3.1 (compte par analyse syntaxique) et 27 v4,
  et 199 sous-essais, le total des 126 + 73 annoncés (répartition non séparée).
- Banc, une fois : `nice -n 10 python3 -I -B essais/mutations_attaque_goodhart_v3.py --raisons` : **49 mutations, 49 tuées pour la
  raison attendue**, 0 pour une autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin 33 essais sans échec avant et
  après ; code 0 (01:03:10 à 01:04:26 UTC). Essais v2 : non rejoués.
- Après ces passages, `git status` restreint à `orchestrator/` : vide ; aucun fichier plus récent sous `orchestrator/`.

## 2. Question 1 — B1, VL-01, VL-02, VL-04 ; « arrêt sur tout code 4 »

| constat | garde | cas sain | artefact | mutation (raison relevée) | levé |
|---|---|---|---|---|---|
| B1, attente | `appeler`, C31:417-433 | `DelaiEtAppelCoupe.test_code_3_cout_pire_cas_attend_comme_au_plancher` (40 s au pire cas : 15 + 30 s, loi lue, journal égal au plancher) | `RelaisInjoignable.test_appel_coupe_attente_puis_echouee` (onze appels, 1 800 s, « échouée (relais) ») ; `ArretAuPlafond.test_panne_de_l_interface_attend_puis_arret_au_plafond` | 41 : « unexpectedly None » au sous-essai `cout=1.61` | oui |
| B1 et VL-04, arrêt | C31:414-416 ; `Compteur.arreter_sur_refus_de_budget`, C31:298-321 | code 5 et budget par appel dépassé sans code 4 : aucun arrêt (`CodesDeSortie.test_code_4_compte_budget_depasse_puis_arret`) | registre simulé au plafond : 17 acceptés, 18ᵉ refusé, « plafond » ; loin du plafond et à la part ; lanceur à blanc, code 3, trace scellée (`ArretAuPlafond.*`, `LanceurABlanc.test_course_a_blanc_plafond_atteint_arret_code_3`, `…_code_4_arret_et_trace_partielle`) | 42 : « ArretAttaque not raised » ; 43 : motif « part » au lieu de « plafond » ; 47 : `KeyError: 'interrompue'` ; 48 : « 12 != 18 » appels ; 49 : premier arrêt écrasé ; 24 réalignée : « ['erreur'] != ['budget_depasse'] » | oui |
| VL-01 | `exiger_substitutions`, L31:302-333, appelée à L31:359 | `--registre {REGISTRE}` et `--registre={REGISTRE}` | dix formes refusées ; lanceur en `--verifier-seulement` : code 2, rien écrit (`LanceurCheminReel.test_substitutions_des_commandes_exigees`) | 44 : « AttaqueRefusee not raised » (registre à chemin fixe) ; la vérification de bout en bout ne passe plus que par `--verifier-seulement` : une mutation ne peut plus lancer de course (incident du premier passage du banc corrigé) | oui ; configuration gelée conforme (section 5) |
| VL-02 | `lire_relais_perdu`, L31:237-247 | « AUCUN », « 0,5 », « 72 » | `inf`, `nan`, `-1`, `1e306` (texte) ; `inf`, `nan` (à blanc) | 45 : « PreenregistrementRefuse not raised » (cas `inf`) | oui |

Le registre simulé des essais (réglé + pire cas > plafond) est exact à un fil (aucun engagé en vol). Sur le vrai registre et le code v3,
VL (section 3.6) a vu le premier refus à 398,40 USD réglés, le compteur comptant la même somme : sous la v3.1, 398,40 + 1,8 > 400, nature
« plafond » ; la revérification sur la v3.1 reste à demander (couple 15).

**« Arrêt sur tout code 4, même loin du plafond »** — juste pour ce plan. Sources de code 4 de la commande `221df610…` (n° 287, n° 294) :

| source | passagère ? | sous la v3.1 | sous la v3 |
|---|---|---|---|
| garde cumulée ou d'étape du registre (réglé + engagé + pire cas > 400, dès ≈ 398,39 USD réglés) | non : le réglé ne fait que croître ; à un fil, aucun engagé en vol (les réservations d'appels muets restent engagées : monotone aussi) ; au plus un appel de plus passerait (pire cas d'une consigne courte ≈ 1,61 contre ≤ 1,8) | arrêt « plafond », code 3, trace complète ; seconde course admise (section 8) | suite de refus en millisecondes, cases vidées, code 0 (VL 3.6 : 664 acceptés, 3 828 refus) |
| relais, HTTP 402 (`--plafond-usd`) | non : réservation au pire cas sous verrou, monotone pendant la vie du relais ; relais monofil et un seul fil : la réservation précédente est réglée avant la suivante | à ≥ 400 USD, mord avec ou après le registre (« plafond ») ; plus bas (80 USD d'A1, par exemple), arrêt « refus_de_budget » à ce niveau, propre ; seconde course | suite de refus, cases vidées |
| relais, HTTP 429 (`--max-appels`) | non : compte d'appels monotone ; seul `--max-appels` rend 429 (n° 294 : aucune autre limite dans le relais) | même lecture ; borne à chiffrer (couple 16) | idem |
| plafond de session (l. 303, 306) | déterministe par consigne | **exclu ici** : la consigne la plus longue possible (tentative 16, 15 lois de 6 000 octets ; une loi plus longue n'entre dans l'historique que par son motif, C31:506) tient sous 1,8 USD (VL 3.6) ; c'est le seul code 4 pour lequel arrêter coûterait plus que continuer (la v3 n'y perdait que la fin d'une suite) | refus local |
| registre étranger (chemin fixe portant une course antérieure) | non | **exclu** par VL-01 et le dossier de sortie neuf | refus dès le premier appel |
| quota de l'interface (HTTP 429 de Google) | oui, mais **ce n'est pas un code 4** : code 3 au pire cas (n° 294) | attendu (15, 30, 60 s…, tentative non consommée) ; un quota à la minute coûte un à trois appels comptés (≈ 1,6 à 4,8 USD) ; un quota quotidien ou une clé refusée : ≈ 33,9 USD comptés par heure jusqu'au plafond (I1) | deux appels par tentative, puis B1 |

La règle deviendrait fausse avec un relais qui rendrait un quota passager en 402 ou 429 (relais suivants : Kimi, Claude, Astra) : à
revérifier relais par relais (remarque R2). Avec plusieurs fils, la nature « plafond » se dégrade en « refus_de_budget » près du plafond
(engagé en vol), l'arrêt restant juste : sans objet ici.

## 3. Question 2 — B4 = B3 + 42 couples + v3.1, et rien d'autre

- **Couples** : application refaite ; chaque « ancien » présent une seule fois dans B3 et au moment de son application ; B3c =
  `5507536934dfb733…`, égal au texte annoncé.
- **Renumérotation** : B3c contre la base renumérotée du développeur (`084781dc…`) : textes égaux une fois chaque suite de chiffres
  masquée ; 102 lignes changées, toutes par des nombres. Les 117 renvois de la table (`renvois-b4-table.json`, `baa7227b…`) contrôlés
  par programme contre `git show e58cfec:` et `git show 9776ed0:` : 112 bornes au même contenu ; les 5 autres, réécrits à la main, sont
  justes (L31:97, motif des marqueurs ; C31:417-433 et C31:417, attente ; L31:593-594, création du compteur ; le cinquième, section 14
  de B3, a disparu avec la section réécrite).
- **Échantillon à la main** : les 130 renvois de B4 vers C31 et L31 (renumérotés et neufs) relus contre la ligne visée du commit : tous
  justes ; une attribution ambiguë (l. 529 : `:298-321` implicite après une mention du lanceur, la fonction nommée étant celle du cœur ;
  couple 9). Renvois vers d'autres fichiers (lanceur v2 `:58`, `:185-196`, `:233-250`, ligne 248, `:300-306` ; cœur v2 `:777`,
  `:821-824` ; `pole/adaptateurs.py:622`, `:751-765` ; `demonstrations/ideation_v8.py:74` ; `essais/test_attaque_goodhart_v2.py:102-114`) : justes.
- **Changements v3.1** : base renumérotée → B4 : 64 blocs, tous dans la liste 0.1 ter. Au niveau des fonctions, la v3.1 ne touche que
  `Compteur`, `appeler`, `jouer_suite`, `jouer_unite`, `jouer_tout`, `ProposeurScripte`, `description`, `VERSION`, deux constantes
  (cœur), et `exiger_substitutions`, `reglages_de_configuration`, `lire_relais_perdu`, `principal`, `MARQUEUR`, options à blanc
  (lanceur) : lecture, juge, instrument, devis et graines intacts, comme écrit.
- **Bloc `empreintes-du-code`** : 73 lignes triées, égales aux fichiers de `9776ed0`, au disque et à `FICHIERS_GELES` lu dans un
  processus neuf ; les 71 lignes de T identiques ; seules changent les deux lignes v3.
- **Marqueurs** : `<<COMMIT_V3_1>>` exactement cinq fois (lignes 115, 311, 635, 1143, 1295), aucun autre double chevron ; seul
  identifiant de GO : GO-2026-11-02-21.
- **Scellement simulé** (copie `…-v3-v1.md`, marqueur rempli, compagnon par `ecrire_scelle`, dossier sous `/tmp`) : accepté (73
  empreintes, entropie ≥ 2⁶⁴, Argon, 400 USD, GO-21) ; refusé avec le marqueur, au nom de brouillon et sans scellement. Même
  résultat sur B4 corrigé par les 18 couples, marqueur rempli par `9776ed0efee9…` ; plan lu identique à B4.
- **Noms** : tous les essais cités existent (74 v3.1 ; la liste v2 de la section 8 égale les 45 essais v2), hors les quatre anciens
  noms de la liste des renommages ; table des mutations égale au banc sur ses 49 lignes (libellé, fichier, fonction, essai qui tue).
- **Courses à blanc** (L16) : sorties et manifestes à leurs empreintes (`5a874faa…`, `52a9337c…`, `cafd0300…`, `bc99d804…`, compagnons
  conformes) ; course à 40 USD : nature « plafond », 546 appels comptés = 546 dans la trace, un seul refus.

## 4. Question 3 — section 0.4, dispense M10, réponses I7

- **(a)** I6, **(c)** VL-04 et B1, **(d)** VL-05, **(f)** changements v3.1 (T, ligne 123, et lignes 125 et 126 : vérifiées), **(g)** M10 : exacts.
- **(b)** VL-03 : exact, mais renvoie au point 7 de la section 13 pour « le contrôle du relais avant le départ », que ce point ne
  contient pas (seulement la lecture de code du n° 294 et des valeurs « à écrire ») : couples 4 et 18.
- **(e)** I4 et VL-06 : exact (registre privé, ligne 67 : « code v3 (`ideation-organism` `d15f489`) ») ; l'écart reste à consigner par le
  directeur avant le scellement (au registre privé, je ne trouve que le constat, R-1286).
- Complétude : seules manquent des observations de VL sans écart à T : VL-07 (sans objet à un fil), VL-09 (rien à corriger) et
  **VL-08, encore vrai dans un sous-cas** (M9) : un arrêt à la garde d'avant appel, avant le premier appel d'une suite, laisse une suite
  sans tentative dont la cause dominante est nulle ; à savoir pour l'audit.
- **Dispense M10** : conforme à R-1294 (« A1-v3 dispensé par écrit du témoin négatif planté (M10 ; le bras « témoin », sans retour, joue
  ce rôle) », Lazar vers 00:35 heure de Paris ; ligne écrite le 2 novembre à 23:36 UTC ; heure UTC ajoutée, couple 1). Le paragraphe de
  la section 7 est juste : l'essai cité dit bien quatre cartes, log W max ≤ 10⁻⁶ (`TOLERANCE_LOG_W`), au moins trois promotions ;
  1 − 0,95¹⁶ = 0,56. Un juge qui promeut à tort dans les deux bras se voit au taux absolu et à A2 ; un juge qui ne promeut jamais se voit
  aux témoins positifs (dents sous v7, W2) : la dispense ne laisse pas de trou non dit.
- **Réponses I7** (section 13, point 7) : conformes au n° 294, section 3 (402 et 429 → code 4 au plancher ; 4 000 000 octets, 413, 411 ;
  aucune reprise, toute erreur de l'interface et le 429 de Google en code 3 au pire cas ; blocage du prompt en code 5 ; 400, 403, 411,
  413 en code 3 au plancher). Incomplètes sur un point : (a) laisse les valeurs du relais à écrire sans chiffre exigé et sous-estime le
  compte (deux appels par tentative au plus hors attente : 6 144, non 3 072) : couple 16.

## 5. Question 4 — configuration gelée et VL-01

Le chemin cité (`/home/user/controle-ia-travail/donnees/…/configuration-mini-course-kimi-argon-v3.json`) est sur la machine de
session-depot ; le texte admet « tout chemin où le fichier a l'empreinte `e5306c47…` ». Lu à cette empreinte dans la copie versée par
session-depot (`origin/canal/session-depot-reprise-n122`,
`brouillons/canal-reprise-releve-v1/envois/session-depot/conf-a1-v3/configuration-mini-course-kimi-argon-v3.json`, par `git show`,
même empreinte sur n120 et n121, compagnon conforme). Commande d'Argon : `/usr/bin/python3 -I -B …/commande_argon_v56_nuit_v2.py
appeler --url-relais http://127.0.0.1:8805 --registre {REGISTRE} --plafond-cumule-usd 80 --max-sortie-proposeur 32000
--max-sortie-court 4000 --sortie-min-jetons 1000 --delai-s 1750`. Joué avec L31 chargé tel quel : `exiger_substitutions` accepte (un
jeton, en forme séparée après `--registre`, option unique ; `--plafond-cumule-usd` unique, séparée, valeur « 80 ») ;
`reglages_de_configuration` rend (1,8 USD, `argon` → `gemini-4-argon`) ; `substituer_commandes` fait les quatre substitutions annoncées
(dont 80 → 400). **VL-01 passe.** Réserve : la lecture complète (`lire_configuration_v56`) exige aussi les six pièces de la configuration
(`pieces/…`, chemins relatifs au fichier) ; ma copie seule est refusée pour cela (code 2 au lanceur, sans dépense) : « tout chemin » est
incomplet (couple 11).

## 6. Question 5 — effet sur la v4

Essais v4 : 27 réussis, 73 sous-essais (passage commun, section 1). La v4 hérite de `a3.appeler` (tout code 3 attend ; premier code 4
= arrêt), de `a3.Compteur` créé **sans** `pire_cas_par_appel_usd` (`demonstrations/attaque_goodhart_v4.py:341-342` : tout code 4 y
est qualifié « refus_de_budget », motif « loin du plafond … pire cas par appel inconnu », même au plafond), de
`l3.reglages_de_configuration` (VL-01) et de `l3.lire_relais_perdu` (VL-02) ; elle n'hérite ni de la trace partielle complète (ses
`jouer_suite`, `jouer_unite`, `jouer_tout` propres : l'appel refusé et les suites finies de l'unité manquent à la trace), ni de
`nature_de_l_arret` et `arret_premier` (son lanceur ne les écrit pas), ni de `regle_du_refus_de_budget` au manifeste, ni du motif de
marqueur à chiffres (`l2.MARQUEUR`). Son texte (brouillon 2, `7be8589e…`) doit changer :
1. code gelé : les deux fichiers v3 au commit `9776ed0` (`cb9cffe7…`, `87d52ace…`) au lieu de `e58cfec` (`b821bdb7…`, `ff8aa180…`),
   tableau de tête et bloc de 77 lignes ;
2. « identiques à B2, section 4 (règles v3) » : périmé ; renvoyer au texte A1-v3 scellé : tout code 3 attend, premier code 4 arrête la
   course, substitutions exigées, `relais_perdu_h` fini ;
3. **prix sous son plafond de 200 USD** (attendu ≈ 110 USD, haut 130,94, maximum 190,46) : marge avant l'arrêt de ≈ 88 / 67 / 8 USD,
   soit ≈ 55 / 42 / 5 appels en échec au pire cas (≈ 3 % / 2 % / 0,2 % des appels) ou ≈ 2,6 / 2,0 / 0,2 h de panne de l'interface :
   le défaut de conception le plus net de la famille (une journée dégradée de l'interface arrête la v4 sans lecture) ; à déclarer, ou
   plafond et GO relevés (décision de Lazar) ;
4. liste d'arrêt : ajouter le premier refus en code 4 ; « un taux deux fois plus haut … arrêterait la course au plafond vers
   1 610 appels » devient : au premier refus de la garde du registre (≈ 198,4 USD réglés), motif « refus de budget loin du plafond »,
   sauf si le lanceur v4 passe le budget par appel au compteur (code v4) ;
5. trace partielle incomplète à l'arrêt (appels de la trace < appels comptés) : à déclarer ou à porter ;
6. configuration (jeton CASE_CONFIGURATION) : doit porter `{REGISTRE}` et `--plafond-cumule-usd` (la `e5306c47…` passe) ;
7. un marqueur à chiffres serait invisible au lanceur v4 (ses deux marqueurs actuels n'en ont pas) ;
8. la ligne de GO-2026-11-02-22 dit « code v4 neuf (fichiers neufs, v3 intact) » : la v3 ne l'est plus ; écart à déclarer et à
   consigner, comme I4.

## 7. Question 6 — ce qui empêcherait un résultat concluant « par défaut de conception »

**I1 — Écriture au pire cas des erreurs de l'interface (important).** Pour toute erreur de l'interface (429 de quota, 5xx, 400, 401,
403, 404), la commande gelée ne lit aucun coût et règle son pire cas (≈ 1,61 USD ; origine « pire_cas », n° 294), au compteur comme au
registre ; la v3.1 fait attendre ces appels (onze par tentative, ≈ 33,9 USD comptés par heure). Le plafond est donc encore atteint
sans dépense mesurée équivalente : (i) après ≈ 6,1 à 11,8 h de panne continue (déclaré) ; (ii) par des erreurs **intermittentes**,
chacune comptée même si l'appel suivant répond : ≈ 206 appels en échec aux taux d'A1 (≈ 20 % des ≈ 1 054 appels attendus), ≈ 166 à
l'attendu haut (≈ 8 %), ≈ 129 au maximum du devis (≈ 4 %) (non déclaré) ; (iii) par une erreur **permanente** (clé, facturation,
modèle, requête refusée), attendue comme une panne jusqu'à l'arrêt au plafond (non déclaré). Le texte nomme ce coût « dépense » et
conclut « Le plafond de 400 USD redevient une garde, non un piège » : trop fort. Couples 10 et 13 (déclaration), 18 (alerte écrite
d'avance : dès la première tentative « échouée (relais) », lecture des statuts du relais ; cause durable → Lazar décide par écrit).
*Décision proposée au directeur* : accepter avec ces couples, ou corriger. Enjeu : une interface durablement en erreur rend la course
non concluante après ≈ 6 à 12 h. (a) Couples seuls : course dès le scellement ; le risque continu reste, déclaré, l'erreur permanente
devient une décision en ≈ 30 min. (b) v3.2 : calendrier plus lent pour le seul code 3 au pire cas (par exemple 60, 300, 600, 840 s :
cinq appels par tentative, ≈ 15,8 USD comptés par heure, ≈ 21 h de marge aux taux d'A1) : un cycle de plus (code, essais, banc, texte,
contre-lecture). (c) GO et plafond relevés à 800 USD (≈ 21,6 h de marge) : décision de dépense de Lazar. Recommandation : (a), confiance
0,65 (Argon a échoué une fois sur 527 appels dans A1 ; course attendue ≈ 3,9 h) ; défaut sous 48 heures : (a).

**I2 — Réglages propres du relais non chiffrés (important).** Un `--plafond-usd` ou un `--max-appels` sous la course arrête celle-ci
« refus_de_budget » loin du plafond (arrêt propre, mais non concluant). Le point 7 (a) exige « au moins le nombre d'appels au plus de la
course (3 072 … plus les appels en attente) » : pas un nombre, et trop bas (règle v2 : deux appels par tentative au plus, 6 144). Couple
16 : au moins 400 USD et au moins 8 000 appels, ou sans borne ; mêmes valeurs après une relance par un guetteur.

**I3 — Empreinte de la commande et du relais non exigée au lancement (important).** La table des codes, l'attente sur tout code 3 et
l'arrêt sur code 4 ont été établis sur `commande_argon_v56_nuit_v2.py` `221df610…` (le relais 8805 est sa sous-commande `servir`, qui
charge `collisionneur_v7.py` `c9725f02…`) ; la configuration ne gèle que le chemin, le lanceur n'en écrit l'empreinte qu'au manifeste,
après coup (un fichier absent n'y est même pas refusé), et n° 294 demande de confirmer la copie vivante par empreinte. Couple 17 :
empreintes au journal avant `--verifier-seulement`, toute autre empreinte : pas de course.

**I4 — Contrôle du relais promis, absent (important).** Section 0.4 (b) renvoie au point 7 pour le contrôle du relais avant le départ ;
le point 7 ne l'a pas. Un refus durable du relais avant l'interface (VL-03 : modèle non permis, réglage) est attendu tentative après
tentative jusqu'à la garde de 72 h. Couples 4 et 18 (même alerte qu'I1).

**Remarques, sans couple.**
- **R1** — Tout arrêt efface la lecture, même d'un monde entièrement joué (règle de T, « aucun taux lu ») ; W1 (≈ 90 % des appels)
  est joué avant W2 : un arrêt pendant W2 perdrait un W1 complet. Peu probable ici ; lire les mondes finis avant un arrêt serait un
  changement de critère (décision de Lazar), à envisager pour les courses suivantes.
- **R2** — « Arrêt sur tout code 4 » repose sur la table des codes de ce relais (quota de l'interface en code 3) : à revérifier pour
  chaque relais neuf.
- **R3** — Pas d'autre défaut trouvé. La garde de 72 h reste une garde (attendu 3,88 h) ; une issue 6 par panne du relais ou de
  l'interface est impossible en 72 h sous attente (13 suites de 16 tentatives à 30 min : ≥ 104 h) ; un échec rapide hors code 3
  (code 2) viderait la course en minutes (issue 6, code 0, seconde course), mais VL l'a exclu sur le vrai code de la commande avec
  l'environnement réel, et un fichier absent ou différent est fermé par le couple 17 ; un plantage muet compte 1,8 USD par appel et
  arrête la course au plafond en ≈ 223 appels (arrêt propre) ; A9 suspend sans rendre non concluant ; après un arrêt, `une_unite` rend
  aussitôt (aucune suite vide ajoutée à la trace).

## 8. Constats et couples

Mineurs : **M1** énoncés que le scellement rendrait faux (le commit existe : `9776ed0`, 3 novembre, 00:56 UTC, R-1299) ; **M2** le
point 13.1 prête au n° 294 une revérification de l'arrêt au plafond sur le vrai registre (n° 294 n'annonce que VL-01 et la commande
exacte) ; **M3** pièces de la configuration ; **M4** « ≈ 17,7 USD » contre ≈ 17,76 (« ≈ 17,8 ») ailleurs ; **M5** renvoi implicite
ambigu ; **M6** une autre source dans la bande de 1,8 USD serait aussi dite « plafond » ; **M7** sources du « refus_de_budget » exclues
ici, non dites ; **M8** heure de R-1294 en heure de Paris seulement ; **M9** VL-08 (section 4), sans couple.

| couple | ligne de B4 | constat |
|---|---|---|
| 1 | 92 | M8 |
| 2 | 115 | M1 (en-tête) |
| 3 | 211 | M4 |
| 4 | 302 | I4 (0.4 (b)) |
| 5 | 310 | M1 (0.4 (e)) |
| 6 | 421 | M4 |
| 7 | 434 | M6 |
| 8 | 437 | M7, question 1 |
| 9 | 529 | M5 |
| 10 | 546 | I1 (prix déclaré, section 4) |
| 11 | 671 | M3 |
| 12 | 1143 | M1 (section 11) |
| 13 | 1281 | I1 (section 12) |
| 14 | 1294 | M1 (section 13, point 1) |
| 15 | 1301 | M2 |
| 16 | 1323 | I2 |
| 17 | 1331 | I3 |
| 18 | 1335 | I4 et I1 (alerte écrite d'avance) |

Chaque « ancien » est présent une seule fois dans B4 et au moment de son application ; ordre du document ; aucun chevauchement ;
les cinq marqueurs restent. B4 corrigé (hors du dépôt) : `5155c3e2e22ba62447a92f52f07ddab71459fb8f293782ad672352095912a33d` ; bloc
`plan-gele` lu identique ; scellement simulé accepté.

## 9. Avant le scellement, dans l'ordre

1. Appliquer les 18 couples mot pour mot ; remplir les cinq marqueurs par `9776ed0efee97146182ff2c4b409e5ec224a0bbf`.
2. Consigner l'écart I4 et VL-06 ; trancher le nœud d'I1 (défaut : couples seuls).
3. Chez session-depot : VL-01 et commande exacte (annoncés, n° 294), arrêt au plafond sur le vrai registre (couple 15), valeurs du
   relais (couple 16), empreintes (couple 17), alerte (couple 18).
4. Renommer en `prereg/preenregistrement-attaque-goodhart-v3-vN.md`, sceller, refaire la simulation de `lire_preenregistrement`, commit
   et poussée avant la course.
5. Prévenir le rédacteur de la v4 (section 6).

## 10. Fichiers du contre-lecteur (bloc-notes `/tmp/cl-a1v3-1-b4/`)

`sha256sum` à l'assemblage (01:28 UTC) :
- `scripts/appliquer.py` `d9eea66536503641aca78ab958c238259d14d2e78a60186f5c2354a78e8be1f2` → `b3c.md` `5507536934dfb733d918053e6598134a3bc3557c3dcdf7188a087a63afffb79f`
- `scripts/chiffres.py` `44699b5dfa821ed7425f80c5f69b52abe7ddf003350c8762433c594f7ca66a92` ; `scripts/table_renvois.py` `fa6aba31c451b0b80e310b66837cd16e1208c3f362020d0725e949d2e4f7521c` ; `scripts/renvois_b4.py` `f86eed7d9cabd6eb1aa8bfe085147cf201f50f088c8a502eeb98a1ff37e7b1d6`
- `scripts/empreintes.py` `2e4d4f83920fbeffe724b8997d94617088bed0118ffa8ab809723a2734725a52` ; `scripts/fonctions.py` `37e95b3a700e4c08fb4f9a50e91238ccd6cf03505edba61c144e3f4a7308341a`
- `scripts/noms.py` `c2a78a43bc23d9007cff05399085fdecb6a7428c2d20e191001fee457859941a` ; `scripts/table_mutations.py` `edc9075f4cc2ddc6a341b66380e02c85233199c939fb382152c23266bd61fd1f`
- `scripts/scellement_simule.py` `06a58f7282f4aca6669350178d74cde918f4f91ae920de461094cba9b6f28251` ; `scripts/vl01_conf.py` `b8705ac4c0671c51a50b905f217ef134a95ebc97875f04235e3b7c86a2825876` ; `configuration-mini-course-kimi-argon-v3.json` `e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30`
- `scripts/couples_b4.py` `f8518e94400245d399b220706bc90df86095107ab0102adbc523717ea9211233` → `couples-b4.json` `9662e57334b182ac153f48d60f4df7dc93d7d8aaf815506b9a5ee373b7df140a` (copié à l'octet en `prereg/couples-contre-lecture-attaque-goodhart-v3-brouillon4.json`), `b4-couples-appliques.md` `5155c3e2e22ba62447a92f52f07ddab71459fb8f293782ad672352095912a33d` ; `scripts/verif_corrige.py` `703b769cdbcbe370784d0409c1c327a6eadc2e0f834520388ae43533c554e572`
- sorties : `essais-v3-v4.txt` `1039a0b5a5363c05f4793ae22d2d7aec0965e3e589432f3c4af1127103ac8075`, `banc-v3-1.txt` `8247edb815c75e836006dba3a3141b84114babe6158f164c7badd8e46c1f2d47`

Ce fichier ne peut pas porter sa propre empreinte ; elle est donnée avec sa remise.
