# Préenregistrement — le tour fermé pour de vrai (tâches A2, A3 et A4), brouillon 3 (scellement de l'étage 1 seul)

Statut : **brouillon 3 : contre-lecture 2 appliquée pour l'étage 1 (`prereg/contre-lecture-preenregistrement-tour-ferme-v2.md`, sha256 `8a74dfd2…`, verdict « non scellable »), code `_v62` ; non contre-lu une troisième fois (règle R2 : texte et code v62), non scellé. Portée : l'étage 1 seul (décision de Lazar en attente, défaut sous 48 heures : étage 1 seul).** Brouillon 3 rédigé le 2 novembre 2026 par un troisième sous-agent rédacteur-développeur (qui n'a écrit ni les contre-lectures ni les brouillons précédents), sans appel de modèle, sans clé, sans commit, sous `nice -n 10` ; rapport `prereg/rapport-redaction-tour-ferme-v3.md`. Brouillon 1 rédigé le 2 novembre 2026, de 07:02 à 07:45 UTC ; brouillon 2 le 2 novembre, achevé à 09:23 UTC (fichier écrit à 09:23, commit `7d3aa82` à 09:25 UTC ; les heures « 09:30 à 11:10 » du rapport de rédaction sont fausses), par
un second sous-agent rédacteur-développeur (qui n'a écrit ni le brouillon 1 ni la contre-lecture), sans aucun appel de modèle, sans clé, sans commit ni `git fetch`, sous `nice -n 10`. Dépôt public à
la tête `c47b608` pour le brouillon 2 (fichiers `_v61` non suivis), à la tête `82ad7a8` pour le brouillon 3 (fichiers `_v62` non suivis). Le scellement (compagnon `.sha256` écrit par le directeur, sur une version contre-lue renommée
`preenregistrement-tour-ferme-v1-v<N>.md`, sans « brouillon ») fixe la graine (section 8) ; le lanceur (section 13, v62)
refuse tout fichier dont le nom contient « brouillon » et tout fichier non scellé. **Aucune course réelle avant le
scellement, la contre-lecture, la validation par Lazar des décisions D2 à D9 (section 14 ; D1 est prise) et son feu vert (GO) sur le devis
(section 12).** Les cases « à remplir avant scellement » (section 5.2) sont remplies par la session-depot, qui tient les
données privées, puis relues par le contre-lecteur ; un texte qui en garde une vide ne se scelle pas.

## 0. En dix lignes

**Portée de ce scellement : l'étage 1 seul (A2 et A4).** Les sections de l'étage 2 (A3) restent dans ce texte, entre les balises `etage-2-hors-scellement`, **hors de ce scellement : texte de l'étage 2 à sceller plus tard, avant toute lecture de T**, non corrigées par la contre-lecture 2 ; le lanceur v62 ne lit pas ces zones (marqueurs compris) et refuse tout étage 2. L'étage 2 sera un préenregistrement à part (texte, code, configuration et GO à lui), dont la porte lira la lecture scellée de l'étage 1.

Un seul préenregistrement, deux étages. **Étage 1 (A2 et A4)** : la boucle fermée de la v59 (`pole/boucle_fermee_v59.py`)
jouée avec de vrais modèles sur un monde à loi plantée connue hors du système (S-V1 de `exemples/temoins-pari-demo-v1.json`),
trois générations, trois bras : le **bras réel** (Kimi et Argon proposent), le **bras aléatoire** et le **bras qui recopie
ou mélange** les lois déjà retenues, tous passés par la même chaîne — gardien, juge statistique sous le nul v8, tests de mort
exécutés dans le vrai bac à sable, vérificateur d'une autre famille, sélection scellée lue par la génération suivante. Des
témoins plantés (la loi vraie, quatre lois fausses, deux cas d'instrument) sont mêlés à chaque génération de chaque bras.
**Étage 2 (A3)** : le même tour sur la vraie question du 1er novembre, sur la banque d'épisodes réels, avec des **données
tenues à l'écart réservées par empreinte avant la course** ; joué **seulement si l'étage 1 tient** (critère gelé, section
4.6). Zéro promotion à l'étage 2 est un résultat et se rapporte tel quel (règle R3 : aucun run visant un signe).

## 1. Question, motivation, ce qui existe

- **Question (Lazar, addendum au brief de reprise du 2 novembre)** : la chaîne entière — proposition, garde de forme,
  jugement statistique, test de mort exécuté, vérification croisée, sélection — tient-elle quand elle est fermée et jouée
  avec de vrais modèles (A2) ? Quel est son taux de fausses découvertes face à des proposeurs sans intelligence (A4) ?
  Promeut-elle au moins une hypothèse réelle qui survit à un test exécuté sur des données tenues à l'écart (A3) ?
- **Pour le mentor** (Jan Kirchner, « chercheurs d'alignement automatisés ») : l'étage des tests de mort et la boucle entre
  générations n'ont jamais tourné pour de vrai (README, section 4 : « Death tests and generation-to-generation loop :
  implemented, tested offline, never run for real ») ; les lancements réels du 27 octobre exécutaient déjà du code en bac à
  sable, mais dans un monde tautologique (plomberie, pas découverte). Ce tour serait le premier où une hypothèse écrite par un
  modèle sur une question réelle peut être promue par le juge figé puis vérifiée par exécution sur des données tenues à
  l'écart.
- **Ce qui existe** (rapport `prereg/rapport-code-boucle-fermee-v1.md`, sha256 `884b4f4f…`) : la v59 ferme la flèche
  « sélection → génération suivante » (bilan scellé, lecture vérifiée par empreinte, contre-vérification des retenues contre
  les verdicts scellés du noyau, vue des proposeurs sans verdict), les deux proposeurs de référence
  (`pole/proposeurs_references_v59.py`), un mode à blanc joué dans le vrai bac à sable (`bwrap` 0.9.0), 28 essais et 9 mutations
  tuées sur 9. **Ce qui manque** pour ce tour, dit en section 13 : un lanceur à vrais modèles (écrit en `_v61` pour l'étage 1, section 13 ; cœur de l'étage 2 non écrit), des témoins exclus de
  l'archive, un gabarit de test de mort imposé aux proposeurs, un contre-calcul de la statistique par l'orchestrateur, la porte entre étages. Sont écrits avec ce brouillon : la réserve par empreinte des données tenues à l'écart
  (`pole/reserve_tenue_a_l_ecart_v60.py`), l'oracle avec le classement gelé des cartes et les intervalles
  (`pole/oracle_tour_ferme_v60.py`) et la lecture gelée des deux étages (`pole/lecture_tour_ferme_v60.py`, remplacée pour ce texte par `pole/lecture_tour_ferme_v61.py`, section 4.6) : 46 essais,
  17 mutations tuées sur 17 pour la raison attendue.

## 2. Ce que voient les proposeurs (point ouvert (i) du développeur — décision D1, prise par Lazar : GO-2026-11-02-06, registres/go.md, 2 novembre 2026)

**Changement par rapport à la v57 et aux tours réels précédents.** Jusqu'à la v56, la génération suivante héritait du
**classement des juges**, écrit avant l'étage des tests de mort (README, section 2, étape 9). En v59 et dans ce tour, chaque
proposeur reçoit **seulement** (`boucle_fermee_v59.vue_pour_proposeur`, garde `exiger_vue_sans_verdict`) :

1. la **liste des lois retenues** de son bras (identifiant opaque `F-<12 hexadécimaux>`, empreinte de l'identifiant réel, et loi prédictive, rien d'autre ; l'identifiant réel d'une carte, `G<g>-<proposeur>-<nn>`, qui dit sa génération et son auteur, n'est jamais servi : code v62, C15) : celles dont le verdict
   scellé du noyau au test de mort est « survit », cumulées depuis la génération 1 ;
2. la description publique du monde (traits, sous-populations, nombre d'issues ; jamais une issue de l'épreuve), le gabarit (types de loi permis **avec les champs exacts de chaque type, ceux de `selection_pari.valider_loi`, et un exemple valide par type**, borne des poids ; section 4.1) et, à l'étage 1, **200 épisodes de développement** tirés à chaque génération dans le
   monde planté (traits, sous-population, issue ; graine de la tâche « développement ») ; à l'étage 2, la partie
   « développement » de la banque (section 5.3) et le texte de la question ;
3. une consigne figée (empreinte consignée au manifeste) : « propose au plus 6 lois qui prédisent l'issue mieux que la
   marginale et mieux que les lois déjà retenues ».

**Jamais** : un verdict, une richesse, un log e, une promotion, un rang, un motif d'élimination, un compte, une carte non
retenue (y compris les siennes), une carte d'un autre bras, un témoin. La garde lève `VueAvecVerdict` sur toute clé interdite
à toute profondeur (essais v59 : cas sain et artefact ; mutation « garde neutralisée » tuée).

Conséquence à lire honnêtement : le seul canal d'information du juge vers les proposeurs est **un bit par carte testée**
(retenue ou non), porté par la présence d'une loi dans la vue. Le préenregistrement de l'attaque de Goodhart (A1, brouillon 1)
mesure le pire cas où ce canal serait large (verdict et richesse rendus) ; ici il reste étroit, par construction.

## 3. Définitions gelées (point ouvert (ii) — décision D2)

**Oracle** (audit seulement : jamais servi, jamais décisif pour la chaîne ; `pole/oracle_tour_ferme_v60.py`, écrit avec ce
brouillon, 14 essais, 4 mutations tuées sur 4) :
sur 4 000 instances tirées une fois (tâche « oracle|instances », racine des graines de la section 8), avec L* la loi plantée,
m* la marginale du monde et q la loi d'une carte :

- **G(q)** = E_x E_{y∼L*(x)} [log q(y|x) − log m*(y)] : gain attendu de log-score sur la marginale, en nat par épisode
  (exemples, lecture L1 : L* 0,523 ; S-F2 −0,133 ; loi plantée restreinte au trait z1 0,402) ;
- **D(q)** = E_x KL(L*(x) ‖ q(x)) : divergence de Kullback-Leibler moyenne de la loi plantée à la carte ;
- **G_arch** : meilleur gain connu de l'archive que la carte a affrontée au jugement, dans la classe du nul v8 calculée au
  niveau de l'oracle : max(0 ; G de chaque loi de l'archive ; G de la mise en commun linéaire des lois de l'archive, de
  l'uniforme et des trois lois certaines, poids ajustés par maximum de vraisemblance sur les 4 000 instances ; G de chaque loi
  de l'archive tempérée et inclinée, p(k) ∝ S(k)^a·exp(β_k), ajustée de même) ; **ΔG = G(q) − G_arch**.

Seuil gelé **g₀ = 0,02 nat par épisode** (le seuil du test de mort des cartes, section 4.1).

| issue d'une carte (non témoin) | définition gelée |
|---|---|
| **promue** | retenue par la règle de Benjamini-Hochberg sur e-valeurs (e-BH) de sa génération et de son bras, au niveau α = 0,05 |
| **promue puis survivante** (PS) | promue **et** verdict scellé du noyau « survit » au test de mort (seul ce cas entre à l'archive) |
| **vraie découverte** (VD) | PS **et** ΔG ≥ g₀ (G ≥ g₀ en découle, puisque G_arch ≥ 0 ; l'oracle rapporte les deux) : la carte porte au moins 0,02 nat d'information sur le monde au-delà de sa marginale **et** au-delà de ce que l'archive savait déjà |
| **loi plantée retrouvée** (VD*) | VD **et** D ≤ 0,05 nat |
| **fausse découverte** (FD) | PS **et** (G < g₀ **ou** ΔG < g₀). Toute PS du bras « recopie-mélange » est une FD par construction (sa loi est fonction des seules lois de l'archive), quel que soit l'oracle |
| **fausse promotion du juge** | promue **et** (G < g₀ ou ΔG < g₀), quel que soit le test de mort (erreur du juge que le test de mort doit rattraper) |
| **inconclusive** | verdict du noyau « non concluant » (aucune exécution réussie, fichier brut absent ou illisible, plafond de la fiche atteint sans fichier, incident de la fiche). Une session en échec, un refus de modèle (R-764) ou un contre-calcul en désaccord **arrêtent** la course (section 7, gardes 10 et 13) : ce ne sont pas des « non concluant » |

Pourquoi cette définition : le mode à blanc v59 a vu une loi aléatoire promue et survivante qui porte une vraie information
(G1-ALEA-06 : +0,30 nat, divergence 0,22 nat à la loi plantée) ; la lecture L2 (section 10) montre que, dans ce monde,
**13 % des lois aléatoires de la grammaire portent G ≥ 0,02** (159 sur 1 200). Appeler « fausse » toute découverte qui n'est
pas la loi plantée compterait comme erreurs de la chaîne des découvertes partielles vraies ; appeler « vraie » toute loi qui
survit compterait comme découvertes des redites de l'archive. La définition retenue sépare les deux : information sur le
monde (G) **et** nouveauté par rapport à l'archive (ΔG). Limite dite : ΔG est mesuré contre la classe du nul v8 calculée à
l'oracle, pas contre toute recombinaison concevable de l'archive.

## 4. Étage 1 — monde à loi plantée, bras réel et deux bras de référence (A2 et A4)

### 4.1 Plan

- **Monde** : la loi plantée L* est celle du témoin vrai S-V1 de `exemples/temoins-pari-demo-v1.json` (sha256
  `fdf4d5c1ca0d2971b416ee5f694deff7a4696fe5defb3a6a1843dffef1231877`) : softmax, 3 issues, 2 traits gaussiens, 2
  sous-populations — la classe de mondes du banc des tricheurs v8, sur laquelle le nul v8 a été validé
  (`prereg/preenregistrement-validation-nul-v8-v2.md`, sha256 `7f37631d…` ; issue « confirmée »). Monde jamais servi.
- **Générations** : 3 par bras (la boucle se referme deux fois) ; la génération g+1 de chaque bras lit le bilan scellé de la
  génération g (`lire_heritage`, empreinte passée par l'orchestrateur) avant toute proposition.
- **Bras réel** : Kimi (K3.1 Pro) et Argon (Gemini), modèles et adaptateurs de la configuration du second tour réel du
  1er novembre (`demonstrations/ideation_v8.adaptateurs_reels_v56`) ; un appel par proposeur et par génération, au plus
  6 cartes chacun (12 emplacements par génération). Gabarit fermé de la proposition : `{enonce (≤ 400 caractères),
  loi_predictive}` (types softmax, par_sous_population, si_sinon, melange, fixe, transformee ; dimension 2 ; 3 issues ; poids
  bornés à ±4 ; la consigne figée sert la grammaire exacte : champs de chaque type selon `selection_pari.valider_loi` et un exemple valide par type, chacun essayé par `valider_loi` ; v62). **L'orchestrateur complète** tous les autres champs, dont le test de mort : le proposeur ne choisit ni la
  statistique, ni le seuil, ni les données (garde neuve, section 7).
- **Bras aléatoire** : `proposeurs_references_v59.proposer_aleatoire`, 12 cartes par génération (softmax sur un ou deux traits,
  poids gaussiens d'écart-type 1,2 bornés à ±4, biais nuls) ; vue vérifiée, jamais lue. Décision D7 (paramètre `d7` du plan gelé, <<DECISION_D7>>) : « archive_du_bras_reel » = ses cartes sont jugées contre l'archive du bras réel de la même génération (même nul que les cartes réelles) et ses retenues ne sont jamais utilisées au jugement ni servies (son bilan v59 existe, lu et vérifié, archive jamais lue) ; « archive_propre » = sa propre boucle. Ordre dans une génération : réel, puis recopie-mélange, puis aléatoire. Les témoins sont testés dans leur propre étage (même tranche que les cartes), ce qui les tient hors de la sélection v57 et de l'archive.
- **Bras recopie-mélange** : `proposeurs_references_v59.proposer_recopie_melange`, au plus 12 cartes par génération, faites des
  seules lois **retenues par le bras réel** jusqu'à g−1 (décision D4 : il lit, vérifié par empreinte, le bilan du bras réel,
  et ses cartes sont jugées contre l'archive du bras réel, c'est-à-dire contre le même nul que les cartes réelles de la même
  génération). Génération 1 : archive vide, aucune carte (motif consigné, aucun repli). S'il n'a aucune carte en générations
  2 et 3, sa mesure est « non mesurable » (issue écrite, section 4.7).
- **Témoins** (ajoutés à chaque génération de chaque bras qui joue ; identifiants opaques ; servis à l'expérimentateur sous le même titre et le même énoncé neutres que les cartes, sans bras ni statut de témoin, v62 ; jugés comme témoins,
  sans membres d'archive, comme `cycle.Generation.geler` ; **jamais retenus, jamais servis**, décision D3) :
  T-VRAIE = L* ; T-F1, T-F2, T-F4 = S-F1, S-F2, S-F4 (G = −2,35 ; −0,13 ; −0,91) ; T-ANTI = poids opposés à L* (G = −3,81) ;
  T-ELIM (instrument du test de mort) = L* accentuée (puissance 1,25) dont le test exige un gain d'au moins 2,0 nat
  (inatteignable) ; T-MAL (instrument du gardien) = carte sans bloc `statistique`. Le cas « inconclusif » scripté du mode à
  blanc v59 n'est pas repris (un expérimentateur modèle ne se scénarise pas) ; il reste dans la répétition à blanc.
- **Gardien** : deux couches, la même pour les trois bras et les témoins. (a) mécanique : gabarit, `selection_pari.valider_loi`,
  `tests_de_mort_v5.valider_champ_test` (bloc `statistique` exigé) ; (b) **retirée** (décision D9, recommandation de la contre-lecture, I6 : gardien mécanique seul, décisif, pour les trois bras ; l'aiguilleur v53 est hors de portée ; le lanceur refuse `d9 = aiguilleur` avant tout appel).
- **Juge** : `a_blanc_v59.juger_carte` (appel pour appel `banc_tricheurs_v8.juger_v8`, genre « fraîche ») : bibliothèque
  aveugle + marginale d'entraînement (100 tirages) + membres d'archive du nul v8 (`nul_v8.membres_archive_v8` sur l'archive du
  bras), engagement gelé, ordre secret, 200 tirages frais liés à l'empreinte de l'engagement, lecture aux instants fixés ;
  puis e-BH par (bras, génération) avec **m fixé à 19** avant toute issue (12 emplacements de cartes + 7 témoins, les témoins
  comptant dans m mais lus hors famille (au seuil m/α, sans peser sur k*, comme le témoin vrai de `cycle.appliquer_multiplicite`) ; un emplacement vide vaut e = 0) — le même m dans les trois bras.
- **Tests de mort** : étage v5 (`tests_de_mort_v5`) par `etage_entre_generations_v57.jouer_etage_v57`, dans le **vrai bac à
  sable** (`bwrap`, sans réseau, un seul dossier, 768 Mo tenus par le bac et annoncés dans la consigne de l'étage (v62 ; la v61 annonçait le quota par défaut de l'étage, 1 024 Mo, non tenu), filtre d'appels système, identité dédiée sans privilège ; jamais de
  repli sur l'exécuteur factice), pour toutes les cartes promues et tous les témoins promus de la génération. Tranche : 400
  épisodes frais du monde planté par (bras, génération). Gabarit gelé du test (`proposeurs_references_v59.TEST_DE_MORT`) :
  gain moyen par épisode du log-score de la loi sur la marginale empirique de la tranche (comptes + 0,5), fichier brut
  `gains.csv`, colonne `gain`, statistique « moyenne », seuil « au moins 0,02 », valeurs écrites en pleine précision (`repr` de Python). **Loi servie** : la loi gelée de la carte (JSON canonique, borné en taille) et l'évaluateur de référence de la grammaire (le code du contre-calcul, fichier de la tranche, même empreinte pour toutes les cartes) sont servis à l'expérimentateur dans le préenregistrement court ; le mode à blanc ne lui passe rien d'autre (v62). **Expérimentateur** : Kimi (session modèle,
  au plus 12 tours, 3 exécutions de 120 s au plus, plafond 0,5 USD (dollars américains) par carte). **Vérificateur** : Argon,
  lecteur témoin d'une autre famille que l'expérimentateur (plafond 0,1 USD par carte), jamais décisif. Verdict : celui du noyau
  v5 sur la copie scellée du fichier brut, **plus** le contre-calcul de l'orchestrateur (section 7, garde 10).
- **Sélection et bilan** : `selection_entre_generations` (v57 : « survit » seulement, témoins exclus), bilan v59 scellé, lu par
  la génération suivante.

### 4.2 Hypothèses

- **H-A2-1 (la loi vraie survit)** : le témoin T-VRAIE est promu et reçoit « survit » du noyau dans presque toutes ses
  passes.
- **H-A2-2 (les fausses sont éliminées)** : aucun témoin faux n'est retenu par la chaîne (promu puis survivant), et T-ELIM
  testé reçoit « éliminée ».
- **H-A2-3 (l'instrument conclut)** : la part de « non concluant » parmi les cartes testées reste sous un seuil.
- **H-A2-4 (la boucle est fermée)** : chaque génération g ≥ 2 de chaque bras lit le bilan scellé de g−1, à l'empreinte
  consignée, et ne sert aucune information du juge aux proposeurs.
- **H-A4-1 (taux de fausses découvertes de la chaîne)** : sous les deux bras de référence, la part de cartes qui deviennent
  des fausses découvertes est petite (bornée par α par carte pour les recombinaisons de l'archive, argument de Ville, et
  par le test de mort pour les lois sans information).
- **H-A4-2 (la chaîne distingue le bras réel du hasard)** : le bras réel produit plus de cartes promues puis survivantes, et
  plus de vraies découvertes, que le bras aléatoire.

### 4.3 Prédictions chiffrées et signées (ouvertes dans les deux sens)

Écrites après les lectures préalables L0 à L4 (section 10), qui n'utilisent ni modèle ni vrai expérimentateur ; elles ne
décident pas des issues, qui suivent les critères des sections 4.6 et 4.7.

- **P1 (signe +, loi plantée)** : T-VRAIE « survit » dans **8 passes sur 8** (L1 : promue et statistique ≥ 0,02 dans 200
  graines sur 200). Ouverte : ≤ 6 sur 8 dirait que le vrai expérimentateur (ou le gardien modèle) perd une loi que le juge
  promeut toujours.
- **P2 (signe −, fausses)** : **0** témoin faux promu puis survivant sur 32 passes (T-F1, T-F2, T-F4, T-ANTI × 8) ; T-F2
  promu par le juge dans 0 à 4 passes (L1 : 83 sur 200 seul ; e-BH à m = 19 l'abaisse), éliminé au test de mort dans
  toutes (L1 : la statistique de T-F2 n'atteint 0,02 que dans 3 graines sur 200) ; T-ELIM « éliminée » dans toutes ses passes
  testées. Ouverte : un témoin faux retenu dirait que le test de mort ne rattrape pas une fausse promotion.
- **P3 (inconclusif)** : part de « non concluant » parmi les cartes et témoins testés **≤ 0,10** dans chaque bras (le seuil
  gelé est 0,20, section 4.6). Ouverte : au-dessus de 0,20, l'instrument ne conclut pas.
- **P4 (bras aléatoire, sous D7 « archive du bras réel »)** : génération 1 (archive vide dans tous les cas) : PS **entre 1 et 4 cartes sur 12** (L2b : 35/288 = 0,122 par carte ; probabilité ≈ 0,78 ; 0 sur 12 a une probabilité ≈ 0,21). Générations 2 et 3, jugées contre l'archive du bras réel : ≈ 0 si elle porte une loi voisine de L* (L2b-v61, une répétition : 0 sur 24), ≈ 0,12 par carte si elle reste vide. Trois générations : **entre 1 et 6 cartes sur 36** si l'archive réelle est informative dès la génération 1 ; **entre 1 et 8** si elle reste vide (binomiale (36 ; 0,122) : P(≤ 8) ≈ 0,97, P(≥ 7) ≈ 0,14) ; L2b (archive propre, 0,056) n'est une borne haute que dans le premier cas. FD du bras aléatoire **≤ 1 carte sur 36** (L2 : 3 sur 1 200 = 0,0025). Ouverte : une part hors de la bande de son cas dirait que le juge ou le test de mort ne se comporte pas comme sur L2 et L2b ; rapportée, auditée (S2), non décisive. Cas lu par la lecture v62 sur la taille de l'archive de jugement du bras aléatoire en génération 2 : non vide → « informative » (1 à 6) ; vide, qu'elle le reste ou non en génération 3 → bande 1 à 8, borne haute.
- **P5 (bras recopie-mélange)** : **0 FD** (L2 : 0 promue sur 300 face à une archive informative ; validation du nul v8 :
  0 sur 1 000 pour T02, T03b, T04, T05s, T17s). Ouverte : une FD, possible au niveau α par carte, est rapportée et auditée.
- **P6 (signe +, bras réel)** : part PS du bras réel **≥ 0,30 en génération 1** (au moins 4 cartes sur 12) et part VD ≥ 0,25 en génération 1 ; sur trois générations, rapportée sans seuil (un bras qui trouve la loi en génération 1 sature son archive : L2b, 0/96 ensuite), donc au-dessus du bras
  aléatoire (Newcombe, borne basse > 0 attendue). Ouverte dans l'autre sens : PS réel ≤ 0,15 dirait que les vrais proposeurs,
  avec 200 épisodes de développement, ne font pas mieux que le hasard dans ce monde. Aucune lecture préalable ne porte sur ce
  bras (aucun modèle appelé) : prédiction de rédacteur.
- **P7 (loi plantée retrouvée par les proposeurs)** : **aucune VD*** (D ≤ 0,05 nat) en génération 1 ; la plus petite
  divergence D parmi les VD du bras réel **décroît** de la génération 1 à la génération 3 (mesurée, sans seuil). Ouverte : une
  VD* dès la génération 1 dirait que 200 épisodes suffisent à un modèle de langage pour ajuster la loi à 0,05 nat près.
- **P8 (gardien)** : part de cartes refusées par le gardien mécanique ≤ 0,10 dans chaque bras ; écart entre bras ≤ 0,15. Ouverte : au-dessus, le gabarit fermé est mal compris par un proposeur (refus mesurés, motifs lus, S5).

### 4.4 Métriques et taille

- Par bras b : N_b cartes jugées (passées au gardien) ; PS_b, VD_b, FD_b, cartes testées, « non concluant » ; parts
  r_b = PS_b / N_b, vd_b = VD_b / N_b, fd_b = FD_b / N_b ; **intervalle de Wilson (score) bilatéral à 95 %** pour chacune ;
  **intervalle de Newcombe** (méthode 10, hybride de Wilson) pour r_réel − r_aléatoire et vd_réel − vd_aléatoire.
- Diagnostic de la chaîne (oracle, tous bras réunis) : sensibilité P(PS | carte informative et nouvelle, G ≥ g₀ et ΔG ≥ g₀) et
  part P(PS | carte non informative) ; Wilson.
- Témoins : passes et verdicts par témoin (8 passes de chacun : 3 réel, 3 aléatoire, 2 recopie-mélange ; 6 si le bras
  recopie-mélange ne joue pas).
- **Taille** : bras réel ≤ 36 cartes, bras aléatoire 36, bras recopie-mélange ≤ 24, témoins 56 passes. Ce qu'elle tranche
  (Wilson 95 %) : 0/36 → [0 ; 0,096] ; 2/36 → [0,015 ; 0,181] ; 4/36 → [0,044 ; 0,253] ; 14/36 → [0,248 ; 0,551] ;
  T-VRAIE 8/8 → [0,676 ; 1]. Écart réel − aléatoire : avec 4/36 au bras aléatoire, la borne basse de Newcombe dépasse 0 dès
  **11/36** au bras réel (0,31) ; à 9/36 elle vaut −0,042. **Un écart inférieur à environ 0,2 n'est pas décidable** à cette
  taille ; un taux de fausses découvertes de la chaîne au-dessus d'environ 0,10 par carte serait visible (borne haute de
  Wilson de 0/36 = 0,096). Doubler le bras aléatoire (une seconde réplique de 36 cartes, ≈ 2,5 USD) resserrerait la référence :
  option laissée à Lazar (D6).

### 4.5 Ce qui est mesuré sans critère

Trajectoire de la meilleure D et du meilleur G du bras réel par génération ; refus du gardien par bras et motifs ; log W
maximal et membre dominant du nul par carte ; sessions, exécutions et coût par carte testée ; désaccords du vérificateur
avec le noyau.

### 4.6 Critère gelé « l'étage 1 tient » (porte vers l'étage 2)

Calculé par `pole/lecture_tour_ferme_v61.lire_etage1` (C1, C2 appliqués ; la v60 reste, inchangée) sur le relevé scellé, dans cet ordre ;
**tous** doivent tenir :

1. **T1 — boucle** : aucune `SelectionNonVerifiee`, `HeritageRefuse` ni `VueAvecVerdict` ; chaque génération g ≥ 2 de chaque bras qui joue a lu le bilan
   de g−1 à l'empreinte consignée (journal ; une lecture vérifiée par génération g ≥ 2 de chaque bras, qu'il joue ou non : le bras recopie-mélange lit le bilan du bras réel même quand l'archive vide l'empêche de jouer ; attendu = lu ; lecture v62) ; aucun arrêt de la liste d'arrêt.
2. **T2 — loi plantée** : T-VRAIE « survit » dans **toutes ses passes sauf au plus une** (une passe par génération jouée de chaque bras, nombre compté sur le journal : 8 si le bras recopie-mélange joue en
   générations 2 et 3, 7 s'il ne joue qu'en génération 3, 6 s'il ne joue pas), « éliminée » dans aucune.
3. **T3 — fausses** : au plus **1** passe de témoin faux promue puis survivante sur 32 (24 si le bras recopie-mélange ne joue
   pas) ; T-ELIM testé et « éliminée » dans toutes ses passes sauf au plus une, jamais « survit » ; T-MAL présent et refusé au gardien dans chaque génération jouée de chaque bras.
4. **T4 — inconclusif** : « non concluant » / testées ≤ **0,20** sur les trois bras réunis et ≤ 0,40 dans chaque bras (cartes et témoins) ;
   chaque carte testée porte un contre-calcul (absent : relevé invalide, issue N) ; aucun désaccord du contre-calcul (un désaccord arrête la course, garde 10 : relevé partiel scellé, sans les cartes de la génération arrêtée ; T1 manqué par l'arrêt).
5. **T5 — fausses découvertes** : FD du bras aléatoire ≤ **1** (sur 36 cartes ; L2 attend 0,0025 par carte) ; FD du bras
   recopie-mélange ≤ **1** (ou bras « non mesurable »).

Un critère manqué : **l'étage 2 n'est pas joué** ; l'issue est « étage 1 ne tient pas (Tk) », publiée telle quelle avec ses
chiffres, et A3 est « non jugée ». Aucune reprise du même texte scellé après lecture : toute réparation est une version
nouvelle avec un préenregistrement nouveau.

### 4.7 Lecture A4 gelée et issues écrites d'avance

1. **Taux de fausses découvertes de la chaîne** : fd_aléatoire et fd_recopie avec Wilson ; c'est le taux par carte proposée
   auquel la chaîne transforme une proposition sans information, ou une redite de l'archive, en découverte retenue.
2. **Lecture de Lazar, gelée telle quelle** : r_réel, r_aléatoire, r_recopie (part de cartes promues puis survivantes) avec
   Wilson ; **si la borne basse de Newcombe de r_réel − r_aléatoire est ≤ 0 (« le bras aléatoire promeut autant que le bras
   réel »), la chaîne ne distingue pas les vrais proposeurs du hasard dans ce monde : réserve majeure pour A3**, écrite dans
   la phrase au mentor (section 5.6).
3. **Ce qui départage, écrit d'avance** : l'oracle sépare les causes d'un écart non positif, par la part de cartes informatives et nouvelles à l'oracle (G ≥ g₀ et ΔG ≥ g₀, mesurée sur toutes les cartes jugées, promues ou non) : si sa borne basse de Newcombe réel − aléatoire est > 0, les proposeurs produisent de l'information que la chaîne ne retient pas (« sensibilité de la chaîne insuffisante ») ; sinon « on ne peut pas dire, à cette taille, que les vrais proposeurs battent le hasard dans ce monde ». Puissance dite : à 36 contre 36, un écart vrai de 0,10 sur r est déclaré « discrimine » avec une probabilité d'environ 0,2, un écart de 0,20 avec environ 0,6. Si T5 tient (la chaîne ne
   transforme presque aucune loi sans information ni aucune redite en découverte), un écart nul dit que **les vrais proposeurs
   ne font pas mieux que le hasard dans ce monde** (où 13 % des lois aléatoires sont informatives) ; si T5 manque, c'est **la
   chaîne qui ne discrimine pas**, et l'étage 2 n'est pas joué. Sensibilité de la chaîne rapportée, sans seuil.
4. **Issues (exhaustives)** : T5 manque → « la chaîne ne discrimine pas » (étage 2 non joué) ; T5 tient et borne basse de
   Newcombe de r_réel − r_aléatoire > 0 → « discrimine » ; T5 tient et borne ≤ 0 → « le bras aléatoire promeut autant que le
   bras réel à cette taille : la chaîne ne distingue pas les vrais proposeurs du hasard dans ce monde » (phrase de Lazar ; réserve majeure pour A3, point 2), suivie de la cause lue au point 3 ; la comparaison de la seule génération 1 est rapportée à côté, sans décider. Le bras
   recopie-mélange sans aucune carte en générations 2 et 3 → « recopie non mesurable », dit à côté de l'issue. Bras réel sans aucune carte jugée → issue A4 « non mesurable (aucune carte réelle jugée) », jamais « promeut autant » (lecture v62).

### 4.8 Phrases préparées pour le mentor, étage 1 seul (anglais ; chiffres de la sortie scellée, sans autre changement)

- **N1** (« ne tient pas », critère) : « The closed loop did not pass its own planted-world gate ([criterion]); we did not run it on the real question. »
- **N1, arrêt** (T1 manqué par un arrêt de la liste d'arrêt ; champ `n1 = arret` de la lecture v62) : « The planted-world run was stopped before its end ([stop: budget / duration / recomputation disagreement / session failure]); we did not run the loop on the real question. »
- **Tient, « discrimine »** : « We ran our automated research loop closed, for real, on a planted-law world: two proposer models (Kimi, Gemini Argon) that never see a verdict, a form gatekeeper, a frozen statistical judge, death tests executed in a network-less sandbox, a verifier from another model family, and a sealed selection read by the next generation. The chain kept the planted law in [k] of [n] passes, and promoted and kept [r_real] (Wilson 95 % [a, b]) of the models' proposals against [r_random] of random proposals ([x] of which carried no new information by an oracle that knows the planted law); the difference is above zero at 95 % (Newcombe [c, d]). This is one planted world, three generations, 36 proposals per arm. »
- **Tient, autre issue A4** : la même phrase, la dernière proposition remplacée par l'issue A4 gelée (section 4.7) : « at this size we could not show that the models' proposals do better than random ones ([cause]) » ou « not measurable: no proposal from the models was judged ».

En français, pour le dossier : N1 — « la boucle n'a pas passé sa propre porte sur monde planté » ; tient — « la chaîne fermée a tourné pour de vrai sur un monde planté et a gardé la loi plantée ; [issue A4] ».

<!-- etage-2-hors-scellement : début -->

**Étage 2 — hors de ce scellement, texte de l'étage 2 à sceller plus tard, avant toute lecture de T.**

## 5. Étage 2 — la vraie question (A3), joué seulement si l'étage 1 tient

### 5.1 Question et monde

- **Question** : celle du second tour réel du 1er novembre (Kimi et Argon, 62 appels, 1,47 USD ; préenregistrement sha256
  `6fcb1035aa46be34caba9b381b1f9bf0a054fc6d3e9b4430b18e680c101c7481`, **introuvable dans les arbres lus** — README, section 4,
  et message n° 334 de conv-audit). Le texte servi et son empreinte sont **à nommer par la session-depot avant scellement**
  (case Q ci-dessous). Candidats trouvés, sans preuve qu'ils soient le texte servi le 1er novembre : le texte I de la course 2
  (`question-course-2-defense-fusion-v5.md`, sha256 `a7501449…`, en-tête « brouillon, non servi ») et la question du
  collisionneur de la course 2 (`docs/notes/ideation-organisme-v1/course-2/question-course-2-v1.md`).
- **Forme testable** : le juge statistique ne juge que des lois prédictives sur un monde d'épisodes. L'étage 2 sert la question
  comme contexte et demande des **lois du score d'un des 13 moniteurs réels en fonction des traits de l'épisode** (4 traits :
  `log_jetons_total`, `actions_valides`, `jetons_par_action_ecart_type`, `bruit` ; 2 sous-populations ; 2 ou 3 issues selon le
  moniteur) — la forme des lectures sur banque déjà faites (README, section 4). Portée dite : **la vraie question, restreinte
  à ce que la banque T0.5 peut trancher.** La traduction des fiches d'idées du 1er novembre par le pont
  (`pont-fiche-loi-v1/`) est une autre voie, hors de ce texte.
- **Monde de l'étage 2** (construit par la session-depot, scellé avant la course) : épisodes publics de `exemples/banque-t05-v2.json`
  (120 épisodes, 60 tâches, sha256 `f26cc857…`) et 288 épisodes à graines neuves du 2 novembre (96 tâches × 3, privés, ceux
  de la lecture `preenregistrement-lecture-t05-graines-neuves-v2.md`, sha256 `93923d71…`), **moins toutes les tâches réservées**
  (section 5.2). Parties, par tâche entière : calibrage (partie « calibrage » de la banque publique : prédicteur connu de
  chaque moniteur), développement (servi aux proposeurs, traits et issues) et épreuve (paris du juge), réparties par la
  graine de la tâche « etage=2|partition » (un tiers développement, deux tiers épreuve, parmi les tâches non réservées hors
  calibrage).

### 5.2 Données tenues à l'écart (réserve par empreinte, avant la course)

**Ce qui existe** : aucune donnée réelle neuve n'a été produite pour ce tour ; les seules données réelles du pôle sont la banque
T0.5 (publique, 120 épisodes) et les 288 épisodes à graines neuves (privés, lus **une fois** par le juge dans la lecture du
2 novembre, pour les lois des 13 moniteurs, jamais par un proposeur). **Plus petite réserve honnête proposée** :

- **Règle (fixée ici, indépendante de la graine scellée et de toute issue)** : une tâche t est réservée si et seulement si
  `int(sha256("tour-ferme-v1|tenue-a-l-ecart|" + t).hexdigest(), 16) % 3 == 0` (environ un tiers des tâches). Les **données
  tenues à l'écart T** = tous les épisodes **privés à graines neuves** des tâches réservées (attendu ≈ 96 épisodes, ≈ 32
  tâches) ; les épisodes **publics** des tâches réservées sont retirés de tout (ni monde du juge, ni T), pour que T ne
  contienne que des épisodes jamais publiés ni servis et qu'aucune tâche de T n'apparaisse dans ce que voient les
  proposeurs ou le juge.
- **Exécution** : par la session-depot (qui garde `donnees/`), avec le module public `pole/reserve_tenue_a_l_ecart_v60.py`
  (écrit avec ce brouillon ; commande en section 9), **avant scellement** ; elle rend au rédacteur les seules empreintes et les seuls comptes (aucun contenu), qui
  sont recopiés ici ; T est scellé, gardé chez elle, et n'est monté que dans la tranche du bac à sable de l'étage des tests de
  mort de l'étage 2.

| case (à remplir avant scellement par la session-depot) | valeur |
|---|---|
| Q — texte de la question servie à l'étage 2 : le texte du 1er novembre reste introuvable ; **défaut** (contre-lecture, B2) : la question du collisionneur de la course 2, nommée comme telle (`docs/notes/ideation-organisme-v1/course-2/question-course-2-v1.md`), sans prétendre être le texte du 1er novembre ; sha256 : <<CASE_Q>> |
| E0 — fichier des 288 épisodes à graines neuves (entrée de la réserve), sha256 | <<CASE_E0>> (session-depot) |
| R — liste triée des tâches réservées, sha256 ; nombre de tâches | <<CASE_R>> (session-depot ; sur les 60 tâches publiques : 16 réservées, L4) |
| T — fichier des données tenues à l'écart, sha256 ; épisodes ; épisodes par moniteur | <<CASE_T>> (session-depot) |
| M2 — monde de l'étage 2 (sans les tâches réservées), sha256 ; épisodes par partie | <<CASE_M2>> (session-depot ; vérifié par `verifier_disjonction`) |
| V — sha256 du module de réserve exécuté et de son manifeste | module v60 `2399d5eca73e5a5f832c72a0b62c0c9110ae238ea2b48a31cab318a00e43edc0`, v61 `b99fe5a58d6348e80e9ff0b3184a69b4602951d8c8e439a59c240e3ef5883ff9` ; manifeste : <<CASE_V>> (session-depot ; recopié dans `reserve_manifeste_sha256` du plan gelé) |

- **Essai de la règle sur les seuls identifiants de tâches publics** (lecture L4, aucune issue lue) : sur les 60 tâches de
  `banque-t05-v2.json`, 16 sont réservées (32 épisodes publics, retirés de tout), 44 restent (88 épisodes). Sur les 96 tâches
  à graines neuves, environ 32 sont attendues (≈ 96 épisodes dans T) ; le compte exact est celui de la case R.
- **Jamais vues** : T n'entre ni dans le contexte d'un proposeur, ni dans le monde du juge, ni dans une vue ; le lanceur
  vérifie l'empreinte de T avant de le monter et cherche, dans chaque contexte servi et dans M2, chaque tâche réservée sous sa forme normalisée (sans suffixe de version), chaque identifiant d'épisode de T et chaque vecteur de traits de T arrondi à 4 décimales (garde 11, section 7 ; `pole/reserve_tenue_a_l_ecart_v61.py`) ; la session-depot vérifie que les tâches communes à E0 et à la banque publique y sont écrites à l'identique (refus sinon). T est lu, dans le bac, par l'expérimentateur (Kimi) et le vérificateur (Argon) de l'étage 2 : c'est la seule lecture de T par un modèle.
- **Une lecture par génération décisive** : T sert aux tests de mort des **deux** générations de l'étage 2 ; seule la
  **génération 1** est décisive pour A3 (T n'y a influencé aucune proposition). En génération 2, la vue des proposeurs porte les
  lois retenues sur T en génération 1 (un bit par carte testée) : ses survivantes sont rapportées comme « survivantes sur T
  relue », exploratoires (décision D5 ; l'alternative, T coupé en deux moitiés par tâche, une par génération, coûte la moitié
  des épisodes à chaque test de mort).

### 5.3 Plan de l'étage 2

Même chaîne que l'étage 1, avec : deux générations ; bras réel (Kimi, Argon, 6 cartes chacun, gabarit fermé `{enonce, moniteur,
loi_predictive}`, le test de mort complété par l'orchestrateur) ; **bras aléatoire de contrôle** (12 lois par génération tirées
dans la grammaire du monde de l'étage 2, moniteur tiré au hasard ; décision D6) ; pas de bras recopie-mélange. Témoins
d'instrument seulement (aucune vérité connue sur des données réelles) : T2-CONNU (le prédicteur connu d'un moniteur, membre du
nul : ne doit jamais être promu) et T2-MAL (carte sans bloc : refusée au gardien). Juge : configuration du juge de production à
plan pleine épreuve (`juge_plan_plein_v1` : nul v8, monde informé avec le membre « connu:<moniteur> », e-BH, α = 0,05, plan =
tout le réservoir d'épreuve du moniteur de la carte) **étendue aux membres d'archive du bras** pour la génération 2 (la garde
`verifier_archive_vide` de la v1 l'interdit : variante `_v60` à écrire). m fixé à 14 (12 cartes + 2 témoins). Test de mort :
gain moyen du log-score de la loi sur le prédicteur connu du moniteur (membre « connu:<moniteur> », ajusté sur la seule partie calibrage, gelé avant la course ; décision D8, <<DECISION_D8>> ; le gain sur la marginale empirique de T, comptes + 0,5, est rapporté à côté), calculé sur les épisodes de T qui portent une
issue pour le moniteur de la carte ; seuil « au moins 0,02 » ; fichier brut `gains.csv`.

### 5.4 Hypothèse et prédictions (étage 2)

- **H-A3** : au moins une loi proposée par le bras réel en génération 1 est promue par le juge puis survit à son test de mort
  exécuté sur T.
- **P9 (signe : zéro, ouverte dans les deux sens)** : l'issue la plus probable est **Z, aucune promotion survivante**
  (probabilité de rédacteur ≈ 0,75) : la lecture à graines neuves borne les lois de moniteur de la forme plantée sous
  0,057 à 0,117 nat par épisode (puissance 0,9) et n'en a promu aucune ; le juge sur cette banque est faible sous 0,06 nat.
  Ouverte : une promotion survivante viendrait d'un lien d'une autre forme (si_sinon, par_sous_population) au-dessus de cette
  borne.
- **P10 (contrôle)** : le bras aléatoire de l'étage 2 n'a **aucune** carte promue puis survivante (le membre « connu » du nul
  absorbe le signal linéaire). Ouverte : une PS aléatoire dirait que la chaîne laisse passer le hasard sur cette banque.

### 5.5 Puissance (calcul approché, marqué SUPPOSÉ là où il l'est)

- Juge : courbe de puissance sur cette banque (README, section 4) : force 0,5 (≈ 0,06 nat par épisode) promue 65 à 73 % entre
  120 et 180 épisodes d'épreuve avec le plan gelé, 0,9 vers 233 épisodes avec le plan plein ; ici ≈ 180 épisodes d'épreuve
  au total, moins par moniteur (SUPPOSÉ : 75 à 150).
- Test de mort sur T (≈ 40 à 85 épisodes par moniteur ; écart-type du gain par épisode SUPPOSÉ 0,5 nat) : une loi qui porte
  0,06 nat survit avec une probabilité ≈ 0,69 à 0,77 ; 0,12 nat ≈ 0,90 à 0,97 ; une loi sans information (gain ≈ −0,03)
  ≈ 0,18 à 0,26 (approximation normale de la moyenne, n = 40 à 85, épisodes SUPPOSÉS indépendants ; ils ne le sont pas, 3 par tâche : à corrélation ρ entre épisodes d'une même tâche, n effectif ≈ n / (1 + 2ρ), et la survie d'une loi sans information monte).
- Conjointe (juge SUPPOSÉ à 0,4 à 0,7 pour 0,06 nat et ≥ 0,9 pour 0,12 nat à ces tailles) : une loi réelle de 0,06 nat a
  ≈ 0,3 à 0,55 de passer les deux ; de 0,12 nat, ≈ 0,8 ou plus. **Zéro promotion ne dira donc
  rien des liens sous ≈ 0,06 à 0,12 nat par épisode**, ce que la phrase au mentor dit.

### 5.6 Issues écrites d'avance et phrase pour le mentor

Calculées par `pole/lecture_tour_ferme_v61.lire_etage2`, dans cet ordre :

1. **N — non jugée** : étage 1 ne tient pas (section 4.6) ; ou arrêt de la liste d'arrêt à l'étage 2 ; ou « non concluant »
   > 0,20 des cartes testées de l'étage 2 ; ou contre-calcul en désaccord.
2. **P — promotion** : au moins une carte du bras réel de **génération 1** promue (e-BH) **et** « survit » au noyau sur T, contre-
   calcul concordant. Rapporté par carte : moniteur, forme de la loi, log e, statistique sur T, empreintes ; plus les
   survivantes de génération 2 « sur T relue » (exploratoires). Réserves automatiques : (a) celle de A4 si l'issue A4 n'est
   pas « discrimine » ; (b) « le hasard passe aussi » si le bras aléatoire de l'étage 2 a une carte promue puis survivante.
3. **Z — zéro** : aucune carte du cas P. Rapporté tel quel, avec la borne de la section 5.5.

Phrases préparées pour Jan Kirchner (anglais), à compléter par les chiffres de la sortie scellée, sans autre changement :

- **P** : « We ran our automated research loop closed, for real: two proposer models (Kimi, Gemini Argon) that never see a
  verdict, a form gatekeeper, a frozen statistical judge, death tests executed in a network-less sandbox, a verifier from
  another model family, and a sealed selection read by the next generation. On our real question, restricted to laws of monitor scores that our episode bank can test, [n] hypothesis(es) written
  by the models was promoted by the judge and then survived a preregistered death test run on held-out episodes reserved by
  hash before the run (fresh-seed episodes of the same tasks, never shown to a proposer or to this run's judge; read once before by our judge for other laws). On a planted-law world the same chain [kept / lost] the planted law and promoted and kept [r] (Wilson 95 % [a, b])
  of random proposals, [x] of which carried no new information by an oracle that knows the planted law; copy-and-mix proposals, restricted to forms our judge's null covers by construction, gave [y]. This is a first hypothesis out of a
  verdict-blind pipeline, not a validated finding: it holds on fresh episodes of the same tasks, and needs new tasks. »
  [+ réserve (a) : « Caveat: on the planted world, we could not show, at 36 proposals per arm, that our proposers produce more surviving
  discoveries than a random proposer ([cause]), so this promotion cannot yet be credited to their judgement. »] [+ réserve (b) : « Caveat: a random proposer also
  got through on the real bank. »]
- **Z** : « We ran the loop closed, for real, on our real question: it promoted nothing that survived the held-out death test,
  and we report that zero as preregistered. On a planted-law world the same chain [kept the planted law] and promoted and kept [r] of
  random proposals, [x] of them without new information by the oracle; on our real episode bank, links weaker than about 0.06 to 0.12 nat per episode
  would pass unseen. The pipeline now runs end to end; at this data size, the real question did not yield a hypothesis it
  could confirm. »
- **N** : N1 (étage 1) : « The closed loop did not pass its own planted-world gate ([criterion]); we did not run it on the real question. » N2 (étage 2) : « We ran the closed loop on the real question, but the run is not judgeable ([stop / inconclusive share above 0.20 / recomputation disagreement]); we report no outcome for the real question. »

En français, pour le dossier : P — « une hypothèse écrite par les modèles, promue par le juge figé, a survécu à un test de mort
exécuté sur des épisodes tenus à l'écart » ; Z — « la boucle fermée a tourné pour de vrai sur la vraie question et n'a rien
promu qui survive ; zéro est le résultat » ; N — « la boucle n'a pas passé sa propre porte sur monde planté ».

<!-- etage-2-hors-scellement : fin -->

## 6. Audit de symétrie (règle R4), écrit d'avance

Un résultat trop propre, dans un sens ou dans l'autre, déclenche le même audit **avant** toute lecture d'issue. Le point (3) de S1 (poids de L* et lignes de tranche dans les contextes servis) est fait à chaque course, déclenchée ou non, par le code gelé (champ `recherche_loi_plantee` du relevé, calculé ; absent ou `null` : relevé invalide ; v62). S1 ou S3 déclenché sans défaut trouvé : l'issue porte la réserve « trop beau, audité sans défaut » (R4).

- **S1 — trop beau (étage 1)** : aucune FD dans aucun bras **et** aucun « non concluant » **et** T-VRAIE « survit » 8 fois sur
  8 **et** une VD* du bras réel dès la génération 1. Audit : (1) contre-calcul hors bac de chaque statistique testée depuis la
  loi gelée et la tranche scellée ; (2) lecture de chaque script d'expérimentateur : le fichier brut est-il calculé depuis
  `episodes.csv`, ou fabriqué ? (3) recherche, dans chaque contexte servi aux proposeurs, des poids de L* (exacts et arrondis à
  deux décimales) et de toute ligne de tranche ; (4) vérification que les témoins ont été jugés sans membres d'archive et
  exclus de l'archive ; (5) oracle rejoué sur un cas connu (G(L*) = 0,523). Un défaut trouvé : course invalide, aucune issue.
- **S2 — trop laid (étage 1)** : T-VRAIE « éliminée » ou « non concluant » dans au moins 2 passes, ou fd_aléatoire > 0,05, ou
  une FD du bras recopie-mélange. Audit : les cinq points de S1, puis : rejouer chaque carte en cause avec l'exécuteur factice (même tranche, mêmes graines)
  et comparer les verdicts du noyau ; vérifier les membres ajustés du nul (`nul_v8.exiger_membres_ajustes`) ; relire les
  sessions de l'expérimentateur ; puis lecture des critères, sans les changer.
<!-- etage-2-hors-scellement : début -->

**Étage 2 — hors de ce scellement, texte de l'étage 2 à sceller plus tard, avant toute lecture de T.**

- **S3 — trop beau (étage 2)** : une carte P avec log e > 20, ou une statistique sur T > 0,3 nat (bien au-dessus de la borne
  de 0,06 à 0,12 nat de la lecture à graines neuves). Audit : empreinte de T au montage ; recherche des tâches réservées dans les
  contextes servis ; la loi encode-t-elle l'identité d'une tâche (trait `bruit`, valeurs exactes) ? contre-calcul.
- **S4 — décevant (étage 2)** : issue Z ou N. Même profondeur d'audit que S3 : plans du juge de la taille prévue, cartes
  valides, refus du gardien par bras, témoins d'instrument conformes, borne de puissance recalculée.
<!-- etage-2-hors-scellement : fin -->

- **S5 — asymétrie du gardien et de l'expérimentateur** : part de refus du gardien mécanique, ou part de « non concluant », d'un bras supérieure de plus de 0,15 à la même part d'un autre bras : motifs
  lus avant lecture des parts (un gardien qui refuse les cartes réelles et non les scriptées fausserait A4).

## 7. Liste d'arrêt (chaque garde essayée sur un cas sain et sur un artefact, règle R5)

| # | garde | cas sain | artefact | essai |
|---|---|---|---|---|
| 1 | lecture vérifiée de l'héritage | bilan, sélection, cartes, verdicts aux empreintes consignées | sélection réécrite avec sceau juste ; bilan d'une autre empreinte ; lien symbolique ; retenue non survivante → `SelectionNonVerifiee` / `HeritageRefuse` | existe : `essais/test_v59_boucle_fermee.py` |
| 2 | vue sans verdict | lois seules | clé `log_richesse_max`, `promue`, `comptes` à toute profondeur → `VueAvecVerdict` | existe (v59) |
| 3 | vrai bac à sable, aucun repli | `bwrap` présent, sonde réussie | `bwrap` absent ; superutilisateur sans identité dédiée → `BacASableIndisponible` | existe (v59) |
| 4 | graines dérivées de la tâche (R9) | deux tâches → deux graines | `spawn_key=()` → graines égales (mutation tuée) | existe (v59) |
| 5 | plafond de dépense par étage, vérifié après chaque appel de proposeur et chaque étage de tests de mort ; plafond dur tenu par les relais (registre cumulé ; part de chaque relais fixée au plan, v62) | appels à 0,01 USD : étage complet | plafond franchi → arrêt, code 3, sortie scellée, aucune issue lue ; plafond d'un relais atteint (« budget_depasse » hors plafond de la fiche) → arrêt, jamais « non concluant » | `essais/test_v61_tour_ferme.py` (`Garde5Et13` ; lanceur, code 3) ; parts des relais : `PartsDesRelais` et `Arrets` (v62 : part franchie, pire cas avant l'étage, « budget_depasse » d'un relais hors du plafond de la fiche → arrêt, code 3), mutations tuées |
| 6 | préenregistrement scellé exigé | fichier scellé, bloc de code gelé conforme | nom avec « brouillon », sceau absent ou faux, marqueur restant, empreinte de code différente, entropie < 2⁶⁴ → code 2, rien écrit | `Garde6` (v61) : plan sain et artefacts ; nom « brouillon », hors de `prereg/`, absent ; v62 : `Garde6Complete` (cas sain complet accepté ; sceau faux, marqueur hors de l'étage 2, empreinte de code, zone ouverte, nom « brouillon », hors du dossier, entropie < 2⁶⁴ refusés), mutations tuées |
| 7 | témoins jamais retenus ni servis | témoin promu et survivant : absent de la sélection, de l'archive, de la vue | témoin introduit dans l'archive → refus | `Garde7` (v61), mutation tuée |
| 8 | gabarit du test de mort imposé | carte du proposeur complétée par l'orchestrateur | carte d'un proposeur qui porte son propre seuil, sa propre statistique ou ses propres données → refusée au gardien mécanique | `Garde8` et lanceur `--scenario-proposeur hors_gabarit` (v61), mutation tuée |
| 9 | familles séparées | expérimentateur Kimi, vérificateur Argon | même famille → refus avant toute session | `Garde9` et lanceur `--familles-a-blanc a,a`, code 2 (v61), mutation tuée |
| 10 | contre-calcul de la statistique | gain recalculé par l'orchestrateur depuis la loi gelée et la tranche = statistique du noyau à 10⁻⁶ près | script qui écrit des gains fabriqués → **arrêt de la course**, code 3, relevé partiel scellé, audit S1 | `Garde10` (unité, v61), mutation tuée ; arrêt de bout en bout : `Arrets` (v62 : gains arrondis à 2 décimales et gains fabriqués → code 3, relevé partiel scellé), mutation tuée |
| 11 | **étage 2 : hors de ce scellement** — données tenues à l'écart jamais servies | empreinte de T conforme au montage ; aucun identifiant de tâche réservée dans les contextes | T altéré, rescellé ; tâche réservée déplacée au reste ; liste des tâches incohérente ; tâche réservée dans un contexte → refus | **écrite pour la réserve** (`verifier_reserve`, `taches_reservees_dans` ; `essais/test_v60_reserve_tenue_a_l_ecart.py`, 15 essais ; `essais/mutations_v60.py`, 8 mutations de la réserve tuées sur 8) ; appel au montage et balayage des contextes par le lanceur **à écrire** |
| 12 | porte entre étages | lecture scellée de l'étage 1 « tient » | étage 2 lancé sans elle, ou avec « ne tient pas » → code 2 | `Garde12` (v61) ; **sous ce texte (étage 1 seul)** : `--etage 2` → code 2 avant tout appel (`RefusAvantToutAppel`, v62) ; la porte relèvera du préenregistrement de l'étage 2 |
| 13 | modèle servi inconnu, session en échec, durée | modèle attendu | autre modèle servi (refus R-764) ou session en échec, chez un proposeur comme à l'étage → arrêt, code 3, sortie scellée ; durée > plafond (4 h étage 1, 2 h étage 2), vérifiée entre deux appels (un étage en cours n'est pas interrompu) → arrêt, code 3 | durée : `Garde5Et13` (horloge factice, v61) ; modèle servi et session en échec sur le chemin du tour : `ProposeurChemin` et `Arrets` (v62 : refus R-764 d'un proposeur, session en échec à l'étage → code 3, relevé partiel scellé), mutations tuées |
| 14 | lecture gelée | relevé sain **produit par le cœur** → « tient », « discrimine », P | chaque critère T1 à T5 manqué → « ne tient pas » ; survivante de génération 2 seule → Z ; contre-calcul absent → N ; étage 1 manqué → N1 | `essais/test_v61_lecture_tour_ferme.py` (14 essais), 6 mutations tuées ; relevés produits par le cœur (bras réel muet en génération 1, puis en générations 1 et 2) : `CourseMuette` (v62, « tient ») ; lecture v62 : `LectureV62`, mutations tuées |
| 15 | machine jetable (R-640, CL20-14) | `POLE_MACHINE_JETABLE_V56=1` déclaré, environnement dans la liste blanche | variable absente ou variable hors liste → code 2, avant tout appel | `MachineJetable` (v62 : environnement du processus et liste permise de la configuration, refus avant tout appel ; la v61 passait à l'étage un environnement constant, `ENV_A_BLANC`, aussi en mode réel), mutation tuée |

Essais v62 de l'étage 1 : `essais/test_tour_ferme_v62.py` (gardes 5 à 10, 12 à 15 et corrections C8 à C21, cas sain et artefact) ; banc `essais/mutations_tour_ferme_v62.py` (une mutation au moins par correction).

Arrêt = sortie scellée telle quelle, code 3, aucune issue lue ; toute exception après le manifeste est un arrêt (v62, C12) ; reprise seulement dans un dossier neuf, avec le même fichier
scellé, si l'arrêt vient d'une panne d'infrastructure consignée (règle de la section 8 du préenregistrement du nul v8).

## 8. Graines (règle R9)

Entropie racine **E = int(sha256 du fichier scellé, 16)** (entier gros-boutiste de l'empreinte des octets ; E ≥ 2⁶⁴ exigé en mode
réel, E < 2⁶⁴ exigé à blanc : espaces disjoints). Toute graine est `boucle_fermee_v59.graine_de_tache(E, tâche)` =
`numpy.random.SeedSequence(E, spawn_key=(cle_de_tache(tâche),))`, avec les tâches nommées
`tour-ferme-v61|etage=<e>|bras=<b>|generation=<g>` (préfixe = `VERSION` du cœur gelé ; `tour-ferme-v62|…` avec un cœur v62) suivies de `|carte=<id>|plan`, `|noyau`, `|frais|<empreinte de
l'engagement>`, `|tranche`, `|developpement`, `|proposeur=aleatoire`, `|proposeur=recopie_melange`, `|temoin=<id>` ; oracle :
`oracle|instances` ; partition du monde de l'étage 2 : `tour-ferme-v1|etage=2|partition`. La réserve de T ne dépend pas de E
(section 5.2). E est public dès la poussée du texte scellé : tranches et épisodes de développement se calculent d'avance ; sans effet tant que proposeurs et expérimentateur n'ont ni outil ni accès au dépôt. Les sorties des modèles ne sont pas reproductibles ; elles sont gardées (texte caviardé, empreinte de chaque
consigne et de chaque contexte servi).

## 9. Commandes exactes

Depuis `orchestrator/`, dossiers de sortie neufs.

- **Répétition à blanc avec le code existant** (v59, aucun modèle ; faite en L3) :
  `nice -n 10 python3 -I -B demonstrations/mode_a_blanc_v59.py SORTIE --graine 20261102 --bac reel --utilisateur-bac 64097 --generations 3 --cartes-reference 12`
- **Essais et banc** avant scellement : `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v59_boucle_fermee.py essais/test_v60_reserve_tenue_a_l_ecart.py essais/test_v60_oracle_tour_ferme.py essais/test_v60_lecture_tour_ferme.py essais/test_v61_lecture_tour_ferme.py essais/test_v61_reserve_tenue_a_l_ecart.py essais/test_v61_tour_ferme.py essais/test_tour_ferme_v62.py` ;
  `nice -n 10 python3 -I -B essais/mutations_v59.py` ; `… essais/mutations_v60.py` ; `… essais/mutations_v61.py` ; `… essais/mutations_tour_ferme_v62.py`.
- **Réserve des données tenues à l'écart** (session-depot, avant scellement) :
  `nice -n 10 python3 -I -B demonstrations/reserve_tenue_a_l_ecart_v60.py EPISODES_GRAINES_NEUVES.json SORTIE_RESERVE [--cle-tache NOM]`
  (rend les empreintes et les comptes de la case 5.2, aucun contenu).
- **Répétition à blanc du lanceur v62** (vrai bac ; doublures scriptées branchées sur le chemin réel, une seule course à la fois par identité dédiée) : `nice -n 10 python3 -I -B demonstrations/tour_ferme_v62.py SORTIE --etage 1 --a-blanc --graine 20261102 --bac reel --utilisateur-bac 64097`
- **Étage 1, réel** (chez la session-depot, clés et `bwrap`) :
  `nice -n 10 python3 -I -B demonstrations/tour_ferme_v62.py ../resultats/tour-ferme-v1-etage1 --etage 1 --preenregistrement prereg/preenregistrement-tour-ferme-v1-v<N>.md --configuration CONF_V3 --moteur reel --confirmer-moteur-reel --registre-go registres/go.md --go <<CASE_GO>> --bac reel --utilisateur-bac UID` (d'abord avec `--verifier-seulement`)
<!-- etage-2-hors-scellement : début -->

**Étage 2 — hors de ce scellement, texte de l'étage 2 à sceller plus tard, avant toute lecture de T.**

- **Étage 2, réel**, seulement sur lecture scellée « tient » :
  `nice -n 10 python3 -I -B demonstrations/tour_ferme_v61.py ../resultats/tour-ferme-v1-etage2 --etage 2 --lecture-etage-1 LECTURE.json --lecture-etage-1-sha256 SHA --tenue-a-l-ecart DOSSIER_RESERVE (mêmes options)` — refusé par cette version après la porte et le montage (cœur de l'étage 2 non écrit).

<!-- etage-2-hors-scellement : fin -->

- **Lecture gelée de l'étage 1** (après la course, par un lecteur neuf, R13) : `nice -n 10 python3 -I -B demonstrations/lire_tour_ferme_v62.py ../resultats/tour-ferme-v1-etage1 LECTURE.json` (à écrire en v62 : vérifie le sceau et l'empreinte du relevé, applique `lire_tour` au champ `releve`, écrit la lecture scellée qu'exige la garde 12).

Sorties : `manifeste.json` (écrit avant le premier appel : empreintes du code gelé, configuration, E, consignes) et
`tour-ferme-v1-etage<e>.json`, chacun avec son `.sha256`. Codes : 0 (sortie écrite), 2 (refus avant tout appel), 3 (arrêt) ;
**le code de sortie ne décide rien.**

## 10. Lectures préalables déclarées

| # | qui, quand (UTC, 2 novembre) | course | racines | vu |
|---|---|---|---|---|
| L0 | développeur v59, avant 07:00 | mode à blanc v59, 2 générations, 3 bras, vrai bac | 20261102 | rapport v59 § 4 : G1-FAUSSE-2 promue puis éliminée ; G1-ALEA-06 promue et survivante (+0,30 nat) ; zéros de la génération 2 |
| L1 | rédacteur, ≈ 07:09 | juge seul (archive vide) et statistique du test de mort calculée en processus, sans bac : L*, S-F1, S-F2, S-F4, anti-loi, L* tempérée, L* restreinte à z0 et à z1, 200 graines chacune ; 1 000 lois aléatoires | 1000–1199, 5000–5999 ; oracle 20261102 | L* promue 200/200, statistique ≥ 0,02 200/200, G = 0,523 ; S-F2 promue seule 83/200, statistique ≥ 0,02 3/200 ; S-F1, S-F4, anti-loi 0/200 ; L* restreinte à z1 G = 0,402 promue 200/200 ; restreinte à z0 G = −0,154, 0 PS ; aléatoires : G ≥ 0,02 pour 120/1 000, PS 112, dont 2 avec G < 0,02 ; 35 promues avec G < 0,02, dont 1 survivante |
| L2 | rédacteur, ≈ 07:11 | bras aléatoire (12 cartes, e-BH de la génération) et recopie-mélange face à l'archive {L* restreinte à z1}, 100 répétitions, statistique en processus | 9000–9099 | aléatoire : 1 200 cartes, 175 promues, PS 150 (0,125), informatives 159, FD 3 (0,0025), VD 147 ; recopie : 300 cartes, 0 promue |
| L3 | rédacteur, ≈ 07:16 | mode à blanc v59, 3 générations, 12 cartes de référence, vrai bac (`bwrap`, identité 64097), 24 s, code 0 | 20261102 | journal sha256 `474d005a5e7383d8ccb4f3a59638f639149a2bb8d1d4a309d6e0ffd0caaf15a0` : en v59 la loi plantée de l'amorce entre à l'archive de chaque bras en génération 1, et les générations 2 et 3 ne promeuvent plus rien (par construction) — d'où la décision D3 |
| L2b | contre-lecteur, ≈ 07:40 | bras aléatoire et « bon proposeur » simulés, trois générations, chaque bras contre sa propre archive, e-BH m = 19 avec témoins, statistique en processus, oracle v60 ; 24 et 8 répétitions | 31000– | PS aléatoire 35/288 (g1), 13/576 (g2–3), 48/864 = 0,056 [0,042 ; 0,073] ; FD 1/864 ; bon proposeur 48/48 puis 0/96 |
| L2b-v61 | rédacteur 2, 09:10 à 09:12 (manifeste `debut_utc` 09:10:08 Z, relevé `fin_utc` 09:11:40 Z) | répétition à blanc du lanceur v61 aux conditions exactes du plan (D7 archive du bras réel, D9 mécanique, témoins hors famille, trois bras, trois générations, vrai bac `bwrap`, proposeurs réels simulés par L* bruitée), **une répétition** | 20261102 | relevé sha256 `d1bc9283deebf79a8d4363e5d6eca82ddc8abbcadba27f9e1761bcdb18f3a1a3` : étage 1 « tient », A4 « discrimine » (Newcombe [0,147 ; 0,469]) ; réel 36 jugées, PS 11, VD 11, FD 0 ; aléatoire 36, PS 0 (génération 1 jugée contre une archive réelle encore vide : 0 sur 12, probabilité ≈ 0,21 ; générations 2 et 3 contre l'archive réelle informative) ; recopie 24, PS 0 ; 0 non concluant, 30 contre-calculs concordants, 8 passes de témoins, 6 lectures ; 91 s. Audit S1 « trop beau » déclenché (proposeurs scriptés voisins de L* : VD* en génération 1, attendu à blanc). Conséquence lue : sous D7, la part PS du bras aléatoire dépend de l'archive réelle (ici 0/36) ; P4 est écrite par cas (section 4.3). **Limite** : les deux rôles modèles y reçoivent hors bande ce que les vrais ne reçoivent pas (la loi éprouvée pour l'expérimentateur, la grammaire des lois pour les proposeurs) : cette répétition n'essaie pas le chemin réel |
| L2b-v62 | rédacteur 3, 13:41:23 à 13:51:43 UTC (une course à la fois) | répétitions à blanc du lanceur v62 aux conditions du plan (D7 archive du bras réel, D9 mécanique, trois bras, trois générations, vrai bac `bwrap`, identité 64097), **doublures scriptées branchées sur le chemin réel** : proposeurs derrière `ProposeurAdaptateur` (softmax ajustée sur les 200 épisodes de développement servis, écrite selon la grammaire servie), expérimentateur derrière `AdaptateurEtageV62` (loi lue dans le préenregistrement court, évaluateur de la tranche) ; aucun canal hors bande ; 5 racines | 20261102, 20261103, 20261104, 20261105, 20261106 | 20261102 : code 0, 97.8 s, « tient », A4 « discrimine », réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0], aléatoire jugées/PS/FD [36, 1, 0], recopie jugées/PS [24, 0], non concluant 0, consignes d'expérimentateur avec loi 60/60, S1 déclenché, touches de L* 0 sur 6 contextes, relevé `8ce5c8bce0716a35…`; 20261103 : code 0, 102.1 s, « tient », A4 « discrimine », réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0], aléatoire jugées/PS/FD [36, 1, 0], recopie jugées/PS [24, 0], non concluant 0, consignes d'expérimentateur avec loi 66/66, S1 déclenché, touches de L* 0 sur 6 contextes, relevé `6f339f730bb652fc…`; 20261104 : code 0, 107.5 s, « tient », A4 « discrimine », réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0], aléatoire jugées/PS/FD [36, 2, 0], recopie jugées/PS [24, 0], non concluant 0, consignes d'expérimentateur avec loi 66/66, S1 déclenché, touches de L* 0 sur 6 contextes, relevé `26a19fa12ffee3b7…`; 20261105 : code 0, 127.3 s, « tient », A4 « discrimine », réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0], aléatoire jugées/PS/FD [36, 1, 0], recopie jugées/PS [24, 0], non concluant 0, consignes d'expérimentateur avec loi 60/60, S1 déclenché, touches de L* 0 sur 6 contextes, relevé `9aebaa914b9c45c1…`; 20261106 : code 0, 110.3 s, « tient », A4 « discrimine », réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0], aléatoire jugées/PS/FD [36, 1, 0], recopie jugées/PS [24, 0], non concluant 0, consignes d'expérimentateur avec loi 64/64, S1 déclenché, touches de L* 0 sur 6 contextes, relevé `ac25158a666ed8fe…` |
| L4 | rédacteur, ≈ 07:24 | règle de réserve (section 5.2) appliquée aux identifiants de tâches de la banque **publique** par `demonstrations/reserve_tenue_a_l_ecart_v60.py` ; aucune issue lue, aucun contenu imprimé | — (aucune graine) | 16 tâches sur 60 réservées, 32 épisodes sur 120 ; manifeste sha256 `2c20acf7c6edf3df4c0c398516bf41c18948b118a91d2675c94c8530c57cb7be` (dossier de travail du rédacteur) |

Scripts d'exploration L1 et L2 : hors de l'arbre (dossier de travail du rédacteur), cités au rapport de rédaction. Aucune lecture
n'a utilisé de modèle, de vrai expérimentateur, de donnée privée ni l'entropie décisive (inexistante avant scellement). Les
prédictions ont été écrites après L0 à L4 : déclaré ; aucune ne porte sur un modèle de langage, sauf P6 et P7 (sans lecture).

## 10 bis. Contre-lecture (règle R2)

Première contre-lecture : `prereg/contre-lecture-preenregistrement-tour-ferme-v1.md` (2 novembre 2026, 07:05 à 07:55 UTC, sous-agent neuf), verdict **non scellable** : bloquants B1 à B6, importants I1 à I9, mineurs 1 à 10, remplacements T1 à T18, changements de code C1 à C7, décisions D7 à D9 proposées. Ce brouillon 2 applique T1 à T18 (T7 adapté : borne haute de P4 à 6 cartes sur 36 et mention de L2b-v61 ; T12 dans sa forme D9), les constats B1 (code écrit, essayé, à blanc ; étage 2 non écrit, dit), B2 (cases : défaut Q, marqueurs pour les cases privées), B3 à B6, I1 à I9 et les mineurs 1 à 9 ; mineur 10 (découvertes distinctes) : champ `vd_distinctes` du relevé, vide dans le code v61 : calculé par le cœur v62 avant toute lecture (`decouvertes_distinctes` : par bras et génération, divergence symétrique < 0,05 nat sur les instances de l'oracle) ; jamais calculée après lecture. Rapport de rédaction : `prereg/rapport-redaction-tour-ferme-v2.md`. Seconde contre-lecture : `prereg/contre-lecture-preenregistrement-tour-ferme-v2.md` (sha256 `8a74dfd2d455c977c2f14bafcdfd217e86e191661cec59929666410b5ac82b7d`), verdict **non scellable** : bloquants B7 à B9, importants I10 à I24, mineurs 11 à 25, couples T19 à T63, changements de code C8 à C22. Ce brouillon 3 applique T19 à T63 pour l'étage 1 (T22, T26, T32, T52, T55 autrement, dit au rapport v3), et le code `_v62` applique C8 à C22 pour l'étage 1. Rapport : `prereg/rapport-redaction-tour-ferme-v3.md`. **Troisième contre-lecture à faire, sur ce texte et sur le code `_v62`.**

## 11. Portée

- **Étage 1** : un seul monde planté (facile : 13 % des lois aléatoires y sont informatives ; z1 porte l'essentiel de
  l'information), deux fournisseurs, trois générations, un expérimentateur (Kimi) et un vérificateur (Argon) fixes pour tous
  les bras (symétrie exacte ; le vérificateur partage la famille des cartes d'Argon, l'expérimentateur celle des cartes de
  Kimi : le verdict ne dépend d'aucun des deux, il est calculé par le noyau et contre-calculé). Le gardien est la couche mécanique seule, la même pour les trois bras (décision D9, <<DECISION_D9>>) ; l'aiguilleur v53 (fiches d'idées) est hors de portée. Le bras recopie-mélange ne propose que des formes couvertes par le nul v8 : sa FD est nulle par construction ; il vérifie que l'archive du bras réel entre au nul, il ne mesure pas les recombinaisons non couvertes (si/sinon, produits).
<!-- etage-2-hors-scellement : début -->

**Étage 2 — hors de ce scellement, texte de l'étage 2 à sceller plus tard, avant toute lecture de T.**

- **Étage 2** : la vraie question restreinte aux lois de moniteurs sur la banque T0.5 ; T est fait d'épisodes neufs **des mêmes
  tâches** que la banque (aucune tâche nouvelle : rien ne se transporte à d'autres tâches) ; ces épisodes ont été lus une fois
  par le juge pour d'autres lois (lecture du 2 novembre), jamais par un proposeur ; puissance faible sous 0,06 à 0,12 nat.

<!-- etage-2-hors-scellement : fin -->

- **Hors portée** : proposeurs de la famille Claude ; bisociateur ; moisson ; juges d'idéation croisés ; mondes à plusieurs lois
  plantées ; attaques contre le juge (A1) ; traduction des fiches par le pont.

## 12. Devis

Calé sur le second tour réel du 1er novembre (62 appels, 1,47 USD, soit **0,0237 USD par appel**, préenregistrement
`6fcb1035…`) pour les appels simples (proposeurs, gardien), et sur les appels par carte du rapport v59 (section 9) pour les tests
de mort. Session d'expérimentateur SUPPOSÉE à 0,04 USD (consigne plus tranche lue ; ordre de grandeur des lancements réels du
27 octobre, 136 appels pour 5,89 USD avec d'autres modèles), session de vérificateur SUPPOSÉE à 0,02 USD ; en moyenne 2 sessions
d'expérimentateur (un tour d'exécution, un tour de fin) et 1 de vérificateur par carte testée.

| étage, bras | appels attendus | dont tests de mort | USD attendus |
|---|---|---|---|
| 1, réel (3 générations : 2 proposeurs + 18 au gardien ; ≈ 4, 2, 2 cartes et ≈ 2,4 témoins testés) | ≈ 106 | ≈ 46 | ≈ 2,9 |
| 1, aléatoire (3 générations : 18 au gardien ; ≈ 1,5 carte et 2,4 témoins testés) | ≈ 89 | ≈ 35 | ≈ 2,5 |
| 1, recopie-mélange (générations 2 et 3 : ≈ 15 au gardien ; ≈ 2,5 testés) | ≈ 45 | ≈ 15 | ≈ 1,2 |
| **étage 1** (sans gardien modèle, D9 : − 138 appels, − ≈ 3,3 USD) | **≈ 102** | | **≈ 3,3** (2 tours par carte) à ≈ 12 (6 tours) |
| 2, réel (2 générations : 2 proposeurs + 13 au gardien ; ≈ 0,5 testée) | ≈ 33 | ≈ 3 | ≈ 0,8 à 1,2 (contexte plus long) |
| 2, aléatoire de contrôle (2 générations : 13 au gardien) | ≈ 27 | ≈ 1 | ≈ 0,7 |
| **étage 2** | **≈ 60** | | **≈ 1,5 à 2** |
| **total** | **≈ 160** | | **≈ 5 à 14** (plafonds 15 + 5) |

**Plafonds durs** dans le lanceur (plan gelé) : **15 USD pour l'étage 1**, dont **12 USD pour le relais de Kimi et 3 USD pour celui d'Argon** (parts au plan gelé, v62) (contre-lecture C7 : le nombre réel de tours d'expérimentateur par carte n'a pas pu être relevé ici, les journaux du 27 octobre et du 1er novembre étant privés ; à 2, 4 ou 6 tours par carte testée l'étage 1 coûte ≈ 3,3, ≈ 8,4 ou ≈ 12,2 USD une fois le gardien modèle retiré, D9, au prix de 0,04 USD par tour à 2 tours et de 0,06 USD à 4 et 6 tours, contre-lecture 1, I7 ; Kimi, proposeur et expérimentateur, en porte ≈ 2,6, ≈ 7,8 et ≈ 11,6 USD, Argon ≈ 0,7 USD ; le lanceur v61 donne à la porte de chaque relais la moitié du plafond, 7,5 USD, que Kimi dépasse dès 4 tours : la part de chaque relais est fixée au plan gelé, par exemple 12 USD pour Kimi et 3 USD pour Argon, v62), **5 USD pour l'étage 2** (arrêt, code 3, au-delà ; les plafonds par
carte de l'étage v5, 0,5 et 0,1 USD, restent) ; maximum théorique sans plafond d'étage bien plus haut (jusqu'à 19 cartes testées
par génération à 0,6 USD). **Durée** : appels en série à 10 à 40 s → ≈ 0,7 à 2,7 heures pour l'étage 1, ≈ 0,2 à 0,7 heure pour
l'étage 2 ; exécutions du bac (≤ 3 × 120 s par carte testée, en pratique quelques secondes) ; calcul du juge négligeable
(L1 : 2 600 jugements en 56 s sur 2 cœurs). Plafonds de durée : 4 heures et 2 heures. Option D6 (seconde réplique du bras
aléatoire de l'étage 1) : + ≈ 90 appels, + ≈ 2,5 USD.

## 13. Code gelé (bloc vérifié par le lanceur) et plan gelé

Écrit avec ce brouillon 3 (fichiers neufs, règle R12 ; aucun `_v61` modifié) : `pole/tour_ferme_v62.py` (cœur de l'étage 1 : loi gelée et évaluateur servis à l'expérimentateur par le préenregistrement court, grammaire des lois servie aux proposeurs et tenue par le gardien, étage servi à l'aveugle, arrêts scellés, parts des relais, recopie sur le bilan réel de g−1, recherche de L* et découvertes distinctes au relevé, doublures scriptées branchées sur le chemin réel), `pole/evaluateur_lois_v62.py` (évaluateur de référence, bibliothèque standard, servi tel quel dans la tranche), `pole/lecture_tour_ferme_v62.py` (lecture gelée de l'étage 1 : C10, C16), `demonstrations/tour_ferme_v62.py` (lanceur de l'étage 1 : plan d'étage 1, zones de l'étage 2 ignorées, garde 6 complète, machine jetable, monde gelé, moteur de l'étage), `demonstrations/lire_tour_ferme_v62.py` (lecture scellée, C18), `essais/test_tour_ferme_v62.py`, `essais/mutations_tour_ferme_v62.py`. Le code `_v61` reste tel quel ; il n'est plus dans le code gelé de ce texte.

**Le lanceur lit les décisions D7 et D9 dans le bloc `plan-gele` ci-dessous** (D8 relève de l'étage 2, hors de ce scellement ; D2 à D6 sont écrites dans le code gelé : un refus de l'une d'elles exige un code nouveau) (`d7`, `d9`, plafond de l'étage et parts des relais, m, générations, empreintes
de la configuration et du monde planté, GO) et refuse toute valeur hors liste ou tout marqueur restant :
un changement de décision est une version nouvelle du texte, jamais un choix enfoui dans le code. La configuration exigée est
une **configuration à empreinte neuve (v3)** dérivée de celle du 1er novembre (`configuration-mini-course-kimi-argon-v2.json`,
sha256 `4ae5a1e0947d44c1a08548d1b0197bfd96a2264f455189713b06183b2bc83108`), dont `budget.plafond_usd` vaut le plafond de
l'étage ; le lanceur refuse toute autre empreinte ; dans la copie servie aux relais, il remplace le jeton `{REGISTRE}` des
commandes externes **et** la valeur de `--plafond-cumule-usd` par le plafond de l'étage (`attaque_goodhart_v2.substituer_commandes`, substitutions déclarées au manifeste), puis transmet à la porte de chaque relais un plafond d'étape (v61 : la moitié du plafond de l'étage ; v62 : la part fixée au plan).

<!-- plan-gele : début -->
generations_etage_1: 3
cartes_par_proposeur: 6
cartes_reference: 12
m_e_bh_etage_1: 19
plafond_etage_1_usd: 15
plafond_kimi_usd: 12
plafond_argon_usd: 3
duree_etage_1_h: 4
d7: archive_du_bras_reel
d9: mecanique
configuration_sha256: <<CASE_CONFIGURATION_V3>>
go: <<CASE_GO>>
monde_sha256: fdf4d5c1ca0d2971b416ee5f694deff7a4696fe5defb3a6a1843dffef1231877
ordre_des_bras: reel, recopie_melange, aleatoire
<!-- plan-gele : fin -->

<!-- etage-2-hors-scellement : début -->

**Étage 2 — hors de ce scellement, texte de l'étage 2 à sceller plus tard, avant toute lecture de T.** Plan de l'étage 2 (non lu par le lanceur v62 ; à reprendre dans le préenregistrement de l'étage 2) : `generations_etage_2: 2`, `m_e_bh_etage_2: 14`, `plafond_etage_2_usd: 5`, `duree_etage_2_h: 2`, `d8: predicteur_connu`, `reserve_manifeste_sha256: <<CASE_V>>`.

<!-- etage-2-hors-scellement : fin -->

**Étage 2 : aucun code sous ce texte, dit** : le lanceur v62 refuse `--etage 2` avant tout appel (code 2) ; le cœur de l'étage 2 (juge à plan plein étendu aux membres d'archive, constructeur du monde M2, test de mort contre le prédicteur connu, D8, garde 11 branchée) relève du préenregistrement de l'étage 2 ; ce texte ne revendique aucun essai de l'étage 2.

Empreintes du code gelé (fermeture des imports des chemins à blanc et réel et de la lecture gelée, plus l'évaluateur servi, essai `Fermeture` de `essais/test_tour_ferme_v62.py` ; calculées à la tête `c47b608` ; revérifiées par la contre-lecture 2 à la tête `7d3aa82`, où les fichiers `_v61` sont suivis : 83 empreintes, aucun écart ; recalculées ci-dessous pour le code v62, arbre de travail à la tête `82ad7a8`, fichiers v62 non suivis : à revérifier après commit) :

<!-- empreintes-du-code : début -->
702250e351e53902028b8fb82970a3c4139e6b87cbe67f9fe66fa27186665d06  demonstrations/tour_ferme_v62.py
e18e9858dc23623e3d00a218373a9b72c736145c2b8478e224defe22ec8bb2a9  demonstrations/lire_tour_ferme_v62.py
58609e0c9fc5c5eea5de1dbb8c9b8235fd85a9884d326ffe09dfb50b21af79cf  demonstrations/attaque_goodhart_v2.py
bc5e9c98acff41b97487e2345d33768c8cdf41f0ededf8b2eed0bf842c889845  demonstrations/ideation_v2.py
4212d4c9d014a265847d4c4ed87a8cd804fdafa73f85fd8947874d63fca1c36d  demonstrations/ideation_v4.py
1894f250264eaaccbf891dfa255e71dc587fe415c8d21e283391203a2fe73444  demonstrations/ideation_v5.py
4c302e5b97b229d5b3edd9e9a427f1e50796c10f7081f63132165ffeef854ba4  demonstrations/ideation_v6.py
7b90e65e1308b1c230b3f804743cfc42b9dc571d93b73ed6c5f3f8c9d2b481b2  demonstrations/ideation_v7.py
2e2be8d72c548e183b94c14de20c971f241f998f54f64c5281b2427fdd64e9d1  demonstrations/ideation_v8.py
f7341b965ddba1e0fb21b44d9068f59650d5c77e3175f2b6b7ca879219fa5c9b  pole/__init__.py
606aa8b4fcc38786b38cf2954da46533eed9384232a56100d22ff30b8ce0826c  pole/a_blanc_v59.py
09a46515ff30a99f360fcbc7d4c613c35cb511439a5b6c249327e477fdee4ada  pole/adaptateur_kimi_v53.py
a1a8ede8d38884a28365ee797dcd3018dbf09ea1baefa3f57cfcb3281c529c99  pole/adaptateurs.py
d36c79b272af450b8d67313f44068743d80f0204bcedbd30f5d879829c945a17  pole/adaptateurs_v56.py
a856cdaa37e8fb1f3b873ef2c0d9aa439ee0a8838f5ee9a2910cb3c0dcf8007f  pole/aiguilleur_v53.py
3c9de8b83b6fcf198d12cacf6a6738c2fc3fe4ade9391f943b3924592959e703  pole/attaque_goodhart_v2.py
962eb8ce22d5af1bf59970e9ef9cab15620edef4d5e9746161bc302e97c2af02  pole/bisociateur_v53.py
20d938b2dcafcd4bb7c9777a0182a3590b390a146a8375590905741ea0e250f8  pole/bisociateur_v54.py
d9521311a96384494871e9f9fcd4b4554548b9f45fdc28e8e75ca30d4c54d22f  pole/bisociateur_v55.py
a2de486592fc98c14e13bb9071d272fb65d4f49de38dd188ee64857698177681  pole/boucle_fermee_v59.py
cefc7e76322b8f8266ec77f31ecb06bf1ea21633ab5dec1e1b91dc62e4374345  pole/budget_v53.py
220d25e6ce5a7eed008c095ef1a9f66e84b4e98f801dfee2f74bdda02ba5ac62  pole/budget_v54.py
3a672aceeeee3cf83cd4e46ca461fdbaf3acd0a9552be24d2566627ce6b7c13e  pole/budget_v56.py
78abfd4731218e20538418608ebebaca3364206ef6d014b7a34829a3c9fd7e85  pole/caviardage.py
f8a70c8f71c380689b2979e3c212d09379ceee1973465b2b207b493cbd73c380  pole/coffre_v53.py
ef10fe044608fda51d5cd4b3b855da677845be83d1367ca3aa33fe45337e33fd  pole/coffre_v55.py
ef72ffbf6b5ba546fb5e509502b59f0d9ac4f78772dcb9570ef36086639f4a78  pole/configuration_v53.py
3424ca7fa8911e5c2656cb56632f7d74c958008b9366af0ac45e6a62e4d16d66  pole/configuration_v54.py
2e6237c0a8b1c823fa17ddd6c680357a59ec4030bfbe9ac6ba970a700a864071  pole/configuration_v55.py
122405228d6ec550b2120114e87a1e70bcc74c14eee17342605d8402bd015d6b  pole/configuration_v56.py
fabc3d0873e6db639f2578eb00ef0035d7831a3b2a1457ffce1d91aa7a364e1c  pole/controles_pari.py
8f2d035828df913d8fa92e1b7d0c8e41ac73e8416e60f3b674753c27f5c61237  pole/course2_v53.py
ac1980d04eb88d8fbb9a073902e47146ab9eadd3375a41cd72835fa5acf20342  pole/course2_v54.py
ee6a861e7f8db32a9545372a51f902389cdbea809b0ba354e621a3681e541a70  pole/course2_v55.py
14f655696876afc8453ec5237236b3f9daf8d87844c4acc9d5189b3e61b310f1  pole/course2_v56.py
798f039042e3ee1f18df5c566f5a0ddee5dac5c98225c8ce621e267174c8ee18  pole/cycle.py
62fd284519278382592a4684e9d4ecd32baad5e11491c256ef64ee844f08d087  pole/dossier_ferme.py
d568d25bf7d96011cfdcda12e7bc2c1933a61827b237f8c8c363b4055122ad4b  pole/etage_entre_generations_v53.py
86a6bec00c3fee9b4ea510cf8dad8d899b9c96adef1e5ae4f8a8281d658143e5  pole/etage_entre_generations_v54.py
865bd7e5734618a2e989bdd14726ff7db53e014963cbc93b48be1892c7ab4dd9  pole/etage_entre_generations_v55.py
f0c80e2d9801d4a928574f7f442e2950c2d130d77015b30102911bfa87dd6eba  pole/etage_entre_generations_v56.py
e4bf36819d18844079a2bb4996991fd65c233a51d76b7d3daf5b866a71328318  pole/etage_entre_generations_v57.py
26613fe72da7f049d5dd076aab51a3808221bf52686b9d0258a201c8b38b8632  pole/evaluateur_lois_v62.py
ec018f147196222268d91358ce2038bb35bf76069e6bf8928dea9e3db59d1074  pole/fiche.py
7cfcf8329c66c7a37ceb2992cc96e21aedbfa0a10525467672794090a128eda6  pole/fiches_v53.py
1ab0796dd5d9de14ea84953b0307a065572bc300ebe45209ca207d7880bbaebf  pole/fiches_v54.py
3abd0e19a8f16cc1c2a8f2590ea04831a7d9ba25c02129fb881b87be3983f390  pole/garde_outils.py
83b54b816b3277d97f5340ad4a316094a492bc2090c782b3e134092a97ca1edf  pole/gardes_e0_v54.py
e46c5cd0a301c89830d97c098ee52b33ead6b01cafe15ab8454e6b7957c54db1  pole/gardes_e0_v55.py
921e59f23753666d6367678447edf4ee2964dc6ec3d382aefa8582b996e123b9  pole/gardes_e0_v56.py
7eb838958b28c7b7a5ee20177dfc3d0c194002b99b2382e019fe7d91c3090dc0  pole/graines_v53.py
67d2ad3591b21601ece4101154138f532ba519024761beb8c9738181f8f3fefc  pole/ideation_v2.py
c4c6ab12dc471eef078c116a4205a22d9b498da720ce71e37a0a6edae6c4239b  pole/juges_croises_v53.py
c7f6ebc8ea0cb24ed97a45362361ab9c9b3a17f0e88d43aeb914617eafd8387a  pole/lecture_tour_ferme_v62.py
71f1d08613bf335aa9ef7aa1397f20aa24553fea2f1b858c10b265d62f8ab79e  pole/memoire.py
43b01b43b1ec347ff02b456975d74c17e7a0e974e9b95e9ba4935bdb895f31a0  pole/memoire_v53.py
8f3f57fc98972fbcf6aefb27fd37298ac67f249cd295c7127b47ab8e77626c08  pole/mesures_v54.py
35d9a996aaacf6d61e84762a2173e73e3c1a90eda730cce122a0f321b038d0e1  pole/moisson.py
711a32679164bd63605f0bcc2a96f37d53260c479004d04d887d8228ac7d431b  pole/noyau_v54.py
ca0f2dda980777da9c549519c6b15994309722353b22f88d117e95aa2c2d4035  pole/noyau_v55.py
eb5a003e8f23b0882e5588fe537e8b65b890f0d7d19560896be4e85a0731543b  pole/noyau_v56.py
0ed9b4adbcddc4ad77a1c97d5cbd5706f14926e9c47fe96ce2bab3221a138910  pole/nul_filles_v2.py
cc452aafd17121a7c0ec42829eea47063ffee1f6cdf7f642e264d528f976b888  pole/nul_v8.py
514864b7879e5131ee37f7a57951db5ece514abe9acbd90b1294e0d914041669  pole/oracle_tour_ferme_v60.py
966d9553026aad1eb7d97fa677334f1b59f22a39f15eef95134d63bc47634444  pole/outils.py
ec6c2cf64d0c9a3bcb3484f2bc58ca986c89e97829bd45fdb96cbc42bf094fef  pole/pari_apparie.py
77056684e5d1b2149521878da396d51bb3f16834de85ca9e86acdc7e1998592d  pole/prepilote_v54.py
e91e07e4f3bf67cd5106129586048abb3b06284eb9812f8e4da4082087859f05  pole/prepilote_v55.py
dfce55061c65b5ae7526161c54be17005ddef631cb539463cd2c23b32b87b087  pole/prepilote_v56.py
7d00371a8fcfa3efc2c17b2f0ab33d18ef83b41f3988744ea12dcf823806f68f  pole/proposeurs_references_v59.py
0657eec8e0b1a3d2a3f57f37aad59c34554a2352be4e42ed2c3395e9e94fe2b5  pole/protocole_outils.py
b5a76343e458cf8fb91ee1928244f9cb65d50c27ab9b1bae91c21a5c82349da3  pole/relais.py
1b90b020287e575b5564508f9ba33b87bbc051c1015f4198e6b6e648d50ee153  pole/relais_reel.py
359928110d757cd54cc0d2773910c7360895b68cac5d17e0e4b4e9933ef306bc  pole/selection_pari.py
620225973d68670a56ca913cdd02709fa576fa43e1393d166915ea67c1d7c3bb  pole/suivi_roles_v54.py
1a8267fea6d147b070d697ccd2c9d33f2514be6fcba106dca8ca123be1cb7403  pole/tableau_v53.py
363a3725885da08412f25b28defba7a8d204d883c3637f1de1df83686d93a41a  pole/tests_de_mort_v2.py
ea05eb55f9d179501fb091d25298deaf36cd66ad16fd65bdca4dcf5e4ba74bba  pole/tests_de_mort_v3.py
35912a3ab5e9e289077ffdceb492bb966f24176244976b3923dcfe95bda1603a  pole/tests_de_mort_v4.py
da524871b9b498693d67cc099240acb98c4c84c800ee4c69f0a1cb5fe60b64f1  pole/tests_de_mort_v5.py
0af0f759a45cf90b769908d0fb72a2837f18994859651444fc280dc5127c3c99  pole/tour_ferme_v62.py
<!-- empreintes-du-code : fin -->

## 14. Décisions, et ce qui manque pour lancer

- **D1** — **prise** par Lazar (`GO-2026-11-02-06`, registre privé, 2 novembre 2026) : les proposeurs ne reçoivent que les lois retenues, sans verdict ni rang.

Décisions écrites selon la recommandation de la contre-lecture (section 5 de celle-ci), chacune marquée dans le texte par `<<DECISION_Dn>>` à remplir sur le mot de Lazar ; un refus = version nouvelle (D7 et D9 sont des paramètres du plan gelé de l'étage 1, lus par le lanceur ; D8 est un paramètre de l'étage 2, hors de ce scellement ; D2 à D6 sont écrites dans le code gelé : un refus de l'une d'elles exige aussi un code nouveau) :
- **D2** — définition de la fausse découverte par l'oracle, g₀ = 0,02 nat, nouveauté contre l'archive (section 3) (oui). Mot de Lazar : <<DECISION_D2>>.
- **D3** — témoins jamais retenus ni servis, contrairement au mode à blanc v59 où l'amorce entre à l'archive (oui ; L3 montre
  qu'autrement les générations 2 et 3 ne mesurent plus rien). Mot de Lazar : <<DECISION_D3>>.
- **D4** — bras recopie-mélange nourri par l'archive du bras réel (oui ; sinon il ne recopie que ce que le hasard a retenu). Mot de Lazar : <<DECISION_D4>>.
<!-- etage-2-hors-scellement : début -->

**Étage 2 — hors de ce scellement, texte de l'étage 2 à sceller plus tard, avant toute lecture de T.**

- **D5** — T entier pour les deux générations de l'étage 2, génération 1 seule décisive (oui) ; ou T coupé en deux. Mot de Lazar : <<DECISION_D5>>.
<!-- etage-2-hors-scellement : fin -->

- **D6** — bras aléatoire de contrôle à l'étage 2 (oui, ≈ 0,7 USD) ; seconde réplique du bras aléatoire de l'étage 1 : non (recommandation : les 2,5 USD servent mieux au plafond). Mot de Lazar : <<DECISION_D6>>.
- **D7** — le bras aléatoire est jugé contre l'archive du bras réel de la même génération, ses retenues ne servent à rien (`d7 = archive_du_bras_reel`) ; alternative `archive_propre`.
<!-- etage-2-hors-scellement : début -->

**Étage 2 — hors de ce scellement, texte de l'étage 2 à sceller plus tard, avant toute lecture de T.**

- **D8** — statistique du test de mort de l'étage 2 = gain sur le prédicteur connu du moniteur (`d8 = predicteur_connu`) ; alternative `marginale`.
<!-- etage-2-hors-scellement : fin -->

- **D9** — gardien mécanique seul pour les trois bras (`d9 = mecanique`) ; l'alternative `aiguilleur` n'est pas écrite (refus du lanceur).

Ce qui manque, dans l'ordre : (1) le code `_v62` (contre-lecture 2 : loi servie à l'expérimentateur, grammaire servie aux proposeurs, lectures d'héritage, arrêts scellés, relais, machine jetable) et, pour l'étage 2, son cœur ; leurs essais, leur banc de mutations et une répétition à blanc où les rôles scriptés ne reçoivent que ce que reçoivent les modèles ;
(2) la contre-lecture R2 de ce texte et de ce code par un sous-agent neuf ; (3) les décisions D2 à D9 (marqueurs) ; (4) chez la
session-depot : le texte et l'empreinte de la question du 1er novembre et la configuration de son tour (modèles,
adaptateurs), l'exécution de la réserve et les cases de la section 5.2, le monde M2, les clés, **`bwrap` 0.9.0 et une identité
dédiée sans privilège sur son instance** ; (5) le scellement par le directeur, commit et poussée du texte scellé **avant** la
course ; (6) le GO de Lazar sur ce devis : une ligne de `registres/go.md` de type « calcul », par Lazar, en cours de validité, d'un montant **exactement égal** au plafond de l'étage (15 USD pour l'étage 1 ; `configuration_v55.verifier_go_v55` refuse tout autre montant) ; l'étage 2 exige un GO et une configuration à lui (5 USD) ; (7) après la course : sortie
scellée avant lecture, lecture par le code gelé, verdict par un lecteur neuf (règle R13).
