# Préenregistrement — validation décisive du nul v8 du juge (banc des tricheurs v8), v2

Statut : **version 2, après contre-lecture (R2) ; non scellée.** La version 1 (`preenregistrement-validation-nul-v8-v1.md`,
sha256 `894b294b2a3d3eb455ff77e709695026795e6d67199e94f2a905491cddf2d4b4`) est gardée telle que le contre-lecteur l'a lue ; elle
n'est pas scellée et ne le sera pas. Cette version intègre les corrections C1 à C15 du rapport de contre-lecture (section 12).
Rédigée le 1er novembre 2026 vers 22:30 UTC par l'auteur de la v1. Le scellement est l'écriture, par le directeur, du compagnon
`preenregistrement-validation-nul-v8-v2.md.sha256` (format de `sha256sum`) à côté de ce fichier, committé avec lui et les
fichiers de la section 13. **Le premier scellement est contraignant** : la graine décisive est l'empreinte du fichier scellé
(section 4) ; tout rescellement change la graine et reste visible dans l'historique public du dépôt ; la règle « un scellement,
une course » est écrite en section 4. Aucune course décisive avant le scellement (R1) : le banc la refuse
(`PreenregistrementNonScelle`). Si le code gelé (section 11) change avant le scellement, le bloc d'empreintes est recalculé
(commande en section 11) avant de sceller.

Fichiers à donner au lecteur neuf du diff v1 → v2 : la v1, cette v2, le rapport de contre-lecture
(`contre-lecture-prereg-nul-v8-v1.md`, section 12) ; pour vérification au besoin : `pole/nul_v8.py`,
`demonstrations/banc_tricheurs_v8.py`, `essais/test_v58_nul_v8.py`.

## 1. Objet et motivation

Décision du directeur (1er novembre 2026) : le nul d'archive **ajusté** devient le seul nul du juge, partout, en version
nouvelle (v58 de l'orchestrateur ; nul « v8 », `pole/nul_v8.py`). Ce préenregistrement fixe sa validation décisive.

**Motivation seulement (ce n'est pas une preuve de ce qui est testé ici)** : le banc v7 à 200 répétitions,
`../resultats/banc-tricheurs-v7-2026-11-01/banc-tricheurs-v7.json`, sha256
`2fc037b4eda23cf6b36e038c2034c53e6de4625f07308159a896ad04c808ca3c` : sans le nul ajusté, quatre tricheurs par recombinaison
de survivantes battent le juge (T02 75 %, T03b 85 %, T04 95 %, T05s 80,5 % de promotion) ; avec lui (réglage « candidat »),
0/200 chacun ; perte de puissance −0,03 (fille neuve) et +0,01 (fraîche neuve). Le nul v8 est ce « candidat » rendu par la
fonction du juge de production : mêmes membres, membre à membre, et mêmes évaluations aux mêmes graines (essais
`MembresNulV8.test_identiques_au_candidat_du_banc_v7` et `JugeSousNulV8.test_juge_v8_identique_au_banc_v7_aux_memes_graines`
de `essais/test_v58_nul_v8.py`).

Argument de validité (docstring de `pole/nul_v8.py`, résumé) : élargir la bibliothèque de nuls ajustée sur les tirages frais
ne peut que réduire la richesse W_t (à issues égales, W_t(v8) ≤ W_t(v7) ; donc, en loi pour un même monde,
taux(v8) ≤ taux(v7)) ; si la loi du monde est dans une famille du nul, W_t reste sous un rapport de vraisemblance, martingale
positive d'espérance 1, et Ville borne la promotion par α (inférence universelle, rapport de vraisemblance scindé :
Wasserman, Ramdas et Balakrishnan, 2020). Les membres ajustés le sont **sur les issues mêmes où le numérateur est évalué**
(pas de part séparée pour le nul) ; la condition de l'inférence universelle porte sur le numérateur, gelé avant les tirages :
elle est respectée. Réserve dite : pour les membres log-linéaires, la marge de Newton ajoutée borne l'écart à l'optimum au
second ordre seulement (pas de preuve pour le logit multinomial). Ce que le banc mesure, l'argument ne le remplace pas : le
prix en puissance, et le comportement réel du code.

## 2. Hypothèse

Sous le nul v8 du juge (banc `demonstrations/banc_tricheurs_v8.py`, mondes et tricheurs du banc v7 : K = 3 issues, 2 traits,
2 sous-populations ; filles : 50 tirages de calibrage puis 200 d'évaluation ; fiches sans parent : 200 tirages ; lecture
aux instants 25, 50, …, 200 ; marge des filles 2δ₀ = 0,02 ; ordre d'exécution secret ; α = 0,05), **H** est la conjonction :

- **H1 (validité)** : chacune des 11 lignes fatales est promue au taux ≤ α = 0,05 ;
- **H2 (prix en puissance)** : la perte de puissance, taux(v7) − taux(v8), est ≤ 0,05 sur « fille neuve » et sur « fraîche
  neuve » ;
- **H3 (dents du banc)** : l'artefact T01|v1 est promu au taux > α ;
- **H4 (nul exact)** : la ligne « nul exact » est promue au taux ≤ α (elle appartient aux 11 lignes de H1, dite à part).

Lignes (A, B : parents ; S1, S2 : survivantes de l'archive ; N : loi neuve ; toutes softmax tirées au hasard ; q : loi
aveugle tirée de Dirichlet ; le monde de chaque tricheur est sa propre loi, sauf mention) :

| ligne | genre | loi de la fiche | monde | classe sous v8 | rôle |
|---|---|---|---|---|---|
| T01 | fille | ½A + ½q | = fiche | linéaire (membre linéaire des parents) | fatale |
| T02 | fille | ½A + ½S1 (copie cachée) | = fiche | linéaire (`ajuste_lineaire:archive`) | fatale |
| T03u | sans parent | ½S1 + ½uniforme | = fiche | linéaire | fatale |
| T03b | sans parent | ½S1 + ½q | = fiche | linéaire | fatale |
| T04 | sans parent | π·S1 + (1 − π)·S2, π ∈ [0,3 ; 0,7] | = fiche | linéaire | fatale |
| T05s | sans parent | S1 tempérée et inclinée | = fiche | log-linéaire (`ajuste_log:archive:S1`) | fatale |
| T09g | fille | A à la puissance 6 | = fiche | log-linéaire (`ajuste_log:A`) | fatale |
| T09l | fille | 0,03·A + 0,97·q | = fiche | linéaire | fatale |
| T12a | fille | A déformé (oscillation sur un trait) | A | hors classe ; le monde est au nul (Ville) | fatale |
| T17s | sans parent | S1 recopiée | = fiche | linéaire (`archive:S1`) | fatale |
| nul exact | fille | A | A | linéaire (`parent:A`) | fatale |
| T01\|v1 | fille | ½A + ½q, jugée sous le nul v1 (sans membres ajustés ni archive) | = fiche | — | artefact requis |
| fille neuve | fille | A en sous-population 0, N ailleurs | idem | — | puissance (v8 et v7) |
| fraîche neuve | sans parent | N | N | — | puissance (v8 et v7) |
| T07 | fille | composition (mélange aveugle, puissance, inclinaison de A) | = fiche | hors classe | mesurée |
| T12b | fille | A déformé (oscillation) | = fiche | nouveauté : la fiche dit vrai | mesurée |

## 3. Prédictions chiffrées et signées

Écrites avant la course décisive, à partir du banc v7 publié (section 1) et des lectures préalables déclarées (section 9).
Rapportées par le banc (`lecture.predictions`) ; **elles ne changent pas l'issue**, que seuls les critères des sections 6 et 7
décident.

- **P1a** (signe : sous α) : chacune des 8 lignes fatales de la classe linéaire (T01, T02, T03u, T03b, T04, T09l, T17s, nul
  exact), refusées par construction : **0 promotion sur 1 000**, et log W ≤ 0 (aux arrondis près, moins de 10⁻⁶) à chaque
  répétition.
- **P1b** (signe : sous α, confiance moindre) : T05s et T09g, de la classe log-linéaire, où le refus tient à la marge de
  Newton, non démontrée (section 1) : **0 promotion sur 1 000** attendue, et log W max ≤ +0,25 (marge de Newton maximale admise
  par le code). Repère : −0,04 et −0,03 sur 20 répétitions (L8). Une promotion, ou un log W max au-dessus de +0,25, déclenche
  l'audit de la section 7 (conséquences en section 7).
- **P1c** : T12a (la vérité est au nul, la fiche est hors classe) : **au plus 10 promotions sur 1 000** (taux ≤ 0,010). Risque
  dit : la borne de Ville n'impose que 5 % ; si T12a dépasse 38 promotions, « non jugeable » ou « non tenue » est l'issue
  honnête (section 5).
- **P2** (signe : perte ≥ 0 en espérance, par la monotonie de la section 1) : perte observée dans **[−0,02 ; +0,04]** sur
  chacune des deux lignes de puissance.
- **P3** (signe : au-dessus de α) : T01|v1 promue au taux **[0,30 ; 0,60]**.
- **P4** (mesures, sans seuil de validité) : T07|v8 au taux **≤ 0,02** ; T12b|v8 dans **[0,80 ; 0,95]**.
- **P5** : puissance sous v8 **≥ 0,95** sur chacune des deux lignes de puissance.

## 4. Plan d'analyse

- **Pourquoi un banc v8.** Le banc v7 (`banc_tricheurs_v7.py`, chargé en instance propre et inchangé pour ses scénarios) ne
  peut ni dériver sa graine de l'empreinte d'un fichier scellé (il dérive ses graines par SHA-256, sans `SeedSequence`) ni
  juger sous le nul de production (ses membres d'archive « candidat » sont une copie locale) ; `banc_tricheurs_v8.py` le fait,
  et les essais `MembresNulV8.test_identiques_au_candidat_du_banc_v7` et
  `JugeSousNulV8.test_juge_v8_identique_au_banc_v7_aux_memes_graines` garantissent l'identité avec le candidat du banc v7.
- **Lignes et répétitions** : les 18 lignes de la section 2 (11 fatales sous v8, l'artefact T01|v1, 4 lignes de puissance —
  fille neuve et fraîche neuve sous v8 et sous v7 —, 2 mesurées), **1 000 répétitions indépendantes par ligne**, scénario
  tiré à neuf à chaque répétition. Lignes v7 et v8 d'une même loi : échantillons indépendants (graines différentes).
- **Graine (R9), règle exacte** :
  1. entropie racine E = l'empreinte SHA-256 des **octets** du fichier scellé `orchestrator/prereg/preenregistrement-
     validation-nul-v8-v2.md` (ce fichier, tel que committé avec son compagnon `.sha256` conforme), ses 32 octets lus comme
     un **entier non signé gros-boutiste** de 256 bits — en Python `int(hashlib.sha256(octets).hexdigest(), 16)` ;
  2. répétition r ∈ {0, …, 999} de la ligne d'identifiant « nom|nul » (par exemple « T02|v8 », « fille_neuve|v7 ») :
     `numpy.random.SeedSequence(entropy=E, spawn_key=(c, r))`, où c est l'entier gros-boutiste des 4 premiers octets de
     SHA-256(« nom|nul » encodé en UTF-8) ;
  3. `.spawn(3)` : trois enfants, dans l'ordre scénario, noyau, tirages frais ; chacun est réduit à l'entier de 128 bits
     s₀ + 2⁶⁴·s₁, où (s₀, s₁) = `generate_state(2, dtype=numpy.uint64)` ;
  4. le scénario (lois, monde, marginale d'entraînement, instances) est tiré par `random.Random(graine scénario)` ; le juge
     de production dérive ensuite l'ordre d'exécution secret de la graine noyau et les tirages frais de la graine tirages
     frais et de l'empreinte de l'engagement gelé (`outils.graine_derivee`, inchangé).
  Le banc calcule lui-même E à partir du fichier (option `--preenregistrement`) ; aucune graine n'est tapée à la main.
- **Un scellement, une course décisive.** Aucune course en mode décisif n'a été lancée, sur aucune version de ce fichier
  (vérifié avant scellement : aucun dossier `resultats/banc-tricheurs-v8-validation-v1*`, aucun compagnon `.sha256`). La course
  décisive n'est lancée qu'après la poussée, dans l'historique public, du commit qui contient ce fichier, son compagnon
  `.sha256` et les 12 fichiers de code gelés (section 13). Toute course décisive dont le manifeste a été écrit est rapportée,
  qu'elle aille à son terme ou non. Si elle a rendu une issue (code 0 ou 1), cette issue fait foi : modifier ce fichier, le
  resceller (nouvelle graine) et rejouer n'est pas admis ; une reprise passe par un préenregistrement de version nouvelle (R12)
  qui cite la première course, son dossier et son empreinte. Un arrêt sans taux lu (code 3) autorise le rejeu de la section 8,
  et lui seul.
- **Garantie que la graine décisive diffère de toute lecture préalable** : (i) E est l'empreinte d'un fichier qui n'existe
  scellé qu'après la contre-lecture : aucune course antérieure n'a pu l'utiliser ; (ii) le banc n'accepte en mode
  exploratoire que des graines dans [0 ; 2⁶⁴[ et **refuse une entropie décisive inférieure à 2⁶⁴** (`EcartAuPlan`) : les
  deux espaces sont disjoints par construction (gardes éprouvées : essais `test_refus_du_banc_avant_toute_course`,
  `test_artefacts_preenregistrement` ; mutations « espace exploratoire non borné » et « entropie décisive dans l'espace
  exploratoire acceptée », tuées). Toutes les lectures de la section 9 ont une entropie < 2⁶⁴.
- **Code gelé** : le bloc de la section 11 gèle l'empreinte de chacun des 12 fichiers que la course importe (fermeture des
  imports mesurée par l'essai `test_fichiers_geles_couvrent_les_imports`) ; le banc refuse la course si un fichier manque au
  bloc ou diffère de son empreinte gelée.
- **Environnement de la mesure** : Python 3.13.18, numpy 2.5.3, 2 cœurs partagés ; le manifeste de la course consigne les
  versions et les empreintes de tout le code du pôle (pas l'identifiant de commit : il est noté dans le rapport, section 13).
  Un autre environnement n'arrête pas la course ; il est dit dans le rapport.
- **Commande exacte** (depuis `orchestrator/`, dossier de sortie neuf) :

  ```
  python3 -I -B demonstrations/banc_tricheurs_v8.py ../resultats/banc-tricheurs-v8-validation-v1 \
      --preenregistrement prereg/preenregistrement-validation-nul-v8-v2.md --repetitions 1000 --processus 2
  ```

  Sortie : `manifeste.json` (écrit avant la course) et `banc-tricheurs-v8.json` (résultats et lecture), chacun avec son
  compagnon `.sha256` ; le code de sortie dit 0, 1, 2 ou 3 (docstring du banc) mais **ne décide pas** : 0 et 1 comparent les
  taux observés à α (estimations ponctuelles, indicateur pour l'intégration continue) ; seule la lecture gelée
  (`lecture.issue`, section 6 : bornes de Clopper-Pearson et de Newcombe, correction de Holm), complétée par les audits de la
  section 7, décide. Un code 0 n'est pas « confirmée » (par exemple T12a à 4 % rend 0 et « non jugeable »). Les comptes ne
  dépendent pas du nombre de processus (essai `test_resultats_independants_du_nombre_de_processus`).
- **Durée estimée sur 2 cœurs (mesure)** : la course complète à 20 répétitions par ligne (graine exploratoire 7, déjà lue :
  section 9, L2 et L8) a pris **20,1 s** sur 2 processus (charge moyenne de la machine 2,5 à 2,8 pendant la mesure ; somme des
  durées par ligne 38,8 s). Durée par répétition × 1 000, ordonnancement simulé du réservoir de 2 processus dans l'ordre du
  plan : **≈ 1 000 s, soit ≈ 17 minutes** ; la même course jouée par l'agent précédent sous un partage plus lourd (49,3 s à
  20 répétitions) donne **≈ 41 minutes**. Attendu : **17 à 55 minutes** selon la charge de la machine (rejeu de L8 par le
  contre-lecteur sous charge : 63,2 s à 20 répétitions, soit ≈ 53 minutes) ; arrêt à 3 heures (section 8).

## 5. Métriques

- **Taux de promotion** d'une ligne = promotions / répétitions ; une promotion est la décision du juge de production
  (`nul_filles_v2.evaluer_v2` ; `selection_pari.evaluer` pour la référence v7 des fiches sans parent) : W ≥ 1/α à un instant
  lu, et pour une fille la marge 2δ₀ sur la meilleure enveloppe.
- **Bornes d'une proportion seule : Clopper-Pearson (exactes), unilatérales à 95 %** ; valeurs p par le **test binomial
  exact unilatéral** (une valeur p ≤ a ⇔ la borne de Clopper-Pearson de niveau a franchit le seuil).
- **Lignes fatales (H1, H4)** : famille = les 11 lignes fatales sous v8. Pour la décision « tenue », hypothèses nulles
  H0ᵢ : « taux de la ligne i ≥ α », contre « taux < α » (unilatérales, vers le bas) ; valeur p = P(Bin(1 000 ; α) ≤ xᵢ) ;
  procédure de **Holm** au niveau familial 0,05. Pour la décision « non tenue », dans l'autre sens, H0'ᵢ : « taux ≤ α »,
  contre « taux > α » ; valeur p = P(Bin(1 000 ; α) ≥ xᵢ) ; Holm au niveau familial 0,05 sur la même famille.
- **Nombre maximal de promotions sur 1 000 compatible avec « tenue » après Holm** (rang de la ligne dans l'ordre croissant des
  valeurs p ; seuil de Holm du rang j : 0,05/(12 − j)) — calculé par `promotions_max_tenue(1000, 11)`, vérifié par l'essai
  `test_seuils_de_holm_a_1000_repetitions`, par un calcul indépendant de l'auteur avec scipy et par le contre-lecteur
  (rapport, partie B) :

  | rang | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | promotions max (« tenue ») | 32 | 32 | 32 | 33 | 33 | 33 | 34 | 34 | 35 | 36 | 38 |
  | promotions min (« non tenue ») | 70 | 70 | 69 | 69 | 69 | 68 | 68 | 67 | 66 | 65 | 63 |

  Lecture : **toute ligne à 32 promotions ou moins est tenue quelles que soient les autres** ; 38 est le plafond absolu, pour
  la ligne de rang 11 si les dix autres sont tenues ; de 33 à 69 environ, « non jugeable » est possible.
- **Perte de puissance (H2)** : Δ = taux(v7) − taux(v8), échantillons indépendants. **Le critère porte sur une borne de la
  différence, pas sur l'estimation** : borne de **Newcombe** (méthode 10, score hybride bâti sur les intervalles de Wilson ;
  approchée, non exacte ; niveau réel mesuré par simulation par le contre-lecteur : 0,021 à 0,026 pour 0,025 nominal, 0,044 à
  0,051 pour 0,05). Famille = les 2 lignes de puissance. « Tenue » : H0 « Δ ≥ 0,05 » rejetée par Holm au niveau familial 0,05
  (valeur p unilatérale par inversion de la borne haute de Newcombe) ; « non tenue » : H0 « Δ ≤ 0,05 » rejetée par Holm.
  Exemples (nombre minimal de promotions sous v8 pour « tenue », garanti au niveau 0,025 / au mieux au niveau 0,05) : v7 à
  1 000/1 000 → 964 / 962 ; v7 à 990 → 956 / 953 ; v7 à 970 → 939 / 936 (perte maximale observée compatible ≈ 0,031 à 0,038).
- **Artefact (H3)** : **borne basse** de Clopper-Pearson unilatérale à 95 % > α → « tenue », soit **au moins 63 promotions
  sur 1 000** ; borne haute < α → « non tenue » ; sinon « non jugeable ». Un test, sans correction.
- **Conclusion d'ensemble** : test intersection-union — « confirmée » exige que chaque composante soit tenue, chacune à son
  niveau ; Holm, conservateur pour cette conclusion, sert aux conclusions ligne par ligne.
- Rapportés sans critère de la lecture gelée (mais lus par les audits A4, A5 et la règle P1b de la section 7) : médiane, 99ᵉ
  centile et maximum de log W max par ligne, membres dominants à l'instant final (quatre premiers par ligne), bornes de
  Newcombe à 95 % non corrigées de chaque perte, taux des lignes mesurées.

## 6. Critères de lecture gelés et issues écrites d'avance

Par composante (calculé par `lire_v8`, code gelé) : **tenue / non tenue / non jugeable (précision insuffisante)**, selon la
section 5. Issue de la course complète calculée par le code, dans cet ordre de priorité, **avant** les conséquences des
audits (section 7), qui peuvent l'invalider ou la remplacer :

1. **« infirmée (validité) »** — une ligne fatale au moins est non tenue. Lecture : le nul v8 ne ferme pas cette ligne ; il
   n'est pas validé ; la ligne est ouverte et nommée ; toute réparation est une version nouvelle, avec un préenregistrement
   nouveau.
2. **« infirmée (puissance) »** — aucune ligne fatale non tenue, une perte de puissance au moins non tenue. Lecture : le nul v8
   ferme les lignes mais coûte plus de 0,05 de puissance sur une loi vraiment neuve ; décision au directeur (accepter le prix
   ou changer le nul : version nouvelle).
3. **« non jugeable (banc sans dents) »** — rien d'infirmé, mais l'artefact T01|v1 n'est pas tenu. Lecture : le banc n'a pas
   vu le tricheur que l'ancien nul laisse passer ; aucune conclusion sur le nul v8 ; réparer le banc (version nouvelle,
   préenregistrement nouveau).
4. **« confirmée »** — les 11 lignes fatales, l'artefact et les 2 pertes tenus. Lecture : sur les mondes synthétiques du banc
   (K = 3 issues, 2 traits), aucune des 11 lignes fatales n'est promue au-dessus de α (bornes de Clopper-Pearson, Holm) ; le
   banc a vu l'artefact qu'il doit voir ; et le nul v8 ne coûte pas plus de 0,05 de puissance sur les deux lignes de puissance,
   **qui sont à effet fort** (puissance attendue ≥ 0,95, P5). Dix des onze lignes fatales vérifient l'inégalité « log W ≤ 0 »
   de leur classe (exacte pour la classe linéaire, à la marge de Newton près pour la classe log-linéaire) ; seule T12a éprouve
   la borne probabiliste de Ville. Le nul v8 peut porter la mention « validé sur la classe du banc (section 10) » ; rien n'est
   revendiqué hors de cette classe, ni sur la puissance à effet faible, ni sur la multiplicité entre fiches, ni sur la banque
   réelle.
5. **« non jugeable (précision insuffisante) »** — aucun des cas précédents. Lecture : on rapporte, on ne conclut pas ; aucun
   complément de répétitions sur la même graine ; une nouvelle course passe par un préenregistrement nouveau.

Tout audit déclenché (section 7) **suspend l'issue** (`issue_suspendue_par_audit` pour A1 à A4, calculés par le code ; A5, A6
et la règle P1b, lus par le contre-lecteur du verdict) jusqu'à l'audit écrit.

Usage du nul v8 (C12, règle appliquée par la session au vu de la décision du directeur citée ci-dessous) : l'issue gouverne la mention « validé » du nul v8, non son usage. La
décision de Lazar du 1er novembre 2026, 20:59 heure de Paris (« le nul ajusté devient le seul nul du juge, en version
nouvelle »), est déjà en vigueur. En conséquence :

- **« confirmée »** : le nul v8 reste le seul nul du juge ; le README dit sa validation, avec sa portée (section 10) ;
- **« infirmée »** (validité ou puissance) : le nul v8 reste le réglage par défaut jusqu'à une version nouvelle, puisque rien
  n'indique qu'un nul plus petit serait plus sûr (par la monotonie de la section 1, il ne promeut pas plus que le nul v7, en probabilité pour un même monde) ;
  le README annonce l'infirmation et le retour au banc sous un préenregistrement nouveau ;
- **« non jugeable »** (quelle qu'en soit la cause ; une course invalidée par un audit, qui ne rend aucune issue, est traitée comme non jugeable pour l'usage) : comme « infirmée », avec une
  reprise sous un préenregistrement nouveau.

Dans tous les cas, aucune promotion obtenue sous le nul v8 n'est revendiquée comme validée au-delà de ce que le banc éprouve.

## 7. Audit de symétrie (R4), écrit d'avance

Déclencheurs symétriques — une issue trop belle est auditée comme une issue trop laide. A1 à A4 sont calculés par le code gelé
(`lecture.audits`) ; A5, A6 et le seuil +0,25 de P1b sont lus dans le rapport par le contre-lecteur du verdict (R13), sans
calcul nouveau :

- **A1** — au moins une promotion sur une ligne refusée par construction (toute ligne fatale sauf T12a). Classe linéaire :
  impossible si l'argument et le code sont justes ; classe log-linéaire : désigne la marge de Newton (réserve de la
  section 1).
- **A2** — nul v8 **plus puissant** que v7 sur une ligne de puissance (borne haute de Newcombe de la perte, 95 % unilatérale non
  corrigée, < 0) : contraire à la monotonie (vraie trajectoire par trajectoire à issues égales, donc en loi pour un même monde).
  Les deux échantillons étant indépendants, ce déclencheur peut se produire par hasard (de l'ordre de 5 % par ligne sous un nul
  correct ; déjà vu sur le banc v7 publié de la section 1, fille neuve : borne haute −0,010). Trop beau, donc audité ; sans
  défaut trouvé, l'issue n'est pas changée.
- **A3** — taux de l'artefact hors de [0,10 ; 0,90] : trop bas (le banc perd ses dents) comme trop haut (le scénario a
  changé) déclenche l'audit.
- **A4** — log W > 10⁻⁶ sur une répétition d'une ligne de la classe linéaire (où log W ≤ 0 par construction, aux arrondis
  flottants près, de l'ordre de 10⁻¹³) : défaut du code, même sans promotion.
- **A5** — nul ajusté inactif (propreté suspecte : un 0/1 000 qui ne viendrait pas du nul ajusté). Lu sur les membres dominants
  à l'instant final (`dominants` du rapport, quatre premiers de chaque ligne) : sur T02, T03b et T04, si
  `ajuste_lineaire:archive` domine dans moins de la moitié des répétitions ; sur T05s, si `ajuste_log:archive:S1` et
  `ajuste_lineaire:archive` ensemble dominent dans moins de la moitié des répétitions. Repère : sur 20 répétitions (L8), ces
  membres dominent 18/20, 16/20, 19/20 et 20/20. Audit : les survivantes S1 et S2 étaient-elles dans l'archive de la fiche,
  les membres ajustés construits, les instants de lecture respectés ?
- **A6** — toute issue « infirmée (validité) », « infirmée (puissance) » ou « non jugeable (banc sans dents) » : même audit,
  avant la lecture de l'issue (R4 : une issue décevante est auditée comme une issue trop belle). Un défaut du code ou du banc
  trouvé rend la course invalide ; sinon l'issue est lue, la note jointe.

Audit : note écrite (cause cherchée, vérifications faites, conclusion) avant toute lecture de l'issue. Conséquences, écrites
d'avance :

- **A4, ou A1 sur une ligne de la classe linéaire** : l'inégalité log W ≤ 0, démontrée pour cette classe et éprouvée par les
  essais et les mutations, est falsifiée. Défaut du code ou de l'argument, localisé ou non : la course est **invalide d'office**
  et ne rend aucune issue, quelle que soit la conclusion de l'audit. L'audit sert à trouver la cause ; la reprise est une
  version nouvelle, avec un préenregistrement nouveau.
- **A1 sur T05s ou T09g seulement (classe log-linéaire), ou log W max > +0,25 sur l'une de ces deux lignes** (0,25 : marge de
  Newton maximale admise par le code, `DECREMENT_ADMIS`) : l'issue « confirmée » est **interdite**. Si l'audit localise un
  défaut du code, la course est invalide comme ci-dessus ; sinon l'issue est « non jugeable (réserve log-linéaire) » : la ligne
  est déclarée ouverte (la marge de Newton n'est pas démontrée) et les autres lignes sont rapportées sans revendication sur la
  classe log-linéaire.
- **A2, A3, A5, A6** : l'audit dit si un défaut est trouvé (course invalide, aucune issue) ou non (l'issue est lue avec la note
  jointe).

Une issue « confirmée » sans déclencheur n'est pas pour autant tenue pour propre : le contre-lecteur du verdict (R13) relit les
membres dominants et les log W rapportés.

## 8. Liste d'arrêt

- **Ligne en erreur** (exception, richesse non finie) : arrêt, code 3, aucun verdict, aucun taux rapporté (le rapport ne
  nomme que les lignes terminées) ; les lignes déjà en cours dans l'autre processus vont à leur terme.
- **Durée > 3 heures** (`--duree-max-s` 10 800, gelé) : arrêt, code 3, même règle.
- **Écart au plan**, refusé avant toute course (code 2, aucune écriture) : autre fichier que ce préenregistrement ; fichier non
  scellé ou compagnon `.sha256` non conforme ; fichier du code gelé absent du bloc ou différent de son empreinte ; option
  `--lignes` ; répétitions ≠ 1 000 ; durée maximale ≠ 3 heures ; entropie < 2⁶⁴ ; dossier de sortie non vide.
- Après un arrêt (code 3 ; aucun taux lu), le dossier de sortie de la course arrêtée contient déjà `manifeste.json` : le banc
  refuse de le réutiliser (code 2, « dossier de sortie non vide »). On le conserve tel quel (jamais supprimé ni renommé en
  silence, R12) et on rejoue la commande de la section 4 avec **un seul changement**, un dossier de sortie neuf (par exemple
  `../resultats/banc-tricheurs-v8-validation-v1-reprise-1`) : même fichier scellé, donc même graine, donc même course. La cause
  de l'arrêt et le rejeu sont dits dans le rapport. Toute autre intervention manuelle est un écart, consigné.

## 9. Lectures préalables déclarées

Toutes les courses jouées sous le nul v8 (ou son équivalent « candidat ») par l'agent précédent, par l'auteur et par le
contre-lecteur, dont il reste une trace, avec ce qui a été vu. Heures UTC du 1er novembre 2026. « Scratchpad » =
`/tmp/claude-0/-home-claude/730d0294-0b2b-55ca-8b32-49f2d3ec072d/scratchpad/` (hors du dépôt, non durable) ; « prélectures » =
`resultats/prelectures-nul-v8-2026-11-01/` (dans le dépôt, copies à l'octet près). Empreintes SHA-256 pleines.

| # | qui, quand | course | entropie | lignes (nul) × répétitions | vu | sortie et empreinte |
|---|---|---|---|---|---|---|
| L0 | banc v7 publié, 19:51 | `banc_tricheurs_v7.py --graine 20261101 --repetitions 200` | dérivation SHA-256 (`graine_derivee`) de 20261101 | toutes les lignes v7, dont « candidat » ≡ v8 : T02, T03b, T04, T05s, T07, fille neuve, fraîche neuve | candidat : 0/200 × 4 ; fille neuve 200/200 ; fraîche neuve 198/200 ; T07 1/200 ; T01\|v1 90/200 | `resultats/banc-tricheurs-v7-2026-11-01/banc-tricheurs-v7.json`, `2fc037b4eda23cf6b36e038c2034c53e6de4625f07308159a896ad04c808ca3c` |
| L1 | agent précédent, 20:16 | banc v8 brouillon, `--lignes T02,T04,nul_exact --repetitions 20` | 20261101 | T02, T04, nul exact (v8) × 20 | 0/20 chacune | scratchpad `v8/banc-reduit-1/banc-tricheurs-v8.json`, `bde5a7951f7085893ccea38484bcaa1dc77fa3bd903d3dc31d74bb19175cc958` |
| L2 | agent précédent, 20:17 | banc v8 brouillon, toutes les lignes, `--repetitions 20` | 7 | 18 lignes × 20 | fatales 0/20 ; T01\|v1 10/20 ; fille neuve v8 20/20, v7 20/20 ; fraîche neuve v8 18/20, v7 20/20 ; T07 0/20 ; T12b 18/20 ; médianes et 99ᵉ centiles de log W | scratchpad `v8/banc-complet-20/banc-tricheurs-v8.json`, `95527da3c31514173f714bbe12bc47fe380ed86f14d43796903e6e520440821e` |
| L3 | agent précédent, 20:19 à 20:21 | démonstrations v8 et v7 (proposeur, 4 générations ; couche 1, 2 générations) | 20261027 | — | verdicts identiques v7/v8 | scratchpad `v8/demo-proposeur-v8/demo-couche1-proposeur-v8.json`, `9dc732eed5632c90187f100b8202c39997f1f28cf1bf58698b336065c99b0bdb` ; `v8/demo-couche1-v8/demo-couche1-v8-v1.json`, `a406b84be598e87b35e1d44f17cc84859d1fad828a0895868f6c3b24301a7667` ; v7 : `v8/demo-proposeur-v7/demo-couche1-proposeur-v7.json`, `e1e9a8403f7c987485db6d102c559434f9c52ffc21cdcb0d4d23dbee8eb9080d` ; `v8/demo-couche1-v7/demo-couche1-v7-v3.json`, `957c90bdcf3c4f59a7e574249e0fed1a6b0d2ec2fffc46910b8fdf1426c9d326` |
| L4 | agent précédent, vers 20:13 à 20:29 | essais du brouillon `test_v58_nul_v8.py` (nombre de passages inconnu) | 20261101 ; 3 | T02, T03b, T04, T05s, fille neuve, fraîche neuve, nul exact (v8) × 20 ; T02, T04 (v7, aux graines v8) × 20 ; T01\|v1 × 20 ; T04\|v8 × 3 | réussite ou échec des assertions (0/20 ; ≥ 16/20 ; ≤ α ; > α) | — |
| L5 | auteur, 20:45 à 21:10 | essais `test_v58_nul_v8.py` (brouillon puis version finale, plusieurs passages) et banc de mutations | 20261101 ; 3 ; 5 ; `graine_derivee(20261101, …)` | comme L4 ; plus T04 et T03u (v8) × 2 (graine 5) ; 2 répétitions de T02, T04, T05s (candidat ≡ v8, v7), T01\|v1 | assertions seulement sous v8 ; sous des nuls **mutés** (pas v8) : sans `ajuste_lineaire:archive`, T02 16/20, T03b 2/20, T04 19/20 ; sans les survivantes tempérées, T05s 12/20 | — |
| L6 | auteur, 20:59 | vérification des bornes (script `v58_verif_bornes.py`, scratchpad, `f9ac2824bf6d3778cb322666981ad90ebbb8ce1dfe06a9f00f280474fcbe0cbf`) | 41 | 11 lignes fatales (v8) × 10 | 0 promotion ; log W max le plus haut par ligne (classe linéaire : −1,0·10⁻⁵ au plus ; T12a : −1,08) | — (sortie à l'écran) |
| L7 | auteur, 21:16 | commande de l'intégration continue : `--lignes T02,T04,nul_exact,T01 --repetitions 20` | 20261101 | T01, T02, T04, nul exact (v8), T01\|v1 × 20 | fatales 0/20 ; T01\|v1 11/20 | prélectures `L7-banc-reduit-ci/banc-tricheurs-v8.json`, `c565dcddd3c674c2927709f0b3a2c7e272c15bfb5223864c24fa976cd295528c` ; `manifeste.json`, `ec43b17abd33c9ecb893e4b5c3c13cfada4fc20800c55398ca213e6b47b5c2ba` |
| L8 | auteur, 21:16 | mesure de durée : toutes les lignes, `--repetitions 20` | 7 | 18 lignes × 20 | identique à L2, valeur pour valeur ; en plus, log W max le plus haut par ligne (T12a : 2,45) | prélectures `L8-banc-complet-20-graine7/banc-tricheurs-v8.json`, `483f2e05ee243053e1084a6837cf56a6da0da55f82f1c58deecc14ef6eb830e5` ; `manifeste.json`, `51195d44fd84830e0b905b530ea7160bf984e0f45997a50817d4feffe84a57b7` |
| L9 | auteur, 21:13 à 21:18 | démonstrations v8 (proposeur, 4 générations ; couche 1, 2 générations) et v7 (proposeur, 4) | 20261027 | — | verdicts identiques v7/v8 (section 10) | scratchpad `v58/demo-proposeur-v8/demo-couche1-proposeur-v8.json`, `fc39bc2cbc1cb4d8f7a26f7ded94d3b96a70633d91ac5798b72fd9d9119ebacd` ; `v58/demo-proposeur-v7/demo-couche1-proposeur-v7.json`, `2dea09f8e33d2595a568836c2906f1e04eaf8fc60f199aec17ee9bc49f4c82ce` ; `v58/demo-couche1-v8/demo-couche1-v8-v1.json`, `bc32d6310716244e074a2b77041f58fea400d946c2e13d5d236d3e95410de81f` ; journaux de génération 3 cités en section 10 : v7 aveugle `d08911053777018fe78fad49e24076fade0efad2ad9658f09a7f6d9aefa130e2`, v8 aveugle `9b835af431525511061a54f631df226ab8f6aa5e74facf4bce7a8190d4ae72c2`, v7 exploration `e165d7169d8a7108667f8c5f8f5c1fd3f0ea4c87a549be969f2cc3471abadb4a`, v8 exploration `fb7f6fb571d7f65d18a750cc821b396695c192418122ca8896f812f53b290274` |
| L10 | intégration continue, à chaque poussée | `.github/workflows/bench-reduit.yml` = L7 | 20261101 | = L7 | = L7 (le code est déterministe ; l'intégration continue installe numpy ≥ 1.25 sans version fixe et Python 3.12 : identité non garantie entre versions ; elle ne décide rien) | — |
| L11 | auteur, 21:23 | rejeu de la commande de l'intégration continue avec le banc **gelé** (`23d2b7d2…`) | 20261101 | T01, T02, T04, nul exact (v8), T01\|v1 × 20 | identique à L7, ligne par ligne (promotions, log W max, membres dominants) ; seules les durées diffèrent | prélectures `L11-banc-reduit-ci-rejeu-banc-gele/banc-tricheurs-v8.json`, `56276b9e0b625d83ddf6854a6070b1f626347f430d1205f3d063a0981173b3d5` ; `manifeste.json`, `93257cd8001694511a6c596b2898e04ef23e963e19c835a0862c3c0978a7c3b5` |
| L12 | contre-lecteur (R2), 21:30 à 22:05 | (a) les 35 essais de `essais/test_v58_nul_v8.py` (deux passages) ; (b) `essais/mutations_v58.py --raisons` ; (c) rejeu de L8 avec le banc gelé ; (d) rejeu de L6 (`v58_verif_bornes.py`) | (a, b) comme L4 et L5 ; (c) 7 ; (d) 41 | (c) 18 lignes × 20 ; (d) 11 lignes fatales × 10 | (a) 35 réussis, 51 sous-essais ; (b) 34 mutations tuées pour la raison attendue, mêmes comptes que L5 ; (c) identique à L8 valeur pour valeur, 63,2 s ; T12a log W max +2,448, T05s −0,038, T09g −0,033 ; (d) mêmes maxima que L6 ; vérification couche 1 : 352 fiches, aucune différence de log W max v7/v8 | prélectures `L12c-rejeu-L8-contre-lecteur/banc-tricheurs-v8.json`, `5ad6b686b5c7ead84e59746c002bb482e0c1bae1a9b30d94fd7e9f191e43a608` ; `manifeste.json`, `0972d2c0623f783daf60a90045b05cd130402e2919aaa1928bb8e4a9026cc351` ; `L12ab-essais-mutations-contre-lecteur/pytest_final.txt`, `1e771cef98021e27dd4af2a4a2afe47915f4f9f4932faf534adec8aac6641dd7` ; `mutations_sortie.txt`, `0a913b5b9cf96fb625f677a2c00f9edf45f8ad991218dd4713452465c70aa815` ; déclaration : rapport de contre-lecture, annexe 3 |

Code joué par chaque lecture : L1 et L2 ont été jouées avec un brouillon de `pole/nul_v8.py` (`59c2f58f…`) ; L7 et L8 avec le
`nul_v8.py` final (`cc452aaf…`) mais un état antérieur du banc (`demonstrations/banc_tricheurs_v8.py`, `0506194b…`, empreinte
lue dans leurs manifestes) ; le banc gelé (`23d2b7d2…`) reproduit L7 (L11) et L8 (L12, c) valeur pour valeur : les chiffres de
L7 et de L8 valent donc pour le code gelé. Les sorties de L7, L8, L11 et L12 sont copiées dans le dépôt sous les prélectures
(sans compagnon `.sha256` ; empreintes pleines ci-dessus ; les journaux d'essais de L12 contiennent des chemins temporaires
locaux, sans conséquence) ; les autres lectures sont citées par leur empreinte pleine, dans le scratchpad hors du dépôt. Deux
dossiers du dossier de travail du contre-lecteur ne sont pas des lectures du nul v8 : une démonstration du juge v7 jouée à
19:41, avant la décision v8, et une copie de L0. Des courses de l'agent précédent sans trace sur disque ne peuvent pas être
exclues ; aucune n'a pu utiliser la graine décisive (section 4, garantie (i)). Les prédictions de la section 3 ont été écrites
après L0 à L12 et en tiennent compte : c'est déclaré, et c'est pourquoi elles ne décident pas de l'issue.

## 10. Portée

- **Classe couverte** (la loi du tricheur est un membre du nul v8) : recombinaisons linéaires de lois connues (chaque loi
  seule, tout mélange de parents et de survivantes, avec ou sans loi aveugle fixe) ; recombinaisons log-linéaires d'une loi
  connue (survivante ou parent tempéré et incliné ; pour une fille, produit des deux parents tempéré et incliné).
- **Classe non couverte** (dite, non fermée) : recombinaisons par morceaux mettant en jeu une survivante (si/sinon par
  sous-population ou seuil d'un trait), poids de mélange dépendant de l'instance ; produits de plus de deux lois, et produits
  de deux lois autres que les deux parents d'une fille ; compositions d'étapes (T07, mesurée seulement) ; déformations non
  monotones (T12) ; lois hors de l'archive (témoins, autre espace).
- **Couverte par l'argument, sans ligne du banc** : le produit des deux parents d'une fille, tempéré et incliné (membre
  `ajuste_log:AB`), et les formes de v0 ; leur fermeture n'est pas mesurée ici.
- **Hors de la portée de cette validation** : la multiplicité entre fiches (règle e-BH ; lignes T14 à T16 du banc v7, non
  rejouées) ; la puissance à effet faible (les deux lignes de puissance sont à effet fort) ; la banque réelle.
- Mondes synthétiques du banc (K = 3, 2 traits) : rien n'est revendiqué sur la banque réelle. Les démonstrations v8 (L9)
  rendent les mêmes verdicts que v7 : dans la démonstration avec proposeur, le nul ajusté n'a été exercé que sur 8
  engagements de génération 3 du monde planté (après les survivantes G2-F05 et G2-F14), tous éliminés sous v7 comme sous v8,
  log W max abaissé de 1,3 à 19 nats ; l'un (G3-F16) passait 1/α par fiche sous v7 (log W 4,13), retenu seulement par la
  règle e-BH, et reste sous 1/α sous v8 (2,81) ; dans la démonstration couche 1, aucun engagement ne porte de membre
  d'archive (aucune survivante non témoin de même espace) : v8 y est v7 par construction.
- « Partout » vaut pour les entrées v8 ; la ligne de commande v7 (`pole/pole.py`, commitée) accepte encore
  `--sans-nul-archive` et `--sans-nul-archive-ajuste`.

## 11. Empreintes du code gelé

Les 12 fichiers que la course importe (`FICHIERS_GELES` du banc). Le banc vérifie chaque ligne de ce bloc et refuse la course
si l'un des 12 manque ou diffère. Recalcul avant scellement, si le code a changé (depuis `orchestrator/`) :
`sha256sum demonstrations/banc_tricheurs_v7.py demonstrations/banc_tricheurs_v8.py pole/__init__.py pole/caviardage.py pole/controles_pari.py pole/cycle.py pole/fiche.py pole/memoire.py pole/nul_filles_v2.py pole/nul_v8.py pole/outils.py pole/selection_pari.py`.

<!-- empreintes-du-code : début -->
```
ef016d250b7b503f705dc95919719c68c8f968534fd901df7364a6062d67cf12  demonstrations/banc_tricheurs_v7.py
0be47e4b5916a98499faf9c40d65369b41e3a5463d7ab444ed18ba18bba08c03  demonstrations/banc_tricheurs_v8.py
f7341b965ddba1e0fb21b44d9068f59650d5c77e3175f2b6b7ca879219fa5c9b  pole/__init__.py
78abfd4731218e20538418608ebebaca3364206ef6d014b7a34829a3c9fd7e85  pole/caviardage.py
fabc3d0873e6db639f2578eb00ef0035d7831a3b2a1457ffce1d91aa7a364e1c  pole/controles_pari.py
798f039042e3ee1f18df5c566f5a0ddee5dac5c98225c8ce621e267174c8ee18  pole/cycle.py
ec018f147196222268d91358ce2038bb35bf76069e6bf8928dea9e3db59d1074  pole/fiche.py
71f1d08613bf335aa9ef7aa1397f20aa24553fea2f1b858c10b265d62f8ab79e  pole/memoire.py
0ed9b4adbcddc4ad77a1c97d5cbd5706f14926e9c47fe96ce2bab3221a138910  pole/nul_filles_v2.py
cc452aafd17121a7c0ec42829eea47063ffee1f6cdf7f642e264d528f976b888  pole/nul_v8.py
966d9553026aad1eb7d97fa677334f1b59f22a39f15eef95134d63bc47634444  pole/outils.py
359928110d757cd54cc0d2773910c7360895b68cac5d17e0e4b4e9933ef306bc  pole/selection_pari.py
```
<!-- empreintes-du-code : fin -->

Non gelés ici (hors de la course ; le banc ne les vérifie pas) : essais `essais/test_v58_nul_v8.py` et
`essais/mutations_v58.py`, démonstrations `demonstrations/demo_couche1_v8.py` et `demonstrations/demo_couche1_proposeur_v8.py`,
intégration continue `../.github/workflows/bench-reduit.yml`.

## 12. Contre-lecture (R2)

Contre-lecteur neuf (ni auteur de ce fichier ni du code) : rapport `contre-lecture-prereg-nul-v8-v1.md` (copie dans le dépôt :
`orchestrator/prereg/contre-lecture-prereg-nul-v8-v1.md`), empreinte SHA-256
`e0faa4f2fad1426bf08b1ff6b04b9b42fa1bd2542502ee71cef5cde682bad06f`, sur la version 1 de ce fichier, empreinte SHA-256
`894b294b2a3d3eb455ff77e709695026795e6d67199e94f2a905491cddf2d4b4` ; verdict « scellable après corrections mineures
(listées) », corrections obligatoires C1 à C9, recommandées C10 à C15. Corrections appliquées dans cette version :

- C1 (section 7, conséquences des audits : A4 et A1 sur la classe linéaire invalident d'office ; classe log-linéaire : « confirmée » interdite) ;
- C2 (section 7, audit A5, nul ajusté inactif, lu sur les membres dominants) ;
- C3 (section 4, « un scellement, une course décisive ») ;
- C4 (section 8, rejeu après arrêt dans un dossier de sortie neuf) ;
- C5 (section 9 : L11 et L12 ajoutées ; code joué par chaque lecture ; empreintes pleines ; copies de L7, L8, L11 et L12 dans
  `resultats/prelectures-nul-v8-2026-11-01/`, sur instruction du coordinateur — le rapport proposait aussi L1 à L9 et un autre
  nom de dossier) ;
- C6 (section 3, P1 scindée en P1a, P1b, P1c) ;
- C7 (section 6, issue 4 ; section 10, deux alinéas) ;
- C8 (cette section) ;
- C9 (section 4, le code de sortie ne décide pas) ;
- C10 (section 7, A2 : monotonie en loi, fausse alerte possible) ;
- C11 (section 4, durée attendue 17 à 55 minutes) ;
- C12 (section 6, dernier alinéa : règle appliquée par la session au vu de la décision du directeur du 1er novembre, 20:59 heure de Paris ; usage du nul v8 selon l'issue) ;
- C13 (section 7, audit A6) ;
- C14 (section 4, « Pourquoi un banc v8 ») ;
- C15 (section 13, procédure et fichiers à committer ensemble).

Aussi : en-tête, nom du fichier dans la règle de la graine et dans la commande (v2), métrique de Newcombe (niveau réel mesuré
par le contre-lecteur), environnement (identifiant de commit), section 6 (ordre entre lecture gelée et audits). Non
appliquées : aucune. Un seul changement de code, approuvé par le coordinateur : dans `demonstrations/banc_tricheurs_v8.py`,
le fichier imposé au mode décisif (`PREREG_DECISIF`) et sa mention dans la docstring passent de la v1 à la v2 de ce
préenregistrement ; la ligne de ce fichier dans le bloc de la section 11 est recalculée, les 11 autres sont inchangées. Le diff
entre la version lue (`894b294b…`) et cette version a été relu par un lecteur neuf : oui, par un lecteur neuf (relecture courte du diff `diff -u` v1 vers v2, 1er novembre 2026) : C1 à C15 appliquées fidèlement, aucun changement de fond non demandé, 12 empreintes du bloc gelé vérifiées par `sha256sum`, 35 essais réussis ; rapport `contre-lecture-diff-nul-v8-v1-v2.md` (même dossier) ; deux précisions de rédaction qu'il demandait (« en probabilité pour un même monde » ; « traitée comme non jugeable pour l'usage ») appliquées avant le scellement.

## 13. Procédure avant la course et fichiers à committer ensemble

En **un seul commit**, au scellement (chemins depuis la racine du dépôt) :

- `orchestrator/prereg/preenregistrement-validation-nul-v8-v2.md` et son compagnon `preenregistrement-validation-nul-v8-v2.md.sha256` ;
- `orchestrator/prereg/preenregistrement-validation-nul-v8-v1.md` (version lue, gardée telle quelle, sans compagnon) ;
- `orchestrator/prereg/contre-lecture-prereg-nul-v8-v1.md` (rapport de contre-lecture, copie à l'octet près) ;
- les 12 fichiers gelés de la section 11 (dont `orchestrator/demonstrations/banc_tricheurs_v8.py` et `orchestrator/pole/nul_v8.py`,
  neufs ; les dix autres sont déjà suivis et inchangés) ;
- `orchestrator/essais/test_v58_nul_v8.py`, `orchestrator/essais/mutations_v58.py` ;
- `orchestrator/demonstrations/demo_couche1_v8.py`, `orchestrator/demonstrations/demo_couche1_proposeur_v8.py` ;
- `.github/workflows/bench-reduit.yml` ;
- `resultats/prelectures-nul-v8-2026-11-01/` (10 fichiers : `L7-banc-reduit-ci/`, `L8-banc-complet-20-graine7/`,
  `L11-banc-reduit-ci-rejeu-banc-gele/`, `L12c-rejeu-L8-contre-lecteur/` — chacun `banc-tricheurs-v8.json` et `manifeste.json` —
  et `L12ab-essais-mutations-contre-lecteur/pytest_final.txt`, `mutations_sortie.txt`).

Puis, avant la course : pousser ce commit ; noter son identifiant (`git rev-parse HEAD`) dans le rapport de la course ;
rejouer sur l'arbre scellé les 35 essais (`python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v58_nul_v8.py`) et le
banc de mutations (`python3 -I -B essais/mutations_v58.py`) ; lancer la commande de la section 4.
