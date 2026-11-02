non scellable

# Contre-lecture R2 — préenregistrement du tour fermé (A2, A3, A4), brouillon 2, et code `_v61`

2 novembre 2026, de 09:20 à 10:00 UTC environ. Contre-lecteur neuf : je n'ai écrit ni le brouillon 1, ni le brouillon 2, ni leur
code, ni la première contre-lecture. Lecture seule ; un seul fichier écrit dans l'arbre, celui-ci. Aucun commit, aucun `.sha256`,
aucun `git fetch`, aucun appel de réseau ni de modèle, aucune clé ; calculs sous `nice -n 10`. Dépôt public à la tête `7d3aa82`,
arbre propre avant et après (`git status` vide). Dépôt privé : `CLAUDE.md` seulement.

**Verdict en trois lignes.** Le texte applique bien la première contre-lecture, le bloc des empreintes est conforme à `7d3aa82`, et
les 110 essais et les 15 mutations se rejouent. Mais le chemin réel ne peut pas marcher : l'expérimentateur réel ne reçoit jamais la
loi qu'il doit éprouver (B7), les proposeurs réels ne reçoivent pas la grammaire des lois (B8), et la répétition à blanc ne le voit
pas parce que ses doublures scriptées reçoivent l'une et l'autre hors bande. La lecture gelée dit en outre « ne tient pas (T1) » sur
une course saine dès que le bras réel ne retient rien en génération 1 (B9 : B4 n'est pas corrigé de bout en bout). Il faut du code
`_v62`, un brouillon 3 (couples T19 à T63 ci-dessous) et une troisième contre-lecture.

## 0. Fichiers lus, empreintes vérifiées, ce qui a été rejoué

| fichier (depuis `orchestrator/`) | sha256 vérifié |
|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon2.md` | `37ae595f95bb0e0d4777b3ae469aad5f7b270eb8a8b9c30d86da78f3d38b999f` (= rapport de rédaction) |
| `prereg/rapport-redaction-tour-ferme-v2.md`, `prereg/contre-lecture-preenregistrement-tour-ferme-v1.md` | lus en entier |
| les huit fichiers de code de la section 3 du rapport (`pole/tour_ferme_v61.py`, `demonstrations/tour_ferme_v61.py`, `pole/lecture_tour_ferme_v61.py`, `pole/reserve_tenue_a_l_ecart_v61.py`, `essais/test_v61_*.py`, `essais/mutations_v61.py`) | les huit empreintes du rapport, toutes égales |
| `pole/a_blanc_v59.py`, `pole/boucle_fermee_v59.py`, `pole/proposeurs_references_v59.py`, `pole/oracle_tour_ferme_v60.py`, `pole/cycle.py` (`appliquer_multiplicite`), `pole/tests_de_mort_v5.py` (`executer_tests_de_mort`, `verdict_du_noyau_v5`), `demonstrations/attaque_goodhart_v2.py` (fonctions importées), `pole/etage_entre_generations_v56.py` et `_v57.py`, `pole/adaptateurs_v56.py` (portes), `pole/configuration_v55.py` (`verifier_go_v55`), `pole/selection_pari.py` (`valider_loi`) | lus |
| script du brouillon 2, `…/scratchpad/tf61/construire_brouillon2.py` | `be658260b7d95aa90054f04141caceac4e5024eb1d185eb6d3356c38c1bfdf14` (= rapport) |
| relevé et manifeste de la répétition à blanc, `…/scratchpad/tf61/blanc1/` | `d1bc9283…` et `21d4d8b7718a38dd7110df596ce2833659f0c582b6a30cdc8c7678c915d6930f`, sceaux justes |

Rejoué :

- `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v59_*.py essais/test_v60_*.py essais/test_v61_*.py` :
  **110 réussis** (57 s). `nice -n 10 python3 -I -B essais/mutations_v61.py` : **15 tuées sur 15** pour la raison attendue, témoin
  28 essais avant et après (1 s).
- **Construction du brouillon 2** rejouée hors du dépôt (liens vers `pole/`, `demonstrations/`, `exemples/`, copie du brouillon 1
  `09b9dfcc…`) : sortie d'empreinte `37ae595f…`, **égale à l'octet** ; les 18 `replace` hors boucle du script, sans contrôle de compte,
  ont tous agi une fois. Les défauts du brouillon 2 sont donc dans ce qui n'a pas été remplacé.
- **Lecture gelée v61 rejouée sur le relevé à blanc** : « tient », A4 « discrimine », Newcombe [0,147 ; 0,469] — et **S1 « trop beau »
  déclenché**, ce que ni le texte ni le rapport ne disent (mineur 18).
- **Les 60 consignes d'expérimentateur** écrites par la répétition à blanc (`…/tf61/blanc1/**/experimentateur/traces-tour-*/consigne.md`)
  ont été lues : **aucune** ne contient un paramètre de loi (`"poids"`, `"biais"`, `"composantes"`, `"base"` : 0 sur 60) (B7).
- Sondes de ce contre-lecteur, dans `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/cl2-tour-ferme/` :
  - `demonstrations/tour_ferme_v61.py …/cl2-tour-ferme/sonde-illisible --etage 1 --a-blanc --graine 7 --bac factice --scenario-proposeur illisible`
    (5 s) : lecture v61 → **« ne tient pas (T1) »** (B9) ;
  - `sonde_b4_coeur.py` (sha256 `13012ed1e6360e5b43e8fa10b8bdad3dcd8f8993fc525707424f21ab03742b93`), vrai cœur v61, proposeurs
    scriptés muets en générations 1 et 2, sortie `…/cl2-tour-ferme/sonde-b4-g12/` : recopie jouée en génération 3 seulement, 7 passes,
    T2 vrai, **T1 faux → « ne tient pas (T1) »** ; muets en génération 1 seulement (`…/sonde-b4/`) : « tient » (B9) ;
  - `sonde_panne_session.py` (sha256 `fc4941000ed31b297a02fabd2283c72d65ce725d80c6ac6fea3f6cb4a80d2670`), une session de
    l'expérimentateur rend le statut « erreur » : **code de sortie 1**, `EtageInterrompu` non rattrapée, aucun relevé scellé
    (`…/sonde-panne/` ne contient que `manifeste.json` et `bras-reel/`) (I10) ;
  - `couples_cl2.py` (sha256 `98e80775a4f64e4922fdeba2449d77cfeff25afb2cef1e598341886672ad4edd`) : les 45 couples de la section 9,
    chaque cible présente **une fois** dans le brouillon 2 et encore une fois au moment de son application ; 16 marqueurs avant et
    après ; texte obtenu `d472ee7b…`.

## 1. Constats

Numérotation à la suite de la première contre-lecture (B7…, I10…, mineurs 11…).

### Bloquants

**B7 — La loi éprouvée n'est jamais servie à l'expérimentateur réel.** Les fiches de l'étage sont faites des seuls
`A.CHAMPS_FICHE` (`pole/a_blanc_v59.py:61` ; `pole/tour_ferme_v61.py:359-360`) : titre, hypothèse, prédiction, signe, métrique,
test de mort. La clé `extraits.loi_predictive` du préenregistrement court porte {métrique, prédiction, signe}, pas la loi ; le texte
du test dit « le log-score de la loi » sans la donner. À blanc, l'expérimentateur scripté reçoit la loi **hors bande** : le lanceur
remplace `T.jouer_etage` pour remplir `AdaptateurEtageBlanc.lois` (`demonstrations/tour_ferme_v61.py:225-236`), puis
`AdaptateurAblanc.lancer` écrit le script depuis `self.lois[ident]` (`pole/a_blanc_v59.py:276-281`). En mode réel,
`AdaptateurEtage.lancer` ne fait que transmettre la consigne (`demonstrations/tour_ferme_v61.py:206-210`). Preuve : 0 consigne sur 60
porte un paramètre de loi. Conséquence : Kimi ne peut pas calculer la statistique ; soit il n'écrit pas `gains.csv` (« non concluant »
partout : T2 et T4 manquent), soit il écrit des gains d'une loi devinée (désaccord du contre-calcul : arrêt, garde 10). Même servie,
une loi ne suffit pas : l'expérimentateur doit l'évaluer exactement comme `selection_pari.proba` (types `si_sinon`,
`par_sous_population`, `transformee`, plancher 10⁻¹²) à 10⁻⁶ près ; il faut lui servir aussi l'évaluateur de référence. Borne : le
champ `test` d'une fiche fait au plus 3 000 caractères (`pole/tests_de_mort_v2.py:129`) ; une loi complexe peut dépasser. Code C8,
couple T27.

**B8 — La grammaire des lois n'est pas servie aux proposeurs réels.** La consigne (`pole/tour_ferme_v61.py:72-76`) et le gabarit du
contexte (`:266-268`) ne donnent que les noms de types ; `selection_pari.valider_loi` exige des champs précis, en français (`poids`,
`biais`, `probas`, `composantes`, `lois`, `condition`, `sinon`, `base`, `puissance`, `inclinaison`…) (`pole/selection_pari.py:179-236`).
En génération 1, la vue est vide : aucun exemple. Les proposeurs scriptés écrivent des softmax valides par construction
(`pole/tour_ferme_v61.py:229-237`). Conséquence : refus massifs au gardien pour le bras réel seul (P8, S5), un bras réel réduit à ce
qu'il devine du format ; A2 et A4 ne se lisent plus. Code C9, couples T23 et T24.

**B9 — B4 n'est pas corrigé de bout en bout : T1 manque sur une course saine dès que le bras recopie ne joue pas en génération
g ≥ 2.** Le cœur consigne la lecture de l'héritage **avant** de décider que la recopie ne joue pas (`pole/tour_ferme_v61.py:536`,
puis `:540-544`) ; la lecture n'attend de lecture que pour les générations jouées (`pole/lecture_tour_ferme_v61.py:136-139`). Sondes
sur le vrai cœur : bras réel muet en générations 1 et 2 (le cas B4 exact : recopie en génération 3 seulement, 7 passes) →
**« ne tient pas (T1) »** ; bras réel muet partout → idem. L'essai v61 `test_B4_recopie_en_generation_3_seule_sept_passes_tient`
passe parce que sa fixture n'écrit de lecture que pour les générations jouées (`essais/test_v61_lecture_tour_ferme.py:38`), ce que
le cœur ne fait pas. Le scénario est prévu par le texte (P6 « ouverte » vers PS réel ≤ 0,15) : la porte refuserait alors l'étage 2
pour un défaut de « boucle » qui n'existe pas, et la phrase N1 le dirait au mentor. Code C10, couples T29 et T43.

### Importants

**I10 — Arrêts non scellés, refus de modèle tu.** Le lanceur ne rattrape que `ArretTour` et `TourRefuse` après l'écriture du
manifeste (`demonstrations/tour_ferme_v61.py:392-405`) ; le cœur ne convertit que l'héritage refusé en cours de boucle
(`pole/tour_ferme_v61.py:533-535`). Sortent en **code 1, sans relevé scellé** : `EtageInterrompu` (session de l'étage ≠ « ok »,
refus de modèle R-764 : `pole/tests_de_mort_v5.py:383-412`), `VueAvecVerdict`, `BacASableIndisponible` (exécuteur refait à chaque
génération), `HeritageRefuse` à la lecture finale (`pole/tour_ferme_v61.py:557-561`). Sonde : statut « erreur » → code 1. Côté
proposeurs, `ProposeurAdaptateur.proposer` rend `""` pour tout statut autre que « ok » (`:255`) : un refus R-764 (modèle servi
inconnu) ou une panne devient « réponse illisible », zéro carte, course poursuivie — la garde 13, dite « existe » au texte (l. 424),
ne protège pas le chemin du tour. Le texte promet « sortie scellée telle quelle, code 3 » (l. 427). Code C12, couple T42.

**I11 — Le texte dit trois choses différentes d'un désaccord du contre-calcul et d'une session en échec.** Section 3 (l. 94) : ce
sont des « non concluant » ; 4.6 T4 (l. 228) : un désaccord arrête la course ; section 7, garde 10 (l. 421) : « non concluant », audit
S1. Le code arrête (`pole/tour_ferme_v61.py:375-378`) et l'étage v5 arrête sur une session en échec. Une lecture gelée doit dire une
seule chose. Couples T40, T42, T63.

**I12 — Devis et plafonds : la part de Kimi dépasse la porte de son relais.** (a) Le lanceur donne à la porte de chaque relais la
moitié du plafond, 7,5 USD (`demonstrations/tour_ferme_v61.py:194`, recopié de l'attaque de Goodhart où les deux rôles sont
symétriques). Avec D9, Kimi (proposeur et expérimentateur) porte ≈ 2,6, ≈ 7,8 et ≈ 11,6 USD à 2, 4 et 6 tours par carte (prix I7 :
0,04 puis 0,06 USD par tour ; totaux 3,34, 8,46, 12,3 USD, ceux du texte), Argon ≈ 0,7 USD : Kimi passe 7,5 USD dès 4 tours. Son
relais répond alors « budget_depasse » (HTTP 402, `pole/adaptateur_kimi_v53.py:131`), que l'étage v5 prend pour le plafond de la
fiche (`pole/tests_de_mort_v5.py:409-410`, `:477-479`) : les cartes suivantes deviennent « non concluant » (T4 menacé) sans arrêt, et
un proposeur Kimi rend zéro carte. (b) Le compteur ne vérifie qu'après chaque étage (`pole/tour_ferme_v61.py:368`) : le plafond dur
réel est celui des relais (registre cumulé, `--plafond-cumule-usd` remplacé par 15, `demonstrations/attaque_goodhart_v2.py:247-249`).
(c) Le GO doit porter **exactement** le plafond de l'étage (`pole/configuration_v55.py:96-98`) ; la section 14 dit « plafonds 12 + 5
USD » (l. 674). Un seul `go` et une seule `configuration_sha256` au plan ne peuvent servir l'étage 1 (15 USD) et l'étage 2 (5 USD) :
`roles_reels` refuse une configuration dont `budget.plafond_usd` diffère du plafond de l'étage (`demonstrations/tour_ferme_v61.py:186-188`).
Code C13, couples T35, T51, T62.

**I13 — Marqueurs D2 à D6 placés dans ce que voient les proposeurs** (l. 54-55) : « le gabarit (décisions, références du registre à
porter : D2 … <<DECISION_D6>>) (types de loi permis…) ». Rempli, le texte gelé par D1 dirait que les proposeurs reçoivent les
décisions de Lazar. Couples T23 et T56 à T60 (marqueurs déplacés en section 14, même ensemble de 16 marqueurs).

**I14 — Contre-calcul à 10⁻⁶ absolu sur un script écrit par un modèle.** Un `gains.csv` arrondi à 4 décimales donne sur la moyenne
une erreur d'écart-type ≈ 1,4·10⁻⁶ à n = 400 : à peu près une carte sur deux déclencherait l'arrêt de toute la course. Le gabarit du
test ne demande aucune précision. Il faut exiger la pleine précision et servir l'évaluateur de référence (C8, C14, couple T27), puis
choisir : arrêt (code actuel) ou carte « non concluant (contre-calcul) » comptée en T4 (choix de conception, à trancher par le
rédacteur ou Lazar ; le texte suit le choix).

**I15 — L'expérimentateur n'est aveugle ni au bras ni aux témoins.** Il lit `nom : témoin` (`pole/tour_ferme_v61.py:157-162` ; vu
dans les consignes), « Référence aléatoire n° k », « Référence recopie ou mélange … (copie de G1-kimi-03 …) », et des identifiants
`G1-kimi-01`. Le texte dit les témoins « mêlés anonymement » (l. 127). Un « non concluant » d'un bras compte comme non promu puis
survivant : un effort inégal de Kimi selon le bras déplacerait r_réel − r_aléatoire. Code C15, couples T25, T34.

**I16 — P4 n'est pas une borne haute sous D7 quand l'archive réelle reste vide.** Sous D7, le bras aléatoire est jugé contre
l'archive du bras réel : si elle reste vide, sa part reste ≈ 0,122 par carte sur les trois générations (binomiale (36 ; 0,122) :
P(≥ 7) ≈ 0,14, contre 0,003 sous l'archive propre de L2b). « Se lit comme borne haute » n'est écrit qu'en section 10 (l. 471),
pas dans P4 (l. 181), dont le code teste une bande [1 ; 6] (`pole/lecture_tour_ferme_v61.py:41-42`, `:176-177`) ; P4 n'a pas de
clause « ouverte ». Couples T28, T49 ; code C16.

**I17 — Bras réel sans carte jugée : A4 dit « le bras aléatoire promeut autant que le bras réel ».** Newcombe vaut `None` si
n_réel = 0, et le code tombe dans la branche « égal » (`pole/lecture_tour_ferme_v61.py:157`, `:167-169`) ; la porte n'exige d'ailleurs
aucune carte réelle jugée (avec B8, cas probable). Couple T31 ; code C16 (« non mesurable »).

**I18 — Le point (3) de S1 n'est pas fait par le code.** Le relevé porte `recherche_loi_plantee: []` en constante
(`pole/tour_ferme_v61.py:568`) ; la lecture le recopie (`pole/lecture_tour_ferme_v61.py:190`). Une liste vide se lit « rien
trouvé » alors que rien n'a été cherché ; le texte dit ce point fait « à chaque course » (l. 388). Couple T33 ; code C16.

**I19 — Garde 6 : le cas sain complet n'est jamais essayé.** `Garde6` (`essais/test_v61_tour_ferme.py:63-85`) essaie le plan et
trois artefacts de chemin ; ni un texte scellé accepté, ni un sceau faux, ni un marqueur restant, ni une empreinte de code
différente, ni l'entropie < 2⁶⁴ (`demonstrations/tour_ferme_v61.py:133-166`). Le premier verrou du chemin réel n'a jamais passé.
Code C17, couple T36.

**I20 — Aucune commande ni aucun programme ne produit la lecture scellée** qu'exige la garde 12 (`lire_lecture_etage_1`) : la
lecture v61 est une bibliothèque qui prend le champ `releve` du rapport. Couple T46 ; code C18.

**I21 — Section 13 : « ne substitue aucun plafond » est faux** (l. 537-538) : `substituer_commandes` remplace aussi la valeur de
`--plafond-cumule-usd`, et le lanceur transmet un plafond d'étape à chaque porte. Couple T53.

**I22 — Machine jetable neutralisée en mode réel.** `ENV_ETAGE = dict(A.ENV_A_BLANC)` (`pole/tour_ferme_v61.py:77`) est passé à
`jouer_etage_v57` dans les deux modes (`:366`) : `exiger_machine_jetable_v56` (`pole/etage_entre_generations_v56.py:33-48`) vérifie
alors un dictionnaire constant qui déclare `POLE_MACHINE_JETABLE_V56=1`, au lieu de l'environnement du processus que la v8 lui passe
(`demonstrations/ideation_v8.py:110`). R-640 (machine louée jetable, sans secret) et la liste blanche (CL20-14) ne sont pas vérifiées ;
seule l'absence de variables de clé l'est (`demonstrations/tour_ferme_v61.py:180-183`). Hors de la liste d'arrêt. Code C11, couple
T43 (garde 15).

**I23 — D4 : le texte et le code divergent.** Le bras réel joue avant la recopie dans la génération g ; la recopie lit
`etat["reel"]`, déjà à jour (`pole/tour_ferme_v61.py:530`, `:555`) : elle recopie les lois retenues **jusqu'à g compris** et ses
cartes sont jugées contre l'archive après g. Le texte (l. 122-126) dit « jusqu'à g−1 » et « le même nul que les cartes réelles de
la même génération ». Recommandé : aligner le code sur le texte (C19), ce qui donne le même nul aux trois bras de la génération g,
comme D7 le fait déjà pour le bras aléatoire.

**I24 — Le monde planté n'est pas gelé.** `exemples/temoins-pari-demo-v1.json` (L*, témoins, oracle ; sha256 `fdf4d5c1…`, cité
l. 109 et égal sur disque) n'est pas dans le bloc des empreintes, et le lanceur ne compare pas `monde["sha256"]` au texte. Code C20.

### Mineurs

11. **Heures fausses.** En-tête (l. 3) « brouillon 2 … de 09:30 à 11:10 UTC » et L2b-v61 « ≈ 10:40 » (l. 471) : la répétition à
    blanc a couru de 09:10:08 à 09:11:40 UTC (manifeste, relevé), le brouillon 2 a été écrit à 09:23 UTC, le commit `7d3aa82` est de
    09:25 UTC, et 11:10 UTC n'était pas encore passé à l'heure de cette contre-lecture. Couples T19, T47.
12. **Passages périmés** : section 1 (l. 40-44 : lanceur « à écrire », lecture v60) ; section 14 (l. 669 : « code `_v60` »).
    Couples T20, T21, T61.
13. **« Identifiant opaque »** (l. 52) : `G<g>-<proposeur>-<nn>` dit la génération et l'auteur. Couple T22.
14. **Mémoire du bac** : 768 Mo tenus par l'exécuteur, 1 024 Mo annoncés dans la consigne de l'étage (quota par défaut). Couple T26.
15. **Effet d'un arrêt** : T4 n'est pas manqué par un arrêt (les cartes de la génération arrêtée ne sont pas au relevé) ; seul T1
    l'est (l. 228). La phrase N1 dirait « did not pass its own gate » pour un arrêt de budget. Couples T30, T32.
16. **S5** parle du « gardien modèle » (l. 405), retiré par D9. Couple T34.
17. **Préfixe des tâches** : le texte dit `tour-ferme-v1|…` (l. 435), le code `tour-ferme-v61|…` (`pole/tour_ferme_v61.py:394`).
    Couple T44. La graine publique (mineur 7 de la contre-lecture 1) n'est pas écrite : couple T45.
18. **L2b-v61** : S1 s'y déclenche (non dit) ; le bras aléatoire y est jugé en génération 1 contre une archive vide, pas « contre
    l'archive réelle informative ». Couples T48, T49.
19. **`vd_distinctes`** : champ vide en constante (`pole/tour_ferme_v61.py:568`) ; à calculer avant scellement ou à retirer, jamais
    après lecture. Couple T50.
20. **Phrase de tête des empreintes** (l. 565-566) : à mettre à jour (vérifiées à `7d3aa82`). Couple T54.
21. **`moteur="simule"` en mode réel** (`demonstrations/tour_ferme_v61.py:350`). Dans l'étage v5, `moteur` ne sert qu'à deux choses
    (`pole/tests_de_mort_v5.py:279-280`, `:309`) : refuser un exécuteur factice avec le moteur réel, et écrire `cout_fictif`.
    Effets : chaque `manifeste-tests-de-mort.json` d'une course payante écrira `cout_fictif: true` (étiquette fausse au dossier), et
    la défense de l'étage contre l'exécuteur factice est éteinte — compensée par le lanceur (`--bac reel` exigé, `choisir_executeur`
    sans repli). Aucun effet sur le verdict. Code C21.
22. **Durée** : vérifiée entre deux appels de proposeur et après chaque étage ; un étage en cours (jusqu'à 12 cartes × 12 tours) n'est
    pas interrompu. Dit par le couple T42.
23. **`--verifier-seulement`** annonce « aucun appel, aucune écriture », mais `roles_reels` a déjà relancé les portes des relais à
    plafond/2 (`demonstrations/tour_ferme_v61.py:194`) et créé un dossier de sessions temporaire jamais retiré.
24. Propositions au-delà de 6 par proposeur ignorées sans compte (`pole/tour_ferme_v61.py:407`) ; le contre-calcul lit la copie de la
    tranche sans en vérifier l'empreinte contre l'index (`:369`).
25. **Pour l'étage 2** (version suivante) : T2-CONNU promu n'a aucune conséquence écrite (`pole/lecture_tour_ferme_v61.py:234`) ; la
    recherche des traits de T par chaîne arrondie à 4 décimales (`pole/reserve_tenue_a_l_ecart_v61.py:57-67`) ne voit rien si le
    contexte écrit 6 décimales (comparer des nombres, pas des chaînes) ; en mode réel, les gardes 12 et 11 de l'étage 2 sont
    inatteignables avec un seul `go` et une seule configuration (refus au GO avant elles).

## 2. Couverture de la première contre-lecture

| constat | état dans le brouillon 2 et le code v61 |
|---|---|
| B1 | Code de l'étage 1 écrit, essayé, banc 15/15, à blanc dans le vrai bac : **oui**. Mais le chemin réel n'est pas essayé et ne marche pas (B7, B8) ; garde 6 sans cas sain complet (I19) ; table de la section 7 non mise à jour (l. 416-425). Étage 2 non écrit, dit (l. 560-563). |
| B2 | Défaut Q nommé (l. 296) ; E0, R, T, M2, V en marqueurs : **oui**. |
| B3 | Cause lue à l'oracle (`pole/lecture_tour_ferme_v61.py:156-169`), phrase de Lazar mot pour mot, génération 1 à côté : **oui** ; reste I17 (n_réel = 0). |
| B4 | Passes comptées sur le journal (`:128`, `:140`) : **oui** pour T2 ; **non de bout en bout** : T1 manque dans le même scénario (B9). |
| B5 | `exiger_contre_calculs` (`:74-79`), N1 par `lire_tour`, N2 à l'étage 2 : **oui**. |
| B6 | T13 à T17 appliqués (l. 365-380) : **oui** ; N1 pour un arrêt (mineur 15). |
| I1 | T7 (adapté), T8 : appliqués ; P4 mal conditionnée sous D7 (I16). |
| I2 | D8 au texte (l. 324) et au plan ; lu et vérifié, utilisé par aucun code (étage 2 non écrit). |
| I3 | `reserve_tenue_a_l_ecart_v61` écrit et essayé (6 essais, 3 mutations) ; non branché (étage 2). |
| I4 | T10, T11 : appliqués (l. 307, l. 346). |
| I5 | T1, T3, T4 de la porte (`:136-152`) : **oui** ; mais B9. |
| I6 | D9 « mecanique » ; « aiguilleur » refusé avant tout appel (`pole/tour_ferme_v61.py:110-111`) : **oui**. |
| I7 | Plafond 15 USD (C7, sans relevé) : **oui** ; part des relais (I12). |
| I8 | T12 en forme D9 (l. 487) : **oui**. |
| I9 | S2 « les cinq points de S1 », tête de section 6 : **oui** ; point (3) de S1 non fait par le code (I18). |
| Mineurs 1 à 10 | 1, 2, 3, 4, 5, 6, 8 : oui. 7 (graine publique) : non écrit (T45). 9 (calibrage réduit) : à moitié (« ajusté sur la seule partie calibrage », l. 324, sans « réduite des tâches réservées ») ; étage 2. 10 : champ vide (mineur 19). |
| T1 à T18 | Tous présents dans le brouillon 2 (construction rejouée à l'octet) ; T7 adapté (P4 à 6 sur 36), T12 en forme D9. |
| C1, C2 | `lecture_tour_ferme_v61` : oui, sauf B9, I17, I18. |
| C3 | Essai « contre-calcul absent → Z » inversé (N) ; 5 mutations demandées présentes (`essais/mutations_v61.py:31-43`) : oui. |
| C4 | Oui (orthographe, forme normalisée, identifiants et traits, disjonction) ; non branché (étage 2). |
| C5 | Témoins hors famille (`pole/tour_ferme_v61.py:291-300`), D7 (`:545-548`), ordre des bras (`:65`), gardien mécanique, passes au relevé, manifeste (commit, Python, numpy, bwrap, ordre, décisions : `:574-593`) : oui. D8 de l'étage 2 : non écrit. |
| C6 | L2b-v61 : une répétition (dit) ; 5 racines non faites (dit). |
| C7 | Relevé impossible (journaux privés) ; plafond 15 : oui. |

## 3. Le code de l'étage 1, point par point

- **Fuites de la réserve** : l'étage 1 ne touche pas T. Le lanceur, en étage 2, vérifie la porte puis `verifier_reserve` (v60) et
  refuse (`demonstrations/tour_ferme_v61.py:354-360`) ; les gardes v61 (`fuites_dans`, `verifier_disjonction`,
  `verifier_orthographe`) ne sont appelées nulle part. Rien à redire pour l'étage 1 ; tout à brancher pour l'étage 2.
- **Ordre réel → recopie → aléatoire** : respecté (`pole/tour_ferme_v61.py:65`, `:524`) ; mais la recopie lit le bilan réel de la
  même génération (I23).
- **e-BH à m = 19, témoins hors famille** : conforme à `cycle.appliquer_multiplicite` (`pole/cycle.py:741-779`) ; le seuil m/α
  des témoins est celui du témoin vrai de `cycle` (`pole/tour_ferme_v61.py:289-300`).
- **Contre-calcul hors du bac** : fait depuis la copie de l'orchestrateur et la loi gelée (`:313-345`), formule identique au script
  scripté (plancher 10⁻¹², comptes + 0,5) ; tolérance et précision (I14) ; empreinte de la copie non vérifiée (mineur 24).
- **Plafond et durée** : `Compteur` (`:115-137`), vérifié après chaque appel de proposeur et chaque étage (I12, mineur 22).
- **Refus avant tout appel** : chemin réel — dossier de sortie, bac, texte scellé (garde 6), plan, configuration (empreinte et
  plafond), GO (montant exact), variables de clé, adaptateurs, familles, sonde du bac — tous avant le premier appel de modèle. Manquent
  la machine jetable (I22) et la précision : les portes des relais sont relancées avant (mineur 23).
- **Refus de l'étage 2** : à blanc et réel, avant tout appel (`:354-362`) ; voir mineur 25 pour l'ordre réel.
- **`moteur="simule"` en mode réel** : mineur 21.
- **`vd_distinctes`** : non calculé (mineur 19).

## 4. Bloc des empreintes du code gelé

**Conforme à `7d3aa82`.** 83 lignes ; mêmes noms, même ordre que `FICHIERS_GELES` (`demonstrations/tour_ferme_v61.py:60-79`) ;
chaque empreinte égale à celle du fichier de l'arbre de travail **et** de `git show 7d3aa82:orchestrator/<fichier>` ; tous suivis à
`7d3aa82`. Fermeture : les imports paresseux du chemin réel (`pole.relais`, `pole.adaptateur_kimi_v53`, `pole.adaptateurs_v56`,
`pole.dossier_ferme`, `pole.ideation_v2`, `pole.configuration_v56`, `pole.tests_de_mort_v5`…) sont tous dans le bloc ; aucun module
importé hors du bloc. Restent : la phrase de tête (mineur 20) et le monde planté hors du bloc (I24). Tout code v62 rend ce bloc caduc.

## 5. Lecture gelée et issues

- **Deux sens (R4)** : S1 (trop beau) et S2 (trop laid) ont le même audit en cinq points, S2 un peu plus ; S3 et S4 de même profondeur ;
  S5 pour l'asymétrie. Le code calcule S1, S2, S5 (`pole/lecture_tour_ferme_v61.py:184-193`) ; le point (3) de S1 n'est pas fait (I18) ;
  S5 ne regarde pas le « non concluant » par bras (I15, T34). Prédictions : toutes « ouvertes » sauf P4 (T28).
- **P4 « borne haute »** : écrit seulement en section 10 (l. 471), pas dans P4 (l. 181) ni dans le code (bande [1 ; 6]) ; et faux
  si l'archive réelle reste vide (I16). P4 doit s'écrire par cas (T28), et la lecture v62 la lire par cas (C16).
- **Issues** : T5 / Newcombe / cause à l'oracle conformes au texte ; B9 et I17 faussent deux issues prévisibles ; N1 pour un arrêt
  (mineur 15).

## 6. Décisions D2 à D9 : paramètre lu dans le texte scellé, ou code ?

| décision | paramètre du plan gelé ? | où |
|---|---|---|
| D2 (définitions, g₀) | **non** : code gelé | `pole/oracle_tour_ferme_v60.py:32-33`, `:132-143` |
| D3 (témoins jamais retenus ni servis) | **non** : code gelé | `pole/tour_ferme_v61.py:446-449`, `:500-505` |
| D4 (recopie nourrie par le bras réel) | **non** : code gelé (et texte ≠ code, I23) | `pole/tour_ferme_v61.py:530` |
| D5 (T entier, génération 1 décisive) | **non** : lecture gelée ; cœur de l'étage 2 absent | `pole/lecture_tour_ferme_v61.py:231-232` |
| D6 (contrôle aléatoire à l'étage 2 ; pas de seconde réplique) | **non** : code gelé (un seul bras aléatoire) | `pole/tour_ferme_v61.py:65` ; `pole/lecture_tour_ferme_v61.py:38` |
| D7 | **oui** : `d7`, lu, vérifié, utilisé | `demonstrations/tour_ferme_v61.py:121` ; `pole/tour_ferme_v61.py:545-548` |
| D8 | lu et vérifié, **utilisé par aucun code** | `demonstrations/tour_ferme_v61.py:121` |
| D9 | **oui** : `d9`, « aiguilleur » refusé avant tout appel | `pole/tour_ferme_v61.py:110-111`, `:190-194` |

Un refus de D2 à D6 exige donc un code nouveau, pas seulement un texte nouveau (couples T52, T55). Le plan pré-remplit `d7`, `d8`,
`d9` aux valeurs recommandées : si Lazar choisit l'autre valeur, la ligne du plan change avec la phrase.

## 7. Portée de scellement (décision de Lazar ; les deux listes, sans choisir)

**A. Sceller l'étage 1 seul.**

1. Code `_v62` : C8 à C22 (au moins B7, B8, B9, I10, I12, I14, I22, I23 ; le reste selon les couples), essais, banc, répétitions à
   blanc où les rôles scriptés ne reçoivent que ce que reçoivent les modèles (5 racines).
2. **Lanceur à plan d'étage 1** : le `lire_plan` v61 exige les 17 clés, dont `generations_etage_2`, `m_e_bh_etage_2`,
   `plafond_etage_2_usd`, `duree_etage_2_h`, `d8` et un `reserve_manifeste_sha256` hexadécimal (`demonstrations/tour_ferme_v61.py:80-82`,
   `:107-108`, `:122-123`) : un texte d'étage 1 seul ne passe pas le lanceur v61 sans empreinte factice (à refuser). Nom du texte : celui
   qu'attend `NOM_PREREG` (`:52`), ou un nom neuf accepté par le lanceur v62.
3. **Texte scindé**, sections gardées : 0 (réécrite pour un étage), 1, 2, 3, 4 (4.1 à 4.7), 6 (S1, S2, S5), 7 (gardes 1 à 10, 13, 14,
   15 ; la garde 12 devient « aucun étage 2 sous ce texte » ; la garde 11 sort), 8 (sans la partition de l'étage 2), 9 (à blanc, essais,
   étage 1 réel, lecture gelée), 10 (L0 à L3, L2b, L2b-v61, nouvelles répétitions ; L4 sort), 10 bis, 11 (étage 1, et « étage 2 hors de
   ce texte »), 12 (étage 1), 13 (code v62, plan d'étage 1), 14 (D1, D2, D3, D4, D6 pour sa seule partie « pas de seconde réplique », D7,
   D9). Sortent : la section 5 entière (5.1 à 5.6, P9, P10, phrases P, Z, N2), S3, S4 ; une phrase au mentor pour l'issue de l'étage 1
   seul (A2, A4) est à écrire, N1 reste.
4. **Marqueurs à remplir** : `<<DECISION_D2>>`, `<<DECISION_D3>>`, `<<DECISION_D4>>`, `<<DECISION_D6>>`, `<<DECISION_D7>>`,
   `<<DECISION_D9>>`, `<<CASE_CONFIGURATION_V3>>` (configuration de l'étage 1, `budget.plafond_usd` = 15), `<<CASE_GO>>` (GO à exactement
   15 USD). **Marqueurs qui sortent avec l'étage 2** : `<<DECISION_D5>>`, `<<DECISION_D8>>`, `<<CASE_Q>>`, `<<CASE_E0>>`, `<<CASE_R>>`,
   `<<CASE_T>>`, `<<CASE_M2>>`, `<<CASE_V>>` (deux occurrences : case V et plan).
5. Contre-lecture R2 neuve du texte et du code v62, scellement, commit et poussée avant la course. L'étage 2 devient un préenregistrement
   à part (son texte, son code, son GO à 5 USD), dont la porte lit la lecture scellée de l'étage 1.

**B. Sceller les deux étages ensemble.**

1. Tout le point A pour l'étage 1.
2. Cœur de l'étage 2 écrit et essayé : juge à plan plein avec membres d'archive (variante sans `verifier_archive_vide`), constructeur
   de M2 (`verifier_disjonction`, `verifier_orthographe`), test de mort contre le prédicteur connu (D8) et son contre-calcul, loi et
   évaluateur servis à l'expérimentateur (B7), grammaire de la banque servie aux proposeurs (B8 : 4 traits, moniteur, 2 ou 3 issues),
   garde 11 sur chaque contexte servi (traits comparés en nombres), T monté dans le seul bac de l'étage 2, témoins T2-CONNU et T2-MAL
   avec leurs conséquences écrites, bras aléatoire de contrôle, garde 12 essayée de bout en bout ; essais, banc, répétition à blanc
   sur une banque synthétique.
3. Les 16 marqueurs remplis : D2 à D9, Q (empreinte), E0, R, T, M2, V (module et manifeste), configuration, GO.
4. **Plan par étage** : `configuration_sha256_etage_1/2` et `go_etage_1/2` (le GO exige le montant exact de chaque étage ; la
   configuration, son plafond).
5. Section 5 mise à jour (« variante `_v60` à écrire », calibrage réduit des tâches réservées) ; bloc des empreintes couvrant l'étage 2 ;
   contre-lecture R2 neuve des deux étages.

## 8. Devis

Arithmétique juste : 102 appels et ≈ 3,3 USD à 2 tours ; 8,4 et 12,2 USD se retrouvent avec le prix de 0,06 USD par tour de I7, que
le texte ne dit pas (T51). Plafond de l'étage 1 à 15 USD cohérent avec C7 ; mais le plafond qui mord est la porte de Kimi à 7,5 USD,
dépassée dès 4 tours par carte, avec une dégradation silencieuse en « non concluant » (I12). Étage 2 : ≈ 60 appels, 1,5 à 2 USD,
plafond 5 USD, cohérent ; il lui faut son GO et sa configuration (I12 c). Total 5 à 14 USD sous plafonds 15 + 5 : cohérent une fois
la part des relais fixée au plan.

## 9. Remplacements (brouillon 2 → brouillon 3)

Chaque cible « remplacer » figure exactement une fois dans le brouillon 2 (`37ae595f…`) ; appliqués dans l'ordre, chacun figure encore
une fois au moment de son application ; les 16 marqueurs sont conservés (vérifié par `couples_cl2.py`, section 0). Ces couples
supposent le code v62 de la section 10 ; ceux qui citent « v62 » décrivent ce code.

**T19** — en-tête : heures fausses (mineur 11)

remplacer :

~~~~text
brouillon 2 le 2 novembre, de 09:30 à 11:10 UTC environ, par
~~~~

par :

~~~~text
brouillon 2 le 2 novembre, achevé à 09:23 UTC (fichier écrit à 09:23, commit `7d3aa82` à 09:25 UTC ; les heures « 09:30 à 11:10 » du rapport de rédaction sont fausses), par
~~~~

**T20** — section 1 : lanceur dit manquant (mineur 12)

remplacer :

~~~~text
un lanceur à vrais modèles (`_v60`), des témoins exclus de
~~~~

par :

~~~~text
un lanceur à vrais modèles (écrit en `_v61` pour l'étage 1, section 13 ; cœur de l'étage 2 non écrit), des témoins exclus de
~~~~

**T21** — section 1 : lecture v60 (mineur 12)

remplacer :

~~~~text
la lecture gelée des deux étages (`pole/lecture_tour_ferme_v60.py`) : 46 essais,
~~~~

par :

~~~~text
la lecture gelée des deux étages (`pole/lecture_tour_ferme_v60.py`, remplacée pour ce texte par `pole/lecture_tour_ferme_v61.py`, section 4.6) : 46 essais,
~~~~

**T22** — section 2 : identifiant dit opaque (mineur 13)

remplacer :

~~~~text
(identifiant opaque et loi prédictive, rien d'autre)
~~~~

par :

~~~~text
(identifiant et loi prédictive, rien d'autre ; l'identifiant d'une carte réelle, `G<g>-<proposeur>-<nn>`, dit sa génération et son auteur)
~~~~

**T23** — section 2 : marqueurs D2 à D6 mal placés et grammaire non servie (B8, I13)

remplacer :

~~~~text
le gabarit (décisions, références du registre à porter : D2 définitions <<DECISION_D2>> ; D3 témoins jamais retenus ni servis <<DECISION_D3>> ; D4 recopie nourrie par l'archive du bras réel <<DECISION_D4>> ; D5 T entier, génération 1 décisive <<DECISION_D5>> ; D6 bras aléatoire de contrôle à l'étage 2, sans seconde réplique à l'étage 1 <<DECISION_D6>>)
   (types de loi permis, borne des poids)
~~~~

par :

~~~~text
le gabarit (types de loi permis **avec les champs exacts de chaque type, ceux de `selection_pari.valider_loi`, et un exemple valide par type**, borne des poids ; section 4.1)
~~~~

**T24** — 4.1 : grammaire servie aux proposeurs (B8)

remplacer :

~~~~text
  bornés à ±4). **L'orchestrateur complète**
~~~~

par :

~~~~text
  bornés à ±4 ; la consigne figée sert la grammaire exacte : champs de chaque type selon `selection_pari.valider_loi` et un exemple valide par type, chacun essayé par `valider_loi` ; v62). **L'orchestrateur complète**
~~~~

**T25** — 4.1 : témoins non anonymes pour l'expérimentateur (I15)

remplacer :

~~~~text
- **Témoins** (mêlés anonymement à chaque génération de chaque bras qui joue ; identifiants opaques ;
~~~~

par :

~~~~text
- **Témoins** (ajoutés à chaque génération de chaque bras qui joue ; identifiants opaques ; servis à l'expérimentateur sous le même titre et le même énoncé neutres que les cartes, sans bras ni statut de témoin, v62 ;
~~~~

**T26** — 4.1 : mémoire du bac (mineur 14)

remplacer :

~~~~text
un seul dossier, 768 Mo, filtre d'appels système
~~~~

par :

~~~~text
un seul dossier, 768 Mo tenus par le bac (la consigne de l'étage v5 annonce 1 024 Mo, quota par défaut de l'étage, non tenu), filtre d'appels système
~~~~

**T27** — 4.1 : loi éprouvée servie à l'expérimentateur, pleine précision (B7, I14)

remplacer :

~~~~text
seuil « au moins 0,02 ». **Expérimentateur** :
~~~~

par :

~~~~text
seuil « au moins 0,02 », valeurs écrites en pleine précision (`repr` de Python). **Loi servie** : la loi gelée de la carte (JSON canonique, borné en taille) et l'évaluateur de référence de la grammaire (le code du contre-calcul, fichier de la tranche, même empreinte pour toutes les cartes) sont servis à l'expérimentateur dans le préenregistrement court ; le mode à blanc ne lui passe rien d'autre (v62). **Expérimentateur** :
~~~~

**T28** — 4.3 : P4 écrite par cas sous D7 (I16)

remplacer :

~~~~text
- **P4 (bras aléatoire)** : part PS du bras aléatoire **entre 1 et 6 cartes sur 36** (L2, génération 1 seule, archive vide, m = 12 sans témoins : 0,125 ; aux conditions du plan, lecture L2b du contre-lecteur, trois générations, archive propre : 48/864 = 0,056, Wilson [0,042 ; 0,073], dont 0,122 en génération 1 et 0,023 ensuite ; sous la décision D7 « archive du bras réel », L2b-v61, une répétition : 0/36) ; P4 se lit : génération 1 entre 1 et 4 cartes sur 12, trois générations entre 1 et 6 cartes sur 36 (borne haute relevée d'une carte, marge de L2b) ; FD du bras aléatoire **≤ 1 carte sur 36** (L2 : 3 sur 1 200 = 0,0025).
~~~~

par :

~~~~text
- **P4 (bras aléatoire, sous D7 « archive du bras réel »)** : génération 1 (archive vide dans tous les cas) : PS **entre 1 et 4 cartes sur 12** (L2b : 35/288 = 0,122 par carte ; probabilité ≈ 0,78 ; 0 sur 12 a une probabilité ≈ 0,21). Générations 2 et 3, jugées contre l'archive du bras réel : ≈ 0 si elle porte une loi voisine de L* (L2b-v61, une répétition : 0 sur 24), ≈ 0,12 par carte si elle reste vide. Trois générations : **entre 1 et 6 cartes sur 36** si l'archive réelle est informative dès la génération 1 ; **entre 1 et 8** si elle reste vide (binomiale (36 ; 0,122) : P(≤ 8) ≈ 0,97, P(≥ 7) ≈ 0,14) ; L2b (archive propre, 0,056) n'est une borne haute que dans le premier cas. FD du bras aléatoire **≤ 1 carte sur 36** (L2 : 3 sur 1 200 = 0,0025). Ouverte : une part hors de la bande de son cas dirait que le juge ou le test de mort ne se comporte pas comme sur L2 et L2b ; rapportée, auditée (S2), non décisive.
~~~~

**T29** — 4.6 T1 : lectures attendues (B9)

remplacer :

~~~~text
(journal ; nombre de lectures égal au nombre attendu)
~~~~

par :

~~~~text
(journal ; une lecture vérifiée par génération g ≥ 2 de chaque bras, qu'il joue ou non : le bras recopie-mélange lit le bilan du bras réel même quand l'archive vide l'empêche de jouer ; attendu = lu ; lecture v62)
~~~~

**T30** — 4.6 T4 : effet d'un arrêt (mineur 15)

remplacer :

~~~~text
(un désaccord arrête la course, garde 10 : relevé partiel scellé, T1 et T4 manqués)
~~~~

par :

~~~~text
(un désaccord arrête la course, garde 10 : relevé partiel scellé, sans les cartes de la génération arrêtée ; T1 manqué par l'arrêt)
~~~~

**T31** — 4.7 point 4 : bras réel sans carte jugée (I17)

remplacer :

~~~~text
recopie-mélange sans aucune carte en générations 2 et 3 → « recopie non mesurable », dit à côté de l'issue.
~~~~

par :

~~~~text
recopie-mélange sans aucune carte en générations 2 et 3 → « recopie non mesurable », dit à côté de l'issue. Bras réel sans aucune carte jugée → issue A4 « non mesurable (aucune carte réelle jugée) », jamais « promeut autant » (lecture v62).
~~~~

**T32** — 5.6 : phrase N1 pour un arrêt (mineur 15)

remplacer :

~~~~text
N1 (étage 1) : « The closed loop did not pass its own planted-world gate ([criterion]); we did not run it on the real question. »
~~~~

par :

~~~~text
N1 (étage 1) : « The closed loop did not pass its own planted-world gate ([criterion]); we did not run it on the real question. » ; si T1 manque par un arrêt de la liste d'arrêt : « The planted-world run was stopped before its end ([stop: budget / duration / recomputation disagreement / session failure]); we did not run the loop on the real question. »
~~~~

**T33** — 6 : point (3) de S1 fait par le code (I18)

remplacer :

~~~~text
est fait à chaque course, déclenchée ou non. S1 ou S3
~~~~

par :

~~~~text
est fait à chaque course, déclenchée ou non, par le code gelé (champ `recherche_loi_plantee` du relevé, calculé ; absent ou `null` : relevé invalide ; v62). S1 ou S3
~~~~

**T34** — 6 S5 : gardien mécanique, non concluant par bras (I15, mineur 16)

remplacer :

~~~~text
- **S5 — asymétrie du gardien** : refus du gardien modèle d'un bras supérieur de plus de 0,15 à celui d'un autre bras : motifs
~~~~

par :

~~~~text
- **S5 — asymétrie du gardien et de l'expérimentateur** : part de refus du gardien mécanique, ou part de « non concluant », d'un bras supérieure de plus de 0,15 à la même part d'un autre bras : motifs
~~~~

**T35** — 7, garde 5 (I12)

remplacer :

~~~~text
| 5 | plafond dur de dépense par étage | appels à 0,01 USD : étage complet | plafond franchi → arrêt, code 3, sortie scellée, aucune issue lue | **à écrire** (v60) |
~~~~

par :

~~~~text
| 5 | plafond de dépense par étage, vérifié après chaque appel de proposeur et chaque étage de tests de mort ; plafond dur tenu par les relais (registre cumulé ; part de chaque relais fixée au plan, v62) | appels à 0,01 USD : étage complet | plafond franchi → arrêt, code 3, sortie scellée, aucune issue lue ; plafond d'un relais atteint (« budget_depasse » hors plafond de la fiche) → arrêt, jamais « non concluant » | `essais/test_v61_tour_ferme.py` (`Garde5Et13` ; lanceur, code 3) ; part des relais : **à écrire** (v62) |
~~~~

**T36** — 7, garde 6 (I19)

remplacer :

~~~~text
| 6 | préenregistrement scellé exigé | fichier scellé, bloc de code gelé conforme | nom avec « brouillon », sceau absent ou faux, empreinte de code différente → code 2, rien écrit | **à écrire** (v60, comme `banc_tricheurs_v8.lire_preenregistrement`) |
~~~~

par :

~~~~text
| 6 | préenregistrement scellé exigé | fichier scellé, bloc de code gelé conforme | nom avec « brouillon », sceau absent ou faux, marqueur restant, empreinte de code différente, entropie < 2⁶⁴ → code 2, rien écrit | `Garde6` (v61) : plan sain et artefacts ; nom « brouillon », hors de `prereg/`, absent ; **cas sain complet, sceau faux, marqueur, empreinte de code, entropie : à écrire** (v62) |
~~~~

**T37** — 7, garde 7

remplacer :

~~~~text
| 7 | témoins jamais retenus ni servis | témoin promu et survivant : absent de la sélection, de l'archive, de la vue | témoin introduit dans l'archive → refus | **à écrire** |
~~~~

par :

~~~~text
| 7 | témoins jamais retenus ni servis | témoin promu et survivant : absent de la sélection, de l'archive, de la vue | témoin introduit dans l'archive → refus | `Garde7` (v61), mutation tuée |
~~~~

**T38** — 7, garde 8

remplacer :

~~~~text
→ refusée au gardien mécanique | **à écrire** |
~~~~

par :

~~~~text
→ refusée au gardien mécanique | `Garde8` et lanceur `--scenario-proposeur hors_gabarit` (v61), mutation tuée |
~~~~

**T39** — 7, garde 9

remplacer :

~~~~text
| 9 | familles séparées | expérimentateur Kimi, vérificateur Argon | même famille → refus avant toute session | **à écrire** |
~~~~

par :

~~~~text
| 9 | familles séparées | expérimentateur Kimi, vérificateur Argon | même famille → refus avant toute session | `Garde9` et lanceur `--familles-a-blanc a,a`, code 2 (v61), mutation tuée |
~~~~

**T40** — 7, garde 10 (I11)

remplacer :

~~~~text
| script qui écrit des gains fabriqués → « non concluant », audit S1 | **à écrire** |
~~~~

par :

~~~~text
| script qui écrit des gains fabriqués → **arrêt de la course**, code 3, relevé partiel scellé, audit S1 | `Garde10` (unité, v61), mutation tuée ; arrêt de bout en bout : **à écrire** (v62) |
~~~~

**T41** — 7, garde 12

remplacer :

~~~~text
| étage 2 lancé sans elle, ou avec « ne tient pas » → code 2 | **à écrire** |
~~~~

par :

~~~~text
| étage 2 lancé sans elle, ou avec « ne tient pas » → code 2 | `Garde12` (v61) |
~~~~

**T42** — 7, garde 13 (I10, I11)

remplacer :

~~~~text
| 13 | modèle servi inconnu, signal, durée | modèle attendu | autre modèle servi ; durée > plafond (4 h étage 1, 2 h étage 2) → arrêt, code 3 | existe pour le modèle et le signal (`noyau_v56`) ; durée **à écrire** |
~~~~

par :

~~~~text
| 13 | modèle servi inconnu, session en échec, durée | modèle attendu | autre modèle servi (refus R-764) ou session en échec, chez un proposeur comme à l'étage → arrêt, code 3, sortie scellée ; durée > plafond (4 h étage 1, 2 h étage 2), vérifiée entre deux appels (un étage en cours n'est pas interrompu) → arrêt, code 3 | durée : `Garde5Et13` (horloge factice, v61) ; modèle servi et session en échec sur le chemin du tour : **à écrire** (v62 ; la v61 tait le refus d'un proposeur et sort en code 1 sur `EtageInterrompu`) |
~~~~

**T43** — 7, garde 14 et garde 15 nouvelle (B9, I22)

remplacer :

~~~~text
| 14 | lecture gelée | relevé sain → « tient », « discrimine », P | chaque critère T1 à T5 manqué → « ne tient pas » ; survivante de génération 2 seule → Z ; contre-calcul absent → Z ; étage 1 manqué → N | **écrite** : `essais/test_v60_lecture_tour_ferme.py` (17 essais), 5 mutations tuées sur 5 |
~~~~

par :

~~~~text
| 14 | lecture gelée | relevé sain **produit par le cœur** → « tient », « discrimine », P | chaque critère T1 à T5 manqué → « ne tient pas » ; survivante de génération 2 seule → Z ; contre-calcul absent → N ; étage 1 manqué → N1 | `essais/test_v61_lecture_tour_ferme.py` (14 essais), 6 mutations tuées ; relevés produits par le cœur (bras réel muet en génération 1, puis en générations 1 et 2) : **à écrire** (v62) |
| 15 | machine jetable (R-640, CL20-14) | `POLE_MACHINE_JETABLE_V56=1` déclaré, environnement dans la liste blanche | variable absente ou variable hors liste → code 2, avant tout appel | **à écrire** (v62 : la v61 passe à l'étage un environnement constant, `ENV_A_BLANC`, aussi en mode réel) |
~~~~

**T44** — 8 : préfixe des tâches (mineur 17)

remplacer :

~~~~text
`tour-ferme-v1|etage=<e>|bras=<b>|generation=<g>` suivies de
~~~~

par :

~~~~text
`tour-ferme-v61|etage=<e>|bras=<b>|generation=<g>` (préfixe = `VERSION` du cœur gelé ; `tour-ferme-v62|…` avec un cœur v62) suivies de
~~~~

**T45** — 8 : graine publique (mineur 7 de la contre-lecture 1)

remplacer :

~~~~text
La réserve de T ne dépend pas de E
(section 5.2).
~~~~

par :

~~~~text
La réserve de T ne dépend pas de E
(section 5.2). E est public dès la poussée du texte scellé : tranches et épisodes de développement se calculent d'avance ; sans effet tant que proposeurs et expérimentateur n'ont ni outil ni accès au dépôt.
~~~~

**T46** — 9 : commande de la lecture gelée (I20)

remplacer :

~~~~text
Sorties : `manifeste.json` (écrit avant le premier appel
~~~~

par :

~~~~text
- **Lecture gelée de l'étage 1** (après la course, par un lecteur neuf, R13) : `nice -n 10 python3 -I -B demonstrations/lire_tour_ferme_v62.py ../resultats/tour-ferme-v1-etage1 LECTURE.json` (à écrire en v62 : vérifie le sceau et l'empreinte du relevé, applique `lire_tour` au champ `releve`, écrit la lecture scellée qu'exige la garde 12).

Sorties : `manifeste.json` (écrit avant le premier appel
~~~~

**T47** — 10, L2b-v61 : heure (mineur 11)

remplacer :

~~~~text
| L2b-v61 | rédacteur 2, ≈ 10:40 |
~~~~

par :

~~~~text
| L2b-v61 | rédacteur 2, 09:10 à 09:12 (manifeste `debut_utc` 09:10:08 Z, relevé `fin_utc` 09:11:40 Z) |
~~~~

**T48** — 10, L2b-v61 : bras aléatoire en génération 1 (mineur 18)

remplacer :

~~~~text
aléatoire 36, PS 0 (jugé contre l'archive réelle informative)
~~~~

par :

~~~~text
aléatoire 36, PS 0 (génération 1 jugée contre une archive réelle encore vide : 0 sur 12, probabilité ≈ 0,21 ; générations 2 et 3 contre l'archive réelle informative)
~~~~

**T49** — 10, L2b-v61 : S1, borne haute, limite (I16, mineur 18)

remplacer :

~~~~text
Conséquence lue : sous D7, la part PS du bras aléatoire dépend de la force de l'archive réelle (ici 0/36) ; P4 reste écrite sur L2b (archive propre) et se lit comme borne haute |
~~~~

par :

~~~~text
Audit S1 « trop beau » déclenché (proposeurs scriptés voisins de L* : VD* en génération 1, attendu à blanc). Conséquence lue : sous D7, la part PS du bras aléatoire dépend de l'archive réelle (ici 0/36) ; P4 est écrite par cas (section 4.3). **Limite** : les deux rôles modèles y reçoivent hors bande ce que les vrais ne reçoivent pas (la loi éprouvée pour l'expérimentateur, la grammaire des lois pour les proposeurs) : cette répétition n'essaie pas le chemin réel |
~~~~

**T50** — 10 bis : découvertes distinctes (mineur 19)

remplacer :

~~~~text
mineur 10 (découvertes distinctes) : champ `vd_distinctes` du relevé, calcul à écrire au cœur, mesure sans critère.
~~~~

par :

~~~~text
mineur 10 (découvertes distinctes) : champ `vd_distinctes` du relevé, vide dans le code v61 : calcul à écrire au cœur v62 avant scellement, ou mesure retirée du texte ; jamais calculée après lecture.
~~~~

**T51** — 12 : prix par tour et part de Kimi (I12)

remplacer :

~~~~text
≈ 3,3, ≈ 8,4 ou ≈ 12,2 USD une fois le gardien modèle retiré, D9)
~~~~

par :

~~~~text
≈ 3,3, ≈ 8,4 ou ≈ 12,2 USD une fois le gardien modèle retiré, D9, au prix de 0,04 USD par tour à 2 tours et de 0,06 USD à 4 et 6 tours, contre-lecture 1, I7 ; Kimi, proposeur et expérimentateur, en porte ≈ 2,6, ≈ 7,8 et ≈ 11,6 USD, Argon ≈ 0,7 USD ; le lanceur v61 donne à la porte de chaque relais la moitié du plafond, 7,5 USD, que Kimi dépasse dès 4 tours : la part de chaque relais est fixée au plan gelé, par exemple 12 USD pour Kimi et 3 USD pour Argon, v62)
~~~~

**T52** — 13 : décisions lues par le lanceur (réponse D2 à D9)

remplacer :

~~~~text
**Le lanceur lit chaque décision dans le bloc `plan-gele` ci-dessous**
~~~~

par :

~~~~text
**Le lanceur lit les décisions D7, D8 et D9 dans le bloc `plan-gele` ci-dessous** (D2 à D6 sont écrites dans le code gelé : un refus de l'une d'elles exige un code nouveau)
~~~~

**T53** — 13 : substitution du plafond dans les commandes (I21)

remplacer :

~~~~text
le lanceur refuse toute autre empreinte et ne substitue aucun plafond en mémoire (seul le jeton `{REGISTRE}` des
commandes externes est remplacé, mécanisme du lanceur de l'attaque de Goodhart v2, substitution déclarée au manifeste).
~~~~

par :

~~~~text
le lanceur refuse toute autre empreinte ; dans la copie servie aux relais, il remplace le jeton `{REGISTRE}` des
commandes externes **et** la valeur de `--plafond-cumule-usd` par le plafond de l'étage (`attaque_goodhart_v2.substituer_commandes`, substitutions déclarées au manifeste), puis transmet à la porte de chaque relais un plafond d'étape (v61 : la moitié du plafond de l'étage ; v62 : la part fixée au plan).
~~~~

**T54** — 13 : tête des empreintes (mineur 20)

remplacer :

~~~~text
tête `c47b608`, fichiers
`_v61` non suivis au moment du calcul : recalculer après commit si un fichier change)
~~~~

par :

~~~~text
calculées à la tête `c47b608` ; revérifiées par la contre-lecture 2 à la tête `7d3aa82`, où les fichiers `_v61` sont suivis : 83 empreintes, aucun écart ; à recalculer pour le code v62)
~~~~

**T55** — 14 : nature des décisions (réponse D2 à D9)

remplacer :

~~~~text
à remplir sur le mot de Lazar ; un refus = version nouvelle :
~~~~

par :

~~~~text
à remplir sur le mot de Lazar ; un refus = version nouvelle (D7, D8 et D9 sont des paramètres du plan gelé, lus par le lanceur ; D2 à D6 sont écrites dans le code gelé : un refus de l'une d'elles exige aussi un code nouveau) :
~~~~

**T56** — 14 : marqueur D2 déplacé ici (I13)

remplacer :

~~~~text
nouveauté contre l'archive (section 3) (oui).
~~~~

par :

~~~~text
nouveauté contre l'archive (section 3) (oui). Mot de Lazar : <<DECISION_D2>>.
~~~~

**T57** — 14 : marqueur D3 déplacé ici (I13)

remplacer :

~~~~text
qu'autrement les générations 2 et 3 ne mesurent plus rien).
~~~~

par :

~~~~text
qu'autrement les générations 2 et 3 ne mesurent plus rien). Mot de Lazar : <<DECISION_D3>>.
~~~~

**T58** — 14 : marqueur D4 déplacé ici (I13)

remplacer :

~~~~text
sinon il ne recopie que ce que le hasard a retenu).
~~~~

par :

~~~~text
sinon il ne recopie que ce que le hasard a retenu). Mot de Lazar : <<DECISION_D4>>.
~~~~

**T59** — 14 : marqueur D5 déplacé ici (I13)

remplacer :

~~~~text
génération 1 seule décisive (oui) ; ou T coupé en deux.
~~~~

par :

~~~~text
génération 1 seule décisive (oui) ; ou T coupé en deux. Mot de Lazar : <<DECISION_D5>>.
~~~~

**T60** — 14 : marqueur D6 déplacé ici (I13)

remplacer :

~~~~text
les 2,5 USD servent mieux au plafond).
~~~~

par :

~~~~text
les 2,5 USD servent mieux au plafond). Mot de Lazar : <<DECISION_D6>>.
~~~~

**T61** — 14 : ce qui manque, point (1) (mineur 12)

remplacer :

~~~~text
(1) le code `_v60` de la section 13, ses essais, son banc de mutations et sa répétition à blanc ;
~~~~

par :

~~~~text
(1) le code `_v62` (contre-lecture 2 : loi servie à l'expérimentateur, grammaire servie aux proposeurs, lectures d'héritage, arrêts scellés, relais, machine jetable) et, pour l'étage 2, son cœur ; leurs essais, leur banc de mutations et une répétition à blanc où les rôles scriptés ne reçoivent que ce que reçoivent les modèles ;
~~~~

**T62** — 14 : GO exact (I12)

remplacer :

~~~~text
(6) le GO de Lazar sur ce devis (ligne dans `registres/go.md`, plafonds 12 + 5 USD)
~~~~

par :

~~~~text
(6) le GO de Lazar sur ce devis : une ligne de `registres/go.md` de type « calcul », par Lazar, en cours de validité, d'un montant **exactement égal** au plafond de l'étage (15 USD pour l'étage 1 ; `configuration_v55.verifier_go_v55` refuse tout autre montant) ; l'étage 2 exige un GO et une configuration à lui (5 USD)
~~~~

**T63** — 3 : « inconclusive » contredit la garde 10 et l'étage v5 (I11)

remplacer :

~~~~text
| **inconclusive** | verdict du noyau « non concluant » (fichier brut absent, incident de la fiche, session en échec, contre-calcul en désaccord : section 7) |
~~~~

par :

~~~~text
| **inconclusive** | verdict du noyau « non concluant » (aucune exécution réussie, fichier brut absent ou illisible, plafond de la fiche atteint sans fichier, incident de la fiche). Une session en échec, un refus de modèle (R-764) ou un contre-calcul en désaccord **arrêtent** la course (section 7, gardes 10 et 13) : ce ne sont pas des « non concluant » |
~~~~

## 10. Changements de code (fichiers neufs `_v62`, aucun `_v61` modifié)

- **C8 (B7)** — Servir à l'expérimentateur la loi gelée (JSON canonique, taille bornée et refus motivé au gardien au-delà) et
  l'évaluateur de référence de la grammaire (le code de `statistique_hors_bac`, fichier de la tranche, même empreinte pour toutes les
  cartes). L'expérimentateur scripté du mode à blanc lit la loi **dans sa consigne** et nulle part ailleurs (supprimer le passage hors
  bande `demonstrations/tour_ferme_v61.py:225-236`). Essais : chaque consigne contient sa loi (sain) ; loi absente → l'expérimentateur
  scripté échoue (artefact) ; mutation « loi non servie » tuée.
- **C9 (B8)** — Consigne v62 : champs exacts de chaque type et un exemple valide par type ; essai : chaque exemple passe
  `selection_pari.valider_loi`. Le proposeur scripté construit ses lois depuis la grammaire servie.
- **C10 (B9)** — Lecture v62 : lectures attendues = {(bras, g) : 2 ≤ g ≤ `releve["plan"]["generations"]`}, jouées ou non (le cœur
  consigne déjà la lecture de la recopie muette) ; essais sur des relevés **produits par le cœur** (les deux sondes de la section 0 →
  « tient ») ; mutation tuée.
- **C11 (I22)** — Mode réel : `environnement=os.environ` et `permis_en_plus` de la configuration (`etage_tests_de_mort.environnement_permis`)
  passés à l'étage ; `exiger_machine_jetable_v56` appelé par le lanceur avant tout appel. Essais sain et artefact (variable absente,
  variable hors liste → code 2).
- **C12 (I10)** — Le cœur convertit `EtageInterrompu`, `VueAvecVerdict`, `BacASableIndisponible`, `HeritageRefuse` (lecture finale) en
  `ArretTour` avec relevé partiel ; `ProposeurAdaptateur` lève `ArretTour` sur tout statut autre que « ok » (refus R-764 compris) ; le
  lanceur rattrape toute exception après le manifeste : rapport partiel scellé, code 3. Essais : la sonde `sonde_panne_session.py`
  (attendu : code 3, relevé scellé) ; proposeur en refus R-764 → code 3.
- **C13 (I12)** — Parts des relais au plan (`plafond_kimi_usd`, `plafond_argon_usd`, somme = plafond de l'étage), transmises aux
  portes ; compteur par relais ; arrêt avant un étage si la part restante d'un relais est sous le pire cas de l'étage (cartes × 0,6 USD) ;
  « budget_depasse » d'un relais hors plafond de la fiche → arrêt. Plan par étage pour `go` et `configuration_sha256` si les deux
  étages sont scellés ensemble.
- **C14 (I11, I14)** — Gabarit du test v62 : « valeurs en pleine précision (`repr`) » ; traitement du désaccord tranché et écrit
  (arrêt, ou carte « non concluant (contre-calcul) » comptée en T4) ; essai : `gains.csv` arrondi à 4 décimales → comportement écrit.
- **C15 (I15)** — Étage servi à l'aveugle : identifiant opaque (empreinte de l'identifiant réel) et titre, hypothèse neutres pour
  toute carte et tout témoin ; correspondance gardée par l'orchestrateur ; essai : aucune consigne ne contient « témoin », « ALEA »,
  « COPIE », « kimi », « argon ».
- **C16 (I16, I17, I18, mineurs 16, 19)** — Lecture v62 : P4 par cas (archive réelle vide ou non, lue sur `archive_de_jugement` du
  journal) ; A4 « non mesurable » si n_réel = 0 ; S5 sur le « non concluant » par bras ; `recherche_loi_plantee` calculé par le cœur sur
  chaque contexte servi (poids de L* exacts et à deux décimales, lignes de tranche), absent ou `null` → `ReleveInvalide` ;
  `vd_distinctes` calculé ou retiré.
- **C17 (I19)** — Essais de la garde 6 avec `DOSSIER_PREREG` pointé vers un dossier temporaire : texte scellé accepté (sain) ; sceau
  faux, marqueur, empreinte de code différente, entropie < 2⁶⁴ (artefacts).
- **C18 (I20)** — `demonstrations/lire_tour_ferme_v62.py` : vérifie sceau et empreinte du relevé, applique `lire_tour`, écrit la lecture
  scellée lue par la garde 12.
- **C19 (I23)** — La recopie de la génération g lit le bilan du bras réel de g−1 (garder l'état précédent) ; essai : son
  `archive_de_jugement` égale celle des cartes réelles de g.
- **C20 (I24)** — Geler le monde planté : `exemples/temoins-pari-demo-v1.json` dans le bloc des empreintes, ou clé `monde_sha256` au
  plan comparée à `charger_monde`.
- **C21 (mineur 21)** — Mode réel : passer `moteur="claude-sdk"` à l'étage (refus de l'exécuteur factice rallumé, `cout_fictif` juste),
  ou garder « simule » en refusant au cœur tout étage `factice` et en disant au relevé que l'étiquette est héritée.
- **C22** — Répétitions à blanc sur 5 racines avec C8 et C9 (aucun canal hors bande), déclarées en section 10.

## 11. Ce qu'il faut pour sceller

1. Code `_v62` (section 10), essais, banc, répétitions à blanc ; nouveau bloc des empreintes.
2. Brouillon 3 : couples T19 à T63, plus ce que demandera le choix de portée (section 7) et celui de C14.
3. Mot de Lazar sur D2 à D9 (marqueurs), sur la portée (A ou B) ; cases privées par la session-depot ; configuration et GO au montant
   exact de chaque étage.
4. Contre-lecture R2 neuve du brouillon 3 et du code v62 ; puis scellement par le directeur, commit et poussée avant la course.

Aucun point de ce rapport ne demande d'appel de modèle ni de dépense.
