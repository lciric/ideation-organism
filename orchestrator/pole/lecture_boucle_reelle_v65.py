"""Lecture gelée de la plus petite course réelle de la boucle complète, version 65 (fichier neuf, R12) — critères C1 à C6 et
audits A1 à A4 du brouillon 1 du préenregistrement (dépôt de travail, `docs/notes/organisme-boucle-reelle-v1/
preenregistrement-boucle-reelle-organisme-v1-brouillon1.md`, sha256 736e3fd6…, sections 4 à 9). Appelée après la course par un
programme à part (`demonstrations/lire_boucle_reelle_v65.py`), par un lecteur neuf (R13). Aucun appel de modèle, aucun réseau.

Ordre gelé (§ 8) ; la première ligne qui s'applique donne l'issue :
- **C5** « non jugeable (arrêt) » : course arrêtée ou relevé incomplet ; si le relevé partiel montre déjà une fausse ou une copie
  promue, ou une lecture de sélection en écart, C2 ou C4 s'écrit aussi, marquée « partielle » (un arrêt ne masque jamais une
  brèche) ;
- **C4** « boucle non fermée » : P6 manquée (empreinte lue ≠ écrite ; vue ou archive de la génération 2 ≠ {K1} ∪ retenues ;
  membres d'archive des lois jugées en génération 2 ≠ ceux qu'impose {K1} ∪ retenues ; copies ≠ quatre premières retenues par
  log e), ou une copie de la génération 2 promue ;
- **C2** « brèche dans la classe couverte » : une fausse F1 à F4 promue en génération 1 ou 2 ;
- **C3** « sans dents » : aucune vraie promue puis survivante en génération 1 ;
- **C6** « instrument en défaut » : T-ELIM survivante, non concluante ou non promue, ou T-MAL jugée (passée au gardien) ;
- **C1** « la chaîne garde (classe couverte, ce monde, cette taille) » : P1, P4 et P6 tenues.
Audits (§ 9), déclenchés d'office et écrits avant toute phrase de résultat : **A1** si C1 (« trop beau ») ; **A2** si une fausse
est promue, et pour toute fausse découverte d'une carte réelle ; **A3** si C3 ; **A4** si une copie est promue.
Mesures sans issue : P3 (V3 et V4), P7 (cartes réelles par fournisseur, classes de l'oracle), coût, recherche de la loi plantée.
**Aucune moyenne ni médiane sur des jetons** : la lecture ne lit aucun jeton. L'oracle du monde planté n'est calculé qu'ici, après
la course (§ 7.3), avec la racine des graines du relevé.
"""

import math

from . import a_blanc_v59 as A
from . import boucle_reelle_v65 as B
from .oracle_tour_ferme_v60 import G0, Oracle, classer

VERSION = "lecture-boucle-reelle-v65"
ISSUES = {"C1": "la chaîne garde (classe couverte, ce monde, cette taille)", "C2": "brèche dans la classe couverte",
          "C3": "sans dents", "C4": "boucle non fermée", "C5": "non jugeable (arrêt)", "C6": "instrument en défaut"}
ORDRE = ("C5", "C4", "C2", "C3", "C6", "C1")
TOLERANCE_LOG_W_FAUSSE = 1e-6  # A1 : une fausse de la classe couverte a W ≤ 1 à chaque instant, aux arrondis flottants près
REJEUX_A2 = 200


class LectureImpossible(ValueError):
    """Relevé d'une autre version, ou sans les champs que la lecture gelée lit."""


def _plantees(releve, generation=None, groupe=None, nom=None):
    return [p for p in releve.get("plantees") or [] if (generation is None or p.get("generation") == generation)
            and (groupe is None or p.get("groupe") == groupe) and (nom is None or p.get("nom") == nom)]


def _promue_survivante(p):
    return bool(p.get("promue")) and p.get("verdict") == "survit"


def _retenues_g1(releve):
    return sorted(c["identifiant_servi"] for c in releve.get("cartes") or [] if c.get("generation") == 1 and c.get("retenue"))


def verifier_lecture_selection(releve):
    """P6 : rend la liste des écarts (vide = tenue) — lectures (attendu = lu), vue, archive et membres d'archive de la génération 2,
    copies conformes à la sélection lue."""
    ecarts = []
    depart = releve.get("heritage_depart") or {}
    k = dict(depart.get("archive") or {})
    retenues = _retenues_g1(releve)
    if 2 not in (releve.get("generations_jouees") or []):
        return ecarts
    lectures = {str(x.get("generation")): x for x in (releve.get("boucle") or {}).get("lectures") or []}
    if "2" not in lectures:
        ecarts.append("lecture de la sélection de la génération 1 absente")
    for g, x in sorted(lectures.items()):
        if x.get("attendu") != x.get("lu") or not x.get("lu"):
            ecarts.append(f"lecture {g} : empreinte lue {str(x.get('lu'))[:12]} ≠ écrite {str(x.get('attendu'))[:12]}")
    attendu = sorted(set(k) | set(retenues))
    if "2" in lectures and sorted(lectures["2"].get("retenues_lues") or []) != retenues:
        ecarts.append(f"retenues lues {sorted(lectures['2'].get('retenues_lues') or [])} ≠ retenues écrites {retenues}")
    vues = {v.get("generation"): v for v in releve.get("vues") or []}
    if sorted((vues.get(2) or {}).get("lois") or []) != attendu:
        ecarts.append(f"vue de la génération 2 {sorted((vues.get(2) or {}).get('lois') or [])} ≠ {{K1}} ∪ retenues {attendu}")
    arch2 = (releve.get("archives_de_jugement") or {}).get("2")
    if not isinstance(arch2, dict) or sorted(arch2) != attendu:
        ecarts.append(f"archive de jugement de la génération 2 {sorted(arch2 or {})} ≠ {{K1}} ∪ retenues {attendu}")
    else:
        lois_ret = {c["identifiant_servi"]: c.get("loi") for c in releve.get("cartes") or [] if c.get("identifiant_servi") in retenues}
        attendue = dict(k, **lois_ret)
        if not B._egales(arch2, attendue):
            ecarts.append("archive de jugement de la génération 2 : lois ≠ K1 et lois des retenues")
        n = B.membres_attendus(attendue)
        jugees = [c for c in releve.get("cartes") or [] if c.get("generation") == 2 and c.get("gardien") == "passe"] + \
                 [p for p in _plantees(releve, 2) if p.get("gardien") == "passe"]
        faux = sorted(x["identifiant_servi"] for x in jugees if x.get("membres_d_archive") != n)
        if faux:
            ecarts.append(f"membres d'archive de la génération 2 ≠ {n} (imposés par {{K1}} ∪ retenues) pour {faux}")
    log_e = {c["identifiant_servi"]: c.get("log_e") for c in releve.get("cartes") or [] if c.get("generation") == 1}
    ordre = sorted(retenues, key=lambda i: (-(log_e.get(i) if isinstance(log_e.get(i), (int, float)) else -math.inf), i))
    attendues = ordre[:B.COPIES_MAX]
    copies = [(c.get("nom"), c.get("source")) for c in releve.get("copies") or []]
    if [s for _, s in copies] != attendues:
        ecarts.append(f"copies de la génération 2 {copies} ≠ quatre premières retenues par log e {attendues}")
    replantees = sorted(p.get("source") for p in _plantees(releve, 2, "copie"))
    if replantees != sorted(attendues):
        ecarts.append(f"copies jugées en génération 2 {replantees} ≠ {sorted(attendues)}")
    return ecarts


def _complet(releve):
    """Relevé complet : deux générations jouées, lecture finale, cartes et lois plantées des deux générations présentes."""
    manques = []
    if (releve.get("generations_jouees") or []) != [1, 2]:
        manques.append(f"générations jouées {releve.get('generations_jouees')} ≠ [1, 2]")
    if "finale" not in {str(x.get("generation")) for x in (releve.get("boucle") or {}).get("lectures") or []}:
        manques.append("lecture finale du bilan de la génération 2 absente")
    noms_g1 = sorted(p.get("nom") for p in _plantees(releve, 1))
    if noms_g1 != sorted(B.PLANTEES_G1):
        manques.append(f"lois plantées de la génération 1 {noms_g1} ≠ {sorted(B.PLANTEES_G1)}")
    if sorted(p.get("nom") for p in _plantees(releve, 2, "fausse")) != sorted(B.FAUSSES):
        manques.append("fausses replantées de la génération 2 incomplètes")
    return manques


def mesures_oracle(releve, monde):
    """Classes gelées de l'oracle v60 (§ 5) pour les cartes réelles passées au gardien : gain, gain au-delà de l'archive de jugement
    de leur génération, divergence ; calculées ici seulement, après la course."""
    o = Oracle(monde["loi"], int(releve["entropie_racine"]), A.DIM)
    out = {}
    archives = releve.get("archives_de_jugement") or {}
    gains_archive = {g: o.gain_archive(a) for g, a in archives.items()}
    for c in releve.get("cartes") or []:
        if c.get("gardien") != "passe" or c.get("loi") is None:
            continue
        g = str(c["generation"])
        gain, div = o.gain(c["loi"]), o.divergence(c["loi"])
        f = classer(promue=c.get("promue"), survit=c.get("verdict") == "survit", gain_nat=gain, delta_gain_nat=gain - gains_archive.get(g, 0.0),
                    divergence_nat=div, bras="reel")
        out[c["identifiant_servi"]] = dict(f, gain_nat=round(gain, 6), delta_gain_nat=round(gain - gains_archive.get(g, 0.0), 6),
                                           divergence_nat=round(div, 6), generation=c["generation"], fournisseur=c.get("fournisseur"))
    return out


def forme_de_la_loi(loi, connues):
    """A2 : forme d'une loi promue — ligne couverte du banc, ou « par morceaux », « produit », « composition », « autre »."""
    ligne = B.classer_couverte(loi, connues)
    if ligne:
        return f"couverte ({ligne})"
    t = loi.get("type") if isinstance(loi, dict) else None
    if t in ("si_sinon", "par_sous_population"):
        return "par morceaux"
    if t == "transformee" and len(set(loi) - {"type", "base"}) > 1 and ({"melange_aveugle", "oscillation"} & set(loi)):
        return "composition"
    if t == "transformee" and "oscillation" in loi:
        return "autre (oscillation)"
    return "autre"


def _rejouer(loi, monde, archive, racine, tache, n):
    """A2 : la loi rejouée `n` fois sur des tirages neufs (tâches « …|rejeu=k »), même archive ; rend le nombre de promotions."""
    k = 0
    for r in range(n):
        ev, _ = A.juger_carte(loi, monde, archive, racine, f"{tache}|rejeu={r}")
        k += bool(ev["promue"])
    return k


def lire_boucle(releve, monde, rejeux_a2=REJEUX_A2, journal=None):
    """La lecture gelée : rend {issue, code, lignes, partielles, audits, mesures, en_tete}. `journal` (facultatif) : le journal de
    la course, pour l'audit A1 (bac réel, contre-calcul) ; `rejeux_a2` : nombre de rejeux de l'audit A2 (200 au brouillon)."""
    if not isinstance(releve, dict) or releve.get("version") != B.VERSION:
        raise LectureImpossible(f"relevé d'une autre version ({(releve or {}).get('version')!r}) : la lecture v65 ne lit que {B.VERSION}")
    for cle in ("cartes", "plantees", "boucle", "heritage_depart", "generations_jouees", "entropie_racine"):
        if cle not in releve:
            raise LectureImpossible(f"relevé sans le champ « {cle} »")
    arret = releve.get("arret")
    manques = _complet(releve)
    ecarts_p6 = verifier_lecture_selection(releve)
    fausses_promues = sorted(f"G{p['generation']}-{p['nom']}" for p in releve["plantees"] if p.get("groupe") == "fausse" and p.get("promue"))
    copies_promues = sorted(f"G{p['generation']}-{p['nom']}" for p in releve["plantees"] if p.get("groupe") == "copie" and p.get("promue"))
    vraies_ps = sorted(p["nom"] for p in _plantees(releve, 1, "vraie") if _promue_survivante(p))
    t_elim = (_plantees(releve, 1, nom="T-ELIM") or [{}])[0]
    t_mal = (_plantees(releve, 1, nom="T-MAL") or [{}])[0]
    p4_ecarts = []
    if not (t_elim.get("promue") and t_elim.get("verdict") == "éliminée"):
        p4_ecarts.append(f"T-ELIM : promue {t_elim.get('promue')}, verdict {t_elim.get('verdict')!r} (attendu : promue puis éliminée)")
    if t_mal.get("gardien") != "refuse":
        p4_ecarts.append(f"T-MAL : gardien {t_mal.get('gardien')!r} (attendu : refusée au gardien)")
    conditions = {
        "C5": bool(arret) or bool(manques),
        "C4": bool(ecarts_p6) or bool(copies_promues),
        "C2": bool(fausses_promues),
        "C3": not vraies_ps,
        "C6": bool(p4_ecarts),
        "C1": bool(vraies_ps) and not fausses_promues and not copies_promues and not p4_ecarts and not ecarts_p6,
    }
    issue = next(c for c in ORDRE if conditions[c])
    partielles = []
    if issue == "C5":
        if ecarts_p6 or copies_promues:
            partielles.append("C4 (partielle)")
        if fausses_promues:
            partielles.append("C2 (partielle)")
    oracle = {}
    try:
        oracle = mesures_oracle(releve, monde) if releve.get("cartes") else {}
    except Exception as e:  # noqa: BLE001 — mesure sans issue : son échec est dit, jamais tu
        oracle = {"erreur": f"{type(e).__name__} : {str(e)[:200]}"}
    fausses_decouvertes = sorted(i for i, f in oracle.items() if isinstance(f, dict) and f.get("fausse_decouverte"))
    audits = {"A1": audit_a1(releve, journal) if issue == "C1" else {"declenche": False},
              "A2": audit_a2(releve, monde, rejeux_a2, fausses_decouvertes) if (fausses_promues or fausses_decouvertes) else {"declenche": False},
              "A3": audit_a3(releve, monde) if issue == "C3" else {"declenche": False},
              "A4": audit_a4(releve) if copies_promues else {"declenche": False}}
    p3 = {n: _promue_survivante((_plantees(releve, 1, nom=n) or [{}])[0]) for n in ("V3", "V4")}
    p7 = {}
    for c in releve["cartes"]:
        x = p7.setdefault(f"generation-{c['generation']}|{c.get('fournisseur')}", {"proposees": 0, "refusees_au_gardien": 0, "promues": 0,
                                                                                   "testees": 0, "survivantes": 0, "retenues": 0,
                                                                                   "vraies_decouvertes": 0, "fausses_decouvertes": 0})
        x["proposees"] += 1
        x["refusees_au_gardien"] += c.get("gardien") == "refuse"
        x["promues"] += bool(c.get("promue"))
        x["testees"] += c.get("verdict") is not None
        x["survivantes"] += c.get("verdict") == "survit"
        x["retenues"] += bool(c.get("retenue"))
        f = oracle.get(c.get("identifiant_servi")) if isinstance(oracle, dict) else None
        if isinstance(f, dict):
            x["vraies_decouvertes"] += bool(f.get("vraie_decouverte"))
            x["fausses_decouvertes"] += bool(f.get("fausse_decouverte"))
    en_tete = [f"fausse découverte d'une carte réelle : {i} (hors du dessin ; audit A2 sur sa forme)" for i in fausses_decouvertes]
    return {"version": VERSION, "issue": issue, "libelle": ISSUES[issue], "partielles": partielles, "en_tete": en_tete,
            "conditions": conditions, "constats": {"arret": arret, "relevé_incomplet": manques, "ecarts_p6": ecarts_p6,
                                                   "fausses_promues": fausses_promues, "copies_promues": copies_promues,
                                                   "vraies_promues_survivantes_g1": vraies_ps, "ecarts_p4": p4_ecarts},
            "audits": audits,
            "mesures": {"P3": p3, "P7": p7, "oracle": oracle, "cout": releve.get("depense"),
                        "recherche_loi_plantee": {"touches": len((releve.get("recherche_loi_plantee") or {}).get("touches") or []),
                                                  "etage_touches_hors_loi_gelee": len(((releve.get("recherche_loi_plantee") or {}).get(
                                                      "etage") or {}).get("touches_hors_loi_gelee") or []),
                                                  "lignes_de_tranche_dans_les_contextes": len((releve.get("recherche_loi_plantee") or {}).get(
                                                      "lignes_de_tranche_dans_les_contextes") or [])}},
            "regle": "ordre gelé C5, C4, C2, C3, C6, C1 ; première ligne qui s'applique ; audits écrits avant toute phrase de résultat"}


def audit_a1(releve, journal=None):
    """A1 « trop beau » (déclenché d'office si C1) : chaque vraie survivante jugée avec les membres d'archive de sa génération,
    testée dans le bac réel (journal de l'étage : `bwrap`, non factice), contre-calcul égal, expérimentateur appelé ; fausses à log W
    maximal ≤ 0 aux arrondis près ; vue de la génération 2 sans loi plantée."""
    constats = []
    attendu = (releve.get("membres_attendus") or {}).get("1")
    etages = [l for l in (journal or []) if l.get("evenement") == "etage-tests-de-mort"]
    bac_reel = bool(etages) and all(l.get("bac_a_sable") == "bwrap" and l.get("factice") is False for l in etages)
    sessions = ((releve.get("sessions") or {}).get("1") or {}).get("plantees") or []
    exp = [s for s in sessions if s.get("role") == "experimentateur_test" and s.get("statut") == "ok"]
    for p in _plantees(releve, 1, "vraie"):
        if _promue_survivante(p):
            constats.append({"loi": p["nom"], "membres_d_archive": p.get("membres_d_archive"), "attendus": attendu,
                             "ok_archive": p.get("membres_d_archive") == attendu, "contre_calcul_ok": p.get("contre_calcul_ok") is True})
    fausses = [{"loi": f"G{p['generation']}-{p['nom']}", "log_w_max": p.get("log_richesse_max"),
                "ok": isinstance(p.get("log_richesse_max"), (int, float)) and p["log_richesse_max"] <= TOLERANCE_LOG_W_FAUSSE}
               for p in releve.get("plantees") or [] if p.get("groupe") == "fausse" and p.get("gardien") == "passe"]
    ids_plantes = {p.get("identifiant") for p in releve.get("plantees") or []} | {p.get("identifiant_servi") for p in releve.get("plantees") or []}
    vue2 = next((v for v in releve.get("vues") or [] if v.get("generation") == 2), {})
    vue_sans_plantee = not (set(vue2.get("lois") or []) & ids_plantes)
    ok = all(c["ok_archive"] and c["contre_calcul_ok"] for c in constats) and bac_reel and bool(exp) and all(f["ok"] for f in fausses) \
        and vue_sans_plantee
    return {"declenche": True, "vraies_survivantes": constats, "bac_reel": bac_reel if journal is not None else "journal non fourni",
            "sessions_experimentateur_ok_g1": len(exp), "fausses_log_w_max": fausses, "vue_g2_sans_loi_plantee": vue_sans_plantee,
            "tout_conforme": ok,
            "reste": "registre des relais apparié appel par appel : hors de ce programme (pièces des relais), à faire par le lecteur"}


def audit_a2(releve, monde, rejeux, fausses_decouvertes=()):
    """A2 « fausse promue » : chaque fausse ou copie promue rejouée `rejeux` fois sur des tirages neufs avec la même archive ; ses
    membres d'archive contre ceux de sa génération ; sa forme. Une fausse jugée sans archive est un défaut de chaîne, non une
    brèche du nul. Fausses découvertes des cartes réelles : forme seule."""
    out = {"declenche": True, "fausses": [], "cartes_reelles": []}
    racine = int(releve["entropie_racine"])
    for p in releve.get("plantees") or []:
        if p.get("groupe") not in ("fausse", "copie") or not p.get("promue"):
            continue
        g = str(p["generation"])
        archive = (releve.get("archives_de_jugement") or {}).get(g) or {}
        attendu = (releve.get("membres_attendus") or {}).get(g)
        k = _rejouer(p["loi"], monde, archive, racine, f"audit-a2|{p['identifiant_servi']}", rejeux) if rejeux else None
        out["fausses"].append({"loi": f"G{g}-{p['nom']}", "rejeux": rejeux, "promue_au_rejeu": k,
                               "membres_d_archive": p.get("membres_d_archive"), "attendus": attendu,
                               "jugee_sans_archive": p.get("membres_d_archive") == 0 and bool(archive),
                               "forme": forme_de_la_loi(p.get("loi"), archive),
                               "lecture": ("défaut de chaîne (jugée sans l'archive)" if p.get("membres_d_archive") != attendu
                                           else "membre du nul promu : défaut numérique à établir")})
    cartes = {c["identifiant_servi"]: c for c in releve.get("cartes") or []}
    for i in fausses_decouvertes:
        c = cartes.get(i, {})
        archive = (releve.get("archives_de_jugement") or {}).get(str(c.get("generation"))) or {}
        out["cartes_reelles"].append({"carte": i, "forme": forme_de_la_loi(c.get("loi"), archive), "fournisseur": c.get("fournisseur")})
    return out


def audit_a3(releve, monde):
    """A3 « sans dents » : pour chaque vraie, non promue / promue non survivante / non concluante ; sessions de l'expérimentateur de
    l'étage des lois plantées ; jugement rejoué hors ligne à la même graine (log W maximal égal ou non)."""
    racine = int(releve["entropie_racine"])
    archive = (releve.get("archives_de_jugement") or {}).get("1") or {}
    sessions = ((releve.get("sessions") or {}).get("1") or {}).get("plantees") or []
    out = {"declenche": True, "vraies": [], "sessions_etage_plantees": sessions}
    tache = f"{B.VERSION}|bras={B.BRAS}|generation=1"
    for p in _plantees(releve, 1, "vraie"):
        if not p.get("promue"):
            cat = "non promue"
        elif p.get("verdict") == "non concluant" or p.get("verdict") is None:
            cat = "promue, non concluante"
        elif p.get("verdict") != "survit":
            cat = "promue non survivante"
        else:
            cat = "promue puis survivante"
        ev, _ = A.juger_carte(p["loi"], monde, archive, racine, f"{tache}|plantee={p['identifiant_servi']}")
        out["vraies"].append({"loi": p["nom"], "categorie": cat, "log_w_max_releve": p.get("log_richesse_max"),
                              "log_w_max_rejoue": round(ev["log_richesse_max"], 6),
                              "rejeu_egal": p.get("log_richesse_max") == round(ev["log_richesse_max"], 6)})
    return out


def audit_a4(releve):
    """A4 « copie promue » : membres d'archive de chaque copie promue contre ceux qu'impose la sélection lue."""
    attendu = (releve.get("membres_attendus") or {}).get("2")
    return {"declenche": True, "copies": [{"copie": p["nom"], "source": p.get("source"), "membres_d_archive": p.get("membres_d_archive"),
                                           "attendus": attendu, "egal": p.get("membres_d_archive") == attendu}
                                          for p in _plantees(releve, 2, "copie") if p.get("promue")]}


__all__ = ("VERSION", "ISSUES", "ORDRE", "LectureImpossible", "lire_boucle", "verifier_lecture_selection", "mesures_oracle",
           "forme_de_la_loi", "audit_a1", "audit_a2", "audit_a3", "audit_a4", "G0")
