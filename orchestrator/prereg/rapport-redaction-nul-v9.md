# Rapport de rédaction — nul v9 du juge (recombinaisons par morceaux), brouillon de conception et de validation

Rédigé le 2 novembre 2026, de 17:32 à 18:32 UTC (`date -u`), par un sous-agent concepteur neuf (statisticien) qui n'a écrit ni le
nul v8 ni l'attaque contre le juge. Aucun appel de modèle, aucun réseau, aucune dépense ; aucun commit, aucun `.sha256` dans
le dépôt, aucun fichier existant modifié, rien sous `donnees/` ; tout calcul sous `nice -n 10 python3 -I -B`, pytest avec
`-p no:cacheprovider` ; fichiers temporaires dans le bloc-notes `…/scratchpad/nul-v9/` (chemin complet en section 9).

## 1. Verdict

Le nul v9 ferme, par construction, la recombinaison par morceaux à un niveau des lois connues (par sous-population, et par
**tout** seuil réel sur un trait), avec un mélange des lois connues propre à chaque morceau et un bruit aveugle commun : sur les
courses à blanc, le monde W2 de l'attaque et six autres tricheurs par morceaux ne sont jamais promus sous v9 (0/100 et 0/30,
log W ≤ 0) alors qu'ils le sont sous v8 (jusqu'à 99/100). Le prix en puissance est faible sur les effets forts (perte appariée
0 à 0,05) et d'environ 0,11 sur une interaction faible près du seuil. **Un écart au brief est dit** (section 3.5) : le
dénominateur reste un **maximum** sur les membres ; un « mélange a priori sur les membres » au dénominateur ne garde pas
Ville au niveau α. **Une affirmation reprise est corrigée** (section 4 du préenregistrement, section 1) : le banc v8 joue 18
lignes sur 15 scénarios, pas « 27 tricheurs ».

## 2. Conception

### 2.1 Membres

Nul v9 d'une fiche = nul v8 (inchangé, `nul_v8.membres_archive_v8`, sa garde comprise) + membres de type `ajuste_morceaux`
construits sur les **lois connues** de la fiche (celles du membre `ajuste_lineaire:archive` du v8, dans son ordre : parents
triés, puis survivantes triées hors parents ; au moins deux lois, sinon aucun membre — avec une seule loi et un bruit commun,
chaque morceau porte la même loi : c'est le membre linéaire du v8) :

- `morceaux:sous_population` : un morceau par valeur de g présente dans la part d'évaluation ;
- `morceaux:seuil:z<j>` pour chaque trait j : deux morceaux, z_j ≤ s et z_j > s, le seuil s étant **ajusté sur tout ℝ**.

Sur chaque morceau P : m_P(x)(k) = Σ_j a^P_j·L_j(x)(k) + r_k, avec a^P ≥ 0 propre au morceau, r ≥ 0 **commun**, et
Σ_j a^P_j + Σ_k r_k = 1 pour chaque P. La famille contient le monde W2 (a^0 = e_S1, a^1 = e_S2, r = 0), tout si/sinon de deux
lois connues sur un seuil, tout mélange propre à chaque morceau, et ces lois mélangées à une même loi aveugle fixe. Profondeur
1 au moins, comme demandé ; la profondeur 2 n'est pas couverte (section 4).

Fichier : `pole/nul_v9.py` (`membres_morceaux`, `lois_connues`, `membres_archive_v9`, garde `exiger_membres_v9` qui lève
`NulV9Refuse` : membres du v8 altérés, membre par morceaux absent, en double, inattendu, lois ou partition altérées).

### 2.2 Pourquoi le bruit est commun aux morceaux

Un bruit aveugle propre à chaque morceau mettrait dans le nul toute **loi en escalier aveugle** (une loi fixe sur g = 0, une
autre sur g = 1 ; ou de part et d'autre d'un seuil) : une dépendance de l'issue à g ou à un seuil, que l'archive ne dit pas et
qui serait une découverte, ne pourrait plus jamais être promue. Avec r commun, si r porte toute la masse d'un morceau il la porte
sur tous : aucune loi aveugle propre à un morceau. C'est un choix de sens de « rien au-delà de l'archive » (la recombinaison
des lois connues n'est pas neuve ; une dépendance nouvelle l'est), dit ici et dans la description publique ; la contre-lecture
doit le vérifier (section 11, point 3). Prix : un tricheur « par morceaux avec un bruit différent par morceau » n'est pas
couvert (ligne mesurée H04, 26/100 promus sous v9 à blanc).

Les membres tempérés et inclinés du v8 (p ∝ S^a·exp(β)) ne sont **pas** repris par morceaux : avec a = 0 sur un morceau, ce
serait encore une loi aveugle propre au morceau. Non couvert, dit (ligne H05, 10/100).

### 2.3 Calcul

Pour un instant de lecture t (les t premières issues de la part d'évaluation, comme les membres ajustés du v8) et une partition
fixée, f(x) = Σ_i log(c_i·x) est concave sur le polytope 𝒫 = {a^P ≥ 0, r ≥ 0, Σ_j a^P_j + Σ_k r_k = 1 ∀P}.

- **Valeur rendue = certificat**, jamais la valeur atteinte : pour tout x > 0, sup_𝒫 f ≤ f(x) + max_{v ∈ sommets(𝒫)} ∇f(x)·v −
  ∇f(x)·x, et ∇f(x)·x = Σ_i (c_i·x)/(c_i·x) = t **exactement** (homogénéité), sans hypothèse d'admissibilité ni de
  convergence ; sommets : « une loi connue par morceau, r = 0 » et « r = δ_k, a = 0 » (𝒫 est l'enveloppe convexe de ces
  points) ; borne aussi par 0 (m_i ≤ 1). Fonctions `_certificats` et la ligne `certificat = …` de `maximiser_par_lots`.
- **Optimisation** : points intérieurs (Newton avec barrière logarithmique, contraintes d'égalité couplées résolues par le
  système de Karush-Kuhn-Tucker, pas fractionnaire au bord 0,99, recherche linéaire d'Armijo), paliers μ = 10⁻², 10⁻⁴, 10⁻⁶,
  10⁻⁸, au plus 30 pas par palier, **par lots** sur toutes les coupes de tous les instants et de tous les membres d'un même
  nombre de morceaux ; départ = 0,9 × mélange sans coupure (même mélange sur chaque morceau) + 0,1 × centre de 𝒫, et le mélange
  sans coupure lui-même est certifié avant le premier pas. L'espérance-maximisation, essayée d'abord (L1), converge trop
  lentement quand l'optimum est au bord (écarts résiduels jusqu'à 1,6 nat après 2 000 itérations).
- **Élagage certifié** : une coupe dont le meilleur certificat est sous la meilleure valeur atteinte de son groupe (membre,
  instant) ne peut pas porter le maximum ; elle garde son dernier certificat ; un groupe est terminé quand sa plus haute borne
  est à moins de 10⁻³ de sa meilleure valeur atteinte. **Valeur du membre = maximum, sur toutes les coupes du groupe (élaguées
  comprises), de leur meilleur certificat** : valide quoi qu'il arrive ; la tolérance 10⁻³ ne coûte que de la puissance.
- Durée : 0,1 à 0,2 s par évaluation sous v9 sur machine peu chargée (L1), 0,24 à 0,54 s par répétition « v9 + v8 apparié »
  sur machine partagée (L4).

L'évaluateur `evaluer_v9` est une copie de `nul_filles_v2.evaluer_v2` (mêmes gardes, même lecture aux instants fixés, même
règle de marge des filles) où la liste des types ajustés gagne `ajuste_morceaux` ; son calcul sans garde,
`evaluer_sur_issues`, sert aux bancs pour évaluer deux bibliothèques sur les mêmes issues (`sans_morceaux` rend la
bibliothèque v8 de la même fiche).

## 3. Preuve (validité)

Notations : 𝓝₉ = 𝓝₈ ∪ {F_g} ∪ {F_{s,j}}, j = 0..d−1 ; pour un membre ajusté F, v_F(t) sa valeur rendue à l'instant t ; pour un
membre ordinaire, sa log-vraisemblance. D_t = max_F v_F(t) ; N_t = log q(y_1..t | x_1..t), q loi gelée de la fiche (ou mélange
du pari à fraction) ; log W_t = N_t − D_t, lu aux instants fixés d'avance.

**3.1 Domination.** Pour F = F_g ou F_{s,j} et toute loi P ∈ F (sans mémoire : P(y | x) ne dépend que de l'instance) :
v_F(t) ≥ log P(y_1..t | x_1..t), pour toutes issues. Preuve : P correspond à un point x_P de 𝒫 pour la partition de P
(sous-population, ou coupe c_P réalisée par son seuil, voir 3.2) ; chaque certificat de la coupe c_P, pris en un point x
quelconque, est ≥ sup_𝒫 f_{c_P} ≥ f_{c_P}(x_P) = log P(y_1..t | x_1..t) (concavité : f(x_P) ≤ f(x) + ∇f(x)·(x_P − x) ≤ f(x) +
max_sommets ∇f(x)·v − t) ; le meilleur certificat de c_P l'est donc aussi, et le maximum sur toutes les coupes de leur meilleur
certificat (la valeur rendue) le domine. Pour les membres du v8 : inchangé (écart de Frank-Wolfe exact pour le membre linéaire ; marge de Newton au
second ordre seulement, non démontrée, pour les membres log-linéaires — réserve du v8, reprise telle quelle).

**3.2 Tout seuil réel.** f ne dépend de s que par la partition {i ≤ t : z_ij ≤ s}. Si u_0 < … < u_{q−1} sont les valeurs
distinctes de z_j parmi les t instances, toute partition réalisée par un s réel est {z ≤ −∞} (vide) ou {z ≤ u_k} : ce sont les
q + 1 coupes de `_coupes` (les égalités sont groupées : aucune coupe ne sépare deux valeurs égales). Le sup sur s ∈ ℝ est donc
un maximum fini, chacune de ses coupes certifiée. La condition « z_j > s » de `selection_pari._condition` est la branche
« si » : le morceau haut.

**3.3 La richesse sous un membre reste sous une martingale de test.** Si le monde P ∈ F* ∈ 𝓝₉ : D_t ≥ v_{F*}(t) ≥ log P(y_1..t),
donc W_t ≤ Λ_t := q(y_1..t)/P(y_1..t) trajectoire par trajectoire. Dans l'ordre du plan, q est prévisible (gelée avant les
tirages, dont la graine dérive de l'empreinte de l'engagement) : E_P[q(y_t | ·)/P(y_t | ·) | 𝓕_{t−1}] = Σ_k q_k = 1, donc Λ est
une martingale positive d'espérance 1 sous P. Pari à fraction : le numérateur est un mélange a priori, à poids fixés, de lois
prévisibles ; chaque rapport est une martingale de test sous P, et **un mélange à poids fixés de martingales de test sous la
même loi P est une martingale de test** (linéarité de l'espérance conditionnelle). W est donc majorée par une martingale de
test : c'est une surmartingale positive majorée, la forme que demande le brief.

**3.4 Ville.** P(∃ t lu : W_t ≥ 1/α) ≤ P(sup_t Λ_t ≥ 1/α) ≤ α, pour tout monde de tout membre, **quel que soit le nombre de
membres** (le maximum ne coûte jamais de validité). La règle de marge des filles ne fait que retirer des promotions.

**3.5 Pourquoi pas un mélange a priori sur les membres au dénominateur (écart au brief, dit).** Avec D̃_t = log Σ_F π_F·e^{v_F(t)},
pour P ∈ F* : D̃_t ≥ log π_{F*} + log P(y_1..t), donc W̃_t ≤ Λ_t/π_{F*} et Ville ne donne que P(promotion) ≤ α/π_{F*} : la garantie
tombe d'un facteur 1/π_{F*} (pour un seuil continu à prior diffus, π de la cellule du vrai seuil est de l'ordre de 1/t : la
garantie disparaît). Le maximum garde α pour tout membre. Le « mélange a priori » qui garde Ville est celui du numérateur
(3.3), déjà dans le juge (pari à fraction) ; il est inchangé. Si le brief entendait par « mélange » une répartition de α
entre membres (seuil 1/(α·π_F) pour le membre F), le maximum n'en a pas besoin : il garde α pour chaque membre sans rien
répartir, quel que soit le nombre de membres (W_max ≤ W̃ trajectoire par trajectoire).

**3.6 Monotonie.** 𝓝₉ ⊇ 𝓝₈ : D_t(v9) ≥ D_t(v8) sur les mêmes issues, W(v9) ≤ W(v8) trajectoire par trajectoire, toute
promotion sous v9 en est une sous v8, et le taux de fausse promotion de tout monde est ≤ celui du v8. Gardé à chaque
répétition du banc (`verifier_monotonie` : arrêt, code 3).

**3.7 Réserves.** (i) Mondes sans mémoire seulement (comme le v8) ; (ii) marge de Newton des membres log-linéaires du v8 :
second ordre, non démontrée (inchangé) ; (iii) le certificat est exact en arithmétique réelle ; en flottants, l'erreur est de
l'ordre de t·10⁻¹⁶ (tolérances des essais : 10⁻⁹) ; (iv) la condition de l'inférence universelle est la même que celle du v8
(nul ajusté sur les issues où le numérateur est évalué, numérateur gelé avant) : respectée.

## 4. Ce qui reste non couvert (la description publique le dira, `nul_v9.NON_COUVERT_V9`)

| classe non couverte | ligne mesurée (L3, 100 répétitions, sous v9 ; v8 apparié) |
|---|---|
| profondeur 2 (sous-population puis seuil, deux seuils, deux traits) ; coupes obliques | H01 : 89/100 (97) |
| plusieurs seuils sur un même trait (escalier), poids qui varient continûment (aiguillage doux) | H02 : 21/100 (96) |
| produits de lois connues (sauf, pour une fille, celui des deux parents) | H03 : 90/100 (93) |
| bruit aveugle propre à un morceau, loi aveugle seule sur un morceau | H04 : 26/100 (98) |
| lois tempérées ou inclinées différemment par morceau ; compositions d'étapes | H05 : 10/100 (100) ; T07 : 1/100 (3) |
| déformations non monotones ; lois hors de l'archive | T12b (la fiche dit vrai) : 77/100 (84) |

Ces taux sont ceux de **mondes égaux à la loi du tricheur** (pire cas) ; ils mesurent combien chaque trou reste ouvert, pas
une faiblesse de la garantie sur la classe couverte. Rien de ce tableau n'est revendiqué fermé.

## 5. Coût en puissance (mesuré à blanc ; la mesure décisive est celle du préenregistrement)

Perte **appariée** (même fiche, mêmes issues ; part promue sous v8 et non sous v9), L3, 100 répétitions, graine 20261102 :

| monde à loi neuve plantée | v9 | v8 apparié | perte |
|---|---|---|---|
| fille neuve (A sur g = 0, N ailleurs) | 96 | 100 | 0,04 |
| fraîche neuve (N) | 94 | 94 | 0,00 |
| I01 interaction forte (signe de z0·z1, hors de l'archive et du v9) | 87 | 92 | 0,05 |
| I02 interaction faible | 41 | 52 | 0,11 |
| F03 loi neuve faible (N × 0,3) | 72 | 75 | 0,03 |

Décalage du dénominateur Δ = log W(v8) − log W(v9) sur les mêmes issues (L4, 40 répétitions) : médiane 0,35 nat (T17s, monde
S1), 2,47 (T04, mélange), 0 (fraîche neuve), 1,76 (I01), 0,66 (I02), 0,07 (F03), 18,75 (fille neuve). Lecture : sur un monde
du v8, les membres par morceaux surajustent de l'ordre de 0,3 à 3,7 nats (le maximum sur ≈ 400 partitions et des poids par
morceau) ; la perte se concentre sur les lois neuves dont la richesse est près du seuil log 20 (effets faibles). **Fille
neuve** : son décalage de 18,75 nats n'est pas un pur coût — le membre par sous-population reconnaît A sur g = 0, et le v9 ne
crédite plus la fille que de ce qu'elle dit de neuf (N sur g = 1) ; sa puissance reste 0,96.

## 6. Fichiers neufs et empreintes

Voir section 9 (empreintes calculées après le dernier passage des essais et des mutations). Aucun autre fichier n'a été créé
dans le dépôt ; aucun fichier existant n'a été modifié (les fichiers des autres agents, `*attaque_goodhart_v3*`,
`*tour_ferme_v63*`, `*juges_idees_v2*`, `*brouillon4*`, n'ont été que lus, ou pas du tout).

## 7. Essais (`essais/test_nul_v9.py`)

32 essais, 32 sous-essais, réussis (≈ 36 à 45 s ; dernier passage en section 9). Chaque garde sur un cas sain et un artefact
(R5) : membres (sain : v8 intact puis 3 membres ; artefacts : 9 altérations refusées) ; certificat (sain : 30 mondes de la
famille × 5 instants, valeur ≥ log-vraisemblance du monde ; seuil égal à une valeur observée ; référence indépendante scipy
SLSQP sur 14 instances, valeur ≥ référence et ≤ référence + 10⁻² ; artefacts : la valeur atteinte au départ est **sous** la
vraisemblance du monde W2 — ce qu'un calcul sans certificat rendrait —, et un monde à bruit propre au morceau n'est pas dominé,
limite dite de la famille) ; départ non admissible refusé ; évaluateur (identique à `evaluer_v2` sans membre par morceaux,
fille et fiche ; départage des égalités par le nom ; monotonie v9 ≤ v8 ; gardes d'engagement et de tirages ; membre ou
partition inconnus refusés) ; tricheurs (le monde W2 de l'attaque, cartes 0 à 3 de `attaque_goodhart_v2.carte(7, c, "W2")`, et
la loi « si/sinon par sous-population S1, S2 » : jamais promus sous v9, log W ≤ 10⁻⁶, promus sous v8 ; W1 non plus ; M01 0/20,
M02 à M07 0/8 ; I01 et fraîche neuve ≥ 15/20 avec ≤ 2 pertes ; artefact : sans membres par morceaux, M01 promu ≥ 16/20 ; perte
appariée comptée dans le bon sens) ; lecture gelée (cinq issues, plan incomplet, audits A1, A3, A4, A5) ; préenregistrement
(nom, dossier, scellement, gel, empreinte) ; refus avant course (code 2) ; liste d'arrêt (durée, erreur, monotonie violée :
code 3 ; fatale promue : code 1) ; fermeture des imports = `FICHIERS_GELES` (14 fichiers, égalité exacte).

## 8. Banc de mutations (`essais/mutations_nul_v9.py`)

33 mutations, **33 tuées pour la raison attendue**, 0 survivante, témoin 21 essais sans échec avant et après (dernier passage
en section 9). Liste : certificat remplacé par la valeur atteinte (deux endroits) ; sommets r = δ_k oubliés ; seuils sur une
grille fixe ; seuil lu sur le mauvais trait ; élagage trop agressif ; départ sur le bord ; sous-population à un seul morceau ;
pas de Newton à l'envers ; aucun membre pour deux lois ; garde des membres neutralisée, lois non vérifiées, membres du v8 non
vérifiés ; membres par morceaux ignorés par l'évaluateur ; membre inconnu ignoré ; garde d'engagement retirée ; départage par
l'ordre ; monotonie non gardée ; perte appariée à l'envers ; v8 apparié évalué avec les morceaux ; « trou » jamais rendu ;
perte sans effet ; marge ignorée ; artefacts appariés non lus ; audits A4 (classe par morceaux) et A5 retirés ; test exact
inversé ; brouillon accepté ; non scellé accepté ; empreintes non vérifiées ; espace des graines non borné ; erreur avalée ;
code de sortie forcé. Au premier passage, deux mutations survivaient : « coupe z ≤ s devenue z < s » (**mutation
équivalente** : la partition « tout en bas » manque mais équivaut à « tout en haut », les deux morceaux ayant la même famille ;
remplacée par « seuil lu sur le mauvais trait ») et « départage par l'ordre » (aucune égalité exacte dans les essais ; essai
`test_departage_des_membres_comme_v2` ajouté).

## 9. Courses à blanc réduites, lectures préalables, empreintes

Bloc-notes : `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/nul-v9/`. Toutes les graines sont
exploratoires (< 2⁶⁴) et différentes de la graine décisive (empreinte d'un fichier scellé qui n'existe pas encore).

- **L1** (17:40 à 18:05) : prototypes `proto/proto_seuil_v1.py` `ce34f62f…1d251`… (espérance-maximisation par lots, élagage,
  ensemble actif), `proto/proto_pi_v1.py` à `v3` (points intérieurs) ; essais rapides `essais-rapides/essai_w2_v1.py`
  `27fe7703…b9af`, `paliers_v1.py`, `reglages_v1.py` `c2249b24…988b` (réglage des paliers : |Δ log W| ≤ 4·10⁻⁴, jamais du côté
  imprudent), `profil_v1.py`, `profil_v2.py`, `instrument_v1.py`.
- **L2** (18:06) : fumée, toutes les lignes, 2 répétitions, graine 11 : `fumee-1/banc-tricheurs-v9.json` `0e04a45160f78c660e2a54b6b951cea18e2314648aaae8f9d42d81c1e648a946`,
  manifeste `053e80eeb935761fa8be9b947187e9cf7ceb4257f4cd93ce626fed26b9065db8`.
- **L3** (18:07 à 18:13) : 15 lignes × 100, graine 20261102 : `blanc-L2-puissance-mesures/banc-tricheurs-v9.json`
  `dda51da36b56ce6f89a47e8ca2119320633c3da6ccaf784033eaa6a373018101`, manifeste
  `ef14fe6c5a611760461896a3e823cff5076c6b66bd618843bd969c7cc3912fe4` (résultats en sections 4 et 5 et au préenregistrement).
- **L4** (18:16 à 18:18) : décalage Δ, `calculs/decalage_v1.py` `a344f89dceca5bf189f34736221b5c2669c4d9357ed50a88873d3b96e99d35c5`
  → `calculs/decalage_v1.json` `3319a8406615c3e1181ca4e6c402aa70f107b0daa81dbf9ae85d98a75fddff9f`.
- **L5** : tables de la lecture, `calculs/tables_v1.py` `22a1d559b844caf00ca0168d192302d8a46ba9e9e0c5fd3acabc449f6668a9e0` →
  `calculs/tables_v1.txt` `10ac2c884ab45d9d5d7238be086613a84fabb4abfd9f4bccdc7ed8c5a6fe0e7e`.
- **L6** (18:20 à 18:22) : 16 lignes × 30 (11 fatales du v8, M03 à M06, T01|v1), graine 20261103 :
  `blanc-L6-fatales/banc-tricheurs-v9.json` `b24a4faf44bcd53a5c3e45f192091c0ce22a9b97f48f131006189e5857e878b8`, manifeste
  `0cca817723b3f21c8b57849ee0351b9a068aaabd2d7ce6b0ec2d69eb83817a6f` ; les 15 fatales 0/30, log W max ≤ 0 ; v8 apparié : M03
  29/30, M04 28/30, M05 16/30, M06 29/30 ; T01|v1 13/30 ; 69,1 s.
- **L7** : essais et mutations ; premier passage `mutations-L5-sortie.txt` (31 mutations, 29 tuées, 2 survivantes, voir section
  8) ; deuxième `essais-et-mutations-L5b-sortie.txt` `f8653453935afbdf413f3832fea4fb4bacd430a7f1efba7d7cf20f34e2d6fbbf` (32
  essais ; 33/33) ; **passage final sur le code livré** : `essais-et-mutations-final-sortie.txt` (empreinte ci-dessous).

Empreintes des fichiers neufs du dépôt et du passage final : complétées en fin de rédaction, bloc suivant.

<!-- empreintes-livraison : début -->
```
8cb44adf8b325ac656b077f03dddb44311071510a5785ebd3f0aa8c37aebc655  pole/nul_v9.py
c7ab547065180b6e23e0e496d9c9dc96b674ed4c1b47766b3e108709fdbcf466  demonstrations/banc_tricheurs_v9.py
f674e9cac121d8930942738e28f938bd3613018c0c4371bd4621e53020212855  essais/test_nul_v9.py
576eea7917cc9c0ed5213eeb22f191add217cc91b54fc4368a087911f153507d  essais/mutations_nul_v9.py
253eece5598f582b09b0fd468fde55b0b7bda98454d25505971b65cbe6afccf0  prereg/preenregistrement-validation-nul-v9-brouillon1.md
```
Passage final des essais et des mutations sur ce code (18:23:22 à 18:25:08 UTC : 32 essais réussis, 32 sous-essais ; 33 mutations tuées pour la raison attendue sur 33 ; témoin 21 essais sans échec avant et après) :
`…/scratchpad/nul-v9/essais-et-mutations-final-sortie.txt` `ba65ab5bf73714ae84f5a3e9759d46f68ebeffaa3f23f848569bc503a75f7940`.
Dépendances gelées inchangées (mêmes empreintes que le bloc du préenregistrement du v8, section 11) : les 12 fichiers `demonstrations/banc_tricheurs_v7.py` … `pole/selection_pari.py` ; vérifié par `sha256sum` le 2 novembre à 18:26 UTC.
Ce rapport ne peut pas porter sa propre empreinte ; elle est donnée avec sa remise.
<!-- empreintes-livraison : fin -->

## 10. Esquisse de la suite : l'attaque relancée contre le juge v9 (une page)

**Question.** Le juge v9 résiste-t-il au proposeur qui le lit et reçoit ses verdicts, sur W1 et W2, maintenant que **les deux
mondes sont au nul** (W1 ∈ v8 ⊂ v9 ; W2 ∈ v9) ? Sous v9, toute promotion est bornée par α tentative par tentative (Ville) ; une
fausse promotion ne peut venir que de la multiplicité des tentatives (plafond 1 − 0,95¹⁶ = 0,56) ou d'un défaut du code. C'est
l'étage 1 d'A1, joué cette fois sur les deux mondes.

**Plan (mêmes règles que la reprise propre, `prereg/preenregistrement-attaque-goodhart-v3-brouillon1.md`)** : Argon seul
(`gemini-4-argon`, commande externe, 2 fils), 16 tentatives, quatre suites par unité, consigne et grammaire servies
inchangées, rejeux, audits A1 à A9, règles des unités non jouées et du relais perdu, graines de T. Deux changements de fond :
(i) le juge de chaque suite « juge » devient **v9** ; (ii) le juge « ancien » (dents) dépend du monde : **v7 sur W1** (A1 :
Argon 10/12), **v8 sur W2** (A1 : Argon 12/12, dès la première tentative). Sur W2, l'hypothèse H4 (« taux de fausses
promotions hors du nul ») devient une hypothèse de résistance comme H2 ; la qualification « brèche par classe non couverte »
n'a plus d'objet sur W2 (brèche par multiplicité ou par défaut du juge).

**Ce qu'il faut changer dans le code v3 (fichiers neufs, R12 : `pole/attaque_goodhart_v4.py`, `demonstrations/attaque_goodhart_v4.py`,
essais et mutations v4)** :
1. `JUGES` : (« v9 », « ancien ») et une table `JUGE_ANCIEN = {"W1": "v7", "W2": "v8"}` ; étiquettes de graines recalculées
   (le juge est dans l'étiquette) et `verifier_cles_distinctes` rejoué.
2. `juger` : « v9 » → `banc_tricheurs_v9.engagement_v9` et `nul_v9.evaluer_v9` (le v8 apparié de `juger_v9` peut être gardé au
   journal, sans effet) ; « v8 », « v7 » → `banc_tricheurs_v8.juger_v8` (inchangé).
3. `bibliotheque_du_juge("v9", L)` : standard + `nul_v9.membres_archive_v9` ; `PHRASES_MEMBRES` + `nul_v9.PHRASES_MEMBRES_V9` ;
   `description_du_juge("v9", L)` ajoute la phrase « Non couvert : » suivie de `NON_COUVERT_V9` (la description publique dit le
   non-couvert, comme le demande le brief) ; refus d'un membre sans phrase, inchangé.
4. `structurellement_couverte` et `hors_classe` : classe couverte du v9 (lois connues, fixes, leurs mélanges, et leurs
   si/sinon et par-sous-population à un niveau de mélanges de lois connues, sous un même mélange à une loi fixe) — sinon
   l'instrument « part hors classe » compterait comme « hors classe » des lois que le v9 refuse par construction.
5. `qualifier_breche`, `lire_monde`, `PREDICTIONS` : W2 lu comme W1 (résistance) ; prédictions réécrites (ouvertes dans les deux
   sens : par exemple taux(v9, retour, 16) ≤ 0,10 sur chaque monde ; taux(ancien, retour, 16) ≥ 0,50 sur chaque monde).
6. `REJEUX = {"v9": 200, "v8": 20, "v7": 20}` ; `SECONDES_PAR_EVALUATION_V9` mesurée (≈ 0,3 s, contre 0,056 s sous v8) ;
   `LOIS_V9_PAR_UNITE = {"W1": 32, "W2": 32}` ; `APPELS_PAR_UNITE` : W2 passe de (12, 40) à (32, 40) (sous v9, W2 ne se gagne
   plus à la première tentative).
7. `GRILLES` : ajouter la grille de 6 unités par case (ε = 0,40 : « résiste » ⇔ 0/6, « brèche » ⇔ ≥ 2/6, la grille d'A1) ; le v3
   n'admet que 24 et 48.
8. `FICHIERS_GELES` : + `pole/nul_v9.py`, `demonstrations/banc_tricheurs_v9.py`, les deux fichiers v4 (fermeture remesurée) ;
   texte `prereg/preenregistrement-attaque-goodhart-v4-vN.md`.

**Devis (Argon : 0,062 USD et 7,6 s par appel mesurés dans A1 ; au plus 64 appels par unité)** :

| option | cartes par monde | unités par case | appels attendus (max) | USD attendus (max) | durée attendue des appels (max, 40 s, 2 fils) | rejeux sous v9 (2 cœurs) |
|---|---|---|---|---|---|---|
| A — W1 et W2, 16 tentatives | 6 | 6 | 444 (768) | 27,5 (47,6) | 0,5 h (4,3 h) | ≈ 77 000 évaluations, 3,2 à 5,4 h |
| B — W1 et W2, 8 tentatives (écart aux règles) | 12 | 12 | ≈ 456 (768) | ≈ 28 (47,6) | 0,5 h (4,3 h) | ≈ 77 000, 3,2 à 5,4 h |
| C — W2 seul, 16 tentatives | 12 | 12 | 408 (768) | 25,3 (47,6) | 0,4 h (4,3 h) | ≈ 77 000, 3,2 à 5,4 h |

Appels attendus : W1 ≈ 40 par unité (A1, Argon : 39,7), W2 ≈ 34 sous v9 (32 sans promotion + 2 sous v8). Le lanceur v3 exige un
plafond ≥ le maximum du devis : **plafond 48 USD** (≤ 50) pour chacune des trois options ; un GO de calcul de ce montant (nœud de
décision de Lazar). Rejeux : ≈ 32 lois sous v9 par unité × 12 unités × 201 évaluations ≈ 77 000, à 0,3 à 0,5 s : 6,4 à 10,7 h de
processeur, 3,2 à 5,4 h sur deux cœurs ; durée attendue haute ≈ 10 h, plafond 20 h comme T. **Option A** répond au brief
(W1 et W2, mêmes règles, ≤ 50 USD) mais à 6 unités par case : « résiste » ne veut dire que 0/6 (ε = 0,40, ≈ 0,031 par
tentative ; selon A1, p₁₆ = 0,05 → résiste 0,74, brèche 0,03, non concluant 0,23). **Option C** achète deux fois plus de
précision au même prix : W1 sous v9 est dominé par W1 sous v8 (monotonie : promotion sous v9 ⇒ promotion sous v8 sur les mêmes
issues, donc en loi), que la reprise A1-v3 mesure déjà à 24 cartes ; c'est un écart au brief (« W1 et W2 ») que seul Lazar peut
accepter. Ordre recommandé : validation du v9 (gratuite, 2 à 5 h de processeur) d'abord, l'attaque v4 ensuite.

## 11. Ce qu'une contre-lecture neuve doit vérifier en premier

1. **Le certificat** (`_certificats`, ligne `certificat = …` de `maximiser_par_lots`) : sommets du polytope (une loi connue par
   morceau avec r = 0 ; r = δ_k avec a = 0), ∇f·x = t_c exact, masque des instances hors de l'instant (m = 1, poids 0), borne par
   0 ; refaire la référence indépendante (essai scipy) sur d'autres tirages.
2. **Tout seuil réel** (`_coupes`) : s = −∞ puis chaque valeur distincte ; égalités groupées ; correspondance avec
   `selection_pari._condition` (z > s : branche « si », morceau haut) ; la mutation équivalente de la section 8.
3. **Le bruit commun** : la matrice B des contraintes (même r pour tous les morceaux) ; qu'une loi en escalier aveugle reste
   hors du nul ; si ce choix de sens (section 2.2) est le bon pour le programme — c'est une question de revendication.
4. **Élagage et fin de groupe** : la valeur d'un membre est le maximum, sur toutes les coupes, de leur meilleur certificat ;
   aucune coupe élaguée ne peut faire baisser ce maximum sous le vrai sup ; la tolérance 10⁻³ ne coûte que de la puissance.
5. **L'évaluateur** : `evaluer_sur_issues` identique à `evaluer_v2` sans morceaux (y compris les égalités) ; `sans_morceaux`
   rend membre pour membre la bibliothèque du v8 ; gardes de `evaluer_v9`.
6. **L'appariement** : le v8 apparié sur les issues du v9 a la même loi qu'une évaluation v8 (la graine des tirages dépend de
   l'empreinte, pas leur loi) ; la garde de monotonie (tolérance 10⁻⁶ due aux arrondis à 6 décimales) ; la perte comptée
   dans le bon sens.
7. **La lecture gelée** : familles de Holm (18 fatales ; 5 pertes, tests exacts sur proportions appariées), 3 artefacts
   (borne basse > α), ordre des issues, audits A1 à A5 ; refaire les tables de la section 6 du préenregistrement.
8. **La preuve et l'écart au brief** (sections 3.3 et 3.5) : le maximum garde α, le mélange a priori au dénominateur ne le garde
   pas ; le mélange a priori au numérateur (pari à fraction) est couvert ; mondes sans mémoire seulement.
9. **La puissance et la marge** : prédictions P4, P5 tirées de 100 répétitions (L3) ; la recommandation (a) de l'annexe A n'est
   pas taillée sur L3 ; la lecture « fille neuve » (section 5) ; I01 et I02 sont bien hors du v9 (aucun trait seul n'informe).
10. **La fermeture et les gardes du mode décisif** (14 fichiers ; nom `…-nul-v9-v<N>.md` dans `prereg/` ; scellement ;
    empreintes) ; les chiffres d'A1 cités au préenregistrement (section 1) sont des transcriptions non vérifiées (R7) ; la
    correction « 18 lignes sur 15 scénarios, pas 27 tricheurs ».

## 12. Nœuds ouverts pour Lazar

- Marge de perte de puissance (préenregistrement, annexe A) : recommandation (a) 0,05 partout, défaut sous 48 heures.
- Sens de « rien au-delà de l'archive » (section 2.2) : bruit commun, loi en escalier aveugle promouvable — revendication, à
  confirmer.
- Le nul de production reste le v8 (`cycle.membres_de_l_archive` inchangé) : brancher le v9 en production demande une entrée
  v9 du cycle (fichier neuf) après la validation.
- Attaque v4 : option A, B ou C (section 10), plafond 48 USD, GO de calcul.
