# J05 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `J05_analyse.csv`, rien d'autre. Code : `verification.py` (conventions 5.2,
K, régression sans constante avec effets fixes d'échéance et erreur type groupée par mois, tout réimplémenté à la main ;
statsmodels sert seulement de contrôle croisé et donne la même erreur type à 10⁻¹⁵ près). Sortie : `verification.json`.

## Nombres (verification.json)

schema_ok 0 · n_avant 206 · n_apres 116 · n_grappes_avant 96 · n_grappes_apres 39 · n_echec_convention 0 ·
ecart_max_rdt_pb 5,7e-11 · k_moyen_avant_pb 0,6815 · k_moyen_apres_pb 1,1043 · delta_k_pb −0,6587 ·
erreur_type_pb 0,3733 · borne_inf_90_pb −1,2728 · borne_sup_90_pb −0,0445 · marge_zone_grise −0,5445.

Mon recalcul des colonnes 16 et 33-38 redonne celles du fichier à 6·10⁻¹¹ pb près ; le K du fichier et le mien diffèrent
d'au plus 9·10⁻¹¹ pb. Δ̂ est négatif : K est **plus élevé** après 2021 qu'avant.

## Lectures retenues aux points ambigus

1. **Contrôle 5, écart de 7 à 9 jours civils.** Lu littéralement : la règle chiffrée (7 à 9) s'applique ; la parenthèse
   (« cinq jours ouvrés, au plus deux fériés ») est lue comme sa justification. Autre lecture littérale : la parenthèse
   est la règle, et les trois lignes ci-dessous la respectent (un seul férié). Les deux lectures donnent `schema_ok` = 0
   ou 1 ; j'inscris 0, la lecture du chiffre écrit étant la plus littérale. Aucun autre nombre n'en dépend.
2. **Contrôle 4.** « Postérieure d'au plus 20 jours » lu comme 0 < délai ≤ 20 (délais observés : tous dans cette plage).
3. **Contrôles 6 et 7** appliqués aux seules valeurs présentes (« quand les deux sont présents » pour 7 ; pour 6, une
   valeur vide n'est pas hors plage). Le coupon est exigé présent.
4. **Contrôle 8, colonne 42** : `convention_ok` recalculé à partir des colonnes 13, 15, 16 et 33 du fichier ; une valeur
   vide donne 0.
5. **`ecart_max_rdt_pb`** : sur les colonnes 33 à 38 seulement, lignes `avant` et `apres`. La colonne 16 (non un
   rendement) est recalculée à part : écart maximal 1·10⁻¹⁶ pour 100.
6. **Statistique** calculée avec mes propres rendements (section 6), sur P défini par la colonne `dans_p` du fichier.
7. **Contrôle 5, « aucun prix FedInvest postérieur à J »** : vérifiable seulement par les dates portées (`date_jm5`,
   `date_adjudication`) ; le lien entre le paramètre GSW et sa date dans D2 ne peut pas être vérifié depuis le fichier.

## Violation de schéma

Contrôle 5 (écart `date_jm5` → J hors de 7 à 9 jours civils) sur trois lignes, toutes dans P, écart de 10 jours :
`9128282A7_2016-09-12`, `91282CCB5_2021-07-12`, `91282CFF3_2022-09-12`.
**Nature : lignes correctes que la formulation n'a pas prévues.** Les trois adjudications ont lieu un lundi, et le lundi
précédent est férié (Labor Day 2016 et 2022, Independence Day observé le 5 juillet 2021). Cinq rangs en arrière dans le
calendrier GSW tombent alors sur le vendredi d'avant : deux week-ends et un férié, soit 10 jours. Ce n'est ni une erreur
de données ni un regard vers l'avenir (`date_jm5` < J, jour ouvré). La borne « 7 à 9 » suppose un seul week-end dans la
fenêtre, ce qui est faux pour une adjudication du lundi. Tous les autres contrôles (1-4, 6-8) passent.

Sans ces trois lignes (descriptif) : n 204/115, grappes 96/39, K moyen 0,664/1,129, Δ̂ = −0,710, ET 0,374,
IC 90 % [−1,326 ; −0,094], marge −0,594. Rien ne change qualitativement.

## Autres constats

- Hors de P : `912810TC2_2021-12-02` (20 ans, prix FedInvest absent à J−5 = 2021-11-24, le titre n'étant sans doute pas
  encore émis ce jour-là) et `912810UX4_2026-10-21` (sans `high_yield`, annoncé en section 4). Le 20 ans `avant` n'a donc
  que 13 lignes dans P.
- Trois lignes de P ont une clôture d'adjudication à 11 h ou 11 h 30 (2012-09-13, 2012-12-12, 2019-06-21) ; la
  préinscription ne les écarte pas. K = −4,05 ; −5,46 ; 0,04.
- `beta0` GSW quasi nul (< 0,01) sur 42 lignes de P depuis 2019-12 : propriété de l'estimation GSW (borne), pas une
  erreur ; le contrôle 7 passe sur ces lignes.
- Valeur extrême : `912810SL3_2020-03-12` (30 ans, mars 2020), K = −25,9 pb ; écart-type de K en 2020 : 6,4 pb.
- Écart-type de K : 3,00 pb avant, 2,82 pb après (n − 1), ET obtenue 0,37 pb : entre les cas favorable et central de la
  section 7. Médianes : 0,83 avant, 0,71 après.
- Descriptif : S1 (C en niveau, sur P) Δ = +3,56 (ET 0,72) ; S3 (prime Π à J−5) Δ = +4,22 (ET 0,70), surtout à 30 ans
  (−2,6 → −11,5 pb) ; S2 montée à la clôture R : Δ = −0,64 (ET 0,28), reste A : Δ = −0,02 (ET 0,27). La comparaison en
  niveau aurait donc donné un Δ fortement positif porté par le déplacement de la prime que A1 voulait neutraliser.

## Fragilité

- **Par année.** K moyen 2010-2021 entre −0,41 (2012) et 1,99 (2014) ; 2022 −0,16 ; 2023 **3,34** ; 2024 0,84 ;
  2025 0,66 ; 2026 0,79. Δ̂ de chaque année d'après contre tout l'avant : 2022 +0,60 [−0,13 ; 1,33] ;
  2023 −2,88 ; 2024 −0,29 ; 2025 −0,05 ; 2026 −0,25. Sans 2023 : Δ̂ = −0,04, IC [−0,55 ; 0,48]. En retirant une année
  quelconque, la borne haute reste entre −0,26 et 0,48 (toujours < 0,5).
- **Sans chaque échéance.** Sans 10 ans : Δ̂ −0,94 [−1,75 ; −0,12] ; sans 20 ans : −0,77 [−1,45 ; −0,09] ; sans 30 ans :
  −0,22 [−0,94 ; **0,51**]. La hausse de K vient surtout du 30 ans (seul : −1,26) ; sans lui la borne haute frôle 0,5.
- **Sans les cinq réouvertures les plus influentes** (retrait exact une à une : 2020-03-12 30 ans, 2023-07-13 30 ans,
  2023-09-13 30 ans, 2026-06-11 30 ans, 2023-12-11 10 ans) : Δ̂ = −0,22, ET 0,30, IC [−0,70 ; 0,27].
- Le signe négatif de Δ̂ dépend de 2023 et des réouvertures à 30 ans ; la position de la borne haute sous 0,5 tient dans
  toutes les découpes sauf le retrait du 30 ans (0,506).
