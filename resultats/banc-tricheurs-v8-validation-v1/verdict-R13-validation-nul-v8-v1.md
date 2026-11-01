# Verdict R13 — validation décisive du nul v8 (banc des tricheurs v8), lecture neuve, version 1

**confirmée avec réserves (listées)** — l'issue « confirmée » rendue par le code est exacte ; aucun déclencheur d'audit ; deux réserves mineures, aucune majeure (section 8) ; portée limitée à la classe du banc (section 7).

Lecteur : neuf (R13) ; je n'ai écrit ni le préenregistrement, ni le code, ni lancé la course. Je n'ai modifié aucun fichier existant, rien commité, aucun accès réseau, aucune clé ni aucun secret lu. Ce fichier est le seul fichier que j'écris dans le dépôt.

## 0. Légende (chaque sigle ou code utilisé plus bas)

| Code | Sens en clair |
|---|---|
| α, 1/α | α = 0,05 : taux d'erreur toléré. 1/α = 20 : seuil de richesse pour promouvoir une fiche (log 20 = 2,9957). |
| W, log W, « log W max » | Richesse : vraisemblance de la loi proposée par la fiche divisée par la meilleure vraisemblance de la bibliothèque « nulle » sur les mêmes issues. « log W max » : le plus grand log W parmi les 8 instants de lecture (25, 50, …, 200). |
| nul v8 / v7 / v1 | Bibliothèques de lois concurrentes : v8 = ajustée sur toutes les lois connues (parents et survivantes de l'archive) ; v7 = sans les membres ajustés sur l'archive ; v1 = plus pauvre encore (sert d'artefact : le banc doit voir passer le tricheur). |
| Marge des filles 2δ₀ | Pour une fille (fiche à deux parents A et B) : en plus de W ≥ 20 à un instant lu, le gain moyen par tirage, au dernier instant (200), doit dépasser de 2δ₀ = 0,02 nat celui de la meilleure « enveloppe » (parents, mélanges, membres ajustés). |
| Lignes fatales (11) | Tricheurs que le juge doit refuser (taux de promotion ≤ 5 %) : **T01** fille = ½ parent A + ½ loi aveugle fixe q ; **T02** fille = ½ A + ½ survivante S1 (copie cachée) ; **T03u** sans parent = ½ S1 + ½ uniforme ; **T03b** sans parent = ½ S1 + ½ q ; **T04** mélange de S1 et S2 ; **T05s** S1 tempérée et inclinée ; **T09g** A à la puissance 6 ; **T09l** 3 % A + 97 % q ; **T12a** A déformé par une oscillation, monde = A ; **T17s** copie de S1 ; **nul exact** fille = A, monde = A. |
| Artefact **T01\|v1** | T01 jugée sous l'ancien nul v1 : doit être promue (le banc a des dents). |
| Puissance | **fille neuve** (A en sous-population 0, loi neuve ailleurs) et **fraîche neuve** (loi neuve, sans parent), chacune sous v8 et sous v7 (référence). Perte = taux(v7) − taux(v8). |
| Mesurées | **T07** composition de trois étapes (hors classe couverte) ; **T12b** A déformé quand le monde est cette déformation (la fiche dit vrai). |
| H1 à H4 | Hypothèses du préenregistrement : H1 les 11 lignes fatales ≤ α ; H2 perte de puissance ≤ 0,05 sur les deux lignes de puissance ; H3 l'artefact T01\|v1 > α ; H4 le « nul exact » ≤ α (comprise dans H1). |
| A1 à A6 | Déclencheurs d'audit (section 7 du préenregistrement) : A1 une promotion sur une ligne refusée par construction ; A2 v8 plus puissant que v7 ; A3 artefact hors de [0,10 ; 0,90] ; A4 log W > 10⁻⁶ sur la classe linéaire ; A5 nul ajusté inactif (propreté suspecte, lu sur les membres dominants) ; A6 audit systématique des issues décevantes. |
| P1a à P5 | Prédictions chiffrées écrites d'avance (elles ne décident pas de l'issue). |
| CP, Holm, Newcombe | Bornes de Clopper-Pearson (exactes, proportion seule) ; correction de Holm (plusieurs tests, niveau familial 0,05) ; bornes de Newcombe (différence de deux proportions indépendantes, approchée). |

## 1. Sceaux et identité du code

- `sha256sum -c` : `preenregistrement-validation-nul-v8-v2.md` OK (`7f37631d…0de4c5`, égale à l'empreinte attendue du brief) ; `manifeste.json` OK (`06e506ab…`) ; `banc-tricheurs-v8.json` OK (`7a10f4c7…`). Le dossier contient aussi `journal-lancement-v1.txt` et `sortie-standard-v1.txt` (avec compagnons), ajoutés à 00:18 (heure de Paris) par la session principale (commit `2cfb940`) : sceaux OK, contenu identique aux copies du scratchpad (départ 22:25:14, fin 23:16:55 UTC, code 0, commit `1bad95f`).
- Graine : `manifeste.reglages.entropie_racine` = `int(sha256(octets du préenregistrement), 16)` (recalculé), supérieure à 2⁶⁴ (espace décisif disjoint de l'exploratoire). Les 18 clés de graines par ligne sont distinctes (recalcul) : les lignes v7 et v8 d'une même loi sont bien des échantillons indépendants, condition de Newcombe.
- Code : `git diff --stat 1bad95f 02ca692` = `MANIFEST.md` et `README.md` seulement (3 insertions, 2 suppressions ; texte du README sur une autre expérience). `git diff --name-only 1bad95f HEAD` (HEAD = `2cfb940`) : README, MANIFEST et le dossier de résultats ; **aucun fichier sous `orchestrator/` ni `.github/`**. Arbre de travail propre.
- Empreintes : le bloc « Empreintes du code gelé » (section 11 du préenregistrement, 12 fichiers) = `manifeste.reglages.code_du_banc_sha256` = `preenregistrement.empreintes_du_code_verifiees` du rapport (12/12 identiques) ; `sha256sum -c` du bloc sur le disque : 12 OK ; les 12 fichiers à `1bad95f` ont les mêmes empreintes ; `manifeste.code_sha256` (93 fichiers de `pole/`) = disque, 0 écart, aucun fichier en trop ni manquant.
- Environnement du manifeste : Python 3.13.18, numpy 2.5.3, 2 processus = ceux du plan. Durée 3 101,3 s = 22:25:14 → 23:16:55 UTC. Le reflog local de `origin/main` date la poussée de `1bad95f` à 22:25:07 UTC, soit 7 s avant le départ (voir réserve R2).
- Remarque de forme, sans effet : la première ligne du préenregistrement dit encore « non scellée » ; le sceau est le compagnon `.sha256` (section 13), et le fichier ne pouvait plus changer sans changer la graine.

## 2. Composantes : comptes bruts, bornes, seuils, statuts

Tout est recalculé par moi à partir de `promues / repetitions` du JSON (script indépendant, scipy : `beta.ppf` pour Clopper-Pearson, `binom.cdf` pour les valeurs p, Holm réécrit d'après le texte, Newcombe méthode 10 réécrite d'après la formule et vérifiée sur l'exemple publié 56/70 contre 48/80 : (0,0524 ; 0,3339) retrouvé). Les bornes du JSON sont retrouvées à 10⁻¹⁵ près.

### 2.1 Les 11 lignes fatales (H1, H4)

Famille de 11 lignes ; hypothèse testée pour « tenue » : H0 « taux ≥ 0,05 » contre « taux < 0,05 », valeur p = P(Bin(1 000 ; 0,05) ≤ x), Holm au niveau familial 0,05 (seuil du rang j : 0,05/(12 − j), de 0,00455 au rang 1 à 0,05 au rang 11). Pour « non tenue » : sens inverse, P(Bin ≥ x), même Holm.

| Ligne | Promues / 1 000 | Borne haute CP 95 % (unilatérale) | Valeur p « tenue » | Valeur p « non tenue » | Statut du code | Mon statut |
|---|---|---|---|---|---|---|
| T01 | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T02 | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T03u | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T03b | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T04 | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T05s | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T09g | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T09l | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T12a | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| T17s | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |
| nul exact | 0 | 0,002991 | 5,29·10⁻²³ | 1,0 | tenue | tenue |

Toutes les valeurs p sont égales (0 promotion) ; la plus grande est une vingtaine d'ordres de grandeur sous le seuil le plus strict de Holm (0,00455), donc les 11 sont rejetées à tous les rangs. Au niveau le plus strict de Holm, la borne haute de CP serait 0,00538, encore très en dessous de 0,05. Le tableau de la section 5 du préenregistrement (promotions maximales compatibles avec « tenue » : 32, 32, 32, 33, 33, 33, 34, 34, 35, 36, 38 ; minimales pour « non tenue » : 70, 70, 69, 69, 69, 68, 68, 67, 66, 65, 63) est retrouvé exactement par mon calcul. Le code rend 11 « tenue » ; **exact**.

### 2.2 Artefact (H3) : T01|v1

395 promues sur 1 000 (0,395). Borne basse de CP 95 % unilatérale = 0,3693 > 0,05, sans correction (un seul test) ; le seuil est 63 promotions (retrouvé). Code : tenue ; moi : tenue. **Exact.**

### 2.3 Pertes de puissance (H2)

Différence taux(v7) − taux(v8), échantillons indépendants, borne haute de Newcombe ; « tenue » si H0 « perte ≥ 0,05 » est rejetée par Holm sur la famille des 2 lignes (valeur p par inversion de la borne : plus petit niveau pour lequel la borne haute passe sous 0,05).

| Ligne | v7 | v8 | Perte observée | Newcombe 95 % non corrigée | Newcombe au niveau de Holm du rang 1 (0,025) | Valeur p | Seuil de Holm | Code | Moi |
|---|---|---|---|---|---|---|---|---|---|
| fille neuve | 988 | 983 | +0,005 | [−0,0040 ; +0,0143] | borne haute 0,0163 | 3,0·10⁻⁹ | 0,025 (rang 1) | tenue | tenue |
| fraîche neuve | 998 | 978 | +0,020 | [+0,0124 ; +0,0291] | borne haute 0,0312 | 9,9·10⁻⁶ | 0,05 (rang 2) | tenue | tenue |

Les deux bornes hautes sont très en dessous de 0,05 même au niveau le plus strict. Pour mémoire, avec v7 observé, il aurait fallu au moins 954 (fille neuve) et 962 (fraîche neuve) promotions sous v8 pour « tenue » au niveau 0,025. Code : 2 « tenue » ; **exact**.

### 2.4 Mesurées (sans seuil de validité)

T07 sous v8 : 16/1 000 = 0,016 (CP 95 % [0,0101 ; 0,0242]). T12b sous v8 : 903/1 000 = 0,903 (CP 95 % [0,8862 ; 0,9180]).

## 3. Déclencheurs d'audit

| Déclencheur | Règle | Valeur lue | Déclenché ? |
|---|---|---|---|
| A1 (calculé par le code) | au moins une promotion sur une ligne refusée par construction (toutes les fatales sauf T12a) | 0 promotion sur les 10 lignes (8 linéaires + T05s + T09g) | non (confirmé par moi) |
| A2 (code) | borne haute de Newcombe de la perte < 0 | +0,0143 (fille neuve) et +0,0291 (fraîche neuve) | non |
| A3 (code) | taux de T01\|v1 hors de [0,10 ; 0,90] | 0,395 | non |
| A4 (code) | log W > 10⁻⁶ sur une répétition d'une ligne de la classe linéaire | maximum des 8 lignes linéaires : −5,09·10⁻⁶ (T04) ; puis −7,49·10⁻⁶ (T02) ; les 6 autres ≤ −0,0059 (T17s −0,0060, T03b −0,0080, T03u −0,0083, nul exact −0,0224, T01 −0,0401, T09l −0,0511) | non |
| A5 (lu par moi) | nul ajusté inactif : sur T02, T03b, T04, `ajuste_lineaire:archive` domine dans moins de la moitié des répétitions ; sur T05s, `ajuste_log:archive:S1` et `ajuste_lineaire:archive` ensemble dans moins de la moitié | T02 : 965/1 000 ; T03b : 898/1 000 ; T04 : 983/1 000 ; T05s : 956 + 41 = 997/1 000 (repères de 20 répétitions : 18, 16, 19, 20 sur 20, soit 90 %, 80 %, 95 %, 100 %) | non |
| A6 | issue « infirmée » ou « non jugeable (banc sans dents) » | issue « confirmée » | sans objet |
| Seuil +0,25 de P1b (lu par moi) | log W max > +0,25 sur T05s ou T09g | T05s −0,0048 ; T09g −0,0071 | non |

Mes lectures de A1 à A4 coïncident avec `lecture.audits = []` et `issue_suspendue_par_audit = false` du rapport. Pour A5, les quatre premiers membres dominants listés totalisent 1 000/1 000 sur chacune des quatre lignes : rien n'est caché hors liste. Aucune issue n'est suspendue.

## 4. Prédictions (elles ne changent pas l'issue)

| Prédiction | Énoncé | Valeur observée | Tenue ? |
|---|---|---|---|
| P1a | 8 lignes linéaires : 0 promotion sur 1 000 et log W ≤ 0 (moins de 10⁻⁶) à chaque répétition | 0 promotion ; maximum −5,09·10⁻⁶ | oui |
| P1b | T05s et T09g : 0 promotion et log W max ≤ +0,25 | 0 promotion ; −0,0048 et −0,0071 | oui |
| P1c | T12a : au plus 10 promotions sur 1 000 | 0 | oui |
| P2 | perte dans [−0,02 ; +0,04] sur chaque ligne de puissance | +0,005 et +0,020 | oui |
| P3 | T01\|v1 promue au taux [0,30 ; 0,60] | 0,395 | oui |
| P4 | T07 ≤ 0,02 ; T12b dans [0,80 ; 0,95] | 0,016 ; 0,903 | oui (T07 : la borne haute de CP, 0,024, dépasse 0,02 ; la prédiction porte sur l'estimation) |
| P5 | puissance sous v8 ≥ 0,95 sur chaque ligne de puissance | 0,983 et 0,978 | oui |

Le champ `predictions` du JSON ne code que les comptes (pas le « log W ≤ 0 » de P1a ni le « +0,25 » de P1b) : je les ai vérifiés à la main sur `log_w_max_max`, section 3.

## 5. Issue selon la section 6 du préenregistrement

Règle appliquée dans l'ordre : aucune ligne fatale « non tenue » ; aucune perte « non tenue » ; l'artefact est « tenu » ; les 11 lignes, l'artefact et les 2 pertes sont « tenus » → **issue 4 : « confirmée »**. Aucun audit déclenché, donc aucune suspension (les audits A4 et A1 sur la classe linéaire, qui auraient invalidé la course d'office, ne sont pas déclenchés ; ni la réserve log-linéaire qui aurait interdit « confirmée »).

## 6. Point à éclaircir : T12a (0 promotion, log W max = 4,38) et T07 (16 promotions, maximum 9,31)

### 6.1 Où le code décide (lu dans le code gelé)

Dans `pole/nul_filles_v2.py`, `evaluer_v2` (lignes 190 à 241), appelée par `juger_v8` pour toute fille :

1. `log_w[i] = numérateur(t) − meilleur membre du nul à t`, pour chacun des 8 instants de lecture `instants_lecture` = 25, 50, …, 200 (n = 200 tirages d'évaluation après 50 tirages de calibrage) ; `log_richesse_max = max(log_w)` (ligne 224) : c'est le maximum **sur les 8 instants**, et non la valeur finale.
2. `promue = (il existe un instant avec log_w ≥ log 20)` (lignes 221 à 223), **puis** (lignes 232 à 237), pour une fille avec δ₀ = 0,01 : `gain = (numérateur[−1] − meilleure enveloppe[−1]) / n` et `promue = promue and gain >= 2·δ₀` (0,02 par tirage, soit au moins 4 nats d'avance sur la meilleure enveloppe à n = 200). Les membres ajustés comptent parmi les enveloppes.
3. `log_richesse_max` est calculé avant et indépendamment de la marge ; il n'est jamais remis à zéro quand la marge refuse la promotion. Une répétition peut donc rapporter log W max = 4,38 > log 20 et ne pas être promue.

Ce n'est ni un défaut ni un écart au texte : le préenregistrement le dit (section 5, première ligne : « W ≥ 1/α à un instant lu, et pour une fille la marge 2δ₀ sur la meilleure enveloppe ») ; la docstring de `pole/nul_v8.py`, point 2, et celle de `nul_filles_v2.py` aussi (« la règle de marge des filles ne fait que retirer des promotions »). La marge de Newton (≤ 0,25), elle, ne concerne que les dénominateurs log-linéaires et ne peut que diminuer W : elle n'explique rien ici.

### 6.2 Rejeu diagnostique (lecture seule) pour le constater

J'ai rejoué les lignes T12a et T07 aux graines de la course décisive, en appelant les fonctions du banc telles quelles (graines, scénario, `juger_v8`) et en conservant, pour chaque répétition, la trajectoire de log W, la marge et la meilleure enveloppe. Ce rejeu n'est pas une nouvelle course décisive, n'écrit rien dans le dépôt et ne participe pas à l'issue. **Il reproduit le rapport scellé à l'identique** : T12a : 0 promotion, `log_w_max_max` = 4,38015180017841 (égal au bit près), médiane −3,35, 99ᵉ centile 1,962, mêmes dominants ; T07 : 16 promotions, `log_w_max_max` = 9,305976229757647, médiane −0,597, 99ᵉ centile 4,791, mêmes dominants. Cela confirme aussi le déterminisme de la course.

**T12a** (fiche = A déformé, monde = A, donc fiche fausse) :

- 4 répétitions sur 1 000 franchissent log 20 à au moins un instant lu : r = 65 (log W max 4,380), r = 354 (4,355), r = 454 (3,688), r = 184 (3,372). **Aucune ne finit au-dessus du seuil**, et toutes ont un gain final négatif (−0,0047 ; −0,0107 ; −0,0760 ; −0,0085), très loin de 0,02 : la marge les arrête toutes. Le meilleur gain final de toute la ligne est −0,0047 ; la marge n'est jamais atteinte.
- La répétition r = 65, celle qui porte le maximum 4,38 : log W aux instants 25 à 200 = 0,260 ; 2,969 ; 3,516 ; 3,570 ; **4,380** ; 2,251 ; 2,163 ; −0,934. Elle franchit le seuil (2,9957) à t = 75, 100 et 125 (premier franchissement à 75), puis redescend à −0,934 à t = 200 ; meilleure enveloppe `ajuste_log:AB`, gain final −0,00467 < 0,02 : `promue = False`, et `t_promotion` est remis à `None`.
- Taux de franchissement de 1/α **sans** la marge : 4/1 000 = 0,4 % (borne haute CP 95 % : 0,91 %), sous les 5 % de Ville. Même sans la marge, T12a n'aurait pas dépassé la prédiction P1c.

**T07** (composition hors classe couverte, fiche = monde) : 35 répétitions sur 1 000 franchissent log 20 ; **16 sont promues** (gain final de 0,0201 à 0,0465 ≥ 0,02) et **19 sont arrêtées par la marge** (gain de 0,0050 à 0,0192). Le maximum 9,306 est la répétition r = 729 : elle franchit dès t = 25 (3,079) et atteint 9,306 à t = 200 (gain 0,0465) : une vraie accumulation de preuve contre le nul, à la différence des franchissements passagers de T12a.

Conclusion : l'écart « 0 promotion et log W max 4,38 » s'explique entièrement par deux règles écrites du texte : le maximum est pris sur 8 instants, la marge n'est lue qu'au dernier. Pas de défaut du code, pas d'écart au texte : **pas de réserve majeure**. Seule la lisibilité du rapport scellé est en cause (réserve R1).

## 7. Symétrie (R4) : rien de suspect de propreté

« Tout tenu » ne rend pas le résultat propre pour autant (section 7 du préenregistrement) ; ce que j'ai regardé :

1. **Le 0/1 000 vient-il du nul ajusté ?** Oui, trois preuves.
   - *Membres dominants* : sur les 11 lignes fatales, tous les membres dominants listés au dernier instant sont des membres ajustés (`ajuste_*`), jamais un membre ordinaire : 10 939 répétitions listées sur 11 000 (les 61 non listées, hors des quatre premiers membres rapportés : 58 sur T09l, 2 sur T12a, 1 sur T01). Les quatre lignes qui motivent le nul ajusté sont dominées par le bon membre (A5, section 3).
   - *Contrôle apparié (le mien, complémentaire, hors critères gelés, 60 répétitions par ligne)* : mêmes scénarios (graines des lignes « nom\|v8 »), nul v7 au lieu de v8 : T02 49/60, T03b 48/60, T04 56/60, T05s 50/60 promues, avec un log W max (maximum sur les 60 répétitions) de 35 à 48 ; sous v8, les mêmes 60 scénarios : 0/60 sur chacune, dominées par `ajuste_lineaire:archive` (T02 59/60, T03b 53/60, T04 58/60) ou `ajuste_log:archive:S1` (T05s 57/60). Ce n'est donc pas un scénario dégénéré ni un banc qui ne promeut jamais : le zéro vient bien de l'archive ajustée.
   - *Lignes qui promeuvent* : puissance 98,3 % et 97,8 % sous v8, T12b 90,3 %, T01\|v1 39,5 % (banc v7 publié : 90/200 = 45 %, compatible), T07 1,6 % hors classe. L'instrument promeut là où il doit et pas ailleurs.
2. **Limite connue, non dissimulée** : dans cette course, la seule ligne qui montre les « dents » (H3) est T01\|v1, que le nul v7 suffirait à refuser sans membre d'archive. Les quatre tricheurs qui exigent les membres ajustés sur l'archive (T02, T03b, T04, T05s) n'ont pas de contrôle positif dans la course décisive elle-même ; leur contrôle positif est dans le banc v7 (200 répétitions : 75 %, 85 %, 95 %, 80,5 % sous le nul v7) et dans mon contrôle apparié ci-dessus (80 % à 93 % sous v7). Ce n'est pas un défaut du plan écrit (H3 est écrite pour T01\|v1) ; c'est ce que A5 remplace.
3. **Classe linéaire** (8 lignes × 1 000 = 8 000 répétitions) : log W max toujours strictement négatif, maximum −5,09·10⁻⁶. Les valeurs de T02 et T04 (99ᵉ centile « −0,0 », maximum à quelques 10⁻⁶) sont du même ordre que l'écart toléré de l'optimiseur (au plus 10⁻⁵, ajouté au dénominateur) : c'est ce qu'on attend d'une loi qui est exactement un membre du nul ; je n'y vois rien d'anormal.
4. **Classe log-linéaire** : T05s et T09g restent négatifs sur 1 000 répétitions (maximum −0,0048 et −0,0071) ; la marge de Newton admise (+0,25) n'est jamais approchée. Les ajustements log-linéaires non convergés (qui prendraient la borne triviale 0 et rendraient le résultat artificiellement propre) ne dominent pas : `ajuste_log:archive:S1` domine 956/1 000 sur T05s et `ajuste_log:AB` 998/1 000 sur T09g.
5. **T12a** : log W max jusqu'à 4,38 et franchissements passagers (section 6) : cette ligne n'est pas « trop propre », elle bouge comme une ligne soumise à la borne de Ville.
6. **Prédictions toutes tenues** : elles ont été écrites après les lectures préalables L0 à L12 (même code, autres graines), ce que la section 9 déclare. Leur réussite était attendue et n'ajoute aucune preuve ; ce sont les comptes scellés qui décident.
7. Sorties inattendues cherchées et non trouvées : aucune répétition à richesse non finie (la course l'aurait arrêtée), aucune ligne dupliquée, aucune clé de graine en collision, instants de lecture de `instants_reguliers(200, 8)` = 25 … 200 pour les fiches sans parent comme pour les filles, membres ajustés vérifiés par la garde `exiger_membres_ajustes` à chaque évaluation (la course n'a pas levé `NulV8Refuse`).

## 8. Réserves

Aucune réserve majeure. Deux réserves mineures, sans effet sur l'issue :

- **R1 — Lecture du rapport scellé (T12a).** Le rapport ne donne pas le nombre de répétitions qui franchissent 1/α indépendamment de la marge des filles ; « 0/1 000 avec log W max = 4,38 » n'est lisible qu'en connaissant la règle de marge. Mon rejeu : 4/1 000 franchissements, tous arrêtés par la marge. La phrase « seule T12a éprouve la borne probabiliste de Ville » (section 6, issue 4) doit se lire : T12a éprouve la borne **jointe à la marge** ; le franchissement seul (0,4 %, borne haute 0,91 %) reste sous 5 %. À répéter tel quel dans le README si T12a y est citée.
- **R2 — Procédure avant la course (section 13).** Le texte demande, après la poussée du commit et avant la course, de rejouer les 35 essais et le banc de mutations « sur l'arbre scellé ». Le reflog local de `origin/main` date la poussée à 22:25:07 UTC et le départ est à 22:25:14 UTC : 7 s, trop court pour ce rejeu, et je n'en trouve aucune trace dans le dépôt. Atténuant : un lecteur neuf a fait passer les 35 essais (34 s, 35 réussis) sur l'arbre de la v2 avant scellement, et les 12 fichiers de code sont identiques à l'octet ; la course est refusée par le banc si le code diffère. À confirmer ou à consigner comme écart de procédure par la session principale ; l'issue n'en dépend pas (ce n'est ni un critère gelé ni une garde du banc).

Note sans réserve : le dossier de sortie s'appelle `…-validation-v1` alors que le fichier scellé est la v2 ; c'est écrit dans le texte (sections 4 et 12), à ne pas confondre.

## 9. Portée exacte (section 10 du préenregistrement) : rien hors de la classe du banc

Ce que la course établit : sur les mondes synthétiques du banc (3 issues, 2 traits, 2 sous-populations ; filles : 50 tirages de calibrage puis 200 d'évaluation ; fiches sans parent : 200 tirages ; lecture aux instants 25 à 200 ; marge 2δ₀ = 0,02 ; α = 0,05 ; 1 000 répétitions par ligne), le nul v8 ne promeut aucune des 11 lignes fatales au-dessus de α (borne haute de CP 0,3 % par ligne, Holm) ; il a vu l'artefact que l'ancien nul laisse passer (39,5 %) ; et il coûte au plus 2,0 points de puissance observés (borne haute de Newcombe 3,1 points au niveau de Holm) sur deux lignes à **effet fort** (puissance 98 %). Dix des onze lignes vérifient log W ≤ 0 à chaque répétition (8 000 + 2 000 répétitions) ; seule T12a éprouve Ville (et la marge, R1). Mention autorisée pour le nul v8 : « validé sur la classe du banc (section 10) ».

**Classe couverte** : recombinaisons linéaires de lois connues (chaque loi seule, tout mélange de parents et de survivantes, avec ou sans loi aveugle fixe) ; recombinaisons log-linéaires d'une loi connue (survivante ou parent tempéré et incliné ; pour une fille, produit des deux parents tempéré et incliné).

**Non couvert, non revendiqué** : recombinaisons par morceaux avec une survivante (si/sinon par sous-population ou seuil d'un trait), poids de mélange dépendant de l'instance ; produits de plus de deux lois ou de deux lois autres que les deux parents ; compositions d'étapes (T07 : mesurée, 1,6 % ; elle n'est pas fermée, borne haute 2,4 %) ; déformations non monotones (T12 : T12a est refusée au sens de la course, T12b est de la puissance sur la nouveauté, 90,3 %) ; lois hors de l'archive. **Hors validation** : la multiplicité entre fiches (règle e-BH, lignes T14 à T16 du banc v7, non rejouées) ; la puissance à effet faible ; la banque réelle. La réserve sur les membres log-linéaires (marge de Newton non démontrée) subsiste en théorie ; elle n'a pas été éprouvée par cette course (écart maximal −0,0048 et −0,0071, jamais d'effet de la marge).

Usage (section 6, dernier alinéa) : issue « confirmée » → le nul v8 reste le seul nul du juge ; le README peut dire sa validation avec la portée ci-dessus.

## 10. Traçabilité de mon travail

- Aucun fichier du dépôt modifié ; aucun commit ; aucun accès réseau ; aucune clé lue. Le `__pycache__` de `orchestrator/pole/` date de 20:49 la veille (non créé par moi ; mes exécutions utilisaient `python3 -I -B`).
- Lu en entier : le brief, le préenregistrement v2 (sections 1 à 13), `banc-tricheurs-v8.json`, `manifeste.json`, `demonstrations/banc_tricheurs_v8.py`, `banc_tricheurs_v7.py`, `pole/nul_v8.py`, `pole/nul_filles_v2.py`, `pole/selection_pari.py` (évaluation, tirages frais), `pole/cycle.py` (`membres_de_l_archive`, `instants_reguliers`). J'ai lu le rapport de relecture du diff v1 → v2 pour la seule question de la section 13 (R2). Je n'ai pas ouvert les rapports de contre-lecture du préenregistrement ni les scripts de recalcul d'autres sessions du scratchpad.
- Scripts et sorties (hors dépôt, dans le scratchpad) : `/tmp/claude-0/-home-claude/730d0294-0b2b-55ca-8b32-49f2d3ec072d/scratchpad/R13/recalcul.py` (recalcul indépendant des décisions, sections 2 à 4), `rejeu_ligne.py` et `analyse_rejeu.py` (rejeu de T12a et T07, section 6), `controle_apparie.py` (contrôle v7 contre v8, section 7), sorties dans `rejeu/` et `controle_apparie.txt` du même dossier.
