Non scellable en l'état — bloquant B1 (règle R5 : le mode décisif du banc v9 n'a aucun cas sain éprouvé, `--lignes` et le nombre de répétitions n'y sont refusés par aucun essai, la durée transmise à la course n'est pas vérifiée, l'arrêt de monotonie « par la seule richesse » n'a pas d'artefact : cinq mutations du code gelé survivent à toute la suite) ; B1 se lève par des essais seulement (aucun fichier gelé touché, bloc de la section 12 inchangé) ; puis scellable après les 38 couples du JSON.

# Contre-lecture R2 n° 1 — préenregistrement de la validation du nul v9 (brouillon 2) et code au commit `e58cfec`

2 novembre 2026, de 19:06 à 19:45 UTC environ (heures de `date -u`). Contre-lecteur neuf : je n'ai écrit ni le nul v8, ni le nul
v9, ni les bancs v8 et v9, ni leurs essais, ni le rapport de rédaction, ni les brouillons 1 et 2. Lecture seule du dépôt public ;
aucun commit, aucun `.sha256`, aucun fichier existant modifié, rien sous `donnees/`, aucun `git fetch`, aucun réseau ni modèle ;
tout calcul sous `nice -n 10 python3 -I -B`. Deux fichiers neufs dans le dépôt : celui-ci et
`prereg/couples-contre-lecture-validation-nul-v9-v1.json`. Le reste (sondes, sorties, texte du brouillon 2 avec les couples
appliqués) est dans le bloc-notes `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/contre-lecture-nul-v9/`
(le même bloc-notes de session que celui du concepteur, dont je n'ai que lu les sorties sous `nul-v9/`). Dépôt à la tête `e58cfec`
au début, `08b1f17` à la fin, sans changement des fichiers lus (section 8).

**Verdict.**
1. **La preuve tient**, refaite pas à pas (section 1) : chaque membre par morceaux domine la vraisemblance de toute loi de sa
   famille à chaque instant lu ; le certificat de Frank-Wolfe est une borne valide en tout point du domaine, sans admissibilité
   ni convergence ; le sup sur s ∈ ℝ est un maximum sur au plus t + 1 coupes ; le maximum (et non un mélange a priori) au
   dénominateur garde Ville au niveau α quel que soit le nombre de membres ; W(v9) ≤ W(v8) trajectoire par trajectoire. Cas
   limites sains (égalités de z, seuils hors de l'étendue, morceaux vides) ; une limite non dite, hors du banc (traits non
   finis). Mes sondes neuves ne trouvent aucun écart ; les tables de la section 6 se recalculent à l'identique ; la graine
   décisive est neuve et disjointe des graines exploratoires.
2. **Bloquant B1 (R5)** : quatre gardes du mode décisif et un disjoint de l'arrêt de monotonie ne sont éprouvés par aucun essai
   (mutations G1 à G5 du contre-lecteur, toutes survivantes), alors que la section 9 l'affirme ; l'annexe B demandait le cas sain
   de la durée, l'essai livré ne vérifie que la constante.
3. **Importants** : I1 la lecture de « puissance perdue », l'issue attendue, n'exige pas que la validité soit établie ; I2 le
   choix du bruit commun est mal reporté (H04 et T12b comptés comme « fausses promotions », `NON_COUVERT_V9` range le choix
   parmi les trous, poids commun du bruit non dit) ; I3 un sens de revendication ne prend pas effet par défaut ; I4 la règle
   « un scellement, une course décisive » est tronquée et les arrêts déterministes n'ont pas de lecture ; I5 l'ordre des issues
   n'est éprouvé par aucun essai ; I6 la valeur certifiée sous optimisation tronquée n'est éprouvée par aucun essai ; I7
   en-tête, statut, sections 9, 12, 14 et annexe B périmés depuis `e58cfec`. Mineurs M1 à M10. 38 couples (section 7).

## 0. Fichiers lus, empreintes, ce qui a été rejoué

| pièce (depuis `orchestrator/`) | vérification |
|---|---|
| `prereg/preenregistrement-validation-nul-v9-brouillon2.md` | `0a906f8c43099670f1c6694d7ec67b847ff9bc28687d0906e8419e3e23d8bcb7`, 511 lignes, égal à `git show e58cfec:` ; lu en entier |
| `prereg/rapport-redaction-nul-v9.md` | `bbf9b38f…233089`, égal au commit et à l'en-tête du brouillon ; lu en entier |
| `pole/nul_v9.py` | `8cb44adf…aebc655`, identique à `5e352ec` et `e58cfec` ; lu en entier |
| `demonstrations/banc_tricheurs_v9.py` | `7e4bff59…6e24e44` au commit `e58cfec` et sur disque (= la valeur donnée pour le jeton) ; diff `5e352ec..e58cfec` : lignes 40, 47 et 84 seulement (durée) ; lu en entier |
| `essais/test_nul_v9.py` | `9eb966ad…a67b21` (diff : `test_duree_du_mode_decisif_48_h`, lignes 601 à 613) ; lu en entier |
| `essais/mutations_nul_v9.py` | `9cb305e4…252d16` (diff : une mutation, lignes 97 à 99) ; lu en entier |
| ce qu'importe le banc | `pole/nul_v8.py`, `pole/nul_filles_v2.py`, `demonstrations/banc_tricheurs_v8.py` lus en entier ; `pole/selection_pari.py` lignes 30 à 209 et 270 à 698 ; `demonstrations/banc_tricheurs_v7.py` lignes 60 à 160 ; `pole/controles_pari.py` (`_dirichlet`, `_fixe`), `pole/outils.py` (scellement), `pole/cycle.py` (`instants_reguliers`) |
| bloc de la section 12 | 13 empreintes écrites et valeur du jeton égales aux 14 fichiers sur disque et à `git show e58cfec:` (0 écart) ; les 12 dépendances égales au bloc du v8 (`prereg/preenregistrement-validation-nul-v8-v2.md`, lignes 365 à 376) |
| textes cités | `prereg/preenregistrement-validation-nul-v8-v2.md` lignes 119 à 135 et 360 à 378 ; `prereg/preenregistrement-attaque-goodhart-v2-v1.md` ligne 26 (« 27 tricheurs **scriptés** »), `fc81d015…`, égal à son compagnon ; empreintes citées en section 1 du brouillon (`3c9de8b8…`, `2c0465be…`, `0be47e4b…`) exactes |
| sorties exploratoires du concepteur (bloc-notes, `nul-v9/`) | `fumee-1`, `blanc-L2-puissance-mesures`, `blanc-L6-fatales`, `calculs/*`, `essais-et-mutations-*.txt` : empreintes égales à celles des sections 9 et 10 du brouillon et du rapport ; L3 et L6 relus (comptes, dominants, durées) pour vérifier les repères de la section 10 |

Rejoué ou calculé (sorties dans le bloc-notes, empreintes en section 9) :
- **Essais** : `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_nul_v9.py` : **33 réussis, 32 sous-essais**,
  39,9 s, 19:11:17 à 19:11:58 UTC, code 0.
- **Banc de mutations** : `nice -n 10 python3 -I -B essais/mutations_nul_v9.py --raisons` : **34 mutations, 34 tuées pour la
  raison attendue**, témoin 22 essais sans échec avant et après, 19:14:31 à 19:17:56 UTC, code 0.
- **Tables de la section 6** (`tables_contre_lecture_v1.py` : fonctions du banc v8, recoupées par `scipy.stats.binom`) :
  identiques (section 2).
- **Mes mutations** (`sondes_mutations_contre_lecture_v1.py`, en mémoire, contre les 33 essais, 19:19:42 à 19:35:57 UTC) :
  section 5.
- **Mes sondes** : `sonde_domination_v1.py` (19:23:41 à 19:24:52 UTC ; section 1.6) ; la sonde de troncature (fin de
  `sondes_mutations_contre_lecture_v1.py`) ; `fermeture_dynamique_v1.py` (une répétition de M01, M06 et T01|v1 par
  `jouer_ligne`, en mémoire, graine exploratoire 5, taux non lus) : modules du dépôt chargés pendant la course = les 14 de
  `FICHIERS_GELES`, ni plus ni moins (au chargement du banc et après la course).
- Python 3.13.18, numpy 2.5.3, scipy 1.18.1 ; processus démarrés par `fork`. Aucun dossier `resultats/banc-tricheurs-v9*`,
  aucun compagnon `.sha256` d'un texte du v9 (vérifié à 19:33 UTC).

## 1. La preuve, refaite (point 1 de la demande)

Notations du rapport (section 3) : pour une coupe c à P morceaux, x = (a¹, …, a^P, r), f_c(x) = Σ_i actif_i·log m_i(x),
m_i = Σ_p M[p,i]·(L_i·a^p) + r_{y_i} sur les instances de la coupe, m_i = 1 ailleurs ; 𝒫 = {x ≥ 0 : Σ_j a^p_j + Σ_k r_k = 1 ∀p}.

**1.1 Sommets.** Soit ρ = Σ_k r_k. Si ρ < 1, x = (1 − ρ)·(a¹/(1 − ρ), …, a^P/(1 − ρ), 0) + Σ_k r_k·(0, …, 0, e_k), et le premier point
est dans le produit de simplexes Δ_J^P, enveloppe convexe des J^P points « une loi connue par morceau, r = 0 » ; si ρ = 1, a = 0 et
x = Σ_k r_k·(0, …, e_k). Donc 𝒫 = conv{J^P sommets produits ; K sommets « r = δ_k, a = 0 »}, et
max_{v ∈ 𝒫} ∇f·v = max(Σ_p max_j g^p_j ; max_k g^r_k) : c'est exactement V (`pole/nul_v9.py:209-212` et `:288-299`). Les points
« loi connue sur un morceau, bruit seul sur un autre » ne sont pas dans 𝒫 : c'est le bruit commun (contrainte `B`,
`pole/nul_v9.py:238-241`, même bloc r dans chaque ligne ; d'où Σ_j a^p_j = 1 − ρ sur **tous** les morceaux : même loi aveugle
**et même poids**, voir I2).

**1.2 Borne en tout point.** f_c est concave sur le convexe {x : c_i·x > 0}. Pour x_P ∈ 𝒫 et tout x du domaine :
f(x_P) ≤ f(x) + ∇f(x)·(x_P − x) ≤ f(x) + V(x) − ∇f(x)·x, et ∇f(x)·x = Σ_i actif_i·(c_i·x)/(c_i·x) = t_c pour **tout** x du domaine,
dans 𝒫 ou non (homogénéité) : ni admissibilité ni convergence ne sont requises (la dérive des itérés hors de B·x = 1 ne coûte
rien). `max(0, V − t_c)` ne fait qu'élargir la borne (V ≥ t_c dès que x ∈ 𝒫) ; `min(0, ·)` est valide car m_i ≤ Σ_j a^p_j + Σ_k r_k
= 1 sur 𝒫 (L ≤ 1, Y indicatrice). Masque : une instance hors de la coupe a m = 1, inv = 0 ; elle ne compte ni dans le gradient
ni dans t_c = `actif.sum(axis=0)` (`pole/nul_v9.py:196`, `:207`, `:213`, `:300`). Chaque borne stockée est le minimum de bornes
valides (départ strictement positif, point sans coupure s'il est admissible, chaque itéré, point final) ; une borne non finie
lève `CalculMorceauxImpossible` (`:351-352`) ; une NaN s'y propage et lève aussi. La valeur rendue est le maximum, sur **toutes**
les coupes du groupe, de leur borne (`:443`) ; une coupe élaguée a une borne sous la meilleure valeur atteinte d'une autre coupe,
elle-même sous la borne de celle-ci : elle ne porte jamais le maximum. Élagage et fin de groupe ne coûtent que de la puissance.

**1.3 Tout seuil réel.** f ne dépend de s que par {i < t : z_ij ≤ s}. Pour s réel, c'est ∅ (s < min) ou {z_ij ≤ u}, u = max des
z_ij ≤ s : une des coupes de `_coupes` (seuils = {−∞} ∪ valeurs distinctes de z[:t], `pole/nul_v9.py:397-399`), donc au plus
t + 1 coupes. Cas limites : égalités de z groupées, aucun seuil réel ne les sépare (une condition « ≥ s » réalise aussi une coupe
de la liste) ; seuil du monde au-delà de l'étendue observée : tout d'un côté, réalisé par −∞ ou par u = max ; morceau vide :
gradient nul sur ses poids, terme de sommet 0 ; membre sans instance : impossible (t ≥ 1, `InstantsInvalides`), et moins de deux
lois connues → aucun membre (avec une seule loi, la famille est le membre linéaire du v8). Remarque sans effet : la coupe −∞ est
redondante dès que deux valeurs distinctes existent (toute famille à deux morceaux contient la famille à un morceau). **Limite
non dite** : un trait non fini (NaN) va dans le morceau haut pour `_coupes` (z ≤ s faux) et dans la branche « sinon » pour
`selection_pari._condition` (z > s faux, `pole/selection_pari.py:106`) ; la partition du monde peut alors n'être réalisée par
aucune coupe. Impossible dans le banc (`tirer_instances` : traits gaussiens arrondis) ; à dire (M6, couple T10).

**1.4 Domination, Ville.** Pour P ∈ F, x_P ∈ 𝒫 pour la coupe que réalise P, et f(x_P) = log P(y_1..t | x_1..t) aux arrondis près
(le monde passe par `proba`, même plancher et même normalisation que les tables L) ; donc v_F(t) ≥ log P(y_1..t | x_1..t).
D_t = max_F v_F(t) ≥ v_{F*}(t) ≥ log P ⇒ W_t ≤ Λ_t = q(y_1..t)/P(y_1..t). Λ est une martingale positive d'espérance 1 sous P dans
l'ordre du plan : monde sans mémoire (issues indépendantes sachant les instances, l'ordre secret étant une permutation
indépendante des issues), q prévisible (gelée avant les tirages ; pari à fraction : mélange à poids fixés de lois prévisibles).
Ville : P(∃ t lu : W_t ≥ 1/α) ≤ α, pour tout monde de tout membre, quel que soit le nombre de membres. La correction 1 de la
section 1 bis est juste : avec D̃_t = log Σ_F π_F·e^{v_F(t)}, seul D̃_t ≥ log π_{F*} + log P tient, d'où α/π_{F*} ; et W_max ≤ W̃
trajectoire par trajectoire. Dans le banc, la fiche des lignes « par construction » **est** le monde (pari plein : aucun
engagement n'y porte `fractions`, `pole/selection_pari.py:385-387`) : log W ≤ 0 y est déterministe, et A4 (log W > 10⁻⁶) ne
peut venir que d'un défaut.

**1.5 Monotonie.** Les membres du v8 sont calculés par le même code, sur les mêmes issues, dans l'évaluation v9 et dans le v8
apparié (`calibrer` ne touche que les `melange_lois` marqués, membre par membre) : D_t(v9) = max(D_t(v8) ; morceaux) ≥ D_t(v8) en
flottants ; l'arrondi à 6 décimales est monotone ; les enveloppes du v9 contiennent celles du v8, donc gain(v9) ≤ gain(v8) et
promue(v9) ⇒ promue(v8). La garde `verifier_monotonie` (`demonstrations/banc_tricheurs_v9.py:269-274`) ne peut se déclencher
que sur un défaut du code — d'où I4 (arrêt déterministe).

**1.6 Épreuves du contre-lecteur** (`sonde_domination_v1.py`, graines neuves) :
- **48 mondes neufs** (graines 910000 à 910047) : fiches (2 lois connues) et filles (4 : A, B, S1, S2), 2 ou 3 sous-populations,
  sommets (une loi connue par morceau), mélanges propres aux morceaux, bruit commun (ε jusqu'à 0,6), seuils au milieu, aux
  bords et hors de l'étendue (± 9) ; instants 5, 10, 25, 50, 100, 200 : **288 instants, 0 échec**, pire (vraisemblance − valeur)
  = −6,0·10⁻¹⁴.
- **Égalités** (traits arrondis à 0,1, seuil égal à une valeur observée, 12 tirages) : 36 instants, 0 échec ; nombre de coupes =
  valeurs distinctes + 1.
- **Référence scipy** (SLSQP, 6 départs, 8 tirages neufs, t = 12 à 19, 2 et 4 lois connues) : 24 comparaisons ; valeur ≥
  référence partout (de 7,7·10⁻⁷ au moins) et ≤ référence + 5,3·10⁻⁴.
- **Optimisation tronquée** (les 30 mondes de l'essai de domination, 150 instants) : un palier et un pas, la valeur certifiée
  n'est **jamais** sous la vraisemblance du monde (pire écart −0,15) quand « meilleure valeur atteinte + 10⁻³ » l'est à 83
  instants ; trois pas : 0 contre 58 ; réglages livrés : 0 contre 0. Le certificat porte la validité dès que l'optimiseur
  s'arrête tôt ; aux réglages livrés, l'optimiseur converge — d'où I6.

## 2. Complétude R1, critères gelés, liste d'arrêt, R5 (point 2)

- **R1** : hypothèses (section 3, H1 à H4), prédictions chiffrées et signées (section 4), métriques et seuils (section 6), plan
  d'analyse et règle des graines (section 5), critères de lecture gelés (section 7, `lire_v9`), audits (section 8), liste
  d'arrêt (section 9) : présents. Deux règles sont appliquées par le lecteur du verdict et non par le code (A6, règle de P1b) :
  dites ; la seconde crée une sixième issue que la section 7 ne nomme pas (couple T20).
- **Familles de Holm, ordre, artefacts, marge** : code conforme au texte — 18 fatales (`banc_tricheurs_v9.py:371-374`), 5 pertes à
  la marge 0,05 (`:87`, `:388-395`), 3 artefacts par borne basse de Clopper-Pearson (`:378-387`), ordre des issues (`:441-452`),
  audits A1 à A5 (`:401-424`).
- **Tables recalculées** (`tables_contre_lecture_v1.txt`) : maximum de promotions pour « tenue » (18 rangs) 31, 31, 31, 31, 31, 32,
  32, 32, 32, 32, 33, 33, 33, 34, 34, 35, 36, 38 ; minimum pour « non tenue » 71, 71, 71, 71, 70, 70, 70, 70, 70, 69, 69, 69, 68, 68,
  67, 66, 65, 63 ; artefact : 63 (Clopper-Pearson basse de 62/1 000 : 0,04993 ; de 63 : 0,05083) ; pertes : 34, 34, 35, 36, 38 pour
  « tenue », 68 (rang 1) à 63 (rang 5) pour « non tenue » ; probabilités de la section 6 retrouvées au millième (taux 0,02 :
  0,9925 à 0,9999 ; 0,03 : 0,6197 à 0,9381 ; 0,04 : 0,0812 à 0,4135 ; 0,05 : 0,0022 à 0,0433 ; pertes 0,02 → 0,9987 ; 0,03 → 0,8005 à
  0,9381 ; 0,04 → 0,1887 à 0,4135 ; 0,05 → 0,0093 à 0,0433 ; « non tenue » au rang 1 : 0,06 → 0,1588, 0,08 → 0,9302, 0,10 → 0,9998).
- **R5, garde par garde** (section 9 du brouillon contre les essais réels) : membres, certificat, départ, évaluateur, tricheurs,
  perte appariée, préenregistrement (`lire_preenregistrement` appelée directement), fermeture : cas sain et artefact présents.
  **Manquent** : le cas sain du mode décisif (aucun essai ne fait passer `principal` en mode décisif jusqu'à la course), les
  refus de `--lignes` et des répétitions en mode décisif, la durée effectivement transmise, la monotonie « par la seule
  richesse » (B1) ; l'ordre des issues (I5) ; la valeur certifiée de bout en bout sous optimisation tronquée (I6) ; A2 n'a pas
  d'essai synthétique (M8).
- **Liste d'arrêt** : conforme au code (code 3 : erreur, richesse non finie, monotonie, durée ; code 2 : refus). Ce qui suit un
  arrêt déterministe n'est pas écrit (I4).

## 3. Les prédictions (point 3)

- **Usage licite**, à trois conditions toutes remplies : (i) c'est déclaré (sections 4 et 10 : écrites après L1 à L5, « ne
  décident pas de l'issue ») ; (ii) elles ne décident pas : `lecture.predictions` est calculé à part et l'issue n'en dépend pas
  (`banc_tricheurs_v9.py:425-455`), P7 n'est que rapportée ; (iii) ce qui décide n'a pas été taillé sur L3 : les 31 lignes, force
  de I02 comprise, existaient avant toute lecture informative (L2, fumée de 2 répétitions, 18:06 UTC, même version de banc que
  L3 ; entre L3 et le commit, seuls `PREDICTIONS` et son calcul ont changé), et la marge (a) est la règle du v8. Nuance (M9) :
  (a) a été **retenue pour le v9** après L3, avec l'issue prédite de chaque option sous les yeux (annexe A du brouillon 1) ;
  l'option retenue est celle qui prédit « puissance perdue », non « confirmé » : aucun conflit avec R3, mais la phrase « fixée par
  Lazar avant toute course du v9 » ne le dit pas (couple T29).
- **Portée** : P4 à P6 sont L3 ± deux écarts types environ (100 répétitions) — des épreuves de reproductibilité, non d'une
  théorie ; P7 est presque certaine (perte de I02 ≈ 0,11, « non tenue » dès 68/1 000 : probabilité ≈ 1). Rien à redire tant que
  c'est dit, et c'est dit.
- **Graine décisive** : E = entier de l'empreinte SHA-256 du fichier scellé, calculé par le banc (`banc_tricheurs_v9.py:487-490`),
  refusé sous 2⁶⁴ ; graines exploratoires lues jusqu'ici : 11, 20261102, 20261103, 777 (L4), 20261102 (essais), et les miennes (5 ;
  sondes hors du banc) : toutes < 2⁶⁴. Les flux `SeedSequence(E, spawn_key=(c, r))` sont neufs ; E change avec tout octet du texte,
  couples compris. Ce qui manque : l'interdit de resceller pour changer de graine après une issue (I4).

## 4. Le bruit commun : ce que v9 couvre et ne couvre pas (point 4)

**Couvert (en plus du v8)**, pour une fiche à J ≥ 2 lois connues L_1..L_J (parents triés puis survivantes triées) : toute loi
P(y | x) = Σ_j a^{π(x)}_j·L_j(x)(y) + r_y, où π est la sous-population (un morceau par valeur de g présente dans la part
d'évaluation) ou le côté d'un seuil réel sur **un** trait ; a^p ≥ 0 propre au morceau ; r ≥ 0 **commun : même loi aveugle et
même poids** ε = Σ_k r_k sur tous les morceaux. D'où : W2 ; tout si/sinon de deux lois connues, ou de deux mélanges de lois
connues, sur un seuil ; tout mélange propre à chaque sous-population ; chacune de ces lois mélangée, avec le même poids, à une
même loi aveugle fixe.

**Hors du nul v9**, en deux sortes qu'il faut distinguer :
- **trous** (recombinaisons de lois connues, donc « rien au-delà de l'archive » au sens choisi, mais non couvertes) :
  profondeur ≥ 2, plusieurs seuils sur un trait, coupes obliques, morceaux par historique ou par instant ; aiguillage doux ;
  lois tempérées ou inclinées par morceau ; compositions ; produits (hors produit des parents d'une fille, couvert par le v8) ;
  déformations non monotones (question de nouveauté, T12) ;
- **hors du nul par choix** (dépendances aveugles nouvelles, promouvables au sens choisi) : loi en escalier aveugle ; loi aveugle
  seule sur un morceau ; bruit aveugle propre à un morceau — autre loi aveugle, **ou même loi aveugle avec un autre poids** ;
- et, comme pour le v8 : lois hors de l'archive ; mondes avec mémoire ; traits non finis (1.3).

**La revendication « une loi en escalier aveugle reste promouvable » est exacte** pour la famille (1.1 : aucun sommet mixte ;
essai `test_hors_famille_bruit_propre_au_morceau_non_domine`). Aucune ligne du banc ne mesure la puissance sur une loi en
escalier aveugle pure (H04 n'en est qu'un voisin) : la revendication porte sur la famille, pas sur la puissance (M10).

**Ce que dit la description publique.** `NON_COUVERT_V9` (`pole/nul_v9.py:111-118`) : cinq phrases ; la troisième, « bruit aveugle
propre à chaque morceau, ou loi aveugle seule sur un morceau », range la deuxième sorte **parmi les non-couverts, sans dire que
c'est un choix** ; « lois hors de l'archive » n'y est pas (seule la docstring, `:71`, le dit), ni l'exception des parents d'une
fille (prudent), ni le poids commun du bruit. `PHRASES_MEMBRES_V9` (`:105-110`) dit « un bruit aveugle fixe commun à tous les
morceaux » : juste, ambigu sur le poids. Au commit `e58cfec`, **aucune description publique du juge v9 n'existe** : celle de
l'attaque v4 (`pole/attaque_goodhart_v4.py`, non suivi, vu par recherche seulement : lignes 20 à 22 et 148) concatène les
phrases des membres et « Non couvert : » suivi de `NON_COUVERT_V9`. La phrase de la section 2 du brouillon, « dit par
`nul_v9.NON_COUVERT_V9`, et par la description publique du juge », est donc inexacte sur ces trois points (I2).

## 5. Essais, mutations du banc, mutations du contre-lecteur (point 5)

Essais et banc de mutations : conformes (section 0). Mes douze mutations, appliquées en mémoire par la mécanique de
`essais/mutations_nul_v9.py` (`appliquer_fonction`), chacune contre **les 33 essais** :

| # | mutation | résultat |
|---|---|---|
| C1 | certificat sans le terme d'écart : `min(0, f)` aux deux endroits (`pole/nul_v9.py:213`, `:300`) | **tuée** (13 essais en échec, dont la domination, la référence scipy et l'artefact du départ) |
| C2 | t_c = n (masque ignoré) au lieu des instances de la coupe (`:213`, `:300`) | **tuée** (11) |
| C3 | masque des instances futures décalé d'un cran, `<` → `<=` (`:389`) | **tuée** (11 ; domination dès t = 25) |
| C4 | sommets : moyenne des gradients d'un morceau au lieu du maximum (`:211`, `:291`) | **tuée** (14) |
| C5 | valeur du membre = meilleure valeur atteinte + 10⁻³ (`:443`) | **survit** (I6 : invalide sous optimisation tronquée, 1.6) |
| G1 | mode décisif : `--lignes` accepté (`demonstrations/banc_tricheurs_v9.py:524`) | **survit** (B1) |
| G2 | mode décisif : autre nombre de répétitions accepté (`:524`) | **survit** (B1) |
| G3 | mode décisif toujours refusé, cas sain jamais joué (`:524`) | **survit** (B1) |
| G4 | durée transmise plafonnée à 8 h, la garde acceptant 48 h (`:550-551`) | **survit** (B1) |
| G5 | monotonie : écart de richesse non gardé, seule la promotion inversée arrête (`:272`) | **survit** (B1) |
| L1 | ordre des issues : « banc sans dents » avant « puissance perdue » (`:445-448`) | **survit** (I5) |
| L2 | ordre des issues : « puissance perdue » avant « trou » (`:443-446`) | **survit** (I5) |

La mutation demandée en exemple (« certificat sans le terme d'écart ») est tuée (13 essais en échec sur 33) ; toutes les
mutations de la preuve (C1 à C4) le sont. Les survivantes sont toutes dans le harnais du mode décisif, la lecture ou la
valeur de bout en bout : le code gelé y est juste (lu ligne à ligne), mais rien ne l'épingle.

## 6. Points

### Bloquant

**B1 — R5 : le mode décisif du banc n'est pas éprouvé (cinq mutations du code gelé survivent).** Le brouillon affirme « chaque
garde éprouvée sur un cas sain et un artefact » (section 9, titre, ligne 345) et liste en code 2 « `--lignes`, répétitions
≠ 1 000, durée ≠ 48 h » (ligne 366), en code 3 la monotonie violée par la richesse **ou** par la promotion (lignes 362-363). Or :
(a) aucun essai ne fait passer `principal` en mode décisif jusqu'à `jouer_tout` : `test_cas_sain_et_artefacts_preenregistrement`
(`essais/test_nul_v9.py:530-548`) appelle `lire_preenregistrement` directement ; `test_refus_du_banc_avant_toute_course`
(`:550-571`) n'a que des refus, aucun avec `--lignes` ni `--repetitions` en mode décisif ; (b) `test_duree_du_mode_decisif_48_h`
(`:601-613`) ne joue que l'artefact (28 800 s → code 2) et vérifie la constante, pas le cas sain que demandait l'annexe B
(lignes 500-505 : « sans `--duree-max-s`, le banc passe les gardes et appelle le bouchon (durée transmise = 172 800 s) ») ;
(c) le cas « monotonie » de `test_banc_reduit_et_liste_d_arret` (`:587-592`) viole les deux disjoints à la fois. Mutations G1 à G5 :
survivantes (section 5). **Levée**, par des essais seulement (fichiers non gelés : le bloc de la section 12 ne change pas) :
1. `test_mode_decisif_cas_sain_et_refus` (dans `GrainesEtPreenregistrement`) : `DOSSIER_PREREG` et `jouer_tout` remplacés comme
   dans les essais voisins (bouchon qui consigne ses tâches et rend un arrêt) ; texte d'essai scellé au bon nom gelant les 14
   empreintes réelles (`self._prereg(self._gel())`) ; **cas sain** : `principal([sortie, "--preenregistrement", p])` → code 3 (le
   bouchon a été appelé une fois), 31 tâches, toutes à 1 000 répétitions, durée 172 800 s, entropie `int(sha256(p), 16)` ;
   **artefacts** : `--lignes M01`, puis `--repetitions 999` → code 2, bouchon jamais appelé. Tue G1 et G2 (« 3 != 2 »), G3
   (« 2 != 3 »), G4 (« 28800 »).
2. Dans `test_banc_reduit_et_liste_d_arret`, un sous-essai « richesse » : `juger_v9` rend v9 non promu à log W 2,0 et v8 non promu à
   log W 1,0 → code 3, « MonotonieViolee » ; tue G5.
3. Les cinq mutations G1 à G5 (fragments exacts dans `sondes_mutations_contre_lecture_v1.py`) ajoutées à
   `essais/mutations_nul_v9.py`, chacune tuée pour la raison attendue ; essais et banc rejoués, témoin sans échec.

### Importants

**I1 — « puissance perdue », l'issue attendue, ne demande pas que la validité soit établie.** Condition : « aucune ligne fatale
non tenue, une perte au moins non tenue » (ligne 297 ; code `banc_tricheurs_v9.py:443-446`) ; elle admet des fatales « non
jugeables » et des artefacts non tenus (le « banc sans dents » passe après, `:447-448`), et la règle de P1b (lignes 341-343)
n'interdit que « confirmé ». Pourtant la lecture dit « le v9 ferme les lignes » et ouvre la production (lignes 297-300, 316-318).
En pratique les 17 lignes « par construction » seront tenues (0/1 000, valeur p ≈ 5·10⁻²³) et les artefacts probablement aussi,
mais c'est le chemin de lecture le plus probable : il doit dire sa condition. **Couples** T17 (lecture à deux étages, sans
toucher au code : champs `lecture.fatales` et `lecture.artefact`), T18, T20.

**I2 — Le choix du bruit commun est mal reporté.** (a) La section 2 ne dit pas que le **poids** du bruit est commun (une même loi
aveugle avec des poids propres aux morceaux n'est pas couverte ; `pole/nul_v9.py:238-241`) ; (b) P6 (ligne 214) appelle « taux de
fausse promotion des trous restants » les taux de T12b (« la fiche dit vrai », ligne 182) et de H04 (S1 + q sur g = 0, S2 + q′
sur g = 1, ligne 186) — or, au sens choisi (lignes 138-141 : « une dépendance nouvelle de l'issue à g ou à un seuil l'est »), H04
porte une dépendance aveugle nouvelle (q ≠ q′) : sa promotion n'est pas fausse ; la section 11 (lignes 401-402) dit de même
« trous restants » ; (c) `NON_COUVERT_V9` range le choix parmi les trous, n'a pas « lois hors de l'archive », et la description
publique du v9 n'existe pas au commit (section 4). Conséquence pour Lazar : sa confirmation du sens (I3) doit voir que, sous le
bruit commun, H04 est promu à 26/100 à blanc (L3) **légitimement**. **Couples** T09, T10, T14, T30 ; pour l'attaque v4 et la
production (hors de ce texte, code gelé ici) : la description publique doit séparer « trous » et « hors du nul par choix ».

**I3 — Un sens de revendication ne prend pas effet par défaut.** Le brouillon porte le bruit commun « par défaut et à confirmer
par Lazar (… défaut sous 48 heures) » (lignes 42-44, 139-141) et « sans réponse, le défaut vaut et la revendication publique le dit
comme un choix » (lignes 457-458), alors qu'il range lui-même l'usage en production sous le nœud « modification d'hypothèse ou de
revendication » (lignes 317-318). La course n'en dépend pas (dit, juste) ; la revendication publique et la production, si.
Recommandation (confiance moyenne : la règle du dépôt pour ce cas précis ne m'est pas visible) : course sans attendre,
revendication et production après la réponse explicite. **Couples** T11, T36.

**I4 — « Un scellement, une course décisive » est tronquée, et l'arrêt déterministe n'a pas de lecture.** Le brouillon dit la
règle du v8 « reprise mot pour mot » (lignes 238-240) mais omet l'interdit de resceller pour changer de graine après une issue,
la citation de la première course par toute reprise, la vérification avant scellement de l'absence de dossier décisif
(`prereg/preenregistrement-validation-nul-v8-v2.md:121-128`). Et « après un arrêt, rejeu … même fichier scellé » (lignes 364-365)
vaut pour la durée, non pour une erreur, une richesse non finie ou une monotonie violée : à graines égales elles se reproduisent
à l'identique, et ce sont des défauts du code du v9 (1.5), qui doivent être lus comme tels. **Couples** T15, T26.

**I5 — L'ordre gelé des issues n'est éprouvé par aucun essai.** Aucun essai de `LectureGelee` (`essais/test_nul_v9.py:459-503`) ne
combine deux conditions ; L1 et L2 survivent. Or l'ordre « trou » avant « puissance perdue » est ce qui empêche une ligne fatale
non tenue d'être lue « puissance perdue » quand I02 perd, ce qui est presque sûr. **Levée** : un essai
`test_ordre_des_issues` (M03 à 90/1 000 et perte de I02 à 120/1 000 → « trou » ; perte de I02 et M02 apparié à 20/1 000 →
« puissance perdue ») et les mutations L1, L2. Couple T22 (tableau).

**I6 — La validité « quel que soit l'état de convergence » n'est éprouvée que sur `_certificats` au point de départ.** C5 (valeur
= meilleure valeur atteinte + 10⁻³) survit à toute la suite, parce qu'aux réglages livrés l'optimiseur converge (1.6 : 0 écart) ;
sous optimisation tronquée, C5 tombe sous la vraisemblance du monde à 83 instants sur 150, le certificat jamais. **Levée** : un
essai `test_valeur_certifiee_sous_optimisation_tronquee` (les 30 mondes de l'essai de domination, `PALIERS_MU = (1e-2,)`,
`PAS_MAX_PAR_PALIER = 1` par `unittest.mock.patch.object` : valeur ≥ vraisemblance à chaque instant ; et, pour les dents de
l'essai, au moins un instant où la meilleure valeur atteinte + 10⁻³ est dessous) et la mutation C5. Couple T21 (tableau).

**I7 — En-tête, statut, section 9, section 12, section 14 et annexe B décrivent l'état d'avant `e58cfec`.** « Correction … dite,
non faite » (lignes 10-14, 47, 486), en-tête au commit `5e352ec` avec les empreintes d'avant pour le banc, les essais et les
mutations (lignes 16-27), « aucun essai ne vise ce refus » (ligne 358), « 33 mutations » (lignes 368-370), jeton et « valeur à ne
pas geler » (lignes 411-414, 420), étape 1 de la section 14 (lignes 452-456), « marqueur restant » (lignes 510-511). **Couples**
T01 à T08, T24, T27, T28, T31 à T35, T37, T38.

### Mineurs

- **M1** — A5 compte les membres par morceaux parmi les **quatre premiers** dominants rapportés (`banc_tricheurs_v9.py:313`,
  `:417`) : sous-estimation possible, jamais surestimation ; à dire (T19).
- **M2** — Repère A5 de M07 : « seuil 41 » (ligne 335) ; L3 donne seuils 90/100 (z0 : 41, z1 : 49) (T19).
- **M3** — « onze fois le pire coût mesuré » (ligne 261) : onze fois le coût **moyen** ; le pire par ligne (T12b, 0,93 s par
  répétition en L3) donne six fois (T16). 48 h restent très larges.
- **M4** — I01 et I02 : « aucune survivante, aucun morceau à un niveau n'en dit rien » (lignes 189-191) est trop fort : sur un
  morceau coupé sur un trait, les survivantes, qui dépendent de l'autre, en suivent une part — c'est le prix mesuré (T13).
- **M5** — M01 est la **forme** du monde W2 sur des lois tirées à chaque répétition ; les cartes réelles de W2 sont éprouvées par
  `test_monde_w2_de_l_attaque_membre_du_nul_v9` (T12).
- **M6** — Traits non finis : hors de la preuve (1.3), impossibles dans le banc ; à dire (T10).
- **M7** — Les docstrings du code gelé citent encore le brouillon 1 (`banc_tricheurs_v9.py:7`, `:109`, `:369` ;
  `pole/nul_v9.py:6`) : sans effet ; ne pas y toucher (empreintes).
- **M8** — A2 (`banc_tricheurs_v9.py:421-423`) est inaccessible dans une course complète (l'arrêt de monotonie passe avant) et n'a
  pas d'essai synthétique dans `LectureGelee` : essai facultatif.
- **M9** — « La marge (a) est celle du v8, fixée par Lazar avant toute course du v9 » (lignes 393-395) : la valeur l'était ; son
  adoption pour le v9 vient après L3 (section 3) (T29).
- **M10** — La promouvabilité d'une loi en escalier aveugle pure n'est mesurée par aucune ligne ; la revendication porte sur la
  famille (section 4). Rien à changer pour cette course.

Vérifié sans réserve : correction 1 de la section 1 bis (1.4) ; correction 2 (le banc v8 joue 18 lignes sur 15 scénarios :
`demonstrations/banc_tricheurs_v8.py:114-127`, `LIGNES` ; « 27 » est la numérotation T01 à T27 de la note du banc,
`demonstrations/banc_tricheurs_v7.py:7`) ; les 31 lignes du tableau de la section 3 contre `scenario_v9`, `v7.scenario` et `LIGNES`
(lois, mondes, intervalles des tirages) ; `PREDICTIONS` égale à la section 4 ; repères de L3 et L6 de la section 10 retrouvés
dans les sorties ; commande de la section 5 conforme aux options du banc ; fermeture statique et dynamique = 14 fichiers.

## 7. Couples

`prereg/couples-contre-lecture-validation-nul-v9-v1.json` : 38 couples {"ancien", "nouveau"}, numérotés ici T01 à T38 dans
l'ordre du fichier. Construits par `couples_contre_lecture_v1.py` (bloc-notes), qui prend chaque « ancien » dans le brouillon 2
(plage de lignes ou fragment littéral) et vérifie : chaque « ancien » présent **une seule fois** dans le brouillon 2, et encore
une seule fois au moment de son application dans l'ordre du fichier ; après application, jeton absent, un seul bloc, 14 lignes
au format du banc, noms = `FICHIERS_GELES` dans l'ordre, empreintes = fichiers présents. Texte obtenu (559 lignes, non
scellable avant B1) : `texte-applique-brouillon2-couples-v1.md` dans le bloc-notes.

| couples | objet |
|---|---|
| T01 | statut |
| T02 à T08 | correction de l'annexe B faite, en-tête au commit `e58cfec`, passages des essais et mutations, section 0 (I7) |
| T09 à T11 | section 2 : poids commun, trous et choix, revendication sans défaut (I2, I3, M6) |
| T12, T13 | section 3 : M01, I01 et I02 (M5, M4) |
| T14 | P6 (I2) |
| T15, T16 | section 5 : règle « un scellement », durée (I4, M3) |
| T17, T18 | section 7 : « puissance perdue » à deux étages, production (I1) |
| T19, T20 | section 8 : A5, réserve log-linéaire sous « puissance perdue » (M1, M2, I1) |
| T21 à T25 | section 9, tableau : certificat (I6), lecture gelée (I5), refus avant course, durée, liste d'arrêt (B1) |
| T26, T27 | section 9 : arrêts déterministes (I4) ; banc de mutations (I7, B1) |
| T28 à T30 | section 10 : ligne L10 ; marge (a) ; section 11 : H04 (I7, M9, I2) |
| T31 à T33 | section 12 : valeurs revérifiées ; ligne du banc ; **jeton remplacé** par `7e4bff5995df2a7d62a4f5a2f5f9176da614e657a55b05183325fa2fc6e24e44` |
| T34 | section 13 |
| T35, T36 | section 14 : étapes 1 (B1, I5, I6 à faire) et 2 (I3) |
| T37, T38 | annexe B : titre, marqueur levé et écart dit |

Les couples nomment les essais à ajouter (`test_mode_decisif_cas_sain_et_refus`, `test_ordre_des_issues`,
`test_valeur_certifiee_sous_optimisation_tronquee`) : si le directeur les nomme autrement, T23 et T24 suivent. Les empreintes
des essais et des mutations de l'en-tête (T04, T05) sont celles de `e58cfec` ; la version finale est celle du commit de scellement.

## 8. Observé en passant, sans y toucher

- À 19:15:08 UTC, pendant cette contre-lecture, `prereg/preenregistrement-validation-nul-v9-brouillon3.md` est apparu (autre
  travail), puis a été commité (`9e6ca23`, 19:23:53 UTC : « bench hash at the 48 h fix (e58cfec), no marker left ; under fresh
  counter-reading ») ; deux autres commits ont suivi (`a12713a`, `08b1f17`, tête à 19:41 UTC). Aucun ne touche les fichiers lus
  ici : `pole/nul_v9.py`, le banc v9, ses essais, ses mutations et le brouillon 2 sont égaux de `e58cfec` à `08b1f17`
  (`git diff --quiet`). Le brouillon 3 (`347523dd…`, 110 lignes de diff avec le brouillon 2) **n'est pas contre-lu ici**. Contrôle
  mécanique seulement : des 38 « anciens », 23 sont présents une seule fois dans le brouillon 3 (T07 à T23, T25, T26, T29, T30,
  T34, T36 : tous les couples de fond, B1 et I1 à I6 compris, s'y appliquent tels quels) ; 15 n'y sont plus (T01 à T06, T24,
  T27, T28, T31 à T33, T35, T37, T38 : passages d'en-tête, de statut, de section 9, 10, 12, 14 et d'annexe B que le brouillon 3 a
  réécrits ; I7 est à revérifier sur sa version). Les essais de B1, I5 et I6 restent à ajouter : le code des essais est inchangé
  à la tête.
- Arbre : fichiers `*tour_ferme_v63*` modifiés et fichiers de l'attaque v4 non suivis (autres travaux), non touchés ;
  `pole/attaque_goodhart_v4.py` consulté par recherche seulement (section 4).
- Charge de la machine 6 à 12 (autres agents) pendant mes passages ; durées des essais et du banc de mutations conformes.

## 9. Empreintes des pièces de cette contre-lecture (bloc-notes)

```
15f1bf6cf794cc7745722abb9f537d4a0291f8a7e96ef44c4c972a5ac8d46d36  tables_contre_lecture_v1.py
e5a4431a04fbc8a8b47cbda5873e2031f4019f96106843c287c7d8d65b323737  tables_contre_lecture_v1.txt
a91589835da036ee1c045f464a2b74f649a68c4b951aa799a86ffd58e4d65bd7  sondes_mutations_contre_lecture_v1.py
f6776f76287475831df79d231228fe5da889aa89b7b4a4f1b82820f018f3abf6  sondes-mutations-sortie.txt
38dc0a3b2a3876246be602212a518762a172ccbfce521ca83134184f9b96a9cb  sonde_domination_v1.py
93b650c872104c941ca1e3aafb3b33976de05e28ef137811b310b0c2b946b180  sonde-domination-sortie.txt
6127d47318a317f9c99ed3e8b6ff8c60c21dc9313730f19847969e756a0b203f  fermeture_dynamique_v1.py
1f9ae2792d3be914c2b8de9e0a88f8de492537bffe05c066fd6cafb7f124732b  fermeture-dynamique-sortie.txt
a81133953ef2b8acebf9ce52f0dbf3d1559d37ea90b1b367aaf9a825c6779d11  essais-v9-sortie.txt
029fdd8a759ea5deed988c1eebfbf871831a9d11d9d068237ae642cea444c6cd  mutations-v9-sortie.txt
0140562a661f36d86cede4ebfebba13107c7dbc59c7e22c445ac30078fc140cb  couples_contre_lecture_v1.py
78c9b1e5c1f2337c6a5ee09cd7d24c35b050242ea61b4c83b4a31d2479e71f20  couples-contre-lecture-validation-nul-v9-v1.json
6d38e39bbae737db4b9f97d0085cf2eca729c93cbd9f19eb64782e13acd58b4b  texte-applique-brouillon2-couples-v1.md
```

Le JSON du dépôt est la copie, à l'octet, de celui du bloc-notes. Ce fichier ne porte pas sa propre empreinte ; elle est donnée
avec sa remise.
