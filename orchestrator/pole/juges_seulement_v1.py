"""Mode « juges seulement » (orchestrateur v52, version 1 du module) : noter les fiches validées d'une course **arrêtée**,
scellées par elle, sans refaire les proposeurs — décision du directeur R-805 (30 octobre 2026, ≈ 08:00 UTC) pour la course 1,
tentative 2 (arrêtée à 07:44 UTC sur un refus du juge Fable 5.1, après les deux passes : 29 fiches validées).

Ce que le mode garantit, dans l'ordre, **avant tout appel et toute écriture** (`preparer_juges_seulement`) :
1. la course arrêtée est intacte : sceaux de `manifeste-depart.json`, `manifeste-fin.json` et `fiches-validees.json`, et
   empreintes du manifeste de fin et des fiches validées **égales à celles données** (`empreinte_manifeste_fin`,
   `empreinte_fiches_validees`, fixées dans le lanceur) : une fiche altérée puis rescellée est refusée ; la course s'est arrêtée
   en erreur, sans classement ;
2. les fiches ne sont **jamais lues par un humain ici** : le noyau les traite comme des données ; chacune est revalidée au
   gabarit depuis sa vue servie (ordre canonique des champs, celui de la course), et son empreinte recalculée doit être celle
   écrite par la course ;
3. mêmes témoins plantés, mêmes pièces des juges, même question, même liste blanche, même graine, à l'empreinte écrite au
   manifeste de départ de la course ; mêmes étiquettes et modèles de juges que la course (l'anonymisation dépend de
   l'étiquette) ; seules les fiches **validées** sont servies (la quarantaine et les refus jamais) ;
4. **mêmes consignes** : la consigne de chaque juge est rebâtie comme la course la bâtissait (`anonymiser`, `consigne_juge`) ; toute
   consigne de juge que la course a écrite (dans `juges/` ou mise à l'écart dans `A-L-ECART-modele-non-autorise/juges/`) doit
   avoir **exactement** l'empreinte de sa reconstruction — au moins une, sinon refus (la reconstruction ne serait pas éprouvée) ;
5. budgets par rôle (`budgets[("juge_ideation", modèle)]`), budget total Claude et budget externe séparés : la somme des
   plafonds (contrôles, juges, et pour chaque bascule déclarée la session de repli) tient dans chaque total, sinon refus ;
6. bascules déclarées (`bascules` {modèle déclaré: modèle de repli}) : seulement celles de `BASCULES_AUTORISEES` (R-805 :
   `claude-opus-5-5` → `claude-opus-4-6`), sur un modèle de juge Claude ; jamais pour un juge externe ;
7. relais Claude lisible (moteur réel) : modèles permis **exactement** les modèles Claude du mode (juges et replis déclarés),
   relais v2 (`version_relais`, barème des modèles permis) quand une bascule est déclarée, plafond − réserve − dépense ≥ somme
   des plafonds Claude ;
8. juge externe sur le moteur réel : attestation de lecture humaine scellée portant l'empreinte des fiches validées et de la
   consigne de chaque juge externe (le même contrat que le bras différé : un juge d'une autre lignée ne lit les fiches qu'après
   lecture humaine attestée) ; garde de taille de sa consigne (plafond du juge / prix d'un caractère, provision de sortie).

Puis (`executer_juges_seulement`) : nouveau dossier de sortie (jamais écrasé, R12), manifeste de départ scellé avant tout appel ;
appels de contrôle courts (externe d'abord, puis chaque modèle Claude, repli déclaré compris) ; juges Claude, puis juges externes.
**Refus** (R-764) : le refus d'un modèle déclaré (`stop_reason = refusal`, modèle servi = modèle demandé) ouvre, **si et seulement
si** une bascule est déclarée pour ce modèle, une session **neuve** du même juge (même étiquette, même consigne, même clé
d'anonymisation) sur le modèle de repli ; le refus initial (session mise à l'écart, coût compté), la bascule et le modèle servi
sont consignés. Tout autre refus — sans bascule déclarée, du modèle de repli, d'un juge externe — et tout changement de modèle
non déclaré (événement de repli du kit, modèle servi ≠ modèle demandé, même s'il est le modèle de repli) est un **arrêt**.
Enfin : notes, témoins lus chez chaque juge (critère gelé), classement (moyenne à deux juges, médiane au-delà), manifeste de fin
et liste des empreintes de la sortie, tout scellé.
"""

import hashlib
import json
import os
import re
import shutil
import tempfile

from .adaptateurs import controle_modele_resultat, modele_conforme
from .adaptateurs_v2 import verifier_bascules
from .caviardage import caviarder
from .ideation_v2 import (AUTEUR_TEMOIN, CRITERES, ETIQUETTE, MAX_TOURS_IDEATION, PROVISION_SORTIE_PAR_NOTE, PRIX_CARACTERE_PRUDENT_USD,
                          RAPPORT_SORTIE_ENTREE_PRUDENT, CourseInterrompue, FicheIdeationInvalide, NotesInvalides,
                          TailleConsigneRefusee, _classer, _exiger_plafonds, _exiger_somme, _lire_attestation,
                          _longueurs_temoins, anonymiser, appel_de_controle, charger_liste_blanche, charger_temoins,
                          consigne_juge, cout_compte_controle, garde_taille_consigne, lecture_auto_preference, lecture_temoins,
                          lire_pieces, provision_sortie_juge_caracteres, taille_max_consigne_par_defaut, texte_a_analyser,
                          valider_fiche_ideation, valider_notes, vue_servie)
from .outils import (dossier_traces, ecrire_json_scelle, ecrire_scelle, extraire_bloc_json, manifeste, sha256_fichier,
                     verifier_scelle)
from .pari_apparie import _fini

VERSION_MODE = "juges-seulement-v1 (orchestrateur v52)"
ECART = "A-L-ECART-modele-non-autorise"
EVENEMENTS_REFUS_DU_MODELE = ("result.stop_reason", "assistant.stop_reason")  # refus dit par le modèle lui-même
MOTIF_IDENTIFIANT = re.compile(r"^([a-z0-9][a-z0-9-]{0,39})-p([12])-(\d{2})$")
FICHIERS_SCELLES_COURSE = ("manifeste-depart.json", "manifeste-fin.json", "fiches-validees.json")


class JugesSeulementRefuse(CourseInterrompue):
    """Refus avant tout appel et toute écriture (rien payé)."""


# --- course arrêtée ----------------------------------------------------------------------------------------------------


def _lire_json(chemin):
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def lire_course_arretee(course, empreinte_manifeste_fin, empreinte_fiches_validees):
    """Vérifie la course arrêtée (sceaux, empreintes attendues, arrêt sans classement) ; rend (départ, fin, fiches brutes,
    description). Les fiches ne sont qu'empreintées et chargées comme données."""
    course = os.path.abspath(course)
    if not os.path.isdir(course) or os.path.islink(course):
        raise JugesSeulementRefuse(f"dossier de la course arrêtée absent, ou lien symbolique : {course}")
    for nom, attendu in (("empreinte_manifeste_fin", empreinte_manifeste_fin),
                         ("empreinte_fiches_validees", empreinte_fiches_validees)):
        if not isinstance(attendu, str) or not re.fullmatch(r"[0-9a-f]{64}", attendu):
            raise JugesSeulementRefuse(f"{nom} : empreinte SHA-256 complète (64 caractères hexadécimaux) exigée")
    for nom in FICHIERS_SCELLES_COURSE:
        chemin = os.path.join(course, nom)
        if os.path.islink(chemin) or not verifier_scelle(chemin):
            raise JugesSeulementRefuse(f"course arrêtée : {nom} absent, lien symbolique, ou sceau faux (fichier altéré) : refus")
    empreintes = {nom: sha256_fichier(os.path.join(course, nom)) for nom in FICHIERS_SCELLES_COURSE}
    if empreintes["manifeste-fin.json"] != empreinte_manifeste_fin:
        raise JugesSeulementRefuse(f"manifeste-fin.json : empreinte {empreintes['manifeste-fin.json'][:16]}… ≠ attendue "
                                   f"{empreinte_manifeste_fin[:16]}… : refus")
    if empreintes["fiches-validees.json"] != empreinte_fiches_validees:
        raise JugesSeulementRefuse(f"fiches-validees.json : empreinte {empreintes['fiches-validees.json'][:16]}… ≠ attendue "
                                   f"{empreinte_fiches_validees[:16]}… (fiches altérées, ou autre course) : refus")
    depart = _lire_json(os.path.join(course, "manifeste-depart.json"))["reglages"]
    fin = _lire_json(os.path.join(course, "manifeste-fin.json"))["reglages"]
    if fin.get("phase") != "fin" or depart.get("phase") != "depart":
        raise JugesSeulementRefuse("manifestes de la course : phases « depart » et « fin » attendues")
    if not fin.get("erreur"):
        raise JugesSeulementRefuse("la course ne s'est pas arrêtée en erreur : le mode « juges seulement » ne note que les fiches "
                                   "d'une course arrêtée (une course complète passe par son bras)")
    if fin.get("nombre_lignes_classement") or os.path.exists(os.path.join(course, "classement.json")):
        raise JugesSeulementRefuse("la course a écrit un classement : rien à rejouer")
    for cle in ("dossier_ferme", "moisson", "tests_de_mort"):
        if depart.get(cle):
            raise JugesSeulementRefuse(f"course avec {cle} : non pris en charge par la v52 (consigne des juges différente)")
    fiches = _lire_json(os.path.join(course, "fiches-validees.json"))
    if not isinstance(fiches, list) or not fiches:
        raise JugesSeulementRefuse("fiches-validees.json : liste non vide attendue")
    description = {"dossier": course, "empreintes": empreintes, "nombre_fiches_validees": len(fiches),
                   "statut_course": fin.get("statut_course"), "arret": caviarder(str(fin.get("erreur")))[0][:500],
                   "graine": depart.get("graine"), "moteur_de_la_course": depart.get("moteur")}
    return depart, fin, fiches, description


def reconstruire_fiches(fiches):
    """Chaque fiche revalidée au gabarit depuis sa vue servie (ordre canonique des champs) ; l'empreinte recalculée et la fiche
    entière doivent être celles de la course. Rend la liste reconstruite (ordre de la course)."""
    vues, sortie = set(), []
    for k, f in enumerate(fiches, 1):
        if not isinstance(f, dict):
            raise JugesSeulementRefuse(f"fiche validée n° {k} : objet attendu")
        m = MOTIF_IDENTIFIANT.match(str(f.get("identifiant_auteur")))
        if not m or f.get("auteur") != m.group(1) or f.get("passe") != int(m.group(2)):
            raise JugesSeulementRefuse(f"fiche validée n° {k} : identifiant, auteur ou passe incohérents")
        if f["identifiant_auteur"] in vues:
            raise JugesSeulementRefuse(f"fiche validée n° {k} : identifiant en double")
        vues.add(f["identifiant_auteur"])
        try:
            r = valider_fiche_ideation(vue_servie(f), m.group(1), int(m.group(3)), passe=int(m.group(2)))
        except FicheIdeationInvalide as e:
            raise JugesSeulementRefuse(f"fiche validée n° {k} ({f['identifiant_auteur']}) : ne repasse pas le gabarit ({e})") from e
        if r.get("empreinte") != f.get("empreinte") or r != f:
            raise JugesSeulementRefuse(f"fiche validée n° {k} ({f['identifiant_auteur']}) : empreinte recalculée ≠ empreinte de "
                                       "la course (fiche altérée) : refus")
        sortie.append(r)
    return sortie


def consignes_ecrites_par_la_course(course):
    """{étiquette: {chemin, sha256}} des consignes de juge écrites et scellées par la course (juges joués, ou mis à l'écart)."""
    trouvees = {}
    for base in ("juges", os.path.join(ECART, "juges")):
        dossier = os.path.join(course, base)
        if not os.path.isdir(dossier):
            continue
        for nom in sorted(os.listdir(dossier)):
            if not nom.startswith("traces-"):
                continue
            chemin = os.path.join(dossier, nom, "consigne.md")
            if not os.path.isfile(chemin):
                continue
            if os.path.islink(chemin) or not verifier_scelle(chemin):
                raise JugesSeulementRefuse(f"consigne de juge de la course au sceau faux : {os.path.relpath(chemin, course)}")
            etiquette = nom[len("traces-"):]
            if etiquette in trouvees:
                raise JugesSeulementRefuse(f"deux consignes écrites pour le juge {etiquette!r} dans la course")
            trouvees[etiquette] = {"chemin": os.path.relpath(chemin, course), "sha256": sha256_fichier(chemin)}
    return trouvees


# --- préparation (aucun appel, aucune écriture) -------------------------------------------------------------------------


def preparer_juges_seulement(course, *, empreinte_manifeste_fin, empreinte_fiches_validees, liste_blanche, question,
                             pieces_juge, temoins, juges, juges_externes=(), budgets, budget_total_usd,
                             budget_externe_usd=0.0, budget_controle_usd=0.2, bascules=None,
                             prix_caractere_usd=PRIX_CARACTERE_PRUDENT_USD, taille_max_consigne_externe=None):
    """Tout ce qui se vérifie sans appel ni écriture ; rend le plan (consignes, clés, sommes, descriptions). `juges` et
    `juges_externes` : listes de (étiquette, modèle)."""
    depart, _fin, fiches_brutes, description = lire_course_arretee(course, empreinte_manifeste_fin, empreinte_fiches_validees)
    juges, juges_externes = [tuple(j) for j in juges], [tuple(j[:2]) for j in juges_externes]
    if not juges and not juges_externes:
        raise JugesSeulementRefuse("aucun juge donné")
    for e, _ in juges + juges_externes:  # mêmes règles d'étiquette que la course (`valider_etiquettes`), sans proposeur
        if not ETIQUETTE.match(e) or e == AUTEUR_TEMOIN:
            raise JugesSeulementRefuse(f"étiquette de juge invalide ou réservée : {e!r}")
    if len({e for e, _ in juges + juges_externes}) != len(juges + juges_externes):
        raise JugesSeulementRefuse("étiquettes de juges en double")
    course_juges = {e: m for e, m in depart.get("juges") or []}
    course_externes = {e: m for e, m in depart.get("juges_externes") or []}
    for e, m in juges:
        if course_juges.get(e) != m:
            raise JugesSeulementRefuse(f"juge {e}={m} : pas un juge Claude de la course ({course_juges}) — mêmes étiquettes et "
                                       "modèles, sinon la consigne (anonymisation par étiquette) change")
    for e, m in juges_externes:
        if course_externes.get(e) != m:
            raise JugesSeulementRefuse(f"juge externe {e}={m} : pas un juge externe de la course ({course_externes})")
    # bascules : autorisées, sur un modèle de juge Claude seulement
    bascules_lues = verifier_bascules(bascules or {})
    for declare in bascules_lues:
        if declare not in {m for _, m in juges}:
            raise JugesSeulementRefuse(f"bascule déclarée sur {declare!r}, qui n'est le modèle d'aucun juge Claude donné "
                                       "(jamais de bascule pour un juge externe)")
    # budgets par rôle et totaux
    _exiger_plafonds(budgets)
    for nom_b, b in (("budget_total_usd", budget_total_usd), ("budget_externe_usd", budget_externe_usd),
                     ("budget_controle_usd", budget_controle_usd)):
        _exiger_somme(nom_b, b)
    replis = [b["repli"] for b in bascules_lues.values()]
    for m in [m for _, m in juges + juges_externes] + replis:
        if ("juge_ideation", m) not in budgets:
            raise JugesSeulementRefuse(f"aucun plafond par session pour ('juge_ideation', {m!r})")
    modeles_claude = sorted({m for _, m in juges} | set(replis))
    somme_claude = budget_controle_usd * len(modeles_claude) + sum(budgets[("juge_ideation", m)] for _, m in juges) \
        + sum(budgets[("juge_ideation", bascules_lues[m]["repli"])] for _, m in juges if m in bascules_lues)
    somme_externe = budget_controle_usd * len(juges_externes) + sum(budgets[("juge_ideation", m)] for _, m in juges_externes)
    if somme_claude > float(budget_total_usd) + 1e-9:
        raise JugesSeulementRefuse(f"somme des plafonds Claude {somme_claude:.4f} (contrôles, juges, sessions de repli déclarées) "
                                   f"> total {budget_total_usd} : refus")
    if juges_externes and somme_externe > float(budget_externe_usd) + 1e-9:
        raise JugesSeulementRefuse(f"somme des plafonds externes {somme_externe:.4f} > total externe {budget_externe_usd} : refus")
    # mêmes entrées que la course, aux empreintes du manifeste de départ
    liste = charger_liste_blanche(liste_blanche)
    if (depart.get("liste_blanche") or {}).get("sha256") != sha256_fichier(liste_blanche):
        raise JugesSeulementRefuse("liste blanche : empreinte ≠ celle de la course")
    question_lue = lire_pieces([question], liste)[0]
    if [question_lue[0], question_lue[2]] != [(depart.get("question") or {}).get("nom"), (depart.get("question") or {}).get("sha256")]:
        raise JugesSeulementRefuse("question : nom ou empreinte ≠ ceux de la course")
    taille_max_pieces = depart.get("taille_max_pieces")
    pieces_juge_lues = lire_pieces(list(pieces_juge), liste, taille_max_pieces) if pieces_juge else []
    if [{"nom": n, "sha256": h} for n, _, h in pieces_juge_lues] != list(depart.get("pieces_juge") or []):
        raise JugesSeulementRefuse("pièces des juges : liste (noms, empreintes, ordre) ≠ celle de la course")
    if not temoins or (depart.get("temoins") or {}).get("sha256") != liste.get(os.path.realpath(temoins)):
        raise JugesSeulementRefuse("témoins : fichier absent, ou empreinte ≠ celle de la course")
    temoins_lus = charger_temoins(temoins, liste)
    if len(temoins_lus) != (depart.get("temoins") or {}).get("nombre"):
        raise JugesSeulementRefuse("témoins : nombre ≠ celui de la course")
    fiches = reconstruire_fiches(fiches_brutes)
    graine = depart.get("graine")
    servies = fiches + temoins_lus
    par_ident = {f["identifiant_auteur"]: f for f in servies}

    def batir(etiquette):
        anonymes, cle = anonymiser(servies, graine, etiquette)
        texte = consigne_juge(anonymes, question_lue[1], pieces_juge_lues, citations=False, moisson=False)
        return texte, cle

    # mêmes consignes : chaque consigne écrite par la course a l'empreinte de sa reconstruction
    ecrites = consignes_ecrites_par_la_course(description["dossier"])
    if not ecrites:
        raise JugesSeulementRefuse("aucune consigne de juge écrite par la course : la reconstruction des consignes ne peut pas "
                                   "être éprouvée (refus)")
    reconstruction = {}
    for etiquette, e in sorted(ecrites.items()):
        texte, _ = batir(etiquette)
        sha = hashlib.sha256(texte.encode("utf-8")).hexdigest()
        reconstruction[etiquette] = dict(e, sha256_reconstruite=sha, identique=(sha == e["sha256"]))
        if sha != e["sha256"]:
            raise JugesSeulementRefuse(f"consigne du juge {etiquette!r} reconstruite ({sha[:16]}…) ≠ consigne écrite par la course "
                                       f"({e['sha256'][:16]}…) : refus (fiches, témoins, pièces ou code différents)")
    consignes, cles = {}, {}
    for e, _ in juges + juges_externes:
        texte, cle = batir(e)
        consignes[e] = {"texte": texte, "sha256": hashlib.sha256(texte.encode("utf-8")).hexdigest(), "taille": len(texte)}
        cles[e] = cle
    # garde de taille des juges externes (sans dépense), comme le bras
    gardes = {}
    for e, m in juges_externes:
        if taille_max_consigne_externe is not None:
            tmax, origine, prov = int(taille_max_consigne_externe), "donnée (--taille-max-consigne-externe-bras)", 0
        else:
            plafond = budgets[("juge_ideation", m)]
            prov = provision_sortie_juge_caracteres(len(cles[e]))
            tmax = taille_max_consigne_par_defaut(plafond, prov, prix_caractere_usd)
            origine = (f"défaut : plafond du juge {plafond} / prix {prix_caractere_usd:.4e} dollar par caractère − provision de sortie "
                       f"{prov} ({len(cles[e])} fiches × {PROVISION_SORTIE_PAR_NOTE} au rapport {RAPPORT_SORTIE_ENTREE_PRUDENT:g})")
        try:
            gardes[e] = garde_taille_consigne(f"consigne du juge externe {e!r}", consignes[e]["taille"], tmax, origine, prov,
                                              prix_caractere_usd)
        except TailleConsigneRefusee as exc:
            raise JugesSeulementRefuse(f"garde de taille : {exc} (rien envoyé, rien payé)") from exc
    modele_par_auteur = {e: m for e, m in depart.get("proposeurs") or []}
    modele_par_auteur.update({e: m for e, m, *_ in depart.get("proposeurs_externes") or []})
    return {"course": description, "depart_course": depart, "fiches": fiches, "temoins": temoins_lus, "servies": servies,
            "par_ident": par_ident, "consignes": consignes, "cles": cles, "reconstruction": reconstruction,
            "juges": juges, "juges_externes": juges_externes, "bascules": bascules_lues, "modeles_claude": modeles_claude,
            "budgets": dict(budgets), "budget_total_usd": float(budget_total_usd),
            "budget_externe_usd": float(budget_externe_usd), "budget_controle_usd": float(budget_controle_usd),
            "sommes": {"claude": round(somme_claude, 6), "total_claude": float(budget_total_usd),
                       "externe": round(somme_externe, 6), "total_externe": float(budget_externe_usd)},
            "gardes_taille": gardes, "graine": graine, "modele_par_auteur": modele_par_auteur,
            "entrees": {"liste_blanche": {"fichier": os.path.basename(liste_blanche), "sha256": sha256_fichier(liste_blanche)},
                        "question": {"nom": question_lue[0], "sha256": question_lue[2]},
                        "pieces_juge": [{"nom": n, "sha256": h} for n, _, h in pieces_juge_lues],
                        "temoins": dict(depart.get("temoins") or {})}}


def resume_du_plan(plan):
    """Ce que `--verifier-seulement` imprime : empreintes, comptes, tailles, sommes — jamais le contenu d'une fiche."""
    return {"sans_appel": True, "course_arretee": plan["course"], "fiches_servies": len(plan["fiches"]),
            "temoins_servis": len(plan["temoins"]), "reconstruction_des_consignes_de_la_course": plan["reconstruction"],
            "consignes": {e: {"sha256": c["sha256"], "taille": c["taille"]} for e, c in plan["consignes"].items()},
            "juges": [list(j) for j in plan["juges"]], "juges_externes": [list(j) for j in plan["juges_externes"]],
            "bascules_declarees": plan["bascules"], "modeles_claude_du_relais": plan["modeles_claude"],
            "sommes_des_plafonds": plan["sommes"], "gardes_taille": plan["gardes_taille"],
            "attestation_a_signer": {"fiches_validees_sha256": plan["course"]["empreintes"]["fiches-validees.json"],
                                     "consignes_en_attente_sha256": {e: plan["consignes"][e]["sha256"]
                                                                     for e, _ in plan["juges_externes"]}}}


def verifier_relais_juges(etat, plan):
    """Relais Claude (moteur réel) : champs finis ; modèles permis = exactement les modèles Claude du mode ; relais v2 si une
    bascule est déclarée ; plafond − réserve − dépense ≥ somme des plafonds Claude. Rend l'état lu."""
    for champ in ("plafond_usd", "reserve_par_appel_usd", "depense_usd"):
        v = etat.get(champ)
        if v is None or not _fini(v) or v < 0:
            raise JugesSeulementRefuse(f"relais : {champ} absent, non fini ou négatif ({v!r})")
    permis = etat.get("modeles_permis")
    if not isinstance(permis, list) or set(permis) != set(plan["modeles_claude"]):
        raise JugesSeulementRefuse(f"relais : modèles permis {permis!r} ≠ modèles Claude du mode {plan['modeles_claude']} (R-764, "
                                   "barrière 3 : juges et replis déclarés, exactement)")
    if plan["bascules"]:
        bareme = etat.get("bareme_modeles_permis")
        if not etat.get("version_relais") or not isinstance(bareme, dict) \
                or any(b["repli"] not in bareme for b in plan["bascules"].values()):
            raise JugesSeulementRefuse("relais : bascule déclarée, relais v2 exigé (pole/relais_reel_v2.py : version_relais et barème "
                                       "des modèles permis, borne haute pour un modèle hors barème)")
    reste = float(etat["plafond_usd"]) - float(etat["reserve_par_appel_usd"]) - float(etat["depense_usd"])
    if reste < plan["sommes"]["claude"] - 1e-9:
        raise JugesSeulementRefuse(f"relais : plafond − réserve − dépense = {reste:.4f} < somme des plafonds Claude "
                                   f"{plan['sommes']['claude']:.4f}")
    return {k: etat.get(k) for k in ("plafond_usd", "reserve_par_appel_usd", "depense_usd", "modeles_permis", "version_relais",
                                     "bareme_modeles_permis")}


# --- exécution ---------------------------------------------------------------------------------------------------------


def refus_dit_par_le_modele(refus, modele):
    """Vrai si le refus est celui du modèle demandé lui-même (`stop_reason = refusal`, modèle servi absent ou conforme) — le seul
    refus qui ouvre une bascule déclarée. Un événement de repli du kit ou un modèle servi différent n'en est jamais un."""
    servi = refus.get("modele_servi")
    return refus.get("evenement") in EVENEMENTS_REFUS_DU_MODELE and (servi is None or modele_conforme(modele, servi))


def executer_juges_seulement(plan, sortie, adaptateur, externes=None, *, moteur="simule", lire_etat_relais=None,
                             horodatage=None, versions=None, commande_externe=None, attestation_lecture_humaine=None,
                             exiger_attestation=False, exiger_modele_servi_claude=False, max_tours=MAX_TOURS_IDEATION):
    """Joue les juges du plan. `adaptateur` : juges Claude (et sessions de repli) ; `externes` : {étiquette: adaptateur}.
    Rend {"classement", "lecture", "journal", "lisible"} ; lève `CourseInterrompue` sur tout arrêt (manifeste de fin écrit)."""
    externes = dict(externes or {})
    for e, _ in plan["juges_externes"]:
        if e not in externes:
            raise JugesSeulementRefuse(f"aucun adaptateur pour le juge externe {e!r}")
        if moteur == "claude-sdk" and getattr(externes[e], "nom", None) != "commande-externe":
            raise JugesSeulementRefuse(f"moteur réel : seule une commande externe joue le juge {e!r} (CL35-04)")
    if moteur == "claude-sdk" and plan["juges"] and getattr(adaptateur, "nom", None) != "claude-sdk":
        raise JugesSeulementRefuse("moteur réel déclaré, mais l'adaptateur des juges Claude n'est pas celui du kit")
    attestation = None
    if attestation_lecture_humaine or (exiger_attestation and plan["juges_externes"]):
        if not attestation_lecture_humaine:
            raise JugesSeulementRefuse("juge externe sur le moteur réel : attestation de lecture humaine scellée exigée "
                                       "({lecteur, lu_le, fiches_validees_sha256, consignes_en_attente_sha256}), comme au bras "
                                       "différé ; --verifier-seulement imprime les empreintes à attester")
        attestation = _lire_attestation(attestation_lecture_humaine,
                                        ("lecteur", "lu_le", "fiches_validees_sha256", "consignes_en_attente_sha256"))
        if attestation["fiches_validees_sha256"] != plan["course"]["empreintes"]["fiches-validees.json"]:
            raise JugesSeulementRefuse("attestation : empreinte des fiches validées ≠ celle de la course")
        attestees = attestation["consignes_en_attente_sha256"]
        for e, _ in plan["juges_externes"]:
            if not isinstance(attestees, dict) or attestees.get(e) != plan["consignes"][e]["sha256"]:
                raise JugesSeulementRefuse(f"attestation : empreinte de la consigne du juge externe {e!r} absente ou différente")
    etat_relais_depart = verifier_relais_juges(lire_etat_relais(), plan) if lire_etat_relais else None
    sortie = os.path.abspath(sortie)
    if os.path.exists(sortie):
        raise JugesSeulementRefuse(f"SORTIE existe déjà : {sortie} (jamais écrasée, R12)")
    course = plan["course"]["dossier"]
    if sortie == course or sortie.startswith(course + os.sep):
        raise JugesSeulementRefuse("SORTIE dans le dossier de la course arrêtée : refus (la course reste intacte)")

    budgets = plan["budgets"]
    journal = {"appels": [], "cout_total_usd": 0.0, "cout_externe_usd": 0.0, "cout_fictif": moteur != "claude-sdk",
               "controles": {}, "arret": None, "refus_modele": [], "bascules": [], "modele_servi_par_juge": {},
               "depense_modele_non_autorise_usd": 0.0, "statut": None}
    # manifeste de départ : dossier provisoire puis renommé (aucune SORTIE laissée par une interruption avant)
    parent = os.path.dirname(sortie)
    os.makedirs(parent, exist_ok=True)
    provisoire = tempfile.mkdtemp(prefix=os.path.basename(sortie) + ".depart-en-cours-", dir=parent)
    try:
        ecrire_json_scelle(os.path.join(provisoire, "manifeste-depart-juges.json"), manifeste(
            phase="depart-juges-seulement", mode=VERSION_MODE, horodatage=horodatage, moteur=moteur, versions=versions or {},
            course_arretee=plan["course"], reconstruction_des_consignes=plan["reconstruction"],
            entrees=plan["entrees"], graine=plan["graine"], fiches_servies=len(plan["fiches"]),
            temoins_servis=len(plan["temoins"]), regle_des_fiches="fiches validées seulement (quarantaine et refus jamais servis) ; "
            "contenu jamais lu par l'opérateur du code : empreintes vérifiées",
            juges=[list(j) for j in plan["juges"]], juges_externes=[list(j) for j in plan["juges_externes"]],
            consignes={e: {"sha256": c["sha256"], "taille": c["taille"]} for e, c in plan["consignes"].items()},
            bascules_declarees=plan["bascules"], modeles_claude=plan["modeles_claude"],
            budgets_par_session={f"{r}|{m}": v for (r, m), v in budgets.items()}, somme_des_plafonds=plan["sommes"],
            budget_controle_usd=plan["budget_controle_usd"], gardes_taille=plan["gardes_taille"],
            relais_au_depart=etat_relais_depart, commande_externe=commande_externe,
            attestation=({"fichier": os.path.basename(attestation_lecture_humaine),
                          "sha256": sha256_fichier(attestation_lecture_humaine), "lecteur": attestation.get("lecteur"),
                          "lu_le": attestation.get("lu_le")} if attestation else None),
            exiger_modele_servi_claude=exiger_modele_servi_claude))
        if os.path.exists(sortie):
            raise JugesSeulementRefuse(f"SORTIE existe déjà : {sortie} (R12)")
        os.rename(provisoire, sortie)
    except BaseException:
        shutil.rmtree(provisoire, ignore_errors=True)
        raise

    def arreter(motif, statut=None):
        journal["arret"] = motif
        if statut:
            journal["statut"] = statut
        raise CourseInterrompue(motif)

    def mettre_a_l_ecart(dossier):
        deplaces = []
        for source in (dossier, dossier_traces(dossier)):
            if os.path.isdir(source):
                cible = os.path.join(sortie, ECART, os.path.relpath(source, sortie))
                os.makedirs(os.path.dirname(cible), exist_ok=True)
                shutil.move(source, cible)
                deplaces.append(os.path.relpath(cible, sortie))
        return deplaces

    def session(etiquette, modele, dossier, adapt, externe):
        """Une session de juge ; rend (r, refus | None). Coût compté (déclaré, ou écart lu au relais, le plus grand)."""
        plafond = budgets[("juge_ideation", modele)]
        cle, total = ("cout_externe_usd", plan["budget_externe_usd"]) if externe else ("cout_total_usd", plan["budget_total_usd"])
        if journal[cle] + plafond > total + 1e-9:
            arreter(f"plafond {'externe' if externe else 'total Claude'} {total} atteint avant le juge {etiquette} ({modele})",
                    {"statut": "plafond"})
        consigne = plan["consignes"][etiquette]["texte"]
        os.makedirs(dossier, exist_ok=True)
        traces = dossier_traces(dossier)
        empreinte = ecrire_scelle(os.path.join(traces, "consigne.md"), consigne)
        if empreinte != plan["consignes"][etiquette]["sha256"]:
            arreter(f"consigne du juge {etiquette} : empreinte écrite ≠ empreinte du plan")
        avant = lire_etat_relais() if (lire_etat_relais and not externe) else None
        try:
            r = adapt.lancer("juge_ideation", consigne, dossier, plafond, max_tours, modele=modele)
        except BaseException as e:
            journal[cle] += plafond
            journal["appels"].append({"role": "juge_ideation", "etiquette": etiquette, "modele": modele, "externe": externe,
                                      "statut": "interrompue", "cout_compte_usd": plafond, "cout_inconnu": True,
                                      "erreur": type(e).__name__ + " : " + caviarder(str(e))[0][:300]})
            journal["arret"] = f"juge {etiquette} ({modele}) interrompu : {type(e).__name__}"
            raise
        apres = lire_etat_relais() if (lire_etat_relais and not externe) else None
        texte = caviarder(r.texte_final or "")[0]
        ecrire_scelle(os.path.join(traces, "reponse.md"), texte)
        ecart_relais = None
        if avant is not None and apres is not None:
            ecart_relais = round(float(apres.get("depense_usd", 0.0)) - float(avant.get("depense_usd", 0.0)), 6)
        cout = max(float(r.cout_declare_usd or 0.0), ecart_relais or 0.0)
        journal[cle] += cout
        appel = {"role": "juge_ideation", "etiquette": etiquette, "modele": modele, "externe": externe, "statut": r.statut,
                 "cout_declare_usd": r.cout_declare_usd, "ecart_relais_usd": ecart_relais, "cout_compte_usd": cout,
                 "cout_inconnu": bool(getattr(r, "cout_inconnu", False)), "erreur": r.erreur,
                 "modele_servi": getattr(r, "modele_servi", None), "taille_consigne": len(consigne),
                 "consigne_sha256": empreinte, "dossier": os.path.relpath(dossier, sortie)}
        journal["appels"].append(appel)
        refus = getattr(r, "refus", None)
        if refus is None and r.statut != "refus":  # défense en profondeur sur le modèle servi, tout adaptateur
            refus = controle_modele_resultat(modele, r, getattr(adapt, "modeles_servis_permis", None))
            if refus is not None:
                depense = float(getattr(r, "depense_modele_non_autorise_usd", 0.0) or 0.0) or cout
                r.depense_modele_non_autorise_usd = depense
        if refus is not None or r.statut == "refus":
            refus = dict(refus or {"motif": str(r.erreur), "modele_demande": modele,
                                   "modele_servi": getattr(r, "modele_servi", None), "evenement": None})
            depense = float(getattr(r, "depense_modele_non_autorise_usd", 0.0) or 0.0)
            journal["depense_modele_non_autorise_usd"] += depense
            deplaces = mettre_a_l_ecart(dossier)
            entree = {"etiquette": etiquette, "modele_demande": modele, "modele_servi": refus.get("modele_servi"),
                      "evenement": refus.get("evenement"), "motif": caviarder(str(refus.get("motif")))[0][:300],
                      "externe": externe, "cout_compte_usd": cout, "depense_modele_non_autorise_usd": depense,
                      "mis_a_l_ecart": deplaces}
            journal["refus_modele"].append(entree)
            appel.update({"statut": "refus", "refus": entree})
            return r, entree
        if r.statut != "ok" or r.erreur:
            arreter(f"juge {etiquette} ({modele}) : statut {r.statut!r}, erreur {r.erreur!r}", {"statut": "erreur"})
        if not externe and exiger_modele_servi_claude and not getattr(r, "modele_servi", None):
            arreter(f"juge {etiquette} ({modele}) : modèle servi non lu (contrôle du modèle servi exigé sur le moteur réel)",
                    {"statut": "erreur"})
        return r, None

    notes_par_juge, doublons_par_juge = {}, {}

    def noter(etiquette, r):
        cle = plan["cles"][etiquette]
        try:
            notes, doubles = valider_notes(extraire_bloc_json(texte_a_analyser(r), "notes"), list(cle.keys()))
        except NotesInvalides as e:
            arreter(caviarder(f"juge {etiquette} : notes invalides ({e})")[0], {"statut": "erreur"})
        notes_par_juge[etiquette] = {cle[i]: n for i, n in notes.items()}
        doublons_par_juge[etiquette] = doubles

    erreur = None
    resultat = {"classement": None, "lecture": None, "journal": journal, "lisible": False}
    try:
        # --- appels de contrôle courts : externes d'abord, puis chaque modèle Claude (repli déclaré compris)
        for e, m in plan["juges_externes"]:
            try:
                lec = appel_de_controle(externes[e], [m], os.path.join(sortie, "controles", "externe-" + e),
                                        plan["budget_controle_usd"], None, exiger_cout=(moteur == "claude-sdk"),
                                        role="juge_ideation")[m]
            except BaseException as exc:
                lec = (getattr(exc, "lecture", None) or {}).get(m, {})
                journal["cout_externe_usd"] += cout_compte_controle(lec) if lec else 0.0
                journal["controles"]["externe:" + e] = lec
                journal["arret"] = f"contrôle du juge externe {e} ({m}) refusé : " + caviarder(str(exc))[0][:300]
                journal["statut"] = {"statut": "controle_refuse", "etiquette": e, "modele": m}
                raise
            journal["controles"]["externe:" + e] = lec
            journal["cout_externe_usd"] += cout_compte_controle(lec)
        if plan["modeles_claude"]:
            try:
                lectures = appel_de_controle(adaptateur, plan["modeles_claude"], os.path.join(sortie, "controles", "claude"),
                                             plan["budget_controle_usd"], lire_etat_relais, exiger_cout=(moteur == "claude-sdk"))
            except BaseException as exc:
                lectures = getattr(exc, "lecture", None) or {}
                journal["cout_total_usd"] += sum(cout_compte_controle(x) for x in lectures.values())
                journal["controles"].update(lectures)
                journal["arret"] = "contrôle Claude refusé : " + caviarder(str(exc))[0][:300]
                journal["statut"] = {"statut": "controle_refuse"}
                raise
            journal["controles"].update(lectures)
            journal["cout_total_usd"] += sum(cout_compte_controle(x) for x in lectures.values())
        # --- juges Claude, puis juges externes
        for etiquette, modele in plan["juges"]:
            r, refus = session(etiquette, modele, os.path.join(sortie, "juges", etiquette), adaptateur, False)
            servi = getattr(r, "modele_servi", None) or modele
            if refus is not None:
                bascule = plan["bascules"].get(modele)
                if bascule is None or not refus_dit_par_le_modele(refus, modele):
                    pourquoi = ("aucune bascule déclarée pour ce modèle" if bascule is None else
                                "changement de modèle non déclaré (seul un refus dit par le modèle demandé ouvre la bascule)")
                    arreter(f"refus (R-764) : juge {etiquette}, modèle demandé {modele!r}, modèle servi {refus.get('modele_servi')!r}, "
                            f"événement {refus.get('evenement')!r} : {pourquoi} ; session close, sortie mise à l'écart",
                            {"statut": "refus", "etiquette": etiquette, "modele_demande": modele,
                             "modele_servi": refus.get("modele_servi")})
                repli = bascule["repli"]
                entree = {"etiquette": etiquette, "modele_declare": modele, "modele_repli": repli,
                          "autorisation": bascule["autorisation"], "refus_initial": refus,
                          "regle": "bascule déclarée (option explicite), ouverte par un refus dit par le modèle déclaré ; "
                                   "session neuve du même juge, même consigne, même clé d'anonymisation"}
                journal["bascules"].append(entree)
                r, refus2 = session(etiquette, repli, os.path.join(sortie, "juges-bascule", etiquette), adaptateur, False)
                if refus2 is not None:
                    entree["refus_du_repli"] = refus2
                    arreter(f"refus (R-764) : juge {etiquette} sur le modèle de repli {repli!r} (modèle servi "
                            f"{refus2.get('modele_servi')!r}) : arrêt, aucune autre bascule",
                            {"statut": "refus", "etiquette": etiquette, "modele_demande": repli,
                             "modele_servi": refus2.get("modele_servi")})
                servi = getattr(r, "modele_servi", None) or repli
                entree["modele_servi"] = servi
                entree["session"] = os.path.join("juges-bascule", etiquette)
            journal["modele_servi_par_juge"][etiquette] = {"demande": modele, "servi": servi,
                                                           "servi_lu": bool(getattr(r, "modele_servi", None)),
                                                           "bascule": any(b["etiquette"] == etiquette for b in journal["bascules"])}
            noter(etiquette, r)
        for etiquette, modele in plan["juges_externes"]:
            r, refus = session(etiquette, modele, os.path.join(sortie, "juges-externes", etiquette), externes[etiquette], True)
            if refus is not None:
                arreter(f"refus (R-764) : juge externe {etiquette} ({modele}), modèle servi {refus.get('modele_servi')!r} : arrêt "
                        "(jamais de bascule pour un juge externe)",
                        {"statut": "refus", "etiquette": etiquette, "modele_demande": modele,
                         "modele_servi": refus.get("modele_servi")})
            journal["modele_servi_par_juge"][etiquette] = {"demande": modele, "servi": getattr(r, "modele_servi", None) or modele,
                                                           "servi_lu": bool(getattr(r, "modele_servi", None)), "bascule": False}
            noter(etiquette, r)
        # --- lecture : témoins chez chaque juge, classement
        temoins = plan["temoins"]
        modele_par_juge = {e: v["servi"] for e, v in journal["modele_servi_par_juge"].items()}
        lt = lecture_temoins(notes_par_juge, temoins, doublons_par_juge, plan["cles"])
        base = {"temoins": lt,
                "temoins_ok_par_juge": {e: lecture_temoins({e: n}, temoins, doublons_par_juge, plan["cles"])["temoins_ok"]
                                        for e, n in notes_par_juge.items()},
                "auto_preference": lecture_auto_preference(notes_par_juge, modele_par_juge, plan["modele_par_auteur"]),
                "longueur_temoins_contre_fiches": _longueurs_temoins(plan["fiches"], temoins),
                "juges_rendus": len(notes_par_juge), "modele_servi_par_juge": journal["modele_servi_par_juge"],
                "bascules": [{k: b.get(k) for k in ("etiquette", "modele_declare", "modele_repli", "modele_servi")}
                             for b in journal["bascules"]],
                "regle": "mode « juges seulement » (R-805) : fiches validées d'une course arrêtée, mêmes consignes, mêmes témoins ; "
                         "agrégat nommé (moyenne à deux juges, médiane au-delà) ; un témoin échoué chez un juge rend L2 et L4 "
                         "illisibles"}
        classement, lecture = _classer(notes_par_juge, plan["par_ident"], temoins, base)
        lecture["lisible_L2_L4"] = lt["temoins_ok"]
        os.makedirs(os.path.join(sortie, "noyau"), exist_ok=True)
        ecrire_json_scelle(os.path.join(sortie, "noyau", "cles-anonymisation-par-juge.json"), plan["cles"])
        ecrire_json_scelle(os.path.join(sortie, "noyau", "temoins-servis.json"), temoins)
        ecrire_json_scelle(os.path.join(sortie, "noyau", "modeles.json"),
                           {"par_auteur": plan["modele_par_auteur"], "par_juge": journal["modele_servi_par_juge"]})
        ecrire_json_scelle(os.path.join(sortie, "notes-par-juge.json"), notes_par_juge)
        ecrire_json_scelle(os.path.join(sortie, "doublons-par-juge.json"), doublons_par_juge)
        ecrire_json_scelle(os.path.join(sortie, "classements-par-juge.json"), lecture.pop("_classements_par_juge"))
        ecrire_json_scelle(os.path.join(sortie, "classement.json"), {"lisible_L2_L4": lecture["lisible_L2_L4"],
                                                                     "lignes": classement})
        ecrire_json_scelle(os.path.join(sortie, "lecture.json"), lecture)
        journal["statut"] = {"statut": "ok", "lisible_L2_L4": lecture["lisible_L2_L4"]}
        resultat.update({"classement": classement, "lecture": lecture, "lisible": lecture["lisible_L2_L4"]})
        return resultat
    except BaseException as exc:
        erreur = journal["arret"] or (type(exc).__name__ + " : " + caviarder(str(exc))[0][:500])
        journal["arret"] = erreur
        if not journal["statut"]:
            journal["statut"] = {"statut": "erreur"}
        if notes_par_juge:  # notes déjà rendues : gardées, scellées, jamais agrégées sans tous les juges
            ecrire_json_scelle(os.path.join(sortie, "notes-par-juge-partielles.json"), notes_par_juge)
        raise
    finally:
        ecrire_json_scelle(os.path.join(sortie, "manifeste-fin-juges.json"), manifeste(
            phase="fin-juges-seulement", mode=VERSION_MODE, horodatage=horodatage, moteur=moteur, journal=journal,
            erreur=erreur, statut=journal["statut"], bascules=journal["bascules"], refus_modele=journal["refus_modele"],
            modele_servi_par_juge=journal["modele_servi_par_juge"],
            depense_modele_non_autorise_usd=journal["depense_modele_non_autorise_usd"],
            lisible_L2_L4=resultat["lisible"], nombre_lignes_classement=len(resultat["classement"] or [])))
        ecrire_empreintes_sortie(sortie)


def ecrire_empreintes_sortie(sortie):
    """La liste des empreintes de tous les fichiers de la sortie (format sha256sum), scellée ; écrite en dernier."""
    lignes = []
    for racine, dossiers, fichiers in os.walk(sortie):
        dossiers.sort()
        for nom in sorted(fichiers):
            chemin = os.path.join(racine, nom)
            rel = os.path.relpath(chemin, sortie)
            if rel in ("empreintes-sortie.txt", "empreintes-sortie.txt.sha256") or os.path.islink(chemin):
                continue
            lignes.append(f"{sha256_fichier(chemin)}  {rel}")
    return ecrire_scelle(os.path.join(sortie, "empreintes-sortie.txt"), "\n".join(lignes) + "\n")


__all__ = ["CRITERES", "JugesSeulementRefuse", "executer_juges_seulement", "lire_course_arretee", "preparer_juges_seulement",
           "refus_dit_par_le_modele", "resume_du_plan", "verifier_relais_juges"]
