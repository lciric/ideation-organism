# K01 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `K01_analyse.csv`, rien d'autre. Je n'ai vu ni le code ni les chiffres de
l'expérimentateur. Code : `verification.py`. Sortie : `verification.json`. Ce rapport ne donne pas de verdict.

## Contrôles de schéma (section 6)

Les 12 contrôles passent sur le fichier tel qu'il est : `n_violations_schema` = 0. Comptes : 14 255 lignes SPF et 291 BCE,
22 colonnes dans l'ordre, tri conforme. Tous les comptes attendus sont retrouvés : 8 595 lignes dans E, 94 prévisionnistes,
96 tours, 24 cibles, 4 393 lignes d'horizon 0 et 4 202 d'horizon 1, de 47 à 108 lignes par tour (médiane 92), 7 425 lignes
hors 2021-2023, 6 269 avant 2020, 188 cellules de consensus et 188 cellules BCE (96 d'horizon 0, 92 d'horizon 1).

Points vérifiés en plus :
- **Révision.** `prevision_prec` est la prévision du même prévisionniste, pour la même cible, au tour `t_tour − 1`. L'égalité
  est exacte en flottant sur toutes les lignes : les prévisions ont au plus 5 décimales et sont écrites avec 6.
- **Instrument.** C'est la révision du même prévisionniste, au même tour, pour l'autre année (y + 1 à l'horizon 0, y − 1 à
  l'horizon 1). Il est identique à la colonne `revision` de la ligne désignée (écart maximal 0). Il ne contient ni π(y) ni
  F(i, t, y).
- **Antériorité.** `horizon` ≥ 0 sur toutes les lignes : aucune prévision ne porte sur une année antérieure à celle de son
  tour.
- **Signes.** `erreur` = `realise` − `prevision` et `revision` = nouvelle − ancienne, à 10⁻¹⁵ près.
- **Réalisé.** Une seule valeur par année. Les valeurs sont plausibles (2009 : 0,3 ; 2022 : 8,4 ; 2023 : 5,4).
- **Règle des 8 tours.** Elle retire 11 identifiants, comme l'annonce le préenregistrement.

## Lectures retenues sur les points ambigus

1. **Contrôle 7, « une décimale au plus ».** Je l'ai lu sur le texte de la cellule `realise`. Toutes les cellules ont une
   décimale.
2. **Contrôles 8 et 9, « égale ».** J'ai lu une égalité numérique stricte (tolérance 10⁻¹²). L'égalité exacte passe aussi,
   donc les deux lectures ne changent rien.
3. **Année du tour.** Je l'ai tirée de `tour` (AAAA), soit `t_tour` // 4. Pour la BCE, c'est l'année du millésime.
4. **Consensus.** C(t, y) est la moyenne de toutes les lignes SPF du tour t et de la cible y, que la ligne ait une prévision
   précédente ou non. C'est la lecture littérale : la révision du consensus inclut donc les entrées et sorties du panel.
5. **LRV₈.** Les couples sont formés sur l'écart des numéros de tour. Dans E′, les 8 tours de 2021-2022 manquent.
   L'écart entre 2020T4 et 2023T1 vaut 9, donc aucun couple ne traverse le trou, et la question ne se pose pas.
6. **`b_consensus_hors_2021_2023` et `b_bce_hors_2021_2023`.** Le texte dit « mêmes pentes », sans préciser où les moyennes
   d'horizon sont retirées. Deux lectures sont possibles :
   - moyennes retirées dans le sous-échantillon, comme pour E′ : 0,515 et 0,162. **C'est la lecture retenue dans le json.**
   - moyennes de l'échantillon complet : 0,782 et 0,365.

   L'écart dépasse la tolérance. L'expérimentateur pourrait avoir choisi l'autre lecture.
7. **Effets fixes.** Les résidus MCO sur les indicatrices d'identifiant et l'indicatrice `horizon` = 1 sont calculés sur
   l'échantillon de chaque statistique : E pour `b_iv_ef_prev`, E restreint aux cibles ≤ 2019 pour `b_mco_ef_avant_2020`.
8. **Bornes de bruit.** Elles valent 0 par la formule max(0, −b), car les deux pentes sont positives.

**Contrôle croisé.** Avec `linearmodels` 7.1, je retrouve b_IV (IV2SLS avec deux constantes d'horizon), le coefficient de
première étape, et l'écart-type de Driscoll-Kraay de la pente MCO naïve (PanelOLS, noyau de Bartlett, largeur 8 :
0,188360). Les trois sont identiques à mes calculs.

## Ce qui est peu plausible ou à signaler

- **b_IV = +1,151** (écart-type 0,463), hors de la plage attendue par le rédacteur (−0,3 à +0,3, écart-type de l'ordre de
  0,25). Il est aussi plus grand que la pente du consensus (0,918).
- Cette valeur est une moyenne de deux horizons très différents, pondérés presque à égalité (Σ z̃ x̃ ≈ 525 et 522) :
  - horizon 0 : 0,279 (écart-type 0,099) ;
  - horizon 1 : 2,027 (écart-type 0,849).

  La première étape est forte dans chaque horizon (F ≈ 64 et 67), mais ses coefficients diffèrent (0,65 et 0,40). Le F
  regroupé vaut 514.
- L'écart-type de Driscoll-Kraay (0,463) est plus grand que celui groupé par année cible (0,293). Sur avant 2020, il vaut
  0,604, plus que sur l'échantillon complet. C'est inhabituel mais possible : les révisions de l'horizon 1 sont peu
  dispersées et les erreurs de l'horizon 1 très dispersées.
- **Pente intra-tour : −0,452.** C'est proche du −1/2 mécanique de la section 2.1, comme annoncé.

## Fragilité

- **Sans une année cible à la fois.** b_IV va de 0,895 (sans 2023) à 1,320 (sans 2009). La borne basse à 90 % devient
  négative seulement sans 2022 (−0,043) ou sans 2023 (−0,058). Dans les 24 cas, la marge d'indécision reste négative
  (au plus −0,092).
- **Sans 2021-2023.** b = 0,168 (écart-type 0,466). L'IC 90 vaut [−0,631 ; 0,967] et contient 0 comme −0,15. F = 315.
- **Par horizon, hors 2021-2023.**
  - horizon 0 : 0,100 (écart-type 0,077) ;
  - horizon 1 : 0,225 (écart-type 0,849).
- **Avant 2020.**
  - b_IV = 0,134 (écart-type 0,604) ;
  - MCO avec effets fixes = 0,043 (écart-type 0,095), contre −0,169 (0,182) chez Broer et Kohlhas.

**Lecture.** La pente est positive dans toutes les coupes. Son éloignement de zéro et de −0,15 tient à l'épisode 2021-2023
et surtout à l'horizon 1 : avec cet épisode, on observe de grandes erreurs sur l'année suivante.
