# F01 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `panel.csv`, rien d'autre (ni code, ni résultats, ni journaux de l'expérimentateur).
Code : `verification.py` (MCO exacts par équations normales sur matrice creuse, jackknife par année codé à la main).
Sortie : `verification.json`. Aucun verdict n'est rendu ici.

## Nombres (verification.json)

theta −0,0639 ; se_theta 0,1205 ; IC95 [−0,3195 ; 0,1916] ; marge_ambiguite 0,0195 ; tau_bar −0,0443 ; m_bar 0,6938 ;
b_attente −0,2257 ; t_avance −1,148 ; T : 9 942 lignes, 185 anomalies ; 8 712 lignes `attente` ; 40 blocs ; 0 violation de schéma.

## Lecture des points ambigus

1. **Ensemble K (« au moins 60 lignes `origine` »).** Lu sur toutes les dates du fichier (§ 3 : l'anomalie « reste dans
   `panel.csv` », le compte se fait sur ses lignes ; § 4 annonce 210 anomalies dans U, cohérent avec cette lecture).
   Exclues : AnalystRevision, ConsRecomm, DownRecomm, UpRecomm. **Autre lecture** (60 lignes `origine` dans la fenêtre
   1974-2013) : K exclut en plus BM, Beta, DivYieldST, EP, Price, Size, et donne theta −0,0486, se 0,1239,
   IC [−0,3113 ; 0,2142], marge 0,0113, tau_bar −0,0337, m_bar 0,6949, b −0,2245, t_avance −1,110, T 9 702 lignes /
   181 anomalies, 8 568 lignes `attente`. Les deux lectures donnent marge_ambiguite ≥ 0. Retenue : toutes dates.
2. **Jackknife.** K et `moy_origine` non recalculés ; T redéfini à chaque bloc (anomalie et mois encore présents dans U réduit).
   Les 40 années 1974-2013 ont toutes des lignes dans U. `t_avance` = d̂ (échantillon complet) / se_d jackknife centré sur
   la moyenne des d_g.
3. **Contrôle 9.** Moyenne recalculée sur les lignes dont le statut recalculé est `origine` (identique au statut du fichier).
4. **Contrôle 10.** Rang testé sur la matrice dense de U complet : 686 colonnes (206 anomalies, 479 mois, `attente`), rang 686.

## Schéma

Les 10 contrôles passent : colonnes et ordre exacts, aucun doublon (signal, date), 212 signaux, dates valides, médiane
|ret| = 1,65, années constantes et D ≤ F < P avec P dans 1973-2016, `statut`, `dans_fenetre` et `moy_origine` exacts
(à 1e-8), fichier trié par signal puis date, 175 529 lignes.

## Ce qui mérite attention

- **marge_ambiguite = 0,0195**, proche de 0 (tolérance 0,015) : la borne basse (−0,319) est à 0,02 de −0,30.
- **Effectifs** : 9 942 lignes traitées (10 296 attendues), 185 anomalies (189 ; les 4 manquantes sont exactement les
  4 exclues par K), 8 712 lignes `attente` (8 904), 56 173 `origine` (57 204), 206 anomalies dans U (210). Écarts de 2-3 %,
  dus aux rendements manquants ; Beta et Price (P = 1973) n'ont aucune ligne U dans la fenêtre, comme prévu.
- **Concentration** : 2005-2013 portent 6 618 des 9 942 lignes traitées. Les blocs 2008 (theta_g −0,121) et 2009 (+0,016)
  pèsent le plus. Retirer les 5 anomalies au tau le plus négatif (Mom6mJunk, MomVol, MomRev, Size, BidAskSpread) donne
  theta +0,016 ; retirer les 5 plus positives donne −0,122 : l'estimation dépend d'une poignée d'anomalies de type momentum.
- **Rendements extrêmes** : max 321,3 % (IO_ShortInterest, 2021-01, hors fenêtre), min −83,6 % ; aucun ≤ −100 %.
  Dans la fenêtre, les |ret| > 30 % se groupent sur des mois connus (1975-01, 2000-02, 2001-01, 2009-04). Plausibles pour
  du long-court, mais très influents sur un estimateur non pondéré.
- **Moyenne d'origine négative** pour trois anomalies traitées (VarCF −0,59, GrSaleToGrOverhead −0,03, FirmAge −0,02) :
  elles entrent dans m_bar sans filtre, conformément au texte.
- **Quasi-doublon** : PriceDelaySlope et PriceDelayTstat, corrélation 0,996 dans la fenêtre (deux anomalies comptées pour une).
- **Trous de séries** : 16 anomalies ont des mois manquants internes (DivOmit 20 trous, ChNAnalyst 9). Les fins de série
  diffèrent un peu des notes de version citées : PatentsRD va jusqu'en 2008 (texte : 2006), ProbInformedTrading jusqu'en
  2013 (texte : 2012). Pas de ligne remplie à zéro détectée.
- Années de publication : réparties de 1973 à 2016, aucune incohérence D ≤ F < P ; attente de 1 à 10 ans (moyenne 3,6).
