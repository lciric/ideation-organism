"""Cœur de la plus petite course réelle de la boucle complète de l'organisme, version 65 (fichier neuf, R12).

Dessin : `preenregistrement-boucle-reelle-organisme-v1-brouillon1.md` (dépôt de travail, sha256 `736e3fd6…`), sections 3, 5 à
10 et 12 ; constats de l'essai à blanc v1 (`journal-essai-a-blanc-v1.md`, `627f7a4c…`, section 4 : M1 à M5). Ce module **ne lit
aucune issue** : il produit le relevé que lit `pole/lecture_boucle_reelle_v65.py` (programme `demonstrations/lire_boucle_reelle_v65.py`).
Il **réutilise sans le modifier** le cœur du tour fermé v64 (`pole/tour_ferme_v64.py` : gardien, gabarit, contexte servi, étage
des tests de mort, contre-calcul, compteur de dépense, doublures) et la boucle fermée v59 (`pole/boucle_fermee_v59.py` : bilan
scellé, `lire_heritage`, vue sans verdict).

Ce qui change par rapport au tour fermé v64 (pièces du brouillon, section 12) :

M1. **Héritage de départ scellé** (« génération 0 ») : un fichier scellé `heritage-depart-v65.json` porte l'archive {K1}, K1
    marquée « connue, déclarée » ; `lire_heritage_depart` ne l'accepte que si son empreinte est celle que porte le texte scellé
    (`heritage_depart_sha256` du plan gelé), si son sceau compagnon est juste, si son archive est exactement celle du jeu planté
    du texte (K1 à l'octet en JSON canonique) et si aucune loi plantée (vraie ou instrument) n'y figure ; sinon
    `HeritageDepartRefuse` (code 2, aucun repli). Il rend un héritage au format de `boucle_fermee_v59.lire_heritage`, que la
    génération 1 lit comme toute autre (vue des proposeurs = {K1} ; archive de jugement = {K1}).
M2. **Jeu planté lu dans le texte scellé** (remplace `TEMOINS` de la v64) : bloc `jeu-plante-v65` (JSON) entre les marques
    `<!-- jeu-plante-v65 : début -->` et `<!-- jeu-plante-v65 : fin -->` ; `lire_jeu_plante` exige un seul bloc, l'empreinte des
    octets du bloc égale à `jeu_plante_sha256` du plan gelé, exactement V1 à V4, F1 à F4, T-ELIM, T-MAL et K1, chaque loi dans
    la grammaire servie, et **chaque fausse dans la classe que couvre le nul v8** pour l'archive de départ (`classe_couverte` :
    copie d'une loi de l'archive, mélange de lois de l'archive et de lois fixes, loi de l'archive tempérée et inclinée, ou mêlée
    à une loi aveugle fixe ; tout le reste — par morceaux, produit, composition, loi inconnue — est refusé, code 2).
M3. **Lois plantées jugées avec l'archive de jugement de leur génération** (`juger_v65`) : nul v8 avec les membres d'archive de
    la génération, hors de la famille des cartes réelles, au seuil log(m/α) ; garde 18 : le nombre de membres d'archive de chaque
    loi plantée doit être celui qu'impose l'archive de sa génération (`nul_v8.membres_archive_v8`), sinon `ArretTour` (code 3).
    (La v64 juge ses témoins sans archive : `juger(…, {}, …)`.)
M4. **Bras réel seul ; génération 2 complète** : un seul bras (« reel ») ; tout autre bras demandé → `TourRefuse` (garde 20,
    code 2). La génération 2 lit le bilan scellé de la génération 1 par `boucle_fermee_v59.lire_heritage` (empreinte écrite =
    empreinte lue), sert aux proposeurs la vue {K1} ∪ retenues, juge ses cartes avec l'archive lue, replante F1 à F4 et une
    **copie renommée de chacune des quatre premières retenues par log e**, lues dans l'héritage lu (garde 21 : copie d'une carte
    non retenue → `CopieNonRetenue`, arrêt) ; V1 à V4 et les instruments ne sont pas replantés. Arrêt après la génération 2.
Gardes de dépense : plafond des modèles et parts des relais tenus par `tour_ferme_v64.Compteur` (arrêt au franchissement,
    arrêt avant un étage si une part restante est sous le pire cas de l'étage) ; en plus, **avant chaque appel d'un proposeur**,
    la part restante de son relais doit couvrir le budget de l'appel (`exiger_part_avant_appel`, arrêt) ; en mode réel, **aucun
    appel sans GO cité et vérifié** (`exiger_go`, refus avant tout appel).

Aucun réseau ici ; les adaptateurs réels sont construits par le lanceur `demonstrations/boucle_reelle_v65.py`.
"""

import hashlib
import json
import math
import os
import re

from . import a_blanc_v59 as A
from . import boucle_fermee_v59 as bf
from . import nul_v8
from . import tour_ferme_v64 as T
from .outils import ecrire_json_scelle, json_canonique

VERSION = "boucle-reelle-v65"
VERSION_JEU = "jeu-plante-boucle-reelle-v65"
VERSION_HERITAGE_DEPART = "heritage-depart-boucle-reelle-v65"
NOM_HERITAGE_DEPART = "heritage-depart-v65.json"
ALPHA = T.ALPHA
K, DIM = T.K, T.DIM
BRAS = ("reel",)
GENERATIONS = 2
M_FIXE = 22  # 12 cartes réelles, 8 lois plantées, 2 cas d'instrument (brouillon, section 6)
VRAIES = ("V1", "V2", "V3", "V4")
FAUSSES = ("F1", "F2", "F3", "F4")
INSTRUMENTS = ("T-ELIM", "T-MAL")
ARCHIVE_DE_DEPART = ("K1",)
STATUT_K1 = "connue, déclarée"
COPIES_MAX = 4
DEBUT_JEU, FIN_JEU = "<!-- jeu-plante-v65 : début -->", "<!-- jeu-plante-v65 : fin -->"
SEUIL_TEST, SEUIL_T_ELIM = T.SEUIL_TEST, T.SEUIL_T_ELIM
CLES_JEU = {"version", "archive_de_depart", "vraies", "fausses", "instruments"}


class TourRefuse(T.TourRefuse):
    """Refus avant tout appel (code 2)."""


class JeuPlanteRefuse(TourRefuse):
    """Garde 19 : bloc du jeu planté absent, en double, d'une autre empreinte, incomplet, ou fausse hors de la classe couverte."""


class HeritageDepartRefuse(TourRefuse):
    """Garde 17 : héritage de départ d'une autre empreinte que celle du texte, sceau faux, K1 altérée, loi plantée dedans."""


class BrasRefuse(TourRefuse):
    """Garde 20 : un bras autre que le bras réel demandé."""


class GoAbsent(TourRefuse):
    """Mode réel sans GO cité et vérifié : aucun appel."""


class ArretTour(T.ArretTour):
    """Arrêt de la liste d'arrêt (code 3, relevé partiel scellé)."""


class PlanteeSansArchive(ArretTour):
    """Garde 18 : une loi plantée jugée avec un autre nombre de membres d'archive que celui de sa génération."""


class CopieNonRetenue(ArretTour):
    """Garde 21 : copie de la génération 2 d'une carte que la sélection lue ne retient pas, ou d'une autre loi."""


# --- M2 : jeu planté lu dans le texte scellé ------------------------------------------------------------------------------------


def bloc_du_jeu(texte):
    """Les octets du bloc `jeu-plante-v65` (entre les deux marques, une seule fois chacune) et l'objet JSON du bloc de code qu'il
    contient ; `JeuPlanteRefuse` sinon."""
    if texte.count(DEBUT_JEU) != 1 or texte.count(FIN_JEU) != 1:
        raise JeuPlanteRefuse("bloc « jeu-plante-v65 » absent ou en double dans le texte scellé")
    i, j = texte.find(DEBUT_JEU), texte.find(FIN_JEU)
    if j < i:
        raise JeuPlanteRefuse("bloc « jeu-plante-v65 » fermé avant d'être ouvert")
    brut = texte[i + len(DEBUT_JEU):j]
    m = re.fullmatch(r"\s*```json\n(.*?)\n```\s*", brut, re.S)
    if not m:
        raise JeuPlanteRefuse("bloc « jeu-plante-v65 » : un seul bloc de code ```json attendu entre les marques")
    try:
        jeu = json.loads(m.group(1))
    except ValueError as e:
        raise JeuPlanteRefuse(f"bloc « jeu-plante-v65 » : JSON illisible ({e})") from None
    return m.group(1).encode("utf-8"), jeu


def empreinte_du_bloc(texte):
    """sha256 des octets du JSON du bloc (ce que porte `jeu_plante_sha256` du plan gelé)."""
    return hashlib.sha256(bloc_du_jeu(texte)[0]).hexdigest()


def _egales(a, b):
    try:
        return json_canonique(a) == json_canonique(b)
    except (TypeError, ValueError):
        return False


def classe_couverte(loi, archive):
    """La forme de `loi` dans la classe couverte du nul v8 (docstring de `pole/nul_v8.py`) pour l'archive `archive` ({id: loi}),
    ou None si la loi n'y est pas **par construction**. Formes reconnues (banc v8) : « copie d'une loi de l'archive » (T17s) ;
    « mélange de lois de l'archive et de lois fixes » (T03u, T03b, T01, T02) ; « loi de l'archive tempérée et inclinée » (T05s) ;
    « loi de l'archive mêlée à une loi aveugle fixe » (`melange_aveugle` seul). Tout le reste (par morceaux, produit,
    composition d'étapes, oscillation, loi inconnue du pôle) → None."""
    connues = list(archive.values())
    if not connues or not isinstance(loi, dict):
        return None
    if any(_egales(loi, k) for k in connues):
        return "copie d'une loi de l'archive"
    t = loi.get("type")
    if t == "melange":
        comp, poids = loi.get("composantes"), loi.get("poids")
        if not isinstance(comp, list) or not isinstance(poids, list) or len(comp) != len(poids) or not comp:
            return None
        if any(not isinstance(w, (int, float)) or isinstance(w, bool) or not math.isfinite(w) or w < 0 for w in poids) \
                or abs(sum(poids) - 1.0) > 1e-9:
            return None
        sortes = ["archive" if any(_egales(c, k) for k in connues) else ("fixe" if isinstance(c, dict) and c.get("type") == "fixe"
                                                                             else None) for c in comp]
        if None in sortes or "archive" not in sortes:
            return None
        return "mélange de lois de l'archive et de lois fixes"
    if t == "transformee" and any(_egales(loi.get("base"), k) for k in connues):
        cles = set(loi) - {"type", "base"}
        if cles and cles <= {"puissance", "inclinaison"}:
            return "loi de l'archive tempérée et inclinée"
        if cles == {"melange_aveugle"}:
            return "loi de l'archive mêlée à une loi aveugle fixe"
    return None


def verifier_jeu_plante(jeu):
    """Garde 19 (structure) : exactement K1, V1 à V4, F1 à F4, T-ELIM et T-MAL, chaque loi de la grammaire servie, chaque fausse
    dans la classe couverte pour l'archive de départ, aucune vraie ni instrument égal à K1. Rend le jeu ; `JeuPlanteRefuse` sinon."""
    if not isinstance(jeu, dict) or set(jeu) != CLES_JEU or jeu.get("version") != VERSION_JEU:
        raise JeuPlanteRefuse(f"jeu planté : clés {sorted(CLES_JEU)} et version {VERSION_JEU!r} exigées")
    attendu = {"archive_de_depart": ARCHIVE_DE_DEPART, "vraies": VRAIES, "fausses": FAUSSES, "instruments": INSTRUMENTS}
    for groupe, noms in attendu.items():
        if not isinstance(jeu[groupe], dict) or sorted(jeu[groupe]) != sorted(noms):
            raise JeuPlanteRefuse(f"jeu planté incomplet ou en trop : {groupe} = {sorted(jeu[groupe]) if isinstance(jeu[groupe], dict) else jeu[groupe]!r}, "
                                  f"attendu {sorted(noms)}")
        for nom, loi in jeu[groupe].items():
            motif = T.verifier_loi_servable(loi)
            if motif:
                raise JeuPlanteRefuse(f"jeu planté : {groupe}.{nom} hors de la grammaire servie : {motif}")
    archive = jeu["archive_de_depart"]
    for nom, loi in jeu["fausses"].items():
        if classe_couverte(loi, archive) is None:
            raise JeuPlanteRefuse(f"jeu planté : la fausse {nom} n'est pas dans la classe que couvre le nul v8 pour l'archive de "
                                  "départ (recombinaison par morceaux, produit, composition ou loi inconnue du pôle) : refus")
    for groupe in ("vraies", "instruments"):
        for nom, loi in jeu[groupe].items():
            if any(_egales(loi, k) for k in archive.values()):
                raise JeuPlanteRefuse(f"jeu planté : {groupe}.{nom} est une loi de l'archive de départ")
    return jeu


def lire_jeu_plante(texte, sha_attendue):
    """Garde 19 : le jeu planté du texte scellé, lu à l'octet : empreinte des octets du bloc = `sha_attendue` (plan gelé), puis
    `verifier_jeu_plante`. Rend (jeu, empreinte)."""
    octets, jeu = bloc_du_jeu(texte)
    sha = hashlib.sha256(octets).hexdigest()
    if not isinstance(sha_attendue, str) or sha != sha_attendue:
        raise JeuPlanteRefuse(f"jeu planté d'empreinte {sha[:12]}… ≠ empreinte du plan gelé {str(sha_attendue)[:12]}… : refus")
    return verifier_jeu_plante(jeu), sha


def texte_du_bloc(jeu):
    """Le bloc à recopier dans le texte scellé (marques comprises), JSON indenté à clés triées."""
    return DEBUT_JEU + "\n```json\n" + json.dumps(jeu, ensure_ascii=False, indent=1, sort_keys=True) + "\n```\n" + FIN_JEU


def jeu_du_dessin(monde):
    """Le jeu du brouillon 1, sections 3.2 à 3.4 et 3.6, tel que le joue `puissance-boucle-reelle-v1.py` (`a2afcdd3…`,
    `lois_du_dessin`) : K1 gelée en littéral, V1 à V4, F1 à F4, T-ELIM, T-MAL. Sert à écrire le bloc du texte (outil de
    préparation) ; jamais lu par une course, qui lit le texte scellé."""
    L = monde["loi"]
    k1 = {"type": "softmax", "poids": [[0.0, 0.0], [-0.834964, 0.0], [-0.242046, 0.0]], "biais": [0.0, 0.941698, 0.721847]}
    uniforme = {"type": "fixe", "probas": [1.0, 1.0, 1.0]}
    aveugle = {"type": "fixe", "probas": [0.3, 0.4, 0.3]}
    return {"version": VERSION_JEU, "archive_de_depart": {"K1": k1},
            "vraies": {"V1": L, "V2": {"type": "softmax", "poids": [[0.0, ligne[1]] for ligne in L["poids"]], "biais": list(L["biais"])},
                       "V3": {"type": "transformee", "base": L, "puissance": 0.08},
                       "V4": {"type": "melange", "composantes": [L, uniforme], "poids": [0.15, 0.85]}},
            "fausses": {"F1": json.loads(json.dumps(k1)),
                        "F2": {"type": "melange", "composantes": [k1, uniforme], "poids": [0.8, 0.2]},
                        "F3": {"type": "melange", "composantes": [k1, aveugle], "poids": [0.8, 0.2]},
                        "F4": {"type": "transformee", "base": k1, "puissance": 1.2, "inclinaison": [0.0, 0.05, -0.05]}},
            "instruments": {"T-ELIM": {"type": "transformee", "base": L, "puissance": 1.25}, "T-MAL": L}}


# --- M1 : héritage de départ scellé -------------------------------------------------------------------------------------------


def ecrire_heritage_depart(dossier, jeu):
    """Écrit et scelle `heritage-depart-v65.json` (génération 0 déclarée : archive {K1}, K1 « connue, déclarée ») ; rend son
    empreinte, à porter au plan gelé du texte (`heritage_depart_sha256`). Outil de préparation, jamais joué par une course."""
    verifier_jeu_plante(jeu)
    objet = {"version": VERSION_HERITAGE_DEPART, "generation": 0, "archive": dict(jeu["archive_de_depart"]),
             "statut": {k: STATUT_K1 for k in jeu["archive_de_depart"]},
             "regle": "génération 0 déclarée, aucune sélection ; la génération 1 juge ses cartes et ses lois plantées avec cette "
                      "archive et la sert aux proposeurs"}
    return ecrire_json_scelle(os.path.join(dossier, NOM_HERITAGE_DEPART), objet)


def lire_heritage_depart(chemin, sha_du_texte, jeu):
    """Garde 17 : l'héritage de départ, accepté seulement si son empreinte est celle du texte scellé (lue **avant** le contenu,
    sceau compagnon compris, par `boucle_fermee_v59.lire_scelle_verifie`), sa version et sa génération justes, son archive
    exactement {K1} du jeu planté (à l'octet), K1 « connue, déclarée », aucune loi plantée vraie ou instrument dedans. Rend
    l'héritage au format v59 (génération lue 0) ; lève `HeritageDepartRefuse` sinon (aucun repli)."""
    try:
        h = bf.lire_scelle_verifie(chemin, sha_du_texte, "héritage de départ")
    except bf.SelectionNonVerifiee as e:
        raise HeritageDepartRefuse(f"héritage de départ refusé : {e}") from None
    if not isinstance(h, dict) or h.get("version") != VERSION_HERITAGE_DEPART or h.get("generation") != 0:
        raise HeritageDepartRefuse("héritage de départ d'une autre version ou d'une autre génération : refus")
    archive = h.get("archive")
    if not isinstance(archive, dict) or sorted(archive) != sorted(ARCHIVE_DE_DEPART):
        raise HeritageDepartRefuse(f"héritage de départ : archive {sorted(archive) if isinstance(archive, dict) else archive!r} ≠ {list(ARCHIVE_DE_DEPART)}")
    if not _egales(archive, jeu["archive_de_depart"]):
        raise HeritageDepartRefuse("héritage de départ : K1 ≠ K1 du jeu planté du texte scellé (loi altérée) : refus")
    if h.get("statut") != {k: STATUT_K1 for k in ARCHIVE_DE_DEPART}:
        raise HeritageDepartRefuse(f"héritage de départ : K1 doit être marquée « {STATUT_K1} »")
    for groupe in ("vraies", "instruments"):
        for nom, loi in jeu[groupe].items():
            if any(_egales(loi, k) for k in archive.values()):
                raise HeritageDepartRefuse(f"héritage de départ : loi plantée {nom} dans l'archive : refus")
    return {"version": bf.VERSION, "generation_lue": 0, "bilan_sha256": sha_du_texte, "retenues": [], "archive": dict(archive),
            "empreintes_lues": {"heritage_depart": sha_du_texte}}


# --- gardes : bras, GO, parts avant appel --------------------------------------------------------------------------------------


def exiger_bras(bras):
    """Garde 20 : le bras réel seul (D1)."""
    b = tuple(bras) if isinstance(bras, (list, tuple)) else (bras,)
    if b != BRAS:
        raise BrasRefuse(f"bras demandé(s) {list(b)} ; le code v65 joue le bras réel seul (D1) : refus avant tout appel")
    return BRAS


def exiger_go(reel, go):
    """Aucun appel en mode réel sans GO cité et vérifié (ligne du registre rendue par `configuration_v56.verifier_go_v56`)."""
    if reel and not (isinstance(go, dict) and isinstance(go.get("identifiant"), str) and go.get("plafond_lu_usd")):
        raise GoAbsent("mode réel sans GO cité et vérifié : aucun appel")
    return True


def exiger_part_avant_appel(compteur, relais, besoin_usd):
    """Avant l'appel d'un proposeur : la part restante de son relais (et le plafond restant) doit couvrir le budget de l'appel."""
    if relais in compteur.parts and compteur.parts[relais] - compteur.par_relais.get(relais, 0.0) < float(besoin_usd) - 1e-9:
        raise ArretTour(f"part restante du relais {relais} ({compteur.parts[relais] - compteur.par_relais.get(relais, 0.0):.4f} USD) "
                        f"sous le budget de l'appel ({float(besoin_usd):.4f} USD) : arrêt avant l'appel")
    if compteur.plafond_usd - compteur.usd < float(besoin_usd) - 1e-9:
        raise ArretTour(f"plafond restant ({compteur.plafond_usd - compteur.usd:.4f} USD) sous le budget de l'appel : arrêt avant l'appel")


# --- M3 : juge, lois plantées avec l'archive ---------------------------------------------------------------------------------


def membres_attendus(archive):
    """Nombre de membres d'archive du nul v8 qu'impose `archive` ({id: loi}) : `nul_v8.membres_archive_v8`."""
    return len(nul_v8.membres_archive_v8(dict(archive), None, K, DIM)) if archive else 0


def juger_v65(cartes, plantees, monde, archive, racine, tache, m, archive_des_plantees=None):
    """Rend (promues cartes, promues plantées, détail, m, membres attendus). Cartes : `tour_ferme_v64.juger` (nul v8 avec
    l'archive, règle e-BH à m fixé). Lois plantées ((nom, carte servie)) : nul v8 **avec l'archive de la génération**, hors
    famille au seuil log(m/α) (M3). Garde 18 : membres d'archive de chaque loi plantée = membres attendus de l'archive (et > 0
    si l'archive n'est pas vide), sinon `PlanteeSansArchive`. `archive_des_plantees` : essais seulement (l'artefact qui
    reproduit le canal de la v64)."""
    promues, _, detail, m = T.juger(cartes, [], monde, archive, racine, tache, m)
    attendus = membres_attendus(archive)
    a_plantees = archive if archive_des_plantees is None else archive_des_plantees
    seuil = math.log(m / ALPHA)
    promues_p = []
    for nom, c in plantees:
        ev, d = A.juger_carte(c["loi_predictive"], monde, a_plantees, racine, f"{tache}|plantee={c['identifiant']}")
        if d["membres_d_archive"] != attendus or (archive and d["membres_d_archive"] == 0):
            raise PlanteeSansArchive(f"loi plantée {nom} jugée avec {d['membres_d_archive']} membre(s) d'archive ; l'archive de sa "
                                     f"génération en impose {attendus} (garde 18) : arrêt")
        traj = ev["trajectoire_log_w"]
        log_e = -math.inf if ev.get("marge_atteinte") is False else next((v for v in traj if v >= seuil), traj[-1])
        promue = bool(ev["promue"]) and log_e >= seuil
        detail[c["identifiant"]] = dict(d, plantee=nom, promue_seule=bool(ev["promue"]), promue=promue,
                                        log_e=None if math.isinf(log_e) else round(log_e, 6),
                                        log_richesse_max=round(ev["log_richesse_max"], 6),
                                        regle="hors famille, seuil log(m/α), avec l'archive de la génération (M3)")
        if promue:
            promues_p.append(c["identifiant"])
    return promues, promues_p, detail, m, attendus


# --- M4 : lois plantées par génération, copies de la sélection lue -------------------------------------------------------------


def plantees_de_la_generation(jeu, generation, racine, tache, copies=()):
    """(nom, identifiant réel, carte servie, source) des lois plantées d'une génération : génération 1 : V1 à V4, F1 à F4,
    T-ELIM (seuil « au moins 2,0 »), T-MAL (sans statistique) ; génération 2 : F1 à F4 et les copies ((nom, source, loi))."""
    lois = []
    if generation == 1:
        lois += [(n, jeu["vraies"][n], None) for n in VRAIES] + [(n, jeu["fausses"][n], None) for n in FAUSSES]
        lois += [(n, jeu["instruments"][n], None) for n in INSTRUMENTS]
    else:
        lois += [(n, jeu["fausses"][n], None) for n in FAUSSES] + [(n, loi, src) for n, src, loi in copies]
    out = []
    for nom, loi, source in lois:
        reel = "P-" + hashlib.sha256(f"{racine}|{tache}|{nom}".encode("utf-8")).hexdigest()[:12]
        servi = T.identifiant_opaque(racine, tache, reel)
        c = T.carte_servie(servi, json.loads(json.dumps(loi)), "temoin", seuil=SEUIL_T_ELIM if nom == "T-ELIM" else SEUIL_TEST,
                           sans_statistique=nom == "T-MAL")
        out.append((nom, reel, c, source))
    return out


def copies_de_la_selection(heritage, log_e_g1, n=COPIES_MAX):
    """Garde 21 : les copies renommées des `n` premières retenues de la génération 1 par log e (puis identifiant), lues dans
    l'**héritage lu** (`lire_heritage`) : ((« C1 »…, source, loi de l'archive lue)). Une retenue sans log e (jamais jugée) ou
    absente de l'archive lue → `CopieNonRetenue`."""
    retenues = list(heritage.get("retenues") or [])
    for i in retenues:
        if i not in (heritage.get("archive") or {}):
            raise CopieNonRetenue(f"retenue {i} absente de l'archive lue : refus (garde 21)")
        if log_e_g1.get(i) is None:
            raise CopieNonRetenue(f"retenue {i} sans log e de la génération 1 : refus (garde 21)")
    ordre = sorted(retenues, key=lambda i: (-float(log_e_g1[i]), i))[:n]
    return [(f"C{k}", i, json.loads(json.dumps(heritage["archive"][i]))) for k, i in enumerate(ordre, 1)]


def exiger_copies_de_la_selection(copies, heritage):
    """Garde 21 : chaque copie vient d'une retenue de la sélection lue, avec sa loi exacte ; au plus quatre ; sinon arrêt."""
    if len(copies) > COPIES_MAX:
        raise CopieNonRetenue(f"{len(copies)} copies : au plus {COPIES_MAX}")
    for nom, src, loi in copies:
        if src not in (heritage.get("retenues") or []) or not _egales(loi, (heritage.get("archive") or {}).get(src)):
            raise CopieNonRetenue(f"copie {nom} de {src} : carte non retenue par la sélection lue, ou loi différente : refus (garde 21)")
    return True


# --- une génération du bras réel ---------------------------------------------------------------------------------------------


def jouer_generation(dossier, generation, monde, jeu, heritage, racine, fabrique_executeur, proposeurs, adaptateur_etage, roles,
                     decisions, plan, compteur, journal, releve, recherche, copies=(), moteur="simule", environnement=None,
                     permis_en_plus=(), archive_des_plantees=None):
    """Une génération du bras réel : proposition → gardien → juge (cartes et lois plantées, avec l'archive lue) → étage des
    cartes promues et étage des lois plantées promues (même tranche) → contre-calcul → sélection (cartes seules) → bilan scellé.
    Rend (empreinte du bilan, ligne de journal)."""
    tache = f"{VERSION}|bras=reel|generation={generation}"
    archive = heritage["archive"]
    vue = bf.vue_pour_proposeur(heritage)
    cartes, refusees, appels, reels, enonces, proposeur_de = [], {}, [], {}, {}, {}
    contexte = T.contexte_du_proposeur(monde, vue, racine, tache)
    consigne = T.CONSIGNE_PROPOSEUR.format(n=plan["cartes_par_proposeur"])
    for p in proposeurs:
        recherche["contextes_cherches"] += 1
        recherche["touches"] += T.chercher_loi_plantee(monde, consigne, contexte, f"{tache}|proposeur={p.nom}")
        exiger_part_avant_appel(compteur, p.relais, p.budget)
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
            reels[ident], proposeur_de[ident] = ident_reel, p.relais
            c, motif_c = T.completer_carte(prop, ident)
            if c is None:
                refusees[ident] = f"gardien mécanique (gabarit) : {motif_c}"
            else:
                enonces[ident] = prop["enonce"]
                cartes.append(c)
    plantees = plantees_de_la_generation(jeu, generation, racine, tache, copies)
    ids_plantees = {c["identifiant"] for _, _, c, _ in plantees} | {r for _, r, _, _ in plantees}
    passees, plantees_passees, plantees_refusees = [], [], {}
    for c in cartes:
        passeport, motif = T.garder(c, decisions)
        if passeport is None:
            refusees[c["identifiant"]] = motif
        else:
            passees.append(c)
    for nom, _, c, _ in plantees:
        passeport, motif = T.garder(c, decisions)
        if passeport is None:
            plantees_refusees[nom] = motif
        else:
            plantees_passees.append((nom, c))
    promues, promues_p, detail, m, attendus = juger_v65(passees, plantees_passees, monde, archive, racine, tache, plan["m_e_bh"],
                                                        archive_des_plantees=archive_des_plantees)
    par_ident = {c["identifiant"]: c for c in passees}
    par_ident_p = {c["identifiant"]: (nom, c) for nom, c in plantees_passees}
    executeur, description_bac = fabrique_executeur()
    resume, chemin_sel, sha_sel, tranche, cc = T.jouer_etage(
        os.path.join(dossier, bf.DOSSIER_ETAGE), [par_ident[i] for i in promues], {i: c["loi_predictive"] for i, c in par_ident.items()},
        monde, racine, tache, executeur, adaptateur_etage, roles, compteur, journal, moteur=moteur, environnement=environnement,
        permis_en_plus=permis_en_plus)
    executeur_p, _ = fabrique_executeur()
    resume_p, _, sha_sel_p, _, cc_p = T.jouer_etage(
        os.path.join(dossier, "etage-plantees"), [par_ident_p[i][1] for i in promues_p],
        {i: c["loi_predictive"] for i, (_, c) in par_ident_p.items()}, monde, racine, tache, executeur_p, adaptateur_etage, roles,
        compteur, journal, tranche=tranche, moteur=moteur, environnement=environnement, permis_en_plus=permis_en_plus)
    verdicts, verdicts_p = T._verdicts(resume), T._verdicts(resume_p)
    with open(chemin_sel, encoding="utf-8") as f:
        retenues = json.load(f)["retenues"]
    if set(retenues) & ids_plantees:  # garde 7 : aucune loi plantée dans la sélection
        raise T.TemoinRetenu(f"loi plantée dans la sélection de {tache} : refus")
    for c in passees:
        i = c["identifiant"]
        releve["cartes"].append({"generation": generation, "proposeur": proposeur_de[i], "identifiant": reels[i], "identifiant_servi": i,
                                 "gardien": "passe", "promue": i in promues, "promue_seule": detail[i].get("promue_seule"),
                                 "log_e": detail[i].get("log_e"), "log_richesse_max": detail[i].get("log_richesse_max"),
                                 "membres_d_archive": detail[i].get("membres_d_archive"), "verdict": verdicts.get(i),
                                 "contre_calcul_ok": cc[i]["ok"] if i in cc else None, "retenue": i in retenues,
                                 "loi": c["loi_predictive"], "enonce": enonces.get(i)})
    for i, motif in refusees.items():
        releve["cartes"].append({"generation": generation, "proposeur": proposeur_de.get(i), "identifiant": reels.get(i, i),
                                 "identifiant_servi": i, "gardien": "refuse", "motif": motif, "promue": False, "verdict": None,
                                 "retenue": False, "enonce": enonces.get(i)})
    for nom, reel, c, source in plantees:
        i = c["identifiant"]
        d = detail.get(i, {})
        releve["plantees"].append({"generation": generation, "nom": nom, "source": source, "identifiant": reel, "identifiant_servi": i,
                                   "gardien": "refuse" if nom in plantees_refusees else "passe", "motif": plantees_refusees.get(nom),
                                   "promue": i in promues_p, "promue_seule": d.get("promue_seule"), "log_e": d.get("log_e"),
                                   "log_richesse_max": d.get("log_richesse_max"), "membres_d_archive": d.get("membres_d_archive"),
                                   "membres_attendus": attendus, "verdict": verdicts_p.get(i),
                                   "contre_calcul_ok": cc_p[i]["ok"] if i in cc_p else None, "loi": c["loi_predictive"]})
    comptes = {"proposees": len(reels), "refusees_au_gardien": len(refusees), "jugees": len(passees), "m_e_bh": m,
               "promues": len(promues), "testees": len(verdicts), "retenues": len(retenues), "plantees_promues": len(promues_p),
               "plantees_testees": len(verdicts_p), "appels_proposeurs": appels}
    graines = {"tache": tache, "par_carte": {i: d["graines"] for i, d in detail.items()}}
    sha_bilan = bf.ecrire_bilan_generation(dossier, generation=generation, bras="reel", cartes=passees, resume_etage=resume,
                                           chemin_selection=chemin_sel, sha_selection=sha_sel, archive_precedente=archive,
                                           heritage_lu=heritage, comptes=comptes, graines=graines)
    releve["archives_de_jugement"][str(generation)] = json.loads(json.dumps(archive))
    releve["retenues"][str(generation)] = list(retenues)
    releve["membres_attendus"][str(generation)] = attendus
    releve["etages"].append({"generation": generation, "bac_a_sable": description_bac.get("nom"),
                             "factice": bool(description_bac.get("factice")), "selection_sha256": sha_sel,
                             "selection_plantees_sha256": sha_sel_p, "bilan_sha256": sha_bilan,
                             "contre_calculs": {"cartes": cc, "plantees": cc_p}})
    ligne = {"evenement": "generation", "generation": generation, "heritage_lu": heritage.get("bilan_sha256"),
             "archive_de_jugement": sorted(archive), "membres_attendus": attendus, "refusees_au_gardien": refusees,
             "plantees_refusees": plantees_refusees, "promues": promues, "plantees_promues": promues_p, "correspondance": reels,
             "verdicts": verdicts, "verdicts_plantees": verdicts_p, "retenues": retenues, "comptes": comptes,
             "selection_sha256": sha_sel, "bilan_sha256": sha_bilan, "depense": compteur.etat(),
             "log_e": {i: d.get("log_e") for i, d in detail.items()}}
    journal.append(ligne)
    return sha_bilan, ligne


# --- la boucle entière : génération 0 déclarée, génération 1, génération 2, relevé ----------------------------------------------


def jouer_boucle(sortie, *, monde, jeu, heritage_depart, racine, plan, decisions, proposeurs, adaptateur_etage, roles,
                 fabrique_executeur, compteur, reel=False, go=None, moteur="simule", environnement=None, permis_en_plus=(),
                 archive_des_plantees=None, lire=None):
    """Génération 1 (héritage de départ {K1}), puis génération 2 (bilan de la génération 1 lu par `lire_heritage`), bras réel
    seul. Rend (relevé, journal). Toute exception après le premier appel lève `ArretTour` avec le relevé partiel. `lire` : essais
    seulement (la fonction de lecture de l'héritage ; défaut `boucle_fermee_v59.lire_heritage`)."""
    exiger_bras(plan.get("bras", BRAS))
    exiger_go(reel, go)
    if plan.get("generations") != GENERATIONS:
        raise TourRefuse(f"générations : {plan.get('generations')!r} ; le code v65 joue la génération 1 et la génération 2 (D2)")
    T.verifier_decisions(decisions)
    T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                               (roles["verificateur"][0], roles["familles"]["verificateur"]))
    adaptateur_etage.parts = dict(compteur.parts)
    lire = lire or bf.lire_heritage
    journal = []
    releve = {"version": VERSION, "arret": None, "complet": False, "generations_jouees": [], "bras": list(BRAS),
              "racine": str(racine), "monde_sha256": monde.get("sha256"), "plan": dict(plan), "decisions": dict(decisions),
              "heritage_depart": {"sha256": heritage_depart.get("bilan_sha256"), "archive": sorted(heritage_depart["archive"])},
              "cartes": [], "plantees": [], "archives_de_jugement": {}, "retenues": {}, "membres_attendus": {}, "etages": [],
              "lecture_selection": None, "moteur_etage": moteur}
    recherche = {"contextes_cherches": 0, "touches": []}
    try:
        d1 = os.path.join(sortie, "generation-1")
        os.makedirs(d1)
        sha1, ligne1 = jouer_generation(d1, 1, monde, jeu, heritage_depart, racine, fabrique_executeur, proposeurs, adaptateur_etage,
                                        roles, decisions, plan, compteur, journal, releve, recherche, (), moteur, environnement,
                                        permis_en_plus, archive_des_plantees)
        releve["generations_jouees"].append(1)
        with open(os.path.join(d1, bf.DOSSIER_ETAGE, T.NOM_SELECTION), encoding="utf-8") as f:  # telle qu'écrite par la génération 1
            retenues_ecrites = json.load(f)["retenues"]
        try:
            h2 = lire(d1, sha1)
        except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:
            raise ArretTour(f"héritage de la génération 1 refusé ({type(e).__name__}) : {e}") from e
        vue = bf.vue_pour_proposeur(h2)
        copies = copies_de_la_selection(h2, {i: ligne1["log_e"].get(i) for i in h2["retenues"]})
        exiger_copies_de_la_selection(copies, h2)
        releve["lecture_selection"] = {"attendu": sha1, "lu": h2["bilan_sha256"], "empreintes_lues": h2["empreintes_lues"],
                                       "vue": sorted(x["identifiant"] for x in vue["lois_retenues"]),
                                       "vue_attendue": sorted(set(heritage_depart["archive"]) | set(retenues_ecrites)),
                                       "retenues_ecrites_g1": sorted(retenues_ecrites), "retenues_lues": sorted(h2["retenues"]),
                                       "copies": [{"nom": n, "source": s} for n, s, _ in copies]}
        journal.append({"evenement": "heritage-lu", "generation": 2, "bilan_sha256": h2["bilan_sha256"], "archive": sorted(h2["archive"])})
        d2 = os.path.join(sortie, "generation-2")
        os.makedirs(d2)
        sha2, _ = jouer_generation(d2, 2, monde, jeu, h2, racine, fabrique_executeur, proposeurs, adaptateur_etage, roles,
                                   decisions, plan, compteur, journal, releve, recherche, copies, moteur, environnement,
                                   permis_en_plus, archive_des_plantees)
        releve["generations_jouees"].append(2)
        fin = lire(d2, sha2)  # la sélection de la génération 2 est scellée et relue ; aucune génération 3
        releve["selection_finale"] = {"bilan_sha256": sha2, "retenues": sorted(fin["retenues"])}
        releve["complet"] = True
    except Exception as e:  # noqa: BLE001 — toute exception après le premier appel est un arrêt scellé, motif et type dits
        releve["arret"] = f"{type(e).__name__} : {str(e)[:500]}"
        journal.append({"evenement": "arret", "motif": releve["arret"], "depense": compteur.etat()})
    releve["recherche_loi_plantee"] = {"contextes_cherches": recherche["contextes_cherches"], "touches": recherche["touches"],
                                       "formes": ["exacte", "deux décimales"]}
    releve["depense"] = compteur.etat()
    if releve["arret"]:
        raise ArretTour(releve["arret"], {"releve": releve, "journal": journal})
    return releve, journal


__all__ = ("VERSION", "VERSION_JEU", "NOM_HERITAGE_DEPART", "BRAS", "GENERATIONS", "M_FIXE", "VRAIES", "FAUSSES", "INSTRUMENTS",
           "DEBUT_JEU", "FIN_JEU", "TourRefuse", "JeuPlanteRefuse", "HeritageDepartRefuse", "BrasRefuse", "GoAbsent", "ArretTour",
           "PlanteeSansArchive", "CopieNonRetenue", "bloc_du_jeu", "empreinte_du_bloc", "classe_couverte", "verifier_jeu_plante",
           "lire_jeu_plante", "texte_du_bloc", "jeu_du_dessin", "ecrire_heritage_depart", "lire_heritage_depart", "exiger_bras",
           "exiger_go", "exiger_part_avant_appel", "membres_attendus", "juger_v65", "plantees_de_la_generation",
           "copies_de_la_selection", "exiger_copies_de_la_selection", "jouer_generation", "jouer_boucle")
