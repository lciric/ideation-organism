"""Lecture gelée de la plus petite course réelle de la boucle complète, version 66 (fichier neuf, R12 ; la lecture v65 reste
intacte). Applique au relevé du cœur `pole/boucle_reelle_v66.py` les critères gelés C1 à C6 et les audits A1 à A4 du brouillon
(`preenregistrement-boucle-reelle-organisme-v1-brouillon1.md`, sections 8 et 9), dans l'ordre du texte : C5, C4, C2, C3, C6, C1.

Corrections de la contre-lecture du code v65 (`contre-lecture-code-v65-v2.md`, `c4ddfc7f…`), côté lecture :

CLV65-01 **Complétude exigée avant toute issue autre que C5** (`completude`) : deux générations jouées, un étage par génération,
    membres attendus des deux générations (> 0) ; V1 à V4, T-ELIM et T-MAL une fois chacune en génération 1 ; F1 à F4 une fois
    chacune dans chaque génération ; autant de copies que le plus petit de quatre et du nombre de retenues de la génération 1,
    chacune d'une retenue ; **chaque fausse et chaque copie passée au gardien et jugée** (membres d'archive = membres attendus de
    sa génération, log W maximal présent) ; toute loi plantée passée au gardien jugée de même ; vue servie consignée pour les deux
    générations ; sélection finale relue. Sinon **C5 « relevé incomplet »**, manques écrits. L'audit A1 ne lit plus un log W
    absent comme « ≤ 0 » (il est faux).
CLV65-02 (b) **Héritage refusé lu comme un écart** : `lecture_selection.refus` (empreinte attendue, empreinte sur disque, motif)
    est un écart de P6 ; sous C5, « C4 (partielle) ». Les incidents de garde 7, 21 et 23 consignés par le cœur aussi.
CLV65-03 **Vue réellement servie** : P6 compare les identifiants servis aux proposeurs de la génération 2
    (`vues_servies["2"]`, consignés au moment du service) à {K1} ∪ retenues de la génération 1 **recalculé ici** depuis le
    relevé ; la génération 1 doit avoir servi {K1} seule ; l'archive de jugement de la génération 2 doit être {K1} ∪ retenues.
CLV65-08 Mesures sans issue ajoutées : intervalles de Wilson à 95 % des parts par fournisseur (P7) ; jetons (sommes par
    relais, jamais de moyenne ni de médiane) ; recherche de la loi plantée chez les proposeurs, l'expérimentateur et le
    vérificateur ; lignes de tranche dans les contextes servis. CLV65-11 : la phrase dit le mode, l'absence d'oracle et la
    présence d'une fausse découverte réelle.

L'oracle du monde planté n'est lu qu'ici, après la course (dans l'esprit de N-050).
"""

import math

VERSION = "lecture-boucle-reelle-v66"
VERSION_DU_COEUR = "boucle-reelle-v66"
VRAIES = ("V1", "V2", "V3", "V4")
FAUSSES = ("F1", "F2", "F3", "F4")
INSTRUMENTS = ("T-ELIM", "T-MAL")
ARCHIVE_DE_DEPART = ("K1",)
COPIES_MAX = 4
N_REJEU_A2 = 200  # « rejouer la loi promue 200 fois sur des tirages neufs » (brouillon, section 9)
MARGE_LOG_W = 1e-6  # « log W maximaux ≤ 0 aux marges près » (audit A1)
Z_WILSON_95 = 1.959963984540054
ISSUES = {"C5": "non jugeable (arrêt)", "C4": "boucle non fermée", "C2": "brèche dans la classe couverte", "C3": "sans dents",
          "C6": "instrument en défaut", "C1": "la chaîne garde (classe couverte, ce monde, cette taille)"}


class ReleveInvalide(ValueError):
    """Relevé d'une autre version ou mal formé : aucune issue lue."""


def _plantees(releve, generation=None, noms=None, copies=None):
    out = []
    for p in releve.get("plantees") or []:
        if generation is not None and p.get("generation") != generation:
            continue
        if noms is not None and p.get("nom") not in noms:
            continue
        if copies is not None and (p.get("source") is not None) != copies:
            continue
        out.append(p)
    return out


def exiger_forme(releve):
    if not isinstance(releve, dict) or releve.get("version") != VERSION_DU_COEUR:
        raise ReleveInvalide(f"relevé d'une autre version ({(releve or {}).get('version') if isinstance(releve, dict) else releve!r}) : "
                             f"la lecture v66 ne lit que les relevés du cœur {VERSION_DU_COEUR}")
    for k in ("cartes", "plantees", "generations_jouees", "membres_attendus", "retenues", "etages", "vues_servies",
              "archives_de_jugement", "incidents"):
        if k not in releve:
            raise ReleveInvalide(f"relevé sans champ « {k} »")
    for p in releve["plantees"]:
        for k in ("generation", "nom", "promue", "gardien", "membres_d_archive", "membres_attendus", "verdict", "log_richesse_max"):
            if k not in p:
                raise ReleveInvalide(f"loi plantée sans champ « {k} »")
    return releve


def _jugee(p, attendus):
    """Une loi plantée passée au gardien et jugée avec les membres d'archive de sa génération (log W maximal présent)."""
    return (p.get("gardien") == "passe" and isinstance(attendus, int) and attendus > 0 and p.get("membres_d_archive") == attendus
            and p.get("log_richesse_max") is not None)


def completude(releve):
    """CLV65-01 : la liste des manques qui empêchent toute issue autre que C5 (vide si le relevé est complet)."""
    manques = []
    if releve.get("generations_jouees") != [1, 2]:
        manques.append(f"générations jouées {releve.get('generations_jouees')!r} ≠ [1, 2]")
    etages = sorted(e.get("generation") for e in releve.get("etages") or [] if isinstance(e, dict))
    if etages != [1, 2]:
        manques.append(f"étages consignés pour les générations {etages} ≠ [1, 2]")
    attendus = {g: (releve.get("membres_attendus") or {}).get(str(g)) for g in (1, 2)}
    for g, a in attendus.items():
        if not isinstance(a, int) or isinstance(a, bool) or a <= 0:
            manques.append(f"membres d'archive attendus de la génération {g} absents ou nuls ({a!r})")
    for g, noms in ((1, VRAIES + FAUSSES + INSTRUMENTS), (2, FAUSSES)):
        for n in noms:
            k = len(_plantees(releve, g, (n,), copies=False))
            if k != 1:
                manques.append(f"loi plantée {n} présente {k} fois en génération {g} (une fois exigée)")
    en_trop = [p.get("nom") for p in _plantees(releve, 2, copies=False) if p.get("nom") not in FAUSSES]
    if en_trop:
        manques.append(f"lois plantées en trop en génération 2 : {en_trop}")
    retenues_g1 = list((releve.get("retenues") or {}).get("1") or [])
    copies = _plantees(releve, 2, copies=True)
    if len(copies) != min(COPIES_MAX, len(retenues_g1)):
        manques.append(f"{len(copies)} copie(s) en génération 2 ; {min(COPIES_MAX, len(retenues_g1))} attendue(s) "
                       f"(le plus petit de {COPIES_MAX} et des {len(retenues_g1)} retenues de la génération 1)")
    for c in copies:
        if c.get("source") not in retenues_g1:
            manques.append(f"copie {c.get('nom')} d'une carte que la génération 1 n'a pas retenue ({c.get('source')})")
    for p in _plantees(releve, noms=FAUSSES, copies=False) + copies:
        if not _jugee(p, attendus.get(p.get("generation"))):
            manques.append(f"{p.get('nom')} (génération {p.get('generation')}) non jugée avec l'archive de sa génération "
                           f"(gardien {p.get('gardien')!r}, membres {p.get('membres_d_archive')!r} contre {attendus.get(p.get('generation'))!r}, "
                           f"log W max {p.get('log_richesse_max')!r})")
    for p in _plantees(releve, noms=VRAIES + INSTRUMENTS):
        if p.get("gardien") == "passe" and not _jugee(p, attendus.get(p.get("generation"))):
            manques.append(f"{p.get('nom')} passée au gardien mais non jugée avec l'archive de sa génération")
    for g in ("1", "2"):
        if not isinstance((releve.get("vues_servies") or {}).get(g), dict):
            manques.append(f"vue servie aux proposeurs de la génération {g} non consignée")
    fin = releve.get("selection_finale")
    if not isinstance(fin, dict) or fin.get("refus") is not None or fin.get("retenues") is None:
        manques.append("sélection de la génération 2 non relue")
    return manques


def p6_ecarts(releve):
    """P6 et A4 : écarts de la lecture de la sélection et de la vue servie (liste vide si P6 tient) ; None si la génération 2
    n'a pas commencé (rien à lire)."""
    ls = releve.get("lecture_selection")
    incidents = [i for i in releve.get("incidents") or [] if i.get("garde") in (7, 21, 23)]
    vues = releve.get("vues_servies") or {}
    if ls is None and not incidents and "2" not in vues:
        v1 = vues.get("1")
        if isinstance(v1, dict) and v1.get("identifiants") != list(ARCHIVE_DE_DEPART):
            return [f"vue servie en génération 1 {v1.get('identifiants')} ≠ {{K1}}"]
        return None
    ecarts = []
    for i in incidents:
        ecarts.append(f"garde {i.get('garde')} (génération {i.get('generation')}) : {i.get('type')} : {str(i.get('motif'))[:200]}")
    v1 = vues.get("1")
    if isinstance(v1, dict) and v1.get("identifiants") != list(ARCHIVE_DE_DEPART):
        ecarts.append(f"vue servie en génération 1 {v1.get('identifiants')} ≠ {{K1}}")
    lu_a_part = ls is not None
    ls = ls or {}
    if ls.get("refus"):
        ecarts.append(f"héritage de la génération 1 refusé ({ls['refus'].get('type')}) : empreinte lue sur disque "
                      f"{str(ls.get('lu'))[:12]}… contre écrite {str(ls.get('attendu'))[:12]}… ; {str(ls['refus'].get('motif'))[:200]}")
    if lu_a_part and (not ls.get("attendu") or ls.get("attendu") != ls.get("lu")):
        ecarts.append(f"empreinte lue {str(ls.get('lu'))[:12]}… ≠ écrite {str(ls.get('attendu'))[:12]}…")
    retenues_g1 = sorted((releve.get("retenues") or {}).get("1") or ls.get("retenues_ecrites_g1") or [])
    attendue = sorted(set(ARCHIVE_DE_DEPART) | set(retenues_g1))
    if lu_a_part and not ls.get("refus"):
        if sorted(ls.get("vue") or []) != attendue:
            ecarts.append(f"vue lue {sorted(ls.get('vue') or [])} ≠ {{K1}} ∪ retenues {attendue}")
        if sorted(ls.get("retenues_lues") or []) != retenues_g1:
            ecarts.append("retenues lues ≠ retenues écrites par la génération 1")
    v2 = vues.get("2")
    if isinstance(v2, dict) and sorted(v2.get("identifiants") or []) != attendue:
        ecarts.append(f"vue servie aux proposeurs de la génération 2 {sorted(v2.get('identifiants') or [])} ≠ {{K1}} ∪ retenues {attendue}")
    plantes = {p.get("identifiant") for p in releve.get("plantees") or []} | {p.get("identifiant_servi") for p in releve.get("plantees") or []}
    for g, v in sorted(vues.items()):
        if isinstance(v, dict) and set(v.get("identifiants") or []) & plantes:
            ecarts.append(f"loi plantée servie aux proposeurs en génération {g}")
    a2 = (releve.get("archives_de_jugement") or {}).get("2")
    if a2 is not None and sorted(a2) != attendue:
        ecarts.append(f"archive de jugement de la génération 2 {sorted(a2)} ≠ {{K1}} ∪ retenues {attendue}")
    for c in ls.get("copies") or []:
        if c.get("source") not in retenues_g1:
            ecarts.append(f"copie {c.get('nom')} d'une carte non retenue ({c.get('source')})")
    fin = releve.get("selection_finale")
    if isinstance(fin, dict) and fin.get("refus"):
        ecarts.append(f"relecture de la sélection de la génération 2 refusée ({fin['refus'].get('type')})")
    attendus = (releve.get("membres_attendus") or {}).get("2")
    if attendus is not None:
        for c in releve.get("cartes") or []:
            if c.get("generation") == 2 and c.get("gardien") == "passe" and c.get("membres_d_archive") != attendus:
                ecarts.append(f"carte {c.get('identifiant')} de la génération 2 jugée avec {c.get('membres_d_archive')} membres "
                              f"d'archive (attendus {attendus})")
        for p in _plantees(releve, 2):
            if p.get("gardien") == "passe" and p.get("membres_d_archive") != attendus:
                ecarts.append(f"loi plantée {p['nom']} de la génération 2 jugée avec {p.get('membres_d_archive')} membres (attendus {attendus})")
    return ecarts


def lire_criteres(releve):
    """Issue (C1 à C6) et constats, dans l'ordre gelé du texte ; lève `ReleveInvalide` si le relevé n'est pas du cœur v66."""
    exiger_forme(releve)
    manques = completude(releve)
    partiel = bool(releve.get("arret")) or not releve.get("complet") or bool(manques)
    fausses_promues = [f"{p['nom']} (génération {p['generation']})" for p in _plantees(releve, noms=FAUSSES, copies=False) if p["promue"]]
    copies_promues = [f"{p['nom']} ← {p.get('source')}" for p in _plantees(releve, 2, copies=True) if p["promue"]]
    ecarts = p6_ecarts(releve)
    p6_tenue = ecarts == []
    vraies_g1 = {p["nom"]: p for p in _plantees(releve, 1, noms=VRAIES)}
    vraies_survivantes = sorted(n for n, p in vraies_g1.items() if p["promue"] and p.get("verdict") == "survit")
    t_elim = next(iter(_plantees(releve, 1, noms=("T-ELIM",))), None)
    t_mal = next(iter(_plantees(releve, 1, noms=("T-MAL",))), None)
    p4 = bool(t_elim and t_elim["promue"] and t_elim.get("verdict") == "éliminée" and t_mal and t_mal["gardien"] == "refuse"
              and not t_mal["promue"])
    p1 = bool(vraies_survivantes) and not fausses_promues and not copies_promues
    cause = None
    if partiel:
        cause = (f"arrêt : {releve.get('arret')}" if releve.get("arret") else "relevé incomplet") + \
                (" ; manques : " + " ; ".join(manques) if manques else "")
    constats = {"partiel": partiel, "arret": releve.get("arret"), "cause_c5": cause, "manques": manques,
                "fausses_promues": fausses_promues, "copies_promues": copies_promues, "ecarts_p6": ecarts, "p6_tenue": p6_tenue,
                "vraies_promues_survivantes_g1": vraies_survivantes, "p1": p1, "p4": p4,
                "t_elim": None if t_elim is None else {"promue": t_elim["promue"], "verdict": t_elim.get("verdict")},
                "t_mal": None if t_mal is None else {"gardien": t_mal["gardien"], "promue": t_mal["promue"]},
                "p2_v1_v2": all(n in vraies_survivantes for n in ("V1", "V2")),
                "p3_mesure": {n: {"promue": p["promue"], "verdict": p.get("verdict")} for n, p in sorted(vraies_g1.items()) if n in ("V3", "V4")},
                "p5_copies_refusees": None if not _plantees(releve, 2, copies=True) else not copies_promues}
    aussi = []
    if partiel:
        code = "C5"
        if ecarts or copies_promues:
            aussi.append("C4 (partielle)")
        if fausses_promues:
            aussi.append("C2 (partielle)")
    elif ecarts or copies_promues:
        code = "C4"
    elif fausses_promues:
        code = "C2"
    elif not vraies_survivantes:
        code = "C3"
    elif not p4:
        code = "C6"
    elif p1 and p4 and p6_tenue:
        code = "C1"
    else:  # aucun chemin du texte n'y mène : défaut de la lecture, jamais une issue
        raise ReleveInvalide(f"aucune ligne des critères ne s'applique (p1={p1}, p4={p4}, p6={p6_tenue}) : relevé incohérent")
    return {"code": code, "issue": ISSUES[code], "aussi": aussi, "constats": constats}


def audits(releve, lecture):
    """Audits A1 à A4 (section 9), écrits avant toute phrase de résultat ; chacun déclenché selon l'issue ou le constat."""
    c = lecture["constats"]
    out = {"A1": None, "A2": None, "A3": None, "A4": None}
    if lecture["code"] == "C1":  # « trop beau », d'office
        attendus = releve.get("membres_attendus") or {}
        vs = [p for p in _plantees(releve, 1, noms=VRAIES) if p["promue"] and p.get("verdict") == "survit"]
        etages = releve.get("etages") or []
        fausses = _plantees(releve, noms=FAUSSES)
        testees = [x for x in (releve.get("plantees") or []) + (releve.get("cartes") or []) if x.get("verdict") is not None]
        plantes = {p.get("identifiant") for p in releve.get("plantees") or []} | {p.get("identifiant_servi") for p in releve.get("plantees") or []}
        v2 = (releve.get("vues_servies") or {}).get("2") or {}
        out["A1"] = {"declenche": "d'office (issue C1)",
                     "vraies_survivantes_membres_justes": bool(vs) and all(p.get("membres_d_archive") == attendus.get(str(p["generation"])) for p in vs),
                     "bac_reel_partout": len(etages) == 2 and all(e.get("factice") is False for e in etages),
                     "contre_calcul_egal": bool(testees) and all(x.get("contre_calcul_ok") is True for x in testees),
                     "fausses_log_w_max_au_plus_0": len(fausses) == 2 * len(FAUSSES) and all(
                         p.get("log_richesse_max") is not None and p["log_richesse_max"] <= MARGE_LOG_W for p in fausses),
                     "plus_grand_log_w_max_des_fausses": max((p["log_richesse_max"] for p in fausses if p.get("log_richesse_max") is not None),
                                                             default=None),
                     "vue_g2_sans_loi_plantee": bool(v2.get("identifiants")) and not (set(v2.get("identifiants") or []) & plantes),
                     "a_verifier_sur_fichiers_bruts": ["fichier témoin et journal de bwrap de chaque gains.csv",
                                                       "registre du relais apparié appel par appel (expérimentateur appelé)"]}
    fp = [p for p in _plantees(releve, noms=FAUSSES, copies=False) if p["promue"]]
    if fp:
        out["A2"] = {"declenche": "fausse promue", "lois": [
            {"nom": p["nom"], "generation": p["generation"], "membres_d_archive": p.get("membres_d_archive"),
             "membres_attendus": p.get("membres_attendus"), "membre_dominant_final": p.get("membre_dominant_final"),
             "empreinte_engagement": p.get("empreinte_engagement"),
             "diagnostic": "jugée sans archive : défaut de chaîne" if not p.get("membres_d_archive")
             else ("membres d'archive en écart : défaut de chaîne" if p.get("membres_d_archive") != p.get("membres_attendus")
                   else "membre du nul promu : défaut numérique"),
             "a_rejouer": "200 fois sur des tirages neufs (rejouer_a2)"} for p in fp]}
    if lecture["code"] == "C3":
        out["A3"] = {"declenche": "sans dents", "vraies": {
            p["nom"]: ("non promue" if not p["promue"] else ("non concluante" if p.get("verdict") == "non concluant"
                       else ("promue non survivante" if p.get("verdict") != "survit" else "survivante")))
            for p in _plantees(releve, 1, noms=VRAIES)},
            "a_relire": "traces de l'expérimentateur (tours, fin des tours, « rien envoyé ») ; jugement rejoué hors ligne à la même graine"}
    if c["copies_promues"] or c["ecarts_p6"]:
        ls = releve.get("lecture_selection") or {}
        attendus = (releve.get("membres_attendus") or {}).get("2")
        retenues_g1 = (releve.get("retenues") or {}).get("1") or ls.get("retenues_ecrites_g1") or []
        out["A4"] = {"declenche": "copie promue ou lecture de sélection en écart", "copies": [
            {"nom": p["nom"], "source": p.get("source"), "promue": p["promue"], "membres_d_archive": p.get("membres_d_archive"),
             "membres_imposes_par_la_selection_lue": attendus, "source_retenue": p.get("source") in retenues_g1}
            for p in _plantees(releve, 2, copies=True)], "ecarts_p6": c["ecarts_p6"]}
    return out


def wilson(k, n, z=Z_WILSON_95):
    """Intervalle de Wilson (95 % par défaut) de la part k/n ; None si n = 0."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, centre - demi), 6), round(min(1.0, centre + demi), 6)]


PARTS_WILSON = (("refusees_au_gardien", "proposees"), ("promues", "proposees"), ("survivantes", "testees"),
                ("retenues", "proposees"), ("vraies_decouvertes", "promues"), ("fausses_decouvertes", "promues"))


def mesures_oracle(releve, monde, oracle=None):
    """P7 (mesure sans issue) : par carte réelle promue, classe de l'oracle v60 contre l'archive de jugement de sa génération ;
    par fournisseur, comptes et intervalles de Wilson à 95 % des parts ; fausses découvertes réelles rendues en tête."""
    from .oracle_tour_ferme_v60 import Oracle, classer
    o = oracle or Oracle(monde["loi"], int(releve["racine"]), 2)
    par_f, fd = {}, []
    for c in releve.get("cartes") or []:
        f = par_f.setdefault(c.get("proposeur") or "?", {"proposees": 0, "refusees_au_gardien": 0, "promues": 0, "testees": 0,
                                                         "survivantes": 0, "retenues": 0, "vraies_decouvertes": 0,
                                                         "fausses_decouvertes": 0, "fausses_promotions_du_juge": 0})
        f["proposees"] += 1
        if c.get("gardien") != "passe":
            f["refusees_au_gardien"] += 1
            continue
        f["promues"] += bool(c.get("promue"))
        f["testees"] += c.get("verdict") is not None
        f["survivantes"] += c.get("verdict") == "survit"
        f["retenues"] += bool(c.get("retenue"))
        if not c.get("promue"):
            continue
        archive = (releve.get("archives_de_jugement") or {}).get(str(c["generation"])) or {}
        g = o.gain(c["loi"])
        k = classer(promue=True, survit=c.get("verdict") == "survit", gain_nat=g, delta_gain_nat=g - o.gain_archive(archive),
                    divergence_nat=o.divergence(c["loi"]), bras="reel")
        f["vraies_decouvertes"] += k["vraie_decouverte"]
        f["fausses_decouvertes"] += k["fausse_decouverte"]
        f["fausses_promotions_du_juge"] += k["fausse_promotion_du_juge"]
        if k["fausse_decouverte"]:
            fd.append({"identifiant": c.get("identifiant"), "generation": c["generation"], "proposeur": c.get("proposeur"),
                       "forme": forme_de_la_loi(c["loi"]), "audit": "A2 sur sa forme"})
    for f in par_f.values():
        f["wilson_95"] = {f"{a}/{b}": wilson(f[a], f[b]) for a, b in PARTS_WILSON}
    return {"par_fournisseur": par_f, "fausses_decouvertes_reelles": fd}


def forme_de_la_loi(loi):
    """Forme d'une loi pour l'audit A2 : « par morceaux », « composition d'étapes », « déformation d'une loi », « mélange »,
    « softmax », « fixe », « autre »."""
    t = (loi or {}).get("type")
    if t in ("si_sinon", "par_sous_population"):
        return "par morceaux"
    if t == "transformee":
        return "composition d'étapes" if len(set(loi) - {"type", "base"}) > 1 or "oscillation" in loi else "déformation d'une loi"
    if t in ("melange", "softmax", "fixe"):
        return {"melange": "mélange", "softmax": "softmax", "fixe": "fixe"}[t]
    return "autre"


def rejouer_a2(loi, monde, archive, racine, n=200):
    """Audit A2 : rejoue `loi` `n` fois sous le nul v8 avec `archive`, sur des tâches neuves ; rend {promues, n, membres}."""
    from . import a_blanc_v59 as A
    promues, membres = 0, set()
    for r in range(n):
        ev, d = A.juger_carte(loi, monde, archive, racine, f"{VERSION}|audit-a2|rejeu={r}")
        promues += bool(ev["promue"])
        membres.add(d["membres_d_archive"])
    return {"promues": promues, "n": n, "membres_d_archive": sorted(membres)}


def mesures_sans_issue(releve):
    """Coût, jetons (sommes par relais), recherche de la loi plantée, lignes de tranche dans les contextes servis : rapportés
    tels que le cœur les a relevés ; aucune issue n'en dépend."""
    return {"depense": releve.get("depense"), "jetons": releve.get("jetons"),
            "recherche_loi_plantee": releve.get("recherche_loi_plantee"),
            "lignes_de_tranche_dans_les_contextes": releve.get("lignes_de_tranche_dans_les_contextes")}


def lire_boucle(releve, monde=None, mode=None):
    """La lecture entière : critères, puis audits (écrits avant la phrase de résultat), puis mesures ; l'oracle n'est lu que
    si `monde` est donné (sinon dit). `mode` : celui du rapport de course (« a-blanc … » ou « reel … »), écrit dans la phrase."""
    lecture = lire_criteres(releve)
    sortie = {"version": VERSION, "audits": audits(releve, lecture), "issue": lecture["issue"], "code": lecture["code"],
              "aussi": lecture["aussi"], "constats": lecture["constats"], "mesures_sans_issue": mesures_sans_issue(releve)}
    if monde is not None and releve.get("cartes"):
        sortie["oracle"] = mesures_oracle(releve, monde)
    elif monde is None:
        sortie["oracle"] = "non lu (--sans-oracle) : P7 par fournisseur et fausses découvertes des cartes réelles absentes de cette lecture"
    if monde is not None and sortie["audits"]["A2"]:  # A2 : chaque fausse promue rejouée 200 fois avec l'archive de sa génération
        for x in sortie["audits"]["A2"]["lois"]:
            p = next(q for q in releve["plantees"] if q["nom"] == x["nom"] and q["generation"] == x["generation"] and q["promue"])
            archive = (releve.get("archives_de_jugement") or {}).get(str(x["generation"])) or {}
            x["rejeu"] = rejouer_a2(p["loi"], monde, archive, int(releve["racine"]), n=N_REJEU_A2)
    fd = (sortie.get("oracle") or {}).get("fausses_decouvertes_reelles") if isinstance(sortie.get("oracle"), dict) else None
    tete = (f"EN TÊTE : {len(fd)} fausse(s) découverte(s) d'une carte réelle (audit A2 sur sa forme). " if fd else "")
    mode_dit = "mode non dit" if not mode else (f"course à blanc ({mode})" if str(mode).startswith("a-blanc") else f"course {mode}")
    factice = any(e.get("factice") for e in releve.get("etages") or [])
    sortie["phrase"] = (tete + f"Issue {lecture['code']} : « {lecture['issue']} »"
                        + (f" ; aussi : {', '.join(lecture['aussi'])}" if lecture["aussi"] else "")
                        + f" — {mode_dit}" + (", exécuteur factice (rien sur le vrai bac à sable)" if factice else "")
                        + ("" if monde is not None else ", oracle non lu")
                        + " (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte).")
    return sortie


__all__ = ("VERSION", "ISSUES", "ReleveInvalide", "completude", "p6_ecarts", "lire_criteres", "audits", "wilson",
           "mesures_oracle", "rejouer_a2", "mesures_sans_issue", "lire_boucle", "forme_de_la_loi")
