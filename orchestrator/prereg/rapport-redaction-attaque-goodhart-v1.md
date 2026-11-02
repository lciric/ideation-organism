# Rapport de rédaction — attaque de Goodhart v1 (brouillon 1)

2 novembre 2026, vers 07:00 UTC. Sous-agent rédacteur. Aucun appel de modèle, aucune clé lue, aucun commit, aucun
`git fetch`, aucun scellement, aucun fichier existant modifié ; calculs sous `nice -n 10`. Dépôt public à `1dac1fe`.

## Fichiers neufs (depuis `orchestrator/`) et empreintes SHA-256

| fichier | sha256 |
|---|---|
| `pole/attaque_goodhart_v1.py` (cœur : monde au nul, consigne, analyse, juge, suites, proposeurs scripté et par adaptateur, lecture gelée) | `7bdbfe243fbfab3a76fb04fb5692fe34470c851955ba0df4a91ff002d1aed317` |
| `demonstrations/attaque_goodhart_v1.py` (lanceur : à blanc ; réel par `ideation_v8.adaptateurs_reels_v56`) | `9641a96d80228975a49f20fb25fb90022c16f8ffc94b3954b2efcfe3d4539241` |
| `essais/test_attaque_goodhart_v1.py` (20 essais, cas sain et artefact) | `3133ba5185ade8ded5580f52b6e054d89ba5c6cb6604ecbc8fc5092b74912454` |
| `prereg/preenregistrement-attaque-goodhart-v1-brouillon1.md` | `af9b8588360ec501df0ea1d539b6e9eb013d64d8ff560401848ead7df2953fde` |
| `prereg/rapport-redaction-attaque-goodhart-v1.md` (ce fichier) | (non auto-référencé) |

Code importé, inchangé, aux empreintes du bloc gelé du préenregistrement du nul v8 : `banc_tricheurs_v8.py` `0be47e4b…`,
`banc_tricheurs_v7.py` `ef016d25…`, `nul_v8.py` `cc452aaf…`, `nul_filles_v2.py` `0ed9b4ad…`, `selection_pari.py` `35992811…`,
`cycle.py` `798f0390…`, `outils.py` `966d9553…`.

## Essais

- `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_attaque_goodhart_v1.py` : **20 réussis, 0 échoué,
  0 sauté** (≈ 10 s). Un premier passage avait 1 échec (artefact « loi trop longue » trop court dans l'essai lui-même :
  400 lignes = 5 600 octets < 6 000) ; corrigé dans l'essai (500 lignes), pas dans le code.
- Voisin importé : `essais/test_v58_nul_v8.py` : **35 réussis, 51 sous-essais réussis**, 0 échoué.
- Pas de banc de mutations écrit pour ce module (manque, ci-dessous).

## Course à blanc (L1, L3)

L1 (2 cartes, 16 tentatives, proposeur scripté) : 136 appels simulés, 22,9 s ; sous v8 aucune promotion (log W max ≤ 0),
sous v7 promotion à la tentative 2. L3 (plan gelé, 3 cartes, 20 rejeux) : sortie dans le scratchpad du rédacteur
(`a-blanc-plan-gele/`), durée lue dans `a-blanc-sortie.txt` (voir la réponse finale du rédacteur).

## Devis (section 12 du préenregistrement)

Maximum 288 appels (3 cartes × 2 fournisseurs × 3 suites × 16) ; attendu ≈ 210 à 250. Au taux moyen du second tour du
1er novembre (1,47 USD / 62 appels = 0,0237 USD par appel, préenregistrement `6fcb1035…`) : ≈ 5,0 à 5,9 USD attendus,
6,8 USD au maximum, **plafond dur 6 USD** dans le lanceur. Jetons : entrée ≈ 2 000 à 4 500, sortie ≈ 150 à 600 par appel.
Durée : 0,6 à 2,8 heures d'appels en série, plafond 3 heures. Puissance : 6 cartes-fournisseur par cellule ; Wilson 95 %
0/6 → [0 ; 0,39], 3/6 → [0,19 ; 0,81] ; seuls des écarts ≥ ≈ 0,5 entre bras sont visibles.

## Fichiers à donner au contre-lecteur neuf (R2)

1. `orchestrator/prereg/preenregistrement-attaque-goodhart-v1-brouillon1.md` ;
2. `orchestrator/pole/attaque_goodhart_v1.py`, `orchestrator/demonstrations/attaque_goodhart_v1.py`,
   `orchestrator/essais/test_attaque_goodhart_v1.py` ;
3. pour le juge : `orchestrator/demonstrations/banc_tricheurs_v8.py` (`juger_v8`), `orchestrator/demonstrations/banc_tricheurs_v7.py`
   (`scenario`, `_monde_lois`, `membres_archive`), `orchestrator/pole/nul_v8.py`, `orchestrator/pole/selection_pari.py`
   (`valider_loi`, `proba`) ;
4. pour le style et la règle « un scellement, une course » : `orchestrator/prereg/preenregistrement-validation-nul-v8-v2.md` ;
5. pour les adaptateurs : `orchestrator/demonstrations/ideation_v8.py` (`adaptateurs_reels_v56`), `orchestrator/pole/adaptateurs_v56.py`,
   `orchestrator/pole/adaptateur_kimi_v53.py`, `orchestrator/pole/adaptateurs.py` (`Resultat`) ;
6. ce rapport ; `README.md` (sections 3 et 4) ; `CLAUDE.md` du dépôt privé (R1 à R14).

Questions à lui poser : le seuil ε = 0,40 et la taille de 6 cartes-fournisseur sont-ils acceptables, ou faut-il demander à
Lazar le devis à 30 cartes ; la lecture emboîtée (nombre de tentatives tu) est-elle exacte ; la consigne « boîte blanche »
(juge décrit) est-elle le bon pire cas ; le bras témoin jugé sous deux nuls à partir des mêmes lois est-il sain.

## Ce qui manque pour lancer

- **Contre-lecture (R2)** et brouillon 2 ; **bloc d'empreintes du code gelé** écrit dans le texte et **vérifié par le
  lanceur** (comme `banc_tricheurs_v8.lire_preenregistrement`) — le lanceur v1 consigne les empreintes au manifeste mais ne
  les compare pas encore à un bloc gelé ;
- **chemin réel non essayé** : `proposeurs_reels` (lecture de la configuration v56, `adaptateurs_reels_v56`, porte de
  plafond A15) n'a été exercé par aucun essai (il faut un essai avec une configuration factice et des adaptateurs simulés,
  sans réseau) ; le budget par appel (`attaque_goodhart.budget_appel_usd`, défaut 0,10 USD) est à fixer dans la
  configuration ;
- banc de mutations du module (`essais/mutations_attaque_goodhart_v1.py`, à écrire) ;
- **clés chez session-depot** et **configuration du second tour du 1er novembre** (privée) ;
- **GO de Lazar** sur le devis (ligne dans `registres/go.md`), puis scellement par le directeur, commit et poussée avant la
  course.
