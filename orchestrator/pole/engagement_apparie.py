"""Engagement « apparié » (v7, versions 23, 25 à 30) — la fiche du pari apparié borné, de bout en bout hors du cycle : construite
et scellée avant toute issue d'épreuve, puis jugée sur la banque de scores (conception v2 § 7 point 1 ; v3 à v6).

`construire(monde, ...)` fixe, **avant** toute lecture de l'épreuve : les contrastes nommés (coefficients vérifiés par la
règle double), τ, la strate, la partie lue, m_max (plafond, D-S27), la garde (cellules A et B, δ), le budget d'entrée
(α_c, m_c ; D-S25 bis), les **seuils**, calculés sur le seul calibrage, et la **clé de l'héritage** (D-S18 : contrastes et
coefficients ; pondération et m_max ; τ ; strate ; comparateurs ; seuils scellés ; population = empreinte de la banque ou
vivier déclaré ; plus la garde). L'empreinte de l'engagement fixe l'ordre secret de lecture.

`evaluer(monde, engagement)` lit la partie d'épreuve : parts, contrastes dans l'ordre secret, garde, e-valeur du minimum
des processus arrêtée au seuil m_c/α_c (`pari_apparie.evaluer`), bornes basses rapportées (jamais une condition).

Version 25 (contre-lecture de la conception v7) : la **partie lue** et la grille **Λ** entrent dans la clé de l'héritage
(K7-3) ; `evaluer` rend les **identifiants des unités lues** (banque, partie, unité) et leur empreinte, à passer à
`Course.ajouter_trajectoire(unites=…)` qui refuse toute intersection (K7-2, K8-1 : fraîcheur, pas seulement répétition). Restent à la charge de l'orchestrateur : consigner
l'empreinte de l'engagement **hors de l'objet** (journal, mémoire) avant l'épreuve — le scellement détecte une altération,
il ne l'empêche pas (K7-4) ; et, tant que la garde et les contrastes ne portent pas sur les mêmes unités, les processus
sont alignés par rang et non par unité (K7-6 : niveau tenu, espérance au franchissement joint non garantie ≤ 1).

Version 28 (contre-lecture de la conception v9, K9-1 à K9-6, K9-9) : la clé est **canonique** (contrastes par cellules et
coefficients triés, sans nom libre : renommer un contraste ne fait pas une autre affirmation, K9-3), elle porte la
**version de l'e-processus** (K8-4, K9-4) et le **plan des tranches** (unités par génération, scellé avec l'engagement,
dérivé de la banque et jamais des scores, K9-5) ; `evaluer(monde, engagement, generation=g, fiche=…, journal=…)` lit la
tranche de la génération dans l'ordre dérivé de l'empreinte et de la génération (plus d'étiquette libre), **journalise
lui-même** la partie (K9-6) ; plusieurs gardes, une par comparateur (K9-9) ; identifiants d'unités par l'**identité** de la
banque (K9-2) ; `Lignees` refuse aussi une seconde clé pour une fiche.

Version 29 (contre-lecture de la conception v10, K10-1 à K10-10) : la clé est **en deux parties** — `affirmation` (contrastes
canoniques, τ, strate, seuils, comparateurs, gardes) et `lecture` (partie, plan des tranches, population, m_max, Λ,
e-processus) ; `Lignees` tient « une affirmation, une fiche » sur l'**empreinte de l'affirmation** (K10-6 : un plan ou une
population différents ne font pas une autre affirmation) ; l'**ordre secret** dérive de l'empreinte de la clé (jamais du nom,
du budget ou de l'empreinte de l'engagement), de la génération et de la graine scellée du monde (K10-3) ; le **journal** est
en lecture seule pour l'appelant (ajout seul, identifiants d'unités gardés, génération fournie par la course) (K10-4) ; une
partie **vide** est journalisée vide et vaut déclaration (K10-5) ; **`jouer_generation`** joue une génération entière sans
rendre une trajectoire à l'orchestrateur : les décisions « avant toute issue » (abandons, fiches non lancées) sont des
**entrées** de la fonction, prises avant qu'elle ne calcule quoi que ce soit (K10-1, K10-2). **Frontière de confiance (dite)** :
tant qu'une partie tient les scores d'épreuve, rien ne l'empêche de calculer en privé ; dans le pôle, le monde tient les
scores et la course les lit — l'orchestrateur reçoit des engagements et des verdicts, jamais la banque d'épreuve.

Version 30 (contre-lecture de la conception v11, K11-1 à K11-7) : `jouer_generation` calcule **toutes** les parties avant
d'appliquer la règle d'abandon « après partie » (qui ne voit donc aucune issue avant que toutes soient journalisées) et ne
laisse pas une exception au milieu sans trace : la génération est marquée **interrompue** au journal et la course refuse
la lecture jusqu'à ce que `jouer_generation` la reprenne (les parties déjà calculées restent au journal, jamais recalculées) ;
`evaluer` exige un journal hors `essai=True` ; le journal enregistre l'**empreinte de la trajectoire** et la clé (K11-3) ;
« le côté de confiance » est nommé : banque d'épreuve, monde et sa graine, course et journal, construction des engagements.
"""

from . import pari_apparie as pa
from .outils import empreinte_objet


class EngagementInvalide(ValueError):
    pass


def canonique(coefficients, constante):
    """Forme canonique d'un contraste (K9-3) : cellules triées, coefficients et constante arrondis à 1e-12 ; le nom n'y est pas."""
    return [[c, round(float(a), 12)] for c, a in sorted(coefficients.items())] + [["constante", round(float(constante), 12)]]


def construire(monde, contrastes, tau, alpha_c=0.05, m_c=1, strate=None, partie="epreuve", m_max=None, garde=None,
               population=None, plan_tranches=None):
    """`contrastes` : {nom: {"coefficients": {cellule: a}, "constante": a₀}} — l'affirmation « chaque contraste a une
    espérance > 0 » (intersection-union) ; `garde` : {"a": cellule, "b": cellule, "delta": δ}, ou une **liste** de telles
    gardes (une par comparateur, K9-9), ou None ; `plan_tranches` : {génération (entier) : [unités de la partie]} scellé
    avec l'engagement — tranches disjointes, dérivées de la banque et jamais des scores (K9-5) ; sans plan, la partie
    entière se lit en une fois."""
    if not contrastes:
        raise EngagementInvalide("au moins un contraste")
    if partie == "calibrage":
        raise EngagementInvalide("la partie de calibrage ne se lit jamais comme épreuve")
    cellules = set()
    propres, noms = {}, {}
    for nom, c in sorted(contrastes.items()):
        coefficients, constante = dict(c["coefficients"]), float(c.get("constante", 0.0))
        try:
            pa.verifier_coefficients(coefficients, constante)
        except pa.ContrasteInvalide as e:
            raise EngagementInvalide(f"contraste {nom!r} : {e}") from None
        inconnues = set(coefficients) - set(monde.cellules)
        if inconnues:
            raise EngagementInvalide(f"contraste {nom!r} : cellules inconnues {sorted(inconnues)}")
        cellules |= set(coefficients)
        forme = empreinte_objet(canonique(coefficients, constante))[:16]
        if forme in propres:
            raise EngagementInvalide(f"contraste {nom!r} : même affirmation que {noms[forme]!r} (K9-3)")
        propres[forme] = {"coefficients": coefficients, "constante": constante}
        noms[forme] = nom
    gardes = [] if garde is None else (list(garde) if isinstance(garde, (list, tuple)) else [garde])
    propres_gardes = []
    for g in gardes:
        if g.get("a") not in monde.cellules or g.get("b") not in monde.cellules or not 0.0 < g.get("delta", 0) < 1.0:
            raise EngagementInvalide("garde : cellules connues et δ dans ]0 ; 1[")
        cellules |= {g["a"], g["b"]}
        propres_gardes.append({"a": g["a"], "b": g["b"], "delta": float(g["delta"])})
    propres_gardes.sort(key=lambda g: (g["a"], g["b"], g["delta"]))
    garde = propres_gardes or None
    if plan_tranches is not None:
        if not plan_tranches or any(not isinstance(g, int) or g < 1 for g in plan_tranches):
            raise EngagementInvalide("plan des tranches : générations entières ≥ 1")
        toutes = set(monde.unites(partie))
        vues = set()
        for g, unites_g in plan_tranches.items():
            u = set(unites_g)
            if not u or u - toutes or u & vues:
                raise EngagementInvalide(f"plan des tranches : génération {g} vide, hors partie ou non disjointe")
            vues |= u
        plan_tranches = {str(g): sorted(plan_tranches[g]) for g in sorted(plan_tranches)}
    if not (isinstance(m_c, int) and m_c >= 1) or not 0.0 < alpha_c < 1.0:
        raise EngagementInvalide("budget d'entrée : m_c entier ≥ 1, α_c dans ]0 ; 1[")
    if m_max is not None and not (isinstance(m_max, int) and m_max >= 1):
        raise EngagementInvalide("m_max : entier ≥ 1")
    seuils = {c: monde.seuil(c, tau, strate) for c in sorted(cellules)}
    insuffisants = sorted(c for c, s in seuils.items() if s["calibrage_insuffisant"])
    if insuffisants:
        raise EngagementInvalide(f"calibrage insuffisant pour τ = {tau} : {insuffisants}")
    affirmation = {"contrastes": propres, "comparateurs": sorted(propres), "tau": tau, "strate": dict(sorted((strate or {}).items())),
                   "seuils": {c: s["seuil"] for c, s in seuils.items()}, "garde": garde}
    lecture = {"partie": partie, "plan_tranches": plan_tranches, "population": population or monde.identite,
               "ponderation": ("plafond" if m_max is not None else "par_unite"), "m_max": m_max, "lambdas": list(pa.LAMBDAS),
               "e_processus": dict(pa.E_PROCESSUS)}
    cle = {"affirmation": affirmation, "lecture": lecture,
           # champs à plat gardés pour la lecture (mêmes valeurs que ci-dessus)
           "contrastes": propres, "comparateurs": sorted(propres), "tau": tau, "strate": affirmation["strate"], "seuils": affirmation["seuils"],
           "garde": garde, "partie": partie, "plan_tranches": plan_tranches, "population": lecture["population"],
           "ponderation": lecture["ponderation"], "m_max": m_max, "lambdas": lecture["lambdas"], "e_processus": lecture["e_processus"]}
    engagement = {"type": "apparie", "cle_heritage": cle, "empreinte_cle": empreinte_objet(cle),
                  "empreinte_affirmation": empreinte_objet(affirmation), "partie": partie,
                  "alpha_c": alpha_c, "m_c": m_c, "seuils_detail": seuils, "monde": monde.empreinte, "noms": noms}
    engagement["empreinte"] = empreinte_objet(engagement)
    return engagement


def evaluer(monde, engagement, generation=None, fiche=None, journal=None, unites=None, essai=False):
    """Version 28 : la lecture d'une génération se fait par `generation=g` — la tranche est celle du **plan scellé** dans
    l'engagement (K9-5), l'ordre secret est dérivé de l'empreinte de l'engagement et de g (plus d'étiquette libre) ; sans
    plan, la partie entière est lue (génération None) ; `unites` n'est accepté que sans plan et avec une génération
    (tranche dérivée par l'orchestrateur de la banque, jamais des scores — à sa charge, dit). Avec `journal` (un
    `Lignees`), la partie est **journalisée ici même** sous le nom `fiche` (K9-6) ; une seconde évaluation d'une même fiche
    dans une génération est refusée par le journal."""
    if engagement.get("type") != "apparie" or engagement.get("empreinte") != empreinte_objet(
            {k: v for k, v in engagement.items() if k != "empreinte"}):
        raise EngagementInvalide("engagement altéré ou d'un autre type")
    if engagement["monde"] != monde.empreinte:
        raise EngagementInvalide("engagement scellé sur une autre banque")
    cle = engagement["cle_heritage"]
    plan = cle.get("plan_tranches")
    if plan is not None:
        if generation is None or unites is not None:
            raise EngagementInvalide("engagement à plan de tranches : passer generation=g, jamais d'unités libres (K9-5)")
        if str(generation) not in plan:
            raise EngagementInvalide(f"génération {generation} absente du plan des tranches")
        unites = plan[str(generation)]
    elif unites is not None:
        if generation is None:
            raise EngagementInvalide("une tranche libre demande sa génération (ordre dérivé de l'empreinte et de g)")
        absentes = set(unites) - set(monde.unites(engagement["partie"]))
        if absentes:
            raise EngagementInvalide(f"tranche : {len(absentes)} unité(s) hors de la partie {engagement['partie']!r} : "
                                     f"{sorted(map(str, absentes))[:3]}")
    if (journal is None) != (fiche is None):
        raise EngagementInvalide("journal et fiche vont ensemble (K9-6)")
    if journal is None and not essai:
        raise EngagementInvalide("évaluation sans journal : une partie calculée en privé n'est pas une partie du pôle (K10-1, K11-3) ; "
                                 "passer journal et fiche, ou essai=True pour un essai hors course")
    # K10-3 : l'ordre dérive de l'empreinte de la **clé** (ni nom, ni budget, ni empreinte de l'engagement) et de la génération
    etiquette = engagement["empreinte_cle"] if generation is None else f"{engagement['empreinte_cle']}|g{int(generation)}"
    parts = monde.parts(cle["seuils"], engagement["partie"], cle["strate"] or None, unites)
    ordre = monde.ordre_secret(parts, etiquette)
    valeurs = {nom: monde.contrastes(parts, c["coefficients"], c["constante"], ordre, cle["m_max"])
               for nom, c in cle["contrastes"].items()}
    if len({len(v) for v in valeurs.values()}) != 1:
        raise EngagementInvalide("contrastes sur des unités différentes")
    g, deltas = None, None
    if cle["garde"]:
        g = {f"{k['a']}-{k['b']}": monde.ecarts_faux_positifs(parts, k["a"], k["b"], ordre) for k in cle["garde"]}
        deltas = {f"{k['a']}-{k['b']}": k["delta"] for k in cle["garde"]}
    r = pa.evaluer(valeurs, ecarts_faux_positifs=g, delta=deltas, alpha=engagement["alpha_c"], m=engagement["m_c"])
    r["log_richesse_finale_par_comparateur"] = {engagement["noms"].get(k, k): v for k, v in r["log_richesse_finale_par_comparateur"].items()}
    r["bornes_basses"] = {engagement["noms"].get(nom, nom): pa.borne_basse(v) for nom, v in valeurs.items() if v}
    r["empreinte_cle"] = engagement["empreinte_cle"]
    r["unites_lues"] = len(ordre)
    # version 26 (K8-1) : les identifiants des unités (banque, partie, unité), à passer à `Course.ajouter_trajectoire(unites=…)`,
    # qui refuse toute intersection avec les unités déjà lues par la fiche ; l'empreinte reste pour le manifeste
    r["identifiants_unites"] = [(monde.identite, engagement["partie"], u) for u in sorted(ordre)]
    r["empreinte_unites"] = empreinte_objet({"banque": monde.identite, "partie": engagement["partie"],
                                             "unites": sorted(ordre)})
    r["empreinte_affirmation"] = engagement["empreinte_affirmation"]
    r["generation"] = generation
    if journal is not None:
        journal.journaliser(generation, fiche, r)
    return r


def jouer_generation(course, monde, engagements, abandons_avant=None, non_lancees=None, abandon_apres=None):
    """Version 29 (K10-1, K10-2, K10-5) : joue **une génération entière** de la course sans rendre une trajectoire à
    l'orchestrateur. `engagements` : {fiche: engagement} des fiches entrées. Les décisions « avant toute issue de la
    génération » sont des **entrées** : `abandons_avant` {fiche: motif} (abandon « avant partie », contrat de D-S25 bis (2)),
    `non_lancees` {fiche: motif} (déclaration « sans partie » décidée avant). Puis, pour chaque fiche active, la partie est
    calculée **ici**, journalisée par `evaluer` sous la génération de la course, et ajoutée ; une partie vide est journalisée
    vide et déclarée. `abandon_apres(fiche, valeur_log)` → motif ou None : abandon après la partie (permis par le contrat : la
    partie est déjà ajoutée). Enfin la lecture. Renvoie le compte rendu (sans trajectoire)."""
    g = course.generation
    journal = course.journal
    if journal is None:
        raise EngagementInvalide("jouer_generation demande une course avec journal")
    abandons_avant, non_lancees = dict(abandons_avant or {}), dict(non_lancees or {})
    compte = {"generation": g, "abandons_avant": {}, "non_lancees": {}, "parties": {}, "vides": {}, "abandons_apres": {}}
    for f, motif in abandons_avant.items():
        course.abandonner(f, avant_partie=True, motif=motif)
        compte["abandons_avant"][f] = motif
    actives = [f for f in course.budgets if f not in course.gelees and f not in course.promues and f not in course.arretees
               and f not in course.exclues]
    sans_partie = {}
    for f, motif in non_lancees.items():
        if f not in actives:
            raise EngagementInvalide(f"non-lancement de {f!r} : fiche non active")
        sans_partie[f] = motif
        compte["non_lancees"][f] = motif
    a_lire = [f for f in sorted(actives, key=str) if f not in sans_partie]
    # première passe (K11-1) : **toutes** les parties sont calculées, journalisées et ajoutées avant qu'aucune règle ne voie une
    # issue ; une partie déjà au journal pour cette génération (reprise après interruption) n'est pas recalculée
    valeurs = {}
    try:
        for f in a_lire:
            if f not in engagements:
                raise EngagementInvalide(f"fiche active sans engagement : {f!r}")
            deja = [j for j in journal.journal if j["generation"] == g and j["fiche"] == f]
            if deja and course.derniere_partie.get(f) == g:
                valeurs[f] = course.log_e[f]
                continue
            if deja:
                raise EngagementInvalide(f"fiche {f!r} : partie de la génération {g} au journal mais non ajoutée — génération interrompue "
                                         f"irrécupérable sans la trajectoire (K11-4) ; la fiche doit être retirée (D-S26 bis)")
            r = evaluer(monde, engagements[f], generation=g, fiche=f, journal=journal)
            if r["unites"] == 0:
                journal.marquer_vide(g, f)
                sans_partie[f] = "partie vide : aucune unité de la tranche dans la strate de la fiche (journalisée vide)"
                compte["vides"][f] = sans_partie[f]
                continue
            valeurs[f] = course.ajouter_trajectoire(f, r["trajectoire_log_min"], unites=r["identifiants_unites"],
                                                    empreinte_cle=r["empreinte_cle"], empreinte_unites=r["empreinte_unites"])
            compte["parties"][f] = {"unites": r["unites"], "log_e_valeur": valeurs[f], "arretee": f in course.arretees,
                                    "log_richesse_finale_par_comparateur": r["log_richesse_finale_par_comparateur"],
                                    "log_gardes_finales": r["log_gardes_finales"]}
    except Exception as e:
        journal.interrompre(g, f"{type(e).__name__}: {e}"[:200])
        raise
    # seconde passe : la règle d'abandon « après partie » ne voit les issues qu'une fois toutes les parties ajoutées
    if abandon_apres is not None:
        for f, valeur in valeurs.items():
            if f in course.arretees or f in course.gelees:
                continue
            motif = abandon_apres(f, valeur)
            if motif:
                course.abandonner(f, motif=motif)
                compte["abandons_apres"][f] = motif
    compte["promues"] = sorted(map(str, course.lire(sans_partie=sans_partie)))
    compte["sans_partie"] = sans_partie
    compte["interruptions"] = journal.interruptions(g)
    return compte


class Lignees:
    """Version 27 — la **mémoire des lignées de clé** (D-S25 bis (5), « à coder » dans la conception v9) : une affirmation
    (clé de l'héritage) n'est portée que par **une** fiche ; une relance sous un autre nom (même clé, autre fiche) est
    refusée — la fiche d'origine garde son budget d'entrée et ses unités lues. Le **journal des parties** (K8-2 : « le
    monde journalise toute partie calculée ») vit ici aussi : `journaliser` est appelé par le monde (ou l'orchestrateur,
    à chaque `evaluer`) avant toute lecture ; `verifier_sans_partie` confronte une déclaration « sans partie » au journal
    et refuse la déclaration mensongère (0,40 puis 0,98 de fausse promotion sinon, contre-lecture de la v8)."""

    class _Journal(tuple):
        """Journal en lecture seule pour l'appelant : un tuple, étendu seulement par `Lignees` (K10-4)."""

    def __init__(self):
        self.proprietaire = {}
        self._journal = []

    @property
    def journal(self):
        return Lignees._Journal(dict(j) for j in self._journal)

    def entrer(self, fiche, engagement):
        aff = engagement["empreinte_affirmation"]
        if aff in self.proprietaire and self.proprietaire[aff] != fiche:
            raise EngagementInvalide(f"fiche {fiche!r} : même affirmation que {self.proprietaire[aff]!r} — relance sous un autre nom "
                                     f"(ou autre plan, autre population) refusée (D-S25 bis (5), K10-6 : une affirmation, une fiche, un budget)")
        autres = [c for c, f in self.proprietaire.items() if f == fiche and c != aff]
        if autres:
            raise EngagementInvalide(f"fiche {fiche!r} : déjà liée à une autre affirmation — une fiche, une affirmation (K9-2)")
        self.proprietaire[aff] = fiche

    def journaliser(self, generation, fiche, resultat):
        if generation is not None and not isinstance(generation, int):
            raise EngagementInvalide("génération : entier (fournie par la course), jamais une chaîne (K10-4)")
        if any(j["generation"] == generation and j["fiche"] == fiche for j in self._journal):
            raise EngagementInvalide(f"fiche {fiche!r} : seconde évaluation dans la génération {generation} refusée (K9-6)")
        self._journal.append({"generation": generation, "fiche": fiche, "empreinte_unites": resultat["empreinte_unites"],
                              "empreinte_cle": resultat["empreinte_cle"], "unites": len(resultat["identifiants_unites"]),
                              "identifiants_unites": list(resultat["identifiants_unites"]), "vide": len(resultat["identifiants_unites"]) == 0,
                              "empreinte_trajectoire": pa._empreinte_trajectoire(resultat["trajectoire_log_min"])})

    def interrompre(self, generation, motif):
        """K11-4 : une génération interrompue (exception au milieu de `jouer_generation`) est tracée, jamais tue."""
        self._interruptions = getattr(self, "_interruptions", [])
        self._interruptions.append({"generation": generation, "motif": motif})

    def interruptions(self, generation=None):
        return [dict(i) for i in getattr(self, "_interruptions", []) if generation is None or i["generation"] == generation]

    def marquer_vide(self, generation, fiche):
        for j in self._journal:
            if j["generation"] == generation and j["fiche"] == fiche:
                if j["unites"] != 0:
                    raise EngagementInvalide(f"fiche {fiche!r} : la partie de la génération {generation} n'est pas vide")
                j["vide"] = True
                return
        raise EngagementInvalide(f"fiche {fiche!r} : aucune partie journalisée en génération {generation}")

    def parties_calculees(self, generation):
        return {j["fiche"] for j in self._journal if j["generation"] == generation and not j.get("vide")}

    def verifier_sans_partie(self, generation, sans_partie):
        calculees = self.parties_calculees(generation)
        menteuses = sorted(str(f) for f in (sans_partie or {}) if f in calculees)
        if menteuses:
            raise EngagementInvalide(f"génération {generation} : déclaration « sans partie » contredite par le journal "
                                     f"des parties pour {menteuses[:5]} (K8-2 : toute partie calculée est ajoutée)")
