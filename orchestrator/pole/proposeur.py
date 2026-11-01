"""Rôle proposeur (version 0.7.0, pièce 4 de v7) : un agent qui formule les fiches d'une génération, à liberté bornée.

Sur le « go now » de Lazar du 27 octobre (15:11 heure de Paris) et son « yes go » de 15:20 pour la stratégie « hors des
bassins déjà promus ». Le proposeur reçoit un **contexte public** (`contexte-proposeur.json`) : la description du monde
(traits, moniteurs, nombres d'issues, effectifs ; **jamais les issues**), les prédicteurs connus du noyau (ajustés sur la
partie de calibrage, déjà visibles dans les engagements), l'archive du pôle (énoncé, statut, moniteur, loi, stratégie,
et le seul drapeau « expliquée par le connu » — **jamais la richesse**), le catalogue des stratégies et le gabarit. Il rend
un bloc JSON `{"fiches": [{"enonce", "strategie", "moniteur", "loi_predictive", "domaines"?, "operateurs"?}]}` ; le noyau
complète les champs fixes (métrique, nul, seuil 1/α, sévérité α, protocole, prédiction), valide le gabarit et refuse le
reste avec un motif. Moins de texte libre : moins de canaux.

**Liberté bornée** : la stratégie doit être déclarée et appartenir au catalogue ; la loi doit être d'un type permis, de
la dimension du monde, au nombre d'issues du moniteur, à poids bornés. La mesure : combien de fiches promues par
stratégie (journal `proposeur.par_strategie`).

**Exposition adaptative** (faille A4 de la contre-lecture d'aptitude, « jeu de test réutilisé ») : chaque verdict montré
au proposeur est une information sur les issues d'épreuve ; le monde sur banque peut couper la partie d'épreuve en
tranches, une par génération (`MondeBanque(tranches=G)`), pour que les fiches d'une génération soient éprouvées sur des
instances dont aucun verdict n'a encore été montré ; sans tranches, le journal compte l'exposition.

Stratégies d'**allocation** à mesurer plus tard comme hypothèses (non codées) : la « loi mère » et l'allocation par champ
moyen (Thouless-Anderson-Palmer) de la relève de Gemini, contre une allocation apprise des promotions.
"""

import json
import math
import os

from . import selection_pari as sp
from .caviardage import caviarder
from .fiche import Fiche, FicheInvalide
from .outils import dossier_traces, ecrire_json_scelle, ecrire_scelle, extraire_bloc_json

CATALOGUE = {
    "monotone_un_trait": "l'issue croît (ou décroît) avec un seul trait (loi softmax ordinale sur ce trait)",
    "interaction_deux_traits": "l'effet d'un trait dépend du signe d'un autre (loi si_sinon, seuil 0 sur le second)",
    "difference_sous_populations": "la loi diffère entre sous-populations (loi par_sous_population)",
    "correction_eliminee": "reprise d'une fiche éliminée (non expliquée par le connu), moins confiante ou de sens inverse",
    "transposition_moniteur": "la loi d'une survivante transposée à un autre moniteur de même nombre d'issues",
    "hors_bassins_promus": "un couple (moniteur, trait) qu'aucune fiche promue ne couvre encore",
    "au_dela_du_connu": "un trait que le prédicteur connu du moniteur pèse peu",
    "ajustee_sur_developpement": ("loi ajustée sur la partie de développement (traits et issues visibles), de forme que le "
                                  "prédicteur connu, linéaire en tous les traits, ne contient pas (par sous-population, "
                                  "si/sinon) ; seulement si la phase exploratoire est ouverte"),
}
STRATEGIES_D_ALLOCATION_A_MESURER = {
    "loi_mere": "relève de Gemini : une loi unique de priorité à tous les étages — à tester comme hypothèse",
    "champ_moyen_tap": "relève de Gemini : priorités par magnétisation de Thouless-Anderson-Palmer — à tester",
}
TYPES_PERMIS = ("softmax", "par_sous_population", "si_sinon", "melange", "fixe")
BORNE_POIDS = 4.0
MAX_FICHES = 40


class PropositionRefusee(ValueError):
    pass


def _types_et_poids(loi, profondeur=0):
    """Vérifie récursivement les types permis et la borne des poids ; lève PropositionRefusee."""
    if profondeur > 4:
        raise PropositionRefusee("loi trop imbriquée (profondeur > 4)")
    if not isinstance(loi, dict) or loi.get("type") not in TYPES_PERMIS:
        raise PropositionRefusee(f"type de loi hors gabarit : {loi.get('type') if isinstance(loi, dict) else loi!r} "
                                 f"(permis : {', '.join(TYPES_PERMIS)})")
    if loi["type"] == "softmax":
        for ligne in loi.get("poids", []):
            for w in ligne:
                if not isinstance(w, (int, float)) or not math.isfinite(w) or abs(w) > BORNE_POIDS:
                    raise PropositionRefusee(f"poids hors borne (|w| ≤ {BORNE_POIDS})")
        for b in loi.get("biais", []):
            if not isinstance(b, (int, float)) or not math.isfinite(b) or abs(b) > 2 * BORNE_POIDS:
                raise PropositionRefusee(f"biais hors borne (|b| ≤ {2 * BORNE_POIDS})")
    elif loi["type"] == "par_sous_population":
        for sous in list(loi.get("lois", {}).values()) + ([loi["defaut"]] if loi.get("defaut") else []):
            _types_et_poids(sous, profondeur + 1)
    elif loi["type"] == "si_sinon":
        _types_et_poids(loi.get("si"), profondeur + 1)
        _types_et_poids(loi.get("sinon"), profondeur + 1)
    elif loi["type"] == "melange":
        for c in loi.get("composantes", []):
            _types_et_poids(c, profondeur + 1)


def contexte_proposeur(monde, memoire, generation, nombre, alpha, expliquees=()):
    """Contexte public servi au proposeur : jamais une issue, jamais une richesse."""
    archive = []
    if memoire is not None:
        for ident, e in sorted(memoire.index.items()):
            if e.get("temoin"):
                continue
            archive.append({"identifiant": ident, "enonce": e["enonce"], "statut": e["statut"],
                            "loi_predictive": e.get("loi_predictive"), "strategie": _strategie_de(e.get("source")),
                            "moniteur": (e.get("espace_instances") or {}).get("moniteur"),
                            "expliquee_par_le_connu": ident in expliquees})
    description = monde.description_publique()
    return {"generation": generation, "nombre_de_fiches": nombre, "alpha": alpha, "monde": description,
            "predicteurs_connus": monde.predicteurs_connus_publics() if hasattr(monde, "predicteurs_connus_publics") else {},
            "archive": archive, "catalogue": CATALOGUE,
            "gabarit": {"types_de_loi": list(TYPES_PERMIS), "borne_des_poids": BORNE_POIDS,
                        "dimension": len(description["traits"]), "champs": ["enonce", "strategie", "moniteur",
                                                                             "loi_predictive", "domaines", "operateurs"]}}


def _strategie_de(source):
    if isinstance(source, str) and source.startswith("proposeur:"):
        return source.split(":")[1]
    return None


def valider_proposition(p, monde, alpha, identifiant, modele, references=False):
    """Fiche complète à partir d'une proposition au gabarit ; lève PropositionRefusee avec le motif. Les stratégies des
    proposeurs de référence (`proposeurs_references.REFERENCES`) ne sont acceptées que si `references` (v7, version 7)."""
    from .proposeurs_references import REFERENCES
    if not isinstance(p, dict):
        raise PropositionRefusee("proposition non conforme (objet attendu)")
    inconnus = set(p) - {"enonce", "strategie", "moniteur", "loi_predictive", "domaines", "operateurs"}
    if inconnus:
        raise PropositionRefusee("champs hors gabarit : " + ", ".join(sorted(inconnus)))
    strategie = p.get("strategie")
    if strategie not in CATALOGUE and not (references and strategie in REFERENCES):
        raise PropositionRefusee(f"stratégie non déclarée ou hors catalogue : {strategie!r}")
    description = monde.description_publique()
    moniteur = p.get("moniteur")
    if moniteur not in description["moniteurs"]:
        raise PropositionRefusee(f"moniteur inconnu du monde : {moniteur!r}")
    k, d = description["moniteurs"][moniteur]["nombre_issues"], len(description["traits"])
    loi = p.get("loi_predictive")
    _types_et_poids(loi)
    try:
        sp.valider_loi(loi, k, d)
    except sp.LoiInvalide as e:
        raise PropositionRefusee(f"loi invalide : {e}") from e
    enonce = p.get("enonce")
    if not isinstance(enonce, str) or not enonce.strip() or len(enonce) > 400:
        raise PropositionRefusee("énoncé : texte non vide de 400 caractères au plus")
    domaines = p.get("domaines") or [f"moniteur {moniteur}"]
    operateurs = p.get("operateurs") or [strategie]
    try:
        fiche = Fiche.depuis_dict({
            "identifiant": identifiant, "enonce": enonce.strip(),
            "prediction": {"signe": "+", "valeur": 0.1, "texte": "log-richesse positive contre la bibliothèque nulle"},
            "metrique": "richesse W contre la bibliothèque (aveugle et prédicteur connu)",
            "nul": "prédicteurs aveugles et prédicteur connu du moniteur", "seuil": round(1.0 / alpha, 6),
            "severite_attendue": alpha, "cout_borne": 1.0,
            "protocole": "pari sur les instances d'épreuve choisies ex ante par divergence, après le gel",
            "domaines": [str(x) for x in domaines][:4], "operateurs": [str(x) for x in operateurs][:4],
            "contraintes": [], "source": f"proposeur:{strategie}:{modele}", "loi_predictive": loi,
            "espace_instances": {"dimension": d, "nombre_issues": k, "sous_populations": description["sous_populations"],
                                 "moniteur": moniteur, "banque": description["nom"]}}).valider()
    except FicheInvalide as e:
        raise PropositionRefusee(str(e)) from e
    return fiche


def consigne_proposeur(nombre):
    return (f"Tu es le proposeur du pôle. Lis `contexte-proposeur.json` : le monde (traits, moniteurs, nombre d'issues ; "
            f"jamais les issues), les prédicteurs connus, l'archive des fiches (énoncé, statut, loi, stratégie) et le "
            f"catalogue des stratégies. Propose au plus {nombre} fiches qui ont une chance de battre les prédicteurs "
            "aveugles **et** le prédicteur connu, en déclarant pour chacune une stratégie du catalogue, sans redire une "
            "fiche de l'archive. Réponds par un bloc ```json {\"fiches\": [{\"enonce\": \"…\", \"strategie\": \"…\", "
            "\"moniteur\": \"…\", \"loi_predictive\": {…}}]}``` au gabarit (types de loi permis, dimension, borne des "
            "poids) ; tout champ hors gabarit fait refuser la fiche.")


def proposer(adaptateur, config, monde, memoire, generation, dossier, budget, nombre, expliquees=()):
    """Lance le proposeur ; rend {"fiches": [...], "refusees": [...], "rapport": {...}}."""
    rapport = {"demandees": nombre, "proposees": 0, "acceptees": 0, "par_strategie": {}, "refus": []}
    if nombre <= 0:
        return {"fiches": [], "refusees": [], "rapport": rapport}
    genre = getattr(config, "proposeur", "agent")
    if genre != "agent":
        return _proposer_reference(genre, config, monde, generation, dossier, nombre, rapport)
    if not budget.reserver(config.plafond_proposeur_usd):
        return {"fiches": [], "refusees": [], "rapport": dict(rapport, motif="budget insuffisant pour le proposeur")}
    os.makedirs(dossier, exist_ok=True)
    contexte = contexte_proposeur(monde, memoire, generation, nombre, config.alpha, expliquees)
    if getattr(config, "exploration_developpement", False) and hasattr(monde, "donnees_developpement"):
        # v7, pièce 4 bis : phase exploratoire — la partie de développement (traits et issues) est déposée pour le
        # proposeur, qui peut y ajuster et y itérer librement ; l'épreuve reste cachée jusqu'au gel.
        donnees = monde.donnees_developpement()
        ecrire_json_scelle(os.path.join(dossier, "developpement.json"), donnees)
        contexte["developpement"] = {"fichier": "developpement.json", "instances": len(donnees["instances"]),
                                     "note": "traits et issues de la partie de développement ; l'épreuve n'est jamais "
                                             "visible ; une loi ajustée ici est jugée sur l'épreuve, après le gel"}
    ecrire_json_scelle(os.path.join(dossier, "contexte-proposeur.json"), contexte)
    consigne = consigne_proposeur(nombre)
    traces = dossier_traces(dossier)  # v7, version 5 : traces de l'orchestrateur hors du dossier de l'agent
    ecrire_scelle(os.path.join(traces, "consigne.txt"), consigne)
    res = adaptateur.lancer("proposeur", consigne, dossier, config.plafond_proposeur_usd, config.max_tours_proposeur,
                            modele=config.modele_proposeur)
    budget.regler(config.plafond_proposeur_usd, res.cout_declare_usd)
    ecrire_scelle(os.path.join(traces, "reponse.txt"), caviarder(res.texte_final)[0])
    bloc = extraire_bloc_json(res.texte_final, "fiches") or {}
    propositions = bloc.get("fiches") if isinstance(bloc.get("fiches"), list) else []
    rapport["proposees"] = len(propositions)
    fiches, refusees = [], []
    for i, p in enumerate(propositions[:min(nombre, MAX_FICHES)], 1):
        strategie = p.get("strategie") if isinstance(p, dict) else None
        compte = rapport["par_strategie"].setdefault(str(strategie), {"proposees": 0, "acceptees": 0})
        compte["proposees"] += 1
        try:
            fiche = valider_proposition(p, monde, config.alpha, f"prop-g{generation:02d}-{i:02d}", config.modele_proposeur)
        except PropositionRefusee as e:
            refusees.append({"rang": i, "strategie": strategie, "motif": str(e)})
            continue
        compte["acceptees"] += 1
        fiches.append(fiche)
    if len(propositions) > nombre:
        refusees.append({"rang": None, "strategie": None, "motif": f"{len(propositions) - nombre} fiches au-delà du nombre demandé"})
    rapport.update(acceptees=len(fiches), refus=refusees, cout=res.cout_declare_usd, statut=res.statut)
    return {"fiches": fiches, "refusees": refusees, "rapport": rapport}


def _proposer_reference(genre, config, monde, generation, dossier, nombre, rapport):
    """v7, version 7 : proposeur de référence, sans modèle ni dépense (aléatoire au gabarit, ou mécanique sur la partie
    de développement) ; ses propositions passent par la même porte que celles d'un agent."""
    from . import proposeurs_references as pr
    description = monde.description_publique()
    if genre == "aleatoire":
        propositions = pr.propositions_aleatoires(description, nombre, config.graine, generation)
    elif genre == "mecanique":
        if not (getattr(config, "exploration_developpement", False) and hasattr(monde, "donnees_developpement")):
            raise ValueError("proposeur mécanique : la phase exploratoire (partie de développement) est requise")
        propositions = pr.propositions_mecaniques(description, monde.donnees_developpement(), nombre)
    else:
        raise ValueError(f"proposeur inconnu : {genre!r}")
    traces = dossier_traces(dossier)
    ecrire_json_scelle(os.path.join(traces, "propositions-reference.json"), {"genre": genre, "generation": generation,
                                                                              "propositions": propositions})
    rapport["proposees"] = len(propositions)
    fiches, refusees = [], []
    for i, p in enumerate(propositions[:min(nombre, MAX_FICHES)], 1):
        compte = rapport["par_strategie"].setdefault(str(p.get("strategie")), {"proposees": 0, "acceptees": 0})
        compte["proposees"] += 1
        try:
            fiche = valider_proposition(p, monde, config.alpha, f"prop-g{generation:02d}-{i:02d}", f"reference-{genre}",
                                        references=True)
        except PropositionRefusee as e:
            refusees.append({"rang": i, "strategie": p.get("strategie"), "motif": str(e)})
            continue
        compte["acceptees"] += 1
        fiches.append(fiche)
    rapport.update(acceptees=len(fiches), refus=refusees, cout=0.0, statut="ok", genre=genre)
    return {"fiches": fiches, "refusees": refusees, "rapport": rapport}


def expliquees_par_le_connu(issues):
    """Identifiants des fiches éliminées dont le membre dominant final du nul est un prédicteur connu."""
    sortie = set()
    for ident, issue in issues.items():
        pari = issue.get("pari") or {}
        if issue.get("verdict_final") == "eliminee" and str(pari.get("membre_dominant_final", "")).startswith("connu:"):
            sortie.add(ident)
    return sortie


__all__ = ["CATALOGUE", "STRATEGIES_D_ALLOCATION_A_MESURER", "PropositionRefusee", "consigne_proposeur",
           "contexte_proposeur", "expliquees_par_le_connu", "proposer", "valider_proposition", "json"]
