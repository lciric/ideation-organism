"""Cœur du tour fermé, version 61 (fichier neuf, R12 ; tâches A2, A3 et A4) — étage 1 (monde à loi plantée, trois bras) et
porte vers l'étage 2.

Préenregistrement : `prereg/preenregistrement-tour-ferme-v1-brouillon2.md`, sections 2 à 4, 7 (liste d'arrêt), 8 (graines),
13 (code gelé). Contre-lecture appliquée : `prereg/contre-lecture-preenregistrement-tour-ferme-v1.md`, changement C5.
Ce module **ne lit aucune issue** : il produit le relevé que lit `pole/lecture_tour_ferme_v61.py`.

Ce qu'il ajoute à la boucle fermée v59 (`pole/boucle_fermee_v59.py`, `pole/a_blanc_v59.py`, réutilisées appel pour appel pour le
juge, la tranche, l'exécuteur et la lecture vérifiée de l'héritage) :

1. **Témoins** (décision D3) : sept témoins par génération et par bras qui joue (T-VRAIE, T-F1, T-F2, T-F4, T-ANTI, T-ELIM,
   T-MAL), identifiants opaques dérivés de la graine, jugés **sans membres d'archive**, lus **hors famille** dans la règle e-BH
   (seuil m/α, sans peser sur k*, comme le témoin vrai de `cycle.appliquer_multiplicite`), testés dans **leur propre étage**
   (dossier `etage-temoins`, même tranche que les cartes), **jamais** dans la sélection, l'archive ni la vue (garde 7,
   `TemoinRetenu`, vérifiée après chaque génération).
2. **Gabarit fermé du proposeur** (garde 8) : une proposition est `{enonce, loi_predictive}` (plus `moniteur` à l'étage 2) ;
   toute autre clé (test, seuil, statistique, données…) est un refus au gardien mécanique, motif dit ; l'orchestrateur complète
   la carte, test de mort compris (`proposeurs_references_v59.TEST_DE_MORT`).
3. **Gardien** : décision D9 lue dans le plan gelé ; « mecanique » = `a_blanc_v59.garder` pour les trois bras et les témoins ;
   « aiguilleur » n'est pas écrit dans cette version (refus avant tout appel, dit).
4. **e-BH à m fixé** (plan gelé, 19 à l'étage 1) sur la famille des cartes ; témoins hors famille.
5. **Ordre des bras** dans une génération : réel, puis recopie-mélange, puis aléatoire (décision D4 : le bras recopie lit le
   bilan du bras réel, vérifié par empreinte, et ses cartes sont jugées contre l'archive du bras réel ; décision D7, paramètre :
   « archive_du_bras_reel » = les cartes aléatoires sont jugées contre l'archive du bras réel de la même génération et ses
   retenues ne vont dans aucune archive ; « archive_propre » = le bras aléatoire a sa propre boucle).
6. **Familles séparées** (garde 9) : l'expérimentateur et le vérificateur sont de deux familles différentes, vérifié avant toute
   session (`FamillesNonSeparees`).
7. **Contre-calcul** (garde 10) : pour chaque carte ou témoin testé, l'orchestrateur recalcule hors bac la statistique depuis la
   loi gelée et la tranche scellée ; écart > 10⁻⁶ avec la valeur du noyau → **arrêt** de la course (aucune issue lue, la carte
   n'entre pas à l'archive) ; absence de valeur du noyau (« non concluant ») : contre-calcul fait, concordance « sans objet »,
   booléen vrai, consigné.
8. **Plafond de dépense et de durée** (gardes 5 et 13) : `Compteur`, `ArretTour` avec la trace partielle.
9. **Relevé** au format de `lecture_tour_ferme_v61` (générations jouées par bras, lectures d'héritage, cartes avec oracle), et
   manifeste (commit, versions de Python, numpy et bwrap, ordre des bras, décisions).

Aucun réseau ici ; les adaptateurs réels sont construits par le lanceur `demonstrations/tour_ferme_v61.py`.
"""

import hashlib
import json
import math
import os
import platform
import random
import re
import subprocess
import time

from . import a_blanc_v59 as A
from . import boucle_fermee_v59 as bf
from . import proposeurs_references_v59 as pr
from . import selection_pari as sp
from . import tests_de_mort_v5 as v5
from .adaptateurs import Resultat
from .cycle import appliquer_multiplicite
from .etage_entre_generations_v53 import preparer_generation
from .etage_entre_generations_v57 import NOM_SELECTION, jouer_etage_v57
from .fiches_v53 import preparer
from .oracle_tour_ferme_v60 import Oracle
from .outils import ecrire_json_scelle, empreinte_objet

VERSION = "tour-ferme-v61"
ALPHA = 0.05
K, DIM = pr.K, pr.DIM
BRAS_ETAGE1 = ("reel", "recopie_melange", "aleatoire")  # ordre de jeu dans une génération (D4, D7)
TEMOINS = ("T-VRAIE", "T-F1", "T-F2", "T-F4", "T-ANTI", "T-ELIM", "T-MAL")
CLES_PROPOSITION = {1: ("enonce", "loi_predictive"), 2: ("enonce", "moniteur", "loi_predictive")}
LONGUEUR_ENONCE = 400
DECISIONS = {"d7": ("archive_du_bras_reel", "archive_propre"), "d8": ("predicteur_connu", "marginale"),
             "d9": ("mecanique", "aiguilleur")}
TOLERANCE_CONTRE_CALCUL = 1e-6
CONSIGNE_PROPOSEUR = ("Propose au plus {n} lois qui prédisent l'issue mieux que la marginale et mieux que les lois déjà "
                      "retenues. Réponds par un bloc JSON : une liste d'objets {{\"enonce\": texte (≤ 400 caractères), "
                      "\"loi_predictive\": loi}} ; types permis : softmax, par_sous_population, si_sinon, melange, fixe, "
                      "transformee ; {dim} traits ; {k} issues ; poids bornés à ±{borne}. Rien d'autre : le test de mort, "
                      "son seuil, sa statistique et ses données sont fixés par l'orchestrateur.")
ENV_ETAGE = dict(A.ENV_A_BLANC)


class TourRefuse(RuntimeError):
    """Refus avant tout appel (plan, décisions, familles, bac, gabarit du monde) : code 2, rien d'écrit."""


class TemoinRetenu(TourRefuse):
    """Un témoin est entré dans une sélection, une archive ou une vue (garde 7)."""


class FamillesNonSeparees(TourRefuse):
    """Expérimentateur et vérificateur de la même famille (garde 9)."""


class ArretTour(RuntimeError):
    """Arrêt de la liste d'arrêt (plafond de dépense, durée, contre-calcul en désaccord) ; `partiel` porte la trace."""

    def __init__(self, motif, partiel=None):
        super().__init__(motif)
        self.partiel = partiel or {}


# --- plan et décisions ---------------------------------------------------------------------------------------------------


def verifier_decisions(decisions):
    """Les décisions D7, D8, D9 lues dans le plan gelé : chacune parmi ses valeurs permises ; rien n'est enfoui dans le code."""
    if not isinstance(decisions, dict) or set(decisions) != set(DECISIONS):
        raise TourRefuse(f"décisions attendues {sorted(DECISIONS)}, reçues {sorted(decisions) if isinstance(decisions, dict) else decisions!r}")
    for k, permises in DECISIONS.items():
        if decisions[k] not in permises:
            raise TourRefuse(f"décision {k.upper()} = {decisions[k]!r} ; permises : {permises}")
    if decisions["d9"] == "aiguilleur":
        raise TourRefuse("décision D9 = aiguilleur : gardien modèle non écrit dans cette version (refus avant tout appel)")
    return dict(decisions)


class Compteur:
    """Plafond dur de dépense et de durée d'un étage (gardes 5 et 13) ; lève `ArretTour` au franchissement."""

    def __init__(self, plafond_usd, duree_max_s, horloge=time.time):
        self.plafond_usd, self.duree_max_s, self.horloge = float(plafond_usd), float(duree_max_s), horloge
        self.debut, self.usd, self.appels = horloge(), 0.0, 0
        self.par_role = {}

    def ajouter(self, usd, role):
        self.appels += 1
        self.usd += float(usd)
        self.par_role[role] = round(self.par_role.get(role, 0.0) + float(usd), 6)
        if self.usd > self.plafond_usd:
            raise ArretTour(f"plafond de dépense de l'étage franchi : {self.usd:.4f} USD > {self.plafond_usd} USD")
        self.verifier_duree()

    def verifier_duree(self):
        if self.horloge() - self.debut > self.duree_max_s:
            raise ArretTour(f"plafond de durée de l'étage franchi : {self.horloge() - self.debut:.0f} s > {self.duree_max_s:.0f} s")

    def etat(self):
        return {"appels": self.appels, "depense_usd": round(self.usd, 6), "par_role_usd": dict(self.par_role),
                "duree_s": round(self.horloge() - self.debut, 1)}


# --- témoins (D3) et gabarit (garde 8) ---------------------------------------------------------------------------------------


def identifiant_opaque(racine, tache, nom):
    return "W-" + hashlib.sha256(f"{racine}|{tache}|{nom}".encode("utf-8")).hexdigest()[:12]


def temoins_du_monde(monde, racine, tache):
    """Les sept témoins d'une génération d'un bras : (nom, carte complète) ; identifiants opaques."""
    v = monde["loi"]
    anti = {"type": "softmax", "poids": [[-w for w in ligne] for ligne in v["poids"]], "biais": list(v["biais"])}
    lois = {"T-VRAIE": v, "T-F1": monde["fausses"]["S-F1"], "T-F2": monde["fausses"]["S-F2"], "T-F4": monde["fausses"]["S-F4"],
            "T-ANTI": anti, "T-ELIM": {"type": "transformee", "base": v, "puissance": 1.25}, "T-MAL": v}
    out = []
    for nom in TEMOINS:
        ident = identifiant_opaque(racine, tache, nom)
        if nom == "T-ELIM":
            c = pr.carte(ident, "témoin", lois[nom], "temoin", test_de_mort=dict(pr.TEST_DE_MORT, seuil="au moins 2,0"))
        elif nom == "T-MAL":
            c = dict(pr.carte(ident, "témoin", lois[nom], "temoin"),
                     test_de_mort={k: x for k, x in pr.TEST_DE_MORT.items() if k != "statistique"})
        else:
            c = pr.carte(ident, "témoin", lois[nom], "temoin")
        out.append((nom, c))
    return out


def completer_carte(proposition, ident, bras, etage=1):
    """Garde 8 : la proposition doit être exactement au gabarit fermé ; l'orchestrateur complète tout le reste (test de mort
    imposé). Rend (carte, None) ou (None, motif)."""
    cles = CLES_PROPOSITION[etage]
    if not isinstance(proposition, dict):
        return None, "proposition non dictionnaire"
    en_trop = sorted(set(proposition) - set(cles))
    manquantes = [k for k in cles if k not in proposition]
    if en_trop or manquantes:
        return None, f"gabarit du proposeur : clés en trop {en_trop}, manquantes {manquantes} (le test de mort est imposé)"
    enonce = proposition["enonce"]
    if not isinstance(enonce, str) or not enonce.strip() or len(enonce) > LONGUEUR_ENONCE:
        return None, f"énoncé : texte non vide de {LONGUEUR_ENONCE} caractères au plus attendu"
    if not isinstance(proposition["loi_predictive"], dict):
        return None, "loi prédictive : dictionnaire attendu"
    if etage == 2 and (not isinstance(proposition["moniteur"], str) or not proposition["moniteur"]):
        return None, "moniteur : texte non vide attendu"
    carte = pr.carte(ident, enonce[:80], proposition["loi_predictive"], bras, hypothese=enonce)
    if etage == 2:
        carte["moniteur"] = proposition["moniteur"]
    return carte, None


def garder(carte, decisions):
    """Gardien de la décision D9 (« mecanique » seule écrite) : `a_blanc_v59.garder`, le même pour les trois bras et les témoins."""
    if decisions["d9"] != "mecanique":
        raise TourRefuse(f"gardien {decisions['d9']!r} non écrit")
    return A.garder(carte)


# --- proposeurs ------------------------------------------------------------------------------------------------------------


def extraire_propositions(texte):
    """Liste de propositions dans un bloc ```json … ``` (ou le texte entier) ; liste vide si illisible (refus mesuré)."""
    m = re.search(r"```json\s*(.*?)\s*```", texte or "", re.S)
    brut = m.group(1) if m else (texte or "")
    try:
        obj = json.loads(brut)
    except ValueError:
        return [], "réponse illisible (JSON)"
    if isinstance(obj, dict) and isinstance(obj.get("propositions"), list):
        obj = obj["propositions"]
    if not isinstance(obj, list):
        return [], "réponse sans liste de propositions"
    return obj, None


class ProposeurScripte:
    """Proposeur réel simulé du mode à blanc : lois voisines de la loi plantée (bruit gaussien), ou artefacts sur demande
    (`scenario` : « hors_gabarit » ajoute un seuil et une statistique à chaque proposition ; « illisible » rend du texte)."""
    famille = "scripte"

    def __init__(self, nom, monde, ecart=0.6, scenario=None, cout_par_appel=0.0):
        self.nom, self.monde, self.ecart, self.scenario, self.cout = nom, monde, ecart, scenario, cout_par_appel
        self.appels = []

    def proposer(self, consigne, contexte, nombre, racine, tache):
        rng = random.Random(bf.graine_de_tache(racine, f"{tache}|proposeur={self.nom}"))
        self.appels.append({"consigne_sha256": hashlib.sha256(consigne.encode()).hexdigest(), "contexte_sha256": empreinte_objet(contexte)})
        if self.scenario == "illisible":
            return "je ne sais pas", self.cout
        v = self.monde["loi"]
        props = []
        for i in range(nombre):
            loi = {"type": "softmax", "poids": [[max(-pr.BORNE, min(pr.BORNE, round(w + rng.gauss(0.0, self.ecart), 6))) for w in l]
                                                for l in v["poids"]], "biais": [round(b + rng.gauss(0.0, 0.3), 6) for b in v["biais"]]}
            p = {"enonce": f"{self.nom} : loi softmax n° {i + 1} ajustée sur les épisodes de développement", "loi_predictive": loi}
            if self.scenario == "hors_gabarit":
                p.update(test_de_mort={"seuil": "au moins 0,0"}, statistique="moyenne")
            props.append(p)
        return "```json\n" + json.dumps(props, ensure_ascii=False) + "\n```", self.cout


class ProposeurAdaptateur:
    """Proposeur réel : un appel par génération par l'adaptateur du pôle (rôle « proposeur »), budget par appel, modèle exact."""

    def __init__(self, nom, famille, adaptateur, dossier, budget_usd, modele):
        self.nom, self.famille, self.ad, self.dossier, self.budget, self.modele = nom, famille, adaptateur, dossier, budget_usd, modele
        self.appels = []

    def proposer(self, consigne, contexte, nombre, racine, tache):
        d = os.path.join(self.dossier, re.sub(r"[^A-Za-z0-9=|-]", "_", tache))
        os.makedirs(d, exist_ok=True)
        texte = consigne + "\n\n```json\n" + json.dumps(contexte, ensure_ascii=False) + "\n```\n"
        r = self.ad.lancer("proposeur", texte, d, self.budget, 1, modele=self.modele)
        self.appels.append({"tache": tache, "statut": r.statut, "cout_usd": r.cout_declare_usd,
                            "consigne_sha256": hashlib.sha256(texte.encode()).hexdigest()})
        return (r.texte_final if r.statut == "ok" else ""), float(r.cout_declare_usd or 0.0)


def contexte_du_proposeur(monde, vue, racine, tache, n_dev=200):
    """Description publique du monde, gabarit, lois retenues (vue v59, vérifiée) et épisodes de développement (graine de la
    tâche « développement ») ; jamais une issue de l'épreuve, jamais un verdict."""
    bf.exiger_vue_sans_verdict(vue)
    rng = random.Random(bf.graine_de_tache(racine, f"{tache}|developpement"))
    dev = []
    for x in sp.tirer_instances(rng, n_dev, DIM):
        dev.append({"z": [round(z, 6) for z in x["z"]], "g": x["g"], "y": sp.tirer_categorie(rng, sp.proba(monde["loi"], x, [], 0))})
    return {"monde": {"traits": DIM, "sous_populations": 2, "issues": K, "enonce_public": "monde synthétique à loi inconnue"},
            "gabarit": {"types": ["softmax", "par_sous_population", "si_sinon", "melange", "fixe", "transformee"],
                        "borne_des_poids": pr.BORNE, "cartes_max": 6},
            "lois_retenues": vue["lois_retenues"], "episodes_developpement": dev}


# --- juge : cartes contre l'archive, témoins sans archive, e-BH à m fixé, témoins hors famille ----------------------------------


def juger(cartes, temoins, monde, archive, racine, tache, m):
    """Rend (promues cartes, promus témoins, détail). Cartes : nul v8 avec membres d'archive, règle e-BH de la famille des cartes
    à m fixé ; témoins : sans membres d'archive, hors famille au seuil m/α (ne pèsent pas sur k*)."""
    if m < len(cartes):
        raise TourRefuse(f"m fixé ({m}) < cartes jugées ({len(cartes)})")
    issues, detail = {}, {}
    for c in cartes:
        ev, d = A.juger_carte(c["loi_predictive"], monde, archive, racine, f"{tache}|carte={c['identifiant']}")
        issues[c["identifiant"]] = {"verdict_final": "survit" if ev["promue"] else "eliminee", "motif": "", "pari": dict(ev)}
        detail[c["identifiant"]] = dict(d, promue_seule=bool(ev["promue"]), log_richesse_max=round(ev["log_richesse_max"], 6))
    mult = appliquer_multiplicite(issues, ALPHA, m_fixe=m) if issues else {"m": m, "retenues": []}
    for i, issue in issues.items():
        detail[i].update(promue=issue["verdict_final"] == "survit", log_e=issue["pari"].get("multiplicite", {}).get("log_e"))
    promues = sorted((i for i in issues if detail[i]["promue"]), key=lambda i: (-(detail[i]["log_e"] or -1e9), i))
    seuil = math.log(m / ALPHA)
    promus_temoins = []
    for nom, c in temoins:
        ev, d = A.juger_carte(c["loi_predictive"], monde, {}, racine, f"{tache}|temoin={c['identifiant']}")
        traj = ev["trajectoire_log_w"]
        log_e = -math.inf if ev.get("marge_atteinte") is False else next((v for v in traj if v >= seuil), traj[-1])
        retenu = bool(ev["promue"]) and log_e >= seuil
        detail[c["identifiant"]] = dict(d, temoin=nom, promue_seule=bool(ev["promue"]), promue=retenu,
                                        log_e=None if math.isinf(log_e) else round(log_e, 6), regle="hors famille, seuil m/α",
                                        membres_d_archive=0)
        if retenu:
            promus_temoins.append(c["identifiant"])
    return promues, promus_temoins, detail, mult["m"]


# --- étage de tests de mort (expérimentateur et vérificateur), contre-calcul ----------------------------------------------------


def exiger_familles_separees(experimentateur, verificateur):
    """Garde 9 : (étiquette, famille) de chacun ; même famille → `FamillesNonSeparees`, avant toute session."""
    if not experimentateur[1] or not verificateur[1] or experimentateur[1] == verificateur[1]:
        raise FamillesNonSeparees(f"expérimentateur {experimentateur} et vérificateur {verificateur} : familles non séparées")


def statistique_hors_bac(loi, chemin_episodes):
    """Le gabarit gelé du test de mort, recalculé par l'orchestrateur : gain moyen de log-score de la loi sur la marginale
    empirique de la tranche (comptes + 0,5), nat par épisode."""
    import csv
    with open(chemin_episodes, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    comptes = [0.5] * K
    for r in lignes:
        comptes[int(r["y"])] += 1
    s = sum(comptes)
    marg = [c / s for c in comptes]
    gains = []
    for r in lignes:
        y = int(r["y"])
        p = sp.proba(loi, {"z": [float(r["z0"]), float(r["z1"])], "g": int(r["g"])}, [], 0)
        gains.append(math.log(max(p[y], 1e-12)) - math.log(marg[y]))
    return sum(gains) / len(gains)


def contre_calculer(resume, lois, chemin_episodes):
    """Garde 10 : pour chaque fiche testée, valeur du noyau contre la statistique recalculée ; rend {ident: {ok, noyau,
    orchestrateur, verdict}}. `ok` est toujours un booléen (B5) : vrai si le noyau n'a pas de valeur (« non concluant »)."""
    out = {}
    for r in (resume or {}).get("par_fiche", []):
        if r.get("statut") != "testée":
            continue
        ident, noyau = r["identifiant_auteur"], r.get("verdict_noyau") or {}
        val = noyau.get("valeur_noyau")
        mienne = statistique_hors_bac(lois[ident], chemin_episodes)
        ok = True if val is None else abs(float(val) - mienne) <= TOLERANCE_CONTRE_CALCUL
        out[ident] = {"ok": bool(ok), "noyau": val, "orchestrateur": round(mienne, 9), "verdict": noyau.get("verdict"),
                      "sans_objet": val is None}
    return out


def jouer_etage(dossier_etage, cartes, lois_par_ident, monde, racine, tache, executeur, adaptateur, roles, compteur, journal,
                tranche=None, moteur="simule"):
    """L'étage v5 puis la sélection v57 sur `cartes` (ordre des e-valeurs) ; sans carte, sélection vide scellée. Rend
    (résumé, chemin de la sélection, empreinte, tranche, contre-calculs)."""
    if not cartes:
        os.makedirs(dossier_etage)
        from .etage_entre_generations_v57 import selection_entre_generations
        chemin = os.path.join(dossier_etage, NOM_SELECTION)
        return None, chemin, ecrire_json_scelle(chemin, selection_entre_generations({"par_fiche": [], "version_etage": None})), tranche, {}
    if tranche is None:
        tranche = A.creer_tranche(os.path.join(os.path.dirname(dossier_etage), "exploratoire-etage"), monde, racine, tache)
    fiches = {c["identifiant"]: preparer({k: c[k] for k in A.CHAMPS_FICHE}, list(A.CHAMPS_FICHE), ident=c["identifiant"],
                                         case=("tour-ferme", c["source"]), fournisseur="tour-ferme-v61", passe=1) for c in cartes}
    classement = [{"ident": c["identifiant"], "notable": True, "rang": k} for k, c in enumerate(cartes, 1)]
    preparer_generation(dossier_etage, classement, fiches, nombre=len(cartes), tranche_index_sha256=tranche.index_sha256,
                        correspondance=A.CORRESPONDANCE, lisible=True)
    reglages = {"tranche": tranche, "nombre": len(cartes), "experimentateur": roles["experimentateur"], "lecteur": roles["verificateur"],
                "executeur": executeur, "moteur": moteur}
    resume = jouer_etage_v57(adaptateur, dossier_etage, reglages=reglages, environnement=ENV_ETAGE)
    cout = float((resume.get("couts") or {}).get("externe_usd", 0.0)) + float((resume.get("couts") or {}).get("claude_usd", 0.0))
    compteur.ajouter(cout, "tests_de_mort")
    chemin_ep = os.path.join(os.path.dirname(dossier_etage), "exploratoire-etage", "tranche", "episodes.csv")
    cc = contre_calculer(resume, lois_par_ident, chemin_ep)
    journal.append({"evenement": "etage-tests-de-mort", "tache": tache, "dossier": os.path.basename(dossier_etage),
                    "bac_a_sable": resume["bac_a_sable"].get("nom"), "factice": resume["bac_a_sable"].get("factice"),
                    "tranche_index_sha256": tranche.index_sha256, "comptes": resume["comptes"], "selection_sha256": resume["selection"]["sha256"],
                    "contre_calcul": cc})
    desaccords = sorted(i for i, x in cc.items() if not x["ok"])
    if desaccords:
        raise ArretTour(f"contre-calcul en désaccord avec le noyau pour {desaccords} (garde 10) : arrêt, aucune issue lue",
                        {"contre_calcul": cc})
    return resume, os.path.join(dossier_etage, NOM_SELECTION), resume["selection"]["sha256"], tranche, cc


# --- une génération d'un bras ------------------------------------------------------------------------------------------------


def _verdicts(resume):
    return {r["identifiant_auteur"]: r["verdict_noyau"]["verdict"] for r in (resume or {}).get("par_fiche", []) if r.get("statut") == "testée"}


def jouer_generation(dossier, bras, generation, monde, heritage, archive_jugement, racine, fabrique_executeur, proposeurs,
                     adaptateur_etage, roles, decisions, plan, oracle, compteur, journal, releve_cartes, moteur="simule"):
    """Une génération d'un bras : proposition → gardien → juge (cartes contre `archive_jugement`, témoins sans archive) → étage
    des cartes et étage des témoins (même tranche) → contre-calcul → sélection (cartes seules) → bilan scellé. Rend l'empreinte
    du bilan et la ligne de journal."""
    tache = f"{VERSION}|etage=1|bras={bras}|generation={generation}"
    vue = bf.vue_pour_proposeur(heritage)
    cartes, refusees, motifs_proposeur, appels = [], {}, [], []
    if bras == "reel":
        contexte = contexte_du_proposeur(monde, vue, racine, tache)
        consigne = CONSIGNE_PROPOSEUR.format(n=plan["cartes_par_proposeur"], dim=DIM, k=K, borne=pr.BORNE)
        for p in proposeurs:
            texte, cout = p.proposer(consigne, contexte, plan["cartes_par_proposeur"], racine, tache)
            compteur.ajouter(cout, "proposeur")
            props, motif = extraire_propositions(texte)
            appels.append({"proposeur": p.nom, "cout_usd": cout, "propositions": len(props), "motif": motif})
            if motif:
                motifs_proposeur.append(f"{p.nom} : {motif}")
            for i, prop in enumerate(props[:plan["cartes_par_proposeur"]]):
                ident = f"G{generation}-{p.nom}-{i + 1:02d}"
                c, motif_c = completer_carte(prop, ident, bras)
                if c is None:
                    refusees[ident] = f"gardien mécanique (gabarit) : {motif_c}"
                    releve_cartes.append({"bras": bras, "generation": generation, "identifiant": ident, "temoin": None,
                                          "gardien": "refuse", "promue": False, "verdict": None, "contre_calcul_ok": None,
                                          "gain_nat": None, "delta_gain_nat": None, "divergence_nat": None, "motif": refusees[ident]})
                else:
                    cartes.append(c)
    elif bras == "aleatoire":
        c, m = pr.proposer_aleatoire(vue, plan["cartes_reference"], racine, tache)
        cartes, motifs_proposeur = c, [m] if m else []
    elif bras == "recopie_melange":
        c, m = pr.proposer_recopie_melange(vue, plan["cartes_reference"], racine, tache)
        cartes, motifs_proposeur = c, [m] if m else []
    else:
        raise TourRefuse(f"bras inconnu : {bras}")
    temoins = temoins_du_monde(monde, racine, tache)
    passees, temoins_passes, temoins_refuses = [], [], {}
    for c in cartes:
        passeport, motif = garder(c, decisions)
        if passeport is None:
            refusees[c["identifiant"]] = motif
        else:
            passees.append(c)
    for nom, c in temoins:
        passeport, motif = garder(c, decisions)
        if passeport is None:
            temoins_refuses[nom] = motif
        else:
            temoins_passes.append((nom, c))
    promues, promus_temoins, detail, m = juger(passees, temoins_passes, monde, archive_jugement, racine, tache, plan["m_e_bh"])
    par_ident = {c["identifiant"]: c for c in passees}
    par_ident_t = {c["identifiant"]: (nom, c) for nom, c in temoins_passes}
    executeur, description_bac = fabrique_executeur()
    resume, chemin_sel, sha_sel, tranche, cc = jouer_etage(os.path.join(dossier, bf.DOSSIER_ETAGE), [par_ident[i] for i in promues],
                                                           {i: c["loi_predictive"] for i, c in par_ident.items()}, monde, racine, tache,
                                                           executeur, adaptateur_etage, roles, compteur, journal, moteur=moteur)
    executeur_t, _ = fabrique_executeur()
    resume_t, _, sha_sel_t, _, cc_t = jouer_etage(os.path.join(dossier, "etage-temoins"), [par_ident_t[i][1] for i in promus_temoins],
                                                  {i: c["loi_predictive"] for i, (_, c) in par_ident_t.items()}, monde, racine, tache,
                                                  executeur_t, adaptateur_etage, roles, compteur, journal, tranche=tranche, moteur=moteur)
    verdicts, verdicts_t = _verdicts(resume), _verdicts(resume_t)
    with open(chemin_sel, encoding="utf-8") as f:
        retenues = json.load(f)["retenues"]
    # garde 7 : aucun témoin dans la sélection
    if set(retenues) & set(par_ident_t):
        raise TemoinRetenu(f"témoin dans la sélection de {tache} : refus")
    ga = oracle.gain_archive(archive_jugement)
    for c in passees:
        g, d = oracle.gain(c["loi_predictive"]), oracle.divergence(c["loi_predictive"])
        v = verdicts.get(c["identifiant"])
        releve_cartes.append({"bras": bras, "generation": generation, "identifiant": c["identifiant"], "temoin": None, "gardien": "passe",
                              "promue": c["identifiant"] in promues, "verdict": v,
                              "contre_calcul_ok": cc[c["identifiant"]]["ok"] if c["identifiant"] in cc else None,
                              "gain_nat": round(g, 6), "delta_gain_nat": round(g - ga, 6), "divergence_nat": round(d, 6),
                              "log_e": detail[c["identifiant"]].get("log_e"), "retenue": c["identifiant"] in retenues})
    for ident, motif in refusees.items():
        if not any(x["identifiant"] == ident for x in releve_cartes):
            releve_cartes.append({"bras": bras, "generation": generation, "identifiant": ident, "temoin": None, "gardien": "refuse",
                                  "promue": False, "verdict": None, "contre_calcul_ok": None, "gain_nat": None, "delta_gain_nat": None,
                                  "divergence_nat": None, "motif": motif})
    for nom, c in temoins:
        ident = c["identifiant"]
        passe = nom not in temoins_refuses
        releve_cartes.append({"bras": bras, "generation": generation, "identifiant": ident, "temoin": nom,
                              "gardien": "passe" if passe else "refuse", "promue": ident in promus_temoins,
                              "verdict": verdicts_t.get(ident), "contre_calcul_ok": cc_t[ident]["ok"] if ident in cc_t else None,
                              "log_e": detail.get(ident, {}).get("log_e"), "motif": temoins_refuses.get(nom)})
    comptes = {"proposees": len(cartes) + len([r for r in refusees if r not in {c["identifiant"] for c in cartes}]),
               "refusees_au_gardien": len(refusees), "jugees": len(passees), "m_e_bh": m, "promues": len(promues),
               "testees": len(verdicts), "retenues": len(retenues), "temoins_promus": len(promus_temoins),
               "temoins_testes": len(verdicts_t), "motifs_du_proposeur": motifs_proposeur, "appels_proposeurs": appels}
    graines = {"tache": tache, "par_carte": {i: d["graines"] for i, d in detail.items()}}
    sha_bilan = bf.ecrire_bilan_generation(dossier, generation=generation, bras=bras, cartes=passees, resume_etage=resume,
                                           chemin_selection=chemin_sel, sha_selection=sha_sel, archive_precedente=heritage["archive"],
                                           heritage_lu=heritage, comptes=comptes, graines=graines)
    ligne = {"evenement": "generation", "etage": 1, "bras": bras, "generation": generation, "heritage_lu": heritage.get("bilan_sha256"),
             "archive_lue": sorted(heritage["archive"]), "archive_de_jugement": sorted(archive_jugement), "refusees_au_gardien": refusees,
             "temoins_refuses": temoins_refuses, "promues": promues, "temoins_promus": promus_temoins,
             "verdicts": verdicts, "verdicts_temoins": verdicts_t, "retenues": retenues, "comptes": comptes,
             "bac_a_sable": description_bac.get("nom"), "factice": description_bac.get("factice"), "selection_sha256": sha_sel,
             "selection_temoins_sha256": sha_sel_t, "bilan_sha256": sha_bilan,
             "juge": {i: {k: d.get(k) for k in ("promue", "promue_seule", "log_richesse_max", "log_e", "membres_d_archive", "empreinte_engagement", "temoin")}
                      for i, d in detail.items()}, "depense": compteur.etat()}
    journal.append(ligne)
    return sha_bilan, ligne


# --- l'étage 1 entier : générations, ordre des bras, D7, relevé ---------------------------------------------------------------


def exiger_sans_temoin(heritage, temoins_ids):
    """Garde 7 : aucun identifiant de témoin dans l'archive ni dans la vue."""
    vue = bf.vue_pour_proposeur(heritage)
    presents = sorted(set(heritage.get("archive") or {}) & temoins_ids) + sorted({x["identifiant"] for x in vue["lois_retenues"]} & temoins_ids)
    if presents:
        raise TemoinRetenu(f"témoin(s) dans l'archive ou la vue : {presents} : refus")


def jouer_etage_1(sortie, *, monde, racine, plan, decisions, proposeurs, adaptateur_etage, roles, fabrique_executeur, compteur,
                  moteur="simule"):
    """Trois bras, `plan['generations']` générations ; dans chaque génération l'ordre est réel → recopie-mélange → aléatoire.
    Rend (relevé de l'étage 1, journal). Un `ArretTour` porte le relevé partiel dans `partiel`."""
    verifier_decisions(decisions)
    exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                             (roles["verificateur"][0], roles["familles"]["verificateur"]))
    oracle = Oracle(monde["loi"], racine, DIM)
    journal, releve_cartes, lectures, incidents = [], [], [], []
    jouees = {b: [] for b in BRAS_ETAGE1}
    etat = {b: {"dossier_prec": None, "sha_prec": None} for b in BRAS_ETAGE1}
    temoins_ids = set()
    archive_reel_courante = {}
    arret = None
    try:
        for g in range(1, plan["generations"] + 1):
            for bras in BRAS_ETAGE1:
                d = os.path.join(sortie, f"bras-{bras}", f"generation-{g}")
                os.makedirs(d)
                if g == 1:
                    heritage = bf.heritage_initial()
                else:
                    src = etat["reel" if bras == "recopie_melange" else bras]
                    try:
                        heritage = bf.lire_heritage(src["dossier_prec"], src["sha_prec"])
                    except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:
                        incidents.append({"bras": bras, "generation": g, "type": type(e).__name__, "motif": str(e)[:300]})
                        raise ArretTour(f"héritage refusé ({type(e).__name__}) : arrêt", {}) from e
                    lectures.append({"bras": bras, "generation": g, "attendu": src["sha_prec"], "lu": heritage["bilan_sha256"]})
                    journal.append({"evenement": "heritage-lu", "bras": bras, "generation": g, "bilan_sha256": heritage["bilan_sha256"],
                                    "source": "reel" if bras == "recopie_melange" else bras, "archive": sorted(heritage["archive"])})
                exiger_sans_temoin(heritage, temoins_ids)
                if bras == "recopie_melange" and not heritage["archive"]:  # ne joue pas : aucune carte, aucun témoin (passe non jouée)
                    journal.append({"evenement": "generation-non-jouee", "bras": bras, "generation": g,
                                    "motif": "archive du bras réel vide : aucune carte à recopier ni à mélanger (aucun repli)"})
                    etat[bras] = {"dossier_prec": d, "sha_prec": None}
                    continue
                if bras == "reel" or decisions["d7"] == "archive_propre" or bras == "recopie_melange":
                    archive_jugement = heritage["archive"]
                else:  # D7 « archive_du_bras_reel » : le bras aléatoire est jugé contre l'archive du bras réel de la génération
                    archive_jugement = archive_reel_courante
                sha, ligne = jouer_generation(d, bras, g, monde, heritage, archive_jugement, racine, fabrique_executeur, proposeurs,
                                              adaptateur_etage, roles, decisions, plan, oracle, compteur, journal, releve_cartes, moteur)
                temoins_ids |= {x["identifiant"] for x in releve_cartes if x.get("temoin")}
                jouees[bras].append(g)
                if bras == "reel":
                    archive_reel_courante = heritage["archive"]
                etat[bras] = {"dossier_prec": d, "sha_prec": sha}  # D7 « archive_du_bras_reel » : le bilan du bras aléatoire est
                # lu (boucle vérifiée) mais son archive n'est jamais utilisée au jugement ni servie (vue jamais lue)
        for bras in BRAS_ETAGE1:
            if etat[bras]["sha_prec"]:
                fin = bf.lire_heritage(etat[bras]["dossier_prec"], etat[bras]["sha_prec"])
                exiger_sans_temoin(fin, temoins_ids)
                journal.append({"evenement": "heritage-final-lu", "bras": bras, "bilan_sha256": etat[bras]["sha_prec"], "archive": sorted(fin["archive"])})
    except ArretTour as e:
        arret = str(e)
        journal.append({"evenement": "arret", "motif": arret, "depense": compteur.etat()})
    releve = {"version": VERSION, "etage": 1, "arret": arret, "generations_jouees": jouees,
              "boucle": {"incidents": incidents, "lectures": lectures}, "cartes": releve_cartes,
              "decisions": dict(decisions), "plan": dict(plan), "depense": compteur.etat(),
              "vd_distinctes": {}, "recherche_loi_plantee": []}
    if arret:
        raise ArretTour(arret, {"releve": releve, "journal": journal})
    return releve, journal


def manifeste_tour(**champs):
    """Manifeste R9 : commit, versions (Python, numpy, bwrap), ordre des bras, décisions, plan, racine des graines."""
    try:
        np_v = __import__("numpy").__version__
    except ImportError:
        np_v = None
    try:
        bw = subprocess.run(["bwrap", "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        bw = None
    try:
        racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        commit = subprocess.run(["git", "-C", racine, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or "inconnu"
        modifie = bool(subprocess.run(["git", "-C", racine, "status", "--porcelain"], capture_output=True, text=True, timeout=30).stdout.strip())
    except (OSError, subprocess.SubprocessError):
        commit, modifie = "inconnu", None
    return dict({"version": VERSION, "python": platform.python_version(), "numpy": np_v, "bwrap": bw,
                 "depot": {"commit": commit, "arbre_modifie": modifie}, "ordre_des_bras": list(BRAS_ETAGE1),
                 "regle_des_graines": "SeedSequence(E, spawn_key=(cle_de_tache(tâche),)) ; tâches « tour-ferme-v61|etage=<e>|bras=<b>|generation=<g>|… »"},
                **champs)


__all__ = ("jouer_etage_1", "jouer_generation", "juger", "completer_carte", "temoins_du_monde", "garder", "contre_calculer",
           "statistique_hors_bac", "exiger_familles_separees", "exiger_sans_temoin", "verifier_decisions", "Compteur",
           "ProposeurScripte", "ProposeurAdaptateur", "contexte_du_proposeur", "extraire_propositions", "manifeste_tour",
           "TourRefuse", "TemoinRetenu", "FamillesNonSeparees", "ArretTour", "VERSION", "BRAS_ETAGE1", "TEMOINS", "DECISIONS", "ALPHA")
