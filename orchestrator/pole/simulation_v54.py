"""Moteur simulé de la v54 (aucun appel, aucune dépense réelle) — au-dessus de `simulation_v53` (inchangé).

Ajouts : lecteur de niches au format de l'annexe (structures nommées par leur identifiant, champ « affirmation centrale »),
lecture du désaccord (`## Deux affirmations`), et les rôles du pré-pilote, reconnus aux marques que le noyau écrit dans la
consigne : rédacteur (`## Fond`), metteur en forme (`## Éléments à mettre en forme`), relecteur (consigne figée contenant
`RELECTEUR`), second lecteur et adjudicateur de M5 (`SECOND_LECTEUR`, `ADJUDICATEUR` : même contrat que l'aiguilleur),
paraphrase (`## Paraphrase`), vérificateur d'antériorité (`VERIFICATEUR`), table seule de l'axe 7 (`TABLE_SEULE`). Les
réponses sont déterministes (empreinte de la consigne) ; les essais remplacent `decider` pour planter un artefact.
"""

import hashlib
import json
import re

from .simulation_v53 import AdaptateurSimuleCourse2

VERSION = "simulation-v54"


def _h(texte, sel=""):
    return int.from_bytes(hashlib.sha256((sel + texte).encode("utf-8")).digest()[:4], "big")


def _bloc(consigne, titre):
    m = re.search(r"## " + re.escape(titre) + r"[^\n]*\n```json\n(.*?)\n```", consigne, re.S)
    return json.loads(m.group(1)) if m else None


class AdaptateurSimuleV54(AdaptateurSimuleCourse2):
    def __init__(self, *, longueur_rendu=5000, **kw):
        super().__init__(**kw)
        self.longueur_rendu = longueur_rendu

    def description(self):
        return dict(super().description(), version=VERSION)

    def reponse(self, role, consigne, modele):
        h = _h(consigne)
        if "## Lecture : niches" in consigne:
            liste = json.loads(re.search(r"## Liste fermée\n```json\n(.*?)\n```", consigne, re.S).group(1))
            fiche = _bloc(consigne, "La fiche") or {}
            hf = _h(json.dumps(fiche, sort_keys=True, ensure_ascii=False))
            niches, st = liste["niches"], liste["structures"]
            return json.dumps({"niche": niches[hf % len(niches)], "structures": [st[hf % len(st)], st[(hf // 7) % len(st)]],
                               "affirmation_centrale": str(fiche.get("hypothese", ""))[:80]}, ensure_ascii=False)
        m = re.search(r"PRODUIT:(\w+):(\d+)", consigne)
        if m:
            cle, n = m.group(1), int(m.group(2))
            return json.dumps({cle: [self.fiche(_h(consigne, str(i))) for i in range(n)]}, ensure_ascii=False)
        if "## Deux affirmations" in consigne:
            return json.dumps({"desaccord": ("oui", "non", "indecidable")[h % 3]})
        if "## Fond" in consigne:
            fond = _bloc(consigne, "Fond")
            n = 12 + h % 5
            ancres = [f"ancre-{fond['ident']}-{i} : valeur {i * 7}" for i in range(n)]
            couples = [] if fond["classe"] in ("P", "C") else [[f"defaut-a-{fond['ident']}", f"defaut-b-{fond['ident']}"]]
            item = {"P": "aucun", "C": "aucun", "N1": "K1", "N2": "K2", "N3": "K3", "N4": "K4", "G": "K5"}[fond["classe"]]
            return json.dumps({"squelette": {"ancres": ancres, "couples": couples},
                               "declaration": {"item": item, "champs": ["hypothese", "methode"] if couples else [], "phrase": "phrase du texte I"}},
                              ensure_ascii=False)
        if "## Éléments à mettre en forme" in consigne:
            el = _bloc(consigne, "Éléments à mettre en forme")
            corps = " ; ".join(el["ancres"] + [x for c in el["couples"] for x in c])
            remplissage = max(0, self.longueur_rendu - len(corps) - 200)
            f = {c: f"{c} : texte de méthode" for c in self.champs}
            f[self.champ_titre] = "Titre rendu " + str(h % 1000)
            f["methode"] = corps + " " + ("m" * remplissage)
            return json.dumps({"fiches": [f]}, ensure_ascii=False)
        if "RELECTEUR" in consigne:
            fiche = _bloc(consigne, "La fiche") or {}
            defaut = "defaut-a-" in json.dumps(fiche, ensure_ascii=False)
            return json.dumps({"notable": not defaut, "item": None, "champs": [], "defaut_present": defaut, "classe": None})
        if "SECOND_LECTEUR" in consigne or "ADJUDICATEUR" in consigne:
            return json.dumps({"classe": "niveau_methode"})
        if "## Paraphrase" in consigne:
            fiche = _bloc(consigne, "La fiche") or {}
            return json.dumps({"fiches": [{k: f"{v} (reformulé)" for k, v in fiche.items() if k != "identifiant"}]}, ensure_ascii=False)
        if "VERIFICATEUR" in consigne:
            fiche = _bloc(consigne, "La fiche") or {}
            refs = fiche.get("references", [])
            return json.dumps({"references": [{"id": r.get("id"), "verdict": "reelle"} for r in refs]})
        if "TABLE_SEULE" in consigne:
            return json.dumps({"items": {"table": bool(h % 2)}})
        return super().reponse(role, consigne, modele)
