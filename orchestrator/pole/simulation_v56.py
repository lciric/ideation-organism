"""Moteur simulé de la v56 (aucun appel, aucune dépense) — au-dessus de `simulation_v55` (inchangé, R12).

Seul ajout : le rédacteur des fiches de M6b (D-g (b), CL20-08), reconnu à la marque `## Source M6b` que le pré-pilote v56 écrit
dans l'entrée : il rend un bloc `{"fiche_m6b": {titre, idee, references: [...]}}` dont les antériorités ne citent pas la source
servie (le nombre de références est lu à la marque `REFERENCES:N` de la consigne de rédaction, 5 à défaut). Le modèle servi
est celui demandé (comme la v55)."""

import json
import re

from .simulation_v54 import _bloc, _h
from .simulation_v55 import AdaptateurSimuleV55

VERSION = "simulation-v56"


class AdaptateurSimuleV56(AdaptateurSimuleV55):
    def description(self):
        return dict(super().description(), version=VERSION)

    def reponse(self, role, consigne, modele):
        if "## Source M6b" in consigne:
            src = _bloc(consigne, "Source M6b") or {}
            m = re.search(r"REFERENCES:(\d+)", consigne)
            n = int(m.group(1)) if m else 5
            h = _h(json.dumps(src, sort_keys=True, ensure_ascii=False))
            fiche = {"titre": "Idée reformulée " + "".join("abcdefghij"[int(c)] for c in str(h % 1000)),
                     "idee": "une idée reformulée sans nommer sa source",
                     "references": [{"id": f"r{k}", "titre": f"Antériorité simulée {k}"} for k in range(n)]}
            return "```json\n" + json.dumps({"fiche_m6b": fiche}, ensure_ascii=False) + "\n```"
        return super().reponse(role, consigne, modele)
