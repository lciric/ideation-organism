# M01 - rapport de l'experimentateur

Sceau : sha256 de la preinscription conforme au fichier `.sha256`. Aucun verdict ici ; `verdict.py` non execute.

## Ce qui a ete fait
- **Reprise.** La session precedente a ete interrompue par un redemarrage du conteneur. Reutilise : D1, D3, D4 (telecharges a 09:33,
  non refaits), 501 pages FedInvest valides, `telecharger.py`, `commun.py`, `construire.py`, `analyse.py` (relus contre le texte,
  voir `ecarts.md`). Rien n'a ete repris du premier `M01_analyse.csv` (09:36, anterieur au telechargement complet) : il a ete
  reconstruit.
- **Telechargement FedInvest** termine : 923 dates sur 923, toutes valides (date affichee = date demandee, en-tete exact), 15 echecs
  reseau repris. Procedure 5.2 : cookie et `_csrf`, une session par date, pause d'1 s, 302 non suivi. Provenance : `donnees/PROVENANCE.md`.
- **Fichier d'analyse** `M01_analyse.csv` : 324 lignes, 59 colonnes, tri date puis echeance ; P = 321 lignes (204 avant : 95/13/96 ;
  117 apres : 39/39/39 ; 96 et 39 mois), 3 exclues `fenetre_chevauchee`, aucune `valeur_manquante`. sha256
  fd2eeedccea52bffb0b79539373a15515a28cf303832c6966b583122950ca9ac.
- **Controles de schema 1 a 9** : tous passes (`schema_ok` = 1) ; chacun detecte une alteration sur copie (`donnees/demonstration_controles.txt`).
- **Analyse** (`analyse.py`, `temoin.json`, `figure.png`) : tous les champs de `champs_verification`, plus `descriptif` S1-S4.
  `ecart_max_rdt_pb` = 1,9e-11 avec un second code (Newton, pandas) : les deux codes de 6.2 s'accordent.

## Chiffres du temoin (pb)
| champ | valeur |
|---|---|
| n_avant, n_apres ; grappes | 204, 117 ; 96, 39 |
| V_own avant (ET) ; borne basse 90 % | 0,1260 (0,0787) ; -0,0033 -> controle_positif_ok = 0 |
| V_cmt avant, apres ; baisse (ET) ; borne basse | 1,3449, 0,0189 ; 1,3260 (0,3730) ; 0,7123 -> controle_cassure_ok = 1 |
| V_own apres (ET) ; borne basse | 0,4158 (0,3525) ; -0,1641 |
| baisse de V_own (ET) ; borne basse | -0,2897 (0,3612) ; -0,8839 |
| D (ET) ; IC 90 % | -1,6157 (0,1695) ; [-1,8945 ; -1,3370] |
| m (ET) ; sans 2023 ; sans le 30 ans | -0,9527 (0,2117) ; -0,8068 ; -0,8517 |
| indecis | 1 (ni le profil S, qui exige borne basse de V_own apres > 0, ni E ne tient) |

Lecture factuelle, sans verdict : l'instrument V_own ne voit pas la pression en 2010-2021 (0,13 pb, contre 1,38 attendu) ; c'est la
condition `controle_positif_ok` de la regle. Les deux jambes (S2) : montee de V_own 0,16 avant, 0,61 apres ; redescente -0,03 avant,
-0,19 apres (le pic d'un jour de V_cmt n'apparait pas dans les prix FedInvest). Par echeance (S1), V_own avant : 0,36 (10 ans), 0,01 (20),
-0,09 (30). Correlation V_own/V_cmt : 0,51 avant, 0,94 apres. 11 lignes de P ont un prix identique a deux dates.
Valeurs completes dans `temoin.json` (clef `descriptif`).

## Fichiers
`M01_analyse.csv`, `temoin.json`, `figure.png`, `analyse.py`, `construire.py`, `commun.py`, `telecharger.py`, `ecarts.md`,
`donnees/` (bruts, `PROVENANCE.md`, `fedinvest_log.jsonl`, `fedinvest_run2.log`, `demonstration_controles.txt`).
