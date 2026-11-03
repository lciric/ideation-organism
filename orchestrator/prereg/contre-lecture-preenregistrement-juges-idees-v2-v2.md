# Contre-lecture R2 n° 2 — validation des juges d'idéation v2, brouillon 2, et code `juges_idees_v2` (commit public `3e7ca5c`)

3 novembre 2026, de 05:24 à 06:06 UTC (heures de `date -u`). Contre-lecteur neuf : je n'ai écrit ni l'étage des juges
d'idéation, ni le protocole v2, ni ses brouillons 1 et 2, ni la contre-lecture du brouillon 1, ni les essais, le banc ou le lanceur.
Consigne suivie : `/home/claude/controle-ia-travail/brouillons/reprise-conv-audit-2026-11-02-nuit/prompts-sous-agents/contre-lecture-juges-idees-v2-brouillon2-prompt.md`
(sha256 `decf0298a46ef3a2787d2cd02c08e09e5fd814ff3fd306822c3b4d8f87b871a8`, compagnon vérifié). Lecture seule de `ideation-organism`
(tête `d54b85c` au début, `ba4edfe` à la fin, commit d'autrui ; `git diff --stat 3e7ca5c` est vide sur tous les fichiers relus) et des
registres du dépôt de travail. Aucun commit, aucun compagnon `.sha256`, aucun fichier existant modifié, rien sous `donnees/`, aucun
`git fetch`, `checkout` ou `stash`, aucun réseau, aucun modèle ; calculs sous `nice -n 10 python3 -I -B`, `TMPDIR=/tmp`. Le dossier
`../resultats/banc-tricheurs-v9-validation-v1/` n'a pas été ouvert. Sondes et sorties : `/home/claude/scratch/juges-v2/contre-lecture/`
(empreintes en annexe). Numérotation à la suite de la contre-lecture v1 : B8, I6, M8.

**Verdict : non scellable** — le code (matériaux, contrôle de diagnosticité, politique du relais, horloge de panne, ordre des phases, journal) doit changer, puis un brouillon 3 et une contre-lecture neuve du delta.
**Bloquants (2)** : B8 — la lecture des tables (D1b, T1) s'obtient sans lire une table : un juge scripté qui préfère l'ampleur annoncée la plus forte tient D1b 20 fois sur 20 et dépasse, pour D1, l'aire moyenne de 0,62 que le code refuse ; B9 — la politique du relais ne suit ni la commande Argon réelle (n° 294 de session-depot : le quota de Google et toute erreur de l'interface sortent en code 3 au pire cas, le code 4 n'est jamais passager) ni la règle R-1276 : cinq erreurs de suite donnent I0 en quelques secondes (rejoué), un code 4 est attendu 6 heures, la panne de 6 heures coupe la phase décisive de A.
**Importants (4)** : I6 horloge de panne partie du dernier succès ; I7 bras sans dossier joué après B ; I8 aucun journal sur disque avant la fin ; I9 épreuve et configuration à compléter. **Mineurs (9)** : M8 à M16. Le reste tient : essais (79 et 72 sous-essais) et banc (104 sur 104) rejoués à l'identique, B2 au sens strict, B6, B7, puissance, plafond exact de 60 USD, garde de 48 heures en tant que garde, statistiques, contrôle de diagnosticité et vérité des 36 fiches recalculés à l'identique.

## 1. Pièces lues, empreintes

| pièce (depuis `orchestrator/` sauf mention) | sha256 | état |
|---|---|---|
| `prereg/preenregistrement-juges-idees-v2-brouillon2.md` | `c1df7e911c1e0f6b3b342b65a68b65bd7b362759617bfb756ec5eb08a19d9fff` | égal à `3e7ca5c` et à la consigne ; lu en entier |
| `prereg/rapport-redaction-juges-idees-v2-brouillon2.md` | `196b97013d828fdc5cce7f78906a6a3cb19e233e841369e50a1635693bff274a` | dix points et section 10 d'abord, puis en entier |
| `prereg/contre-lecture-preenregistrement-juges-idees-v2-v1.md` | `1dc3c1943c5322731efa7deedd97e9cce7fe7746f6cec268bc05c3f980d43977` | lu en entier |
| `prereg/couples-contre-lecture-juges-idees-v2-v1.json` | `ad48ba2f40287b9a46b79e5e64a243880d0b72b2e95cde06b3dbfc111e55d79a` | 40 couples confrontés au brouillon 2 par script |
| `prereg/preenregistrement-juges-idees-v2-brouillon1.md` | `d72750747c1d07b8fd5fe388e9c6208a150bc60f9eece0140efc76645fb307ef` | consulté |
| `pole/juges_idees_v2.py` | `7eee3b29f10212c169672b39ab75326c2af894f5b031594223656b29313f1067` | égal au rapport ; lu en entier (2 996 lignes) |
| `demonstrations/validation_juges_idees_v2.py` | `01eadabc95dce0206ffd32b9250ef16e8bd505dd7ed43321794ee93a1590fc27` | lu en entier |
| `essais/test_juges_idees_v2.py` | `fbe7afa5f42e4ccc914d0a72d44964e937c18adfaa18f587a527abb4ba9b996e` | classes `Relais`, `Compteur`, `Pannes`, chemin réel lues ; liste des essais |
| `essais/mutations_juges_idees_v2.py` | `7b267ef851e043bb0b62e701660f0940c3a392c10ff38deb104c8eaea4322a0e` | lu en entier |
| `pole/adaptateurs.py`, `pole/adaptateurs_v56.py` | — | `AdaptateurCommandeExterne.lancer` (l. 721-775), `modele_conforme` et `SUFFIXE_DE_DATE` (l. 360-375), v56 (l. 81-95, 120-139) |
| `registres/go.md` (dépôt de travail) | `53985197d3e9780db9bf9738c050c3e746eea149af3e4024649f41db5cedef0a` | ligne 78 relue ; `configuration_v56.verifier_go_v56` : 60 USD admis, 59 et 61 refusés (« pas exactement ») |
| `registres/decisions.md` | `2d8d07f5fd7d69a873f3cc72b25022c1d912ba10755e2968d9aea7f13ad068e8` | a crû depuis `39ef7ecb…` ; lignes 1215, 1230, 1240, 1241 inchangées ; 1257-1258 (R-1293, R-1294), 1264-1265 (R-1300, R-1301) lues |
| `registres/etat.md` | `f425a6842d3d711f419670517895f4a0c609b23b60d37873cdf4f31633f637cd` | lignes 2 et 6 |
| `/home/claude/lectures/session-depot_2026-11-02_n294.md` | `81e601fad368cbf06e8cce0ff30b79f97c5063f5bc263db042356e7bea2878c5` | l'empreinte que R-1293 cite ; égal à la copie de `scratch/a1-v3-1/` ; lu en entier |
| patch interrompu (`controle-ia-travail/brouillons/passation-conv-audit-2026-11-02-soir/travail-interrompu/juges_idees_v2-partiel-sur-516feca.patch`) | `28ef9cf8d2e6c23defd97a6d124eccc7b3ac7c995179204741f4b69628ea0966` | compagnon vérifié ; module patché `scratch/juges-v2/juges_idees_v2-patch-applique.py` `bc64a2a3…` ; relu (relais, constantes) |
| consigne du développeur (`…/prompts-sous-agents/juges-idees-v2-developpeur-brouillon2-v2-prompt.md`) | `558a9f7a75d0f1ad91b2cd49f8e71c655322e0de0d194b5c3c6386fd06141385` | ne cite ni le n° 294 ni la table des codes de la commande |
| sorties du développeur (`/home/claude/scratch/juges-v2/`) | `puissance-b2.json` `6026cdc3…`, `sondes/chiffres-brouillon2.json` `de2f4f94…`, `forme_lois_fausses.txt` `375ee440…`, `forme2_adapte.txt` `85e9b5eb…`, `essais-final.txt` `692d320c…`, `banc/mutations-1.txt` `5fe262fe…`, `banc/mutations-2.txt` `b22b92b1…` | égales au rapport ; six courses à blanc : sceaux vérifiés par `sha256sum -c` |

## 2. Ce qui a été rejoué

- **Essais** : `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py`
  → **79 réussis, 72 sous-essais réussis**, 135,80 s, 05:34:15 à 05:36:32 UTC, code 0. Égal au rapport.
- **Banc, une fois** : `… essais/mutations_juges_idees_v2.py --raisons` → **104 mutations, 104 tuées pour la raison attendue**, 0 pour une
  autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin 73 essais, 0 en échec avant et après ; 05:36:56 à 05:50:49
  UTC, code 0. Égal au rapport (une mutation tuée par un refus non nommé : M15).
- **Une course à blanc** : `demonstrations/validation_juges_idees_v2.py …/contre-lecture/course-rafale-code3 --a-blanc --graine 20261102 --panne-a relais_pire_cas:100-104`
  (juges par défaut : A « indulgent », B « parfait ») : cinq codes 3 au pire cas de suite pour Argon dans sa phase décisive, ce que
  rend la commande réelle sur un quota de Google (B9) → **code 3, `ArretPanne` « 5 échecs coûteux de suite », 104 appels, 7,638 USD,
  0 attente, issue I0** ; cinq pertes, aucune définitive ; sceaux vérifiés ; lecture `ea3e23d1…`, journal `264112cd…`.
- **Sondes sans appel** (bloc-notes, annexe) : vérité des 36 fiches relue à la main sur la table 1 et indices de forme
  supplémentaires (`materiaux_cl2`) ; juges scriptés « ampleur » sur les 20 graines du contrôle de diagnosticité, deux jeux de
  matériaux (`juge_ampleur`) ; horloge de panne (`horloge_panne`) ; contrôle de diagnosticité recalculé (`diagnosticite_cl2`) ;
  seuils exacts par énumération et scipy 1.18.1 (`stats_cl2`) ; puissance binormale par un code et des graines propres (`puissance_cl2`).

## 3. Question 1 — ce qui est levé

| point | levé ? | essai : cas sain / artefact | mutation | remarque |
|---|---|---|---|---|
| B1 témoins séparables sans tables | **non (B8)** | `Materiaux.*` ; `Diagnosticite.test_artefact_diagnosticite_brouillon1` (sain : ce texte ; artefact : brouillon 1 reconstruit) | 10, tuées pour la bonne raison | six indices et sept juges nommés : table du texte rejouée à l'identique (section 12) ; l'ampleur annoncée, non contrôlée, sépare parfaitement lois fausses et bonnes lois |
| B2 statuts lus comme réponses | **oui au sens strict** : aucun statut n'est lu comme une réponse | `Relais` (10), `Pannes` (10), `LanceurCheminReel.test_statuts_du_relais_par_la_vraie_commande_externe` | 13 | la politique qui remplace B2 repose sur une table des codes qui n'est pas celle de la commande réelle : B9 |
| B6 choix des juges | oui | `Plan.test_artefacts_juges_…`, chemin [même relais], [famille des gabarits], [relais absent], [budget par appel] | 6 | GO-2026-11-02-32 (ligne 78) nomme Argon et Astra et exclut Kimi ; reste l'épreuve d'Astra (marqueur) ; la clé d'Astra est sur la fille neuve (R-1294, R-1301) |
| B7 sept gardes sans artefact | oui | les sept artefacts de la table B7 du rapport | les sept, tuées pour la raison attendue (banc rejoué) | — |
| puissance, 15 contre 15, trois mondes | oui | `Statistiques.test_puissance`, `test_binomial_exact`, `test_aire_et_mann_whitney` | 3 | D1 0,927 à une aire de 0,8 (0,924 sur 200 000 répétitions, M13) ; D1 et D4 0,894 ; plan joué : I1 dans 49 courses sur 60 à 0,75 (JSON relu) |
| plafond exactement 60 USD | oui | chemin [plafond au-dessus de 60], [parts au-dessus du plafond] ; GO de 25 USD « pas exactement » | 3 | bloc `plafond_usd: 60`, parts 24 et 36 ; `verifier_go_v56` rejoué à 59 et 61 : refusé |
| garde de 48 heures | oui comme garde ; **mais** la panne de 6 heures coupe la phase décisive de A (B9-iii) | `Compteur` [durée 0, −1, infinie], `Pannes.test_artefact_duree_maximale`, chemin [durée nulle], [durée haute] | 4 | — |
| bras « ancien sans dossier » | oui : joué, mesuré, lu S0 à S3 ; **exposé** (I6, I7) | `Entrees.test_entree_ancienne_sans_dossier_identique_a_la_v53`, `Mesures.test_bras_sans_dossier_mesure`, `Lecture.test_lectures_jointes_bras_et_tables`, course factice complète (30 appels) | « S1 confondue avec S2 » | joué après les deux phases de B |

## 4. Question 2 — une panne, un refus ou un quota peut-il rendre la course non concluante par défaut de conception ?

Oui, par sept chemins (lus dans le code, rejoués ou sondés) :
1. **Rafale d'erreurs de l'interface d'Argon** (quota de Google, erreur 5xx, coupure) dans la phase décisive de A : code 3 au pire cas,
   échec coûteux sans attente, cinq de suite → panne → arrêt de la course → I0 (course à blanc : I0 au 104e appel, 0 attente). B9-i.
2. **Code 4 déterministe** (plafond propre ou nombre d'appels du relais 8805, pire cas au-dessus du budget par appel, registre) :
   attendu jusqu'à 6 heures, puis panne → I0 dans la phase décisive de A ; 6 heures perdues ailleurs. B9-ii.
3. **Relais injoignable plus de 6 heures** dans la phase décisive de A (le conteneur de conv-audit a été réclamé de ≈ 01:00 à 05:15
   UTC cette nuit, R-1300) → I0, alors que la garde de 48 heures laisserait reprendre. B9-iii.
4. **Juge rappelé après plus de 6 heures sans appel** (bras sans dossier après une panne de B ; 21 905 s d'écart dans la course
   « panne » du rapport) : panne au premier « rien d'envoyé », sans aucune attente → bras non joué → S0. I6.
5. **A2 du juge B** (y compris un identifiant servi daté à tirets, que `modele_conforme` refuse) : arrêt de la course après la phase
   décisive de A ; le bras sans dossier, joué après B, est perdu (S0). I7.
6. **Processus tué** (redémarrage, conteneur réclamé, signal) : seuls le manifeste, les matériaux, le plan et le registre des
   commandes sont sur disque ; tout ce qui a été payé est perdu ; aucune règle écrite. I8.
7. **Configuration** : budget par appel sous le pire cas réservé d'une commande, sortie d'Argon tronquée (code 5), identifiant servi
   non admis — rien de cela n'est vu par `--verifier-seulement`, qui ne fait aucun appel. I9.

Ce qui tient : hors de la phase décisive de A, une panne, une part épuisée ou des réponses inexploitables de B n'arrêtent que B (essais,
mutations « arrêt du juge B étendu à toute la course » et « juge arrêté : ses étapes suivantes jouées quand même » tuées ; course
« panne » du rapport : I1 avec la réserve « accord du juge B non mesuré ») ; les comparaisons de B passent avant son ancien protocole
et la projection étape par étape garde D6 mesurable jusqu'à environ 1,6 USD par appel d'Astra (calcul : 32 comparaisons en trois
étapes dans 36 USD). **Règle écrite d'avance pour les comparaisons perdues** (section 8) : une perte définitive manque au journal des
réponses, sort de l'ajustement de Bradley et Terry comme une comparaison nulle, est comptée à part, et au-delà de 15 % des appels
prévus de la phase décisive de A donne I0 « infrastructure » ; elle est codée (`jouer_etape` l. 2066-2073, `_garde_pertes`
l. 1990-1998, `lire_validation` l. 2471-2473), essayée (`Relais.test_reprise_bornee_puis_perte_definitive`,
`test_artefact_pertes_definitives_au_dela_de_15_pour_cent`) et ses mutations sont tuées. Mais elle est **préemptée** par la panne à
cinq échecs : dans la course à blanc, cinq pertes, aucune définitive, et déjà I0. Et une perte définitive dans les 30 appels de l'ancien
protocole compte comme un verdict manquant : quatre suffisent à I0 sous la règle des 27 sur 30 (M14).

## 5. Points bloquants

**B8 — La lecture des tables (D1b, T1) s'obtient sans lire une table : l'ampleur annoncée sépare parfaitement lois fausses et bonnes lois.**
Constat. Les lois fausses affirment un écart tiré dans `ECARTS_FAUX = (6, 7, 8)` (l. 483) ; les bonnes lois recopient l'écart de la
table, qui vaut ici de 9 à 18 points (interactions : 27 à 31 points dans la catégorie, différences d'écarts de 19 à 28) ; le seuil de
prédiction suit `_seuils` (l. 627-629, moitié de l'écart) :
**les 7 lois fausses d'évaluation annoncent « au moins 3 points », les 15 bonnes lois au moins 4** (4 à 14). Aire de l'indice « seuil
de prédiction » : **1,000 entre bonnes lois et lois fausses**, 0,640 entre bons et mauvais témoins (`materiaux_cl2.txt`). Ni l'écart
affirmé ni le seuil ne sont dans `INDICES_FORME` (l. 929) ni dans `VARIANTES_FORME` (l. 939-940). Joué sur le plan v2 du juge A au
tirage 1 et les 20 graines fixes du contrôle de diagnosticité (`juge_ampleur.txt`) : un juge scripté qui ne lit **ni le dossier ni les
tables** et préfère la fiche au seuil de prédiction le plus haut tient **D1b 20 fois sur 20** (aire moyenne des lois fausses contre les
bonnes 0,958, minimum 0,876) et D1 2 fois sur 20 avec une **aire moyenne de 0,624** ; s'il préfère l'écart affirmé le plus grand :
D1b 20 sur 20 (0,958), aire moyenne 0,629. Sur les matériaux du brouillon 1, D1b 16 et 18 fois sur 20 : le défaut est ancien, ni la
contre-lecture v1 ni le développeur ne l'ont vu. La consigne v2 demande quelle loi « mérite le plus d'être mise à l'épreuve » et range
en quatrième critère « l'ampleur et le signe annoncés » : un juge réel qui préfère les lois les plus franches, sans ouvrir une table, est
plausible.
Conséquence. T1 « lecture des tables établie » peut être prononcé pour un juge qui ne lit aucune table ; les phrases « c'est D1b qui la
mesure » (section 4) et « seule D1b mesure la lecture des tables » (section 10) sont fausses ; P14 et H2b ne se séparent pas de H0(a)
« tranchent par la forme ». Côté D1, l'aire moyenne de ces juges (0,624 et 0,629) dépasse `DIAGNOSTICITE_AIRE_MAX = 0,62` (l. 933) : le
code refuserait ces matériaux si ces juges étaient parmi les siens. Le B1 de la contre-lecture v1 n'est donc pas levé.
Correction (code, matériaux, texte ; nouvelle empreinte, nouveau banc). Tirer l'écart affirmé de chaque loi fausse dans la loi des
écarts vrais de son monde (même gabarit), pour que seuils et ampleurs se recouvrent ; ajouter « écart affirmé » et « seuil de
prédiction » aux indices de forme, bornés des deux côtés, mesurés sur l'évaluation **et sur le sous-ensemble de D1b** (ce qui couvre
aussi la longueur 0,657 et les chiffres 0,638 du point 2 du rapport) ; ajouter les juges « seuil » et « ampleur » et leurs combinaisons
lexicographiques avec « interaction » (trois bonnes fiches, aucune mauvaise : aire 0,6) et « signe moins » (M12) aux juges de forme,
tenus à D1 et à D1b ; artefact : les matériaux `59737a16…` refusés ; mutation.

**B9 — La politique du relais ne suit ni la commande Argon réelle ni la règle R-1276.**
Source. N° 294 de session-depot (2 novembre, 22:54 UTC, `81e601fa…`, section 3 : lecture du code du relais 8805 et de
`commande_argon_v56_nuit_v2.py`, `221df610…`), lu par le directeur à 23:32 UTC (R-1293, ligne 1257), non transmis au développeur
(sa consigne `558a9f7a…` ne le cite pas) : le relais ne reprend aucune erreur (« `attentes=(0,)` ») ; « toute erreur de l'interface
revient au relais comme `echec` … la commande sort alors en **code 3 au pire cas réservé** (`envoye=true`) » ; « HTTP 429 de Google
(quota) → … code 3 au pire cas » ; « `--plafond-usd` du relais → HTTP 402 ; `--max-appels` → HTTP 429 ; la commande lit 402 et 429
comme **code 4 au plancher** » ; section 4, TF-02 : la commande sort aussi en code 4 quand le pire cas dépasse le plafond de session.
(i) **Code 3 au pire cas : aucune attente, puis panne.** Le texte (section 8) le range en « échec coûteux (code 3 après envoi …) » ;
`appeler` (l. 1963-1974) ne l'attend pas, `jouer_etape` le remet en fin d'étape et appelle `verifier_echecs_couteux` (l. 2071), qui
déclare la panne au cinquième de suite (l. 1858-1860) ; dans la phase décisive de A, l'arrêt remonte à la course (l. 2146-2149) : I0.
Rejoué : I0 au 104e appel, en quelques secondes d'horloge, 0 attente. Pour la même commande, A1-v3.1 (scellé, `ba4edfe`) attend tout
code 3, « à coût plancher (rien n'a été envoyé) comme au pire cas » (`pole/attaque_goodhart_v3.py` au commit `3e7ca5c`, l. 88-90).
(ii) **Code 4 attendu 6 heures sur une prémisse fausse.** Le rapport (section 2) le reprend « parce qu'un 429 est passager » ; pour
cette commande, le 429 passager (celui de Google) sort en code 3, et le code 4 n'est jamais passager (402 et 429 propres du relais,
pire cas au-dessus du budget par appel, registre). Effet : 6 heures d'attente puis panne — I0 dans la phase décisive de A ; pour B,
par exemple quand le reste de sa part tombe sous le budget minimal de la commande, 6 heures perdues puis B en panne. La commande
factice de `test_statuts_du_relais_par_la_vraie_commande_externe` (l. 1376-1399) rend « code 4 : 429 » au plancher : elle ne reproduit
pas la commande réelle. La contre-lecture courte du tour fermé v6 (B11, `d54b85c`) lit le n° 294 de la même façon.
(iii) **La panne de 6 heures coupe la mesure décisive.** Dans la phase décisive de A, un relais injoignable plus de 6 heures donne I0,
alors que la garde de 48 heures laisserait reprendre ; c'est un budget de temps qui coupe une mesure décisive, contraire à la règle
prise sur les mots de Lazar (R-1276, ligne 1240 : « aucun budget de temps qui coupe une mesure décisive (gardes contre une boucle folle
seulement) ») et à la ligne du GO (« garde de durée 48 h (boucle folle seulement) ») ; le développeur l'a laissé « à trancher » (point 5).
Correction (code, texte, essais, banc). Code 3, au plancher comme au pire cas → même appel repris après des attentes croissantes
(jusqu'à 30 minutes entre deux tentatives au pire cas), le pire cas compté dans la dépense hors du prix observé, borné par la part
et la projection — jamais par un compte d'échecs de suite ; panne = durée sans réponse depuis le premier échec de la série en cours
(I6) ; dans les phases décisives, aucune panne avant la garde de 48 heures (ou un seuil long que le directeur fixe ; proposer avec
recommandation) ; code 4 → refus de budget : arrêt du juge hors de la phase décisive de A, arrêt de la course dans celle-ci, nature
écrite, comme A1-v3.1 et le tour fermé v64, et prévenu par les relevés d'I9 ; la règle des cinq échecs de suite gardée pour les codes 2,
5, 6, la commande muette et le dépassement, avec des attentes entre eux ; essais du chemin réel avec la vraie table (quota de Google =
code 3 au pire cas ; 402 et 429 du relais = code 4 au plancher), mutations ; marge d'incidents d'Argon écrite au devis : 24 − 17,11 =
6,89 USD, soit une trentaine de tentatives au pire cas réservé si celui-ci vaut ≈ 0,23 USD (barème prudent de la commande : 10 et 50 USD
par million, caractères divisés par 3, 4 000 jetons de sortie pour un rôle autre que proposeur ; n° 294, section 4 ; à mesurer, I9).

## 6. Points importants

**I6 — L'horloge de panne part du dernier succès du juge, pas du début de la série d'échecs.** `Compteur.debut_essais` (l. 1842-1843)
ne pose la référence qu'au premier appel de la course (`setdefault`) ; `verifier_panne` (l. 1849-1853) compare l'heure au dernier
succès. Sondé (`horloge_panne.txt`) : succès à t = 0, sept heures passées sur l'autre juge, premier « rien d'envoyé » → `ArretPanne`
après un appel et **zéro attente**, avec le message « malgré les attentes », faux. Cas réel : 21 905 s séparent la phase décisive de A
de son bras sans dossier dans la course « panne » du rapport. Correction : référence = premier échec depuis le dernier succès, remise à
zéro sur succès ; artefact (longue pause puis un échec au plancher : attentes, pas de panne) ; mutation. Nouveau dans la réécriture :
le patch bornait l'attente par appel (30 minutes), sans horloge de juge.

**I7 — Le bras sans dossier est joué après les deux phases de B.** Un A2 de B (arrêt de la course, `ArretModeleServi` n'est pas un
`ArretJuge`), la garde de 48 heures pendant les attentes de B, ou I6 après une panne de B le font perdre (S0). Il coûte 30 appels
d'Argon (1,86 USD) sur la part de A, et le relais d'Argon est chaud juste après la phase décisive de A. Recommandation (routine) :
jouer `sans-dossier-a` juste après `decisive-a` (`PHASES_V2` et `etapes_v2`), projection « toute la phase » inchangée ; et demander si un
A2 de B doit arrêter la course ou seulement B (A2 exige de ne jamais servir la réponse d'un autre modèle, ce que l'arrêt de B suffit à
tenir ; aucune bascule). Identifiant servi : `SUFFIXE_DE_DATE` (`pole/adaptateurs.py` l. 362) n'admet que `-AAAAMMJJ` ; un identifiant
daté à tirets serait un A2 au premier appel de B : l'épreuve le relève, la configuration l'admet par `modeles_servis_permis` (couple).

**I8 — Aucun journal sur disque avant la fin de la course.** `executer_validation` tient le journal en mémoire ; le lanceur ne l'écrit
qu'à la fin ou sur un `ArretJuges` (`validation_juges_idees_v2.py` l. 523-532, 635-648) ; un signal d'arrêt, une interruption clavier
(non prise par `except Exception`, l. 2165) ou un conteneur réclamé ne laissent que le manifeste, les matériaux, le plan et le registre
de dépense des commandes ; les dossiers de session sont dans un `tempfile.mkdtemp` hors de la sortie (l. 399). Vu cette nuit : machine
redémarrée vers 01:07 UTC (rapport, section 10), conteneur réclamé de ≈ 01:00 à 05:15 UTC (R-1300). Le texte dit « une seule fois »
sans règle pour une course tuée. Correction : journal ajouté au fil de l'eau (une ligne JSON par réponse et par perte, vidée sur
disque) dans la sortie, scellé à la fin ; règle écrite d'avance : course tuée = I0 « infrastructure », dépense relue au registre des
commandes, aucune relance sans GO de Lazar (ou une règle de reprise écrite d'avance).

**I9 — Épreuve et configuration à compléter avant le scellement** (texte, sections 4 et 13 ; couples).
(a) Argon dans le rôle de juge n'a jamais été mesuré sur une comparaison (A1 : proposeur ; 1er novembre : ancien protocole) ;
`--max-sortie-court` vaut 4 000 jetons pour tout rôle autre que proposeur (n° 294, section 4, TF-04) : une sortie tronquée est un code 5,
échec coûteux. Deux ou trois appels d'Argon sur l'entrée de comparaison la plus longue rejoignent l'épreuve.
(b) Le réglage d'effort d'Argon est déjà connu : aucun (défaut de l'interface, TF-04) ; il s'écrit maintenant.
(c) `plafonds_session.juge` doit valoir au moins le budget minimal accepté par chaque commande pour l'entrée la plus longue et deux fois
le coût par appel le plus haut relevés à l'épreuve, pas seulement deux fois le prix de plan : sinon chaque appel sort en code 4 ou en
dépassement (cinq de suite : panne).
(d) Avant la course : réglages propres du relais 8805 (`--plafond-usd`, `--max-appels`, réglé et engagé) relevés et suffisants.
(e) Sur un code 5, la dernière ligne dit-elle `modele_servi` et `refus` ? Le code 5 de la commande d'Argon couvre aussi « modèle servi
différent, refus du modèle, tronquée, vide » (`pole/attaque_goodhart_v3.py` au commit `3e7ca5c`, l. 78, d'après le n° 287 ;
`prereg/preenregistrement-attaque-goodhart-v3-brouillon4.md`, l. 755-757) ; si la ligne ne le dit pas, un A2 et un refus du modèle
deviennent ici des échecs coûteux, repris puis comptés en panne, au lieu d'un arrêt A2 et d'une réponse inexploitable.
(f) La dépense de l'épreuve n'est dans aucun devis : sous quel GO ?
(g) La machine : la clé d'Astra est sur la fille neuve (R-1294, R-1301), pas sur le compte de session-depot du n° 294.

## 7. Points mineurs

- **M8** — Sources du devis (section 12) : « `pole/attaque_goodhart_v3.py`, lignes 84-85 de ce dépôt, sha256 `b821bdb7…` », « ligne 91 »,
  « lignes 82-83 » valent au commit `66dbcf1` ; au commit du brouillon (`3e7ca5c`), le fichier est la v3.1 (`cb9cffe7…`) et les mêmes
  valeurs sont aux lignes 103-106 et 112. Couples.
- **M9** — `registres/decisions.md` vaut maintenant `2d8d07f5…` (lignes citées inchangées) : empreinte à relever au scellement. Couple.
- **M10** — Constantes mortes : `CLASSES_HORS_TABLES` (l. 97) et `A_PRIORI` (l. 204), venues du patch, et `ROLES` (l. 98).
- **M11** — Le juge « dossier sans tables » ne voit pas la redite de monde-2 (`defauts_hors_tables` cherche « présence d'un champ de
  paiement » dans R2, qui dit « comportant un champ de paiement ») : son D1 de 15 sur 20 sous-estime ce que permet la lecture du
  contenu sans les tables ; à dire à la section 4.
- **M12** — Le champ « signe » vaut « - » sur trois bonnes fiches et sur aucune mauvaise (aire 0,600 sur les deux ensembles ; de même la
  prédiction négative) ; à équilibrer avec B8 (par exemple une loi fausse décroissante).
- **M13** — Puissance de D1 à 15 contre 15 et une aire de 0,8 : 0,927 à la graine 20261102 ; 0,9238 sur 200 000 répétitions (mon code),
  0,9235 par le module à la graine 7 : bruit de simulation ; « au moins 0,9 » tient. Couple.
- **M14** — Validité : une perte définitive d'un des 30 appels de l'ancien protocole compte comme un verdict manquant (quatre → I0) ; et
  un arrêt de la course après la phase décisive de A n'est pas I0 par lui-même (la lecture « partielle » est la lecture gelée) : à dire.
  Couples.
- **M15** — La mutation « lanceur : relais d'un juge absent admis » est tuée par un `KeyError` que le lanceur rend en refus non nommé
  (code 2) : aucun repli silencieux ; à dire au rapport.
- **M16** — A1-v3, scellé (R-1301), emploie le même relais à un fil jusqu'à 72 heures ; GO-2026-11-02-32 échoit le 16 novembre :
  ordonnancement à écrire à la section 13. Couple.

## 8. Question 3 — prédictions, critères, audit, graines, devis, plafond

| exigence | état |
|---|---|
| prédictions chiffrées et signées, ouvertes dans les deux sens | P1 à P16, chacune avec son sens contraire et ce qu'il dirait ; évaluées par `predictions_v2`, jamais lues comme issue ; P14 n'est pas séparée d'un juge qui suit l'ampleur annoncée (B8) |
| critères gelés, issue « le nouveau protocole ne fait pas mieux » | D1 à D7 et D1b ; I0, I3 (a, b), I4, I1, I2 dans cet ordre ; S0 à S3 et T1, T0, T- joints sans changer l'issue ; seuils égaux au code (`Lecture.test_seuils_du_texte_egaux_au_code`) ; D1, D4, D5, D6 choisis après les simulations (déclaré, section 9) : défendables — un juge nul passe D1 et D4 ensemble environ 5 fois sur 1 000, la course « biaisée de position » donne bien I4 (D4, D5), D5 à 0,15 garde la réserve « préférence modérée » |
| audit de symétrie | déclencheurs dans les deux sens, une seule liste (`Lecture.test_audit_symetrique`) |
| graines | entropie = entier de l'empreinte du texte scellé (`lire_preenregistrement` l. 248-249 ; `LanceurCheminReelComplet`) ; matériaux et contrôle de diagnosticité à graines fixes, propriété des matériaux |
| devis par juge | Argon 0,062 USD et 7,6 s (R-1266, ligne 1230, relue) ; chiffres recalculés : 276 appels et 17,11 USD, au plus 69 et 34,50, 51,61 requis, 302 et 18,72, 95 et 47,50, 39,36 et 48,86 attendus, 0,88 à 6,07 heures ; Astra : la borne de 0,50 USD (≈ 9 000 jetons de sortie au prix supposé) n'est pas prudente pour un effort élevé, mais D6 reste mesurable jusqu'à ≈ 1,6 USD par appel ; le budget par appel doit suivre l'épreuve (I9-c) ; marge d'incidents non écrite (B9) |
| plafond exactement 60 USD | oui : bloc, lanceur (`PLAFOND_MAX_USD = 60`) et GO exact (59 et 61 refusés) |

## 9. Question 4 — couples de la contre-lecture v1

Confrontés au brouillon 2 par script : C3, C5, C14, C17, C19, C26 présents mot pour mot ; C6, C9, C11, C25, C28 précisés sans changer le
sens ; les adaptés et refaits portent les valeurs de GO-2026-11-02-32 (relu) et du code (recalculé). Les raisons tiennent, sauf :

| couple | sort annoncé | constat |
|---|---|---|
| C7 | refait (rééquilibrage, six indices, diagnosticité) | fait et rejoué à l'identique, mais B1 non levé pour D1b (B8) |
| C30 | refait (code 4 attendu, code 3 au pire cas perdu, panne de 6 h) | la raison « un 429 est passager » ne tient pas pour la commande Argon (n° 294) : B9 ; reprises en fin d'étape et arrêts par juge : tiennent |
| C33 | refait (sources écrites) | une source citée à l'empreinte d'un fichier changé depuis (M8) |
| C2 | refait (trois marqueurs) | conforme à la consigne ; la part Argon des réglages est déjà connue (I9-b) |
| C24 | adapté (règle des pertes) | écrite et codée ; préemptée par la panne à cinq échecs (section 4) |
| C40 | adapté (avant la course) | à compléter : relevés du relais 8805, ordonnancement avec A1-v3 (I9-d, M16) |

## 10. Question 5 — marqueurs restants

Exactement trois, comme la consigne les permet : `<<CONFIGURATION_SHA256>>` (deux occurrences), `<<EMPREINTE_DU_CODE>>` (62 lignes, une par
fichier de la fermeture, plus la mention du statut ; essai `Fermeture` réussi) et `<<EPREUVE_ASTRA_8807>>` (deux) ; aucun marqueur de GO
(GO-2026-11-02-32 est écrit et passe le vérificateur gelé). Le bloc d'empreintes ne peut pas être rempli avant les changements de code
de B8, B9, I6 à I8 ; la liste de l'épreuve est à étendre (I9, couple).

## 11. Question 6 — ce que le patch interrompu a laissé

- Code 4 : le patch l'arrêtait (« dépense ») ; la réécriture l'attend 6 heures sur la prémisse d'un 429 passager, fausse pour la commande
  Argon : l'arrêt du patch était plus proche de la commande réelle (trop fort hors de la phase décisive de A). B9-ii.
- Code 3 au pire cas : ni le patch (perte) ni la réécriture (perte, reprise, panne à cinq) ne l'attendent : défaut non corrigé. B9-i.
- La réécriture a remplacé la borne de 30 minutes par appel du patch par une horloge de juge qui part du dernier succès : défaut neuf. I6.
- Constantes du patch restées sans usage : `CLASSES_HORS_TABLES`, `A_PRIORI`. M10.
- Seuil d'aire du contrôle de diagnosticité : 0,60 au patch, 0,62 ici (déclaré, choisi après mesure) ; le juge « seuil » de B8 (0,624)
  échoue aux deux.
- Matériaux « mondes-brouillon1 » reconstruits (`f4ff3485…`), non égaux à l'octet à `c3eeb559…` (déclaré) : rejoués, refusés pour les
  mêmes motifs (trois juges de forme, D1b 17 sur 20).
- Rien d'autre de faux dans ce qui a été repris (trois mondes, étiquettes d'a priori, genres « loi fausse graduée » et « signe
  contraire », compteur à parts, A2 sur le statut « refus » selon `refus.evenement`, phase du bras sans dossier) : relu, essayé, banc.

## 12. Recalculs indépendants

- **Mann et Whitney exact** (énumération) : 15 contre 15, U ≥ 153 sur 225 (aire 0,680), niveau 0,0488 ; au niveau 0,10, U ≥ 145 (0,644),
  0,0936 ; 15 contre 7, U ≥ 77 sur 105 (0,733), 0,0455 ; 10 contre 10, 73 (0,0446) ; 20 contre 20, 262 (0,0482). Égaux au texte.
- **Binomial exact** (énumération et `scipy.stats.binom`) : k critique 14, 16, 18, 21, 23, 24 pour 20, 24, 28, 32, 36, 39 comparaisons,
  niveaux 0,0577, 0,0758, 0,0925, 0,0551, 0,0662, 0,0998, puissances égales au texte. **Plafond de Spearman** : 0,7508.
- **Puissance binormale** (code et graines propres) : D1 0,922, 0,921, 0,924, 0,922 (20 000 répétitions chacun), 0,9238 sur 200 000 ;
  D4 0,965 ; D1 et D4 0,891 ; D1b à 15 contre 7 et 0,8 : 0,772. Égaux au texte dans le bruit (M13).
- **Contrôle de diagnosticité** recalculé sur les deux jeux : les deux tables de la section 4 du texte, à l'identique.
- **Matériaux** : empreinte `59737a16…` (tentatives 0, 6, 10), `verifier_materiaux` vide, six indices 0,624, 0,531, 0,500, 0,467, 0,520,
  0,527 ; les 36 fiches relues à la main sur la table 1 (par exemple monde-1-07, tests exécutés : 25,0, 24,6, 25,7 contre « 25 % → 31 % » ;
  monde-2-08, jour : 29,5 contre 30,7 pour « 37 % contre 29 % » ; monde-3-11, signe contraire : hypothèse 38 → 20 juste, prédiction
  « supérieur d'au moins 9 points » contraire) : aucune erreur de classe ; le défaut est ailleurs (B8).

## 13. Couples et suite

`prereg/couples-contre-lecture-juges-idees-v2-v2.json` : 12 couples `{"ancien", "nouveau"}`, texte seul, dans l'ordre d'application ;
chaque « ancien » est un texte exact du brouillon 2, présent une seule fois, et le reste au moment de son application ; construits et
contrôlés par `couples/construire.py` du bloc-notes ; aperçu du texte obtenu : 668 lignes, `bf68deb4…`, trois marqueurs. Ils corrigent
M8, M9, M13, M14, M16 et écrivent les demandes d'I9 ; **ils ne lèvent ni B8 ni B9, ni I6 à I8**, qui demandent du code.

Avant le scellement, dans l'ordre :
1. Code : B8 (matériaux, indices, juges de forme, nouvelle empreinte), B9 (politique du relais), I6, I7, I8 ; un essai sur un cas sain et
   sur un artefact par garde, une mutation chacune ; banc complet ; courses à blanc dont une rafale de codes 3 au pire cas dans la phase
   décisive de A (doit attendre, pas I0), un code 4 (arrêt nommé, immédiat), une longue pause puis un échec au plancher (attente, pas
   de panne).
2. Brouillon 3 : ces couples, le texte des règles neuves, les tables recalculées.
3. Épreuve (I9) par la fille neuve, configuration, relevés du relais 8805.
4. Contre-lecture neuve du delta (R2), puis la suite de la section 13 du texte.

## Annexe — sondes de la contre-lecture (`/home/claude/scratch/juges-v2/contre-lecture/`)

| fichier | sha256 | rôle |
|---|---|---|
| `essais.txt` | `3cf88f8b4360670e0932455ec3ac26efe3d28fa154101ff7053b7c3ab50487e9` | suite d'essais rejouée |
| `banc.txt` | `5c1b0efd9a477bb53518bbe86a9db13ed99b5efcb93a84a6716ad18248f5ab7a` | banc de mutations rejoué une fois |
| `course-rafale-code3.err` | `eb2980830933fa6f6409f7b1ceeea733a42fdb09550b830ba6b39d161eb12d41` | course à blanc : arrêt, I0 |
| `course-rafale-code3/lecture-juges-idees-v2.json` | `ea3e23d1ae524a0fd47cee6d1a68bd0ee570aabdc2d9984e1aeea8259a7baf15` | lecture partielle scellée par le lanceur |
| `course-rafale-code3/journal-juges-idees-v2.json` | `264112cd26d0edf6e183e245363b3d51b5dc31698a34ed84cd156aa9cb9120e7` | journal partiel |
| `sondes/materiaux_cl2.py` ; `.txt` | `beb19dc17f2abf4eed3c38c21be1c43b5b0afa9c501dfff4d997e9bbad0ecec8` ; `e353d0bc9b82f9b648083a4efb3733b0a876e0f7305f6c13eab73a24e4cb584a` | vérité des fiches, indices de forme supplémentaires |
| `sondes/juge_ampleur.py` ; `.txt` | `5e1afe08bd5f2054bb8357e3cc58b1046031e5c2746573646aa80cd913a1c3d9` ; `ba591b07faec8f553116e2944c8dcbe92c27cd9393a339b188cf739d032d6358` | juges « seuil » et « ampleur » (B8) |
| `sondes/horloge_panne.py` ; `.txt` | `4c838667bf81dc1f121d7eb8d63e582f2ad10953ed83bc9825f88570bfe7c489` ; `6f8b98f86a2c826c254e73a509dfe20b575ee3d7e50f33c65a2d36d84eaea729` | horloge de panne (I6) |
| `sondes/diagnosticite_cl2.py` ; `.txt` | `f75a4a6f9a27edc792c4d562967ebea4dd6cc6f0378f048f4256289730b4dc60` ; `2fdb39d2983ab086fb4895a7a1f34c902fe2eb0106ce286b6edbc08e31ca9a56` | contrôle de diagnosticité recalculé |
| `sondes/stats_cl2.py` | `b2e8f032873b559c7456d4c0891eb2cfb5c7dd138f265465e60f7f0fd79f6536` | seuils exacts |
| `sondes/puissance_cl2.py` | `4b7d97c1497ef514188f2b0b99f51d6509204c54b442a431844fa2d85e2d8720` | puissance binormale |
| `couples/construire.py` | `511c82905d4e0c30818fb68b0b78b03f479726c62366b64131c2cdd245dc8594` | construction et contrôle des couples |
