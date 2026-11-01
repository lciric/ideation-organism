# Orchestrateur v7 — conception avant code — v1 (monde du programme sur banque en cache, nul informé, sans urne, proposeur, moissonneur)

Lignée conv-audit (instance du 27 octobre 2026, servie par Fable 5.1), écrit à partir de 13:50 UTC (heure lue sur
`date -u` : 13:50:12). Suite directe de la contre-lecture d'aptitude (`../premier-lancement-reel/contre-lecture-aptitude-v1/`,
`d4c6ef64…`) et du programme de conception (`../programme-conception-organisme-v1.md`, `72fa0e60…`, § 3.1). Exploratoire ;
aucune dépense ; v6 n'est pas modifié (R12).

## Verdict

1. **La banque de la couche 1 existe sur `main`** : le pilote de T0.5 (`diag/20261012-105125-t05-pilote-reel/episodes.json`,
   180 épisodes du modèle de 8 milliards, 10 propositions chacun, jetons par action, empreintes d'activations) et les
   notations décisives des deux juges (`diag/20261017-193648-t05-notations-reel/notations-{8B,3B}-decisives.json`, 180
   notations chacun : sept notes de grille entières — BALANCE, COHERENCE, NOVELTY, RIGOR, RESULT_REASONING, deux
   pénalités — et un score complet pour 54 (8B) et 50 (3B) d'entre elles ; les autres ont des notes non entières dans
   d'autres rubriques, consignées comme anomalies). Rien n'est à relancer : une banque figée.
2. **Pièce 1 de v7 : `MondeBanque`** — un monde dont les instances sont les lignes d'une banque (traits visibles, issues
   cachées), qui tire le plan dans la banque après le gel et dépose les issues lues (jamais calculées). Même interface
   que `MondeNoyau` (`mesures(enonce, gele, graine_noyau, numero_generation)`), donc rien ne change dans le cycle.
3. **Pièce 2 : nul informé** — un membre de bibliothèque « prédicteur connu », loi par instance ajustée **avant le gel**
   sur une partie de calibrage de la banque disjointe du plan, déclarée dans l'engagement (sous son empreinte) ; le juge
   promeut alors ce qui bat le connu, pas ce qui bat l'aveugle.
4. **Pièce 3 : configuration sans urne** (`urne=False`) : sur une banque figée il n'y a pas de dérive dans le temps ; le
   membre « urne » coûte de la puissance (≈ 5,5 nats à 200 tirages, expérience 1) pour rien ; l'ordre secret reste
   (il ne coûte rien et garde la garde du plan d'exécution).
5. **Pièces 4 et 5 : proposeur et moissonneur** (sections 4 et 5) ; **pièce 6 : fermeture des canaux de texte et
   aptitude = preuve** (section 6). Ordre : 1, 2, 3 d'abord (ils bloquent la couche 1), puis 6, puis 4 et 5.

## 1. Le monde sur banque (`pole/monde_banque.py`)

- **Banque** : fichier JSON scellé, tenu hors des dossiers d'agents : `{"traits": [noms], "instances": [{"identifiant",
  "z": [valeurs des traits, centrées-réduites par la banque], "g": sous-population, "issues": {moniteur: entier}}]}`.
  Pour T0.5 : identifiant = `tâche/épisode/passe` ; traits = longueur totale en jetons, nombre d'actions valides, longueur
  moyenne d'une action, rang de la passe, et un trait de tâche (numéro de la tâche, codé) ; sous-population = juge (8B ou
  3B) ; issues = une note de grille discrétisée en trois classes (par exemple NOVELTY ∈ {1, 2, 3} → {0, 1, 2}), une
  issue par rubrique disponible. Un script `exemples/construire_banque_t05_v1.py` la construit à partir des fichiers de
  `main` cités, avec leurs empreintes dans son manifeste.
- **Fiche sur banque** : `espace_instances = {"banque": nom, "moniteur": rubrique, "nombre_issues": K, "dimension": d}` ;
  la loi prédictive est une loi des types existants sur `z` (rien ne change pour le juge).
- **Plan** : `selection_divergence` sur la **partie d'épreuve** de la banque (jamais sur la partie de calibrage) ; la partie
  d'épreuve d'une fiche est tirée après le gel, par la graine du noyau, sans remise ; une instance déjà servie à une
  fiche promue n'est pas resservie à une fiche de même classe (mémoire) — règle à écrire dans le préenregistrement de la
  couche 1, pas ici.
- **Issues** : lues dans la banque pour le moniteur de la fiche ; `mesures.json` déposé comme en v6 ; dépôt unique par
  engagement conservé.
- **Témoins de domaine** : fiches dont la vérité est connue par construction sur la banque — vraies : « la note NOVELTY
  croît avec la longueur de l'ensemble » si c'est établi sur la partie de calibrage avec une marge (à vérifier, pas à
  présumer) ; fausses : lois qui dépendent d'un trait **permuté** par le noyau (artefact planté) ; les deux sortes
  déclarées dans `temoins`, vérité sous empreinte.

## 2. Le nul informé

- Membre `{"type": "connu", "loi": <loi ajustée>, "ajuste_sur": empreinte de la partie de calibrage, "moniteur": r}` ;
  ajusté par le noyau avant le gel (régression multinomiale sur `z`, bibliothèque standard, Newton comme dans le nul des
  filles v2) ; sa trajectoire est celle d'une loi fixée (type `loi`), déjà prise en charge par `trajectoire_membre`.
- Deux variantes à lire côte à côte : `𝓛_V1 + connu` (sévère) et `𝓛_V1` seul (le juge d'aujourd'hui) : la différence
  mesure « ce que le pôle promeut qui n'est que du connu ».
- Témoin : une fiche qui redit exactement le prédicteur connu doit être **éliminée** sous `+ connu` et **promue** sans.

## 3. Sans urne

`ConfigGeneration.urne: bool = True` ; `preparer_engagement` prend `BIBLIOTHEQUE_STANDARD_V1` sans le membre « urne » si
`urne=False` ; `valider` : `urne=False` seulement avec `juge="v1"` (le plan d'exécution secret reste) ; les essais du
nul des filles v2 passent tels quels (ils n'utilisent pas l'urne). Lecture attendue : puissance rendue sur petit effet
(T3 ε = 0,05 : de 0,196 vers ~0,9, à vérifier), aucune garantie perdue sur une banque figée (pas de dérive).

## 4. Le proposeur (rôle `proposeur`)

- Entrées : le texte du programme (ou de la question de la couche), la description de la banque (traits, moniteurs,
  tailles ; jamais les issues), la mémoire du pôle (classes, survivantes, redites refusées), la moisson (section 5).
- Sortie : des fiches au format du pôle (loi prédictive comprise), par un **gabarit** : le proposeur choisit un type de
  loi et des paramètres dans des bornes ; le noyau valide (`valider_loi`) et refuse ce qui est hors gabarit.
- **Catalogue de stratégies** (liberté bornée, v7) : « monotone en un trait », « interaction de deux traits », « différence
  entre sous-populations », « redite corrigée d'une éliminée », « transposition d'une survivante à un autre moniteur » ;
  le proposeur déclare la stratégie employée (mesure : quelles stratégies produisent des promues).
- Enfichable : l'interface est `proposer(contexte) -> [fiches]` ; un proposeur de la littérature se branche ici, dans un
  conteneur sans clés, après le tour du collisionneur.

## 5. Le moissonneur

- Routes du relais (`/moisson/arxiv`, `/moisson/openalex`, `/moisson/semantic-scholar`, `/moisson/brave`) ; clés de
  moisson lues par le relais dans son seul environnement ; quotas par rôle et par course ; journal sans clé ; **garde de
  fuite** (CE3-04) : refus de toute requête qui porte un texte de test ou un identifiant d'épisode.
- Provenance : tout document rapporté est empreinté (SHA-256 du PDF ou de la page), cité par chemin et empreinte dans la
  fiche ; un chiffre sans empreinte est « non opposable » (R7) et le noyau l'étiquette ainsi.
- Les agents n'ont toujours ni réseau ni clé : ils parlent au relais local avec le jeton factice, par des commandes
  permises par la garde des outils (une commande `moisson …` fournie par le noyau).

## 6. Canaux de texte, lignée, aptitude

- Rejeu : le vérificateur ne reçoit que la fiche, l'engagement, les mesures déposées, le code déclaré et les fichiers
  que ce code lit (liste déclarée) — plus rien d'autre du dossier de l'expérimentateur.
- Leçons : champs structurés (`causes`, `protocoles`, `redites`) à partir de l'index, jamais de prose libre servie.
- Lignée : le modèle du vérificateur doit être d'une **autre lignée déclarée** que l'expérimentateur (table des lignées
  : Opus 5.5 et Fable 5.1 sont deux modèles de la même famille ; N-052 l'admet pour la contre-lecture ; pour le
  vérificateur, c'est la contrainte de Lazar qui fixe les deux modèles).
- Aptitude : `log_richesse_max` de la dernière promotion, utilisée par le tirage à marchepieds et par l'index.

## 7. Essais prévus (R5)

Cas sains et artefacts pour chaque pièce : banque permutée (vraie fiche éliminée), prédicteur connu redit (éliminé sous
`+ connu`), fiche qui réclame une instance de calibrage (refusée), issue absente pour le moniteur demandé (refus, jamais
de repli silencieux), proposeur hors gabarit (refusé), moisson avec texte de test (refusée), rejeu avec fichier non déclaré
(absent du dossier du vérificateur), aptitude = preuve (ordre des marchepieds change).
