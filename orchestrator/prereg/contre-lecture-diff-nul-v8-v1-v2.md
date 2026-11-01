# Relecture du diff v1 vers v2 du préenregistrement « validation décisive du nul v8 »

**Verdict : diff conforme, scellable.** Les 15 corrections C1 à C15 sont appliquées fidèlement, aucun changement de fond non demandé, les 12 empreintes du bloc gelé concordent, la commande prend la v2, les 35 essais passent. Deux précisions de rédaction sont recommandées avant scellement (partie 3). Aucune n'est bloquante, mais le fichier change encore (voir le point « à remplir » plus bas), donc elles ne coûtent rien.

Phrase prête à coller pour le champ de la section 12 : « oui, par un lecteur neuf (relecture courte du diff `diff -u` v1 vers v2, 1er novembre 2026) : C1 à C15 appliquées fidèlement, aucun changement de fond non demandé, 12 empreintes du bloc gelé vérifiées par `sha256sum`, 35 essais réussis ; rapport `relecture-diff-nul-v8-v1-v2.md` ».

Pour mémoire, je n'ai pas lancé le banc et n'ai pas calculé l'empreinte de la v2. Lecteur : neuf, n'a écrit ni la v1, ni la v2, ni le code. Empreinte de la v1 relue : `894b294b…` (inchangée).

## 1. Corrections C1 à C15, une par une

Chacune a été comparée au texte « à coller » du rapport.

| n° | Où dans la v2 | Fidélité |
|---|---|---|
| C1 | section 7, conséquences | Texte identique, sauf une extension cohérente : « A2, A3, A5, A6 » au lieu de « A2, A3, A5 » (A6 vient de C13). Mon seul constat : le texte de C1 cite « A1 sur T05s ou T09g » et A1 vise bien toutes les fatales hors T12a, donc T01, T02, T03u, T03b, T04, T09l, T17s et nul exact sont de la classe linéaire. Aucun trou. |
| C2 | section 7, A5 | Identique. Repères revérifiés dans la sortie de L8 : T02 18/20, T03b 16/20, T04 19/20, T05s 19+1 = 20/20. |
| C3 | section 4 | Identique, plus l'ajout « fichiers de la section 13 ». |
| C4 | section 8 | Identique. |
| C5 | section 9 | Appliquée, avec l'écart déclaré (copies de L7, L8, L11, L12 seulement, nom de dossier `prelectures-nul-v8-2026-11-01`, sur instruction du coordinateur). J'ai recalculé : les 10 fichiers du dossier et le rapport de contre-lecture ont des empreintes pleines qui apparaissent toutes dans la v2. Spot-check de 5 empreintes du dossier de travail (L1, L2, L6, L9) : retrouvées. |
| C6 | section 3 | P1a, P1b, P1c identiques. Seul écart, voulu : P1b dit « conséquences en section 7 » au lieu de « en A1 et C1 » (une référence interne à la contre-lecture n'aurait pas de sens dans le fichier). Phrase d'ouverture de la section 3 mise à jour (« sections 6 et 7 »), bien. |
| C7 | section 6 (issue 4), section 10 | Identique. |
| C8 | section 12 | Appliquée et enrichie (liste des 15 corrections, empreinte du rapport, `e0faa4f2…`, vérifiée). Le champ « diff relu » est encore à remplir : voir « avant de sceller ». |
| C9 | section 4 | Identique. |
| C10 | section 7 (A2) et section 1 | A2 identique ; la section 1 est aussi nuancée (« à issues égales… en loi pour un même monde »), ce qui est la conséquence que le rapport demandait (« le mot trajectoire par trajectoire dans A2 doit être nuancé »). |
| C11 | section 4 | Identique (17 à 55 minutes). |
| C12 | fin de section 6 | Rédigée par l'auteur à partir d'une phrase « à trancher ». Voir partie 3. |
| C13 | section 7 (A6) | Identique. |
| C14 | section 4 | Identique. |
| C15 | section 13 | Appliquée (commit unique, identifiant noté, rejeu des 35 essais et des mutations avant la course). |

Ajouts non listés dans C1 à C15, signalés dans la section 12 (« Aussi ») et que je juge fidèles à l'esprit des corrections : en-tête, nom du fichier dans la règle de la graine et dans la commande (v2), niveau réel de Newcombe mesuré par le contre-lecteur (0,021 à 0,026 ; 0,044 à 0,051 : chiffres retrouvés dans la partie B du rapport), identifiant de commit non écrit dans le manifeste, ordre entre lecture gelée et audits en tête de section 6, renvoi de section 5 vers A4, A5 et P1b pour les valeurs « rapportées sans critère ».

## 2. Pas de changement de fond non demandé

Le diff touche exactement les endroits ci-dessus. Hypothèses (section 2), plan des lignes (18 lignes, 1 000 répétitions), seuils (Holm, 63 pour l'artefact, 0,05 pour la perte, Newcombe), prédictions P2 à P5, règle de graine (hors nom du fichier), liste d'arrêt (hors C4), classe couverte de la section 10 : inchangés. Dans la section 3, seule P1 est modifiée (C6). Le tableau de la section 9 reprend les lignes L0 à L10 à l'identique pour ce qui est vu et ajoute les empreintes (C5).

## 3. Règle C12 et deux ajouts de l'auteur

La structure de C12 est cohérente avec le reste : l'issue gouverne la mention « validé », non l'usage ; la décision du 1er novembre 2026 (« le nul ajusté devient le seul nul du juge ») est la même que dans la docstring de `pole/nul_v8.py`. Je ne peux pas vérifier la citation « 20:59 heure de Paris » ni que Lazar a bien choisi la première branche de l'alternative du rapport (rester par défaut quelle que soit l'issue) : le rapport laissait ce choix à Lazar, le fichier écrit « tranché par le directeur ». La session principale doit confirmer que c'est bien sa décision.

**3a. « v8 ne promeut jamais plus que v7, par la monotonie de la section 1 »** : exact en loi, trop absolu dans la lettre.
- Argument vérifié : la docstring de `nul_v8.py` donne 𝓝₈ ⊇ 𝓝₇ ; pour une même suite d'issues, le maximum au dénominateur est plus grand, donc W_t(v8) ≤ W_t(v7), et la règle de marge des filles ne fait que retirer des promotions. Donc, pour un même monde et une même fiche, P(promotion v8) ≤ P(promotion v7). C'est exactement ce que dit la section 1 de la v2.
- Mais la monotonie par trajectoire ne vaut qu'à issues égales. Les tirages frais ont pour graine l'empreinte de l'engagement gelé (`selection_pari.tirer_frais`, `graine_derivee(graine, "tirages-frais", gele.empreinte)`), et cette empreinte contient la bibliothèque, donc v7 et v8 ne voient pas les mêmes issues dans le banc. Et la v2 dit elle-même, en A2, que le taux observé de v8 peut dépasser celui de v7 par hasard.
- Lu « jamais » au pied de la lettre pour une exécution donnée, c'est faux ; lu en probabilité par fiche et par monde, c'est juste. Il ne couvre pas non plus les familles ajoutées : v8 est plus sûr que v7 pour les mondes où v7 promeut trop (c'est la motivation), il n'est pas démontré sûr pour les mondes hors classe (déjà dit en section 10).
- **Précision recommandée** (non bloquante) : remplacer « il ne promeut jamais plus que le nul v7 » par « il ne promeut pas plus que le nul v7, en probabilité pour un même monde ». Le sens de la règle (rien n'indique qu'un nul plus petit serait plus sûr) reste inchangé.

**3b. « une course invalidée par un audit est non jugeable »** : cohérent sur le fond, ambigu sur l'étiquette.
- La section 7 dit qu'une course invalide « ne rend aucune issue » ; la section 6 énumère cinq issues, dont deux commençant par « non jugeable » (« banc sans dents », « précision insuffisante ») et une troisième apparue en section 7 (« non jugeable (réserve log-linéaire) »). Le mot « non jugeable » de la parenthèse de C12 désigne un traitement pour l'usage, non l'issue 5.
- Conséquence concrète : aucune, car les trois cas (infirmée, non jugeable, course invalide) ont le même traitement de l'usage (nul v8 gardé par défaut, reprise sous préenregistrement nouveau). Pas d'incohérence logique.
- **Précision recommandée** (non bloquante) : écrire « traitée comme non jugeable pour l'usage » ou « (course invalidée par un audit : aucune issue, traitée comme non jugeable pour l'usage) », pour qu'un lecteur ne l'assimile pas à l'issue 5.

À noter aussi : le dossier de sortie du banc s'appelle toujours `banc-tricheurs-v8-validation-v1` alors que le fichier scellé est la v2. C'est cohérent avec le texte (la commande et le « validation-v1* » de la règle « un scellement, une course » concordent), mais on peut s'attendre à une confusion de nom ; sans conséquence pour le banc.

## 4. Empreintes du bloc gelé (section 11)

`sha256sum -c` sur les 12 lignes du bloc extraites de la v2 : **12 OK sur 12** (dont `banc_tricheurs_v7.py`, `banc_tricheurs_v8.py` = `0be47e4b…`, `pole/nul_v8.py`, `pole/nul_filles_v2.py`, `pole/cycle.py`).

Vérification du seul changement de code approuvé : il n'existe plus de copie de l'ancien banc, mais en remplaçant dans le banc actuel `preenregistrement-validation-nul-v8-v2.md` par `…-v1.md` (2 occurrences : l. 24 de la docstring et l. 108, `PREREG_DECISIF`), l'empreinte obtenue est `23d2b7d2352443a377b85bee6a7817d53a7abeea8260c0197a9866dfb64cb8d1`, exactement celle du bloc de la v1. Donc **ces deux occurrences sont les seules lignes modifiées** ; les onze autres fichiers sont inchangés, byte pour byte. Le garde du mode décisif (l. 177) compare bien le fichier donné à `PREREG_DECISIF`.

## 5. Commande décrite

La commande de la section 4 est `python3 -I -B demonstrations/banc_tricheurs_v8.py ../resultats/banc-tricheurs-v8-validation-v1 --preenregistrement prereg/preenregistrement-validation-nul-v8-v2.md --repetitions 1000 --processus 2`. Elle prend la v2 et est acceptée par la garde du banc (pas lancée). Mode décisif : toutes les lignes, 1 000 répétitions, 3 heures, comme écrit. La règle de la graine (section 4, point 1) nomme aussi la v2.

## 6. Essais

`python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v58_nul_v8.py` : **35 passed, 51 subtests passed** en 34 s.

## Avant de sceller (pour la session principale)

1. Le champ de la section 12 « [à remplir : oui, par … / non] » est encore là : le remplir **avant** de calculer l'empreinte (il change le fichier, donc la graine). Aucun autre marqueur « à remplir » dans le fichier.
2. Appliquer ou refuser les deux précisions de la partie 3 avant le même calcul ; une fois l'empreinte prise, plus rien ne change.
3. Le compagnon `.sha256`, le commit unique (section 13) et l'ordre commit puis course sont à la charge de la session principale. Aucun dossier `resultats/banc-tricheurs-v8-validation-v1*` ni compagnon `.sha256` de la v2 n'existe actuellement (cohérent avec la règle écrite en section 4).
4. Tous les fichiers de la section 13 sont encore non suivis par git (`??`), y compris la v1 et la contre-lecture : rien n'est figé dans l'historique avant le commit.
