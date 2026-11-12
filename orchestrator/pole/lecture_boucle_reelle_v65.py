"""Lecture gelée de la plus petite course réelle de la boucle complète, version 65 (fichier neuf, R12 ; pièce M5).

Applique au relevé scellé de `pole/boucle_reelle_v65.py` les critères gelés C1 à C6 et les audits A1 à A4 du brouillon 1
(`preenregistrement-boucle-reelle-organisme-v1-brouillon1.md`, sections 8 et 9), **dans l'ordre du texte** : C5, C4, C2, C3,
C6, C1 ; la première ligne qui s'applique donne l'issue. Un arrêt ne masque jamais une brèche : sous C5, une fausse ou une copie
promue, ou une lecture de sélection en écart, s'écrit aussi (C2 ou C4 « partielle »). Les audits s'écrivent avant toute phrase
de résultat. Aucune moyenne ni médiane sur des jetons (aucun jeton n'est lu ici). Le code de sortie d'une course ne décide rien ;
ceci décide.

L'oracle du monde planté n'est lu qu'ici, après la course (dans l'esprit de N-050) : `mesures_oracle` classe les cartes réelles
(vraie découverte, fausse découverte, fausse promotion du juge, `oracle_tour_ferme_v60.classer`, seuil g₀ = 0,02 nat, gain
au-delà de l'archive de jugement de la carte) — mesure P7, sans issue ; une fausse découverte d'une carte réelle s'écrit en tête
et déclenche l'audit A2 sur sa forme. `rejouer_a2` rejoue une loi promue sur des tirages neufs (audit A2).
"""

VERSION = "lecture-boucle-reelle-v65"
VERSION_DU_COEUR = "boucle-reelle-v65"
VRAIES = ("V1", "V2", "V3", "V4")
FAUSSES = ("F1", "F2", "F3", "F4")
N_REJEU_A2 = 200  # « rejouer la loi promue 200 fois sur des tirages neufs » (brouillon, section 9)
MARGE_LOG_W = 1e-6  # « log W maximaux ≤ 0 aux marges près » (audit A1)
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
                             f"la lecture v65 ne lit que les relevés du cœur {VERSION_DU_COEUR}")
    for k in ("cartes", "plantees", "generations_jouees", "membres_attendus", "retenues", "etages"):
        if k not in releve:
            raise ReleveInvalide(f"relevé sans champ « {k} »")
    for p in releve["plantees"]:
        for k in ("generation", "nom", "promue", "gardien", "membres_d_archive", "membres_attendus", "verdict"):
            if k not in p:
                raise ReleveInvalide(f"loi plantée sans champ « {k} »")
    return releve


def p6_ecarts(releve):
    """P6 et A4 : écarts de la lecture de la sélection (empreinte lue ≠ écrite ; vue ≠ {K1} ∪ retenues ; membres d'archive des
    cartes et des lois plantées de la génération 2 ≠ ceux qu'impose l'archive lue ; copie d'une carte non retenue). Rend la
    liste des écarts (vide si P6 tient) ; None si la génération 2 n'a pas commencé (rien à lire)."""
    ls = releve.get("lecture_selection")
    if ls is None:
        return None
    ecarts = []
    if not ls.get("attendu") or ls.get("attendu") != ls.get("lu"):
        ecarts.append(f"empreinte lue {str(ls.get('lu'))[:12]}… ≠ écrite {str(ls.get('attendu'))[:12]}…")
    if sorted(ls.get("vue") or []) != sorted(ls.get("vue_attendue") or []) or not ls.get("vue_attendue"):
        ecarts.append(f"vue {sorted(ls.get('vue') or [])} ≠ {{K1}} ∪ retenues {sorted(ls.get('vue_attendue') or [])}")
    if sorted(ls.get("retenues_lues") or []) != sorted(ls.get("retenues_ecrites_g1") or []):
        ecarts.append("retenues lues ≠ retenues écrites par la génération 1")
    for c in ls.get("copies") or []:
        if c.get("source") not in (ls.get("retenues_ecrites_g1") or []):
            ecarts.append(f"copie {c.get('nom')} d'une carte non retenue ({c.get('source')})")
    attendus = (releve.get("membres_attendus") or {}).get("2")
    if 2 in (releve.get("generations_jouees") or []) or attendus is not None:
        for c in releve.get("cartes") or []:
            if c.get("generation") == 2 and c.get("gardien") == "passe" and c.get("membres_d_archive") != attendus:
                ecarts.append(f"carte {c.get('identifiant')} de la génération 2 jugée avec {c.get('membres_d_archive')} membres "
                              f"d'archive (attendus {attendus})")
        for p in _plantees(releve, 2):
            if p.get("gardien") == "passe" and p.get("membres_d_archive") != attendus:
                ecarts.append(f"loi plantée {p['nom']} de la génération 2 jugée avec {p.get('membres_d_archive')} membres (attendus {attendus})")
    return ecarts


def lire_criteres(releve):
    """Issue (C1 à C6) et constats, dans l'ordre gelé du texte. Rend un dictionnaire ; lève `ReleveInvalide` si le relevé n'est
    pas du cœur v65."""
    exiger_forme(releve)
    partiel = bool(releve.get("arret")) or not releve.get("complet")
    fausses_promues = [f"{p['nom']} (génération {p['generation']})" for p in _plantees(releve, noms=FAUSSES, copies=False) if p["promue"]]
    copies_promues = [f"{p['nom']} ← {p.get('source')}" for p in _plantees(releve, 2, copies=True) if p["promue"]]
    ecarts = p6_ecarts(releve)
    p6_tenue = ecarts == [] if ecarts is not None else False
    vraies_g1 = {p["nom"]: p for p in _plantees(releve, 1, noms=VRAIES)}
    vraies_survivantes = sorted(n for n, p in vraies_g1.items() if p["promue"] and p.get("verdict") == "survit")
    t_elim = next(iter(_plantees(releve, 1, noms=("T-ELIM",))), None)
    t_mal = next(iter(_plantees(releve, 1, noms=("T-MAL",))), None)
    p4 = bool(t_elim and t_elim["promue"] and t_elim.get("verdict") == "éliminée" and t_mal and t_mal["gardien"] == "refuse"
              and not t_mal["promue"])
    p1 = bool(vraies_survivantes) and not fausses_promues and not copies_promues
    constats = {"partiel": partiel, "arret": releve.get("arret"), "fausses_promues": fausses_promues,
                "copies_promues": copies_promues, "ecarts_p6": ecarts, "p6_tenue": p6_tenue,
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
    """Audits A1 à A4 (section 9), écrits avant toute phrase de résultat ; chacun déclenché selon l'issue ou le constat, le même
    quelle que soit l'issue. Rend {A1: …, A2: …, A3: …, A4: …} (None si non déclenché)."""
    c = lecture["constats"]
    out = {"A1": None, "A2": None, "A3": None, "A4": None}
    if lecture["code"] == "C1":  # « trop beau », d'office
        attendus = releve.get("membres_attendus") or {}
        vs = [p for p in _plantees(releve, 1, noms=VRAIES) if p["promue"] and p.get("verdict") == "survit"]
        etages = releve.get("etages") or []
        vue_sans_plantee = True
        ls = releve.get("lecture_selection") or {}
        noms_plantes = set(VRAIES) | set(FAUSSES) | {"T-ELIM", "T-MAL"}
        noms_plantes |= {p.get("identifiant") for p in releve.get("plantees") or []} | {p.get("identifiant_servi") for p in releve.get("plantees") or []}
        if set(ls.get("vue") or []) & noms_plantes:
            vue_sans_plantee = False
        fausses = _plantees(releve, noms=FAUSSES)
        out["A1"] = {"declenche": "d'office (issue C1)",
                     "vraies_survivantes_membres_justes": all(p.get("membres_d_archive") == attendus.get(str(p["generation"])) for p in vs),
                     "bac_reel_partout": bool(etages) and all(not e.get("factice") for e in etages),
                     "contre_calcul_egal": all(p.get("contre_calcul_ok") is not False for p in releve.get("plantees") or [])
                     and all(x.get("contre_calcul_ok") is not False for x in releve.get("cartes") or []),
                     "fausses_log_w_max_au_plus_0": all((p.get("log_richesse_max") is None) or p["log_richesse_max"] <= MARGE_LOG_W
                                                        for p in fausses),
                     "plus_grand_log_w_max_des_fausses": max((p["log_richesse_max"] for p in fausses if p.get("log_richesse_max") is not None),
                                                             default=None),
                     "vue_g2_sans_loi_plantee": vue_sans_plantee,
                     "a_verifier_sur_fichiers_bruts": ["fichier témoin et journal de bwrap de chaque gains.csv",
                                                       "registre du relais apparié appel par appel (expérimentateur appelé)"]}
    fp = [p for p in _plantees(releve, noms=FAUSSES, copies=False) if p["promue"]]
    if fp:
        out["A2"] = {"declenche": "fausse promue", "lois": [
            {"nom": p["nom"], "generation": p["generation"], "membres_d_archive": p.get("membres_d_archive"),
             "membres_attendus": p.get("membres_attendus"),
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
        out["A4"] = {"declenche": "copie promue ou lecture de sélection en écart", "copies": [
            {"nom": p["nom"], "source": p.get("source"), "promue": p["promue"], "membres_d_archive": p.get("membres_d_archive"),
             "membres_imposes_par_la_selection_lue": attendus, "source_retenue": p.get("source") in (ls.get("retenues_ecrites_g1") or [])}
            for p in _plantees(releve, 2, copies=True)], "ecarts_p6": c["ecarts_p6"]}
    return out


def mesures_oracle(releve, monde, oracle=None):
    """P7 (mesure sans issue) : par carte réelle promue, classe de l'oracle v60 contre l'archive de jugement de sa génération ;
    par fournisseur, proposées, refusées au gardien, promues, testées, survivantes, retenues, vraies et fausses découvertes. Une
    fausse découverte d'une carte réelle est rendue en tête (`fausses_decouvertes_reelles`)."""
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
    return {"par_fournisseur": par_f, "fausses_decouvertes_reelles": fd}


def forme_de_la_loi(loi):
    """Forme d'une loi pour l'audit A2 : « par morceaux », « produit ou composition », « mélange », « softmax », « autre »."""
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


def lire_boucle(releve, monde=None):
    """La lecture entière : critères, puis audits (écrits avant la phrase de résultat), puis mesures de l'oracle si `monde`."""
    lecture = lire_criteres(releve)
    sortie = {"version": VERSION, "audits": audits(releve, lecture), "issue": lecture["issue"], "code": lecture["code"],
              "aussi": lecture["aussi"], "constats": lecture["constats"]}
    if monde is not None and releve.get("cartes"):
        sortie["oracle"] = mesures_oracle(releve, monde)
    if monde is not None and sortie["audits"]["A2"]:  # A2 : chaque fausse promue rejouée 200 fois avec l'archive de sa génération
        for x in sortie["audits"]["A2"]["lois"]:
            p = next(q for q in releve["plantees"] if q["nom"] == x["nom"] and q["generation"] == x["generation"] and q["promue"])
            archive = (releve.get("archives_de_jugement") or {}).get(str(x["generation"])) or {}
            x["rejeu"] = rejouer_a2(p["loi"], monde, archive, int(releve["racine"]), n=N_REJEU_A2)
    sortie["phrase"] = (f"Issue {lecture['code']} : « {lecture['issue']} »" + (f" ; aussi : {', '.join(lecture['aussi'])}" if lecture["aussi"] else "")
                        + " (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte).")
    return sortie


__all__ = ("VERSION", "ISSUES", "ReleveInvalide", "lire_criteres", "audits", "mesures_oracle", "rejouer_a2", "lire_boucle",
           "p6_ecarts", "forme_de_la_loi")
