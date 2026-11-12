# F04 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `F04_analyse.csv`, rien d'autre. Je n'ai ouvert ni le code ni les résultats de
l'expérimentateur. Code : `verification.py`. Nombres : `verification.json`.

## Lectures retenues aux points ambigus

- **Lecture du fichier.** Tout est lu en texte (aucune conversion implicite) ; un champ vide est une valeur manquante. Les
  rendements sont pris tels qu'écrits, sans arrondi.
- **Contrôle 2, valeurs permises.** `type_ligne` ∈ {reelle, placebo} ; `echeance` ∈ {2, 3, 5, 7, 10, 20, 30} ; `reouverture`,
  `principal`, `complet`, `fenetre_propre` ∈ {0, 1}.
- **Contrôle 7, « pour chaque date ».** Lu comme : pour chaque ligne et chacune des trois dates (J − 5, J, J + 5),
  |cmt − gsw| ≤ 1 lorsque les deux valeurs existent.
- **Échantillon P et placebo.** Appliqués tels qu'écrits, avec les colonnes `complet` et `fenetre_propre` du fichier.
  J'ai aussi recalculé ces deux colonnes moi-même ; elles concordent sur les 1 606 lignes. Pour un placebo, « autre
  adjudication » s'applique à toutes les adjudications `reelle`, l'adjudication d'origine comprise (elle tombe de toute façon
  avant `date_jm5`).
- **Erreur type.** Formule de la section 6 appliquée telle quelle : (1/N) · racine(G/(G − 1) · Σ_g S_g²), sans autre facteur.
- **`marge_zone_grise`.** min(2 − t, B − 0,5), avec B = V̄ + 1,96 · ET.

## Contrôles de schéma

Les huit contrôles passent : `schema_ok` = 1. 1 606 lignes (1 285 `reelle`, 321 `placebo`), 321 lignes `reelle` avec
`principal` = 1.

## Autres vérifications sur le fichier

- Aucun doublon : ni `id_ligne`, ni (cusip, date, type), ni ligne identique hors identifiant. Tri conforme.
- Les nombres par `terme_api` correspondent exactement au tableau D1 (201 × 4, 67/26/67, 67 + 68, 25 + 27, 67 + 67).
  `reouverture` et `id_ligne` sont cohérents avec `terme_api`, `cusip` et la date.
- Rendements cohérents entre lignes : une même échéance à une même date porte toujours les mêmes valeurs `cmt` et `gsw`.
  `cmt` a toujours deux décimales, comme les séries FRED.
- Aucune date de week-end. Les fenêtres font 7 à 11 jours civils pour 5 rangs ; les plus longues correspondent toutes à des
  jours fériés (fêtes de fin d'année, 4 juillet, Labor Day, MLK, Presidents' Day, Thanksgiving). Le fichier ne permet pas de
  reconstruire C en entier, donc les rangs eux-mêmes ne sont pas vérifiables.
- Placebo : `date_j` est 14 à 17 jours civils après l'adjudication, ce qui va avec J + 10 jours ouvrés. Le placebo garde le
  cusip de la réouverture d'origine. 3 placebos sur 321 ont `fenetre_propre` = 0 (recalcul identique) ; il en reste 318.
- Toutes les 321 réouvertures sont `complet` = 1 et `fenetre_propre` = 1 : N = 321, comme annoncé, et les sous-périodes
  comptent 80, 190 et 51 lignes, comme prévu en S3.

## Points à signaler (sans effet sur le schéma)

- **Placebo et adjudication partagent une date.** Pour chaque placebo, `date_jm5` = `date_jp5` de la réouverture réelle
  correspondante (même valeur de rendement). C'est une conséquence mécanique de « J + 10 » avec une fenêtre de ±5, pas une
  erreur. Mais le placebo n'est donc pas indépendant de l'échantillon principal : E(J + 5) de l'adjudication entre dans les deux.
- **Hétérogénéité par échéance (descriptif).** V̄ ≈ 1,17 pb à 10 ans (135), ≈ 1,04 pb à 30 ans (134), ≈ −0,13 pb à 20 ans (52).
- **Écart-type de V sur P** : 2,57 pb, dans la fourchette supposée en section 7 (2 à 5 pb).
- Rien d'impossible ni d'invraisemblable relevé dans les valeurs.
