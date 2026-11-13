# K11 — écarts à la préinscription (expérimentateur)

## En tête : contradiction interne du contrôle de schéma n° 5, révélée par les données

Ce n'est pas une affirmation chiffrée fausse sur les données (aucune n'a été trouvée : voir la fin de ce fichier), mais une
règle que le fichier d'analyse **ne peut pas satisfaire** quand on applique la préinscription à la lettre.

- La section 4.4 (étape 4) et la colonne 79 prévoient qu'une ligne soit `prix_manquant` lorsqu'il reste « moins de trois
  témoins valides après remplacements ». C'est arrivé : **8 lignes** (2013-04-10, 2013-12-11, 2016-04-13, 2017-10-11,
  2017-12-11 et 2019-07-10 à 10 ans ; 2023-06-21 à 20 ans ; 2023-09-12 à 10 ans). Sur chacune, 3 à 5 candidats à 18 mois ou
  moins avaient un prix `END OF DAY` identique à J−5 et J ou à J et J+5 (« figés »), et la liste des candidats s'est épuisée
  avant d'atteindre trois témoins (il reste 0, 1 ou 2 témoins).
- Le contrôle 5 (section 5.3) exige pourtant, sur **toute ligne non écartée par les métadonnées**, « trois CUSIP distincts »
  et `rang_t1 < rang_t2 < rang_t3`. Ces 8 lignes ne peuvent pas avoir trois témoins sans violer la règle de sélection 4.4.
- **Lecture littérale retenue** (consigne : la plus littérale) : le contrôle 5 échoue sur ces 8 lignes, donc
  **`schema_ok` = 0** dans `temoin.json`.
- **Autre lecture** (contrôle 5 appliqué aux seuls témoins présents, ou aux lignes qui ont trois témoins) : tous les autres
  éléments du contrôle 5 passent (rangs, échéances, écarts de mois, premier ancien = rang 1, témoins parmi les 3 + s premiers
  candidats refaits sur D1), et **`schema_ok` = 1**. `construire.py` imprime les deux (`controle 5` et `controle 5bis`).
- Aucun autre champ de `temoin.json` ne dépend de cette lecture : les 8 lignes ont `dans_p` = 0 dans les deux cas.

## Autres écarts et choix d'interprétation (du plus au moins important)

1. **Pages FedInvest copiées de J05.** Sur les 905 dates requises, 614 pages ont été copiées sans modification depuis
   `tests-de-mort/J05/donnees/fedinvest/` (consigne de l'orchestrateur) au lieu d'être téléchargées par K11 ; 291 ont été
   téléchargées par K11. La préinscription demande que l'expérimentateur enregistre chaque page « avec la date de
   téléchargement » : pour les copies, la date notée dans `PROVENANCE.md` est l'heure d'écriture du fichier par J05
   (conservée par `shutil.copy2`), pas une date de téléchargement par K11. Contrôle : 17 dates copiées (une par année,
   2010 à 2026) ont été retéléchargées dans `donnees/fedinvest_controle/`. **Aucune n'est identique octet par octet** : la
   seule différence, sur chacune, est le jeton de session `_csrf` (deux lignes `<input type="hidden" name="_csrf" ...>`,
   jeton aléatoire par session) ; le tableau de prix extrait est identique pour les 17 (`comparaison_controle.txt`). Les 614
   copies sont identiques octet par octet à leur source J05 (vérifié par `cmp`).
2. **D1 n'a pas été repris de J05.** La réponse de l'API conservée par J05 a une autre liste de champs (pas
   d'`original_security_term`) ; K11 a fait la requête exacte de la section 4.1 (HTTP 200, 2 793 lignes, une page). Ce n'est
   pas un écart à la préinscription ; noté pour la traçabilité.
3. **Colonnes des lignes écartées par les métadonnées** (10 lignes : `hors_calendrier`, `temoins_insuffisants`,
   `titre_non_emis_a_jm5`). La section 5.1 permet de laisser vides les colonnes 18 à 78, mais le contrôle 2 exige
   `identite_fi_ok` ∈ {0, 1} sur toutes les lignes : `identite_fi_ok` = 0 y est écrit (pas vide). `rdt_limite_pct` et
   `prix_limite` (54-55, tirés de D1) y sont remplis ; les autres colonnes 18-78 sont vides. Aucune page FedInvest n'a été lue
   pour ces lignes (leurs dates ne sont pas dans les 905).
4. **Lignes `prix_manquant` faute de trois témoins.** Les témoins valides trouvés (0 à 2) sont écrits dans `cusip_t1`, …
   dans l'ordre ; les places restantes sont vides. `identite_fi_ok` = 0 (la définition porte sur « les trois témoins », qui
   n'existent pas) ; `complet` = 0 ; E, V, montée, détente, V_PA et `p_carte_pb` vides (une entrée manque). Les prix et
   rendements du titre rouvert et du premier ancien y sont remplis.
5. **Format des nombres.** Écrits par `repr` de Python (plus courte écriture qui redonne exactement le flottant) : aucun
   arrondi, mais les nombres exacts courts (prix au 1/32 comme `101.71875`, coupons comme `2.375`) ont moins de 10 chiffres
   significatifs. Lecture retenue : « sans arrondi » prime ; ajouter des zéros n'apporterait rien.
6. **Précision du rendement.** `construire.py` résout Y(P, d) par bissection jusqu'à 10⁻¹² point (plus strict que les
   10⁻⁹ demandés). Le second code (`analyse.py`, Newton, dates de coupon générées autrement) s'arrête à 10⁻¹³.
   `ecart_max_rdt_pb` porte sur les 12 rendements des colonnes 56-67 (titre et témoins), pas sur ceux du premier ancien.
7. **V utilisés pour les statistiques.** `analyse.py` calcule les statistiques avec les V recalculés par son second code
   (« ses propres V ») ; ils diffèrent de la colonne `v_pb` d'au plus 1,9 × 10⁻¹⁰ pb, et la moyenne principale ne change
   qu'au-delà de la dixième décimale.
8. **Identité FedInvest.** `RATE` (« 2.375% ») est comparé numériquement à `int_rate` (« 2.375000 ») à 10⁻⁹ près ;
   `MATURITY DATE` est lue comme date. Un CUSIP présent deux fois sur une page serait traité comme absent (cas non rencontré).
9. **Prix figés.** L'égalité est testée sur les prix lus en flottant (équivalent à l'égalité des chaînes à 6 décimales de
   FedInvest).
10. **Client de téléchargement.** `curl` (agent par défaut), une session (fichier de témoins neuf) par date, sans suivre la
    redirection ; pause d'une seconde ; jusqu'à 5 essais avec attente de 5, 10, 20, 40 s. Un seul incident : 2010-03-17,
    connexion réinitialisée au premier GET, réussie au deuxième essai. Les 291 + 17 téléchargements ont répondu
    200 / 302 / 200 avec la date affichée égale à la date demandée.
11. **Descriptifs non préinscrits.** `analyse.py` imprime aussi V̄ par année pour 2010-2021 (toutes échéances de P), utilisé
    par `figure.png`. C'est descriptif, hors préinscription, sans effet sur `temoin.json`.

## Affirmations de la préinscription vérifiées sur les données (aucune trouvée fausse)

324 réouvertures (97/14/96 avant, 39/39/39 après) ; J ∈ C pour toutes ; écarts J − (J−5) de 7 (209 + 52 = 261), 8 (60) ou
10 (3) jours et (J+5) − J de 7 (272) ou 8 (52) ; 905 dates distinctes dont 316 en 2022-2026 ; candidats à 6, 9 et 12 mois
(313 lignes) et 6, 9, 18 mois (30 ans du 2010-01-14) ; 0, 0, 0, 0, 1, 1, 2, 2 candidats pour les huit 20 ans du 2020-06-17 au
2021-04-21 ; seul `titre_non_emis_a_jm5` : 912810TC2_2021-12-02 ; rang 0 = titre rouvert partout ; toutes les échéances
utilisées tombent le 15 ; seule réouverture étudiée sans `high_yield` : 2026-10-21 ; aucune page vide parmi les 905 dates.
L'hypothèse de dispersion de la section 7 (σ ≈ 3,2 pb) est une supposition déclarée, pas un fait : l'écart-type observé de V
est de 0,78 pb (après) et 0,94 pb (avant, 10 et 30 ans).
