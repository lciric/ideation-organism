# scellable après remplacements

Contre-lecture courte (R2) du brouillon 2 du préenregistrement « attaque de Goodhart du juge statistique » (v2), de son
code et de ses essais. Contre-lecteur neuf, 2 novembre 2026, vers 09:30 UTC ; n'a écrit ni le brouillon 1, ni le
brouillon 2, ni leur code, ni la première contre-lecture. Lecture seule : aucun commit, aucun `.sha256` dans le dépôt,
aucun `git fetch`, aucun appel de réseau ni de modèle, aucune clé ; un seul fichier écrit (celui-ci) ; calculs sous
`nice -n 10`. Tête `c47b608` (arbre propre hors un fichier non suivi étranger, `pole/lecture_tour_ferme_v61.py`).

**Verdict.** Le brouillon 2 applique la première contre-lecture : les sept constats bloquants sont corrigés dans le code
et dans le texte, les gardes neuves sont essayées sur un cas sain et sur un artefact, les couples R1 à R23 sont portés.
Essais rejoués : 45 réussis, 0 échec ; banc : 26 mutations tuées sur 26. Deux choses empêchent de sceller tel quel :
(1) le texte cite la configuration v2 (`4ae5a1e0…`) et une substitution du plafond en mémoire que la configuration v3
(`e5306c47…`) rend sans objet — remplacements V1 à V8 ci-dessous ; (2) **hors du texte, bloquant pour le lancement** : le
registre privé tient aujourd'hui `GO-2026-11-02-07` pour **révoqué**, parce que la ligne de révocation
`GO-2026-11-02-08` le nomme dans son périmètre ; le lanceur refuserait (code 2) dès `--verifier-seulement`. Aucun
changement de code n'est nécessaire ; le bloc `empreintes-du-code` reste valable (71 empreintes conformes à l'arbre).

## 0. Ce qui a été lu et rejoué

- Empreintes vérifiées, conformes au rapport de rédaction : brouillon 2 `15f27d5f…`, contre-lecture v1 `e0866a64…` ;
  `prereg/preenregistrement-validation-nul-v8-v2.md` `7f37631d…` (cité section 1).
- `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_attaque_goodhart_v2.py` : **45 réussis, 54
  sous-essais réussis, 0 échec** (40,5 s).
- `nice -n 10 python3 -I -B essais/mutations_attaque_goodhart_v2.py` : **26 mutations, 26 tuées pour la raison attendue**,
  0 pour une autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin 19 essais sans échec après restauration.
- Configurations lues par `git -C /home/claude/controle-ia-travail show` (aucun `fetch`) : v2 `4ae5a1e0947d44c1a08548d1b0197bfd96a2264f455189713b06183b2bc83108`,
  v3 `e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30`, extrait des commandes `98203f1aa929f8aebc16d7206c646319b7aec193c8ab808d64bad269f319c091` :
  toutes trois conformes aux empreintes annoncées.
- Différence v2 → v3 par aplatissement des deux JSON (182 feuilles chacun) : **exactement trois feuilles** —
  `fournisseurs.kimi.commande[9]` « 10 » → « 80 », `fournisseurs.argon.commande[10]` « 10 » → « 80 », `_lisez_moi`
  (phrase d'en-tête). Le jeton `{REGISTRE}` est gardé aux deux commandes.
- Lanceur sur la v3 (copie du brouillon 2 où `4ae5a1e0…` est remplacé par `e5306c47…`, scellée dans un dossier
  temporaire, `DOSSIER_PREREG` détourné par `mock`, rien d'écrit dans le dépôt) : `lire_preenregistrement` passe (71
  empreintes conformes, plan 12 cartes, W1 et W2, 80 USD, 20 h, `configuration_sha256 = e5306c47…`, GO-2026-11-02-07) ;
  `substituer_commandes(v3, <sortie>/registre-depense-cumulee-v1.jsonl, 80)` fait quatre substitutions : `{REGISTRE}` →
  `/home/claude/ideation-organism/resultats/attaque-goodhart-v2/registre-depense-cumulee-v1.jsonl` (argon [8], kimi [7]) et
  « 80 » → « 80 » (argon [10], kimi [9]) : **sans effet, écrite au manifeste** ; `reglages_de_configuration(v3)` rend
  budget 1,8 USD, modèles `kimi-k3.1-pro` et `gemini-4-argon`.
- `configuration_v56.verifier_go_v56("GO-2026-11-02-07", <registre privé>, 80.0)` : **`GoRefuse : A15 : GO-2026-11-02-07
  révoqué par GO-2026-11-02-08`** (constat 1).

## 1. Constats

**1. Bloquant pour le lancement (registre privé, pas le texte) — le GO cité est tenu pour révoqué.** La règle commune à
`pole/configuration_v55.py:89-92` (`verifier_go_v55`, appelée par `demonstrations/attaque_goodhart_v2.py:194`) et à la
garde du dépôt (`controle-ia-travail/.claude/hooks/garde_calcul.py:96-100`) : un GO est révoqué si une ligne de type
« révocation » le nomme dans son périmètre ou sa référence. La ligne `GO-2026-11-02-08` (`registres/go.md:54`) a pour
périmètre « GO-2026-11-02-03 et GO-2026-11-02-04 remplacés par **GO-2026-11-02-07** » : l'identifiant du GO vivant y
figure, donc `verifier_go_v56` lève `GoRefuse` et le lanceur rend 2 dès `--verifier-seulement` (vérifié, section 0).
Les essais `LanceurGo.*` et `LanceurCheminReel.*` ne l'ont pas vu : leur registre factice n'a aucune ligne de révocation
(`essais/test_attaque_goodhart_v2.py:454-455`, `:521-522`). À faire avant tout lancement, décision de Lazar (registre) :
reformuler le périmètre de la ligne 08 sans l'identifiant, par exemple « GO-2026-11-02-03 et GO-2026-11-02-04 remplacés
par le GO d'A1 du même jour (ligne précédente, 80 USD) » — ni le périmètre ni la référence ne doivent contenir la chaîne
`GO-2026-11-02-07`. L'autre voie (un contrôle propre au lanceur) changerait un fichier gelé et les 71 empreintes, pour
contourner une convention du registre ; non recommandée. Le texte le dit en section 13 (couple V9).

**2. Important — le texte cite la v2 et une substitution que la v3 rend sans objet.** Section 4, lignes 146 à 169
(« Configuration gelée », « Deux substitutions déclarées »), ligne 179 (commande), ligne 202 (bloc `plan-gele`),
sections 10, 13 et 14 : tout renvoie à `configuration-mini-course-kimi-argon-v2.json`, `4ae5a1e0…`, référence `n81`, et
à la réécriture de `--plafond-cumule-usd` « 10 » → « 80 » comme condition de la course. Avec la v3, cette substitution
devient « 80 » → « 80 » (le lanceur la fait et l'écrit au manifeste quand même, `demonstrations/attaque_goodhart_v2.py:247-249`) ;
seule celle de `{REGISTRE}` agit encore. La constante `CONF_DU_1ER_NOVEMBRE` nommée ligne 146 n'existe pas dans le code
v2 (`grep` : 0 occurrence). Couples V1 à V8.

**3. Important — la lecture de W2 ne dit pas d'avance ce que « brèche » ne veut pas dire.** Section 6, lignes 256 à 258,
donne la lecture positive (« un proposeur modèle de langage trouve la classe non couverte… ») ; section 1 explique le
régime. Manque l'énoncé négatif : l'issue « infirmée (brèche sous v8) » sur W2 n'infirme ni le nul v8 ni Ville (la classe
est déclarée non couverte par `pole/nul_v8.py` lui-même, la loi par morceaux de S1 et S2 y est attendue promue), ne dit
rien de W1 ni de la production. Et le « trop beau » symétrique sur W2 n'est pas nommé : (a) le témoin qui trouve le trou
dès la tentative 1 (à blanc : 24/24 sans retour, 23/24 avec) rend Δ(v8) et Δ_loi(W2, v8) muets sur le goût du juge —
A4 ne couvre que v7 (`pole/attaque_goodhart_v2.py:886-887`) ; (b) retour ≥ 4/24 avec témoin ≤ 1/24 (P5 éclatante)
mérite le même audit des consignes du témoin que A2. Sans changement de code (A4 ne suspend pas l'issue ; le taux
`v8|temoin|n=1|ensemble` est déjà dans la sortie, `:840`) : couples V11 et V12.

**4. Important — la mesure par loi d'H3 n'est pas définie quand la promotion arrive dès la tentative 1.**
`ecart_par_loi` (`pole/attaque_goodhart_v2.py:796-818`) ne retient que les unités où les deux suites ont une loi k ≥ 2 ;
sur W2, le cas attendu est justement la promotion précoce : à blanc, aucune unité (L6). Le texte le dit en L6 et en
réserve (section 14), pas là où H3 est définie (sections 2 et 5). Il faut l'écrire avec le nombre d'unités retenues et
une règle de lecture gelée pour peu d'unités (le code écrit « gain du retour » dès que la borne basse est > 0, même sur
deux unités) ; H3 est rapportée sans effet sur les issues, donc une règle de texte suffit. Couple V10.

**5. Mineur — empreinte du README.** Section 12, ligne 440 : `README.md` à `482a6354…` ; sur la tête `c47b608` le README est
`af0b9709…` (`482a6354…` = commit `1dac1fe`, 2 novembre 03:21 +01:00). Le chiffre reste rattaché à une empreinte (R6) ;
ajouter le commit pour qu'il soit retrouvable. Couple V13.

**6. Mineur — en-tête de la v3.** Son `_lisez_moi` parle d'une option `--sortie` du lanceur ; le dossier de sortie est
l'argument positionnel `dossier`. Prose seulement, empreinte gelée : rien à changer, à savoir.

**7. Mineur.** Section 14, ligne 496 : « la configuration du second tour est privée (non vue) » — elle a été vue (v2 et
v3, `git show`) ; la réserve qui tient est « les pièces (`pieces/*.md`), les scripts de commande et les relais restent
chez session-depot, non vérifiables ici ». Couple V14.

### Couverture de la première contre-lecture (question 1)

| constat | corrigé (code) | texte | R5 (sain / artefact) |
|---|---|---|---|
| 1 grammaire, plantage | `pole/attaque_goodhart_v2.py:190-276` (`grammaire_servie`), `:386` (avant `sp.valider_loi`), `:441-451` (`juger` : toute exception → « evaluation_impossible ») | section 4, lignes 121-126 | `Grammaire.*` : 5 lois bornées jugées sans exception ; 7 sondes + poids, clé, 11 niveaux, 6 000 octets, condition → invalides |
| 2 richesse non finie, suites perdues | `:449-452` (NaN, −∞ → impossible ; +∞ → promue), `:90-96` (`ArretAttaque.partiel`), `:560-564`, `:986-997` ; lanceur `:410-418` (code 3, trace partielle scellée) | section 4 ligne 123, section 8 ligne 314 | `Grammaire.test_richesse_non_finie…`, `ListeDArret.*`, `LanceurABlanc` (plafond atteint → 3) |
| 3 description v8 aux suites v7 | `:282-351` (`bibliotheque_du_juge`, `description_du_juge`, refus d'un membre non décrit, `consigne(…, juge)`), `:56` (quatre suites) | section 4 lignes 109-116 | `Consigne.*` (v7 sans mélange, v8 avec ; une ligne diffère ; membre sans description → refus ; espion : témoin sans verdict) |
| 4 bloc gelé, chemin, GO | lanceur `:67-85` (71 fichiers), `:151-182` (chemin fixé, scellé, marqueurs, bloc exact, empreintes), `:185-196` (GO du texte) | section 11, bloc `empreintes-du-code` ; section 4 « GO » | `LanceurPreenregistrement.*` (12 artefacts isolés + chemin non fixé), `LanceurGo.*`, `Fermeture.*` (fermeture mesurée = liste) |
| 5 chemin réel non exercé, défaut 0,10 USD | lanceur `:212-230` (budget = `plafonds_session.proposeur`, aucun défaut ; modèles exacts ; types), `:265-297` ; cœur `:487-488`, `:508` (`budget_depasse` à part), `:731-746` (modèle demandé passé) | section 4 lignes 154-169, A7 | `LanceurCheminReel.*` (faux relais Kimi local, commande factice Argon, Kimi aussi par commande externe ; budget absent, sous le pire cas, Argon absent, clé → refus ; 7 refus isolés à `--verifier-seulement`, rien écrit) |
| 6 ordre des issues | `:853-862` (brèche d'abord) | section 6 ligne 251 | `Suites.test_breche_avant_dents` |
| 7 écart au brief | `:161-187` (W2), `:642-651` (qualification) | sections 1, 2, 10 ; R-1123 cité ; `decision_ecart` dans `plan-gele` | `Mondes.*`, `Suites.test_w2_…` |

R1 à R20 : chaque cible retrouvée au texte (R1, R2 : lignes 35-37 ; R3 : 40-53 ; R4 : 89 ; R5, R6 : 109-110 ; R7 : 112 ;
R8 : 123 ; R9 : 128 ; R10 : 132-133 ; R11 : 251 ; R12 : 255 ; R13 : 261-262 ; R14 : 273 ; R15 : 314 ; R16 : 333 ; R17 :
346 ; R18 : 356 ; R19 : 440 ; R20 : 448) ; R21 à R23 portés (ε = 0,25 ligne 70 ; bloc `plan-gele` ; tableau ligne 225-230).
Règles de lecture recalculées par le code : à 24 unités, « résiste » ⇔ ≤ 1/24, « brèche » ⇔ ≥ 4/24 ; à 6, 0/6 et ≥ 2/6 —
conformes au texte. Les constats 8 à 19 : traités comme le rapport de rédaction le dit (vérifié par sondage : 9 par
`nombre_lu` `:396-405` et `hors_classe` `:427-429` ; 12 par A1 = A2 = A5, lignes 273-278 ; 14 par `:534-535` (`del brut`) ;
15 par le manifeste du lanceur `:395-405` ; 16 par `test_refus_du_lanceur_isoles` ; 19 c par `:138-143`).

### Points ouverts du rédacteur (question 2)

- **GO nommé par le texte, ligne de GO sans empreinte du texte** : acceptable tel quel — le texte, dont l'empreinte est
  la graine, lie son GO ; la ligne 07 nomme le motif `preenregistrement-attaque-goodhart-v2-v<N>.md`, 80 USD, échéance
  2026-11-16, Lazar : conforme au format que `verifier_go_v55` lit. **Mais** la ligne 08 le révoque par citation
  (constat 1) : à corriger au registre avant le lancement.
- **Budget par appel = 1,8 USD sans défaut** : acceptable. Ordre de grandeur Kimi (prix de l'essai, 0,6 et 2,5 USD par
  million) : consigne la plus longue ≈ 90 000 octets ≈ 25 000 à 30 000 jetons d'entrée, 65 536 de sortie au plus → pire cas
  ≈ 0,18 USD, loin sous 1,8 ; pour une commande externe, le pire cas est tenu par la commande (`PLAFOND_SESSION_USD`) et
  tout refus est compté à part (A7). Rien à changer.
- **Durée maximale 20 h (attendue haute 13,4 h)** : acceptable. À 3 072 appels (maximum) en parallèle, 20 h moins 1,7 h de
  rejeux laissent ≈ 43 s par appel ; à 2 112 appels, ≈ 62 s. L'hypothèse « 10 à 40 s par appel » est déclarée ; un arrêt
  par durée rend code 3, trace partielle scellée, aucun taux lu — dit en section 8. Un plafond plus haut ne coûterait rien
  (c'est une borne, pas une dépense) ; choix du directeur, non bloquant.
- **Mesure par loi d'H3 indéfinie à la promotion en tentative 1** : à changer avant scellement, par le texte (constat 4,
  couple V10).
- **Course à blanc à 20 rejeux au lieu de 200** : acceptable. Les rejeux sont du code déterministe déjà essayé (1 et
  2 processus, mêmes comptes, `Rejeux.*`) ; 200 ne change que la durée, mesurée par évaluation (56 ms) et déclarée.
- **Chemin réel contre un faux relais et des commandes factices seulement** : acceptable avec la réserve écrite, parce que
  `--verifier-seulement` est exigé avant la course (adaptateurs construits, portes accusées, aucun appel) et que
  l'adaptateur v56 est celui qui a servi le 1er novembre avec ces mêmes commandes.

### Lecture de W2 (question 3)

Vue ci-dessus, constat 3 : la lecture positive est écrite, l'énoncé négatif et le « trop beau » symétrique manquent ;
couples V11 et V12. Noter aussi que sur W2 « résiste » est bien qualifié de réserve (section 6, lignes 264-266) et que A1
(calculé sur « aucune promotion sous v8 ») s'y déclenche : la symétrie est tenue dans ce sens-là.

### Devis (question 4)

Cohérent et honnête. `devis(12, [W1, W2])` : appels 1 152 à 2 112 (3 072 au plus), 27,3 à 50,1 USD (72,8 au plus) au taux
0,0237 ; plafond 80 ≥ 72,8 ; le texte dit le facteur 2 et son effet (arrêt au-delà de ≈ 1 690 appels à un taux doublé,
code 3, aucun taux lu) ; l'écart avec le registre (≈ 41 à 55) est déclaré et expliqué (appels attendus sur W2, non
mesurés sur un modèle) ; 55 < 80. Le taux du 1er novembre vient d'appels à sortie longue (fiches, juges) alors que les
nôtres ont une sortie courte et une entrée parfois longue : le facteur 2 est une marge raisonnable, pas une certitude. Le
plafond cumulé des commandes (80, v3) porte sur le registre partagé des deux fournisseurs, comme le compteur du lanceur ;
la porte « environnement » donne 40 USD à chaque commande (`PLAFOND_ETAPE_USD`) : trois gardes concordantes.

### Configuration v3 (question 6)

(a) Trois feuilles, vérifiées (section 0). (b) Le lanceur accepte un texte à l'empreinte v3 ; la substitution du plafond
devient « 80 » → « 80 », écrite au manifeste. (c) **Aucun code appelé par le lanceur ne se sert de `budget.plafond_usd`
(10) ni de `budget.arret_etape_usd` (9)** : `lire_configuration_v56` (`pole/configuration_v56.py:90-113`) ne lit que
`budget.etapes` ; la lecture v53 ne fait que valider ces deux clés (réel > 0 ; `pole/configuration_v53.py:81-82`) ;
`montant_requis` (`pole/configuration_v54.py:142-144`, seul lecteur de S17) n'est pas appelé par le lanceur, qui passe
`plan["plafond_usd"]` = 80 à `verifier_go_v56` (`demonstrations/attaque_goodhart_v2.py:194`) ; `adaptateurs_reels_v56`
(`demonstrations/ideation_v8.py:59-81`) ne lit que `fournisseurs.*` ; les portes reçoivent 40 USD chacune (`:284-285`) ;
le `Compteur` reçoit 80 (`:406`). **Pas de v4 nécessaire.** Réserve : les scripts `commande_kimi_v2.py` et
`commande_argon_v56_nuit_v2.py` (chez session-depot) ne lisent pas le JSON de configuration d'après leurs arguments, mais
ils n'ont pas été lus ici. (d) Le texte scellé doit citer : l'empreinte `e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30`,
le chemin `brouillons/canal-reprise-releve-v1/envois/session-depot/conf-a1-v3/configuration-mini-course-kimi-argon-v3.json`
(référence `origin/canal/session-depot-reprise-n86`), le dossier de sortie `../resultats/attaque-goodhart-v2` depuis
`orchestrator/` (déjà dans la commande, ligne 177) et la commande exacte avec `…-v3.json` : couples V1 à V8.

## 2. Remplacements (couples exacts, brouillon 2 ; chaque cible apparaît une fois, vérifié par programme)

V1a. remplacer : ``la configuration du tour réel du 1er novembre (`CONF_DU_1ER_NOVEMBRE`,``
par : `la configuration v3 de session-depot (`

V1b. remplacer : ``  `configuration-mini-course-kimi-argon-v2.json`, **sha256 `4ae5a1e0947d44c1a08548d1b0197bfd96a2264f455189713b06183b2bc83108`**),``
par : ``  `configuration-mini-course-kimi-argon-v3.json`, **sha256 `e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30`**),``

V1c. remplacer : ``  copiée à l'octet par session-depot dans le dépôt privé de travail (`controle-ia-travail`, référence``
par : ``  déposée par session-depot dans le dépôt privé de travail (`controle-ia-travail`, référence``

V1d. remplacer : ``  `origin/canal/session-depot-reprise-n81`, chemin``
par : ``  `origin/canal/session-depot-reprise-n86`, chemin``

V1e. remplacer : ``  `brouillons/canal-reprise-releve-v1/envois/session-depot/conf-1er-novembre-v1/configuration-mini-course-kimi-argon-v2.json`,``
par : ``  `brouillons/canal-reprise-releve-v1/envois/session-depot/conf-a1-v3/configuration-mini-course-kimi-argon-v3.json` ; copie de la configuration du tour réel du 1er novembre, `conf-1er-novembre-v1/configuration-mini-course-kimi-argon-v2.json` (référence `origin/canal/session-depot-reprise-n81`, sha256 `4ae5a1e0947d44c1a08548d1b0197bfd96a2264f455189713b06183b2bc83108`), à trois feuilles près, vérifiées par aplatissement des deux JSON (182 feuilles chacun, contre-lecture courte du 2 novembre) : `fournisseurs.kimi.commande[9]` et `fournisseurs.argon.commande[10]`, valeur de `--plafond-cumule-usd`, « 10 » → « 80 », et la phrase d'en-tête `_lisez_moi` ; le jeton `{REGISTRE}` est gardé,``

V1f. remplacer : ``  avec l'extrait des commandes `commandes-relais-nuit-v2-extrait.json`, sha256``
par : ``  avec l'extrait des commandes du 1er novembre `commandes-relais-nuit-v2-extrait.json`, sha256``

V1g. remplacer : ``  `98203f1aa929f8aebc16d7206c646319b7aec193c8ab808d64bad269f319c091`), lue par `git show` le 2 novembre vers 07:50 UTC. Le``
par : ``  `98203f1aa929f8aebc16d7206c646319b7aec193c8ab808d64bad269f319c091`), lues par `git show` le 2 novembre (v2 vers 07:50 UTC par le rédacteur, v3 par la contre-lecture courte). Le``

V2a. remplacer : ``  remplaçait par le registre de son run) ; la valeur de `--plafond-cumule-usd` (10 USD au 1er novembre) devient le plafond``
par : ``  remplaçait par le registre de son run) ; la valeur de `--plafond-cumule-usd` (80 dans la v3) est réécrite au plafond``

V2b. remplacer : `  de la course, 80 USD — sans quoi les commandes refuseraient tout appel au-delà de 10 USD cumulés, ce qui changerait des`
par : `  de la course, 80 USD : substitution sans effet (« 80 » → « 80 »), écrite au manifeste comme telle ; sous la v2 (10 USD), les commandes auraient refusé tout appel au-delà de 10 USD cumulés et changé des`

V2c. remplacer : `  tentatives en échecs. Si le budget par appel`
par : ``  tentatives en échecs, d'où la v3. Le registre de la course est partagé par les deux commandes : leur plafond cumulé de 80 USD porte sur la somme des deux fournisseurs, comme le compteur du lanceur ; chaque commande reçoit en outre sa part, 40 USD, par la porte « environnement » (`PLAFOND_ETAPE_USD`). Aucun code appelé par le lanceur ne lit `budget.plafond_usd` (10) ni `budget.arret_etape_usd` (9) de la configuration : la lecture v53 ne fait que les valider, et le montant passé au contrôle du GO est le plafond du bloc `plan-gele`. Si le budget par appel``

V3. remplacer : `      --configuration CHEMIN/configuration-mini-course-kimi-argon-v2.json \`
par : `      --configuration CHEMIN/configuration-mini-course-kimi-argon-v3.json \`

V4. remplacer : `configuration_sha256: 4ae5a1e0947d44c1a08548d1b0197bfd96a2264f455189713b06183b2bc83108`
par : `configuration_sha256: e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30`

V5. remplacer : ``**avant** la course ; à session-depot : la configuration du 1er novembre à l'empreinte du bloc `plan-gele`, ses scripts de``
par : ``**avant** la course ; à session-depot : la configuration v3 à l'empreinte du bloc `plan-gele`, les scripts de``

V6a. remplacer : `(section 5, complété par la ligne des 6 unités). La configuration de R22 (chemin, empreinte, modèles, budget par appel) est`
par : `(section 5, complété par la ligne des 6 unités). La configuration de R22 (chemin, empreinte, modèles, budget par appel) est la v3 de session-depot, copie de`

V6b. remplacer : ``  celle du 1er novembre, gelée par son empreinte dans le bloc `plan-gele` ; ses modèles sont ceux de ses proposeurs ; le``
par : ``  celle du 1er novembre au plafond cumulé près (80 USD), gelée par son empreinte dans le bloc `plan-gele` ; ses modèles sont ceux de ses proposeurs ; le``

V7. remplacer : `configuration du second tour du 1er novembre), une forme`
par : `configuration v3, copie de celle du second tour du 1er novembre au plafond cumulé près), une forme`

V8. remplacer : `  ainsi le GO ; le GO ayant été inscrit avant le scellement, il ne peut pas citer l'empreinte du texte.`
par : `  ainsi le GO ; le GO ayant été inscrit avant le scellement, il ne peut pas citer l'empreinte du texte. Une ligne de révocation qui nomme un GO le révoque (règle commune à `configuration_v55.verifier_go_v55` et à la garde du dépôt privé) : aucune ligne du registre autre que la sienne ne doit porter la chaîne « GO-2026-11-02-07 ».`

V9. remplacer : ``variable de clé ; `--verifier-seulement` (aucun appel) puis la course ; sortie scellée avant lecture ; verdict par un``
par : ``variable de clé ; au registre privé, la ligne de révocation GO-2026-11-02-08 reformulée sans l'identifiant GO-2026-11-02-07 (le 2 novembre, la contre-lecture courte a vu `configuration_v56.verifier_go_v56` tenir GO-2026-11-02-07 pour révoqué parce que cette ligne le nomme dans son périmètre : le lanceur rendrait 2) ; `--verifier-seulement` (aucun appel) puis la course ; sortie scellée avant lecture ; verdict par un``

V10. remplacer : `« non tranché » sinon. Aucun modèle de`
par : ``« non tranché » sinon. Une unité n'entre dans Δ_loi que si ses deux suites (retour et témoin, même juge) ont au moins une loi valide de tentative k ≥ 2 : une suite promue dès la tentative 1 n'en a aucune, et Δ_loi est « non tranché (aucune unité) » quand aucune unité ne reste — cas attendu sur W2, vu à blanc (L6). Le nombre d'unités retenues est écrit (`unites`) ; sur moins de 6 unités, l'intervalle est rapporté brut et la lecture écrite par le code (« gain », « perte ») n'est pas reprise : « non lisible (unités insuffisantes) ». Aucun modèle de``

V11. remplacer : `lecture est alors « un proposeur modèle de langage trouve la classe non couverte en au plus 16 tentatives, à ce taux ».`
par : ``lecture est alors « un proposeur modèle de langage trouve la classe non couverte en au plus 16 tentatives, à ce taux ». Ce qu'elle ne dit pas : que le nul v8 a un défaut, ou que la garantie de Ville est battue — la classe est déclarée non couverte par `pole/nul_v8.py` lui-même (lignes 83 à 90) et une loi par morceaux de S1 et S2 y est attendue promue ; rien sur W1 ; rien sur la production, dont l'archive et les classes couvertes sont autres. Ce que la course ajoute : le taux auquel un modèle de langage trouve ce trou en au plus 16 tentatives, et, par Δ (H3, P5, P6), la part qu'y prennent la description du juge et le retour.``

V12. remplacer : `  tentative ; alors Δ(v7) ne mesure plus le retour ; noté, l'issue n'est pas changée.`
par : ``  tentative ; alors Δ(v7) ne mesure plus le retour ; noté, l'issue n'est pas changée.
- **A4 bis — trou donné par la description (W2)** : taux(v8, témoin, 1) ≥ 0,5 sur W2 (lu dans `taux["v8|temoin|n=1|ensemble"]` de la sortie, compté à la main : le code ne le calcule pas comme audit) : le témoin trouve la classe non couverte dès la première tentative, le retour n'a rien à apprendre, Δ(v8) et Δ_loi(W2, v8) ne mesurent plus le goût du juge appris ; noté, l'issue n'est pas changée. Trop beau symétrique sur W2 : sous v8, retour ≥ 4/24 et témoin ≤ 1/24 (P5 éclatante) déclenche avant lecture, sur les consignes du témoin, le même audit que A2 (présence de la description du juge, absence de tout verdict, empreintes `consigne_sha256`) ; c'est un cas sous A2 (calculé), nommé ici.``

V13. remplacer : `README.md (sha256 482a63540d6176a2f3027c30f3a2bcfceb8a6b91fbd1b274e1789c6bded90458, section 4)`
par : `README.md au commit 1dac1fe (sha256 482a63540d6176a2f3027c30f3a2bcfceb8a6b91fbd1b274e1789c6bded90458, section 4 ; le README de la tête c47b608, af0b9709…, a changé depuis)`

V14. remplacer : `(jamais contre les relais de session-depot) ; la configuration du second tour est privée (non vue) ; le taux par appel et la`
par : `(jamais contre les relais de session-depot) ; les pièces de la configuration, ses scripts de commande et ses relais restent chez session-depot (non vus) ; le taux par appel et la`

## 3. Changements de code

Aucun. Le bloc `empreintes-du-code` du brouillon 2 est conforme à l'arbre `c47b608` (71 empreintes vérifiées par le lanceur
sur la copie temporaire) et reste valable tant qu'aucun fichier gelé ne change. Si le directeur retient l'autre voie du
constat 1 (contrôle du GO propre au lanceur), le bloc est à recalculer et cette contre-lecture à refaire sur ce point.

## 4. Avant le scellement, dans l'ordre

1. Appliquer V1 à V14, renommer `prereg/preenregistrement-attaque-goodhart-v2-v1.md`, sceller (directeur), commit, poussée.
2. Au registre privé : reformuler la ligne GO-2026-11-02-08 sans « GO-2026-11-02-07 » (Lazar) ; rejouer
   `configuration_v56.verifier_go_v56("GO-2026-11-02-07", registres/go.md, 80.0)` : doit rendre la ligne, pas `GoRefuse`.
3. Chez session-depot : v3 au chemin de la commande, relais 8804 et 8805, scripts de commande, pièces ; `--verifier-seulement`
   (code 0, rien écrit) ; puis la course dans `../resultats/attaque-goodhart-v2`.
