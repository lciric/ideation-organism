"""Course d'idéation de l'organisme : lanceur, **version 2** (orchestrateur v51 ; la version 1, `demonstrations/ideation_v1.py`,
est celle de l'orchestrateur v50, gardée telle quelle, R12). Ce qui change (contre-lecture CL15) : le cœur et l'étage sont
`pole/ideation_v2.py` et `pole/tests_de_mort_v2.py` ; `--memoire-bac-non-bornee-permise` (CL15-02 : lève, sur demande
expresse dite au manifeste, la borne mémoire du bac entier par groupe de contrôle ; défaut : bornée, étage refusé si
impossible) ; `--modele-commande-externe` **refusé** avec le moteur réel, s'il diffère de `gemini-4-argon`, tant que
`--commande-externe-lit-modele` n'atteste pas une commande qui lit le modèle demandé (CL15-05 : la commande d'Argon v2 demande
toujours `gemini-4-argon`) ; et le premier appel réel d'Argon fixe `--modele-servi-externe-permis` avec Lazar (le format réel
de `modelVersion` n'est pas connu : un identifiant servi hors liste est refusé **après** l'appel payé, R-764). Sans
`--tests-de-mort`, les sorties sont celles du lanceur v1 octet pour octet.

Course d'idéation de l'organisme (v7, version 47) : lanceur.

Deux moteurs :
- `--moteur simule` (sans dépense) : des proposeurs scriptés rendent des fiches au gabarit tirées d'un petit catalogue, des
  juges scriptés notent par une règle fixe qui respecte le critère des témoins — répétition de la plomberie, du scellement et
  de la lecture ; ce n'est pas l'idéation ; les coûts sont **fictifs** (marqués au manifeste, jamais comptés comme réels) ;
- `--moteur claude-sdk --url-relais http://127.0.0.1:PORT --confirmer-moteur-reel` (dépense, chez session-depot, sous un
  GO cité) : vrais agents (Opus 5.5 et Fable 5.1 seuls), **aucun outil intégré** (`tools=[]` du kit, soit `--tools ''`) ;
  v47 (R-764, barrière 3) : le relais de clé est lancé avec `--modeles-permis` égal **exactement** aux modèles des
  proposeurs et des juges (`claude-opus-5-5,claude-fable-5-1` aux réglages du devis), le lanceur le vérifie à l'état du
  relais avant tout contrôle ; v49 (contre-lecture CL13) : cette liste comprend aussi, avec `--tests-de-mort`, le modèle de
  l'expérimentateur Claude et celui du lecteur, et avec le moteur réel la commande externe doit rendre `modele_servi`
  (R-764 pour Argon : absent ou différent du modèle demandé = refus = arrêt),
  deux tours au plus, borne de temps par session, bac à sable exigé, clé tenue par le relais du noyau avec son propre
  plafond ; **appel de contrôle de bout en bout par modèle avant la course** (CL31-01), compté au journal ; toute session en
  erreur arrête la course et le lanceur rend un code ≠ 0.

Usage (course) :
  python -I -B demonstrations/ideation_v2.py SORTIE_NEUVE --liste-blanche LISTE.json --question Q.md --piece P1.md …
      --temoins TEMOINS.json [--piece-juge A1.md …] [--materiau M.md … --seconde-passe]
      [--proposeur opus=claude-opus-5-5] [--proposeur fable=claude-fable-5-1]
      [--juge juge-fable=claude-fable-5-1] [--juge juge-opus=claude-opus-5-5]
      [--proposeur-externe argon=gemini-argon --commande-externe "…" [--variable-transmise NOM] …]
      [--juge-externe argon=gemini-argon] [--attestation-materiau ATT.json]
      [--budget proposeur_ideation|claude-fable-5-1=10] … [--budget-total-usd 40] [--budget-externe-usd 9]
      [--nombre 8] [--graine 20261028] [--moteur simule|claude-sdk] [--url-relais URL] [--confirmer-moteur-reel]
      [--horodatage "date -u"] [--racine-depot CHEMIN] [--delai-session-s 3600] [--delai-commande-s 1800]
      [--taille-max-pieces 750000]                                                  # défauts : devis v7 quinquies
      [--tolerer-somme-plafonds-claude] [--tolerer-somme-plafonds-externe] [--taille-max-consigne-externe N]

v36 (décisions de Lazar du 28 octobre, 21:05 et 21:20 UTC ; messages n° 117 à 119 de session-depot) :
- **Argon propose à égalité** (`--proposeur-externe`, joué dans la course par `--commande-externe`, qui reçoit la question
  et les pièces sur l'entrée standard) ; sa seconde passe exige `--attestation-materiau` (lecture humaine attestée,
  scellée, du matériau de seconde passe), sinon la course refuse avant tout appel ;
- **Argon juge à poids égal** (`--juge-externe`), **toujours différé** : la course n'appelle jamais le juge externe, écrit
  sa consigne en attente scellée **et n'écrit aucun classement** ; après l'attestation de lecture humaine
  (`{"lecteur", "lu_le", "fiches_validees_sha256", "consignes_en_attente_sha256": {etiquette: …}}`, scellée), le bras joue
  Argon (appel de contrôle, plafond externe séparé) puis écrit le classement **à trois juges** (médiane par critère) :
  python -I -B demonstrations/ideation_v2.py SORTIE --bras-rapporte-differe --attestation-lecture-humaine ATTEST.json \
      --juge-externe argon=gemini-argon --commande-externe "…" [--variable-transmise NOM]
- plafonds : `--budget-total-usd` (Claude, contrôles compris) et `--budget-externe-usd` (Argon, proposeur et juge), séparés.
`--attestation-lecture-humaine` hors du bras, `--commande-externe` sans proposeur externe ni bras, un bras sans commande sur
une course réelle, `--delai-session-s` ≤ 0 : refusés.
Codes de sortie : 0 lisible (ou course écrite, en attente du bras) ; 2 arrêt (session en erreur, pièce refusée, appel de
contrôle, réglage refusé, toute exception — y compris « bras non joué » et « tentative de contrôle scellée ») ; 4 témoins
échoués chez un juge (classement écrit, marqué illisible ; aucune « retenue » imprimée) ; 5 juge externe sans réponse,
ou (v42) tentative du bras scellée non relançable (classement à deux juges écrit, marqué « sans juge externe, illisible
au sens du devis »).
v41 (relecture CL7) : toute tentative de contrôle qui a coûté (contrôle refusé, contrôle interrompu — compté au plafond de
sa session —, ou refus du cœur après les contrôles) est scellée dans `SORTIE-controle/tentative-N.json` ; son champ
`relancable` est **calculé** : moins de trois tentatives ET, coûts déjà imputés compris, somme des plafonds Claude ≤ total
Claude, somme externe ≤ total externe, relais suffisant. Aux réglages du devis v7 quinquies (somme Claude 40,0 exactement),
il est **faux dès qu'un contrôle Claude a coûté** : la relance exige alors un mot de Lazar. Le lanceur l'imprime.
v42 (contre-lecture CL8) : le contrôle d'Argon est joué **avant** les contrôles Claude (une panne d'Argon ne coûte rien
chez Claude) ; **garde de taille sans dépense** avant tout contrôle : la consigne de contrôle d'Argon (sa plus grosse
consigne) au-delà de `--taille-max-consigne-externe` (défaut : `--budget-controle-externe-usd` / prix prudent d'un
caractère, `idn.PRIX_CARACTERE_PRUDENT_USD`, soit 1 000 000 caractères pour 2,5) → refus scellé dans
`SORTIE-controle/refus-taille-K.json`, rien payé ; au bras, même garde sur la consigne du juge (défaut : plafond du juge /
même prix), contrôle **court**, `--budget-externe-usd` transmis s'il est donné ; `relancable` écrit l'hypothèse « relais
gardé » et calcule aussi « relais relancé à neuf » ; SORTIE sans manifeste de départ → `relancable` faux.
v43 (contre-lecture CL9) : garde de la course par défaut = plus petit plafond des sessions d'Argon qui reçoivent sa plus
grosse consigne — contrôle (`--budget-controle-externe-usd`, entrée seule) et passe (`proposeur_ideation|<Argon>`, 2,5 par
défaut, moins la provision de sortie : `--nombre` fiches de 12 000 caractères au rapport sortie/entrée 5) : **520 000
caractères** aux réglages du devis, et toujours 520 000 si seul le contrôle est relevé ; chaque passe d'Argon est aussi
gardée par le cœur avant son envoi. Au bras : `--taille-max-consigne-externe-bras` (défaut : plafond du juge / prix
prudent moins une provision de sortie de 2 000 caractères de note par fiche servie au rapport 5 : 880 000 pour 3,5 et 52
fiches) ; `--taille-max-consigne-externe` ne vaut que pour la course ; un
refus de taille au bras compte une tentative non relançable et écrit le classement sans bras (code 5). L'échec d'un
classement de repli est dit (sortie d'erreur, `classement-sans-bras-impossible-N.json`). Sans dépense :
  python -I -B demonstrations/ideation_v2.py --mesurer-consignes --liste-blanche … --question … --piece … [--materiau …
      --seconde-passe] [--temoins …] [--piece-juge …] [--proposeur-externe …] [--juge-externe …] [--nombre N]
écrit (sortie standard) les tailles réelles des consignes de contrôle, de passe 2 maximale et de juge, et les gardes qui
s'y appliqueraient ; aucun appel, aucun fichier, code 0.
v43, décisions de Lazar relayées par session-depot : CL42-04 « retirer » — plus de borne de taille de la fiche entière, la
marge du contrôle d'Argon redevient `--nombre` fiches au pire cas des bornes par champ (`fiche_maximale()`, 44 259
caractères) ; la garde prend `--prix-entree-usd-par-million-jetons` (défaut 10,0, barème prudent du code ; 4 caractères
par jeton). CL40-01 option (c) — à la relance après une tentative scellée, les contrôles **réussis** (même rôle, même
modèle, même consigne, même commande ou même moteur et relais) ne sont pas rejoués : ils sont repris (`controles_repris`
au manifeste de départ et au journal : tentative, empreinte du fichier, empreinte de la consigne), seuls les contrôles
échoués ou non faits sont (re)payés, et `relancable` compte les seuls contrôles à refaire.
v44 (contre-lecture CL10) : `--budget-passe-2-externe-usd` — plafond propre à la seconde passe d'Argon (défaut : le
plafond de sa passe 1, `proposeur_ideation|<Argon>`, 2,5 par défaut), compté dans la somme externe (contrôle + passe 1 +
passe 2 + juge + contrôle du bras) ; chaque passe d'Argon est gardée contre son propre plafond moins une provision de
sortie (`idn.garde_passe_externe`), même avec `--taille-max-consigne-externe` (la plus petite des deux), la passe 1 avant
tout contrôle ; à la relance, un contrôle Claude réussi n'est repris que si la dépense lue au relais n'a pas baissé depuis
(sinon le relais a été relancé : rejoué) ; la relance reste bornée par les sommes **et** par `idn.MAX_TENTATIVES_BRAS`
(3) tentatives de contrôle.

v46 (tour (c) « outils clôturés », décisions de Lazar du 29 octobre, R-433 à R-448 ; **en préparation : jamais lancé en
réel avec ces options**) : `--dossier-ferme DOSSIER` — dossier aux fichiers listés dans un `index.json` scellé (et dans la
liste blanche), empreintes vérifiées avant tout appel ; la consigne des proposeurs porte l'index, pas le texte
(`--taille-max-pieces` ne s'y applique pas) ; proposeurs Claude à outils de lecture du kit (`Read`, `Grep`, `Glob` sur une
copie vérifiée), ou par protocole avec `--outils-par-protocole` (comme Argon : demandes `{"demandes": [...]}` servies au tour
suivant) ; juges sans outil ; aucun nombre de tours fixé : plafond en dollars de la session, `--delai-session-s` (délai de
l'ensemble des tours d'une passe par protocole, et de chaque session du kit), `--max-demandes-lecture` (défaut 1 000 ;
franchi : incident, arrêt) ; avertissement de budget à 80 % ; mesures de lecture au manifeste de fin ; citations vérifiées
servies aux juges. Sans `--dossier-ferme`, la ligne de commande et les entrées de la v45 restent valides, inchangées.

v47 (moissonneur, option (A) retenue par Lazar le 29 octobre 2026, 11:52 heure de Paris ; **en préparation : aucune moisson
réelle ici, la première est un GO séparé chez session-depot**) : `--moisson frais|rejeu|aucune` (défaut `aucune` : course de
la v46, consignes identiques octet pour octet) ; un tour de moisson par proposeur entre les passes (`--seconde-passe`
obligatoire), session à part sous `--budget-moisson-usd-par-session` (0,5), `--tours-moisson` (1, borné à 2) ; sources
arXiv et OpenAlex (métadonnées et résumés), servies par le noyau, seul client du relais de moisson
(`pole/relais_moisson.py`, processus à part sur la boucle locale) ; `--url-relais-moisson URL` (frais ; avec le moteur réel :
obligatoire, plus `--confirmer-moisson-reelle`) — avec le moteur simulé, sans adresse, un **relais factice en mémoire**
est lancé sur la boucle locale (aucun réseau) ; `--cache-moisson DOSSIER` (rejeu : `noyau/moisson` d'une course passée,
jamais le réseau) ; `--registre-bardeaux FICHIER` (registre scellé d'empreintes de bardeaux des textes de test, garde de
fuite, règle 5). Les juges ne moissonnent jamais ; `--mesurer-consignes --moisson frais` compte la moisson au pire cas.

v48 (étage de tests de mort, décision de Lazar R-776 (a) ; **en préparation : aucun test réel ici, le premier est un GO
séparé**) : `--tests-de-mort N` (défaut 0 : étage absent, course de la v47, consignes et sorties identiques octet pour
octet) joue, après le classement figé, les N premières fiches éligibles : préenregistrement court scellé, expérimentateur
sans outil du kit (`--experimentateur ETIQUETTE=MODELE`, ou `--experimentateur-externe ETIQUETTE=MODELE` pour Argon par
`--commande-externe`, même consigne) dont le noyau exécute les scripts dans un bac à sable (`bwrap`, réseau isolé,
système de fichiers en lecture seule hors d'un dossier de travail par fiche ; refus sans `bwrap`, aucun repli), lecteur
neuf (`--lecteur-test ETIQUETTE=MODELE`) ; la tranche exploratoire (`--tranche-exploratoire DOSSIER`, lecture seule, index
scellé dans la liste blanche) est obligatoire ; quotas `--executions-par-fiche` (3), `--delai-execution-s` (120),
`--memoire-test-mo` (1024), plafonds `--budget-test-usd` (0,5 par fiche) et `--budget-lecteur-test-usd` (0,1 par fiche) ;
`--executeur-tests factice` : démonstration, moteur simulé seulement. Course à juge externe : l'étage se joue après le bras,
avec `--bras-rapporte-differe --tests-de-mort N …` (mêmes réglages, `--liste-blanche` redonnée). Les modèles Claude de
l'étage sont ceux de la course. Résultats : section « tests de mort (exploratoires) » du manifeste de fin (course sans
juge externe) et `manifeste-tests-de-mort.json` ; jamais servis aux juges de la même course.

v50 (contre-lecture CL14, bac à sable et Argon) : `--utilisateur-bac UID|NOM` (utilisateur sans privilège sous lequel `bwrap` est
lancé par `setpriv` ; **obligatoire quand le noyau tourne en superutilisateur**, sinon l'étage est refusé), `--dossier-travail-bac
DOSSIER` (racine des dossiers de travail, hors de la sortie, possédée par cet utilisateur, non inscriptible par d'autres,
traversable par lui ; obligatoire avec `--utilisateur-bac`), `--userns-imbriques-permis` (lève `--disable-userns`, dit au
manifeste ; défaut : interdits) ; avec le moteur réel et `--commande-externe` : `--modele-commande-externe` (étiquette que la
commande d'Argon demande toujours, défaut `gemini-4-argon` ; tout autre rôle externe est refusé avant tout appel),
`--modele-servi-externe-permis DEMANDÉ=SERVI` (identifiants servis permis, liste explicite ; défaut : l'identifiant demandé ou
suivi de `-AAAAMMJJ`), et `--experimentateur-externe` **refusé** tant que `--commande-externe-accepte-experimentateur` n'atteste pas
une commande qui accepte `experimentateur_test` : la commande réelle (`/opt/argon/commande_argon_v2.py`) ne joue que
`proposeur_ideation` et `juge_ideation` (code 2 sinon). Les options du bac et `--commande-externe-accepte-experimentateur` ne
valent qu'avec `--tests-de-mort N`.

La commande externe : consigne sur l'entrée standard, environnement minimal explicite (plus `PLAFOND_SESSION_USD`,
`ROLE_POLE` et `--variable-transmise`, jamais un nom de clé), dernière ligne `{"texte": …, "cout_usd": …}` — coût
**obligatoire, fini, strictement positif** ; sur un échec, le coût imprimé est compté, sinon le plafond de session l'est
(marqué inconnu) ; au délai, tout son groupe de processus est arrêté. En moteur simulé, sans commande, un adaptateur scripté
joue les rôles externes (jamais sur une course réelle).

La liste blanche (`{chemin réel: sha256}`) est écrite par `--construire-liste-blanche FICHIERS…` puis scellée par le devis ;
le noyau refuse toute pièce, question, matériau ou témoin hors liste ou à empreinte différente, tout lien symbolique, et
toute zone interdite (quarantaine, banques, préenregistrements, carte des hypothèses).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole import ideation_v2 as idn  # noqa: E402  (v51 : version 2 du cœur)
from pole import tests_de_mort_v2 as idn_tests  # noqa: E402  (v51 : version 2 de l'étage)
from pole.adaptateurs import Resultat  # noqa: E402
from pole.outils import graine_derivee, horodatage  # noqa: E402

# v37 (CL36-04) : défauts = devis en vigueur (v7 quinquies ; externe : mot de Lazar, 11,6) ; tout est réglable par --budget
BUDGETS_PAR_DEFAUT = {("proposeur_ideation", "claude-opus-5-5"): 5.0, ("proposeur_ideation", "claude-fable-5-1"): 9.3,
                      ("juge_ideation", "claude-opus-5-5"): 4.0, ("juge_ideation", "claude-fable-5-1"): 7.0}
BUDGET_EXTERNE_PROPOSEUR = 2.5
BUDGET_EXTERNE_JUGE = 3.5


class AdaptateurIdeationSimule:
    """Moteur simulé : fiches au gabarit tirées d'un catalogue, notes par règle fixe (les témoins sont reconnus à leur
    nom, comme un juge honnête les reconnaîtrait à leur contenu), « OK » à l'appel de contrôle. Coûts fictifs.
    v47 : au tour de moisson, rend un bloc de demandes (deux requêtes admises, une refusable par la garde) ; en passe 2,
    cite la première notice servie en antériorité MOISSONNE avec son étiquette."""
    nom = "simule-ideation"
    COUT = {"proposeur_ideation": 0.40, "juge_ideation": 0.60, "moisson": 0.05, "experimentateur_test": 0.05,
            "lecteur_test": 0.02}  # v48

    def __init__(self, graine):
        self.graine = graine

    @staticmethod
    def notices_servies(consigne):
        """Les notices de la section « Moisson servie par le noyau » d'une consigne de passe 2 (données entre délimiteurs)."""
        from pole.protocole_outils import DEBUT_DONNEES, FIN_DONNEES
        m = re.search(re.escape(DEBUT_DONNEES) + r"\s*```json\n(.*?)\n```\s*" + re.escape(FIN_DONNEES), consigne, re.S)
        if not m:
            return []
        try:
            tours = json.loads(m.group(1))
        except ValueError:
            return []
        return [r for t in tours for rep in t.get("reponses", []) for r in rep.get("resultats", [])]

    @staticmethod
    def donnees_apres(consigne, debut_titre):
        """v48 : l'objet JSON de la section de données (`section_servie`) dont le titre commence par `debut_titre`, ou None."""
        from pole.protocole_outils import DEBUT_DONNEES, FIN_DONNEES
        m = re.search(r"## " + re.escape(debut_titre) + r"[^\n]*\n.*?" + re.escape(DEBUT_DONNEES) + r"\s*```json\n(.*?)\n```\s*"
                      + re.escape(FIN_DONNEES), consigne, re.S)
        return json.loads(m.group(1)) if m else None

    def tour_experimentateur(self, consigne, rng):
        """v48 : premier tour, un script qui lit la première donnée demandée et imprime `RESULTAT: <nombre>` ; tour suivant
        (l'historique est servi), `fin`."""
        if "Ce que le noyau t'a servi" in consigne:
            return {"fin": "test exécuté, sortie à lire"}
        prereg = self.donnees_apres(consigne, idn_tests.TITRE_SECTION_PREREG)
        chemin = prereg["donnees"][0]["chemin"]
        valeur = round(rng.uniform(0.0, 0.5), 3)
        script = (f"lignes = open('tranche/{chemin}', encoding='utf-8').read().splitlines()\n"
                  f"print('lignes lues :', len(lignes))\nprint('RESULTAT: {valeur}')\n")
        return {"experience": [{"executer": {"script": script}}]}

    def lecture_lecteur(self, consigne):
        """v48 : le lecteur simulé applique le seuil gelé à la dernière ligne `RESULTAT:` de la dernière exécution réussie."""
        prereg = self.donnees_apres(consigne, idn_tests.TITRE_SECTION_PREREG)
        vue = self.donnees_apres(consigne, "Sortie scellée des exécutions")
        reussies = [e for e in vue if e["statut"] == "réussie" and e["lignes_resultat"]]
        if not reussies:
            return "VERDICT: non concluant ; chiffre: aucun ; ligne: aucune"
        ligne = reussies[-1]["lignes_resultat"][-1]
        valeur = float(ligne.split(":", 1)[1].strip().replace(",", "."))
        survit = idn_tests.comparer(valeur, prereg["seuil"]["comparateur"], prereg["seuil"]["valeur"])
        return f"VERDICT: {'survit' if survit else 'éliminée'} ; chiffre: {valeur} ; ligne: {ligne}"

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, racine_lecture=None,
               max_demandes_lecture=None, mode_lecture=None):
        """v46 : les arguments de lecture du dossier fermé sont acceptés et ignorés (aucun outil simulé : le proposeur
        simulé rend ses fiches au premier tour, sans demande). v48 : rôles de l'étage de tests de mort (expérimentateur :
        un script puis `fin` ; lecteur : le seuil gelé appliqué à la sortie) ; avec une tranche servie, les fiches portent
        un `test_de_mort` (une sur quatre environ en est privée : refusée à l'étage)."""
        import random
        rng = random.Random(graine_derivee(self.graine, role, dossier))
        if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):  # v40 (CL39-08) : contrôle à la taille réelle
            return Resultat("OK", [], 0.0, "ok")
        if role == "experimentateur_test":
            return Resultat("```json\n" + json.dumps(self.tour_experimentateur(consigne, rng), ensure_ascii=False) + "\n```", [],
                            self.COUT[role], "ok")
        if role == "lecteur_test":
            return Resultat(self.lecture_lecteur(consigne), [], self.COUT[role], "ok")
        if role == "proposeur_ideation" and consigne.startswith(idn.TITRE_TOUR_MOISSON):  # v47 : tour de moisson
            demandes = [{"source": "arxiv", "requete": "monitor transfer diffuse sabotage probes", "resultats": 3},
                        {"source": "openalex", "requete": "quickest change detection covert adversary", "resultats": 2},
                        {"source": "arxiv", "requete": "voir https://exemple.org/page", "resultats": 5}]  # refusée (adresse)
            return Resultat("```json\n" + json.dumps({"moisson": demandes}, ensure_ascii=False) + "\n```", [], self.COUT["moisson"], "ok")
        if role == "proposeur_ideation":
            n = rng.randint(2, 4)
            notices = self.notices_servies(consigne)
            tranche = re.search(r"## Tranche exploratoire[^\n]*\n.*?```json\n(.*?)\n```", consigne, re.S)  # v48
            chemins_tranche = [e["chemin"] for e in json.loads(tranche.group(1))] if tranche else []
            fiches = [{
                "nom": f"Idée simulée {i + 1}", "type": rng.choice(idn.TYPES_FICHE),
                "enonce": "Énoncé simulé, falsifiable par construction.",
                "loi_predictive": {"espace_instances": "dix familles", "prediction": "effet de 0,2",
                                   "signe": rng.choice(idn.SIGNES), "metrique": "rappel à fausses alertes fixées"},
                "perte_traduction": "aucune, c'est une simulation",
                "questions_servies": [rng.choice(["Q1", "Q2", "Q3", "Q4", "Q-pont", "nouvelle"])],
                "avantage": {"source": rng.choice(idn.SOURCES_AVANTAGE), "texte": "avantage simulé",
                             "incopiable_parce_que": "raison simulée"},
                "originalite": {"niveau": rng.choice(idn.NIVEAUX_ORIGINALITE), "texte": "texte simulé"},
                "demande_organisme": {"nature": rng.choice(idn.NATURES_DEMANDE), "texte": "module simulé"},
                "cout": {"nature": rng.choice(idn.NATURES_COUT), "ordre_de_grandeur": "simulé"},
                "piege": "piège simulé", "cosmetique_si": "si rien ne bouge",
                "anteriorite": [{"reference": "référence simulée", "statut": "SUPPOSE"}]} for i in range(n)]
            if chemins_tranche:  # v48 : un test de mort par fiche, sauf une fiche sur quatre (refusée à l'étage)
                for f in fiches:
                    if rng.random() >= 0.25:
                        f["test_de_mort"] = {"seuil": "au moins 0,25", "test": "part des lignes de la première donnée ; élimine si "
                                             "elle reste sous le seuil", "donnees": [chemins_tranche[0]]}
            if notices:  # v47 : la première notice servie, citée au statut MOISSONNE avec son étiquette telle quelle
                r = notices[0]
                fiches[0]["anteriorite"].append({"reference": f"{r['titre']}, {r['auteurs']}, {r['date'][:4]}, {r['identifiant']} "
                                                              f"{r['etiquette']}", "statut": idn.STATUT_MOISSONNE})
            return Resultat("```json\n" + json.dumps({"fiches": fiches}, ensure_ascii=False) + "\n```", [],
                            self.COUT[role], "ok")
        if role == "juge_ideation":
            bloc = json.loads(re.search(r"```json\n(\[.*\])\n```", consigne, re.S).group(1))
            notes, doublons, par_nom = [], [], {f["nom"]: f["identifiant"] for f in bloc}
            for f in bloc:
                c = {k: rng.randint(1, idn.NOTE_MAX) for k in idn.CRITERES}
                nom = f["nom"].lower()
                if "verbeux" in nom or "occup" in nom:
                    c.update({"avantage": 1, "originalite": 0, "falsifiabilite": 1})
                if "sobre" in nom or "jumeau" in nom:
                    c.update({"avantage": 3, "originalite": 2})
                notes.append({"identifiant": f["identifiant"], "criteres": c,
                              "justifications": {k: "justification simulée" for k in idn.CRITERES}})
            for f in bloc:
                if f["nom"].lower().startswith("jumeau"):
                    cible = next((v for k, v in par_nom.items() if k.lower().startswith("sobre")), None)
                    if cible:
                        doublons.append([f["identifiant"], cible])
            return Resultat("```json\n" + json.dumps({"notes": notes, "doublons": doublons}) + "\n```", [],
                            self.COUT[role], "ok")
        raise ValueError(role)


# v50 (CL14-07) : le modèle que la commande d'Argon (`/opt/argon/commande_argon_v2.py`, option `--modele`, que
# `appel-argon-v3.sh` ne passe pas) demande TOUJOURS ; elle ignore `MODELE_DEMANDE_POLE`. Tout autre modèle donné au noyau pour un
# rôle externe fait arrêter la course au premier appel (modèle servi ≠ modèle demandé) : refusé avant tout appel avec le moteur réel.
MODELE_ARGON_COMMANDE_V2 = "gemini-4-argon"


def paire(texte, defaut_etiquette):
    if "=" in texte:
        etiquette, modele = texte.split("=", 1)
    else:
        etiquette, modele = defaut_etiquette, texte
    return etiquette.strip(), modele.strip()


def lecteur_relais(url):
    """v35 (CL34-09) : ouvreur sans mandataire (`ProxyHandler({})`) — les variables de mandataire de l'environnement ne
    détournent jamais la lecture de l'état du relais local."""
    ouvreur = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def lire():
        with ouvreur.open(url.rstrip("/") + "/relais/etat", timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    return lire


def lire_tentatives_controle(sortie_controle):
    """v40 (CL39-02) : les tentatives de contrôle déjà payées dans `SORTIE-controle` (fichiers scellés `tentative-N.json`),
    dont les coûts s'imputent aux totaux de la course suivante.
    v41 (CL40-05) : chaque fichier est lu **sceau vérifié** (refus s'il est absent ou faux), ses deux coûts doivent être des
    réels finis ≥ 0 ; la numérotation doit être continue (1 … N) et tout dossier de contrôle `tentative-K` doit avoir sa
    tentative scellée — sinon un fichier a été retiré, ou un arrêt brutal (sans gestionnaire) a laissé un contrôle au coût
    inconnu : refus, plus de relance sans un mot de Lazar."""
    from pole.outils import verifier_scelle
    from pole.pari_apparie import _fini
    if not os.path.isdir(sortie_controle):
        return []
    noms = os.listdir(sortie_controle)
    numeros = sorted(int(m.group(1)) for m in (re.match(r"tentative-(\d+)\.json$", n) for n in noms) if m)
    dossiers = sorted(int(m.group(1)) for m in (re.match(r"tentative-(\d+)$", n) for n in noms) if m
                      and os.path.isdir(os.path.join(sortie_controle, m.group(0))))
    compagnons = sorted(int(m.group(1)) for m in (re.match(r"tentative-(\d+)\.json\.sha256$", n) for n in noms) if m)
    if numeros != list(range(1, len(numeros) + 1)) or any(k not in numeros for k in dossiers + compagnons):
        raise idn.CourseInterrompue(f"tentatives de contrôle incohérentes dans {sortie_controle} (fichiers {numeros}, dossiers "
                                    f"{dossiers}, sceaux {compagnons}) : tentative retirée, ou contrôle arrêté sans être scellé "
                                    "(coût inconnu) ; plus de relance sans un mot de Lazar (CL40-05)")
    tentatives = []
    for k in numeros:
        nom = f"tentative-{k}.json"
        chemin = os.path.join(sortie_controle, nom)
        if not verifier_scelle(chemin):
            raise idn.CourseInterrompue(f"tentative de contrôle au sceau absent ou faux : {nom} (CL40-05)")
        with open(chemin, "r", encoding="utf-8") as f:
            r = json.load(f)["reglages"]
        couts = {c: r.get(c) for c in ("cout_claude_usd", "cout_externe_usd")}
        for c, v in couts.items():
            if not _fini(v) or v < 0:
                raise idn.CourseInterrompue(f"tentative de contrôle {nom} : {c} non fini ou négatif ({v!r}) (CL40-05)")
        tentatives.append(dict({"fichier": nom}, **{c: float(v) for c, v in couts.items()}))
    return tentatives


def cle_reprise(role, modele, consigne_sha256, identite):
    """v43 (CL40-01, option c) : clé d'un contrôle — rôle, modèle, empreinte de la consigne de contrôle et identité de ce qui
    le joue (commande externe et empreintes de ses fichiers, ou moteur et adresse du relais) ; un contrôle réussi n'est
    repris que pour la même clé (une commande changée, une consigne changée : rejoué)."""
    return hashlib.sha256(json.dumps({"role": role, "modele": modele, "consigne_sha256": consigne_sha256, "identite": identite},
                                     ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def controle_reussi(lecture):
    """v43 : une lecture de contrôle scellée réussie — statut ok, texte « OK », aucun problème, lancée, avec sa clé."""
    return (isinstance(lecture, dict) and bool(lecture.get("cle_reprise")) and lecture.get("statut") == "ok"
            and not lecture.get("problemes") and not lecture.get("non_lance")
            and str(lecture.get("texte") or "").upper().strip(".!») ") == "OK")


def controles_reussis(sortie_controle, tentatives):
    """v43 (CL40-01, option c) : {clé: reprise} des contrôles réussis scellés dans les tentatives précédentes (déjà lues
    sceau vérifié par `lire_tentatives_controle`) ; la plus récente l'emporte. La reprise porte le numéro de tentative,
    l'empreinte du fichier scellé, l'empreinte de la consigne et le coût déjà imputé par cette tentative."""
    from pole.outils import sha256_fichier
    reussis = {}
    for t in tentatives:
        chemin = os.path.join(sortie_controle, t["fichier"])
        with open(chemin, "r", encoding="utf-8") as f:
            lectures = json.load(f)["reglages"].get("lectures") or {}
        numero = int(re.match(r"tentative-(\d+)\.json$", t["fichier"]).group(1))
        for nom, lec in lectures.items():
            if controle_reussi(lec):
                reussis[lec["cle_reprise"]] = {"controle": nom, "repris_de_tentative": numero, "fichier": t["fichier"],
                                               "sha256_tentative": sha256_fichier(chemin),
                                               "consigne_sha256": lec.get("consigne_sha256"),
                                               # v44 (CL43-03) : dépense lue au relais juste après ce contrôle
                                               "relais_apres_depense_usd": (lec.get("relais_apres") or {}).get("depense_usd"),
                                               "cout_compte_usd_impute_par_cette_tentative": idn.cout_compte_controle(lec),
                                               "cle_reprise": lec["cle_reprise"]}
    return reussis


def filtrer_reprises_claude(repris, lire_relais):
    """v44 (CL43-03) : un contrôle Claude réussi n'est repris que si le relais n'a pas été relancé depuis — la dépense lue
    maintenant au relais n'est pas plus basse que celle lue juste après ce contrôle (`relais_apres_depense_usd`). Relais
    relancé (dépense plus basse), dépense non lue à la tentative, ou relais illisible maintenant : le contrôle est rejoué
    (0,2 au plus, dans les sommes). Sans relais lisible (moteur simulé) : repris, comme en v43. Rend (reprises gardées,
    motifs {contrôle: motif}), motifs écrits au manifeste de départ, au journal du cœur et à la tentative."""
    from pole.pari_apparie import _fini
    claude = [k for k in repris if not k.startswith("externe:")]
    if not claude:
        return dict(repris), {}
    motifs = {}
    if lire_relais is None:
        return dict(repris), {k: "repris : moteur sans relais lisible (simulé)" for k in claude}
    try:
        actuelle = lire_relais().get("depense_usd")
        actuelle = float(actuelle or 0.0) if (actuelle is None or _fini(actuelle)) else None
    except Exception as e:  # noqa: BLE001 — relais illisible : rien n'est repris côté Claude
        actuelle, erreur = None, f"{type(e).__name__} : {str(e)[:120]}"
    else:
        erreur = "dépense non finie"
    gardes = dict(repris)
    for k in claude:
        avant = repris[k].get("relais_apres_depense_usd")
        t = repris[k].get("repris_de_tentative")
        if actuelle is None:
            motifs[k] = f"rejoué : relais illisible maintenant ({erreur})"
        elif avant is None or not _fini(avant):
            motifs[k] = f"rejoué : dépense du relais non lue après ce contrôle à la tentative {t}"
        elif actuelle < float(avant) - 1e-9:
            motifs[k] = (f"rejoué : relais relancé depuis la tentative {t} (dépense lue {actuelle:.4f} < {float(avant):.4f} lue "
                         "juste après ce contrôle)")
        else:
            motifs[k] = f"repris de la tentative {t} : dépense lue {actuelle:.4f} ≥ {float(avant):.4f} (relais non relancé)"
            continue
        del gardes[k]
    return gardes, motifs


def relance_possible(numero, verif, cout_claude, cout_externe, total_claude, total_externe, tolere_claude, tolere_externe,
                     externes, relais=None, budgets=None, juges=None, details=False):
    """v41 (CL40-01, code) : ce que la relance vérifiera, calculé au moment de sceller la tentative `numero` — moins de
    trois tentatives ; somme des plafonds Claude de la relance (celle de cette course, coûts de cette tentative imputés) ≤
    total ; même chose côté externe ; relais (plafond − réserve − dépense, la dépense de cette tentative ajoutée) ≥ total −
    plus petit juge. Rend (relançable, motifs). Ne change pas la politique (aucune marge ajoutée).
    v42 (CL41-05) : `relancable` reste calculé dans l'hypothèse **« relais gardé »** (sa dépense, celle de cette tentative
    comprise, est comptée), écrite dans le motif ; le second calcul **« relais relancé à neuf »** (dépense 0, devis point 4)
    est rendu à côté (`details=True` : troisième élément {relancable, motifs}) et nommé dans le motif s'il diffère."""
    motifs = []
    if numero >= idn.MAX_TENTATIVES_BRAS:  # v44 (CL43-05) : borne gardée, en plus des sommes
        motifs.append(f"{idn.MAX_TENTATIVES_BRAS} tentatives faites (borne MAX_TENTATIVES_BRAS, en plus des sommes)")
    somme_c = verif["somme_claude"] + cout_claude
    if not tolere_claude and somme_c > total_claude + 1e-9:
        motifs.append(f"somme des plafonds Claude de la relance {somme_c:.4f} > total {total_claude}")
    somme_e = verif["somme_externe"] + cout_externe
    if externes and not tolere_externe and somme_e > total_externe + 1e-9:
        motifs.append(f"somme des plafonds externes de la relance {somme_e:.4f} > total externe {total_externe}")
    autres = list(motifs)  # tout sauf le relais : communs aux deux hypothèses
    a_neuf = {"relancable": not autres, "motifs": list(autres), "hypothese": "relais relancé à neuf (dépense 0)"}
    if relais and relais.get("plafond_usd") is not None and relais.get("reserve_par_appel_usd") is not None:
        plus_petit_juge = min(budgets[("juge_ideation", m)] for _, m in juges)
        besoin = total_claude - plus_petit_juge
        neuf = float(relais["plafond_usd"]) - float(relais["reserve_par_appel_usd"])
        reste = neuf - float(relais.get("depense_usd") or 0.0) - cout_claude
        if neuf < besoin - 1e-9:
            a_neuf["motifs"].append(f"relais relancé à neuf : {neuf:.4f} < total {total_claude} − plus petit juge "
                                    f"{plus_petit_juge}")
            a_neuf["relancable"] = False
        if reste < besoin - 1e-9:
            motifs.append(f"relais gardé (hypothèse) : {reste:.4f} restants < total {total_claude} − plus petit juge "
                          f"{plus_petit_juge}" + ("" if a_neuf["motifs"] != autres else
                                                 f" ; relais relancé à neuf (devis, point 4) : {neuf:.4f} ≥ {besoin:.4f}, "
                                                 "la garde du relais accepterait"))
    if details:
        return not motifs, motifs, a_neuf
    return not motifs, motifs


def racine_depot(donnee=None):
    """v35 (CL34-06) : la racine du dépôt, donnée (`--racine-depot`) ou lue par `git rev-parse --show-toplevel` depuis le
    dossier du code ; sinon, cinq niveaux au-dessus du code (arborescence d'envoi), avec son origine consignée."""
    import subprocess
    if donnee:
        return os.path.abspath(donnee), "--racine-depot"
    try:
        r = subprocess.run(["git", "-C", RACINE, "rev-parse", "--show-toplevel"], capture_output=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return os.path.abspath(r.stdout.decode("utf-8").strip()), "git rev-parse --show-toplevel"
    except (OSError, subprocess.SubprocessError):
        pass
    return os.path.abspath(os.path.join(RACINE, *([os.pardir] * 5))), "cinq niveaux au-dessus du code (repli)"


def version_outil_ligne_de_commande(sdk):
    """v35 (CL34-09) : version de l'outil en ligne de commande que le kit lance (`claude --version`), ou « inconnue »."""
    import shutil
    import subprocess
    candidats = []  # CL35-10 : l'outil que le kit lance réellement d'abord (embarqué), PATH en repli
    try:
        from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
        candidats.append(SubprocessCLITransport("", sdk.ClaudeAgentOptions())._find_cli())
    except Exception:  # noqa: BLE001 — la version est une information du manifeste, jamais une condition
        pass
    candidats.append(shutil.which("claude"))
    for c in candidats:
        if c and os.path.exists(c):
            try:
                r = subprocess.run([c, "--version"], capture_output=True, timeout=30)
                if r.returncode == 0:
                    return {"chemin": c, "version": r.stdout.decode("utf-8", "replace").strip()[:80]}
            except (OSError, subprocess.SubprocessError):
                pass
    return {"chemin": None, "version": "inconnue"}


class _Explicite(argparse.Action):
    """v42 (CL41-01) : retient qu'une option a été donnée (le bras ne prend `--budget-externe-usd` que s'il est donné ;
    sinon le plafond relu au manifeste de départ de la course)."""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + "_explicite", True)


def reglages_lecture(args, delai_session):
    """v46 : arguments du tour (c) passés au cœur — vides sans `--dossier-ferme` (course de la v45, inchangée)."""
    if not args.dossier_ferme:
        return {}
    return {"dossier_ferme": args.dossier_ferme, "outils_par_protocole": args.outils_par_protocole,
            "max_demandes_lecture": max_demandes_lecture(args)}


def reglages_moisson(args, url_relais_moisson=None):
    """v47 : arguments de la moisson passés au cœur — vides sans `--moisson` (course de la v46, consignes inchangées)."""
    if args.moisson == "aucune":
        return {}
    return {"moisson": args.moisson, "tours_moisson": args.tours_moisson,
            "budget_moisson_usd_par_session": args.budget_moisson_usd_par_session,
            "url_relais_moisson": url_relais_moisson if args.moisson == "frais" else None,
            "cache_moisson": args.cache_moisson if args.moisson == "rejeu" else None,
            "registre_bardeaux": args.registre_bardeaux}


def reglages_tests_de_mort(args, externe=None):
    """v48 : le dictionnaire `etage_tests` du cœur — None sans `--tests-de-mort` (course de la v47, consignes inchangées)."""
    if not args.tests_de_mort:
        return None
    exp = paire(args.experimentateur, "experimentateur") if args.experimentateur else None
    exp_ext = (*paire(args.experimentateur_externe, "experimentateur-externe"), externe) if args.experimentateur_externe else None
    executeur = (idn_tests.ExecuteurFactice(delai_s=args.delai_execution_s, memoire_mo=args.memoire_test_mo)
                 if args.executeur_tests == "factice" else None)
    memoire_permise = getattr(args, "memoire_bac_non_bornee_permise", False)  # v51 (CL15-02)
    if args.executeur_tests == "bwrap" and (args.utilisateur_bac or args.dossier_travail_bac or args.userns_imbriques_permis
                                            or memoire_permise):
        try:  # v50 : utilisateur dédié, dossier racine du bac, espaces d'utilisateurs imbriqués (défaut : le bac à sable par défaut du cœur)
            executeur = idn_tests.ExecuteurBacASable(delai_s=args.delai_execution_s, memoire_mo=args.memoire_test_mo,
                                                     utilisateur_bac=args.utilisateur_bac, racine_travail=args.dossier_travail_bac,
                                                     userns_imbriques_permis=args.userns_imbriques_permis,
                                                     memoire_bac_non_bornee_permise=memoire_permise)
        except ValueError as e:
            raise idn.CourseInterrompue(f"bac à sable de l'étage : {e}") from e
    return {"nombre": args.tests_de_mort, "tranche": args.tranche_exploratoire, "experimentateur": exp,
            "experimentateur_externe": exp_ext, "lecteur": paire(args.lecteur_test, "lecteur-test") if args.lecteur_test else None,
            "budget_test_usd": args.budget_test_usd, "budget_lecteur_usd": args.budget_lecteur_test_usd,
            "executions_par_fiche": args.executions_par_fiche, "delai_execution_s": args.delai_execution_s,
            "memoire_mo": args.memoire_test_mo, "executeur": executeur}


def construire_analyseur():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("sortie", nargs="?", help="dossier de sortie, absent (jamais écrasé)")
    a.add_argument("--construire-liste-blanche", nargs="+", metavar="FICHIER",
                   help="écrit la liste blanche (chemins réels et empreintes) des fichiers donnés dans SORTIE puis sort")
    a.add_argument("--liste-blanche", help="fichier JSON {chemin réel: sha256} (scellé par le devis)")
    a.add_argument("--question", help="fichier texte de la question posée aux proposeurs (dans la liste blanche)")
    a.add_argument("--piece", action="append", default=[], help="pièce servie aux proposeurs (répétable)")
    a.add_argument("--piece-juge", action="append", default=[], help="pièce d'antériorité servie aux juges (répétable)")
    a.add_argument("--materiau", action="append", default=[], help="matériau servi en seconde passe seulement")
    a.add_argument("--temoins", help="fichier JSON des témoins plantés écrits par un tiers (dans la liste blanche)")
    a.add_argument("--seconde-passe", action="store_true")
    a.add_argument("--proposeur", action="append", default=[], help="etiquette=modele (répétable)")
    a.add_argument("--juge", action="append", default=[], help="etiquette=modele (répétable)")
    a.add_argument("--proposeur-externe", action="append", default=[],
                   help="etiquette=modele d'une autre lignée, joué dans la course par --commande-externe")
    a.add_argument("--juge-externe", action="append", default=[], help="etiquette=modele d'une autre lignée, juge différé")
    a.add_argument("--commande-externe", "--commande-juge-externe", dest="commande_externe",
                   help="commande (shell, découpée) qui joue les rôles externes (consigne sur l'entrée standard)")
    a.add_argument("--variable-transmise", action="append", default=[],
                   help="nom d'une variable d'environnement transmise à la commande externe (jamais un nom de clé)")
    a.add_argument("--attestation-lecture-humaine",
                   help="JSON scellé {lecteur, lu_le, fiches_validees_sha256, consignes_en_attente_sha256} : autorise le bras")
    a.add_argument("--attestation-materiau",
                   help="JSON scellé {lecteur, lu_le, materiau_sha256: {nom: sha256}} : seconde passe d'un proposeur externe")
    a.add_argument("--bras-rapporte-differe", action="store_true",
                   help="joue seulement les juges externes différés d'une course déjà faite (SORTIE existante)")
    a.add_argument("--budget", action="append", default=[], help="role|modele=plafond par session en dollars (répétable)")
    a.add_argument("--nombre", type=int, default=8, help=f"fiches au plus par proposeur et par passe (1 à {idn.MAX_FICHES_ABSOLU})")
    a.add_argument("--max-tours", type=int, default=idn.MAX_TOURS_IDEATION)
    a.add_argument("--budget-total-usd", type=float, default=40.0,
                   help="plafond total côté Claude, contrôles compris (devis v7 quinquies)")
    a.add_argument("--budget-externe-usd", type=float, default=11.6, action=_Explicite,
                   help="plafond total des sessions externes (Argon : contrôle à taille réelle 2,5, deux passes à 2,5, juge 3,5, "
                        "contrôle du bras 0,2 ≈ 11,2 ; mot de Lazar : 11,6 — tout est réglable)")
    a.add_argument("--budget-controle-usd", type=float, default=None,
                   help="plafond de chaque appel de contrôle Claude et du contrôle du bras (course : 0,2 par défaut, devis v7 "
                        "quinquies ; bras : par défaut celui que la course a compté, v41)")
    a.add_argument("--racine-depot", help="racine du dépôt (lecture interdite aux agents) ; défaut : git rev-parse")
    a.add_argument("--delai-session-s", type=float, default=None, help="borne de temps par session réelle (défaut 3600, CL37-08)")
    a.add_argument("--delai-commande-s", type=float, default=1800.0, help="borne de temps de la commande externe (CL37-08)")
    a.add_argument("--budget-controle-externe-usd", type=float, default=2.5,
                   help="plafond de l'appel de contrôle du proposeur externe à la taille réelle de la consigne (CL37-01)")
    a.add_argument("--budget-passe-2-externe-usd", type=float, default=None,
                   help="v44 (CL43-01) : plafond de la seconde passe de chaque proposeur externe (défaut : le plafond de sa "
                        "passe 1, proposeur_ideation|<modèle>) ; avec --proposeur-externe et --seconde-passe seulement")
    a.add_argument("--taille-max-consigne-externe", type=int, default=None,
                   help="v42 (CL41-01), v43 : taille maximale (caractères) de la plus grosse consigne d'Argon dans la course (sa "
                        "consigne de contrôle ; chaque passe aussi) ; au-delà, refus scellé avant tout appel, rien payé (défaut : "
                        "plus petit plafond des sessions qui la reçoivent / prix prudent d'un caractère, provision de sortie "
                        "déduite pour la passe) ; course seulement")
    a.add_argument("--taille-max-consigne-externe-bras", type=int, default=None,
                   help="v43 (CL42-05) : taille maximale (caractères) de la consigne du juge externe au bras (défaut : plafond "
                        "du juge / prix prudent − provision de sortie) ; un refus compte une tentative non relançable")
    a.add_argument("--prix-entree-usd-par-million-jetons", type=float, default=10.0,
                   help="v43 (CL42-04 b) : prix d'entrée retenu par les gardes de taille, en dollars par million de jetons (4 "
                        "caractères par jeton ; sortie au rapport 5) ; défaut 10,0, le barème prudent du code")
    a.add_argument("--mesurer-consignes", action="store_true",
                   help="v43 (CL42-03) : écrit les tailles réelles des consignes (contrôle, passe 2 maximale, juge) et les gardes, "
                        "sans aucun appel ni fichier, puis sort 0")
    a.add_argument("--tolerer-somme-plafonds", action="store_true",
                   help="ancienne option : vaut les deux suivantes (consigné au manifeste)")
    a.add_argument("--tolerer-somme-plafonds-claude", action="store_true",
                   help="accepte une somme des plafonds Claude au-dessus du total Claude (CL37-03, v41 ; sinon refus)")
    a.add_argument("--tolerer-somme-plafonds-externe", action="store_true",
                   help="accepte une somme des plafonds externes au-dessus du total externe (CL37-03, v41 ; sinon refus)")
    a.add_argument("--taille-max-pieces", type=int, default=750_000,
                   help=f"caractères servis au plus par lot de pièces (défaut : devis v7 quinquies ; plafond dur {idn.TAILLE_MAX_PIECES_ABSOLUE})")
    a.add_argument("--graine", type=int, default=20261028)
    a.add_argument("--moteur", choices=("simule", "claude-sdk"), default="simule")
    a.add_argument("--url-relais")
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--accepter-sans-bac-a-sable", action="store_true")
    a.add_argument("--motif-sans-bac-a-sable", default="")
    a.add_argument("--horodatage", help="heure UTC lue sur `date -u`")
    a.add_argument("--dossier-ferme", default=None,
                   help="v46 (tour (c)) : dossier fermé (fichiers listés dans un index.json scellé et dans la liste blanche) ; "
                        "proposeurs Claude à outils de lecture du kit, Argon par protocole ; juges sans outil")
    a.add_argument("--outils-par-protocole", action="store_true",
                   help="v46 : avec --dossier-ferme, les proposeurs Claude lisent aussi par protocole, sans outil du kit "
                        "(égalité stricte avec Argon)")
    a.add_argument("--max-demandes-lecture", type=int, default=None,
                   help="v46 : garde-fou anti-boucle par session de proposeur (défaut 1000) ; franchi : incident, arrêt de "
                        "la session ; avec --dossier-ferme seulement")
    a.add_argument("--moisson", choices=idn.MODES_MOISSON, default="aucune",
                   help="v47 : tour de moisson entre les passes (arXiv, OpenAlex ; métadonnées et résumés) — frais : relais "
                        "de moisson interrogé, cache écrit ; rejeu : cache d'une course passée, jamais le réseau ; aucune "
                        "(défaut) : course de la v46, consignes inchangées. Exige --seconde-passe")
    a.add_argument("--url-relais-moisson", default=None,
                   help="v47 : adresse locale du relais de moisson (--moisson frais) ; avec le moteur simulé, sans adresse, un "
                        "relais factice en mémoire est lancé")
    a.add_argument("--cache-moisson", default=None, help="v47 : dossier noyau/moisson d'une course passée (--moisson rejeu)")
    a.add_argument("--budget-moisson-usd-par-session", type=float, default=idn.BUDGET_MOISSON_USD_PAR_SESSION_DEFAUT,
                   help="v47 : plafond de chaque tour de moisson (session à part ; défaut 0,5, SUPPOSÉ)")
    a.add_argument("--tours-moisson", type=int, default=idn.TOURS_MOISSON_DEFAUT,
                   help=f"v47 : tours de moisson par proposeur (défaut 1, borné à {idn.TOURS_MOISSON_MAX})")
    a.add_argument("--registre-bardeaux", default=None,
                   help="v47 : registre scellé d'empreintes de bardeaux des textes de test (garde de fuite, règle 5)")
    a.add_argument("--confirmer-moisson-reelle", action="store_true",
                   help="v47 : avec --moteur claude-sdk --moisson frais seulement (première moisson réelle : GO séparé)")
    # v48 : étage de tests de mort (R-776 a) ; défaut 0 = étage absent (course de la v47)
    a.add_argument("--tests-de-mort", type=int, default=0, metavar="N",
                   help=f"v48 : après le classement figé, test de mort exploratoire des N premières fiches éligibles (0 à "
                        f"{idn_tests.NOMBRE_MAX}) ; 0 (défaut) : étage absent, course de la v47. Exige --tranche-exploratoire, "
                        "--lecteur-test et --experimentateur ou --experimentateur-externe")
    a.add_argument("--tranche-exploratoire", default=None,
                   help="v48 : dossier de la tranche exploratoire (lecture seule ; index.json scellé et dans la liste blanche, "
                        "empreintes vérifiées avant tout appel ; jamais donnees/)")
    a.add_argument("--experimentateur", default=None, metavar="ETIQUETTE=MODELE",
                   help="v48 : expérimentateur Claude (sans outil du kit ; ses scripts sont exécutés par le noyau) ; "
                        "le modèle est celui d'un proposeur ou d'un juge de la course")
    a.add_argument("--experimentateur-externe", default=None, metavar="ETIQUETTE=MODELE",
                   help="v48 : expérimentateur d'une autre lignée (Argon), même consigne, par --commande-externe")
    a.add_argument("--lecteur-test", default=None, metavar="ETIQUETTE=MODELE",
                   help="v48 : lecteur neuf (session sans outil), d'une autre étiquette que l'expérimentateur ; modèle de la course")
    a.add_argument("--budget-test-usd", type=float, default=idn_tests.BUDGET_TEST_USD_DEFAUT,
                   help="v48 : plafond de l'expérimentateur par fiche (défaut 0,5, SUPPOSÉ)")
    a.add_argument("--budget-lecteur-test-usd", type=float, default=idn_tests.BUDGET_LECTEUR_USD_DEFAUT,
                   help="v48 : plafond du lecteur par fiche (défaut 0,1, SUPPOSÉ)")
    a.add_argument("--executions-par-fiche", type=int, default=idn_tests.EXECUTIONS_PAR_FICHE_DEFAUT,
                   help="v48 : exécutions de script par fiche, une demande refusée comptant (défaut 3)")
    a.add_argument("--delai-execution-s", type=float, default=idn_tests.DELAI_EXECUTION_S_DEFAUT,
                   help="v48 : délai d'une exécution, au-delà le groupe de processus est tué (défaut 120)")
    a.add_argument("--memoire-test-mo", type=int, default=idn_tests.MEMOIRE_MO_DEFAUT,
                   help="v48 : mémoire d'une exécution en mégaoctets (défaut 1024)")
    a.add_argument("--executeur-tests", choices=("bwrap", "factice"), default="bwrap",
                   help="v48 : bac à sable des exécutions — bwrap (défaut) ; factice : démonstration, moteur simulé seulement "
                        "(aucune barrière)")
    a.add_argument("--utilisateur-bac", default=None, metavar="UID|NOM",
                   help="v50 (CL14-01) : utilisateur dédié, sans aucun privilège de l'hôte, sous lequel `bwrap` est lancé "
                        "(setpriv --reuid --regid --clear-groups --no-new-privs). OBLIGATOIRE quand le noyau tourne en "
                        "superutilisateur (sinon l'étage est refusé) ; réservé à l'étage, jamais partagé avec un autre processus")
    a.add_argument("--dossier-travail-bac", default=None, metavar="DOSSIER",
                   help="v50 (CL14-01, CL14-04) : dossier racine (chemin absolu) où l'étage crée les dossiers de travail des scripts, "
                        "hors de la sortie, retirés après chaque exécution. Avec --utilisateur-bac : obligatoire, possédé par lui, "
                        "non inscriptible par le groupe ni les autres, traversable par lui (parents compris)")
    a.add_argument("--userns-imbriques-permis", action="store_true",
                   help="v50 (CL14-03) : demande EXPLICITE de ne pas passer --disable-userns à bwrap (bwrap < 0.8.0 ou installé setuid) ; "
                        "dit au manifeste ; par défaut, les espaces d'utilisateurs imbriqués sont interdits et la sonde l'éprouve")
    a.add_argument("--modele-servi-externe-permis", action="append", default=[], metavar="DEMANDÉ=SERVI",
                   help="v50 (CL14-08) : identifiant servi admis en plus de l'identifiant demandé et de son suffixe de date strict "
                        "(-AAAAMMJJ), pour un rôle externe (liste explicite, répétable), par exemple gemini-4-argon=models/gemini-4-argon")
    a.add_argument("--modele-commande-externe", default=None, metavar="MODÈLE",
                   help=f"v50 (CL14-07) : le modèle que la commande externe demande toujours (défaut {MODELE_ARGON_COMMANDE_V2}, celui de "
                        "commande_argon_v2.py) ; avec le moteur réel, tout rôle externe doit porter ce modèle")
    a.add_argument("--memoire-bac-non-bornee-permise", action="store_true",
                   help="v51 (CL15-02) : demande EXPLICITE de ne pas borner la mémoire du bac entier par un groupe de contrôle (aucun "
                        "groupe « memory » utilisable) ; dit au manifeste ; par défaut, la borne est posée et la sonde l'éprouve")
    a.add_argument("--commande-externe-lit-modele", action="store_true",
                   help="v51 (CL15-05) : atteste que la commande externe lit le modèle demandé (--modele ou MODELE_DEMANDE_POLE ; la "
                        "commande d'Argon v2 ne le lit pas) ; exigé avec le moteur réel pour un --modele-commande-externe autre que "
                        f"{MODELE_ARGON_COMMANDE_V2}")
    a.add_argument("--commande-externe-accepte-experimentateur", action="store_true",
                   help="v50 (CL14-07) : atteste que la commande externe accepte le rôle experimentateur_test (la commande d'Argon v2 ne "
                        "l'accepte pas) ; exigé avec le moteur réel et --experimentateur-externe")
    return a


def adaptateur_commande_externe(args):
    """v49 (CL13-05, R-764 pour Argon) : l'adaptateur de la commande externe de la course. Avec le moteur réel
    (`claude-sdk`), la commande **doit** rendre `modele_servi` (égal au modèle demandé, ou suivi d'un suffixe de date) :
    absent ou différent = refus = arrêt ; avec le moteur simulé (essais), la barrière n'agit que si la commande le rend."""
    import shlex
    from pole.adaptateurs import AdaptateurCommandeExterne
    permis = {}
    for texte in getattr(args, "modele_servi_externe_permis", None) or []:  # v50 (CL14-08) : DEMANDÉ=SERVI, liste explicite
        if "=" not in texte:
            raise idn.CourseInterrompue(f"--modele-servi-externe-permis : DEMANDÉ=SERVI attendu (reçu {texte!r})")
        demande, servi = (x.strip() for x in texte.split("=", 1))
        permis.setdefault(demande, []).append(servi)
    return AdaptateurCommandeExterne(shlex.split(args.commande_externe), delai_s=args.delai_commande_s,
                                     variables_transmises=tuple(args.variable_transmise),
                                     exiger_modele_servi=(args.moteur == "claude-sdk"), modeles_servis_permis=permis)


def verifier_commande_externe_reelle(args, prop_ext, juges_ext):
    """v50 (CL14-07) : avec le moteur réel, refusé **avant tout appel** (`CourseInterrompue`) : (a) un rôle externe dont le modèle
    donné au noyau n'est pas celui que la commande demande toujours (`--modele-commande-externe`, défaut
    `MODELE_ARGON_COMMANDE_V2`) : la course s'arrêterait au premier appel d'Argon ; (b) `--experimentateur-externe` : la commande
    réelle (v2) ne joue que `proposeur_ideation` et `juge_ideation` et refuse `experimentateur_test` (code 2) : l'étage
    s'arrêterait au premier tour ; il faut une commande qui l'accepte (nouveau nom, R12), attestée par
    `--commande-externe-accepte-experimentateur`."""
    if args.moteur != "claude-sdk" or not args.commande_externe:
        return
    declare = getattr(args, "modele_commande_externe", None)
    if declare and declare != MODELE_ARGON_COMMANDE_V2 and not getattr(args, "commande_externe_lit_modele", False):
        raise idn.CourseInterrompue(  # v51 (CL15-05) : l'option était déclarative ; la commande v2 demande toujours gemini-4-argon
            f"--modele-commande-externe {declare!r} refusé : la commande d'Argon v2 demande toujours {MODELE_ARGON_COMMANDE_V2!r} "
            "(elle ne lit ni --modele ni MODELE_DEMANDE_POLE) ; tout rôle externe déclaré sous une autre étiquette échouerait au "
            "premier appel, payé (CL15-05). Il faut une commande qui lit le modèle demandé (v3, nouveau nom, R12), attestée par "
            "--commande-externe-lit-modele")
    attendu = declare or MODELE_ARGON_COMMANDE_V2
    modeles = [m for _, m in prop_ext + juges_ext]
    if getattr(args, "experimentateur_externe", None):
        modeles.append(paire(args.experimentateur_externe, "experimentateur-externe")[1])
    ecarts = sorted({m for m in modeles if m != attendu})
    if ecarts:
        raise idn.CourseInterrompue(
            f"modèle(s) externe(s) {ecarts} ≠ {attendu!r}, le modèle que la commande externe demande toujours (la commande d'Argon v2 "
            "ignore MODELE_DEMANDE_POLE et n'a pas reçu --modele) : la course s'arrêterait au premier appel d'Argon (modèle servi ≠ "
            "demandé) ; refusé avant tout appel. Donner l'étiquette exacte, ou --modele-commande-externe si la commande en demande un autre")
    if getattr(args, "experimentateur_externe", None) and not getattr(args, "commande_externe_accepte_experimentateur", False):
        raise idn.CourseInterrompue(
            "--experimentateur-externe NON FONCTIONNEL avec la commande réelle d'Argon (/opt/argon/commande_argon_v2.py : "
            "ROLES = (proposeur_ideation, juge_ideation) ; tout autre ROLE_POLE, dont experimentateur_test, est refusé avec le code 2) : "
            "l'étage s'arrêterait au premier tour de l'expérimentateur ; refusé avant tout appel. Il faut une commande d'Argon qui "
            "accepte experimentateur_test (nouveau nom, R12, côté session-depot), attestée par --commande-externe-accepte-experimentateur ; "
            "en attendant, --experimentateur (Claude)")


def modeles_du_relais(args, proposeurs, juges):
    """v49 (CL13-07, R-764 barrière 3) : les modèles Claude que le relais doit permettre, exactement — proposeurs et juges de
    la course et, quand l'étage de tests de mort est demandé, le modèle de l'expérimentateur (s'il est Claude ; Argon n'est
    pas servi par le relais) et celui du lecteur. Un modèle en plus serait une voie de repli ; un en moins ferait refuser la
    session de l'étage (403) : le LISEZMOI de la v48 le disait, le code de la v48 ne le faisait pas."""
    modeles = [m for _, m in proposeurs + juges]
    if getattr(args, "tests_de_mort", 0):
        if getattr(args, "experimentateur", None):
            modeles.append(paire(args.experimentateur, "experimentateur")[1])
        if getattr(args, "lecteur_test", None):
            modeles.append(paire(args.lecteur_test, "lecteur-test")[1])
    return modeles


def verifier_relais(etat_relais, budget_total_usd, budgets, juges, modeles_attendus=None):
    """v38 (CL37-03) et v40 (CL39-03) : le relais doit pouvoir servir la dernière session que le cœur lancera :
    plafond − réserve − dépense déjà faite ≥ total − plus petit plafond de juge. Rend l'état lu (pour le manifeste) ;
    lève CourseInterrompue sinon. Fonction séparée pour être éprouvée sans relais.
    v41 (CL40-05) : chaque champ présent est un réel fini ≥ 0, jamais un booléen (un NaN désarmait la garde) ; absent
    (`None`), il n'est pas vérifié (relais muet sur ses plafonds) ; une dépense absente vaut 0.
    v47 (R-764, barrière 3) : si l'état porte `modeles_permis` (relais v47), la liste doit être **exactement** l'ensemble
    des modèles Claude de la course (`modeles_attendus` : proposeurs, juges et, avec l'étage, expérimentateur et lecteur —
    `modeles_du_relais`, v49) — un modèle en plus serait une voie de repli,
    un modèle en moins refuserait une session ; un relais muet (v46) est dit au manifeste."""
    from pole.pari_apparie import _fini
    for champ in ("plafond_usd", "reserve_par_appel_usd", "depense_usd"):
        v = etat_relais.get(champ)
        if v is not None and (not _fini(v) or v < 0):
            raise idn.CourseInterrompue(f"relais : {champ} non fini, booléen ou négatif ({v!r}) : garde du relais impossible "
                                        "(CL40-05)")
    plafond_relais = etat_relais.get("plafond_usd")
    reserve = etat_relais.get("reserve_par_appel_usd")
    depense = float(etat_relais.get("depense_usd") or 0.0)
    lu = {"plafond_usd": plafond_relais, "reserve_par_appel_usd": reserve, "depense_usd": depense,
          "modeles_permis": etat_relais.get("modeles_permis", "relais muet (antérieur à la v47) : barrière 3 absente")}
    if modeles_attendus is not None and "modeles_permis" in etat_relais:  # v47 (R-764, barrière 3)
        permis = etat_relais.get("modeles_permis")
        if not isinstance(permis, list) or set(permis) != set(modeles_attendus):
            raise idn.CourseInterrompue(f"relais : modèles permis {permis!r} ≠ modèles de la course {sorted(set(modeles_attendus))} "
                                        "(R-764, barrière 3) : relancer le relais avec --modeles-permis exactement égal aux "
                                        "modèles des proposeurs, des juges et, avec --tests-de-mort, de l'expérimentateur Claude et du lecteur")
    if plafond_relais is not None and reserve is not None:
        plus_petit_juge = min(budgets[("juge_ideation", m)] for _, m in juges)
        if float(plafond_relais) - float(reserve) - depense < budget_total_usd - plus_petit_juge - 1e-9:
            raise idn.CourseInterrompue(f"relais : plafond {plafond_relais} − réserve {reserve} − dépense {depense} < total "
                                        f"{budget_total_usd} − plus petit juge {plus_petit_juge} : le relais refuserait une "
                                        "session que le cœur lance (CL37-03, CL39-03) ; relancer le relais, ou baisser le total")
    return lu


def verifier_reglages_lanceur(args, budgets, proposeurs, juges, juges_ext, prop_ext, cout_tentatives_claude,
                              cout_tentatives_externe, budget_controle, tolere_claude, tolere_externe, taille_max=None,
                              origine_taille="donnée", provision=0, n_controles_claude=None, n_controles_externes=None,
                              garder_passes=False, url_relais_moisson=None, etage_tests=None):
    """v38 (CL37-04) → v42 : tous les réglages vérifiés AVANT tout appel de contrôle, avec le même contrôle du bras que
    celui que reçoit le cœur (`budget_controle`, CL40-03) et la garde de taille d'Argon (CL41-01).
    v43 (CL40-01, option c) : `n_controles_claude`, `n_controles_externes` — les seuls contrôles à jouer (les réussis d'une
    tentative antérieure sont repris) ; par défaut, tous. Garde au prix `--prix-entree-usd-par-million-jetons`.
    v47 : réglages de la moisson (`reglages_moisson`), tours de moisson comptés dans les sommes.
    v48 : `etage_tests` (`reglages_tests_de_mort`) : étage vérifié ici, sonde du bac à sable comprise, plafonds dans les sommes."""
    if n_controles_claude is None:
        n_controles_claude = len({m for _, m in proposeurs + juges})
    if n_controles_externes is None:
        n_controles_externes = len(prop_ext)
    return idn.verifier_reglages(
        dossier_ferme=args.dossier_ferme, outils_par_protocole=args.outils_par_protocole,  # v46
        max_demandes_lecture=max_demandes_lecture(args), **reglages_moisson(args, url_relais_moisson),  # v47
        liste_blanche=args.liste_blanche, question=args.question, pieces=args.piece, materiau=args.materiau,
        pieces_juge=args.piece_juge, temoins=args.temoins, taille_max_pieces=args.taille_max_pieces, max_tours=args.max_tours,
        attestation_materiau=args.attestation_materiau if (prop_ext and args.seconde_passe) else None,
        budgets=budgets, budget_total_usd=args.budget_total_usd,
        budget_externe_usd=args.budget_externe_usd if (prop_ext or juges_ext) else 0.0, proposeurs=proposeurs, juges=juges,
        proposeurs_externes=prop_ext, juges_externes=juges_ext, seconde_passe=args.seconde_passe,
        cout_controles_prevu_usd=cout_tentatives_claude + budget_controle * n_controles_claude,
        cout_controles_externes_prevu_usd=cout_tentatives_externe + args.budget_controle_externe_usd * n_controles_externes,
        tolerer_somme_claude=tolere_claude, tolerer_somme_externe=tolere_externe,
        budget_controle_bras_usd=budget_controle, nombre_par_proposeur=args.nombre,
        taille_max_consigne_externe=taille_max, origine_taille_max=origine_taille, provision_sortie_caracteres=provision,
        prix_caractere_usd=idn.prix_caractere(args.prix_entree_usd_par_million_jetons),
        budget_passe_2_externe_usd=args.budget_passe_2_externe_usd,  # v44 (CL43-01)
        garder_passes_externes=garder_passes,  # v44 (CL43-02) : passe 1 gardée avant tout contrôle
        etage_tests=etage_tests)  # v48


def bilan_tests_de_mort(r):
    """v48 : ce que le bilan imprime de l'étage de tests de mort (comptes et étiquettes ; jamais le détail des sorties)."""
    statut = r.get("statut") or ("joué" if r.get("termine") else "interrompu")
    return {"statut": statut, "motif": r.get("motif"), "comptes": r.get("comptes"),
            "refusees_a_l_etage": r.get("refusees_a_l_etage"), "classement_intact": r.get("classement_intact"),
            "couts": r.get("couts"), "manifeste": "manifeste-tests-de-mort.json", "statut_epistemique": "exploratoire"}


def max_demandes_lecture(args):
    """v46 : `--max-demandes-lecture`, défaut `MAX_DEMANDES_LECTURE_DEFAUT` (1 000)."""
    from pole.dossier_ferme import MAX_DEMANDES_LECTURE_DEFAUT
    return MAX_DEMANDES_LECTURE_DEFAUT if args.max_demandes_lecture is None else args.max_demandes_lecture


def roles_et_budgets(args):
    """Proposeurs, juges, rôles externes et plafonds par session, tels que la course les prend (v43 : partagé avec
    `--mesurer-consignes`)."""
    proposeurs = [paire(p, f"proposeur-{i + 1}") for i, p in enumerate(args.proposeur)] or \
        [("opus", "claude-opus-5-5"), ("fable", "claude-fable-5-1")]
    juges = [paire(j, f"juge-{i + 1}") for i, j in enumerate(args.juge)] or \
        [("juge-fable", "claude-fable-5-1"), ("juge-opus", "claude-opus-5-5")]
    juges_ext = [paire(j, f"externe-{i + 1}") for i, j in enumerate(args.juge_externe)]
    prop_ext = [paire(j, f"externe-{i + 1}") for i, j in enumerate(args.proposeur_externe)]
    budgets = dict(BUDGETS_PAR_DEFAUT)
    for _, m in juges_ext:
        budgets.setdefault(("juge_ideation", m), BUDGET_EXTERNE_JUGE)
    for _, m in prop_ext:
        budgets.setdefault(("proposeur_ideation", m), BUDGET_EXTERNE_PROPOSEUR)
    for b in args.budget:
        cle, valeur = b.split("=", 1)
        role, modele = cle.split("|", 1)
        budgets[(role.strip(), modele.strip())] = float(valeur)
    return proposeurs, juges, juges_ext, prop_ext, budgets


def garde_de_la_course(args, budgets, prop_ext):
    """v43 (CL42-01) : (taille, origine « option » | « defaut », détail, provision) de la garde de taille de la course —
    l'option, ou le plus petit plafond des sessions d'Argon qui reçoivent sa plus grosse consigne (contrôle, entrée seule ;
    passe, provision de sortie déduite)."""
    if args.taille_max_consigne_externe is not None:
        return args.taille_max_consigne_externe, "option", "option --taille-max-consigne-externe", 0
    taille, d = idn.taille_max_consigne_course_par_defaut(  # v44 (CL43-01) : la plus grosse consigne est celle de la passe 2
        args.budget_controle_externe_usd, [idn.plafond_passe_externe(budgets, m, 2 if args.seconde_passe else 1,
                                                                     args.budget_passe_2_externe_usd) for _, m in prop_ext],
        args.nombre,
        idn.prix_caractere(args.prix_entree_usd_par_million_jetons))
    provision = next((s["provision_sortie_caracteres"] for s in d["sessions"] if s["session"] == d["retenue"]), 0)
    return taille, "defaut", d["detail"], provision


def mesurer(args):
    """v43 (CL42-03) : tailles réelles des consignes pour les fichiers donnés et gardes qui s'y appliqueraient — aucun
    appel, aucun adaptateur construit, aucun fichier écrit (SORTIE n'est pas créée) ; imprimé sur la sortie standard."""
    proposeurs, juges, juges_ext, prop_ext, budgets = roles_et_budgets(args)
    idn._exiger_plafonds(budgets)
    m = idn.mesurer_consignes(liste_blanche=args.liste_blanche, question=args.question, pieces=args.piece,
                              materiau=args.materiau, pieces_juge=args.piece_juge, temoins=args.temoins,
                              taille_max_pieces=args.taille_max_pieces, nombre_par_proposeur=args.nombre,
                              seconde_passe=args.seconde_passe, nombre_proposeurs=len(proposeurs) + len(prop_ext),
                              graine=args.graine, dossier_ferme=args.dossier_ferme,  # v46
                              max_demandes_lecture=max_demandes_lecture(args),
                              moisson=args.moisson, tours_moisson=args.tours_moisson,  # v47 : moisson au pire cas
                              etage_tests=reglages_tests_de_mort(args, None))  # v48 : étage au pire cas, sans sonde
    taille, origine, detail, provision = garde_de_la_course(args, budgets, prop_ext)
    prix = idn.prix_caractere(args.prix_entree_usd_par_million_jetons)
    ctrl = m["consigne_de_controle_externe"]
    # v43 : la provision demandée avec CL42-04 (huit fiches à `fiche_maximale()`), rapportée, non appliquée
    prov_dem = idn.provision_sortie_caracteres(args.nombre, m["taille_fiche_maximale_servie"])
    plafonds_passe = [budgets[("proposeur_ideation", mod)] for _, mod in prop_ext]
    taille_dem = min([idn.taille_max_consigne_par_defaut(args.budget_controle_externe_usd, 0, prix)]
                     + [idn.taille_max_consigne_par_defaut(p, prov_dem, prix) for p in plafonds_passe])
    sortie = {"sans_appel": True, "consignes": m, "moisson": m.get("moisson"),  # v47
              "prix_entree_usd_par_million_jetons": args.prix_entree_usd_par_million_jetons, "prix_caractere_usd": prix,
              "garde_course": {"taille_max_caracteres": taille, "origine": origine, "detail": detail,
                               "provision_sortie_caracteres": provision, "consigne_de_controle": ctrl,
                               "passerait": ctrl <= taille, "cout_prudent_entree_usd": round(ctrl * prix, 4),
                               "cout_entree_controle_usd": round(ctrl * prix, 4),
                               "cout_entree_passe_2_maximale_usd": round((m["consigne_passe_2_maximale"] or 0) * prix, 4),
                               "proposeurs_externes": [e for e, _ in prop_ext],
                               "provision_huit_fiches_maximales_non_appliquee": {
                                   "provision_sortie_caracteres": prov_dem, "cout_usd": round(prov_dem * prix, 4),
                                   "taille_max_caracteres": taille_dem,
                                   "motif": "demandée avec CL42-04 (sortie au rapport 5 de --nombre fiches à fiche_maximale()) ; "
                                            "non appliquée : au-dessus du plafond d'une passe, elle annule la garde"}},
              "garde_bras": {}}
    # v44 (CL43-02) : gardes de chaque passe d'Argon (son plafond moins la provision ; la taille donnée s'il y en a une)
    tdon = args.taille_max_consigne_externe
    gp = {}
    for e, mod in prop_ext:
        p1 = idn.plafond_passe_externe(budgets, mod, 1)
        t1, pv1, o1 = idn.garde_passe_externe(1, p1, args.nombre, prix, tdon)
        gp[e] = {"passe_1": {"plafond_usd": p1, "consigne": m["consigne_passe_1"], "taille_max_caracteres": t1,
                             "provision_sortie_caracteres": pv1, "origine": o1, "passerait": m["consigne_passe_1"] <= t1,
                             "cout_entree_usd": round(m["consigne_passe_1"] * prix, 4),
                             "cout_avec_provision_usd": round((m["consigne_passe_1"] + pv1) * prix, 4)}}
        if args.seconde_passe:
            p2 = idn.plafond_passe_externe(budgets, mod, 2, args.budget_passe_2_externe_usd)
            c2 = m["consigne_passe_2_maximale"]
            for nom_g, tf in (("passe_2_fiches_de_passe_1_au_plus_provisionnees", idn.TAILLE_FICHE_PROVISIONNEE_PASSE),
                              ("passe_2_maximale", m["taille_fiche_maximale_servie"])):
                t2, pv2, o2 = idn.garde_passe_externe(2, p2, args.nombre, prix, tdon, tf)
                gp[e][nom_g] = {"plafond_usd": p2, "taille_fiche_provisionnee": tf, "taille_max_caracteres": t2,
                                "provision_sortie_caracteres": pv2, "origine": o2}
            gp[e]["passe_2_maximale"].update({"consigne": c2, "passerait": c2 <= gp[e]["passe_2_maximale"]["taille_max_caracteres"],
                                              "cout_entree_usd": round(c2 * prix, 4),
                                              "cout_avec_provision_usd": round((c2 + gp[e]["passe_2_maximale"]["provision_sortie_caracteres"]) * prix, 4)})
            gp[e]["passe_2_fiches_de_passe_1_au_plus_provisionnees"]["consigne_max_admise"] = \
                gp[e]["passe_2_fiches_de_passe_1_au_plus_provisionnees"]["taille_max_caracteres"]
    sortie["gardes_passes_externes"] = gp
    provision_juge = idn.provision_sortie_juge_caracteres(m["fiches_au_juge_au_maximum"])
    for e, mod in juges_ext:
        if args.taille_max_consigne_externe_bras is not None:
            tb, ob = args.taille_max_consigne_externe_bras, "option --taille-max-consigne-externe-bras"
        else:
            tb = idn.taille_max_consigne_par_defaut(budgets[("juge_ideation", mod)], provision_juge, prix)
            ob = (f"défaut : plafond du juge {budgets[('juge_ideation', mod)]} / prix prudent − provision de sortie "
                  f"{provision_juge}")
        sortie["garde_bras"][e] = {"taille_max_caracteres": tb, "origine": ob,
                                   "consigne_du_juge_maximale": m["consigne_du_juge_maximale"],
                                   "passerait_au_maximum": m["consigne_du_juge_maximale"] <= tb,
                                   "cout_prudent_entree_usd": round(m["consigne_du_juge_maximale"] * prix, 4)}
    print(json.dumps(sortie, ensure_ascii=False, indent=1))
    return 0


def principal(argv=None):
    a = construire_analyseur()
    args = a.parse_args(argv)

    if args.construire_liste_blanche:
        if not args.sortie:
            a.error("--construire-liste-blanche exige SORTIE (le fichier JSON à écrire)")
        liste = idn.construire_liste_blanche(args.construire_liste_blanche, args.sortie)
        print(json.dumps({"liste_blanche": args.sortie, "fichiers": len(liste)}, indent=1))
        return 0
    for nom, valeur in (("--taille-max-consigne-externe", args.taille_max_consigne_externe),
                        ("--taille-max-consigne-externe-bras", args.taille_max_consigne_externe_bras)):
        if valeur is not None and valeur < 1:  # v42 (CL41-01), v43 (CL42-05)
            a.error(f"{nom} doit être un entier ≥ 1")
    import math
    if not (math.isfinite(args.prix_entree_usd_par_million_jetons) and args.prix_entree_usd_par_million_jetons > 0):
        a.error("--prix-entree-usd-par-million-jetons doit être un réel fini > 0")  # v43 (CL42-04 b)
    if args.budget_passe_2_externe_usd is not None:  # v44 (CL43-01)
        if not (math.isfinite(args.budget_passe_2_externe_usd) and args.budget_passe_2_externe_usd > 0):
            a.error("--budget-passe-2-externe-usd doit être un réel fini > 0")
        if not (args.proposeur_externe and args.seconde_passe):
            a.error("--budget-passe-2-externe-usd ne se donne qu'avec --proposeur-externe et --seconde-passe")
    if args.outils_par_protocole and not args.dossier_ferme:  # v46
        a.error("--outils-par-protocole ne se donne qu'avec --dossier-ferme")
    if args.max_demandes_lecture is not None:
        if not args.dossier_ferme:
            a.error("--max-demandes-lecture ne se donne qu'avec --dossier-ferme")
        if args.max_demandes_lecture < 1:
            a.error("--max-demandes-lecture doit être un entier ≥ 1")
    if args.dossier_ferme and args.bras_rapporte_differe and not args.tests_de_mort:
        a.error("--dossier-ferme ne vaut que pour la course : le bras (juge) ne lit rien, il reçoit les fiches et leurs "
                "citations vérifiées (sauf avec --tests-de-mort : l'expérimentateur peut lire les pages)")
    # v48 : étage de tests de mort
    if args.tests_de_mort == 0:
        for nom, valeur in (("--tranche-exploratoire", args.tranche_exploratoire), ("--experimentateur", args.experimentateur),
                            ("--experimentateur-externe", args.experimentateur_externe), ("--lecteur-test", args.lecteur_test)):
            if valeur:
                a.error(f"{nom} ne se donne qu'avec --tests-de-mort N (N ≥ 1)")
        if args.executeur_tests != "bwrap":
            a.error("--executeur-tests ne se donne qu'avec --tests-de-mort N (N ≥ 1)")
        for nom, valeur in (("--utilisateur-bac", args.utilisateur_bac), ("--dossier-travail-bac", args.dossier_travail_bac),
                            ("--userns-imbriques-permis", args.userns_imbriques_permis),
                            ("--memoire-bac-non-bornee-permise", args.memoire_bac_non_bornee_permise),
                            ("--commande-externe-accepte-experimentateur", args.commande_externe_accepte_experimentateur)):
            if valeur:
                a.error(f"{nom} ne se donne qu'avec --tests-de-mort N (N ≥ 1)")
    else:
        if not 1 <= args.tests_de_mort <= idn_tests.NOMBRE_MAX:
            a.error(f"--tests-de-mort ∉ [0, {idn_tests.NOMBRE_MAX}]")
        if not args.tranche_exploratoire:
            a.error("--tests-de-mort exige --tranche-exploratoire (dossier en lecture seule, index scellé)")
        if bool(args.experimentateur) == bool(args.experimentateur_externe):
            a.error("--tests-de-mort exige exactement un expérimentateur : --experimentateur (Claude) ou "
                    "--experimentateur-externe (Argon par --commande-externe)")
        if not args.lecteur_test:
            a.error("--tests-de-mort exige --lecteur-test (session neuve, d'une autre étiquette que l'expérimentateur)")
        if args.executeur_tests == "factice" and args.moteur == "claude-sdk":
            a.error("--executeur-tests factice : démonstration, moteur simulé seulement (aucune barrière)")
        if args.executeur_tests == "factice" and (args.utilisateur_bac or args.dossier_travail_bac or args.userns_imbriques_permis
                                                  or args.memoire_bac_non_bornee_permise):
            a.error("--utilisateur-bac, --dossier-travail-bac, --userns-imbriques-permis et --memoire-bac-non-bornee-permise ne valent "
                    "que pour le bac à sable bwrap")
        if args.commande_externe_accepte_experimentateur and not args.experimentateur_externe:
            a.error("--commande-externe-accepte-experimentateur ne se donne qu'avec --experimentateur-externe")
    # v47 : moisson — seconde passe obligatoire ; frais : adresse (moteur réel : obligatoire, plus la confirmation) ; rejeu : cache
    if args.moisson == "aucune":
        for nom, valeur in (("--url-relais-moisson", args.url_relais_moisson), ("--cache-moisson", args.cache_moisson),
                            ("--registre-bardeaux", args.registre_bardeaux)):
            if valeur:
                a.error(f"{nom} ne se donne qu'avec --moisson frais ou rejeu")
        if args.confirmer_moisson_reelle:
            a.error("--confirmer-moisson-reelle ne se donne qu'avec --moisson frais et --moteur claude-sdk")
    else:
        if args.bras_rapporte_differe:
            a.error("--moisson ne vaut que pour la course : le bras (juge) ne moissonne jamais")
        if not args.seconde_passe:
            a.error("--moisson exige --seconde-passe (les résultats sont servis dans la consigne de passe 2)")
        if not 1 <= args.tours_moisson <= idn.TOURS_MOISSON_MAX:
            a.error(f"--tours-moisson ∉ [1, {idn.TOURS_MOISSON_MAX}]")
        if not (math.isfinite(args.budget_moisson_usd_par_session) and args.budget_moisson_usd_par_session > 0):
            a.error("--budget-moisson-usd-par-session doit être un réel fini > 0")
        if args.moisson == "frais":
            if args.cache_moisson:
                a.error("--cache-moisson ne se donne qu'avec --moisson rejeu")
            if args.url_relais_moisson:
                try:
                    idn.valider_url_relais_moisson(args.url_relais_moisson)
                except Exception as e:  # noqa: BLE001 — adresse refusée avant tout
                    a.error(f"--url-relais-moisson : {e}")
            if args.moteur == "claude-sdk" and not (args.url_relais_moisson and args.confirmer_moisson_reelle):
                a.error("--moisson frais avec le moteur réel exige --url-relais-moisson et --confirmer-moisson-reelle (la "
                        "première moisson réelle est un GO séparé)")
            if args.moteur != "claude-sdk" and args.confirmer_moisson_reelle:
                a.error("--confirmer-moisson-reelle ne se donne qu'avec --moteur claude-sdk")
        else:
            if args.url_relais_moisson or args.confirmer_moisson_reelle:
                a.error("--moisson rejeu : jamais le réseau (ni --url-relais-moisson ni --confirmer-moisson-reelle)")
            if not args.cache_moisson:
                a.error("--moisson rejeu exige --cache-moisson (dossier noyau/moisson d'une course passée)")
    if args.mesurer_consignes:  # v43 (CL42-03) : sans dépense, sans appel, sans fichier
        if args.bras_rapporte_differe:
            a.error("--mesurer-consignes mesure les consignes d'une course à venir, pas le bras d'une course faite")
        for nom in ("liste_blanche", "question"):
            if not getattr(args, nom):
                a.error(f"--mesurer-consignes exige --{nom.replace('_', '-')}")
        if not 1 <= args.nombre <= idn.MAX_FICHES_ABSOLU:
            a.error(f"--nombre ∉ [1, {idn.MAX_FICHES_ABSOLU}]")
        try:
            return mesurer(args)
        except Exception as e:  # noqa: BLE001 — pièce refusée, réglage refusé : code 2, rien écrit
            print(json.dumps({"arret": type(e).__name__ + " : " + str(e)[:1000]}, ensure_ascii=False), file=sys.stderr)
            return 2
    if args.bras_rapporte_differe and args.taille_max_consigne_externe is not None:  # v43 (CL42-05)
        a.error("--taille-max-consigne-externe ne vaut que pour la course ; au bras : --taille-max-consigne-externe-bras "
                "(la valeur de la course ne s'applique plus au bras)")
    if args.taille_max_consigne_externe_bras is not None and not args.bras_rapporte_differe:
        a.error("--taille-max-consigne-externe-bras ne se donne qu'avec --bras-rapporte-differe")
    requis = (("sortie", "liste_blanche") if args.tests_de_mort else ("sortie",)) if args.bras_rapporte_differe \
        else ("sortie", "liste_blanche", "question", "temoins")
    for nom in requis:
        if not getattr(args, nom):
            a.error(f"--{nom.replace('_', '-')} est requis" if nom != "sortie" else "SORTIE est requis")
    if args.bras_rapporte_differe and not (args.juge_externe and args.attestation_lecture_humaine):
        a.error("--bras-rapporte-differe exige --juge-externe et --attestation-lecture-humaine")
    if args.attestation_lecture_humaine and not args.bras_rapporte_differe:  # CL34-01
        a.error("--attestation-lecture-humaine ne se donne qu'avec --bras-rapporte-differe : le bras est toujours différé")
    if args.commande_externe and not (args.bras_rapporte_differe or args.proposeur_externe or args.experimentateur_externe):  # CL35-07a
        a.error("--commande-externe n'a d'usage qu'avec --proposeur-externe (course), --bras-rapporte-differe ou "
                "--experimentateur-externe (v48)")
    if args.commande_externe_lit_modele and not args.commande_externe:  # v51 (CL15-05)
        a.error("--commande-externe-lit-modele ne se donne qu'avec --commande-externe")
    if args.bras_rapporte_differe and args.proposeur_externe:
        a.error("--bras-rapporte-differe ne joue que des juges externes")
    if not 1 <= args.nombre <= idn.MAX_FICHES_ABSOLU:  # CL34-11
        a.error(f"--nombre ∉ [1, {idn.MAX_FICHES_ABSOLU}]")
    if args.delai_session_s is not None and not args.delai_session_s > 0:  # CL35-09
        a.error("--delai-session-s doit être strictement positif")
    if not args.delai_commande_s > 0:
        a.error("--delai-commande-s doit être strictement positif")
    import signal

    def interrompre(num, _cadre):  # v40 (CL39-05) : SIGTERM et SIGHUP suivent le chemin de SIGINT (groupe d'Argon arrêté,
        raise KeyboardInterrupt(f"signal {num}")  # session comptée au plafond, contrôle compris (v41), manifeste écrit)
    for sig in (signal.SIGTERM, signal.SIGHUP):
        try:
            signal.signal(sig, interrompre)
        except (ValueError, OSError):  # hors du fil principal
            pass
    import contextlib
    pile = contextlib.ExitStack()  # v47 : le relais de moisson factice en mémoire (moteur simulé) est arrêté à la sortie
    try:
        with pile:
            return _principal(args, pile)
    except KeyboardInterrupt as e:
        print(json.dumps({"arret": "interruption : " + str(e)[:200] + " ; session en cours comptée au plafond — contrôle compris "
                          "(v41) : course → manifeste de fin, ou tentative scellée dans SORTIE-controle si l'interruption "
                          "précède le manifeste de départ ; bras → tentative scellée avant envoi, ou après envoi manifeste du "
                          "bras, classement-sans-bras.json (deux juges, illisible) et bras verrouillé"}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 — CL35-08 : toute exception après l'analyse des arguments rend 2
        arret = {"arret": type(e).__name__ + " : " + str(e)[:1000]}
        if getattr(e, "repli_impossible", None):  # v43 (CL42-06) : l'échec du classement de repli est dit
            arret["classement_sans_bras_impossible"] = e.repli_impossible
        print(json.dumps(arret, ensure_ascii=False), file=sys.stderr)
        return 2


def _principal(args, pile=None):
    proposeurs, juges, juges_ext, prop_ext, budgets = roles_et_budgets(args)

    etat_bac = None
    versions = {"python": sys.version.split()[0]}
    lire_relais = None
    interdits = []
    sortie = os.path.abspath(args.sortie)
    sortie_controle = sortie + "-controle"
    delai_session = None
    if args.tests_de_mort:  # v48 : les modèles Claude de l'étage sont ceux de la course (contrôles, relais, barrière 3)
        modeles_etage = ([paire(args.experimentateur, "experimentateur")[1]] if args.experimentateur else []) \
            + ([paire(args.lecteur_test, "lecteur-test")[1]] if args.lecteur_test else [])
        hors = sorted(set(modeles_etage) - {m for _, m in proposeurs + juges})
        if hors:
            raise idn.CourseInterrompue(f"étage de tests de mort : modèle(s) {hors} hors de ceux des proposeurs et des juges de la "
                                        "course (contrôle de bout en bout et relais : un modèle en plus serait une voie de repli)")
    if args.moteur == "claude-sdk" and not args.bras_rapporte_differe and not (prop_ext and juges_ext):  # CL36-03, M29
        raise idn.CourseInterrompue("course réelle : --proposeur-externe et --juge-externe (Argon) sont obligatoires "
                                    "(décision de Lazar : poids égal, égalité)")
    if args.moteur == "claude-sdk" and (not args.bras_rapporte_differe or args.tests_de_mort):  # v48 : l'étage joue des sessions Claude
        from pole.adaptateurs import (DELAI_SESSION_S, AdaptateurClaudeSDK, MoteurNonArme, etat_bac_a_sable_detaille,
                                      importer_sdk, verifier_modele_reel)
        if not args.confirmer_moteur_reel:
            raise MoteurNonArme("--moteur claude-sdk exige --confirmer-moteur-reel (dépense réelle, relais local requis)")
        if not args.url_relais:
            raise MoteurNonArme("--moteur claude-sdk exige --url-relais")
        idn.valider_url_relais_ideation(args.url_relais)
        for _, m in proposeurs + juges:
            verifier_modele_reel(m)
        sdk = importer_sdk()
        versions["claude_agent_sdk"] = getattr(sdk, "__version__", "inconnue")
        versions["outil_ligne_de_commande"] = version_outil_ligne_de_commande(sdk)  # CL34-09, CL35-10
        etat_bac = etat_bac_a_sable_detaille()
        if not etat_bac["actif"]:
            raise idn.CourseInterrompue("bac à sable inactif : " + etat_bac["motif"])
        if not etat_bac["proc_neuf"] and os.geteuid() == 0:
            raise idn.CourseInterrompue("le bac à sable ne monte pas un /proc neuf et l'orchestrateur tourne sous root : "
                                        "lancer les agents sous un utilisateur non root distinct de celui du relais (CL31-15)")
        racine, origine_racine = racine_depot(args.racine_depot)
        interdits = [sortie, sortie_controle, racine, os.path.expanduser("~")]
        versions["racine_depot"] = {"chemin": racine, "origine": origine_racine}
        delai_session = args.delai_session_s or DELAI_SESSION_S
        adaptateur = AdaptateurClaudeSDK(args.url_relais, arme=True, interdire_lecture=interdits, delai_s=delai_session)
        adaptateur.bac_a_sable = etat_bac
        lire_relais = lecteur_relais(args.url_relais)
        adaptateur.lire_etat_relais = lire_relais  # v46 : avertissement de budget du crochet de lecture seule
    else:
        adaptateur = AdaptateurIdeationSimule(args.graine)

    # --- adaptateur des rôles externes (Argon) : la commande, ou un adaptateur scripté en moteur simulé seulement
    externe, commande_externe = None, None
    if args.commande_externe:
        verifier_commande_externe_reelle(args, prop_ext, juges_ext)  # v50 (CL14-07) : avant tout appel
        externe = adaptateur_commande_externe(args)
        commande_externe = externe.description()
    elif args.moteur == "simule" and (prop_ext or args.bras_rapporte_differe or args.experimentateur_externe):
        externe = AdaptateurIdeationSimule(args.graine + 1)
    elif prop_ext:
        raise idn.CourseInterrompue("--proposeur-externe exige --commande-externe avec le moteur réel")
    elif args.experimentateur_externe:
        raise idn.CourseInterrompue("--experimentateur-externe exige --commande-externe avec le moteur réel")
    elif args.bras_rapporte_differe:
        raise idn.CourseInterrompue("--bras-rapporte-differe exige --commande-externe avec le moteur réel")

    # v47 : relais de moisson — donné (`--url-relais-moisson`, le noyau seul client), ou, avec le moteur simulé sans adresse,
    # un relais factice en mémoire sur la boucle locale (aucun réseau), arrêté à la sortie ; rejeu : aucun relais
    url_moisson = None
    if args.moisson == "frais" and not args.bras_rapporte_differe:
        if args.url_relais_moisson:
            url_moisson = idn.valider_url_relais_moisson(args.url_relais_moisson)
            versions["moisson"] = {"relais": "donné (--url-relais-moisson) ; réel ou factice selon ce qui écoute", "url": url_moisson}
        else:
            from pole.moisson import RelaisMoissonFactice
            relais_factice = RelaisMoissonFactice()
            if pile is not None:
                pile.callback(relais_factice.arreter)
            url_moisson = relais_factice.url
            versions["moisson"] = {"relais": "factice en mémoire (moteur simulé) : notices de démonstration, aucun réseau",
                                   "url": url_moisson}
    elif args.moisson == "rejeu":
        versions["moisson"] = {"relais": "aucun (rejeu, jamais le réseau)", "cache": os.path.abspath(args.cache_moisson)}

    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    if args.bras_rapporte_differe:
        try:
            res = idn.executer_bras_differe(sortie, attestation_lecture_humaine=args.attestation_lecture_humaine,
                                            juges_externes=[(e, m, externe) for e, m in juges_ext], budgets=budgets,
                                            horodatage=horodatage(args.horodatage), budget_controle_usd=args.budget_controle_usd,
                                            exiger_cout_controle=bool(args.commande_externe),
                                            # v42 (CL41-01) : le plafond externe donné passe au bras ; sinon celui de la course
                                            budget_externe_usd=(args.budget_externe_usd
                                                                if getattr(args, "budget_externe_usd_explicite", False) else None),
                                            commande_externe=commande_externe,
                                            # v43 (CL42-05) : garde propre au bras ; la valeur de la course n'y vaut plus
                                            taille_max_consigne_externe=args.taille_max_consigne_externe_bras,
                                            prix_caractere_usd=idn.prix_caractere(args.prix_entree_usd_par_million_jetons))
        except idn.SansJugeExterne as e:
            print(json.dumps({"arret": "sans juge externe, illisible au sens du devis : " + str(e),
                              "classement_sans_bras": "classement-sans-bras.json (deux juges, illisible)",
                              "cout_total_usd": round(e.resultat["journal"]["cout_total_usd"], 4)}, ensure_ascii=False,
                             indent=1), file=sys.stderr)
            return 5
        lisible = res["lecture"]["lisible_L2_L4"]
        bilan = {"juges_agreges": res["lecture"]["juges_agreges"], "nom_agregat": res["lecture"]["nom_agregat"],
                 "temoins_ok": res["lecture"]["temoins"]["temoins_ok"], "classement_lisible_L2_L4": lisible,
                 "accords_de_rang_par_paire": res["lecture"]["accords_de_rang_par_paire"],
                 "cout_total_usd": round(res["journal"]["cout_total_usd"], 4), "cout_fictif": res["journal"]["cout_fictif"]}
        if lisible:
            bilan["retenues"] = [(l["rang"], l["identifiant_auteur"], l["nom"], l["total"]) for l in res["classement"]
                                 if l["eligible"]][:5]
        if args.tests_de_mort:  # v48 : l'étage se joue après le bras, classement scellé et figé ; jamais sur un classement illisible
            if lisible:
                if lire_relais is not None:  # barrière 3 (R-764) : relais permettant exactement les modèles de la course
                    verifier_relais(lire_relais(), 0.0, budgets, juges, modeles_attendus=modeles_du_relais(args, proposeurs, juges))
                bilan["tests_de_mort"] = bilan_tests_de_mort(idn.jouer_etage_apres_bras(
                    adaptateur, sortie, reglages_tests_de_mort(args, externe), liste_blanche=args.liste_blanche,
                    dossier_ferme=args.dossier_ferme, moteur=args.moteur, horodatage=horodatage(args.horodatage),
                    lire_etat_relais=lire_relais, budget_total_usd=args.budget_total_usd, budget_externe_usd=args.budget_externe_usd,
                    prix_caractere_usd=idn.prix_caractere(args.prix_entree_usd_par_million_jetons)))
            else:
                bilan["tests_de_mort"] = {"statut": "non joué : classement illisible au sens du devis"}
        print(json.dumps(bilan, ensure_ascii=False, indent=1))
        return 0 if lisible else 4
    # CL31-01 : appel de contrôle par modèle Claude, avant tout, dans `SORTIE-controle` (interdit en lecture aux agents) ;
    # son coût est compté dans le plafond total (CL34-07). Le juge externe fait le sien sur le chemin différé.
    if args.moteur == "claude-sdk" and not (prop_ext and juges_ext):  # CL36-03
        raise idn.CourseInterrompue("course réelle : --proposeur-externe et --juge-externe (Argon) sont obligatoires "
                                    "(décision de Lazar : poids égal, égalité)")
    # v38 (CL37-04) : tous les réglages vérifiés AVANT tout appel de contrôle (liste blanche, pièces et tailles, attestation
    # du matériau, plafonds finis, somme des plafonds) — un refus ici ne coûte rien
    if os.path.exists(sortie):  # v40 (CL39-07) : refus avant tout contrôle
        raise idn.CourseInterrompue(f"SORTIE existe déjà : {sortie} (jamais écrasée, R12)")
    tentatives = lire_tentatives_controle(sortie_controle)  # v40 (CL39-02) : contrôles déjà payés dans cette SORTIE-controle
    if len(tentatives) >= idn.MAX_TENTATIVES_BRAS:
        raise idn.CourseInterrompue(f"{len(tentatives)} tentatives de contrôle déjà faites dans {sortie_controle} : la relance "
                                    f"est bornée par les sommes ET par {idn.MAX_TENTATIVES_BRAS} tentatives "
                                    "(MAX_TENTATIVES_BRAS) ; plus de relance sans un mot de Lazar (CL39-02, CL43-05)")
    budget_controle = 0.2 if args.budget_controle_usd is None else args.budget_controle_usd  # devis v7 quinquies
    cout_tentatives_claude = sum(t["cout_claude_usd"] for t in tentatives)
    cout_tentatives_externe = sum(t["cout_externe_usd"] for t in tentatives)
    # v41 (CL40-01, code) : deux tolérances séparées ; l'ancienne option vaut les deux (consigné au manifeste)
    tolere_claude, tolere_externe = idn.tolerances(args.tolerer_somme_plafonds, args.tolerer_somme_plafonds_claude,
                                                   args.tolerer_somme_plafonds_externe)
    versions["tolerances"] = {"claude": tolere_claude, "externe": tolere_externe,
                              "option_ancienne_les_deux": bool(args.tolerer_somme_plafonds)}
    # v42 (CL41-01) : taille maximale de la plus grosse consigne d'Argon dans la course (sa consigne de contrôle) — donnée,
    # ou prix prudent d'un caractère (barème le plus haut du code, 4 caractères par jeton). v43 (CL42-01) : défaut = plus
    # petit plafond des sessions d'Argon qui reçoivent cette consigne (contrôle, entrée seule ; passe, provision de sortie
    # déduite) — `--budget-controle-externe-usd 3.0` seul laisse la garde à 520 000 (la passe reste à 2,5)
    taille_max, _origine, origine_taille, provision_taille = garde_de_la_course(args, budgets, prop_ext)
    versions["taille_max_consigne_externe"] = {"valeur": taille_max, "origine": "option" if args.taille_max_consigne_externe
                                               is not None else "defaut", "detail": origine_taille,
                                               "provision_sortie_caracteres": provision_taille,
                                               "prix_entree_usd_par_million_jetons": args.prix_entree_usd_par_million_jetons}
    # v43 (CL40-01, option c, décision de Lazar) : les contrôles réussis d'une tentative scellée ne sont pas rejoués — clé
    # de chaque contrôle (la consigne d'Argon est lue sans garde ni somme : celles-ci se jouent juste après, sur les seuls
    # contrôles restants)
    modeles = sorted({m for _, m in proposeurs} | {m for _, m in juges})
    reussis = controles_reussis(sortie_controle, tentatives)
    identite_claude = {"moteur": args.moteur, "url_relais": args.url_relais}
    identite_externe = commande_externe or {"adaptateur": type(externe).__name__ if externe is not None else None}
    cles = {m: cle_reprise("juge_ideation", m, hashlib.sha256(idn.APPEL_DE_CONTROLE_CONSIGNE.encode("utf-8")).hexdigest(),
                           identite_claude) for m in modeles}
    if prop_ext and reussis:
        texte_ext = verifier_reglages_lanceur(args, budgets, proposeurs, juges, juges_ext, prop_ext, cout_tentatives_claude,
                                              cout_tentatives_externe, budget_controle, True, True,
                                              url_relais_moisson=url_moisson,
                                              etage_tests=reglages_tests_de_mort(args, externe))["texte_controle_externe"]
        for e, m in prop_ext:
            cles[f"externe:{e}"] = cle_reprise("proposeur_ideation", m, hashlib.sha256(
                idn.consigne_de_controle(texte_ext).encode("utf-8")).hexdigest(), identite_externe)
    repris = {k: reussis[c] for k, c in cles.items() if c in reussis}
    repris, motifs_reprise = filtrer_reprises_claude(repris, lire_relais)  # v44 (CL43-03)
    if motifs_reprise:
        print(json.dumps({"reprise_des_controles_claude": motifs_reprise}, ensure_ascii=False), file=sys.stderr)
    a_jouer_claude = [m for m in modeles if m not in repris]
    a_jouer_externe = [(e, m) for e, m in prop_ext if f"externe:{e}" not in repris]
    try:
        verif = verifier_reglages_lanceur(args, budgets, proposeurs, juges, juges_ext, prop_ext, cout_tentatives_claude,
                                          cout_tentatives_externe, budget_controle, tolere_claude, tolere_externe,
                                          taille_max if prop_ext else None, origine_taille, provision_taille,
                                          n_controles_claude=len(a_jouer_claude), n_controles_externes=len(a_jouer_externe),
                                          garder_passes=True,  # v44 (CL43-02) : passe 1 gardée avant tout contrôle
                                          url_relais_moisson=url_moisson,  # v47
                                          etage_tests=reglages_tests_de_mort(args, externe))  # v48
    except idn.TailleConsigneRefusee as e:  # refus scellé, avant tout contrôle, rien payé, aucune tentative comptée
        from pole.outils import ecrire_json_scelle, manifeste
        os.makedirs(sortie_controle, exist_ok=True)
        k = 1 + sum(1 for n in os.listdir(sortie_controle) if re.match(r"refus-taille-\d+\.json$", n))
        chemin_r = os.path.join(sortie_controle, f"refus-taille-{k}.json")
        ecrire_json_scelle(chemin_r, manifeste(phase="controle-refus-taille", horodatage=horodatage(args.horodatage),
                                               erreur=str(e), garde_taille=e.details, tentative_comptee=False, cout_usd=0.0))
        print(json.dumps({"refus_taille_scelle": chemin_r, "cout_usd": 0.0, "garde_taille": e.details}, ensure_ascii=False),
              file=sys.stderr)
        raise
    if prop_ext:  # v42 (CL41-02) : la taille de la marge et du contrôle, écrite au manifeste de départ
        versions["marge_controle_externe"] = {"taille_consigne_de_controle": verif["taille_consigne_controle_externe"],
                                              "taille_fiche_maximale_servie": verif["taille_fiche_maximale"],
                                              "nombre": args.nombre, "seconde_passe": args.seconde_passe,
                                              "garde_taille": verif["garde_taille"]}
    if lire_relais is not None:  # CL37-03 / CL39-03 : cohérence plafond, réserve, dépense déjà faite, total du cœur
        versions["relais_au_depart"] = verifier_relais(lire_relais(), args.budget_total_usd, budgets, juges,
                                                       modeles_attendus=modeles_du_relais(args, proposeurs, juges))  # v47 (R-764), v49
    versions["tentatives_precedentes"] = tentatives
    versions["controles_repris"] = repris  # v43 (CL40-01, option c) : tentative, empreinte du fichier et de la consigne
    versions["motifs_reprise_controles"] = motifs_reprise  # v44 (CL43-03)
    numero_tentative = len(tentatives) + 1
    dossier_tentative = os.path.join(sortie_controle, f"tentative-{numero_tentative}")
    controle = {}
    try:
        for e, m in a_jouer_externe:  # CL36-02 / CL37-01 : contrôle du proposeur externe AVANT la passe 1, sous son rôle,
            # à la taille réelle de la plus grosse consigne qu'il recevra (CL39-06, CL40-04 : sa consigne de passe 2 au
            # maximum ; v42 : matériau encadré, consigne qui finit par « OK », CL41-03) ; v42 (CL41-07) : joué AVANT les
            # contrôles Claude — une panne d'Argon au contrôle ne coûte rien chez Claude ; v43 (CL40-01 c) : sauf s'il est repris
            controle[f"externe:{e}"] = idn.appel_de_controle(
                externe, [m], dossier_tentative + "-externe-" + e, args.budget_controle_externe_usd, None,
                exiger_cout=bool(args.commande_externe), role="proposeur_ideation", supplement=verif["texte_controle_externe"])[m]
            controle[f"externe:{e}"]["cle_reprise"] = cle_reprise("proposeur_ideation", m, controle[f"externe:{e}"]["consigne_sha256"],
                                                                identite_externe)
        if a_jouer_claude:  # v43 (CL40-01 c) : les contrôles Claude réussis d'une tentative antérieure ne sont pas rejoués
            controle.update(idn.appel_de_controle(adaptateur, a_jouer_claude, dossier_tentative, budget_controle, lire_relais,
                                                  exiger_cout=(args.moteur == "claude-sdk")))
            for m in a_jouer_claude:
                controle[m]["cle_reprise"] = cles[m]
        cout_controle = sum(idn.cout_compte_controle(c) for k, c in controle.items() if not k.startswith("externe:"))
        cout_controle_externe = sum(idn.cout_compte_controle(c) for k, c in controle.items() if k.startswith("externe:"))
        # v41 (CL40-03) : le cœur reçoit le même contrôle du bras que verifier_reglages ; tout refus du cœur avant son
        # manifeste de départ est une tentative payée (scellée ci-dessous, bornée)
        res = idn.executer_ideation(adaptateur, sortie, liste_blanche=args.liste_blanche, question=args.question,
                                    pieces=args.piece, proposeurs=proposeurs, juges=juges, temoins=args.temoins,
                                    graine=args.graine, budget_total_usd=args.budget_total_usd, budgets=budgets,
                                    nombre_par_proposeur=args.nombre, max_tours=args.max_tours, materiau=args.materiau,
                                    seconde_passe=args.seconde_passe, pieces_juge=args.piece_juge,
                                    horodatage=horodatage(args.horodatage), moteur=args.moteur,
                                    lire_etat_relais=lire_relais, etat_bac_a_sable=etat_bac, url_relais=args.url_relais,
                                    versions=dict(versions, appel_de_controle=controle), juges_externes=juges_ext,
                                    proposeurs_externes=[(e, m, externe) for e, m in prop_ext],
                                    budget_externe_usd=args.budget_externe_usd if (prop_ext or juges_ext) else 0.0,
                                    attestation_materiau=args.attestation_materiau,
                                    cout_deja_engage_usd=cout_controle + cout_tentatives_claude,
                                    lectures_interdites=interdits, commande_externe=commande_externe,
                                    # v46 : en moteur simulé avec --dossier-ferme, --delai-session-s borne les passes par protocole
                                    delai_session_s=(args.delai_session_s if (delai_session is None and args.dossier_ferme)
                                                     else delai_session), taille_max_pieces=args.taille_max_pieces,
                                    cout_externe_deja_engage_usd=cout_controle_externe + cout_tentatives_externe,
                                    tolerer_somme_claude=tolere_claude, tolerer_somme_externe=tolere_externe,
                                    budget_controle_bras_usd=budget_controle,
                                    # v43 (CL42-01) : chaque passe d'Argon gardée avant son envoi, sans dépense
                                    taille_max_consigne_externe=args.taille_max_consigne_externe,
                                    garder_sessions_externes=True,
                                    origine_taille_max=("option --taille-max-consigne-externe"
                                                        if args.taille_max_consigne_externe is not None else None),
                                    prix_caractere_usd=idn.prix_caractere(args.prix_entree_usd_par_million_jetons),
                                    controles_repris=repris, motifs_reprise_controles=motifs_reprise,  # v44 (CL43-03)
                                    budget_passe_2_externe_usd=args.budget_passe_2_externe_usd,  # v44 (CL43-01)
                                    **reglages_lecture(args, delai_session),  # v46 : vide sans --dossier-ferme
                                    **reglages_moisson(args, url_moisson),  # v47 : vide sans --moisson
                                    etage_tests=reglages_tests_de_mort(args, externe))  # v48 : None sans --tests-de-mort
    except BaseException as e:  # v40 (CL39-02), v41 (CL40-02, CL40-03) : contrôle refusé, contrôle interrompu (plafond
        # compté) ou refus du cœur avant son manifeste de départ → tentative scellée avec ses coûts, relance calculée
        if os.path.exists(os.path.join(sortie, "manifeste-depart.json")):
            raise  # la course a commencé : son manifeste de fin porte tout
        lectures, etiquette_externe = dict(controle), {m: e2 for e2, m in prop_ext}
        for m, c in (getattr(e, "lecture", None) or {}).items():  # lectures accumulées jointes à l'exception (CL40-02)
            lectures[("externe:" + etiquette_externe.get(m, m)) if c.get("role") == "proposeur_ideation" else m] = c
        for k, c in lectures.items():  # v43 (CL40-01 c) : chaque lecture porte sa clé de reprise
            if isinstance(c, dict) and not c.get("cle_reprise"):
                if k.startswith("externe:") and c.get("consigne_sha256"):
                    c["cle_reprise"] = cle_reprise("proposeur_ideation", c.get("modele") or dict(prop_ext).get(k[8:]),
                                                   c["consigne_sha256"], identite_externe)
                elif k in cles:
                    c["cle_reprise"] = cles[k]
        cout_c = sum(idn.cout_compte_controle(c) for k, c in lectures.items() if not k.startswith("externe:"))
        cout_x = sum(idn.cout_compte_controle(c) for k, c in lectures.items() if k.startswith("externe:"))
        # v43 (CL40-01, option c) : la relance ne rejouera que les contrôles échoués ou non faits — sa somme compte les
        # coûts déjà imputés, les plafonds de ces seuls contrôles et les sessions
        tous = [m for m in modeles] + [f"externe:{e2}" for e2, _ in prop_ext]
        reussis_ici = set(repris) | {k for k, c in lectures.items() if controle_reussi(c)}
        a_refaire = [k for k in tous if k not in reussis_ici]
        n_c = sum(1 for k in a_refaire if not k.startswith("externe:"))
        n_x = sum(1 for k in a_refaire if k.startswith("externe:"))
        verif_relance = dict(verif, somme_claude=verif["somme_claude"] + budget_controle * (n_c - len(a_jouer_claude)),
                             somme_externe=verif["somme_externe"]
                             + args.budget_controle_externe_usd * (n_x - len(a_jouer_externe)))
        relancable, motifs, relais_a_neuf = relance_possible(
            numero_tentative, verif_relance, cout_c, cout_x, args.budget_total_usd,
            args.budget_externe_usd if (prop_ext or juges_ext) else 0.0, tolere_claude, tolere_externe,
            bool(prop_ext or juges_ext), versions.get("relais_au_depart"), budgets, juges, details=True)
        if os.path.exists(sortie):  # v42 (CL41-06) : SORTIE sans manifeste de départ — la relance refuserait « SORTIE existe »
            relancable = False
            relais_a_neuf = dict(relais_a_neuf, relancable=False)
            motifs.append(f"SORTIE {sortie} existe sans manifeste de départ (interruption entre sa création et le manifeste) : "
                          "la relance refuserait « SORTIE existe déjà » ; mot de Lazar")
        from pole.outils import ecrire_json_scelle, manifeste
        chemin_t = os.path.join(sortie_controle, f"tentative-{numero_tentative}.json")
        ecrire_json_scelle(chemin_t, manifeste(
            phase="controle-tentative", horodatage=horodatage(args.horodatage), lectures=lectures,
            cout_claude_usd=cout_c, cout_externe_usd=cout_x, erreur=type(e).__name__ + " : " + str(e)[:500],
            relancable=relancable, motifs_relance=motifs, sommes_de_cette_course={
                "claude": verif["somme_claude"], "externe": verif["somme_externe"]}, tolerances=versions["tolerances"],
            hypothese_relancable="relais gardé (sa dépense comptée)", relance_relais_relance_a_neuf=relais_a_neuf,
            controles_repris=repris, controles_a_refaire=a_refaire,  # v43 (CL40-01, option c)
            motifs_reprise_controles=motifs_reprise,  # v44 (CL43-03)
            sommes_de_la_relance_hors_cette_tentative={"claude": verif_relance["somme_claude"],
                                                       "externe": verif_relance["somme_externe"]}))
        print(json.dumps({"tentative_scellee": chemin_t, "cout_claude_usd": round(cout_c, 6),
                          "cout_externe_usd": round(cout_x, 6), "relancable": relancable,
                          "controles_repris": sorted(repris), "controles_a_refaire": a_refaire,
                          "motifs_relance": motifs or ["aucun : relance permise"],
                          "relance_relais_relance_a_neuf": relais_a_neuf}, ensure_ascii=False), file=sys.stderr)
        raise
    bilan = {"fiches_validees": len(res["fiches"]), "refusees": len(res["refus"]), "quarantaine": len(res["quarantaine"]),
             "quarantaine_par_proposeur": res["lecture"]["quarantaine_par_proposeur"],
             "temoins_ok": res["lecture"]["temoins"]["temoins_ok"],
             "cout_total_usd": round(res["journal"]["cout_total_usd"], 4),
             "cout_externe_usd": round(res["journal"]["cout_externe_usd"], 4), "cout_fictif": res["journal"]["cout_fictif"]}
    if "moisson" in res["journal"]:  # v47 : tours de moisson, demandes par statut, MOISSONNE vérifiées (jamais aux juges)
        m = res["journal"]["moisson"]
        statuts = {}
        for etat in m["par_proposeur"].values():
            for t in etat["tours"]:
                for s, n in (t.get("par_statut") or {}).items():
                    statuts[s] = statuts.get(s, 0) + n
        verif = m.get("verification_moissonnees") or {}
        bilan["moisson"] = {"mode": m["mode"], "proposeurs_avec_tour": len(m["par_proposeur"]), "demandes_par_statut": statuts,
                            "refus_durs_juges": len(m["refus_durs"]),
                            "moissonnees_citees": sum(len(l) for l in verif.values()),
                            "moissonnees_verifiees": sum(1 for l in verif.values() for x in l if x.get("verifiee")),
                            "candidats_corpus": "candidats-corpus.json"}
    if res.get("tests_de_mort"):  # v48 : course sans juge externe, l'étage a été joué par le cœur
        bilan["tests_de_mort"] = bilan_tests_de_mort(res["tests_de_mort"])
    if res["en_attente_bras"]:
        bilan["en_attente_bras"] = res["lecture"]["bras_rapporte_differe"]
        bilan["classement"] = "aucun avant le bras (n° 118 point 1)"
        if args.tests_de_mort:
            bilan["tests_de_mort"] = {"statut": "différé : après le bras (--bras-rapporte-differe --tests-de-mort, mêmes réglages)"}
        print(json.dumps(bilan, ensure_ascii=False, indent=1))
        return 0 if res["lecture"]["temoins"]["temoins_ok"] else 4
    lisible = res["lecture"]["temoins"]["temoins_ok"]
    bilan["classement_lisible_L2_L4"] = lisible
    if lisible:  # v34 (P-7) : aucune « retenue » n'est imprimée quand les témoins ont échoué
        bilan["retenues"] = [(l["rang"], l["identifiant_auteur"], l["nom"], l["total"]) for l in res["classement"]
                             if l["eligible"]][:5]
    print(json.dumps(bilan, ensure_ascii=False, indent=1))
    return 0 if lisible else 4


if __name__ == "__main__":
    raise SystemExit(principal())
