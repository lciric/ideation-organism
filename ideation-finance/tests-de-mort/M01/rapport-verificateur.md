# M01 — Rapport du vérificateur

Rédigé le 2026-11-13 par le vérificateur indépendant. Pas de verdict ici : `verdict.py` n'a pas été lancé.

**Fichiers lus, et eux seuls** : `M01/preenregistrement.md` (et son `.sha256`), `M01/M01_analyse.csv`,
`tests-de-mort/protocole.md`, `tests-de-mort/verdict.py`. Je n'ai ouvert ni les scripts de l'expérimentateur, ni
`temoin.json`, ni `ecarts.md`, ni les rapports, ni la figure, ni `simulation_decision.py`, ni `donnees/`, ni d'autre dossier.
**Donnée externe** : le contrôle 2 demande de reconstruire la population « à partir de D1 (une requête) » ; j'ai donc lancé
moi-même la requête D1 de la section 5.1 (2026-11-13, HTTP 200, 2 793 lignes, sha256
`2fed01bf60d1c088504dc62f565d3ac506aefff2168148713519e1ba2ad85424`), enregistrée hors du dossier M01 (bloc-notes de session).
Sans argument, `verification.py` refait cette requête.

**Fichiers écrits** : `verification.py` (code principal), `verification.json` (sortie), `verification_controle.py`
(contrôle croisé par d'autres chemins), ce rapport. Aucun fichier existant n'a été modifié.

## 1. Sceau

`sha256sum preenregistrement.md` = `363a53c6c9e5ae993c270c37c2595a824214baf40b838a5c0ce631ba0832e343`, identique au contenu de
`preenregistrement.md.sha256`. **Sceau intact.**

## 2. Contrôles de schéma (section 7)

Portée appliquée à la lettre : contrôles 1 et 2 sur le fichier entier ; contrôles 3 à 9 sur les seules lignes `dans_p` = 1 ;
les lignes exclues sont seulement comptées. Aucun contrôle en jours civils.

| N° | Contrôle | Résultat |
|---|---|---|
| 1 | 59 colonnes de 6.1, dans l'ordre, aucune autre | passe (en plus : pas de BOM, 324 lignes, tri par date puis échéance correct) |
| 2 | `id_ligne` unique ; ensemble = population de 4.5 reconstruite sur D1 | passe : 324 = 324, mêmes identifiants ; D1 donne 97/14/96 avant et 39/39/39 après |
| 3 | identité, `echeance`/préfixe, `mois`/`annee`/`periode`, coupon, échéance et émission d'origine = première adjudication D1 (une seule par CUSIP), `complet` = 1, colonnes 18/58/59 dans {0,1} | passe sur les 321 lignes de P |
| 4 | J ∈ C ; `date_jm5` = C[rang−5] ; `date_jp5` = C[rang+5], C reconstruit selon 4.3 | passe sur P (et J ∈ C pour les 324) |
| 5 | aucune autre adjudication du même CUSIP (toute ligne D1) à ≤ 10 rangs de J ; émission d'origine ≤ J−5 | passe sur P |
| 6 | `identite_fi_ok` = 1 | passe |
| 7 | plages (prix [30;200], τ > 0, CMT/SVENPY/rendements [−1;20], coupon [0;15]) | passe |
| 8 | \|f−g\| ≤ 0,60 et \|CMT−SVENPY\| ≤ 1 point aux trois dates | passe |
| 9 | colonnes 49-57 = formules à 10⁻⁶ pb ; colonnes 15-42 remplies | passe (écart max 1,4·10⁻¹³ pb) |

Calendrier C : construit à la main depuis le texte de 4.3 (lundi-vendredi du 2009-06-01 au 2026-12-31 ; onze fériés de
5 U.S.C. 6103 tels qu'énumérés, Juneteenth à partir de 2021, samedi → vendredi précédent, dimanche → lundi suivant, y compris
le 1er janvier observé le 31 décembre précédent ; moins 2012-10-30 et 2018-12-05). Le jour d'investiture, absent de
l'énumération du texte, n'est pas retiré. Contrôle croisé avec `pandas.USFederalHolidayCalendar` : mêmes J±5 pour les 321
lignes.

Cohérence : `motif_exclusion` vide ⇔ `dans_p` = 1 sur les 324 lignes. Motifs recalculés de mon côté sur D1 : les trois mêmes
lignes `fenetre_chevauchee` (9128286T2 du 2019-06-12 et du 2019-06-21 ; 912810TC2 du 2021-12-02), aucune autre.

**`schema_ok` = 1.**

## 3. Échantillon

Exclues (comptées, non contrôlées) : `fenetre_chevauchee` 3 ; `titre_non_emis_a_jm5` 0 (la ligne 2021-12-02 le serait aussi
mais le premier motif a priorité) ; `valeur_manquante` 0.
P = 321 lignes, conforme à l'attendu de 4.5 : A = 204 (95 / 13 / 96 aux 10 / 20 / 30 ans ; 96 mois), B = 117 (39 / 39 / 39 ;
39 mois), dont 24 lignes en 2023 (8 mois). Sans 2023 : 93 lignes après (31 mois). Sans le 30 ans : 108 avant (95 mois) et 78
après (39 mois).

## 4. Recalcul des rendements

Code écrit de zéro (section 6.2 : dates de coupon reculées de 6k mois depuis M, dernier jour du mois si besoin ; coupon
couru linéaire en jours civils entre L et N ; période fractionnaire composée ; courbe de Svensson en composition continue,
m = jours/365,25 ; résolution par `brentq`, xtol 10⁻¹²). Les six rendements des 321 lignes de P concordent avec ceux du
fichier : **`ecart_max_rdt_pb` = 2,8·10⁻¹¹ pb** (seuil 0,05). Second chemin (`relativedelta` + Newton) : 1,0·10⁻¹¹ pb d'écart
au premier.

Toutes les statistiques sont calculées sur mes propres valeurs : V_own à partir de mes rendements ; V_cmt à partir des
colonnes 37-42 du fichier (recopies de DGS et SVENPY, que je ne peux pas recalculer autrement).

## 5. Champs de la règle (section 8), en pb

ET groupée par mois avec G/(G−1), aucun autre facteur ; bornes à 1,645 exactement.

| Champ | Valeur |
|---|---|
| n_avant / n_apres | 204 / 117 |
| n_grappes_avant / n_grappes_apres | 96 / 39 |
| ecart_max_rdt_pb | 2,76·10⁻¹¹ |
| v_own_avant_pb (ET) | 0,12604 (0,07865) |
| borne_inf_90_v_own_avant_pb | **−0,00334** |
| controle_positif_ok | **0** |
| v_cmt_avant_pb / v_cmt_apres_pb | 1,34485 / 0,01889 |
| baisse_cmt_pb (ET) | 1,32596 (0,37302) |
| borne_inf_90_baisse_cmt_pb | 0,71235 |
| controle_cassure_ok | 1 |
| v_own_apres_pb (ET) | 0,41578 (0,35254) |
| borne_inf_90_v_own_apres_pb | −0,16415 |
| baisse_own_pb (ET) | −0,28974 (0,36120) |
| borne_inf_90_baisse_own_pb | −0,88392 |
| d_pb (ET) | −1,61570 (0,16945) |
| borne_inf_90_d_pb / borne_sup_90_d_pb | −1,89446 / −1,33695 |
| marge_moitie_pb (ET, par h) | −0,95272 (0,21167) |
| marge_moitie_sans_2023_pb | −0,80675 |
| marge_moitie_sans_30_pb | −0,85167 |
| indecis | **1** |

Profil (S) : m ≤ 0 sur les trois échantillons, mais `borne_inf_90_v_own_apres_pb` = −0,164 ≤ 0 → (S) ne tient pas.
Profil (E) : `borne_inf_90_baisse_own_pb` ≤ 0 et m ≤ 0 → (E) ne tient pas. D'où `indecis` = 1.
Contrôle arithmétique : `d_pb` − (`baisse_own_pb` − `baisse_cmt_pb`) = 4·10⁻¹⁶.

Contrôle croisé (`verification_controle.py` : calendrier pandas, échéancier `relativedelta`, Newton, ET par `statsmodels`
OLS sur une constante avec `cov_type="cluster"`, m par la moyenne de h) : tous les champs ci-dessus retrouvés à moins de
4·10⁻¹² pb.

## 6. Descriptif (S1-S4, clé `descriptif` de `verification.json`)

- **S1, par échéance** (V_own avant / après ; V_cmt avant / après ; D ; m) : 10 ans 0,357 / 0,594 ; 1,632 / −0,044 ;
  D −1,913 ; m −1,075. 20 ans (13 lignes avant) 0,014 / −0,225 ; 1,137 / −0,741 ; D −1,640 ; m −0,701. 30 ans −0,087 / 0,878 ;
  1,089 / 0,842 ; D −1,212 ; m −1,089.
- **S2, deux jambes** : montée de V_own 0,156 (ET 0,087) avant, 0,606 (0,213) après, « baisse » −0,450 (0,230) — même signe
  que le R de J05 (−0,64, ET 0,28) ; redescente de V_own −0,030 avant, −0,190 après. V_cmt : montée 0,756 → 0,315 ; redescente
  0,589 → −0,296.
- **S3, par année** : V_own par année entre −0,59 (2013) et 0,96 (2023) ; V_cmt entre −0,54 (2025) et 2,11 (2017) ; détail
  dans le JSON. m sans 2023 et sans le 30 ans à la fois : −0,734.
- **S4** : écarts-types (n−1) de V_own 1,145 avant, 3,141 après, 5,154 en 2023 ; de V_cmt 1,932, 3,229, 5,433 ; corrélation
  V_own/V_cmt 0,507 avant, 0,939 après ; exclues 3 / 0 / 0 ; 11 lignes de P ont un prix FedInvest identique à deux des trois
  dates (8 avant, 3 après).

## 7. Ambiguïtés et lecture retenue

1. **D1 pour les contrôles 2, 3 et 5.** La consigne de vérification me limite à quatre fichiers, mais la préinscription
   (contrôle 2) demande de reconstruire la population sur D1 « (une requête) ». J'ai lancé cette requête publique moi-même,
   sans lire le D1 de l'expérimentateur. Les comptes reproduisent exactement ceux de 4.5.
2. **Rang d'une autre adjudication (contrôle 5)** : rang dans C de sa date ; une date hors de C prendrait le rang du premier
   jour de C qui la suit. Le cas ne se présente pas pour les CUSIP de P.
3. **Échantillon P** : défini par `motif_exclusion` vide (4.5) et par `dans_p` = 1 (7) ; les deux coïncident.
4. **Sous-échantillons** : `marge_moitie_sans_2023_pb` et `_sans_30_pb` recalculent D et la baisse de V_cmt sur le
   sous-échantillon (A inchangé sans 2023, puisque 2023 n'est que dans B). Aucune ET n'y est demandée.
5. **`et_marge_moitie_pb`** : par h = ½·V_cmt − V_own, comme écrit (et non par une combinaison des ET de D et de la baisse).
6. **ET par année et par échéance (descriptif)** : même formule, G = nombre de mois du sous-ensemble.
7. **V_cmt** : « mes propres valeurs » ne peut porter que sur l'arithmétique (E_cmt, V_cmt recalculés depuis les colonnes
   37-42) ; les niveaux DGS et SVENPY sont pris du fichier, que le contrôle 9 relie à ses colonnes dérivées.

## 8. Ce qui paraît anormal ou fragile (constats, pas de verdict)

- **Le contrôle positif échoue de très peu** : borne basse −0,0033 pb pour une ET de 0,079. V_own avant 2022 vaut 0,126 pb,
  très loin de l'hypothèse d'instrument non atténué (≈ 1,38) et même de l'instrument atténué de la simulation (0,85). Par
  échéance, il est de 0,36 à 10 ans et de −0,09 à 30 ans. Ce résultat se trouve **à l'intérieur de la tolérance de 0,01 pb sur
  les bornes, mais `controle_positif_ok` a une tolérance de 0** : si le calcul de l'expérimentateur donnait une borne positive de
  quelques millièmes, les deux bornes s'accorderaient et l'indicateur divergerait. Mes deux chemins s'accordent à 10⁻¹² pb ; le
  signe ne dépend d'aucun arrondi de mon côté.
- Le signe dépend de quelques observations : sans mars 2020 (deux lignes, dont le 30 ans du 2020-03-12, V_own = −5,84), la
  borne deviendrait +0,009. Je ne fais que le constater ; la règle porte sur P entier.
- Corrélation V_own/V_cmt de 0,94 après 2021 contre 0,51 avant : après le changement de méthode, la courbe du Trésor suit de
  près l'écart du titre rouvert à GSW, alors qu'avant 2022 V_cmt montrait un pic à J (≈ 1,34 pb) que le prix FedInvest ne
  montre presque pas (0,13 pb).
- 11 lignes de P ont un prix FedInvest identique à deux dates sur trois (prix peut-être non mis à jour). Les retirer laisse la
  borne basse de V_own avant à −0,003.
- Rien d'anormal dans le fichier lui-même : schéma, calendrier, métadonnées et rendements concordent exactement.
