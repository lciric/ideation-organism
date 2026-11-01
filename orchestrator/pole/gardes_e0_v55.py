"""Rejeu de la table R5 à É0, version 55 — reprend `gardes_e0_v54` (inchangé, R12) ligne à ligne, avec :

- **CL19-01** : ligne 20 « sans objet (déclarée) » quand le bras Gu-Krenn est « non produit (source absente) » à É0 (A19 :
  déclaré, compté C12, O15 ; ni nœud ni arrêt) — comme 22b, 23, 24 quand le bras méta est non produit (A20). Quand la
  source est là, l'artefact « source à empreinte différente » est rejoué sur la vraie source.
- **CL19-08** : `_arrete(f, types, motif)` exige le **type** d'exception attendu (et, s'il est donné, le motif) : une
  exception quelconque (`KeyError`, `TypeError`…) ne compte plus comme « arrêtée ». Ligne 21 : artefacts réels (déclaration
  absente à É0 ; changée après É0) sur `course2_v55.verifier_bascule_gk`. Ligne 22b : artefacts réels sur la lecture de
  l'annexe (annexe absente ; non contre-lue ; à empreinte différente), en plus de la non-vacuité.
- **CL19-07** : ligne 5 : artefacts « 12 → 13 », « 12 → 123 », « 0,3 → 0,35 », couple incomplet, nombre ajouté.
- **CL19-06** : lignes externes (6, 8, 9, 10, 17, 19) : la pièce de résultat doit être **scellée** (compagnon `.sha256`) et
  à son empreinte ; elle cite son identifiant (égal à celui déclaré dans `prepilote.gardes_externes`), la ligne, et le script
  qui l'a produite par **nom de pièce et empreinte**, recalculée ; ligne 6 : l'empreinte de l'analyseur injecté, si l'analyseur
  en porte une (`sha256`), doit être celle citée.
- **CL19-10** : ligne 1 : artefact « modèle servi absent » (`noyau_v55.controle_a2`).
- **CL19-03** : ligne 30 : lecture par programme non déclarée → incident ; déclarée → journalisée avec sa sortie (comptes
  seulement) ; une sortie qui porte des identifiants est refusée.
"""

import copy
import json
import os
import re
import tempfile

from . import bisociateur_v54 as b54
from . import bisociateur_v55 as b55
from . import fiches_v54 as fv
from .bisociateur_v54 import BisociationRefusee
from .budget_v54 import JOUER, NON_MESUREE, BudgetV54, rejouer_consommations
from .coffre_v53 import LectureAvantFinE9
from .coffre_v55 import CoffreV55, SortieDeGardeRefusee
from .configuration_v53 import ConfigurationRefusee, chemin_piece, texte_piece
from .course2_v55 import CAUSE_SOURCE_ABSENTE, BasculeGuKrennInterdite, _piece_annexe, verifier_bascule_gk
from .gardes_e0_v54 import EXTERNES, LIGNES_COURSE, LIGNES_PRE_PILOTE, GardesE0Refusees, _Aig, _fiche, _Horloge
from .memoire_v53 import Memoire
from .mesures_v54 import aire_forme, regle_s20
from .noyau_v55 import ModeleServiAbsent, controle_a2
from .outils import ecrire_scelle, verifier_scelle
from .suivi_roles_v54 import BasculeInterdite, SuiviRoles
from .tableau_v53 import TableauRefuse, verifier_tableau

VERSION = "gardes-e0-v55"
REJOUEE, SANS_OBJET = "rejouée", "sans objet (déclarée)"
STATUTS_SATISFAITS = (REJOUEE, SANS_OBJET)


def _arrete(f, types, motif=None):
    """Vrai si `f()` lève une exception du type attendu (et dont le texte contient `motif`, expression régulière)."""
    try:
        f()
    except types as e:
        return motif is None or re.search(motif, str(e)) is not None
    except Exception:  # noqa: BLE001 — autre exception : la garde n'a pas arrêté pour sa raison
        return False
    return False


def _annexe_modifiee(tmp, chemin, **remplacements):
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    m = next(x for x in re.finditer(r"```json\s*(\{.*?\})\s*```", texte, re.S) if "parametres_bras_meta" in x.group(1))
    bloc = json.loads(m.group(1))
    bloc["parametres_bras_meta"].update(remplacements)
    texte = texte[:m.start(1)] + json.dumps(bloc, ensure_ascii=False) + texte[m.end(1):]
    copie = os.path.join(tmp, "annexe-artefact.md")
    ecrire_scelle(copie, texte)
    from .outils import sha256_fichier
    return copie, sha256_fichier(copie)


def verifier_resultat_externe(conf, n, declaration, etage1=None):
    """Lignes externes (CL19-06). Rend (sain, artefact, motif)."""
    if not isinstance(declaration, dict) or not declaration.get("piece") or not declaration.get("identifiant"):
        return False, False, "déclaration {piece, identifiant} exigée dans prepilote.gardes_externes"
    nom = declaration["piece"]
    if nom not in conf["pieces"]:
        return False, False, f"pièce {nom!r} absente de « pieces »"
    if not verifier_scelle(chemin_piece(conf, conf["pieces"][nom]["chemin"])):
        return False, False, "résultat externe non scellé (compagnon .sha256 absent ou faux)"
    res = json.loads(texte_piece(conf, nom))
    if res.get("ligne") != n or res.get("identifiant") != declaration["identifiant"]:
        return False, False, "ligne ou identifiant du résultat différents de ceux déclarés"
    script = res.get("script")
    if not isinstance(script, str) or script not in conf["pieces"] or conf["pieces"][script]["sha256"] != res.get("script_sha256"):
        return False, False, "script du résultat : pièce empreintée citée par nom et empreinte exigée"
    texte_piece(conf, script)  # empreinte recalculée (A16)
    if n == "6" and getattr(etage1, "sha256", None) is not None and res.get("analyseur_sha256") != etage1.sha256:
        return False, False, "ligne 6 : le résultat ne cite pas l'empreinte de l'analyseur injecté"
    return res.get("cas_sain") == "passe", res.get("artefact") == "arrete", None


def rejouer_gardes_v55(conf, bras_decl, bras_params, *, plan="course", etage1=None):
    lignes = []

    def ligne(n, garde, sain, artefact, motif=None, statut=None):
        if statut is None:
            statut = REJOUEE if (sain and artefact) else ("non rejouée" if sain is None else "ÉCHEC")
        lignes.append({"ligne": n, "garde": garde, "cas_sain": sain, "artefact": artefact, "statut": statut, "motif": motif})

    a4, I, arrets = conf["a4"], conf["etiquettes_interdites"], conf["arrets"]
    bras_conf = conf["bisociateur"]["bras"]

    def suivi():
        h = _Horloge()
        return SuiviRoles(arrets, horloge=h), h

    # 1 A2 / 32 A11
    s, _ = suivi()
    m = (arrets["a11_modeles"] or ["modele-a11"])[0]
    if not arrets["a11_modeles"]:
        s.modeles_a11.add(m)
    sain = s.apres("r", "e", fournisseur="x", modele=m, duree=1, statut="ok", exploitable=True, modele_servi=m)[0] and controle_a2("ok", m, m)
    ligne("1", "modèle servi (A2) ; modèle servi absent", sain,
          _arrete(lambda: s.apres("r2", "e", fournisseur="x", modele=m, duree=1, statut="ok", exploitable=True, modele_servi=m + "-autre"),
                  BasculeInterdite) and _arrete(lambda: controle_a2("ok", None, m), ModeleServiAbsent))
    s, _ = suivi()
    s.modeles_a11.add(m)
    s.apres("o", "e", fournisseur="x", modele=m, duree=1, statut="refus", exploitable=False)
    refus_compte = s.roles["o"]["refus_a11"] == 1 and not s.roles["o"]["arrete"]
    s.apres("o", "e", fournisseur="x", modele=m, duree=1, statut="limite", exploitable=False)
    ligne("32", "refus ou limite d'Opus (A11)", refus_compte, bool(s.roles["o"]["arrete"]) and _arrete(
        lambda: s.apres("o2", "e", fournisseur="x", modele=m, duree=1, statut="ok", exploitable=True, modele_servi="autre"), BasculeInterdite))
    # 2 A4
    variantes = [I[0]] + ([I[0] + "s"] if a4["mode"] == "prefixe" else [])
    ligne("2", "étiquettes (A4)", not fv.trouver("une méthode de mesure séquentielle", I, a4["mode"]),
          all(fv.trouver("entrée : " + t, I, a4["mode"]) for t in variantes)
          and _arrete(lambda: fv.garde("entrée : " + I[0], I, a4["mode"]), fv.EtiquetteDansEntree))
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
    kw = {"longueur_max_titre": 10, "longueur_max_resume": 10}
    ok = not _arrete(lambda: verifier_tableau(tab, ["t", "b"], aig, fiches, **kw), Exception)
    ligne("13", "cloisons du tableau (A18)", ok, _arrete(lambda: verifier_tableau(
        {"entrees": [dict(tab["entrees"][0], case=["t", "autre"])]}, ["t", "b"], aig, fiches, **kw), TableauRefuse, "autre case"))
    ligne("14", "fiche entière dans le tableau (A18)", ok, _arrete(lambda: verifier_tableau(
        {"entrees": [dict(tab["entrees"][0], resume="r" * 3000)]}, ["t", "b"], aig, fiches, **kw), TableauRefuse, "résumé"))
    ligne("15", "titre d'une fiche aiguillée (A18)", ok, _arrete(lambda: verifier_tableau(
        {"entrees": [dict(tab["entrees"][0], ident="z")]}, ["t", "b"], aig, dict(fiches, z=_fiche("z", {"t": "z"})), **kw),
        TableauRefuse, "sans passeport"))
    # 16 paires
    f1, f2, f3 = _fiche("f1", {"t": 1}), _fiche("f2", {"t": 2}), _fiche("f3", {"t": 3}, case=("t", "autre"))
    aig = _Aig({x["ident"]: x["empreinte"] for x in (f1, f2, f3)})
    q = b54.cle_paire("f1", "f2")
    choix, _ = b54.choisir_paires_v54([f1, f2], {"a": {q: (1.0, None)}, "b": {q: (2.0, None)}}, ["a", "b"], 1, aig,
                                      {"a": {q: 0.1}, "b": {q: 0.2}})
    art = (_arrete(lambda: b54.verifier_paires_globales({"a": [q], "b": [("f1", "f3")], "c": [("f2", "f3")]}, 2), BisociationRefusee, "n = 2")
           and _arrete(lambda: b54.verifier_paire(f1, f3, aig), BisociationRefusee, "traversant")
           and _arrete(lambda: b54.verifier_paire(f1, f1, aig), BisociationRefusee, "elle-même")
           and _arrete(lambda: b54.verifier_paires_globales({"a": [q], "b": [q]}, 3), BisociationRefusee, "même paire"))
    ligne("16", "paire bien formée ; n = 2 au bras de priorité 1", choix == {"a": [q], "b": []}, art)
    # 18 lecteurs d'étiquettes
    ligne("18", "lecteurs d'étiquettes", b54.b53.valider_etiquettes(["a"], ["a", "b"]) == ["a"],
          _arrete(lambda: b54.b53.valider_etiquettes(["z"], ["a", "b"]), BisociationRefusee, "hors liste"))
    # 20, 21 Gu et Krenn (CL19-01, CL19-08)
    dgk = bras_decl.get("gu_krenn")
    if "gu_krenn" not in bras_conf:
        ligne("20", "note Gu-Krenn", None, None, "bras Gu-Krenn hors configuration", statut=SANS_OBJET)
        ligne("21", "bascule Gu-Krenn (A19)", None, None, "bras Gu-Krenn hors configuration", statut=SANS_OBJET)
    else:
        if "gu_krenn" in bras_params:
            src = bras_params["gu_krenn"]
            gk = conf["bisociateur"]["gu_krenn"]
            voc = sorted(src.actifs)
            from .bisociateur_v53 import SourceGuKrenn
            fausse = lambda: SourceGuKrenn(chemin_piece(conf, gk["source"]["chemin"]), "0" * 64,  # noqa: E731
                                           oeuvres_min_vocabulaire=gk["oeuvres_min_vocabulaire"], date_debut=gk["date_debut"],
                                           date_coupure=gk["date_coupure"], actif_depuis=gk["actif_depuis"],
                                           actif_min_oeuvres=gk["actif_min_oeuvres"])
            ligne("20", "note Gu-Krenn (substitut)", len(voc) >= 2,
                  len(voc) >= 2 and _arrete(lambda: src.note(["hors-vocabulaire", voc[0]], voc[:2]), BisociationRefusee, "hors vocabulaire")
                  and src.note(voc[:1], voc[:2]) is None and _arrete(fausse, BisociationRefusee, "empreinte différente"))
        elif isinstance(dgk, dict) and dgk.get("cause") == CAUSE_SOURCE_ABSENTE:
            ligne("20", "note Gu-Krenn", None, None, "bras Gu-Krenn « non produit (source absente) », déclaré à É0, compté C12 "
                  "(A19, O15) : garde sans objet", statut=SANS_OBJET)
        else:
            ligne("20", "note Gu-Krenn", None, None, "bras Gu-Krenn non produit sans cause déclarée")
        modifiee = copy.deepcopy(bras_decl)
        if isinstance(modifiee.get("gu_krenn"), dict):
            modifiee["gu_krenn"]["mode" if "mode" in modifiee["gu_krenn"] else "cause"] = "autre déclaration"
        ligne("21", "bascule Gu-Krenn déclarée à É0 (A19)",
              not _arrete(lambda: verifier_bascule_gk(bras_decl, copy.deepcopy(bras_decl)), Exception),
              _arrete(lambda: verifier_bascule_gk({}, bras_decl), BasculeGuKrennInterdite, "absente")
              and _arrete(lambda: verifier_bascule_gk(bras_decl, modifiee), BasculeGuKrennInterdite, "changée"))
    # 22b, 23, 24 bras méta
    if "meta" in bras_params:
        p = bras_params["meta"]
        mconf = conf["bisociateur"]["meta"]
        chemin, sha = chemin_piece(conf, mconf["annexe"]["chemin"]), mconf["annexe"]["sha256"]
        lire = lambda c, s: b55.lire_annexe_meta_v55(c, s, definitions=mconf["definitions"],  # noqa: E731
                                                     texte_consigne_lecteur=(texte_piece(conf, conf["bisociateur"]["consigne_lecteur_etiquettes"])
                                                                             if mconf["definitions"] == "consigne" else None),
                                                     brouillon_relu=_piece_annexe(conf, mconf, "brouillon_relu"),
                                                     rapport=_piece_annexe(conf, mconf, "rapport_contre_lecture"))
        with tempfile.TemporaryDirectory() as tmp:
            sain = bool(bras_decl["meta"].get("non_vacuite_e0")) and not _arrete(lambda: lire(chemin, sha), Exception)
            copie, sha_copie = _annexe_modifiee(tmp, chemin, contre_lecture="À REMPLIR")
            art = (_arrete(lambda: lire(os.path.join(tmp, "absente.md"), sha), BisociationRefusee, "absente")
                   and _arrete(lambda: lire(copie, sha_copie), BisociationRefusee, "contre_lecture")
                   and _arrete(lambda: lire(chemin, "0" * 64), BisociationRefusee, "empreinte différente")
                   and _arrete(lambda: b54.verifier_non_vacuite(p, {}), BisociationRefusee, "I-10"))
        ligne("22b", "bras méta, intégrité et non-vacuité (A20, I-9, I-10)", sain, art)
        n0, s0 = p["niches"][0], p["types_structure"][0]
        sain = b54.valider_niche_v54({"niche": n0, "structures": [s0]}, p["niches"], p["types_structure"])[0] == n0
        art = (_arrete(lambda: b54.valider_niche_v54({"niche": "hors"}, p["niches"], p["types_structure"]), BisociationRefusee, "hors grille")
               and _arrete(lambda: b54.valider_niche_v54({"niche": n0, "structures": ["hors"]}, p["niches"], p["types_structure"]),
                           BisociationRefusee, "hors liste")
               and _arrete(lambda: b54.valider_niche_v54({"niche": n0, "structures": [{"type": s0, "nom": s0 + " (autre nom)"}]},
                                                          p["niches"], p["types_structure"]), BisociationRefusee, "I-1")
               and _arrete(lambda: b54.valider_niche_v54({"niche": [n0, p["niches"][1]]}, p["niches"], p["types_structure"]),
                           BisociationRefusee, "une niche par fiche"))
        ligne("23", "lecteurs de niches et structures (I-1)", sain, art)
        n1 = p["niches"][1]

        def triche(pp, na, nb, sa, sb, desaccord=None):
            return b54.score_meta(pp, na, nb, sa, sb) + (1.0 if desaccord == "oui" else 0.0)
        ligne("24", "désaccord hors score (I-2)", not _arrete(lambda: b54.garde_desaccord_v54(b54.score_meta, p, n0, n1, set(), set()), Exception),
              _arrete(lambda: b54.garde_desaccord_v54(triche, p, n0, n1, set(), set()), BisociationRefusee, "désaccord entre dans le score"))
    else:
        for n in ("22b", "23", "24"):
            ligne(n, "bras méta", None, None, "bras méta non produit à É0 (A20) : garde sans objet, déclarée ; réserve jointe (O15)",
                  statut=SANS_OBJET)
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
    # 29 A16, 4 A13, 30 A21
    with tempfile.TemporaryDirectory() as tmp:
        nom = next(iter(conf["pieces"]))
        src = conf["pieces"][nom]
        with open(chemin_piece(conf, src["chemin"]), "rb") as x:
            octets = x.read()
        copie = os.path.join(tmp, "piece")
        with open(copie, "wb") as x:
            x.write(octets)
        c2 = {"pieces": {nom: {"chemin": copie, "sha256": src["sha256"]}}, "_base": tmp}
        sain = not _arrete(lambda: texte_piece(c2, nom), Exception)
        with open(copie, "ab") as x:
            x.write(b"!")
        ligne("29", "versions empreintées (A16)", sain, _arrete(lambda: texte_piece(c2, nom), ConfigurationRefusee, "A16"))
        t = os.path.join(tmp, "temoin.json")
        ecrire_scelle(t, json.dumps({"x": 1}))
        sain = verifier_scelle(t)
        with open(t, "a", encoding="utf-8") as x:
            x.write(" ")
        ligne("4", "empreinte d'un témoin (A13)", sain, not verifier_scelle(t))
        cf = CoffreV55(os.path.join(tmp, "coffre"), lectures_permises=[("cle-x", "boite")])
        cf.deposer("verdicts-e6-x", {"v": 1})
        cf.deposer("cle-x", {"t1": {"classe": "P"}})
        cf.noter_consommation("p", "r", 1.0)
        jeton, _contenu = cf.lire_pour_garde("cle-x", "boite", "garde d'essai")
        journalisee = cf.acces[jeton - 1]["quoi"] == "lecture_par_programme" and "horodatage" in cf.acces[jeton - 1]
        sortie_refusee = _arrete(lambda: cf.noter_sortie_garde(jeton, {"idents": ["t1"]}), SortieDeGardeRefusee)
        cf.noter_sortie_garde(jeton, {"primaires": 1})
        art = (_arrete(lambda: cf.ouvrir("verdicts-e6-x"), LectureAvantFinE9, "A21")
               and _arrete(lambda: cf.lire_pour_garde("cle-x", "autre-role", "essai"), LectureAvantFinE9, "non déclarée")
               and len(cf.incidents) == 2 and sortie_refusee)
        dec, _ = rejouer_consommations(5.0, "sans", [et[0]], cf.consommations())
        b4 = BudgetV54(5.0, "sans", [et[0]])
        b4.avant_etape("p")
        b4.apres_etape("p", 1.0)
        ligne("30", "aveugle de l'orchestrateur (A21) ; lectures par programme journalisées", dec == b4.decisions() and journalisee,
              art and _arrete(lambda: cf.noter_consommation("p", "r", 1.0, verdicts={"x": 1}), ValueError, "aucun verdict"))
    if plan == "pre_pilote":
        from .prepilote_v55 import controle_ancres_v55, controle_longueur, garde_m6b
        pp = conf["prepilote"]
        ok, _ = controle_longueur({"contenu": {"t": "x" * 5000}}, pp["a8"]["min"], pp["a8"]["max"])
        ligne("3", "longueur (A8)", ok, not controle_longueur({"contenu": {"t": "x" * 2900}}, pp["a8"]["min"], pp["a8"]["max"])[0]
              and not controle_longueur({"contenu": {"t": "x" * 8100}}, pp["a8"]["min"], pp["a8"]["max"])[0])
        sq = {"ancres": ["valeur 12", "seuil 0,3"], "couples": [["défaut A", "défaut B"]]}
        ctl = lambda a, b="défaut A", c="défaut B": controle_ancres_v55({"contenu": {"a": a, "b": b, "c": c}}, sq)  # noqa: E731
        c_ok = ctl("valeur 12 ; seuil 0,3")
        art = (ctl("valeur 13 ; seuil 0,3")["ancres"] < 1 and ctl("valeur 123 ; seuil 0,3")["ancres"] < 1
               and ctl("valeur 12 ; seuil 0,35")["ancres"] < 1 and ctl("valeur 12 ; seuil 0,3", c="")["couples"] < 1
               and ctl("valeur 12 ; seuil 0,3 ; 7 cas")["nombres_ajoutes"] == 1)
        ligne("5", "contrôleur d'ancres (S6)", c_ok == {"ancres": 1.0, "couples": 1.0, "nombres_ajoutes": 0}, art)
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
            if n not in externes:
                ligne(n, "garde externe", None, None, "non rejouable par l'orchestrateur : résultat externe scellé exigé "
                                                      "(prepilote.gardes_externes)")
                continue
            try:
                sain, art, motif = verifier_resultat_externe(conf, n, externes[n], etage1)
                ligne(n, "garde externe (résultat scellé, script empreinté)", sain, art, motif)
            except (ConfigurationRefusee, OSError, ValueError, KeyError) as e:
                ligne(n, "garde externe", False, False, str(e)[:200])
    exigees = LIGNES_PRE_PILOTE if plan == "pre_pilote" else LIGNES_COURSE
    manquantes = [x for x in lignes if x["ligne"] in exigees and x["statut"] not in STATUTS_SATISFAITS]
    absentes = [n for n in exigees if not any(x["ligne"] == n for x in lignes)]
    if manquantes or absentes:
        raise GardesE0Refusees("A12 : gardes de la table R5 non rejouées à É0 : "
                               + "; ".join(f"ligne {x['ligne']} ({x['statut']}{' : ' + x['motif'] if x['motif'] else ''})" for x in manquantes)
                               + ("; absentes : " + ", ".join(absentes) if absentes else ""))
    return lignes


__all__ = ("rejouer_gardes_v55", "GardesE0Refusees", "verifier_resultat_externe", "STATUTS_SATISFAITS", "SANS_OBJET", "REJOUEE",
           "LIGNES_COURSE", "LIGNES_PRE_PILOTE")
