"""Cœur de la plus petite course réelle de la boucle complète de l'organisme, version 65 (fichier neuf, R12) — **bras réel
seul**, génération 1 complète, génération 2 complète jusqu'à sa sélection scellée.

Dessin : brouillon 1 du préenregistrement de la course (dépôt de travail, `docs/notes/organisme-boucle-reelle-v1/
preenregistrement-boucle-reelle-organisme-v1-brouillon1.md`, sha256 736e3fd6…), sections 3, 5 à 10 et 12 ; défauts de la v64
relevés par l'essai à blanc v1 (`essai-a-blanc-v1/journal-essai-a-blanc-v1.md`, sha256 627f7a4c…, section 4) ; décision du
directeur GO-2026-11-08-02 (D1 bras réel seul, D2 génération 2 complète, D3 plafonds). Ce module **ne lit aucune issue** : il
produit le relevé que lit `pole/lecture_boucle_reelle_v65.py` (lecture gelée), par le programme
`demonstrations/lire_boucle_reelle_v65.py`. Aucun réseau ici ; les adaptateurs réels sont construits par le lanceur
`demonstrations/boucle_reelle_v65.py`.

Pièces (repères du brouillon, section 12) :

M1. **Héritage de départ scellé** (`lire_heritage_depart`) : la « génération 0 » déclarée porte la seule loi K1, marquée « connue,
    déclarée » ; elle n'est acceptée que si l'empreinte de ses octets est celle que porte le plan du texte qu'on lui passe
    (`heritage_depart_sha256`), sans repli ; elle ne contient aucune autre loi, et aucune loi plantée (garde 17). La génération 1
    juge contre elle et la sert aux proposeurs (vue v59) ; la génération 2 lit le bilan de la génération 1 par `lire_heritage_v65`
    (la lecture v59 inchangée, plus : archive exactement {K1} ∪ retenues, K1 inchangée).
M2. **Jeu planté lu dans le texte** (`lire_jeu_plante`) : remplace les `TEMOINS` fixes de la v64 ; un bloc JSON canonique (lu à
    l'octet, empreinte égale à `jeu_plante_sha256` du plan : garde 19) porte V1 à V4, F1 à F4, T-ELIM et T-MAL ; chaque fausse
    est vérifiée dans la classe que le nul v8 couvre (`classer_couverte` : copie d'une loi connue, mélange de lois connues et de
    lois aveugles fixes, loi connue tempérée et inclinée — docstring de `pole/nul_v8.py`, brouillon § 3.4), sa ligne du banc
    déclarée égale à sa forme ; toute autre forme est refusée (`FausseHorsClasse`).
M3. **Jugement avec l'archive** (`juger_v65`) : les lois plantées (et, en génération 2, les copies) sont jugées sous le nul v8
    **avec l'archive de jugement de leur génération** — la même que celle des cartes réelles —, hors de la famille des cartes
    (elles ne pèsent pas sur le nombre de cartes retenues), promues si le juge les promeut et si leur log e atteint log(m/α).
    La v64 les jugeait sans archive (`tour_ferme_v64.juger`, témoins : `{}`). Garde 18 (`exiger_archive_des_plantees`) : le
    nombre de membres d'archive de chaque loi plantée doit être celui qu'impose l'archive de sa génération, sinon arrêt.
M4. **Bras réel seul ; génération 2 complète** : option scellée « reel_seul » (`exiger_bras_reel_seul`, garde 20) ; la génération 2
    lit la sélection de la génération 1 (empreinte du bilan passée par l'orchestrateur), sert aux proposeurs {K1} ∪ retenues,
    juge contre la même archive, teste les seules cartes réelles promues, et replante F1 à F4 plus une copie renommée de
    chacune des quatre premières retenues par log e (`copies_de_la_selection`, garde 21), lois prises dans l'héritage lu.
    Génération 1 : toute loi plantée promue est testée (comme les témoins de la v64 : P1 et P4 l'exigent pour les vraies et
    T-ELIM) ; génération 2 : aucune loi plantée n'est testée (brouillon § 3.7 (iii) et § 7.2).
Gardes de dépense (`CompteurV65`, `AdaptateurSousGo`) : plafond des modèles et part de chaque relais (Kimi, Argon), plafond de la
    machine à part ; **aucun appel dont la borne dépasse la part restante** (arrêt au plafond, avant l'appel) ; aucun appel d'un
    adaptateur réel sans la ligne de GO vérifiée, à l'identifiant et au montant du plan.

Relevé : le jugement d'une génération y entre **avant** ses étages (un arrêt pendant un étage laisse un relevé partiel qui montre déjà
une fausse ou une copie promue : § 8, C5) ; recherche des paramètres de L* dans les contextes des proposeurs (v64) et, § 7.6, dans les
consignes de l'expérimentateur et du vérificateur hors de la loi gelée servie (`chercher_dans_l_etage`, mesure sans issue).

Réutilisé sans modification : `tour_ferme_v64` (gabarit, gardien mécanique, juge des cartes à e-BH, étage des tests de mort et
contre-calcul, proposeurs et doublures), `boucle_fermee_v59` (bilan, lecture vérifiée, vue sans verdict), `nul_v8` (membres
d'archive), `a_blanc_v59` (juge d'une carte). L'oracle du monde planté n'est **pas** appelé pendant la course (brouillon § 7.3) :
gains et classes sont calculés après, par la lecture gelée.
"""

import copy
import hashlib
import json
import math
import os
import re
import stat
import time

from . import a_blanc_v59 as A
from . import boucle_fermee_v59 as bf
from . import nul_v8
from . import tour_ferme_v64 as T
from .outils import json_canonique, sha256_fichier

VERSION = "boucle-reelle-v65"
ALPHA = T.ALPHA
GENERATIONS = 2
OPTION_BRAS = "reel_seul"
BRAS = "reel"
VRAIES = ("V1", "V2", "V3", "V4")
FAUSSES = ("F1", "F2", "F3", "F4")
INSTRUMENTS = ("T-ELIM", "T-MAL")
PLANTEES_G1 = VRAIES + FAUSSES + INSTRUMENTS
COPIES_MAX = 4
NOM_DEPART = "K1"
STATUT_DECLARE = "connue, déclarée"
VERSION_HERITAGE = "heritage-depart-v65"
VERSION_JEU = "jeu-plante-v65"
SOURCE_PLANTEE = "temoin"  # le mot de la v64 pour une loi plantée (jamais servi : C15)
DOSSIER_ETAGE_PLANTEES = "etage-plantees"
DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele-v65 : début -->", "<!-- plan-gele-v65 : fin -->"
DEBUT_JEU, FIN_JEU = "<!-- jeu-plante-v65 : début -->", "<!-- jeu-plante-v65 : fin -->"
CLES_PLAN = ("generations", "bras", "cartes_par_proposeur", "m_e_bh", "plafond_modeles_usd", "plafond_kimi_usd", "plafond_argon_usd",
             "plafond_machine_usd", "duree_h", "d9", "configuration_sha256", "go", "monde_sha256", "heritage_depart_sha256",
             "jeu_plante_sha256")
LIGNES_DU_BANC = {"T17s": "copie renommée d'une loi connue", "T01": "mélange de lois connues",
                  "T03u": "mélange de lois connues et de l'uniforme", "T03b": "mélange de lois connues et d'une loi aveugle fixe",
                  "T05s": "loi connue tempérée et inclinée"}
SHA = re.compile(r"^[0-9a-f]{64}$")
TOLERANCE_CENTIME = 0.5


class BoucleRefusee(T.TourRefuse):
    """Refus avant tout appel (code 2) : plan, héritage de départ, jeu planté, bras, commandes, GO."""


class HeritageDepartRefuse(BoucleRefusee):
    """Garde 17 : héritage de départ d'une autre empreinte que celle du texte, altéré, ou portant une loi plantée."""


class JeuPlanteRefuse(BoucleRefusee):
    """Garde 19 et M2 : jeu planté absent, incomplet, non canonique, d'une autre empreinte que celle du plan."""


class FausseHorsClasse(JeuPlanteRefuse):
    """M2 : une loi fausse plantée hors de la classe que le nul v8 couvre (brouillon § 3.4)."""


class BrasRefuse(BoucleRefusee):
    """Garde 20 : un autre bras que le bras réel seul."""


class GoNonCite(BoucleRefusee):
    """Aucun appel d'un adaptateur réel sans la ligne de GO vérifiée (identifiant et montant du plan)."""


class ArchiveDesPlanteesAbsente(T.ArretTour):
    """Garde 18 : une loi plantée jugée avec un autre nombre de membres d'archive que celui de sa génération (code 3)."""


class CopieRefusee(T.ArretTour):
    """Garde 21 : copie d'une carte non retenue, d'une autre loi, ou autres que les quatre premières retenues par log e."""


class PlafondAtteint(T.ArretTour):
    """Arrêt au plafond : la borne d'un appel dépasse la part restante de son relais ou le plafond restant (avant l'appel)."""


# --- plan du texte -------------------------------------------------------------------------------------------------------------


def bloc_unique(texte, debut, fin, nom, erreur=BoucleRefusee):
    """Le contenu entre `debut` et `fin`, chacun présent exactement une fois et dans cet ordre ; sinon `erreur`."""
    if not isinstance(texte, str) or texte.count(debut) != 1 or texte.count(fin) != 1 or texte.find(fin) < texte.find(debut):
        raise erreur(f"bloc « {nom} » absent, en double ou mal formé dans le texte")
    return texte[texte.find(debut) + len(debut):texte.find(fin)]


def m_impose(cartes_par_proposeur):
    """m fixé d'avance (brouillon § 6) : cartes réelles des deux proposeurs + 8 lois plantées + 2 cas d'instrument."""
    return 2 * cartes_par_proposeur + len(VRAIES) + len(FAUSSES) + len(INSTRUMENTS)


def lire_plan(texte):
    """Bloc `plan-gele-v65` : lignes « clé: valeur » ; rend le plan ou lève `BoucleRefusee` (code 2). Le code gèle deux générations,
    le bras réel seul, m = 2 × cartes + 10, la durée de 72 heures (R-1294), le gardien mécanique ; les parts des relais font le
    plafond des modèles au centime."""
    lignes = {}
    for l in bloc_unique(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele-v65").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise BoucleRefusee(f"plan-gele-v65 : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    if set(lignes) != set(CLES_PLAN):
        raise BoucleRefusee(f"plan-gele-v65 : clés attendues {sorted(CLES_PLAN)}, manquantes {sorted(set(CLES_PLAN) - set(lignes))}, "
                            f"en trop {sorted(set(lignes) - set(CLES_PLAN))}")
    try:
        entiers = {k: int(lignes[k]) for k in ("generations", "cartes_par_proposeur", "m_e_bh")}
        reels = {k: float(lignes[k].replace(",", ".")) for k in ("plafond_modeles_usd", "plafond_kimi_usd", "plafond_argon_usd",
                                                                 "plafond_machine_usd", "duree_h")}
    except ValueError:
        raise BoucleRefusee("plan-gele-v65 : générations, cartes, m, plafonds et durée numériques") from None
    if entiers["generations"] != GENERATIONS:
        raise BoucleRefusee(f"plan-gele-v65 : generations = {entiers['generations']} ; le code v65 gèle {GENERATIONS} (D2)")
    exiger_bras_reel_seul(lignes["bras"])
    if not 1 <= entiers["cartes_par_proposeur"] <= 6 or entiers["m_e_bh"] != m_impose(entiers["cartes_par_proposeur"]):
        raise BoucleRefusee(f"plan-gele-v65 : cartes par proposeur dans [1 ; 6] et m = 2 × cartes + 10 (brouillon § 6 : 22 pour 6) ; "
                            f"lus {entiers['cartes_par_proposeur']} et {entiers['m_e_bh']}")
    if any(not math.isfinite(v) or v <= 0 for v in reels.values()):
        raise BoucleRefusee("plan-gele-v65 : plafonds et durée réels finis > 0")
    if round(reels["plafond_kimi_usd"] * 100) + round(reels["plafond_argon_usd"] * 100) != round(reels["plafond_modeles_usd"] * 100):
        raise BoucleRefusee("plan-gele-v65 : parts des relais (Kimi + Argon) ≠ plafond des modèles (au centime)")
    if reels["duree_h"] != T.DUREE_ETAGE_1_H:
        raise BoucleRefusee(f"plan-gele-v65 : duree_h = {lignes['duree_h']} ; le code gèle {T.DUREE_ETAGE_1_H:g} h (R-1294)")
    if lignes["d9"] != "mecanique":
        raise BoucleRefusee("plan-gele-v65 : d9 = mecanique (gardien mécanique, aucun juge à modèle)")
    for k in ("configuration_sha256", "monde_sha256", "heritage_depart_sha256", "jeu_plante_sha256"):
        if not SHA.match(lignes[k]):
            raise BoucleRefusee(f"plan-gele-v65 : {k} = 64 caractères hexadécimaux")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise BoucleRefusee("plan-gele-v65 : go = GO-AAAA-MM-JJ-NN")
    return dict(entiers, **reels, bras=lignes["bras"], d9="mecanique", **{k: lignes[k] for k in (
        "configuration_sha256", "go", "monde_sha256", "heritage_depart_sha256", "jeu_plante_sha256")})


def exiger_bras_reel_seul(option):
    """Garde 20 (D1) : un seul bras joué, le bras réel ; toute autre option (bras de référence demandés) → refus, code 2."""
    if option != OPTION_BRAS:
        raise BrasRefuse(f"bras {option!r} : le code v65 joue le bras réel seul (« {OPTION_BRAS} », décision D1) ; les bras de "
                         "référence exigent un autre code et un autre devis")
    return (BRAS,)


# --- M1 : héritage de départ ----------------------------------------------------------------------------------------------------


def objet_heritage_depart(k1):
    return {"version": VERSION_HERITAGE, "generation": 0,
            "lois": {NOM_DEPART: {"loi": k1, "statut": STATUT_DECLARE}},
            "regle": ("génération 0 déclarée, scellée par son empreinte dans le texte scellé de la course : la loi K1 est connue "
                      "et déclarée d'avance (aucun test de mort) ; elle est membre du nul de toute loi jugée en génération 1 et "
                      "visible des proposeurs ; aucune autre loi")}


def octets_heritage_depart(k1):
    """Les octets du fichier d'héritage de départ (format des fichiers scellés du pôle : JSON indenté, clés triées)."""
    return (json.dumps(objet_heritage_depart(k1), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _egales(a, b):
    try:
        return json_canonique(a) == json_canonique(b)
    except (TypeError, ValueError):
        return False


def lire_heritage_depart(chemin, texte, jeu=None):
    """M1, garde 17 : l'héritage de la génération 1, accepté seulement si l'empreinte des octets lus est le
    `heritage_depart_sha256` du plan du texte passé (aucun repli) ; fichier régulier, version, génération 0, la seule loi K1
    « connue, déclarée », loi servable ; si `jeu` est donné, K1 n'est égale à aucune loi vraie ni à aucun cas d'instrument (une
    loi plantée dans l'héritage). Rend l'héritage au format de `boucle_fermee_v59` (archive {K1}, retenues vides)."""
    attendue = lire_plan(texte)["heritage_depart_sha256"]
    try:
        st = os.lstat(chemin)
    except OSError as e:
        raise HeritageDepartRefuse(f"héritage de départ absent ({chemin}) : {type(e).__name__}") from None
    if not stat.S_ISREG(st.st_mode):
        raise HeritageDepartRefuse(f"héritage de départ : pas un fichier régulier (lien ou autre) : {chemin}")
    with open(chemin, "rb") as f:
        octets = f.read()
    sha = hashlib.sha256(octets).hexdigest()
    if sha != attendue:
        raise HeritageDepartRefuse(f"héritage de départ d'empreinte {sha[:16]}… ≠ celle du texte scellé {attendue[:16]}… : refus, aucun repli")
    try:
        obj = json.loads(octets.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise HeritageDepartRefuse(f"héritage de départ illisible ({type(e).__name__})") from None
    if not isinstance(obj, dict) or obj.get("version") != VERSION_HERITAGE or obj.get("generation") != 0:
        raise HeritageDepartRefuse("héritage de départ : version « heritage-depart-v65 » et génération 0 exigées")
    lois = obj.get("lois")
    if not isinstance(lois, dict) or sorted(lois) != [NOM_DEPART]:
        raise HeritageDepartRefuse(f"héritage de départ : la seule loi {NOM_DEPART} exigée (trouvées {sorted(lois or {})})")
    entree = lois[NOM_DEPART]
    if not isinstance(entree, dict) or set(entree) != {"loi", "statut"} or entree["statut"] != STATUT_DECLARE:
        raise HeritageDepartRefuse(f"héritage de départ : {NOM_DEPART} marquée « {STATUT_DECLARE} » exigée")
    motif = T.verifier_loi_servable(entree["loi"])
    if motif:
        raise HeritageDepartRefuse(f"héritage de départ : loi {NOM_DEPART} non servable : {motif}")
    if jeu is not None:
        plantees = dict(jeu["vraies"], **{n: e["loi"] for n, e in jeu["instruments"].items()})
        egales = sorted(n for n, l in plantees.items() if _egales(l, entree["loi"]))
        if egales:
            raise HeritageDepartRefuse(f"héritage de départ : loi plantée dans l'héritage ({egales}) : refus")
    return {"version": bf.VERSION, "generation_lue": 0, "bilan_sha256": sha, "retenues": [], "archive": {NOM_DEPART: entree["loi"]},
            "empreintes_lues": {"heritage_depart": sha}, "declarees": {NOM_DEPART: STATUT_DECLARE}}


def lire_heritage_v65(dossier_generation, sha256_bilan, archive_precedente, depart):
    """Lecture du bilan d'une génération (par la génération 2, puis lecture finale) : la lecture vérifiée v59 (sceaux, empreintes,
    contre-vérification des retenues), puis l'archive lue doit être **exactement** l'archive contre laquelle cette génération a
    jugé (`archive_precedente` : {K1} pour la génération 1) plus les lois de ses retenues, et K1 y être inchangée ; sinon
    `HeritageRefuse`. Rend l'héritage v59 augmenté des lois déclarées."""
    h = bf.lire_heritage(dossier_generation, sha256_bilan)
    attendue = dict(archive_precedente)
    attendue.update({i: h["archive"].get(i) for i in h["retenues"]})
    if not _egales(h["archive"], attendue):
        raise bf.HeritageRefuse(f"archive lue ≠ archive précédente ∪ retenues ({sorted(h['archive'])} contre {sorted(attendue)}) : refus")
    if any(not _egales(h["archive"].get(n), l) for n, l in depart["archive"].items()):
        raise bf.HeritageRefuse("archive lue : loi de départ (K1) absente ou altérée : refus")
    h["declarees"] = dict(depart.get("declarees") or {})
    return h


# --- M2 : jeu planté ------------------------------------------------------------------------------------------------------------


def jeu_plante_du_brouillon(monde, k1):
    """Le jeu planté du brouillon 1 (§ 3.3, 3.4, 3.6), construit depuis la loi du monde L* et K1 : sert à écrire le bloc du texte
    (le texte fait foi ; la course lit le bloc, jamais cette fonction)."""
    L = copy.deepcopy(monde["loi"])
    uniforme = {"type": "fixe", "probas": [1.0, 1.0, 1.0]}
    aveugle = {"type": "fixe", "probas": [0.3, 0.4, 0.3]}
    v2 = {"type": "softmax", "poids": [[0.0, ligne[1]] for ligne in L["poids"]], "biais": list(L["biais"])}
    k = copy.deepcopy(k1)
    return {"version": VERSION_JEU,
            "vraies": {"V1": L, "V2": v2, "V3": {"type": "transformee", "base": L, "puissance": 0.08},
                       "V4": {"type": "melange", "composantes": [L, uniforme], "poids": [0.15, 0.85]}},
            "fausses": {"F1": {"loi": k, "ligne_du_banc": "T17s"},
                        "F2": {"loi": {"type": "melange", "composantes": [k, uniforme], "poids": [0.8, 0.2]}, "ligne_du_banc": "T03u"},
                        "F3": {"loi": {"type": "melange", "composantes": [k, aveugle], "poids": [0.8, 0.2]}, "ligne_du_banc": "T03b"},
                        "F4": {"loi": {"type": "transformee", "base": k, "puissance": 1.2, "inclinaison": [0.0, 0.05, -0.05]},
                               "ligne_du_banc": "T05s"}},
            "instruments": {"T-ELIM": {"loi": {"type": "transformee", "base": L, "puissance": 1.25}, "seuil": T.SEUIL_T_ELIM},
                            "T-MAL": {"loi": L, "sans_statistique": True}}}


def bloc_jeu_plante(jeu):
    """Le bloc du texte : marqueurs, JSON canonique dans un bloc ```json (une seule ligne : c'est elle qui est lue à l'octet)."""
    return DEBUT_JEU + "\n```json\n" + json_canonique(jeu).decode("utf-8") + "\n```\n" + FIN_JEU


def _uniforme(loi):
    p = loi.get("probas") if isinstance(loi, dict) else None
    return isinstance(p, list) and len(p) == T.K and p[0] > 0 and all(x == p[0] for x in p)


def classer_couverte(loi, connues):
    """La ligne du banc des tricheurs v8 dont `loi` relève dans la classe **couverte** relativement aux lois connues `connues`
    ({identifiant: loi}), ou None (hors de la classe couverte, ou forme non reconnue). Couvert (docstring de `pole/nul_v8.py`) :
    une loi connue seule (T17s) ; un mélange dont chaque composante est une loi connue ou une loi aveugle fixe, une loi connue au
    moins (T01, T03u, T03b) ; une loi connue tempérée et/ou inclinée, sans autre étape (T05s). Non couvert : par morceaux,
    produits, compositions d'étapes (mélange aveugle puis puissance…), oscillation, lois inconnues du pôle."""
    lc = list((connues or {}).values())
    if not lc or not isinstance(loi, dict):
        return None
    if any(_egales(loi, k) for k in lc):
        return "T17s"
    if loi.get("type") == "melange":
        comps = loi.get("composantes")
        if not isinstance(comps, list) or len(comps) < 2:
            return None
        connues_ici = [c for c in comps if any(_egales(c, k) for k in lc)]
        fixes = [c for c in comps if not any(_egales(c, k) for k in lc) and isinstance(c, dict) and c.get("type") == "fixe"]
        if not connues_ici or len(connues_ici) + len(fixes) != len(comps):
            return None
        if not fixes:
            return "T01"
        return "T03u" if all(_uniforme(f) for f in fixes) else "T03b"
    if loi.get("type") == "transformee":
        etapes = set(loi) - {"type", "base"}
        if any(_egales(loi.get("base"), k) for k in lc) and etapes and etapes <= {"puissance", "inclinaison"}:
            return "T05s"
    return None


def verifier_jeu(jeu, archive_depart):
    """Structure exacte du jeu (V1 à V4, F1 à F4, T-ELIM, T-MAL), lois servables, fausses dans la classe couverte relativement à
    l'archive de départ et à leur ligne du banc déclarée, T-ELIM au seuil « au moins 2,0 », T-MAL sans statistique."""
    if not isinstance(jeu, dict) or set(jeu) != {"version", "vraies", "fausses", "instruments"} or jeu["version"] != VERSION_JEU:
        raise JeuPlanteRefuse(f"jeu planté : clés version, vraies, fausses, instruments et version « {VERSION_JEU} » exigées")
    for groupe, noms in (("vraies", VRAIES), ("fausses", FAUSSES), ("instruments", INSTRUMENTS)):
        if not isinstance(jeu[groupe], dict) or tuple(sorted(jeu[groupe])) != tuple(sorted(noms)):
            raise JeuPlanteRefuse(f"jeu planté incomplet ou en trop : {groupe} {sorted(jeu[groupe]) if isinstance(jeu[groupe], dict) else jeu[groupe]!r}, "
                                  f"attendues {list(noms)}")
    lois = dict(jeu["vraies"])
    for n in FAUSSES:
        e = jeu["fausses"][n]
        if not isinstance(e, dict) or set(e) != {"loi", "ligne_du_banc"} or e["ligne_du_banc"] not in LIGNES_DU_BANC:
            raise JeuPlanteRefuse(f"jeu planté : {n} = {{loi, ligne_du_banc ∈ {sorted(LIGNES_DU_BANC)}}} exigé")
        lois[n] = e["loi"]
    attendus = {"T-ELIM": ({"loi", "seuil"}, "seuil", T.SEUIL_T_ELIM), "T-MAL": ({"loi", "sans_statistique"}, "sans_statistique", True)}
    for n, (cles, champ, valeur) in attendus.items():
        e = jeu["instruments"][n]
        if not isinstance(e, dict) or set(e) != cles or e[champ] != valeur or type(e[champ]) is not type(valeur):
            raise JeuPlanteRefuse(f"jeu planté : {n} = {sorted(cles)} avec {champ} = {valeur!r} exigé")
        lois[n] = e["loi"]
    for n, l in sorted(lois.items()):
        motif = T.verifier_loi_servable(l)
        if motif:
            raise JeuPlanteRefuse(f"jeu planté : loi {n} non servable : {motif}")
    for n in FAUSSES:
        ligne = classer_couverte(jeu["fausses"][n]["loi"], archive_depart)
        if ligne is None:
            raise FausseHorsClasse(f"jeu planté : fausse {n} hors de la classe que le nul v8 couvre (relativement à l'archive de "
                                   f"départ {sorted(archive_depart)}) : refus (GO-2026-11-07-11, brouillon § 3.4)")
        if ligne != jeu["fausses"][n]["ligne_du_banc"]:
            raise JeuPlanteRefuse(f"jeu planté : fausse {n} déclarée {jeu['fausses'][n]['ligne_du_banc']}, de forme {ligne}")
    return True


def lire_jeu_plante(texte, archive_depart):
    """M2, garde 19 : le bloc `jeu-plante-v65` du texte (exactement un), un bloc ```json d'une ligne, JSON **canonique** (les octets
    lus sont ceux que l'on hache : aucune variante d'écriture), d'empreinte égale au `jeu_plante_sha256` du plan, structure et
    classe vérifiées (`verifier_jeu`). Rend (jeu, empreinte, octets)."""
    bloc = bloc_unique(texte, DEBUT_JEU, FIN_JEU, "jeu-plante-v65", JeuPlanteRefuse)
    m = re.fullmatch(r"\n```json\n([^\n]+)\n```\n", bloc)
    if not m:
        raise JeuPlanteRefuse("jeu planté : un bloc ```json d'une seule ligne exigé entre les marqueurs")
    octets = m.group(1).encode("utf-8")
    try:
        jeu = json.loads(octets.decode("utf-8"))
    except ValueError as e:
        raise JeuPlanteRefuse(f"jeu planté illisible ({type(e).__name__})") from None
    try:
        canonique = json_canonique(jeu)
    except (TypeError, ValueError):
        canonique = None
    if canonique != octets:
        raise JeuPlanteRefuse("jeu planté non canonique (clés triées, séparateurs compacts) : il est lu à l'octet")
    sha = hashlib.sha256(octets).hexdigest()
    attendue = lire_plan(texte)["jeu_plante_sha256"]
    if sha != attendue:
        raise JeuPlanteRefuse(f"jeu planté d'empreinte {sha[:16]}… ≠ jeu_plante_sha256 du plan {attendue[:16]}… (garde 19) : refus")
    verifier_jeu(jeu, archive_depart)
    return jeu, sha, octets


def exiger_jeu_conforme(jeu, octets):
    """Garde 19 : les lois que la course plante sont égales à l'octet au bloc lu dans le texte ; sinon refus (code 2)."""
    if json_canonique(jeu) != octets:
        raise JeuPlanteRefuse("garde 19 : le jeu planté utilisé ≠ le bloc du texte scellé (une loi changée) : refus")
    return True


def _plantee(nom, loi, racine, tache, seuil=T.SEUIL_TEST, sans_statistique=False):
    reel = "P-" + hashlib.sha256(f"{racine}|{tache}|{nom}".encode("utf-8")).hexdigest()[:12]
    servi = T.identifiant_opaque(racine, tache, reel)
    return nom, reel, T.carte_servie(servi, copy.deepcopy(loi), SOURCE_PLANTEE, seuil=seuil, sans_statistique=sans_statistique)


def plantees_generation_1(jeu, racine, tache):
    """V1 à V4, F1 à F4, T-ELIM (seuil « au moins 2,0 »), T-MAL (sans statistique) : (nom, identifiant réel, carte servie)."""
    out = [_plantee(n, jeu["vraies"][n], racine, tache) for n in VRAIES]
    out += [_plantee(n, jeu["fausses"][n]["loi"], racine, tache) for n in FAUSSES]
    out.append(_plantee("T-ELIM", jeu["instruments"]["T-ELIM"]["loi"], racine, tache, seuil=T.SEUIL_T_ELIM))
    out.append(_plantee("T-MAL", jeu["instruments"]["T-MAL"]["loi"], racine, tache, sans_statistique=True))
    return out


def plantees_generation_2(jeu, copies, racine, tache):
    """F1 à F4 replantées, puis les copies renommées des retenues (ligne T17s) ; V1 à V4 et T-ELIM ne sont pas replantées."""
    return [_plantee(n, jeu["fausses"][n]["loi"], racine, tache) for n in FAUSSES] + \
           [_plantee(nom, loi, racine, tache) for nom, _source, loi in copies]


def copies_de_la_selection(heritage, log_e):
    """Garde 21 : (nom, source, loi) des copies renommées des quatre premières retenues par log e (identifiant en cas d'égalité),
    lois prises **dans l'héritage lu** ; aucune si rien n'est retenu."""
    retenues = list(heritage.get("retenues") or [])
    cle = (lambda i: (-(log_e.get(i) if isinstance(log_e.get(i), (int, float)) else -math.inf), i))
    return [(f"C{k}", src, copy.deepcopy(heritage["archive"][src])) for k, src in enumerate(sorted(retenues, key=cle)[:COPIES_MAX], 1)]


def exiger_copies_conformes(copies, heritage, log_e):
    """Garde 21 : chaque copie vient d'une retenue de l'héritage lu, porte sa loi, et les sources sont les quatre premières par
    log e ; sinon `CopieRefusee` (arrêt)."""
    retenues = set(heritage.get("retenues") or [])
    for nom, src, loi in copies:
        if src not in retenues:
            raise CopieRefusee(f"copie {nom} d'une carte non retenue ({src}) : refus (garde 21)")
        if not _egales(loi, heritage["archive"].get(src)):
            raise CopieRefusee(f"copie {nom} : loi ≠ loi retenue de {src} dans l'héritage lu : refus (garde 21)")
    attendues = [(n, s) for n, s, _ in copies_de_la_selection(heritage, log_e)]
    if [(n, s) for n, s, _ in copies] != attendues:
        raise CopieRefusee(f"copies {[(n, s) for n, s, _ in copies]} ≠ quatre premières retenues par log e {attendues} (garde 21)")
    return True


# --- M3 : jugement avec l'archive ---------------------------------------------------------------------------------------------


def membres_attendus(archive):
    """Nombre de membres d'archive du nul v8 qu'impose `archive` (0 pour une archive vide)."""
    return len(nul_v8.membres_archive_v8(dict(archive), None, T.K, T.DIM)) if archive else 0


def exiger_archive_des_plantees(detail, identifiants, archive):
    """Garde 18 : chaque loi plantée a été jugée avec le nombre de membres d'archive qu'impose l'archive de sa génération ; sinon
    `ArchiveDesPlanteesAbsente` (arrêt, code 3)."""
    attendu = membres_attendus(archive)
    ecarts = sorted(i for i in identifiants if detail.get(i, {}).get("membres_d_archive") != attendu)
    if ecarts:
        raise ArchiveDesPlanteesAbsente(f"loi(s) plantée(s) jugée(s) sans l'archive de leur génération ({ecarts} ; membres attendus "
                                        f"{attendu}, lus {[detail.get(i, {}).get('membres_d_archive') for i in ecarts]}) : arrêt (garde 18)")
    return attendu


def juger_v65(cartes, plantees, monde, archive, racine, tache, m):
    """Rend (promues cartes, promues plantées, détail, m). Cartes : `tour_ferme_v64.juger` (nul v8 avec l'archive, e-BH de la famille
    des cartes à m fixé). Lois plantées ((nom, carte)) : nul v8 **avec la même archive**, hors famille, seuil log(m/α) (M3) ;
    garde 18 vérifiée sur chacune."""
    promues, _, detail, m_lu = T.juger(cartes, [], monde, archive, racine, tache, m)
    seuil = math.log(m / ALPHA)
    archive_plantees = archive  # M3 : l'archive de jugement de la génération (la v64 passait {})
    promues_plantees = []
    for nom, c in plantees:
        ev, d = A.juger_carte(c["loi_predictive"], monde, archive_plantees, racine, f"{tache}|plantee={c['identifiant']}")
        traj = ev["trajectoire_log_w"]
        log_e = -math.inf if ev.get("marge_atteinte") is False else next((v for v in traj if v >= seuil), traj[-1])
        promue = bool(ev["promue"]) and log_e >= seuil
        detail[c["identifiant"]] = dict(d, plantee=nom, promue_seule=bool(ev["promue"]), promue=promue,
                                        log_e=None if math.isinf(log_e) else round(log_e, 6),
                                        log_richesse_max=round(ev["log_richesse_max"], 6), regle="hors famille, seuil log(m/α), archive de la génération")
        if promue:
            promues_plantees.append(c["identifiant"])
    exiger_archive_des_plantees(detail, [c["identifiant"] for _, c in plantees], archive)
    return promues, promues_plantees, detail, m_lu


# --- gardes de dépense ------------------------------------------------------------------------------------------------------------


class CompteurV65(T.Compteur):
    """Le compteur de la v64 (plafond des modèles, part de chaque relais, durée ; arrêt dès qu'un plafond est franchi), plus :
    `verifier_avant_appel` (aucun appel dont la borne dépasse la part restante de son relais ou le plafond restant des modèles ;
    part ou plafond épuisé → aucun appel) et le plafond de la machine, compté à part (`ajouter_machine`)."""

    def __init__(self, plafond_modeles_usd, duree_max_s, parts, plafond_machine_usd, horloge=time.time):
        if not parts or set(parts) != {"kimi", "argon"}:
            raise BoucleRefusee(f"parts des relais kimi et argon exigées (reçues {parts!r})")
        if round(sum(float(v) for v in parts.values()) * 100) != round(float(plafond_modeles_usd) * 100):
            raise BoucleRefusee("parts des relais ≠ plafond des modèles (au centime)")
        super().__init__(plafond_modeles_usd, duree_max_s, parts, horloge)
        self.plafond_machine_usd, self.machine_usd = float(plafond_machine_usd), 0.0

    def verifier_avant_appel(self, relais, borne_usd):
        borne = float(borne_usd)
        reste_part = self.parts.get(relais, 0.0) - self.par_relais.get(relais, 0.0)
        reste = self.plafond_usd - self.usd
        if relais not in self.parts or reste_part <= 1e-9 or reste <= 1e-9 or borne > reste_part + 1e-9 or borne > reste + 1e-9:
            raise PlafondAtteint(f"arrêt au plafond : appel du relais {relais} de borne {borne:.4f} USD non lancé (part restante "
                                 f"{reste_part:.4f} USD, plafond restant des modèles {reste:.4f} USD)")
        self.verifier_duree()

    def ajouter_machine(self, usd):
        self.machine_usd += float(usd)
        if self.machine_usd > self.plafond_machine_usd + 1e-9:
            raise PlafondAtteint(f"plafond de la machine franchi : {self.machine_usd:.4f} USD > {self.plafond_machine_usd} USD")

    def etat(self):
        return dict(super().etat(), plafond_modeles_usd=self.plafond_usd, machine_usd=round(self.machine_usd, 6),
                    plafond_machine_usd=self.plafond_machine_usd)


def exiger_go_cite(go, go_attendu, montant_usd):
    """Aucun appel sans GO cité : `go` est la ligne rendue par `configuration_v56.verifier_go_v56` (identifiant, plafond lu, montant
    requis), à l'identifiant du plan et au montant total (modèles + machine) ; sinon `GoNonCite`."""
    if not isinstance(go, dict) or go.get("identifiant") != go_attendu \
            or abs(float(go.get("montant_requis_usd") or -1) - float(montant_usd)) > 1e-9 \
            or abs(float(go.get("plafond_lu_usd") or -1) - float(montant_usd)) > 1e-9:
        raise GoNonCite(f"aucun appel sans le GO {go_attendu} vérifié au montant de {float(montant_usd):g} USD (reçu {go!r})")
    return True


class AdaptateurSousGo:
    """Enveloppe d'un adaptateur **réel** : avant chaque appel, le GO cité (`exiger_go_cite`) puis la borne de l'appel contre la part
    restante du relais (`CompteurV65.verifier_avant_appel`) ; refus avant d'appeler l'adaptateur enveloppé. Rôles, modèles servis
    permis et description passent tels quels."""

    def __init__(self, adaptateur, relais, go, go_attendu, montant_usd, compteur):
        self.ad, self.relais, self.go, self.go_attendu, self.montant_usd, self.compteur = adaptateur, relais, go, go_attendu, montant_usd, compteur
        self.ROLES_PERMIS = T.roles_permis(adaptateur)

    def lancer(self, role, texte, dossier, budget_usd, max_tours, modele=None):
        exiger_go_cite(self.go, self.go_attendu, self.montant_usd)
        if self.compteur is None:
            raise GoNonCite("aucun appel sans compteur des plafonds")
        self.compteur.verifier_avant_appel(self.relais, budget_usd)
        return self.ad.lancer(role, texte, dossier, budget_usd, max_tours, modele=modele)

    def description(self):
        d = self.ad.description() if hasattr(self.ad, "description") else {}
        return dict(d, sous_go=self.go_attendu, montant_go_usd=self.montant_usd)

    def __getattr__(self, nom):
        if nom == "ad":
            raise AttributeError(nom)
        return getattr(self.ad, nom)


# --- une génération du bras réel ----------------------------------------------------------------------------------------------


def exiger_sans_plantee(heritage, ids_plantes):
    """Garde 7 : aucun identifiant de loi plantée (réel ou servi) dans l'archive ni dans la vue."""
    vue = bf.vue_pour_proposeur(heritage)
    presents = sorted(set(heritage.get("archive") or {}) & ids_plantes) + sorted({x["identifiant"] for x in vue["lois_retenues"]} & ids_plantes)
    if presents:
        raise T.TemoinRetenu(f"loi(s) plantée(s) dans l'archive ou la vue : {presents} : refus")


def _sessions(adaptateur, depuis):
    return [{k: a.get(k) for k in ("role", "relais", "statut", "cout_usd", "rien_envoye")} for a in list(getattr(adaptateur, "appels", []))[depuis:]]


def jouer_generation_v65(dossier, generation, monde, heritage, racine, fabrique_executeur, proposeurs, adaptateur_etage, roles,
                         plan, jeu, compteur, journal, releve, recherche, copies=None, moteur="simule", environnement=None,
                         permis_en_plus=()):
    """Une génération du bras réel : proposition (vue = archive de l'héritage) → gardien → juge (cartes et lois plantées avec
    l'archive de jugement de la génération) → étage des cartes promues ; génération 1 : étage des lois plantées promues, même
    tranche → contre-calcul → sélection (cartes seules) → bilan scellé. Rend (empreinte du bilan, ligne de journal)."""
    tache = f"{VERSION}|bras={BRAS}|generation={generation}"
    archive_jugement = heritage["archive"]
    vue = bf.vue_pour_proposeur(heritage)
    contexte = T.contexte_du_proposeur(monde, vue, racine, tache)
    consigne = T.CONSIGNE_PROPOSEUR.format(n=plan["cartes_par_proposeur"])
    cartes, refusees, reels, enonces, fournisseurs, appels = [], {}, {}, {}, {}, []
    for p in proposeurs:
        recherche["contextes_cherches"] += 1
        recherche["touches"] += T.chercher_loi_plantee(monde, consigne, contexte, f"{tache}|proposeur={p.nom}")
        recherche["episodes_servis"] |= {(e["z"][0], e["z"][1], e["g"]) for e in contexte["episodes_developpement"]}
        compteur.verifier_avant_appel(p.relais, p.budget)  # arrêt au plafond, avant l'appel
        try:
            texte, cout = p.proposer(consigne, contexte, tache)
        except T.ArretTour as e:
            compteur.ajouter(e.cout, "proposeur", p.relais)
            raise
        compteur.ajouter(cout, "proposeur", p.relais)
        props, motif = T.extraire_propositions(texte)
        appels.append({"proposeur": p.nom, "relais": p.relais, "cout_usd": cout, "propositions": len(props),
                       "ignorees_au_dela_du_maximum": max(0, len(props) - plan["cartes_par_proposeur"]), "motif": motif})
        for i, prop in enumerate(props[:plan["cartes_par_proposeur"]]):
            ident_reel = f"G{generation}-{p.nom}-{i + 1:02d}"
            ident = T.identifiant_opaque(racine, tache, ident_reel)
            reels[ident], fournisseurs[ident] = ident_reel, p.relais
            c, motif_c = T.completer_carte(prop, ident)
            if c is None:
                refusees[ident] = f"gardien mécanique (gabarit) : {motif_c}"
            else:
                enonces[ident] = prop["enonce"]
                cartes.append(c)
    plantees = plantees_generation_1(jeu, racine, tache) if generation == 1 else plantees_generation_2(jeu, copies or [], racine, tache)
    ids_plantes = {reel for _, reel, _ in plantees} | {c["identifiant"] for _, _, c in plantees}
    exiger_sans_plantee(heritage, ids_plantes)
    reels.update({c["identifiant"]: reel for _, reel, c in plantees})
    passees, plantees_passees, plantees_refusees = [], [], {}
    for c in cartes:
        passeport, motif = T.garder(c, {"d9": "mecanique"})
        if passeport is None:
            refusees[c["identifiant"]] = motif
        else:
            passees.append(c)
    for nom, _, c in plantees:
        passeport, motif = T.garder(c, {"d9": "mecanique"})
        if passeport is None:
            plantees_refusees[nom] = motif
        else:
            plantees_passees.append((nom, c))
    promues, promues_plantees, detail, m = juger_v65(passees, plantees_passees, monde, archive_jugement, racine, tache, plan["m_e_bh"])
    par_ident = {c["identifiant"]: c for c in passees}
    par_ident_p = {c["identifiant"]: (nom, c) for nom, c in plantees_passees}
    a_tester_p = promues_plantees if generation == 1 else []  # § 3.7 (iii) : génération 2, cartes réelles seules testées
    # Le jugement entre au relevé **avant** les étages : un arrêt pendant un étage laisse un relevé partiel qui montre déjà une fausse
    # ou une copie promue (C5 avec C2 ou C4 « partielle », § 8 : un arrêt ne masque jamais une brèche) ; verdicts complétés après.
    n_archive = len(archive_jugement)
    releve["vues"].append({"generation": generation, "lois": [x["identifiant"] for x in vue["lois_retenues"]],
                           "sha256": hashlib.sha256(json_canonique(vue)).hexdigest()})
    releve["archives_de_jugement"][str(generation)] = copy.deepcopy(archive_jugement)
    releve["membres_attendus"][str(generation)] = membres_attendus(archive_jugement)
    entrees_c, entrees_p = {}, {}
    for c in passees:
        i = c["identifiant"]
        entrees_c[i] = {"generation": generation, "identifiant": reels[i], "identifiant_servi": i, "fournisseur": fournisseurs.get(i),
                        "gardien": "passe", "promue": i in promues, "verdict": None, "contre_calcul_ok": None, "log_e": detail[i].get("log_e"),
                        "log_richesse_max": detail[i].get("log_richesse_max"), "membres_d_archive": detail[i].get("membres_d_archive"),
                        "retenue": False, "archive_de_jugement": n_archive, "loi": c["loi_predictive"], "enonce": enonces.get(i)}
        releve["cartes"].append(entrees_c[i])
    for i, motif in refusees.items():
        releve["cartes"].append({"generation": generation, "identifiant": reels.get(i, i), "identifiant_servi": i,
                                 "fournisseur": fournisseurs.get(i), "gardien": "refuse", "promue": False, "verdict": None,
                                 "contre_calcul_ok": None, "motif": motif, "retenue": False, "archive_de_jugement": n_archive,
                                 "enonce": enonces.get(i)})
    sources = {nom: src for nom, src, _ in (copies or [])}
    lignes_banc = {n: jeu["fausses"][n]["ligne_du_banc"] for n in FAUSSES}
    for nom, reel, c in plantees:
        i = c["identifiant"]
        d = detail.get(i, {})
        entrees_p[i] = {"generation": generation, "nom": nom, "identifiant": reel, "identifiant_servi": i,
                        "groupe": ("vraie" if nom in VRAIES else "fausse" if nom in FAUSSES else "instrument" if nom in INSTRUMENTS else "copie"),
                        "source": sources.get(nom), "ligne_du_banc": lignes_banc.get(nom, "T17s" if nom in sources else None),
                        "gardien": "refuse" if nom in plantees_refusees else "passe", "motif": plantees_refusees.get(nom),
                        "promue": i in promues_plantees, "promue_seule": d.get("promue_seule"), "testee": i in a_tester_p,
                        "verdict": None, "contre_calcul_ok": None, "log_e": d.get("log_e"), "log_richesse_max": d.get("log_richesse_max"),
                        "membres_d_archive": d.get("membres_d_archive"), "loi": c["loi_predictive"]}
        releve["plantees"].append(entrees_p[i])
    executeur, description_bac = fabrique_executeur()
    avant = len(getattr(adaptateur_etage, "appels", []))
    resume, chemin_sel, sha_sel, tranche, cc = T.jouer_etage(
        os.path.join(dossier, bf.DOSSIER_ETAGE), [par_ident[i] for i in promues], {i: c["loi_predictive"] for i, c in par_ident.items()},
        monde, racine, tache, executeur, adaptateur_etage, roles, compteur, journal, moteur=moteur, environnement=environnement,
        permis_en_plus=permis_en_plus)
    sessions_cartes = _sessions(adaptateur_etage, avant)
    executeur_p, _ = fabrique_executeur()
    avant = len(getattr(adaptateur_etage, "appels", []))
    resume_p, _, sha_sel_p, _, cc_p = T.jouer_etage(
        os.path.join(dossier, DOSSIER_ETAGE_PLANTEES), [par_ident_p[i][1] for i in a_tester_p],
        {i: c["loi_predictive"] for i, (_, c) in par_ident_p.items()}, monde, racine, tache, executeur_p, adaptateur_etage, roles,
        compteur, journal, tranche=tranche, moteur=moteur, environnement=environnement, permis_en_plus=permis_en_plus)
    sessions_plantees = _sessions(adaptateur_etage, avant)
    verdicts, verdicts_p = T._verdicts(resume), T._verdicts(resume_p)
    with open(chemin_sel, encoding="utf-8") as f:
        retenues = json.load(f)["retenues"]
    if set(retenues) & set(par_ident_p) or set(retenues) & ids_plantes:  # garde 7
        raise T.TemoinRetenu(f"loi plantée dans la sélection de {tache} : refus")
    for i, e in entrees_c.items():
        e.update(verdict=verdicts.get(i), contre_calcul_ok=cc[i]["ok"] if i in cc else None, retenue=i in retenues)
    for i, e in entrees_p.items():
        e.update(verdict=verdicts_p.get(i), contre_calcul_ok=cc_p[i]["ok"] if i in cc_p else None)
    comptes = {"proposees": len(cartes) + len([r for r in refusees if r not in par_ident]), "refusees_au_gardien": len(refusees),
               "jugees": len(passees), "m_e_bh": m, "promues": len(promues), "testees": len(verdicts), "retenues": len(retenues),
               "plantees_promues": len(promues_plantees), "plantees_testees": len(verdicts_p), "appels_proposeurs": appels}
    graines = {"tache": tache, "par_carte": {i: d["graines"] for i, d in detail.items()}}
    sha_bilan = bf.ecrire_bilan_generation(dossier, generation=generation, bras=BRAS, cartes=passees, resume_etage=resume,
                                           chemin_selection=chemin_sel, sha_selection=sha_sel, archive_precedente=heritage["archive"],
                                           heritage_lu=heritage, comptes=comptes, graines=graines)
    releve["sessions"][str(generation)] = {"cartes": sessions_cartes, "plantees": sessions_plantees}
    ligne = {"evenement": "generation", "bras": BRAS, "generation": generation, "heritage_lu": heritage.get("bilan_sha256"),
             "archive_lue": sorted(heritage["archive"]), "archive_de_jugement": sorted(archive_jugement), "refusees_au_gardien": refusees,
             "plantees_refusees": plantees_refusees, "promues": promues, "plantees_promues": promues_plantees, "correspondance": reels,
             "verdicts": verdicts, "verdicts_plantees": verdicts_p, "retenues": retenues, "comptes": comptes,
             "bac_a_sable": description_bac.get("nom"), "factice": description_bac.get("factice"), "selection_sha256": sha_sel,
             "selection_plantees_sha256": sha_sel_p, "bilan_sha256": sha_bilan,
             "log_e_des_cartes": {i: detail[i].get("log_e") for i in par_ident},
             "juge": {i: {k: d.get(k) for k in ("promue", "promue_seule", "log_richesse_max", "log_e", "membres_d_archive",
                                                "empreinte_engagement", "plantee")} for i, d in detail.items()},
             "depense": compteur.etat()}
    journal.append(ligne)
    return sha_bilan, ligne


def chercher_dans_un_texte_d_etage(monde, texte, loi_gelee, ou):
    """§ 7.6 : touches des paramètres de L* (exacts ou à deux décimales) dans une consigne de l'étage, **hors** de la loi gelée servie
    au test de mort (que l'expérimentateur doit voir) : la loi gelée est retirée du texte (forme canonique et forme échappée dans
    une chaîne JSON) avant la recherche. Rend (touches hors de la loi gelée, touches de la loi gelée seule)."""
    canon = json_canonique(loi_gelee).decode("utf-8") if loi_gelee is not None else None
    reste = texte
    if canon:
        for forme in (json.dumps(canon, ensure_ascii=False)[1:-1], canon):
            reste = reste.replace(forme, " ")
    hors = T.chercher_loi_plantee(monde, reste, {}, ou)
    dans = T.chercher_loi_plantee(monde, canon or "", {}, ou + "|loi-gelee")
    return hors, dans


def chercher_dans_l_etage(sortie, monde, lois_par_ident):
    """§ 7.6 (mesure sans issue) : chaque `consigne.md` de l'expérimentateur et du vérificateur sous `sortie` ; la loi gelée est
    celle de la fiche du dossier (`tests-de-mort/<identifiant servi>/…`)."""
    out = {"consignes_cherchees": 0, "touches_hors_loi_gelee": [], "touches_dans_la_loi_gelee": 0}
    for base, _dirs, noms in sorted(os.walk(sortie)):
        if "consigne.md" not in noms or not (os.sep + "experimentateur" in base or os.sep + "lecteur" in base):
            continue
        morceaux = base.split(os.sep)
        ident = next((morceaux[k + 1] for k in range(len(morceaux) - 1) if morceaux[k] == "tests-de-mort"), None)
        with open(os.path.join(base, "consigne.md"), encoding="utf-8") as f:
            texte = f.read()
        hors, dans = chercher_dans_un_texte_d_etage(monde, texte, lois_par_ident.get(ident), os.path.relpath(base, sortie))
        out["consignes_cherchees"] += 1
        out["touches_hors_loi_gelee"] += hors
        out["touches_dans_la_loi_gelee"] += len(dans)
    return out


def jouer_boucle(sortie, *, monde, racine, plan, jeu, depart, proposeurs, adaptateur_etage, roles, fabrique_executeur, compteur,
                 moteur="simule", environnement=None, permis_en_plus=()):
    """Le bras réel seul, deux générations. Génération 1 : héritage de départ ; génération 2 : bilan de la génération 1 lu par
    `lire_heritage_v65`, copies des retenues ; lecture finale du bilan de la génération 2. Rend (relevé, journal) ; toute exception
    lève `ArretTour` avec le relevé partiel (C12)."""
    exiger_bras_reel_seul(plan["bras"])
    T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                               (roles["verificateur"][0], roles["familles"]["verificateur"]))
    adaptateur_etage.parts = dict(compteur.parts)
    journal = []
    releve = {"version": VERSION, "bras": OPTION_BRAS, "arret": None, "generations_jouees": [], "entropie_racine": str(racine),
              "monde_sha256": monde.get("sha256"),
              "heritage_depart": {"sha256": depart["bilan_sha256"], "archive": copy.deepcopy(depart["archive"]),
                                  "declarees": dict(depart["declarees"])},
              "jeu_plante_sha256": hashlib.sha256(json_canonique(jeu)).hexdigest(), "jeu_plante": copy.deepcopy(jeu),
              "boucle": {"incidents": [], "lectures": []}, "cartes": [], "plantees": [], "copies": [], "vues": [],
              "archives_de_jugement": {}, "membres_attendus": {}, "sessions": {}, "retenues": {}, "plan": dict(plan),
              "moteur_etage": moteur, "alpha": ALPHA}
    recherche = {"contextes_cherches": 0, "touches": [], "episodes_servis": set()}
    prec = None
    try:
        log_e_g1 = {}
        for g in range(1, GENERATIONS + 1):
            d = os.path.join(sortie, f"bras-{BRAS}", f"generation-{g}")
            os.makedirs(d)
            copies = None
            if g == 1:
                heritage = depart
            else:
                try:
                    heritage = lire_heritage_v65(prec["dossier"], prec["sha"], prec["archive"], depart)
                except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:
                    releve["boucle"]["incidents"].append({"generation": g, "type": type(e).__name__, "motif": str(e)[:300]})
                    raise T.ArretTour(f"héritage refusé ({type(e).__name__}) : arrêt") from e
                releve["boucle"]["lectures"].append({"generation": g, "attendu": prec["sha"], "lu": heritage["bilan_sha256"],
                                                     "retenues_lues": list(heritage["retenues"]), "archive_lue": sorted(heritage["archive"])})
                journal.append({"evenement": "heritage-lu", "generation": g, "bilan_sha256": heritage["bilan_sha256"],
                                "archive": sorted(heritage["archive"])})
                copies = copies_de_la_selection(heritage, log_e_g1)
                exiger_copies_conformes(copies, heritage, log_e_g1)
                releve["copies"] = [{"nom": n, "source": s, "loi": l} for n, s, l in copies]
            sha, ligne = jouer_generation_v65(d, g, monde, heritage, racine, fabrique_executeur, proposeurs, adaptateur_etage, roles,
                                              plan, jeu, compteur, journal, releve, recherche, copies, moteur, environnement,
                                              permis_en_plus)
            releve["generations_jouees"].append(g)
            releve["retenues"][str(g)] = list(ligne["retenues"])
            if g == 1:
                log_e_g1 = dict(ligne["log_e_des_cartes"])
            prec = {"dossier": d, "sha": sha, "archive": heritage["archive"]}
        try:
            fin = lire_heritage_v65(prec["dossier"], prec["sha"], prec["archive"], depart)
        except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:
            releve["boucle"]["incidents"].append({"generation": "finale", "type": type(e).__name__, "motif": str(e)[:300]})
            raise T.ArretTour(f"héritage final refusé ({type(e).__name__}) : arrêt") from e
        releve["boucle"]["lectures"].append({"generation": "finale", "attendu": prec["sha"], "lu": fin["bilan_sha256"],
                                             "retenues_lues": list(fin["retenues"]), "archive_lue": sorted(fin["archive"])})
        journal.append({"evenement": "heritage-final-lu", "bilan_sha256": prec["sha"], "archive": sorted(fin["archive"])})
    except T.ArretTour as e:
        releve["arret"] = f"{type(e).__name__} : {e}"
    except Exception as e:  # noqa: BLE001 — C12 : toute exception d'une génération est un arrêt scellé, motif et type dits
        releve["arret"] = f"{type(e).__name__} : {str(e)[:500]}"
        releve["boucle"]["incidents"].append({"type": type(e).__name__, "motif": str(e)[:300]})
    if releve["arret"]:
        journal.append({"evenement": "arret", "motif": releve["arret"], "depense": compteur.etat()})
    tranches = set()
    for g in releve["generations_jouees"]:
        tranches |= T.lignes_de_tranche(monde, racine, f"{VERSION}|bras={BRAS}|generation={g}")
    releve["recherche_loi_plantee"] = {"contextes_cherches": recherche["contextes_cherches"], "parametres_de_la_loi_plantee": 9,
                                       "formes": ["exacte", "deux décimales"], "touches": recherche["touches"],
                                       "lignes_de_tranche_dans_les_contextes": [list(x) for x in sorted(recherche["episodes_servis"] & tranches)]}
    try:
        lois_par_ident = {x["identifiant_servi"]: x.get("loi") for x in releve["cartes"] + releve["plantees"]}
        releve["recherche_loi_plantee"]["etage"] = chercher_dans_l_etage(sortie, monde, lois_par_ident)
    except Exception as e:  # noqa: BLE001 — mesure sans issue : son échec est dit, jamais tu
        releve["recherche_loi_plantee"]["etage"] = {"erreur": f"{type(e).__name__} : {str(e)[:200]}"}
    releve["depense"] = compteur.etat()
    if releve["arret"]:
        raise T.ArretTour(releve["arret"], {"releve": releve, "journal": journal})
    return releve, journal


def manifeste_boucle(**champs):
    """Manifeste R9 : celui du tour fermé v64 (commit, versions, bwrap, évaluateur, consigne, grammaire), version v65, règle des
    graines de la v65."""
    m = T.manifeste_tour(**champs)
    m.update(version=VERSION, ordre_des_bras=[BRAS], bras=OPTION_BRAS,
             regle_des_graines=f"SeedSequence(E, spawn_key=(cle_de_tache(tâche),)) ; tâches « {VERSION}|bras=reel|generation=<g>|… »")
    return m


__all__ = ("VERSION", "GENERATIONS", "OPTION_BRAS", "VRAIES", "FAUSSES", "INSTRUMENTS", "COPIES_MAX", "STATUT_DECLARE", "CLES_PLAN",
           "BoucleRefusee", "HeritageDepartRefuse", "JeuPlanteRefuse", "FausseHorsClasse", "BrasRefuse", "GoNonCite",
           "ArchiveDesPlanteesAbsente", "CopieRefusee", "PlafondAtteint", "lire_plan", "exiger_bras_reel_seul",
           "objet_heritage_depart", "octets_heritage_depart", "lire_heritage_depart", "lire_heritage_v65", "jeu_plante_du_brouillon",
           "bloc_jeu_plante", "classer_couverte", "verifier_jeu", "lire_jeu_plante", "exiger_jeu_conforme", "plantees_generation_1",
           "plantees_generation_2", "copies_de_la_selection", "exiger_copies_conformes", "membres_attendus",
           "exiger_archive_des_plantees", "juger_v65", "CompteurV65", "exiger_go_cite", "AdaptateurSousGo", "jouer_generation_v65",
           "chercher_dans_un_texte_d_etage", "chercher_dans_l_etage",
           "jouer_boucle", "manifeste_boucle", "sha256_fichier")
