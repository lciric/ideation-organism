"""Cœur de la plus petite course réelle de la boucle complète de l'organisme, version 66 (fichier neuf, R12 ; la v65 reste
intacte et ses fonctions sont réutilisées telles quelles : jeu planté, héritage de départ, gardes 17 à 21, copies).

Corrections de la contre-lecture du code v65 (`contre-lecture-code-v65-v2.md`, `c4ddfc7f…`), côté cœur :

CLV65-02 (a) **Jugements écrits au relevé au fil de l'étage** : dès la sortie du juge, chaque carte et chaque loi plantée de la
    génération entre au relevé (promotion, log e, log W maximal, membres d'archive, membre dominant du nul, empreinte
    d'engagement, graines ; verdict « en attente ») ; les verdicts, le contre-calcul et la retenue s'y ajoutent **après** les
    étages. Un arrêt pendant un étage laisse donc au relevé partiel toute promotion déjà prononcée (une fausse promue s'y lit).
CLV65-02 (b) **Héritage refusé consigné** : si la lecture du bilan de la génération 1 est refusée, `lecture_selection` porte
    l'empreinte attendue, l'empreinte **sur disque** du bilan (relue à part, en octets : « empreinte lue ≠ écrite » devient
    atteignable) et le motif ; la lecture gelée v66 écrit « C4 (partielle) ». De même pour la relecture finale (génération 2).
CLV65-03 **Vue réellement servie, vérifiée au moment du service** (garde 23, neuve) : avant le premier appel d'une génération,
    les lois du contexte servi aux proposeurs doivent être exactement {K1} ∪ retenues **écrites** par la génération 1 (fichier de
    sélection relu à part, pas l'héritage lu), chacune égale à sa loi dans l'archive de jugement, aucune loi plantée ; après
    chaque appel, l'empreinte du texte qu'a reçu le proposeur (`ProposeurAdaptateur.appels[-1].consigne_sha256`) doit être
    celle du texte bâti sur ce contexte vérifié. Sinon `VueServieRefusee` (arrêt). Le relevé porte, par génération, les
    identifiants servis, l'empreinte des lois servies et celle de chaque texte servi (`vues_servies`) ; la lecture compare.
CLV65-05 **Garde 7, moitié « ni servies »** : `tour_ferme_v64.exiger_sans_temoin` (aucun identifiant de loi plantée, réel ou
    servi, dans l'archive ni dans la vue) est rappelée sur l'héritage lu avant la génération 2 et sur la relecture finale ;
    la moitié « ni retenues » (sélection de chaque génération) reste, comme en v65.
CLV65-08 **Mesures promises par le brouillon** : membre dominant du nul et empreinte d'engagement par loi (juge `juger_v66`,
    même calcul que `tour_ferme_v64.juger` et `boucle_reelle_v65.juger_v65`, ces deux champs gardés ; équivalence essayée) ;
    recherche de la loi plantée dans les consignes servies à l'expérimentateur et au vérificateur (`EtageMesure`, hors de la
    loi gelée du test, que l'expérimentateur doit voir, et dedans, comptées à part) ; lignes de la tranche présentes dans les
    contextes servis (mesure de la v64, reprise, comparée à six décimales) ; jetons d'entrée et de sortie par appel quand la
    commande externe les rend (`ReleveDeJetons`, champ `usage` de la dernière ligne JSON ; sommes par relais, jamais de moyenne).
Incidents de garde (7, 21, 23) écrits au relevé avant l'arrêt (`incidents`), lus par la lecture gelée comme écarts de P6.

Aucun réseau ici ; les adaptateurs réels sont construits par le lanceur `demonstrations/boucle_reelle_v66.py`.
"""

import hashlib
import json
import math
import os
import stat

from . import a_blanc_v59 as A
from . import boucle_fermee_v59 as bf
from . import boucle_reelle_v65 as B65
from . import tour_ferme_v64 as T
from .cycle import appliquer_multiplicite
from .outils import json_canonique

VERSION = "boucle-reelle-v66"
ALPHA, K, DIM = B65.ALPHA, B65.K, B65.DIM
BRAS, GENERATIONS, M_FIXE = B65.BRAS, B65.GENERATIONS, B65.M_FIXE
VRAIES, FAUSSES, INSTRUMENTS = B65.VRAIES, B65.FAUSSES, B65.INSTRUMENTS
ARCHIVE_DE_DEPART, COPIES_MAX = B65.ARCHIVE_DE_DEPART, B65.COPIES_MAX
DECIMALES_TRANCHE = 6  # les épisodes servis aux proposeurs sont écrits à six décimales (`tour_ferme_v64.episodes_de_developpement`)

TourRefuse, ArretTour, GoAbsent, BrasRefuse = B65.TourRefuse, B65.ArretTour, B65.GoAbsent, B65.BrasRefuse
JeuPlanteRefuse, HeritageDepartRefuse = B65.JeuPlanteRefuse, B65.HeritageDepartRefuse
PlanteeSansArchive, CopieNonRetenue = B65.PlanteeSansArchive, B65.CopieNonRetenue
exiger_bras, exiger_go, exiger_part_avant_appel = B65.exiger_bras, B65.exiger_go, B65.exiger_part_avant_appel


class VueServieRefusee(ArretTour):
    """Garde 23 : la vue servie aux proposeurs n'est pas {K1} ∪ retenues écrites, une loi servie diffère de l'archive, une loi
    plantée est servie, ou le texte reçu par un proposeur n'est pas celui bâti sur la vue vérifiée."""


def _sha(octets):
    return hashlib.sha256(octets).hexdigest()


def _egales(a, b):
    try:
        return json_canonique(a) == json_canonique(b)
    except (TypeError, ValueError):
        return False


def empreinte_sur_disque(chemin):
    """sha256 des octets d'un fichier régulier (aucun lien suivi), ou None : l'empreinte « lue » quand une lecture est refusée."""
    try:
        if not stat.S_ISREG(os.lstat(chemin).st_mode):
            return None
        with open(chemin, "rb") as f:
            return _sha(f.read())
    except OSError:
        return None


def _incident(releve, garde, generation, e):
    releve["incidents"].append({"garde": garde, "generation": generation, "type": type(e).__name__, "motif": str(e)[:500]})


# --- juge v66 : celui de la v64 (cartes) et de la v65 (lois plantées), membre dominant gardé ------------------------------------


def juger_v66(cartes, plantees, monde, archive, racine, tache, m, archive_des_plantees=None):
    """Rend (promues cartes, promues plantées, détail, m, membres attendus), **même calcul** que `tour_ferme_v64.juger` (cartes :
    nul v8 avec l'archive, règle e-BH à m fixé) suivi de `boucle_reelle_v65.juger_v65` (lois plantées : nul v8 avec l'archive de
    la génération, hors famille au seuil log(m/α), garde 18), avec en plus, par loi, le membre dominant final du nul
    (`membre_dominant_final`) ; l'empreinte d'engagement et les graines viennent de `a_blanc_v59.juger_carte`."""
    if m < len(cartes):
        raise TourRefuse(f"m fixé ({m}) < cartes jugées ({len(cartes)})")
    issues, detail = {}, {}
    for c in cartes:
        ev, d = A.juger_carte(c["loi_predictive"], monde, archive, racine, f"{tache}|carte={c['identifiant']}")
        issues[c["identifiant"]] = {"verdict_final": "survit" if ev["promue"] else "eliminee", "motif": "", "pari": dict(ev)}
        detail[c["identifiant"]] = dict(d, promue_seule=bool(ev["promue"]), log_richesse_max=round(ev["log_richesse_max"], 6),
                                        membre_dominant_final=ev.get("membre_dominant_final"))
    mult = appliquer_multiplicite(issues, ALPHA, m_fixe=m) if issues else {"m": m, "retenues": []}
    for i, issue in issues.items():
        detail[i].update(promue=issue["verdict_final"] == "survit", log_e=issue["pari"].get("multiplicite", {}).get("log_e"))
    promues = sorted((i for i in issues if detail[i]["promue"]), key=lambda i: (-(detail[i]["log_e"] or -1e9), i))
    m = mult["m"]
    attendus = B65.membres_attendus(archive)
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
                                        membre_dominant_final=ev.get("membre_dominant_final"),
                                        regle="hors famille, seuil log(m/α), avec l'archive de la génération (M3)")
        if promue:
            promues_p.append(c["identifiant"])
    return promues, promues_p, detail, m, attendus


# --- garde 23 : vue servie ----------------------------------------------------------------------------------------------------


def texte_servi(consigne, contexte):
    """Le texte que `tour_ferme_v64.ProposeurAdaptateur.proposer` bâtit et sert (même forme, octet pour octet)."""
    return consigne + "\n\n```json\n" + json.dumps(contexte, ensure_ascii=False) + "\n```\n"


def exiger_vue_servie(contexte, ids_attendus, archive, ids_plantees):
    """Garde 23 (avant le premier appel) : lois du contexte servi = `ids_attendus` exactement, chacune égale à sa loi dans
    `archive`, aucune loi plantée (garde 7, « ni servies ») ; rend {identifiants, lois_sha256, contexte_sha256}."""
    servis = contexte.get("lois_retenues") if isinstance(contexte, dict) else None
    if not isinstance(servis, list):
        raise VueServieRefusee("contexte servi sans lois retenues : refus (garde 23)")
    ids = sorted(str(x.get("identifiant")) for x in servis if isinstance(x, dict))
    if len(ids) != len(servis) or ids != sorted(ids_attendus):
        raise VueServieRefusee(f"vue servie {ids} ≠ {{K1}} ∪ retenues écrites {sorted(ids_attendus)} : arrêt (garde 23)")
    plantes = sorted(set(ids) & set(ids_plantees))
    if plantes:
        raise VueServieRefusee(f"loi(s) plantée(s) servie(s) aux proposeurs : {plantes} : arrêt (garde 7, « ni servies »)")
    for x in servis:
        if not _egales(x.get("loi"), (archive or {}).get(x["identifiant"])):
            raise VueServieRefusee(f"loi servie {x['identifiant']} ≠ sa loi dans l'archive de jugement : arrêt (garde 23)")
    return {"identifiants": ids, "lois_sha256": _sha(json_canonique(servis)), "contexte_sha256": _sha(json_canonique(contexte))}


def exiger_texte_recu(proposeur, avant, sha_attendue):
    """Garde 23 (après l'appel) : le proposeur a consigné exactement un appel de plus, et l'empreinte du texte reçu est celle du
    texte bâti sur le contexte vérifié ; rend l'empreinte."""
    traces = getattr(proposeur, "appels", None)
    if not isinstance(traces, list) or len(traces) != avant + 1 or not isinstance(traces[-1], dict):
        raise VueServieRefusee(f"proposeur {getattr(proposeur, 'nom', '?')} sans trace de l'appel : texte servi non vérifiable (garde 23)")
    recu = traces[-1].get("consigne_sha256")
    if recu != sha_attendue:
        raise VueServieRefusee(f"texte reçu par {getattr(proposeur, 'nom', '?')} ({str(recu)[:12]}…) ≠ texte bâti sur la vue vérifiée "
                               f"({sha_attendue[:12]}…) : arrêt (garde 23)")
    return recu


# --- garde 7, moitié « ni retenues » (sélection d'une génération) ----------------------------------------------------------------


def exiger_selection_sans_plantee(retenues, ids_plantees, tache):
    """Garde 7 : aucune loi plantée (identifiant réel ou servi) dans la sélection d'une génération."""
    presentes = sorted(set(retenues) & set(ids_plantees))
    if presentes:
        raise T.TemoinRetenu(f"loi(s) plantée(s) dans la sélection de {tache} : {presentes} : refus (garde 7)")
    return True


# --- mesures : recherche de L* chez l'expérimentateur et le vérificateur, jetons -------------------------------------------------


def consigne_sans_loi_gelee(texte):
    """(texte hors des lois gelées, texte des lois gelées) : après chaque `tour_ferme_v64.MARQUE_LOI`, l'objet entre accolades
    qui suit (échappé ou non dans un JSON) est retiré du premier et mis dans le second ; sans accolade, rien n'est retiré."""
    hors, dans, i = [], [], 0
    while True:
        j = texte.find(T.MARQUE_LOI, i)
        if j < 0:
            hors.append(texte[i:])
            break
        k = j + len(T.MARQUE_LOI)
        hors.append(texte[i:k])
        while k < len(texte) and texte[k] in " \t":
            k += 1
        if k >= len(texte) or texte[k] != "{":
            i = k
            continue
        profondeur, fin = 0, None
        for n in range(k, len(texte)):
            if texte[n] == "{":
                profondeur += 1
            elif texte[n] == "}":
                profondeur -= 1
                if profondeur == 0:
                    fin = n + 1
                    break
        if fin is None:
            i = k
            continue
        dans.append(texte[k:fin])
        i = fin
    reste = "".join(hors)
    for seg in sorted(set(dans), key=len, reverse=True):  # la même loi recopiée ailleurs (écho du script de l'expérimentateur)
        for v in _formes_de_la_loi(seg):
            n = reste.count(v)
            if n:
                reste = reste.replace(v, " ")
                dans.extend([v] * n)
    return reste, "\n".join(dans)


def _formes_de_la_loi(seg):
    """Le segment tel quel et la loi qu'il porte écrite en JSON canonique sans échappement, échappée une fois, deux fois."""
    formes = {seg}
    for brut in (seg, seg.replace('\\"', '"')):
        try:
            canon = json_canonique(json.loads(brut)).decode("utf-8")
        except (ValueError, TypeError):
            continue
        une = json.dumps(canon, ensure_ascii=False)[1:-1]
        formes |= {canon, une, json.dumps(une, ensure_ascii=False)[1:-1]}
    return sorted(formes, key=len, reverse=True)


class EtageMesure:
    """Enveloppe de l'adaptateur de l'étage (brouillon, section 7, point 6) : avant chaque session, cherche les paramètres de L*
    dans la consigne servie au rôle (expérimentateur ou vérificateur), **hors** de la loi gelée du test (attendu : aucune
    touche) et **dans** la loi gelée (comptées à part : l'expérimentateur doit la voir), puis rend la main à l'adaptateur sans
    rien changer. Tout autre attribut (dépense, parts, appels, prix) est lu et écrit sur l'adaptateur enveloppé."""

    _PROPRES = ("_ad", "_monde", "_mesure", "tache")

    def __init__(self, adaptateur, monde, mesure):
        object.__setattr__(self, "_ad", adaptateur)
        object.__setattr__(self, "_monde", monde)
        object.__setattr__(self, "_mesure", mesure)
        object.__setattr__(self, "tache", "")

    def __getattr__(self, nom):
        return getattr(object.__getattribute__(self, "_ad"), nom)

    def __setattr__(self, nom, valeur):
        if nom in self._PROPRES:
            object.__setattr__(self, nom, valeur)
        else:
            setattr(self._ad, nom, valeur)

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        hors, dans = consigne_sans_loi_gelee(consigne if isinstance(consigne, str) else "")
        ou = f"{self.tache}|etage|{role}"
        m = self._mesure
        m["consignes_cherchees"] += 1
        m["par_role"][role] = m["par_role"].get(role, 0) + 1
        m["touches_hors_loi_gelee"] += T.chercher_loi_plantee(self._monde, hors, {}, ou)
        m["touches_dans_la_loi_gelee"] += len(T.chercher_loi_plantee(self._monde, dans, {}, ou))
        return self._ad.lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)


def jetons_de_l_usage(usage):
    """{entree, sortie, usage} d'un champ `usage` de commande : Kimi (`prompt_tokens`, `completion_tokens`) ou Argon
    (`promptTokenCount`, `candidatesTokenCount` + `thoughtsTokenCount`) ; None si absent."""
    if not isinstance(usage, dict) or not usage:
        return {"entree": None, "sortie": None, "usage": None}
    if "prompt_tokens" in usage or "completion_tokens" in usage:
        e, s = usage.get("prompt_tokens"), usage.get("completion_tokens")
    else:
        e = usage.get("promptTokenCount")
        parts = [usage.get(k) for k in ("candidatesTokenCount", "thoughtsTokenCount") if usage.get(k) is not None]
        s = sum(parts) if parts else None
    return {"entree": e, "sortie": s, "usage": dict(usage)}


class ReleveDeJetons:
    """Jetons d'entrée et de sortie par appel (brouillon, section 5), lus dans le champ `usage` de la dernière ligne JSON que rend
    une commande externe : `instrumenter` enveloppe, **sur l'instance**, `lancer` et `lire_derniere_ligne` d'un adaptateur à
    commande (rien d'autre ne change) ; `rendu` donne les appels et les **sommes** par relais (aucune moyenne, aucune médiane)."""

    def __init__(self):
        self.appels = []

    def instrumenter(self, ad, relais):
        if getattr(ad, "_jetons_v66", False):
            return ad
        lancer, lire = ad.lancer, getattr(ad, "lire_derniere_ligne", None)
        etat = {"usage": None}

        def lire_derniere_ligne(sortie_octets):
            objet, motif = lire(sortie_octets)
            if isinstance(objet, dict) and isinstance(objet.get("usage"), dict):
                etat["usage"] = {k: v for k, v in objet["usage"].items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
            return objet, motif

        def lancer_mesure(role, consigne, dossier, budget_usd, max_tours, modele=None):
            etat["usage"] = None
            try:
                return lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)
            finally:
                self.appels.append(dict(jetons_de_l_usage(etat["usage"]), relais=relais, role=role))

        if lire is not None:
            ad.lire_derniere_ligne = lire_derniere_ligne
        ad.lancer = lancer_mesure
        ad._jetons_v66 = True
        return ad

    def rendu(self):
        sommes = {}
        for a in self.appels:
            s = sommes.setdefault(a["relais"], {"entree": 0, "sortie": 0, "appels_avec_usage": 0, "appels_sans_usage": 0})
            if a["entree"] is None and a["sortie"] is None:
                s["appels_sans_usage"] += 1
                continue
            s["appels_avec_usage"] += 1
            s["entree"] += a["entree"] or 0
            s["sortie"] += a["sortie"] or 0
        return {"source": "champ « usage » de la dernière ligne JSON des commandes externes", "appels": list(self.appels),
                "sommes_par_relais": sommes}


def lignes_de_tranche_servies(monde, racine, taches, episodes_servis):
    """Mesure de la v64 reprise : épisodes (z0, z1, g) des tranches des tâches `taches` présents parmi les épisodes servis aux
    proposeurs, comparés à six décimales (les épisodes servis sont arrondis à six décimales)."""
    tranche = set()
    for t in taches:
        tranche |= {(round(z0, DECIMALES_TRANCHE), round(z1, DECIMALES_TRANCHE), g) for z0, z1, g in T.lignes_de_tranche(monde, racine, t)}
    servis = {(round(z0, DECIMALES_TRANCHE), round(z1, DECIMALES_TRANCHE), g) for z0, z1, g in episodes_servis}
    return {"taches_comparees": len(taches), "episodes_servis": len(servis), "lignes_de_tranche": len(tranche),
            "communes": [list(x) for x in sorted(servis & tranche)], "precision": f"{DECIMALES_TRANCHE} décimales"}


# --- une génération du bras réel ----------------------------------------------------------------------------------------------


def tache_de(generation):
    return f"{VERSION}|bras=reel|generation={generation}"


def jouer_generation(dossier, generation, monde, jeu, heritage, ids_attendus, ids_plantees_avant, racine, fabrique_executeur,
                     proposeurs, etage, roles, decisions, plan, compteur, journal, releve, recherche, copies=(), moteur="simule",
                     environnement=None, permis_en_plus=(), archive_des_plantees=None, juger=None):
    """Une génération du bras réel : vue vérifiée (garde 23) → proposition → gardien → juge → **jugements écrits au relevé** →
    étage des cartes promues et étage des lois plantées promues (même tranche) → verdicts au relevé → sélection (garde 7) →
    bilan scellé. Rend (empreinte du bilan, ligne de journal)."""
    juger = juger or juger_v66
    tache = tache_de(generation)
    archive = heritage["archive"]
    plantees = B65.plantees_de_la_generation(jeu, generation, racine, tache, copies)
    ids_plantees_g = {c["identifiant"] for _, _, c, _ in plantees} | {r for _, r, _, _ in plantees}
    ids_plantees = set(ids_plantees_avant) | ids_plantees_g
    vue = bf.vue_pour_proposeur(heritage)
    contexte = T.contexte_du_proposeur(monde, vue, racine, tache)
    try:
        servie = exiger_vue_servie(contexte, ids_attendus, archive, ids_plantees)
    except VueServieRefusee as e:
        _incident(releve, 23, generation, e)
        raise
    consigne = T.CONSIGNE_PROPOSEUR.format(n=plan["cartes_par_proposeur"])
    sha_texte = hashlib.sha256(texte_servi(consigne, contexte).encode()).hexdigest()
    servie.update(attendus=sorted(ids_attendus), texte_sha256=sha_texte, appels=[])
    releve["vues_servies"][str(generation)] = servie
    cartes, refusees, appels, reels, enonces, proposeur_de = [], {}, [], {}, {}, {}
    for p in proposeurs:
        recherche["proposeurs"]["contextes_cherches"] += 1
        recherche["proposeurs"]["touches"] += T.chercher_loi_plantee(monde, consigne, contexte, f"{tache}|proposeur={p.nom}")
        recherche["episodes_servis"] |= {(e["z"][0], e["z"][1], e["g"]) for e in contexte["episodes_developpement"]}
        exiger_part_avant_appel(compteur, p.relais, p.budget)
        avant = len(getattr(p, "appels", None) or [])
        try:
            texte, cout = p.proposer(consigne, contexte, tache)
        except T.ArretTour as e:
            compteur.ajouter(e.cout, "proposeur", p.relais)
            raise
        compteur.ajouter(cout, "proposeur", p.relais)
        try:
            servie["appels"].append({"proposeur": p.nom, "texte_recu_sha256": exiger_texte_recu(p, avant, sha_texte)})
        except VueServieRefusee as e:
            _incident(releve, 23, generation, e)
            raise
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
    promues, promues_p, detail, m, attendus = juger(passees, plantees_passees, monde, archive, racine, tache, plan["m_e_bh"],
                                                    archive_des_plantees=archive_des_plantees)
    # CLV65-02 (a) : jugements au relevé avant tout étage
    releve["archives_de_jugement"][str(generation)] = json.loads(json.dumps(archive))
    releve["membres_attendus"][str(generation)] = attendus
    du_juge = ("promue_seule", "log_e", "log_richesse_max", "membres_d_archive", "membre_dominant_final", "empreinte_engagement",
               "graines")
    entrees_c, entrees_p = {}, {}
    for c in passees:
        i = c["identifiant"]
        e = dict({"generation": generation, "proposeur": proposeur_de[i], "identifiant": reels[i], "identifiant_servi": i,
                  "gardien": "passe", "promue": i in promues}, **{k: detail[i].get(k) for k in du_juge},
                 verdict=None, contre_calcul_ok=None, retenue=None, etage="en attente", loi=c["loi_predictive"], enonce=enonces.get(i))
        releve["cartes"].append(e)
        entrees_c[i] = e
    for i, motif in refusees.items():
        releve["cartes"].append({"generation": generation, "proposeur": proposeur_de.get(i), "identifiant": reels.get(i, i),
                                 "identifiant_servi": i, "gardien": "refuse", "motif": motif, "promue": False, "verdict": None,
                                 "retenue": False, "etage": "sans objet (refusée au gardien)", "enonce": enonces.get(i)})
    for nom, reel, c, source in plantees:
        i = c["identifiant"]
        d = detail.get(i, {})
        e = dict({"generation": generation, "nom": nom, "source": source, "identifiant": reel, "identifiant_servi": i,
                  "gardien": "refuse" if nom in plantees_refusees else "passe", "motif": plantees_refusees.get(nom),
                  "promue": i in promues_p}, **{k: d.get(k) for k in du_juge},
                 membres_attendus=attendus, verdict=None, contre_calcul_ok=None,
                 etage="en attente" if nom not in plantees_refusees else "sans objet (refusée au gardien)", loi=c["loi_predictive"])
        releve["plantees"].append(e)
        entrees_p[i] = e
    journal.append({"evenement": "jugement-ecrit", "generation": generation, "promues": promues, "plantees_promues": promues_p,
                    "membres_attendus": attendus, "m_e_bh": m})
    par_ident = {c["identifiant"]: c for c in passees}
    par_ident_p = {c["identifiant"]: (nom, c) for nom, c in plantees_passees}
    executeur, description_bac = fabrique_executeur()
    etage.tache = tache
    resume, chemin_sel, sha_sel, tranche, cc = T.jouer_etage(
        os.path.join(dossier, bf.DOSSIER_ETAGE), [par_ident[i] for i in promues], {i: c["loi_predictive"] for i, c in par_ident.items()},
        monde, racine, tache, executeur, etage, roles, compteur, journal, moteur=moteur, environnement=environnement,
        permis_en_plus=permis_en_plus)
    verdicts = T._verdicts(resume)
    for i, e in entrees_c.items():
        e.update(verdict=verdicts.get(i), contre_calcul_ok=cc[i]["ok"] if i in cc else None, etage="joué")
    executeur_p, _ = fabrique_executeur()
    resume_p, _, sha_sel_p, _, cc_p = T.jouer_etage(
        os.path.join(dossier, "etage-plantees"), [par_ident_p[i][1] for i in promues_p],
        {i: c["loi_predictive"] for i, (_, c) in par_ident_p.items()}, monde, racine, tache, executeur_p, etage, roles,
        compteur, journal, tranche=tranche, moteur=moteur, environnement=environnement, permis_en_plus=permis_en_plus)
    verdicts_p = T._verdicts(resume_p)
    for i, e in entrees_p.items():
        if e["gardien"] == "passe":
            e.update(verdict=verdicts_p.get(i), contre_calcul_ok=cc_p[i]["ok"] if i in cc_p else None, etage="joué")
    with open(chemin_sel, encoding="utf-8") as f:
        retenues = json.load(f)["retenues"]
    try:
        exiger_selection_sans_plantee(retenues, ids_plantees, tache)
    except T.TemoinRetenu as e:
        _incident(releve, 7, generation, e)
        raise
    for i, e in entrees_c.items():
        e["retenue"] = i in retenues
    comptes = {"proposees": len(reels), "refusees_au_gardien": len(refusees), "jugees": len(passees), "m_e_bh": m,
               "promues": len(promues), "testees": len(verdicts), "retenues": len(retenues), "plantees_promues": len(promues_p),
               "plantees_testees": len(verdicts_p), "appels_proposeurs": appels}
    graines = {"tache": tache, "par_carte": {i: d["graines"] for i, d in detail.items()}}
    sha_bilan = bf.ecrire_bilan_generation(dossier, generation=generation, bras="reel", cartes=passees, resume_etage=resume,
                                           chemin_selection=chemin_sel, sha_selection=sha_sel, archive_precedente=archive,
                                           heritage_lu=heritage, comptes=comptes, graines=graines)
    releve["retenues"][str(generation)] = list(retenues)
    releve["etages"].append({"generation": generation, "bac_a_sable": description_bac.get("nom"),
                             "factice": bool(description_bac.get("factice")), "selection_sha256": sha_sel,
                             "selection_plantees_sha256": sha_sel_p, "bilan_sha256": sha_bilan,
                             "contre_calculs": {"cartes": cc, "plantees": cc_p}})
    ligne = {"evenement": "generation", "generation": generation, "heritage_lu": heritage.get("bilan_sha256"),
             "archive_de_jugement": sorted(archive), "membres_attendus": attendus, "refusees_au_gardien": refusees,
             "plantees_refusees": plantees_refusees, "promues": promues, "plantees_promues": promues_p, "correspondance": reels,
             "verdicts": verdicts, "verdicts_plantees": verdicts_p, "retenues": retenues, "comptes": comptes,
             "selection_sha256": sha_sel, "bilan_sha256": sha_bilan, "depense": compteur.etat(),
             "vue_servie": servie["identifiants"], "log_e": {i: d.get("log_e") for i, d in detail.items()}}
    journal.append(ligne)
    return sha_bilan, ligne


# --- la boucle entière ----------------------------------------------------------------------------------------------------------


def _ids_plantees(releve):
    return {p.get("identifiant") for p in releve["plantees"]} | {p.get("identifiant_servi") for p in releve["plantees"]}


def jouer_boucle(sortie, *, monde, jeu, heritage_depart, racine, plan, decisions, proposeurs, adaptateur_etage, roles,
                 fabrique_executeur, compteur, reel=False, go=None, moteur="simule", environnement=None, permis_en_plus=(),
                 archive_des_plantees=None, lire=None, juger=None, jetons=None):
    """Génération 1 (héritage de départ {K1}), puis génération 2 (bilan de la génération 1 lu par `lire_heritage`), bras réel
    seul. Rend (relevé, journal) ; toute exception après le premier appel lève `ArretTour` avec le relevé partiel. Essais
    seulement : `lire` (lecture de l'héritage), `juger` (juge), `archive_des_plantees` ; `jetons` : un `ReleveDeJetons` (mode
    réel)."""
    exiger_bras(plan.get("bras", BRAS))
    exiger_go(reel, go)
    if plan.get("generations") != GENERATIONS:
        raise TourRefuse(f"générations : {plan.get('generations')!r} ; le code v66 joue la génération 1 et la génération 2 (D2)")
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
              "vues_servies": {}, "lecture_selection": None, "selection_finale": None, "incidents": [], "moteur_etage": moteur}
    recherche = {"proposeurs": {"contextes_cherches": 0, "touches": []}, "episodes_servis": set(),
                 "etage": {"consignes_cherchees": 0, "par_role": {}, "touches_hors_loi_gelee": [], "touches_dans_la_loi_gelee": 0}}
    etage = EtageMesure(adaptateur_etage, monde, recherche["etage"])
    commun = dict(racine=racine, fabrique_executeur=fabrique_executeur, proposeurs=proposeurs, etage=etage, roles=roles,
                  decisions=decisions, plan=plan, compteur=compteur, journal=journal, releve=releve, recherche=recherche,
                  moteur=moteur, environnement=environnement, permis_en_plus=permis_en_plus,
                  archive_des_plantees=archive_des_plantees, juger=juger)
    depart = sorted(heritage_depart["archive"])
    try:
        d1 = os.path.join(sortie, "generation-1")
        os.makedirs(d1)
        sha1, ligne1 = jouer_generation(d1, 1, monde, jeu, heritage_depart, depart, set(), **commun)
        releve["generations_jouees"].append(1)
        with open(os.path.join(d1, bf.DOSSIER_ETAGE, T.NOM_SELECTION), encoding="utf-8") as f:  # telle qu'écrite par la génération 1
            retenues_ecrites = json.load(f)["retenues"]
        vue_attendue = sorted(set(depart) | set(retenues_ecrites))
        ids_plantees = _ids_plantees(releve)
        try:
            h2 = lire(d1, sha1)
        except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:  # CLV65-02 (b) : le refus est consigné, empreinte sur disque
            releve["lecture_selection"] = {"attendu": sha1, "lu": empreinte_sur_disque(os.path.join(d1, bf.NOM_BILAN)),
                                           "refus": {"type": type(e).__name__, "motif": str(e)[:500]}, "vue": None,
                                           "vue_attendue": vue_attendue, "retenues_ecrites_g1": sorted(retenues_ecrites),
                                           "retenues_lues": None, "copies": None}
            raise ArretTour(f"héritage de la génération 1 refusé ({type(e).__name__}) : {e}") from e
        vue = bf.vue_pour_proposeur(h2)
        lecture = {"attendu": sha1, "lu": h2["bilan_sha256"], "lu_sur_disque": empreinte_sur_disque(os.path.join(d1, bf.NOM_BILAN)),
                   "refus": None, "empreintes_lues": h2["empreintes_lues"],
                   "vue": sorted(x["identifiant"] for x in vue["lois_retenues"]), "vue_attendue": vue_attendue,
                   "retenues_ecrites_g1": sorted(retenues_ecrites), "retenues_lues": sorted(h2["retenues"]), "copies": None}
        releve["lecture_selection"] = lecture
        try:
            T.exiger_sans_temoin(h2, ids_plantees)  # garde 7, moitié « ni servies » (v64, `tour_ferme_v64.py` l. 1106)
        except T.TemoinRetenu as e:
            _incident(releve, 7, 2, e)
            raise
        try:
            copies = B65.copies_de_la_selection(h2, {i: ligne1["log_e"].get(i) for i in h2["retenues"]})
            B65.exiger_copies_de_la_selection(copies, h2)
        except CopieNonRetenue as e:
            _incident(releve, 21, 2, e)
            raise
        lecture["copies"] = [{"nom": n, "source": s} for n, s, _ in copies]
        journal.append({"evenement": "heritage-lu", "generation": 2, "bilan_sha256": h2["bilan_sha256"], "archive": sorted(h2["archive"])})
        d2 = os.path.join(sortie, "generation-2")
        os.makedirs(d2)
        sha2, _ = jouer_generation(d2, 2, monde, jeu, h2, vue_attendue, ids_plantees, copies=copies, **commun)
        releve["generations_jouees"].append(2)
        ids_plantees |= _ids_plantees(releve)
        try:
            fin = lire(d2, sha2)  # la sélection de la génération 2 est scellée et relue ; aucune génération 3
        except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:
            releve["selection_finale"] = {"bilan_sha256": sha2, "lu": empreinte_sur_disque(os.path.join(d2, bf.NOM_BILAN)),
                                          "refus": {"type": type(e).__name__, "motif": str(e)[:500]}, "retenues": None}
            raise ArretTour(f"relecture de la sélection de la génération 2 refusée ({type(e).__name__}) : {e}") from e
        try:
            T.exiger_sans_temoin(fin, ids_plantees)  # garde 7, relecture finale (v64, l. 1134)
        except T.TemoinRetenu as e:
            _incident(releve, 7, "finale", e)
            raise
        releve["selection_finale"] = {"bilan_sha256": sha2, "lu": fin["bilan_sha256"], "refus": None, "retenues": sorted(fin["retenues"])}
        releve["complet"] = True
    except Exception as e:  # noqa: BLE001 — toute exception après le premier appel est un arrêt scellé, motif et type dits
        releve["arret"] = f"{type(e).__name__} : {str(e)[:500]}"
        journal.append({"evenement": "arret", "motif": releve["arret"], "depense": compteur.etat()})
    rp, re_ = recherche["proposeurs"], recherche["etage"]
    releve["recherche_loi_plantee"] = {
        "parametres_de_la_loi_plantee": len(T.parametres_de_la_loi_plantee(monde)), "formes": ["exacte", "deux décimales"],
        "proposeurs": {"contextes_cherches": rp["contextes_cherches"], "touches": rp["touches"]},
        "experimentateur_et_verificateur": {"consignes_cherchees": re_["consignes_cherchees"], "par_role": dict(re_["par_role"]),
                                            "touches_hors_loi_gelee": re_["touches_hors_loi_gelee"],
                                            "touches_dans_la_loi_gelee": re_["touches_dans_la_loi_gelee"]},
        "attendu": "aucune touche hors de la loi gelée servie au test de mort (que l'expérimentateur doit voir)"}
    try:
        releve["lignes_de_tranche_dans_les_contextes"] = lignes_de_tranche_servies(
            monde, racine, [tache_de(g) for g in (1, 2) if str(g) in releve["vues_servies"]], recherche["episodes_servis"])
    except Exception as e:  # noqa: BLE001 — mesure sans critère : son échec est dit, jamais tu
        releve["lignes_de_tranche_dans_les_contextes"] = {"erreur": f"{type(e).__name__} : {str(e)[:200]}"}
    releve["jetons"] = jetons.rendu() if jetons is not None else {
        "source": "non mesurés : aucun relevé de jetons branché (à blanc, doublures sans champ « usage »)"}
    releve["depense"] = compteur.etat()
    if releve["arret"]:
        raise ArretTour(releve["arret"], {"releve": releve, "journal": journal})
    return releve, journal


__all__ = ("VERSION", "BRAS", "GENERATIONS", "M_FIXE", "VRAIES", "FAUSSES", "INSTRUMENTS", "TourRefuse", "ArretTour", "GoAbsent",
           "BrasRefuse", "JeuPlanteRefuse", "HeritageDepartRefuse", "PlanteeSansArchive", "CopieNonRetenue", "VueServieRefusee",
           "empreinte_sur_disque", "juger_v66", "texte_servi", "exiger_vue_servie", "exiger_texte_recu",
           "exiger_selection_sans_plantee", "consigne_sans_loi_gelee", "EtageMesure", "jetons_de_l_usage", "ReleveDeJetons",
           "lignes_de_tranche_servies", "tache_de", "jouer_generation", "jouer_boucle")
