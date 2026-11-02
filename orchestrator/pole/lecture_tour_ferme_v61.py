"""Lecture gelée du tour fermé, version 61 (fichier neuf, R12 ; tâches A2, A3 et A4). Remplace, pour le brouillon 2 et la
suite, `lecture_tour_ferme_v60` (inchangée) ; corrections C1 et C2 de la contre-lecture
(`prereg/contre-lecture-preenregistrement-tour-ferme-v1.md`, constats B3, B4, B5, I5, mineur 10).

Préenregistrement : `prereg/preenregistrement-tour-ferme-v1-brouillon2.md`, sections 4.3, 4.6, 4.7, 5.6 et 6. Ce module ne
lance rien : il lit le relevé scellé que produit `pole/tour_ferme_v61.py` et rend critères, issues et drapeaux d'audit, dans
l'ordre du texte. Le code de sortie d'une course ne décide rien ; ceci décide.

Ce qui change par rapport à la v60 :
- T1 exige **une lecture vérifiée par génération g ≥ 2 de chaque bras qui joue** (`generations_jouees` du relevé), ni plus ni
  moins, attendu = lu ;
- T2 compte les passes attendues sur le journal (une par génération jouée de chaque bras), au lieu de 8 ou 6 codés en dur ;
- T3 exige T-ELIM testé et « éliminée » dans toutes ses passes sauf au plus une, jamais « survit », et T-MAL présent et
  refusé dans chaque génération jouée de chaque bras ;
- T4 : « non concluant » / testées ≤ 0,20 sur les trois bras réunis et ≤ 0,40 dans chaque bras ; **toute carte ou tout
  témoin testé sans contre-calcul booléen rend le relevé invalide** (`ReleveInvalide` à l'étage 1, issue N1 par
  `lire_tour` ; issue N2 à l'étage 2), jamais Z ni « tient » ;
- A4 : la cause d'un écart non positif vient de l'oracle (Newcombe sur la part informative et nouvelle, réel − aléatoire,
  mesurée sur toutes les cartes jugées) ; le libellé « ne battent pas le hasard » disparaît ; la génération 1 seule est
  rapportée à côté, sans décider ; découvertes distinctes et part sur cartes proposées rapportées ;
- N1 (étage 1) et N2 (étage 2) distingués ; la réserve (a) de l'étage 2 reprend la cause lue en A4.

Relevé d'un étage : {"etage": 1|2, "arret": None|texte, "generations_jouees": {bras: [g, …]}, "boucle": {"incidents": [...],
"lectures": [{"bras", "generation", "attendu", "lu"}]}, "cartes": [{"bras", "generation", "identifiant", "temoin" (None ou
T-VRAIE, T-F1, T-F2, T-F4, T-ANTI, T-ELIM, T-MAL, T2-CONNU, T2-MAL), "gardien" ("passe"|"refuse"), "promue" (bool), "verdict"
(None|"survit"|"éliminée"|"non concluant"), "contre_calcul_ok" (bool pour toute carte testée), "gain_nat", "delta_gain_nat",
"divergence_nat" (étage 1, cartes non témoins), "log_e", "statistique" (étage 2)}], "vd_distinctes": {bras: entier}
(facultatif), "recherche_loi_plantee": [...] (facultatif)}.
"""

from .oracle_tour_ferme_v60 import classer, newcombe, wilson

VERSION = "lecture-tour-ferme-v61"
FAUX = ("T-F1", "T-F2", "T-F4", "T-ANTI")
SEUIL_INCONCLUSIF = 0.20
SEUIL_INCONCLUSIF_PAR_BRAS = 0.40
BRAS_ETAGE1 = ("reel", "aleatoire", "recopie_melange")
BRAS_ETAGE2 = ("reel", "aleatoire")
VERDICTS = ("survit", "éliminée", "non concluant")
# Prédictions P4 (bras aléatoire) : bornes relues sur la lecture L2b-v61 (section 10 du texte), non décisives.
P4_GENERATION_1 = (1, 4)
P4_TROIS_GENERATIONS = (1, 6)
A4_SENSIBILITE = "sensibilité de la chaîne insuffisante : les proposeurs produisent de l'information que la chaîne ne retient pas"
A4_TAILLE = "on ne peut pas dire, à cette taille, que les vrais proposeurs battent le hasard dans ce monde"
A4_EGAL = ("le bras aléatoire promeut autant que le bras réel à cette taille : la chaîne ne distingue pas les vrais proposeurs "
           "du hasard dans ce monde")


class ReleveInvalide(ValueError):
    pass


def _bras_permis(releve):
    return BRAS_ETAGE1 if releve.get("etage") == 1 else BRAS_ETAGE2


def _cartes(releve, bras=None, temoin=False, generation=None):
    out = []
    for c in releve.get("cartes") or []:
        if not isinstance(c, dict) or c.get("bras") not in _bras_permis(releve):
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


def comptes_bras(releve, bras, generation=None):
    cartes = _cartes(releve, bras, generation=generation)
    jugees = [c for c in cartes if c.get("gardien") == "passe"]
    flags = [classer(promue=c.get("promue"), survit=c.get("verdict") == "survit", gain_nat=c["gain_nat"],
                     delta_gain_nat=c["delta_gain_nat"], divergence_nat=c["divergence_nat"], bras=bras) for c in jugees] \
        if releve.get("etage") == 1 else []
    testees = [c for c in cartes + _cartes(releve, bras, temoin=True, generation=generation) if _testee(c)]
    n = len(jugees)
    r = {"proposees": len(cartes), "refusees_au_gardien": len(cartes) - n, "jugees": n,
         "ps": sum(bool(c.get("promue")) and c.get("verdict") == "survit" for c in jugees),
         "testees": len(testees), "non_concluant": sum(c.get("verdict") == "non concluant" for c in testees),
         "contre_calcul_en_desaccord": sum(c.get("contre_calcul_ok") is False for c in testees)}
    if flags:
        r.update(vd=sum(f["vraie_decouverte"] for f in flags), vd_plantee=sum(f["loi_plantee_retrouvee"] for f in flags),
                 fd=sum(f["fausse_decouverte"] for f in flags),
                 fausses_promotions_du_juge=sum(f["fausse_promotion_du_juge"] for f in flags),
                 informatives=sum(f["informative_et_nouvelle"] for f in flags))
    for k in ("ps", "vd", "fd", "informatives"):
        if k in r and n:
            r[f"wilson_{k}"] = list(wilson(r[k], n))
    r["part_ps_sur_proposees"] = r["ps"] / r["proposees"] if r["proposees"] else None
    r["part_non_concluant"] = r["non_concluant"] / r["testees"] if r["testees"] else 0.0
    r["part_refus_gardien"] = r["refusees_au_gardien"] / r["proposees"] if r["proposees"] else 0.0
    return r


def _jouees(releve):
    gj = releve.get("generations_jouees")
    if not isinstance(gj, dict) or set(gj) != set(_bras_permis(releve)) \
            or any(not isinstance(v, list) or any(isinstance(g, bool) or not isinstance(g, int) or g < 1 for g in v)
                   for v in gj.values()):
        raise ReleveInvalide("relevé sans « generations_jouees » complet (une liste d'entiers ≥ 1 par bras)")
    return {b: sorted(set(v)) for b, v in gj.items()}


def _newcombe_ou_rien(x1, n1, x2, n2):
    return list(newcombe(x1, n1, x2, n2)) if n1 and n2 else None


def lire_etage1(releve):
    """Critères T1 à T5 (section 4.6), lecture A4 (section 4.7), prédictions (4.3, non décisives), audits S1, S2, S5.
    Lève `ReleveInvalide` sur un relevé mal formé ou une carte testée sans contre-calcul (B5)."""
    if releve.get("etage") != 1:
        raise ReleveInvalide("relevé de l'étage 1 attendu")
    exiger_contre_calculs(releve)
    jouees = _jouees(releve)
    attendues = sum(len(v) for v in jouees.values())
    bras = {b: comptes_bras(releve, b) for b in BRAS_ETAGE1}
    tem = _cartes(releve, temoin=True)
    vraie = [c for c in tem if c["temoin"] == "T-VRAIE"]
    elim = [c for c in tem if c["temoin"] == "T-ELIM"]
    mal = [c for c in tem if c["temoin"] == "T-MAL"]
    b = releve.get("boucle") or {}
    lectures = b.get("lectures") or []
    lectures_attendues = sorted((x, g) for x, v in jouees.items() for g in v if g >= 2)
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
    t5 = bras["aleatoire"].get("fd", 0) <= 1 and bras["recopie_melange"].get("fd", 0) <= 1
    t = {"T1": bool(t1), "T2": bool(t2), "T3": bool(t3), "T4": bool(t4), "T5": bool(t5)}
    manques = [k for k, v in t.items() if not v]
    nr, na = bras["reel"]["jugees"], bras["aleatoire"]["jugees"]
    diff = _newcombe_ou_rien(bras["reel"]["ps"], nr, bras["aleatoire"]["ps"], na)
    diff_vd = _newcombe_ou_rien(bras["reel"].get("vd", 0), nr, bras["aleatoire"].get("vd", 0), na)
    diff_info = _newcombe_ou_rien(bras["reel"].get("informatives", 0), nr, bras["aleatoire"].get("informatives", 0), na)
    g1 = {x: comptes_bras(releve, x, generation=1) for x in ("reel", "aleatoire")}
    diff_g1 = _newcombe_ou_rien(g1["reel"]["ps"], g1["reel"]["jugees"], g1["aleatoire"]["ps"], g1["aleatoire"]["jugees"])
    cause = None
    if not t5:
        a4 = "la chaîne ne discrimine pas"
    elif diff is not None and diff[0] > 0:
        a4 = "discrimine"
    else:
        a4 = A4_EGAL
        cause = A4_SENSIBILITE if (diff_info is not None and diff_info[0] > 0) else A4_TAILLE
    passes_vraie = sum(c.get("verdict") == "survit" for c in vraie)
    na1 = g1["aleatoire"]["jugees"]
    predictions = {
        "P1": passes_vraie == len(vraie) and len(vraie) > 0,
        "P2": faux_ps == 0,
        "P3": all(r["part_non_concluant"] <= 0.10 for r in bras.values()),
        "P4": {"generation_1": (P4_GENERATION_1[0] <= g1["aleatoire"]["ps"] <= P4_GENERATION_1[1]) if na1 else None,
               "trois_generations": (P4_TROIS_GENERATIONS[0] <= bras["aleatoire"]["ps"] <= P4_TROIS_GENERATIONS[1]) if na else None,
               "fd": bras["aleatoire"].get("fd", 0) <= 1},
        "P5": bras["recopie_melange"].get("fd", 0) == 0,
        "P6": ((g1["reel"]["ps"] / g1["reel"]["jugees"] >= 0.30 and g1["reel"].get("vd", 0) / g1["reel"]["jugees"] >= 0.25)
               if g1["reel"]["jugees"] else None),
        "P8": all(r["part_refus_gardien"] <= 0.10 for r in bras.values())}
    refus = [r["part_refus_gardien"] for r in bras.values() if r["proposees"]]
    s1 = (all(r.get("fd", 0) == 0 and r["non_concluant"] == 0 for r in bras.values()) and passes_vraie == len(vraie)
          and any(c.get("generation") == 1 and classer(
              promue=c.get("promue"), survit=c.get("verdict") == "survit", gain_nat=c["gain_nat"],
              delta_gain_nat=c["delta_gain_nat"], divergence_nat=c["divergence_nat"], bras="reel")["loi_plantee_retrouvee"]
              for c in _cartes(releve, "reel") if c.get("gardien") == "passe"))
    audits = {"S1_trop_beau": bool(s1),
              "S1_point_3_loi_plantee_dans_les_contextes": list(releve.get("recherche_loi_plantee") or []),
              "S2_trop_laid": sum(c.get("verdict") in ("éliminée", "non concluant") for c in vraie) >= 2
              or (bras["aleatoire"].get("fd", 0) / na > 0.05 if na else False) or bras["recopie_melange"].get("fd", 0) > 0,
              "S5_asymetrie_du_gardien": (max(refus) - min(refus) > 0.15) if refus else False}
    return {"version": VERSION, "etage": 1, "criteres": t,
            "issue_etage_1": "tient" if not manques else f"ne tient pas ({', '.join(manques)})",
            "passes_attendues": attendues, "lectures_attendues": len(lectures_attendues), "bras": bras,
            "generation_1": g1, "newcombe_ps_reel_moins_aleatoire": diff, "newcombe_vd_reel_moins_aleatoire": diff_vd,
            "newcombe_informatives_reel_moins_aleatoire": diff_info, "newcombe_ps_generation_1_seule": diff_g1,
            "issue_a4": a4, "cause_a4": cause, "recopie_mesurable": bras["recopie_melange"]["jugees"] > 0,
            "vd_distinctes": dict(releve.get("vd_distinctes") or {}),
            "reserve_majeure_pour_a3": a4 != "discrimine", "predictions": predictions, "audits": audits,
            "reserve_trop_beau": bool(s1)}


def lire_etage2(releve, lecture1):
    """Issues N (N1 : étage 1 ; N2 : étage 2), P, Z de A3 (section 5.6), réserves automatiques et audits S3, S4."""
    if releve is not None and releve.get("etage") != 2:
        raise ReleveInvalide("relevé de l'étage 2 attendu")
    if lecture1.get("issue_etage_1") != "tient":
        return {"version": VERSION, "issue_a3": "N", "n": "N1", "motif": f"étage 1 : {lecture1.get('issue_etage_1')}",
                "audits": {"S4": True}}
    if releve is None:
        raise ReleveInvalide("étage 1 « tient » : le relevé de l'étage 2 est exigé")
    try:
        exiger_contre_calculs(releve)
    except ReleveInvalide as e:
        return {"version": VERSION, "issue_a3": "N", "n": "N2", "motif": f"relevé invalide : {e}", "audits": {"S4": True}}
    bras = {b: comptes_bras(releve, b) for b in BRAS_ETAGE2}
    testees = sum(r["testees"] for r in bras.values())
    nc = sum(r["non_concluant"] for r in bras.values())
    motif = ("arrêt de la liste d'arrêt" if releve.get("arret") else
             "« non concluant » au-dessus de 0,20 des cartes testées" if testees and nc / testees > SEUIL_INCONCLUSIF else
             "contre-calcul en désaccord" if any(r["contre_calcul_en_desaccord"] for r in bras.values()) else None)
    if motif:
        return {"version": VERSION, "issue_a3": "N", "n": "N2", "motif": motif, "bras": bras, "audits": {"S4": True}}

    def ps(c):
        return c.get("gardien") == "passe" and bool(c.get("promue")) and c.get("verdict") == "survit" \
            and c.get("contre_calcul_ok") is True

    decisives = [c["identifiant"] for c in _cartes(releve, "reel") if c.get("generation") == 1 and ps(c)]
    relues = [c["identifiant"] for c in _cartes(releve, "reel") if c.get("generation", 1) >= 2 and ps(c)]
    hasard = [c["identifiant"] for c in _cartes(releve, "aleatoire") if ps(c)]
    connu = [c["identifiant"] for c in _cartes(releve, temoin=True) if c["temoin"] == "T2-CONNU" and c.get("promue")]
    reserve_a = lecture1["issue_a4"] + (f" ({lecture1['cause_a4']})" if lecture1.get("cause_a4") else "")
    reserves = ([("a", "réserve A4 : " + reserve_a)] if lecture1.get("reserve_majeure_pour_a3") else []) \
        + ([("b", "le hasard passe aussi la chaîne sur la banque réelle")] if hasard else [])
    trop_beau = any((c.get("log_e") or 0) > 20 or (c.get("statistique") or 0) > 0.3 for c in _cartes(releve, "reel") if ps(c))
    return {"version": VERSION, "issue_a3": "P" if decisives else "Z", "decisives_generation_1": decisives,
            "survivantes_sur_T_relue_generation_2": relues, "aleatoires_promues_puis_survivantes": hasard,
            "temoin_connu_promu": connu, "reserves": reserves, "bras": bras,
            "audits": {"S3": trop_beau, "S4": not decisives}, "reserve_trop_beau": trop_beau}


def lire_tour(releve1, releve2=None):
    """Les deux étages dans l'ordre du texte ; un relevé de l'étage 1 invalide (B5) donne l'issue N1, jamais Z ni « tient »."""
    try:
        l1 = lire_etage1(releve1)
    except ReleveInvalide as e:
        l1 = {"version": VERSION, "etage": 1, "issue_etage_1": f"ne tient pas (relevé invalide : {e})",
              "issue_a4": "non lue (relevé invalide)", "cause_a4": None, "reserve_majeure_pour_a3": True}
    return {"etage_1": l1, "etage_2": lire_etage2(releve2, l1)}


__all__ = ("lire_etage1", "lire_etage2", "lire_tour", "comptes_bras", "exiger_contre_calculs", "ReleveInvalide", "VERSION",
           "SEUIL_INCONCLUSIF", "SEUIL_INCONCLUSIF_PAR_BRAS", "A4_EGAL", "A4_SENSIBILITE", "A4_TAILLE")
