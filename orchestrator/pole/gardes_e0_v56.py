"""Rejeu de la table R5 à É0, version 56 — reprend `gardes_e0_v55` (inchangé, R12) et remplace ou étend quatre lignes :

- **Ligne 1 (CL20-01)** : en plus des cas v55, le **vrai** adaptateur de commande externe v56 (`AdaptateurCommandeExterneV56`)
  est lancé sur une commande factice locale (interpréteur courant, `-I`, aucun réseau, aucune clé) : cas sain — la ligne
  rend `modele_servi` égal au modèle demandé, le résultat « ok » le porte et `controle_a2` passe ; artefacts — l'adaptateur
  v55 (`AdaptateurCommandeExterne`) qui perd le modèle servi est vu par A2 ; une ligne sans `modele_servi` reste sans modèle
  servi (A2) ; un modèle servi différent est un refus.
- **Lignes 11a et 11b (CL20-02, brouillon 10)** à la place de la ligne 11 « réservation » : 11a — plafond dur fixé au
  lancement, recalculé au centime par le second programme et par la formule indépendante, accusé par la porte ; artefacts :
  plafond transmis faux d'un centime, plafond changé pendant l'étape, cumul au-delà de S17, relais réel sans porte (A15) ;
  11b — statuts d'une étape coupée par son relais (protégée → « non mesuré (budget) » ; sacrifiable → retirée ; M6 entière
  → lue réduite si sa réduction a été vérifiée, sinon « non mesuré » ; M6 réduite → « non mesuré » ; M6b → réserve) ; cas
  sain : coût au-delà du plafond de relais sous le plafond dur (souplesse) = étape jouée.
- **Ligne 29 (CL20-03)** : si une spécification est nommée, cas sain = préenregistrement et contre-lecture scellés, conformes ;
  artefacts = un octet changé (copie), sceau absent (copie), marqueur « À REMPLIR » restant.
- **Ligne 5 (CL20-13, pré-pilote)** : en plus de la v55, la numérotation de liste n'est pas un nombre ajouté (cas sain) et un
  nombre ajouté hors numérotation reste compté (artefact).
"""

import copy
import os
import shutil
import tempfile

from . import gardes_e0_v55 as g55
from .adaptateurs import AdaptateurCommandeExterne
from .adaptateurs_v56 import AdaptateurCommandeExterneV56, PortePlafondNoyau, RelaisSansPlafond
from .budget_v56 import (JOUER, NON_MESUREE, NON_MESUREE_HORS_PORTE, RETIREE, BudgetV56, CumulAuDelaDeS17, PlafondDeRelaisFaux,
                         plafond_independant, rejouer_consommations_v56, verifier_cumul, verifier_plafonds_transmis)
from .gardes_e0_v54 import GardesE0Refusees
from .noyau_v55 import ModeleServiAbsent, controle_a2
from .outils import ecrire_scelle

VERSION = "gardes-e0-v56"
REJOUEE, SANS_OBJET, STATUTS_SATISFAITS = g55.REJOUEE, g55.SANS_OBJET, g55.STATUTS_SATISFAITS
LIGNES_COURSE = tuple(x for x in g55.LIGNES_COURSE if x != "11") + ("11a", "11b")
LIGNES_PRE_PILOTE = tuple(x for x in g55.LIGNES_PRE_PILOTE if x != "11") + ("11a", "11b")
_arrete = g55._arrete


def _commande(dossier, nom, objet):
    import sys
    chemin = os.path.join(dossier, nom + ".py")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("import json, sys\nsys.stdin.read()\nprint(json.dumps(" + repr(objet) + "))\n")
    return [sys.executable, "-I", "-B", chemin]


def ligne_1_adaptateur_reel(modele="modele-essai-a2"):
    """(sain, artefact) de la ligne 1 sur le vrai adaptateur de commande externe (CL20-01)."""
    with tempfile.TemporaryDirectory() as tmp:
        ok = _commande(tmp, "ok", {"texte": "réponse", "cout_usd": 0.01, "modele_servi": modele})
        sans = _commande(tmp, "sans", {"texte": "réponse", "cout_usd": 0.01})
        autre = _commande(tmp, "autre", {"texte": "réponse", "cout_usd": 0.01, "modele_servi": modele + "-autre"})
        env = {"PATH": os.defpath}
        lancer = lambda ad: ad.lancer("juge_ideation", "consigne", tmp, 1.0, 1, modele=modele)  # noqa: E731
        r = lancer(AdaptateurCommandeExterneV56(ok, environnement=env, delai_s=60, exiger_modele_servi=True))
        sain = r.statut == "ok" and r.modele_servi == modele and controle_a2(r.statut, r.modele_servi, modele)
        r55 = lancer(AdaptateurCommandeExterne(ok, environnement=env, delai_s=60, exiger_modele_servi=True))
        r_sans = lancer(AdaptateurCommandeExterneV56(sans, environnement=env, delai_s=60))
        r_autre = lancer(AdaptateurCommandeExterneV56(autre, environnement=env, delai_s=60))
        art = (r55.statut == "ok" and r55.modele_servi is None
               and _arrete(lambda: controle_a2(r55.statut, r55.modele_servi, modele), ModeleServiAbsent)
               and r_sans.statut == "ok" and r_sans.modele_servi is None
               and _arrete(lambda: controle_a2(r_sans.statut, r_sans.modele_servi, modele), ModeleServiAbsent)
               and r_autre.statut == "refus")
        return bool(sain), bool(art)


PLAN_11 = [{"nom": "p", "attendu_usd": 1.0, "plafond_relais_usd": 2.0, "role": "protegee"},
           {"nom": "s", "attendu_usd": 1.0, "plafond_relais_usd": 1.5, "role": "sacrifiable", "rang": 1},
           {"nom": "m6", "attendu_usd": 2.0, "plafond_relais_usd": 3.0, "role": "reductible", "rang": 2,
            "reduite": {"attendu_usd": 0.5, "plafond_relais_usd": 1.0}},
           {"nom": "m6b", "attendu_usd": 0.5, "plafond_relais_usd": 1.0, "role": "protegee_hors_porte"}]


def ligne_11a():
    b = BudgetV56(10.0, "sans", copy.deepcopy(PLAN_11))
    cons, transmis = [], []
    for nom, cout in (("p", 1.2), ("s", 0.9), ("m6", 2.5), ("m6b", 0.4)):
        d, detail = b.avant_etape(nom)
        if d != JOUER:
            return False, False
        _, _, plafonds = rejouer_consommations_v56(10.0, "sans", PLAN_11, cons, jusqu_a=nom)
        p2, souple = plafond_independant(PLAN_11, 10.0, b.journal, cons, nom)
        if plafonds.get(nom) != detail["plafond_dur_usd"] or p2 != detail["plafond_dur_usd"] or souple != detail["souple"]:
            return False, False
        transmis.append({"etape": nom, "plafond_usd": PortePlafondNoyau().transmettre(nom, detail["plafond_dur_usd"])["plafond_usd"]})
        b.apres_etape(nom, cout)
        cons.append({"etape": nom, "cout_usd": cout})
    attendus = b.etat()["plafonds_durs_usd"]
    sain = (verifier_plafonds_transmis(transmis, attendus) == 4 and verifier_cumul(cons, 10.0) == 5.0
            and attendus["p"] == 10.0 - 1.0 - 2.0 - 0.5 and attendus["s"] == 1.5)  # protégée souple ; sacrifiable fixe
    faux = [dict(t, plafond_usd=t["plafond_usd"] - 0.01) if t["etape"] == "p" else t for t in transmis]
    change = transmis + [{"etape": "p", "plafond_usd": 2.0}]
    art = (_arrete(lambda: verifier_plafonds_transmis(faux, attendus), PlafondDeRelaisFaux, "différent")
           and _arrete(lambda: verifier_plafonds_transmis(change, attendus), PlafondDeRelaisFaux, "changé")
           and _arrete(lambda: verifier_cumul(cons + [{"etape": "x", "cout_usd": 5.01}], 10.0), CumulAuDelaDeS17)
           and _arrete(lambda: _porte_absente(), RelaisSansPlafond, "A15"))
    return bool(sain), bool(art)


def _porte_absente():
    from .noyau_v56 import OrchestreV56
    OrchestreV56._portes({}, {"argon": AdaptateurCommandeExterneV56(["/bin/true"], environnement={"PATH": os.defpath})})


def ligne_11b():
    def coupee(nom, cout=0.5, avant=(), **kw):
        b = BudgetV56(10.0, "sans", copy.deepcopy(PLAN_11))
        for n in avant:
            b.avant_etape(n)
            b.apres_etape(n, 0.1)
        b.avant_etape(nom)
        return b.apres_etape(nom, cout, coupee=True, **kw), b
    b = BudgetV56(10.0, "sans", copy.deepcopy(PLAN_11))
    b.avant_etape("p")
    souple = b.apres_etape("p", 3.5) == "jouee" and b.journal[-1]["au_dela_du_plafond_de_relais"]
    lue, b_lue = coupee("m6", avant=("p", "s"), lue_reduite=True)
    m6_reduite = BudgetV56(4.0, "sans", copy.deepcopy(PLAN_11))
    m6_reduite.avant_etape("p")
    m6_reduite.apres_etape("p", 0.1)
    m6_reduite.avant_etape("s")
    d, _ = m6_reduite.avant_etape("m6")
    r_reduite = m6_reduite.apres_etape("m6", 0.5, coupee=True) if d == JOUER and m6_reduite.etapes["m6"]["reduite_appliquee"] else None
    art = (coupee("p")[0] == NON_MESUREE and coupee("s", avant=("p",))[0] == RETIREE
           and lue == "jouee" and b_lue.etapes["m6"]["reduite_appliquee"]
           and coupee("m6", avant=("p", "s"), lue_reduite=False)[0] == NON_MESUREE
           and coupee("m6", avant=("p", "s"))[0] == NON_MESUREE
           and r_reduite == NON_MESUREE
           and coupee("m6b", avant=("p", "s", "m6"))[0] == NON_MESUREE_HORS_PORTE)
    return bool(souple), bool(art)


def ligne_29_specification(conf, spec):
    """(sain, artefact) sur la spécification nommée (CL20-03) ; None si la configuration n'en nomme aucune."""
    from .configuration_v53 import chemin_piece
    from .configuration_v56 import verifier_specification_v56
    if conf.get("specification") is None:
        return None
    sain = bool(spec and spec.get("conforme") is True)
    src = chemin_piece(conf, conf["specification"]["preenregistrement"]["chemin"])
    with tempfile.TemporaryDirectory() as tmp:
        def variante(nom, octets_en_plus=b"", sceller=True, texte_en_plus=b""):
            d = os.path.join(tmp, nom)
            os.makedirs(d)
            p = os.path.join(d, os.path.basename(src))
            with open(src, "rb") as f:
                contenu = f.read()
            if sceller:
                ecrire_scelle(p, contenu + texte_en_plus)
                if octets_en_plus:
                    with open(p, "ab") as f:
                        f.write(octets_en_plus)
            else:
                shutil.copyfile(src, p)
            c = copy.deepcopy(conf)
            from .outils import sha256_fichier
            c["specification"]["preenregistrement"] = {"chemin": p, "sha256": sha256_fichier(p) if not octets_en_plus
                                                       else conf["specification"]["preenregistrement"]["sha256"]}
            return verifier_specification_v56(c)
        art = (variante("octet", octets_en_plus=b"!")["conforme"] is False
               and variante("sans-sceau", sceller=False)["conforme"] is False
               and variante("marqueur", texte_en_plus="\nSeuil : À REMPLIR\n".encode("utf-8"))["conforme"] is False)
    return sain, bool(art)


def rejouer_gardes_v56(conf, bras_decl, bras_params, *, plan="course", etage1=None, specification=None):
    """Table R5 v55 rejouée, lignes 1, 5, 11 (→ 11a, 11b) et 29 remplacées comme dit en tête ; refus A12 sur les lignes v56."""
    try:
        lignes = g55.rejouer_gardes_v55(conf, bras_decl, bras_params, plan=plan, etage1=etage1)
    except GardesE0Refusees:
        raise
    par = {x["ligne"]: x for x in lignes}

    def remplacer(n, garde, sain, art, motif=None):
        statut = REJOUEE if (sain and art) else ("non rejouée" if sain is None else "ÉCHEC")
        x = {"ligne": n, "garde": garde, "cas_sain": sain, "artefact": art, "statut": statut, "motif": motif}
        if n in par:
            lignes[lignes.index(par[n])] = x
        else:
            lignes.append(x)
        par[n] = x
    s1, a1 = ligne_1_adaptateur_reel()
    remplacer("1", "modèle servi (A2) ; modèle servi absent ; vrai adaptateur de commande externe (CL20-01)",
              bool(par["1"]["cas_sain"]) and s1, bool(par["1"]["artefact"]) and a1)
    lignes.remove(par.pop("11"))
    remplacer("11a", "plafond dur de relais fixé au lancement, recalculé, transmis (A1, A15, brouillon 10)", *ligne_11a())
    remplacer("11b", "statuts d'une étape coupée par son relais (A1, point 4)", *ligne_11b())
    l29 = ligne_29_specification(conf, specification)
    if l29 is not None:
        remplacer("29", "versions empreintées (A16) ; spécification scellée (CL20-03)", bool(par["29"]["cas_sain"]) and l29[0],
                  bool(par["29"]["artefact"]) and l29[1], None if l29[0] else (specification or {}).get("motif"))
    if plan == "pre_pilote":
        from .prepilote_v56 import controle_ancres_v56
        sq = {"ancres": ["valeur 12", "seuil 0,3"], "couples": [["défaut A", "défaut B"]]}
        num = controle_ancres_v56({"contenu": {"a": "1. valeur 12\n2. seuil 0,3", "b": "défaut A", "c": "défaut B"}}, sq)
        ajout = controle_ancres_v56({"contenu": {"a": "1. valeur 12 ; seuil 0,3 ; 7 cas", "b": "défaut A", "c": "défaut B"}}, sq)
        remplacer("5", "contrôleur d'ancres (S6) ; numérotation de liste comptée à part (CL20-13)",
                  bool(par["5"]["cas_sain"]) and num["nombres_ajoutes"] == 0 and num["numerotation"] == 2,
                  bool(par["5"]["artefact"]) and ajout["nombres_ajoutes"] == 1)
    exigees = LIGNES_PRE_PILOTE if plan == "pre_pilote" else LIGNES_COURSE
    manquantes = [x for x in lignes if x["ligne"] in exigees and x["statut"] not in STATUTS_SATISFAITS]
    absentes = [n for n in exigees if n not in par]
    if manquantes or absentes:
        raise GardesE0Refusees("A12 : gardes de la table R5 non rejouées à É0 : "
                               + "; ".join(f"ligne {x['ligne']} ({x['statut']}{' : ' + x['motif'] if x['motif'] else ''})" for x in manquantes)
                               + ("; absentes : " + ", ".join(absentes) if absentes else ""))
    return lignes


__all__ = ("rejouer_gardes_v56", "GardesE0Refusees", "LIGNES_COURSE", "LIGNES_PRE_PILOTE", "ligne_1_adaptateur_reel", "ligne_11a",
           "ligne_11b", "ligne_29_specification", "STATUTS_SATISFAITS", "REJOUEE", "SANS_OBJET")
