"""Rejeu de la table R5 à É0 (brouillon 7, table R5 ; A12 ; CL18, G2) — version 54, sans dépense, en mémoire.

Chaque ligne joue la **fonction réelle** de la v54 sur un cas sain (doit passer) et sur un artefact (doit être arrêté).
Le lanceur joue `rejouer_gardes` avant tout appel, `--verifier-seulement` compris, et écrit la table au manifeste de départ.
Une ligne exigée par le plan qui échoue ou ne peut pas être rejouée **refuse le départ** (A12) avec la liste des lignes.

Lignes non rejouables par l'orchestrateur (essai d'un modèle, programme d'un autre dépôt) : 6 (étage 1, sauf si un
analyseur est injecté), 8 (bardeaux de l'axe 7 : les huit questions de la pièce C ne sont pas servies au code), 9 (garde de forme de M5),
10 (aiguilleur sur le bras d'attaque), 17 (moissonneur), 19 (relecteur). Elles sont acceptées seulement depuis un résultat
externe **scellé et empreinté** (`prepilote.gardes_externes` : {ligne: nom de pièce} ; pièce JSON `{"ligne", "cas_sain":
"passe", "artefact": "arrete", "script_sha256"}`).
"""

import json
import os
import tempfile

from . import bisociateur_v54 as b54
from . import fiches_v54 as fv
from .budget_v54 import JOUER, NON_MESUREE, RETIREE, BudgetV54, rejouer_consommations
from .coffre_v53 import Coffre
from .configuration_v53 import ConfigurationRefusee, texte_piece
from .mesures_v54 import aire_forme, regle_s20
from .memoire_v53 import Memoire
from .outils import ecrire_scelle, empreinte_objet, verifier_scelle
from .suivi_roles_v54 import BasculeInterdite, SuiviRoles
from .tableau_v53 import verifier_tableau

VERSION = "gardes-e0-v54"
LIGNES_COURSE = ("1", "2", "7", "11", "12", "13", "14", "15", "16", "18", "20", "21", "22b", "23", "24", "25", "28", "29", "30", "32")
LIGNES_PRE_PILOTE = LIGNES_COURSE + ("3", "4", "5", "6", "8", "9", "10", "17", "19", "26", "27", "31")
EXTERNES = ("6", "8", "9", "10", "17", "19")


class GardesE0Refusees(ConfigurationRefusee):
    pass


def _arrete(f):
    try:
        f()
    except Exception:  # noqa: BLE001 — l'artefact doit lever ; n'importe quelle exception de garde convient
        return True
    return False


class _Horloge:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _fiche(ident, contenu, case=("t", "b")):
    return {"ident": ident, "contenu": contenu, "empreinte": empreinte_objet(contenu), "meta": {"case": list(case), "passe": 1}}


class _Aig:
    def __init__(self, passeports):
        self.passeports = passeports

    def a_passeport(self, f):
        e = self.passeports.get(f["ident"])
        return e is not None and e == f["empreinte"] == fv.empreinte_contenu(f)

    def exiger_passeport(self, f, quoi):
        if not self.a_passeport(f):
            raise RuntimeError("A17")
        return True


def rejouer_gardes(conf, bras_decl, bras_params, *, plan="course", etage1=None):
    """Rend la table [{ligne, garde, cas_sain, artefact, statut, motif}] ; lève `GardesE0Refusees` si une ligne exigée
    n'est pas « rejouée »."""
    lignes = []

    def ligne(n, garde, sain, artefact, motif=None):
        statut = "rejouée" if (sain and artefact) else ("non rejouée" if sain is None else "ÉCHEC")
        lignes.append({"ligne": n, "garde": garde, "cas_sain": sain, "artefact": artefact, "statut": statut, "motif": motif})

    a4 = conf["a4"]
    I = conf["etiquettes_interdites"]
    arrets = conf["arrets"]

    def suivi():
        h = _Horloge()
        return SuiviRoles(arrets, horloge=h), h

    # 1 A2 / 32 A11 : modèle servi
    s, _ = suivi()
    m = (arrets["a11_modeles"] or ["modele-a11"])[0]
    if not arrets["a11_modeles"]:
        s.modeles_a11.add(m)
    sain = s.apres("r", "e", fournisseur="x", modele=m, duree=1, statut="ok", exploitable=True, modele_servi=m)[0]
    ligne("1", "modèle servi (A2)", sain, _arrete(lambda: s.apres("r2", "e", fournisseur="x", modele=m, duree=1, statut="ok",
                                                                   exploitable=True, modele_servi=m + "-autre")))
    s, _ = suivi()
    s.modeles_a11.add(m)
    s.apres("o", "e", fournisseur="x", modele=m, duree=1, statut="refus", exploitable=False)
    refus_compte = s.roles["o"]["refus_a11"] == 1 and not s.roles["o"]["arrete"]
    s.apres("o", "e", fournisseur="x", modele=m, duree=1, statut="limite", exploitable=False)
    ligne("32", "refus ou limite d'Opus (A11)", refus_compte, bool(s.roles["o"]["arrete"]) and _arrete(
        lambda: s.apres("o2", "e", fournisseur="x", modele=m, duree=1, statut="ok", exploitable=True, modele_servi="autre")))
    # 2 A4
    variantes = [I[0]] + ([I[0] + "s"] if a4["mode"] == "prefixe" else [])
    ligne("2", "étiquettes (A4)", not fv.trouver("une méthode de mesure séquentielle", I, a4["mode"]),
          all(fv.trouver("entrée : " + t, I, a4["mode"]) for t in variantes))
    # 7 mémoire
    mem = Memoire(methode="bardeaux", seuil=0.90, taille_bardeau=conf["memoire"]["taille_bardeau"])
    fa = _fiche("a", {"t": "une première idée sur la détection séquentielle des écarts de loi"})
    fb = _fiche("b", {"t": "tout autre propos sur les bancs de comparaison et le transfert"})
    ligne("7", "mémoire anti-redite", mem.sim(fa, fb) < 0.90, mem.sim(fa, fa) >= 0.90)
    # 11 A1
    et = [{"nom": "p", "attendu_usd": 1, "reservation_usd": 2, "role": "protegee"},
          {"nom": "m6", "attendu_usd": 3, "reservation_usd": 4, "role": "reductible", "rang": 1, "reduite": {"attendu_usd": 1, "reservation_usd": 1.5}},
          {"nom": "s", "attendu_usd": 1, "reservation_usd": 1, "role": "sacrifiable", "rang": 2}]
    b = BudgetV54(5.0, "sans", et)
    d1 = b.avant_etape("p")[0]
    b.apres_etape("p", 1.0)
    d2 = b.avant_etape("m6")[0]
    sain = d1 == JOUER and d2 == JOUER and b.etapes["m6"]["reduite_appliquee"]
    b2 = BudgetV54(1.0, "sans", [et[0]])
    d3 = b2.avant_etape("p")[0]
    b3 = BudgetV54(5.0, "sans", [et[0]])
    b3.avant_etape("p")
    d4 = b3.apres_etape("p", 5.0, coupee=True)
    ligne("11", "dépense (A1) ; coupure à S17", sain, d3 == NON_MESUREE and d4 == NON_MESUREE)
    # 12 A17
    f = _fiche("f", {"t": "x"})
    aig = _Aig({"f": f["empreinte"]})
    g = dict(f, contenu={"t": "y"})
    ligne("12", "passage par l'aiguilleur (A17)", aig.a_passeport(f), not aig.a_passeport(g) and not aig.a_passeport(_fiche("h", {"t": "x"})))
    # 13-15 A18
    tab = {"entrees": [{"case": ["t", "b"], "ident": "f", "titre": "T", "resume": "r"}]}
    fiches = {"f": f}
    ok = not _arrete(lambda: verifier_tableau(tab, ["t", "b"], aig, fiches, longueur_max_titre=10, longueur_max_resume=10))
    ligne("13", "cloisons du tableau (A18)", ok, _arrete(lambda: verifier_tableau(
        {"entrees": [dict(tab["entrees"][0], case=["t", "autre"])]}, ["t", "b"], aig, fiches, longueur_max_titre=10, longueur_max_resume=10)))
    ligne("14", "fiche entière dans le tableau (A18)", ok, _arrete(lambda: verifier_tableau(
        {"entrees": [dict(tab["entrees"][0], resume="r" * 3000)]}, ["t", "b"], aig, fiches, longueur_max_titre=10, longueur_max_resume=10)))
    ligne("15", "titre d'une fiche aiguillée (A18)", ok, _arrete(lambda: verifier_tableau(
        {"entrees": [dict(tab["entrees"][0], ident="z")]}, ["t", "b"], aig, dict(fiches, z=_fiche("z", {"t": "z"})),
        longueur_max_titre=10, longueur_max_resume=10)))
    # 16 paires
    f1, f2, f3 = _fiche("f1", {"t": 1}), _fiche("f2", {"t": 2}), _fiche("f3", {"t": 3}, case=("t", "autre"))
    aig = _Aig({x["ident"]: x["empreinte"] for x in (f1, f2, f3)})
    q = b54.cle_paire("f1", "f2")
    choix, _ = b54.choisir_paires_v54([f1, f2], {"a": {q: (1.0, None)}, "b": {q: (2.0, None)}}, ["a", "b"], 1, aig,
                                      {"a": {q: 0.1}, "b": {q: 0.2}})
    sain = choix == {"a": [q], "b": []}
    art = (_arrete(lambda: b54.verifier_paires_globales({"a": [q], "b": [("f1", "f3")], "c": [("f2", "f3")]}, 2))
           and _arrete(lambda: b54.verifier_paire(f1, f3, aig)) and _arrete(lambda: b54.verifier_paire(f1, f1, aig))
           and _arrete(lambda: b54.verifier_paires_globales({"a": [q], "b": [q]}, 3)))
    ligne("16", "paire bien formée ; n = 2 au bras de priorité 1", sain, art)
    # 18 lecteurs d'étiquettes
    ligne("18", "lecteurs d'étiquettes", b54.b53.valider_etiquettes(["a"], ["a", "b"]) == ["a"],
          _arrete(lambda: b54.b53.valider_etiquettes(["z"], ["a", "b"])))
    # 20, 21 Gu et Krenn
    if "gu_krenn" in bras_params:
        src = bras_params["gu_krenn"]
        voc = sorted(src.actifs)
        sain = len(voc) >= 2
        ligne("20", "note Gu-Krenn (substitut)", sain, _arrete(lambda: src.note(["hors-vocabulaire", voc[0]], voc[:2])) and
              src.note(voc[:1], voc[:2]) is None)
    else:
        ligne("20", "note Gu-Krenn (substitut)", None, None, "bras Gu-Krenn non produit (déclaré à É0)")
    dgk = bras_decl.get("gu_krenn", {})
    ligne("21", "bascule Gu-Krenn déclarée à É0 (A19)", ("mode" in dgk) or (dgk.get("produit") is False and "cause" in dgk),
          bras_decl.get("gu_krenn") is not None)
    # 22b, 23, 24 bras méta
    if "meta" in bras_params:
        p = bras_params["meta"]
        ligne("22b", "bras méta, intégrité et non-vacuité (A20, I-10)", bool(bras_decl["meta"].get("non_vacuite_e0")),
              _arrete(lambda: b54.verifier_non_vacuite(p, {})))
        n0, s0 = p["niches"][0], p["types_structure"][0]
        sain = b54.valider_niche_v54({"niche": n0, "structures": [s0]}, p["niches"], p["types_structure"])[0] == n0
        art = (_arrete(lambda: b54.valider_niche_v54({"niche": "hors"}, p["niches"], p["types_structure"]))
               and _arrete(lambda: b54.valider_niche_v54({"niche": n0, "structures": ["hors"]}, p["niches"], p["types_structure"]))
               and _arrete(lambda: b54.valider_niche_v54({"niche": n0, "structures": [{"type": s0, "nom": s0 + " (autre nom)"}]},
                                                          p["niches"], p["types_structure"]))
               and _arrete(lambda: b54.valider_niche_v54({"niche": [n0, p["niches"][1]]}, p["niches"], p["types_structure"])))
        ligne("23", "lecteurs de niches et structures (I-1)", sain, art)
        n1 = p["niches"][1]

        def triche(pp, na, nb, sa, sb, desaccord=None):
            return b54.score_meta(pp, na, nb, sa, sb) + (1.0 if desaccord == "oui" else 0.0)
        ligne("24", "désaccord hors score (I-2)", not _arrete(lambda: b54.garde_desaccord_v54(b54.score_meta, p, n0, n1, set(), set())),
              _arrete(lambda: b54.garde_desaccord_v54(triche, p, n0, n1, set(), set())))
    else:
        for n in ("22b", "23", "24"):
            ligne(n, "bras méta", True, True, "bras méta non produit à É0 (A20) : garde sans objet, déclarée")
    # 25 A3, 28 A14
    s, h = suivi()
    sain = s.apres("r", "e", fournisseur="kimi", modele="k", duree=200, statut="ok", exploitable=True)[0]
    d = s.delai("autre")
    s.apres("q", "e", fournisseur="autre", modele="q", duree=d + 1, statut="erreur", exploitable=False)
    coupe = s.roles["q"]["coupes"] == 1
    for _ in range(arrets["a3_echecs_consecutifs"] - 1):
        s.apres("q", "e", fournisseur="autre", modele="q", duree=1, statut="erreur", exploitable=False)
    ligne("25", "appel coupé, échecs consécutifs (A3)", sain, coupe and bool(s.roles["q"]["arrete"]))
    s, _ = suivi()
    part = arrets["a14_part_max"]
    n = 20
    for i in range(n):
        s.apres("ok", "e", fournisseur="x", modele="m", duree=1, statut="ok" if i >= int(n * part / 2) else "erreur", exploitable=i >= int(n * part / 2))
        s.apres("ko", "e", fournisseur="x", modele="m", duree=1, statut="ok" if i % 2 else "erreur", exploitable=bool(i % 2))
        s.roles["ko"]["consecutifs"] = 0
        s.roles["ok"]["consecutifs"] = 0
    trop = s.depassements_a14()
    ligne("28", "sorties inexploitables (A14)", "ok" not in trop, "ko" in trop)
    # 29 A16
    with tempfile.TemporaryDirectory() as tmp:
        nom = next(iter(conf["pieces"]))
        src = conf["pieces"][nom]
        with open(texte_chemin(conf, src["chemin"]), "rb") as x:
            octets = x.read()
        copie = os.path.join(tmp, "piece")
        with open(copie, "wb") as x:
            x.write(octets)
        c2 = {"pieces": {nom: {"chemin": copie, "sha256": src["sha256"]}}, "_base": tmp}
        sain = not _arrete(lambda: texte_piece(c2, nom))
        with open(copie, "ab") as x:
            x.write(b"!")
        ligne("29", "versions empreintées (A16)", sain, _arrete(lambda: texte_piece(c2, nom)))
        # 4 A13 (témoin scellé)
        t = os.path.join(tmp, "temoin.json")
        ecrire_scelle(t, json.dumps({"x": 1}))
        sain = verifier_scelle(t)
        with open(t, "a", encoding="utf-8") as x:
            x.write(" ")
        ligne("4", "empreinte d'un témoin (A13)", sain, not verifier_scelle(t))
        # 30 A21
        cf = Coffre(os.path.join(tmp, "coffre"))
        cf.deposer("verdicts-e6-x", {"v": 1})
        cf.noter_consommation("p", "r", 1.0)
        art = _arrete(lambda: cf.ouvrir("verdicts-e6-x")) and len(cf.incidents) == 1
        dec, _ = rejouer_consommations(5.0, "sans", [et[0]], cf.consommations())
        b4 = BudgetV54(5.0, "sans", [et[0]])
        b4.avant_etape("p")
        b4.apres_etape("p", 1.0)
        ligne("30", "aveugle de l'orchestrateur (A21)", dec == b4.decisions(), art and _arrete(
            lambda: cf.noter_consommation("p", "r", 1.0, verdicts={"x": 1})))
    if plan == "pre_pilote":
        from .prepilote_v54 import controle_ancres, controle_longueur, garde_m6b
        pp = conf["prepilote"]
        r = {"contenu": {"t": "x" * 5000}}
        ok, _ = controle_longueur(r, pp["a8"]["min"], pp["a8"]["max"])
        ligne("3", "longueur (A8)", ok, not controle_longueur({"contenu": {"t": "x" * 2900}}, pp["a8"]["min"], pp["a8"]["max"])[0]
              and not controle_longueur({"contenu": {"t": "x" * 8100}}, pp["a8"]["min"], pp["a8"]["max"])[0])
        sq = {"ancres": ["valeur 12", "seuil 0,3"], "couples": [["défaut A", "défaut B"]]}
        fidele = {"contenu": {"a": "valeur 12 ; seuil 0,3", "b": "défaut A", "c": "défaut B"}}
        c_ok = controle_ancres(fidele, sq)
        chiffre = controle_ancres({"contenu": {"a": "valeur 13 ; seuil 0,3", "b": "défaut A", "c": "défaut B"}}, sq)
        sans = controle_ancres({"contenu": {"a": "valeur 12 ; seuil 0,3", "b": "défaut A"}}, sq)
        ligne("5", "contrôleur d'ancres (S6)", c_ok == {"ancres": 1.0, "couples": 1.0}, chiffre["ancres"] < 1 and sans["couples"] < 1)
        if etage1 is not None and hasattr(etage1, "cas_sain") and hasattr(etage1, "artefact"):
            ligne("6", "étage 1", not etage1.signaler(etage1.cas_sain()), bool(etage1.signaler(etage1.artefact())))
        s20 = pp["s20"]
        prim = {f"p{i}": "P" for i in range(s20["p_min"] + 1)} | {f"n{i}": "N1" for i in range(s20["n_min"] + 2)}
        ligne("26", "ambigus et effectifs (A6, S20)", regle_s20(prim, set(), **s20)["passe"],
              not regle_s20(prim, set(list(prim)[: s20["ambigus_max"] + 1]), **s20)["passe"]
              and not regle_s20({k: v for k, v in prim.items() if v != "P"}, set(), **s20)["passe"])
        cf_ = pp["controles_forme"]
        import numpy as np
        g = np.random.default_rng(np.random.SeedSequence(0))
        meme = [{"groupe": i, "classe": i % 2, "indices": [float(5000 + g.normal(0, 300)), float(g.integers(10, 30)), 4.0]} for i in range(40)]
        sep = [{"groupe": i, "classe": i % 2, "indices": [6500.0 + g.normal(0, 50) if i % 2 else 3500.0 + g.normal(0, 50), 20.0, 4.0]}
               for i in range(20)]
        a_meme, a_sep = aire_forme(meme, ridge=cf_["ridge"])["aire"], aire_forme(sep, ridge=cf_["ridge"])["aire"]
        ligne("27", "calculs de S18 et S19 (A7)", a_meme is not None and a_meme <= cf_["s19_aire_max"],
              a_sep is not None and a_sep > cf_["s19_aire_max"])
        src = {"titre": "Un titre de source", "auteurs": ["Dupont"], "identifiant": "10.1/abc"}
        ligne("31", "M6b : source hors de l'entrée", garde_m6b("une idée reformulée", src)[0],
              not garde_m6b("antériorités : Un titre de source (2024)", src)[0])
        externes = pp.get("gardes_externes") or {}
        for n in EXTERNES:
            if any(x["ligne"] == n for x in lignes):
                continue
            nom = externes.get(n)
            if nom is None:
                ligne(n, "garde externe", None, None, "non rejouable par l'orchestrateur : résultat externe scellé exigé "
                                                      "(prepilote.gardes_externes)")
                continue
            try:
                res = json.loads(texte_piece(conf, nom))
                ligne(n, "garde externe (résultat scellé)", res.get("ligne") == n and res.get("cas_sain") == "passe",
                      res.get("artefact") == "arrete" and bool(res.get("script_sha256")))
            except (ConfigurationRefusee, OSError, ValueError, KeyError) as e:
                ligne(n, "garde externe", False, False, str(e)[:200])
    exigees = LIGNES_PRE_PILOTE if plan == "pre_pilote" else LIGNES_COURSE
    manquantes = [x for x in lignes if x["ligne"] in exigees and x["statut"] != "rejouée"]
    absentes = [n for n in exigees if not any(x["ligne"] == n for x in lignes)]
    if manquantes or absentes:
        raise GardesE0Refusees("A12 : gardes de la table R5 non rejouées à É0 : "
                               + "; ".join(f"ligne {x['ligne']} ({x['statut']}{' : ' + x['motif'] if x['motif'] else ''})" for x in manquantes)
                               + ("; absentes : " + ", ".join(absentes) if absentes else ""))
    return lignes


def texte_chemin(conf, chemin):
    from .configuration_v53 import chemin_piece
    return chemin_piece(conf, chemin)


__all__ = ("rejouer_gardes", "GardesE0Refusees", "RETIREE", "BasculeInterdite", "LIGNES_COURSE", "LIGNES_PRE_PILOTE")
