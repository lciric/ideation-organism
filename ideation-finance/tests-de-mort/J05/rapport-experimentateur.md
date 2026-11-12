# J05 — Rapport de l'expérimentateur

Rôle : expérimentateur. Ce rapport décrit ce qui a été fait et les nombres obtenus ; il ne contient pas de verdict. Les
nombres de `temoin.json` sont un témoin ; le verdict se calcule sur ceux du vérificateur. Préinscription lue en entier,
non modifiée (`sha256sum -c preenregistrement.md.sha256` : OK). **Lire `ecarts.md` d'abord : `schema_ok` vaut 0** à cause
d'une plage de dates inexacte dans le contrôle 5 de la préinscription (E1).

## 1. Ce qui a été fait

1. **Données** (toutes dans `donnees/`, brutes, non modifiées ; `donnees/PROVENANCE.md` donne URL, heure, sha256, lignes) :
   - D1 `auctions_query.json` : la requête exacte de la section 4, téléchargée le 2026-11-12 à 21:20 UTC ; HTTP 200,
     2 375 lignes, une page. Le fichier de F04 n'a pas été réutilisé : il n'avait ni `int_rate`, `high_yield`, `high_price`,
     `accrued_int_per1000`, … ni de date après le 2026-09-24.
   - D2 `feds200628.csv` : retéléchargé le 2026-11-12 à 21:20 UTC ; sha256 identique à la copie de F04
     (`dfaad994…`). En-tête à la ligne 10, colonnes `BETA0`–`TAU2` présentes, dernière date 2026-11-06 (celle attendue).
   - D3 FedInvest : `telecharger_fedinvest.py` applique la procédure en trois étapes (GET avec témoin et `_csrf`, POST
     `priceDate=…&submit=Show+Prices&_csrf=…` → 302, GET `securityPriceDetail` → 200), une date à la fois, session neuve à
     chaque date, pause d'une seconde, jusqu'à 5 tentatives, chaque page mise en cache sur disque
     (`donnees/fedinvest/AAAA-MM-JJ.html`) et journalisée (`donnees/fedinvest_journal.csv`). **630 dates demandées
     (J et J−5 de toutes les réouvertures `avant` et `apres`), 630 obtenues au premier essai, 0 échec**, de 21:21 à 21:56
     UTC. Toutes les pages affichent « Prices For: » à la date demandée et un tableau rempli (256 à 464 titres) ; en-tête du
     tableau conforme (`CUSIP, SECURITY TYPE, RATE, MATURITY DATE, CALL DATE, BUY, SELL, END OF DAY`).
2. **`construire.py`** relit uniquement `donnees/`, construit `J05_analyse.csv` (389 lignes × 45 colonnes, ordre et noms de
   la section 5.1), applique les conventions de 5.2 (dates de coupon nominales au 15, coupon couru, rendement Y par
   bissection à 10⁻¹² point, courbe de Nelson-Siegel-Svensson avec m = jours/365,25, g_terme en prix à terme pour règlement
   s, g au comptant, f sur `END OF DAY`) puis relit le fichier écrit et exécute les huit contrôles de 5.3
   (résultat dans `construire_journal.json`). Formule GSW contrôlée contre `SVENY01/10/30` sur 4 215 dates depuis 2010 :
   écart maximal 5·10⁻⁵ point, soit l'arrondi à 4 décimales de `SVENY`.
3. **`analyse.py`** relit `J05_analyse.csv`, recalcule avec un code distinct les colonnes 16 et 33 à 38 (et K), et estime la
   régression préinscrite (MCO sans constante, `apres` + trois indicatrices d'échéance, ET groupée par mois avec le seul
   facteur G/(G − 1)) ; écrit `temoin.json`, `resultats_analyse.json` et `figure.png`.

## 2. Échantillon à chaque filtre

| Étape | `ancien` | `avant` | `apres` |
|---|---|---|---|
| Lignes D1 (Note/Bond, 1991-01-01 à 2026-10-31) | — | — | 2 375 au total |
| Réouvertures nominales à taux fixe 9-, 19-, 29-Year (= lignes du fichier) | 65 | 207 (97 ; 14 ; 96) | 117 (39 ; 39 ; 39) |
| écartées pour `first_int_period` ≠ "Normal" | 0 | 0 | 0 |
| `high_yield` et `high_price` présents | 65 | 207 | 116 (manque : `912810UX4_2026-10-21`) |
| J présent dans C (GSW du jour même) | 65 | 207 | 117 |
| `convention_ok` = 1 | 51 | 207 | 116 |
| Prix FedInvest à J−5 présent | — | 206 | 116 |
| `complet_k` = 1 | 0 (par définition) | 206 | 116 |
| **P (`dans_p` = 1)** | — | **206** | **116** |
| mois distincts dans P | — | **96** | **39** |
| `complet_r` = 1 dans P (S2) | — | 206 | 116 |

- La ligne `avant` perdue est `912810TC2_2021-12-02` (réouverture du 20 ans) : à son J−5 (2021-11-24) le titre n'était pas
  encore émis (émission initiale le 2021-11-30), donc absent du tableau FedInvest. Comptée manquante selon la règle.
- Les 14 lignes `ancien` en échec de convention (8 adjudications « Multi-Price » de 1992 à 1998 et 6 « Single-Price » de
  1999 à 2002 ; écart entre Y(`high_price`) et `high_yield` de 0,0010 à 0,0023 point) ne servent qu'à S1a, qui les exclut.
- Comptes conformes aux attendus de la section 4 (65 ; 207 ; 117) et aux plages du contrôle 3.

## 3. Contrôles

| Contrôle (5.3) | Résultat |
|---|---|
| 1 colonnes | OK |
| 2 identifiants, échéance, mois, période, indicatrices | OK |
| 3 dates et comptes par période | OK (65 ; 207 ; 117) |
| 4 règlement et échéance | OK (délai 1 à 15 jours) |
| **5 pas de regard vers l'avenir** | **échec sur 3 lignes** : `date_jm5` à 10 jours de J (lundi d'adjudication après un lundi férié) ; voir `ecarts.md` E1. Aucun paramètre GSW ni prix postérieur à J : `date_gsw_j` = `date_adjudication` sur les 389 lignes, `date_jm5` < J toujours, jamais un week-end. |
| 6 plages | OK |
| 7 appariement | OK (max \|f(J−5) − g(J−5)\| = 0,31 point ; max \|f(J) − `high_yield`\| = 0,16 point) |
| 8 formules et indicatrices | OK |
| **`schema_ok`** | **0** |

Convention de rendement : sur les 323 lignes `avant`/`apres` avec un prix, max \|Y(`prix_limite`, s) − `high_yield`\| =
0,00098 point (sous la tolérance de 0,001, mais près d'elle) ; max \|AI calculé − AI de l'API\| = 5·10⁻⁷.
`n_echec_convention` = 0. L'écart vient de la période fractionnaire actualisée en composition dans la préinscription et en
intérêt simple par le Trésor (`ecarts.md` E2).

## 4. Statistique principale (témoin)

| Champ | Valeur |
|---|---|
| `schema_ok` | 0 |
| `n_avant` / `n_apres` | 206 / 116 |
| `n_grappes_avant` / `n_grappes_apres` | 96 / 39 |
| `n_echec_convention` | 0 |
| `ecart_max_rdt_pb` | 3,6·10⁻¹¹ |
| `k_moyen_avant_pb` | 0,6815 |
| `k_moyen_apres_pb` | 1,1043 |
| `delta_k_pb` (Δ̂ = −b̂) | **−0,6587** |
| `erreur_type_pb` | 0,3733 |
| `borne_inf_90_pb` | −1,2728 |
| `borne_sup_90_pb` | −0,0445 |
| `marge_zone_grise` = min(−L, U − 0,5) | −0,5445 |

En mots : à échéance égale, K est **plus élevé** de 0,66 pb en 2022-2026 qu'en 2010-2021 (Δ̂ négatif) ; l'IC à 90 %
[−1,27 ; −0,04] est entièrement sous 0, donc sous 0,5. Coefficients d'échéance (niveau de K en 2010-2021) : 10 ans 1,27 pb ;
20 ans −0,15 pb ; 30 ans 0,20 pb. Moyennes simples par période et échéance : `avant` 1,37 / 0,33 / 0,03 pb, `apres`
1,66 / 0,35 / 1,29 pb (10 / 20 / 30 ans).

Écart-type de K sur P (dénominateur n − 1) : **3,00 pb** avant, **2,82 pb** après (hypothèse centrale de la section 7 :
3,2 et 4,2). ET obtenue 0,37 pb, entre les cas « favorable » (0,33) et « central » (0,50).

## 5. Analyses secondaires — descriptives, sans effet sur le verdict

| Analyse | Échantillon | Δ (pb) | ET (pb) |
|---|---|---|---|
| S1a : C en niveau, `apres` contre `ancien` + `avant` | c_pb présent et `convention_ok` = 1 : 374 lignes (51 ; 207 ; 116), 180 mois | 1,840 | 0,775 |
| S1b : C en niveau, sur P | 322 lignes, 135 mois | 3,562 | 0,724 |
| S2 : R = montée de l'écart du titre à la courbe, J−5 → clôture de J | P, `complet_r` = 1 : 322 | −0,637 | 0,280 |
| S2 : A = K − R (décote d'adjudication et après-midi) | idem | −0,021 | 0,274 |
| S3 : Π = prime du titre à J−5 (f − g) | P : 322 | 4,220 | 0,697 |

- S2, moyennes simples : R = 0,16 pb avant, 0,62 pb après ; A = 0,52 pb avant, 0,49 pb après.
- S3, Π moyen (pb) par période et échéance sur P : `avant` 10 ans −4,05 (n = 97), 20 ans +2,36 (13), 30 ans −2,57 (96) ;
  `apres` 10 ans −5,92 (39), 20 ans +4,96 (38), 30 ans −11,53 (39). Par période : −2,96 avant, −4,24 après.
- Lecture descriptive : en niveau (C), la concession « baisse » de 3,6 pb sur la même fenêtre ; le déplacement de la prime
  du titre courant (Π, plus négative après 2021, à échéance égale de 4,2 pb) est du même ordre. K, qui retire Π, ne baisse
  pas.

## 6. Figure

`figure.png` : K moyen par année (2010 à 2026) avec IC à 90 % (ET groupée par mois dans l'année, 7 à 8 mois par année),
nombre de réouvertures par année, moyennes simples de chaque période, coupure du 1er janvier 2022 en pointillé. Δ̂ et son
IC à effets fixes sont rappelés dans le titre. Moyennes annuelles (pb) : 2010 0,71 ; 2011 1,87 ; 2012 −0,41 ; 2013 −0,34 ;
2014 1,99 ; 2015 0,51 ; 2016 0,95 ; 2017 0,50 ; 2018 1,09 ; 2019 0,42 ; 2020 0,04 ; 2021 0,93 ; 2022 −0,16 ; 2023 3,34 ;
2024 0,84 ; 2025 0,66 ; 2026 0,79.

## 7. Difficultés

1. **Contrôle 5 en échec par construction** (E1) : la plage « 7 à 9 jours » de la préinscription exclut le cas d'un lundi
   d'adjudication précédé d'un lundi férié (10 jours). Trois lignes. Exécuté tel qu'écrit : `schema_ok` = 0.
2. **Convention de rendement** (E2) : la formule préinscrite n'est pas exactement celle du Trésor (période fractionnaire en
   composition au lieu d'intérêt simple). Toutes les lignes passent la tolérance de 0,001, la plus proche à 0,00098.
3. **Valeurs extrêmes.** Plus petite valeur de K : −25,9 pb (`912810SL3_2020-03-12`, réouverture à 30 ans en pleine crise
   de mars 2020) ; puis −6,4 et −6,0 pb. Plus grandes : 9,9 ; 8,8 ; 8,1 pb. La moyenne de 2023 (3,34 pb) est la plus haute
   de la série. Aucune valeur n'a été retirée (la préinscription garde la moyenne, limite 9).
4. **FedInvest** a répondu sans incident (aucun 403, aucune page vide, aucune date décalée). Un seul titre manquant, pour
   une raison de calendrier d'émission (section 2).
5. La réutilisation des fichiers de F04 n'a pas eu lieu : D1 de F04 ne contenait pas les champs nécessaires ; D2 a été
   retéléchargé et s'est révélé identique (même sha256).

## 8. Fichiers

`J05_analyse.csv`, `construire.py`, `construire_journal.json`, `analyse.py`, `resultats_analyse.json`, `temoin.json`,
`figure.png`, `telecharger_fedinvest.py`, `ecarts.md`, `donnees/` (avec `PROVENANCE.md`). Pour tout reconstruire :
`python3 -I construire.py && python3 -I analyse.py` dans `tests-de-mort/J05/`.
