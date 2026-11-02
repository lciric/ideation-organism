# Rapport de rédaction — préenregistrement du tour fermé (A2, A3, A4), brouillon 1

2 novembre 2026, de 07:02 à 07:40 UTC environ. Sous-agent rédacteur. Aucun appel de modèle, aucune clé lue, aucun commit,
aucun `git fetch`, aucun scellement (aucun compagnon `.sha256` posé dans l'arbre), aucun fichier existant modifié ; calculs
sous `nice -n 10`. Dépôt public à la tête `7fadf96`. Dépôt privé lu en lecture seule (branche `canal/conv-audit-n04`), sur
`CLAUDE.md`, `docs/notes/ideation-organisme-v1/` et `brouillons/` seulement : rien sous `donnees/`, aucune ref `donnees/*` ni
`calcul/*`, le dossier `bras-attaque-v1/` non ouvert.

## 1. Fichiers neufs (depuis `orchestrator/`) et empreintes SHA-256

| fichier | rôle | sha256 |
|---|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon1.md` | le préenregistrement (deux étages, 579 lignes) | `09b9dfcc7aa55eef4739a50cc989f7c8967686b5e59659b7bb83520b954f5e52` |
| `pole/reserve_tenue_a_l_ecart_v60.py` | réserve par empreinte des données tenues à l'écart (A3), vérification au montage | `2399d5eca73e5a5f832c72a0b62c0c9110ae238ea2b48a31cab318a00e43edc0` |
| `demonstrations/reserve_tenue_a_l_ecart_v60.py` | ligne de commande de la réserve (empreintes et comptes seulement) | `2c9a60e9232770090df545de3bd3ac2f2e4b2dabe52182fa708515865d3c79db` |
| `pole/oracle_tour_ferme_v60.py` | oracle (G, D, G_arch à la classe du nul v8, ΔG), classement gelé VD / VD* / FD, Wilson, Newcombe | `514864b7879e5131ee37f7a57951db5ece514abe9acbd90b1294e0d914041669` |
| `pole/lecture_tour_ferme_v60.py` | lecture gelée : critères T1 à T5, issue A4, issues N / P / Z de A3, audits S1 à S5 | `f7f5101ed32a52e2c1866ab9a06892c083abfab07684398c17a326ebf8990261` |
| `essais/test_v60_reserve_tenue_a_l_ecart.py` | 15 essais (cas sain et artefact) | `470e48a72f31e48effaea7fb11256224a639705e2b08e0963c08c08e671bb0f1` |
| `essais/test_v60_oracle_tour_ferme.py` | 14 essais | `142f48cd083b86c8ca885ba339f08f449cffacb7a6ca45e58721f6c4a20cbd7b` |
| `essais/test_v60_lecture_tour_ferme.py` | 17 essais | `ef2f530166c81fcc62fbad91d1ba0ae4c6e09ac6db5bf9c8cb1113ef0d5e5751` |
| `essais/mutations_v60.py` | banc de mutations (mécanique du banc v56) | `87377f841b55e59dc1b08802b16dd8534fec5d1f4730b360b443da501c73773e` |
| `prereg/rapport-redaction-tour-ferme-v1.md` | ce rapport | (non auto-référencé) |

`git status` montre aussi `pole/attaque_goodhart_v2.py`, `demonstrations/attaque_goodhart_v2.py` et
`essais/test_attaque_goodhart_v2.py`, non suivis : **ils ne sont pas de ce rédacteur** (apparus pendant la session, sans doute
le travail parallèle sur A1) ; non lus, non touchés. Aucun fichier suivi n'est modifié (`git diff --stat` vide).

Les noms `_v60` sont pris par ces fichiers : le lanceur et le cœur restant à écrire sont nommés `pole/tour_ferme_v60.py`,
`demonstrations/tour_ferme_v60.py`, `essais/test_v60_tour_ferme.py`, `essais/mutations_v60_tour_ferme.py` (section 13 du texte).

## 2. Essais et banc

- `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v60_reserve_tenue_a_l_ecart.py essais/test_v60_oracle_tour_ferme.py essais/test_v60_lecture_tour_ferme.py` :
  **46 réussis**, 0 échoué, 0 ignoré (≈ 2 s).
- `nice -n 10 python3 -I -B essais/mutations_v60.py` : **17 mutations, 17 tuées pour la raison attendue**, 0 survivante,
  témoin 43 essais avant et après, code 0. Premier passage : 1 survivante (« T2 tolère toute perte de la loi plantée ») —
  l'artefact « deux passes non concluantes sans élimination » manquait aux essais ; ajouté à l'essai, pas au code ; puis
  17 sur 17. Deux cibles de mutation d'abord mal nommées (méthode de classe) : corrigées dans le banc.
- Rejoués, inchangés : `essais/test_v59_boucle_fermee.py` : **28 réussis, 28 sous-essais** (13 s), vrai bac à sable joué
  (`bwrap` 0.9.0 présent ici).

## 3. Lectures préalables (déclarées en section 10 du texte)

| # | quoi | sortie (dossier de travail du rédacteur, hors de l'arbre) | sha256 |
|---|---|---|---|
| L1 | juge seul et statistique du test de mort en processus, 2 600 jugements, 56 s | script `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/explo/explo_tour_ferme.py` ; sortie `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/explo/L1.json` | `18fa2220…` ; `928b71c8…` |
| L2 | bras aléatoire et recopie-mélange, e-BH, 100 répétitions, 40 s | script `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/explo/explo_bras.py` ; sortie `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/explo/L2.json` | `8ab78123…` ; `74a0f77b…` |
| L3 | mode à blanc v59, 3 générations, 12 cartes de référence, vrai bac, 24 s, code 0 | `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/ablanc-g3-c12/journal-a-blanc-v59.json` | `474d005a…` |
| L4 | règle de réserve sur les identifiants de tâches de la banque publique | `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/reserve-banque-publique-L4/manifeste-reserve-v60.json` | `2c20acf7…` |

Chiffres clés : loi plantée G = 0,523 nat, promue et survivante 200 sur 200 ; S-F2 promue seule 83 sur 200 mais survivante
3 sur 200 ; lois aléatoires informatives (G ≥ 0,02) 13 % ; bras aléatoire : PS 0,125, FD 0,0025 par carte ; recopie-mélange :
0 promue sur 300 ; en v59 l'amorce plantée entre à l'archive et rend les générations 2 et 3 muettes (d'où la décision D3).

## 4. Devis (section 12 du texte)

≈ 240 appels et ≈ 6,6 USD attendus pour l'étage 1 (réel ≈ 106 appels, 2,9 USD ; aléatoire ≈ 89, 2,5 USD ; recopie-mélange
≈ 45, 1,2 USD), ≈ 60 appels et 1,5 à 2 USD pour l'étage 2 ; **total ≈ 300 appels, ≈ 8 à 9 USD**, environ 5 fois le second tour
du 1er novembre (62 appels, 1,47 USD, soit 0,0237 USD par appel). Sessions d'expérimentateur SUPPOSÉES à 0,04 USD, de
vérificateur à 0,02 USD. **Plafonds durs proposés : 12 USD (étage 1) et 5 USD (étage 2)** ; durée 0,7 à 2,7 heures (étage 1)
et 0,2 à 0,7 heure (étage 2), plafonds 4 et 2 heures. Option D6 (seconde réplique du bras aléatoire) : + ≈ 90 appels,
+ ≈ 2,5 USD.

## 5. La vraie question du 1er novembre et les données tenues à l'écart

- **Question** : le préenregistrement `6fcb1035…` du second tour réel est introuvable dans les arbres lus ; le dépôt privé
  (portée permise) ne cite la mini-course que par ses comptes (messages n° 323 et n° 334 de conv-audit). Candidats trouvés,
  sans preuve qu'ils soient le texte servi : le texte I de la course 2 (`…/question-mere-course-v1/recoupement-v1/question-course-2-defense-fusion-v5.md`,
  sha256 `a750144963913ba1c3dcf3eed5d4f8322d7d0246135e17c95ac8e7253c2dd680`, en-tête « brouillon, non servi ») et la question du
  collisionneur (`docs/notes/ideation-organisme-v1/course-2/question-course-2-v1.md`). Le texte laisse la case Q à la
  session-depot.
- **Données réelles neuves** : aucune n'existe pour ce tour. **Plus petite réserve honnête proposée** : par tâche entière,
  règle `sha256("tour-ferme-v1|tenue-a-l-ecart|" + tâche) % 3 == 0`, fixée avant la course et indépendante de toute graine et
  de toute issue ; T = les épisodes **privés à graines neuves** (288 du 2 novembre) des tâches réservées (≈ 96 épisodes,
  ≈ 32 tâches) ; épisodes publics des tâches réservées retirés de tout. Exécution chez la session-depot avec le module
  écrit ici ; empreintes et comptes recopiés dans le texte avant scellement. Limite dite : ces épisodes ont été lus une fois
  par le juge (lecture à graines neuves, pour d'autres lois), jamais par un proposeur ; mêmes tâches que la banque.

## 6. Ce qui manque pour lancer

1. Le code `_v60` restant (texte, section 13) : `pole/tour_ferme_v60.py` (témoins exclus de l'archive, gabarit imposé du test
   de mort, consigne et contexte du proposeur réel, recopie-mélange nourri par le bras réel, e-BH à m fixé, familles séparées,
   contre-calcul de la statistique hors bac, appel de l'oracle, relevé au format de `lecture_tour_ferme_v60`) ; juge à plan
   plein avec membres d'archive et monde M2 pour l'étage 2 ; lanceur `demonstrations/tour_ferme_v60.py` (à blanc par le faux
   SDK et réel par `ideation_v8.adaptateurs_reels_v56`, préenregistrement scellé et bloc gelé vérifiés, plafonds, porte) ;
   leurs essais et leur banc ; **répétition à blanc de bout en bout** (trois bras, trois générations, quatre rôles simulés,
   vrai bac, au moins 5 racines), qui couvre le point (iii) du développeur.
2. Contre-lecture R2 par un sous-agent neuf ; brouillon 2.
3. Décisions de Lazar D1 à D6 (texte, section 14), dont **D1 = point (i)** (les proposeurs ne voient que les lois retenues,
   sans verdict, richesse ni rang) et **D2 = définition de la fausse découverte** (point (ii)).
4. Chez la session-depot : texte et empreinte de la question du 1er novembre, configuration de son tour (modèles,
   adaptateurs), exécution de la réserve et cases de la section 5.2, monde M2, clés, **`bwrap` 0.9.0 et une identité dédiée
   sans privilège sur son instance**.
5. Scellement par le directeur, commit et poussée **avant** la course ; GO de Lazar sur le devis (ligne dans `registres/go.md`).

## 7. Fichiers à donner au contre-lecteur neuf (R2)

1. `orchestrator/prereg/preenregistrement-tour-ferme-v1-brouillon1.md` (le texte) et ce rapport ;
2. le code neuf : `orchestrator/pole/reserve_tenue_a_l_ecart_v60.py`, `orchestrator/demonstrations/reserve_tenue_a_l_ecart_v60.py`,
   `orchestrator/pole/oracle_tour_ferme_v60.py`, `orchestrator/pole/lecture_tour_ferme_v60.py`,
   `orchestrator/essais/test_v60_reserve_tenue_a_l_ecart.py`, `orchestrator/essais/test_v60_oracle_tour_ferme.py`,
   `orchestrator/essais/test_v60_lecture_tour_ferme.py`, `orchestrator/essais/mutations_v60.py` ;
3. la boucle fermée v59 et son rapport : `orchestrator/prereg/rapport-code-boucle-fermee-v1.md`, `orchestrator/pole/boucle_fermee_v59.py`,
   `orchestrator/pole/a_blanc_v59.py`, `orchestrator/pole/proposeurs_references_v59.py`, `orchestrator/pole/course2_v59.py`,
   `orchestrator/essais/test_v59_boucle_fermee.py` ;
4. le juge et l'étage : `orchestrator/pole/nul_v8.py`, `orchestrator/pole/selection_pari.py` (`proba`, `valider_loi`),
   `orchestrator/pole/cycle.py` (`appliquer_multiplicite`), `orchestrator/pole/juge_plan_plein_v1.py`,
   `orchestrator/pole/tests_de_mort_v5.py` (en-tête), `orchestrator/pole/etage_entre_generations_v57.py`,
   `orchestrator/pole/aiguilleur_v53.py` (en-tête, `classer`) ;
5. les mondes : `orchestrator/exemples/temoins-pari-demo-v1.json`, `orchestrator/exemples/banque-t05-v2.json` (structure seulement) ;
6. pour le style et les précédents : `orchestrator/prereg/preenregistrement-validation-nul-v8-v2.md`,
   `orchestrator/prereg/preenregistrement-lecture-t05-graines-neuves-v2.md`, `orchestrator/prereg/preenregistrement-attaque-goodhart-v1-brouillon1.md` ;
7. `README.md` (sections 2 à 4) ; `CLAUDE.md` du dépôt privé (règles R1 à R14).

Questions à lui poser : (1) la définition de la fausse découverte (oracle, g₀ = 0,02, ΔG contre la classe du nul v8) est-elle
la bonne, et la lecture A4 « écart nul + T5 tenu → les proposeurs ne battent pas le hasard » est-elle juste ; (2) la porte T1
à T5 est-elle trop lâche ou trop stricte (T2 tolère une passe perdue, T5 une FD) ; (3) la réserve (un tiers des tâches, T
privé, génération 1 seule décisive, T relue en génération 2) est-elle la plus petite réserve honnête, ou faut-il couper T en
deux ; (4) le bras recopie-mélange nourri par l'archive du bras réel (D4) peut-il rester « non mesurable » trop souvent ;
(5) le gardien modèle `aiguilleur_v53`, écrit pour des fiches d'idées, est-il un gardien acceptable pour des cartes-lois, ou
faut-il le réduire à la couche mécanique pour les trois bras ; (6) le devis (sessions d'expérimentateur SUPPOSÉES à 0,04 USD).
