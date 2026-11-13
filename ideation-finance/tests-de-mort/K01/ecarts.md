# K01 — Écarts à la préinscription (expérimentateur)

**Aucune affirmation factuelle de la préinscription sur les données ne s'est révélée fausse.** Tout ce qu'elle annonce a été
retrouvé à l'identique : sha256 de l'archive de l'enquête (`49348fa3…`) et de `1_HICP.csv` (`a8e99246…`, deux copies
identiques) ; sha256 du fichier Eurostat (`43ef7b6b…`) et date de mise à jour `17/09/26` ; 29 années 1997-2025 sans drapeau ;
97 séries MPD en HTTP 200, première année de statut `F` = année de l'exercice pour les 97, colonne `TITLE` vide ; 14 255 lignes
SPF (5 457 / 5 346 / 3 452), 97 tours, 106 identifiants ; 291 lignes BCE ; 10 474 → 8 873 → 8 663 (105 identifiants) →
8 595 lignes, 94 prévisionnistes, 96 tours, 24 années cibles, 4 393 + 4 202 ; 47 à 108 lignes par tour (médiane 92) ; 7 425
lignes sur 88 tours hors cibles 2021-2023 ; 6 269 lignes sur les cibles 2002-2019 ; 188 cellules agrégées par source (96 + 92) ;
11 identifiants et 68 lignes retirés par la règle des 8 tours.

Aucun écart de fond : la statistique principale, l'échantillon et les contrôles sont exécutés comme écrits. Les points
ci-dessous sont des écarts de forme ou des lectures d'une formule incomplète ; chacun est noté, même minime.

## É1 — Le journal de téléchargement est écrit par un script séparé
La préinscription place sha256, date et code HTTP dans `construire_journal.json`. Ce fichier existe, mais il est écrit par
`telecharger.py` (téléchargement) et non par `construire.py`, afin que `construire.py` reconstruise le fichier d'analyse à
partir de `donnees/` seul, sans réseau. `donnees/PROVENANCE.md` est produit par `provenance.py` à partir de ce journal ; le
sha256 de chaque fichier y est recalculé et comparé au journal.

## É2 — Politique d'essais : celle de la préinscription, pas celle de la consigne de session
La consigne de session demandait jusqu'à 8 essais avec délai croissant ; la préinscription fixe jusqu'à 10 essais, 120 s au
plus par essai, 10 s entre deux essais. J'ai suivi la préinscription. Sans conséquence : les 99 fichiers ont été reçus au
premier essai (HTTP 200), entre 00:02 et 00:19 UTC le 2026-11-13.

## É3 — Écriture des nombres dans le fichier d'analyse
- `prevision` et `realise` sont recopiés **tels que publiés** (chaîne de la source : par exemple `2`, `1.8`, `1.86361`).
- Les différences (`revision`, `instrument`, `erreur`) sont écrites « sans arrondi » au sens suivant : la plus courte écriture
  décimale qui redonne exactement le nombre double calculé (par exemple `-0.09999999999999987`), complétée par des zéros à au
  moins 6 décimales (`0.500000`).
- Les colonnes qui recopient une autre prévision (`prevision_prec`, `prevision_autre`, `prevision_autre_prec`) suivent la même
  règle (au moins 6 décimales, par exemple `1.900000`). La préinscription n'impose le format qu'aux différences ; la valeur est
  identique à celle de la prévision recopiée (contrôles 8 et 9 satisfaits à 10⁻¹² près).

## É4 — Dénominateur des écarts-types MCO (lecture d'une formule incomplète)
Pour `et_b_mco_naif_dk8` et `et_b_mco_ef_avant_2020_dk8`, la préinscription donne S_t mais pas la division finale. J'ai pris
racine(LRV₈(S)) / Σ x̃², par analogie avec la formule écrite pour les pentes agrégées (section 7, « Consensus et BCE ») et avec
le sandwich MCO. Contrôle croisé : statsmodels, `cov_type="hac-groupsum"`, 8 retards, sans correction, donne
0,188360 pour `et_b_mco_naif_dk8` (mon calcul : 0,188360). Aucune autre lecture raisonnable n'a été trouvée.

## É5 — `b_mco_ef_avant_2020` : mise en œuvre par Frisch-Waugh-Lovell sur le sous-échantillon
« MCO avec indicatrices d'identifiant et d'horizon » : e et x sont résidualisés par MCO sur les indicatrices d'identifiant et
l'indicatrice `horizon` = 1, **sur l'échantillon restreint aux cibles ≤ 2019** ; puis b = Σ ẍ ë / Σ ẍ², S_t = Σ ẍ (ë − b ẍ),
et = racine(LRV₈(S)) / Σ ẍ². C'est le même coefficient et le même sandwich que la régression avec indicatrices.

## É6 — Pentes agrégées : détails de lecture
- Le consensus C(t, y) est la moyenne des lignes `SPF` du fichier d'analyse (identifiants numériques), non la moyenne publiée
  `AGG` de l'archive, conformément au texte (« toutes les lignes SPF du tour t »). Pour les cellules d'horizon 1 d'un tour T1,
  C(t − 1, y) vient des lignes d'horizon 2 du tour T4 précédent (présentes dans le fichier). Aucune cellule n'a été perdue
  (188 + 188).
- `b_consensus_hors_2021_2023` et `b_bce_hors_2021_2023` : moyennes retirées par horizon **dans le sous-échantillon** (164
  cellules chacun), comme pour E'.
- Pour `et_diff_dk8`, ψ_t est formé sur la réunion des tours des deux sources (identiques ici : 96 tours).

## É7 — Variance de long terme quand des tours manquent (E')
Hors cibles 2021-2023, les 8 tours 2021Q1-2022Q4 (8084-8091) n'ont plus aucune ligne. Lecture littérale appliquée : les
retards se comptent en numéros de tour (`t_tour`), un tour absent ne crée aucun couple. Lecture alternative (retards comptés
en rang des tours présents, 88 tours consécutifs) : `et_b_iv_hors_2021_2023_dk8` = 0,465842 au lieu de 0,466177 ;
`borne_haute_ic90_hors_2021_2023` = 0,966801 au lieu de 0,967375 ; `f_premiere_etape_hors_2021_2023` = 321,58 au lieu de
315,45. Seule la lecture littérale est dans `temoin.json`.

## É8 — `b_iv_max_sans_une_annee`
« La plus grande (la moins négative) » : les 24 valeurs sont toutes positives ; j'ai pris la plus grande au sens littéral
(1,319787, sans l'année 2009). La parenthèse ne change rien à ce choix.

## É9 — Fichiers produits en plus des livrables
`telecharger.py`, `provenance.py`, `construire_controles.json` (effectifs à chaque filtre et résultat des 12 contrôles),
`analyse_details.json` (quantités intermédiaires, 24 valeurs sans une année), `controle_croise.py` et
`controle_croise.json` (contrôle croisé hors préinscription : linearmodels `IV2SLS` et sandwich matriciel complet,
identiques à 10⁻¹² près pour b_IV et son écart-type de Driscoll-Kraay). Ils ne modifient aucun chiffre du témoin.

## É10 — Figure
Sur `figure.png`, les pentes descriptives sont tracées avec b ± 1,714 × écart-type (Driscoll-Kraay). Pour elles, cet
intervalle n'est pas préinscrit ; c'est un repère visuel, signalé en légende.
