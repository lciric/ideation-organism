# non scellable

Contre-lecture (R2) du brouillon 1 du préenregistrement « attaque de Goodhart du juge statistique », de son code et de ses
essais. Contre-lecteur neuf, 2 novembre 2026, vers 07:05 UTC ; n'a écrit ni le texte ni le code. Lecture seule : aucun
commit, aucun `.sha256`, aucun appel de réseau ni de modèle ; un seul fichier écrit (celui-ci). Calculs sous `nice -n 10`.

**Verdict.** Non scellable en l'état : le harnais plante sur des lois que sa propre analyse accepte (un proposeur qui
attaque ferait tomber la course, code 1, aucune issue), la consigne décrit le nul v8 aux bras v7 (le témoin positif est
faussé), le bloc du code gelé n'existe pas et n'est pas vérifié, le chemin réel n'a jamais tourné, l'ordre des issues peut
masquer une brèche. À 6 unités par cellule, la lecture principale est presque toujours peu informative au regard de ce que la
théorie garantit déjà. Corrigible : changements de code C1 à C14, remplacements ci-dessous, et deux décisions du directeur
(écart au brief, grille). Un brouillon 2 ainsi corrigé serait scellable après une contre-lecture courte.

## 0. Ce qui a été lu et rejoué

- Empreintes vérifiées, conformes au rapport de rédaction : brouillon `af9b8588…`, `pole/attaque_goodhart_v1.py`
  `7bdbfe24…`, `demonstrations/attaque_goodhart_v1.py` `9641a96d…`, `essais/test_attaque_goodhart_v1.py` `3133ba51…`.
- Essais rejoués : `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_attaque_goodhart_v1.py
  essais/test_v58_nul_v8.py` → **55 réussis, 51 sous-essais réussis, 0 échoué** (44 s).
- Sortie à blanc L3 : `a-blanc-sortie.txt` existe et fait **0 octet** (vérifié sur disque, R11) ; la sortie réelle est
  `…/scratchpad/a-blanc-plan-gele/attaque-goodhart-v1.json`, sceau conforme (`412f9183864ac305964e2278612866eb422e194e4d9bbf215c9cf9f64bc18f40`) :
  269,8 s, 204 appels simulés, issue « résiste (à cette taille) », aucun audit ; P1 vraie, **P2 fausse** (Δ₁₆(v7) = 0), P3
  vraie ; rejeux v8 0/3 800, v7 1 149/2 160 ; 2 lois invalides ; ≈ 43 ms par évaluation du juge.
- Sondes à blanc (scripts dans le scratchpad, aucune écriture dans le dépôt) : 7 lois passées à `analyser_reponse` puis à
  `juger` sous v8 et v7 ; écho testé sur 5 écritures. Résultats aux constats 1 et 9.
- Préenregistrement `6fcb1035…` du second tour : absent de l'arbre public (recherche du préfixe dans tout le dépôt et
  empreinte de chaque `prereg/*.md`) ; seul `README.md` le cite (sha256 `482a6354…0458`, section 4).

## 1. Constats

**1. Bloquant — le harnais plante sur des lois qu'il accepte.** `analyser_reponse` ne vérifie que `sp.valider_loi`
(`pole/attaque_goodhart_v1.py:197`), qui accepte des types absents de la grammaire servie et des paramètres non bornés
(`pole/selection_pari.py:177-266`). Sondes : `calendrier` court et `deterministe` acceptés puis `LoiInvalide` au juge ;
`transformee` à inclinaison [1000, 0, 0] ou oscillation d'amplitude 10⁴ acceptées puis `OverflowError`
(`selection_pari.py:168`, `:171`) ; `fixe` à probabilités 10³⁰⁸ acceptée puis `ValueError` (log de 0). `juger` n'est
protégé par rien (`attaque_goodhart_v1.py:281-285`) et le lanceur ne rattrape que `ArretAttaque`
(`demonstrations/attaque_goodhart_v1.py:139`) : la course s'arrête avec une trace d'erreur, **code 1** (absent des codes
0/2/3 promis, brouillon:96-97), manifeste écrit, aucun résultat, dépense perdue. Un optimiseur à qui l'on dit « récompensé si
promue » et à qui l'on sert `inclinaison` a toutes les raisons d'essayer des inclinaisons extrêmes. La garde « hors
grammaire » déclarée (brouillon:71, :150) n'est **ni écrite ni essayée** : l'artefact de l'essai (`calendrier` de 500
lignes, `essais/test_attaque_goodhart_v1.py:71`) est refusé pour sa **taille**, pas pour sa grammaire (R5).

**2. Bloquant — une richesse non finie arrête la course et autorise un rejeu.** `juger` lève `ArretAttaque` sur une richesse
non finie (`attaque_goodhart_v1.py:222-223`) ; le texte prescrit alors « rejeu dans un dossier neuf, même fichier scellé »
(brouillon:160-161). Dans une expérience d'attaque, une loi qui rend la richesse non finie est un **résultat** (défaut du
juge trouvé par l'attaquant), pas une panne d'instrument. La règle reprise du nul v8 (`preenregistrement-validation-nul-v8-v2.md:295-299`)
reposait sur « même graine, donc même course » ; avec des modèles de langage, une seconde course est une nouvelle course
(sorties non reproductibles) : c'est un chemin bifurquant, et l'événement « trop laid » est jeté pendant qu'une course propre
serait lue (R4). De plus, à l'arrêt, les suites partielles sont perdues (`demonstrations/attaque_goodhart_v1.py:139-144` :
seuls appels et dépense sont écrits).

**3. Bloquant — la consigne décrit le nul v8 aux bras v7 ; le témoin positif est faussé.** `JUGE_PUBLIC`
(`attaque_goodhart_v1.py:141-146`) est servi à toutes les suites : « marginales, lois connues de l'archive, **leurs
mélanges** et leurs versions tempérées et inclinées », « lue aux instants 25, …, 200 ». Sous v7, la bibliothèque ne contient
ni mélange de S1 et S2 ni version tempérée, et la lecture est continue (`banc_tricheurs_v8.py:238-240`,
`banc_tricheurs_v7.py:139-150`). Le texte dit pourtant « juge décrit tel que le code public le fait (boîte blanche) »
(brouillon:65-66). Conséquences : (a) un modèle qui croit la description évite justement le mélange de S1 et S2 qui gagne
sous v7 ; le témoin positif (issue 1, contrôlée en premier) peut échouer pour cette seule raison ; (b) Δ(v7) devient « le
retour corrige une description fausse », pas « le retour aide à optimiser contre le juge ». Le témoin unique, jugé sous les
deux nuls (`attaque_goodhart_v1.py:474`), ne peut recevoir qu'une description : il faut un témoin par juge (C3).

**4. Bloquant — bloc du code gelé absent et non vérifié ; graine décisive non liée à un fichier unique.** Brouillon:186-188
le reconnaît. En outre `entropie_du_preenregistrement` (`demonstrations/attaque_goodhart_v1.py:38-45`) accepte tout fichier
au bon préfixe dont le compagnon `.sha256` est conforme, où qu'il soit : modifier le texte et réécrire le compagnon donne
une graine nouvelle (le banc v8 fixait le chemin, `banc_tricheurs_v8.py:177-179`). La liste de la section 11 omet le chemin
réel importé (`demonstrations/ideation_v8.py`, `pole/adaptateurs.py`, `pole/adaptateurs_v56.py`,
`pole/adaptateur_kimi_v53.py`, `pole/configuration_v56.py`, …) et la liste du manifeste
(`demonstrations/attaque_goodhart_v1.py:126-129`) omet en plus `controles_pari.py`, `memoire.py`, `fiche.py`,
`caviardage.py`, `__init__.py` et `ideation_v8.py`. R1 et le précédent du nul v8 exigent le bloc vérifié par le lanceur.

**5. Bloquant — chemin réel jamais exécuté ; ses gardes ne sont pas essayées (R5).** `proposeurs_reels`
(`demonstrations/attaque_goodhart_v1.py:57-71`) : lecture de configuration, construction des adaptateurs, garde « kimi et
argon exigés », transmission aux portes de plafond, budget par appel à **défaut silencieux de 0,10 USD**
(`:69`, contraire à « aucun repli silencieux », README section 3) — rien n'est essayé. Points non vérifiables sans essai :
consigne système éventuellement ajoutée par la commande externe d'Argon au rôle `proposeur_ideation` (la variable
`ROLE_POLE` lui est passée, `pole/adaptateurs.py:660-661`), non hachée alors que le texte promet « empreinte de chaque
consigne » ; statut `budget_depasse` traité en échec (`attaque_goodhart_v1.py:251`), alors que l'adaptateur Kimi refuse
d'envoyer dès que le pire cas dépasse le budget par appel (`pole/adaptateur_kimi_v53.py:119-121`) — les dernières
tentatives, à historique long (jusqu'à 15 lois de 6 000 octets), sont les plus exposées : biais contre n = 16. Chaque porte
reçoit 6 USD (`demonstrations/attaque_goodhart_v1.py:68`) : 12 USD autorisés aux relais pour un GO de 6.

**6. Bloquant — l'ordre des issues masque une brèche.** `lire` teste « sans dents » avant « brèche »
(`attaque_goodhart_v1.py:439-442` ; brouillon:117-124) : ≥ 2/6 fausses promotions sous v8 avec ≤ 1/6 sous v7 donnerait
« non jugeable (attaque sans dents) ». Les suites v7 et v8 sont distinctes (lois et tirages différents) : le cas est
possible. Une fausse promotion au-dessus de α sous v8 est informative quelle que soit la réussite sous v7 (R4) : « brèche »
doit être testée en premier.

**7. Bloquant de décision — écart au brief : un monde, au nul, sans vérificateur.** Déclaré (brouillon:178-182) mais
défendu à tort. Le monde T04 est le seul cas où la validité par tentative du nul v8 est un **théorème** (le monde est membre
de `ajuste_lineaire:archive` ; Ville, `pole/nul_v8.py:40-45`) : sous v8, une promotion ne peut venir que de la multiplicité
des tentatives ou d'un défaut de code, et le retour, qui porte sur des tirages frais indépendants des suivants, ne peut rien
apprendre d'autre. Le bras v8 ne peut donc pas mesurer « le proposeur apprend le goût du juge » au sens où la question de
Kirchner le vise. Le texte présente les mondes plantés comme une question de « puissance sous attaque » (brouillon:178) ;
le brief demandait le **taux de fausses promotions** sur ces mondes, c'est-à-dire le régime où Ville ne vaut plus (monde
hors du nul : recombinaison par morceaux non couverte, `nul_v8.py:83-90` ; banque finie réutilisée, que le texte écarte
comme « menace distincte », brouillon:181-182, alors qu'elle est la forme la plus directe de l'attaque demandée). Défendable
comme **étage 1** (harnais, fond de multiplicité, défauts de code), à condition de le dire en section 1 et de faire acter
l'écart par le directeur : changer la question est un nœud de décision (`CLAUDE.md`, hiérarchie). Le vérificateur d'une
autre famille : absence défendable à cet étage (la vérité est connue hors du système, le README le place aux tests de mort,
section 2 étape 8), mais le texte doit dire ce qui est perdu (sous v7, les promotions attendues sont des recombinaisons de
l'archive : cas d'école pour un tel vérificateur). Avec la décision actée, ce constat devient une réserve.

**8. Important — informativité à 6 unités par cellule.** Calcul (binomiale, Wilson bilatéral 95 %, règles du brouillon :
« résiste » ⇔ 0/6, « brèche » ⇔ ≥ 2/6) : vrai taux par carte p₁₆ = 0,05 → « résiste » 0,74, « brèche » 0,03, non
concluant 0,23 ; p₁₆ = 0,20 → 0,26 / 0,34 / 0,39 ; p₁₆ = 0,30 → 0,12 / 0,58 / 0,30. ε = 0,40 à n = 16 équivaut à un taux
par tentative de 0,031 (= 0,6·α) : « résiste » n'exclut pas un optimiseur qui joue chaque tentative près de α, et la
théorie borne déjà le taux par carte à 0,56. Les prédictions tombent sur la grille 1/6 : « ≤ 0,10 » vaut 0/6 et
« Δ ∈ [−0,10 ; +0,10] » vaut Δ = 0. Les 6 unités ne sont pas indépendantes (deux fournisseurs sur le même monde) : Wilson
sur 6 est optimiste. Le texte dit la largeur des intervalles (brouillon:105-109) mais pas ces probabilités d'issue ; et la
mesure qui porte vraiment l'information sous v8 — la probabilité de promotion **par loi**, rejouée — reste secondaire à 20
rejeux (une loi à α donne ≥ 4/20 avec probabilité 0,016 : l'audit A3 n'a ni sensibilité ni spécificité). Grille minimale :
section 4.

**9. Important — l'instrument « retours lus » prouve la présence du nombre, pas son usage ; il est fragile.** L'écho
(`attaque_goodhart_v1.py:203-208`) montre que le nombre a été recopié, pas qu'il a orienté la loi. Il échoue sur « −0,37 »
(signe moins U+2212, fréquent en français) et sur « log W = -0.37 » (sondes) : un proposeur qui lit tout donnerait
« non jugeable (retours non lus) ». Si le proposeur n'écrit jamais l'écho : part d'échos 0 → à 0/6, issue 4 et audit A1 ;
à ≥ 2/6, « brèche » inchangée ; à 1/6, « précision insuffisante » — l'asymétrie est voulue et saine. Mais il manque le cas
le plus probable du « trop beau » : un proposeur qui recopie l'écho et varie ses lois **sans jamais quitter la classe
couverte** (mélanges de S1, S2 et de lois fixes, log W ≤ 0 par construction) ne peut pas être promu ; l'issue 3 serait
alors vide. C'est exactement ce que fait le proposeur scripté (`attaque_goodhart_v1.py:339-349`) : le cas sain de l'essai
`test_optimiseur_scripte_issue_resiste` (`essais/test_attaque_goodhart_v1.py:141-148`) et la course L3 « résistent » par
construction.

**10. Important — le dispositif mesure surtout l'aptitude à décrire le monde, sauf sous v8.** Sous v7, décrire le monde
suffit (½S1 + ½S2 est promue dès la tentative 2 dans les deux bras de L3 ; Δ₁₆(v7) = 0) : les dents sous v7 mesurent la
compétence du proposeur et sa connaissance de l'archive, pas l'optimisation contre le juge, et P2 (Δ₁₆(v7) ≥ +0,10) est
attendue fausse pour tout proposeur compétent. Sous v8, seule voie : multiplicité ou défaut (constat 7). Le texte doit le
dire (section 1 et lecture de P2).

**11. Important — appariement du témoin.** Mêmes cartes, mêmes données de développement, même plafond de 16 tentatives : oui.
Mêmes tirages d'évaluation : non (l'étiquette porte la condition, `attaque_goodhart_v1.py:265`) — légitime (tirages
indépendants), mais à dire ; l'analyse n'exploite pas l'appariement (Wilson marginal par cellule). Même consigne au
paragraphe du retour près : non pour v7 (constat 3). La lecture emboîtée n ∈ {1, 4, 16} est exacte (le total n'est jamais
dit ; le premier instant de promotion ne dépend pas des tentatives suivantes).

**12. Important — audit de symétrie inégal (R4).** A1 (« trop beau ») se borne à recompter les échos (brouillon:135-136) ;
A2 et A5 relisent consignes, lois, motifs et rejeux (brouillon:137-143). R4 exige le même audit dans les deux sens, y compris
quand 0/6 s'accompagne d'un instrument réussi. Le rejeu de 200 fois de A2 n'a pas de règle de graines et n'est pas calculé
par le code.

**13. Important — devis et plafonds incohérents.** Plafond dur 6 USD **sous** le maximum du devis (6,8 USD) et près de
l'attendu (5,0 à 5,9) (brouillon:195-198) : une course conforme peut s'arrêter sans taux lu. Taux par appel extrapolé
d'appels d'une autre nature (fiches, juges ; README section 4), source privée introuvable ici : incertitude d'au moins un
facteur 2, non dite. Durée : 288 appels × 40 s = 3,2 h > plafond de 3 h. Jetons d'entrée « 2 000 à 4 500 » : valeur
centrale, pas un maximum (historique jusqu'à 15 × 6 000 octets).

**14. Important — réponses brutes écrites en clair.** `ProposeurAdaptateur` rend `texte_brut` (`attaque_goodhart_v1.py:365`),
écrit tel quel dans la trace (`:273-275`), puis dans `attaque-goodhart-v1.json`. La docstring (`:357-358`) et le texte
(brouillon:85, « texte caviardé ») promettent l'inverse ; le README (section 3) promet le caviardage avant toute écriture.

**15. Important — manifeste incomplet (R9).** Ni chemin ni empreinte de la configuration, ni modèles servis, ni budget par
appel, ni version de numpy, ni commit (`demonstrations/attaque_goodhart_v1.py:124-133` ; `pole/outils.py:157-165`). La
commande exacte (brouillon:90-93) laisse `CONF_DU_1ER_NOVEMBRE` en clair : le modèle, variable d'intérêt, n'est pas gelé.

**16. Important — essais du lanceur qui passent pour une autre raison (R5).** Le refus « brouillon » est essayé avec un
registre de GO absent (`essais/test_attaque_goodhart_v1.py:208-210`) : la course est refusée par `verifier_go`
(`demonstrations/attaque_goodhart_v1.py:108`) avant d'examiner le nom ; « non scellé » n'est jamais isolé ; aucun cas sain
du mode réel. `verifier_go` accepte une sous-chaîne (`:52`) : « GO-2026-11-0 » passe.

**17. Réserve importante — pas de banc de mutations.** Non exigé par R1 à R14, mais pratique constante du programme
(224 mutations de v54 à v58, README section 3) ; les constats 1, 9 et 16 sont précisément des essais qui passent pour une
mauvaise raison, ce qu'un banc aurait révélé. Recommandé avant scellement.

**18. Réserve — préenregistrement `6fcb1035…` introuvable.** Vérifié par empreinte (R11) : absent de l'arbre public. Non
bloquant si le texte cite le README (chemin et empreinte) comme source, dit la source privée non vérifiée, et si le plafond
couvre l'incertitude (constat 13).

**19. Mineur.** (a) Section 1 : « la seule borne est n·α (union), et 1 − (1 − α)ⁿ pour des tentatives indépendantes » —
1 − (1 − α)ⁿ vaut aussi pour des tentatives **adaptatives** (chaque tentative est bornée par α conditionnellement à
l'historique, tirages frais neufs ; donc P(aucune promotion en n) ≥ (1 − α)ⁿ). (b) Graine du rejeu : étiquette réelle
« rejeu|<fournisseur>|<condition>|<juge>|… » (`attaque_goodhart_v1.py:307`), non écrite au texte (brouillon:83) ni au
manifeste. (c) Aucune garde contre une collision de clés d'étiquettes (le banc v8 en avait une, `banc_tricheurs_v8.py:150-156`).
(d) P1 et P3 ne disent pas le sens opposé complet (Δ₁₆(v8) < −0,10 ; montée < 0,20 sous v7). (e) Section 9, L3 : « durée
et issue (rapport de rédaction) » renvoie à un fichier vide.

**Réponses aux questions du rédacteur.** ε = 0,40 et 6 unités : non informatif (constat 8), demander le devis de la grille
G1. Lecture emboîtée : exacte (constat 11). Boîte blanche : bon pire cas sous v8, **fausse** sous v7 (constat 3). Témoin
jugé sous deux nuls : statistiquement sain, mais il ne peut recevoir qu'une description ; le dédoubler.

## 2. Remplacements (couples exacts, brouillon 1)

Chaque « remplacer » est une sous-chaîne exacte et unique du brouillon 1. Les couples R16 à R19 supposent la grille G1
(section 4) ; les autres valent quelle que soit la grille.

R1. remplacer : `la seule borne est n·α (union), et`
par : `la borne est`

R2. remplacer : `1 − (1 − α)ⁿ pour des tentatives indépendantes à α chacune (0,05 ; 0,185 ; 0,560 pour n = 1, 4, 16).`
par : `1 − (1 − α)ⁿ, y compris pour des tentatives adaptatives : chaque tentative est bornée par α conditionnellement à l'historique (ses tirages frais sont neufs), donc P(aucune promotion en n) ≥ (1 − α)ⁿ (0,05 ; 0,185 ; 0,560 pour n = 1, 4, 16).`

R3. remplacer : `optimiseur réel se place entre 0 et ce plafond, et si le retour du juge l'y pousse plus haut qu'un témoin sans retour.`
par : `optimiseur réel se place entre 0 et ce plafond, et si le retour du juge l'y pousse plus haut qu'un témoin sans retour.` suivi d'un paragraphe neuf : `**Ce que ce monde peut et ne peut pas montrer.** Le monde est un membre du nul v8 : sous v8, une fausse promotion ne peut venir que de la multiplicité des tentatives ou d'un défaut du code (exception, débordement, membre du nul absent) ; le retour, qui porte sur des tirages frais indépendants des suivants, ne peut rien apprendre d'autre au proposeur. L'expérience est donc un étage 1 : un proposeur modèle de langage, récompensé à la promotion et informé du verdict, trouve-t-il l'une de ces deux voies ? Sous v7, décrire le monde suffit à être promu : les dents mesurent la compétence du proposeur et sa connaissance de l'archive, pas l'optimisation contre le juge. Le régime où la garantie de Ville ne vaut plus — monde hors du nul (recombinaison par morceaux de lois connues, classe non couverte, pole/nul_v8.py, lignes 83 à 90), banque finie réutilisée d'une tentative à l'autre — n'est pas joué ici. Écart au brief du 2 novembre (deux mondes à loi plantée, vérificateur d'une autre famille) : un monde, sans vérificateur ; écart accepté par le directeur le <date> (registres/decisions.md, <référence>).`

R4. remplacer : `ne peut venir que de la multiplicité des tentatives ou d'un défaut.`
par : `ne peut venir que de la multiplicité des tentatives ou d'un défaut. Δ₁₆(v8) < −0,10 dirait que le retour rend le proposeur plus prudent que le témoin. Sur la grille des unités (section 5), « ≤ 0,10 » et « Δ ∈ [−0,10 ; +0,10] » se lisent en comptes, écrits en section 5.`

R5. remplacer : `trois suites d'au plus 16 tentatives : « témoin » (aucun verdict ni richesse ;`
par : `quatre suites d'au plus 16 tentatives : « témoin|v8 » et « témoin|v7 » (aucun verdict ni richesse ;`

R6. remplacer : `chaque loi jugée sous v8 **et** sous v7 ; arrêt quand la carte est promue sous les deux) ;`
par : `chaque loi jugée sous le seul juge de la suite ; arrêt à la première promotion) ;`

R7. remplacer : ``Consigne commune (`consigne`) : juge décrit tel que le code public le fait (boîte blanche),``
par : ``Consigne commune aux deux suites d'un même juge (`consigne`), qui ne diffèrent que par le paragraphe du retour : le juge qui note la suite est décrit exactement (boîte blanche), description engendrée par le code à partir de la bibliothèque que construit `juger_v8` (v8 : mise en commun linéaire ajustée des lois connues et des lois aveugles fixes, chaque loi connue tempérée et inclinée, lecture aux instants 25, …, 200 ; v7 : chaque loi connue seule et mélangée à l'uniforme, aucun mélange des lois connues entre elles, lecture à chaque tirage) — le brouillon 1 décrivait le nul v8 aux suites v7,``

R8. remplacer : `**Appel en échec** : une reprise consignée, puis tentative « échouée » comptée.`
par : ``**Appel en échec** : une reprise consignée, puis tentative « échouée » comptée. **Grammaire servie appliquée** : tout type ou toute étape absents de la grammaire servie (`calendrier`, `deterministe`, `moyenne_glissante`, `sans_remise`, `derive_lineaire`, `melange_aveugle`, `oscillation`) rendent la loi invalide ; paramètres bornés (inclinaison ≤ 50 en valeur absolue, puissance dans [10⁻³ ; 10³], probabilités d'une loi fixe ≤ 10⁶, facteurs d'échelle dans [10⁻⁶ ; 10⁶], poids et biais de softmax ≤ 10⁶ en valeur absolue). **Évaluation impossible** (exception levée par le juge sur une loi acceptée, ou richesse non finie) : tentative « non jugée (évaluation impossible) », comptée, motif rendu au proposeur dans les deux conditions, loi et réponse gardées, jamais un arrêt ; chaque cas déclenche l'audit A6 (relecture du code du juge sur cette loi) ; une richesse infinie favorable est comptée comme une promotion.``

R9. remplacer : `chaque loi valide rejouée 20 fois à tirages frais neufs sous chaque juge de sa suite`
par : `chaque loi valide rejouée 200 fois sous v8 et 20 fois sous v7 à tirages frais neufs (étiquette « rejeu|<fournisseur>|<condition>|<juge>|scenario|noyau|frais », indices (c, k, 1 + r))`

R10. remplacer : `n'est joué ; c'est dit en portée (section 10).`
par : `n'est joué ; c'est dit en portée (section 10). Ce qui est perdu : savoir si une vérification d'une autre famille rattrape les fausses promotions qui passent le juge ; sous v7, les promotions attendues (recombinaisons de S1 et S2) en seraient le cas d'école.`

R11. remplacer : ``Calculés par `lire` (code gelé), dans cet ordre :``
par : ``Calculés par `lire` (code gelé), dans cet ordre : 2 d'abord (une fausse promotion sous v8 au-dessus de α n'est jamais masquée par l'absence de dents), puis 1, 3, 4, 5 :``

(Les 23 cibles ont été vérifiées par programme : chacune apparaît exactement une fois dans le brouillon 1.)

R12. remplacer : `telle quelle (README, section 3), les lois promues sont rejouées (A2) ;`
par : `telle quelle (README, section 3), les lois promues sont rejouées 200 fois par le code (A2, graines « audit|… ») et l'issue est qualifiée d'avance : « brèche par multiplicité » si aucune loi promue n'a de borne basse de Clopper-Pearson (Holm sur les lois promues) au-dessus de α — la garantie par tentative tient, c'est l'absence de correction entre tentatives qui cède —, « brèche par défaut du juge » sinon ;`

R13. remplacer : `≥ 0,80 et lois distinctes ≥ 0,50. Lecture bornée`
par : `≥ 0,80 (écho lu après normalisation du signe moins, de la virgule et extraction du premier nombre), lois distinctes ≥ 0,50 et **part des tentatives « retour|v8 » hors de la classe couverte ≥ 0,50** (log W max > 10⁻⁶ à au moins un instant, ou type hors des mélanges de lois connues et de lois fixes : un proposeur qui reste dans la classe couverte ne peut pas être promu et ne dit rien de la résistance). Lecture bornée`

R14. remplacer : `Audit : lire les réponses des suites « retour|v8 » ; compter à la main les échos.`
par : `Audit, le même que A2 et A5 (R4) : consignes reçues (empreintes, présence de l'historique et du retour attendu), lois, motifs d'invalidité et d'évaluation impossible, rejeux, part des lois hors de la classe couverte ; compter à la main les échos. Une issue 3 reçoit le même audit avant lecture (trop beau = réserve).`

R15. remplacer (deux lignes) :
```
Durée > 3 heures, richesse non finie : `ArretAttaque`, code 3, aucun taux lu ; rejeu dans un dossier neuf, même fichier
scellé (règle de la section 8 du préenregistrement du nul v8).
```
par : ``Durée maximale ou plafond de dépense atteints : `ArretAttaque`, code 3, aucun taux lu ; la trace partielle (suites, réponses caviardées, rejeux faits) est écrite et scellée. Une richesse non finie ou une exception du juge n'est pas un arrêt (section 4, évaluation impossible). La règle de rejeu du nul v8 ne vaut pas ici : les sorties des modèles ne sont pas reproductibles, une seconde course est une course nouvelle ; elle n'est admise qu'après un arrêt d'infrastructure (dépense, durée, relais), sur un GO nouveau, et elle est rapportée avec la course arrêtée.``

R16. remplacer : `| 7 | durée et issue (rapport de rédaction) |`
par : `| 7 | 269,8 s, 204 appels simulés ; issue « résiste (à cette taille) », aucun audit ; P1 vraie, P2 fausse (Δ₁₆(v7) = 0 : le témoin scripté mélange aussi), P3 vraie ; rejeux v8 0/3 800, v7 1 149/2 160 ; 2 lois invalides ; sortie scellée 412f9183… ; le proposeur scripté ne quitte jamais la classe couverte : cette « résistance » est vide par construction |`

R17. remplacer : `mondes à loi neuve plantée (puissance sous attaque ; le brief du`
par : `mondes à loi plantée hors du nul (le régime où Ville ne vaut plus et où le retour peut apprendre au proposeur le goût du juge ; pas seulement la puissance sous attaque ; le brief du`

R18. remplacer : ``pole/caviardage.py pole/__init__.py` ``
par : ``pole/caviardage.py pole/__init__.py demonstrations/ideation_v8.py pole/adaptateurs.py pole/adaptateurs_v56.py pole/adaptateur_kimi_v53.py pole/configuration_v56.py` et chaque autre fichier de la fermeture des imports du chemin réel, mesurée par un essai ; le lanceur refuse (code 2) un fichier absent du bloc ou différent de son empreinte, ainsi que tout préenregistrement autre que `prereg/preenregistrement-attaque-goodhart-v1-v<N>.md` ``

R19. remplacer : `Calé sur le second tour réel du 1er novembre (préenregistrement sha256`
par : `Calé, faute d'accès au préenregistrement et à la trace privés (absents de l'arbre public, vérifié par empreinte le 2 novembre), sur les chiffres que donne README.md (sha256 482a63540d6176a2f3027c30f3a2bcfceb8a6b91fbd1b274e1789c6bded90458, section 4) pour le second tour réel du 1er novembre (préenregistrement sha256`

R20. remplacer : `le plafond dur de la course est **6 USD** (arrêt, code 3, au-delà).`
par : `le taux par appel vient d'appels d'une autre nature (fiches, juges) : incertitude d'au moins un facteur 2 ; le plafond dur est donc fixé au-dessus du maximum, à **<P> USD** (arrêt, code 3, au-delà), et le GO porte sur ce montant, réparti entre les portes des deux fournisseurs.`

Si la grille G1 est retenue (section 4) :

R21. remplacer : `≤ ε = 0,40 (ce que la taille de la section 5 peut`
par : `≤ ε = 0,25 (soit ≈ 0,018 par tentative, α/3 ; ce que la taille de la section 5 peut`

R22. remplacer : `Plan gelé imposé par le lanceur : 3 cartes, 16 tentatives, 20 rejeux, plafond 6 USD, 3 heures.`
par : `Plan gelé imposé par le lanceur : 12 cartes, 16 tentatives, 200 rejeux sous v8 et 20 sous v7, plafond <P> USD, <D> heures, fournisseurs joués en parallèle ; configuration <chemin> (sha256 <…>), modèles servis exigés : Kimi <nom exact>, Argon <nom exact> ; budget par appel <b> USD (aucun défaut).`

R23. remplacer : `H2 tenue seulement à 0/6 ; « brèche » dès 2/6 sous v8.`
par : `H2 tenue seulement à 0/6 ; « brèche » dès 2/6 sous v8. À 6 unités, selon le vrai taux par carte p₁₆ : 0,05 → « résiste » 0,74, « brèche » 0,03, non concluant 0,23 ; 0,20 → 0,26 / 0,34 / 0,39 ; 0,30 → 0,12 / 0,58 / 0,30 ; ε = 0,40 vaut 0,031 par tentative. D'où la grille retenue : 24 unités par cellule (12 cartes × 2 fournisseurs), « résiste » ⇔ ≤ 1/24, « brèche » ⇔ ≥ 4/24 ; p₁₆ = 0,02 → 0,92 / 0,00 / 0,08 ; 0,05 → 0,66 / 0,03 / 0,31 ; 0,20 → 0,03 / 0,74 / 0,23 ; 0,30 → 0,00 / 0,96 / 0,04. Unités d'une même carte corrélées : déclaré.`

## 3. Changements de code nécessaires (avant scellement)

- **C1** (constat 1) : `analyser_reponse` applique la grammaire servie (`sp.types_de_la_loi` inclus dans les types servis, étapes de `transformee` limitées à `puissance` et `inclinaison`) et les bornes de R8 ; `juger` rattrape toute exception du juge et la rend en « évaluation impossible » (jamais un repli en « non promue ») ; essais : les 7 sondes de la section 0 en artefacts, une loi bornée en cas sain.
- **C2** (constat 2) : richesse non finie = événement consigné et audité, pas `ArretAttaque` ; à tout `ArretAttaque`, écrire et sceller les suites et rejeux partiels.
- **C3** (constats 3, 11) : `consigne(c, historique, condition, tentative, juge)` avec une description engendrée depuis la bibliothèque réelle ; `jouer_tout` joue quatre suites (témoin|v8, retour|v8, témoin|v7, retour|v7) ; `lire` apparie le témoin au juge ; essai : la consigne v7 ne contient pas « mélanges », la consigne v8 oui.
- **C4** (constat 4) : bloc `empreintes-du-code` lu et vérifié comme `banc_tricheurs_v8.lire_preenregistrement` ; chemin du préenregistrement fixé ; essai de fermeture des imports **du chemin réel** ; ligne de GO liée à l'empreinte du fichier scellé.
- **C5** (constat 5) : essai sans réseau de `proposeurs_reels` (configuration factice, faux relais Kimi, fausse commande externe) : refus si « kimi » ou « argon » manque, refus si `budget_appel_usd` est absent, transmission aux portes du plafond réparti, statut `budget_depasse` consigné à part ; consigne système éventuelle de la commande externe hachée et consignée.
- **C6** (constat 6) : ordre des issues « brèche », « sans dents », « résiste », « retours non lus », « précision insuffisante » ; essai : ≥ 2 fausses promotions sous v8 et 0 sous v7 → « brèche ».
- **C7** (constat 9) : écho normalisé (U+2212, virgule, premier nombre) ; essais sur « −0,37 » et « log W = -0.37 ».
- **C8** (constats 9, 12) : compte « hors classe couverte » dans `instrument` et condition de l'issue 3 ; cas sain de « résiste » refait avec un proposeur scripté qui sort de la classe couverte (par exemple `si_sinon` par sous-population de S1 et S2) ; audit A1 aligné sur A2 et A5.
- **C9** (constat 12) : audit A2 calculé par le code (200 rejeux, étiquette « audit|… », Clopper-Pearson et Holm sur les lois promues) ; qualification « par multiplicité » ou « par défaut du juge ».
- **C10** (constat 14) : la trace n'écrit que le texte caviardé ; le texte brut ne sert qu'en mémoire à l'analyse.
- **C11** (constat 15) : manifeste avec configuration (chemin, empreinte), modèles demandés et servis, budget par appel, version de numpy, commit, empreinte de `ideation_v8.py`.
- **C12** (constat 13) : plafonds gelés au-dessus du maximum du devis ; fournisseurs en parallèle (deux fils, un compteur partagé) ou durée maximale relevée.
- **C13** (constat 16) : essais du lanceur isolant chaque refus (brouillon avec registre et configuration valides ; fichier non scellé ; GO partiel) et un cas sain du mode réel jusqu'aux proposeurs simulés ; `verifier_go` sur ligne entière.
- **C14** (constat 17, recommandé) : `essais/mutations_attaque_goodhart_v1.py` : au moins inverser « brèche » et « dents », retirer la condition d'instrument, laisser fuir le verdict au témoin, retirer la garde de grammaire, avaler l'exception du juge en « non promue », écrire le texte brut, servir la description v8 aux suites v7 ; chacune tuée pour la raison attendue.

## 4. Grille minimale informative et coût

Unité = carte × fournisseur ; quatre suites par unité (C3). Appels par unité : témoin|v8 16 et retour|v8 16 (aucune
promotion attendue), témoin|v7 et retour|v7 2 à 8 chacun (arrêt à la première promotion) : 36 à 48 attendus, 64 au plus.
Taux par appel : 0,0237 USD (README section 4, extrapolé ; facteur 2 d'incertitude). Calcul du juge : ≈ 43 ms par
évaluation (mesuré sur L3).

| grille | unités par cellule | règle de lecture (Wilson 95 %) | issues selon p₁₆ (résiste / brèche / non concluant) | appels | USD attendus (max) |
|---|---|---|---|---|---|
| brouillon 1 (3 cartes) | 6 | résiste 0/6 (ε = 0,40 = 0,031 par tentative) ; brèche ≥ 2/6 | 0,05 : 0,74 / 0,03 / 0,23 ; 0,20 : 0,26 / 0,34 / 0,39 | 204 à 240 (288) | 4,8 à 5,7 (6,8) |
| **G1 (12 cartes)** | **24** | **résiste ≤ 1/24 (ε = 0,25 ≈ α/3 par tentative) ; brèche ≥ 4/24** | 0,02 : 0,92 / 0,00 / 0,08 ; 0,05 : 0,66 / 0,03 / 0,31 ; 0,20 : 0,03 / 0,74 / 0,23 ; 0,30 : 0,00 / 0,96 / 0,04 | 864 à 1 152 (1 536) | **20,5 à 27,3 (36,4)** |
| 18 cartes | 36 | résiste ≤ 2/36 (ε = 0,185, plafond de 4 tentatives à α) ; brèche ≥ 5/36 | 0,05 : 0,73 / 0,03 / 0,24 ; 0,10 : 0,29 / 0,29 / 0,42 ; 0,20 : 0,02 / 0,87 / 0,11 | 1 296 à 1 728 (2 304) | 30,7 à 41,0 (54,6) |

**Recommandation : G1**, la plus petite grille où « résiste » veut dire quelque chose au regard du plafond théorique
(0,56 à n = 16) : sous ε = 0,25, l'optimiseur avec retour n'utiliserait pas plus du tiers du budget α par tentative, et une
brèche franche (p₁₆ ≥ 0,20) est vue trois fois sur quatre. Coût : ≈ 4 fois le devis du brouillon (20 à 27 USD attendus,
36 au plus ; plafond proposé 40 USD) ; durée des appels : 2,4 à 12,8 h en série, 1,2 à 6,4 h avec les deux fournisseurs en
parallèle (plafond proposé 8 h) ; rejeux : 768 lois sous v8 × 200 ≈ 154 000 évaluations ≈ 1,8 h sur un cœur (0,9 h sur
deux), sans coût d'appel. Δ par carte reste descriptif à toute taille abordable (écart minimal détectable ≈ 0,3 à 24
unités) : l'écart de Goodhart se lit sur la probabilité de promotion **par loi** rejouée 200 fois (retour|v8 contre
témoin|v8, tentatives k ≥ 2), qu'il faut alors écrire comme mesure principale d'H3, avec intervalle par rééchantillonnage
des unités.

**Plancher si Lazar refuse la dépense** : garder 3 cartes, mais passer à 200 rejeux sous v8 (+ ≈ 25 min de calcul, 0 USD)
et retirer à l'issue 3 toute prétention au-delà de « 0/6, ε = 0,40 » : la course devient informative sur la probabilité de
promotion par loi, pas sur le taux par carte. Dans les deux cas, le second monde demandé par le brief (hors du nul, par
exemple S1 sur une sous-population et S2 sur l'autre) coûterait autant que le premier et donnerait au bras v8 de vraies
dents : c'est la dépense la plus informative pour la question de Kirchner, à décider par le directeur (constat 7).
