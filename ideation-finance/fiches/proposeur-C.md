# Fiches du proposeur C — les modèles de langage comme objet ou instrument de recherche économique

Conventions communes aux cinq fiches (pour ne pas les répéter) :

- **T_c** = date de coupure des connaissances du modèle utilisé, telle que publiée par son éditeur (à relever et à citer dans le
  dépôt ; je ne l'affirme pour aucun modèle : « à vérifier »). **Fenêtre propre** = observations datées d'au moins 3 mois après T_c.
  L'étudiant choisit un modèle avec T_c ≤ juin 2025, ce qui laisse environ 12 mois de fenêtre propre (octobre 2025 à septembre ou
  octobre 2026 selon la série).
- **Sonde de récitation** (garde commune) : on demande au modèle, sans lui fournir de données, la valeur des séries cibles pour des
  mois de la fenêtre propre. Si son erreur n'est pas pire que celle d'une marche aléatoire arrêtée à T_c, la fenêtre est déclarée
  contaminée et reculée de 3 mois.
- **Prix supposé des appels** : 3 USD par million de jetons en entrée, 15 USD par million en sortie (hypothèse à vérifier chez
  l'éditeur ; un modèle plus petit divise ces coûts).
- **Tests d'accès** : tous faits avec curl depuis cette machine le 2026-11-12, avec l'agent utilisateur par défaut de curl.
  Je n'ai lu que les en-têtes et les dernières dates des fichiers, aucun résultat de test.
- Références : « titre vérifié sur arXiv » signifie que l'API d'arXiv a renvoyé ce titre et ces auteurs le 2026-11-12 ; je n'ai
  pas relu le contenu. Tout le reste vient de ma mémoire et porte « à vérifier ».

---

### C1 — Ménages synthétiques et prix de l'essence : une expérience par vignettes

- **Question** : des ménages simulés par un modèle de langage révisent-ils leur anticipation d'inflation à un an, après une hausse
  du prix de l'essence, avec la même ampleur que les ménages de l'enquête du Michigan ?
- **Hypothèse falsifiable** : la révision des ménages synthétiques est positive, propre à l'essence (plus forte que pour un prix
  placebo hors panier), et du même ordre que l'élasticité observée dans l'enquête, avec une tendance à l'exagérer (rapport
  synthétique / réel supérieur à 1).
- **Prédiction chiffrée** : élasticité réelle b_réel ≈ +0,02 point d'anticipation pour +1 % de prix de l'essence dans le mois
  (plage 0,01 à 0,04) ; élasticité synthétique nette (essence moins placebo) entre +0,02 et +0,06 ; rapport R = b_synth / b_réel
  entre 1 et 3, valeur centrale 2. Écart d'anticipation « revenu < 50 k$ » moins « revenu > 100 k$ » positif chez les synthétiques,
  entre +0,5 et +2 points, contre environ +0,5 point dans l'enquête de la Fed de New York (ordre de grandeur de mémoire, à calculer).
- **Test de mort** : calculé par un code séparé sur les fichiers bruts. L'idée meurt si l'un des trois cas se produit :
  (a) l'intervalle de confiance à 95 % de (b_essence − b_placebo), erreurs groupées par répondant synthétique, contient 0 ou est
  négatif ; (b) R estimé sort de [1/3 ; 3] ; (c) l'écart par revenu chez les synthétiques est de signe opposé à l'écart moyen de
  l'enquête de la Fed de New York sur juin 2013 – T_c. Échantillon : 400 répondants synthétiques × 3 vignettes ; régression réelle
  sur 1990-10 à T_c (environ 415 mois).
- **Données** :
  - Anticipation médiane à un an, Michigan : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=MICH` → **200** (1978-01 à 2026-09).
  - Même série à la source : `https://www.sca.isr.umich.edu/files/tbmpx1px5.csv` → **200** (colonnes Month, YYYY, PX_MD, PX5_MD ; jusqu'à octobre 2026).
  - Prix de l'essence ordinaire, mensuel : `...fredgraph.csv?id=GASREGM` → **200** (1990-09 à 2026-10). Indice des prix : `...id=CPIAUCSL` → **200**.
  - Enquête de la Fed de New York, anticipations par âge, diplôme, revenu, région :
    `https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-data.xlsx` → **200** (1,27 Mo ; feuille
    « Inflation expectations Demo », 2013-06 à 2026-10).
  - Tableaux démographiques du Michigan (`https://data.sca.isr.umich.edu/data-archive/mine.php`) → **200** mais c'est un formulaire :
    non retenu, la ventilation vient de la Fed de New York.
- **Méthode** : (1) Régression réelle : ΔMICH_t sur 100·Δln(GASREGM_t) et la variation retardée de l'inflation sur 12 mois, MCO,
  erreurs de Newey-West. (2) Expérience : 400 personas tirés dans 54 cellules (âge × diplôme × revenu × sexe) répondent à la question
  de l'enquête sur un scénario de base, puis à trois vignettes où l'on tire au hasard une dose (−20 % à +30 %) pour l'essence,
  l'alimentation et un bien hors panier (placebo qui mesure la complaisance du modèle envers tout chiffre qu'on lui montre).
  (3) MCO de la révision sur les trois doses avec effet fixe de répondant ; comparaison de b_essence − b_placebo avec b_réel par
  bootstrap. (4) En complément descriptif : les mêmes personas reçoivent les vraies conditions de chaque mois de la fenêtre propre.
  **Garde contre la connaissance du futur** : les vignettes sont fictives, sans année ni niveau de prix réel, donc aucune valeur
  mémorisée ne peut y répondre ; le complément (4) ne porte que sur des mois postérieurs à T_c + 3 mois.
- **Ce qui serait nouveau** : les travaux que je connais comparent des niveaux moyens d'anticipations simulées à ceux des enquêtes ;
  ici on compare une **réponse causale** (dose-réponse randomisée) à une élasticité observée, avec un bras placebo pour l'effet de
  complaisance. Travaux proches : Horton, Filippas et Manning, « Large Language Models as Simulated Economic Agents », arXiv
  2301.07543 (titre vérifié sur arXiv) ; Bybee, « Surveying Generative AI's Economic Expectations », arXiv 2305.02823 (titre vérifié
  sur arXiv) ; Iadisernia et Camassa, « Prompting for Policy: Forecasting Macroeconomic Scenarios with Synthetic LLM Personas »,
  arXiv 2511.02458 (titre vérifié sur arXiv) ; Coibion et Gorodnichenko (2015) sur le pétrole et les anticipations des ménages
  (à vérifier) ; Binder (2018), « Inflation expectations and the price at the pump » (à vérifier) ; D'Acunto, Malmendier, Ospina
  et Weber sur les prix d'épicerie (à vérifier) ; une étude expérimentale de Zarifhonarvar sur les anticipations d'inflation de
  modèles de langage (référence incertaine).
- **Rôle de l'IA** : un agent écrit le générateur de vignettes et lance les appels ; un second agent écrit la régression réelle
  sans voir les réponses synthétiques. L'humain fixe les doses, les cellules, la bande [1/3 ; 3] et le texte exact de la question.
  Garde : prédiction et seuils scellés (sha256) avant tout appel ; le verdict sort d'un script figé qui lit les réponses brutes et
  les CSV ; l'agent qui a produit les réponses n'a ni les séries réelles ni le script de verdict.
- **Coût et durée** : 400 bases + 1 200 vignettes + 1 400 appels « conditions réelles » (100 personas × 14 mois) = **3 000 appels**
  d'environ 500 jetons en entrée et 60 en sortie, soit environ 1,5 M de jetons en entrée et 0,2 M en sortie : **≈ 8 USD**.
  Calcul négligeable. 4 semaines.
- **Risques** : la régression réelle est observationnelle (l'essence bouge avec d'autres nouvelles) alors que la vignette est
  « toutes choses égales » : les deux élasticités ne mesurent pas exactement le même objet. Le modèle a lu la littérature et peut
  réciter le fait stylisé plutôt que le simuler. Le résultat peut dépendre fortement de la formulation du prompt (à mesurer avec
  deux formulations figées d'avance).
- **Valeur si l'hypothèse meurt** : une mesure propre de l'écart entre répondants synthétiques et réels sur une réponse causale,
  avec l'effet de complaisance chiffré par le placebo ; c'est une mise en garde utilisable contre le remplacement d'enquêtes par
  des simulations.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai mesuré, par une expérience randomisée sur 400 répondants
  simulés, la réaction des anticipations d'inflation au prix de l'essence et je l'ai comparée à l'élasticité estimée sur l'enquête
  du Michigan. » Graphique : courbes dose-réponse (essence, alimentation, placebo) avec, superposée, la droite de l'élasticité
  réelle et son intervalle. Métiers : recherche économique en banque centrale, études macroéconomiques, conseil économique.

---

### C2 — Le ton des communiqués du FOMC, lu avec et sans date

- **Question** : le ton du communiqué du FOMC, noté par un modèle de langage, explique-t-il la variation du taux à 2 ans le jour de
  l'annonce au-delà de la décision de taux, et cette relation tient-elle quand le modèle ne peut pas connaître la suite ?
- **Hypothèse falsifiable** : un communiqué noté plus restrictif que le précédent s'accompagne d'une hausse du taux à 2 ans le
  jour même, à décision de taux donnée ; la note tirée du texte anonymisé ne prédit pas la dérive des 20 jours suivants, alors que
  la note tirée du texte daté la prédit davantage (fuite d'information future).
- **Prédiction chiffrée** : un point de ton (échelle −2 à +2) ↔ +2 à +5 points de base sur le 2 ans le jour J, gain de R² de 0,05
  à 0,15 par rapport à la seule décision. Régression placebo sur la dérive de J+1 à J+20 : coefficient du bras anonymisé entre
  −2 et +2 pb avec |t| < 2 ; coefficient du bras daté supérieur de 0 à 5 pb à celui du bras anonymisé avant T_c, et écart nul
  (|t| < 2) après T_c.
- **Test de mort** : sur le bras anonymisé, environ 220 communiqués (mai 1999 – octobre 2026) : l'idée meurt si le t de Student
  robuste du coefficient de ton est < 2 ; ou si, dans la régression placebo (dérive J+1 à J+20), le coefficient du bras anonymisé a
  |t| > 2 (la mesure est alors contaminée ou capte autre chose que l'annonce) ; ou si, sur les réunions de la fenêtre propre
  (environ 9, d'octobre 2025 à octobre 2026), le coefficient est de signe opposé à celui d'avant T_c (rapporté avec sa valeur p de
  permutation exacte).
- **Données** :
  - Communiqués récents : `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` → **200** (liens jusqu'à
    `monetary20261028a.htm`) ; exemple `https://www.federalreserve.gov/newsevents/pressreleases/monetary20240131a.htm` → **200** ;
    `.../monetary20261028a.htm` → **200**.
  - Communiqués anciens : `https://www.federalreserve.gov/monetarypolicy/fomchistorical2015.htm` → **200** ;
    `.../fomchistorical2003.htm` → **200** ; exemple ancien `https://www.federalreserve.gov/boarddocs/press/monetary/2003/20030129/default.htm` → **200**.
  - Taux à 2 ans quotidien : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2` → **200** (jusqu'au 2026-11-09).
  - Cible des fonds fédéraux : `...id=DFEDTAR` → **200** (1982 – 2008-12-15) ; `...id=DFEDTARU` → **200** ; `...id=DFEDTARL` → **200**.
  - Attention : FRED a renvoyé une erreur HTTP/2 (code 000) quand curl se présentait avec un agent utilisateur de navigateur ;
    avec l'agent par défaut, 200.
- **Méthode** : étude d'événement quotidienne. Pour chaque réunion, le modèle reçoit le communiqué et le précédent et rend une
  note entière de −2 à +2, trois fois (pour mesurer son bruit). Deux bras : texte daté ; texte anonymisé par un script déterministe
  (dates, noms, niveaux de taux et chiffres remplacés par des marques, la décision réduite à « inchangé / hausse / baisse »).
  MCO : ΔDGS2_J = a + b·Ton + c·ΔCible + d·ΔDGS2_{J−1} + e, erreurs robustes. Régression placebo : même membre de droite, variable
  expliquée = DGS2_{J+20} − DGS2_J. **Garde contre la connaissance du futur** : (i) bras anonymisé, avec un test de datation (on
  demande au modèle l'année du texte anonymisé ; on rapporte l'erreur absolue médiane) ; (ii) régression placebo sur la dérive
  future, qui doit être nulle ; (iii) sous-échantillon postérieur à T_c + 3 mois.
- **Ce qui serait nouveau** : le ton des communiqués noté par un modèle a déjà été étudié ; ce qui manque, à ma connaissance, est
  une **mesure chiffrée de la fuite d'information future** dans ce cadre monétaire, par l'écart daté − anonymisé d'une régression
  placebo. Travaux proches : Hansen et Kazinnik, « Can ChatGPT Decipher Fedspeak? » (à vérifier) ; Peskoff, Visokay, Schulhoff et
  Wachspress, « GPT Deciphering Fedspeak », arXiv 2407.19110 (titre vérifié sur arXiv) ; Glasserman et Lin, « Assessing Look-Ahead
  Bias in Stock Return Predictions Generated By GPT Sentiment Analysis », arXiv 2309.17322 (titre vérifié sur arXiv) ; Sarkar et
  Vafa, « Lookahead bias in pretrained language models » (à vérifier) ; Gürkaynak, Sack et Swanson (2005) sur les deux facteurs
  des annonces (à vérifier) ; Lucca et Trebbi (2009) sur la mesure automatique des communiqués (à vérifier).
- **Rôle de l'IA** : un agent collecte et anonymise les textes ; un autre lance la notation ; aucun des deux ne lit les séries de
  taux. L'humain fixe l'échelle, la fenêtre de 20 jours, les contrôles et les seuils. Garde : notes scellées (sha256) avant le
  téléchargement de DGS2 ; régressions et verdict par un script figé d'avance, exécuté par un rôle distinct.
- **Coût et durée** : 220 communiqués × 2 bras × 3 répétitions = 1 320 appels + 220 appels de datation = **1 540 appels**
  d'environ 2 500 jetons en entrée (deux communiqués) et 30 en sortie : ≈ 3,9 M de jetons en entrée, soit **≈ 12 à 13 USD**.
  5 semaines (la collecte des pages anciennes prend une semaine).
- **Risques** : données quotidiennes seulement (pas de fenêtre de 30 minutes, pas de contrats à terme sur fonds fédéraux gratuits),
  donc la surprise de taux est mal contrôlée et d'autres nouvelles du jour polluent ; les communiqués sont reconnaissables à leurs
  formules même anonymisés (le test de datation le dira) ; 9 réunions propres ne donnent qu'une vérification de signe.
- **Valeur si l'hypothèse meurt** : si le ton n'explique rien au-delà de la décision en données quotidiennes, c'est une borne
  utile sur ce qu'on peut tirer du texte sans données intrajournalières ; si le placebo échoue, on a une mesure directe de la
  contamination des études de ce type.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai mesuré l'effet du ton des communiqués du FOMC sur le taux à
  2 ans sur environ 220 réunions, et chiffré par une régression placebo la part due à la connaissance du futur par le modèle. »
  Graphique : quatre coefficients avec intervalles (jour J et dérive J+1…J+20, texte daté et anonymisé), avant et après T_c.
  Métiers : stratégie taux, recherche en banque centrale, gestion obligataire, recherche quantitative macro.

---

### C3 — Contexte ou mémoire ? Prévoir l'inflation à un mois avec des chiffres nommés ou anonymes

- **Question** : dire à un modèle « voici l'inflation de tel pays à telle date » améliore-t-il sa prévision à un mois par rapport
  aux mêmes chiffres rendus anonymes, et quelle part de ce gain disparaît après sa date de coupure ?
- **Hypothèse falsifiable** : le gain de précision apporté par le contexte (nom du pays, variable, dates) est nettement plus fort
  avant la date de coupure qu'après : l'essentiel du gain mesuré en rétro-test est de la mémoire, et la valeur du contexte en
  conditions propres est proche de zéro.
- **Prédiction chiffrée** : avant T_c, l'erreur quadratique moyenne du bras nommé est inférieure de 15 à 40 % à celle du bras
  anonyme ; après T_c + 3 mois, l'écart est compris entre −5 % et +10 %. Coefficient de différence de différences δ > 0,
  représentant au moins 70 % du gain d'avant coupure. En fenêtre propre, le bras nommé ne bat pas un AR(1) : |statistique de
  Diebold-Mariano| < 1,96.
- **Test de mort** : deux modèles dont les dates de coupure diffèrent d'au moins 9 mois ; 11 pays × 36 mois × 2 bras × 2 modèles.
  On régresse d = (perte anonyme − perte nommée) sur un effet fixe de modèle, un effet fixe de mois et l'indicatrice « mois
  antérieur à la coupure de ce modèle ». L'idée meurt si δ ≤ 0 ou si sa valeur p unilatérale (bootstrap sauvage groupé par mois)
  est ≥ 0,05. Condition de validité écrite d'avance : la perte du bras anonyme rapportée à celle de l'AR(1) doit rester stable à
  ± 25 % entre les périodes, sinon le verdict est « non concluant » et non « confirmé ».
- **Données** :
  - Indices des prix harmonisés mensuels par pays, sur FRED : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=CP0000DEM086NEST`
    → **200** (1996-01 à 2026-09) ; mêmes séries pour FR, IT, ES, NL, AT, BE, FI, IE, PT, GR (`CP0000<PAYS>M086NEST`) → **200**
    chacune, toutes jusqu'à 2026-09.
  - Source d'origine, en secours : `https://data-api.ecb.europa.eu/service/data/ICP/M.DE+FR+IT.N.000000.4.ANR?startPeriod=2025-01&format=csvdata`
    → **200** une fois, puis délai dépassé (code 000) sur la même requête avec `startPeriod=2026-01` : source instable ce jour-là,
    donc non retenue comme source principale.
  - Millésimes en temps réel (robustesse) : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=UNRATE&vintage_date=2025-03-07`
    → **200** (colonne `UNRATE_20250307`). Le paramètre `vintage_date` de `fredgraph.csv` est en revanche ignoré (200, mais données
    courantes).
- **Méthode** : cible = glissement annuel de l'indice, prévu à un mois à partir des 24 mois précédents. Bras nommé : pays, variable,
  dates, valeurs vraies. Bras anonyme : « série A, mois 1 à 24 », valeurs décalées d'une constante tirée au hasard, prévision
  ramenée ensuite à l'échelle. Références : marche aléatoire et AR(1) à fenêtre croissante. Différence de différences modèle × période
  avec effets fixes de mois (les mois situés entre les deux coupures sont « avant » pour un modèle et « après » pour l'autre),
  erreurs groupées par mois. Graphique en temps d'événement autour de chaque coupure. **Garde contre la connaissance du futur** :
  c'est l'objet même du plan : l'écart nommé − anonyme n'est interprété comme valeur économique que sur les mois postérieurs à
  T_c + 3 mois ; la sonde de récitation vérifie la fenêtre ; le second modèle sert de placebo (la cassure doit se déplacer avec la
  date de coupure et non rester à une date de calendrier).
- **Ce qui serait nouveau** : plusieurs travaux affirment qu'un modèle prévoit l'inflation aussi bien ou mieux que les
  prévisionnistes, d'autres montrent que les modèles récitent le passé ; je ne connais pas de plan qui **sépare la valeur du
  contexte économique de la mémoire** par un croisement nommé/anonyme × avant/après coupure sur un panel de pays. Travaux proches :
  Faria-e-Castro et Leibovici, « Artificial Intelligence and Inflation Forecasts » (à vérifier) ; Lopez-Lira, Tang et Zhu, « The
  Memorization Problem: Can We Trust LLMs' Economic Forecasts? », arXiv 2504.14765 (titre vérifié sur arXiv) ; He, Lv, Manela et
  Wu, « Chronologically Consistent Large Language Models », arXiv 2502.21206 (titre vérifié sur arXiv) ; Faust et Wright (2013),
  « Forecasting inflation » (à vérifier) ; Atkeson et Ohanian (2001) pour la marche aléatoire comme référence (à vérifier).
- **Rôle de l'IA** : un agent construit les invites des deux bras et lance les appels ; un autre code l'AR(1) et le script de
  verdict. L'humain choisit les deux modèles, relève leurs dates de coupure, fixe les fenêtres et la condition de validité. Garde :
  les prévisions sont écrites dans un fichier scellé (sha256) avant que le script de verdict ne lise les valeurs réalisées ;
  l'agent prévisionniste ne reçoit jamais les mois cibles.
- **Coût et durée** : 11 × 36 × 2 × 2 = **1 584 appels** de prévision + 792 appels de sonde de récitation = **2 376 appels**
  d'environ 500 jetons en entrée et 40 en sortie : ≈ 1,2 M de jetons en entrée, soit **≈ 5 USD**. Calcul négligeable. 4 semaines.
- **Risques** : si le modèle ne mémorise pas l'inflation mensuelle de petits pays, δ sera faible même si le problème existe
  ailleurs ; 36 mois ne font que 36 grappes ; la période d'avant coupure peut être plus agitée que celle d'après, d'où la condition
  de validité et le second modèle ; sans économie dans la question, la fiche tomberait dans le simple banc d'essai : l'accent doit
  rester sur « que vaut le contexte pour prévoir l'inflation ».
- **Valeur si l'hypothèse meurt** : si δ ≈ 0, les rétro-tests d'inflation par modèle de langage sont moins contaminés qu'on le
  craint sur ce type de données, ce qui est publiable ; si le contexte aide encore après coupure, on a une estimation propre de
  la valeur du jugement économique à un mois.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai séparé, sur 11 pays de la zone euro et deux modèles, ce qui
  relève de la mémoire et ce qui relève de l'information économique dans les prévisions d'inflation à un mois d'un modèle de
  langage. » Graphique : gain du bras nommé sur le bras anonyme, mois par mois, en temps relatif à la date de coupure, une courbe
  par modèle. Métiers : recherche quantitative (tout métier qui fait des rétro-tests), prévision macroéconomique, banque centrale.

---

### C4 — Les a priori d'un modèle sur l'exposition des industries au pétrole, aux taux et au dollar

- **Question** : l'exposition des 49 industries américaines aux chocs de pétrole, de taux longs et de dollar est-elle connaissable
  a priori, par raisonnement économique écrit avant de voir les rendements ?
- **Hypothèse falsifiable** : les bêtas annoncés par le modèle, scellés avant lecture des données, classent correctement les
  industries selon leurs bêtas réalisés après la date de coupure (corrélation de rang positive), mais n'ajoutent rien à un bêta
  historique estimé sur cinq ans.
- **Prédiction chiffrée** : corrélation de Spearman entre a priori et bêtas réalisés en fenêtre propre : pétrole 0,4 à 0,7 ; taux
  à 10 ans 0,2 à 0,5 ; dollar 0,0 à 0,3. Bêta historique sur 5 ans : 0,6 à 0,8 pour le pétrole. Corrélation partielle de l'a
  priori une fois le bêta historique pris en compte : inférieure à 0,2. En revanche, contracter un bêta estimé sur 60 jours vers
  l'a priori du modèle réduit l'erreur quadratique de 5 à 20 % par rapport à une contraction vers zéro.
- **Test de mort** : fenêtre propre = jours de bourse de T_c + 3 mois au 2026-09-30 (au moins 240 jours). L'idée meurt si la
  valeur p de permutation (10 000 permutations des étiquettes d'industrie) du Spearman est ≥ 0,05 pour le pétrole (seuil d'environ
  0,24 avec 49 industries) **et** pour la mesure empilée des trois chocs. Seconde branche, jugée séparément : la contraction vers
  l'a priori meurt si elle ne réduit pas l'erreur quadratique face à la contraction vers zéro (valeur p ≥ 0,05, bootstrap par
  blocs de jours). Un plafond de bruit (corrélation entre bêtas réalisés des jours pairs et impairs) est rapporté à côté.
- **Données** :
  - 49 industries, rendements quotidiens : `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/49_Industry_Portfolios_daily_CSV.zip`
    → **200** (4,2 Mo ; « created using the 202609 CRSP database » ; dernière ligne 20260930).
  - Facteur de marché et taux sans risque quotidiens : `.../ftp/F-F_Research_Data_Factors_daily_CSV.zip` → **200** (jusqu'au 20260930).
  - Pétrole WTI quotidien : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO` → **200** (jusqu'au 2026-11-03).
  - Taux à 10 ans : `...id=DGS10` → **200** (jusqu'au 2026-11-09). Indice large du dollar : `...id=DTWEXBGS` → **200** (2006-01-02 au 2026-11-06).
- **Méthode** : (1) Le modèle donne, pour chaque industrie et chaque choc (pétrole +1 %, taux à 10 ans +10 pb, dollar +1 %), la
  réaction attendue du rendement en excès du marché, en points de base, avec une phrase de justification ; cinq passages avec
  l'ordre des industries mélangé, moyenne par industrie. (2) Scellement. (3) Bêtas réalisés par MCO quotidien du rendement en excès
  sur le marché et les trois chocs, en fenêtre propre. (4) Spearman avec test de permutation ; régression transversale du bêta
  réalisé sur le bêta historique et l'a priori ; comparaison de trois contractions d'un bêta de 60 jours (vers zéro, vers
  l'historique, vers l'a priori). **Garde contre la connaissance du futur** : aucune donnée n'est fournie au modèle ; les bêtas
  réalisés ne sont estimés que sur des rendements postérieurs à T_c + 3 mois ; en placebo, on compare le Spearman obtenu sur les
  cinq années d'avant coupure à celui de la fenêtre propre : l'écart mesure ce qui relève du souvenir de l'historique.
- **Ce qui serait nouveau** : on sait que les bêtas d'industrie estimés sont bruités et instables et qu'on les contracte vers une
  cible statistique ; utiliser comme cible un **a priori économique écrit et scellé**, puis le juger sur une période que le modèle
  n'a pas pu lire, est à ma connaissance peu fait. Travaux proches : Fama et French (1997), « Industry costs of equity »
  (à vérifier) ; Vasicek (1973) sur la contraction bayésienne des bêtas (à vérifier) ; Ludwig et Mullainathan, « Machine learning
  as a tool for hypothesis generation » (à vérifier) ; pour l'élicitation d'a priori par modèle de langage en finance : référence
  incertaine.
- **Rôle de l'IA** : le modèle joue le rôle de générateur d'hypothèses (147 signes et grandeurs) ; un agent distinct écrit
  l'estimation des bêtas et le verdict. L'humain choisit les trois chocs, la fenêtre de 60 jours et les seuils. Garde : le fichier
  des a priori est scellé (sha256) avant tout téléchargement de rendements postérieurs à T_c ; la règle statistique est écrite hors
  du modèle et exécutée par un rôle qui n'a pas produit les a priori.
- **Coût et durée** : 3 chocs × 5 passages × 7 lots de 7 industries = 105 appels, plus 45 appels de reformulation de contrôle :
  **150 appels** d'environ 800 jetons en entrée et 400 en sortie, soit **≈ 1,5 USD**. Calcul : quelques secondes. 4 semaines.
- **Risques** : 12 mois de fenêtre propre donnent des bêtas réalisés bruités pour les industries peu exposées (d'où le plafond de
  bruit) ; un Spearman positif pour le pétrole peut paraître évident (les pétrolières aiment le pétrole cher) : l'intérêt repose
  alors sur les taux, le dollar et la branche « contraction » ; les trois chocs sont corrélés entre eux certains jours.
- **Valeur si l'hypothèse meurt** : si l'a priori ne classe rien, c'est un résultat net sur les limites du « raisonnement
  économique » d'un modèle face à une statistique simple ; si seule la contraction échoue, on documente que l'historique sur 5 ans
  suffit, ce qui intéresse un constructeur de modèles de risque.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai fait écrire et sceller par un modèle de langage 147 hypothèses
  d'exposition sectorielle au pétrole, aux taux et au dollar, puis je les ai jugées sur des rendements postérieurs à sa date de
  coupure. » Graphique : nuage des 49 industries, bêta pétrole annoncé en abscisse, bêta réalisé en ordonnée, noms des industries
  affichés. Métiers : modèles de risque et gestion d'actifs, recherche quantitative actions, stratégie sectorielle en banque
  d'investissement.

---

### C5 — Livre beige : le texte régional dit-il quelque chose que l'emploi passé ne dit pas ?

- **Question** : le ton du rapport de chaque district de la Réserve fédérale dans le Livre beige prédit-il la croissance de
  l'emploi de ce district sur les trois mois suivants, une fois retirés la conjoncture nationale, le niveau moyen du district et
  l'emploi passé ?
- **Hypothèse falsifiable** : à date donnée, les districts dont le rapport est noté plus favorable connaissent ensuite une
  croissance de l'emploi plus forte que les autres (coefficient positif), y compris quand le texte est anonymisé et sur les
  rapports postérieurs à la date de coupure.
- **Prédiction chiffrée** : un point de ton (échelle −2 à +2) ↔ +0,05 à +0,15 point de croissance de l'emploi sur trois mois (non
  annualisée) par rapport aux autres districts à la même date ; gain de R² intra-groupe ≤ 0,02 ; écart entre bras daté et bras
  anonymisé inférieur à 30 % du coefficient.
- **Test de mort** : bras anonymisé, 12 districts × environ 150 rapports (2008 – mi-2026), soit environ 1 800 observations. L'idée
  meurt si le coefficient de ton est ≤ 0 ou si sa valeur p est ≥ 0,05 selon un test de permutation qui réattribue les notes entre
  districts **à l'intérieur de chaque date** (5 000 tirages) ; ou si, sur les rapports de la fenêtre propre (environ 6 livraisons
  dont la cible à trois mois est déjà publiée, soit environ 72 observations), le coefficient est négatif avec un intervalle à 95 %
  qui exclut l'estimation d'avant coupure.
- **Données** :
  - Rapports par district, archive de la Fed de Minneapolis, adresse régulière `https://www.minneapolisfed.org/beige-book-reports/<AAAA>/<AAAA>-<MM>-<code>` :
    `.../1985/1985-03-ch` → **200** ; `.../2024/2024-10-at` → **200** ; `.../2026/2026-10-at` → **200** ; les dix autres codes
    (bo, cl, da, kc, mi, ny, ph, ri, sf, sl) testés sur 2015-06 → **200** chacun ; synthèse nationale `.../2024/2024-10-su` → **200**.
  - Mêmes textes à la source : `https://www.federalreserve.gov/monetarypolicy/beigebook202410.htm` → **200** ;
    `.../beigebook202410-atlanta.htm` (lien présent dans la page) ; `.../beigebook202610-atlanta.htm` → **200** ; liste
    `https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm` → **200** ; archive
    `.../beige-book-archive.htm` → **200**. (Une adresse devinée, `beigebook202609.htm`, a rendu 404 : il n'y a pas de livraison ce mois-là.)
  - Emploi salarié non agricole par État, mensuel : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=CANA` → **200** (1990-01 à
    2026-09) ; `...id=TXNA` → **200**. Chômage par État : `...id=CAUR` → **200**. Les 48 autres États suivent le même schéma de nom
    (`<ÉTAT>NA`), non testés un par un.
  - Millésimes pour les contrôles en temps réel : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=CANA&vintage_date=2024-06-30` → **200**.
- **Méthode** : panel district × livraison. Le modèle note de −2 à +2 l'emploi et l'activité décrits par chaque rapport. Emploi du
  district = somme des États rattachés à titre principal (table de correspondance fixée d'avance). Régression :
  croissance_{d, t→t+3} = α_d + γ_t + β·Ton_{d,t} + deux retards de croissance + ε, effets fixes de district et de date, inférence
  par permutation intra-date et, en contrôle, erreurs groupées par date. Bras anonymisé (noms de district, de villes, d'États,
  d'entreprises et dates masqués par un script) sur tout l'échantillon ; bras daté sur un quart tiré au hasard, pour mesurer
  l'écart. **Garde contre la connaissance du futur** : (i) les effets fixes de date absorbent tout ce que le modèle sait de la
  conjoncture nationale future ; l'identification ne vient que des écarts entre districts à la même date ; (ii) anonymisation ;
  (iii) sous-échantillon postérieur à T_c + 3 mois ; (iv) écart daté − anonymisé rapporté comme mesure de fuite.
- **Ce qui serait nouveau** : les travaux que je connais relient le Livre beige à l'activité nationale ou notent le texte par
  dictionnaire ; ici l'identification est **intra-date, entre districts**, avec un test propre de fuite d'information et une
  fenêtre postérieure à la coupure. Travaux proches : Balke et Petersen (2002), « How well does the Beige Book reflect economic
  activity? » (à vérifier) ; Armesto, Hernández-Murillo, Owyang et Piger (2009) sur le contenu informatif du Livre beige
  (à vérifier) ; Shi et Hollifield, « Predictive Power of LLMs in Financial Markets », arXiv 2411.16569 (titre vérifié sur arXiv,
  ressorti d'une recherche « Beige Book », contenu non relu) ; notes récentes de la Réserve fédérale utilisant des modèles de
  langage sur le Livre beige : référence incertaine.
- **Rôle de l'IA** : un agent collecte et anonymise les rapports, un autre lance la notation, un troisième construit le panel
  d'emploi sans voir les notes. L'humain fixe la table États → districts, l'horizon de trois mois, l'échelle et les seuils. Garde :
  notes scellées (sha256) avant la construction de la variable expliquée ; régression et permutation dans un script figé d'avance,
  exécuté par un rôle qui n'a pas noté les textes.
- **Coût et durée** : 1 800 appels (bras anonymisé) + 450 appels (bras daté) = **2 250 appels** d'environ 2 300 jetons en entrée
  et 40 en sortie : ≈ 5,2 M de jetons en entrée, soit **≈ 17 USD**. Calcul : moins d'une minute. 6 semaines (collecte et table de
  correspondance : deux semaines).
- **Risques** : les districts ne suivent pas les frontières des États (la Pennsylvanie, par exemple, est partagée), d'où une
  erreur de mesure qui tire le coefficient vers zéro ; l'emploi par État est révisé chaque année, donc les retards utilisés en
  contrôle doivent venir des millésimes d'ALFRED ; le ton peut ne résumer que l'emploi déjà publié ; 12 districts donnent peu de
  variation transversale par date.
- **Valeur si l'hypothèse meurt** : un résultat nul bien identifié dit que l'information qualitative régionale n'ajoute rien aux
  chiffres d'emploi à trois mois, ce qui nuance l'usage courant du Livre beige ; le jeu de notes district × date, publié, reste
  réutilisable.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai construit un panel de 12 districts sur 18 ans à partir du
  texte du Livre beige noté par un modèle de langage et testé, avec effets fixes de date et de district, s'il prédit l'emploi
  régional à trois mois. » Graphique : nuage par classes de la croissance résiduelle de l'emploi contre le ton résiduel, en deux
  couleurs (avant et après la date de coupure). Métiers : recherche économique et banque centrale, études régionales, conseil
  économique, recherche macro en gestion d'actifs.

---

## Sources testées et écartées (pour mémoire)

- `https://www.sec.gov/Archives/edgar/full-index/2026/QTR3/form.idx` → **403** (« Undeclared Automated Tool ») et
  `https://www.sec.gov/files/dera/data/financial-statement-data-sets/2026q2.zip` → **403** : le texte des dépôts d'entreprises
  n'est pas joignable d'ici sans déclarer une adresse de contact. En revanche `https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json`
  → 200 et `https://data.sec.gov/api/xbrl/frames/us-gaap/Revenues/USD/CY2026Q2.json` → 200 (chiffres seulement). Une fiche sur le
  texte des rapports d'entreprise a donc été abandonnée au profit de C5.
- `.../survey-of-professional-forecasters/historical-data/individual_cpi.xlsx` (Fed de Philadelphie) → 200 mais le corps est une
  page HTML, pas un classeur : adresse devinée fausse. Fonctionnent : `.../historical-data/medianlevel.xlsx` → 200 (feuilles CPI,
  UNEMP, etc., jusqu'à 2026 T3), `.../historical-data/dispersion_1.xlsx` → 200, `.../data-files/files/median_cpi_level.xlsx` → 200.
  Aucune fiche n'en dépend.
- API de la BCE : `.../service/data/SPF/Q.U2.HICP.POINT.P12M.Q.AVG?...` → délai dépassé (000) ; `.../service/data/HICP/...` → 503 ;
  `.../service/dataflow/ECB/SPF` → 200 après plus d'une minute. Trop instable ce jour pour porter une fiche.
- Conférences de presse de la BCE : page d'index `https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/html/index.en.html`
  → 200, mais l'adresse d'un communiqué que j'avais devinée → 404 ; les liens sont chargés dynamiquement. Non utilisé.
