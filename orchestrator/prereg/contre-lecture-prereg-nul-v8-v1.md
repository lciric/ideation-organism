**scellable après corrections mineures (listées)**

# Contre-lecture du préenregistrement « validation décisive du nul v8 du juge », v1

Lecteur : contre-lecteur neuf (règle R2 du programme de Lazar : le préenregistrement est relu par quelqu'un qui ne l'a pas écrit). Date : 1er novembre 2026, de 21:30 à 23:05 heure de Paris environ. Fichier lu : `orchestrator/prereg/preenregistrement-validation-nul-v8-v1.md`, brouillon de 288 lignes, empreinte SHA-256 `894b294b2a3d3eb455ff77e709695026795e6d67199e94f2a905491cddf2d4b4` (inchangée de mon début à ma fin de lecture ; pas de compagnon `.sha256` : non scellé, comme annoncé). Numéros de ligne ci-dessous = lignes de ce brouillon.

## En clair

Le plan de la course décisive tient. Les seuils statistiques sont justes : je les ai recalculés à part avec scipy, ils concordent à l'unité près. La commande annoncée fait exactement ce que le texte dit. L'argument de validité est correct, y compris sur le point que l'auteur soulevait lui-même : ajuster le nul sur les mêmes issues que celles où l'on évalue est bien permis, c'est même ce qui fait fonctionner l'inférence universelle ; ce qui doit être séparé, c'est la loi proposée par la fiche, et elle est gelée avant les tirages.

Ce qui manque est de la rédaction, pas de la mécanique. Quatre faiblesses, par ordre d'importance :

1. La règle qui dit quoi conclure quand le banc observe une promotion « impossible par construction » est trop indulgente : un audit qui « ne trouve pas de défaut » laisserait lire « confirmée » malgré une inégalité démontrée qui vient d'être violée.
2. L'issue que le texte prédit, « 0 promotion sur 1 000 partout », n'a aucun contrôle écrit pour s'assurer qu'elle vient bien du nul ajusté (et non d'un nul ajusté qui ne serait jamais exercé). Seule une ligne de dents, sur la famille « parent + loi aveugle », existe dans la course.
3. Deux lectures préalables ne sont pas déclarées, les chiffres cités renvoient à des fichiers hors dépôt par des préfixes de huit caractères, et la règle « un scellement, une course » est annoncée sans être écrite.
4. Le mot « validé » en dit un peu plus que ce que la course mesure : dix des onze lignes fatales vérifient une inégalité (exacte pour huit, vraie à la marge de Newton près pour deux), non un contrôle probabiliste ; les deux lignes de puissance sont à effet fort.

Aucune correction ne touche au code gelé : les douze empreintes de la section 11 restent valables (je les ai comparées aux fichiers présents : identiques). Les corrections obligatoires sont C1 à C9, les recommandées C10 à C15 ; toutes sont des textes à coller. Faire relire le seul diff par un lecteur neuf avant scellement (les sections 3, 4, 6, 7, 8, 9, 10 changent de fond).

## Sigles, développés une fois

- R1 : préenregistrement scellé avant toute expérience décisive. R2 : contre-lecture par un lecteur neuf. R4 : symétrie (un résultat suspect de propreté est audité comme un résultat laid). R5 : chaque garde d'arrêt éprouvée sur un cas sain et sur un artefact (cas piégé). R6 : tout dépôt a une empreinte compagnon, tout chiffre renvoie à un chemin et une empreinte. R9 : graines par le générateur `numpy.random.SeedSequence`, dérivées par tâche. R12 : versions dans les noms, on n'écrase jamais. R13 : le verdict est prononcé par un sous-agent neuf qui applique les critères gelés.
- H1 à H4 : les quatre hypothèses de la section 2 (validité, prix en puissance, dents du banc, nul exact). P1 à P5 : les cinq prédictions de la section 3. A1 à A4 : les quatre audits de la section 7 (A1 : promotion d'une ligne refusée par construction ; A2 : nul v8 plus puissant que v7 ; A3 : taux de l'artefact hors de [0,10 ; 0,90] ; A4 : log W positif dans la classe linéaire). A5 et A6 : audits que je propose. L0 à L10 : lectures préalables déclarées en section 9 ; L11 et L12 : celles que je propose d'ajouter.
- T01, T02, T03u, T03b, T04, T05s, T09g, T09l, T12a, T17s, « nul exact », T07, T12b, « fille neuve », « fraîche neuve » : noms des lignes du banc (un tricheur ou un cas de puissance par ligne), tableau de la section 2 du préenregistrement. Une « fille » est une fiche née de deux lois parents A et B ; S1 et S2 sont des « survivantes » (lois déjà promues, gardées dans l'archive) ; un tricheur « recombine » des lois connues sans rien apporter de neuf.
- « log W » : logarithme népérien de la richesse W du juge ; la promotion a lieu quand W atteint 1/α = 20, c'est-à-dire log W ≥ 2,996 (en nats, l'unité naturelle du logarithme). « Classe linéaire » : lois du tricheur qui sont une combinaison linéaire de lois connues (membre `ajuste_lineaire:archive`). « Classe log-linéaire » : lois connues tempérées et inclinées (membres `ajuste_log:…`). « e-BH » : procédure de Benjamini-Hochberg appliquée à des e-valeurs (richesses), qui gère la multiplicité entre fiches.

## Ce que j'ai fait, et pas fait

- Lu en entier : le préenregistrement ; `pole/nul_v8.py` ; `pole/cycle.py` (fonction `membres_de_l_archive`, l. 260-288) ; `demonstrations/banc_tricheurs_v8.py` (593 lignes) et `banc_tricheurs_v7.py` ; `pole/nul_filles_v2.py` ; les parties de `pole/selection_pari.py` et `pole/outils.py` qui servent aux graines et aux tirages frais ; `essais/test_v58_nul_v8.py` et `essais/mutations_v58.py` ; `.github/workflows/bench-reduit.yml` ; les rubriques du gabarit du programme ; le fichier publié du banc v7.
- Joué : les 35 essais (`35 passed, 51 subtests passed`, 29,7 s) ; le banc de mutations (34 mutations, 34 tuées pour la raison attendue, 0 survivante, témoin 20 essais sans échec) ; un rejeu exploratoire de L8 (entropie 7, 18 lignes × 20 répétitions) avec le banc gelé ; un rejeu de L6 (entropie 41, 11 lignes × 10) ; les recalculs statistiques par scipy et une simulation Monte-Carlo du niveau de la règle de Newcombe. Annexe 3 : déclaration de ces lectures.
- Pas joué : aucune course décisive, ni entière ni partielle, ni avec ce préenregistrement ni avec un autre fichier. Pas de réseau, pas de commit. Aucun fichier du dépôt modifié par moi (comparaison d'instantanés avant/après : seuls ont bougé quatre fichiers de la tâche T05 menée par un autre agent en parallèle, et trois fichiers `.pyc` disparus ; aucun n'est l'un des douze fichiers gelés, le préenregistrement ou le rapport de ce banc).
- Vérifié à l'instant de finir : `orchestrator/prereg/` ne contient aucun compagnon `.sha256` pour ce fichier, et `resultats/` ne contient aucun dossier `banc-tricheurs-v8*` : aucune course décisive n'a laissé de trace.

## Liste des corrections

| n° | point | où | gravité | objet |
|---|---|---|---|---|
| C1 | H | section 7, l. 205-208 | obligatoire | conséquences des audits : A1 sur la classe linéaire et A4 invalident la course d'office ; la classe log-linéaire interdit « confirmée » |
| C2 | H | section 7, après A4 | obligatoire | A5 : déclencheur de propreté suspecte (nul ajusté inactif), lu sur les membres dominants |
| C3 | C | section 4, après l. 104 | obligatoire | un scellement, une course décisive ; aucune course décisive antérieure ; ordre commit puis course |
| C4 | D | section 8, l. 218-219 | obligatoire | le rejeu après arrêt exige un dossier de sortie neuf (la « même commande » serait refusée) |
| C5 | I, G | section 9 | obligatoire | lectures L11 et L12 non déclarées ; code joué par chaque lecture ; empreintes pleines ; copies dans le dépôt |
| C6 | J2 | section 3, l. 78-80 | obligatoire | P1 scindée : classe linéaire, classe log-linéaire (confiance moindre), T12a (risque dit) |
| C7 | F | section 6 (issue 4) et section 10 | obligatoire | portée de « validé » : inégalités exactes contre contrôle probabiliste, puissance à effet fort, lignes sans test, multiplicité entre fiches |
| C8 | A | nouvelle section 12 | obligatoire | rubrique « Contre-lecture » du gabarit absente |
| C9 | B | section 4, l. 124-126 | obligatoire | le code de sortie n'est pas l'issue (il repose sur des estimations ponctuelles) |
| C10 | E, H | section 7, A2 | recommandée | A2 : monotonie « en loi », fausse alerte possible (déjà vue sur le banc v7 publié) |
| C11 | D | section 4, l. 130-131 | recommandée | durée attendue 17 à 55 minutes |
| C12 | A | section 6 | recommandée, au directeur | ce que chaque issue change pour l'usage du nul v8 en production |
| C13 | H | section 7 | recommandée | A6 : une issue décevante est auditée au même titre qu'une issue trop belle |
| C14 | D | section 4 | recommandée | une phrase sur la raison d'être du banc v8 (le banc v7 ne peut ni dériver la graine ni appeler le juge de production) |
| C15 | C, G | procédure | recommandée | commit unique des fichiers gelés et du préenregistrement ; noter le commit ; relecture du diff |

---

## A. Complétude R1 — conforme, sauf la rubrique « Contre-lecture » (C8)

Rubriques du gabarit du programme : hypothèse ; prédiction chiffrée et signe attendu ; métrique ; seuil ; plan d'analyse ; critères de lecture gelés ; liste d'arrêt ; contre-lecture.

- Hypothèse : section 2 (H1 à H4, conjonction, avec le plan du banc rappelé : K = 3 issues, 2 traits, 2 sous-populations, 50 tirages de calibrage puis 200 d'évaluation, lecture aux instants 25 à 200, marge 2δ₀ = 0,02, α = 0,05). Conforme.
- Prédiction chiffrée et signée : section 3, P1 à P5, chacune avec un signe ou une bande, et la mention que les prédictions « ne changent pas l'issue ». Conforme, avec la réserve C6 sur P1. Les bandes sont cohérentes avec le code (`PREDICTIONS`, banc l. 120-122).
- Métrique et seuil : section 5 (taux de promotion, bornes de Clopper-Pearson unilatérales à 95 %, test binomial exact, Holm, Newcombe, tableau des seuils). Conforme (point B).
- Plan d'analyse : section 4 (lignes, répétitions, graine, code gelé, environnement, commande, sortie, durée). Conforme, avec C3, C4, C9, C11.
- Critères de lecture gelés : section 6 (tenue / non tenue / non jugeable par composante, cinq issues ordonnées par priorité, chacune avec sa lecture). Conforme ; le code `lire_v8` (banc l. 437-508) les applique dans cet ordre (vérifié ligne à ligne). La lecture de l'issue 4 est à resserrer (C7).
- Liste d'arrêt : section 8. Conforme, avec C4.
- Issues écrites d'avance et ce que chacune change : oui pour la science (nul validé, ligne ouverte, décision du directeur, banc à réparer, rapport sans conclusion) ; absent pour l'usage en production, puisque le nul v8 est déjà décidé comme nul par défaut avant sa validation (C12).
- Contre-lecture : absente, normal avant mon rapport ; à écrire (C8).

**C8 — texte à coller, nouvelle section 12 en fin de fichier, avant « Non gelés ici » ou après lui :**

```
## 12. Contre-lecture (R2)

Contre-lecteur neuf (ni auteur de ce fichier ni du code) : rapport `contre-lecture-prereg-nul-v8-v1.md`, empreinte SHA-256
[à calculer et recopier], verdict « scellable après corrections mineures (listées) », corrections obligatoires C1 à C9,
recommandées C10 à C15. Corrections appliquées dans cette version : [liste, avec les sections touchées]. Non appliquées :
[aucune, ou liste motivée]. Le diff entre le brouillon lu (`894b294b…`) et la version scellée a été relu par un lecteur neuf :
[oui, par … / non].
```

---

## B. Statistique — conforme (recalculs concordants), avec une précision (C9)

**Ce que le texte porte.** Toutes les décisions reposent sur des bornes ou des valeurs p exactes, jamais sur l'estimation ponctuelle seule.

- Ligne fatale (H1, H4) : test binomial exact unilatéral, équivalent à la borne de Clopper-Pearson unilatérale à 95 % (section 5, l. 138-143 ; code `p_valeur_exacte`, banc l. 359-366). Deux familles de onze hypothèses nulles chacune, au niveau familial 0,05, par la procédure de Holm (descendante) : « tenue » rejette H0ᵢ « taux ≥ α » (valeur p = P(Bin(1 000 ; 0,05) ≤ xᵢ)) ; « non tenue » rejette H0'ᵢ « taux ≤ α » (valeur p = P(Bin ≥ xᵢ)). Famille, sens, niveau, hypothèses : tout est défini. Le nul exact suit la même règle que les autres lignes fatales (il en fait partie).
- Artefact (H3) : borne basse de Clopper-Pearson unilatérale à 95 % > α, un seul test, sans correction (une seule hypothèse).
- Perte de puissance (H2) : borne de Newcombe (méthode 10, score hybride bâti sur les intervalles de Wilson), sur la différence de deux échantillons indépendants ; Holm sur une famille de deux ; le critère porte bien sur une borne de la différence, pas sur l'estimation.
- Conclusion d'ensemble : test d'intersection-union (tout doit être tenu, chacun à son niveau) ; Holm est plus sévère que nécessaire pour cette conclusion, donc prudent.
- Unité d'échantillonnage : la répétition (scénario tiré à neuf : lois, monde, instances, tirages) ; les répétitions et les lignes sont indépendantes par construction de la clé de graines. Aucune dépendance cachée (pas de grappe).

**Mes recalculs (scipy 1.18.1, numpy 2.5.3, Python 3.13.18 ; scripts `stats_scipy.py`, `newcombe_scipy.py` dans le dossier de travail du contre-lecteur).**

| rang de Holm | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| seuil 0,05/(12 − rang) | 0,004545 | 0,005 | 0,005556 | 0,00625 | 0,007143 | 0,008333 | 0,01 | 0,0125 | 0,016667 | 0,025 | 0,05 |
| promotions maximales « tenue » (texte) | 32 | 32 | 32 | 33 | 33 | 33 | 34 | 34 | 35 | 36 | 38 |
| promotions maximales « tenue » (moi) | 32 | 32 | 32 | 33 | 33 | 33 | 34 | 34 | 35 | 36 | 38 |
| promotions minimales « non tenue » (texte) | 70 | 70 | 69 | 69 | 69 | 68 | 68 | 67 | 66 | 65 | 63 |
| promotions minimales « non tenue » (moi) | 70 | 70 | 69 | 69 | 69 | 68 | 68 | 67 | 66 | 65 | 63 |

Détail des bornes : P(X ≤ 32) = 0,00366 (≤ 0,004545, donc 32 passe à tout rang), P(X ≤ 33) = 0,00592 ; P(X ≤ 38) = 0,04335, P(X ≤ 39) = 0,05982 (rang 11) ; P(X ≥ 63) = 0,03839, P(X ≥ 62) = 0,05111. La lecture du texte est exacte : « toute ligne à 32 promotions ou moins est tenue quelles que soient les autres ; 38 est le plafond absolu ; entre 39 et 62 une ligne n'est jamais « non tenue » ni « tenue » ; de 33 à 69 « non jugeable » est possible ». Borne haute de Clopper-Pearson à 0 promotion : 1 − 0,05^(1/1000) = 0,002991.

Artefact : 63 promotions sur 1 000 donne une borne basse de 0,050833 (> 0,05) ; 62 donne 0,049929. Le texte dit « au moins 63 » : exact.

Newcombe, nombre minimal de promotions sous v8 pour « tenue » (niveau 0,025 garanti / niveau 0,05 au mieux), avec les intervalles de Wilson de scipy (`binomtest(...).proportion_ci(method="wilson")`) : v7 à 1 000/1 000 → 964 / 962 ; v7 à 990 → 956 / 953 ; v7 à 970 → 939 / 936 ; perte maximale compatible 0,036 à 0,031 (niveau 0,025) et 0,038 à 0,034 (niveau 0,05). Le texte (l. 159-161) donne exactement ces nombres. Détail d'un cas : 970 contre 939 au niveau 0,025 : bornes [0,01280 ; 0,04982], donc borne haute < 0,05 ; 970 contre 938 : 0,05092, refusé.

**Niveau réel de la règle de Newcombe** (le texte la dit « approchée, non exacte » ; je l'ai mesurée). Simulation de 400 000 couples de 1 000 répétitions à la frontière exacte de H0 (perte vraie = 0,05), pour des puissances de 1,00 à 0,50 : probabilité de déclarer « tenue » à tort entre 0,0212 et 0,0260 pour un niveau nominal de 0,025, et entre 0,0437 et 0,0510 pour 0,05. L'approximation est correcte (au plus +0,001 d'excès) ; la règle est un peu prudente aux puissances proches de 1, qui sont celles de la course. Pas d'objection.

**Précision à ajouter (C9).** Le code de sortie du banc (0 ou 1) compare les taux observés à α, c'est-à-dire des estimations ponctuelles (`fatales_au_dessus_de_alpha`, banc l. 301-303 ; `code_de_sortie`, l. 311-313). Il sert à l'intégration continue, pas à l'issue. Le texte dit seulement « le code de sortie dit 0, 1, 2 ou 3 » : un lecteur pressé lira « 0 = confirmée », ce qui serait faux (T12a à 4 % rend 0 et « non jugeable »).

**C9 — texte à coller, remplace la fin de la ligne 124-126 (« …le code de sortie dit 0, 1, 2 ou 3 (docstring du banc). ») :**

```
le code de sortie dit 0, 1, 2 ou 3 (docstring du banc) mais **ne décide pas** : 0 et 1 comparent les taux observés à α
(estimations ponctuelles, indicateur pour l'intégration continue) ; seule la lecture gelée (`lecture.issue`, section 6 :
bornes de Clopper-Pearson et de Newcombe, correction de Holm) décide. Un code 0 n'est pas « confirmée » (par exemple T12a à
4 % rend 0 et « non jugeable »).
```

---

## C. Graine — règle sans ambiguïté ; parade contre le choix de graine à écrire (C3)

**Règle.** Elle est écrite sans ambiguïté (section 4, l. 92-104) et le code la suit à la lettre :

1. E = entier non signé gros-boutiste des 32 octets du SHA-256 des octets du fichier (`int(hashlib.sha256(octets).hexdigest(), 16)`). Code : `sha256_fichier` lit le fichier en binaire par blocs, sans normalisation (outils l. 33-37) ; `entropie_du_preenregistrement` fait `int(empreinte, 16)` (banc l. 169-172).
2. Répétition r de la ligne « nom|nul » : `SeedSequence(entropy=E, spawn_key=(c, r))`, c = entier gros-boutiste des quatre premiers octets de SHA-256 du texte UTF-8 « nom|nul » (`cle_ligne`, l. 146-147). Les 18 clés sont vérifiées distinctes avant toute course (`verifier_cles_distinctes`, l. 150-156).
3. `.spawn(3)` : scénario, noyau, tirages frais ; chacun réduit à s₀ + 2⁶⁴·s₁ avec `generate_state(2, uint64)` (l. 159-166). Le juge de production dérive ensuite ses graines internes avec `outils.graine_derivee`, inchangée.
4. Le banc calcule E lui-même ; aucune graine n'est tapée (mode décisif : `--graine` et `--preenregistrement` sont mutuellement exclusifs, l. 525-527).

**Peut-on choisir sa graine ?** Oui, par un détour que le texte n'écrit pas : la graine est l'empreinte du fichier, donc retoucher une virgule la change. Le texte écrit deux parades (l. 6-8) : « le premier scellement est contraignant » et « tout rescellement change la graine et reste visible dans l'historique public ». C'est insuffisant : (i) « contraignant » ne dit pas ce qu'on s'interdit ; (ii) rien n'empêche de lancer le banc en mode décisif sur des variantes du fichier avec des compagnons `.sha256` écrits en local (le code ne vérifie que la concordance du hash, pas qui a scellé ni si le commit existe), ce qui ne laisse aucune trace publique ; (iii) après une course décisive à l'issue décevante, rien n'interdit de modifier, resceller et rejouer. Je confirme que, pour l'instant, aucune course de ce genre n'a eu lieu (aucun dossier de sortie, aucun compagnon).

**C3 — texte à coller, nouvel alinéa à la suite de « Le banc calcule lui-même E… » (après la ligne 104) :**

```
- **Un scellement, une course décisive.** Aucune course en mode décisif n'a été lancée, sur aucune version de ce fichier
  (vérifié avant scellement : aucun dossier `resultats/banc-tricheurs-v8-validation-v1*`, aucun compagnon `.sha256`). La course
  décisive n'est lancée qu'après la poussée, dans l'historique public, du commit qui contient ce fichier, son compagnon
  `.sha256` et les 12 fichiers de code gelés. Toute course décisive dont le manifeste a été écrit est rapportée, qu'elle aille à
  son terme ou non. Si elle a rendu une issue (code 0 ou 1), cette issue fait foi : modifier ce fichier, le resceller (nouvelle
  graine) et rejouer n'est pas admis ; une reprise passe par un préenregistrement de version nouvelle (R12) qui cite la
  première course, son dossier et son empreinte. Un arrêt sans taux lu (code 3) autorise le rejeu de la section 8, et lui seul.
```

Remarque (pas une correction) : le scellement est une convention (un compagnon de format `sha256sum`) ; le code ne peut pas savoir qui l'a écrit. Le commit publié est donc la vraie preuve, d'où la mention de l'ordre commit puis course dans C3.

---

## D. Fidélité de la commande — conforme ; deux précisions (C4, C14)

Vérifié ligne à ligne contre `banc_tricheurs_v8.py` :

- Lignes : sans `--lignes`, le banc joue `LIGNES` (l. 124-127) = 11 fatales sous v8, T01 sous v1, fille neuve et fraîche neuve sous v8 et sous v7, T07 et T12b sous v8 = 18 lignes, comme la section 2 et la section 4.
- Répétitions : 1 000 (`REPETITIONS_DECISIVES`) ; le mode décisif refuse tout autre nombre, `--lignes` et toute autre durée maximale (l. 541-543). Durée maximale 10 800 s = 3 heures (l. 102).
- Graine dérivée de l'empreinte du fichier scellé, entropie ≥ 2⁶⁴ exigée (l. 204-206), fichier imposé `PREREG_DECISIF` (l. 177-179).
- Nul : sous « v8 », la bibliothèque est celle du juge de production (`nul_v8.membres_archive_v8` → `cycle.membres_de_l_archive(..., ajuste=True)`, `nul_v8.py` l. 161, banc l. 224 et 233) et le même évaluateur que la production (`nf.evaluer_v2`, banc l. 230 et 237 ; `cycle.py` l. 566). Sous « v7 » : `v7.membres_archive` et, pour les fiches sans parent, le juge continu `sp.evaluer` (l. 238-242). Sous « v1 » : la bibliothèque de la fille seule, sans membres ajustés ni archive (l. 223-226 : ni la branche v8 ni la branche v7 n'est prise), ce que dit la ligne T01|v1 de la section 2.
- Gel : `FICHIERS_GELES` (l. 111-113) compte 12 fichiers ; le bloc de la section 11 en compte 12 ; leurs empreintes sont identiques à celles des fichiers présents (comparaison `sha256sum` / bloc : aucune différence) ; l'essai `test_fichiers_geles_couvrent_les_imports` mesure la fermeture des imports.
- Sortie : `manifeste.json` écrit avant la course (l. 565), puis `banc-tricheurs-v8.json`, chacun avec son compagnon (`ecrire_json_scelle`) ; dossier de sortie non vide refusé (l. 534-535).
- Les tests (35) et les 34 mutations couvrent ces gardes (voir annexe 3) : R5 est respectée sur les gardes du banc.

**Incohérence de la section 8 (C4).** Le texte dit : « Après un arrêt (aucun taux lu), la même commande peut être rejouée ». Or un arrêt laisse `manifeste.json` (et le rapport d'arrêt) dans le dossier de sortie ; la même commande se heurte à `FileExistsError` (« dossier de sortie non vide », code 2). Il faut le dire.

**C4 — texte à coller, remplace le dernier alinéa de la section 8 (l. 218-219) :**

```
- Après un arrêt (code 3 ; aucun taux lu), le dossier de sortie de la course arrêtée contient déjà `manifeste.json` : le banc
  refuse de le réutiliser (code 2, « dossier de sortie non vide »). On le conserve tel quel (jamais supprimé ni renommé en
  silence, R12) et on rejoue la commande de la section 4 avec **un seul changement**, un dossier de sortie neuf (par exemple
  `../resultats/banc-tricheurs-v8-validation-v1-reprise-1`) : même fichier scellé, donc même graine, donc même course. La cause
  de l'arrêt et le rejeu sont dits dans le rapport. Toute autre intervention manuelle est un écart, consigné.
```

**Banc v7 et banc v8 (C14, recommandée).** Le banc v7 ne peut ni dériver la graine d'un fichier scellé (il dérive ses graines par SHA-256 sans `SeedSequence`) ni appeler la fonction du juge de production (il garde une copie locale du « candidat ») ; le préenregistrement nomme bien le fichier qui le fait (`banc_tricheurs_v8.py`, commande l. 120) mais ne dit pas pourquoi un banc v8 existe : c'est dans la docstring du banc (l. 7-9). Une phrase suffit.

```
- **Pourquoi un banc v8.** Le banc v7 (`banc_tricheurs_v7.py`, chargé en instance propre et inchangé pour ses scénarios) ne peut ni
  dériver sa graine de l'empreinte d'un fichier scellé (il dérive ses graines par SHA-256, sans `SeedSequence`) ni juger sous le
  nul de production (ses membres d'archive « candidat » sont une copie locale) ; `banc_tricheurs_v8.py` le fait, et les essais
  `MembresNulV8.test_identiques_au_candidat_du_banc_v7` et `JugeSousNulV8.test_juge_v8_identique_au_banc_v7_aux_memes_graines`
  garantissent l'identité avec le candidat du banc v7.
```

**Durée (C11, recommandée).** Mon rejeu de L8 (18 lignes × 20 répétitions) a pris 63,2 s de mur (somme des lignes 123,3 s) sous la charge des autres agents, contre 20,1 s pour L8 de l'auteur, soit environ 53 minutes pour 1 000 répétitions. La bande « 17 à 45 minutes » est donc un peu optimiste ; l'arrêt à 3 heures laisse largement de la marge.

```
Attendu : 17 à 55 minutes selon la charge de la machine (rejeu de L8 par le contre-lecteur sous charge : 63,2 s à 20
répétitions, soit ≈ 53 minutes) ; arrêt à 3 heures (section 8).
```

---

## E. Argument de validité (`nul_v8.py`) — correct tel qu'écrit

**Ce que fait exactement le code.** Pour une fiche, le juge forme `log W_t = log q(y_1..t) − max_m log p̂_m(y_1..t)` (`evaluer_v2`, `nul_filles_v2.py` l. 207-221), où :

- q est la loi gelée de la fiche, figée avant les tirages frais (l'empreinte de l'engagement entre dans la graine des tirages : `selection_pari.tirer_frais`, l. 525-547) ;
- les membres ordinaires sont évalués tels quels ; la part de calibrage d'une fille (ses 50 premiers tirages) ne sert qu'au poids calibré d'un membre ordinaire (`sp.calibrer(e["bibliotheque"], issues[:c], …)`, l. 207), jamais aux membres ajustés ;
- les membres ajustés (`ajuste_lineaire:archive`, `ajuste_log:archive:<survivante>`, et pour une fille ceux du nul des filles v2) sont ajustés **à chaque instant de lecture t, sur les t premières issues de la part d'évaluation**, c'est-à-dire exactement les issues sur lesquelles le numérateur est évalué (`issues, instances = issues[c:], instances[c:]` ; `valeurs_ajustees` ajuste sur `G_tout[:t]` ou `X_tout[:t]`, l. 154-185). **Il n'y a pas de part séparée pour le nul**, comme le dit le texte.
- Marges d'optimisation : le membre linéaire est maximisé par espérance-maximisation et l'on ajoute l'écart de dualité de Frank-Wolfe (`grad.max() − t`), borne exacte pour un problème concave sur le simplexe (`_lineaire`, l. 91-108) ; le membre log-linéaire est maximisé par la méthode de Newton amortie et l'on ajoute le décrément de Newton au carré s'il est ≤ 0,25, sinon la borne triviale 0 (`_logit`, l. 111-151). Les deux sont plafonnés à 0 (une log-vraisemblance est ≤ 0).

**L'argument est-il juste ?**

1. *Élargir la bibliothèque ne peut que réduire la richesse* : oui, le maximum sur une famille plus grande est plus grand, donc W plus petit, pour une même suite d'issues. Précision de portée (C10) : dans le banc, v7 et v8 ne voient pas la même suite d'issues (la graine des tirages frais dérive de l'empreinte de l'engagement, qui contient la bibliothèque), et les lignes v7 et v8 sont de toute façon des échantillons indépendants. La monotonie « trajectoire par trajectoire » vaut à issues égales ; elle donne en loi « taux(v8) ≤ taux(v7) » pour un même monde. C'est ce que dit le texte pour l'erreur de première espèce ; le mot « trajectoire par trajectoire » dans A2 doit être nuancé (C10).
2. *Condition de l'inférence universelle (point 1 de l'auteur, section J)* : exacte. Dans le rapport de vraisemblance scindé de Wasserman, Ramdas et Balakrishnan (2020), le maximum de vraisemblance du **nul** est calculé sur la part même où le rapport est évalué ; c'est ce qui lui permet de dominer la vraisemblance de la vraie loi, W_t ≤ q(y_1..t)/P(y_1..t), rapport de vraisemblance qui est une martingale positive d'espérance 1 sous P. Ce qui doit être indépendant des données d'évaluation, c'est l'**alternative** (le numérateur) : ici la loi gelée avant les tirages. La version séquentielle (réestimation à chaque instant t, lecture à huit instants fixés) reste valide parce que la borne W_t ≤ M_t, avec M_t = q/P, tient trajectoire par trajectoire quel que soit l'instant et la manière dont le maximum est atteint ; Ville s'applique à M_t, donc à tout sous-ensemble d'instants. Le texte (section 1, l. 33-34) et la docstring (point 4) disent la même chose, correctement.
3. *Extension aux familles ajoutées* : correcte sous l'hypothèse que la loi du monde appartient à une famille du nul. Les lignes T12a (monde = parent A) et nul exact (fille = A, monde A) sont dans ce cas ; pour les huit lignes de la classe linéaire et les deux de la classe log-linéaire, la loi **de la fiche** est elle-même un membre, donc log W ≤ 0 quel que soit le monde (cas plus fort que Ville). Le tricheur du banc est toujours « monde = fiche », le pire cas.
4. *Règle de marge des filles* : elle ne fait que retirer des promotions. J'ai vérifié que « tous les membres ajustés comptent parmi les enveloppes » (docstring `nul_v8.py` l. 34-35) est exact pour le comportement : l'évaluateur ajoute à `enveloppes` **tous** les membres de `par_ajuste`, drapeau `enveloppe` ou non (`nul_filles_v2.py` l. 230-231). Aucune inexactitude à corriger.
5. Réserves du texte (ajustement à second ordre pour les membres log-linéaires, bornes des paramètres à [−60 ; 60], archive restreinte à l'espace de la fiche, multiplicité entre fiches inchangée) : dites, correctes, reprises section 1 et section 10.

Je n'ai trouvé aucune erreur dans l'argument. Une observation de fond, reprise en F : sa conclusion (« le taux d'erreur de première espèce est conservé ») ne dit rien d'un monde qui ne serait dans aucune famille du nul.

---

## F. Classe d'attaque et revendications — dite explicitement ; quatre précisions (C7)

**Conforme.** La section 10 sépare une classe couverte (la loi du tricheur est un membre du nul v8) d'une classe non couverte, « dite, non fermée » (recombinaisons par morceaux avec une survivante, poids dépendant de l'instance, produits de plus de deux lois ou de deux lois autres que les parents, compositions d'étapes, déformations non monotones, lois hors archive). Elle dit que rien n'est revendiqué sur la banque réelle. Cela correspond à la docstring de `nul_v8.py` (l. 75-90). La règle d'anti-faux-gap (R8) est respectée sur l'essentiel.

**À préciser, sans quoi « confirmée » dirait plus que ce que la course mesure :**

1. *Dix lignes sur onze vérifient une inégalité, pas un contrôle probabiliste.* Pour les huit lignes de la classe linéaire, log W ≤ 0 est exact (aux arrondis près) à chaque répétition, quel que soit le monde : le banc vérifie que le code applique l'inégalité, pas que l'erreur de première espèce est contrôlée sur des mondes variés. Pour T05s et T09g, c'est la même inégalité à la marge de Newton près. Seule T12a (le monde est au nul, la fiche est hors classe) éprouve la borne probabiliste de Ville. Ce n'est pas un défaut du plan (c'est exactement ce que v8 promet), mais le texte ne doit pas laisser croire à onze épreuves probabilistes.
2. *Le « prix en puissance » est mesuré à effet fort.* Les deux lignes de puissance (fille neuve, fraîche neuve) ont, dans le banc publié, des richesses médianes de l'ordre de 40 à 70 nats pour un seuil de 3 ; une perte de quelques nats sur le dénominateur, qui est le prix attendu d'un nul plus riche, y est invisible. Le critère « perte ≤ 0,05 » ne dit rien de la puissance d'une découverte modérée. C'est une limite de la mesure, pas une erreur ; elle doit figurer dans la lecture de « confirmée ». Une ligne à effet faible serait un complément pour une version suivante (elle exigerait de changer le code gelé).
3. *Une partie de la classe couverte n'a pas de ligne.* Le produit des deux parents tempéré et incliné (membre `ajuste_log:AB`) et les formes de v0 sont dans la classe couverte (section 10, l. 249 ; `nul_v8.py` l. 79-82) mais aucune ligne du banc ne les attaque (T05s et T09g utilisent une loi connue seule).
4. *La multiplicité entre fiches n'est pas rejouée.* Les lignes T14 à T16 du banc v7 (règle e-BH) ne sont pas dans la course (le banc v8 le dit, docstring l. 36 ; le préenregistrement ne le dit pas). Comme les richesses ne peuvent que baisser, la règle e-BH ne promeut pas plus qu'avant, mais « validé » ne couvre pas ce point.

**C7 — textes à coller.**

Remplace l'issue 4 de la section 6 (l. 183-184) :

```
4. **« confirmée »** — les 11 lignes fatales, l'artefact et les 2 pertes tenus. Lecture : sur les mondes synthétiques du banc
   (K = 3 issues, 2 traits), aucune des 11 lignes fatales n'est promue au-dessus de α (bornes de Clopper-Pearson, Holm) ; le banc
   a vu l'artefact qu'il doit voir ; et le nul v8 ne coûte pas plus de 0,05 de puissance sur les deux lignes de puissance, **qui
   sont à effet fort** (puissance attendue ≥ 0,95, P5). Dix des onze lignes fatales vérifient l'inégalité « log W ≤ 0 » de leur
   classe (exacte pour la classe linéaire, à la marge de Newton près pour la classe log-linéaire) ; seule T12a éprouve la borne
   probabiliste de Ville. Le nul v8 peut porter la mention « validé sur la classe du banc (section 10) » ; rien n'est revendiqué
   hors de cette classe, ni sur la puissance à effet faible, ni sur la multiplicité entre fiches, ni sur la banque réelle.
```

Ajoute à la section 10, à la suite de la liste « Classe non couverte » (après la ligne 253) :

```
- **Couverte par l'argument, sans ligne du banc** : le produit des deux parents d'une fille, tempéré et incliné (membre
  `ajuste_log:AB`), et les formes de v0 ; leur fermeture n'est pas mesurée ici.
- **Hors de la portée de cette validation** : la multiplicité entre fiches (règle e-BH ; lignes T14 à T16 du banc v7, non
  rejouées) ; la puissance à effet faible (les deux lignes de puissance sont à effet fort) ; la banque réelle.
```

---

## G. Provenance — chiffres du banc de 200 répétitions bien étiquetés ; renvois à durcir (C5)

**Conforme.**

- Aucun chiffre du banc de 200 répétitions n'est présenté comme résultat : la section 1 les donne comme « motivation seulement (ce n'est pas une preuve de ce qui est testé ici) », avec chemin et empreinte, et la section 3 dit que les prédictions ont été écrites après les lectures préalables et ne décident pas.
- Empreinte du fichier publié : `sha256sum resultats/banc-tricheurs-v7-2026-11-01/banc-tricheurs-v7.json` = `2fc037b4eda23cf6b36e038c2034c53e6de4625f07308159a896ad04c808ca3c`, celle que cite le texte (l. 22) ; elle concorde aussi avec son compagnon. Les chiffres cités sont exacts : T02 150/200 = 75 %, T03b 170/200 = 85 %, T04 190/200 = 95 %, T05s 161/200 = 80,5 % sous v7 ; 0/200 chacun sous « candidat » ; perte de puissance −0,03 (fille neuve : 0,97 contre 1,00) et +0,01 (fraîche neuve : 1,00 contre 0,99) ; et, dans L0, fille neuve 200/200, fraîche neuve 198/200, T07 1/200, T01|v1 90/200.
- Durées de la section 4 (20,1 s ; 38,8 s ; 49,3 s) : exactes (JSON de L8 et de L2). Chiffres de la section 10 sur les démonstrations : exacts (8 engagements de génération 3 des deux courses du monde planté ; log W max abaissé de 1,33 à 18,89 nats ; G3-F16 : 4,13 sous v7 puis 2,81 sous v8 ; couche 1 : 352 fiches comparées, aucune différence de log W max).
- Préfixes de hachage cités à la section 9 : tous exacts (annexe 2 donne les empreintes pleines).

**À corriger (C5).**

1. Les chemins de la section 9 sont dans un dossier de travail hors dépôt (`/tmp/claude-0/…/scratchpad/`), qui ne survivra pas ; les empreintes sont des préfixes de huit caractères. Ce n'est pas une provenance au sens de R6.
2. Deux lectures sont absentes du tableau (voir I).
3. L7 et L8 ont été jouées avec un état antérieur du banc (`banc_tricheurs_v8.py`, `0506194b…`), L1 et L2 avec un brouillon de `nul_v8.py` (`59c2f58f…`) ; le texte ne le dit pas. Le banc gelé (`23d2b7d2…`) reproduit L7 et L8 valeur pour valeur (deux rejeux indépendants, annexe 3), donc les chiffres valent pour le code gelé ; il faut l'écrire.

Le texte à coller est donné en I (C5).

---

## H. Symétrie (R4) — partiellement conforme ; trois corrections (C1, C2, C13)

**Conforme.** Les audits A1 à A4 sont écrits d'avance, calculés par le code gelé (`lire_v8`, l. 465-479), suspendent l'issue (`issue_suspendue_par_audit`), et le texte dit qu'une issue « confirmée » sans déclencheur n'est pas pour autant tenue pour propre (R13 relit les membres dominants et les log W). Les deux sens sont couverts pour l'artefact (A3 : trop bas, le banc perd ses dents ; trop haut, le scénario a changé) ; A2 vise « trop beau » (v8 plus puissant que v7) ; A1 et A4 visent « trop laid ».

**Trois lacunes.**

1. *La règle de conclusion après audit est trop indulgente (C1).* Le texte dit : « soit un défaut est trouvé — la course est invalide —, soit aucun défaut n'est trouvé et l'issue est lue avec la note jointe ». Pour A1 sur la classe linéaire et pour A4, une promotion ou un log W positif contredit une inégalité démontrée, éprouvée par 35 essais et 34 mutations ; « aucun défaut trouvé » voudrait dire que l'inégalité est fausse ou que l'audit est incomplet, deux cas où lire « confirmée » tromperait. Et A4 est décrit à la ligne 203 comme « défaut du code, même sans promotion » avant d'être soumis à la même alternative : contradiction. Pire, une seule promotion sur 1 000 (« tenue » à tous les rangs de Holm) peut laisser l'issue à « confirmée ». Pour la classe log-linéaire, la marge de Newton n'est pas démontrée : une promotion y est improbable (l'écart réel à l'optimum devrait dépasser la marge d'au moins 3 nats) mais elle ne doit pas permettre « confirmée ».
2. *Le résultat « trop beau » que le texte prédit n'a pas de contrôle écrit (C2).* P1 prédit 0 promotion partout : si c'est ce qui sort, rien dans le texte ne distingue « le nul ajusté a fermé les lignes » de « le nul ajusté n'a pas été exercé ». La seule dent de la course, T01|v1, ne concerne que la famille « parent + loi aveugle » ; les quatre lignes qui ont motivé v8 (T02, T03b, T04, T05s) n'ont aucune ligne de dents dans la course (leurs lignes « v7 » du banc publié n'y sont pas rejouées). Les dents de ces quatre lignes reposent sur L0 (200 répétitions) et L5 (nuls mutés), exploratoires. Un contrôle sans coût de code existe : le rapport donne les membres dominants. Dans mon rejeu de L8, `ajuste_lineaire:archive` domine 18/20 (T02), 16/20 (T03b), 19/20 (T04), et `ajuste_log:archive:S1` plus `ajuste_lineaire:archive` 20/20 (T05s).
3. *Une issue décevante n'est auditée que si elle tombe dans A1 à A4 (C13, recommandée).* Une ligne T12a « non tenue », une perte de puissance « non tenue » ou un « banc sans dents » n'ont pas d'audit. R4 veut le même effort dans les deux sens.

**C1 — texte à coller, remplace l'alinéa « Audit : note écrite… » (l. 205-208) :**

```
Audit : note écrite (cause cherchée, vérifications faites, conclusion) avant toute lecture de l'issue. Conséquences, écrites
d'avance :

- **A4, ou A1 sur une ligne de la classe linéaire** : l'inégalité log W ≤ 0, démontrée pour cette classe et éprouvée par les
  essais et les mutations, est falsifiée. Défaut du code ou de l'argument, localisé ou non : la course est **invalide d'office**
  et ne rend aucune issue, quelle que soit la conclusion de l'audit. L'audit sert à trouver la cause ; la reprise est une
  version nouvelle, avec un préenregistrement nouveau.
- **A1 sur T05s ou T09g seulement (classe log-linéaire), ou log W max > +0,25 sur l'une de ces deux lignes** (0,25 : marge de
  Newton maximale admise par le code, `DECREMENT_ADMIS`) : l'issue « confirmée » est **interdite**. Si l'audit localise un
  défaut du code, la course est invalide comme ci-dessus ; sinon l'issue est « non jugeable (réserve log-linéaire) » : la ligne
  est déclarée ouverte (la marge de Newton n'est pas démontrée) et les autres lignes sont rapportées sans revendication sur la
  classe log-linéaire.
- **A2, A3, A5** : l'audit dit si un défaut est trouvé (course invalide, aucune issue) ou non (l'issue est lue avec la note
  jointe).

Une issue « confirmée » sans déclencheur n'est pas pour autant tenue pour propre : le contre-lecteur du verdict (R13) relit les
membres dominants et les log W rapportés.
```

**C2 — texte à coller, nouvel audit à la suite de A4 (après la ligne 204) :**

```
- **A5** — nul ajusté inactif (propreté suspecte : un 0/1 000 qui ne viendrait pas du nul ajusté). Lu sur les membres dominants
  à l'instant final (`dominants` du rapport, quatre premiers de chaque ligne) : sur T02, T03b et T04, si
  `ajuste_lineaire:archive` domine dans moins de la moitié des répétitions ; sur T05s, si `ajuste_log:archive:S1` et
  `ajuste_lineaire:archive` ensemble dominent dans moins de la moitié des répétitions. Repère : sur 20 répétitions (L8), ces
  membres dominent 18/20, 16/20, 19/20 et 20/20. Audit : les survivantes S1 et S2 étaient-elles dans l'archive de la fiche,
  les membres ajustés construits, les instants de lecture respectés ?
```

**C13 (recommandée) — texte à coller, nouvel audit à la suite de A5 :**

```
- **A6** — toute issue « infirmée (validité) », « infirmée (puissance) » ou « non jugeable (banc sans dents) » : même audit,
  avant la lecture de l'issue (R4 : une issue décevante est auditée comme une issue trop belle). Un défaut du code ou du banc
  trouvé rend la course invalide ; sinon l'issue est lue, la note jointe.
```

---

## I. Lectures préalables et espaces de graines — garantie appliquée ; déclaration incomplète (C5)

**L'espace de graines disjoint est réellement appliqué.**

- Mode exploratoire : `--graine` doit être dans [0 ; 2⁶⁴[ ; sinon refus, code 2 (banc l. 549-550). Mode décisif : `lire_preenregistrement` refuse une entropie < 2⁶⁴ (l. 205-206). Les deux gardes sont éprouvées : essais `test_refus_du_banc_avant_toute_course` et `test_artefacts_preenregistrement` ; mutations « espace exploratoire non borné » et « entropie décisive dans l'espace exploratoire acceptée » : tuées.
- Une empreinte SHA-256 est inférieure à 2⁶⁴ avec une probabilité de 2⁻¹⁹² : la garde ne se déclenchera jamais sur un vrai fichier, elle ne sert qu'à interdire une manœuvre.
- Les entropies de toutes les lectures du tableau (7, 41, 20261101, 20261027, 3, 5 et les `graine_derivee` du banc v7) sont < 2⁶⁴. Résidu honnête : les lectures de l'agent précédent « sans trace sur disque » (déclarées l. 241-243) ne peuvent pas être exclues, mais elles ont toutes utilisé `--graine` (donc < 2⁶⁴) ou la dérivation du banc v7 : la graine décisive, empreinte d'un fichier qui n'existe pas encore sous sa forme scellée, ne peut pas avoir été jouée.

**Lectures non déclarées** (inventaire de `…/scratchpad/v8/`, `…/scratchpad/v58/` et `…/organisme-depot/`) :

- `v58/runner/banc-reduit-v8/` : un rejeu, à 21:23 UTC, de la commande de l'intégration continue (entropie 20261101, T01, T02, T04, nul exact × 20, T01|v1 × 20), avec le banc **gelé** (`23d2b7d2…`). Résultat identique à L7 ligne par ligne (promotions, log W max, membres dominants) ; seules les durées diffèrent. Absent du tableau.
- Mes propres lectures (annexe 3) : essais, mutations, rejeu de L8, rejeu de L6.
- Le dossier `organisme-depot/demo-proposeur-1941` est une démonstration du juge v7 jouée à 19:41 UTC, avant la décision v8 : hors sujet, mais à savoir. Le dossier `organisme-depot/banc-tricheurs-1946` est une copie du banc v7 publié (même empreinte `2fc037b4…`) : c'est L0.

Toutes les autres lectures du tableau correspondent à des fichiers retrouvés dont les préfixes de hachage sont exacts. Ce qui était vu est correctement résumé (comptes de L1, L2, L7, L8, L9 recoupés ; L5 : mes mutations donnent les mêmes comptes, T02 16/20, T03b 2/20, T04 19/20, T05s 12/20 ; L6 : mon rejeu donne les mêmes maxima, T02 −1,02·10⁻⁵ pour le plus haut de la classe linéaire, T12a −1,084).

**C5 — texte à coller.** Ajoute deux lignes au tableau de la section 9 (après L10) :

```
| L11 | auteur, 21:23 | rejeu de la commande de l'intégration continue avec le banc **gelé** (`23d2b7d2…`) | 20261101 | T01, T02, T04, nul exact (v8), T01\|v1 × 20 | identique à L7, ligne par ligne (promotions, log W max, membres dominants) ; seules les durées diffèrent | `resultats/lectures-prealables-nul-v8-v1/L11-banc-reduit-v8.json` (`56276b9e0b62…`) |
| L12 | contre-lecteur (R2), 21:30 à 22:05 | (a) les 35 essais de `essais/test_v58_nul_v8.py` ; (b) `essais/mutations_v58.py` ; (c) rejeu de L8 avec le banc gelé ; (d) rejeu de L6 (`v58_verif_bornes.py`) | (a, b) comme L4 et L5 ; (c) 7 ; (d) 41 | (c) 18 lignes × 20 ; (d) 11 lignes fatales × 10 | (a) 35 réussis ; (b) 34 mutations tuées pour la raison attendue, mêmes comptes que L5 ; (c) identique à L8 valeur pour valeur ; (d) mêmes maxima que L6 | rapport de contre-lecture, annexe 3 |
```

Remplace l'alinéa qui suit le tableau (l. 241-243) par :

```
Code joué par chaque lecture : L1 et L2 ont été jouées avec un brouillon de `pole/nul_v8.py` (`59c2f58f…`) ; L7 et L8 avec le
`nul_v8.py` final (`cc452aaf…`) mais un état antérieur du banc (`demonstrations/banc_tricheurs_v8.py`, `0506194b…`) ; le banc
gelé (`23d2b7d2…`) reproduit L7 (L11) et L8 (L12, c) valeur pour valeur : les chiffres de L7 et de L8 valent donc pour le code
gelé. Les sorties L1 à L9 et L11 (fichiers JSON de résultats, plus les journaux de génération 3 qui fondent les chiffres de la
section 10 ; pas les dossiers de cours, de plusieurs dizaines de mégaoctets) sont copiées dans le dépôt, avec leur compagnon
`.sha256`, sous `resultats/lectures-prealables-nul-v8-v1/` ; les empreintes pleines sont données en annexe du rapport de
contre-lecture. Des courses de l'agent précédent sans trace sur disque ne peuvent pas être exclues ; aucune n'a pu utiliser la
graine décisive (section 4, garantie (i)). Les prédictions de la section 3 ont été écrites après L0 à L12 et en tiennent
compte : c'est déclaré, et c'est pourquoi elles ne décident pas de l'issue.
```

---

## J. Les quatre points signalés par l'auteur

**(1) Le nul est ajusté sur les mêmes issues fraîches que le numérateur : l'auteur a-t-il raison ?** Oui, exactement. Voir E, point 2. L'inférence universelle exige l'indépendance entre l'**estimateur de l'alternative** (ici la loi gelée avant les tirages) et la part d'évaluation ; le maximum de vraisemblance sous le **nul** se calcule sur la part d'évaluation elle-même, et c'est ce qui fait dominer le vrai modèle. Le code le fait comme le texte le dit (ajustement sur les t premières issues, à chaque instant de lecture, borne ajoutée). Aucune correction.

**(2) Classe log-linéaire : le refus « par construction » n'est pas démontré. Le texte le dit-il et en tire-t-il une prédiction prudente ?** Il le dit, bien et à trois endroits (section 1, réserve ; section 7, A1 ; banc, docstring), mais P1 traite les dix lignes de la même façon (« refusées par construction… 0 promotion sur 1 000 »), ce qui contredit la réserve. Une prudence existe dans les données : sur 20 répétitions, log W max vaut −0,038 (T05s) et −0,033 (T09g) (L8, rejeu), très loin de 0,25. Mais ce n'est pas écrit. D'où C6, qui scinde P1 et fixe, pour la classe log-linéaire, une prédiction chiffrée plus prudente et un déclencheur (C1, deuxième alinéa). Remarque de bon sens : pour qu'une promotion se produise sur T05s ou T09g, il faudrait que l'écart réel à l'optimum dépasse la marge de Newton (décrément au carré) d'au moins log 20 ≈ 3,0 nats, pas de quelques centièmes ; l'événement est improbable, mais le texte ne doit pas le déclarer impossible. Le déclencheur « log W max > +0,25 » de C1 est la même grandeur vue plus tôt : l'écart réel dépasse la marge de plus de 0,25 nat.

**C6 — texte à coller, remplace P1 (l. 78-80) :**

```
- **P1a** (signe : sous α) : chacune des 8 lignes fatales de la classe linéaire (T01, T02, T03u, T03b, T04, T09l, T17s, nul
  exact), refusées par construction : **0 promotion sur 1 000**, et log W ≤ 0 (aux arrondis près, moins de 10⁻⁶) à chaque
  répétition.
- **P1b** (signe : sous α, confiance moindre) : T05s et T09g, de la classe log-linéaire, où le refus tient à la marge de
  Newton, non démontrée (section 1) : **0 promotion sur 1 000** attendue, et log W max ≤ +0,25 (marge de Newton maximale admise
  par le code). Repère : −0,04 et −0,03 sur 20 répétitions (L8). Une promotion, ou un log W max au-dessus de +0,25, déclenche
  l'audit de la section 7 (conséquences en A1 et C1).
- **P1c** : T12a (la vérité est au nul, la fiche est hors classe) : **au plus 10 promotions sur 1 000** (taux ≤ 0,010). Risque
  dit : la borne de Ville n'impose que 5 % ; si T12a dépasse 38 promotions, « non jugeable » ou « non tenue » est l'issue
  honnête (section 5).
```

Compatible avec le code gelé : `PREDICTIONS` et `lecture.predictions` rapportent déjà, par ligne, « 0 promotion » (hors T12a) et « taux ≤ 0,010 » pour T12a ; le seuil +0,25 se lit dans `log_w_max_max` du rapport.

**(3) Seuils de Holm annoncés (32 à 38 ; 63 pour l'artefact) : recalcul.** Concordent exactement, rang par rang, dans les deux sens (tableau en B). Le tableau « promotions min (non tenue) » (70 à 63) concorde aussi.

**(4) Critère de perte de puissance par borne de Newcombe : recalcul d'un cas.** Concorde : v7 à 970/1 000, v8 à 939/1 000, niveau 0,025 : bornes [0,01280 ; 0,04982] avec les intervalles de Wilson de scipy, donc « tenue » ; à 938 : 0,05092, refusé. Les trois exemples du texte (964/962, 956/953, 939/936) sont exacts. Niveau réel de la règle mesuré par simulation (B) : entre 0,0212 et 0,0260 pour 0,025 nominal. Une conséquence à savoir pour A2 : sur le banc v7 publié, fille neuve, 194/200 contre 200/200 donne une borne haute de la perte de −0,0104 (< 0) : A2 se serait déclenché sur L0. Il peut se déclencher par hasard (de l'ordre de 5 % par ligne de puissance sous un nul correct, parce que les deux échantillons sont indépendants) ; le texte doit le dire.

**C10 (recommandée) — texte à coller, remplace A2 (l. 198-200) :**

```
- **A2** — nul v8 **plus puissant** que v7 sur une ligne de puissance (borne haute de Newcombe de la perte, 95 % unilatérale non
  corrigée, < 0) : contraire à la monotonie (vraie trajectoire par trajectoire à issues égales, donc en loi pour un même monde).
  Les deux échantillons étant indépendants, ce déclencheur peut se produire par hasard (de l'ordre de 5 % par ligne sous un nul
  correct ; déjà vu sur le banc v7 publié de la section 1, fille neuve : borne haute −0,010). Trop beau, donc audité ; sans défaut
  trouvé, l'issue n'est pas changée.
```

**C12 (recommandée, décision du directeur) — texte proposé à la fin de la section 6.** Le nul v8 est déjà décidé comme nul par défaut ; les issues ne disent rien de cet usage. Phrase à trancher par Lazar, non à coller sans lui :

```
Cette issue gouverne la mention « validé » du nul v8, non son usage : [à décider par le directeur : le nul v8 reste le nul par
défaut du dépôt quelle que soit l'issue, puisque, par la monotonie de la section 1, il ne promeut jamais plus que le nul v7 ;
ou : il est retiré de la ligne de commande par défaut en cas d'issue « infirmée (validité) »].
```

---

## Procédure avant la course (C15, recommandée)

- Au scellement, committer **en un seul commit** : ce fichier, son compagnon `.sha256`, les douze fichiers gelés, `essais/test_v58_nul_v8.py`, `essais/mutations_v58.py`, `.github/workflows/bench-reduit.yml`. Au moment où j'écris, tous ces fichiers sont non suivis par git (état `??`) ; la section 11 dit que le banc vérifie les empreintes, mais seul un commit les fige pour un lecteur extérieur.
- Noter dans le rapport de la course l'identifiant du commit (`git rev-parse HEAD`) : le manifeste du banc enregistre l'empreinte de chaque fichier de code (93 fichiers) mais pas l'identifiant de commit.
- Lancer les 35 essais et le banc de mutations sur l'arbre scellé avant la course (ils prennent respectivement 30 s et quelques minutes).
- Remarque sans conséquence : l'intégration continue installe `numpy>=1.25` sans version fixe et Python 3.12 ; le texte (L10) la dit « déterministe » ; c'est vrai du code, pas garanti entre versions de numpy. Elle ne décide rien.

---

## Annexe 1 — recalculs statistiques (scripts)

Dans `/tmp/claude-0/-home-claude/730d0294-0b2b-55ca-8b32-49f2d3ec072d/scratchpad/contrelecture-v8/` : `stats_scipy.py` (Holm dans les deux sens, artefact, bornes de Clopper-Pearson par loi bêta), `newcombe_scipy.py` (Newcombe avec les intervalles de Wilson de scipy, cas publiés), `niveau_newcombe_mc.py` (niveau réel de la règle, 400 000 simulations par cas, graine propre `SeedSequence(2026110177)`), `exact_inconditionnel.py` (essai écarté : un test exact inconditionnel à statistique non studentisée n'a aucun pouvoir ici, valeur p de 0,2 à 0,3 aux cas limites ; sans objet pour juger du texte). Aucune course du banc.

## Annexe 2 — empreintes pleines des lectures préalables (SHA-256)

Base : `/tmp/claude-0/-home-claude/730d0294-0b2b-55ca-8b32-49f2d3ec072d/scratchpad/` (chemin des chiffres de la section 9).

| lecture | fichier | empreinte |
|---|---|---|
| L1 | `v8/banc-reduit-1/banc-tricheurs-v8.json` | `bde5a7951f7085893ccea38484bcaa1dc77fa3bd903d3dc31d74bb19175cc958` |
| L2 | `v8/banc-complet-20/banc-tricheurs-v8.json` | `95527da3c31514173f714bbe12bc47fe380ed86f14d43796903e6e520440821e` |
| L3 | `v8/demo-proposeur-v8/demo-couche1-proposeur-v8.json` | `9dc732eed5632c90187f100b8202c39997f1f28cf1bf58698b336065c99b0bdb` |
| L3 | `v8/demo-couche1-v8/demo-couche1-v8-v1.json` | `a406b84be598e87b35e1d44f17cc84859d1fad828a0895868f6c3b24301a7667` |
| L3 (v7, non cité) | `v8/demo-proposeur-v7/demo-couche1-proposeur-v7.json` | `e1e9a8403f7c987485db6d102c559434f9c52ffc21cdcb0d4d23dbee8eb9080d` |
| L3 (v7, non cité) | `v8/demo-couche1-v7/demo-couche1-v7-v3.json` | `957c90bdcf3c4f59a7e574249e0fed1a6b0d2ec2fffc46910b8fdf1426c9d326` |
| L6 | `v58_verif_bornes.py` | `f9ac2824bf6d3778cb322666981ad90ebbb8ce1dfe06a9f00f280474fcbe0cbf` |
| L7 | `v58/banc-reduit-ci/banc-tricheurs-v8.json` | `c565dcddd3c674c2927709f0b3a2c7e272c15bfb5223864c24fa976cd295528c` |
| L8 | `v58/banc-complet-20-graine7/banc-tricheurs-v8.json` | `483f2e05ee243053e1084a6837cf56a6da0da55f82f1c58deecc14ef6eb830e5` |
| L9 | `v58/demo-proposeur-v8/demo-couche1-proposeur-v8.json` | `fc39bc2cbc1cb4d8f7a26f7ded94d3b96a70633d91ac5798b72fd9d9119ebacd` |
| L9 | `v58/demo-proposeur-v7/demo-couche1-proposeur-v7.json` | `2dea09f8e33d2595a568836c2906f1e04eaf8fc60f199aec17ee9bc49f4c82ce` |
| L9 | `v58/demo-couche1-v8/demo-couche1-v8-v1.json` | `bc32d6310716244e074a2b77041f58fea400d946c2e13d5d236d3e95410de81f` |
| L11 (non déclarée) | `v58/runner/banc-reduit-v8/banc-tricheurs-v8.json` | `56276b9e0b625d83ddf6854a6070b1f626347f430d1205f3d063a0981173b3d5` |
| section 10 | `v58/demo-proposeur-v7/courses/plante-aveugle/journal/generation-03.json` | `d08911053777018fe78fad49e24076fade0efad2ad9658f09a7f6d9aefa130e2` |
| section 10 | `v58/demo-proposeur-v8/courses/plante-aveugle/journal/generation-03.json` | `9b835af431525511061a54f631df226ab8f6aa5e74facf4bce7a8190d4ae72c2` |
| section 10 | `v58/demo-proposeur-v7/courses/plante-exploration/journal/generation-03.json` | `e165d7169d8a7108667f8c5f8f5c1fd3f0ea4c87a549be969f2cc3471abadb4a` |
| section 10 | `v58/demo-proposeur-v8/courses/plante-exploration/journal/generation-03.json` | `fb7f6fb571d7f65d18a750cc821b396695c192418122ca8896f812f53b290274` |

Empreintes de contrôle du code gelé, lues à l'instant de finir : les douze fichiers de la section 11 ont exactement les empreintes du bloc (`sha256sum` contre bloc, aucune différence).

## Annexe 3 — déclaration des lectures du contre-lecteur (pour L12)

Toutes sous graines < 2⁶⁴, hors graine décisive, hors de ce préenregistrement. Heures de Paris, 1er novembre 2026.

- Essais : `python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v58_nul_v8.py` (depuis `orchestrator/`), joués deux fois : 35 réussis, 51 sous-essais réussis, 29,7 s la dernière fois. Graines des essais : celles du fichier (20261101, 3, 5, `graine_derivee(20261101, …)`), comme L4 et L5.
- Banc de mutations : `python3 -I -B essais/mutations_v58.py --raisons` : « mutations : 34 ; tuées pour la raison attendue : 34 ; tuées pour une autre raison : 0 ; défaut du banc : 0 ; survivantes : 0 ; non appliquées : 0 » ; témoin avant et après restauration : 20 essais, 0 échec ; code de sortie 0. Comptes des nuls mutés recoupant L5 : T02 16/20, T03b 2/20, T04 19/20, T05s 12/20.
- Rejeu de L8 avec le banc gelé : `python3 -I -B demonstrations/banc_tricheurs_v8.py <dossier neuf hors dépôt> --graine 7 --repetitions 20 --processus 2` ; 18 lignes, identique à L8 valeur pour valeur (promotions, log W max, médianes, 99ᵉ centiles, membres dominants) ; durée 63,2 s ; T12a : log W max +2,448 (le plus proche du seuil 2,996 de toutes les lignes) ; T05s −0,038, T09g −0,033.
- Rejeu de L6 : `python3 -I -B v58_verif_bornes.py` (entropie 41, 10 répétitions par ligne fatale) : mêmes maxima que L6 (classe linéaire : −1,0·10⁻⁵ au plus, T12a −1,084 ; 0 promotion).
- Vérification de la démonstration de la couche 1 : 352 fiches comparées entre v7 et v8, aucune différence de log W max.
- Aucune course du banc avec ce préenregistrement (`--preenregistrement` jamais utilisé), aucun fichier du dépôt écrit.
