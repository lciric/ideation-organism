# Contre-lecture du préenregistrement de lecture du lot T0.5 à graines neuves (v1)

**Verdict : scellable après corrections mineures (C1 à C11 ci-dessous ; C1, C2, C3, C4, C5 et C10 sont les plus importantes, toutes sont du texte, aucune ne touche au code hashé).**

- Contre-lecteur neuf (n'a rien écrit de l'objet ni du code). Fichiers lus : tous ceux de la liste R2, plus `pole/cycle.py` (`preparer_engagement`, `appliquer_multiplicite`), `pole/monde_banque.py`, `pole/selection_pari.py`, `exemples/construire_banque_t05_v3.py`, `resultats/puissance-juge-banque-v1-2026-11-01/*`, le gabarit, `src/controle_ia/prereg.py`, le préenregistrement frère `preenregistrement-validation-nul-v8-v1.md` (précédent pour les « lectures préalables » et le bloc d'empreintes).
- Rien du lot lu, rien récupéré (aucun réseau, aucun fetch). Je n'ai pas ouvert les dossiers `a-blanc-final/lot/*` ni `plomberie*` du répertoire de l'auteur (fichiers factices ou anciens renommés) ; j'ai seulement regardé la sortie `.md` de la course à blanc (synthétique) pour voir la forme du rapport.
- Joué : 36 essais sur 36 réussis (10 s) ; `sha256sum -c` du bloc de la section 15 : 11 lignes OK ; annexe `constats_calibrage_v1.py` rejouée sur `banque-e2.json` : sortie sha256 `d24f8bed…4c91`, identique à la valeur citée, et tous les chiffres de la section 2 (rangs, couvertures, informations hors échantillon) retrouvés.
- Heure de ce rapport : environ 22:00 UTC, 1er novembre. Le scellement avant 02:00 est tenable : C1 à C11 sont des remplacements de texte (30 à 45 minutes) ; relancer ensuite `sha256sum -c` sur le bloc (le texte change, pas le code) et calculer H une seule fois, sur le texte final.

---

## 1. Les cinq points signalés par l'auteur

### (1) Famille T décisive, famille R non décisive : cohérent, honnête, mais la famille décisive n'éprouve pas l'instrument de la question scientifique

- **Cohérence : oui.** Avec 0 témoin vrai réel (A7 le garde), seuls des témoins plantés peuvent mesurer les dents ; en monde informé les lois connues ne peuvent pas gagner (elles sont dans le nul), d'où R en monde aveugle. Les comptes sont justes : m_T = 13 faux réels + 3 TFP + 3 TFN = 19 (les 3 TVP sont hors famille) ; m_R = 13 lois connues + 13 faux réels = 26 ; log(19/0,05) = 5,940, log(26/0,05) = 6,254, log 20 = 2,996, log(17/0,05) = 5,829 ; fiches jugées T 22, R 26 (section 6) : conforme au code (`m_t`, `m_r`, `lire_famille`).
- **Honnêteté : oui** sur ce qui est dit (section 0, 16.1 : « dents non mesurées sur les témoins réels, par construction » ; le rejet d'un seuil |ρ| ≥ 0,2 est bien argumenté). Le fait que la famille T ait été conçue **après** avoir vu le calibrage nul (plus grand |ρ| = 0,248) est une liberté de l'auteur : permise (le lot n'existe pas) mais à déclarer dans les lectures préalables (C5).
- **La famille décisive est la bonne pour ce qu'elle décide** (validité contre des nuls structurels : bruit, permutation ; dents sur loi oracle). Elle n'est **pas** celle qui décide de la phrase finale sur les lois réelles : cette phrase vit entièrement dans R, qui n'a **aucun témoin positif** (la loi connue estimée, en monde aveugle, au seuil 6,25 n'a jamais été éprouvée sur une dépendance plantée). La borne I*(N) est transposée de la courbe (loi oracle si/sinon, monde informé, seuil 5,83, banc exploratoire « rien d'opposable » selon sa propre réserve). Voir C3, C4 et C8.
- Précision de langage : « non décisive » (R) ne veut pas dire « sans effet sur la conclusion » : R fixe I1 contre I2 et donc la phrase du résultat. Écrire « non décisive pour la validité et les dents du juge ; décisive pour la phrase sur les lois réelles » (C3).

### (2) Invariant « plein ≥ gelé » et comparaison descriptive : bien dit

- Code vérifié : même graine de plan (`graine_derivee(config.graine, "plan", fiche.empreinte())`), même mélange, `selection_divergence` tri stable `(-score, indice)` : le plan gelé est le préfixe du plan plein ; les membres du nul (marginale au maximum de vraisemblance, moyennes glissantes à fenêtres, uniforme, connu) sont causaux, donc les trajectoires coïncident sur les 120 premiers instants. Pour un témoin vrai **hors famille** (seuil fixe m/α), la propriété est exacte. Le texte (sections 4, 12 « Comparaison des bras », 16.7) dit bien : invariant, pas prédiction ; pour une fiche en famille le verdict e-BH peut changer dans les deux sens ; l'intervalle de la différence est biaisé par les doublons du rééchantillonnage.
- Probabilités de P4 recalculées : gain attendu 0,253 / 0,314 / 0,586 ; P(gain ≥ 1) = 0,234 / 0,284 / 0,481 (192 / 210 / 288) : justes.
- Seul défaut : P4 figure dans le tableau des « prédictions » avec « réfutée si : — » ; c'est une lecture, pas une prédiction réfutable (C7).

### (3) Calibrage lu dans une banque dérivée : acceptable, avec une vérification que je viens de faire et qu'il faut écrire

- Contrôle indépendant fait ici : pour les 60 tâches du pilote, j'ai recalculé depuis les fichiers bruts du dépôt privé (`diag/20261012-105125-t05-pilote-reel/episodes.json`, `diag/20261017-193648-t05-notations-reel/notations-{8B,3B}-decisives.json`) (a) les trois traits normalisés des 180 épisodes : écart maximal de 1e-5 toléré, **0 écart** ; (b) les issues des 13 moniteurs sur les épisodes e0 et e1 avec les coupes de la banque : **1560 cellules, 0 écart**. Non vérifiables ici : les e2 du pilote et les 36 tâches de la couche 1 bis (fichiers dans un répertoire d'une autre session, hors dépôt ; la banque en porte les empreintes dans `sources`, par ex. `episodes.json` `4eccb069…`).
- Normalisation de la banque : moyenne 0 et écart-type 1 exacts sur les 288 instances (elle est donc calculée sur les 288, pas sur la seule partie « calibrage » de la banque) : cohérent avec le choix de tout traiter en calibrage. Le script réécrit `partie = "calibrage"` pour les 288 et ignore le découpage calibrage / développement / épreuve de la banque : voulu, mais à écrire (C10).
- Les moniteurs « plante:* » de l'ancienne banque sont bien filtrés (`juge in JUGES`), pas de collision avec les nouveaux `plante:0..2`.

### (4) Sévérité de la liste d'arrêt : proportionnée, deux trous

- Les gardes A1 à A7 correspondent au code ligne à ligne (lu : `empreinte_compagnon`, `lire_table`, `_lire_notations`, `lire_lot`, `verifier_moniteurs`, `verifier_table_de_rangs`, `verifier_code`) ; aucun repli silencieux repéré : les seules exclusions silencieuses sont celles que le texte déclare (épisode sans jetons, sans notation).
- **Trou 1 (D)** : A8 écrit « `PlanPleinRefuse` → arrêt », mais `executer` ne capte que `Arret` ; `PlanPleinRefuse`, `LoiInvalide`, `BanqueInvalide`, `FileExistsError` ou toute exception non prévue sortent en trace, sans `arret.json`. C'est bruyant, donc acceptable (R5), mais le texte promet autre chose (C2).
- **Trou 2 (sévérité)** : A1 sur « lot de la table sans course » et A4 (K = 60) arrêtent **toute** la lecture ; P(A4) est négligeable (le plus bas, 3B:RESULT_REASONING, attendu 83 [69 ; 97] à 192) mais la perte d'un seul lot (ex. D, 6 tâches) condamnerait la nuit. Garder la sévérité, mais écrire que l'addendum peut prévoir une lecture sur les lots disponibles, scellé avant relance, sans note lue (C2). Pas de changement de code nécessaire à l'instant.

### (5) Borne transposée par l'information par épisode : « approximation » dite, mais pas ses sens

Voir C3 pour le texte. Chiffres de la borne recalculés : N = 120 → force 0,752, 0,117 nat ; 200 → 0,586, 0,080 ; 240 → 0,496, 0,060 ; 288 → 0,464, 0,054 : conformes à la section 12. Le point nouveau et le plus lourd : **la loi connue est ajustée sur 4 entrées (les 3 traits et le trait de bruit : `d = len(traits) = 4`, `ajuster_softmax`)**. Son coût d'estimation au premier ordre est (K−1)(d+1)/(2·n_cal,M) = 0,011 à 0,029 nat par épisode selon le moniteur (par ex. 3B:BALANCE 0,020 ; 8B:RIGOR 0,029 ; 3B:RIGOR 0,012), soit 20 à 50 % de I*(288) = 0,054 : cela concorde avec les informations hors échantillon négatives de la section 2. La phrase « la dépendance porte moins que I* » confond donc l'information de la loi **ajustée** et celle de la dépendance **vraie**.

---

## 2. Points A à H : conforme ou à corriger

| point | état | détail |
|---|---|---|
| A. Complétude R1 | conforme sur le fond ; **à corriger (C10)** sur la forme | Hypothèse (3), prédictions chiffrées et signées (7), métrique (8), seuil (9), plan (11), critères gelés (12), liste d'arrêt (14), contre-lecture (17) : tout y est. Mais `controle_ia.prereg.problemes()` sur une copie du fichier rend 8 « section absente » (titres numérotés ou différents : « Hypothèses », « Prédictions chiffrées et signées », etc.) : `sceller_prereg` le refuserait ; l'en-tête n'a pas « Commit du code d'analyse ». |
| B. Statistique | conforme | Seuils e-BH : voir (1). Règle e-BH conforme à `cycle.appliquer_multiplicite` (e-valeur arrêtée à m/α, k*, témoins vrais hors famille à m/α). Rééchantillonnage par tâche : `integers(0,T,size=T)`, B = 1000, quantiles au rang le plus proche, jeu rejoué en entier, m inchangés : conforme au code. P3 recalculée : fraction attendue 0,728 / 0,752 / 0,857 et P(≥ 2/3) = 0,896 / 0,917 / 0,985 : justes. Table par paire : moyennes des 6 paires et dictionnaires du script identiques au texte. **À corriger** : P1 (« P ≥ 0,9 » présentée comme prédiction chiffrée alors que la garantie est ≤ 0,05 par configuration, C7) ; intervalles : ne couvrent pas l'aléa des issues plantées (une seule plantation) (C9). |
| C. Graines | conforme au code ; **parade à ajouter (C6)** | Quatre fils dans l'ordre, bruit tiré par épisode retenu dans l'ordre trié, permutations dans l'ordre `plante:0,1,2` sur calibrage puis épreuve triée, tirages du rééchantillonnage faits d'avance : conforme. Rien n'empêche aujourd'hui d'essayer des retouches du texte jusqu'à obtenir des paires de traits confortables (H dépend de chaque octet). |
| D. Fidélité code / commande / texte | **à corriger (C1, C2)** | Commande : tous les arguments existent, `-I -B` fonctionne (`sys.path` posé par le script). Bloc de 11 empreintes OK, mais la course importe **trois fichiers de plus** non couverts : `pole/__init__.py`, `pole/caviardage.py`, `pole/proposeurs_references.py` (relevé par `sys.modules` après une course à blanc complète ; aucun import paresseux de `nul_filles_v2` ni `monde_noyau` n'est atteint). Le préenregistrement frère couvre `__init__` et `caviardage`. A8/`PlanPleinRefuse` non capté. Chaîne d'une fiche identique à `puissance_juge_banque_v1.juger_temoin` (diffère par : nul v8 ajusté, garde d'archive vide, garde de plan plein). |
| E. Lectures préalables | **à corriger (C5)** | Les plomberies sont déclarées mais en une phrase de la section 17 ; le frère a une section dédiée avec un tableau « qui, quand, graine, ce qui a été vu ». Déclarer aussi : calcul des constats du calibrage (qui a guidé la conception de T), scripts `cv_connu*.py`, tables par paire, course à blanc synthétique, plomberie sur fichiers anciens renommés avec le vrai calibrage (la sortie de ces essais contient des chiffres réels dérivés : à dire qu'elle n'a servi à rien de décisif). |
| F. Revendications / règle d'un nul | **à corriger (C3, C4)** | Voir (1) et (5). |
| G. Provenance | conforme, trois empreintes (et plus) revérifiées | `banque-e2.json` `f59018fb…b22e` OK ; table `76375391…0a772f` OK (`git show f40c8aa9:donnees/…`) ; courbe `060216fe…4c55` OK. En plus : `origines…v2` `ea231aab…`, `force-en-clair` `74193588…a1a6`, fiches de production A à D (`e14946e3…`, `1baf41cf…`, `4af4ca08…`, `c24db30e…`) au commit `f40c8aa9`, `juges.py`, `rubrique.py` au commit `2660b07`, H3, H4, index, configuration, annexes (`e234286d…`, `f8b73c12…`), sorties par paire `22d12017…`, `30de2400…` : toutes conformes. **Réserves** : `puissance-juge-banque-v1.json` est cité comme « document qui fait foi » alors que son `.md` dit « rien d'opposable » (C3) ; beaucoup d'empreintes sont tronquées (8 à 16 caractères) (C10) ; les sorties par paire n'existent que dans le répertoire de travail de l'auteur (C10). |
| H. Symétrie R4 | **à corriger (C8)** | Les déclencheurs « trop beau / trop mauvais / incohérence » sont raisonnables et symétriques sur les témoins. Asymétrie réelle : l'issue **prédite** (I1, aucune loi réelle promue) est un négatif propre et n'ouvre aucun audit, alors qu'une loi promue en ouvre un. R4 dit « positif ou négatif ». |

---

## 3. Corrections, avec texte de remplacement prêt à coller

### C1 — Bloc d'empreintes (section 15) : ajouter les trois fichiers importés

Remplacer le bloc `11 lignes` par ce bloc de 14 lignes (les empreintes sont recalculées ici ; l'ordre est indifférent pour le script, qui lit toutes les lignes `hash␣␣chemin`) :

```
91973f2582c4db08d86250594adec317bc6796095bfdd60d3119a8c21dde179d  demonstrations/lecture_t05_graines_neuves_v1.py
6bcec082991bd8a4d55d195adb0e7b35f4e5dec00f85330e70863da96f4b4569  pole/juge_plan_plein_v1.py
f7341b965ddba1e0fb21b44d9068f59650d5c77e3175f2b6b7ca879219fa5c9b  pole/__init__.py
78abfd4731218e20538418608ebebaca3364206ef6d014b7a34829a3c9fd7e85  pole/caviardage.py
6ed7e56fb1a1f7441467281d414b892176e73a1ffa528db090684cb6cf20805c  pole/proposeurs_references.py
359928110d757cd54cc0d2773910c7360895b68cac5d17e0e4b4e9933ef306bc  pole/selection_pari.py
33088eb9088549a20ffd489687928a1f1469d1df85a025db29bc9ce3f93e7b18  pole/monde_banque.py
798f039042e3ee1f18df5c566f5a0ddee5dac5c98225c8ce621e267174c8ee18  pole/cycle.py
cc452aafd17121a7c0ec42829eea47063ffee1f6cdf7f642e264d528f976b888  pole/nul_v8.py
ec018f147196222268d91358ce2038bb35bf76069e6bf8928dea9e3db59d1074  pole/fiche.py
71f1d08613bf335aa9ef7aa1397f20aa24553fea2f1b858c10b265d62f8ab79e  pole/memoire.py
966d9553026aad1eb7d97fa677334f1b59f22a39f15eef95134d63bc47634444  pole/outils.py
dff00005b80e8bfdd5cf3198336cbaebd0ca21752dc1c0d983835cc71f7fdaeb  exemples/construire_banque_t05_v3.py
cdfa818d0f6f9a6740e4dc6d6905d9515ffc617d6d047a7fdf566ffdfb31937d  exemples/proposeur_scripte_banque_v1.py
```

et, juste avant le bloc, remplacer « Empreintes du code (chemins relatifs à `orchestrator/`…) » par : « Empreintes des **14 fichiers que la course importe** (relevés par `sys.modules` après une course à blanc complète ; aucun import paresseux de `nul_filles_v2` ni de `monde_noyau` n'est atteint par cette lecture) ; chemins relatifs à `orchestrator/` ; … » (reste inchangé). Le script les vérifie toutes (A2) : ne pas toucher au code. Le champ `empreintes` du JSON de sortie n'en consigne que 7 (cosmétique : les 14 sont déjà dans la vérification du bloc, dont `verification_du_code.fichiers`).

### C2 — Section 14 : A8 et exceptions non prévues, I6, lot manquant

Remplacer la ligne A8 par :

| A8 | incohérence interne : loi connue ≠ membre informé du monde de lecture ; lecture aux instants inattendue ; sévérité ≠ α ou loi absente ; plan plein plus court que le réservoir, plan plein refusé ou membres d'archive inattendus (`PlanPleinRefuse` du juge) | arrêt. **Réalisation exacte** : le script n'écrit `arret.json` que pour ses propres gardes (`Arret`) ; une `PlanPleinRefuse`, une `LoiInvalide`, une `BanqueInvalide` ou toute autre exception non prévue interrompt le script par une trace sur la sortie d'erreur (code de sortie ≠ 0) **sans aucun fichier de résultat** (rien n'est écrit avant la fin) ; cela compte comme un arrêt A8 : le lanceur lit la trace pour vérifier qu'elle ne porte ni note ni issue, la consigne, et ne relance qu'après un addendum scellé |

Ajouter à la fin de la section 14, après le paragraphe sur les notations descriptives :

« **Lot manquant ou moniteur trop pauvre (A1, A4).** Ces arrêts sont volontairement absolus : le script exige les quatre lots et K = 60. Si un lot manque (ex. le lot D, 6 tâches) ou si un moniteur passe sous K, l'addendum scellé peut prévoir une lecture sur les lots disponibles ou sans ce moniteur (m recalculés par le script), à condition d'être scellé avant toute relance et rédigé sans avoir lu ni note ni issue (seuls les comptes de `arret.json` sont connus). La probabilité d'A4 est négligeable à N_ép = 192 (le moniteur le plus pauvre, 3B:RESULT_REASONING, est attendu à 83 [69 ; 97]). »

### C3 — Sections 3, 12(a), 16.5, 4 : dire ce que la borne est, et ce que « valide » veut dire

(a) Section 3, remplacer H3 par :

« **H3 (lois réelles)** : la loi connue de chaque moniteur — régression multinomiale à crête ajustée sur les 288 épisodes déjà courus, sur **les trois traits réels et le trait de bruit** (quatre entrées, comme le membre informé du juge de production) — ne bat pas la bibliothèque aveugle sur l'épreuve ; aucune loi réelle n'est promue. Le trait de bruit coûte de l'information (paramètres inutiles) : c'est l'instrument de production, gardé tel quel. »

(b) Section 4 (après « Deux familles… »), remplacer l'intitulé « Famille R (lois réelles ; préenregistrée, non décisive pour le juge) » par « Famille R (lois réelles ; préenregistrée ; **non décisive pour la validité et les dents du juge, décisive pour la phrase sur les lois réelles** : elle fixe I1 contre I2) ». Et ajouter après la définition de R : « Famille R sans témoin positif : aucune dépendance plantée n'est jugée avec une loi estimée en monde aveugle ; la sensibilité de R n'est donc pas mesurée par cette lecture mais transposée (section 12) ; c'est une réserve (section 16). »

(c) Section 12(a), remplacer les deux phrases « **Ce que cela dit** : … (approximation dite). » par :

« **Ce que cela dit** : la loi connue du moniteur M, **telle qu'ajustée sur le calibrage** (n_cal,M instances, quatre entrées), n'atteint pas, sur graines neuves des mêmes 96 tâches, l'information par épisode I*(N_M) à partir de laquelle une loi plantée de la forme si/sinon, correctement spécifiée, est promue avec une probabilité ≥ 0,9 sous le plan plein (courbe publiée) — à condition que l'issue soit I1 et que la règle de la section 12 bis (dents) soit satisfaite. C'est un **ordre de grandeur de la sensibilité de l'instrument « loi connue »**, pas une borne démontrée sur la dépendance vraie, pour quatre raisons : (i) *coût d'estimation* : l'information de la loi ajustée est celle de la dépendance vraie moins environ (K−1)(d+1)/(2·n_cal,M) nat par épisode (d = 4 ; de 0,011 à 0,029 nat selon le moniteur, premier ordre, non mesuré sous le nul), soit 20 à 50 % de I*(288) = 0,054 : une dépendance vraie plus forte que I* de cet ordre peut passer inaperçue ; (ii) *courbe* : elle est mesurée sur une loi plantée exacte (oracle), non linéaire, en monde **informé**, au seuil 5,83 (m = 17), par un banc exploratoire sans préenregistrement ni contre-lecture (« rien d'opposable », sa propre réserve) sur 60 tâches tirées avec remise au-delà de N = 80 ; la famille R juge une loi **estimée** en monde **aveugle** (plus favorable à la détection) au seuil 6,25 (m = 26, plus défavorable) : le sens net de l'écart n'est pas établi ; (iii) I* est une moyenne sur 6 paires de traits (à force 0,5 l'information va de 0,043 à 0,072 nat selon la paire, soit ± 30 %) ; (iv) une dérive des fréquences de classes entre calibrage et épreuve pénalise la loi connue (son biais est fixé au calibrage) alors que la bibliothèque ajuste sa marginale a posteriori. La borne est donnée **moniteur par moniteur** (0,9 par moniteur, pas pour les 13 à la fois). »

(d) Section 16, remplacer le point 5 par :

« 5. La borne I*(N) est lue sur une courbe exploratoire non opposable (sa propre réserve), mesurée avec une loi plantée exacte en monde informé au seuil 5,83, et transposée à une loi connue **estimée** en monde aveugle au seuil 6,25 par l'information par épisode : ordre de grandeur, pas borne. Le coût d'estimation de la loi connue (quatre entrées, de 0,011 à 0,029 nat par épisode selon le moniteur) et les dérives de fréquences de classes la défavorisent ; le monde aveugle la favorise. Aucun témoin positif de la famille R n'est jugé. »

(e) Section 0 et section 12(a), « juge valide » : ajouter une fois, à la première occurrence (section 0) : « *valide contre des nuls structurels* (trait de bruit indépendant, issues permutées) *sur les données réelles de ce lot ; sans signification pour un faux lien induit par la tâche (le lot a des tâches communes au calibrage)* ».

(f) Section « Documents qui font foi », ligne de la courbe : ajouter « (banc exploratoire non contre-lu, rien d'opposable selon sa propre réserve ; sert ici de prédiction et d'ordre de grandeur, pas de preuve) ».

### C4 — Section 12(a) : quand la borne peut être écrite (dents partielles)

Ajouter à la fin de 12(a) :

« **Condition pour écrire la borne d'un moniteur M** : un témoin vrai planté de force **supérieure ou égale** à la force f*(N_M) de la borne est promu sous T-plein, c'est-à-dire le témoin de force 0,8 si f*(N_M) > 0,5, et celui de force 0,5 si f*(N_M) ≤ 0,5 (N_M ≥ 241 environ). Si cette condition n'est pas remplie pour M (par ex. témoin de force 0,5 manqué alors que 0,8 est promu : I1 est alors tenu mais l'audit R4 « trop mauvais » est déclenché), la ligne de M reste « borne non soutenue », quelle que soit l'issue. La table des bornes du rapport porte, pour chaque M, f*(N_M), le témoin requis et son état. »

(Aujourd'hui I1 se contente d'« au moins une des forces 0,5 et 0,8 promue » : la borne de 3B:COHERENCE à N ≈ 260, f* = 0,48, serait annoncée avec un témoin de 0,5 manqué.)

### C5 — Nouvelle section « Lectures préalables déclarées » (avant la section 17, renuméroter 17 en 18 ou l'appeler 16 bis)

À copier, en complétant les cases entre crochets (je ne sais pas ce que l'auteur a regardé dans les sorties de plomberie) :

« ## 16 bis. Lectures préalables déclarées

Aucune donnée du lot n'a été lue. Les lectures suivantes ont été faites **avant** ce texte ; la conception de la famille T a été décidée **après** la première (le calibrage ne donne aucun témoin vrai).

| # | qui, quand (UTC, 1er nov.) | quoi | vu |
|---|---|---|---|
| P1 | auteur, [heure] | table de rangs de la règle de L3 sur `banque-e2.json`, couvertures, informations hors échantillon de la loi connue (`constats_calibrage_v1.py`, `cv_connu.py`, `cv_connu_meme_tache.py`) | aucun témoin vrai ; plus grand \|ρ\| = 0,248 ; informations ≤ 0,0085 nat ; **a motivé l'ajout de la famille T décisive** |
| P2 | auteur, [heure] | table de puissance par paire (`puissance_par_paire_v1.py`, 40 répétitions par cellule, traits du calibrage en substitut de l'épreuve, sorties `22d12017…` et `30de2400…`) | taux par paire et par force (section 7) |
| P3 | auteur, [heure] | course à blanc complète sur données **synthétiques**, avec préenregistrement factice | forme du rapport, durée ; [dire si des verdicts synthétiques ont été regardés] |
| P4 | auteur, [heure] | plomberie : fichiers **anciens** du pilote et de la couche 1 bis renommés `-g2` et répartis en lots a à d, avec le **vrai** calibrage, la vraie table, le bloc d'empreintes ; lots c et d fabriqués en renommant les fichiers du lot b ; graine factice (empreinte d'un autre fichier) | arrêt A1 attendu ; course complète sur 192 épisodes ; invariant du préfixe tenu ; instances par moniteur 85 à 176 ; [dire si les verdicts de cette course ont été regardés : dans cette plomberie, les issues de l'« épreuve » sont celles du calibrage, ils ne disent rien du lot] |
| P5 | auteur, [heure] | essais (36) | réussite des assertions |

Depuis le début de la rédaction : aucun fichier de résultats d'une course du lot (branches `calcul/t05-graines-neuves-*`, `donnees/*`) n'a été récupéré, ouvert ou résumé pour l'auteur ; seul `git ls-remote` a été utilisé [à confirmer]. La course du lot D (6 tâches) peut finir avant le scellement (≈ 23:00 UTC) : sa branche peut exister au moment du scellement ; elle n'est pas lue. Heure du scellement : [heure UTC]. »

### C6 — Section 10 : parade contre le choix de graine

Ajouter à la fin de la section 10 :

« **Parade contre le choix de graine.** Les quatre graines (dont l'entier de plantation, donc les paires de traits et les signes) dépendent de chaque octet de ce fichier : H n'est calculé **qu'une fois**, sur le texte final, après la section 17. Aucune retouche du texte n'a été motivée par les paires tirées ni par une graine ; toute retouche après le calcul de H change H et sera déclarée comme un nouveau scellement avec ses nouvelles paires. Les paires tirées sont rapportées dans la sortie ; la prédiction conditionnelle qui en découle (section 7) est lue et sert seulement à l'audit d'un échec des dents. Le script ne tire aucune autre graine que celles-ci (graine du juge constante). »

### C7 — Section 7 : libellés des prédictions (P1, P2, P4) et scénarios de N_ép

Remplacer les lignes P1, P2, P4 du tableau par :

| P1 (L1) | 0 témoin faux promu (e-BH), dans chacune des 4 configurations | attente ≈ 0,9 à 0,95 ; **garantie** : chaque configuration est un e-BH sur des fiches toutes nulles (FDR ≤ α·m₀/m = 0,05), donc P(L1 non tenu) ≤ 0,05 par configuration, ≤ 0,20 par l'union (≤ 0,10 si l'on compte pour un les deux bras d'une famille, qui coïncident sur le préfixe) ; la courbe donne 0 à 1/1000 par cellule | idem | idem | ≥ 1 témoin faux promu (e-BH) |
| P2 (contrôle, non prédiction) | 0 témoin vrai réel | certain par la garde A7 | idem | idem | A7 (arrêt) |
| P4 (lecture descriptive, hors prédictions réfutables) | gain du plan plein (témoins plantés promus sous plein et non sous gelé) | … (inchangé) | … | … | sans objet : signe garanti ; un gain négatif est une incohérence (I5) |

Ajouter à la fin de l'introduction de la section 7 : « Si les notations descriptives (e2) sont **partielles** (un seul juge, ou une partie des tâches d'un lot), N_ép prend toute valeur entre 192 et 288 : le script interpole la courbe en N_ép observé ; le tableau des instances par moniteur vaut alors par morceaux (colonne 192 pour les moniteurs d'un juge sans e2). Dans le cas « descriptives du 8B seules », N_ép augmente mais les moniteurs du 3B restent à leur colonne 192. »

### C8 — Section 13 : symétrie R4 du négatif propre ; contrôle positif de R

Ajouter au début de la liste de la section 13 :

« - **trop propre (négatif)** : issue I1 *attendue* (aucune loi réelle promue). Un négatif propre n'est pas une preuve : l'audit R4 allégé est **toujours** fait en cas d'I1, par un agent neuf : recalcul indépendant, depuis les fichiers du lot et du calibrage, de la loi connue de chaque moniteur (ajustement sur le calibrage seul), de ses probabilités sur les instances d'épreuve avec les traits normalisés par le calibrage, et de log W maximal des 13 lois connues ; accord à 1e-6 près avec le rapport ; contrôle que les 13 lois connues ne sont pas dégénérées (poids non nuls, biais proches de la marginale d'ajustement). Il n'autorise ni ne refuse rien d'autre. »

Ajouter à la section 16, point 11 : « 11. La famille R n'a pas de témoin positif. Si le temps le permet avant le lancement de l'analyse, un témoin positif **non décisif** peut être ajouté par un addendum scellé avant la lecture : trois moniteurs plantés de loi **softmax linéaire** à quatre entrées (information visée 0,03 / 0,06 / 0,12 nat par épisode), issues tirées sur les 288 + N_ép instances, loi connue ajustée sur la partie de calibrage par `lois_connues`, jugée en monde aveugle au seuil 6,25 : cela mesurerait directement la sensibilité de R et remplacerait la transposition de la courbe. Sans lui, la phrase de la section 12(a) reste un ordre de grandeur. »

(Option B, plus lourde, non nécessaire pour sceller : ajouter ces témoins dans le script ; cela change l'empreinte du script, exige des essais R5 et le bloc de la section 15 : je ne recommande pas de le faire avant 02:00 ; si l'auteur choisit de le faire, il faut une nouvelle contre-lecture des seules lignes ajoutées.)

### C9 — Section 8 : ce que les intervalles couvrent

Ajouter à la fin de la section 8 : « Les intervalles par tâche couvrent l'aléa d'échantillonnage des tâches d'épreuve, **pas** celui des issues plantées (une seule plantation par force, issues fixées par la graine de plantation) ni celui du choix des paires de traits ; ils ne sont ni des intervalles de confiance de la puissance ni des tests. Pour trois témoins, les fractions possibles sont 0, 1/3, 2/3, 1. »

### C10 — Forme, scellement et provenance

1. **Validateur du dépôt privé** : `controle_ia.prereg.problemes` cherche les titres de niveau 2 exacts « Hypothèse », « Prédiction chiffrée et signe attendu », « Métrique », « Seuil », « Plan d'analyse », « Critères de lecture gelés », « Liste d'arrêt », « Contre-lecture ». Ce fichier a des titres numérotés (« 3. Hypothèses »…) : `sceller_prereg` le refuserait. Le préenregistrement frère (nul v8) est dans le même cas, donc la pratique de ce dépôt est de sceller par `controle_ia.scellement.sceller` (empreinte compagnon seule). Écrire une ligne dans l'en-tête : « Scellé par `controle_ia.scellement.sceller` ; correspondance avec les sections du gabarit : Hypothèse = 3 ; Prédiction chiffrée et signe attendu = 7 ; Métrique = 8 ; Seuil = 9 ; Plan d'analyse = 11 ; Critères de lecture gelés = 12 ; Liste d'arrêt = 14 ; Contre-lecture = 17. » (ou renommer les titres : cela ne change aucune référence numérique si l'on garde les numéros dans les titres, mais le validateur veut l'égalité exacte, donc la correspondance est plus simple).
2. **Commit du code** : le gabarit et R9 demandent le commit ; ici « aucun commit : les empreintes font foi », avec des fichiers non suivis par git (`git status` : script, juge, `nul_v8.py`, essais, annexes, `prereg/` en `??`). Un hash ne rend pas le contenu ; si le répertoire de travail est perdu ou modifié, la lecture est inrejouable. Ajouter : « Le code listé en section 15 est versé en commit local immédiatement après le scellement ; le numéro du commit est consigné en section 17 et dans l'en-tête. » Faire ce commit (sans rien pousser vers un dépôt public avant décision).
3. **Section 2** : ajouter « La banque lit `partie` en trois morceaux (calibrage 72, développement 72, épreuve 144) ; cette lecture les ignore et traite les 288 comme calibrage ; la normalisation de la banque (moyenne 0, écart-type 1) est calculée sur les 288. Contrôle fait par le contre-lecteur : pour les 60 tâches du pilote, traits et issues e0 et e1 (1560 cellules) recalculés depuis `diag/20261012-105125-t05-pilote-reel/episodes.json` et `diag/20261017-193648-t05-notations-reel/notations-*-decisives.json` : 0 écart ; e2 du pilote et couche 1 bis non recalculables (fichiers `banque-complete-v2/…`, hors dépôt ; empreintes dans `sources` de la banque). »
4. **Empreintes complètes** (remplacer les formes tronquées de l'en-tête ; copier-coller) :
   - fiche A `e14946e30fa3a743a79a33210f0f9a4329b64583526d5d0837a1a7c946e9503f` ; B `1baf41cf4a1611b707fe03d72a9bc956050b30907c6ad0026b0e0064630149d8` ; C `4af4ca08864abfec793081756091b91d8641f89b41a666d6ea85e271a2c1e0c5` ; D `c24db30e756fdd522a8bcd069dde3ea2789128a6d18d47e2a9198e282518af54` (commit `f40c8aa9`) ;
   - `origines-taches-graines-neuves-v2.json` `ea231aaba076348f5e74af678a788ac267870124a07ef1d4db617523afa97cc1` ;
   - `force-en-clair-v1.txt` `7419358857c824e0f67c76fb8a130faef1cf0071ce27b5d4bd0bbd900106a1a6` ; `puissance-juge-banque-v1.md` `d06d86e9cae12c1493aa38737a996dc148226cbc2e8f226d32b022e200bfe5d2` ;
   - H3 `52ab1e255360cf80a7a27ae3f8e6feb1eee5a26ae7ccee3d10ebc9ddd58c9c4d` ; H4 `cb103166b1c21f8caeb00ebc90730cb62b6cbda89ea3c89469674bcd60786fbc` ; index `adb4b8bca7788baf2c4714df96dcdcc2c5043e8f1943542d0fbe1863491ae2d9` ; `juges.py` (2660b07) `52610b0ad8e0a4ea1d749829f2ef2ff990e84538705b1d173cc6a221aa37f91e` ; `rubrique.py` `da2f7a1e3b4c2e11aa845816afe51f068420355da2ad6c3bfb3e66484764e0dd` ; configuration `6979a00ebef1e794f900e089df9b1658482f8600ce343cb81c95da4434da2b8a` ;
   - annexes `constats_calibrage_v1.py` `e234286d8decf393c03d967cc8c2ff8a948d1e8ae8da47c62c7231b9cb7eee2e` ; `puissance_par_paire_v1.py` `f8b73c1221ffc46b64469c287fd5f14d8c432cc02cb6348ee2153529263a5463` ; sorties `puissance-par-paire-192-v1.txt` `22d12017354e452135dfce5a9592432f9b02c0f52c756bdf9aa6be90b9936908`, `puissance-par-paire-288-v1.txt` `30de2400a9b08bc3c8f7dcdf4c13b667411aa55a71c6c199caa5b3cb2eb47699` ; sortie des constats `d24f8bedbbfe203be48ed6d8c160d79652bdb80ae319e77466a6d4e34adf4c91`.
5. **Sorties de l'annexe par paire** : elles ne sont que dans le répertoire de travail de l'auteur (`…/scratchpad/lecture-t05/paires/`) ; les copier à côté des annexes (`demonstrations/annexes_lecture_t05_v1/`) avant le scellement et citer ce chemin (R6 : chemin durable).

### C11 — Détails de rédaction (facultatif)

- Section 13, « 32 témoins faux » : les 13 faux réels sont les mêmes fiches dans T et R (mondes différents) : écrire « 19 témoins faux distincts, 32 fiches-configurations ».
- Section 12 : si une loi réelle est promue (I2), la garantie e-BH de L1 change de nature (k* plus grand abaisse le seuil des faux) : ajouter « sous I2 le seuil des témoins faux de R se relâche (k* ≥ 1) ; L1 est alors lu avec cette réserve ».
- Section 7, ligne P5 : écrire que P(≥ 1 loi promue) ≤ 0,1 est une estimation à partir de la courbe (oracle) et non une garantie ; la prédiction se renforce par le fait que la loi connue ajustée a une information hors échantillon négative sur 12 moniteurs sur 13 (section 2) : bon argument, à nommer comme tel.

---

## 4. Ce qui est solide (à ne pas toucher)

- Choix épreuve neuve lue une seule fois, rejet argumenté de la banque élargie, écart d'indépendance dit (mêmes tâches, puissance comptée en tâches, intervalles par tâche).
- Invariant du préfixe vérifié dans le code et par essai ; garde `verifier_plan_plein` ; `PlanPleinRefuse` pour un plan trop court ; refus d'un dossier de sortie non vide ou dans le dépôt public ; une seule lecture.
- Règle d'interprétation (b) à (d) : « ce que cela ne dit pas » complet et honnête (effet de tâche, causalité, états internes).
- Table des instances attendues par moniteur : arithmétique juste (échantillon vérifié : 3B:BALANCE 97, 124 ; 3B:COHERENCE 171, 260 ; K = 60 plus petit N de la courbe).
- Les fiches et le juge sont cohérents avec la courbe (réglages communs identiques à `config_du_juge`, plus le nul v8 imposé).

## 5. Ordre de travail conseillé avant 02:00 UTC

1. C1 (bloc), puis `sha256sum -c` sur la copie du bloc (rien d'autre à relancer côté code).
2. C2, C3, C4, C5, C7, C8, C9, C6, C10 : remplacements de texte.
3. Remplir la section 17 : chemin et empreinte de ce rapport, traitement de chaque remarque (accepté / refusé).
4. Commit local du code (C10.2), calcul de H **une seule fois**, scellement, `sha256sum -c` du bloc depuis un autre répertoire, puis seulement ensuite récupération du lot par refspec explicite.
