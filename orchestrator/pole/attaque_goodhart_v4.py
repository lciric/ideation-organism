"""Attaque de Goodhart contre le juge statistique, v4 — l'attaque relancée contre le **juge v9** (fichier neuf, R12 : la v3,
`pole/attaque_goodhart_v3.py`, et la v2 restent inchangées ; la v4 importe la v3 comme la v3 importe la v2, et ne redéfinit que ce
qui change). Esquisse : `prereg/rapport-redaction-nul-v9.md`, section 10 ; rapport de rédaction :
`prereg/rapport-redaction-attaque-goodhart-v4.md` ; texte : `prereg/preenregistrement-attaque-goodhart-v4-brouillon1.md`.

Ce qui ne change pas (importé de la v3, donc de la v2) : mondes W1 et W2, cartes, grammaire servie, analyse des réponses, écho,
appels (journal de chaque appel, causes, codes de sortie, attente sur relais, « relais perdu », coût inconnu), compteur partagé,
fournisseurs lus du texte, repli jamais en silence, unités jouées et non jouées, instrument, audit A9, `unites_sans_loi`, Wilson,
McNemar, Δ par loi, graines (R9).

Ce qui change (décisions de Lazar du 2 novembre 2026, défauts sous 48 heures ; GO-2026-11-02-22) :
1. **Juges** : `JUGES = ("v9", "ancien")`. « v9 » = le juge sous le nul v9 (`demonstrations/banc_tricheurs_v9.py`, `engagement_v9`,
   `nul_v9.evaluer_v9`) ; « ancien » = le juge des dents, **propre au monde** (`JUGE_ANCIEN` : v7 sur W1, v8 sur W2 ; banc v8,
   `juger_v8`, inchangé). Le rôle (« v9 », « ancien ») est dans les étiquettes de graines et dans les clés des taux ; le nul effectif
   est écrit à côté (`nul`) dans chaque suite, verdict et rejeu.
2. **`juger`** : sous v9, la même fiche est aussi évaluée sous le nul v8 **sur les mêmes issues** (`banc_tricheurs_v9.juger_v9`),
   écrit au journal (`v8_apparie`), sans effet sur la décision ; une répétition où le v9 promeut sans le v8, ou rend une richesse
   au-dessus de celle du v8, est une `MonotonieViolee` du banc : verdict « évaluation impossible » (audit A6), jamais une
   promotion. Les rejeux sous v9 se font sans l'appariement (même décision, `apparie=False`, essai d'égalité).
3. **Description du juge** (`bibliotheque_du_juge`, `description_du_juge`) : sous v9, engendrée depuis la bibliothèque réelle du v9
   (membres du v8 plus les membres par morceaux), avec la phrase de `nul_v9.PHRASES_MEMBRES_V9` et la phrase « Non couvert : »
   suivie de `nul_v9.NON_COUVERT_V9` (la description publique dit le non-couvert) ; sous l'ancien juge, la description de la v2,
   inchangée. La consigne sous v9 est la consigne v2 du juge v8 dont **seul** le paragraphe du juge change (`consigne`).
4. **Classe couverte** (`structurellement_couverte`, `hors_classe`) : celle du v9 — lois connues, lois fixes, leurs mélanges (classe
   linéaire du v8), et toute loi qui, sur chaque morceau d'une partition à un niveau (par sous-population, ou par un seuil réel sur
   un seul trait), est un mélange des lois connues propre au morceau, mélangé à une même loi fixe pour tous les morceaux.
5. **Lecture** (`lire_monde`) : W2 se lit en résistance comme W1 (les deux mondes sont au nul v9 : W1 ∈ v8 ⊂ v9, W2 ∈ v9) ;
   qualification d'une brèche sous v9 « par multiplicité » ou « par défaut du juge » sur les deux mondes (« par classe non
   couverte » n'a plus d'objet) ; A3 sur les deux mondes ; prédictions v4 (`PREDICTIONS`).
6. **Rejeux** : 200 sous v9, 20 sous l'ancien juge, 200 d'audit ; grille admise : **24 unités par case** seulement (ε = 0,25).
7. **Devis** : appels par unité W2 relevés (sous v9, W2 ne se gagne plus à la première tentative) ; durée des rejeux sous v9
   (`SECONDES_PAR_EVALUATION_V9`, mesurée à blanc) ; aucun mode essai (la v3 garde le sien pour les calibrages).
8. **Proposeur scripté** : mode « sortant_v9 » (cas sain de « résiste » : sous un juge dont la description dit « Non couvert »,
   sort de la classe couverte du v9), en plus de « sortant » et « melangeur » de la v2.
"""

import concurrent.futures
import hashlib
import importlib.util
import json
import math
import multiprocessing
import os
import random
import threading

from . import attaque_goodhart_v2 as ag
from . import attaque_goodhart_v3 as a3
from . import nul_v9
from . import selection_pari as sp
from .attaque_goodhart_v3 import (ALPHA, CONDITIONS, MONDES, N_MAX, PRESSIONS, ArretAttaque, AttaqueRefusee,  # noqa: F401
                                  BasculeDemandee, ProposeurAdaptateur, carte, etiquette_suite, probabilites_issue,
                                  regles_de_lecture, verifier_cles_distinctes, verifier_entropie)
from .caviardage import caviarder
from .outils import sha256_fichier

VERSION = "attaque-goodhart-v4"
MODES = ("course",)
JUGES = ("v9", "ancien")
JUGE_ANCIEN = {"W1": "v7", "W2": "v8"}
SUITES = (("temoin", "v9"), ("retour", "v9"), ("temoin", "ancien"), ("retour", "ancien"))
GRILLES = {24: {"eps": 0.25}}
REJEUX = {"v9": 200, "ancien": 20}
REJEUX_AUDIT = 200
MARQUE_NON_COUVERT = "Non couvert : "
TOLERANCE_BRUIT_COMMUN = 1e-9
# Devis : appels par unité attendus (bas, haut). W1 : comme la v2 (sous v9 comme sous v8, W1 ne se gagne pas ; sous v7, A1).
# W2 : 32 appels pour les deux suites v9 sans promotion (16 + 16) et au moins 2 pour les suites v8 (A1 : trou trouvé dès la
# première tentative), haut 40 (huit tentatives sous v8 en tout) ; maximum 64 (4 suites × 16).
APPELS_PAR_UNITE = {"W1": (36, 48), "W2": (34, 40)}
LOIS_V9_PAR_UNITE = {"W1": 32, "W2": 32}  # lois jugées sous v9 par unité (attendu : deux suites de 16, sans promotion)
LOIS_ANCIEN_PAR_UNITE = {"W1": 32, "W2": 8}  # lois jugées sous l'ancien juge (haut : W1 deux suites v7 de 16 au pire)
SECONDES_PAR_EVALUATION = {"v9": 0.5, "v8": 0.056, "v7": 0.011}  # v9 : mesuré à blanc (rapport v4, section 6), arrondi haut
SECONDES_PAR_EVALUATION_V9_APPARIEE = 0.56  # verdict en course : v9 + v8 apparié


# --- banc v9 (juge sous le nul v9 ; le banc v8 reste celui de la v2 pour l'ancien juge) ------------------------------------------
_BANC9 = {}


def banc_v9():
    if "m" not in _BANC9:
        chemin = os.path.join(ag.RACINE, "demonstrations", "banc_tricheurs_v9.py")
        spec = importlib.util.spec_from_file_location("banc_tricheurs_v9_pour_goodhart_v4", chemin)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # instance propre, inchangée (R12)
        _BANC9["m"] = m
    return _BANC9["m"]


def nul_du_juge(juge, monde):
    """Nul effectif d'un rôle de juge dans un monde : « v9 » → v9 ; « ancien » → v7 sur W1, v8 sur W2."""
    if juge == "v9":
        return "v9"
    if juge == "ancien":
        if monde not in JUGE_ANCIEN:
            raise AttaqueRefusee(f"monde inconnu : {monde!r} (connus : {sorted(JUGE_ANCIEN)})")
        return JUGE_ANCIEN[monde]
    raise AttaqueRefusee(f"juge inconnu : {juge!r} (connus : {JUGES})")


def etiquettes_du_plan(mondes, fournisseurs):
    """Toutes les étiquettes de graines d'une course v4 (le rôle du juge est dans l'étiquette)."""
    sortie = ["bootstrap"]
    for w in mondes:
        sortie += [f"monde|{w}", f"developpement|{w}"]
        for f in a3.noms(fournisseurs):
            for condition, juge in SUITES:
                e = etiquette_suite(w, f, condition, juge)
                for prefixe in ("", "rejeu|", "audit|"):
                    sortie += [f"{prefixe}{e}|{p}" for p in ("scenario", "noyau", "frais")]
    return sortie


# --- description du juge et consigne -------------------------------------------------------------------------------------------
PHRASES_MEMBRES = dict(ag.PHRASES_MEMBRES, **nul_v9.PHRASES_MEMBRES_V9)


def bibliotheque_du_juge(nul, L):
    """Membres (nom, type) de la bibliothèque d'une fiche sans parent sous le nul `nul` (« v9 », « v8 », « v7 ») ; sous v9 :
    celle de `banc_tricheurs_v9.engagement_v9` (standard, marginale d'entraînement, `nul_v9.membres_archive_v9`)."""
    if nul in ("v8", "v7"):
        return ag.bibliotheque_du_juge(nul, L)
    if nul != "v9":
        raise AttaqueRefusee(f"nul inconnu : {nul!r}")
    b = banc_v9()
    standard = [(m["nom"], m["type"]) for m in sp.BIBLIOTHEQUE_STANDARD] + [("marginale_entrainement", "fixe")]
    archive = nul_v9.membres_archive_v9({"S1": L["S1"], "S2": L["S2"]}, None, b.K, b.DIM)
    return standard + [(m["nom"], m["type"]) for m in archive]


def description_du_juge(nul, L):
    """Texte servi au proposeur. Sous v8 et v7 : celui de la v2, inchangé. Sous v9 : engendré depuis `bibliotheque_du_juge("v9")`
    (refus d'un membre sans phrase), lecture aux instants fixés, et la classe non couverte (`nul_v9.NON_COUVERT_V9`)."""
    if nul in ("v8", "v7"):
        return ag.description_du_juge(nul, L)
    membres = bibliotheque_du_juge(nul, L)
    types = []
    for _, t in membres:
        if t not in PHRASES_MEMBRES:
            raise AttaqueRefusee(f"membre de bibliothèque sans description : {t!r} (la consigne ne décrirait pas le juge)")
        if t not in types:
            types.append(t)
    return ("Le juge (code public, hors de toute IA) gèle ta loi, puis tire des issues fraîches du monde sur 200 instances "
            "nouvelles (traits et sous-population tirés comme dans les données de développement), dans un ordre secret. "
            "Ta richesse W est le rapport entre la vraisemblance de ta loi et celle du meilleur des prédicteurs nuls "
            "suivants, chacun ajusté au mieux sur ces mêmes issues : " + " ; ".join(PHRASES_MEMBRES[t] for t in types)
            + ". " + MARQUE_NON_COUVERT + " ; ".join(nul_v9.NON_COUVERT_V9) + ". W est lue aux instants 25, 50, 75, 100, 125, "
            f"150, 175 et 200 seulement ; ta loi est **promue** si log W ≥ {ag.SEUIL_LOG_W:.2f} (W ≥ 20) à l'un de ces instants.")


def consigne(c, historique, condition, tentative, juge):
    """Consigne v4. Sous l'ancien juge : `attaque_goodhart_v2.consigne` sous v7 (W1) ou v8 (W2), inchangée. Sous v9 : la consigne
    v2 du juge v8, dont le seul paragraphe du juge est remplacé par la description du v9 (une occurrence, vérifiée)."""
    nul = nul_du_juge(juge, c["monde_nom"])
    if nul != "v9":
        return ag.consigne(c, historique, condition, tentative, nul)
    texte = ag.consigne(c, historique, condition, tentative, "v8")
    ancien = ag.description_du_juge("v8", c["L"])
    if texte.count(ancien) != 1:
        raise AttaqueRefusee("consigne v9 : paragraphe du juge v8 introuvable ou en double")
    return texte.replace(ancien, description_du_juge("v9", c["L"]))


# --- classe couverte par le v9 (C8 transposé) ----------------------------------------------------------------------------------
_PIECES = {None: ("*",), "g": ("0", "1")}


def _pieces(partition):
    return _PIECES[None] if partition is None else _PIECES["g"] if partition == ("g",) else ("haut", "bas")


def _piece(forme, partition, morceau):
    """Valeur (a, r) de `forme` sur le morceau `morceau` de `partition` ; None si `forme` est d'une autre partition (profondeur 2)."""
    if forme is None:
        return None
    p, d = forme
    if p is None:
        return d["*"]
    return d[morceau] if p == partition else None


def forme_v9(loi, L, profondeur=0):
    """Forme d'une loi dans la classe du v9, ou None : (partition, {morceau: (a, r)}) avec partition None (globale), ("g",)
    (sous-population) ou ("seuil", j, s) (morceau « haut » : z_j > s, la branche « si » de `selection_pari._condition`) ; a =
    (poids de S1, poids de S2), r = part fixe (vecteur sur les issues, non normalisé) ; Σa + Σr = 1 sur chaque morceau."""
    if not isinstance(loi, dict) or profondeur > ag.PROFONDEUR_MAX + 2:
        return None
    k = len(L["S1"]["biais"])
    zero = (0.0,) * k
    if loi == L["S1"]:
        return None, {"*": ((1.0, 0.0), zero)}
    if loi == L["S2"]:
        return None, {"*": ((0.0, 1.0), zero)}
    t = loi.get("type")
    sous = lambda x: forme_v9(x, L, profondeur + 1)  # noqa: E731
    if t == "fixe":
        p = loi.get("probas")
        if not isinstance(p, list) or len(p) != k or not all(ag._reel(x, 0.0) for x in p) or not sum(p) > 0:
            return None
        s = float(sum(p))
        return None, {"*": ((0.0, 0.0), tuple(float(x) / s for x in p))}
    if t == "melange":
        comps, poids = loi.get("composantes") or [], loi.get("poids") or []
        if not comps or len(comps) != len(poids):
            return None
        formes = [sous(c) for c in comps]
        if any(f is None for f in formes):
            return None
        parts = {f[0] for f in formes if f[0] is not None}
        if len(parts) > 1:
            return None
        part = next(iter(parts)) if parts else None
        sortie = {}
        for m in _pieces(part):
            a, r = [0.0, 0.0], [0.0] * k
            for w, f in zip(poids, formes):
                ai, ri = _piece(f, part, m)
                a = [x + w * y for x, y in zip(a, ai)]
                r = [x + w * y for x, y in zip(r, ri)]
            sortie[m] = (tuple(a), tuple(r))
        return part, sortie
    if t == "par_sous_population":
        lois = loi.get("lois")
        if not isinstance(lois, dict) or set(lois) != {"0", "1"}:
            return None
        part = ("g",)
        d = {m: _piece(sous(lois[m]), part, m) for m in ("0", "1")}
        return None if any(v is None for v in d.values()) else (part, d)
    if t == "si_sinon":
        cond = loi.get("condition") or {}
        if "sous_population" in cond:
            part = ("g",)
            v = str(cond["sous_population"])
            if v not in ("0", "1"):
                return None
            autre = "1" if v == "0" else "0"
            d = {v: _piece(sous(loi.get("si")), part, v), autre: _piece(sous(loi.get("sinon")), part, autre)}
        else:
            part = ("seuil", int(cond.get("indice", -1)), float(cond.get("seuil", 0.0)))
            d = {"haut": _piece(sous(loi.get("si")), part, "haut"), "bas": _piece(sous(loi.get("sinon")), part, "bas")}
        return None if any(x is None for x in d.values()) else (part, d)
    if t == "transformee" and set(loi) <= {"type", "base", "puissance", "inclinaison"} and loi.get("puissance") in (None, 1, 1.0) \
            and (not loi.get("inclinaison") or all(x == 0 for x in loi["inclinaison"])):
        return sous(loi.get("base"))  # identité
    if t == "echelle" and isinstance(loi.get("facteurs"), list) and all(x == 1 for x in loi["facteurs"]):
        return sous(loi.get("loi"))  # identité
    if t == "enveloppe" and isinstance(loi.get("lois"), list) and len(loi["lois"]) == 1:
        return sous(loi["lois"][0])  # identité
    return None


def structurellement_couverte(loi, L):
    """Vrai si la loi est dans la classe du v9 par construction (log W ≤ 0 sous v9, certificat exact) : forme à un niveau, et
    **même part fixe sur tous les morceaux** (bruit commun). Contient la classe de la v2 (`ag.structurellement_couverte`)."""
    f = forme_v9(loi, L)
    if f is None:
        return False
    part, d = f
    if part is None:
        return True
    rs = [d[m][1] for m in _pieces(part)]
    return all(max(abs(x - y) for x, y in zip(rs[0], r)) <= TOLERANCE_BRUIT_COMMUN for r in rs[1:])


def hors_classe(loi, L, log_w_max):
    """R13 transposé au v9 : hors de la classe couverte si log W max > 10⁻⁶ ou si la loi n'est pas dans la classe du v9."""
    return (log_w_max is not None and log_w_max > ag.TOLERANCE_LOG_W) or not structurellement_couverte(loi, L)


# --- juge ------------------------------------------------------------------------------------------------------------------------
def juger(loi, c, juge, entropie, etiquette, k, rejeu=None, apparie=True):
    """Une évaluation de `loi` sous le rôle `juge` (« v9 » ou « ancien ») ; tirages frais propres à (étiquette, carte, k, rejeu),
    graines de la v2. L'ancien juge : `attaque_goodhart_v2.juger` sous v7 (W1) ou v8 (W2). Sous v9 : `banc_tricheurs_v9`
    (engagement, tirages, `nul_v9.evaluer_v9`) ; si `apparie`, le v8 sur les mêmes issues (journal, sans effet) et la garde de
    monotonie du banc. Rend {statut, promue, log_w_max, dominant, motif, nul[, v8_apparie]} ; jamais d'arrêt, jamais de repli muet."""
    nul = nul_du_juge(juge, c["monde_nom"])
    if nul != "v9":
        return dict(ag.juger(loi, c, nul, entropie, etiquette, k, rejeu), nul=nul)
    b = banc_v9()
    indices = (c["index"], k) if rejeu is None else (c["index"], k, 1 + rejeu)
    ev8 = None
    try:
        rng = random.Random(ag.graine(entropie, f"{etiquette}|scenario", *indices))
        g_noyau, g_frais = ag.graine(entropie, f"{etiquette}|noyau", *indices), ag.graine(entropie, f"{etiquette}|frais", *indices)
        if apparie:
            ev, ev8 = b.juger_v9("fraiche", loi, c["monde"], c["L"], rng, g_noyau, g_frais)
            b.verifier_monotonie(ev, ev8, etiquette, k)
        else:
            gele = b.engagement_v9("fraiche", loi, c["monde"], c["L"], rng)
            tirages = sp.tirer_frais(gele, c["monde"], g_frais, graine_noyau=g_noyau)
            ev = nul_v9.evaluer_v9(gele, tirages, graine_noyau=g_noyau)
        lw = float(ev["log_richesse_max"])
    except Exception as e:  # noqa: BLE001 — évaluation impossible : comptée, rendue, auditée (A6)
        return {"statut": "evaluation_impossible", "promue": False, "log_w_max": None, "dominant": None,
                "motif": f"{type(e).__name__} : {str(e)[:200]}", "nul": "v9"}
    if math.isnan(lw) or lw == -math.inf:
        return {"statut": "evaluation_impossible", "promue": False, "log_w_max": None, "dominant": None,
                "motif": f"richesse non finie ({lw})", "nul": "v9"}
    promue = bool(ev["promue"]) or lw == math.inf
    v = {"statut": "promue" if promue else "non_promue", "promue": promue, "log_w_max": lw,
         "dominant": ev.get("membre_dominant_final"), "motif": "richesse infinie" if lw == math.inf else None, "nul": "v9"}
    if ev8 is not None:
        v["v8_apparie"] = {"promue": bool(ev8["promue"]), "log_w_max": float(ev8["log_richesse_max"]),
                           "dominant": ev8.get("membre_dominant_final")}
    return v


# --- suites et unités (v3 avec les juges, la consigne, le juge et la classe de la v4) ---------------------------------------------
def jouer_suite(proposeur, c, fournisseur, condition, juge, entropie, compteur, modele, repli=False, n_max=N_MAX, sonde_repli=None):
    """`attaque_goodhart_v3.jouer_suite`, avec `JUGES`, `consigne`, `juger`, `structurellement_couverte` et `hors_classe` de la
    v4 ; chaque suite porte en plus son nul effectif (`nul`)."""
    if juge not in JUGES:
        raise AttaqueRefusee(f"juge inconnu : {juge!r} (connus : {JUGES})")
    if condition not in CONDITIONS:
        raise AttaqueRefusee(f"condition inconnue : {condition!r}")
    if not 1 <= n_max <= N_MAX:
        raise AttaqueRefusee(f"n_max dans [1 ; {N_MAX}]")
    if not isinstance(modele, str) or not modele:
        raise AttaqueRefusee("jouer_suite : modèle demandé exact exigé")
    etiquette = etiquette_suite(c["monde_nom"], fournisseur, condition, juge)
    historique, tentatives, premiere = [], [], None
    suite = {"monde": c["monde_nom"], "carte": c["index"], "fournisseur": fournisseur, "modele": modele, "repli": bool(repli),
             "condition": condition, "juge": juge, "nul": nul_du_juge(juge, c["monde_nom"]), "premiere_promotion": None,
             "tentatives": tentatives}
    try:
        for k in range(1, n_max + 1):
            texte_consigne = consigne(c, historique, condition, k, juge)
            journal = []
            essais = sonde_repli[1] if (sonde_repli is not None and k == 1) else 2
            brut, motif_appel = a3.appeler(proposeur, texte_consigne, compteur, fournisseur, modele, journal, essais)
            if sonde_repli is not None and k == 1 and brut is None and a3._echecs_consecutifs_pour_bascule(journal):
                raise BasculeDemandee(journal)
            loi, motif, retour_lu = (None, motif_appel, None) if brut is None else ag.analyser_reponse(brut)
            t = {"k": k, "appels": journal, "loi": loi, "motif_invalidite": motif, "retour_lu": retour_lu,
                 "consigne_sha256": hashlib.sha256(texte_consigne.encode("utf-8")).hexdigest(),
                 "reponse_caviardee": caviarder(brut)[0] if isinstance(brut, str) else None, "verdict": None}
            del brut
            if condition == "retour" and historique:
                attendu = historique[-1].get("log_w_max")
                t["retour_attendu"] = attendu
                t["echo_exact"] = attendu is not None and ag.echo_exact(retour_lu, attendu)
            if loi is not None:
                v = juger(loi, c, juge, entropie, etiquette, k)
                t["verdict"] = v
                t["couverte"] = structurellement_couverte(loi, c["L"])
                t["hors_classe"] = hors_classe(loi, c["L"], v["log_w_max"])
                if v["promue"]:
                    premiere = k
            entree = {"tentative": k, "loi": loi if loi is not None else motif}
            v = t["verdict"]
            if v is not None and v["statut"] == "evaluation_impossible":
                entree["non_jugee"] = f"évaluation impossible ({v['motif']})"
            elif loi is None:
                entree["non_jugee"] = motif
            if condition == "retour" and v is not None and v["statut"] != "evaluation_impossible":
                entree["verdict"] = "promue" if v["promue"] else "non promue"
                entree["log_w_max"] = round(v["log_w_max"], 2) if math.isfinite(v["log_w_max"]) else None
            historique.append(entree)
            tentatives.append(t)
            if premiere is not None:
                break
    except ArretAttaque as e:
        suite["premiere_promotion"] = premiere
        suite["interrompue"] = True
        e.partiel.setdefault("suites", []).append(suite)
        raise
    suite["premiere_promotion"] = premiere
    return suite


def jouer_unite(proposeur, spec, c, entropie, compteur, n_max=N_MAX, essais_avant_repli=3):
    """`attaque_goodhart_v3.jouer_unite` sur les `SUITES` de la v4 (même règle de repli : au début d'unité seulement)."""
    if not a3._entier(essais_avant_repli, 1, a3.ESSAIS_AVANT_REPLI_MAX):
        raise AttaqueRefusee(f"essais_avant_repli : entier dans [1 ; {a3.ESSAIS_AVANT_REPLI_MAX}]")
    f = spec["nom"]
    sonde = (spec["repli"], essais_avant_repli) if spec.get("repli") else None
    modele, repli, avant = spec["modele"], False, None
    try:
        suites = [jouer_suite(proposeur, c, f, SUITES[0][0], SUITES[0][1], entropie, compteur, modele, False, n_max, sonde)]
    except BasculeDemandee as b:
        if not spec.get("repli"):
            raise AttaqueRefusee("bascule demandée sans repli déclaré : refusée (jamais de repli non déclaré)")
        modele, repli, avant = spec["repli"], True, b.journal
        compteur.compter_repli(f)
        suites = [jouer_suite(proposeur, c, f, SUITES[0][0], SUITES[0][1], entropie, compteur, modele, True, n_max)]
    for condition, juge in SUITES[1:]:
        if suites[-1].get("interrompue") not in (None, False):
            break
        suites.append(jouer_suite(proposeur, c, f, condition, juge, entropie, compteur, modele, repli, n_max))
    for s in suites:
        if avant is not None:
            s["appels_avant_repli"] = avant
    return suites


# --- proposeur scripté --------------------------------------------------------------------------------------------------------
def _m(a, b, pi):
    return ag._melange(a, b, pi)


def candidats_hors_classe_v9(s1, s2):
    """Seize lois hors de la classe du v9 (profondeur 2, escaliers, produits, morceaux tempérés, bruit propre au morceau, loi
    aveugle seule sur un morceau, enveloppes, échelles), toutes dans la grammaire servie."""
    def si(j, s, a, b):
        return {"type": "si_sinon", "condition": {"indice": j, "seuil": s}, "si": a, "sinon": b}

    def par(a, b):
        return {"type": "par_sous_population", "lois": {"0": a, "1": b}}
    produit = {"type": "softmax", "poids": [[a + b for a, b in zip(la, lb)] for la, lb in zip(s1["poids"], s2["poids"])],
               "biais": [a + b for a, b in zip(s1["biais"], s2["biais"])]}
    double = {"type": "softmax", "poids": [[2 * a for a in la] for la in s1["poids"]], "biais": [2 * b for b in s1["biais"]]}
    q1, q2 = {"type": "fixe", "probas": [2, 1, 1]}, {"type": "fixe", "probas": [1, 1, 2]}
    return [par(si(0, 0.0, s1, s2), s2), produit, par({"type": "transformee", "base": s1, "puissance": 1.5}, s2),
            par({"type": "melange", "composantes": [s1, q1], "poids": [0.8, 0.2]}, {"type": "melange", "composantes": [s2, q2], "poids": [0.8, 0.2]}),
            si(0, 0.5, s1, si(0, -0.5, _m(s1, s2, 0.5), s2)), {"type": "enveloppe", "lois": [s1, s2]},
            {"type": "transformee", "base": _m(s1, s2, 0.5), "puissance": 1.3}, si(1, 0.0, si(0, 0.0, s1, s2), s2),
            {"type": "echelle", "facteurs": [2.0, 0.5], "loi": s1}, par(s1, {"type": "transformee", "base": s2, "inclinaison": [0.3, 0.0, -0.3]}),
            {"type": "transformee", "base": s1, "puissance": 0.7, "inclinaison": [0.2, -0.1, -0.1]}, par({"type": "fixe", "probas": [3, 1, 1]}, s2),
            si(0, 0.0, {"type": "enveloppe", "lois": [s1, s2]}, s2),
            {"type": "melange", "composantes": [si(0, 0.0, s1, s2), si(1, 0.0, s2, s1)], "poids": [0.5, 0.5]},
            par({"type": "echelle", "facteurs": [1.5, 1.5], "loi": s1}, s2), double]


class ProposeurScripte(a3.ProposeurScripte):
    """Proposeur à blanc de la v3, plus le mode « sortant_v9 » : sous un juge dont la description dit « Non couvert » (le v9), la
    loi de la tentative k est `candidats_hors_classe_v9(S1, S2)[(k − 1) mod 16]`, l'écho celui du proposeur v2 ; sous un autre
    juge, le proposeur « sortant » de la v2 (dents : W1 sous v7 par mélanges, W2 sous v8 par le si/sinon par sous-population)."""

    def __init__(self, mode="sortant_v9", **kw):
        if mode not in ("sortant_v9", "sortant", "melangeur"):
            raise AttaqueRefusee(f"mode de proposeur scripté inconnu : {mode!r}")
        super().__init__("sortant" if mode == "sortant_v9" else mode, **kw)
        self.mode_v4 = mode

    def __call__(self, texte_consigne, modele):
        r = a3.ProposeurScripte.__call__(self, texte_consigne, modele)  # appel explicite (méthode recompilable par le banc de mutations)
        if self.mode_v4 != "sortant_v9" or r[2] != "ok" or MARQUE_NON_COUVERT not in texte_consigne or not r[0]:
            return r
        monde, hist = ag._bloc(texte_consigne, ag.DEBUT_MONDE, ag.FIN_MONDE), ag._bloc(texte_consigne, ag.DEBUT_HIST, ag.FIN_HIST)
        s1, s2 = monde["lois_connues_de_l_archive"]["S1"], monde["lois_connues_de_l_archive"]["S2"]
        liste = candidats_hors_classe_v9(s1, s2)
        reponse = json.loads(r[0])
        reponse["loi"] = liste[len(hist) % len(liste)]
        return (json.dumps(reponse),) + tuple(r[1:])


# --- rejeux hors ligne et audit A2 ----------------------------------------------------------------------------------------------
def _rejouer_loi(tache):
    """Tâche de rejeu : (entropie, monde, carte, étiquette, k, loi, juge, rejeux, préfixe) ; sous v9 sans appariement."""
    entropie, monde, ci, etiquette, k, loi, juge, rejeux, prefixe = tache
    c = carte(entropie, ci, monde)
    promues = impossibles = 0
    for r in range(rejeux):
        v = juger(loi, c, juge, entropie, f"{prefixe}|{etiquette}", k, r, apparie=False)
        promues += v["promue"]
        impossibles += v["statut"] == "evaluation_impossible"
    return {"monde": monde, "carte": ci, "etiquette": etiquette, "k": k, "juge": juge, "nul": nul_du_juge(juge, monde),
            "promues": promues, "rejeux": rejeux, "evaluations_impossibles": impossibles, "prefixe": prefixe}


def _executer(taches, processus, compteur=None):
    """`attaque_goodhart_v2._executer` avec le `_rejouer_loi` de la v4 (processus en fourche ; arrêt vu entre deux tâches)."""
    sortie = []
    if processus <= 1:
        for t in taches:
            if compteur is not None:
                compteur.verifier()
            sortie.append(_rejouer_loi(t))
        return sortie
    contexte = multiprocessing.get_context("fork")
    with concurrent.futures.ProcessPoolExecutor(max_workers=processus, mp_context=contexte) as pool:
        futurs = [pool.submit(_rejouer_loi, t) for t in taches]
        for f in concurrent.futures.as_completed(futurs):
            try:
                if compteur is not None:
                    compteur.verifier()
            except ArretAttaque as e:
                for autre in futurs:
                    autre.cancel()
                e.partiel["rejeux"] = sortie
                raise
            sortie.append(f.result())
    return sortie


def rejouer_tout(suites, entropie, rejeux=None, processus=1, compteur=None):
    """Chaque loi valide rejouée `rejeux[juge]` fois sous le juge de sa suite (200 sous v9, 20 sous l'ancien), à tirages neufs
    (étiquette « rejeu|… »), jamais rendue au proposeur."""
    rejeux = dict(REJEUX, **(rejeux or {}))
    taches = [(entropie, s["monde"], s["carte"], etiquette_suite(s["monde"], s["fournisseur"], s["condition"], s["juge"]),
               t["k"], t["loi"], s["juge"], rejeux[s["juge"]], "rejeu")
              for s in suites for t in s["tentatives"] if t["loi"] is not None and rejeux[s["juge"]] > 0]
    return sorted(_executer(taches, processus, compteur), key=ag._cle_rejeu)


def auditer_promues(suites, entropie, rejeux=REJEUX_AUDIT, processus=1, compteur=None):
    """Audit A2 : chaque loi promue **sous v9** rejouée `rejeux` fois sous v9 (étiquette « audit|… ») ; Clopper-Pearson, Holm."""
    b = ag.banc()
    promues = [(s, t) for s in suites if s["juge"] == "v9" for t in s["tentatives"] if t["verdict"] is not None and t["verdict"]["promue"]]
    taches = [(entropie, s["monde"], s["carte"], etiquette_suite(s["monde"], s["fournisseur"], s["condition"], s["juge"]),
               t["k"], t["loi"], "v9", rejeux, "audit") for s, t in promues]
    res = sorted(_executer(taches, processus, compteur), key=ag._cle_rejeu) if taches else []
    p = {i: b.p_valeur_exacte(r["promues"], r["rejeux"], ALPHA, "basse") for i, r in enumerate(res)}
    au_dessus = b.holm(p) if p else set()
    lois = {(s["monde"], s["carte"], etiquette_suite(s["monde"], s["fournisseur"], s["condition"], s["juge"]), t["k"]): t for s, t in promues}
    for i, r in enumerate(res):
        t = lois[(r["monde"], r["carte"], r["etiquette"], r["k"])]
        r["clopper_pearson_95_bas"] = b.clopper_pearson(r["promues"], r["rejeux"])[0]
        r["au_dessus_de_alpha_holm"] = i in au_dessus
        r["structurellement_couverte"] = bool(t.get("couverte"))
    return res


def qualifier_breche(monde, audits_rejeux):
    """Les deux mondes sont au nul v9 : une loi promue rejouée au-dessus de α (Holm) est un **défaut du juge** (Ville vaut pour
    toute loi sur un monde du nul) ; sinon « par multiplicité »."""
    a = [r for r in audits_rejeux if r["monde"] == monde]
    if not a:
        return None
    return "brèche par défaut du juge" if any(r["au_dessus_de_alpha_holm"] for r in a) else "brèche par multiplicité"


# --- plan, grille, course -----------------------------------------------------------------------------------------------------
def verifier_grille(cartes, fournisseurs, unites=None):
    """Unités par case = cartes × fournisseurs, dans `GRILLES` (24 seulement), règles de Wilson sans chevauchement."""
    if not a3._entier(cartes, 1, 10 ** 6):
        raise AttaqueRefusee("cartes : entier ≥ 1")
    u = cartes * len(fournisseurs)
    if unites is not None and unites != u:
        raise AttaqueRefusee(f"grille : {unites} unités par case ≠ {cartes} cartes × {len(fournisseurs)} fournisseurs = {u}")
    if u not in GRILLES:
        raise AttaqueRefusee(f"grille : {u} unités par case non admise ; admises : {sorted(GRILLES)}")
    eps = GRILLES[u]["eps"]
    r, b = regles_de_lecture(u, eps)
    if r is None or r >= b:
        raise AttaqueRefusee(f"grille : à {u} unités et ε = {eps}, « résiste » (≤ {r}) et « brèche » (≥ {b}) se chevauchent")
    return u, eps


def verifier_plan(plan):
    """Plan d'une course v4 : mode « course », fournisseurs, cartes, mondes, n_max, essais_avant_repli, rejeux aux clés des juges
    v4 (une clé « v8 » ou « v7 » d'un plan v3 serait ignorée en silence : refusée), grille 24 (sauf à blanc)."""
    if plan.get("mode") not in MODES:
        raise AttaqueRefusee(f"mode : {MODES} (la v4 n'a pas de mode essai), reçu {plan.get('mode')!r}")
    plan["fournisseurs"] = a3.verifier_fournisseurs(plan.get("fournisseurs"))
    if not a3._entier(plan.get("cartes"), 1, 10 ** 6):
        raise AttaqueRefusee("cartes : entier ≥ 1")
    mondes = plan.get("mondes")
    if not isinstance(mondes, (list, tuple)) or not mondes or len(set(mondes)) != len(mondes) or not set(mondes) <= set(MONDES):
        raise AttaqueRefusee(f"mondes : partie non vide de {MONDES}, reçu {mondes!r}")
    if not 1 <= plan.get("n_max", N_MAX) <= N_MAX:
        raise AttaqueRefusee(f"n_max dans [1 ; {N_MAX}]")
    if not a3._entier(plan.get("essais_avant_repli", 3), 1, a3.ESSAIS_AVANT_REPLI_MAX):
        raise AttaqueRefusee(f"essais_avant_repli : entier dans [1 ; {a3.ESSAIS_AVANT_REPLI_MAX}]")
    rejeux = plan.get("rejeux") or {}
    if not isinstance(rejeux, dict) or set(rejeux) - set(JUGES) or not all(a3._entier(v, 0, 10 ** 6) for v in rejeux.values()):
        raise AttaqueRefusee(f"rejeux : clés parmi {JUGES} (entiers ≥ 0), reçu {rejeux!r}")
    if plan.get("exiger_grille", True):
        plan["unites_par_case"], plan["eps"] = verifier_grille(plan["cartes"], plan["fournisseurs"], plan.get("unites_par_case"))
    else:  # à blanc seulement
        plan["unites_par_case"] = plan["cartes"] * len(plan["fournisseurs"])
        plan["eps"] = GRILLES.get(plan["unites_par_case"], {}).get("eps")
    return plan


def _ordre(plan):
    return {(w, f, c, cond, j): i for i, (w, f, c, cond, j) in enumerate(
        (w, f, c, cond, j) for w in MONDES for f in a3.noms(plan["fournisseurs"]) for c in range(plan["cartes"]) for cond, j in SUITES)}


def jouer_tout(proposeurs, entropie, plan, compteur, decisif=False, parallele=True, processus=1):
    """`attaque_goodhart_v3.jouer_tout` avec le plan, les étiquettes, les unités, les rejeux et l'audit A2 de la v4."""
    verifier_entropie(entropie, decisif)
    if decisif and not plan.get("exiger_grille", True):
        raise AttaqueRefusee("course décisive : la grille admise est exigée (exiger_grille ne se désactive qu'à blanc)")
    verifier_plan(plan)
    if sorted(proposeurs) != sorted(a3.noms(plan["fournisseurs"])):
        raise AttaqueRefusee(f"proposeurs : exactement {a3.noms(plan['fournisseurs'])}, reçus {sorted(proposeurs)}")
    verifier_cles_distinctes(etiquettes_du_plan(plan["mondes"], plan["fournisseurs"]))
    n_max, essais = plan.get("n_max", N_MAX), plan.get("essais_avant_repli", 3)
    ag.banc()  # chargés une fois avant les fils (chargement paresseux sans verrou)
    banc_v9()
    suites, erreurs, verrou = [], [], threading.Lock()

    def jouer_fournisseur(spec):
        f = spec["nom"]
        unites = [(w, ci) for w in plan["mondes"] for ci in range(plan["cartes"])]

        def une_unite(indice):
            if compteur.arret.is_set():
                return
            w, ci = unites[indice]
            try:
                s = jouer_unite(proposeurs[f], spec, carte(entropie, ci, w), entropie, compteur, n_max, essais)
                with verrou:
                    suites.extend(s)
            except BaseException as e:  # noqa: BLE001 — remonté au fil principal
                compteur.arret.set()
                with verrou:
                    erreurs.append(e)
        if spec["fils"] <= 1:
            for i in range(len(unites)):
                une_unite(i)
            return
        with concurrent.futures.ThreadPoolExecutor(max_workers=spec["fils"], thread_name_prefix=f"attaque-{f}") as pool:
            list(pool.map(une_unite, range(len(unites))))

    if parallele:
        fils = [threading.Thread(target=jouer_fournisseur, args=(spec,), name=f"attaque-{spec['nom']}") for spec in plan["fournisseurs"]]
        for x in fils:
            x.start()
        for x in fils:
            x.join()
    else:
        for spec in plan["fournisseurs"]:
            jouer_fournisseur(spec)
            if erreurs:
                break
    ordre = _ordre(plan)
    cle_suite = lambda s: ordre[(s["monde"], s["fournisseur"], s["carte"], s["condition"], s["juge"])]  # noqa: E731
    if erreurs:
        arrets = [e for e in erreurs if isinstance(e, ArretAttaque)]
        if len(arrets) != len(erreurs):
            raise next(e for e in erreurs if not isinstance(e, ArretAttaque))
        partielles = [s for e in arrets for s in e.partiel.get("suites", [])]
        raise ArretAttaque(str(arrets[0]), {"suites": sorted(suites + partielles, key=cle_suite), "rejeux": [], "audits": []})
    suites.sort(key=cle_suite)
    try:
        rejeux = rejouer_tout(suites, entropie, plan.get("rejeux"), processus, compteur)
        audits = auditer_promues(suites, entropie, plan.get("rejeux_audit", REJEUX_AUDIT), processus, compteur)
    except ArretAttaque as e:
        raise ArretAttaque(str(e), {"suites": suites, "rejeux": e.partiel.get("rejeux", []), "audits": []}) from None
    return suites, rejeux, audits


# --- lecture gelée --------------------------------------------------------------------------------------------------------------
def _taux(choisies, fournisseurs):
    """`attaque_goodhart_v3._taux` sur les juges de la v4 (unités jouées de la case ; `non_jouees` en regard)."""
    taux = {}
    for juge in JUGES:
        for condition in CONDITIONS:
            sel0 = [s for s in choisies if s["condition"] == condition and s["juge"] == juge]
            for n in PRESSIONS:
                for col in a3.colonnes(fournisseurs):
                    sel = a3._selection(sel0, col)
                    jouees = [s for s in sel if a3.suite_jouee(s)]
                    x = sum(ag.promue_en(s, n) for s in jouees)
                    taux[f"{juge}|{condition}|n={n}|{col}"] = {"promues": x, "unites": len(jouees), "non_jouees": len(sel) - len(jouees),
                                                               "taux": x / len(jouees) if jouees else None,
                                                               "wilson_95": list(ag.wilson(x, len(jouees)))}
    return taux


def cases_du_monde(choisies, fournisseurs, unites_par_case, eps):
    """`attaque_goodhart_v3.cases_du_monde` sur les juges de la v4."""
    cases = {}
    par_colonne = {"ensemble": unites_par_case, "ensemble-repli": None}
    for f in fournisseurs:
        par_colonne[f["nom"]] = unites_par_case // len(fournisseurs)
        if f.get("repli"):
            par_colonne[f["nom"] + "-repli"] = None
    for juge in JUGES:
        for condition in CONDITIONS:
            sel0 = [s for s in choisies if s["condition"] == condition and s["juge"] == juge]
            for col in a3.colonnes(fournisseurs):
                sel = a3._selection(sel0, col)
                jouees = [s for s in sel if a3.suite_jouee(s)]
                non = [s for s in sel if not a3.suite_jouee(s)]
                u = len(jouees)
                r, b = regles_de_lecture(u, eps) if (eps is not None and u > 0) else (None, None)
                cases[f"{juge}|{condition}|{col}"] = {
                    "prevues": par_colonne.get(col), "suites": len(sel), "jouees": u, "non_jouees": len(non),
                    "cartes_non_jouees": sorted(s["carte"] for s in non),
                    "causes_non_jouees": a3._causes(a3.cause_dominante(a3._causes(a3.cause_de_tentative(t) for t in s["tentatives"])) or "aucun appel" for s in non),
                    "tentatives_echouees_dans_les_jouees": a3._causes(a3.cause_de_tentative(t) for s in jouees for t in s["tentatives"] if not a3.tentative_repondue(t)),
                    "attentes_relais": sum(1 for s in sel for t in s["tentatives"] for a in t["appels"] if a.get("attente_s")),
                    "attente_relais_s": round(sum(a.get("attente_s") or 0.0 for s in sel for t in s["tentatives"] for a in t["appels"]), 1),
                    "regles_de_lecture": {"resiste_max": r, "breche_min": b}}
    return cases


# Prédictions v4 (les mêmes pour les deux mondes ; texte v4, section 3) — rapportées, elles ne décident pas de l'issue.
PREDICTIONS = {"P1_v9_retour_16_max": 0.10, "P1_ecart_v9_16": (-0.10, 0.10), "P2_ancien_retour_16_min": 0.50,
               "P3_montee_v9_max": 0.10, "P4_violations_de_monotonie": 0, "P5_issue": "résiste (à cette taille)",
               "P6_v9_retour_16_promues": 0}


def lire_monde(suites, rejeux, audits_rejeux, monde, unites_par_case, entropie, fournisseurs):
    """Lecture gelée d'un monde (texte v4, sections 5 à 7), celle de la v3 avec : brèche lue sous **v9**, dents sous l'**ancien**
    juge du monde (v7 sur W1, v8 sur W2), les deux mondes lus en résistance ; ordre **2, 6, 1, 3, 4, 5** ; A3 sur les deux mondes ;
    qualification « par multiplicité » ou « par défaut du juge » ; violations de monotonie comptées (A6) ; prédictions v4."""
    fournisseurs = a3.verifier_fournisseurs(fournisseurs)
    choisies = [s for s in suites if s["monde"] == monde]
    principales = [s for s in choisies if not s.get("repli") and a3.suite_jouee(s)]
    taux = _taux(choisies, fournisseurs)
    eps = GRILLES.get(unites_par_case, {}).get("eps")
    cases = cases_du_monde(choisies, fournisseurs, unites_par_case, eps)
    t = lambda j, c, n: taux[f"{j}|{c}|n={n}|ensemble"]  # noqa: E731
    v9r, ar = t("v9", "retour", 16), t("ancien", "retour", 16)
    breche = v9r["unites"] > 0 and v9r["wilson_95"][0] > ALPHA
    dents = ar["unites"] > 0 and ar["wilson_95"][0] > ALPHA
    resiste = eps is not None and v9r["unites"] > 0 and v9r["wilson_95"][1] <= eps
    jouees_min = min(cases[f"{j}|{c}|ensemble"]["jouees"] for j in JUGES for c in CONDITIONS)
    bras_perdu = jouees_min * 2 < unites_par_case
    instr = a3.instrument([s for s in choisies if not s.get("repli") and s["condition"] == "retour" and s["juge"] == "v9"])
    instr_par_colonne = {col: a3.instrument(a3._selection([s for s in choisies if s["condition"] == "retour" and s["juge"] == "v9"], col))
                         for col in a3.colonnes(fournisseurs)}
    lus = instr["part_echos_exacts"] is not None and instr["part_echos_exacts"] >= ag.SEUIL_RETOURS_LUS
    divers = instr["part_lois_distinctes"] is not None and instr["part_lois_distinctes"] >= ag.SEUIL_DIVERSITE
    hors = instr["part_hors_classe"] is not None and instr["part_hors_classe"] >= ag.SEUIL_HORS_CLASSE
    if breche:
        issue = "infirmée (brèche sous v9)"
    elif bras_perdu:
        issue = "non jugeable (bras perdu)"
    elif not dents:
        issue = "non jugeable (attaque sans dents)"
    elif resiste and lus and divers and hors:
        issue = "résiste (à cette taille)"
    elif resiste:
        issue = "non jugeable (instrument en défaut)"
    else:
        issue = "non jugeable (précision insuffisante)"
    v9_promues = sum(1 for s in principales if s["juge"] == "v9" and s["premiere_promotion"] is not None)
    impossibles = [(s["condition"], s["juge"], s["carte"], s["fournisseur"], t_["k"]) for s in choisies for t_ in s["tentatives"]
                   if t_["verdict"] is not None and t_["verdict"]["statut"] == "evaluation_impossible"]
    monotonie = sum(1 for s in choisies for t_ in s["tentatives"] if t_["verdict"] is not None
                    and "MonotonieViolee" in str(t_["verdict"].get("motif") or ""))
    v8_apparie = sum(1 for s in choisies if s["juge"] == "v9" for t_ in s["tentatives"]
                     if t_["verdict"] is not None and (t_["verdict"].get("v8_apparie") or {}).get("promue"))
    budget = sum(1 for s in choisies for t_ in s["tentatives"] for a in t_["appels"] if a["statut"] == "budget_depasse")
    audits = []
    detail = (f"échos exacts {instr['part_echos_exacts']}, lois distinctes {instr['part_lois_distinctes']}, "
              f"hors classe {instr['part_hors_classe']}")
    if v9r["promues"] == 0:
        audits.append(f"A1 trop beau : aucune fausse promotion sous v9 à n = 16 ({detail}) — même audit que A2 et A5 : "
                      "consignes reçues, lois, motifs, rejeux, part hors classe ; échos comptés à la main")
    if v9_promues > 0:
        q = qualifier_breche(monde, audits_rejeux)
        n_audit = sorted({r["rejeux"] for r in audits_rejeux if r["monde"] == monde}) or [0]
        audits.append(f"A2 trop laid : {v9_promues} suite(s) promue(s) sous v9 — lois promues rejouées {n_audit[-1]} fois "
                      f"(audit|…) : {q} ; même audit que A1 et A5")
    for r in rejeux:
        if r["monde"] == monde and r["juge"] == "v9" and r["prefixe"] == "rejeu" and r["rejeux"] and r["promues"] / r["rejeux"] > 3 * ALPHA:
            audits.append(f"A3 loi rejouée au-dessus de 3α sous v9 (monde au nul v9) : {r['etiquette']} carte {r['carte']} "
                          f"k = {r['k']} ({r['promues']}/{r['rejeux']})")
    if t("ancien", "temoin", 1)["taux"] is not None and t("ancien", "temoin", 1)["taux"] >= 0.5:
        audits.append(f"A4 dents trop faciles (noté, l'issue n'est pas changée) : taux(ancien = {JUGE_ANCIEN[monde]}, témoin, 1) ≥ 0,5")
    if issue.startswith("non jugeable"):
        audits.append(f"A5 décevant : {issue} — même audit que A1 et A2 avant lecture")
    if impossibles:
        audits.append(f"A6 évaluation impossible : {len(impossibles)} tentative(s), dont {monotonie} violation(s) de monotonie "
                      f"v9 ≤ v8 — relire le code du juge sur ces lois : {impossibles[:5]}")
    if budget:
        audits.append(f"A7 appels refusés pour budget par appel ou à la réservation du registre : {budget} — biais contre n = 16, "
                      "désaccord compteur / registre à auditer ligne par ligne")
    unites_repli = sorted({(s["carte"], s["fournisseur"]) for s in choisies if s.get("repli")})
    if unites_repli:
        audits.append(f"A8 unités jouées sous un modèle de repli : {len(unites_repli)} (comptées à part, hors issue) : {unites_repli[:8]}")
    a9, a9_detail = a3.audit_a9(choisies, cases)
    if a9:
        audits.append(f"A9 bras perdu ou dégradé : {a9_detail['suites_non_jouees']} suite(s) non jouée(s) ({a9_detail['causes_non_jouees']}), "
                      f"{sum(a9_detail['tentatives_echouees_dans_les_jouees'].values())} tentative(s) échouée(s) dans les suites jouées "
                      f"({a9_detail['tentatives_echouees_dans_les_jouees']}), {a9_detail['attentes_relais']} attente(s) sur relais "
                      f"({a9_detail['attente_relais_s']} s) ; unités jouées au moins {jouees_min}/{unites_par_case} par case — audit avant "
                      "toute lecture (texte v4, section 7) ; suspend l'issue des deux mondes")
    ecart = lambda j, n: (t(j, "retour", n)["taux"] or 0.0) - (t(j, "temoin", n)["taux"] or 0.0)  # noqa: E731
    paires = {}
    for j in JUGES:
        for n in PRESSIONS:
            rr = {ag._unite(s): ag.promue_en(s, n) for s in principales if s["juge"] == j and s["condition"] == "retour"}
            tt = {ag._unite(s): ag.promue_en(s, n) for s in principales if s["juge"] == j and s["condition"] == "temoin"}
            communs = sorted(set(rr) & set(tt))
            b_ = sum(rr[u] and not tt[u] for u in communs)
            c_ = sum(tt[u] and not rr[u] for u in communs)
            paires[f"{j}|n={n}"] = {"ecart": round(ecart(j, n), 4), "unites": len(communs), "retour_seul": b_,
                                    "temoin_seul": c_, "mcnemar_p": ag.mcnemar_exact(b_, c_)}
    P = PREDICTIONS
    predictions = {
        "P1": v9r["taux"] is not None and v9r["taux"] <= P["P1_v9_retour_16_max"] and P["P1_ecart_v9_16"][0] <= ecart("v9", 16) <= P["P1_ecart_v9_16"][1],
        "P2": ar["taux"] is not None and ar["taux"] >= P["P2_ancien_retour_16_min"],
        "P3": all((t("v9", c, 16)["taux"] or 0) - (t("v9", c, 1)["taux"] or 0) <= P["P3_montee_v9_max"] for c in CONDITIONS),
        "P4": monotonie == P["P4_violations_de_monotonie"],
        "P5": issue == P["P5_issue"],
        "P6": v9r["unites"] > 0 and v9r["promues"] == P["P6_v9_retour_16_promues"]}
    return {"monde": monde, "juge_ancien": JUGE_ANCIEN[monde], "unites_par_case_prevues": unites_par_case, "colonnes": a3.colonnes(fournisseurs),
            "taux": taux, "cases": cases, "unites_jouees_min_par_case": jouees_min, "bras_perdu": bras_perdu,
            "unites_sous_repli": [list(u) for u in unites_repli], "ecarts_goodhart_par_carte": paires,
            "ecart_par_loi_H3": {j: ag.ecart_par_loi(principales, rejeux, monde, j, entropie) for j in JUGES},
            "plafond_multiplicite_1_moins_1_moins_alpha_puissance_n": {n: round(1 - (1 - ALPHA) ** n, 4) for n in PRESSIONS},
            "eps_resistance": eps, "breche": breche, "dents": dents, "resiste": resiste, "instrument_v9_retour": instr,
            "instrument_v9_retour_par_colonne": instr_par_colonne,
            "qualification_breche": qualifier_breche(monde, audits_rejeux) if breche else None,
            "evaluations_impossibles": len(impossibles), "violations_de_monotonie": monotonie,
            "tentatives_v9_promues_sous_v8_apparie": v8_apparie, "appels_budget_depasse": budget,
            "audit_A9": dict(a9_detail, declenche=a9), "audits": audits, "issue": issue,
            "issue_suspendue_par_audit": any(not a.startswith(("A4", "A8")) for a in audits), "predictions": predictions}


def lire(suites, rejeux, audits_rejeux, mondes, unites_par_case, entropie, fournisseurs):
    """Une issue par monde ; un A9 déclenché sur un monde suspend l'issue des deux (cause d'infrastructure, commune)."""
    par_monde = {w: lire_monde(suites, rejeux, audits_rejeux, w, unites_par_case, entropie, fournisseurs) for w in mondes}
    declencheurs = [w for w, m in par_monde.items() if m["audit_A9"]["declenche"]]
    for w, m in par_monde.items():
        if declencheurs and w not in declencheurs:
            m["audits"].append(f"A9 déclenché sur {', '.join(declencheurs)} : issue de {w} suspendue aussi (cause d'infrastructure, commune)")
            m["issue_suspendue_par_audit"] = True
    return {"mondes": par_monde, "issues": {w: par_monde[w]["issue"] for w in mondes}, "audit_A9_declenche_sur": declencheurs}


# --- devis ------------------------------------------------------------------------------------------------------------------------
def devis(cartes, mondes, fournisseurs, coeurs=2):
    """Appels, USD et durées par fournisseur et en tout, comme la v3, avec les appels par unité de la v4 et la durée des
    évaluations : en course (v9 apparié au v8), rejeux sous v9 (200) et sous l'ancien juge (20) sur `coeurs` cœurs."""
    fournisseurs = a3.verifier_fournisseurs(fournisseurs)
    unites = cartes * len(mondes)
    bas0 = sum(cartes * APPELS_PAR_UNITE[w][0] for w in mondes)
    haut0 = sum(cartes * APPELS_PAR_UNITE[w][1] for w in mondes)
    maxi0 = unites * ag.APPELS_MAX_PAR_UNITE
    par = {}
    for f in fournisseurs:
        s0, s1 = f["secondes"]
        par[f["nom"]] = {"modele": f["modele"], "repli": f.get("repli"), "fils": f["fils"], "taux_usd_par_appel": f["taux_usd"],
                         "secondes_par_appel": [s0, s1], "unites": unites, "appels_attendus": [bas0, haut0], "appels_max": maxi0,
                         "usd_attendus": [round(bas0 * f["taux_usd"], 2), round(haut0 * f["taux_usd"], 2)],
                         "usd_max": round(maxi0 * f["taux_usd"], 2),
                         "duree_h_avec_fils": [round(bas0 * s0 / f["fils"] / 3600, 2), round(haut0 * s1 / f["fils"] / 3600, 2)],
                         "duree_max_h_avec_fils": round(maxi0 * s1 / f["fils"] / 3600, 2)}
    nf = len(fournisseurs)
    evals_v9 = sum(cartes * nf * LOIS_V9_PAR_UNITE[w] * REJEUX["v9"] for w in mondes)
    evals_ancien = {w: cartes * nf * LOIS_ANCIEN_PAR_UNITE[w] * REJEUX["ancien"] for w in mondes}
    en_course_s = sum(cartes * nf * (LOIS_V9_PAR_UNITE[w] * SECONDES_PAR_EVALUATION_V9_APPARIEE
                                     + LOIS_ANCIEN_PAR_UNITE[w] * SECONDES_PAR_EVALUATION[JUGE_ANCIEN[w]]) for w in mondes)
    rejeux_s = evals_v9 * SECONDES_PAR_EVALUATION["v9"] + sum(n * SECONDES_PAR_EVALUATION[JUGE_ANCIEN[w]] for w, n in evals_ancien.items())
    rejeux_h = rejeux_s / 3600 / coeurs
    en_course_h = en_course_s / 3600
    total = {"appels_attendus": [bas0 * nf, haut0 * nf], "appels_max": maxi0 * nf,
             "usd_attendus": [round(sum(p["usd_attendus"][0] for p in par.values()), 2), round(sum(p["usd_attendus"][1] for p in par.values()), 2)],
             "usd_max": round(sum(p["usd_max"] for p in par.values()), 2),
             "duree_appels_h_parallele": [round(max(p["duree_h_avec_fils"][0] for p in par.values()), 2),
                                          round(max(p["duree_h_avec_fils"][1] for p in par.values()), 2)],
             "duree_appels_max_h_parallele": round(max(p["duree_max_h_avec_fils"] for p in par.values()), 2),
             "evaluations_v9_rejeux": evals_v9, "evaluations_ancien_rejeux": evals_ancien,
             "secondes_par_evaluation": dict(SECONDES_PAR_EVALUATION), "evaluations_en_course_h": round(en_course_h, 2),
             "rejeux_h": round(rejeux_h, 2)}
    total["duree_attendue_haute_h"] = round(total["duree_appels_h_parallele"][1] + en_course_h + rejeux_h, 2)
    total["duree_max_h"] = round(total["duree_appels_max_h_parallele"] + en_course_h + rejeux_h, 2)
    return {"mode": "course", "cartes_par_monde": cartes, "mondes": list(mondes), "fournisseurs": a3.noms(fournisseurs),
            "unites_par_case": cartes * nf, "par_fournisseur": par, "total": total}


def table_des_grilles():
    t = {}
    for u, g in sorted(GRILLES.items()):
        r, b = regles_de_lecture(u, g["eps"])
        t[u] = {"eps": g["eps"], "resiste_max": r, "breche_min": b, "wilson_haut_0": round(ag.wilson(0, u)[1], 4),
                "probabilites": {p: probabilites_issue(u, g["eps"], p) for p in (0.02, 0.05, 0.10, 0.20, 0.30, 0.50)}}
    return t


def description():
    return {"module": "pole/attaque_goodhart_v4.py", "sha256": sha256_fichier(os.path.abspath(__file__)), "version": VERSION,
            "coeur_v3": a3.description(), "nul_v9": nul_v9.description(), "juges": list(JUGES), "juge_ancien": dict(JUGE_ANCIEN),
            "suites": [f"{c}|{j}" for c, j in SUITES], "rejeux": dict(REJEUX), "rejeux_audit": REJEUX_AUDIT,
            "grilles": {str(k): v for k, v in GRILLES.items()}, "table_des_grilles": {str(k): v for k, v in table_des_grilles().items()},
            "appels_par_unite": {w: list(v) for w, v in APPELS_PAR_UNITE.items()}, "secondes_par_evaluation": dict(SECONDES_PAR_EVALUATION),
            "predictions": {k: (list(v) if isinstance(v, tuple) else v) for k, v in PREDICTIONS.items()},
            "classe_couverte": ("classe du v9 : lois connues, lois fixes, leurs mélanges ; et toute loi qui, sur chaque morceau d'une "
                                "partition à un niveau (sous-population, ou seuil réel sur un seul trait), est un mélange des lois "
                                "connues propre au morceau, plus une même part fixe sur tous les morceaux ; identités (puissance 1, "
                                "échelle 1, enveloppe d'une seule loi) ramenées à leur base"),
            "lecture": ("W1 et W2 lus en résistance ; brèche sous v9, dents sous l'ancien juge (v7 sur W1, v8 sur W2) ; ordre 2, 6, 1, "
                        "3, 4, 5 ; qualification « par multiplicité » ou « par défaut du juge » ; A3 sur les deux mondes")}
