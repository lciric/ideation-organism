"""La fiche d'hypothèse : dataclass, validation, vues, empreintes et gel.

Deux empreintes :
- `empreinte()` — SHA-256 du JSON canonique de la **vue publique** (ce que voit l'expérimentateur) : c'est l'empreinte
  du test, écrite avant l'expérience et vérifiée à chaque exécution ;
- `empreinte_complete()` — couvre en plus les champs privés de l'orchestrateur (vérité du témoin, source, parents),
  gelée au même moment : la vérité d'un témoin ne peut pas être changée après coup sans que la mesure de qualité le voie.
Le statut, le nombre d'essais et l'historique changent au fil des générations : ils ne sont dans aucune empreinte.
"""

import dataclasses
import json
import math
import os
import re
from dataclasses import dataclass, field

from .outils import ecrire_scelle, json_canonique, nombre_fini, sha256_fichier, sha256_octets

STATUTS = {
    "proposee", "gelee", "survit", "eliminee", "indecise", "retiree", "rejetee (test change)",
    "refusee (modifiee apres gel)", "refusee (redite)", "refusee (fille sans prediction nouvelle)",
    "refusee (invalide)", "hors budget",
}
CHAMPS_MUTABLES = ("statut", "essais", "historique")
CHAMPS_PRIVES = ("temoin", "source", "parents")
MOTIF_TEMOIN = re.compile(r"^\s*t[ée]moin\s+(vrai|faux|vraie|fausse)\s*:?\s*", re.IGNORECASE)
MOTIF_IDENTIFIANT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}$")


class FicheInvalide(ValueError):
    def __init__(self, problemes):
        self.problemes = list(problemes)
        super().__init__("fiche invalide : " + " ; ".join(self.problemes))


class FicheModifieeApresGel(RuntimeError):
    """La fiche ne correspond plus à l'empreinte gelée : elle est refusée."""


@dataclass
class Fiche:
    identifiant: str
    enonce: str
    prediction: dict
    metrique: str
    nul: str
    seuil: float
    severite_attendue: float
    cout_borne: float
    protocole: str
    parents: list = field(default_factory=list)
    domaines: list = field(default_factory=list)
    operateurs: list = field(default_factory=list)
    contraintes: list = field(default_factory=list)
    statut: str = "proposee"
    temoin: object = None
    source: str = "population-initiale"
    ce_que_la_fille_predit_de_plus: str = ""
    ce_qui_change: dict = field(default_factory=dict)
    loi_predictive: object = None
    espace_instances: object = None
    essais: int = 0
    historique: list = field(default_factory=list)

    # --- validation -------------------------------------------------------------------------------------------
    def problemes(self):
        p = []
        if not isinstance(self.identifiant, str) or not MOTIF_IDENTIFIANT.match(self.identifiant):
            p.append("identifiant : 1 à 64 caractères [A-Za-z0-9_.-], sans séparateur de chemin")
        for nom in ("enonce", "metrique", "nul", "protocole"):
            valeur = getattr(self, nom)
            if not isinstance(valeur, str) or not valeur.strip():
                p.append(f"{nom} : texte non vide requis")
        if isinstance(self.enonce, str) and len(self.enonce) > 2000:
            p.append("enonce : au plus 2000 caractères")
        pred = self.prediction
        if not isinstance(pred, dict):
            p.append("prediction : objet {signe, valeur, texte} requis")
        else:
            if pred.get("signe") not in ("+", "-"):
                p.append("prediction.signe : « + » ou « - »")
            if not nombre_fini(pred.get("valeur")) or pred.get("valeur") <= 0:
                p.append("prediction.valeur : nombre fini strictement positif (la prédiction doit être chiffrée)")
        if not nombre_fini(self.seuil):
            p.append("seuil : nombre fini requis")
        s = self.severite_attendue
        if not nombre_fini(s) or not (0.0 < s < 1.0):
            p.append("severite_attendue : probabilité de passer le seuil sous le nul, dans ]0 ; 1[")
        if not nombre_fini(self.cout_borne) or self.cout_borne <= 0:
            p.append("cout_borne : nombre fini strictement positif")
        for nom in ("parents", "domaines", "operateurs", "contraintes"):
            valeur = getattr(self, nom)
            if not isinstance(valeur, list) or any(not isinstance(v, str) or not v.strip() for v in valeur):
                p.append(f"{nom} : liste de textes non vides")
        if isinstance(self.domaines, list) and not self.domaines:
            p.append("domaines : au moins un domaine")
        if self.statut not in STATUTS:
            p.append(f"statut inconnu : {self.statut!r}")
        if self.temoin not in (None, "vraie", "fausse"):
            p.append("temoin : None, « vraie » ou « fausse »")
        if not isinstance(self.source, str) or not self.source:
            p.append("source : texte non vide")
        if not isinstance(self.ce_que_la_fille_predit_de_plus, str):
            p.append("ce_que_la_fille_predit_de_plus : texte")
        if isinstance(self.parents, list) and self.parents and not str(self.ce_que_la_fille_predit_de_plus).strip():
            p.append("fiche fille : ce_que_la_fille_predit_de_plus doit être non vide (prédiction nouvelle exigée)")
        if not isinstance(self.ce_qui_change, dict) or any(
                not isinstance(k, str) or not isinstance(v, str) or not v.strip() for k, v in self.ce_qui_change.items()):
            p.append("ce_qui_change : objet {identifiant: texte non vide}")
        if self.loi_predictive is not None and (not isinstance(self.loi_predictive, dict) or "type" not in self.loi_predictive):
            p.append("loi_predictive : None ou objet avec un champ « type »")
        if self.espace_instances is not None and not isinstance(self.espace_instances, dict):
            p.append("espace_instances : None ou objet")
        if not isinstance(self.essais, int) or isinstance(self.essais, bool) or self.essais < 0:
            p.append("essais : entier positif ou nul")
        try:
            json_canonique(self.vers_dict())
        except (TypeError, ValueError):
            p.append("la fiche doit être sérialisable en JSON fini")
        return p

    def valider(self):
        problemes = self.problemes()
        if problemes:
            raise FicheInvalide(problemes)
        return self

    # --- vues et empreintes -----------------------------------------------------------------------------------
    def vers_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def depuis_dict(cls, donnees):
        connus = {f.name for f in dataclasses.fields(cls)}
        inconnus = sorted(set(donnees) - connus)
        if inconnus:
            raise FicheInvalide([f"champ inconnu : {nom}" for nom in inconnus])
        manquants = [f.name for f in dataclasses.fields(cls)
                     if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
                     and f.name not in donnees]
        if manquants:
            raise FicheInvalide([f"champ manquant : {nom}" for nom in manquants])
        return cls(**json.loads(json.dumps(donnees)))

    def vue_publique(self):
        d = self.vers_dict()
        for nom in CHAMPS_MUTABLES + CHAMPS_PRIVES:
            d.pop(nom, None)
        # v7, version 11 (contre-lecture du socle, C5) : un témoin était reconnaissable à son énoncé (« Témoin vrai : … »)
        # dès qu'il passait par un agent ; la vue publique neutralise ce préfixe, quel que soit le générateur.
        if isinstance(d.get("enonce"), str):
            d["enonce"] = MOTIF_TEMOIN.sub("", d["enonce"]).strip() or d["enonce"]
        return d

    def vue_complete_gelee(self):
        d = self.vers_dict()
        for nom in CHAMPS_MUTABLES:
            d.pop(nom, None)
        return d

    def canonique(self):
        return json_canonique(self.vue_publique())

    def empreinte(self):
        return sha256_octets(self.canonique())

    def empreinte_complete(self):
        return sha256_octets(json_canonique(self.vue_complete_gelee()))

    def aptitude(self):
        """Sévérité du test survécu : −ln(probabilité de passer le seuil sous le nul). Jamais le signe ni l'ampleur."""
        return -math.log(self.severite_attendue)

    def famille_source(self):
        """Source pour la calibration : la recombinaison garde son modèle (« recombinaison:<modèle> »)."""
        tete = self.source.split(":", 1)[0]
        return self.source if tete in ("recombinaison", "agent", "proposeur") else tete


class RegistreGel:
    """Empreintes gelées avant l'expérience ; toute exécution les revérifie."""

    def __init__(self):
        self._publiques = {}
        self._completes = {}

    def geler(self, fiche):
        fiche.valider()
        publique, complete = fiche.empreinte(), fiche.empreinte_complete()
        deja = self._publiques.get(fiche.identifiant)
        if deja is not None and (deja != publique or self._completes[fiche.identifiant] != complete):
            raise FicheModifieeApresGel(f"{fiche.identifiant} : fiche modifiée depuis son premier gel")
        self._publiques[fiche.identifiant] = publique
        self._completes[fiche.identifiant] = complete
        return publique

    def est_gelee(self, identifiant):
        return identifiant in self._publiques

    def empreinte(self, identifiant):
        return self._publiques[identifiant]

    def empreinte_complete(self, identifiant):
        return self._completes[identifiant]

    def verifier(self, fiche):
        if fiche.identifiant not in self._publiques:
            raise FicheModifieeApresGel(f"{fiche.identifiant} : aucune empreinte gelée, exécution refusée")
        if fiche.empreinte() != self._publiques[fiche.identifiant]:
            raise FicheModifieeApresGel(f"{fiche.identifiant} : le test a changé après le gel")
        if fiche.empreinte_complete() != self._completes[fiche.identifiant]:
            raise FicheModifieeApresGel(f"{fiche.identifiant} : un champ privé (témoin, source, parents) a changé après le gel")
        return True

    def etat(self):
        return {i: {"empreinte": self._publiques[i], "empreinte_complete": self._completes[i]} for i in sorted(self._publiques)}


def ecrire_fiche_gelee(fiche, dossier):
    """Écrit `fiche.json` = octets canoniques de la vue publique (son SHA-256 est l'empreinte) et son `.sha256`."""
    return ecrire_scelle(os.path.join(dossier, "fiche.json"), fiche.canonique())


def verifier_fichier_fiche(chemin, empreinte_attendue):
    return os.path.exists(chemin) and sha256_fichier(chemin) == empreinte_attendue


def charger_fiches(chemin):
    with open(chemin, encoding="utf-8") as f:
        donnees = json.load(f)
    if isinstance(donnees, dict) and "fiches" in donnees:
        donnees = donnees["fiches"]
    if not isinstance(donnees, list):
        raise FicheInvalide(["le fichier doit contenir une liste de fiches (ou {\"fiches\": [...]})"])
    return [Fiche.depuis_dict(d).valider() for d in donnees]
