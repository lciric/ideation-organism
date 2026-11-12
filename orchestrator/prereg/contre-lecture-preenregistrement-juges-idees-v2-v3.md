# Contre-lecture R2 n° 3 — validation des juges d'idéation v2, brouillon 3, et code `juges_idees_v2` (commit public `faff48b`)

4 novembre 2026, de 01:34 à 02:21 UTC (heures de `date -u` ; le conteneur a redémarré vers 01:53 UTC : banc de mutations et
recalcul de puissance perdus en cours de route et relancés une fois, rien d'autre n'a été perdu sur disque). Contre-lecteur neuf : je
n'ai écrit ni l'étage des juges d'idéation, ni le protocole v2, ni ses brouillons 1, 2 et 3, ni les contre-lectures des brouillons 1 et 2.
Consignes suivies, empreintes vérifiées par `sha256sum` avant lecture : avenant
`/home/claude/controle-ia-travail/brouillons/reprise-fusionnee-2026-11-04/avenant-relances-v1.md` (`d4f14478…`, sections « Pour les trois »
et « Contre-lecture des juges v2 ») et consigne
`/home/claude/controle-ia-travail/brouillons/reprise-conv-audit-2026-11-02-nuit/prompts-sous-agents/contre-lecture-juges-idees-v2-brouillon3-prompt.md`
(`072c3f59…`, compagnon concordant). Lecture seule de `ideation-organism` (lien vers le clone public, tête `faff48b`, arbre propre). Aucun
commit, aucun compagnon `.sha256`, aucun fichier existant modifié, rien sous `donnees/`, aucun `git fetch`, `checkout` ou `stash`, aucun
réseau, aucun modèle ; calculs sous `nice -n 10 python3 -I -B` (Python du `.venv` de `/home/user/controle-ia-travail`, le Python du
système n'a pas pytest), `TMPDIR=/tmp`. `../resultats/banc-tricheurs-v9-validation-v1/` n'a pas été ouvert. Sondes et sorties :
`/home/claude/scratch/juges-v3-contre-lecture/` (annexe). Numérotation à la suite des contre-lectures v1 et v2 : B10, I10, M17.

**Verdict : non scellable** — les matériaux doivent changer encore (code, nouvelle empreinte, contrôles et plan joué recalculés), puis un brouillon 4 et une contre-lecture neuve du delta ; B9, I6, I7, I8 sont levés.
**Bloquant (1)** : B10 — B8 n'est pas levé : quatre traits de surface que le développeur n'a pas écrits (rang de la caractéristique dans le dossier, nombre de lignes du dossier qui la nomment, rapport du seuil d'abandon au seuil de prédiction, longueur moyenne des mots) enfreignent les règles gelées du contrôle de diagnosticité ; « seuil d'abandon / seuil de prédiction » tient D1 13 fois sur 20 (aire 0,696) et D1b 14 fois sur 20 (0,741).
**Importants (3)** : I10 code 6 (délai) compté dans les cinq échecs coûteux de suite : I0 au 104e appel ; I11 le relevé de l'épreuve n'est refusé par aucun lanceur ; I12 prix d'Argon mesuré à l'épreuve sans règle qui le rattache à la part de 24 USD. **Mineurs (6)** : M17 à M22. **Rejoué** : essais 102 et 81 sous-essais réussis ; banc 133 mutations sur 133 tuées pour la raison attendue ; contrôles de forme et de diagnosticité sur les trois jeux à l'identique ; puissance et plan joué identiques à l'octet (`af9c52f8…`, I1 dans 56 courses sur 60 à 0,75) ; 62 empreintes du code concordantes ; trois courses à blanc ; 40 juges de surface neufs.

## 1. Pièces lues, empreintes

| pièce (depuis `orchestrator/`) | sha256 | état |
|---|---|---|
| `prereg/preenregistrement-juges-idees-v2-brouillon3.md` | `2680cf6a5c7f080d796a9089a85d3c454f030a02186b5dc3d24728c600523dce` | égal à la consigne, 835 lignes, lu en entier |
| `prereg/rapport-redaction-juges-idees-v2-brouillon3.md` | `aad855365a3f2f655cb86934a6c5f0060144bd98c3f14bc0b4699360a3f353ce` | dix points et section 8 d'abord, puis en entier |
| `prereg/contre-lecture-preenregistrement-juges-idees-v2-v2.md` ; couples `…-v2.json` | `8b91ab57…` ; `e20cdc1f…` | égaux à la consigne ; lus en entier ; couples confrontés au brouillon 3 par script |
| `prereg/preenregistrement-juges-idees-v2-brouillon2.md` | `c1df7e91…` | consulté |
| `pole/juges_idees_v2.py`, `demonstrations/validation_juges_idees_v2.py`, `essais/test_juges_idees_v2.py`, `essais/mutations_juges_idees_v2.py` | `57e4474a…`, `2494a56f…`, `7e01500b…`, `cb84dda4…` | égaux au rapport ; relais, compteur, classement, étapes, contrôles, juge scripté, lanceur (journal, signal, gardes) lus |
| `pole/adaptateurs.py` | — | `modele_conforme` (l. 362-376), `AdaptateurCommandeExterne.lancer` (l. 721-775) |
| bloc `empreintes-du-code` (62 lignes) | — | `sha256sum -c` sur l'arbre `faff48b` : 62 OK |
| `registres/go.md` (branche, ligne de GO-2026-11-02-32) | — | ligne lue en entier : 60 USD, parts 24 et 36, garde 48 h, « plafond du texte scellé exactement 60 USD » |
| `registres/decisions.md` (branche) | — | R-1276 (l. 1240), R-1277 (l. 1241), R-1293 (l. 1257) |
| n° 294 de session-depot (`81e601fa…`) | **absent de cette machine** | `/home/claude/lectures/` n'existe plus (avenant : travail de l'ancienne machine perdu) ; la table des codes est relue dans R-1277, dans la contre-lecture v2 (citations du § 3) et dans `commande_argon_v2.py` (forme « HTTP {code} : … » sur la sortie d'erreur) : réserve M22 |
| `/home/claude/scratch/juges-v3/` (bloc-notes du développeur) | **absent** (avenant) | non cherché ; les empreintes de ses sorties n'ont pas pu être confrontées, mes recalculs les remplacent |

## 2. Ce qui a été rejoué

- **Essais** : `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py`
  → **102 réussis, 81 sous-essais réussis**, 140,96 s (01:35:16 à 01:37:37 UTC), code 0. Égal au rapport.
- **Banc de mutations** : premier lancement (01:38 UTC) tué par le redémarrage du conteneur après 110 mutations, **110 tuées pour la
  raison attendue**, témoin 101 essais, 0 en échec (`banc-1-interrompu.txt`) ; relancé une fois, seul avec le recalcul de puissance, sans
  suite d'essais en même temps : **133 mutations, 133 tuées pour la raison attendue**, 0 pour une autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin 101 essais, 0 en échec avant et après (01:55:41 à 02:20:11 UTC, code 0, `banc-2.txt`). Égal au rapport ; la course à 25 pires cas rejouée donne lecture et journal au fil **égaux à l'octet** à ceux du rapport (`5bfc03e8…`, `848e1883…`).
- **Contrôles des matériaux** (`diag_cl3.py`) : `construire_materiaux(20261102)` = `2ee2f2e4…`, `"mondes-v2"` = `59737a16…`,
  `"mondes-brouillon1"` = `f4ff3485…` ; `verifier_materiaux` vide sur les trois ; forme : conforme, refusé, refusé ; diagnosticité :
  conforme (aucun motif ; « dossier sans tables » D1 20/20 aire 0,763, D1b 0 ; lecteur des tables D1b 20/20, aire des lois fausses 0,997),
  refusé (« ampleur » et « seuil » D1b 20/20, aires 0,958), refusé. **Les tables de la section 4 du texte, à l'identique.**
- **Puissance et plan joué** (`--puissance --graine 20261102 --repetitions 20000 --graines-plan 60`, 01:55 à 02:06 UTC) : sortie
  **identique à l'octet** à celle que cite le texte (`af9c52f874d6f3a8b063166bfe3b987c4092b349d9c8b40e14652c01920aac02`) : I1 dans
  **56 courses sur 60** à 0,75 (I3 2, I4 2), 58 à 0,80, 60 à 0,85 ; D1b tenu dans 52 sur 60 à 0,75.
- **Courses à blanc** (`courses/`, juges par défaut, graine 20261102) : (a) cinq codes 6 (délai) de suite dans la phase décisive de A
  (`--panne-a delai:100-104`) → **code 3, `ArretPanne` « 5 échecs coûteux de suite », 104 appels, 11,138 USD, I0** (I10) ; (b) rafale de 25
  codes 3 au pire cas (`relais_pire_cas:100-104,quota:150-169`) → code 0, 345 appels, 54,496 USD, **I1a, S0, T1**, audit déclenché
  (égal au rapport) ; (c) 413 du relais au 120e appel (`requete:120`) → code 3, `ArretRequete` immédiat, 120 appels, 7,378 USD, I0.
- **Juges de surface neufs** (`juges_surface_cl3.py`, 40 juges, 18 traits et leurs contraires et 4 combinaisons, joués comme ceux du
  code : `jouer_v2_tirage_1`, graines `Graines(20261102000 + k)`, k = 0…19, trois jeux) : section 3.

## 3. Question 1 — B8 (témoins séparables sans lire une table) : **non levé (B10)**

**Le contrôle du développeur tient sur ses propres juges** (rejoué ci-dessus). Mais sur 40 juges que je n'ai pas tirés de sa liste,
joués par son plan et ses règles gelées (D1 au plus 2 sur 20 et aire moyenne au plus 0,62 ; D1b au plus 2 sur 20 et aire des lois
fausses au plus 0,62), **neuf enfreignent les règles sur les matériaux de ce texte** :

| juge de surface (rien des taux des tables) | D1 sur 20 | aire moyenne | D1b sur 20 | aire des lois fausses | brouillon 2 : D1b ; aire | brouillon 1 : D1b ; aire |
|---|---|---|---|---|---|---|
| **rapport seuil d'abandon / seuil de prédiction, le plus haut** (deux nombres de la fiche) | **13** | **0,696** | **14** | **0,741** | 20 ; 0,941 | 0 ; 0,477 |
| **longueur moyenne des mots, la plus courte** | **10** | **0,662** | 2 | 0,646 | 7 ; 0,706 | 0 ; 0,547 |
| **caractéristique nommée le plus tôt dans le dossier** (numéro de sa première ligne de table 1, lu sur l'étiquette) | 0 | 0,505 | **7** | **0,702** | 13 ; 0,753 | 15 ; 0,895 |
| même rang, relatif à son bloc (caractéristiques de même nombre de niveaux) | 0 | 0,525 | **5** | **0,684** | 9 ; 0,736 | 0 ; 0,353 |
| **caractéristique nommée dans le plus de lignes du dossier** (une table croisée lui est consacrée) | **3** | 0,608 | 2 | **0,631** | 17 ; 0,781 | 19 ; 0,951 |
| lignes, puis rang | 6 | 0,646 | 9 | 0,737 | 17 ; 0,842 | 18 ; 0,935 |
| rang, puis lignes ; rang relatif, puis lignes ; pourcentages présents dans le dossier, puis rang | 0 | ≤ 0,525 | 7 ; 5 ; 3 | 0,702 ; 0,691 ; 0,687 | — | — |

Les 31 autres tiennent les règles (chiffres ronds, cohérence de l'écart et des taux écrits, centre des taux, écart relatif, rapport
seuil/écart, longueur du nom et du titre, débuts de titre, variantes de rédaction, méthode de Wilson, mots des lois établies, et
« pourcentages de l'hypothèse présents n'importe où dans le dossier » : D1b 1 sur 20 dans les deux sens — l'appariement des taux tient).
Indices correspondants, à la manière du contrôle de forme (bons contre mauvais ; bonnes lois contre lois fausses) : seuil de prédiction
pair 0,700 ; 0,729 — rapport abandon/prédiction 0,727 ; 0,738 — rang dans le dossier 0,418 ; 0,710 — lignes du dossier 0,709 ; 0,643 —
longueur moyenne des mots 0,647 ; 0,652 : quatre hors de [0,35 ; 0,65].

**Mécanismes.** (i) Seuils : `_seuils` donne un seuil d'abandon égal à la moitié entière du seuil de prédiction ; le rapport vaut 0,5
pour un seuil pair, moins pour un impair ; les lois fausses recalculent leurs seuils sur l'écart **décalé d'un point** (`JITTER_APPARIE`) :
1 seuil pair sur 7, contre 9 sur 15 pour les bonnes lois. (ii) Rang : dans chaque bloc de la table 1, les caractéristiques sans effet
sont écrites **après** celles qui ont un effet (monde-1 : « tests exécutés » après « lecture seule » ; « langue », « suite de tests »
après « heure » ; de même dans monde-2 et monde-3) ; toute loi fausse porte sur une caractéristique sans effet. (iii) Lignes : la
bonne loi graduée croissante et la bonne interaction portent sur la caractéristique de la table 2 (13 lignes du dossier, choix (6) du
brouillon 3), monde-1 n'a pas de table 3, et les lois fausses de deux groupes portent sur des binaires (2 lignes). Un juge réel qui
préfère « la loi à laquelle le dossier consacre une table » ou la première caractéristique qu'il lit n'a rien d'invraisemblable.

**Conséquence.** T1 « lecture des tables établie » peut encore être prononcé pour un juge qui ne lit aucun taux ; les phrases de P14
(« aucun juge scripté de surface n'y arrive »), de T1 (« aucun juge scripté qui ne lit pas les tables n'y arrive plus de 2 fois sur 20 »)
et de la section 10 sont fausses pour ces juges ; et D1, l'issue elle-même, s'obtient 13 fois sur 20 par la parité des seuils.

**Les jumelles (monde-3-07 et monde-3-01, mêmes taux 19 % et 45 %, même rédaction)** : c'est ce que le plan veut — dans une telle
paire, tous les juges de surface du code et les miens qui ne lisent que le texte de la fiche donnent le même score aux deux ; seule la
caractéristique diffère. Mais c'est aussi pourquoi le signal résiduel se reporte sur ce qui la distingue dans le dossier (rang, lignes) :
l'appariement concentre la fuite sur la place de la caractéristique, que personne n'a contrôlée.

**Retouches après mesure (section 9).** Déclarées avec exactitude (quatre étapes, cinq jeux ; le rapport dit « trois fois », M21) ; les
seuils (2 sur 20, 0,62, 90 %) sont bien gelés avant la dernière retouche. **Mais la liste des juges ne l'était pas** : l'étape (2) ajoute
l'indice et le juge « plus haut pourcentage » ; matériaux et batterie ont été accordés l'un à l'autre, si bien que le succès du contrôle
ne prouve plus l'absence de fuite hors de la batterie — ce que montrent les juges ci-dessus. Le déclarer ne suffit pas.

**Correction (code, matériaux, texte ; nouvelle empreinte, nouveau banc).** (1) Ordre des caractéristiques de la table 1 tiré par graine
(ou alphabétique) dans chaque monde, pour que les caractéristiques sans effet ne soient pas en fin de bloc ; (2) une loi fausse reprend
**les seuils** de sa bonne loi appariée (pas ceux de l'écart décalé), ou le décalage s'applique aussi aux bonnes lois ; (3) une table
croisée par monde porte une caractéristique sans effet visée par une loi fausse non interaction (ou monde-1 reçoit sa table 3), pour
équilibrer les lignes ; (4) ajouter au contrôle de forme « seuil pair », « rapport abandon/prédiction », « rang dans le dossier »,
« lignes du dossier », « longueur moyenne des mots », et à la batterie les juges correspondants et leurs combinaisons ; (5) **figer la
batterie avant toute nouvelle retouche** et faire jouer, avant le scellement, une batterie tenue à l'écart écrite par un autre que
celui qui accorde les matériaux (`juges_surface_cl3.py` peut en être le noyau). À 15 contre 7, sur plusieurs centaines de traits, quelques
aires sortiront de [0,35 ; 0,65] par le seul hasard : le texte doit dire ce qui est retiré par construction (1 à 3) et ce qui reste au
hasard, plutôt que promettre qu'aucun trait ne sépare.

## 4. Question 2 — B9 (politique du relais) : **levé**, avec I10, M17, M18, M19

- **Table des codes.** `classer_resultat` et `appeler` suivent la table telle que R-1277 et la contre-lecture v2 la citent du n° 294 :
  code 3 au plancher (relais injoignable) et au pire cas (toute erreur de l'interface, quota de Google compris) attendus et repris sans
  limite de nombre ni compte de suite, le pire cas compté hors du prix observé ; code 4 (402, 429 du relais, pire cas au-dessus du
  budget, registre) jamais attendu : `ArretRefusBudget`, ou `ArretPart`/`ArretDevis` si le budget était déjà borné par la part ou le
  plafond ; code 3 au plancher portant 400, 403, 411, 413 : `ArretRequete` ; le relais ne reprend rien. Rejoué (courses (b) et (c)).
- **Reconnaissance « HTTP 4xx ».** Le motif `HTTP (400|403|411|413)\b` est cherché dans `"code 3 : " + caviarder(sortie d'erreur)[:300]`.
  Les commandes Argon antérieures écrivent « HTTP {code} : … » sur la sortie d'erreur : la forme est probablement la bonne. Si elle
  diffère (« HTTP Error 413 », message sur la sortie standard, au-delà de 300 caractères) : le refus est lu comme un code 3 au plancher,
  attendu sans dépense (1e-6 par tentative) jusqu'à la garde de 48 heures dans une phase décisive (environ 100 tentatives), puis
  `ArretDuree` et I0 ; 6 heures puis panne ailleurs. Pas de boucle sans attente, pas de dépense, mais 48 heures perdues : M17 (motif
  plus large, par exemple `HTTP\D{0,8}(400|403|411|413)\b`) et couple 3 (l'épreuve le vérifie, sinon nouveau texte).
- **Aucune boucle sans dépense ni attente** : chaque passage par un code 3 journalise, vérifie la durée (`verifier_duree` en tête de
  boucle), attend au moins 15 s ; un échec coûteux attend 30 à 300 s et n'est repris que deux fois ; code 4, refus de requête et A2
  lèvent. Lu dans le code ; courses (a) à (c).
- **Horloge de panne (I6)** : levée (`echec` pose le début de série, `succes` le retire ; aucune panne dans les phases décisives). Reste
  M18 : une série ouverte dans la phase décisive de A et close sans réponse (dernière comparaison perdue définitivement après une longue
  attente) se prolonge dans le bras sans dossier, qui peut alors tomber en panne au premier échec, sans attente.
- **Journal au fil de l'eau (I8)** : levé (`FilJournal` écrit, vide, synchronise chaque ligne ; scellé sur fin normale ou arrêt ; le
  signal de fin devient `KeyboardInterrupt`, la commande en cours est tuée par `killpg` dans `lancer`, puis `ArretInterruption` scelle le
  journal partiel). Reste M19 : le coût de l'appel en vol au moment du signal n'est pas compté au bilan (il l'est au registre des
  commandes) ; `SIGHUP` n'est pas converti ; les essais simulent l'interruption dans l'adaptateur scripté, aucun n'envoie un vrai signal
  pendant une vraie commande.
- **Relais mort pour toujours dans une phase décisive** : seule la garde de 48 heures ; c'est la règle R-1276 (« gardes contre une boucle
  folle seulement ») et la ligne du GO ; essayé sur un cas sain (`test_relais_de_a_injoignable_sept_heures_puis_reprise`) et deux artefacts
  (`test_artefact_a_hors_service_arrete_la_course_issue_i0`, `test_b_hors_service_attendu_jusqu_a_la_garde_de_duree`). Acceptable.
- **I10 (important) — Code 6 dans les cinq échecs coûteux de suite.** Le délai (code 6 de la commande, ou délai de 1 800 s de
  l'adaptateur) est l'échec passager type d'un relais à un fil ou d'une interface lente ; il reste compté avec les codes 2 et 5 :
  cinq de suite dans la phase décisive de A → panne → arrêt → **I0** (course (a) : 104e appel, 510 s d'attentes en tout). C'est
  l'issue « non concluante par défaut de conception » que R-1276 écarte. Correction : dans les phases décisives, un délai à coût déclaré
  traité comme un code 3 au pire cas (attendu, repris, pire cas compté, borné par la part), sans compte de suite ; un délai de l'adaptateur
  (coût inconnu, budget compté, ≥ 1 USD) borné par la part ; la règle des cinq gardée pour les codes 2 et 5, la commande muette et le
  dépassement ; essai et mutation. Ou décision du directeur.

## 5. Question 3 — issues et dépense

- **Course à 25 pires cas → S0.** Lisible et déclarée : l'issue (I1a) n'est pas touchée, S0 « non mesuré » est une lecture gelée, la
  cause est au journal (étape non jouée, motif « budget ») et au rapport. Mais le texte (section 12) dit seulement « au-delà, la part de A
  est atteinte et la phase décisive s'arrête » : entre 6,89 et environ 8,75 USD d'incidents, la phase décisive finit et le bras est perdu
  (couple 5). C'est une perte par la part, que Lazar a écartée (« de plafond ou que sais-je ») : elle ne touche qu'une lecture jointe, et
  la seule autre voie est un GO qui déplace les parts (décision 3).
- **Devis** : 60 USD exactement (bloc, `PLAFOND_MAX_USD`, GO) ; 24 + 36 ; 276 × 0,062 = 17,11 ; 69 × 0,50 = 34,50 ; 51,61 ; marge
  24 − 17,11 = 6,89 USD ; pire cas réservé 10 654 / 3 × 10 + 4 000 × 50 par million ≈ 0,2355 USD ; 29 tentatives ; 4 125 s + 21 × 1 800 s
  ≈ 11,6 heures : recalculés, justes. Les incidents comptés au pire cas sont une réserve comptable, pas une dépense observée.
- **I12 (important) — Le prix d'Argon reste celui d'A1 (proposeur, 0,062 USD), aucune règle ne le rattache à l'épreuve.** Une
  comparaison porte 8 565 à 10 654 caractères ; la course projette au prix observé et la phase décisive est « tout ou arrêt » : à
  0,087 USD par comparaison, les 276 appels prennent toute la part ; à 0,075, la marge tombe sous 3,3 USD (14 pires cas). Le lanceur
  ne contrôle le devis qu'au prix du plan gelé. Couple 3 : au-dessus de 0,074 USD mesuré, nouveau texte.
- **Astra non mesuré, 0,50 USD** : prudente pour ce qui décide — les comparaisons de B passent d'abord, étape par étape, et D6 reste
  mesurable jusqu'à environ 1,1 USD par appel pour les 32 comparaisons de B (36 USD), et jusqu'à environ 1,6 USD pour les 20 que D6 exige (contre-lecture v2) ; au-delà de 0,50, ce sont l'ancien protocole de B (P11,
  descriptif) et les phases réelles qui tombent. Elle n'est pas prudente pour un effort de raisonnement élevé : l'épreuve tranche.

## 6. Question 4 — texte

| exigence | état |
|---|---|
| prédictions chiffrées, signées, ouvertes dans les deux sens | P1 à P16, chacune avec son sens contraire ; la justification de P14 tombe avec B10 |
| critères gelés, issue « le nouveau protocole ne fait pas mieux » | D1 à D7, D1b ; I0, I3 (a, b), I4, I1, I2 ; S0 à S3 et T1, T0, T- joints ; inchangés depuis le brouillon 2, justes |
| plan joué recalculé (I1 dans 56 courses sur 60 à 0,75) | **vérifié** : sortie identique à l'octet (`af9c52f8…`) ; 49 au brouillon 2 |
| graines depuis l'empreinte du texte scellé | `lire_preenregistrement` : `int(sha256_fichier(texte), 16)` ; aucune graine en ligne de commande en mode réel |
| couples C6, C8, C9 refaits | leur sens est repris (section 4 : épreuve complète, table des codes en plus ; section 13, points 3 à 5) ; les neuf autres présents mot pour mot |
| un seul marqueur (« À REMPLIR », commit, section 11) | exact ; le lanceur le refuse (`MARQUEUR`) |
| `configuration_sha256` | refusé tant que ce n'est pas une empreinte, puis tant qu'elle diffère de `sha256_fichier(--configuration)` ; le texte ne dit pas « sha256 du fichier » : couples 1 et 4 |
| relevé de l'épreuve | **I11 (important)** : seule une phrase l'annonce, **aucun lanceur ne la refuse** ; un texte scellé sans relevé passerait toutes les gardes. Couples 1 et 2 : un second marqueur « À REMPLIR », que `MARQUEUR` refuse (aperçu vérifié : exactement deux occurrences, aucune mention en clair qui resterait après remplissage) |

## 7. Question 5 — code et banc

- `modeles_servis_permis` : repris de l'adaptateur construit par la configuration (`juges_reels`, l. 343-344), écrit au plan
  (l. 420) ; `classer_resultat` passe la liste à `modele_conforme` ; un identifiant hors liste reste un A2 au premier appel. Levé.
- Lecteur des tables : `verifier_par_les_tables(contenu, dossier)` ne reçoit que la fiche servie (identifiant retiré) et le dossier
  servi ; aucune métadonnée ; il ne contredit que les dix lois fausses. Levé.
- Mutation « durée maximale ignorée » restreinte : la garde n'est pas affaiblie dans le code (`verifier_duree` en tête de chaque passage
  d'`appeler`), et `test_artefact_duree_maximale` la tue sur le chemin sain ; mais **la garde dans la boucle d'attente** n'est essayée que
  par des essais qui ne finissent pas sans elle : une régression qui sortirait `verifier_duree` de la boucle ne serait vue que par un
  essai bloqué. M20 : un essai borné (relais injoignable dès l'appel 1, durée 2 h, adaptateur qui lève au-delà de 10 000 appels) et une
  mutation « garde de durée hors de la boucle d'attente ».
- Contrôle de forme isolé : l'essai neutralise le vocabulaire pour les indices et les indices pour le vocabulaire, et l'indice
  synthétique (aire 0,467 ; 0,200) ne sépare que le sous-ensemble de D1b. Juste.
- Mémoire du contrôle de diagnosticité : copiée après le témoin, vidée avant toute mutation du cœur, **restaurée dans un `finally`**
  après chaque mutation (l. 440-460) ; sur une mutation non appliquée, vidée sans restauration (recalcul, sans effet sur le verdict).

## 8. Question 6 — décisions proposées au directeur (rapport, section 8)

1. **Aucune panne par la durée dans les phases décisives (a)** : tient (R-1276, ligne du GO). Tomberait si l'hôte ne peut être gardé
   48 heures ou si l'échéance du GO (16 novembre) ne laisse plus 48 heures de marge ; à condition d'I10 (le délai doit suivre la même logique).
2. **A2 de B arrête la course (a)** : tient, enjeu faible (depuis I7, ne restent derrière que les phases descriptives). Tomberait si
   l'A2 venait d'un identifiant servi connu mais absent de la liste (erreur de configuration, pas du relais) : (b) garderait alors les
   phases réelles d'Argon.
3. **Parts du GO (a), puis 30/30 si Astra < 0,40 USD (b)** : tient sous condition. Tombe si l'épreuve mesure Argon au-dessus de
   0,074 USD par comparaison (I12 : la part de 24 ne suffit plus), ou si Astra est mesuré au-dessus de 0,40 (alors aucun déplacement n'est
   possible et S0 par la part reste le risque déclaré).
4. **Motif « HTTP 4xx »** : tient (forme « HTTP {code} : » des commandes Argon connues ; l'épreuve provoque un 413 sans dépense). Tombe si
   la ligne diffère : élargir le motif dès le brouillon 4 (M17) coûte moins qu'un texte de plus.

## 9. Points

**Bloquant.** **B10** — B8 non levé : section 3.

**Importants.** **I10** — code 6 compté dans les cinq échecs de suite : I0 au 104e appel (section 4). **I11** — relevé de l'épreuve sans
marqueur ni refus (section 6 ; couples 1, 2). **I12** — prix d'Argon de l'épreuve sans règle (section 5 ; couple 3).

**Mineurs.** **M17** motif de refus de requête étroit (sortie d'erreur seule, 300 caractères, « HTTP » suivi du code). **M18** série
d'échecs prolongée d'une phase décisive dans le bras sans dossier. **M19** coût de l'appel en vol hors du bilan sur interruption ; `SIGHUP`
non converti ; aucun essai par un vrai signal. **M20** garde de durée de la boucle d'attente essayée seulement par des essais qui ne
finissent pas sans elle. **M21** le rapport dit « trois fois » retouchés, le texte en compte quatre (section 9). **M22** le n° 294 n'est
plus sur cette machine : la table des codes est vérifiée sur ses citations (R-1277, contre-lecture v2), pas sur la pièce ; à recopier
dans le dépôt de travail avec son empreinte.

## 10. Couples et suite

`prereg/couples-contre-lecture-juges-idees-v2-v3.json` : 5 couples `{"ancien", "nouveau"}`, texte seul, dans l'ordre d'application ;
chaque « ancien » présent une seule fois dans le brouillon 3 et au moment de son application (`couples/construire.py`) ; aperçu :
833 lignes, exactement deux « À REMPLIR ». C1 statut et marqueurs ; C2 marqueur du relevé de l'épreuve (I11) ; C3 seuil de prix d'Argon
et forme du 413 (I12, décision 4) ; C4 `configuration_sha256` = sha256 du fichier ; C5 marge d'incidents : S0 avant I0. **Ils ne lèvent
ni B10 ni I10**, qui demandent du code.

Avant le scellement, dans l'ordre : (1) code : B10 (ordre de la table 1, seuils des lois fausses, tables croisées, indices et juges neufs,
batterie figée et batterie tenue à l'écart), I10, M17 à M20 ; essais, banc, contrôles, plan joué recalculés ; (2) brouillon 4 : ces
couples, P14, T1 et la section 10 réécrits sur les nouveaux chiffres ; (3) contre-lecture neuve du delta (R2), avec des juges de surface
qu'elle écrit elle-même ; (4) puis la section 13 du texte (épreuve, configuration, relevés, ordonnancement).

## Annexe — sondes de la contre-lecture (`/home/claude/scratch/juges-v3-contre-lecture/`)

| fichier | sha256 | rôle |
|---|---|---|
| `essais.txt` | `3c33b309a43422d67055a2676b2297f9c4862aac9fd807b8a0761c0948dcc714` | suite d'essais rejouée (102, 81 sous-essais) |
| `banc-1-interrompu.txt` | `ed2c30cebfe074bb074a19f4cbbdf7390a5dc23380cdb4f5493127757ffb3950` | banc, premier lancement, tué au redémarrage après 110 mutations (toutes tuées) |
| `banc-2.txt` | `983b1823327954361adac47518de16caa1200b2effd6c429d670e81e71de22f4` | banc relancé une fois : 133 sur 133 |
| `puissance-cl3.json` | `af9c52f874d6f3a8b063166bfe3b987c4092b349d9c8b40e14652c01920aac02` | puissance et plan joué (égal à l'octet au texte) |
| `empreintes-b3.txt` | `ab0e7fb1f5bdb00c02ee8632e3b73b909c3fecfcdf6230c460a93c6d49204e9c` | bloc de la section 11 extrait (égal à l'empreinte que cite le rapport) ; `sha256sum -c` : 62 OK |
| `sondes/diag_cl3.py` ; `.txt` ; `.json` | `ed85432b250403f34698da659d5547e2d2070c19ce1acfb475aac374c55403b0` ; `a258682859a5de745d5833d3ae32871124f781bc47fd3db35d4f83de02eb49dc` ; `673b7e31b730afcead82810d2b8c17500bc65ac8311f405e93a90d19e8892041` | contrôles de forme et de diagnosticité, trois jeux ; indices neufs |
| `sondes/juges_surface_cl3.py` ; `.txt` | `717095c61a93e087229b87382652940b41d14216702e7b34fb28a2ba75f4012a` ; `3aa411e46cbfebe7fde32e8ab530cf144f16829558318186bc8483222a073218` | 40 juges de surface neufs, trois jeux (B10) |
| `sondes/fiches.py` ; `.txt` | `2be1b4289d613f824c35a79667b291e8901311cfc4e10af12fe4a0680661efdd` ; `990b958c26af8f154c4baf52e9ef846bb29126024eabae72c974c68f6e0106eb` | les 36 fiches et les trois dossiers de `mondes-v3` |
| `sondes/traits_fiches.py`, `sondes/lm.py` | `200d5442a8aa84c9ebf920ca5b38da496d2167265d70ddc78a85dae598513087`, `8f75b89294fede73ee887792909a94dbe380aa42dd43bb48a142e8ff812c8360` | traits par fiche ; longueur des mots par classe |
| `courses/delai-5-decisive-a/lecture-juges-idees-v2.json` | `fa88ed59edb993a3c3fb64997875b4761d80025a31a3bd8b94ae8250e6275285` | course à blanc (a) : I0 (I10) |
| `courses/rafale-code3-pire-cas-25/lecture-juges-idees-v2.json` ; journal au fil | `5bfc03e863e3f4bf6f4a1281e61ffc7b5c5ed55a365bc39d2033d7661a181d68` ; `848e1883060869787b6716a68078b68fb640e8f34ec689e5758bb642f5835a1e` | course (b) : égales à l'octet à celles du rapport |
| `courses/requete-413-decisive-a/lecture-juges-idees-v2.json` | `c0babbb13ce3870ae0a48db5c85f6d4491f2d7b372f022c5b3591a0bf16fa7dc` | course (c) : arrêt nommé, I0 |
| `couples/construire.py` ; `couples/apercu-b3-plus-couples.md` | `8ece91ff05d7b0ac8708c304d7e3f5349f77edf5b6926d618fb613d695e149de` ; `a36e7e481b577f233ada27300e6a7ebf19f29aba3cc7b88bf25a62834c825f65` | construction et contrôle des couples ; aperçu (833 lignes, deux marqueurs) |
| `../../ideation-organism/orchestrator/prereg/couples-contre-lecture-juges-idees-v2-v3.json` | `80119546fec70e378b290a685245909e8f02a9fa53be7875e44ba7b9685d65a9` | les 5 couples |

Les sceaux des courses à blanc (compagnons écrits par le lanceur dans le bloc-notes) concordent.
