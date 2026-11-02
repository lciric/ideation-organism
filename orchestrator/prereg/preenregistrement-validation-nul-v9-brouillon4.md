# Préenregistrement — validation décisive du nul v9 du juge (banc des tricheurs v9), brouillon 4

**Statut : brouillon 4 — contre-lu (R2 n° 1, `prereg/contre-lecture-preenregistrement-validation-nul-v9-v1.md`, sur le brouillon 2),
couples appliqués (38 : 23 tels quels, 15 refaits sur le brouillon 3), bloquant B1 et importants I5, I6 levés par des essais,
I2 levé par la description publique du nul (section 0 ter) ; non scellé ; aucun marqueur ni jeton.** Brouillon 2 rédigé le
2 novembre 2026, de 18:51 à 18:55 UTC (`date -u`) ; brouillon 3 (section 0 bis) de 19:14 à 19:20 UTC ; brouillon 4 (section 0 ter)
de 19:46 à 20:10 UTC ; tous trois par un
sous-agent repreneur neuf qui n'a écrit ni le nul v8, ni le nul v9, ni le brouillon 1, ni l'attaque contre le juge, ni leurs
préenregistrements (il reprend le travail d'un concepteur coupé par une panne de crédits, qui n'avait rien écrit au-delà du
commit). Aucun appel de modèle, aucun réseau, **aucune dépense** (tout est hors ligne, sur processeur) ; aucun commit, aucun
`.sha256` dans le dépôt, rien sous `donnees/` ; aucun fichier existant modifié jusqu'au brouillon 3 ; au brouillon 4, à la
demande du directeur, trois fichiers existants modifiés et seulement eux : `pole/nul_v9.py` (description, aucun calcul),
`essais/test_nul_v9.py` et `essais/mutations_nul_v9.py` (les brouillons 1 à 3 restent intacts). Le banc refuse ce
brouillon en mode décisif (nom hors de `prereg/preenregistrement-validation-nul-v9-v<N>.md`, non scellé) : c'est voulu.

**La correction du code que le brouillon 2 disait indispensable est faite** (par le directeur, commit `e58cfec`, section 0 bis) :
le banc gèle 48 heures en mode décisif (`demonstrations/banc_tricheurs_v9.py`, ligne 84, `DUREE_MAX_S = 48 * 3600.0`, comparée
ligne 524 ; docstring et usage, lignes 40 et 47) ; un essai (`test_duree_du_mode_decisif_48_h`) et une mutation (« durée du mode
décisif non gardée ») l'accompagnent. Le cas sain que demandait l'annexe B (durée par défaut → la course démarre, durée transmise
172 800 s) manquait (B1 de la contre-lecture) : il est ajouté au brouillon 4 (`test_mode_decisif_cas_sain_et_refus`). Le bloc de
la section 12 porte les 14 empreintes du code final, dont celle de `pole/nul_v9.py` modifié pour sa description seulement
(section 0 ter, point 5).

**Code et textes du nul v9** (commit de conception `5e352ec57ec2f7a1bf96b71fe4bd18cac4a43cfb` de `ideation-organism`, branche
`main`, 2 novembre 2026, 18:35:13 UTC ; empreintes recalculées par `sha256sum` sur disque et sur `git show 5e352ec:…`, égales, à
18:50 UTC). **Trois de ces fichiers ont changé au commit `e58cfec936461a72a173c667e91755582e04bcb8`** (19:05:02 UTC, correction de
la durée, section 0 bis) ; valeurs au commit `e58cfec` dans la dernière colonne (arbre de travail égal au commit pour ces
fichiers, vérifié par `git diff --quiet e58cfec` à 19:05 UTC). **Au brouillon 4, trois fichiers changent encore** (arbre de travail,
non commité ; le directeur recommite avant le scellement) : `pole/nul_v9.py` (description seulement, aucun calcul), les essais
et le banc de mutations (section 0 ter) ; dernière colonne :

| fichier | rôle | sha256 au commit `5e352ec` | sha256 au commit `e58cfec` | sha256 au brouillon 4 (arbre) |
|---|---|---|---|---|
| `pole/nul_v9.py` | le nul (au brouillon 4 : description publique, aucun calcul changé) | `8cb44adf8b325ac656b077f03dddb44311071510a5785ebd3f0aa8c37aebc655` | inchangé | `7ae450df2482246122bf9fbcf0fa5ef30b4a7e4c6f0d09531e83af048e46ee95` |
| `demonstrations/banc_tricheurs_v9.py` | le banc (durée corrigée) ; à `5e352ec`, non gelé | `c7ab547065180b6e23e0e496d9c9dc96b674ed4c1b47766b3e108709fdbcf466` | `7e4bff5995df2a7d62a4f5a2f5f9176da614e657a55b05183325fa2fc6e24e44` | inchangé |
| `essais/test_nul_v9.py` | essais (non gelé) ; au brouillon 4 : B1, I5, I6, I2 | `f674e9cac121d8930942738e28f938bd3613018c0c4371bd4621e53020212855` | `9eb966ad4220fc6cd297eef53ebec36a0f77655c2eadaceedc52ad72a1a67b21` | `d42a50eb4ba9691e75e82fa4bc714a925615da80df22227fee730392015999b9` |
| `essais/mutations_nul_v9.py` | banc de mutations (non gelé) ; au brouillon 4 : G1 à G5, L1, L2, C5, description | `576eea7917cc9c0ed5213eeb22f191add217cc91b54fc4368a087911f153507d` | `9cb305e45b8c005564184df621e68c05f1ac36b92e520ee081dbed735a252d16` | `f004dba63ffe25c66b9b41edefbd8307e188feccd8a8e15aa9754e472dca3f52` |
| `prereg/rapport-redaction-nul-v9.md` | conception, preuve, non-couvert, esquisse de la suite | `bbf9b38f3b2fca44ac33bf36c7e67f39c6525dfd6561c9f84a00cda758233089` | inchangé | inchangé |
| `prereg/preenregistrement-validation-nul-v9-brouillon1.md` | brouillon 1 de ce texte | `253eece5598f582b09b0fd468fde55b0b7bda98454d25505971b65cbe6afccf0` | inchangé | inchangé |
| `prereg/preenregistrement-validation-nul-v9-brouillon2.md` | brouillon 2 de ce texte (au commit `e58cfec`) | — | `0a906f8c43099670f1c6694d7ec67b847ff9bc28687d0906e8419e3e23d8bcb7` | inchangé |
| `prereg/preenregistrement-validation-nul-v9-brouillon3.md` | brouillon 3 de ce texte (commit `9e6ca23`) | — | — | `347523dd429745be47803a4676ac451371592c790def39a68da109676a460cb2` |
| `prereg/contre-lecture-preenregistrement-validation-nul-v9-v1.md` | contre-lecture R2 n° 1 (non commitée à la rédaction) | — | — | `41f4f56d85456520394835f96d7c6a5d06b51138dc985fd0d40fdb67cac9b9d5` |
| `prereg/couples-contre-lecture-validation-nul-v9-v1.json` | ses 38 couples | — | — | `78c9b1e5c1f2337c6a5ee09cd7d24c35b050242ea61b4c83b4a31d2479e71f20` |

Les quatre empreintes de code et celle du brouillon 1 sont celles du bloc de livraison du rapport de rédaction (section 9) ;
le rapport lui-même ne portait pas la sienne (elle est ci-dessus). Essais et mutations sur ce code : passage final du concepteur
(18:23 à 18:25 UTC, 32 essais réussis, 32 sous-essais ; 33 mutations tuées pour la raison attendue sur 33 ; témoin 21 essais
sans échec avant et après), puis passage indépendant de 18:33 à 18:35 UTC (message du commit `5e352ec`). Après la correction :
33 essais réussis, 34 mutations tuées sur 34 (directeur, message du commit `e58cfec` et message au repreneur) ; même résultat au
passage du contre-lecteur R2 n° 1 (33 essais, 32 sous-essais, 19:11:17 à 19:11:58 UTC ; 34 mutations sur 34, témoin 22 essais,
19:14:31 à 19:17:56 UTC ; section 10, L11). **Au brouillon 4, sur le code final** (repreneur, section 10, L12) : **37 essais
réussis, 35 sous-essais ; 43 mutations tuées pour la raison attendue sur 43**, témoin 26 essais sans échec avant et après.

## 0 ter. Changements du brouillon 3 au brouillon 4

1. **Contre-lecture R2 n° 1** (`prereg/contre-lecture-preenregistrement-validation-nul-v9-v1.md`, sha256
   `41f4f56d85456520394835f96d7c6a5d06b51138dc985fd0d40fdb67cac9b9d5`, sur le brouillon 2 ; couples
   `prereg/couples-contre-lecture-validation-nul-v9-v1.json`, sha256 `78c9b1e5c1f2337c6a5ee09cd7d24c35b050242ea61b4c83b4a31d2479e71f20`) :
   la preuve tient, refaite et éprouvée sans écart ; non scellable à cause de B1 ; scellable après couples une fois B1 levé.
2. **Couples** : les 23 qui s'appliquent tels quels au brouillon 3 (T07 à T23, T25, T26, T29, T30, T34, T36) sont appliqués
   tels quels, dans l'ordre du fichier ; les 15 d'I7, dont le passage du brouillon 2 n'existe plus (T01 à T06, T24, T27, T28, T31 à
   T33, T35, T37, T38), sont refaits sur le texte du brouillon 3 : statut, paragraphe de la correction, tableau d'en-tête (une
   colonne « brouillon 4 »), passages des essais et mutations, ligne « durée » de la section 9, paragraphe du banc de mutations,
   lignes L11 (contre-lecteur) et L12 (brouillon 4) de la section 10 (le brouillon 3 avait déjà une L10), section 12 et son bloc,
   étape 1 de la section 14, annexe B. Puis les mentions « à ajouter » des couples T07, T10, T21 à T23 et T25 sont mises à l'état
   du brouillon 4 (essais faits). Construction et contrôles (chaque « ancien » présent une seule fois) : `construire_b4.py`
   (bloc-notes `…/scratchpad/validation-b4/`).
3. **B1 levé** (essais seulement, aucun fichier gelé) : `GrainesEtPreenregistrement.test_mode_decisif_cas_sain_et_refus` — cas
   sain : texte d'essai scellé au nom décisif gelant les 14 empreintes, sans option → code 3 (course lancée une fois, bouchon de
   `jouer_tout`), 31 lignes du plan, 1 000 répétitions, durée transmise 172 800 s, entropie = empreinte du texte, manifeste
   « decisif » ; artefacts : `--lignes M01`, `--repetitions 999` → code 2, texte jamais lu, rien écrit ; sous-essai
   « monotonie-richesse » de `test_banc_reduit_et_liste_d_arret` (log W v9 2,0 contre v8 1,0, aucune promotion → code 3,
   `MonotonieViolee`). Mutations G1 à G5 du contre-lecteur ajoutées au banc : tuées pour la raison attendue.
4. **I5, I6 levés** : `LectureGelee.test_ordre_des_issues` (M03 à 90/1 000 et perte de I02 à 120/1 000 → « trou » ; perte de I02 et
   M02 apparié à 20/1 000 → « puissance perdue ») ; `CertificatMorceaux.test_valeur_certifiee_sous_optimisation_tronquee` (les 30
   mondes de l'essai de domination, `PALIERS_MU = (1e-2,)`, `PAS_MAX_PAR_PALIER = 1` : valeur ≥ vraisemblance du monde à chaque
   instant ; dents : meilleure valeur atteinte + 10⁻³ dessous à au moins un instant). Mutations L1, L2 et C5 : tuées.
5. **I2 levé — `pole/nul_v9.py` modifié pour sa description seulement** (empreinte `8cb44adf…aebc655` → `7ae450df…e46ee95` ;
   la ligne du bloc de la section 12 suit) : `NON_COUVERT_V9` ne garde que les quatre trous (le « bruit aveugle propre à chaque
   morceau, ou loi aveugle seule sur un morceau » en sort) ; constantes neuves `HORS_DU_NUL_PAR_CHOIX_V9` (loi en escalier aveugle ;
   loi aveugle seule sur un morceau ; bruit aveugle propre à un morceau, autre loi aveugle ou même loi avec un autre poids),
   `HORS_DU_NUL_PAR_NATURE_V9` (lois hors de l'archive), `RESERVES_V9` (mondes sans mémoire ; traits finis ; marge de Newton des
   membres log-linéaires) ; `PHRASES_MEMBRES_V9` dit « même loi aveugle, même poids » ; fonction neuve `description_publique()`
   (maximum au dénominateur, classe couverte, garantie, puis trous, choix, nature et réserves, dans cet ordre) ; `description()` les
   rend. **Aucun calcul ne change** : comparaison des arbres syntaxiques du module avant et après (seuls changent ces constantes et
   les deux fonctions de description ; la docstring du module dit les trois sortes) ; essais `DescriptionPublique` (dont un
   artefact : la liste du brouillon 2, qui rangeait un choix parmi les trous, est détectée) ; mutation « description publique :
   choix rangés parmi les trous », tuée.
6. **I1, I3, I4** par couples : lecture de « puissance perdue » à deux étages (T17, T18, T20 : fermeture des 18 lignes fatales et
   des 3 artefacts d'abord, puissance ensuite ; sans changer le code, sur les champs `lecture.fatales` et `lecture.artefact`) ;
   revendication publique et production après le mot explicite de Lazar sur le sens du bruit commun, la course peut partir (T11,
   T36) ; interdit de resceller pour changer de graine, et un arrêt déterministe est un défaut du code, pas un rejeu (T15, T26).
7. **Mineurs** : M1, M2 (T19) ; M3 (T16) ; M4 (T13) ; M5 (T12) ; M6 (T10) ; M9 (T29) ; M10 (phrase ajoutée en section 2) ; M7 : les
   docstrings du code gelé qui citent le brouillon 1 (banc, et `pole/nul_v9.py` ligne 6) ne sont pas touchées (seule la
   description du nul l'est) ; M8 : aucun essai synthétique d'A2 (facultatif, inaccessible dans une course complète : l'arrêt de
   monotonie passe avant).
8. **Essais et mutations sur le code final** (L12) : 37 essais réussis, 35 sous-essais ; 43 mutations tuées pour la raison attendue
   sur 43 ; témoin 26 essais sans échec avant et après.

Rien d'autre ne change : lignes, scénarios, graines, métriques, familles de Holm, seuils, prédictions, audits, liste d'arrêt.

## 0 bis. Changements du brouillon 2 au brouillon 3

1. **Correction du banc faite par le directeur** (commit `e58cfec`, 19:05:02 UTC) : `demonstrations/banc_tricheurs_v9.py`,
   `DUREE_MAX_S = 48 * 3600.0` (ligne 84, avec le commentaire « garde contre une boucle folle seulement (course attendue : 1,3 à
   5 h) »), docstring (garde de durée et usage `[--duree-max-s 172800]`) ; sha256 `7e4bff5995df2a7d62a4f5a2f5f9176da614e657a55b05183325fa2fc6e24e44`.
2. **Essai neuf** : `GrainesEtPreenregistrement.test_duree_du_mode_decisif_48_h` (`essais/test_nul_v9.py`, sha256
   `9eb966ad…a67b21`) — cas sain : la durée gelée vaut 48 h ; artefact : un texte décisif lancé avec `--duree-max-s 28800` (l'ancienne
   durée) est refusé, code 2, avant même la lecture du texte. **Mutation neuve** : « durée du mode décisif non gardée (une autre
   durée acceptée) » (`essais/mutations_nul_v9.py`, sha256 `9cb305e4…252d16`), tuée par cet essai. Directeur : 33 essais réussis, 34
   mutations tuées sur 34 (non relancé ici).
3. **Section 12** : le jeton du brouillon 2 est remplacé par l'empreinte du banc corrigé ; les 14 lignes sont égales à
   `FICHIERS_GELES` et aux fichiers de l'arbre (égal au commit `e58cfec`), vérifié à 19:15 UTC ; texte accepté par le banc corrigé
   (scellement simulé hors du dépôt, section 10, L10).
4. **Sections 9 et 14, annexe B** : la garde de durée renvoie à son essai ; l'étape 1 de la procédure est faite ; l'annexe B est
   gardée comme trace de la correction.
5. Remarque (sans effet sur la course) : le cas sain de l'essai neuf vérifie la constante gelée, non le passage de la garde par
   une course décisive à la durée par défaut ; la garde le permet par construction (la valeur par défaut de `--duree-max-s` est
   `DUREE_MAX_S`), et la commande de la section 5 ne passe pas l'option.

Rien d'autre ne change.

## 0. Changements du brouillon 1 au brouillon 2

Décisions de Lazar portées (défauts de Lazar sous 48 heures, relayés par le directeur ; mots de Lazar : « prends des budgets
et plafonds très larges », « je ne veux pas de résultats non concluants par défaut de conception, de plafond ») :

1. **Marge de perte de puissance : option (a), 0,05 sur chacune des 5 lignes de puissance** (annexe A) ; le marqueur du
   brouillon 1 est levé ; la constante du banc (`MARGE_PERTE = 0.05`, ligne 87) porte déjà (a) : rien à changer dans le code.
2. **Sens de « rien au-delà de l'archive » : bruit commun aux morceaux** (une loi en escalier aveugle reste promouvable) —
   porté comme défaut, **déclaré comme choix de revendication à confirmer** par Lazar (section 2, dernier point ; section 14,
   étape 2). La course n'en dépend pas : elle éprouve le nul tel qu'il est écrit.
3. **Durée de la course décisive : 48 heures** au lieu de 8, **sans couperet** : la garde ne sert qu'à arrêter une boucle folle
   (durée attendue 2 à 5 heures sur la machine partagée, section 5) ; le banc refusera toute autre valeur en mode décisif
   (sections 5 et 9). **Correction du code faite au commit `e58cfec`** (annexe B ; essais du mode décisif complétés au brouillon 4, B1 de la contre-lecture).
4. **Juge de production inchangé (nul v8)** : le v9 n'entre en production qu'après la course et la décision de Lazar (section 7,
   dernier paragraphe) ; c'était la proposition du brouillon 1, c'est désormais la décision.
5. **Commit `5e352ec` cité ; six empreintes recalculées** (en-tête) ; elles sont égales à celles du rapport de rédaction, et
   l'empreinte du rapport, qu'il ne pouvait pas porter, est ajoutée.
6. **Section 1 bis, nouvelle : les deux corrections au brief écrites en clair** (dénominateur = maximum sur les membres, jamais
   un mélange a priori ; le banc v8 joue 18 lignes sur 15 scénarios, pas « 27 tricheurs »). Le brouillon 1 les disait en
   passant (sections 1 et 4 du rapport) ; elles sont ici énoncées, justifiées et rattachées à leur source.
7. **Section 12 : 13 des 14 empreintes gelées calculées au commit `5e352ec`** (aucune n'est touchée par la correction de la
   durée) ; la quatorzième, celle du banc v9 corrigé, est celle du commit `e58cfec` (`7e4bff59…6e24e44`), portée par la
   contre-lecture R2 n° 1. Le brouillon 1 laissait tout le bloc vide.
8. **Section 4, P7 et section 7** : l'issue attendue sous la marge (a) est « puissance perdue » (portée par I02) ; c'est une issue
   conclusive, écrite d'avance, qui renvoie à Lazar la seule question du prix — non un « non concluant » par défaut de
   conception (ce que Lazar ne veut pas). Aucun seuil ni aucune prédiction n'est changé.
9. **Section 14 (procédure)** : étapes réordonnées (correction de la durée, essais et mutations rejoués, empreinte du banc
   recalculée, puis contre-lecture) ; ordre recommandé tenu : **validation du v9 d'abord** (gratuite, hors ligne), **attaque v4
   ensuite**. Les décisions de Lazar sur l'attaque contre le v9 (W1 et W2, 24 cartes par monde, un fil, GO-2026-11-02-22,
   200 USD) sont portées par le texte de l'attaque v4 (`prereg/preenregistrement-attaque-goodhart-v4-brouillon1.md`), pas ici.
10. **Annexe A** : décision consignée ; les options (b) à (d) restent, comme trace de ce qui n'a pas été choisi.
11. **Annexe B, nouvelle** : la correction du banc, ligne par ligne, et l'essai à ajouter pour la garde de durée (cas sain et
    artefact, R5).

Rien d'autre ne change : lignes, scénarios, graines, métriques, familles de Holm, seuils, prédictions P1 à P7, audits A1 à A6,
liste d'arrêt (à la durée près), portée.

## 1. Objet et motivation

Le nul v8 (`pole/nul_v8.py`, sha256 `cc452aaf…b976b888`, lignes 83 à 90) déclare lui-même ne pas couvrir la recombinaison par
morceaux de lois connues. L'attaque du 2 novembre l'a confirmé : sur le monde W2 (S1 sur la sous-population 0, S2 sur la
sous-population 1 ; `pole/attaque_goodhart_v2.py`, fonction `carte`, sha256 `3c9de8b8…92959e703`), un proposeur modèle de
langage qui lit la description du juge trouve une loi promue sous v8, qui n'apporte rien au-delà de l'archive. **Chiffres de
motivation, transcrits et non vérifiés sur leur source** (R7 : non opposables) : le brouillon de la reprise
(`prereg/preenregistrement-attaque-goodhart-v3-brouillon1.md`, sha256 `2c0465be…6a92fa`, section 0) rapporte, d'après le
verdict de la course A1 (`verdict-a1-v1.md`, sha256 `795e5e99…`, dépôt privé, non lu ici), « W2 : 12/24 … portée par Argon seul
(12/12) » et « Argon trouvait le trou dès la première tentative dans les deux conditions ». Ce texte n'en tire aucun chiffre
décisif.

Décision de conception (rapport de rédaction, sections 2 et 3) : le nul v9 est le nul v8 **plus** trois membres ajustés « par
morceaux » sur les lois connues de la fiche (parents puis survivantes, celles du membre `ajuste_lineaire:archive`) :
`morceaux:sous_population` (un morceau par valeur de g) et `morceaux:seuil:z<j>` pour chaque trait j (deux morceaux,
z_j ≤ s et z_j > s, **tout seuil réel s**, ajusté) ; sur chaque morceau un mélange des lois connues propre au morceau, plus un
bruit aveugle fixe **commun** à tous les morceaux. La valeur d'un membre est un **certificat** (écart de Frank-Wolfe) qui
domine le maximum de vraisemblance de sa famille quel que soit l'état de l'optimisation ; le dénominateur reste le
**maximum** des membres (section 1 bis).

Argument de validité (rapport, section 3) : pour tout monde P d'une famille du nul v9, W_t ≤ q(y_1..t)/P(y_1..t) à chaque
instant lu, martingale de test sous P ; Ville borne la promotion par α ; le nul v9 contient le v8, donc W(v9) ≤ W(v8)
trajectoire par trajectoire. **Ce que le banc mesure, l'argument ne le remplace pas** : le prix en puissance sur des lois
vraiment neuves, et le comportement réel du code.

## 1 bis. Deux corrections au brief, écrites en clair

**Correction 1 — le dénominateur reste un maximum sur les membres, jamais un mélange a priori.** Le brief demandait un
dénominateur « mélange a priori sur les membres » du nul. Ce texte ne le fait pas, et voici pourquoi (rapport, section 3.5).
Notons v_F(t) la valeur du membre F à l'instant t (log-vraisemblance maximale certifiée de sa famille sur les t premières
issues), et log W_t = N_t − D_t, avec N_t la log-vraisemblance de la loi gelée de la fiche.
- Avec le **maximum**, D_t = max_F v_F(t) : pour un monde P d'un membre F*, D_t ≥ v_{F*}(t) ≥ log P(y_1..t), donc
  W_t ≤ q(y_1..t)/P(y_1..t), martingale de test sous P, et Ville donne P(promotion) ≤ α **pour tout membre, quel que soit
  leur nombre**.
- Avec un **mélange a priori**, D̃_t = log Σ_F π_F·exp(v_F(t)) : on n'a que D̃_t ≥ log π_{F*} + log P(y_1..t), donc
  W̃_t ≤ Λ_t/π_{F*} et Ville ne donne plus que P(promotion) ≤ α/π_{F*}. La garantie se dégrade d'un facteur 1/π_{F*} ; pour un
  membre à seuil continu sous un a priori diffus, la masse de la cellule du vrai seuil est de l'ordre de 1/t : la garantie
  disparaît.
- Le mélange a priori qui **garde** Ville est celui du **numérateur** (pari à fraction : mélange à poids fixés de lois
  prévisibles, chaque rapport étant une martingale de test sous la même loi P) ; il est déjà dans le juge, inchangé. Si le brief
  entendait par « mélange » une répartition de α entre membres (seuil 1/(α·π_F) pour le membre F), le maximum n'en a pas
  besoin : W_max ≤ W̃ trajectoire par trajectoire, et le maximum garde α pour chaque membre sans rien répartir.
Conséquence : le juge v9 est valide quel que soit le nombre de membres (trois de plus que le v8 pour une fiche à deux traits) ;
le seul prix de membres supplémentaires est un prix en puissance, que la course mesure (H2).

**Correction 2 — le banc v8 joue 18 lignes construites sur 15 scénarios, pas « 27 tricheurs ».** Le texte scellé de l'attaque
(`prereg/preenregistrement-attaque-goodhart-v2-v1.md`, sha256 `fc81d015…a925b65`, ligne 26) dit le juge « validé contre 27
tricheurs **scriptés** (`demonstrations/banc_tricheurs_v8.py`) », et le brief l'a repris. Vérifié sur le fichier
(`demonstrations/banc_tricheurs_v8.py`, sha256 `0be47e4b…ba08c03`, lignes 114 à 127, constantes `FATALES`, `PUISSANCE`,
`LIGNES` ; relu par ce repreneur le 2 novembre à 18:50 UTC) : `LIGNES` = 11 lignes fatales (T01, T02, T03u, T03b, T04, T05s,
T09g, T09l, T12a, T17s, nul exact) + l'artefact T01|v1 + 2 scénarios de puissance (fille neuve, fraîche neuve) joués chacun sous
v8 et sous v7 (4 lignes) + 2 lignes mesurées (T07, T12b) = **18 lignes** ; scénarios distincts = 11 + 2 + 2 = **15** (T01 sert
deux fois). « 27 » est la numérotation T01 à T27 de la note du banc, dont le banc v8 ne joue qu'une partie. La phrase juste est :
« validé par un banc de 18 lignes sur 15 scénarios de tricheurs scriptés ». Le banc v9 reprend les 15 scénarios du v8 et en
ajoute 15 (section 3) ; le texte scellé de l'attaque n'est pas modifié (il est scellé) : la correction vaudra pour tout texte
nouveau qui le cite.

## 2. Ce qui est couvert et ce qui ne l'est pas (dit d'avance)

- **Couvert en plus du v8** : toute loi qui, sur chaque morceau d'une partition à un niveau — par sous-population (un morceau
  par valeur de g), ou par un seuil réel quelconque sur un seul trait —, est un mélange de lois connues propre au morceau,
  mélangé à une même loi aveugle fixe **avec le même poids** sur tous les morceaux (un même vecteur de bruit r, de masse
  commune ; dont le monde W2, tout si/sinon de deux lois connues ou de deux mélanges de lois connues sur un seuil, et ces lois
  « avec bruit » commun). Preuve : rapport, section 3 ; refaite par la contre-lecture R2 n° 1, section 1.
- **Hors du nul v9** (dit, depuis le brouillon 4, par la description publique du nul, `nul_v9.description_publique()` : (a) par
  `NON_COUVERT_V9`, (b) par `HORS_DU_NUL_PAR_CHOIX_V9`, (c) par `HORS_DU_NUL_PAR_NATURE_V9` et `RESERVES_V9` ; au commit `e58cfec`,
  `NON_COUVERT_V9` rangeait (b) parmi ses cinq phrases et aucune description publique du v9 n'existait, I2 de la contre-lecture) : (a) **trous** — recombinaisons de lois connues que le v9 ne couvre pas : profondeur 2 et plus,
  plusieurs seuils sur un même trait, seuils sur une combinaison de traits ; poids qui varient continûment avec l'instance
  (aiguillage doux) ; lois tempérées ou inclinées différemment par morceau ; compositions d'étapes ; produits de lois (sauf,
  pour une fille, celui des deux parents) ; déformations non monotones (question de nouveauté, T12) ; (b) **hors du nul par le
  choix du point suivant**, promouvables comme dépendances nouvelles : bruit aveugle propre à un morceau (autre loi aveugle,
  ou même loi aveugle avec un autre poids), loi aveugle seule sur un morceau, loi en escalier aveugle ; (c) lois hors de
  l'archive ; mondes avec mémoire (réserve du v8) ; traits non finis (hors de la preuve ; impossibles dans le banc).
  La description publique sépare ces trois sortes (essai `DescriptionPublique.test_description_publique_separe_trous_choix_et_nature`) ;
  l'attaque v4 et toute production la reprennent. La promouvabilité d'une loi en escalier aveugle **pure** n'est mesurée par aucune
  ligne du banc (H04 n'en est qu'un voisin) : la revendication porte sur la famille du nul (aucun sommet mixte), pas sur une
  puissance (M10 de la contre-lecture).
- **Une loi en escalier aveugle (loi fixe propre à chaque morceau) reste promouvable** : elle dit une dépendance que
  l'archive ne dit pas. C'est pourquoi le bruit est commun aux morceaux (rapport, section 2.2). **Choix de revendication,
  proposé, à confirmer par Lazar** (proposition du 2 novembre ; la course n'en dépend pas ; aucune revendication publique
  ni mise en production sur ce sens avant sa réponse explicite, section 14, étape 2) : « rien au-delà de l'archive »
  s'entend « aucune recombinaison des lois connues n'est neuve ; une dépendance nouvelle de l'issue à g ou à un seuil l'est ».
  Le sens contraire (bruit propre à chaque morceau) mettrait toute loi en escalier aveugle dans le nul : elle ne pourrait plus
  jamais être promue. Une réponse contraire de Lazar n'est pas une correction de ce texte : c'est un nul nouveau (v10), un banc
  nouveau et un préenregistrement nouveau.

## 3. Hypothèses

Sous le nul v9 du juge (banc `demonstrations/banc_tricheurs_v9.py`, mondes et tricheurs des bancs v7 et v8 : K = 3 issues,
2 traits gaussiens, 2 sous-populations ; filles : 50 tirages de calibrage puis 200 d'évaluation ; fiches sans parent : 200
tirages ; lecture aux instants 25, 50, …, 200 ; marge des filles 2δ₀ = 0,02 ; ordre d'exécution secret ; α = 0,05), **H** est
la conjonction :

- **H1 (validité)** : chacune des 18 lignes fatales est promue au taux ≤ α ;
- **H2 (prix en puissance)** : sur chacune des 5 lignes de puissance, la **perte appariée** (part des répétitions promues sous
  le v8 apparié et non sous v9, sur les mêmes issues) est ≤ **0,05** (marge (a), annexe A) ;
- **H3 (dents du banc)** : T01|v1 est promu au taux > α, **et** M01 et M02 sont promus au-dessus de α sous le v8 apparié (le
  trou que le v9 ferme est vu par le banc) ;
- **H4 (le monde de l'attaque)** : M01, le monde W2, est promu au taux ≤ α sous v9 (il appartient à H1, dit à part).

Lignes (A, B : parents ; S1, S2 : survivantes ; N : loi neuve ; toutes softmax tirées au hasard ; q : loi aveugle tirée de
Dirichlet ; le monde de chaque tricheur est sa propre loi) :

| ligne | genre | loi de la fiche (= monde) | classe sous v9 | rôle |
|---|---|---|---|---|
| T01, T02, T03u, T03b, T04, T09l, T17s, nul exact | comme le v8 | comme le v8 | linéaire (membres du v8) | fatale |
| T05s, T09g | comme le v8 | comme le v8 | log-linéaire (membres du v8) | fatale |
| T12a | fille | A déformé (oscillation), monde A | hors classe ; le monde est au nul (Ville) | fatale |
| M01 | sans parent | S1 si g = 0, S2 si g = 1 (**forme du monde W2**, lois tirées à chaque répétition ; les cartes 0 à 3 de W2 : essai `test_monde_w2_de_l_attaque_membre_du_nul_v9`) | par morceaux | fatale |
| M02 | sans parent | S1 si z_j > s, S2 sinon (j au hasard, s uniforme dans [−1 ; 1]) | par morceaux | fatale |
| M03 | sans parent | (1 − ε)·M01 + ε·q, ε dans [0,05 ; 0,30] (bruit commun) | par morceaux | fatale |
| M04 | sans parent | (1 − ε)·M02 + ε·q | par morceaux | fatale |
| M05 | sans parent | g = 0 : π·S1 + (1 − π)·S2 ; g = 1 : π′·S1 + (1 − π′)·S2 (π, π′ uniformes) | par morceaux | fatale |
| M06 | fille | A si z_j > s, S1 sinon | par morceaux (parent et survivante) | fatale |
| M07 | sans parent | S1 si z_j > s, S2 sinon, s dans [1,5 ; 2,5] (quelques instances au-dessus) | par morceaux | fatale |
| T01\|v1 | fille | ½A + ½q, jugée sous le nul v1 | — | artefact requis |
| M01, M02 sous le v8 apparié | | (mêmes répétitions que leur ligne v9) | hors du v8 | artefact requis |
| fille neuve | fille | A sur g = 0, N ailleurs | — | puissance appariée |
| fraîche neuve | sans parent | N | — | puissance appariée |
| I01 | sans parent | interaction forte : q₁ si z0 et z1 sont du même signe, q₂ sinon (lois fixes, logits d'écart type 1,2) | hors du v9 | puissance appariée |
| I02 | sans parent | interaction faible (logits d'écart type 0,45) | hors du v9 | puissance appariée |
| F03 | sans parent | N à poids × 0,3 (loi neuve faible) | — | puissance appariée |
| T07, T12b | fille | comme le v8 | hors classe ; T12b : la fiche dit vrai | mesurée |
| H01 | sans parent | profondeur 2 : g = 0 : (S1 si z_j > s, S2 sinon) ; g = 1 : S2 | non couverte | mesurée |
| H02 | sans parent | escalier sur un trait (trois seuils : S2, ¼S1 + ¾S2, ¾S1 + ¼S2, S1) | non couverte | mesurée |
| H03 | sans parent | produit normalisé S1·S2 | non couverte | mesurée |
| H04 | sans parent | bruit propre à chaque morceau (S1 + q sur g = 0, S2 + q′ sur g = 1) | non couverte | mesurée |
| H05 | sans parent | S1 tempérée sur g = 0, S2 sur g = 1 | non couverte | mesurée |

Les interactions I01 et I02 ne dépendent que du signe de z0·z1 : la loi de l'issue sachant un seul trait, ou sachant g, est
la même partout, et aucune loi du nul v9 ne les égale (en général). Un membre par morceaux peut toutefois en approcher une
partie : sur un morceau coupé sur un trait, les survivantes, qui dépendent des deux traits, suivent en partie l'autre signe —
c'est le prix mesuré (P4). Elles sont « hors de l'archive et hors du nul v9 » au sens de la demande.

## 4. Prédictions chiffrées et signées (ouvertes dans les deux sens)

Inchangées depuis le brouillon 1. Écrites avant la course décisive, **après** les lectures préalables de la section 10
(déclaré) : elles en tiennent compte et, pour cette raison, **ne décident pas de l'issue**. Rapportées par le banc
(`lecture.predictions`, `PREDICTIONS`).

- **P1a** (signe : sous α, par construction) : les 8 lignes de la classe linéaire et les 7 lignes par morceaux (M01 à M07) :
  **0 promotion sur 1 000**, et log W ≤ 10⁻⁶ à chaque répétition. Ouverte : une seule promotion, ou un log W au-dessus de
  10⁻⁶, falsifie le certificat ou le code (audits A1 et A4, conséquences en section 8).
- **P1b** : T05s et T09g (classe log-linéaire, marge de Newton non démontrée, réserve du v8) : **0 sur 1 000**, log W max
  ≤ +0,25.
- **P1c** : T12a (vérité au nul, fiche hors classe) : **au plus 10 sur 1 000** (Ville n'impose que 50).
- **P2** (signe : le banc voit le trou du v8) : sous le v8 apparié, M01 **≥ 0,95**, M02 **≥ 0,90** (lecture L3 : 0,99 et
  0,96 sur 100). Ouverte : sous 0,50, le trou se fermerait sans le v9 (audit A3).
- **P3** : T01|v1 dans **[0,30 ; 0,60]** (prédiction du v8, reprise).
- **P4** (signe : perte ≥ 0, par la monotonie ; ouverte vers le haut et vers le bas) : perte appariée dans
  fille neuve **[0,01 ; 0,08]**, fraîche neuve **[0,00 ; 0,03]**, I01 **[0,02 ; 0,09]**, I02 **[0,06 ; 0,17]**,
  F03 **[0,01 ; 0,07]** (L3, 100 répétitions : 0,04 ; 0,00 ; 0,05 ; 0,11 ; 0,03). Sous la borne basse : le surajustement des
  membres par morceaux coûte moins qu'à blanc ; au-dessus de la borne haute : il coûte plus.
- **P5** (puissance sous v9) : fille neuve **[0,90 ; 1]**, fraîche neuve **[0,88 ; 1]**, I01 **[0,80 ; 1]**, I02
  **[0,30 ; 0,52]**, F03 **[0,60 ; 0,82]** (L3 : 0,96 ; 0,94 ; 0,87 ; 0,41 ; 0,72).
- **P6** (mesurées sous v9, hors de la classe couverte ; taux de fausse promotion pour les recombinaisons de lois connues que
  le v9 ne couvre pas, T07, H01, H02, H03, H05 ; pour T12b, dont la fiche dit vrai, et pour H04, dont le bruit propre au
  morceau est une dépendance aveugle nouvelle que le choix de la section 2 tient pour neuve, taux de promotion d'une loi qui
  n'est pas, ou pas seulement, une recombinaison de l'archive) : T07 **≤ 0,03** ;
  T12b **[0,65 ; 0,88]** ; H01 **[0,80 ; 0,96]** ; H02 **[0,12 ; 0,32]** ; H03 **[0,82 ; 0,96]** ; H04 **[0,16 ; 0,38]** ;
  H05 **[0,04 ; 0,18]** (L3 : 0,01 ; 0,77 ; 0,89 ; 0,21 ; 0,90 ; 0,26 ; 0,10).
- **P7** (issue) : sous la marge décidée (option (a) : 0,05 sur chaque ligne), **« puissance perdue »**, portée par I02 (perte
  attendue ≈ 0,11 ; « non tenue » dès 68 pertes sur 1 000 au rang 1 de Holm : probabilité ≈ 1 si la vraie perte est 0,10) ;
  I01 et fille neuve près de la marge. Ouverte : « confirmé » dirait une perte de I02 sous ≈ 0,035 (bien en dessous de la
  lecture préalable) ; « trou » dirait une ligne fatale au-dessus de α (contraire à l'argument).

## 5. Plan d'analyse

- **Pourquoi un banc v9** : le banc v8 ne juge pas sous le nul v9 et n'évalue pas deux nuls sur les mêmes issues ; le banc v9
  charge le banc v8 (instance propre, inchangé) pour ses scénarios, son juge v1 et sa statistique, et ajoute le juge v9
  (`engagement_v9`, `juger_v9`) et le v8 apparié (`nul_v9.evaluer_sur_issues` sur `nul_v9.sans_morceaux(engagement)`, la
  bibliothèque v9 privée de ses membres par morceaux, qui est exactement celle du v8 : essai
  `EvaluateurV9.test_identique_a_v2_sans_morceaux`).
- **Lignes et répétitions** : les 31 lignes de la section 3 (`LIGNES` : 18 fatales sous v9 ; T01|v1 ; 5 de puissance ; 7
  mesurées), **1 000 répétitions indépendantes par ligne**, scénario tiré à neuf à chaque répétition ; dans chaque répétition
  d'une ligne v9, la même fiche est évaluée sous v9 (juge complet, gardes comprises) et sous le v8 apparié (mêmes issues).
- **Graines (R9), règle exacte**, celle du banc v8 inchangée : entropie racine E = l'empreinte SHA-256 des octets du fichier
  scellé `orchestrator/prereg/preenregistrement-validation-nul-v9-vN.md`, lue comme entier non signé gros-boutiste ; répétition
  r de la ligne « nom|nul » : `numpy.random.SeedSequence(E, spawn_key=(c, r))`, c = entier gros-boutiste des 4 premiers octets
  de SHA-256(« nom|nul ») ; `.spawn(3)` : scénario, noyau, tirages frais, chacun réduit à s₀ + 2⁶⁴·s₁ ; le v8 apparié n'a pas de
  graine propre (mêmes issues). Le banc calcule E depuis le fichier ; espaces disjoints : exploratoire [0 ; 2⁶⁴[, décisif
  ≥ 2⁶⁴ (refus sinon). Clés de lignes distinctes vérifiées (`verifier_cles_distinctes`, 31 clés).
- **Un scellement, une course décisive** (règle du v8, section 4 de son préenregistrement, transposée) : aucune course en
  mode décisif sur aucune version de ce fichier avant son scellement (vérifié avant scellement : aucun dossier
  `resultats/banc-tricheurs-v9-validation-v1*`, aucun compagnon `.sha256` de ce texte) ; la course décisive n'est lancée
  qu'après la poussée du commit qui contient ce fichier, son compagnon `.sha256` et les 14 fichiers gelés (section 14). Toute
  course décisive dont le manifeste est écrit est rapportée, qu'elle aille à son terme ou non. Une issue rendue (code 0 ou 1)
  fait foi : modifier ce fichier, le resceller (nouvelle graine) et rejouer n'est pas admis ; une reprise passe par un
  préenregistrement de version nouvelle (R12) qui cite la première course, son dossier et son empreinte. Un arrêt sans taux
  (code 3) n'autorise que le rejeu de la section 9, et seulement pour un arrêt que les mêmes graines ne reproduisent pas
  (durée) : un arrêt déterministe (erreur, richesse non finie, monotonie violée) est un défaut du code du v9 (section 9).
- **Code gelé** : les 14 fichiers de `FICHIERS_GELES` (fermeture des imports mesurée par l'essai
  `GrainesEtPreenregistrement.test_fichiers_geles_couvrent_les_imports`, égalité exacte) ; le banc refuse la course si l'un
  manque au bloc de la section 12 ou diffère de son empreinte.
- **Commande exacte** (depuis `orchestrator/`, dossier neuf ; `--duree-max-s` vaut par défaut la durée gelée, 172 800 s, et
  n'est pas passé) :

  ```
  nice -n 10 python3 -I -B demonstrations/banc_tricheurs_v9.py ../resultats/banc-tricheurs-v9-validation-v1 \
      --preenregistrement prereg/preenregistrement-validation-nul-v9-vN.md --repetitions 1000 --processus 2
  ```

  Sorties : `manifeste.json` (avant la course) et `banc-tricheurs-v9.json`, chacun avec son compagnon `.sha256` écrit par le
  banc dans le dossier de sortie ; le code de sortie (0, 1, 2, 3) **ne décide pas**.
- **Aucune dépense** : tout est calcul local sur processeur ; aucun modèle, aucun réseau, aucun GO de calcul n'est requis.
- **Durée** (lectures L3 et L6, `nice -n 10`, machine partagée avec d'autres agents, charge 1 à 5 sur 2 cœurs) : 0,3 s (L6)
  à 0,5 s (L3) de processeur par répétition de ligne (v9 et v8 apparié ; les filles coûtent environ deux fois une fiche sans
  parent) ; 31 000 répétitions ≈ 9 300 à 15 500 s de processeur, soit **≈ 1,3 à 2,2 h sur deux cœurs libres, 2 à 5 h sur la
  machine partagée**. **Durée maximale gelée : 48 heures** (172 800 s ; décision de Lazar, section 0, point 3) — ≈ 10 fois la
  durée haute attendue sur machine partagée : ce n'est pas un couperet de plan, c'est une garde contre une boucle folle (un
  calcul par morceaux qui ne finirait pas, une répétition bloquée) ; une course lente mais saine n'est jamais arrêtée par elle
  dans les conditions mesurées (il faudrait ≈ 5,6 s d'horloge par répétition en moyenne, même sur un seul cœur effectif, soit onze fois le coût moyen mesuré et six fois le pire coût mesuré par ligne, T12b à ≈ 0,93 s par répétition en L3). Le brouillon 1
  gelait 8 heures, soit moins de deux fois la durée haute : sur une machine plus chargée qu'à blanc, la course pouvait
  s'arrêter sans verdict (code 3) — c'est le « non concluant par défaut de plafond » que Lazar exclut.

## 6. Métriques et puissance du banc

- **Taux de promotion** d'une ligne = promotions / répétitions (décision du juge : W ≥ 1/α à un instant lu, et pour une fille
  la marge 2δ₀ sur la meilleure enveloppe, les membres ajustés v8 et v9 comptant parmi les enveloppes).
- **Bornes** : Clopper-Pearson exactes, unilatérales à 95 % ; valeurs p par le test binomial exact unilatéral.
- **Lignes fatales (H1, H4)** : famille des 18 lignes ; « tenue » si H0 « taux ≥ α » est rejetée par Holm au niveau familial
  0,05 ; « non tenue » si H0 « taux ≤ α » est rejetée par Holm ; sinon « non jugeable ». Nombre maximal de promotions sur 1 000
  compatible avec « tenue » selon le rang de Holm (`promotions_max_tenue(1000, 18)`) :
  31, 31, 31, 31, 31, 32, 32, 32, 32, 32, 33, 33, 33, 34, 34, 35, 36, 38 ; minimal pour « non tenue » : 71, 71, 71, 71, 70, 70,
  70, 70, 70, 69, 69, 69, 68, 68, 67, 66, 65, 63 (calcul `…/scratchpad/nul-v9/calculs/tables_v1.py`, section 10, L5).
  Puissance (`calculs/tables_v2.py`) : une ligne de vrai taux 0,01 est « tenue » avec probabilité 1,000 ; 0,02 : 0,993 (rang 1)
  à 1,000 (rang 18) ; 0,03 : 0,62 à 0,94 ; 0,04 : 0,08 à 0,41 ; 0,05 : 0,002 à 0,04.
- **Artefacts (H3)** : T01|v1, M01 et M02 sous le v8 apparié ; chacun « tenu » si sa borne basse de Clopper-Pearson > α, soit
  **au moins 63 promotions sur 1 000** ; intersection-union, sans correction.
- **Perte de puissance (H2)** : **appariée** ; d = (promues sous v8 et non sous v9)/1 000, proportion binomiale (la monotonie,
  gardée à chaque répétition, interdit l'inverse). « Tenue » si H0 « d ≥ 0,05 » est rejetée (test exact, Holm sur les 5
  lignes) ; « non tenue » si H0 « d ≤ 0,05 » est rejetée (Holm) ; sinon « non jugeable ». À la marge 0,05 : pertes maximales
  pour « tenue » selon le rang 34, 34, 35, 36, 38 ; « non tenue » dès 68 au rang 1 ; selon la vraie perte, probabilité de
  « tenue » : 0,02 → 0,999 à 1,000 ; 0,03 → 0,80 à 0,94 ; 0,04 → 0,19 à 0,41 ; 0,05 → 0,01 à 0,04 ; probabilité de « non
  tenue » au rang 1 : 0,06 → 0,16 ; 0,08 → 0,93 ; 0,10 → 1,00 (tables du brouillon 1, L5, non recalculées ici).
  Pourquoi apparier : sur les mêmes issues, seule la différence des dénominateurs joue ; la perte est une proportion simple,
  bornée exactement, au lieu d'une différence de deux échantillons indépendants (borne de Newcombe approchée du v8).
- **Rapportés sans critère** : médiane, 99ᵉ centile et maximum de log W max par ligne ; taux du v8 apparié sur toutes les
  lignes ; quatre premiers membres dominants à l'instant final ; taux des lignes mesurées.

## 7. Critères de lecture gelés et issues écrites d'avance

Calculés par `lire_v9` (code gelé), dans cet ordre, **avant** les conséquences des audits (section 8) :

1. **« trou »** — une ligne fatale au moins est non tenue. Lecture : le nul v9 ne ferme pas cette ligne (si c'est une ligne
   M, la classe par morceaux n'est pas fermée par le code tel qu'écrit, contrairement à l'argument : défaut à chercher) ; le
   v9 n'est pas validé ; réparation = version nouvelle, préenregistrement nouveau.
2. **« puissance perdue »** — aucune ligne fatale non tenue, une perte au moins non tenue. Lecture **à deux étages** : (i) si
   les 18 lignes fatales sont « tenues » **et** les 3 artefacts « tenus » (champs `lecture.fatales` et `lecture.artefact`), et
   si la règle de P1b (section 8) ne joue pas, le v9 ferme les lignes, au prix mesuré sur la ligne nommée ; **décision de
   Lazar** : accepter le prix (le v9 devient le nul du juge, la description publique dit le prix) ou chercher un nul moins
   coûteux (version nouvelle) ; (ii) sinon (une ligne fatale « non jugeable », un artefact non tenu ou non jugeable, ou la
   réserve log-linéaire), la perte est établie mais pas la validité sur cette course : « puissance perdue, validité non
   établie », le v9 n'est pas proposé en production. Les pertes et puissances observées sont publiées avec leurs bornes.
   C'est l'issue attendue sous la marge (a) (P7).
3. **« non concluant (banc sans dents) »** — rien de ce qui précède, mais un artefact (T01|v1, M01 ou M02 sous le v8 apparié)
   n'est pas tenu. Lecture : le banc n'a pas vu ce qu'il doit voir ; aucune conclusion sur le v9 ; réparer le banc.
4. **« confirmé »** — les 18 lignes fatales, les 3 artefacts et les 5 pertes tenus. Lecture : sur les mondes synthétiques du
   banc (K = 3, 2 traits, 2 sous-populations), aucune ligne fatale n'est promue au-dessus de α (Clopper-Pearson, Holm), dont
   les 7 tricheurs par morceaux et le monde W2 ; le banc voit le trou du v8 ; la perte de puissance appariée reste sous la
   marge sur les 5 lignes. Le v9 peut porter « validé sur la classe du banc (section 11) » ; rien n'est revendiqué hors de
   cette classe (section 2).
5. **« non concluant (précision insuffisante) »** — aucun des cas précédents. On rapporte, on ne conclut pas ; aucun
   complément de répétitions sur la même graine ; une nouvelle course passe par un préenregistrement nouveau.

Plan incomplet (`--lignes`, exploratoire) : « partielle (plan incomplet : aucune issue) ». Tout audit déclenché **suspend
l'issue** jusqu'à l'audit écrit (`issue_suspendue_par_audit`).

**Usage du nul v9 selon l'issue (décision de Lazar du 2 novembre : juge de production inchangé)** : le nul de production reste
le v8 (`cycle.membres_de_l_archive` inchangé) et la description publique du juge v8 dit la classe par morceaux non couverte.
Le v9 n'est proposé comme nul de production qu'après une issue « confirmé », ou « puissance perdue » lue au premier étage
(18 lignes fatales et 3 artefacts tenus, réserve log-linéaire non déclenchée) avec le prix accepté par Lazar ; le brancher demande alors une entrée v9 du cycle (fichier neuf) et une décision de Lazar (nœud « modification
d'hypothèse ou de revendication »). L'attaque v4 contre le juge v9 (texte à part) éprouve le v9 hors production, comme l'attaque
A1 a éprouvé le v8.

## 8. Audit de symétrie (R4), écrit d'avance

Inchangé depuis le brouillon 1. Calculés par le code (`lecture.audits`) : A1 à A5 ; lus par le contre-lecteur du verdict
(R13) : A6 et la règle de P1b.

- **A1** — une promotion sur une ligne refusée par construction (classes linéaire, par morceaux, log-linéaire).
- **A2** — perte négative (v9 plus puissant que le v8 apparié) : impossible par la monotonie, que le banc garde déjà à chaque
  répétition (arrêt, section 9) ; ici, double vérification.
- **A3** — T01|v1 hors de [0,10 ; 0,90] ; M01 ou M02 sous le v8 apparié sous 0,50 (trop bas : le banc perd ses dents ; trop
  beau pour le v9 : le trou se fermerait sans lui).
- **A4** — log W > 10⁻⁶ sur une répétition d'une ligne de la classe linéaire ou par morceaux (défaut du code ou du certificat,
  même sans promotion).
- **A5** — **propreté suspecte** : sur une ligne M, un membre par morceaux domine à l'instant final dans moins de la moitié
  des répétitions (un 0/1 000 qui ne viendrait pas du nul v9), compté parmi les quatre premiers membres dominants que le banc
  rapporte (`dominants` de `jouer_ligne`) : la troncature peut sous-estimer la part des membres par morceaux, jamais la
  surestimer ; un A5 déclenché se vérifie, pour l'audit écrit, en recomptant les dominants de la ligne sur les mêmes graines
  (calcul déterministe, sans effet sur l'issue). Repère L3 : `morceaux:sous_population` 100/100 sur M01 ; seuils 100/100 sur
  M02 ; M07 : seuils 90/100 (z0 : 41, z1 : 49) et `ajuste_log:archive:S2` 10 (le seuil extrême laisse dominer d'autres
  membres : à lire, pas un défaut).
- **A6** — toute issue « trou », « puissance perdue », ou « non concluant » : même audit avant lecture (une issue décevante
  est auditée comme une issue trop belle) ; « confirmé » sans déclencheur est relu de même (membres dominants, log W).

Conséquences : **A4, ou A1 sur la classe linéaire ou par morceaux** : course invalide d'office (le certificat est une
inégalité exacte) ; l'audit cherche la cause ; reprise en version nouvelle. **A1 sur T05s ou T09g seulement**, ou log W max
> +0,25 sur ces lignes : « confirmé » interdit, issue « non concluant (réserve log-linéaire) » sauf défaut localisé (règle du
v8) ; sous « puissance perdue », lecture au second étage (section 7, issue 2). Cette issue, appliquée par le
lecteur du verdict (R13), s'ajoute aux cinq de `lire_v9`. **A2, A3, A5, A6** : défaut trouvé → course invalide ; sinon l'issue est lue, note jointe.

## 9. Liste d'arrêt (chaque garde éprouvée sur un cas sain et un artefact, R5)

| garde | cas sain | artefact | essai (`essais/test_nul_v9.py`) |
|---|---|---|---|
| membres du v9 | membres v8 intacts puis 3 membres par morceaux ; fille : lois A, B, S1, S2 ; une seule loi connue : aucun | membre absent, en double, inattendu, lois tronquées ou réordonnées, partition ou type changés, membre linéaire du v8 retiré → `NulV9Refuse` | `MembresNulV9.*` |
| certificat | valeur ≥ log-vraisemblance du monde, 30 mondes de la famille, 5 instants ; seuil égal à une valeur observée ; référence scipy (SLSQP) sur 14 instances, à 10⁻² près ; mêmes 30 mondes sous optimisation tronquée (un palier, un pas) : valeur ≥ log-vraisemblance du monde (`test_valeur_certifiee_sous_optimisation_tronquee`, I6) | valeur atteinte au départ sous la vraisemblance du monde W2 (ce qu'un calcul sans certificat rendrait) ; monde hors famille (bruit propre au morceau) non dominé ; sous optimisation tronquée, « meilleure valeur atteinte + 10⁻³ » sous la vraisemblance du monde (mutation C5 de la contre-lecture, tuée : I6) | `CertificatMorceaux.*` |
| départ du calcul | départ admissible | hors contraintes, coordonnée nulle, non fini → `CalculMorceauxImpossible` | `test_garde_depart_non_admissible` |
| évaluateur | identique à `evaluer_v2` sans membre par morceaux (fille, fiche) ; départage par le nom ; monotonie v9 ≤ v8 | engagement modifié, tirages d'un autre engagement, membre de type inconnu, partition inconnue → refus | `EvaluateurV9.*` |
| tricheurs | monde W2 de l'attaque (cartes 0 à 3) et loi « si/sinon S1, S2 » : jamais promus sous v9, promus sous v8 ; M01 0/20, M02 à M07 0/8, log W ≤ 10⁻⁶ ; I01 et fraîche neuve ≥ 15/20, ≤ 2 pertes | sans membres par morceaux, M01 promu ≥ 16/20 | `TricheursParMorceaux.*` |
| perte appariée | comptée dans le bon sens (v8 oui, v9 non) | (mutation « à l'envers », tuée) | `test_perte_appariee_comptee_dans_le_bon_sens` |
| lecture gelée | tout tenu → « confirmé », aucun audit | « trou », « puissance perdue », « banc sans dents », « précision insuffisante », plan incomplet ; audits A1, A3, A4, A5 ; **ordre des issues** : fatale non tenue et perte non tenue → « trou » ; perte non tenue et artefact non tenu → « puissance perdue » (`test_ordre_des_issues`, I5 de la contre-lecture ; mutations L1 et L2 tuées) | `LectureGelee.*` |
| préenregistrement | fichier `…-nul-v9-v1.md` scellé, code gelé conforme | brouillon, non scellé, fichier manquant au gel, empreinte fausse, bon nom hors de `prereg/` | `test_cas_sain_et_artefacts_preenregistrement` |
| refus avant course | texte décisif scellé et conforme, sans option → les gardes passent et la course démarre (bouchon de `jouer_tout` : 31 tâches, 1 000 répétitions, 172 800 s, entropie = empreinte du texte ; B1) | brouillon en mode décisif, ligne inconnue, graine ≥ 2⁶⁴, graine négative, dossier non vide → code 2, aucune course ; en mode décisif, `--lignes M01` et `--repetitions 999` → code 2, texte jamais lu (B1 ; mutations G1 à G3 tuées) | `test_refus_du_banc_avant_toute_course`, `test_mode_decisif_cas_sain_et_refus` (B1) |
| durée gelée (48 h) | texte décisif scellé, durée par défaut → durée transmise à chaque ligne = 172 800 s (et `DUREE_MAX_S` = 48 h) | texte décisif et `--duree-max-s 28800` (l'ancienne valeur) → code 2, texte jamais lu | `test_duree_du_mode_decisif_48_h` (artefact), `test_mode_decisif_cas_sain_et_refus` (cas sain, B1) |
| liste d'arrêt | course réduite → code 0 | fatale promue → 1 ; durée → 3 (`ArretDuree`) ; erreur du juge → 3 ; **monotonie violée → 3** (`MonotonieViolee`) : par une promotion sous v9 sans promotion sous v8, et par la seule richesse, log W v9 > log W v8 + 10⁻⁶ sans promotion inversée (sous-essai « monotonie-richesse », B1 ; mutation G5 tuée) | `test_banc_reduit_et_liste_d_arret` |
| fermeture | imports mesurés dans un processus neuf = `FICHIERS_GELES` (14) | — | `test_fichiers_geles_couvrent_les_imports` |

Arrêts (code 3, aucun verdict, aucun taux) : ligne en erreur, richesse non finie, **monotonie violée** (une répétition où
log W v9 dépasse log W v8 de plus de 10⁻⁶, ou une promotion sous v9 sans promotion sous v8 : défaut du code), **durée
> 48 h** (garde contre une boucle folle). Après un arrêt de durée, rejeu dans un dossier de sortie neuf, même fichier scellé (règle du
v8). Après un arrêt déterministe (ligne en erreur, richesse non finie, monotonie violée : les mêmes graines le reproduisent),
pas de rejeu : l'arrêt est rapporté comme un défaut du code du v9 (le v9 n'est pas validé ; audit écrit, R4) ; réparation =
version nouvelle, préenregistrement nouveau. Refus avant toute course (code 2) : autre fichier, non scellé, code gelé absent ou différent, `--lignes`, répétitions
≠ 1 000, **durée ≠ 48 h**, entropie < 2⁶⁴, dossier non vide.

Banc de mutations (`essais/mutations_nul_v9.py`) : au commit `e58cfec`, 34 mutations, 34 tuées (directeur ; contre-lecteur R2
n° 1, L11) ; avant la correction, 33 sur 33 (L7). **Au brouillon 4 : 43 mutations, 43 tuées pour la raison attendue**, témoin
26 essais sans échec avant et après (L12) : les 34 précédentes, les mutations G1 à G5 de la contre-lecture (mode décisif :
`--lignes` et répétitions acceptés, cas sain toujours refusé, durée transmise plafonnée à 8 h ; monotonie par la seule
richesse), L1 et L2 (ordre des issues), C5 (valeur du membre remplacée par la meilleure valeur atteinte + 10⁻³) et « description
publique : choix rangés parmi les trous » — fragments de G1 à G5, L1, L2 et C5 repris à l'identique du script du contre-lecteur.
À rejouer sur l'arbre scellé.

## 10. Lectures préalables déclarées

Toutes à graine exploratoire (< 2⁶⁴), aucune sur l'entropie décisive (inexistante avant scellement). « Bloc-notes » =
`/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/nul-v9/` (hors du dépôt, non durable). Heures UTC
du 2 novembre 2026. Code joué : `pole/nul_v9.py` `8cb44adf…aebc655` pour L2 à L7 (lu dans les manifestes de L2, L3, L6) ;
`demonstrations/banc_tricheurs_v9.py` `bf59c9ce…4c38656` pour L2 et L3, `c7ab5470…fcf466` (la version du commit) pour L6 et L7 ;
entre les deux, seuls la constante `PREDICTIONS` et le calcul de `lecture.predictions` ont changé (aucun effet sur les décisions,
les issues ni les audits).

| # | quand | quoi | entropie | vu | sortie et empreinte |
|---|---|---|---|---|---|
| L1 | 17:40 à 18:00 | prototypes du calcul par morceaux (espérance-maximisation par lots, puis points intérieurs) et essais rapides v8 contre v9 sur 6 tirages des mondes W2, seuil et loi neuve | graines fixes 3 à 7, 100 à 105 | W2 et seuil : promus sous v8 (log W 11 à 56), refusés sous v9 (log W ≤ 0) ; loi neuve promue sous les deux (une sur six refusée sous v9 : log W 1,8) ; espérance-maximisation trop lente au bord (écarts résiduels jusqu'à 1,6 nat), d'où les points intérieurs ; réglage des paliers : écart ≤ 4·10⁻⁴ nat, jamais du côté imprudent | bloc-notes `proto/` et `essais-rapides/` (empreintes au rapport, section 9) |
| L2 | 18:06 | banc v9, toutes les lignes, 2 répétitions (fumée) | 11 | harnais de bout en bout, 17,5 s ; issue « non concluant (banc sans dents) » (2 répétitions : rien n'est tenu) | `fumee-1/banc-tricheurs-v9.json` `0e04a451…6db8` ; manifeste `053e80ee…db8` |
| L3 | 18:07 à 18:13 | banc v9, 15 lignes (M01, M02, M07, 5 de puissance, 7 mesurées), 100 répétitions | 20261102 | M01 0/100 (v8 apparié 99), M02 0/100 (96), M07 0/100 (60) ; puissance v9/v8 : fille neuve 96/100, fraîche neuve 94/94, I01 87/92, I02 41/52, F03 72/75 ; mesurées v9 (v8) : T07 1 (3), T12b 77 (84), H01 89 (97), H02 21 (96), H03 90 (93), H04 26 (98), H05 10 (100) ; aucun audit ; 377,8 s | `blanc-L2-puissance-mesures/banc-tricheurs-v9.json` `dda51da3…8101` ; manifeste `ef14fe6c…2fe4` |
| L4 | 18:16 à 18:18 | décalage du dénominateur Δ = log W(v8) − log W(v9) sur les mêmes issues, 40 répétitions × 7 lignes | 777 | Δ final médian : T17s 0,35 ; T04 2,47 ; fraîche neuve 0,00 ; I01 1,76 ; I02 0,66 ; F03 0,07 ; fille neuve 18,75 nats ; durée moyenne par répétition (v9 et v8) 0,24 à 0,54 s | `calculs/decalage_v1.json` `3319a840…ff9f` ; script `a344f89d…5a5` |
| L5 | 18:15 et 18:27 | tables de la lecture gelée (Holm, artefact, perte appariée ; puissance des lignes fatales aux seuils de Holm à 18 lignes) | — | section 6 | `calculs/tables_v1.txt` `10ac2c88…e7e` ; `calculs/tables_v2.txt` `69fa85bb…0895` |
| L6 | 18:20 à 18:22 | banc v9, 16 lignes (11 fatales du v8 et M03 à M06 sous v9, T01\|v1), 30 répétitions | 20261103 | les 15 lignes fatales 0/30 sous v9, log W max ≤ 0 partout (classe linéaire −0,41 à −1,37 ; T05s −0,027 ; T09g −0,030 ; M03 à M06 −0,000 à −0,075) ; sous le v8 apparié : M03 29/30, M04 28/30, M05 16/30, M06 29/30, les 11 lignes du v8 0/30 ; T01\|v1 13/30 ; aucun audit ; 69,1 s (somme des lignes 133,4 s, soit ≈ 0,3 s par répétition) | `blanc-L6-fatales/banc-tricheurs-v9.json` `b24a4faf…78b8` ; manifeste `0cca8177…a6f` |
| L7 | 18:14 à 18:25 | essais `essais/test_nul_v9.py` (32 réussis, 32 sous-essais) et banc de mutations (33/33), trois passages ; le dernier sur le code du commit | 20261102 (essais) | section 9 | dernier passage `essais-et-mutations-final-sortie.txt` `ba65ab5b…7940` ; précédent `essais-et-mutations-L5b-sortie.txt` `f8653453…bbf` |
| L8 | 18:33 à 18:35 | passage indépendant des essais et des mutations sur le code du commit (message du commit `5e352ec`) | — | 32 essais réussis ; 33 mutations tuées sur 33 | message du commit (non relu sur une sortie) |
| L9 | 18:45 à 18:55 (repreneur, brouillon 2) | lecture en entier du rapport de rédaction, du brouillon 1, de `pole/nul_v9.py`, du banc v9, des essais et du banc de mutations ; lignes 60 à 260 du banc v8 ; recalcul des empreintes (six fichiers v9, 14 fichiers gelés) sur disque et au commit ; ligne 26 du texte scellé de l'attaque ; aucun essai, aucun banc, aucune course relancés | — | en-tête, section 1 bis, section 12 ; la durée gelée du banc (8 h) contredit la décision de Lazar (48 h) : annexe B | — |
| L10 | 19:14 à 19:20 (repreneur, brouillon 3) | diff du commit `e58cfec` sur le banc, les essais et les mutations du v9 ; empreintes des 14 fichiers gelés sur l'arbre (égal au commit) ; texte du brouillon 3 lu par `lire_preenregistrement` du banc corrigé, scellement simulé dans un dossier temporaire hors du dépôt (`verif_b3_validation.py`, bloc-notes `…/scratchpad/attaque-v4/verif-b3-validation/`) ; ni essai, ni banc de mutations, ni course | accepté, 14 fichiers gelés égaux à `FICHIERS_GELES` ; section 0 bis |

Les prédictions de la section 4 ont été écrites après L1 à L5 et en tiennent compte (déclaré). La marge (a) est la règle du v8,
écrite avant toute course du v9 ; elle a été retenue pour le v9 le 2 novembre, après L3 et la recommandation (a) du brouillon
1, dont l'annexe A donnait l'issue prédite de chaque option : l'option retenue est celle dont l'issue prédite est « puissance
perdue », non celle qui promettait « confirmé » (R3 : la marge est le prix acceptable, non l'issue visée).

| L11 | 19:06 à 19:36 (contre-lecteur R2 n° 1) | essais et banc de mutations rejoués sur le code du commit `e58cfec` ; 12 mutations du contre-lecteur, en mémoire, contre toute la suite ; sondes : domination sur 48 mondes neufs, égalités de z, référence scipy, optimisation tronquée (30 mondes de l'essai de domination) ; fermeture dynamique (une répétition de M01, M06 et T01\|v1 par `jouer_ligne`, en mémoire, taux non lus) ; tables de la section 6 recalculées ; aucune course par `principal` | essais 20261102 ; sondes : graines 910000 à 930011 et celles de l'essai de domination ; fermeture 5 | 33 essais réussis ; 34 mutations tuées sur 34 ; 8 des 12 mutations du contre-lecteur survivent (B1, I5, I6) ; aucun écart de domination ; tables identiques | `prereg/contre-lecture-preenregistrement-validation-nul-v9-v1.md`, sections 0, 1 et 5 |
| L12 | 19:46 à 20:10 (repreneur, brouillon 4) | essais neufs (B1, I5, I6, I2) et mutations neuves (G1 à G5, L1, L2, C5, description) ; `pole/nul_v9.py` modifié pour sa description seulement, vérifié par comparaison des arbres syntaxiques avant et après (seuls changent `PHRASES_MEMBRES_V9`, `NON_COUVERT_V9`, trois constantes neuves de description, `description_publique` et `description`) ; essais et banc de mutations rejoués sur le code final ; texte lu par `lire_preenregistrement` du banc (scellement simulé hors du dépôt) ; aucune course par `principal` hors des bouchons des essais | essais 20261102 ; mutations : celles des essais | 37 essais réussis, 35 sous-essais ; 43 mutations tuées sur 43 pour la raison attendue ; texte accepté (14 fichiers gelés) | bloc-notes `…/scratchpad/validation-b4/` (empreintes à la remise) |

## 11. Portée

Mondes synthétiques des bancs (K = 3 issues, 2 traits gaussiens, 2 sous-populations ; 200 tirages) ; deux lois d'archive
(fiches sans parent) ou quatre (filles) ; rien sur la banque réelle, la multiplicité entre fiches (règle e-BH), les autres
espaces. Classe éprouvée : section 2 ; les lignes H01 à H05 mesurent, sans seuil, ce que la description
publique dit hors du nul v9 (des trous pour H01, H02, H03 et H05 ; pour H04, une dépendance aveugle nouvelle, promouvable par
le choix de la section 2) ; elles ne sont pas des lignes fatales et leur taux ne dit rien de la validité du v9 sur sa classe. Rien sur un
proposeur qui lit le juge et reçoit ses verdicts : c'est l'objet de l'attaque v4.

## 12. Empreintes du code

Les 14 fichiers que la course importe (`FICHIERS_GELES`). Le banc vérifie chaque ligne du bloc. Recalcul (depuis
`orchestrator/`) : `sha256sum demonstrations/banc_tricheurs_v7.py demonstrations/banc_tricheurs_v8.py demonstrations/banc_tricheurs_v9.py pole/__init__.py pole/caviardage.py pole/controles_pari.py pole/cycle.py pole/fiche.py pole/memoire.py pole/nul_filles_v2.py pole/nul_v8.py pole/nul_v9.py pole/outils.py pole/selection_pari.py`.
Valeurs du 2 novembre 2026, à la remise du brouillon 4 (heure dans la section 10, L12), sur l'arbre de travail. Les 12
dépendances (tous les fichiers sauf les deux fichiers v9) sont **identiques** au bloc du préenregistrement scellé du v8
(`prereg/preenregistrement-validation-nul-v8-v2.md`, lignes 365 à 376, comparées ligne pour ligne ; revérifiées par le
contre-lecteur R2 n° 1 au commit `e58cfec`). `demonstrations/banc_tricheurs_v9.py` est le banc corrigé du commit `e58cfec`
(l'empreinte d'avant la correction, `c7ab5470…fcf466`, n'est pas gelée). **`pole/nul_v9.py` a changé au brouillon 4** (description
publique seulement, aucun calcul : section 0 ter, point 5) : sa ligne porte la nouvelle empreinte ; l'ancienne (`8cb44adf…aebc655`)
n'est plus gelée. Les essais de B1, I5 et I6 ne touchent aucun des 14 fichiers. Le directeur recommite, recalcule le bloc au
scellement et refuse tout écart.

<!-- empreintes-du-code : début -->
```
ef016d250b7b503f705dc95919719c68c8f968534fd901df7364a6062d67cf12  demonstrations/banc_tricheurs_v7.py
0be47e4b5916a98499faf9c40d65369b41e3a5463d7ab444ed18ba18bba08c03  demonstrations/banc_tricheurs_v8.py
7e4bff5995df2a7d62a4f5a2f5f9176da614e657a55b05183325fa2fc6e24e44  demonstrations/banc_tricheurs_v9.py
f7341b965ddba1e0fb21b44d9068f59650d5c77e3175f2b6b7ca879219fa5c9b  pole/__init__.py
78abfd4731218e20538418608ebebaca3364206ef6d014b7a34829a3c9fd7e85  pole/caviardage.py
fabc3d0873e6db639f2578eb00ef0035d7831a3b2a1457ffce1d91aa7a364e1c  pole/controles_pari.py
798f039042e3ee1f18df5c566f5a0ddee5dac5c98225c8ce621e267174c8ee18  pole/cycle.py
ec018f147196222268d91358ce2038bb35bf76069e6bf8928dea9e3db59d1074  pole/fiche.py
71f1d08613bf335aa9ef7aa1397f20aa24553fea2f1b858c10b265d62f8ab79e  pole/memoire.py
0ed9b4adbcddc4ad77a1c97d5cbd5706f14926e9c47fe96ce2bab3221a138910  pole/nul_filles_v2.py
cc452aafd17121a7c0ec42829eea47063ffee1f6cdf7f642e264d528f976b888  pole/nul_v8.py
7ae450df2482246122bf9fbcf0fa5ef30b4a7e4c6f0d09531e83af048e46ee95  pole/nul_v9.py
966d9553026aad1eb7d97fa677334f1b59f22a39f15eef95134d63bc47634444  pole/outils.py
359928110d757cd54cc0d2773910c7360895b68cac5d17e0e4b4e9933ef306bc  pole/selection_pari.py
```
<!-- empreintes-du-code : fin -->

Non gelés ici : `essais/test_nul_v9.py`, `essais/mutations_nul_v9.py` (rejoués après la correction et sur l'arbre scellé avant
la course).

## 13. Contre-lecture (R2) — faite (n° 1 : `prereg/contre-lecture-preenregistrement-validation-nul-v9-v1.md`)

Fichiers à donner au contre-lecteur neuf : ce brouillon ; le brouillon 1 (pour la section 0) ; `prereg/rapport-redaction-nul-v9.md` ;
`pole/nul_v9.py` ; `demonstrations/banc_tricheurs_v9.py` (corrigé selon l'annexe B, avec le diff de la correction) ;
`essais/test_nul_v9.py` ; `essais/mutations_nul_v9.py` ; pour comparaison `pole/nul_v8.py`, `pole/nul_filles_v2.py` (fonctions
`_lineaire`, `valeurs_ajustees`, `evaluer_v2`), `demonstrations/banc_tricheurs_v8.py` (lignes 98 à 127 pour la correction 2), le diff du commit `e58cfec` sur les trois
fichiers v9,
`prereg/preenregistrement-validation-nul-v8-v2.md`, `prereg/preenregistrement-attaque-goodhart-v2-v1.md` (ligne 26). Les dix
points à vérifier en premier sont au rapport de rédaction (section 11) ; s'y ajoutent : (11) la section 1 bis (les deux
corrections au brief, contre la preuve et contre le banc v8) ; (12) la correction de la durée (annexe B : une constante, la
docstring, un essai neuf ; rien d'autre ne change dans le banc) ; (13) le bloc de la section 12 contre `FICHIERS_GELES` et
contre le bloc du v8.

## 14. Procédure avant la course

1. **Correction du banc (annexe B) : faite** (directeur, commit `e58cfec` ; section 0 bis) ; empreinte du banc corrigé portée à la
   section 12. **Essais de B1, I5 et I6 de la contre-lecture : faits au brouillon 4** (`test_mode_decisif_cas_sain_et_refus`,
   sous-essai « monotonie-richesse » de `test_banc_reduit_et_liste_d_arret`, `test_ordre_des_issues`,
   `test_valeur_certifiee_sous_optimisation_tronquee`) avec leurs mutations (G1 à G5, L1, L2, C5), toutes tuées pour la raison
   attendue ; description publique (I2) écrite. Essais et banc de mutations rejoués sur l'arbre scellé :
   `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_nul_v9.py` ;
   `nice -n 10 python3 -I -B essais/mutations_nul_v9.py`.
2. **Confirmation du sens de « rien au-delà de l'archive »** par Lazar (section 2 ; proposition : bruit commun). La course
   n'en dépend pas et peut avoir lieu sans réponse ; la revendication publique et l'usage en production attendent la réponse
   explicite de Lazar (nœud « revendication », sans défaut) ; une réponse contraire arrête ce texte (nul v10).
3. Contre-lecture neuve (R2) : **faite** (n° 1, sur le brouillon 2) ; couples appliqués au brouillon 4 (section 0 ter) ;
   vérification courte des changements 3 → 4 recommandée avant le scellement (essais et mutations neufs, et surtout le changement
   de `pole/nul_v9.py`, description seulement, que la contre-lecture n'a pas vu) ; version renommée
   `prereg/preenregistrement-validation-nul-v9-vN.md` (N ≥ 1).
4. Bloc d'empreintes recalculé sur le code final (14 fichiers) ; égalité avec `FICHIERS_GELES` vérifiée.
5. Scellement par le directeur (compagnon `.sha256`) ; commit et poussée du texte, du code, des essais, des mutations et du
   rapport **avant** la course ; identifiant de commit noté.
6. Sur l'arbre scellé : essais et banc de mutations ; puis la commande de la section 5 (durée gelée 48 h par défaut).
7. Sortie scellée avant lecture ; audit écrit ; verdict par un lecteur neuf (R13) ; soumis à Lazar.
8. Ensuite seulement, l'attaque v4 contre le juge v9 (son texte, son GO : GO-2026-11-02-22).

## Annexe A. Marge de perte de puissance — décision consignée

**Décision (défaut de Lazar sous 48 heures, porté le 2 novembre 2026) : option (a), 0,05 sur chacune des 5 lignes de
puissance.** Marqueur du brouillon 1 levé. Les options écartées restent comme trace (probabilités d'issue sous les pertes de L3
prises pour vraies ; section 6) :

| option | marge | avantage | inconvénient | issue prédite |
|---|---|---|---|---|
| **(a), retenue** | 0,05 sur les 5 lignes (règle du v8) | aucune marge choisie après une course à blanc ; continuité avec le v8 | l'expérience ne tranche plus que la validité : « puissance perdue » presque sûre (I02) | « puissance perdue » |
| (b) | 0,05 sur fille neuve, fraîche neuve, I01 ; 0,15 sur I02, F03 | prix distinct pour les effets faibles | marges posées après L3 ; I01 (0,05) et fille neuve (0,04) près de leur marge | le plus souvent « non concluant (précision insuffisante) » |
| (c) | 0,10 sur les 5 lignes | une seule valeur | I02 (≈ 0,11) au bord : issue au hasard | « non concluant » ou « puissance perdue » |
| (d) | 0,10 sur les lignes fortes, 0,20 sur les faibles | « confirmé » probable | marges taillées sur L3 (R3 : viser un signe) | « confirmé » |

Lecture de la décision avec les mots de Lazar (« je ne veux pas de résultats non concluants par défaut de conception, de
plafond ») : (a) donne une issue conclusive attendue (« puissance perdue »), écrite d'avance, qui renvoie à Lazar la seule
question qui lui appartient — accepter ou non le prix publié ; (b) et (c) exposaient précisément à un « non concluant » par
choix de marge. Le code du banc porte (a) (`MARGE_PERTE = 0.05`) ; rien à changer.

## Annexe B. Correction du banc v9 (faite au commit `e58cfec`) et marqueur levé — trace

**Pourquoi** : la décision de Lazar gèle 48 heures ; le banc du commit gèle 8 heures et refuse toute autre valeur en mode
décisif. Sans correction, la commande de la section 5 lancerait une course arrêtée à 8 heures, et la même commande avec
`--duree-max-s 172800` serait refusée (code 2, `EcartAuPlan`). Le repreneur du brouillon 2 n'avait pas le droit de modifier un fichier existant.

**Correction** (fichier `demonstrations/banc_tricheurs_v9.py`, au commit `5e352ec`, sha256 `c7ab5470…fcf466`) :
- ligne 84 : `DUREE_MAX_S = 8 * 3600.0` → `DUREE_MAX_S = 48 * 3600.0` (le commentaire peut dire « garde contre une boucle
  folle ; durée attendue 2 à 5 h ») ;
- ligne 40 (docstring) : « une autre durée maximale que 8 heures » → « une autre durée maximale que 48 heures » ;
- ligne 47 (docstring, usage) : `[--duree-max-s 28800]` → `[--duree-max-s 172800]` ;
- rien d'autre : la garde (ligne 524) compare déjà à `DUREE_MAX_S`, le message (ligne 526) l'imprime, `jouer_ligne` (lignes 285
  et 286) arrête sur la valeur passée.

**Essai proposé par le brouillon 2** (R5 ; la garde de durée n'avait alors aucun essai en mode décisif ; fait au brouillon 4, `test_mode_decisif_cas_sain_et_refus`) : dans
`GrainesEtPreenregistrement`, avec un texte d'essai scellé au bon nom (comme `test_cas_sain_et_artefacts_preenregistrement`)
et `jouer_tout` remplacé par un bouchon : cas sain — sans `--duree-max-s`, le banc passe les gardes et appelle le bouchon
(durée transmise = 172 800 s) ; artefact — `--duree-max-s 28800` → code 2, bouchon jamais appelé. Une mutation associée
(« durée gelée non vérifiée en mode décisif », fragment `or args.duree_max_s != DUREE_MAX_S` retiré de `principal`) doit être
tuée par l'artefact.

**Effets** : l'empreinte du banc change (le jeton de la section 12 prend la nouvelle) ; les essais et les mutations sont rejoués ;
aucune prédiction, aucun seuil, aucune graine ne change (la graine est l'empreinte du texte scellé, pas du banc).

**Marqueur levé** : le jeton EMPREINTE_DU_BANC_CORRIGE (entre doubles chevrons) du brouillon 2 porte l'empreinte du banc corrigé
au commit `e58cfec` (`7e4bff59…6e24e44`). Les marqueurs du brouillon 1 sont levés (marge : annexe A). Écart à cette annexe, dit
au brouillon 3 et relevé par la contre-lecture (B1) : l'essai livré au commit `e58cfec` (`test_duree_du_mode_decisif_48_h`) jouait
l'artefact (28 800 s → code 2, texte jamais lu) et vérifiait la constante, pas le cas sain demandé ; **levé au brouillon 4** par
`test_mode_decisif_cas_sain_et_refus` (durée par défaut → la course démarre, durée transmise 172 800 s à chacune des 31 lignes),
et la mutation G4 (durée transmise plafonnée à 8 h) est tuée.
