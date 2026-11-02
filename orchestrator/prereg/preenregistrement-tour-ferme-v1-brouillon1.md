# Préenregistrement — le tour fermé pour de vrai (tâches A2, A3 et A4), brouillon 1

Statut : **brouillon 1, non contre-lu (règle R2), non scellé.** Rédigé le 2 novembre 2026, de 07:02 à 07:45 UTC environ, par
un sous-agent rédacteur, sans aucun appel de modèle, sans clé, sans commit ni `git fetch`, sous `nice -n 10`. Dépôt public à
la tête `7fadf96`. Le scellement (compagnon `.sha256` écrit par le directeur, sur une version contre-lue renommée
`preenregistrement-tour-ferme-v1-v<N>.md`, sans « brouillon ») fixe la graine (section 8) ; le lanceur à écrire (section 13)
devra refuser tout fichier dont le nom contient « brouillon » et tout fichier non scellé. **Aucune course réelle avant le
scellement, la contre-lecture, la validation par Lazar des décisions D1 à D6 (section 14) et son feu vert (GO) sur le devis
(section 12).** Les cases « à remplir avant scellement » (section 5.2) sont remplies par la session-depot, qui tient les
données privées, puis relues par le contre-lecteur ; un texte qui en garde une vide ne se scelle pas.

## 0. En dix lignes

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
  tuées sur 9. **Ce qui manque** pour ce tour, dit en section 13 : un lanceur à vrais modèles (`_v60`), des témoins exclus de
  l'archive, un gabarit de test de mort imposé aux proposeurs, un contre-calcul de la statistique par l'orchestrateur, un
  la porte entre étages. Sont écrits avec ce brouillon : la réserve par empreinte des données tenues à l'écart
  (`pole/reserve_tenue_a_l_ecart_v60.py`), l'oracle avec le classement gelé des cartes et les intervalles
  (`pole/oracle_tour_ferme_v60.py`) et la lecture gelée des deux étages (`pole/lecture_tour_ferme_v60.py`) : 46 essais,
  17 mutations tuées sur 17 pour la raison attendue.

## 2. Ce que voient les proposeurs (point ouvert (i) du développeur — décision D1, à valider par Lazar)

**Changement par rapport à la v57 et aux tours réels précédents.** Jusqu'à la v56, la génération suivante héritait du
**classement des juges**, écrit avant l'étage des tests de mort (README, section 2, étape 9). En v59 et dans ce tour, chaque
proposeur reçoit **seulement** (`boucle_fermee_v59.vue_pour_proposeur`, garde `exiger_vue_sans_verdict`) :

1. la **liste des lois retenues** de son bras (identifiant opaque et loi prédictive, rien d'autre) : celles dont le verdict
   scellé du noyau au test de mort est « survit », cumulées depuis la génération 1 ;
2. la description publique du monde (traits, sous-populations, nombre d'issues ; jamais une issue de l'épreuve), le gabarit
   (types de loi permis, borne des poids) et, à l'étage 1, **200 épisodes de développement** tirés à chaque génération dans le
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
| **vraie découverte** (VD) | PS **et** G ≥ g₀ **et** ΔG ≥ g₀ : la carte porte au moins 0,02 nat d'information sur le monde au-delà de sa marginale **et** au-delà de ce que l'archive savait déjà |
| **loi plantée retrouvée** (VD*) | VD **et** D ≤ 0,05 nat |
| **fausse découverte** (FD) | PS **et** (G < g₀ **ou** ΔG < g₀). Toute PS du bras « recopie-mélange » est une FD par construction (sa loi est fonction des seules lois de l'archive), quel que soit l'oracle |
| **fausse promotion du juge** | promue **et** (G < g₀ ou ΔG < g₀), quel que soit le test de mort (erreur du juge que le test de mort doit rattraper) |
| **inconclusive** | verdict du noyau « non concluant » (fichier brut absent, incident de la fiche, session en échec, contre-calcul en désaccord : section 7) |

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
  bornés à ±4). **L'orchestrateur complète** tous les autres champs, dont le test de mort : le proposeur ne choisit ni la
  statistique, ni le seuil, ni les données (garde neuve, section 7).
- **Bras aléatoire** : `proposeurs_references_v59.proposer_aleatoire`, 12 cartes par génération (softmax sur un ou deux traits,
  poids gaussiens d'écart-type 1,2 bornés à ±4, biais nuls) ; vue vérifiée, jamais lue.
- **Bras recopie-mélange** : `proposeurs_references_v59.proposer_recopie_melange`, au plus 12 cartes par génération, faites des
  seules lois **retenues par le bras réel** jusqu'à g−1 (décision D4 : il lit, vérifié par empreinte, le bilan du bras réel,
  et ses cartes sont jugées contre l'archive du bras réel, c'est-à-dire contre le même nul que les cartes réelles de la même
  génération). Génération 1 : archive vide, aucune carte (motif consigné, aucun repli). S'il n'a aucune carte en générations
  2 et 3, sa mesure est « non mesurable » (issue écrite, section 4.7).
- **Témoins** (mêlés anonymement à chaque génération de chaque bras qui joue ; identifiants opaques ; jugés comme témoins,
  sans membres d'archive, comme `cycle.Generation.geler` ; **jamais retenus, jamais servis**, décision D3) :
  T-VRAIE = L* ; T-F1, T-F2, T-F4 = S-F1, S-F2, S-F4 (G = −2,35 ; −0,13 ; −0,91) ; T-ANTI = poids opposés à L* (G = −3,81) ;
  T-ELIM (instrument du test de mort) = L* accentuée (puissance 1,25) dont le test exige un gain d'au moins 2,0 nat
  (inatteignable) ; T-MAL (instrument du gardien) = carte sans bloc `statistique`. Le cas « inconclusif » scripté du mode à
  blanc v59 n'est pas repris (un expérimentateur modèle ne se scénarise pas) ; il reste dans la répétition à blanc.
- **Gardien** : deux couches, la même pour les trois bras et les témoins. (a) mécanique : gabarit, `selection_pari.valider_loi`,
  `tests_de_mort_v5.valider_champ_test` (bloc `statistique` exigé) ; (b) `aiguilleur_v53` de la configuration du 1er novembre,
  une session neuve par carte, consigne figée : seule la classe « niveau méthode » donne un passeport ; réponse illisible ou
  refus = aiguillage (pas de passage).
- **Juge** : `a_blanc_v59.juger_carte` (appel pour appel `banc_tricheurs_v8.juger_v8`, genre « fraîche ») : bibliothèque
  aveugle + marginale d'entraînement (100 tirages) + membres d'archive du nul v8 (`nul_v8.membres_archive_v8` sur l'archive du
  bras), engagement gelé, ordre secret, 200 tirages frais liés à l'empreinte de l'engagement, lecture aux instants fixés ;
  puis e-BH par (bras, génération) avec **m fixé à 19** avant toute issue (12 emplacements de cartes + 7 témoins, les témoins
  comptant dans m comme dans `cycle.appliquer_multiplicite` ; un emplacement vide vaut e = 0) — le même m dans les trois bras.
- **Tests de mort** : étage v5 (`tests_de_mort_v5`) par `etage_entre_generations_v57.jouer_etage_v57`, dans le **vrai bac à
  sable** (`bwrap`, sans réseau, un seul dossier, 768 Mo, filtre d'appels système, identité dédiée sans privilège ; jamais de
  repli sur l'exécuteur factice), pour toutes les cartes promues et tous les témoins promus de la génération. Tranche : 400
  épisodes frais du monde planté par (bras, génération). Gabarit gelé du test (`proposeurs_references_v59.TEST_DE_MORT`) :
  gain moyen par épisode du log-score de la loi sur la marginale empirique de la tranche (comptes + 0,5), fichier brut
  `gains.csv`, colonne `gain`, statistique « moyenne », seuil « au moins 0,02 ». **Expérimentateur** : Kimi (session modèle,
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
- **P4 (bras aléatoire)** : part PS du bras aléatoire **entre 0,05 et 0,25** (L2 : 150 sur 1 200 = 0,125, Wilson
  [0,107 ; 0,145]) ; FD du bras aléatoire **≤ 1 carte sur 36** (L2 : 3 sur 1 200 = 0,0025).
- **P5 (bras recopie-mélange)** : **0 FD** (L2 : 0 promue sur 300 face à une archive informative ; validation du nul v8 :
  0 sur 1 000 pour T02, T03b, T04, T05s, T17s). Ouverte : une FD, possible au niveau α par carte, est rapportée et auditée.
- **P6 (signe +, bras réel)** : part PS du bras réel **≥ 0,30** et part VD **≥ 0,25** sur ses cartes, donc au-dessus du bras
  aléatoire (Newcombe, borne basse > 0 attendue). Ouverte dans l'autre sens : PS réel ≤ 0,15 dirait que les vrais proposeurs,
  avec 200 épisodes de développement, ne font pas mieux que le hasard dans ce monde. Aucune lecture préalable ne porte sur ce
  bras (aucun modèle appelé) : prédiction de rédacteur.
- **P7 (loi plantée retrouvée par les proposeurs)** : **aucune VD*** (D ≤ 0,05 nat) en génération 1 ; la plus petite
  divergence D parmi les VD du bras réel **décroît** de la génération 1 à la génération 3 (mesurée, sans seuil). Ouverte : une
  VD* dès la génération 1 dirait que 200 épisodes suffisent à un modèle de langage pour ajuster la loi à 0,05 nat près.
- **P8 (gardien)** : part de cartes refusées par le gardien modèle ≤ 0,10 dans chaque bras ; écart entre bras ≤ 0,15.

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

Calculé par `pole/lecture_tour_ferme_v60.lire_etage1` (écrit avec ce brouillon) sur le relevé scellé, dans cet ordre ;
**tous** doivent tenir :

1. **T1 — boucle** : aucune `SelectionNonVerifiee`, `HeritageRefuse` ni `VueAvecVerdict` ; chaque génération g ≥ 2 a lu le bilan
   de g−1 à l'empreinte consignée (journal) ; aucun arrêt de la liste d'arrêt.
2. **T2 — loi plantée** : T-VRAIE « survit » dans **toutes ses passes sauf au plus une** (8 passes prévues ; 6 si le bras
   recopie-mélange ne joue pas), « éliminée » dans aucune.
3. **T3 — fausses** : au plus **1** passe de témoin faux promue puis survivante sur 32 (24 si le bras recopie-mélange ne joue
   pas) ; T-ELIM jamais « survit » ; T-MAL refusé au gardien dans toutes ses passes.
4. **T4 — inconclusif** : dans chaque bras, « non concluant » / testées ≤ **0,20** (cartes et témoins) ; aucun désaccord du
   contre-calcul.
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
3. **Ce qui départage, écrit d'avance** : l'oracle sépare deux causes d'un r_réel trop bas. Si T5 tient (la chaîne ne
   transforme presque aucune loi sans information ni aucune redite en découverte), un écart nul dit que **les vrais proposeurs
   ne font pas mieux que le hasard dans ce monde** (où 13 % des lois aléatoires sont informatives) ; si T5 manque, c'est **la
   chaîne qui ne discrimine pas**, et l'étage 2 n'est pas joué. Sensibilité de la chaîne rapportée, sans seuil.
4. **Issues (exhaustives)** : T5 manque → « la chaîne ne discrimine pas » (étage 2 non joué) ; T5 tient et borne basse de
   Newcombe de r_réel − r_aléatoire > 0 → « discrimine » ; T5 tient et borne ≤ 0 → « la chaîne écarte les lois sans
   information, mais les vrais proposeurs ne battent pas le hasard dans ce monde » (réserve majeure pour A3, point 2). Le bras
   recopie-mélange sans aucune carte en générations 2 et 3 → « recopie non mesurable », dit à côté de l'issue.

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
| Q — texte de la question du 1er novembre, chemin et sha256 | — |
| E0 — fichier des 288 épisodes à graines neuves (entrée de la réserve), sha256 | — |
| R — liste triée des tâches réservées, sha256 ; nombre de tâches | — |
| T — fichier des données tenues à l'écart, sha256 ; épisodes ; épisodes par moniteur | — |
| M2 — monde de l'étage 2 (sans les tâches réservées), sha256 ; épisodes par partie | — |
| V — sha256 du module de réserve exécuté et de son manifeste | — |

- **Essai de la règle sur les seuls identifiants de tâches publics** (lecture L4, aucune issue lue) : sur les 60 tâches de
  `banque-t05-v2.json`, 16 sont réservées (32 épisodes publics, retirés de tout), 44 restent (88 épisodes). Sur les 96 tâches
  à graines neuves, environ 32 sont attendues (≈ 96 épisodes dans T) ; le compte exact est celui de la case R.
- **Jamais vues** : T n'entre ni dans le contexte d'un proposeur, ni dans le monde du juge, ni dans une vue ; le lanceur
  vérifie l'empreinte de T avant de le monter et cherche, dans chaque contexte servi, chaque identifiant de tâche réservée
  (garde 11, section 7).
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
gain moyen du log-score de la loi sur la marginale empirique de T (comptes + 0,5), calculé sur les épisodes de T qui portent une
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
  ≈ 0,18 à 0,26 (approximation normale de la moyenne, n = 40 à 85).
- Conjointe (juge SUPPOSÉ à 0,4 à 0,7 pour 0,06 nat et ≥ 0,9 pour 0,12 nat à ces tailles) : une loi réelle de 0,06 nat a
  ≈ 0,3 à 0,55 de passer les deux ; de 0,12 nat, ≈ 0,8 ou plus. **Zéro promotion ne dira donc
  rien des liens sous ≈ 0,06 à 0,12 nat par épisode**, ce que la phrase au mentor dit.

### 5.6 Issues écrites d'avance et phrase pour le mentor

Calculées par `pole/lecture_tour_ferme_v60.lire_etage2`, dans cet ordre :

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
  another model family, and a sealed selection read by the next generation. On our real question, [n] hypothesis(es) written
  by the models was promoted by the judge and then survived a preregistered death test run on held-out episodes reserved by
  hash before the run. On a planted-law world the same chain [kept / lost] the planted law and turned [x] (Wilson 95 % [a, b])
  of random proposals and [y] of copy-and-mix proposals into false discoveries. This is a first hypothesis out of a
  verdict-blind pipeline, not a validated finding: it holds on fresh episodes of the same tasks, and needs new tasks. »
  [+ réserve (a) : « Caveat: on the planted world, our proposers did not produce more surviving discoveries than a random
  proposer, so this promotion cannot be credited to their judgement. »] [+ réserve (b) : « Caveat: a random proposer also
  got through on the real bank. »]
- **Z** : « We ran the loop closed, for real, on our real question: it promoted nothing that survived the held-out death test,
  and we report that zero as preregistered. On a planted-law world the same chain [kept the planted law] and turned [x] of
  random proposals into false discoveries; on our real episode bank, links weaker than about 0.06 to 0.12 nat per episode
  would pass unseen. The pipeline now runs end to end; at this data size, the real question did not yield a hypothesis it
  could confirm. »
- **N** : « The closed loop did not pass its own planted-world gate ([criterion]); we did not run it on the real question. »

En français, pour le dossier : P — « une hypothèse écrite par les modèles, promue par le juge figé, a survécu à un test de mort
exécuté sur des épisodes tenus à l'écart » ; Z — « la boucle fermée a tourné pour de vrai sur la vraie question et n'a rien
promu qui survive ; zéro est le résultat » ; N — « la boucle n'a pas passé sa propre porte sur monde planté ».

## 6. Audit de symétrie (règle R4), écrit d'avance

Un résultat trop propre, dans un sens ou dans l'autre, déclenche le même audit **avant** toute lecture d'issue :

- **S1 — trop beau (étage 1)** : aucune FD dans aucun bras **et** aucun « non concluant » **et** T-VRAIE « survit » 8 fois sur
  8 **et** une VD* du bras réel dès la génération 1. Audit : (1) contre-calcul hors bac de chaque statistique testée depuis la
  loi gelée et la tranche scellée ; (2) lecture de chaque script d'expérimentateur : le fichier brut est-il calculé depuis
  `episodes.csv`, ou fabriqué ? (3) recherche, dans chaque contexte servi aux proposeurs, des poids de L* (exacts et arrondis à
  deux décimales) et de toute ligne de tranche ; (4) vérification que les témoins ont été jugés sans membres d'archive et
  exclus de l'archive ; (5) oracle rejoué sur un cas connu (G(L*) = 0,523). Un défaut trouvé : course invalide, aucune issue.
- **S2 — trop laid (étage 1)** : T-VRAIE « éliminée » ou « non concluant » dans au moins 2 passes, ou fd_aléatoire > 0,05, ou
  une FD du bras recopie-mélange. Audit : rejouer chaque carte en cause avec l'exécuteur factice (même tranche, mêmes graines)
  et comparer les verdicts du noyau ; vérifier les membres ajustés du nul (`nul_v8.exiger_membres_ajustes`) ; relire les
  sessions de l'expérimentateur ; puis lecture des critères, sans les changer.
- **S3 — trop beau (étage 2)** : une carte P avec log e > 20, ou une statistique sur T > 0,3 nat (bien au-dessus de la borne
  de 0,06 à 0,12 nat de la lecture à graines neuves). Audit : empreinte de T au montage ; recherche des tâches réservées dans les
  contextes servis ; la loi encode-t-elle l'identité d'une tâche (trait `bruit`, valeurs exactes) ? contre-calcul.
- **S4 — décevant (étage 2)** : issue Z ou N. Même profondeur d'audit que S3 : plans du juge de la taille prévue, cartes
  valides, refus du gardien par bras, témoins d'instrument conformes, borne de puissance recalculée.
- **S5 — asymétrie du gardien** : refus du gardien modèle d'un bras supérieur de plus de 0,15 à celui d'un autre bras : motifs
  lus avant lecture des parts (un gardien qui refuse les cartes réelles et non les scriptées fausserait A4).

## 7. Liste d'arrêt (chaque garde essayée sur un cas sain et sur un artefact, règle R5)

| # | garde | cas sain | artefact | essai |
|---|---|---|---|---|
| 1 | lecture vérifiée de l'héritage | bilan, sélection, cartes, verdicts aux empreintes consignées | sélection réécrite avec sceau juste ; bilan d'une autre empreinte ; lien symbolique ; retenue non survivante → `SelectionNonVerifiee` / `HeritageRefuse` | existe : `essais/test_v59_boucle_fermee.py` |
| 2 | vue sans verdict | lois seules | clé `log_richesse_max`, `promue`, `comptes` à toute profondeur → `VueAvecVerdict` | existe (v59) |
| 3 | vrai bac à sable, aucun repli | `bwrap` présent, sonde réussie | `bwrap` absent ; superutilisateur sans identité dédiée → `BacASableIndisponible` | existe (v59) |
| 4 | graines dérivées de la tâche (R9) | deux tâches → deux graines | `spawn_key=()` → graines égales (mutation tuée) | existe (v59) |
| 5 | plafond dur de dépense par étage | appels à 0,01 USD : étage complet | plafond franchi → arrêt, code 3, sortie scellée, aucune issue lue | **à écrire** (v60) |
| 6 | préenregistrement scellé exigé | fichier scellé, bloc de code gelé conforme | nom avec « brouillon », sceau absent ou faux, empreinte de code différente → code 2, rien écrit | **à écrire** (v60, comme `banc_tricheurs_v8.lire_preenregistrement`) |
| 7 | témoins jamais retenus ni servis | témoin promu et survivant : absent de la sélection, de l'archive, de la vue | témoin introduit dans l'archive → refus | **à écrire** |
| 8 | gabarit du test de mort imposé | carte du proposeur complétée par l'orchestrateur | carte d'un proposeur qui porte son propre seuil, sa propre statistique ou ses propres données → refusée au gardien mécanique | **à écrire** |
| 9 | familles séparées | expérimentateur Kimi, vérificateur Argon | même famille → refus avant toute session | **à écrire** |
| 10 | contre-calcul de la statistique | gain recalculé par l'orchestrateur depuis la loi gelée et la tranche = statistique du noyau à 10⁻⁶ près | script qui écrit des gains fabriqués → « non concluant », audit S1 | **à écrire** |
| 11 | données tenues à l'écart jamais servies | empreinte de T conforme au montage ; aucun identifiant de tâche réservée dans les contextes | T altéré, rescellé ; tâche réservée déplacée au reste ; liste des tâches incohérente ; tâche réservée dans un contexte → refus | **écrite pour la réserve** (`verifier_reserve`, `taches_reservees_dans` ; `essais/test_v60_reserve_tenue_a_l_ecart.py`, 15 essais ; `essais/mutations_v60.py`, 8 mutations de la réserve tuées sur 8) ; appel au montage et balayage des contextes par le lanceur **à écrire** |
| 12 | porte entre étages | lecture scellée de l'étage 1 « tient » | étage 2 lancé sans elle, ou avec « ne tient pas » → code 2 | **à écrire** |
| 13 | modèle servi inconnu, signal, durée | modèle attendu | autre modèle servi ; durée > plafond (4 h étage 1, 2 h étage 2) → arrêt, code 3 | existe pour le modèle et le signal (`noyau_v56`) ; durée **à écrire** |
| 14 | lecture gelée | relevé sain → « tient », « discrimine », P | chaque critère T1 à T5 manqué → « ne tient pas » ; survivante de génération 2 seule → Z ; contre-calcul absent → Z ; étage 1 manqué → N | **écrite** : `essais/test_v60_lecture_tour_ferme.py` (17 essais), 5 mutations tuées sur 5 |

Arrêt = sortie scellée telle quelle, code 3, aucune issue lue ; reprise seulement dans un dossier neuf, avec le même fichier
scellé, si l'arrêt vient d'une panne d'infrastructure consignée (règle de la section 8 du préenregistrement du nul v8).

## 8. Graines (règle R9)

Entropie racine **E = int(sha256 du fichier scellé, 16)** (entier gros-boutiste de l'empreinte des octets ; E ≥ 2⁶⁴ exigé en mode
réel, E < 2⁶⁴ exigé à blanc : espaces disjoints). Toute graine est `boucle_fermee_v59.graine_de_tache(E, tâche)` =
`numpy.random.SeedSequence(E, spawn_key=(cle_de_tache(tâche),))`, avec les tâches nommées
`tour-ferme-v1|etage=<e>|bras=<b>|generation=<g>` suivies de `|carte=<id>|plan`, `|noyau`, `|frais|<empreinte de
l'engagement>`, `|tranche`, `|developpement`, `|proposeur=aleatoire`, `|proposeur=recopie_melange`, `|temoin=<id>` ; oracle :
`oracle|instances` ; partition du monde de l'étage 2 : `tour-ferme-v1|etage=2|partition`. La réserve de T ne dépend pas de E
(section 5.2). Les sorties des modèles ne sont pas reproductibles ; elles sont gardées (texte caviardé, empreinte de chaque
consigne et de chaque contexte servi).

## 9. Commandes exactes

Depuis `orchestrator/`, dossiers de sortie neufs.

- **Répétition à blanc avec le code existant** (v59, aucun modèle ; faite en L3) :
  `nice -n 10 python3 -I -B demonstrations/mode_a_blanc_v59.py SORTIE --graine 20261102 --bac reel --utilisateur-bac 64097 --generations 3 --cartes-reference 12`
- **Essais et banc** avant scellement : `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v59_boucle_fermee.py essais/test_v60_reserve_tenue_a_l_ecart.py essais/test_v60_oracle_tour_ferme.py essais/test_v60_lecture_tour_ferme.py essais/test_v60_tour_ferme.py` ;
  `nice -n 10 python3 -I -B essais/mutations_v59.py` ; `nice -n 10 python3 -I -B essais/mutations_v60.py` ; `nice -n 10 python3 -I -B essais/mutations_v60_tour_ferme.py`
  (`test_v60_tour_ferme.py` et `mutations_v60_tour_ferme.py` sont à écrire).
- **Réserve des données tenues à l'écart** (session-depot, avant scellement) :
  `nice -n 10 python3 -I -B demonstrations/reserve_tenue_a_l_ecart_v60.py EPISODES_GRAINES_NEUVES.json SORTIE_RESERVE [--cle-tache NOM]`
  (rend les empreintes et les comptes de la case 5.2, aucun contenu).
- **Étage 1, réel** (chez la session-depot, clés et `bwrap`) — lanceur **à écrire** :
  `nice -n 10 python3 -I -B demonstrations/tour_ferme_v60.py ../resultats/tour-ferme-v1-etage1 --etage 1 --preenregistrement prereg/preenregistrement-tour-ferme-v1-v<N>.md --configuration CONF_DU_1ER_NOVEMBRE --moteur reel --confirmer-moteur-reel --registre-go registres/go.md --go GO-2026-11-0X-NN --bac reel --utilisateur-bac UID`
- **Étage 2, réel**, seulement sur lecture scellée « tient » :
  `nice -n 10 python3 -I -B demonstrations/tour_ferme_v60.py ../resultats/tour-ferme-v1-etage2 --etage 2 --lecture-etage-1 SHA256_LECTURE --tenue-a-l-ecart T.json --monde-etage-2 M2.json (mêmes options)`

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
| L4 | rédacteur, ≈ 07:24 | règle de réserve (section 5.2) appliquée aux identifiants de tâches de la banque **publique** par `demonstrations/reserve_tenue_a_l_ecart_v60.py` ; aucune issue lue, aucun contenu imprimé | — (aucune graine) | 16 tâches sur 60 réservées, 32 épisodes sur 120 ; manifeste sha256 `2c20acf7c6edf3df4c0c398516bf41c18948b118a91d2675c94c8530c57cb7be` (dossier de travail du rédacteur) |

Scripts d'exploration L1 et L2 : hors de l'arbre (dossier de travail du rédacteur), cités au rapport de rédaction. Aucune lecture
n'a utilisé de modèle, de vrai expérimentateur, de donnée privée ni l'entropie décisive (inexistante avant scellement). Les
prédictions ont été écrites après L0 à L4 : déclaré ; aucune ne porte sur un modèle de langage, sauf P6 et P7 (sans lecture).

## 11. Portée

- **Étage 1** : un seul monde planté (facile : 13 % des lois aléatoires y sont informatives ; z1 porte l'essentiel de
  l'information), deux fournisseurs, trois générations, un expérimentateur (Kimi) et un vérificateur (Argon) fixes pour tous
  les bras (symétrie exacte ; le vérificateur partage la famille des cartes d'Argon, l'expérimentateur celle des cartes de
  Kimi : le verdict ne dépend d'aucun des deux, il est calculé par le noyau et contre-calculé). Le gardien modèle classe des
  cartes-lois avec une consigne écrite pour des fiches d'idées : ses refus sont mesurés, pas interprétés.
- **Étage 2** : la vraie question restreinte aux lois de moniteurs sur la banque T0.5 ; T est fait d'épisodes neufs **des mêmes
  tâches** que la banque (aucune tâche nouvelle : rien ne se transporte à d'autres tâches) ; ces épisodes ont été lus une fois
  par le juge pour d'autres lois (lecture du 2 novembre), jamais par un proposeur ; puissance faible sous 0,06 à 0,12 nat.
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
| **étage 1** | **≈ 240** | | **≈ 6,6** |
| 2, réel (2 générations : 2 proposeurs + 13 au gardien ; ≈ 0,5 testée) | ≈ 33 | ≈ 3 | ≈ 0,8 à 1,2 (contexte plus long) |
| 2, aléatoire de contrôle (2 générations : 13 au gardien) | ≈ 27 | ≈ 1 | ≈ 0,7 |
| **étage 2** | **≈ 60** | | **≈ 1,5 à 2** |
| **total** | **≈ 300** (environ 5 fois le tour du 1er novembre) | | **≈ 8 à 9** |

**Plafonds durs** dans le lanceur : **12 USD pour l'étage 1, 5 USD pour l'étage 2** (arrêt, code 3, au-delà ; les plafonds par
carte de l'étage v5, 0,5 et 0,1 USD, restent) ; maximum théorique sans plafond d'étage bien plus haut (jusqu'à 19 cartes testées
par génération à 0,6 USD). **Durée** : appels en série à 10 à 40 s → ≈ 0,7 à 2,7 heures pour l'étage 1, ≈ 0,2 à 0,7 heure pour
l'étage 2 ; exécutions du bac (≤ 3 × 120 s par carte testée, en pratique quelques secondes) ; calcul du juge négligeable
(L1 : 2 600 jugements en 56 s sur 2 cœurs). Plafonds de durée : 4 heures et 2 heures. Option D6 (seconde réplique du bras
aléatoire de l'étage 1) : + ≈ 90 appels, + ≈ 2,5 USD.

## 13. Code gelé (à recalculer avant scellement) et code à écrire

Code existant cité, inchangé (sha256 au 2 novembre, tête `7fadf96`) : `pole/boucle_fermee_v59.py` `a2de4865…`,
`pole/a_blanc_v59.py` `606aa8b4…`, `pole/proposeurs_references_v59.py` `7d00371a…`, `pole/course2_v59.py` `b5a19a47…`,
`pole/ideation_v59.py` `069f920a…`, `demonstrations/mode_a_blanc_v59.py` `3f0f8de0…`, `demonstrations/ideation_v59.py`
`5419137c…`, `essais/test_v59_boucle_fermee.py` `ffaad449…`, `essais/mutations_v59.py` `2594f5fb…`, `pole/nul_v8.py`
`cc452aaf…`, `pole/nul_filles_v2.py` `0ed9b4ad…`, `pole/selection_pari.py` `35992811…`, `pole/cycle.py` `798f0390…`,
`pole/juge_plan_plein_v1.py` `6bcec082…`, `pole/tests_de_mort_v5.py` `da524871…`, `pole/tests_de_mort_v4.py` `35912a3a…`,
`pole/etage_entre_generations_v57.py` `e4bf3681…`, `pole/aiguilleur_v53.py` `a856cdaa…`, `pole/monde_banque.py` `33088eb9…`,
`pole/graines_v53.py` `7eb83895…`, `pole/outils.py` `966d9553…`, `demonstrations/banc_tricheurs_v8.py` `0be47e4b…`,
`demonstrations/ideation_v8.py` `2e2be8d7…`. Le bloc complet sera écrit après la contre-lecture et **vérifié par le lanceur**.

**Code à écrire (version `_v60`, fichiers neufs, règle R12), avant scellement** :

1. `pole/tour_ferme_v60.py` — cœur (déjà écrits avec ce brouillon : l'oracle, le classement gelé et les intervalles de Wilson
   et de Newcombe, `pole/oracle_tour_ferme_v60.py`, 14 essais ; la lecture gelée des sections 4.6, 4.7, 5.6 et des audits S1 à
   S5 sur un relevé au format documenté, `pole/lecture_tour_ferme_v60.py`, 17 essais) : témoins marqués, jugés sans membres d'archive, exclus de la sélection et de l'archive
   (D3) ; gabarit fermé du proposeur réel (`{enonce, loi_predictive}`, plus `moniteur` à l'étage 2) et test de mort complété
   par l'orchestrateur ; consigne et contexte du proposeur (vue v59, épisodes de développement) ; bras recopie-mélange lisant
   le bilan du bras réel (D4) ; e-BH à m fixé ; familles séparées ; **contre-calcul** de la statistique hors bac ; appel de
   l'oracle sur chaque carte ; production du relevé scellé au format que lit `lecture_tour_ferme_v60`.
2. **Écrit avec ce brouillon** : `pole/reserve_tenue_a_l_ecart_v60.py` (règle de la section 5.2, manifeste
   d'empreintes et de comptes sans contenu, vérification au montage), sa ligne de commande
   `demonstrations/reserve_tenue_a_l_ecart_v60.py`, ses essais `essais/test_v60_reserve_tenue_a_l_ecart.py` (15 réussis) et
   le banc `essais/mutations_v60.py` (17 mutations — réserve, oracle et lecture — tuées sur 17 pour la raison attendue) ;
   empreintes au rapport de rédaction.
3. Variante du juge à plan plein avec membres d'archive pour l'étage 2 ; constructeur du monde M2 et du format de tranche de
   l'étage 2 (traits, sous-population, tâche, issue par moniteur).
4. `demonstrations/tour_ferme_v60.py` — lanceur : à blanc (adaptateurs simulés par le faux SDK) et réel
   (`ideation_v8.adaptateurs_reels_v56`, porte de plafond), lecture du préenregistrement scellé et du bloc gelé, plafonds de
   dépense et de durée, porte entre étages, manifeste écrit avant le premier appel.
5. `essais/test_v60_tour_ferme.py` (gardes 5 à 10, 12 et 13, et l'appel de la garde 11 par le lanceur ; cas sain et artefact)
   et `essais/mutations_v60_tour_ferme.py` (au moins : témoin retenu, seuil du proposeur accepté, contre-calcul sauté, T servi,
   porte sautée, recopie sur sa propre archive, m d'e-BH compté après coup).
6. **Répétition à blanc de bout en bout du lanceur v60**, trois bras, trois générations, adaptateurs simulés pour les quatre
   rôles (proposeur, gardien, expérimentateur, vérificateur), vrai bac, au moins 5 racines : ce qui couvre les points ouverts
   (iii) du développeur (course v59 essayée par unités seulement, gardien scripté, aucun vérificateur à modèle, une seule
   graine).

## 14. Décisions à faire valider par Lazar, et ce qui manque pour lancer

Décisions (recommandation du rédacteur entre parenthèses) :

- **D1** — vue des proposeurs : lois retenues seules, sans verdict, richesse, rang ni compte (section 2) (oui ; c'est le point
  ouvert (i) du développeur).
- **D2** — définition de la fausse découverte par l'oracle, g₀ = 0,02 nat, nouveauté contre l'archive (section 3) (oui).
- **D3** — témoins jamais retenus ni servis, contrairement au mode à blanc v59 où l'amorce entre à l'archive (oui ; L3 montre
  qu'autrement les générations 2 et 3 ne mesurent plus rien).
- **D4** — bras recopie-mélange nourri par l'archive du bras réel (oui ; sinon il ne recopie que ce que le hasard a retenu).
- **D5** — T entier pour les deux générations de l'étage 2, génération 1 seule décisive (oui) ; ou T coupé en deux.
- **D6** — bras aléatoire de contrôle à l'étage 2 (oui, ≈ 0,7 USD) ; seconde réplique du bras aléatoire de l'étage 1
  (facultative, ≈ 2,5 USD).

Ce qui manque, dans l'ordre : (1) le code `_v60` de la section 13, ses essais, son banc de mutations et sa répétition à blanc ;
(2) la contre-lecture R2 de ce texte et de ce code par un sous-agent neuf ; (3) les décisions D1 à D6 ; (4) chez la
session-depot : le texte et l'empreinte de la question du 1er novembre et la configuration de son tour (modèles,
adaptateurs), l'exécution de la réserve et les cases de la section 5.2, le monde M2, les clés, **`bwrap` 0.9.0 et une identité
dédiée sans privilège sur son instance** ; (5) le scellement par le directeur, commit et poussée du texte scellé **avant** la
course ; (6) le GO de Lazar sur ce devis (ligne dans `registres/go.md`, plafonds 12 + 5 USD) ; (7) après la course : sortie
scellée avant lecture, lecture par le code gelé, verdict par un lecteur neuf (règle R13).
