# M01 - ecarts a la preinscription (experimentateur)

Sceau verifie avant tout : sha256 de `preenregistrement.md` = 363a53c6...e343, identique a `preenregistrement.md.sha256`.

## Ecarts de definition ou de calcul
Aucun. Aucune definition, aucun seuil, aucun echantillon n'a ete modifie apres avoir vu des chiffres. Aucune ambiguite de la
preinscription n'a eu d'effet numerique : il n'y a donc pas de double lecture a chiffrer.

## Ecarts de procedure et precisions (sans effet sur les chiffres)
1. **Reprise apres redemarrage du conteneur.** La session precedente avait telecharge D1, D3, D4 (09:33 UTC, sha256 dans
   `donnees/meta_base.json`, non retelecharges) et 501 pages FedInvest (log `donnees/fedinvest_log.jsonl`). J'ai verifie que
   chacune de ces 501 pages est valide (le script saute une date seulement si la page enregistree a la date demandee et l'en-tete
   exact), puis telecharge les 422 autres le 2026-11-13 (processus nohup, journal `donnees/fedinvest_run2.log`). Le journal
   cumule 938 tentatives : 923 valides (une par date), 15 echecs reseau ou de session (curl sans reponse, HTTP 502, etape 2 ou 3
   sans reponse), repris par le script ; aucune page rejetee pour date ou en-tete.
2. **Scripts de la session precedente relus, pas reecrits.** `commun.py`, `telecharger.py`, `construire.py` : conformes au texte
   apres relecture ligne a ligne (calendrier C, population, exclusions et leur ordre, conventions 6.2, colonnes, controles 1 a 9
   et leur portee). Seul changement : `analyse.py` remplace les nombres non finis du bloc `descriptif` par `null` (JSON valide) ;
   cela n'affecte aucun champ de `champs_verification`.
3. **Calendrier verifie sur les metadonnees avant tout calcul de V** : J dans C pour les 324 lignes ; J-(J-5) vaut 7 (261), 8 (60),
   10 (3 : 2016-09-12, 2021-07-12, 2022-09-12) ; (J+5)-J vaut 7 (272), 8 (52) : exactement les comptes de la section 4.3.
4. **Controle de la formule de courbe apres avoir vu les resultats** (verification d'implementation, aucune definition changee) :
   z(m) de 6.2 redonne `SVENY02`, `SVENY10`, `SVENY30` a 5e-5 point de pourcentage pres sur cinq dates (precision d'affichage du
   fichier). Les niveaux moyens de E_own (de -2,8 a -4,2 pb) ont aussi ete regardes ; rien n'a ete modifie.
5. **`schema_ok` dans `analyse.py`** : `analyse.py` recalcule tout depuis `M01_analyse.csv` seul, avec son propre code de rendement
   (Newton, pandas) ; mais les controles 2, 3 et 5 exigent D1 (la preinscription le prevoit : le verificateur reconstruit la
   population depuis D1) et `schema_ok` est donc obtenu en important `construire.controles`, qui lit `donnees/D1_auctions.json` et
   reutilise le calendrier de `commun.py`. Le calendrier de ce controle n'est donc pas independant du constructeur ; le seul
   code independant est celui des rendements (`ecart_max_rdt_pb`).
6. **Demonstration de detection** (`donnees/demonstration_controles.txt`) : chaque controle 1 a 9 detecte une alteration faite sur
   copie (colonnes permutees, ligne supprimee, id duplique, periode, date_jm5 decalee d'un rang, emission posterieure, identite,
   prix 250, rendement +1 point, v_cmt +1e-3, cmt effacee) ; l'alteration d'une ligne exclue (9128286T2_2019-06-12) ne declenche
   rien. Plusieurs alterations declenchent aussi d'autres controles (ex. cmt effacee : 3 a 9) : normal, une valeur illisible fait
   echouer tous les controles de ligne qui la lisent.
7. `donnees/PROVENANCE.md` : la colonne « lignes de tableau » compte les lignes `<tr><td` ; elle va de 256 (pages de 2010) a 464,
   ce qui est coherent avec les 420-464 de 2020 et apres citees en 5.2 (les premieres annees ont moins de titres).
8. **Aveugle.** Je n'ai ouvert aucun fichier d'un autre dossier de `tests-de-mort/` (hors `protocole.md` et `verdict.py`, demandes),
   rien sous `projects/`, ni `simulation_decision.py` (present dans M01/, vu seulement dans un `ls`), ni journal git. `git status`
   a ete lance une fois (aucun log).
9. **Resultat a signaler.** `controle_positif_ok` = 0 (borne basse a 90 % de V_own avant 2022 = -0,0033 pb). Selon la regle ce
   resultat rend le test non concluant ; je n'ecris pas de verdict et n'ai pas execute `verdict.py`.
