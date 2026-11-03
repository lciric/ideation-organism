# Résultats de T0.3 — simulation du lemme d'additivité et du théorème négatif — v1

Date : 2026-10-04 (UTC). Tâche T0.3, phase 0. Critère 5 de la porte G0 : « agrégateurs validés en simulation ».

## Pièces (R6)

| Pièce | Chemin | sha256 |
|---|---|---|
| Préenregistrement scellé | `prereg/T0.3-simulation-lemme-theoreme-v1.md` | `7474743a0fa2a9db5da85bcedb0087ea57114fcca0fbb3415c7a97bf1b78d1fb` |
| Grille décisive | `prereg/T0.3-grille-v2.json` | `5609f920c0d606a192e92b2c2172416dad740b158940aac1ee049de8b8affe23` |
| Contre-lectures (3) | `prereg/contre-lectures/` | empreintes dans chaque fichier compagnon |
| Manifeste du run | `runs/20261004-080257-t03/manifeste.json` | `c9bba5e1f5f8dbf268e47023db8fac56c2cfd011721c6f89ba8ecad413e1a8ea` |
| Lecture gelée | `diag/20261004-080257-t03/lecture.json` | `c5aa62b42feed399e8626e3f681830023dc2dd124663d138e3a0c8170f1a7bbb` |
| Table de lecture | `diag/20261004-080257-t03/lecture.md` | `650ef86bef453104784fa7237187aa2d211be3169f25ffa9bba854d0b2f5722d` |
| Calibrage | `diag/20261004-080257-t03/calibrage.json` | `cb72b41d4dff5ee547037e700aeec963dbf5762a0727ccf6f615fbcad178f383` |
| Figures F1 à F6 | `diag/20261004-080257-t03/figures/` | empreintes dans chaque fichier compagnon |

Conditions du run :
- run unique, décisif, complet ;
- code au commit cité d73ac46, vérifié identique au lancement ;
- graines dérivées de l'entropie scellée de la grille (3 280 tâches) ;
- versions : Python 3.11.15, numpy 2.4.6, scipy 1.17.1 ;
- durée : 706 s.

Toutes les gardes de la liste d'arrêt sont passées : calibrage sous P₀ sur 12 configurations, équivalence des statistiques, préservation du multi-ensemble.

## Prononcé de la lecture gelée

**Les 31 prédictions sont confirmées** :
- 342 cellules statistiques et 544 cellules trajectorielles ;
- 0 cellule contraire, donc ni réplication ni audit de réplication ;
- 0 violation trajectorielle.

**Audit de symétrie (R4) : non déclenché.** La variance des écarts réduits vaut :
- 0,955 sur les 63 comparaisons aux formes closes ;
- 0,853 sur les 104 égalités ;
- bornes gelées : [0,3 ; 3].

Les écarts à la théorie se comportent donc comme un bruit Monte-Carlo ordinaire, ni trop propre ni trop bruité.

**Réserve (R4, « trop beau = réserve »).** Que tout soit confirmé était attendu : la plupart des prédictions sont des **vérifications de l'instrument**, qui ne pouvaient échouer que par une erreur de code ou d'énoncé (préenregistrement, « Nature »). Cette confirmation établit trois choses :
- les agrégateurs et les calibrages sont corrects ;
- l'arithmétique des preuves de la note v2 est juste ;
- les magnitudes des prédictions informatives sont celles annoncées.

**Elle ne prouve ni le lemme ni le théorème sur des activations réelles** : c'est l'objet des phases suivantes.

## Magnitudes informatives

Tous les taux sont à α = 0,05 et R = 20 000, sauf mention contraire. Valeurs tirées des fichiers `bloc-*.json` du run.

1. **La lecture séquentielle dépend du calendrier (P3.2).** Exemple : n₀ = 200, B = 25, m = 10, processus e unilatéral de Ville.

   | Calendrier du sabotage | Alarme d'ici n₀ |
   |---|---|
   | début | 1,000 |
   | aléatoire | 0,312 |
   | uniforme | 0,278 |
   | fin | 0,160 |
   | borne terminale | 0,158 (théorie 0,159) |

   Un sabotage reporté ramène la lecture toujours valide à sa borne terminale. La « puissance qui ne dépend que de B » ne vaut que pour la statistique terminale.
2. **Pour alarmer avant que le dommage ne soit fait, il faut des détecteurs de rupture (P3.4).** Sabotage en bloc à la fin de l'horizon (m = 5 à 20 actions), alarme avant la dernière action sabotée, au même taux de fausses alarmes :

   | Statistique | Taux |
   |---|---|
   | Processus e cumulé, calibré | 0,09 à 0,25 |
   | Processus e cumulé, au seuil de Ville | 0,04 à 0,15 |
   | Page | 0,57 à 1,00 |
   | Détecteur e | 0,52 à 1,00 |

   Conséquence pour H2 et la porte G1 : l'agrégateur séquentiel du programme doit comprendre un détecteur de rupture, et pas seulement la somme cumulée toujours valide, si la sécurité se définit comme « alarme avant que le dommage atteigne θ ».
3. **Le max s'effondre, la somme non (P1, P2).** À n₀ = 200 et B = 20 :
   - la somme terminale vaut 0,41, quelle que soit la répartition ;
   - le max passe de 1,00 (m ≤ 5) à 0,165 (m = 20), puis 0,071 (m = 200), plancher prédit 0,0714.

   À B fixé, la puissance de la somme décroît avec n₀. Pour B = 20 : 0,88 (n₀ = 50) → 0,16 (n₀ = 1000).
4. **Classe K : le théorème du programme est faux tel qu'écrit (P6).**
   - Copule AR(1) gaussienne, φ = +0,5 : somme 0,167 (théorie 0,170), e unilatéral 0,195, max 0,048, autocorrélation 1,000.
   - φ = −0,5 : somme 0,0024, e 0,000, |autocorrélation| 1,000.
   - **Construction de 2606.10456** (φ₀ = 0,5, T = 300) :

     | φ₁ | Somme | Max | Autocorrélation | Page |
     |---|---|---|---|---|
     | 0,59 | 0,072 | 0,048 | 0,59 | 0,13 |
     | 0,725 | 0,126 | 0,044 | 0,998 | 0,36 |
     | 0,9 | 0,253 | 0,027 | 1,000 | 0,72 |

     La « puissance = taux de faux positifs » de sa proposition 1 est fausse pour la somme. Elle est vraie, et même pessimiste, pour le max.
   - Équicorrélation entre agents c = 0,4 : somme 0,157, co-élévation 0,72, corrélation entre agents 1,00, max 0,049.
5. **Classe C : aveuglement exact, et un attaquant adaptatif neutralise les statistiques globales (P4, P5).**
   - Sous réarrangement, les statistiques symétriques sont identiques au bit près (T1). Sous rebrassage uniforme, toute statistique est à son taux sous P₀ (T2, 68 cellules).
   - Suite des 5 plus hautes valeurs : l'autocorrélation détecte à 0,46. Après appariement adaptatif, elle tombe à 0,0515 (P₀ : 0,0507), alors que la moyenne glissante (w = 5) reste à 1,000 et Page à 0,997 (T3).
   - Le groupe compte : rebrassage total 0,967 (forme close exacte 0,967), rebrassage intra-agent 0,0505.
6. **La règle de Ville n'est pas valide hors hypothèses ; le calibrage sur épisodes entiers l'est (P8).**

   | Situation | Taux de fausses alarmes de la règle de Ville |
   |---|---|
   | Bien spécifiée | 0,017 à 0,019 |
   | Effet épisode τ = 0,2, n₀ = 200 | 0,21 |
   | Effet épisode τ = 0,2, n₀ = 1000 | 0,35 |
   | Effet épisode τ = 0,1, n₀ = 1000 | 0,24 |
   | Équicorrélation entre agents c = 0,4 | 0,17 |
   | σ sous-estimé de 20 % | 0,066 |
   | AR(1) φ = 0,2 | 0,057 |

   Le calibrage conforme sur 1 000 épisodes honnêtes entiers donne 0,046 à 0,055 dans les 17 réglages (prédit : 0,04995).

## Lecture des énoncés du programme (table E, prononcée par le code)

1. **Lemme.**
   - Exact pour la statistique terminale à n₀ fixé, « variance » au sens de la statistique (n₀σ²), pour toute répartition.
   - Faux à variance par action fixée quand n₀ = NT varie.
   - Faux pour la lecture séquentielle quant au calendrier.
   - L4 (répartition entre agents au même pas) n'est pas testé.
2. **Max** : il s'effondre, avec un plancher strictement au-dessus de α.
3. **Théorème négatif.**
   - Vrai en classe C : statistiques symétriques, et toute statistique sous rebrassage uniforme ; le groupe compte.
   - Faux en classe K : la somme et le processus e sont au-dessus de leur taux sous P₀ sous dépendance positive, en dessous sous dépendance négative ; sous dépendance positive, le max est à son taux ou en dessous.
4. **« Il faut l'autocorrélation ou la co-élévation »** : vrai en classe K. Face à un attaquant adaptatif de classe C, seules les statistiques locales gardent une garantie.
5. **« La somme cumulée échoue »** : exact en classe C et au sens adverse (T4) ; inexact en classe K, où la somme n'est pas aveugle mais reste faible.
6. **Garde de G1 : décisive.**

## Conséquences — à soumettre, sans rien trancher

- **N-003 et N-004** : la simulation confirme les énoncés corrigés de la note v2 et réfute les formulations littérales du programme dans les cas annoncés. La recommandation (a) des deux nœuds en sort renforcée. La décision reste à Lazar.
- **Porte G1 et H2** : la garde « faux positifs vérifiés sur épisodes honnêtes » doit être opérée par un calibrage sur épisodes honnêtes entiers (conforme), et non par le seuil de Ville. L'agrégateur séquentiel doit inclure un détecteur de rupture. Ces deux points iront dans le préenregistrement de G1, en proposition.
- **Papier A** : figures F1 à F6 disponibles. La distinction entre puissance au sens de Wald et garantie toujours valide (2208.07610) et la borne de l'adversaire couvert (2601.20022), demandées par le brief pour la note, restent à écrire après lecture de ces PDF (R7) : note mathématique v3.

## Reste de T0.3

- Note mathématique v3 : intégrer ces résultats, puis les deux références ci-dessus après lecture sur PDF.
- Correction reportée pendant le gel du code (O-2) : un préenregistrement placé hors du dépôt doit arrêter par `GardeArret`.
