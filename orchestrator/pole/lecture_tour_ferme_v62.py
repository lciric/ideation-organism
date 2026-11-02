"""Lecture gelée du tour fermé, version 62 (fichier neuf, R12) — **étage 1 seul** (tâches A2 et A4). Remplace, pour le
brouillon 3, `lecture_tour_ferme_v61` (inchangée) ; corrections C10 et C16 de la contre-lecture 2
(`prereg/contre-lecture-preenregistrement-tour-ferme-v2.md` : B9, I16, I17, I18, mineurs 16 et 19).

Ce module ne lance rien : il lit le relevé scellé que produit `pole/tour_ferme_v62.py` et rend critères, issues et drapeaux
d'audit, dans l'ordre du texte (sections 4.3, 4.6, 4.7, 4.8 et 6). Le code de sortie d'une course ne décide rien ; ceci décide.

Ce qui change par rapport à la v61 :
- **B9, C10** : T1 attend une lecture vérifiée pour **chaque** (bras, g) avec 2 ≤ g ≤ `plan.generations`, que le bras joue ou
  non (la recopie-mélange lit le bilan du bras réel même quand l'archive vide l'empêche de jouer) ; attendu = lu ;
- **I16, C16** : P4 lue par cas, sur la taille de l'archive de jugement du bras aléatoire en génération 2 (relevé) ;
- **I17** : bras réel (ou aléatoire) sans carte jugée → issue A4 « non mesurable (aucune carte réelle jugée) », jamais « promeut
  autant » ;
- **I18** : le point (3) de S1 est le champ calculé `recherche_loi_plantee` du relevé ; absent, `null` ou mal formé → relevé
  invalide (aucune issue) ;
- **T34, mineur 16** : S5 porte sur le gardien mécanique **et** sur la part de « non concluant » par bras ;
- **mineur 19** : `vd_distinctes` calculé par le cœur, rapporté sans critère ;
- **T32** : une issue « ne tient pas » par arrêt de la liste d'arrêt est distinguée (phrase N1 d'arrêt, section 4.8).
"""

from .oracle_tour_ferme_v60 import classer, newcombe, wilson

VERSION = "lecture-tour-ferme-v62"
FAUX = ("T-F1", "T-F2", "T-F4", "T-ANTI")
SEUIL_INCONCLUSIF = 0.20
SEUIL_INCONCLUSIF_PAR_BRAS = 0.40
BRAS_ETAGE1 = ("reel", "aleatoire", "recopie_melange")
VERDICTS = ("survit", "éliminée", "non concluant")
P4_GENERATION_1 = (1, 4)
P4_TROIS_GENERATIONS = {"informative": (1, 6), "vide": (1, 8)}  # section 4.3 (T28) ; cas lu sur l'archive de jugement en g2
A4_SENSIBILITE = "sensibilité de la chaîne insuffisante : les proposeurs produisent de l'information que la chaîne ne retient pas"
A4_TAILLE = "on ne peut pas dire, à cette taille, que les vrais proposeurs battent le hasard dans ce monde"
A4_EGAL = ("le bras aléatoire promeut autant que le bras réel à cette taille : la chaîne ne distingue pas les vrais proposeurs "
           "du hasard dans ce monde")
A4_NON_MESURABLE = "non mesurable (aucune carte réelle jugée)"
ECART_S5 = 0.15


class ReleveInvalide(ValueError):
    pass


def _cartes(releve, bras=None, temoin=False, generation=None):
    out = []
    for c in releve.get("cartes") or []:
        if not isinstance(c, dict) or c.get("bras") not in BRAS_ETAGE1:
            raise ReleveInvalide(f"carte mal formée ou bras inconnu : {str(c)[:120]}")
        if c.get("verdict") is not None and c.get("verdict") not in VERDICTS:
            raise ReleveInvalide(f"verdict inconnu : {c.get('verdict')!r}")
        if (c.get("temoin") is not None) == temoin and (bras is None or c["bras"] == bras) \
                and (generation is None or c.get("generation") == generation):
            out.append(c)
    return out


def _testee(c):
    return c.get("verdict") in VERDICTS


def exiger_contre_calculs(releve):
    """B5 : toute carte ou tout témoin testé porte un contre-calcul booléen ; sinon `ReleveInvalide` (aucun repli)."""
    sans = [c.get("identifiant") for c in (releve.get("cartes") or []) if isinstance(c, dict) and _testee(c)
            and not isinstance(c.get("contre_calcul_ok"), bool)]
    if sans:
        raise ReleveInvalide(f"carte(s) testée(s) sans contre-calcul : {sans[:10]} : relevé invalide")


def exiger_recherche(releve):
    """I18 : la recherche de la loi plantée (S1, point 3) doit avoir été faite par le cœur, à chaque course."""
    r = releve.get("recherche_loi_plantee")
    if not isinstance(r, dict) or isinstance(r.get("contextes_cherches"), bool) or not isinstance(r.get("contextes_cherches"), int) \
            or not isinstance(r.get("touches"), list) or not isinstance(r.get("lignes_de_tranche_dans_les_contextes"), list):
        raise ReleveInvalide("recherche de la loi plantée absente, nulle ou mal formée (S1, point 3) : relevé invalide")
    return r


def comptes_bras(releve, bras, generation=None):
    cartes = _cartes(releve, bras, generation=generation)
    jugees = [c for c in cartes if c.get("gardien") == "passe"]
    flags = [classer(promue=c.get("promue"), survit=c.get("verdict") == "survit", gain_nat=c["gain_nat"],
                     delta_gain_nat=c["delta_gain_nat"], divergence_nat=c["divergence_nat"], bras=bras) for c in jugees]
    testees = [c for c in cartes + _cartes(releve, bras, temoin=True, generation=generation) if _testee(c)]
    n = len(jugees)
    r = {"proposees": len(cartes), "refusees_au_gardien": len(cartes) - n, "jugees": n,
         "ps": sum(bool(c.get("promue")) and c.get("verdict") == "survit" for c in jugees),
         "testees": len(testees), "non_concluant": sum(c.get("verdict") == "non concluant" for c in testees),
         "contre_calcul_en_desaccord": sum(c.get("contre_calcul_ok") is False for c in testees),
         "vd": sum(f["vraie_decouverte"] for f in flags), "vd_plantee": sum(f["loi_plantee_retrouvee"] for f in flags),
         "fd": sum(f["fausse_decouverte"] for f in flags), "fausses_promotions_du_juge": sum(f["fausse_promotion_du_juge"] for f in flags),
         "informatives": sum(f["informative_et_nouvelle"] for f in flags)}
    for k in ("ps", "vd", "fd", "informatives"):
        if n:
            r[f"wilson_{k}"] = list(wilson(r[k], n))
    r["part_ps_sur_proposees"] = r["ps"] / r["proposees"] if r["proposees"] else None
    r["part_non_concluant"] = r["non_concluant"] / r["testees"] if r["testees"] else 0.0
    r["part_refus_gardien"] = r["refusees_au_gardien"] / r["proposees"] if r["proposees"] else 0.0
    return r


def _jouees(releve):
    gj = releve.get("generations_jouees")
    if not isinstance(gj, dict) or set(gj) != set(BRAS_ETAGE1) \
            or any(not isinstance(v, list) or any(isinstance(g, bool) or not isinstance(g, int) or g < 1 for g in v)
                   for v in gj.values()):
        raise ReleveInvalide("relevé sans « generations_jouees » complet (une liste d'entiers ≥ 1 par bras)")
    return {b: sorted(set(v)) for b, v in gj.items()}


def _generations_du_plan(releve):
    g = (releve.get("plan") or {}).get("generations")
    if isinstance(g, bool) or not isinstance(g, int) or g < 2:
        raise ReleveInvalide("relevé sans plan.generations (entier ≥ 2) : lectures attendues incalculables")
    return g


def _newcombe_ou_rien(x1, n1, x2, n2):
    return list(newcombe(x1, n1, x2, n2)) if n1 and n2 else None


def cas_p4(releve):
    """« informative » si le bras aléatoire a été jugé en génération 2 contre une archive non vide, « vide » sinon (T28)."""
    g2 = [c.get("archive_de_jugement") for c in _cartes(releve, "aleatoire", generation=2)]
    if not g2 or any(isinstance(x, bool) or not isinstance(x, int) for x in g2):
        return None
    return "informative" if max(g2) > 0 else "vide"


def lire_etage1(releve):
    """Critères T1 à T5 (section 4.6), lecture A4 (section 4.7), prédictions (4.3, non décisives), audits S1, S2, S5.
    Lève `ReleveInvalide` sur un relevé mal formé, une carte testée sans contre-calcul (B5) ou sans recherche de L* (I18)."""
    if releve.get("etage") != 1:
        raise ReleveInvalide("relevé de l'étage 1 attendu")
    exiger_contre_calculs(releve)
    recherche = exiger_recherche(releve)
    jouees = _jouees(releve)
    n_gen = _generations_du_plan(releve)
    attendues = sum(len(v) for v in jouees.values())
    bras = {b: comptes_bras(releve, b) for b in BRAS_ETAGE1}
    tem = _cartes(releve, temoin=True)
    vraie = [c for c in tem if c["temoin"] == "T-VRAIE"]
    elim = [c for c in tem if c["temoin"] == "T-ELIM"]
    mal = [c for c in tem if c["temoin"] == "T-MAL"]
    b = releve.get("boucle") or {}
    lectures = b.get("lectures") or []
    lectures_attendues = sorted((x, g) for x in BRAS_ETAGE1 for g in range(2, n_gen + 1))  # B9 : jouées ou non
    lectures_faites = sorted((x.get("bras"), x.get("generation")) for x in lectures)
    t1 = (not releve.get("arret") and not b.get("incidents") and lectures_faites == lectures_attendues
          and all(x.get("attendu") == x.get("lu") and x.get("lu") for x in lectures))
    t2 = (len(vraie) == attendues and attendues > 0 and sum(c.get("verdict") == "survit" for c in vraie) >= attendues - 1
          and not any(c.get("verdict") == "éliminée" for c in vraie))
    faux_ps = sum(bool(c.get("promue")) and c.get("verdict") == "survit" for c in tem if c["temoin"] in FAUX)
    mal_par_passe = sorted((c["bras"], c.get("generation")) for c in mal)
    t3 = (faux_ps <= 1 and len(elim) == attendues and sum(c.get("verdict") == "éliminée" for c in elim) >= attendues - 1
          and not any(c.get("verdict") == "survit" for c in elim)
          and mal_par_passe == sorted((x, g) for x, v in jouees.items() for g in v)
          and all(c.get("gardien") == "refuse" for c in mal))
    testees = sum(r["testees"] for r in bras.values())
    nc = sum(r["non_concluant"] for r in bras.values())
    t4 = ((nc / testees if testees else 0.0) <= SEUIL_INCONCLUSIF
          and all(r["part_non_concluant"] <= SEUIL_INCONCLUSIF_PAR_BRAS for r in bras.values())
          and all(r["contre_calcul_en_desaccord"] == 0 for r in bras.values()))
    t5 = bras["aleatoire"]["fd"] <= 1 and bras["recopie_melange"]["fd"] <= 1
    t = {"T1": bool(t1), "T2": bool(t2), "T3": bool(t3), "T4": bool(t4), "T5": bool(t5)}
    manques = [k for k, v in t.items() if not v]
    nr, na = bras["reel"]["jugees"], bras["aleatoire"]["jugees"]
    diff = _newcombe_ou_rien(bras["reel"]["ps"], nr, bras["aleatoire"]["ps"], na)
    diff_vd = _newcombe_ou_rien(bras["reel"]["vd"], nr, bras["aleatoire"]["vd"], na)
    diff_info = _newcombe_ou_rien(bras["reel"]["informatives"], nr, bras["aleatoire"]["informatives"], na)
    g1 = {x: comptes_bras(releve, x, generation=1) for x in ("reel", "aleatoire")}
    diff_g1 = _newcombe_ou_rien(g1["reel"]["ps"], g1["reel"]["jugees"], g1["aleatoire"]["ps"], g1["aleatoire"]["jugees"])
    cause = None
    if not t5:
        a4 = "la chaîne ne discrimine pas"
    elif not nr or not na:
        a4 = A4_NON_MESURABLE  # I17 : jamais « promeut autant » sans carte réelle jugée
    elif diff[0] > 0:
        a4 = "discrimine"
    else:
        a4 = A4_EGAL
        cause = A4_SENSIBILITE if (diff_info is not None and diff_info[0] > 0) else A4_TAILLE
    passes_vraie = sum(c.get("verdict") == "survit" for c in vraie)
    na1 = g1["aleatoire"]["jugees"]
    cas = cas_p4(releve)
    bande = P4_TROIS_GENERATIONS.get(cas) if cas else None
    predictions = {
        "P1": passes_vraie == len(vraie) and len(vraie) > 0,
        "P2": faux_ps == 0,
        "P3": all(r["part_non_concluant"] <= 0.10 for r in bras.values()),
        "P4": {"generation_1": (P4_GENERATION_1[0] <= g1["aleatoire"]["ps"] <= P4_GENERATION_1[1]) if na1 else None,
               "cas": cas, "bande_trois_generations": list(bande) if bande else None,
               "trois_generations": (bande[0] <= bras["aleatoire"]["ps"] <= bande[1]) if (na and bande) else None,
               "fd": bras["aleatoire"]["fd"] <= 1},
        "P5": bras["recopie_melange"]["fd"] == 0,
        "P6": ((g1["reel"]["ps"] / g1["reel"]["jugees"] >= 0.30 and g1["reel"]["vd"] / g1["reel"]["jugees"] >= 0.25)
               if g1["reel"]["jugees"] else None),
        "P8": all(r["part_refus_gardien"] <= 0.10 for r in bras.values())}
    refus = [r["part_refus_gardien"] for r in bras.values() if r["proposees"]]
    inconclusifs = [r["part_non_concluant"] for r in bras.values() if r["testees"]]
    s1 = (all(r["fd"] == 0 and r["non_concluant"] == 0 for r in bras.values()) and passes_vraie == len(vraie)
          and any(c.get("generation") == 1 and classer(
              promue=c.get("promue"), survit=c.get("verdict") == "survit", gain_nat=c["gain_nat"],
              delta_gain_nat=c["delta_gain_nat"], divergence_nat=c["divergence_nat"], bras="reel")["loi_plantee_retrouvee"]
              for c in _cartes(releve, "reel") if c.get("gardien") == "passe"))
    s5_gardien = (max(refus) - min(refus) > ECART_S5) if refus else False
    s5_nc = (max(inconclusifs) - min(inconclusifs) > ECART_S5) if inconclusifs else False
    audits = {"S1_trop_beau": bool(s1),
              "S1_point_3_loi_plantee_dans_les_contextes": {"contextes_cherches": recherche["contextes_cherches"],
                                                           "touches": list(recherche["touches"]),
                                                           "lignes_de_tranche": list(recherche["lignes_de_tranche_dans_les_contextes"])},
              "S2_trop_laid": sum(c.get("verdict") in ("éliminée", "non concluant") for c in vraie) >= 2
              or (bras["aleatoire"]["fd"] / na > 0.05 if na else False) or bras["recopie_melange"]["fd"] > 0,
              "S5_asymetrie": bool(s5_gardien or s5_nc), "S5_gardien": bool(s5_gardien), "S5_non_concluant": bool(s5_nc)}
    issue = "tient" if not manques else f"ne tient pas ({', '.join(manques)})"
    return {"version": VERSION, "etage": 1, "criteres": t, "issue_etage_1": issue,
            "arret": releve.get("arret"), "n1": None if not manques else ("arret" if releve.get("arret") else "critere"),
            "passes_attendues": attendues, "lectures_attendues": len(lectures_attendues), "bras": bras,
            "generation_1": g1, "newcombe_ps_reel_moins_aleatoire": diff, "newcombe_vd_reel_moins_aleatoire": diff_vd,
            "newcombe_informatives_reel_moins_aleatoire": diff_info, "newcombe_ps_generation_1_seule": diff_g1,
            "issue_a4": a4, "cause_a4": cause, "recopie_mesurable": bras["recopie_melange"]["jugees"] > 0,
            "vd_distinctes": releve.get("vd_distinctes"),
            "reserve_majeure_pour_a3": a4 != "discrimine", "predictions": predictions, "audits": audits,
            "reserve_trop_beau": bool(s1)}


def lire_tour_etage_1(releve1):
    """L'étage 1 seul (ce texte) ; un relevé invalide donne « ne tient pas (relevé invalide) », jamais « tient »."""
    try:
        l1 = lire_etage1(releve1)
    except ReleveInvalide as e:
        l1 = {"version": VERSION, "etage": 1, "issue_etage_1": f"ne tient pas (relevé invalide : {e})", "n1": "critere",
              "arret": (releve1 or {}).get("arret"), "issue_a4": "non lue (relevé invalide)", "cause_a4": None,
              "reserve_majeure_pour_a3": True}
    return {"version": VERSION, "etage_1": l1, "etage_2": "hors de ce texte (étage 1 seul)"}


__all__ = ("lire_etage1", "lire_tour_etage_1", "comptes_bras", "exiger_contre_calculs", "exiger_recherche", "cas_p4",
           "ReleveInvalide", "VERSION", "SEUIL_INCONCLUSIF", "SEUIL_INCONCLUSIF_PAR_BRAS", "A4_EGAL", "A4_SENSIBILITE",
           "A4_TAILLE", "A4_NON_MESURABLE")
