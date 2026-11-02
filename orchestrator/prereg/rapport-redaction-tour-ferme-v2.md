# Rapport de rédaction — tour fermé (A2, A3, A4), brouillon 2

2 novembre 2026, de 09:30 à 11:10 UTC environ. Rédacteur-développeur neuf (ni le brouillon 1, ni son code, ni la contre-lecture).
Aucun appel de modèle, aucune clé, aucun réseau, aucun commit, aucun `git fetch`, aucun scellement, aucun `.sha256` ; `nice -n 10` ;
fichiers neufs seulement (R12). Dépôt à la tête `c47b608`. Le fichier `pole/lecture_tour_ferme_v61.py` laissé par la première
instance (jamais committé) a été lu, jugé complet et conforme à C1 et C2, **gardé tel quel** (une constante relue : P4 à 6 sur 36).

## 1. Verdict

Brouillon 2 écrit, couples T1 à T18 appliqués, code C1 à C5 et C7 écrit et essayé, répétition à blanc de bout en bout dans le vrai
bac. **Non scellable encore** : (a) la seconde contre-lecture R2 (texte et code) n'est pas faite ; (b) le cœur de l'étage 2 n'est
pas écrit (dit dans le texte, section 13) ; (c) 16 marqueurs restent (décisions D2 à D9 et cases privées) ; (d) C7 non relevé
(journaux privés) : plafond 15 USD.

## 2. Couples et constats, un par ligne

- T1 phrase cassée : appliqué. T2 D1 prise (GO-2026-11-02-06) : appliqué. T3, T3b, T3c, T3d (T2, T3, T4, T1 de la porte) : appliqués ;
  T3c dit de plus qu'un désaccord du contre-calcul **arrête** la course (choix de code, garde 10).
- T4, T5 (lecture A4 : cause lue à l'oracle, phrase de Lazar gardée mot pour mot, génération 1 à côté) : appliqués.
- T6 (témoins hors famille) : appliqué, et codé (`juger`, seuil m/α). T7 (P4 par génération, L2b) : appliqué, **adapté** : borne haute
  de trois générations à 6 cartes sur 36 (le `_v61` laissé par la première instance la portait ; marge d'une carte sur L2b) ; L2b-v61
  cité. T8 (P6 par génération) : appliqué.
- T9 (D8 prédicteur connu) : appliqué dans le texte avec marqueur ; **le code de l'étage 2 n'est pas écrit** (le paramètre `d8` est lu et
  vérifié par le lanceur).
- T10, T11 (garde 11 durcie, dépendance des épisodes) : appliqués ; code C4. T12 : forme D9 (gardien mécanique seul) plus la portée du
  bras recopie. T13 à T17 (phrases au mentor, N1/N2) : appliqués. T18 et ajout en tête de la section 6 : appliqués.
- B1 : cœur et lanceur écrits (étage 1), gardes 5 à 10, 12, 13 essayées (cas sain et artefact), banc de 15 mutations, répétition à blanc.
- B2 : case Q au défaut (question du collisionneur de la course 2) ; E0, R, T, M2 : marqueurs `<<CASE_X>>` (données privées) ; V : empreintes
  des modules v60 et v61 écrites, manifeste en marqueur.
- B3 à B6 : code v61 (lecture) et texte. I1 (P4, P6) : T7, T8. I2 (D8) : texte, paramètre. I3 (fuites) : `reserve_tenue_a_l_ecart_v61`. I4 :
  T10, T11. I5 : lecture v61 (T1, T3, T4). I6 (D9) : gardien mécanique, aiguilleur refusé par le lanceur. I7 (devis) : plafond 15 USD,
  tableau refait sans gardien modèle. I8 : portée (T12). I9 : section 6 symétrisée.
- Mineurs 1 à 9 : appliqués (manifeste : commit, Python, numpy, bwrap, ordre des bras, décisions ; graine publique dite par construction du
  texte ; P8 ouverte ; calibrage réajusté dit en T9 ; doublons : champ `vd_distinctes` du relevé, **calcul non écrit** au cœur, dit).

## 3. Code (fichiers neufs, sha256)

| fichier | sha256 |
|---|---|
| `pole/tour_ferme_v61.py` | `d7817ce03877e0817d1f7b381981a16455ece514b383cbe78013bfc91c4a3a7f` |
| `demonstrations/tour_ferme_v61.py` | `f420274ca81c5b762de8247aff48645f660e27fef8d5df01344305930a561a60` |
| `pole/lecture_tour_ferme_v61.py` | `0e9d19630d02ab140c7190aa94a212974021b179602eb00984fb52e50e81dfee` |
| `pole/reserve_tenue_a_l_ecart_v61.py` | `b99fe5a58d6348e80e9ff0b3184a69b4602951d8c8e439a59c240e3ef5883ff9` |
| `essais/test_v61_tour_ferme.py` | `936bec92d1aa87765c803192b74043a6423e8c9645eaf3b886167ba683e8873c` |
| `essais/test_v61_lecture_tour_ferme.py` | `d8d71f3fea635ebfaaca905fc729f209901eba3535ac1aeb46e68f15ab48bd59` |
| `essais/test_v61_reserve_tenue_a_l_ecart.py` | `c62a4dd260e8edda75960df97b914c08bb65e7a8698ad53f3453a7197e251568` |
| `essais/mutations_v61.py` | `3feadc7fa2fc86d596819f119cedc147333838cfa4321381f7576924b9cf6477` |
| `prereg/preenregistrement-tour-ferme-v1-brouillon2.md` | `37ae595f95bb0e0d4777b3ae469aad5f7b270eb8a8b9c30d86da78f3d38b999f` |

Choix de code à contre-lire : (1) les témoins sont testés dans **leur propre étage** v5 (`etage-temoins`, même tranche), ce qui les tient
hors de la sélection v57 et de l'archive sans toucher la boucle v59 ; (2) un désaccord du contre-calcul (> 10⁻⁶) **arrête** la course
(`ArretTour`) avant que la carte n'entre à l'archive ; une valeur absente du noyau (« non concluant ») donne `contre_calcul_ok = True`
avec `sans_objet` ; (3) D7 : le bras aléatoire a toujours un bilan v59 (lu, vérifié) mais son archive n'est jamais lue au jugement ;
(4) le mode réel importe `reglages_de_configuration`, `substituer_commandes` et `charger_ideation_v8` du lanceur de l'attaque de Goodhart
v2 (même mécanisme ; `demonstrations/attaque_goodhart_v2.py` entre donc dans le code gelé) ; (5) en mode réel, `moteur="simule"` est
passé à l'étage v5 (c'est le mot de l'étage pour « pas le kit Claude » ; les coûts viennent des adaptateurs externes) — à contre-lire ;
(6) le chemin réel (adaptateurs, portes, GO) n'a **pas** été exécuté ici (aucune configuration v3, aucun registre) : seules ses gardes
statiques sont essayées ; (7) `T.jouer_etage` est remplacé dans le processus du mode à blanc pour nourrir l'expérimentateur scripté.

## 4. Essais et mutants

- `essais/test_v61_tour_ferme.py` : 16 essais (décisions ; gardes 5, 13, 6 (plan, chemin, scellement), 7, 8, 9, 10, 12 ; fermeture du code
  gelé ; lanceur : refus avant tout appel, course courte factice puis lecture, artefact garde 8 (proposeur hors gabarit), artefact garde 5
  (plafond → code 3, sortie scellée) ; vrai bac `bwrap`, identité 64097).
- `essais/test_v61_lecture_tour_ferme.py` : 14 essais (B3, B4, B5, I5, N1/N2, réserve (a) avec cause).
- `essais/test_v61_reserve_tenue_a_l_ecart.py` : 6 essais (orthographe, normalisation, identifiants et traits, disjonction).
- Tous rejoués ensemble avec v59 et v60 : **110 réussis** (63 s). Bancs : v59 9/9, v60 17/17, **v61 15/15** tuées pour la raison attendue
  (témoin 28 essais avant et après).
- Non essayé (dit) : gardes 11 (appel au montage, seulement par la fonction v60 déjà essayée) et 12 sur une vraie course de l'étage 2 ;
  `DebordementKimi` (D9 retire l'aiguilleur) ; garde 13 durée sur une course (essayée sur le compteur à horloge factice).

## 5. Répétition à blanc (L2b-v61)

`nice -n 10 python3 -I -B demonstrations/tour_ferme_v61.py SORTIE --etage 1 --a-blanc --graine 20261102 --bac reel --utilisateur-bac 64097` :
code 0, **91 s**, 15 appels scriptés, 0 USD ; relevé `tour-ferme-v1-etage1.json` sha256
`d1bc9283deebf79a8d4363e5d6eca82ddc8abbcadba27f9e1761bcdb18f3a1a3`, manifeste `21d4d8b7…` (bloc-notes
`/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/tf61/blanc1/`). Lecture v61 : « tient » (T1 à T5), A4
« discrimine », Newcombe [0,147 ; 0,469], 8 passes attendues, 6 lectures ; réel 36 jugées, PS 11, VD 11, FD 0 ; aléatoire 36, PS 0 ;
recopie 24, PS 0 ; 0 non concluant ; 30 contre-calculs concordants ; 9 étages dans `bwrap`, `factice = False`. Une seule répétition
(budget) : le texte le dit ; les 5 racines demandées au brouillon 1 (section 13, point 6) **ne sont pas faites**.

## 6. Devis

Étage 1 sans gardien modèle : ≈ 102 appels ; 3,3 USD à 2 tours d'expérimentateur par carte, 8,4 à 4, 12,2 à 6 ; plafond **15 USD**
(C7 : relevé impossible ici, journaux privés). Étage 2 : ≈ 60 appels, 1,5 à 2 USD, plafond 5 USD. Total 5 à 14 USD.

## 7. Fichiers pour la contre-lecture neuve (texte **et** code)

`prereg/preenregistrement-tour-ferme-v1-brouillon2.md`, ce rapport, `prereg/contre-lecture-preenregistrement-tour-ferme-v1.md`,
les huit fichiers de code de la section 3, `pole/a_blanc_v59.py`, `pole/boucle_fermee_v59.py`, `pole/proposeurs_references_v59.py`,
`pole/oracle_tour_ferme_v60.py`, `pole/reserve_tenue_a_l_ecart_v60.py`, `pole/cycle.py` (`appliquer_multiplicite`),
`pole/tests_de_mort_v5.py` (`executer_tests_de_mort`, `verdict_du_noyau_v5`), `demonstrations/attaque_goodhart_v2.py` (fonctions
importées), le relevé et le manifeste de la répétition à blanc (bloc-notes), le script `construire_brouillon2.py` du bloc-notes
(sha256 `be658260b7d95aa90054f04141caceac4e5024eb1d185eb6d3356c38c1bfdf14` : le brouillon 2 est le brouillon 1 plus ces remplacements).

## 8. Ce qui manque pour lancer

1. Décisions D2 à D9 de Lazar (marqueurs `<<DECISION_D2>>` … `<<DECISION_D9>>`).
2. Session-depot : cases E0, R, T, M2, V (`<<CASE_E0>>`, `<<CASE_R>>`, `<<CASE_T>>`, `<<CASE_M2>>`, `<<CASE_V>>`), sha256 de Q
   (`<<CASE_Q>>`), configuration v3 à plafond 15 USD (`<<CASE_CONFIGURATION_V3>>`), GO (`<<CASE_GO>>`), relevé C7.
3. Cœur de l'étage 2 (`_v62` : juge à plan plein étendu à l'archive, M2, test de mort D8) et ses essais — ou un texte scellé pour l'étage 1
   seul, avec l'étage 2 en version nouvelle.
4. Calcul de `vd_distinctes` au cœur (mineur 10) ; répétitions à blanc sur 5 racines.
5. Seconde contre-lecture R2 (texte et code), scellement par le directeur, commit et poussée **avant** la course.
