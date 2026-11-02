"""Cœur du tour fermé, version 62 (fichier neuf, R12 ; tâches A2 et A4) — **étage 1 seul** (monde à loi plantée, trois bras).

Préenregistrement : `prereg/preenregistrement-tour-ferme-v1-brouillon3.md` (étage 1 ; le texte de l'étage 2 y est hors de ce
scellement). Contre-lecture appliquée : `prereg/contre-lecture-preenregistrement-tour-ferme-v2.md` (B7, B8, B9, C8 à C21 pour
l'étage 1). Ce module **ne lit aucune issue** : il produit le relevé que lit `pole/lecture_tour_ferme_v62.py`.

Ce qui change par rapport à la v61 (`pole/tour_ferme_v61.py`, inchangée) :

1. **B7, C8 — la loi éprouvée est servie à l'expérimentateur** : le texte du test de mort de chaque carte et de chaque témoin
   porte sa loi gelée en JSON canonique (au plus `TAILLE_MAX_LOI_SERVIE` caractères ; au-delà, refus motivé au gardien), et la
   tranche porte l'évaluateur de référence `evaluateur_lois_v62.py` (même empreinte pour toutes les fiches), nommé dans les
   données du test : l'expérimentateur reçoit l'un et l'autre **dans le préenregistrement court**, par le seul chemin de l'étage.
2. **B8, C9 — la grammaire des lois est servie aux proposeurs** (consigne et contexte) : champs exacts de chaque type, un exemple
   valide par type, bornes ; le gardien accepte exactement cette grammaire (types, champs, structure, bornes de sûreté, taille),
   le même pour les trois bras et les témoins ; la borne ±4 des poids et biais de softmax est celle du gabarit des proposeurs.
3. **I10, C12 — arrêts scellés** : toute exception d'une génération devient `ArretTour` avec le relevé partiel ; un proposeur
   dont la session n'est pas « ok » (refus R-764 compris, modèle servi contrôlé) arrête la course, jamais « réponse illisible ».
4. **I12, C13 — parts des relais** : compteur par relais, part fixée au plan ; arrêt avant un étage si la part restante d'un
   relais est sous son pire cas (cartes × plafond par fiche de son rôle) ; « budget_depasse » d'un relais hors du plafond de la
   fiche → arrêt.
5. **I14, C14 — pleine précision** exigée dans le gabarit du test ; un désaccord du contre-calcul **arrête** la course (garde 10,
   choix gardé) ; l'empreinte de la copie de la tranche est vérifiée contre l'index avant le contre-calcul.
6. **I15, C15 — étage servi à l'aveugle** : identifiant opaque `F-<12 hex>` (empreinte de l'identifiant réel) pour toute carte
   et tout témoin, titre et hypothèse neutres ; la correspondance est gardée par l'orchestrateur (relevé).
7. **I16 à I18, C16, mineur 19** : le relevé porte la taille de l'archive de jugement par carte, la recherche de la loi plantée
   faite sur chaque contexte servi (`recherche_loi_plantee`, calculée) et les découvertes distinctes (`vd_distinctes`).
8. **I23, C19** : la recopie de la génération g lit le bilan du bras réel de g−1 (même nul que les cartes réelles de g).
9. **I22, C11 ; C21** : l'environnement et la liste permise de l'étage sont ceux que passe le lanceur (mode réel : environnement du
   processus) ; le mot « moteur » de l'étage est passé par le lanceur (mode réel : « claude-sdk », coûts réels, exécuteur
   factice refusé par l'étage).

Aucun réseau ici ; les adaptateurs réels sont construits par le lanceur `demonstrations/tour_ferme_v62.py`.
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
from .adaptateurs import Resultat, controle_modele_resultat
from .cycle import appliquer_multiplicite
from .etage_entre_generations_v53 import preparer_generation
from .etage_entre_generations_v57 import NOM_SELECTION, jouer_etage_v57, selection_entre_generations
from .fiches_v53 import preparer
from .oracle_tour_ferme_v60 import Oracle, classer, matrice
from .outils import ecrire_json_scelle, empreinte_objet, json_canonique, nombre_fini, sha256_fichier

VERSION = "tour-ferme-v62"
ALPHA = 0.05
K, DIM = pr.K, pr.DIM
BRAS_ETAGE1 = ("reel", "recopie_melange", "aleatoire")  # ordre de jeu dans une génération (D4, D7)
TEMOINS = ("T-VRAIE", "T-F1", "T-F2", "T-F4", "T-ANTI", "T-ELIM", "T-MAL")
CLES_PROPOSITION = ("enonce", "loi_predictive")
LONGUEUR_ENONCE = 400
DECISIONS = {"d7": ("archive_du_bras_reel", "archive_propre"), "d9": ("mecanique", "aiguilleur")}
TOLERANCE_CONTRE_CALCUL = 1e-6
TYPES_PERMIS = ("softmax", "par_sous_population", "si_sinon", "melange", "fixe", "transformee")
CHAMPS_PAR_TYPE = {"fixe": ({"type", "probas"}, set()), "softmax": ({"type", "poids", "biais"}, set()),
                   "par_sous_population": ({"type", "lois"}, {"defaut"}), "melange": ({"type", "composantes", "poids"}, set()),
                   "si_sinon": ({"type", "condition", "si", "sinon"}, set()),
                   "transformee": ({"type", "base"}, {"melange_aveugle", "puissance", "inclinaison", "oscillation"})}
BORNE_GABARIT = pr.BORNE  # ±4 : poids et biais de softmax d'une proposition (gabarit des proposeurs)
BORNE_SURETE = 50.0  # inclinaison, amplitude, puissance : bornes de sûreté du calcul (tous bras, témoins compris)
TAILLE_MAX_LOI_SERVIE = 2000  # caractères du JSON canonique de la loi servie dans le texte du test (≤ 3 000 au total)
FICHIER_EVALUATEUR = "evaluateur_lois_v62.py"
CHEMIN_EVALUATEUR = os.path.join(os.path.dirname(os.path.abspath(__file__)), FICHIER_EVALUATEUR)
MARQUE_LOI = "Loi gelée L (JSON canonique) : "
TITRE_NEUTRE = "Loi à éprouver"
HYPOTHESE_NEUTRE = "La loi gelée L prédit l'issue mieux que la marginale empirique de la tranche."
MEMOIRE_BAC_MO = 768  # la borne que tient l'exécuteur du bac (`a_blanc_v59.choisir_executeur`), annoncée dans la consigne
SEUIL_TEST, SEUIL_T_ELIM = "au moins 0,02", "au moins 2,0"
ENV_A_BLANC = dict(A.ENV_A_BLANC)  # déclaration du mode à blanc ; le mode réel passe l'environnement du processus (C11)
DEUX_DECIMALES = 0.005

GRAMMAIRE = {
    "regles": ("Trois issues (0, 1, 2), deux traits réels z0 et z1, sous-population g dans {0, 1}. Une loi est un objet JSON de "
               "l'un des six types ci-dessous, avec exactement ses champs (aucun autre). Probabilité d'une issue : celle que "
               "donne la loi, chaque probabilité relevée au plancher 1e-12 puis renormalisée. JSON canonique de la loi : "
               f"au plus {TAILLE_MAX_LOI_SERVIE} caractères. Softmax d'une proposition : chaque poids et chaque biais dans "
               f"[−{BORNE_GABARIT:g} ; {BORNE_GABARIT:g}]. Inclinaison et amplitude : valeur absolue ≤ {BORNE_SURETE:g} ; "
               f"puissance dans ]0 ; {BORNE_SURETE:g}]."),
    "types": {
        "fixe": {"champs": {"type": "\"fixe\"", "probas": "3 nombres ≥ 0 de somme > 0 (normalisés)"},
                 "exemple": {"type": "fixe", "probas": [0.5, 0.25, 0.25]}},
        "softmax": {"champs": {"type": "\"softmax\"", "poids": "3 lignes (une par issue) de 2 nombres (coefficients de z0, z1)",
                               "biais": "3 nombres (un par issue)"},
                    "formule": "p(k) ∝ exp(biais[k] + poids[k][0]·z0 + poids[k][1]·z1)",
                    "exemple": {"type": "softmax", "poids": [[1.0, -0.5], [0.0, 0.0], [-1.0, 0.5]], "biais": [0.0, 0.25, -0.25]}},
        "par_sous_population": {"champs": {"type": "\"par_sous_population\"",
                                           "lois": "objet {\"0\": loi, \"1\": loi} (clé : la sous-population g, en texte)",
                                           "defaut": "facultatif : loi des sous-populations absentes de « lois » (exigé si une "
                                                     "clé manque)"},
                                "exemple": {"type": "par_sous_population",
                                            "lois": {"0": {"type": "fixe", "probas": [0.5, 0.25, 0.25]},
                                                     "1": {"type": "softmax", "poids": [[0.5, 0.0], [0.0, 0.5], [0.0, 0.0]],
                                                           "biais": [0.0, 0.0, 0.0]}}}},
        "melange": {"champs": {"type": "\"melange\"", "composantes": "liste non vide de lois",
                               "poids": "un poids ≥ 0 par composante, de somme 1"},
                    "exemple": {"type": "melange", "composantes": [{"type": "fixe", "probas": [1.0, 1.0, 1.0]},
                                                                   {"type": "softmax", "poids": [[0.5, 0.0], [0.0, 0.0], [-0.5, 0.0]],
                                                                    "biais": [0.0, 0.0, 0.0]}], "poids": [0.25, 0.75]}},
        "si_sinon": {"champs": {"type": "\"si_sinon\"",
                                "condition": "{\"sous_population\": 0 ou 1} (vraie si g vaut cette valeur), ou {\"indice\": 0 ou "
                                             "1, \"seuil\": nombre facultatif, 0 par défaut} (vraie si z[indice] > seuil)",
                                "si": "loi si la condition est vraie", "sinon": "loi sinon"},
                     "exemple": {"type": "si_sinon", "condition": {"indice": 1, "seuil": 0.5},
                                 "si": {"type": "fixe", "probas": [0.25, 0.5, 0.25]},
                                 "sinon": {"type": "fixe", "probas": [0.25, 0.25, 0.5]}}},
        "transformee": {"champs": {"type": "\"transformee\"", "base": "loi",
                                   "melange_aveugle": "facultatif : {\"lambda\": nombre dans [0 ; 1], \"probas\": 3 nombres ≥ 0} "
                                                      "(p ← (1 − lambda)·p + lambda·probas normalisées)",
                                   "puissance": "facultatif : nombre > 0 (p ← p^puissance, renormalisé)",
                                   "inclinaison": "facultatif : 3 nombres (p(k) ← p(k)·exp(inclinaison[k]), renormalisé)",
                                   "oscillation": "facultatif : {\"amplitude\", \"frequence\", \"trait\": 0 ou 1, \"issue\": 0, 1 "
                                                  "ou 2, \"phase\" facultative} (p(issue) ← p(issue)·exp(amplitude·cos(frequence·"
                                                  "z[trait] + phase)))"},
                        "ordre": "mélange aveugle, puis puissance, puis inclinaison, puis oscillation",
                        "exemple": {"type": "transformee", "base": {"type": "softmax", "poids": [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]],
                                                                    "biais": [0.0, 0.0, 0.0]},
                                    "puissance": 0.5, "inclinaison": [0.0, 0.25, -0.25]}},
    }}
CONSIGNE_PROPOSEUR = ("Propose au plus {n} lois qui prédisent l'issue mieux que la marginale et mieux que les lois déjà "
                      "retenues. Réponds par un bloc JSON : une liste d'objets {{\"enonce\": texte (≤ 400 caractères), "
                      "\"loi_predictive\": loi}}, et rien d'autre. Une loi suit exactement la grammaire servie dans le contexte "
                      "(« gabarit » → « grammaire » : types, champs exacts, un exemple valide par type, bornes) ; toute autre clé, "
                      "tout autre type ou toute borne dépassée est refusé au gardien. Rien d'autre n'est à proposer : le test de "
                      "mort, son seuil, sa statistique et ses données sont fixés par l'orchestrateur.")


class TourRefuse(RuntimeError):
    """Refus avant tout appel (plan, décisions, familles, bac, gabarit du monde) : code 2, rien d'écrit."""


class TemoinRetenu(TourRefuse):
    """Un témoin est entré dans une sélection, une archive ou une vue (garde 7)."""


class FamillesNonSeparees(TourRefuse):
    """Expérimentateur et vérificateur de la même famille (garde 9)."""


class ArretTour(RuntimeError):
    """Arrêt de la liste d'arrêt (plafond de dépense, part d'un relais, durée, contre-calcul en désaccord, session en échec,
    refus de modèle, héritage refusé…) ; `partiel` porte la trace ; `cout` la dépense de l'appel qui l'a levé (proposeur)."""

    def __init__(self, motif, partiel=None, cout=0.0):
        super().__init__(motif)
        self.partiel = partiel or {}
        self.cout = float(cout or 0.0)


# --- plan et décisions ---------------------------------------------------------------------------------------------------


def verifier_decisions(decisions):
    """Les décisions D7 et D9 lues dans le plan gelé de l'étage 1 : chacune parmi ses valeurs permises."""
    if not isinstance(decisions, dict) or set(decisions) != set(DECISIONS):
        raise TourRefuse(f"décisions attendues {sorted(DECISIONS)}, reçues {sorted(decisions) if isinstance(decisions, dict) else decisions!r}")
    for k, permises in DECISIONS.items():
        if decisions[k] not in permises:
            raise TourRefuse(f"décision {k.upper()} = {decisions[k]!r} ; permises : {permises}")
    if decisions["d9"] == "aiguilleur":
        raise TourRefuse("décision D9 = aiguilleur : gardien modèle non écrit dans cette version (refus avant tout appel)")
    return dict(decisions)


class Compteur:
    """Plafond dur de dépense et de durée de l'étage (gardes 5 et 13) et parts des relais (C13) ; lève `ArretTour`."""

    def __init__(self, plafond_usd, duree_max_s, parts=None, horloge=time.time):
        self.plafond_usd, self.duree_max_s, self.horloge = float(plafond_usd), float(duree_max_s), horloge
        self.parts = {k: float(v) for k, v in (parts or {}).items()}
        self.debut, self.usd, self.appels = horloge(), 0.0, 0
        self.par_role, self.par_relais = {}, {k: 0.0 for k in self.parts}

    def ajouter(self, usd, role, relais=None):
        self.appels += 1
        self.usd += float(usd)
        self.par_role[role] = round(self.par_role.get(role, 0.0) + float(usd), 6)
        if relais is not None:
            self.par_relais[relais] = self.par_relais.get(relais, 0.0) + float(usd)
            if relais in self.parts and self.par_relais[relais] > self.parts[relais] + 1e-9:
                raise ArretTour(f"part du relais {relais} franchie : {self.par_relais[relais]:.4f} USD > {self.parts[relais]} USD")
        if self.usd > self.plafond_usd:
            raise ArretTour(f"plafond de dépense de l'étage franchi : {self.usd:.4f} USD > {self.plafond_usd} USD")
        self.verifier_duree()

    def verifier_parts_avant_etage(self, besoins):
        """Avant un étage de tests de mort : la part restante de chaque relais doit couvrir son pire cas ({relais: USD})."""
        for relais, besoin in sorted(besoins.items()):
            if relais in self.parts and self.parts[relais] - self.par_relais.get(relais, 0.0) < besoin - 1e-9:
                raise ArretTour(f"part restante du relais {relais} ({self.parts[relais] - self.par_relais.get(relais, 0.0):.4f} USD) "
                                f"sous le pire cas de l'étage ({besoin:.4f} USD) : arrêt avant l'étage (C13)")
        restant = self.plafond_usd - self.usd
        if sum(besoins.values()) > restant + 1e-9 and not self.parts:
            raise ArretTour(f"plafond restant de l'étage ({restant:.4f} USD) sous le pire cas de l'étage ({sum(besoins.values()):.4f} USD)")

    def verifier_duree(self):
        if self.horloge() - self.debut > self.duree_max_s:
            raise ArretTour(f"plafond de durée de l'étage franchi : {self.horloge() - self.debut:.0f} s > {self.duree_max_s:.0f} s")

    def etat(self):
        return {"appels": self.appels, "depense_usd": round(self.usd, 6), "par_role_usd": dict(self.par_role),
                "par_relais_usd": {k: round(v, 6) for k, v in self.par_relais.items()}, "parts_usd": dict(self.parts),
                "duree_s": round(self.horloge() - self.debut, 1)}


# --- grammaire des lois (C9) et gabarit (garde 8) ---------------------------------------------------------------------------


def _nombres(x):
    return isinstance(x, list) and all(nombre_fini(v) for v in x)


def verifier_loi_servable(loi, borne_softmax=None, profondeur=0):
    """Rend None si `loi` suit exactement la grammaire servie (types, champs, structure, bornes de sûreté, taille), le motif sinon.
    `borne_softmax` (gabarit des proposeurs) : poids et biais de chaque softmax dans [−borne ; borne]."""
    if profondeur == 0:
        try:
            sp.valider_loi(loi, K, DIM)
        except Exception as e:  # noqa: BLE001 — tout refus de la loi est un refus de forme, motif dit
            return f"loi invalide : {type(e).__name__} : {str(e)[:160]}"
        n = len(json_canonique(loi).decode("utf-8"))
        if n > TAILLE_MAX_LOI_SERVIE:
            return f"loi trop longue pour être servie à l'expérimentateur : {n} > {TAILLE_MAX_LOI_SERVIE} caractères (JSON canonique)"
    if profondeur > 40:
        return "loi trop imbriquée (plus de 40 niveaux)"
    if not isinstance(loi, dict) or loi.get("type") not in TYPES_PERMIS:
        return f"type de loi hors de la grammaire servie : {loi.get('type') if isinstance(loi, dict) else loi!r} (permis : {', '.join(TYPES_PERMIS)})"
    t = loi["type"]
    requis, facultatifs = CHAMPS_PAR_TYPE[t]
    if not requis <= set(loi) or set(loi) - requis - facultatifs:
        return f"{t} : champs exacts {sorted(requis)} (+ facultatifs {sorted(facultatifs)}), reçus {sorted(loi)}"
    sous = []
    if t == "fixe":
        if len(loi["probas"]) != K:
            return "fixe : 3 probabilités"
    elif t == "softmax":
        if borne_softmax is not None and any(abs(v) > borne_softmax for v in [w for l in loi["poids"] for w in l] + list(loi["biais"])):
            return f"softmax : poids et biais dans [−{borne_softmax:g} ; {borne_softmax:g}] (gabarit des proposeurs)"
    elif t == "par_sous_population":
        cles = set(loi["lois"])
        if not cles <= {"0", "1"}:
            return "par_sous_population : clés de « lois » parmi \"0\" et \"1\""
        if cles != {"0", "1"} and "defaut" not in loi:
            return "par_sous_population : les deux sous-populations, ou une loi « defaut »"
        sous = list(loi["lois"].values()) + ([loi["defaut"]] if "defaut" in loi else [])
    elif t == "melange":
        sous = list(loi["composantes"])
    elif t == "si_sinon":
        c = loi["condition"]
        if set(c) == {"sous_population"}:
            if c["sous_population"] not in (0, 1) or isinstance(c["sous_population"], bool):
                return "si_sinon : sous_population 0 ou 1"
        elif set(c) in ({"indice"}, {"indice", "seuil"}):
            if isinstance(c["indice"], bool) or c["indice"] not in (0, 1) or not nombre_fini(c.get("seuil", 0.0)):
                return "si_sinon : indice 0 ou 1, seuil fini"
        else:
            return "si_sinon : condition {sous_population} ou {indice, seuil facultatif}"
        sous = [loi["si"], loi["sinon"]]
    elif t == "transformee":
        g = loi.get("puissance")
        if g is not None and not (0 < g <= BORNE_SURETE):
            return f"transformee : puissance dans ]0 ; {BORNE_SURETE:g}]"
        b = loi.get("inclinaison")
        if b is not None and (not _nombres(b) or any(abs(x) > BORNE_SURETE for x in b)):
            return f"transformee : inclinaison, 3 nombres de valeur absolue ≤ {BORNE_SURETE:g}"
        m = loi.get("melange_aveugle")
        if m is not None and set(m) != {"lambda", "probas"}:
            return "transformee : melange_aveugle = {lambda, probas} exactement"
        o = loi.get("oscillation")
        if o is not None:
            if not isinstance(o, dict) or not {"amplitude", "frequence", "trait", "issue"} <= set(o) \
                    or set(o) - {"amplitude", "frequence", "trait", "issue", "phase"} or abs(o["amplitude"]) > BORNE_SURETE \
                    or isinstance(o["trait"], bool) or o["trait"] not in (0, 1):
                return f"transformee : oscillation = {{amplitude (|·| ≤ {BORNE_SURETE:g}), frequence, trait 0 ou 1, issue, phase facultative}}"
        sous = [loi["base"]]
    for s in sous:
        motif = verifier_loi_servable(s, borne_softmax, profondeur + 1)
        if motif:
            return motif
    return None


def texte_du_test(loi):
    """Le texte gelé du test de mort v62 : statistique, évaluateur de référence, pleine précision, script attendu, loi gelée."""
    return ("Gain moyen par épisode du log-score de la loi gelée L sur la marginale empirique de la tranche (comptes + 0,5 ; nat), "
            f"calculé sur episodes.csv par l'évaluateur de référence {FICHIER_EVALUATEUR} (même fichier pour toutes les fiches). "
            "gains.csv : colonnes episode, gain ; une ligne par épisode ; valeurs en pleine précision (repr de Python), jamais "
            f"arrondies. Script attendu, tel quel : import json, runpy ; ev = runpy.run_path('tranche/{FICHIER_EVALUATEUR}') ; "
            "ev['ecrire_gains'](json.loads(LOI), 'tranche/episodes.csv', 'gains.csv') ; où LOI est le texte JSON de L ci-dessous, "
            "recopié exactement. " + MARQUE_LOI + json_canonique(loi).decode("utf-8"))


def test_de_mort_impose(loi, seuil=SEUIL_TEST, sans_statistique=False):
    t = {"seuil": seuil, "donnees": ["episodes.csv", FICHIER_EVALUATEUR], "test": texte_du_test(loi),
         "statistique": {"fichier": "gains.csv", "colonne": "gain", "statistique": "moyenne"}}
    if sans_statistique:
        del t["statistique"]
    return t


def loi_du_texte(texte):
    """La loi gelée lue dans un texte de test (après `MARQUE_LOI`), ou None : ce que lit l'expérimentateur."""
    i = (texte or "").find(MARQUE_LOI)
    if i < 0:
        return None
    try:
        return json.JSONDecoder().raw_decode(texte, i + len(MARQUE_LOI))[0]
    except ValueError:
        return None


def identifiant_opaque(racine, tache, ident_reel):
    """C15 : identifiant servi à l'étage et aux proposeurs, le même format pour toute carte et tout témoin."""
    return "F-" + hashlib.sha256(f"{racine}|{tache}|{ident_reel}".encode("utf-8")).hexdigest()[:12]


def carte_servie(ident_servi, loi, source, seuil=SEUIL_TEST, sans_statistique=False):
    """Une carte au gabarit du pôle, servie à l'aveugle (C15) : identifiant opaque, titre et hypothèse neutres, test imposé."""
    c = pr.carte(ident_servi, TITRE_NEUTRE, loi, source, test_de_mort=test_de_mort_impose(loi, seuil, sans_statistique),
                 hypothese=HYPOTHESE_NEUTRE)
    c["prediction"] = f"gain moyen de log-score {seuil} nat par épisode"
    return c


def temoins_du_monde(monde, racine, tache):
    """Les sept témoins d'une génération d'un bras : (nom, identifiant réel, carte servie)."""
    v = monde["loi"]
    anti = {"type": "softmax", "poids": [[-w for w in ligne] for ligne in v["poids"]], "biais": list(v["biais"])}
    lois = {"T-VRAIE": v, "T-F1": monde["fausses"]["S-F1"], "T-F2": monde["fausses"]["S-F2"], "T-F4": monde["fausses"]["S-F4"],
            "T-ANTI": anti, "T-ELIM": {"type": "transformee", "base": v, "puissance": 1.25}, "T-MAL": v}
    out = []
    for nom in TEMOINS:
        reel = "W-" + hashlib.sha256(f"{racine}|{tache}|{nom}".encode("utf-8")).hexdigest()[:12]
        servi = identifiant_opaque(racine, tache, reel)
        c = carte_servie(servi, lois[nom], "temoin", seuil=SEUIL_T_ELIM if nom == "T-ELIM" else SEUIL_TEST,
                         sans_statistique=nom == "T-MAL")
        out.append((nom, reel, c))
    return out


def completer_carte(proposition, ident_servi):
    """Garde 8 : la proposition doit être exactement au gabarit fermé (clés, énoncé, loi de la grammaire servie, bornes ±4) ;
    l'orchestrateur complète tout le reste (test de mort imposé, carte servie). Rend (carte, None) ou (None, motif)."""
    if not isinstance(proposition, dict):
        return None, "proposition non dictionnaire"
    en_trop = sorted(set(proposition) - set(CLES_PROPOSITION))
    manquantes = [k for k in CLES_PROPOSITION if k not in proposition]
    if en_trop or manquantes:
        return None, f"gabarit du proposeur : clés en trop {en_trop}, manquantes {manquantes} (le test de mort est imposé)"
    enonce = proposition["enonce"]
    if not isinstance(enonce, str) or not enonce.strip() or len(enonce) > LONGUEUR_ENONCE:
        return None, f"énoncé : texte non vide de {LONGUEUR_ENONCE} caractères au plus attendu"
    motif = verifier_loi_servable(proposition["loi_predictive"], borne_softmax=BORNE_GABARIT)
    if motif:
        return None, f"gabarit du proposeur : {motif}"
    return carte_servie(ident_servi, proposition["loi_predictive"], "reel"), None


def garder(carte, decisions):
    """Gardien de la décision D9 (« mecanique ») : `a_blanc_v59.garder` puis la grammaire servie (types, champs, bornes de sûreté,
    taille de la loi servie), le même pour les trois bras et les témoins."""
    if decisions["d9"] != "mecanique":
        raise TourRefuse(f"gardien {decisions['d9']!r} non écrit")
    passeport, motif = A.garder(carte)
    if passeport is None:
        return None, motif
    motif = verifier_loi_servable(carte["loi_predictive"])
    if motif:
        return None, f"grammaire servie : {motif}"
    return passeport, None


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


class ProposeurAdaptateur:
    """Proposeur du chemin réel **et** du mode à blanc (C12) : un appel par génération par un adaptateur du pôle (rôle
    « proposeur ») ; tout statut autre que « ok », toute erreur, tout refus R-764 ou modèle servi non conforme → `ArretTour`."""

    def __init__(self, nom, relais, adaptateur, dossier, budget_usd, modele):
        self.nom, self.relais, self.ad, self.dossier, self.budget, self.modele = nom, relais, adaptateur, dossier, budget_usd, modele
        self.appels = []

    def proposer(self, consigne, contexte, tache):
        d = os.path.join(self.dossier, re.sub(r"[^A-Za-z0-9=|-]", "_", tache))
        os.makedirs(d, exist_ok=True)
        texte = consigne + "\n\n```json\n" + json.dumps(contexte, ensure_ascii=False) + "\n```\n"
        r = self.ad.lancer("proposeur", texte, d, self.budget, 1, modele=self.modele)
        cout = float(r.cout_declare_usd or 0.0)
        refus = getattr(r, "refus", None)
        if refus is None and r.statut != "refus":
            refus = controle_modele_resultat(self.modele, r, getattr(self.ad, "modeles_servis_permis", None))
        self.appels.append({"tache": tache, "statut": r.statut, "cout_usd": cout, "refus": refus, "erreur": r.erreur,
                            "consigne_sha256": hashlib.sha256(texte.encode()).hexdigest()})
        if r.statut != "ok" or r.erreur or refus is not None:
            raise ArretTour(f"proposeur {self.nom} : session {r.statut!r}, erreur {str(r.erreur)[:200]!r}, refus {refus!r} : arrêt "
                            "(garde 13 ; jamais « réponse illisible »)", cout=cout)
        brut = getattr(r, "texte_brut", None)
        return (brut if isinstance(brut, str) and brut else r.texte_final), cout


def episodes_de_developpement(monde, racine, tache, n_dev=200):
    rng = random.Random(bf.graine_de_tache(racine, f"{tache}|developpement"))
    return [{"z": [round(z, 6) for z in x["z"]], "g": x["g"], "y": sp.tirer_categorie(rng, sp.proba(monde["loi"], x, [], 0))}
            for x in sp.tirer_instances(rng, n_dev, DIM)]


def contexte_du_proposeur(monde, vue, racine, tache, n_dev=200):
    """Description publique du monde, gabarit **avec la grammaire exacte des lois** (C9), lois retenues (vue v59, vérifiée,
    identifiants opaques) et épisodes de développement ; jamais une issue de l'épreuve, jamais un verdict."""
    bf.exiger_vue_sans_verdict(vue)
    return {"monde": {"traits": DIM, "sous_populations": 2, "issues": K, "enonce_public": "monde synthétique à loi inconnue"},
            "gabarit": {"types": list(TYPES_PERMIS), "borne_des_poids": BORNE_GABARIT, "cartes_max": 6,
                        "grammaire": json.loads(json.dumps(GRAMMAIRE))},
            "lois_retenues": vue["lois_retenues"], "episodes_developpement": episodes_de_developpement(monde, racine, tache, n_dev)}


# --- recherche de la loi plantée dans les contextes servis (S1, point 3 ; C16) -------------------------------------------------


def _nombres_de(objet, chemin="$"):
    if isinstance(objet, bool):
        return
    if isinstance(objet, (int, float)):
        yield chemin, float(objet), repr(objet)
    elif isinstance(objet, str):
        for m in re.finditer(r"-?\d+\.\d+", objet):
            yield chemin + f"@{m.start()}", float(m.group(0)), m.group(0)
    elif isinstance(objet, dict):
        for k, v in objet.items():
            yield from _nombres_de(v, f"{chemin}.{k}")
    elif isinstance(objet, (list, tuple)):
        for i, v in enumerate(objet):
            yield from _nombres_de(v, f"{chemin}[{i}]")


def parametres_de_la_loi_plantee(monde):
    v = monde["loi"]
    return [("poids", i, j, w) for i, l in enumerate(v["poids"]) for j, w in enumerate(l)] + [("biais", i, None, b) for i, b in enumerate(v["biais"])]


def chercher_loi_plantee(monde, consigne, contexte, ou):
    """Touches des paramètres de L* (exacts, ou écrits à deux décimales) parmi les nombres d'une consigne et d'un contexte servis."""
    touches = []
    params = parametres_de_la_loi_plantee(monde)
    for chemin, x, ecrit in list(_nombres_de(consigne, "consigne")) + list(_nombres_de(contexte, "contexte")):
        deux = "." in ecrit and len(ecrit.split(".")[1].rstrip("0")) <= 2
        for nom, i, j, p in params:
            if abs(x - p) <= 1e-9:
                touches.append({"ou": ou, "chemin": chemin, "valeur": ecrit, "parametre": [nom, i, j], "forme": "exacte"})
            elif deux and abs(x - round(p, 2)) <= 1e-12:
                touches.append({"ou": ou, "chemin": chemin, "valeur": ecrit, "parametre": [nom, i, j], "forme": "deux décimales"})
    return touches


def lignes_de_tranche(monde, racine, tache):
    """Les épisodes (z0, z1, g) de la tranche d'une tâche, recalculés depuis la graine (sans écrire de fichier)."""
    rng = random.Random(bf.graine_de_tache(racine, f"{tache}|tranche"))
    out = set()
    for x in sp.tirer_instances(rng, A.EPISODES_TRANCHE, DIM):
        sp.tirer_categorie(rng, sp.proba(monde["loi"], x, [], 0))
        out.add((x["z"][0], x["z"][1], x["g"]))
    return out


# --- juge : cartes contre l'archive, témoins sans archive, e-BH à m fixé, témoins hors famille ----------------------------------


def juger(cartes, temoins, monde, archive, racine, tache, m):
    """Rend (promues cartes, promus témoins, détail, m). Cartes : nul v8 avec membres d'archive, règle e-BH de la famille des
    cartes à m fixé ; témoins : sans membres d'archive, hors famille au seuil m/α (ne pèsent pas sur k*)."""
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


class AdaptateurEtageV62:
    """L'adaptateur de l'étage v5, le même en mode réel et à blanc : expérimentateur et vérificateur routés vers leurs
    adaptateurs (réels : Kimi et Argon ; à blanc : doublures scriptées qui ne lisent que la consigne) ; dépense comptée par relais ;
    « budget_depasse » d'un relais hors du plafond de la fiche (coût déclaré sous le plafond passé, ou part du relais épuisée) →
    `ArretTour` (C13, I12)."""
    nom = "etage-v62"

    def __init__(self, experimentateur, verificateur, relais_experimentateur="kimi", relais_verificateur="argon"):
        self.roles = {v5.ROLE_EXPERIMENTATEUR: (experimentateur, relais_experimentateur),
                      v5.ROLE_LECTEUR: (verificateur, relais_verificateur)}
        self.depense = {relais_experimentateur: 0.0, relais_verificateur: 0.0}
        self.parts, self.appels = {}, []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        if role not in self.roles:
            raise ArretTour(f"rôle inattendu à l'étage : {role}")
        ad, relais = self.roles[role]
        r = ad.lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)
        cout = float(r.cout_declare_usd or 0.0)
        self.depense[relais] = self.depense.get(relais, 0.0) + cout
        self.appels.append({"role": role, "relais": relais, "modele": modele, "cout_usd": cout, "statut": r.statut,
                            "budget_passe_usd": float(budget_usd)})
        part = self.parts.get(relais)
        if r.statut == "budget_depasse" and (cout < float(budget_usd) - 1e-6 or (part is not None and self.depense[relais] >= part - 1e-9)):
            raise ArretTour(f"relais {relais} : « budget_depasse » hors du plafond de la fiche (coût déclaré {cout:.4f} USD, plafond "
                            f"passé {float(budget_usd):.4f} USD, dépense du relais {self.depense[relais]:.4f} USD) : arrêt (garde 5, C13)")
        return r


def statistique_hors_bac(loi, chemin_episodes):
    """Le gabarit gelé du test de mort, recalculé par l'orchestrateur avec `selection_pari.proba` (indépendant de l'évaluateur
    servi) : gain moyen de log-score de la loi sur la marginale empirique de la tranche (comptes + 0,5), nat par épisode."""
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


def contre_calculer(resume, lois, chemin_episodes, sha_attendue=None):
    """Garde 10 : pour chaque fiche testée, valeur du noyau contre la statistique recalculée ; la copie de la tranche est d'abord
    vérifiée contre l'empreinte de l'index (mineur 24 ; écart → `ArretTour`). Rend {ident: {ok, noyau, orchestrateur, verdict}}."""
    if sha_attendue is not None and sha256_fichier(chemin_episodes) != sha_attendue:
        raise ArretTour("contre-calcul : la copie de la tranche n'a pas l'empreinte de l'index : arrêt (garde 10)")
    out = {}
    for r in (resume or {}).get("par_fiche", []):
        if r.get("statut") != "testée":
            continue
        ident, noyau = r["identifiant_auteur"], r.get("verdict_noyau") or {}
        val = noyau.get("valeur_noyau")
        mienne = statistique_hors_bac(lois[ident], chemin_episodes)
        ok = True if val is None else abs(float(val) - mienne) <= TOLERANCE_CONTRE_CALCUL
        out[ident] = {"ok": bool(ok), "noyau": val, "orchestrateur": round(mienne, 12), "verdict": noyau.get("verdict"),
                      "sans_objet": val is None}
    return out


def creer_tranche(dossier, monde, racine, tache):
    """La tranche de l'étage v62 : `episodes.csv` (celle de `a_blanc_v59.creer_tranche`, même graine) **et** l'évaluateur de
    référence, copié octet pour octet (C8) ; index, liste blanche, chargement vérifié par l'étage v5."""
    from . import dossier_ferme as dfm
    from . import ideation_v2 as idn
    rng = random.Random(bf.graine_de_tache(racine, f"{tache}|tranche"))
    lignes = ["episode,z0,z1,g,y"]
    for i, x in enumerate(sp.tirer_instances(rng, A.EPISODES_TRANCHE, DIM), 1):
        y = sp.tirer_categorie(rng, sp.proba(monde["loi"], x, [], 0))
        lignes.append(f"{i},{x['z'][0]!r},{x['z'][1]!r},{x['g']},{y}")
    tr = os.path.join(dossier, "tranche")
    os.makedirs(tr)
    with open(os.path.join(tr, "episodes.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    with open(CHEMIN_EVALUATEUR, "rb") as f:
        octets = f.read()
    with open(os.path.join(tr, FICHIER_EVALUATEUR), "wb") as f:
        f.write(octets)
    dfm.ecrire_index(tr, [{"chemin": "episodes.csv", "titre": "Épisodes du monde",
                           "resume": "traits z0, z1, sous-population g, issue y"},
                          {"chemin": FICHIER_EVALUATEUR, "titre": "Évaluateur de référence des lois",
                           "resume": "proba(loi, instance), gains(loi, chemin), ecrire_gains(loi, chemin, sortie) : bibliothèque standard"}])
    lb = os.path.join(dossier, "liste-blanche.json")
    idn.construire_liste_blanche([os.path.join(tr, "index.json")], lb)
    return v5.charger_tranche(tr, idn.charger_liste_blanche(lb))


def jouer_etage(dossier_etage, cartes, lois_par_ident, monde, racine, tache, executeur, adaptateur, roles, compteur, journal,
                tranche=None, moteur="simule", environnement=None, permis_en_plus=()):
    """L'étage v5 puis la sélection v57 sur `cartes` (cartes servies, ordre des e-valeurs) ; sans carte, sélection vide scellée.
    Rend (résumé, chemin de la sélection, empreinte, tranche, contre-calculs)."""
    if not cartes:
        os.makedirs(dossier_etage)
        chemin = os.path.join(dossier_etage, NOM_SELECTION)
        return None, chemin, ecrire_json_scelle(chemin, selection_entre_generations({"par_fiche": [], "version_etage": None})), tranche, {}
    n = len(cartes)
    compteur.verifier_parts_avant_etage({roles["relais"]["experimentateur"]: n * v5.BUDGET_TEST_USD_DEFAUT,
                                         roles["relais"]["verificateur"]: n * v5.BUDGET_LECTEUR_USD_DEFAUT})
    if tranche is None:
        tranche = creer_tranche(os.path.join(os.path.dirname(dossier_etage), "exploratoire-etage"), monde, racine, tache)
    fiches = {c["identifiant"]: preparer({k: c[k] for k in A.CHAMPS_FICHE}, list(A.CHAMPS_FICHE), ident=c["identifiant"],
                                         case=("tour-ferme", c["source"]), fournisseur="tour-ferme-v62", passe=1) for c in cartes}
    classement = [{"ident": c["identifiant"], "notable": True, "rang": k} for k, c in enumerate(cartes, 1)]
    preparer_generation(dossier_etage, classement, fiches, nombre=n, tranche_index_sha256=tranche.index_sha256,
                        correspondance=A.CORRESPONDANCE, lisible=True)
    reglages = {"tranche": tranche, "nombre": n, "experimentateur": roles["experimentateur"], "lecteur": roles["verificateur"],
                "executeur": executeur, "moteur": moteur, "memoire_mo": MEMOIRE_BAC_MO}
    avant = dict(adaptateur.depense)
    try:
        resume = jouer_etage_v57(adaptateur, dossier_etage, reglages=reglages, environnement=environnement,
                                 permis_en_plus=permis_en_plus)
    finally:
        for relais, usd in adaptateur.depense.items():
            delta = usd - avant.get(relais, 0.0)
            if delta:
                compteur.ajouter(delta, "tests_de_mort", relais)
    chemin_ep = os.path.join(os.path.dirname(dossier_etage), "exploratoire-etage", "tranche", "episodes.csv")
    cc = contre_calculer(resume, lois_par_ident, chemin_ep, tranche.fichiers["episodes.csv"]["sha256"])
    journal.append({"evenement": "etage-tests-de-mort", "tache": tache, "dossier": os.path.basename(dossier_etage),
                    "bac_a_sable": resume["bac_a_sable"].get("nom"), "factice": resume["bac_a_sable"].get("factice"),
                    "tranche_index_sha256": tranche.index_sha256, "comptes": resume["comptes"], "selection_sha256": resume["selection"]["sha256"],
                    "couts_etage": resume.get("couts"), "contre_calcul": cc})
    desaccords = sorted(i for i, x in cc.items() if not x["ok"])
    if desaccords:
        raise ArretTour(f"contre-calcul en désaccord avec le noyau pour {desaccords} (garde 10) : arrêt, aucune issue lue",
                        {"contre_calcul": cc})
    return resume, os.path.join(dossier_etage, NOM_SELECTION), resume["selection"]["sha256"], tranche, cc


# --- une génération d'un bras ------------------------------------------------------------------------------------------------


def _verdicts(resume):
    return {r["identifiant_auteur"]: r["verdict_noyau"]["verdict"] for r in (resume or {}).get("par_fiche", []) if r.get("statut") == "testée"}


def jouer_generation(dossier, bras, generation, monde, heritage, archive_jugement, racine, fabrique_executeur, proposeurs,
                     adaptateur_etage, roles, decisions, plan, oracle, compteur, journal, releve_cartes, recherche,
                     moteur="simule", environnement=None, permis_en_plus=()):
    """Une génération d'un bras : proposition → gardien → juge → étage des cartes et étage des témoins (même tranche) →
    contre-calcul → sélection (cartes seules) → bilan scellé. Rend l'empreinte du bilan et la ligne de journal."""
    tache = f"{VERSION}|etage=1|bras={bras}|generation={generation}"
    vue = bf.vue_pour_proposeur(heritage)
    cartes, refusees, motifs_proposeur, appels, reels = [], {}, [], [], {}
    if bras == "reel":
        contexte = contexte_du_proposeur(monde, vue, racine, tache)
        consigne = CONSIGNE_PROPOSEUR.format(n=plan["cartes_par_proposeur"])
        for p in proposeurs:
            recherche["contextes_cherches"] += 1
            recherche["touches"] += chercher_loi_plantee(monde, consigne, contexte, f"{tache}|proposeur={p.nom}")
            recherche["episodes_servis"] |= {(e["z"][0], e["z"][1], e["g"]) for e in contexte["episodes_developpement"]}
            try:
                texte, cout = p.proposer(consigne, contexte, tache)
            except ArretTour as e:
                compteur.ajouter(e.cout, "proposeur", p.relais)
                raise
            compteur.ajouter(cout, "proposeur", p.relais)
            props, motif = extraire_propositions(texte)
            ignorees = max(0, len(props) - plan["cartes_par_proposeur"])
            appels.append({"proposeur": p.nom, "cout_usd": cout, "propositions": len(props), "ignorees_au_dela_du_maximum": ignorees,
                           "motif": motif})
            if motif:
                motifs_proposeur.append(f"{p.nom} : {motif}")
            for i, prop in enumerate(props[:plan["cartes_par_proposeur"]]):
                ident_reel = f"G{generation}-{p.nom}-{i + 1:02d}"
                ident = identifiant_opaque(racine, tache, ident_reel)
                reels[ident] = ident_reel
                c, motif_c = completer_carte(prop, ident)
                if c is None:
                    refusees[ident] = f"gardien mécanique (gabarit) : {motif_c}"
                else:
                    c["_enonce"] = prop["enonce"]
                    cartes.append(c)
    elif bras in ("aleatoire", "recopie_melange"):
        f = pr.proposer_aleatoire if bras == "aleatoire" else pr.proposer_recopie_melange
        brutes, m = f(vue, plan["cartes_reference"], racine, tache)
        motifs_proposeur = [m] if m else []
        for b in brutes:
            ident = identifiant_opaque(racine, tache, b["identifiant"])
            reels[ident] = b["identifiant"]
            cartes.append(carte_servie(ident, b["loi_predictive"], bras))
    else:
        raise TourRefuse(f"bras inconnu : {bras}")
    enonces = {c["identifiant"]: c.pop("_enonce") for c in cartes if "_enonce" in c}
    temoins = temoins_du_monde(monde, racine, tache)
    reels.update({c["identifiant"]: reel for _, reel, c in temoins})
    passees, temoins_passes, temoins_refuses = [], [], {}
    for c in cartes:
        passeport, motif = garder(c, decisions)
        if passeport is None:
            refusees[c["identifiant"]] = motif
        else:
            passees.append(c)
    for nom, _, c in temoins:
        passeport, motif = garder(c, decisions)
        if passeport is None:
            temoins_refuses[nom] = motif
        else:
            temoins_passes.append((nom, c))
    promues, promus_temoins, detail, m = juger(passees, temoins_passes, monde, archive_jugement, racine, tache, plan["m_e_bh"])
    par_ident = {c["identifiant"]: c for c in passees}
    par_ident_t = {c["identifiant"]: (nom, c) for nom, c in temoins_passes}
    executeur, description_bac = fabrique_executeur()
    resume, chemin_sel, sha_sel, tranche, cc = jouer_etage(
        os.path.join(dossier, bf.DOSSIER_ETAGE), [par_ident[i] for i in promues], {i: c["loi_predictive"] for i, c in par_ident.items()},
        monde, racine, tache, executeur, adaptateur_etage, roles, compteur, journal, moteur=moteur, environnement=environnement,
        permis_en_plus=permis_en_plus)
    executeur_t, _ = fabrique_executeur()
    resume_t, _, sha_sel_t, _, cc_t = jouer_etage(
        os.path.join(dossier, "etage-temoins"), [par_ident_t[i][1] for i in promus_temoins],
        {i: c["loi_predictive"] for i, (_, c) in par_ident_t.items()}, monde, racine, tache, executeur_t, adaptateur_etage, roles,
        compteur, journal, tranche=tranche, moteur=moteur, environnement=environnement, permis_en_plus=permis_en_plus)
    verdicts, verdicts_t = _verdicts(resume), _verdicts(resume_t)
    with open(chemin_sel, encoding="utf-8") as f:
        retenues = json.load(f)["retenues"]
    if set(retenues) & set(par_ident_t):  # garde 7 : aucun témoin dans la sélection
        raise TemoinRetenu(f"témoin dans la sélection de {tache} : refus")
    ga = oracle.gain_archive(archive_jugement)
    taille_archive = len(archive_jugement)
    for c in passees:
        i = c["identifiant"]
        g, d = oracle.gain(c["loi_predictive"]), oracle.divergence(c["loi_predictive"])
        releve_cartes.append({"bras": bras, "generation": generation, "identifiant": reels[i], "identifiant_servi": i, "temoin": None,
                              "gardien": "passe", "promue": i in promues, "verdict": verdicts.get(i),
                              "contre_calcul_ok": cc[i]["ok"] if i in cc else None, "gain_nat": round(g, 6),
                              "delta_gain_nat": round(g - ga, 6), "divergence_nat": round(d, 6), "log_e": detail[i].get("log_e"),
                              "retenue": i in retenues, "archive_de_jugement": taille_archive, "enonce": enonces.get(i)})
    for i, motif in refusees.items():
        releve_cartes.append({"bras": bras, "generation": generation, "identifiant": reels.get(i, i), "identifiant_servi": i,
                              "temoin": None, "gardien": "refuse", "promue": False, "verdict": None, "contre_calcul_ok": None,
                              "gain_nat": None, "delta_gain_nat": None, "divergence_nat": None, "motif": motif,
                              "archive_de_jugement": taille_archive, "enonce": enonces.get(i)})
    for nom, reel, c in temoins:
        i = c["identifiant"]
        passe = nom not in temoins_refuses
        releve_cartes.append({"bras": bras, "generation": generation, "identifiant": reel, "identifiant_servi": i, "temoin": nom,
                              "gardien": "passe" if passe else "refuse", "promue": i in promus_temoins,
                              "verdict": verdicts_t.get(i), "contre_calcul_ok": cc_t[i]["ok"] if i in cc_t else None,
                              "log_e": detail.get(i, {}).get("log_e"), "motif": temoins_refuses.get(nom),
                              "archive_de_jugement": 0})
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
             "temoins_refuses": temoins_refuses, "promues": promues, "temoins_promus": promus_temoins, "correspondance": reels,
             "verdicts": verdicts, "verdicts_temoins": verdicts_t, "retenues": retenues, "comptes": comptes,
             "bac_a_sable": description_bac.get("nom"), "factice": description_bac.get("factice"), "selection_sha256": sha_sel,
             "selection_temoins_sha256": sha_sel_t, "bilan_sha256": sha_bilan,
             "juge": {i: {k: d.get(k) for k in ("promue", "promue_seule", "log_richesse_max", "log_e", "membres_d_archive", "empreinte_engagement", "temoin")}
                      for i, d in detail.items()}, "depense": compteur.etat()}
    journal.append(ligne)
    return sha_bilan, ligne


# --- l'étage 1 entier : générations, ordre des bras, D7, relevé ---------------------------------------------------------------


def exiger_sans_temoin(heritage, temoins_ids):
    """Garde 7 : aucun identifiant de témoin (réel ou servi) dans l'archive ni dans la vue."""
    vue = bf.vue_pour_proposeur(heritage)
    presents = sorted(set(heritage.get("archive") or {}) & temoins_ids) + sorted({x["identifiant"] for x in vue["lois_retenues"]} & temoins_ids)
    if presents:
        raise TemoinRetenu(f"témoin(s) dans l'archive ou la vue : {presents} : refus")


def divergence_moyenne(oracle, loi_p, loi_q):
    import numpy as np
    P, Q = matrice(loi_p, oracle.instances), matrice(loi_q, oracle.instances)
    return float(np.mean(np.sum(P * (np.log(P) - np.log(Q)), axis=1)))


def decouvertes_distinctes(releve_cartes, lois, oracle, seuil=0.05):
    """Mineur 19 (mesure sans critère) : par bras et génération, VD comptées une fois si leur divergence symétrique (le maximum
    des deux sens, moyenne sur les instances de l'oracle) à une VD déjà comptée est sous `seuil` nat ; ordre des identifiants."""
    out = {}
    for c in releve_cartes:
        if c.get("temoin") or c.get("gardien") != "passe":
            continue
        f = classer(promue=c["promue"], survit=c["verdict"] == "survit", gain_nat=c["gain_nat"], delta_gain_nat=c["delta_gain_nat"],
                    divergence_nat=c["divergence_nat"], bras=c["bras"])
        if f["vraie_decouverte"]:
            out.setdefault(c["bras"], {}).setdefault(str(c["generation"]), []).append(c["identifiant_servi"])
    rendu = {}
    for b, par_g in out.items():
        for g, ids in par_g.items():
            gardees = []
            for i in sorted(ids):
                if all(max(divergence_moyenne(oracle, lois[i], lois[j]), divergence_moyenne(oracle, lois[j], lois[i])) >= seuil for j in gardees):
                    gardees.append(i)
            rendu.setdefault(b, {})[g] = {"vd": len(ids), "distinctes": len(gardees)}
    return rendu


def jouer_etage_1(sortie, *, monde, racine, plan, decisions, proposeurs, adaptateur_etage, roles, fabrique_executeur, compteur,
                  moteur="simule", environnement=None, permis_en_plus=()):
    """Trois bras, `plan['generations']` générations ; dans chaque génération l'ordre est réel → recopie-mélange → aléatoire.
    Rend (relevé de l'étage 1, journal). Toute exception d'une génération (`ArretTour`, session en échec, refus de modèle, vue
    avec verdict, bac indisponible, héritage refusé, témoin retenu, erreur) lève `ArretTour` avec le relevé partiel (C12)."""
    verifier_decisions(decisions)
    exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                             (roles["verificateur"][0], roles["familles"]["verificateur"]))
    adaptateur_etage.parts = dict(compteur.parts)
    oracle = Oracle(monde["loi"], racine, DIM)
    journal, releve_cartes, lectures, incidents = [], [], [], []
    jouees = {b: [] for b in BRAS_ETAGE1}
    etat = {b: {"dossier_prec": None, "sha_prec": None} for b in BRAS_ETAGE1}
    temoins_ids, lois_servies = set(), {}
    recherche = {"contextes_cherches": 0, "touches": [], "episodes_servis": set()}
    archive_reel_courante = {}
    arret = None
    try:
        for g in range(1, plan["generations"] + 1):
            source_recopie = dict(etat["reel"])  # C19 : la recopie de g lit le bilan du bras réel de g−1
            for bras in BRAS_ETAGE1:
                d = os.path.join(sortie, f"bras-{bras}", f"generation-{g}")
                os.makedirs(d)
                if g == 1:
                    heritage = bf.heritage_initial()
                else:
                    src = source_recopie if bras == "recopie_melange" else etat[bras]
                    try:
                        heritage = bf.lire_heritage(src["dossier_prec"], src["sha_prec"])
                    except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:
                        incidents.append({"bras": bras, "generation": g, "type": type(e).__name__, "motif": str(e)[:300]})
                        raise ArretTour(f"héritage refusé ({type(e).__name__}) : arrêt") from e
                    lectures.append({"bras": bras, "generation": g, "attendu": src["sha_prec"], "lu": heritage["bilan_sha256"],
                                     "source": "reel" if bras == "recopie_melange" else bras})
                    journal.append({"evenement": "heritage-lu", "bras": bras, "generation": g, "bilan_sha256": heritage["bilan_sha256"],
                                    "source": "reel" if bras == "recopie_melange" else bras, "archive": sorted(heritage["archive"])})
                exiger_sans_temoin(heritage, temoins_ids)
                if bras == "recopie_melange" and not heritage["archive"]:  # ne joue pas : aucune carte, aucun témoin
                    journal.append({"evenement": "generation-non-jouee", "bras": bras, "generation": g,
                                    "motif": "archive du bras réel (g−1) vide : aucune carte à recopier ni à mélanger (aucun repli)"})
                    etat[bras] = {"dossier_prec": d, "sha_prec": None}
                    continue
                if bras == "reel" or decisions["d7"] == "archive_propre" or bras == "recopie_melange":
                    archive_jugement = heritage["archive"]
                else:  # D7 « archive_du_bras_reel » : le bras aléatoire est jugé contre l'archive du bras réel de la génération
                    archive_jugement = archive_reel_courante
                sha, ligne = jouer_generation(d, bras, g, monde, heritage, archive_jugement, racine, fabrique_executeur, proposeurs,
                                              adaptateur_etage, roles, decisions, plan, oracle, compteur, journal, releve_cartes,
                                              recherche, moteur, environnement, permis_en_plus)
                temoins_ids |= {x["identifiant"] for x in releve_cartes if x.get("temoin")}
                temoins_ids |= {x["identifiant_servi"] for x in releve_cartes if x.get("temoin")}
                with open(os.path.join(d, bf.NOM_CARTES), encoding="utf-8") as f:
                    lois_servies.update({c["identifiant"]: c["loi_predictive"] for c in json.load(f)["cartes"]})
                jouees[bras].append(g)
                if bras == "reel":
                    archive_reel_courante = heritage["archive"]
                etat[bras] = {"dossier_prec": d, "sha_prec": sha}
        for bras in BRAS_ETAGE1:
            if etat[bras]["sha_prec"]:
                try:
                    fin = bf.lire_heritage(etat[bras]["dossier_prec"], etat[bras]["sha_prec"])
                except (bf.HeritageRefuse, bf.SelectionNonVerifiee) as e:
                    incidents.append({"bras": bras, "generation": "finale", "type": type(e).__name__, "motif": str(e)[:300]})
                    raise ArretTour(f"héritage final refusé ({type(e).__name__}) : arrêt") from e
                exiger_sans_temoin(fin, temoins_ids)
                journal.append({"evenement": "heritage-final-lu", "bras": bras, "bilan_sha256": etat[bras]["sha_prec"], "archive": sorted(fin["archive"])})
    except ArretTour as e:
        arret = str(e)
    except Exception as e:  # noqa: BLE001 — C12 : toute exception d'une génération est un arrêt scellé, motif et type dits
        arret = f"{type(e).__name__} : {str(e)[:500]}"
        incidents.append({"type": type(e).__name__, "motif": str(e)[:300]})
    if arret:
        journal.append({"evenement": "arret", "motif": arret, "depense": compteur.etat()})
    tranches = set()
    for bras in BRAS_ETAGE1:
        for g in jouees[bras]:
            tranches |= lignes_de_tranche(monde, racine, f"{VERSION}|etage=1|bras={bras}|generation={g}")
    lignes_trouvees = sorted(recherche["episodes_servis"] & tranches)
    recherche_rendue = {"contextes_cherches": recherche["contextes_cherches"], "parametres_de_la_loi_plantee": 9,
                        "formes": ["exacte", "deux décimales"], "touches": recherche["touches"],
                        "tranches_comparees": sum(len(v) for v in jouees.values()),
                        "lignes_de_tranche_dans_les_contextes": [list(x) for x in lignes_trouvees]}
    try:
        vd = decouvertes_distinctes(releve_cartes, lois_servies, oracle)
    except Exception as e:  # noqa: BLE001 — mesure sans critère ; son échec est dit, jamais tu
        vd = {"erreur": f"{type(e).__name__} : {str(e)[:200]}"}
    releve = {"version": VERSION, "etage": 1, "arret": arret, "generations_jouees": jouees,
              "boucle": {"incidents": incidents, "lectures": lectures}, "cartes": releve_cartes,
              "decisions": dict(decisions), "plan": dict(plan), "depense": compteur.etat(), "moteur_etage": moteur,
              "vd_distinctes": vd, "recherche_loi_plantee": recherche_rendue}
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
                 "evaluateur_sha256": sha256_fichier(CHEMIN_EVALUATEUR), "consigne_proposeur_sha256":
                 hashlib.sha256(CONSIGNE_PROPOSEUR.encode()).hexdigest(), "grammaire_sha256": empreinte_objet(GRAMMAIRE),
                 "regle_des_graines": f"SeedSequence(E, spawn_key=(cle_de_tache(tâche),)) ; tâches « {VERSION}|etage=1|bras=<b>|generation=<g>|… »"},
                **champs)


# --- doublures scriptées du mode à blanc : branchées sur le chemin réel, elles ne lisent que ce que lit un modèle --------------


def _graine_texte(*morceaux):
    return int(hashlib.sha256("|".join(morceaux).encode("utf-8")).hexdigest()[:16], 16)


def _dernier_bloc_json(texte):
    blocs = re.findall(r"```json\s*(.*?)\s*```", texte or "", re.S)
    for b in reversed(blocs):
        try:
            return json.loads(b)
        except ValueError:
            continue
    return None


def ajuster_softmax(episodes, iterations=300, pas=0.5):
    """Régression logistique multinomiale (3 issues, 2 traits, biais) par montée de gradient sur les épisodes servis."""
    W, b = [[0.0, 0.0] for _ in range(K)], [0.0] * K
    n = len(episodes)
    for _ in range(iterations):
        gW, gb = [[0.0, 0.0] for _ in range(K)], [0.0] * K
        for e in episodes:
            z = e["z"]
            s = [b[k] + W[k][0] * z[0] + W[k][1] * z[1] for k in range(K)]
            m = max(s)
            ex = [math.exp(x - m) for x in s]
            t = sum(ex)
            for k in range(K):
                r = (1.0 if e["y"] == k else 0.0) - ex[k] / t
                gW[k][0] += r * z[0]
                gW[k][1] += r * z[1]
                gb[k] += r
        for k in range(K):
            W[k][0] += pas * gW[k][0] / n
            W[k][1] += pas * gW[k][1] / n
            b[k] += pas * gb[k] / n
    return W, b


class AdaptateurProposeurScripte:
    """Doublure scriptée d'un proposeur, branchée derrière `ProposeurAdaptateur` (chemin réel) : elle ne lit que le texte servi
    (consigne et contexte) ; elle ajuste une softmax sur les épisodes de développement servis et l'écrit **selon la grammaire
    servie** (champs lus dans « gabarit » → « grammaire » ; grammaire absente : elle devine un format, refusé au gardien).
    Scénarios : « hors_gabarit » (clés en trop), « illisible », « muet:1,2 » (aucune proposition aux appels nommés), « refus »
    (statut R-764), « erreur » (session en échec)."""

    def __init__(self, nom, ecart=0.4, scenario=None, cout_par_appel=0.0):
        self.nom, self.ecart, self.scenario, self.cout = nom, ecart, scenario or "", cout_par_appel
        self.appels = []

    def lancer(self, role, texte, dossier, budget_usd, max_tours, modele=None):
        self.appels.append({"role": role, "texte_sha256": hashlib.sha256(texte.encode()).hexdigest()})
        n_appel = len(self.appels)
        with open(os.path.join(dossier, f"servi-{n_appel:02d}.md"), "w", encoding="utf-8") as f:
            f.write(texte)
        if self.scenario == "refus":
            refus = {"motif": "modèle servi « autre-modele » ≠ modèle demandé (doublure)", "modele_demande": modele,
                     "modele_servi": "autre-modele", "evenement": "doublure"}
            return Resultat("", [], self.cout, "refus", "refus (R-764) : " + refus["motif"], refus=refus, modele_servi="autre-modele")
        if self.scenario == "erreur":
            return Resultat("", [], self.cout, "erreur", "session en échec (doublure)")
        if self.scenario == "illisible":
            return Resultat("je ne sais pas", [], self.cout, "ok")
        if self.scenario.startswith("muet:") and str(n_appel) in self.scenario[5:].split(","):
            return Resultat("```json\n[]\n```", [], self.cout, "ok")
        contexte = _dernier_bloc_json(texte) or {}
        n = int(re.search(r"au plus (\d+) lois", texte).group(1)) if re.search(r"au plus (\d+) lois", texte) else 1
        episodes = contexte.get("episodes_developpement") or []
        gram = ((contexte.get("gabarit") or {}).get("grammaire") or {}).get("types") or {}
        champs = set((gram.get("softmax") or {}).get("champs") or {})
        borne = float((contexte.get("gabarit") or {}).get("borne_des_poids") or 1.0)
        rng = random.Random(_graine_texte(self.nom, texte))
        W, b = ajuster_softmax(episodes) if episodes else ([[0.0, 0.0] for _ in range(K)], [0.0] * K)
        props = []
        for i in range(n):
            e = 0.0 if i == 0 else self.ecart
            w = [[max(-borne, min(borne, round(x + rng.gauss(0.0, e), 6))) for x in ligne] for ligne in W]
            bb = [max(-borne, min(borne, round(x + rng.gauss(0.0, e / 2), 6))) for x in b]
            if {"type", "poids", "biais"} <= champs:
                loi = {"type": "softmax", "poids": w, "biais": bb}
            else:  # grammaire non servie : format deviné
                loi = {"type": "logistique", "weights": w, "bias": bb}
            p = {"enonce": f"loi ajustée n° {i + 1} sur les épisodes de développement servis", "loi_predictive": loi}
            if self.scenario == "hors_gabarit":
                p.update(test_de_mort={"seuil": "au moins 0,0"}, statistique="moyenne")
            props.append(p)
        return Resultat("```json\n" + json.dumps(props, ensure_ascii=False) + "\n```", [], self.cout, "ok")


SCRIPT_EXPERIMENTATEUR = ("import json, runpy\nLOI = {loi!r}\nev = runpy.run_path('tranche/{fichier}')\n"
                          "ev['ecrire_gains'](json.loads(LOI), 'tranche/episodes.csv', 'gains.csv')\n")
SCRIPT_ARRONDI = ("import json, runpy\nLOI = {loi!r}\nev = runpy.run_path('tranche/{fichier}')\n"
                  "g = ev['gains'](json.loads(LOI), 'tranche/episodes.csv')\n"
                  "open('gains.csv', 'w', encoding='utf-8').write('episode,gain\\n' + ''.join('%d,%.{d}f\\n' % (i, x) for i, x in enumerate(g, 1)))\n"
                  "print('RESULTAT: %r' % (sum(g) / len(g)))\n")
SCRIPT_FABRIQUE = ("open('gains.csv', 'w', encoding='utf-8').write('episode,gain\\n' + ''.join('%d,0.5\\n' % i for i in range(1, 401)))\n"
                   "print('RESULTAT: 0.5')\n")
FIN_SCRIPTEE = "```json\n" + json.dumps({"fin": "fini"}) + "\n```"


def lire_loi_de_la_consigne(consigne):
    """Ce que lit l'expérimentateur scripté : le préenregistrement court servi, la loi gelée dans son texte de test, et
    l'évaluateur nommé dans ses données ; (loi, None) ou (None, motif)."""
    prereg = A._section(consigne, v5.TITRE_SECTION_PREREG)
    if not isinstance(prereg, dict):
        return None, "préenregistrement court absent de la consigne"
    loi = loi_du_texte(prereg.get("test_de_mort"))
    if loi is None:
        return None, "loi gelée absente du préenregistrement court"
    if FICHIER_EVALUATEUR not in [d.get("chemin") for d in prereg.get("donnees") or []]:
        return None, "évaluateur de référence absent des données du préenregistrement court"
    return loi, None


class AdaptateurExperimentateurScripte:
    """Doublure scriptée de l'expérimentateur, branchée derrière `AdaptateurEtageV62` : elle lit la loi **dans la consigne**
    (préenregistrement court) et nulle part ailleurs (C8) ; loi absente → elle finit sans script (« non concluant »). Scénarios :
    « arrondi:N » (gains arrondis à N décimales), « fabrique » (gains fabriqués), « erreur » (session en échec), « refus » (R-764)."""

    def __init__(self, scenario=None, cout_par_session=0.0):
        self.scenario, self.cout, self.appels = scenario or "", cout_par_session, []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        tour = int(os.path.basename(dossier).split("-")[1])
        loi, motif = lire_loi_de_la_consigne(consigne)
        self.appels.append({"role": role, "tour": tour, "loi_lue": loi is not None, "motif": motif})
        if self.scenario == "erreur":
            return Resultat("", [], self.cout, "erreur", "session en échec (doublure)")
        if self.scenario == "refus":
            refus = {"motif": "modèle servi « autre » (doublure)", "modele_demande": modele, "modele_servi": "autre", "evenement": "doublure"}
            return Resultat("", [], self.cout, "refus", "refus (R-764) : " + refus["motif"], refus=refus, modele_servi="autre")
        if tour > 1 or loi is None:
            return Resultat(FIN_SCRIPTEE if loi is not None else "```json\n" + json.dumps({"fin": motif}) + "\n```", [], self.cout, "ok")
        texte_loi = json_canonique(loi).decode("utf-8")
        if self.scenario.startswith("arrondi:"):
            script = SCRIPT_ARRONDI.replace("{d}", self.scenario.split(":")[1]).format(loi=texte_loi, fichier=FICHIER_EVALUATEUR)
        elif self.scenario == "fabrique":
            script = SCRIPT_FABRIQUE
        else:
            script = SCRIPT_EXPERIMENTATEUR.format(loi=texte_loi, fichier=FICHIER_EVALUATEUR)
        return Resultat("```json\n" + json.dumps({"experience": [{"executer": {"script": script}}]}, ensure_ascii=False) + "\n```",
                        [], self.cout, "ok")


class AdaptateurVerificateurScripte:
    """Doublure du vérificateur (lecteur témoin) : lit la seule consigne (`a_blanc_v59.verificateur_temoin`)."""

    def __init__(self, cout_par_session=0.0):
        self.cout, self.appels = cout_par_session, []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        self.appels.append({"role": role})
        return Resultat(A.verificateur_temoin(consigne), [], self.cout, "ok")


__all__ = ("jouer_etage_1", "jouer_generation", "juger", "completer_carte", "temoins_du_monde", "garder", "contre_calculer",
           "statistique_hors_bac", "exiger_familles_separees", "exiger_sans_temoin", "verifier_decisions", "Compteur",
           "ProposeurAdaptateur", "AdaptateurEtageV62", "AdaptateurProposeurScripte", "AdaptateurExperimentateurScripte",
           "AdaptateurVerificateurScripte", "contexte_du_proposeur", "extraire_propositions", "manifeste_tour", "verifier_loi_servable",
           "texte_du_test", "test_de_mort_impose", "loi_du_texte", "lire_loi_de_la_consigne", "identifiant_opaque", "carte_servie",
           "chercher_loi_plantee", "creer_tranche", "decouvertes_distinctes", "TourRefuse", "TemoinRetenu", "FamillesNonSeparees",
           "ArretTour", "VERSION", "BRAS_ETAGE1", "TEMOINS", "DECISIONS", "ALPHA", "GRAMMAIRE", "TYPES_PERMIS")
