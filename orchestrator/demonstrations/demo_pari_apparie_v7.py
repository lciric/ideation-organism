"""Le pari apparié borné de bout en bout (v7, version 30) — zéro dépense, aucun agent : une **banque de scores**
synthétique (unités à effet aléatoire partagé entre sabotés et honnêtes d'une même unité ; sept cellules : `blanc`,
`blanc_jumeau` (même loi que `blanc`), `cascade` (ii), `dernier_etat` (iii), `noir_action`, `noir_sequentiel`, `juge`),
un **proposeur mécanique** de contrastes (témoins plantés vrais à quatre forces, faux « nul exact » et « signe inversé »,
contrastes tirés au hasard à vérité connue, et une fiche « G1 » en intersection-union contre les cinq comparateurs avec
garde), des **engagements** scellés sur le seul calibrage, une **Course** sous D-S25 bis : une tranche d'épreuve
**fraîche** par génération (identifiants d'unités, intersection refusée), budgets D-S24 (α / G_max par génération,
α_c / m_c par fiche, gardé à vie), abandons sous contrat (après partie, avant partie), déclaration « sans partie »
confrontée au **journal des parties** (K8-2), **lignées de clé** (D-S25 bis (5) : une affirmation, une fiche), et la
lecture L1 / L2 / L3 fixée ici, avant la course :

- **L1** validité : aucune fiche d'**espérance conditionnelle aux seuils scellés** ≤ 0 promue (K9-7 : la vérité d'un
  contraste se calcule ici analytiquement, cellule par cellule, au seuil scellé — pas « par construction » : deux cellules
  de même loi ont des seuils scellés différents, le « faux nul » peut être vrai conditionnellement) ; le témoin « faux
  nul » est rapporté comme **contrôle 12** (« calibrage insuffisant » s'il est promu), pas comme une violation ;
- **L2** dents : quels décalages de loi de témoin vrai sont promus, et à quelle génération (un décalage 0,5 ≈ 14 points
  de rappel au seuil τ = 0,05, K9-10 e) ;
- **L3** la fiche de **forme G1** (intersection-union contre cinq comparateurs, cinq gardes), lue **dans la course du
  pôle** par e-BH pondéré — ce n'est pas la lecture de G1 (une fois, hors de la suite, N-050) : la sortie par
  **e-Bonferroni** (ce qui sort du pôle, D-S25 bis (6)) est rapportée à côté ; les richesses par comparateur sont
  **descriptives** (K9-8).

`--nul R` : la même course, R fois, sur des banques **nulles** (toutes les cellules de même loi) : part des répétitions
avec au moins une promotion, à comparer à α (garantie de D-S25 bis sur l'union des promotions) ; artefacts (R5) :
relecture d'une tranche (refusée), tranche d'une génération antérieure lue par une autre fiche (refusée, K9-1), « sans
partie » mensonger (refusé par le journal), relance sous un autre nom (refusée), partie d'une autre clé (refusée, K9-2).
Version 28 : plan des tranches scellé dans chaque engagement, ordre dérivé de l'empreinte et de la génération, journal
tenu par `evaluer`, décisions « avant partie » prises avant toute issue de la génération (K9-10 b).

Usage : python -I -B demonstrations/demo_pari_apparie_v7.py DOSSIER_NEUF [--generations 4] [--unites-par-tranche 40]
        [--graine 20261028] [--alpha 0.05] [--nul 200]
"""

import argparse
import math
import os
import random
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole import engagement_apparie as ea  # noqa: E402
from pole import monde_banque_scores as mbs  # noqa: E402
from pole import pari_apparie as pa  # noqa: E402
from pole.outils import ecrire_json_scelle, graine_derivee  # noqa: E402

CELLULES = ("blanc", "blanc_jumeau", "cascade", "dernier_etat", "noir_action", "noir_sequentiel", "juge")
# décalage de la loi des sabotés par cellule (honnêtes : 0 partout) ; `blanc_jumeau` = `blanc` (nul exact)
DECALAGES = {"blanc": 1.5, "blanc_jumeau": 1.5, "cascade": 1.0, "dernier_etat": 0.9, "noir_action": 0.5,
             "noir_sequentiel": 0.7, "juge": 0.3}
COMPARATEURS_G1 = ("cascade", "dernier_etat", "noir_action", "noir_sequentiel", "juge")
MODES = ("diffus", "concentre")


def banque(rng, tranches, unites_par_tranche, calibrage=60, developpement=0, sabotes=8, honnetes=8, sigma_unite=0.6,
           nul=False):
    """Épisodes avec un effet d'unité partagé (les instances d'une unité ne sont pas indépendantes, D-S1) ; les unités
    d'épreuve portent leur tranche dans `strates["tranche"]` ; la tranche 1 ne contient que le mode « diffus » (pour
    exercer la déclaration « sans partie » d'une fiche stratifiée « concentré »)."""
    dec = {c: (0.0 if nul else d) for c, d in DECALAGES.items()}
    episodes = []

    def ajouter(partie, unite, mode, tranche, avec_sabotes):
        eta = rng.gauss(0, sigma_unite)
        for etiquette, nombre in (("sabote", sabotes if avec_sabotes else 0), ("honnete", honnetes)):
            for k in range(nombre):
                scores = {c: eta + (dec[c] if etiquette == "sabote" else 0.0) + rng.gauss(0, 1) for c in CELLULES}
                episodes.append({"id": f"{unite}-{etiquette}-{k}", "unite": unite, "etiquette": etiquette, "partie": partie,
                                 "strates": {"mode": mode, "tranche": str(tranche)}, "scores": scores})

    for u in range(calibrage):
        ajouter("calibrage", f"cal-{u}", MODES[u % 2], 0, False)
    for u in range(developpement):
        ajouter("developpement", f"dev-{u}", MODES[u % 2], 0, True)
    for t in range(1, tranches + 1):
        for u in range(unites_par_tranche):
            mode = "diffus" if t == 1 else MODES[u % 2]
            ajouter("epreuve", f"epr-{t}-{u}", mode, t, True)
    return {"identite": f"demo-pari-apparie-v7-{tranches}x{unites_par_tranche}{'-nul' if nul else ''}", "cellules": list(CELLULES),
            "strates": ["mode", "tranche"], "episodes": episodes}


def esperance_connue(coefficients, constante=0.0):
    """Signe en **population** (seuils à τ exacts, cellules de même variance) : Σ a_c · décalage_c + a₀ ; vrai pour des paires
    ±1 seulement (K9-7). La vérité de L1 est `esperance_conditionnelle`, aux seuils scellés."""
    return sum(a * DECALAGES[c] for c, a in coefficients.items()) + constante


def esperance_conditionnelle(coefficients, seuils, constante=0.0, sigma_unite=0.6, nul=False, strate=None):
    """Espérance du contraste **conditionnelle aux seuils scellés** s_c (K9-7) : la part d'une cellule c chez les sabotés
    d'une unité vaut en espérance P(η + d_c + ε > s_c) = Φ((d_c − s_c) / √(1 + σ_u²)) (effet d'unité η ~ N(0, σ_u²), bruit
    ε ~ N(0, 1), décalage d_c des sabotés ; la strate ne change pas la loi des scores dans cette banque)."""
    import statistics
    phi = statistics.NormalDist(0.0, math.sqrt(1.0 + sigma_unite ** 2))
    v = constante
    for c, a in coefficients.items():
        d = 0.0 if nul else DECALAGES[c]
        v += a * (1.0 - phi.cdf(seuils[c] - d))
    return v


def propositions(rng, generation, n_hasard):
    """Les fiches de la génération : témoins plantés en génération 1, contrastes au hasard ensuite (vérité connue)."""
    fiches = {}
    if generation == 1:
        fiches["temoin-vrai-fort"] = {"coefficients": {"blanc": 1, "juge": -1}}          # écart 1,2
        fiches["temoin-vrai-moyen"] = {"coefficients": {"blanc": 1, "noir_action": -1}}   # écart 1,0
        fiches["temoin-vrai-faible"] = {"coefficients": {"blanc": 1, "cascade": -1}}      # écart 0,5
        fiches["temoin-vrai-tenu"] = {"coefficients": {"cascade": 1, "dernier_etat": -1}}  # écart 0,1
        fiches["temoin-faux-nul"] = {"coefficients": {"blanc": 1, "blanc_jumeau": -1}}    # nul exact
        fiches["temoin-faux-inverse"] = {"coefficients": {"juge": 1, "blanc": -1}}        # signe inversé
        fiches["temoin-vrai-concentre"] = {"coefficients": {"blanc": 1, "noir_sequentiel": -1}, "strate": {"mode": "concentre"}}
    for k in range(n_hasard):
        a, b = rng.sample(CELLULES, 2)
        fiches[f"hasard-g{generation}-{k}"] = {"coefficients": {a: 1, b: -1}}
    return fiches


def fiche_forme_g1():
    """Forme de G1 : intersection-union du blanc contre cinq comparateurs, **une garde par comparateur** (K9-9)."""
    return {"coefficients_par_comparateur": {c: {"blanc": 1, c: -1} for c in COMPARATEURS_G1},
            "garde": [{"a": "blanc", "b": c, "delta": 0.10} for c in COMPARATEURS_G1]}


def unites_de_tranche(monde, t):
    return sorted({e["unite"] for e in monde.episodes("epreuve", None, {"tranche": str(t)})})


def plan_des_tranches(monde, generations):
    """Le plan scellé (K9-5) : la tranche g = les unités d'épreuve de strate `tranche` = g — dérivé de la banque, jamais des scores."""
    return {g: unites_de_tranche(monde, g) for g in range(1, generations + 1)}


def construire_engagement(monde, nom, fiche, tau, alpha_c, m_c, plan, partie="epreuve"):
    if "coefficients_par_comparateur" in fiche:
        contrastes = {c: {"coefficients": k} for c, k in fiche["coefficients_par_comparateur"].items()}
        return ea.construire(monde, contrastes, tau, alpha_c=alpha_c, m_c=m_c, partie=partie, garde=fiche.get("garde"),
                             plan_tranches=plan)
    return ea.construire(monde, {nom: {"coefficients": fiche["coefficients"]}}, tau, alpha_c=alpha_c, m_c=m_c,
                         partie=partie, strate=fiche.get("strate"), plan_tranches=plan)


def verite_conditionnelle(nom, fiche, engagement, nul=False):
    """Espérance conditionnelle aux seuils scellés de l'engagement ; pour une forme G1, le minimum sur les comparateurs."""
    seuils = engagement["cle_heritage"]["seuils"]
    if "coefficients_par_comparateur" in fiche:
        return min(esperance_conditionnelle(k, seuils, nul=nul) for k in fiche["coefficients_par_comparateur"].values())
    return esperance_conditionnelle(fiche["coefficients"], seuils, nul=nul)


def course(monde, generations, alpha, tau, graine, n_hasard=6, avec_g1=True, seuil_abandon_log=-1.0, nul=False):
    """La course entière ; renvoie le journal (par génération) et l'état final. D-S24 : α_g = α / G_max. Version 29 : chaque
    génération est jouée par `engagement_apparie.jouer_generation` — l'orchestrateur (cette fonction) décide **avant** toute
    issue qui est abandonné ou non lancé, puis ne reçoit qu'un compte rendu, jamais une trajectoire (K10-1, K10-2)."""
    rng = random.Random(graine_derivee(graine, "proposeur"))
    lignees = ea.Lignees()
    c = pa.Course(alpha=alpha, journal=lignees)
    plan = plan_des_tranches(monde, generations)
    engagements, verites, verites_population, journal = {}, {}, {}, []
    alpha_g = alpha / generations
    for g in range(1, generations + 1):
        nouvelles = propositions(rng, g, n_hasard)
        if g == 1 and avec_g1:
            nouvelles["forme-G1"] = fiche_forme_g1()
        # la mémoire refuse les redécouvertes (K9-3, K10-6) : une proposition qui porte la même **affirmation** qu'une fiche
        # entrée n'entre pas ; m_c compte les fiches réellement entrées
        redites = []
        for nom, fiche in list(nouvelles.items()):
            essai = construire_engagement(monde, nom, fiche, tau, alpha_g, 1, plan)
            aff = essai["empreinte_affirmation"]
            if aff in lignees.proprietaire or any(e["empreinte_affirmation"] == aff for n, e in engagements.items() if n in nouvelles):
                redites.append((nom, lignees.proprietaire.get(aff, "proposition jumelle de la même génération")))
                del nouvelles[nom]
                continue
            engagements[nom] = essai  # provisoire (m_c = 1) ; reconstruit ci-dessous au vrai m_c
        m_c = len(nouvelles)
        for nom, fiche in nouvelles.items():
            engagements[nom] = construire_engagement(monde, nom, fiche, tau, alpha_g, m_c, plan)
            lignees.entrer(nom, engagements[nom])
            verites[nom] = verite_conditionnelle(nom, fiche, engagements[nom], nul=nul)
            if "coefficients_par_comparateur" in fiche:
                verites_population[nom] = min(esperance_connue(k) for k in fiche["coefficients_par_comparateur"].values())
            else:
                verites_population[nom] = esperance_connue(fiche["coefficients"])
        if nouvelles:  # une génération sans fiche nouvelle (toutes redites) n'entre aucune famille : son α_g reste non dépensé
            c.entrer(f"g{g}", list(nouvelles), alpha_g, cles={n: engagements[n]["empreinte_cle"] for n in nouvelles})
        # décisions **avant toute issue de la génération** (K9-10 b, K10-2) : en génération 2, le proposeur retire le témoin
        # inversé (mode `avant_partie` du contrat de D-S25 bis (2) ; sa valeur gelée est celle d'après la partie de la génération 1)
        abandons_avant = {}
        if g == 2 and "temoin-faux-inverse" in c.budgets and "temoin-faux-inverse" not in c.gelees | c.promues | c.arretees:
            abandons_avant["temoin-faux-inverse"] = "retrait du proposeur avant toute issue de la génération"
        # règle d'abandon après partie du proposeur : ses contrastes au hasard seulement (les témoins et la forme G1 sont lus
        # jusqu'au bout : ce sont eux qu'on lit en L2 et L3)
        def abandon_apres(nom, valeur):
            return (f"log-richesse {valeur:.2f} < {seuil_abandon_log} après la partie" if nom.startswith("hasard-") and valeur < seuil_abandon_log else None)
        compte = ea.jouer_generation(c, monde, engagements, abandons_avant=abandons_avant, abandon_apres=abandon_apres)
        journal.append({"generation": g, "tranche_unites": len(plan[g]), "nouvelles": sorted(nouvelles), "redites_refusees": redites,
                        "alpha_g": alpha_g, "m_c": m_c, "parties": compte["parties"], "sans_partie": compte["sans_partie"],
                        "abandons": [(f, "avant_partie") for f in compte["abandons_avant"]] + [(f, "apres_partie") for f in compte["abandons_apres"]],
                        "promues": compte["promues"]})
    return {"journal": journal, "promues": sorted(c.promues), "bonferroni": sorted(c.bonferroni()), "verites": verites,
            "verites_population": verites_population, "cles": {n: e["empreinte_cle"] for n, e in engagements.items()},
            "affirmations": {n: e["empreinte_affirmation"] for n, e in engagements.items()},
            "log_e": dict(c.log_e), "seuils_log": {f: c.seuil_log(f) for f in c.budgets}, "gelees": sorted(c.gelees),
            "abandons": {str(k): v for k, v in c.abandons.items()}, "sans_partie": {str(k): v for k, v in c.sans_partie.items()},
            "journal_parties": [{k: v for k, v in j.items() if k != "identifiants_unites"} for j in lignees.journal], "alpha_engage": c.alpha_engage}


def lecture(etat):
    promues, verites, pop = etat["promues"], etat["verites"], etat["verites_population"]
    fausses = sorted(f for f in promues if verites[f] <= 1e-12)
    temoins_vrais = {f: v for f, v in verites.items() if f.startswith("temoin-vrai")}
    par_generation = {f: g["generation"] for g in etat["journal"] for f in g["promues"]}
    bonf = set(etat["bonferroni"])
    g1 = {}
    if "forme-G1" in verites:
        derniere = next((g["parties"]["forme-G1"] for g in reversed(etat["journal"]) if "forme-G1" in g["parties"]), None)
        parties_g1 = [(g["generation"], g["parties"]["forme-G1"]) for g in etat["journal"] if "forme-G1" in g["parties"]]
        # K10-8 : par partie, le processus qui fixe le minimum (contraste ou garde) est rapporté
        minima = []
        for gen, pg in parties_g1:
            candidats = dict(pg["log_richesse_finale_par_comparateur"]); candidats.update({f"garde:{k}": v for k, v in (pg.get("log_gardes_finales") or {}).items() if v is not None})
            minima.append({"generation": gen, "processus_minimal": min(candidats, key=candidats.get), "valeur": min(candidats.values()),
                           "gardes": pg.get("log_gardes_finales"), "contrastes": pg["log_richesse_finale_par_comparateur"]})
        g1 = {"promue_dans_la_course_eBH": "forme-G1" in promues, "generation": par_generation.get("forme-G1"),
              "sortie_e_bonferroni": "forme-G1" in bonf, "log_e_final": etat["log_e"]["forme-G1"],
              "seuil_log_fiche_seule": etat["seuils_log"]["forme-G1"], "parties": minima,
              "note": "lecture dans la course du pôle (e-BH pondéré) ; la lecture de G1 se fait une fois, hors de la suite (N-050) ; "
                      "ce qui sort du pôle se lit par e-Bonferroni ; richesses des contrastes et des gardes par partie, descriptives ; "
                      "le processus minimal (souvent une garde, K10-8) fixe l'e-valeur"}
    controle_12 = {f: {"promue": f in promues, "esperance_conditionnelle": verites[f], "esperance_population": pop[f]}
                   for f in verites if f.startswith("temoin-faux-nul")}
    return {"L1_validite": {"tenue": not fausses, "promues_d_esperance_conditionnelle_nulle_ou_negative": fausses,
                            "definition": "vérité = espérance conditionnelle aux seuils scellés (K9-7)"},
            "controle_12_calibrage": {**controle_12, "lecture": ("calibrage insuffisant : le jumeau de même loi est promu" if any(d["promue"] for d in controle_12.values())
                                                                 else "jumeau non promu")},
            "L2_dents": {f: {"esperance_conditionnelle": v, "esperance_population": pop[f], "promue": f in promues,
                             "sortie_e_bonferroni": f in bonf, "generation": par_generation.get(f),
                             "log_e_final": etat["log_e"][f]} for f, v in sorted(temoins_vrais.items())},
            "L3_forme_G1": g1, "promues": promues, "bonferroni": etat["bonferroni"],
            "affirmations_distinctes": len(set(etat["affirmations"].values())), "fiches": len(etat["affirmations"])}


def artefacts(monde, alpha, tau, graine):
    """R5 : chaque garde sur un cas sain et sur un artefact — sept refus attendus (version 30)."""
    sortie = {}
    plan = plan_des_tranches(monde, 2)
    e = construire_engagement(monde, "x", {"coefficients": {"blanc": 1, "juge": -1}}, tau, alpha / 4, 1, plan)
    e_y = construire_engagement(monde, "y", {"coefficients": {"blanc": 1, "noir_action": -1}}, tau, alpha / 4, 1, plan)
    # (A) fraîcheur, course sans journal (pour isoler les gardes de fraîcheur)
    c = pa.Course(alpha=alpha, essai=True)  # (A) : course d'essai sans journal, pour isoler les gardes de fraîcheur
    c.entrer("a", ["x", "y"], alpha / 2, cles={"x": e["empreinte_cle"], "y": e_y["empreinte_cle"]})
    r1 = ea.evaluer(monde, e, generation=1, essai=True)
    c.ajouter_trajectoire("x", r1["trajectoire_log_min"], unites=r1["identifiants_unites"], empreinte_cle=r1["empreinte_cle"])
    ry = ea.evaluer(monde, e_y, generation=1, essai=True)  # cas sain : y lit la même tranche dans la même génération
    c.ajouter_trajectoire("y", ry["trajectoire_log_min"], unites=ry["identifiants_unites"], empreinte_cle=ry["empreinte_cle"])
    c.lire()
    try:  # artefact 1 : la même fiche relit la tranche 1 en génération 2
        c.ajouter_trajectoire("x", r1["trajectoire_log_min"], unites=r1["identifiants_unites"], empreinte_cle=r1["empreinte_cle"])
        sortie["relecture_tranche"] = "ACCEPTÉE — artefact non détecté"
    except ValueError as err:
        sortie["relecture_tranche"] = f"refusée : {err}"
    # artefact 2 (K9-1) : une fiche nouvelle lit en génération 2 des unités que la course a lues en génération 1
    e_z = construire_engagement(monde, "z", {"coefficients": {"blanc": 1, "cascade": -1}}, tau, alpha / 4, 1, {1: plan[2], 2: plan[1]})
    c.entrer("b", ["z"], alpha / 4, cles={"z": e_z["empreinte_cle"]})
    rz = ea.evaluer(monde, e_z, generation=2, essai=True)  # son plan met les unités physiques de la tranche 1 en génération 2
    try:
        c.ajouter_trajectoire("z", rz["trajectoire_log_min"], unites=rz["identifiants_unites"], empreinte_cle=rz["empreinte_cle"])
        sortie["tranche_anterieure_par_autre_fiche"] = "ACCEPTÉE — artefact non détecté"
    except ValueError as err:
        sortie["tranche_anterieure_par_autre_fiche"] = f"refusée : {err}"
    # (B) journal et clés
    lg = ea.Lignees()
    cj = pa.Course(alpha=alpha, journal=lg)
    lg.entrer("x", e); lg.entrer("y", e_y)
    cj.entrer("a", ["x", "y"], alpha / 2, cles={"x": e["empreinte_cle"], "y": e_y["empreinte_cle"]})
    rj = ea.evaluer(monde, e, generation=1, fiche="x", journal=lg)
    cj.ajouter_trajectoire("x", rj["trajectoire_log_min"], unites=rj["identifiants_unites"], empreinte_cle=rj["empreinte_cle"], empreinte_unites=rj["empreinte_unites"])
    try:  # artefact 3 (K8-2, K9-6) : « sans partie » pour y alors que sa partie de la génération 1 a été calculée (journalisée)
        ea.evaluer(monde, e_y, generation=1, fiche="y", journal=lg)
        cj.lire(sans_partie={"y": "prétendue absence"})
        sortie["sans_partie_mensonger"] = "ACCEPTÉ — artefact non détecté"
    except ValueError as err:
        sortie["sans_partie_mensonger"] = f"refusé : {err}"
    try:  # artefact 4 (K9-3) : relance sous un autre nom (même affirmation, même clé canonique, autre ordre des cellules)
        lg.entrer("x-bis", construire_engagement(monde, "x-bis", {"coefficients": {"juge": -1, "blanc": 1}}, tau, alpha / 4, 1, plan))
        sortie["relance_sous_autre_nom"] = "ACCEPTÉE — artefact non détecté"
    except ea.EngagementInvalide as err:
        sortie["relance_sous_autre_nom"] = f"refusée : {err}"
    try:  # artefact 5 (K9-2) : partie d'une autre clé (τ changé) ajoutée à la fiche x
        e_tau = ea.construire(monde, {"x": {"coefficients": {"blanc": 1, "juge": -1}}}, 0.10, alpha_c=alpha / 4, m_c=1, plan_tranches=plan)
        rt = ea.evaluer(monde, e_tau, generation=1, essai=True)
        c.ajouter_trajectoire("y", rt["trajectoire_log_min"], unites=rt["identifiants_unites"], empreinte_cle=rt["empreinte_cle"])
        sortie["partie_d_une_autre_cle"] = "ACCEPTÉE — artefact non détecté"
    except ValueError as err:
        sortie["partie_d_une_autre_cle"] = f"refusée : {err}"
    try:  # artefact 6 (K10-6, K10-2) : « fiche espionne » = même affirmation sous une autre population → refusée par la mémoire
        lg.entrer("espion", ea.construire(monde, {"x": {"coefficients": {"blanc": 1, "juge": -1}}}, tau, alpha_c=alpha / 4, m_c=1, plan_tranches=plan, population="autre"))
        sortie["fiche_espionne_autre_population"] = "ACCEPTÉE — artefact non détecté"
    except ea.EngagementInvalide as err:
        sortie["fiche_espionne_autre_population"] = f"refusée : {err}"
    try:  # artefact 7 (K10-7) : course sans journal en production → refusée
        pa.Course(alpha=alpha)
        sortie["course_sans_journal"] = "ACCEPTÉE — artefact non détecté"
    except ValueError as err:
        sortie["course_sans_journal"] = f"refusée : {err}"
    sortie["cas_sains"] = {"tranche_partagee": "deux fiches lisent la tranche 1 en génération 1 : accepté",
                           "relecture_tranche": "la première partie est acceptée", "sans_partie": "les déclarations vraies de la course de démonstration sont acceptées",
                           "relance": "la fiche d'origine garde sa clé", "cle": "la partie de la bonne clé est acceptée"}
    return sortie


def repetitions_nulles(args):
    """Garantie sous le nul complet : part des répétitions avec au moins une promotion (et au moins une fiche au seuil
    de Bonferroni), avec un intervalle de Clopper-Pearson approché par Wilson."""
    au_moins_une, bonf = 0, 0
    for k in range(args.nul):
        rng = random.Random(graine_derivee(args.graine, "nul", k))
        b = banque(rng, args.generations, args.unites_par_tranche, nul=True)
        monde = mbs.MondeBanqueScores(b, graine_derivee(args.graine, "monde-nul", k))
        etat = course(monde, args.generations, args.alpha, args.tau, graine_derivee(args.graine, "course-nul", k),
                      avec_g1=True, nul=True)
        au_moins_une += bool(etat["promues"])
        bonf += bool(etat["bonferroni"])
    n = args.nul
    p = au_moins_une / n
    z = 1.96
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return {"repetitions": n, "au_moins_une_promotion": au_moins_une, "part": p, "wilson_95": [centre - demi, centre + demi],
            "au_moins_une_bonferroni": bonf, "alpha": args.alpha,
            "lecture": ("tenue" if centre + demi >= args.alpha and p <= args.alpha else
                        ("tenue (part sous α)" if p <= args.alpha else "ROMPUE : part > α"))}


def principal():
    a = argparse.ArgumentParser()
    a.add_argument("dossier")
    a.add_argument("--generations", type=int, default=4)
    a.add_argument("--unites-par-tranche", type=int, default=40)
    a.add_argument("--graine", type=int, default=20261028)
    a.add_argument("--alpha", type=float, default=0.05)
    a.add_argument("--tau", type=float, default=0.05)
    a.add_argument("--hasard", type=int, default=6)
    a.add_argument("--nul", type=int, default=0)
    args = a.parse_args()
    if os.path.exists(args.dossier):
        raise SystemExit(f"dossier existant : {args.dossier} (R12 : jamais d'écrasement)")
    os.makedirs(args.dossier)
    rng = random.Random(graine_derivee(args.graine, "banque"))
    b = banque(rng, args.generations, args.unites_par_tranche)
    monde = mbs.MondeBanqueScores(b, graine_derivee(args.graine, "monde"))
    ecrire_json_scelle(os.path.join(args.dossier, "banque.json"), b)
    etat = course(monde, args.generations, args.alpha, args.tau, graine_derivee(args.graine, "course"), n_hasard=args.hasard)
    lec = lecture(etat)
    lec["artefacts_R5"] = artefacts(monde, args.alpha, args.tau, args.graine)
    if args.nul:
        lec["nul_repete"] = repetitions_nulles(args)
    lec["reglages"] = {k: v for k, v in vars(args).items()}
    lec["banque"] = monde.description_publique()
    ecrire_json_scelle(os.path.join(args.dossier, "course.json"), etat)
    ecrire_json_scelle(os.path.join(args.dossier, "lecture-pari-apparie.json"), lec)
    print("L1 validité (espérance conditionnelle aux seuils scellés) :", "tenue" if lec["L1_validite"]["tenue"] else f"ROMPUE {lec['L1_validite']['promues_d_esperance_conditionnelle_nulle_ou_negative']}")
    print("contrôle 12 :", lec["controle_12_calibrage"]["lecture"])
    for f, d in lec["L2_dents"].items():
        print(f"L2 {f:24s} esp. cond. {d['esperance_conditionnelle']:+.3f} (pop. {d['esperance_population']:+.2f})  {'promue g' + str(d['generation']) if d['promue'] else 'non promue':14s} "
              f"Bonferroni {'oui' if d['sortie_e_bonferroni'] else 'non'}  log e {d['log_e_final']:+.2f}")
    if lec["L3_forme_G1"]:
        g = lec["L3_forme_G1"]
        print(f"L3 forme G1 : e-BH dans la course {'promue g' + str(g['generation']) if g['promue_dans_la_course_eBH'] else 'non promue'} ; "
              f"sortie e-Bonferroni : {'oui' if g['sortie_e_bonferroni'] else 'non'} ; log e {g['log_e_final']:+.2f} / seuil fiche seule {g['seuil_log_fiche_seule']:.2f} ; "
              f"processus minimal par partie : {[p['processus_minimal'] for p in g['parties']]}")
    print("promues :", lec["promues"], "; Bonferroni :", lec["bonferroni"], f"; {lec['fiches']} fiches, {lec['affirmations_distinctes']} affirmations")
    for k, v in lec["artefacts_R5"].items():
        if k != "cas_sains":
            print(f"artefact {k} : {v[:70]}")
    if args.nul:
        n = lec["nul_repete"]
        print(f"nul × {n['repetitions']} : au moins une promotion dans {n['au_moins_une_promotion']} ({n['part']:.3f} ; Wilson "
              f"[{n['wilson_95'][0]:.3f} ; {n['wilson_95'][1]:.3f}]) ; α = {n['alpha']} → {n['lecture']}")


if __name__ == "__main__":
    principal()
