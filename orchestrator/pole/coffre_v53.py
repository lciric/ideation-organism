"""Règle de non-lecture (A21 ; brouillon 6, CP5-08) : aucun verdict d'É6 ni d'É7, aucune clé des classes ni des bras n'est lu
avant la fin d'É9 ; seules les consommations (M7) sont lues en route.

`Coffre` : les verdicts des juges et les clés (anonymisation, classes, bras) y sont **déposés** scellés ; le dépôt rend une
empreinte, jamais le contenu. `ouvrir` avant `declarer_fin_e9()` est un **incident** : consigné au journal d'accès (scellé
avec la sortie), puis `LectureAvantFinE9` est levée (l'orchestrateur s'arrête ; les décisions de sacrifice se rejouent sur
les seules consommations, `budget_v53.rejouer`). Les consommations vivent à part (`noter_consommation`, `consommations`) et
se lisent à tout moment. Le journal d'accès consigne chaque dépôt, chaque lecture de consommation et chaque tentative.
"""

import json
import os

from .outils import EcrasementInterdit, ecrire_json_scelle, verifier_scelle

VERSION = "coffre-a21-v53"


class LectureAvantFinE9(RuntimeError):
    pass


class Coffre:
    def __init__(self, dossier):
        if os.path.exists(dossier):
            raise EcrasementInterdit(f"coffre {dossier} : déjà présent (jamais réutilisé, R12)")
        os.makedirs(dossier)
        self.dossier = dossier
        self.fin_e9 = False
        self.acces = []
        self.incidents = []
        self._consommations = []

    def _acces(self, quoi, nom=None, **champs):
        self.acces.append(dict({"n": len(self.acces) + 1, "quoi": quoi, "nom": nom, "apres_fin_e9": self.fin_e9}, **champs))

    def deposer(self, nom, objet):
        if not isinstance(nom, str) or not nom or "/" in nom or nom.startswith("."):
            raise ValueError("nom de dépôt : simple, sans séparateur")
        sha = ecrire_json_scelle(os.path.join(self.dossier, nom + ".json"), objet)
        self._acces("depot", nom, sha256=sha)
        return sha

    def noter_consommation(self, etape, role, cout_usd, **champs):
        """M7 : jetons, durée, coût, modèle servi — rien d'un verdict."""
        interdits = {"verdict", "verdicts", "items", "notable", "classe", "cle", "bras", "notes"} & set(champs)
        if interdits:
            raise ValueError(f"une consommation ne porte aucun verdict ni clé ({sorted(interdits)})")
        self._consommations.append(dict({"etape": etape, "role": role, "cout_usd": float(cout_usd)}, **champs))

    def consommations(self):
        self._acces("lecture_consommations")
        return [dict(c) for c in self._consommations]

    def declarer_fin_e9(self):
        self.fin_e9 = True
        self._acces("fin_e9")

    def ouvrir(self, nom):
        if not self.fin_e9:
            incident = {"quoi": "lecture d'un verdict ou d'une clé avant la fin d'É9 (A21)", "nom": nom, "n_acces": len(self.acces) + 1}
            self.incidents.append(incident)
            self._acces("tentative_avant_fin_e9", nom)
            raise LectureAvantFinE9(f"A21 : lecture de {nom!r} avant la fin d'É9 refusée ; incident consigné ; les décisions prises "
                                    "après la lecture se rejouent sur les seules consommations")
        chemin = os.path.join(self.dossier, nom + ".json")
        if not verifier_scelle(chemin):
            raise LectureAvantFinE9(f"dépôt {nom!r} : sceau absent ou faux")
        self._acces("ouverture", nom)
        with open(chemin, "r", encoding="utf-8") as f:
            return json.load(f)

    def journal(self):
        return {"version": VERSION, "fin_e9": self.fin_e9, "acces": list(self.acces), "incidents": list(self.incidents)}
