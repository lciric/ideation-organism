"""Attaque de Goodhart contre le juge statistique, v5 — les mondes **W2 et W2 gradué (W2g)** contre le **juge v9** (fichier
neuf, R12 : la v4, `pole/attaque_goodhart_v4.py`, la v3 et la v2 restent inchangées ; la v5 importe la v4 et ne redéfinit que ce
qui change). Texte : `prereg/preenregistrement-attaque-goodhart-v4-brouillon3.md` du dépôt de travail (sections 0.6, 2 à 6, 11),
périmètre des mondes tranché par Lazar le 8 novembre 2026 (R-1890 : W2 + W2 gradué).

Ce qui ne change pas (importé de la v4, donc de la v3 et de la v2) : juges « v9 » et « ancien », description du juge v9 et
consigne (le paragraphe du juge seul), classe couverte du v9 (`structurellement_couverte`, `hors_classe`), proposeur scripté
« sortant_v9 », cartes de W2, grammaire servie, écho, appels, compteur, étiquettes de graines (R9), Wilson, McNemar, Δ par loi,
lecture de W2 (`attaque_goodhart_v4.lire_monde`, ordre 2, 6, 1, 3, 4, 5), audit A2, grille admise (24 unités, ε = 0,25).

Ce qui change :
1. **Mondes** : `MONDES = ("W2", "W2g")` ; W1 retiré (membre du v8 ⊂ v9 : la course n'y éprouverait que le code et la
   multiplicité, note W2 § 2). Le juge des dents (« ancien ») est le **v8 sur les deux mondes** (`JUGE_ANCIEN`).
2. **Monde W2 gradué** (`monde_w2g`, `carte_w2g`, `verifier_dose`, `ecart_w2g`) : famille de mondes paramétrée par une **dose
   λ ∈ [0 ; 1]**. Loi du monde : S1 sur la sous-population g = 0 ; sur g = 1, le mélange (1 − λ)·S2 + λ·N, où S1 et S2 sont les
   lois connues de l'archive et N une **loi neuve** (softmax tirée au hasard, `banc_tricheurs_v7._monde_lois`, comme la loi
   neuve des lignes « fille neuve » et « F03 » du banc du v9), tirée **par carte, de la graine de la carte** (étiquette
   « monde|W2g »), jamais servie au proposeur.
   - λ = 0 : la loi est, **à l'octet**, `attaque_goodhart_v2.monde_w2(L)` (recombinaison pure, membre du nul v9) ;
   - λ > 0 : `{"type": "par_sous_population", "lois": {"0": S1, "1": {"type": "melange", "composantes": [S2, N],
     "poids": [1 − λ, λ]}}}` ; à λ = 1, S1 sur g = 0 et N seule sur g = 1 ;
   - **une seule définition de l'écart** (`ecart_w2g`) : l'écart entre le monde W2g(λ) et la recombinaison pure W2 (λ = 0),
     mesuré dans l'espace où le juge lit les lois — la vraisemblance des issues sachant l'instance —, est la **divergence de
     Kullback-Leibler moyenne par instance**, E_x KL(P_λ(· | x) ‖ P_0(· | x)), estimée sur une grille fixe de `INSTANCES_ECART`
     instances tirées de la graine fixe `GRAINE_ECART` (traits et sous-population tirés comme les instances du juge). Sur g = 0
     le terme est nul ; sur g = 1 c'est KL((1 − λ)·S2 + λ·N ‖ S2), convexe en λ et nul en λ = 0, donc **l'écart croît avec λ**
     (au sens large) et ne s'annule qu'en λ = 0 (N ≠ S2 presque sûrement). Comme W2 est un membre du v9, cet écart majore
     l'écart du monde à toute recombinaison par morceaux des lois d'archive ; il est écrit dans la vérité de la carte
     (`verite.ecart_kl_vers_w2`) et au rapport, jamais servi au proposeur.
   - La **vérité du monde** (N, λ, écart) vit dans `carte["verite"]`, hors de `carte["description"]` ; la description servie
     est celle de W2 (mêmes clés : lois d'archive S1 et S2, données de développement tirées du monde). Garde
     `verifier_verite_non_servie` : toute consigne de W2g qui contiendrait la loi neuve N ou la clé « verite » lève
     `VeriteServie` (R5 : cas sain et artefact dans les essais).
3. **Dose lue du plan** : `plan["dose_w2g"]` (ligne `dose_w2g` du bloc `plan-gele`, lue par le lanceur v5), exigée dès que
   W2g est joué ; refusée hors de la grille gelée `GRILLE_DOSES_W2G` de l'épreuve hors ligne « W2 gradué »
   (`demonstrations/epreuve_w2g_dose_v1.py`), refusée à 0 (W2g serait W2) ; écrite au manifeste et dans chaque carte.
4. **Lecture de W2g** (`lire_monde_w2g`, texte § 6.2) : critères neufs **sans zone morte**, ordre **2′, 6′, 1′, 3′, 4′, 5′** ;
   r = part des lois promues sous v9 (toutes conditions) rejouées au-dessus de α après Holm (audit A2) ; « frontière franchie »
   qualifiée « robuste » (r ≥ 0,5) ou « par le bruit » (r < 0,5) ; « frontière non franchie (à cette taille) » ; A1 sur
   « 2′ robuste, r = 1, Δ₁₆ ≥ +0,5 » et sur « 3′ à 0/24 » ; A2 sur « 2′ par le bruit » ; **pas d'A3** (une loi rejouée au-dessus
   de 3α est une découverte, comptée dans r) ; A4, A5, A6, A7, A8, A9 comme la v4 ; prédictions P7 à P11 (`PREDICTIONS_W2G`).
5. **Devis** : W2g pris comme W2 (appels, lois jugées ; texte § 12).
6. **Étiquettes** : celles de la v4 (`etiquettes_du_plan`) sur les mondes W2 et W2g ; aucune étiquette de W1.
"""

import concurrent.futures
import hashlib
import json
import math
import multiprocessing
import os
import random
import threading

from . import attaque_goodhart_v2 as ag
from . import attaque_goodhart_v3 as a3
from . import attaque_goodhart_v4 as a4
from . import selection_pari as sp
from .attaque_goodhart_v3 import (ALPHA, CONDITIONS, N_MAX, PRESSIONS, ArretAttaque, AttaqueRefusee,  # noqa: F401
                                  BasculeDemandee, ProposeurAdaptateur, etiquette_suite, regles_de_lecture,
                                  verifier_cles_distinctes, verifier_entropie)
from .attaque_goodhart_v4 import (GRILLES, JUGES, MODES, REJEUX, REJEUX_AUDIT, SUITES, ProposeurScripte,  # noqa: F401
                                  banc_v9, bibliotheque_du_juge, candidats_hors_classe_v9, description_du_juge,
                                  etiquettes_du_plan, hors_classe, structurellement_couverte, verifier_grille)
from .caviardage import caviarder
from .outils import sha256_fichier

VERSION = "attaque-goodhart-v5"
MONDES = ("W2", "W2g")
JUGE_ANCIEN = {"W2": "v8", "W2g": "v8"}
# Grille gelée des doses de l'épreuve hors ligne « W2 gradué » (texte § 4 : λ* = plus petite dose de la grille où la loi du
# monde est promue par le v9 avec une probabilité ≥ 0,80 sur 1 000 répétitions et la recombinaison pure jamais) ; une dose de
# course hors de cette grille est refusée (`verifier_plan`).
GRILLE_DOSES_W2G = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00)
TOLERANCE_DOSE = 1e-9
GRAINE_ECART = 2026  # graine fixe de la grille d'instances de l'écart (indépendante de la course : l'écart décrit le monde)
INSTANCES_ECART = 400
SEUIL_ROBUSTE = 0.5  # texte § 6.2 : « robuste » si r ≥ 0,5
SEUIL_A1_ECART_W2G = 0.5  # A1 sur W2g : 2′ robuste avec r = 1 et Δ₁₆ ≥ +0,5
# Devis (texte § 12 : W2g pris comme W2).
APPELS_PAR_UNITE = {"W2": a4.APPELS_PAR_UNITE["W2"], "W2g": a4.APPELS_PAR_UNITE["W2"]}
LOIS_V9_PAR_UNITE = {"W2": a4.LOIS_V9_PAR_UNITE["W2"], "W2g": a4.LOIS_V9_PAR_UNITE["W2"]}
LOIS_ANCIEN_PAR_UNITE = {"W2": a4.LOIS_ANCIEN_PAR_UNITE["W2"], "W2g": a4.LOIS_ANCIEN_PAR_UNITE["W2"]}
SECONDES_PAR_EVALUATION = dict(a4.SECONDES_PAR_EVALUATION)
SECONDES_PAR_EVALUATION_V9_APPARIEE = a4.SECONDES_PAR_EVALUATION_V9_APPARIEE


class VeriteServie(AttaqueRefusee):
    """La vérité du monde W2g (loi neuve N, dose) a été trouvée dans un texte destiné au proposeur : arrêt, jamais d'appel."""


# --- juges (rôle → nul effectif) -------------------------------------------------------------------------------------------------
def nul_du_juge(juge, monde):
    """Nul effectif d'un rôle de juge dans un monde : « v9 » → v9 ; « ancien » → v8 sur W2 et sur W2g (le v7 n'est plus joué)."""
    if juge == "v9":
        return "v9"
    if juge == "ancien":
        if monde not in JUGE_ANCIEN:
            raise AttaqueRefusee(f"monde inconnu : {monde!r} (connus : {sorted(JUGE_ANCIEN)})")
        return JUGE_ANCIEN[monde]
    raise AttaqueRefusee(f"juge inconnu : {juge!r} (connus : {JUGES})")


# --- monde W2 gradué --------------------------------------------------------------------------------------------------------------
def verifier_dose(dose):
    """Dose λ : nombre réel fini dans [0 ; 1] (ni booléen, ni texte) ; rend `float(dose)`. Toute autre valeur : refus."""
    if isinstance(dose, bool) or not isinstance(dose, (int, float)):
        raise AttaqueRefusee(f"dose : nombre réel dans [0 ; 1] exigé, reçu {dose!r}")
    d = float(dose)
    if not math.isfinite(d) or d < 0.0 or d > 1.0:
        raise AttaqueRefusee(f"dose : nombre réel dans [0 ; 1] exigé, reçu {dose!r}")
    return d


def monde_w2g(L, dose):
    """Loi du monde W2 gradué à la dose λ : S1 sur g = 0 ; (1 − λ)·S2 + λ·N sur g = 1. À λ = 0, **à l'octet** la loi de W2
    (`attaque_goodhart_v2.monde_w2`, membre du nul v9) ; à λ > 0, le mélange de S2 et de la loi neuve N (poids [1 − λ, λ])."""
    d = verifier_dose(dose)
    if d == 0.0:
        return ag.monde_w2(L)
    if "N" not in L:
        raise AttaqueRefusee("monde W2g : la loi neuve N manque aux lois de la carte")
    melange = {"type": "melange", "composantes": [L["S2"], L["N"]], "poids": [1.0 - d, d]}
    return {"type": "par_sous_population", "lois": {"0": L["S1"], "1": melange}}


def instances_ecart():
    """Grille fixe d'instances (traits gaussiens, sous-population équiprobable, comme `selection_pari.tirer_instances`) sur
    laquelle l'écart est estimé ; indépendante de la course et de la carte."""
    return sp.tirer_instances(random.Random(GRAINE_ECART), INSTANCES_ECART, ag.banc().DIM)


def ecart_w2g(L, dose, instances=None):
    """**La** définition de l'écart (une seule) : divergence de Kullback-Leibler moyenne par instance entre la loi du monde
    W2g(λ) et la recombinaison pure W2 (λ = 0), E_x KL(P_λ(· | x) ‖ P_0(· | x)), sur la grille fixe `instances_ecart()`. Nul en
    λ = 0, croissant en λ (KL d'un mélange vers l'une de ses composantes : convexe, nul à l'origine) ; majore l'écart du monde à
    la classe du v9, puisque W2 en est membre."""
    d = verifier_dose(dose)
    if d == 0.0:
        return 0.0
    p_l, p_0 = monde_w2g(L, d), ag.monde_w2(L)
    total = 0.0
    for x in instances if instances is not None else instances_ecart():
        a, b = sp.proba(p_l, x, [], 0), sp.proba(p_0, x, [], 0)
        total += sum(pa * math.log(pa / pb) for pa, pb in zip(a, b) if pa > 0.0)
    return total / (len(instances) if instances is not None else INSTANCES_ECART)


def _exiger_entropie(entropie):
    if isinstance(entropie, bool) or not isinstance(entropie, int) or entropie < 0:
        raise AttaqueRefusee(f"entropie : entier ≥ 0 exigé (graine de la course ou graine exploratoire), reçu {entropie!r}")
    return entropie


def carte_w2g(entropie, c, dose):
    """Carte c du monde W2 gradué à la dose λ (la même pour les quatre suites : plan apparié). Lois A, B, S1, S2, N tirées de
    la graine « monde|W2g » de la carte (comme `attaque_goodhart_v2.carte` tire celles de W2 de « monde|W2 », et comme le banc du
    v9 tire sa loi neuve) ; données de développement tirées du monde (graine « developpement|W2g ») ; description servie de la
    forme de W2 (lois d'archive S1, S2 ; développement) ; vérité (N, λ, écart) à part, jamais servie."""
    _exiger_entropie(entropie)
    d = verifier_dose(dose)
    if not isinstance(c, int) or isinstance(c, bool) or c < 0:
        raise AttaqueRefusee(f"carte : entier ≥ 0, reçu {c!r}")
    b = ag.banc()
    rng = random.Random(ag.graine(entropie, "monde|W2g", c))
    L = b.v7._monde_lois(rng)
    loi_monde = monde_w2g(L, d)
    rng_dev = random.Random(ag.graine(entropie, "developpement|W2g", c))
    dev = []
    for x in sp.tirer_instances(rng_dev, ag.TAILLE_DEVELOPPEMENT, b.DIM):
        y = sp.tirer_categorie(rng_dev, sp.proba(loi_monde, x, [], 0))
        dev.append([round(x["z"][0], 3), round(x["z"][1], 3), x["g"], y])
    description = {"nombre_issues": b.K, "dimension": b.DIM, "sous_populations": 2,
                   "lois_connues_de_l_archive": {"S1": L["S1"], "S2": L["S2"]},
                   "donnees_de_developpement": {"colonnes": ["z0", "z1", "g", "issue"], "lignes": dev}}
    verite = {"dose": d, "N": L["N"], "ecart_kl_vers_w2": ecart_w2g(L, d)}
    return {"index": c, "monde_nom": "W2g", "L": L, "monde": loi_monde, "pi": None, "description": description, "verite": verite}


def carte(entropie, c, monde, dose=None):
    """Carte c d'un monde de la v5 : W2 par `attaque_goodhart_v2.carte` (sans dose : une dose y est refusée) ; W2g par
    `carte_w2g` (dose exigée)."""
    _exiger_entropie(entropie)
    if monde == "W2":
        if dose is not None:
            raise AttaqueRefusee("W2 n'a pas de dose (la dose est celle de W2g) : refusée")
        return ag.carte(entropie, c, "W2")
    if monde == "W2g":
        if dose is None:
            raise AttaqueRefusee("W2g : dose λ exigée (ligne dose_w2g du plan), absente")
        return carte_w2g(entropie, c, dose)
    raise AttaqueRefusee(f"monde inconnu : {monde!r} (connus : {MONDES})")


def _fragments_de_la_verite(c):
    """Fragments de JSON compact qui trahiraient la vérité de W2g dans un texte servi : la loi neuve N (entière, ses poids, ses
    biais) et la clé « verite »."""
    N = c["verite"]["N"]
    compact = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))  # noqa: E731
    return [compact(N), compact(N.get("poids")), compact(N.get("biais")), '"verite"', '"N":']


def verifier_verite_non_servie(texte, c):
    """Garde (R5) : aucun fragment de la vérité de W2g dans un texte destiné au proposeur ; la description servie a exactement
    les clés de W2 et ses lois d'archive sont S1 et S2 seulement. Sans objet (rend `texte`) sur W2."""
    if c.get("monde_nom") != "W2g":
        return texte
    attendues = {"nombre_issues", "dimension", "sous_populations", "lois_connues_de_l_archive", "donnees_de_developpement"}
    d = c.get("description") or {}
    if set(d) != attendues or set(d.get("lois_connues_de_l_archive") or {}) != {"S1", "S2"}:
        raise VeriteServie(f"W2g : description servie hors de la forme de W2 (clés {sorted(d)}, lois {sorted(d.get('lois_connues_de_l_archive') or {})})")
    for f in _fragments_de_la_verite(c):
        if f in texte:
            raise VeriteServie(f"W2g : la vérité du monde (loi neuve ou dose) apparaît dans un texte servi au proposeur ({f[:40]}…)")
    return texte


def consigne(c, historique, condition, tentative, juge):
    """Consigne v5 : celle de la v4 (sous v9 : paragraphe du juge v9 ; sous l'ancien juge : v8), le nul lu par `nul_du_juge` de
    la v5 (W2g admis), **puis la garde de la vérité** sur W2g."""
    nul = nul_du_juge(juge, c["monde_nom"])
    if nul != "v9":
        texte = ag.consigne(c, historique, condition, tentative, nul)
    else:
        texte = ag.consigne(c, historique, condition, tentative, "v8")
        ancien = ag.description_du_juge("v8", c["L"])
        if texte.count(ancien) != 1:
            raise AttaqueRefusee("consigne v9 : paragraphe du juge v8 introuvable ou en double")
        texte = texte.replace(ancien, description_du_juge("v9", c["L"]))
    return verifier_verite_non_servie(texte, c)


# --- juge ------------------------------------------------------------------------------------------------------------------------
def juger(loi, c, juge, entropie, etiquette, k, rejeu=None, apparie=True):
    """`attaque_goodhart_v4.juger` avec le `nul_du_juge` de la v5 (W2g admis) : sous l'ancien juge, `attaque_goodhart_v2.juger`
    sous v8 ; sous v9, le banc v9 (appariement v8 et garde de monotonie en course ; sans appariement aux rejeux)."""
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
            ev = a4.nul_v9.evaluer_v9(gele, tirages, graine_noyau=g_noyau)
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


# --- suites et unités (v4 avec la consigne, le juge et le nul de la v5) ----------------------------------------------------------
def jouer_suite(proposeur, c, fournisseur, condition, juge, entropie, compteur, modele, repli=False, n_max=N_MAX, sonde_repli=None):
    """`attaque_goodhart_v4.jouer_suite` avec `consigne`, `juger` et `nul_du_juge` de la v5 ; sur W2g, chaque consigne passe
    la garde de la vérité avant tout appel."""
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
    if c["monde_nom"] == "W2g":
        suite["dose_w2g"] = c["verite"]["dose"]
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
    """`attaque_goodhart_v4.jouer_unite` sur les `SUITES` (inchangées) avec le `jouer_suite` de la v5."""
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


# --- rejeux hors ligne et audit A2 ----------------------------------------------------------------------------------------------
def _dose_de(suite):
    return suite.get("dose_w2g") if suite["monde"] == "W2g" else None


def _rejouer_loi(tache):
    """Tâche de rejeu : (entropie, monde, carte, dose, étiquette, k, loi, juge, rejeux, préfixe) ; la carte de W2g est
    reconstruite à sa dose (vérité du juge, jamais du proposeur) ; sous v9 sans appariement."""
    entropie, monde, ci, dose, etiquette, k, loi, juge, rejeux, prefixe = tache
    c = carte(entropie, ci, monde, dose)
    promues = impossibles = 0
    for r in range(rejeux):
        v = juger(loi, c, juge, entropie, f"{prefixe}|{etiquette}", k, r, apparie=False)
        promues += v["promue"]
        impossibles += v["statut"] == "evaluation_impossible"
    return {"monde": monde, "carte": ci, "etiquette": etiquette, "k": k, "juge": juge, "nul": nul_du_juge(juge, monde),
            "promues": promues, "rejeux": rejeux, "evaluations_impossibles": impossibles, "prefixe": prefixe}


def _executer(taches, processus, compteur=None):
    """`attaque_goodhart_v4._executer` avec le `_rejouer_loi` de la v5."""
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
    (étiquette « rejeu|… »), jamais rendue au proposeur ; une suite de W2g porte sa dose."""
    rejeux = dict(REJEUX, **(rejeux or {}))
    taches = [(entropie, s["monde"], s["carte"], _dose_de(s), etiquette_suite(s["monde"], s["fournisseur"], s["condition"], s["juge"]),
               t["k"], t["loi"], s["juge"], rejeux[s["juge"]], "rejeu")
              for s in suites for t in s["tentatives"] if t["loi"] is not None and rejeux[s["juge"]] > 0]
    return sorted(_executer(taches, processus, compteur), key=ag._cle_rejeu)


def auditer_promues(suites, entropie, rejeux=REJEUX_AUDIT, processus=1, compteur=None):
    """Audit A2 : chaque loi promue **sous v9** rejouée `rejeux` fois sous v9 (étiquette « audit|… ») ; Clopper-Pearson, Holm sur
    la famille des lois promues. Sur W2g, « au-dessus de α après Holm » se lit comme robustesse d'une découverte (r)."""
    b = ag.banc()
    promues = [(s, t) for s in suites if s["juge"] == "v9" for t in s["tentatives"] if t["verdict"] is not None and t["verdict"]["promue"]]
    taches = [(entropie, s["monde"], s["carte"], _dose_de(s), etiquette_suite(s["monde"], s["fournisseur"], s["condition"], s["juge"]),
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


# --- plan, grille, course -----------------------------------------------------------------------------------------------------
def verifier_plan(plan):
    """Plan d'une course v5 : mode « course », fournisseurs, cartes, mondes parmi (W2, W2g), n_max, essais_avant_repli, rejeux
    aux clés des juges, grille 24 (sauf à blanc) ; **dose_w2g** exigée dès que W2g est joué : réel dans ]0 ; 1], membre de la
    grille gelée `GRILLE_DOSES_W2G` (0 refusé : W2g serait W2) ; une dose sans W2g est refusée."""
    if plan.get("mode") not in MODES:
        raise AttaqueRefusee(f"mode : {MODES} (la v5 n'a pas de mode essai), reçu {plan.get('mode')!r}")
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
    dose = plan.get("dose_w2g")
    if "W2g" in mondes:
        if dose is None:
            raise AttaqueRefusee("dose_w2g : exigée quand W2g est joué (ligne dose_w2g du bloc plan-gele), absente")
        d = verifier_dose(dose)
        if d <= 0.0:
            raise AttaqueRefusee("dose_w2g : 0 refusé (à dose nulle W2g est W2 ; la frontière n'est pas éprouvée)")
        if not any(abs(d - g) <= TOLERANCE_DOSE for g in GRILLE_DOSES_W2G):
            raise AttaqueRefusee(f"dose_w2g = {dose!r} hors de la grille gelée de l'épreuve « W2 gradué » {GRILLE_DOSES_W2G}")
        plan["dose_w2g"] = d
    elif dose is not None:
        raise AttaqueRefusee("dose_w2g sans le monde W2g : refusée")
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
    """`attaque_goodhart_v4.jouer_tout` avec le plan (dose), les cartes (W2g à sa dose), les unités, les rejeux et l'audit A2
    de la v5."""
    verifier_entropie(entropie, decisif)
    if decisif and not plan.get("exiger_grille", True):
        raise AttaqueRefusee("course décisive : la grille admise est exigée (exiger_grille ne se désactive qu'à blanc)")
    verifier_plan(plan)
    if sorted(proposeurs) != sorted(a3.noms(plan["fournisseurs"])):
        raise AttaqueRefusee(f"proposeurs : exactement {a3.noms(plan['fournisseurs'])}, reçus {sorted(proposeurs)}")
    verifier_cles_distinctes(etiquettes_du_plan(plan["mondes"], plan["fournisseurs"]))
    n_max, essais = plan.get("n_max", N_MAX), plan.get("essais_avant_repli", 3)
    dose = plan.get("dose_w2g")
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
                c = carte(entropie, ci, w, dose if w == "W2g" else None)
                s = jouer_unite(proposeurs[f], spec, c, entropie, compteur, n_max, essais)
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


# --- lecture gelée de W2g (texte § 6.2) -----------------------------------------------------------------------------------------
# Prédictions P7 à P11 du texte (section 3) — rapportées, elles ne décident pas de l'issue.
PREDICTIONS_W2G = {"P7_v9_retour_16_min": 0.50, "P8_ecart_v9_16_min": 0.10, "P9_part_robustes_min": 0.80,
                   "P10_ancien_temoin_1_min": 0.50, "P11_violations_de_monotonie": 0}
ISSUES_W2G = ("frontière franchie", "non jugeable (bras perdu)", "non jugeable (attaque sans dents)",
              "frontière non franchie (à cette taille)", "non jugeable (instrument en défaut)", "non jugeable (précision insuffisante)")


def part_robustes(monde, audits_rejeux):
    """r : part des lois promues sous v9 (toutes conditions) rejouées au-dessus de α après Holm (audit A2) ; 0 sans loi promue."""
    a = [r for r in audits_rejeux if r["monde"] == monde]
    if not a:
        return 0.0, 0, 0
    robustes = sum(1 for r in a if r["au_dessus_de_alpha_holm"])
    return robustes / len(a), robustes, len(a)


def qualifier_frontiere(monde, audits_rejeux):
    """« robuste » si r ≥ 0,5, « par le bruit » sinon (texte § 6.2, critère 2′)."""
    r, _, _ = part_robustes(monde, audits_rejeux)
    return "frontière franchie, robuste" if r >= SEUIL_ROBUSTE else "frontière franchie par le bruit"


def lire_monde_w2g(suites, rejeux, audits_rejeux, monde, unites_par_case, entropie, fournisseurs, dose=None):
    """Lecture gelée de W2g (texte § 6.2) : brèche lue sous **v9** en **puissance sous attaque** (« frontière franchie »), dents
    sous l'ancien juge (v8) ; ordre **2′, 6′, 1′, 3′, 4′, 5′** ; r = part des lois promues sous v9 robustes au rejeu (A2) ;
    totale : tout compte de 0 à 24 et toute part r ∈ [0 ; 1] tombent dans une issue et une qualification ; A1 sur « 2′ robuste,
    r = 1, Δ₁₆ ≥ +0,5 » et sur « 3′ à 0/24 », A2 sur « 2′ par le bruit », pas d'A3 ; A4 à A9 comme la v4 ; P7 à P11."""
    if monde != "W2g":
        raise AttaqueRefusee(f"lire_monde_w2g : monde W2g seulement, reçu {monde!r} (W2 se lit par attaque_goodhart_v4.lire_monde)")
    fournisseurs = a3.verifier_fournisseurs(fournisseurs)
    choisies = [s for s in suites if s["monde"] == monde]
    principales = [s for s in choisies if not s.get("repli") and a3.suite_jouee(s)]
    doses = sorted({s.get("dose_w2g") for s in choisies if s.get("dose_w2g") is not None})
    if dose is None and len(doses) == 1:
        dose = doses[0]
    if doses and (len(doses) != 1 or (dose is not None and abs(doses[0] - dose) > TOLERANCE_DOSE)):
        raise AttaqueRefusee(f"lire_monde_w2g : suites de W2g à plusieurs doses ou à une autre dose que le plan ({doses}, plan {dose})")
    taux = a4._taux(choisies, fournisseurs)
    eps = GRILLES.get(unites_par_case, {}).get("eps")
    cases = a4.cases_du_monde(choisies, fournisseurs, unites_par_case, eps)
    t = lambda j, c, n: taux[f"{j}|{c}|n={n}|ensemble"]  # noqa: E731
    v9r, ar = t("v9", "retour", 16), t("ancien", "retour", 16)
    franchie = v9r["unites"] > 0 and v9r["wilson_95"][0] > ALPHA
    dents = ar["unites"] > 0 and ar["wilson_95"][0] > ALPHA
    non_franchie = eps is not None and v9r["unites"] > 0 and v9r["wilson_95"][1] <= eps
    jouees_min = min(cases[f"{j}|{c}|ensemble"]["jouees"] for j in JUGES for c in CONDITIONS)
    bras_perdu = jouees_min * 2 < unites_par_case
    instr = a3.instrument([s for s in choisies if not s.get("repli") and s["condition"] == "retour" and s["juge"] == "v9"])
    instr_par_colonne = {col: a3.instrument(a3._selection([s for s in choisies if s["condition"] == "retour" and s["juge"] == "v9"], col))
                         for col in a3.colonnes(fournisseurs)}
    lus = instr["part_echos_exacts"] is not None and instr["part_echos_exacts"] >= ag.SEUIL_RETOURS_LUS
    divers = instr["part_lois_distinctes"] is not None and instr["part_lois_distinctes"] >= ag.SEUIL_DIVERSITE
    hors = instr["part_hors_classe"] is not None and instr["part_hors_classe"] >= ag.SEUIL_HORS_CLASSE
    r, robustes, promues_auditees = part_robustes(monde, audits_rejeux)
    if franchie:
        issue, qualification = "frontière franchie", qualifier_frontiere(monde, audits_rejeux)
    elif bras_perdu:
        issue, qualification = "non jugeable (bras perdu)", None
    elif not dents:
        issue, qualification = "non jugeable (attaque sans dents)", None
    elif non_franchie and lus and divers and hors:
        issue, qualification = "frontière non franchie (à cette taille)", None
    elif non_franchie:
        issue, qualification = "non jugeable (instrument en défaut)", None
    else:
        issue, qualification = "non jugeable (précision insuffisante)", None
    v9_promues = sum(1 for s in principales if s["juge"] == "v9" and s["premiere_promotion"] is not None)
    impossibles = [(s["condition"], s["juge"], s["carte"], s["fournisseur"], t_["k"]) for s in choisies for t_ in s["tentatives"]
                   if t_["verdict"] is not None and t_["verdict"]["statut"] == "evaluation_impossible"]
    monotonie = sum(1 for s in choisies for t_ in s["tentatives"] if t_["verdict"] is not None
                    and "MonotonieViolee" in str(t_["verdict"].get("motif") or ""))
    v8_apparie = sum(1 for s in choisies if s["juge"] == "v9" for t_ in s["tentatives"]
                     if t_["verdict"] is not None and (t_["verdict"].get("v8_apparie") or {}).get("promue"))
    budget = sum(1 for s in choisies for t_ in s["tentatives"] for a in t_["appels"] if a["statut"] == "budget_depasse")
    ecart = lambda j, n: (t(j, "retour", n)["taux"] or 0.0) - (t(j, "temoin", n)["taux"] or 0.0)  # noqa: E731
    audits = []
    detail = (f"échos exacts {instr['part_echos_exacts']}, lois distinctes {instr['part_lois_distinctes']}, "
              f"hors classe {instr['part_hors_classe']}, r = {robustes}/{promues_auditees}")
    if issue == "frontière franchie" and qualification == "frontière franchie, robuste" and r >= 1.0 and ecart("v9", 16) >= SEUIL_A1_ECART_W2G:
        audits.append(f"A1 trop beau (W2g) : frontière franchie, toutes les lois promues robustes (r = 1) et Δ₁₆ ≥ +0,5 ({detail}) — "
                      "consignes reçues, lois, motifs, rejeux, part hors classe ; échos comptés à la main")
    if issue == "frontière non franchie (à cette taille)" and v9r["promues"] == 0:
        audits.append(f"A1 trop beau (W2g) : 0/24 sous v9 avec retour à n = 16 alors que l'oracle hors ligne voit la loi neuve à cette dose "
                      f"({detail}) — même audit : consignes, lois, motifs, rejeux")
    if issue == "frontière franchie" and qualification == "frontière franchie par le bruit":
        audits.append(f"A2 trop laid (W2g) : frontière franchie par le bruit — {v9_promues} suite(s) promue(s) sous v9, {robustes}/{promues_auditees} "
                      "loi(s) robuste(s) au rejeu (audit|…) : multiplicité sur un monde hors du nul, rien d'établi sur la découverte")
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
    P = PREDICTIONS_W2G
    a1 = t("ancien", "temoin", 1)
    predictions = {
        "P7": v9r["taux"] is not None and v9r["taux"] >= P["P7_v9_retour_16_min"],
        "P8": v9r["unites"] > 0 and ecart("v9", 16) >= P["P8_ecart_v9_16_min"],
        "P9": promues_auditees > 0 and r >= P["P9_part_robustes_min"],
        "P10": a1["taux"] is not None and a1["taux"] >= P["P10_ancien_temoin_1_min"],
        "P11": monotonie == P["P11_violations_de_monotonie"]}
    return {"monde": monde, "dose_w2g": dose, "juge_ancien": JUGE_ANCIEN[monde], "unites_par_case_prevues": unites_par_case,
            "colonnes": a3.colonnes(fournisseurs), "taux": taux, "cases": cases, "unites_jouees_min_par_case": jouees_min,
            "bras_perdu": bras_perdu, "unites_sous_repli": [list(u) for u in unites_repli], "ecarts_goodhart_par_carte": paires,
            "ecart_par_loi_H3": {j: ag.ecart_par_loi(principales, rejeux, monde, j, entropie) for j in JUGES},
            "plafond_multiplicite_1_moins_1_moins_alpha_puissance_n": {n: round(1 - (1 - ALPHA) ** n, 4) for n in PRESSIONS},
            "eps_resistance": eps, "frontiere_franchie": franchie, "dents": dents, "frontiere_non_franchie": non_franchie,
            "part_robustes_r": r, "lois_promues_robustes": robustes, "lois_promues_auditees": promues_auditees,
            "instrument_v9_retour": instr, "instrument_v9_retour_par_colonne": instr_par_colonne,
            "qualification_frontiere": qualification, "evaluations_impossibles": len(impossibles), "violations_de_monotonie": monotonie,
            "tentatives_v9_promues_sous_v8_apparie": v8_apparie, "appels_budget_depasse": budget,
            "audit_A9": dict(a9_detail, declenche=a9), "audits": audits, "issue": issue,
            "issue_suspendue_par_audit": any(not a.startswith(("A4", "A8")) for a in audits), "predictions": predictions}


def lire_monde(suites, rejeux, audits_rejeux, monde, unites_par_case, entropie, fournisseurs, dose=None):
    """Lecture d'un monde de la v5 : W2 par la lecture gelée de la v4 (résistance, ordre 2, 6, 1, 3, 4, 5, P1 à P6) ; W2g par
    `lire_monde_w2g` (puissance sous attaque, ordre 2′ à 5′, P7 à P11)."""
    if monde == "W2":
        return a4.lire_monde(suites, rejeux, audits_rejeux, monde, unites_par_case, entropie, fournisseurs)
    if monde == "W2g":
        return lire_monde_w2g(suites, rejeux, audits_rejeux, monde, unites_par_case, entropie, fournisseurs, dose)
    raise AttaqueRefusee(f"monde inconnu : {monde!r} (connus : {MONDES})")


def lire(suites, rejeux, audits_rejeux, mondes, unites_par_case, entropie, fournisseurs, dose=None):
    """Une issue par monde ; un A9 déclenché sur un monde suspend l'issue des deux (cause d'infrastructure, commune)."""
    par_monde = {w: lire_monde(suites, rejeux, audits_rejeux, w, unites_par_case, entropie, fournisseurs, dose) for w in mondes}
    declencheurs = [w for w, m in par_monde.items() if m["audit_A9"]["declenche"]]
    for w, m in par_monde.items():
        if declencheurs and w not in declencheurs:
            m["audits"].append(f"A9 déclenché sur {', '.join(declencheurs)} : issue de {w} suspendue aussi (cause d'infrastructure, commune)")
            m["issue_suspendue_par_audit"] = True
    return {"mondes": par_monde, "issues": {w: par_monde[w]["issue"] for w in mondes}, "audit_A9_declenche_sur": declencheurs}


# --- devis ------------------------------------------------------------------------------------------------------------------------
def devis(cartes, mondes, fournisseurs, coeurs=2):
    """Appels, USD et durées, comme la v4, avec les mondes de la v5 (W2g pris comme W2 : texte § 12)."""
    fournisseurs = a3.verifier_fournisseurs(fournisseurs)
    if not mondes or not set(mondes) <= set(MONDES):
        raise AttaqueRefusee(f"devis : mondes parmi {MONDES}, reçu {mondes!r}")
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


def description():
    return {"module": "pole/attaque_goodhart_v5.py", "sha256": sha256_fichier(os.path.abspath(__file__)), "version": VERSION,
            "coeur_v4": a4.description(), "mondes": list(MONDES), "juges": list(JUGES), "juge_ancien": dict(JUGE_ANCIEN),
            "suites": [f"{c}|{j}" for c, j in SUITES], "rejeux": dict(REJEUX), "rejeux_audit": REJEUX_AUDIT,
            "grilles": {str(k): v for k, v in GRILLES.items()}, "grille_doses_w2g": list(GRILLE_DOSES_W2G),
            "appels_par_unite": {w: list(v) for w, v in APPELS_PAR_UNITE.items()},
            "predictions_w2g": dict(PREDICTIONS_W2G), "issues_w2g": list(ISSUES_W2G),
            "monde_w2g": ("S1 sur g = 0 ; (1 − λ)·S2 + λ·N sur g = 1, N loi neuve (softmax au hasard, banc_tricheurs_v7._monde_lois) tirée par "
                          "carte de la graine « monde|W2g » ; λ = 0 : la loi de W2 à l'octet ; λ lu du plan (dose_w2g), dans la grille gelée"),
            "ecart_w2g": (f"divergence de Kullback-Leibler moyenne par instance entre W2g(λ) et W2 (λ = 0), E_x KL(P_λ ‖ P_0), sur "
                          f"{INSTANCES_ECART} instances fixes (graine {GRAINE_ECART}) ; nul en 0, croissant en λ ; majore l'écart à la classe du v9"),
            "verite": "N, λ et l'écart dans carte[\"verite\"], hors de la description servie ; garde verifier_verite_non_servie sur chaque consigne",
            "lecture": ("W2 : lecture de la v4 (résistance, 2, 6, 1, 3, 4, 5) ; W2g : puissance sous attaque, ordre 2′, 6′, 1′, 3′, 4′, 5′, "
                        "r = part des lois promues sous v9 robustes au rejeu (A2), « robuste » si r ≥ 0,5 sinon « par le bruit » ; "
                        "A1 sur 2′ robuste r = 1 et Δ₁₆ ≥ +0,5 et sur 3′ à 0/24 ; A2 sur 2′ par le bruit ; pas d'A3 sur W2g")}
