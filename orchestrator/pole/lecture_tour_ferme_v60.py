"""Lecture gelée du tour fermé, version 60 (fichier neuf, R12 ; tâches A2, A3 et A4).

Préenregistrement : `prereg/preenregistrement-tour-ferme-v1-brouillon1.md`, sections 4.3 (prédictions), 4.6 (porte « l'étage 1
tient »), 4.7 (lecture A4), 5.6 (issues de A3) et 6 (audits calculés). Ce module **ne lance rien** : il lit un relevé (format
ci-dessous, que le lanceur v60 à écrire devra produire, scellé) et rend les critères, les issues et les drapeaux d'audit,
calculés dans l'ordre du texte. Le code de sortie d'une course ne décide rien ; ceci décide.

Relevé d'un étage : {"etage": 1|2, "arret": None|texte, "boucle": {"incidents": [...], "lectures": [{"attendu", "lu"}]},
"cartes": [{"bras", "generation", "identifiant", "temoin" (None ou T-VRAIE, T-F1, T-F2, T-F4, T-ANTI, T-ELIM, T-MAL, T2-CONNU,
T2-MAL), "gardien" ("passe"|"refuse"), "promue" (bool), "verdict" (None|"survit"|"éliminée"|"non concluant"),
"contre_calcul_ok" (None|bool), "gain_nat", "delta_gain_nat", "divergence_nat" (étage 1, cartes non témoins ; oracle),
"log_e", "statistique" (étage 2)}]}.
"""

from .oracle_tour_ferme_v60 import classer, newcombe, wilson

VERSION = "lecture-tour-ferme-v60"
FAUX = ("T-F1", "T-F2", "T-F4", "T-ANTI")
SEUIL_INCONCLUSIF = 0.20
BRAS_ETAGE1 = ("reel", "aleatoire", "recopie_melange")


class ReleveInvalide(ValueError):
    pass


def _cartes(releve, bras=None, temoin=False):
    out = []
    for c in releve.get("cartes") or []:
        if not isinstance(c, dict) or c.get("bras") not in (BRAS_ETAGE1 if releve.get("etage") == 1 else ("reel", "aleatoire")):
            raise ReleveInvalide(f"carte mal formée ou bras inconnu : {str(c)[:120]}")
        if (c.get("temoin") is not None) == temoin and (bras is None or c["bras"] == bras):
            out.append(c)
    return out


def _testee(c):
    return c.get("verdict") in ("survit", "éliminée", "non concluant")


def comptes_bras(releve, bras):
    cartes = _cartes(releve, bras)
    jugees = [c for c in cartes if c.get("gardien") == "passe"]
    flags = [classer(promue=c.get("promue"), survit=c.get("verdict") == "survit", gain_nat=c["gain_nat"],
                     delta_gain_nat=c["delta_gain_nat"], divergence_nat=c["divergence_nat"], bras=bras) for c in jugees] \
        if releve.get("etage") == 1 else []
    testees = [c for c in cartes + _cartes(releve, bras, temoin=True) if _testee(c)]
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
    for k in ("ps", "vd", "fd"):
        if k in r and n:
            r[f"wilson_{k}"] = list(wilson(r[k], n))
    r["part_non_concluant"] = r["non_concluant"] / r["testees"] if r["testees"] else 0.0
    r["part_refus_gardien"] = r["refusees_au_gardien"] / r["proposees"] if r["proposees"] else 0.0
    return r


def lire_etage1(releve):
    """Critères T1 à T5 (section 4.6), lecture A4 (section 4.7), prédictions (4.3, non décisives), audits S1, S2, S5."""
    if releve.get("etage") != 1:
        raise ReleveInvalide("relevé de l'étage 1 attendu")
    bras = {b: comptes_bras(releve, b) for b in BRAS_ETAGE1}
    tem = _cartes(releve, temoin=True)
    vraie = [c for c in tem if c["temoin"] == "T-VRAIE"]
    recopie_joue = any(c["bras"] == "recopie_melange" for c in tem)
    b = releve.get("boucle") or {}
    t = {"T1": not releve.get("arret") and not b.get("incidents") and all(x.get("attendu") == x.get("lu") and x.get("lu")
                                                                           for x in b.get("lectures") or [{}]),
         "T2": len(vraie) >= (8 if recopie_joue else 6) and sum(c.get("verdict") == "survit" for c in vraie) >= len(vraie) - 1
         and not any(c.get("verdict") == "éliminée" for c in vraie),
         "T3": sum(bool(c.get("promue")) and c.get("verdict") == "survit" for c in tem if c["temoin"] in FAUX) <= 1
         and not any(c.get("verdict") == "survit" for c in tem if c["temoin"] == "T-ELIM")
         and all(c.get("gardien") == "refuse" for c in tem if c["temoin"] == "T-MAL"),
         "T4": all(r["part_non_concluant"] <= SEUIL_INCONCLUSIF and r["contre_calcul_en_desaccord"] == 0 for r in bras.values()),
         "T5": bras["aleatoire"].get("fd", 0) <= 1 and bras["recopie_melange"].get("fd", 0) <= 1}
    manques = [k for k, v in t.items() if not v]
    recopie_mesurable = bras["recopie_melange"]["jugees"] > 0
    nr, na = bras["reel"]["jugees"], bras["aleatoire"]["jugees"]
    diff = list(newcombe(bras["reel"]["ps"], nr, bras["aleatoire"]["ps"], na)) if nr and na else None
    diff_vd = list(newcombe(bras["reel"].get("vd", 0), nr, bras["aleatoire"].get("vd", 0), na)) if nr and na else None
    if not t["T5"]:
        a4 = "la chaîne ne discrimine pas"
    elif diff is not None and diff[0] > 0:
        a4 = "discrimine"
    else:
        a4 = "la chaîne écarte les lois sans information, mais les vrais proposeurs ne battent pas le hasard dans ce monde"
    passes_vraie = sum(c.get("verdict") == "survit" for c in vraie)
    predictions = {"P1": passes_vraie == len(vraie) and len(vraie) > 0,
                   "P2": sum(bool(c.get("promue")) and c.get("verdict") == "survit" for c in tem if c["temoin"] in FAUX) == 0,
                   "P3": all(r["part_non_concluant"] <= 0.10 for r in bras.values()),
                   "P4": (0.05 <= bras["aleatoire"]["ps"] / na <= 0.25 if na else None, bras["aleatoire"].get("fd", 0) <= 1),
                   "P5": bras["recopie_melange"].get("fd", 0) == 0,
                   "P6": (bras["reel"]["ps"] / nr >= 0.30 and bras["reel"].get("vd", 0) / nr >= 0.25) if nr else None,
                   "P8": all(r["part_refus_gardien"] <= 0.10 for r in bras.values())}
    refus = [r["part_refus_gardien"] for r in bras.values() if r["proposees"]]
    audits = {"S1_trop_beau": all(r.get("fd", 0) == 0 and r["non_concluant"] == 0 for r in bras.values())
              and passes_vraie == len(vraie) and any(c.get("generation") == 1 and classer(
                  promue=c.get("promue"), survit=c.get("verdict") == "survit", gain_nat=c["gain_nat"],
                  delta_gain_nat=c["delta_gain_nat"], divergence_nat=c["divergence_nat"], bras="reel")["loi_plantee_retrouvee"]
                  for c in _cartes(releve, "reel") if c.get("gardien") == "passe"),
              "S2_trop_laid": sum(c.get("verdict") in ("éliminée", "non concluant") for c in vraie) >= 2
              or (bras["aleatoire"].get("fd", 0) / na > 0.05 if na else False) or bras["recopie_melange"].get("fd", 0) > 0,
              "S5_asymetrie_du_gardien": (max(refus) - min(refus) > 0.15) if refus else False}
    return {"version": VERSION, "etage": 1, "criteres": t, "issue_etage_1": "tient" if not manques else
            f"ne tient pas ({', '.join(manques)})", "bras": bras, "newcombe_ps_reel_moins_aleatoire": diff,
            "newcombe_vd_reel_moins_aleatoire": diff_vd, "issue_a4": a4, "recopie_mesurable": recopie_mesurable,
            "reserve_majeure_pour_a3": a4 != "discrimine", "predictions": predictions, "audits": audits}


def lire_etage2(releve, lecture1):
    """Issues N, P, Z de A3 (section 5.6), réserves automatiques et audits S3, S4."""
    if releve is not None and releve.get("etage") != 2:
        raise ReleveInvalide("relevé de l'étage 2 attendu")
    if lecture1.get("issue_etage_1") != "tient":
        return {"version": VERSION, "issue_a3": "N", "motif": f"étage 1 : {lecture1.get('issue_etage_1')}", "audits": {"S4": True}}
    if releve is None:
        raise ReleveInvalide("étage 1 « tient » : le relevé de l'étage 2 est exigé")
    bras = {b: comptes_bras(releve, b) for b in ("reel", "aleatoire")}
    if releve.get("arret") or any(r["part_non_concluant"] > SEUIL_INCONCLUSIF or r["contre_calcul_en_desaccord"]
                                  for r in bras.values()):
        return {"version": VERSION, "issue_a3": "N", "motif": "arrêt, non concluant > 0,20 ou contre-calcul en désaccord",
                "bras": bras, "audits": {"S4": True}}

    def ps(c):
        return c.get("gardien") == "passe" and bool(c.get("promue")) and c.get("verdict") == "survit" \
            and c.get("contre_calcul_ok") is True

    decisives = [c["identifiant"] for c in _cartes(releve, "reel") if c.get("generation") == 1 and ps(c)]
    relues = [c["identifiant"] for c in _cartes(releve, "reel") if c.get("generation", 1) >= 2 and ps(c)]
    hasard = [c["identifiant"] for c in _cartes(releve, "aleatoire") if ps(c)]
    reserves = ([("a", "réserve A4 : " + lecture1["issue_a4"])] if lecture1.get("reserve_majeure_pour_a3") else []) \
        + ([("b", "le hasard passe aussi la chaîne sur la banque réelle")] if hasard else [])
    trop_beau = any((c.get("log_e") or 0) > 20 or (c.get("statistique") or 0) > 0.3
                    for c in _cartes(releve, "reel") if ps(c))
    return {"version": VERSION, "issue_a3": "P" if decisives else "Z", "decisives_generation_1": decisives,
            "survivantes_sur_T_relue_generation_2": relues, "aleatoires_promues_puis_survivantes": hasard,
            "reserves": reserves, "bras": bras, "audits": {"S3": trop_beau, "S4": not decisives}}


__all__ = ("lire_etage1", "lire_etage2", "comptes_bras", "ReleveInvalide", "VERSION", "SEUIL_INCONCLUSIF")
